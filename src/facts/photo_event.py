# src/facts/photo_event.py
"""G7 -- §4.2's deterministic photo event, and §2.6's media-type conflict (M2).

§4.2, the only sentence in the design that states this fact exists:

    "For a photo group, it might be a deterministic event created from camera, time,
     and GPS metadata."

§2.6, the hierarchy this module READS and never rebuilds:

    "camera EXIF is strong photo evidence; capture time, GPS, and sensor-shaped
     dimensions reinforce it; exact display resolutions, PNG format, and software
     metadata may support a screenshot hypothesis; conflicting signals should lead to
     abstention rather than an invented classification."

**The tier is read, never re-derived (M2).** P4 puts `signal_tier` on the observation
for exactly this consumer, so this module branches on the integer and on nothing else
-- not on `extractor_name`, not on the container-path label. An observation P5 left
untiered contributes to nothing. Deriving the band from a name would encode §2.6 in a
second place, which is the defect M2 exists to prevent.

**The bands are P4's published order, read.** `SIGNAL_TIERS == (1, 2, 3)` and §2.6's
three bands arrive in that order, so the screenshot band is `SIGNAL_TIERS[-1:]` and
the photo bands are the rest. `extractors/ocr_policy.py` already reads the same split
as `USABLE_METADATA_TIERS`; a literal `3` here would be a third home for one boundary.
Both are tuples rather than ints because a band index is not a threshold and must not
look like one to Task 25's namespace introspection.

**P5 spells the EXIF tag names and this module holds no copy.** The tag name a
container-path label carries is "the reader-supplied tag name, which P5 deliberately
never spells", so the labels arrive inside the injected `PhotoEventClustering`.

**The event is `validated`.** Not `direct` -- no explicit slot states an event. Not
`possible` -- P9 requires a seed fact to be Direct or Validated, so a `possible` event
is a seed P9 can never use and G7 would deliver nothing. The spelling is
`facts.states.VALIDATED`; this module publishes a name for the choice, not a copy of
the state.

**`media_type` is the ordinary §3.7 procedure.** Each tiered observation is one
weighted vote, the candidates are ranked by `facts.facets.fill_or_abstain`, and that
function owns the two thresholds and the `below_margin` row. One rule is applied
BEFORE the ranking, and it is the only rule here the injected numbers cannot override:
a file whose only tiered observations are in the screenshot band fills nothing.
§2.6 -- "the system must not mistake the absence of EXIF for proof that an image is a
screenshot" -- and the screenshot band is what every image carries, so it separates
the two hypotheses by nothing. `below_margin` is the SPEC's own home for §2.6's
abstention: "margin over second-best not cleared -- including the
conflicting-image-signal case (§2.6)".

**OCR text density is never a signal here.** §2.6 rules it out by name, and this
module imports nothing from `evidence_shape.store` and holds no identifier that could
reach a text unit.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, SIGNAL_TIERS, check

from facts.cache import pass_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.facets import Candidate, fill_or_abstain
from facts.file_facts import RULE, write_fact
from facts.states import VALIDATED
from facts.unresolved import (
    BELOW_MARGIN, NO_CANDIDATE_EVIDENCE, RULE_ROUTE, write_unresolved,
)
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's Photos fields, snake_case per D6. Both already exist in the catalogue, so
#: this module creates no field: §3.12 lets values auto-create and fields never.
EVENT_FIELD: str = "event"
MEDIA_TYPE_FIELD: str = "media_type"

#: §3.13's definition of `validated` -- a deterministic rule that passes a contextual
#: check -- and the contextual check is the injected `same_event` predicate. The
#: spelling is `facts.states`'; preamble §3.1 gives a published state one home.
EVENT_STATE: str = VALIDATED

#: §4.2's three inputs, in §4.2's order: "camera, time, and GPS metadata". These are
#: the KEYS the injected label sets arrive under, not the labels themselves.
EVENT_INPUTS: tuple[str, str, str] = ("camera", "capture_time", "location")

#: §2.6's two hypotheses, photograph first. There is no third and no "unknown"
#: member: not filling the field IS the third outcome, and it is a row (B7).
MEDIA_TYPES: tuple[str, str] = ("photograph", "screenshot")

#: §2.6's three bands, read off P4's published order rather than re-spelled. Tuples,
#: not ints: a band index is not a threshold and must not look like one to Task 25.
PHOTO_BANDS: tuple[int, ...] = SIGNAL_TIERS[:-1]
SCREENSHOT_BAND: tuple[int, ...] = SIGNAL_TIERS[-1:]


@dataclass(frozen=True)
class PhotoEventClustering:
    """§4.2's three inputs, and the thresholds the design states for none of them.

    Every field is required and none has a default.

    `labels` maps each member of `EVENT_INPUTS` to the container-path labels P5's
    reader used for that input. P5 spells the EXIF tag names and this module holds no
    copy, so the mapping is the injection site and `EVENT_INPUTS` is its one address.

    `same_event` receives two files' signal mappings -- each `{kind: sorted raw
    values}` over `EVENT_INPUTS` -- and answers whether they describe one occasion.
    The time window, the GPS radius and the camera-identity test are Deferred
    together; they arrive as this one predicate rather than as three numbers.

    `minimum_members` is how many photographs make an event. §4.2 uses the event as a
    GROUP seed and states no count, so the count is the caller's.
    """
    labels: Mapping[str, frozenset[str]]
    same_event: Callable[[Mapping[str, tuple[str, ...]],
                          Mapping[str, tuple[str, ...]]], bool]
    minimum_members: int

    def __post_init__(self) -> None:
        for kind in EVENT_INPUTS:
            check(kind, self.labels, name="event input")


@dataclass(frozen=True)
class _Photo:
    """One (file, content hash) with its §4.2 inputs already read once."""
    file_id: str
    content_hash: str
    cited: tuple[Observation, ...]
    signals: Mapping[str, tuple[str, ...]]

    @property
    def offered(self) -> bool:
        """Did this file offer any of §4.2's three inputs at all?"""
        return any(self.signals[kind] for kind in EVENT_INPUTS)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str],
          clustering: PhotoEventClustering) -> tuple[_Photo, ...]:
    """Every version, in file-id order, with its signals resolved.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus.
    """
    photos: list[_Photo] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        observations = observations_for_version(conn, file_id, content_hash)
        signals: dict[str, tuple[str, ...]] = {}
        cited: dict[str, Observation] = {}
        for kind in EVENT_INPUTS:
            labels = clustering.labels[kind]
            readings = tuple(
                one for one in observations
                if one.signal_tier in PHOTO_BANDS
                and any(segment.label in labels
                        for segment in one.location.container_path))
            signals[kind] = tuple(sorted(one.raw_value for one in readings))
            for one in readings:
                cited[cite(one)] = one
        photos.append(_Photo(
            file_id=file_id, content_hash=content_hash,
            cited=tuple(cited[key] for key in sorted(cited)), signals=signals))
    return tuple(photos)


def photo_events(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                 clustering: PhotoEventClustering) -> Mapping[str, str]:
    """Done-means 26. `file_id -> fact_id` for every member of a photo event.

    An image that offered none of §4.2's three inputs gets no fact AND no `unresolved`
    row: the abstention record names "the field that was attempted", and a file that
    proposed nothing was never attempted. Recording it would make the abstention table
    a list of every image in the corpus.

    The event's name is a digest of its members -- `sha256_of(canonical_json(sorted
    member file ids)))` -- so nothing about where the photographs sat reaches a value.
    Adding a member renames the event, which is stated rather than hidden.
    """
    photos = _read(conn, file_ids, clustering)
    by_id = {photo.file_id: photo for photo in photos}
    offered = sorted(photo.file_id for photo in photos if photo.offered)
    parent = {file_id: file_id for file_id in offered}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    for left, right in combinations(offered, 2):
        if clustering.same_event(by_id[left].signals, by_id[right].signals):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in offered:
        components.setdefault(find(file_id), []).append(file_id)

    written: dict[str, str] = {}
    for members in sorted(components.values()):
        if len(members) < clustering.minimum_members:
            continue
        canonical_value = sha256_of(canonical_json(sorted(members)))
        for file_id in members:
            photo = by_id[file_id]
            refs = tuple(sorted(cite(one) for one in photo.cited))
            value_id = ensure_value(
                conn, field_key=EVENT_FIELD, canonical_value=canonical_value,
                first_evidence_ref=refs[0], origin=VALUE_ORIGINS[0])
            written[file_id] = write_fact(
                conn, file_id=file_id, content_hash=photo.content_hash,
                field_key=EVENT_FIELD, value_id=value_id,
                reliability_state=EVENT_STATE, origin=RULE,
                evidence_refs=refs,
                cache_key=pass_cache_key(conn, file_id=file_id,
                                          content_hash=photo.content_hash),
                active=True)
    return written


def _abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
             reason: str, considered: tuple[Observation, ...]) -> None:
    """B7: a refusal is a row naming the field, the reason, and what it looked at."""
    write_unresolved(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, reason=reason,
        attempted_producers=(RULE_ROUTE,),
        evidence_refs=tuple(sorted(cite(one) for one in considered)),
        cache_key=pass_cache_key(conn, file_id=file_id,
                                  content_hash=content_hash))


def media_type(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               tier_weight: Mapping[int, float], minimum_score: float,
               minimum_margin: float) -> str | None:
    """Done-means 27. §2.6's two hypotheses, ranked by §3.7's ordinary procedure.

    Every tiered observation is one weighted vote: the screenshot band votes
    `screenshot`, every other band votes `photograph`. The weights are injected --
    §3.7's numbers are Deferred and the SPEC files the tier-to-weight mapping with
    them -- and the ranking, the score floor, the margin and the two refusal rows they
    produce all belong to `facts.facets.fill_or_abstain`.

    Two refusals happen here rather than there, and each is a sentence of §2.6:

    * no tiered observation at all -> `no_candidate_evidence`. Nothing was read about
      this image, so there is nothing to rank and nothing to cite (rule 1).
    * only screenshot-band observations -> `below_margin`. "The system must not
      mistake the absence of EXIF for proof that an image is a screenshot", and that
      band is what EVERY image carries, so it separates the two hypotheses by nothing.
      Left to the arithmetic this file has one candidate, no second-best, and clears
      any injected margin -- which is exactly A07's forbidden value. The reason is
      §2.6's own: the SPEC files "the conflicting-image-signal case (§2.6)" under
      `below_margin`.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    tiered = tuple(one for one in observations if one.signal_tier in SIGNAL_TIERS)
    if not tiered:
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason=NO_CANDIDATE_EVIDENCE, considered=())
        return None
    if all(one.signal_tier in SCREENSHOT_BAND for one in tiered):
        _abstain(conn, file_id=file_id, content_hash=content_hash,
                 reason=BELOW_MARGIN, considered=tiered)
        return None

    candidates: list[Candidate] = []
    for value, band in ((MEDIA_TYPES[0], PHOTO_BANDS),
                        (MEDIA_TYPES[1], SCREENSHOT_BAND)):
        voters = tuple(one for one in tiered if one.signal_tier in band)
        if not voters:
            # A candidate with nothing to cite is not a candidate (rule 1). It is
            # also not a subtraction: a signal P5 never wrote moves neither side.
            continue
        candidates.append(Candidate(
            value=value,
            score=sum(tier_weight[one.signal_tier] for one in voters),
            evidence_refs=tuple(sorted(cite(one) for one in voters))))

    return fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash,
        field_key=MEDIA_TYPE_FIELD, candidates=tuple(candidates),
        minimum_score=minimum_score, minimum_margin=minimum_margin)

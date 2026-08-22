# src/privacy/items.py
"""§8.4's compact dossier: the six kinds a request may name, and the nine it may not.

§8.4: "When a cloud model is used, the engine should send only a compact dossier
relevant to the current question: selected excerpts, redacted identifiers, candidate
labels, non-sensitive metadata, and evidence references." That is FIVE. `filename` is
a sixth, adopted by P7's SPEC and held unratified here -- see `FILENAME_OPEN_QUESTION`
and `UNRATIFIED_ITEM_KINDS`, NEEDS-JOSEPH B5d and C9a.

Every item carries a REFERENCE. SPEC §6: "requested_items[] item kinds from §4 above
-- references only, never materialised content." A field named `value` on any of these
would make that sentence false, so there is none: an excerpt is an
`(observation_key, span)` address, an evidence reference is "an id only -- no
content", a metadata field is a NAME, and a filename is a `file_id`. `resolve.py` is
the one module that turns a reference into a string.

Two refusals fire at CONSTRUCTION, because the skeleton's word is "not expressible"
and Task 20 is already written against it: a request naming one of §8.4's nine
always-local items cannot be built, so it cannot be a fixture either.

  AlwaysLocalRequested  -- a `MetadataField` naming one of the nine, or a `Filename`
                           whose `file_id` is a path.
  WholeDocumentRequested -- raised by `check_item`, not here: it needs the stored unit
                           length, which only `resolve.materialise` can supply.

This module holds no threshold, no regex, no gazetteer and no keyword list. The nine
names come from `vocabulary.ALWAYS_LOCAL`, which Task 2 derives from §8.4's own
sentence; `_normalise` is Task 2's transformation and nothing more. The consequence is
that `MetadataField(name="current_path")` is NOT caught, and that gap is deliberate
and tested: a synonym list would be a detection rule P7 is forbidden to own.

It also imports neither `defaults` nor `policy`. Task 6's local-first posture is a
DEFAULT that a user may change; the always-local nine are not a posture at all, and a
module with no mode to branch on is the structural way to say so.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Container, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import TextSpan
from evidence_shape.store import runs_for_file
from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    ALWAYS_LOCAL, ITEM_KINDS, OPEN_QUESTIONS, OutOfVocabulary, check_item_kind,
)


class AlwaysLocalRequested(ValueError):
    """§8.4's nine, named in a request. SPEC §3: "Nothing in this set can be named as
    a releasable item kind. The gate has no code path that materialises one."

    Task 13's `deny_always_local_item` translates a caught instance into the gate's
    `Denied(always_local_item)`; it does not re-decide which names are always-local.
    """


class WholeDocumentRequested(ValueError):
    """§8.4: the engine "should not send full documents where a short heading or OCR
    excerpt is enough to resolve the question." Raised by `check_item`, which is the
    first point at which the stored unit length is known.
    """


class UnratifiedItemKind(ValueError):
    """A kind §8.4's own sentence does not name, admitted without the opt-in.

    Deliberately NOT one of `vocabulary.DENIAL_REASONS`: this is a build defect, not
    a policy outcome, and it must reach the developer rather than a user who might
    try to consent around it.
    """


class ProtectedItemRequested(ValueError):
    """§7.3: `Protected Records` "must not cause filenames or content to be exposed
    in model prompts." Scoped here to the filename; the content half is Task 13's
    `protected_records_template`, so the rule keeps one home each.
    """


def _normalise(name: str) -> str:
    """Task 2's transformation, and not a second one.

    Task 2 derives `ALWAYS_LOCAL` from §8.4's sentence with
    `word.lower().replace(" ", "_")`. Using anything wider here would be a keyword
    rule; using anything narrower would let "GPS" through while refusing "gps".
    """
    return name.strip().lower().replace(" ", "_")


def _refuse_always_local_name(field: str, value: str) -> None:
    key = _normalise(value)
    if key in ALWAYS_LOCAL:
        raise AlwaysLocalRequested(
            f"{field}={value!r} names {key!r}, which §8.4 places in the always-local "
            f"set: 'Paths, complete extracted text, OCR output, file hashes, image "
            f"EXIF, GPS, user edits, group memberships, and raw sensitive values "
            f"should remain local.' Nothing in that set can be named as a releasable "
            f"item kind, so the request is not constructible rather than merely "
            f"denied. §8.4's releasable five are: selected excerpts, redacted "
            f"identifiers, candidate labels, non-sensitive metadata, and evidence "
            f"references."
        )


@dataclass(frozen=True)
class Excerpt:
    """SPEC §4: `{ observation_key, span, reason }`, "resolved by the gate from local
    storage". The span is the whole of what bounds it -- an excerpt with no bound is
    the full document §8.4 forbids.

    `span` is `TextSpan | None`: `None` is §2.3's cell and §2.8's EXIF field, where
    `unit_for_observation` returns `None` and the address is the whole citation
    (Task 9's pin). It is never "unbounded".
    """

    observation_key: str
    span: TextSpan | None
    reason: str


@dataclass(frozen=True)
class RedactedIdentifier:
    """SPEC §4: `{ observation_key, span, identifier_class }`.

    `identifier_class` is an OPAQUE string. SPEC *Deferred*: "Which identifier classes
    exist and how each is transformed is not enumerated anywhere in the design." Task 8
    carries it through to the manifest; this module enumerates none.
    """

    observation_key: str
    span: TextSpan | None
    identifier_class: str


@dataclass(frozen=True)
class CandidateLabel:
    """SPEC §4: "a label already present in the local database (§4.5, §5.4)".

    A DESTINATION name, not a kind of data -- which is why the always-local check does
    not run over it. A label carries no observation and no value, so a label reading
    "GPS" releases the word and nothing else.
    """

    label: str


@dataclass(frozen=True)
class MetadataField:
    """SPEC §4: "a named non-sensitive field (e.g. file type, page count, capture
    year)". The NAME only -- the gate looks the value up, per SPEC §6's "references
    only, never materialised content".

    This is the single field in the product through which one of §8.4's nine could be
    NAMED, which is why it is the one that is checked.
    """

    name: str

    def __post_init__(self) -> None:
        _refuse_always_local_name("name", self.name)


@dataclass(frozen=True)
class EvidenceReference:
    """SPEC §4: "an id only -- no content"."""

    observation_key: str


@dataclass(frozen=True)
class Filename:
    """The unratified sixth kind. NEEDS-JOSEPH B5d and C9a; SPEC Open question 2.

    Carries a `file_id`, not a name: SPEC §6 says requests carry references only, and
    the gate is what resolves the reference. A `file_id` holding a path separator is
    a path wearing an id's field name, and §8.4's first always-local word is "Paths".
    """

    file_id: str

    def __post_init__(self) -> None:
        if "/" in self.file_id or "\\" in self.file_id:
            raise AlwaysLocalRequested(
                f"file_id={self.file_id!r} carries a path separator, and §8.4 places "
                f"'paths' in the always-local set. `Filename` carries P1's opaque "
                f"file id; the gate resolves the name. A file id that is a path is a "
                f"path wearing an id's field name."
            )


RequestedItem = (Excerpt | RedactedIdentifier | CandidateLabel | MetadataField
                 | EvidenceReference | Filename)

#: Every branch in this module keys off `kind_of`, so `ITEM_KINDS` is the one place a
#: seventh kind would have to be added. Validated through Task 2's checker at import,
#: so these are provably members of the closed vocabulary and not a second spelling.
_KIND_BY_TYPE: Mapping[type, str] = MappingProxyType({
    Excerpt: check_item_kind("excerpt"),
    RedactedIdentifier: check_item_kind("redacted_identifier"),
    CandidateLabel: check_item_kind("candidate_label"),
    MetadataField: check_item_kind("metadata_field"),
    EvidenceReference: check_item_kind("evidence_reference"),
    Filename: check_item_kind("filename"),
})

#: §8.4's own five, in the design's order.
RATIFIED_ITEM_KINDS: tuple[str, ...] = (
    _KIND_BY_TYPE[Excerpt], _KIND_BY_TYPE[RedactedIdentifier],
    _KIND_BY_TYPE[CandidateLabel], _KIND_BY_TYPE[MetadataField],
    _KIND_BY_TYPE[EvidenceReference],
)

#: The sixth. Built, named, and unadmittable without `allow_unratified=True`.
UNRATIFIED_ITEM_KINDS: tuple[str, ...] = (_KIND_BY_TYPE[Filename],)

#: SPEC Open question 2, quoted from `vocabulary.OPEN_QUESTIONS` rather than retyped,
#: so the module and the SPEC's list cannot drift apart. NEEDS-JOSEPH B5d and C9a.
FILENAME_OPEN_QUESTION: str = OPEN_QUESTIONS[2]

#: Kind -> field names, READ from the dataclasses. Retyping them would be a second
#: home for a shape SPEC §4 already fixes, and the field list is what the "no content
#: field" guard reads.
ITEM_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    kind: tuple(field.name for field in dataclasses.fields(cls))
    for cls, kind in _KIND_BY_TYPE.items()
})


def kind_of(item: object) -> str:
    """The `ITEM_KINDS` name for one item. A foreign type is a load error (A13)."""
    kind = _KIND_BY_TYPE.get(type(item))
    if kind is None:
        raise OutOfVocabulary(
            f"{type(item).__name__!r} is not one of the {len(ITEM_KINDS)} releasable "
            f"item kinds the design defines {ITEM_KINDS}. §8.4's vocabularies are "
            f"closed: an unrecognised kind is a load error, not a fallback."
        )
    return kind


def is_whole_document(item: object, *, unit_length: int | None) -> bool:
    """§8.4: "It should not send full documents where a short heading or OCR excerpt
    is enough to resolve the question."

    `unit_length is None` is the container-path form -- §2.3's cell, §2.8's EXIF
    field -- where `unit_for_observation` returns `None` and there is no unit for a
    span to cover. Reading it as length zero would make every cell a whole document.
    """
    if "span" not in ITEM_FIELDS[kind_of(item)]:
        return False
    span = item.span
    if span is None or unit_length is None:
        return False
    return span.start <= 0 and span.end >= unit_length


def check_item(item: object, *, unit_length: int | None, protected: bool,
               sensitive_keys: Container[str], allow_unratified: bool) -> None:
    """The release-time half of §8.4's item rules. Returns None or raises (A11).

    Four required keywords, no defaults. `sensitive_keys` in particular: a default of
    the empty set would mean "nothing is sensitive" for a caller who never wired P5,
    which is the same shape of failure as a column with no writer.

    The order matches `release.DECISION_ORDER`: always-local before whole-document,
    so an item that fails both is reported as the stronger refusal.

    Not checked here, on purpose:
      * the always-local NAMES -- refused in `__post_init__`, so a request holding one
        is unconstructible;
      * protected CONTENT and the cloud-prompt default -- Task 13's
        `protected_records_template` and `protected_cloud_target`.
    """
    kind = kind_of(item)

    if kind in UNRATIFIED_ITEM_KINDS and not allow_unratified:
        raise UnratifiedItemKind(
            f"{kind!r} is a releasable item kind §8.4's own sentence does not name. "
            f"§8.4 names five -- selected excerpts, redacted identifiers, candidate "
            f"labels, non-sensitive metadata, and evidence references -- and puts "
            f"paths in the always-local set. P7's SPEC adds this sixth on the reading "
            f"that §7.3's carve-out is otherwise vacuous, and flags it as its own "
            f"Open question 2. NEEDS-JOSEPH B5d and C9a. Pass allow_unratified=True "
            f"to admit it deliberately; there is no default."
        )

    if protected and kind in UNRATIFIED_ITEM_KINDS:
        raise ProtectedItemRequested(
            f"§7.3: a Protected Records file 'should normally remain local-only and "
            f"must not cause filenames or content to be exposed in model prompts.' "
            f"That sentence carries no locality qualifier, so a {kind!r} on a "
            f"protected file is refused for any target. §8.4's 'not included in "
            f"cloud-model prompts by default' is what the consent path reopens, and "
            f"that path is NeedsConsent."
        )

    if kind == _KIND_BY_TYPE[Excerpt] and item.observation_key in sensitive_keys:
        raise AlwaysLocalRequested(
            f"observation {item.observation_key!r} was marked "
            f"{POTENTIALLY_SENSITIVE!r} at emission, and §8.4 places "
            f"'raw_sensitive_values' in the always-local set. §8.4 permits 'redacted "
            f"identifiers', so the same key is releasable as a RedactedIdentifier, "
            f"whose transform is injected with no default."
        )

    if is_whole_document(item, unit_length=unit_length):
        raise WholeDocumentRequested(
            f"span {item.span.start}-{item.span.end} covers the whole of a "
            f"{unit_length}-character text unit. §8.4: the engine 'should not send "
            f"full documents where a short heading or OCR excerpt is enough to "
            f"resolve the question.'"
        )


def sensitive_observation_keys(conn: sqlite3.Connection,
                               file_id: str) -> frozenset[str]:
    """P4's runs for a file -> P5's per-value sensitivity signals (A13).

    P7 owns no detector, and this is the only per-value sensitivity signal in the
    product. P5 assigns no handling class -- §8.4 gives classification to P7 -- so
    this says "P5 saw a value worth redacting", never "this file is sensitive".

    An empty set means NOTHING WAS SIGNALLED, not "nothing is sensitive". The two
    published readers are composed here; no reader is added to P4 or P5.
    """
    keys: set[str] = set()
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                keys.add(row["observation_key"])
    return frozenset(keys)

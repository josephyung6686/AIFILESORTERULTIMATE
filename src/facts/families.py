# src/facts/families.py
"""G5 -- the duplicate family and the version family (§2.6, §2.9, §3.11, §8.3).

Both are §3.11 universal fields and **version family had no owner anywhere in the
design**. §2.9 lists "duplicate and version-family signals" among what basic
extraction produces and defines neither, so this module builds the two ends the
design does state and holds the middle open:

    byte identity          §8.3: "A content-hash match supports deduplication
                           review; a filename match alone does not."     -> `direct`
    near-duplicates        §2.6: "Exact hashes and perceptual hashes can identify
                           duplicates and near-duplicates."              -> `possible`
    shared lineage         nothing states it                             -> injected

**Why the decision and the citation are different objects.** P1's `content_hash`
lives on the `files` row and is not an observation -- `extractors/filesystem.py`
deliberately does not re-emit it, because "a second copy here would be two homes for
one value". So the hash decides membership and cannot be cited for it. What is cited
is the observations the members SHARE: `observation_key` hashes
`content_hash / extractor_name / locator / raw_value` and nothing else, so two files
holding the same bytes produce literally the same keys for every extractor that read
those bytes. The citation is a consequence of byte identity, not a proxy for it.

When the shared set is empty, this module abstains: a fact with no citable evidence
is not a fact, and the refusal is a row (B7), not a gap.

**No filename ever establishes either family.** `report (1).pdf` and
`invoice (1).pdf` share a suffix and nothing else. That pair produces no fact and no
`unresolved` row: the SPEC's `unresolved` schema records "the field that was
attempted", and a relation nobody proposed was never attempted.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from itertools import combinations
from typing import Callable, Iterable

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, check

from facts.cache import pass_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import (
    DETERMINISTIC_EXTRACTOR, FACT_ORIGINS, RULE, facts_for_file, write_fact,
)
from facts.states import DIRECT, POSSIBLE, VALIDATED
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, RULE_ROUTE,
    write_unresolved,
)
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.11's universal field keys, snake_case per D6. Resolved through the catalogue on
#: every write, so a drift raises `FieldNotInCatalogue` rather than inserting a field.
DUPLICATE_FAMILY_FIELD: str = "duplicate_family"
VERSION_FAMILY_FIELD: str = "version_family"

#: The NAME of the required keyword the container-path label arrives under -- not the
#: label. P5 spells the label and it has a space in it; a copy here would be a second
#: home for one string. Task 25 asserts this names a keyword-only parameter of
#: `duplicate_family` with no default.
PERCEPTUAL_HASH_LABEL: str = "perceptual_hash_label"

#: Done-means 24: a version family is never `direct`, because no explicit slot states
#: a version relation. §3.13: a deterministic rule that passes a contextual check is
#: `validated`; anything weaker is `possible`. Two of the six, named through
#: `facts.states` -- this is not a second copy of the vocabulary (preamble §3.1).
VERSION_FAMILY_STATES: tuple[str, str] = (VALIDATED, POSSIBLE)


@dataclass(frozen=True)
class Lineage:
    """One injected rule's verdict that two file versions share lineage.

    The rule is the caller's: §2.9 names the signals and states none of them. What
    this type enforces is the half the design DOES state -- that the answer is never
    `direct`.
    """
    family_value: str
    reliability_state: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.reliability_state, VERSION_FAMILY_STATES, name="reliability_state")


@dataclass(frozen=True)
class _Version:
    """One (file, content hash) with its evidence already read once."""
    file_id: str
    content_hash: str
    observations: tuple[Observation, ...]

    @property
    def keys(self) -> frozenset[str]:
        return frozenset(cite(one) for one in self.observations)


def _read(conn: sqlite3.Connection, file_ids: Iterable[str]) -> tuple[_Version, ...]:
    """Every version, in file-id order.

    Sorted before anything is decided. P4's reads are in insertion order (verified by
    execution) and insertion order is a property of one database, not of the corpus;
    a computation that inherited it would make the same corpus resolve differently
    depending on the order it was extracted in.
    """
    versions = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        content_hash = row["content_hash"]
        versions.append(_Version(
            file_id=file_id, content_hash=content_hash,
            observations=tuple(observations_for_version(conn, file_id, content_hash))))
    return tuple(versions)


def _abstain(conn: sqlite3.Connection, *, version: _Version, field_key: str,
             producer: str) -> None:
    """B7: a refusal is a row naming the field and the reason it refused."""
    write_unresolved(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, reason=NO_CANDIDATE_EVIDENCE,
        attempted_producers=(producer,), evidence_refs=(),
        cache_key=pass_cache_key(conn, file_id=version.file_id,
                              content_hash=version.content_hash))


def _write_family(conn: sqlite3.Connection, *, version: _Version, field_key: str,
                  canonical_value: str, reliability_state: str, origin: str,
                  evidence_refs: tuple[str, ...],
                  cited: tuple[Observation, ...]) -> str:
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=canonical_value,
                            first_evidence_ref=evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, value_id=value_id,
        reliability_state=reliability_state, origin=origin,
        evidence_refs=evidence_refs,
        cache_key=pass_cache_key(conn, file_id=version.file_id,
                              content_hash=version.content_hash),
        active=True)


def _family_values(conn: sqlite3.Connection, file_id: str) -> dict[str, set[str]]:
    """This file version's active family values, by field key.

    Keyed on the field rather than flattened, because the whole question below is
    WHICH of the two fields two files meet in, and a flat set of values cannot say.

    `read_surface.family_facts` is the published read over exactly these two keys and
    is deliberately NOT used: it imports both field constants from this module, so
    depending on it here would be an import cycle. This reads what it filters, one
    layer down, and narrows on the same two keys.
    """
    content_hash = dict(get_file(conn, file_id))["content_hash"]
    values: dict[str, set[str]] = {DUPLICATE_FAMILY_FIELD: set(),
                                   VERSION_FAMILY_FIELD: set()}
    for row in facts_for_file(conn, file_id, content_hash):
        if row["active"] and row["field_key"] in values:
            values[row["field_key"]].add(row["canonical_value"])
    return values


def shared_family_field(conn: sqlite3.Connection, *, left_file_id: str,
                        right_file_id: str) -> str | None:
    """Which family field, if either, these two file versions share a value in.

    **Written because binding `duplicate_family` makes P9's `duplicate_or_version`
    authority compulsory rather than optional.** `grouping.retrieval` opens its
    `duplicate-or-version-link` channel off `family_facts`, which covers BOTH fields,
    and `grouping.graph._edge_type` then RAISES `ConfigurationRequired` if it has no
    authority to say which one an edge is: "the wrong answer puts two revisions of
    one document into a group as two documents." Verified by running the product --
    with the families bound and this unbound, a corpus holding one duplicate pair
    stops the run.

    **P6 answers with its OWN field key and never with P9's word.** P9 spells the two
    verdicts in `grouping.vocabulary` (`DUPLICATE`, `VERSION_FAMILY`) and a copy of
    either here would be a second home for one string. The composition root maps this
    key onto that vocabulary, which is the one place allowed to know both.

    `None` when they meet in neither, and that is not a defect: a caller obliged to
    produce one of two words must be able to tell that neither is true, or P9's
    refusal turns into P6's coin toss.

    Duplicate wins a tie it cannot actually have. Identical hashes are excluded from
    version families by `version_family` itself, so no pair can be in both; the order
    states which claim would be the stronger one if that ever changed -- `direct`
    byte identity over an injected rule's `possible`.
    """
    left = _family_values(conn, left_file_id)
    right = _family_values(conn, right_file_id)
    for field_key in (DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD):
        if left[field_key] & right[field_key]:
            return field_key
    return None


def duplicate_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     perceptual_hash_label: str,
                     near_match: Callable[[str, str], bool]) -> tuple[str, ...]:
    """Done-means 23. Byte identity is `direct`; a near match is at most `possible`.

    `perceptual_hash_label` and `near_match` are required with no default. §2.6 names
    the perceptual hash and states no distance metric and no threshold, so P6 holds
    neither; the label is P5's string and P6 holds no copy of it.

    **The family is NAMED by its shared citations, never by the content hash.** The
    header above already separates deciding from citing -- "the hash decides
    membership and cannot be cited for it" -- and the name is a third thing again,
    on the far side of a privacy line the other two never cross. §8.4 puts
    `file_hashes` among the nine that never leave the device, and a fact's value is
    RELEASABLE by design: `grouping.seeds` reads `family_facts` into its anchor rows
    deliberately, so the value becomes a `Seed`, and from there
    `grouping.naming.label_for` puts it on a group's display label and
    `grouping.dossier` puts it in `key_facts`, which is the half of a candidate-group
    dossier that reaches a model. None of those three is wrong and none of them is
    P6's to change. What is P6's is not to hand them an always-local value.

    So the name is `sha256_of(canonical_json(shared))` -- the fingerprint of the
    citation set the members share -- which is the shape `_near_families` already
    uses. Its decisive property is that it releases nothing new: every input is an
    observation key, and observation keys already cross the wire as
    `EvidenceItem.observation_key`. A digest of the content hash would NOT have that
    property; it is a deterministic function of the bytes under a published
    algorithm, so it confirms possession of a known file exactly as the hash does,
    and renaming it would be a fig leaf rather than a fix.

    **The cost, stated rather than hidden: this name is not stable across a change
    in extraction coverage.** `shared` is the intersection of what was actually read,
    so re-scanning with a reader that emits one more observation mints a second value
    for the same family. The content hash would have been stable for ever. That is
    the trade accepted here, and it is the same one `_near_families` accepted when it
    named a near-family after the perceptual readings that happened to exist.
    """
    versions = _read(conn, file_ids)
    written: list[str] = []

    by_hash: dict[str, list[_Version]] = {}
    for version in versions:
        by_hash.setdefault(version.content_hash, []).append(version)

    # `_hash` is the grouping key and NOT the family's name: see the docstring.
    for _hash, members in sorted(by_hash.items()):
        if len(members) < 2:
            continue
        shared = sorted(frozenset.intersection(*(m.keys for m in members)))
        for member in members:
            if not shared:
                _abstain(conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                         producer=DIRECT_ROUTE)
                continue
            cited = tuple(one for one in member.observations
                          if cite(one) in set(shared))
            written.append(_write_family(
                conn, version=member, field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=sha256_of(canonical_json(shared)),
                reliability_state=DIRECT,
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=tuple(shared),
                cited=cited))

    written.extend(_near_families(conn, versions=versions,
                                  perceptual_hash_label=perceptual_hash_label,
                                  near_match=near_match))
    return tuple(written)


def _perceptual(version: _Version, label: str) -> tuple[Observation, ...]:
    """Every observation whose container path carries the injected label."""
    return tuple(
        one for one in version.observations
        if any(segment.label == label
               for segment in one.location.container_path))


def _near_families(conn: sqlite3.Connection, *, versions: tuple[_Version, ...],
                   perceptual_hash_label: str,
                   near_match: Callable[[str, str], bool]) -> list[str]:
    """§2.6's near-duplicates, at `possible` and never above.

    Pairs already in one exact family are skipped: they are a duplicate family at
    `direct` already, and a weaker second fact over the same members for the same
    field is noise rather than evidence.
    """
    carriers = {version.file_id: readings
                for version in versions
                if (readings := _perceptual(version, perceptual_hash_label))}
    # The pair loop below is quadratic, and this is what bounds it: it enumerates
    # PERCEPTUAL-HASH CARRIERS, never the roster. A corpus of 10,000 files with no
    # perceptual hash in it does no work here at all -- which is today's case, since
    # the wired `readers.image_headers` reader supplies none, measured 0 carriers on
    # both real corpora. Returning early is not an optimisation of that; it is so
    # that the bound is stated in the code rather than inferred from a dict
    # comprehension by the next person who reads this for its cost.
    if len(carriers) < 2:
        return []
    parent = {file_id: file_id for file_id in carriers}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    by_id = {version.file_id: version for version in versions}
    for left, right in combinations(sorted(carriers), 2):
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        if any(near_match(a.raw_value, b.raw_value)
               for a in carriers[left] for b in carriers[right]):
            parent[find(left)] = find(right)

    components: dict[str, list[str]] = {}
    for file_id in sorted(carriers):
        components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        raws = sorted({one.raw_value for file_id in members
                       for one in carriers[file_id]})
        canonical_value = sha256_of(canonical_json(raws))
        for file_id in members:
            cited = carriers[file_id]
            refs = tuple(sorted(cite(one) for one in cited))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=DUPLICATE_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state=POSSIBLE,
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=refs, cited=cited))
    return written


def version_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                   lineage_rule: Callable[[sqlite3.Connection, str, str],
                                          "Lineage | None"]) -> tuple[str, ...]:
    """Done-means 24. Distinct content hashes, never `direct`, never a filename.

    `lineage_rule` is required with no default and receives the connection and the
    two file ids: §2.9 names the signals and defines none, so P6 states nothing about
    what a lineage is and a rule that establishes nothing writes nothing.

    A family is only as strong as its weakest link -- a component joined by one
    `validated` edge and one `possible` edge is written at `possible`, because the
    component is only connected at all through the weaker claim.
    """
    versions = _read(conn, file_ids)
    by_id = {version.file_id: version for version in versions}
    parent = {version.file_id: version.file_id for version in versions}
    edges: dict[str, list[Lineage]] = {}

    def find(file_id: str) -> str:
        while parent[file_id] != file_id:
            parent[file_id] = parent[parent[file_id]]
            file_id = parent[file_id]
        return file_id

    refused: set[str] = set()
    for left, right in combinations(sorted(by_id), 2):
        # Identical hashes are a duplicate family, never a version family.
        if by_id[left].content_hash == by_id[right].content_hash:
            continue
        lineage = lineage_rule(conn, left, right)
        if lineage is None:
            continue
        if not lineage.evidence_refs:
            refused.update((left, right))
            continue
        parent[find(left)] = find(right)
        for file_id in (left, right):
            edges.setdefault(file_id, []).append(lineage)

    for file_id in sorted(refused):
        if file_id not in edges:
            _abstain(conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                     producer=RULE_ROUTE)

    components: dict[str, list[str]] = {}
    for file_id in sorted(by_id):
        if file_id in edges:
            components.setdefault(find(file_id), []).append(file_id)

    written: list[str] = []
    for members in sorted(components.values()):
        if len(members) < 2:
            continue
        lineages = [one for file_id in members for one in edges[file_id]]
        canonical_value = min(one.family_value for one in lineages)
        weakest = (POSSIBLE if any(one.reliability_state == POSSIBLE
                                   for one in lineages) else VALIDATED)
        for file_id in members:
            refs = tuple(sorted({ref for one in edges[file_id]
                                 for ref in one.evidence_refs}))
            cited = tuple(one for one in by_id[file_id].observations
                          if cite(one) in set(refs))
            written.append(_write_family(
                conn, version=by_id[file_id], field_key=VERSION_FAMILY_FIELD,
                canonical_value=canonical_value, reliability_state=weakest,
                origin=RULE, evidence_refs=refs, cited=cited))
    return tuple(written)

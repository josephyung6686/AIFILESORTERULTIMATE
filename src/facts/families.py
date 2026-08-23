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

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import DETERMINISTIC_EXTRACTOR, FACT_ORIGINS, RULE, write_fact
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


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a fact built from several observations.

    §3.4 states one extractor version and one analysis tier; a fact citing several
    observations has several of each, and no task owns the reconciliation. The rule
    is written out here rather than shared because `facts.cache` is another task's
    module: the versions are the canonical JSON of the sorted distinct
    (name, version) pairs, and the tier is the LAST one present in `ANALYSIS_TIERS`
    order -- filesystem < native < ocr < llm -- so a fact that cited an `ocr`
    reading lands outside the cache slot the native pass computed under, which is
    what makes preamble rule 5's pass 4 supersede rather than overwrite. Identical
    wording in `facts.direct`, `facts.discount` and `facts.session`; see Contract
    ambiguities.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    tier = max(tiers, key=ANALYSIS_TIERS.index) if tiers else ANALYSIS_TIERS[0]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)


def _abstain(conn: sqlite3.Connection, *, version: _Version, field_key: str,
             producer: str) -> None:
    """B7: a refusal is a row naming the field and the reason it refused."""
    write_unresolved(
        conn, file_id=version.file_id, content_hash=version.content_hash,
        field_key=field_key, reason=NO_CANDIDATE_EVIDENCE,
        attempted_producers=(producer,), evidence_refs=(),
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=version.observations))


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
        cache_key=_cache_key(conn, content_hash=version.content_hash,
                             observations=cited),
        active=True)


def duplicate_family(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     perceptual_hash_label: str,
                     near_match: Callable[[str, str], bool]) -> tuple[str, ...]:
    """Done-means 23. Byte identity is `direct`; a near match is at most `possible`.

    `perceptual_hash_label` and `near_match` are required with no default. §2.6 names
    the perceptual hash and states no distance metric and no threshold, so P6 holds
    neither; the label is P5's string and P6 holds no copy of it.
    """
    versions = _read(conn, file_ids)
    written: list[str] = []

    by_hash: dict[str, list[_Version]] = {}
    for version in versions:
        by_hash.setdefault(version.content_hash, []).append(version)

    for content_hash, members in sorted(by_hash.items()):
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
                canonical_value=content_hash, reliability_state=DIRECT,
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

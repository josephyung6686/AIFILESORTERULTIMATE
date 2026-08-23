# src/facts/facets.py
"""§3.7 conservative facet extraction: word boundary, positional weight, score, margin.

§3.7, verbatim and in its own order: *"It should use word-boundary matching rather
than substring matching. Without this rule, names such as MIT can be found inside
"submit," and UNC can be found inside "uncertainty," producing polished but
completely false filing paths. It should use positional weighting because a value in
a filename or document title carries more meaning than the same value in a footer or
a late body-page reference. It should rank candidate matches instead of accepting the
first match, and it should require both a minimum score and a minimum margin over the
second-best candidate before it fills a facet."*

Four obligations, and this module is all four:

1. word-boundary matching, never substring;
2. positional weighting off P4's `location.zone`;
3. ranked candidates, never first-match;
4. a minimum score AND a minimum margin, both cleared, before a facet is filled.

**Every weight and every threshold is a required keyword with no default.** §3.7's
numbers are Deferred -- the SPEC's own table lists "Minimum score and minimum margin
values", "Positional weight per document zone" and "Signal-tier weights for §2.6's
three bands" as manual work. A default here would answer them.

**The total order is this module's, not P4's.** `observations_for_file` orders by
rowid, which is insertion order and is not a property of the corpus. `rank` therefore
sorts by (weighted score descending, smallest cited observation key ascending, value
ascending) before anything looks at the first element, and `fill_or_abstain` applies
the same order again to its own input. Without that, a tie is decided by whichever
run happened to be written first and §8.5's replay reports a regression when nothing
changed.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import pass_cache_key
from facts.evidence import (
    analysis_tier_for_observation, observations_for_version,
)
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value


#: §3.13's third state. Rule 2: the six literals are P4's and P6 re-spells none of
#: them, so every state in this module is addressed by its index into P4's tuple.
_VALIDATED = VALIDATED


class MissingWeight(KeyError):
    """A zone or signal tier with no injected weight. P6 invents no number."""


@dataclass(frozen=True, slots=True)
class Candidate:
    """One candidate value for one field.

    `value`, `score` and `evidence_refs` are the published three. `zone` and
    `signal_tier` are the two P4 descriptors `rank` weights by; they are present on a
    contribution (one candidate from one observation) and cleared on the aggregate
    `rank` returns, because a ranked candidate spans several positions and a single
    zone would be a lie about where it came from.
    """

    value: str
    score: float
    evidence_refs: tuple[str, ...]
    zone: str | None = None
    signal_tier: int | None = None


def _is_word_character(character: str) -> bool:
    return character.isalnum() or character == "_"


def word_boundary_match(needle: str, haystack: str) -> bool:
    """True when `needle` occurs in `haystack` bounded by non-word characters.

    §3.7's own two cases are the specification: `MIT` must not match inside "submit"
    and `UNC` must not match inside "uncertainty". Both are decided by the boundary
    and not by case, which is why folding case (N-6, required for the §3.5 context
    check that shares this matcher) does not weaken either refusal.

    `re.escape` is applied to the needle: facet values contain `/`, `-`, `+` and `.`
    (`PVA/RDP`, `AY 2024-25`, `C++`), and a needle compiled as a pattern would make
    the value catalogue an injection surface. `\\b` is not used either -- it is
    defined against a word character on both sides, which is wrong for a needle whose
    own first or last character is not one.
    """
    if not needle or not haystack:
        return False
    for match in re.finditer(re.escape(needle), haystack, flags=re.IGNORECASE):
        start, end = match.start(), match.end()
        if _is_word_character(haystack[start]) and start > 0 \
                and _is_word_character(haystack[start - 1]):
            continue
        if _is_word_character(haystack[end - 1]) and end < len(haystack) \
                and _is_word_character(haystack[end]):
            continue
        return True
    return False


def _weight_of(candidate: Candidate, *, zone_weight: Mapping[str, float],
               tier_weight: Mapping[int, float]) -> float:
    if candidate.zone is None:
        raise MissingWeight(
            "a contribution carries P4's location.zone; §3.7's positional weighting "
            "has nothing to weight without it")
    try:
        weight = zone_weight[candidate.zone]
    except KeyError as exc:
        raise MissingWeight(f"no injected weight for zone {candidate.zone!r}") from exc
    if candidate.signal_tier is None:
        # §2.6 is image-scoped (P4 conformance rule 11 ties a non-null signal_tier to
        # source_type == "image"). No tier means the hierarchy does not apply, not
        # that some default band does -- absence is never evidence (§2.6).
        return candidate.score * weight
    try:
        return candidate.score * weight * tier_weight[candidate.signal_tier]
    except KeyError as exc:
        raise MissingWeight(
            f"no injected weight for signal tier {candidate.signal_tier!r}") from exc


def _order(candidate: Candidate) -> tuple[float, str, str]:
    refs = sorted(candidate.evidence_refs)
    return (-candidate.score, refs[0] if refs else "", candidate.value)


def rank(candidates: Iterable[Candidate], *, zone_weight: Mapping[str, float],
         tier_weight: Mapping[int, float]) -> tuple[Candidate, ...]:
    """Aggregate per-observation contributions into weighted, totally ordered candidates.

    Contributions for the same value are summed, so a value stated in a filename and
    again in a heading outranks one stated once in a footer -- which is §3.7's
    positional weighting, expressed as an injected map over P4's fifteen zones rather
    than as a number this module chose.
    """
    weighted: dict[str, float] = {}
    refs: dict[str, set[str]] = {}
    for candidate in candidates:
        score = _weight_of(candidate, zone_weight=zone_weight, tier_weight=tier_weight)
        weighted[candidate.value] = weighted.get(candidate.value, 0.0) + score
        refs.setdefault(candidate.value, set()).update(candidate.evidence_refs)
    aggregated = tuple(
        Candidate(value=value, score=weighted[value],
                  evidence_refs=tuple(sorted(refs[value])))
        for value in weighted)
    return tuple(sorted(aggregated, key=_order))


def fill_or_abstain(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    field_key: str, candidates: Iterable[Candidate],
                    minimum_score: float, minimum_margin: float) -> str | None:
    """Fill the facet, or write the refusal that says why it was not filled.

    Three different refusals, never one: no candidate at all is
    `no_candidate_evidence`; a winner under the floor is `below_score_threshold`; a
    winner too close to the runner-up is `below_margin`. §8.5 asks "Did it abstain
    when evidence was absent?" and a single reason cannot answer it.

    The state is `validated`: §3.13 defines it as "found by a deterministic rule and
    passed contextual checks", and clearing a minimum score and a minimum margin over
    ranked candidates is exactly that check. Nothing here produces `direct` -- no
    explicit slot states a ranked facet -- and nothing here produces `possible`.
    """
    ordered = tuple(sorted(candidates, key=_order))
    if not ordered:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="no_candidate_evidence",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=(),
                         cache_key=pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    considered = tuple(sorted({ref for candidate in ordered
                               for ref in candidate.evidence_refs}))
    winner = ordered[0]
    if winner.score < minimum_score:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_score_threshold",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    if len(ordered) > 1 and winner.score - ordered[1].score < minimum_margin:
        write_unresolved(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, reason="below_margin",
                         attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                         evidence_refs=considered,
                         cache_key=pass_cache_key(conn, file_id=file_id,
                                                   content_hash=content_hash))
        return None
    value_id = ensure_value(conn, field_key=field_key,
                            canonical_value=winner.value,
                            first_evidence_ref=winner.evidence_refs[0],
                            origin=VALUE_ORIGINS[0])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=_VALIDATED, origin=RULE,
                      evidence_refs=winner.evidence_refs,
                      cache_key=pass_cache_key(conn, file_id=file_id,
                                                content_hash=content_hash),
                      active=True)

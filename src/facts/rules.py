# src/facts/rules.py
"""§3.5 rule-validated facts: a pattern match PLUS a strict context check.

§3.5, verbatim and load-bearing: *"Rules create validated facts when a candidate
passes strict context checks. For example, BUSIB 4300 becomes a course fact only when
the engine finds a course-code pattern together with academic context such as
"syllabus," "lecture," "credits," "instructor," or "semester.""*

Five terms are stated literally and they are the only context vocabulary this module
authors. Every other domain's terms arrive on the `Rule`, because the SPEC defers
them: *"Rule context-term lists beyond the five literal academic terms | §3.5 | Only
"syllabus", "lecture", "credits", "instructor", "semester" are stated. Every other
domain's context vocabulary is unauthored."* There is no sixth term here and adding
one is a design change, not an implementation detail.

**The check is case-insensitive (N-6).** §3.5 writes its five terms in lowercase and
states no matching rule, so P6 states one. P4's fixture 1 carries `context_before`
exactly `"Syllabus - "` with a capital S, and B8(a)'s whole purpose was to make the
walking skeleton's one fact resolvable; a case-sensitive reading refuses that fixture
and the skeleton produces no fact at all.

**Case-insensitivity does not relax the word boundary.** The matcher is
`facts.facets.word_boundary_match`, the same one §3.7's facet values go through, so
`semester` still cannot match inside a longer word. One rule, one implementation.

**A truncated context is not a clean refusal.** §8.6 forbids silent truncation, so a
check that fails on a record with `context_truncated = true` writes
`reason = context_truncated` and never `context_check_failed`: the term may have been
cut off, and reporting a considered refusal would be a claim this module cannot make.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key
from facts.evidence import (
    analysis_tier_for_observation, cite, context_pair, observations_for_version,
)
from facts.facets import word_boundary_match
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import VALIDATED
from facts.unresolved import ATTEMPTED_PRODUCERS, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: §3.5's five academic context terms, quoted from the design and complete. This is
#: the ONLY context vocabulary `facts` authors; everything else is injected on a
#: `Rule`. A sixth term is a design change.
ACADEMIC_CONTEXT_TERMS: tuple[str, str, str, str, str] = (
    "syllabus", "lecture", "credits", "instructor", "semester")

#: Task 1 owns the spelling. Never an index into STATES.
_VALIDATED = VALIDATED


class MalformedRule(ValueError):
    """A rule with no pattern, no context term, or no field. §3.5 requires all three."""


@dataclass(frozen=True, slots=True)
class Rule:
    """One injected §3.5 rule: a pattern, the context it demands, and the field it fills.

    Every one of the three is caller-supplied. `facts.rules` authors no course-code
    regex (§3.10's catalogue beyond the three named date patterns is Deferred and a
    course-code pattern is not among them), and it authors no field key -- D6 fixes
    the academic key as `subject`, and a module that spelled it would be a second home
    for `fields`.
    """

    pattern: re.Pattern[str]
    required_context_terms: tuple[str, ...]
    field_key: str

    def __post_init__(self) -> None:
        if not isinstance(self.pattern, re.Pattern):
            raise MalformedRule("a rule matches a compiled pattern, never a string: "
                                "§3.10 requires explicit regular expressions")
        if not self.required_context_terms:
            raise MalformedRule(
                f"rule for {self.field_key!r} demands no context term; §3.5's whole "
                "point is that a pattern match alone is not a fact")
        if not self.field_key:
            raise MalformedRule("a rule names the field it fills")


def context_check(before: str, after: str, terms: Iterable[str]) -> bool:
    """True when any required term appears in either half of §2.8's context pair.

    The two halves are read together and never concatenated (M5): P4 split them so
    §8.4 can redact a value without dropping its context, and joining them here would
    forge an adjacency that the document does not contain.
    """
    haystacks = (before or "", after or "")
    return any(word_boundary_match(term, haystack)
               for term in terms for haystack in haystacks)


def _pass_cache_key(conn: sqlite3.Connection, *, file_id: str,
                    content_hash: str) -> str:
    """§3.4's key for one deterministic pass over one file version.

    Written out here rather than imported from a producer sibling: the SPEC requires
    an `unresolved` row to carry the "same composition as `file_facts` (§3.4), so an
    abstention is invalidated by the same events that invalidate a fact", and the
    reconciliation of several extractor versions into one key belongs to `facts.cache`
    (Task 6), which does not own it yet. See the plan's contract ambiguities.
    """
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(o.extractor_name, o.extractor_version) for o in observations})
    tiers = {analysis_tier_for_observation(conn, o) for o in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    if not present:
        raise ValueError(
            f"no extraction run for {content_hash!r}: §3.4's key has no analysis tier")
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1], model_identifier=None, prompt_fingerprint=None)


def apply_rules(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                rules: Sequence[Rule]) -> tuple[str, ...]:
    """Run every rule over every observation of one file version.

    Three outcomes and they are not interchangeable:

    * the pattern does not match -- nothing at all. A rule that does not apply is not
      a refusal, and writing one would fill `unresolved` with every field every rule
      could theoretically have produced;
    * the pattern matches and the context check passes -- one `validated` fact citing
      that observation's key (M14);
    * the pattern matches and the context check fails -- one `unresolved` row, whose
      reason is `context_truncated` when P4 flagged the context as cut and
      `context_check_failed` when it did not.
    """
    written: list[str] = []
    observations = sorted(observations_for_version(conn, file_id, content_hash),
                          key=lambda o: o.observation_key)
    for observation in observations:
        before, after, truncated = context_pair(observation)
        for rule in rules:
            match = rule.pattern.search(observation.raw_value)
            if match is None:
                continue
            if not context_check(before, after, rule.required_context_terms):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=rule.field_key,
                    reason="context_truncated" if truncated else "context_check_failed",
                    attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                    evidence_refs=(cite(observation),),
                    cache_key=_pass_cache_key(conn, file_id=file_id,
                                              content_hash=content_hash))
                continue
            value_id = ensure_value(conn, field_key=rule.field_key,
                                    canonical_value=match.group(0),
                                    first_evidence_ref=cite(observation),
                                    origin=VALUE_ORIGINS[0])
            written.append(write_fact(
                conn, file_id=file_id, content_hash=content_hash,
                field_key=rule.field_key, value_id=value_id,
                reliability_state=_VALIDATED, origin=RULE,
                evidence_refs=(cite(observation),),
                cache_key=_pass_cache_key(conn, file_id=file_id,
                                          content_hash=content_hash),
                active=True))
    return tuple(written)

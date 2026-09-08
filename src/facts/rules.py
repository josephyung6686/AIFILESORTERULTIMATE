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
from typing import Callable

from evidence_shape.canonical import canonical_json
from evidence_shape.store import is_derived
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import pass_cache_key
from facts.discount import MetadataScreen, field_permitted
from facts.evidence import (
    analysis_tier_for_observation, cite, context_pair, observations_for_version,
)
from facts.facets import word_boundary_match
from facts.file_facts import FACT_ORIGINS, write_fact, RULE
from facts.states import VALIDATED
from facts.unresolved import (
    ATTEMPTED_PRODUCERS, RULE_FOUND_SEVERAL_VALUES, write_unresolved,
)
from facts.values import VALUE_ORIGINS, add_raw_variant, ensure_value

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
    #: How the matched span becomes the fact's value. `None` stores the match
    #: verbatim, which is what this producer has always done and what every existing
    #: caller gets.
    #:
    #: IT EXISTS BECAUSE WITHOUT IT THIS PRODUCER CANNOT BE BOUND BESIDE A SLOT.
    #: `DirectSlot` has carried a `canonical` callable from the start; `Rule` did
    #: not, so `apply_rules` stored `match.group(0)` and a deployment whose slot
    #: canonicalises `PHYS 1401` to `PHYS1401` got BOTH spellings in one field --
    #: one course arriving as two values, which is `65` §4.2's recorded failure:
    #: "four files of one course became four one-file groups because one identity
    #: arrived as several spellings". Measured end to end on a five-file corpus, the
    #: whole course folder disappeared and every course file went unplaced. No unit
    #: test saw it, because a test writes `PHYS1401` and a person writes `PHYS 1401`.
    #:
    #: The callable is the CALLER'S for the same reason `DirectSlot.canonical` is:
    #: round 4's C-5 records that `normalize(field, raw_value)` is claimed by P8's
    #: Contract-in and disowned by P6's Task 17, so no part builds it. P6 gains no
    #: opinion about what a course code looks like -- only the ability to be told.
    #: A canonicaliser that raises propagates: a broken injection must not arrive as
    #: a silent absence of facts (§8.6).
    canonical: Callable[[str], str] | None = None

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


def apply_rules(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                rules: Sequence[Rule],
                screen: MetadataScreen) -> tuple[str, ...]:
    """Run every rule over every observation of one file version.

    `screen` is §2.2/§2.3's injected catalogue and has NO DEFAULT (F8). A rule is the
    caller's, and a caller's rule that happens to match a generator string must not be
    able to turn it into a conclusion: `python-docx` reached `subject` as a `validated`
    fact for exactly as long as `field_permitted` had no production caller.

    Four outcomes and they are not interchangeable:

    * the pattern does not match -- nothing at all. A rule that does not apply is not
      a refusal, and writing one would fill `unresolved` with every field every rule
      could theoretically have produced;
    * the pattern matches a value §2.2 SUPPRESSES, or a value §2.3 DEMOTES in a field
      that is not an authorship role -- nothing at all, and no second `unresolved`
      row: `screen_metadata` already wrote the one row Done-means 22 asks for, and a
      refusal recorded twice is counted twice (§8.5). The check sits BEFORE the
      context check, because a suppressed value whose context also failed would
      otherwise be recorded as a considered refusal it never was;
    * the pattern matches and the context check passes -- one `validated` fact citing
      that observation's key (M14), UNLESS the field is contested, below;
    * the pattern matches and the context check fails -- one `unresolved` row, whose
      reason is `context_truncated` when P4 flagged the context as cut and
      `context_check_failed` when it did not.

    **A FIFTH, AND IT IS WHY THIS RUNS IN TWO PASSES.** `104` R-37's own principle one
    layer down: a producer that finds TWO DISTINCT canonical values for one field on
    one file version has not RESOLVED that field. Writing both is not a resolution, it
    is a disagreement recorded as two conclusions -- and §3.7 then settles on neither,
    so the level disappears silently. `104` R-146 measured it: a syllabus printing
    `Physics 1401` and `Section 001` beside one `Instructor:` produced two `validated`
    subjects, and the run built both `term` folders and NO course folder at all. Read
    at `9cd52c6` with the same text in capitals, the older uppercase-only recogniser
    did the same thing, so this is not a new defect and the repair is not R-146's
    either -- it is the one R-37 already ruled.

    So the matches are collected first and the writes decided per FIELD:

    * one distinct canonical value -- every fact is written exactly as before, in
      exactly the order it was written before. This is the whole corpus's normal case
      and nothing about it moves, which `tests/p6` and the r37 byte-identity fixture
      both assert rather than assume;
    * two or more -- NO fact and no `values` row for that field, and one `unresolved`
      row per candidate observation, each citing its own, with the reason
      `rule_found_several_values`. The field stays absent from `file_facts`, so
      `model_facts.pending_fields_for` keeps it PENDING and the candidates reach site A
      as the file's own readings. The model decides which of them names the thing.

    **Nothing here chooses, and that is the point.** No first-wins, no longest-match,
    no sort order, no preference between an uppercase spelling and a title-case one --
    every one of those would be this module answering "which word names the course",
    which the constitution puts on the model ("LLM decides, code delivers"). The rule's
    honest answer to two candidates is that it has none.

    **The anchor pass is unaffected and deliberately so.** `record_anchor_statements`
    carries its own `is_code` and runs before this, so a file printing two code-shaped
    readings still STATES both, and a neighbour still receives both lines as context.
    That is the same answer this function is giving: the model is shown both and
    judges. A file that declines here has not gone quiet.
    """
    written: list[str] = []
    # Every match that cleared both screens, in the order it cleared them, so the
    # write pass below can reproduce that order exactly for the uncontested field.
    candidates: list[tuple[Rule, object, str, str]] = []
    # `104` R-135: a DERIVED reading is an addressable copy of this file's own words
    # and never a second reading of them. `starter.py`'s docstring prints
    # `BUSIB 4300 Homework 2 starter`; the minted line's context carried `Homework`,
    # this pass read the copy, and a validated course fact appeared for a file whose
    # own reading had already been judged. One predicate, P4's, so the rule pass and
    # the recogniser cannot disagree about what a copy is.
    observations = sorted(
        (one for one in observations_for_version(conn, file_id, content_hash)
         if not is_derived(one)),
        key=lambda o: o.observation_key)
    for observation in observations:
        before, after, truncated = context_pair(observation)
        for rule in rules:
            match = rule.pattern.search(observation.raw_value)
            if match is None:
                continue
            if not field_permitted(
                    observation, rule.field_key,
                    tool_producer_strings=screen.tool_producer_strings,
                    metadata_property_names=screen.metadata_property_names):
                continue
            if not context_check(before, after, rule.required_context_terms):
                write_unresolved(
                    conn, file_id=file_id, content_hash=content_hash,
                    field_key=rule.field_key,
                    reason="context_truncated" if truncated else "context_check_failed",
                    attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                    evidence_refs=(cite(observation),),
                    cache_key=pass_cache_key(conn, file_id=file_id,
                                              content_hash=content_hash))
                continue
            matched = match.group(0)
            candidates.append((
                rule, observation, matched,
                matched if rule.canonical is None else rule.canonical(matched)))

    # WHICH FIELDS THE RULES DISAGREED ABOUT. Distinct CANONICAL values, not distinct
    # matches: `PHYS 1401` and `PHYS1401` on one page are one course and one value,
    # which is the whole reason `rule.canonical` exists (`65` §4.2), and counting the
    # raw matches would refuse the very collapse this producer was built to make.
    values_by_field: dict[str, set[str]] = {}
    for rule, _observation, _matched, canonical in candidates:
        values_by_field.setdefault(rule.field_key, set()).add(canonical)
    contested = {field for field, values in values_by_field.items() if len(values) > 1}

    for rule, observation, matched, canonical in candidates:
        if rule.field_key in contested:
            write_unresolved(
                conn, file_id=file_id, content_hash=content_hash,
                field_key=rule.field_key, reason=RULE_FOUND_SEVERAL_VALUES,
                attempted_producers=(ATTEMPTED_PRODUCERS[1],),
                evidence_refs=(cite(observation),),
                cache_key=pass_cache_key(conn, file_id=file_id,
                                          content_hash=content_hash))
            continue
        # `canonical` is the one computed in the collect pass, not a second call to
        # `rule.canonical`. The contested check above counted THOSE values, so reusing
        # them is what makes "one distinct value" and "the value written" the same
        # sentence; a canonicaliser asked twice could answer twice.
        value_id = ensure_value(conn, field_key=rule.field_key,
                                canonical_value=canonical,
                                first_evidence_ref=cite(observation),
                                origin=VALUE_ORIGINS[0])
        # §2.8's FIRST rendering, the same one `facts.direct` keeps and for the
        # same reason: "the raw observation remains exactly that wording".
        #
        # IT IS HERE BECAUSE A FIELD MOVED. `subject` was a DIRECT slot until
        # 2026-09-04 and `direct_facts` has kept its raw variants since the
        # column gained its first caller; moving the field to a rule moved it to
        # the one producer that dropped them, and `PHYS 1401`, `PHYS-1401` and
        # `PHYS1401` would have collapsed to one value with no surviving record
        # that any document printed a space. `rule.canonical` is exactly what
        # makes that a loss rather than a redundancy -- it exists to collapse
        # spellings, and once it has, the canonical form is the only evidence
        # left of what was on the page.
        #
        # The MATCH, not the whole reading: `pattern.search` may claim a
        # substring, and the wording this column promises is the wording of the
        # value, not of the paragraph it was found in.
        add_raw_variant(conn, value_id, matched)
        written.append(write_fact(
            conn, file_id=file_id, content_hash=content_hash,
            field_key=rule.field_key, value_id=value_id,
            reliability_state=_VALIDATED, origin=RULE,
            evidence_refs=(cite(observation),),
            cache_key=pass_cache_key(conn, file_id=file_id,
                                      content_hash=content_hash),
            active=True))
    return tuple(written)

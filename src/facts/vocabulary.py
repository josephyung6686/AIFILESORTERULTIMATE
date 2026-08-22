# src/facts/vocabulary.py
"""P6's own closed vocabularies, published once, checked through P4's `check`.

Global constraint: "`unresolved` reasons and `origin` values are P6's own closed
vocabularies, published once, in one module, checked with P4's
`evidence_shape.vocabulary.check(value, vocabulary, *, name)` so a bad value raises
`NotInVocabulary` rather than being stored."

The six reliability states are NOT here — they are P4's, re-exported by
`facts.states`, and a second copy is what preamble rule 2 forbids.

Task 5 adds `UNRESOLVED_REASONS` and `ATTEMPTED_PRODUCERS` to this module.
"""
from __future__ import annotations

#: §3.11's six domain families plus the universal scope. Exactly the SPEC's list, in
#: the SPEC's order. Adding a member is a contract revision: §3.15 names Career and
#: recruiting, identity, medical and legal, and §3.11 gives them no field row, so
#: they are Deferred rather than empty scopes (S3).
FIELD_SCOPES: tuple[str, ...] = (
    "universal",
    "academic",
    "college_applications",
    "research",
    "finance",
    "photos",
    "code",
)

#: How a field's values normalize (SPEC, `fields` table). Exactly the four kinds
#: `planning/domains/canonical_fields.json` uses; P6 invents no fifth.
#:
#: The SPEC's column comment adds "date/term fields must use §3.10 rules", but that
#: file types `term` as `string`. Rather than mint a `term` kind the design does not
#: name, the §3.10 obligation stays in `facts.dates`, keyed on the field, with its
#: injected patterns. The gap is named in the plan, not closed here.
VALUE_KINDS: tuple[str, ...] = ("string", "date", "identifier", "enum")

# ---------------------------------------------------------------------------
# Task 5 — the abstention vocabularies (§3.6, §8.5, §8.6; B7)
# ---------------------------------------------------------------------------

#: The thirteen reasons, one named constant each. This module owns the literal
#: spelling; every call site imports the CONSTANT (preamble §3.1). That
#: `write_unresolved` validates the reason through P4's `check` -- so a misspelling
#: raises `NotInVocabulary` rather than storing -- is true and worth knowing, and it
#: is NOT a reason to spell the reason inline: validation at the seam catches a TYPO,
#: it does not stop the literal being a SECOND HOME.
NO_CANDIDATE_EVIDENCE: str = "no_candidate_evidence"
BELOW_SCORE_THRESHOLD: str = "below_score_threshold"
BELOW_MARGIN: str = "below_margin"
CONTEXT_CHECK_FAILED: str = "context_check_failed"
CONTEXT_TRUNCATED: str = "context_truncated"
FIELD_NOT_IN_ACTIVE_SCHEMA: str = "field_not_in_active_schema"
CITATION_ABSENT_FROM_EVIDENCE: str = "citation_absent_from_evidence"
NORMALIZATION_FAILED: str = "normalization_failed"
CONTRADICTED_BY_STRONGER_FACT: str = "contradicted_by_stronger_fact"
MODEL_RETURNED_UNKNOWN: str = "model_returned_unknown"
DISCOUNTED_TOOL_METADATA: str = "discounted_tool_metadata"
PRIVACY_WITHHELD: str = "privacy_withheld"
BUDGET_DEFERRED: str = "budget_deferred"

#: The thirteen in the SPEC's own table order, for iteration and membership. Each is
#: fired by exactly one place, named in the comment beside it, so a reason with no
#: producer or a producer with no reason is visible by reading this list. To NAME one
#: reason, import the constant above -- never a literal, never an index.
UNRESOLVED_REASONS: tuple[str, ...] = (
    NO_CANDIDATE_EVIDENCE,           # no observation offered a candidate (§3.6)
    BELOW_SCORE_THRESHOLD,           # §3.7 minimum score not cleared
    BELOW_MARGIN,                    # §3.7 margin not cleared, incl. §2.6's conflict
    CONTEXT_CHECK_FAILED,            # §3.5 pattern matched, required context absent
    CONTEXT_TRUNCATED,               # §3.5 check failed on context_truncated = true (§8.6)
    FIELD_NOT_IN_ACTIVE_SCHEMA,      # §3.6 check 1
    CITATION_ABSENT_FROM_EVIDENCE,   # §3.6 check 2
    NORMALIZATION_FAILED,            # §3.6 check 3
    CONTRADICTED_BY_STRONGER_FACT,   # §3.6 check 4
    MODEL_RETURNED_UNKNOWN,          # §3.6 — the model declined
    DISCOUNTED_TOOL_METADATA,        # the §2.2/§2.3 producer/creator discount fired
    PRIVACY_WITHHELD,                # P7's handling class forbids the model route (§8.4)
    BUDGET_DEFERRED,                 # §8.6 ceiling reached — never merged with abstention
)

#: §3.5's three routes, one named constant each. `direct` and `rule` are P6's own;
#: `llm` is P8's, and P6 records that it was tried without owning the call (§3.3).
#: The `_ROUTE` suffix is deliberate: `facts.states.DIRECT` (a reliability state) and
#: `facts.file_facts.RULE` (a fact origin) are different vocabularies that happen to
#: share a word, and four modules import two of the three.
DIRECT_ROUTE: str = "direct"
RULE_ROUTE: str = "rule"
LLM_ROUTE: str = "llm"

ATTEMPTED_PRODUCERS: tuple[str, str, str] = (DIRECT_ROUTE, RULE_ROUTE, LLM_ROUTE)

#: The two reasons that are NOT abstentions (B7, §8.6). A refusal for either of these
#: means the question was never answered on the evidence: the budget stopped the work,
#: or the privacy class forbade the only remaining route. §8.6: "If the budget is
#: exhausted, the product should retain extracted evidence, mark the deferred stage,
#: and leave the file or group in review rather than guessing", and reporting
#: "avoids the false impression that an unprocessed file was understood and found
#: unimportant". Reporting either of these as a considered refusal is that impression.
#:
#: This is a frozenset and not a tuple because it is asked `in` and never iterated for
#: order, and because P2's writer (`record_stage_output`) already enforces the
#: consequence -- outcome `deferred` requires budget_state `ceiling_reached`, and
#: `ceiling_reached` refuses outcome `abstained`. P6 does not re-implement that rule;
#: it names the two reasons that must not be routed into it as abstentions.
NOT_ABSTENTIONS: frozenset[str] = frozenset({BUDGET_DEFERRED, PRIVACY_WITHHELD})

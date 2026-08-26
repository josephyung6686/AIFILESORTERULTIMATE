# tests/p9/p8_fixtures.py
"""Recorded P8 Site-B verdicts, for P9's deterministic tasks. TESTS ONLY.

`src/grouping/` may never import this module, and a test asserts it does not.

The plan was written when P8 did not exist and specified a shape-alike carrying
`outcome`, `reasons`, `may_propose`, `requires_review` and `citations_checked`.
P8 exists now, so these build the REAL `llm_harness.records.P8Verdict`. A
shape-alike would be a second vocabulary that could drift from the first, which is
the thing P9 is under orders not to create — the SPEC is explicit that P9
publishes no verdict enum of its own.

Task 10 replaces these with a live `run_call`. Until then they stand in at the
named seam and nowhere else.
"""
from __future__ import annotations

from llm_harness.records import CheckedCitation, P8Verdict
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CONTEXT_ONLY_SUPPORT,
    BELOW_SUPPORT_THRESHOLD,
    GENERIC_SIMILARITY_ONLY,
    INVENTED_MEMBERSHIP,
    LLM_SUPPORTED,
    LLM_SUPPORTED_REVIEW,
    REJECT,
    REJECTED,
    SCOPE_GROUP,
    UNRESOLVED,
    WEAK,
)

VALIDATOR_VERSION = "P8/0.1.0"
POLICY_VERSION = "policy-1"


def _verdict(**overrides) -> P8Verdict:
    values = dict(
        verdict_id="fixture-verdict",
        dossier_id="fixture-course-dossier",
        claim_ref="claim-0",
        outcome=ACCEPT_DIRECT,
        disposition=LLM_SUPPORTED,
        reasons=(),
        may_propose=True,
        requires_review=False,
        citations_checked=(
            CheckedCitation(
                citation_ref="sha256:fixture", resolved=True, span_matched=True,
            ),
        ),
        scope=SCOPE_GROUP,
        validator_version=VALIDATOR_VERSION,
        policy_version=POLICY_VERSION,
        plan_version=None,
    )
    values.update(overrides)
    return P8Verdict(**values)


def accepted_direct_verdict(**overrides) -> P8Verdict:
    """A membership resting on direct evidence. No review required."""
    return _verdict(**overrides)


def accepted_context_supported_verdict(**overrides) -> P8Verdict:
    """Valid, but on context. Always routed to user review, never silently kept."""
    values = dict(
        verdict_id="fixture-verdict-context",
        outcome=ACCEPT_CONTEXT_SUPPORTED,
        disposition=LLM_SUPPORTED_REVIEW,
        reasons=(CONTEXT_ONLY_SUPPORT,),
        may_propose=True,
        requires_review=True,
    )
    values.update(overrides)
    return _verdict(**values)


def invented_membership_verdict(**overrides) -> P8Verdict:
    """A member the dossier never contained."""
    values = dict(
        verdict_id="fixture-verdict-invented",
        outcome=REJECT,
        disposition=REJECTED,
        reasons=(INVENTED_MEMBERSHIP,),
        may_propose=False,
        requires_review=False,
    )
    values.update(overrides)
    return _verdict(**values)


def generic_similarity_only_verdict(**overrides) -> P8Verdict:
    """Connected by embeddings alone. SR2's shape, seen from P8's side."""
    values = dict(
        verdict_id="fixture-verdict-generic",
        outcome=REJECT,
        disposition=REJECTED,
        reasons=(GENERIC_SIMILARITY_ONLY,),
        may_propose=False,
        requires_review=False,
    )
    values.update(overrides)
    return _verdict(**values)


def weak_verdict(**overrides) -> P8Verdict:
    """Below the site's support bar. `may_propose` is false: never a folder."""
    values = dict(
        verdict_id="fixture-verdict-weak",
        outcome=WEAK,
        disposition=UNRESOLVED,
        reasons=(BELOW_SUPPORT_THRESHOLD,),
        may_propose=False,
        requires_review=True,
    )
    values.update(overrides)
    return _verdict(**values)


def abstained_verdict(**overrides) -> P8Verdict:
    """The model returned unknown, or the harness refused to call."""
    values = dict(
        verdict_id="fixture-verdict-abstain",
        outcome=ABSTAIN,
        disposition=ABSTAIN,
        reasons=(),
        may_propose=False,
        requires_review=False,
        citations_checked=(),
    )
    values.update(overrides)
    return _verdict(**values)


RECORDED_P8_VERDICTS = (
    accepted_direct_verdict,
    accepted_context_supported_verdict,
    invented_membership_verdict,
    generic_similarity_only_verdict,
    weak_verdict,
    abstained_verdict,
)

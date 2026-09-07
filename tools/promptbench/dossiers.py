# tools/promptbench/dossiers.py
"""A case as the product's `Dossier`, and the exact bytes a model is shown.

The bench never hand-writes dossier JSON. It constructs the frozen `Dossier`
record and lets `llm_harness.dossier.canonical_dossier_bytes` and
`llm_harness.records.assemble` produce the model-visible bytes, under a bench
wire-handle key -- so the model sees keyed observation handles exactly as it
would from the product, and `dispatch` is given the same key to read them back.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from llm_harness.dossier import canonical_dossier_bytes  # noqa: E402
from llm_harness.records import (  # noqa: E402
    Conflict, Dossier, EvidenceItem, FolderLevel, PromptDefinition,
    ReleasedEvidence, assemble,
)
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE, B_GROUP, C_PLACEMENT,
    COHERENCE_JUDGEMENT, D_RESIDUAL, E_TEMPLATE, REDUCTION_NONE,
    REMAINS_AMBIGUOUS, SEVERAL_LEGAL_NODES_PLAUSIBLE,
    USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
)

from tools.promptbench.cases import Case

#: Not a deployment key. It keys the handles of synthetic evidence only.
BENCH_HANDLE_KEY: bytes = b"promptbench-wire-handle-key-not-a-deployment-key"
POLICY_VERSION: str = "promptbench-policy-1"
RELEASE_ID: str = "promptbench-release"
MAX_DOSSIER_TOKENS: int = 4000

ELIGIBILITY = {
    A_FACT: REMAINS_AMBIGUOUS,
    B_GROUP: COHERENCE_JUDGEMENT,
    C_PLACEMENT: SEVERAL_LEGAL_NODES_PLAUSIBLE,
    D_RESIDUAL: USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
    E_TEMPLATE: ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
}


def evidence_items_of(case: Case) -> tuple[EvidenceItem, ...]:
    items = [
        EvidenceItem(
            evidence_ref=item.key, kind=item.kind, location=item.location,
            excerpt_span=item.span, reliability_state=item.reliability_state,
            basis=item.basis)
        for item in case.evidence
    ]
    items.extend(
        EvidenceItem(
            evidence_ref=item.evidence_ref, kind=item.kind,
            location=item.location, excerpt_span=None,
            reliability_state=item.reliability_state, basis=item.basis)
        for item in case.items
    )
    return tuple(items)


def released_of(case: Case) -> tuple[ReleasedEvidence, ...]:
    return tuple(
        ReleasedEvidence(observation_key=item.key, address=item.address,
                         value=item.value, zone=item.zone)
        for item in case.released()
    )


def dossier_of(case: Case, *, allowed_vocabulary=None,
               folder_levels=None) -> Dossier:
    """The frozen record for one case. Site A callers pass the P6-derived
    vocabulary and levels; every other site takes the case's own."""
    vocabulary = tuple(allowed_vocabulary if allowed_vocabulary is not None
                       else case.allowed_vocabulary)
    levels = tuple(
        FolderLevel(field=f, label=l, requirement=r)
        for f, l, r in (folder_levels if folder_levels is not None
                        else case.folder_levels))
    return Dossier(
        dossier_id=f"promptbench:{case.site}:{case.case_id}",
        call_site=case.site,
        subject_ref=case.subject_ref,
        eligibility_reason=ELIGIBILITY[case.site],
        plan_version=case.plan_version,
        policy_version=POLICY_VERSION,
        allowed_vocabulary=vocabulary,
        evidence_items=evidence_items_of(case),
        conflicts=tuple(Conflict(conflict_id=c, kind=k) for c, k in case.conflicts),
        released_evidence=released_of(case),
        max_dossier_tokens=MAX_DOSSIER_TOKENS,
        reduction_rung=REDUCTION_NONE,
        release_id=RELEASE_ID,
        folder_levels=levels,
    )


def model_visible_bytes(dossier: Dossier, prompt: PromptDefinition) -> bytes:
    """Exactly what `transport.issue` would send: template bytes + dossier bytes."""
    return assemble(prompt, canonical_dossier_bytes(
        dossier, prompt, handle_key=BENCH_HANDLE_KEY))


def resolver_for(case: Case):
    """`evidence_resolver`: a released key resolves to its value; nothing else."""
    values = {item.key: item.value for item in case.released()}
    return lambda key: values.get(key)


__all__ = ["BENCH_HANDLE_KEY", "MAX_DOSSIER_TOKENS", "POLICY_VERSION",
           "dossier_of", "evidence_items_of", "model_visible_bytes",
           "released_of", "resolver_for"]

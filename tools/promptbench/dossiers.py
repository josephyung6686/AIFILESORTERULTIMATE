# tools/promptbench/dossiers.py
"""A case as the product's `Dossier`, and the exact bytes a model is shown.

The bench never hand-writes dossier JSON. It constructs the frozen `Dossier`
record and lets `llm_harness.dossier.canonical_dossier_bytes` and
`llm_harness.records.assemble` produce the model-visible bytes, under a bench
wire-handle key -- so the model sees keyed observation handles exactly as it
would from the product, and `dispatch` is given the same key to read them back.
"""
from __future__ import annotations

import json

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from llm_harness.dossier import canonical_dossier_bytes  # noqa: E402
from evidence_shape.canonical import canonical_json  # noqa: E402
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


def model_visible_bytes(dossier: Dossier, prompt: PromptDefinition, *,
                        readings: list | None = None,
                        layout: str = "canonical") -> bytes:
    """Exactly what `transport.issue` would send: template bytes + dossier bytes.

    With `readings`, the bench emulates the dossier key R-08 asks for: the
    product's canonical bytes are parsed, `readings` is added, and the object is
    re-emitted either in the product's form (`canonical`: `canonical_json`,
    sorted keys, so `readings` lands between `policy_version` and
    `reduction_rung`, after the file's own keys) or `frame-first` (the situation
    frame -- vocabulary, glossary, levels, readings, versions, schema, policy --
    before the file part). The product writes neither the key nor the second
    layout today (G18); the `Dossier` the judge validates against is untouched.
    """
    raw = canonical_dossier_bytes(dossier, prompt, handle_key=BENCH_HANDLE_KEY)
    if readings is None and layout == "canonical":
        return assemble(prompt, raw)
    body = json.loads(raw.decode("utf-8"))
    if readings is not None:
        body["readings"] = list(readings)
    return assemble(prompt, serialise_dossier(body, layout).encode("utf-8"))


#: The keys that are the same on every file of one situation, in the order the
#: stable-prefix lever wants them, and the keys that belong to the file.
FRAME_KEYS = ("allowed_vocabulary", "call_site", "field_glossary", "folder_levels",
              "readings", "max_dossier_tokens", "plan_version", "policy_version",
              "reduction_rung", "response_schema", "shaping_policy")
FILE_KEYS = ("subject_ref", "eligibility_reason", "evidence_items",
             "released_evidence", "conflicts")


def serialise_dossier(body: dict, layout: str) -> str:
    if layout == "canonical":
        return canonical_json(body)
    if layout != "frame-first":
        raise ValueError(f"unknown layout {layout!r}; canonical or frame-first")
    unknown = set(body) - set(FRAME_KEYS) - set(FILE_KEYS)
    if unknown:
        raise ValueError(f"dossier keys with no place in the frame-first layout: {sorted(unknown)}")
    ordered = {k: body[k] for k in FRAME_KEYS if k in body}
    ordered.update({k: body[k] for k in FILE_KEYS if k in body})
    return json.dumps(ordered, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


RECOGNITION_FILE = _ROOT / "src" / "recognition" / "library" / "recognition.json"


def readings_for(rows) -> list[dict]:
    """The `needs_llm` readings of the named recognition rows, verbatim.

    Transcribed, never authored: every `text` is byte-equal to a string in
    `recognition.json`, and the row it came from travels with it.
    """
    library = json.loads(RECOGNITION_FILE.read_text(encoding="utf-8"))["schemas"]
    wanted = tuple(rows)
    out = []
    for row in wanted:
        schema = library[row.split(".")[0]]
        entries = [e for e in schema["needs_llm"] if e["row"] == row]
        if not entries:
            raise KeyError(f"no needs_llm entry for row {row!r}")
        for entry in entries:
            out.extend({"row": row, "text": text} for text in entry["readings"])
    return out


def resolver_for(case: Case):
    """`evidence_resolver`: a released key resolves to its value; nothing else."""
    values = {item.key: item.value for item in case.released()}
    return lambda key: values.get(key)


__all__ = ["BENCH_HANDLE_KEY", "FILE_KEYS", "FRAME_KEYS", "MAX_DOSSIER_TOKENS",
           "POLICY_VERSION", "dossier_of", "evidence_items_of", "model_visible_bytes",
           "readings_for", "released_of", "resolver_for", "serialise_dossier"]

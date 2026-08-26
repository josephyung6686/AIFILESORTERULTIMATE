"""Two-process determinism probe for P8 Task 12.

Creates its own temporary database, seeds fixed logical inputs, re-validates a
recorded response, and writes one canonical JSON line to stdout. Database-generated
ids and timestamps are stripped before output.

Run (repo root):

    PYTHONPATH=src python tests/p8/determinism_probe.py
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from dataclasses import fields, is_dataclass
from types import MappingProxyType

from database_agent.db import create_schema
from eval_harness.store import create_eval_schema
from evidence_shape.canonical import canonical_json
from evidence_shape.schema import create_evidence_schema
from llm_harness.fingerprint import dossier_content_address, prompt_fingerprint
from llm_harness.dossier import canonical_dossier_bytes, dossier_address
from llm_harness.records import (
    Conflict,
    Dossier,
    EvidenceItem,
    PromptDefinition,
    ReleasedEvidence,
)
from llm_harness.schema import create_llm_schema
from llm_harness.store import record_dossier, record_response
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    A_FACT,
    DIRECT_ANCHOR,
    REDUCTION_NONE,
    REMAINS_AMBIGUOUS,
)


RELEASED = b"Columbia University - redacted dossier excerpt"
SCHEMA = b'{"type":"object"}'
VOCABULARY = ("subject",)
RESPONSE = (
    b'{"claims":[{"claim_ref":"c1","payload":{"field":"subject","value":'
    b'"Columbia University"},"citations":[{"evidence_ref":"obs-key-1",'
    b'"cited_span":"Columbia University","why_it_supports":"names the school"}]}]}'
)
OBSERVED_AT = "2026-08-25T12:00:00Z"


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=SCHEMA,
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _dossier() -> Dossier:
    return Dossier(
        dossier_id="probe-dossier",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=VOCABULARY,
        evidence_items=(
            EvidenceItem(
                evidence_ref="obs-key-1", kind="excerpt", location="body",
                excerpt_span=(0, 20), reliability_state="direct",
                basis=DIRECT_ANCHOR,
            ),
        ),
        conflicts=(Conflict(conflict_id="c1", kind="stronger_fact"),),
        released_evidence=(
            ReleasedEvidence(
                observation_key="obs-key-1", address="0:20",
                value=RELEASED.decode("utf-8"), zone="body",
                context_before=None, context_after=None, context_truncated=False,
            ),
        ),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-probe",
    )


def _jsonable(value):
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, (dict, MappingProxyType)):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return value.hex()
    return value


def run_probe() -> dict:
    prompt = _prompt()
    dossier = _dossier()
    fingerprint = prompt_fingerprint(prompt)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    create_evidence_schema(conn)
    create_llm_schema(conn)
    create_eval_schema(conn)
    record_dossier(conn, dossier, observed_at=OBSERVED_AT)
    record_response(
        conn,
        dossier_id=dossier.dossier_id,
        response_bytes=RESPONSE,
        model_id="fixture-model",
        prompt_fingerprint=fingerprint,
        release_audit_id=17,
        observed_at=OBSERVED_AT,
    )
    verdicts, report = validate_response(
        dossier, RESPONSE,
        evidence_resolver=lambda key: RELEASED.decode() if key == "obs-key-1" else None,
        site_validator=lambda *_a, **_k: None,
        contradicts=lambda *_a, **_k: False,
        model_id="fixture-model",
        prompt_fingerprint=fingerprint,
        dossier_builder="determinism-probe",
        release_audit_id=17,
    )
    address = dossier_address(dossier, _prompt())
    return {
        "dossier_content_address": address,
        "canonical_dossier_sha256": hashlib.sha256(
            canonical_dossier_bytes(dossier, _prompt())
        ).hexdigest(),
        "response_sha256": hashlib.sha256(RESPONSE).hexdigest(),
        "verdict": json.loads(canonical_json(_jsonable(verdicts))),
        "grounding_report": json.loads(canonical_json(_jsonable(report))),
        "p2_payload": json.loads(canonical_json(_jsonable(verdicts[0]))),
        "prompt_fingerprint": fingerprint,
    }


def main() -> None:
    sys.stdout.write(canonical_json(run_probe()) + "\n")


if __name__ == "__main__":
    main()

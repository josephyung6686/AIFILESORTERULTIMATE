"""Two-process determinism probe for P8 (repair R5).

Creates its own temporary database, seeds fixed logical inputs, re-validates a
recorded response THROUGH REPLAY AND THE SITE DISPATCHER, emits and reads back the
P2 stage row, and writes one canonical JSON line to stdout. Database-generated ids
and timestamps are stripped before output.

Before R5 the probe called `validate_response` directly with a permissive site
callback and reported the verdict re-serialised as its own "p2_payload". It
therefore proved determinism of a path the product does not take: not the
dispatcher, not replay, and not a real P2 row.

The subject is Site B. Site B takes no injected authority bundle, so the whole
probe stays a function of fixed constants -- no file ids, no uuids, nothing a
second process could disagree with.

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
from eval_harness.run import VERSION_TUPLE_FIELDS, start_run
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from evidence_shape.canonical import canonical_json
from evidence_shape.schema import create_evidence_schema
from llm_harness.dossier import canonical_dossier_bytes, dossier_address
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.fixtures import SITE_B_OUTCOME_PAIRS
from llm_harness.records import PromptDefinition
from llm_harness.schema import create_llm_schema
from llm_harness.sites import SiteDependencies
from llm_harness.stage_output import (
    emit_stage_output,
    record_p8_version_tuple,
    replay_recorded_response,
)
from llm_harness.store import record_dossier, record_response
from llm_harness.vocabulary import B_GROUP

#: The recorded Site-B pair P8 owns. Content-free contract witness, fixed bytes.
PAIR = SITE_B_OUTCOME_PAIRS[0]
RELEASED = PAIR.dossier.released_evidence[0].value.encode("utf-8")
OBSERVATION_KEY = PAIR.dossier.released_evidence[0].observation_key
RESPONSE = PAIR.response_bytes
SCHEMA = b'{"type":"object"}'
VOCABULARY = PAIR.dossier.allowed_vocabulary
POLICY_VERSION = PAIR.dossier.policy_version
OBSERVED_AT = "2026-08-25T12:00:00Z"


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.grouping",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=SCHEMA,
        call_site=B_GROUP,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _dossier():
    return PAIR.dossier


def _site_dependencies() -> SiteDependencies:
    """Site B needs no injected authority. It needs the dispatcher to pick it."""
    return SiteDependencies(fact=None, placement=None, residual=None, template=None)


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

    # Replay reads the stored bytes back and routes them through the same
    # dispatcher a live call uses. Nothing here supplies an acceptance callback.
    verdicts, report = replay_recorded_response(
        conn, dossier,
        evidence_resolver=lambda key: (
            RELEASED.decode() if key == OBSERVATION_KEY else None
        ),
        site_dependencies=_site_dependencies(),
        contradicts=lambda *_a, **_k: False,
        dossier_builder="determinism-probe",
        policy_version=POLICY_VERSION,
    )

    # The P2 row is emitted and read back, not re-serialised from the verdict.
    axes = {name: None for name in VERSION_TUPLE_FIELDS}
    axes["extractor_versions"] = {}
    axes["prompt_fingerprint"] = fingerprint
    axes["model_identifier"] = "fixture-model"
    axes["analysis_tiers_enabled"] = ["llm"]
    ref = record_p8_version_tuple(conn, **axes)
    run_id = start_run(
        conn, bundle_id="bundle-probe", run_kind="replay",
        version_tuple_ref=ref, budget_ceilings={},
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id="plan-probe", pinned_plan_version="1",
    )
    emit_stage_output(
        conn, run_id=run_id, subject_ref=dossier.subject_ref,
        result=verdicts[0], inputs=(OBSERVATION_KEY,), version_tuple_ref=ref,
    )
    stage_row = stage_outputs(conn, run_id, stage_id="llm_interpretation")[0]

    return {
        "dossier_content_address": dossier_address(dossier, prompt),
        "canonical_dossier_sha256": hashlib.sha256(
            canonical_dossier_bytes(dossier, prompt)
        ).hexdigest(),
        "response_sha256": hashlib.sha256(RESPONSE).hexdigest(),
        "verdict": json.loads(canonical_json(_jsonable(verdicts))),
        "grounding_report": json.loads(canonical_json(_jsonable(report))),
        "p2_stage_outcome": stage_row["outcome"],
        "p2_budget_state": stage_row["budget_state"],
        "p2_payload": json.loads(stage_row["payload"]),
        "prompt_fingerprint": fingerprint,
    }


def main() -> None:
    sys.stdout.write(canonical_json(run_probe()) + "\n")


if __name__ == "__main__":
    main()

"""P8 provenance: subsystem authorship, fingerprint keyword, audit/model explanation."""
from __future__ import annotations

import inspect
import json

from database_agent.events import REGISTERED_EVENT_TYPES
from llm_harness.schema import create_llm_schema
import llm_harness.store as store
from llm_harness.authorship import (
    AUTHORED_EVENT_TYPES,
    COMPONENT_VERSION,
    SUBSYSTEM,
    event_defaults,
)

from p8.conftest import (
    FIXED_CLOCK,
    make_abstention,
    make_dossier,
    make_issued_report,
    make_refusal,
    make_verdict,
    make_zero_report,
)


def _events(conn) -> list:
    return list(conn.execute(
        "SELECT event_type, subsystem, component_version, prompt_fingerprint, "
        "observed_at, explanation FROM events WHERE subsystem = ? "
        "ORDER BY event_id",
        (SUBSYSTEM,),
    ))


def _body(row) -> dict:
    return json.loads(row["explanation"])


def test_authorship_names_p8_and_the_five_registered_types():
    assert SUBSYSTEM == "P8"
    assert AUTHORED_EVENT_TYPES == (
        "model_response_received",
        "validation_verdict",
        "verdict_superseded",
        "call_refused",
        "model_call_issued",
    )
    assert "llm_call_failure" not in AUTHORED_EVENT_TYPES
    for name in AUTHORED_EVENT_TYPES:
        assert name in REGISTERED_EVENT_TYPES
    assert "model_call_issued" in REGISTERED_EVENT_TYPES


def test_event_defaults_return_a_mapping_and_do_not_write(p8_conn):
    before = p8_conn.execute("SELECT count(*) AS c FROM events").fetchone()["c"]
    fields = event_defaults(
        event_type="validation_verdict",
        observed_at=FIXED_CLOCK,
        explanation="{}",
        prompt_fingerprint="fp-canonical",
    )
    after = p8_conn.execute("SELECT count(*) AS c FROM events").fetchone()["c"]
    assert after == before
    assert "conn" not in event_defaults.__code__.co_varnames
    assert fields["subsystem"] == "P8"
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["observed_at"] == FIXED_CLOCK
    assert fields["prompt_fingerprint"] == "fp-canonical"
    assert fields["event_type"] == "validation_verdict"


def test_create_llm_schema_does_not_register_events(p8_conn):
    create_llm_schema(p8_conn)
    assert set(AUTHORED_EVENT_TYPES) <= set(REGISTERED_EVENT_TYPES)


def test_record_response_writes_fingerprint_keyword_and_audit_model_explanation(
    p8_conn,
):
    store.record_response(
        p8_conn,
        dossier_id="dossier-1",
        response_bytes=b"{}",
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    rows = _events(p8_conn)
    assert len(rows) == 1
    row = rows[0]
    assert row["event_type"] == "model_response_received"
    assert row["subsystem"] == "P8"
    assert row["component_version"] == COMPONENT_VERSION
    assert row["prompt_fingerprint"] == "fp-canonical"
    assert row["observed_at"] == FIXED_CLOCK
    body = _body(row)
    assert body["audit_id"] == 17
    assert body["model_id"] == "fixture-model"
    assert body["prompt_fingerprint"] == "fp-canonical"


def test_verdict_event_writers_require_provenance_with_no_defaults():
    for writer in (store.record_verdict, store.supersede_verdict):
        params = inspect.signature(writer).parameters
        for name in ("model_id", "prompt_fingerprint", "release_audit_id"):
            assert params[name].kind is inspect.Parameter.KEYWORD_ONLY
            assert params[name].default is inspect.Parameter.empty


def test_record_verdict_and_supersede_author_exact_provenance(p8_conn):
    store.record_verdict(
        p8_conn,
        make_verdict(),
        model_id="fixture-model-v1",
        prompt_fingerprint="fp-v1",
        release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    store.record_verdict(
        p8_conn,
        make_verdict(verdict_id="verdict-2"),
        model_id="fixture-model-v2",
        prompt_fingerprint="fp-v2",
        release_audit_id=29,
        observed_at=FIXED_CLOCK,
    )
    store.supersede_verdict(
        p8_conn, "verdict-1", "verdict-2",
        reason="validator revision",
        model_id="fixture-model-v2",
        prompt_fingerprint="fp-v2",
        release_audit_id=29,
        observed_at=FIXED_CLOCK,
    )
    rows = _events(p8_conn)
    types = [row["event_type"] for row in rows]
    assert types == ["validation_verdict", "validation_verdict", "verdict_superseded"]
    assert {row["subsystem"] for row in rows} == {"P8"}
    assert all(row["component_version"] == COMPONENT_VERSION for row in rows)
    assert [row["prompt_fingerprint"] for row in rows] == ["fp-v1", "fp-v2", "fp-v2"]
    first = _body(rows[0])
    assert first["verdict_id"] == "verdict-1"
    assert first["audit_id"] == 17
    assert first["model_id"] == "fixture-model-v1"
    assert first["prompt_fingerprint"] == "fp-v1"
    superseded = _body(rows[2])
    assert superseded["old_verdict_id"] == "verdict-1"
    assert superseded["new_verdict_id"] == "verdict-2"
    assert superseded["audit_id"] == 29
    assert superseded["model_id"] == "fixture-model-v2"
    assert superseded["prompt_fingerprint"] == "fp-v2"


def test_refusal_and_abstention_call_refused_carry_report_provenance(p8_conn):
    refused = make_zero_report(
        dossier_id="dossier-refused",
        prompt_fingerprint="fp-refused",
        model_id="fixture-model",
        release_audit_id=None,
    )
    store.record_refusal(p8_conn, make_refusal(), refused, observed_at=FIXED_CLOCK)
    abstained = make_zero_report(
        dossier_id="dossier-abstain",
        prompt_fingerprint="fp-abstain",
        model_id="fixture-model",
    )
    store.record_pre_call_abstention(
        p8_conn, make_abstention(), abstained, observed_at=FIXED_CLOCK,
    )
    rows = _events(p8_conn)
    assert [row["event_type"] for row in rows] == ["call_refused", "call_refused"]
    assert rows[0]["prompt_fingerprint"] == "fp-refused"
    assert rows[1]["prompt_fingerprint"] == "fp-abstain"
    first, second = _body(rows[0]), _body(rows[1])
    assert first["audit_id"] is None
    assert first["model_id"] == "fixture-model"
    assert first["prompt_fingerprint"] == "fp-refused"
    assert second["model_id"] == "fixture-model"
    assert second["prompt_fingerprint"] == "fp-abstain"
    assert {row["subsystem"] for row in rows} == {"P8"}


def test_silent_writers_append_no_p8_event(p8_conn):
    store.record_dossier(p8_conn, make_dossier(), observed_at=FIXED_CLOCK)
    store.record_grounding_report(
        p8_conn, make_issued_report(), observed_at=FIXED_CLOCK,
    )
    store.record_call_failure(
        p8_conn, dossier_id="dossier-1", failure_class="transport",
        explanation="client raised", observed_at=FIXED_CLOCK,
    )
    assert _events(p8_conn) == []


def test_store_does_not_emit_model_call_issued(p8_conn):
    store.record_dossier(p8_conn, make_dossier(), observed_at=FIXED_CLOCK)
    store.record_response(
        p8_conn, dossier_id="dossier-1", response_bytes=b"{}",
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK,
    )
    issued = [
        row["event_type"] for row in p8_conn.execute(
            "SELECT event_type FROM events WHERE event_type = 'model_call_issued'"
        )
    ]
    assert issued == []

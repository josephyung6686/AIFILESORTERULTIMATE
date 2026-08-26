"""Append-only P8 storage: Task 3 tables, writers, and the writer→event matrix."""
from __future__ import annotations

import json
import sqlite3

import pytest

import llm_harness.store as store
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    BUDGET_EXHAUSTED,
    NOT_ELIGIBLE_FOR_MODEL,
    USER_REJECTED_EQUIVALENT,
)
from privacy.consent import ConsentRequirement
from privacy.release import NeedsConsent

from p8.conftest import (
    BUDGET_TABLES,
    FIXED_CLOCK,
    TASK3_TABLES,
    make_abstention,
    make_dossier,
    make_issued_report,
    make_refusal,
    make_verdict,
    make_zero_report,
)


def _tables(conn) -> set[str]:
    return {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }


def _columns(conn, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _index_columns(conn, table: str) -> set[str]:
    names: set[str] = set()
    for index in conn.execute(f"PRAGMA index_list({table})"):
        for column in conn.execute(f"PRAGMA index_info({index['name']})"):
            names.add(column["name"])
    return names


def _capture_events(monkeypatch) -> list[dict]:
    calls: list[dict] = []

    def capture(conn, **fields):
        calls.append(fields)
        return len(calls)

    monkeypatch.setattr(store, "append_event", capture)
    return calls


def test_task_3_tables_exist_and_budget_tables_do_not(p8_conn):
    names = _tables(p8_conn)
    assert set(TASK3_TABLES) <= names
    assert not set(BUDGET_TABLES) & names


def test_create_llm_schema_is_idempotent(p8_conn):
    create_llm_schema(p8_conn)
    create_llm_schema(p8_conn)
    assert set(TASK3_TABLES) <= _tables(p8_conn)


def test_identity_and_version_columns_are_present_and_indexed(p8_conn):
    assert {
        "dossier_id", "policy_version", "release_id", "observed_at", "payload",
    } <= _columns(p8_conn, "llm_dossier")
    assert {
        "dossier_id", "response_bytes", "model_id", "prompt_fingerprint",
        "release_audit_id", "observed_at",
    } <= _columns(p8_conn, "llm_response")
    assert {
        "verdict_id", "dossier_id", "validator_version", "policy_version",
        "observed_at", "payload",
    } <= _columns(p8_conn, "llm_verdict")
    assert {
        "dossier_id", "prompt_fingerprint", "validator_version", "observed_at",
        "payload",
    } <= _columns(p8_conn, "llm_grounding_report")

    indexed = set()
    for table in TASK3_TABLES:
        indexed |= _index_columns(p8_conn, table)
    for column in (
        "dossier_id", "verdict_id", "prompt_fingerprint",
        "validator_version", "policy_version", "release_id",
    ):
        assert column in indexed, column


def test_record_dossier_stores_canonical_payload_and_appends_no_event(
    p8_conn, monkeypatch,
):
    events = _capture_events(monkeypatch)
    dossier = make_dossier()
    returned = store.record_dossier(p8_conn, dossier, observed_at=FIXED_CLOCK)
    assert returned == dossier.dossier_id
    row = p8_conn.execute(
        "SELECT * FROM llm_dossier WHERE dossier_id = ?", (dossier.dossier_id,),
    ).fetchone()
    payload = json.loads(row["payload"])
    assert payload["dossier_id"] == dossier.dossier_id
    assert payload["policy_version"] == dossier.policy_version
    assert payload["release_id"] == dossier.release_id
    assert row["dossier_id"] == dossier.dossier_id
    assert row["policy_version"] == dossier.policy_version
    assert row["release_id"] == dossier.release_id
    assert row["observed_at"] == FIXED_CLOCK
    assert events == []


def test_record_response_preserves_raw_bytes_and_appends_one_received_event(
    p8_conn, monkeypatch,
):
    events = _capture_events(monkeypatch)
    raw = b"\x00\xff{not-json"
    response_id = store.record_response(
        p8_conn,
        dossier_id="dossier-1",
        response_bytes=raw,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    row = p8_conn.execute(
        "SELECT response_bytes, model_id, prompt_fingerprint, release_audit_id "
        "FROM llm_response WHERE response_id = ?",
        (response_id,),
    ).fetchone()
    assert bytes(row["response_bytes"]) == raw
    assert row["model_id"] == "fixture-model"
    assert row["prompt_fingerprint"] == "fp-canonical"
    assert row["release_audit_id"] == 17
    assert [event["event_type"] for event in events] == ["model_response_received"]


def test_record_response_rejects_non_bytes(p8_conn, monkeypatch):
    events = _capture_events(monkeypatch)
    with pytest.raises(TypeError):
        store.record_response(
            p8_conn,
            dossier_id="dossier-1",
            response_bytes="not-bytes",
            model_id="fixture-model",
            prompt_fingerprint="fp-canonical",
            release_audit_id=17,
            observed_at=FIXED_CLOCK,
        )
    assert p8_conn.execute("SELECT count(*) AS c FROM llm_response").fetchone()["c"] == 0
    assert events == []


def test_record_verdict_inserts_a_row_and_appends_validation_verdict(
    p8_conn, monkeypatch,
):
    events = _capture_events(monkeypatch)
    verdict = make_verdict()
    returned = store.record_verdict(
        p8_conn,
        verdict,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    assert returned == verdict.verdict_id
    row = p8_conn.execute(
        "SELECT * FROM llm_verdict WHERE verdict_id = ?", (verdict.verdict_id,),
    ).fetchone()
    payload = json.loads(row["payload"])
    assert payload["verdict_id"] == verdict.verdict_id
    assert payload["outcome"] == verdict.outcome
    assert row["dossier_id"] == verdict.dossier_id
    assert row["validator_version"] == verdict.validator_version
    assert row["policy_version"] == verdict.policy_version
    assert [event["event_type"] for event in events] == ["validation_verdict"]
    assert events[0]["prompt_fingerprint"] == "fp-canonical"
    assert json.loads(events[0]["explanation"])["audit_id"] == 17


def test_record_verdict_is_atomic_when_append_event_fails(p8_conn, monkeypatch):
    def boom(conn, **fields):
        raise RuntimeError("append failed")

    monkeypatch.setattr(store, "append_event", boom)
    with pytest.raises(RuntimeError, match="append failed"):
        store.record_verdict(
            p8_conn,
            make_verdict(),
            model_id="fixture-model",
            prompt_fingerprint="fp-canonical",
            release_audit_id=17,
            observed_at=FIXED_CLOCK,
        )
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict"
    ).fetchone()["c"] == 0


def test_prior_verdict_survives_supersession(p8_conn, monkeypatch):
    events = _capture_events(monkeypatch)
    old = make_verdict(verdict_id="verdict-old")
    new = make_verdict(verdict_id="verdict-new")
    store.record_verdict(p8_conn, old, model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    store.record_verdict(p8_conn, new, model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    events.clear()
    store.supersede_verdict(
        p8_conn, old.verdict_id, new.verdict_id,
        reason="validator revision", model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    prior = p8_conn.execute(
        "SELECT * FROM llm_verdict WHERE verdict_id = ?", (old.verdict_id,),
    ).fetchone()
    assert json.loads(prior["payload"])["outcome"] == old.outcome
    assert prior["superseded_by"] == new.verdict_id
    assert prior["supersede_reason"] == "validator revision"
    successor = p8_conn.execute(
        "SELECT supersedes FROM llm_verdict WHERE verdict_id = ?", (new.verdict_id,),
    ).fetchone()
    assert successor["supersedes"] == old.verdict_id
    link = p8_conn.execute(
        "SELECT old_verdict_id, new_verdict_id, reason FROM llm_verdict_supersession"
    ).fetchone()
    assert tuple(link) == (old.verdict_id, new.verdict_id, "validator revision")
    assert [event["event_type"] for event in events] == ["verdict_superseded"]


def test_supersede_verdict_rejects_unknown_new_verdict_id(p8_conn, monkeypatch):
    events = _capture_events(monkeypatch)
    old = make_verdict(verdict_id="verdict-old")
    store.record_verdict(p8_conn, old, model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    events.clear()
    with pytest.raises(KeyError):
        store.supersede_verdict(
            p8_conn, old.verdict_id, "v-does-not-exist",
            reason="validator revision", model_id="fixture-model",
            prompt_fingerprint="fp-fixture",
            release_audit_id=1,
            observed_at=FIXED_CLOCK,
        )
    prior = p8_conn.execute(
        "SELECT superseded_by FROM llm_verdict WHERE verdict_id = ?",
        (old.verdict_id,),
    ).fetchone()
    assert prior["superseded_by"] is None
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict_supersession"
    ).fetchone()["c"] == 0
    assert events == []


@pytest.mark.parametrize("table", TASK3_TABLES)
def test_delete_on_audit_tables_is_refused(p8_conn, table, monkeypatch):
    _capture_events(monkeypatch)
    _seed_one_row(p8_conn, table)
    with pytest.raises(sqlite3.IntegrityError):
        p8_conn.execute(f"DELETE FROM {table}")
    assert p8_conn.execute(f"SELECT count(*) AS c FROM {table}").fetchone()["c"] >= 1


def test_update_of_payload_columns_is_refused_and_supersede_columns_stay_writable(
    p8_conn, monkeypatch,
):
    _capture_events(monkeypatch)
    dossier = make_dossier()
    store.record_dossier(p8_conn, dossier, observed_at=FIXED_CLOCK)
    with pytest.raises(sqlite3.IntegrityError):
        p8_conn.execute(
            "UPDATE llm_dossier SET payload = '{}' WHERE dossier_id = ?",
            (dossier.dossier_id,),
        )
    raw_id = store.record_response(
        p8_conn, dossier_id=dossier.dossier_id, response_bytes=b"abc",
        model_id="m", prompt_fingerprint="fp", release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    with pytest.raises(sqlite3.IntegrityError):
        p8_conn.execute(
            "UPDATE llm_response SET response_bytes = ? WHERE response_id = ?",
            (b"zzz", raw_id),
        )
    verdict = make_verdict()
    store.record_verdict(p8_conn, verdict, model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    with pytest.raises(sqlite3.IntegrityError):
        p8_conn.execute(
            "UPDATE llm_verdict SET payload = '{}' WHERE verdict_id = ?",
            (verdict.verdict_id,),
        )
    p8_conn.execute(
        "UPDATE llm_verdict SET superseded_by = 'later', supersede_reason = 'x' "
        "WHERE verdict_id = ?",
        (verdict.verdict_id,),
    )
    row = p8_conn.execute(
        "SELECT superseded_by, supersede_reason FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()
    assert row["superseded_by"] == "later"
    assert row["supersede_reason"] == "x"


def test_record_grounding_report_for_an_issued_call_appends_no_event(
    p8_conn, monkeypatch,
):
    events = _capture_events(monkeypatch)
    report = make_issued_report()
    report_id = store.record_grounding_report(
        p8_conn, report, observed_at=FIXED_CLOCK,
    )
    row = p8_conn.execute(
        "SELECT citations_total, payload FROM llm_grounding_report WHERE report_id = ?",
        (report_id,),
    ).fetchone()
    assert json.loads(row["payload"])["citations_total"] == 1
    assert events == []


def test_record_refusal_is_denied_only_stores_zero_count_report_and_call_refused(
    p8_conn, monkeypatch,
):
    events = _capture_events(monkeypatch)
    refusal = make_refusal()
    report = make_zero_report()
    refusal_id = store.record_refusal(
        p8_conn, refusal, report, observed_at=FIXED_CLOCK,
    )
    stored = p8_conn.execute(
        "SELECT payload FROM llm_refusal WHERE refusal_id = ?", (refusal_id,),
    ).fetchone()
    payload = json.loads(stored["payload"])
    assert payload["denied"]["reason"] == refusal.denied.reason
    report_row = p8_conn.execute(
        "SELECT citations_total, claims_total FROM llm_grounding_report "
        "WHERE dossier_id = ?",
        (report.dossier_id,),
    ).fetchone()
    assert report_row["citations_total"] == 0
    assert report_row["claims_total"] == 0
    assert [event["event_type"] for event in events] == ["call_refused"]


@pytest.mark.parametrize("reason", (
    NOT_ELIGIBLE_FOR_MODEL, USER_REJECTED_EQUIVALENT, BUDGET_EXHAUSTED,
))
def test_record_pre_call_abstention_stores_zero_count_report_and_call_refused(
    p8_conn, monkeypatch, reason,
):
    events = _capture_events(monkeypatch)
    abstention = make_abstention(reason=reason)
    report = make_zero_report(dossier_id=f"dossier-{reason}")
    store.record_pre_call_abstention(
        p8_conn, abstention, report, observed_at=FIXED_CLOCK,
    )
    row = p8_conn.execute(
        "SELECT reason FROM llm_pre_call_abstention WHERE dossier_id = ?",
        (report.dossier_id,),
    ).fetchone()
    assert row["reason"] == reason
    counts = p8_conn.execute(
        "SELECT citations_total FROM llm_grounding_report WHERE dossier_id = ?",
        (report.dossier_id,),
    ).fetchone()
    assert counts["citations_total"] == 0
    assert [event["event_type"] for event in events] == ["call_refused"]


def test_record_call_failure_is_a_row_only(p8_conn, monkeypatch):
    events = _capture_events(monkeypatch)
    failure_id = store.record_call_failure(
        p8_conn,
        dossier_id="dossier-1",
        failure_class="transport",
        explanation="client raised",
        observed_at=FIXED_CLOCK,
    )
    row = p8_conn.execute(
        "SELECT failure_class, explanation FROM llm_call_failure WHERE failure_id = ?",
        (failure_id,),
    ).fetchone()
    assert row["failure_class"] == "transport"
    assert row["explanation"] == "client raised"
    assert events == []


def test_needs_consent_has_no_p8_writer_and_no_p8_event():
    assert not hasattr(store, "record_needs_consent")
    assert not hasattr(store, "record_consent")
    writers = [
        name for name in dir(store)
        if name.startswith("record_") or name == "supersede_verdict"
    ]
    assert "NeedsConsent" not in writers
    needs = NeedsConsent(
        consent_request_id="consent-1",
        requirement=ConsentRequirement(
            file_ids=("file-1",),
            handling_class="public_low",
            items=(("obs-key-1", "0:4"),),
            why="sensitive text",
        ),
    )
    assert not any(
        getattr(store, name) is needs for name in writers
    )


def test_record_refusal_is_atomic_when_append_event_fails(p8_conn, monkeypatch):
    def boom(conn, **fields):
        raise RuntimeError("append failed")

    monkeypatch.setattr(store, "append_event", boom)
    with pytest.raises(RuntimeError):
        store.record_refusal(
            p8_conn, make_refusal(), make_zero_report(), observed_at=FIXED_CLOCK,
        )
    assert p8_conn.execute("SELECT count(*) AS c FROM llm_refusal").fetchone()["c"] == 0
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_grounding_report"
    ).fetchone()["c"] == 0


def test_record_pre_call_abstention_is_atomic_when_append_event_fails(
    p8_conn, monkeypatch,
):
    def boom(conn, **fields):
        raise RuntimeError("append failed")

    monkeypatch.setattr(store, "append_event", boom)
    with pytest.raises(RuntimeError):
        store.record_pre_call_abstention(
            p8_conn, make_abstention(), make_zero_report(), observed_at=FIXED_CLOCK,
        )
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_pre_call_abstention"
    ).fetchone()["c"] == 0
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_grounding_report"
    ).fetchone()["c"] == 0


def test_writer_event_matrix_is_exact_and_has_no_sixth_event(p8_conn, monkeypatch):
    events = _capture_events(monkeypatch)
    store.record_dossier(p8_conn, make_dossier(), observed_at=FIXED_CLOCK)
    store.record_response(
        p8_conn, dossier_id="dossier-1", response_bytes=b"{}",
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK,
    )
    store.record_verdict(p8_conn, make_verdict(), model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    store.record_verdict(
        p8_conn, make_verdict(verdict_id="verdict-2"), model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    store.supersede_verdict(
        p8_conn, "verdict-1", "verdict-2",
        reason="correction", model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    store.record_grounding_report(
        p8_conn, make_issued_report(), observed_at=FIXED_CLOCK,
    )
    store.record_refusal(
        p8_conn, make_refusal(), make_zero_report(dossier_id="dossier-refused"),
        observed_at=FIXED_CLOCK,
    )
    store.record_pre_call_abstention(
        p8_conn, make_abstention(), make_zero_report(dossier_id="dossier-abstain"),
        observed_at=FIXED_CLOCK,
    )
    store.record_call_failure(
        p8_conn, dossier_id="dossier-1", failure_class="timeout",
        explanation="deadline", observed_at=FIXED_CLOCK,
    )
    types = [event["event_type"] for event in events]
    assert types == [
        "model_response_received",
        "validation_verdict",
        "validation_verdict",
        "verdict_superseded",
        "call_refused",
        "call_refused",
    ]
    assert "model_call_issued" not in types
    assert "llm_call_failure" not in types
    assert len(set(types)) == 4


def _seed_one_row(conn, table: str) -> None:
    """Insert the minimum row so a DELETE trigger has something to refuse."""
    if table == "llm_dossier":
        store.record_dossier(conn, make_dossier(), observed_at=FIXED_CLOCK)
    elif table == "llm_response":
        store.record_response(
            conn, dossier_id="dossier-1", response_bytes=b"x",
            model_id="m", prompt_fingerprint="fp", release_audit_id=1,
            observed_at=FIXED_CLOCK,
        )
    elif table == "llm_verdict":
        store.record_verdict(conn, make_verdict(), model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
    elif table == "llm_grounding_report":
        store.record_grounding_report(
            conn, make_issued_report(), observed_at=FIXED_CLOCK,
        )
    elif table == "llm_verdict_supersession":
        store.record_verdict(conn, make_verdict(), model_id="fixture-model", prompt_fingerprint="fp-fixture", release_audit_id=1, observed_at=FIXED_CLOCK)
        store.record_verdict(
            conn, make_verdict(verdict_id="verdict-2"), model_id="fixture-model",
            prompt_fingerprint="fp-fixture",
            release_audit_id=1,
            observed_at=FIXED_CLOCK,
        )
        store.supersede_verdict(
            conn, "verdict-1", "verdict-2",
            reason="seed", model_id="fixture-model",
            prompt_fingerprint="fp-fixture",
            release_audit_id=1,
            observed_at=FIXED_CLOCK,
        )
    elif table == "llm_refusal":
        store.record_refusal(
            conn, make_refusal(), make_zero_report(), observed_at=FIXED_CLOCK,
        )
    elif table == "llm_pre_call_abstention":
        store.record_pre_call_abstention(
            conn, make_abstention(), make_zero_report(), observed_at=FIXED_CLOCK,
        )
    elif table == "llm_call_failure":
        store.record_call_failure(
            conn, dossier_id="dossier-1", failure_class="x",
            explanation="y", observed_at=FIXED_CLOCK,
        )
    else:
        raise AssertionError(table)

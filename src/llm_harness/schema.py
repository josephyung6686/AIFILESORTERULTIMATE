# src/llm_harness/schema.py
"""P8's Task 3 tables. They live inside the one local SQLite database P1 owns.

Budget tables (`llm_scan_budget`, `llm_budget_reservation`) belong wholly to Task 4
and are not created here. `create_llm_schema` is idempotent; tests call it
explicitly. `src/production.py` is not edited.

`record_id` on `llm_verdict` is a VIRTUAL generated projection of `verdict_id` so
P1's `mark_superseded` / `chain` (which key on `record_id`) can be reused. It stores
nothing and does not appear in `PRAGMA table_info`.
"""
from __future__ import annotations

import sqlite3

from database_agent.supersede import supersede_ddl

SUPERSEDE_ADAPTER_COLUMN = "record_id"

TASK3_TABLES: tuple[str, ...] = (
    "llm_dossier",
    "llm_response",
    "llm_verdict",
    "llm_grounding_report",
    "llm_verdict_supersession",
    "llm_refusal",
    "llm_pre_call_abstention",
    "llm_call_failure",
)

LLM_DOSSIER_DDL = """
CREATE TABLE IF NOT EXISTS llm_dossier (
    dossier_id        TEXT PRIMARY KEY,
    call_site         TEXT NOT NULL,
    subject_ref       TEXT NOT NULL,
    eligibility_reason TEXT NOT NULL,
    plan_version      TEXT,
    policy_version    TEXT NOT NULL,
    reduction_rung    TEXT NOT NULL,
    release_id        TEXT NOT NULL,
    payload           TEXT NOT NULL,
    observed_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_dossier_policy ON llm_dossier (policy_version);
CREATE INDEX IF NOT EXISTS llm_dossier_release ON llm_dossier (release_id);
CREATE TRIGGER IF NOT EXISTS llm_dossier_no_delete
BEFORE DELETE ON llm_dossier
BEGIN SELECT RAISE(ABORT, 'a dossier is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_dossier_never_overwritten
BEFORE UPDATE ON llm_dossier
BEGIN SELECT RAISE(ABORT, 'a dossier is append-only, never overwritten'); END;
"""

LLM_RESPONSE_DDL = """
CREATE TABLE IF NOT EXISTS llm_response (
    response_id        TEXT PRIMARY KEY,
    dossier_id         TEXT NOT NULL,
    response_bytes     BLOB NOT NULL,
    model_id           TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    release_audit_id   INTEGER NOT NULL,
    observed_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_response_dossier ON llm_response (dossier_id);
CREATE INDEX IF NOT EXISTS llm_response_fingerprint ON llm_response (prompt_fingerprint);
CREATE TRIGGER IF NOT EXISTS llm_response_no_delete
BEFORE DELETE ON llm_response
BEGIN SELECT RAISE(ABORT, 'a response is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_response_never_overwritten
BEFORE UPDATE ON llm_response
BEGIN SELECT RAISE(ABORT, 'a response is append-only, never overwritten'); END;
"""

LLM_VERDICT_DDL = f"""
CREATE TABLE IF NOT EXISTS llm_verdict (
    verdict_id         TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (verdict_id) VIRTUAL,
    dossier_id         TEXT NOT NULL,
    claim_ref          TEXT NOT NULL,
    outcome            TEXT NOT NULL,
    disposition        TEXT NOT NULL,
    validator_version  TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    plan_version       TEXT,
    payload            TEXT NOT NULL,
    observed_at        TEXT NOT NULL,
    {supersede_ddl("llm_verdict")}
);
CREATE INDEX IF NOT EXISTS llm_verdict_dossier ON llm_verdict (dossier_id);
CREATE INDEX IF NOT EXISTS llm_verdict_validator ON llm_verdict (validator_version);
CREATE INDEX IF NOT EXISTS llm_verdict_policy ON llm_verdict (policy_version);
CREATE TRIGGER IF NOT EXISTS llm_verdict_no_delete
BEFORE DELETE ON llm_verdict
BEGIN SELECT RAISE(ABORT, 'a verdict is superseded, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_verdict_never_overwritten
BEFORE UPDATE OF verdict_id, dossier_id, claim_ref, outcome, disposition,
                 validator_version, policy_version, plan_version, payload, observed_at
    ON llm_verdict
BEGIN SELECT RAISE(ABORT, 'a verdict is superseded, never overwritten'); END;
"""

LLM_GROUNDING_REPORT_DDL = """
CREATE TABLE IF NOT EXISTS llm_grounding_report (
    report_id          TEXT PRIMARY KEY,
    dossier_id         TEXT NOT NULL,
    call_site          TEXT NOT NULL,
    model_id           TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    validator_version  TEXT NOT NULL,
    citations_total    INTEGER NOT NULL,
    claims_total       INTEGER NOT NULL,
    reduction_rung     TEXT NOT NULL,
    release_audit_id   INTEGER,
    payload            TEXT NOT NULL,
    observed_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_grounding_report_dossier
    ON llm_grounding_report (dossier_id);
CREATE INDEX IF NOT EXISTS llm_grounding_report_fingerprint
    ON llm_grounding_report (prompt_fingerprint);
CREATE INDEX IF NOT EXISTS llm_grounding_report_validator
    ON llm_grounding_report (validator_version);
CREATE TRIGGER IF NOT EXISTS llm_grounding_report_no_delete
BEFORE DELETE ON llm_grounding_report
BEGIN SELECT RAISE(ABORT, 'a grounding report is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_grounding_report_never_overwritten
BEFORE UPDATE ON llm_grounding_report
BEGIN SELECT RAISE(ABORT, 'a grounding report is append-only, never overwritten'); END;
"""

LLM_VERDICT_SUPERSESSION_DDL = """
CREATE TABLE IF NOT EXISTS llm_verdict_supersession (
    supersession_id TEXT PRIMARY KEY,
    old_verdict_id  TEXT NOT NULL,
    new_verdict_id  TEXT NOT NULL,
    reason          TEXT NOT NULL,
    observed_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_verdict_supersession_old
    ON llm_verdict_supersession (old_verdict_id);
CREATE TRIGGER IF NOT EXISTS llm_verdict_supersession_no_delete
BEFORE DELETE ON llm_verdict_supersession
BEGIN SELECT RAISE(ABORT, 'a supersession is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_verdict_supersession_never_overwritten
BEFORE UPDATE ON llm_verdict_supersession
BEGIN SELECT RAISE(ABORT, 'a supersession is append-only, never overwritten'); END;
"""

LLM_REFUSAL_DDL = """
CREATE TABLE IF NOT EXISTS llm_refusal (
    refusal_id  TEXT PRIMARY KEY,
    dossier_id  TEXT NOT NULL,
    payload     TEXT NOT NULL,
    observed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_refusal_dossier ON llm_refusal (dossier_id);
CREATE TRIGGER IF NOT EXISTS llm_refusal_no_delete
BEFORE DELETE ON llm_refusal
BEGIN SELECT RAISE(ABORT, 'a refusal is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_refusal_never_overwritten
BEFORE UPDATE ON llm_refusal
BEGIN SELECT RAISE(ABORT, 'a refusal is append-only, never overwritten'); END;
"""

LLM_PRE_CALL_ABSTENTION_DDL = """
CREATE TABLE IF NOT EXISTS llm_pre_call_abstention (
    abstention_id TEXT PRIMARY KEY,
    dossier_id    TEXT NOT NULL,
    reason        TEXT NOT NULL,
    call_site     TEXT NOT NULL,
    subject_ref   TEXT NOT NULL,
    payload       TEXT NOT NULL,
    observed_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_pre_call_abstention_dossier
    ON llm_pre_call_abstention (dossier_id);
CREATE TRIGGER IF NOT EXISTS llm_pre_call_abstention_no_delete
BEFORE DELETE ON llm_pre_call_abstention
BEGIN SELECT RAISE(ABORT, 'a pre-call abstention is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_pre_call_abstention_never_overwritten
BEFORE UPDATE ON llm_pre_call_abstention
BEGIN SELECT RAISE(ABORT, 'a pre-call abstention is append-only, never overwritten'); END;
"""

LLM_CALL_FAILURE_DDL = """
CREATE TABLE IF NOT EXISTS llm_call_failure (
    failure_id    TEXT PRIMARY KEY,
    dossier_id    TEXT NOT NULL,
    failure_class TEXT NOT NULL,
    explanation   TEXT NOT NULL,
    observed_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_call_failure_dossier ON llm_call_failure (dossier_id);
CREATE TRIGGER IF NOT EXISTS llm_call_failure_no_delete
BEFORE DELETE ON llm_call_failure
BEGIN SELECT RAISE(ABORT, 'a call failure is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_call_failure_never_overwritten
BEFORE UPDATE ON llm_call_failure
BEGIN SELECT RAISE(ABORT, 'a call failure is append-only, never overwritten'); END;
"""


def create_llm_schema(conn: sqlite3.Connection) -> None:
    """Create P8's Task 3 tables. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(LLM_DOSSIER_DDL)
    conn.executescript(LLM_RESPONSE_DDL)
    conn.executescript(LLM_VERDICT_DDL)
    conn.executescript(LLM_GROUNDING_REPORT_DDL)
    conn.executescript(LLM_VERDICT_SUPERSESSION_DDL)
    conn.executescript(LLM_REFUSAL_DDL)
    conn.executescript(LLM_PRE_CALL_ABSTENTION_DDL)
    conn.executescript(LLM_CALL_FAILURE_DDL)

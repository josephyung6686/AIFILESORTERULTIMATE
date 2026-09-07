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
    "llm_call_identity",
    "llm_call_reuse",
    "llm_call_usage",
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
    payload           TEXT NOT NULL,
    observed_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_dossier_policy ON llm_dossier (policy_version);
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
    release_id         TEXT NOT NULL,
    observed_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_response_dossier ON llm_response (dossier_id);
CREATE INDEX IF NOT EXISTS llm_response_release ON llm_response (release_id);
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
    release_id    TEXT NOT NULL,
    observed_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_call_failure_dossier ON llm_call_failure (dossier_id);
CREATE INDEX IF NOT EXISTS llm_call_failure_release ON llm_call_failure (release_id);
CREATE TRIGGER IF NOT EXISTS llm_call_failure_no_delete
BEFORE DELETE ON llm_call_failure
BEGIN SELECT RAISE(ABORT, 'a call failure is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_call_failure_never_overwritten
BEFORE UPDATE ON llm_call_failure
BEGIN SELECT RAISE(ABORT, 'a call failure is append-only, never overwritten'); END;
"""


#: `104` R-13 and `00`:44's cache. "Each extraction result is tied to the content
#: hash and the exact process that produced it. The cache key includes content hash,
#: extractor version, analysis tier, model identifier when relevant, and prompt
#: fingerprint for model-derived results" -- and the sentence after it says what the
#: key is FOR: it "makes model or prompt changes auditable".
#:
#: `dimensions` is the canonical JSON the digest was taken over, stored beside it.
#: A digest nobody can read back is a cache nobody can audit: a person asking why a
#: file was asked again gets an answer from this column and from no other row in the
#: database.
#:
#: KEYED ON THE PAIR, so the table stays append-only like its siblings. One identity
#: may reach a second dossier -- the schema widened, so a field the prior did not
#: cover was asked -- and an UPDATE would be the overwrite every other table here
#: refuses. The lookup takes the most recent row for an identity.
LLM_CALL_IDENTITY_DDL = """
CREATE TABLE IF NOT EXISTS llm_call_identity (
    identity_id TEXT NOT NULL,
    dossier_id  TEXT NOT NULL,
    call_site   TEXT NOT NULL,
    subject_ref TEXT NOT NULL,
    dimensions  TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    PRIMARY KEY (identity_id, dossier_id)
);
CREATE INDEX IF NOT EXISTS llm_call_identity_lookup
    ON llm_call_identity (identity_id);
CREATE INDEX IF NOT EXISTS llm_call_identity_subject
    ON llm_call_identity (subject_ref);
CREATE TRIGGER IF NOT EXISTS llm_call_identity_no_delete
BEFORE DELETE ON llm_call_identity
BEGIN SELECT RAISE(ABORT, 'a call identity is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_call_identity_never_overwritten
BEFORE UPDATE ON llm_call_identity
BEGIN SELECT RAISE(ABORT, 'a call identity is append-only, never overwritten'); END;
"""

#: One row per question NOT asked because it already had an answer. `00`:257's
#: "mark the deferred stage" applied to spend rather than to budget: a run that
#: quietly makes fewer calls than the last one is indistinguishable from a run that
#: silently dropped files, and this is the difference written down.
#:
#: NOT an event, and that is a constraint rather than a choice. `database_agent.
#: events` says registration "is a spec-level act (rule 4) ... There is no run-time
#: registration call", and the one addition to that closed set on record was
#: approved by the owner. So `model_call_reused` is a name the owner ratifies, and
#: until then the provenance lives in this row.
LLM_CALL_REUSE_DDL = """
CREATE TABLE IF NOT EXISTS llm_call_reuse (
    reuse_id         TEXT PRIMARY KEY,
    identity_id      TEXT NOT NULL,
    prior_dossier_id TEXT NOT NULL,
    call_site        TEXT NOT NULL,
    subject_ref      TEXT NOT NULL,
    reused_fields    TEXT NOT NULL,
    observed_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_call_reuse_identity ON llm_call_reuse (identity_id);
CREATE INDEX IF NOT EXISTS llm_call_reuse_prior
    ON llm_call_reuse (prior_dossier_id);
CREATE TRIGGER IF NOT EXISTS llm_call_reuse_no_delete
BEFORE DELETE ON llm_call_reuse
BEGIN SELECT RAISE(ABORT, 'a reuse record is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_call_reuse_never_overwritten
BEFORE UPDATE ON llm_call_reuse
BEGIN SELECT RAISE(ABORT, 'a reuse record is append-only, never overwritten'); END;
"""


#: `104` R-14. What the provider said one call cost, in the provider's own numbers.
#: `00`:251 budgets "maximum model cost per scan" and `harness.run_call` settles
#: every call against a constant, so the ledger has never held an observed number.
#:
#: `prompt_cache_hit_tokens` is why this table has the two columns nothing else in
#: the product has: it is the number `104` R-58's frame-first prefix moves, and
#: without it the effect is visible in a bench and nowhere a person or a later run
#: can read it.
#:
#: `response_format` is here because `prompt_fingerprint` does not cover transport
#: parameters, so this row is the only place that can say whether a call was made
#: with JSON mode on. It comes out the day the fingerprint covers it.
#:
#: `reserved_cost` is the OTHER half of the pair and is the only NOT NULL column
#: among the numbers: what the budget put aside before the call is always known,
#: while what the provider reported may not be. The budget is unchanged -- its unit
#: is calls, `cli.FACT_CALL_COST` is 1 against a 200-per-scan ceiling, and
#: `settle_call` still settles one call as one -- and the pair is what makes the
#: distance between the estimate and the truth readable per call and per scan
#: without changing what the budget enforces. Re-denominating the ceiling in tokens
#: is an owner question: `00`:259 names coverage throttling as the failure a wrong
#: number causes.
#:
#: Every observed column is NULLABLE, and that is the audit's answer rather than a
#: gap: a provider that reports no usage still made a call, and a row of nulls says
#: "asked, and it told us nothing" where no row at all is indistinguishable from a
#: call that never happened.
LLM_CALL_USAGE_DDL = """
CREATE TABLE IF NOT EXISTS llm_call_usage (
    usage_id                 TEXT PRIMARY KEY,
    dossier_id               TEXT NOT NULL,
    release_id               TEXT NOT NULL,
    model_id                 TEXT,
    prompt_tokens            INTEGER,
    completion_tokens        INTEGER,
    prompt_cache_hit_tokens  INTEGER,
    prompt_cache_miss_tokens INTEGER,
    response_format          TEXT,
    reserved_cost            TEXT NOT NULL,
    observed_at              TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS llm_call_usage_dossier ON llm_call_usage (dossier_id);
CREATE INDEX IF NOT EXISTS llm_call_usage_release ON llm_call_usage (release_id);
CREATE TRIGGER IF NOT EXISTS llm_call_usage_no_delete
BEFORE DELETE ON llm_call_usage
BEGIN SELECT RAISE(ABORT, 'a usage record is append-only, never removed'); END;
CREATE TRIGGER IF NOT EXISTS llm_call_usage_never_overwritten
BEFORE UPDATE ON llm_call_usage
BEGIN SELECT RAISE(ABORT, 'a usage record is append-only, never overwritten'); END;
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
    conn.executescript(LLM_CALL_IDENTITY_DDL)
    conn.executescript(LLM_CALL_REUSE_DDL)
    conn.executescript(LLM_CALL_USAGE_DDL)

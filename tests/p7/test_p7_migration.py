# tests/p7/test_p7_migration.py
"""A database written before today's columns existed must still open, and still refuse.

`create_privacy_schema` is `CREATE TABLE IF NOT EXISTS`, so a column added to a DDL
string never reaches a database that already has the table. Two were added on
2026-09-02 -- `privacy_policies.suspended_item_kinds` and `release_ledger.
content_digest` -- and the owner has a database written before either.

Without a migration the failure is loud rather than leaky (`set_policy` raises
`OperationalError`), which is the right direction and not a fix: the product would
simply not run for the person it was built for.

The three properties, and the second is the one that matters:

  1. It OPENS. Reading an old row answers the question it can answer.
  2. It still REFUSES. A release minted before `content_digest` existed carries NULL,
     and NULL equals nothing, so it cannot be spent. `ALTER TABLE ADD COLUMN` cannot
     take a NOT NULL without a default, and a default would have been the hole --
     every old release would match whatever produced it.
  3. A migrated table has the SAME columns as a fresh one, so nothing downstream has
     to ask which kind of database it is holding.
"""
from __future__ import annotations

import sqlite3

import pytest

from database_agent.db import create_schema
from privacy.binding import (
    BindingMismatch, ReleaseAlreadySpent, consume_release, content_digest_of,
    mint_release,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, current_policy, set_policy
from privacy.defaults import MORE_REDACTING
from privacy.release import ModelTarget, Released
from privacy.redaction import RedactionManifest
from privacy.schema import POLICIES_TABLE, PRIVACY_ADDED_COLUMNS, create_privacy_schema

AT = "2026-09-02T09:00:00Z"
PLAN = "plan-1"
CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")

#: P7's two tables exactly as they were before 2026-09-02. Written out rather than
#: derived, because the point of the test is a shape this repo no longer produces.
OLD_SCHEMA = f"""
CREATE TABLE {POLICIES_TABLE} (
    policy_version             TEXT PRIMARY KEY,
    plan_version               TEXT NOT NULL,
    operation_mode             TEXT NOT NULL,
    consent_grants             TEXT NOT NULL,
    redaction_settings         TEXT NOT NULL,
    automatic_move_permissions TEXT NOT NULL,
    set_at                     TEXT NOT NULL,
    supersedes                 TEXT,
    superseded_by              TEXT,
    supersede_reason           TEXT
);
CREATE TABLE release_ledger (
    release_id         TEXT PRIMARY KEY,
    model_target       TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    audit_id           INTEGER NOT NULL,
    minted_at          TEXT NOT NULL,
    spent_at           TEXT
);
"""


def _a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(), redaction_settings=dict(MORE_REDACTING),
                automatic_move_permissions={}, plan_version=PLAN, set_at=AT)
    base.update(over)
    return Policy(**base)


@pytest.fixture()
def old_conn(conn):
    """P1's database with P7's PRE-2026-09-02 tables, then today's creator run over it."""
    create_schema(conn)
    conn.executescript(OLD_SCHEMA)
    return conn


def _columns(conn, table) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def test_the_old_tables_really_do_lack_the_columns(old_conn):
    """A guard on the fixture. If it drifts into having them, everything below
    passes while testing nothing."""
    for table, column, _type in PRIVACY_ADDED_COLUMNS:
        assert column not in _columns(old_conn, table)


def test_the_creator_adds_them_and_is_idempotent(old_conn):
    create_privacy_schema(old_conn)
    for table, column, _type in PRIVACY_ADDED_COLUMNS:
        assert column in _columns(old_conn, table)
    before = {t: _columns(old_conn, t) for t, _c, _ty in PRIVACY_ADDED_COLUMNS}
    create_privacy_schema(old_conn)
    assert {t: _columns(old_conn, t) for t, _c, _ty in PRIVACY_ADDED_COLUMNS} == before


def test_a_migrated_table_has_the_same_columns_as_a_fresh_one(old_conn, tmp_path):
    create_privacy_schema(old_conn)
    fresh = sqlite3.connect(":memory:")
    fresh.row_factory = sqlite3.Row
    create_schema(fresh)
    create_privacy_schema(fresh)
    for table, _c, _ty in PRIVACY_ADDED_COLUMNS:
        assert _columns(old_conn, table) == _columns(fresh, table)


def test_a_policy_written_before_the_column_suspends_nothing(old_conn):
    """The read half. `80` §8.3's condition C1 has to survive a migration: a plan
    written before the amendment existed permitted nothing, and must say so."""
    old_conn.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, "
        "operation_mode, consent_grants, redaction_settings, "
        "automatic_move_permissions, set_at) VALUES (?,?,?,?,?,?,?)",
        ("policy-old", PLAN, "cloud_assisted", "[]",
         '{"names":"redacted","previews":"redacted","thumbnails":"redacted",'
         '"ocr_text":"redacted","location_data":"redacted"}', "{}", AT))
    create_privacy_schema(old_conn)
    stored = current_policy(old_conn, plan_version=PLAN)
    assert stored is not None
    assert stored.suspended_item_kinds == ()


def test_a_new_policy_can_be_written_to_a_migrated_database(old_conn):
    """The write half, which is the one that RAISED before the migration existed:
    `_persist` names every column, and `OperationalError` is where the owner's
    end-to-end run would have stopped."""
    create_privacy_schema(old_conn)
    version = set_policy(old_conn, _a_policy(), component_version="0.1.0",
                         user_id="joseph", reason="after migration")
    assert current_policy(old_conn, plan_version=PLAN).policy_version == version


def test_a_release_minted_before_the_term_existed_cannot_be_spent(old_conn):
    """The property that makes a NULLABLE migration safe.

    An old ledger row has NULL where the fourth binding term goes. NULL equals
    nothing, so `consume_release` refuses it -- CR-02's guarantee holds backwards in
    time as well as forwards. A `DEFAULT` on the ALTER would have been the hole:
    every release minted before the term existed would then match whatever produced
    that default.
    """
    old_conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, audit_id, minted_at, spent_at) VALUES (?,?,?,?,?,?,NULL)",
        ("release-from-yesterday", '{"locality":"cloud","model_id":"acme-large",'
         '"provider":"Acme"}', "fp-1", "policy-1", 1, AT))
    create_privacy_schema(old_conn)

    stale = Released(
        release_id="release-from-yesterday", audit_id=1, policy_version="policy-1",
        materialised_items=(), redaction_manifest=RedactionManifest(entries=()),
        model_target=CLOUD)
    with pytest.raises(BindingMismatch):
        consume_release(old_conn, stale, model_target=CLOUD,
                        prompt_fingerprint="fp-1", policy_version="policy-1",
                        content_digest=content_digest_of(()))
    assert old_conn.execute(
        "SELECT spent_at FROM release_ledger WHERE release_id = ?",
        ("release-from-yesterday",)).fetchone()["spent_at"] is None


def test_a_release_minted_after_the_migration_spends_normally(old_conn):
    """The control. A migrated ledger is a working ledger, not a bricked one."""
    create_privacy_schema(old_conn)
    version = set_policy(old_conn, _a_policy(), component_version="0.1.0",
                         user_id="joseph", reason="after migration")
    policy = current_policy(old_conn, plan_version=PLAN)
    digest = content_digest_of(())
    release_id = mint_release(
        old_conn, policy=policy, model_target=CLOUD, prompt_fingerprint="fp-2",
        content_digest=digest, audit_id=1, minted_at=AT)
    live = Released(release_id=release_id, audit_id=1,
                    policy_version=version, materialised_items=(),
                    redaction_manifest=RedactionManifest(entries=()),
                    model_target=CLOUD)
    consume_release(old_conn, live, model_target=CLOUD, prompt_fingerprint="fp-2",
                    policy_version=version, content_digest=digest)
    with pytest.raises(ReleaseAlreadySpent):
        consume_release(old_conn, live, model_target=CLOUD,
                        prompt_fingerprint="fp-2", policy_version=version,
                        content_digest=digest)

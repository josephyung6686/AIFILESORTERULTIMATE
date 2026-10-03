# src/understanding/store.py
"""Consent for this pass, the response cache, and the audit log.

The consent row stores the sentence the person accepted, not a secret.
The cache key is the dossier hash. The audit row names the file, the
fields, the model, and the token counts. It has no column for a key.
"""
from __future__ import annotations

import json
import sqlite3

STATEMENT: str = (
    "Dossier text goes to the provider's servers. The dossier is the "
    "filename, path hints, kind, the first 400 words of text or OCR, and "
    "key metadata. Whole files are not sent. Protected files, held files, "
    "and areas marked private are not sent. Offline mode sends nothing."
)

CONSENT_DDL = """
CREATE TABLE IF NOT EXISTS understanding_consent (
    decision_id INTEGER PRIMARY KEY,
    corpus_root TEXT NOT NULL,
    statement   TEXT NOT NULL,
    user_id     TEXT NOT NULL,
    decided_at  TEXT NOT NULL
);
"""

CACHE_DDL = """
CREATE TABLE IF NOT EXISTS understanding_cache (
    cache_key      TEXT PRIMARY KEY,
    model_id       TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    response_json  TEXT NOT NULL,
    stored_at      TEXT NOT NULL
);
"""

AUDIT_DDL = """
CREATE TABLE IF NOT EXISTS understanding_audit (
    audit_id           INTEGER PRIMARY KEY,
    file_id            TEXT NOT NULL,
    fields_sent        TEXT NOT NULL,
    model_id           TEXT NOT NULL,
    prompt_tokens      INTEGER,
    completion_tokens  INTEGER,
    cache_hit          INTEGER NOT NULL,
    recorded_at        TEXT NOT NULL,
    exception_class    TEXT
);
"""


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(CONSENT_DDL + CACHE_DDL + AUDIT_DDL)
    # A database created before exception_class existed still has the table.
    # Creating the table when it is missing does not add a column to an old one.
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(understanding_audit)")
    }
    if "exception_class" not in columns:
        conn.execute(
            "ALTER TABLE understanding_audit ADD COLUMN exception_class TEXT")


def record_consent(conn: sqlite3.Connection, *, corpus_root: str, user_id: str,
                   decided_at: str) -> None:
    ensure_schema(conn)
    if not corpus_root or not user_id or not decided_at:
        raise ValueError("consent needs a folder, a person, and a time")
    conn.execute(
        "INSERT INTO understanding_consent "
        "(corpus_root, statement, user_id, decided_at) VALUES (?, ?, ?, ?)",
        (corpus_root, STATEMENT, user_id, decided_at),
    )


def consent_recorded(conn: sqlite3.Connection, corpus_root: str) -> bool:
    ensure_schema(conn)
    row = conn.execute(
        "SELECT decision_id FROM understanding_consent WHERE corpus_root = ? "
        "ORDER BY decision_id DESC LIMIT 1",
        (corpus_root,),
    ).fetchone()
    return row is not None


def cache_get(conn: sqlite3.Connection, cache_key: str) -> str | None:
    ensure_schema(conn)
    row = conn.execute(
        "SELECT response_json FROM understanding_cache WHERE cache_key = ?",
        (cache_key,),
    ).fetchone()
    if row is None:
        return None
    return row[0]


def cache_put(conn: sqlite3.Connection, *, cache_key: str, model_id: str,
              response_json: str, stored_at: str) -> None:
    from understanding.dossier import PROMPT_VERSION
    ensure_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO understanding_cache "
        "(cache_key, model_id, prompt_version, response_json, stored_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (cache_key, model_id, PROMPT_VERSION, response_json, stored_at),
    )


def audit(conn: sqlite3.Connection, *, file_id: str, fields: tuple[str, ...],
          model_id: str, prompt_tokens: int | None, completion_tokens: int | None,
          cache_hit: bool, recorded_at: str,
          exception_class: str | None = None) -> None:
    ensure_schema(conn)
    conn.execute(
        "INSERT INTO understanding_audit "
        "(file_id, fields_sent, model_id, prompt_tokens, completion_tokens, "
        "cache_hit, recorded_at, exception_class) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (file_id, json.dumps(list(fields)), model_id, prompt_tokens,
         completion_tokens, 1 if cache_hit else 0, recorded_at,
         exception_class),
    )

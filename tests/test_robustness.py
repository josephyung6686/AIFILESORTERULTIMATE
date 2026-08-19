"""Gaps found auditing the sixteen Done-means against the tests that exist.

Done-means 11 requires the writer to reject "an attempt to redefine one of the
nineteen reserved names". The frozen table checks that at import (Task 5), but
nothing proved the check actually fires — a passing set-intersection assertion
only shows today's table is clean, not that a dirty one would be caught.
"""
import importlib.util
import sqlite3
import sys
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database
from database_agent.events import RESERVED_EVENT_TYPES

SRC = Path(__file__).resolve().parents[1] / "src" / "database_agent"


def _load_events_variant(tmp_path: Path, mutate: str, name: str):
    """Import a copy of events.py with one line changed, to prove an import-time
    guard fires. The real module is untouched."""
    source = (SRC / "events.py").read_text(encoding="utf-8").replace(
        '    "consent_requested": None,', mutate
    )
    module_path = tmp_path / f"{name}.py"
    module_path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def test_redefining_a_reserved_name_is_an_import_error(tmp_path: Path):
    # Done-means 11, rule 1. A part that tries to redefine one of §8.2's nineteen
    # must be refused. Because registration is spec-level, the refusal happens at
    # import — so a bad table cannot even be loaded, let alone written through.
    with pytest.raises(ImportError, match="shadow reserved"):
        _load_events_variant(tmp_path, '    "discovery": None,', "events_shadowing")


def test_a_specialization_of_a_non_reserved_base_is_an_import_error(tmp_path: Path):
    # The base of a typed specialization must be one of the nineteen. Otherwise
    # `base_event_type` would point at a name no SPEC reserves, and B5's rollup
    # ("every specialization is queryable as its base") would silently break.
    with pytest.raises(ImportError, match="specialization base"):
        _load_events_variant(
            tmp_path, '    "consent_requested": "not a reserved name",', "events_badbase"
        )


def test_the_nineteen_are_exactly_the_8_2_names():
    # Guards against a typo silently shrinking the reserved set.
    assert RESERVED_EVENT_TYPES == frozenset({
        "discovery", "stat observation", "hashing", "extraction", "OCR",
        "fact creation", "fact rejection", "graph-edge creation",
        "group membership proposal", "user group decision", "template application",
        "destination-tree edit", "placement recommendation",
        "filename-collision resolution", "planned move", "executed move",
        "failed move", "external modification detection", "undo",
    })


def test_opening_a_database_yields_one_ready_to_use(tmp_path: Path):
    # Contract out §6 publishes "one local SQLite database ... transactional and
    # inspectable". A handle whose tables do not exist is not that. Requiring every
    # caller to remember a second call is a footgun: the skeleton and every
    # neighbouring part would each have to know, and one that forgets gets
    # "no such table" at its first write rather than at open.
    conn = open_database(tmp_path / "agent.sqlite")
    tables = {r["name"] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in ("files", "events", "learning_resets", "budget_ceilings",
                  "vector_arrays", "scan_resource_usage"):
        assert table in tables, f"{table} missing from a freshly opened database"
    conn.close()


def test_create_schema_stays_idempotent_and_callable(tmp_path: Path):
    # Neighbouring parts and the existing tests call it explicitly. Wiring it into
    # open_database must not make a second call an error.
    conn = open_database(tmp_path / "agent.sqlite")
    create_schema(conn)
    create_schema(conn)
    assert conn.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    conn.close()


def test_the_append_only_triggers_survive_a_reopen(tmp_path: Path):
    # R6 must hold across process restarts, not just in the session that created
    # the schema. A trigger created but not persisted would leave history mutable
    # for every later run.
    path = tmp_path / "agent.sqlite"
    first = open_database(path)
    first.execute(
        "INSERT INTO events (event_type, subsystem, observed_at) "
        "VALUES ('discovery', 'P3', '2026-08-19T00:00:00+00:00')"
    )
    first.close()

    second = open_database(path)
    with pytest.raises(sqlite3.IntegrityError):
        second.execute("UPDATE events SET explanation = 'rewritten'")
    with pytest.raises(sqlite3.IntegrityError):
        second.execute("DELETE FROM events")
    second.close()


def test_the_writer_and_the_learning_store_share_one_scope_vocabulary():
    """One concept, one definition. Two copies of the six scopes would let a scope
    be accepted by the writer and rejected by the reader — storable, permanently
    unreadable, and a silently lost user correction."""
    from database_agent.events import CORRECTION_SCOPES
    from database_agent.learning import SCOPES
    assert SCOPES is CORRECTION_SCOPES

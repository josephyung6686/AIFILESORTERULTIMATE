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


def test_the_reserved_set_is_exactly_the_8_2_names_and_the_approved_twentieth():
    # Guards against a typo silently shrinking the reserved set -- and, now,
    # against one silently growing it. Nineteen of these are §8.2's list verbatim.
    # `refused move` is the twentieth: the owner (Joseph) approved it on
    # 2026-08-29 because §8.2 reserved `failed move` for a move that was tried and
    # broke and reserved nothing for a move refused before it was tried, and P12
    # cannot record what it mostly does without saying which happened.
    assert RESERVED_EVENT_TYPES == frozenset({
        "discovery", "stat observation", "hashing", "extraction", "OCR",
        "fact creation", "fact rejection", "graph-edge creation",
        "group membership proposal", "user group decision", "template application",
        "destination-tree edit", "placement recommendation",
        "filename-collision resolution", "planned move", "executed move",
        "failed move", "refused move", "external modification detection", "undo",
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


def test_p1_stores_p3s_basic_record_and_derives_none_of_it(conn, tmp_path):
    """P1 SPEC Contract in: P3 hands P1 "its stat result (size, timestamps) ... and
    the §1.2 per-file fields — filename, normalized filename, extension" and P1's
    obligation is "store them". P3 SPEC O5: R2 is "the only computation of this
    record"; a second derivation is a contract violation, and P3's plan has a drift
    test that fails on one.

    The strong form: hand P1 values that DISAGREE with the filesystem and assert P1
    stored what it was given. If P1 re-derives, the assertion fails — and downstream
    §3.7 word-boundary matching, §2.9's duplicate family and P5's filesystem
    observations would all be reading a string P3 never produced.
    """
    from database_agent.db import create_schema
    from database_agent.files_table import get_file, record_file

    create_schema(conn)
    path = tmp_path / "on-disk-name.txt"
    path.write_bytes(b"bytes")

    file_id = record_file(
        conn, path,
        filename="P3-SUPPLIED.txt",
        normalized_filename="p3-supplied.txt",
        extension=".p3",
        observed_size=999999,
        observed_timestamps='{"mtime": "from-P3"}',
        parent_folder_context="corpus",
        mime_type="text/plain", detected_format="txt",
        scan_state="scanned", materialized=True,
    )
    row = get_file(conn, file_id)
    assert row["filename"] == "P3-SUPPLIED.txt"
    assert row["normalized_filename"] == "p3-supplied.txt"
    assert row["extension"] == ".p3"
    assert row["observed_size"] == 999999
    assert row["observed_timestamps"] == '{"mtime": "from-P3"}'


def test_the_r2_fields_have_no_defaults(conn, tmp_path):
    """O5 again: a default would let a caller omit the field and get P1's derivation
    silently, which is the violation wearing a friendlier face."""
    import pytest as _pytest

    from database_agent.db import create_schema
    from database_agent.files_table import record_file

    create_schema(conn)
    path = tmp_path / "f.txt"
    path.write_bytes(b"bytes")
    with _pytest.raises(TypeError):
        record_file(conn, path, parent_folder_context="c", mime_type=None,
                    detected_format=None, scan_state="scanned", materialized=True)


def test_p1_adopts_the_scan_identity_p3_publishes(conn):
    """OQ16, ratified 2026-08-20: P3 owns the scan, so P3 publishes `scan_run_id`
    and P1's resource row is keyed on that value rather than on one P1 minted.

    Three documents previously named three scan identities — P1's private
    `scan_id`, P3's private `scan_run_id`, and 11-ops-runtime §3 writing
    `scan_run_id — P3's scan` as though it were already shared. With three
    identities and no join, P13 cannot show §8.6's six counters beside the file
    counts from the same scan, and a P2 bundle cannot name the scan it captured.
    """
    from database_agent.db import create_schema
    from database_agent.scan_usage import scan_resource_usage, start_scan

    create_schema(conn)
    returned = start_scan(conn, scan_run_id="p3-run-7")
    assert returned == "p3-run-7"
    assert scan_resource_usage(conn, "p3-run-7") is not None


def test_p1_mints_no_scan_identity_of_its_own(conn):
    """P1 adopting P3's value means P1 has no fallback that would mint a second
    one. A default here would let a caller omit it and get a private identifier
    that nothing else can join — the exact failure OQ16 closed."""
    import pytest as _pytest

    from database_agent.db import create_schema
    from database_agent.scan_usage import start_scan

    create_schema(conn)
    with _pytest.raises(TypeError):
        start_scan(conn)

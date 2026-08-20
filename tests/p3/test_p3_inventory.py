# tests/p3/test_p3_inventory.py
import json
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.inventory import (
    CURATION_CURATED, CURATION_INCIDENTAL, CURATION_SIGNAL_VALUES,
    CURATION_UNDETERMINED, directory_inventory,
)
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


def _scan(conn, corpus, *, roots=()):
    selection = record_selection(conn, sources=[corpus], candidate_roots=list(roots),
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_every_non_excluded_directory_has_a_row(ready, corpus: Path):
    # Done-means 15, first half.
    (corpus / "Coursework" / "2026").mkdir(parents=True)
    (corpus / "Coursework" / "syllabus.pdf").write_bytes(b"x")
    (corpus / "node_modules").mkdir()
    run = _scan(ready, corpus)

    rows = {r["directory_path"]: r for r in directory_inventory(ready, run)}
    assert set(rows) == {
        str(corpus), str(corpus / "Coursework"), str(corpus / "Coursework" / "2026"),
    }
    assert rows[str(corpus)]["parent_directory"] is None
    assert rows[str(corpus / "Coursework")]["parent_directory"] == str(corpus)


def test_a_row_carries_5_10s_counts_and_the_mix(ready, corpus: Path):
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "a.pdf").write_bytes(b"x")
    (corpus / "Coursework" / "b.pdf").write_bytes(b"x")
    (corpus / "Coursework" / "c.json").write_bytes(b"{}")
    (corpus / "Coursework" / "nested").mkdir()
    run = _scan(ready, corpus)

    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "Coursework")][0]
    assert row["file_count"] == 3
    assert row["subdirectory_count"] == 1
    assert json.loads(row["extension_mix"]) == {".pdf": 2, ".json": 1}


def test_counts_and_mix_see_only_non_excluded_files(ready, corpus: Path):
    (corpus / "dist").mkdir()
    (corpus / "dist" / "bundle.js").write_bytes(b"x")
    (corpus / "a.pdf").write_bytes(b"x")
    run = _scan(ready, corpus)
    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus)][0]
    assert row["file_count"] == 1
    assert row["subdirectory_count"] == 0
    assert json.loads(row["extension_mix"]) == {".pdf": 1}


def test_every_signal_is_undetermined_and_none_is_silently_incidental(ready, corpus: Path):
    # Done-means 15, second half. The threshold is Deferred: §1.1 gives no number,
    # no ratio, and no list of which extensions read as software material.
    (corpus / "AIKonic Project").mkdir()
    for name in ("a.json", "b.json", "c.json", "d.py"):
        (corpus / "AIKonic Project" / name).write_bytes(b"{}")
    (corpus / "Empty").mkdir()
    run = _scan(ready, corpus)

    rows = directory_inventory(ready, run)
    assert rows
    assert {r["curation_signal"] for r in rows} == {CURATION_UNDETERMINED}
    assert CURATION_INCIDENTAL not in {r["curation_signal"] for r in rows}


def test_an_empty_directory_is_undetermined_not_incidental(ready, corpus: Path):
    # §8.6: "leave the file or group in review rather than guessing".
    (corpus / "Empty").mkdir()
    run = _scan(ready, corpus)
    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "Empty")][0]
    assert row["file_count"] == 0
    assert row["curation_signal"] == CURATION_UNDETERMINED


def test_the_evidence_travels_with_the_value(ready, corpus: Path):
    # §8.2's "structured explanation or evidence reference".
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    (corpus / "notes.md").write_bytes(b"x")
    run = _scan(ready, corpus)

    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "app")][0]
    evidence = json.loads(row["curation_evidence"])
    assert evidence["file_count"] == 0          # every child is an excluded descendant
    assert evidence["subdirectory_count"] == 0
    assert evidence["extension_mix"] == {}
    # R3 records the one marker that fired; R6 records all of them.
    assert evidence["project_root_markers"] == ["package.json", "go.mod"]


def test_the_three_signal_values_are_5_10s_three():
    assert CURATION_SIGNAL_VALUES == ("curated", "incidental", "undetermined")


def test_p3_holds_no_threshold_and_no_software_material_list():
    # SPEC Deferred. Guessing either would be P3 authoring what §1.1 does not supply.
    import scan_agent.inventory as module
    source = Path(module.__file__).read_text()
    # Tokens a threshold would have to introduce. The docstring quotes §1.1's
    # deferral in prose, so this checks code, not commentary.
    for forbidden in ("_THRESHOLD", "_RATIO", "PERCENT", "SOFTWARE_MATERIAL",
                      "if evidence[", "sum(", ">=", "<=", "0.5"):
        assert forbidden not in source, forbidden


def test_the_curation_signal_changes_nothing_else(tmp_path: Path, corpus: Path, monkeypatch):
    # Done-means 16: "the same corpus scanned with and without a curation threshold
    # authored yields identical files rows, identical exclusion verdicts, and
    # identical cache verdicts. The signal is an observation, not an exclusion rule."
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "a.pdf").write_bytes(b"a")
    (corpus / "node_modules").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "Cargo.toml").write_bytes(b"[package]")
    (corpus / "b.txt").write_bytes(b"b")

    def everything_but_the_signal(conn):
        return (
            [tuple(r) for r in conn.execute(
                "SELECT current_path, content_hash, observed_size, mime_type, "
                "scan_state, directory_position FROM files ORDER BY current_path")],
            [tuple(r) for r in conn.execute(
                "SELECT path, rule, rule_subject, applies_to FROM exclusion_verdicts "
                "ORDER BY path, applies_to")],
            [tuple(r) for r in conn.execute(
                "SELECT observed_path, verdict, reason FROM stat_cache_verdicts "
                "ORDER BY observed_path")],
        )

    def run_against(db_name):
        conn = open_database(tmp_path / db_name)
        create_schema(conn)
        create_scan_schema(conn)
        run = _scan(conn, corpus)
        return conn, run

    baseline_conn, _ = run_against("baseline.sqlite")

    import scan_agent.inventory as module
    monkeypatch.setattr(module, "curation_signal", lambda evidence: CURATION_CURATED)
    authored_conn, authored_run = run_against("authored.sqlite")

    assert everything_but_the_signal(baseline_conn) == \
           everything_but_the_signal(authored_conn)
    assert {r["curation_signal"] for r in directory_inventory(authored_conn, authored_run)} \
           == {CURATION_CURATED}
    baseline_conn.close()
    authored_conn.close()

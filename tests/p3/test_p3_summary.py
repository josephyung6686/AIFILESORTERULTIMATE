# tests/p3/test_p3_summary.py
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.deferrals import DEFERRED_BUDGET, scan_deferrals
from scan_agent.exclusion import RULE_LITERAL_DIRECTORY_NAME, RULE_PROJECT_ROOT_DESCENDANT
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.summary import R5_COUNTERS, scan_run_summary

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus, budget=NEVER):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=budget)


def test_the_summary_has_exactly_the_specs_five_counters():
    assert R5_COUNTERS == (
        "files_indexed", "paths_excluded_by_rule", "files_reused_from_stat_cache",
        "files_recomputed", "files_deferred",
    )


def test_the_summary_publishes_no_sixth_counter(ready, corpus: Path):
    # §8.6's example line draws `indexed` from P3; the extraction, model-review and
    # unreadable counts are P5's and P8's, and P3 does not invent a slot for them.
    (corpus / "a.txt").write_bytes(b"a")
    run = _scan(ready, corpus)
    assert tuple(scan_run_summary(ready, run)) == R5_COUNTERS


def test_a_first_scan_counts_indexed_and_recomputed(ready, corpus: Path):
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"x")
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert summary["files_indexed"] == 3
    assert summary["files_recomputed"] == 3
    assert summary["files_reused_from_stat_cache"] == 0
    assert summary["files_deferred"] == 0


def test_a_second_scan_counts_reuse(ready, corpus: Path):
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_bytes(b"x")
    _scan(ready, corpus)
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert summary["files_indexed"] == 2
    assert summary["files_reused_from_stat_cache"] == 2
    assert summary["files_recomputed"] == 0


def test_exclusions_are_counted_by_rule(ready, corpus: Path):
    (corpus / "node_modules").mkdir()
    (corpus / "dist").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    (corpus / "app" / "main.go").write_bytes(b"package main")
    run = _scan(ready, corpus)
    by_rule = scan_run_summary(ready, run)["paths_excluded_by_rule"]
    assert by_rule[RULE_LITERAL_DIRECTORY_NAME] == 2
    assert by_rule[RULE_PROJECT_ROOT_DESCENDANT] == 2


def test_budget_exhaustion_is_counted_and_the_corpus_cannot_read_as_complete(
        ready, corpus: Path):
    # Done-means 13.
    for name in ("a.txt", "b.txt", "c.txt", "d.txt", "e.txt"):
        (corpus / name).write_bytes(b"x")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "f.txt").write_bytes(b"x")

    calls = {"n": 0}

    def after_two():
        calls["n"] += 1
        return calls["n"] > 2

    run = _scan(ready, corpus, budget=after_two)
    summary = scan_run_summary(ready, run)

    assert summary["files_deferred"] > 0
    assert summary["files_indexed"] < 6
    # everything already recorded is retained (§8.6)
    assert summary["files_indexed"] > 0
    # and the unreached frontier is on the record, directories included
    deferred = scan_deferrals(ready, run)
    assert {d["reason"] for d in deferred} == {DEFERRED_BUDGET}
    assert any(d["is_directory"] for d in deferred)


def test_exhaustion_relaxes_no_exclusion_rule(ready, corpus: Path):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." P3 does not finish faster by letting node_modules through.
    #
    # The fixture is ordered so the RULE fires before the budget trips. Entries are
    # listed sorted by path, so the walk reaches a.txt, then node_modules, then
    # z.txt, and the predicate returns True on the third call. A budget that tripped
    # first would defer node_modules as unreached, and the assertion below would
    # pass without the §1.1 rule ever running — which is the whole thing under test.
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "buried.txt").write_bytes(b"x")
    (corpus / "a.txt").write_bytes(b"x")
    (corpus / "z.txt").write_bytes(b"x")

    calls = {"n": 0}

    def after_two():
        calls["n"] += 1
        return calls["n"] > 2

    run = _scan(ready, corpus, budget=after_two)

    # the budget really did trip, so this is the exhaustion path
    assert scan_run_summary(ready, run)["files_deferred"] == 1
    # and the exclusion is why node_modules is absent — the verdict is on the record
    excluded = ready.execute(
        "SELECT path, rule FROM exclusion_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchall()
    assert [(r["path"], r["rule"]) for r in excluded] == [
        (str(corpus / "node_modules"), RULE_LITERAL_DIRECTORY_NAME),
    ]
    paths = [r["current_path"] for r in ready.execute("SELECT current_path FROM files")]
    assert not any("node_modules" in p for p in paths)


def test_a_dataless_detection_is_not_an_r5_counter(ready, corpus: Path, monkeypatch):
    # 11 §5: the progress line must be able to NAME these files rather than folding
    # them into another count. Naming is `dataless_detections`, not an R5 slot.
    import scan_agent.corpus_source as module
    (corpus / "cloud.pdf").write_bytes(b"x")
    real_entries = module.FilesystemCorpusSource.entries

    def entries(self, directory):
        from dataclasses import replace
        return [replace(e, dataless=e.name == "cloud.pdf")
                for e in real_entries(self, directory)]

    monkeypatch.setattr(module.FilesystemCorpusSource, "entries", entries)
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert tuple(summary) == R5_COUNTERS
    assert summary["files_indexed"] == 0
    assert summary["files_deferred"] == 0
    assert ready.execute(
        "SELECT count(*) c FROM dataless_detections WHERE scan_run_id = ?", (run,)
    ).fetchone()["c"] == 1

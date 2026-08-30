# tests/p3/test_p3_set_aside_reporting.py
"""§1.1's OTHER exclusions, said out loud -- the half of "never silently omitted"
that only protected containers had.

`cli.py`'s protected-container block states the standing rule and states it well:
"Marked, counted, never silently omitted" has no success-path exception, so it is
said as soon as it is known. It says it about ONE of §1.1's four rules.
`tree_design.upstream.protected_areas` filters `exclusion_verdicts` to
`RULE_PROTECTED_CONTAINER` and drops the other three on the floor, so a scan that
set aside `Library/` -- where a real person's mail, app data and, in the run that
found this, their tax records live -- reported one line: "Protected containers: 0
marked, none opened", and nothing at all about the folder it had just skipped.

A person cannot ask for a file back that they were never told was left behind.
This module publishes the same reading for the rules that had no reader.
"""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import (
    RULE_LITERAL_DIRECTORY_NAME, RULE_PROJECT_ROOT_DESCENDANT,
    RULE_PROTECTED_CONTAINER,
)
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.summary import SetAside, set_aside_paths

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def test_a_rule_excluded_folder_is_reported_by_name(ready, corpus: Path):
    # The run that found this: `Library/important.txt` held "my tax records 2025",
    # and the plan named one file and never mentioned the folder it had skipped.
    (corpus / "lab.txt").write_bytes(b"coursework")
    (corpus / "Library").mkdir()
    (corpus / "Library" / "important.txt").write_bytes(b"tax records")
    run = _scan(ready, corpus)

    set_aside = set_aside_paths(ready, scan_run_id=run)

    assert [item.display_label for item in set_aside] == ["Library"]
    assert set_aside[0].rule == RULE_LITERAL_DIRECTORY_NAME
    assert set_aside[0].path.endswith("Library")


def test_every_rule_that_fired_is_reported_not_just_the_first(ready, corpus: Path):
    # Two different §1.1 rules on one scan. A reader that reported the first rule
    # it saw would tell the person about `Library` and stay silent about the
    # project tree, which is the same silence one folder narrower.
    (corpus / "Library").mkdir()
    (corpus / "Library" / "mail.txt").write_bytes(b"mail")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "pkg.js").write_bytes(b"junk")
    project = corpus / "code"
    project.mkdir()
    (project / "package.json").write_bytes(b"{}")
    (project / "src.py").write_bytes(b"x")
    run = _scan(ready, corpus)

    set_aside = set_aside_paths(ready, scan_run_id=run)
    by_label = {item.display_label: item.rule for item in set_aside}

    assert by_label["Library"] == RULE_LITERAL_DIRECTORY_NAME
    assert by_label["node_modules"] == RULE_LITERAL_DIRECTORY_NAME
    assert RULE_PROJECT_ROOT_DESCENDANT in by_label.values()


def test_a_protected_container_is_not_repeated_here(ready, corpus: Path):
    # It has its own block, with its own wording about never being opened. Saying
    # it twice in two voices is how a person comes to believe two things happened.
    (corpus / "Notes.app").mkdir()
    (corpus / "Notes.app" / "secret.txt").write_bytes(b"private")
    (corpus / "Library").mkdir()
    (corpus / "Library" / "mail.txt").write_bytes(b"mail")
    run = _scan(ready, corpus)

    set_aside = set_aside_paths(ready, scan_run_id=run)

    assert [item.display_label for item in set_aside] == ["Library"]
    assert RULE_PROTECTED_CONTAINER not in {item.rule for item in set_aside}


def test_a_scan_that_excluded_nothing_reports_nothing(ready, corpus: Path):
    # An empty tuple, not a sentence. Whether a clean scan says "0 set aside" is
    # the caller's presentation choice; inventing a row here would put a folder in
    # the reading that no rule excluded.
    (corpus / "lab.txt").write_bytes(b"coursework")
    run = _scan(ready, corpus)

    assert set_aside_paths(ready, scan_run_id=run) == ()


def test_the_reading_carries_no_field_a_file_inside_could_occupy(ready, corpus: Path):
    # §1.1: an excluded path yields no `files` row and no descendants. P3 never
    # listed the folder's contents, so there is nothing here that could name one
    # -- and no field a later caller in a hurry could populate with one.
    fields = set(SetAside.__dataclass_fields__)

    assert fields == {"path", "display_label", "rule", "rule_subject"}

# tests/p3/test_p3_exclusion.py
import sqlite3
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, CATEGORY_MEMBERS,
    EXCLUDED_DIRECTORY_NAMES, EXCLUSION_CATEGORIES, RULE_CATEGORY,
    RULE_LITERAL_DIRECTORY_NAME, exclusion_for, exclusion_verdicts, record_exclusion,
)
from scan_agent.run import start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


@pytest.fixture()
def run(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    selection = record_selection(conn, sources=[tmp_path], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return start_scan_run(conn, selection)


def test_the_eleven_names_are_1_1s_eleven_verbatim_and_in_order():
    assert EXCLUDED_DIRECTORY_NAMES == (
        "node_modules", ".git", "venv", "build", "dist", "target", "vendor",
        "Pods", "site-packages", "Library", "__pycache__",
    )
    assert len(EXCLUDED_DIRECTORY_NAMES) == 11


def test_each_of_the_eleven_is_excluded_as_a_directory(tmp_path: Path):
    for name in EXCLUDED_DIRECTORY_NAMES:
        verdict = exclusion_for(tmp_path / name, is_dir=True,
                                applies_to=APPLIES_TO_SCANNED_SOURCE)
        assert verdict is not None, name
        assert verdict.rule == RULE_LITERAL_DIRECTORY_NAME
        assert verdict.rule_subject == name
        assert verdict.applies_to == APPLIES_TO_SCANNED_SOURCE


def test_the_rule_is_about_directories(tmp_path: Path):
    # §1.1: "the system excludes directories that should not participate".
    # A FILE named `build` is not a directory and this rule does not reach it.
    assert exclusion_for(tmp_path / "build", is_dir=False,
                         applies_to=APPLIES_TO_SCANNED_SOURCE) is None


def test_an_ordinary_directory_is_not_excluded(tmp_path: Path):
    assert exclusion_for(tmp_path / "Coursework", is_dir=True,
                         applies_to=APPLIES_TO_SCANNED_SOURCE) is None


def test_the_five_categories_are_named_and_have_no_members():
    # SPEC Deferred: §1.1 names the categories and enumerates no member of any of
    # them. The rule is wired and empty; guessing a member would be P3 authoring a
    # gazetteer the design does not supply.
    assert EXCLUSION_CATEGORIES == (
        "build artifacts", "caches", "auto-save folders", "previews",
        "generated dependency trees",
    )
    assert set(CATEGORY_MEMBERS) == set(EXCLUSION_CATEGORIES)
    assert all(members == () for members in CATEGORY_MEMBERS.values())


def test_the_category_rule_fires_the_day_a_member_is_authored(tmp_path: Path, monkeypatch):
    # The rule is wired: authoring the deferred list is a data change, not a code
    # change. This test proves the wiring without authoring anything.
    from types import MappingProxyType

    import scan_agent.exclusion as module
    authored = dict.fromkeys(EXCLUSION_CATEGORIES, ())
    authored["caches"] = ("SomeHandAuthoredCacheDirectory",)
    monkeypatch.setattr(module, "CATEGORY_MEMBERS", MappingProxyType(authored))

    verdict = module.exclusion_for(tmp_path / "SomeHandAuthoredCacheDirectory",
                                   is_dir=True, applies_to=APPLIES_TO_SCANNED_SOURCE)
    assert verdict is not None
    assert verdict.rule == RULE_CATEGORY
    assert verdict.rule_subject == "caches"


def test_a_verdict_names_the_rule_that_rejected_the_path(conn, run, tmp_path: Path):
    # Done-means 6, and §8.2's "structured explanation or evidence reference".
    verdict = exclusion_for(tmp_path / "node_modules", is_dir=True,
                            applies_to=APPLIES_TO_SCANNED_SOURCE)
    record_exclusion(conn, run, verdict)
    row = exclusion_verdicts(conn, run)[0]
    assert row["path"] == str(tmp_path / "node_modules")
    assert row["rule"] == RULE_LITERAL_DIRECTORY_NAME
    assert row["rule_subject"] == "node_modules"
    assert row["applies_to"] == APPLIES_TO_SCANNED_SOURCE
    assert row["observed_at"]


def test_applies_to_has_exactly_the_specs_two_values():
    assert APPLIES_TO_SCANNED_SOURCE == "scanned source"
    assert APPLIES_TO_CANDIDATE_ROOT == "candidate root"


def test_a_verdict_is_never_deleted(conn, run, tmp_path: Path):
    # SPEC, "What P3 never overwrites": a verdict explaining why a path was skipped
    # is not deleted when the path later becomes eligible.
    record_exclusion(conn, run, exclusion_for(tmp_path / ".git", is_dir=True,
                                              applies_to=APPLIES_TO_SCANNED_SOURCE))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM exclusion_verdicts")


def test_an_exclusion_appends_no_event(conn, run, tmp_path: Path):
    # SPEC Q13 is OPEN: §8.2's event record is keyed on file ID and an excluded
    # directory has no file record. This plan does not answer it, so R3 lives in
    # its own table and no event is appended. When Q13 closes, this test changes.
    record_exclusion(conn, run, exclusion_for(tmp_path / "dist", is_dir=True,
                                              applies_to=APPLIES_TO_SCANNED_SOURCE))
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0


from scan_agent.exclusion import (
    PROJECT_ROOT_MARKERS, RULE_PROJECT_ROOT_DESCENDANT, project_root_markers_in,
)


def test_the_four_markers_are_1_1s_four_verbatim():
    assert PROJECT_ROOT_MARKERS == (
        "package.json", "requirements.txt", "Cargo.toml", "go.mod",
    )


def test_each_marker_makes_its_directory_a_project_root():
    for marker in PROJECT_ROOT_MARKERS:
        listing = [("README.md", False), (marker, False), ("src", True)]
        assert project_root_markers_in(listing) == (marker,)


def test_a_marker_must_be_a_file_not_a_directory():
    # §1.1: "indicated by FILES such as package.json".
    assert project_root_markers_in([("package.json", True)]) == ()


def test_markers_are_reported_in_the_designs_order():
    listing = [("go.mod", False), ("package.json", False)]
    assert project_root_markers_in(listing) == ("package.json", "go.mod")


def test_a_descendant_of_a_project_root_is_rejected(tmp_path: Path):
    # Done-means 4. Both a file and a subdirectory inside the marker-bearing
    # directory are descendants of it.
    markers = ("package.json",)
    for child, is_dir in (("notes.txt", False), ("src", True)):
        verdict = exclusion_for(tmp_path / "app" / child, is_dir=is_dir,
                                applies_to=APPLIES_TO_SCANNED_SOURCE,
                                project_root_markers=markers)
        assert verdict is not None
        assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT
        assert verdict.rule_subject == "package.json"


def test_the_marker_file_is_itself_a_descendant_and_is_rejected(tmp_path: Path):
    verdict = exclusion_for(tmp_path / "app" / "package.json", is_dir=False,
                            applies_to=APPLIES_TO_SCANNED_SOURCE,
                            project_root_markers=("package.json",))
    assert verdict is not None
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT


def test_the_marker_bearing_directory_itself_is_not_rejected_by_this_rule(tmp_path: Path):
    # SPEC Q9 is OPEN: §1.1 says "descendants of software project roots" and says
    # nothing about the root directory itself. This plan implements §1.1's literal
    # word and decides nothing about whether that directory may be a candidate root.
    assert exclusion_for(tmp_path / "app", is_dir=True,
                         applies_to=APPLIES_TO_SCANNED_SOURCE,
                         project_root_markers=()) is None


def test_the_project_root_rule_outranks_the_literal_name_rule(tmp_path: Path):
    # A `build` directory inside a project root is rejected as a descendant. Both
    # rules would fire; the verdict names one, deterministically.
    verdict = exclusion_for(tmp_path / "app" / "build", is_dir=True,
                            applies_to=APPLIES_TO_SCANNED_SOURCE,
                            project_root_markers=("Cargo.toml",))
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT
    assert verdict.rule_subject == "Cargo.toml"

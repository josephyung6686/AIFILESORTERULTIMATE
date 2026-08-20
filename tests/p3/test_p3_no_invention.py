# tests/p3/test_p3_no_invention.py
"""Done-means 17, and the standing record that P3 answers no open question in code."""
from pathlib import Path

import pytest

import scan_agent
from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"

SOURCE_DIR = Path(scan_agent.__file__).parent


def modules():
    return sorted(SOURCE_DIR.glob("*.py"))


def all_source() -> str:
    return "\n".join(path.read_text() for path in modules())


def fixture_mime(path: Path) -> str | None:
    return "application/pdf" if path.suffix == ".pdf" else None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_the_observed_values_and_the_stored_values_are_the_same_values(ready, corpus: Path):
    # Done-means 17, as the drift test O5 argues for: "the two would drift".
    import os
    document = corpus / "Syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    observed = os.stat(document)

    selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    run = scan(ready, selection, source=FilesystemCorpusSource(),
               mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
               budget_exhausted=NEVER)

    row = ready.execute("SELECT * FROM files").fetchone()
    verdict = ready.execute(
        "SELECT * FROM stat_cache_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchone()

    assert row["observed_size"] == observed.st_size == verdict["observed_size"]
    assert verdict["observed_modification_time"] == observed.st_mtime
    assert row["filename"] == document.name
    assert row["extension"] == document.suffix
    assert row["mime_type"] == fixture_mime(document)


def test_p3_hashes_nothing_itself():
    # O5: a second hash is a contract violation. P1's hash_file is the only one.
    source = all_source()
    assert "hashlib" not in source
    assert "sha256" not in source
    assert "md5" not in source


def test_p3_determines_no_mime_type():
    # SPEC Q6 is OPEN: whether P3 sniffs a signature or records an extension-derived
    # type P5 later corrects is unsettled. P3 does neither.
    source = all_source()
    assert "mimetypes" not in source
    assert "%PDF" not in source
    assert "magic" not in source


def test_p3_defines_no_filename_normalization():
    # SPEC Q1 is OPEN: Unicode form, case folding, whitespace and separator collapse,
    # extension retention and diacritic handling are all unstated.
    source = all_source()
    assert "unicodedata" not in source
    assert "casefold" not in source
    assert "NFC" not in source and "NFD" not in source


def test_p3_holds_no_scan_state_enumeration():
    # SPEC Q4 is OPEN: the enumeration, and its relationship to §8.2's "extraction
    # status by extractor tier", is unsettled. The caller supplies the value.
    source = all_source()
    for value in ('"scanned"', '"unscanned"', '"pending"', '"superseded_content"',
                  '"stale"', '"complete"', '"skipped"'):
        assert value not in source, value


def test_p3_writes_no_extraction_run_and_names_no_completeness():
    # P4 Open question 6 stays open. None of P4's eight values means "the bytes are
    # not on this machine", and P3 chooses none and adds no ninth.
    source = all_source()
    for name in ("extraction_runs", "completeness", "text_units", "file_facts",
                 "handling_class", "sensitivity_state", "plan_version"):
        assert name not in source, name


def test_p3_holds_no_ceiling_and_no_threshold():
    # §8.6 names a configurable ceiling for neither traversal nor hashing, and SPEC
    # Q15 is OPEN. Every budget decision arrives as a caller-supplied predicate.
    source = all_source()
    # Constant-style spellings: a held ceiling would have to be bound to a name.
    # SQL's `LIMIT 1` and prose mentions of a deferred threshold are not ceilings.
    for token in ("MAX_", "_LIMIT", "CEILING", "THRESHOLD", "max_pages", "max_time"):
        assert token not in source, token


def test_p3_never_deletes_or_updates_an_event():
    source = all_source().upper()
    assert "DELETE FROM EVENTS" not in source
    assert "UPDATE EVENTS" not in source


def test_p3_never_updates_the_files_table():
    # P1 owns identity resolution (§8.2); every files write goes through observe_path.
    source = all_source().upper()
    assert "UPDATE FILES" not in source
    assert "INSERT INTO FILES" not in source


def test_every_event_names_p3_and_only_through_event_defaults():
    # M8. `subsystem` is set in exactly one place.
    for path in modules():
        source = path.read_text()
        if path.name == "authorship.py":
            continue
        assert "subsystem=" not in source, path.name
        if "append_event(" in source:
            assert "event_defaults(" in source, path.name


def test_an_exclusion_still_appends_no_event():
    # SPEC Q13 is OPEN: §8.2's event record is keyed on file ID and an excluded
    # directory has no file record. This test is the standing record of that; it
    # changes the day Q13 closes.
    source = (SOURCE_DIR / "exclusion.py").read_text()
    assert "append_event" not in source
    assert "event_defaults" not in source


def test_nothing_branches_on_cross_folder_moves():
    # SPEC Q12 is OPEN: §1.1 records the selection, §6 and §7 never mention it, and
    # no part is assigned its enforcement. P3 records it and enforces nothing.
    for path in modules():
        source = path.read_text()
        if path.name == "selection.py":
            assert "if cross_folder_moves" not in source
            continue
        assert "cross_folder_moves" not in source, path.name


def test_p3_holds_no_placement_vocabulary():
    # §1.1's roots are context, not permission. (This guard never asserted anything
    # about scan identity — it was named for a claim its body does not make, and
    # SPEC Q16 has since closed the other way: P3 DOES publish the scan identity.)
    source = all_source()
    for token in ("placement", "destination_node", "authorize", "approved_move",
                  "template_id", "domain_id"):
        assert token not in source, token


def test_p3_reads_no_volume_identifier():
    # P1 OQ9 is OPEN and P1's volume_id is session-tagged and nullable on purpose.
    # No P3 decision is built on it.
    source = all_source()
    assert "volume_id" not in source
    assert "OBSERVATION_SESSION" not in source


def test_the_deferred_exclusion_categories_are_still_empty():
    # SPEC Deferred: §1.1 names five categories and enumerates no member.
    from scan_agent.exclusion import CATEGORY_MEMBERS
    assert all(members == () for members in CATEGORY_MEMBERS.values())


def test_the_curation_threshold_is_still_unauthored():
    # SPEC Deferred, and Done-means 15.
    from scan_agent.inventory import CURATION_UNDETERMINED, curation_signal
    for evidence in (
        {"file_count": 0, "subdirectory_count": 0, "extension_mix": {},
         "project_root_markers": []},
        {"file_count": 900, "subdirectory_count": 40,
         "extension_mix": {".json": 800, ".py": 100}, "project_root_markers": []},
        {"file_count": 12, "subdirectory_count": 0, "extension_mix": {".pdf": 12},
         "project_root_markers": []},
    ):
        assert curation_signal(evidence) == CURATION_UNDETERMINED

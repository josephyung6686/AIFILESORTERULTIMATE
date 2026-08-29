# tests/p3/test_p3_no_invention.py
"""Done-means 17, and the standing record that P3 answers no open question in code."""
import ast
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
    """Raw text, comments and docstrings included. Use `code_tokens()` instead for
    any assertion of the form "this token appears nowhere"."""
    return "\n".join(path.read_text() for path in modules())


def _docstrings(tree: ast.AST) -> set[int]:
    """The id() of every node that is a docstring, so it can be skipped."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def code_tokens() -> set[str]:
    """Every name and literal P3's modules actually USE -- prose excluded.

    An assertion that a token appears nowhere in a module is the technique that has
    produced a false result seven times in this project, because a comment or a
    docstring EXPLAINING why a value is absent matches the scan for that value. Here
    it broke the other way round and cost a real edit: `scan.py` gained a comment
    saying no later stage could emit a `completeness` value, and the test asserting
    P3 names no completeness value failed on the word inside the explanation.

    Parsing is the fix. Identifiers, attribute names, keyword-argument names, import
    aliases and string and numeric literals are what the code DOES; comments and
    docstrings are what it says about itself, and only the first kind can invent a
    vocabulary.
    """
    return code_names() | code_strings()


def code_names() -> set[str]:
    """Identifiers only: what P3's code CALLS things."""
    tokens: set[str] = set()
    for path in modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        skip = _docstrings(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                tokens.add(node.id)
            elif isinstance(node, ast.Attribute):
                tokens.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                tokens.add(node.name)
            elif isinstance(node, ast.arg):
                tokens.add(node.arg)
            elif isinstance(node, ast.keyword) and node.arg:
                tokens.add(node.arg)
            elif isinstance(node, ast.alias):
                tokens.add(node.name)
                if node.asname:
                    tokens.add(node.asname)
    return tokens


def code_strings() -> set[str]:
    """String and numeric LITERALS only, docstrings excluded: the values P3 holds.

    Separate from `code_names()` because the distinction is load-bearing. `pending`
    is a local in `traversal.py`'s breadth-first queue and `complete` could be any
    variable; neither is P3 holding a scan-state enumeration. A held vocabulary VALUE
    has to be written down as a literal, and this is the set of literals.
    """
    tokens: set[str] = set()
    for path in modules():
        tree = ast.parse(path.read_text(), filename=str(path))
        skip = _docstrings(tree)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant) and id(node) not in skip
                    and isinstance(node.value, (str, int, float))
                    and not isinstance(node.value, bool)):
                tokens.add(str(node.value))
    return tokens


def code_text() -> str:
    """`code_tokens()` joined, for substring assertions such as `MAX_`."""
    return "\n".join(sorted(code_tokens()))


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
    tokens = code_tokens()
    assert "unicodedata" not in tokens
    assert "casefold" not in tokens
    assert "NFC" not in tokens and "NFD" not in tokens


def test_p3_holds_no_scan_state_enumeration():
    # SPEC Q4 is OPEN: the enumeration, and its relationship to §8.2's "extraction
    # status by extractor tier", is unsettled. The caller supplies the value.
    values = code_strings()
    for value in ("scanned", "unscanned", "pending", "superseded_content",
                  "stale", "complete", "skipped"):
        assert value not in values, value


def test_p3_writes_no_extraction_run_and_names_no_completeness():
    # P4 Open question 6 is CLOSED (C4, 2026-08-20): the ninth `completeness` value
    # is `dataless`, and it means exactly "the bytes are not on this machine". That
    # does not change P3's obligation -- the value is P4's vocabulary and P5 is its
    # writer. P3 records the detection and names no status.
    tokens = code_tokens()
    for name in ("extraction_runs", "completeness", "text_units", "file_facts",
                 "handling_class", "sensitivity_state", "plan_version"):
        assert name not in tokens, name


def test_p3_holds_no_ceiling_and_no_threshold():
    # §8.6 names a configurable ceiling for neither traversal nor hashing, and SPEC
    # Q15 is OPEN. Every budget decision arrives as a caller-supplied predicate.
    source = code_text()
    # Constant-style spellings: a held ceiling would have to be bound to a name.
    # SQL's `LIMIT 1` and prose mentions of a deferred threshold are not ceilings.
    for token in ("MAX_", "_LIMIT", "CEILING", "THRESHOLD", "max_pages", "max_time"):
        assert token not in source, token


def test_p3_never_deletes_or_updates_an_event():
    source = code_text().upper()
    assert "DELETE FROM EVENTS" not in source
    assert "UPDATE EVENTS" not in source


def test_p3_never_updates_the_files_table():
    # P1 owns identity resolution (§8.2); every files write goes through observe_path.
    source = code_text().upper()
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

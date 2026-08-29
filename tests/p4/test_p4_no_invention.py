# tests/p4/test_p4_no_invention.py
"""The standing record that P4 answers no open question in code, and invents nothing.

Every token guard runs against `code_only`: the module with its docstrings and
comments removed. `assert "gazetteer" not in source` otherwise matches the docstring
that says P4 authors no gazetteer, which is the opposite of a violation.
"""
import ast
import inspect
from pathlib import Path

import pytest

import evidence_shape
from database_agent.budget import CEILING_KEYS
from database_agent.events import RESERVED_EVENT_TYPES
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.authorship import (
    EXTRACTION_EVENT, OCR_EVENT, RUN_EVENT_TYPES, UnauthoredEvent, check_author,
    event_defaults,
)
from evidence_shape.observation import (
    OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS, observation_key,
)
from evidence_shape.text_units import TEXT_UNIT_FIELDS
from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, EXTRACTOR_RELIABILITY_STATES, OPEN_QUESTIONS,
    RELIABILITY_STATES, SIGNAL_TIERS, SOURCE_TYPES,
)

SOURCE_DIR = Path(evidence_shape.__file__).parent

#: Data, not code. The nineteen worked examples are the SPEC's own table, and a
#: format-catalogue guard that read them as code would have to forbid the SPEC's own
#: examples. Every structural guard below still covers this module.
FIXTURE_DATA = "fixtures.py"


def modules():
    return sorted(path for path in SOURCE_DIR.glob("*.py")
                  if path.name != "__init__.py")


def code_only(path: Path) -> str:
    """The module's source with docstrings and comments removed."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                              ast.AsyncFunctionDef))
                and body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:] or [ast.Pass()]
    return ast.unparse(tree)


def all_code(*, skip=()) -> str:
    return "\n".join(code_only(path) for path in modules()
                     if path.name not in skip)


def identifiers(*, skip=()) -> set[str]:
    """Every name the package binds or reads -- and no string literal.

    Some obligations cannot be guarded on text at all, because the published contract
    quotes the very words a violation would use: `OPEN_QUESTIONS["OQ6"]` contains
    "iCloud dataless" because that is the question being HELD OPEN. A question is
    text; an answer would be a name.
    """
    names: set[str] = set()
    for path in modules():
        if path.name in skip:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, ast.arg):
                names.add(node.arg)
            elif isinstance(node, ast.keyword) and node.arg:
                names.add(node.arg)
    return names


def module_constants(path: Path):
    """Top-level `NAME = <literal>` bindings, as (name, value-node) pairs."""
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        elif isinstance(node, ast.AnnAssign):
            target = node.target
        else:
            continue
        if isinstance(target, ast.Name) and node.value is not None:
            yield target.id, node.value


# ── P4 runs no extractor, opens no file, and reaches no network ───────────────

def test_p4_imports_nothing_outside_the_stdlib_and_p1():
    # "P4 runs no extractor. §2.8 is a shape, not a reader." The import graph is the
    # exact form of that claim: no format library can be reached from here.
    allowed = {"__future__", "collections", "dataclasses", "datetime", "hashlib",
               "json", "sqlite3", "types", "unicodedata", "uuid",
               "database_agent", "evidence_shape"}
    for path in modules():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            for name in names:
                assert name.split(".")[0] in allowed, f"{path.name}: {name}"


def test_p4_opens_no_file():
    # Every test in this part builds its records in memory or from a fixture string.
    # That is what makes the whole part testable before P5 exists.
    source = all_code()
    for token in ("pathlib", "Path(", "open(", "os.", "io."):
        assert token not in source, token


def test_p4_sniffs_no_format_and_holds_no_routing_table():
    # SPEC Deferred: the MIME/signature -> extractor routing table is P5's, and
    # "which structured strings each extractor should recognize" is P5's per format.
    source = all_code(skip=(FIXTURE_DATA,))
    for token in ("mimetypes", "magic", "%PDF", "zipfile", "tarfile", "openpyxl",
                  "PyPDF", "PIL", "pytesseract", "csv", "docx", "pdf", "exif"):
        assert token not in source, token


def test_p4_reaches_no_network_and_prompts_no_model():
    # §2.8: extraction "does not treat model output as proof". P8 owns the model.
    source = all_code()
    for token in ("urllib", "requests", "socket", "prompt", "openai", "anthropic"):
        assert token not in source, token


# ── P4 invents no value ──────────────────────────────────────────────────────

def test_the_package_publishes_no_numeric_constant_outside_its_one_allowlist():
    # SHAPE_VERSION is D2's (a vocabulary change is a contract revision plus a bump);
    # SIGNAL_TIERS is §2.6's three levels. There is no third, and in particular no
    # §8.6 ceiling: those numbers are configuration and P1 owns the keys.
    allowed = {"SHAPE_VERSION", "SIGNAL_TIERS"}
    found = set()
    for path in modules():
        for name, value in module_constants(path):
            numbers = ([value] if isinstance(value, ast.Constant)
                       else list(value.elts) if isinstance(value, ast.Tuple) else [])
            if numbers and all(isinstance(node, ast.Constant)
                               and isinstance(node.value, (int, float))
                               and not isinstance(node.value, bool)
                               for node in numbers):
                found.add(name)
    assert found == allowed


def test_p4_authors_no_threshold_weight_gazetteer_or_template_library():
    # SPEC Deferred, every row of it: gazetteer contents (§3.7), positional weights
    # per zone (§3.7), the 200-300 domain template library (§5.7), the residual
    # library (§7.2-§7.4), date-candidate patterns (§3.10).
    source = all_code()
    for token in ("GAZETTEER", "gazetteer", "THRESHOLD", "threshold", "CEILING",
                  "MAX_", "_LIMIT", "WEIGHT", "weight", "TEMPLATE_LIBRARY",
                  "RESIDUAL", "re.compile", "import re"):
        assert token not in source, token


def test_the_context_budget_is_caller_supplied_and_p4_holds_no_length():
    # B4, ratified 2026-08-20: the ceiling now HAS a home -- P1's sixteenth key
    # `evidence.context_window` -- and it belongs in the run's `config` so it is
    # fingerprinted (two runs at different context widths must not look identical to
    # §3.4's cache key). What has not changed is that P4 holds no NUMBER: the value is
    # read from P1 by the caller and arrives as data. That is the claim this guards.
    assert "context_truncated" in OBSERVATION_FIELDS
    assert "evidence.context_window" in CEILING_KEYS      # P1 owns the ceiling
    assert "evidence.context_window" not in all_code()    # P4 does not read it itself
    source = all_code()
    for token in ("truncate(", "MAX_CONTEXT", "CONTEXT_LENGTH", "context_length"):
        assert token not in source, token


def test_p4_normalizes_nothing():
    # RAW-1 and §2.8: raw_value is "exactly that wording" -- no case folding, no
    # Unicode normalization, no whitespace collapse, no trimming. `unicodedata` is
    # imported for one call, `category(...) == "Cc"`, which is control-character
    # detection inside locator escaping and rewrites nothing.
    source = all_code()
    for token in ("unicodedata.normalize", "NFC", "NFD", "casefold", ".lower()",
                  ".upper()"):
        assert token not in source, token


def test_there_is_no_seventh_vocabulary():
    # Six closed vocabularies, published as ten names because three are derived
    # subsets. A seventh appearing here is a contract revision, not an edit.
    published = set()
    for name, value in module_constants(SOURCE_DIR / "vocabulary.py"):
        if (isinstance(value, ast.Tuple) and value.elts
                and all(isinstance(node, ast.Constant) and isinstance(node.value, str)
                        for node in value.elts)):
            published.add(name)
    assert published == {
        "ZONES", "INDEXED_SEGMENT_KINDS", "LABEL_SEGMENT_KINDS", "SOURCE_TYPES",
        "RELIABILITY_STATES", "EXTRACTOR_RELIABILITY_STATES", "COMPLETENESS",
        "ZERO_OBSERVATION_COMPLETENESS", "ANALYSIS_TIERS", "REGION_UNITS"}


# ── P4 authors no event ──────────────────────────────────────────────────────

def test_p4_supplies_no_default_author_and_refuses_p1():
    # M8: "The acting part authors; P1 writes. P1 appends no event on its own
    # initiative." §8.2 requires the responsible subsystem on every event.
    with pytest.raises(UnauthoredEvent):
        check_author("")
    with pytest.raises(UnauthoredEvent):
        check_author("P1")
    with pytest.raises(TypeError):
        event_defaults(component_version="1.0.0", event_type=EXTRACTION_EVENT)


def test_the_subsystem_field_is_set_in_exactly_one_module():
    for path in modules():
        if path.name == "authorship.py":
            continue
        assert "subsystem" not in code_only(path), path.name


def test_p4_registers_no_event_type_and_adds_no_event_field():
    # P1 Contract out §3, rule 4: registration is a spec-level act. Both names are
    # already among §8.2's nineteen. MINOR 1: §8.2 lists eleven fields and P4 adds none.
    assert "register" not in all_code()
    assert set(RUN_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_minor_2_the_ocr_event_and_the_ocr_vocabulary_member_are_two_things():
    # §8.2 spells the event `OCR`; `source_type` and `analysis_tier` spell their own
    # member `ocr`. Neither is a case variant of the other and nothing folds one into
    # the other -- P1's writer validates against §8.2's spelling and would reject it.
    assert OCR_EVENT == "OCR"
    assert OCR_EVENT not in SOURCE_TYPES
    assert OCR_EVENT not in ANALYSIS_TIERS
    assert "ocr" in SOURCE_TYPES and "ocr" in ANALYSIS_TIERS
    assert "ocr" not in RESERVED_EVENT_TYPES


def test_minor_3_the_third_supersede_column_is_supersede_reason():
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")
    assert set(SUPERSEDE_COLUMNS) <= set(OBSERVATION_ROW_FIELDS)
    assert "supersession_reason" not in all_code()
    # M1: `preferred` is P1's fourth column and is NOT adopted. §8.2 gives preference
    # to the resolver and §3.2 places the resolver after extraction.
    assert "preferred" not in OBSERVATION_ROW_FIELDS


def test_minor_8_the_citation_handle_excludes_the_extractor_version_on_purpose():
    # NOT a bug to be fixed. §8.5's replay diff compares a new extractor version
    # against a prior result for the same content; a key carrying the version would
    # make every row a false diff and leave nothing to diff against.
    parameters = inspect.signature(observation_key).parameters
    assert set(parameters) == {"content_hash", "extractor_name", "locator", "raw_value"}
    assert "extractor_version" not in parameters


# ── Every open question, held open ───────────────────────────────────────────

def test_the_one_open_question_is_published_and_is_not_answered():
    # OQ1 closed as I4 (analysis_tier's four values); OQ2 closed 2026-08-20.
    # Both are deliberately absent.
    assert sorted(OPEN_QUESTIONS) == ["OQ4"]
    assert "OQ1" not in OPEN_QUESTIONS   # closed as I4
    assert "OQ2" not in OPEN_QUESTIONS   # closed 2026-08-20
    for key, text in OPEN_QUESTIONS.items():
        assert text.strip().endswith("?"), key


def test_oq2_ratified_the_content_hash_owns_the_observation(p4_conn):
    # OQ2 CLOSED, ratified 2026-08-20: the content hash owns the observation, and two
    # file records sharing a hash share one observation set. §2.8 still requires a file
    # identifier, so both fields stay — but `file_id` is a way in, not the owner.
    # These are the same assertions this test made while the question was open, and
    # they are now REQUIRED rather than merely permitted: a foreign key to `files`
    # would make the file record the owner in DDL, which is the answer we did not take.
    assert "file_id" in OBSERVATION_FIELDS
    assert "content_hash" in OBSERVATION_FIELDS
    referenced = {row[2] for row in p4_conn.execute(
        "PRAGMA foreign_key_list(evidence)")}
    assert referenced == {"extraction_runs"}


def test_oq3_ratified_one_reliability_vocabulary_extractors_stamp_two():
    # C1 CLOSED, ratified 2026-08-20: ONE vocabulary -- §3.13's six -- and extractors
    # may stamp only `direct` | `possible` (D11). These are the same assertions this
    # test made while the question was open, and they are now REQUIRED rather than
    # merely P4's reading. A seventh state, or a separate observation-level
    # vocabulary, is now a contract violation and not an open alternative. P6 must
    # STATE this rather than re-ask it -- see its open question 12.
    assert len(RELIABILITY_STATES) == 6
    assert set(EXTRACTOR_RELIABILITY_STATES) < set(RELIABILITY_STATES)


def test_oq4_stays_open_p4_stores_no_handling_class(p4_conn):
    # "Is the §8.4 handling class stored per observation or only per file?" P4 adds no
    # privacy field (P7 owns handling classes) and instead guarantees BOTH
    # granularities are addressable, so either answer stays implementable.
    for table in ("evidence", "extraction_runs", "text_units"):
        columns = {row[1] for row in p4_conn.execute(f"PRAGMA table_info({table})")}
        assert not columns & {"handling_class", "sensitivity", "sensitivity_state",
                              "privacy_class", "redaction"}
    assert "observation_key" in OBSERVATION_FIELDS      # addressable per observation
    assert "file_id" in OBSERVATION_FIELDS              # joinable per file
    assert TEXT_UNIT_FIELDS[:2] == ("run_id", "container_path")   # D12's key


def test_oq5_ratified_a_user_corrects_facts_never_an_observation():
    # C3 CLOSED, ratified 2026-08-20: a user corrects the FACT at P6 and never
    # `raw_value`. A better OCR pass supersedes (new row, old still readable, §8.2).
    # So P4 publishes no user-authored writer and no reliability state an extractor
    # could reach that would mean one -- the same assertions, now required. RAW-2
    # survives because there is exactly one way to mint evidence.
    import evidence_shape.store as store
    writers = sorted(name for name in dir(store)
                     if name.startswith(("record_", "supersede_", "correct_",
                                         "amend_", "edit_")))
    assert writers == ["record_observation", "record_run", "record_run_event",
                       "record_text_unit", "supersede_chain", "supersede_observation"]
    assert "user_confirmed" not in EXTRACTOR_RELIABILITY_STATES


def test_oq6_closed_the_ninth_completeness_is_dataless():
    # "What completeness does a source that is not on this machine carry?" None of the
    # eight fit: deferred is budget exhaustion, unreadable is encrypted-or-damaged,
    # metadata_only is a format decision. Ratified 2026-08-20: a ninth, and it is
    # `dataless` -- the word P1 (`DatalessFileRefused`), P3 (`scan_agent.dataless`)
    # and 11-ops-runtime §5 already use. Coining `not_local` beside them would have
    # been two vocabularies for one concept, this project's most expensive defect.
    assert len(COMPLETENESS) == 9
    assert COMPLETENESS[-1] == "dataless"
    # that it forbids observations is pinned in test_p4_vocabulary.py, which owns
    # ZERO_OBSERVATION_COMPLETENESS -- not restated here across files.
    for not_coined in ("not_downloaded", "offline", "remote", "evicted", "unavailable",
                       "not_local", "cloud_only"):
        assert not_coined not in COMPLETENESS
    # Guarded on NAMES, not on text: OPEN_QUESTIONS["OQ6"] quotes "iCloud dataless"
    # because that is the question being held open. A detection would be a name.
    lowered = {name.lower() for name in identifiers()}
    for token in ("dataless", "icloud", "downloaded", "evicted"):
        assert not any(token in name for name in lowered), token


def test_the_signal_tier_hierarchy_is_carried_but_not_catalogued():
    # M2 puts §2.6's three levels on the record. WHICH field belongs to which tier is
    # P5's catalogue (SPEC Deferred), and P4 names no EXIF field: enumerating one
    # would be the gazetteer the hard rules forbid. Task 16's fixture 7 is the case
    # that proves it -- DateTimeOriginal is both "camera EXIF" and a "capture time".
    assert SIGNAL_TIERS == (1, 2, 3)
    source = all_code(skip=(FIXTURE_DATA,))
    for field_name in ("DateTimeOriginal", "GPSLatitude", "Make", "Model",
                       "PixelXDimension", "Software"):
        assert field_name not in source, field_name

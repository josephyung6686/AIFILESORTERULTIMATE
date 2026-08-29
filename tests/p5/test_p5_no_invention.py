# tests/p5/test_p5_no_invention.py
"""The standing record that P5 answers no open question in code.

Every guard is RUNTIME INTROSPECTION. A source-text guard matches its own docstrings
— this file's own prose names `python-docx`, Apple Vision and 200 DPI, all of which
are design quotations — so nothing here reads a `.py` file.
"""
import importlib
import inspect
import re
import sqlite3
from pathlib import Path

import pytest

import extractors
from database_agent.db import create_schema
from database_agent.events import RESERVED_EVENT_TYPES

from extractors.archive import ArchiveManifest, extract_archive
from extractors.authorship import AUTHORED_EVENT_TYPES, SUBSYSTEM
from extractors.image import extract_image
from extractors.long_tail import POTENTIALLY_SENSITIVE, extract_long_tail
from extractors.ocr import extract_ocr
from extractors.ocr_policy import document_ocr_decision, text_layer_state
from extractors.pdf import extract_pdf
from extractors.router import SOURCE_TYPE_BY_FORMAT, route
from extractors.schema import create_extraction_schema
from extractors.shape import (
    ANALYSIS_TIERS, ForbiddenAnalysisTier, P5_ANALYSIS_TIERS, run,
)
from extractors.structured_text import extract_structured_text

SOURCE_DIR = Path(extractors.__file__).parent

#: The one module-level pattern P5 owns: P4 D8's "soft-hyphen/line-break repair",
#: which the design names as one of exactly four mechanical transforms.
MECHANICAL_REPAIR = ("extractors.shape", "_LINE_BREAK_HYPHEN")

RESOLUTION = re.compile(r"^\d+\s*[x×]\s*\d+$")
LANGUAGE_TAG = re.compile(r"^[a-z]{2}-[A-Z]{2}$")


def p5_modules():
    return [importlib.import_module(f"extractors.{path.stem}")
            for path in sorted(SOURCE_DIR.glob("*.py")) if path.stem != "__init__"]


def constants(module):
    """Module-level names and values, minus dunders — which is where `__doc__` is."""
    return {name: value for name, value in vars(module).items()
            if not name.startswith("__")}


def strings(value):
    """Every string reachable inside a module-level constant."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)


def module_strings():
    for module in p5_modules():
        for name, value in constants(module).items():
            if (inspect.isclass(value) or inspect.isfunction(value)
                    or inspect.ismodule(value)):
                continue
            for text in strings(value):
                yield module.__name__, name, text


# --- the value guards -------------------------------------------------------

def test_p5_holds_no_number_anywhere():
    # One assertion for six Deferred rows: threshold, ceiling, DPI, aspect ratio,
    # confidence cutoff and page cap are all numbers, and P5 holds none.
    for module in p5_modules():
        for name, value in constants(module).items():
            assert not isinstance(value, (int, float)) or isinstance(value, bool), (
                f"{module.__name__}.{name} = {value!r}")


def test_the_only_pattern_p5_owns_is_p4_d8s_mechanical_repair():
    found = [(module.__name__, name) for module in p5_modules()
             for name, value in constants(module).items()
             if isinstance(value, re.Pattern)]
    assert found == [MECHANICAL_REPAIR]


def test_no_screen_resolution_no_language_tag_and_no_producer_string():
    # SPEC Deferred: "Known screen resolutions", "OCR language configuration", and
    # the "Tool-generated producer/creator string list".
    for module_name, name, text in module_strings():
        assert not RESOLUTION.match(text), f"{module_name}.{name} = {text!r}"
        assert not LANGUAGE_TAG.match(text), f"{module_name}.{name} = {text!r}"
        assert "python-docx" not in text, f"{module_name}.{name}"
        assert "Mozilla" not in text, f"{module_name}.{name}"


def test_the_marker_classes_hold_no_members():
    # SPEC Deferred: §1.1's four repository markers are P3's and "Everything else"
    # is unsettled; the archive marker set likewise. P5 holds the CLASS names §2.4
    # and §2.5 spell, and no file name.
    from extractors.archive import MARKER_KINDS
    from extractors.structured_text import STRUCTURAL_MARKER_KINDS
    for value in (*MARKER_KINDS, *STRUCTURAL_MARKER_KINDS):
        assert "." not in value, value
        assert "/" not in value, value


def test_p5_hashes_no_file_bytes():
    # O5. `hashlib` is bound in NO P5 module. It used to be bound in exactly one,
    # `extractors.shape`, where it hashed a CONFIGURATION mapping — never a path,
    # never a byte. That import outlived its use: `fingerprint` delegates the whole
    # digest to P4's `config_fingerprint`, so P5 now computes no digest at all and
    # the invariant this test names holds more strongly, not less. The empty list is
    # the assertion; a hashing module reappearing in P5 is the thing to catch.
    binding = [module.__name__ for module in p5_modules()
               if getattr(constants(module).get("hashlib"), "__name__", "")
               == "hashlib"]
    assert binding == []
    from extractors.shape import fingerprint
    parameters = inspect.signature(fingerprint).parameters
    assert list(parameters) == ["config"]
    with pytest.raises((TypeError, AttributeError)):
        fingerprint(Path("/corpus/anything.pdf"))


def test_p5_determines_no_mime_type():
    # SPEC OQ4 and §2.9: the real MIME type or signature comes from an injected
    # reader; P5 owns the routing TABLE and not the detection.
    for module in p5_modules():
        for name, value in constants(module).items():
            assert getattr(value, "__name__", "") not in ("mimetypes", "magic"), name
    assert (inspect.signature(route).parameters["detect_format"].default
            is inspect.Parameter.empty)


def test_there_is_no_global_language_quality_check():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents." §2.7 repeats
    # it. The only input about a non-empty text layer is P6's verdict.
    for module in p5_modules():
        for name, value in constants(module).items():
            if not callable(value):
                continue
            for token in ("quality", "legible", "gibberish", "garbled",
                          "language_check", "readable_text"):
                assert token not in name.lower(), f"{module.__name__}.{name}"
    parameters = set(inspect.signature(text_layer_state).parameters)
    assert parameters == {"result", "file_id", "content_hash", "no_usable_facts"}


def test_p5_makes_no_model_call_and_writes_no_llm_tier():
    # I4 and §3.3. "P5 contains no model call of any kind."
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert P5_ANALYSIS_TIERS == ("filesystem", "native", "ocr")
    with pytest.raises(ForbiddenAnalysisTier):
        run(file_id="f", content_hash="h", extractor_name="x", extractor_version="1",
            source_type="image", analysis_tier="llm", config={},
            completeness="complete", coverage={"units": "files", "processed": 1,
                                               "total": 1},
            observation_count=0, started_at="t", finished_at="t")
    for module in p5_modules():
        for name, value in constants(module).items():
            if not callable(value):
                continue
            for token in ("llm", "model_", "_model", "embedding", "dossier"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_subsystem_is_set_in_exactly_one_module():
    # M8: the acting part authors and P1 writes. There is one place that value lives.
    holders = [module.__name__ for module in p5_modules()
               if constants(module).get("SUBSYSTEM") == SUBSYSTEM]
    assert holders == ["extractors.authorship"]


def test_p5_registers_no_event_type():
    # B5 rule 4: registration is a spec-level act, and both P5 types are already
    # reserved §8.2 names in P1's frozen table.
    assert set(AUTHORED_EVENT_TYPES) <= RESERVED_EVENT_TYPES


def test_p5_creates_none_of_p4s_three_tables(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    tables = {row["name"] for row in
              conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"extraction_routing", "extraction_sensitivity_signal"} <= tables
    assert not {"evidence", "extraction_runs", "text_units"} & tables


# --- one guard per open question --------------------------------------------

def test_oq1_the_no_usable_facts_threshold_is_not_answered_here():
    # OQ1: "§2.2 and §2.7 define the trigger in terms of facts and the design never
    # says how few facts is 'no usable facts'. It is a deferred configuration value."
    parameter = inspect.signature(document_ocr_decision).parameters["no_usable_facts"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    import extractors.ocr_policy as policy
    assert not [n for n, v in constants(policy).items()
                if isinstance(v, (int, float)) and not isinstance(v, bool)]


def test_oq2_the_formats_section_2_9_lists_twice_still_have_two_candidates():
    # OQ2: "CSV appears under both Spreadsheets and Code/structured data; PDF appears
    # under both Text documents and Presentations. The design specifies different
    # field lists for each and no tiebreak."
    assert len(SOURCE_TYPE_BY_FORMAT["csv"]) == 2
    assert len(SOURCE_TYPE_BY_FORMAT["pdf"]) == 2
    decision = route(file_id="f", content_hash="h", path=Path("/corpus/a.csv"),
                     extension=".csv", detect_format=lambda target: "csv")
    # The candidates are recorded rather than discarded, and the operative one is
    # §2.9's own document order — not a preference of P5's.
    assert decision.source_type_candidates == SOURCE_TYPE_BY_FORMAT["csv"]
    assert decision.source_type == SOURCE_TYPE_BY_FORMAT["csv"][0]


def test_oq3_is_closed_and_stays_closed():
    # I4, ratified 2026-08-19: the four tiers are closed and P5 writes the first
    # three. This guard exists so a later edit cannot quietly re-open it.
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    assert "llm" not in P5_ANALYSIS_TIERS


def test_oq4_every_library_and_engine_choice_is_a_required_keyword():
    # OQ4: "The design names Apple Vision for macOS OCR and names no library for PDF,
    # DOCX, HEIC, archives, spreadsheets, presentations, email, calendar, contacts,
    # audio/video, or design formats."
    required = {
        extract_pdf: ("read_pdf", "find_structured_strings"),
        extract_structured_text: ("read_text_document", "find_structured_strings"),
        extract_long_tail: ("read_long_tail", "find_structured_strings",
                            "transcription_authorized"),
        extract_archive: ("read_manifest", "recognize_markers"),
        extract_image: ("read_image", "dimension_signal", "filename_pattern"),
        extract_ocr: ("ocr_engine", "config", "find_structured_strings"),
    }
    for function, names in required.items():
        parameters = inspect.signature(function).parameters
        for name in names:
            assert parameters[name].default is inspect.Parameter.empty, name
            assert parameters[name].kind is inspect.Parameter.KEYWORD_ONLY, name


def test_oq5_spreadsheets_and_presentations_are_the_callers_release_decision(sink):
    # OQ5: "§2.4 explicitly permits either; §2.9 specifies full field lists for both.
    # Which is a release-scope decision the design leaves open."
    result = extract_long_tail(
        file_row={"file_id": "f", "content_hash": "h", "filename": "x.xlsx"},
        path=Path("/corpus/x.xlsx"),
        policy=__import__("extractors.safety", fromlist=["SafetyPolicy"]).SafetyPolicy(
            is_protected_container=lambda p: False, is_dataless=lambda p: False),
        source_type="spreadsheet", read_long_tail=lambda p, *, transcribe: None,
        find_structured_strings=lambda text: (),
        transcription_authorized=lambda: False, now="t", context_window=1)
    assert result.extraction.run["completeness"] == "unsupported"
    for module_name, name, text in module_strings():
        assert "launch" not in text.lower(), f"{module_name}.{name}"


def test_oq6_ratified_p5_holds_no_privacy_or_gating_vocabulary():
    # OQ6 CLOSED, ratified 2026-08-20: GATE by default, with an explicit
    # user-initiated delete. Both halves belong elsewhere — the gate is P7's handling
    # class, the delete surface is P13's — and "P5 publishes no deletion" is now a
    # ratified requirement rather than a question being held open. Same assertions,
    # stronger standing: P5 neither deletes (guarded in test_p5_reextraction.py)
    # nor gates.
    for module in p5_modules():
        for name in constants(module):
            for token in ("private", "gated", "gate_", "quarantine", "consent"):
                assert token not in name.lower(), f"{module.__name__}.{name}"


def test_oq7_there_is_one_sensitivity_value_and_no_handling_class():
    # OQ7: "§2.9 requires email addresses, message content and VCF output be treated
    # as potentially sensitive; §8.4 puts handling-class assignment in P7. The
    # boundary between 'P5 flags' and 'P7 classifies' is unstated."
    assert isinstance(POTENTIALLY_SENSITIVE, str)
    for module in p5_modules():
        for name in constants(module):
            for token in ("handling_class", "sensitivity_state", "classify",
                          "HANDLING"):
                assert token not in name, f"{module.__name__}.{name}"


def test_oq8_no_nested_manifest_is_read():
    # OQ8: "May a nested archive's manifest be read one level down, in memory? §2.5
    # lists nested archives among those marked unreadable or partially inspected, but
    # reading an inner manifest without unpacking is not the same act as extraction,
    # and the design does not distinguish them."
    fields = set(inspect.signature(ArchiveManifest).parameters)
    assert not {"nested", "inner", "nested_manifests", "children"} & fields
    readers = [name for name in inspect.signature(extract_archive).parameters
               if name.startswith("read_")]
    assert readers == ["read_manifest"]

"""The compiler turns ratified node rows into a versioned manifest.

`planning/domains/` is a research and authorship surface, not a runtime import
target (`src/facts/fields.py`, `src/tree_design/catalogue.py`). The compiler is
the ONE place allowed to read a node row, and what it emits is data, not code.
"""
from __future__ import annotations

import json

import pytest

from facts.domains import SCHEMA_IDS, UnknownSchema
from recognition.compile import compile_rules
from recognition.vocabulary import MANIFEST_VERSION


def row(**overrides):
    """A node row with every key the compiler reads, so a test states its delta."""
    base = {
        "id": "academic.coursework",
        "kind": "template",
        "schema_id": "academic",
        "launch": "full",
        "refuse_node": False,
        "proposed_context_terms": [],
        "work_types": [],
        "file_kinds": {"source_types": ["text_document"], "extensions": [".pdf"],
                       "never_alone": True},
        "recognition": {"deterministic": [], "needs_llm": [], "never_alone": []},
    }
    base.update(overrides)
    return base


# --- the closed vocabulary ---------------------------------------------------

def test_a_row_naming_a_schema_outside_SCHEMA_IDS_is_a_load_error():
    # `SCHEMA_IDS` is closed. A row naming a schema the product does not recognise
    # is refused rather than compiled into a rule nothing can ever activate.
    with pytest.raises(UnknownSchema):
        compile_rules([row(schema_id="astrology")])


def test_the_compiler_never_hard_codes_how_many_schemas_there_are():
    # `SCHEMA_IDS` is widening 10 -> 23 underneath this package. The manifest is
    # sized by the rows it was given, never by a count written here.
    compiled = compile_rules([row(schema_id=SCHEMA_IDS[0]),
                              row(id="other", schema_id=SCHEMA_IDS[-1])])
    assert set(compiled["schemas"]) == {SCHEMA_IDS[0], SCHEMA_IDS[-1]}


# --- what compiles, and what does not ----------------------------------------

def test_terms_are_normalised_deduplicated_and_ordered():
    compiled = compile_rules([
        row(proposed_context_terms=["  Problem Set ", "midterm", "problem set"]),
        row(id="academic.teaching", proposed_context_terms=["Midterm", "roster"]),
    ])
    assert compiled["schemas"]["academic"]["context_terms"] == [
        "midterm", "problem set", "roster"]


def test_context_terms_inside_recognition_merge_with_the_top_level_ones():
    # 15 rows carry `proposed_context_terms` inside `recognition` and 272 carry it
    # at the top level. Reading one place would silently drop the other.
    compiled = compile_rules([row(
        proposed_context_terms=["syllabus"],
        recognition={"deterministic": [], "needs_llm": [], "never_alone": [],
                     "proposed_context_terms": ["office hours"]})])
    assert compiled["schemas"]["academic"]["context_terms"] == [
        "office hours", "syllabus"]


def test_a_term_authored_in_both_roles_lands_in_exactly_one():
    # Two homes for one term would score it twice, and the arity rule counts
    # DISTINCT terms. The context role wins and the work-type copy is dropped.
    compiled = compile_rules([row(proposed_context_terms=["lecture"],
                                  work_types=["lecture", "essay"])])
    schema = compiled["schemas"]["academic"]
    assert schema["context_terms"] == ["lecture"]
    assert schema["work_type_terms"] == ["essay"]


def test_a_refused_row_contributes_no_terms_and_is_counted_never_omitted():
    # 44 of the 358 rows are `refuse_node: true`: the research decided the node does
    # not exist, and one of them says so in its own `never_alone` -- "STATED FOR THE
    # REFUSAL RECORD, NOT AS THIS ROW'S RECOGNITION". Compiling its terms would
    # resurrect a node the research killed. It is still named in the manifest.
    compiled = compile_rules([
        row(proposed_context_terms=["syllabus"], work_types=["lecture"]),
        row(id="academic.ghost", refuse_node=True,
            proposed_context_terms=["ghost term"], work_types=["ghost work"]),
    ])
    schema = compiled["schemas"]["academic"]
    assert schema["context_terms"] == ["syllabus"]
    assert schema["work_type_terms"] == ["lecture"]
    assert schema["refused_rows"] == ["academic.ghost"]
    assert schema["rows"] == ["academic.coursework"]
    assert compiled["refused_rows"] == 1


# --- the needs_llm hand-off ---------------------------------------------------

def test_needs_llm_readings_are_carried_verbatim_and_attributed_to_their_row():
    # These are NOT implemented here. They are the cases a deterministic rule
    # cannot settle, compiled as the stated reason the detector abstained so P8
    # can pick them up later.
    reading = "an unlabelled prose assignment whose only signal is register"
    compiled = compile_rules([row(
        recognition={"deterministic": [], "never_alone": [],
                     "needs_llm": [reading]})])
    assert compiled["schemas"]["academic"]["needs_llm"] == [
        {"row": "academic.coursework", "readings": [reading]}]


def test_never_alone_prose_is_counted_and_attributed_but_never_copied():
    # The never-alone DISCIPLINE is compiled into the arity rule the detector
    # applies: one matched term never activates a schema. Carrying the 3,245
    # sentences as well would be a second, non-executable home for a rule the
    # compiler already enforces -- this project's named defect.
    compiled = compile_rules([row(
        recognition={"deterministic": [], "needs_llm": [],
                     "never_alone": ["a bare 4-digit number",
                                     "a university name with no course context"]})])
    schema = compiled["schemas"]["academic"]
    assert schema["never_alone_rows"] == [
        {"row": "academic.coursework", "cautions": 2}]
    assert "a bare 4-digit number" not in json.dumps(compiled)


# --- file kinds ---------------------------------------------------------------

def test_file_kinds_union_and_carry_their_own_never_alone_flag():
    # All 358 rows set `file_kinds.never_alone: true`. Compiled as a flag rather
    # than assumed, so a row that ever sets it false becomes visible.
    compiled = compile_rules([
        row(file_kinds={"source_types": ["text_document"],
                        "extensions": [".pdf", ".DOCX"], "never_alone": True}),
        row(id="academic.teaching",
            file_kinds={"source_types": ["spreadsheet", "text_document"],
                        "extensions": [".xlsx"], "never_alone": True}),
    ])
    schema = compiled["schemas"]["academic"]
    assert schema["source_types"] == ["spreadsheet", "text_document"]
    assert schema["extensions"] == [".docx", ".pdf", ".xlsx"]
    assert schema["file_kind_never_alone"] is True


def test_a_row_that_turns_file_kind_never_alone_off_turns_it_off_for_the_schema():
    compiled = compile_rules([
        row(file_kinds={"source_types": ["text_document"], "extensions": [".pdf"],
                        "never_alone": True}),
        row(id="academic.teaching",
            file_kinds={"source_types": [], "extensions": [], "never_alone": False}),
    ])
    assert compiled["schemas"]["academic"]["file_kind_never_alone"] is False


# --- the manifest is a release --------------------------------------------------

def test_the_manifest_carries_its_version_and_what_it_was_compiled_from():
    compiled = compile_rules([row(), row(id="x", refuse_node=True)])
    assert compiled["manifest_version"] == MANIFEST_VERSION
    assert compiled["compiled_rows"] == 2
    assert compiled["refused_rows"] == 1


def test_compiling_the_same_rows_twice_produces_byte_identical_output():
    rows = [row(proposed_context_terms=["b", "a"]),
            row(id="z", schema_id=SCHEMA_IDS[-1], work_types=["q"])]
    assert json.dumps(compile_rules(rows), sort_keys=True) == json.dumps(
        compile_rules(list(reversed(rows))), sort_keys=True)

# tests/p6/test_p6_anchor_statements.py
"""`104` R-135 -- where an anchor document states a course's name, and what it costs.

Product constitution 1: *"LLM decides, code delivers. Never hardcode domain knowledge:
no alias tables, no equivalence maps, no sorting rules."* This module records WHERE a
line printed a course code. It never records what the course is called, and nothing here
turns one spelling into another. Site C's own text puts that judgement on the model:
"two spellings can be one thing ... yours to judge from the evidence".

Every deployment argument is `cli`'s, imported rather than restated. A test holding its
own pattern would be testing a rule `facts` does not have.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.anchor_statements import (
    anchor_statements_for, record_anchor_statements,
)

import cli

CLOCK = "2026-09-07T00:00:00Z"
SCAN = "scan-r135"

#: The owner's own syllabus heading, from `104` R-135. Both spellings, one line.
HEADING = "COMS W3134: Data Structures"

RECORD = dict(
    is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
    canonical=cli.SUBJECT_RULE.canonical,
    anchor_terms=cli.COURSE_ANCHOR_TERMS,
    reads_in_document=cli.reads_a_structured_string)


def _file(conn, tmp_path, name):
    body = name.encode()
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, file_id, content_hash, raw, zone="heading", span=None,
             before=None, after=None, ordinal=1):
    run_id = f"run-{file_id}"
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1), Segment("heading", ordinal)),
                          text_span=span),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=before, context_after=after)
    record_observation(conn, observation)
    return observation


def _syllabus(conn, tmp_path, *, name="syllabus.pdf", heading=HEADING, code="W3134"):
    """One anchor document: the heading, and the identifier P4 found inside it.

    Both readings share a container path, which is how `extractors/pdf.py` emits them
    and is the only relationship this module reads.
    """
    file_id, content_hash = _file(conn, tmp_path, name)
    start = heading.index(code)
    line = _observe(conn, file_id=file_id, content_hash=content_hash, raw=heading,
                    span=TextSpan(0, len(heading)),
                    before="Syllabus\n", after="\nInstructor: Dr Lacker")
    identifier = _observe(
        conn, file_id=file_id, content_hash=content_hash, raw=code,
        span=TextSpan(start, start + len(code)),
        before=f"Syllabus\n{heading[:start]}", after=heading[start + len(code):])
    return (file_id, content_hash), line, identifier


def test_an_anchor_line_is_recorded_as_a_citation_and_not_as_its_words(
        p6_conn, tmp_path):
    """The row's mechanism, and the constitution's line, in one assertion.

    The stored row names the anchor file, its content hash, the code, and TWO
    observation keys. It contains no title, no name and no pairing: what the line says
    stays in the document, and a model reads it from there.
    """
    version, line, identifier = _syllabus(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert len(statements) == 1
    one = statements[0]
    assert one.stating_file_id == version[0]
    assert one.canonical_code == "W3134"
    assert one.code_evidence_ref == identifier.observation_key
    # The containing reading, found by span inside one container path -- no parsing,
    # no separator, no title shape. This is the reading whose words are the whole line.
    assert one.line_evidence_ref == line.observation_key

    columns = {row[1] for row in p6_conn.execute(
        "PRAGMA table_info(anchor_statements)")}
    assert "title" not in columns and "alias" not in columns
    stored = p6_conn.execute(
        "SELECT * FROM anchor_statements").fetchone()
    assert "Data Structures" not in json.dumps([*stored])


def test_two_anchors_naming_one_course_are_both_kept(p6_conn, tmp_path):
    """Nothing is chosen by code, and nothing is dropped by sort order.

    An earlier draft of this row resolved a title to a code and, when two anchors
    disagreed, let `ORDER BY canonical_code` pick. That is the sorting rule the
    constitution forbids. Both statements are returned; which course a file belongs to
    is the model's judgement on the evidence, and here the evidence is two documents.
    """
    first, _, first_id = _syllabus(p6_conn, tmp_path, name="one.pdf")
    second, _, second_id = _syllabus(
        p6_conn, tmp_path, name="two.pdf",
        heading="ENGI E1006: Data Structures", code="E1006")
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[first, second], **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert {one.canonical_code for one in statements} == {"W3134", "E1006"}
    assert {one.code_evidence_ref for one in statements} == {
        first_id.observation_key, second_id.observation_key}


@pytest.mark.parametrize("zone", ["filename", "path", "title"])
def test_a_name_never_yields_an_anchor_statement(p6_conn, tmp_path, zone):
    """A folder called `Data Structures` is what the product is EXPLAINING.

    The gate is `cli.reads_a_structured_string` -- a span inside `body` or `heading` --
    so these three zones are outside it by construction rather than by a second list.
    The same reading, with the same anchor words around it, records nothing.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, "W3134.pdf")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             zone=zone, span=TextSpan(0, 5), before="Syllabus\n",
             after=": Data Structures")
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    assert anchor_statements_for(p6_conn, SCAN) == ()


def test_a_document_that_only_mentions_a_course_states_nothing(p6_conn, tmp_path):
    """A problem set prints the code too. It does not say what the course is called."""
    file_id, content_hash = _file(p6_conn, tmp_path, "hw3.pdf")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             span=TextSpan(0, 5), before="Problem Set 4\n", after=" due Friday")
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    assert anchor_statements_for(p6_conn, SCAN) == ()


@pytest.mark.parametrize("heading,code", [
    ("General Chemistry I 1403: Sample Exam 1", "I 1403"),
    ("SPRING 2026: Data Structures", "SPRING 2026"),
])
def test_a_reading_the_subject_rule_refuses_states_nothing(p6_conn, tmp_path,
                                                           heading, code):
    """The asserting knob, not the seeing one.

    `_STRUCTURED` matches both of these because it is what the product SEES;
    `SUBJECT_RULE.pattern` refuses both, because it is what the product ASSERTS. `I 1403`
    is `General Chemistry I` glued to a number -- the reading that filed three of the
    owner's chemistry exams under a course called `I1403` -- and `SPRING 2026` is a term.
    """
    version, _line, _identifier = _syllabus(p6_conn, tmp_path, heading=heading,
                                            code=code)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    assert anchor_statements_for(p6_conn, SCAN) == ()


def test_this_module_holds_no_name_to_code_mapping(p6_conn):
    """The constitution's first rule, asserted against this change's own CODE.

    An AST walk and never a text search, which is the lesson
    `tests/p6/test_p6_no_invention.py` states in its own preamble: prose reaches a
    source search and means nothing, and the first draft of this test failed on the
    word "equivalence" inside the docstring that QUOTES the rule. What is checked here
    is what the module defines and what it names -- a mapping would have to be one of
    those.

    Scoped to this row's module, deliberately. A grep over all of `src/` fails on
    legitimate pre-existing uses -- the `values.aliases` column, `merge_values`'
    taxonomy aliases -- so the guard that means something is the narrow one.
    """
    import ast
    import inspect

    from facts import anchor_statements

    tree = ast.parse(inspect.getsource(anchor_statements))
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    attributes = {node.attr for node in ast.walk(tree)
                  if isinstance(node, ast.Attribute)}
    fields = {node.target.id for node in ast.walk(tree)
              if isinstance(node, ast.AnnAssign)
              and isinstance(node.target, ast.Name)}
    vocabulary = defined | names | attributes | fields

    # Nothing that answers "which code is this name", and no field that pairs the two.
    for forbidden in ("resolve", "codes_by_title", "code_by_spelling",
                      "canonical_spelling", "CourseAliases", "resolve_subject_facts",
                      "alias_text", "title"):
        assert forbidden not in vocabulary, forbidden

    # And the table has no column that could hold the pairing.
    columns = {row[1] for row in p6_conn.execute(
        "PRAGMA table_info(anchor_statements)")}
    assert columns == {"statement_id", "scan_run_id", "stating_file_id",
                       "stating_content_hash", "canonical_code",
                       "code_evidence_ref", "line_evidence_ref"}

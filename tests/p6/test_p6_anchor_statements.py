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

from extractors.long_tail import SENSITIVITY_DDL

import cli

CLOCK = "2026-09-07T00:00:00Z"
SCAN = "scan-r135"

#: The owner's own syllabus heading, from `104` R-135. Both spellings, one line.
HEADING = "COMS W3134: Data Structures"

RECORD = dict(
    is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
    canonical=cli.SUBJECT_RULE.canonical,
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
    This is the refusal that did NOT move when the anchor-word gate was removed, and it
    is the one that matters: with any in-document code line now a statement, the wall
    between a document's words and its NAME is the whole of what keeps a folder called
    `Data Structures` from becoming the evidence for what `Data Structures` means.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, "W3134.pdf")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             zone=zone, span=TextSpan(0, 5), before="Syllabus\n",
             after=": Data Structures")
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    assert anchor_statements_for(p6_conn, SCAN) == ()


def test_a_body_line_that_prints_a_code_is_a_statement(p6_conn, tmp_path):
    """THIS TEST FLIPPED, and the measurement is why.

    It asserted the opposite: a problem set prints the code but does not say what the
    course is CALLED, so an anchor word -- `syllabus`, `registrar`, `enrolled in` -- had
    to appear beside the code. Run against the owner's corpus that gate refused all 106
    readings that pass `is_code`. Three files in the whole corpus mention any of those
    words anywhere in their text and none of them prints a code, so the table held zero
    rows and no dossier ever carried context. The document the rule described is not in
    this corpus; 44 files that print a code in their own text are.

    A gate that refuses 106 of 106 is code deciding, badly, the question the
    constitution gives the model -- site C's own sentence is "two spellings can be one
    thing ... yours to judge". So every line of a document's own text that prints a code
    is a statement, this one included, and no anchor word appears anywhere near it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, "hw3.pdf")
    identifier = _observe(
        p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
        zone="body", span=TextSpan(0, 5), before="Problem Set 4\n",
        after=" due Friday")
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert [one.canonical_code for one in statements] == ["W3134"]
    assert statements[0].code_evidence_ref == identifier.observation_key


def test_two_code_lines_in_one_document_are_two_statements(p6_conn, tmp_path):
    """One document, two courses, two rows, and no preference between them.

    A transcript or a schedule prints several codes, and with the anchor-word gate gone
    it is an ordinary case rather than a corner. Nothing here chooses: `canonical_code`
    orders the read for §8.5's replay and is not a ranking, and which of the two a given
    file belongs to is the model's judgement at sites A and C.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, "schedule.pdf")
    first = _observe(p6_conn, file_id=file_id, content_hash=content_hash,
                     raw="W3134", zone="body", span=TextSpan(0, 5),
                     before="Autumn\n", after=" 10:10am", ordinal=1)
    second = _observe(p6_conn, file_id=file_id, content_hash=content_hash,
                      raw="E1006", zone="body", span=TextSpan(0, 5),
                      before="Autumn\n", after=" 1:10pm", ordinal=2)
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert {one.canonical_code for one in statements} == {"W3134", "E1006"}
    assert {one.code_evidence_ref for one in statements} == {
        first.observation_key, second.observation_key}
    assert {one.stating_file_id for one in statements} == {file_id}


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


# ----------------------------------------------------------------------------
# The LINE, when the document carries no reading that is one
# ----------------------------------------------------------------------------

BODY = "Autumn term\nCOMS W3134 Data Structures\nMeets Tuesdays at 10:10\n"

#: Where the code sits inside it, stated by the fixture rather than parsed, for
#: `_syllabus`' reason: this file measures the MINTING and must not contain a second
#: implementation of the reading.
BODY_CODE_START = BODY.index("W3134")
BODY_LINE = "COMS W3134 Data Structures"


def _text_document(conn, tmp_path, *, text=BODY, name="notes.txt", unit=True,
                   code="W3134"):
    """A `.txt` as the product actually reads one: ONE body unit, and inside it a
    span-less whole-document reading beside the span the structured-string pass found.

    That is the shape `104` R-135's second measurement is about. `extractors/pdf.py`
    gives a heading its own unit and its own reading, so a PDF heading has a containing
    reading to cite; a `.txt` body has one reading with no span, and a span-less sibling
    is exactly what `_containing_span_reading` skips.

    `code` is the reading the structured-string pass found, stated by the caller for
    the reason `BODY_CODE_START` is: this file measures the MINTING and must not hold
    a second implementation of the recogniser. `104` R-146 added the second caller.
    """
    from evidence_shape.store import record_text_unit
    from evidence_shape.text_units import TextUnit

    file_id, content_hash = _file(conn, tmp_path, name)
    run_id = f"run-{file_id}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="text.structured", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    if unit:
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=(), text=text))

    def observe(raw, span):
        observation = Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="1.0.0",
            source_type="text_document", raw_value=raw,
            location=Location("body", (), text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        return observation

    whole = observe(text, None)
    start = text.index(code)
    reading = observe(code, TextSpan(start, start + len(code)))
    return (file_id, content_hash), whole, reading


def test_a_body_code_gets_its_line_minted_as_a_reading_of_its_own(p6_conn, tmp_path):
    """`104` R-135's second measurement, and the whole path turned on it.

    On the owner's corpus: `anchor_statements` held 99 rows and the citation shapes were
    `code: body span` 91 / `line: none` 91 against `code: heading span` 8 /
    `line: heading span` 8. So 91 statements of 99 carried no line, the context path
    passed over every one, and the first 18 fresh `A_fact` dossiers of a live run
    carried 125 released items with not one context item among them.

    The line is now MINTED: a span reading of the code's own unit, from the newline
    before to the newline after, recorded through the same store the extractors use and
    carrying its own extractor name so nothing reads it as something a document
    extractor found. The code's own reading is untouched.
    """
    from evidence_shape.store import get_observation
    from facts.anchor_statements import LINE_EXTRACTOR

    version, whole, code = _text_document(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert len(statements) == 1
    one = statements[0]
    assert one.code_evidence_ref == code.observation_key
    assert one.line_evidence_ref is not None
    assert one.line_evidence_ref not in (code.observation_key,
                                         whole.observation_key)

    row = p6_conn.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (one.line_evidence_ref,)).fetchone()
    minted = get_observation(p6_conn, row["observation_id"])
    assert minted.raw_value == BODY_LINE
    assert minted.location.text_span.start == BODY.index(BODY_LINE)
    assert minted.location.text_span.end == BODY.index(BODY_LINE) + len(BODY_LINE)
    assert minted.location.zone == "body"
    # Its provenance is this producer's and not the document extractor's, so a reader
    # can always tell a minted line from one a pass over the bytes found.
    assert minted.extractor_name == LINE_EXTRACTOR
    assert minted.run_id == code.run_id
    # And the code's own reading is exactly as it was.
    assert get_observation(p6_conn, p6_conn.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (code.observation_key,)).fetchone()["observation_id"]).raw_value == "W3134"


def test_minting_twice_writes_one_reading(p6_conn, tmp_path):
    """A re-scan cites the row it wrote last time. The handle is content-addressed, so
    a second insert would be the same reading twice under two ids, and §8.5 replays a
    run and compares it."""
    from facts.anchor_statements import LINE_EXTRACTOR

    version, _whole, _code = _text_document(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)
    first = anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    assert anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref == first
    assert p6_conn.execute(
        "SELECT count(*) FROM evidence WHERE extractor_name = ?",
        (LINE_EXTRACTOR,)).fetchone()[0] == 1


def test_a_heading_document_still_cites_the_heading_and_mints_nothing(
        p6_conn, tmp_path):
    """A reading the document already carries always wins. `extractors/pdf.py` wrote
    the heading; minting a second reading of the same characters would put an invented
    row beside a real one for no gain."""
    from facts.anchor_statements import LINE_EXTRACTOR

    version, line, _identifier = _syllabus(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    assert anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref == (
        line.observation_key)
    assert p6_conn.execute(
        "SELECT count(*) FROM evidence WHERE extractor_name = ?",
        (LINE_EXTRACTOR,)).fetchone()[0] == 0


@pytest.mark.parametrize("zone", ["filename", "path", "title"])
def test_a_name_never_gets_a_line_minted_over_it(p6_conn, tmp_path, zone):
    """§8.4's members 1 and 6, and the constraint the ruling names first.

    The in-document rule runs BEFORE any of this, so a name never becomes a statement
    and so never reaches the minting at all. Asserted on the evidence table rather than
    on the return value, because what would be wrong here is a ROW: a minted reading
    over a filename would be a path-derived reading wearing a body reading's shape, and
    every release rule downstream reads the zone off exactly that row.
    """
    from facts.anchor_statements import LINE_EXTRACTOR

    file_id, content_hash = _file(p6_conn, tmp_path, "W3134.pdf")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             zone=zone, span=TextSpan(0, 5))
    record_anchor_statements(p6_conn, scan_run_id=SCAN,
                             file_versions=[(file_id, content_hash)], **RECORD)

    assert anchor_statements_for(p6_conn, SCAN) == ()
    assert p6_conn.execute(
        "SELECT count(*) FROM evidence WHERE extractor_name = ?",
        (LINE_EXTRACTOR,)).fetchone()[0] == 0


def test_a_code_with_no_stored_unit_keeps_no_line(p6_conn, tmp_path):
    """The first of the two refusals, and it is why the caller has a fallback.

    Without the unit's stored text there is nothing to read the line back FROM, and a
    minted reading whose characters are not the stored characters fails
    `check_span_anchor` at the door -- after a release has been minted. So the statement
    keeps `line=None`, and `cli.anchor_context_observations` offers the code's own span
    instead of passing the file over.
    """
    version, _whole, code = _text_document(p6_conn, tmp_path, unit=False)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert [one.code_evidence_ref for one in statements] == [code.observation_key]
    assert statements[0].line_evidence_ref is None


def test_a_line_that_is_only_the_code_mints_nothing(p6_conn, tmp_path):
    """The second refusal. The reading would carry the characters the code already
    carries and differ only in its handle, which is noise; the caller's fallback offers
    the code, and that is the same text by a shorter route."""
    version, _whole, code = _text_document(
        p6_conn, tmp_path, text="Autumn term\nW3134\nMeets Tuesdays\n")
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert [one.code_evidence_ref for one in statements] == [code.observation_key]
    assert statements[0].line_evidence_ref is None


def test_a_minted_line_is_derived_and_the_rule_pass_skips_it(p6_conn, tmp_path):
    """`104` R-135's ruling: a copy is not a second thing the file says about itself.

    Measured on the chain. `starter.py`'s docstring prints `BUSIB 4300 Homework 2
    starter`; the minted line's context then carried `Homework`, §3.5's rule pass read
    the copy as a second reading, a validated course fact appeared, and a file the
    premise of `test_p15_a_promised_gesture_is_offered` says nothing reaches was placed.

    The predicate is P4's and reads a NAMESPACE rather than a list, so the rule pass and
    the recogniser cannot disagree about what a copy is and a producer written later
    opts in by naming itself.
    """
    from evidence_shape.store import DERIVED_NAMESPACE, get_observation, is_derived
    from facts.file_facts import facts_for_file
    from facts.discount import MetadataScreen
    from facts.rules import Rule, apply_rules

    version, _whole, _code = _text_document(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)
    ref = anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref
    minted = get_observation(p6_conn, p6_conn.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (ref,)).fetchone()["observation_id"])

    assert minted.extractor_name.startswith(DERIVED_NAMESPACE)
    assert is_derived(minted) is True

    # The rule pass reads this file's readings and never the copy. `Data Structures` is
    # in the minted line and in no primary reading with a rule-matching shape, so a
    # fact resting on it is a fact the copy created.
    written = apply_rules(
        p6_conn, file_id=version[0], content_hash=version[1],
        rules=(Rule(pattern=cli.SUBJECT_RULE.pattern,
                    required_context_terms=("structures",),
                    field_key="subject",
                    canonical=cli.SUBJECT_RULE.canonical),),
        screen=MetadataScreen())
    cited = "".join(row["evidence_refs"] or ""
                    for row in facts_for_file(p6_conn, version[0], version[1]))

    assert ref not in cited, written


def test_a_derived_reading_is_still_citable_and_still_releasable(p6_conn, tmp_path):
    """The half that must NOT move, and it is the whole reason the reading exists.

    Skipping a copy as EVIDENCE ABOUT THE FILE is not withdrawing it. It stays live, it
    stays the citation `anchor_statements` recorded, and `model_facts` still offers it
    -- site A releases it as the file's own text, because it IS the file's own text,
    and `104` R-135's context path carries it to a neighbour. A fix that made the
    reading unreachable would have closed the row it was written for.
    """
    from model_facts import releasable_readings

    version, _whole, _code = _text_document(p6_conn, tmp_path)
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)
    ref = anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref

    p6_conn.executescript(SENSITIVITY_DDL)
    offered = releasable_readings(
        p6_conn, file_id=version[0], content_hash=version[1], keys=[ref])

    assert [one.observation_key for one in offered] == [ref]
    assert offered[0].raw_value == BODY_LINE


# ----------------------------------------------------------------------------
# `104` R-146: a course this pass could not see at all
# ----------------------------------------------------------------------------

#: A syllabus that prints its course as a capitalised word and four digits, beside
#: `Instructor:` -- the shape `104` R-146 measured on the owner's disk, where the 18
#: labelled files of one course have their code stated this way and NO anchor
#: statement carried it. Read with the uppercase-only recogniser that shipped until
#: 2026-09-08, `find_structured_strings` returned NOTHING for this text, so there was
#: no code reading, so `record_anchor_statements` had nothing to record and the
#: neighbours in the folder were offered no statement of what their course is called.
WORD_BODY = ("Spring 2026\nPhysics 1401 Introductory Mechanics\n"
             "Instructor: Dr. Lee. Credits: 3.\n")
WORD_LINE = "Physics 1401 Introductory Mechanics"


def test_the_recogniser_is_what_makes_this_document_statable_at_all():
    """The premise of the test below, asserted rather than assumed.

    This file's own rule is that it holds no second implementation of the reading;
    the corollary is that when the reading changes, the fixture must be re-measured
    against the shipped recogniser and not adjusted until it passes. Two readings
    come out of this body: the term, which `_TERM` claims first, and the course.
    """
    found = [WORD_BODY[one.start:one.end]
             for one in cli.find_structured_strings(WORD_BODY)]

    assert found == ["Spring 2026", "Physics 1401"]
    # And only the second of them is something the rule will call a course.
    assert cli.SUBJECT_RULE.pattern.search("Physics 1401") is not None
    assert cli.SUBJECT_RULE.pattern.search("Spring 2026") is None


def test_a_course_printed_as_a_word_states_its_folder_like_any_other(p6_conn,
                                                                    tmp_path):
    """`104` R-146 at the anchor pass, which is where its cost was measured.

    R-146's finding was not that a `subject` was wrong -- it was that of 43 labelled
    files, the label's subject is stated by a recognised anchor in the file's own
    folder family for NONE of them, and that the model then copied the only anchor
    that shared the digits (a one-letter identifier naming something else) onto 9 of
    its 19 `subject` answers. A document nothing can read states nothing.

    Nothing in `facts.anchor_statements` changed for this to work. The row is the
    same row: the stating file, its hash, the canonical code, and two citations --
    no title, no name, no pairing. What the line SAYS stays in the document and the
    model reads it from there.
    """
    version, whole, code = _text_document(
        p6_conn, tmp_path, text=WORD_BODY, name="physics syllabus.txt",
        code="Physics 1401")
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    statements = anchor_statements_for(p6_conn, SCAN)
    assert len(statements) == 1
    one = statements[0]
    assert one.stating_file_id == version[0]
    # `104` R-147 owns the spelling and it is not decided here: the canonical value
    # is what `SUBJECT_RULE.canonical` does with what the document printed.
    assert one.canonical_code == "Physics 1401"
    assert one.code_evidence_ref == code.observation_key
    assert one.line_evidence_ref not in (None, whole.observation_key)


def test_the_minted_line_is_the_documents_own_sentence_about_the_course(p6_conn,
                                                                       tmp_path):
    """And the line a neighbour is offered is the one a person would point at.

    The minting is `104` R-135's and is untouched: the code's own unit, from the
    newline before to the newline after. What R-146 changed is that there is now a
    code here to mint a line around.
    """
    from evidence_shape.store import get_observation
    from facts.anchor_statements import LINE_EXTRACTOR

    version, _whole, _code = _text_document(
        p6_conn, tmp_path, text=WORD_BODY, name="physics syllabus.txt",
        code="Physics 1401")
    record_anchor_statements(p6_conn, scan_run_id=SCAN, file_versions=[version],
                             **RECORD)

    ref = anchor_statements_for(p6_conn, SCAN)[0].line_evidence_ref
    row = p6_conn.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?",
        (ref,)).fetchone()
    minted = get_observation(p6_conn, row["observation_id"])

    assert minted.raw_value == WORD_LINE
    assert minted.extractor_name == LINE_EXTRACTOR
    assert minted.location.zone == "body"

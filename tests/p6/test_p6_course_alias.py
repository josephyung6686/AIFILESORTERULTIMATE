# tests/p6/test_p6_course_alias.py
"""`104` R-135 -- the course alias table, and a title resolved into the code it names.

The corpus these tests build is the one the row describes: a syllabus whose heading
states `COMS W3134: Data Structures`, and coursework files whose only words are
`Data Structures`. The measured defect is that the second kind of file recorded the
TITLE, or nothing at all, where the label expects the code.

Every deployment argument is `cli`'s, imported rather than restated. `facts.course_alias`
holds no pattern, no term, no separator and no bound of its own, and a test that spelled
one here would be testing a rule this package does not have.
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

from facts.course_alias import (
    AMBIGUOUS, BARE_WORD, CODE_SPELLING, NAMED, TITLE_ALIAS, UNKNOWN,
    build_course_aliases, load_course_aliases, resolve_subject_facts,
)
from facts.file_facts import facts_for_file
from facts.unresolved import NORMALIZATION_FAILED, unresolved_for_file
from facts.values import values_in_field

import cli

CLOCK = "2026-09-07T00:00:00Z"
SCAN = "scan-r135"

#: The deployment's, every one of them. `_STRUCTURED` and `_subject_title_shape` are
#: private to `cli` and are reached through the module rather than copied: the whole
#: claim of this change is that the alias table and the two normalisers agree about what
#: a code and a title are, and a test holding its own copy could not detect them
#: disagreeing.
BUILD = dict(code_pattern=cli._STRUCTURED, canonical=cli.SUBJECT_RULE.canonical,
             is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
             anchor_terms=cli.COURSE_ANCHOR_TERMS,
             separators=cli.COURSE_TITLE_SEPARATORS,
             department_prefix=cli._DEPARTMENT_PREFIX,
             title_of=cli._subject_title_shape,
             reads_in_document=cli.reads_a_structured_string)

RESOLVE = dict(field_key=cli.SUBJECT_FIELD, naming_zones=cli.NAMING_ZONES,
               title_of=cli._subject_title_shape)


def _file(conn, tmp_path, *, name, body):
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


def _observe(conn, *, file_id, content_hash, raw, zone="heading",
             before=None, after=None, span=True, run_id=None):
    run_id = run_id or f"run-{file_id}"
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    location = Location(zone, (Segment("page", 1),),
                        text_span=TextSpan(0, len(raw)) if span else None)
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=location, occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id=run_id, context_before=before,
        context_after=after)
    record_observation(conn, observation)
    return observation


def _syllabus(conn, tmp_path, *, name="COMS W3134 syllabus.pdf", code="W3134",
              before="Syllabus\nCOMS ", after=": Data Structures\nInstructor: Dr Lacker"):
    file_id, content_hash = _file(conn, tmp_path, name=name, body=name.encode())
    observation = _observe(conn, file_id=file_id, content_hash=content_hash, raw=code,
                           before=before, after=after)
    return (file_id, content_hash), observation


def _coursework(conn, tmp_path, *, name="Data Structures.pdf", title="Data Structures",
                zone="filename"):
    file_id, content_hash = _file(conn, tmp_path, name=name, body=name.encode())
    _observe(conn, file_id=file_id, content_hash=content_hash, raw=title, zone=zone,
             span=False)
    return file_id, content_hash


def _aliases(conn):
    return load_course_aliases(conn, SCAN)


def _subjects(conn, file_id, content_hash):
    return [(row["canonical_value"], row["reliability_state"], row["origin"])
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == cli.SUBJECT_FIELD and row["active"]]


# --- building ---------------------------------------------------------------------

def test_an_anchor_line_states_the_alias_and_the_row_cites_the_line(p6_conn, tmp_path):
    """The whole mechanism in one assertion: the syllabus said it, and the row proves it.

    `104` R-135: "stored in the database as facts with their evidence refs, never
    invented". The evidence ref is M14's observation key -- content-addressed, so it
    still resolves after an extractor upgrade -- and it is the key of the reading that
    carried the code, which is the same handle any fact built on this alias will cite.
    """
    version, observation = _syllabus(p6_conn, tmp_path)
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)

    rows = p6_conn.execute(
        "SELECT canonical_code, alias_text, alias_kind, evidence_ref, anchor_file_id "
        "FROM course_aliases ORDER BY alias_kind, alias_text").fetchall()
    assert [(row["canonical_code"], row["alias_text"], row["alias_kind"])
            for row in rows] == [
        ("W3134", "COMS W3134", CODE_SPELLING),
        ("W3134", "W3134", CODE_SPELLING),
        ("W3134", "Data Structures", TITLE_ALIAS)]
    assert {row["evidence_ref"] for row in rows} == {observation.observation_key}
    assert {row["anchor_file_id"] for row in rows} == {version[0]}


def test_the_two_spellings_the_anchor_states_together_are_one_course(p6_conn, tmp_path):
    """`104` R-91, closed at its source: `COMS W3134` and `W3134` are not two courses.

    The department prefix reaches P6 only in `context_before` -- `_STRUCTURED` claims
    `W3134` and `COMS` is not in the value -- so the rule's canonicaliser cannot see it
    and `65` §4.2's one-identity-two-spellings failure had no other place to be closed.
    """
    version, _ = _syllabus(p6_conn, tmp_path)
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)
    aliases = _aliases(p6_conn)

    assert aliases.canonical_spelling("COMS W3134") == "W3134"
    assert aliases.resolve("COMS W3134").outcome == NAMED
    assert aliases.resolve("COMS W3134").code == "W3134"
    assert cli.normalize_for_model("subject", "COMS W3134", aliases=aliases) == "W3134"


def test_an_alias_is_never_built_from_a_filename(p6_conn, tmp_path):
    """A folder called `Data Structures` is what the product is EXPLAINING.

    The predicate is `cli.reads_a_structured_string` -- a span inside `body` or
    `heading` -- so `filename`, `path`, `title` and every `metadata:*` zone are outside
    it by construction and not by a second list. The same words, in the same shape, with
    the same anchor context, build nothing.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="W3134.pdf", body=b"x")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             zone="filename", before="Syllabus\nCOMS ", after=": Data Structures",
             span=False)
    build_course_aliases(p6_conn, scan_run_id=SCAN,
                         file_versions=[(file_id, content_hash)], **BUILD)

    assert p6_conn.execute("SELECT count(*) FROM course_aliases").fetchone()[0] == 0


def test_a_line_that_is_not_an_anchor_document_builds_nothing(p6_conn, tmp_path):
    """A homework sheet MENTIONS a course; it does not state what the course is called.

    `COURSE_ANCHOR_TERMS` is a strict subset of `SUBJECT_CONTEXT_TERMS`, and this is the
    narrowing doing its job: the same shape of line, in a document that prints
    `problem set` instead of `syllabus`, defines nothing for the rest of the corpus.
    """
    version, _ = _syllabus(p6_conn, tmp_path, before="Problem Set 4\nCOMS ")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)

    assert p6_conn.execute("SELECT count(*) FROM course_aliases").fetchone()[0] == 0


def test_running_words_between_the_code_and_the_colon_build_nothing(p6_conn, tmp_path):
    """`W3134 Problem Set 4: Chapter 2` is a heading, not a course naming itself."""
    version, _ = _syllabus(p6_conn, tmp_path,
                           after=" Problem Set 4: Chapter 2\nsyllabus")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)

    assert p6_conn.execute("SELECT count(*) FROM course_aliases").fetchone()[0] == 0


# --- resolving --------------------------------------------------------------------

def test_a_file_named_by_the_title_gets_the_code_and_keeps_the_title(p6_conn, tmp_path):
    """The row's own worked example, end to end.

    The subject is the CODE, `validated`, citing two observations -- the file's own
    reading and the anchor line that supplied the code. The title survives as a raw
    variant on the value, because §2.8 says "the raw observation remains exactly that
    wording" and the canonical value is a code this document never printed.
    """
    anchor, observation = _syllabus(p6_conn, tmp_path)
    file_id, content_hash = _coursework(p6_conn, tmp_path)
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[anchor], **BUILD)
    written = resolve_subject_facts(
        p6_conn, _aliases(p6_conn), file_versions=[(file_id, content_hash)], **RESOLVE)

    assert len(written) == 1
    assert _subjects(p6_conn, file_id, content_hash) == [("W3134", "validated", "rule")]
    fact = [row for row in facts_for_file(p6_conn, file_id, content_hash)
            if row["field_key"] == cli.SUBJECT_FIELD][0]
    assert observation.observation_key in json.loads(fact["evidence_refs"])
    value = [row for row in values_in_field(p6_conn, cli.SUBJECT_FIELD)
             if row["canonical_value"] == "W3134"][0]
    assert "Data Structures" in json.loads(value["raw_variants"])


def test_a_title_with_no_anchor_stays_on_the_review_path_and_writes_no_subject(
        p6_conn, tmp_path):
    """R-98 is unchanged for a course this corpus cannot explain.

    Two halves, and both matter. The corpus pass writes NOTHING -- a producer that
    cannot name the course does not guess one -- and `normalize_for_review` still
    returns the title, so the person is still asked. What R-135 removes is the third
    option the run actually took: recording the title as the subject.
    """
    file_id, content_hash = _coursework(p6_conn, tmp_path,
                                        name="Rotational Dynamics.pdf",
                                        title="Rotational Dynamics")
    aliases = _aliases(p6_conn)
    written = resolve_subject_facts(
        p6_conn, aliases, file_versions=[(file_id, content_hash)], **RESOLVE)

    assert written == ()
    assert _subjects(p6_conn, file_id, content_hash) == []
    assert aliases.resolve("Rotational Dynamics").outcome == UNKNOWN
    assert cli.normalize_for_review(
        "subject", "Rotational Dynamics", aliases=aliases) == "Rotational Dynamics"
    assert cli.normalize_for_model(
        "subject", "Rotational Dynamics", aliases=aliases) is None


def test_two_courses_sharing_one_title_are_refused_and_the_refusal_names_both(
        p6_conn, tmp_path):
    """A name two courses answer to names neither, and the row cites both anchors.

    The reason is a SENTENCE on the `SubjectReading` and the `unresolved` row carries
    `NORMALIZATION_FAILED` -- §3.6 check 3's own reason. No fourteenth reason word is
    minted: what NAMES the two courses is the pair of evidence refs, which resolve to
    the two syllabus lines that disagreed.
    """
    first, first_observation = _syllabus(p6_conn, tmp_path,
                                         name="one.pdf", code="W3134")
    second, second_observation = _syllabus(
        p6_conn, tmp_path, name="two.pdf", code="E1006", before="Syllabus\nENGI ")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[first, second],
                         **BUILD)
    aliases = _aliases(p6_conn)

    reading = aliases.resolve("Data Structures")
    assert reading.outcome == AMBIGUOUS
    assert reading.code is None
    assert "W3134" in reading.reason and "E1006" in reading.reason
    assert set(reading.evidence_refs) == {first_observation.observation_key,
                                          second_observation.observation_key}
    assert cli.normalize_for_model("subject", "Data Structures", aliases=aliases) is None
    assert cli.normalize_for_review("subject", "Data Structures",
                                    aliases=aliases) is None

    file_id, content_hash = _coursework(p6_conn, tmp_path, name="hw.pdf")
    assert resolve_subject_facts(p6_conn, aliases,
                                 file_versions=[(file_id, content_hash)],
                                 **RESOLVE) == ()
    rows = [row for row in unresolved_for_file(p6_conn, file_id, content_hash)
            if row["field_key"] == cli.SUBJECT_FIELD]
    assert [row["reason"] for row in rows] == [NORMALIZATION_FAILED]
    assert set(json.loads(rows[0]["evidence_refs"])) == {
        first_observation.observation_key, second_observation.observation_key}


@pytest.mark.parametrize("word", ["Physics", "Economics", "Chemistry"])
def test_a_bare_department_word_is_never_a_subject(p6_conn, tmp_path, word):
    """`104` R-135's third ruling: nine of the 22 wrong subjects were one word.

    Unconditional -- it fires with no alias table at all, which is what makes it a fix
    rather than a feature of corpora that happen to hold a syllabus. A SHAPE and not a
    list: a gazetteer of department names could not be complete and `facts` may not hold
    one. The stated cost is that a genuinely one-word course name is refused too, unless
    an anchor in the corpus names it beside a code -- which is the next test.
    """
    for aliases in (None, _aliases(p6_conn)):
        assert cli.normalize_for_model("subject", word, aliases=aliases) is None
        assert cli.normalize_for_review("subject", word, aliases=aliases) is None
    assert _aliases(p6_conn).resolve(word).outcome == BARE_WORD
    assert word in _aliases(p6_conn).resolve(word).reason


def test_a_one_word_course_the_anchor_names_is_still_filable(p6_conn, tmp_path):
    """The bound on the ruling above, and the reason it is not a coverage regression.

    `Thermodynamics` is a real course name the model produced on the bench (`105` §1.3)
    and the shape rule refuses it. The alias table is what gives it back: a syllabus that
    prints `PHYS 1401: Thermodynamics` makes the word resolvable, and the fact that
    follows is the CODE, which is what the label wanted in the first place.
    """
    version, _ = _syllabus(p6_conn, tmp_path, name="phys.pdf", code="PHYS 1401",
                           before="Syllabus\n", after=": Thermodynamics\nsemester")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)
    aliases = _aliases(p6_conn)

    assert aliases.resolve("Thermodynamics").outcome == NAMED
    assert cli.normalize_for_model("subject", "Thermodynamics",
                                   aliases=aliases) == "PHYS1401"


def test_a_rule_written_subject_is_left_alone_and_never_doubled(p6_conn, tmp_path):
    """§3.5's rule ran first and this producer does not argue with it.

    `file_facts` has no uniqueness constraint over (file_id, content_hash, field_key),
    so a second write here is one file with two live subjects, two reliability states
    and two folder levels -- the defect the removed term slot was deleted over.
    Superseding another producer's conclusion is §8.2's path and is not this change.
    """
    from facts.discount import MetadataScreen
    from facts.rules import apply_rules

    anchor, _ = _syllabus(p6_conn, tmp_path)
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[anchor], **BUILD)

    file_id, content_hash = _file(p6_conn, tmp_path, name="hw3.pdf", body=b"hw")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash, raw="W3134",
             before="syllabus ", after=" problem set")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="Data Structures", zone="filename", span=False)
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(cli.SUBJECT_RULE,), screen=cli.METADATA_SCREEN)

    assert resolve_subject_facts(p6_conn, _aliases(p6_conn),
                                 file_versions=[(file_id, content_hash)],
                                 **RESOLVE) == ()
    assert _subjects(p6_conn, file_id, content_hash) == [("W3134", "validated", "rule")]


def test_a_file_naming_two_courses_is_refused_rather_than_picked(p6_conn, tmp_path):
    """Two titles, two codes, one file. §2.6's conflict, and never a vote."""
    first, _ = _syllabus(p6_conn, tmp_path, name="one.pdf", code="W3134")
    second, _ = _syllabus(p6_conn, tmp_path, name="two.pdf", code="E1006",
                          before="Syllabus\nENGI ",
                          after=": Introduction to Computing\nsemester")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[first, second],
                         **BUILD)

    file_id, content_hash = _file(p6_conn, tmp_path, name="both.pdf", body=b"b")
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="Data Structures", zone="filename", span=False)
    _observe(p6_conn, file_id=file_id, content_hash=content_hash,
             raw="Introduction to Computing", zone="title", span=False)

    assert resolve_subject_facts(p6_conn, _aliases(p6_conn),
                                 file_versions=[(file_id, content_hash)],
                                 **RESOLVE) == ()
    assert _subjects(p6_conn, file_id, content_hash) == []
    assert [row["reason"] for row in unresolved_for_file(p6_conn, file_id, content_hash)
            if row["field_key"] == cli.SUBJECT_FIELD] == [NORMALIZATION_FAILED]


def test_a_reading_the_subject_rule_refuses_never_defines_a_course(p6_conn, tmp_path):
    """The asserting knob, not the seeing one. `_SUBJECT_IDENTIFIER`'s two lookaheads.

    `I 1403` is `General Chemistry I` plus `1403` concatenated across a space -- the
    reading that filed three of the owner's chemistry exams under a course called
    `I1403` -- and `SPRING 2026` is a term. `_STRUCTURED` matches both, because it is
    what the product SEES; `SUBJECT_RULE.pattern` refuses both, because it is what the
    product ASSERTS. Only the second may define a course name for the whole corpus.
    """
    truncation, _ = _syllabus(p6_conn, tmp_path, name="chem.pdf", code="I 1403",
                              before="Syllabus\nGeneral Chemistry ",
                              after=": Sample Exam 1\nsemester")
    term, _ = _syllabus(p6_conn, tmp_path, name="term.pdf", code="SPRING 2026",
                        before="Syllabus\n", after=": Data Structures\nsemester")
    build_course_aliases(p6_conn, scan_run_id=SCAN,
                         file_versions=[truncation, term], **BUILD)

    assert p6_conn.execute("SELECT count(*) FROM course_aliases").fetchone()[0] == 0


def test_a_spelling_two_anchors_claim_is_dropped_rather_than_decided(p6_conn, tmp_path):
    """One anchor makes `CS3134` a spelling of `W3134`; another makes it a course.

    Sort order must not settle that. Keeping either would re-spell a real course into a
    different one, silently and on every file of it. The claim is dropped: the code
    stays itself, and the two TITLES still resolve, so the corpus loses an identity it
    could not establish and gains no wrong one.
    """
    both, _ = _syllabus(p6_conn, tmp_path, name="both.pdf", code="W3134",
                        before="Syllabus\nCOMS ",
                        after=" / CS3134: Data Structures\nsemester")
    own, _ = _syllabus(p6_conn, tmp_path, name="own.pdf", code="CS3134",
                       before="Syllabus\n", after=": Algorithms\nsemester")
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[both, own], **BUILD)
    aliases = _aliases(p6_conn)

    assert aliases.canonical_spelling("CS3134") == "CS3134"
    assert aliases.resolve("Data Structures").code == "W3134"
    assert aliases.resolve("Algorithms").code == "CS3134"


def test_check_four_compares_against_the_same_table_check_three_used(p6_conn, tmp_path):
    """§3.6 check 4, on the values check 3 now admits.

    Check 4's promise is that the comparison happens AFTER canonicalisation, so the
    model AGREEING in a different spelling does not read as a conflict. R-135 gave
    `normalize_for_model` a second way to answer, and an unbound check 4 would normalise
    `Data Structures` to `None` and answer `False` -- writing a second live `subject`
    beside a validated one that names a different course.
    """
    from types import SimpleNamespace

    version, _ = _syllabus(p6_conn, tmp_path)
    build_course_aliases(p6_conn, scan_run_id=SCAN, file_versions=[version], **BUILD)
    aliases = _aliases(p6_conn)
    proposal = SimpleNamespace(field_key=cli.SUBJECT_FIELD, value="Data Structures")

    disagrees = {"field_key": cli.SUBJECT_FIELD, "canonical_value": "E1006"}
    agrees = {"field_key": cli.SUBJECT_FIELD, "canonical_value": "W3134"}
    assert cli.contradicts_stronger(proposal, disagrees, aliases=aliases) is True
    assert cli.contradicts_stronger(proposal, agrees, aliases=aliases) is False
    # And the same words with no table are not normalizable, so check 3 refused them
    # first and check 4 keeps its one-reason-per-refusal rule.
    assert cli.contradicts_stronger(proposal, disagrees) is False

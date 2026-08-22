# tests/p6/test_p6_rules.py
"""§3.5 rule-validated facts -- Done-means 8, N-6, B8(a), and A03's ZIP-code case."""
import dataclasses
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import facts_for_file
from facts.rules import (
    ACADEMIC_CONTEXT_TERMS, MalformedRule, Rule, apply_rules, context_check,
)
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue is Deferred beyond the three named date patterns, and a
#: course-code pattern is not among them -- so the pattern is the test's, injected on
#: the Rule, and `facts.rules` holds no regex of its own.
COURSE_CODE = re.compile(r"\b[A-Z]{2,5} ?\d{2,5}\b")


def _record(conn, tmp_path, *, name, body):
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


def _run(conn, *, run_id, file_id, content_hash, analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             context_before=None, context_after=None, context_truncated=False):
    _run(conn, run_id=run_id, file_id=file_id, content_hash=content_hash)
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1), Segment("heading", 2))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after,
        context_truncated=context_truncated)
    record_observation(conn, observation)
    return observation


def _course_rule(terms=ACADEMIC_CONTEXT_TERMS):
    # D6: the stored academic key is `subject`. §3.11's word "course" is the design's
    # prose for the same field and survives inside quotations only.
    return Rule(pattern=COURSE_CODE, required_context_terms=tuple(terms),
                field_key="subject")


# --- the five terms are the design's, complete, and closed -------------------

def test_the_five_context_terms_are_exactly_the_designs_five():
    # §3.5, verbatim: "a course-code pattern together with academic context such as
    # "syllabus," "lecture," "credits," "instructor," or "semester."" Five terms are
    # stated literally; a sixth is a design change, not an implementation detail.
    assert ACADEMIC_CONTEXT_TERMS == ("syllabus", "lecture", "credits",
                                      "instructor", "semester")
    assert len(ACADEMIC_CONTEXT_TERMS) == 5
    assert len(set(ACADEMIC_CONTEXT_TERMS)) == 5


def test_no_other_context_vocabulary_is_authored_in_the_module():
    # "Rule context-term lists beyond the five literal academic terms | §3.5 | Only
    # "syllabus", "lecture", "credits", "instructor", "semester" are stated. Every
    # other domain's context vocabulary is unauthored."
    import facts.file_facts
    import facts.rules as module
    import facts.states
    import facts.unresolved
    import facts.values
    import evidence_shape.vocabulary
    foreign = {id(value)
               for source in (evidence_shape.vocabulary, facts.states,
                              facts.file_facts, facts.unresolved, facts.values)
               for value in vars(source).values()}
    catalogues = [name for name, value in vars(module).items()
                  if isinstance(value, tuple) and value and id(value) not in foreign
                  and all(isinstance(entry, str) for entry in value)]
    assert catalogues == ["ACADEMIC_CONTEXT_TERMS"]


def test_a_rule_carries_its_own_terms_and_the_module_supplies_no_default():
    # Every other domain's terms arrive injected; there is no default argument that
    # would quietly lend the academic five to a research or finance rule.
    with pytest.raises(TypeError):
        Rule(pattern=COURSE_CODE, field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=COURSE_CODE, required_context_terms=(), field_key="subject")
    with pytest.raises(MalformedRule):
        Rule(pattern=r"\b[A-Z]{2,5} ?\d{3,4}\b",
             required_context_terms=ACADEMIC_CONTEXT_TERMS, field_key="subject")


# --- the context check itself ------------------------------------------------

def test_the_context_check_is_case_insensitive():
    # N-6. §3.5 writes its terms lowercase and states no matching rule, so P6 states
    # one: a term matches regardless of the case it appears in.
    for spelling in ("Syllabus", "SYLLABUS", "syllabus", "SyLLaBuS"):
        assert context_check(f"{spelling} - ", "", ACADEMIC_CONTEXT_TERMS) is True


def test_case_insensitivity_does_not_relax_the_word_boundary():
    # The §3.7 discipline is unchanged: a case-insensitive match is not a substring
    # match, so `semester` must not match inside a longer word.
    assert context_check("Semesterly digest", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check("", "mid-semester break", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("lectureship award", "", ACADEMIC_CONTEXT_TERMS) is False


def test_both_halves_of_the_context_pair_are_read_and_never_concatenated():
    # M5: P4 split the context so §8.4 can redact a value without dropping its
    # context. Joining the halves would forge an adjacency the document does not have.
    assert context_check("Instructor: ", "", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("", " - 3 credits", ACADEMIC_CONTEXT_TERMS) is True
    assert context_check("sylla", "bus", ACADEMIC_CONTEXT_TERMS) is False


def test_an_absent_context_half_is_not_a_match():
    assert context_check("", "", ACADEMIC_CONTEXT_TERMS) is False
    assert context_check(None, None, ACADEMIC_CONTEXT_TERMS) is False


# --- Done-means 8, both halves ----------------------------------------------

def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # Done-means 8, negative half: "A course-code-shaped string with no academic
    # context term in its surrounding context produces no course fact."
    file_id, content_hash = _record(p6_conn, tmp_path, name="receipt.pdf",
                                    body=b"receipt")
    _observe(p6_conn, run_id="r-plain", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Order ", context_after=" shipped")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_check_failed"]


def test_p4s_fixture_1_verbatim_does_produce_one_validated_fact(p6_conn, tmp_path):
    # Done-means 8, positive half, and B8(a): fixture 1 carries `context_before`
    # exactly "Syllabus - " with a capital S. A case-sensitive check refuses it and
    # the walking skeleton produces no fact at all.
    fixture = by_number(1)
    original = fixture.observations[0]
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300 Syllabus")
    _run(p6_conn, run_id="fixture-1", file_id=file_id, content_hash=content_hash)
    observation = dataclasses.replace(original, file_id=file_id,
                                      content_hash=content_hash, run_id="fixture-1")
    record_observation(p6_conn, observation)

    assert observation.raw_value == "BUSIB 4300"
    assert observation.context_before == "Syllabus — "   # capital S, EM DASH
    assert observation.context_before[0] == "S"

    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(_course_rule(),))
    assert len(written) == 1
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("subject", "BUSIB 4300", "validated")]
    assert json.loads(rows[0]["evidence_refs"]) == [observation.observation_key]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_the_fact_cites_an_observation_key_and_leaves_the_raw_value_alone(
        p6_conn, tmp_path):
    # §3.2: the conclusion is stored beside the evidence, and the evidence survives.
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    observation = _observe(p6_conn, run_id="r-ok", file_id=file_id,
                           content_hash=content_hash, raw="BUSIB 4300",
                           context_before="Syllabus — ")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    refs = json.loads(facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]
    assert all(ref.startswith("sha256:") for ref in refs)
    stored = p6_conn.execute("SELECT raw_value FROM evidence WHERE file_id = ?",
                             (file_id,)).fetchone()
    assert stored["raw_value"] == "BUSIB 4300"


def test_every_one_of_the_five_terms_satisfies_the_check_on_its_own(
        p6_conn, tmp_path):
    for index, term in enumerate(ACADEMIC_CONTEXT_TERMS):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"t{index}.pdf",
                                        body=f"BUSIB 4300 {term}".encode())
        _observe(p6_conn, run_id=f"r{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_after=f" ({term.title()})")
        assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                               rules=(_course_rule(),))) == 1


def test_a_term_outside_the_five_does_not_satisfy_the_check(p6_conn, tmp_path):
    # "course", "class", "professor" and "seminar" all read as academic context to a
    # human. The design names five and this module authors no sixth.
    for index, near_miss in enumerate(("course", "class", "professor", "seminar")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"n{index}.pdf",
                                        body=f"BUSIB 4300 {near_miss}".encode())
        _observe(p6_conn, run_id=f"n{index}", file_id=file_id,
                 content_hash=content_hash, raw="BUSIB 4300",
                 context_before=f"{near_miss} ")
        assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),)) == ()
        assert [r["reason"] for r in unresolved_for_file(
            p6_conn, file_id, content_hash)] == ["context_check_failed"]


# --- §8.6: a cut context is not a clean refusal ------------------------------

def test_a_failed_check_on_a_truncated_record_is_context_truncated(
        p6_conn, tmp_path):
    # §8.6 forbids silent truncation. The term may have been cut off, so this is not
    # the same refusal as "the term is not there".
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...ourse outline for ",
             context_after=" and the", context_truncated=True)
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert [r["reason"] for r in rows] == ["context_truncated"]
    assert unresolved_for_file(p6_conn, file_id, content_hash,
                               reason="context_check_failed") == []


def test_a_truncated_record_whose_check_passes_still_produces_the_fact(
        p6_conn, tmp_path):
    # Truncation is only a problem for a refusal. If the term is present, it was not
    # the part that got cut.
    file_id, content_hash = _record(p6_conn, tmp_path, name="cut2.pdf", body=b"cut")
    _observe(p6_conn, run_id="r-cut2", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="...Syllabus — ",
             context_truncated=True)
    assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(_course_rule(),))) == 1
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- the shape of the refusal set --------------------------------------------

def test_a_pattern_that_does_not_match_writes_no_row_at_all(p6_conn, tmp_path):
    # A rule that does not apply is not a refusal. Writing one would fill
    # `unresolved` with every field every rule could theoretically have produced.
    file_id, content_hash = _record(p6_conn, tmp_path, name="prose.pdf",
                                    body=b"prose")
    _observe(p6_conn, run_id="r-none", file_id=file_id, content_hash=content_hash,
             raw="a paragraph about nothing in particular",
             context_before="Syllabus — ")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a03s_zip_code_produces_no_subject_fact(p6_conn, tmp_path):
    # A03, `subject_ref: "A03::zip::course"`, `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "course", "value": "MA 02139"}` -- read on the
    # stored key, which D6 fixes as `subject`. The pattern DOES match; the context
    # check is what refuses it, which is exactly §3.5's point.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-zip.txt",
                                    body=b"Ship to Cambridge MA 02139 by Friday.")
    _observe(p6_conn, run_id="A03-zip", file_id=file_id, content_hash=content_hash,
             raw="MA 02139", zone="body", context_before="Ship to Cambridge ",
             context_after=" by Friday.")
    assert COURSE_CODE.search("MA 02139") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_a03s_device_model_produces_no_subject_fact(p6_conn, tmp_path):
    # A03's second subject: `{"field": "course", "value": "XPS 13"}`.
    file_id, content_hash = _record(p6_conn, tmp_path, name="A03-device.txt",
                                    body=b"Receipt for one XPS 13 laptop.")
    _observe(p6_conn, run_id="A03-device", file_id=file_id,
             content_hash=content_hash, raw="XPS 13", zone="body",
             context_before="Receipt for one ", context_after=" laptop.")
    assert COURSE_CODE.search("XPS 13") is not None
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(_course_rule(),)) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == ["context_check_failed"]


def test_rules_do_not_read_another_versions_observations(p6_conn, tmp_path):
    # The abstention and the fact are both per file VERSION (§3.4, §8.2), so the read
    # filters on content hash and a prior version's evidence cannot resolve this one.
    file_id, content_hash = _record(p6_conn, tmp_path, name="v1.pdf", body=b"one")
    _observe(p6_conn, run_id="r-old", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    other_hash = "f" * 64
    _run(p6_conn, run_id="r-other", file_id=file_id, content_hash=other_hash)
    record_observation(p6_conn, Observation(
        file_id=file_id, content_hash=other_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value="ECON 1001", location=Location("heading", (Segment("page", 1),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="r-other", context_before="Syllabus — "))
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(),))
    values = {r["canonical_value"]
              for r in facts_for_file(p6_conn, file_id, content_hash)}
    assert values == {"BUSIB 4300"}


def test_the_outcome_does_not_depend_on_p4s_insertion_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid. Two observations, written in either
    # order, must produce the same two facts.
    def resolve(order):
        file_id, content_hash = _record(
            p6_conn, tmp_path, name=f"order-{'-'.join(order)}.pdf", body=b"x")
        for index, raw in enumerate(order):
            _observe(p6_conn, run_id=f"o{index}-{raw}", file_id=file_id,
                     content_hash=content_hash, raw=raw,
                     context_before="Syllabus — ")
        apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                    rules=(_course_rule(),))
        return sorted(r["canonical_value"]
                      for r in facts_for_file(p6_conn, file_id, content_hash))

    assert resolve(("BUSIB 4300", "ECON 1001")) == \
        resolve(("ECON 1001", "BUSIB 4300")) == ["BUSIB 4300", "ECON 1001"]


def test_several_rules_over_one_observation_each_write_their_own_row(
        p6_conn, tmp_path):
    # One rule fills, one refuses. The two outcomes are independent and neither
    # suppresses the other.
    file_id, content_hash = _record(p6_conn, tmp_path, name="two.pdf", body=b"two")
    _observe(p6_conn, run_id="r-two", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", context_before="Syllabus — ")
    venue_rule = Rule(pattern=COURSE_CODE,
                      required_context_terms=("proceedings", "conference"),
                      field_key="venue")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(_course_rule(), venue_rule))
    assert [r["field_key"] for r in facts_for_file(
        p6_conn, file_id, content_hash)] == ["subject"]
    assert [(r["field_key"], r["reason"]) for r in unresolved_for_file(
        p6_conn, file_id, content_hash)] == [("venue", "context_check_failed")]

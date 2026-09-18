# tests/p6/test_cli_one_syllabus_names_a_school.py
"""`106` Phase 6.4: a school one anchor names is put to the person.

`105` §14.4 makes a school level from two independent anchors in one scope, and
`_group_level_agreed` says what a course with one syllabus gets: "a school on that
syllabus and no school level". Nobody was told. The person's own answer stands alone
under the same rule, and `--confirm` already writes it -- so the whole of this is
the sentence that shows them what the one document said and what to type.

Lives under `tests/p6/` because `p6_conn` is `tests/p6/conftest.py`'s fixture; the
plan wrote the path one level up, where nothing provides it.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.evidence import cite
from facts.file_facts import LLM_INTERPRETATION, RULE, write_fact
from facts.states import (
    LLM_SUPPORTED, POSSIBLE, REJECTED, USER_CONFIRMED, VALIDATED,
)
from facts.values import VALUE_ORIGINS, ensure_value

import cli

CLOCK = "2026-09-18T00:00:00+00:00"
SYLLABUS = "PHYS 1401 syllabus.pdf"


def _file(conn, tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"syllabus")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=8,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _reading(conn, *, file_id, content_hash, raw):
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("title", ()), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="run-1")
    record_observation(conn, observation)
    return observation


def _fact(conn, file_id, content_hash, field_key, value, state, origin, refs=(),
          **extra):
    # A value with no citation is the person's own (`values.py` §3.12 refuses an
    # `automatic` value that cites nothing).
    value_id = ensure_value(conn, field_key=field_key, canonical_value=value,
                            first_evidence_ref=refs[0] if refs else None,
                            origin=VALUE_ORIGINS[0] if refs else VALUE_ORIGINS[1])
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key=field_key, value_id=value_id,
                      reliability_state=state, origin=origin,
                      evidence_refs=refs,
                      # The state is in `write_fact`'s identity already; it is in the
                      # key too so two writes of one value at two states cannot be
                      # read as one conclusion by anyone.
                      cache_key=f"t:{file_id}:{field_key}:{state}",
                      active=True, **extra)


def _one_syllabus_and_its_line(conn, tmp_path):
    file_id, content_hash = _file(conn, tmp_path, SYLLABUS)
    line = _reading(conn, file_id=file_id, content_hash=content_hash,
                    raw="PHYS 1401 Syllabus - Columbia University, Spring 2026")
    _fact(conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "syllabus",
          VALIDATED, RULE, (cite(line),))
    _fact(conn, file_id, content_hash, "school", "Columbia University",
          LLM_SUPPORTED, LLM_INTERPRETATION, (cite(line),))
    return file_id, content_hash, line


def _one_syllabus(conn, tmp_path):
    file_id, content_hash, _line = _one_syllabus_and_its_line(conn, tmp_path)
    return file_id, content_hash


def test_a_school_one_syllabus_names_is_put_to_the_person(p6_conn, tmp_path):
    """SABOTAGE: print nothing -- the syllabus's school dies at the two-anchor rule
    and the person never learns a single `--confirm` would have built the level."""
    _one_syllabus(p6_conn, tmp_path)
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    text = out.getvalue()
    assert "Columbia University" in text
    assert f"--confirm '{SYLLABUS}:school=Columbia University'" in text
    assert "Spring 2026" in text, "the line the model read is beside the value"


def test_a_school_on_a_file_that_is_not_an_anchor_is_not_offered(p6_conn, tmp_path):
    """`105` §14.4: only an anchor's own text establishes the relationship.
    SABOTAGE: drop the `work_type` test -- every `school` the model ever wrote off
    a header is offered as a folder, which is `104` §11.1's five essays under a
    high school."""
    file_id, content_hash = _file(p6_conn, tmp_path, "essay.pdf")
    line = _reading(p6_conn, file_id=file_id, content_hash=content_hash,
                    raw="Columbia University essay")
    _fact(p6_conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "essay",
          VALIDATED, RULE, (cite(line),))
    _fact(p6_conn, file_id, content_hash, "school", "Columbia University",
          LLM_SUPPORTED, LLM_INTERPRETATION, (cite(line),))
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert out.getvalue() == ""


def test_a_rejected_kind_beside_a_school_does_not_crash_the_screen(p6_conn, tmp_path):
    """`strength` raises on `rejected`, and a rejected row can be active -- the
    sibling `_print_values_to_confirm` skips it before the ladder is read for
    exactly this reason. SABOTAGE: call `strength` on every active row -- a person
    who rejected one kind guess loses the whole fact-pass screen to a traceback."""
    file_id, content_hash, line = _one_syllabus_and_its_line(p6_conn, tmp_path)
    _fact(p6_conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "essay",
          REJECTED, LLM_INTERPRETATION, (cite(line),), rejection_reason="not this")
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert "Columbia University" in out.getvalue()


def test_a_possible_school_is_below_the_ladder_and_not_offered(p6_conn, tmp_path):
    """ONE STATE. A `possible` school is not what the two-anchor rule counts, and
    its review path is the owner's open question at `REVIEW_NORMALISED_FIELDS`.
    SABOTAGE: read `possible` too -- this screen opens the door that comment
    refuses."""
    file_id, content_hash = _file(p6_conn, tmp_path, SYLLABUS)
    line = _reading(p6_conn, file_id=file_id, content_hash=content_hash,
                    raw="PHYS 1401 Syllabus - Columbia University, Spring 2026")
    _fact(p6_conn, file_id, content_hash, cli.WORK_TYPE_FIELD, "syllabus",
          VALIDATED, RULE, (cite(line),))
    _fact(p6_conn, file_id, content_hash, "school", "Columbia University",
          POSSIBLE, LLM_INTERPRETATION, (cite(line),))
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert out.getvalue() == ""


def test_a_school_the_person_already_confirmed_is_not_asked_again(p6_conn, tmp_path):
    """`00`:298 -- proposed once. SABOTAGE: read every state."""
    file_id, content_hash = _one_syllabus(p6_conn, tmp_path)
    _fact(p6_conn, file_id, content_hash, "school", "Columbia University",
          USER_CONFIRMED, RULE)
    out = io.StringIO()
    cli._print_schools_one_document_names(p6_conn, out)
    assert out.getvalue() == ""


def test_the_confirm_line_writes_the_answer_the_two_anchor_rule_admits_alone(
        p6_conn, tmp_path):
    """The gesture already exists; this pins that the line the screen prints is the
    line the gesture accepts. Passes before the screen exists, by design."""
    file_id, content_hash = _one_syllabus(p6_conn, tmp_path)
    cli.apply_confirmations(
        p6_conn, [f"{SYLLABUS}:school=Columbia University"],
        user_id="owner", observed_at=CLOCK)
    states = {row["reliability_state"] for row in cli.facts_for_file(
        p6_conn, file_id, content_hash) if row["field_key"] == "school" and row["active"]}
    assert USER_CONFIRMED in states

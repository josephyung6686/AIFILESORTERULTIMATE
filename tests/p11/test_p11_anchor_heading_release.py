# tests/p11/test_p11_anchor_heading_release.py
"""`104` R-135 -- what site C's candidate release can and cannot show the model.

The row's worked example is a syllabus whose heading reads `COMS W3134: Data
Structures` and coursework files whose text says only `Data Structures`. The model is
the only thing that may decide those name one course (product constitution 1: "LLM
decides, code delivers ... no alias tables, no equivalence maps"), and site C's own
prompt already tells it "two spellings can be one thing ... yours to judge from the
evidence".

This file measures whether the evidence reaches it. `extractors/pdf.py` emits TWO
observations over that heading:

  * the heading itself -- `zone="heading"`, `raw_value` the whole line, span `(0, len)`
    over a unit whose text IS the line;
  * the identifier inside it -- `raw_value="W3134"`, a span partway into the same unit.

Only the second survives `model_placement.releasable_excerpts`, because the first is
caught by §8.4's whole-document refusal: its span covers the whole of its unit. So the
model is shown `W3134` and never the words beside it, and the judgement the prompt asks
for cannot be made from what it is given.

These are CHARACTERISATION tests: they pin what the code does today, including the part
that is wrong, so the refusal is a measured fact and not an assertion. Changing what
leaves the device is the lead's ruling, not this file's.
"""
from __future__ import annotations

import json
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    record_observation, record_run, record_text_unit,
)
from evidence_shape.text_units import TextUnit

from extractors.long_tail import SENSITIVITY_DDL

from model_placement import releasable_excerpts

CLOCK = "2026-09-07T00:00:00Z"

#: The owner's own syllabus heading, from `104` R-135. Both spellings, one line.
HEADING = "COMS W3134: Data Structures"

#: Where `W3134` sits inside it. Not a parser -- the fixture states the span the way
#: `find_structured_strings` would have found it, because this file measures the
#: RELEASE and must not contain a second implementation of the reading.
CODE_START = HEADING.index("W3134")
CODE_END = CODE_START + len("W3134")


def _corpus(conn, tmp_path):
    """One syllabus file, one heading unit, and the two observations over it."""
    create_schema(conn)
    create_evidence_schema(conn)
    # P5's per-value signal table. Created EMPTY and created visibly: nothing in this
    # fixture is signalled, and the release path reads the table on every candidate, so
    # "this test signals nothing" is written here rather than being an absence that
    # happens to pass.
    conn.executescript(SENSITIVITY_DDL)
    body = HEADING.encode()
    path = tmp_path / "syllabus.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="syllabus.pdf", normalized_filename="syllabus.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-syllabus"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    # The heading is its own text unit, exactly as `extractors/pdf.py` builds one.
    container = (Segment("page", 1), Segment("heading", 1))
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=container, text=HEADING))

    def observe(raw, span):
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location("heading", container, text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        return observation

    whole = observe(HEADING, TextSpan(0, len(HEADING)))
    code = observe("W3134", TextSpan(CODE_START, CODE_END))
    return file_id, whole, code


def test_the_code_inside_the_heading_is_released(conn, tmp_path):
    """The reading the model DOES get: five characters, and no words beside them."""
    _file_id, _whole, code = _corpus(conn, tmp_path)

    offered = releasable_excerpts(
        conn, evidence_refs=[code.observation_key])

    assert [one.observation_key for one in offered] == [code.observation_key]


def test_the_heading_that_states_both_spellings_is_released(conn, tmp_path):
    """`104` R-135, after the ruling. This test FLIPPED, deliberately.

    It measured the blocker first: the one reading in the corpus that carries the code
    AND the course's name was refused, because §8.4's whole-document rule fired on a
    HEADING. §8.4's sentence is "should not send full documents where a short heading or
    OCR excerpt is enough", so the rule was refusing the alternative it exists to prefer.

    The ruling is `privacy.release.unit_is_a_heading`: a whole heading unit is released,
    a whole document is not, and no length bound is invented. The exposure is counted
    instead. Both readings now reach the model, which is what site C's own instruction
    to judge two spellings needs in order to mean anything.
    """
    _file_id, whole, code = _corpus(conn, tmp_path)

    offered = releasable_excerpts(
        conn, evidence_refs=[whole.observation_key, code.observation_key])

    keys = [one.observation_key for one in offered]
    assert whole.observation_key in keys
    assert code.observation_key in keys


def test_site_a_releases_the_same_heading_for_the_same_reason(conn, tmp_path):
    """The ruling is the PRODUCT's, not site C's, which is why both sites move together.

    `model_facts.releasable_observations` carried the identical whole-unit condition and
    takes the identical exemption, so the heading that states the course's code and its
    name together now reaches the fact model too. Constitution 2: "Any successfully-read
    file must reach the model" -- the file always reached it; the one reading that
    settles this row did not, at either site, and now does at both.
    """
    from model_facts import releasable_observations

    _file_id, whole, code = _corpus(conn, tmp_path)

    offered = releasable_observations(
        conn, file_id=_file_id, content_hash=get_file(conn, _file_id)["content_hash"],
        limit=10)
    keys = [one.observation_key for one in offered]

    assert code.observation_key in keys
    assert whole.observation_key in keys


def test_no_release_carries_the_context_beside_a_span(conn, tmp_path):
    """The other route to the title, closed on purpose and not by accident.

    `privacy.release.ReleasedItem` has no `context_before` and no `context_after`, and
    its docstring says why: the context is raw text on either side of the span and §8.4
    puts complete extracted text in the always-local set. So `: Data Structures` cannot
    reach the model as the identifier's context either, and a fix that added it would be
    the fifth field that docstring names as the failure.
    """
    from privacy.release import RELEASED_EVIDENCE_FIELDS, ReleasedItem

    assert "context_before" not in RELEASED_EVIDENCE_FIELDS
    assert "context_after" not in RELEASED_EVIDENCE_FIELDS
    assert not hasattr(ReleasedItem(observation_key="", span="", value="", zone="",
                                    unit_length=None), "context_before")


def test_a_whole_body_unit_is_still_refused(conn, tmp_path):
    """The half of the ruling that did NOT move, and the reason it is safe.

    `104` R-135 exempts a whole HEADING unit and nothing else. A span covering a whole
    `body` unit is a full document, which is exactly what §8.4 forbids sending, and the
    exemption is structural -- the innermost container segment -- so it cannot widen to
    a page by accident. Without this assertion the ruling would read as "whole units are
    releasable now", which is not what was ruled.
    """
    from evidence_shape.location import Location, Segment, TextSpan

    _file_id, _whole, code = _corpus(conn, tmp_path)
    file_id = code.file_id
    page = (Segment("page", 1),)
    prose = "The whole of a page of this document, which is not a heading."
    record_text_unit(conn, TextUnit(
        run_id="run-syllabus", container_path=page, text=prose))
    body = Observation(
        file_id=file_id, content_hash=code.content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=prose,
        location=Location("body", page, text_span=TextSpan(0, len(prose))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-syllabus")
    record_observation(conn, body)

    offered = releasable_excerpts(conn, evidence_refs=[body.observation_key])

    assert offered == ()


# --------------------------------------------------------------------------
# The exposure the ruling reports instead of bounding
# --------------------------------------------------------------------------

#: A second heading unit, longer than the first, so "the longest" is a choice the
#: assertion can catch getting wrong rather than the only number available.
SECOND_HEADING = "COMS W3157: Advanced Programming, Fall 2026"


def _dossier_released(*released):
    """One site-A dossier carrying exactly these released items and nothing else.

    Built by hand rather than from `llm_harness.fixtures` because that builder writes
    one constant address into every item, and the counter reads the address.
    """
    from llm_harness.records import Dossier, EvidenceItem
    from llm_harness.vocabulary import (
        A_FACT, DIRECT_ANCHOR, REDUCTION_NONE, REMAINS_AMBIGUOUS,
    )

    return Dossier(
        dossier_id="dossier-r135-exposure",
        call_site=A_FACT,
        subject_ref="file-1",
        eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None,
        policy_version="policy-1",
        allowed_vocabulary=("subject",),
        evidence_items=tuple(
            EvidenceItem(
                evidence_ref=item.observation_key, kind="excerpt",
                location=item.address, excerpt_span=None,
                reliability_state="direct", basis=DIRECT_ANCHOR)
            for item in released),
        conflicts=(),
        released_evidence=tuple(released),
        max_dossier_tokens=4000,
        reduction_rung=REDUCTION_NONE,
        release_id="rel-1")


def _report(dossier):
    from llm_harness.validation import report_from_verdicts

    return report_from_verdicts(
        dossier, (), model_id="local-model", prompt_fingerprint="fp-1",
        dossier_builder="r135-exposure-suite", release_audit_id=None)


def test_two_heading_units_released_whole_are_counted_and_the_longer_measured():
    """`104` R-135's count, and the field it feeds was reporting zero until now.

    The ruling sets NO length bound -- "a bound is a number nobody authored" -- and
    reports the exposure instead. A declared counter nothing populates reports zero on
    a run that released every heading in the corpus, which is worse than no counter:
    it answers the question the ruling promised to answer, wrongly.

    Two whole heading units here, of different lengths, so the longest is a choice.
    """
    from llm_harness.records import ReleasedEvidence

    dossier = _dossier_released(
        ReleasedEvidence(
            observation_key="obs-heading-1",
            address=f"heading:page=1/heading=1#0-{len(HEADING)}",
            value=HEADING, zone="heading", unit_length=len(HEADING)),
        ReleasedEvidence(
            observation_key="obs-heading-2",
            address=f"heading:page=2/heading=1#0-{len(SECOND_HEADING)}",
            value=SECOND_HEADING, zone="heading",
            unit_length=len(SECOND_HEADING)))

    report = _report(dossier)

    assert report.heading_units_released == 2
    assert report.longest_heading_unit_length == len(SECOND_HEADING)
    assert len(SECOND_HEADING) > len(HEADING)


def test_a_dossier_with_no_whole_heading_reports_zero():
    """Zero when zero, and the identifier INSIDE a heading is the case that matters.

    `extractors/pdf.py` gives `W3134` the same container path as the heading it sits
    in, so a count that read the container alone would report this call as an exposure
    it is not: the span is five characters of a twenty-seven character unit and no
    exemption was taken to release it. The predicate reads the span, and this is the
    assertion that says so. A whole `body` unit is not counted either -- the release
    builders refuse it, so a dossier could not carry one.
    """
    from llm_harness.records import ReleasedEvidence

    dossier = _dossier_released(
        ReleasedEvidence(
            observation_key="obs-code",
            address=f"heading:page=1/heading=1#{CODE_START}-{CODE_END}",
            value="W3134", zone="heading", unit_length=len(HEADING)),
        ReleasedEvidence(
            observation_key="obs-body",
            address="body:page=1#0-12", value="a short run",
            zone="body", unit_length=400))

    report = _report(dossier)

    assert report.heading_units_released == 0
    assert report.longest_heading_unit_length == 0

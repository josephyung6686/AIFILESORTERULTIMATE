# tests/p11/test_p11_line_unit_release.py
"""`104` R-152 -- a unit that holds no line break is a LINE, and a line is an excerpt.

The twin of `test_p11_anchor_heading_release.py`, which is R-135's file, and it is a
separate file for the reason the rulings are separate rows: R-135 asks what the
innermost container segment says a unit IS, and R-152 asks whether the unit's own text
says it has a second line. They meet in one predicate family in `privacy.release` and
one pair of counters in `GroundingReport`, and they are measured apart.

What the row measured, at r13 on the owner's corpus: 47 calls came back
`Denied(whole_document_requested)`, 36 of them at site A, where the denial is the
file's WHOLE call -- `PRIVACY_GATE_REFUSED` in the grounding report and every fact of
the file recorded `missing`. The units were under 200 characters, 24 of them under 50,
mostly pdf and docx. §8.4's sentence is *"should not send full documents where a short
heading or OCR excerpt is enough to resolve the question"*, and a nineteen-character
line IS that short excerpt. The rule was refusing the thing it exists to prefer.

The gate half of the ruling is measured in `tests/p7/test_p7_whole_document.py`, beside
the refusal it excepts. This file is the two release BUILDERS and the report.
"""
from __future__ import annotations

import json

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run, record_text_unit
from evidence_shape.text_units import TextUnit

from extractors.long_tail import SENSITIVITY_DDL

from model_placement import releasable_excerpts
from privacy.vocabulary import CLOUD_LOCALITY
#: `104` R-159's two new keywords, spelled once for this file. `CLOUD_LOCALITY`
#: because every test here predates the ruling and asserts the cloud half of it,
#: which is the half that did not change; the ceiling because a cloud call is bound
#: by the COUNT and never reads the ceiling, so any value states the same thing.
A_CEILING = 4000


CLOCK = "2026-09-08T00:00:00Z"

#: Nineteen characters, one line. A running footer, a table cell and an OCR excerpt all
#: arrive in this shape, which is why the row measured mostly pdf and docx.
A_LINE = "Invoice total 42.00"

#: A longer line, so "the longest" is a choice an assertion can catch getting wrong.
A_LONGER_LINE = "Remit to Accounts Receivable, 200 West 116th Street"

#: The same words as `A_LINE` with the line breaks a page of prose has. The ONLY
#: difference is the newlines, so a rule that admits one and refuses the other has
#: isolated the criterion and is not reading length, zone or extractor.
A_PAGE = "Invoice total 42.00\nDue on receipt, net 30\nRemit to the address above"

#: Where `42.00` sits inside the page. Stated, not parsed: this file measures the
#: release and must not carry a second implementation of the reading.
INNER_START = A_PAGE.index("42.00")
INNER_END = INNER_START + len("42.00")


def _corpus(conn, tmp_path):
    """One invoice, a one-line unit, a multi-line unit, and a span inside the latter."""
    create_schema(conn)
    create_evidence_schema(conn)
    # P5's per-value signal table, created EMPTY and created visibly: the release path
    # reads it for every candidate, so "this fixture signals nothing" is written here
    # rather than being an absence that happens to pass.
    conn.executescript(SENSITIVITY_DDL)
    body = A_PAGE.encode()
    path = tmp_path / "invoice.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="invoice.pdf", normalized_filename="invoice.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Bills", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-invoice"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    line_at = (Segment("page", 1), Segment("paragraph", 1))
    page_at = (Segment("page", 2),)
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=line_at, text=A_LINE))
    record_text_unit(conn, TextUnit(
        run_id=run_id, container_path=page_at, text=A_PAGE))

    def observe(raw, container, span):
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location("body", container, text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        return observation

    line = observe(A_LINE, line_at, TextSpan(0, len(A_LINE)))
    page = observe(A_PAGE, page_at, TextSpan(0, len(A_PAGE)))
    inner = observe("42.00", page_at, TextSpan(INNER_START, INNER_END))
    return file_id, content_hash, line, page, inner


# --------------------------------------------------------------------------
# The two release builders
# --------------------------------------------------------------------------

def test_site_c_offers_a_whole_single_line_unit(conn, tmp_path):
    """`104` R-152 at `model_placement.releasable_excerpts`.

    Before the ruling this returned `()`: the span covers the whole of its unit, the
    unit's innermost segment is not `heading`, and the builder stopped there. So a
    nineteen-character line -- the very thing §8.4 names as sufficient instead of a
    document -- was never offered to a model.

    SABOTAGE: drop the `unit_holds_line_break` argument and let the predicate default
    to "unknown", and this goes red, which is the criterion doing the work.
    """
    _file_id, _hash, line, _page, _inner = _corpus(conn, tmp_path)

    offered = releasable_excerpts(conn, evidence_refs=[line.observation_key], locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [line.observation_key]


def test_site_c_still_refuses_the_same_words_once_they_hold_line_breaks(
        conn, tmp_path):
    """The control. A unit that holds a line break has said it has a second line, and
    the whole of it is what §8.4 calls a full document. Nothing here is about length:
    the page is 68 characters and the released line is 19, and swapping the two numbers
    would not swap the answers."""
    _file_id, _hash, _line, page, _inner = _corpus(conn, tmp_path)

    assert releasable_excerpts(conn, evidence_refs=[page.observation_key], locality=CLOUD_LOCALITY) == ()


def test_site_c_still_offers_a_bounded_span_inside_the_multi_line_unit(
        conn, tmp_path):
    """The document stays refused and its excerpts stay releasable, which is the whole
    of §8.4's preference. Without this, "a multi-line unit is refused" could be read as
    "a multi-line unit is unreachable"."""
    _file_id, _hash, _line, _page, inner = _corpus(conn, tmp_path)

    offered = releasable_excerpts(conn, evidence_refs=[inner.observation_key], locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [inner.observation_key]


def test_site_a_takes_the_same_ruling_for_the_same_reason(conn, tmp_path):
    """The ruling is the PRODUCT's, not one site's, which is why both sites move.

    `model_facts.releasable_observations` carried the identical whole-unit condition
    and now takes the identical exemption, through the same predicate the report counts
    by and the gate excepts by. Constitution 2: "Any successfully-read file must reach
    the model" -- at site A the denial was the file's whole call, so the file reached no
    model at all.
    """
    from model_facts import releasable_observations

    file_id, content_hash, line, page, inner = _corpus(conn, tmp_path)

    offered = releasable_observations(
        conn, file_id=file_id, content_hash=content_hash, limit=10, locality=CLOUD_LOCALITY, ceiling=A_CEILING)
    keys = [one.observation_key for one in offered]

    assert line.observation_key in keys
    assert inner.observation_key in keys
    assert page.observation_key not in keys


def test_the_named_readings_builder_takes_it_too(conn, tmp_path):
    """`model_facts.releasable_readings` answers "may these particular readings be
    shown" and runs the same exclusions as the ranking above. `104` R-135's context
    builder is its caller, so a one-line reading of a neighbouring file was refused
    there as well."""
    from model_facts import releasable_readings

    file_id, content_hash, line, page, _inner = _corpus(conn, tmp_path)

    offered = releasable_readings(
        conn, file_id=file_id, content_hash=content_hash,
        keys=[page.observation_key, line.observation_key], locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [line.observation_key]


# --------------------------------------------------------------------------
# The exposure the ruling reports instead of bounding
# --------------------------------------------------------------------------

def _dossier_released(*released):
    """One site-A dossier carrying exactly these released items and nothing else.

    Built by hand rather than from `llm_harness.fixtures` for the reason R-135's file
    gives: that builder writes one constant address into every item, and the counter
    reads the address.
    """
    from llm_harness.records import Dossier, EvidenceItem
    from llm_harness.vocabulary import (
        A_FACT, DIRECT_ANCHOR, REDUCTION_NONE, REMAINS_AMBIGUOUS,
    )

    return Dossier(
        dossier_id="dossier-r152-exposure",
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
        dossier_builder="r152-exposure-suite", release_audit_id=None)


def test_two_line_units_released_whole_are_counted_and_the_longer_measured():
    """`104` R-152's count, which is what the ruling reports INSTEAD of a length bound.

    A bound is a number nobody authored and this deployment invents none, so the first
    scorecard has to show how much line text actually left and how long the longest
    piece was. `longest_line_unit_length` is also where `104` R-145's long paragraph
    becomes visible: a 4,000-character single line is still one line and is still
    released, and its size is §8.6's dossier ceiling to bound, not this predicate's.
    """
    from llm_harness.records import ReleasedEvidence

    dossier = _dossier_released(
        ReleasedEvidence(
            observation_key="obs-line-1",
            address=f"body:page=1/paragraph=1#0-{len(A_LINE)}",
            value=A_LINE, zone="body", unit_length=len(A_LINE),
            whole_line_unit=True),
        ReleasedEvidence(
            observation_key="obs-line-2",
            address=f"body:page=2/paragraph=1#0-{len(A_LONGER_LINE)}",
            value=A_LONGER_LINE, zone="body", unit_length=len(A_LONGER_LINE),
            whole_line_unit=True))

    report = _report(dossier)

    assert report.line_units_released == 2
    assert report.longest_line_unit_length == len(A_LONGER_LINE)
    assert len(A_LONGER_LINE) > len(A_LINE)
    assert report.heading_units_released == 0


def test_a_bounded_span_inside_a_unit_is_not_counted():
    """Zero when zero. The excerpt took no exemption to be released -- its span is five
    characters of a sixty-eight character unit -- so counting it would report an
    exposure that did not happen. The predicate reads the span, and the item carries
    what the predicate answered."""
    from llm_harness.records import ReleasedEvidence

    dossier = _dossier_released(
        ReleasedEvidence(
            observation_key="obs-inner",
            address=f"body:page=2#{INNER_START}-{INNER_END}",
            value="42.00", zone="body", unit_length=len(A_PAGE)))

    report = _report(dossier)

    assert report.line_units_released == 0
    assert report.longest_line_unit_length == 0


def test_a_one_line_heading_is_counted_under_both_and_summed_under_neither():
    """The overlap, stated rather than left to be discovered.

    Most headings are one line, so most of R-135's exemptions are also R-152's. The two
    counters answer different questions about the same run -- whether
    `recognition/detector.py` is tagging prose as a heading, and whether a long
    paragraph is leaving whole -- so the item is counted under each and the two are
    never added. A merged count would hide both defects behind each other.
    """
    from llm_harness.records import ReleasedEvidence

    title = "COMS W3134: Data Structures"
    dossier = _dossier_released(
        ReleasedEvidence(
            observation_key="obs-title",
            address=f"heading:page=1/heading=1#0-{len(title)}",
            value=title, zone="heading", unit_length=len(title),
            whole_heading_unit=True, whole_line_unit=True))

    report = _report(dossier)

    assert report.heading_units_released == 1
    assert report.line_units_released == 1
    assert report.longest_heading_unit_length == len(title)
    assert report.longest_line_unit_length == len(title)

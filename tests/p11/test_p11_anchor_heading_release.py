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
from privacy.vocabulary import CLOUD_LOCALITY
#: `104` R-159's two new keywords, spelled once for this file. `CLOUD_LOCALITY`
#: because every test here predates the ruling and asserts the cloud half of it,
#: which is the half that did not change; the ceiling because a cloud call is bound
#: by the COUNT and never reads the ceiling, so any value states the same thing.
A_CEILING = 4000


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
        conn, evidence_refs=[code.observation_key], locality=CLOUD_LOCALITY)

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
        conn, evidence_refs=[whole.observation_key, code.observation_key], locality=CLOUD_LOCALITY)

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
        limit=10, locality=CLOUD_LOCALITY, ceiling=A_CEILING)
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

    `104` R-135 exempts a whole HEADING unit and `104` R-152 a whole LINE unit, and
    nothing else. A span covering a whole `body` unit of SEVERAL LINES is a full
    document, which is exactly what §8.4 forbids sending, and both exemptions are
    structural -- the innermost container segment, and whether the unit holds a line
    break -- so neither can widen to a page by accident. Without this assertion the
    ruling would read as "whole units are releasable now", which is not what was ruled.

    THE PROSE GAINED ITS LINE BREAKS FOR R-152. It was one 61-character line, which
    made this test a pin on the refusal that row measured as a coverage loss: 47 gate
    refusals at r13, 36 of them the whole of a site-A call, on units under 200
    characters. A one-line unit is now released, so a control that used one was
    measuring the defect rather than the rule. A page of prose has line breaks in it,
    which is the shape this test was always about.
    """
    from evidence_shape.location import Location, Segment, TextSpan

    _file_id, _whole, code = _corpus(conn, tmp_path)
    file_id = code.file_id
    page = (Segment("page", 1),)
    prose = ("The whole of a page of this document, which is not a heading.\n"
             "It runs to a second line, and to a third, the way a page does.\n"
             "A unit that holds line breaks is what §8.4 calls a full document.")
    record_text_unit(conn, TextUnit(
        run_id="run-syllabus", container_path=page, text=prose))
    body = Observation(
        file_id=file_id, content_hash=code.content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=prose,
        location=Location("body", page, text_span=TextSpan(0, len(prose))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-syllabus")
    record_observation(conn, body)

    offered = releasable_excerpts(conn, evidence_refs=[body.observation_key], locality=CLOUD_LOCALITY)

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
            value=HEADING, zone="heading", unit_length=len(HEADING),
            whole_heading_unit=True),
        ReleasedEvidence(
            observation_key="obs-heading-2",
            address=f"heading:page=2/heading=1#0-{len(SECOND_HEADING)}",
            value=SECOND_HEADING, zone="heading",
            unit_length=len(SECOND_HEADING), whole_heading_unit=True))

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


def test_an_item_that_could_not_be_classified_counts_as_nothing():
    """The regression, and it cost fourteen already-answered calls.

    The first spelling of this count parsed `ReleasedEvidence.address` back into a
    `Location`. `parse_locator` refuses in three ways -- a shape it cannot read, a zone
    or segment kind outside P4's closed sets, a location whose parts disagree -- and a
    dossier built by hand, as `llm_harness.fixtures` and every harness test build one,
    carries addresses that are not locators. `tests/p8/test_p8_harness.py` raised
    `NotInVocabulary: zone='0'` out of `report_from_verdicts` and ended fourteen calls
    the model had already answered.

    A released item now SAYS what it is, decided in `resolve.materialise` where P4's
    `Location` still exists. Nothing at report time derives, so nothing at report time
    can refuse. An address that is not a locator is not an error here; it is an item
    that is not a whole heading unit, and it counts as nothing.
    """
    from llm_harness.records import ReleasedEvidence

    report = _report(_dossier_released(
        ReleasedEvidence(observation_key="obs-fixture", address="0:18",
                         value="Columbia University", zone="body"),
        ReleasedEvidence(observation_key="obs-fixture-2", address="heading:course",
                         value=HEADING, zone="heading")))

    assert report.heading_units_released == 0
    assert report.longest_heading_unit_length == 0


# --------------------------------------------------------------------------
# Site C: the line reaches the judge, and two lines reach it as two
# --------------------------------------------------------------------------

#: A second syllabus heading in the same document, naming the same course a second
#: way. Two anchors for one course is the case the constitution's "no sorting rules"
#: is about, so the fixture has to be able to produce it.
SECOND_LINE = "COMS W3134 Data Structures in Java, Section 002"


def _anchor_corpus(conn, tmp_path, *, lines=(HEADING,)):
    """A syllabus whose headings each print a course code, with anchor rows recorded.

    Built the way `extractors/pdf.py` builds one: each heading is its own text unit,
    and P4 emits the heading AND the identifier inside it over the same container path.
    The deployment's own four arguments come from `cli`, never restated here -- a test
    holding its own pattern would be testing a rule `facts` does not have.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    conn.executescript(SENSITIVITY_DDL)

    body = b"syllabus"
    path = tmp_path / "syllabus.pdf"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="syllabus.pdf", normalized_filename="syllabus.pdf",
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = "run-anchor"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))

    emitted = []
    for ordinal, line in enumerate(lines, start=1):
        container = (Segment("page", 1), Segment("heading", ordinal))
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=container, text=line))
        start = line.index("W3134")
        end = start + len("W3134")

        def observe(raw, span, before, after):
            observation = Observation(
                file_id=file_id, content_hash=content_hash,
                extractor_name="pdf.text", extractor_version="1.0.0",
                source_type="text_document", raw_value=raw,
                location=Location("heading", container, text_span=span),
                occurrence_count=1, observed_at=CLOCK, reliability="possible",
                run_id=run_id, context_before=before, context_after=after)
            record_observation(conn, observation)
            return observation

        whole = observe(line, TextSpan(0, len(line)),
                        "Syllabus\n", "\nInstructor: Dr Lacker")
        code = observe("W3134", TextSpan(start, end),
                       f"Syllabus\n{line[:start]}", line[end:])
        emitted.append((whole, code))

    record_anchor_statements(
        conn, scan_run_id="scan-r135", file_versions=[(file_id, content_hash)],
        is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)
    return file_id, tuple(emitted)


def test_the_candidate_excerpt_carries_the_whole_line_and_not_the_code_alone(
        conn, tmp_path):
    """`104` R-135 at site C: the judge is shown the words beside the code.

    A fact cites the reading that MATCHED it, and §3.5's `subject` rule matches a code,
    so `evidence_for` offered `W3134` and nothing else. `: Data Structures` sat in a
    second reading of the same heading that no fact had any reason to cite -- and site
    C's own prompt asks the model whether two spellings are one thing, which is not a
    question five characters can answer.

    The assertion is on the RELEASED text and not on the offer: the excerpt the model
    sees is materialised here, and its value is the whole line.
    """
    import cli
    from privacy.resolve import materialise

    file_id, emitted = _anchor_corpus(conn, tmp_path)
    (whole, code), = emitted

    lines = cli.anchor_line_citations(
        conn, scan_run_id="scan-r135", file_id=file_id)
    assert [ref for ref, _location, _reliability in lines] == [
        whole.observation_key]

    offered = releasable_excerpts(
        conn, evidence_refs=[ref for ref, _l, _r in lines], locality=CLOUD_LOCALITY)
    assert [one.observation_key for one in offered] == [whole.observation_key]

    released = materialise(conn, offered[0], within_file_ids=(file_id,))
    assert released.value == HEADING
    assert "Data Structures" in released.value
    assert "W3134" in released.value
    # P4's own word for that reading, not a constant the builder typed.
    assert [reliability for _ref, _l, reliability in lines] == [whole.reliability]


def test_two_anchor_lines_for_one_course_both_appear_and_neither_is_chosen(
        conn, tmp_path):
    """Constitution 1: *"no sorting rules ... reconciliation is a model decision."*

    One document naming one course on two lines is the case where a tie-breaker would
    be invented. The first attempt at this row broke exactly this tie by sort order.
    Both lines are offered, in `anchor_statements_for`'s recorded order, and the two
    released values differ -- so the model has two readings to reconcile and the code
    has expressed no preference between them.
    """
    import cli
    from privacy.resolve import materialise

    file_id, emitted = _anchor_corpus(
        conn, tmp_path, lines=(HEADING, SECOND_LINE))

    lines = cli.anchor_line_citations(
        conn, scan_run_id="scan-r135", file_id=file_id)
    offered_refs = [ref for ref, _location, _reliability in lines]

    assert len(offered_refs) == 2
    assert set(offered_refs) == {emitted[0][0].observation_key,
                                 emitted[1][0].observation_key}

    offered = releasable_excerpts(conn, evidence_refs=offered_refs, locality=CLOUD_LOCALITY)
    values = [materialise(conn, one, within_file_ids=(file_id,)).value
              for one in offered]
    assert sorted(values) == sorted([HEADING, SECOND_LINE])


#: The filename `extractors/filesystem.py` reads, and the length the register
#: measured on the real corpus: `excerpt / filename / [0,22] / possible`.
ANCHOR_FILENAME = "COMS W3134 syllabus.md"

#: The document's own first line, whose `W3134` sits at the same offsets the
#: filename's does. The two spans are what makes the defect reachable.
ANCHOR_BODY = "COMS W3134 syllabus\nInstructor: Dr Lacker"


def _filename_line_corpus(conn, tmp_path):
    """A file whose containing reading for its course code is its own FILENAME.

    Two runs, exactly as a real scan has them, and the container path is what joins
    them. `extractors/filesystem.py` gives the filename "the run's single
    `container_path: ()` text unit" and reads it as one span over the whole name; a
    text extractor gives the document body a `()` unit of its own. So the two
    readings SERIALIZE TO THE SAME CONTAINER PATH, and
    `anchor_statements._containing_span_reading` compares spans within a path and
    asks nothing about the zone -- the filename's `[0, 22]` covers the body's
    `W3134`, and it is shorter than nothing else, so it wins and is recorded as the
    statement's line.

    Nothing here is contrived to produce the defect: the fixture is two extractors
    writing what they write, and the register measured the result on the owner's
    corpus.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    conn.executescript(SENSITIVITY_DDL)

    body = ANCHOR_BODY.encode()
    path = tmp_path / ANCHOR_FILENAME
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=ANCHOR_FILENAME,
        normalized_filename=ANCHOR_FILENAME, extension=".md",
        observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="text/markdown",
        detected_format="markdown", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]

    def _read(run_id, extractor, text, *, zone, raw, span):
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=extractor, extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
        record_text_unit(conn, TextUnit(run_id=run_id, container_path=(),
                                        text=text))
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name=extractor,
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location(zone, (), text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id)
        record_observation(conn, observation)
        return observation

    # The filesystem extractor's own reading of the name, over its own `()` unit.
    name = _read("run-fs", "filesystem", ANCHOR_FILENAME, zone="filename",
                 raw=ANCHOR_FILENAME,
                 span=TextSpan(0, len(ANCHOR_FILENAME)))
    start = ANCHOR_BODY.index("W3134")
    code = _read("run-md", "markdown.text", ANCHOR_BODY, zone="body",
                 raw="W3134", span=TextSpan(start, start + len("W3134")))

    record_anchor_statements(
        conn, scan_run_id="scan-r150", file_versions=[(file_id, content_hash)],
        is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)
    return file_id, name, code


def test_an_anchor_line_in_an_always_local_zone_is_never_offered(conn, tmp_path):
    """`104` R-150: the site-C dossier stops carrying an item that cannot leave.

    Measured on the same six-file stub corpus as R-149: the syllabus's site-C
    dossier carried `excerpt / filename / [0, 22] / possible` beside the fact item
    at the same address. Nothing leaked -- `releasable_excerpts` drops an
    always-local zone and the gate would refuse it again -- but the payload
    carried an item that was dead on arrival, and every such dossier was one item
    larger than what the model may be shown.

    The anchor loop now asks §8.4's always-local exclusion a step early, which is
    the pattern `releasable_excerpts` states for its own five: *"each is one of
    the gate's own refusals applied a step early, so the request is never BUILT
    rather than built and denied."*

    The statement itself is untouched. `facts.anchor_statements` still records the
    line it found -- what a document contains is P4's and P6's answer, not this
    site's -- and what changes is only what site C OFFERS.
    """
    import cli
    from facts.anchor_statements import anchor_statements_for

    file_id, name, code = _filename_line_corpus(conn, tmp_path)

    # The state the register measured: the statement's line IS the filename.
    statements = anchor_statements_for(conn, "scan-r150",
                                       stating_file_ids=(file_id,))
    assert [s.line_evidence_ref for s in statements] == [name.observation_key]

    assert cli.anchor_line_citations(
        conn, scan_run_id="scan-r150", file_id=file_id) == ()


def test_the_body_line_beside_it_is_still_offered(conn, tmp_path):
    """The twin that says R-150 is an exclusion and not a silencing.

    `104` R-135's whole point is that the judge sees the words beside the code, and
    a document whose containing reading is its own heading still hands that reading
    over. Only the zone §8.4 will never release is dropped.
    """
    import cli

    file_id, emitted = _anchor_corpus(conn, tmp_path)
    (whole, _code), = emitted

    lines = cli.anchor_line_citations(
        conn, scan_run_id="scan-r135", file_id=file_id)

    assert [ref for ref, _location, _reliability in lines] == [
        whole.observation_key]
    assert [location.zone for _ref, location, _r in lines] == ["heading"]


def test_a_document_that_states_no_course_offers_no_anchor_line(conn, tmp_path):
    """The empty case, and it is the one that says this is not a widening.

    ITS PREMISE CHANGED WITH THE RULE. It used to record the same syllabus heading and
    rely on the anchor-word gate refusing it for want of the word `syllabus` nearby.
    That gate is gone -- on the owner's corpus it refused all 106 readings that pass
    `is_code` -- so a heading printing a code IS a statement now, and the honest empty
    case is a document that prints no code at all.

    Nothing is offered for it, which is what says this reads the anchor table rather
    than handing every heading in the corpus to every judge.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    conn.executescript(SENSITIVITY_DDL)

    prose = "Reading list and office hours"
    path = tmp_path / "notes.pdf"
    path.write_bytes(prose.encode())
    file_id = record_file(
        conn, path, filename="notes.pdf", normalized_filename="notes.pdf",
        extension=".pdf", observed_size=len(prose.encode()),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="run-notes", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = (Segment("page", 1), Segment("heading", 1))
    record_text_unit(conn, TextUnit(
        run_id="run-notes", container_path=container, text=prose))
    record_observation(conn, Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=prose,
        location=Location("heading", container, text_span=TextSpan(0, len(prose))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-notes"))
    record_anchor_statements(
        conn, scan_run_id="scan-empty", file_versions=[(file_id, content_hash)],
        is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)

    assert cli.anchor_line_citations(
        conn, scan_run_id="scan-empty", file_id=file_id) == ()


# --------------------------------------------------------------------------
# Site A: the syllabus beside the file reaches the fact model, as CONTEXT
# --------------------------------------------------------------------------

#: The coursework file's own words. It names the course the way the person does and
#: never the way the label expects -- which is `104` R-135's whole finding: 35 of the
#: 43 files whose label carries a course name carry no code anywhere in their bytes.
COURSEWORK = "Data Structures, Homework 3: heaps and priority queues"


def _classified(conn, file_id, content_hash, *, refs, protected=False):
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore

    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="public_low", protected=protected, basis="detector",
        evidence_refs=tuple(refs), reliability_state="direct",
        observed_at=CLOCK))


def _folder_corpus(conn, tmp_path, *, coursework_folder="Courses/Data Structures",
                   syllabus_folder="Courses/Data Structures"):
    """A syllabus and a piece of coursework, in folders the caller chooses.

    The two folders are parameters because the containment rule is the thing under
    test: the same two files in sibling folders must produce nothing.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements
    from facts.fields import create_fields
    from privacy.schema import create_privacy_schema

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    conn.executescript(SENSITIVITY_DDL)

    def store(folder, name, text, *, zone, span, before, after, ordinal):
        path = tmp_path / folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode())
        file_id = record_file(
            conn, path, filename=name, normalized_filename=name.lower(),
            extension=".pdf", observed_size=len(text.encode()),
            observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
            parent_folder_context=folder, mime_type="application/pdf",
            detected_format="pdf", scan_state="included", materialized=True)
        content_hash = get_file(conn, file_id)["content_hash"]
        run_id = f"run-{name}"
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
        container = (Segment("page", 1), Segment("heading", ordinal))
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=container, text=text))
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=text,
            location=Location(zone, container, text_span=span),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=run_id, context_before=before, context_after=after)
        record_observation(conn, observation)
        _classified(conn, file_id, content_hash,
                    refs=(observation.observation_key,))
        return file_id, content_hash, observation

    syllabus, syllabus_hash, line = store(
        syllabus_folder, "syllabus.pdf", HEADING, zone="heading",
        span=TextSpan(0, len(HEADING)), before="Syllabus\n",
        after="\nInstructor: Dr Lacker", ordinal=1)
    # The identifier P4 finds inside the heading, over the same container path.
    code_start = HEADING.index("W3134")
    code = Observation(
        file_id=syllabus, content_hash=syllabus_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value="W3134",
        location=Location("heading", (Segment("page", 1), Segment("heading", 1)),
                          text_span=TextSpan(code_start, code_start + 5)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-syllabus.pdf",
        context_before=f"Syllabus\n{HEADING[:code_start]}",
        context_after=HEADING[code_start + 5:])
    record_observation(conn, code)

    homework, homework_hash, own = store(
        coursework_folder, "homework3.pdf", COURSEWORK, zone="body",
        span=TextSpan(0, 14), before="", after="", ordinal=1)

    record_anchor_statements(
        conn, scan_run_id="scan-r135",
        file_versions=[(syllabus, syllabus_hash), (homework, homework_hash)],
        is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)
    return dict(syllabus=syllabus, syllabus_hash=syllabus_hash, line=line,
                homework=homework, homework_hash=homework_hash, own=own)


def _prompt():
    from llm_harness.records import PromptDefinition
    from llm_harness.vocabulary import A_FACT

    return PromptDefinition(
        template_id="template.a_fact.r135", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site=A_FACT,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def _target():
    from privacy.release import ModelTarget

    return ModelTarget(locality="local", model_id="local-model",
                       provider="fixture")


def _fact_request(conn, world, context):
    """P6's request for the coursework file, carrying the context it was shown."""
    from facts.domains import ActivationSignal, ActivationSignals
    from facts.llm_seam import build_request

    return build_request(
        conn, file_id=world["homework"], content_hash=world["homework_hash"],
        activation_signals=ActivationSignals(signals=(
            ActivationSignal(schema_id="academic", activates=lambda rows: True),)),
        normalizers={}, context_observations=context)


def _site_a_dossier_with_context(request, world):
    """What P7 released for that call: the file's own reading, and the neighbour's.

    The neighbour's item carries `context-supported`, which is the single field
    `_acceptance_outcome` reads to decide the verdict under test.
    """
    from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
    from llm_harness.vocabulary import (
        A_FACT, CONTEXT_SUPPORTED, DIRECT_ANCHOR, REDUCTION_NONE,
        REMAINS_AMBIGUOUS,
    )

    own, line = world["own"], world["line"]
    return Dossier(
        dossier_id="dossier-r135-site-a", call_site=A_FACT,
        subject_ref=request.file_id, eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None, policy_version="policy-1",
        allowed_vocabulary=tuple(request.allowlist),
        evidence_items=(
            EvidenceItem(evidence_ref=own.observation_key, kind="excerpt",
                         location="body", excerpt_span=(0, 14),
                         reliability_state="possible", basis=DIRECT_ANCHOR),
            EvidenceItem(evidence_ref=line.observation_key, kind="excerpt",
                         location="heading", excerpt_span=(0, len(HEADING)),
                         reliability_state="possible", basis=CONTEXT_SUPPORTED)),
        conflicts=(),
        released_evidence=(
            ReleasedEvidence(observation_key=own.observation_key,
                             address="body:page=1/heading=1#0-14",
                             value=COURSEWORK[:14], zone="body",
                             unit_length=len(COURSEWORK)),
            ReleasedEvidence(observation_key=line.observation_key,
                             address=f"heading:page=1/heading=1#0-{len(HEADING)}",
                             value=HEADING, zone="heading",
                             unit_length=len(HEADING),
                             whole_heading_unit=True)),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE,
        release_id="rel-1")


def _context_for(conn, world, *, fields=("subject",)):
    import cli

    return cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"], fields=fields,
        limit=10, locality=CLOUD_LOCALITY)


def test_the_syllabus_beside_a_file_reaches_its_subject_call_as_context(
        conn, tmp_path):
    """`104` R-135 at site A, and it is the half no site-C fix can reach.

    The coursework file says `Data Structures` and no code; the code is printed once,
    on the syllabus in the same folder, and a `FactResolver` stage asked about one file
    version at a time can never see it. 19 of the owner's 43 labelled course codes came
    back missing for exactly that reason.

    The reading arrives as CONTEXT and is marked as one. `basis` is
    `context-supported`, the target names the syllabus so the gate will resolve its
    span, and the subject file is FIRST in that target because `Gate._decisive` reads
    `file_ids[0]` as the class the release is judged under.
    """
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    from model_facts import build_fact_request

    world = _folder_corpus(conn, tmp_path)
    context = _context_for(conn, world)
    assert [one.observation_key for one in context] == [
        world["line"].observation_key]

    request = _fact_request(conn, world, context)
    built = build_fact_request(
        request, (world["own"],), context=context,
        model_target=_target(), prompt=_prompt(), max_dossier_tokens=4000)

    carried = {item.evidence_ref: item for item in built.evidence_items}
    line_key = world["line"].observation_key
    assert carried[line_key].basis == CONTEXT_SUPPORTED
    assert carried[world["own"].observation_key].basis != CONTEXT_SUPPORTED
    assert line_key in {getattr(item, "observation_key", None)
                        for item in built.model_call_request.requested_items}
    # The subject file first, the stating file after it, and no third.
    assert built.model_call_request.target.file_ids == (
        world["homework"], world["syllabus"])


def test_a_code_cited_from_the_syllabus_validates_as_context_supported(
        conn, tmp_path):
    """The verdict, which is the assertion that says this is not a widening.

    A `subject` the model read off a NEIGHBOUR is accepted and it is accepted as
    `accept_context_supported`, so `_make_verdict` sets `requires_review` and the fact
    reaches a person rather than standing as if the file had said it itself. Check 2
    admits the citation because `FactRequest.context_observations` carries the reading;
    without that the claim is `CITATION_NOT_FOUND` and the model is shown evidence it
    is forbidden to cite, which is worse than showing it nothing.
    """
    from facts.llm_seam import Proposal
    from llm_harness.fact_validation import (
        FactValidationDependencies, validate_fact_proposal,
    )
    from llm_harness.records import Citation
    from llm_harness.vocabulary import ACCEPT_CONTEXT_SUPPORTED

    world = _folder_corpus(conn, tmp_path)
    context = _context_for(conn, world)
    request = _fact_request(conn, world, context)
    line_key = world["line"].observation_key

    dossier = _site_a_dossier_with_context(request, world)
    proposal = Proposal(field_key="subject", value="W3134",
                        citations=(line_key,), unknown=False)
    verdict = validate_fact_proposal(
        conn, request, proposal,
        dependencies=FactValidationDependencies(
            normalize=lambda field, raw: raw,
            contradicts=lambda proposal, row: False,
            normalize_for_review=None),
        model_identifier="local-model", prompt_fingerprint="fp-1",
        policy_version="policy-1", dossier=dossier,
        citations=(Citation(evidence_ref=line_key, cited_span="W3134",
                            metadata_field_name=None,
                            why_it_supports="the syllabus states the code"),),
        evidence_resolver=lambda key: HEADING,
        apply_consequence=False)

    assert verdict.outcome == ACCEPT_CONTEXT_SUPPORTED, verdict.reasons
    assert verdict.requires_review is True


def test_a_file_whose_folder_has_no_anchor_gets_no_context(conn, tmp_path):
    """Containment, and nothing looser. A syllabus in a SIBLING folder speaks for
    nothing here: `_folder_family` is the file's own folder and its ancestors, which is
    a fact the person created by filing the two apart. A resemblance rule would have
    matched these two on the words in their names, which is the second thing site C's
    prompt tells a model not to do.
    """
    world = _folder_corpus(
        conn, tmp_path,
        coursework_folder="Courses/Data Structures",
        syllabus_folder="Courses/Advanced Programming")

    assert _context_for(conn, world) == ()


def test_a_call_not_asking_the_field_gets_no_context(conn, tmp_path):
    """The narrowing that keeps this off every other call in the product.

    Which field a course code answers is `cli`'s, beside `SUBJECT_RULE` -- a call about
    `language` or `file_type` is handed nothing, so no other file's text joins a
    dossier that had no use for it and no target grows an id for nothing.
    """
    world = _folder_corpus(conn, tmp_path)

    assert _context_for(conn, world, fields=("language", "file_type")) == ()


def test_no_filename_and_no_path_ever_becomes_an_anchor(conn, tmp_path):
    """§8.4's members 1 and 6, and the reason this row could not have been built on
    them. The corpus below puts the course code in the FOLDER NAME and in the FILE
    NAME and nowhere in any document, which is the shape a resemblance rule would have
    loved. `reads_a_structured_string` admits a span inside `body` or `heading` only,
    so `filename`, `path`, `title` and every `metadata:*` zone are outside the anchor
    rule by construction and no statement is recorded at all.
    """
    import cli
    from facts.anchor_statements import anchor_statements_for
    from facts.fields import create_fields
    from evidence_shape.location import Segment as Seg

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    conn.executescript(SENSITIVITY_DDL)

    folder = tmp_path / "Courses" / "COMS W3134 Data Structures"
    folder.mkdir(parents=True)
    name = "COMS W3134 syllabus.pdf"
    path = folder / name
    path.write_bytes(b"nothing in the bytes names a course")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=34,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    record_run(conn, ExtractionRun(
        run_id="run-named", file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem", extractor_version="1.0.0",
        source_type="filesystem", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    for zone, value in (("filename", name), ("path", str(folder)),
                        ("title", "COMS W3134 Data Structures")):
        record_observation(conn, Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem", extractor_version="1.0.0",
            source_type="filesystem", raw_value=value,
            location=Location(zone, (Seg("field", label=zone),)),
            occurrence_count=1, observed_at=CLOCK, reliability="direct",
            run_id="run-named", context_before="Syllabus ", context_after=" 2026"))

    from facts.anchor_statements import record_anchor_statements

    record_anchor_statements(
        conn, scan_run_id="scan-r135", file_versions=[(file_id, content_hash)],
        is_code=lambda text: cli.SUBJECT_RULE.pattern.search(text) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)

    assert anchor_statements_for(conn, "scan-r135") == ()
    assert cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=file_id,
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY) == ()


# --------------------------------------------------------------------------
# The reuse cache has to see the anchor, or the fix above never runs twice
# --------------------------------------------------------------------------

def test_the_call_identity_moves_when_an_anchor_appears_beside_a_file(
        conn, tmp_path, monkeypatch):
    """`104` R-135's cache term, and without it this row's fix is inert on rerun.

    `call_identity_dimensions` reads exactly one term off the readings a call carries:
    `extractor_versions`, a SET of `(name, version)` pairs. A syllabus read by
    `pdf.text 1.0.0` beside coursework read by `pdf.text 1.0.0` adds nothing to that
    set -- so an identity computed over the union of the two observation lists is
    BYTE-IDENTICAL to the identity of the call that never saw the syllabus.

    `answered_fields` counts an abstention as an answer (`104` R-109), so the file whose
    prior verdict was `unknown` about `subject` -- which is the 19 missing course codes
    this row exists for -- would be reused on every later run and never shown the
    heading at all. `context_refs` is the term that makes the two calls two questions.

    `_policy_content` is monkeypatched: it reads a stored policy row and is a different
    term of the same digest. What is under test is that the context CHANGES the digest,
    and a policy fixture would not make that truer.
    """
    from types import SimpleNamespace

    import model_facts
    from llm_harness.store import CALL_IDENTITY_DIMENSIONS, call_identity

    world = _folder_corpus(conn, tmp_path)
    context = _context_for(conn, world)
    assert context, "the fixture must produce an anchor for this to mean anything"

    monkeypatch.setattr(model_facts, "_policy_content",
                        lambda _conn, _version: "{}")
    authorities = SimpleNamespace(
        model_target=_target(), policy_version="policy-1", prompt=_prompt(),
        activation_signals=SimpleNamespace(
            signals=(SimpleNamespace(schema_id="academic"),)))

    def dimensions(context_readings):
        return model_facts.call_identity_dimensions(
            conn, file_id=world["homework"],
            content_hash=world["homework_hash"], observations=(world["own"],),
            authorities=authorities, context=context_readings)

    without, with_anchor = dimensions(()), dimensions(context)

    assert "context_refs" in CALL_IDENTITY_DIMENSIONS
    assert without["context_refs"] == []
    assert with_anchor["context_refs"] == [world["line"].observation_key]
    # The KEYS and not a count: an observation key is content-addressed, so a different
    # heading, a re-extracted one, or one a later reading retracted is a different term.
    assert call_identity(without) != call_identity(with_anchor)
    # And the union that would NOT have worked, spelled out so the trap stays recorded.
    folded = model_facts.call_identity_dimensions(
        conn, file_id=world["homework"], content_hash=world["homework_hash"],
        observations=(world["own"],) + context, authorities=authorities)
    assert folded["extractor_versions"] == without["extractor_versions"]
    assert call_identity(folded) == call_identity(without)


def test_the_release_path_itself_sets_the_flag_the_counters_add_up(conn, tmp_path):
    """The end-to-end half, and without it the counters could quietly be zero again.

    `104` R-135's first defect was a field nothing populated. Moving the decision from
    report time to resolution time re-creates exactly that risk one layer down: if
    `materialise` never sets `whole_heading_unit`, every count is zero and every unit
    test above still passes, because those tests construct the flag themselves.

    So this one asks the REAL path. The heading, whose span covers the whole of a unit
    that is a heading, comes back `True`. The identifier inside it, which shares the
    heading's container path and is five characters of a twenty-seven character unit,
    comes back `False` -- the case a count taken over the container alone would get
    wrong.
    """
    from privacy.resolve import materialise

    file_id, emitted = _anchor_corpus(conn, tmp_path)
    (whole, code), = emitted

    offered = releasable_excerpts(
        conn, evidence_refs=[whole.observation_key, code.observation_key], locality=CLOUD_LOCALITY)
    by_key = {one.observation_key: materialise(conn, one, within_file_ids=(file_id,))
              for one in offered}

    assert by_key[whole.observation_key].whole_heading_unit is True
    assert by_key[whole.observation_key].value == HEADING
    assert by_key[code.observation_key].whole_heading_unit is False
    assert by_key[code.observation_key].value == "W3134"


def test_a_dossier_that_carried_context_survives_the_round_trip_out_of_its_row(conn):
    """`104` R-127's re-judgement, over a dossier `104` R-135 gave context to.

    `store.load_dossier` rebuilds a stored dossier and compares it against the row key
    by key, because "a record put back together with a field dropped would be judged
    against evidence the model was not shown". `record_dossier` stores every field of
    the record, so the two fields R-135 added to `ReleasedEvidence` were written and
    not read back, and the comparison refused.

    THE COST WAS NOT A LOST STATISTIC. `_reuse_is_current` answers `False` when the
    dossier will not rebuild, and `False` means the caller asks a model again. Every
    dossier recorded since R-135 carries those fields, so every validator change would
    have re-BOUGHT an answer this deployment already had -- which is R-127's whole
    point inverted. The guard was right and the rebuild was short.

    Both halves are asserted: the context item keeps `context-supported`, which is what
    makes the re-judgement reach `ACCEPT_CONTEXT_SUPPORTED` a second time, and the
    released item keeps the measurement and the classification the counters add up.
    """
    from database_agent.db import create_schema
    from llm_harness.records import Dossier, EvidenceItem, ReleasedEvidence
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import load_dossier, record_dossier
    from llm_harness.vocabulary import (
        A_FACT, CONTEXT_SUPPORTED, DIRECT_ANCHOR, REDUCTION_NONE,
        REMAINS_AMBIGUOUS,
    )

    create_schema(conn)
    create_llm_schema(conn)
    dossier = Dossier(
        dossier_id="dossier-r135-round-trip", call_site=A_FACT,
        subject_ref="file-1", eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None, policy_version="policy-1",
        allowed_vocabulary=("subject",),
        evidence_items=(
            EvidenceItem(evidence_ref="own", kind="excerpt", location="body",
                         excerpt_span=(0, 14), reliability_state="possible",
                         basis=DIRECT_ANCHOR),
            EvidenceItem(evidence_ref="line", kind="excerpt", location="heading",
                         excerpt_span=(0, len(HEADING)),
                         reliability_state="possible", basis=CONTEXT_SUPPORTED)),
        conflicts=(),
        released_evidence=(
            ReleasedEvidence(
                observation_key="line",
                address=f"heading:page=1/heading=1#0-{len(HEADING)}",
                value=HEADING, zone="heading", unit_length=len(HEADING),
                whole_heading_unit=True),),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE,
        release_id="rel-1")

    record_dossier(conn, dossier, observed_at=CLOCK)
    rebuilt = load_dossier(conn, dossier.dossier_id, release_id="rel-1")

    assert rebuilt.released_evidence == dossier.released_evidence
    assert rebuilt.evidence_items == dossier.evidence_items
    assert [item.basis for item in rebuilt.evidence_items] == [
        DIRECT_ANCHOR, CONTEXT_SUPPORTED]


def test_a_row_written_before_r135_still_rebuilds(conn):
    """The other half of reading them with a default, and it is the reason for it.

    A dossier recorded before these fields existed carries neither key. Refusing such a
    row would make an old database unreadable in order to say that a new field is
    absent from it -- which is the sentence `load_dossier` already writes about
    `folder_levels`. The absent case rebuilds as "no unit measured, not a heading
    unit", which is what those defaults mean everywhere else.
    """
    from llm_harness.dossier import dossier_from_stored_body

    body = {
        "dossier_id": "old", "call_site": "A_fact", "subject_ref": "file-1",
        "eligibility_reason": "remains_ambiguous", "plan_version": None,
        "policy_version": "policy-1", "allowed_vocabulary": ["subject"],
        "evidence_items": [{"evidence_ref": "own", "kind": "excerpt",
                            "location": "body", "excerpt_span": [0, 14],
                            "reliability_state": "possible",
                            "basis": "direct-anchor"}],
        "conflicts": [],
        "released_evidence": [{"observation_key": "own", "address": "0:14",
                               "value": "Data Structures", "zone": "body"}],
        "max_dossier_tokens": 4000, "reduction_rung": "none",
    }

    rebuilt = dossier_from_stored_body(body, release_id="rel-1")

    assert rebuilt.released_evidence[0].unit_length is None
    assert rebuilt.released_evidence[0].whole_heading_unit is False


def test_a_maximal_dossier_round_trips_and_survives_the_seeder_re_addressing(conn):
    """Every shape one site-A dossier can carry, through the row and back, and then
    through `104` R-137's own move on top of it.

    The two tests above pin the fields `104` R-135 added. This one pins the WHOLE
    record, because the failure they came from was not "a field is wrong" but "a
    rebuild named fewer fields than the row holds", and that mistake is invisible until
    some record grows. A filename item with no span, a span-less release, a conflict,
    a folder level, a measured heading unit and two items that are not one are all here
    so a future field lands on an assertion rather than on a run.

    THE SECOND HALF IS R-137's SEEDER. `tools/groundtruth/reuse.py` rewrites
    `subject_ref` in the stored body, rebuilds through this same
    `dossier_from_stored_body`, and re-addresses the result -- so a rebuild that drops
    a field costs a seeded corpus every answer it was seeded with. The rebuild after
    the swap is asserted to keep the classification and the measurement.
    """
    import json

    from database_agent.db import create_schema
    from llm_harness.dossier import dossier_from_stored_body
    from llm_harness.records import (
        Conflict, Dossier, EvidenceItem, FolderLevel, ReleasedEvidence,
    )
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import _jsonable, load_dossier, record_dossier
    from llm_harness.vocabulary import (
        A_FACT, CONTEXT_SUPPORTED, DIRECT_ANCHOR, REDUCTION_NONE,
        REMAINS_AMBIGUOUS,
    )

    create_schema(conn)
    create_llm_schema(conn)
    dossier = Dossier(
        dossier_id="dossier-r135-maximal", call_site=A_FACT,
        subject_ref="file-1", eligibility_reason=REMAINS_AMBIGUOUS,
        plan_version=None, policy_version="policy-1",
        allowed_vocabulary=("subject", "work_type"),
        evidence_items=(
            EvidenceItem(evidence_ref="name", kind="filename",
                         location="filename", excerpt_span=None,
                         reliability_state="direct", basis=DIRECT_ANCHOR),
            EvidenceItem(evidence_ref="own", kind="excerpt", location="body",
                         excerpt_span=(0, 14), reliability_state="possible",
                         basis=DIRECT_ANCHOR),
            EvidenceItem(evidence_ref="line", kind="excerpt", location="heading",
                         excerpt_span=(0, len(HEADING)),
                         reliability_state="possible", basis=CONTEXT_SUPPORTED)),
        conflicts=(Conflict(conflict_id="c1", kind="different_term"),),
        released_evidence=(
            ReleasedEvidence(observation_key="name",
                             address="filename:field=name", value="hw3.pdf",
                             zone="filename"),
            ReleasedEvidence(observation_key="own", address="body:page=1#0-14",
                             value=COURSEWORK[:14], zone="body",
                             unit_length=len(COURSEWORK)),
            ReleasedEvidence(observation_key="line",
                             address=f"heading:page=1/heading=1#0-{len(HEADING)}",
                             value=HEADING, zone="heading",
                             unit_length=len(HEADING), whole_heading_unit=True)),
        max_dossier_tokens=4000, reduction_rung=REDUCTION_NONE,
        release_id="rel-1",
        folder_levels=(FolderLevel(field="subject", label="Course",
                                   requirement="required"),))

    record_dossier(conn, dossier, observed_at=CLOCK)
    stored = json.loads(conn.execute(
        "SELECT payload FROM llm_dossier WHERE dossier_id = ?",
        (dossier.dossier_id,)).fetchone()["payload"])
    rebuilt = _jsonable(dossier_from_stored_body(stored, release_id="rel-1"))

    # Key by key, which is the comparison `load_dossier` makes and the one a short
    # rebuild fails. Named rather than counted, so a failure says WHICH field.
    assert [name for name, value in stored.items()
            if rebuilt.get(name) != value] == []
    assert load_dossier(conn, dossier.dossier_id, release_id="rel-1") is not None

    # R-137's move: the seeder swaps the subject and rebuilds through this function.
    swapped = dict(stored, subject_ref="file-translated")
    seeded = dossier_from_stored_body(swapped, release_id="rel-1")

    assert seeded.subject_ref == "file-translated"
    assert seeded.released_evidence == dossier.released_evidence
    assert seeded.evidence_items == dossier.evidence_items


# --------------------------------------------------------------------------
# The minted line, and the fallback, reaching a neighbour's subject call
# --------------------------------------------------------------------------

#: A schedule as a `.txt` is read: one body unit, one span-less whole reading, and the
#: span the structured-string pass found inside it. `104` R-135's second measurement
#: says this is 91 of the corpus's 99 statements and the PDF heading shape is 8.
SCHEDULE = "Autumn term\nCOMS W3134 Data Structures\nMeets Tuesdays at 10:10\n"


def _body_neighbour(conn, tmp_path, *, text=SCHEDULE,
                    folder="Courses/Data Structures", protected_stating=False,
                    code="W3134", coursework=None):
    """A body-shaped stating file beside a piece of coursework, both classified.

    `code` is the reading the structured-string pass found inside `text`, and
    `coursework` the neighbour's own body. Both are the caller's for the same reason
    the span is stated rather than parsed: this fixture must not hold a second
    implementation of the recogniser. `104` R-146 added the callers that pass them.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements
    from facts.fields import create_fields
    from privacy.schema import create_privacy_schema

    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    conn.executescript(SENSITIVITY_DDL)

    def store(name, body, *, spanned, protected=False):
        path = tmp_path / folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body.encode())
        file_id = record_file(
            conn, path, filename=name, normalized_filename=name.lower(),
            extension=Path(name).suffix, observed_size=len(body.encode()),
            observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
            parent_folder_context=folder, mime_type="text/plain",
            detected_format="txt", scan_state="included", materialized=True)
        content_hash = get_file(conn, file_id)["content_hash"]
        run_id = f"run-{name}"
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=(), text=body))

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

        whole = observe(body, None)
        reading = None
        if spanned:
            start = body.index(code)
            reading = observe(code, TextSpan(start, start + len(code)))
        # ONE live record per file version: `ClassificationStore.strongest` refuses
        # two at one reliability, so the protected case is built here rather than
        # written over an ordinary one.
        _classified(conn, file_id, content_hash, refs=(whole.observation_key,),
                    protected=protected)
        return file_id, content_hash, whole, reading

    stating, stating_hash, _whole, found = store(
        "schedule.txt", text, spanned=True, protected=protected_stating)
    homework, homework_hash, own, _none = store(
        "homework3.txt", (coursework or COURSEWORK) + "\n", spanned=False)

    record_anchor_statements(
        conn, scan_run_id="scan-r135",
        file_versions=[(stating, stating_hash), (homework, homework_hash)],
        is_code=lambda one: cli.SUBJECT_RULE.pattern.search(one) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)
    return dict(stating=stating, code=found, homework=homework,
                homework_hash=homework_hash, own=own)


def test_the_excerpt_shape_names_each_anchors_own_span(conn, tmp_path):
    """`104` R-145: the same offer, in §8.6's preserved-anchors shape.

    A `.docx` paragraph or a page of PDF text is one newline-delimited segment, and
    `line_reading_for` reads it back as one LINE -- 27,510 characters on the owner's
    corpus, in a dossier whose ceiling is 4,000. The excerpt shape offers the code's
    own span instead: same statement, same stating file, same release check, and the
    model still sees which course the folder states.
    """
    import cli

    paragraph = ("Course policies. " * 300 + "COMS W3134 Data Structures. "
                 + "Late work is not accepted. " * 100)
    assert "\n" not in paragraph and len(paragraph) > 4000
    world = _body_neighbour(conn, tmp_path,
                            text="Autumn term\n" + paragraph + "\nMeets Tuesdays\n")

    lines = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)
    excerpts = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, preserved_anchors=True, locality=CLOUD_LOCALITY)

    assert len(lines) == 1 and lines[0].raw_value == paragraph
    assert len(excerpts) == 1
    assert excerpts[0].raw_value == "W3134"
    assert excerpts[0].observation_key == world["code"].observation_key
    assert excerpts[0].file_id == world["stating"]


def _body_neighbour_extra(conn, tmp_path, *, name, text,
                          folder="Courses/Data Structures"):
    """A SECOND stating file in the same folder, so "which anchor" is a real question.

    Returns its file id. The corpus is re-recorded for this file alone, which is what
    `record_anchor_statements` does per version anyway.
    """
    import cli
    from facts.anchor_statements import record_anchor_statements

    path = tmp_path / folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode())
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(text.encode()),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=folder, mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = f"run-{name}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="text.structured", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
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
    start = text.index("E1006")
    observe("E1006", TextSpan(start, start + 5))
    _classified(conn, file_id, content_hash, refs=(whole.observation_key,))
    record_anchor_statements(
        conn, scan_run_id="scan-r135", file_versions=[(file_id, content_hash)],
        is_code=lambda one: cli.SUBJECT_RULE.pattern.search(one) is not None,
        canonical=cli.SUBJECT_RULE.canonical,
        reads_in_document=cli.reads_a_structured_string)
    return file_id


def test_a_minted_line_is_releasable_and_reaches_a_neighbours_subject_call(
        conn, tmp_path):
    """`104` R-135's second blocker, end to end and on the shape that is 91 of 99.

    Before the minting the measured run was unambiguous: `anchor_statements` held 99
    rows from 40 files, the first 18 fresh `A_fact` dossiers all sat in folders holding
    a stating file, 15 of them asked `subject`, and not one carried a context item --
    125 released items, every one `direct-anchor`. `_containing_span_reading` had no
    span-bearing sibling to find in a `.txt` body, so 91 statements carried no line and
    `anchor_context_observations` skipped every one.

    Three things are asserted because three could each break it alone: the minted
    reading survives `releasable_observations` (it is a span inside a body unit, so the
    whole-unit refusal does not touch it), it reaches the neighbour's dossier, and it
    arrives marked `context-supported` with the stating file in the target so P7 will
    resolve it.
    """
    import cli
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    from model_facts import build_fact_request, releasable_observations
    from privacy.resolve import materialise

    world = _body_neighbour(conn, tmp_path)
    context = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)

    assert len(context) == 1
    minted = context[0]
    assert minted.raw_value == "COMS W3134 Data Structures"
    assert minted.file_id == world["stating"]

    # It is releasable in its own right, which is the step that used to be untestable
    # because nothing ever produced the reading.
    offered = releasable_observations(
        conn, file_id=world["stating"],
        content_hash=get_file(conn, world["stating"])["content_hash"], limit=20, locality=CLOUD_LOCALITY, ceiling=A_CEILING)
    assert minted.observation_key in {one.observation_key for one in offered}

    request = _fact_request(conn, world, context)
    built = build_fact_request(
        request, (world["own"],), context=context,
        model_target=_target(), prompt=_prompt(), max_dossier_tokens=4000)
    carried = {item.evidence_ref: item for item in built.evidence_items}

    assert carried[minted.observation_key].basis == CONTEXT_SUPPORTED
    assert built.model_call_request.target.file_ids == (
        world["homework"], world["stating"])
    # And what the model would actually read is the line, not the five characters.
    from privacy.items import Excerpt

    released = materialise(
        conn, Excerpt(observation_key=minted.observation_key,
                      span=minted.location.text_span, reason="context"),
        within_file_ids=(world["stating"],))
    assert released.value == "COMS W3134 Data Structures"


def test_when_no_line_can_be_minted_the_code_span_is_offered_instead(
        conn, tmp_path):
    """The fallback, and it is offered rather than skipped for a measured reason.

    Skipping is what the loop used to do, and it skipped 91 statements of 99. When the
    line would carry the code's own characters -- here the schedule prints the code on a
    line by itself -- there is nothing to mint, and the code's span is what the corpus
    has. A code beside a neighbouring file is less than a line, and it is more than the
    nothing this path delivered on every file of the measured run.
    """
    import cli

    world = _body_neighbour(
        conn, tmp_path, text="Autumn term\nW3134\nMeets Tuesdays at 10:10\n")
    context = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in context] == [
        world["code"].observation_key]
    assert context[0].raw_value == "W3134"


# --------------------------------------------------------------------------
# `104` R-146: the same path for a course the recogniser could not see
# --------------------------------------------------------------------------

#: The shape R-146 measured on the owner's disk: a syllabus that prints its course as
#: a capitalised word, a space and four digits, beside `Instructor:`. Under the
#: uppercase-only recogniser that shipped until 2026-09-08 this text produced no code
#: reading, so no anchor statement, so nothing on this path at all -- which is R-146's
#: finding stated as a mechanism: of 43 labelled files, the label's subject is stated
#: by a recognised anchor in the file's own folder family for NONE, and the model then
#: copied the only anchor sharing the digits onto 9 of its 19 `subject` answers.
WORD_SCHEDULE = ("Spring 2026\nPhysics 1401 Introductory Mechanics\n"
                 "Instructor: Dr. Lee. Credits: 3.\n")
WORD_COURSEWORK = "Introductory Mechanics, Homework 3: rotational dynamics"


def test_a_course_printed_as_a_word_reaches_its_neighbour_as_context(conn, tmp_path):
    """`104` R-146, end to end on the path R-135 built: read, state, carry.

    Nothing on this path changed for it to work. `record_anchor_statements` takes the
    same `is_code` and the same `canonical`, `anchor_context_observations` runs the
    same query, and what the neighbour is offered is the stating document's own
    sentence -- `Physics 1401 Introductory Mechanics`, not the four digits and not a
    name this repo invented for the course. The one thing that moved is upstream of
    all of it: the recogniser now produces a reading for the line.

    The homework file states no code of its own, which is the case the path is FOR:
    a piece of coursework that says what it is about in words, in a folder whose
    syllabus says what the course is called.
    """
    import cli
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    from model_facts import build_fact_request

    # The premise, measured against the shipped recogniser rather than assumed: two
    # readings, the term first because `find_structured_strings` takes its spans first.
    assert [WORD_SCHEDULE[one.start:one.end]
            for one in cli.find_structured_strings(WORD_SCHEDULE)] == [
        "Spring 2026", "Physics 1401"]

    world = _body_neighbour(conn, tmp_path, text=WORD_SCHEDULE,
                            folder="Courses/Introductory Mechanics",
                            code="Physics 1401", coursework=WORD_COURSEWORK)
    context = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)

    assert len(context) == 1
    minted = context[0]
    assert minted.raw_value == "Physics 1401 Introductory Mechanics"
    assert minted.file_id == world["stating"]

    request = _fact_request(conn, world, context)
    built = build_fact_request(
        request, (world["own"],), context=context,
        model_target=_target(), prompt=_prompt(), max_dossier_tokens=4000)
    carried = {item.evidence_ref: item for item in built.evidence_items}

    assert carried[minted.observation_key].basis == CONTEXT_SUPPORTED
    assert built.model_call_request.target.file_ids == (
        world["homework"], world["stating"])


# --------------------------------------------------------------------------
# The release check is asked of the READINGS, not of the stating file's ranking
# --------------------------------------------------------------------------

def _crowd(conn, file_id, content_hash, *, count):
    """`count` more readings of the stating file, every one ranked ABOVE a body line.

    `title` is first in `model_facts._ZONE_PREFERENCE` and `body` is fourth, so these
    fill the head of that file's own ranking. The point of the fixture is that they are
    perfectly ordinary readings: nothing here is unreleasable, and nothing about them
    says anything about the line.
    """
    for index in range(count):
        value = f"Reading {index} of this document"
        container = (Segment("field", label=f"note-{index}"),)
        record_text_unit(conn, TextUnit(
            run_id="run-schedule.txt", container_path=container,
            text=value + " and more besides"))
        record_observation(conn, Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="1.0.0",
            source_type="text_document", raw_value=value,
            location=Location("title", container,
                              text_span=TextSpan(0, len(value))),
            occurrence_count=1, observed_at=CLOCK, reliability="direct",
            run_id="run-schedule.txt"))


def test_a_minted_line_survives_a_stating_file_whose_own_ranking_is_full(
        conn, tmp_path):
    """`104` R-135's third defect, and the code read as though it were doing right.

    The builder collected the line keys it wanted and then kept only those that also
    appeared in `releasable_observations(file_id=<the stating file>, limit=12, locality=CLOUD_LOCALITY, ceiling=A_CEILING)` -- that
    file's OWN ranked, capped dossier. A minted body line is `possible` reliability in
    the `body` zone and never reaches a syllabus's top twelve, so it was dropped for
    losing a competition it was never in. Measured over the first 9 files asked on r9:
    120 statements refused as "line not among releasable", and 7 of those 9 files ended
    with no context at all, while nothing about the readings was unreleasable.

    Here the stating file carries twenty `title` readings, all ranked above `body`, so
    the line is far outside its own top twelve. It is offered anyway, because the
    question asked of it is "may this reading be released", not "did it place".
    """
    import cli
    from model_facts import releasable_observations

    world = _body_neighbour(conn, tmp_path)
    stating_hash = get_file(conn, world["stating"])["content_hash"]
    _crowd(conn, world["stating"], stating_hash, count=20)

    # The premise, measured rather than assumed: the line really is off the ranking.
    ranked = releasable_observations(
        conn, file_id=world["stating"], content_hash=stating_hash, limit=12, locality=CLOUD_LOCALITY, ceiling=A_CEILING)
    context = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)

    assert len(context) == 1
    assert context[0].raw_value == "COMS W3134 Data Structures"
    assert context[0].observation_key not in {
        one.observation_key for one in ranked}


def test_a_line_in_a_protected_stating_file_is_still_refused(conn, tmp_path):
    """The gate's refusal that did NOT move, and the reason it is asked per FILE.

    The target gains the stating file's id, so `Gate._decisive` classifies it and a
    protected neighbour denies the fact call of an unrelated file beside it. Asking the
    release question of the readings does not widen that by an inch: a protected file
    contributes nothing, whatever its readings look like.
    """
    import cli

    world = _body_neighbour(conn, tmp_path, protected_stating=True)

    assert cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY) == ()


def test_a_whole_body_line_is_refused_and_a_heading_is_released(conn, tmp_path):
    """The whole-unit rule and `104` R-135's exemption, both intact under the new call.

    `releasable_readings` runs the same four exclusions as `releasable_observations`,
    so a span covering a whole MULTI-LINE `body` unit is still a full document and
    refused, and a span covering a whole `heading` unit is still the thing §8.4 names
    as what to send instead. Asked of named readings rather than of a ranking, which is
    the only thing that changed.

    THE PROSE GAINED ITS LINE BREAKS FOR `104` R-152, for the reason the whole-body
    test above gives: a 54-character single line is a line, §8.4's short excerpt, and
    is released now. This test is about the DOCUMENT, so it uses one.
    """
    from model_facts import releasable_readings

    file_id, emitted = _anchor_corpus(conn, tmp_path)
    (whole, code), = emitted
    content_hash = get_file(conn, file_id)["content_hash"]

    page = (Segment("page", 2),)
    prose = ("A whole page of this document, which is not a heading.\n"
             "It runs to a second line, the way a page of prose does.")
    record_text_unit(conn, TextUnit(
        run_id="run-anchor", container_path=page, text=prose))
    body = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=prose,
        location=Location("body", page, text_span=TextSpan(0, len(prose))),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id="run-anchor")
    record_observation(conn, body)

    offered = releasable_readings(
        conn, file_id=file_id, content_hash=content_hash,
        keys=[body.observation_key, whole.observation_key,
              code.observation_key], locality=CLOUD_LOCALITY)

    assert [one.observation_key for one in offered] == [
        whole.observation_key, code.observation_key]


def test_the_cap_bounds_the_context_items_and_not_the_candidates(conn, tmp_path):
    """The cap is on what this call SENDS, which is what a release cap is for.

    Two stating files in the folder, each with a line to offer. At `limit=1` exactly one
    context item arrives -- not one per file, and not one per file's ranking. The one
    that arrives is the first in the product's own zone preference and then in the order
    `anchor_statements_for` recorded, which is `104` R-135's whole answer to "which
    anchor": nothing here prefers a nearer folder or a shorter path, because which
    anchor names this file's course is the model's judgement.
    """
    import cli

    world = _body_neighbour(conn, tmp_path)
    second = _body_neighbour_extra(
        conn, tmp_path, name="handbook.txt",
        text="Programme handbook\nENGI E1006 Introduction to Computing\nPage 2\n")

    uncapped = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=10, locality=CLOUD_LOCALITY)
    capped = cli.anchor_context_observations(
        conn, scan_run_id="scan-r135", file_id=world["homework"],
        fields=("subject",), limit=1, locality=CLOUD_LOCALITY)

    assert len(uncapped) == 2
    assert {one.file_id for one in uncapped} == {world["stating"], second}
    assert len(capped) == 1
    assert capped[0].observation_key == uncapped[0].observation_key

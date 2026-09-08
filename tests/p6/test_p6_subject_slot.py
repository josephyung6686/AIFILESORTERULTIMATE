# tests/p6/test_p6_subject_slot.py
"""The shipped `subject` slot, against the readings a real disk actually produces.

Measured on the owner's own Downloads, 54 files, run `academic.coursework`: the
`fields` catalogue declares 56 fields and exactly two ever took a value. One of the
two was `subject`, with 196 distinct values across 18 files -- eleven "subjects" per
document -- and the values were `!`, `&`, `-`, `(i)`, `* DIEI ==outcomes in E` and
`#corre 1 . 4 - 1 : 4 . 10 - 4`. A probability lecture was reporting punctuation as
what it is about.

**Where they came from, exactly.** `cli.reads_a_structured_string` admits a locator
whose zone is `body` or `heading` and which carries a `#` span. Its docstring states
the invariant that bound is meant to rest on: "A structured string always carries a
span because it is a substring the pass located; a whole zone never does." That
sentence is FALSE for one emitter. `extractors.pdf.extract_pdf` builds its heading
`_Candidate` with an explicit `span={"start": 0, "end": len(heading_text)}` -- every
heading REGION is emitted as an observation of the whole region -- so a whole heading
arrives looking exactly like a located substring, while the whole-page `text_unit`
built two statements earlier carries no span at all. Of the 158 heading-zone
observations in that run, all 158 were whole regions; of the 77 body-zone spans, 76
were located substrings. The zone list was not the defect and narrowing it is not the
fix: the same function's `zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, region.zone
...)` gives an identifier FOUND INSIDE a heading `zone="heading"` too, so dropping the
zone would throw away the course code printed in a slide title -- `00`:78's own worked
example.

**So the refusal belongs to the slot's `matches` predicate, over the READING.** The
slot is `cli.text.identifier` and its declared claim is "the identifier the
structured-string pass found in the document's text". This deployment authors exactly
one definition of an identifier, `cli._STRUCTURED`, and a located structured string's
raw value IS its match -- `extract_pdf` slices it, `raw = unit_text[start:end]`. A
reading that the deployment's own pattern would not have produced is not an
identifier, and a slot that stores it is claiming a reading it never made. No
threshold is invented here and no vocabulary is added: the test asks the shipped
pattern about the shipped readings.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import cli

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file
from facts.values import values_in_field

CLOCK = "2026-08-19T12:00:00+00:00"

#: Six of the values the measured run stored in `subject`, byte-exact from the run
#: database, beside the two readings that belong there. The pairing is the point: one
#: predicate has to refuse the left column while admitting the right.
LAYOUT_DEBRIS: tuple[str, ...] = (
    "!", "&", "-", "(i)", "* DIEI ==outcomes in E", "#corre 1 . 4 - 1 : 4 . 10 - 4")

#: Whole headings from the same run. Prose, correctly read, and still not a subject:
#: a slide titled `AUDIENCES IN GA4` is not a document ABOUT an identifier, and
#: `cli.py`'s own record of the whole-zone failure is a proposed folder named
#: "Fudan application checklist [x] transcript [x] personal statement [ ]".
WHOLE_HEADINGS: tuple[str, ...] = (
    "AUDIENCES IN GA4", "ADVERTISING REPORTS", "Addition principle-",
    "Analytics with google analytics 4 (ga4)")

#: Readings the same run produced that ARE identifiers, from `body` spans. These must
#: survive: refusing the noise by refusing everything would be the other failure.
#:
#: `I 1403` WAS A FOURTH ROW AND LEFT ON 2026-09-05. It is still an identifier by
#: SHAPE -- `cli._STRUCTURED` reads it, which is what this file is about, and
#: `test_the_deployment_still_reads_every_identifier_it_ever_read` holds that shut
#: -- but the `subject` RULE now refuses a lone leading capital as a fragment of
#: something longer (`General Chemistry I 1403`), so it can no longer stand here as
#: a reading the pass turns into a fact. `BOEING 777` carries the canonicaliser
#: half of the row's job unchanged. See
#: `tests/p6/test_p6_subject_rule.py::test_a_partial_identifier_is_refused_rather_than_stored`.
IDENTIFIERS: tuple[str, ...] = ("UARF470911", "UA872", "BOEING 777")


def _file(conn, tmp_path, *, name="lecture.pdf", body=b"a probability lecture"):
    path = tmp_path / "Downloads" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _whole_heading(conn, *, run_id, file_id, content_hash, raw, page, ordinal):
    """P4's heading-region observation, in `extractors.pdf.extract_pdf`'s own shape.

    The span is `0 .. len(raw)` because that is what the emitter writes, and it is
    the whole reason this reading reaches a slot that believes it only sees
    substrings.
    """
    return _record(conn, run_id=run_id, file_id=file_id, content_hash=content_hash,
                   raw=raw, zone="heading",
                   container_path=(Segment("page", index=page),
                                   Segment("heading", index=ordinal, label=raw)),
                   span=TextSpan(0, len(raw)))


def _located_string(conn, *, run_id, file_id, content_hash, raw, page, start):
    """P4's structured-string observation: a substring the finder located on a page."""
    return _record(conn, run_id=run_id, file_id=file_id, content_hash=content_hash,
                   raw=raw, zone="body",
                   container_path=(Segment("page", index=page),),
                   span=TextSpan(start, start + len(raw)))


def _record(conn, *, run_id, file_id, content_hash, raw, zone, container_path, span,
            before="", after=""):
    """P4's observation. `before`/`after` are §2.8's context pair, empty by default.

    They gained a default rather than a caller on every call site: a reading with no
    context is what most of this file is about, and §3.5's rule refuses one -- which
    is the same answer the removed slot's `matches` predicate gave for the readings
    that mattered here, reached by a producer that says WHY in an `unresolved` row.
    """
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="0.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="0.1.0", source_type="text_document", raw_value=raw,
        location=Location(zone, container_path, text_span=span),
        occurrence_count=1, observed_at=CLOCK, reliability="possible", run_id=run_id,
        context_before=before, context_after=after)
    record_observation(conn, observation)
    return observation


def _subjects(conn, file_id, content_hash) -> set[str]:
    """What the shipped deterministic pass put in `subject`, as values.

    BOTH stages, since 2026-09-04. The slot this file is named after is gone --
    `cli.DIRECT_SLOTS` is empty and `subject` is filled by `cli.SUBJECT_RULE`
    through §3.5's context check -- so a helper that ran only the direct stage
    would now answer "nothing" for every case here and prove nothing at all.
    `tests/p6/test_p6_subject_rule.py` holds the reason the slot was removed; what
    this file still proves is that the READINGS a real disk produces are handled
    the way its measurements say they must be, and that the model seam agrees with
    whichever producer is shipped.
    """
    cli._direct_stage(conn, file_id=file_id, content_hash=content_hash)
    cli._rule_stage(conn, file_id=file_id, content_hash=content_hash)
    by_id = {row["value_id"]: row["canonical_value"]
             for row in values_in_field(conn, "subject")}
    return {by_id[row["value_id"]]
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == "subject"}


def test_layout_debris_in_a_pdf_heading_is_not_a_subject(p6_conn, tmp_path):
    """The measured failure, reproduced from the six values the run actually stored.

    Each of these arrives as `heading:page=N/heading=M#0-K` with `K == len(raw)`,
    which is what `pdf.py` writes for a heading REGION. `reads_a_structured_string`
    admits it, `matches` only asked whether it was a term, and `direct_facts` writes
    `direct` unconditionally (§3.5 names a location and applies no test to the
    reading) -- so a punctuation mark became the strongest state P6 can state about
    what a document is about, and then a candidate folder name.
    """
    file_id, content_hash = _file(p6_conn, tmp_path)
    for ordinal, raw in enumerate(LAYOUT_DEBRIS, start=1):
        _whole_heading(p6_conn, run_id=f"run-debris-{ordinal}", file_id=file_id,
                       content_hash=content_hash, raw=raw, page=1, ordinal=ordinal)

    assert _subjects(p6_conn, file_id, content_hash) == set(), (
        "punctuation and layout debris were stored as what a lecture is ABOUT; "
        "the deployment's own identifier pattern would never have produced them")


def test_a_whole_heading_is_not_a_subject_even_when_it_reads_as_prose(
        p6_conn, tmp_path):
    """The half that is not obviously broken, and is broken the same way.

    `AUDIENCES IN GA4` is a real slide title, read correctly. It is still a whole
    zone, and `cli.py` already records what a slot fed a whole zone proposes: a
    folder named "Fudan application checklist [x] transcript [x] personal statement
    [ ] recommendation [ ] HSK certificate". The refusal has to be the same one, or
    the noise comes back the moment a deck has clean headings.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="deck.pdf",
                                  body=b"a marketing deck")
    for ordinal, raw in enumerate(WHOLE_HEADINGS, start=1):
        _whole_heading(p6_conn, run_id=f"run-heading-{ordinal}", file_id=file_id,
                       content_hash=content_hash, raw=raw, page=2, ordinal=ordinal)

    assert _subjects(p6_conn, file_id, content_hash) == set()


def test_the_identifiers_the_pass_located_are_not_subjects_by_being_identifiers(
        p6_conn, tmp_path):
    """THIS TEST ASSERTED THE DEFECT, and the file it belongs to is why.

    It used to require that all four of these become `subject` facts, on the
    argument that "refusing everything would be the other way to be wrong". The
    argument is right and the example was the bug: these four came off a FLIGHT
    MANIFEST. `UARF470911` is a United booking reference, `UA872` a flight number
    and `BOEING 777` an aircraft type, and the run that produced them proposed
    folders named after all three. Measured against the hand-made labels, the
    producer that claimed them was 0 correct and 14 wrong.

    The shape cannot separate them and this test no longer pretends it can. What
    separates them is the document they sit in, so that is what is asked here.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="manifest.pdf",
                                  body=b"a flight manifest")
    for index, raw in enumerate(IDENTIFIERS):
        _located_string(p6_conn, run_id=f"run-id-{index}", file_id=file_id,
                        content_hash=content_hash, raw=raw, page=1, start=index * 40)

    assert _subjects(p6_conn, file_id, content_hash) == set()


def test_refusing_them_is_not_refusing_everything(p6_conn, tmp_path):
    """The negative twin, kept, and its answer moved on 2026-09-08.

    The same three readings, in a document that describes a course instead of a
    flight. This asserted that all three become `subject` facts, and said so
    honestly: "`BOEING777` under the word `syllabus` IS a subject here. The rule
    has no vocabulary of plausible course codes ... so it cannot know an aircraft
    from a course by looking at it."

    **`104` R-37's principle one layer down says it never had to.** Three DISTINCT
    canonical values for one field on one file version is not a resolution --
    §3.7 settles on none of them and the level disappears with no row saying why --
    so `apply_rules` now declines and records one `unresolved` row per candidate,
    each citing its own reading. The document then reaches the model with all three
    of its readings, and the model, which can read the words around them, decides.
    That is the constitution's answer to the question the shape cannot ask: a
    curated department list was rejected twice and could not answer for a
    university nobody told it about, and nothing here needs one.

    **The half that was always true is still true and is why this test survives.**
    Refusing everything would be the other way to be wrong, and the rule does not:
    a document offering ONE course still gets it as a `validated` fact with no
    model involved, which `tests/p6/test_p6_subject_rule.py` holds. What changed is
    only what happens when a file offers several, and the difference between "no
    fact" here and "no fact" in the flight-manifest test above is the ROW: this
    file's refusal names three candidates and hands them on, that one's names none.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="outline.pdf",
                                  body=b"a course outline")
    for index, raw in enumerate(IDENTIFIERS):
        _record(p6_conn, run_id=f"run-ctx-{index}", file_id=file_id,
                content_hash=content_hash, raw=raw, zone="body",
                container_path=(Segment("page", index=1),),
                span=TextSpan(index * 40, index * 40 + len(raw)),
                before="Syllabus - ", after=", 3 credits.")

    assert _subjects(p6_conn, file_id, content_hash) == set()

    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="subject")
    assert sorted(row["reason"] for row in rows) == [
        "rule_found_several_values"] * 3
    # Three candidates, three citations, so the handoff names what it could not
    # choose between rather than reporting a bare silence.
    cited = {ref for row in rows for ref in json.loads(row["evidence_refs"])}
    assert len(cited) == 3


def test_an_identifier_printed_inside_a_heading_survives_the_refusal(
        p6_conn, tmp_path):
    """Why the refusal is not "drop the `heading` zone", stated as a test.

    `extractors.pdf.extract_pdf`'s `for found in find_structured_strings(page.text)`
    loop: a structured string found inside a heading region
    keeps the heading's container AND takes the heading's zone, because
    `ZONE_BY_STRUCTURED_KIND` names no zone for an `identifier` and the fallback is
    the region's own. So `heading:page=1/heading=3#9-18` is a LOCATED SUBSTRING in
    the heading zone -- a course code in a slide title, which is `00`:78's own
    recommended tree (`Academics/Columbia/2026-Spring/PHYS1401/Homework`).

    Narrowing `_TEXT_ZONES` to `body` would have cleaned the measured noise and
    thrown this away with it.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="syllabus.pdf",
                                  body=b"a syllabus")
    heading = "Homework: PHYS 1401, week 3 -- lecture slides"
    start = heading.index("PHYS 1401")
    _record(p6_conn, run_id="run-in-heading", file_id=file_id,
            content_hash=content_hash, raw="PHYS 1401", zone="heading",
            container_path=(Segment("page", index=1),
                            Segment("heading", index=3, label=heading)),
            span=TextSpan(start, start + len("PHYS 1401")),
            before=heading[:start], after=heading[start + len("PHYS 1401"):])

    assert _subjects(p6_conn, file_id, content_hash) == {"PHYS1401"}


def test_a_term_in_a_heading_is_still_the_other_slot_s_business(p6_conn, tmp_path):
    """The predicate gained a clause; it did not lose the one it had.

    `SPRING2026` matches `_STRUCTURED` as well as `_TERM` -- `cli.find_structured_
    strings` says so in its own docstring, which is why the term pattern runs first
    and takes its spans. `not _is_term` is what keeps the two slots from claiming
    each other's readings, and P6 SPEC:409-410 sends a date read out of text down
    §3.10's path as `validated`, never `direct`.
    """
    file_id, content_hash = _file(p6_conn, tmp_path, name="term.pdf",
                                  body=b"a term sheet")
    _located_string(p6_conn, run_id="run-term", file_id=file_id,
                    content_hash=content_hash, raw="SPRING2026", page=1, start=0)

    assert _subjects(p6_conn, file_id, content_hash) == set()


@pytest.mark.parametrize("raw", LAYOUT_DEBRIS + WHOLE_HEADINGS)
def test_the_model_seam_refuses_the_same_values_the_slot_refuses(raw):
    """§3.6 check 3, asked about the values §3.5 now refuses.

    `normalize_for_model` reuses the slot's own `matches` on purpose -- "a model
    proposing `Spring 2026` as a SUBJECT is proposing something the field's own rule
    says is not one, and returning a canonical form would launder it into a folder
    name". The same sentence has to hold for `!`: one rule, both producers, or the
    cloud path re-opens the door the deterministic path just shut.
    """
    assert cli.normalize_for_model("subject", raw) is None


@pytest.mark.parametrize("raw,expected", [("PHYS 1401", "PHYS1401"),
                                          ("PHYS1401", "PHYS1401"),
                                          ("UA872", "UA872")])
def test_the_model_seam_still_normalizes_an_identifier(raw, expected):
    """And the twin again, at the seam: agreement in another spelling is agreement.

    `contradicts_stronger` compares AFTER this call, so a `None` here would make a
    model's correct answer read as a refusal it never was.
    """
    assert cli.normalize_for_model("subject", raw) == expected

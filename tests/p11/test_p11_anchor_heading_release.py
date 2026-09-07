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


def test_the_heading_that_states_both_spellings_is_refused(conn, tmp_path):
    """`104` R-135's blocker, measured rather than asserted.

    The one reading in the corpus that carries the code AND the course's name is
    refused, and the refusal is §8.4's whole-document rule firing on a HEADING:
    `model_placement.releasable_excerpts` skips a span whose `start <= 0` and whose
    `end >= unit_length`, and `extractors/pdf.py` gives a heading observation exactly
    that span over exactly that unit.

    §8.4's sentence is "should not send full documents where a short heading or OCR
    excerpt is enough" -- a heading is the thing it names as sufficient, so the rule is
    refusing the alternative it exists to prefer. Whether that changes is a decision
    about what leaves the device, and this test states the current behaviour so the
    decision is taken against a number rather than a guess.
    """
    _file_id, whole, code = _corpus(conn, tmp_path)

    offered = releasable_excerpts(
        conn, evidence_refs=[whole.observation_key, code.observation_key])

    keys = [one.observation_key for one in offered]
    assert whole.observation_key not in keys
    assert keys == [code.observation_key]


def test_site_a_refuses_the_same_heading_for_the_same_reason(conn, tmp_path):
    """The refusal is the PRODUCT's, not site C's, and that is what makes it a
    coverage question rather than a placement one.

    `model_facts.releasable_observations` carries the identical whole-unit condition
    (`src/model_facts.py:449-455`), so the heading that states the course's code and
    its name together never reaches the fact model either. Constitution 2: "Any
    successfully-read file must reach the model" -- the file does reach it; the one
    reading that would settle this row does not, at either site.
    """
    from model_facts import releasable_observations

    _file_id, whole, code = _corpus(conn, tmp_path)

    offered = releasable_observations(
        conn, file_id=_file_id, content_hash=get_file(conn, _file_id)["content_hash"],
        limit=10)
    keys = [one.observation_key for one in offered]

    assert code.observation_key in keys
    assert whole.observation_key not in keys


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

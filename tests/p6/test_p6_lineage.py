# tests/p6/test_p6_lineage.py
"""`97`'s lineage rule under the owner's ruling of 11 Sep 2026.

`97` was ratified as written (`00`, Amendments of 2026-09-11, item 4) and as written
it ruled none of its four candidate signals -- "Candidate signals, none of them
ruled" (§3). The owner then ruled: two files are two versions of one document when
they share a document title -- the `title` observation, or the first `heading` where
there is none -- and their content hashes differ; filenames are never a basis; the
family's stored name is the shared title; the blocking key is that title's canonical
form.

What is measured here is the rule and the key as a pair. `version_family` states a
contract it cannot check -- the key must be a NECESSARY CONDITION of the rule -- and
`facts/lineage.py` satisfies it by building both from one reading of the title. The
last test is the one that would catch them drifting apart.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts import lineage as lineage_module
from facts.families import VERSION_FAMILY_FIELD, version_family
from facts.file_facts import facts_for_file
from facts.lineage import title_block_key, title_lineage

CLOCK = "2026-09-11T12:00:00+00:00"

TITLE = "Thesis Proposal - Tidal Mixing"


def canonical(field_key: str, raw_value: str) -> str | None:
    """A stand-in for the deployment's own `cli.normalize_for_model`.

    That function collapses whitespace for a field with no slot and `version_family`
    has none, so this is the same rule on the same input -- injected rather than
    imported, because importing `cli` into a P6 unit test would make the rule's one
    seam into two.
    """
    text = " ".join(raw_value.split())
    return text or None


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Documents", mime_type="text/markdown",
        detected_format="md", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, index=1):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="text.structured", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = ((Segment("heading", index=index, label="h"),)
                 if zone == "heading" else ())
    observation = Observation(
        file_id=file_id, content_hash=content_hash,
        extractor_name="text.structured", extractor_version="1.0.0",
        source_type="text_document", raw_value=raw,
        location=Location(zone, container), occurrence_count=1,
        observed_at=CLOCK, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _titled(conn, tmp_path, *, name, body, title, zone="heading", run=None):
    file_id, digest = _record(conn, tmp_path, name=name, body=body)
    key = _observe(conn, run_id=run or f"r-{name}", file_id=file_id,
                   content_hash=digest, raw=title, zone=zone)
    return file_id, digest, key


def test_two_files_with_one_title_and_different_bytes_are_one_lineage(
        p6_conn, tmp_path):
    left, _, left_key = _titled(p6_conn, tmp_path, name="draft.md",
                                body=b"draft one", title=TITLE)
    right, _, right_key = _titled(p6_conn, tmp_path, name="final.md",
                                  body=b"draft two", title=TITLE)

    found = title_lineage(canonical)(p6_conn, left, right)

    assert found is not None
    assert found.family_value == TITLE
    # `00`:50's ladder: a `validated` fact "passed contextual checks", and one
    # signal with nothing beside it did not; `direct` is forbidden outright by
    # Done-means 24. THE RULING DID NOT NAME THIS STATE -- `facts/lineage.py`
    # derives it and writes out the counter-argument.
    assert found.reliability_state == "possible"
    # `97` §3: "a family with nothing to cite is not written." Both titles, so each
    # member's fact can cite the observation on its own file.
    assert set(found.evidence_refs) == {left_key, right_key}


def test_two_titles_that_differ_propose_no_lineage(p6_conn, tmp_path):
    left, _, _ = _titled(p6_conn, tmp_path, name="a.md", body=b"one",
                         title=TITLE)
    right, _, _ = _titled(p6_conn, tmp_path, name="b.md", body=b"two",
                          title="Electricity invoice, March 2026")
    assert title_lineage(canonical)(p6_conn, left, right) is None


def test_a_file_that_states_no_title_proposes_no_lineage(p6_conn, tmp_path):
    """`None`, and deliberately not an `unresolved` row.

    A document that states no title has proposed no relation, and the module's
    standing rule is that a relation nobody proposed was never attempted.
    """
    left, _, _ = _titled(p6_conn, tmp_path, name="a.md", body=b"one", title=TITLE)
    right, right_hash = _record(p6_conn, tmp_path, name="b.md", body=b"two")
    _observe(p6_conn, run_id="r-body", file_id=right, content_hash=right_hash,
             raw=TITLE, zone="body")

    assert title_lineage(canonical)(p6_conn, left, right) is None
    assert title_block_key(canonical)(p6_conn, right) is None
    assert version_family(p6_conn, file_ids=(left, right),
                          lineage_rule=title_lineage(canonical),
                          block_key=title_block_key(canonical)) == ()
    assert facts_for_file(p6_conn, right, right_hash) == []


def test_a_shared_filename_stem_is_never_a_lineage(p6_conn, tmp_path):
    """§8.3: "a filename match alone does not". The rule reads no name at all.

    `report.md` and `report (1).md` are the browser's second download and `97` §1
    names the rule everybody reaches for first as the one the design rules out.
    Neither file states a title, so neither proposes anything -- and the module's
    own code is checked for the three name-bearing zones as well, because a rule
    that never fires on this fixture and reads `filename` elsewhere would pass.
    """
    left, left_hash = _record(p6_conn, tmp_path, name="report.md", body=b"one")
    right, right_hash = _record(p6_conn, tmp_path, name="report (1).md",
                                body=b"two")
    _observe(p6_conn, run_id="f-left", file_id=left, content_hash=left_hash,
             raw="report.md", zone="filename")
    _observe(p6_conn, run_id="f-right", file_id=right, content_hash=right_hash,
             raw="report (1).md", zone="filename")

    assert title_lineage(canonical)(p6_conn, left, right) is None
    source = inspect.getsource(lineage_module)
    for forbidden in ('"filename"', "'filename'", '"path"', "'path'",
                      '"normalized_filename"', "'normalized_filename'"):
        assert forbidden not in source, forbidden


def test_a_stated_title_outranks_a_heading_and_the_first_heading_wins(
        p6_conn, tmp_path):
    """The ruling's own order: the `title` observation, or the FIRST `heading`.

    "First" is P6's total order over the version's observations and not P4's
    insertion order, so the answer is a property of the document rather than of the
    run that extracted it.
    """
    stated, stated_hash = _record(p6_conn, tmp_path, name="props.md", body=b"one")
    _observe(p6_conn, run_id="s-h", file_id=stated, content_hash=stated_hash,
             raw="Chapter One", zone="heading", index=1)
    _observe(p6_conn, run_id="s-t", file_id=stated, content_hash=stated_hash,
             raw=TITLE, zone="title")

    headed, headed_hash = _record(p6_conn, tmp_path, name="heads.md", body=b"two")
    _observe(p6_conn, run_id="h-2", file_id=headed, content_hash=headed_hash,
             raw="Chapter Two", zone="heading", index=2)
    _observe(p6_conn, run_id="h-1", file_id=headed, content_hash=headed_hash,
             raw=TITLE, zone="heading", index=1)

    key = title_block_key(canonical)
    assert key(p6_conn, stated) == TITLE
    assert key(p6_conn, headed) == TITLE
    assert title_lineage(canonical)(p6_conn, stated, headed) is not None


def test_the_block_key_is_a_necessary_condition_of_the_rule(p6_conn, tmp_path):
    """The contract `version_family` states and cannot check, measured here.

    Over a corpus of titled and untitled files, every pair the rule answers for is a
    pair the key puts in one block. A key and a rule that read the title differently
    would drift apart silently, and the symptom would be a missing family rather
    than a failing call -- which is why this is asserted rather than argued.
    """
    made = []
    for index, (name, title) in enumerate((
            ("a.md", TITLE), ("b.md", TITLE), ("c.md", "Reading list"),
            ("d.md", "Reading  list"), ("e.md", None))):
        if title is None:
            made.append(_record(p6_conn, tmp_path, name=name,
                                body=f"body {index}".encode())[0])
            continue
        made.append(_titled(p6_conn, tmp_path, name=name,
                            body=f"body {index}".encode(), title=title)[0])

    rule = title_lineage(canonical)
    key = title_block_key(canonical)
    for left in made:
        for right in made:
            if left == right or rule(p6_conn, left, right) is None:
                continue
            left_key = key(p6_conn, left)
            assert left_key is not None
            assert left_key == key(p6_conn, right), (left, right)

    # And the pair whose titles differ only in whitespace IS one family, which is
    # what makes the canonical form the family's name rather than either spelling.
    written = version_family(p6_conn, file_ids=tuple(made), lineage_rule=rule,
                             block_key=key)
    assert len(written) == 4
    values = {row["canonical_value"]
              for file_id in made
              for row in facts_for_file(
                  p6_conn, file_id, get_file(p6_conn, file_id)["content_hash"])
              if row["field_key"] == VERSION_FAMILY_FIELD}
    assert values == {TITLE, "Reading list"}, values

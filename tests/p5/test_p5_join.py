# tests/p5/test_p5_join.py
"""The four join defects the 2026-08-21 stress test executed against live packages.

Each passed every unit test in tests/p5/ while being broken, because the suite is
comprehensive about SHAPE and was not comprehensive about the JOIN: P5 never called
extraction_status_by_tier on the two-run unrouted fixture, never raised from a
reader, never collapsed DOCX, and never went through P4's event writer.
"""
from pathlib import Path

import pytest

#: A live P1 content hash: 64 hex, no `sha256:` prefix. Mixing the two spellings in
#: one database splits one file into two evidence sets.
CONTENT_HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
PAGE_ONE = "BUSIB 4300 Syllabus\nSpring 2026. Meetings on Tuesdays."
HEADING = "BUSIB 4300 Syllabus"
CLOCK = "2026-08-19T12:00:00+00:00"


@pytest.fixture()
def p4_tables(conn):
    """P1's database with P4's three tables. tests/p5 has no `p4_conn` of its own and
    tests/p4/conftest.py is another package's file."""
    from evidence_shape.schema import create_evidence_schema
    create_evidence_schema(conn)
    return conn


# ---------------------------------------------------------------- break 2
def test_an_unrouted_run_is_the_native_tier_not_a_second_filesystem_extract():
    """A4, ratified 2026-08-20: a routed-but-stopped run carries `analysis_tier: native`.

    It was `filesystem`, reusing `filesystem.record` as the extractor name. So a .dmg
    produced TWO runs in the filesystem tier -- `complete` from the indexer and
    `metadata_only` from the stopper -- and extraction_status_by_tier raised
    TierConflict on the first .dmg in Downloads. The stopping run is not a second
    filesystem extract; it is the native extractor that did not exist or refused.
    """
    from extractors.filesystem import unrouted_result
    from extractors.router import route
    row = {"file_id": "f1", "content_hash": "a" * 64, "filename": "archive.dmg",
           "extension": ".dmg", "mime_type": None, "detected_format": "dmg"}
    decision = route(file_id="f1", content_hash="a" * 64, path=Path("/c/archive.dmg"),
                     extension=".dmg", detect_format=lambda p: "dmg")
    result = unrouted_result(file_row=row, decision=decision, now="t")
    assert result.run["analysis_tier"] == "native"
    assert result.run["extractor_name"] != "filesystem.record"


def test_the_indexer_and_the_stopper_no_longer_collide():
    """The executed failure: extraction_status_by_tier([filesystem, unrouted]) raised."""
    from extractors.runs import extraction_status_by_tier
    fs = {"analysis_tier": "filesystem", "completeness": "complete"}
    stopped = {"analysis_tier": "native", "completeness": "metadata_only"}
    assert extraction_status_by_tier([fs, stopped]) == {
        "filesystem": "complete", "native": "metadata_only"}


# ---------------------------------------------------------------- break 3
def test_a_reader_that_raises_becomes_a_failed_run_not_a_crashed_scan():
    """§2.4's `completeness=failed` is in P4's vocabulary and rule 9. Nothing produced
    it: `src/extractors/` contained zero `except`. A password-protected PDF, a corrupt
    ZIP or a truncated DOCX propagated and ended the scan."""
    from extractors.failure import failed_result
    row = {"file_id": "f1", "content_hash": "b" * 64, "filename": "locked.pdf",
           "extension": ".pdf", "mime_type": None, "detected_format": "pdf"}
    result = failed_result(file_row=row, error=ValueError("file is encrypted"),
                           extractor_name="pdf.text", extractor_version="0.1.0",
                           source_type="text_document", now="t")
    assert result.run["completeness"] == "failed"
    assert result.observations == ()          # P4 rule 9: failed carries none
    assert "encrypted" in result.run["failure_reason"]


def test_the_exception_is_the_signal_and_no_threshold_is_invented():
    """"Do not invent a threshold for 'too corrupt.' The exception is the signal."""
    import ast, inspect
    from extractors import failure
    # Scoped to CODE, not prose. Asserting a token appears nowhere in the source also
    # matches the docstring explaining WHY the token is absent -- the guard-token trap
    # that has now bitten this project five times. Names and literals only.
    tree = ast.parse(inspect.getsource(failure))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    numbers = {n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))}
    assert not any("threshold" in x.lower() or "max_" in x.lower() for x in names), names
    assert not (numbers - {0, 1}), f"an invented number: {numbers}"


# ---------------------------------------------------------------- break 4
def test_every_extractor_collapses_because_the_result_itself_does():
    """P4 D10: one observation per (run, exact raw value, zone), `occurrence_count`
    counting within the zone and `location` addressing the FIRST occurrence.

    `_collapse` lived in pdf.py and archive.py only, so DOCX, structured text,
    long-tail, OCR, image and filesystem emitted one row per hit -- exploding row
    counts and splitting P6's weight across clones of one string. Collapsing where
    every extractor already passes (ExtractionResult) fixes six at one point, and a
    seventh extractor inherits it instead of silently skipping it.
    """
    from extractors.sink import ExtractionResult
    from extractors.shape import location, observation
    def obs(raw):
        return observation(file_id="f1", content_hash="c" * 64,
                           extractor_name="docx.text", extractor_version="0.1.0",
                           source_type="text_document", raw_value=raw,
                           location=location(zone="body"), observed_at="t",
                           reliability="possible")
    result = ExtractionResult(run={"run_id": "r"},
                              observations=(obs("Columbia"), obs("Columbia"), obs("Yale")))
    assert len(result.observations) == 2, "two Columbia hits must collapse to one row"
    columbia = [o for o in result.observations if o["raw_value"] == "Columbia"][0]
    assert columbia["occurrence_count"] == 2


# ---------------------------------------------------------------- break 5
def a_pdf_result(document: Path):
    """One real extractor's output, so the join is exercised end to end and not
    against a dict this file wrote to suit itself."""
    from extractors.pdf import PdfDocument, PdfPage, extract_pdf
    from extractors.reading import Region
    from extractors.safety import SafetyPolicy
    file_row = {"file_id": "f1", "content_hash": CONTENT_HASH,
                "filename": document.name}
    page = PdfPage(number=1, text=PAGE_ONE,
                   regions=(Region(zone="heading", start=0, end=len(HEADING),
                                   ordinal=1, label=HEADING),))
    return extract_pdf(
        file_row=file_row, path=document,
        policy=SafetyPolicy(is_protected_container=lambda p: False,
                            is_dataless=lambda p: False),
        read_pdf=lambda target: PdfDocument(metadata={}, pages=(page,)),
        find_structured_strings=lambda text: (), now=CLOCK, context_window=24)


def test_p5_publishes_no_event_writer_of_its_own():
    """P4's `record_run_event` shipped and `extractors.events.append` still called
    P1's `append_event` directly, so an orchestrator following both plans wrote TWO
    `extraction` events per run and "exactly one event per run" could not hold.

    What had blocked the swap was the missing batch writer: `record_run_event` builds
    its explanation from the STORED `observation_key`s, so it needs the run and its
    observations written first, and P5 authored its event for a run no sink had seen.
    `evidence_shape.store.RunWriter` is that ordering, and it appends the event
    itself -- so `append` is gone rather than delegating. A one-line pass-through
    would leave a second NAME for one writer, which is the defect this project has
    paid for most often.

    Parsed, not grepped: asserting a token appears nowhere in a module's source also
    matches the comment explaining why the token is absent -- the guard-token trap
    that has now bitten this project five times. Names, aliases and attributes only.
    """
    import ast, inspect
    from extractors import events
    tree = ast.parse(inspect.getsource(events))

    assert not hasattr(events, "append"), "P5's event writer is gone, not renamed"
    assert "append" not in {node.name for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef)}
    imported = {alias.asname or alias.name for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names}
    referenced = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    referenced |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert "append_event" not in imported | referenced, "P1's writer is P4's to call"


def test_the_sink_appends_exactly_one_event_per_run(p4_tables, tmp_path: Path):
    """The join, end to end: one real extractor result, one `write`, one event -- and
    its §8.2 evidence reference is the run's own stored `observation_key`s."""
    import json
    from evidence_shape.store import RunWriter, observation_keys_for_run

    document = tmp_path / "Syllabus BUSIB 4300.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    run_id = RunWriter(p4_tables, author="P5").write(a_pdf_result(document))

    rows = p4_tables.execute("SELECT * FROM events").fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == "P5"
    explanation = json.loads(rows[0]["explanation"])
    assert explanation["run_id"] == run_id
    assert explanation["observation_keys"] == observation_keys_for_run(p4_tables,
                                                                          run_id)
    assert explanation["observation_keys"], "the heading is a cited row, not nothing"


def test_the_real_sink_and_the_recording_sink_agree_on_the_contract(p4_tables,
                                                                   tmp_path: Path):
    """`RecordingSink` is what all six extractor test modules write through, so it is
    the shape P5 is tested against; `RunWriter` is the shape P5 ships against. One
    `ExtractionResult` in, the same observable batch out, or the double is quietly
    testing something the database does not do.

    Compared through P4's own derivations -- `observation_key` and the two locators --
    because those are what a citation resolves on. Comparing the emitted dicts instead
    would pass while the stored rows addressed something else.
    """
    from evidence_shape.store import (
        RunWriter, get_run, observations_for_run, text_units_for_run,
    )
    from conftest import RecordingSink
    from p4_stub import locator_for, observation_key, unit_locator_for

    document = tmp_path / "Syllabus BUSIB 4300.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    result = a_pdf_result(document)

    recording = RecordingSink()
    recorded_id = recording.write(result)
    stored_id = RunWriter(p4_tables, author="P5").write(result)
    recording.conforms()

    def without_run_id(mapping):
        return {name: value for name, value in mapping.items() if name != "run_id"}

    assert without_run_id(get_run(p4_tables, stored_id).to_mapping()) == \
        without_run_id(recording.run_for(recorded_id))

    assert [(o.observation_key, o.raw_value, o.locator, o.occurrence_count,
             o.reliability, o.source_type)
            for o in observations_for_run(p4_tables, stored_id)] == \
        [(observation_key(o), o["raw_value"], locator_for(o["location"]),
          o["occurrence_count"], o["reliability"], o["source_type"])
         for o in recording.observations_for(recorded_id)]

    assert [(u.unit_locator, u.text, u.length, u.truncated)
            for u in text_units_for_run(p4_tables, stored_id)] == \
        [(unit_locator_for(u["container_path"]), u["text"], len(u["text"]),
          u["truncated"])
         for u in recording.units_for(recorded_id)]


def test_the_double_and_the_real_sink_have_one_signature():
    # The Protocol is the contract; a double that drifted from it would let the six
    # extractor modules keep passing against a `write` P4 does not offer.
    import inspect
    from evidence_shape.store import RunWriter
    from extractors.sink import EvidenceSink
    from conftest import RecordingSink
    reference = inspect.signature(EvidenceSink.write)
    for implementation in (RunWriter, RecordingSink):
        actual = inspect.signature(implementation.write)
        assert list(actual.parameters) == list(reference.parameters)
        assert [p.kind for p in actual.parameters.values()] == \
            [p.kind for p in reference.parameters.values()]


def test_neither_sink_lets_a_batch_name_its_own_run_id(p4_tables):
    """`run_id` is P4-assigned -- `extractors.shape`'s header says so and P5 emits
    none. Both writers merged the batch's own mapping OVER the id they had just
    minted, so a batch that carried one would have been honoured silently by the
    double and half-honoured by the database, where the run row lands under the
    caller's id while the event and the returned handle use the minted one.

    The double is only a double while it refuses what the real writer refuses.
    """
    from evidence_shape.runs import MalformedRun
    from evidence_shape.store import RunWriter
    from extractors.sink import ExtractionResult
    from conftest import RecordingSink

    named = ExtractionResult(run={"run_id": "r1"})
    with pytest.raises(MalformedRun):
        RunWriter(p4_tables, author="P5").write(named)
    with pytest.raises(MalformedRun):
        RecordingSink().write(named)

# tests/p7/test_p7_resolve.py
"""The one place in the repository where (observation_key, span) becomes text.

Everything here is about narrowness. Two resolvers and no third; the current row and
not the first; a refusal where P4 gives no answer, never a best-effort substring; and
an AST guard proving no other module under `src/privacy/` binds a P4 materialiser.
"""
import ast
import dataclasses
import pathlib

import pytest

from evidence_shape.location import Location, Region, Segment, TextSpan, TimeSpan
from evidence_shape.locator import serialize_locator
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    get_observation, observations_by_key, record_observation, record_run,
    record_text_unit, supersede_observation, unit_for_observation,
)
from evidence_shape.text_units import TextUnit

import privacy
from privacy.redaction import RegionOriginUnspecified, span_address
from privacy.resolve import (
    MATERIALISERS, AmbiguousObservationKey, Materialised, UnresolvableSpan,
    current_observation, materialise,
)

CONTENT_HASH = "a" * 64
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T13:00:00+00:00"
PAGE = (Segment(kind="page", index=2),)
BODY = "Passport number 992-33-1188 issued 2019."
VALUE = "992-33-1188"
BEFORE = "Passport number "
AFTER = " issued 2019."
CELL = (Segment(kind="sheet", index=1), Segment(kind="row", index=4),
        Segment(kind="cell", index=3))


class Item:
    """Stands in for Task 7's `Excerpt` / `RedactedIdentifier`.

    Task 9 reads exactly two attributes -- `observation_key` and `span` -- and Task 7
    owns the rest of the shape. A local stand-in keeps this test from going red when a
    field this module never touches is added next door, and states the pin: `span` is
    a `TextSpan | None`.
    """

    def __init__(self, observation_key: str, span: TextSpan | None):
        self.observation_key = observation_key
        self.span = span


@pytest.fixture()
def evidence(p7_conn):
    create_evidence_schema(p7_conn)
    return p7_conn


def a_run(conn, run_id, version, started):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id="file-1", content_hash=CONTENT_HASH,
        extractor_name="pdf_text", extractor_version=version,
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=started, observation_count=1))


def an_observation(conn, *, run_id, version, location, raw_value=VALUE,
                   context_before=BEFORE, context_after=AFTER,
                   context_truncated=False, extractor_name="pdf_text",
                   source_type="text_document", observed_at=FIXED_CLOCK) -> str:
    return record_observation(conn, Observation(
        file_id="file-1", content_hash=CONTENT_HASH, extractor_name=extractor_name,
        extractor_version=version, source_type=source_type, raw_value=raw_value,
        location=location, occurrence_count=1, observed_at=observed_at,
        reliability="direct", run_id=run_id, context_before=context_before,
        context_after=context_after, context_truncated=context_truncated))


def key_for(location, *, extractor_name="pdf_text", raw_value=VALUE) -> str:
    """P4 mints the key from `serialize_locator`, not from `span_address`.

    They agree on the two forms P7 can resolve and differ on the two it refuses --
    `span_address` raises for a region and a time span, and P4 still has a key for
    both. The key is P4's, so the test computes it P4's way.
    """
    return observation_key(content_hash=CONTENT_HASH, extractor_name=extractor_name,
                           locator=serialize_locator(location), raw_value=raw_value)


@pytest.fixture()
def one_excerpt(evidence):
    """One run, one unit, one observation: the ordinary text-span case."""
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    return key_for(location), location


# --- the ordinary text-span path ---------------------------------------------

def test_a_text_span_materialises_the_substring(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.value == VALUE
    assert result.value == BODY[16:27]


def test_the_result_carries_the_key_the_address_and_the_zone(evidence, one_excerpt):
    key, location = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.observation_key == key
    assert result.span == "body:page=2#16-27" == span_address(location)
    assert result.zone == "body"


def test_the_three_context_fields_travel_with_the_value(evidence, one_excerpt):
    # M5, and Task 8's whole reason for existing: §8.4 redacts the value without
    # dropping what surrounds it, so the value cannot arrive at the redactor alone.
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    assert result.context_before == BEFORE
    assert result.context_after == AFTER
    assert result.context_truncated is False


def test_context_truncated_travels_too(evidence):
    # §8.6 forbids anything being truncated silently, so the flag reaches the manifest.
    a_run(evidence, "run-t", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-t", container_path=PAGE, text=BODY))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-t", version="1.0.0", location=location,
                   context_truncated=True)
    result = materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert result.context_truncated is True


def test_materialised_holds_no_path_and_no_file_id(evidence, one_excerpt):
    # §8.4 puts "Paths" in the always-local set. The type cannot carry one.
    names = {field.name for field in dataclasses.fields(Materialised)}
    assert names == {"observation_key", "span", "value", "zone", "context_before",
                     "context_after", "context_truncated", "unit_length"}
    assert not names & {"file_id", "path", "current_path", "filename", "content_hash"}


def test_unit_length_travels_so_the_whole_document_check_can_run(evidence, one_excerpt):
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question." Task 7's `check_item(item, *, unit_length)`
    # needs the stored length, and this is the only module that may ask P4 for it.
    key, _ = one_excerpt
    assert materialise(evidence, Item(key, TextSpan(16, 27))).unit_length == len(BODY)


def test_a_container_path_address_has_no_unit_length(evidence, one_cell):
    key, _ = one_cell
    assert materialise(evidence, Item(key, None)).unit_length is None


def test_materialised_is_frozen(evidence, one_excerpt):
    key, _ = one_excerpt
    result = materialise(evidence, Item(key, TextSpan(16, 27)))
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.value = "anything else"


# --- the current-row rule ------------------------------------------------------

@pytest.fixture()
def two_versions(evidence):
    """P4's guaranteed shape: two extractor versions, one key (MINOR 8)."""
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    a_run(evidence, "run-1", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-1", container_path=PAGE, text=BODY))
    old = an_observation(evidence, run_id="run-1", version="1.0.0", location=location)
    a_run(evidence, "run-2", "2.0.0", LATER)
    record_text_unit(evidence, TextUnit(run_id="run-2", container_path=PAGE, text=BODY))
    new = an_observation(evidence, run_id="run-2", version="2.0.0", location=location,
                         observed_at=LATER)
    return key_for(location), old, new


def test_p4_really_does_return_two_rows_for_one_key(evidence, two_versions):
    # The premise. If P4 ever made the key unique this test goes red and the
    # current-row rule below becomes unnecessary rather than silently wrong.
    key, _, _ = two_versions
    assert len(observations_by_key(evidence, key)) == 2


def test_resolution_picks_the_current_row_and_not_the_first(evidence, two_versions):
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    resolved = current_observation(evidence, key)
    assert resolved.extractor_version == "2.0.0"
    assert resolved.run_id == "run-2"
    assert resolved == get_observation(evidence, new)


def test_two_unsuperseded_rows_raise_rather_than_picking_one(evidence, two_versions):
    # "an unresolvable ambiguity raises rather than picking the first." Releasing the
    # wrong one of two live rows is a silent release of retracted text.
    key, _, _ = two_versions
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_p1s_writer_refuses_to_build_a_headless_chain(evidence, two_versions):
    # Verified against the live substrate: `mark_superseded` rejects a cycle and
    # rejects re-superseding a superseded row, so a key with no live head cannot be
    # reached through P1's published writer at all. Asserted here so the next test's
    # raw UPDATE is legible as "around the writer" rather than as normal usage.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    with pytest.raises(ValueError, match="cycle"):
        supersede_observation(evidence, old_observation_id=new,
                              new_observation_id=old,
                              reason="a cycle nobody meant to write")


def test_a_key_with_no_live_row_raises(evidence, two_versions):
    # Reachable only by writing around P1's writer -- which is what a hand-edited,
    # half-restored, or partially migrated database looks like. The gate answers it
    # with a refusal rather than with whichever row it happened to see last.
    key, old, new = two_versions
    supersede_observation(evidence, old_observation_id=old, new_observation_id=new,
                          reason="extractor upgrade")
    evidence.execute("UPDATE evidence SET superseded_by = ? WHERE observation_id = ?",
                     (old, new))
    with pytest.raises(AmbiguousObservationKey):
        current_observation(evidence, key)


def test_an_unknown_key_is_unresolvable(evidence):
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, "sha256:" + "f" * 64)


def test_an_observation_id_is_not_a_citation_handle(evidence, one_excerpt):
    # M14: "a per-row `observation_id` dies on extractor upgrade". A caller who
    # passes one gets a refusal here rather than a resolution that stops working
    # the next time an extractor ships.
    key, location = one_excerpt
    row = evidence.execute(
        "SELECT observation_id FROM evidence WHERE observation_key = ?", (key,)
    ).fetchone()
    with pytest.raises(UnresolvableSpan):
        current_observation(evidence, row["observation_id"])


def test_p4_publishes_no_current_row_reader(evidence, one_excerpt):
    # The reported gap, asserted so it cannot be quietly forgotten: the published
    # reader returns records with no id and no supersession column, so P7 cannot
    # ask P4 which row is current. `store.current_observation_by_key` would close it.
    key, _ = one_excerpt
    (only,) = observations_by_key(evidence, key)
    names = {field.name for field in dataclasses.fields(only)}
    assert "observation_id" not in names
    assert "superseded_by" not in names


# --- the second resolver: a container-path address -----------------------------

@pytest.fixture()
def one_cell(evidence):
    a_run(evidence, "run-c", "1.0.0", FIXED_CLOCK)
    location = Location(zone="table", container_path=CELL)
    an_observation(evidence, run_id="run-c", version="1.0.0", location=location,
                   raw_value="4,200.00", extractor_name="xlsx_tables",
                   source_type="spreadsheet", context_before=None, context_after=None)
    return key_for(location, extractor_name="xlsx_tables", raw_value="4,200.00"), location


def test_a_container_path_address_materialises_the_raw_value(evidence, one_cell):
    key, location = one_cell
    result = materialise(evidence, Item(key, None))
    assert result.value == "4,200.00"
    assert result.span == "table:sheet=1/row=4/cell=3"
    assert result.zone == "table"


def test_a_container_path_address_has_no_text_unit_at_all(evidence, one_cell):
    # The reason it is a SECOND resolver and not a degenerate first: there is
    # nothing to take a substring of.
    key, _ = one_cell
    assert unit_for_observation(evidence, current_observation(evidence, key)) is None


def test_a_container_path_address_never_falls_back_to_a_unit(evidence, one_cell):
    # Even with a unit sitting at the same run, the cell address resolves to the
    # cell. "Send the cell" must not become "send the sheet".
    key, _ = one_cell
    record_text_unit(evidence, TextUnit(run_id="run-c", container_path=CELL,
                                        text="the whole sheet, flattened"))
    assert materialise(evidence, Item(key, None)).value == "4,200.00"


# --- refusals ------------------------------------------------------------------

def test_a_span_that_does_not_anchor_is_unresolvable(evidence):
    # P4 does NOT validate the anchor at write time -- verified against the live
    # store, a non-anchoring observation records cleanly -- so this check is the
    # only thing standing between a stale span and released text.
    a_run(evidence, "run-x", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-x", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-x", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan) as caught:
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))
    assert "RAW-1" in str(caught.value.__cause__)


def test_a_failed_anchor_returns_no_substring_at_all(evidence):
    # "P4's checker raises; never returns a repair, and a gate that repaired would
    # release text nobody addressed." The wrong substring is right there in the
    # unit; nothing hands it back.
    a_run(evidence, "run-y", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-y", container_path=PAGE,
                                        text="X" * 40))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(16, 27))
    an_observation(evidence, run_id="run-y", version="1.0.0", location=location)
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location), TextSpan(16, 27)))


def test_a_span_beyond_the_stored_unit_is_unresolvable(evidence):
    a_run(evidence, "run-z", "1.0.0", FIXED_CLOCK)
    record_text_unit(evidence, TextUnit(run_id="run-z", container_path=PAGE,
                                        text="short", truncated=True))
    location = Location(zone="body", container_path=PAGE, text_span=TextSpan(10, 20))
    an_observation(evidence, run_id="run-z", version="1.0.0", location=location,
                   raw_value="beyond")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="beyond"),
                                   TextSpan(10, 20)))


def test_a_text_span_with_no_unit_is_unresolvable(evidence):
    a_run(evidence, "run-w", "1.0.0", FIXED_CLOCK)
    location = Location(zone="body", container_path=(Segment(kind="page", index=9),),
                        text_span=TextSpan(0, 6))
    an_observation(evidence, run_id="run-w", version="1.0.0", location=location,
                   raw_value="orphan")
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key_for(location, raw_value="orphan"),
                                   TextSpan(0, 6)))


def test_the_callers_span_must_match_the_one_the_key_carries(evidence, one_excerpt):
    # SPEC §4: an excerpt is "resolved by the gate from local storage". The caller's
    # coordinates are a claim, and a claim that disagrees with the record is refused
    # rather than honoured or silently replaced.
    key, _ = one_excerpt
    with pytest.raises(UnresolvableSpan):
        materialise(evidence, Item(key, TextSpan(0, 39)))


def test_a_region_addressed_observation_is_refused(evidence):
    # NEEDS-JOSEPH C3, reached through Task 8's `span_address`.
    a_run(evidence, "run-r", "1.0.0", FIXED_CLOCK)
    location = Location(zone="ocr", container_path=PAGE,
                        region=Region(0.10, 0.22, 0.30, 0.04, "norm"))
    an_observation(evidence, run_id="run-r", version="1.0.0", location=location,
                   raw_value="992-33-1188", extractor_name="ocr_engine",
                   source_type="ocr")
    key = key_for(location, extractor_name="ocr_engine")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


def test_a_time_span_addressed_observation_is_refused(evidence):
    a_run(evidence, "run-a", "1.0.0", FIXED_CLOCK)
    location = Location(zone="transcript", container_path=(),
                        time_span=TimeSpan(1000, 2000))
    an_observation(evidence, run_id="run-a", version="1.0.0", location=location,
                   raw_value="spoken", extractor_name="whisper_local",
                   source_type="audio_video")
    key = key_for(location, extractor_name="whisper_local", raw_value="spoken")
    with pytest.raises(RegionOriginUnspecified):
        materialise(evidence, Item(key, None))


# --- the single-locus guard ----------------------------------------------------

def test_the_materialiser_list_names_p4s_functions_and_not_a_pattern():
    assert MATERIALISERS["evidence_shape.text_units"] == ("raw_value_at",)
    assert "unit_for_observation" in MATERIALISERS["evidence_shape.store"]
    assert "get_observation" in MATERIALISERS["evidence_shape.store"]


def test_resolve_is_the_only_module_under_src_privacy_that_binds_one():
    # Asserted by walking the AST, not by reading source text: a text scan matches
    # docstrings and comments, and this repository has recorded that false result
    # more than once. Task 21 runs the same walk over the finished package.
    package = pathlib.Path(privacy.__file__).parent
    offenders: dict[str, list[str]] = {}
    for path in sorted(package.glob("*.py")):
        if path.name == "resolve.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        bound: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                names = MATERIALISERS.get(node.module or "", ())
                bound |= {f"{node.module}.{a.name}" for a in node.names
                          if a.name in names}
            elif isinstance(node, ast.Import):
                bound |= {a.name for a in node.names if a.name in MATERIALISERS}
        if bound:
            offenders[path.name] = sorted(bound)
    assert offenders == {}, (
        f"{sorted(offenders)} bind a P4 materialiser; resolve.py is the only module "
        "under src/privacy/ that may, and release.py is the only one that may import "
        "resolve")

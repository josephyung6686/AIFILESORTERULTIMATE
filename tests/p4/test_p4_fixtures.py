# tests/p4/test_p4_fixtures.py
"""Done-means 5, and the coverage shortfall the SPEC's own examples leave."""
import pytest

from evidence_shape.canonical import canonical_json
from evidence_shape.conformance import validate_run
from evidence_shape.determinism import observation_set_digest
from evidence_shape.fixtures import (
    FIXTURES, SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE, ZONES_WITHOUT_A_WORKED_EXAMPLE,
    ZONES_WITH_A_WORKED_EXAMPLE, by_number,
)
from evidence_shape.store import (
    observations_for_run, record_observation, record_run, record_text_unit,
    text_units_for_run,
)
from evidence_shape.vocabulary import SOURCE_TYPES, ZONES

#: The SPEC's worked-example table, column "locator", verbatim. Fixture 16's
#: locator is written there as `metadata:field=name` with "(in `key=dependencies`)"
#: beside it; the two segments serialize outermost-first.
GOLDEN_LOCATORS = {
    1: "heading:page=1/heading=2",
    2: "title:page=1",
    3: "body:page=18#12043-12051",
    4: "table:table=3/row=2/column=1",
    5: "heading:page=1/heading=1",
    6: "metadata:field=Producer",
    7: "metadata:field=DateTimeOriginal",
    8: "ocr:page=4/region=2#0-24",
    9: "manifest:entry=docs%2Ftranscript.pdf",
    10: "manifest:field=file_count",
    11: "filename#0-6",
    12: "table:sheet=2/row=7/column=3",
    13: "notes:slide=6#0-42",
    14: "metadata:field=Subject",
    15: "metadata:field=DTSTART",
    16: "metadata:key=dependencies/field=name",
    17: "transcript@252500-255200",
    18: "metadata:layer=3",
}


def test_there_are_nineteen_fixtures_numbered_as_the_spec_numbers_them():
    assert [fixture.number for fixture in FIXTURES] == list(range(1, 20))


def test_every_fixture_carries_its_golden_locator():
    for number, locator in GOLDEN_LOCATORS.items():
        observation, = by_number(number).observations
        assert observation.locator == locator, number


def test_fixture_19_emits_no_observation_and_says_so_on_the_run():
    # §2.9's safe default. The file is still indexed through its filesystem
    # observations (fixture 11's pattern), which this extractor does not write.
    nineteen = by_number(19)
    assert nineteen.observations == ()
    assert nineteen.run.completeness == "metadata_only"


def test_fixture_18_is_unreadable_and_still_carries_its_metadata_row(       ):
    # M3, and §2.9's "indexed-but-unreadable rather than silently treated as empty".
    eighteen = by_number(18)
    assert eighteen.run.completeness == "unreadable"
    assert len(eighteen.observations) == 1


def test_every_fixture_passes_the_conformance_gate():
    # The strongest form of Done-means 5: the golden records are not merely present,
    # they satisfy all twelve rules through the call an extractor author makes.
    for fixture in FIXTURES:
        assert validate_run(fixture.run, fixture.observations,
                            fixture.text_units) is fixture.run


def test_the_worked_examples_reach_ten_of_the_fifteen_zones():
    # Done-means 5 asks for all of them. The SPEC's own table does not supply them,
    # and P4 does not invent the missing five: a fabricated `link` or `annotation`
    # example is what six extractor authors would then implement against.
    assert ZONES_WITHOUT_A_WORKED_EXAMPLE == (
        "path", "header_footer", "link", "annotation", "reference_list")
    assert len(ZONES_WITH_A_WORKED_EXAMPLE) == 10
    assert set(ZONES_WITH_A_WORKED_EXAMPLE) | set(ZONES_WITHOUT_A_WORKED_EXAMPLE) == set(ZONES)


def test_the_worked_examples_reach_thirteen_of_the_fourteen_source_types():
    assert SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE == ("contacts",)
    covered = {fixture.run.source_type for fixture in FIXTURES}
    assert covered == set(SOURCE_TYPES) - {"contacts"}


def test_the_page_eighteen_reference_list_is_filed_under_body():
    # Reported, not repaired: the SPEC's own reference-list example carries the
    # `body` zone, so `reference_list` has no worked example at all.
    observation, = by_number(3).observations
    assert observation.zone == "body"
    assert "reference list" in by_number(3).design_case


def test_the_filename_span_is_anchored_in_a_text_unit_holding_the_filename():
    # Rule 10 requires a unit for EVERY non-null text_span, and fixture 11's golden
    # locator is a span into a filename. §2.2/§2.4/§2.7 describe text_units as the
    # home for bulk text; this is the edge the contract does not discuss.
    fixture = by_number(11)
    unit, = fixture.text_units
    observation, = fixture.observations
    assert unit.container_path == ()
    assert unit.text.startswith(observation.raw_value)


def test_no_fixture_carries_a_signal_tier():
    # P4 names no EXIF field and authors no field-to-tier mapping; that catalogue is
    # P5's (SPEC Deferred). Rule 11's three tiers are exercised in Task 13.
    assert all(observation.signal_tier is None
               for fixture in FIXTURES for observation in fixture.observations)


def test_fixture_1_carries_the_context_the_walking_skeleton_depends_on():
    # B8a: the context term is what lets P6 resolve the skeleton fixture rather than
    # refuse it. P4 asserts the SPEC's literal string and holds no term list of its
    # own -- §3.5's five terms are P6's.
    observation, = by_number(1).observations
    assert observation.context_before == "Syllabus — "
    assert observation.context_after == " — Spring 2026"
    assert observation.raw_value == "BUSIB 4300"


def test_every_fixture_round_trips_through_canonical_bytes():
    for fixture in FIXTURES:
        for observation in fixture.observations:
            assert canonical_json(observation.to_mapping())


def test_the_fixtures_store_and_read_back_unchanged(p4_conn):
    # What P6, P7, P8 and P2 do with this module: load it into P1's database and
    # build against it with no extractor in existence.
    for fixture in FIXTURES:
        record_run(p4_conn, fixture.run)
        for unit in fixture.text_units:
            record_text_unit(p4_conn, unit)
        for observation in fixture.observations:
            record_observation(p4_conn, observation)

    for fixture in FIXTURES:
        stored = observations_for_run(p4_conn, fixture.run.run_id)
        assert (observation_set_digest(stored)
                == observation_set_digest(fixture.observations)), fixture.number
        assert len(text_units_for_run(p4_conn, fixture.run.run_id)) == len(fixture.text_units)


def test_by_number_rejects_a_number_the_spec_does_not_have():
    with pytest.raises(KeyError):
        by_number(20)

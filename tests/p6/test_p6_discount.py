# tests/p6/test_p6_discount.py
"""Done-means 22, M4, §8.5's A04 "generic author metadata", and §3.8's half of 13."""
from __future__ import annotations

import ast
import inspect
import json
import unicodedata
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_by_key, record_observation, record_run

from facts import discount as discount_module
from facts.discount import (
    AUTHORSHIP_FIELDS, DISCOUNT_OUTCOMES, discount, field_permitted,
    is_discount_target, screen_metadata,
)
from facts.evidence import cite, observations_for_version
from facts.fields import get_field
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-19T12:00:00+00:00"
SUPPRESS, DEMOTE, NOT_METADATA = DISCOUNT_OUTCOMES

#: Catalogue 01's `property_names`, FLATTENED by the caller. The catalogue groups
#: these by format family; flattening here rather than inside `facts` is what keeps
#: the discount from becoming a lookup keyed by format (§2.8, Task 7's guard).
PROPERTY_NAMES = frozenset({
    "Producer", "Creator", "Author",            # pdf_info_dictionary
    "pdf:Producer", "xmp:CreatorTool", "dc:creator",
    "creator", "lastModifiedBy",                # ooxml_core_properties
    "Application", "AppVersion",
    "meta:generator", "meta:initial-creator",
    "Software", "ProcessingSoftware", "HostComputer",
    "TENC", "TSSE", "PRODID", "X-Mailer", "User-Agent",
})


def _fold(value: str) -> str:
    return value.casefold()


def _exact(match: str, *, case_sensitive: bool):
    """One catalogue `exact` entry, compiled to the predicate P6 is handed.

    Copied from `planning/deferred-catalogues/01-tool-producer-strings.json` by hand.
    Nothing under `src/facts/` reads that file, and nothing under `planning/` is
    edited by this task: the catalogue is data injected at construction, and a test
    is a construction site like any other.
    """
    target = _fold(match) if not case_sensitive else match
    return lambda value: (_fold(value) if not case_sensitive else value) == target


#: `tps-python-docx`: match "python-docx", match_kind "exact", case_sensitive false.
#: `tps-ua-mozilla-5`: match "Mozilla/5.0", match_kind "prefix", case_sensitive true
#: -- rendered here as a bare `startswith` because the catalogue's boundary rule is
#: prose and its compiler does not exist (see Contract ambiguities). The two entries
#: §2.2 names by name are the two this task needs.
TOOL_STRINGS = (
    _exact("python-docx", case_sensitive=False),
    lambda value: value.startswith("Mozilla/5.0"),
)

#: §3.8's "never topic, purpose, project, course, institution or target", spelled in
#: the catalogue's keys. `subject` is D6's key for §3.11's "course".
NON_AUTHORSHIP_FIELDS = ("subject", "purpose", "project", "term", "work_type",
                         "target_university", "application_document_type")


def _file(conn, tmp_path, *, name, body, parent="Documents"):
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=parent,
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        detected_format="docx", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="metadata",
             slot="Producer", extractor="docx.metadata", version="1.0.0",
             source_type="text_document", reliability="direct", occurrences=1):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    container = (Segment("field", label=slot),) if slot is not None else ()
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, container), occurrence_count=occurrences,
        observed_at=CLOCK, reliability=reliability, run_id=run_id)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal that is not a docstring. Same helper as Task 7's file."""
    tree = ast.parse(inspect.getsource(module))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings}


def _screen(conn, file_id, content_hash):
    return screen_metadata(
        conn, file_id=file_id, content_hash=content_hash,
        observations=observations_for_version(conn, file_id, content_hash),
        tool_producer_strings=TOOL_STRINGS,
        metadata_property_names=PROPERTY_NAMES)


@pytest.fixture()
def docx(p6_conn, tmp_path):
    return _file(p6_conn, tmp_path, name="Wash U.docx", body=b"PK\x03\x04docx")


# --- the two tiers, and the swap that must fail -------------------------------

def test_a_tool_string_is_suppressed_and_never_demoted(p6_conn, docx):
    # Done-means 22, first half. §2.2: such a value "should not be mistaken for
    # meaningful content" -- not "for strong content". A tool name is a true fact
    # about the software and no evidence at all about the document, so there is
    # nothing a `possible` fact could be weak about.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-tool", file_id=file_id,
                    content_hash=content_hash, raw="python-docx")

    assert discount(tool, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    assert discount(tool, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) != DEMOTE

    survivors = _screen(p6_conn, file_id, content_hash)
    assert survivors == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    assert field_permitted(tool, "authored_by", tool_producer_strings=TOOL_STRINGS,
                           metadata_property_names=PROPERTY_NAMES) is False


def test_a_suppressed_tool_string_writes_exactly_one_unresolved_row(p6_conn, docx):
    # Done-means 22's second clause, and B7: the refusal is a record, not a gap.
    # §8.5 asks under Fact quality "Did it abstain when evidence was absent?" and an
    # absent row cannot answer it.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-tool", file_id=file_id,
                    content_hash=content_hash, raw="python-docx")
    _screen(p6_conn, file_id, content_hash)

    rows = unresolved_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert rows[0]["reason"] == "discounted_tool_metadata"
    assert rows[0]["field_key"] == AUTHORSHIP_FIELDS[0] == "authored_by"
    assert json.loads(rows[0]["evidence_refs"]) == [cite(tool)]


def test_a_human_name_is_demoted_and_never_suppressed(p6_conn, docx):
    # Done-means 22, second half, and §2.3: author metadata "should remain supporting
    # information only". Supporting information is KEPT. Suppressing it here would
    # lose real authorship and would write an abstention that did not happen.
    file_id, content_hash = docx
    person = _observe(p6_conn, run_id="run-person", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="Author")

    assert discount(person, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == DEMOTE
    assert discount(person, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) != SUPPRESS

    survivors = _screen(p6_conn, file_id, content_hash)
    assert [one.raw_value for one in survivors] == ["Jane Chen"]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_demoted_value_may_populate_authored_by_and_no_other_field(p6_conn, docx):
    # §3.8: "It should avoid using authorship or creator identity as a destination
    # dimension ... Authorship is usually metadata; the document's purpose, project,
    # subject, or target is more informative for placement."
    file_id, content_hash = docx
    person = _observe(p6_conn, run_id="run-person", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="creator")

    assert field_permitted(person, "authored_by", tool_producer_strings=TOOL_STRINGS,
                           metadata_property_names=PROPERTY_NAMES) is True
    for field_key in NON_AUTHORSHIP_FIELDS:
        assert field_permitted(
            person, field_key, tool_producer_strings=TOOL_STRINGS,
            metadata_property_names=PROPERTY_NAMES) is False, field_key


def test_the_two_tiers_are_different_outcomes_for_the_same_slot(p6_conn, docx):
    # The anti-swap assertion, stated once with both values in one place: same file,
    # same zone, same property name, two values, two different tiers.
    file_id, content_hash = docx
    tool = _observe(p6_conn, run_id="run-a", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", slot="Creator")
    person = _observe(p6_conn, run_id="run-b", file_id=file_id,
                      content_hash=content_hash, raw="Jane Chen", slot="Author")
    kwargs = dict(tool_producer_strings=TOOL_STRINGS,
                  metadata_property_names=PROPERTY_NAMES)

    assert (discount(tool, **kwargs), discount(person, **kwargs)) == (SUPPRESS, DEMOTE)
    assert [one.raw_value for one in _screen(p6_conn, file_id, content_hash)] == [
        "Jane Chen"]
    assert len(unresolved_for_file(p6_conn, file_id, content_hash)) == 1


# --- §3.8's half of Done-means 13 ---------------------------------------------

def test_authored_by_is_never_destination_eligible(p6_conn):
    # Done-means 13. §3.8: "A folder should not become a collection point for
    # everything produced by the same person or organization."
    for field_key in AUTHORSHIP_FIELDS:
        row = get_field(p6_conn, field_key)
        assert row is not None, field_key
        assert not row["destination_eligible"], field_key


# --- P4's fixture 6, verbatim --------------------------------------------------

def test_fixture_six_is_a_discount_target_and_its_direct_reliability_is_untouched(
        p6_conn, tmp_path):
    # M4 in one assertion: P4 emits `python-docx` with reliability `direct` because
    # `direct` describes the SLOT. P6 discounts the VALUE and changes nothing P4
    # wrote -- the two statements are about different things and both stay true.
    fixture = by_number(6)
    assert fixture.observations[0].raw_value == "python-docx"
    assert fixture.observations[0].reliability == "direct"
    assert fixture.observations[0].locator == "metadata:field=Producer"

    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)

    assert is_discount_target(fixture.observations[0],
                              metadata_property_names=PROPERTY_NAMES) is True
    assert discount(fixture.observations[0], tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    still = observations_by_key(p6_conn, fixture.observations[0].observation_key)
    assert [(one.raw_value, one.reliability) for one in still] == [
        ("python-docx", "direct")]


# --- what is and is not a target ------------------------------------------------

def test_a_value_outside_the_metadata_zone_is_not_a_discount_target(p6_conn, docx):
    # Catalogue 01's `match_field`: zone `metadata` PLUS a listed property name. A
    # body paragraph that happens to read "python-docx" is text, and text is §3.7's.
    file_id, content_hash = docx
    body = _observe(p6_conn, run_id="run-body", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", zone="body",
                    slot=None, reliability="possible")

    assert is_discount_target(body, metadata_property_names=PROPERTY_NAMES) is False
    assert discount(body, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == NOT_METADATA
    assert [one.raw_value for one in _screen(p6_conn, file_id, content_hash)] == [
        "python-docx"]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_metadata_slot_not_on_the_injected_names_is_not_a_target(p6_conn, docx):
    # Catalogue 01: "A slot not on this list is not a discount target." `Subject` is
    # a real PDF info-dictionary slot and is deliberately absent from the list.
    file_id, content_hash = docx
    subject = _observe(p6_conn, run_id="run-subject", file_id=file_id,
                      content_hash=content_hash, raw="python-docx", slot="Subject")

    assert is_discount_target(subject,
                              metadata_property_names=PROPERTY_NAMES) is False
    assert discount(subject, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == NOT_METADATA


def test_a_metadata_observation_with_no_field_segment_is_not_a_target(p6_conn, docx):
    # P4's `container_path` is a tuple and may be empty. Reading `[0]` unguarded is
    # the crash this asserts is not there.
    file_id, content_hash = docx
    bare = _observe(p6_conn, run_id="run-bare", file_id=file_id,
                    content_hash=content_hash, raw="python-docx", slot=None)
    assert is_discount_target(bare, metadata_property_names=PROPERTY_NAMES) is False


# --- ordering: before the ranking, not after -----------------------------------

def test_the_discount_fires_before_ranking_and_the_second_candidate_wins(
        p6_conn, docx):
    # The requirement, in its own words: run a corpus where the discounted string
    # would otherwise be the top-ranked candidate and show the field is filled by the
    # second candidate rather than left empty for the wrong reason. `facts.facets` is
    # Task 11's and is not imported; "top-ranked" is stated here as the highest
    # occurrence count, which is what makes the setup adversarial in the first place.
    file_id, content_hash = docx
    _observe(p6_conn, run_id="run-tool", file_id=file_id, content_hash=content_hash,
             raw="python-docx", occurrences=40)
    _observe(p6_conn, run_id="run-real", file_id=file_id, content_hash=content_hash,
             raw="Columbia", zone="heading", slot=None, reliability="possible",
             occurrences=3)

    before = observations_for_version(p6_conn, file_id, content_hash)
    assert max(before, key=lambda one: one.occurrence_count).raw_value == "python-docx"

    survivors = _screen(p6_conn, file_id, content_hash)
    assert survivors != ()
    assert max(survivors, key=lambda one: one.occurrence_count).raw_value == "Columbia"


def test_screening_preserves_the_order_it_was_given(p6_conn, docx):
    # Task 7's read is already a total order keyed on `observation_key`. Screening
    # filters; it must not reorder, or every downstream tie changes for a reason that
    # has nothing to do with the corpus (§8.5 replay).
    file_id, content_hash = docx
    for index, raw in enumerate(("Columbia", "Wash U", "UChicago")):
        _observe(p6_conn, run_id=f"run-{index}", file_id=file_id,
                 content_hash=content_hash, raw=raw, zone="heading", slot=None,
                 reliability="possible")
    _observe(p6_conn, run_id="run-tool", file_id=file_id, content_hash=content_hash,
             raw="python-docx")

    given = observations_for_version(p6_conn, file_id, content_hash)
    survivors = _screen(p6_conn, file_id, content_hash)
    assert [cite(one) for one in survivors] == [
        cite(one) for one in given if one.raw_value != "python-docx"]


# --- matching: normalized for comparison, never written back --------------------

def test_the_matcher_normalizes_for_comparison_only(p6_conn, docx):
    # Catalogue 01: "Compare against the raw value with Unicode NFC applied and
    # leading/trailing whitespace stripped, for comparison only. P4 RAW-1/RAW-2 keep
    # the stored raw_value byte-for-byte untouched."
    file_id, content_hash = docx
    padded = _observe(p6_conn, run_id="run-pad", file_id=file_id,
                      content_hash=content_hash, raw="  PYTHON-DOCX ")

    assert discount(padded, tool_producer_strings=TOOL_STRINGS,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS
    still = observations_by_key(p6_conn, padded.observation_key)
    assert [one.raw_value for one in still] == ["  PYTHON-DOCX "]


def test_a_composed_and_a_decomposed_value_match_the_same_entry(p6_conn, docx):
    # NFC, from the same clause. The two spellings of the same string must not give
    # two different tiers, because which one an extractor emits is the reader's
    # accident and not a fact about the file.
    file_id, content_hash = docx
    decomposed = unicodedata.normalize("NFD", "Café Writer")
    assert decomposed != "Café Writer"
    observation = _observe(p6_conn, run_id="run-nfd", file_id=file_id,
                           content_hash=content_hash, raw=decomposed)
    matcher = (_exact("Café Writer", case_sensitive=False),)

    assert discount(observation, tool_producer_strings=matcher,
                    metadata_property_names=PROPERTY_NAMES) == SUPPRESS


def test_one_unresolved_row_even_when_several_slots_carry_a_tool_string(
        p6_conn, docx):
    # Done-means 22 says ONE row. A DOCX commonly writes the same generator into
    # `creator` and `lastModifiedBy`; two rows would double-count one refusal and
    # make §8.5's abstention count wrong.
    file_id, content_hash = docx
    first = _observe(p6_conn, run_id="run-1", file_id=file_id,
                     content_hash=content_hash, raw="python-docx", slot="creator")
    second = _observe(p6_conn, run_id="run-2", file_id=file_id,
                      content_hash=content_hash, raw="python-docx",
                      slot="lastModifiedBy")
    _screen(p6_conn, file_id, content_hash)

    rows = unresolved_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        {cite(first), cite(second)})


def test_screening_a_version_with_nothing_to_discount_writes_no_row(p6_conn, docx):
    # An abstention that did not happen must not be recorded as one (B7).
    file_id, content_hash = docx
    _observe(p6_conn, run_id="run-clean", file_id=file_id,
             content_hash=content_hash, raw="Columbia", zone="heading", slot=None,
             reliability="possible")
    assert len(_screen(p6_conn, file_id, content_hash)) == 1
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


# --- the injection --------------------------------------------------------------

def test_the_list_and_the_property_names_have_no_defaults(p6_conn, docx):
    # Catalogue 01: "P6 receives this list as data at construction ... It is not
    # imported as a module-level constant."
    file_id, content_hash = docx
    observation = _observe(p6_conn, run_id="run-inj", file_id=file_id,
                           content_hash=content_hash, raw="python-docx")
    with pytest.raises(TypeError):
        discount(observation)
    with pytest.raises(TypeError):
        discount(observation, tool_producer_strings=TOOL_STRINGS)
    with pytest.raises(TypeError):
        is_discount_target(observation)


def test_facts_discount_holds_no_producer_string_and_no_property_catalogue():
    # Runtime introspection over the module namespace, not a source-text search.
    # Copying catalogue 01 into `src/facts/` would satisfy Task 25's letter and
    # destroy its point, so the guard is here as well as there.
    literals = _code_strings(discount_module)
    assert "python-docx" not in literals
    assert not [one for one in literals if one.startswith("Mozilla")]
    assert literals & PROPERTY_NAMES == set()

    catalogues = {name: value for name, value in vars(discount_module).items()
                  if not name.startswith("_")
                  and name not in {"AUTHORSHIP_FIELDS", "DISCOUNT_OUTCOMES"}
                  and isinstance(value, (tuple, list, dict, set, frozenset))}
    assert catalogues == {}
    assert len(AUTHORSHIP_FIELDS) == 1
    assert len(DISCOUNT_OUTCOMES) == 3

# tests/p6/test_p6_dates.py
"""§3.10 -- Done-means 10, and A03's ZIP code and device model as date candidates."""
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, REQUIRED_PATTERN_IDS, SEASON_YEAR,
    DateMatch, DatePattern, DatePatterns, MissingRequiredPattern, NoPatternIdentity,
    date_candidates, date_matches, parse_exact,
)
from facts.facets import fill_or_abstain, rank
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.10's catalogue beyond the three named patterns is Deferred, so these three
#: expressions are the TEST's and live nowhere in `src/facts`. Each is dedicated to
#: exactly one of the design's three worked cases.
SPRING_2025 = DatePattern(
    pattern_id=SEASON_YEAR,
    pattern=re.compile(r"\b(?:Spring|Summer|Fall|Autumn|Winter) \d{4}\b"))
AY_2024_25 = DatePattern(
    pattern_id=ACADEMIC_YEAR_RANGE, pattern=re.compile(r"\bAY \d{4}-\d{2}\b"))
MICHAELMAS_TERM_2024 = DatePattern(
    pattern_id=NAMED_TERM_YEAR,
    pattern=re.compile(
        r"\b(?:Michaelmas|Hilary|Trinity|Lent|Easter) Term \d{4}\b"))
PATTERNS = DatePatterns(patterns=(SPRING_2025, AY_2024_25, MICHAELMAS_TERM_2024))

ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}


def _record(conn, tmp_path, *, name, body):
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("page", 1),)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _resolve(conn, tmp_path, *, name, raw, field_key="term"):
    file_id, content_hash = _record(conn, tmp_path, name=name, body=raw.encode())
    observation = _observe(conn, run_id=f"run-{name}", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5)
    return file_id, content_hash, fact_id


# --- the three named patterns are required, dedicated, and identified --------

def test_the_three_named_academic_term_patterns_are_required():
    # §3.10: "Academic terms such as Spring 2025, AY 2024-25, and Michaelmas Term 2024
    # require dedicated patterns rather than generic parsing."
    assert REQUIRED_PATTERN_IDS == ("season_year", "academic_year_range",
                                    "named_term_year")
    for dropped in range(3):
        remaining = tuple(one for index, one in enumerate(PATTERNS.patterns)
                          if index != dropped)
        with pytest.raises(MissingRequiredPattern):
            DatePatterns(patterns=remaining)


def test_the_catalogue_beyond_the_three_is_injected_and_empty_by_default():
    # "Date and academic-term regex catalogue beyond the three named patterns |
    # §3.10 | ... The rest is manual."
    assert PATTERNS.extra_pattern_ids == ()
    extended = DatePatterns(patterns=PATTERNS.patterns + (
        DatePattern(pattern_id="iso_day", pattern=re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),))
    assert extended.extra_pattern_ids == ("iso_day",)


def test_duplicate_pattern_ids_are_refused():
    with pytest.raises(ValueError):
        DatePatterns(patterns=PATTERNS.patterns + (SPRING_2025,))


@pytest.mark.parametrize("raw,expected_id", [
    ("Spring 2025", SEASON_YEAR),
    ("AY 2024-25", ACADEMIC_YEAR_RANGE),
    ("Michaelmas Term 2024", NAMED_TERM_YEAR),
])
def test_each_named_term_is_claimed_by_its_own_dedicated_pattern(raw, expected_id):
    # Done-means 10 asserts dedication "by pattern identity in the result rather than
    # by the value alone", which is what `DateMatch.pattern_id` is for.
    observation = Observation(
        file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="r")
    found = date_matches(observation, patterns=PATTERNS)
    assert [one.pattern_id for one in found] == [expected_id]
    assert [one.value for one in found] == [raw]


def test_no_pattern_claims_another_patterns_case():
    # Three dedicated patterns, not one general one wearing three ids.
    for one in PATTERNS.patterns:
        claimed = [raw for raw in ("Spring 2025", "AY 2024-25",
                                   "Michaelmas Term 2024")
                   if one.pattern.search(raw)]
        assert len(claimed) == 1


# --- Done-means 10, positive half -------------------------------------------

@pytest.mark.parametrize("raw", ["Spring 2025", "AY 2024-25",
                                 "Michaelmas Term 2024"])
def test_each_named_term_produces_exactly_one_term_fact(raw, p6_conn, tmp_path):
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{raw.replace(' ', '-')}.txt", raw=raw)
    assert fact_id is not None
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert [(r["field_key"], r["canonical_value"], r["reliability_state"])
            for r in rows] == [("term", raw, "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_a_term_fact_cites_the_observation_that_carried_the_span(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="syllabus.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-cite", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="term",
                    candidates=rank(date_candidates(observation, patterns=PATTERNS),
                                    zone_weight=ZONE_WEIGHT,
                                    tier_weight=TIER_WEIGHT),
                    minimum_score=1.0, minimum_margin=0.5)
    refs = json.loads(
        facts_for_file(p6_conn, file_id, content_hash)[0]["evidence_refs"])
    assert refs == [observation.observation_key]


# --- Done-means 10, negative half: §3.10's four look-alike number kinds ------

@pytest.mark.parametrize("raw,name", [
    ("v2024", "version"),
    ("build 20240117", "build"),
    ("Ship to Cambridge MA 02139 by Friday.", "zip"),
    ("Receipt for one XPS 13 laptop.", "device"),
    ("BUSIB 4300", "course_identifier"),
])
def test_a_number_that_only_looks_like_a_year_produces_no_date_fact(
        raw, name, p6_conn, tmp_path):
    # §3.10: "file names and documents frequently contain numbers that look like years
    # but are course identifiers, version numbers, build numbers, ZIP codes, or other
    # unrelated values." A03's two subjects are the ZIP and the device model.
    file_id, content_hash, fact_id = _resolve(
        p6_conn, tmp_path, name=f"{name}.txt", raw=raw)
    assert fact_id is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="term")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_a_bare_year_is_not_a_candidate_without_a_pattern_that_claims_it(
        p6_conn, tmp_path):
    # The trap §3.10 exists to close: `2025` on its own is a four-digit number, and
    # no pattern in the catalogue claims it.
    assert date_matches(
        Observation(file_id="f", content_hash="a" * 64, extractor_name="pdf.text",
                    extractor_version="1.0.0", source_type="text_document",
                    raw_value="2025", location=Location("heading", ()),
                    occurrence_count=1, observed_at=CLOCK, reliability="possible",
                    run_id="r"),
        patterns=PATTERNS) == ()


# --- no fuzzy path exists ----------------------------------------------------

def test_there_is_no_route_to_a_value_without_a_pattern_id():
    # "no bare four-digit-year regex reachable without a pattern id, and no fallback
    # that accepts a candidate a pattern rejected."
    with pytest.raises(NoPatternIdentity):
        parse_exact("Spring 2025", pattern_id="")
    with pytest.raises(NoPatternIdentity):
        parse_exact("   ", pattern_id=SEASON_YEAR)
    with pytest.raises(NoPatternIdentity):
        DatePattern(pattern_id="", pattern=re.compile(r"x"))


def test_parse_exact_reinterprets_nothing():
    # "then parsed without fuzzy matching" -- whitespace runs collapse and that is
    # the entire transformation. No month table, no locale, no century expansion.
    assert parse_exact("Spring  2025", pattern_id=SEASON_YEAR) == "Spring 2025"
    assert parse_exact("AY 2024-25", pattern_id=ACADEMIC_YEAR_RANGE) == "AY 2024-25"
    assert parse_exact("Michaelmas Term 2024",
                       pattern_id=NAMED_TERM_YEAR) == "Michaelmas Term 2024"
    assert parse_exact("Fall 25", pattern_id=SEASON_YEAR) == "Fall 25"


def test_no_fuzzy_parser_is_imported_or_reachable():
    # Runtime introspection, not a source-text search: a fuzzy parser would arrive as
    # a callable in the module namespace or as an import.
    import facts.dates as module
    names = {name.lower() for name in vars(module)}
    assert not any(marker in name for name in names
                   for marker in ("dateutil", "fuzzy", "guess", "strptime",
                                  "parse_date", "dateparser"))
    import sys
    assert "dateutil" not in sys.modules


def test_the_module_authors_no_regular_expression():
    # §3.10's catalogue is Deferred. The ids are the design's three cases; every
    # expression that recognises them is the caller's.
    import facts.dates as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, re.Pattern)] == []
    assert [name for name, value in vars(module).items()
            if isinstance(value, (DatePattern, DatePatterns))] == []


def test_a_string_is_not_accepted_where_an_explicit_expression_is_required():
    with pytest.raises(ValueError):
        DatePattern(pattern_id=SEASON_YEAR, pattern=r"\bSpring \d{4}\b")


# --- several spans in one observation ----------------------------------------

def test_two_terms_in_one_raw_value_are_two_candidates_and_fill_nothing(
        p6_conn, tmp_path):
    # Two dedicated patterns each claim a span, the two candidates tie, and §3.7's
    # margin refuses -- a date is ranked like any other facet and gets no exemption.
    raw = "Spring 2025 and Michaelmas Term 2024"
    file_id, content_hash = _record(p6_conn, tmp_path, name="both.txt",
                                    body=raw.encode())
    observation = _observe(p6_conn, run_id="r-both", file_id=file_id,
                           content_hash=content_hash, raw=raw)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert sorted(c.value for c in candidates) == ["Michaelmas Term 2024",
                                                   "Spring 2025"]
    assert fill_or_abstain(
        p6_conn, file_id=file_id, content_hash=content_hash, field_key="term",
        candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                        tier_weight=TIER_WEIGHT),
        minimum_score=1.0, minimum_margin=0.5) is None
    assert [r["reason"] for r in unresolved_for_file(
        p6_conn, file_id, content_hash, field_key="term")] == ["below_margin"]


def test_a_candidate_carries_p4s_zone_so_the_ranker_can_weight_it(p6_conn, tmp_path):
    # §3.7's positional weighting applies to dates too; the producer supplies the
    # zone and never the weight.
    file_id, content_hash = _record(p6_conn, tmp_path, name="pos.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-pos", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025",
                           zone="filename")
    candidate = date_candidates(observation, patterns=PATTERNS)[0]
    assert candidate.zone == "filename"
    assert candidate.signal_tier is None
    assert candidate.score == 1.0


def test_date_candidates_is_date_matches_projected_onto_the_facet_shape(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="proj.txt",
                                    body=b"Spring 2025")
    observation = _observe(p6_conn, run_id="r-proj", file_id=file_id,
                           content_hash=content_hash, raw="Spring 2025")
    found = date_matches(observation, patterns=PATTERNS)
    candidates = date_candidates(observation, patterns=PATTERNS)
    assert len(found) == len(candidates) == 1
    assert isinstance(found[0], DateMatch)
    assert candidates[0].value == found[0].value
    assert candidates[0].evidence_refs == (found[0].evidence_ref,)

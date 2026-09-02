# tests/p6/test_p6_date_facts.py
"""§3.10's producer: `date_candidates` -> `rank` -> `fill_or_abstain`, wired.

`facts.dates` published the candidates and `facts.facets` published the ranker, and
nothing in `src/` joined them -- so Done-means 10's three written forms produced no
term fact at all, and the one form a deployment reimplemented inline reached the tree
as a `direct` fact, which the SPEC's production rules forbid in as many words:

    "Filesystem timestamps are direct; dates recovered from text or filenames are
    not, and take the §3.10 path."  (P6 SPEC:409-410)

Two things are asserted here that no unit test in `test_p6_dates.py` could reach,
because both are properties of the JOIN and not of either half:

* **one term, one value, whatever it was written as.** `Spring 2026`, `Spring2026`
  and `2026-Spring` are one semester. Canonicalised at the CANDIDATE, they aggregate
  into one ranked candidate and fill one facet; canonicalised any later they are two
  candidates that tie, and §3.7's margin refuses both -- so a person who wrote the
  term two ways would get no term at all, or two folders for one term. Both of those
  failures are on this project's record (`65` §4.2, and the run of 2026-08-31).
* **two terms that genuinely differ stay two.** The canonicaliser above is the whole
  risk of the fix: one that reduced `AY 2024-25` and `AY 2025-26` to the same string
  would file two academic years into one folder, which is worse than the bug.
"""
import json
import re
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts.date_facts import date_facts
from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, SEASON_YEAR,
    DatePattern, DatePatterns,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

# --- the catalogue, which is the CALLER'S ------------------------------------
#
# §3.10's regex catalogue is Deferred and `facts.dates` authors not one character of
# it, so the three expressions and the three canonicalisers below are the TEST'S --
# and they are, character for character, the ones the composition root must bind.
# They live here so the rule they express is proved by a test rather than asserted in
# a comment at the one call site.

_SEASON = r"(?:Spring|Summer|Fall|Autumn|Winter)"
_TERM_NAME = r"(?:Michaelmas|Hilary|Trinity|Lent|Easter)"

#: `Spring 2025`, and the other three ways a person writes the same semester.
SEASON_YEAR_SOURCE = (
    rf"\b(?:{_SEASON}[ \-_]?[0-9]{{4}}|[0-9]{{4}}[ \-_]?{_SEASON})\b")
#: `AY 2024-25`.
ACADEMIC_YEAR_SOURCE = r"\bAY[ \-_]?[0-9]{4}[ ]?[-/][ ]?[0-9]{2}\b"
#: `Michaelmas Term 2024`, and `Michaelmas 2024`, which is the same term.
NAMED_TERM_SOURCE = rf"\b{_TERM_NAME}(?:[ \-_]Term)?[ \-_][0-9]{{4}}\b"


def canonical_season_year(raw: str) -> str:
    """`Spring 2026`, `Spring2026`, `2026-Spring`, `SPRING 2026` -> `Spring2026`."""
    season = re.search(_SEASON, raw, re.IGNORECASE).group(0)
    year = re.search(r"[0-9]{4}", raw).group(0)
    return f"{season.capitalize()}{year}"


def canonical_academic_year(raw: str) -> str:
    """`AY 2024-25`, `AY2024/25`, `ay 2024 - 25` -> `AY2024-25`."""
    match = re.search(r"([0-9]{4})[^0-9]+([0-9]{2})", raw)
    return f"AY{match.group(1)}-{match.group(2)}"


def canonical_named_term(raw: str) -> str:
    """`Michaelmas Term 2024`, `michaelmas 2024` -> `Michaelmas2024`."""
    name = re.search(_TERM_NAME, raw, re.IGNORECASE).group(0)
    year = re.search(r"[0-9]{4}", raw).group(0)
    return f"{name.capitalize()}{year}"


PATTERNS = DatePatterns(patterns=(
    DatePattern(pattern_id=SEASON_YEAR,
                pattern=re.compile(SEASON_YEAR_SOURCE, re.IGNORECASE),
                canonical=canonical_season_year),
    DatePattern(pattern_id=ACADEMIC_YEAR_RANGE,
                pattern=re.compile(ACADEMIC_YEAR_SOURCE, re.IGNORECASE),
                canonical=canonical_academic_year),
    DatePattern(pattern_id=NAMED_TERM_YEAR,
                pattern=re.compile(NAMED_TERM_SOURCE, re.IGNORECASE),
                canonical=canonical_named_term),
))

#: P4's fifteen zones. Every one carries a weight, because `rank` raises rather than
#: defaulting and a corpus reaches zones a test did not think of.
ZONE_WEIGHT = {"filename": 3.0, "title": 3.0, "heading": 2.0, "body": 1.0,
               "header_footer": 0.25, "metadata": 1.0, "path": 1.0, "table": 1.0,
               "notes": 1.0, "link": 1.0, "annotation": 1.0, "reference_list": 0.5,
               "manifest": 1.0, "ocr": 1.0, "transcript": 1.0}
TIER_WEIGHT = {1: 4.0, 2: 2.0, 3: 1.0}
MINIMUM_SCORE = 1.0
MINIMUM_MARGIN = 0.5


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


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="body"):
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


def _run(conn, tmp_path, *, name, texts, field_key="term"):
    """One file, one observation per text, then the producer over the version."""
    file_id, content_hash = _record(conn, tmp_path, name=name,
                                    body="\n".join(texts).encode())
    for index, text in enumerate(texts):
        _observe(conn, run_id=f"run-{name}-{index}", file_id=file_id,
                 content_hash=content_hash, raw=text)
    written = date_facts(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key, patterns=PATTERNS,
                         zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT,
                         minimum_score=MINIMUM_SCORE,
                         minimum_margin=MINIMUM_MARGIN)
    return file_id, content_hash, written


def _values(conn, file_id, content_hash, field_key="term"):
    return [row["canonical_value"]
            for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == field_key and row["active"]]


# --- Done-means 10: all three written forms, each one term fact --------------

@pytest.mark.parametrize("written,expected", [
    ("Spring 2025", "Spring2025"),
    ("AY 2024-25", "AY2024-25"),
    ("Michaelmas Term 2024", "Michaelmas2024"),
])
def test_each_of_the_three_written_forms_produces_one_term_fact(
        written, expected, p6_conn, tmp_path):
    # "`Spring 2025`, `AY 2024-25`, and `Michaelmas Term 2024` each produce exactly
    # one term fact (§3.10)" -- Done-means 10. Two of the three produced NOTHING
    # before this producer existed, which is most of the UK and much of the US.
    file_id, content_hash, written_ids = _run(
        p6_conn, tmp_path, name=f"{expected}.txt", texts=[f"Coursework {written}"])
    assert len(written_ids) == 1
    assert _values(p6_conn, file_id, content_hash) == [expected]
    assert unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key="term") == []


def test_a_term_fact_is_validated_and_never_direct(p6_conn, tmp_path):
    # SPEC:409-410: "Filesystem timestamps are direct; dates recovered from text or
    # filenames are not, and take the §3.10 path." This IS the §3.10 path, and its
    # end is `fill_or_abstain`, whose state is `validated`.
    file_id, content_hash, _ = _run(p6_conn, tmp_path, name="state.txt",
                                    texts=["Spring 2025"])
    rows = [row for row in facts_for_file(p6_conn, file_id, content_hash)
            if row["field_key"] == "term"]
    assert [row["reliability_state"] for row in rows] == ["validated"]
    assert [row["origin"] for row in rows] == ["rule"]


def test_a_term_fact_cites_the_observation_the_span_came_from(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="cite.txt",
                                    body=b"Michaelmas Term 2024")
    observation = _observe(p6_conn, run_id="r-cite", file_id=file_id,
                           content_hash=content_hash, raw="Michaelmas Term 2024")
    date_facts(p6_conn, file_id=file_id, content_hash=content_hash,
               field_key="term", patterns=PATTERNS, zone_weight=ZONE_WEIGHT,
               tier_weight=TIER_WEIGHT, minimum_score=MINIMUM_SCORE,
               minimum_margin=MINIMUM_MARGIN)
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    assert json.loads(row["evidence_refs"]) == [observation.observation_key]


# --- TWIN 1: one term is one value, however it was written -------------------

def test_the_three_spellings_of_one_semester_are_one_fact_and_not_two_that_tie(
        p6_conn, tmp_path):
    # THE WHOLE POINT. Canonicalised at the candidate, three readings of one semester
    # aggregate into ONE ranked candidate whose score is their sum. Canonicalised any
    # later, they are three candidates inside §3.7's margin of each other and
    # `fill_or_abstain` refuses all three -- a person who wrote the term two ways
    # would end with no term folder, or with one folder per spelling.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="spellings.txt",
        texts=["Spring 2026 syllabus", "Spring2026 homework", "2026-Spring lab"])
    assert len(written) == 1
    assert _values(p6_conn, file_id, content_hash) == ["Spring2026"]
    assert unresolved_for_file(p6_conn, file_id, content_hash,
                               field_key="term") == []
    # All three readings are cited, because all three supported the one value.
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    assert len(json.loads(row["evidence_refs"])) == 3


def test_one_observation_carrying_two_spellings_still_fills_one_facet(
        p6_conn, tmp_path):
    # The same collapse, inside a single reading rather than across three.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="one-line.txt",
        texts=["SPRING2026 midterm, rescheduled from 2026 Spring."])
    assert len(written) == 1
    assert _values(p6_conn, file_id, content_hash) == ["Spring2026"]


# --- TWIN 2: two terms that differ must stay two -----------------------------

@pytest.mark.parametrize("first,second", [
    # the year differs
    ("Spring 2026", "Spring 2025"),
    # the season differs
    ("Spring 2026", "Fall 2026"),
    # the academic year differs, and only the second half of it in one case
    ("AY 2024-25", "AY 2025-26"),
    # the named term differs on the name alone
    ("Michaelmas Term 2024", "Hilary Term 2024"),
    # and a season year is not an academic year range that shares its first year
    ("Spring 2024", "AY 2024-25"),
])
def test_two_terms_that_genuinely_differ_are_never_collapsed_into_one(
        first, second, p6_conn, tmp_path):
    # The risk the fix creates. An over-broad canonicaliser -- one that kept only the
    # leading four digits, or dropped the term's name, or dropped the range's second
    # half -- would file two different terms into one folder, which is worse than the
    # bug it was written to fix. Both readings on ONE file, so the producer itself
    # has to keep them apart: collapsed, they would be one candidate and would FILL;
    # kept apart they are two candidates inside the margin, and §3.7 refuses.
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="different.txt", texts=[first, second])
    assert written == ()
    assert _values(p6_conn, file_id, content_hash) == []
    assert [row["reason"] for row in unresolved_for_file(
        p6_conn, file_id, content_hash, field_key="term")] == ["below_margin"]


def test_the_canonicaliser_maps_the_written_forms_onto_distinct_values():
    # The same guard stated over the rule itself, so a future edit to it is caught at
    # the canonicaliser rather than three layers downstream.
    same = ["Spring 2026", "Spring2026", "2026-Spring", "SPRING 2026", "spring_2026"]
    assert {canonical_season_year(one) for one in same} == {"Spring2026"}
    assert {canonical_academic_year(one)
            for one in ["AY 2024-25", "AY2024-25", "ay 2024/25"]} == {"AY2024-25"}
    assert {canonical_named_term(one)
            for one in ["Michaelmas Term 2024", "michaelmas 2024",
                        "MICHAELMAS-TERM-2024"]} == {"Michaelmas2024"}
    different = ["Spring 2026", "Spring 2025", "Fall 2026", "Winter 2026"]
    assert len({canonical_season_year(one) for one in different}) == len(different)
    ranges = ["AY 2024-25", "AY 2025-26", "AY 2024-26"]
    assert len({canonical_academic_year(one) for one in ranges}) == len(ranges)
    named = ["Michaelmas Term 2024", "Hilary Term 2024", "Michaelmas Term 2025"]
    assert len({canonical_named_term(one) for one in named}) == len(named)


# --- Done-means 10's negative half, through the producer ---------------------

@pytest.mark.parametrize("raw", [
    "v2024", "build 20240117", "Ship to Cambridge MA 02139 by Friday.",
    "Receipt for one XPS 13 laptop.", "BUSIB 4300", "2025",
])
def test_a_number_that_only_looks_like_a_year_produces_no_term_fact(
        raw, p6_conn, tmp_path):
    file_id, content_hash, written = _run(
        p6_conn, tmp_path, name="lookalike.txt", texts=[raw])
    assert written == ()
    assert _values(p6_conn, file_id, content_hash) == []
    assert [row["reason"] for row in unresolved_for_file(
        p6_conn, file_id, content_hash, field_key="term")] == [
            "no_candidate_evidence"]


# --- the producer holds no opinion of its own --------------------------------

def test_the_producer_authors_no_expression_no_weight_and_no_threshold():
    # The same runtime introspection `facts.dates` carries. Every number and every
    # pattern in this module's answers arrived through its signature.
    import facts.date_facts as module
    assert [name for name, value in vars(module).items()
            if isinstance(value, re.Pattern)] == []
    assert [name for name, value in vars(module).items()
            if isinstance(value, (DatePattern, DatePatterns))] == []
    assert [name for name, value in vars(module).items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            and not name.startswith("__") and value not in (0, 1)] == []


def test_the_producer_refuses_to_run_without_the_thresholds_and_the_weights():
    # F8: a default here would answer a Deferred question. Absent means refuse.
    import inspect
    signature = inspect.signature(date_facts)
    required = {"patterns", "zone_weight", "tier_weight", "minimum_score",
                "minimum_margin", "field_key"}
    for name in required:
        assert signature.parameters[name].default is inspect.Parameter.empty


# --- the composition root must not claim `term` twice ------------------------

def test_no_direct_slot_claims_a_field_the_date_producer_fills():
    # THE COLLISION, stated as a test rather than as a warning in a report. Two
    # producers that can both write `term` for one file version give a person two
    # term folders: `file_facts` has no uniqueness constraint over
    # (file_id, content_hash, field_key), so nothing below this line would catch it.
    import cli
    assert "term" not in {slot.field_key for slot in cli.DIRECT_SLOTS.slots}

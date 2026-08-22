# tests/p6/test_p6_facets.py
"""§3.7 -- Done-means 7 and 9, adversarial cases A01 and A02."""
import itertools
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ZONES

from facts.facets import (
    Candidate, MissingWeight, fill_or_abstain, rank, word_boundary_match,
)
from facts.file_facts import facts_for_file
from facts.unresolved import unresolved_for_file

CLOCK = "2026-08-22T00:00:00Z"

#: §3.7's weights are Deferred -- "Positional weight per document zone | §3.7, §2.2 |
#: Zones arrive from P4's `location`; the weights are manual." These are the test's
#: own, injected at every call, and they exist nowhere in `src/facts`.
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
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, occurrence_count=1,
             signal_tier=None, source_type="text_document", analysis_tier="native"):
    if conn.execute("SELECT 1 FROM extraction_runs WHERE run_id = ?",
                    (run_id,)).fetchone() is None:
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name="text.plain", extractor_version="1.0.0",
            source_type=source_type, analysis_tier=analysis_tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="text.plain",
        extractor_version="1.0.0", source_type=source_type, raw_value=raw,
        location=Location(zone, (Segment("page", 1),)),
        occurrence_count=occurrence_count, observed_at=CLOCK,
        reliability="possible", run_id=run_id, signal_tier=signal_tier)
    record_observation(conn, observation)
    return observation


def _candidate(observation, value, score=1.0):
    return Candidate(value=value, score=score,
                     evidence_refs=(observation.observation_key,),
                     zone=observation.location.zone,
                     signal_tier=observation.signal_tier)


# --- the word-boundary rule, which is the whole of A01 and A02 -----------------

def test_mit_is_not_found_inside_submit():
    # §3.7, verbatim: "names such as MIT can be found inside "submit,"" -- and A01
    # carries that exact sentence as `Please submit the completed form.`
    assert word_boundary_match("MIT", "Please submit the completed form.") is False


def test_unc_is_not_found_inside_uncertainty():
    # §3.7's second named case; A02's text unit verbatim.
    assert word_boundary_match(
        "UNC", "Measurement uncertainty dominates the result.") is False


def test_the_same_needles_do_match_when_they_stand_alone():
    # The refusal has to be a boundary rule and not a blanket "never match", or the
    # facet could never be filled at all.
    assert word_boundary_match("MIT", "Accepted to MIT this spring.") is True
    assert word_boundary_match("UNC", "UNC Chapel Hill, 2024") is True
    assert word_boundary_match("MIT", "MIT") is True


def test_case_folding_does_not_relax_the_boundary():
    # N-6 makes the §3.5 context check case-insensitive and it shares this matcher.
    # If folding case turned the rule into a substring rule, A01 and A02 would both
    # start passing, so this is the assertion that keeps N-6 safe.
    for haystack in ("Please SUBMIT the form.", "please submit the form.",
                     "Submit the form."):
        assert word_boundary_match("mit", haystack) is False
    assert word_boundary_match("syllabus", "Syllabus — ") is True
    assert word_boundary_match("SYLLABUS", "syllabus — ") is True


def test_a_needle_whose_edges_are_not_word_characters_still_bounds_correctly():
    # `\b` is defined against a word character on both sides and would be wrong here;
    # the matcher tests the boundary per edge instead.
    assert word_boundary_match("PVA/RDP", "the PVA/RDP abstract") is True
    assert word_boundary_match("AY 2024-25", "Calendar AY 2024-25 published") is True
    assert word_boundary_match("C++", "written in C++ and Rust") is True


def test_the_needle_is_never_compiled_as_a_pattern():
    # A gazetteer entry is data, not syntax. `.` must match a full stop and nothing
    # else, or one catalogue row would match every file in the corpus.
    assert word_boundary_match("M.I.T", "MXIXT") is False
    assert word_boundary_match("a+", "aaaa") is False


def test_an_empty_needle_or_haystack_matches_nothing():
    assert word_boundary_match("", "anything") is False
    assert word_boundary_match("MIT", "") is False


# --- ranking: never first-match, and never P4's read order --------------------

def test_ranking_is_over_all_candidates_and_never_the_first_match(p6_conn, tmp_path):
    # §3.7: "It should rank candidate matches instead of accepting the first match."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(footer, "Duke"), _candidate(title, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert [c.value for c in ranked] == ["Columbia", "Duke"]


def test_a_title_outranks_a_footer_and_a_late_body_page(p6_conn, tmp_path):
    # §3.7: "a value in a filename or document title carries more meaning than the
    # same value in a footer or a late body-page reference."
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    in_title = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Columbia", zone="title")
    in_footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                         content_hash=content_hash, raw="Columbia",
                         zone="header_footer")
    weighted = rank([_candidate(in_footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    stronger = rank([_candidate(in_title, "Columbia")], zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT)[0].score
    assert stronger > weighted


def test_contributions_for_one_value_are_summed_and_their_refs_merged(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    first = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="body")
    second = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia College",
                      zone="heading")
    ranked = rank([_candidate(first, "Columbia"), _candidate(second, "Columbia")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert len(ranked) == 1
    assert ranked[0].score == pytest.approx(3.0)
    assert ranked[0].evidence_refs == tuple(sorted(
        (first.observation_key, second.observation_key)))


def test_the_result_does_not_depend_on_p4s_read_order(p6_conn, tmp_path):
    # `observations_for_file` orders by rowid, which is insertion order and not a
    # property of the corpus. Every permutation must produce the same ranking or
    # §8.5's replay compares a run against itself and reports a regression.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    made = [
        _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                            content_hash=content_hash, raw=raw, zone=zone), value)
        for raw, zone, value in (("Columbia", "title", "Columbia"),
                                 ("Duke", "body", "Duke"),
                                 ("Yale", "header_footer", "Yale"),
                                 ("Duke again", "heading", "Duke"))]
    expected = rank(made, zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    for permutation in itertools.permutations(made):
        assert rank(permutation, zone_weight=ZONE_WEIGHT,
                    tier_weight=TIER_WEIGHT) == expected


def test_a_tie_is_broken_by_the_observation_key_and_not_by_insertion_order(
        p6_conn, tmp_path):
    # The case that actually bites: two candidates with identical weighted scores.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                               content_hash=content_hash, raw="Duke", zone="body"),
                      "Duke")
    right = _candidate(_observe(p6_conn, run_id="r1", file_id=file_id,
                                content_hash=content_hash, raw="Yale", zone="body"),
                       "Yale")
    forward = rank([left, right], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    backward = rank([right, left], zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert forward == backward
    assert forward[0].score == forward[1].score
    assert forward[0].evidence_refs[0] < forward[1].evidence_refs[0]


def test_a_signal_tier_weights_the_contribution_and_absence_of_one_does_not(
        p6_conn, tmp_path):
    # §2.6, and M2: P6 consumes P4's integer tier and never re-derives it. A null
    # tier is not a band -- "the system must not mistake the absence of EXIF for
    # proof that an image is a screenshot."
    file_id, content_hash = _record(p6_conn, tmp_path, name="photo.jpg", body=b"px")
    tier_one = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R6",
                        zone="metadata", signal_tier=1, source_type="image")
    untiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                        content_hash=content_hash, raw="Canon EOS R5",
                        zone="metadata", source_type="image")
    assert rank([_candidate(tier_one, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(4.0)
    assert rank([_candidate(untiered, "photograph")], zone_weight=ZONE_WEIGHT,
                tier_weight=TIER_WEIGHT)[0].score == pytest.approx(1.0)


def test_an_unweighted_zone_or_tier_raises_rather_than_defaulting(p6_conn, tmp_path):
    # No default weight exists anywhere: §3.7's numbers are Deferred and a fallback
    # would answer them silently.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    observation = _observe(p6_conn, run_id="r1", file_id=file_id,
                           content_hash=content_hash, raw="Columbia", zone="title")
    with pytest.raises(MissingWeight):
        rank([_candidate(observation, "Columbia")], zone_weight={},
             tier_weight=TIER_WEIGHT)
    with pytest.raises(MissingWeight):
        rank([Candidate(value="Columbia", score=1.0, evidence_refs=("sha256:a",))],
             zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    tiered = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Canon", zone="metadata",
                      signal_tier=2, source_type="image")
    with pytest.raises(MissingWeight):
        rank([_candidate(tiered, "photograph")], zone_weight=ZONE_WEIGHT,
             tier_weight={})


def test_every_p4_zone_is_weightable_because_the_map_is_the_callers(p6_conn):
    # The map is over P4's fifteen zones; P6 states which zones exist nowhere.
    assert set(ZONE_WEIGHT) == set(ZONES)


# --- the two thresholds, and the three different refusals ---------------------

def test_a_clear_winner_fills_the_facet_as_validated(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fact_id = fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                              field_key="school", candidates=ranked,
                              minimum_score=1.0, minimum_margin=1.0)
    assert fact_id is not None
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [(r["canonical_value"], r["reliability_state"]) for r in rows] == \
        [("Columbia", "validated")]
    assert unresolved_for_file(p6_conn, file_id, content_hash) == []


def test_two_candidates_within_the_margin_fill_nothing(p6_conn, tmp_path):
    # Done-means 9, and §3.7's "minimum margin over the second-best candidate".
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    left = _observe(p6_conn, run_id="r1", file_id=file_id,
                    content_hash=content_hash, raw="Columbia", zone="heading")
    right = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Duke", zone="heading")
    ranked = rank([_candidate(left, "Columbia"), _candidate(right, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is None
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_margin"]
    assert json.loads(rows[0]["evidence_refs"]) == sorted(
        (left.observation_key, right.observation_key))


def test_failing_the_minimum_score_is_a_different_refusal_from_the_margin(
        p6_conn, tmp_path):
    # Two thresholds, two reasons. §8.5 asks "Did it abstain when evidence was
    # absent?" and one merged reason cannot answer it.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Columbia",
                      zone="header_footer")
    ranked = rank([_candidate(footer, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=0.1) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["below_score_threshold"]


def test_no_candidate_at_all_is_a_third_refusal(p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    _observe(p6_conn, run_id="r1", file_id=file_id, content_hash=content_hash,
             raw="nothing relevant", zone="body")
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=(),
                           minimum_score=1.0, minimum_margin=1.0) is None
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key="school")
    assert [r["reason"] for r in rows] == ["no_candidate_evidence"]
    assert json.loads(rows[0]["evidence_refs"]) == []


def test_a_lone_candidate_clears_the_margin_because_there_is_no_second_best(
        p6_conn, tmp_path):
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    ranked = rank([_candidate(title, "Columbia")], zone_weight=ZONE_WEIGHT,
                  tier_weight=TIER_WEIGHT)
    assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                           field_key="school", candidates=ranked,
                           minimum_score=1.0, minimum_margin=1.0) is not None


def test_fill_or_abstain_re_imposes_the_order_on_its_own_input(p6_conn, tmp_path):
    # A caller that hands the candidates over in the wrong order must not change the
    # outcome: `rank` orders, and `fill_or_abstain` orders again before it looks at
    # the first element.
    file_id, content_hash = _record(p6_conn, tmp_path, name="essay.txt", body=b"one")
    title = _observe(p6_conn, run_id="r1", file_id=file_id,
                     content_hash=content_hash, raw="Columbia", zone="title")
    footer = _observe(p6_conn, run_id="r1", file_id=file_id,
                      content_hash=content_hash, raw="Duke", zone="header_footer")
    ranked = rank([_candidate(title, "Columbia"), _candidate(footer, "Duke")],
                  zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key="school", candidates=tuple(reversed(ranked)),
                    minimum_score=1.0, minimum_margin=1.0)
    rows = [r for r in facts_for_file(p6_conn, file_id, content_hash)
            if r["field_key"] == "school"]
    assert [r["canonical_value"] for r in rows] == ["Columbia"]


def test_a01_and_a02_fill_nothing_end_to_end(p6_conn, tmp_path):
    # The two adversarial cases as built: `expected_outcome_kind: "abstained"`,
    # `forbidden_value: {"field": "school", "value": "MIT"}` / `"UNC"`. The gazetteer
    # is the test's, because §3.7's gazetteer contents are Deferred.
    gazetteer = ("MIT", "UNC", "Columbia")
    for name, text, forbidden in (("A01", "Please submit the completed form.", "MIT"),
                                  ("A02", "Measurement uncertainty dominates the "
                                          "result.", "UNC")):
        file_id, content_hash = _record(p6_conn, tmp_path, name=f"{name}.txt",
                                        body=text.encode())
        observation = _observe(p6_conn, run_id=f"{name}-run", file_id=file_id,
                               content_hash=content_hash, raw=text, zone="body")
        candidates = [_candidate(observation, entry) for entry in gazetteer
                      if word_boundary_match(entry, observation.raw_value)]
        assert candidates == []
        assert fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                               field_key="school",
                               candidates=rank(candidates, zone_weight=ZONE_WEIGHT,
                                               tier_weight=TIER_WEIGHT),
                               minimum_score=1.0, minimum_margin=1.0) is None
        assert facts_for_file(p6_conn, file_id, content_hash) == []
        rows = unresolved_for_file(p6_conn, file_id, content_hash,
                                   field_key="school")
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]

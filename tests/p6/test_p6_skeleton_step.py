# tests/p6/test_p6_skeleton_step.py
"""The walking skeleton's P6 step, and Done-means 4 end to end.

`planning/02-segmentation-map.md`, line 190, verbatim:

    P6      resolve it to ONE validated fact (subject = X) with its evidence link  [D6]

and §3.2's own three-observation example, which is the same step run over the whole of
the design's case rather than over one observation.

**This does not go through `run_wave2`.** Task 26 is cut (D5): the step resolves facts
from evidence P4 has already stored, and `facts` is wired into no caller. The last two
tests assert that negative directly, because this file is the exact place a reader
decides P6 is ready to be wired in. It is not, and the reason is
`extractors.ocr_policy.text_layer_state` consulting `no_usable_facts` for every
text-bearing PDF before any deterministic pass has run, while Task 19's
`FactPassNotRun` is a `ContractViolation` that `orchestrator._extract_one` re-raises by
name -- so the first text-bearing PDF would end the scan.

**Two places this file departs from its plan section, both because shipped code
outranks a task body.**

* `facts.dates.DatePatterns` ships as `patterns: tuple[DatePattern, ...]`, not as the
  `Mapping[str, re.Pattern[str]]` Task 27 declared, and its three required pattern ids
  are `season_year`, `academic_year_range` and `named_term_year` -- not
  `academic_year` and `named_term`. The constructor REFUSES a catalogue missing any of
  the three, so this is a contract that cannot be papered over. Task 12 owns the
  contents; the expressions below are the TEST's.
* §3.7's rank/aggregate step is not optional. `fill_or_abstain` sorts its input and
  does not aggregate, so two separate contributions of the same value tie and the
  facet abstains with `below_margin`. The design's example states `Spring 2026` twice,
  in the filename and in a heading, and §3.7's positional weighting is what turns two
  contributions into one winner -- so `facts.facets.rank` runs between them, with the
  test's own zone weights. Task 27's step-3 listing skipped that call while defining
  the weight map it needs, which would have made Done-means 4 abstain.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
import re
from pathlib import Path

import pytest

import orchestrator

from database_agent.files_table import get_file, record_file

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import observations_for_file, record_observation, record_run

from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, SEASON_YEAR, DatePattern, DatePatterns,
    date_candidates,
)
from facts.discount import MetadataScreen
from facts.facets import fill_or_abstain, rank
from facts.file_facts import FORBIDDEN_COLUMN_SUBSTRINGS, facts_for_file
from facts.rules import Rule, apply_rules
from facts.states import VALIDATED
from facts.unresolved import CONTEXT_CHECK_FAILED, unresolved_for_file

#: Task 6's §2.2/§2.3 screen, injected EMPTY and injected VISIBLY. These tests hold no
#: tool-producer catalogue and no metadata property list, so nothing here is suppressed
#: or demoted -- but the producer takes the screen with no default (F8), so "this test
#: injects an empty catalogue" is written at every call site instead of being a silence
#: that let `python-docx` through. `tests/p6/test_p6_discount.py` is where a POPULATED
#: screen is driven end to end.
NO_CATALOGUE = MetadataScreen()

CLOCK = "2026-08-19T14:00:00+00:00"

#: §3.11's Academic row in D6's snake_case. §3.2 spells the third "work type" with a
#: space; a field key is a join handle and two spellings are two columns.
SUBJECT, TERM, WORK_TYPE = "subject", "term", "work_type"

#: The rules the TEST injects. §3.5 states that a course-code-shaped string needs an
#: academic context term; it states no pattern, and Task 10 takes both the pattern and
#: the term list as injected `Rule`s for that reason. The terms are lowercase on
#: purpose: the context check is case-insensitive (N-6) and fixture 1's context is
#: capital-S "Syllabus -- ", so a case-sensitive check would refuse the skeleton's own
#: fixture and the walking skeleton would have no P6 step at all.
SUBJECT_RULE = Rule(pattern=re.compile(r"\b[A-Z]{4,6}\s\d{4}\b"),
                    required_context_terms=("syllabus", "course", "term"),
                    field_key=SUBJECT)
WORK_TYPE_RULE = Rule(pattern=re.compile(r"\b[Ss]yllabus\b"),
                      required_context_terms=("syllabus",),
                      field_key=WORK_TYPE)

#: §3.10's three named academic-term patterns, under the pattern ids
#: `facts.dates.REQUIRED_PATTERN_IDS` addresses them by. The TEST supplies the
#: expressions; the catalogue Task 12 ships is its own and nothing here asserts
#: anything about it.
PATTERNS = DatePatterns(patterns=(
    DatePattern(pattern_id=SEASON_YEAR,
                pattern=re.compile(r"\b(?:Spring|Summer|Autumn|Fall|Winter)\s\d{4}\b")),
    DatePattern(pattern_id=ACADEMIC_YEAR_RANGE,
                pattern=re.compile(r"\bAY\s\d{4}-\d{2}\b")),
    DatePattern(pattern_id=NAMED_TERM_YEAR,
                pattern=re.compile(r"\b(?:Michaelmas|Hilary|Trinity)\sTerm\s\d{4}\b")),
))

#: §3.7's weights and thresholds are Deferred. Every number below is the TEST's.
ZONE_WEIGHT = {zone: 1.0 for zone in
               ("filename", "path", "metadata", "title", "heading", "body", "table",
                "header_footer", "notes", "link", "annotation", "reference_list",
                "manifest", "ocr", "transcript")}
ZONE_WEIGHT.update({"title": 5.0, "filename": 4.0, "heading": 3.0})
TIER_WEIGHT = {1: 1.0, 2: 1.0, 3: 1.0}
MINIMUM_SCORE, MINIMUM_MARGIN = 1.0, 0.5


def _p1_row(conn, tmp_path, *, name, body):
    """A real P1 `files` row over real bytes, so the content hash is P1's own.

    P1's hash is 64 lowercase hex characters with no `sha256:` prefix and
    `ExtractionRun.__post_init__` rejects any other shape, so a P4 fixture's own
    `content_hash` cannot be reused against a P1 database.
    """
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Courses", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _rebind(fixture, *, file_id, content_hash):
    """P4's fixture, moved onto a P1 row, with everything else carried across.

    `Observation` and `ExtractionRun` are frozen dataclasses and `dataclasses.replace`
    is the supported move. The raw value, the location, the context pair and the
    reliability come across untouched: the point is to resolve P4's fixture, not a
    convenient paraphrase of it. Rebinding changes `observation_key`, because the key
    hashes `content_hash . extractor_name . locator . raw_value` -- so every test reads
    the key off the REBOUND observation and never off the original.
    """
    run = dataclasses.replace(fixture.run, file_id=file_id,
                              content_hash=content_hash)
    observations = tuple(
        dataclasses.replace(one, file_id=file_id, content_hash=content_hash,
                            run_id=run.run_id)
        for one in fixture.observations)
    return run, observations


def _observe(conn, *, run_id, file_id, content_hash, raw, zone, label,
             extractor="pdf.text", context_before=None, context_after=None):
    """One ordinary P4-shaped observation, for §3.2's three-observation case."""
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("field", label=label),)),
        occurrence_count=1, observed_at=CLOCK, reliability="possible",
        run_id=run_id, context_before=context_before, context_after=context_after)
    record_observation(conn, observation)
    return observation


@pytest.fixture()
def skeleton(p6_conn, tmp_path):
    """Fixture 1 -- the walking-skeleton fixture -- on a real P1 row."""
    fixture = by_number(1)
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"one PDF whose title carries a course code")
    run, observations = _rebind(fixture, file_id=file_id,
                                content_hash=content_hash)
    record_run(p6_conn, run)
    for observation in observations:
        record_observation(p6_conn, observation)
    return file_id, content_hash, observations[0]


def test_fixture_one_resolves_to_one_validated_fact_with_its_evidence_link(
        skeleton, p6_conn):
    # The segmentation map's P6 step, whole: "resolve it to ONE validated fact
    # (subject = X) with its evidence link".
    file_id, content_hash, observation = skeleton
    written = apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                          rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)
    assert len(written) == 1                                       # ONE fact
    rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(rows) == 1
    row = rows[0]
    assert row["field_key"] == SUBJECT                             # subject = X (D6)
    assert row["canonical_value"] == "BUSIB 4300"
    # Task 1 owns the spelling and this test imports it; the literal below is the
    # segmentation map's own word, asserted against the constant rather than instead
    # of it.
    assert row["reliability_state"] == VALIDATED                   # validated
    assert VALIDATED == "validated"
    assert json.loads(row["evidence_refs"]) == [observation.observation_key]
    assert observation.observation_key.startswith("sha256:")       # M14, its link
    # And the link is the OBSERVATION key, never a row id: the rebound observation's
    # key is what the fact cites, and it is not the fixture's own.
    assert observation.observation_key != by_number(1).observations[0].observation_key


def test_the_step_is_named_in_the_segmentation_map_in_these_words(skeleton, p6_conn):
    # The step is read from the file, not remembered. D6 rewrote `course = X` to
    # `subject = X` there; Done-means 17's sentence still says `course`, and the
    # skeleton's own rule is that the unreconciled line is the error, not the
    # decision.
    repo_root = Path(__file__).resolve().parents[2]
    text = (repo_root / "planning" / "02-segmentation-map.md").read_text(
        encoding="utf-8")
    assert "resolve it to ONE validated fact (subject = X) with its evidence link" \
        in text
    assert "(course = X)" not in text


def test_the_context_that_makes_it_resolvable_is_byte_exact(skeleton):
    # B8(a) put this string on fixture 1 so the skeleton's one fact is resolvable at
    # all, and N-6 is why it is capital-S: §3.5's context check is case-insensitive,
    # and a case-sensitive one comparing against a lowercase term list refuses the
    # walking skeleton's own fixture.
    _, _, observation = skeleton
    assert observation.context_before == "Syllabus — "        # U+2014 EM DASH
    assert observation.context_after == " — Spring 2026"
    assert observation.raw_value == "BUSIB 4300"
    assert observation.location.zone == "heading"
    assert observation.locator == "heading:page=1/heading=2"
    assert observation.reliability == "possible"                   # a fact is not
    assert observation.occurrence_count == 3
    assert all(term.islower() for term in SUBJECT_RULE.required_context_terms)


def test_the_skeleton_step_survives_only_because_the_context_check_folds_case(
        skeleton, p6_conn):
    # N-6's CONSEQUENCE, made falsifiable rather than described. Task 10 owns
    # `context_check` and its case-insensitivity; this asserts what it buys: fixture
    # 1's context is capital-S "Syllabus — " and the rule's term is lowercase
    # "syllabus", so a case-sensitive reading refuses the walking skeleton's own
    # fixture and the P6 step disappears.
    file_id, content_hash, _ = skeleton
    lowercase_term = Rule(pattern=SUBJECT_RULE.pattern,
                          required_context_terms=("syllabus",), field_key=SUBJECT)
    assert len(apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                           rules=(lowercase_term,), screen=NO_CATALOGUE)) == 1
    # The control, so the pass above is not "any term at all resolves": one of §3.5's
    # own five terms that this context does NOT contain refuses.
    absent_term = Rule(pattern=SUBJECT_RULE.pattern,
                       required_context_terms=("lecture",), field_key=SUBJECT)
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(absent_term,), screen=NO_CATALOGUE) == ()
    assert CONTEXT_CHECK_FAILED in [
        row["reason"] for row in
        unresolved_for_file(p6_conn, file_id, content_hash, field_key=SUBJECT)]


def test_a_course_code_with_no_academic_context_produces_no_fact(p6_conn, tmp_path):
    # The negative half of the same rule, and the reason the positive half is not an
    # accident: the identical string in the identical zone, with the context removed.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unlabelled.pdf",
                                    body=b"a heading and nothing around it")
    _observe(p6_conn, run_id="bare", file_id=file_id, content_hash=content_hash,
             raw="BUSIB 4300", zone="heading", label="heading:page=1/heading=2")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(SUBJECT_RULE,), screen=NO_CATALOGUE) == ()
    assert facts_for_file(p6_conn, file_id, content_hash) == []
    rows = unresolved_for_file(p6_conn, file_id, content_hash, field_key=SUBJECT)
    assert [row["reason"] for row in rows] == [CONTEXT_CHECK_FAILED]


def test_the_three_facts_of_the_designs_own_example(p6_conn, tmp_path):
    # Done-means 4, end to end: "the filename Syllabus BUSIB 4300 Spring 2026.pdf, the
    # PDF title BUSIB 4300 Syllabus, and a page-one heading Spring 2026 are
    # observations. From those observations, the system can create facts such as
    # subject = BUSIB 4300, term = Spring 2026, and work type = syllabus."
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"the design's own example")
    name = _observe(p6_conn, run_id="fn", file_id=file_id,
                    content_hash=content_hash,
                    raw="Syllabus BUSIB 4300 Spring 2026.pdf", zone="filename",
                    label="filename", extractor="filesystem.name")
    title = _observe(p6_conn, run_id="ti", file_id=file_id,
                     content_hash=content_hash, raw="BUSIB 4300 Syllabus",
                     zone="title", label="title",
                     context_before="Title: ", context_after=" (syllabus)")
    heading = _observe(p6_conn, run_id="hd", file_id=file_id,
                       content_hash=content_hash, raw="Spring 2026", zone="heading",
                       label="heading:page=1/heading=1",
                       context_before="Syllabus — ", context_after="")

    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE, WORK_TYPE_RULE), screen=NO_CATALOGUE)
    contributions = tuple(candidate
                          for observation in (name, title, heading)
                          for candidate in date_candidates(observation,
                                                           patterns=PATTERNS))
    # §3.7's positional weighting is what makes ONE winner out of the two places the
    # design's example states the term. Without `rank`, `fill_or_abstain` sees two
    # tied contributions and abstains with `below_margin`.
    assert len(contributions) == 2
    ranked = rank(contributions, zone_weight=ZONE_WEIGHT, tier_weight=TIER_WEIGHT)
    assert len(ranked) == 1
    fill_or_abstain(p6_conn, file_id=file_id, content_hash=content_hash,
                    field_key=TERM, candidates=ranked,
                    minimum_score=MINIMUM_SCORE, minimum_margin=MINIMUM_MARGIN)

    all_rows = facts_for_file(p6_conn, file_id, content_hash)
    assert len(all_rows) == 3                                      # exactly three
    rows = {row["field_key"]: row for row in all_rows}
    assert set(rows) == {SUBJECT, TERM, WORK_TYPE}
    assert rows[SUBJECT]["canonical_value"] == "BUSIB 4300"
    assert rows[TERM]["canonical_value"] == "Spring 2026"
    # §2.8: "the raw observation remains exactly that wording". The design's prose
    # spells the third value lowercase; the document spells it "Syllabus", and the
    # per-field normalizer that would fold the two is Deferred (§2.8, §3.6). So the
    # stored value is the document's wording, and this test says so rather than
    # lower-casing it to make the prose come true.
    assert rows[WORK_TYPE]["canonical_value"] == "Syllabus"
    for row in rows.values():
        refs = json.loads(row["evidence_refs"])
        assert refs and all(ref.startswith("sha256:") for ref in refs)
    # The two facts the rules produced cite the TITLE observation, which is the one
    # that carried academic context; the term cites the two positions it was stated
    # in. Nothing cites an observation that did not support it.
    assert json.loads(rows[SUBJECT]["evidence_refs"]) == [title.observation_key]
    assert json.loads(rows[WORK_TYPE]["evidence_refs"]) == [title.observation_key]
    assert sorted(json.loads(rows[TERM]["evidence_refs"])) == sorted(
        [name.observation_key, heading.observation_key])


def test_the_filenames_course_code_abstains_rather_than_becoming_a_fact(
        p6_conn, tmp_path):
    # The other half of the example, and the half a reader assumes did not happen:
    # the filename states `BUSIB 4300` too, with no context pair at all, so it
    # produces a REFUSAL and not a second subject fact. §3.2's "three observations,
    # three facts" is not "every observation, one fact each".
    file_id, content_hash = _p1_row(
        p6_conn, tmp_path, name="Syllabus BUSIB 4300 Spring 2026.pdf",
        body=b"the design's own example, filename only")
    _observe(p6_conn, run_id="fn", file_id=file_id, content_hash=content_hash,
             raw="Syllabus BUSIB 4300 Spring 2026.pdf", zone="filename",
             label="filename", extractor="filesystem.name")
    assert apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                       rules=(SUBJECT_RULE, WORK_TYPE_RULE), screen=NO_CATALOGUE) == ()
    reasons = {row["field_key"]: row["reason"]
               for row in unresolved_for_file(p6_conn, file_id, content_hash)}
    assert reasons == {SUBJECT: CONTEXT_CHECK_FAILED,
                       WORK_TYPE: CONTEXT_CHECK_FAILED}


def test_every_observation_is_unchanged_after_resolution(p6_conn, tmp_path):
    # §3.2: "the product must preserve both the original evidence and the conclusion
    # built from it." P4 makes this unfalsifiable at the database -- the `evidence`
    # table carries `evidence_never_overwritten` and `evidence_no_delete` triggers --
    # so this asserts the INTENT and the triggers guarantee it cannot pass by
    # accident.
    file_id, content_hash = _p1_row(p6_conn, tmp_path, name="unchanged.pdf",
                                    body=b"evidence outlives the conclusion")
    original = _observe(p6_conn, run_id="u", file_id=file_id,
                        content_hash=content_hash, raw="BUSIB 4300", zone="heading",
                        label="heading:page=1/heading=2",
                        context_before="Syllabus — ", context_after="")
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)
    after = [one for one in observations_for_file(p6_conn, file_id)
             if one.observation_key == original.observation_key]
    assert len(after) == 1
    assert after[0].raw_value == "BUSIB 4300"
    assert after[0].context_before == "Syllabus — "
    assert after[0].reliability == "possible"
    assert after[0].extractor_version == "1.0.0"
    assert after[0].occurrence_count == 1


def test_the_resolved_fact_carries_no_path_destination_folder_or_group(
        skeleton, p6_conn):
    # §3.14: "A fact such as subject = BUSIB 4300 does not itself dictate one
    # permanent folder path." Task 4 asserts this of the SCHEMA; this asserts it of a
    # row the walking skeleton actually produced, which is where a reviewer looks.
    file_id, content_hash, _ = skeleton
    apply_rules(p6_conn, file_id=file_id, content_hash=content_hash,
                rules=(SUBJECT_RULE,), screen=NO_CATALOGUE)
    row = facts_for_file(p6_conn, file_id, content_hash)[0]
    assert FORBIDDEN_COLUMN_SUBSTRINGS                             # not vacuous
    for column in row.keys():
        assert not [bad for bad in FORBIDDEN_COLUMN_SUBSTRINGS
                    if bad in column.lower()], column


def test_p6_is_not_wired_into_the_wave_2_caller():
    # D5 cut Task 26, and this is the point in the plan where a reader decides P6 is
    # ready to be wired in. It is not. `ocr_policy.text_layer_state` consults
    # `no_usable_facts` for every text-bearing PDF before any deterministic pass has
    # run, and Task 19's `FactPassNotRun` is a `ContractViolation` that
    # `orchestrator._extract_one` re-raises by name -- so passing P6's resolver ends
    # the scan on the first text-bearing PDF.
    tree = ast.parse(inspect.getsource(orchestrator))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert imported                                                # not vacuous
    assert not [name for name in imported if name.split(".")[0] == "facts"]
    # The stub is KEPT, not deleted -- round 5's simplification, in the Task 26 cut
    # note. And nothing can acquire P6 by omission: the parameter has no default.
    assert callable(orchestrator.TARGETED_OCR_UNAVAILABLE)
    parameter = inspect.signature(orchestrator.run_wave2).parameters[
        "no_usable_facts"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty


def test_this_step_never_runs_through_run_wave2():
    # The other half of the same negative, from this test module's own imports: the
    # skeleton's P6 step resolves from STORED evidence. `orchestrator` is imported
    # here read-only, for the guard above, and `run_wave2` is not imported at all.
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            imported_names.update(f"{node.module}.{alias.name}"
                                  for alias in node.names)
    assert imported_names                                          # not vacuous
    assert "orchestrator.run_wave2" not in imported_names
    assert not [name for name in imported_names
                if name.startswith("extractors.")]

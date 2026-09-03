# tests/p6/test_p6_evidence.py
"""M14, Done-means 6 and 30 — keys, the context pair, truncation, and no per-format branching."""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import pkgutil

import pytest

from evidence_shape.fixtures import by_number
from evidence_shape.location import Location
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import SOURCE_TYPES

import facts
from facts.evidence import (
    UnknownRun, analysis_tier_for_observation, cite, context_pair,
    observations_for_version, resolve_citation,
)

CLOCK = "2026-08-19T12:00:00+00:00"

#: A second content hash for the same `file_id`: the file was edited, so §3.4 puts its
#: facts in a different cache slot and §8.2 makes the old version's rows survive.
SECOND_HASH = "b" * 64

#: Every `extractor_name` P4's nineteen fixtures use. P6 must not contain one of these
#: strings in code: branching on the extractor is branching on the format (§2.8), and
#: F14 records that P4's fixture names and P5's live names already differ.
FIXTURE_EXTRACTORS = frozenset(
    by_number(n).run.extractor_name for n in range(1, 20))


def _run(conn, *, run_id, file_id, content_hash, extractor="pdf.text",
         version="1.0.0", source_type="text_document", tier="native"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name=extractor, extractor_version=version,
        source_type=source_type, analysis_tier=tier, config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, file_id, content_hash, raw, zone="heading",
             container_path=(), extractor="pdf.text", version="1.0.0",
             source_type="text_document", before=None, after=None,
             truncated=False):
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location(zone, tuple(container_path)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id=run_id,
        context_before=before, context_after=after, context_truncated=truncated)
    record_observation(conn, observation)
    return observation


def _code_strings(module) -> set[str]:
    """Every string literal in a module that is NOT a docstring.

    A source-text search matches comments and docstrings, and a guard that does that
    has broken three tasks on this project already (P5 PLAN, Task 20). This reads the
    code.
    """
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


def _facts_modules():
    """Every module in the `facts` package, imported. Grows as siblings land."""
    for info in pkgutil.iter_modules(facts.__path__):
        yield importlib.import_module(f"facts.{info.name}")


# --- the per-version read (F12) ------------------------------------------------

def test_observations_for_version_does_not_return_a_prior_versions_observations(p6_conn):
    # §3.4 and §8.2 make every P6 computation per file *version*. P4 publishes only
    # `observations_for_file`, which spans content hashes; the filter lives here once.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-old", file_id="file-01",
         content_hash=fixture.run.content_hash)
    _run(p6_conn, run_id="r-new", file_id="file-01", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r-old", file_id="file-01",
             content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    _observe(p6_conn, run_id="r-new", file_id="file-01",
             content_hash=SECOND_HASH, raw="PHYS 1401")

    new = observations_for_version(p6_conn, "file-01", SECOND_HASH)
    assert [one.raw_value for one in new] == ["PHYS 1401"]

    old = observations_for_version(p6_conn, "file-01", fixture.run.content_hash)
    assert [one.raw_value for one in old] == ["BUSIB 4300"]


def test_observations_for_version_returns_a_tuple_not_a_list(p6_conn):
    # A tuple is the shape `PLAN-tasks-14-15.md` stores on its `_Version` record, and
    # an immutable read is one fewer way a producer can reorder its own input.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    _observe(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH, raw="x")
    assert isinstance(observations_for_version(p6_conn, "f1", SECOND_HASH), tuple)


def test_the_read_order_is_p6s_own_and_not_p4s_insertion_order(p6_conn):
    # Verified by execution 2026-08-21: `observations_for_file` is ORDER BY rowid,
    # which is a property of this database and not of the corpus. Two files given the
    # same three values in opposite write orders must read back identically, or §8.5's
    # replay compares a run against itself and reports a regression.
    values = ["Columbia", "BUSIB 4300", "Wash U"]
    _run(p6_conn, run_id="r-fwd", file_id="f-fwd", content_hash=SECOND_HASH)
    _run(p6_conn, run_id="r-rev", file_id="f-rev", content_hash=SECOND_HASH)
    for raw in values:
        _observe(p6_conn, run_id="r-fwd", file_id="f-fwd",
                 content_hash=SECOND_HASH, raw=raw)
    for raw in reversed(values):
        _observe(p6_conn, run_id="r-rev", file_id="f-rev",
                 content_hash=SECOND_HASH, raw=raw)

    forward = observations_for_version(p6_conn, "f-fwd", SECOND_HASH)
    reverse = observations_for_version(p6_conn, "f-rev", SECOND_HASH)
    assert [one.raw_value for one in forward] == [one.raw_value for one in reverse]
    assert [cite(one) for one in forward] == sorted(cite(one) for one in forward)


# --- the citation (M14, Done-means 30) ----------------------------------------

def test_cite_returns_the_observation_key_and_never_the_observation_id(p6_conn):
    # M14. `observation_id` is per-row and P4-assigned; a fact citing one is a fact an
    # extractor upgrade silently orphans.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="Columbia")
    assert cite(observation) == observation.observation_key
    assert cite(observation).startswith("sha256:")
    assert not hasattr(observation, "observation_id")


def test_a_citation_stored_before_a_version_bump_still_resolves_after_it(p6_conn):
    # Done-means 30 and §8.7. `observation_key` hashes content_hash · extractor_name ·
    # locator · raw_value and NOT extractor_version, so the same reading re-extracted
    # at 2.0.0 carries the identical key and the stored reference resolves to both.
    fixture = by_number(1)
    _run(p6_conn, run_id="r-1", file_id="file-01",
         content_hash=fixture.run.content_hash)
    before = _observe(p6_conn, run_id="r-1", file_id="file-01",
                      content_hash=fixture.run.content_hash, raw="BUSIB 4300")
    stored = cite(before)

    _run(p6_conn, run_id="r-2", file_id="file-01",
         content_hash=fixture.run.content_hash, version="2.0.0")
    after = _observe(p6_conn, run_id="r-2", file_id="file-01",
                     content_hash=fixture.run.content_hash, raw="BUSIB 4300",
                     version="2.0.0")
    assert cite(after) == stored

    resolved = resolve_citation(p6_conn, stored)
    assert {one.extractor_version for one in resolved} == {"1.0.0", "2.0.0"}
    assert {one.raw_value for one in resolved} == {"BUSIB 4300"}


def test_resolve_citation_returns_empty_for_a_key_no_observation_carries(p6_conn):
    # §3.6 check 2 asks whether a cited quote is present in the evidence. An empty
    # answer is the answer; an exception would make an absent citation a crash.
    assert resolve_citation(p6_conn, "sha256:" + "0" * 64) == ()


def test_resolve_citation_is_ordered_and_not_p4s_rowid_order(p6_conn):
    # The newer extractor version is written FIRST, so P4's rowid order and P6's order
    # disagree and the assertion has something to catch.
    fixture = by_number(1)
    stored = ""
    for run_id, version in (("r-b", "2.0.0"), ("r-a", "1.0.0")):
        _run(p6_conn, run_id=run_id, file_id="file-01",
             content_hash=fixture.run.content_hash, version=version)
        stored = cite(_observe(
            p6_conn, run_id=run_id, file_id="file-01",
            content_hash=fixture.run.content_hash, raw="BUSIB 4300",
            version=version))

    resolved = resolve_citation(p6_conn, stored)
    assert [one.extractor_version for one in resolved] == ["1.0.0", "2.0.0"]


# --- the context pair (M5, §8.6) ----------------------------------------------

def test_context_pair_returns_two_values_and_never_a_concatenation(p6_conn):
    # M5: P4 split §2.8's "surrounding context" into two fields so §8.4 can redact a
    # value without dropping its context. Fixture 1's bytes, verbatim.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="Syllabus — ", after=" — Spring 2026")
    before, after, truncated = context_pair(observation)
    assert before == "Syllabus — "
    assert after == " — Spring 2026"
    assert truncated is False
    assert before + after not in (before, after)


def test_context_pair_hands_back_the_truncation_flag_with_the_context(p6_conn):
    # §8.6: "A model prompt that exceeds its token budget should not truncate silently
    # in a way that removes the decisive evidence." Three values in one call is how a
    # caller is stopped from reading the context without seeing the flag.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300",
                           before="…llabus ", after=" — Spri", truncated=True)
    assert context_pair(observation) == ("…llabus ", " — Spri", True)
    assert len(context_pair(observation)) == 3


def test_context_pair_renders_an_absent_context_as_the_empty_string(p6_conn):
    # Fixture 2 (the PDF title) carries context_before=None. A caller doing a
    # substring or word-boundary check on None raises; on "" it simply finds nothing.
    _run(p6_conn, run_id="r1", file_id="f1", content_hash=SECOND_HASH)
    observation = _observe(p6_conn, run_id="r1", file_id="f1",
                           content_hash=SECOND_HASH, raw="BUSIB 4300 Syllabus",
                           zone="title")
    assert observation.context_before is None
    assert context_pair(observation) == ("", "", False)


# --- the analysis tier comes from P4 and is never inferred ---------------------

def test_the_analysis_tier_is_read_from_p4s_run(p6_conn):
    # Global constraint: P6 never re-derives what P4 assigns. Inferring the tier from
    # `extractor_name` would encode the routing table in a second place.
    _run(p6_conn, run_id="r-ocr", file_id="f1", content_hash=SECOND_HASH,
         extractor="ocr.apple_vision", source_type="ocr", tier="ocr")
    observation = _observe(p6_conn, run_id="r-ocr", file_id="f1",
                           content_hash=SECOND_HASH, raw="Your Columbia University",
                           zone="ocr", extractor="ocr.apple_vision",
                           source_type="ocr")
    assert analysis_tier_for_observation(p6_conn, observation) == "ocr"


def test_an_observation_whose_run_was_never_recorded_raises(p6_conn):
    # Guessing a tier here would put the wrong value in §3.4's cache key, and a wrong
    # cache key is a fact that never invalidates. Refusing is the only safe answer.
    observation = Observation(
        file_id="f1", content_hash=SECOND_HASH, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value="x",
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id="run-that-does-not-exist")
    with pytest.raises(UnknownRun):
        analysis_tier_for_observation(p6_conn, observation)


def test_a_run_recorded_under_a_DIFFERENT_content_version_is_not_this_ones(p6_conn):
    """The subtle half, and the one a faster lookup could silently drop.

    The tier is read by asking for the runs of THIS observation's `content_hash`
    and finding its `run_id` among them. A lookup that went straight to the
    `run_id` -- which is the primary key, so it is the obvious way to make this
    fast -- would happily return the tier of a run belonging to a different
    version of the file. §3.4 keys its cache on the content hash, and a tier
    borrowed across versions is a fact that never invalidates.

    Fixture 1's run is recorded under its own hash; this asks for it under
    `SECOND_HASH`, which is the same file after an edit.
    """
    fixture = by_number(1)
    record_run(p6_conn, fixture.run)
    borrowed = fixture.observations[0]
    assert borrowed.run_id == fixture.run.run_id
    assert borrowed.content_hash != SECOND_HASH

    observation = Observation(
        file_id=borrowed.file_id, content_hash=SECOND_HASH,
        extractor_name=borrowed.extractor_name,
        extractor_version=borrowed.extractor_version,
        source_type=borrowed.source_type, raw_value=borrowed.raw_value,
        location=borrowed.location, occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id=borrowed.run_id)

    with pytest.raises(UnknownRun):
        analysis_tier_for_observation(p6_conn, observation)


# --- Done-means 6: no per-format branching ------------------------------------

def test_p6_reads_an_observation_whose_source_type_it_has_never_seen(p6_conn):
    # Done-means 6. Fixture 18 is `design_creative`, indexed-but-unreadable (M3) --
    # a source type nothing in `facts` was written against. It reads, it cites, and
    # its tier resolves, with no code added for it.
    fixture = by_number(18)
    record_run(p6_conn, fixture.run)
    for observation in fixture.observations:
        record_observation(p6_conn, observation)

    read = observations_for_version(p6_conn, fixture.run.file_id,
                                    fixture.run.content_hash)
    assert [one.raw_value for one in read] == ["Background"]
    assert cite(read[0]).startswith("sha256:")
    assert analysis_tier_for_observation(p6_conn, read[0]) == "native"
    assert context_pair(read[0]) == ("", "", False)


def test_a_source_type_outside_p4s_vocabulary_cannot_be_constructed_at_all():
    # Why Done-means 6 is read as "unknown to P6" and not "unknown to P4": P4 refuses
    # the latter at the record, so the only reachable case is a member of the fourteen
    # that P6 has no code for. Verified by execution, not by reading the docstring.
    from evidence_shape.vocabulary import NotInVocabulary
    with pytest.raises(NotInVocabulary):
        dataclasses.replace(by_number(1).observations[0],
                            source_type="holographic_scroll")


def test_no_facts_module_holds_a_dispatch_table_keyed_by_source_type():
    # §2.8 exists so downstream logic does not branch per format. "At least two keys,
    # all of them source types" is the shape of a real dispatch table; the bound is
    # two because `ocr` is a member of BOTH SOURCE_TYPES and ZONES, so a zone-keyed
    # map with a single `ocr` entry would otherwise read as a format branch.
    offenders = []
    for module in _facts_modules():
        for name, value in vars(module).items():
            if name.startswith("__") or not isinstance(value, dict):
                continue
            keys = {k for k in value if isinstance(k, str)}
            if len(keys) >= 2 and keys <= set(SOURCE_TYPES):
                offenders.append(f"{module.__name__}.{name}")
    assert offenders == []


def test_no_facts_module_names_a_source_type_or_an_extractor_in_code():
    # The stronger half: a single `if observation.source_type == "image"` is a format
    # branch too. Extractor names are checked against P4's nineteen fixtures because
    # F14 records that P4's fixture names and P5's live names already differ -- only
    # the no-branching rule keeps that harmless.
    forbidden = set(SOURCE_TYPES) | FIXTURE_EXTRACTORS
    offenders = []
    for module in _facts_modules():
        for literal in _code_strings(module) & forbidden:
            offenders.append(f"{module.__name__}: {literal!r}")
    assert offenders == []

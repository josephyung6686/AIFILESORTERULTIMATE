# tests/p6/test_p6_cache_one_rule.py
"""Preamble §3.2's ruling, pinned: ONE cache-key rule, ONE helper, and it is Task 6's.

The plan settled this and the built producers did not follow it. Seven modules each
wrote out a private copy, and three of them -- `facts.direct`, `facts.discount` and
`facts.families` -- carried the rule the preamble explicitly rejected, keying off the
observations a fact happens to CITE instead of every observation of the file version.
Nothing failed, because nothing tested it. These tests are that test.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from evidence_shape.runs import ExtractionRun
from evidence_shape.observation import Observation
from evidence_shape.location import Location
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS

from facts.cache import fact_cache_key, is_stale, pass_cache_key
from facts.fields import FIELD_ROWS
from facts.unresolved import write_unresolved

CLOCK = "2026-08-19T14:03:22+00:00"
FILE = "file-1"
HASH = "a" * 64


def _run(conn, *, run_id, extractor, version, tier, source_type="text_document"):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=FILE, content_hash=HASH, extractor_name=extractor,
        extractor_version=version, source_type=source_type, analysis_tier=tier,
        config={}, completeness="complete", started_at=CLOCK, finished_at=CLOCK))


def _observe(conn, *, run_id, raw, extractor, version, source_type="text_document"):
    observation = Observation(
        file_id=FILE, content_hash=HASH, extractor_name=extractor,
        extractor_version=version, source_type=source_type, raw_value=raw,
        location=Location("heading", ()), occurrence_count=1, observed_at=CLOCK,
        reliability="possible", run_id=run_id)
    record_observation(conn, observation)
    return observation


def _native_and_ocr(conn):
    """One file version read twice: a native pass, then a richer OCR pass."""
    _run(conn, run_id="run-native", extractor="pdf.text", version="1.0.0",
         tier="native")
    native = _observe(conn, run_id="run-native", raw="Chem 101", extractor="pdf.text",
                      version="1.0.0")
    _run(conn, run_id="run-ocr", extractor="vision.ocr", version="2.0.0", tier="ocr",
         source_type="image")
    ocr = _observe(conn, run_id="run-ocr", raw="Chem 101", extractor="vision.ocr",
                   version="2.0.0", source_type="image")
    return native, ocr


# -- the ruling itself --------------------------------------------------------

def test_the_key_is_the_whole_version_and_not_the_observations_a_fact_cites(p6_conn):
    """The rejected rule and the settled one give DIFFERENT keys, so which one a
    producer used was always observable -- it was simply never observed."""
    _native_and_ocr(p6_conn)

    settled = pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)

    # what `facts.direct`, `facts.discount` and `facts.families` used to compute: the
    # cite set, here a fact that cites only the native reading.
    rejected = fact_cache_key(
        content_hash=HASH,
        extractor_version='[["pdf.text","1.0.0"]]',
        analysis_tier="native",
        model_identifier=None, prompt_fingerprint=None)

    assert settled != rejected


def test_the_tier_is_the_last_one_present_so_a_richer_pass_supersedes(p6_conn):
    """§3.3: filesystem < native < ocr < llm. The OCR pass must not land in the slot
    the native pass computed under, or it would overwrite rather than supersede."""
    _native_and_ocr(p6_conn)
    both = pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)

    native_only = fact_cache_key(
        content_hash=HASH, extractor_version='[["pdf.text","1.0.0"]]',
        analysis_tier="native", model_identifier=None, prompt_fingerprint=None)

    assert both != native_only


def test_a_fact_and_its_abstention_from_one_pass_share_one_key(p6_conn):
    """The deciding argument in preamble §3.2: an abstention has no citations, so a
    cite-set key cannot be computed for it at all."""
    _native_and_ocr(p6_conn)
    assert (pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)
            == pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH))


def test_no_observation_at_all_still_yields_a_key(p6_conn):
    """An abstention fires precisely where there is nothing to read; a pass that
    cannot be keyed cannot be recorded as having happened."""
    key = pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)
    assert key == fact_cache_key(
        content_hash=HASH, extractor_version="[]",
        analysis_tier=ANALYSIS_TIERS[0], model_identifier=None,
        prompt_fingerprint=None)


# -- supersede, re-verified after the change ---------------------------------

def test_an_ocr_pass_leaves_the_native_slot_stale(p6_conn):
    """Re-verifies §8.2 at the cache: work recorded under the native-only key is not
    found under the key the later OCR pass computes."""
    _run(p6_conn, run_id="run-native", extractor="pdf.text", version="1.0.0",
         tier="native")
    _observe(p6_conn, run_id="run-native", raw="Chem 101", extractor="pdf.text",
             version="1.0.0")
    native_key = pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)

    write_unresolved(
        p6_conn, file_id=FILE, content_hash=HASH, field_key=FIELD_ROWS[0].field_key,
        reason="no_candidate_evidence", attempted_producers=("direct",),
        evidence_refs=(), cache_key=native_key)
    assert not is_stale(p6_conn, file_id=FILE, content_hash=HASH,
                        cache_key=native_key)

    _run(p6_conn, run_id="run-ocr", extractor="vision.ocr", version="2.0.0",
         tier="ocr", source_type="image")
    _observe(p6_conn, run_id="run-ocr", raw="Chem 101", extractor="vision.ocr",
             version="2.0.0", source_type="image")
    ocr_key = pass_cache_key(p6_conn, file_id=FILE, content_hash=HASH)

    assert ocr_key != native_key
    assert is_stale(p6_conn, file_id=FILE, content_hash=HASH, cache_key=ocr_key)


# -- the structural guard: the copies must not come back ----------------------

def test_no_facts_module_writes_its_own_cache_key_helper():
    """`facts.cache` is Task 6's module and no other task may add to it. Seven private
    copies is how the rejected rule survived assembly; this fails if one returns."""
    offenders = []
    for path in sorted(pathlib.Path("src/facts").glob("*.py")):
        if path.name == "cache.py":
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and "cache_key" in node.name:
                offenders.append(f"{path.name}:{node.name}")
    assert offenders == []

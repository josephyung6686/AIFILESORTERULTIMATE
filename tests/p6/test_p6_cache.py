# tests/p6/test_p6_cache.py
"""§3.4 — Done-means 15 and 16. The five-part key, and what invalidates a fact.

"The cache key includes content hash, extractor version, analysis tier, model
identifier when relevant, and prompt fingerprint for model-derived results. This
prevents stale results from surviving a content rewrite, avoids unnecessary work when
a file is merely renamed, and makes model or prompt changes auditable."
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation, observation_key
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import get_run, record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS, NotInVocabulary

from extractors.runs import cache_key as extraction_cache_key

from facts import cache as cache_module
from facts.cache import CACHE_KEY_PARTS, fact_cache_key, is_stale
from facts.file_facts import RULE, write_fact
from facts.states import POSSIBLE, VALIDATED
from facts.unresolved import (
    DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, RULE_ROUTE, write_unresolved,
)
from facts.values import ensure_value

CLOCK = "2026-08-22T12:00:00+00:00"

#: The design's five parts, in the design's own order, spelled independently of the
#: module under test so the assertion is a comparison and not an echo.
DESIGN_FIVE = ("content_hash", "extractor_version", "analysis_tier",
               "model_identifier", "prompt_fingerprint")

#: One deterministic baseline. `model_identifier` and `prompt_fingerprint` are None
#: because P6 contains no model call of any kind (§3.3) and P8 does not exist.
BASELINE = dict(content_hash="a" * 64, extractor_version="1.0.0",
                analysis_tier="native", model_identifier=None,
                prompt_fingerprint=None)


def _record(conn, tmp_path: Path, *, name: str, body: bytes) -> tuple[str, str]:
    """A real P1 file row, so this test never assumes whether `file_facts` carries a
    foreign key to `files`. Returns `(file_id, content_hash)`."""
    path = tmp_path / "corpus" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=path.suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _write_subject_fact(conn, *, file_id: str, content_hash: str, key: str) -> str:
    ref = observation_key(content_hash=content_hash, extractor_name="pdf.text",
                          locator="heading:page=1/heading=2", raw_value="BUSIB 4300")
    value_id = ensure_value(conn, field_key="subject", canonical_value="BUSIB 4300",
                            first_evidence_ref=ref, origin="automatic")
    # Task 4 owns the literal spelling of `rule` and publishes the named constant.
    return write_fact(conn, file_id=file_id, content_hash=content_hash,
                      field_key="subject", value_id=value_id,
                      reliability_state=VALIDATED, origin=RULE,
                      evidence_refs=(ref,), cache_key=key, active=True)


def test_the_key_is_exactly_section_3_4s_five_parts(p6_conn):
    assert CACHE_KEY_PARTS == DESIGN_FIVE
    parameters = inspect.signature(fact_cache_key).parameters
    assert tuple(parameters) == CACHE_KEY_PARTS
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters.values())
    assert all(p.default is inspect.Parameter.empty for p in parameters.values()), (
        "every part is supplied by the caller; a defaulted part is a part that "
        "silently stops distinguishing cache slots")


def test_changing_any_one_part_changes_the_key(p6_conn):
    baseline = fact_cache_key(**BASELINE)
    mutations = (
        dict(BASELINE, content_hash="b" * 64),
        dict(BASELINE, extractor_version="2.0.0"),
        dict(BASELINE, analysis_tier="ocr"),
        dict(BASELINE, model_identifier="claude-x/2026-08"),
        dict(BASELINE, prompt_fingerprint="sha256:prompt-1"),
    )
    keys = {baseline} | {fact_cache_key(**one) for one in mutations}
    assert len(keys) == 6, "each of the five parts must move the key on its own"
    assert baseline.startswith("sha256:")
    assert fact_cache_key(**BASELINE) == baseline, "the key is a pure function"


def test_a_rename_cannot_reach_the_key(p6_conn, tmp_path):
    """Done-means 16, first half, at the strongest place to assert it: the key has no
    path input at all -- not ignored, not nullable, absent."""
    parameters = inspect.signature(fact_cache_key).parameters
    for forbidden in ("path", "current_path", "filename", "file_id", "directory_position"):
        assert forbidden not in parameters

    before = _record(p6_conn, tmp_path, name="Syllabus.pdf", body=b"BUSIB 4300")
    after = _record(p6_conn, tmp_path, name="renamed.pdf", body=b"BUSIB 4300")
    assert before[1] == after[1], "same bytes, same content hash (P1 R1)"
    assert (fact_cache_key(**dict(BASELINE, content_hash=before[1]))
            == fact_cache_key(**dict(BASELINE, content_hash=after[1])))


def test_a_rename_triggers_no_re_resolution_and_a_content_change_does(p6_conn, tmp_path):
    """Done-means 16, end to end, through the fact table."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=key)

    # The rename: P1's identity is the content hash, so the row is the same row and
    # the key is the same key.
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False

    # The content rewrite: a new content hash is a new slot, and nothing has been
    # computed in it.
    _, rewritten = _record(p6_conn, tmp_path, name="Syllabus-v2.pdf",
                           body=b"BUSIB 4300 revised")
    assert rewritten != content_hash
    rewritten_key = fact_cache_key(**dict(BASELINE, content_hash=rewritten))
    assert is_stale(p6_conn, file_id=file_id, content_hash=rewritten,
                    cache_key=rewritten_key) is True


def test_a_bumped_extractor_version_re_resolves(p6_conn, tmp_path):
    """Done-means 15's trigger. The supersession itself is Task 23's."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Syllabus.pdf",
                                    body=b"BUSIB 4300")
    old = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=old)

    bumped = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                   extractor_version="2.0.0"))
    assert bumped != old
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=bumped) is True
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=old) is False


def test_a_changed_prompt_fingerprint_re_resolves(p6_conn, tmp_path):
    """§3.4's "makes model or prompt changes auditable" -- both keys stay computable,
    and the fact written under the old one stays readable."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Essay.pdf",
                                    body=b"Columbia")
    first = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                           analysis_tier="llm", model_identifier="model-a",
                           prompt_fingerprint="sha256:prompt-1")
    _write_subject_fact(p6_conn, file_id=file_id, content_hash=content_hash, key=first)
    second = fact_cache_key(content_hash=content_hash, extractor_version="1.0.0",
                            analysis_tier="llm", model_identifier="model-a",
                            prompt_fingerprint="sha256:prompt-2")
    assert first != second
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=second) is True


def test_none_is_distinguishable_from_the_empty_string(p6_conn):
    """P4's `sha256_of` is length-prefixed and injective, and each part is
    canonical_json-encoded before it is hashed, so `null` and `""` are different
    strings of different lengths. A property to assert, not a hazard to avoid."""
    absent = fact_cache_key(**dict(BASELINE, model_identifier=None))
    empty = fact_cache_key(**dict(BASELINE, model_identifier=""))
    assert absent != empty
    assert (fact_cache_key(**dict(BASELINE, prompt_fingerprint=None))
            != fact_cache_key(**dict(BASELINE, prompt_fingerprint="")))
    # And no two parts can be smeared into each other by concatenation.
    assert (fact_cache_key(content_hash="ab", extractor_version="c",
                           analysis_tier="native", model_identifier=None,
                           prompt_fingerprint=None)
            != fact_cache_key(content_hash="a", extractor_version="bc",
                              analysis_tier="native", model_identifier=None,
                              prompt_fingerprint=None))


def test_the_deterministic_fact_carries_neither_model_part(p6_conn):
    """Done-means 17's half of this task: P8 is absent, so both are None and the key
    is still computable. P6 contains no model call of any kind (§3.3)."""
    assert fact_cache_key(**BASELINE).startswith("sha256:")
    assert BASELINE["model_identifier"] is None
    assert BASELINE["prompt_fingerprint"] is None


def test_the_analysis_tier_is_p4s_and_a_fourth_value_is_refused(p6_conn):
    """P6 never infers a tier -- it comes from P4's `ExtractionRun` (Global
    Constraints), and an unknown one raises rather than being hashed."""
    assert ANALYSIS_TIERS == ("filesystem", "native", "ocr", "llm")
    for tier in ANALYSIS_TIERS:
        assert fact_cache_key(**dict(BASELINE, analysis_tier=tier))
    with pytest.raises(NotInVocabulary):
        fact_cache_key(**dict(BASELINE, analysis_tier="ocr_v2"))
    for empty in ("content_hash", "extractor_version"):
        with pytest.raises(ValueError):
            fact_cache_key(**dict(BASELINE, **{empty: ""}))


def test_a_run_supplies_the_two_parts_p6_must_not_invent(p6_conn, tmp_path):
    """Preamble rule 5, at the key: a native run and an OCR run over the same content
    hash land in different cache slots, which is why pass 4 supersedes rather than
    overwrites (§8.2). Both parts are read off P4's run, never inferred."""
    _, content_hash = _record(p6_conn, tmp_path, name="Scan.pdf", body=b"scanned")
    runs = [
        ExtractionRun(run_id=f"run-{tier}", file_id="file-scan",
                      content_hash=content_hash, extractor_name="pdf.text",
                      extractor_version="1.0.0", source_type="text_document",
                      analysis_tier=tier, config={}, completeness="complete",
                      started_at=CLOCK, finished_at=CLOCK)
        for tier in ("native", "ocr")
    ]
    keys = {fact_cache_key(content_hash=run.content_hash,
                           extractor_version=run.extractor_version,
                           analysis_tier=run.analysis_tier,
                           model_identifier=None, prompt_fingerprint=None)
            for run in runs}
    assert len(keys) == 2


def test_an_abstention_counts_as_work_done_under_that_key(p6_conn, tmp_path):
    """The SPEC's `unresolved.cache_key` is "same composition as `file_facts` (§3.4),
    so an abstention is invalidated by the same events that invalidate a fact". A
    reader that saw only `file_facts` would call a file that produced only refusals
    stale forever and re-resolve it on every loop."""
    file_id, content_hash = _record(p6_conn, tmp_path, name="Blank.pdf", body=b"   ")
    key = fact_cache_key(**dict(BASELINE, content_hash=content_hash))
    write_unresolved(p6_conn, file_id=file_id, content_hash=content_hash,
                     field_key="subject", reason=NO_CANDIDATE_EVIDENCE,
                     attempted_producers=(DIRECT_ROUTE, RULE_ROUTE), evidence_refs=(),
                     cache_key=key)
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=key) is False
    ocr = fact_cache_key(**dict(BASELINE, content_hash=content_hash,
                                analysis_tier="ocr"))
    assert is_stale(p6_conn, file_id=file_id, content_hash=content_hash,
                    cache_key=ocr) is True


def test_the_fact_key_is_not_p5s_extraction_key(p6_conn):
    """The naming trap. Two functions, two questions, one design sentence."""
    content_hash = BASELINE["content_hash"]
    mine = fact_cache_key(**BASELINE)
    theirs = extraction_cache_key(content_hash=content_hash,
                                  extractor_name="pdf.text",
                                  extractor_version="1.0.0",
                                  analysis_tier="native",
                                  config_fingerprint="sha256:config-1")
    assert mine != theirs

    ours = set(inspect.signature(fact_cache_key).parameters)
    p5 = set(inspect.signature(extraction_cache_key).parameters)
    assert "extractor_name" not in ours and "config_fingerprint" not in ours
    assert "model_identifier" not in p5 and "prompt_fingerprint" not in p5

    # Runtime introspection, not a source-text search: this file's own docstrings
    # name `extractors.runs.cache_key` and a text guard would match them.
    namespace = vars(cache_module).values()
    assert not any(one is extraction_cache_key for one in namespace)
    assert not any(getattr(one, "__name__", "") == "extractors.runs"
                   for one in namespace)

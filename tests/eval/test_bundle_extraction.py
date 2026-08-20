# tests/eval/test_bundle_extraction.py
import json
from pathlib import Path

import pytest

from eval_harness.bundle import (
    P4_RUN_FIELDS, P4_TEXT_UNIT_FIELDS, add_extraction_output, add_extraction_run,
    add_file_entry, add_text_unit, extraction_outputs, extraction_runs, open_bundle,
    text_units,
)
from eval_harness.store import create_eval_schema

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _snapshot(conn):
    return open_bundle(conn, corpus_form="snapshot", source_scan_ref="scan-fixture",
                       pinned_plan_id="plan-fixture", pinned_plan_version="1",
                       policy_settings={})


def test_the_promoted_run_columns_are_exactly_the_ones_the_spec_enumerates():
    # SPEC Contract out §3: "run_id, file_id, content_hash, extractor name and
    # version, source_type, config_fingerprint, completeness, coverage,
    # observation_count."
    assert P4_RUN_FIELDS == (
        "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
        "source_type", "config_fingerprint", "completeness", "coverage",
        "observation_count",
    )
    assert P4_TEXT_UNIT_FIELDS == (
        "run_id", "container_path", "unit_locator", "text", "length", "truncated",
    )


def test_a_run_row_round_trips_every_field_p4_publishes(eval_conn):
    # "Read exactly as P4 publishes them; P2 defines none of it." Fields P2 does
    # not promote to columns survive in the verbatim row.
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    for row in _load("p4_runs.json"):
        add_extraction_run(eval_conn, bundle_id, row=row)
    stored = {r["run_id"]: r for r in extraction_runs(eval_conn, bundle_id)}
    ocr = stored["run-ocr-1"]
    assert ocr["completeness"] == "capped"
    assert ocr["coverage"] == {"units": "pages", "processed": 40, "total": 312}
    assert ocr["analysis_tier"] == "ocr"          # not promoted, not lost
    assert ocr["config"] == {"dpi": 200, "languages": ["en", "zh-Hans"],
                             "recognition": "accurate"}
    assert stored["run-broken-1"]["failure_reason"] == "damaged"


def test_two_extractor_versions_of_one_content_hash_coexist(eval_conn):
    # This is why bundle_extraction_output is keyed by hash PLUS version: one
    # bundle holds both sides of a version-to-version diff (§8.5).
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="1.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"old"}')
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="2.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"new"}')
    both = extraction_outputs(eval_conn, bundle_id, content_hash="sha256:syl")
    assert {r["extractor_version"] for r in both} == {"1.0.0", "2.0.0"}
    assert {r["payload"] for r in both} == {'{"v":"old"}', '{"v":"new"}'}


def test_the_observation_key_survives_an_extractor_upgrade(eval_conn):
    # P4's observation_key deliberately EXCLUDES the extractor version, so a
    # citation recorded today still resolves after an upgrade (§8.7). P2's key
    # deliberately includes it. Neither should be "fixed" into agreement.
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="1.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"old"}')
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:syl",
                          extractor_version="2.0.0",
                          observation_key="sha256:obs-a", payload='{"v":"new"}')
    cited = eval_conn.execute(
        "SELECT DISTINCT observation_key FROM bundle_extraction_output "
        "WHERE bundle_id = ?", (bundle_id,)).fetchall()
    assert [r["observation_key"] for r in cited] == ["sha256:obs-a"]


def test_an_extraction_payload_is_opaque(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    blob = "not JSON, still an observation payload"
    add_extraction_output(eval_conn, bundle_id, content_hash="sha256:x",
                          extractor_version="1.0.0", observation_key="sha256:k",
                          payload=blob)
    assert extraction_outputs(eval_conn, bundle_id)[0]["payload"] == blob


def test_text_units_round_trip_with_their_container_path(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _snapshot(eval_conn)
    for row in _load("p4_text_units.json"):
        add_text_unit(eval_conn, bundle_id, row=row)
    page_four = text_units(eval_conn, bundle_id, run_id="run-ocr-1")[0]
    assert page_four["container_path"] == [{"kind": "page", "index": 4}]
    assert page_four["unit_locator"] == "page=4"
    assert page_four["text"] == "recovered page four text"
    assert page_four["truncated"] is False
    whole_file = text_units(eval_conn, bundle_id, run_id="run-native-1")[0]
    assert whole_file["container_path"] == []          # D12: [] is the whole file


def test_a_metadata_safe_bundle_refuses_text_units_and_names_the_open_question(eval_conn):
    # SPEC Open question 5: "What exactly does 'metadata-safe' exclude?" P2 does
    # not answer it. It refuses, naming OQ5, rather than deciding either way in
    # silence. One line changes the day OQ5 closes.
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(eval_conn, corpus_form="metadata_safe",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    with pytest.raises(NotImplementedError) as excinfo:
        add_text_unit(eval_conn, bundle_id, row=_load("p4_text_units.json")[0])
    assert "Open question 5" in str(excinfo.value)


def test_p2_invents_no_text_unit_field():
    # The shape is P4's D12 and P2 publishes none of it.
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness" / "bundle.py"
    text = src.read_text(encoding="utf-8")
    for invented in ("excerpt", "snippet", "page_text", "ocr_text", "full_text"):
        assert invented not in text

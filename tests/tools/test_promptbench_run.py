"""The bench's run loop, end to end, with a fake model: files written, resume, score.

`run_site` is what the packet's numbers come from, so it is run here over two real
suites (C, and A with its P6 world and glossary swap) against a client that
answers from the case's own expectation. What is asserted is the plumbing: one
JSON per call, the recorded fields, the summary, and that a second run skips
what the first recorded.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llm_harness.vocabulary import A_FACT, C_PLACEMENT  # noqa: E402
from llm_harness.wire_handles import wire_handle  # noqa: E402

from tools.promptbench.__main__ import run_site  # noqa: E402
from tools.promptbench.clients import CallMeta  # noqa: E402
from tools.promptbench.dossiers import BENCH_HANDLE_KEY  # noqa: E402


def _handle_of_first_released(payload: bytes) -> tuple[str, str]:
    """The keyed handle and value of the first released item in the model-visible
    bytes -- what a model would actually cite."""
    body = json.loads(payload.decode("utf-8").split("The dossier follows.\n", 1)[1])
    item = body["released_evidence"][0]
    return item["observation_key"], item["value"]


def _fake_c_client(payload: bytes) -> tuple[bytes, CallMeta]:
    body = json.loads(payload.decode("utf-8").split("The dossier follows.\n", 1)[1])
    handle, value = _handle_of_first_released(payload)
    candidates = list(body["allowed_vocabulary"])
    conflicts = [c["conflict_id"] for c in body["conflicts"]]
    response = {"claims": [{
        "payload": {"destination": candidates[0], "per_dimension_support": [
            {"dimension": "a level", "value": value[:6], "support": "direct"}],
            "alternatives": candidates[1:2], "conflicts_considered": conflicts,
            "support": 1, "next_support": 0, "refinement": "not_applicable"},
        "citations": [{"evidence_ref": handle, "cited_span": value[:6],
                       "why_it_supports": "the released text carries it"}]}]}
    return json.dumps(response).encode("utf-8"), CallMeta(
        model_id="fake", locality="local", latency_seconds=0.01,
        prompt_tokens=10, completion_tokens=5, num_ctx=8192,
        prompt_bytes=len(payload), settings={"fake": True})


def _fake_a_client(payload: bytes) -> tuple[bytes, CallMeta]:
    body = json.loads(payload.decode("utf-8").split("The dossier follows.\n", 1)[1])
    handle, value = _handle_of_first_released(payload)
    fields = list(body["allowed_vocabulary"])
    claims = [{"payload": {"field": fields[0], "value": value[:8]},
               "citations": [{"evidence_ref": handle, "cited_span": value[:8],
                              "why_it_supports": "the released text carries it"}]}]
    claims += [{"payload": {"field": f},
                "unknown": {"insufficiency_statement": "nothing states it"}}
               for f in fields[1:]]
    return json.dumps({"claims": claims}).encode("utf-8"), CallMeta(
        model_id="fake", locality="local", latency_seconds=0.01,
        prompt_tokens=10, completion_tokens=5, num_ctx=8192,
        prompt_bytes=len(payload), settings={"fake": True})


def test_run_site_c_writes_one_record_per_call_and_a_summary(tmp_path):
    out = tmp_path / "out"
    run_site(site=C_PLACEMENT, candidate_names=["walk"], model_names=["fake"],
             out=out, case_ids=["C01", "C04"], clients={"fake": _fake_c_client},
             ledger_path=tmp_path / "ledger.json", log=lambda *a: None)
    files = sorted((out / "calls" / C_PLACEMENT / "walk" / "fake").glob("*.json"))
    assert [f.stem for f in files] == ["C01", "C04"]
    record = json.loads(files[0].read_text())
    assert record["template_id"] == "c_placement.unratified.walk.2026-09-06"
    assert record["request"].startswith("You are a destination judge.")
    assert record["meta"]["num_ctx"] == 8192
    judgement = record["judgement"]
    assert judgement["parsed"] and judgement["json_schema_valid"]
    assert judgement["citations_span_matched"] == 1
    summary = json.loads((out / "summary.json").read_text())
    row = summary["summary"]["rows"][0]
    assert (row["site"], row["candidate"], row["model"], row["cases"]) == (
        C_PLACEMENT, "walk", "fake", 2)
    assert (out / "summary.md").read_text().startswith("# promptbench summary")

    # Resume: a second run over the same out dir records nothing new.
    before = {f: f.stat().st_mtime_ns for f in files}
    run_site(site=C_PLACEMENT, candidate_names=["walk"], model_names=["fake"],
             out=out, case_ids=["C01", "C04"], clients={"fake": _fake_c_client},
             ledger_path=tmp_path / "ledger.json", log=lambda *a: None)
    assert {f: f.stat().st_mtime_ns for f in files} == before


def test_stress_tables_render_one_row_per_case_and_one_column_per_arm(tmp_path):
    from tools.promptbench.report import stress_tables
    from tools.promptbench.suites import cases_for

    out = tmp_path / "out"
    run_site(site=C_PLACEMENT, candidate_names=["walk"], model_names=["fake"],
             out=out, case_ids=["C01", "C04"], clients={"fake": _fake_c_client},
             ledger_path=tmp_path / "ledger.json", log=lambda *a: None)
    table = stress_tables(out, cases_for(C_PLACEMENT))
    lines = table.splitlines()
    assert lines[0].endswith("| walk / fake |")
    assert len(lines) == 2 + len(cases_for(C_PLACEMENT))
    c01 = next(l for l in lines if l.startswith("| C01"))
    c04 = next(l for l in lines if l.startswith("| C04"))
    c02 = next(l for l in lines if l.startswith("| C02"))
    assert "correct / acc_direct" in c01          # the fake chose the first id, C01's answer
    assert "ANSWERED" in c04                       # a should-abstain case the fake answered
    assert c02.endswith("| — |")                   # not run: no cell


def test_run_site_a_builds_a_p6_world_and_swaps_the_glossary(tmp_path):
    out = tmp_path / "out"
    run_site(site=A_FACT, candidate_names=["ratified-glossary", "proposed-glossary"],
             model_names=["fake"], out=out, case_ids=["A03"],
             clients={"fake": _fake_a_client}, ledger_path=tmp_path / "ledger.json",
             log=lambda *a: None)
    records = {}
    for name in ("ratified-glossary", "proposed-glossary"):
        path = out / "calls" / A_FACT / name / "fake" / "A03.json"
        records[name] = json.loads(path.read_text())
    assert records["ratified-glossary"]["glossary_in_force"].endswith("field_glossary.json")
    assert records["proposed-glossary"]["glossary_in_force"].endswith(
        "field_glossary_proposal_2026-09-06.json")
    # The dossier the model saw carried the proposal's meaning under that arm
    # and the ratified meaning under the other.
    proposed = records["proposed-glossary"]["request"]
    ratified = records["ratified-glossary"]["request"]
    assert "the institution that offers this course and term" in proposed
    assert "the person's own school" in ratified
    # A real P6 world: the observation keys the model was shown are P4's, keyed.
    body = json.loads(proposed.split("The dossier follows.\n", 1)[1])
    assert body["folder_levels"][0]["field"] in body["allowed_vocabulary"]
    assert all(item["observation_key"].startswith("handle:")
               for item in body["released_evidence"])
    judgement = records["proposed-glossary"]["judgement"]
    assert judgement["parsed"] and len(judgement["verdicts"]) == len(
        body["allowed_vocabulary"])

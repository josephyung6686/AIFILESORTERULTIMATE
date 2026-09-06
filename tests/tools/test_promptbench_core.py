"""The bench before any model: its clients, its ledger, its judge, its bytes.

Every claim the D2 packet makes with a number rests on this instrument, so the
instrument is tested with fake models first. Nothing here opens a socket.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from llm_harness.records import PromptDefinition  # noqa: E402
from llm_harness.vocabulary import (  # noqa: E402
    ABSTAIN, ACCEPT_DIRECT, C_PLACEMENT, INVENTED_NODE, REJECT,
)
from llm_harness.wire_handles import wire_handle  # noqa: E402

from tools.promptbench.cases import Case, Item, check_cases, evidence  # noqa: E402
from tools.promptbench.clients import (  # noqa: E402
    CallLedger, CallMeta, CloudCapReached, NUM_CTX_MAXIMUM, NUM_CTX_MINIMUM,
    cloud_client, local_client, num_ctx_for,
)
from tools.promptbench.dossiers import (  # noqa: E402
    BENCH_HANDLE_KEY, dossier_of, model_visible_bytes,
)
from tools.promptbench.judge import judge, site_dependencies_for  # noqa: E402
from tools.promptbench.report import aggregate  # noqa: E402

SUBJECT = "file:bench-1"


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="c_placement.unratified.test.2026-09-06",
        template_bytes=b"TEMPLATE\nThe dossier follows.\n",
        response_schema_bytes=b'{"type":"object"}',
        call_site=C_PLACEMENT, call_site_version="1",
        shaping_policy_bytes=b'{"policy":"bench"}')


def _case() -> Case:
    heading = evidence(subject_ref=SUBJECT, address="heading:1",
                       value="PHYS 1401 Problem Set 4", zone="heading")
    return Case(
        case_id="T01", site=C_PLACEMENT, title="a test case", persona="Priya",
        traces=("00:110",), subject_ref=SUBJECT,
        allowed_vocabulary=("node-a", "node-b"),
        evidence=(heading,),
        items=(Item(evidence_ref="node-a", kind="candidate",
                    location="Coursework / PHYS1401 / homework"),
               Item(evidence_ref="node-b", kind="candidate",
                    location="Coursework / PHYS1401")),
        plan_version="plan-bench",
        expect={"destination": "node-a"}, should_abstain=False,
    )


def _response(case: Case, *, destination, cite: bool = True) -> bytes:
    key = wire_handle(case.evidence[0].key, key=BENCH_HANDLE_KEY)
    claim = {"payload": {"destination": destination, "per_dimension_support": [],
                         "alternatives": ["node-b"], "conflicts_considered": [],
                         "support": 1, "next_support": 0}}
    if cite:
        claim["citations"] = [{"evidence_ref": key, "cited_span": "PHYS 1401",
                               "why_it_supports": "names the course"}]
    else:
        claim["unknown"] = {"insufficiency_statement": "nothing names a course"}
    return json.dumps({"claims": [claim]}).encode("utf-8")


# --- bytes --------------------------------------------------------------------


def test_model_visible_bytes_are_template_then_keyed_dossier():
    case = _case()
    payload = model_visible_bytes(dossier_of(case), _prompt())
    assert payload.startswith(b"TEMPLATE\nThe dossier follows.\n{")
    text = payload.decode("utf-8")
    # The observation key is keyed on the wire; the node ids and the subject
    # handle are what the product would send.
    assert case.evidence[0].key not in text
    assert wire_handle(case.evidence[0].key, key=BENCH_HANDLE_KEY) in text
    assert '"node-a"' in text
    body = json.loads(text.split("The dossier follows.\n", 1)[1])
    assert sorted(body) == [
        "allowed_vocabulary", "call_site", "conflicts", "eligibility_reason",
        "evidence_items", "field_glossary", "folder_levels", "max_dossier_tokens",
        "plan_version", "policy_version", "reduction_rung", "released_evidence",
        "response_schema", "shaping_policy", "subject_ref"]


def test_check_cases_refuses_duplicates_and_nothing_released():
    case = _case()
    with pytest.raises(ValueError):
        check_cases((case, case))
    import dataclasses
    silent = dataclasses.replace(case, evidence=tuple(
        dataclasses.replace(e, released=False) for e in case.evidence))
    with pytest.raises(ValueError):
        check_cases((silent,))


# --- judge --------------------------------------------------------------------


def test_judge_accepts_the_labelled_destination_and_reads_it_back():
    case = _case()
    dossier = dossier_of(case)
    verdict = judge(case, dossier, _response(case, destination="node-a"),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.parsed and verdict.json_schema_valid
    assert verdict.worst_outcome == ACCEPT_DIRECT and verdict.accepted
    assert verdict.correct is True and verdict.abstained is False
    assert (verdict.citations_total, verdict.citations_span_matched) == (1, 1)


def test_judge_records_an_invented_node_as_the_validators_reject():
    case = _case()
    verdict = judge(case, dossier_of(case), _response(case, destination="node-zzz"),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == REJECT
    assert [INVENTED_NODE] in [v["reasons"] for v in verdict.verdicts]
    assert verdict.correct is False


def test_judge_reads_an_unknown_claim_as_abstention():
    case = _case()
    verdict = judge(case, dossier_of(case),
                    _response(case, destination="none", cite=False),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ABSTAIN and verdict.abstained
    assert verdict.correct is False          # the case wanted node-a
    assert verdict.detail["false_abstention"] is True


# --- clients --------------------------------------------------------------------


def test_num_ctx_grows_with_the_prompt_and_refuses_beyond_the_window():
    assert num_ctx_for(1_000) == NUM_CTX_MINIMUM
    assert num_ctx_for(20_000) > NUM_CTX_MINIMUM
    assert num_ctx_for(60_000) <= NUM_CTX_MAXIMUM
    with pytest.raises(ValueError):
        num_ctx_for(400_000)


def test_local_client_sets_think_off_and_num_ctx_and_records_them():
    seen: dict = {}

    def fake_post(url, body, *, timeout):
        seen["body"] = json.loads(body)
        return json.dumps({"response": '{"claims": []}', "done_reason": "stop",
                           "prompt_eval_count": 1200, "eval_count": 9}).encode()

    call = local_client(post=fake_post)
    answer, meta = call(b"x" * 9000)
    assert answer == b'{"claims": []}'
    assert seen["body"]["think"] is False
    assert seen["body"]["options"]["num_ctx"] == meta.num_ctx >= NUM_CTX_MINIMUM
    assert seen["body"]["options"]["temperature"] == 0 and seen["body"]["format"] == "json"
    assert meta.prompt_tokens == 1200 and meta.completion_tokens == 9
    assert meta.settings["think"] is False and meta.locality == "local"


def test_local_client_refuses_a_prompt_that_filled_the_context():
    def fake_post(url, body, *, timeout):
        num_ctx = json.loads(body)["options"]["num_ctx"]
        return json.dumps({"response": "{}", "done_reason": "stop",
                           "prompt_eval_count": num_ctx}).encode()

    with pytest.raises(RuntimeError, match="truncated"):
        local_client(post=fake_post)(b"x" * 100)


class _Usage:
    prompt_tokens = 321
    completion_tokens = 45


class _Choice:
    finish_reason = "stop"

    class message:
        content = '{"claims": []}'


class _Response:
    choices = [_Choice()]
    usage = _Usage()


def test_cloud_client_spends_the_ledger_before_the_socket_and_stops_at_the_cap(
        tmp_path, monkeypatch):
    monkeypatch.setattr("tools.promptbench.clients.credentials",
                        lambda: ("not-a-real-key", "https://example.invalid"))
    ledger = CallLedger(path=tmp_path / "ledger.json", cap=2)
    calls: list[dict] = []

    def fake_send(**kw):
        calls.append(kw)
        return _Response()

    client = cloud_client(ledger, send=fake_send)
    answer, meta = client(b"payload-1")
    assert answer == b'{"claims": []}'
    assert meta.prompt_tokens == 321 and meta.settings["temperature"] == 0.0
    client(b"payload-2")
    with pytest.raises(CloudCapReached):
        client(b"payload-3")
    assert len(calls) == 2, "the third call never reached the socket"
    state = json.loads((tmp_path / "ledger.json").read_text())
    assert state == {"calls": 2, "prompt_tokens": 642, "completion_tokens": 90,
                     "cap": 2}
    # A second ledger over the same file continues the count.
    assert CallLedger(path=tmp_path / "ledger.json", cap=2).summary()["calls"] == 2


# --- report -----------------------------------------------------------------------


def test_aggregate_reports_the_five_rates_per_candidate_and_model():
    def call(case_id, *, should, abstained, correct, accepted, tokens=(10, 2)):
        return {
            "site": C_PLACEMENT, "case_id": case_id, "candidate": "c1",
            "model": "cloud",
            "meta": {"latency_seconds": 1.0, "prompt_tokens": tokens[0],
                     "completion_tokens": tokens[1]},
            "judgement": {
                "parsed": True, "json_schema_valid": True, "verdicts": [
                    {"reasons": []}], "accepted": accepted,
                "citations_total": 2, "citations_span_matched": 1,
                "should_abstain": should, "abstained": abstained,
                "correct": correct, "worst_outcome": "accept_direct"},
        }

    rows = aggregate([
        call("a", should=False, abstained=False, correct=True, accepted=True),
        call("b", should=False, abstained=True, correct=False, accepted=False),
        call("c", should=True, abstained=True, correct=None, accepted=False),
    ])["rows"]
    assert len(rows) == 1
    row = rows[0]
    assert row["cases"] == 3
    assert row["grounding_rate"] == 0.5
    assert row["abstain_rate_on_should_abstain"] == 1.0
    assert row["correct_rate_on_should_answer"] == 0.5
    assert row["false_abstain_rate_on_should_answer"] == 0.5
    assert row["prompt_tokens_total"] == 30 and row["completion_tokens_total"] == 6

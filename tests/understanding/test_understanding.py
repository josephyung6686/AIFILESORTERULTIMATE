# tests/understanding/test_understanding.py
"""The understanding pass, against a fake transport. No key is an answer."""
from __future__ import annotations

import io
import json
import sqlite3

import pytest

from understanding.answer import interpret_answer
from understanding.catalog import ModelIdNotListed, resolve_model_id
from understanding.dossier import FileView
from understanding.onboarding import questions_from_names
from understanding.provider import CompletionRequest
from understanding.reasoning import read_completion
from understanding.run import Budget, run_understanding
from understanding.store import audit
from readers.model_understanding_http import (
    DeepSeekUnderstanding, OllamaUnderstanding, ProviderError,
)

SECRET = "sk-test-understanding-secret"


def _answer(**overrides) -> str:
    body = {
        "kind": "syllabus",
        "life_area": "academic",
        "course": "CHEM",
        "term": "2026 Fall",
        "company": None,
        "project": None,
        "concerns": "user",
        "confidence": 0.9,
        "evidence_quote": "office hours",
    }
    body.update(overrides)
    return json.dumps(body)


def _completion(content: str, *, finish: str = "stop", reasoning: str = "") -> dict:
    message = {"content": content}
    if reasoning:
        message["reasoning_content"] = reasoning
    return {
        "choices": [{"finish_reason": finish, "message": message}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 4},
    }


class Fake:
    def __init__(self, payloads, *, locality="cloud"):
        self.payloads = list(payloads)
        self.locality_name = locality
        self.calls = []

    def provider_name(self):
        return "fake"

    def locality(self):
        return self.locality_name

    def complete(self, request: CompletionRequest):
        assert SECRET not in request.prompt
        assert request.thinking == "disabled"
        self.calls.append(request)
        return self.payloads.pop(0)


def _conn():
    conn = sqlite3.connect(":memory:")
    return conn


def _view(name="notes.txt", text="office hours json", **kwargs):
    return FileView(
        file_id=kwargs.pop("file_id", name),
        path=kwargs.pop("path", f"/folder/{name}"),
        filename=name, text=text, **kwargs)


def test_catalog_accepts_the_flash_alias_and_names_a_bad_id():
    assert resolve_model_id("deepseek-v4-flash", {"deepseek-flash", "deepseek-v4-pro"}) == "deepseek-flash"
    assert resolve_model_id("deepseek-flash", {"deepseek-v4-flash"}) == "deepseek-v4-flash"
    assert resolve_model_id("deepseek-v4-pro", {"deepseek-v4-pro"}) == "deepseek-v4-pro"
    with pytest.raises(ModelIdNotListed) as raised:
        resolve_model_id("DeepSeek-R1", {"deepseek-flash"})
    assert "DeepSeek-R1" in str(raised.value)
    assert "deepseek-flash" in str(raised.value)


def test_empty_content_with_length_is_a_retry_and_not_an_answer():
    reading = read_completion(_completion("", finish="length", reasoning="thinking"))
    assert reading.retry
    assert reading.content == ""
    conn = _conn()
    provider = Fake([
        _completion("", finish="length", reasoning="thinking"),
        _completion(_answer()),
    ])
    report = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t")
    assert report.called_complete == 2
    assert report.results[0].status == "answered"
    assert provider.calls[1].max_tokens == provider.calls[0].max_tokens * 4


def test_category_gate_rejects_business_when_it_was_not_declared():
    understood = interpret_answer(
        _answer(life_area="business_operations", confidence=0.99),
        file_id="f", declared_areas={"academic"})
    assert understood.needs_review
    assert "business_operations" in understood.reason
    kept = interpret_answer(
        _answer(life_area="academic"), file_id="f", declared_areas={"academic"})
    assert kept.needs_review is False
    assert kept.life_area == "academic"


def test_private_and_protected_files_are_not_sent():
    conn = _conn()
    provider = Fake([])
    report = run_understanding(
        conn=conn,
        views=[
            _view("secret.pem", path="/folder/secret.pem", file_id="pem"),
            _view("notes.txt", path="/medical/notes.txt", file_id="med"),
            _view("held.txt", held=True, file_id="held"),
        ],
        declared_areas={"academic"}, private_areas={"medical"},
        provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t")
    assert provider.calls == []
    assert report.sent == 0
    assert report.excluded == 3


def test_consent_is_required_and_offline_sends_nothing():
    conn = _conn()
    provider = Fake([_completion(_answer())])
    with pytest.raises(Exception) as raised:
        run_understanding(
            conn=conn, views=[_view()], declared_areas={"academic"},
            private_areas=set(), provider=provider, model_id="m",
            offline=False, consent=False)
    assert SECRET not in str(raised.value)
    assert provider.calls == []
    report = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="m",
        offline=True, consent=True)
    assert report.sent == 0
    assert provider.calls == []
    assert report.results[0].reason == "offline"


def test_cache_hit_does_not_call_the_provider_again():
    conn = _conn()
    provider = Fake([_completion(_answer())])
    first = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t")
    assert first.sent == 1
    second = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t2")
    assert second.cache_hits == 1
    assert second.called_complete == 0
    assert provider.calls and len(provider.calls) == 1


def test_budget_stop_and_low_confidence_need_review():
    conn = _conn()
    provider = Fake([_completion(_answer(confidence=0.2))])
    report = run_understanding(
        conn=conn, views=[_view("a.txt", file_id="a"), _view("b.txt", file_id="b")],
        declared_areas={"academic"}, private_areas=set(), provider=provider,
        model_id="deepseek-flash", offline=False, consent=True,
        budget=Budget(max_calls=0), now="t")
    assert report.budget_stopped == 2
    assert provider.calls == []
    provider = Fake([_completion(_answer(confidence=0.2))])
    report = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t")
    assert report.needs_review == 1
    assert report.results[0].understanding.needs_review


def test_malformed_output_is_rejected():
    conn = _conn()
    provider = Fake([_completion("not json")])
    report = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=provider, model_id="m",
        offline=False, consent=True, now="t")
    assert report.needs_review == 1
    assert report.results[0].status == "needs_review"


def test_audit_and_provider_errors_do_not_contain_the_key():
    conn = _conn()
    audit(conn, file_id="f", fields=("filename",), model_id="deepseek-flash",
          prompt_tokens=1, completion_tokens=1, cache_hit=False, recorded_at="t")
    dumped = " ".join(str(row) for row in conn.execute("SELECT * FROM understanding_audit"))
    assert SECRET not in dumped

    def post(url, headers, body):
        raise RuntimeError(SECRET)

    adapter = DeepSeekUnderstanding(
        api_key=SECRET, base_url="https://api.deepseek.com", post=post)
    with pytest.raises(ProviderError) as raised:
        adapter.complete(CompletionRequest(
            model_id="deepseek-flash", prompt="Reply with one JSON object",
            max_tokens=16, thinking="disabled"))
    assert SECRET not in str(raised.value)
    with pytest.raises(ProviderError):
        OllamaUnderstanding(base_url="https://example.invalid", post=post)


def test_small_dossiers_share_one_call():
    conn = _conn()
    files = [_answer(kind="a"), _answer(kind="b")]
    # file_id is overwritten by interpret from the view, but the object must parse.
    payload = {"files": [json.loads(_answer()) , json.loads(_answer())]}
    payload["files"][0]["file_id"] = "a.txt"
    payload["files"][1]["file_id"] = "b.txt"
    provider = Fake([_completion(json.dumps(payload))])
    report = run_understanding(
        conn=conn,
        views=[_view("a.txt", file_id="a.txt"), _view("b.txt", file_id="b.txt")],
        declared_areas={"academic"}, private_areas=set(), provider=provider,
        model_id="deepseek-flash", offline=False, consent=True, now="t")
    assert report.called_complete == 1
    assert report.sent == 2


def test_onboarding_questions_require_consent_and_use_names_only():
    provider = Fake([_completion(json.dumps({
        "summary": "These names look like a course.",
        "questions": ["Which term is CHEM?"],
    }))])
    with pytest.raises(Exception):
        questions_from_names(["CHEM.pdf"], declared_areas={"academic"},
                             provider=provider, model_id="deepseek-v4-pro",
                             consent=False)
    assert provider.calls == []
    result = questions_from_names(
        ["CHEM.pdf"], declared_areas={"academic"}, provider=provider,
        model_id="deepseek-v4-pro", consent=True)
    assert "CHEM.pdf" in provider.calls[0].prompt
    assert "course" in result["summary"].lower() or result["questions"]


def test_dry_run_prints_fields_and_the_formula_and_sends_nothing(tmp_path):
    import cli
    (tmp_path / "notes.txt").write_text("hello")
    (tmp_path / "secret.pem").write_text(SECRET)
    out = io.StringIO()
    code = cli.main([str(tmp_path), "--model-dry-run"], out=out)
    text = out.getvalue()
    assert code == 0
    assert "Nothing was sent" in text
    assert "filename" in text
    assert "input_usd_per_million" in text
    assert SECRET not in text
    assert "Candidates: 1" in text


def test_rate_limit_waits_and_is_not_an_answer():
    from understanding.backoff import RateLimited
    from readers.model_understanding_http import status_error

    refused = status_error(429, SECRET)
    assert isinstance(refused, RateLimited)
    assert SECRET not in str(refused)
    assert status_error(429, "0.25").retry_after == 0.25

    class Once(Fake):
        def complete(self, request):
            assert SECRET not in request.prompt
            self.calls.append(request)
            if len(self.calls) == 1:
                raise RateLimited(0.25)
            return self.payloads.pop(0)

    slept = []
    report = run_understanding(
        conn=_conn(), views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=Once([_completion(_answer())]),
        model_id="deepseek-flash", offline=False, consent=True, now="t",
        sleep=slept.append, attempts=3)
    assert slept == [0.25]
    assert report.results[0].status == "answered"
    assert report.called_complete == 1


def test_two_batches_overlap_when_workers_allow_it():
    import threading
    barrier = threading.Barrier(2)

    class Overlap(Fake):
        def complete(self, request):
            barrier.wait(timeout=2)
            self.calls.append(request)
            if "one object per dossier" in request.prompt:
                count = request.prompt.count('"file_id"')
                body = {"files": [json.loads(_answer()) for _ in range(count)]}
                return _completion(json.dumps(body))
            return _completion(_answer())

    views = [_view(f"n{i}.txt", file_id=f"n{i}.txt") for i in range(9)]
    report = run_understanding(
        conn=_conn(), views=views, declared_areas={"academic"},
        private_areas=set(), provider=Overlap([]), model_id="deepseek-flash",
        offline=False, consent=True, now="t", workers=2, sleep=lambda _seconds: None)
    assert report.sent == 9
    assert report.called_complete == 2


def test_logic_and_reasoning_keep_the_category_gate():
    from understanding.roles import group_files, resolve_conflict

    provider = Fake([_completion(json.dumps({"groups": [
        {"life_area": "academic", "file_ids": ["a"], "reason": "course"},
        {"life_area": "business", "file_ids": ["b"], "reason": "guess"},
    ]}))])
    with pytest.raises(Exception):
        group_files([], provider=provider, model_id="deepseek-chat",
                    declared_areas={"academic"}, consent=False)
    assert provider.calls == []
    grouped = group_files(
        [{"file_id": "a", "life_area": "academic", "kind": "notes"}],
        provider=provider, model_id="deepseek-chat",
        declared_areas={"academic"}, consent=True, sleep=lambda _seconds: None)
    assert grouped["groups"][0]["life_area"] == "academic"
    assert grouped["groups"][1]["life_area"] == "needs_review"
    assert provider.calls[0].model_id == "deepseek-chat"

    provider = Fake([_completion(_answer(life_area="business"))])
    resolved = resolve_conflict(
        file_id="a", dossier={"file_id": "a", "filename": "notes.txt"},
        candidates=["academic", "business"], provider=provider,
        model_id="deepseek-v4-pro", declared_areas={"academic"}, consent=True,
        sleep=lambda _seconds: None)
    assert resolved.needs_review
    assert provider.calls[0].model_id == "deepseek-v4-pro"


def test_onboarding_questions_command_sends_nothing_without_consent(tmp_path):
    import cli
    (tmp_path / "CHEM.pdf").write_text(SECRET)
    out = io.StringIO()
    code = cli.main([str(tmp_path), "--onboarding-questions"], out=out)
    text = out.getvalue()
    assert code == 0
    assert "sent nothing" in text
    assert SECRET not in text
    assert "Names seen: 1" in text

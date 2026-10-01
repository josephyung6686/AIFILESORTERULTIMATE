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


def test_a_profile_note_reaches_the_prompt_and_not_the_persons_name():
    from onboarding.answers import model_context
    note = model_context({
        "person_name": SECRET,
        "lives": ["academic"],
        "school": "Example School",
        "courses": [{"code": "CHEM 101", "name": "Chemistry", "term": "2026 Fall"}],
        "companies": ["Example Lab"],
        "situations": {"academic": "academic.coursework"},
    })
    conn = _conn()
    provider = Fake([_completion(_answer()), _completion(_answer())])
    first = run_understanding(
        conn=conn, views=[_view(text="office hours Tuesday")],
        declared_areas={"academic"}, private_areas=set(), provider=provider,
        model_id="deepseek-flash", offline=False, consent=True, now="t",
        profile_note=note)
    assert first.sent == 1
    prompt = provider.calls[0].prompt
    assert SECRET not in prompt
    assert "Example School" in prompt
    assert "CHEM 101" in prompt
    assert "Example Lab" in prompt
    assert "Business is not a fallback" in prompt
    assert '"concerns" is one string' in prompt
    second = run_understanding(
        conn=conn, views=[_view(text="office hours Tuesday")],
        declared_areas={"academic"}, private_areas=set(), provider=provider,
        model_id="deepseek-flash", offline=False, consent=True, now="t2",
        profile_note=note + " changed")
    assert second.cache_hits == 0
    assert second.sent == 1
    assert len(provider.calls) == 2


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


def test_a_stored_excerpt_is_capped_before_it_can_leave():
    from understanding.attach import stored_excerpt
    from understanding.dossier import build_dossier
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE extraction_runs (run_id TEXT, file_id TEXT, started_at TEXT)")
    conn.execute("CREATE TABLE text_units (run_id TEXT, text TEXT)")
    words = " ".join(f"w{i}" for i in range(500))
    conn.execute("INSERT INTO extraction_runs VALUES ('r', 'f', 't')")
    conn.execute("INSERT INTO text_units VALUES ('r', ?)", (words,))
    text = stored_excerpt(conn, "f")
    assert text.split()[0] == "w0"
    assert len(text.split()) == 400
    assert "w499" not in text
    dossier = build_dossier(
        FileView(file_id="f", path="/folder/notes.txt", filename="notes.txt", text=text),
        private_areas=set())
    assert len(dossier["text_excerpt"].split()) == 400
    assert SECRET not in dossier["text_excerpt"]
    # A filename record and the document can share one timestamp. The body
    # is the excerpt. The filename is already its own field.
    conn.execute("INSERT INTO extraction_runs VALUES ('name', 'f', 't')")
    conn.execute("INSERT INTO text_units VALUES ('name', 'notes.txt')")
    assert stored_excerpt(conn, "f").split()[0] == "w0"


def test_a_one_element_concerns_list_is_not_a_type_error():
    understood = interpret_answer(
        _answer(concerns=["user"]), file_id="f", declared_areas={"academic"})
    assert understood.concerns == "user"
    assert not understood.needs_review
    with pytest.raises(Exception) as raised:
        interpret_answer(
            _answer(concerns=["user", "someone_else"]),
            file_id="f", declared_areas={"academic"})
    assert type(raised.value).__name__ == "AnswerRejected"
    assert not isinstance(raised.value, TypeError)


def test_one_bad_member_does_not_drop_the_rest_of_the_batch():
    good = json.loads(_answer())
    listed = json.loads(_answer())
    listed["concerns"] = ["user", "someone_else"]
    also = json.loads(_answer(kind="notes"))
    payload = {"files": [good, listed, also]}
    provider = Fake([_completion(json.dumps(payload))])
    conn = _conn()
    report = run_understanding(
        conn=conn,
        views=[
            _view("a.txt", file_id="a.txt"),
            _view("b.txt", file_id="b.txt"),
            _view("c.txt", file_id="c.txt"),
        ],
        declared_areas={"academic"}, private_areas=set(), provider=provider,
        model_id="deepseek-flash", offline=False, consent=True, now="t",
        workers=2, sleep=lambda _seconds: None)
    assert len(report.results) == 3
    by_id = {item.file_id: item for item in report.results}
    assert by_id["a.txt"].status == "answered"
    assert by_id["b.txt"].status == "needs_review"
    assert by_id["c.txt"].status == "answered"
    rows = conn.execute(
        "SELECT file_id, exception_class FROM understanding_audit"
    ).fetchall()
    assert {row[0] for row in rows} == {"a.txt", "b.txt", "c.txt"}
    rejected = [row for row in rows if row[0] == "b.txt"]
    assert rejected and rejected[0][1] == "AnswerRejected"


def test_an_unexpected_error_is_audited_as_its_class_and_not_the_key():
    class Boom(Fake):
        def complete(self, request):
            raise RuntimeError(SECRET)

    conn = _conn()
    report = run_understanding(
        conn=conn, views=[_view()], declared_areas={"academic"},
        private_areas=set(), provider=Boom([]), model_id="deepseek-flash",
        offline=False, consent=True, now="t", sleep=lambda _seconds: None)
    assert report.results[0].status == "needs_review"
    assert SECRET not in report.results[0].reason
    row = conn.execute(
        "SELECT exception_class, fields_sent FROM understanding_audit"
    ).fetchone()
    assert row[0] == "RuntimeError"
    assert SECRET not in " ".join(str(cell) for cell in row)


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


def test_after_understanding_prints_life_areas_including_cached_answers():
    """The rules' gist is printed before this pass. This block is the pass."""
    from understanding.answer import Understanding
    from understanding.attach import print_after_understanding
    from understanding.run import FileResult, PassReport

    def named(file_id, area, *, needs=False):
        return Understanding(
            file_id=file_id, kind="resume", life_area=area,
            course=None, term=None, company=None, project=None,
            concerns="user", confidence=0.4 if needs else 0.9,
            evidence_quote="cover letter", needs_review=needs,
            reason="confidence is low" if needs else "")

    report = PassReport(results=[
        FileResult("a", "cache", understanding=named("a", "career")),
        FileResult("b", "answered", understanding=named("b", "career")),
        FileResult("c", "answered", understanding=named("c", "academic", needs=True)),
        FileResult("d", "needs_review", reason="budget stop"),
        FileResult("e", "excluded", reason="protected"),
    ])
    out = io.StringIO()
    print_after_understanding(report, out)
    text = out.getvalue()
    assert "After understanding: 5 files." in text
    assert "2 career" in text
    assert "1 academic" in text
    assert "1 need review" in text
    assert "1 excluded" in text
    assert "1 of the named files need review" in text
    assert "business" not in text


def test_http_402_stops_the_pass_and_names_the_balance_in_the_audit():
    """A fake 402. Not retried, and later batches are not sent."""
    from understanding.attach import print_after_understanding
    from understanding.backoff import BALANCE_EMPTY, InsufficientBalance

    class Empty(Fake):
        def complete(self, request):
            self.calls.append(request)
            raise InsufficientBalance()

    provider = Empty([])
    conn = _conn()
    views = [_view(f"{i}.txt", file_id=f"{i}.txt", text="office hours json")
             for i in range(9)]
    slept = []
    report = run_understanding(
        conn=conn, views=views, declared_areas={"academic", "career"},
        private_areas=set(), provider=provider, model_id="deepseek-flash",
        offline=False, consent=True, now="t", workers=1, attempts=4,
        sleep=slept.append)
    assert len(provider.calls) == 1
    assert slept == []
    assert report.called_complete == 1
    assert report.balance_notice == BALANCE_EMPTY
    assert report.needs_review == 9
    classes = {
        row[0] for row in conn.execute(
            "SELECT exception_class FROM understanding_audit")
    }
    assert classes == {"InsufficientBalance"}
    assert "ProviderError" not in classes
    out = io.StringIO()
    print_after_understanding(report, out)
    text = out.getvalue()
    assert BALANCE_EMPTY in text
    assert SECRET not in text


def test_a_402_response_and_an_insufficient_balance_body_are_not_retried(monkeypatch):
    import io as _io
    import urllib.error
    import urllib.request
    from understanding.backoff import (
        BALANCE_EMPTY, InsufficientBalance, complete_with_backoff,
    )
    from understanding.provider import CompletionRequest
    from readers.model_understanding_http import DeepSeekUnderstanding, post_json, status_error

    payload = json.dumps({
        "error": {
            "message": "Insufficient Balance",
            "code": "invalid_request_error",
        },
    }).encode()
    calls = []

    def unpaid(request, timeout=None):
        calls.append(request.full_url)
        raise urllib.error.HTTPError(
            request.full_url, 402, "Payment Required", hdrs=None,
            fp=_io.BytesIO(payload))

    monkeypatch.setattr(urllib.request, "urlopen", unpaid)
    with pytest.raises(InsufficientBalance) as raised:
        post_json("https://api.deepseek.com/chat/completions",
                  {"Authorization": "Bearer " + SECRET},
                  {"model": "deepseek-flash"})
    assert str(raised.value) == BALANCE_EMPTY
    assert SECRET not in str(raised.value)
    assert type(raised.value).__name__ == "InsufficientBalance"
    assert len(calls) == 1

    def paid_looking(request, timeout=None):
        calls.append("200")

        class _Body:
            def read(self):
                return payload

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        return _Body()

    monkeypatch.setattr(urllib.request, "urlopen", paid_looking)
    with pytest.raises(InsufficientBalance):
        post_json("https://api.deepseek.com/chat/completions", {}, {"model": "x"})

    refused = status_error(400, None, payload)
    assert isinstance(refused, InsufficientBalance)
    ordinary = status_error(401, None, b'{"error":{"message":"Invalid API key"}}')
    assert type(ordinary).__name__ == "ProviderError"
    assert "balance" not in str(ordinary)
    vague = status_error(400, None, b'{"error":{"message":"the balance of evidence is low"}}')
    assert type(vague).__name__ == "ProviderError"
    assert "evidence" not in str(vague)

    adapter = DeepSeekUnderstanding(
        api_key=SECRET, base_url="https://api.deepseek.com", post=post_json)
    monkeypatch.setattr(urllib.request, "urlopen", unpaid)
    before = len(calls)
    slept = []
    with pytest.raises(InsufficientBalance):
        complete_with_backoff(
            adapter,
            CompletionRequest(
                model_id="deepseek-flash", prompt="Reply with one JSON object",
                max_tokens=16, thinking="disabled"),
            sleep=slept.append, attempts=4)
    assert len(calls) == before + 1
    assert slept == []
    assert SECRET not in str(raised.value)


def test_the_facts_summary_prints_an_empty_balance_without_the_body():
    import cli
    from llm_harness.records import CallFailed

    def failed(kind, status):
        return CallFailed(
            request_identity="req", release_id="rel", audit_id=1,
            explanation=json.dumps({"type": kind, "status": status}),
            validator_version="v", policy_version="p")

    out = io.StringIO()
    cli._print_fact_pass(
        written=0, withheld={}, files=2,
        outcomes=[
            ("a", failed("InsufficientBalance", 402)),
            ("b", failed("ProviderDidNotAnswer", 401)),
        ],
        model_id="deepseek-chat", out=out)
    text = out.getvalue()
    assert "cloud provider balance is empty — top up or switch keys" in text
    assert "1 refused: the call did not come back (CallFailed)." in text
    assert "Insufficient Balance" not in text
    assert SECRET not in text

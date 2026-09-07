"""`104` §7 Phase 0a: A_fact answered by a model on this machine, end to end.

D1's local half. `00`:189-193's second operation mode -- *"Local extraction plus a
user-installed local LLM for eligible dossiers"* -- driven through `cli.main` over a
synthetic corpus, with the plan database read back for the counts `103` §10 names as
the pass test: `llm_response >= 1`, `llm_verdict >= 1`, at least one `llm_supported`
fact, and the "Facts from a model" line printing a true sent count.

**NO OLLAMA RUNS HERE, and no network either.** A stub HTTP server on loopback
speaks the one endpoint `readers.model_ollama` calls, records every request body,
and answers from the dossier it was handed. That is what makes these assertions
about THE WIRING -- does a local target reach the gate, the transport, the
validator and the fact store -- rather than about what a language model happens to
say today. The real model is measured separately, by hand, and its numbers go in
the report.

**The stub answers by copying, which is the point.** A supported fact has to be
GROUNDED: `llm_harness.value_grounding` requires the proposed value's characters to
be a whole-token run of a released value the claim cites. So the stub reads the
dossier's own `released_evidence`, cites one item, and proposes a run of tokens
taken out of that item's text. An answer invented here would be rejected by the
validator, and the test would be asserting that the validator works rather than
that the pass runs.

**`--enable-cloud` appears nowhere in this file.** That is the assertion, not an
omission: a model on the person's own machine needs no consent to send, because
nothing is sent.
"""
from __future__ import annotations

import io
import json
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

import cli
from llm_harness.value_grounding import grounding_tokens
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)

SITUATION = "academic.coursework"
LABEL = "Coursework"
MODEL_ID = "stub-qwen3:8b"

#: The dossier is appended to the ratified template, and this is the template's own
#: last sentence, so the JSON half is whatever follows it.
#:
#: IT USED TO BE `'{"allowed_vocabulary"'`, on the argument that `canonical_json`
#: sorts keys so the body "begins here and nowhere else in the payload". True when
#: written and false since `104` R-58: the body is emitted frame first now, so
#: `call_site` leads and this locator found nothing at all. The coupling was
#: invisible -- nothing said the locator rested on an ordering decision made in
#: another module -- which is why the replacement leans on ratified text that cannot
#: move without the owner rather than on a key order that can.
DOSSIER_FOLLOWS = "The dossier follows."

#: The one file in the corpus the detector marks protected. Measured rather than
#: assumed: it comes back `sensitive_personal, protected=True, basis=safety_domain`
#: from an ordinary run, which is what makes the negative test below a real one.
PROTECTED_NAME = "Passport scan.txt"
PROTECTED_SECRET = "K12345678"


def _corpus(root: Path) -> Path:
    """`tests/integration/test_103_diagnosis_backlog.py::_corpus`, plus the fifth.

    The four are that file's, unchanged, so the two tests describe one corpus. The
    fifth is protected, and it is here rather than in a test of its own because the
    guarantee is about what happens WHEN THE MODEL IS RUNNING over a mixed folder:
    a protected file that is never sent while its neighbours are is the standing
    rule working, and a protected file alone in a corpus proves nothing about it.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 08.txt").write_text(
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular momentum.\n")
    (corpus / "HW 3.txt").write_text(
        "Homework 3\n\nProblem 1. A ball is thrown upward...\n")
    (corpus / "Columbia Essay.txt").write_text(
        "Dear Admissions Committee at Columbia University,\nMy essay follows.\n")
    (corpus / PROTECTED_NAME).write_text(
        f"Passport\nHong Kong Special Administrative Region\n"
        f"Passport No. {PROTECTED_SECRET}\nDate of birth: 1 January 1990\n")
    return corpus


# --- a stub that speaks ollama, on loopback, in this process -------------------

def dossier_in(payload: str) -> dict:
    """The JSON half of the model-visible bytes, as the model would read it."""
    return json.loads(payload.split(DOSSIER_FOLLOWS, 1)[1])


def _first_supportable(dossier: dict) -> tuple[str, str, str, str] | None:
    """A field, a value, an evidence key and a span -- all copied, none invented.

    The value is a run of tokens lifted out of a released value, so
    `value_grounding.occurs_in` accepts it for the same reason a real model's
    correct answer is accepted: the characters are in the text the claim cites.
    """
    fields = [field for field in dossier.get("allowed_vocabulary", ())
              if isinstance(field, str)]
    released = [item for item in dossier.get("released_evidence", ())
                if isinstance(item, dict) and isinstance(item.get("value"), str)]
    for item in released:
        if len(grounding_tokens(item["value"])) < 2:
            continue
        span = item["value"].strip().splitlines()[0].strip()
        if not span or not fields:
            continue
        return fields[0], span, item["observation_key"], span
    return None


def _answer_for(payload: str) -> str:
    """One claim per allowed field: the first supported, the rest declined."""
    dossier = dossier_in(payload)
    fields = [field for field in dossier.get("allowed_vocabulary", ())
              if isinstance(field, str)]
    supportable = _first_supportable(dossier)
    claims = []
    if supportable is not None:
        field, value, evidence_ref, span = supportable
        claims.append({
            "payload": {"field": field, "value": value},
            "citations": [{"evidence_ref": evidence_ref, "cited_span": span,
                           "why_it_supports": "the value is copied from this span"}],
        })
    supported = {claims[0]["payload"]["field"]} if claims else set()
    for field in fields:
        if field in supported:
            continue
        claims.append({
            "payload": {"field": field},
            "unknown": {"insufficiency_statement":
                        "no released evidence carries this field"},
        })
    return json.dumps({"claims": claims or [
        {"payload": {"field": "work_type"},
         "unknown": {"insufficiency_statement": "the dossier released nothing"}}]})


class StubOllama:
    """`/api/chat` on loopback, recording everything it was asked."""

    def __init__(self, answer=_answer_for):
        self.requests: list[dict] = []
        self.raw: list[bytes] = []
        self._answer = answer
        recorder = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):  # keep pytest's output readable
                pass

            def do_POST(self):  # noqa: N802 - http.server's spelling
                body = self.rfile.read(int(self.headers["Content-Length"]))
                recorder.raw.append(body)
                request = json.loads(body)
                recorder.requests.append(dict(request, _path=self.path))
                prompt = request["messages"][0]["content"]
                reply = json.dumps({
                    "model": request["model"],
                    "message": {"role": "assistant",
                                "content": recorder._answer(prompt)},
                    "done": True,
                    "done_reason": "stop",
                    # Below the window every time: this stub is not the thing under
                    # test when the transport's truncation receipt is.
                    "prompt_eval_count": 16,
                    # `104` R-14. ollama's own name for the answer's token count,
                    # beside the prompt's. Both are what `usage_of` reads, and a
                    # stub that reported only one would let a half-written usage row
                    # pass for a whole one.
                    "eval_count": 7,
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reply)))
                self.end_headers()
                self.wfile.write(reply)

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        self.base_url = "http://127.0.0.1:%d" % self._server.server_address[1]

    def __enter__(self):
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *_exc):
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)

    def prompts(self) -> list[str]:
        return [request["messages"][0]["content"] for request in self.requests]


@pytest.fixture()
def stub():
    with StubOllama() as running:
        yield running


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database), *extra], out=out)
    return code, out.getvalue()


def _query(database: Path, sql: str, *params):
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _local_run(tmp_path, stub, monkeypatch):
    monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
    monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)
    assert code == 0, report
    return database, report


# --- `103` §10's pass test, on a local model ----------------------------------

def test_the_fact_pass_runs_and_writes_a_supported_fact(tmp_path, stub, monkeypatch):
    """PHASE 0a, in one test. Every number `103` §10 names as the pass condition,
    with no key, no consent and nothing over the internet.

    What made this impossible before was not the transport. It was one line:
    `_model_fact_pass` returned unless the operation mode was `hybrid`, and
    `hybrid` requires this folder's stored cloud consent. A model on the person's
    own machine needs none, and `00`:189-193 says so -- `offline` is "No content
    leaves the device; only local rules and LOCAL MODELS may run"."""
    database, report = _local_run(tmp_path, stub, monkeypatch)

    responses = _query(database, "SELECT COUNT(*) FROM llm_response")[0][0]
    verdicts = _query(database, "SELECT COUNT(*) FROM llm_verdict")[0][0]
    supported = _query(
        database,
        "SELECT field_key, model_identifier FROM file_facts "
        "WHERE reliability_state = 'llm_supported'")

    assert responses >= 1, report
    assert verdicts >= 1, report
    assert supported, report
    assert all(row[1] == MODEL_ID for row in supported), (
        "a fact the local model supported has to name the local model", supported)


def test_the_sent_line_is_true_and_names_the_local_model(tmp_path, stub, monkeypatch):
    """`103` §10's other half: "the 'Facts from a model' line prints the true sent
    count". A count of zero would mean the wiring reported a pass that did not
    happen, which is the untruth `WIRED_CALL_SITES` was added to stop."""
    database, report = _local_run(tmp_path, stub, monkeypatch)

    line = re.search(r"Facts from a model: (\d+) written, from (\d+) files? "
                     r"sent to (\S+?)\.", report)
    assert line, report
    assert int(line.group(2)) >= 1, report
    assert line.group(3) == MODEL_ID, report
    # THE A CALLS, and not every call the run made. Site B now runs in observe
    # mode against the same local model, so the stub sees its requests too. The
    # line is about the FACT pass and names A's model, so counting every request
    # against it would make it false the moment a second site was wired -- which
    # is the direction `104` §7 Phase 1 step 6 moves in.
    assert int(line.group(2)) == _calls_at(database, "A_fact"), (
        "the sent count is the number of A_fact calls that happened, not the "
        "number that were considered and not every site's calls")


def test_the_audit_row_names_the_local_model_and_says_local(
        tmp_path, stub, monkeypatch):
    """§8.4 audits "which model received the data". `release_ledger.model_target` is
    where that is written, and for a local run every word of it has to be true: the
    provider the transport actually called, the model id the person named, and the
    locality `Gate.release` was told -- which is the value the whole gate decides
    by and cannot itself measure."""
    database, _ = _local_run(tmp_path, stub, monkeypatch)

    targets = [json.loads(row[0]) for row in
               _query(database, "SELECT model_target FROM release_ledger")]

    assert targets
    for target in targets:
        assert target["locality"] == "local", target
        assert target["model_id"] == MODEL_ID, target
        assert target["provider"] == "ollama", target


def test_the_audit_row_names_the_window_the_model_was_actually_given(
        tmp_path, stub, monkeypatch):
    """§8.4 audits what the model was GIVEN, and the window is part of what it was
    given: ollama truncates a prompt that will not fit and says nothing, so two
    runs over one file under different windows are two different questions and
    only one of them was asked.

    THE ASSERTION IS THAT THE ROW IS TRUE, not that the row exists. The number is
    read out of `release_ledger.model_target` and compared against the `num_ctx`
    that actually went over the wire, because a record naming a window the request
    did not carry would describe a call that never happened, in the one place a
    person or a replay has to trust."""
    database, _ = _local_run(tmp_path, stub, monkeypatch)

    targets = [json.loads(row[0]) for row in
               _query(database, "SELECT model_target FROM release_ledger")]
    sent = {request["options"]["num_ctx"] for request in stub.requests}

    assert targets
    assert sent == {cli.LOCAL_CONTEXT_CEILING}
    for target in targets:
        assert target["context_tokens"] == cli.LOCAL_CONTEXT_CEILING, target
        assert {target["context_tokens"]} == sent, target


def test_the_request_carries_thinking_off_and_a_window(tmp_path, stub, monkeypatch):
    """`104` R-18 and the truncation finding, asserted where they are observable:
    on the bytes that actually left for the model."""
    _local_run(tmp_path, stub, monkeypatch)

    assert stub.requests
    for request in stub.requests:
        assert request["_path"] == "/api/chat"
        assert request["think"] is False
        assert request["format"] == "json"
        assert request["options"]["num_ctx"] >= len(
            request["messages"][0]["content"]) // 2
        assert request["options"]["num_ctx"] <= cli.LOCAL_CONTEXT_CEILING


# --- the standing rule, under a model that is running -------------------------

def test_a_protected_file_is_never_sent_to_the_local_model_either(
        tmp_path, stub, monkeypatch):
    """MARKED AND COUNTED, NEVER OPENED -- and "never" includes a model on the
    person's own machine.

    The gate alone would not have carried this. `privacy.denial.protected_cloud_denies`
    returns False for any locality that is not `cloud`, so a local target walks past
    it; what holds the line is `cli.model_route_permitted`, which refuses a protected
    file whatever the destination. This test exists because that is not obvious from
    either function on its own, and because the local route is the first thing in
    this product that could ever have tested it.

    Asserted twice over, because a count is not a guarantee: no dossier was built
    about that file, AND its text is not in any of the bytes the server received.
    """
    database, report = _local_run(tmp_path, stub, monkeypatch)

    protected = _query(
        database,
        "SELECT f.file_id FROM files f JOIN classifications c "
        "ON c.file_id = f.file_id WHERE c.protected = 1 AND f.filename = ?",
        PROTECTED_NAME)
    assert protected, "the corpus no longer contains a protected file: " + report
    file_id = protected[0][0]

    dossiers = _query(
        database, "SELECT COUNT(*) FROM llm_dossier WHERE subject_ref = ?",
        file_id)[0][0]
    assert dossiers == 0, "a protected file reached a dossier"

    for sent in stub.raw:
        assert PROTECTED_SECRET.encode("utf-8") not in sent
        assert b"Passport" not in sent


def test_the_other_files_were_sent_so_the_protected_one_is_a_refusal_not_a_silence(
        tmp_path, stub, monkeypatch):
    """The negative twin of the negative test. A run that sent nothing at all would
    pass the assertion above and mean nothing, which is how a coverage regression
    gets read as a safety guarantee."""
    _local_run(tmp_path, stub, monkeypatch)

    assert len(stub.requests) >= 1
    assert any("PHYS 1401" in prompt for prompt in stub.prompts()), (
        "the ordinary files were not sent either, so the protected one being "
        "absent says nothing about protection")


# --- the unchanged half, pinned -----------------------------------------------

def test_with_no_local_model_configured_nothing_is_asked_and_nothing_changes(
        tmp_path, stub):
    """The default, and the state the whole suite runs in. `conftest` clears the
    name, so this is what every other integration test is doing implicitly, made
    explicit once."""
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)

    assert code == 0
    assert cli.model_route(out=io.StringIO()) is None
    assert _query(database, "SELECT COUNT(*) FROM llm_response")[0][0] == 0
    assert stub.requests == []
    assert "Facts from a model" not in report


def test_a_cloud_model_without_consent_still_sends_nothing(tmp_path, monkeypatch):
    """THE CONDITION ON THE GUARD CHANGE, pinned so the widening cannot drift into
    the cloud half. `_model_fact_pass` used to test the mode alone; it now tests
    the A_fact target's LOCALITY, and a cloud target under any mode but `hybrid`
    must still return before a single dossier is built.

    No socket exists here to catch a mistake: if this regressed, the run would try
    to reach a real provider with a fake key, and the assertion below would fail on
    the refusal rather than on the send. Both are failures; only one costs money,
    and it is the one that cannot happen because the key is not real."""
    from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME
    from readers.model_routing import MODEL_NAME_OF_TIER

    monkeypatch.setenv(CREDENTIAL_NAME, "not-a-real-key")
    monkeypatch.setenv(BASE_URL_NAME, "https://example.invalid")
    for name in MODEL_NAME_OF_TIER.values():
        monkeypatch.setenv(name, "a-model")
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)

    assert code == 0
    assert _query(database, "SELECT COUNT(*) FROM llm_response")[0][0] == 0, report
    assert _query(database, "SELECT COUNT(*) FROM llm_dossier")[0][0] == 0, report


# --- `104` R-03: the sent count is responses, and nothing else ----------------

def _verdict(**over):
    """A real `P8Verdict`, because the thing under test reads one of its fields.

    A stand-in with a `claim_ref` attribute would pass whatever `_sent_and_abstained`
    does today and keep passing if the harness stopped setting that field.
    """
    from llm_harness.records import P8Verdict
    from llm_harness.vocabulary import ABSTAIN, SCHEMA_INVALID, SCOPE_FILE
    fields = dict(verdict_id="v1", dossier_id="d1", claim_ref="claim-1",
                  outcome=ABSTAIN, disposition=ABSTAIN, reasons=(SCHEMA_INVALID,),
                  may_propose=False, requires_review=False, citations_checked=(),
                  scope=SCOPE_FILE, validator_version="vv", policy_version="pv",
                  plan_version=None)
    fields.update(over)
    return P8Verdict(**fields)


def test_the_sent_count_is_what_a_model_answered_and_not_what_the_pass_produced():
    """`104` R-03 in one assertion. A gate refusal sends nothing -- P7 denies
    before `transport.issue` opens a socket -- and the line counted it as a file
    sent, on the one sentence a person reads to learn what happened to a folder.

    THE PRE-CALL ABSTENTION IS THE HALF A TYPE CHECK MISSES. `_persist_abstention`
    mints a `P8Verdict` and hands it back, so counting verdicts would report a run
    that deferred every file for budget as a run that sent every file, with no
    model asked at all. `claim_ref` is what the harness sets to tell them apart."""
    from llm_harness.records import CallFailed, ValidationUnavailable
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, PRE_CALL_NAMESPACE

    answered = _verdict(claim_ref="claim-1")
    not_asked = _verdict(claim_ref=PRE_CALL_NAMESPACE, reasons=(BUDGET_EXHAUSTED,))
    failed = CallFailed(request_identity="f3", release_id="r3", audit_id=None,
                        explanation="{}", validator_version="vv",
                        policy_version="pv")
    unavailable = ValidationUnavailable(missing=("prompt",))

    sent, abstained = cli._sent_and_abstained(
        [("f1", answered), ("f2", not_asked), ("f3", failed),
         ("f4", unavailable)])

    assert sent == 1
    assert abstained == {BUDGET_EXHAUSTED: 1}


def test_a_file_that_was_never_asked_about_gets_its_own_line_and_its_own_reason():
    """sf1-gate recorded the abstention and left the screen line. A file the run
    decided not to ask about then read exactly like a file a model shrugged at,
    and "the dossier would not fit" and "this scan has spent its budget" are
    different sentences to a person -- only one of them is about their file."""
    from llm_harness.vocabulary import BUDGET_EXHAUSTED, PRE_CALL_NAMESPACE
    out = io.StringIO()

    cli._print_fact_pass(
        written=0, withheld={}, files=1, model_id=MODEL_ID, out=out,
        outcomes=[("f1", _verdict(claim_ref=PRE_CALL_NAMESPACE,
                                  reasons=(BUDGET_EXHAUSTED,)))])
    printed = out.getvalue()

    assert "from 0 files sent" in printed
    assert BUDGET_EXHAUSTED in printed
    assert "before any call was made" in printed


def test_the_printed_sent_count_is_the_number_of_responses_on_disk(
        tmp_path, stub, monkeypatch):
    """The invariant, end to end and over a real corpus rather than over four
    hand-made outcomes: what the screen says was sent is what the database says
    came back. It holds for any corpus, so it keeps holding when the mix of
    refusals, abstentions and answers changes."""
    database, report = _local_run(tmp_path, stub, monkeypatch)

    line = re.search(r"Facts from a model: \d+ written, from (\d+) files? sent",
                     report)
    # SCOPED TO A, through the dossier that names the call site. `llm_response`
    # now holds site B's rows as well -- B runs in observe mode against the same
    # local model -- and the sentence on screen is about the fact pass.
    responses = _calls_at(database, "A_fact")

    assert line, report
    assert int(line.group(1)) == responses, report
    assert responses < len(stub.requests), (
        "site B reaches the same local model in observe mode, so the run makes "
        "more calls than the fact line counts", report)


def test_a_protected_file_is_not_told_that_nothing_has_classified_it():
    """The sentence was false about the one file it was most often printed for.

    `PRIVACY_BAR` is one word for three different reasons the route withholds a
    file, and the screen printed the unclassified sentence for all of them. A
    protected file IS classified -- the detector reached `sensitive_personal` and
    said so -- and telling its owner nothing had classified it is not a rounding
    of the truth, it is the opposite of what happened, on the line that explains
    why their passport was left alone."""
    out = io.StringIO()

    cli._print_fact_pass(
        written=0, withheld={cli.WITHHELD_PROTECTED: 1}, files=2,
        model_id=MODEL_ID, out=out, outcomes=[])
    # Collapsed, because `_wrapped` breaks these sentences across lines and a
    # phrase split by a newline is the same sentence to the person reading it.
    printed = " ".join(out.getvalue().split())

    assert "protected material" in printed
    assert "nothing has classified them" not in printed


def test_the_two_reasons_the_route_withholds_for_get_a_line_each():
    """Counted and named separately, because a person with one protected file and
    one the detector abstained on has two different things to do about them."""
    out = io.StringIO()

    cli._print_fact_pass(
        written=0, files=3, model_id=MODEL_ID, out=out, outcomes=[],
        withheld={cli.WITHHELD_PROTECTED: 1, cli.WITHHELD_UNCLASSIFIED: 2})
    printed = " ".join(out.getvalue().split())

    assert "1 of 3 files were not sent" in printed
    assert "2 of 3 files were not sent" in printed
    assert "protected material" in printed
    assert "nothing has classified them" in printed


def test_a_gate_refusal_is_named_by_the_gates_own_word_and_is_not_counted_as_sent():
    """`104` R-02 and R-03 meeting on one line, with a REAL `Denied` behind it.

    The screen said "1 refused: the gate refused the release (Refusal)". `Refusal`
    is the Python class that carried the answer and says nothing about the answer:
    protected material and a dossier over the ceiling are different things to do
    something about, and P7 had already decided which it was. `Denied.reason` is
    that decision, checked against a closed vocabulary when the gate builds it.

    And the same file must not appear in the sent count, which is R-03: the gate
    denies before `transport.issue` opens a socket, so nothing was sent about it.
    """
    from llm_harness.records import Refusal
    from privacy.denial import RemedyOption, deny

    denied = deny(
        "protected_cloud_target",
        explanation="this file is protected and the target is a cloud model",
        remedy_options=(RemedyOption(
            action="use_local_model",
            detail="ask a model on this device instead"),),
        evidence_refs=())
    refusal = Refusal(denied=denied, validator_version="vv", policy_version="pv")
    out = io.StringIO()

    cli._print_fact_pass(
        written=0, withheld={}, files=2, model_id=MODEL_ID, out=out,
        outcomes=[("f1", refusal), ("f2", _verdict(claim_ref="claim-1"))])
    printed = " ".join(out.getvalue().split())

    assert "from 1 file sent" in printed, "a refusal sends nothing"
    assert "protected_cloud_target" in printed
    assert "(Refusal)" not in printed, (
        "the class name is not the reason; it names the envelope the answer "
        "arrived in and tells a person nothing about what to do")


# --- `104` R-14: what the local call consumed, beside what was reserved ---------

def test_a_local_fact_call_records_the_tokens_it_actually_used(
        tmp_path, stub, monkeypatch):
    """The deployment D1 steers toward, recording what it spent.

    **`104` R-71 closed, and the count is why it was a strict xfail.** `len(rows)
    == responses` is the whole assertion: four A responses carried four usage rows
    and B's fifth carried none, because P9's authority bundle deliberately holds no
    usage sink. The sink now reaches `run_call` from the composition root, past the
    bundle, so every response this run wrote has the tokens it actually spent
    beside it.

    The cloud half of R-14 landed first and left this one blind: `cli.model_route`
    gives the LOCAL model site A_fact whenever one is configured, so on the ordinary
    local deployment every usage row would have carried its reservation and no
    tokens at all. Both routes are handed the same mailbox now.

    `reserved_cost` is what the budget put aside -- one call, its unit -- and the
    token counts are ollama's own. The pair is the point: the budget still enforces
    calls, and the distance between the estimate and the truth is readable beside it
    without changing what it enforces.
    """
    database, report = _local_run(tmp_path, stub, monkeypatch)

    rows = _query(
        database,
        "SELECT prompt_tokens, completion_tokens, prompt_cache_hit_tokens, "
        "model_id, response_format, reserved_cost FROM llm_call_usage")
    responses = _query(database, "SELECT COUNT(*) FROM llm_response")[0][0]

    assert len(rows) == responses >= 1, report
    for prompt, completion, cache_hit, model_id, fmt, reserved in rows:
        assert prompt == 16, "the stub's `prompt_eval_count`, read not invented"
        assert completion == 7, "the stub's `eval_count`"
        # ollama's `/api/chat` reports no cache counter. `None` says nobody counted,
        # where a zero would claim nothing was served from cache -- and
        # `prompt_eval_count` does fall on a hit, so the effect is in the total even
        # though its size is not reported.
        assert cache_hit is None
        assert model_id == MODEL_ID
        assert fmt == "json", "what this transport actually sends in `format`"
        assert reserved == format(cli.FACT_CALL_COST, "f")


def test_the_usage_row_joins_to_the_dossier_it_describes(tmp_path, stub, monkeypatch):
    """A usage row nothing can join is a number with no call attached to it."""
    database, report = _local_run(tmp_path, stub, monkeypatch)

    joined = _query(
        database,
        "SELECT COUNT(*) FROM llm_call_usage u "
        "JOIN llm_dossier d ON d.dossier_id = u.dossier_id")[0][0]
    total = _query(database, "SELECT COUNT(*) FROM llm_call_usage")[0][0]

    assert joined == total >= 1, report
def _calls_at(database, call_site: str) -> int:
    """Responses recorded at one site, read through the dossier that names it.

    NOT counted off the stub's prompts. Site B now reaches the same local model
    in observe mode and its dossier is JSON in the same envelope, so a text probe
    counts both; `llm_dossier.call_site` is what the product itself wrote down.
    """
    return _query(
        database,
        "SELECT COUNT(*) FROM llm_response r JOIN llm_dossier d "
        "ON d.dossier_id = r.dossier_id WHERE d.call_site = ?", call_site)[0][0]


# --- `104` §7 Phase 1 step 6: site B runs and applies nothing ----------------

def test_site_b_records_a_dossier_a_response_and_a_verdict(
        tmp_path, stub, monkeypatch):
    """The first half of observe mode: the call HAPPENS and is written down.

    A site that recorded nothing would be indistinguishable from a site nobody
    wired, which is the state `104` R-04 names -- B, C, D and E injected as
    `None` since P11 landed. The dossier proves a request was built through the
    real gate, the response proves the model answered, and the verdict proves the
    validator ran on what it said."""
    database, _ = _local_run(tmp_path, stub, monkeypatch)

    dossiers = _query(database, "SELECT COUNT(*) FROM llm_dossier "
                                "WHERE call_site = 'B_group'")[0][0]
    verdicts = _query(
        database,
        "SELECT COUNT(*) FROM llm_verdict v JOIN llm_dossier d "
        "ON d.dossier_id = v.dossier_id WHERE d.call_site = 'B_group'")[0][0]

    assert dossiers >= 1
    assert _calls_at(database, "B_group") >= 1
    assert verdicts >= 1


def test_site_b_writes_no_accepted_group_and_no_membership_a_model_chose(
        tmp_path, stub, monkeypatch):
    """The second half, and the one that makes the first half safe.

    `104` §7 Phase 1 step 6: "apply nothing until Phase 3 fixes R-15 and R-16."
    R-16 is that `apply_p8_verdict` writes no `display_label`, no
    `group_category` and no `coherence_verdict`, so a per-member
    include/exclude/uncertain answer collapses to blanket memberships. Applying a
    verdict under a mapping known to lose the answer writes the wrong thing
    confidently.

    `ObservedOnly` is what stops it, and the assertion is on the tables rather
    than on the wrapper: no membership carries a verdict reference, because a
    verdict reference is what a model-chosen membership would carry."""
    database, _ = _local_run(tmp_path, stub, monkeypatch)

    assert _calls_at(database, "B_group") >= 1, "B did not run, so this proves nothing"

    from_model = _query(
        database,
        "SELECT COUNT(*) FROM memberships "
        "WHERE validation_verdict_ref IS NOT NULL")[0][0]

    assert from_model == 0, "a membership a model chose was written"


def test_site_bs_response_carries_the_tokens_it_spent(
        tmp_path, stub, monkeypatch):
    """`104` R-71, asserted at the site rather than in the total.

    The count above says every response has a row; this says WHICH response gained
    one, because a total can be made to balance by two errors. B is the site whose
    row was missing, so B is the site the join is asked about -- and it is asked
    through `llm_dossier.call_site`, which the product wrote down, rather than off
    the stub's prompts.

    The tokens are the stub's own `prompt_eval_count` and `eval_count`, read and
    not invented, and they are the same numbers A's rows carry: one mailbox, one
    transport, one reading per call. What a B row must NOT be is a row with the
    reservation and no tokens, which is what a sink wired only to A would leave.
    """
    database, report = _local_run(tmp_path, stub, monkeypatch)

    rows = _query(
        database,
        "SELECT u.prompt_tokens, u.completion_tokens, u.model_id, u.reserved_cost "
        "FROM llm_call_usage u JOIN llm_dossier d ON d.dossier_id = u.dossier_id "
        "WHERE d.call_site = 'B_group'")

    assert _calls_at(database, "B_group") >= 1, "B did not run, so this proves nothing"
    assert len(rows) == _calls_at(database, "B_group"), report
    for prompt, completion, model_id, reserved in rows:
        assert prompt == 16, "the stub's `prompt_eval_count`, read not invented"
        assert completion == 7, "the stub's `eval_count`"
        assert model_id == MODEL_ID
        assert reserved == format(cli.FACT_CALL_COST, "f")


def test_site_b_is_asked_under_a_draft_that_says_unratified(
        tmp_path, stub, monkeypatch):
    """What makes an observe run auditable after the fact. Every B row points at
    a template id carrying the packet's status in the id itself, so nobody has to
    remember which text a record was written under."""
    database, _ = _local_run(tmp_path, stub, monkeypatch)

    assert _calls_at(database, "B_group") >= 1
    assert cli.OBSERVE_TEMPLATE_ID["B_group"].startswith("b_group.unratified.")

# tests/integration/test_a_fact_reuse_after_a_verdict.py
"""`104` R-109: a resumed run does not buy the answers it already paid for.

R-13's cache shipped and R-109 is what it missed. `104` R-109: *"After R-108's crash
the same database was re-run at d409f58: extraction resumed from its records ... but
the fact pass began again from the first file -- `llm_call_reuse` stayed at 0 and 120
recorded responses were not consulted, so the two hours of local calls are spent
twice and a cloud rerun would be billed twice."* `00`:44 is the rule it breaks: an
answer is *"tied to the content hash and the exact process that produced it"*, and an
identical request under an identical key is not a new question.

**The cause, measured on the corpus below before anything was changed.** The reuse
compared the still-open fields against the prior dossier's ABSTENTIONS only. A
`reject` is not an abstention: the model answered, the validator refused the answer,
no fact was written and the field came back open -- so run 2 asked the identical
question under the identical identity and got the identical rejection. Two files, two
calls on the first run and **two more** on an unchanged second, `llm_call_reuse`
empty. On the owner's run almost every verdict was a reject.

**It was not the key.** The same measurement counted the identity rows: four rows
over **two distinct** `identity_id`s, so nothing in `CALL_IDENTITY_DIMENSIONS` moved
between two runs of one checkout over unchanged files.
`test_the_identity_is_the_same_on_an_unchanged_second_run` pins that, because a
dimension that started varying would reopen R-109 through a door nobody was watching.

**Everything here is real except the socket**, exactly as in
`test_a_fact_call_cache.py`: `readers.model_routing.deepseek_invoke` is the documented
deployment seam, and the gate, the release ledger, the transport, the validator,
`apply_verdict` and the whole of `cli.run` are the production path. Counting `invoke`
calls counts model calls exactly.
"""
from __future__ import annotations

import dataclasses
import io
import json
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from privacy.gate import Gate  # noqa: E402
from privacy.resolve import UnresolvableSpan  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402

SITUATION = "academic.coursework"

#: R-13's own corpus, and for R-13's own reason: two files with releasable text and
#: no deterministic course code, so the rule stage settles nothing and both files
#: reach a model.
CORPUS = {
    "reading notes.txt":
        "Notes on the assigned reading for this seminar. The lecture covered the "
        "textbook chapters on momentum and energy, and the homework is due "
        "Thursday.\n",
    "week two notes.txt":
        "Second week of the course. Notes from the tutorial on aggregate demand, "
        "with the problem set questions the instructor assigned.\n",
}

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}

#: A supported claim citing nothing. The validator's own words for it are
#: `CITATION_NOT_FOUND` and the verdict is `reject` -- the outcome R-109 is about,
#: and the one the abstention-only comparison could not see.
UNCITED = "Something the evidence does not carry"


class _Socket:
    """Every model call this run makes, and the dossier each one carried.

    `answer` decides what comes back, so one class serves the rejecting run, the
    partly-accepting run and the failing run without three copies of the plumbing.
    """

    def __init__(self, answer=None) -> None:
        self.payloads: list[bytes] = []
        self._answer = answer or self.reject_everything

    def __len__(self) -> int:
        return len(self.payloads)

    def subjects(self) -> list[str]:
        return [self._body(payload)["subject_ref"] for payload in self.payloads]

    @staticmethod
    def _body(payload: bytes) -> dict:
        text = payload.decode("utf-8")
        return json.loads(text.split("The dossier follows.", 1)[1])

    @staticmethod
    def reject_everything(body: dict) -> bytes:
        return json.dumps({"claims": [
            {"payload": {"field": field, "value": UNCITED}, "citations": []}
            for field in body["allowed_vocabulary"]]}).encode("utf-8")

    @staticmethod
    def accept_the_work_type(body: dict) -> bytes:
        """One field accepted, the rest rejected.

        The accepted one is grounded the way the ratified schema asks: an
        `observation_key` copied from `released_evidence` and a `cited_span` copied
        out of that item's own value. `work_type` is the field the filename can
        carry, and `accept_direct` is what the four checks return for it.
        """
        name = next((item for item in body["released_evidence"]
                     if item["zone"] == "filename"), None)
        claims = []
        for field in body["allowed_vocabulary"]:
            if field == "work_type" and name is not None and "notes" in name["value"]:
                claims.append({
                    "payload": {"field": field, "value": "notes"},
                    "citations": [{"evidence_ref": name["observation_key"],
                                   "cited_span": "notes",
                                   "why_it_supports": "the name says what it is"}]})
            else:
                claims.append({"payload": {"field": field, "value": UNCITED},
                               "citations": []})
        return json.dumps({"claims": claims}).encode("utf-8")

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            return self._answer(self._body(payload))
        return invoke


@pytest.fixture()
def socket(monkeypatch):
    recorder = _Socket()
    monkeypatch.setattr(model_routing, "deepseek_invoke", recorder.factory)
    return recorder


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own key must not decide whether these tests pass."""
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


@pytest.fixture()
def corpus(tmp_path):
    folder = tmp_path / "holder" / "corpus"
    folder.mkdir(parents=True)
    for name, body in CORPUS.items():
        (folder / name).write_text(body)
    return folder


def _run(corpus, *extra) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", SITUATION, "--label", "Coursework",
              "--user", "jy", "--database", str(corpus.parent / "plan.sqlite"),
              *extra], out=out)
    return out.getvalue()


def _rows(corpus, sql, *params):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def _count(corpus, table) -> int:
    return _rows(corpus, f"SELECT count(*) AS n FROM {table}")[0]["n"]


def _outcomes(corpus) -> list[str]:
    return [row["outcome"] for row in _rows(
        corpus, "SELECT outcome FROM llm_verdict WHERE superseded_by IS NULL")]


# --- the defect itself ------------------------------------------------------------


def test_a_rejected_answer_is_not_bought_a_second_time(corpus, socket):
    """R-109 in one number. Measured before the fix: 2 calls, then 2 more."""
    _run(corpus, "--enable-cloud")
    first = len(socket)
    assert first == 2, socket.subjects()
    assert set(_outcomes(corpus)) == {"reject"}, _outcomes(corpus)

    _run(corpus)

    assert len(socket) == first, (
        f"the second run re-asked {len(socket) - first} questions whose answers "
        f"were already on disk: {socket.subjects()[first:]}")
    reuses = _rows(corpus, "SELECT * FROM llm_call_reuse")
    assert len(reuses) == first
    priors = {row["dossier_id"] for row in _rows(
        corpus, "SELECT dossier_id FROM llm_call_identity")}
    for reuse in reuses:
        assert reuse["prior_dossier_id"] in priors
        assert reuse["call_site"] == cli.A_FACT
        assert json.loads(reuse["reused_fields"])


def test_a_reused_question_spends_no_slot_no_release_and_no_call(corpus, socket):
    """"Nothing after this line is free": the reuse is read before the budget slot
    is reserved, before the gate mints a release and before the transport sends."""
    _run(corpus, "--enable-cloud")
    spent = {table: _count(corpus, table) for table in (
        "llm_budget_reservation", "release_ledger", "llm_response", "llm_dossier")}

    _run(corpus)

    assert {table: _count(corpus, table) for table in spent} == spent


def test_a_partly_accepted_answer_is_reused_for_what_is_still_open(corpus, socket):
    """One field accepted and settled, the rest rejected and still open.

    The second run's question is SMALLER than the first's -- which is exactly why
    the asked field set cannot be a dimension of the identity, as `call_identity`
    says -- and every field still in it already has an answer.
    """
    socket._answer = socket.accept_the_work_type
    _run(corpus, "--enable-cloud")
    first = len(socket)
    outcomes = _outcomes(corpus)
    assert "accept_direct" in outcomes and "reject" in outcomes, outcomes
    facts = _count(corpus, "file_facts")

    _run(corpus)

    assert len(socket) == first, socket.subjects()[first:]
    reuses = _rows(corpus, "SELECT * FROM llm_call_reuse")
    assert len(reuses) == first
    # What was reused is what was still OPEN, and the accepted field is not in it:
    # it was settled, so it never reached the comparison.
    for reuse in reuses:
        assert "work_type" not in json.loads(reuse["reused_fields"])
    assert _count(corpus, "file_facts") == facts, "a reuse writes no new fact"


def test_the_identity_is_the_same_on_an_unchanged_second_run(corpus, socket):
    """The other half of the diagnosis: the key did not move, the comparison did.

    Two runs of one checkout over unchanged files produce one `identity_id` per
    file. If a dimension ever starts carrying a run id, a timestamp or a path, this
    is the test that says so -- R-109 would come back as "the cache never hits" and
    look exactly like the defect this file is about.
    """
    _run(corpus, "--enable-cloud")
    _run(corpus)

    identities = _rows(corpus, "SELECT DISTINCT identity_id FROM llm_call_identity")
    assert len(identities) == 2
    dimensions = [json.loads(row["dimensions"]) for row in _rows(
        corpus, "SELECT dimensions FROM llm_call_identity")]
    assert {name for row in dimensions for name in row} == {
        "call_site", "content_hash", "extractor_versions", "model_id",
        "plan_version", "policy", "prompt_fingerprint", "schema_id", "subject_ref"}


# --- what a reuse must NOT swallow ------------------------------------------------


def test_a_call_that_failed_is_asked_again(corpus, socket, monkeypatch):
    """A provider that hangs up is not an answer. `CallFailed` is not a `P8Verdict`,
    so no identity is recorded and the next run asks -- which is the whole point of
    the exclusion: a transient failure must not become a permanent silence about
    the file."""
    def _hang_up(**_unused):
        def invoke(payload: bytes) -> bytes:
            socket.payloads.append(payload)
            raise ConnectionError("the provider hung up")
        return invoke

    monkeypatch.setattr(model_routing, "deepseek_invoke", _hang_up)
    _run(corpus, "--enable-cloud")
    failed = len(socket)
    assert failed == 2
    assert _count(corpus, "llm_call_failure") == 2
    assert _count(corpus, "llm_call_identity") == 0

    monkeypatch.setattr(model_routing, "deepseek_invoke", socket.factory)
    _run(corpus)

    assert len(socket) - failed == 2, "a failed call was remembered as an answer"
    assert _count(corpus, "llm_call_reuse") == 0


def test_a_call_the_gate_refused_is_asked_again(corpus, socket, monkeypatch):
    """`104` R-O's outcome, and the same exclusion. A refusal is recorded, the run
    goes on, and nothing about it says the question was answered."""
    def _refuse(self, request):
        raise UnresolvableSpan("the span does not belong to this request's target")

    # Restored by hand rather than with `monkeypatch.undo()`: the socket and the
    # environment are patched through the same `monkeypatch` instance, and undoing
    # all three would leave the second run with no model wired at all -- which makes
    # zero calls for a reason that has nothing to do with the reuse.
    real_release = Gate.release
    monkeypatch.setattr(Gate, "release", _refuse)
    _run(corpus, "--enable-cloud")
    assert len(socket) == 0, "a refused call still reached the transport"
    assert _count(corpus, "llm_call_identity") == 0

    monkeypatch.setattr(Gate, "release", real_release)
    _run(corpus, "--enable-cloud")

    assert len(socket) == 2, "a refusal was remembered as an answer"
    assert _count(corpus, "llm_call_reuse") == 0


# --- and what is a different question ---------------------------------------------


def test_changing_one_files_content_re_asks_that_file_alone(corpus, socket):
    """A rewrite is a new file version and a new identity; the other file's answer
    is untouched."""
    _run(corpus, "--enable-cloud")
    first = len(socket)

    (corpus / "reading notes.txt").write_text(
        "Rewritten notes for this seminar. The lecture now covers rotational "
        "motion, and the problem set is due the following Tuesday.\n")
    _run(corpus)

    assert len(socket) - first == 1
    assert _count(corpus, "llm_call_reuse") == 1


def test_changing_only_the_prompt_re_asks_every_file(corpus, socket, monkeypatch):
    """`00`:44 wants "model or prompt changes auditable", and a rejected answer is
    no more durable across a prompt change than an accepted one.

    Only `template_id` moves, so the ratified bytes and their digest are untouched
    and nothing changes but the fingerprint -- the dimension under test.
    """
    _run(corpus, "--enable-cloud")
    first = len(socket)

    real = cli.a_fact_prompt()
    monkeypatch.setattr(cli, "a_fact_prompt", lambda: dataclasses.replace(
        real, template_id=f"{real.template_id}.a-second-revision"))
    _run(corpus)

    assert len(socket) - first == 2
    assert _count(corpus, "llm_call_reuse") == 0

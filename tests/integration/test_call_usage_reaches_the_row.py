# tests/integration/test_call_usage_reaches_the_row.py
"""R-14's second half, wired: what a call consumed reaches the database.

`104` R-14 ends "`actual_cost` is a constant, not observed usage". The reading half
landed with the transport (`readers/model_deepseek.usage_of`); this is the wire from
there to a row, and it crosses four seams that each belong to someone:

    cli.main            builds the one-slot mailbox
    cli.model_route     hands it to `deepseek_routing(on_usage=...)`
    cli.run             hands it to `_model_fact_pass`
    fact_call_authorities carries it to `model_facts.fact_call_stage`
    harness.run_call    takes from it after `settle_call` and writes the row

**The budget is untouched and that is a ruling, not an omission.**
`cli.FACT_CALL_COST` is `Decimal("1")` and `FACT_CALLS_PER_SCAN_CEILING` is
`Decimal("200")`, so the budget's unit is CALLS -- 200 of them per scan -- and
`settle_call` still settles one call as one. What the row adds is the pair: what was
reserved beside what the provider says was consumed, so the difference is readable
per call and per scan without changing what the budget enforces. Re-denominating the
ceiling in tokens is an owner question (`00`:259 names coverage throttling as the
failure a wrong number causes).

**Nothing here stubs the usage path itself.** The socket is replaced, as everywhere
else in this suite, but the real `deepseek_invoke` is what runs -- so `on_usage`, the
mailbox, the keyword chain and the writer are the production code and only the bytes
coming back over the wire are the test's.
"""
from __future__ import annotations

import io
import json
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from readers import model_deepseek, model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402

SITUATION = "academic.coursework"

CORPUS = {
    "reading notes.txt":
        "Notes on the assigned reading for this seminar. The lecture covered the "
        "textbook chapters on momentum and energy, and the homework is due "
        "Thursday.\n",
}

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}

PROMPT_TOKENS = 4970
CACHE_HIT = 4480
CACHE_MISS = 490


class _Usage:
    prompt_tokens = PROMPT_TOKENS
    completion_tokens = 120
    prompt_cache_hit_tokens = CACHE_HIT
    prompt_cache_miss_tokens = CACHE_MISS


class _Message:
    def __init__(self, content: str) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str) -> None:
        self.message = _Message(content)
        self.finish_reason = "stop"


class _Response:
    def __init__(self, content: str, usage) -> None:
        self.choices = [_Choice(content)]
        if usage is not None:
            self.usage = usage


def _declining(payload_holder: list, usage=_Usage()):
    """A provider that declines every offered field and reports what it spent."""
    def send(*, api_key, base_url, model_id, max_tokens, prompt,
             timeout_seconds=None):
        payload_holder.append(prompt)
        body = json.loads(prompt.split("The dossier follows.", 1)[1])
        answer = json.dumps({"claims": [
            {"payload": {"field": field},
             "unknown": {"insufficiency_statement": "the evidence does not name it"}}
            for field in body["allowed_vocabulary"]]})
        return _Response(answer, usage)
    return send


@pytest.fixture()
def socket(monkeypatch):
    """The REAL `deepseek_invoke`, over a replaced socket.

    `model_routing.deepseek_invoke` is rebound to a factory that forwards every
    keyword `deepseek_routing` supplies -- `on_usage` included -- so the usage wire
    under test is the shipped one and only `send` is the test's.
    """
    sent: list[str] = []
    real = model_deepseek.deepseek_invoke

    def factory(**keywords):
        return real(**{**keywords, "send": _declining(sent)})

    monkeypatch.setattr(model_routing, "deepseek_invoke", factory)
    return sent


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, cli.LOCAL_MODEL_NAME,
                 *MODEL_NAME_OF_TIER.values()):
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


def _rows(corpus, sql):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql)]
    finally:
        conn.close()


# --- the wire -------------------------------------------------------------------


def test_one_row_per_answered_call_carrying_what_the_provider_reported(
        corpus, socket):
    _run(corpus, "--enable-cloud")

    rows = _rows(corpus, "SELECT * FROM llm_call_usage")
    assert len(rows) == len(socket) == 1
    row = rows[0]
    assert row["prompt_tokens"] == PROMPT_TOKENS
    assert row["completion_tokens"] == 120
    assert row["prompt_cache_hit_tokens"] == CACHE_HIT
    assert row["prompt_cache_miss_tokens"] == CACHE_MISS
    assert row["model_id"] == "a-logician"
    assert row["response_format"] == "json_object"


def test_the_row_joins_to_the_dossier_and_the_release_it_describes(corpus, socket):
    """A usage row nothing can join is a number with no call attached to it."""
    _run(corpus, "--enable-cloud")

    usage = _rows(corpus, "SELECT * FROM llm_call_usage")[0]
    dossiers = {row["dossier_id"] for row in _rows(
        corpus, "SELECT dossier_id FROM llm_dossier")}
    releases = {row["release_id"] for row in _rows(
        corpus, "SELECT release_id FROM llm_response")}

    assert usage["dossier_id"] in dossiers
    assert usage["release_id"] in releases


def test_what_was_reserved_is_recorded_beside_what_was_consumed(corpus, socket):
    """The pair is the point. The budget still settles one call as one -- the unit
    is CALLS, `FACT_CALL_COST` is 1 against a 200-per-scan ceiling -- and this is
    what makes the distance between the estimate and the truth readable without
    changing what the budget enforces."""
    _run(corpus, "--enable-cloud")

    usage = _rows(corpus, "SELECT * FROM llm_call_usage")[0]
    settled = _rows(corpus, "SELECT estimated_cost, actual_cost, status "
                            "FROM llm_budget_reservation")

    assert usage["reserved_cost"] == format(cli.FACT_CALL_COST, "f")
    assert [row["status"] for row in settled] == ["settled"]
    assert settled[0]["actual_cost"] == format(cli.FACT_CALL_COST, "f")


def test_a_provider_that_reports_nothing_still_leaves_the_call_recorded(
        corpus, monkeypatch):
    """Silence is an audit answer. A row with null token counts says "asked, and
    the provider told us nothing"; no row at all is indistinguishable from a call
    that never happened."""
    sent: list[str] = []
    real = model_deepseek.deepseek_invoke
    monkeypatch.setattr(model_routing, "deepseek_invoke", lambda **keywords: real(
        **{**keywords, "send": _declining(sent, usage=None)}))

    _run(corpus, "--enable-cloud")

    rows = _rows(corpus, "SELECT * FROM llm_call_usage")
    assert len(rows) == 1
    assert rows[0]["prompt_tokens"] is None
    assert rows[0]["reserved_cost"] == format(cli.FACT_CALL_COST, "f")


def test_a_second_run_reuses_and_therefore_records_no_new_usage(corpus, socket):
    """R-13 and R-14 meet: a call not made consumes nothing and is not billed for
    nothing either."""
    _run(corpus, "--enable-cloud")
    _run(corpus)

    assert len(socket) == 1
    assert len(_rows(corpus, "SELECT * FROM llm_call_usage")) == 1
    assert len(_rows(corpus, "SELECT * FROM llm_call_reuse")) == 1


# --- and the seams it crosses ----------------------------------------------------


def test_a_deployment_that_records_no_usage_is_a_real_deployment(conn):
    """Every keyword on the wire is defaulted, so a caller that never heard of the
    mailbox still builds a client, a route and a call."""
    import inspect

    for function, name in ((cli.model_route, "on_usage"),
                           (cli.run, "usage_recorder"),
                           (cli.fact_call_authorities, "usage_recorder"),
                           # `104` R-71's half of the same contract. Site B reaches
                           # `run_call` through this function rather than through
                           # `fact_call_authorities`, and a deployment that records
                           # no usage still asks B.
                           (cli.observed_run_call, "usage_recorder"),
                           (model_routing.deepseek_routing, "on_usage")):
        parameter = inspect.signature(function).parameters[name]
        assert parameter.default is None, (function, name)

    from llm_harness.harness import run_call

    assert inspect.signature(run_call).parameters[
        "usage_recorder"].default is None


def test_the_mailbox_holds_one_call_and_empties_when_read():
    """One slot, not a queue. `run_call` takes immediately after the call it made,
    so a second value in the box would mean a call nobody settled -- and a queue
    would hide it instead of losing it loudly."""
    box = cli.UsageMailbox()

    assert box.take() is None
    box(None)
    assert box.take() == {}
    box(model_deepseek.Usage(
        model_id="m", prompt_tokens=3, completion_tokens=1,
        prompt_cache_hit_tokens=2, prompt_cache_miss_tokens=1,
        response_format="json_object"))
    taken = box.take()
    assert taken["prompt_tokens"] == 3
    assert taken["prompt_cache_hit_tokens"] == 2
    assert box.take() is None


def test_the_price_hook_exists_and_is_unused():
    """`00`:251 budgets "maximum model cost per scan" in money, and this product
    has no rate card: prices are a deployment fact and nobody has supplied one. The
    hook is documented and `None`, so the day prices exist there is one place to put
    them -- and until then nothing multiplies a token by a number somebody guessed.
    """
    assert cli.TOKEN_PRICES is None

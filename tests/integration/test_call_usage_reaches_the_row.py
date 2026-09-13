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

**AND A LOCAL MODEL IS NOW PART OF THE DEPLOYMENT, `00` amendment 7(c).** This file
configured a cloud key and nothing else, and that stopped being a deployment site A
can run in: the gate, `cli.ask_the_gate`, reads every un-held file on this device
BEFORE anything about it may be sent, `cli.CLOUD_CLEARING_BASES` is what
`model_route_permitted` asks for a cloud target, and the rules' own word is no
longer among them. With no local model nothing is cleared, site A never reaches the
transport, and every row this file reads is absent -- which is the 0-for-1 these
pins measured. The local half is `StubOllama`, answering the gate `none_of_these`
and declining the situation, exactly as
`test_the_scoreboard_reuses_a_prior_runs_answers` does and for its reasons.

**AND THE ROWS ARE NOW READ AT SITE A.** `llm_call_usage` is written wherever a
call was ANSWERED, which since amendment 7(c) is the gate (over the local
transport, which reports its own tokens -- see
`test_local_model_fact_pass.test_a_local_fact_call_records_the_tokens_it_actually_
used`), site G, site C and site A alike. `[0]` off an unscoped read is whichever
site the rowid happened to give, and a count off one is four sites' calls reported
as the fact pass's. Every read below joins through `llm_dossier.call_site`, and the
reservations are read from the fact pass's own purse (`_reservations_in`).
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
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
# The two local sites' answers come from the files that own them, imported rather
# than copied on `test_site_e_reuses_its_answer`'s own rule: one stub speaking one
# protocol, so this file and the gate's own pins cannot drift into describing two
# different gates.
from test_local_model_fact_pass import (  # noqa: E402
    MODEL_ID, StubOllama, _answer_for, dossier_in,
)
from test_site_g_end_to_end import _decline  # noqa: E402
from test_site_h_gate import _clear  # noqa: E402

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
        # SITE G ARRIVES HERE TOO since `00` amendment 7(c): a file the gate CLEARED
        # may have its situation asked off the device, so this provider sees a
        # situation dossier whose schema is not site A's. Declining it field by
        # field would be a malformed claim the validator refuses -- a silence
        # reached by a fault -- so it is declined in the shape the ratified prompt
        # asks for, and the usage row it produces is a real one.
        if body["call_site"] == cli.G_SITUATION_SENSITIVITY:
            return _Response(_decline(body), usage)
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
    """The developer's own key and the developer's own local model, both cleared.

    The local names are not a formality: a machine with ollama running would answer
    the gate with whatever it pulled, and these token counts would then be a model
    nobody chose here. `_local_model` puts the stub's own names back.
    """
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, LOCAL_MODEL_NAME,
                 LOCAL_BASE_URL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
    for name, value in ENV.items():
        monkeypatch.setenv(name, value)


def _local_answer(payload: str) -> str:
    """The local half of the deployment, dispatched on the dossier's own site.

    `test_site_h_gate._dispatching` in shape, with site G declined rather than
    answered for the reason in this file's own header.
    """
    dossier = dossier_in(payload)
    site = dossier.get("call_site")
    if site == cli.H_RESTRICTED_KIND:
        return _clear(dossier)
    if site == cli.G_SITUATION_SENSITIVITY:
        return _decline(dossier)
    return _answer_for(payload)


@pytest.fixture(autouse=True)
def _local_model(monkeypatch, _no_ambient_key):
    """A local model for the whole test, because a run now needs one to send.

    AUTOUSE AND PER TEST, beside `_no_ambient_key` and for its reason: this is what
    the deployment IS since amendment 7(c), not something one pin arranges. One
    server for the test rather than one per run, so a second run of the same corpus
    is given the same base URL as the first.
    """
    with StubOllama(answer=_local_answer) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        yield stub


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
              "--accept-groups",
              *extra], out=out)
    return out.getvalue()


def _rows(corpus, sql, *params):
    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in conn.execute(sql, params)]
    finally:
        conn.close()


def _usage_at(corpus, call_site) -> list[dict]:
    """The usage rows ONE site's answered calls left behind.

    `llm_call_usage` is written wherever a call was answered and it carries the
    dossier, which carries the site. That was one site when R-14 was wired; since
    `00` amendment 7(c) a run of this one-file corpus answers at the gate, at site
    G, at site C and at site A, so a `[0]` off an unscoped read is whichever row
    the rowid gave and a count off one is four sites reported as the fact pass.
    """
    return _rows(
        corpus,
        "SELECT u.* FROM llm_call_usage u JOIN llm_dossier d ON "
        "d.dossier_id = u.dossier_id WHERE d.call_site = ?", call_site)


def _cloud_calls_at(socket, call_site) -> int:
    """How many prompts this run put on the CLOUD wire at one site.

    `socket` is the prompts `_declining` was handed, and it used to hold site A's
    alone. Site C reaches the same provider (`104` §17.13 ruling 3) and, since `00`
    amendment 7(c), so does site G for a file the gate cleared -- so `len(socket)`
    is no longer a fact-pass number.
    """
    return sum(1 for prompt in socket
               if dossier_in(prompt).get("call_site") == call_site)


#: Every purse but the fact pass's, by the suffix `cli` appends to the fact
#: budget's own `scan_id` to make it (`cli.OBSERVE_BUDGET_SUFFIX` and its four
#: neighbours). Read off `cli` rather than spelled, so a sixth purse is a name this
#: file already knows.
OTHER_PURSE_SUFFIXES = (cli.OBSERVE_BUDGET_SUFFIX, cli.SITUATION_BUDGET_SUFFIX,
                        cli.TEMPLATE_BUDGET_SUFFIX, cli.GATE_BUDGET_SUFFIX)


def _fact_reservations(corpus) -> list[dict]:
    """The slots reserved from the FACT PASS's purse, and no other site's.

    A reservation names its purse through its `scan_id`: `cli` mints every other
    ledger as the fact budget's id plus a word -- `:gate`, `:situation`,
    `:observe`, `:template` -- so the fact pass's is the bare id. Before amendment
    7(c) this corpus filled one purse and the read needed no clause.
    """
    return [row for row in _rows(
        corpus, "SELECT scan_id, estimated_cost, actual_cost, status "
                "FROM llm_budget_reservation")
            if not row["scan_id"].endswith(OTHER_PURSE_SUFFIXES)]


# --- the wire -------------------------------------------------------------------


def test_one_row_per_answered_call_carrying_what_the_provider_reported(
        corpus, socket):
    """ONE ROW PER ANSWERED CALL AT SITE A, and the corpus is one file.

    `len(socket)` was site A's total when R-14 was wired and is now every cloud
    site's, so both halves of the count are taken at the site (`_usage_at`,
    `_cloud_calls_at`). The gate's answered call leaves a usage row too -- over the
    local transport, whose own token counts are pinned in
    `test_local_model_fact_pass` -- and it is stated on its own line rather than
    folded into a number this pin reads as site A's.
    """
    _run(corpus, "--enable-cloud")

    rows = _usage_at(corpus, cli.A_FACT)
    assert len(rows) == _cloud_calls_at(socket, cli.A_FACT) == 1
    # The gate answered too, and its usage reached a row of its own. Without this
    # line site A's `1` would be indistinguishable from a run in which the gate was
    # the only site the wire recorded anything for.
    assert len(_usage_at(corpus, cli.H_RESTRICTED_KIND)) == 1
    row = rows[0]
    assert row["prompt_tokens"] == PROMPT_TOKENS
    assert row["completion_tokens"] == 120
    assert row["prompt_cache_hit_tokens"] == CACHE_HIT
    assert row["prompt_cache_miss_tokens"] == CACHE_MISS
    assert row["model_id"] == "a-logician"
    assert row["response_format"] == "json_object"


def test_the_row_joins_to_the_dossier_and_the_release_it_describes(corpus, socket):
    """A usage row nothing can join is a number with no call attached to it.

    Site A's row (`_usage_at`): a `[0]` off the whole table is whichever of the four
    sites' rows the rowid gave, and this pin is about the fact pass's.
    """
    _run(corpus, "--enable-cloud")

    usage = _usage_at(corpus, cli.A_FACT)[0]
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
    changing what the budget enforces.

    THE FACT PASS'S PURSE, `_fact_reservations`. `00` amendment 7(c) and the two
    rulings before it gave the gate, site G, site C and site E ledgers of their own
    -- `cli` mints each as the fact budget's `scan_id` plus a word, because a shared
    purse starved site C (`104` R-131) -- so a read of the whole table is four
    purses and `[0]` is whichever of them came first."""
    _run(corpus, "--enable-cloud")

    usage = _usage_at(corpus, cli.A_FACT)[0]
    settled = _fact_reservations(corpus)

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

    # Site A's rows (`_usage_at`): the silence is the CLOUD provider's, and the gate
    # answered over the local transport, which reports its tokens as usual.
    rows = _usage_at(corpus, cli.A_FACT)
    assert len(rows) == 1
    assert rows[0]["prompt_tokens"] is None
    assert rows[0]["reserved_cost"] == format(cli.FACT_CALL_COST, "f")


def test_a_second_run_reuses_and_therefore_records_no_new_usage(corpus, socket):
    """R-13 and R-14 meet: a call not made consumes nothing and is not billed for
    nothing either.

    All three counts at site A. Site C repeats itself on every run because it
    records no identity to reuse, and site G does the same -- so `len(socket)` and
    the whole of `llm_call_usage` both grow on the second run for reasons that have
    nothing to do with whether the fact pass bought its answer twice.
    """
    _run(corpus, "--enable-cloud")
    _run(corpus)

    assert _cloud_calls_at(socket, cli.A_FACT) == 1
    assert len(_usage_at(corpus, cli.A_FACT)) == 1
    assert len(_rows(corpus, "SELECT * FROM llm_call_reuse WHERE call_site = ?",
                     cli.A_FACT)) == 1


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

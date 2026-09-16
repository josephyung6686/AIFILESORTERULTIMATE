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

**Everything here is real except the two model seams**, exactly as in
`test_a_fact_call_cache.py`: `readers.model_routing.deepseek_invoke` is the documented
deployment seam, and the gate, the release ledger, the transport, the validator,
`apply_verdict` and the whole of `cli.run` are the production path. Counting `invoke`
calls counts model calls exactly -- but it counts EVERY site's, and since `104`
§17.13 ruling 3 and R-170 that is no longer site A's alone. Every count below is
taken at one call site, and the argument for that is in `_Socket`.

**AND A LOCAL MODEL IS NOW PART OF THE DEPLOYMENT, `00` amendment 7(c).** This file
configured a cloud key and nothing else, and that stopped being a deployment site A
can run in: the gate, `cli.ask_the_gate`, reads every un-held file on this device
BEFORE anything about it may be sent, `cli.CLOUD_CLEARING_BASES` is what
`model_route_permitted` asks for a cloud target, and the rules' own word is no
longer among them. With no local model the gate has no destination, no file is
cleared, and site A is refused the cloud for every one of them -- measured here as
`calls_at(A_FACT) == 0` where these pins say 2. So the local half is `StubOllama`,
`test_local_model_fact_pass`'s own server, answering the gate `none_of_these` and
DECLINING the situation; `test_the_scoreboard_reuses_a_prior_runs_answers` carries
the long form of why G is declined rather than answered. Both seams are stubs;
neither is the thing under test.

**AND THE GATE RECORDS AN IDENTITY AND REUSES IT** (45d36ca0), which is what moved
the numbers in this file. `llm_call_identity` and `llm_call_reuse` were site A's
alone the day R-109 was written -- site C and site G record none -- so the reads
here carried no call-site clause and said so in their own docstrings. They are two
sites' now: an unscoped `llm_call_reuse` reads 2 where a pin says 0 because THE GATE
saved, with site A having reused nothing at all. Every one of them is scoped through
`_reuses_at` and `_identities_at`, and the gate's own saving is stated where a pin
rests on it rather than folded into site A's number.
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
from facts.states import EXCLUDED_STATE, LLM_SUPPORTED, is_stronger  # noqa: E402
from privacy.gate import Gate  # noqa: E402
from privacy.resolve import UnresolvableSpan  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
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

    **COUNTED PER CALL SITE, `104` §17.13 ruling 3 and R-170.** When R-109 was
    written this corpus produced one model call per file and nothing else, so a
    bare `len(self)` was a site-A total. §17.13 moved site C's `eliminate-v2` from
    `ratified_local` to `ratified` and R-170 made the route a per-FILE question, so
    a run now also sends a `C_placement` dossier for each file P11 proposes a folder
    for -- through this same stubbed `deepseek_invoke`, on the cloud run and on the
    plain one alike, because the route decides WHERE a call goes and not WHETHER
    there is one.

    R-109 is about the reuse of ANSWERS, and the thing a reuse is looked up by is an
    identity: `llm_call_identity` is written at site A and site C records none, so
    there is nothing of C's for `_reuse_is_current` to find and C repeats itself on
    every run by construction. Folding C into the totals would report this file's
    own defect -- a second run buying answers it already had -- when what moved was a
    site that was never given one. So every pin states site A's reuse at
    `calls_at(A_FACT)` and site C's repetition on its own line: a placement that
    starts reusing, or stops calling, turns a line red instead of quietly moving a
    number the assertion above it reads as site A's.
    """

    def __init__(self, answer=None) -> None:
        self.payloads: list[bytes] = []
        self._answer = answer or self.reject_everything

    def __len__(self) -> int:
        return len(self.payloads)

    def calls_at(self, call_site: str) -> int:
        """How many calls this run made at ONE site."""
        return sum(1 for payload in self.payloads
                   if self._body(payload)["call_site"] == call_site)

    def subjects_at(self, call_site: str) -> list[str]:
        return [self._body(payload)["subject_ref"] for payload in self.payloads
                if self._body(payload)["call_site"] == call_site]

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
            body = self._body(payload)
            # SITE G ARRIVES HERE TOO since `00` amendment 7(c): G's row is
            # `ratified` and a file the gate CLEARED may have its situation asked
            # off the device, so the cloud seam sees a situation dossier whose
            # schema is not site A's. `reject_everything` and `accept_the_work_type`
            # both answer in site A's shape, which at site G is a malformed claim
            # the validator refuses -- the same silence, reached by a fault -- so it
            # is declined in the shape the ratified prompt asks for and the gate's
            # clearance stands as this file's route.
            if body["call_site"] == cli.G_SITUATION_SENSITIVITY:
                return _decline(body).encode("utf-8")
            return self._answer(body)
        return invoke


@pytest.fixture()
def socket(monkeypatch):
    recorder = _Socket()
    monkeypatch.setattr(model_routing, "deepseek_invoke", recorder.factory)
    return recorder


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own key must not decide whether these tests pass.

    The local model's two names are cleared for the same reason and it is not a
    formality: a machine with ollama running would answer the gate with whatever it
    pulled, and these counts would then depend on a model nobody chose here.
    `_local_model` puts the stub's own names back.
    """
    for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                 LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
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
    server for the test rather than one per run -- every test here runs the product
    twice over one corpus, and a stub that came and went between them would give the
    second run a different base URL from the first.
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


def _count(corpus, table) -> int:
    return _rows(corpus, f"SELECT count(*) AS n FROM {table}")[0]["n"]


def _outcomes(corpus) -> list[str]:
    """The standing verdicts of the pass this file is about, and no other site's.

    `llm_verdict` holds every site's judgements, and since `104` §17.13 ruling 3 a
    run of this corpus writes `C_placement` verdicts beside site A's. An unscoped
    read would let a placement's outcome decide whether the fact pass rejected --
    and `accept_the_work_type`, which answers by the FILENAME's reading, says
    nothing about what a placement dossier asks. Joined on `llm_dossier.call_site`,
    which is the record of which site asked.
    """
    return [row["outcome"] for row in _rows(
        corpus,
        "SELECT v.outcome AS outcome FROM llm_verdict v "
        "JOIN llm_dossier d ON d.dossier_id = v.dossier_id "
        "WHERE v.superseded_by IS NULL AND d.call_site = ?", cli.A_FACT)]


#: Every purse but the fact pass's, by the suffix `cli` appends to the fact
#: budget's own `scan_id` to make it. Read off `cli` and not spelled here: a sixth
#: purse added without a line in this tuple would be a purse `_purse_of` could not
#: name, and `_every_reservation_is_in_a_known_purse` is what turns that into a red
#: line rather than into a reservation this file quietly stops counting.
OTHER_PURSE_SUFFIXES = (cli.OBSERVE_BUDGET_SUFFIX, cli.SITUATION_BUDGET_SUFFIX,
                        cli.TEMPLATE_BUDGET_SUFFIX, cli.GATE_BUDGET_SUFFIX)


def _reservations_in(corpus, suffix: str | None) -> int:
    """The slots reserved from ONE purse: the fact pass's when `suffix` is `None`.

    **A RESERVATION DOES NAME ITS SITE, through the `scan_id` the purse was built
    with.** This file used to say it did not, and that was true of the column and
    not of the value: `cli` mints every other ledger as `fact_budget.scan_id + <a
    suffix>` -- `:observe`, `:situation`, `:template`, `:gate` -- so the fact pass's
    purse is the bare scan id and each of the others is that id plus its own word.
    The separation exists because a shared purse starved site C (`104` R-131), and
    what it gives this file is the fourth ledger scoped like the other three.
    """
    rows = _rows(corpus, "SELECT scan_id FROM llm_budget_reservation")
    if suffix is None:
        return sum(1 for row in rows
                   if not row["scan_id"].endswith(OTHER_PURSE_SUFFIXES))
    return sum(1 for row in rows if row["scan_id"].endswith(suffix))


def _spend_at(corpus, call_site, purse) -> dict[str, int]:
    """The four ledgers ONE site filled, and no other site's.

    `104` R-109's "nothing after this line is free" is a claim about one site, and
    all four ledgers it is claimed on can be read at the site that filled them:
    `llm_dossier` carries `call_site` itself, `llm_response` and the
    `release_ledger` reach it through the dossier a response was written for, and
    the reservation reaches it through its purse (`_reservations_in`). A release is
    counted through the response because a minted release only becomes a spent one
    when the transport was reached, which is the thing R-109 says a reuse must not
    do.
    """
    at_site = ("FROM llm_response r JOIN llm_dossier d "
               "ON d.dossier_id = r.dossier_id WHERE d.call_site = ?")
    return {
        "llm_budget_reservation": _reservations_in(corpus, purse),
        "llm_dossier": _rows(
            corpus, "SELECT count(*) AS n FROM llm_dossier WHERE call_site = ?",
            call_site)[0]["n"],
        "llm_response": _rows(
            corpus, f"SELECT count(*) AS n {at_site}", call_site)[0]["n"],
        "release_ledger": _rows(
            corpus, f"SELECT count(DISTINCT r.release_id) AS n {at_site}",
            call_site)[0]["n"],
    }


def _a_fact_spend(corpus) -> dict[str, int]:
    """What site A bought, out of its own purse."""
    return _spend_at(corpus, cli.A_FACT, None)


def _gate_spend(corpus) -> dict[str, int]:
    """What the gate bought, out of the purse `00` amendment 7(c) gave it."""
    return _spend_at(corpus, cli.H_RESTRICTED_KIND, cli.GATE_BUDGET_SUFFIX)


def _rule_settled(corpus) -> dict[str, set[str]]:
    """Per file, the fields a fact STRONGER than an LLM conclusion holds.

    `104` §18.2 gap 1's half of the question, read with the product's own predicate
    rather than a list of state names copied into a test: `model_facts
    ._rule_settled_field_keys` is `is_stronger(state, LLM_SUPPORTED)` over the file's
    active facts, and a state promoted above `llm_supported` tomorrow has to move
    this test with it or the two disagree about the same file.

    Scoped to the file's CURRENT content hash for the same reason `facts_for_file`
    is: a fact is an answer about one version of the bytes, and a rewrite makes it
    somebody else's.
    """
    settled: dict[str, set[str]] = {}
    for row in _rows(corpus,
                     "SELECT f.file_id AS file_id, f.field_key AS field_key, "
                     "f.reliability_state AS reliability_state FROM file_facts f "
                     "JOIN files x ON x.file_id = f.file_id "
                     "AND x.content_hash = f.content_hash WHERE f.active = 1"):
        if (row["reliability_state"] != EXCLUDED_STATE
                and is_stronger(row["reliability_state"], LLM_SUPPORTED)):
            settled.setdefault(row["file_id"], set()).add(row["field_key"])
    return settled


def _identities_at(corpus, call_site) -> list[dict]:
    """The answers ONE site recorded an identity for, and no other site's.

    `llm_call_identity` was site A's alone the day R-109 was written, which is why
    the reads in this file carried no clause and said so. Since `00` amendment 7(c)
    the gate records one per file too, so an unscoped count reads two sites' answers
    as site A's. Site C and site G record none and are in neither number.
    """
    return _rows(
        corpus,
        "SELECT i.* FROM llm_call_identity i JOIN llm_dossier d ON "
        "d.dossier_id = i.dossier_id WHERE d.call_site = ?", call_site)


def _reuses_at(corpus, call_site) -> list[dict]:
    """Questions this run did not ask again AT ONE SITE.

    `llm_call_reuse` carries its own `call_site` and is every site's savings in one
    table. That is exactly why a count of the whole table cannot stand in for site
    A's: the gate saves on the same files (45d36ca0), so the number moves when a
    second site starts reusing with site A having reused nothing at all -- which is
    the shape of the defect R-109 IS.
    """
    return _rows(corpus, "SELECT * FROM llm_call_reuse WHERE call_site = ?",
                 call_site)


def _a_fact_failures(corpus) -> int:
    """The calls that reached the transport and got no answer, at site A alone.

    Same join and the same reason as `_a_fact_spend`: a provider that hangs up
    hangs up on every site it is asked from, so an unscoped count of
    `llm_call_failure` would answer for the placement too.
    """
    return _rows(
        corpus,
        "SELECT count(*) AS n FROM llm_call_failure f "
        "JOIN llm_dossier d ON d.dossier_id = f.dossier_id "
        "WHERE d.call_site = ?", cli.A_FACT)[0]["n"]


# --- the defect itself ------------------------------------------------------------


def test_a_rejected_answer_is_not_bought_a_second_time(corpus, socket):
    """R-109 in one number. Measured before the fix: 2 calls, then 2 more.

    The number is site A's, per `_Socket`. Site C's placement is asked on both runs
    and is stated on its own line below.
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)
    assert first == len(CORPUS), socket.subjects_at(cli.A_FACT)
    assert set(_outcomes(corpus)) == {"reject"}, _outcomes(corpus)

    _run(corpus)

    assert socket.calls_at(cli.A_FACT) == first, (
        f"the second run re-asked {socket.calls_at(cli.A_FACT) - first} questions "
        f"whose answers were already on disk: "
        f"{socket.subjects_at(cli.A_FACT)[first:]}")
    # Site C's own line. C records no `llm_call_identity`, so it has no prior answer
    # to be found and repeats what it did on run 1. If it ever stops, the line above
    # keeps its meaning and this one says the corpus changed under it.
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    # SITE A'S SAVINGS AND SITE A'S PRIORS (`_reuses_at`, `_identities_at`). Both
    # tables were site A's alone when this pin was written; since `00` amendment
    # 7(c) the gate is in them too, so unscoped these read 4 on a two-file corpus --
    # and would go on reading 4 with site A re-buying every answer, which is R-109
    # itself passing this pin.
    reuses = _reuses_at(corpus, cli.A_FACT)
    assert len(reuses) == first
    priors = {row["dossier_id"] for row in _identities_at(corpus, cli.A_FACT)}
    for reuse in reuses:
        assert reuse["prior_dossier_id"] in priors
        assert json.loads(reuse["reused_fields"])
    # THE GATE SAVED TOO, on `_Socket`'s standing rule that a site whose behaviour
    # these numbers rest on gets a line of its own rather than being folded in: the
    # gate is asked once per file in front of site A, and a second run that re-asked
    # it would pay for the whole roster again on this machine while every number
    # above still read right.
    assert len(_reuses_at(corpus, cli.H_RESTRICTED_KIND)) == len(CORPUS)


def test_a_reused_question_spends_no_slot_no_release_and_no_call(corpus, socket):
    """"Nothing after this line is free": the reuse is read before the budget slot
    is reserved, before the gate mints a release and before the transport sends.

    Read at the site, `104` §17.13 ruling 3, and ALL FOUR LEDGERS ARE NOW READ THERE
    (`_spend_at`). This pin used to say the budget slot could not be scoped and
    bounded it by the whole table instead, accounting for the growth as site C's.
    That accounting broke on `00` amendment 7(c) for a reason that was never about
    site A: site G records no identity either, so a second run buys ITS calls again
    as well and the whole-table growth is two repeating sites' and not one's.

    The repair is not a bigger accounting but the scoping the fourth ledger turns
    out to allow. `cli` mints every other purse as the fact budget's own `scan_id`
    plus a word -- `:gate`, `:situation`, `:observe`, `:template` -- so a
    reservation names its purse and the fact pass's is the bare id
    (`_reservations_in`). Site A's freeze is therefore stated on all four ledgers
    directly, which is what the accounting was standing in for.

    **AND THE GATE IS FROZEN BESIDE IT, which is a claim this pin could not make
    before.** The gate holds an answer per file and reuses it (45d36ca0), so it is
    the second site R-109's sentence is now true of -- and a gate that re-asked
    would spend the whole roster again on this machine, out of its own purse, with
    every site-A number here still reading right.

    `_every_reservation_is_in_a_known_purse` is what keeps the bare-id read a
    partition rather than a filter: a sixth purse would otherwise be slots this pin
    silently stopped counting.
    """
    _run(corpus, "--enable-cloud")
    spent = _a_fact_spend(corpus)
    gate = _gate_spend(corpus)
    placements = socket.calls_at(cli.C_PLACEMENT)

    _run(corpus)

    assert _a_fact_spend(corpus) == spent
    assert _gate_spend(corpus) == gate
    # Site C's own line, unchanged in meaning: it holds no identity, so it repeats
    # itself and the freezes above are freezes in a run that did buy things.
    assert socket.calls_at(cli.C_PLACEMENT) - placements == placements, (
        "site C is no longer asked once per run and the freezes above are "
        "measuring a run that bought nothing at all")


def test_every_reservation_is_in_a_known_purse(corpus, socket):
    """The partition `_reservations_in` rests on, asserted rather than assumed.

    Site A's purse is READ AS THE ABSENCE OF A SUFFIX, so a purse nobody listed
    would be counted as the fact pass's and a slot it bought would land in site A's
    freeze above -- which is the one number this file exists to protect. Every
    `scan_id` is therefore either the bare scan id or that id plus one of `cli`'s
    own suffixes, and the suffixes are read off `cli` and not spelled here.

    SABOTAGE: add a sixth purse in `cli` without adding it to
    `OTHER_PURSE_SUFFIXES`, and this goes red on the first run that spends from it.
    """
    _run(corpus, "--enable-cloud")

    scan_ids = {row["scan_id"] for row in
                _rows(corpus, "SELECT scan_id FROM llm_budget_reservation")}
    assert scan_ids
    bare = {scan_id for scan_id in scan_ids
            if not scan_id.endswith(OTHER_PURSE_SUFFIXES)}
    assert len(bare) == 1, bare
    the_scan = bare.pop()
    assert scan_ids - {the_scan} == {
        the_scan + suffix for suffix in OTHER_PURSE_SUFFIXES
        if the_scan + suffix in scan_ids}
    # And the fact pass and the gate both spent from theirs, so the two freezes in
    # the pin above are freezes of purses this corpus actually reaches.
    assert _reservations_in(corpus, None) == len(CORPUS)
    assert _reservations_in(corpus, cli.GATE_BUDGET_SUFFIX) == len(CORPUS)


def test_a_partly_accepted_answer_is_reused_for_what_is_still_open(corpus, socket):
    """One field accepted and settled, the rest rejected and still open.

    The second run's question is SMALLER than the first's -- which is exactly why
    the asked field set cannot be a dimension of the identity, as `call_identity`
    says -- and every field still in it already has an answer.

    **WHAT "SETTLED" MEANS HERE MOVED, and this pin's reason moved with it (`104`
    §18.2 gap 1).** It used to read `reused_fields` as "the fields still open" and
    assert the accepted one was gone from every row. `open_question` now asks
    `pending ∪ settled`: a field a RULE already answered is re-offered on every run
    so the model can flag the disagreement `rule_conflicts` builds check 4's
    `existing_facts` for, and gap 1 exists precisely because a rule deciding a level
    behind the model's back was the thing r15 measured.

    So the accepted field leaves the question only where the acceptance is the
    STRONGEST thing holding it. On this corpus that splits the two files: the rule
    stage answers `work_type` for one of them from the filename it shares with the
    model's own citation, and does not for the other. The pin now says the split
    itself -- `work_type` is in a reuse row exactly when a rule holds it -- which is
    the original claim (a field the model settled is not asked again) plus the
    reason it does not hold for a rule-settled field, and it fails if either half
    stops being true. A field held only by the model's `llm_supported` answer is in
    NEITHER half, which is `00`:298's *"proposed once"*.
    """
    socket._answer = socket.accept_the_work_type
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)
    outcomes = _outcomes(corpus)
    assert "accept_direct" in outcomes and "reject" in outcomes, outcomes
    facts = _count(corpus, "file_facts")

    _run(corpus)

    assert socket.calls_at(cli.A_FACT) == first, \
        socket.subjects_at(cli.A_FACT)[first:]
    # Site C's own line, and it moves with the facts: an accepted `work_type` is
    # what P11 proposes a folder from, so this corpus asks more placements here than
    # the rejecting pins do. Its repetition, not its size, is what the count above
    # depends on.
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    # Site A's savings (`_reuses_at`): the gate saved on the same two files.
    reuses = _reuses_at(corpus, cli.A_FACT)
    assert len(reuses) == first
    # A reuse covers the WHOLE question the second run would have asked, and the
    # accepted field is in that question exactly where a rule -- not the model --
    # holds it. Both sides of the split are asserted below, so a corpus that stopped
    # producing one of them fails here rather than passing on the other's strength.
    rule_settled = _rule_settled(corpus)
    carried = {}
    for reuse in reuses:
        subject = reuse["subject_ref"]
        fields = json.loads(reuse["reused_fields"])
        carried[subject] = "work_type" in fields
        assert carried[subject] == (
            "work_type" in rule_settled.get(subject, set())), (
            f"{subject} reused {sorted(fields)} with a rule holding "
            f"{sorted(rule_settled.get(subject, set()))}")
    assert set(carried.values()) == {True, False}, carried
    assert _count(corpus, "file_facts") == facts, "a reuse writes no new fact"


def test_the_identity_is_the_same_on_an_unchanged_second_run(corpus, socket):
    """The other half of the diagnosis: the key did not move, the comparison did.

    Two runs of one checkout over unchanged files produce one `identity_id` per
    file. If a dimension ever starts carrying a run id, a timestamp or a path, this
    is the test that says so -- R-109 would come back as "the cache never hits" and
    look exactly like the defect this file is about. `104` R-172a is that failure
    happening: §18.7's standing consent grant was scoped to a fresh-per-run
    `scan_run_id` and `policy` is one of `CALL_IDENTITY_DIMENSIONS`.

    SITE A'S ROWS (`_identities_at`). `llm_call_identity` is written where an answer
    can be reused from -- site C and site G record none -- and that made it site A's
    alone until `00` amendment 7(c) gave the gate one per file as well. Unscoped, the
    count reads 4 for the 2 this pin means, and the dimension set below would be
    asserted of a row whose `model_id` is the local model's and whose `call_site` is
    not site A's.

    `104` §18.60, 13 Sep 2026: `max_dossier_tokens` is the eleventh term
    (`llm_harness.store.CALL_IDENTITY_DIMENSIONS`). The gate's ceiling moved from
    1,200 bytes to 3,000 without the per-file identity naming HOW MUCH of each
    reading was shown, only WHICH readings (`context_refs`) -- so 238 of 320 gated
    files kept the answer given under the old, tighter excerpt. The dimension's own
    empty value is `None`, so every identity written before this term existed is
    asked once more under its true bound rather than silently trusting a cache built
    on a ceiling it never recorded.
    """
    _run(corpus, "--enable-cloud")
    _run(corpus)

    identities = {row["identity_id"] for row in _identities_at(corpus, cli.A_FACT)}
    assert len(identities) == 2
    dimensions = [json.loads(row["dimensions"])
                  for row in _identities_at(corpus, cli.A_FACT)]
    assert {name for row in dimensions for name in row} == {
        "call_site", "content_hash", "context_refs", "extractor_versions",
        "max_dossier_tokens", "model_id", "plan_version", "policy",
        "prompt_fingerprint", "sampling", "schema_id", "subject_ref"}
    # `context_refs` is `104` R-135's tenth term: the observation keys of readings of
    # OTHER files a call was shown. It is exactly the shape this test's docstring warns
    # about, so it is checked rather than trusted. An `observation_key` is
    # `sha256(content_hash, extractor_name, locator, raw_value)` -- content, and no run
    # id, no file id, no timestamp and no path -- so it is stable across runs and
    # across databases over the same bytes, which is what `104` R-123's
    # `--reuse-answers-from` needs. `is_observation_key` is P4's own shape test, asked
    # here rather than restated.
    from evidence_shape.observation import is_observation_key

    for row in dimensions:
        assert isinstance(row["context_refs"], list)
        assert all(is_observation_key(ref) for ref in row["context_refs"])


# --- what a reuse must NOT swallow ------------------------------------------------


def test_a_call_that_failed_is_asked_again(corpus, socket, monkeypatch):
    """A provider that hangs up is not an answer. `CallFailed` is not a `P8Verdict`,
    so no identity is recorded and the next run asks -- which is the whole point of
    the exclusion: a transient failure must not become a permanent silence about
    the file.

    A provider that hangs up hangs up on every site it is asked from, so both the
    calls and the failure rows are read at site A (`104` §17.13 ruling 3): C's
    placement fails alongside and is stated on its own line.
    """
    def _hang_up(**_unused):
        def invoke(payload: bytes) -> bytes:
            socket.payloads.append(payload)
            raise ConnectionError("the provider hung up")
        return invoke

    monkeypatch.setattr(model_routing, "deepseek_invoke", _hang_up)
    _run(corpus, "--enable-cloud")
    failed = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)
    assert failed == len(CORPUS)
    assert _a_fact_failures(corpus) == len(CORPUS)
    # SITE A'S IDENTITIES. The gate is local and its calls did not hang up, so it
    # answered and recorded one per file (`00` amendment 7(c)); an unscoped zero
    # would now be asserting that the gate failed too, which is not what was
    # sabotaged and not what R-109 is about.
    assert _identities_at(corpus, cli.A_FACT) == []

    monkeypatch.setattr(model_routing, "deepseek_invoke", socket.factory)
    _run(corpus)

    assert socket.calls_at(cli.A_FACT) - failed == len(CORPUS), \
        "a failed call was remembered as an answer"
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    assert _reuses_at(corpus, cli.A_FACT) == []
    # And the gate DID save, which is what makes the line above site A's own zero
    # rather than a run in which nothing was reusable: the gate answered on run 1
    # and reused on run 2 over the same unchanged files.
    assert len(_reuses_at(corpus, cli.H_RESTRICTED_KIND)) == len(CORPUS)


def test_a_call_the_gate_refused_is_asked_again(corpus, socket, monkeypatch):
    """`104` R-O's outcome, and the same exclusion. A refusal is recorded, the run
    goes on, and nothing about it says the question was answered.

    The refusal is total -- the gate is the door every site goes through -- so the
    first run's `len(socket) == 0` is every site's zero and needs no scoping. The
    second run's count does: it is site A that must ask again, and site C, which
    never had an answer to remember, is stated separately. C's repetition cannot be
    read off the first run here (it made no calls either), so what is asserted is
    that C did ask and that R-O's exclusion holds at BOTH sites -- no reuse row
    anywhere.
    """
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

    assert socket.calls_at(cli.A_FACT) == len(CORPUS), \
        "a refusal was remembered as an answer"
    assert socket.calls_at(cli.C_PLACEMENT), (
        "site C stopped calling and the count above is measuring something other "
        "than the fact pass")
    assert _count(corpus, "llm_call_reuse") == 0


# --- and what is a different question ---------------------------------------------


def test_changing_one_files_content_re_asks_that_file_alone(corpus, socket):
    """A rewrite is a new file version and a new identity; the other file's answer
    is untouched.

    One call at site A, per `_Socket` -- and site C's placement is asked for both
    files again either way, which is exactly the repetition that would have been
    read as the untouched file being re-asked.
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)

    (corpus / "reading notes.txt").write_text(
        "Rewritten notes for this seminar. The lecture now covers rotational "
        "motion, and the problem set is due the following Tuesday.\n")
    _run(corpus)

    assert socket.calls_at(cli.A_FACT) - first == 1, \
        socket.subjects_at(cli.A_FACT)[first:]
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    # Site A's own saving (`_reuses_at`): the gate saves on the same untouched file
    # and in the same table, so the whole table reads 2 where site A saved once.
    assert len(_reuses_at(corpus, cli.A_FACT)) == 1


def test_changing_only_the_prompt_re_asks_every_file(corpus, socket, monkeypatch):
    """`00`:44 wants "model or prompt changes auditable", and a rejected answer is
    no more durable across a prompt change than an accepted one.

    Only `template_id` moves, so the ratified bytes and their digest are untouched
    and nothing changes but the fingerprint -- the dimension under test.

    It is site A's prompt that moves, so it is site A's calls that are counted
    (`104` §17.13 ruling 3). Site C's placement carries its own prompt, untouched
    here, and asks again regardless -- which is precisely why a total would have
    said "every file re-asked" for two different reasons at once.
    """
    _run(corpus, "--enable-cloud")
    first = socket.calls_at(cli.A_FACT)
    placements = socket.calls_at(cli.C_PLACEMENT)

    real = cli.a_fact_prompt()
    monkeypatch.setattr(cli, "a_fact_prompt", lambda: dataclasses.replace(
        real, template_id=f"{real.template_id}.a-second-revision"))
    _run(corpus)

    assert socket.calls_at(cli.A_FACT) - first == len(CORPUS)
    assert socket.calls_at(cli.C_PLACEMENT) == placements * 2, (
        "site C is no longer asked once per run and the count above is measuring "
        "something other than the fact pass")
    # SITE A SAVED NOTHING, which is the claim; the gate saved everything, because
    # site A's prompt is not the gate's and a revision of one is no reason to re-ask
    # the other. An unscoped zero here would have gone red for that, and the two
    # facts are worth different lines.
    assert _reuses_at(corpus, cli.A_FACT) == []
    assert len(_reuses_at(corpus, cli.H_RESTRICTED_KIND)) == len(CORPUS)

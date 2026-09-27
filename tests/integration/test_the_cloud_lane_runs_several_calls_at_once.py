# tests/integration/test_the_cloud_lane_runs_several_calls_at_once.py
"""`104` §18.15: the cloud lane holds several round trips at once; local stays one.

The owner's direction, 9 September 2026 and again on the 10th: *"use the cloud in
PARALLEL -- the cloud sites A and C carry no serial limit, so the scoreboard runs
them with more workers while the local lane (G, and A/C for unclassified and
protected files) stays serial"*. **Measured on r19 (§18.22): 223 dossiers in nine
hours, site A's cloud share 47%, and every call -- cloud or local -- one after
another.** The lane is what that measurement asks for.

**What is under test is the ORDER OF WORK, not the speed.** A wall-clock assertion
would measure this machine; these assertions measure which thread did what and in
what order, which is the thing that can be wrong. Five properties, one per test:

1. Every cloud call of one batch is on the wire at the same moment. The stub blocks
   each arrival until the lane is as wide as `cli.CLOUD_CALLS_AT_ONCE`, so a pass
   that sent them one at a time cannot finish the batch and says so.
2. The gate is asked for every call in a batch BEFORE the first of them is queued.
   Rule three of the build: nothing about the privacy decision moved, and the
   release is still minted on the calling thread, before any bytes exist to send.
3. Rows are written in the order the files were WALKED even when the provider
   answers in the reverse order. The stub hands the answers back last-arrived-first
   and the `llm_response` rows still come out in roster order.
4. One call that does not come back records its own `llm_call_failure` row and the
   other six in the batch complete. §8's rule and `104` R-O's, unchanged by the
   lane: a failed call is a row, not the end of a run.
5. A LOCAL send is never beside anything -- not another local send, and not a cloud
   one. One Ollama server holds one model in memory, and a second concurrent local
   call is what filled the machine's swap in r18 (§17.21). That property lives in
   the driver, so it is pinned at the driver, over both localities at once.

**Everything here is real except the two model seams.** `readers.model_routing.
deepseek_invoke` is the documented deployment seam and the stub is bound in its
place, exactly as `tests/integration/test_a_fact_call_cache.py` binds it, so the
route, the gate, the release ledger, the transport, the validator and the whole of
`cli.run` are the production path. The stub is the only thing that knows a thread
from another one.

**AND A LOCAL MODEL IS NOW PART OF THE DEPLOYMENT, `00` amendment 7(c).** This file
configured a cloud key and nothing else, and that stopped being a deployment a
CLOUD LANE can exist in: the gate, `cli.ask_the_gate`, reads every un-held file on
this device BEFORE anything about it may be sent, `cli.CLOUD_CLEARING_BASES` is
what `model_route_permitted` asks for a cloud target, and the rules' own word is no
longer among them. With no local model nothing is cleared, every file is routed
local, and the widest lane a run can open is one -- measured as `at_once` and
`calls_at(A_FACT)` reading 0 where these pins say seven. The local half is
`StubOllama`, `test_local_model_fact_pass`'s own server, answering the gate
`none_of_these` and DECLINING the situation, for the reasons
`test_the_scoreboard_reuses_a_prior_runs_answers` states at length.

**THE LOCAL LANE IS STILL ONE WIDE AND THE GATE IS PART OF IT**, which is the point
worth keeping in view here of all files: the gate is a per-file LOCAL loop in front
of the batch, so seven files are seven serial local calls and then one cloud batch
of seven. That is `104` §18.15's own shape -- the local lane serial, the cloud lane
as wide as `cli.CLOUD_CALLS_AT_ONCE` -- and the width measured below is the cloud
half of it.
"""
from __future__ import annotations

import io
import json
import sqlite3
import threading

import pytest

import cli
from llm_harness.harness import CallLane, in_walk_order
from llm_harness.transport import SendResult
from model_facts import PerFileCeiling
from privacy import gate as gate_module
from privacy.vocabulary import CLOUD_LOCALITY
from readers import model_routing
from readers.model_routing import MODEL_NAME_OF_TIER
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME
#: P7 names the cloud half of `LOCALITIES` and leaves the other half to whoever
#: claims it, so the local word is read off the transport that can honestly claim
#: it -- `tests/integration/test_per_file_model_route.py` reads it from the same
#: place and for the same reason.
from readers.model_ollama import LOCAL as LOCAL_LOCALITY
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
# The two local sites' answers come from the files that own them, imported rather
# than copied on `test_site_e_reuses_its_answer`'s own rule: one stub speaking one
# protocol, so this file and the gate's own pins cannot drift into describing two
# different gates. `_decline` is renamed on the way in because `_Lane` already has
# a `_decline` of its own, and the two are different declines.
from test_local_model_fact_pass import (
    MODEL_ID, StubOllama, _answer_for, dossier_in,
)
from test_site_g_end_to_end import _decline as _decline_the_situation
from test_site_h_gate import _clear

SITUATION = "academic.coursework"

#: HOW LONG A CALL WAITS FOR THE REST OF ITS BATCH BEFORE GIVING UP. The stubs
#: block on a predicate rather than on a `threading.Barrier` so that a lane that
#: never opens FAILS an assertion instead of hanging a suite: every waiter times
#: out, the run finishes, and the high-water mark says what really happened.
PATIENCE = 30.0

#: The distinctive word in the one file whose call is made to fail, and it is a
#: word rather than a file id because the stub sees bytes and not a roster. It is
#: in the file's own body, so it is in the released evidence of that file's dossier
#: and of no other's.
FAILING_WORD = "quicksilver"

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}

#: The dossier is appended to the ratified template and this is the template's own
#: last sentence, so the JSON half is whatever follows it. Same locator, same
#: reason, as `tests/integration/test_local_model_fact_pass.py`.
DOSSIER_FOLLOWS = "The dossier follows."


#: One ordinary file per cloud call the run may hold open, and no more, so a
#: full batch is exactly the corpus: what the lane can hold and what the pass
#: has to send are the same number, and the high-water mark below is an
#: equality rather than an inequality.
WEEKS = tuple(str(n) for n in range(1, cli.CLOUD_CALLS_AT_ONCE + 1))


def _corpus_bodies() -> dict[str, str]:
    """Seven weeks of one course. `test_a_fact_call_cache.py`'s file, multiplied.

    Releasable prose with NO deterministic course code, for that file's own
    reason: a file whose subject the rule stage settles has no open field left and
    never reaches a model at all, so a corpus of syllabi would measure nothing.

    **They are seven weeks of ONE course and not seven unrelated readings, and
    that is measured rather than decorative.** Seven files that share nothing are
    grouped into nothing, no group is accepted, `design_tree` raises
    `NothingToDesign`, and site C is never reached -- so the placement test below
    would have had no calls to count. Seven weeks of one course group, get a
    branch, and every one of them is put to site C.
    """
    bodies = {
        f"week {week} notes.txt": (
            f"Week {week} of the course. Notes from the tutorial on aggregate "
            f"demand, with the problem set questions the instructor assigned in "
            f"week {week}.\n")
        for week in WEEKS
    }
    # THE ONE THE FAILING-CALL TEST AIMS AT, and it is one of the same seven rather
    # than an eighth: a batch with a hole in it has to be a FULL batch, or the test
    # measures a lane of six that happened to work.
    first = f"week {WEEKS[0]} notes.txt"
    bodies[first] = bodies[first].replace("tutorial", f"{FAILING_WORD} tutorial")
    return bodies


class _Lane:
    """Every call the run made, with the width of the lane it was made in.

    **The waiting is the assertion.** `arrive` blocks until `expected` calls are in
    flight at the same moment, or until `PATIENCE` runs out; `at_once` is the most
    that were ever in flight together. A pass that sent its calls one after another
    leaves `at_once` at 1 and the test says so with a number, which is what `104`
    §18.22 measured about r19 and what this build is meant to change.

    It records `call_site` off the dossier so that site C -- which reaches this same
    stub for every file P11 proposes a folder for -- is neither counted in site A's
    width nor made to wait for six companions it will never have.
    """

    def __init__(self, *, expected: int, reverse: bool = False,
                 fail_on: str | None = None, witness=None,
                 at_site: str = cli.A_FACT):
        #: WHICH SITE'S LANE THIS INSTRUMENT IS ABOUT. Every other site is served
        #: straight through, so a site making one call is neither counted in this
        #: one's width nor made to wait for companions it will never have.
        self.at_site = at_site
        self.expected = expected
        self.reverse = reverse
        self.fail_on = fail_on
        #: What `_Releases` had logged when each of site A's calls entered the
        #: stub. All equal means no release was minted while bytes were in the
        #: air, which is the gate having been asked for the whole batch first.
        self.witness = witness
        self.releases_when_sent: list[int] = []
        self.at_once = 0
        self.payloads: list[bytes] = []
        self.arrivals: list[str] = []
        self.returns: list[str] = []
        self._in_flight = 0
        self._released = 0
        self._cond = threading.Condition()

    # --- what the run did, read back -------------------------------------

    def _body(self, payload: bytes) -> dict:
        return json.loads(payload.decode("utf-8").split(DOSSIER_FOLLOWS, 1)[1])

    def calls_at(self, call_site: str) -> int:
        return sum(1 for payload in self.payloads
                   if self._body(payload)["call_site"] == call_site)

    # --- the socket ------------------------------------------------------

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            body = self._body(payload)
            if body["call_site"] != self.at_site:
                self.payloads.append(payload)
                # SITE G ARRIVES HERE TOO since `00` amendment 7(c): a file the
                # gate CLEARED may have its situation asked off the device, so this
                # seam sees a situation dossier whose schema is not site A's.
                # `_decline` below answers field by field, which at site G is a
                # malformed claim the validator refuses -- a silence reached by a
                # fault -- so it is declined in the shape the ratified prompt asks
                # for. It is served straight through either way: site G runs before
                # the batch and is neither counted in its width nor made to wait.
                if body["call_site"] == cli.G_SITUATION_SENSITIVITY:
                    return _decline_the_situation(body).encode("utf-8")
                return self._decline(body)
            subject = body["subject_ref"]
            self._arrive(subject)
            try:
                if self.fail_on is not None and self.fail_on in payload.decode(
                        "utf-8"):
                    # A PROVIDER THAT HUNG UP, which is what `transport.issue`'s
                    # `except Exception` is written for. Raised inside the send, on
                    # whichever thread is running it, which is the state the lane
                    # has to survive.
                    raise ConnectionResetError("the provider hung up")
                self.payloads.append(payload)
                return self._decline(body)
            finally:
                self._leave(subject)
        return invoke

    def _decline(self, body: dict) -> bytes:
        """Every field declined. What is under test is the wiring, not an answer."""
        fields = [field for field in body.get("allowed_vocabulary", ())
                  if isinstance(field, str)]
        return json.dumps({"claims": [
            {"payload": {"field": field},
             "unknown": {"insufficiency_statement":
                         "nothing in the released evidence names it"}}
            for field in fields] or [
            {"payload": {"field": "work_type"},
             "unknown": {"insufficiency_statement": "the dossier released nothing"}}
        ]}).encode("utf-8")

    def _arrive(self, subject: str) -> None:
        with self._cond:
            if self.witness is not None:
                self.releases_when_sent.append(self.witness())
            self.arrivals.append(subject)
            self._in_flight += 1
            self.at_once = max(self.at_once, self._in_flight)
            self._cond.notify_all()
            self._cond.wait_for(lambda: self.at_once >= self.expected,
                                timeout=PATIENCE)
            if not self.reverse:
                return
            # LAST IN, FIRST OUT. The provider answers in the opposite order to the
            # one the files were walked in, so the walk-order test is measuring the
            # driver and not a coincidence of arrival.
            mine = self.arrivals.index(subject)
            self._cond.wait_for(
                lambda: len(self.arrivals) - 1 - self._released == mine,
                timeout=PATIENCE)
            self._released += 1
            self._cond.notify_all()

    def _leave(self, subject: str) -> None:
        with self._cond:
            self._in_flight -= 1
            self.returns.append(subject)
            self._cond.notify_all()


class _Releases:
    """How many releases `Gate.release` has decided so far, at any moment.

    Bound OVER the real method rather than replacing it: the decision is the
    product's and this counts it, so nothing about what may leave the device is
    decided by a test. `ModelCallRequest` carries no `call_site` -- B2 puts the
    site inside the prompt fingerprint (`privacy/release.py`) -- so this counts
    every site's, which is why the assertion below is about a count that does not
    MOVE during a batch's sends rather than about whose release it was.
    """

    def __init__(self):
        self.decided = 0
        self._lock = threading.Lock()

    def note(self) -> None:
        with self._lock:
            self.decided += 1

    def so_far(self) -> int:
        with self._lock:
            return self.decided


@pytest.fixture()
def releases(monkeypatch):
    recorder = _Releases()
    original = gate_module.Gate.release

    def watched(self, request, *args, **kwargs):
        decision = original(self, request, *args, **kwargs)
        recorder.note()
        return decision

    monkeypatch.setattr(gate_module.Gate, "release", watched)
    return recorder


@pytest.fixture(autouse=True)
def _no_ambient_key(monkeypatch, tmp_path):
    """The developer's own key must not decide whether these tests pass.

    The local model's two names are cleared for the same reason and it is not a
    formality here of all places: a machine with ollama running would answer the
    gate with whatever it pulled, and a real local model's latency would decide
    whether seven calls were ever in flight together. `_local_model` puts the
    stub's own names back.
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
        return _decline_the_situation(dossier)
    return _answer_for(payload)


@pytest.fixture(autouse=True)
def _local_model(monkeypatch, _no_ambient_key):
    """A local model for the whole test, because a run now needs one to send.

    AUTOUSE AND PER TEST, beside `_no_ambient_key` and for its reason: this is what
    the deployment IS since amendment 7(c), not something one pin arranges. It is
    on the driver-only tests too, which drive `in_walk_order` and reach no model at
    all -- one deployment for the file rather than a fixture each pin has to
    remember, which is the mistake that put a 0 in the four pins below.
    """
    with StubOllama(answer=_local_answer) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        yield stub


@pytest.fixture()
def corpus(tmp_path):
    folder = tmp_path / "holder" / "corpus"
    folder.mkdir(parents=True)
    for name, body in _corpus_bodies().items():
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


# --- 1 and 2: the width, and the gate before the queue ------------------------


def test_every_cloud_call_of_a_batch_is_on_the_wire_at_the_same_moment(
        corpus, monkeypatch, releases):
    """`104` §18.15. Measured on r19 (§18.22): 223 dossiers in nine hours with
    every call one after another, site A's cloud share 47%. Here the stub holds
    each of site A's calls until `cli.CLOUD_CALLS_AT_ONCE` of them are in flight
    together, and the pass finishes -- which a serial pass could not do. The
    high-water mark is the measurement and it is the lane's whole width.

    **AND THE GATE IS ASKED BEFORE ANY OF THEM IS QUEUED.** Rule three of the
    build: the privacy decision did not move. Every one of the batch's releases is
    minted on the calling thread while the dossiers are being built, so site A's
    log reads as seven releases and then seven sends -- not one release, one send,
    seven times over.
    """
    lane = _Lane(expected=cli.CLOUD_CALLS_AT_ONCE, witness=releases.so_far)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.calls_at(cli.A_FACT) == cli.CLOUD_CALLS_AT_ONCE, (
        f"the corpus is one file per worker and every one of them should have "
        f"reached the model: {report}")
    assert lane.at_once == cli.CLOUD_CALLS_AT_ONCE, (
        f"{lane.at_once} of {cli.CLOUD_CALLS_AT_ONCE} calls were ever in flight "
        f"together; r19's number was 1 and this build exists to change it")
    # The pass says so on the screen, in the sentence that already says where the
    # calls went. `104` §18.15 rule six: no new counter in the prose.
    assert f"up to {cli.CLOUD_CALLS_AT_ONCE} at a time" in report, report
    # THE GATE, ASKED FOR EVERY ONE OF THEM BEFORE THE FIRST BYTE LEFT. The count
    # of decided releases is read as each call enters the stub, and it is the same
    # number for all seven: not one release was minted while a call was in the air,
    # because all seven were minted on the calling thread before any of them was
    # queued. A pass that released and sent in turn would show seven rising numbers.
    assert len(set(lane.releases_when_sent)) == 1, (
        f"a release was minted while bytes were already on the wire: "
        f"{lane.releases_when_sent}")
    assert lane.releases_when_sent[0] >= cli.CLOUD_CALLS_AT_ONCE, (
        f"only {lane.releases_when_sent[0]} releases had been decided when the "
        f"first call left, and the batch is {cli.CLOUD_CALLS_AT_ONCE} calls")


def test_two_local_sends_never_overlap_but_a_local_send_runs_beside_the_cloud():
    """`104` §18.15's local rule, stated over the two things it is about.

    **What must never happen** is a second concurrent LOCAL call: one Ollama
    server holds one model in memory, and the second one is what filled the
    machine's swap in r18 and made the OS kill the run (§17.21). The driver needs
    no counter for that -- the local sends are performed on the calling thread, and
    one thread cannot be in two places.

    **What must happen** is a local send running WHILE the cloud sends of its batch
    are in the air. The first build settled the batch before every local call and
    ran it alone, which is stricter than the direction ("the local lane stays
    serial") and cost the whole gain: site A's cloud share was 47% (§18.22), so a
    walk that alternates would settle a batch of one or two over and over. A cloud
    socket waiting beside a local call costs the server nothing.

    Measured here over a walk that alternates the two localities, which is that
    corpus's shape: no local send is ever beside another, every local send is
    beside a cloud one, and the cloud sends of one batch overlap each other.
    """
    watcher = _Overlaps(hold_until_locals=2)
    walk = [("cloud-a", CLOUD_LOCALITY), ("cloud-b", CLOUD_LOCALITY),
            ("local-a", LOCAL_LOCALITY), ("cloud-c", CLOUD_LOCALITY),
            ("cloud-d", CLOUD_LOCALITY), ("local-b", LOCAL_LOCALITY)]
    lane = CallLane(width=cli.CLOUD_CALLS_AT_ONCE)
    answered = list(in_walk_order(
        ((key, _one_send(key, locality, watcher)) for key, locality in walk),
        lane=lane))

    assert [key for key, _value in answered] == [key for key, _ in walk]
    assert watcher.local_beside_local == [], (
        f"a local send overlapped another local send ({watcher.local_beside_local})"
        f", and one local model in memory is the machine's whole budget")
    assert sorted(watcher.local_beside_cloud) == ["local-a", "local-b"], (
        f"only {watcher.local_beside_cloud} ran beside the cloud lane; a local "
        f"call that stops the world is the lane the first build shipped and the "
        f"one this test exists to keep")
    assert watcher.widest_cloud > 1, (
        "no two cloud sends were ever open together, so the lane did nothing")


def test_a_local_send_with_nothing_to_be_beside_is_settled_at_once():
    """`104` §18.15: a local call joins a batch only to overlap cloud work.

    A run with no cloud target -- every file local, which is what
    `tests/integration/test_local_model_fact_pass.py` drives end to end -- has
    nothing for a local send to be beside, so holding it back would mint its
    release and reserve its budget slot early and buy nothing. Measured: over a
    walk of local sends alone, the cloud lane never opens and each call is
    performed and finished before the next file's is prepared.
    """
    watcher = _Overlaps()
    prepared: list[str] = []
    walk = [("local-a", LOCAL_LOCALITY), ("local-b", LOCAL_LOCALITY),
            ("local-c", LOCAL_LOCALITY)]
    lane = CallLane(width=cli.CLOUD_CALLS_AT_ONCE)
    answered = list(in_walk_order(
        ((key, _one_send(key, locality, watcher, prepared=prepared))
         for key, locality in walk),
        lane=lane))

    assert [key for key, _value in answered] == [key for key, _ in walk]
    assert watcher.local_beside_local == []
    assert watcher.local_beside_cloud == []
    assert lane.at_once <= 1, (
        f"{lane.at_once} calls were open at once on a walk with no cloud target")
    # PREPARED, SENT, FINISHED, then the next one -- the serial path, unchanged.
    assert prepared == ["local-a", "local-b", "local-c"]


def test_the_slow_local_call_is_still_charged_to_the_file_that_made_it():
    """`104` R-175's per-file ceiling, over a walk that has a batch in it.

    That ceiling is a backstop against one file holding a 199-file run (§18.22:
    r19 hung for 26 minutes on a local call with an idle server). It charges a
    file the time the run spends WITH it, by turns -- and a batch breaks that in
    two ways. The wait for seven cloud calls belongs to no single file, so the
    driver stops the clock before it. Stopping it closes the only open turn, so a
    file whose own call then runs alone -- every LOCAL file, which is the slow
    one this ceiling is FOR -- would be charged nothing at all unless the clock is
    started again for it. `on_pause` and `on_resume` are that pair.

    **AND THE LOCAL SEND NOW RUNS INSIDE THE SHARED WINDOW, which is what makes
    the pair load-bearing rather than tidy.** The cloud sends of the batch are in
    the air while this thread spends the two minutes, so the clock is reopened for
    the file about to spend them and closed again the moment it is done -- the
    gather that follows is nobody's.

    **Measured on an injected clock, so the ceiling can be held against a
    two-minute call without spending two minutes.** Two cloud sends and two local
    ones in one batch, each local taking 120 seconds: each is charged for its OWN
    call, neither is charged for the other's, and the cloud files are charged for
    neither.
    """
    ticks = [0.0]
    moving = threading.Lock()
    ceiling = PerFileCeiling(seconds=600.0, clock=lambda: ticks[0])
    # The cloud stubs hold until both local sends have entered, so the window this
    # measures is genuinely shared and not two windows in a row.
    watcher = _Overlaps(hold_until_locals=2)
    walk = [("cloud-a", CLOUD_LOCALITY), ("cloud-b", CLOUD_LOCALITY),
            ("local-a", LOCAL_LOCALITY), ("local-b", LOCAL_LOCALITY)]

    def _tick(key: str, seconds: float):
        def moved():
            # UNDER A LOCK. The clock is now advanced from the pool's threads and
            # from this one at the same time, and `+=` on a shared cell is a read
            # and a write with a gap between them.
            with moving:
                ticks[0] += seconds
        return moved

    lane = CallLane(width=cli.CLOUD_CALLS_AT_ONCE)
    answered = list(in_walk_order(
        ((key, _one_send(key, locality, watcher,
                         opens_turn=ceiling.open_turn,
                         # A CLOUD CALL COSTS NOTHING ON THIS CLOCK. Its wait is
                         # real and belongs to no file, and giving it seconds here
                         # would only measure how the two localities interleave.
                         costs=(120.0 if locality == LOCAL_LOCALITY else 0.0),
                         tick=_tick))
         for key, locality in walk),
        lane=lane, on_pause=ceiling.close_turn, on_resume=ceiling.open_turn))
    ceiling.close_turn()

    assert [key for key, _value in answered] == [key for key, _ in walk]
    for key in ("local-a", "local-b"):
        assert 120.0 <= ceiling.spent[key] < 240.0, (
            f"{key}'s call took 120 seconds and its file was charged "
            f"{ceiling.spent[key]}; R-175's backstop reads this number, and a "
            f"file billed for its neighbour's call is over any ceiling worth "
            f"setting")
    for key in ("cloud-a", "cloud-b"):
        assert ceiling.spent[key] < 120.0, (
            f"{key} was charged {ceiling.spent[key]} seconds -- a file billed for "
            f"a wait it shared with three others is over any ceiling worth setting")


def test_rows_are_written_in_walk_order_when_the_provider_answers_backwards(
        corpus, monkeypatch):
    """`104` §18.15 rule five. Two runs over one corpus must write the same rows in
    the same order whichever call came back first, so the driver resumes the
    batch's generators in the order the files were WALKED and never in the order
    the answers arrived.

    Measured by making the provider answer last-arrived-first: the stub releases
    the batch in the reverse of its arrival order, and the `llm_response` rows --
    written after the resume, one per answered call -- still come out in the roster
    order the `llm_dossier` rows were written in before any of them was sent.
    """
    lane = _Lane(expected=cli.CLOUD_CALLS_AT_ONCE, reverse=True)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.at_once == cli.CLOUD_CALLS_AT_ONCE, report
    assert lane.returns[:2] != lane.arrivals[:2], (
        f"the stub was asked to answer backwards and did not: "
        f"{lane.arrivals} then {lane.returns}")
    walked = [row["subject_ref"] for row in _rows(
        corpus,
        "SELECT subject_ref FROM llm_dossier WHERE call_site = ? ORDER BY rowid",
        cli.A_FACT)]
    answered = [row["subject_ref"] for row in _rows(
        corpus,
        "SELECT d.subject_ref AS subject_ref FROM llm_response r "
        "JOIN llm_dossier d ON d.dossier_id = r.dossier_id "
        "WHERE d.call_site = ? ORDER BY r.rowid", cli.A_FACT)]
    assert answered == walked, (
        f"the responses were written in the order they came back and not in the "
        f"order the files were walked: {answered} against {walked}")


def test_one_call_that_does_not_come_back_leaves_the_others_alone(
        corpus, monkeypatch):
    """`104` §18.15 rule four, and `104` R-O's rule unchanged by the lane: a call
    that fails is a row and the run goes on. Before the lane a raise inside one
    call could only cost that file; inside a batch the six beside it have already
    spent a release and sent their bytes, so the driver records every response it
    is holding before anything is re-raised.

    Measured: one of the seven raises `ConnectionResetError` on its own thread; it
    writes one `llm_call_failure` row of class `client_raised`, and the other six
    are answered and recorded.
    """
    lane = _Lane(expected=cli.CLOUD_CALLS_AT_ONCE, fail_on=FAILING_WORD)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.at_once == cli.CLOUD_CALLS_AT_ONCE, report
    failures = _rows(
        corpus,
        "SELECT f.failure_class AS failure_class FROM llm_call_failure f "
        "JOIN llm_dossier d ON d.dossier_id = f.dossier_id "
        "WHERE d.call_site = ?", cli.A_FACT)
    assert [row["failure_class"] for row in failures] == ["client_raised"], (
        f"one call was made to fail and the failure row is what says so: {report}")
    answered = _rows(
        corpus,
        "SELECT count(*) AS n FROM llm_response r "
        "JOIN llm_dossier d ON d.dossier_id = r.dossier_id "
        "WHERE d.call_site = ?", cli.A_FACT)[0]["n"]
    assert answered == cli.CLOUD_CALLS_AT_ONCE - 1, (
        f"{answered} of the other six calls were recorded; one failure does not "
        f"stop the batch: {report}")
    # AND THE RUN ITSELF FINISHED. `104` R-O: the person gets the report the run
    # had already earned, not a traceback.
    assert "Facts from a model" in report, report


def test_the_placement_pass_holds_its_cloud_calls_open_together_too(
        corpus, monkeypatch):
    """`104` §18.15 names two sites: *"the cloud sites A and C carry no serial
    limit"*. Site C is the placement check -- one call per file P11 proposes a
    folder for -- and r19 never reached it (§18.22), so r20 is the first run where
    its wall-clock counts.

    Measured the same way and through the same stub, with the barrier moved to
    site C: the per-file placement pass holds all of them open at once. The lane's
    width comes from `PipelineInputs.calls_at_once`, which `cli` fills from the
    same `EXTRACTION_WORKERS` the fact pass uses -- one answer to "how much of
    this machine may one run take", spent at both sites.

    **The group pass and the multi-home branch stay serial and that is stated in
    `run_corpus`.** A group plan's calls are one per GROUP, and the multi-home
    branch puts a question to the person; neither is a lane's worth of waiting.
    """
    lane = _Lane(expected=cli.CLOUD_CALLS_AT_ONCE, at_site=cli.C_PLACEMENT)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.calls_at(cli.C_PLACEMENT) == cli.CLOUD_CALLS_AT_ONCE, (
        f"one placement call per file is what site C makes: {report}")
    assert lane.at_once == cli.CLOUD_CALLS_AT_ONCE, (
        f"{lane.at_once} of {cli.CLOUD_CALLS_AT_ONCE} placement calls were ever in "
        f"flight together")
    # And the pass says so, on the sentence that already counts what it decided.
    # `104` §18.15 rule six: no new counter in the prose.
    assert f"checked {cli.CLOUD_CALLS_AT_ONCE} at a time" in report, report


# --- the driver's own instrument ----------------------------------------------


class _Overlaps:
    """Which sends were open at the same moment, by locality.

    Two readings, and `104` §18.15's local rule is the difference between them.
    `local_beside_local` is the one that must stay empty: one Ollama server holds
    one model in memory and a second concurrent local call is what filled the
    machine's swap in r18 (§17.21). `local_beside_cloud` is the one that must NOT
    be empty on a mixed walk -- a cloud socket waiting beside a local call costs
    the server nothing, and a driver that stopped the world for every local file
    would settle batches of one or two on a corpus that is 47% cloud and the lane
    would be a lane in name.
    """

    def __init__(self, *, hold_until_locals: int = 0):
        #: HOW MANY LOCAL SENDS A CLOUD SEND WAITS FOR before it answers. A stub
        #: that returns the moment its companions arrive is gone again before the
        #: calling thread reaches the local half of the batch, and "they
        #: overlapped" would then be a fact about scheduling luck. Zero for a walk
        #: with no local send in it.
        self.hold_until_locals = hold_until_locals
        self.open: dict[str, int] = {CLOUD_LOCALITY: 0, LOCAL_LOCALITY: 0}
        self.widest_cloud = 0
        self.locals_seen = 0
        self.local_beside_local: list[str] = []
        self.local_beside_cloud: list[str] = []
        self._lock = threading.Lock()
        self._gathered = threading.Condition(self._lock)

    def enter(self, key: str, locality: str) -> None:
        with self._gathered:
            self.open[locality] += 1
            if locality == LOCAL_LOCALITY:
                self.locals_seen += 1
                if self.open[LOCAL_LOCALITY] > 1:
                    self.local_beside_local.append(key)
                if self.open[CLOUD_LOCALITY]:
                    self.local_beside_cloud.append(key)
            self.widest_cloud = max(self.widest_cloud, self.open[CLOUD_LOCALITY])
            self._gathered.notify_all()
            if locality == CLOUD_LOCALITY:
                # Hold until the rest of this batch has arrived, so "they overlap"
                # is a fact about the driver and not about how fast a list append
                # happens to be.
                self._gathered.wait_for(
                    lambda: (self.widest_cloud > 1
                             and self.locals_seen >= self.hold_until_locals),
                    timeout=PATIENCE)

    def leave(self, locality: str) -> None:
        with self._gathered:
            self.open[locality] -= 1
            self._gathered.notify_all()


def test_the_same_question_twice_in_one_batch_is_one_call():
    """`104` §18.28: a duplicate waits for its twin's answer instead of buying it.

    The batch is the window the old note called an accepted cost: `llm_call_
    identity` is written AFTER the call, so inside one window two copies of a file
    both reached the provider and a person paid twice for one answer. The driver is
    the only place that can see both at once, and the bytes are what it compares --
    `assemble` is the template plus the canonical dossier and carries no
    provenance, so equal bytes are the same prompt about the same content.

    Measured here over three cloud subjects, two of which ask the same thing: the
    later one is answered out of the earlier one's round trip (its answer IS the
    earlier one's raw bytes), the third is asked on its own, and the lane counts
    the question it did not buy.
    """
    watcher = _Overlaps()
    walk = [("first", b"the same question"), ("twin", b"the same question"),
            ("other", b"a different question")]
    lane = CallLane(width=cli.CLOUD_CALLS_AT_ONCE)
    answered = list(in_walk_order(
        ((key, _one_send(key, CLOUD_LOCALITY, watcher, asks=asks))
         for key, asks in walk), lane=lane))

    assert [key for key, _value in answered] == ["first", "twin", "other"]
    got = dict(answered)
    # THE TWIN CARRIES THE ASKING SUBJECT'S OWN ANSWER. The fake answers with its
    # own key, so `b"first"` here is the proof that no second socket was opened
    # for `twin`: its own send would have said `b"twin"`.
    assert got["twin"] == b"first", got
    assert got["first"] == b"first" and got["other"] == b"other", got
    assert lane.reused == 1, (
        f"the lane says {lane.reused} questions were answered out of another "
        f"call, and exactly one duplicate stood in this batch")
    # The window is the DISTINCT questions: two, not three.
    assert lane.at_once == 2, lane.at_once


def test_a_call_that_failed_is_not_handed_to_its_twin():
    """`104` §18.28, and the half that is about coverage rather than money.

    A provider that timed out bought no answer. Handing that failure to the
    duplicate standing beside it would spend a second file's only chance on the
    first one's bad minute -- two files with no fact where the run before this
    rule would have had one -- so the twin makes its own send, in its turn, and
    nothing is counted as reused.
    """
    watcher = _Overlaps()
    outage = TimeoutError("the provider did not answer")
    lane = CallLane(width=cli.CLOUD_CALLS_AT_ONCE)
    answered = list(in_walk_order(
        [("first", _one_send("first", CLOUD_LOCALITY, watcher,
                             asks=b"the same question", fails=outage)),
         ("twin", _one_send("twin", CLOUD_LOCALITY, watcher,
                            asks=b"the same question")),
         ("other", _one_send("other", CLOUD_LOCALITY, watcher,
                             asks=b"a different question"))],
        lane=lane))

    got = dict(answered)
    assert [key for key, _value in answered] == ["first", "twin", "other"]
    # A `SendResult` carrying an exception has no `raw`, which is what the failing
    # subject's steps return; the twin asked and has its own.
    assert got["first"] is None, got
    assert got["twin"] == b"twin", got
    assert lane.reused == 0, (
        "a failure was counted as an answer reused, which is the one thing this "
        "rule must not do to a second file")


#: ONE MODEL BEHIND EVERY FAKE CARRIER, because the driver's question key is the
#: bytes AND the client: two clients are two models and two answers, and a fake
#: that minted one client per subject could never be a duplicate of anything.
_ONE_CLIENT = object()


def _one_send(key: str, locality: str, watcher: _Overlaps, *,
              opens_turn=None, costs: float = 0.0, tick=None, prepared=None,
              asks: bytes | None = None, fails: BaseException | None = None):
    """One subject's steps: nothing but a socket, so the driver is what is tested.

    **THE CARRIER IS A FAKE AND THAT IS DELIBERATE.** The real one is
    `transport._PendingSend`, and it is private because `perform` IS the egress and
    a public one would be a second door (P7 Done-means 3). The driver never builds
    one and never names its type -- it asks for a `locality` and calls `perform` --
    so a fake that answers those two is the protocol, and using it here keeps this
    pin about the driver's ORDER OF WORK with no database, gate or model in the way.

    `asks` is the same protocol one step further: `104` §18.28's duplicate rule
    reads `model_visible_bytes` and `model_client` off the carrier, so a fake that
    offers them is a subject with a question and a fake that does not is a subject
    whose question cannot be read -- which is the case every other test here
    drives, and which is never paired with anything.

    `fails` is what the provider did rather than what it said: a `SendResult`
    carrying the exception, exactly as `_PendingSend.perform` carries one rather
    than raising it across a thread.
    """

    class _Carrier:
        locality = None
        model_visible_bytes = None
        model_client = None

        def perform(self) -> SendResult:
            watcher.enter(key, self.locality)
            try:
                if tick is not None:
                    # THE CALL TAKING TIME, on the injected clock. A real one
                    # spends it in a socket; here it is the only thing that moves.
                    tick(key, costs)()
                if fails is not None:
                    return SendResult(error=fails)
                return SendResult(raw=key.encode("utf-8"))
            finally:
                watcher.leave(self.locality)

    carrier = _Carrier()
    carrier.locality = locality
    if asks is not None:
        carrier.model_visible_bytes = asks
        carrier.model_client = _ONE_CLIENT

    def steps():
        # `104` R-175: the stage opens this file's turn before it does any work,
        # which is where `fact_call_stage` opens it. Only the clock test asks for
        # one; the driver itself never touches the ceiling.
        if opens_turn is not None:
            opens_turn(key)
        # WHEN THIS SUBJECT'S CALL WAS PREPARED, for the test that asks whether a
        # local send with nothing to be beside was held back: a preparation that
        # arrives before an earlier subject's answer is a release minted early.
        if prepared is not None:
            prepared.append(key)
        sent = yield carrier
        return sent.raw

    return steps()

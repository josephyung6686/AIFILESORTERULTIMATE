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
   each arrival until the lane is as wide as `cli.EXTRACTION_WORKERS`, so a pass
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

**Everything here is real except the socket.** `readers.model_routing.
deepseek_invoke` is the documented deployment seam and the stub is bound in its
place, exactly as `tests/integration/test_a_fact_call_cache.py` binds it, so the
route, the gate, the release ledger, the transport, the validator and the whole of
`cli.run` are the production path. The stub is the only thing that knows a thread
from another one.
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


def _corpus_bodies() -> dict[str, str]:
    """One ordinary file per worker the run already spawns, and no more.

    `cli.EXTRACTION_WORKERS` files, so a full batch is exactly the corpus: what the
    lane can hold and what the pass has to send are the same number, and the
    high-water mark below is therefore an equality rather than an inequality. The
    bodies are `test_a_fact_call_cache.py`'s two, multiplied: releasable prose with
    NO deterministic course code, because a file whose subject the rule stage
    settles has no open field left and never reaches a model at all.
    """
    bodies = {}
    for index in range(cli.EXTRACTION_WORKERS):
        bodies[f"reading notes {index}.txt"] = (
            f"Notes on the assigned reading for seminar {index}. The lecture "
            f"covered the textbook chapters on momentum and energy, and the "
            f"homework is due Thursday.\n")
    # THE ONE THE FAILING-CALL TEST AIMS AT, and it is one of the same seven rather
    # than an eighth: a batch with a hole in it has to be a FULL batch, or the test
    # measures a lane of six that happened to work.
    first = "reading notes 0.txt"
    bodies[first] = bodies[first].replace("seminar 0", f"seminar {FAILING_WORD}")
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
                 fail_on: str | None = None, witness=None):
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
            if body["call_site"] != cli.A_FACT:
                # Every other site is served straight through. Only site A's lane
                # is under test here and a site with one call cannot fill a batch.
                self.payloads.append(payload)
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
    for name, body in _corpus_bodies().items():
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


# --- 1 and 2: the width, and the gate before the queue ------------------------


def test_every_cloud_call_of_a_batch_is_on_the_wire_at_the_same_moment(
        corpus, monkeypatch, releases):
    """`104` §18.15. Measured on r19 (§18.22): 223 dossiers in nine hours with
    every call one after another, site A's cloud share 47%. Here the stub holds
    each of site A's calls until `cli.EXTRACTION_WORKERS` of them are in flight
    together, and the pass finishes -- which a serial pass could not do. The
    high-water mark is the measurement and it is the lane's whole width.

    **AND THE GATE IS ASKED BEFORE ANY OF THEM IS QUEUED.** Rule three of the
    build: the privacy decision did not move. Every one of the batch's releases is
    minted on the calling thread while the dossiers are being built, so site A's
    log reads as seven releases and then seven sends -- not one release, one send,
    seven times over.
    """
    lane = _Lane(expected=cli.EXTRACTION_WORKERS, witness=releases.so_far)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.calls_at(cli.A_FACT) == cli.EXTRACTION_WORKERS, (
        f"the corpus is one file per worker and every one of them should have "
        f"reached the model: {report}")
    assert lane.at_once == cli.EXTRACTION_WORKERS, (
        f"{lane.at_once} of {cli.EXTRACTION_WORKERS} calls were ever in flight "
        f"together; r19's number was 1 and this build exists to change it")
    # The pass says so on the screen, in the sentence that already says where the
    # calls went. `104` §18.15 rule six: no new counter in the prose.
    assert f"up to {cli.EXTRACTION_WORKERS} at a time" in report, report
    # THE GATE, ASKED FOR EVERY ONE OF THEM BEFORE THE FIRST BYTE LEFT. The count
    # of decided releases is read as each call enters the stub, and it is the same
    # number for all seven: not one release was minted while a call was in the air,
    # because all seven were minted on the calling thread before any of them was
    # queued. A pass that released and sent in turn would show seven rising numbers.
    assert len(set(lane.releases_when_sent)) == 1, (
        f"a release was minted while bytes were already on the wire: "
        f"{lane.releases_when_sent}")
    assert lane.releases_when_sent[0] >= cli.EXTRACTION_WORKERS, (
        f"only {lane.releases_when_sent[0]} releases had been decided when the "
        f"first call left, and the batch is {cli.EXTRACTION_WORKERS} calls")


def test_a_local_target_is_never_sent_beside_anything_else(monkeypatch):
    """`104` §18.15 rule three and §17.21's cost. One Ollama server holds one model
    in memory; the second concurrent local call is what filled the machine's swap
    in r18 and made the OS kill the run. So the driver settles everything it is
    holding BEFORE a local send, runs that send by itself on the calling thread,
    and settles it before walking on.

    Measured here over a walk that alternates the two localities, which is the
    shape a real corpus has (§18.22: site A's cloud share was 47%, the rest local):
    the local sends never overlap each other and never overlap a cloud send, while
    the cloud sends of one batch do overlap.
    """
    watcher = _Overlaps()
    walk = [("cloud-a", CLOUD_LOCALITY), ("cloud-b", CLOUD_LOCALITY),
            ("local-a", LOCAL_LOCALITY), ("cloud-c", CLOUD_LOCALITY),
            ("cloud-d", CLOUD_LOCALITY), ("local-b", LOCAL_LOCALITY)]
    lane = CallLane(width=cli.EXTRACTION_WORKERS)
    answered = list(in_walk_order(
        ((key, _one_send(key, locality, watcher)) for key, locality in walk),
        lane=lane))

    assert [key for key, _value in answered] == [key for key, _ in walk]
    assert watcher.local_beside_anything == [], (
        f"a local send overlapped {watcher.local_beside_anything}, and one local "
        f"model in memory is the machine's whole budget")
    assert watcher.widest_cloud > 1, (
        "no two cloud sends were ever open together, so the lane did nothing")


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
    lane = _Lane(expected=cli.EXTRACTION_WORKERS, reverse=True)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.at_once == cli.EXTRACTION_WORKERS, report
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
    lane = _Lane(expected=cli.EXTRACTION_WORKERS, fail_on=FAILING_WORD)
    monkeypatch.setattr(model_routing, "deepseek_invoke", lane.factory)

    report = _run(corpus, "--enable-cloud")

    assert lane.at_once == cli.EXTRACTION_WORKERS, report
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
    assert answered == cli.EXTRACTION_WORKERS - 1, (
        f"{answered} of the other six calls were recorded; one failure does not "
        f"stop the batch: {report}")
    # AND THE RUN ITSELF FINISHED. `104` R-O: the person gets the report the run
    # had already earned, not a traceback.
    assert "Facts from a model" in report, report


# --- the driver's own instrument ----------------------------------------------


class _Overlaps:
    """Which sends were open at the same moment, by locality."""

    def __init__(self):
        self.open: dict[str, int] = {CLOUD_LOCALITY: 0, LOCAL_LOCALITY: 0}
        self.widest_cloud = 0
        self.local_beside_anything: list[str] = []
        self._lock = threading.Lock()
        self._gathered = threading.Condition(self._lock)

    def enter(self, key: str, locality: str) -> None:
        with self._gathered:
            self.open[locality] += 1
            if locality == LOCAL_LOCALITY and (
                    self.open[LOCAL_LOCALITY] > 1 or self.open[CLOUD_LOCALITY]):
                self.local_beside_anything.append(key)
            if self.open[CLOUD_LOCALITY] and self.open[LOCAL_LOCALITY]:
                self.local_beside_anything.append(key)
            self.widest_cloud = max(self.widest_cloud, self.open[CLOUD_LOCALITY])
            self._gathered.notify_all()
            if locality == CLOUD_LOCALITY:
                # Hold until the rest of this batch has arrived, so "they overlap"
                # is a fact about the driver and not about how fast a list append
                # happens to be.
                self._gathered.wait_for(lambda: self.widest_cloud > 1,
                                        timeout=PATIENCE)

    def leave(self, locality: str) -> None:
        with self._gathered:
            self.open[locality] -= 1
            self._gathered.notify_all()


def _one_send(key: str, locality: str, watcher: _Overlaps):
    """One subject's steps: nothing but a socket, so the driver is what is tested.

    **THE CARRIER IS A FAKE AND THAT IS DELIBERATE.** The real one is
    `transport._PendingSend`, and it is private because `perform` IS the egress and
    a public one would be a second door (P7 Done-means 3). The driver never builds
    one and never names its type -- it asks for a `locality` and calls `perform` --
    so a fake that answers those two is the protocol, and using it here keeps this
    pin about the driver's ORDER OF WORK with no database, gate or model in the way.
    """

    class _Carrier:
        locality = None

        def perform(self) -> SendResult:
            watcher.enter(key, self.locality)
            try:
                return SendResult(raw=key.encode("utf-8"))
            finally:
                watcher.leave(self.locality)

    carrier = _Carrier()
    carrier.locality = locality

    def steps():
        sent = yield carrier
        return sent.raw

    return steps()

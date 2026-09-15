# tests/readers/test_model_deepseek_deadline.py
"""`104` R-176: one deadline over the WHOLE cloud call, against a real socket.

**These tests start a server, and every other test of this transport does not.**
`tests/readers/test_model_deepseek.py` says why it injects `send`: the two
statements that reach the provider cannot run without a key and a bill. That
argument is exactly right for everything ABOVE the socket and exactly wrong here,
because the defect R-176 records lives IN the socket. It is not a shape `_send`'s
callers can see -- an SDK timeout becomes four per-operation timers, and no fake
that raises on cue can tell that apart from a deadline. So these servers are real,
they are on loopback, they speak plain HTTP, and the whole of what they do is
refuse to finish. No key is needed to run them and nothing is billed.

**What the run sat in (`104` §18.28, 10 Sep 2026).** The internet dropped for about
ninety minutes. Three agents died on DNS and on a stream watchdog; r20 went on
making site A dossiers and recorded NO failure for seven files, because the cloud
client had no whole-call deadline and its per-operation timers were being satisfied
by sockets that were never going to answer. A run that records nothing is the
failure: the person is shown a corpus that was judged when part of it was never
asked.

**The third test is the one that discriminates.** A provider that accepts and sends
nothing, and one that stalls mid-body, are caught by a per-read timer too -- they
would pass against the client R-176 was filed against. A TRICKLE would not:
`test_a_provider_that_dribbles_a_byte_forever_still_ends_at_the_deadline` sends a
byte four times per patience, so no read ever waits long enough to fire and the old
client waits for as long as the trickle lasts. The fourth test holds the ONE bound
this seam cannot make tight, so that it is a measured promise and not a hope.
"""
from __future__ import annotations

import json
import socket
import threading
import time

import pytest

pytest.importorskip("openai", reason="the model transports are a `models` extra")
pytest.importorskip("httpx", reason="the OpenAI client's own transport library")

from privacy.release import ModelTarget                        # noqa: E402
from readers.model_deepseek import (                           # noqa: E402
    JUDGE_SAMPLING,
    READING_THE_BODY, WAITING_FOR_THE_FIRST_BYTE,
    ModelRanOutOfTime, ModelRanOutOfTimeReadingTheBody,
    ModelRanOutOfTimeWaitingForTheFirstByte, deepseek_invoke, request_body,
)

TARGET = ModelTarget(locality="cloud", model_id="a-model", provider="deepseek")

#: The deployment's number is `cli.MODEL_CALL_TIMEOUT_SECONDS` and is ninety
#: seconds. This is the same MECHANISM at a size a test can wait for: what is
#: asserted is that the call ends at the deadline, not what the deadline is.
PATIENCE = 0.6

#: How long past the deadline a call is allowed to take before the test calls it a
#: hang. VERY generous, and it costs the test nothing to be: what these tests have
#: to distinguish is "ends at the deadline" from "does not end at all", and the
#: client R-176 replaces did not end. Any finite bound discriminates, and a tight
#: one buys no power while making the pin flaky on a machine under load -- this
#: repo's own suite has run at a load average near a hundred beside other agents,
#: where several seconds of scheduling delay is ordinary and means nothing about
#: the client. The first call in a process also pays for `import openai`, which is
#: outside the budget and inside the measurement.
SLACK = 20.0

RESPONSE_TOKENS = 512

#: The word `request_body` requires in the prompt, because `JSON_MODE` is set and
#: the provider's stated precondition is that the prompt asks for JSON. A dossier
#: without it is refused before any socket is opened, which is a different test.
DOSSIER = b'{"dossier": "x", "answer_with": "one json object"}'

ANSWER = '{"claims": []}'


def _completion(text: str) -> bytes:
    """The smallest body the SDK will parse as one finished answer."""
    return json.dumps({
        "id": "chatcmpl-test", "object": "chat.completion", "created": 0,
        "model": "a-model",
        "choices": [{"index": 0, "finish_reason": "stop",
                     "message": {"role": "assistant", "content": text}}],
    }).encode("utf-8")


def _http(body: bytes) -> bytes:
    return (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: " + str(len(body)).encode("ascii") +
            b"\r\nConnection: close\r\n\r\n" + body)


class _Server:
    """A loopback server that answers requests badly, on purpose.

    `behave` is handed each accepted socket and does whatever this test's sabotage
    is. It runs on a thread so the client can block against it; `stop` is set when
    the test is done, so a thread stuck in its own wait loop leaves. It serves more
    than one connection because the byte-identity test needs two clients to reach
    the SAME port -- a second port would change the `host:` header and make the
    comparison meaningless.
    """

    def __init__(self, behave):
        self._behave = behave
        self.stop = threading.Event()
        self.requests: list[bytes] = []
        self._listener = socket.socket()
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(2)
        self.port = self._listener.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def _serve(self) -> None:
        # ACCEPT IN SHORT WAITS AND POLL `stop`, because a thread blocked in
        # `accept` is not reliably woken by another thread closing the listener --
        # measured at twenty seconds of teardown on this machine, for nothing.
        self._listener.settimeout(PATIENCE)
        while not self.stop.is_set():
            try:
                accepted, _ = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:  # the listener was closed: the test is over
                return
            with accepted:
                try:
                    self._behave(self, accepted, self.stop)
                except OSError:
                    # The client hung up at its deadline, which is the point.
                    pass

    def close(self) -> None:
        self.stop.set()
        self._listener.close()
        self._thread.join(timeout=SLACK)


@pytest.fixture
def server():
    made = []

    def start(behave) -> _Server:
        running = _Server(behave)
        made.append(running)
        return running

    yield start
    for running in made:
        running.close()


def _read_the_request(running: _Server, accepted: socket.socket) -> bytes:
    """Drain the client's POST so the server is genuinely mid-conversation."""
    accepted.settimeout(PATIENCE + SLACK)
    seen = b""
    while b"\r\n\r\n" not in seen:
        piece = accepted.recv(4096)
        if not piece:
            return seen
        seen += piece
    head, body = seen.split(b"\r\n\r\n", 1)
    length = 0
    for line in head.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            length = int(line.split(b":", 1)[1])
    while len(body) < length:
        piece = accepted.recv(4096)
        if not piece:
            break
        body += piece
    whole = head + b"\r\n\r\n" + body
    running.requests.append(whole)
    return whole


def _invoke(base_url: str):
    return deepseek_invoke(
        api_key="not-a-real-key", base_url=base_url, model_target=TARGET,
        max_response_tokens=RESPONSE_TOKENS, timeout_seconds=PATIENCE)


def _timed(base_url: str) -> tuple[ModelRanOutOfTime, float]:
    """Call, and give back the refusal and the wall-clock the call actually took."""
    started = time.monotonic()
    with pytest.raises(ModelRanOutOfTime) as raised:
        _invoke(base_url)(DOSSIER)
    return raised.value, time.monotonic() - started


def test_a_provider_that_accepts_and_never_sends_a_byte_runs_out_of_time(server):
    """SABOTAGE: the connection is established and no byte of a reply ever comes.

    This is the outage's own shape. A socket opened to a provider that is no longer
    reachable is ESTABLISHED and silent, and until R-176 there was no deadline for
    it to miss: the SDK's read timer was being restarted by a call that never got
    that far, and the run recorded nothing at all for the file.

    The client must give up at its own deadline and SAY which phase it gave up in
    -- `WAITING_FOR_THE_FIRST_BYTE`, because the request went out and nothing came
    back.
    """
    def silent(running, accepted, stop):
        _read_the_request(running, accepted)
        stop.wait(PATIENCE + SLACK)

    refusal, took = _timed(server(silent).base_url)

    assert took < PATIENCE + SLACK, (
        "a call to a provider that sends nothing has to end at the deadline")
    # THE CLASS AND NOT THE MESSAGE, because the class is what survives into the
    # record: `transport._client_exception_explanation` keeps
    # `type(exc).__qualname__` and drops the text (§8.4 property 4).
    assert isinstance(refusal, ModelRanOutOfTimeWaitingForTheFirstByte)
    assert WAITING_FOR_THE_FIRST_BYTE in str(refusal)
    assert f"{PATIENCE:g} seconds" in str(refusal)


def test_a_provider_that_sends_headers_and_stalls_mid_body_runs_out_of_time(server):
    """SABOTAGE: the status line and headers arrive, then the body stops halfway.

    A `Content-Length` is promised and half of it is sent. The deadline has to cover
    the body and not merely the wait for its first byte, or a provider that has
    started answering can hold a run open indefinitely by never finishing -- and the
    half-document is not an answer either way.
    """
    def stall_mid_body(running, accepted, stop):
        _read_the_request(running, accepted)
        promised = _completion(ANSWER)
        accepted.sendall(_http(promised)[:-len(promised) // 2])
        stop.wait(PATIENCE + SLACK)

    refusal, took = _timed(server(stall_mid_body).base_url)

    assert took < PATIENCE + SLACK, (
        "a body that stops halfway must not outlive the deadline: the rest of the "
        "answer is never going to arrive and the run is waiting for it")
    assert isinstance(refusal, ModelRanOutOfTimeReadingTheBody)
    assert READING_THE_BODY in str(refusal)


def test_a_provider_that_dribbles_a_byte_forever_still_ends_at_the_deadline(server):
    """SABOTAGE THAT NAMES THE DEFECT: a byte every quarter of the patience.

    **The two tests above pass against the client R-176 replaces.** A per-operation
    read timer fires on silence, and both of them are silent. This one is never
    silent: a byte arrives four times per patience, so every read returns promptly
    and the SDK's timer is satisfied for ever. Under the old client this call runs
    until the provider gets bored -- which is what `104` §18.22 measured on the
    local side at twenty-six minutes against a six-hundred-second patience.

    The assertion is therefore about WALL-CLOCK and not only about the exception: a
    client that raised the right error after ten minutes would still be the defect.
    It has to end at the deadline, and it does because the budget is consulted
    BETWEEN the pieces of the body rather than only by the socket's own timer.
    """
    def dribble(running, accepted, stop):
        _read_the_request(running, accepted)
        # A length nothing will ever reach, so the client is always owed more.
        accepted.sendall(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: 1000000\r\n\r\n")
        while not stop.wait(PATIENCE / 4):
            accepted.sendall(b" ")

    refusal, took = _timed(server(dribble).base_url)

    assert took < PATIENCE + SLACK, (
        f"the call took {took:.1f}s against a deadline of {PATIENCE:g}s. A body "
        f"that keeps arriving satisfies a per-read timer for ever, which is why "
        f"`104` R-176 is a DEADLINE and not a shorter timeout")
    assert isinstance(refusal, ModelRanOutOfTimeReadingTheBody)
    assert READING_THE_BODY in str(refusal)


def test_a_reply_that_trickles_and_then_stalls_is_bounded_where_it_is_documented(
        server):
    """THE ONE BOUND THIS SEAM CANNOT MAKE TIGHT, measured so it is a promise.

    The transport library arms each phase's socket timer ONCE -- httpcore reads
    `read` out of the timeout mapping before its body loop, not inside it -- so a
    piece that arrives just before that timer would have fired passes the
    between-pieces check and the NEXT wait is a window that was armed with the
    remainder at the start of the body. A reply that trickles and then goes quiet
    therefore ends at the deadline plus at most one such window, which is under
    twice the deadline and is never unbounded.

    `_under_one_deadline` states exactly that, and this is the measurement behind
    it. It is the honest bound and not the desirable one: making it tight would
    mean re-implementing the body reader, which means leaving the SDK -- and with
    it the owner's key and the TLS -- or running a watchdog thread per call, which
    is a second timing mechanism to keep true. Neither is worth what it buys over
    "silence exact, never unbounded".
    """
    def trickle_then_stall(running, accepted, stop):
        _read_the_request(running, accepted)
        accepted.sendall(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: 1000000\r\n\r\n")
        for _ in range(2):
            if stop.wait(PATIENCE / 4):
                return
            accepted.sendall(b" ")
        stop.wait(2 * PATIENCE + SLACK)

    refusal, took = _timed(server(trickle_then_stall).base_url)

    assert took < 2 * PATIENCE + SLACK, (
        f"the call took {took:.1f}s. The documented bound is the deadline plus one "
        f"armed read window, so under twice {PATIENCE:g}s -- anything longer means "
        f"the window is being RE-armed and the call is unbounded again")
    assert isinstance(refusal, ModelRanOutOfTimeReadingTheBody)


def test_a_normal_call_is_byte_identical_to_what_the_stock_client_sends(server):
    """THE DEADLINE MUST NOT CHANGE THE REQUEST, and this is how that is known.

    `transport.issue` recomputes and fingerprints the model-visible bytes before
    this module is called, and P7's release ledger records what left. A transport
    that altered a header, a path or a body byte would mean the audit record
    described one request and the provider saw another -- so the substituted
    transport is compared against the stock one over the SAME port, and the whole
    request is compared and not a summary of it.

    The answer is asserted too: a deadline that bounded a healthy call would be the
    R-176 defect pointed the other way.
    """
    import openai

    def answer(running, accepted, stop):
        _read_the_request(running, accepted)
        accepted.sendall(_http(_completion(ANSWER)))

    running = server(answer)

    assert _invoke(running.base_url)(DOSSIER) == ANSWER.encode("utf-8")

    # The same request, through the client this module used to build: no
    # `http_client`, so httpx supplies its own transport and its own four timers.
    with openai.OpenAI(api_key="not-a-real-key", base_url=running.base_url,
                       timeout=PATIENCE, max_retries=0) as stock:
        from readers.model_deepseek import JUDGE_SAMPLING, _as_the_sdk_takes_it
        # The same sampling term the product sends (15 Sep 2026): byte-identical
        # means identical INCLUDING the term nobody but this module chooses.
        stock.chat.completions.create(
            **_as_the_sdk_takes_it(request_body(
                model_id=TARGET.model_id, max_tokens=RESPONSE_TOKENS,
                prompt=DOSSIER.decode("utf-8"), temperature=JUDGE_SAMPLING)))

    under_the_deadline, stock_request = running.requests
    assert under_the_deadline == stock_request, (
        "the request the deadline transport sends is not the request the stock "
        "client sends")

    # The readable half of the same fact: what went out IS `request_body`'s output
    # and nothing else, so a term added by the transport fails here by name.
    head, body = under_the_deadline.split(b"\r\n\r\n", 1)
    assert head.split(b"\r\n")[0] == b"POST /chat/completions HTTP/1.1"
    assert json.loads(body) == request_body(
        model_id=TARGET.model_id, max_tokens=RESPONSE_TOKENS,
        prompt=DOSSIER.decode("utf-8"),
        temperature=JUDGE_SAMPLING)

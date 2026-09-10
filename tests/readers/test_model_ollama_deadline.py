# tests/readers/test_model_ollama_deadline.py
"""`104` R-175: one deadline over the WHOLE local call, against a real socket.

**These tests start a server, and every other test of this transport does not.**
`tests/readers/test_model_ollama.py` says why it injects `post`: a test that needed
ollama running is a test that gets skipped on the machine that most needs it. That
argument is exactly right for everything ABOVE the socket and exactly wrong here,
because the defect R-175 records lives IN the socket. It is not a shape `_post`'s
callers can see: `urlopen(timeout=...)` becomes `socket.settimeout`, which bounds
one `recv` and restarts on the next, and no fake that raises `TimeoutError` on cue
can tell that apart from a deadline. So these servers are real, they are on
loopback, they speak to one client each, and the whole of what they do is refuse to
finish.

**What r19 sat in (`104` §18.22, 10 Sep 2026).** The last dossier was written at
14:03; at 14:29 the worker held an ESTABLISHED connection to the local model server
and the server was at 0.4% CPU. The client's patience was 600 seconds and its
`OllamaRanOutOfTime` had already fired four times in the same run -- so the idle
timer was working, and the call was outliving it anyway.

**The third test is the one that discriminates.** A server that accepts and sends
nothing, and a server that stalls mid-body, are both caught by an idle timer too:
they would pass against the code R-175 was filed against. A TRICKLE would not.
`test_a_server_that_dribbles_a_byte_forever_still_ends_at_the_deadline` sends a
byte at a time, more often than the patience, so no `recv` ever waits long enough
to fire and the old client waits for ever. It is the SABOTAGE that names the
defect; the other two hold the phases either side of it.
"""
from __future__ import annotations

import json
import socket
import threading
import time

import pytest

from privacy.release import ModelTarget
from readers.model_ollama import (
    CALL_PHASES, CONNECTING, RAN_OUT_OF_TIME_IN, READING_THE_BODY,
    SENDING_THE_REQUEST, WAITING_FOR_THE_FIRST_BYTE,
    OllamaRanOutOfTime, OllamaRanOutOfTimeReadingTheBody,
    OllamaRanOutOfTimeWaitingForTheFirstByte, ollama_invoke,
)

TARGET = ModelTarget(locality="local", model_id="qwen3:8b", provider="ollama")

#: The deployment's numbers are `cli.py`'s and are minutes long. These are the same
#: MECHANISM at a size a test can wait for: what is asserted is that the call ends
#: at the deadline, not what the deadline is.
PATIENCE = 0.6

#: How long past the deadline a call is allowed to take before the test calls it a
#: hang. VERY generous, and it costs the test nothing to be: what these tests have
#: to distinguish is "ends at the deadline" from "does not end at all", and the old
#: client did not end -- the probe that established the defect only terminated
#: because the SERVER eventually hung up. So any finite bound discriminates, and a
#: tight one buys no power while making the pin flaky on a machine under load. This
#: repo's own suite has run at a load average near a hundred beside other agents,
#: where four seconds of scheduling delay is ordinary and means nothing about the
#: client.
SLACK = 15.0

CEILING = 32768
RESPONSE_TOKENS = 512
DOSSIER = b'{"dossier": "x"}'


class _Server:
    """A loopback server that answers exactly one request, badly, on purpose.

    `behave` is handed the accepted socket and does whatever this test's sabotage
    is. It runs on a thread so the client can block against it; `stop` is set when
    the test is done, so a thread stuck in its own `sleep` loop leaves.
    """

    def __init__(self, behave):
        self._behave = behave
        self.stop = threading.Event()
        self._listener = socket.socket()
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(1)
        self.port = self._listener.getsockname()[1]
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def _serve(self) -> None:
        self._listener.settimeout(PATIENCE + SLACK)
        try:
            accepted, _ = self._listener.accept()
        except OSError:  # the test finished before a client arrived
            return
        with accepted:
            try:
                self._behave(accepted, self.stop)
            except OSError:
                # The client hung up at its deadline, which is the whole point.
                pass

    def close(self) -> None:
        self.stop.set()
        self._listener.close()
        self._thread.join(timeout=SLACK)


@pytest.fixture
def server(request):
    made = []

    def start(behave) -> _Server:
        running = _Server(behave)
        made.append(running)
        return running

    yield start
    for running in made:
        running.close()


def _invoke(base_url: str):
    return ollama_invoke(
        model_target=TARGET, base_url=base_url,
        max_response_tokens=RESPONSE_TOKENS, context_ceiling=CEILING,
        timeout_seconds=PATIENCE)


def _timed(base_url: str) -> tuple[OllamaRanOutOfTime, float]:
    """Call, and give back the refusal and the wall-clock the call actually took."""
    started = time.monotonic()
    with pytest.raises(OllamaRanOutOfTime) as raised:
        _invoke(base_url)(DOSSIER)
    return raised.value, time.monotonic() - started


def _read_the_request(accepted: socket.socket) -> None:
    """Drain the client's POST so the server is genuinely mid-conversation."""
    accepted.settimeout(PATIENCE + SLACK)
    seen = b""
    while b"\r\n\r\n" not in seen:
        piece = accepted.recv(4096)
        if not piece:
            return
        seen += piece
    length = 0
    for line in seen.split(b"\r\n\r\n", 1)[0].split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            length = int(line.split(b":", 1)[1])
    body = seen.split(b"\r\n\r\n", 1)[1]
    while len(body) < length:
        piece = accepted.recv(4096)
        if not piece:
            return
        body += piece


def test_a_server_that_accepts_and_never_sends_a_byte_runs_out_of_time(server):
    """SABOTAGE: the connection is established and no byte of a reply ever comes.

    This is the shape `104` §18.22 found by hand: an ESTABLISHED connection to a
    server that is not working. The client must give up at its own deadline and say
    which phase it gave up in -- `WAITING_FOR_THE_FIRST_BYTE`, because the request
    went out and nothing came back -- rather than waiting on a socket that is
    perfectly healthy and simply silent.
    """
    def silent(accepted, stop):
        _read_the_request(accepted)
        stop.wait(PATIENCE + SLACK)

    refusal, took = _timed(server(silent).base_url)

    assert took < PATIENCE + SLACK, (
        "a call to a server that sends nothing has to end at the deadline")
    # THE CLASS AND NOT THE MESSAGE, because the class is what survives into the
    # record: `transport._client_exception_explanation` keeps `type(exc).
    # __qualname__` and drops the text (§8.4 property 4), and `104` §18.22 read
    # r19's failures out of exactly that column.
    assert isinstance(refusal, OllamaRanOutOfTimeWaitingForTheFirstByte)
    assert WAITING_FOR_THE_FIRST_BYTE in str(refusal)
    assert f"{PATIENCE:g} seconds" in str(refusal)


def test_a_server_that_sends_headers_and_stalls_mid_body_runs_out_of_time(server):
    """SABOTAGE: the status line and headers arrive, then the body stops halfway.

    A `Content-Length` is promised and half of it is sent. `http.client` will wait
    for the rest for as long as the rest takes to arrive, which is for ever. The
    deadline has to cover the body and not merely the wait for the first byte, or
    a server that has started answering can hold a run indefinitely by never
    finishing.
    """
    def stall_mid_body(accepted, stop):
        _read_the_request(accepted)
        promised = json.dumps({"message": {"role": "assistant",
                                           "content": '{"claims":[]}'},
                               "done": True,
                               "done_reason": "stop"}).encode("utf-8")
        accepted.sendall(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: " + str(len(promised)).encode("ascii") +
            b"\r\n\r\n" + promised[:len(promised) // 2])
        stop.wait(PATIENCE + SLACK)

    refusal, took = _timed(server(stall_mid_body).base_url)

    assert took < PATIENCE + SLACK, (
        "a body that stops halfway must not outlive the deadline: the answer is "
        "never going to arrive and the run is waiting for the rest of it")
    assert isinstance(refusal, OllamaRanOutOfTimeReadingTheBody)
    assert READING_THE_BODY in str(refusal)


def test_a_server_that_dribbles_a_byte_forever_still_ends_at_the_deadline(server):
    """SABOTAGE THAT NAMES THE DEFECT: a byte every quarter of the patience.

    **The other two tests pass against the broken client.** An idle timer fires on
    silence, and both of them are silent. This one is never silent: a byte arrives
    four times per patience, so every `recv` returns promptly and `socket.settimeout`
    is satisfied for ever. Under `urlopen(timeout=...)` this call runs until the
    server gets bored, which is what `104` §18.22 measured at twenty-six minutes
    against a six-hundred-second patience.

    The assertion is therefore about WALL-CLOCK and not only about the exception:
    a client that raised the right error after ten minutes would still be the
    defect. It has to end at the deadline.
    """
    def dribble(accepted, stop):
        _read_the_request(accepted)
        # A length nothing will ever reach, so the client is always owed more.
        accepted.sendall(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            b"Content-Length: 1000000\r\n\r\n")
        while not stop.wait(PATIENCE / 4):
            accepted.sendall(b" ")

    refusal, took = _timed(server(dribble).base_url)

    assert took < PATIENCE + SLACK, (
        f"the call took {took:.1f}s against a deadline of {PATIENCE:g}s. A body "
        f"that keeps arriving satisfies an idle timer for ever, which is why "
        f"`104` R-175 is a DEADLINE and not a shorter timeout")
    assert READING_THE_BODY in str(refusal)
    assert isinstance(refusal, OllamaRanOutOfTime), (
        "it is recorded the way the existing failure is recorded -- P8 writes "
        "`client_raised` off an `OllamaRanOutOfTime` -- and every `except` and "
        "`isinstance` upstream still catches the phase-named subclass")


def test_every_phase_of_a_call_has_a_class_because_the_class_is_what_is_kept():
    """The deadline covers CONNECTING too, and each phase is a name in the record.

    A pin on the vocabulary rather than on a hung connect, which cannot be provoked
    on loopback without a firewall: `104` R-175 asks for one deadline over connect,
    first byte and the full body, and these constants are where a reader checks
    that all four are accounted for.

    **And each is a CLASS.** `transport._client_exception_explanation` reduces a
    client exception to its type name and drops the message, so a phase that lived
    only in a sentence would be a phase the `llm_call_failure` row cannot say --
    which is the unattributable failure R-175 exists to end.

    SABOTAGE: add a fifth phase to `_post` and no class for it. `model_ollama`
    fails to import, rather than recording a timeout that names nothing.
    """
    assert CALL_PHASES == (CONNECTING, SENDING_THE_REQUEST,
                           WAITING_FOR_THE_FIRST_BYTE, READING_THE_BODY)
    assert tuple(RAN_OUT_OF_TIME_IN) == CALL_PHASES
    for phase, kind in RAN_OUT_OF_TIME_IN.items():
        assert issubclass(kind, OllamaRanOutOfTime), phase
        # The name alone has to be readable as the phase, because the name alone
        # is what the durable record keeps.
        assert kind.__qualname__ != OllamaRanOutOfTime.__qualname__
        assert kind.__qualname__.startswith(OllamaRanOutOfTime.__qualname__)

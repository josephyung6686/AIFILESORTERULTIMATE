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
    SENDING_THE_REQUEST, WAITING_FOR_THE_FIRST_BYTE, WENT_SILENT,
    OllamaRanOutOfTime, OllamaRanOutOfTimeReadingTheBody,
    OllamaRanOutOfTimeWaitingForAToken,
    OllamaRanOutOfTimeWaitingForTheFirstByte, assemble, ollama_invoke,
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

#: `104` R-177 GAVE THE CALL A SECOND CLOCK, AND THESE TESTS SEPARATE THEM.
#: Every pin above is about the whole-call ceiling, so each of them injects a
#: silence deadline far enough beyond that ceiling that the ceiling is always the
#: nearer of the two -- otherwise a server that is merely SILENT would end under
#: R-177's class and R-175's three pins would stop pinning R-175.
QUIET_BEYOND_THE_CEILING = PATIENCE * 8

#: And the R-177 pins turn the pair around: a silence deadline a test can wait
#: for, under a whole-call ceiling far enough above it that "ended at the silence
#: deadline" and "ended at the ceiling" are different measurements. The ceiling has
#: to exceed `QUIET + SLACK`, or a call held to the ceiling would still satisfy the
#: assertion and the pin would pass against a client that has no silence deadline
#: at all.
QUIET = 4.0
WHOLE_CALL_PATIENCE = 30.0

#: How long a sabotaging server stays at its post: past the longest deadline any
#: test here injects, because the server has to still be misbehaving at the moment
#: the client gives up. That moment is the measurement.
SERVER_WAIT = WHOLE_CALL_PATIENCE + SLACK

CEILING = 32768
RESPONSE_TOKENS = 512
DOSSIER = b'{"dossier": "x"}'

#: The answer, in the pieces `stream: true` delivers it in. `104` R-177: one JSON
#: object per token, the last one carrying `done`, `done_reason` and the counts.
TOKENS = ('{"cla', 'ims"', ':[', ']', '}')
ANSWER = "".join(TOKENS)

#: Small enough to stay under `_upper_bound(len(DOSSIER))`, which is what the
#: transport's truncation receipt checks; this file is not about that receipt.
PROMPT_TOKENS_READ = 8


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
        self._listener.settimeout(SERVER_WAIT)
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


def _invoke(base_url: str, *, timeout: float = PATIENCE,
            silence: float = QUIET_BEYOND_THE_CEILING, on_usage=None):
    return ollama_invoke(
        model_target=TARGET, base_url=base_url,
        max_response_tokens=RESPONSE_TOKENS, context_ceiling=CEILING,
        timeout_seconds=timeout, silence_seconds=silence, on_usage=on_usage)


def _timed(base_url: str, **deadlines) -> tuple[OllamaRanOutOfTime, float]:
    """Call, and give back the refusal and the wall-clock the call actually took."""
    started = time.monotonic()
    with pytest.raises(OllamaRanOutOfTime) as raised:
        _invoke(base_url, **deadlines)(DOSSIER)
    return raised.value, time.monotonic() - started


def _line(**fields) -> bytes:
    return json.dumps(fields).encode("utf-8") + b"\n"


def _token_line(token: str) -> bytes:
    return _line(model="qwen3:8b",
                 message={"role": "assistant", "content": token}, done=False)


def _last_line() -> bytes:
    """The line that ends a stream: an empty token, and every count on it."""
    return _line(model="qwen3:8b",
                 message={"role": "assistant", "content": ""},
                 done=True, done_reason="stop",
                 prompt_eval_count=PROMPT_TOKENS_READ, eval_count=len(TOKENS))


def _streamed() -> list[bytes]:
    return [_token_line(token) for token in TOKENS] + [_last_line()]


def _in_one_piece() -> bytes:
    """The same reply as `stream: false` sent it: one object, the answer whole."""
    return _line(model="qwen3:8b",
                 message={"role": "assistant", "content": ANSWER},
                 done=True, done_reason="stop",
                 prompt_eval_count=PROMPT_TOKENS_READ, eval_count=len(TOKENS))


def _headers(length: int) -> bytes:
    return (b"HTTP/1.1 200 OK\r\nContent-Type: application/x-ndjson\r\n"
            b"Content-Length: " + str(length).encode("ascii") + b"\r\n\r\n")


#: A length nothing will ever reach, so a client reading this body is always owed
#: more and stops only because a deadline says so.
NEVER_FINISHED = b"HTTP/1.1 200 OK\r\nContent-Type: application/x-ndjson\r\n" \
                 b"Content-Length: 1000000\r\n\r\n"


def _read_the_request(accepted: socket.socket) -> None:
    """Drain the client's POST so the server is genuinely mid-conversation."""
    accepted.settimeout(SERVER_WAIT)
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
        stop.wait(SERVER_WAIT)

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
        stop.wait(SERVER_WAIT)

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
    # `104` R-177 adds a class and NOT a phase: the four above still partition the
    # call and still spend one budget between them; the silence deadline runs
    # inside the last two of them and is spent from a different, smaller number.
    # It is in the same map because the map's job is "the name the record keeps,
    # for every way a clock can end a call".
    assert tuple(RAN_OUT_OF_TIME_IN) == CALL_PHASES + (WENT_SILENT,)
    for phase, kind in RAN_OUT_OF_TIME_IN.items():
        assert issubclass(kind, OllamaRanOutOfTime), phase
        # The name alone has to be readable as the phase, because the name alone
        # is what the durable record keeps.
        assert kind.__qualname__ != OllamaRanOutOfTime.__qualname__
        assert kind.__qualname__.startswith(OllamaRanOutOfTime.__qualname__)


# --- `104` R-177: the SECOND clock, and it is the token stream's ----------------
#
# **What R-175 left on the table, measured.** The whole-call ceiling above is the
# LOCAL model's patience and it is ten minutes, because a local model answering a
# whole dossier legitimately takes minutes. On 11 Sep 2026 (`104` §18.37) ollama's
# own log showed `qwen3:8b` answering an ordinary call in 35-55 seconds -- a
# ~3,000-token prompt read at ~105 tokens/s, ~255 tokens written at ~11 -- and
# three calls in r23b's first 57 minutes producing NOTHING and being cut by the
# server at the full ten minutes. Thirty of those 57 minutes went to three calls.
# One hang costs what ten ordinary calls cost, and the ceiling cannot tell them
# apart because it is asked the wrong question.
#
# The question that separates them is whether anything has arrived lately, and
# `stream: true` is what makes it askable. These four tests are the four answers:
# a stream assembles to the reply that used to come in one piece; a stream that
# goes quiet ends at the silence deadline and not at the ceiling; a stream that
# keeps trickling is NOT quiet and completes even though it outlives that
# deadline; and a call that produces nothing at all is the same silence as one
# that stops.


def test_a_streamed_reply_is_the_same_answer_as_one_that_came_in_one_piece(
        server):
    """(a) The mechanism changes and the ANSWER does not.

    `stream: true` is a change to the wire and must be a change to nothing else:
    P8 parses these bytes against the response schema, `104` R-14's usage row is
    read off the same counts, and a transport whose answer depended on how the
    reply was framed would make two runs of one corpus disagree for a reason that
    is not about the evidence.

    Both halves are real sockets, and the same answer arrives over each: five
    lines and a terminator on one, the single object `stream: false` used to send
    on the other. What comes out of `invoke` is compared byte for byte.
    """
    def streamed(accepted, stop):
        _read_the_request(accepted)
        body = b"".join(_streamed())
        accepted.sendall(_headers(len(body)) + body)

    def in_one_piece(accepted, stop):
        _read_the_request(accepted)
        body = _in_one_piece()
        accepted.sendall(_headers(len(body)) + body)

    streamed_usage, whole_usage = [], []
    many = _invoke(server(streamed).base_url,
                   on_usage=streamed_usage.append)(DOSSIER)
    one = _invoke(server(in_one_piece).base_url,
                  on_usage=whole_usage.append)(DOSSIER)

    assert many == ANSWER.encode("utf-8")
    assert many == one
    # `104` R-14's row is read off the LAST line's counts and not off a sum of
    # the pieces, which would count the prompt once per token.
    assert streamed_usage == whole_usage
    assert streamed_usage[0].prompt_tokens == PROMPT_TOKENS_READ
    assert streamed_usage[0].completion_tokens == len(TOKENS)


def test_the_pieces_of_a_stream_parse_to_the_reply_that_arrived_whole():
    """(a), at the seam, because the socket test cannot show WHAT was compared.

    `assemble` is the one function that knows the reply came in pieces. Its
    contract is that the object it hands on is the object `stream: false` used to
    hand on -- so the four refusals in `_answer` and the counts in `usage_of` are
    reading exactly what they have always read.

    And on a reply that arrived in ONE piece it is the identity, byte for byte:
    every injected `post` in this product's tests still sends one object, and a
    function that re-shaped those would be changing what those tests measure.

    SABOTAGE: take the counts off the last line and sum them across the pieces
    instead, and the first assertion names it.
    """
    assert assemble(b"".join(_streamed())) == json.loads(_in_one_piece())

    whole = _in_one_piece()
    assert assemble(whole) == json.loads(whole)
    assert json.dumps(assemble(whole)).encode("utf-8") + b"\n" == whole


def test_a_stream_that_goes_quiet_ends_at_the_silence_deadline(server):
    """(b) SABOTAGE, AND THE ONE R-177 IS ABOUT: one token, then nothing.

    The server answers, so the call is past every phase the ceiling could catch it
    in early; then the generation stops. Under R-175 alone this call runs to the
    whole-call ceiling -- which is what §18.37 measured three times at ten minutes
    each -- and the assertion here is WALL-CLOCK for that reason: a client that
    raised the right class after the ceiling would still be the defect.

    The ceiling injected here is far enough above the silence deadline that
    "ended at the silence deadline" and "ended at the ceiling" cannot be confused
    for one another by the measurement.

    And the class is its own, because the class name is the whole of what the
    durable record keeps: `transport._client_exception_explanation` reduces a
    client exception to `type(exc).__qualname__` and drops the message, so a
    silence recorded under the ceiling's class would be r23b's three hangs and
    r22's seven over-ceiling calls counted as one number.
    """
    def quiet_after_one_token(accepted, stop):
        _read_the_request(accepted)
        accepted.sendall(NEVER_FINISHED + _token_line(TOKENS[0]))
        stop.wait(SERVER_WAIT)

    refusal, took = _timed(server(quiet_after_one_token).base_url,
                           timeout=WHOLE_CALL_PATIENCE, silence=QUIET)

    assert took < QUIET + SLACK, (
        f"the call took {took:.1f}s against a silence deadline of {QUIET:g}s and "
        f"a whole-call ceiling of {WHOLE_CALL_PATIENCE:g}s. `104` R-177: a "
        f"generation that has produced nothing since its first token is a hang, "
        f"and waiting it out to the ceiling costs ten ordinary calls")
    assert isinstance(refusal, OllamaRanOutOfTimeWaitingForAToken)
    assert not isinstance(refusal, OllamaRanOutOfTimeReadingTheBody), (
        "the two clocks must not share a class: the durable failure row keeps the "
        "class name and nothing else")
    assert WENT_SILENT in str(refusal)
    # The SILENCE deadline's seconds, not the ceiling's: a number read against
    # the wrong clock is a number that invites the wrong subtraction.
    assert f"{QUIET:g} seconds" in str(refusal)


def test_a_call_that_produces_nothing_at_all_ends_at_the_silence_deadline(
        server):
    """(d) The same silence, arriving before the first token instead of after it.

    This is the hang §18.37 measured -- ollama accepted the request and answered
    HTTP 500 ten minutes later, having produced no token at all. The silence clock
    therefore starts when the REQUEST IS AWAY and not at the first token: "nothing
    since we asked" and "nothing since the last token" are the same fact about the
    generation and get the same class.

    The contrast with
    `test_a_server_that_accepts_and_never_sends_a_byte_runs_out_of_time` is the
    whole point and is deliberate: that pin is the same sabotage with the CEILING
    nearer, and it still ends under the ceiling's own class. Which clock ends a
    call is the deployment's two numbers, and the record says which one did.
    """
    def nothing_at_all(accepted, stop):
        _read_the_request(accepted)
        stop.wait(SERVER_WAIT)

    refusal, took = _timed(server(nothing_at_all).base_url,
                           timeout=WHOLE_CALL_PATIENCE, silence=QUIET)

    assert took < QUIET + SLACK, (
        f"the call took {took:.1f}s against a silence deadline of {QUIET:g}s; a "
        f"generation that never starts must not be charged the whole-call "
        f"ceiling of {WHOLE_CALL_PATIENCE:g}s")
    assert isinstance(refusal, OllamaRanOutOfTimeWaitingForAToken)
    assert not isinstance(refusal, OllamaRanOutOfTimeWaitingForTheFirstByte)


def test_a_stream_that_keeps_trickling_is_not_silent_and_completes(server):
    """(c) THE TEST THAT STOPS THE SILENCE DEADLINE BEING A SECOND CEILING.

    Every token resets the clock, so a reply that keeps arriving is not silent
    however long it takes in total. This one takes longer than the silence
    deadline -- deliberately, and the `took > QUIET` assertion is what says so --
    and it completes, with the answer whole.

    A client that spent the silence deadline as a whole-call deadline would pass
    (b) and (d) and fail here, which is the confusion worth pinning: R-176's rule
    is *silence ends at the deadline, a trickle within twice it is allowed*, and
    the local model this exists for writes at about eleven tokens a second over
    answers of a couple of hundred tokens. Every ordinary call is a trickle by
    this test's standard.

    SABOTAGE: arm the silence deadline once when the request goes out instead of
    resetting it per line, and this goes red while (b) and (d) stay green.
    """
    gap = QUIET / 4

    def trickle(accepted, stop):
        _read_the_request(accepted)
        lines = _streamed()
        accepted.sendall(_headers(sum(len(line) for line in lines)))
        for line in lines:
            if stop.wait(gap):
                return
            accepted.sendall(line)

    started = time.monotonic()
    answer = _invoke(server(trickle).base_url,
                     timeout=WHOLE_CALL_PATIENCE, silence=QUIET)(DOSSIER)
    took = time.monotonic() - started

    assert answer == ANSWER.encode("utf-8")
    assert took > QUIET, (
        f"the trickle finished in {took:.1f}s, inside the {QUIET:g}s silence "
        f"deadline, so this run did not measure what it claims to: it has to "
        f"outlive that deadline while never being silent for it")
    assert took < WHOLE_CALL_PATIENCE

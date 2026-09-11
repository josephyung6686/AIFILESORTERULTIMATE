# src/readers/model_ollama.py
"""`ModelClient.invoke` backed by a user-installed local model (ollama).

**Which of §8.4's four modes this is.** P7 names them and this is the second,
verbatim: *"Local extraction plus a USER-INSTALLED LOCAL LLM for eligible
dossiers."* The `ModelTarget` a caller pairs with this transport therefore carries
`locality="local"`, and that value is what P7's release ledger and §8.4's audit
record both store about where the data went. Nothing here reaches beyond loopback.

**The bytes are passed through unchanged, and that is the contract.** P8 assembles
the model-visible bytes -- the authored prompt, the response schema, and the
evidence P7 actually released -- and hands them to `invoke`. This module puts them
in front of the model and returns what came back. It repairs nothing and rewrites
nothing: a transport that edited the request would mean the release ledger recorded
one thing and the model saw another, which is the failure P7's whole audit trail
exists to make impossible, and a transport that repaired the REPLY would be
validating it in the one place that holds no evidence to validate it against.

**`/api/chat`, and the endpoint is the decision.** `model_deepseek` sends one user
message carrying the payload and nothing beside it; this sends the same shape to
the same kind of endpoint, so the two transports differ in destination and not in
what the model is asked. `/api/generate` was the first spelling here and was
measured out of it: with `think: false` ollama appends `/no_think` to the PROMPT
TEXT, which is visible in the returned `context` tokens -- a sentence added to what
the fingerprint describes. On `/api/chat` the same flag is a request field and the
payload is untouched.

**THINKING IS OFF, AND IT IS OFF AT THE API.** `104` R-18 is a standing finding:
a reasoning model sharing one budget between thinking and writing never starts
writing. Measured on the cloud tier -- four real dossiers, `finish_reason ==
"length"`, the whole 8,192-token ceiling spent, zero answer characters. `qwen3:8b`
thinks by default. Measured here against ollama 0.31.1 on 2026-09-05: the same
prompt with `think` absent came back carrying a full `thinking` block; with
`think: false` it came back with none, on both `/api/chat` and `/api/generate`, and
on `qwen2.5:3b`, which has no thinking capability at all and accepts the flag
without complaint. So it is sent on every request, and a `thinking` block that
comes back anyway is a refusal rather than an answer: the flag was not honoured,
and this module cannot tell whether what arrived beside it is the whole answer.

**THE CONTEXT WINDOW IS THE ONE THAT LOSES EVIDENCE WITHOUT SAYING SO.** ollama's
`num_ctx` defaults to a small window -- measured 2026-09-05, a ~96,000-character
prompt was truncated to 2,050 tokens -- and the truncation is SILENT. The marker
sentence at the very start of that prompt was cut away and the model answered
confidently with a value that was never in the text. Nothing in the response says
so. That is the worst failure this product can have: not a refusal and not an
abstention, but a fabricated fact about someone's file, citing evidence the model
was never shown, in a system whose entire validator is grounding.

So the window is sent explicitly on every request, and a payload that will not fit
in it is REFUSED BEFORE THE SOCKET rather than truncated into an answer.

**ONE WINDOW FOR THE WHOLE RUN, AND THE MEASUREMENT THAT SETTLED IT.** The first
version of this sized `num_ctx` per request from the payload's own bytes, which is
the memory-frugal answer and the wrong one. ollama holds ONE context length per
loaded model -- `/api/ps` reports it -- so a request naming a different `num_ctx`
UNLOADS AND RELOADS THE MODEL. Measured 2026-09-05: `load_duration` 283.0 seconds on
the call that changed it, against 182.8 seconds of prompt evaluation and 37.5
seconds of answering. A scan is many calls in a row over files whose dossiers differ
in size, so a per-payload window would have paid that reload again and again, for a
saving in KV cache that no scan can spend.

The window is therefore the deployment's ceiling, on every call, unchanged for the
life of the run. That also deletes the rounding and the granularity: there is
nothing left to round.

**A LARGER WINDOW IS NOT A FIX, WHICH IS WHY THE REFUSAL IS THE FIX.** The same
measurement run at `num_ctx` 8,192 and 16,384 truncated at both: the server kept
`num_ctx / 2` prompt tokens each time (2,050, 4,098, 8,194) and answered from
what was left, inventing a different wrong value on each run and never once
saying a word had been dropped. Raising the number only moves where the evidence
is cut. What makes truncation impossible is that the window is sized ABOVE the
prompt -- `BYTES_PER_TOKEN_FLOOR` guarantees the estimate is an upper bound on the
true token count -- so the only way this construction can fail is if a payload
tokenises worse than that floor. `prompt_eval_count` is read back afterwards as
the receipt for exactly that one assumption, and it refuses rather than answers.

**Deterministic.** Temperature zero and a fixed seed, because §8.5's replay
compares two runs over one corpus and a sampling model makes the product's own
evaluation harness meaningless.

**A model that is not running is a refusal, never an empty answer.** `ollama` is a
process the person may simply not have started. Empty bytes would be
indistinguishable from a model that answered with nothing, and §6.10's abstention
reasons have no member for "the call did not happen" -- so an invented empty answer
could file a file on the strength of a model that was never asked.

**No prompt text lives here.** The prompt is `PromptDefinition.template_bytes`,
authored at the composition root and fingerprinted into the audit record. A
sentence added here would be a prompt nobody approved and no record names.

**THE REPLY IS STREAMED, AND THE REASON IS THE HANG (`104` R-177).** R-175 gave
this module one deadline over the whole call, and that deadline is the local
model's: minutes, because a local model answering a whole dossier legitimately
takes minutes. Measured on ollama's own log on 11 Sep 2026 (§18.37): `qwen3:8b`
reads a ~3,000-token prompt at ~105 tokens/s and writes ~255 tokens at ~11
tokens/s -- thirty-five to fifty-five seconds for an ordinary call -- and SOME
calls produce nothing at all and are cut by the server itself at the whole-call
ceiling, ten minutes later. Three of them in r23b's first fifty-seven minutes
cost thirty of those minutes: one hang costs what ten ordinary calls cost.

A whole-call ceiling cannot tell those apart, because it is asked the wrong
question. The question that separates them is *has anything arrived lately*, and
with `stream: false` nothing arrives until everything does -- so there is nothing
to ask. `stream: true` makes the answer a sequence of JSON lines, one per token,
and R-176's rule becomes available here exactly as the cloud client has it:
SILENCE ENDS AT THE DEADLINE, a trickle within twice it is allowed. The whole-call
ceiling stays as the outer bound; the silence deadline is the inner one, reset by
every token, and a call it ends is `OllamaRanOutOfTimeWaitingForAToken` -- its own
class, so the durable failure row says which of the two clocks stopped the call.

**WHAT THE SILENCE DEADLINE COSTS, STATED BECAUSE A BOUND OVERSTATED IS WORSE THAN
A BOUND.** The token stream is legitimately silent for the whole of the prompt
read: ollama sends its first line when the first token is GENERATED, and nothing
before it. At the measured read rate, the silence deadline this deployment injects
(`cli.MODEL_CALL_TIMEOUT_SECONDS`, the same number R-176 spends on the whole cloud
call) buys about nine thousand prompt tokens of patience, and `_fits` admits a
dossier up to the deployment's whole context ceiling -- so a dossier several times
the measured size would be cut while the model was still reading it, and recorded
as a call the model did not answer. The measured ordinary call is well inside it
(twenty-nine seconds of reading), and the ceiling docstring's own measured worst
case -- 8,194 prompt tokens, about seventy-eight seconds of reading -- is inside it
and not by much. Named here rather than guarded by a number this module invented:
what would make the bound wider is a bigger injected number, and `cli.py` is the
only file that picks one.

**And no NUMBER is chosen here.** The response ceiling, the context ceiling, the
whole-call patience and the silence deadline are injected, exactly as
`model_deepseek`'s are: `84` §1's rule is absent means refuse, never guess, and
`src/` picks no numbers. `cli.py` is the only file that picks them.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable
from urllib.parse import urlsplit

if TYPE_CHECKING:  # pragma: no cover - annotation only; no run-time edge
    from privacy.release import ModelTarget

#: The `ModelTarget.provider` value this transport answers to. §8.4 audits "which
#: model received the data"; a target naming another provider would make that
#: record false at the one place in the product where it is written.
PROVIDER: str = "ollama"

#: The one locality a loopback call can honestly claim, and the whole reason this
#: module exists beside the cloud ones. Spelled rather than imported at run time,
#: which is `model_deepseek.CLOUD`'s rule for the same reason; the string is P7's
#: `release.LOCALITIES[0]` and `tests/readers/test_model_ollama.py` asserts they
#: are the same value rather than trusting that they are.
LOCAL: str = "local"

#: Where a deployment names the model and the endpoint. Named so a refusal can say
#: what was missing, and never read from here: a module that reaches for its own
#: configuration can acquire configuration nobody chose to give it. `cli.py` reads
#: the environment and injects both values.
MODEL_NAME: str = "GRAPH_AGENT_LOCAL_MODEL"
BASE_URL_NAME: str = "OLLAMA_BASE_URL"

#: ollama's own default, and the value `cli.py` falls back to when the person has
#: not named one. Loopback, because the locality claim is measured here.
DEFAULT_BASE_URL: str = "http://127.0.0.1:11434"

#: The chat endpoint, appended to whatever loopback endpoint was injected.
CHAT_PATH: str = "/api/chat"

#: The hosts a `locality="local"` claim survives. `Gate.release` is TOLD the
#: locality and cannot measure it; here is where it is a fact, so here is where
#: anything else refuses. A person running ollama on another PORT is ordinary and
#: allowed; a person pointing this at another HOST is making a cloud call wearing
#: a local target.
LOOPBACK_HOSTS: frozenset[str] = frozenset({"127.0.0.1", "localhost", "::1"})

#: BYTES PER TOKEN, AS A FLOOR AND NOT AN AVERAGE. The window has to be big enough
#: for the WORST tokenisation of these bytes, and the dossier's worst parts are its
#: wire handles and content digests -- hex and base64 runs, which tokenise near one
#: token per two or three characters where prose runs nearer four. Two is below
#: every ratio measured on this product's own payloads, so the estimate overshoots
#: and the window is a little larger than needed.
#:
#: Overshooting is the safe direction and undershooting is the unsafe one: too
#: large costs KV cache, too small costs a silently truncated dossier and a fact
#: invented from evidence the model never saw. The receipt below catches an
#: undershoot anyway, by refusing rather than by answering.
BYTES_PER_TOKEN_FLOOR: int = 2

#: What the chat template itself costs on top of the payload -- the role markers
#: and the turn scaffolding ollama wraps the message in. Measured at well under
#: this on both models; it is headroom, not a prediction.
CHAT_TEMPLATE_TOKENS: int = 128

#: The reply field ollama fills when it thought anyway. Its presence is the
#: evidence that `think: false` was not honoured.
THINKING_FIELD: str = "thinking"

#: Where ollama puts the turn it is answering with, and the field inside it that
#: carries the answer. Spelled once because `assemble` joins them across a stream's
#: lines and `_answer` reads them off the joined object: two spellings would let the
#: streamed reply and the read of it drift apart.
MESSAGE_FIELD: str = "message"
CONTENT_FIELD: str = "content"

#: WHAT SEPARATES ONE TOKEN FROM THE NEXT ON THE WIRE. `stream: true` makes
#: `/api/chat` answer in newline-delimited JSON: one object per token, the last of
#: them carrying `done`, `done_reason` and the counts. It is the token boundary and
#: it is therefore also the CLOCK: a newline arriving is the evidence that the
#: generation is still producing, which is the one thing a whole-call ceiling cannot
#: observe (`104` R-177).
NDJSON_END: bytes = b"\n"

#: The only `done_reason` that means the model finished answering, and the same
#: one-member closed set `model_deepseek.FINISHED` is: the failures are the
#: server's to extend and the successes are not.
FINISHED: str = "stop"

#: What this transport asks the model to answer IN, sent as `format` on every
#: request and recorded on the usage row (`104` R-14). Spelled once, because the
#: request and the record must not be able to disagree about it.
RESPONSE_FORMAT: str = "json"

#: THE FOUR PHASES OF ONE LOCAL CALL, IN ORDER, and between them the whole of what
#: `timeout_seconds` has to cover (`104` R-175). They are named rather than left
#: implicit because the failure record has to be able to SAY which one a call died
#: in: r19's 26-minute hang on 10 Sep 2026 was diagnosed from a process tree and a
#: `netstat` line, because the exception the client would have raised -- had one
#: fired -- could say only "it did not answer".
#:
#: The order is also the argument for one deadline over four. Each phase can be the
#: one that never ends, and each can end normally while the next hangs: a server
#: that accepts the connection and sends nothing hangs the third; one that sends
#: headers and stalls hangs the fourth; one that trickles a byte at a time hangs the
#: fourth while satisfying any per-read timer for ever. A budget that is SPENT
#: across all four is the only shape that bounds the call itself.
CONNECTING: str = "connecting"
SENDING_THE_REQUEST: str = "sending the request"
WAITING_FOR_THE_FIRST_BYTE: str = "waiting for the first byte"
READING_THE_BODY: str = "reading the body"
CALL_PHASES: tuple[str, ...] = (
    CONNECTING, SENDING_THE_REQUEST, WAITING_FOR_THE_FIRST_BYTE,
    READING_THE_BODY)

#: THE SECOND CLOCK, AND IT IS NOT A FIFTH PHASE (`104` R-177). The four above
#: partition the whole call and between them spend ONE budget; this one runs inside
#: the last two of them, is reset by every token, and is spent from a DIFFERENT and
#: smaller number. A call can therefore end two ways on a clock -- it outlived the
#: whole-call ceiling, or its token stream went quiet -- and the two are different
#: facts about the model: the first is a model that was working and was slow, the
#: second is a generation that produced nothing, which is the shape §18.37 measured
#: at ten minutes a time.
#:
#: It begins when the request is away, so a reply that never starts is caught by it
#: as well as a reply that stops: "nothing since the last token" and "nothing since
#: we asked" are the same silence and get the same sentence.
WENT_SILENT: str = "waiting for a token"

#: What each deadline is a deadline FOR, written into the sentence the failure
#: carries so the seconds in it cannot be read against the wrong clock.
WHOLE_CALL: str = "the whole call"
THE_TOKEN_STREAM: str = "silence in the token stream"

#: How much of the body is asked for at a time. It is a re-check interval and not a
#: buffer size: the point of reading in pieces is that the deadline is consulted
#: BETWEEN pieces, so a body arriving slowly is cut off at the deadline rather than
#: arriving for ever one satisfied read at a time. One answer from this deployment's
#: models is a few kilobytes, so in practice this is one read.
BODY_CHUNK_BYTES: int = 1 << 16

#: The ports a URL with no port of its own means. Spelled because `http.client`
#: takes the port as an argument and `urlsplit` answers `None` when the endpoint
#: named none; ollama's own default endpoint names 11434 explicitly.
HTTP_PORT: int = 80
HTTPS_PORT: int = 443


class OllamaUnavailable(RuntimeError):
    """The local model could not be reached, so no call happened."""


class OllamaRanOutOfTime(OllamaUnavailable):
    """The model was asked, worked, and did not finish inside our patience.

    A SUBCLASS BECAUSE THE HANDLING IS THE SAME AND THE SENTENCE IS NOT. Either
    way there is no answer and P8 records `client_raised`, so nothing downstream
    needs to tell them apart. But "no call was made" is FALSE here: the request
    reached the model and the model spent real time on it -- measured at about
    170 seconds a file on `qwen3:8b`, which is close enough to any patience worth
    setting that this is an ordinary outcome rather than a broken install. A
    person told to run `ollama serve` when ollama is already running and working
    has been sent to fix the one thing that is not wrong.
    """


class OllamaRanOutOfTimeConnecting(OllamaRanOutOfTime):
    """The deadline expired before the socket to the local server was open."""


class OllamaRanOutOfTimeSendingTheRequest(OllamaRanOutOfTime):
    """The deadline expired while the dossier was still going out."""


class OllamaRanOutOfTimeWaitingForTheFirstByte(OllamaRanOutOfTime):
    """The deadline expired with the request sent and not one byte back.

    THE SHAPE `104` §18.22 FOUND BY HAND. An ESTABLISHED connection to a server at
    0.4% CPU is this class, and until R-175 there was no way for the record to say
    so: the run had to be diagnosed from a process tree.
    """


class OllamaRanOutOfTimeReadingTheBody(OllamaRanOutOfTime):
    """The deadline expired part-way through an answer that never finished.

    A reply that stalls and a reply that trickles land here alike, and both are
    invisible to a per-read timer: the trickle satisfies it for ever.
    """


class OllamaRanOutOfTimeWaitingForAToken(OllamaRanOutOfTime):
    """The token stream said nothing for the silence deadline. `104` R-177.

    THE ROW THAT SEPARATES A HANG FROM A SLOW ANSWER, and a separate class because
    the class name is the whole of what the durable record keeps:
    `transport._client_exception_explanation` reduces a client exception to
    `type(exc).__qualname__` and drops the message, and `llm_call_failure` stores
    that. A silence ended under one class with the ceiling's would be r23b's three
    ten-minute hangs and r22's seven over-ceiling calls counted as one number.

    Still an `OllamaRanOutOfTime`, so every `except` and `isinstance` upstream is
    unchanged and P8 records `client_raised` exactly as before: what happened to
    the file is the same -- no answer, retried next run -- and only the sentence
    and the name are new.
    """


#: PHASE TO THE CLASS THAT NAMES IT, and the reason it is a class per phase rather
#: than a field is the one place the phase has to survive to. `llm_harness.transport.
#: _client_exception_explanation` reduces a client exception to `type(exc).
#: __qualname__` and a status code, deliberately -- §8.4's property 4 says no
#: credential may reach a durable record and there is no way to enumerate every
#: string a library might put in a message, so the MESSAGE IS DROPPED. `104` §18.22
#: read r19's failures as "4 `OllamaRanOutOfTime`", which is exactly that column.
#: A phase carried only in the message would therefore be a phase nobody can read
#: back, which is the defect R-175 is about wearing a fix's clothes.
#:
#: Subclasses and not four unrelated errors: every `except OllamaRanOutOfTime`,
#: every `except OllamaUnavailable` and every `isinstance` upstream still catches
#: them, and a `post` a caller injected that raises the plain `TimeoutError` still
#: gets the base class -- which is the honest record when the phase is unknown.
RAN_OUT_OF_TIME_IN: "MappingProxyType[str, type[OllamaRanOutOfTime]]" = (
    MappingProxyType({
        CONNECTING: OllamaRanOutOfTimeConnecting,
        SENDING_THE_REQUEST: OllamaRanOutOfTimeSendingTheRequest,
        WAITING_FOR_THE_FIRST_BYTE: OllamaRanOutOfTimeWaitingForTheFirstByte,
        READING_THE_BODY: OllamaRanOutOfTimeReadingTheBody,
        # `104` R-177's clock, LAST because it is not one of the phases: the four
        # above partition the call and this one runs inside the last two of them.
        # It is in the same map because the map's job is "the name the record
        # keeps, for every way a clock can end a call", and a silence with no class
        # would be the unattributable failure R-175 exists to end, arriving by the
        # other clock.
        WENT_SILENT: OllamaRanOutOfTimeWaitingForAToken,
    }))

assert tuple(RAN_OUT_OF_TIME_IN) == CALL_PHASES + (WENT_SILENT,), (
    "every phase of a call earns a class, and so does the silence deadline that "
    "runs inside them, because the class name is the whole of what the durable "
    "failure record keeps. One with no class fails to import rather than being "
    "recorded as an unattributed timeout, which is `104` R-175's own defect")


class _OutOfTimeInPhase(TimeoutError):
    """The one deadline expired, and this is the phase of the call it expired in.

    A `TimeoutError` SUBCLASS AND NOT A NEW KIND, because `ollama_invoke` already
    turns a `TimeoutError` into `OllamaRanOutOfTime` and a caller who replaced
    `post` with a fake that raises the plain one must keep working. It is private
    for the same reason the phases are public: nothing outside this module handles
    it, and everything outside this module reads the sentence it produced.

    `phase` is carried as an ATTRIBUTE rather than only in the message so
    `ollama_invoke` can compose its own sentence around it. `104` R-175: the whole
    reason the phases are named is that the hang could not be attributed, and a
    phase that only ever appears inside a formatted string is one the next reader
    has to parse back out.

    `bound` is which of the two clocks these seconds belong to (`104` R-177). The
    sentence used to say "for the whole call" unconditionally, which would read as a
    lie the moment a second, smaller deadline could also produce this exception: the
    number and what it bounds have to travel together or the record invites the
    wrong subtraction.
    """

    def __init__(self, phase: str, *, timeout: float, elapsed: float,
                 bound: str = WHOLE_CALL):
        super().__init__(
            f"the deadline of {timeout:g} seconds for {bound} expired "
            f"while {phase}, {elapsed:.1f} seconds in")
        self.phase = phase
        self.timeout = timeout
        self.elapsed = elapsed


class OllamaContextExceeded(RuntimeError):
    """The dossier will not fit the window, so it was not sent to be truncated."""


class TargetIsNotThisTransport(RuntimeError):
    """The `ModelTarget` does not describe the call this module would make."""


class ModelVisibleBytesNotText(RuntimeError):
    """The released bytes are not UTF-8 and cannot be sent without altering them."""


class NoAnswerFromModel(RuntimeError):
    """Something came back over HTTP 200 and it is not an answer to the dossier."""


@dataclass(frozen=True, slots=True)
class Usage:
    """What ollama says one call cost, in ollama's own numbers (`104` R-14).

    **Why this is not `model_deepseek.Usage`.** That would be an import from `src/`,
    and this module has none at run time -- the property `model_deepseek`'s own
    `CLOUD` constant cites when it declines to import P7's vocabulary. The two are
    structurally identical on purpose and
    `tests/readers/test_model_ollama_usage.py` asserts it, so a field added to one
    and not the other fails rather than drifts.

    **The two cache columns are always `None` here, and that is the truth rather
    than a gap.** ollama reuses its KV cache across requests whose prompts share a
    prefix -- which is what `104` R-52 and R-58 are both about -- but `/api/chat`
    reports no count for it. A zero would claim nothing was served from cache; a
    `None` says nobody counted. `prompt_eval_count` DOES fall when the cache hits,
    so the effect is visible in the total even though its size is not reported.

    `response_format` is `json` and not `json_object`: it is what this transport
    actually sends in `format`, and the row records what the call was made with.
    """

    model_id: str
    prompt_tokens: int
    completion_tokens: int
    prompt_cache_hit_tokens: int | None
    prompt_cache_miss_tokens: int | None
    response_format: str


def usage_of(response: object, *, model_id: str) -> Usage | None:
    """What ollama reported it spent, or `None` because it reported nothing.

    `None` and never zeroes, for `model_deepseek.usage_of`'s reason: a zero reads as
    "this call cost nothing", which is a claim, where absence is what is known.
    `_answer` already reads `prompt_eval_count` for the truncation receipt and threw
    it away afterwards; this is the same number, kept.
    """
    if not isinstance(response, dict):
        return None
    prompt_tokens = response.get("prompt_eval_count")
    completion_tokens = response.get("eval_count")
    if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
        # Half a number in a cost record is worse than no record, because it will
        # be summed. Reported absent rather than partial.
        return None
    return Usage(
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        prompt_cache_hit_tokens=None,
        prompt_cache_miss_tokens=None,
        response_format=RESPONSE_FORMAT,
    )


def _post(url: str, body: bytes, *, timeout: float, silence: float) -> bytes:
    """The one place this module touches a socket, so a test can replace it.

    **ONE DEADLINE OVER THE WHOLE CALL, and `104` R-175 is why this is no longer
    `urlopen(request, timeout=...)`.** That argument becomes `socket.settimeout`,
    which is an INACTIVITY timer and not a deadline: it bounds one `recv` and
    restarts on the next one. The connect is bounded by it once; the status line,
    the headers and every read of the body are bounded only per-read; and the TOTAL
    is bounded by nothing at all. A server that sends a byte more often than the
    patience -- a trickle, a chunked reply it never terminates -- holds the socket
    for ever while the timer goes on being satisfied.

    That is what r19 sat in on 10 Sep 2026 (`104` §18.22): an ESTABLISHED
    connection to a local server at 0.4% CPU, twenty-six minutes into a call whose
    patience was 600 seconds, in a run where this same client's `OllamaRanOutOfTime`
    had already fired four times. The idle timer was working. There was no deadline
    for it to be a substitute for, and `cli.MODEL_CALL_TIMEOUT_SECONDS` said so in
    its own docstring -- *"A total deadline is a different mechanism and is not
    built here"* -- for the cloud client, which is where the shape was copied from.

    **So the budget is SPENT and never restarted.** `started` is taken once and
    every phase asks `left()` for what remains of it: the connect, the write of the
    request, the wait for the first byte, and EACH read of the body. A phase that
    begins with nothing left raises before it blocks; a phase that blocks is given
    only the remainder as its socket timeout. A call therefore cannot outlive
    `timeout` whatever shape the server's silence takes -- silence at the front,
    silence in the middle, or a body that never ends.

    **The phase rides on the exception**, because R-175 was diagnosed from a
    process tree rather than from a message. `_OutOfTimeInPhase` says which of the
    four the call died in, `ollama_invoke` puts that in the `OllamaRanOutOfTime` it
    raises, and P8 stores that sentence as the `client_raised` explanation exactly
    as it stores the existing one.

    **AND A SECOND, SMALLER DEADLINE INSIDE IT: SILENCE (`104` R-177).** The budget
    above is the local model's whole-call patience and it is minutes long, because a
    local model legitimately takes minutes. A generation that produces NOTHING is
    not slow, and charging it those minutes is what cost r23b thirty of its first
    fifty-seven (§18.37). `silence` is the shorter question -- has a token arrived
    lately -- and `quiet_since` is reset by every one that does, so the two clocks
    together say: this call may take `timeout` overall AND may not go quiet for
    `silence`. Each phase after the request is away is armed with whichever of the
    two remainders is nearer, and `armed` remembers which, because the socket's own
    timer fires with no idea what it was armed from.

    Silence starts when the REQUEST IS AWAY and not at the first token, so a
    generation that never begins is bounded by the same clock as one that stops.
    A token is a newline: `stream: true` makes the body newline-delimited JSON, one
    object per token, so a chunk containing one is proof of progress and a chunk
    without one -- a half-written line, or the dribble `104` §18.22 measured -- is
    not. That is the whole difference from the ceiling, which cannot see progress at
    all and so cannot tell a hang from a long answer.

    **`http.client` and not `urllib.request`, for one reason:** `urlopen` offers
    the caller no seam between connecting, sending and reading, so there is nowhere
    to put a budget. Nothing else about the request changes -- same method, same
    header, same bytes, same endpoint -- because a transport that altered the
    request would mean the release ledger recorded one thing and the model saw
    another.
    """
    from http.client import HTTPConnection, HTTPSConnection
    from time import monotonic

    started = monotonic()
    #: The phase now spending the budget. A cell rather than a name because the
    #: `except` below has to say which phase the socket's own timer fired in, and
    #: it is not the one that raised.
    phase = [CONNECTING]
    #: WHICH OF THE TWO CLOCKS ARMED THE SOCKET, and it is not always the phase:
    #: past the request both are running and the nearer one wins. `104` R-177.
    armed = [CONNECTING]
    #: When the token stream last said anything. Set when the request is away, and
    #: again on every newline that arrives.
    quiet_since = [started]

    def left(next_phase: str) -> float:
        """What is left of the one budget, and the phase about to spend it."""
        phase[0] = next_phase
        armed[0] = next_phase
        remaining = timeout - (monotonic() - started)
        if remaining <= 0:
            raise _OutOfTimeInPhase(next_phase, timeout=timeout,
                                    elapsed=monotonic() - started)
        return remaining

    def quiet_left() -> float:
        """What is left of the silence deadline, measured from the last token."""
        waited = monotonic() - quiet_since[0]
        remaining = silence - waited
        if remaining <= 0:
            raise _OutOfTimeInPhase(WENT_SILENT, timeout=silence, elapsed=waited,
                                    bound=THE_TOKEN_STREAM)
        return remaining

    def sooner(next_phase: str) -> float:
        """The nearer of the two deadlines, and the one the socket is armed from.

        Both are consulted, so whichever has already expired raises here rather
        than being handed to a socket as a negative patience.
        """
        whole = left(next_phase)
        quiet = quiet_left()
        if quiet < whole:
            armed[0] = WENT_SILENT
            return quiet
        return whole

    def out_of_time() -> _OutOfTimeInPhase:
        """The clock that armed the socket, as the exception that names it."""
        if armed[0] == WENT_SILENT:
            return _OutOfTimeInPhase(WENT_SILENT, timeout=silence,
                                     elapsed=monotonic() - quiet_since[0],
                                     bound=THE_TOKEN_STREAM)
        return _OutOfTimeInPhase(phase[0], timeout=timeout,
                                 elapsed=monotonic() - started)

    parts = urlsplit(url)
    secure = parts.scheme == "https"
    connection = (HTTPSConnection if secure else HTTPConnection)(
        parts.hostname, parts.port or (HTTPS_PORT if secure else HTTP_PORT),
        timeout=left(CONNECTING))
    try:
        try:
            connection.connect()
            sock = connection.sock
            sock.settimeout(left(SENDING_THE_REQUEST))
            connection.request("POST", parts.path or "/", body=body,
                               headers={"Content-Type": "application/json"})
            # THE SILENCE CLOCK STARTS HERE (`104` R-177). The question it asks --
            # has the model produced anything -- is meaningless before the model has
            # been asked, and from this line on it is the same question whether the
            # answer never starts or stops half way.
            quiet_since[0] = monotonic()
            sock.settimeout(sooner(WAITING_FOR_THE_FIRST_BYTE))
            response = connection.getresponse()
            chunks: list[bytes] = []
            # `read1` AND NOT `read`, AND THE DIFFERENCE IS THE WHOLE FIX. Both
            # `response.read()` and `response.read(n)` sit on a `BufferedReader`,
            # which loops on the socket until it has all n bytes or the peer hangs
            # up -- so a body arriving one byte at a time keeps ONE call to `read`
            # blocked for as long as the trickle lasts, and the budget below is
            # never consulted again. `read1` performs at most one underlying read
            # and hands back whatever arrived, which is what puts a deadline check
            # BETWEEN the pieces of a slow body. It returns `b""` at the end of a
            # length-delimited and a chunked body alike, and closes the response
            # when the last byte is in, which is what ends this loop normally.
            while not response.isclosed():
                sock.settimeout(sooner(READING_THE_BODY))
                chunk = response.read1(BODY_CHUNK_BYTES)
                if not chunk:
                    break
                chunks.append(chunk)
                if NDJSON_END in chunk:
                    # A LINE ENDED, SO A TOKEN ARRIVED, so the stream is not silent
                    # and the silence deadline starts again from here. Bytes without
                    # a newline are a line still being written and prove nothing --
                    # which is exactly the dribble that satisfies an idle timer for
                    # ever (`104` §18.22) and must not satisfy this one.
                    quiet_since[0] = monotonic()
        except _OutOfTimeInPhase:
            raise
        except TimeoutError as expiry:
            # The socket's own timer fired inside the remainder it was armed with,
            # which is the same deadline arriving by a different route -- and which
            # of the two deadlines that was is what `armed` remembers.
            raise out_of_time() from expiry
        return b"".join(chunks)
    finally:
        # A call that ran out of time leaves no socket behind. The ESTABLISHED
        # connection in R-175's evidence outlived the call it belonged to, because
        # nothing closed it when the wait was abandoned.
        connection.close()


def _joined(objects: "list[object]", field: str) -> str | None:
    """One field of the message, concatenated across a stream's lines, or `None`.

    `None` and not `""` when no line carried it, because the two say different
    things and `_answer` branches on the difference: a `thinking` field nobody sent
    is `think: false` honoured, and an EMPTY one is a model that opened a thinking
    block and put nothing in it. Absence is reported as absence.
    """
    parts: list[str] = []
    for one in objects:
        message = one.get(MESSAGE_FIELD) if isinstance(one, dict) else None
        piece = message.get(field) if isinstance(message, dict) else None
        if isinstance(piece, str):
            parts.append(piece)
    return "".join(parts) if parts else None


def assemble(raw: bytes) -> object:
    """ollama's streamed reply, read back as the ONE object a whole reply is.

    `104` R-177. With `stream: true` the body is newline-delimited JSON: one object
    per token, each carrying that token in `message.content`, and the LAST carrying
    `done`, `done_reason` and the counts. Everything downstream -- `_answer`'s four
    refusals and `usage_of`'s row -- was written against the single object
    `stream: false` returns, and none of it changes: this is the one function that
    knows the reply arrived in pieces.

    **The last object is the base and the pieces are only joined into it.** No field
    is computed, dropped or reordered: `done_reason`, `prompt_eval_count` and
    `eval_count` are the final line's own, and the only keys replaced are the two
    that were split across lines. So a body that is ONE object -- which is what
    `stream: false` sent, and what every injected `post` in this product's tests
    sends -- assembles to a dict equal to `json.loads` of it, key order included,
    and this function is the identity on the reply it used to receive.

    A malformed line raises `json.JSONDecodeError` exactly where `json.loads(raw)`
    used to, which is the same sentence about the same defect -- and a body cut
    part-way through a line is malformed by that rule, as a truncated single object
    always was. A body cut ON a line boundary -- the deadline fired between tokens,
    or the server hung up between them -- assembles to the complete lines that
    arrived, whose last one carries no `done_reason`, and `_answer` refuses it by
    name rather than certifying part of a document as an answer.
    """
    pieces = [line for line in raw.split(NDJSON_END) if line.strip()]
    if not pieces:
        # Nothing to join. Handed on as it came so an empty body produces the
        # error an empty body has always produced.
        return json.loads(raw)
    objects = [json.loads(piece) for piece in pieces]
    whole = objects[-1]
    if not isinstance(whole, dict) or not isinstance(
            whole.get(MESSAGE_FIELD), dict):
        # Not the shape this reads; `_answer` says so, and says it about the
        # object the server actually finished with.
        return whole
    message = dict(whole[MESSAGE_FIELD])
    for field in (CONTENT_FIELD, THINKING_FIELD):
        across = _joined(objects, field)
        if across is not None:
            message[field] = across
    return {**whole, MESSAGE_FIELD: message}


#: What a timeout says when it cannot say which phase it died in. A `post` a caller
#: injected -- every test fake, and any other transport somebody wires -- raises a
#: plain `TimeoutError`, and the honest sentence about one of those is that the
#: phase is unknown, not a guess at the likeliest one.
PHASE_UNKNOWN: str = "waiting on the call"


def _out_of_time(problem: BaseException, sentence: str) -> OllamaRanOutOfTime:
    """The phase's own class, carrying the phase's own sentence. `104` R-175.

    **TWO CHANNELS FOR ONE FACT, AND THE CLASS IS THE ONE THAT SURVIVES.**
    `llm_harness.transport._client_exception_explanation` reduces a client exception
    to `type(exc).__qualname__` and a status code and DROPS THE MESSAGE, deliberately
    -- §8.4's property 4 forbids a credential reaching a durable record and there is
    no way to enumerate every string a library may produce. That column is what
    `104` §18.22 was reading when it wrote "5 failures (4 `OllamaRanOutOfTime`, 1
    `NoAnswerFromModel`)". So a phase carried only in the message would be a phase
    nobody can read back, and R-175's whole diagnostic cost was that the hang could
    not be attributed: the run had to be taken apart with a process tree and a
    `netstat` line. The class name carries it; the sentence carries the seconds and
    the advice, for the person at the screen.

    `getattr` and not `isinstance`: an injected `post` may raise the plain
    `TimeoutError`, and the base class plus "waiting on the call" is the honest
    record for one of those rather than a guess at the likeliest phase.
    """
    phase = getattr(problem, "phase", None)
    return RAN_OUT_OF_TIME_IN.get(phase, OllamaRanOutOfTime)(
        sentence.replace(PHASE_SLOT, f"died while {phase or PHASE_UNKNOWN}"))


#: Where `_out_of_time` writes the phase into the sentence its caller wrote, so
#: each timeout branch below reads as the one sentence it is and neither has to
#: know how a phase is spelled.
PHASE_SLOT: str = "<phase>"


def _stopped_waiting(problem: BaseException, *, endpoint: str,
                     timeout_seconds: float, silence_seconds: float) -> str:
    """What the person is told, and WHICH CLOCK STOPPED THE CALL. `104` R-177.

    Two sentences and not one with two numbers in it, because the two failures ask
    the person for different things. Outliving the whole-call ceiling is a model
    that was working and was too slow for this deployment's patience -- a bigger
    model on a busier machine -- and the answer is a longer patience or a smaller
    model. Going SILENT is a generation that produced nothing at all, which no
    amount of patience improves: §18.37 measured three of them, each held to the
    full ten-minute ceiling, together costing thirty of r23b's first fifty-seven
    minutes.

    A `post` a caller injected raises the plain `TimeoutError`, which carries no
    phase, and the honest sentence about one of those is the whole call's: nothing
    observed a token stream, so nothing may claim one went quiet.
    """
    if getattr(problem, "phase", None) == WENT_SILENT:
        return (
            f"the local model at {endpoint} was asked and then said nothing for "
            f"{silence_seconds:g} seconds -- no token at all -- so this run "
            f"stopped waiting ({PHASE_SLOT}: {problem}). The call HAPPENED and "
            f"ollama is running; a generation that produces no token for that "
            f"long has hung, and waiting it out to the whole-call ceiling of "
            f"{timeout_seconds:g} seconds costs what ten ordinary calls cost. "
            f"Nothing was decided on the strength of a judgement that was never "
            f"finished, and this file is asked again on the next run.")
    return (
        f"the local model at {endpoint} was asked and had not answered "
        f"after {timeout_seconds:g} seconds, so this run stopped waiting "
        f"({PHASE_SLOT}: {problem}). The call HAPPENED -- ollama "
        f"is running and was working -- and no answer came back, so "
        f"nothing was decided on the strength of a judgement that was "
        f"never finished. A bigger model on a busy machine is the ordinary "
        f"cause; raise the deployment's patience or name a smaller model.")


def _require_loopback(base_url: str | None) -> str:
    """The locality claim, checked where it is a fact and nowhere else."""
    if not isinstance(base_url, str) or not base_url.strip():
        raise TargetIsNotThisTransport(
            f"no ollama endpoint was injected. Set {BASE_URL_NAME} in the "
            f"environment this run starts from, or leave it unset for "
            f"{DEFAULT_BASE_URL}; `cli.py` reads it and passes it in, because a "
            f"module that reaches for its own configuration can acquire "
            f"configuration nobody chose to give it.")
    endpoint = base_url.strip().rstrip("/")
    host = (urlsplit(endpoint).hostname or "").lower()
    if host not in LOOPBACK_HOSTS:
        raise TargetIsNotThisTransport(
            f"the endpoint {endpoint!r} is not loopback, and this transport's "
            f"whole claim is that it is: its `ModelTarget` says "
            f"locality={LOCAL!r}, §8.4's `offline` mode is 'No content leaves the "
            f"device', and `Gate.release` is TOLD the locality rather than able to "
            f"measure it. A request to {host!r} carrying a local target would be "
            f"authorized by a policy that says it cannot happen. The PORT is "
            f"yours; the host is the claim. Loopback is {sorted(LOOPBACK_HOSTS)}.")
    return endpoint


def _require_target(model_target: "ModelTarget") -> None:
    if model_target.provider != PROVIDER:
        raise TargetIsNotThisTransport(
            f"model_target.provider is {model_target.provider!r}; this transport "
            f"calls {PROVIDER!r}. §8.4 audits which model received the data, and a "
            f"target naming a provider this module does not call makes that record "
            f"false where it is written.")
    if model_target.locality != LOCAL:
        raise TargetIsNotThisTransport(
            f"model_target.locality is {model_target.locality!r}; a call to a "
            f"process on this machine is {LOCAL!r}. A cloud target pointed at this "
            f"transport would have the gate deciding about one destination while "
            f"the bytes went to another -- `model_deepseek` refuses the mirror of "
            f"this for the mirror of this reason.")
    if not model_target.model_id:
        raise TargetIsNotThisTransport(
            "model_target.model_id names which model is asked, and §8.4 requires "
            "the audit record show it")


def _positive(value: object, name: str, why: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} is injected and is {why}; {value!r} is not a "
                         f"number this deployment could have chosen. `cli.py` is "
                         f"the only file that picks it.")
    return value


def _upper_bound(prompt_bytes: int) -> int:
    """The most tokens these bytes can be, if the floor holds. Spelled once,
    because the window is sized from it and the receipt checks it: two
    spellings would let the guarantee and its proof drift apart."""
    return -(-prompt_bytes // BYTES_PER_TOKEN_FLOOR) + CHAT_TEMPLATE_TOKENS


def _fits(prompt_bytes: int, *, max_response_tokens: int,
          context_ceiling: int) -> None:
    """Refuse a payload the run's one window cannot hold. Never a smaller window.

    Room for the prompt AND the answer: `num_ctx` bounds both, so a window that
    fits only the prompt makes the server drop the front of the prompt to leave
    room for the reply -- which is the silent truncation, arrived at by arithmetic
    instead of by default.
    """
    needed = _upper_bound(prompt_bytes) + max_response_tokens
    if needed > context_ceiling:
        raise OllamaContextExceeded(
            f"this dossier needs a context window of about {needed} tokens "
            f"({prompt_bytes} bytes of prompt, plus {max_response_tokens} for the "
            f"answer) and this deployment's window is {context_ceiling}. It was "
            f"NOT sent: ollama truncates a prompt that exceeds `num_ctx` and says "
            f"nothing, so what came back would be an answer about evidence the "
            f"model never saw, cited to a span that had been cut away. Measured "
            f"2026-09-05: a 96,000-character prompt became 2,050 tokens and the "
            f"model invented the value it was asked for. A refusal leaves the "
            f"file's fields open; a truncated call fills them with fiction.")


def ollama_invoke(*, model_target: "ModelTarget", base_url: str | None,
                  max_response_tokens: int, context_ceiling: int,
                  timeout_seconds: float | None,
                  silence_seconds: float | None,
                  post: Callable[..., bytes] = _post,
                  on_usage: Callable[[Usage | None], None] | None = None,
                  ) -> Callable[[bytes], bytes]:
    """A `ModelClient.invoke`: the model-visible bytes in, the model's answer out.

    Every refusal that can fire at build time fires HERE, before the scan: a
    mislabelled target, a host that is not loopback, a number nobody chose. That
    is `deepseek_invoke`'s rule and the reason is the same -- a deployment that is
    going to refuse should refuse before it has read a person's folder.

    `on_usage` is `104` R-14's sink and is optional, exactly as in
    `deepseek_invoke`: a sink and not a return value because `ModelClient.invoke` is
    `Callable[[bytes], bytes]`, called once per ANSWERED call, and handed `None` when
    the server reported no counts -- because "it told us nothing" is itself the
    audit's answer.
    """
    endpoint = _require_loopback(base_url)
    _require_target(model_target)
    response_tokens = _positive(
        max_response_tokens, "max_response_tokens",
        "this deployment's ceiling on what one answer may be")
    ceiling = _positive(
        context_ceiling, "context_ceiling",
        "the largest window this machine will hold open for one call")
    if not isinstance(timeout_seconds, (int, float)) or isinstance(
            timeout_seconds, bool) or timeout_seconds <= 0:
        raise ValueError(
            "timeout_seconds is injected and is the deployment's patience; a "
            "client built without one can hold a scan open for ever, and zero is "
            "not patience but a different bug wearing a number.")
    if not isinstance(silence_seconds, (int, float)) or isinstance(
            silence_seconds, bool) or silence_seconds <= 0:
        raise ValueError(
            "silence_seconds is injected and is how long this deployment lets the "
            "model's token stream say NOTHING before the call is abandoned (`104` "
            "R-177). A client built without one charges every hang the whole-call "
            "ceiling, which is what ten ordinary local calls cost; zero would "
            "abandon every call before the model had read the prompt. `cli.py` is "
            "the only file that picks it.")
    url = endpoint + CHAT_PATH
    model_id = model_target.model_id
    #: The window every call in this run is given, for the row §8.4 writes about
    #: what the model was given. One value, because changing it reloads the model.
    used: dict[str, int] = {"context_tokens": ceiling}

    def invoke(payload: bytes) -> bytes:
        try:
            # VERBATIM. These are the bytes `transport.issue` recomputed from the
            # prompt definition and the canonical dossier and fingerprinted;
            # anything else would send what the audit record does not describe.
            prompt = payload.decode("utf-8")
        except UnicodeDecodeError as problem:
            raise ModelVisibleBytesNotText(
                "the released bytes are not UTF-8. Repairing them here would send "
                "the model something the stored fingerprint does not describe."
            ) from problem
        # BEFORE the socket, so a dossier that cannot fit is never truncated.
        _fits(len(payload), max_response_tokens=response_tokens,
              context_ceiling=ceiling)
        window = ceiling
        body = json.dumps({
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            # `104` R-177, AND IT IS NOT A SAMPLING CHOICE. Streaming changes
            # nothing the model is asked and nothing it answers -- the same bytes
            # go out, temperature and seed still make the reply deterministic, and
            # `assemble` puts the pieces back into the one object this module has
            # always read. What it buys is the only observation that separates a
            # hang from a long answer: a token arriving.
            "stream": True,
            # P8 parses the reply against `response_schema_bytes`. A model free to
            # answer in prose fails that check for a reason that is not about the
            # evidence, which would read as the model declining when it did not.
            "format": RESPONSE_FORMAT,
            # `104` R-18, sent rather than assumed. See the module docstring.
            "think": False,
            "options": {"temperature": 0, "seed": 1,
                        "num_ctx": window, "num_predict": response_tokens},
        }).encode("utf-8")
        try:
            raw = post(url, body, timeout=timeout_seconds,
                       silence=silence_seconds)
        except OllamaUnavailable:
            raise
        except TimeoutError as problem:
            # THE MODEL WAS ASKED AND IS STILL THINKING, which is not the same as
            # a model that is not there, and telling a person to start a server
            # that is already running would send them to fix the thing that works.
            raise _out_of_time(problem, _stopped_waiting(
                problem, endpoint=endpoint, timeout_seconds=timeout_seconds,
                silence_seconds=silence_seconds)) from problem
        except Exception as problem:  # transport failure of any kind
            # A read timeout can also arrive wrapped, and what it MEANS does not
            # change with the wrapper it arrived in.
            if isinstance(getattr(problem, "reason", None), TimeoutError):
                raise _out_of_time(problem.reason, _stopped_waiting(
                    problem.reason, endpoint=endpoint,
                    timeout_seconds=timeout_seconds,
                    silence_seconds=silence_seconds)) from problem
            raise OllamaUnavailable(
                f"the local model at {endpoint} could not be reached ({problem}). "
                f"Start it with `ollama serve`. No call was made, so nothing was "
                f"decided on the strength of a model that was never asked."
            ) from problem
        # `104` R-177: the pieces of a streamed reply, back in the one object every
        # line below this one was written against.
        response = assemble(raw)
        # AFTER `_answer`, so a refusal is a refusal and not a cost. A `thinking`
        # block, a `done_reason` of `length` and a prompt that tokenised worse than
        # the floor all raise there, and none of them is an answer this run may bill
        # itself for.
        answer = _answer(response, window=window, prompt_bytes=len(payload),
                         response_tokens=response_tokens)
        if on_usage is not None:
            on_usage(usage_of(response, model_id=model_id))
        return answer.encode("utf-8")

    return _Invoke(invoke, used)


class _Invoke:
    """`invoke` plus the one number §8.4's record wants beside it.

    A callable and not a closure, because the audit row needs to read the window
    the call actually used and a bare function has nowhere to put it. It is the
    same object `ModelClient.invoke` holds, so nothing else changes shape.
    """

    __slots__ = ("_call", "_used")

    def __init__(self, call: Callable[[bytes], bytes], used: dict[str, int]):
        self._call = call
        self._used = used

    def __call__(self, payload: bytes) -> bytes:
        return self._call(payload)

    @property
    def context_tokens(self) -> int:
        """The window every call in this run is given. One value, by design."""
        return self._used["context_tokens"]


def _answer(response: object, *, window: int, prompt_bytes: int,
            response_tokens: int) -> str:
    """The model's answer, or a raise. Never a partial and never a substitute."""
    if not isinstance(response, dict):
        raise NoAnswerFromModel(
            f"the server returned {type(response).__name__} where ollama's "
            f"`/api/chat` returns an object. What came back does not describe "
            f"what went out.")
    message = response.get(MESSAGE_FIELD)
    if not isinstance(message, dict):
        raise NoAnswerFromModel(
            f"the response carried no `{MESSAGE_FIELD}` object (keys: "
            f"{sorted(response) if isinstance(response, dict) else '?'}). ollama "
            f"puts the answer there and this module reads it nowhere else.")
    thinking = message.get(THINKING_FIELD)
    if isinstance(thinking, str) and thinking.strip():
        raise NoAnswerFromModel(
            f"the reply carried a `{THINKING_FIELD}` block, so `think: false` was "
            f"not honoured by this ollama and the model spent its budget "
            f"thinking. `104` R-18 is that a reasoning model sharing one budget "
            f"between thinking and writing never starts writing -- measured on "
            f"four real dossiers, the whole ceiling spent and zero answer "
            f"characters. What arrived beside the thinking may be a whole answer "
            f"or what was left, and this module cannot tell which, so it does not "
            f"offer it to be validated as the model's reading of the evidence. "
            f"Upgrade ollama, or name a model that does not think.")
    reason = response.get("done_reason")
    if reason == "length":
        raise NoAnswerFromModel(
            f"the answer was cut off at the injected ceiling "
            f"(done_reason='length', num_predict={response_tokens}), so what came "
            f"back is part of a document. Validated it would be schema-invalid, "
            f"and the rejection would be recorded against the model rather than "
            f"against our ceiling.")
    if reason != FINISHED:
        raise NoAnswerFromModel(
            f"done_reason is {reason!r}, and the only reason that means the model "
            f"finished answering is {FINISHED!r}. A reason this module cannot read "
            f"is a reason it cannot certify as complete.")
    # THE RECEIPT BEHIND THE CONSTRUCTION, and it checks the ONE assumption the
    # construction rests on. `_fits` let this payload through only because the
    # window is above `bytes / BYTES_PER_TOKEN_FLOOR`, which is an upper bound on
    # the prompt's true token count -- so the prompt fits, and truncation cannot
    # happen, UNLESS this payload tokenised worse than that floor. `prompt_eval_count` is what
    # the model actually read, and it is the only way to find that out.
    #
    # Above the bound means the floor was beaten and the window may have been too
    # small for the bytes we sent; ollama would then have silently kept part of
    # the prompt and answered from it. Refused rather than validated: a fact cited
    # to a span that was cut away is a fabrication with a citation on it.
    #
    # A cache hit reports FEWER tokens and never more, so this cannot fire on a
    # prompt that fitted.
    read = response.get("prompt_eval_count")
    if isinstance(read, int) and read > _upper_bound(prompt_bytes):
        raise NoAnswerFromModel(
            f"the model read {read} prompt tokens for {prompt_bytes} bytes of "
            f"dossier, which is above the {_upper_bound(prompt_bytes)} this "
            f"module sized the {window}-token window from. That bound is what "
            f"makes truncation impossible here, so a payload above it is a "
            f"payload the window may not have held -- and ollama truncates "
            f"without saying so. Measured 2026-09-05 at three window sizes: it "
            f"kept num_ctx/2 prompt tokens every time and invented a different "
            f"wrong answer on each. Lower BYTES_PER_TOKEN_FLOOR (now "
            f"{BYTES_PER_TOKEN_FLOOR}) and re-run; the answer is refused rather "
            f"than validated as the model's reading of evidence it may never have "
            f"been shown.")
    text = message.get(CONTENT_FIELD)
    if not isinstance(text, str) or not text.strip():
        raise NoAnswerFromModel(
            f"the response carried no message content (done_reason={reason!r}). "
            f"Empty bytes parse as no claims and would be recorded as a rejected "
            f"model answer; there is no model answer here to reject.")
    return text

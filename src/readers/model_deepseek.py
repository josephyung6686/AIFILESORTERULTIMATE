# src/readers/model_deepseek.py
"""`ModelClient.invoke` backed by DeepSeek's OpenAI-compatible API.

The second cloud transport, beside `model_anthropic.py` and for the same reason:
WHICH provider a deployment calls is a deployment fact, and `src/llm_harness/` is
not allowed to know it. `tests/p8/test_p8_architecture.py` and
`tests/p8/test_p8_transport.py::test_sole_invoke_site_is_transport_issue` both
refuse an SDK import anywhere under `src/llm_harness/`, which is the same rule P5's
SPEC states for readers: a part "adds no third-party runtime dependency".

**Which of §8.4's four modes this is.** The third and fourth: *"Sensitive files
remain local; non-sensitive bounded dossiers may use a cloud LLM"* and *"User
explicitly permits selected corpus areas to use a cloud model."* Under the first
two -- `offline` and `local_model` -- `Gate.release` denies a cloud target with
`mode_forbids_target` and this module is never reached.

**The locality claim is checked HERE, because here is the only place it is a
fact.** `Gate.release` decides by `model_target.locality`; it is TOLD the value and
cannot measure it. An API call over the internet carrying `locality="local"` would
be authorized by `offline`, whose whole text is "No content leaves the device", and
every released dossier would leave under a policy that says it does not.
`model_ollama.py` makes the mirror-image argument for its own side -- "a host
parameter would make that claim unverifiable from the record" -- and this is the
same sentence pointed the other way: the socket is the fact, so the socket's module
is where the claim is measured.

**THE ENDPOINT IS THE SAME CLAIM, and it is the one thing this module must check
that the Anthropic twin need not.** The OpenAI-compatible client defaults its
`base_url` to OpenAI's own endpoint. A DeepSeek transport built with no endpoint
would open a socket to a company the `ModelTarget` does not name, while the release
ledger, §8.4's audit record and the screen all say `deepseek`. That the key would
then be rejected is luck, not design. So an absent endpoint refuses, exactly as an
absent key does: `84` §1's rule is absent means refuse, never guess, and an SDK
default is a guess this module did not make.

**Absent means refuse, and a credential is not an exception.** With no API key this
raises, at the moment the client is built, before the scan starts. It does not
return an `invoke` that answers with nothing: empty bytes parse as no claims,
`llm_harness.sites._claims` returns `None`, and Site A records a REJECT verdict
about a judgement no model ever made. A person told their files were judged when
nothing judged them is the failure the whole part exists to prevent.

**The bytes are passed through unchanged, and that is the contract.** P8 assembles
the model-visible bytes -- the authored prompt, the response schema, and the
evidence P7 actually released -- and `transport.issue` recomputes and fingerprints
them before this is called. This module puts them in front of the model and returns
what came back. It repairs nothing and rewrites nothing.

**No prompt text lives here, and no model behaviour is chosen here.** The prompt is
`PromptDefinition.template_bytes`, authored at the composition root and
fingerprinted into every audit record, fact row and cache key (`76`). Nothing here
sets a system message, a temperature or an `n`: a sentence or a knob added here would
be a prompt nobody approved and no record names. The model id comes from the
`ModelTarget` -- which of `83`'s three tiers this client is, is decided by the
caller -- and the token ceiling is injected; §8.6 names its ceilings "configurable"
and gives no values, so neither is chosen here.

**`response_format` IS SET, and the sentence above used to forbid it (`104` R-14).**
The rule it states is right about what it was written against: a knob that changes
what the model is ASKED is a prompt nobody approved. JSON mode is not that. The
ratified A_fact template already says, in the owner's words, *"answer with one JSON
object and nothing else"*, *"No code fence. No backticks"* and *"The first character
you send is { and the last character you send is }"* -- so the flag makes the
transport ENFORCE the ratified text rather than add to it, and the failure it removes
is one this module already has to raise on: a reasoning model that spends the ceiling
on prose returns something `response_text` can only reject. It also has a
precondition the provider states -- the prompt must contain the word "json" or the
reply comes back empty -- and `request_body` refuses rather than sending under a flag
whose condition it has not met, because an empty reply arrives here as
`NoAnswerFromModel` and is recorded against the model for a mistake made on this side.
THE HONEST GAP: `prompt_fingerprint` hashes the template, its id, the response schema,
the shaping policy and the call site, and no transport parameter, so two runs with and
without this flag are indistinguishable in every audit row. The flag is therefore
carried on the usage record, which is the only place that can say which of the two a
call was.

**What the provider says it spent is read, and it leaves by an injected sink**
(`104` R-14, second half). `actual_cost` in the budget is a constant and no code
observed a token count; `response_text` had the usage block in its hand and dropped
it. `usage_of` reads it -- including DeepSeek's own `prompt_cache_hit_tokens`, which
is the number `104` R-58's prefix work moves and which nothing in the product
recorded. It leaves through `on_usage` rather than the return value because
`ModelClient.invoke` is `Callable[[bytes], bytes]`: widening that contract is
`llm_harness/transport.py`'s, and a reader may not reach into it.

**A provider that declines, an answer cut off at the ceiling, and a reason this
module cannot read are all refusals and never answers.** All arrive over HTTP 200.
`finish_reason == "content_filter"` is the provider declining, which is not the
same as the model answering that the evidence is insufficient -- `00` §3.6 demands
the model be able to say `unknown` and only the model can say it.
`finish_reason == "length"` is our own ceiling, and returned as bytes it would be
validated as the model's reading of the evidence and rejected: the person would be
shown a rejection caused by our token ceiling and attributed to the model. So the
set of finish reasons that mean "an answer" has exactly one member and everything
else raises, including a reason DeepSeek publishes and this module has never seen
(`insufficient_system_resource`) and any the provider adds later.
`transport.issue` catches what `invoke` raises and records a `client_raised`
failure, which says what actually happened.

**ONE DEADLINE OVER THE WHOLE CALL (`104` R-176).** `timeout_seconds` used to
become the SDK's own timeout, which is four per-operation timers: each bounds one
connect, one write or one read and restarts on the next, so a call could legally
take several of them and a reply that kept trickling could take all of them for
ever. On 10 Sep 2026 the internet went for ninety minutes, this client sat on dead
connections, and the run recorded NO failure for seven files it never got an answer
about (§18.28). `_under_one_deadline` now spends ONE budget across the four phases
of a call -- connecting, sending the request, waiting for the first byte, reading
the body -- and a call that runs out raises the phase's own class, so
`transport.issue` records an `llm_call_failure` naming the phase and the run goes on
to the next file. The number is still the deployment's and still `cli.py`'s to pick.

**On retries.** The SDK retries 429s and 5xx by default. Those responses are not
billed and are not answers, so they are not a second call in anything this product
measures: `harness.run_call` reserves one budget call and `transport.issue`
consumes one release per `invoke`, and there is no retry in this module over an
answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Mapping

if TYPE_CHECKING:  # pragma: no cover - annotation only; no run-time edge
    from privacy.release import ModelTarget

#: The `ModelTarget.provider` value this transport answers to. §8.4 audits "which
#: model received the data"; a target naming another provider would make that
#: record false at the one place in the product where it is written.
PROVIDER: str = "deepseek"

#: The one locality an API call over the internet can honestly claim. Spelled
#: rather than imported, so this module keeps `model_ollama.py`'s property of
#: importing nothing from `src/` at run time; the string is P7's
#: `release.LOCALITIES[1]` and `tests/readers/test_model_deepseek.py` asserts they
#: are the same value rather than trusting that they are.
CLOUD: str = "cloud"

#: Where a deployment is expected to keep the key, and where it is expected to
#: name the endpoint. Named so a refusal can say what was missing, and never read
#: from here: a module that reaches for its own credential can acquire one nobody
#: chose to give it. The caller reads the environment and injects both values.
CREDENTIAL_NAME: str = "DEEPSEEK_API_KEY"
BASE_URL_NAME: str = "DEEPSEEK_BASE_URL"

#: The only `finish_reason` that means the model finished answering. A one-member
#: closed set rather than a list of known failures, because the failures are the
#: provider's to extend and the successes are not.
FINISHED: str = "stop"

#: `104` R-14. The provider's own name for "reply with one JSON object", which is
#: what the ratified A_fact template already demands in prose. A mapping proxy so a
#: caller cannot mutate the module's copy of a request term.
JSON_MODE: Mapping[str, str] = MappingProxyType({"type": "json_object"})

#: The provider's stated precondition for `JSON_MODE`, checked rather than assumed.
#: Lower-cased comparison because the ratified template says "JSON" and the provider
#: looks for the word, not the capitalisation.
JSON_WORD: str = "json"

#: THE FOUR PHASES OF ONE CLOUD CALL, IN ORDER, and between them the whole of what
#: `timeout_seconds` has to cover (`104` R-176). They are named rather than left
#: implicit for the reason `model_ollama` names its own four: the failure record has
#: to be able to SAY which one a call died in.
#:
#: WHAT THIS IS FILED AGAINST (`104` §18.28, 10 Sep 2026). The internet dropped for
#: about ninety minutes. This client sat on dead connections and r20 made seven site
#: A dossiers in that window with NO failure recorded, because the number it was
#: given was an inactivity timer and there was no deadline for a call to miss. A run
#: that records nothing is worse than a run that records failures: the person is
#: shown a corpus that was judged when part of it was never asked.
#:
#: The order is also the argument for one deadline over four. Each phase can be the
#: one that never ends, and each can end normally while the next hangs: a provider
#: that accepts the connection and sends nothing hangs the third; one that sends
#: headers and stalls hangs the fourth; one that trickles a byte at a time hangs the
#: fourth while satisfying any per-read timer for ever. A budget that is SPENT across
#: all four is the only shape that bounds the call itself.
#:
#: THE SAME FOUR WORDS AS `model_ollama`, COPIED AND NOT IMPORTED. The two transports
#: share no module -- one speaks `http.client` to loopback, one speaks an SDK to the
#: internet -- and a reader importing another reader would make the local client's
#: vocabulary a run-time dependency of the cloud client's. What R-176 asks them to
#: share is the CONTRACT, and the contract is these four names and one spent budget.
CONNECTING: str = "connecting"
SENDING_THE_REQUEST: str = "sending the request"
WAITING_FOR_THE_FIRST_BYTE: str = "waiting for the first byte"
READING_THE_BODY: str = "reading the body"
CALL_PHASES: tuple[str, ...] = (
    CONNECTING, SENDING_THE_REQUEST, WAITING_FOR_THE_FIRST_BYTE,
    READING_THE_BODY)

#: WHICH PHASE EACH OF THE TRANSPORT LIBRARY'S PER-OPERATION TIMERS IS SPENDING.
#: `httpx` hands a transport a `request.extensions["timeout"]` mapping and httpcore
#: asks it for one number per operation: `pool` before a connection is taken,
#: `connect` around the socket and the TLS handshake, `write` for the request, and
#: `read` for the response headers AND for the body. `read` is therefore the one key
#: that names two phases, and `_Budget` tells them apart by WHEN it is asked: the
#: headers are in by the time the body's timer is armed, and `the_headers_are_in` is
#: called at exactly that point.
#:
#: Spelled as data so the two vocabularies cannot drift apart in silence -- the
#: assertion below refuses to import a mapping naming a phase with no class.
TIMER_PHASE: Mapping[str, str] = MappingProxyType({
    "pool": CONNECTING,
    "connect": CONNECTING,
    "write": SENDING_THE_REQUEST,
    "read": WAITING_FOR_THE_FIRST_BYTE,
})


class ModelCredentialMissing(RuntimeError):
    """No API key was injected, so no call can be made and none was."""


class ModelEndpointMissing(RuntimeError):
    """No endpoint was injected, and the SDK's default is another company."""


class TargetIsNotThisTransport(RuntimeError):
    """The `ModelTarget` does not describe the call this module would make."""


class ModelVisibleBytesNotText(RuntimeError):
    """The released bytes are not UTF-8 and cannot be sent without altering them."""


class NoAnswerFromModel(RuntimeError):
    """Something came back over HTTP 200 and it is not an answer to the dossier."""


class PromptDoesNotAskForJson(RuntimeError):
    """`JSON_MODE` is set and the prompt never says the word the provider needs."""


class ModelRanOutOfTime(RuntimeError):
    """The provider was asked and the whole call did not finish inside our patience.

    A `RuntimeError` like every other refusal in this module, so `transport.issue`
    records it as `client_raised` and the run goes on to the next file. That is the
    whole of what `104` R-176 asks for beyond the deadline itself: the outage of 10
    Sep 2026 produced no failure rows at all, and a file nobody asked about must be
    a file the record NAMES rather than one that quietly reads as judged.

    "No call was made" is FALSE here, exactly as it is for the local twin: the
    request left this device, or was about to. Telling a person their key or their
    endpoint is wrong would send them to fix the thing that is not broken.
    """


class ModelRanOutOfTimeConnecting(ModelRanOutOfTime):
    """The deadline expired before the socket to the provider was open."""


class ModelRanOutOfTimeSendingTheRequest(ModelRanOutOfTime):
    """The deadline expired while the dossier was still going out."""


class ModelRanOutOfTimeWaitingForTheFirstByte(ModelRanOutOfTime):
    """The deadline expired with the request sent and not one byte back.

    THE SHAPE THE OUTAGE MADE (`104` §18.28). A connection opened before the
    internet went and still ESTABLISHED after it went is a socket nothing will ever
    answer on, and until R-176 there was no deadline for it to miss.
    """


class ModelRanOutOfTimeReadingTheBody(ModelRanOutOfTime):
    """The deadline expired part-way through an answer that never finished.

    A reply that stalls and a reply that trickles land here alike, and both are
    invisible to a per-read timer: the trickle satisfies it for ever.
    """


#: PHASE TO THE CLASS THAT NAMES IT, and the reason it is a class per phase rather
#: than a field is the one place the phase has to survive to.
#: `llm_harness.transport._client_exception_explanation` reduces a client exception
#: to `type(exc).__qualname__` and a status code, deliberately -- §8.4's property 4
#: says no credential may reach a durable record and there is no way to enumerate
#: every string an SDK might put in a message, so the MESSAGE IS DROPPED. A phase
#: carried only in the message would therefore be a phase nobody can read back,
#: which is the defect R-176 is about wearing a fix's clothes.
#:
#: Subclasses and not four unrelated errors: every `except ModelRanOutOfTime` and
#: every `isinstance` upstream still catches them, and a `send` a caller injected
#: that raises the plain `TimeoutError` still gets the base class -- which is the
#: honest record when the phase is unknown.
RAN_OUT_OF_TIME_IN: "MappingProxyType[str, type[ModelRanOutOfTime]]" = (
    MappingProxyType({
        CONNECTING: ModelRanOutOfTimeConnecting,
        SENDING_THE_REQUEST: ModelRanOutOfTimeSendingTheRequest,
        WAITING_FOR_THE_FIRST_BYTE: ModelRanOutOfTimeWaitingForTheFirstByte,
        READING_THE_BODY: ModelRanOutOfTimeReadingTheBody,
    }))

assert tuple(RAN_OUT_OF_TIME_IN) == CALL_PHASES, (
    "every phase of a call earns a class, because the class name is the whole of "
    "what the durable failure record keeps. A phase with no class fails to import "
    "rather than being recorded as an unattributed timeout, which is `104` R-176's "
    "own defect")

assert set(TIMER_PHASE.values()) <= set(CALL_PHASES), (
    "every per-operation timer this transport sizes has to be spent under a phase "
    "the record can name, or a timeout arrives with a phase nothing above can read")


class _OutOfTimeInPhase(TimeoutError):
    """The one deadline expired, and this is the phase of the call it expired in.

    A `TimeoutError` SUBCLASS AND NOT A NEW KIND, for the reason its local twin is
    one: `deepseek_invoke` turns a `TimeoutError` into `ModelRanOutOfTime`, and a
    caller who replaced `send` with a fake that raises the plain one must keep
    working. It is private for the same reason the phases are public: nothing
    outside this module handles it, and everything outside this module reads the
    sentence it produced.

    `phase` is carried as an ATTRIBUTE rather than only in the message so
    `deepseek_invoke` can compose its own sentence around it -- a phase that only
    ever appears inside a formatted string is one the next reader has to parse back
    out.
    """

    def __init__(self, phase: str, *, timeout: float, elapsed: float):
        super().__init__(
            f"the deadline of {timeout:g} seconds for the whole call expired "
            f"while {phase}, {elapsed:.1f} seconds in")
        self.phase = phase
        self.timeout = timeout
        self.elapsed = elapsed


class _Budget:
    """ONE BUDGET, SPENT ACROSS THE WHOLE CALL, and the phase now spending it.

    This is what `httpx` is handed as `request.extensions["timeout"]`, and it is a
    live object rather than the dict of four numbers httpx would have put there.
    That dict is the mechanism `104` R-175 indicts: each entry bounds ONE operation
    and restarts on the next, so `connect`, `write` and `read` each get the whole
    patience and a call can legally take three of them -- or, with a body that keeps
    arriving, all of them for ever. Here `get` computes what is LEFT of one budget
    taken once at the top of the call, so every operation httpcore arms is armed
    with the remainder and never with the whole.

    A phase that begins with nothing left raises before it blocks, exactly as
    `model_ollama._post`'s `left()` does.
    """

    def __init__(self, timeout: float) -> None:
        self._timeout = float(timeout)
        self._started = monotonic()
        #: The phase now spending the budget. Kept because the exception raised by
        #: the SOCKET's own timer has to say which phase that timer belonged to,
        #: and it arrives from a library that knows nothing about phases.
        self.phase = CONNECTING
        self._reads_are_the_body = False

    def left(self, phase: str) -> float:
        """What is left of the one budget, and the phase about to spend it."""
        self.phase = phase
        remaining = self._timeout - (monotonic() - self._started)
        if remaining <= 0:
            raise self.expired(phase)
        return remaining

    def expired(self, phase: str | None = None) -> _OutOfTimeInPhase:
        """The deadline, as the exception the record can read the phase off."""
        return _OutOfTimeInPhase(phase or self.phase, timeout=self._timeout,
                                 elapsed=monotonic() - self._started)

    def the_headers_are_in(self) -> None:
        """From here a `read` is the body and no longer the wait for its first byte.

        Called by the transport at the ONE moment that distinction is a fact: when
        `handle_request` has returned, the status line and the headers have arrived
        and the body's own timer has not been armed yet. Reading the two `read`s
        apart by their order rather than by their key is the only seam the library
        offers, and doing it here keeps the guess out of `get`.
        """
        self._reads_are_the_body = True

    def get(self, timer: str, default: float | None = None) -> float:
        """httpcore asking for one operation's timeout, answered with the remainder.

        The signature is `Mapping.get`'s because that is how httpcore asks --
        `request.extensions.get("timeout", {}).get("write", None)` -- and `default`
        is accepted and ignored on purpose: a default here would be a patience this
        module invented, and every operation is spending the one budget.

        A timer this module has no phase for still gets the remainder, under the
        phase already running: an unbounded operation would be the R-176 defect
        returning, and a wrong NAME is a smaller failure than no deadline. The
        import-time assertion above is what keeps the names honest.
        """
        if timer == "read":
            return self.left(READING_THE_BODY if self._reads_are_the_body
                             else WAITING_FOR_THE_FIRST_BYTE)
        return self.left(TIMER_PHASE.get(timer, self.phase))


#: What a timeout says when it cannot say which phase it died in. A `send` a caller
#: injected -- every test fake, and any other transport somebody wires -- raises a
#: plain `TimeoutError`, and the honest sentence about one of those is that the
#: phase is unknown, not a guess at the likeliest one.
PHASE_UNKNOWN: str = "waiting on the call"

#: Where `_out_of_time` writes the phase into the sentence its caller wrote, so the
#: timeout branch below reads as the one sentence it is and does not have to know
#: how a phase is spelled.
PHASE_SLOT: str = "<phase>"


def _out_of_time(problem: BaseException, sentence: str) -> ModelRanOutOfTime:
    """The phase's own class, carrying the phase's own sentence. `104` R-176.

    TWO CHANNELS FOR ONE FACT, AND THE CLASS IS THE ONE THAT SURVIVES.
    `llm_harness.transport._client_exception_explanation` keeps `type(exc).
    __qualname__` and DROPS THE MESSAGE (§8.4 property 4), and that column is what a
    person reads a run's failures out of. The class name carries the phase; the
    sentence carries the seconds and the advice, for the person at the screen.

    `getattr` and not `isinstance`: an injected `send` may raise the plain
    `TimeoutError`, and the base class plus "waiting on the call" is the honest
    record for one of those rather than a guess at the likeliest phase.
    """
    phase = getattr(problem, "phase", None)
    return RAN_OUT_OF_TIME_IN.get(phase, ModelRanOutOfTime)(
        sentence.replace(PHASE_SLOT, f"died while {phase or PHASE_UNKNOWN}"))


@dataclass(frozen=True, slots=True)
class Usage:
    """What the provider says one call cost, in the provider's own numbers.

    `104` R-14: `actual_cost` in the budget is a constant and nothing observed a
    token count. This is the observation; pricing it is a deployment fact and no
    price is invented here, the same rule that keeps the model id and the token
    ceiling injected.

    `prompt_cache_hit_tokens` and `prompt_cache_miss_tokens` are DeepSeek's and are
    optional, because a provider that publishes neither still reports what it
    charged for and that half must survive. They are also the numbers `104` R-58
    moves: without them the frame-first prefix is visible only in a bench, never in
    the product's own audit.
    """

    model_id: str
    prompt_tokens: int
    completion_tokens: int
    prompt_cache_hit_tokens: int | None
    prompt_cache_miss_tokens: int | None
    response_format: str


def request_body(*, model_id: str, max_tokens: int, prompt: str,
                 temperature: float | None = None) -> dict:
    """Every term of the one API call, as data, so the socket line stays the only
    untestable statement in this module.

    `_send` is two statements this project cannot exercise without spending money and
    holding a key, and its docstring says so. What the request SAYS is a different
    question from whether it can be sent, and it is answered here.
    """
    if JSON_WORD not in prompt.lower():
        raise PromptDoesNotAskForJson(
            f"{JSON_MODE['type']!r} is set and the prompt never contains the word "
            f"{JSON_WORD!r}, which is the provider's stated precondition for it. "
            f"Sent anyway the reply comes back empty, arrives here as "
            f"NoAnswerFromModel, and is recorded against the model for a mistake "
            f"made on this side."
        )
    body = {
        "model": model_id,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        # `104` R-14. The module docstring carries the whole argument for why this
        # one knob is not a prompt nobody approved.
        "response_format": dict(JSON_MODE),
        # THINKING OFF (14 Sep 2026). The provider's flash model thinks before it
        # writes unless told not to, and under this module's JSON mode and
        # deadline it answered 96 of 170 judge calls on the owner's corpus with
        # no content at all -- the failure `response_text` names as "a reasoning
        # model that spent the ceiling on `reasoning_content`". The provider's
        # own switch for it is this field (api-docs.deepseek.com, thinking mode);
        # a model that does not think ignores it. Every text this product sends
        # asks for one JSON object and nothing else, which is an answer, not a
        # deliberation.
        "thinking": {"type": "disabled"},
    }
    if temperature is not None:
        # A SAMPLING TERM, NOT A PROMPT TERM, by the reading R-14 gave
        # `response_format`: it changes how the provider draws from one
        # distribution, not what the model is asked. Absent unless a caller
        # names it; the lead's bench names it to measure whether the judge's
        # answers stop moving between runs (18 of 44 re-asked files changed
        # their kind between runs 13 and 15 under the provider's default).
        body["temperature"] = temperature
    return body


def usage_of(response: object, *, model_id: str) -> Usage | None:
    """What the provider reported it spent, or `None` because it reported nothing.

    `None` and never zeroes. A zero reads as "this call cost nothing", which is a
    claim; absence is what is actually known, and `00`'s whole posture on unknowns is
    that the two are different answers.
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return None
    prompt_tokens = getattr(usage, "prompt_tokens", None)
    completion_tokens = getattr(usage, "completion_tokens", None)
    if not isinstance(prompt_tokens, int) or not isinstance(completion_tokens, int):
        # A usage block that cannot say what the call cost is not a usage block.
        # Reported as absent rather than as partial: half a number in a cost record
        # is worse than no record, because it will be summed.
        return None

    def optional(name: str) -> int | None:
        value = getattr(usage, name, None)
        return value if isinstance(value, int) else None

    return Usage(
        model_id=model_id,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        prompt_cache_hit_tokens=optional("prompt_cache_hit_tokens"),
        prompt_cache_miss_tokens=optional("prompt_cache_miss_tokens"),
        response_format=JSON_MODE["type"],
    )


def _under_one_deadline(timeout_seconds: float):
    """An HTTP client whose WHOLE call is bounded by one budget. `104` R-176.

    **WHY THE SEAM IS HERE AND NOT IN A HAND-ROLLED SOCKET.** `model_ollama._post`
    answered R-175 by dropping to `http.client`, because loopback HTTP with no
    credential is a request a reader can honestly build by hand. This path is not
    that: it carries the owner's API key over TLS to another company, and
    hand-rolling that would mean this module authoring its own authentication and
    its own certificate handling on the one line where a mistake is a leaked key.
    So R-176 mirrors R-175's CONTRACT and not its mechanism -- one spent budget,
    four named phases, a class per phase, no leaked socket -- through the seam the
    SDK offers: `OpenAI(http_client=...)` takes any `httpx.Client`, and an
    `httpx.Client` takes any transport.

    **WHAT THE LIBRARY'S OWN TIMEOUT IS, AND WHY IT IS NOT THIS.** `httpx.Timeout`
    is four numbers -- connect, write, read, pool -- and each bounds ONE operation
    and restarts on the next. It bounds a SILENT socket and it does not bound a slow
    one, which is the distinction `cli.MODEL_CALL_TIMEOUT_SECONDS` used to record in
    its own docstring and which the outage turned from a note into seven unrecorded
    files. `_Budget` replaces those four numbers with one budget: httpcore asks it
    for each operation's patience and is answered with what is LEFT.

    **THE BOUND THIS ACTUALLY BUYS, stated exactly, because a bound overstated is
    worse than a bound.** httpcore arms each phase's socket timer ONCE, from the
    number it is handed at the moment that phase begins -- `connect` once for the
    TCP connect and the TLS handshake together, `write` once, `read` once for the
    headers and once for the whole body loop. So:

    * **Silence is bounded by the budget.** Whichever phase goes quiet, its timer
      was armed with the remainder, so the call ends at the deadline. This is the
      outage's own shape and the one that mattered.
    * **A body that keeps arriving is cut BETWEEN chunks.** `_BodyUnderTheDeadline`
      consults the budget before each piece, so a trickle cannot satisfy a per-read
      timer for ever the way `104` §18.22 measured at twenty-six minutes.
    * **The one shape that can overshoot is trickle-then-stall**, and it overshoots
      by at most ONE armed window: the last byte arrives just before the body's read
      timer would have fired, the check passes, and the next read waits out a timer
      that was armed with the remainder at the START of the body. Worst case is
      therefore under twice the deadline, and it is never unbounded.
    * **Name resolution is outside every timer**, here and in any client built on
      `socket.create_connection`: `getaddrinfo` runs before the timeout applies, so
      a dead resolver adds the operating system's own patience to the connecting
      phase. The outage killed one agent on exactly that.

    A tighter bound is reachable only by re-implementing the body reader -- which
    means leaving the SDK, and the key and the TLS with it -- or by a watchdog
    thread per call, which is a second timing mechanism to keep true. Neither is
    worth what it buys over "never unbounded, and silence exact", so the bound above
    is the one this module promises and `tests/readers/test_model_deepseek_deadline`
    is the one that measures it.
    """
    import httpx

    class _BodyUnderTheDeadline(httpx.SyncByteStream):
        """The response body, with the budget consulted between the pieces.

        The check has to be HERE and not only in the timers: httpcore arms the
        body's read timer once, before its loop, so a body that keeps producing
        bytes satisfies that timer for as long as the bytes keep coming. Checking
        between chunks is what turns "no read waited too long" into "the call did
        not outlive its deadline".

        Consulted BEFORE each piece rather than after it, the way `_post`'s
        `read1` loop is written. The one difference from that loop, stated because
        a bound overstated is worse than a bound: `_post` asks whether the response
        is closed before it spends any budget, and this cannot -- there is no way
        to know whether the next piece will read the socket or come out of what h11
        already holds. So the check runs once more after the last piece, at
        effectively the instant the stream reports its end, and a body that
        completed inside the deadline is an answer UNLESS the deadline falls in
        that instant.
        """

        def __init__(self, inner, budget: _Budget) -> None:
            self._inner = inner
            self._budget = budget

        def __iter__(self):
            pieces = iter(self._inner)
            while True:
                self._budget.left(READING_THE_BODY)
                try:
                    piece = next(pieces)
                except StopIteration:
                    return
                except _OutOfTimeInPhase:
                    raise
                except httpx.TimeoutException as expiry:
                    # The socket's own timer fired inside the phase's remainder,
                    # which is the same deadline arriving by a different route.
                    raise self._budget.expired(READING_THE_BODY) from expiry
                yield piece

        def close(self) -> None:
            # A call that ran out of time leaves no socket behind. httpx closes a
            # response whose read raised, and this is the line that carries that
            # through to the connection underneath.
            self._inner.close()

    class _OneBudgetForTheWholeCall(httpx.HTTPTransport):
        """The stock transport, with one budget substituted for its four timers."""

        def handle_request(self, request):
            budget = _Budget(timeout_seconds)
            # The mapping httpx built from its own `Timeout` is REPLACED, not
            # amended: leaving any of its four numbers in place would leave one
            # operation bounded by a patience nobody spent.
            request.extensions["timeout"] = budget
            try:
                response = super().handle_request(request)
            except _OutOfTimeInPhase:
                raise
            except httpx.TimeoutException as expiry:
                raise budget.expired() from expiry
            # The status line and the headers are in and the body's own timer has
            # not been armed yet, which is the one moment a `read` changes meaning.
            budget.the_headers_are_in()
            response.stream = _BodyUnderTheDeadline(response.stream, budget)
            return response

    # `trust_env` is left at its default so a deployment's certificate bundle is
    # still honoured. THE ONE BEHAVIOUR THIS COSTS: httpx reads `HTTPS_PROXY` from
    # the environment only when it builds the transport itself, so a deployment
    # behind an environment-configured proxy now reaches the provider directly.
    # Recorded rather than worked around: nothing in this product sets a proxy, and
    # a proxy option here would be a deployment fact this module invented.
    return httpx.Client(transport=_OneBudgetForTheWholeCall(),
                        timeout=timeout_seconds)


def _send(*, api_key: str, base_url: str, model_id: str, max_tokens: int,
          prompt: str, timeout_seconds: float,
          temperature: float | None = None) -> object:
    """The one place this module touches a socket, so a test can replace it.

    Everything the module does with what comes back is `response_text`, which is
    pure. What this function itself does -- open a socket, spend a budget across
    the four phases of one call, and close what it opened -- is measured against a
    real loopback server in `tests/readers/test_model_deepseek_deadline.py`, which
    is `104` R-176's own answer to the sentence this docstring used to carry: that
    these were statements the project could not exercise. It cannot exercise them
    against the PROVIDER without a key and a bill; it can exercise them against a
    socket, and the defect R-176 records lived in the socket.
    """
    import openai

    # TIMEOUT AND RETRIES ARE BOTH SET, and neither has a default here. The
    # library's own are ten minutes PER ATTEMPT with retries on top, so an
    # unanswered request holds a scan open long past the point a person is still
    # watching -- measured: the test suite stopped dead for ten minutes, twice,
    # with no output, the first time a real client reached a `--enable-cloud`
    # test. §8.6 bounds model SPEND and says nothing about a socket that never
    # answers, so a hung call is not a budget event, not a `budget_deferred` and
    # not a refusal: it is a run over ten thousand files that never finishes.
    #
    # `max_retries=0` because a retry multiplies the wait by a number the caller
    # never chose, and because P8 already owns what happens to a failed call --
    # retrying inside the transport would spend a second call the budget never
    # reserved.
    #
    # THE SAME NUMBER TWICE, AND ONLY ONE OF THEM IS READ BY A SOCKET (`104`
    # R-176). `timeout` is what the SDK puts in the request it builds; the client
    # below replaces it with `_Budget` before any operation is armed, so the number
    # that bounds the call is the budget's. It is still passed because it is the
    # deployment's patience and this is where the SDK asks for it -- a client built
    # with none would be a client whose own defaults are back.
    #
    # BOTH ARE CLOSED, and that is the "no leaked socket" half of R-176. The
    # ESTABLISHED connections the outage left behind outlived the calls they
    # belonged to because nothing closed them when the wait was abandoned.
    with _under_one_deadline(timeout_seconds) as http:
        with openai.OpenAI(
            api_key=api_key, base_url=base_url,
            timeout=timeout_seconds, max_retries=0, http_client=http,
        ) as client:
            return client.chat.completions.create(
                # Every term of the request, built and checked by a pure function
                # so this stays the one statement here that reaches the provider
                # (`104` R-14).
                **_as_the_sdk_takes_it(request_body(model_id=model_id, max_tokens=max_tokens,
                             prompt=prompt, temperature=temperature)),
            )


#: The request terms the SDK has no keyword for, and so takes through
#: `extra_body` -- merged into the same JSON body on the wire, which is why
#: `request_body` still states them and the deadline pin still compares the
#: whole body. `thinking` is the provider's own field (14 Sep 2026).
_PROVIDER_ONLY_TERMS: frozenset[str] = frozenset({"thinking"})


def _as_the_sdk_takes_it(body: dict) -> dict:
    """`request_body`'s dict as `chat.completions.create` accepts it: the
    provider-only terms moved under `extra_body`, everything else as keywords."""
    extra = {key: body[key] for key in _PROVIDER_ONLY_TERMS if key in body}
    kwargs = {key: value for key, value in body.items() if key not in extra}
    if extra:
        kwargs["extra_body"] = extra
    return kwargs


def response_text(response: object) -> str:
    """The model's answer, or a raise. Never a partial and never a substitute."""
    choices = tuple(getattr(response, "choices", ()) or ())
    if len(choices) != 1:
        raise NoAnswerFromModel(
            f"the response carried {len(choices)} choices and this module asks for "
            f"one answer to one dossier. It never sets `n`, so anything else means "
            f"what came back does not describe what went out, and choosing among "
            f"them would be deciding between two readings of the evidence on no "
            f"evidence at all."
        )
    choice = choices[0]
    reason = getattr(choice, "finish_reason", None)
    if reason == "content_filter":
        raise NoAnswerFromModel(
            "the provider declined to answer (finish_reason='content_filter'). "
            "That is not the same as answering that the evidence is insufficient "
            "-- only the model can say the second, and it did not."
        )
    if reason == "length":
        raise NoAnswerFromModel(
            "the answer was cut off at the injected token ceiling "
            "(finish_reason='length'), so what came back is part of a document. "
            "Validated it would be schema-invalid, and the rejection would be "
            "recorded against the model rather than against our ceiling."
        )
    if reason != FINISHED:
        raise NoAnswerFromModel(
            f"finish_reason is {reason!r}, and the only reason that means the model "
            f"finished answering is {FINISHED!r}. A reason this module cannot read "
            f"is a reason it cannot certify as complete, and a partial document "
            f"returned as bytes would be validated as the model's reading of the "
            f"evidence."
        )
    text = getattr(getattr(choice, "message", None), "content", None)
    if not isinstance(text, str) or not text.strip():
        raise NoAnswerFromModel(
            f"the response carried no message content (finish_reason={reason!r}). "
            f"Empty bytes parse as no claims and would be recorded as a rejected "
            f"model answer; there is no model answer here to reject. A reasoning "
            f"model that spent the ceiling on `reasoning_content` arrives here."
        )
    return text


#: WHAT A PERSON IS TOLD WHEN THE DEADLINE EXPIRED. `104` R-176.
#:
#: The ENDPOINT IS NOT IN IT, and that is the one difference from the local twin's
#: sentence. `model_ollama` names its endpoint because that endpoint is loopback and
#: was typed by the person reading the message; this one is whatever
#: `DEEPSEEK_BASE_URL` holds, it is on the path that carries a credential, and §8.4's
#: property 4 is that no credential reaches the screen, a log, an audit record or an
#: exception message. The provider's name says everything the person can act on.
#:
#: `PHASE_SLOT` is filled by `_out_of_time` with the phase the call died in.
_RAN_OUT_OF_TIME: str = (
    "the {provider} model was asked and had not answered after {seconds} seconds, "
    "so this run stopped waiting ({phase}). The call HAPPENED -- the request left "
    "this device -- and no answer came back, so nothing was decided on the strength "
    "of a judgement that was never finished. A network that has gone is the "
    "ordinary cause; the file is recorded as one the model did not answer, and the "
    "run goes on to the next one."
).replace("{phase}", PHASE_SLOT)


def _require_credential(api_key: str | None) -> str:
    if not isinstance(api_key, str) or not api_key.strip():
        raise ModelCredentialMissing(
            f"no {PROVIDER} API key was injected, so no model call can be made. "
            f"Put the key in {CREDENTIAL_NAME} in the environment this run starts "
            f"from and pass it in. This refuses rather than continuing without a "
            f"model: a run that carried on silently would tell the person their "
            f"files were judged when nothing judged them."
        )
    return api_key


def _require_endpoint(base_url: str | None) -> str:
    if not isinstance(base_url, str) or not base_url.strip():
        raise ModelEndpointMissing(
            f"no {PROVIDER} endpoint was injected. This SDK is OpenAI's, and with "
            f"no base_url it calls OpenAI -- a company the ModelTarget does not "
            f"name, while §8.4's audit record, P7's release ledger and the screen "
            f"all say {PROVIDER!r}. Put the endpoint in {BASE_URL_NAME} and pass it "
            f"in; a default chosen by an SDK is not a destination this deployment "
            f"chose."
        )
    return base_url


def _require_target(model_target: ModelTarget) -> None:
    if model_target.provider != PROVIDER:
        raise TargetIsNotThisTransport(
            f"model_target.provider is {model_target.provider!r}; this transport "
            f"calls {PROVIDER!r}. §8.4 audits which model received the data, and a "
            f"target naming a provider this module does not call makes that record "
            f"false where it is written."
        )
    if model_target.locality != CLOUD:
        raise TargetIsNotThisTransport(
            f"model_target.locality is {model_target.locality!r}; a call over the "
            f"internet is {CLOUD!r}. §8.4's `offline` mode is 'No content leaves "
            f"the device' and `local_model` is 'a user-installed local LLM'; a "
            f"cloud call wearing a local target is authorized by both, and "
            f"`Gate.release` is told the locality rather than able to measure it."
        )
    if not model_target.model_id:
        raise TargetIsNotThisTransport(
            "model_target.model_id names which model is asked, and §8.4 requires "
            "the audit record show it"
        )


#: THE JUDGES' SAMPLING, the owner's ruling of 15 Sep 2026 ("there should be no
#: abstentions; make sure of that"), measured before it was chosen: on the lead's
#: bench over the owner's corpus the kind judge answered 257 of 310 right at
#: temperature 0 against 243 at the provider's default (one rejected answer
#: against five), and the situation judge 146 of 179 at both; 18 of 44 files
#: re-asked between runs 13 and 15 had changed their answer under the default.
#: A sampling term and not a prompt term, by the reading R-14 gave
#: `response_format`; recorded on every call identity as the `sampling`
#: dimension, so a verdict taken under another setting is re-asked, never
#: replayed. One constant, here, because this module is the one place the
#: request is assembled.
JUDGE_SAMPLING: float = 0.0


def deepseek_invoke(*, api_key: str | None, base_url: str | None,
                    model_target: ModelTarget, max_response_tokens: int,
                    timeout_seconds: float | None = None,
                    send: Callable[..., object] = _send,
                    on_usage: Callable[[Usage | None], None] | None = None,
                    ) -> Callable[[bytes], bytes]:
    """A `ModelClient.invoke`: the model-visible bytes in, the model's answer out.

    Every refusal fires HERE, when the client is built, not on the first call: a
    deployment with no key, no endpoint or a mislabelled target stops before the
    scan rather than after it.

    `on_usage` is `104` R-14's sink and is optional. It is a sink and not a return
    value because `ModelClient.invoke` is `Callable[[bytes], bytes]` and widening
    that contract belongs to `llm_harness/transport.py`, which a reader may not
    reach into. It is called once per ANSWERED call, with `None` when the provider
    reported no usage -- because "the provider told us nothing" is itself the
    audit's answer, and silence there is indistinguishable from a call that never
    happened. A deployment that records no usage supplies none, which is the state
    `model_ollama`'s caller is in.
    """
    key = _require_credential(api_key)
    endpoint = _require_endpoint(base_url)
    _require_target(model_target)
    if not isinstance(max_response_tokens, int) or max_response_tokens < 1:
        raise ValueError(
            "max_response_tokens is injected and is the deployment's ceiling; §8.6 "
            "names its ceilings configurable and gives no values, and a value below "
            "one is not an echo of any ceiling"
        )
    if not isinstance(timeout_seconds, (int, float)) or isinstance(
            timeout_seconds, bool) or timeout_seconds <= 0:
        raise ValueError(
            "timeout_seconds is injected and is the deployment's patience; a "
            "client built without one can hold a scan open for ever, and zero "
            "is not patience but a different bug wearing a number. `cli.py` is "
            "the only file that picks it, the same way it picks every other "
            "number this module refuses to invent."
        )
    model_id = model_target.model_id

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
        try:
            response = send(
                api_key=key, base_url=endpoint, model_id=model_id,
                max_tokens=max_response_tokens, prompt=prompt,
                timeout_seconds=timeout_seconds, temperature=JUDGE_SAMPLING,
            )
        except TimeoutError as problem:
            # THE MODEL WAS ASKED AND DID NOT FINISH, which is not the same as a
            # provider that is not there. `104` R-176: until this branch existed
            # there was no branch at all -- the local twin had one and this one
            # did not, so a cloud call that ran out of time arrived upstream as
            # whatever the SDK happened to raise.
            raise _out_of_time(problem, _RAN_OUT_OF_TIME.format(
                provider=PROVIDER, seconds=f"{timeout_seconds:g}")) from problem
        except Exception as problem:
            # THE SAME DEADLINE, ARRIVING WRAPPED. The SDK turns anything the
            # transport raises into its own connection error with the original as
            # `__cause__`, and what a timeout MEANS does not change with the
            # wrapper it arrived in. Anything else is re-raised exactly as it was:
            # this branch adds a reading, it does not add a handler.
            expiry = problem.__cause__
            if isinstance(expiry, TimeoutError):
                raise _out_of_time(expiry, _RAN_OUT_OF_TIME.format(
                    provider=PROVIDER,
                    seconds=f"{timeout_seconds:g}")) from problem
            raise
        # AFTER `response_text`, so a refusal is a refusal and not a cost. A
        # `content_filter`, a `length` cut-off or an unreadable finish reason all
        # raise there, and none of them is an answer this run may bill itself for.
        answer = response_text(response)
        if on_usage is not None:
            on_usage(usage_of(response, model_id=model_id))
        return answer.encode("utf-8")

    return invoke

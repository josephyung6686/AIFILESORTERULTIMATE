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

**And no NUMBER is chosen here.** The response ceiling, the context ceiling and the
patience are injected, exactly as `model_deepseek`'s are: `84` §1's rule is absent
means refuse, never guess, and `src/` picks no numbers. `cli.py` is the only file
that picks them.
"""
from __future__ import annotations

import json
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

#: The only `done_reason` that means the model finished answering, and the same
#: one-member closed set `model_deepseek.FINISHED` is: the failures are the
#: server's to extend and the successes are not.
FINISHED: str = "stop"


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


class OllamaContextExceeded(RuntimeError):
    """The dossier will not fit the window, so it was not sent to be truncated."""


class TargetIsNotThisTransport(RuntimeError):
    """The `ModelTarget` does not describe the call this module would make."""


class ModelVisibleBytesNotText(RuntimeError):
    """The released bytes are not UTF-8 and cannot be sent without altering them."""


class NoAnswerFromModel(RuntimeError):
    """Something came back over HTTP 200 and it is not an answer to the dossier."""


def _post(url: str, body: bytes, *, timeout: float) -> bytes:
    """The one place this module touches a socket, so a test can replace it."""
    from urllib.request import Request, urlopen

    request = Request(url, data=body,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


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
                  post: Callable[..., bytes] = _post,
                  ) -> Callable[[bytes], bytes]:
    """A `ModelClient.invoke`: the model-visible bytes in, the model's answer out.

    Every refusal that can fire at build time fires HERE, before the scan: a
    mislabelled target, a host that is not loopback, a number nobody chose. That
    is `deepseek_invoke`'s rule and the reason is the same -- a deployment that is
    going to refuse should refuse before it has read a person's folder.
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
            "stream": False,
            # P8 parses the reply against `response_schema_bytes`. A model free to
            # answer in prose fails that check for a reason that is not about the
            # evidence, which would read as the model declining when it did not.
            "format": "json",
            # `104` R-18, sent rather than assumed. See the module docstring.
            "think": False,
            "options": {"temperature": 0, "seed": 1,
                        "num_ctx": window, "num_predict": response_tokens},
        }).encode("utf-8")
        try:
            raw = post(url, body, timeout=timeout_seconds)
        except OllamaUnavailable:
            raise
        except TimeoutError as problem:
            # THE MODEL WAS ASKED AND IS STILL THINKING, which is not the same as
            # a model that is not there, and telling a person to start a server
            # that is already running would send them to fix the thing that works.
            raise OllamaRanOutOfTime(
                f"the local model at {endpoint} was asked and had not answered "
                f"after {timeout_seconds:g} seconds, so this run stopped waiting "
                f"({problem}). The call HAPPENED -- ollama is running and was "
                f"working -- and no answer came back, so nothing was decided on "
                f"the strength of a judgement that was never finished. A bigger "
                f"model on a busy machine is the ordinary cause; raise the "
                f"deployment's patience or name a smaller model."
            ) from problem
        except Exception as problem:  # transport failure of any kind
            # A read timeout can also arrive wrapped, and what it MEANS does not
            # change with the wrapper it arrived in.
            if isinstance(getattr(problem, "reason", None), TimeoutError):
                raise OllamaRanOutOfTime(
                    f"the local model at {endpoint} was asked and had not "
                    f"answered after {timeout_seconds:g} seconds, so this run "
                    f"stopped waiting ({problem}). The call HAPPENED and no "
                    f"answer came back."
                ) from problem
            raise OllamaUnavailable(
                f"the local model at {endpoint} could not be reached ({problem}). "
                f"Start it with `ollama serve`. No call was made, so nothing was "
                f"decided on the strength of a model that was never asked."
            ) from problem
        return _answer(json.loads(raw), window=window,
                       prompt_bytes=len(payload),
                       response_tokens=response_tokens).encode("utf-8")

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
    message = response.get("message")
    if not isinstance(message, dict):
        raise NoAnswerFromModel(
            f"the response carried no `message` object (keys: "
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
    # construction rests on. `_window_for` sized this window above
    # `bytes / BYTES_PER_TOKEN_FLOOR`, which is an upper bound on the prompt's
    # true token count -- so the prompt fits, and truncation cannot happen, UNLESS
    # this payload tokenised worse than that floor. `prompt_eval_count` is what
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
    text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise NoAnswerFromModel(
            f"the response carried no message content (done_reason={reason!r}). "
            f"Empty bytes parse as no claims and would be recorded as a rejected "
            f"model answer; there is no model answer here to reject.")
    return text

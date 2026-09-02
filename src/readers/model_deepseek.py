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
sets a system message, a temperature, a `response_format` or an `n`: a sentence or
a knob added here would be a prompt nobody approved and no record names. The model
id comes from the `ModelTarget` -- which of `83`'s three tiers this client is, is
decided by the caller -- and the token ceiling is injected; §8.6 names its ceilings
"configurable" and gives no values, so neither is chosen here.

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

**On retries.** The SDK retries 429s and 5xx by default. Those responses are not
billed and are not answers, so they are not a second call in anything this product
measures: `harness.run_call` reserves one budget call and `transport.issue`
consumes one release per `invoke`, and there is no retry in this module over an
answer.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable

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


def _send(*, api_key: str, base_url: str, model_id: str, max_tokens: int,
          prompt: str) -> object:
    """The one place this module touches a socket, so a test can replace it.

    Two statements, and they are the two this project cannot exercise without
    spending money and holding a key. Everything the module does with what comes
    back is `response_text`, which is pure.
    """
    import openai

    return openai.OpenAI(api_key=api_key, base_url=base_url).chat.completions.create(
        model=model_id,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )


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


def deepseek_invoke(*, api_key: str | None, base_url: str | None,
                    model_target: ModelTarget, max_response_tokens: int,
                    send: Callable[..., object] = _send,
                    ) -> Callable[[bytes], bytes]:
    """A `ModelClient.invoke`: the model-visible bytes in, the model's answer out.

    Every refusal fires HERE, when the client is built, not on the first call: a
    deployment with no key, no endpoint or a mislabelled target stops before the
    scan rather than after it.
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
        return response_text(send(
            api_key=key, base_url=endpoint, model_id=model_id,
            max_tokens=max_response_tokens, prompt=prompt,
        )).encode("utf-8")

    return invoke

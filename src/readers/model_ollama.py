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
"""
from __future__ import annotations

import json
from typing import Callable

#: Loopback, and not configurable. The `ModelTarget` paired with this transport
#: claims `locality="local"`; a host parameter would make that claim unverifiable
#: from the record, which is the one thing §8.4's audit exists to prevent.
HOST: str = "http://127.0.0.1:11434"
GENERATE: str = f"{HOST}/api/generate"

#: §8.6 wants a run-time limit on model work. Seconds, and the caller's to change
#: by wrapping; a local 3B model answers a bounded dossier well inside this.
TIMEOUT_SECONDS: float = 120.0


class OllamaUnavailable(RuntimeError):
    """The local model could not be reached, so no call happened."""


def _post(url: str, body: bytes, *, timeout: float) -> bytes:
    """The one place this module touches a socket, so a test can replace it."""
    from urllib.request import Request, urlopen

    request = Request(url, data=body,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def ollama_invoke(*, model_id: str,
                  post: Callable[..., bytes] = _post,
                  timeout: float = TIMEOUT_SECONDS) -> Callable[[bytes], bytes]:
    """A `ModelClient.invoke`: the model-visible bytes in, the model's answer out."""

    def invoke(payload: bytes) -> bytes:
        body = json.dumps({
            "model": model_id,
            # VERBATIM. The dossier P8 assembled is the prompt; this module adds
            # no instruction of its own, because an instruction added here would
            # not be in the fingerprint the audit record stores.
            "prompt": payload.decode("utf-8"),
            "stream": False,
            # P8 parses the reply against `response_schema_bytes`. A model free to
            # answer in prose fails that check for a reason that is not about the
            # evidence, which would read as the model declining when it did not.
            "format": "json",
            "options": {"temperature": 0, "seed": 1},
        }).encode("utf-8")
        try:
            raw = post(GENERATE, body, timeout=timeout)
        except OllamaUnavailable:
            raise
        except Exception as problem:  # transport failure of any kind
            raise OllamaUnavailable(
                f"the local model at {HOST} could not be reached ({problem}). "
                "Start it with `ollama serve`. No call was made, so nothing was "
                "decided on the strength of a model that was never asked."
            ) from problem
        answer = json.loads(raw)["response"]
        return answer.encode("utf-8") if isinstance(answer, str) else answer

    return invoke

# tools/promptbench/clients.py
"""The two model clients the bench drives, both built on the product's transports.

Nothing here composes a prompt. The bytes handed to `invoke` are the exact
model-visible bytes `llm_harness.records.assemble` produces, and each client
returns them to the model untouched, the way `readers.model_ollama` and
`readers.model_deepseek` do -- because both clients ARE those two modules, with
one seam each replaced so the bench can measure what the product does not:

* **local**: `readers.model_ollama.ollama_invoke(post=...)`. The replaced `post`
  reads the body the transport built, adds what the transport does not set --
  `think: false` (a qwen3 model must run with thinking off, `104` R-18) and an
  explicit `num_ctx` (Ollama otherwise truncates to its default context silently
  and answers anyway; the coordinator's finding of 2026-09-06) -- and records the
  server's `prompt_eval_count` beside the `num_ctx` it used, so a truncated call
  is a bench defect the record shows rather than a model result.
* **cloud**: `readers.model_deepseek.deepseek_invoke(send=...)`. The replaced
  `send` spends one row of a persisted call ledger BEFORE the socket opens and
  refuses at the cap, pins `temperature=0` (recorded; the product's own `_send`
  sets none, which is a recommendation in the packet, not a fact this bench may
  change), and captures `usage` so the packet can report tokens per candidate.

The key is read through the product's own loader, `cli._dotenv`, pointed at the
main checkout's `.env`. It is held in a closure, never returned, never printed.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from privacy.release import ModelTarget  # noqa: E402
from readers.model_deepseek import (  # noqa: E402
    BASE_URL_NAME, CREDENTIAL_NAME, deepseek_invoke,
)
from readers.model_ollama import ollama_invoke  # noqa: E402

#: Where the deployment keeps its key. NOT `cli.ENV_FILE`: that resolves beside
#: whichever checkout imports `cli`, and a worktree has no `.env`.
MAIN_CHECKOUT_ENV: Path = Path("/Users/jy/GRAPH AGENT/.env")

#: The cloud model the task names. Deliberately not read from the tier names in
#: `.env`: the LOGIC tier there may resolve to a reasoning model, and `104` R-18
#: measured what a reasoner does with a shared thinking-and-writing budget.
CLOUD_MODEL_ID: str = "deepseek-chat"
DEFAULT_BASE_URL: str = "https://api.deepseek.com"
CLOUD_TARGET = ModelTarget(locality="cloud", model_id=CLOUD_MODEL_ID,
                           provider="deepseek")

LOCAL_MODEL_ID: str = "qwen3:8b"
LOCAL_TARGET = ModelTarget(locality="local", model_id=LOCAL_MODEL_ID,
                           provider="ollama")

#: The product's ceilings for a call (`cli.MAX_RESPONSE_TOKENS`,
#: `cli.MODEL_CALL_TIMEOUT_SECONDS` are 8192 and 90); the bench keeps the token
#: ceiling and lengthens the patience, because a local 8B model on a laptop is
#: slower than a provider and a timeout here would be recorded as a model failure.
MAX_RESPONSE_TOKENS: int = 8192
CLOUD_TIMEOUT_SECONDS: float = 180.0
LOCAL_TIMEOUT_SECONDS: float = 900.0

#: Local context sizing. Prompts are UTF-8 JSON; three bytes per token is a
#: conservative estimate for this text (measured 3.3 to 3.9 on the A_fact
#: dossiers), so the estimate overstates the count and the ceiling below it is
#: never too small. The response ceiling is added because `num_ctx` bounds
#: prompt AND answer together.
BYTES_PER_TOKEN_ESTIMATE: float = 3.0
LOCAL_RESPONSE_CEILING: int = 4096
NUM_CTX_MINIMUM: int = 8192
NUM_CTX_MAXIMUM: int = 32768   # qwen3-8b's native window


class CloudCapReached(RuntimeError):
    """The persisted ledger says the cap is spent. No socket was opened."""


@dataclass
class CallMeta:
    """What the bench records about one call beyond the bytes themselves."""

    model_id: str
    locality: str
    latency_seconds: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    num_ctx: int | None = None
    prompt_bytes: int = 0
    settings: dict = field(default_factory=dict)


def num_ctx_for(prompt_bytes: int) -> int:
    """An explicit context ceiling comfortably above the prompt's measured length."""
    estimate = int(prompt_bytes / BYTES_PER_TOKEN_ESTIMATE) + LOCAL_RESPONSE_CEILING
    ceiling = NUM_CTX_MINIMUM
    while ceiling < estimate * 1.25 and ceiling < NUM_CTX_MAXIMUM:
        ceiling *= 2
    if estimate > ceiling:
        raise ValueError(
            f"a {prompt_bytes}-byte prompt needs about {estimate} tokens of "
            f"context and the local model's window is {NUM_CTX_MAXIMUM}; the "
            "case is too large for the local bakeoff and must be shortened")
    return ceiling


def local_client(*, post=None) -> Callable[[bytes], tuple[bytes, CallMeta]]:
    """`invoke(bytes) -> (answer bytes, meta)` over the product's Ollama transport."""
    from urllib.request import Request, urlopen

    def _post(url: str, body: bytes, *, timeout: float) -> bytes:
        request = Request(url, data=body,
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=timeout) as response:
            return response.read()

    real_post = post or _post
    last: dict = {}

    def bench_post(url: str, body: bytes, *, timeout: float) -> bytes:
        payload = json.loads(body)
        prompt_bytes = len(payload["prompt"].encode("utf-8"))
        num_ctx = num_ctx_for(prompt_bytes)
        # The transport's own options are kept (temperature 0, seed 1, format
        # json); the bench adds the two it cannot do without and nothing else.
        payload["think"] = False
        payload["options"] = dict(payload.get("options", {}),
                                  num_ctx=num_ctx,
                                  num_predict=LOCAL_RESPONSE_CEILING)
        started = time.monotonic()
        raw = real_post(url, json.dumps(payload).encode("utf-8"), timeout=timeout)
        elapsed = time.monotonic() - started
        answer = json.loads(raw)
        prompt_tokens = answer.get("prompt_eval_count")
        last.clear()
        last.update(
            latency=elapsed, num_ctx=num_ctx, prompt_bytes=prompt_bytes,
            prompt_tokens=prompt_tokens,
            completion_tokens=answer.get("eval_count"),
            done_reason=answer.get("done_reason"),
            thinking_present=bool(answer.get("thinking")),
        )
        # `prompt_eval_count` can be BELOW the true length when Ollama reuses a
        # cached prefix, so it cannot prove absence of truncation; the byte
        # estimate above is what does. It CAN prove presence: a count at or
        # over the ceiling means the prompt did not fit.
        if isinstance(prompt_tokens, int) and prompt_tokens >= num_ctx:
            raise RuntimeError(
                f"local prompt of {prompt_tokens} tokens reached num_ctx="
                f"{num_ctx}; the call would have been answered over a truncated "
                "prompt and is refused as a bench defect")
        return raw

    invoke = ollama_invoke(model_id=LOCAL_MODEL_ID, post=bench_post,
                           timeout=LOCAL_TIMEOUT_SECONDS)

    def call(payload: bytes) -> tuple[bytes, CallMeta]:
        answer = invoke(payload)
        meta = CallMeta(
            model_id=LOCAL_MODEL_ID, locality="local",
            latency_seconds=last["latency"],
            prompt_tokens=last["prompt_tokens"],
            completion_tokens=last["completion_tokens"],
            num_ctx=last["num_ctx"], prompt_bytes=last["prompt_bytes"],
            settings={"think": False, "format": "json", "temperature": 0,
                      "seed": 1, "num_predict": LOCAL_RESPONSE_CEILING,
                      "done_reason": last["done_reason"],
                      "thinking_present": last["thinking_present"]})
        return answer, meta

    return call


# --- the cloud side -------------------------------------------------------------


@dataclass
class CallLedger:
    """A persisted count of cloud calls, spent before each socket opens.

    One JSON file under the bench's out directory. Re-runs accumulate: the cap is
    on the whole bakeoff, not on one invocation. Every read-modify-write holds an
    exclusive `flock` on a lock file beside it, so five site runs in parallel
    cannot each read 399 and all spend the 400th.
    """

    path: Path
    cap: int

    def _locked(self):
        import fcntl
        from contextlib import contextmanager

        @contextmanager
        def held():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path.with_suffix(".lock"), "a+") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)

        return held()

    def _read(self) -> dict:
        if not self.path.is_file():
            return {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0,
                    "cap": self.cap}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, state: dict) -> None:
        self.path.write_text(json.dumps(state, indent=1), encoding="utf-8")

    def spend(self) -> int:
        with self._locked():
            state = self._read()
            if state["calls"] >= self.cap:
                raise CloudCapReached(
                    f"the cloud ledger at {self.path} records {state['calls']} "
                    f"calls against a cap of {self.cap}; no further call is made")
            state["calls"] += 1
            state["cap"] = self.cap
            self._write(state)
            return state["calls"]

    def record_usage(self, *, prompt_tokens: int, completion_tokens: int) -> None:
        with self._locked():
            state = self._read()
            state["prompt_tokens"] += int(prompt_tokens or 0)
            state["completion_tokens"] += int(completion_tokens or 0)
            self._write(state)

    def summary(self) -> dict:
        with self._locked():
            return self._read()


def credentials() -> tuple[str, str]:
    """The key and endpoint, through the product's own `.env` reader.

    Returned to the caller that builds the client and to nobody else; nothing in
    the bench formats either into a message, a log or a record.
    """
    from cli import _dotenv  # the product's loader, and the only one used

    supplied = _dotenv(MAIN_CHECKOUT_ENV)

    def value(name: str) -> str:
        return (os.environ.get(name) or supplied.get(name) or "").strip()

    key = value(CREDENTIAL_NAME)
    if not key:
        raise RuntimeError(
            f"{CREDENTIAL_NAME} is not set in the environment or in "
            f"{MAIN_CHECKOUT_ENV}; the cloud arm cannot run")
    return key, (value(BASE_URL_NAME) or DEFAULT_BASE_URL)


def cloud_client(ledger: CallLedger, *, send=None,
                 temperature: float = 0.0,
                 ) -> Callable[[bytes], tuple[bytes, CallMeta]]:
    """`invoke(bytes) -> (answer bytes, meta)` over the product's DeepSeek transport.

    `send` may be replaced by a test; the real one is the SDK call the product's
    `_send` makes, with `temperature` added and `usage` kept.
    """
    api_key, base_url = credentials()
    last: dict = {}

    def real_send(*, api_key: str, base_url: str, model_id: str, max_tokens: int,
                  prompt: str, timeout_seconds: float) -> object:
        import openai

        return openai.OpenAI(
            api_key=api_key, base_url=base_url,
            timeout=timeout_seconds, max_retries=0,
        ).chat.completions.create(
            model=model_id, max_tokens=max_tokens, temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

    chosen_send = send or real_send

    def bench_send(**kw) -> object:
        ledger.spend()
        started = time.monotonic()
        response = chosen_send(**kw)
        elapsed = time.monotonic() - started
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)
        ledger.record_usage(prompt_tokens=prompt_tokens or 0,
                            completion_tokens=completion_tokens or 0)
        last.clear()
        last.update(latency=elapsed, prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    prompt_bytes=len(kw["prompt"].encode("utf-8")),
                    finish_reason=getattr(
                        (getattr(response, "choices", None) or [None])[0],
                        "finish_reason", None))
        return response

    invoke = deepseek_invoke(
        api_key=api_key, base_url=base_url, model_target=CLOUD_TARGET,
        max_response_tokens=MAX_RESPONSE_TOKENS,
        timeout_seconds=CLOUD_TIMEOUT_SECONDS, send=bench_send)

    def call(payload: bytes) -> tuple[bytes, CallMeta]:
        answer = invoke(payload)
        meta = CallMeta(
            model_id=CLOUD_MODEL_ID, locality="cloud",
            latency_seconds=last["latency"],
            prompt_tokens=last["prompt_tokens"],
            completion_tokens=last["completion_tokens"],
            prompt_bytes=last["prompt_bytes"],
            settings={"temperature": temperature,
                      "max_tokens": MAX_RESPONSE_TOKENS,
                      "response_format": None,
                      "finish_reason": last["finish_reason"]})
        return answer, meta

    return call


def target_for(locality: str) -> ModelTarget:
    return LOCAL_TARGET if locality == "local" else CLOUD_TARGET


__all__ = [
    "CallLedger", "CallMeta", "CloudCapReached", "cloud_client", "credentials",
    "local_client", "num_ctx_for", "target_for",
]

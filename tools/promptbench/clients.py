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
from readers.model_ollama import (  # noqa: E402
    DEFAULT_BASE_URL as LOCAL_BASE_URL, assemble, ollama_invoke,
)

def _main_checkout(start: Path) -> Path:
    """The checkout a worktree was cut FROM, or `start` when it is not one.

    A worktree's `.git` is a FILE reading `gitdir: <main>/.git/worktrees/<name>`,
    where a real checkout's is a directory. So the main tree is found by reading
    that pointer and walking up to the `.git` it names. No subprocess: this runs
    at import, and a tool that cannot be imported without shelling out to `git`
    is a tool that breaks in every environment that has no `git` on the path.
    """
    marker = start / ".git"
    if marker.is_file():
        pointer = marker.read_text().partition(":")[2].strip()
        gitdir = Path(pointer)
        if not gitdir.is_absolute():
            gitdir = (start / gitdir).resolve()
        for parent in gitdir.parents:
            if parent.name == ".git":
                return parent.parent
    return start


#: Where the deployment keeps its key. NOT `cli.ENV_FILE`: that resolves beside
#: whichever checkout imports `cli`, and a worktree has no `.env`.
#:
#: FOUND, NOT SPELLED. This was the author's own absolute path, which made the
#: tool silently keyless on every other machine -- and "no key" here reads as
#: "the cloud model is unavailable", which is a wrong answer rather than an
#: error. The deployment is whatever checkout this worktree came from.
MAIN_CHECKOUT_ENV: Path = _main_checkout(_ROOT) / ".env"

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

    def _post(url: str, body: bytes, *, timeout: float,
              silence: float) -> bytes:
        # `silence` IS ACCEPTED AND NOT SPENT, and that is the bench's own choice
        # said out loud. `104` R-177's silence deadline lives in the product's
        # `_post`, which drops to `http.client` for the seam between the phases of
        # a call; `urlopen` offers none, which is why the product left it. The
        # bench measures whole calls under `LOCAL_TIMEOUT_SECONDS` as it always
        # has -- a bakeoff wants the slow candidate's real latency, not a run that
        # abandons it -- and takes the argument so it is the product's transport
        # it is driving and not a different one.
        request = Request(url, data=body,
                          headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=timeout) as response:
            return response.read()

    real_post = post or _post
    last: dict = {}

    def bench_post(url: str, body: bytes, *, timeout: float,
                   silence: float) -> bytes:
        payload = json.loads(body)
        if "messages" not in payload:
            # THE MODEL LOAD, not a call: the transport's first request names
            # the model and carries no prompt. Nothing to size, nothing to
            # record; it goes through as it is.
            return real_post(url, body, timeout=timeout, silence=silence)
        # `/api/chat`, WHICH IS THE TRANSPORT THE PRODUCT SHIPS. This read
        # `payload["prompt"]`, the `/api/generate` field, against a 95-line
        # bench-local copy of `ollama_invoke` that the Phase 0a transport
        # replaced. The product's transport sends one user message, and the
        # bench measures the product or it measures nothing.
        prompt_bytes = len(payload["messages"][0]["content"].encode("utf-8"))
        num_ctx = num_ctx_for(prompt_bytes)
        # `think` and `format` are the transport's own and are already set; the
        # bench sizes the WINDOW per prompt, which the product deliberately does
        # not do (`104` R-52: one window per run, because changing it reloads the
        # model). That difference is the bench's to make -- it is comparing
        # prompt texts, not measuring a scan -- and it is why the window is
        # overridden here and nowhere else.
        payload["options"] = dict(payload.get("options", {}),
                                  num_ctx=num_ctx,
                                  num_predict=LOCAL_RESPONSE_CEILING)
        # The machine's load is recorded beside the latency because a local
        # latency on a shared laptop is a fact about the laptop as much as
        # about the model: 5 minutes at load 200 and 40 seconds at load 3
        # are the same call.
        load_before = _load_average_1m()
        started = time.monotonic()
        raw = real_post(url, json.dumps(payload).encode("utf-8"),
                        timeout=timeout, silence=silence)
        elapsed = time.monotonic() - started
        load_after = _load_average_1m()
        # `104` R-177: the transport asks for `stream: true`, so the body is one
        # JSON object per token. `assemble` is the product's own reader of that,
        # used here rather than re-parsed, so the bench's counts and the product's
        # come off the same object.
        answer = assemble(raw)
        prompt_tokens = answer.get("prompt_eval_count")
        last.clear()
        last.update(
            latency=elapsed, num_ctx=num_ctx, prompt_bytes=prompt_bytes,
            prompt_tokens=prompt_tokens,
            completion_tokens=answer.get("eval_count"),
            done_reason=answer.get("done_reason"),
            thinking_present=bool(answer.get("thinking")),
            load_before=load_before, load_after=load_after,
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

    # The ceiling given to the transport is the bench's MAXIMUM, so its
    # pre-socket `_fits` refusal never fires below the window `bench_post` is
    # about to choose; `num_ctx_for` raises on its own for a prompt that cannot
    # fit, which is the bench's version of the same guarantee.
    invoke = ollama_invoke(model_target=LOCAL_TARGET,
                           base_url=LOCAL_BASE_URL,
                           max_response_tokens=LOCAL_RESPONSE_CEILING,
                           context_ceiling=NUM_CTX_MAXIMUM,
                           timeout_seconds=LOCAL_TIMEOUT_SECONDS,
                           silence_seconds=LOCAL_TIMEOUT_SECONDS,
                           post=bench_post)

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
                      "thinking_present": last["thinking_present"],
                      "load_average_1m_before": last["load_before"],
                      "load_average_1m_after": last["load_after"]})
        return answer, meta

    return call


def _load_average_1m() -> float | None:
    """The one-minute load average, or None where the platform has none."""
    try:
        return round(os.getloadavg()[0], 2)
    except (AttributeError, OSError):
        return None


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
                        "finish_reason", None),
                    # The provider's own account of how much of the prompt it
                    # served from its prefix cache: the stable-prefix lever,
                    # measured rather than argued. Absent on other providers.
                    cache_hit_tokens=_usage_extra(usage, "prompt_cache_hit_tokens"),
                    cache_miss_tokens=_usage_extra(usage, "prompt_cache_miss_tokens"))
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
                      "finish_reason": last["finish_reason"],
                      "prompt_cache_hit_tokens": last["cache_hit_tokens"],
                      "prompt_cache_miss_tokens": last["cache_miss_tokens"]})
        return answer, meta

    return call


def _usage_extra(usage, name: str):
    """A provider-specific usage field, or None where the SDK did not carry it."""
    if usage is None:
        return None
    value = getattr(usage, name, None)
    if value is None:
        extra = getattr(usage, "model_extra", None) or {}
        value = extra.get(name) if isinstance(extra, dict) else None
    return int(value) if isinstance(value, (int, float)) else None


def target_for(locality: str) -> ModelTarget:
    return LOCAL_TARGET if locality == "local" else CLOUD_TARGET


__all__ = [
    "CallLedger", "CallMeta", "CloudCapReached", "cloud_client", "credentials",
    "local_client", "num_ctx_for", "target_for",
]

# src/readers/model_claude_code.py
"""Ask the unmodified `claude` binary. This process never reads its login.

Anthropic's legal and compliance page says a third party may not offer
Claude.ai login, may not route Free, Pro, or Max credentials, and may not
collect or store those session tokens. The same page says that does not
prevent a person from signing in to the unmodified Claude Code binary,
including where a product hosts that binary.

https://code.claude.com/docs/en/legal-and-compliance

This module only spawns that binary, and only when FILESORTER_CLAUDE_CODE=1.
It does not read the Claude Code keychain, `~/.claude`, or a browser cookie.
If Anthropic changes enforcement, this path can stop being allowed; the
documentation says so. The picker still shows the lane when the flag is off,
with the reason, so the screen matches the three lanes without shipping the
banned button.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

FLAG: str = "FILESORTER_CLAUDE_CODE"
POLICY: str = (
    "not available — use Claude Code or an API key — Anthropic policy. "
    "Sign in inside Claude Code. This app does not offer Claude.ai login "
    "and does not route Free, Pro, or Max credentials."
)
MISSING: str = (
    "Claude Code is not on PATH. Install the unmodified `claude` binary and "
    "sign in inside Claude Code, or use an Anthropic API key."
)

#: Print mode. The prompt is the next argument. No extra flags: a flag this
#: module invented would be a different program than the binary the person installed.
PRINT_FLAG: str = "-p"


class ClaudeCodeRefused(RuntimeError):
    """The binary was not started."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


Runner = Callable[[Sequence[str]], CommandResult]


def flag_enabled(environ: Mapping[str, str] | None = None) -> bool:
    source = os.environ if environ is None else environ
    return source.get(FLAG) == "1"


def find_binary(which: Callable[[str], str | None]) -> str | None:
    return which("claude")


def classify_argv(binary: str, prompt: str) -> tuple[str, ...]:
    name = binary.rsplit("/", 1)[-1]
    if name != "claude":
        raise ClaudeCodeRefused(
            f"refusing to run {name!r}. Only the unmodified claude binary "
            "is the carve-out.")
    if not prompt.strip():
        raise ClaudeCodeRefused("there is no prompt to hand the binary")
    return (binary, PRINT_FLAG, prompt)


class ClaudeCodeUnderstanding:
    """Classification through the unmodified binary. The login stays inside it."""

    def __init__(self, binary: str, run: Runner):
        self._binary = binary
        self._run = run

    def provider_name(self) -> str:
        return "claude-code"

    def locality(self) -> str:
        # The binary is local. The prompt still leaves the machine if that
        # login is a Claude subscription. offline must refuse it.
        return "cloud"

    def complete(self, request) -> dict:
        text = run_prompt(
            self._binary, request.prompt, run=self._run, flag_on=True)
        return {"choices": [{"finish_reason": "stop",
                             "message": {"content": text}}]}


def default_runner() -> Runner:
    """Spawn the binary. Tests pass their own `run` and never reach this."""
    import subprocess

    def run(argv: Sequence[str]) -> CommandResult:
        completed = subprocess.run(
            list(argv), check=False, capture_output=True, text=True)
        return CommandResult(
            completed.returncode, completed.stdout, completed.stderr)

    return run


def run_prompt(binary: str, prompt: str, *, run: Runner,
               flag_on: bool) -> str:
    """Run `claude -p`. `run` is the process. The flag must already be on."""
    if not flag_on:
        raise ClaudeCodeRefused(POLICY)
    argv = classify_argv(binary, prompt)
    result = run(argv)
    if result.returncode != 0:
        raise ClaudeCodeRefused(
            f"claude exited {result.returncode}. Its login was not read.")
    if not result.stdout.strip():
        raise ClaudeCodeRefused("claude exited 0 and printed no answer")
    return result.stdout

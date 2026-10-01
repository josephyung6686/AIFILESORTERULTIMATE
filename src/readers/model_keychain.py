# src/readers/model_keychain.py
"""Secrets in the macOS Keychain, via the `security` command.

The plan database stores which provider is active. It does not store the key.
`security` is the helper this deployment already expects on a Mac; this module
does not read `~/.codex/auth.json`, a Claude Code keychain item, or a browser
cookie. A missing `security` binary is a refusal, not a fallback into a file.

Nothing this module prints or raises includes the secret. Callers pass a `run`
so a test can stand in for the command.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

#: One keychain service for every secret this product writes. Account names
#: distinguish the provider. They are not secret.
SERVICE: str = "filesorter"

DEEPSEEK_API_KEY: str = "deepseek-api-key"
OPENAI_API_KEY: str = "openai-api-key"
ANTHROPIC_API_KEY: str = "anthropic-api-key"
COMPATIBLE_API_KEY: str = "openai-compatible-api-key"
SIWC_ACCESS: str = "openai-siwc-access"
SIWC_REFRESH: str = "openai-siwc-refresh"
SIWC_REGISTRATION: str = "openai-siwc-registration"

ACCOUNTS: frozenset[str] = frozenset({
    DEEPSEEK_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, COMPATIBLE_API_KEY,
    SIWC_ACCESS, SIWC_REFRESH, SIWC_REGISTRATION,
})


class KeychainError(RuntimeError):
    """The keychain command failed. The message names the account, not the secret."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


Runner = Callable[[Sequence[str]], CommandResult]


def _checked_account(account: str) -> str:
    if account not in ACCOUNTS:
        raise KeychainError(
            f"{account!r} is not a keychain account this product writes")
    return account


def add_secret(account: str, secret: str, *, run: Runner) -> None:
    """Create or replace one secret. `-U` is what makes a rotation an overwrite."""
    account = _checked_account(account)
    if not isinstance(secret, str) or not secret.strip():
        raise KeychainError(f"refusing to store an empty secret for {account}")
    # The secret is an argument of `security`. It is not copied into the error.
    result = run((
        "security", "add-generic-password",
        "-s", SERVICE, "-a", account, "-w", secret, "-U",
    ))
    if result.returncode != 0:
        raise KeychainError(
            f"could not store {account} in the keychain "
            f"(security exited {result.returncode})")


def find_secret(account: str, *, run: Runner) -> str | None:
    """The secret, or None when the item is absent. Never logs the value."""
    account = _checked_account(account)
    result = run((
        "security", "find-generic-password",
        "-s", SERVICE, "-a", account, "-w",
    ))
    if result.returncode != 0:
        return None
    secret = result.stdout.strip()
    return secret or None


def delete_secret(account: str, *, run: Runner) -> bool:
    """Remove one item. False when it was not there. A later add can replace it."""
    account = _checked_account(account)
    result = run((
        "security", "delete-generic-password",
        "-s", SERVICE, "-a", account,
    ))
    if result.returncode != 0:
        return False
    return True

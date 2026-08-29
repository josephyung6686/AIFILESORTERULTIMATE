# src/privacy/binding.py
"""The release ledger: what makes `Released` a capability rather than a value.

SPEC §6 states the property and the reason in one breath: "Binding and single use
exist to keep the audit record truthful. §8.4 requires the record to show *which
model received the data* and *the prompt fingerprint*; a payload that could be
replayed against a different model or under a different prompt would make both
fields false. A release is consumed on first transport use."

Three decisions, each forced rather than chosen:

- **The ledger is the authority, not the entropy.** `ReleaseNotIssued` is what makes
  a hand-constructed `Released` inert, and it is a lookup. The 128 bits are so that a
  caller holding one id cannot enumerate its way to another minted in the same run.
- **The binding is checked before the spend, and a mismatch spends nothing.** A
  mis-wired caller must not be able to burn an authorization the user granted, and a
  release that never reached a model must not be recorded as one that did.
- **`audit_id` is carried and never compared.** SPEC §6: "two releases differing only
  in audit record are the same authorization, while a release spent under a different
  policy version is not." It is `NOT NULL` because `append_event` returns
  `cursor.lastrowid`, which exists only after the audit row does -- so a mint with no
  audit_id is a mint whose audit record was never written, and SQLite refuses it.

This module imports `privacy.release` under `TYPE_CHECKING` only. It never constructs
a `Released` -- `mint_release` returns a `str` and the facade builds the value -- so
the need for the type is annotation-only, and the guard is what lets `release.py`
import nothing from here while `gate.py` imports both.
"""
from __future__ import annotations

import dataclasses
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from evidence_shape.canonical import canonical_json

from privacy.policy import Policy

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelTarget, Released

#: SPEC §6, B2: "The binding tuple is (model_target, prompt_fingerprint,
#: policy_version)." Three terms, and `audit_id` is deliberately not one.
BINDING_TERMS: tuple[str, str, str] = (
    "model_target", "prompt_fingerprint", "policy_version",
)

#: P7's third table, inside P1's single local database (§0). No `BEFORE DELETE`
#: trigger: §8.2's R6 binds `events`, and this is a capability record, not a
#: provenance record. Task 15 counts the guarded tables by name: the SUBSTRATE
#: thirteen (events, evidence, text_units, extraction_runs, exclusion_verdicts
#: and P2's eight bundle_* tables) plus Tasks 4 and 5's two supersede-bearing
#: tables, so the live count on a P7 connection is FIFTEEN. `release_ledger` is
#: not among them, which is what this comment is here to say.
RELEASE_LEDGER_DDL: str = """
CREATE TABLE IF NOT EXISTS release_ledger (
    release_id         TEXT PRIMARY KEY,
    model_target       TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    audit_id           INTEGER NOT NULL,
    minted_at          TEXT NOT NULL,
    spent_at           TEXT
);
"""


class ReleaseNotIssued(Exception):
    """The `release_id` is not in the ledger, so the gate never minted it.

    This is the refusal that makes the door real. A caller may construct a
    `Released` -- it is an ordinary frozen dataclass -- and doing so buys nothing.
    """


class ReleaseAlreadySpent(Exception):
    """SPEC §6: "A release is consumed on first transport use.\""""


class BindingMismatch(Exception):
    """The call does not match the terms the release was minted under.

    Raised before the spend and never after, so a mismatched call leaves the
    authorization intact.
    """


def _target_form(model_target: ModelTarget) -> str:
    """One stored form per model target.

    `canonical_json` over `dataclasses.asdict` rather than `str()`: §8.4's audit
    field is "which model received the data", and a hosted model is identified by
    provider AND id. A form that dropped either would let two different targets
    compare equal.
    """
    return canonical_json(dataclasses.asdict(model_target))


def _utcnow() -> str:
    """The ledger's own clock.

    The published `consume_release` signature carries no `observed_at`, and it is a
    contract with P8's transport. That is tolerable because `spent_at` is not a fact:
    the authoritative time of a model call is the audit record's `observed_at`, which
    the caller supplies, and nothing in P7 reads this column back as evidence.
    """
    return datetime.now(timezone.utc).isoformat()


def mint_release(conn: sqlite3.Connection, *, policy: Policy,
                 model_target: ModelTarget, prompt_fingerprint: str,
                 audit_id: int, minted_at: str) -> str:
    """Record one authorization and return its single-use id.

    Takes the `Policy` object, not a `policy_version` string: SPEC §6 says "the gate
    owns the policy, so the caller does not supply this value, it echoes it", and the
    minter is inside the gate. `consume_release` takes the echo.
    """
    release_id = "release-" + secrets.token_hex(16)
    conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, audit_id, minted_at, spent_at) "
        "VALUES (?, ?, ?, ?, ?, ?, NULL)",
        (release_id, _target_form(model_target), prompt_fingerprint,
         policy.policy_version, audit_id, minted_at),
    )
    return release_id


def consume_release(conn: sqlite3.Connection, released: Released, *,
                    model_target: ModelTarget, prompt_fingerprint: str,
                    policy_version: str) -> None:
    """Spend one release, once, against the terms it was minted under.

    Order: issued, then bound, then spent. Checking the binding after the spend
    would burn a token on a call that was never authorized for that model, and
    would report "already spent" for what is really a forgery-shaped event.
    """
    row = conn.execute("SELECT * FROM release_ledger WHERE release_id = ?",
                       (released.release_id,)).fetchone()
    if row is None:
        raise ReleaseNotIssued(
            f"{released.release_id!r} is not in the release ledger; the gate never "
            "minted it. A `Released` constructed outside `Gate.release` carries no "
            "authorization -- SPEC §6, and the reason a bypassing call cannot be "
            "constructed rather than merely being disallowed"
        )
    call = {
        "model_target": _target_form(model_target),
        "prompt_fingerprint": prompt_fingerprint,
        "policy_version": policy_version,
    }
    differing = [term for term in BINDING_TERMS if row[term] != call[term]]
    if differing:
        raise BindingMismatch(
            f"{released.release_id!r} was minted under different {differing}; SPEC §6 "
            "binds a release to (model_target, prompt_fingerprint, policy_version) so "
            "that §8.4's 'which model received the data' and 'the prompt fingerprint' "
            "stay true of the call that actually happened"
        )
    echoed = {
        "model_target": _target_form(released.model_target),
        "policy_version": released.policy_version,
    }
    disagreeing = [term for term, value in echoed.items() if call[term] != value]
    if disagreeing:
        raise BindingMismatch(
            f"{released.release_id!r} echoes {disagreeing} that the call does not "
            "use; the echo and the binding must agree or one of §8.4's audit fields "
            "is false for whichever the transport actually used"
        )
    spent = conn.execute(
        "UPDATE release_ledger SET spent_at = ? "
        "WHERE release_id = ? AND spent_at IS NULL",
        (_utcnow(), released.release_id),
    )
    if spent.rowcount != 1:
        raise ReleaseAlreadySpent(
            f"{released.release_id!r} was already consumed; SPEC §6: 'A release is "
            "consumed on first transport use.' The check and the mark are one "
            "statement so that single use survives a second caller arriving between "
            "them"
        )

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

This module imports the `Released` and `ModelTarget` TYPES under `TYPE_CHECKING`
only. It never constructs a `Released` -- `mint_release` returns a `str` and the
facade builds the value -- so the need for those is annotation-only, and that is what
lets `release.py` import nothing from here while `gate.py` imports both. The one
run-time import from `release.py` is `CONTENT_BOUND_FIELDS`, a tuple of field names:
the fourth binding term is folded from those three fields on both sides of the door,
and a second spelling of them here would be the drift the term exists to prevent.
"""
from __future__ import annotations

import dataclasses
import secrets
import sqlite3
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from evidence_shape.canonical import canonical_json, sha256_of

from privacy.policy import Policy
# `CONTENT_BOUND_FIELDS` is a tuple of names, not a type: the module docstring's rule
# is that this file never CONSTRUCTS a `Released`, and it still does not. The shape of
# a released item is published where the type is, so the gate that mints and the door
# that spends fold the same three fields.
from privacy.release import CONTENT_BOUND_FIELDS

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelTarget, Released

#: SPEC §6, B2: "The binding tuple is (model_target, prompt_fingerprint,
#: policy_version)." Three terms, and `audit_id` is deliberately not one.
#:
#: A FOURTH WAS ADDED ON 2026-09-02, AND IT EXCEEDS §6's STATED TUPLE. Recorded here
#: rather than in a commit message, because a reader comparing this line with the
#: design needs the reason at the line.
#:
#: The security review's CR-02 reproduced it: the three terms bind WHO receives the
#: bytes and UNDER WHAT POLICY, and nothing bound WHAT. A real release whose one
#: materialised item was `"[redacted]"` was spent on a `CallPayload` whose dossier
#: bytes were a dump of every `raw_value`, every `context_before`, every path and
#: every content hash, and the transport returned a `ModelResponse`. §6's own reason
#: for the tuple -- "binding and single use exist to keep the audit record truthful"
#: -- is what forces this: an audit record naming one redacted excerpt is FALSE of a
#: call that carried a corpus, exactly as it is false of a call to another model.
#: The three answer §8.4's "which model received the data"; the fourth answers what
#: the data was.
#:
#: It is a term rather than a field on `Released` deliberately. `Released` is an
#: ordinary frozen dataclass, so `dataclasses.replace` mints a copy carrying whatever
#: `materialised_items` a caller likes; a check against the object in the caller's
#: hand would compare a forgery with itself. The ledger row was written by the gate.
BINDING_TERMS: tuple[str, str, str, str] = (
    "model_target", "prompt_fingerprint", "policy_version", "content_digest",
)

#: P7's third table, inside P1's single local database (§0). No `BEFORE DELETE`
#: trigger: §8.2's R6 binds `events`, and this is a capability record, not a
#: provenance record. Task 15 counts the guarded tables by name: the SUBSTRATE
#: thirteen (events, evidence, text_units, extraction_runs, exclusion_verdicts
#: and P2's eight bundle_* tables) plus Tasks 4 and 5's two supersede-bearing
#: tables, so the live count on a P7 connection is FIFTEEN. `release_ledger` is
#: not among them, which is what this comment is here to say.
#:
#: `content_digest` IS NOT A SECOND COPY OF THE TEXT. SPEC §7 keeps content out of
#: this table -- `excerpts_included` is "(observation_key, span) pairs ... not a
#: second copy of the text" -- and a digest is not a copy: it is the fourth binding
#: term, it is one column wide whatever was released, and it never leaves the device.
#: CR-03's lesson applies to what is SPOKEN, and this is spoken to nobody: an unkeyed
#: digest is reversible by anyone who can guess the plaintext, and anyone who can read
#: this table can already read `evidence.raw_value` in the same database.
RELEASE_LEDGER_DDL: str = """
CREATE TABLE IF NOT EXISTS release_ledger (
    release_id         TEXT PRIMARY KEY,
    model_target       TEXT NOT NULL,
    prompt_fingerprint TEXT NOT NULL,
    policy_version     TEXT NOT NULL,
    content_digest     TEXT NOT NULL,
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


def content_digest(entries: Sequence[Mapping[str, object]]) -> str:
    """The fourth binding term: one value standing for everything released.

    ORDERED and COMPLETE. A set would let a caller reorder what the model reads, and
    a per-entry digest compared by membership would let a caller drop one. The
    `canonical_json` is `evidence_shape`'s, which is the same encoder the dossier
    body itself is written with, so the two sides cannot disagree about how a string
    is escaped.

    Each entry must carry exactly `CONTENT_BOUND_FIELDS` and nothing else; a mapping
    with a fifth key raises here rather than being projected down to four, because
    silently dropping what it does not recognise is how a check ignores the smuggled
    field it exists to catch. The projection is by NAME rather than by iteration
    order so a caller cannot change the digest by rebuilding the same dict.
    """
    projected = []
    for entry in entries:
        if set(entry) != set(CONTENT_BOUND_FIELDS):
            raise BindingMismatch(
                f"a released item carries {sorted(entry)} where the binding is over "
                f"{sorted(CONTENT_BOUND_FIELDS)}. A field this digest does not "
                "recognise is a field it would otherwise carry to the model unbound"
            )
        projected.append({field: entry[field] for field in CONTENT_BOUND_FIELDS})
    return sha256_of(canonical_json(projected))


def content_digest_of(items: Sequence[object]) -> str:
    """The same term, folded from `ReleasedItem`s rather than from wire entries.

    Two callers, one function, because the point of the term is that the gate's
    answer and the door's answer are comparable. The gate has `ReleasedItem`s; the
    door has parsed JSON. `ReleasedItem.content_mapping` is the bridge, and it lives
    on the type so neither side spells the three field names itself.
    """
    return content_digest([item.content_mapping() for item in items])


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
                 content_digest: str, audit_id: int, minted_at: str) -> str:
    """Record one authorization and return its single-use id.

    Takes the `Policy` object, not a `policy_version` string: SPEC §6 says "the gate
    owns the policy, so the caller does not supply this value, it echoes it", and the
    minter is inside the gate. `consume_release` takes the echo.

    `content_digest` has no default for the reason the other terms have none: a
    deployment that forgot it would mint a release bound to no content, and the door
    would have nothing to compare the bytes against -- which is the state CR-02
    reproduced. The column is `NOT NULL`, so a caller passing an empty string is
    refused here rather than in the comparison.
    """
    if not content_digest:
        raise BindingMismatch(
            "a release must be bound to what it released; an empty content digest "
            "is a release the door cannot check the payload against, and §6 binds "
            "so that the audit record stays true of the call that happened")
    release_id = "release-" + secrets.token_hex(16)
    conn.execute(
        "INSERT INTO release_ledger (release_id, model_target, prompt_fingerprint, "
        "policy_version, content_digest, audit_id, minted_at, spent_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, NULL)",
        (release_id, _target_form(model_target), prompt_fingerprint,
         policy.policy_version, content_digest, audit_id, minted_at),
    )
    return release_id


def consume_release(conn: sqlite3.Connection, released: Released, *,
                    model_target: ModelTarget, prompt_fingerprint: str,
                    policy_version: str, content_digest: str) -> None:
    """Spend one release, once, against the terms it was minted under.

    Order: issued, then bound, then spent. Checking the binding after the spend
    would burn a token on a call that was never authorized for that model, and
    would report "already spent" for what is really a forgery-shaped event.

    `content_digest` is the caller's recomputation FROM THE BYTES IT IS ABOUT TO
    SEND. It is compared against the ledger, and the ledger row is the gate's -- so
    a payload the gate never authorized fails here, before the spend and before the
    socket, and so does a `Released` minted by `dataclasses.replace` to claim it
    authorized one: the object is not what the bytes are checked against.
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
        "content_digest": content_digest,
    }
    differing = [term for term in BINDING_TERMS if row[term] != call[term]]
    if differing:
        raise BindingMismatch(
            f"{released.release_id!r} was minted under different {differing}; SPEC §6 "
            "binds a release to (model_target, prompt_fingerprint, policy_version), "
            "and CR-02 added content_digest, so that §8.4's 'which model received the "
            "data' and 'the prompt fingerprint' stay true of the call that actually "
            "happened -- and so that the record naming what was released describes "
            "the bytes that left"
        )
    # `content_digest` is deliberately NOT echoed here, and the reason is worth
    # keeping. The other two terms are echoed because `Released` CARRIES them and a
    # caller could hand `consume_release` a different value than the object holds --
    # then one of §8.4's two audit fields would be false for whichever the transport
    # actually used. Content has no such pair: the call's digest is folded from the
    # bytes about to be sent and the ledger's was folded by the gate, so if those two
    # agree the bytes ARE what was released, whatever the object in the caller's hand
    # says about itself. An echo was written here first and proved unable to fail --
    # every case it would have caught, the ledger comparison above already refuses --
    # and a check that cannot fire reads like protection without being any.
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

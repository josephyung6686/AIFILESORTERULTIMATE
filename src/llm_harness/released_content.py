# src/llm_harness/released_content.py
"""What the payload's bytes SAY was released, folded into P7's fourth binding term.

`transport.issue` takes two content-shaped arguments: the `Released` the gate minted,
and a `CallPayload` whose `canonical_dossier_bytes` are what the model is actually
shown. Until 2026-09-02 nothing compared them, and the security review's CR-02 spent
a real release -- one materialised item, `"[redacted]"` -- on a payload carrying every
`raw_value`, every `context_before`, every path and every content hash in the corpus.
The transport returned a `ModelResponse`.

This module is the door's half of the fix. `privacy.binding.content_digest` is the
gate's half; the two fold the same three fields of `privacy.release.
CONTENT_BOUND_FIELDS` and the ledger row is what they are compared through.

**Three checks, and the digest is only the third.** A digest over the entries it
recognises would be satisfied by a body carrying a faithful `released_evidence` list
beside a `"paths"` key, or by an entry carrying the correct four fields plus a fifth.
So:

1. The bytes must PARSE as the canonical dossier body. Arbitrary bytes are refused,
   which is the reviewer's own probe.
2. The body's top-level keys must be exactly `DOSSIER_BODY_KEYS`, and each released
   entry's keys exactly `RELEASED_EVIDENCE_FIELDS`. Not a subset -- exactly. A key
   this module does not recognise is a key nothing has bound, and §8.4's always-local
   set is what would ride in it.
3. The entries fold to the ledger's digest, so a substituted value, a reordering, a
   dropped entry and an added entry are each a mismatch.

**What this does NOT bind, stated plainly, because the docstring it replaces did not.**
The body's own builder-authored strings -- `subject_ref`, `evidence_items[].location`,
`evidence_items[].basis`, `conflicts[].kind`, `call_site`, `eligibility_reason` -- are
bound in SHAPE and not in CONTENT: check 2 proves no unexpected key exists, and
nothing here proves that what a producer put in `subject_ref` was not a path. It
cannot: the gate never saw those fields, so there is no authorization to compare them
against. `records.DossierRequest` validates `evidence_ref` and `basis` only. That is a
real gap and it is the review's, listed under what it could not check; it is written
here so the next reader looks rather than stops.

`observation_key` is on the wire and is not folded. `wire_handles` emits
`HMAC(install key, observation_key)`, the transport holds neither the key nor the
keying function, and the gate holds only the unkeyed identifier -- so binding it would
mean handing the transport a credential or unkeying the wire. See
`privacy.release.ReleasedItem.content_mapping`, which is where that is decided.

**DOSSIER_BODY_KEYS is a constant and `dossier._body` is its source.** They are kept
honest by `tests/integration/test_released_content_binding.py`, which asserts the real
builder's bytes carry exactly these keys. A body that gains a key fails that test and
fails this door -- loudly, and in the direction that refuses.
"""
from __future__ import annotations

import json

from llm_harness.records import MalformedRecord
from privacy.binding import content_digest
from privacy.release import RELEASED_EVIDENCE_FIELDS

#: Every top-level key `dossier._body` writes into the model-visible dossier.
DOSSIER_BODY_KEYS: frozenset[str] = frozenset({
    "allowed_vocabulary", "call_site", "conflicts", "eligibility_reason",
    "evidence_items", "field_glossary", "max_dossier_tokens", "plan_version",
    "policy_version", "reduction_rung", "released_evidence", "response_schema",
    "shaping_policy", "subject_ref",
})

#: The one key inside it the release authorized.
RELEASED_EVIDENCE_KEY: str = "released_evidence"


def released_content_digest(canonical_dossier_bytes: bytes) -> str:
    """Fold the payload's own bytes into the term the ledger holds.

    Raises `MalformedRecord` for anything that is not a dossier body, and
    `BindingMismatch` (from `content_digest`) for an entry carrying a field the
    binding does not cover. Both are refusals BEFORE the ledger spend and before the
    client call, so a rejected payload leaves the authorization intact.
    """
    try:
        body = json.loads(canonical_dossier_bytes)
    except (ValueError, UnicodeDecodeError) as exc:
        raise MalformedRecord(
            "the payload's dossier bytes are not the canonical dossier body. §8.4 "
            "requires policy enforcement BEFORE content reaches a model, and bytes "
            "the gate cannot be shown to have authorized are exactly what that "
            "sequencing is about"
        ) from exc
    if not isinstance(body, dict):
        raise MalformedRecord(
            f"the dossier body is a {type(body).__name__}; `_body` writes one JSON "
            "object and the door reads no other shape")
    if set(body) != DOSSIER_BODY_KEYS:
        unexpected = sorted(set(body) - DOSSIER_BODY_KEYS)
        absent = sorted(DOSSIER_BODY_KEYS - set(body))
        raise MalformedRecord(
            f"the dossier body carries unexpected keys {unexpected} and is missing "
            f"{absent}. The released evidence is the only part of these bytes the "
            "gate authorized, so a key beside it is a key nothing bound -- which is "
            "how a faithful evidence list and a corpus travel in one payload"
        )
    entries = body[RELEASED_EVIDENCE_KEY]
    if not isinstance(entries, list):
        raise MalformedRecord(
            f"{RELEASED_EVIDENCE_KEY!r} is a {type(entries).__name__}; `_body` writes "
            "a list of released items and the door reads no other shape")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != set(RELEASED_EVIDENCE_FIELDS):
            raise MalformedRecord(
                f"a released item carries "
                f"{sorted(entry) if isinstance(entry, dict) else type(entry).__name__}"
                f" where `_released_body` writes {sorted(RELEASED_EVIDENCE_FIELDS)}. "
                "A fifth field is how the context §8.4 keeps local rides beside the "
                "value redaction removed from it")
    return content_digest([
        {field: entry[field] for field in entry if field != "observation_key"}
        for entry in entries
    ])

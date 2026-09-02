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

**Check 2 reaches all the way down, since 2026-09-02.** The first version checked the
top-level key set and `released_evidence` entries, and said the builder-authored slots
were bound in shape only. The re-verification took that at its word and ran it: a body
with exactly `DOSSIER_BODY_KEYS`, a faithful `released_evidence` list folding to the
ledger digest, and the corpus in the other slots -- `issue` returned `ModelResponse`
with `current_path` on the wire. `evidence_items` entries had no key-set check at all,
one function away from `released_evidence`, which did.

So every slot that CAN be bound is now bound against something the transport
legitimately holds, and nothing is bound against a guess:

  * `response_schema` / `shaping_policy` -- EQUALITY with the `PromptDefinition` the
    payload carries. These are the two injected authorities `dossier._as_text`
    decodes out of it, so the transport already holds the only correct answer.
  * `field_glossary` -- RECOMPUTED from the body's own `allowed_vocabulary`. Its
    comment in `_body` calls it "the one key here whose content is the same on every
    file in every corpus", which is exactly what makes it checkable.
  * `subject_ref`, `conflicts[].conflict_id` -- `_body` runs `wire_handle` over both
    unconditionally, so an unkeyed string is a value that did not come through the
    builder. `evidence_items[].evidence_ref` is NOT checked this way: `wire_ref`
    deliberately leaves a `file_id` unkeyed, because it is a `uuid4` that inverts to
    nothing and is what the model's own `members` list is read against.
  * `call_site`, `eligibility_reason`, `reduction_rung`, `evidence_items[].basis`,
    `.reliability_state` -- membership in the closed vocabularies P8 publishes.
  * `evidence_items` / `conflicts` entries -- exact key sets, the same rule
    `released_evidence` gets, derived from the dataclasses rather than retyped.
  * `policy_version` -- equality with the payload's, which `_require_binding` has
    already tied to the release.

**What is STILL not bound, and it is three things.** `evidence_items[].location`,
`evidence_items[].kind` and `conflicts[].kind` are free strings with no vocabulary in
`records.py` to check them against, and `allowed_vocabulary` is the caller's declared
answer vocabulary, legitimately arbitrary -- P9 passes group labels, P10 node ids, P11
residual actions, none of them field names, so it cannot be bound to the glossary
either. Nothing here proves a producer did not put a path in one of them; the gate
never saw those fields, so there is no authorization to compare them against.

That list is not maintained by this sentence. `test_what_is_still_not_bound_is_named_
and_nothing_else_is` asserts it, so narrowing the residual without narrowing this
paragraph turns the suite red -- which is the failure mode the docstring this module
replaced actually had.

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

import dataclasses
import json

from llm_harness.dossier import field_glossary
from llm_harness.records import (
    Conflict,
    EvidenceItem,
    MalformedRecord,
    PromptDefinition,
)
from llm_harness.vocabulary import (
    CALL_SITES,
    ELIGIBILITY_BY_SITE,
    EVIDENCE_BASES,
    REDUCTION_RUNGS,
)
# P4's, not P8's: `EvidenceItem.__post_init__` checks `reliability_state` against
# `evidence_shape.vocabulary` and the door checks the same list, so the two cannot
# disagree about what a reliability state is.
from evidence_shape.vocabulary import RELIABILITY_STATES
from llm_harness.wire_handles import HANDLE_PREFIX
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

#: The keys `dossier._evidence_item_body` and `_body`'s conflict comprehension write,
#: READ from the dataclasses so a field added to either is a door that refuses until
#: somebody looks, rather than a slot that silently carries whatever is put in it.
EVIDENCE_ITEM_FIELDS: frozenset[str] = frozenset(
    f.name for f in dataclasses.fields(EvidenceItem))
CONFLICT_FIELDS: frozenset[str] = frozenset(
    f.name for f in dataclasses.fields(Conflict))

#: The prefix `wire_handles.wire_handle` puts on every identifier it keys.
_KEYED: str = HANDLE_PREFIX + ":"


def _refuse(message: str) -> None:
    raise MalformedRecord(message)


def _require_member(value: object, vocabulary, *, slot: str) -> None:
    if value not in vocabulary:
        _refuse(
            f"{slot} is {value!r}, which is not one of {sorted(vocabulary)}. It is a "
            "closed vocabulary P8 publishes, and a door that let a free string sit "
            "in one would be trusting the builder it is here to check")


def _require_keyed(value: object, *, slot: str) -> None:
    if not isinstance(value, str) or not value.startswith(_KEYED):
        _refuse(
            f"{slot} is not a keyed handle. `dossier._body` runs `wire_handle` over "
            "it unconditionally, so an unkeyed value here did not come through the "
            "builder -- and an identifier that reaches the model unkeyed is the "
            "reversible digest CR-03 removed")


def _require_entries(entries: object, expected: frozenset[str], *, slot: str) -> list:
    if not isinstance(entries, list):
        _refuse(f"{slot} is a {type(entries).__name__}; `_body` writes a list")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != expected:
            _refuse(
                f"an entry of {slot} carries "
                f"{sorted(entry) if isinstance(entry, dict) else type(entry).__name__}"
                f" where the builder writes {sorted(expected)}. A key this door does "
                "not recognise is a key nothing bound, which is how a faithful list "
                "and a corpus travel in one payload")
    return entries


def released_content_digest(canonical_dossier_bytes: bytes, *,
                            prompt_definition: PromptDefinition,
                            policy_version: str) -> str:
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
    # The two injected authorities, by EQUALITY: the transport holds the definition
    # they are decoded from, so there is exactly one correct answer and no shape to
    # argue about.
    for slot, raw in (("response_schema", prompt_definition.response_schema_bytes),
                      ("shaping_policy", prompt_definition.shaping_policy_bytes)):
        if body[slot] != raw.decode("utf-8"):
            _refuse(
                f"{slot} is not the one this call's `PromptDefinition` carries. It is "
                "an authored authority meant to CONSTRAIN the answer; a caller who "
                "can rewrite it can hand the model any instructions it likes under a "
                "fingerprint that says otherwise")

    _require_member(body["call_site"], CALL_SITES, slot="call_site")
    _require_member(body["eligibility_reason"],
                    ELIGIBILITY_BY_SITE[body["call_site"]],
                    slot="eligibility_reason")
    _require_member(body["reduction_rung"], REDUCTION_RUNGS, slot="reduction_rung")
    _require_keyed(body["subject_ref"], slot="subject_ref")

    if body["policy_version"] != policy_version:
        _refuse(
            "the dossier body's policy_version is not the payload's, which "
            "`_require_binding` has already tied to the release; §8.4's record names "
            "the authorizing policy and two answers in one call make it false")

    # Built from `allowed_vocabulary` and nothing else, which is what makes it
    # checkable rather than merely declared -- so it is recomputed, never trusted.
    if body["field_glossary"] != field_glossary(body["allowed_vocabulary"]):
        _refuse(
            "field_glossary is not what this call's allowed_vocabulary produces. "
            "`_body` builds it from the vocabulary and nothing else, so a glossary "
            "that disagrees carries text no authored meaning put there")

    for item in _require_entries(body["evidence_items"], EVIDENCE_ITEM_FIELDS,
                                 slot="evidence_items"):
        _require_member(item["basis"], EVIDENCE_BASES, slot="evidence_items[].basis")
        _require_member(item["reliability_state"], RELIABILITY_STATES,
                        slot="evidence_items[].reliability_state")

    for conflict in _require_entries(body["conflicts"], CONFLICT_FIELDS,
                                     slot="conflicts"):
        _require_keyed(conflict["conflict_id"], slot="conflicts[].conflict_id")

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

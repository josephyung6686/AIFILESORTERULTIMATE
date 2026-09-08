# src/llm_harness/dossier.py
"""The canonical post-release dossier: the exact bytes the model is shown.

SPEC §1: the dossier is the only input to a model call, and it is closed-world.
That is only true if the bytes carry everything the response is judged against —
the envelope, the allowed vocabulary, what P7 actually released (address, value,
zone), the builder's reference metadata, the conflicts, and
the authored response schema and shaping policy.

`dossier_id` is the content address of those bytes. It is deliberately NOT
`release_id`: a release id is a single-use spend capability, so using it as the
identity meant two calls over identical content had two identities and no call
could be recognised as a replay of another.

This module authors no content. Every value it serialises comes from P7's
`Released`, the builder's `DossierRequest`, the injected `PromptDefinition`, or
`library/field_glossary.json` -- and that file authors none either: every meaning
in it is quoted from something already ratified, and names the source it was
quoted from.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path

from evidence_shape.canonical import canonical_json
from llm_harness.fingerprint import dossier_content_address
from llm_harness.records import (
    Conflict,
    Dossier,
    DossierRequest,
    EvidenceItem,
    FolderLevel,
    MalformedRecord,
    PromptDefinition,
    ReleasedEvidence,
    ValidationUnavailable,
)
from llm_harness.wire_handles import WIRE_HANDLE_KEY, wire_handle, wire_ref
from privacy.release import Released


GLOSSARY_FILE = Path(__file__).resolve().parent / "library" / "field_glossary.json"


class GlossaryRequired(RuntimeError):
    """The shipped glossary is missing or is not the shape its consumer reads."""


@lru_cache(maxsize=1)
def _meanings() -> Mapping[str, str]:
    """Every authored field meaning, by key. No fallback and no empty default.

    An empty glossary would silently restore the state the owner ruled against: a
    model shown 56 bare keys, guessing or declining. It would also do so invisibly,
    because a dossier with no meanings is well-formed. So a missing file refuses.
    """
    if not GLOSSARY_FILE.is_file():
        raise GlossaryRequired(
            f"{GLOSSARY_FILE} is not on disk; this package ships no default meaning")
    loaded = json.loads(GLOSSARY_FILE.read_text(encoding="utf-8"))
    fields = loaded.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise GlossaryRequired(f"{GLOSSARY_FILE} carries no field meanings")
    return {key: entry["meaning"] for key, entry in fields.items()}


def field_glossary(allowed_vocabulary: Sequence[str]) -> list[dict[str, str]]:
    """What each field key of THIS call means -- and nothing about this file.

    **A LIST OF `field`/`meaning` PAIRS, AND NOT A MAP FROM A FIELD KEY TO A STRING**
    (`104` R-163). The answer this call asks for is `payload`: an answerable field
    key beside one string. A JSON object mapping each answerable field key to one
    string is that same table, sitting in the dossier already filled in -- while
    `released_evidence`, the only place a value may be taken from, is a list of
    objects keyed by observation and not by field at all. So the one structure in
    the dossier shaped like the answer was the one place a value may never come
    from, and the model filled the answer out of it: r15 proposed the literal
    `work_type` as a value 16 times, the phrase out of its meaning 6 times, and
    `term`'s own sentence 3 times. What it wears now is the dossier's OWN shape for
    per-field material that is instruction and not evidence -- `_folder_levels_body`'s,
    a list of objects whose first key is `field`.

    **Every sentence is unchanged, and that is deliberate.** `104` §16.3 rules that
    the normaliser is not at fault and that laundering the symptom out of the answer
    is not the fix; the two sentences R-163 is actually about are §15.4 item 16's,
    the owner's to write. Nothing here edits the library.

    **In the vocabulary's order, which is one order rather than two.**
    `model_facts.order_vocabulary_by_levels` puts the situation's own folder levels
    at the head of `allowed_vocabulary` on measured grounds, and `canonical_json`
    then re-sorted this object's keys behind it -- so the dossier printed the
    vocabulary in the tree's nesting order and the glossary alphabetically. That
    function names the failure in its own words: *"two orders of one list in one
    document is a contradiction the model has to resolve."* A list keeps the order it
    is given, and a repeated field is dropped rather than explained twice, which the
    object shape did silently.

    `76` §10.1 records the glossary decision as owed and names three options; the
    owner chose the one where the dossier carries the meanings. The defence `82`
    §7.1 would otherwise have relied on was rule 2 -- *"if a key's meaning is not
    plain from the key itself, decline that field"* -- which is safe and costs real
    coverage on `subject`, `work_type`, `purpose`, `record_type`, `project` and
    `duplicate_family`, the fields that matter most. Told, the model need neither
    guess nor decline.

    **The vocabulary is the only input, and that is the whole bound.** A meaning
    defines a FIELD; it is never a hint about the FILE. Because nothing about the
    file, the person or the corpus can reach this function, no entry can vary
    between two files and nothing in §8.4's always-local set has a route in.

    A field with no authored meaning is ABSENT, never filled: `library/
    field_glossary.json` records those in `owed`, and for them `82` rule 2's
    fail-closed position still holds -- which is what it was for.
    """
    meanings = _meanings()
    return [{"field": field, "meaning": meanings[field]}
            for field in dict.fromkeys(allowed_vocabulary) if field in meanings]


def _requested_keys(request: DossierRequest) -> frozenset[str]:
    """Observation keys the builder asked P7 for. Not every item kind carries one."""
    return frozenset(
        item.observation_key
        for item in request.model_call_request.requested_items
        if getattr(item, "observation_key", None)
    )


def _released_evidence(released: Released) -> tuple[ReleasedEvidence, ...]:
    return tuple(
        ReleasedEvidence(
            observation_key=item.observation_key,
            address=item.span,
            value=item.value,
            zone=item.zone,
            # `104` R-135. Not on the wire and not in the dossier address: the four
            # keys `_released_body` writes are unchanged, so this crosses into P8's
            # record and stops there. `report_from_verdicts` is the only reader, and
            # without it the two exposure counters could only ever report zero.
            unit_length=item.unit_length,
            # `104` R-135's classification, decided at the point of resolution and
            # carried straight through. Neither field is written by `_released_body`,
            # so the four model-visible keys and the dossier address are unchanged.
            whole_heading_unit=item.whole_heading_unit,
            # `104` R-152's answer, on the same terms as the line above it.
            whole_line_unit=item.whole_line_unit,
        )
        for item in released.materialised_items
    )


def _evidence_item_body(item: EvidenceItem, *, handle_key: bytes) -> dict:
    return {
        "basis": item.basis,
        "evidence_ref": wire_ref(item.evidence_ref, key=handle_key),
        "excerpt_span": list(item.excerpt_span) if item.excerpt_span else None,
        "kind": item.kind,
        "location": item.location,
        "reliability_state": item.reliability_state,
    }


def _released_body(item: ReleasedEvidence, *, handle_key: bytes) -> dict:
    """The model-visible bytes for one released item, and only what P7 released.

    This wrote the raw text on either side of the requested span beside the
    redacted value, so an 8-character span put its whole text unit in front of
    the model. §8.4 keeps "complete extracted text" local; the local audit
    manifest still carries it.

    `observation_key` is keyed here rather than printed. It is a digest of the
    file's bytes, of the locator and of the raw value, and the locator is printed
    in the clear as `address` one line above -- so the un-keyed key was a
    dictionary attack on the value beside it, and the value beside it is the one
    redaction had already removed.
    """
    return {
        "address": item.address,
        "observation_key": wire_handle(item.observation_key, key=handle_key),
        "value": item.value,
        "zone": item.zone,
    }


def _folder_levels_body(
    folder_levels: Sequence[FolderLevel],
    allowed_vocabulary: Sequence[str],
) -> list[dict]:
    """The situation's own folder levels, and the check that they are a projection.

    `allowed_vocabulary` is the FLAT closed list §3.5 turns on -- the universal
    fields plus every active schema's field set -- and it says nothing about which
    of those fields the person's chosen situation actually builds folders out of.
    Measured on 199 real files, the model answered accordingly: 59 `file_type`, 34
    `authored_by`, 19 `creation_date`, and one `work_type`, which is a REQUIRED
    level and decides where the file goes. It was answering the question it was
    asked.

    **Every value here is the library's, in the library's order.** The field key is
    P6's, the label is the shipped applicability row's own `RoleBinding.label`, and
    `required`/`optional` is the template definition's own word for that dimension.
    Order is list position, which is `default_order`'s `order_index` -- the order
    the folders would actually nest in.

    **The projection is enforced, not declared.** A level naming a field outside
    `allowed_vocabulary` would be the model instructed to fill a key the validator
    rejects under check 1 for not being in the active schema:
    `model_facts.pending_fields_for` names that failure exactly -- "a model measured
    against one list and validated against another can be rejected for obeying its
    instructions". So it refuses here, before the release is spent, rather than
    manufacturing a rejection later.

    **Nothing about the file reaches this.** The two arguments are a library
    constant and a closed vocabulary, so no entry can differ between two files in
    one corpus and §8.4's always-local set has no route in -- the same bound
    `field_glossary` above stands on.
    """
    allowed = set(allowed_vocabulary)
    outside = [level.field for level in folder_levels if level.field not in allowed]
    if outside:
        raise MalformedRecord(
            f"folder levels {sorted(outside)} name fields this call's "
            "allowed_vocabulary does not carry. The vocabulary and the levels are "
            "one computation: a level outside it is the model told to fill a field "
            "its answer will be rejected for proposing"
        )
    return [{"field": level.field, "label": level.label,
             "requirement": level.requirement} for level in folder_levels]


def _as_text(raw: bytes, *, name: str) -> str:
    """An injected authority, as the model sees it.

    These were emitted as hex into what this module calls the exact bytes the
    model is shown. Hex is right in `prompt_fingerprint`, where `canonical_json`
    cannot encode raw bytes; in the model-visible body it renders the two
    authorities meant to constrain the answer unreadable to the model. P8 authors
    neither and does not repair them: bytes that are not text cannot constrain
    anything, and that is a caller contract failure, not a fallback.
    """
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MalformedRecord(
            f"{name} is shown to the model and must be text it can read"
        ) from exc


#: THE FRAME: the material that is the same for every file of one situation. The
#: prompt's own two blobs lead it because they are the largest and the most constant
#: (3,999 and 2,378 bytes on the A_fact revision); the vocabulary, its glossary and
#: the folder levels follow, which are the situation's rather than the run's and
#: change only when a file's OPEN field set changes.
_FRAME_KEYS: tuple[str, ...] = (
    "call_site", "response_schema", "shaping_policy", "policy_version",
    "plan_version", "max_dossier_tokens", "reduction_rung", "eligibility_reason",
    "allowed_vocabulary", "field_glossary", "folder_levels",
)

#: THIS FILE, and nothing else. `subject_ref` first because it always differs, so
#: the shared run ends at the earliest point it possibly can and nothing about one
#: person's file can sit inside another's prefix.
_FILE_KEYS: tuple[str, ...] = (
    "subject_ref", "conflicts", "evidence_items", "released_evidence",
)

#: `104` R-58. `canonical_json` sorts, and sorted the fifteen keys INTERLEAVE the
#: two halves above: `conflicts` lands third and `evidence_items` fifth, so the
#: bytes stop being shared 205 into an 8,999-byte body -- 2.3% -- and the glossary
#: and the folder levels, which had not changed at all, are re-read on every call.
#: Measured on the provider's own `prompt_cache_hit_tokens` over one dossier: 90% of
#: the prompt served from cache frame first against 39% sorted, about 2,560 tokens a
#: call. `104` R-52 makes the same argument about `num_ctx` and the KV cache; this is
#: it at the byte level.
#:
#: A CONSTANT and not insertion order, because insertion order is whatever the next
#: edit to `_body` happens to type, and a prefix that depends on that is a prefix
#: nobody can rely on. `_ordered_body` refuses a mapping whose keys are not exactly
#: these, so a sixteenth key is a failure at the seam rather than a silent append.
_BODY_ORDER: tuple[str, ...] = _FRAME_KEYS + _FILE_KEYS


def _ordered_body(body: Mapping[str, object]) -> bytes:
    """`canonical_json`'s form, in `_BODY_ORDER` rather than in sorted order.

    **Only the top level moves.** Every VALUE still goes through `canonical_json`,
    so nested objects stay key-sorted, unpadded, UTF-8 and never ASCII-escaped --
    which is what every cache key and replay diff outside these bytes depends on,
    and what makes this still one form per value. Two equal dossiers still serialise
    identically; a `dossier_id` is still a content address of the result.
    """
    if tuple(sorted(body)) != tuple(sorted(_BODY_ORDER)):
        raise MalformedRecord(
            "the model-visible body is emitted in a documented order and these are "
            f"not its keys: {sorted(set(body) ^ set(_BODY_ORDER))}. A key with no "
            "place in the order would be written wherever it was built, and the "
            "template tells the model the dossier has these keys and no others."
        )
    return ("{" + ",".join(
        f"{canonical_json(key)}:{canonical_json(body[key])}"
        for key in _BODY_ORDER) + "}").encode("utf-8")


def _body(
    *,
    call_site: str,
    subject_ref: str,
    eligibility_reason: str,
    plan_version: str | None,
    policy_version: str,
    max_dossier_tokens: int,
    reduction_rung: str,
    allowed_vocabulary: Sequence[str],
    folder_levels: Sequence[FolderLevel],
    evidence_items: Sequence[EvidenceItem],
    conflicts: Sequence,
    released_evidence: Sequence[ReleasedEvidence],
    prompt: PromptDefinition,
    handle_key: bytes,
) -> bytes:
    """One canonical form. `dossier_id`, `release_id` and `audit_id` are absent.

    The mapping below is written in the order a reader of these fifteen keys would
    want them, alphabetically; `_ordered_body` emits them in `_BODY_ORDER`, which is
    frame first. The two orders are deliberately different and the constant is the
    one that reaches a model (`104` R-58).

    **This is the only function in the product that writes an identifier into
    model-visible bytes**, which is why the keying lives here and nowhere else.
    Four slots carry one, and each is keyed by `wire_handles` before it is
    written: `subject_ref`, every `conflict_id`, every released
    `observation_key`, and every `evidence_ref` that is a P4 key. Everything
    upstream -- the `Dossier` record, the `llm_dossier` payload, the audit, the
    resolver -- keeps the identifiers it always had.
    """
    return _ordered_body({
        "allowed_vocabulary": list(allowed_vocabulary),
        "call_site": call_site,
        # `conflict_id` is `f"{group_id}:{kind}"` at P9's seam, so it carried the
        # same reversible group digest `subject_ref` did. Keyed, not parsed apart:
        # P8 does not know what a producer put in an id and must not have to.
        "conflicts": [
            {"conflict_id": wire_handle(item.conflict_id, key=handle_key),
             "kind": item.kind}
            for item in conflicts
        ],
        "eligibility_reason": eligibility_reason,
        "evidence_items": [
            _evidence_item_body(item, handle_key=handle_key)
            for item in evidence_items
        ],
        # Built from `allowed_vocabulary` and nothing else, deliberately: it is the
        # one key here whose content is the same on every file in every corpus.
        "field_glossary": field_glossary(allowed_vocabulary),
        # The template library's answer for the situation the person named, and a
        # projection of the key above it. Empty at every site that designs no tree.
        "folder_levels": _folder_levels_body(folder_levels, allowed_vocabulary),
        "max_dossier_tokens": max_dossier_tokens,
        "plan_version": plan_version,
        "policy_version": policy_version,
        "reduction_rung": reduction_rung,
        "released_evidence": [
            _released_body(item, handle_key=handle_key)
            for item in released_evidence
        ],
        "response_schema": _as_text(
            prompt.response_schema_bytes, name="response_schema_bytes"),
        "shaping_policy": _as_text(
            prompt.shaping_policy_bytes, name="shaping_policy_bytes"),
        # Keyed WHOLE, never parsed. `records.DossierRequest` validates nothing
        # about `subject_ref`; today's producers pass a group id, but the field is
        # a free string and the next producer's could be a title or a path.
        "subject_ref": wire_handle(subject_ref, key=handle_key),
    })


def canonical_dossier_bytes(
    dossier: Dossier, prompt: PromptDefinition, *, handle_key: bytes,
) -> bytes:
    """The model-visible dossier bytes for an already-materialised `Dossier`.

    `handle_key` has no default. A caller with no key gets `WireHandleKeyRequired`
    and not a set of bytes a recipient could reverse.
    """
    return _body(
        call_site=dossier.call_site,
        subject_ref=dossier.subject_ref,
        eligibility_reason=dossier.eligibility_reason,
        plan_version=dossier.plan_version,
        policy_version=dossier.policy_version,
        max_dossier_tokens=dossier.max_dossier_tokens,
        reduction_rung=dossier.reduction_rung,
        allowed_vocabulary=dossier.allowed_vocabulary,
        folder_levels=dossier.folder_levels,
        evidence_items=dossier.evidence_items,
        conflicts=dossier.conflicts,
        released_evidence=dossier.released_evidence,
        prompt=prompt,
        handle_key=handle_key,
    )


def dossier_address(
    dossier: Dossier, prompt: PromptDefinition, *, handle_key: bytes,
) -> str:
    """The content address of a dossier's model-visible bytes."""
    return dossier_content_address(
        canonical_dossier_bytes(dossier, prompt, handle_key=handle_key),
        allowed_vocabulary=dossier.allowed_vocabulary,
        allowed_schema_bytes=prompt.response_schema_bytes,
    )


def dossier_from_stored_body(body: Mapping[str, object], *,
                             release_id: str) -> Dossier:
    """Rebuild a `Dossier` from the body `store.record_dossier` wrote. `104` R-127.

    **It is HERE and not beside the row it reads, because there is one dossier
    writer.** `test_p8_dossier.test_only_the_dossier_module_and_the_fixtures_
    construct_a_dossier` says why in its own words -- "a second dossier writer can
    address a dossier differently from `build_dossier`" -- and a rebuild is
    exactly that risk: a record put back together with a field dropped or a tuple
    left a list would re-derive different model-visible bytes and so a different
    content address. Keeping it beside `build_dossier` and `dossier_address` puts
    the rebuild and the check that it round-trips in one place, where a change to
    the record's shape reaches both.

    **`release_id` is a parameter because the row does not hold one.**
    `record_dossier` strips it -- the row is addressed by content, and the
    capability that paid for a call is not content -- and `Dossier.__post_init__`
    refuses a record without one. The caller reads it off the response it is about
    to re-judge, which is the release that actually paid for those bytes.

    `folder_levels` is read with a default because it is defaulted on the record:
    a row written before that field existed carries no such key, and refusing one
    would make an old database unreadable to say that a new field is absent.
    """
    if not release_id:
        raise MalformedRecord(
            "a stored dossier is rebuilt with the release that paid for the "
            "response being re-judged; P8 does not mint one to fill the field")
    return Dossier(
        dossier_id=body["dossier_id"],
        call_site=body["call_site"],
        subject_ref=body["subject_ref"],
        eligibility_reason=body["eligibility_reason"],
        plan_version=body["plan_version"],
        policy_version=body["policy_version"],
        allowed_vocabulary=tuple(body["allowed_vocabulary"]),
        evidence_items=tuple(
            EvidenceItem(
                evidence_ref=item["evidence_ref"],
                kind=item["kind"],
                location=item["location"],
                excerpt_span=(None if item["excerpt_span"] is None
                              else tuple(item["excerpt_span"])),
                reliability_state=item["reliability_state"],
                basis=item["basis"],
            ) for item in body["evidence_items"]),
        conflicts=tuple(
            Conflict(conflict_id=item["conflict_id"], kind=item["kind"])
            for item in body["conflicts"]),
        released_evidence=tuple(
            ReleasedEvidence(
                observation_key=item["observation_key"],
                address=item["address"],
                value=item["value"],
                zone=item["zone"],
                # `104` R-135's two, read the way `folder_levels` is read below and
                # for the same reason: they are defaulted on the record, so a row
                # written before they existed carries no such key and refusing one
                # would make an old database unreadable to say a new field is absent.
                #
                # DROPPING THEM WAS NOT A LOST STATISTIC. `store.load_dossier` compares
                # the rebuilt record against the row key by key, so a rebuild short of
                # a field the row holds is `MalformedRecord` -- and R-127's
                # re-judgement of a stored response goes through that check. Every
                # dossier recorded since R-135 carries these, so every one of them
                # would have been refused, and `_reuse_is_current` would have answered
                # `False` and BOUGHT the model answer again. The guard was right; the
                # rebuild was short.
                unit_length=item.get("unit_length"),
                whole_heading_unit=item.get("whole_heading_unit", False),
                # `104` R-152, read the same way and for the paragraph above's reason:
                # `store.record_dossier` serialises the whole record, so a row written
                # since this field existed HOLDS it, and a rebuild short of it is
                # `MalformedRecord` out of a reuse decision.
                whole_line_unit=item.get("whole_line_unit", False),
            ) for item in body["released_evidence"]),
        max_dossier_tokens=body["max_dossier_tokens"],
        reduction_rung=body["reduction_rung"],
        release_id=release_id,
        folder_levels=tuple(
            FolderLevel(
                field=item["field"], label=item["label"],
                requirement=item["requirement"],
            ) for item in body.get("folder_levels", ())),
    )


def build_dossier(
    request: DossierRequest,
    released: Released,
    *,
    reduction_rung: str,
    allowed_vocabulary: Sequence[str],
    folder_levels: Sequence[FolderLevel],
    prompt: PromptDefinition,
    handle_key: bytes,
) -> Dossier | ValidationUnavailable:
    """Materialise one dossier from a live release. Fails closed, before egress.

    Three key sets must agree: what the builder requested of P7, what P7 released,
    and what the builder described. A released key nobody requested is a forged or
    mismatched release; a released key with no builder metadata means P8 would have
    to invent `kind`, `location`, `reliability_state` and `basis`, which §1 forbids.

    A missing `handle_key` is one of the three, and it is checked first: every
    identifier below reaches a model keyed, and there is no unkeyed fallback to
    fall back to.
    """
    if not isinstance(handle_key, (bytes, bytearray)) or not handle_key:
        return ValidationUnavailable(missing=(WIRE_HANDLE_KEY,))
    released_evidence = _released_evidence(released)
    missing: list[str] = []
    if not released_evidence:
        missing.append("released_evidence")
    released_keys = {item.observation_key for item in released_evidence}
    if released_keys - _requested_keys(request):
        missing.append("released_key_not_requested")
    if released_keys - {item.evidence_ref for item in request.evidence_items}:
        missing.append("builder_evidence_metadata")
    if missing:
        return ValidationUnavailable(missing=tuple(missing))

    body = _body(
        call_site=request.call_site,
        subject_ref=request.subject_ref,
        eligibility_reason=request.eligibility_reason,
        plan_version=request.plan_version,
        policy_version=released.policy_version,
        max_dossier_tokens=request.model_call_request.max_dossier_tokens,
        reduction_rung=reduction_rung,
        allowed_vocabulary=allowed_vocabulary,
        folder_levels=folder_levels,
        evidence_items=request.evidence_items,
        conflicts=request.conflicts,
        released_evidence=released_evidence,
        prompt=prompt,
        handle_key=handle_key,
    )
    return Dossier(
        dossier_id=dossier_content_address(
            body,
            allowed_vocabulary=allowed_vocabulary,
            allowed_schema_bytes=prompt.response_schema_bytes,
        ),
        call_site=request.call_site,
        subject_ref=request.subject_ref,
        eligibility_reason=request.eligibility_reason,
        plan_version=request.plan_version,
        policy_version=released.policy_version,
        allowed_vocabulary=tuple(allowed_vocabulary),
        folder_levels=tuple(folder_levels),
        evidence_items=request.evidence_items,
        conflicts=request.conflicts,
        released_evidence=released_evidence,
        max_dossier_tokens=request.model_call_request.max_dossier_tokens,
        reduction_rung=reduction_rung,
        release_id=released.release_id,
    )

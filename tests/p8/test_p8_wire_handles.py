# tests/p8/test_p8_wire_handles.py
"""CR-03: two un-keyed digests went on the wire, and both were reversed.

`sha256(field_key \x1f value)` reached the model as `subject_ref` **with
`field_key` printed in the clear beside it**, and the seed value came back in
3,301 hashes from the wire bytes alone. `sha256(content_hash ‖ extractor ‖
locator ‖ raw_value)` reached it twice -- as `released_evidence[].observation_key`
and as `evidence_items[].evidence_ref` -- **with the locator printed in the clear
as `address`**, and a value the dossier had printed as `"[redacted]"` came back in
about a second from the wire plus a copy of the file. A redaction a second of
compute undoes is not a redaction.

The identity itself is not the defect and does not move. `observation_key` is
M14's version-independent citation handle: the same observation keys the same way
across runs and across extractor versions, and every cache, replay and audit trail
leans on that. What changes is only **what may be spoken aloud**. A local-only key
turns a dictionary attack from a second of compute into an impossibility, because
the attacker cannot compute a single candidate digest at all.

The four identifier slots in the model-visible bytes, and why each is what it is:

* `subject_ref` -- keyed **whole**. `records.py` validates nothing about it, so a
  producer may put anything there; keying the whole string closes the field rather
  than the one producer that was caught leaking through it.
* `conflicts[].conflict_id` -- keyed. It is `f"{group_id}:{kind}"` and carries the
  same group digest `subject_ref` did.
* `released_evidence[].observation_key` -- keyed, always.
* `evidence_items[].evidence_ref` -- keyed when it is a P4 `observation_key`. A
  `file_id` is `uuid.uuid4()`: derived from nothing, inverting to nothing, and the
  thing the model's `members` list is read against.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

import pytest

from evidence_shape.location import TextSpan
from evidence_shape.observation import observation_key
from llm_harness.dossier import (
    build_dossier, canonical_dossier_bytes, dossier_address,
)
from llm_harness.records import (
    Conflict,
    DossierRequest,
    EvidenceItem,
    PromptDefinition,
    ValidationUnavailable,
)
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    A_FACT, ACCEPT_DIRECT, CITATION_NOT_IN_DOSSIER, DIRECT_ANCHOR, REDUCTION_NONE,
    REJECT, REMAINS_AMBIGUOUS,
)
from llm_harness.wire_handles import (
    WireHandleKeyRequired, issued_handles, local_ref, wire_handle,
)
from privacy.items import Excerpt
from privacy.redaction import RedactionManifest
from privacy.release import (
    ModelCallRequest, ModelTarget, Released, ReleasedItem, Target,
)

CLOUD = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")
VOCABULARY = ("school", "subject")

#: The corpus the reviewer ran against: one PDF, one heading, one course code.
CONTENT_HASH = "e46ad27e45dcd74cb7555e526910809c08667d9a64c5d016b22884c572f4093f"
EXTRACTOR = "pdf.text"
LOCATOR = "heading:page=1/heading=1#0-10"
SECRET_VALUE = "BUSIB 4300"
FIELD_KEY = "subject"

#: A key is a credential. Two of them, so a test can prove one is not the other.
KEY_A = bytes.fromhex("00" * 16 + "a1" * 16)
KEY_B = bytes.fromhex("00" * 16 + "b2" * 16)

OBS = observation_key(
    content_hash=CONTENT_HASH, extractor_name=EXTRACTOR, locator=LOCATOR,
    raw_value=SECRET_VALUE)

#: `grouping.pipeline._group_id`, restated here from what it emits, so this test
#: does not have to import P9 to say what P9 put on the wire.
GROUP_DIGEST = hashlib.sha256(
    "\x1f".join((FIELD_KEY, SECRET_VALUE)).encode("utf-8")).hexdigest()
GROUP_ID = f"group:{FIELD_KEY}:{GROUP_DIGEST}:strongly-identified-file"

FILE_ID = "025cfea0-1055-42fb-be12-b142d9e3f93b"

_SIXTY_FOUR_HEX = re.compile(r"[0-9a-f]{64}")


def _prompt() -> PromptDefinition:
    return PromptDefinition(
        template_id="template.fact",
        template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}',
        call_site=A_FACT,
        call_site_version="1",
        shaping_policy_bytes=b'{"policy":"authored"}',
    )


def _request(*, subject_ref: str = GROUP_ID, obs: str = OBS) -> DossierRequest:
    return DossierRequest(
        call_site=A_FACT,
        subject_ref=subject_ref,
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=(
            EvidenceItem(evidence_ref=obs, kind="excerpt", location="heading",
                         excerpt_span=(0, 10), reliability_state="direct",
                         basis=DIRECT_ANCHOR),
            EvidenceItem(evidence_ref=FILE_ID, kind="member", location="unclassified",
                         excerpt_span=None, reliability_state="direct",
                         basis=DIRECT_ANCHOR),
        ),
        conflicts=(Conflict(conflict_id=f"{GROUP_ID}:target_institution",
                            kind="target_institution"),),
        model_call_request=ModelCallRequest(
            stage="fact_extraction",
            target=Target(file_ids=(FILE_ID,)),
            model_target=CLOUD,
            requested_items=(Excerpt(observation_key=obs, span=TextSpan(0, 10),
                                     reason="names the course"),),
            prompt_template_id="template.fact",
            prompt_fingerprint="fingerprint.fact",
            max_dossier_tokens=4000),
        plan_version=None,
        evidence_snapshot_id=None,
    )


def _released(*, obs: str = OBS) -> Released:
    return Released(
        release_id="rel-1", audit_id=17, policy_version="policy-1",
        materialised_items=(ReleasedItem(
            observation_key=obs, span=LOCATOR, value="[redacted]", zone="heading",
            unit_length=64),),
        redaction_manifest=RedactionManifest(entries=()),
        model_target=CLOUD,
    )


def _build(*, handle_key: bytes = KEY_A, subject_ref: str = GROUP_ID,
           obs: str = OBS):
    return build_dossier(
        _request(subject_ref=subject_ref, obs=obs), _released(obs=obs),
        reduction_rung=REDUCTION_NONE, allowed_vocabulary=VOCABULARY,
        prompt=_prompt(), handle_key=handle_key)


def _wire(*, handle_key: bytes = KEY_A, **kwargs) -> dict:
    dossier = _build(handle_key=handle_key, **kwargs)
    assert not isinstance(dossier, ValidationUnavailable), dossier
    return json.loads(
        canonical_dossier_bytes(dossier, _prompt(), handle_key=handle_key)
        .decode("utf-8"))


# --------------------------------------------------------------------------
# 1. What is on the wire


def test_every_long_digest_on_the_wire_is_a_handle_and_nothing_else():
    """Exact set equality, so this fails on a leak AND on a handle gone missing.

    A `!=` against the two known digests would pass the day a third one arrives.
    """
    body = _wire()
    text = json.dumps(body, sort_keys=True)
    on_the_wire = set(_SIXTY_FOUR_HEX.findall(text))
    expected = {
        wire_handle(value, key=KEY_A).partition(":")[2]
        for value in (GROUP_ID, f"{GROUP_ID}:target_institution", OBS)
    }
    assert on_the_wire == expected
    assert GROUP_DIGEST not in text
    assert OBS not in text
    assert CONTENT_HASH not in text


def test_the_file_id_is_not_keyed_because_it_inverts_to_nothing():
    """`uuid.uuid4()`. Keying it would only make the model's members unreadable."""
    body = _wire()
    refs = {item["evidence_ref"] for item in body["evidence_items"]}
    assert FILE_ID in refs


# --------------------------------------------------------------------------
# 2. The reviewer's own recovery, re-run


def _dictionary() -> list[str]:
    words = [f"{school} {number}"
             for school in ("BUSIB", "PHYS", "CHEM")
             for number in range(1000, 5000, 100)]
    return words + [SECRET_VALUE]


def _recover_subject(subject_ref: str) -> str | None:
    """CR-03(b): wire bytes alone. `field_key` was printed beside the digest."""
    parts = subject_ref.split(":")
    if len(parts) != 4 or parts[0] != "group":
        return None
    for guess in _dictionary():
        probe = hashlib.sha256(
            "\x1f".join((parts[1], guess)).encode("utf-8")).hexdigest()
        if probe == parts[2]:
            return guess
    return None


def _recover_value(key: str, address: str) -> str | None:
    """CR-03(a): wire bytes plus a copy of the file, which gives `content_hash`."""
    for guess in _dictionary():
        if observation_key(content_hash=CONTENT_HASH, extractor_name=EXTRACTOR,
                           locator=address, raw_value=guess) == key:
            return guess
    return None


def test_the_probe_recovers_both_values_from_the_shapes_that_used_to_ship():
    """The twin of the two below: an attack that finds nothing proves nothing
    unless the same attack, against the digests as they were, finds everything."""
    assert _recover_subject(GROUP_ID) == SECRET_VALUE
    assert _recover_value(OBS, LOCATOR) == SECRET_VALUE


def test_the_seed_value_is_no_longer_recoverable_from_the_wire_bytes():
    assert _recover_subject(_wire()["subject_ref"]) is None


def test_the_redacted_value_is_no_longer_recoverable_from_wire_plus_file():
    item = _wire()["released_evidence"][0]
    assert item["value"] == "[redacted]"
    assert item["address"] == LOCATOR
    assert _recover_value(item["observation_key"], item["address"]) is None


# --------------------------------------------------------------------------
# 3. Absent means refuse, never guess


@pytest.mark.parametrize("absent", [None, b"", bytearray(), "not-bytes"])
def test_an_absent_key_refuses_rather_than_falling_back_to_an_unkeyed_digest(absent):
    result = _build(handle_key=absent)
    assert isinstance(result, ValidationUnavailable)
    assert "wire_handle_key" in result.missing


def test_the_bytes_cannot_be_produced_without_a_key():
    dossier = _build()
    for absent in (None, b""):
        with pytest.raises(WireHandleKeyRequired):
            canonical_dossier_bytes(dossier, _prompt(), handle_key=absent)
        with pytest.raises(WireHandleKeyRequired):
            dossier_address(dossier, _prompt(), handle_key=absent)


# --------------------------------------------------------------------------
# 4. A key is a credential


def test_the_key_reaches_no_byte_the_model_or_a_reader_ever_sees():
    dossier = _build()
    hexed = KEY_A.hex()
    bytes_out = canonical_dossier_bytes(dossier, _prompt(), handle_key=KEY_A)
    assert KEY_A not in bytes_out
    assert hexed.encode("ascii") not in bytes_out
    assert hexed not in repr(dossier)
    try:
        wire_handle("anything", key=b"")
    except WireHandleKeyRequired as exc:
        assert hexed not in str(exc)
        assert "b''" not in str(exc)
    else:  # pragma: no cover - the call above must raise
        pytest.fail("an absent key must refuse")


# --------------------------------------------------------------------------
# 5. The local side still works: cross-run identity, replay, and the record


def test_one_observation_keys_the_same_way_on_every_run():
    """Cross-run identity is what `record_dossier`'s content address leans on."""
    first, second = _build(), _build()
    assert first.dossier_id == second.dossier_id
    assert (canonical_dossier_bytes(first, _prompt(), handle_key=KEY_A)
            == canonical_dossier_bytes(second, _prompt(), handle_key=KEY_A))


def test_two_different_subjects_never_share_one_address():
    """Ordinal handles would collide here, and `record_dossier` refuses a second
    payload under an address it already holds."""
    other = GROUP_ID.replace("448eba", "999999")
    assert _build().dossier_id != _build(subject_ref=other).dossier_id


def test_two_installs_do_not_hand_a_provider_the_same_handle():
    assert _wire(handle_key=KEY_A)["subject_ref"] != _wire(
        handle_key=KEY_B)["subject_ref"]


def test_the_local_record_still_carries_P4s_own_key():
    """M14's handle is unchanged in the record, so `resolve`, the audit and the
    `llm_dossier` payload all still address the observation they always did."""
    dossier = _build()
    assert dossier.released_evidence[0].observation_key == OBS
    assert dossier.subject_ref == GROUP_ID
    assert {item.evidence_ref for item in dossier.evidence_items} == {OBS, FILE_ID}
    assert dossier.conflicts[0].conflict_id == f"{GROUP_ID}:target_institution"


# --------------------------------------------------------------------------
# 6. The model cites what it saw, and it lands on the local key


def test_a_citation_of_the_handle_resolves_to_the_local_observation_key():
    handles = issued_handles((OBS, FILE_ID), key=KEY_A)
    shown = _wire()["evidence_items"]
    cited = next(item["evidence_ref"] for item in shown
                 if item["evidence_ref"] != FILE_ID)
    assert local_ref(cited, handles=handles) == OBS
    assert local_ref(FILE_ID, handles=handles) == FILE_ID


def test_a_reference_the_dossier_never_issued_stays_unresolved():
    handles = issued_handles((OBS,), key=KEY_A)
    assert local_ref("handle:" + "0" * 64, handles=handles) == "handle:" + "0" * 64


# --------------------------------------------------------------------------
# 7. The whole round trip, through the real validator
#
# Every other test here stops at a boundary. This one is the only twin the
# INVERSE has: the fixtures the rest of the suite validates against cite
# `"obs-1"`, which is not a P4 key, so `wire_ref` hands it straight through and
# a missing inverse looks exactly like a present one. A model that cites the
# handle it was actually shown does not.


def _response(cited: str) -> bytes:
    return json.dumps({"claims": [{
        "claim_ref": "claim-0",
        "payload": {"field": "subject", "value": SECRET_VALUE},
        "citations": [{
            "evidence_ref": cited,
            "cited_span": "redacted",
            "why_it_supports": "the heading states it",
        }],
    }]}).encode("utf-8")


def _validated(cited: str, *, resolves=True):
    """One response through `validate_response`, with the resolver watched.

    The resolver is the store, and the store knows only P4 keys. What it is
    ASKED is the whole question here, so the asking is recorded.
    """
    asked: list[str] = []

    def resolver(ref: str):
        asked.append(ref)
        return object() if resolves and ref == OBS else None

    result = validate_response(
        _build(), _response(cited),
        evidence_resolver=resolver,
        site_validator=lambda _dossier, _raw, _verdict: None,
        contradicts=lambda *_a, **_k: False,
        model_id="fixture-model",
        prompt_fingerprint="fp",
        dossier_builder="p8",
        release_audit_id=17,
        handle_key=KEY_A,
    )
    assert not isinstance(result, ValidationUnavailable), result
    verdicts, _report = result
    return verdicts[0], asked


def test_a_model_citing_the_handle_it_saw_is_grounded_in_the_local_observation():
    shown = _wire()["released_evidence"][0]["observation_key"]
    verdict, asked = _validated(shown)
    # The store was asked about P4's key and never about the handle.
    assert asked == [OBS]
    assert verdict.outcome == ACCEPT_DIRECT
    assert verdict.reasons == ()
    # And the recorded citation names the local key, so the audit row, P6's
    # `evidence_refs` and a later `resolve` all address the observation.
    assert [item.citation_ref for item in verdict.citations_checked] == [OBS]
    assert verdict.citations_checked[0].resolved is True
    assert verdict.citations_checked[0].span_matched is True


def test_a_handle_this_dossier_never_issued_is_absent_from_it():
    verdict, asked = _validated("handle:" + "0" * 64)
    assert asked == []
    assert verdict.outcome == REJECT
    assert verdict.reasons == (CITATION_NOT_IN_DOSSIER,)


def test_no_part_package_reaches_for_the_fixture_key():
    """A printable key wired into the product would void the whole fix.

    `FIXTURE_HANDLE_KEY` exists so a test does not have to mint its own and get
    it subtly wrong. It is also, by construction, a key an attacker has: a
    composition root that reached for it out of convenience would hand every
    handle back to a dictionary attack, and the bytes would look identical.
    """
    source = pathlib.Path(__file__).resolve().parents[2] / "src"
    named = sorted(
        path.relative_to(source).as_posix()
        for path in source.rglob("*.py")
        if "FIXTURE_HANDLE_KEY" in path.read_text(encoding="utf-8"))
    assert named == ["llm_harness/fixtures.py"]

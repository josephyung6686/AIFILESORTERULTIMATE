# tests/p7/test_p7_no_silent_drop.py
"""A requested item is RELEASED or REFUSED. There is no third outcome.

The defect this file exists for, found by review on 2026-09-02 and reproduced:
two items requested, `Excerpt` and `SelfDescription`, with the suspension on. The
gate returned `Released` carrying ONE materialised item, and the self-description
was neither in it nor in the denial nor in `AuditRecord.excerpts_included`. It
evaporated. A caller reading `Released` had no way to learn that the thing it asked
about had not been decided, and a person reading the audit afterwards had no way to
learn it had been asked for.

**Why that is worse than either answer the design allows.** `84` §1: absent means
refuse, never guess. A `Denied` is a fact a person can act on and a `Released` is a
fact a person can audit; an item that is in neither is a hole in the one record
§8.4 says must describe the call. It is also the exact shape P7 was built to make
impossible -- the gate is the single door precisely so that "what was sent" and
"what was asked for" cannot come apart -- and it came apart quietly, which is the
only way this class of defect ever arrives.

**The fix is an allowlist and not a classification**, deliberately. `gate.TEXT_BEARING`
is the two kinds that resolve to a value; `gate.REFERENCE_ONLY` is the four §4 says
carry no content ("an evidence reference is an id only -- no content"), which are
correctly absent from `materialised_items` and always were. Anything in NEITHER is
refused by name. That is `84` §1's rule applied to the item table itself: a kind
this gate has no reading for is a kind it refuses, not a kind it drops.

Nothing here classifies `self_description`. It is the only kind currently in
neither tuple, so it is what the tests below reach for -- and the refusal lifts on
its own, with no edit to `gate.py`, **once a materialiser for the kind exists**.
That ownership stays with the type.

**Not "once it joins `TEXT_BEARING`", and the difference is the whole point.**
`resolve.materialise` reads `item.observation_key` and then `item.span`, and its
docstring says "nothing else is read". A `SelfDescription` carries a `question_id`
and neither of those. Admitting it to `TEXT_BEARING` today does not lift this
refusal -- it reaches `Gate._materialise` and raises `AttributeError`, which is an
unhandled crash standing where a named refusal was, and worse than the silent drop
both of them replace. The materialiser has to exist first; how it dispatches is the
type's owner's call and not named here.

**TWO TESTS HERE DO HAVE TO CHANGE ON THAT DAY, and they are named so the person
wiring the door does not spend an hour thinking they broke the gate.**

* `test_every_kind_is_materialised_or_reference_only_or_refused` pins the leftover
  set to `{"self_description"}` ON PURPOSE. It is a tripwire, not an invariant: a
  kind arriving in neither tuple should stop somebody and make them say which of
  the two readings it gets. Wiring the door moves the leftover to `set()`, and the
  assertion is meant to be updated to that, not deleted.
* `test_a_kind_in_neither_tuple_is_refused_whatever_it_is` constructs a
  `SelfDescription` with no backing row, which is all a refusal needs. Once the kind
  is text-bearing it reaches `_consent_reference` and `_materialise`, which want a
  row -- so that item needs a seeded declaration there, or lifting out of the loop.
  It will fail for a reason that has nothing to do with the property.
"""
from __future__ import annotations

import dataclasses

import pytest

from privacy.authorship import COMPONENT_VERSION
from privacy.gate import REFERENCE_ONLY, TEXT_BEARING
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, Filename, MetadataField,
    RequestedItem, SelfDescription, _KIND_BY_TYPE, kind_of,
)
from privacy.policy import Policy, UNSET_POLICY_VERSION, set_policy
from privacy.release import Denied, MalformedRequest, Released
from privacy.vocabulary import ITEM_KINDS

from p7.test_p7_release import (
    OBSERVED_AT, PLAN_VERSION, SPAN, _classify, _evidence, _file, _gate, _request,
    gate_conn,  # noqa: F401 -- the fixture, used by name in every signature below
)

A_ROLE = "role:me"


def _policy_suspending(conn, kinds: tuple[str, ...]) -> Policy:
    """A stored policy, with `80` §8's suspension named on it or not named at all.

    Written here rather than reused from `test_p7_release._policy` because the
    suspension is the one field these tests vary, and `MORE_REDACTING` is not.
    """
    draft = Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={}, automatic_move_permissions={},
        plan_version=PLAN_VERSION, set_at=OBSERVED_AT,
        suspended_item_kinds=kinds)
    version = set_policy(conn, draft, component_version=COMPONENT_VERSION,
                         user_id="joseph", reason="test fixture")
    return dataclasses.replace(draft, policy_version=version)


def _seeded(conn) -> tuple[str, str]:
    """One clean, releasable file and the observation key of its one excerpt."""
    file_id = _file(conn, "notes.pdf", "hash-notes")
    key = _evidence(conn, file_id, "hash-notes")
    _classify(conn, file_id, "hash-notes", handling_class="public_low",
              protected=False, refs=(key,))
    return file_id, key


# --- the reproduction, and the one line of it that matters ---------------------------


def test_an_item_the_gate_cannot_materialise_is_refused_and_not_dropped(gate_conn):
    """The reviewer's reproduction, turned around.

    Before: `Released`, `len(materialised_items) == 1` of 2 requested, and the
    second item named nowhere in the record. After: a refusal that says which kind
    and why, before any audit row is written -- because a record that does not
    describe the call is worse than no call.
    """
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ("self_description",))

    with pytest.raises(MalformedRequest) as caught:
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
                   SelfDescription(question_id=A_ROLE)),
            file_ids=(file_id,)))

    assert "self_description" in str(caught.value)


def test_the_run_that_would_have_dropped_it_writes_no_audit_row(gate_conn):
    """The refusal lands BEFORE §8.4's record is appended.

    Otherwise the fix would trade a silent drop for a stored record that says one
    item was released when two were asked about -- the same lie, durable.
    """
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ("self_description",))
    before = gate_conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    with pytest.raises(MalformedRequest):
        _gate(gate_conn).release(_request(
            items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
                   SelfDescription(question_id=A_ROLE)),
            file_ids=(file_id,)))

    assert gate_conn.execute(
        "SELECT COUNT(*) FROM events").fetchone()[0] == before


def test_the_refusal_names_the_kind_and_not_the_type(gate_conn):
    """A message a person can act on names the vocabulary member, because that is
    what `ITEM_KINDS`, the policy's `suspended_item_kinds` and the audit all spell.
    A Python class name would send a reader looking in the wrong file."""
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ("self_description",))

    with pytest.raises(MalformedRequest) as caught:
        _gate(gate_conn).release(_request(
            items=(SelfDescription(question_id=A_ROLE),), file_ids=(file_id,)))

    message = str(caught.value)
    assert "self_description" in message and "materialise" in message


# --- and the direction that keeps it a rule rather than a ban ------------------------


def test_a_denial_still_beats_the_refusal(gate_conn):
    """Order, and the one existing behaviour this must not disturb.

    With the suspension OFF, a self-description is `Denied always_local_item` --
    the correct answer, and the one the owner's whole ruling turns on. The new
    check therefore sits AFTER the denials are collected: a request that is both
    forbidden and unmaterialisable is forbidden, because that is the answer a
    person needs and the stronger of the two.
    """
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ())

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               SelfDescription(question_id=A_ROLE)),
        file_ids=(file_id,)))

    assert isinstance(decision, Denied)
    assert decision.reason == "always_local_item"


def test_the_four_reference_only_kinds_release_exactly_as_before(gate_conn):
    """§4: an evidence reference is "an id only -- no content". These four are
    absent from `materialised_items` BY DESIGN and always were, and a check that
    could not tell them from a dropped item would refuse the ordinary path."""
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ())

    decision = _gate(gate_conn).release(_request(
        items=(Excerpt(observation_key=key, span=SPAN, reason="heading"),
               CandidateLabel(label="Passport"), MetadataField(name="page_count"),
               EvidenceReference(observation_key=key), Filename(file_id=file_id)),
        file_ids=(file_id,)))

    assert isinstance(decision, Released)
    assert len(decision.materialised_items) == 1


# --- the property, over the item table rather than over one kind ---------------------


def test_every_kind_is_materialised_or_reference_only_or_refused():
    """`84` §1 applied to the item table itself.

    The two tuples do not have to COVER `ITEM_KINDS` -- `self_description` is in
    neither today and that is the honest state of the door. What must hold is that
    the gate has a reading for every kind: a value, an id, or a refusal. This
    asserts the third by asserting the first two are disjoint and that whatever is
    left over is exactly what the release path refuses.
    """
    materialised = {_KIND_BY_TYPE[cls] for cls in TEXT_BEARING}
    reference_only = {_KIND_BY_TYPE[cls] for cls in REFERENCE_ONLY}

    assert materialised.isdisjoint(reference_only), (
        "a kind that is both resolved and reference-only would be released twice "
        "under two readings")
    assert (materialised | reference_only) <= set(ITEM_KINDS)
    assert set(ITEM_KINDS) - materialised - reference_only == {"self_description"}, (
        "a kind has appeared that the gate neither materialises nor treats as a "
        "reference. That is not a failure -- it is the refusal path being exercised "
        "by a new member -- but it must be a DELIBERATE state, so update this "
        "assertion and say at the type which of the two readings it will get")


def test_the_union_of_the_two_tuples_is_read_from_the_type_table(gate_conn):
    """Neither tuple may hold a type `items.py` does not publish as a kind.

    Spelled once. A type listed here that `_KIND_BY_TYPE` does not know would make
    the gate's reading of an item disagree with the vocabulary's, and the gate's
    reading is the one that decides what leaves the device."""
    for cls in (*TEXT_BEARING, *REFERENCE_ONLY):
        assert cls in _KIND_BY_TYPE
        assert cls in RequestedItem.__args__


def test_a_kind_in_neither_tuple_is_refused_whatever_it_is(gate_conn):
    """The property without `SelfDescription` in it, so this file outlives the door.

    Every published kind is put through the gate one at a time. Each one either
    reaches a decision -- `Released`, `Denied`, `NeedsConsent` -- or raises
    `MalformedRequest`. What must never happen is the third thing: a `Released`
    that does not account for the item that was asked about.
    """
    file_id, key = _seeded(gate_conn)
    _policy_suspending(gate_conn, ("self_description",))
    gate = _gate(gate_conn)

    readable = (*TEXT_BEARING, *REFERENCE_ONLY)
    for item in (Excerpt(observation_key=key, span=SPAN, reason="heading"),
                 CandidateLabel(label="Passport"), MetadataField(name="page_count"),
                 EvidenceReference(observation_key=key), Filename(file_id=file_id),
                 SelfDescription(question_id=A_ROLE)):
        kind = kind_of(item)
        try:
            decision = gate.release(_request(items=(item,), file_ids=(file_id,)))
        except MalformedRequest:
            assert type(item) not in readable, (
                f"{kind!r} has a reading and was refused as though it had none")
            continue
        # The load-bearing line. Reaching a DECISION at all is the claim: a kind the
        # gate has no reading for must not get this far, because everything past
        # here filters on `TEXT_BEARING` and the item stops being counted.
        assert type(item) in readable, (
            f"{kind!r} was requested and the call returned {type(decision).__name__}"
            f" without the gate having any reading for it -- which is the silent "
            f"drop, whatever the decision says")
        if isinstance(decision, Released):
            assert bool(decision.materialised_items) == (type(item) in TEXT_BEARING)

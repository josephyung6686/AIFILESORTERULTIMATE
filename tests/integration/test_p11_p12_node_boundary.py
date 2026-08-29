"""P11 supplies a node; P12 resolves a path. The boundary is a field list."""
from __future__ import annotations

import dataclasses

from placement.fixtures import GOLDEN_DECISIONS, golden_decisions
from placement.records import Destination, PlacementDecision, Subject
from placement.vocabulary import PLACE, PLAN_BEARING_OUTCOMES

#: Every field name P11 publishes on a decision or on anything nested inside one.
_RECORDS = (PlacementDecision, Destination, Subject)

_FORBIDDEN = {
    "path", "resolved_path", "resolved_destination_path", "existing_path",
    "filesystem_path", "directory", "delete", "deleted", "disposable",
    "expiry", "expires_at", "ttl",
}


def test_p12_consumes_exactly_one_outcome():
    # M13. Keyed on `outcome`, not on `confidence_class`, whose value
    # "abstain: no supported destination" is a LABEL on a record and not the
    # record's disposition.
    assert PLAN_BEARING_OUTCOMES == (PLACE,)


def test_nothing_p11_publishes_can_carry_a_resolved_path():
    names = set()
    for record in _RECORDS:
        names |= {f.name for f in dataclasses.fields(record)}
    assert not names & _FORBIDDEN
    assert "node_id" in {f.name for f in dataclasses.fields(Destination)}


def test_the_field_check_would_notice_a_path_if_one_appeared():
    # The negative twin. A predicate that intersected against the wrong field set
    # would pass over a record that had grown a path, and this proves it does not.
    @dataclasses.dataclass(frozen=True)
    class _WithPath:
        node_id: str
        resolved_path: str

    names = {f.name for f in dataclasses.fields(_WithPath)}
    assert names & _FORBIDDEN == {"resolved_path"}


def test_the_golden_records_are_what_p12_and_p13_build_against():
    assert golden_decisions() is GOLDEN_DECISIONS
    assert len(GOLDEN_DECISIONS) == 5
    # Every one is a real `PlacementDecision`, so a shape change breaks the
    # fixtures at import rather than leaving a consumer building against a record
    # the product no longer has.
    assert all(isinstance(d, PlacementDecision) for d in GOLDEN_DECISIONS)
    # Exactly one of them is plan-bearing per outcome family, and only `place`
    # carries a destination -- which is the whole of P12's contract.
    for decision in GOLDEN_DECISIONS:
        assert (decision.destination is not None) == (decision.outcome == PLACE)

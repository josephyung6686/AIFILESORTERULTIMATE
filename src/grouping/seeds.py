# src/grouping/seeds.py
"""Where a group's claim to exist starts. Four kinds, and a narrow evidence bar.

`facts.read_surface.proposal_eligible` is a CANDIDATE read surface, not the anchor
authority. It admits `llm_supported` and `user_confirmed`, and neither may anchor
a group automatically:

- `llm_supported` is a model conclusion. Letting one seed a group lets the model
  confirm its own earlier guess, which is the loop §4.9's stop rules exist to
  break.
- `user_confirmed` is the strongest state P6 has, and it still does not anchor.
  User intent enters through `user_seed_for`, where it carries a decision the user
  actually made about *this group*, rather than by widening the evidence bar so
  that any confirmed fact anywhere starts one.

So P9 applies its own `reliability in {direct, validated}` filter AFTER the public
read. That filter is the anchor bar, and it is deliberately narrower than P6's.

P9 spells no domain field name. The three structural fields it does name
(`EVENT_FIELD`, the two family fields) are P6's own published constants, imported
rather than restated.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from facts.read_surface import (
    DUPLICATE_FAMILY_FIELD,
    EVENT_FIELD,
    VERSION_FAMILY_FIELD,
    event_facts,
    family_facts,
    proposal_eligible,
)

from grouping.records import MalformedGroupRecord, _require
from grouping.vocabulary import (
    STRONGLY_IDENTIFIED_FILE,
    STRUCTURAL_FAMILY,
    USER_CREATED_STARTING_POINT,
    VALIDATED_SHARED_FACT,
)

#: P9's anchor bar. Narrower than `PROPOSAL_ELIGIBLE_STATES` on purpose.
ANCHOR_STATES: frozenset[str] = frozenset({"direct", "validated"})

#: The structural fields whose values name a family rather than a subject.
_FAMILY_FIELDS: frozenset[str] = frozenset(
    {DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD},
)


@dataclass(frozen=True)
class UserSeed:
    """An explicit start the user chose. The only channel user intent enters by."""

    file_id: str
    content_hash: str
    basis: str
    decided_at: str

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "basis", "decided_at"):
            _require(getattr(self, name), name=name)


@dataclass(frozen=True)
class Seed:
    """One legal starting point, with the evidence that makes it legal."""

    seed_kind: str
    file_id: str
    content_hash: str
    field_key: str | None
    value: str | None
    reliability_state: str | None
    observation_key: str | None
    basis: str | None

    def __post_init__(self) -> None:
        _require(self.file_id, name="file_id")
        _require(self.content_hash, name="content_hash")
        if self.seed_kind == USER_CREATED_STARTING_POINT:
            if not self.basis:
                raise MalformedGroupRecord(
                    "a user seed carries the decision the user made; without it "
                    "nothing can say why this file starts a group"
                )
            return
        if self.reliability_state not in ANCHOR_STATES:
            raise MalformedGroupRecord(
                f"reliability_state={self.reliability_state!r} is below P9's anchor "
                f"bar {sorted(ANCHOR_STATES)}; a proposal-eligible fact is a "
                "candidate, not an anchor"
            )
        if not self.observation_key:
            raise MalformedGroupRecord(
                "a seed cites the observation that states it; one that cites "
                "nothing cannot be checked or replayed"
            )


def _first_evidence_ref(row: sqlite3.Row) -> str | None:
    import json

    raw = row["evidence_refs"]
    if isinstance(raw, str) and raw:
        try:
            refs = json.loads(raw)
        except ValueError:
            return None
        if isinstance(refs, list) and refs and isinstance(refs[0], str):
            return refs[0]
    return None


def _seed_kind_for(field_key: str) -> str:
    """Which of the four kinds a fact-backed seed is.

    A family value names a structural relationship rather than a subject, and a
    photo event is a deterministic computation over capture metadata — the design
    lists both separately from a strongly-identified file.
    """
    if field_key in _FAMILY_FIELDS:
        return STRUCTURAL_FAMILY
    if field_key == EVENT_FIELD:
        return VALIDATED_SHARED_FACT
    return STRONGLY_IDENTIFIED_FILE


def _anchor_rows(conn: sqlite3.Connection, *, file_id: str,
                 content_hash: str) -> list[sqlite3.Row]:
    """Every fact at or above P9's anchor bar, from P6's public reads only.

    `event_facts` and `family_facts` are read alongside `proposal_eligible`
    because a structural or event fact may sit at `validated` without being a
    proposal candidate; every row is then put through the same bar.
    """
    seen: dict[str, sqlite3.Row] = {}
    for read in (proposal_eligible, event_facts, family_facts):
        for row in read(conn, file_id=file_id, content_hash=content_hash):
            if row["reliability_state"] not in ANCHOR_STATES:
                continue
            seen.setdefault(f"{row['field_key']}:{row['value_id']}", row)
    return [seen[key] for key in sorted(seen)]


def seeds_for_file(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    user_seed_for: Callable[[str, str], UserSeed | None],
) -> tuple[Seed, ...]:
    """The legal seeds for one file version, deterministically ordered.

    An explicit user seed answers on its own: the user said where a group starts,
    and P9 does not add fact-backed seeds beside that decision.
    """
    chosen = user_seed_for(file_id, content_hash)
    if chosen is not None:
        if not isinstance(chosen, UserSeed):
            raise MalformedGroupRecord(
                "user_seed_for returns a UserSeed or None; P9 does not interpret "
                "another shape as a user decision"
            )
        return (
            Seed(
                seed_kind=USER_CREATED_STARTING_POINT,
                file_id=chosen.file_id,
                content_hash=chosen.content_hash,
                field_key=None,
                value=None,
                reliability_state=None,
                observation_key=None,
                basis=chosen.basis,
            ),
        )

    return tuple(
        Seed(
            seed_kind=_seed_kind_for(row["field_key"]),
            file_id=file_id,
            content_hash=content_hash,
            field_key=row["field_key"],
            value=row["canonical_value"],
            reliability_state=row["reliability_state"],
            observation_key=_first_evidence_ref(row),
            basis=None,
        )
        for row in _anchor_rows(conn, file_id=file_id, content_hash=content_hash)
    )

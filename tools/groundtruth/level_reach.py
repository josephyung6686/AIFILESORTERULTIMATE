# tools/groundtruth/level_reach.py
"""`106` Phase 6's gate: files that carry a level of their OWN situation.

Not `score_fields` (that grades against the owner's labels) and not a fact count.
The question is the one `materialise.py`'s `divides` asks one stage later: is there
a value under this file the template can nest it by. Read directly off the database
so it runs on `run12.sqlite` and `run22.sqlite` alike, aggregates only.

What is NOT counted, and the tests pin each: `file_type` (a level of no situation),
a `possible` proposal (below `PROPOSAL_ELIGIBLE_STATES`), a level of some OTHER
situation, and a file with no situation -- which stays in the denominator, because a
file the judge never placed is a file this phase did not help.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from facts.llm_seam import SITUATION_FIELD
from facts.states import PROPOSAL_ELIGIBLE_STATES
from production import folder_levels_for
from tree_design.config import ConfigurationRequired


@dataclass(frozen=True)
class LevelReach:
    files: int
    with_situation: int
    #: Files whose `situation` fact names nothing `folder_levels_for` resolves --
    #: a bare schema id written before `106` Phase 2(b), or several live values.
    unresolvable: int
    reached: int
    by_field: dict[str, int] = field(default_factory=dict)


def level_reach(conn: sqlite3.Connection, catalogue) -> LevelReach:
    eligible = {row[0] for row in conn.execute(
        "select field_key from fields where destination_eligible = 1")}
    situations: dict[str, set[str]] = {}
    facts: dict[str, set[tuple[str, str]]] = {}
    for row in conn.execute(
            'select ff.file_id, ff.field_key, ff.reliability_state, v.canonical_value '
            'from file_facts ff join "values" v using (value_id) '
            'where ff.active = 1 and ff.superseded_by is null'):
        file_id, key, state, value = row
        if key == SITUATION_FIELD:
            situations.setdefault(file_id, set()).add(value)
        elif key in eligible and state in PROPOSAL_ELIGIBLE_STATES:
            facts.setdefault(file_id, set()).add((key, state))
    files = {row[0] for row in conn.execute("select file_id from files")}
    unresolvable = reached = 0
    by_field: dict[str, int] = {}
    for file_id in files:
        named = situations.get(file_id, set())
        if len(named) != 1:
            unresolvable += bool(named)
            continue
        try:
            levels = {level.field for level in
                      folder_levels_for(catalogue, next(iter(named)))}
        except ConfigurationRequired:
            unresolvable += 1
            continue
        hit = sorted({key for key, _state in facts.get(file_id, ()) if key in levels})
        if not hit:
            continue
        reached += 1
        for key in hit:
            by_field[key] = by_field.get(key, 0) + 1
    return LevelReach(files=len(files), with_situation=len(situations),
                      unresolvable=unresolvable, reached=reached, by_field=by_field)

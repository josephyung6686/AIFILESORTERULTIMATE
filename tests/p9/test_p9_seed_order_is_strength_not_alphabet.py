# tests/p9/test_p9_seed_order_is_strength_not_alphabet.py
"""`104` §18.105: which fact a file groups on was decided by the ALPHABET.

`_anchor_rows` returned `[seen[key] for key in sorted(seen)]`, keyed
`f"{field_key}:{value_id}"`, and `group_subject` takes `seeds[0]`. So a file
holding both a `subject` fact and a `media_type` fact grouped on `media_type`,
because `m` sorts before `s` -- not because the format was better evidence than
the course.

**MEASURED (`104` §18.105).** Graded against the owner's own group labels, run
groups seeded `structural-family` are 27 pure / 1 mixed, while those seeded
`strongly-identified-file` -- the arm this ordering feeds -- are 6 pure / 3
mixed. Wrong a third of the time, on a choice nobody made.

**THE FIX USES THE PRODUCT'S OWN LADDER.** `facts.states.STRENGTH_ORDER` is
§3.13's five ranked states, weakest first, and `strength` is an index into it.
A stronger fact seeds the group; the field key stays in the key as the LAST
term, so the order is still total and a re-run still produces the same groups.

This is deliberately not a judgement about which FIELD is more interesting. The
defect was that the choice was arbitrary, and the product already publishes a
ranking of evidence; using it is the smallest principled change. Whether a
purpose-bearing field should outrank a format one is a separate question and is
`106` Phase 3's, where the owner's ruling on lives decides it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from facts.states import DIRECT, VALIDATED  # noqa: E402
from grouping.seeds import _order_anchor_rows  # noqa: E402


def _row(field_key, value_id, state):
    return {"field_key": field_key, "value_id": value_id,
            "reliability_state": state}


def test_the_stronger_fact_seeds_the_group_even_when_it_sorts_last():
    """The defect, stated so the alphabet cannot satisfy it.

    `subject` sorts AFTER `media_type`, and it is the `direct` one here. Under
    the old ordering the file grouped on its file format; under this one it
    groups on the stronger fact.

    SABOTAGE: return `sorted(rows, key=...field_key...)`. Red, and the product
    goes back to grouping a course's files by whether they are PDFs.
    """
    rows = [_row("media_type", "v1", VALIDATED),
            _row("subject", "v2", DIRECT)]

    assert [r["field_key"] for r in _order_anchor_rows(rows)] == [
        "subject", "media_type"]


def test_equal_strength_still_orders_by_field_key_so_a_rerun_is_stable():
    """A total order, or two runs of one corpus build two different graphs.

    SABOTAGE: drop the field key from the sort key. Python's sort is stable, so
    the order becomes the order the reads happened to return -- which is the
    database's, which is not promised.
    """
    rows = [_row("work_type", "v1", DIRECT),
            _row("subject", "v2", DIRECT)]

    assert [r["field_key"] for r in _order_anchor_rows(rows)] == [
        "subject", "work_type"]


def test_an_unknown_state_sorts_weakest_rather_than_raising():
    """A state this ladder does not name is weaker than every state it does.

    `_anchor_rows` has already refused anything below the anchor bar, so an
    unrecognised word here means a vocabulary this build has not read -- and the
    honest answer is to let the states it DOES understand seed first, never to
    crash a scan over an ordering question.

    SABOTAGE: `STRENGTH_ORDER.index(state)` unguarded. A run meeting one
    unfamiliar row dies, and `104` §17.2's rule that a gap in the vocabulary must
    not become a file that vanished is broken one stage earlier.
    """
    rows = [_row("aaa_first_alphabetically", "v1", "some_future_state"),
            _row("zzz_last_alphabetically", "v2", DIRECT)]

    assert [r["field_key"] for r in _order_anchor_rows(rows)] == [
        "zzz_last_alphabetically", "aaa_first_alphabetically"]

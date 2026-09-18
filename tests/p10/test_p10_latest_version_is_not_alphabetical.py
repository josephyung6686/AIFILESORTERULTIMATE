# tests/p10/test_p10_latest_version_is_not_alphabetical.py
"""`104` §18.113: `latest_version` breaks its tie on the ID, AS A STRING.

`store.latest_version` orders `created_at DESC, plan_version_id DESC`, and its own
docstring explains the tie-break: *"a run that opens a draft in the same second as
the version it was opened from would otherwise be ordered by a row order."* The
reasoning is right and the key is wrong. Plan version ids end in an ordinal --
`..._0`, `..._8`, `..._18` -- and **a run writes several in one second**: the
owner's own database holds a chain `_0` draft, `_8` draft, `_18` frozen, all
sharing one `created_at`. Compared as text, `_8` beats `_18`.

`104` R-38 is the caller: the next draft is opened FROM "whatever the person last
saw". With ten or more versions in a second, it is opened from the wrong tree.

**THE LEAD WROTE THIS EXACT BUG INDEPENDENTLY** while patching
`tools/groundtruth/measure.py`, called it careless, and reverted it -- before an
analyst found the same defect shipping here. It is not a typo; it is what "break
the tie on the id" means when ids carry numbers.

**THE FIX IS `rowid`, NOT A CLEVERER STRING.** SQLite's `rowid` is the insertion
order of the row, which is exactly the "row order" the docstring wanted to avoid
relying on by accident -- and is precisely right to rely on ON PURPOSE, because
what is wanted is "the one written last". `predecessor_id` would also answer, and
is a larger change for the same result.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tree_design.schema import create_tree_schema  # noqa: E402
from tree_design.store import latest_plan_version as latest_version  # noqa: E402

SAME_SECOND = "2026-09-18T19:00:00+00:00"


def _conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tree_schema(conn)
    return conn


def _version(conn, plan_version_id, *, created_at=SAME_SECOND, state="draft"):
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) VALUES (?,?,?,?,0,'s')",
        (plan_version_id, None, state, created_at))


def test_the_tenth_version_of_a_second_beats_the_eighth():
    """The defect, in the shape the owner's own database has.

    SABOTAGE: order by `plan_version_id DESC`. Red here, and `104` R-38 opens the
    next draft from a tree the person did not last see.
    """
    conn = _conn()
    _version(conn, "version_aaaa_0")
    _version(conn, "version_aaaa_8")
    _version(conn, "version_aaaa_18")

    assert latest_version(conn) == "version_aaaa_18"


def test_a_later_second_still_wins_outright():
    """`created_at` remains the first key; only the TIE-BREAK changes.

    SABOTAGE: order by `rowid` alone. A version written earlier in wall-clock time
    but inserted later -- a replay, a repair, an import -- would take the pointer
    from the one the person actually last saw.
    """
    conn = _conn()
    _version(conn, "version_bbbb_99", created_at="2026-09-18T20:00:00+00:00")
    _version(conn, "version_bbbb_1", created_at="2026-09-18T19:00:00+00:00")

    assert latest_version(conn) == "version_bbbb_99"


def test_an_empty_table_answers_none():
    """Unchanged, and pinned: a database with no plan is not a crash."""
    assert latest_version(_conn()) is None


def test_one_version_is_that_version():
    conn = _conn()
    _version(conn, "version_cccc_0")

    assert latest_version(conn) == "version_cccc_0"

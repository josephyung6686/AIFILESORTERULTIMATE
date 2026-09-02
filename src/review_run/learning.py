"""§8.7's inspect surface, and the projection it had no way to build.

    §8.7 requires that the user "be able to inspect or reset learned preferences,
    so personalization remains understandable and reversible."

`review_surface.learning_view` renders that view and filters nothing, "because
§8.7's own promise is that none of the learning is hidden from this view". It
took its rows from an INJECTED projection with no default, and nothing in the
product supplied one: `database_agent.learning.learning_records` is scoped to one
(scope, subject) pair at a time, and a view over everything a person's
corrections have taught the product needs the pairs enumerated first.

**The pairs are read, and the scopes are never spelled.** `learning_projection`
asks the events table which (scope, subject) pairs actually carry a user action.
A hard-coded list of P1's six scopes would stop reporting the day a seventh is
ratified, and the person would lose a whole class of their own corrections with
nothing on the screen to say so.

**Every read goes through `learning_records`, never through the table.** That is
the whole of R6: a reset deletes nothing and records a CUTOFF, so a projection
reading `events` directly would show a person exactly the preferences they had
just thrown away -- reversible in the store and not reversible on the screen,
which is the half §8.7 says has to be understandable.

**A row with no evidence is shown as it is.** `events` carries no `evidence_refs`
column in this build, so every row reaches the view uncited and says so in its
own explanation. A renderer that tidied those away would print "this product has
learned nothing about you" to somebody who had corrected it twice.

**Nothing here applies or deletes anything.** `learning_view.apply` and `.delete`
both raise by design, and this module calls neither; the reset gesture is P13's
`collect_reset`, which is a WRITE and belongs with the gestures rather than here.

**The heading does not say "your corrections", and that is a finding rather than
a preference.** Run against a live database, this view returns P10's own
`destination-tree edit` events -- rows stamped `user_id` and `polarity=accept`
whose own explanations read "the rules adopted plan version ... WITH NOBODY AT
THE SCREEN". `learning_records` selects on `user_id IS NOT NULL`, which is P1's
definition of a person's correction, and on this build the engine's tree edits
satisfy it. Filtering them out here would hide a defect behind a screen and would
break the one rule this view has, so the rows are shown and the heading claims
only what is true of them: these are scoped corrections RECORDED against the
user, not corrections the user is known to have made.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from database_agent.learning import learning_records

from review_surface.learning_view import learning_view

__all__ = ["learning_lines", "learning_projection"]


def learning_projection(
        conn: sqlite3.Connection,
) -> Callable[[], list[Mapping[str, object]]]:
    """A projection over every scoped correction this database holds.

    Returns a callable because `learning_view` takes one: the rows are read when
    the view is built rather than when the projection is made, so a view built
    after a reset in the same run reflects it.
    """

    def projection() -> list[Mapping[str, object]]:
        pairs = conn.execute(
            "SELECT DISTINCT correction_scope, correction_subject FROM events "
            "WHERE correction_scope IS NOT NULL "
            "  AND correction_subject IS NOT NULL AND user_id IS NOT NULL "
            "ORDER BY correction_scope, correction_subject").fetchall()
        return [dict(row)
                for scope, subject in pairs
                # P1's own reader, so the reset cutoff is honoured here exactly
                # as it is honoured everywhere else. Reading `events` again with
                # a wider WHERE would be a second home for R6.
                for row in learning_records(conn, scope, subject)]

    return projection


def learning_lines(conn: sqlite3.Connection, *,
                   projection: Callable[[], Sequence[Mapping[str, object]]],
                   subject_refs: Sequence[str]) -> tuple[str, ...]:
    """§8.7's view, ready to print. Every row P1 has, and no arithmetic over them.

    `subject_refs` is required and may be empty: it names the subjects whose
    prior rejections are re-presented beside the learned rows, and an empty
    sequence is a caller saying it is asking about none rather than a caller
    forgetting to say. The count is printed either way, so a screen that found no
    rejections says so instead of leaving the person to infer it from a gap.

    Each row's sentence is `LearnedPreferenceRow.explanation`, written by P13.
    Composing a second sentence here would put a rival account of the same fact
    in the product, and the two would drift.
    """
    view = learning_view(conn, subject_refs=subject_refs,
                         projection=projection)
    rows = tuple(
        f"  {row.correction_scope} / {row.correction_subject!r} "
        f"-- {row.explanation}"
        for row in view.rows)
    return (
        "",
        "Scoped corrections this database has recorded against you:",
        *rows,
        f"  {len(view.negative_examples)} prior rejections are recorded on "
        "this surface.",
        "  Nothing above has been applied by this screen. It is P1 that stores "
        "these and the part each was routed to that decides what it means.",
    )

"""§8.7's inspect surface. "What has this thing learned about me" had no answer.

    §8.7 requires that the user "be able to inspect or reset learned preferences,
    so personalization remains understandable and reversible."

`review_surface.learning_view` renders P1's scoped projection and filters nothing,
"because §8.7's own promise is that none of the learning is hidden from this
view". It had no caller and no projection: `database_agent.learning.learning_records`
is scoped to ONE (scope, subject) pair, so a view over everything a person's
corrections have taught the product needed something to enumerate the pairs, and
nothing did.

Two properties are load-bearing:

* **Nothing is filtered.** A correction with no stored evidence reaches the view
  and says so, rather than being dropped for looking thin. The sabotage is the
  obvious tidy-up: show only the rows that carry evidence.
* **A reset the person has already made stops speaking.** `learning_records`
  honours the reset cutoff and deletes nothing, and a projection that read the
  table directly would show a person preferences they had already thrown away.
"""
from __future__ import annotations

from database_agent.events import CORRECTION_SCOPES, append_event
from database_agent.learning import reset_preferences

from review_run.learning import learning_lines, learning_projection

#: P13's own registered name for a routed gesture, which is what a correction IS
#: on this table. Taken from the registry's spelling rather than invented here.
ROUTED = "review action routed"

T0 = "2026-09-02T00:00:00Z"
COMPONENT = "p13-fixture-1"


def _correction(conn, *, scope: str, subject: str, polarity: str) -> int:
    return append_event(
        conn, event_type=ROUTED, subsystem="P13",
        component_version=COMPONENT, observed_at=T0,
        explanation=f"the person said {polarity} about {subject}",
        correction_scope=scope, correction_subject=subject,
        polarity=polarity, proposal_class="destination", basis_key="subject",
        user_id="jy")


def test_every_correction_reaches_the_view_including_one_with_no_evidence(
        p13_conn):
    """§8.7's promise, as the whole output rather than as a count.

    `events` carries no `evidence_refs` column at all, so EVERY row in this build
    reaches the view with no citations -- which makes the "shown as it is rather
    than omitted" branch the only branch there is, and makes a renderer that
    dropped evidence-less rows produce an empty screen for a person who had
    corrected the product twice.
    """
    _correction(p13_conn, scope="file", subject="f-1", polarity="reject")
    _correction(p13_conn, scope="node", subject="n-1", polarity="accept")

    assert learning_lines(
        p13_conn, projection=learning_projection(p13_conn),
        subject_refs=()) == (
        "",
        "Scoped corrections this database has recorded against you:",
        "  file / 'f-1' -- a reject correction at 'file' scope about 'f-1', "
        "with no stored evidence reference; it is shown as it is rather than "
        "omitted, because §8.7 requires that none of the learning is hidden "
        "from this view",
        "  node / 'n-1' -- a accept correction at 'node' scope about 'n-1', "
        "with no stored evidence reference; it is shown as it is rather than "
        "omitted, because §8.7 requires that none of the learning is hidden "
        "from this view",
        "  0 prior rejections are recorded on this surface.",
        "  Nothing above has been applied by this screen. It is P1 that stores "
        "these and the part each was routed to that decides what it means.",
    )


def test_a_view_that_showed_only_evidenced_rows_is_empty_on_this_build(
        p13_conn):
    """The sabotage, and on this build it hides everything rather than something.

    A filter that looks conservative -- "only show a preference we can cite" --
    produces a screen saying the product has learned nothing about a person who
    has corrected it twice. That is the failure §8.7's no-filtering rule names,
    and it is invisible in a suite that only checks the rows it does show.
    """
    _correction(p13_conn, scope="file", subject="f-1", polarity="reject")
    projection = learning_projection(p13_conn)

    def only_evidenced():
        """The sabotage: drop what cannot be cited."""
        return [row for row in projection() if row.get("evidence_refs")]

    assert only_evidenced() == []
    assert len(projection()) == 1


def test_a_reset_the_person_already_made_is_honoured_by_the_projection(
        p13_conn):
    """Reversible AND understandable: a thrown-away preference stops appearing.

    `reset_preferences` deletes nothing and records a cutoff (R6), so a
    projection reading `events` directly would show the person exactly what they
    had just reset. Both halves are asserted -- one row before, none after --
    because asserting only the empty result would pass for a projection that
    never returned anything.
    """
    _correction(p13_conn, scope="file", subject="f-1", polarity="reject")
    assert len(learning_projection(p13_conn)()) == 1

    reset_preferences(p13_conn, "file", "f-1", author="P13",
                      component_version=COMPONENT, user_id="jy")
    assert learning_projection(p13_conn)() == []


def test_the_projection_covers_every_one_of_p1s_scopes_and_invents_none(
        p13_conn):
    """The pairs are read from the table; the scopes are checked against P1's.

    A projection that enumerated a hard-coded list of scopes would silently stop
    reporting the day P1 ratified a seventh, and the person would lose a whole
    class of their own corrections with nothing to say so.
    """
    for scope in CORRECTION_SCOPES:
        _correction(p13_conn, scope=scope, subject=f"s-{scope}",
                    polarity="accept")
    rows = learning_projection(p13_conn)()
    assert {row["correction_scope"] for row in rows} == set(CORRECTION_SCOPES)

"""P13's `review_actions` table, and the gesture that finally writes one.

`85` §5's dominant defect at the review surface: P13 shipped twenty-seven modules
and `review_surface.collect` -- the ONE function that turns a person's gesture
into a stored record -- had no caller anywhere in `src/` outside P13 itself. Every
run over a real folder therefore ended with `review_actions` empty, while the
report offered `--send-set` and a person typed it.

These tests are about the seam, not about P13: P13's own refusals are already
tested in `tests/p13/`. What is asserted here is that the seam REACHES them --
that a presentation is recorded for every set the screen shows, that a send
becomes a row, and that a protected set meets P13's own sentence rather than a
paraphrase of it.
"""
from __future__ import annotations

import dataclasses

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from grouping.schema import create_grouping_schema
from placement.residual import ResidualSet
from placement.schema import create_placement_schema
from privacy.display import RedactionSettings
from privacy.schema import create_privacy_schema
from privacy.vocabulary import SHOWN
from tree_design.schema import create_tree_schema

from review_gestures import (
    collect_set_send,
    collect_set_sends,
    record_set_presentations,
)
from review_surface.collect import PresentationRequired, ProtectedContainerHasNoAction
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK,
    SURFACE_RESIDUAL_SET,
    UNTOUCHED_PROTECTED,
)

T0 = "2026-09-04T00:00:00Z"
PLAN = "version-1"
COMPONENT = "review-gestures-fixture-1"
USER = "jy"

#: P7's five facets at their most permissive, which is what a plain local run
#: displays under. The VALUE is not what these tests are about -- what matters is
#: that the same settings object reaches the presentation and is stored with it.
SETTINGS = RedactionSettings(
    names=SHOWN, previews=SHOWN, thumbnails=SHOWN, ocr_text=SHOWN,
    location_data=SHOWN)


@pytest.fixture()
def db(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    create_privacy_schema(conn)
    create_tree_schema(conn)
    create_placement_schema(conn)
    from review_surface.schema import create_review_schema
    create_review_schema(conn)
    return conn


def _set(label: str, members: tuple[str, ...], *, protected: bool) -> ResidualSet:
    return ResidualSet(
        set_id=f"{PLAN}:{label}", plan_version=PLAN, label=label,
        file_count=len(members), representative_examples=members[:3],
        file_type_distribution=(), age_range=(), evidence_availability="partial",
        sensitivity_status="protected" if protected else "none",
        protected=protected, weak_graph_neighbours=(),
        reason_not_placed="nothing matched them well enough to decide",
        member_file_ids=members)


#: FOUR members, and the fourth is load-bearing. §7.5's `representative_examples`
#: is `member_file_ids[:3]`, so a set of three makes the sample and the membership
#: byte-identical -- and a seam that filed the SAMPLE instead of the set would
#: pass every assertion here while silently dropping a file from the record of
#: what was filed. Found by sabotage, which is what sabotage is for.
ORDINARY = _set("Not yet placed", ("f1", "f2", "f3", "f4"), protected=False)
SHIELDED = _set("Protected, and not filed in bulk", ("f9",), protected=True)


def test_every_surfaced_set_gets_a_presentation_including_the_protected_one(db):
    """"Marked and counted, never silently omitted" has no presentation exception.

    A protected set carries no ACTION -- the next test is that refusal -- but it
    is on the person's screen and §8.4 makes what was displayed a fact. A seam
    that recorded only the actionable sets would leave the one set whose display
    the standing rule is about as the only unrecorded one.
    """
    shown = record_set_presentations(
        db, sets=(ORDINARY, SHIELDED), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)

    assert set(shown) == {ORDINARY.set_id, SHIELDED.set_id}
    rows = db.execute(
        "SELECT surface, subject_ref FROM review_presentations "
        "ORDER BY subject_ref").fetchall()
    assert [row["surface"] for row in rows] == [SURFACE_RESIDUAL_SET] * 2
    assert {row["subject_ref"] for row in rows} == {
        ORDINARY.set_id, SHIELDED.set_id}


def test_a_send_becomes_a_review_action_naming_every_file_it_files(db):
    """The row `85` §5 says never appeared. `accept_bulk`, with its members.

    `--send-set` files a whole set in one gesture, which is what `accept_bulk`
    IS, and P13 refuses one that does not enumerate its members: "a filter
    expression cannot be re-read later to say which files a reversal applies
    to". The members are P11's own `member_file_ids` -- the seam counts nothing
    and re-derives nothing.
    """
    shown = record_set_presentations(
        db, sets=(ORDINARY,), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)

    action = collect_set_send(
        db, item=ORDINARY, area_label="Review Later", presented=shown,
        action_id="action-1", plan_version=PLAN, session_id=PLAN,
        correction_scope="file", user_id=USER, component_version=COMPONENT,
        acted_at=T0)

    assert action.action == ACTION_ACCEPT_BULK
    assert action.surface == SURFACE_RESIDUAL_SET
    assert action.bulk_member_refs == ORDINARY.member_file_ids
    row = db.execute("SELECT * FROM review_actions").fetchone()
    assert row["action_id"] == "action-1"
    assert row["subject_ref"] == ORDINARY.set_id
    # P13 routes a residual-set gesture to P11 and the seam spells no part name.
    assert "P11" in row["routed_to"]


def test_a_protected_set_meets_p13s_own_refusal_and_writes_no_action(db):
    """The worst defect this seam could introduce, refused by the part that owns it.

    The seam does not test `item.protected` and raise a sentence of its own. It
    hands P13 the subject kind P13 refuses on, so the person meets P13's
    paragraph -- the same shape `apply_run.approval` uses for the same reason.
    """
    shown = record_set_presentations(
        db, sets=(SHIELDED,), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)

    with pytest.raises(ProtectedContainerHasNoAction):
        collect_set_send(
            db, item=SHIELDED, area_label="Review Later", presented=shown,
            action_id="action-2", plan_version=PLAN, session_id=PLAN,
            correction_scope="file", user_id=USER, component_version=COMPONENT,
            acted_at=T0)

    assert db.execute(
        "SELECT count(*) AS c FROM review_actions").fetchone()["c"] == 0


def test_a_set_that_was_never_presented_cannot_be_acted_on(db):
    """§8.7's rule, reached through the seam rather than asserted about P13.

    Nothing is recorded, so a gesture typed at a set this run did not surface
    carries no record of what was shown -- which is the state `collect` refuses.
    """
    with pytest.raises(PresentationRequired):
        collect_set_send(
            db, item=ORDINARY, area_label="Review Later", presented={},
            action_id="action-3", plan_version=PLAN, session_id=PLAN,
            correction_scope="file", user_id=USER, component_version=COMPONENT,
            acted_at=T0)


def test_a_batch_holding_a_protected_set_is_refused_before_anything_is_decided(db):
    """The defect this ordering exists to end, measured on the owner's own folder.

    Today `--send-set "Protected, and not filed in bulk=Review Later"` reaches
    P11, which writes a `residual_set_decisions` row saying protected material is
    to be filed into a residual area, and only then raises -- uncaught, so the run
    ends "No plan was made" and the decision row survives. Collected first, the
    refusal lands before any decision exists.

    The ordinary set in the same batch is asserted BOTH ways on purpose: its
    gesture is a true record of what the person typed, and no decision was
    written for it either, because P11 was never reached.
    """
    shown = record_set_presentations(
        db, sets=(ORDINARY, SHIELDED), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)
    minted = iter(["action-a", "action-b"])

    with pytest.raises(ProtectedContainerHasNoAction):
        collect_set_sends(
            db,
            sends={ORDINARY.label: "Review Later",
                   SHIELDED.label: "Review Later"},
            sets=(ORDINARY, SHIELDED), presented=shown,
            mint_action_id=lambda: next(minted), plan_version=PLAN,
            session_id=PLAN, correction_scope="file", user_id=USER,
            component_version=COMPONENT, acted_at=T0)

    assert db.execute(
        "SELECT count(*) AS c FROM residual_set_decisions").fetchone()["c"] == 0
    acted = [row["subject_ref"] for row in db.execute(
        "SELECT subject_ref FROM review_actions")]
    assert acted == [ORDINARY.set_id]


def test_a_label_this_run_did_not_surface_is_left_for_p11_to_name(db):
    """The seam matches; it does not refuse. Two homes for one refusal is one too many.

    `act_on_residual_sets` refuses an unsurfaced label with the list of what the
    run DID surface, which is the sentence a person can act on. A refusal here
    would be a second, worse-worded copy of it.
    """
    shown = record_set_presentations(
        db, sets=(ORDINARY,), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)

    actions = collect_set_sends(
        db, sends={"Not yet placed (7 of 2)": "Review Later"},
        sets=(ORDINARY,), presented=shown, mint_action_id=lambda: "action-z",
        plan_version=PLAN, session_id=PLAN, correction_scope="file",
        user_id=USER, component_version=COMPONENT, acted_at=T0)

    assert actions == ()
    assert db.execute(
        "SELECT count(*) AS c FROM review_actions").fetchone()["c"] == 0


def test_the_seam_names_the_protected_subject_kind_p13_publishes(db):
    """Not a string of the seam's own. A second spelling is a second vocabulary."""
    import review_gestures

    assert review_gestures.PROTECTED_SUBJECT_KIND is UNTOUCHED_PROTECTED


def test_two_sets_under_one_label_each_get_their_own_presentation(db):
    """P11 lets a label name more than one set, and each gesture must cite its own.

    `act_on_residual_sets` holds `by_label` as a LIST for exactly this reason. A
    presentation map keyed by the label would keep the last set of the pair, and
    the first set's action would be recorded against a display of the OTHER set --
    a stored gesture whose evidence is somebody else's screen, which is the one
    thing §8.7's presentation requirement exists to prevent.
    """
    first = _set("Not yet placed", ("f1", "f2", "f3", "f4"), protected=False)
    second = dataclasses.replace(
        first, set_id=f"{PLAN}:Not yet placed#2",
        member_file_ids=("f5", "f6"), file_count=2,
        representative_examples=("f5", "f6"))

    shown = record_set_presentations(
        db, sets=(first, second), plan_version=PLAN, session_id=PLAN,
        settings=SETTINGS, user_id=USER, component_version=COMPONENT,
        rendered_at=T0)
    minted = iter(["action-1", "action-2"])
    collect_set_sends(
        db, sends={first.label: "Review Later"}, sets=(first, second),
        presented=shown, mint_action_id=lambda: next(minted), plan_version=PLAN,
        session_id=PLAN, correction_scope="file", user_id=USER,
        component_version=COMPONENT, acted_at=T0)

    cited = {row["subject_ref"]: row["presented_state_ref"] for row in db.execute(
        "SELECT subject_ref, presented_state_ref FROM review_actions")}
    assert cited == {
        first.set_id: shown[first.set_id].presented_state_ref,
        second.set_id: shown[second.set_id].presented_state_ref,
    }

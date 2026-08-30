# tests/p15/test_p15_plan_effects.py
"""§17 -- changing an answer opens a draft, and shows a diff. It never edits.

`66` §17:576-583 is the whole of what this file pins:

> When a user edits or re-runs a structural answer, the product creates a draft
> plan version. It shows a meaningful diff: which schemas become active or
> inactive, which templates are affected, which branches may need review, which
> placement proposals become invalid or newly possible, whether any protected area
> changes, and whether any filing policy is paused. It must NOT silently rename
> folders, reclassify files, reveal protected records, or move anything as a
> consequence of a changed answer.
>
> Existing approved structure remains stable unless the user explicitly adopts the
> new plan.

Both halves already existed as separate mechanisms -- `open_draft` and
`diff_versions` are P10's, `answered_options` is P15's -- and nothing joined them.
Today `--answer` supersedes a row and the next run simply comes out different, with
no draft, no diff, and nothing a person could look at to see what changed.

**The byte-for-byte test is deliberate.** `test_p10_versions.py` says why in its own
header: "unchanged" checked loosely is how evidence loss ships.
"""
from __future__ import annotations

import json
import sqlite3

import pytest

from questions.effects import (
    changed_answer, diff_for_answer_change, draft_for_answer_change,
)
from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import live_answer_id, record_answer, record_question
from questions.vocabulary import CONFIRMED, REVOKED, STRUCTURAL
from tree_design.diff import diff_versions
from tree_design.records import Node, PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import (
    freeze_version, nodes_for_version, open_draft, write_node, write_plan_version,
)
from tree_design.vocabulary import (
    DIFF_REMOVED, DIFF_RENAMED, DIFF_REPARENTED,
)

T0 = "2026-08-31T00:00:00Z"
T1 = "2026-08-31T01:00:00Z"
REF = "sha256:" + "12" * 32


def _ids(prefix="n"):
    counter = iter(range(1000))
    return lambda: f"{prefix}_{next(counter)}"


def _node(node_id, label, *, parent=None, version="plan_1", origin=None, ordinal=0):
    return Node(
        node_id=node_id, plan_version_id=version, node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=ordinal, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive",
        origin_node_id=origin or node_id, existing_path=None)


@pytest.fixture()
def both(conn):
    """One database carrying P10's tables and P15's, which is what a run has."""
    create_tree_schema(conn)
    create_questions_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n1", "Coursework"))
    write_node(conn, _node("n2", "PHYS1401", parent="n1", ordinal=1))
    freeze_version(conn, "plan_1")
    return conn


def a_question(**overrides) -> StructuralQuestion:
    fields = dict(
        question_id="reading.organization:columbia", answer_class=STRUCTURAL,
        prompt="What kind of material is Columbia?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("work", "I work there",
                                activates_schema="career"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=(REF,))
    fields.update(overrides)
    return StructuralQuestion(**fields)


def _answer(conn, question, option_id, *, at, supersedes=None, state=CONFIRMED):
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=option_id, state=state,
        scope=question.scope, user_id="jy", recorded_at=at,
        supersedes=supersedes,
        supersede_reason="the user answered this again" if supersedes else None))


def _change_the_answer(conn, question, first, second):
    record_question(conn, question, asked_at=T0)
    _answer(conn, question, first, at=T0)
    previous = live_answer_id(conn, question_id=question.question_id,
                              scope=question.scope)
    _answer(conn, question, second, at=T1, supersedes=previous)
    return changed_answer(conn, question_id=question.question_id,
                          scope=question.scope)


def _snapshot(conn, version):
    """The frozen tree as bytes, so "unchanged" is not checked loosely."""
    return json.dumps(
        [sorted(vars(node).items(), key=lambda pair: pair[0])
         for node in sorted(nodes_for_version(conn, version),
                            key=lambda node: node.node_id)],
        sort_keys=True, default=str).encode()


# --- A4: the draft ------------------------------------------------------------------


def test_changing_an_answer_opens_a_draft_and_the_frozen_tree_is_byte_identical(both):
    question = a_question()
    change = _change_the_answer(both, question, "study", "work")
    before = _snapshot(both, "plan_1")

    draft = draft_for_answer_change(
        both, change=change, from_version="plan_1", new_version_id="plan_2",
        created_at=T1, mint_node_id=_ids("d"), open_draft=open_draft)

    assert draft is not None
    assert draft.state == "draft"
    assert draft.predecessor_id == "plan_1"
    assert _snapshot(both, "plan_1") == before


def test_changing_an_answer_renames_moves_and_deletes_nothing(both):
    """§17:583: "Existing approved structure remains stable unless the user
    explicitly adopts the new plan." The draft is a COPY to look at, not an edit."""
    question = a_question()
    change = _change_the_answer(both, question, "study", "work")

    draft_for_answer_change(
        both, change=change, from_version="plan_1", new_version_id="plan_2",
        created_at=T1, mint_node_id=_ids("d"), open_draft=open_draft)

    kinds = {entry.kind for entry in
             diff_versions(both, before="plan_1", after="plan_2")}
    assert not (kinds & {DIFF_RENAMED, DIFF_REMOVED, DIFF_REPARENTED})
    assert {node.display_label for node in nodes_for_version(both, "plan_2")} == {
        "Coursework", "PHYS1401"}


def test_an_answer_re_confirmed_unchanged_opens_no_draft(both):
    """A person who re-types the answer they already gave has not changed
    anything, and should not find a draft plan waiting for them."""
    question = a_question()
    change = _change_the_answer(both, question, "study", "study")

    assert draft_for_answer_change(
        both, change=change, from_version="plan_1", new_version_id="plan_2",
        created_at=T1, mint_node_id=_ids("d"), open_draft=open_draft) is None
    assert both.execute(
        "SELECT COUNT(*) FROM plan_versions").fetchone()[0] == 1


def test_a_first_answer_is_not_a_change(both):
    """Nothing was superseded, so §17's "edits or re-runs" has not happened."""
    question = a_question()
    record_question(both, question, asked_at=T0)
    _answer(both, question, "study", at=T0)

    assert changed_answer(both, question_id=question.question_id,
                          scope=question.scope) is None


# --- A5: the diff, in §17's own terms ------------------------------------------------


def test_the_diff_names_the_schemas_that_become_active_and_inactive(both):
    question = a_question()
    change = _change_the_answer(both, question, "study", "work")

    diff = diff_for_answer_change(change)
    assert diff.schemas_activated == ("career",)
    assert diff.schemas_deactivated == ("academic",)


def test_an_answer_re_confirmed_unchanged_produces_an_empty_diff(both):
    """The negative twin. A diff that reported motion where there was none would
    make every re-confirmation look like a decision the person had not taken."""
    question = a_question()
    change = _change_the_answer(both, question, "study", "study")

    diff = diff_for_answer_change(change)
    assert diff.is_empty
    assert diff.schemas_activated == ()
    assert diff.schemas_deactivated == ()
    assert diff.templates_affected == ()
    assert diff.branches_needing_review == ()


def test_revoking_an_answer_deactivates_what_it_had_activated(both):
    """§17:585: "If an answer becomes unavailable or is revoked, the system should
    retain historical provenance but stop using the answer for future decisions."
    """
    question = a_question()
    record_question(both, question, asked_at=T0)
    _answer(both, question, "study", at=T0)
    previous = live_answer_id(both, question_id=question.question_id,
                              scope=question.scope)
    _answer(both, question, None, at=T1, supersedes=previous, state=REVOKED)

    diff = diff_for_answer_change(
        changed_answer(both, question_id=question.question_id,
                       scope=question.scope))
    assert diff.schemas_deactivated == ("academic",)
    assert diff.schemas_activated == ()


def test_a_changed_nesting_answer_names_the_template_and_the_branch(both):
    """§17:577's second and third items. The branch that may need review is the
    one the answer is scoped to -- which is the only branch it can affect."""
    question = a_question(
        question_id="branch:Coursework", scope="branch:Coursework",
        prompt="How should Coursework be organised?",
        options=(QuestionOption("subject", "By subject", gates_template="subject"),
                 QuestionOption("work_type>subject", "By work type then subject",
                                gates_template="work_type>subject")))
    change = _change_the_answer(both, question, "subject", "work_type>subject")

    diff = diff_for_answer_change(change)
    assert diff.templates_affected == ("subject", "work_type>subject")
    assert diff.branches_needing_review == ("Coursework",)


def test_the_things_p15_cannot_compute_are_named_rather_than_omitted(both):
    """§17:577 asks for six things and P15 can produce three of them.

    Placement proposals are P11's -- `tree_design/diff.py` says in as many words
    that the file-level consequence "is computed by P11 from this diff against its
    own placement decisions". Protected areas have no record before §15's
    relationship work, and filing policy has no producer at all yet.

    They are carried as an explicit `None` and NAMED, never as an empty tuple. An
    empty list reads as "nothing changed"; the standing rule on this project is
    that nothing is silently omitted, and a diff is the last place to start.
    """
    question = a_question()
    change = _change_the_answer(both, question, "study", "work")
    diff = diff_for_answer_change(change)

    assert diff.placement_proposals is None
    assert diff.protected_area_change is None
    assert diff.filing_policy_paused is None
    assert set(diff.not_computed) == {
        "placement_proposals", "protected_area_change", "filing_policy_paused"}
    for name in diff.not_computed:
        assert diff.why_not_computed[name]


def test_a_diff_that_reported_an_empty_list_for_an_uncomputed_thing_would_be_caught(both):
    """The negative twin for the omission rule: `is_empty` must not be able to say
    "nothing changed" while three of §17's six questions were never asked."""
    question = a_question()
    change = _change_the_answer(both, question, "study", "study")
    diff = diff_for_answer_change(change)

    assert diff.is_empty
    # ...and it still says which questions it did not answer.
    assert diff.not_computed


def test_a_revoked_answer_that_still_names_its_option_activates_nothing(both):
    """The line between "what you said" and "what still decides".

    `StructuralAnswer` refuses an option on `skipped` and `not_applicable` and
    PERMITS one on `revoked`: the row keeps what the person had chosen, which is
    the historical provenance §17:585 requires it to retain. So a reader that
    looked only at `option_id` would treat a withdrawal as a choice. The line is
    drawn here where `answered_options` draws it -- on the STATE.
    """
    question = a_question()
    record_question(both, question, asked_at=T0)
    _answer(both, question, "study", at=T0)
    previous = live_answer_id(both, question_id=question.question_id,
                              scope=question.scope)
    # The row a stricter `apply_answers` would not write, and the store permits.
    _answer(both, question, "study", at=T1, supersedes=previous, state=REVOKED)

    change = changed_answer(both, question_id=question.question_id,
                            scope=question.scope)
    assert change.after.option_id == "study"      # the provenance is kept
    assert change.option_after is None            # and it decides nothing
    diff = diff_for_answer_change(change)
    assert diff.schemas_activated == ()
    assert diff.schemas_deactivated == ("academic",)

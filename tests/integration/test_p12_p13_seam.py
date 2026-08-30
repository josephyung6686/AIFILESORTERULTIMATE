"""Wave G -- the joint seam. P13 collects the approval; P12 acts on it or refuses.

`74` §6 Wave G names three tasks and this file carries all three:

* **G2** `test_an_approval_collected_under_one_plan_version_does_not_authorize_a_move_under_another`
  with the twin `test_a_rejected_or_deferred_verdict_leaves_the_plan_unexecuted`.
* **G3** `test_every_completed_action_appears_with_all_eight_attributes` with the
  twin `test_an_absent_authorizing_policy_renders_as_an_explicit_none_and_is_never_faked`.
* **G1** the apply, stale-plan and undo-conflict items, once `mutation.undo` exists.

**Why this file assembles the seam itself.** Neither part may import the other:
P13's Done-means 22 guard forbids `src/review_surface/` reaching a mutation
surface, and P12's A5 forbids the reverse. So the join is the composition root's,
and this file plays that role -- it reads P13's stored approval and hands it to
P12's injected `approval_for`, exactly as `src/cli.py` must. A seam test that
mocked either side would prove that the mock fits, which is the defect this wave
exists to stop.

**Nothing here is a fixture stand-in.** Every record below is the real one: a
real file on a real disk, P1's real row, P7's real classification, P10's real
frozen tree, P11's real decision, P12's real `MovePlan` and journal entry, and
P13's real `review_approval` read back out of P13's own table.
"""
from __future__ import annotations

import dataclasses
import inspect
import itertools
import pathlib
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import record_file
from eval_harness.store import create_eval_schema
from placement.fixtures import GOLDEN_DECISIONS
from placement.records import Destination, Subject
from placement.schema import create_placement_schema
from placement.vocabulary import (
    AUTO_ELIGIBLE, PLACE, REVIEW_REQUIRED,
)
from privacy.classification_store import ClassificationRecord, ClassificationStore
from privacy.display import RedactionSettings
from privacy.schema import create_privacy_schema
from tree_design.fixtures import store_fixture_tree
from tree_design.records import Node, PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import write_node, write_plan_version

from mutation import vocabulary as v
from mutation.approval import ReviewApproval
from mutation.plan import PLAN_PRECONDITION_FIELDS
from mutation.constraints import FilesystemConstraints
from mutation.execute import apply_plan
from mutation.plan import build_plan, record_plan
from mutation.schema import create_mutation_schema

from review_surface.apply_seam import (
    ApplyReviewItem,
    StalePlanItem,
    UndoConflictItem,
    apply_review_item,
    controls_offered_on_an_undo_conflict,
    controls_that_would_apply_a_stale_plan,
    fixture_imports,
    stale_plan_item,
    undo_conflict_item,
)
from review_surface.activity import (
    ACTIVITY_ATTRIBUTES,
    AUTHORIZING_POLICY_HAS_NO_PRODUCER,
    UNDO_AVAILABILITY_HAS_NO_PRODUCER,
    ActionNotOneAction,
    ActivityEntry,
    CompletedAction,
    UndoAvailabilityRequired,
    activity_entry,
    activity_list,
    faked_authorizations,
)
from review_surface.approvals import (
    ApprovalPresentationRequired,
    approve,
)
from review_surface.presentation import record_presentation
from review_surface.schema import create_review_schema
from review_surface.store import approvals_for, record_approval
from review_surface.vocabulary import (
    ACTION_ACCEPT,
    ACTION_ACCEPT_BULK,
    ACTION_APPROVE_FOR_APPLY,
    ACTION_REFRESH_PLAN,
    SURFACE_APPLY,
    SURFACE_PLACEMENT,
    VERDICT_APPROVED,
    VERDICT_DEFERRED,
    VERDICT_REFRESH_REQUIRED,
    VERDICT_REJECTED,
)

FIXED = "2026-08-29T00:00:00Z"
COMPONENT = "seam-test-1"
USER = "jy"

SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")

CONSTRAINTS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
    max_path_bytes=4096, prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

PROTECTED_CLASSES = frozenset({
    "sensitive_personal", "highly_sensitive_credential_bearing"})


@dataclasses.dataclass(frozen=True)
class _Faked:
    """An activity row that DOES claim an authorizing policy.

    The twin needs something the guard can find. Built here rather than by
    mutating a real `ActivityEntry`, because a real one has no field to set --
    which is the property under test.
    """

    entry_id: str
    authorizing_policy: object


@dataclasses.dataclass(frozen=True)
class _Offering:
    """An item that DOES offer a control. What the two §8.3 guards are driven at."""

    plan_id: str
    offered_actions: tuple[str, ...]


def _package_sources():
    """Every module in `src/review_surface/`, as (name, source) pairs.

    Read off the installed package rather than off a path this file guesses, so
    a module added anywhere in the package is covered the day it lands.
    """
    import review_surface

    root = pathlib.Path(review_surface.__file__).resolve().parent
    return [(path.name, path.read_text()) for path in sorted(root.glob("*.py"))]


def _node(node_id, label, parent, **kwargs):
    base = dict(
        node_id=node_id, plan_version_id="plan-1", node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(), explanation="seam node",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id)
    base.update(kwargs)
    return Node(**base)


NODES = (_node("n-course", "Coursework", None),
         _node("n-phys", "PHYS1401", "n-course"))
LEGAL = frozenset({"n-course", "n-phys"})


# ---------------------------------------------------------------------------
# The composition root's own assembly, written out rather than imported.
# ---------------------------------------------------------------------------


@pytest.fixture()
def seam_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    create_mutation_schema(conn)
    create_review_schema(conn)
    store_fixture_tree(conn)
    # The same two nodes the plans are built against, in P10's own store, so
    # P13's ancestor label chain is read out of the tree rather than handed in.
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=FIXED, cross_folder_moves=True, selection_id="sel-1"))
    for node in NODES:
        write_node(conn, node)
    return conn


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    made = tmp_path / "seam_root"
    made.mkdir()
    return made


@pytest.fixture()
def landscape(root: Path):
    folders = {"root_documents": root / "Documents",
               "root_downloads": root / "Downloads"}
    for folder in folders.values():
        folder.mkdir()
    return folders


@pytest.fixture()
def clock():
    ticks = iter(f"2026-08-29T00:{minute:02d}:00Z" for minute in range(60))
    return lambda: next(ticks)


@pytest.fixture()
def ids():
    counter = itertools.count()
    return lambda: f"id-{next(counter)}"


def _plan(conn, landscape, ids, *, review_policy=REVIEW_REQUIRED,
          name="Syllabus.pdf", handling_class="personal_non_sensitive",
          protected=False):
    """One real file, one real P1 row, one real classification, one real plan."""
    source = landscape["root_documents"] / "Inbox" / name
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(b"PHYS1401 syllabus")
    stat = source.stat()
    file_id = record_file(
        conn, source, filename=name, normalized_filename=name.casefold(),
        extension=source.suffix, observed_size=stat.st_size,
        observed_timestamps=str(stat.st_mtime), parent_folder_context="Inbox",
        mime_type="application/pdf", detected_format="pdf",
        scan_state="included", materialized=True)
    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (file_id,)).fetchone()[0]
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class=handling_class, protected=protected, basis="user",
        evidence_refs=(), reliability_state="direct", observed_at=FIXED))
    golden = next(item for item in GOLDEN_DECISIONS if item.outcome == PLACE)
    decision = dataclasses.replace(
        golden, destination=Destination(node_id="n-phys", node_role="ordinary"),
        review_policy=review_policy,
        subject=Subject(kind="file", file_id=file_id,
                        content_hash=content_hash, group_id=None,
                        member_file_ids=()))
    built = build_plan(
        conn, decision, nodes=NODES, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders=landscape, volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
        expiration_state="no expiry configured",
        now=lambda: FIXED, mint_id=ids)
    assert built is not None
    plan, resolution = built
    record_plan(conn, plan, resolution, created_at=FIXED,
                component_version=COMPONENT)
    return plan, source


def _presented(conn, plan, *, surface=SURFACE_APPLY, plan_version=None):
    """P13 records what the person was shown before it collects what they said."""
    return record_presentation(
        conn, surface=surface, subject_ref=plan.plan_id,
        plan_version=plan_version or plan.organization_plan_version,
        session_id="s-1", settings=SHOWN, evidence_refs=(), user_id=USER,
        component_version=COMPONENT, rendered_at=FIXED).presented_state_ref


def _collect_approval(conn, plan, *, verdict=VERDICT_APPROVED, ids=None,
                      plan_version=None, presented_state_ref=None):
    """The whole P13 half: validate, append the §8.2 event, store the row."""
    version = plan_version or plan.organization_plan_version
    approval = approve(
        conn, approval_id=(ids() if ids else "approval-1"),
        plan_id=plan.plan_id,
        placement_decision_ref=plan.placement_decision_reference,
        plan_version=version,
        required_review_policy=plan.required_review_policy, verdict=verdict,
        presented_state_ref=(presented_state_ref
                             if presented_state_ref is not None
                             else _presented(conn, plan, plan_version=version)),
        user_id=USER, decided_at=FIXED, component_version=COMPONENT)
    record_approval(conn, approval)
    return approval


def _approval_for(conn):
    """The callable `src/cli.py` must hand P12, built out of P13's own reader.

    It is deliberately NOT scoped to the plan version at the read: P12's gate is
    what decides whether an approval authorizes this plan, and a reader that
    filtered the mismatch away would leave that gate untested and would hide
    from the person the fact that an approval exists but does not apply.
    """
    def lookup(plan_id: str) -> ReviewApproval | None:
        stored = approvals_for(conn, plan_id=plan_id)
        if not stored:
            return None
        latest = stored[-1]
        return ReviewApproval(
            approval_id=latest.approval_id, plan_id=latest.plan_id,
            placement_decision_ref=latest.placement_decision_ref,
            plan_version=latest.plan_version,
            required_review_policy=latest.required_review_policy,
            verdict=latest.verdict,
            presented_state_ref=latest.presented_state_ref,
            user_id=latest.user_id, decided_at=latest.decided_at)
    return lookup


def _apply(conn, plan, root, clock, ids, *, approval_for):
    return apply_plan(
        conn, plan, legal_destination_ids=LEGAL, source_root=root,
        destination_root=root, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        approval_for=approval_for, constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, normalize_filename=lambda name: name,
        unverified_copy_disposition=None, scan_state="included",
        materialized=True, component_version=COMPONENT, user_id=USER,
        now=clock, mint_id=ids)


# ---------------------------------------------------------------------------
# G2 -- `review_approval` produced by P13 and consumed by P12.
# ---------------------------------------------------------------------------


def test_an_approval_p13_recorded_is_what_p12s_gate_reads(
        seam_conn, landscape, root, clock, ids):
    """The chain, end to end, in the only direction that proves it is joined.

    Not a fixture and not a hand-built `ReviewApproval`: the record is collected
    through P13's own writer, stored in P13's own table, read back through P13's
    own reader, and handed to P12's gate. Before this wave the gate was complete
    and had no producer, so it could refuse and could never be satisfied.
    """
    plan, source = _plan(seam_conn, landscape, ids)
    assert plan.required_review_policy == REVIEW_REQUIRED

    # Nobody has answered yet: absence is the refusal.
    refused = _apply(seam_conn, plan, root, clock, ids,
                     approval_for=_approval_for(seam_conn))
    assert refused.result == f"{v.REFUSED}:{v.REVIEW_POLICY_UNSATISFIED}"
    assert source.exists()

    # A person reviews the plan and approves it.
    _collect_approval(seam_conn, plan)
    applied = _apply(seam_conn, plan, root, clock, ids,
                     approval_for=_approval_for(seam_conn))
    assert applied.result == v.APPLIED
    assert not source.exists()
    assert Path(applied.final_destination_path).exists()

    # And P13 said so in §8.2, once, under its own event name.
    rows = seam_conn.execute(
        "SELECT subsystem FROM events WHERE event_type = 'apply review approval'"
    ).fetchall()
    assert [row[0] for row in rows] == ["P13"]


def test_an_approval_collected_under_one_plan_version_does_not_authorize_a_move_under_another(
        seam_conn, landscape, root, clock, ids):
    """`74` §6 G2's named test. §8.8: approvals do not carry across versions."""
    plan, source = _plan(seam_conn, landscape, ids)
    other_version = f"{plan.organization_plan_version}-draft"
    assert other_version != plan.organization_plan_version

    _collect_approval(seam_conn, plan, plan_version=other_version)

    record = _apply(seam_conn, plan, root, clock, ids,
                    approval_for=_approval_for(seam_conn))

    assert record.result == f"{v.REFUSED}:{v.REVIEW_POLICY_UNSATISFIED}"
    assert source.exists(), "the person's file did not move"
    assert not Path(plan.resolved_destination_path).exists()

    refusal = seam_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? "
        "ORDER BY event_id DESC", (v.REFUSED_MOVE,)).fetchone()[0]
    assert "plan_version" in refusal, (
        "the person is told the approval was for a different version of the "
        "plan, not that their approval 'did not work'")


def test_a_rejected_or_deferred_verdict_leaves_the_plan_unexecuted(
        seam_conn, landscape, root, clock, ids):
    """`74` §6 G2's negative twin. Only `approved` satisfies the policy.

    Run over all three non-approving verdicts on three separate plans, because a
    guard that only ever sees `rejected` would pass over a producer that wrote
    `deferred` as though it were consent.
    """
    for index, verdict in enumerate(
            (VERDICT_REJECTED, VERDICT_DEFERRED, VERDICT_REFRESH_REQUIRED)):
        plan, source = _plan(seam_conn, landscape, ids,
                             name=f"Syllabus-{index}.pdf")
        _collect_approval(seam_conn, plan, verdict=verdict, ids=ids)

        record = _apply(seam_conn, plan, root, clock, ids,
                        approval_for=_approval_for(seam_conn))

        assert record.result == f"{v.REFUSED}:{v.REVIEW_POLICY_UNSATISFIED}", (
            f"a {verdict!r} verdict executed the plan")
        assert source.exists(), f"a {verdict!r} verdict moved the person's file"
        assert record.directories_created_by_this_action == ()


def test_p13_refuses_to_record_an_approval_with_no_recorded_presentation(
        seam_conn, landscape, ids):
    """§8.4 and §8.7: an approval is a judgement about something that was SHOWN.

    An approval whose `presented_state_ref` names no recorded presentation
    carries no evidence of what the person was looking at when they gave it,
    which makes it uninterpretable later and unauditable now.
    """
    plan, _ = _plan(seam_conn, landscape, ids)
    with pytest.raises(ApprovalPresentationRequired):
        _collect_approval(seam_conn, plan, presented_state_ref="ps-never-shown")


def test_an_approval_is_refused_when_what_was_shown_was_a_different_version(
        seam_conn, landscape, ids):
    """The presentation and the approval describe ONE moment or neither does."""
    plan, _ = _plan(seam_conn, landscape, ids)
    shown_elsewhere = _presented(seam_conn, plan, plan_version="plan-9")
    with pytest.raises(ApprovalPresentationRequired):
        _collect_approval(seam_conn, plan,
                          presented_state_ref=shown_elsewhere)


def test_an_approval_is_refused_when_what_was_shown_was_a_different_surface(
        seam_conn, landscape, ids):
    """A glance at a placement card is not a review of an apply plan."""
    plan, _ = _plan(seam_conn, landscape, ids)
    elsewhere = _presented(seam_conn, plan, surface=SURFACE_PLACEMENT)
    with pytest.raises(ApprovalPresentationRequired):
        _collect_approval(seam_conn, plan, presented_state_ref=elsewhere)


def test_a_plan_that_demands_no_review_is_not_given_an_approval_to_lift(
        seam_conn, landscape, root, clock, ids):
    """`auto_eligible` needs none, and P13 producing one changes nothing."""
    plan, _ = _plan(seam_conn, landscape, ids, review_policy=AUTO_ELIGIBLE)
    record = _apply(seam_conn, plan, root, clock, ids,
                    approval_for=_approval_for(seam_conn))
    assert record.result == v.APPLIED
    assert approvals_for(seam_conn, plan_id=plan.plan_id) == ()


# ---------------------------------------------------------------------------
# G3 -- `66` §9's activity list, rendered end to end.
#
# "Every completed action appears in a reviewable activity list with the source
# path, destination path, evidence summary, policy that authorized it, collision
# behavior, move time, current status, and undo availability."
#
# Six of the eight have a producer today. Two do not, and this is where that is
# carried rather than filled: there is no filing-policy record in any part's
# Contract-out (`74` §10), and P12's undo retention is Wave F's.
# ---------------------------------------------------------------------------


def _completed(conn, plan):
    """The three P12 records one completed action is made of, by P12's readers.

    `src/cli.py` does exactly this. P13 may not import P12 and P12 may not import
    P13, so assembling the triple is the composition root's job and the readers
    it uses are P12's own published ones -- not a query this file invented.
    """
    from mutation.execute import JournalEntry, executions_for
    from mutation.plan import current_plan

    entry = JournalEntry.for_plan(conn, plan.plan_id)
    if entry is None:
        return None
    return CompletedAction(
        journal_entry=entry,
        execution=executions_for(conn, plan.plan_id)[-1],
        plan=current_plan(conn, plan.plan_id))


def _applied(seam_conn, landscape, root, clock, ids, **planning):
    """One real, approved, completed move. The precondition for an activity row."""
    plan, source = _plan(seam_conn, landscape, ids, **planning)
    _collect_approval(seam_conn, plan, ids=ids)
    record = _apply(seam_conn, plan, root, clock, ids,
                    approval_for=_approval_for(seam_conn))
    assert record.result == v.APPLIED
    return plan, source, record


def test_every_completed_action_appears_with_all_eight_attributes(
        seam_conn, landscape, root, clock, ids):
    """`74` §6 G3's named test, over a move that really happened."""
    plan, source, record = _applied(seam_conn, landscape, root, clock, ids)

    entries = activity_list([_completed(seam_conn, plan)],
                            undo_availability_for=lambda entry: None)
    assert len(entries) == 1
    entry = entries[0]

    # All eight are present. Read off `66` §9's own list rather than spelled
    # again here, so a renderer that dropped one is caught by the list itself.
    assert len(ACTIVITY_ATTRIBUTES) == 8
    for attribute in ACTIVITY_ATTRIBUTES:
        assert hasattr(entry, attribute), attribute

    # And each of the six that HAS a producer carries the real value, not a
    # plausible one. `source_path` and `destination_path` are P12's own -- P13
    # composed neither and resolved neither; §9 requires them and B3's line is
    # about who RESOLVES a path, not about who may show one P12 published.
    assert entry.source_path == plan.expected_source_path == str(source)
    assert entry.destination_path == record.final_destination_path
    assert entry.evidence_summary == plan.reason_and_evidence_summary
    assert entry.collision_behaviour == plan.collision_policy
    assert entry.move_time == record.finished_at
    assert entry.status == v.APPLIED

    # The two with no producer are explicit, named absences -- never a blank,
    # never omitted, and never a nearby value wearing the missing one's name.
    assert entry.authorizing_policy is None
    assert entry.authorizing_policy_absence == AUTHORIZING_POLICY_HAS_NO_PRODUCER
    assert "filing policy" in entry.authorizing_policy_absence
    assert entry.undo_availability is None
    assert entry.undo_availability_absence == UNDO_AVAILABILITY_HAS_NO_PRODUCER


def test_an_absent_authorizing_policy_renders_as_an_explicit_none_and_is_never_faked(
        seam_conn, landscape, root, clock, ids):
    """`74` §6 G3's negative twin. The gap is CARRIED, not filled.

    Three plausible fakes are available at the moment the row is built, and each
    would read as an answer to "what authorized this?": the plan's
    `required_review_policy`, which is the policy that DEMANDED REVIEW and is the
    opposite claim; the approval's copy of the same value; and P7's
    `permitting_policy`, which is a privacy exemption rather than a filing
    authority. None of the three is `66` §9's *policy that authorized it*, and the
    guard below is run against a row that carries one.
    """
    plan, _, _ = _applied(seam_conn, landscape, root, clock, ids)
    real = activity_list([_completed(seam_conn, plan)],
                         undo_availability_for=lambda entry: None)

    # The fake was available: this is a real, non-empty policy string sitting one
    # attribute away. A guard whose fake was unavailable proves nothing.
    assert plan.required_review_policy == REVIEW_REQUIRED

    assert faked_authorizations(real) == []
    assert faked_authorizations([_Faked(entry_id="fake-1",
                                        authorizing_policy=plan.required_review_policy)])
    assert faked_authorizations([_Faked(entry_id="fake-2",
                                        authorizing_policy="auto_eligible")])
    # An empty string is a fake too: it renders as "authorized by nothing in
    # particular" rather than as "nothing here can say".
    assert faked_authorizations([_Faked(entry_id="fake-3",
                                        authorizing_policy="")])

    # And there is no parameter through which one could be supplied. The C2
    # house pattern: a value that cannot be passed cannot be passed by accident.
    field_names = {f.name for f in dataclasses.fields(ActivityEntry)}
    assert "authorizing_policy" not in field_names
    parameters = set(inspect.signature(activity_entry).parameters)
    assert not parameters & {"authorizing_policy", "policy", "authorized_by"}


def test_undo_availability_is_injected_and_absent_means_refuse(
        seam_conn, landscape, root, clock, ids):
    """A7 one part over: `66` §11's retention is the composition root's.

    P12's undo retention is Wave F's and does not exist yet, so what the product
    can honestly say today is "nothing here can tell you". Guessing `66` §11's
    90-day default inside P13 would put a number this package has no authority to
    choose in front of a person as a promise.
    """
    plan, _, _ = _applied(seam_conn, landscape, root, clock, ids)
    action = _completed(seam_conn, plan)

    with pytest.raises(UndoAvailabilityRequired):
        activity_list([action], undo_availability_for=None)

    # And when a producer DOES exist, what it says is what is shown.
    answered = activity_list(
        [action], undo_availability_for=lambda entry: "undoable until 2026-11-27")
    assert answered[0].undo_availability == "undoable until 2026-11-27"
    assert answered[0].undo_availability_absence is None


def test_an_action_stitched_from_three_different_plans_is_refused(
        seam_conn, landscape, root, clock, ids):
    """One row is one action. Three records from three actions are not one."""
    first, _, _ = _applied(seam_conn, landscape, root, clock, ids)
    second, _, _ = _applied(seam_conn, landscape, root, clock, ids,
                            name="Other.pdf")
    mixed = dataclasses.replace(_completed(seam_conn, first),
                                plan=_completed(seam_conn, second).plan)
    with pytest.raises(ActionNotOneAction):
        activity_list([mixed], undo_availability_for=lambda entry: None)


def test_a_refused_move_has_no_activity_row_and_is_not_invented_one(
        seam_conn, landscape, root, clock, ids):
    """§9 is about COMPLETED actions; §19's visibility of a refusal is an event.

    A refused move never happened, so there is no source it left, no destination
    it reached and no time it took. A row for it would have to invent all three.
    """
    plan, source = _plan(seam_conn, landscape, ids)
    record = _apply(seam_conn, plan, root, clock, ids,
                    approval_for=_approval_for(seam_conn))
    assert record.result == f"{v.REFUSED}:{v.REVIEW_POLICY_UNSATISFIED}"
    assert source.exists()
    assert _completed(seam_conn, plan) is None
    assert activity_list([], undo_availability_for=lambda entry: None) == ()

    # The refusal is visible where §19 puts it, so nothing has gone quiet.
    assert seam_conn.execute(
        "SELECT count(*) FROM events WHERE event_type = ?",
        (v.REFUSED_MOVE,)).fetchone()[0] == 1


def test_the_activity_list_is_ordered_by_when_the_move_happened(
        seam_conn, landscape, root, clock, ids):
    """"What moved today" needs an order, and it is the move's own, not the caller's."""
    first, _, _ = _applied(seam_conn, landscape, root, clock, ids)
    second, _, _ = _applied(seam_conn, landscape, root, clock, ids,
                            name="Later.pdf")
    actions = [_completed(seam_conn, second), _completed(seam_conn, first)]
    entries = activity_list(actions, undo_availability_for=lambda entry: None)
    assert [entry.plan_id for entry in entries] == [first.plan_id,
                                                    second.plan_id]
    assert entries[0].move_time <= entries[1].move_time


# ---------------------------------------------------------------------------
# G1 -- P13's apply seam, against P12's real records.
#
# `74` §6 G1 reads "re-point P13's `apply_seam` at the real P12 records and
# delete `tests/p13/p12_fixtures.py`". Neither existed: P13 Task 11 was never
# built, and the fixture module has never been in this repository's history. What
# `src/review_surface/` carried was the vocabulary and the routing for two
# surfaces nothing could construct -- `SURFACE_APPLY` and `SURFACE_UNDO_CONFLICT`
# both routing to P12, and no builder for either. So G1 builds the seam rather
# than re-pointing it, and there is no fixture to delete.
# ---------------------------------------------------------------------------


def test_p13_renders_p12s_real_apply_item_stale_triggers_and_undo_conflict(
        seam_conn, landscape, root, clock, ids):
    """`74` §6 G1's named test. Three items, three real P12 records, no fixture."""
    from mutation.preconditions import evaluate_preconditions, refresh_prompt
    from mutation.undo import undo

    # --- 1. The apply review item, off a real move plan -------------------
    plan, source = _plan(seam_conn, landscape, ids)
    item = apply_review_item(seam_conn, plan)

    # §8.3's thirteen precondition fields, each carrying the plan's own value.
    # Compared field by field against P12's published list rather than against a
    # list respelled here, so a field P12 adds is a failure and not a silence.
    assert len(PLAN_PRECONDITION_FIELDS) == 13
    for field in PLAN_PRECONDITION_FIELDS:
        assert getattr(item, field) == getattr(plan, field), field
    # Plus the five §8.3 asks for beside them.
    assert item.intended_display_name == plan.intended_display_name
    assert item.filesystem_safe_name == plan.filesystem_safe_name
    assert item.placement_decision_reference == plan.placement_decision_reference
    assert item.plan_version == plan.organization_plan_version
    # And B3's chain, read out of P10's store rather than handed in.
    assert item.destination_label_chain == ("Coursework", "PHYS1401")

    # --- 2. The stale plan item, off a real precondition verdict -----------
    source.write_bytes(b"somebody else edited this after the preview")
    verdict = evaluate_preconditions(
        seam_conn, plan, checkpoint="prepare", legal_destination_ids=LEGAL,
        occupant_at_prepare=None, component_version=COMPONENT,
        materialized=True, now=clock)
    assert verdict.trigger == v.CONTENT_HASH_DIFFERS

    stale = stale_plan_item(verdict, plan, sentence=refresh_prompt(verdict))
    assert stale.trigger == v.CONTENT_HASH_DIFFERS
    assert stale.sentence == "This file changed after the preview."
    # Expected against observed, both shown. A stale item that showed only one
    # of them says "something changed" and not "this changed".
    assert stale.expected_content_hash == plan.expected_content_hash
    assert stale.observed_hash_result == verdict.hash_result
    assert stale.expected_source_path == plan.expected_source_path
    assert stale.observed_source_path == verdict.observed_source_path
    # A refresh, and nothing that applies it.
    assert stale.offered_actions == (ACTION_REFRESH_PLAN,)
    assert controls_that_would_apply_a_stale_plan([stale]) == []

    # --- 3. The undo conflict item, off a real undo verdict ----------------
    fresh, _, executed = _applied(seam_conn, landscape, root, clock, ids,
                                  name="Undoable.pdf")
    entry = _completed(seam_conn, fresh).journal_entry
    # Somebody edits the file after it was filed. This is §8.3's own case.
    Path(executed.final_destination_path).write_bytes(b"edited at the destination")
    answered = undo(
        seam_conn, entry.entry_id, constraints=CONSTRAINTS,
        unverified_copy_disposition=None, normalize_filename=lambda name: name,
        scan_state="included", materialized=True, component_version=COMPONENT,
        user_id=USER, now=clock, mint_id=ids)
    assert answered.verdict == v.CONFLICT_DESTINATION_CONTENT_CHANGED

    conflict = undo_conflict_item(answered)
    assert conflict.sentence == (
        "This action cannot be undone automatically because the file changed "
        "after it was moved.")
    assert conflict.original_source_path == entry.original_source_path
    assert conflict.destination_path == entry.destination_path
    assert conflict.expected_content_hash == entry.content_hash_at_movement
    assert conflict.observed_content_hash == answered.observed_destination_hash
    assert conflict.observed_content_hash != conflict.expected_content_hash
    # §8.3: undo must not force a rollback, so nothing here offers to.
    assert conflict.offered_actions == ()
    assert controls_offered_on_an_undo_conflict([conflict]) == []
    # And the file is still where P12 put it: rendering a conflict moved nothing.
    assert Path(executed.final_destination_path).read_bytes() == (
        b"edited at the destination")


def test_review_surface_imports_no_test_fixture_module():
    """`74` §6 G1's negative twin, proven against a module that really does it.

    The task said to delete `tests/p13/p12_fixtures.py`. It has never existed --
    `git log --all` over that path is empty -- so the assertion worth keeping is
    not that it was removed but that no such thing can come back: nothing in
    `src/review_surface/` may import a tests-only stand-in, under either import
    form or any alias.
    """
    assert not (pathlib.Path("tests") / "p13" / "p12_fixtures.py").exists()
    assert fixture_imports(_package_sources()) == []
    # The twin half. A guard whose only evidence is "it found nothing" is worth
    # nothing, so it is driven against sources that genuinely import one.
    assert fixture_imports(
        [("offender.py", "from tests.p13.p12_fixtures import APPLY_ITEM\n")])
    assert fixture_imports([("offender.py", "import tests.p13.p12_fixtures\n")])
    assert fixture_imports(
        [("offender.py", "from placement.fixtures import GOLDEN_DECISIONS\n")])
    assert fixture_imports(
        [("offender.py", "import placement.fixtures as f\n")])
    # A clean module is clean, so the guard is about fixtures and not about
    # having imports at all.
    assert fixture_imports([("clean.py", "import json\nimport sqlite3\n")]) == []


def test_no_item_offers_to_apply_a_stale_plan_or_force_an_undo(
        seam_conn, landscape, root, clock, ids):
    """The two controls §8.3 forbids, and the guards that would find them.

    Both guards take their items as an argument so they can be pointed at
    sabotaged ones. Four guards on this project had quietly stopped being able
    to fail, and a guard only ever run over items that cannot carry the thing it
    looks for is in exactly that state.
    """
    from mutation.preconditions import evaluate_preconditions, refresh_prompt

    plan, source = _plan(seam_conn, landscape, ids)
    source.write_bytes(b"changed")
    verdict = evaluate_preconditions(
        seam_conn, plan, checkpoint="prepare", legal_destination_ids=LEGAL,
        occupant_at_prepare=None, component_version=COMPONENT,
        materialized=True, now=clock)
    stale = stale_plan_item(verdict, plan, sentence=refresh_prompt(verdict))

    assert controls_that_would_apply_a_stale_plan([stale]) == []
    # The sabotage: a stale item that offers the person a way to run it anyway.
    # Every applying action is tried, because a guard that caught only `accept`
    # would leave `approve_for_apply` -- the one that reaches P12 -- wide open.
    for applying in (ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_APPROVE_FOR_APPLY):
        assert controls_that_would_apply_a_stale_plan(
            [_Offering(plan_id="sabotage", offered_actions=(applying,))]), applying
    # A refresh is not an applying control, so the guard is about applying and
    # not about offering anything at all.
    assert controls_that_would_apply_a_stale_plan(
        [_Offering(plan_id="ok", offered_actions=(ACTION_REFRESH_PLAN,))]) == []

    assert controls_offered_on_an_undo_conflict([]) == []
    assert controls_offered_on_an_undo_conflict(
        [_Offering(plan_id="sabotage", offered_actions=(ACTION_ACCEPT,))])

    # And no field on any of the three items could carry a force flag. A field
    # that does not exist cannot be populated by a later caller in a hurry.
    forced = {"force", "force_undo", "forced", "apply_anyway", "override",
              "ignore_conflict", "ignore_staleness"}
    for record in (ApplyReviewItem, StalePlanItem, UndoConflictItem):
        assert not {f.name for f in dataclasses.fields(record)} & forced
    # The name check would notice one, so it is a check and not a formality.
    assert {f.name for f in dataclasses.fields(_Offering)} | {"force"} & forced


@pytest.mark.xfail(strict=True, reason=(
    "`src/mutation/retention.py:272` fills `66` §9's `authorizing_policy` with "
    "the plan's `required_review_policy` -- the policy that DEMANDED REVIEW, "
    "which is the opposite claim to the policy that AUTHORIZED THE MOVE. `74` "
    "§6 G3's twin rules that the gap is carried and never filled, and `74` §10 "
    "records that no filing-policy record exists in any part's Contract-out. "
    "The file is P12 Wave F3's; this reports the disagreement rather than "
    "editing another wave's module, and it turns from xfail into a failure the "
    "day the field is reconciled with `review_surface.activity`."))
def test_p12s_own_activity_row_carries_no_authorizing_policy_either(
        seam_conn, landscape, root, clock, ids):
    from mutation.retention import UndoRetention, activity

    _applied(seam_conn, landscape, root, clock, ids)
    rows = activity(
        seam_conn,
        retention=UndoRetention(choice="until_cleared", period=None,
                                set_at=FIXED, set_by=USER),
        at="2026-08-29T01:00:00Z")
    assert rows
    assert faked_authorizations(rows) == []

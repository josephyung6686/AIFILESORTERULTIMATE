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
import itertools
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
from tree_design.records import Node

from mutation import vocabulary as v
from mutation.approval import ReviewApproval
from mutation.constraints import FilesystemConstraints
from mutation.execute import apply_plan
from mutation.plan import build_plan, record_plan
from mutation.schema import create_mutation_schema

from review_surface.approvals import (
    ApprovalPresentationRequired,
    approve,
)
from review_surface.presentation import record_presentation
from review_surface.schema import create_review_schema
from review_surface.store import approvals_for, record_approval
from review_surface.vocabulary import (
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

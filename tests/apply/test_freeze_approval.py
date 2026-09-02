"""The freeze IS the approval, and it approves only what the person was shown.

The owner ruled it on 2026-09-02: a person who has seen a proposal and typed
`--freeze` has approved those placements. `91` §6 is what that ruling answers --
over the shipped pipeline every placement came back `review_required`, so
`--freeze` froze nothing and the product could move a file and never would.

Three things bound the ruling, and each has its own test below.

* **An approval names what was on the screen.** `review_surface.approvals.approve`
  already refuses an approval whose presentation is missing, is of another
  subject or is of another plan version. What was missing is a CALLER: nothing a
  person runs wrote a `review_presentations` row. A file the report did not name
  is a file nobody saw, and a freeze may not approve it.
* **Protected material is never approved in bulk.** A passport lands in
  `review_required` by `placement.privacy.review_policy_for`'s third rule, so a
  freeze that approved every reviewable placement would be a bulk gesture over a
  passport. It is held, named, and left for the one surface that can grant it.
* **`blocked_pending_user` is not `review_required`.** `placement.privacy`'s own
  words: *"a reviewer can act on a decision that merely needs confirming, and
  cannot act on one whose subject nothing has classified."* A freeze is a
  reviewer.
"""
from __future__ import annotations

import dataclasses

import pytest
from mutation.approval import approval_verdict
from placement.records import PrivacyState
from placement.vocabulary import BLOCKED_PENDING_USER, REVIEW_REQUIRED
from privacy.display import RedactionSettings
from review_surface.approvals import ApprovalPresentationRequired
from review_surface.presentation import presented_state
from review_surface.schema import create_review_schema
from review_surface.store import approvals_for
from review_surface.vocabulary import SURFACE_APPLY, VERDICT_APPROVED

from apply_run.approval import approval_reader, approval_writer
from apply_run.report import freeze_lines
from apply_run.freeze import (
    AWAITING_CLASSIFICATION, NOT_SHOWN, PROTECTED_NEEDS_PERMISSION,
    freeze,
)

from .conftest import COLLISION_POLICY, CONSTRAINTS, LEGAL, NODES, PROTECTED_CLASSES

#: What the person's screen was set to when they read the proposal. Every facet
#: `redacted` is `privacy.defaults.MORE_REDACTING`, which is what a fresh install
#: resolves to, so this is the posture a real first freeze happens under.
SETTINGS = RedactionSettings(
    names="redacted", previews="redacted", thumbnails="redacted",
    ocr_text="redacted", location_data="redacted")


@pytest.fixture()
def reviewable(world):
    """The article needs a person to confirm it; everything else is automatic."""
    return tuple(
        dataclasses.replace(decision, review_policy=REVIEW_REQUIRED)
        if decision.destination.node_id == "n-read" else decision
        for decision in world.decisions)


def _article(decisions):
    return next(d.subject.file_id for d in decisions
                if d.destination.node_id == "n-read")


def _freeze(world, decisions, *, ids, clock, shown, user_id="jy"):
    create_review_schema(world.conn)
    return freeze(
        world.conn, decisions, nodes=NODES, legal_destination_ids=LEGAL,
        cross_folder_moves=True, constraints=CONSTRAINTS,
        high_level_folders={"root_documents": world.documents},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=COLLISION_POLICY,
        expiration_state="no expiry configured",
        shown_file_ids=frozenset(shown),
        approve_reviewed=approval_writer(
            world.conn, settings=SETTINGS, session_id="session-under-test",
            user_id=user_id, component_version="apply-test", mint_id=ids),
        component_version="apply-test", now=clock, mint_id=ids)


def test_a_placement_the_person_was_shown_is_frozen_with_an_approval(
        world, reviewable, ids, clock):
    """The whole ruling in one assertion: it is frozen, and it carries consent."""
    article = _article(reviewable)
    proposal = _freeze(world, reviewable, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in reviewable})

    assert len(proposal.plans) == 4
    assert proposal.held == ()
    plan = next(p for p in proposal.plans if p.file_id == article)
    assert plan.required_review_policy == REVIEW_REQUIRED

    approvals = approvals_for(world.conn, plan_id=plan.plan_id)
    assert [a.verdict for a in approvals] == [VERDICT_APPROVED]
    assert approvals[0].plan_version == plan.organization_plan_version
    assert approvals[0].placement_decision_ref == plan.placement_decision_reference
    assert approvals[0].user_id == "jy"


def test_the_approval_names_the_presentation_the_person_was_actually_shown(
        world, reviewable, ids, clock):
    """`review_surface.presentation`'s row, written by something a person runs.

    Before this, `record_presentation` had no caller outside its own package, so
    the record that makes an approval provable was written by nothing. The
    approval's ref has to resolve, and it has to resolve to THIS plan on the
    apply surface -- otherwise the answer to "what was this person looking at?"
    is wrong rather than missing.
    """
    article = _article(reviewable)
    proposal = _freeze(world, reviewable, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in reviewable})
    plan = next(p for p in proposal.plans if p.file_id == article)
    approval = approvals_for(world.conn, plan_id=plan.plan_id)[0]

    shown = presented_state(world.conn, approval.presented_state_ref)
    assert shown is not None
    assert shown.surface == SURFACE_APPLY
    assert shown.subject_ref == plan.plan_id
    assert shown.plan_version == plan.organization_plan_version
    # The policy in force at the moment of display, kept whole. A facet-by-facet
    # record would let a ref minted under three loosened facets stand in for one
    # minted under four.
    assert shown.redaction_policy == {
        "names": "redacted", "previews": "redacted", "thumbnails": "redacted",
        "ocr_text": "redacted", "location_data": "redacted"}
    # The report displays no observation key, and an empty tuple is the honest
    # answer rather than an absent one.
    assert shown.evidence_refs == ()


def test_a_file_the_report_never_named_is_held_and_no_approval_is_written(
        world, reviewable, ids, clock):
    """The guard that makes "informed" a fact rather than an assumption."""
    article = _article(reviewable)
    proposal = _freeze(
        world, reviewable, ids=ids, clock=clock,
        shown={d.subject.file_id for d in reviewable} - {article})

    assert len(proposal.plans) == 3
    assert [(item.file_id, item.reason) for item in proposal.held] == [
        (article, NOT_SHOWN)]
    assert article not in {plan.file_id for plan in proposal.plans}
    assert world.conn.execute(
        "SELECT COUNT(*) FROM review_approvals").fetchone()[0] == 0
    # And no presentation either: a row saying this was displayed would be a
    # false record of a moment that did not happen.
    assert world.conn.execute(
        "SELECT COUNT(*) FROM review_presentations").fetchone()[0] == 0


def test_a_protected_file_is_never_approved_by_a_freeze_and_is_named(
        world, ids, clock):
    """A freeze may not become a bulk gesture over a passport.

    `placement.privacy.review_policy_for`'s third rule puts a protected file with
    no permitting policy into `review_required`, which is exactly the queue this
    gesture now empties. So the exclusion is explicit here rather than inherited:
    the standing rule is that protected material is marked and counted, and being
    swept into an approval nobody typed individually is neither.
    """
    passport = next(d.subject.file_id for d in world.decisions
                    if d.privacy.protected)
    decisions = tuple(
        dataclasses.replace(d, review_policy=REVIEW_REQUIRED)
        if d.privacy.protected else d
        for d in world.decisions)

    proposal = _freeze(world, decisions, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in decisions})

    assert [(item.file_id, item.reason, item.detail) for item in proposal.held] \
        == [(passport, PROTECTED_NEEDS_PERMISSION,
             "highly_sensitive_credential_bearing")]
    assert passport not in {plan.file_id for plan in proposal.plans}
    assert world.conn.execute(
        "SELECT COUNT(*) FROM review_approvals").fetchone()[0] == 0


def test_an_unclassified_placement_is_not_approvable_and_says_so_in_its_own_words(
        world, ids, clock):
    """`blocked_pending_user` is not a review queue.

    `placement.privacy.blocked_policy`: *"a reviewer can act on a decision that
    merely needs confirming, and cannot act on one whose subject nothing has
    classified. Collapsing the two would put an unclassified file in the ordinary
    approve queue."* A freeze is a reviewer, so it may not collapse them either.
    """
    article = _article(world.decisions)
    decisions = tuple(
        dataclasses.replace(
            d, review_policy=BLOCKED_PENDING_USER,
            privacy=PrivacyState(handling_class="unreadable_unclassified", protected=False,
                                 model_eligibility="local_only",
                                 consent_audit_ref=None))
        if d.subject.file_id == article else d
        for d in world.decisions)

    proposal = _freeze(world, decisions, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in decisions})

    assert [(item.file_id, item.reason, item.detail) for item in proposal.held] \
        == [(article, AWAITING_CLASSIFICATION, BLOCKED_PENDING_USER)]
    assert world.conn.execute(
        "SELECT COUNT(*) FROM review_approvals").fetchone()[0] == 0


def test_the_approval_a_freeze_wrote_satisfies_p12s_gate(
        world, reviewable, ids, clock):
    """The seam, checked rather than assumed. P13 produces; P12 enforces.

    `mutation.approval.approval_verdict` is the gate, and until now the only
    thing that reached it was a lambda returning `None`. This reads the row back
    through the same reader `--apply` uses and hands it to the real gate.
    """
    article = _article(reviewable)
    proposal = _freeze(world, reviewable, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in reviewable})
    plan = next(p for p in proposal.plans if p.file_id == article)

    read = approval_reader(world.conn)
    verdict = approval_verdict(plan, read(plan.plan_id))
    assert verdict.satisfied
    assert verdict.refusal_class is None


def test_an_approval_given_under_another_plan_version_satisfies_nothing(
        world, reviewable, ids, clock):
    """§8.8, through the reader rather than around it.

    A re-run mints a new plan version, and the approval the person gave under the
    old one describes a proposal that no longer exists. The gate names the field
    that differs, so a person is told their approval was for a different version
    rather than that it "did not work".
    """
    article = _article(reviewable)
    proposal = _freeze(world, reviewable, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in reviewable})
    plan = next(p for p in proposal.plans if p.file_id == article)
    later = dataclasses.replace(plan, organization_plan_version="plan-two")

    verdict = approval_verdict(later, approval_reader(world.conn)(plan.plan_id))
    assert not verdict.satisfied
    assert verdict.detail["mismatched"] == ("plan_version",)


def test_a_plan_is_not_frozen_when_its_approval_could_not_be_written(
        world, reviewable, ids, clock):
    """Order is load-bearing: approve, then record the plan.

    `record_presentation` commits. A plan recorded before an approval that then
    refused would sit in the approved set as a file every apply run must decline
    -- which reads as a product that keeps failing, and is the state `91` §3.5
    refused for exactly this reason.
    """
    create_review_schema(world.conn)

    def refuse(plan, at):
        raise ApprovalPresentationRequired("nothing recorded what was shown")

    with pytest.raises(ApprovalPresentationRequired):
        freeze(
            world.conn, reviewable, nodes=NODES, legal_destination_ids=LEGAL,
            cross_folder_moves=True, constraints=CONSTRAINTS,
            high_level_folders={"root_documents": world.documents},
            volume_of=lambda path: "vol-main",
            protected_handling_classes=PROTECTED_CLASSES,
            collision_policy=COLLISION_POLICY,
            expiration_state="no expiry configured",
            shown_file_ids=frozenset(
                d.subject.file_id for d in reviewable),
            approve_reviewed=refuse,
            component_version="apply-test", now=clock, mint_id=ids)

    article = _article(reviewable)
    rows = world.conn.execute(
        "SELECT COUNT(*) FROM move_plans WHERE file_id = ?",
        (article,)).fetchone()[0]
    assert rows == 0


def test_a_protected_hold_is_counted_and_not_named(world, ids, clock):
    """The owner ruled on 2026-09-02: protected filenames sit behind a gesture.

    A freeze cannot approve a protected file at all, so it has no claim on the
    name that the ordinary report does not have -- and putting a passport on the
    screen at the moment a person is being asked to approve a batch is the worst
    place for it. Counted, explained, and not silently omitted: the count is on
    the screen and the total above it includes them.
    """
    passport = next(d.subject.file_id for d in world.decisions
                    if d.privacy.protected)
    decisions = tuple(
        dataclasses.replace(d, review_policy=REVIEW_REQUIRED)
        if d.privacy.protected else d
        for d in world.decisions)
    proposal = _freeze(world, decisions, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in decisions})

    text = "\n".join(freeze_lines(
        proposal, names={f: p.name for f, p in world.sources.items()},
        nodes=NODES, apply_command=lambda branch: "cmd",
        apply_everything_command="all"))

    assert world.sources[passport].name == "passport scan.pdf"
    assert "passport scan.pdf" not in text
    assert "1 protected file(s), counted here and not named" in text
    # Whitespace-collapsed, because the sentence is wrapped to the screen and a
    # containment test against the raw text would be measuring the wrap.
    assert ("freezing a proposal is not permission to move it"
            in " ".join(text.split()))


@pytest.mark.xfail(strict=True, reason=(
    "The two sides of this contradiction are both live and neither is wrong on "
    "its own. `privacy.defaults.MORE_REDACTING` makes every §8.4 facet "
    "`redacted` by default, so a fresh install reads `names: redacted`; and "
    "`cli.report` and `apply_run.report.freeze_lines` both print filenames "
    "without consulting the policy at all. So the presentation this freeze "
    "records is HONEST about the policy in force and the screen did something "
    "else. Recording the policy was the right half to keep -- §8.4 makes what "
    "was displayed a privacy-relevant fact, and a record that guessed at the "
    "screen instead of reading the policy would be a worse lie. Fixing the "
    "screen belongs to whoever owns `report()`; when they do, this test PASSES "
    "and the strict marker turns the suite red so they find this record "
    "waiting for them."))
def test_a_screen_that_prints_a_filename_does_not_record_that_names_were_hidden(
        world, reviewable, ids, clock):
    """The redaction policy on the record, against what the person actually read."""
    article = _article(reviewable)
    proposal = _freeze(world, reviewable, ids=ids, clock=clock,
                       shown={d.subject.file_id for d in reviewable})
    plan = next(p for p in proposal.plans if p.file_id == article)
    approval = approvals_for(world.conn, plan_id=plan.plan_id)[0]
    recorded = presented_state(world.conn, approval.presented_state_ref)

    names = {f: p.name for f, p in world.sources.items()}
    text = "\n".join(freeze_lines(
        proposal, names=names, nodes=NODES,
        apply_command=lambda branch: "cmd", apply_everything_command="all"))

    if recorded.redaction_policy["names"] == "redacted":
        on_screen = [name for name in names.values() if name in text]
        assert on_screen == [], (
            f"the recorded presentation says names were redacted, and the "
            f"screen printed {on_screen}")

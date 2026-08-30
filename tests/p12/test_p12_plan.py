"""§8.3's move plan: the thirteen precondition fields, ten carried, no gaps.

`00`:158-170 lists the thirteen by name. The first test below asserts they are
those thirteen in that order; the negative twin asserts the freeze guarantee --
that a node outside `legal_destination_ids` produces no plan at all.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.files_table import record_file
from placement.fixtures import GOLDEN_DECISIONS
from placement.records import Ask, Destination, ReturnTarget, Subject
from placement.vocabulary import (
    BLOCKED_PENDING_USER, CONFIRMED_DOMAIN_GROUP, LEAVE_IN_PLACE_DISPOSITION,
    NO_SUPPORTED_DESTINATION, PLACE, PROTECTED, RESIDUAL, RESIDUAL_ROLE,
    REVIEW_ONLY, REVIEW_REQUIRED,
)

from mutation import vocabulary as v
from mutation.names import NameUnresolvable
from mutation.plan import (
    PLAN_CARRIED_FIELDS, PLAN_PRECONDITION_FIELDS, IncompletePlan, MovePlan,
    PlanRefused, build_plan, current_plan, plans_in_group, record_plan,
    supersede_plan,
)

from p12.conftest import (
    CONSTRAINTS, FIXTURE_NODES, FOLDING_CONSTRAINTS, LEGAL_DESTINATIONS,
    PROTECTED_CLASSES, fixture_node,
)


def _volume(path: Path) -> str:
    """The fixture volume oracle. One authority for both ends of the move, so
    `expected_source_volume` and `expected_destination_volume` are comparable."""
    return "vol-main"


@pytest.fixture()
def source(landscape):
    path = landscape["root_documents"] / "Inbox" / "Syllabus.pdf"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"PHYS1401 syllabus")
    return path


@pytest.fixture()
def file_id(p12_conn, source: Path):
    stat = source.stat()
    return record_file(
        p12_conn, source, filename="Syllabus.pdf",
        normalized_filename="syllabus.pdf", extension=".pdf",
        observed_size=stat.st_size, observed_timestamps=str(stat.st_mtime),
        parent_folder_context="Inbox", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)


@pytest.fixture()
def decision(p12_conn, file_id):
    golden = next(item for item in GOLDEN_DECISIONS if item.outcome == PLACE)
    content_hash = p12_conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (file_id,)).fetchone()[0]
    return dataclasses.replace(
        golden,
        destination=Destination(node_id="n-phys", node_role="ordinary"),
        subject=Subject(kind="file", file_id=file_id, content_hash=content_hash,
                        group_id=None, member_file_ids=()))


def _build(p12_conn, decision, landscape, ids, *, nodes=FIXTURE_NODES, legal=None,
           cross_folder_moves=True, collision_policy=None,
           constraints=CONSTRAINTS):
    return build_plan(
        p12_conn, decision, nodes=nodes,
        legal_destination_ids=(
            LEGAL_DESTINATIONS if legal is None else legal),
        cross_folder_moves=cross_folder_moves, constraints=constraints,
        high_level_folders=landscape, volume_of=_volume,
        protected_handling_classes=PROTECTED_CLASSES,
        collision_policy=(collision_policy
                          or v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX),
        expiration_state="no expiry configured",
        now=lambda: "2026-08-29T00:00:00Z", mint_id=ids)


# ---------------------------------------------------------------------------
# The pair Wave D1 names.
# ---------------------------------------------------------------------------


def test_a_plan_carries_every_field_00_155_names(p12_conn, decision, landscape,
                                                 ids, source):
    """`00`:158-170's thirteen, by name and in `00`'s order, all populated.

    Asserted three ways, because each catches a different failure: the tuple is
    `00`'s list verbatim; the dataclass has exactly those thirteen plus the ten
    Contract out §1 carries and nothing else; and every one of the thirteen is
    non-empty on a plan built from a real decision over a real file.
    """
    assert PLAN_PRECONDITION_FIELDS == (
        "plan_id", "file_id", "expected_content_hash", "expected_source_path",
        "expected_source_volume", "expected_size_and_modification_state",
        "requested_destination_node", "resolved_destination_path",
        "collision_policy", "sensitivity_and_consent_state",
        "reason_and_evidence_summary", "required_review_policy",
        "creation_time_and_expiration_state")
    assert len(PLAN_PRECONDITION_FIELDS) == len(set(PLAN_PRECONDITION_FIELDS))
    names = {field.name for field in dataclasses.fields(MovePlan)}
    assert set(PLAN_PRECONDITION_FIELDS) | set(PLAN_CARRIED_FIELDS) == names

    built = _build(p12_conn, decision, landscape, ids)
    assert built is not None
    plan, resolution = built
    for name in PLAN_PRECONDITION_FIELDS:
        assert getattr(plan, name), f"{name} is empty on a complete plan"

    assert plan.expected_source_path == str(source)
    assert plan.expected_source_volume == "vol-main"
    assert plan.requested_destination_node == "n-phys"
    assert plan.resolved_destination_path == str(
        landscape["root_documents"] / "Coursework" / "PHYS1401" / "Syllabus.pdf")
    assert plan.intended_display_name == "Syllabus.pdf"
    assert plan.filesystem_safe_name == "Syllabus.pdf"
    assert plan.organization_plan_version == decision.plan_version
    assert plan.placement_decision_reference == decision.decision_id
    assert plan.path_resolution_reference == resolution.resolution_id
    assert plan.destination_root_anchor == "root_documents"
    assert plan.source_high_level_folder == "root_documents"
    assert plan.cross_folder_movement_permission is True
    assert json.loads(plan.expected_size_and_modification_state)["observed_size"] \
        == source.stat().st_size
    assert json.loads(plan.creation_time_and_expiration_state)["expiration_state"] \
        == "no expiry configured"
    # A plan is a proposal. Creating one mutates nothing.
    assert not Path(plan.resolved_destination_path).exists()
    assert not Path(plan.resolved_destination_path).parent.exists()


def test_a_plan_built_for_a_node_outside_legal_destination_ids_is_refused(
        p12_conn, decision, landscape, ids):
    """The negative twin. §6.12: *"No system component may invent a new
    destination after freeze"*, and P10 states the freeze guarantee for P12 as
    well as P11 -- the legal set is exactly `{node_id : accepts_placement}`.

    Both halves are asserted, because a guard that refuses every node is as
    useless as one that refuses none: the same decision builds the moment the
    node is back in the legal set.
    """
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, legal=frozenset({"n-course"}))
    assert excinfo.value.refusal_class == v.NODE_REFUSES_PLACEMENT
    assert excinfo.value.detail["node_id"] == "n-phys"
    assert p12_conn.execute("SELECT COUNT(*) FROM move_plans").fetchone()[0] == 0

    assert _build(p12_conn, decision, landscape, ids,
                  legal=LEGAL_DESTINATIONS) is not None


# ---------------------------------------------------------------------------
# Done-means 2 — one missing field rejects at construction.
# ---------------------------------------------------------------------------


def test_a_plan_missing_one_of_the_thirteen_is_rejected_at_construction(
        p12_conn, decision, landscape, ids):
    plan, _ = _build(p12_conn, decision, landscape, ids)
    for name in PLAN_PRECONDITION_FIELDS:
        with pytest.raises(IncompletePlan) as excinfo:
            dataclasses.replace(plan, **{name: ""})
        assert name in str(excinfo.value)


def test_the_two_legitimately_absent_carried_fields_are_not_forced(
        p12_conn, decision, landscape, ids):
    """`group_plan_reference` is None for a file belonging to no group and
    `source_high_level_folder` is None for a source under none of the §1.1
    folders the person named. Forcing either would make a real state unstorable
    -- and F11's refusal already handles the second, at resolution, where the
    permission is enforced."""
    plan, _ = _build(p12_conn, decision, landscape, ids)
    assert dataclasses.replace(plan, group_plan_reference=None,
                               source_high_level_folder=None)


def test_cross_folder_movement_permission_is_a_bool_never_a_blank(
        p12_conn, decision, landscape, ids):
    plan, _ = _build(p12_conn, decision, landscape, ids)
    for absent in (None, "", "yes"):
        with pytest.raises(IncompletePlan):
            dataclasses.replace(plan, cross_folder_movement_permission=absent)


def test_the_collision_policy_is_one_of_the_four_user_approved_behaviours(
        p12_conn, decision, landscape, ids):
    plan, _ = _build(p12_conn, decision, landscape, ids)
    with pytest.raises(v.OutOfVocabulary):
        dataclasses.replace(plan, collision_policy="overwrite_the_old_one")


# ---------------------------------------------------------------------------
# Done-means 18 — the six non-`place` outcomes produce NO plan, not a refusal.
# ---------------------------------------------------------------------------


#: Each non-`place` outcome carries its own companion field, and P11's record
#: refuses one without it -- `return_to_placement` also belongs to the §7.9
#: residual loop and so carries that path's origin stage and context. Built
#: WELL-FORMED here rather than blanked, so the test proves P12 ignores a real
#: decision of each kind rather than a malformed one.
_NON_PLACE = {
    "mark_review_later": {},
    "leave_in_place": {},
    "mark_state": {"marked_state": PROTECTED},
    "ask_user": {"ask": Ask(question="Where should this live?",
                            options=("Coursework", "Career"))},
    "abstain": {"abstention_reason": NO_SUPPORTED_DESTINATION},
    "return_to_placement": {
        "return_target": ReturnTarget(kind=CONFIRMED_DOMAIN_GROUP, id="g-1")},
}


def _non_place(decision, outcome):
    """One well-formed decision per non-`place` outcome."""
    if outcome == "return_to_placement":
        base = next(item for item in GOLDEN_DECISIONS
                    if item.origin_stage == RESIDUAL)
    else:
        base = dataclasses.replace(decision, residual=None,
                                   origin_stage=decision.origin_stage)
    blanked = {"destination": None, "return_target": None, "marked_state": None,
               "ask": None, "abstention_reason": None}
    return dataclasses.replace(base, outcome=outcome,
                               **{**blanked, **_NON_PLACE[outcome]})


@pytest.mark.parametrize("outcome", sorted(_NON_PLACE))
def test_each_non_place_outcome_produces_no_plan_record_at_all(
        p12_conn, decision, landscape, ids, outcome):
    """`None`, not a refusal. `abstain` is a SUCCESSFUL outcome (§6.10), and
    recording any of the six as a P12 refusal would make the apply run's refused
    count describe decisions that were never asked to move."""
    other = _non_place(decision, outcome)
    assert _build(p12_conn, other, landscape, ids) is None
    assert p12_conn.execute("SELECT COUNT(*) FROM move_plans").fetchone()[0] == 0
    assert p12_conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = ?",
        (v.PLANNED_MOVE,)).fetchone()[0] == 0
    assert p12_conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type = ?",
        (v.REFUSED_MOVE,)).fetchone()[0] == 0


def test_a_node_absent_from_the_frozen_tree_refuses_with_its_own_class(
        p12_conn, decision, landscape, ids):
    """Absence from the tree and refusal by the tree are two different answers
    to the person, so they are two different classes."""
    elsewhere = dataclasses.replace(
        decision,
        destination=Destination(node_id="n-invented", node_role="ordinary"))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, elsewhere, landscape, ids)
    assert excinfo.value.refusal_class == v.NODE_NOT_IN_FROZEN_TREE


def test_a_node_that_refuses_placement_refuses(p12_conn, decision, landscape, ids):
    nodes = (fixture_node("n-course", "Coursework", None),
             fixture_node("n-phys", "PHYS1401", "n-course", node_type="ignored",
                          accepts_placement=False))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, nodes=nodes,
               legal=frozenset({"n-course", "n-phys"}))
    assert excinfo.value.refusal_class == v.NODE_REFUSES_PLACEMENT
    assert excinfo.value.detail["accepts_placement"] is False


@pytest.mark.parametrize("disposition", [REVIEW_ONLY, LEAVE_IN_PLACE_DISPOSITION])
def test_a_review_only_or_leave_in_place_residual_refuses(
        p12_conn, decision, landscape, ids, disposition):
    nodes = (fixture_node("n-course", "Coursework", None),
             fixture_node("n-phys", "PHYS1401", "n-course",
                          node_role=RESIDUAL_ROLE, disposition=disposition))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, nodes=nodes)
    assert excinfo.value.refusal_class == v.NODE_REFUSES_PLACEMENT
    assert excinfo.value.detail["disposition"] == disposition


def test_a_physical_destination_residual_does_not_refuse(p12_conn, decision,
                                                         landscape, ids):
    nodes = (fixture_node("n-course", "Coursework", None),
             fixture_node("n-phys", "PHYS1401", "n-course",
                          node_role=RESIDUAL_ROLE,
                          disposition="physical-destination"))
    plan, _ = _build(p12_conn, decision, landscape, ids, nodes=nodes)
    assert plan.requested_destination_node == "n-phys"


# ---------------------------------------------------------------------------
# Done-means 19's refusal half, and the resolution refusals that reach the plan.
# ---------------------------------------------------------------------------


def test_a_cross_folder_move_refuses_when_the_permission_is_off_and_builds_when_on(
        p12_conn, decision, landscape, ids, source):
    moved = landscape["root_downloads"] / "Syllabus.pdf"
    source.rename(moved)
    p12_conn.execute("UPDATE files SET current_path = ?", (str(moved),))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, cross_folder_moves=False)
    assert excinfo.value.refusal_class == v.CROSS_FOLDER_NOT_PERMITTED
    assert excinfo.value.detail["source_high_level_folder"] == "root_downloads"
    plan, _ = _build(p12_conn, decision, landscape, ids, cross_folder_moves=True)
    assert plan.source_high_level_folder == "root_downloads"
    assert plan.cross_folder_movement_permission is True


def test_two_sibling_labels_colliding_refuse_at_construction(
        p12_conn, decision, landscape, ids):
    nodes = (fixture_node("n-course", "Coursework", None),
             fixture_node("n-phys", "PHYS1401", "n-course"),
             fixture_node("n-phys2", "phys1401", "n-course", ordinal=1))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, nodes=nodes,
               legal=frozenset({"n-course", "n-phys", "n-phys2"}),
               constraints=FOLDING_CONSTRAINTS)
    assert excinfo.value.refusal_class == v.NODE_PATH_COLLISION


def test_a_protected_label_refuses_before_a_plan_exists(p12_conn, decision,
                                                        landscape, ids):
    """C4's guard reaches plan construction: the passport-number label from
    `69` §3 blocker 3 never becomes a plan's `resolved_destination_path`."""
    nodes = (fixture_node("n-course", "Coursework", None),
             fixture_node("n-phys", "X1234567", "n-course",
                          handling_class="highly_sensitive_credential_bearing"))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, decision, landscape, ids, nodes=nodes)
    assert excinfo.value.refusal_class == v.PROTECTED_WITHOUT_POLICY
    assert "X1234567" not in str(excinfo.value.detail)


def test_a_decision_naming_a_file_p1_has_no_record_of_refuses(
        p12_conn, decision, landscape, ids):
    unknown = dataclasses.replace(
        decision,
        subject=Subject(kind="file", file_id="f-nobody-scanned",
                        content_hash="0" * 64, group_id=None,
                        member_file_ids=()))
    with pytest.raises(PlanRefused) as excinfo:
        _build(p12_conn, unknown, landscape, ids)
    assert excinfo.value.refusal_class == v.SOURCE_OR_DESTINATION_UNAVAILABLE


def test_an_unresolvable_name_propagates_rather_than_wearing_a_refusal_class(
        p12_conn, decision, landscape, ids):
    """F3, restated as a test. Contract out §5 has ten refusal classes and none
    of them means *"no safe name exists"*. Mapping it onto `node_path_collision`
    would tell the person a lie, and minting an eleventh would be P12 authoring
    the SPEC. So `NameUnresolvable` propagates and the gap stays visible."""
    directory = landscape["root_documents"] / "Coursework" / "PHYS1401"
    budget = len(str(directory).encode()) + 1
    tight = dataclasses.replace(CONSTRAINTS, max_path_bytes=budget,
                                max_component_bytes=budget)
    with pytest.raises(NameUnresolvable):
        _build(p12_conn, decision, landscape, ids, constraints=tight)


# ---------------------------------------------------------------------------
# Done-means 21's "produces a plan, is not withheld" half.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("policy", [REVIEW_REQUIRED, BLOCKED_PENDING_USER])
def test_a_decision_demanding_review_still_produces_a_plan(
        p12_conn, decision, landscape, ids, policy):
    """§8.3 fixes the order: create a plan, THEN show it where policy requires
    review. Refusing to build would leave the review step with nothing to show
    and P13 with nothing to render. What P12 refuses is to EXECUTE it."""
    needing = dataclasses.replace(decision, review_policy=policy)
    plan, _ = _build(p12_conn, needing, landscape, ids)
    assert plan.required_review_policy == policy


# ---------------------------------------------------------------------------
# Recording, group expansion, and supersession.
# ---------------------------------------------------------------------------


def test_recording_a_plan_appends_one_planned_move_event_and_round_trips(
        p12_conn, decision, landscape, ids):
    plan, resolution = _build(p12_conn, decision, landscape, ids)
    record_plan(p12_conn, plan, resolution, created_at="2026-08-29T00:00:00Z",
                component_version="p12-test")
    assert current_plan(p12_conn, plan.plan_id) == plan
    rows = p12_conn.execute(
        "SELECT subsystem, file_id, old_path, new_path FROM events "
        "WHERE event_type = ?", (v.PLANNED_MOVE,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == v.SUBSYSTEM
    assert rows[0]["file_id"] == plan.file_id
    assert rows[0]["old_path"] == plan.expected_source_path
    assert rows[0]["new_path"] == plan.resolved_destination_path


def test_a_recorded_plan_cannot_be_overwritten(p12_conn, decision, landscape, ids):
    plan, resolution = _build(p12_conn, decision, landscape, ids)
    record_plan(p12_conn, plan, resolution, created_at="2026-08-29T00:00:00Z",
                component_version="p12-test")
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute("UPDATE move_plans SET payload = ?", ("{}",))
    with pytest.raises(sqlite3.IntegrityError):
        p12_conn.execute("DELETE FROM move_plans")


def test_a_group_expands_one_to_one_and_every_member_carries_the_group_id(
        p12_conn, decision, landscape, ids, source, file_id):
    """§6.8: one move plan per member decision, each with its own preconditions
    and its own journal entry, all carrying `group_plan_id` so the set is
    presented as one coherent group plan rather than several unrelated moves."""
    second = source.parent / "Homework.pdf"
    second.write_bytes(b"PHYS1401 homework")
    stat = second.stat()
    second_id = record_file(
        p12_conn, second, filename="Homework.pdf",
        normalized_filename="homework.pdf", extension=".pdf",
        observed_size=stat.st_size, observed_timestamps=str(stat.st_mtime),
        parent_folder_context="Inbox", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    second_hash = p12_conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?",
        (second_id,)).fetchone()[0]
    members = (
        dataclasses.replace(decision, decision_id="d-1", group_plan_id="gp-1"),
        dataclasses.replace(
            decision, decision_id="d-2", group_plan_id="gp-1",
            subject=Subject(kind="file", file_id=second_id,
                            content_hash=second_hash, group_id="g-1",
                            member_file_ids=())),
    )
    for member in members:
        plan, resolution = _build(p12_conn, member, landscape, ids)
        record_plan(p12_conn, plan, resolution,
                    created_at="2026-08-29T00:00:00Z",
                    component_version="p12-test")
    group = plans_in_group(p12_conn, "gp-1")
    assert len(group) == len(members)
    assert {item.file_id for item in group} == {file_id, second_id}
    assert len({item.plan_id for item in group}) == len(members)


def test_a_refreshed_plan_supersedes_the_stale_one_and_the_old_one_is_retained(
        p12_conn, decision, landscape, ids):
    """§8.2: the stale plan is never edited in place. A refreshed plan is a NEW
    record, and the old one keeps its trigger so it can say what made it stale."""
    old, old_resolution = _build(p12_conn, decision, landscape, ids)
    record_plan(p12_conn, old, old_resolution, created_at="2026-08-29T00:00:00Z",
                component_version="p12-test")
    new, new_resolution = _build(p12_conn, decision, landscape, ids)
    supersede_plan(p12_conn, old.plan_id, new, new_resolution,
                   reason=f"stale:{v.CONTENT_HASH_DIFFERS}",
                   created_at="2026-08-29T00:05:00Z",
                   component_version="p12-test")
    assert current_plan(p12_conn, old.plan_id) is None
    assert current_plan(p12_conn, new.plan_id) == new
    row = p12_conn.execute(
        "SELECT superseded_by, supersede_reason FROM move_plans WHERE plan_id = ?",
        (old.plan_id,)).fetchone()
    assert row["superseded_by"] is not None
    assert row["supersede_reason"] == f"stale:{v.CONTENT_HASH_DIFFERS}"

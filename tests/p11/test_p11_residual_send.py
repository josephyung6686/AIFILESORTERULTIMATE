"""§7.6's `send_to_approved_node`, carried out with no model at all.

Of §7.6's four set choices only `review_with_model_against_approved_residual_folders`
needs a model. `send_to_approved_node` is *"already a decision and needs no
interpretation"* (`placement.residual.model_calls_permitted`), so a deployment that
wires no model can still act on it -- and until this file existed, it did not:
`review_residual_sets` skipped every choice but the model one, and a person who had
enabled a residual area was told their files were "held for review" with nothing to
type in reply.

Two refusals are asserted by their twins rather than by their message:

* a set answer belongs to the plan version it was given in (SPEC "Plan versioning":
  residual set decisions *"belong to a plan version, not to the shared evidence
  database"*), so run 1's answer places nothing in run 2; and
* a protected set refuses a send exactly as it refuses a review. A send opens no
  file, and it still refuses -- moving passports and credentials wholesale into a
  residual area handles the material without looking at it, which is not the same
  as leaving it alone.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from llm_harness.budgets import create_budget_schema
from llm_harness.schema import create_llm_schema
from privacy.classification import ClassificationRecord, observation_key
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy

from placement import vocabulary as v
from placement.config import CEILINGS, placement_limits
from placement.index import build_destination_index
from placement.records import MatchingFact, Subject
from placement.residual import (
    ProtectedSetNotReadable, ResidualSetDecision, SetDecisionRequired,
    record_set_decision, require_set_decision,
)
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE

#: The residual node P10 froze into the fixture tree: `node_role = residual`,
#: `disposition = review-only`, and the person's own existing folder.
REVIEW_LATER_ID = "n-review-later"
REVIEW_LATER_LABEL = "To Sort"

SUBJECT = Subject(kind=v.FILE, file_id="f1", content_hash="h1", group_id=None,
                  member_file_ids=())


OBS = observation_key(content_hash="h1", extractor_name="fixture",
                      locator="page-1", raw_value="f1")


def _classify(conn, *, file_id="f1", content_hash="h1"):
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis="detector", evidence_refs=(OBS,), reliability_state="direct",
        observed_at=FIXED_CLOCK))


def _policy(conn, *, plan_version="plan-1"):
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version=plan_version,
        set_at=FIXED_CLOCK),
        component_version="P11-test", user_id="u1",
        reason="skeleton fixture policy")


@pytest.fixture()
def skeleton(p11_conn):
    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    return p11_conn


def _partition(file_ids, *, protected=False, label="Not yet placed"):
    if not file_ids:
        return ()
    return ({"label": label, "member_file_ids": tuple(file_ids),
             "representative_examples": tuple(file_ids[:1]),
             "file_type_distribution": (("pdf", len(file_ids)),),
             "age_range": ("2026-01-01", "2026-08-01"),
             "evidence_availability": "none", "sensitivity_status": "public_low",
             "protected": protected, "weak_graph_neighbours": (),
             "reason_not_placed": "no destination in this tree matched them"},)


def _inputs(conn, **overrides):
    from placement.config import SupportPolicy
    from placement.pipeline import PipelineInputs

    values = dict(
        plan_version="plan-1", tree=FROZEN_TREE,
        policy=SupportPolicy(policy_id="s", support_scale_max=1.0,
                             minimum_support_threshold=0.5, margin_threshold=0.2),
        limits=placement_limits(conn), partition=_partition,
        ask_or_abstain=lambda ids: v.ABSTAIN, max_return_cycles=1,
        gate=None, model_client=None, prompt=None, call_dependencies=None,
        model_call_request=None, chosen_node_of=None, residual_action_of=None,
        sensitivity_policy=None, p2=None)
    values.update(overrides)
    return PipelineInputs(**values)


def _evidence(**overrides):
    values = dict(
        facts=(), evidence_items=(), group_ids=(), curated_folder_labels=(),
        semantic_neighbours=(), related_files=(), entity_frequency={},
        generic_entity_frequency=200)
    values.update(overrides)
    return values


def _corpus(conn, **overrides):
    from placement.pipeline import run_corpus

    kwargs = dict(subjects=(SUBJECT,), group_ids=(), inputs=_inputs(conn),
                  evidence_for=lambda file_id: _evidence(),
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    kwargs.update(overrides)
    return run_corpus(conn, **kwargs)


def _act(conn, result, sends, **overrides):
    from placement.pipeline import act_on_residual_sets

    kwargs = dict(result=result, inputs=_inputs(conn), sends=sends,
                  evidence_for=lambda file_id: _evidence(),
                  component_version="P11-test", observed_at=FIXED_CLOCK,
                  user_id="u1")
    kwargs.update(overrides)
    return act_on_residual_sets(conn, **kwargs)


def _model_sites(monkeypatch):
    """Every call site the run reached, so "no model call" is measured and not
    inferred from the absence of a client."""
    import placement.pipeline as pipeline

    seen = []

    def _fake_call(conn, request, **kwargs):
        seen.append(request.call_site)
        raise AssertionError("no model call may be issued for a sent set")

    monkeypatch.setattr(pipeline, "call_placement", _fake_call)
    return seen


# --- the thing the product could not do -------------------------------------------

def test_a_set_the_person_sent_to_an_approved_node_is_placed_there(skeleton,
                                                                   monkeypatch):
    seen = _model_sites(monkeypatch)
    result = _corpus(skeleton)
    assert result.residual_sets, "the file must reach §7 for this to test anything"
    assert all(d.outcome != v.PLACE for d in result.decisions)

    after = _act(skeleton, result, {"Not yet placed": REVIEW_LATER_LABEL})

    placed = [d for d in after.decisions if d.outcome == v.PLACE]
    assert [d.subject.file_id for d in placed] == ["f1"]
    assert placed[0].destination.node_id == REVIEW_LATER_ID
    assert placed[0].destination.node_role == v.RESIDUAL_ROLE
    assert seen == [], "send_to_approved_node needs no interpretation"


def test_the_sent_files_are_no_longer_reported_as_unplaced(skeleton):
    result = _corpus(skeleton)
    assert result.unplaced_file_ids == ("f1",)
    after = _act(skeleton, result, {"Not yet placed": REVIEW_LATER_LABEL})
    assert after.unplaced_file_ids == ()
    # The set itself is NOT dropped. It was surfaced and counted, and a review
    # screen that deletes a set once it is acted on cannot show what happened.
    assert after.residual_sets == result.residual_sets


def test_the_set_answer_and_the_decision_are_both_recorded(skeleton):
    result = _corpus(skeleton)
    _act(skeleton, result, {"Not yet placed": REVIEW_LATER_LABEL})
    row = skeleton.execute(
        "SELECT choice, node_id FROM residual_set_decisions "
        "WHERE superseded_by IS NULL").fetchone()
    assert row["choice"] == v.SEND_TO_APPROVED_NODE
    assert row["node_id"] == REVIEW_LATER_ID
    events = {r["event_type"] for r in skeleton.execute(
        "SELECT event_type FROM events")}
    assert v.RESIDUAL_SET_DECIDED in events


def test_the_record_says_the_person_decided_this_and_not_a_model(skeleton):
    result = _corpus(skeleton)
    after = _act(skeleton, result, {"Not yet placed": REVIEW_LATER_LABEL})
    placed = [d for d in after.decisions if d.outcome == v.PLACE][0]
    assert placed.residual.set_decision == v.SEND_TO_APPROVED_NODE
    # The explanation a person reads must not credit a judgement nobody made.
    assert "no model was asked" in placed.explanation
    assert REVIEW_LATER_LABEL in placed.explanation
    assert "returned" not in placed.explanation


# --- twin 1: an answer belongs to the version it was given in ---------------------

def test_a_set_answer_is_not_honoured_against_another_plan_version(skeleton):
    """SPEC "Plan versioning": residual set decisions belong to a plan version.

    Sabotage twin: drop `plan_version = ?` from `require_set_decision`'s query and
    this passes, which is run 1's spend-and-destination answer being applied to
    sets run 2's user never saw.
    """
    result = _corpus(skeleton)
    set_id = result.residual_sets[0].set_id
    record_set_decision(
        skeleton,
        ResidualSetDecision(set_id=set_id, plan_version="plan-1",
                            choice=v.SEND_TO_APPROVED_NODE,
                            node_id=REVIEW_LATER_ID, decided_at=FIXED_CLOCK),
        component_version="P11-test", observed_at=FIXED_CLOCK, user_id="u1")

    assert require_set_decision(skeleton, plan_version="plan-1", set_id=set_id)
    with pytest.raises(SetDecisionRequired):
        require_set_decision(skeleton, plan_version="plan-2", set_id=set_id)


def test_a_second_run_does_not_inherit_the_first_runs_set_answer(skeleton):
    """The same twin at the product's scale, over two real plan versions."""
    from p11.p10_fixtures import next_version

    first = _corpus(skeleton)
    _act(skeleton, first, {"Not yet placed": REVIEW_LATER_LABEL})

    second_tree = next_version(FROZEN_TREE, plan_version_id="plan-2",
                               suffix="-2")
    _policy(skeleton, plan_version="plan-2")
    build_destination_index(skeleton, second_tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    again = _corpus(skeleton,
                    inputs=_inputs(skeleton, plan_version="plan-2",
                                   tree=second_tree))
    from placement.pipeline import review_residual_sets

    assert review_residual_sets(
        skeleton, result=again, inputs=_inputs(skeleton, plan_version="plan-2",
                                               tree=second_tree),
        evidence_for=lambda file_id: _evidence(),
        component_version="P11-test", observed_at=FIXED_CLOCK) == ()


# --- twin 2: protected refuses whatever the person chose --------------------------

def test_a_protected_set_refuses_a_send_exactly_as_it_refuses_a_review(skeleton):
    protected = lambda ids: _partition(ids, protected=True, label="Reports")
    result = _corpus(skeleton, inputs=_inputs(skeleton, partition=protected))
    assert result.residual_sets[0].protected is True
    with pytest.raises(ProtectedSetNotReadable):
        _act(skeleton, result, {"Reports": REVIEW_LATER_LABEL},
             inputs=_inputs(skeleton, partition=protected))
    # Marked and COUNTED: the refusal did not delete the set or its count.
    assert result.residual_sets[0].file_count == 1
    assert result.residual_sets[0].reason_not_placed


def test_an_unprotected_set_with_the_same_answer_is_placed(skeleton):
    """The discriminating twin: the refusal above measures the protection and not
    the send."""
    result = _corpus(skeleton)
    after = _act(skeleton, result, {"Not yet placed": REVIEW_LATER_LABEL})
    assert [d.outcome for d in after.decisions if d.outcome == v.PLACE] == [v.PLACE]


# --- refusals that say what to type ------------------------------------------------

def test_a_review_set_this_run_did_not_surface_is_refused_by_name(skeleton):
    from placement.pipeline import ResidualSendRefused

    result = _corpus(skeleton)
    with pytest.raises(ResidualSendRefused) as refusal:
        _act(skeleton, result, {"Screenshots": REVIEW_LATER_LABEL})
    assert "Not yet placed" in str(refusal.value)


def test_a_residual_area_this_plan_does_not_have_is_refused_by_name(skeleton):
    from placement.pipeline import ResidualSendRefused

    result = _corpus(skeleton)
    with pytest.raises(ResidualSendRefused) as refusal:
        _act(skeleton, result, {"Not yet placed": "Reading Inbox"})
    assert REVIEW_LATER_LABEL in str(refusal.value)


def test_an_ordinary_folder_is_not_a_residual_area(skeleton):
    """§7.6's `send_to_approved_node` names an approved RESIDUAL destination.

    `Academics` is a legal node of this tree and is not one, so naming it is
    refused rather than quietly filing every unplaced file under a domain branch.
    """
    from placement.pipeline import ResidualSendRefused

    result = _corpus(skeleton)
    with pytest.raises(ResidualSendRefused):
        _act(skeleton, result, {"Not yet placed": "Academics"})


def test_a_set_nobody_answered_is_left_alone(skeleton):
    """Surfaced-and-undecided stays the ordinary state of the review screen."""
    result = _corpus(skeleton)
    after = _act(skeleton, result, {})
    assert after is result


def test_a_sent_set_never_makes_a_file_movable_without_a_look(p11_conn):
    """A set answer names a destination; it does not approve the moves.

    §7.6 lets the person say where a whole set goes before anything has looked at
    the individual files, so nothing in that answer may clear §6.11's review
    policy: every one of these decisions is a proposal a person still confirms.
    A send that produced `auto_eligible` records would turn one sentence typed at
    a summary screen into files moving on disk unseen.

    The destination here is a residual area whose disposition DOES move files, so
    the assertion is not merely re-measuring the review-only node in the shared
    fixture, which would refuse anything. What remains is defended twice over --
    `_flat_two_condition`'s `requires_review` and §6.6's rule that only a unique
    direct match passes unreviewed -- and sabotaging EITHER one alone leaves this
    passing. Both had to be turned off together to make it fail, which is the
    property being asserted: no single line here is the whole guard.
    """
    from dataclasses import replace

    from p11.p10_fixtures import FREEZE_RECORD, NODES

    physical = tuple(
        replace(node, disposition=v.PHYSICAL_DESTINATION)
        if node.node_id == REVIEW_LATER_ID else node for node in NODES)
    tree = replace(FROZEN_TREE, nodes=physical, freeze_record=FREEZE_RECORD)

    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, tree, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    result = _corpus(p11_conn, inputs=_inputs(p11_conn, tree=tree))
    after = _act(p11_conn, result, {"Not yet placed": REVIEW_LATER_LABEL},
                 inputs=_inputs(p11_conn, tree=tree))
    placed = [d for d in after.decisions if d.outcome == v.PLACE]
    assert placed
    assert all(d.review_policy != v.AUTO_ELIGIBLE for d in placed)

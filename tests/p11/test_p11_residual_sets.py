"""§7.1's ordering and §7.6's spend gate, both enforced by refusal."""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits
from placement.residual import (
    ModelCallNotAuthorised, PlacementPassIncomplete, ProtectedSetNotReadable,
    ResidualPartitionRequired, ResidualSet, ResidualSetDecision,
    SetDecisionRequired, model_calls_permitted, record_set_decision,
    require_model_call_permitted, require_set_decision, surface_residual_sets,
)
from p11.conftest import FIXED_CLOCK

LIMITS = PlacementLimits(
    max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
    max_candidate_cluster_size=6, max_residual_files_per_batch=2,
    max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
    max_cost_per_scan=5,
)
UNPLACED = ("f-gate", "f-receipt", "f-clip")


def _group(label, member_file_ids, **overrides):
    values = dict(
        label=label, member_file_ids=tuple(member_file_ids),
        representative_examples=tuple(member_file_ids[:1]),
        file_type_distribution=(("png", len(member_file_ids)),),
        age_range=("2026-01-01", "2026-08-01"),
        evidence_availability="ocr_present", sensitivity_status="public_low",
        protected=False, weak_graph_neighbours=(),
        reason_not_placed="no direct fact reached any legal destination")
    values.update(overrides)
    return values


def _partition(file_ids):
    return (_group("Screenshots with no association", tuple(file_ids)),)


def _surface(conn, **overrides):
    values = dict(plan_version="plan-1", unplaced=UNPLACED, partition=_partition,
                  limits=LIMITS, placement_pass_complete=True,
                  component_version="P11-test", observed_at=FIXED_CLOCK)
    values.update(overrides)
    return surface_residual_sets(conn, **values)


def _decide(conn, set_id, choice, node_id=None, plan_version="plan-1"):
    decision = ResidualSetDecision(set_id=set_id, plan_version=plan_version,
                                   choice=choice, node_id=node_id,
                                   decided_at=FIXED_CLOCK)
    record_set_decision(conn, decision, component_version="P11-test",
                        observed_at=FIXED_CLOCK, user_id="u1")
    return decision


# --- §7.1: second stage, and only second ------------------------------------------

def test_no_set_is_surfaced_before_the_placement_pass_completes(p11_conn):
    with pytest.raises(PlacementPassIncomplete):
        _surface(p11_conn, placement_pass_complete=False)
    # The negative twin: the SAME call with the pass complete surfaces sets and
    # writes rows, so the refusal above is about the ordering and not about the
    # arguments being unusable.
    assert _surface(p11_conn)
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM residual_sets").fetchone()["c"] == 2


def test_a_refused_surfacing_writes_no_row_and_no_event(p11_conn):
    with pytest.raises(PlacementPassIncomplete):
        _surface(p11_conn, placement_pass_complete=False)
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM residual_sets").fetchone()["c"] == 0
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM events WHERE event_type = ?",
        (v.RESIDUAL_SET_SURFACED,)).fetchone()["c"] == 0


# --- §7.5: what a set shows ---------------------------------------------------------

def test_a_set_carries_every_field_75_names(p11_conn):
    sets = _surface(p11_conn)
    only = sets[0]
    assert isinstance(only, ResidualSet)
    assert only.reason_not_placed
    assert only.representative_examples
    assert only.file_type_distribution
    assert only.age_range == ("2026-01-01", "2026-08-01")
    assert only.evidence_availability == "ocr_present"
    assert only.sensitivity_status == "public_low"
    assert only.weak_graph_neighbours == ()
    assert only.protected is False


def test_a_set_with_no_reason_is_a_pile_and_is_refused():
    with pytest.raises(ValueError):
        ResidualSet(set_id="s", plan_version="plan-1", label="l", file_count=1,
                    representative_examples=(), file_type_distribution=(),
                    age_range=("a", "b"), evidence_availability="none",
                    sensitivity_status="public_low", protected=False,
                    weak_graph_neighbours=(), reason_not_placed="",
                    member_file_ids=("f",))


def test_a_count_that_disagrees_with_the_members_is_refused():
    with pytest.raises(ValueError):
        ResidualSet(set_id="s", plan_version="plan-1", label="l", file_count=2,
                    representative_examples=(), file_type_distribution=(),
                    age_range=("a", "b"), evidence_availability="none",
                    sensitivity_status="public_low", protected=False,
                    weak_graph_neighbours=(), reason_not_placed="r",
                    member_file_ids=("f",))


def test_protected_is_a_flag_and_never_a_null():
    # §8.4 Open question 1: neighbouring parts consume P7's flag rather than
    # infer it from the handling class. A null here reads as `false` to every
    # consumer that tests it, which is a protected set becoming an ordinary one.
    with pytest.raises(ValueError):
        ResidualSet(set_id="s", plan_version="plan-1", label="l", file_count=1,
                    representative_examples=(), file_type_distribution=(),
                    age_range=("a", "b"), evidence_availability="none",
                    sensitivity_status="highly_sensitive_credential_bearing",
                    protected=None, weak_graph_neighbours=(),
                    reason_not_placed="r", member_file_ids=("f",))


# --- §8.6: a ceiling reduces work and never drops files ------------------------------

def test_a_set_over_the_batch_ceiling_is_split_not_truncated(p11_conn):
    # §8.6: a ceiling reduces work, it never drops files. A truncated set would
    # leave files unmentioned, which is the "understood and found unimportant"
    # impression §8.6 exists to prevent.
    sets = _surface(p11_conn)
    assert sum(s.file_count for s in sets) == len(UNPLACED)
    assert all(s.file_count <= LIMITS.max_residual_files_per_batch for s in sets)
    assert {f for s in sets for f in s.member_file_ids} == set(UNPLACED)


def test_a_set_within_the_ceiling_is_not_relabelled_as_a_slice(p11_conn):
    # The negative twin of the split. Without it the "(n of m)" suffix could be
    # unconditional and every single-batch set would read as a fragment.
    sets = _surface(p11_conn, unplaced=("f-gate", "f-receipt"))
    assert len(sets) == 1
    assert sets[0].label == "Screenshots with no association"
    # The id is pinned exactly, not merely checked for a word. `require_set_decision`
    # keys on it, so an id that gains a batch suffix when the ceiling changes would
    # orphan the decision the user already recorded against the set.
    assert sets[0].set_id == "plan-1:Screenshots with no association"


def test_a_partition_that_loses_a_file_is_refused(p11_conn):
    # The residual screen is the LAST place a file can be mentioned. A partition
    # that quietly omits one produces a corpus where some files were never shown
    # and never explained.
    def _drops(file_ids):
        return (_group("Screenshots", tuple(file_ids)[:-1]),)

    with pytest.raises(ValueError) as raised:
        _surface(p11_conn, partition=_drops)
    assert "f-clip" in str(raised.value)

    def _invents(file_ids):
        return (_group("Screenshots", tuple(file_ids) + ("f-ghost",)),)

    with pytest.raises(ValueError) as raised:
        _surface(p11_conn, partition=_invents)
    assert "f-ghost" in str(raised.value)


def test_a_missing_partition_refuses_rather_than_inventing_a_taxonomy(p11_conn):
    with pytest.raises(ResidualPartitionRequired):
        _surface(p11_conn, partition=None)


def test_a_surfacing_that_fails_partway_leaves_no_half_screen(p11_conn):
    """The rows and their events commit together, or not at all.

    The connection is opened `isolation_level=None` (`database_agent/db.py:43`),
    so without one explicit transaction each INSERT commits on its own and a
    partition that raises on its second group leaves the first group's set
    stored, its `residual_set_surfaced` event appended, and a review screen
    showing files whose siblings were never counted.
    """
    def _fails_on_the_second(file_ids):
        return (_group("Screenshots", ("f-gate", "f-receipt")),
                dict(_group("Broken", ("f-clip",)), reason_not_placed=None))

    with pytest.raises((TypeError, ValueError)):
        _surface(p11_conn, partition=_fails_on_the_second)
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM residual_sets").fetchone()["c"] == 0
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM events WHERE event_type = ?",
        (v.RESIDUAL_SET_SURFACED,)).fetchone()["c"] == 0


# --- §7.6: the spend gate ------------------------------------------------------------

def test_a_per_file_call_before_the_set_decision_is_refused(p11_conn):
    sets = _surface(p11_conn)
    with pytest.raises(SetDecisionRequired):
        require_set_decision(p11_conn, plan_version="plan-1",
                             set_id=sets[0].set_id)
    # The negative twin: once the answer exists the same read returns it, so the
    # refusal is about the missing decision and not about the query.
    _decide(p11_conn, sets[0].set_id, v.LEAVE_IN_PLACE)
    assert require_set_decision(p11_conn, plan_version="plan-1",
                                set_id=sets[0].set_id).choice == v.LEAVE_IN_PLACE


def test_a_decision_in_another_plan_version_does_not_unlock_this_one(p11_conn):
    sets = _surface(p11_conn)
    _decide(p11_conn, sets[0].set_id, v.REVIEW_WITH_MODEL, plan_version="plan-9")
    with pytest.raises(SetDecisionRequired):
        require_set_decision(p11_conn, plan_version="plan-1",
                             set_id=sets[0].set_id)


def test_leave_in_place_produces_zero_model_calls(p11_conn):
    sets = _surface(p11_conn)
    _decide(p11_conn, sets[0].set_id, v.LEAVE_IN_PLACE)
    stored = require_set_decision(p11_conn, plan_version="plan-1",
                                  set_id=sets[0].set_id)
    assert model_calls_permitted(stored) is False


def test_only_the_review_with_model_choice_permits_a_call(p11_conn):
    sets = _surface(p11_conn)
    for choice, node_id, permitted in (
        (v.REVIEW_WITH_MODEL, None, True),
        (v.SEND_TO_APPROVED_NODE, "n-review-later", False),
        (v.CREATE_CUSTOM_BRANCH, None, False),
        (v.LEAVE_IN_PLACE, None, False),
    ):
        decision = ResidualSetDecision(
            set_id=f"{sets[0].set_id}-{choice}", plan_version="plan-1",
            choice=choice, node_id=node_id, decided_at=FIXED_CLOCK)
        assert model_calls_permitted(decision) is permitted, choice


def test_an_unpermitted_choice_refuses_the_call_rather_than_skipping_it(p11_conn):
    sets = _surface(p11_conn)
    _decide(p11_conn, sets[0].set_id, v.LEAVE_IN_PLACE)
    with pytest.raises(ModelCallNotAuthorised) as raised:
        require_model_call_permitted(p11_conn, plan_version="plan-1",
                                     residual_set=sets[0])
    assert v.LEAVE_IN_PLACE in str(raised.value)


def test_the_gate_returns_the_decision_when_the_user_asked_for_a_model(p11_conn):
    # The negative twin for every refusal in the gate: one path reaches a call.
    sets = _surface(p11_conn)
    _decide(p11_conn, sets[0].set_id, v.REVIEW_WITH_MODEL)
    decision = require_model_call_permitted(p11_conn, plan_version="plan-1",
                                            residual_set=sets[0])
    assert decision.choice == v.REVIEW_WITH_MODEL


def test_the_gate_refuses_before_it_reads_a_decision(p11_conn):
    sets = _surface(p11_conn)
    with pytest.raises(SetDecisionRequired):
        require_model_call_permitted(p11_conn, plan_version="plan-1",
                                     residual_set=sets[0])


def test_send_to_approved_node_names_one_and_the_others_name_none():
    with pytest.raises(ValueError):
        ResidualSetDecision(set_id="s1", plan_version="plan-1",
                            choice=v.SEND_TO_APPROVED_NODE, node_id=None,
                            decided_at=FIXED_CLOCK)
    with pytest.raises(ValueError):
        ResidualSetDecision(set_id="s1", plan_version="plan-1",
                            choice=v.LEAVE_IN_PLACE, node_id="n-course",
                            decided_at=FIXED_CLOCK)
    with pytest.raises(v.OutOfVocabulary):
        ResidualSetDecision(set_id="s1", plan_version="plan-1",
                            choice="tidy_them_up", node_id=None,
                            decided_at=FIXED_CLOCK)


def test_surfacing_and_deciding_are_two_events(p11_conn):
    # A set that was shown and never decided must be distinguishable from one
    # that was decided, because §7.6 gates spend on the second.
    sets = _surface(p11_conn)
    kinds = [row["event_type"] for row in p11_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]
    assert v.RESIDUAL_SET_SURFACED in kinds
    assert v.RESIDUAL_SET_DECIDED not in kinds
    _decide(p11_conn, sets[0].set_id, v.LEAVE_IN_PLACE)
    kinds = [row["event_type"] for row in p11_conn.execute(
        "SELECT event_type FROM events ORDER BY event_id")]
    assert v.RESIDUAL_SET_SURFACED in kinds
    assert v.RESIDUAL_SET_DECIDED in kinds


def test_a_custom_branch_is_a_tree_edit_and_names_no_new_node(p11_conn):
    # §7.10 and §8.8: creating a folder during residual review is routed to P10
    # and opens a draft plan version. P11 mints no node.
    decision = ResidualSetDecision(set_id="s1", plan_version="plan-1",
                                   choice=v.CREATE_CUSTOM_BRANCH, node_id=None,
                                   decided_at=FIXED_CLOCK)
    assert decision.node_id is None
    assert model_calls_permitted(decision) is False


# --- the standing rule: marked and counted, never opened -----------------------------

PROTECTED_UNPLACED = ("f-gate", "f-keychain")


def _mixed_partition(file_ids):
    return (
        _group("Screenshots with no association", ("f-gate",)),
        _group("System and credential files", ("f-keychain",), protected=True,
               sensitivity_status="highly_sensitive_credential_bearing",
               representative_examples=(),
               reason_not_placed="present and counted; never opened, because "
                                 "these are system or credential-bearing files"),
    )


def test_a_protected_set_is_surfaced_and_counted_and_never_omitted(p11_conn):
    sets = _surface(p11_conn, unplaced=PROTECTED_UNPLACED,
                    partition=_mixed_partition)
    assert sum(s.file_count for s in sets) == len(PROTECTED_UNPLACED)
    protected = next(s for s in sets if s.protected)
    assert protected.file_count == 1
    assert protected.member_file_ids == ("f-keychain",)
    # A reachable explanation, not silence and not "found unimportant".
    assert protected.reason_not_placed
    assert protected.representative_examples == ()
    stored = p11_conn.execute(
        "SELECT count(*) AS c FROM residual_sets WHERE label LIKE ?",
        ("System and credential%",)).fetchone()["c"]
    assert stored == 1


def test_a_model_call_over_a_protected_set_is_refused_not_skipped(p11_conn):
    sets = _surface(p11_conn, unplaced=PROTECTED_UNPLACED,
                    partition=_mixed_partition)
    protected = next(s for s in sets if s.protected)
    ordinary = next(s for s in sets if not s.protected)
    # The user asked for a model over BOTH sets. One is answered, one is refused
    # by name -- so the refusal is about the protection and not about the choice.
    _decide(p11_conn, protected.set_id, v.REVIEW_WITH_MODEL)
    _decide(p11_conn, ordinary.set_id, v.REVIEW_WITH_MODEL)
    with pytest.raises(ProtectedSetNotReadable) as raised:
        require_model_call_permitted(p11_conn, plan_version="plan-1",
                                     residual_set=protected)
    assert protected.set_id in str(raised.value)
    assert require_model_call_permitted(
        p11_conn, plan_version="plan-1",
        residual_set=ordinary).choice == v.REVIEW_WITH_MODEL


def test_a_protected_set_is_refused_before_any_decision_is_even_read(p11_conn):
    # Undecided, the protected set must still refuse the call -- and refuse it as
    # a protection, not as a missing decision, or the fix looks like "decide it".
    sets = _surface(p11_conn, unplaced=PROTECTED_UNPLACED,
                    partition=_mixed_partition)
    protected = next(s for s in sets if s.protected)
    with pytest.raises(ProtectedSetNotReadable):
        require_model_call_permitted(p11_conn, plan_version="plan-1",
                                     residual_set=protected)


def test_two_current_answers_for_one_set_are_refused_by_the_database(p11_conn):
    # `one_current_set_decision` is the guard. Two live answers to "what should
    # happen to this set?" would let the gate authorise a call the user revoked.
    import sqlite3

    sets = _surface(p11_conn)
    _decide(p11_conn, sets[0].set_id, v.LEAVE_IN_PLACE)
    with pytest.raises(sqlite3.IntegrityError):
        record_set_decision(
            p11_conn,
            ResidualSetDecision(set_id=sets[0].set_id, plan_version="plan-1",
                                choice=v.REVIEW_WITH_MODEL, node_id=None,
                                decided_at="2026-08-27T01:00:00Z"),
            component_version="P11-test", observed_at=FIXED_CLOCK, user_id="u1")


def test_a_changed_answer_supersedes_and_the_gate_reads_the_new_one(p11_conn):
    # §7.10 lets a user change a set answer. The gate reads the CURRENT row, so
    # `superseded_by IS NULL` is what stops a revoked `review_with_model` from
    # authorising spend forever -- and the row address has to admit a second row
    # for that clause to be reachable at all.
    from database_agent.supersede import mark_superseded
    from placement.residual import set_decision_id

    sets = _surface(p11_conn)
    first = _decide(p11_conn, sets[0].set_id, v.REVIEW_WITH_MODEL)
    second = ResidualSetDecision(set_id=sets[0].set_id, plan_version="plan-1",
                                 choice=v.LEAVE_IN_PLACE, node_id=None,
                                 decided_at="2026-08-27T01:00:00Z")
    mark_superseded(p11_conn, "residual_set_decisions",
                    old_id=set_decision_id(first), new_id=set_decision_id(second),
                    reason="the user changed their answer for this set")
    record_set_decision(p11_conn, second, component_version="P11-test",
                        observed_at=FIXED_CLOCK, user_id="u1")
    assert require_set_decision(p11_conn, plan_version="plan-1",
                                set_id=sets[0].set_id).choice == v.LEAVE_IN_PLACE
    with pytest.raises(ModelCallNotAuthorised):
        require_model_call_permitted(p11_conn, plan_version="plan-1",
                                     residual_set=sets[0])
    # The revoked answer is still readable; §8.2 keeps it rather than erasing it.
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM residual_set_decisions").fetchone()["c"] == 2


def test_a_set_decision_and_its_event_commit_together(p11_conn):
    """One transaction, not two. A decision row with no event is spend the user
    authorised that §8.2 cannot explain; an event with no row is a claim about an
    answer that was never recorded.

    The event append is made to fail (`observed_at` is required,
    `database_agent/events.py:115`) AFTER the row insert has already succeeded,
    which is the only ordering that tells the two apart.
    """
    from database_agent.events import MalformedEvent

    sets = _surface(p11_conn)
    with pytest.raises(MalformedEvent):
        record_set_decision(
            p11_conn,
            ResidualSetDecision(set_id=sets[0].set_id, plan_version="plan-1",
                                choice=v.LEAVE_IN_PLACE, node_id=None,
                                decided_at=FIXED_CLOCK),
            component_version="P11-test", observed_at="", user_id="u1")
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM residual_set_decisions").fetchone()["c"] == 0
    with pytest.raises(SetDecisionRequired):
        require_set_decision(p11_conn, plan_version="plan-1",
                             set_id=sets[0].set_id)


def _placement_sources_calling(function_name: str) -> set[str]:
    """Modules in `src/placement/` that CALL `function_name`, by AST, not by grep."""
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    callers = set()
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else func.id if isinstance(func, ast.Name) else None)
            if name == function_name:
                callers.add(path.name)
    return callers


def test_the_spend_gate_is_actually_called_before_a_residual_model_call():
    """The gate exists and nothing in `src/placement/` calls it yet.

    `require_model_call_permitted` is §7.6's whole point, and a gate no caller
    passes through is a gate in name only. The owed consumer is the per-file
    residual loop, which is not built.

    The gap is CLOSED: `pipeline.review_residual_sets` calls it immediately
    before the spend, and only for a set whose own decision asked for a model.
    The `xfail(strict=True)` marker that reported the gap is gone, removed by the
    XPASS it was written to produce.
    """
    assert _placement_sources_calling("require_model_call_permitted") - {
        "residual.py"}




"""Sites C/D placement and residual validation against P8-owned recorded pairs."""
from __future__ import annotations

import dataclasses
import inspect
import json
from collections import Counter

import pytest

from database_agent.db import transaction
from llm_harness.fixtures import (
    SITE_C_OUTCOME_PAIRS,
    SITE_C_REASON_PAIRS,
    SITE_D_OUTCOME_PAIRS,
    SITE_D_REASON_PAIRS,
    SITE_D_SUPPORT_RULE_PAIR,
)
from llm_harness.placement_validation import (
    PlacementDependencies,
    ResidualDependencies,
    record_cd_verdict,
    revalidate_for_plan,
    validate_placement_response,
    validate_residual_response,
)
from llm_harness.records import Conflict, P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACTION_NOT_IN_CONTROLLED_SET,
    BELOW_SUPPORT_THRESHOLD,
    CHOOSE_RESIDUAL_DESTINATION,
    CONFLICT_IGNORED,
    C_PLACEMENT,
    D_RESIDUAL,
    DESTINATION_NOT_IN_FROZEN_TREE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN,
    INVENTED_DATE,
    INVENTED_FOLDER,
    INVENTED_INSTITUTION,
    INVENTED_NODE,
    INVENTED_PROJECT,
    LEAVE_IN_CURRENT_LOCATION,
    LEAVE_IN_PLACE,
    MARK_REVIEW_LATER,
    MOVE_PLAN_ELIGIBLE,
    NODE_NOT_IN_FROZEN_TREE,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    REJECT,
    REJECTED,
    RESIDUAL_DESTINATION,
    RESIDUAL_DESTINATION_REVIEW,
    RETURN_TO_PLACEMENT,
    REVIEW_LATER,
    SCHEMA_INVALID,
    SENSITIVITY_POLICY_VIOLATION,
    SENSITIVITY_RESTRICTION_IGNORED,
    SITE_C_REASON_CODES,
    SITE_D_REASON_CODES,
    SLOT_FILLED_WITHOUT_EVIDENCE,
    STRONGER_RELATIONSHIP_OVERLOOKED,
    UNRESOLVED,
    VALID_REVIEW_REQUIRED,
    WEAK,
)
from p8.conftest import FIXED_CLOCK
from llm_harness.fixtures import FIXTURE_HANDLE_KEY
from llm_harness.wire_handles import wire_handle

RELEASED = "span-1"
SUPPORT_THRESHOLD = 0.5


def _resolver(observation_key: str) -> str | None:
    if observation_key.startswith("obs-"):
        return RELEASED
    return None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _margin_ok(best, next_best) -> bool:
    return float(best) - float(next_best) >= 0.2


def _placement_deps(pair) -> PlacementDependencies:
    absent = frozenset(pair.frozen_absent_nodes)

    def node_exists(node_id: str, plan_version: str) -> bool:
        del plan_version
        return node_id not in absent

    return PlacementDependencies(
        node_exists=node_exists,
        support_threshold=SUPPORT_THRESHOLD,
        margin_predicate=_margin_ok,
        sensitivity_policy=lambda dossier, payload: pair.sensitivity_ok,
    )


def _residual_deps(pair) -> ResidualDependencies:
    absent = frozenset(pair.frozen_absent_nodes)

    def node_exists(node_id: str, plan_version: str) -> bool:
        del plan_version
        return node_id not in absent

    return ResidualDependencies(
        node_exists=node_exists,
        sensitivity_policy=lambda dossier, payload: pair.sensitivity_ok,
        approved_target_ids=pair.approved_target_ids,
    )


def _validate_c(pair, *, dependencies=None, contradicts=_never_contradicts):
    deps = _placement_deps(pair) if dependencies is None else dependencies
    return validate_placement_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=contradicts,
        dependencies=deps,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )


def _validate_d(pair, *, dependencies=None, contradicts=_never_contradicts):
    deps = _residual_deps(pair) if dependencies is None else dependencies
    return validate_residual_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=contradicts,
        dependencies=deps,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )


def _with_payload_fields(pair, *, drop=(), **fields):
    parsed = json.loads(pair.response_bytes)
    payload = parsed["claims"][0]["payload"]
    for key in drop:
        payload.pop(key, None)
    payload.update(fields)
    return dataclasses.replace(pair, response_bytes=json.dumps(parsed).encode())


def test_site_c_reason_registry_exercises_each_code_exactly_once():
    seen: list[str] = []
    for pair in SITE_C_REASON_PAIRS:
        assert pair.dossier.call_site == C_PLACEMENT
        assert pair.dossier.plan_version
        result = _validate_c(pair)
        assert not isinstance(result, ValidationUnavailable), pair.name
        verdicts, report = result
        verdict = verdicts[0]
        assert verdict.reasons == pair.expected_reasons
        assert len(verdict.reasons) == 1
        assert verdict.outcome == pair.expected_outcome
        assert verdict.disposition == pair.expected_disposition
        assert verdict.plan_version == pair.dossier.plan_version
        seen.append(verdict.reasons[0])
        assert report.reasons_histogram[verdict.reasons[0]] == 1
    assert tuple(seen) == SITE_C_REASON_CODES
    assert Counter(seen) == Counter(SITE_C_REASON_CODES)


def test_site_d_reason_registry_exercises_each_code_exactly_once():
    seen: list[str] = []
    for pair in SITE_D_REASON_PAIRS:
        assert pair.dossier.call_site == D_RESIDUAL
        assert pair.dossier.plan_version
        result = _validate_d(pair)
        assert not isinstance(result, ValidationUnavailable), pair.name
        verdict = result[0][0]
        assert verdict.reasons == pair.expected_reasons
        assert len(verdict.reasons) == 1
        assert verdict.outcome == pair.expected_outcome
        assert verdict.disposition == pair.expected_disposition
        assert verdict.plan_version == pair.dossier.plan_version
        seen.append(verdict.reasons[0])
    assert tuple(seen) == SITE_D_REASON_CODES
    assert Counter(seen) == Counter(SITE_D_REASON_CODES)


def test_site_c_two_condition_codes_are_weak_and_isolated():
    below = next(
        p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (BELOW_SUPPORT_THRESHOLD,)
    )
    margin = next(
        p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (INSUFFICIENT_MARGIN,)
    )
    hub = next(p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (GENERIC_HUB_ONLY,))
    for pair in (below, margin, hub):
        verdict = _validate_c(pair)[0][0]
        assert verdict.outcome == WEAK
        assert verdict.may_propose is False
        assert verdict.disposition == UNRESOLVED
        assert INSUFFICIENT_MARGIN not in verdict.reasons or pair is margin
        assert BELOW_SUPPORT_THRESHOLD not in verdict.reasons or pair is below


def test_site_c_omitted_support_is_not_accept_direct():
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    result = _validate_c(_with_payload_fields(pair, drop=("support",)))
    assert not isinstance(result, ValidationUnavailable)
    verdict = result[0][0]
    assert verdict.outcome != ACCEPT_DIRECT
    assert verdict.may_propose is False
    assert verdict.outcome in {WEAK, REJECT}
    assert BELOW_SUPPORT_THRESHOLD in verdict.reasons or SCHEMA_INVALID in verdict.reasons


def test_site_c_omitted_next_support_is_not_accept_direct():
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    result = _validate_c(_with_payload_fields(pair, drop=("next_support",)))
    assert not isinstance(result, ValidationUnavailable)
    verdict = result[0][0]
    assert verdict.outcome != ACCEPT_DIRECT
    assert verdict.may_propose is False
    assert verdict.outcome in {WEAK, REJECT}
    assert INSUFFICIENT_MARGIN in verdict.reasons or SCHEMA_INVALID in verdict.reasons


def test_site_c_non_numeric_support_does_not_raise():
    pair = next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")
    for fields in (
        {"support": "high"},
        {"next_support": None},
        {"support": True},
    ):
        result = _validate_c(_with_payload_fields(pair, **fields))
        assert not isinstance(result, ValidationUnavailable), fields
        verdict = result[0][0]
        assert verdict.outcome != ACCEPT_DIRECT, fields
        assert verdict.outcome in {WEAK, REJECT}, fields
        assert SCHEMA_INVALID in verdict.reasons or set(verdict.reasons) & {
            BELOW_SUPPORT_THRESHOLD, INSUFFICIENT_MARGIN,
        }, fields


def test_site_c_slot_filled_without_evidence_rejects():
    pair = next(
        p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (SLOT_FILLED_WITHOUT_EVIDENCE,)
    )
    verdict = _validate_c(pair)[0][0]
    assert verdict.reasons == (SLOT_FILLED_WITHOUT_EVIDENCE,)
    assert verdict.outcome == REJECT
    assert verdict.disposition == NO_DESTINATION


def test_site_c_frozen_tree_and_sensitivity():
    missing = next(
        p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (NODE_NOT_IN_FROZEN_TREE,)
    )
    sensitivity = next(
        p for p in SITE_C_REASON_PAIRS
        if p.expected_reasons == (SENSITIVITY_POLICY_VIOLATION,)
    )
    assert _validate_c(missing)[0][0].outcome == REJECT
    assert _validate_c(sensitivity)[0][0].reasons == (SENSITIVITY_POLICY_VIOLATION,)


def test_site_c_outcome_pairs():
    by_name = {pair.name: pair for pair in SITE_C_OUTCOME_PAIRS}
    direct = _validate_c(by_name["direct_accept"])[0][0]
    assert direct.outcome == ACCEPT_DIRECT
    assert direct.disposition == MOVE_PLAN_ELIGIBLE
    assert direct.reasons == ()
    assert direct.plan_version == by_name["direct_accept"].dossier.plan_version

    context = _validate_c(by_name["context_accept"])[0][0]
    assert context.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert context.disposition == VALID_REVIEW_REQUIRED
    assert context.requires_review is True

    weak = _validate_c(by_name["weak"])[0][0]
    assert weak.outcome == WEAK
    assert weak.disposition == UNRESOLVED
    assert weak.may_propose is False
    assert not set(weak.reasons) & set(SITE_C_REASON_CODES)

    reject = _validate_c(by_name["reject"])[0][0]
    assert reject.outcome == REJECT
    assert reject.disposition == NO_DESTINATION
    assert not set(reject.reasons) & set(SITE_C_REASON_CODES)

    unknown = _validate_c(by_name["unknown"])[0][0]
    assert unknown.outcome == ABSTAIN
    assert unknown.disposition == NO_SUPPORTED_DESTINATION


def test_site_d_stronger_relationship_returns_to_placement():
    pair = next(
        p for p in SITE_D_REASON_PAIRS
        if p.expected_reasons == (STRONGER_RELATIONSHIP_OVERLOOKED,)
    )
    verdict = _validate_d(pair)[0][0]
    assert verdict.reasons == (STRONGER_RELATIONSHIP_OVERLOOKED,)
    assert verdict.outcome == REJECT
    assert verdict.disposition == RETURN_TO_PLACEMENT


# `104` R-157. THE MODEL IS SHOWN A HANDLE AND NEVER THE ID. `dossier._body`
# writes `wire_handle(conflict_id)`, so the list that comes back is a list of
# handles; both checks below used to hold it against the local ids, which never
# left the device, and every answer at a site with a conflict was rejected. The
# handle is computed here from `wire_handle` and not from the validator's own
# inverse, so these hold the wire contract rather than one function against
# itself.


def _shown(dossier) -> list[str]:
    return [wire_handle(item.conflict_id, key=FIXTURE_HANDLE_KEY)
            for item in dossier.conflicts]


def _two_conflict_pair():
    pair = next(
        p for p in SITE_C_REASON_PAIRS if p.expected_reasons == (CONFLICT_IGNORED,)
    )
    dossier = dataclasses.replace(pair.dossier, conflicts=(
        Conflict("c1", "stronger_fact"), Conflict("c2", "stronger_fact")))
    return dataclasses.replace(pair, dossier=dossier)


def test_r157_site_c_every_conflict_named_by_its_wire_handle_is_considered():
    pair = _two_conflict_pair()
    named = _with_payload_fields(pair, conflicts_considered=_shown(pair.dossier))
    verdict = _validate_c(named)[0][0]
    assert CONFLICT_IGNORED not in verdict.reasons
    assert verdict.outcome == ACCEPT_DIRECT
    assert verdict.disposition == MOVE_PLAN_ELIGIBLE


def test_r157_site_c_a_subset_of_the_handles_is_still_conflict_ignored():
    pair = _two_conflict_pair()
    subset = _with_payload_fields(
        pair, conflicts_considered=_shown(pair.dossier)[:1])
    verdict = _validate_c(subset)[0][0]
    assert verdict.reasons == (CONFLICT_IGNORED,)
    assert verdict.outcome == REJECT
    assert verdict.disposition == NO_DESTINATION


def test_r157_site_d_a_stronger_relationship_named_by_handle_is_considered():
    pair = next(
        p for p in SITE_D_REASON_PAIRS
        if p.expected_reasons == (STRONGER_RELATIONSHIP_OVERLOOKED,)
    )
    named = _with_payload_fields(
        pair, relationships_considered=_shown(pair.dossier))
    verdict = _validate_d(named)[0][0]
    assert STRONGER_RELATIONSHIP_OVERLOOKED not in verdict.reasons
    assert verdict.outcome != REJECT


def test_site_d_same_file_evidence_and_controlled_set():
    file_record = next(
        p for p in SITE_D_REASON_PAIRS if p.expected_reasons == (EVIDENCE_NOT_IN_FILE_RECORD,)
    )
    action = next(
        p for p in SITE_D_REASON_PAIRS if p.expected_reasons == (ACTION_NOT_IN_CONTROLLED_SET,)
    )
    folder = next(
        p for p in SITE_D_REASON_PAIRS if p.expected_reasons == (INVENTED_FOLDER,)
    )
    dest = next(
        p for p in SITE_D_REASON_PAIRS if p.expected_reasons == (DESTINATION_NOT_IN_FROZEN_TREE,)
    )
    restriction = next(
        p for p in SITE_D_REASON_PAIRS
        if p.expected_reasons == (SENSITIVITY_RESTRICTION_IGNORED,)
    )
    assert _validate_d(file_record)[0][0].reasons == (EVIDENCE_NOT_IN_FILE_RECORD,)
    assert _validate_d(action)[0][0].reasons == (ACTION_NOT_IN_CONTROLLED_SET,)
    assert _validate_d(folder)[0][0].reasons == (INVENTED_FOLDER,)
    assert _validate_d(dest)[0][0].reasons == (DESTINATION_NOT_IN_FROZEN_TREE,)
    assert _validate_d(restriction)[0][0].reasons == (SENSITIVITY_RESTRICTION_IGNORED,)


def test_site_d_choose_destination_rejects_missing_or_invalid_target():
    pair = next(p for p in SITE_D_OUTCOME_PAIRS if p.name == "direct_accept")
    action = json.loads(pair.response_bytes)["claims"][0]["payload"]["action"]
    assert action == CHOOSE_RESIDUAL_DESTINATION
    for target in (None, "", 123, ["node-legal"]):
        result = _validate_d(_with_payload_fields(pair, target=target))
        assert not isinstance(result, ValidationUnavailable), target
        verdict = result[0][0]
        assert verdict.outcome == REJECT, target
        assert verdict.may_propose is False, target
        assert set(verdict.reasons) & {
            DESTINATION_NOT_IN_FROZEN_TREE, ACTION_NOT_IN_CONTROLLED_SET,
        }, (target, verdict.reasons)


def test_site_d_outcome_pairs():
    by_name = {pair.name: pair for pair in SITE_D_OUTCOME_PAIRS}
    direct = _validate_d(by_name["direct_accept"])[0][0]
    assert direct.outcome == ACCEPT_DIRECT
    assert direct.disposition == RESIDUAL_DESTINATION
    assert direct.reasons == ()

    handback = by_name.get("context_accept")
    context = _validate_d(handback)[0][0]
    assert context.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert context.requires_review is True

    weak = _validate_d(by_name["weak"])[0][0]
    assert weak.outcome == WEAK
    assert weak.disposition in {REVIEW_LATER, LEAVE_IN_PLACE}
    assert weak.may_propose is False

    reject = _validate_d(by_name["reject"])[0][0]
    assert reject.outcome == REJECT
    assert reject.disposition == REJECTED
    assert not set(reject.reasons) & set(SITE_D_REASON_CODES)

    unknown = _validate_d(by_name["unknown"])[0][0]
    assert unknown.outcome == ABSTAIN


def test_site_d_two_condition_fixture_is_unavailable():
    result = _validate_d(SITE_D_SUPPORT_RULE_PAIR)
    assert isinstance(result, ValidationUnavailable)
    assert result.missing == ("site_d_support_rule",)


def test_site_d_does_not_apply_site_c_two_condition_rule():
    result = _validate_d(SITE_D_SUPPORT_RULE_PAIR)
    assert isinstance(result, ValidationUnavailable)
    assert BELOW_SUPPORT_THRESHOLD not in result.missing
    assert INSUFFICIENT_MARGIN not in result.missing


def test_omitting_placement_oracles_is_unavailable():
    pair = SITE_C_OUTCOME_PAIRS[0]
    result = validate_placement_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=None,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    for name in (
        "node_exists", "support_threshold", "margin_predicate", "sensitivity_policy",
    ):
        assert name in result.missing


def test_omitting_residual_oracles_is_unavailable():
    pair = SITE_D_OUTCOME_PAIRS[0]
    result = validate_residual_response(
        pair.dossier,
        pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=None,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    assert "node_exists" in result.missing
    assert "approved_target_ids" in result.missing
    assert "sensitivity_policy" in result.missing
    assert "residual_actions" not in result.missing


def test_cd_verdict_stores_plan_version_and_snapshot_identity(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    assert pair.evidence_snapshot_id
    record_cd_verdict(
        p8_conn, verdict,
        evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        release_audit_id=17,
        observed_at=FIXED_CLOCK,
    )
    row = p8_conn.execute(
        "SELECT plan_version, payload FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()
    assert row["plan_version"] == pair.dossier.plan_version
    payload = json.loads(row["payload"])
    assert payload["plan_version"] == pair.dossier.plan_version
    identity = p8_conn.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()
    assert identity["plan_version"] == pair.dossier.plan_version
    assert identity["evidence_snapshot_id"] == pair.evidence_snapshot_id


def test_record_cd_verdict_requires_provenance_with_no_defaults():
    params = inspect.signature(record_cd_verdict).parameters
    for name in ("model_id", "prompt_fingerprint", "release_audit_id"):
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY
        assert params[name].default is inspect.Parameter.empty


def test_record_cd_verdict_rolls_back_if_identity_insert_fails(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    p8_conn.execute(
        "CREATE TABLE IF NOT EXISTS llm_cd_plan_identity ("
        "verdict_id TEXT PRIMARY KEY, plan_version TEXT NOT NULL, "
        "evidence_snapshot_id TEXT NOT NULL)"
    )
    p8_conn.execute(
        "INSERT INTO llm_cd_plan_identity "
        "(verdict_id, plan_version, evidence_snapshot_id) VALUES (?, ?, ?)",
        (verdict.verdict_id, verdict.plan_version, "pre-existing"),
    )
    with pytest.raises(Exception):
        record_cd_verdict(
            p8_conn,
            verdict,
            evidence_snapshot_id=pair.evidence_snapshot_id,
            model_id="fixture-model",
            prompt_fingerprint="fp-canonical",
            release_audit_id=17,
            observed_at=FIXED_CLOCK,
        )
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()["c"] == 0


class _CallerFailed(Exception):
    """A caller's own failure, raised after the verdict write returned."""


def test_a_cd_verdict_write_leaves_its_callers_transaction_open(p8_conn):
    """`record_cd_verdict` joins the caller's transaction; it never ends it.

    `harness._issue_and_validate` holds ONE transaction over the consequence and
    the verdict that justifies it, and this write runs inside it. The lazy
    `llm_cd_plan_identity` DDL used to run through
    `sqlite3.Connection.executescript`, which COMMITs any pending transaction
    before it runs the script -- unconditionally, even when the script is a
    `CREATE TABLE IF NOT EXISTS` that does nothing. So the harness's transaction
    ended HERE, the verdict write committed on its own, and the harness's own
    COMMIT raised `cannot commit - no transaction is active`. That was every
    live model-backed placement the product ever attempted.
    """
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    with transaction(p8_conn):
        record_cd_verdict(
            p8_conn, verdict,
            evidence_snapshot_id=pair.evidence_snapshot_id,
            model_id="fixture-model",
            prompt_fingerprint="fp-canonical",
            release_audit_id=17,
            observed_at=FIXED_CLOCK,
        )
        # The caller's transaction, not a committed one and not a second one.
        assert p8_conn.in_transaction
    # ... and the caller's own COMMIT is the one that lands both rows.
    assert not p8_conn.in_transaction
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()["c"] == 1
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_cd_plan_identity WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()["c"] == 1


def test_a_cd_verdict_rolls_back_with_the_caller_that_owns_the_transaction(p8_conn):
    """The discriminating twin: not raising is only half of "one transaction".

    A write that quietly commits itself also stops raising. What proves it JOINED
    the caller's transaction is that the caller's failure takes it back out --
    a verdict that survived the rollback of the consequence it justifies is the
    orphan the single transaction exists to prevent.
    """
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    # Pre-created so the rollback below can only remove ROWS: the table itself is
    # not what is under test, and the broken `executescript` committed the
    # caller's transaction even when this DDL had nothing left to do.
    p8_conn.execute(
        "CREATE TABLE IF NOT EXISTS llm_cd_plan_identity ("
        "verdict_id TEXT PRIMARY KEY, plan_version TEXT NOT NULL, "
        "evidence_snapshot_id TEXT NOT NULL)"
    )
    with pytest.raises(_CallerFailed):
        with transaction(p8_conn):
            record_cd_verdict(
                p8_conn, verdict,
                evidence_snapshot_id=pair.evidence_snapshot_id,
                model_id="fixture-model",
                prompt_fingerprint="fp-canonical",
                release_audit_id=17,
                observed_at=FIXED_CLOCK,
            )
            raise _CallerFailed
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()["c"] == 0
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_cd_plan_identity WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()["c"] == 0


def test_revalidate_same_version_is_stable(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    record_cd_verdict(
        p8_conn, verdict,
        evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    result = revalidate_for_plan(
        p8_conn,
        current_plan_version=pair.dossier.plan_version,
        current_evidence_snapshot_id=pair.evidence_snapshot_id,
        previous_verdict_id=verdict.verdict_id,
        dossier=pair.dossier,
        response_bytes=pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=_placement_deps(pair),
        observed_at=FIXED_CLOCK,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, P8Verdict)
    assert result.verdict_id == verdict.verdict_id
    count = p8_conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"]
    assert count == 1
    supersessions = p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict_supersession"
    ).fetchone()["c"]
    assert supersessions == 0


def test_revalidate_changed_plan_appends_and_supersedes(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    record_cd_verdict(
        p8_conn, verdict,
        evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    result = revalidate_for_plan(
        p8_conn,
        current_plan_version="plan-v2",
        current_evidence_snapshot_id=pair.evidence_snapshot_id,
        previous_verdict_id=verdict.verdict_id,
        dossier=pair.dossier,
        response_bytes=pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=_placement_deps(pair),
        observed_at=FIXED_CLOCK,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, P8Verdict)
    assert result.verdict_id != verdict.verdict_id
    assert result.plan_version == "plan-v2"
    rows = p8_conn.execute(
        "SELECT verdict_id, plan_version, superseded_by FROM llm_verdict "
        "ORDER BY observed_at, verdict_id"
    ).fetchall()
    assert len(rows) == 2
    old = next(row for row in rows if row["verdict_id"] == verdict.verdict_id)
    assert old["plan_version"] == pair.dossier.plan_version
    assert old["superseded_by"] == result.verdict_id
    link = p8_conn.execute(
        "SELECT old_verdict_id, new_verdict_id FROM llm_verdict_supersession"
    ).fetchone()
    assert tuple(link) == (verdict.verdict_id, result.verdict_id)


def test_revalidate_changed_snapshot_appends_and_supersedes(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    record_cd_verdict(
        p8_conn, verdict,
        evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    result = revalidate_for_plan(
        p8_conn,
        current_plan_version=pair.dossier.plan_version,
        current_evidence_snapshot_id="snap-changed",
        previous_verdict_id=verdict.verdict_id,
        dossier=pair.dossier,
        response_bytes=pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=_placement_deps(pair),
        observed_at=FIXED_CLOCK,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, P8Verdict)
    assert result.verdict_id != verdict.verdict_id
    assert p8_conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 2


def test_revalidate_missing_oracles_leaves_prior_row_historical(p8_conn):
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict = _validate_c(pair)[0][0]
    record_cd_verdict(
        p8_conn, verdict,
        evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model",
        prompt_fingerprint="fp-fixture",
        release_audit_id=1,
        observed_at=FIXED_CLOCK,
    )
    result = revalidate_for_plan(
        p8_conn,
        current_plan_version="plan-v9",
        current_evidence_snapshot_id="snap-new",
        previous_verdict_id=verdict.verdict_id,
        dossier=pair.dossier,
        response_bytes=pair.response_bytes,
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        dependencies=None,
        observed_at=FIXED_CLOCK,
        model_id="fixture-model",
        prompt_fingerprint="fp-canonical",
        dossier_builder="p8-fixture",
        release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY,
    )
    assert isinstance(result, ValidationUnavailable)
    row = p8_conn.execute(
        "SELECT superseded_by, plan_version FROM llm_verdict WHERE verdict_id = ?",
        (verdict.verdict_id,),
    ).fetchone()
    assert row["superseded_by"] is None
    assert row["plan_version"] == pair.dossier.plan_version
    assert p8_conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == 1
    assert p8_conn.execute(
        "SELECT count(*) AS c FROM llm_verdict_supersession"
    ).fetchone()["c"] == 0


# --- R-15: the per-level check is GROUNDING, never membership of the node list ----
#
# `104` R-15: `_invented_dimension` compared a level's VALUE against
# `dossier.allowed_vocabulary`, which at site C is the list of legal NODE IDS. A
# node id is not a value and a value is not a node id, so every real date,
# institution and project a model reports is "invented" the day C is wired --
# and the only way a fixture could pass was to put values into the node-id list,
# which `_C_VOCAB` did.
#
# `104` §13.6 names the two hard checks: GROUNDING (the value is in the file's own
# evidence) and SCHEMA (the dimension exists). These pin grounding in both
# directions and pin that the frozen-tree checks above it did not move.


def _c_direct_pair():
    """The recorded site-C pair whose response is accepted with no reason."""
    return next(p for p in SITE_C_OUTCOME_PAIRS if p.name == "direct_accept")


def _also_saying(pair, value: str):
    """The same pair, with the file's OWN released evidence also saying `value`.

    Appended rather than replaced: the recorded citation quotes the released
    value, so a replacement would fail `CITATION_SPAN_MISMATCH` and the test
    would pass or fail for the wrong check.
    """
    released = tuple(
        dataclasses.replace(item, value=f"{item.value} {value}")
        for item in pair.dossier.released_evidence
    )
    return dataclasses.replace(
        pair, dossier=dataclasses.replace(pair.dossier, released_evidence=released))


def test_r15_a_project_value_the_files_own_evidence_states_is_not_invented():
    pair = _with_payload_fields(
        _also_saying(_c_direct_pair(), "PVA/RDP"),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "direct"},
        ])
    verdict = _validate_c(pair)[0][0]
    assert verdict.reasons == (), verdict.reasons
    assert verdict.outcome == ACCEPT_DIRECT


def test_r15_a_project_value_the_file_never_states_is_still_invented():
    pair = _with_payload_fields(
        _c_direct_pair(),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "direct"},
        ])
    verdict = _validate_c(pair)[0][0]
    assert verdict.reasons == (INVENTED_PROJECT,)
    assert verdict.outcome == REJECT


def test_r15_membership_of_the_node_id_list_no_longer_grounds_a_value():
    """The defect, from the other side: a value that IS a legal node id is still
    invented, because a node id says nothing about what the file states."""
    pair = _c_direct_pair()
    assert "node-alt" in pair.dossier.allowed_vocabulary
    pair = _with_payload_fields(pair, per_dimension_support=[
        {"dimension": "institution", "value": "node-alt", "support": "direct"},
    ])
    verdict = _validate_c(pair)[0][0]
    assert verdict.reasons == (INVENTED_INSTITUTION,)
    assert verdict.outcome == REJECT


def test_r15_a_date_the_file_states_is_not_invented_and_one_it_does_not_is():
    stated = _with_payload_fields(
        _also_saying(_c_direct_pair(), "Spring 2026"),
        per_dimension_support=[
            {"dimension": "date", "value": "Spring 2026", "support": "direct"},
        ])
    assert _validate_c(stated)[0][0].reasons == ()
    unstated = _with_payload_fields(
        _c_direct_pair(),
        per_dimension_support=[
            {"dimension": "date", "value": "Spring 2026", "support": "direct"},
        ])
    assert _validate_c(unstated)[0][0].reasons == (INVENTED_DATE,)


def _with_accepted_group(pair, group_id: str, *, accepted: bool = True):
    """The same pair, its dossier also carrying an `accepted_group` item: one the
    person accepted the file into (`user_confirmed`), or one it was merely
    retrieved for (`possible`), which `105` §14.1 says is not support."""
    from llm_harness.records import EvidenceItem
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    item = EvidenceItem(
        evidence_ref=group_id, kind="accepted_group",
        location="accepted group: a project the person accepted this file into",
        excerpt_span=None,
        reliability_state="user_confirmed" if accepted else "possible",
        basis=CONTEXT_SUPPORTED)
    dossier = dataclasses.replace(
        pair.dossier, evidence_items=pair.dossier.evidence_items + (item,))
    return dataclasses.replace(pair, dossier=dossier)


def test_r15_a_context_supported_level_is_not_grounded_against_this_files_evidence():
    """A `context` level's value comes from the accepted group the file belongs
    to, not from the file's own text (`00`:111, the C draft's rule 3), and the
    dossier carries no group values to ground it against (packet G3). So the
    check does not fire on one, and firing it would re-create R-15 one step over:
    every context-supported level rejected as invented. What IS verified since
    `105` §14.1 is the membership: the level names its group, and the group is
    one the person accepted the file into."""
    pair = _with_payload_fields(
        _with_accepted_group(_c_direct_pair(), "group-pva"),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "context",
             "context_group": "group-pva"},
        ])
    verdict = _validate_c(pair)[0][0]
    assert INVENTED_PROJECT not in verdict.reasons
    assert verdict.outcome == ACCEPT_DIRECT


def test_a_context_level_that_names_no_accepted_group_is_a_slot_filled_without_evidence():
    """`105` §14.1: accepted-group support is allowed because it is VERIFIABLE.
    A `context` level that names no group, names one the dossier does not carry,
    or names one the file was merely retrieved for is refused, and the value it
    carries is never the reason -- grounding still does not run on it."""
    unnamed = _with_payload_fields(
        _with_accepted_group(_c_direct_pair(), "group-pva"),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "context"}])
    unknown = _with_payload_fields(
        _with_accepted_group(_c_direct_pair(), "group-pva"),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "context",
             "context_group": "group-elsewhere"}])
    retrieved = _with_payload_fields(
        _with_accepted_group(_c_direct_pair(), "group-pva", accepted=False),
        per_dimension_support=[
            {"dimension": "project", "value": "PVA/RDP", "support": "context",
             "context_group": "group-pva"}])
    for pair in (unnamed, unknown, retrieved):
        verdict = _validate_c(pair)[0][0]
        assert verdict.reasons == (SLOT_FILLED_WITHOUT_EVIDENCE,)
        assert verdict.outcome == REJECT
        assert verdict.disposition == NO_DESTINATION


def test_r15_a_destination_outside_the_frozen_tree_is_still_rejected():
    """The two checks that sit ABOVE the dimension check do not move: a
    destination that is not a legal node id, and one the tree no longer has."""
    invented = _with_payload_fields(_c_direct_pair(), destination="node-hallucinated")
    assert _validate_c(invented)[0][0].reasons == (INVENTED_NODE,)
    assert _validate_c(invented)[0][0].outcome == REJECT
    absent = dataclasses.replace(_c_direct_pair(), frozen_absent_nodes=("node-legal",))
    assert _validate_c(absent)[0][0].reasons == (NODE_NOT_IN_FROZEN_TREE,)
    assert _validate_c(absent)[0][0].outcome == REJECT


def test_r56_a_real_folder_the_model_was_not_shown_is_refused_by_the_shortlist():
    """`104` R-56's second abstention mechanism, now that R-17 has a shortlist.

    R-56: "an abstention mechanism ... that does not depend on the model
    volunteering one (a structural 'none of these' option scored by the validator,
    OR THE DETERMINISTIC SHORTLIST REFUSING AN UNGROUNDED CHOICE)". Measured there:
    `qwen3:8b` produced zero abstentions on six should-abstain cases and the
    validator accepted two of its wrong placements.

    `node-legal-elsewhere` is a folder the frozen tree really has -- `node_exists`
    says so, which is what makes this different from
    `test_r15_a_destination_outside_the_frozen_tree_is_still_rejected` -- and it is
    not on the list this file's evidence reached. Before R-17 the vocabulary was
    every legal node, so this answer was ACCEPTED and the file moved into a folder
    no channel had connected it to.
    """
    elsewhere = _with_payload_fields(_c_direct_pair(),
                                     destination="node-legal-elsewhere")
    deps = _placement_deps(elsewhere)
    assert deps.node_exists("node-legal-elsewhere", "plan-1") is True
    assert "node-legal-elsewhere" not in elsewhere.dossier.allowed_vocabulary
    verdict = _validate_c(elsewhere)[0][0]
    assert verdict.reasons == (INVENTED_NODE,)
    assert verdict.outcome == REJECT
    assert verdict.may_propose is False


def test_r56_the_other_mechanism_is_none_and_it_costs_the_model_nothing():
    """The first of R-56's two, and the control for the test above.

    "none" is not a rejection: it is the abstention `00`:114 calls a successful
    outcome, and the drafts tell the model so ("`none` is a correct answer and it
    is recorded as one"). So the two mechanisms are distinguishable in the record
    -- a refused invention is `REJECT` with a reason, an abstention is `ABSTAIN`
    with none -- and a shortlist that refuses an ungrounded choice does not turn
    every uncertain file into a model error.
    """
    abstained = _with_payload_fields(_c_direct_pair(), destination="none")
    verdict = _validate_c(abstained)[0][0]
    assert verdict.outcome == ABSTAIN
    assert verdict.disposition == NO_SUPPORTED_DESTINATION
    assert verdict.reasons == ()


# --- R-56: a structural "none of these" at BOTH sites, scored by the validator ----
#
# "`qwen3:8b` (thinking off) produced zero abstentions on the six should-abstain
# cases at C and D under every wording tried". The answer `104` R-56 names is an
# abstention mechanism "that does not depend on the model volunteering one": a
# structural option in the SCHEMA that the validator scores. C has two -- the word
# `none` as a destination and the `unknown` claim shape -- and both are scored
# above. D has the same two, and one of them was not scored.


def _d_direct_pair():
    return next(p for p in SITE_D_OUTCOME_PAIRS if p.name == "direct_accept")


def _d_with_action(action, **fields):
    return _with_payload_fields(_d_direct_pair(), action=action, **fields)


def test_r56_site_d_scores_the_action_that_says_it_cannot_tell(monkeypatch):
    """The gap, and it was a placement.

    `abstain` is one of the response schema's three `no_target_actions`, so the
    model may take it without volunteering a word of prose -- and the validator
    walked past it: not in `_TARGET_ACTIONS`, so no target was checked, and no
    rewrite, so the claim kept the acceptance its citations earned. A model that
    said it could not tell was recorded as having chosen a residual destination,
    with `target` null underneath.

    Scored the way `mark_review_later` beside it is scored, and the disposition is
    `leave_in_place` because that is what an abstention at the residual site
    LEAVES: `00`:114's correct abstention is a successful outcome, not a rejection
    and not a move.
    """
    verdict = _validate_d(_d_with_action(ABSTAIN, target=None))[0][0]

    assert verdict.outcome == ABSTAIN
    assert verdict.disposition == LEAVE_IN_PLACE
    assert verdict.reasons == ()
    assert verdict.may_propose is False
    assert verdict.requires_review is False


def test_r56_the_unknown_claim_shape_abstains_at_both_sites():
    """The other structural option, and it is one shape for five sites: a claim
    carrying `unknown` and no citations is `ABSTAIN` in `validation.py` before any
    site validator runs, so no site can accidentally not have it."""
    for pairs, site in ((SITE_C_OUTCOME_PAIRS, C_PLACEMENT),
                        (SITE_D_OUTCOME_PAIRS, D_RESIDUAL)):
        pair = next(p for p in pairs if p.name == "unknown")
        assert pair.dossier.call_site == site
        verdict = (_validate_c(pair) if site == C_PLACEMENT
                   else _validate_d(pair))[0][0]
        assert verdict.outcome == ABSTAIN, site
        assert verdict.reasons == (), site
        assert verdict.may_propose is False, site


def test_r56_neither_sites_none_option_needs_the_model_to_volunteer_prose():
    """What "structural" means, asserted on the response schemas the model is
    actually shown rather than on the templates.

    At C the destination key's own description names the word; at D the abstention
    is a member of the action enum. Neither asks the model to say something in a
    free-text field that a validator then has to interpret -- which is the
    mechanism R-56 says does not work.
    """
    import json as _json

    import cli
    from llm_harness.prompt_library import draft_bytes
    from llm_harness.vocabulary import RESIDUAL_ACTIONS

    # The ids are READ from the one table that points a site at its text. A
    # literal here would be a second home for a value that moves -- B is on v2 in
    # this manifest and the wave named v3 -- and a test pinned to a stale id
    # asserts nothing about the schema the model is actually shown.
    _t, c_schema, _p = draft_bytes(cli.OBSERVE_TEMPLATE_ID[C_PLACEMENT])
    c_payload = _json.loads(c_schema)["$defs"]["payload"]["properties"]
    assert "none" in c_payload["destination"]["description"]

    _t, d_schema, _p = draft_bytes(cli.OBSERVE_TEMPLATE_ID[D_RESIDUAL])
    d_payload = _json.loads(d_schema)["$defs"]["payload"]["properties"]
    assert ABSTAIN in d_payload["action"]["enum"]
    assert ABSTAIN in RESIDUAL_ACTIONS


# --- R-104: "leave it here" is a decision, and it was recorded as a destination ---
#
# The twin of the gap above, one action along at the same site. `104` R-104:
# "`leave_in_current_location` at site D has the unscored fall-through `abstain`
# had: `_residual_site` returns `None` for it, so a model asking for the file to
# stay is recorded `accept_direct / residual_destination`."
#
# And it is NOT the abstention above. `abstain` is the model saying it cannot
# tell; `leave_in_current_location` is the model reading the evidence and
# concluding that where the file already sits is where it belongs. So this is
# scored as its own ACCEPTED outcome -- the citations still earn it -- and the
# disposition is the one the offline residual ladder has always used for the same
# choice (`placement/residual.py`: `LEAVE_IN_CURRENT_LOCATION: LEAVE_IN_PLACE`).
# Never `residual_destination`, which says the model named a home it did not
# name, and never `abstain`, which says it declined to answer.


def test_r104_leaving_the_file_where_it_is_is_not_a_residual_destination():
    """The gap itself, and it was a `target` of `None` under a destination.

    `leave_in_current_location` is not a member of `_TARGET_ACTIONS`, so no
    target was checked, and `_residual_site` returned `None`, so nothing rewrote
    the acceptance the citations earned. `_residual_disposition` then read
    `accept_direct` with an action that is not one of the two returns and reached
    for the only remaining branch it had: `residual_destination`.
    """
    verdict = _validate_d(_d_with_action(LEAVE_IN_CURRENT_LOCATION,
                                         target=None))[0][0]

    assert verdict.disposition == LEAVE_IN_PLACE
    assert verdict.disposition != RESIDUAL_DESTINATION
    assert verdict.outcome == ACCEPT_DIRECT
    assert verdict.outcome != ABSTAIN
    assert verdict.reasons == ()
    # Nothing follows a leave: `outcome_for_action` returns `(leave_in_place,
    # None)` and P12 builds a plan from `place` alone. `True` here would be P8
    # saying a move plan may follow a decision that moves nothing, which is what
    # `mark_review_later` and `abstain` beside it already answer `False`.
    assert verdict.may_propose is False


def test_r104_a_leave_that_rests_on_context_still_leaves_and_still_reviews():
    """The other accepted flavour, which had the other wrong disposition.

    A leave whose citations are `context_supported` was recorded
    `residual_destination_review` -- a destination again, and this time one
    queued for a person to confirm. The review is right and stays; the
    destination is the part that was never named.
    """
    pair = next(p for p in SITE_D_OUTCOME_PAIRS if p.name == "context_accept")
    verdict = _validate_d(_with_payload_fields(
        pair, action=LEAVE_IN_CURRENT_LOCATION, target=None))[0][0]

    assert verdict.outcome == ACCEPT_CONTEXT_SUPPORTED
    assert verdict.disposition == LEAVE_IN_PLACE
    assert verdict.disposition != RESIDUAL_DESTINATION_REVIEW
    assert verdict.requires_review is True


def test_r104_a_leave_is_scored_after_its_citations_like_any_accepted_claim():
    """Accepted does not mean unchecked, and this is why the fix is a disposition
    rather than an early return.

    `_residual_site`'s fall-through is what lets the four checks in front of it
    run: grounding at `check_citations`, the file-record check, the sensitivity
    policy and the stronger-relationship one. A leave that fails any of them is
    the rejection that check names, not a leave.
    """
    by_name = {pair.name: pair for pair in SITE_D_REASON_PAIRS}
    for name, expected in (
        (EVIDENCE_NOT_IN_FILE_RECORD, EVIDENCE_NOT_IN_FILE_RECORD),
        (SENSITIVITY_RESTRICTION_IGNORED, SENSITIVITY_RESTRICTION_IGNORED),
        (STRONGER_RELATIONSHIP_OVERLOOKED, STRONGER_RELATIONSHIP_OVERLOOKED),
    ):
        leaving = _with_payload_fields(
            by_name[name], action=LEAVE_IN_CURRENT_LOCATION, target=None)
        verdict = _validate_d(leaving)[0][0]
        assert verdict.outcome == REJECT, name
        assert verdict.reasons == (expected,), name
        assert verdict.disposition != LEAVE_IN_PLACE, name


def test_r104_the_three_answers_that_name_no_home_are_three_answers():
    """`leave_in_current_location`, `mark_review_later` and `abstain` are the
    schema's three `no_target_actions`, and after this fix each is recorded as
    itself. They were one record and two before: a destination, a review and a
    leave.
    """
    scored = {}
    for action in (LEAVE_IN_CURRENT_LOCATION, MARK_REVIEW_LATER, ABSTAIN):
        verdict = _validate_d(_d_with_action(action, target=None))[0][0]
        scored[action] = (verdict.outcome, verdict.disposition)

    assert scored[LEAVE_IN_CURRENT_LOCATION] == (ACCEPT_DIRECT, LEAVE_IN_PLACE)
    assert scored[MARK_REVIEW_LATER] == (WEAK, REVIEW_LATER)
    assert scored[ABSTAIN] == (ABSTAIN, LEAVE_IN_PLACE)
    assert len(set(scored.values())) == 3


def test_r15_no_site_c_fixture_puts_a_value_in_the_node_id_vocabulary():
    """The workaround R-15 forced, gone. `allowed_vocabulary` at C is node ids;
    a fixture that had to add `date-2026` to it to make a date pass was
    describing the defect, not the contract."""
    for pair in SITE_C_REASON_PAIRS + SITE_C_OUTCOME_PAIRS:
        assert all(node_id.startswith("node-")
                   for node_id in pair.dossier.allowed_vocabulary), pair.name

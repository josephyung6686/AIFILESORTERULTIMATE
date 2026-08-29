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
from llm_harness.records import P8Verdict, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    ACTION_NOT_IN_CONTROLLED_SET,
    BELOW_SUPPORT_THRESHOLD,
    CHOOSE_RESIDUAL_DESTINATION,
    C_PLACEMENT,
    D_RESIDUAL,
    DESTINATION_NOT_IN_FROZEN_TREE,
    EVIDENCE_NOT_IN_FILE_RECORD,
    GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN,
    INVENTED_FOLDER,
    LEAVE_IN_PLACE,
    MOVE_PLAN_ELIGIBLE,
    NODE_NOT_IN_FROZEN_TREE,
    NO_DESTINATION,
    NO_SUPPORTED_DESTINATION,
    REJECT,
    REJECTED,
    RESIDUAL_DESTINATION,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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
        release_audit_id=17,
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

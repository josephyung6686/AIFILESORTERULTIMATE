"""G-P8: P11's authorities against the real harness, end to end.

P8 ships, so this runs. It is the test that would fail if P11 ever grew a second
opinion about a Site C check, because it exercises P8's own recorded pairs
through P11's authorities rather than through P8's fixtures' own.
"""
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

import json

from database_agent.db import create_schema
from database_agent.files_table import record_file
from llm_harness.budgets import ScanBudget, create_budget_schema
from llm_harness.fixtures import FIXTURE_HANDLE_KEY, SITE_C_OUTCOME_PAIRS
from llm_harness.harness import CallDependencies, run_call
from llm_harness.placement_validation import (
    record_cd_verdict, revalidate_for_plan, validate_placement_response,
)
from llm_harness.records import (
    DossierRequest, EvidenceItem, P8Verdict, PromptDefinition,
    ValidationUnavailable,
)
from llm_harness.transport import ModelClient
from llm_harness import CallFailed, NeedsConsent, Refusal
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import C_PLACEMENT, DIRECT_ANCHOR
from evidence_shape.schema import create_evidence_schema
from privacy.classification_store import ClassificationStore
from privacy.gate import Gate
from privacy.items import Excerpt, TextSpan
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.schema import create_privacy_schema
from privacy.release import ModelCallRequest, ModelTarget, Target

from placement.config import SupportPolicy
from placement.records import Destination, MatchingFact
from placement.store import record_decision
from placement.versions import reproject
from placement.index import build_destination_index, legal_node_ids
from placement.p8_seam import (
    evidence_snapshot_id_for, placement_authorities, site_dependencies,
    snapshot_observation_keys,
)
from placement.schema import create_placement_schema
from placement.vocabulary import DIRECT
from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE, next_version
from p11.test_p11_records import _decision

POLICY = SupportPolicy(policy_id="integration-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.0, margin_threshold=0.0)


@pytest.fixture()
def p11_conn(conn):
    # `tests/p11/conftest.py` is not on this directory's fixture path, so the
    # database is built here the way every other integration test builds its own.
    create_schema(conn)
    # P8's tables, because `record_cd_verdict` is a real write and a seam test
    # against an absent table would prove nothing about the seam.
    create_llm_schema(conn)
    create_budget_schema(conn)
    create_privacy_schema(conn)
    create_evidence_schema(conn)
    create_placement_schema(conn)
    return conn


@pytest.fixture()
def indexed(p11_conn):
    build_destination_index(p11_conn, FROZEN_TREE,
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    return p11_conn


def _call_dependencies(conn, *, plan_version):
    return CallDependencies(
        proposal_class="placement", basis_key="f1->n-course",
        learning_scope="file", learning_subject_id="f1",
        evidence_resolver=lambda key: "span-1",
        site_dependencies=site_dependencies(placement=placement_authorities(
            conn, plan_version=plan_version, policy=POLICY,
            sensitivity_policy=lambda *_a, **_k: True)),
        contradicts=lambda *_a, **_k: False, unreduced_fits=True,
        summarized_fits=False, anchors_fit=False, split_shard_fits=(),
        split_shards=(),
        scan_budget=ScanBudget(scan_id="scan-p11", corpus_file_count=1000,
                               max_calls_per_1000_files=4,
                               max_estimated_cost=Decimal("10"),
                               min_calls_per_scan=0),
        estimated_cost=Decimal("1"), actual_cost=Decimal("1"),
        allowed_vocabulary=tuple(sorted(
            legal_node_ids(conn, plan_version=plan_version))),
        folder_levels=(), policy_version="policy-1",
        wire_handle_key=FIXTURE_HANDLE_KEY)


#: A real P7 release request. `DossierRequest` refuses anything else, which is
#: what makes this a binding against the live seam rather than a lookalike.
def _corpus_file(conn, directory):
    """A real P1 row. P7's gate resolves the target's content hashes from the
    files table, so a synthesized id would not reach the release at all."""
    directory.mkdir(parents=True, exist_ok=True)
    document = directory / "syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 PHYS1401")
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)


def _model_call_request(file_id="f1"):
    return ModelCallRequest(
        stage="placement", target=Target(file_ids=(file_id,)),
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        requested_items=(Excerpt(observation_key="obs-1",
                                 span=TextSpan(start=0, end=8),
                                 reason="anchor excerpt"),),
        prompt_template_id="template.placement",
        prompt_fingerprint="fp-canonical", max_dossier_tokens=4000)


#: Real injections. `run_call` type-checks the prompt and the model client, so
#: stand-ins would be rejected before P8 ever looked at the request -- and a test
#: that stopped there would prove nothing about the request P11 built.
def _prompt():
    return PromptDefinition(
        template_id="template.placement", template_bytes=b"TEMPLATE",
        response_schema_bytes=b'{"type":"object"}', call_site=C_PLACEMENT,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"authored"}')


def _model_client():
    return ModelClient(
        model_target=ModelTarget(locality="local", model_id="llama-local",
                                 provider="on-device"),
        invoke=lambda payload: b'{"claims": []}')


def _policy(conn):
    """A real P7 policy in force. The gate refuses to invent one, which is the
    behaviour P11's own Task 10 carry depends on."""
    return set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="hybrid",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=FIXED_CLOCK), component_version="P11-integration",
        user_id="joseph", reason="P11 P8-seam integration fixture")


def _gate(conn):
    """P7's real gate. P11 holds it and never calls `release` -- P8 does, inside
    `run_call`, which is the boundary this test exists to walk."""
    return Gate(
        conn, store=ClassificationStore(conn), plan_version="plan-1",
        classifier=lambda value, *, context_before=None, context_after=None: None,
        transform=lambda value, *, identifier_class: "[redacted]",
        unclassified_permits_local=False,
        scope_for=lambda file_id: "area-1", files_in_scope=lambda scope: (),
        component_version="P11-integration", now=lambda: FIXED_CLOCK,
        user_id="joseph")


def _request(*, evidence_snapshot_id, file_id="f1"):
    return DossierRequest(
        call_site=C_PLACEMENT, subject_ref=f"file:{file_id}:h1",
        eligibility_reason="several_legal_nodes_plausible",
        evidence_items=(EvidenceItem(
            evidence_ref="obs-1", kind="fact", location="page-1",
            excerpt_span=(0, 8), reliability_state="direct",
            basis="direct-anchor"),),
        conflicts=(), model_call_request=_model_call_request(file_id),
        plan_version="plan-1",
        evidence_snapshot_id=evidence_snapshot_id)


def test_a_c_verdict_binds_p11s_plan_version_and_snapshot(indexed):
    pair = SITE_C_OUTCOME_PAIRS[0]
    deps = placement_authorities(
        indexed, plan_version=pair.dossier.plan_version, policy=POLICY,
        sensitivity_policy=lambda *_a, **_k: True)
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-integration", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    verdict = result[0][0]
    assert isinstance(verdict, P8Verdict)
    record_cd_verdict(
        indexed, verdict, evidence_snapshot_id=pair.evidence_snapshot_id,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK)
    identity = indexed.execute(
        "SELECT plan_version, evidence_snapshot_id FROM llm_cd_plan_identity "
        "WHERE verdict_id = ?", (verdict.verdict_id,)).fetchone()
    assert identity["plan_version"] == pair.dossier.plan_version


def test_p11s_authorities_reach_the_real_run_call(indexed):
    """The seam bound end to end rather than by reference.

    `run_call` refuses a C request with no `evidence_snapshot_id` BEFORE the
    spend, so this drives P11's real bundle through P8's real entry point and
    lands on P8's own pre-call refusal. Nothing about it is a spy: the arguments
    are the ones `run_call` declares, and P8 is the one that answered.
    """
    from placement.p8_seam import call_placement

    result = call_placement(
        indexed, _request(evidence_snapshot_id=None),
        gate=_gate(indexed), model_client=_model_client(), prompt=_prompt(),
        call_dependencies=_call_dependencies(indexed, plan_version="plan-1"),
        observed_at=lambda: FIXED_CLOCK)
    assert isinstance(result, ValidationUnavailable)
    assert "evidence_snapshot_id" in result.missing


def test_the_snapshot_p11_mints_satisfies_p8s_pre_call_check(indexed, tmp_path):
    from placement.p8_seam import call_placement

    _policy(indexed)
    file_id = _corpus_file(indexed, tmp_path / "corpus")
    minted = evidence_snapshot_id_for(plan_version="plan-1",
                                      observation_keys=("obs-1",))
    result = call_placement(
        indexed, _request(evidence_snapshot_id=minted, file_id=file_id),
        gate=_gate(indexed), model_client=_model_client(), prompt=_prompt(),
        call_dependencies=_call_dependencies(indexed, plan_version="plan-1"),
        observed_at=lambda: FIXED_CLOCK)
    # The snapshot check is behind us: `run_call` went on to the eligibility,
    # reduction and release steps and came back with one of the five types it
    # declares. P7's gate refuses this unclassified fixture, which is P7's answer
    # and not P11's -- the point is that P11's bundle reached it.
    assert "evidence_snapshot_id" not in getattr(result, "missing", ())
    # It went the whole way: eligibility, reduction, and then P7's own
    # `Gate.release`, which refused an unclassified file in §8.4's own words.
    # That refusal is P7's answer, arrived at through P8, using P11's bundle --
    # and it is the same rule `placement.privacy` carries on the deterministic
    # side, reached here from the opposite direction.
    assert isinstance(result, Refusal), result
    assert result.denied.reason == "unclassified"


def _stored_verdict(conn, pair, *, snapshot=None):
    """A real P8 verdict in the table, produced by P8's own validator.

    `revalidate_for_plan` raises `KeyError` on a `previous_verdict_id` that is not
    in `llm_verdict`, so a synthesized id would never reach the revalidation at
    all and the test would prove nothing about the seam.

    `snapshot` names the id the verdict was RECORDED under, which the fixture's
    own literal cannot be for `104` R-155's two tests: they turn on whether the
    stored snapshot and the one P11 mints now are the same id, so the stored one
    has to be minted from a stated evidence set rather than from a constant that
    matches neither.
    """
    deps = placement_authorities(
        conn, plan_version=pair.dossier.plan_version, policy=POLICY,
        sensitivity_policy=lambda *_a, **_k: True)
    result = validate_placement_response(
        pair.dossier, pair.response_bytes,
        evidence_resolver=lambda key: "span-1" if key.startswith("obs-") else None,
        contradicts=lambda *_a, **_k: False, dependencies=deps,
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        dossier_builder="p11-integration", release_audit_id=17, handle_key=FIXTURE_HANDLE_KEY)
    verdict = result[0][0]
    return record_cd_verdict(
        conn, verdict,
        evidence_snapshot_id=(pair.evidence_snapshot_id if snapshot is None
                              else snapshot),
        model_id="fixture-model", prompt_fingerprint="fp-canonical",
        release_audit_id=17, observed_at=FIXED_CLOCK)


def _revalidation_inputs(pair, conn, *, verdict_id, plan_version):
    """Exactly the keywords `revalidate_for_plan` declares, and no others.

    P11 stores no `verdict_id`, dossier or response bytes -- `PlacementDecision`'s
    thirty fields carry none of them -- so they arrive from the caller that made
    the call. Binding them here is what proves the injected mapping is the live
    signature's and not a shape P11 invented.
    """
    return {
        "previous_verdict_id": verdict_id,
        "dossier": pair.dossier,
        "response_bytes": pair.response_bytes,
        "evidence_resolver": lambda key: ("span-1" if key.startswith("obs-")
                                          else None),
        "contradicts": lambda *_a, **_k: False,
        "dependencies": placement_authorities(
            conn, plan_version=plan_version, policy=POLICY,
            sensitivity_policy=lambda *_a, **_k: True),
        "model_id": "fixture-model",
        "prompt_fingerprint": "fp-canonical",
        "dossier_builder": "p11-integration",
        "release_audit_id": 17,
        # The key the dossier's bytes were built with: a re-validation reads the
        # model's references and needs the way back from what the model saw.
        "handle_key": FIXTURE_HANDLE_KEY,
        "observed_at": FIXED_CLOCK,
    }


def _v2_tree(*, rename_course_to=None, plan_version_id="plan-2", suffix="@2"):
    """plan-2, minted P10's way: every node gets a new id, lineage in origin.

    `plan_version_id` is named for `104` R-155's two tests, which re-project onto
    the version the FIXTURE DOSSIER carries (`plan-v1`) rather than onto a later
    one. `revalidate_for_plan` re-validates when the plan OR the snapshot has
    moved, so a test about the snapshot has to hold the plan version still, and
    the one it must hold it at is the dossier's own.
    """
    tree = next_version(plan_version_id=plan_version_id, suffix=suffix)
    if rename_course_to is None:
        return tree
    old_id = next(node.node_id for node in tree.nodes
                  if node.origin_node_id == "n-course")
    nodes = tuple(replace(node, node_id=rename_course_to)
                  if node.node_id == old_id else node for node in tree.nodes)
    profiles = tuple(replace(profile, node_id=rename_course_to)
                     if profile.node_id == old_id else profile
                     for profile in tree.profiles)
    return replace(
        tree, nodes=nodes, profiles=profiles,
        freeze_record=replace(
            tree.freeze_record,
            node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))


def _place_d1(conn, **overrides):
    record_decision(
        conn, _decision(decision_id="d1",
                        destination=Destination(node_id="n-course",
                                                node_role="ordinary"),
                        **overrides),
        component_version="P11-integration", observed_at=FIXED_CLOCK)


def test_p11_reuses_p8s_revalidation_rather_than_remapping_a_decision(indexed):
    # Done-means 16 and §8.8, driven end to end rather than by reference. P8
    # already appends a new verdict and supersedes the old one when the plan or
    # the snapshot changes; P11 calling this is what keeps "never silently
    # reclassify" true at the verdict layer too. The node here SURVIVES -- P10
    # minted it a new id and `reproject` followed the lineage -- so the only
    # remaining question is whether the model's judgement about it still holds,
    # and P8 is the one that answers.
    pair = SITE_C_OUTCOME_PAIRS[0]
    assert pair.expected_outcome == "accept_direct"
    verdict_id = _stored_verdict(indexed, pair)
    _place_d1(indexed)
    node_id = pair.dossier.allowed_vocabulary[0]
    build_destination_index(indexed, _v2_tree(rename_course_to=node_id),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    before = indexed.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"]
    diff = reproject(
        indexed, from_plan_version="plan-1", to_plan_version="plan-2",
        revalidation_inputs={"d1": _revalidation_inputs(
            pair, indexed, verdict_id=verdict_id, plan_version="plan-2")})
    assert diff.carried_unchanged == ("d1",)
    assert diff.requiring_renewed_review == ()
    # P8 really ran: it wrote the fresh verdict itself, stamped with the new plan
    # version. P11 records no verdict of its own, so a second row here would be
    # P11 writing P8's fact twice.
    after = indexed.execute(
        "SELECT plan_version FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::plan-2::" + evidence_snapshot_id_for(
            plan_version="plan-2", observation_keys=("obs-1",)),)).fetchone()
    assert after["plan_version"] == "plan-2"
    assert indexed.execute(
        "SELECT count(*) AS c FROM llm_verdict").fetchone()["c"] == before + 1


def test_a_surviving_node_whose_verdict_no_longer_holds_goes_back_to_the_user(
        indexed):
    # The negative twin, and the half that makes the test above discriminating.
    # The lineage check passes identically -- `n-course` still has a successor in
    # plan-2 -- but the destination the model named is not in the new legal set,
    # so P8's own NODE_NOT_IN_FROZEN_TREE fires and the decision is marked rather
    # than carried. A `_revalidates` that returned True unconditionally would pass
    # the test above and fail here.
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict_id = _stored_verdict(indexed, pair)
    _place_d1(indexed)
    build_destination_index(indexed, _v2_tree(),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    assert pair.dossier.allowed_vocabulary[0] not in legal_node_ids(
        indexed, plan_version="plan-2")
    diff = reproject(
        indexed, from_plan_version="plan-1", to_plan_version="plan-2",
        revalidation_inputs={"d1": _revalidation_inputs(
            pair, indexed, verdict_id=verdict_id, plan_version="plan-2")})
    assert diff.requiring_renewed_review == ("d1",)
    assert diff.carried_unchanged == ()
    # Marked, not remapped: the plan-1 row is untouched and nothing names the
    # surviving lookalike.
    row = indexed.execute(
        "SELECT node_id, superseded_by FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert (row["node_id"], row["superseded_by"]) == ("n-course", None)


def test_a_decision_with_no_model_verdict_needs_no_revalidation(indexed):
    # `revalidation_inputs` is SPARSE on purpose: a deterministic decision has no
    # P8 verdict, so there is nothing to re-validate and the node's survival is
    # the whole question. An empty mapping must not read as "every verdict
    # failed", which would send a clean corpus back to the user wholesale.
    _place_d1(indexed)
    build_destination_index(indexed, _v2_tree(),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    diff = reproject(indexed, from_plan_version="plan-1",
                     to_plan_version="plan-2")
    assert diff.carried_unchanged == ("d1",)


# --- `104` R-155: one snapshot, minted from what the dossier carried ----------------

#: The address `_judge_with_model` mints, spelled with the two functions it mints it
#: with. Retyping the derivation here would let this file agree with a defect: the
#: whole row is that there were two spellings of "what did the model see", so the
#: test asks the one the pipeline asks.
def _items_snapshot(pair, *, plan_version: str) -> str:
    return evidence_snapshot_id_for(
        plan_version=plan_version,
        observation_keys=snapshot_observation_keys(pair.dossier.evidence_items))


def _moved_fact() -> tuple:
    """A settled fact whose citation is NOT one the dossier carried.

    `obs-9` resolves to nothing in this database, which is the point: P11's own
    address for a fact is not a citation the model was offered (`104` R-154), so a
    snapshot built from it addresses a set the dossier never had.
    """
    return (MatchingFact(file_fact_id="ff9", field="subject", value="PHYS9999",
                         reliability=DIRECT, evidence_ref="obs-9"),)


def _verdict_count(conn) -> int:
    return conn.execute("SELECT count(*) AS c FROM llm_verdict").fetchone()["c"]


def test_the_revalidation_snapshot_addresses_the_items_and_not_the_facts(indexed):
    """`104` R-155, the second half of `test_the_snapshot_addresses_the_items_and_
    not_the_facts` in `tests/p11/test_p11_pipeline.py`.

    That test pins the ORIGINAL snapshot to the dossier's items; this pins the
    REVALIDATION snapshot to the same items through the same function, which is
    what makes the two ids comparable at all. Keyed on the matched facts, this
    path addressed a set the dossier never carried -- so the id it compared
    against the stored one differed for a reason that had nothing to do with what
    the model saw.

    The decision's fact cites `obs-9` and the dossier carries `obs-1`, so the two
    derivations cannot agree by accident here.
    """
    pair = SITE_C_OUTCOME_PAIRS[0]
    verdict_id = _stored_verdict(indexed, pair)
    _place_d1(indexed, matching_facts=_moved_fact())
    build_destination_index(indexed,
                            _v2_tree(rename_course_to=pair.dossier.allowed_vocabulary[0]),
                            component_version="P11-integration",
                            observed_at=FIXED_CLOCK)
    diff = reproject(
        indexed, from_plan_version="plan-1", to_plan_version="plan-2",
        revalidation_inputs={"d1": _revalidation_inputs(
            pair, indexed, verdict_id=verdict_id, plan_version="plan-2")})

    assert diff.carried_unchanged == ("d1",)
    # P8 stamps the fresh verdict with the snapshot P11 handed it, so the verdict
    # id IS the answer to "which set did P11 address".
    assert indexed.execute(
        "SELECT plan_version FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::plan-2::"
         + _items_snapshot(pair, plan_version="plan-2"),)
    ).fetchone()["plan_version"] == "plan-2"
    # And the facts' own address named nothing. This is the assertion the old
    # spelling failed: it minted `snap-<hash of obs-9>` and stamped it here.
    assert indexed.execute(
        "SELECT 1 FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::plan-2::" + evidence_snapshot_id_for(
            plan_version="plan-2", observation_keys=("obs-9",)),)).fetchone() is None


def _index_the_dossiers_own_version(conn, pair) -> str:
    """A tree at the plan version the fixture dossier carries, lineage preserved.

    Built BEFORE the verdict is stored, because `_stored_verdict` runs P8's real
    validator against this version: with no index at it, every node the response
    names is absent and the stored verdict is a REJECT, which a short-circuiting
    re-validation would then read back as "the judgement no longer holds" for a
    reason that is the fixture's and not the snapshot's.
    """
    plan = pair.dossier.plan_version
    build_destination_index(
        conn, _v2_tree(rename_course_to=pair.dossier.allowed_vocabulary[0],
                       plan_version_id=plan, suffix="@v1"),
        component_version="P11-integration", observed_at=FIXED_CLOCK)
    return plan


def _reprojected_onto_the_dossiers_own_version(conn, pair, *, verdict_id,
                                               inputs_pair=None):
    """`reproject` with the plan version HELD STILL, which is the only shape in
    which the snapshot is observable.

    `revalidate_for_plan` returns the stored verdict only when the plan version
    AND the snapshot both match what was recorded; with two plan versions the
    version alone forces a re-validation and the snapshot term contributes
    nothing a test can see. So the version this projects onto is the one the
    dossier -- and therefore the recorded verdict -- already carries.
    """
    plan = pair.dossier.plan_version
    return reproject(
        conn, from_plan_version="plan-1", to_plan_version=plan,
        revalidation_inputs={"d1": _revalidation_inputs(
            inputs_pair or pair, conn, verdict_id=verdict_id, plan_version=plan)})


def test_a_dossier_whose_items_changed_revalidates(indexed):
    """A reading added to the dossier is a change, and it fires.

    `104` R-155's first direction. The facts are UNCHANGED and the dossier gained
    an item, which is exactly the case the old spelling missed: it hashed the
    facts, saw the same id as the stored one, and carried a verdict about a
    dossier the model would no longer recognise.
    """
    pair = SITE_C_OUTCOME_PAIRS[0]
    plan = _index_the_dossiers_own_version(indexed, pair)
    # The verdict was recorded when the dossier carried one reading.
    verdict_id = _stored_verdict(indexed, pair,
                                 snapshot=_items_snapshot(pair, plan_version=plan))
    _place_d1(indexed)
    widened = replace(pair, dossier=replace(
        pair.dossier,
        evidence_items=pair.dossier.evidence_items + (
            EvidenceItem(evidence_ref="obs-2", kind="excerpt", location="body",
                         excerpt_span=(0, 6), reliability_state=DIRECT,
                         basis=DIRECT_ANCHOR),)))
    before = _verdict_count(indexed)

    diff = _reprojected_onto_the_dossiers_own_version(
        indexed, pair, verdict_id=verdict_id, inputs_pair=widened)

    assert diff.carried_unchanged == ("d1",)
    # It really re-validated: P8 appended a verdict of its own, stamped with the
    # id minted from the WIDER item set.
    assert _verdict_count(indexed) == before + 1
    assert indexed.execute(
        "SELECT 1 FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::{plan}::"
         + _items_snapshot(widened, plan_version=plan),)).fetchone() is not None


def test_a_dossier_whose_facts_changed_and_items_did_not_does_not_revalidate(indexed):
    """The negative twin, and the direction that cost a model call for nothing.

    Same held plan version, same stored snapshot minted from the dossier's items.
    The decision's fact now cites a different observation and the dossier is
    untouched -- so nothing the model saw has moved, `revalidate_for_plan`
    recognises the stored verdict, and no second verdict is written.

    Under the old spelling the fact's address WAS the snapshot, so this wrote a
    fresh verdict and superseded a sound one: a re-validation fired by a change
    the dossier never carried.
    """
    pair = SITE_C_OUTCOME_PAIRS[0]
    plan = _index_the_dossiers_own_version(indexed, pair)
    verdict_id = _stored_verdict(indexed, pair,
                                 snapshot=_items_snapshot(pair, plan_version=plan))
    _place_d1(indexed, matching_facts=_moved_fact())
    before = _verdict_count(indexed)

    diff = _reprojected_onto_the_dossiers_own_version(
        indexed, pair, verdict_id=verdict_id)

    assert diff.carried_unchanged == ("d1",)
    assert _verdict_count(indexed) == before
    assert indexed.execute(
        "SELECT 1 FROM llm_verdict WHERE verdict_id = ?",
        (f"{verdict_id}::{plan}::" + evidence_snapshot_id_for(
            plan_version=plan, observation_keys=("obs-9",)),)).fetchone() is None

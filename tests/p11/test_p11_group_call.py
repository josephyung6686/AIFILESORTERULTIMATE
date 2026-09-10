"""§6.8 and `00`:112: ONE model call takes the group, and the members follow it.

`104` §18.2 gap 14. Before this, `place_group` placed every member singly and read
the parent off the results -- while its own comment claimed the reverse -- so a
family of files that belongs together was judged one file at a time with none of
them seeing the others, and the group's home was whatever the majority of single
placements happened to land on.

Every seam here is the live one: P1's `files` rows, P7's `ClassificationStore` and
`current_policy`, P9's own group writers and acceptance read, P10's frozen tree,
`placement.retrieval.retrieve`, `placement.scoring.assess`, and the real
append-only decision table. The one fake is `call_placement_steps`, monkeypatched so a
site-C verdict can be forced without a live model -- the same fake and the same
reason as `test_p11_pipeline.py`.

**THE FILES ARE REAL P1 ROWS AND THE GROUP IS BUILT AROUND THEM**, rather than
`p9_fixtures`' synthesised ids. §8.4's protected arm resolves a content hash by
file id through P7's own `may_move_automatically`, so a member with no `files`
row cannot be protected at all -- and "one protected member withholds the group
call" is precisely the measurement this file exists to make.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from database_agent.budget import set_ceiling
from facts.states import VALIDATED
from grouping.acceptance import record_acceptance
from grouping.records import (
    AnchorFact, Conflict, Group, GroupAcceptance, Membership, Support,
)
from grouping.store import record_group, record_membership
from grouping.vocabulary import (
    ACCEPTED, COHERENT, CONTEXT_SUPPORTED as GROUP_CONTEXT, DIRECT_ANCHOR,
    ENGINE, ENGINE_FLAGGED, INCLUDED, NOT_FLAGGED, NO_SENSITIVITY,
    PENDING_REVIEW, RULES, SHARED_VALIDATED_FACT, STRONGLY_IDENTIFIED_FILE,
    SUPPORTED, USER, USER_ATTACHED,
)
from llm_harness.budgets import create_budget_schema
from llm_harness.records import EvidenceItem, P8Verdict
from llm_harness.schema import create_llm_schema
from llm_harness.vocabulary import (
    ABSTAIN as P8_ABSTAIN, ACCEPT_CONTEXT_SUPPORTED,
    NO_SUPPORTED_DESTINATION as P8_NO_SUPPORTED_DESTINATION,
    VALID_REVIEW_REQUIRED,
)
from privacy.release import ModelTarget

from placement import vocabulary as v
from placement.config import CEILINGS
from placement.index import build_destination_index
from placement.records import MatchingFact

from p11.conftest import FIXED_CLOCK
from p11.p10_fixtures import FROZEN_TREE
from p11.test_p11_pipeline import (
    LOCAL_TARGET, _call_dependencies, _classify, _inputs, _policy, _real_file,
)

GROUP_ID: str = "g-packet"

#: The three related files the design sentence is about, and the fourth P9 itself
#: flagged as an outlier. `00`:112's packet, in miniature.
TOGETHER: tuple[str, ...] = ("essay", "transcript", "scan")
FLAGGED: str = "duke"
NAMES: tuple[str, ...] = TOGETHER + (FLAGGED,)

CLOUD_TARGET = ModelTarget(locality="cloud", model_id="cloud-judge",
                           provider="provider")

T0 = "2026-08-27T00:00:00Z"


def _obs(file_id: str) -> str:
    """One observation key per member, so "the dossier lists all three" is a
    measurement over three distinct addresses rather than over one shared one."""
    return f"obs-{file_id}"


def _seed_group(conn, ids: dict) -> None:
    """P9's own records for a four-file packet, through P9's own writers.

    Modelled on `p11/p9_fixtures.py` and for its reason: a shape change in P9
    breaks this at import. What differs is that the members are REAL P1 file ids,
    because §8.4's protected arm resolves a content hash by file id.
    """
    essay = ids["essay"][0]
    transcript = ids["transcript"][0]
    record_group(conn, Group(
        group_id=GROUP_ID, seed_ref="seed-1",
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject = PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401",
            file_ids=(essay, transcript), reliability_state=VALIDATED,
            observation_key=_obs(essay),
            observation_keys=(_obs(essay), _obs(transcript))),),
        pre_model_signals={}, anchor_count=2, coherence_verdict=COHERENT,
        coherence_citations=(_obs(essay),),
        group_category="college_applications",
        display_label="PHYS1401 packet", label_source=ENGINE, conflicts=(),
        stop_rule_hits=(), state=SUPPORTED, sensitivity_state=NO_SENSITIVITY,
        dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
        created_by=RULES, created_at=T0))
    bases = {"essay": DIRECT_ANCHOR, "transcript": GROUP_CONTEXT,
             "scan": USER_ATTACHED, "duke": DIRECT_ANCHOR}
    for name in NAMES:
        file_id, content_hash = ids[name]
        flagged = name == FLAGGED
        record_membership(conn, Membership(
            membership_id=f"m-{file_id}", group_id=GROUP_ID, file_id=file_id,
            content_hash=content_hash, basis=bases[name], decision=INCLUDED,
            decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=_obs(file_id),
                             quote_or_field="subject", location="body",
                             edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=((Conflict(kind="subject",
                                 competing_values=("PHYS1401", "PHYS1402"),
                                 file_ids=(file_id,)),) if flagged else ()),
            outlier_flag=ENGINE_FLAGGED if flagged else NOT_FLAGGED,
            validation_verdict_ref=None, created_at=T0))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id="acc-1", plan_version_id="plan-1", group_id=GROUP_ID,
        membership_id=None, acceptance=ACCEPTED, review_state=PENDING_REVIEW,
        user_edited_label=None, aliases=(), review_decision_ref=None,
        decided_by=USER, created_at=T0))


@pytest.fixture()
def seed(p11_conn, tmp_path):
    """The corpus, with each member's P7 state stated rather than patched later.

    A classification is superseded and never removed (§8.2), so a test that wants
    a protected or an unclassified member says so HERE -- writing a second record
    afterwards leaves two live rows and P7 refuses to read them, and deleting one
    is refused by a trigger. Which is right: the point of both is that P7's answer
    about a file is a record, not a switch.
    """
    def build(*, protected: tuple[str, ...] = (),
              unclassified: tuple[str, ...] = ()) -> SimpleNamespace:
        create_llm_schema(p11_conn)
        create_budget_schema(p11_conn)
        for key in CEILINGS.values():
            set_ceiling(p11_conn, key, 8)
        ids = {
            name: _real_file(p11_conn, tmp_path / "corpus", name=f"{name}.pdf",
                             body=b"%PDF-1.4 " + name.encode())
            for name in NAMES
        }
        for name in NAMES:
            if name in unclassified:
                continue
            file_id, content_hash = ids[name]
            _classify(p11_conn, file_id=file_id, content_hash=content_hash,
                      protected=name in protected,
                      handling_class=("sensitive_personal" if name in protected
                                      else "personal_non_sensitive"))
        _policy(p11_conn)
        build_destination_index(p11_conn, FROZEN_TREE,
                                component_version="P11-test",
                                observed_at=FIXED_CLOCK)
        _seed_group(p11_conn, ids)
        return SimpleNamespace(
            conn=p11_conn, ids=ids,
            file_id={name: ids[name][0] for name in NAMES},
            ref={name: f"{v.FILE}:{ids[name][0]}:{ids[name][1]}"
                 for name in NAMES})
    return build


@pytest.fixture()
def seeded(seed):
    return seed()


def _member_evidence(value: str):
    """One member's accepted fact and the item that addresses it."""
    def build(file_id: str) -> dict:
        return dict(
            facts=(MatchingFact(file_fact_id=f"ff-{file_id}", field="subject",
                                value=value, reliability=v.DIRECT,
                                evidence_ref=_obs(file_id)),),
            evidence_items=(EvidenceItem(
                evidence_ref=_obs(file_id), kind="fact", location="page-1",
                excerpt_span=(0, 8), reliability_state="direct",
                basis="direct-anchor"),),
            group_ids=(GROUP_ID,), curated_folder_labels=(),
            semantic_neighbours=(), related_files=(),
            entity_frequency={value: 6}, generic_entity_frequency=200)
    return build


def _evidence_for(contradicting: str | None = None):
    """`evidence_for`, per member. One member may be given the rival course code,
    which §6.3 suppresses `n-course` on -- the product's own contradiction, not a
    second comparison written for this test."""
    agrees = _member_evidence("PHYS1401")
    disagrees = _member_evidence("PHYS1402")

    def evidence_for(file_id: str) -> dict:
        return (disagrees(file_id) if file_id == contradicting
                else agrees(file_id))
    return evidence_for


def _verdict(node_id: str) -> P8Verdict:
    """A verdict whose `claim_ref` names the node, so `chosen_node_of` can read
    one answer per call instead of every call producing the same destination."""
    return P8Verdict(
        verdict_id=f"vd-{node_id}", dossier_id="ds-1",
        claim_ref=f"claim-{node_id}", outcome=ACCEPT_CONTEXT_SUPPORTED,
        disposition=VALID_REVIEW_REQUIRED, reasons=(), may_propose=True,
        requires_review=True, citations_checked=(), scope="file",
        validator_version="1", policy_version="policy-1", plan_version="plan-1")


def _abstaining_verdict() -> P8Verdict:
    return P8Verdict(
        verdict_id="vd-none", dossier_id="ds-none", claim_ref="claim-none",
        outcome=P8_ABSTAIN, disposition=P8_NO_SUPPORTED_DESTINATION,
        reasons=(), may_propose=False, requires_review=False,
        citations_checked=(), scope="file", validator_version="1",
        policy_version="policy-1", plan_version="plan-1")


def _request_builder(target: ModelTarget = LOCAL_TARGET):
    """A real P7 release request, for a file OR a group.

    `DossierRequest` refuses anything else, so this is a binding against the live
    seam -- and the group arm is the shape `104` §18.2 gap 14 added: every member
    named in `Target.file_ids`, and the destination P11's gate already admitted
    for all of them rather than one re-derived here.
    """
    from privacy.items import Excerpt, TextSpan
    from privacy.release import ModelCallRequest, Target

    def build(*, subject_ref, evidence_items, max_dossier_tokens,
              member_file_ids=(), model_target=None):
        if member_file_ids:
            files = tuple(member_file_ids)
            group_id = subject_ref.partition(":")[2]
        else:
            files, group_id = (subject_ref.split(":")[1],), None
        return ModelCallRequest(
            stage="placement",
            target=Target(file_ids=files, group_id=group_id),
            model_target=model_target or target,
            requested_items=tuple(
                Excerpt(observation_key=item.evidence_ref,
                        span=TextSpan(start=0, end=8), reason="anchor excerpt")
                for item in evidence_items),
            prompt_template_id="template.placement",
            prompt_fingerprint="fp-canonical",
            max_dossier_tokens=max_dossier_tokens)
    return build


def _model_inputs(conn, **overrides):
    values = dict(
        gate=object(), model_client=object(),
        prompt=SimpleNamespace(ratified=True),
        residual_prompt=SimpleNamespace(ratified=True),
        call_dependencies=_call_dependencies(),
        model_call_request=_request_builder(),
        chosen_node_of=lambda verdict: verdict.claim_ref[len("claim-"):],
        sensitivity_policy=lambda *_a, **_k: True,
        model_target=LOCAL_TARGET)
    values.update(overrides)
    return _inputs(conn, **values)


def _place_group(world, *, inputs=None, evidence_for=None, monkeypatch=None,
                 answers=None, verdict_for=None):
    """`place_group` with `call_placement_steps` faked. Returns (plan, calls).

    `answers` maps a `subject_ref` to the node its call names; anything unlisted
    gets `n-course`. `calls` is every request the fake saw, in order, so a test
    can measure HOW MANY calls a group cost as well as what they carried.
    """
    import placement.pipeline as pipeline

    calls: list = []
    answers = answers or {}

    def _fake(conn_, request, **kwargs):
        # `104` §18.15 made the placement call a generator whose one `yield` is
        # the socket; `place_group` reaches it as `call_placement_steps`. The
        # fake is a generator too -- it yields nothing (no socket) and RETURNS
        # the verdict, which is what `drive_inline` and the lane both read.
        calls.append((request, kwargs))
        if verdict_for is not None:
            return verdict_for(request)
        return _verdict(answers.get(request.subject_ref, "n-course"))
        yield  # pragma: no cover -- makes this a generator; never reached

    monkeypatch.setattr(pipeline, "call_placement_steps", _fake)
    plan = pipeline.place_group(
        world.conn, group_id=GROUP_ID,
        inputs=inputs if inputs is not None else _model_inputs(world.conn),
        evidence_for=evidence_for or _evidence_for(),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    return plan, calls


def _group_calls(calls):
    return [request for request, _kwargs in calls
            if request.subject_ref.startswith(f"{v.GROUP}:")]


def _stored(conn, decision):
    row = conn.execute(
        "SELECT payload FROM placement_decisions WHERE record_id = ?",
        (decision.decision_id,)).fetchone()
    return json.loads(row["payload"])


# --- the design sentence: one call, and the group is its subject ------------------


def test_a_group_of_related_files_is_one_call_whose_dossier_lists_them_all(
        seeded, monkeypatch):
    """`00`:112 -- "related files often explain one another more accurately when
    considered together than when classified independently" -- and `104` §18.2
    gap 14's measurement of its absence: "no model call ever takes a group".

    MEASURED: exactly one site-C request whose `subject_ref` is the GROUP, whose
    release target names every member, and whose dossier carries every member's
    own evidence key. Before this, the number of group-subject calls was zero for
    every group in every run.
    """
    _plan, calls = _place_group(seeded, monkeypatch=monkeypatch)
    group_requests = _group_calls(calls)
    assert len(group_requests) == 1
    request = group_requests[0]
    assert request.subject_ref == f"{v.GROUP}:{GROUP_ID}"
    # The RELEASE names every member: the dossier carries their evidence, so a
    # target naming fewer would authorise less than the call sends.
    assert set(request.model_call_request.target.file_ids) == set(
        seeded.file_id.values())
    assert request.model_call_request.target.group_id == GROUP_ID
    # And the dossier lists them: one address per member, all of them present.
    carried = {item.evidence_ref for item in request.evidence_items}
    for name in NAMES:
        assert _obs(seeded.file_id[name]) in carried, name


def test_a_group_whose_members_carry_typed_edges_still_gets_its_call(
        seeded, monkeypatch):
    """SABOTAGE: the group call builds a node-local graph. It must not.

    `placement.graph` refuses a group subject BY NAME -- every `GraphAnchor`
    names the file the edge came from, and "a group subject has no single
    originating file and fails here by name rather than storing one". A packet of
    four files has four originating files and no one of them is the anchor's. So
    the group's call builds no graph, and the ranking is the same arithmetic over
    the same channels either way.

    Without this pin the defect is invisible: every other test in this file runs
    with `related_files=()`, which never reaches the anchor construction, so the
    FIRST real corpus with a group whose members share a typed edge would raise
    inside the group call and take the whole group down to the fallback.
    """
    edges = ({"edge_type": "shared_validated_fact", "to_file_id": "f-syllabus",
              "entity": "PHYS1401", "anchor_file_id": "f-syllabus",
              "weight": 1},)
    agrees = _member_evidence("PHYS1401")

    def evidence_for(file_id: str) -> dict:
        return dict(agrees(file_id), related_files=edges)

    plan, calls = _place_group(seeded, monkeypatch=monkeypatch,
                               evidence_for=evidence_for)
    assert len(_group_calls(calls)) == 1
    assert plan.shared_parent_node_id == "n-course"
    # And a single FILE with the same edges still gets its graph: the refusal is
    # about the group subject, not about graphs.
    assert any(d.group_support is not None for d in plan.member_decisions)


def test_the_members_are_placed_from_the_groups_answer_and_ask_nothing_of_their_own(
        seeded, monkeypatch):
    """§6.8's own sentence, made true: "confirm the shared parent FIRST, then
    classify members beneath it". The members go where the group's call said, the
    plan's shared parent IS that answer rather than a coincidence read off the
    members, and no member costs a second call.

    MEASURED: three members on `n-course`, `shared_parent_node_id == n-course`,
    and NOT ONE of those three costs a question of its own -- the only per-file
    call in the pass is the member P9 had already set apart.
    """
    plan, calls = _place_group(seeded, monkeypatch=monkeypatch)
    assert plan.shared_parent_node_id == "n-course"
    assert {d.subject.file_id for d in plan.member_decisions} == {
        seeded.file_id[name] for name in TOGETHER}
    for decision in plan.member_decisions:
        assert decision.destination.node_id == "n-course"
    # A member whose own evidence does not contradict the group's folder has
    # already been answered about, in the one call that took the group.
    per_file = [request.subject_ref for request, _kwargs in calls
                if not request.subject_ref.startswith(f"{v.GROUP}:")]
    assert per_file == [seeded.ref[FLAGGED]]
    assert len(_group_calls(calls)) == 1


def test_a_member_placed_by_its_group_says_the_model_decided_and_names_the_group(
        seeded, monkeypatch):
    """`104` R-165's distinction has to survive the new route: `placed by =
    model / rule / user` stays true, and the group's answer IS the model's.
    `00`:114's `group_support` gains its first writer -- gap 14 measured it "null
    at every writer".

    READ OFF THE STORED BODY and not the returned object, for R-165's own reason:
    the defect was that the pipeline knew and nothing downstream could read it.
    """
    plan, _calls = _place_group(seeded, monkeypatch=monkeypatch)
    for decision in plan.member_decisions:
        body = _stored(seeded.conn, decision)
        assert body["decided_by"] == v.DECIDED_BY_MODEL
        assert body["group_support"]["group_id"] == GROUP_ID
        assert body["group_plan_id"] == plan.group_plan_id
        # The person is told which question was answered about their file.
        assert GROUP_ID in body["explanation"]


def test_a_member_the_grouping_flagged_never_claims_the_groups_support(
        seeded, monkeypatch):
    """One record cannot say a file was placed by its group AND that the plan
    excluded it as an outlier. `GroupPlan` already refuses the second half --
    "one presentation cannot say a file was placed with the group and left out of
    it" -- and this is the same sentence about the ROW.

    P9's `outlier_flag` is read, never re-derived: a member it flagged is judged
    on its own with the group's folder offered, exactly as a member that
    contradicts the answer is, because it is the same situation reached from P9's
    evidence instead of from this file's.
    """
    plan, calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        answers={seeded.ref[FLAGGED]: "n-course-alt"})
    flagged = seeded.file_id[FLAGGED]
    assert [o.file_id for o in plan.excluded_outliers] == [flagged]
    assert flagged not in {d.subject.file_id for d in plan.member_decisions}
    # It was asked its own question, and the group's folder was on the list.
    own = [(request, kwargs) for request, kwargs in calls
           if request.subject_ref == seeded.ref[FLAGGED]]
    assert len(own) == 1
    assert "n-course" in own[0][1]["call_dependencies"].allowed_vocabulary
    stored = seeded.conn.execute(
        "SELECT payload FROM placement_decisions WHERE subject_ref = ? "
        "AND superseded_by IS NULL", (seeded.ref[FLAGGED],)).fetchone()
    body = json.loads(stored["payload"])
    assert body["group_support"] is None
    assert "set apart from" in body["explanation"]


# --- the outlier: offered the group's folder, judged on its own -------------------


def test_a_contradicting_member_is_placed_singly_with_the_groups_folder_offered(
        seeded, monkeypatch):
    """`00`:112's worked example: "It can identify that a Duke essay is an
    outlier because of its conflicting target-institution fact, exclude it from
    the Columbia packet, and route it to a separate legal branch."

    The contradiction is §6.3's own suppression -- this member states the rival
    course code, so the group's folder is among the nodes its own values ruled
    out -- and P11 writes no second comparison of facts against a node.

    MEASURED: the member gets a call of its own; the group's folder is ON that
    call's `allowed_vocabulary` (offered, not forced); the member lands where its
    own call said; its row carries no `group_support`; and the explanation says
    the disagreement.
    """
    scan = seeded.file_id["scan"]
    plan, calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        evidence_for=_evidence_for(contradicting=scan),
        answers={seeded.ref["scan"]: "n-course-alt"})
    assert len(_group_calls(calls)) == 1
    own = [(request, kwargs) for request, kwargs in calls
           if request.subject_ref == seeded.ref["scan"]]
    assert len(own) == 1, "the member that disagreed is asked its own question"
    # OFFERED. `00`'s amendment: deterministic rules rank and shortlist, they do
    # not delete -- the folder the group chose is on the list the model reads.
    assert "n-course" in own[0][1]["call_dependencies"].allowed_vocabulary
    outlier = next(d for d in plan.member_decisions if d.subject.file_id == scan)
    assert outlier.destination.node_id == "n-course-alt"
    assert outlier.group_support is None
    assert "rule out the folder its group" in outlier.explanation


def test_the_other_members_still_follow_the_group_when_one_of_them_disagrees(
        seeded, monkeypatch):
    """The discriminating twin. Without it the test above could be passing
    because the group's answer stopped reaching anybody."""
    scan = seeded.file_id["scan"]
    plan, _calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        evidence_for=_evidence_for(contradicting=scan),
        answers={seeded.ref["scan"]: "n-course-alt"})
    went = {d.subject.file_id for d in plan.member_decisions
            if d.group_support is not None}
    assert went == {seeded.file_id["essay"], seeded.file_id["transcript"]}


# --- the fallbacks: an abstention, and the gate -----------------------------------


def test_a_group_that_abstains_falls_back_to_the_per_member_placement(
        seeded, monkeypatch):
    """`00`: correct abstention is a successful outcome. An abstention about the
    GROUP is not an abstention about its members -- each is asked its own
    question, exactly as it was before this call existed -- and the shared parent
    goes back to `confirm_shared_parent`'s reading of those results.

    MEASURED: no member carries `group_support`, every member still reaches its
    home, and every member's row says the rules or its own call decided.
    """
    plan, calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        verdict_for=lambda request: (
            _abstaining_verdict() if request.subject_ref.startswith(f"{v.GROUP}:")
            else _verdict("n-course")))
    assert len(_group_calls(calls)) == 1
    assert all(d.group_support is None for d in plan.member_decisions)
    assert {d.destination.node_id for d in plan.member_decisions} == {"n-course"}
    assert plan.shared_parent_node_id == "n-course"


def test_one_protected_member_withholds_the_group_call_altogether(
        seed, monkeypatch):
    """§8.4, over a subject that is not one file: the group dossier is released
    only if EVERY member's release is permitted for the target. The standing rule
    for a protected file is "read on this device and shown to no model", and
    `may_assemble_dossier` refuses it for BOTH localities -- so one protected
    member withholds the group's call exactly as that member alone would be
    withheld, and it is never described to any target.

    MEASURED: not one group-subject request, and not one `llm_dossier` row whose
    subject is the group. The members are still placed -- each meets the same
    gate on its own -- which is the coverage half of the same rule.
    """
    world = seed(protected=("scan",))
    plan, calls = _place_group(world, monkeypatch=monkeypatch)
    assert _group_calls(calls) == []
    assert world.conn.execute(
        "SELECT count(*) AS c FROM llm_dossier WHERE subject_ref LIKE ?",
        (f"{v.GROUP}:%",)).fetchone()["c"] == 0
    assert all(d.group_support is None for d in plan.member_decisions)
    assert len(plan.member_decisions) == len(TOGETHER)


def test_a_member_that_may_not_reach_the_cloud_keeps_the_whole_group_local(
        seed, monkeypatch):
    """`104` §17.13 ruling 3, read over a group: the destination must serve every
    member. A group call carries readings from every file in it, so it is cloud
    only if every member is cloud-permitted, and local otherwise -- site B's own
    sentence about the same shape.

    Here one member is unclassified, which P7 permits a LOCAL model and refuses
    the cloud (R-121). The whole packet goes to the local model, and the one
    member that could not have crossed is not described to a provider.

    MEASURED: the group call happens, and its release is addressed to the local
    target while every other member's own route is the cloud.
    """
    world = seed(unclassified=("scan",))
    scan = world.file_id["scan"]
    local = (object(), LOCAL_TARGET)
    cloud = (object(), CLOUD_TARGET)
    inputs = _model_inputs(
        world.conn, model_target=CLOUD_TARGET,
        model_call_request=_request_builder(CLOUD_TARGET),
        route_for=lambda file_id: local if file_id == scan else cloud)
    _plan, calls = _place_group(world, inputs=inputs, monkeypatch=monkeypatch)
    group_requests = _group_calls(calls)
    assert len(group_requests) == 1
    assert group_requests[0].model_call_request.model_target is LOCAL_TARGET


def test_the_whole_group_goes_to_the_cloud_when_every_member_may(
        seeded, monkeypatch):
    """The discriminating twin of the test above. Without it "local" could be the
    only answer this helper can give, and the rule would look like a rule while
    being a constant."""
    cloud = (object(), CLOUD_TARGET)
    inputs = _model_inputs(
        seeded.conn, model_target=CLOUD_TARGET,
        model_call_request=_request_builder(CLOUD_TARGET),
        route_for=lambda file_id: cloud)
    _plan, calls = _place_group(seeded, inputs=inputs, monkeypatch=monkeypatch)
    assert _group_calls(calls)[0].model_call_request.model_target is CLOUD_TARGET

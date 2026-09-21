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

from p11.conftest import FIXED_CLOCK, NO_CANONICAL_RULE
from placement import vocabulary as v
from placement.config import CEILINGS
from placement.pipeline import GROUP_BUDGET_SUFFIX
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
              unclassified: tuple[str, ...] = (),
              tree: object = None) -> SimpleNamespace:
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
        build_destination_index(p11_conn,
                                FROZEN_TREE if tree is None else tree,
                                component_version="P11-test",
                                observed_at=FIXED_CLOCK, canonical=NO_CANONICAL_RULE)
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
        # The person is told which question was answered about their file --
        # IN THE NAME THEY FILED IT UNDER. This read `GROUP_ID in
        # body["explanation"]` and passed on `g-packet`, which is the key the
        # row above joins on and which nobody owns; on the measured corpus the
        # same assertion would have passed on
        # `plan_0:academic:Coursework:d76647d2fe3c`. The name and the key are
        # different claims, and only the first is the one this test means.
        assert "PHYS1401 packet" in body["explanation"], body["explanation"]
        assert GROUP_ID not in body["explanation"], body["explanation"]


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


# --- `104` §18.2 gap 2: a member the dossier never carried ------------------------
#
# `_group_evidence` carries each member's ACCEPTED FACTS and the items those facts
# cite, so a member with no accepted fact put nothing in front of the model. The
# answer that came back is an answer about the other members, and inheriting it
# filed this file in the group's branch with `decided_by=model` and the group's
# support on the row -- spillover, credited to a judgement that never saw the file.
# `contradicts_the_group` cannot catch it: that reads §6.3's suppression, and a
# file with no stated values suppresses nothing.


def _evidence_for_with_a_factless_member(factless: str):
    """The same `evidence_for`, except one member has no accepted fact at all.

    The commonest file on the owner's own corpus (r6: 164 of 199 files reached
    site C with nothing to send), and P9 can accept it into a packet on a support
    kind that is not a fact -- `scan`'s membership basis here is `user_attached`.
    """
    agrees = _member_evidence("PHYS1401")

    def evidence_for(file_id: str) -> dict:
        if file_id != factless:
            return agrees(file_id)
        return dict(agrees(file_id), facts=(), evidence_items=())
    return evidence_for


def test_a_member_with_no_fact_in_the_group_dossier_never_inherits_its_answer(
        seeded, monkeypatch):
    """MEASURED: the group is asked once, the factless member is not placed by
    that answer, and its row credits neither the model nor the group."""
    scan = seeded.file_id["scan"]
    plan, calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        evidence_for=_evidence_for_with_a_factless_member(scan))

    assert len(_group_calls(calls)) == 1
    # Not one of the files the group's dossier described. The other two are, and
    # `test_a_group_of_related_files_is_one_call_whose_dossier_lists_them_all` is
    # the same read over a group where every member has a fact.
    carried = {item.evidence_ref
               for item in _group_calls(calls)[0].evidence_items}
    assert _obs(scan) not in carried
    assert _obs(seeded.file_id["essay"]) in carried
    apart = next(d for d in plan.member_decisions if d.subject.file_id == scan)
    assert apart.outcome != v.PLACE
    assert apart.destination is None
    assert apart.group_support is None
    # Judged alone, on its own evidence, which reaches no destination -- §6.10's
    # own answer for a file with nothing settled about it, and the answer this
    # member would have got in a run where no group existed. What it is NOT is the
    # group's folder, and the explanation does not name P9 either: the grouping
    # stage flagged nothing here, the dossier simply never carried this file.
    assert apart.abstention_reason == v.NO_SUPPORTED_DESTINATION
    assert "set apart from" not in apart.explanation
    assert not [request for request, _kwargs in calls
                if request.subject_ref == seeded.ref["scan"]], (
        "nothing to send is not a question worth asking")


def test_the_members_the_dossier_did_carry_still_follow_the_groups_answer(
        seeded, monkeypatch):
    """The discriminating twin. Without it the test above could be passing
    because the group's answer stopped reaching anybody at all."""
    scan = seeded.file_id["scan"]
    plan, _calls = _place_group(
        seeded, monkeypatch=monkeypatch,
        evidence_for=_evidence_for_with_a_factless_member(scan))

    went = {d.subject.file_id for d in plan.member_decisions
            if d.group_support is not None}
    assert went == {seeded.file_id["essay"], seeded.file_id["transcript"]}
    assert all(d.destination.node_id == "n-course"
               for d in plan.member_decisions if d.group_support is not None)


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


# --- §6.9: the file with two homes is the JUDGE's question, never a rule's ---------

from p11.p10_fixtures import tree_with
from tree_design.vocabulary import SHARED_BRANCH as SHARED_BRANCH_POLICY

#: §6.9's branch-bearing arm, which is the one `_multi_home_decision` wrote a
#: `place` from. Under `mandatory-review` -- `FROZEN_TREE`'s own policy -- the
#: tree deliberately offers no branch and the selector already decided, so the
#: defect these tests are about is only reachable under a policy that bears one.
SHARED_BRANCH_TREE = tree_with(shared_material_policy=SHARED_BRANCH_POLICY)

#: The second accepted packet that also claims `scan`, and the file that is only
#: ever in it. `00`:113's shape needs both: two groups whose plans settle
#: DIFFERENT parents, and a member of each that is not the shared one -- without a
#: second member of its own the second group has no plan to settle a parent from,
#: and `run_corpus` would find fewer than two competing homes and take the
#: ordinary per-file path.
SECOND_GROUP_ID: str = "g-second"
ONLY_SECOND: str = "brochure"

#: The two packets' answers. Neither is the tree's shared-material branch, which
#: `resolve_multi_home` refuses outright when it is one of the competitors.
FIRST_HOME: str = "n-course"
SECOND_HOME: str = "n-course-alt"


def _seed_second_group(conn, ids) -> None:
    """P9's records for the second packet, through P9's own writers."""
    scan = ids["scan"][0]
    brochure = ids[ONLY_SECOND][0]
    record_group(conn, Group(
        group_id=SECOND_GROUP_ID, seed_ref="seed-2",
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject = PHYS1402",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1402",
            file_ids=(brochure, scan), reliability_state=VALIDATED,
            observation_key=_obs(brochure),
            observation_keys=(_obs(brochure), _obs(scan))),),
        pre_model_signals={}, anchor_count=2, coherence_verdict=COHERENT,
        coherence_citations=(_obs(brochure),),
        group_category="college_applications",
        display_label="PHYS1402 packet", label_source=ENGINE, conflicts=(),
        stop_rule_hits=(), state=SUPPORTED, sensitivity_state=NO_SENSITIVITY,
        dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
        created_by=RULES, created_at=T0))
    for name in (ONLY_SECOND, "scan"):
        file_id, content_hash = ids[name]
        record_membership(conn, Membership(
            membership_id=f"m2-{file_id}", group_id=SECOND_GROUP_ID,
            file_id=file_id, content_hash=content_hash, basis=DIRECT_ANCHOR,
            decision=INCLUDED, decision_source=RULES,
            support=(Support(support_kind=SHARED_VALIDATED_FACT,
                             observation_key=_obs(file_id),
                             quote_or_field="subject", location="body",
                             edge_ref=None),),
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at=T0))
    record_acceptance(conn, GroupAcceptance(
        acceptance_id="acc-2", plan_version_id="plan-1",
        group_id=SECOND_GROUP_ID, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0))


@pytest.fixture()
def two_homes(seeded, p11_conn, tmp_path):
    """`scan` with accepted membership in two packets, each settling its own parent."""
    ids = dict(seeded.ids)
    ids[ONLY_SECOND] = _real_file(
        p11_conn, tmp_path / "corpus", name=f"{ONLY_SECOND}.pdf",
        body=b"%PDF-1.4 " + ONLY_SECOND.encode())
    _classify(p11_conn, file_id=ids[ONLY_SECOND][0],
              content_hash=ids[ONLY_SECOND][1], protected=False,
              handling_class="personal_non_sensitive")
    _seed_second_group(p11_conn, ids)
    return SimpleNamespace(
        conn=p11_conn, ids=ids,
        file_id={name: ids[name][0] for name in ids},
        ref={name: f"{v.FILE}:{ids[name][0]}:{ids[name][1]}" for name in ids})


def _two_home_evidence(world):
    """Each packet's own course code, and the shared file carrying both group ids."""
    first = _member_evidence("PHYS1401")
    second = _member_evidence("PHYS1402")
    scan = world.file_id["scan"]
    brochure = world.file_id[ONLY_SECOND]

    def evidence_for(file_id: str) -> dict:
        if file_id == brochure:
            return dict(second(file_id), group_ids=(SECOND_GROUP_ID,))
        if file_id == scan:
            return dict(first(file_id), group_ids=(GROUP_ID, SECOND_GROUP_ID))
        return first(file_id)
    return evidence_for


def _run_two_homes(world, *, monkeypatch, inputs=None, answers=None,
                   verdict_for=None):
    """`run_corpus` over both packets with `call_placement_steps` faked."""
    import placement.pipeline as pipeline

    from p11.test_p11_pipeline import _partition

    calls: list = []
    answers = dict(answers or {})
    answers.setdefault(f"{v.GROUP}:{GROUP_ID}", FIRST_HOME)
    answers.setdefault(f"{v.GROUP}:{SECOND_GROUP_ID}", SECOND_HOME)

    def _fake(conn_, request, **kwargs):
        calls.append((request, kwargs))
        if verdict_for is not None:
            return verdict_for(request)
        return _verdict(answers.get(request.subject_ref, FIRST_HOME))
        yield  # pragma: no cover -- makes this a generator; never reached

    monkeypatch.setattr(pipeline, "call_placement_steps", _fake)
    if inputs is None:
        inputs = _model_inputs(world.conn, tree=SHARED_BRANCH_TREE,
                               partition=_partition)
    result = pipeline.run_corpus(
        world.conn, subjects=(), group_ids=(GROUP_ID, SECOND_GROUP_ID),
        inputs=inputs, evidence_for=_two_home_evidence(world),
        component_version="P11-test", observed_at=FIXED_CLOCK)
    return result, calls


def _scan_decision(result, world):
    scan = world.file_id["scan"]
    return next(d for d in result.decisions if d.subject.file_id == scan)


def test_gap_a_file_with_two_homes_is_asked_of_the_judge_with_both_homes_offered(
        two_homes, monkeypatch):
    """`00` Amendments -- "every placement goes through the model" -- read over
    §6.9's own case.

    `_multi_home_decision` wrote a `place` whose `decided_by` was the RULES and
    whose destination was the tree's shared-material branch, and site C was never
    asked about the file at all. A two-homes file is the one a judge is most
    needed for: two packets pulled it, and which of them it primarily belongs to
    is a judgement about the file rather than an arrangement of the tree.

    MEASURED: exactly one site-C request whose subject is the file, whose offer is
    the two competing homes and nothing else, and a stored decision that says the
    MODEL decided and names the home it chose.

    SABOTAGE: put the shared branch back as a rule's `place` -- the call count
    goes to zero and `decided_by` reads `rule`.
    """
    result, calls = _run_two_homes(
        two_homes, monkeypatch=monkeypatch,
        answers={two_homes.ref["scan"]: SECOND_HOME})
    own = [(request, kwargs) for request, kwargs in calls
           if request.subject_ref == two_homes.ref["scan"]]
    assert len(own) == 1, "the file with two homes was never asked about"
    offered = list(own[0][1]["call_dependencies"].allowed_vocabulary)
    assert set(offered) == {FIRST_HOME, SECOND_HOME}
    assert len(offered) == 2, "only §6.9's two competing homes are on the offer"
    decision = _scan_decision(result, two_homes)
    assert decision.outcome == v.PLACE
    assert decision.destination.node_id == SECOND_HOME
    body = _stored(two_homes.conn, decision)
    assert body["decided_by"] == v.DECIDED_BY_MODEL
    # AND THE ROW STATES THE BASIS THE JUDGE WAS SHOWN (§6.4). These three were
    # empty tuples while §6.9's `place` was a rule reading a policy, and a record
    # that still said so would tell the person this file's evidence ruled nothing
    # out -- about a file whose own course fact suppressed one of the two homes.
    assert [c["kind"] for c in body["conflicts_considered"]] == ["subject"]


def test_gap_a_two_homes_file_the_judge_abstains_about_is_the_persons_question(
        two_homes, monkeypatch):
    """The other legal outcome, and gap 15 already built it: when the judge does
    not answer, the two homes go to the person as the `Ask` they settle.

    MEASURED: the call was made, no destination was written, and the question
    carries both homes as its options.
    """
    from p11.test_p11_pipeline import _partition

    inputs = _model_inputs(two_homes.conn, tree=SHARED_BRANCH_TREE,
                           partition=_partition,
                           ask_or_abstain=lambda node_ids: v.ASK_USER)
    result, calls = _run_two_homes(
        two_homes, monkeypatch=monkeypatch, inputs=inputs,
        verdict_for=lambda request: (
            _abstaining_verdict()
            if request.subject_ref == two_homes.ref["scan"]
            else _verdict(FIRST_HOME
                          if request.subject_ref == f"{v.GROUP}:{GROUP_ID}"
                          else SECOND_HOME)))
    assert [request.subject_ref for request, _k in calls].count(
        two_homes.ref["scan"]) == 1
    decision = _scan_decision(result, two_homes)
    assert decision.outcome == v.ASK_USER
    assert decision.destination is None
    assert set(decision.ask.options) == {FIRST_HOME, SECOND_HOME}


def test_gap_with_no_model_path_the_two_homes_file_is_still_never_placed_by_a_rule(
        two_homes, monkeypatch):
    """§13.5's fallback does not become a rule's placement here. With no model
    configured there is no judgement to be had about which packet this file is
    primarily in, and §6.9's remaining answers are the person's question and the
    abstention -- never the branch chosen on their behalf.

    MEASURED: no site-C request at all, and the file is the person's question.
    """
    from p11.test_p11_pipeline import _partition

    inputs = _inputs(two_homes.conn, tree=SHARED_BRANCH_TREE,
                     partition=_partition,
                     ask_or_abstain=lambda node_ids: v.ASK_USER)
    result, calls = _run_two_homes(two_homes, monkeypatch=monkeypatch,
                                   inputs=inputs)
    assert calls == []
    decision = _scan_decision(result, two_homes)
    assert decision.outcome == v.ASK_USER
    assert set(decision.ask.options) == {FIRST_HOME, SECOND_HOME}


# --- `00`:112's SECOND sentence: the members are classified WITHIN the branch -----

#: `00`:112: *"classify members within that branch: essay drafts go to Essays;
#: checklists to Forms"*. `FROZEN_TREE`'s `n-course` is a leaf, so every existing
#: test in this file measures the no-sub-level arm -- a member that goes with its
#: group and makes no call. This is the other arm, and it needs a branch with
#: levels under it.
ESSAYS: str = "n-essays"
FORMS: str = "n-forms"


def _sub_level(node_id: str, label: str, value: str, ordinal: int):
    """One level under `n-course`, built through P10's own constructor.

    `expected_values` is the CHAIN, which is what `materialise._project` writes:
    the parent's `subject = PHYS1401` and then this level's own `work_type`.
    """
    from p11.p10_fixtures import ExpectedValue, _node

    return _node(
        node_id=node_id, display_label=label, parent_node_id="n-course",
        ordinal=ordinal, associated_group_ids=(),
        dimension_role="kind of work", dimension="work_type",
        expected_values=(ExpectedValue(field="subject", value="PHYS1401"),
                         ExpectedValue(field="work_type", value=value)),
        explanation=f"The PHYS1401 group holds {label.lower()} of its own.",
        refinement_disposition="refined",
        refinement_reason="The course has enough populated work types for this level.")


def _two_level_tree():
    from dataclasses import replace

    from p11.p10_fixtures import FROZEN_TREE, NODES, _profile

    nodes = NODES + (_sub_level(ESSAYS, "Essays", "essay", 4),
                     _sub_level(FORMS, "Forms", "checklist", 5))
    return replace(
        FROZEN_TREE, nodes=nodes,
        profiles=tuple(_profile(node) for node in nodes),
        freeze_record=replace(
            FROZEN_TREE.freeze_record,
            node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))


TWO_LEVEL_TREE = _two_level_tree()


def _kind_obs(file_id: str) -> str:
    return f"obs-kind-{file_id}"


def _member_evidence_with_kind(kind_value: str | None):
    """One member's accepted facts: the course, and what kind of work it is."""
    def build(file_id: str) -> dict:
        facts = (MatchingFact(file_fact_id=f"ff-{file_id}", field="subject",
                              value="PHYS1401", reliability=v.DIRECT,
                              evidence_ref=_obs(file_id)),)
        items = (EvidenceItem(evidence_ref=_obs(file_id), kind="fact",
                              location="page-1", excerpt_span=(0, 8),
                              reliability_state="direct",
                              basis="direct-anchor"),)
        if kind_value is not None:
            facts += (MatchingFact(file_fact_id=f"ffk-{file_id}",
                                   field="work_type", value=kind_value,
                                   reliability=v.DIRECT,
                                   evidence_ref=_kind_obs(file_id)),)
            items += (EvidenceItem(evidence_ref=_kind_obs(file_id), kind="fact",
                                   location="page-2", excerpt_span=(0, 8),
                                   reliability_state="direct",
                                   basis="direct-anchor"),)
        return dict(facts=facts, evidence_items=items, group_ids=(GROUP_ID,),
                    curated_folder_labels=(), semantic_neighbours=(),
                    related_files=(), entity_frequency={"PHYS1401": 6},
                    generic_entity_frequency=200)
    return build


def _kinded_evidence(world):
    """The essay says it is an essay, the transcript says it is a checklist, and
    the other two say nothing about what kind of work they are."""
    kinds = {world.file_id["essay"]: "essay",
             world.file_id["transcript"]: "checklist"}

    def evidence_for(file_id: str) -> dict:
        return _member_evidence_with_kind(kinds.get(file_id))(file_id)
    return evidence_for


@pytest.fixture()
def sub_levels(seed):
    return seed(tree=TWO_LEVEL_TREE)


def _place_in_branch(world, *, monkeypatch, answers=None, verdict_for=None):
    return _place_group(
        world, monkeypatch=monkeypatch,
        inputs=_model_inputs(world.conn, tree=TWO_LEVEL_TREE),
        evidence_for=_kinded_evidence(world),
        answers=answers, verdict_for=verdict_for)


def _own_call(calls, ref):
    own = [(request, kwargs) for request, kwargs in calls
           if request.subject_ref == ref]
    assert len(own) == 1, f"{ref} was asked {len(own)} questions of its own"
    return own[0]


def test_gap_each_member_is_judged_inside_the_folder_its_group_was_given(
        sub_levels, monkeypatch):
    """`00`:112, the sentence after the one gap 14 built: *"First confirm the
    shared parent branch ... then classify members within that branch: essay
    drafts go to Essays; checklists to Forms."*

    The group's answer was filed on every member VERBATIM. A packet placed at
    `PHYS1401` put the essay, the transcript and the scan in the same folder, and
    the two levels the person's own tree offers under it -- the levels P10 built
    because the course HAS enough populated work types for them -- were never
    offered to anybody. A branch is where a packet belongs; which shelf inside it
    a file belongs on is a second question about that file.

    MEASURED: one call took the group, each member was then asked its own question
    whose offer is the branch and the levels under it, and the two members with
    evidence for different levels land in different folders -- each still carrying
    its group's support, because the branch is still the group's answer.

    SABOTAGE: file the group's answer verbatim again -- both members come back on
    `n-course` and the member calls disappear.
    """
    plan, calls = _place_in_branch(
        sub_levels, monkeypatch=monkeypatch,
        answers={f"{v.GROUP}:{GROUP_ID}": "n-course",
                 sub_levels.ref["essay"]: ESSAYS,
                 sub_levels.ref["transcript"]: FORMS})
    assert len(_group_calls(calls)) == 1
    assert plan.shared_parent_node_id == "n-course"
    placed = {d.subject.file_id: d for d in plan.member_decisions}
    assert placed[sub_levels.file_id["essay"]].destination.node_id == ESSAYS
    assert placed[sub_levels.file_id["transcript"]].destination.node_id == FORMS
    for name in ("essay", "transcript"):
        body = _stored(sub_levels.conn, placed[sub_levels.file_id[name]])
        assert body["decided_by"] == v.DECIDED_BY_MODEL
        assert body["group_support"]["group_id"] == GROUP_ID
    # THE OFFER IS THE BRANCH AND ITS LEVELS, and nothing outside it: the group's
    # answer already settled which branch, and re-opening that is asking one
    # question twice.
    offered = set(_own_call(calls, sub_levels.ref["essay"])[1][
        "call_dependencies"].allowed_vocabulary)
    assert offered == {"n-course", ESSAYS, FORMS}


def test_gap_a_member_the_judge_keeps_at_the_branch_stays_there_with_its_group(
        sub_levels, monkeypatch):
    """The fallback, and it is the coverage half. A refinement question that goes
    unanswered must not undo the answer the group's own call already gave about
    this file: the branch is where it goes, and the level is the part nobody
    settled.

    MEASURED: the judge abstains on the member's own question, the file is still
    placed at the branch, and its row still says the model decided and names the
    group.
    """
    essay = sub_levels.ref["essay"]
    plan, calls = _place_in_branch(
        sub_levels, monkeypatch=monkeypatch,
        verdict_for=lambda request: (
            _abstaining_verdict() if request.subject_ref == essay
            else _verdict("n-course")))
    _own_call(calls, essay)
    decision = next(d for d in plan.member_decisions
                    if d.subject.file_id == sub_levels.file_id["essay"])
    assert decision.destination.node_id == "n-course"
    body = _stored(sub_levels.conn, decision)
    assert body["decided_by"] == v.DECIDED_BY_MODEL
    assert body["group_support"]["group_id"] == GROUP_ID


def test_gap_a_members_own_question_spends_a_members_own_purse(sub_levels,
                                                               monkeypatch):
    """§8.6's ledgers, kept apart. `104` §18.31 is why this is a pin and not a
    comment: the group's call was spending the per-file purse, and the factless
    file site C exists for recorded `BUDGET_EXHAUSTED` on a six-file corpus.

    The group's own question spends `GROUP_BUDGET_SUFFIX`'s ledger
    (`_the_groups_own_answer` replaces `scan_id` on a LOCAL rebinding of `inputs`,
    so `place_group`'s own `inputs` are untouched); a member's refinement question
    is about one file and spends that file's own.

    MEASURED: the group request's scan id carries the suffix and no member's does,
    and every member still reaches a destination -- five calls under this fixture's
    ceiling of eight, so nothing here is deferred for cost.
    """
    plan, calls = _place_in_branch(
        sub_levels, monkeypatch=monkeypatch,
        answers={f"{v.GROUP}:{GROUP_ID}": "n-course",
                 sub_levels.ref["essay"]: ESSAYS,
                 sub_levels.ref["transcript"]: FORMS})
    purses = {request.subject_ref: kwargs["call_dependencies"].scan_budget.scan_id
              for request, kwargs in calls}
    group_purse = purses[f"{v.GROUP}:{GROUP_ID}"]
    assert group_purse.endswith(GROUP_BUDGET_SUFFIX)
    for subject_ref, purse in purses.items():
        if subject_ref.startswith(f"{v.GROUP}:"):
            continue
        assert not purse.endswith(GROUP_BUDGET_SUFFIX), subject_ref
        assert purse == group_purse[:-len(GROUP_BUDGET_SUFFIX)]
    assert all(d.destination is not None for d in plan.member_decisions)
    assert all(d.abstention_reason is None for d in plan.member_decisions)

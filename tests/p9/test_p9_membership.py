# tests/p9/test_p9_membership.py
"""P9 Task 10 — P9 maps P8's verdict. It does not re-decide it.

P8 owns the only function that speaks to a model and the only validator that says
whether the model's answer held. P9's job at this seam is a mapping: an
authoritative outcome in, a membership and an acceptance obligation out. Every
check P8 already ran — invented member, citation grounding, contradiction, schema
— is absent here on purpose, and a test reads this package's imports to prove it.

The rule that costs the most if it is wrong: an `accept_context_supported`
membership and its `pending-review` acceptance row are written in ONE transaction.
A context-supported member is a file the model was not sure about; making it
visible without the review obligation that makes it safe is how an uncertain
guess becomes a silent decision.

SR5 is mapped here and nowhere earlier. It means P8 could not explain the group
with valid citations, and only P8's returned reasons can say that.
"""
from __future__ import annotations

import pytest

from grouping.acceptance import (
    AcceptanceStateAbsent,
    membership_review_state_as_of,
)
from grouping.p8_seam import (
    DossierDeferred,
    GroupDecision,
    apply_p8_verdict,
    build_dossier_request,
)
from grouping.records import AnchorFact, Group
from grouping.schema import create_grouping_schema
from grouping.store import memberships_for_group, record_group
from grouping.vocabulary import (
    CANDIDATE,
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    ENGINE,
    EXCLUDED,
    INCLUDED,
    INTERPRETATION,
    LLM,
    LLM_PROPOSED,
    NO_GROUP,
    PENDING_REVIEW,
    RULES,
    SR5,
    STRONGLY_IDENTIFIED_FILE,
    SUPPORTED,
    UNCERTAIN,
    USER_EDITED,
    VALIDATION,
)
from llm_harness.records import CallFailed, P8Verdict, Refusal, ValidationUnavailable
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    CITATION_NOT_IN_DOSSIER,
    CONTEXT_SUPPORTED_MEMBERSHIP,
    DIRECT_MEMBERSHIP,
    REJECT,
    REJECTED,
    WEAK,
)

T0 = "2026-08-27T00:00:00Z"
GROUP = "fixture-course-group"
PLAN = "plan-2"
KEY = "sha256:" + "d" * 64


@pytest.fixture()
def seam_conn(conn):
    from database_agent.db import create_schema

    create_schema(conn)
    create_grouping_schema(conn)
    return conn


def _group(**overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject=PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("file-1",),
            reliability_state="validated", observation_key=KEY),),
        pre_model_signals={}, anchor_count=1, coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0,
    )
    values.update(overrides)
    return Group(**values)


def _dossier():
    from grouping.fixtures import course_dossier_fixture

    return course_dossier_fixture()


def _verdict(outcome=ACCEPT_DIRECT, **overrides) -> P8Verdict:
    disposition = {
        ACCEPT_DIRECT: DIRECT_MEMBERSHIP,
        ACCEPT_CONTEXT_SUPPORTED: CONTEXT_SUPPORTED_MEMBERSHIP,
        WEAK: "possible",
        REJECT: REJECTED,
        ABSTAIN: ABSTAIN,
    }[outcome]
    values = dict(
        verdict_id="verdict-1", dossier_id="dossier-1", claim_ref="claim-1",
        outcome=outcome, disposition=disposition, reasons=(),
        may_propose=outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED),
        requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
        citations_checked=(), scope="group", validator_version="P8/0.1.0",
        policy_version="policy-1", plan_version=None,
    )
    values.update(overrides)
    return P8Verdict(**values)


def _apply(conn, result, *, group=None, dossier=None, plan_version_id=PLAN):
    return apply_p8_verdict(
        conn, group=group or _group(), dossier=dossier or _dossier(),
        result=result, plan_version_id=plan_version_id, created_at=T0,
    )


def _request(dossier):
    """P9 supplies neither the model target nor the prompt; both are P8's, chosen
    by the caller that owns the run."""
    from privacy.release import ModelTarget

    return build_dossier_request(
        dossier,
        model_target=ModelTarget(
            locality="local", model_id="fixture", provider="fixture"),
        prompt_template_id="template.grouping",
        prompt_fingerprint="sha256:fp",
        max_dossier_tokens=4000,
    )


# --- P9 converts references and never materialises ------------------------------


def test_the_request_is_reference_only_and_is_not_a_p8_dossier():
    from llm_harness.records import DossierRequest

    request = _request(_dossier())
    assert isinstance(request, DossierRequest)
    assert request.subject_ref == GROUP
    assert request.evidence_items
    assert all(item.evidence_ref for item in request.evidence_items)
    for item in request.model_call_request.requested_items:
        assert hasattr(item, "observation_key")


def test_every_dossier_member_arrives_as_a_member_kind_reference():
    """Site B rejects a member the dossier did not carry as `kind == "member"`.
    A candidate P9 sends as an excerpt reference is a member P8 will call
    invented."""
    dossier = _dossier()
    request = _request(dossier)
    members = {
        item.evidence_ref for item in request.evidence_items
        if item.kind == "member"
    }
    expected = {
        item.file_id for item in (*dossier.anchor_files, *dossier.candidate_files)
    }
    assert members == expected


def test_p9_imports_no_gate_no_transport_and_no_materialised_dossier():
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    banned_modules = {"privacy.gate", "privacy.binding", "privacy.resolve"}
    banned_names = {"Dossier", "ModelClient", "issue", "Gate", "Verdict"}
    offenders = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module in banned_modules:
                    offenders.append(f"{path.name}:{node.lineno}:{node.module}")
                for alias in node.names:
                    if alias.name in banned_names:
                        offenders.append(f"{path.name}:{node.lineno}:{alias.name}")
    assert offenders == [], offenders

    # And nothing compares or computes with a token count.
    for node in ast.walk(tree):
        if isinstance(node, (ast.Compare, ast.BinOp)):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Name) and "token" in inner.id.lower():
                    offenders.append(f"{node.lineno}:{inner.id}")
                if isinstance(inner, ast.Attribute) and "token" in inner.attr.lower():
                    offenders.append(f"{node.lineno}:{inner.attr}")
    assert offenders == [], offenders


# --- accept_direct ---------------------------------------------------------------


def test_accept_direct_writes_an_included_direct_anchor_membership(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(ACCEPT_DIRECT))
    assert isinstance(decision, GroupDecision)
    memberships = memberships_for_group(seam_conn, GROUP)
    assert memberships
    assert all(item.basis == DIRECT_ANCHOR for item in memberships)
    assert all(item.decision_source == LLM for item in memberships)
    assert decision.stop_rule_outcome is None


def test_accept_direct_needs_no_review_obligation(seam_conn):
    record_group(seam_conn, _group())
    _apply(seam_conn, _verdict(ACCEPT_DIRECT))
    membership = memberships_for_group(seam_conn, GROUP)[0]
    with pytest.raises(AcceptanceStateAbsent):
        membership_review_state_as_of(
            seam_conn, membership_id=membership.membership_id,
            plan_version_id=PLAN)


# --- accept_context_supported: membership and obligation, or neither -------------


def test_a_context_membership_and_its_review_obligation_land_together(seam_conn):
    record_group(seam_conn, _group())
    _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED))
    memberships = memberships_for_group(seam_conn, GROUP)
    assert memberships
    for membership in memberships:
        assert membership.basis == CONTEXT_SUPPORTED
        assert membership.decision == UNCERTAIN
        assert membership_review_state_as_of(
            seam_conn, membership_id=membership.membership_id,
            plan_version_id=PLAN) == PENDING_REVIEW


def test_a_context_membership_without_a_plan_version_writes_nothing(seam_conn):
    """The obligation is per plan version. Without one there is nowhere to record
    the review, and a membership visible without its review is the failure."""
    record_group(seam_conn, _group())
    with pytest.raises(ValueError) as excinfo:
        _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED), plan_version_id=None)
    # The record would refuse a blank `plan_version_id` too, and the transaction
    # would roll the membership back -- but only after writing it, and with a
    # message about a missing field rather than about a missing review.
    assert "plan version" in str(excinfo.value)
    assert "review" in str(excinfo.value)
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_a_failed_acceptance_write_leaves_no_membership_behind(seam_conn, monkeypatch):
    """One transaction. A membership that became visible while its review
    obligation failed to record is an uncertain guess wearing a decision."""
    import grouping.p8_seam as seam

    record_group(seam_conn, _group())

    def boom(*_a, **_k):
        raise RuntimeError("the acceptance write failed")

    monkeypatch.setattr(seam, "record_context_review_pending", boom)
    with pytest.raises(RuntimeError):
        _apply(seam_conn, _verdict(ACCEPT_CONTEXT_SUPPORTED))
    assert memberships_for_group(seam_conn, GROUP) == ()


# --- everything else cannot make a supported group -------------------------------


@pytest.mark.parametrize("outcome", [WEAK, REJECT, ABSTAIN])
def test_a_non_accepting_outcome_creates_no_membership(seam_conn, outcome):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(outcome))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.group_state != "supported"


def test_a_may_propose_false_verdict_is_refused_even_if_it_says_accept(seam_conn):
    """`may_propose` is P8's own answer to "may this become a proposal". A verdict
    whose outcome and flag disagree is not one P9 resolves in the model's favour.
    """
    record_group(seam_conn, _group())
    with pytest.raises(ValueError):
        _apply(seam_conn, _verdict(ACCEPT_DIRECT, may_propose=False))
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_a_refusal_records_a_validation_failure_and_no_membership(seam_conn):
    from privacy.denial import RemedyOption
    from privacy.release import Denied

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, Refusal(
        denied=Denied(
            reason="unclassified", explanation="no classification is stored",
            remedy_options=(RemedyOption(action="classify", detail="classify first"),),
            evidence_refs=(KEY,)),
        validator_version="P8/0.1.0", policy_version="policy-1"))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.failure_stage == VALIDATION


def test_a_call_failure_records_the_interpretation_stage_and_nothing_else(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, CallFailed(
        request_identity="dossier-1", release_id="rel-1", audit_id=17,
        explanation="the client raised", validator_version="P8/0.1.0",
        policy_version="policy-1"))
    assert decision.failure_stage == INTERPRETATION
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert seam_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 0
    assert seam_conn.execute(
        "SELECT stage FROM group_failure_points").fetchone()["stage"] == INTERPRETATION


def test_validation_unavailable_writes_nothing_and_is_not_an_abstention(seam_conn):
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, ValidationUnavailable(missing=("contradicts",)))
    assert memberships_for_group(seam_conn, GROUP) == ()
    assert decision.failure_stage == VALIDATION
    assert decision.stop_rule_outcome is None


def test_needs_consent_is_returned_unchanged_and_writes_nothing(seam_conn):
    from privacy.consent import ConsentRequirement
    from privacy.release import NeedsConsent

    record_group(seam_conn, _group())
    needs = NeedsConsent(requirement=ConsentRequirement(
        file_ids=("file-1",), handling_class="sensitive_personal",
        items=((KEY, "0:4"),), why="the packet carries a sensitive record"),
        consent_request_id="consent-1")
    assert _apply(seam_conn, needs) is needs
    assert memberships_for_group(seam_conn, GROUP) == ()
    for table in ("group_acceptance", "group_failure_points", "memberships"):
        assert seam_conn.execute(
            f"SELECT count(*) AS c FROM {table}").fetchone()["c"] == 0


# --- SR5 is mapped from P8's reasons, never re-derived ---------------------------


def test_a_citation_failure_from_p8_maps_to_sr5(seam_conn):
    """P9 does not inspect citations. It reads the authoritative reason codes."""
    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        REJECT, reasons=(CITATION_NOT_IN_DOSSIER,)))
    assert decision.stop_rule_outcome is not None
    assert decision.stop_rule_outcome.rules_fired == (SR5,)
    assert decision.stop_rule_outcome.outcome == NO_GROUP


def test_a_rejection_for_another_reason_is_not_sr5(seam_conn):
    from llm_harness.vocabulary import CONTRADICTED_BY_STRONGER

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        REJECT, reasons=(CONTRADICTED_BY_STRONGER,)))
    assert decision.stop_rule_outcome is None


def test_p9_reads_no_citation_and_runs_no_second_validator():
    import ast
    import pathlib

    import grouping.p8_seam as module

    text = pathlib.Path(module.__file__).read_text()
    for banned in ("citations_checked", "span_matched", "resolved",
                   "evidence_resolver", "contradicts", "normalize"):
        assert banned not in text, banned
    tree = ast.parse(text)
    called = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "validate_response" not in called
    assert "dispatch" not in called


# --- a budget-deferred result is not P9's ladder to run --------------------------


def test_a_budget_deferred_p8_result_maps_to_dossier_deferred(seam_conn):
    from llm_harness.vocabulary import BUDGET_EXHAUSTED

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, _verdict(
        ABSTAIN, reasons=(BUDGET_EXHAUSTED,)))
    assert isinstance(decision.deferred, DossierDeferred)
    assert memberships_for_group(seam_conn, GROUP) == ()


def test_p9_never_runs_the_reduction_ladder():
    """M9's summarize -> preserve anchors -> split/defer ladder is P8's `run_call`.
    Checked over identifiers and string literals, since the docstring has to be
    able to name the thing it is refusing to do."""
    import ast
    import pathlib

    import grouping.p8_seam as module

    # `max_dossier_tokens` is P8's own field and P9 passes it through untouched.
    # What is banned is a P9 decision about it.
    banned = {"summarize", "summarise", "split_shard", "reduction"}
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and any(
                word in node.id.lower() for word in banned):
            offenders.append(f"{node.lineno}:{node.id}")
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            for word in banned:
                if word in node.value.lower():
                    offenders.append(f"{node.lineno}:{word}")
    assert offenders == [], offenders


# --- the builder's conflicts reach the membership --------------------------------


def test_an_accepted_membership_carries_the_conflicts_naming_its_file(seam_conn):
    """`Membership.conflicts` was hardcoded `()` here, so a file the builder knew
    was in conflict became a member that claimed no conflict at all. The
    application dossier names `essay-columbia` and `essay-duke` in one
    `target_institution` conflict; `essay-columbia` is an anchor, so its
    `accept_direct` membership must say so and `admissions-checklist`'s must not."""
    from grouping.fixtures import application_dossier_fixture
    from grouping.store import memberships_for_group

    dossier = application_dossier_fixture()
    _apply(seam_conn, _verdict(),
           group=_group(group_id=dossier.group_id), dossier=dossier)

    by_file = {
        item.file_id: item
        for item in memberships_for_group(seam_conn, dossier.group_id)
    }
    assert [c.kind for c in by_file["essay-columbia"].conflicts] == [
        "target_institution"]
    assert by_file["admissions-checklist"].conflicts == ()


# --- `104` R-16 / packet G11: the model's four answers, applied ------------------
#
# `00` §4.5 gives the model four tasks -- coherence, the members, the outliers,
# and (only if coherence holds) a label and a category. R-16: "`apply_p8_verdict`
# writes no `display_label`, `group_category` or `coherence_verdict`; per-member
# include/exclude/uncertain collapses to blanket memberships". G11 says the same
# from the packet's side: "The model's four answers are validated and then three of
# them are dropped. B must be observe-only until P9 reads them."


def _answered(verdict=None, *, coherent=COHERENT, category="academic",
              label="PHYS1401 course materials", members=None):
    from grouping.p8_seam import Answered, MemberDecision, ModelAnswer

    if members is None:
        members = (
            MemberDecision(file_id="lecture-08", decision=INCLUDED,
                           why="states the course code"),
            MemberDecision(file_id="midterm-practice", decision=INCLUDED,
                           why="states the course code"),
            MemberDecision(file_id="hw-3", decision=UNCERTAIN,
                           why="retrieved beside them and states nothing"),
        )
    return Answered(
        result=verdict if verdict is not None else _verdict(ACCEPT_DIRECT),
        answer=ModelAnswer(coherent=coherent, category=category, label=label,
                           members=tuple(members), citations=(KEY,)))


def test_r16_an_accepted_verdict_writes_the_label_the_category_and_the_verdict(
        seam_conn):
    """The group row is INSERTED here, which is what made the three writable.

    `groups_never_overwritten` refuses an UPDATE of any of these columns and a
    superseding row needs a new `group_id`, so a later write was never available:
    `grouping.pipeline` withholds the insert while a ratified model is about to
    decide, and this is the one write for the row.
    """
    from grouping.store import current_group

    _apply(seam_conn, _answered())

    stored = current_group(seam_conn, GROUP)
    assert stored.display_label == "PHYS1401 course materials"
    assert stored.group_category == "academic"
    assert stored.coherence_verdict == COHERENT


def test_r16_the_record_says_the_model_decided_and_never_the_person(seam_conn):
    """`104` R-28's actor rule: never say the person when the rules or the model
    did. `label_source` is the three-author ladder -- engine, llm-proposed,
    user-edited -- and this is the middle rung; the group also names the verdict
    and the dossier the answer came from, so "the model decided" is checkable
    rather than asserted."""
    from grouping.store import current_group

    _apply(seam_conn, _answered())

    stored = current_group(seam_conn, GROUP)
    assert stored.label_source == LLM_PROPOSED
    assert stored.label_source not in (USER_EDITED, ENGINE)
    assert stored.validation_verdict_ref == "verdict-1"
    assert stored.dossier_id == "fixture-course-dossier"


def test_r16_the_engine_keeps_the_row_when_the_model_proposes_no_label(seam_conn):
    """`naming.engine_proposal` is still the author when the model is not.

    "A group below the bar comes back untouched", and a model that accepts the
    coherence without naming the group has proposed nothing to write. What lands is
    exactly what a deterministic deployment would have written, which is why this
    change is invisible to a run with no model."""
    from grouping.store import current_group

    engine_named = _group(state=SUPPORTED, coherence_verdict=COHERENT,
                          group_category="academic", display_label="PHYS1401",
                          label_source=ENGINE)
    _apply(seam_conn, _answered(label=None), group=engine_named)

    stored = current_group(seam_conn, GROUP)
    assert stored.display_label == "PHYS1401"
    assert stored.label_source == ENGINE


# --- `00`'s Q-C (`104` §13.7): the model names, the user confirms ----------------
#
# "A value the library has not seen is proposed once; the user confirms or renames
# it; it then belongs to that user's vocabulary in the database." Half of that was
# built: an unrecognised `group_category` was dropped to NULL, which is the "never
# file under it" clause. The other half was missing entirely -- nothing recorded
# that the value had been said, so the person had nothing to confirm and the
# model's answer left no trace at all.

UNSEEN = "hobby_projects"


def test_qc_an_unrecognised_category_is_written_down_as_a_question(seam_conn):
    """The proposal the ruling asks for, with everything a person needs to answer
    it: the value the model chose, the group it chose it for, the label it gave
    that group, and the verdict and dossier the answer came from."""
    from grouping.store import group_category_proposals

    _apply(seam_conn, _answered(category=UNSEEN))

    rows = group_category_proposals(seam_conn)
    assert [row["proposed_value"] for row in rows] == [UNSEEN]
    assert rows[0]["group_id"] == GROUP
    assert rows[0]["display_label"] == "PHYS1401 course materials"
    assert rows[0]["proposed_by"] == LLM_PROPOSED
    assert rows[0]["verdict_ref"] == "verdict-1"
    assert rows[0]["dossier_id"] == "fixture-course-dossier"


def test_qc_nothing_is_filed_under_a_category_nobody_confirmed(seam_conn):
    """The clause that was already true, and it stays true. P10 selects an
    applicability row BY `group_category`, so writing an unrecognised one files the
    material under a schema that speaks for somebody else's life. The LABEL is kept
    either way, because a label is words and a category is a routing decision."""
    from grouping.store import current_group

    _apply(seam_conn, _answered(category=UNSEEN))

    stored = current_group(seam_conn, GROUP)
    assert stored.group_category is None
    assert stored.display_label == "PHYS1401 course materials"


def test_qc_a_value_is_proposed_once_however_many_groups_say_it(seam_conn):
    """"Proposed ONCE" is the ruling's own word. The third group the model calls
    `hobby_projects` is more evidence for the same question, not a second question,
    and a person asked twice about one word learns that the product is not
    listening."""
    from grouping.store import group_category_proposals

    _apply(seam_conn, _answered(category=UNSEEN))
    _apply(seam_conn, _answered(category=UNSEEN),
           group=_group(group_id="group-2"))

    rows = group_category_proposals(seam_conn)
    assert len(rows) == 1
    assert rows[0]["group_id"] == GROUP, "the first group to say it is the one shown"


def test_qc_a_category_the_library_recognises_is_no_ones_question(seam_conn):
    """The negative half. `academic` is filed on the row and asks nobody
    anything; a proposal for it would be a question with an answer already."""
    from grouping.store import current_group, group_category_proposals

    _apply(seam_conn, _answered())

    assert current_group(seam_conn, GROUP).group_category == "academic"
    assert group_category_proposals(seam_conn) == []


def test_qc_no_category_at_all_is_the_model_declining_and_asks_nothing(seam_conn):
    """A question about nothing is not a question. The model that named no
    category proposed no vocabulary, and a row here would invent one to confirm."""
    from grouping.store import group_category_proposals

    _apply(seam_conn, _answered(category=None))
    _apply(seam_conn, _answered(category=""), group=_group(group_id="group-3"))

    assert group_category_proposals(seam_conn) == []


def test_qc_a_group_the_model_did_not_call_coherent_proposes_no_vocabulary(
        seam_conn):
    """§4.5 runs task 4 -- the label and the category -- "only if coherence is
    supported". A category proposed inside a group the model said was not one
    thing would ask a person to confirm a word about material that has none."""
    from grouping.store import group_category_proposals
    from grouping.vocabulary import ABSTAINED

    _apply(seam_conn, _answered(coherent=ABSTAINED, category=UNSEEN))

    assert group_category_proposals(seam_conn) == []


def test_r16_a_group_already_on_disk_is_left_exactly_as_it_stands(seam_conn):
    """The conservative half, and it is the owner question this leaves open.

    A second, DIFFERING model answer about a group whose row already carries a
    proposal is a real supersession -- a superseding row needs a new `group_id`
    that every membership and `group_acceptance` row would then not name -- and it
    is refused here rather than answered quietly, which is the position
    `record_group`'s own docstring takes for a widened anchor set. The person's
    label is protected by the same rule and by more besides."""
    from grouping.store import current_group

    record_group(seam_conn, _group(
        state=SUPPORTED, coherence_verdict=COHERENT, group_category="academic",
        display_label="My PHYS notes", label_source=USER_EDITED))
    _apply(seam_conn, _answered())

    stored = current_group(seam_conn, GROUP)
    assert stored.display_label == "My PHYS notes"
    assert stored.label_source == USER_EDITED


def test_r16_an_excluded_member_is_recorded_excluded_and_reaches_no_reader_as_one(
        seam_conn):
    """"Excluded members are not members", at the writer AND at both readers.

    The ROW is kept on purpose -- §8.7 stores a withdrawn membership with the
    evidence that produced it, and `tree_design.upstream` publishes it as
    `excluded_members` -- so what "not a member" means is that no reader counts it
    as one, which is asserted here rather than assumed."""
    from grouping.p8_seam import MemberDecision
    from grouping.store import memberships_for_group

    record_group(seam_conn, _group())
    _apply(seam_conn, _answered(members=(
        MemberDecision(file_id="lecture-08", decision=INCLUDED, why="states it"),
        MemberDecision(file_id="midterm-practice", decision=EXCLUDED,
                       why="a different course"),
    )))

    by_file = {item.file_id: item
               for item in memberships_for_group(seam_conn, GROUP)}
    assert by_file["midterm-practice"].decision == EXCLUDED
    assert by_file["lecture-08"].decision == INCLUDED


def test_r16_an_uncertain_member_is_uncertain_and_carries_its_review(seam_conn):
    """"Uncertain members are recorded as uncertain, never silently included."
    The review obligation lands with it, which is what makes an uncertain member
    safe to show: P11 places it as a context-supported match and the person sees
    it pending."""
    from grouping.store import memberships_for_group

    record_group(seam_conn, _group())
    _apply(seam_conn, _answered())

    by_file = {item.file_id: item
               for item in memberships_for_group(seam_conn, GROUP)}
    assert by_file["hw-3"].decision == UNCERTAIN
    assert by_file["lecture-08"].decision == INCLUDED
    assert membership_review_state_as_of(
        seam_conn, membership_id=by_file["hw-3"].membership_id,
        plan_version_id=PLAN) == PENDING_REVIEW


def test_r16_a_member_the_model_did_not_name_gets_no_membership(seam_conn):
    """The model answered about two of the three files in the dossier. P9 writes
    what the model said and nothing else: a third membership here would be P9
    authoring a decision on the model's behalf, which is what the blanket write
    was."""
    from grouping.p8_seam import MemberDecision
    from grouping.store import memberships_for_group

    record_group(seam_conn, _group())
    _apply(seam_conn, _answered(members=(
        MemberDecision(file_id="lecture-08", decision=INCLUDED, why="states it"),
        MemberDecision(file_id="midterm-practice", decision=INCLUDED,
                       why="states it"),
    )))

    assert {item.file_id for item in memberships_for_group(seam_conn, GROUP)} == {
        "lecture-08", "midterm-practice"}


def test_r16_a_member_basis_is_the_dossiers_and_not_the_list_it_came_from(
        seam_conn):
    """The blanket write took `anchor_files` for a direct verdict and
    `candidate_files` for a context one, so the BASIS was decided by which branch
    ran rather than by what the dossier says each file is. `DossierFile.basis` is
    already one of `MEMBERSHIP_BASES` and is what the builder concluded."""
    from grouping.store import memberships_for_group

    record_group(seam_conn, _group())
    _apply(seam_conn, _answered())

    by_file = {item.file_id: item
               for item in memberships_for_group(seam_conn, GROUP)}
    assert by_file["lecture-08"].basis == DIRECT_ANCHOR
    assert by_file["hw-3"].basis == CONTEXT_SUPPORTED


def test_r16_an_observed_answer_is_recorded_and_applied_to_nothing(seam_conn):
    """The half that does not move: under an unratified prompt the site records
    its dossier, its response and its verdict, and applies none of it. `104` §7
    Phase 1 step 6, and it is what `cli.observed_run_call` wraps while
    `drafts_status()` says `unratified`."""
    from grouping.p8_seam import ObservedOnly
    from grouping.store import current_group, memberships_for_group

    record_group(seam_conn, _group())
    decision = _apply(seam_conn, ObservedOnly(result=_answered()))

    assert decision.membership_ids == ()
    assert memberships_for_group(seam_conn, GROUP) == ()
    stored = current_group(seam_conn, GROUP)
    assert stored.display_label is None
    assert stored.coherence_verdict is None


def test_r16_a_rejected_answer_writes_no_label_and_no_membership(seam_conn):
    """The CHECK on `groups` says a label exists only beside `coherent`, and
    `LABEL_WITHOUT_COHERENCE` says the same from the validator's side. A verdict
    P8 did not accept applies nothing at all."""
    from grouping.store import current_group, memberships_for_group

    record_group(seam_conn, _group())
    _apply(seam_conn, _answered(_verdict(REJECT)))

    assert memberships_for_group(seam_conn, GROUP) == ()
    assert current_group(seam_conn, GROUP).display_label is None

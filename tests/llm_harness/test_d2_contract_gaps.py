"""The contract gaps the D2 packet reports, each pinned before it is written down.

`planning/105-D2-PROMPT-PACKET.md` §7 says what the four unwired sites' contracts
cannot express or do wrongly. A sentence there is a claim; a test here is the
evidence. The repo's convention for an open defect is a strict xfail asserting
the CORRECT behaviour, so the day a fix lands the test turns green and fails as
an unexpected pass until its marker is removed.

Every world here is built the way `tools/promptbench` builds one: the frozen
`Dossier`, the model-visible bytes under a wire-handle key, and the response the
model could honestly have written from those bytes.
"""
from __future__ import annotations

import ast
import json
import sys

import pytest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from llm_harness.dossier import field_glossary  # noqa: E402
from llm_harness.records import Dossier  # noqa: E402
from llm_harness.vocabulary import (  # noqa: E402
    ACCEPT_DIRECT, BELOW_SUPPORT_THRESHOLD, C_PLACEMENT, CHOOSE_BROAD_PARENT,
    SCHEMA_INVALID,
    CONFLICT_IGNORED, D_RESIDUAL, EVIDENCE_NOT_IN_FILE_RECORD, INVENTED_PROJECT,
    REJECT, RETURN_ACCEPTED_PACKET, STRONGER_RELATIONSHIP_OVERLOOKED,
    VALID_REVIEW_REQUIRED, WEAK,
)
from llm_harness.wire_handles import wire_handle  # noqa: E402

from tools.promptbench.cases import Case, Item, evidence  # noqa: E402
from tools.promptbench.dossiers import (  # noqa: E402
    BENCH_HANDLE_KEY, dossier_of, model_visible_bytes,
)
from tools.promptbench.judge import judge, site_dependencies_for  # noqa: E402

SUBJECT = "file:gap-1"
PLAN = "plan-gap"


def _c_case(*, conflicts=(), items=(), extra_evidence=()) -> Case:
    heading = evidence(subject_ref=SUBJECT, address="heading:1",
                       value="PHYS 1401 Problem Set 4", zone="heading")
    return Case(
        case_id="G-C", site=C_PLACEMENT, title="gap world", persona="Priya",
        traces=("104:R-15", "00:114"), subject_ref=SUBJECT,
        allowed_vocabulary=("node-hw", "node-course"),
        evidence=(heading,) + tuple(extra_evidence),
        items=tuple(items) or (
            Item(evidence_ref="node-hw", kind="candidate",
                 location="Coursework > PHYS1401 > homework"),
            Item(evidence_ref="node-course", kind="candidate",
                 location="Coursework > PHYS1401")),
        conflicts=tuple(conflicts), plan_version=PLAN,
        expect={"destination": "node-hw"}, should_abstain=False)


def _d_case(*, conflicts=(), location=SUBJECT) -> Case:
    ocr = evidence(subject_ref=SUBJECT, address="ocr:1",
                   value="Your Columbia University application has been submitted",
                   zone="ocr", location=location)
    return Case(
        case_id="G-D", site=D_RESIDUAL, title="gap world", persona="multi-life",
        traces=("00:125",), subject_ref=SUBJECT,
        allowed_vocabulary=("r-temp", "group-columbia"), evidence=(ocr,),
        items=(Item(evidence_ref="r-temp", kind="residual_area",
                    location="Photos > Temporary Screenshots"),
               Item(evidence_ref="group-columbia", kind="accepted_group",
                    location="accepted group: Columbia application packet")),
        conflicts=tuple(conflicts), plan_version=PLAN,
        authorities={"approved_target_ids": ("r-temp",),
                     "frozen_nodes": ("r-temp", "group-columbia")},
        expect={"action": RETURN_ACCEPTED_PACKET, "target": "group-columbia"},
        should_abstain=False)


def _handles_in(case: Case, dossier) -> dict:
    """What the model was shown: the keyed forms of every identifier."""
    text = model_visible_bytes(dossier, _prompt(case.site)).decode("utf-8")
    body = json.loads(text.split("The dossier follows.\n", 1)[1])
    return body


def _prompt(site):
    from llm_harness.records import PromptDefinition
    return PromptDefinition(
        template_id=f"{site.lower()}.unratified.gap-test.2026-09-06",
        template_bytes=b"T\nThe dossier follows.\n",
        response_schema_bytes=b'{"type":"object"}', call_site=site,
        call_site_version="1", shaping_policy_bytes=b'{"policy":"gap"}')


def _cite(case: Case, span: str) -> list[dict]:
    return [{"evidence_ref": wire_handle(case.evidence[0].key, key=BENCH_HANDLE_KEY),
             "cited_span": span, "why_it_supports": "states it"}]


def _c_response(case: Case, **payload) -> bytes:
    # One supported level and no standing alternative: under `105` §14.1 an
    # empty level list is BELOW_SUPPORT_THRESHOLD and a listed alternative is
    # INSUFFICIENT_MARGIN, so the accepted baseline carries neither.
    body = {"destination": "node-hw", "per_dimension_support": [
                {"dimension": "course", "value": "PHYS 1401", "support": "direct"}],
            "alternatives": [], "conflicts_considered": [],
            "support": 1, "next_support": 0}
    body.update(payload)
    return json.dumps({"claims": [{"payload": body,
                                   "citations": _cite(case, "PHYS 1401")}]}).encode()


# --- G1: R-157, CLOSED. The considered list is un-digested before it is read -----
#
# The two xfails here were right: `dossier._body` keys every `conflict_id` with
# `wire_handle` and both sites compared the model's list against the RAW ids, so
# a C dossier carrying any conflict was unanswerable and 15 of r14's site-C
# rejections were this. `_considered_conflicts` now maps the list back through
# `wire_handles.issued_conflict_handles` first, and the three tests below hold
# the repaired contract instead: the handles pass, a subset does not, and a
# handle naming no conflict does not.


def test_g1_site_c_a_model_that_echoes_every_shown_conflict_is_not_ignoring_it():
    case = _c_case(conflicts=(("conflict-abc123", "target_university"),))
    dossier = dossier_of(case)
    shown = [c["conflict_id"] for c in _handles_in(case, dossier)["conflicts"]]
    assert shown and shown != ["conflict-abc123"], "the id IS keyed on the wire"
    verdict = judge(case, dossier, _c_response(case, conflicts_considered=shown),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ACCEPT_DIRECT, verdict.verdicts


def test_g1_both_spellings_of_the_one_conflict_are_considered():
    """The handle the model was shown, and the local id it was not.

    The raw id is accepted on the citation path's own principle: `local_ref`
    hands back a string this dossier never issued, and a string that then equals
    a local id is taken at its word -- which is what `check_citations` does with
    a raw `observation_key`. The model cannot reach either id: the assertion
    below is that the wire body does not carry it.
    """
    case = _c_case(conflicts=(("conflict-abc123", "target_university"),))
    dossier = dossier_of(case)
    body = _handles_in(case, dossier)
    assert "conflict-abc123" not in json.dumps(body)
    for considered in (["conflict-abc123"],
                       [c["conflict_id"] for c in body["conflicts"]]):
        verdict = judge(case, dossier,
                        _c_response(case, conflicts_considered=considered),
                        schema={"type": "object"},
                        site_dependencies=site_dependencies_for(case))
        assert verdict.worst_outcome == ACCEPT_DIRECT, considered


def test_g1_a_handle_that_names_no_conflict_leaves_it_unconsidered():
    """An invented handle resolves to nothing, so the conflict is still ignored.

    SABOTAGE: the un-digested handle starts matching, and a conflict the model
    never looked at reads as considered. `local_ref` hands an unissued string back
    unchanged, so an invented handle names no conflict and `CONFLICT_IGNORED` is
    raised -- that half is G1's and does not move.

    What moved is what follows the code. `104` §18.2 gap 2: the echo is
    bookkeeping about a flag the model was already shown, not a structural fault
    in the answer, and `00`'s amendment of 2026-09-05 leaves site C rejecting only
    "a node that is not in the frozen tree, or a cited fact that is not in the
    evidence". So the code is recorded on a placement that survives and asks for a
    person.
    """
    case = _c_case(conflicts=(("conflict-abc123", "target_university"),))
    dossier = dossier_of(case)
    shown = [c["conflict_id"] for c in _handles_in(case, dossier)["conflicts"]]
    invented = ["handle:" + "f" * (len(shown[0]) - len("handle:"))]
    assert invented != shown
    verdict = judge(case, dossier,
                    _c_response(case, conflicts_considered=invented),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome != REJECT
    assert [CONFLICT_IGNORED] in [v["reasons"] for v in verdict.verdicts]
    assert all(v["disposition"] == VALID_REVIEW_REQUIRED
               for v in verdict.verdicts if CONFLICT_IGNORED in v["reasons"])


def test_g1_site_d_a_model_that_echoes_the_shown_relationship_did_consider_it():
    case = _d_case(conflicts=(("conflict-rel-1", "stronger_relationship"),))
    dossier = dossier_of(case)
    shown = [c["conflict_id"] for c in _handles_in(case, dossier)["conflicts"]]
    response = json.dumps({"claims": [{
        "payload": {"action": RETURN_ACCEPTED_PACKET, "target": "group-columbia",
                    "stop_reason": "the confirmation names the application",
                    "relationships_considered": shown},
        "citations": _cite(case, "Columbia University application")}]}).encode()
    verdict = judge(case, dossier, response, schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ACCEPT_DIRECT, verdict.verdicts
    assert STRONGER_RELATIONSHIP_OVERLOOKED not in [
        r for v in verdict.verdicts for r in v["reasons"]]


# --- G2: R-15, CLOSED. The per-level check is grounding, not the node-id list -----
#
# The xfail here asserted that a real `project` value is not invented, and it was
# right about the defect and wrong about the world it asserted it in: this case's
# only evidence is a `PHYS 1401` heading, so `PVA-RDP` is not something the file
# states and rejecting it is correct under `104` §13.6's grounding rule. Both
# directions are pinned instead, in a world where the file does state it.


def _project_case():
    """The same gap world, with a body line that names the project."""
    return _c_case(extra_evidence=(
        evidence(subject_ref=SUBJECT, address="body:2",
                 value="Prepared for the PVA-RDP study", zone="body"),))


def test_g2_a_project_value_the_files_own_evidence_states_is_not_invented():
    case = _project_case()
    verdict = judge(case, dossier_of(case), _c_response(case, per_dimension_support=[
        {"dimension": "project", "value": "PVA-RDP", "support": "direct"}]),
        schema={"type": "object"}, site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ACCEPT_DIRECT, verdict.verdicts


def test_g2_a_project_value_the_file_never_states_is_still_invented():
    """The control: grounding is a real check and did not become a rubber stamp."""
    case = _c_case()
    verdict = judge(case, dossier_of(case), _c_response(case, per_dimension_support=[
        {"dimension": "project", "value": "PVA-RDP", "support": "direct"}]),
        schema={"type": "object"}, site_dependencies=site_dependencies_for(case))
    assert [INVENTED_PROJECT] in [v["reasons"] for v in verdict.verdicts]


def test_g2_a_node_id_no_longer_launders_a_value():
    """What the defect made possible, gone: `node-course` is a legal destination
    and says nothing about what this file's text contains."""
    case = _c_case()
    verdict = judge(case, dossier_of(case), _c_response(case, per_dimension_support=[
        {"dimension": "project", "value": "node-course", "support": "direct"}]),
        schema={"type": "object"}, site_dependencies=site_dependencies_for(case))
    assert [INVENTED_PROJECT] in [v["reasons"] for v in verdict.verdicts]


# --- G3, CLOSED: the live C/D dossier now carries the profile the drafts describe --


def test_g3_a_node_id_still_gets_no_meaning_from_the_glossary_and_no_field():
    """The two halves of G3 that were never the fix, asserted unchanged.

    `field_glossary` names a P6 FIELD KEY in each entry, so a minted node id gets none
    and always would have; and `Dossier` has no profile field, because the profile
    is not a sixteenth key. `dossier._BODY_ORDER` refuses one (`104` R-58), and the
    drafts describe the profile as an `evidence_item`, which is a key the dossier
    already has.
    """
    assert field_glossary(("node-7f3a", "node-0c11")) == []
    assert "candidate_profiles" not in Dossier.__dataclass_fields__
    assert "node_profiles" not in Dossier.__dataclass_fields__


def test_g3_the_builder_change_the_packet_asked_for_has_landed():
    """`104` R-17: the vocabulary is the ranked shortlist and every id is described.

    This asserted the DEFECT -- `allowed_vocabulary=legal` over
    `sorted(legal_node_ids(...))`, "the live dossier carries ... no label chain, no
    expected values, no known document types, no 'this is the file's own folder'".
    G3's own consequence line says "**Ratifying C or D ratifies that builder
    change**", so the pin turns round with the change rather than being deleted:
    `_judge_with_model` now offers `Assessment.scored`'s order at C and the
    approved residual library plus the retrieved branches at D, and `_offered_items`
    describes every one of them through `placement.index.node_profile`.

    The behaviour is pinned end to end in `tests/p11/test_p11_pipeline.py`'s R-17
    section against the real pipeline; what is asserted here is that the source of
    the gap is gone, because that is what this register row was written about.
    """
    source = (REPO / "src" / "placement" / "pipeline.py").read_text("utf-8")
    assert "allowed_vocabulary=legal" not in source
    assert "allowed_vocabulary=list(offered)" in source
    assert "_offered_items(" in source
    profiles = (REPO / "src" / "placement" / "index.py").read_text("utf-8")
    assert "def node_profile(" in profiles


# --- G4: nothing in src constructs site B's authorities ----------------------------


def test_g4_no_module_in_src_constructs_p8_authorities_for_site_b():
    """`grouping.pipeline` calls `p8_run_call` with a `P8Authorities` bundle that
    no module under `src/` builds, so B's `allowed_vocabulary` is undefined in the
    live product. The bench defines one (the category ids) and the packet says so."""
    constructors = []
    for path in (REPO / "src").rglob("*.py"):
        tree = ast.parse(path.read_text("utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "id", None) or getattr(func, "attr", None)
                if name == "P8Authorities":
                    constructors.append(str(path.relative_to(REPO)))
    assert constructors == [], constructors


# --- G5: R-158, CLOSED. A D citation must name the subject file in `location` -------
#
# The xfail here was right: `_same_file_evidence` looked the citation's
# `evidence_ref` up as the MODEL wrote it, and a P4 key is keyed before it leaves
# the device, so the lookup missed on every real key and the check passed every
# citation -- fail-open, and unmeasurable, since site D is not wired on the
# owner's runs. It now reads `verdict.citations_checked`, which
# `validation._validate_claim` has already un-digested, and the two tests below
# hold the repaired check: the citation is refused under the handle the model
# writes, and under the raw key it cannot see.


def _d_response() -> bytes:
    return json.dumps({"claims": [{
        "payload": {"action": RETURN_ACCEPTED_PACKET, "target": "group-columbia",
                    "stop_reason": "names the application",
                    "relationships_considered": []},
        "citations": None}]}).encode()


def test_g5_site_d_refuses_a_keyed_citation_whose_item_is_not_the_subject_file():
    case = _d_case(location="ocr")            # the item names a zone, not the file
    response = json.loads(_d_response())
    response["claims"][0]["citations"] = _cite(case, "Columbia University application")
    verdict = judge(case, dossier_of(case), json.dumps(response).encode(),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert [EVIDENCE_NOT_IN_FILE_RECORD] in [v["reasons"] for v in verdict.verdicts]


def test_g5_both_spellings_of_the_citation_reach_the_same_refusal():
    """The raw key the model never sees, and the handle it does. R-158."""
    case = _d_case(location="ocr")
    response = json.loads(_d_response())
    response["claims"][0]["citations"] = [{
        "evidence_ref": case.evidence[0].key,      # raw P4 key: not on the wire
        "cited_span": "Columbia University application",
        "why_it_supports": "states it"}]
    verdict = judge(case, dossier_of(case), json.dumps(response).encode(),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert [EVIDENCE_NOT_IN_FILE_RECORD] in [v["reasons"] for v in verdict.verdicts]
    # And the keyed citation, which is all a model can write, reaches it too.
    response["claims"][0]["citations"] = _cite(case, "Columbia University application")
    keyed = judge(case, dossier_of(case), json.dumps(response).encode(),
                  schema={"type": "object"},
                  site_dependencies=site_dependencies_for(case))
    assert keyed.worst_outcome == REJECT
    assert [EVIDENCE_NOT_IN_FILE_RECORD] in [v["reasons"] for v in keyed.verdicts]


# --- G8: a D return must name a frozen NODE, not the group it returns to ------------


def test_g8_site_d_return_target_must_be_a_frozen_node_so_a_group_id_is_refused():
    """§7.7's two returns name 'a confirmed domain group' or 'an accepted graph or
    purpose packet', but `_residual_site` validates their `target` with
    `node_exists` and `approved_target_ids` like a destination. A group id is
    DESTINATION_NOT_IN_FROZEN_TREE; the only target that validates is the branch
    node built from the group (`00`:107). The draft says so; the packet asks
    whether that is the intended reading."""
    import dataclasses
    case = dataclasses.replace(_d_case(), authorities={
        "approved_target_ids": ("r-temp",), "frozen_nodes": ("r-temp",)})
    response = json.loads(_d_response())
    response["claims"][0]["citations"] = _cite(case, "Columbia University application")
    verdict = judge(case, dossier_of(case), json.dumps(response).encode(),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == REJECT
    assert ["DESTINATION_NOT_IN_FROZEN_TREE"] in [v["reasons"] for v in verdict.verdicts]


# --- G6: site C demands numeric support and next_support from the model -----------


def test_g6_site_c_without_the_two_numbers_is_a_shape_violation_not_a_weak_placement():
    """G6, closed by `105` §14.1: the two counts are recorded diagnostics. They
    are still part of the shape -- absent, the answer is malformed and is
    rejected as such -- but no threshold is applied to them."""
    case = _c_case()
    response = json.loads(_c_response(case))
    del response["claims"][0]["payload"]["support"]
    del response["claims"][0]["payload"]["next_support"]
    verdict = judge(case, dossier_of(case), json.dumps(response).encode(),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == REJECT
    assert [SCHEMA_INVALID] in [v["reasons"] for v in verdict.verdicts]
    assert BELOW_SUPPORT_THRESHOLD not in [r for v in verdict.verdicts for r in v["reasons"]]


def test_g6_a_tie_in_the_counts_no_longer_turns_a_placement_weak():
    """The third time C05 came back `weak` on `support` 1, `next_support` 1 was
    the ruling's own example (`105` §14.1): counts do not establish uniqueness.
    A tie, a runner-up ahead, and a clear win are all recorded and none vetoes."""
    case = _c_case()
    for support, next_support in ((1, 1), (0, 3), (2, 1)):
        verdict = judge(case, dossier_of(case),
                        _c_response(case, support=support, next_support=next_support),
                        schema={"type": "object"},
                        site_dependencies=site_dependencies_for(case))
        assert verdict.worst_outcome == ACCEPT_DIRECT, (support, next_support)
        assert BELOW_SUPPORT_THRESHOLD not in [
            r for v in verdict.verdicts for r in v["reasons"]]


# --- G7: D's controlled set has a broad-parent action with no channel for depth ----


def test_g7_site_d_broad_parent_and_residual_destination_are_one_disposition():
    """§7.7's 'choose an approved broad parent branch' and 'choose one approved
    residual destination' both validate as a `target` in `approved_target_ids`
    and both land as RESIDUAL_DESTINATION; only the injected `residual_action_of`
    can tell them apart. Pinned so the draft's `action` key is known to carry the
    distinction the verdict drops."""
    case = _d_case()
    import dataclasses
    case = dataclasses.replace(case, authorities={
        "approved_target_ids": ("r-temp", "group-columbia"),
        "frozen_nodes": ("r-temp", "group-columbia")})
    response = json.dumps({"claims": [{
        "payload": {"action": CHOOSE_BROAD_PARENT, "target": "r-temp",
                    "stop_reason": "no trip group", "relationships_considered": []},
        "citations": _cite(case, "Columbia University application")}]}).encode()
    verdict = judge(case, dossier_of(case), response, schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))
    assert verdict.worst_outcome == ACCEPT_DIRECT
    assert verdict.verdicts[0]["disposition"] == "residual_destination"


# --- G8: the mark's two state words have no P8 home, so P8 cannot refuse a third --
#
# `104` R-104's second half, and the half this change could NOT close. The
# ratified D text tells the model that `mark_protected_or_unsupported`'s
# `"target" is the word "protected" or the word "unsupported"`
# (`d_residual_template.ladder.txt`:41), and P11 enforces exactly that: the two
# words are `placement.vocabulary.MARKED_STATES` and
# `PlacementDecision.marked_state` refuses a third by name.
#
# P8 cannot. `llm_harness.vocabulary` carries the ACTION and neither of its
# states, and `tests/p8/test_p8_architecture.py`'s `NEIGHBOUR_PRODUCERS` forbids
# every P8 module from importing `placement`. So a third word is ACCEPTED here,
# reaches `_residual_action_of` (`cli.py`:1710) as raw payload, and ends the run
# inside `placement.residual.outcome_for_action` -- a set the person was in the
# middle of answering dies on one bad word in one answer about one file.
#
# The unblock is one line outside this half of the repo: either the two words get
# a P8 home in `llm_harness/vocabulary.py` (a mirror of P11's `MARKED_STATES`,
# pinned equal by test -- a closed-vocabulary placement and so the owner's), or
# `ResidualDependencies` grows a `marked_states` injection wired at the
# composition root. Once either lands, `_residual_site` refuses the word with
# `ACTION_NOT_IN_CONTROLLED_SET` and `placement/pipeline.py`:4226 already routes
# a rejected D verdict to the abstention record, so the run continues and nothing
# downstream changes.


@pytest.mark.xfail(strict=True, reason="`104` R-104: P8 has no home for the two "
                                       "marked-state words, so it cannot refuse "
                                       "a third; the run ends in P11 instead")
def test_g8_a_mark_whose_state_is_neither_word_is_refused_by_p8():
    """DESIGN: a word the ratified D text did not offer is a rejected claim
    recorded on the set, not a `ValueError` that ends the run.

    MEASUREMENT: a site D answer marking the file `"archived"` -- a word neither
    `protected` nor `unsupported` -- comes back REJECT. Today it comes back
    `accept_direct`, and the word travels to `outcome_for_action`, which raises.
    """
    case = _d_case()
    response = json.dumps({"claims": [{
        "payload": {"action": "mark_protected_or_unsupported",
                    "target": "archived",
                    "stop_reason": "cannot be read",
                    "relationships_considered": []},
        "citations": _cite(case, "Columbia University application")}]}).encode()
    verdict = judge(case, dossier_of(case), response, schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))

    assert verdict.worst_outcome == REJECT


# --- G9: §13.6's schema half still has no channel at site C -------------------
#
# `104` R-77. §13.6 makes a hard veto of two things, and only one of them is
# buildable here today: a model fact "not grounded in the file's own evidence"
# (built -- `_invented_dimension` now grounds every non-`context` level whatever
# the model calls it) "or FALLS OUTSIDE THE DERIVED SCHEMA" (not built). At site
# A the derived schema is the dossier's own field keys, so "the field exists" is
# a lookup. At C the schema is the frozen tree's levels and nothing in the
# dossier names them: `Dossier.folder_levels` is `()` at C by design
# (`model_placement.py`:448, "C and D place a file inside a tree that is already
# designed"), `allowed_vocabulary` is node ids, and R-17's node profiles reach
# the dossier as one free-text `location` string per candidate rather than as an
# enumeration. The wired C schema constrains `dimension` to any non-empty string.
#
# So a level the tree does not have, whose value the file DOES state, is admitted
# -- grounded, and about a level that does not exist. The unblock is a channel,
# not a check: `folder_levels` filled at C, or a node-profile field that names
# the levels. Inventing the list inside the validator would be a rule guessing at
# the tree, which is the one thing `_invented_dimension` is written not to do.


@pytest.mark.xfail(strict=True, reason="`104` R-77: nothing in the C dossier "
                                       "names the tree's levels, so the schema "
                                       "half of 13.6 has no channel")
def test_g9_a_level_the_tree_does_not_have_is_refused_at_site_c():
    """DESIGN: 13.6 hard-vetoes a fact that falls outside the derived schema,
    and at site C the derived schema is the frozen tree's own levels.

    MEASUREMENT: a placement whose level is named `sabbatical` -- no such level
    exists in any tree this product designs -- comes back REJECT even though the
    value it carries is stated by the file. Today it is accepted, because
    grounding is all the validator can ask.
    """
    case = _c_case()
    response = _c_response(case, support=1, next_support=0)
    parsed = json.loads(response)
    parsed["claims"][0]["payload"]["per_dimension_support"] = [
        {"dimension": "sabbatical",
         "value": "PHYS 1401", "support": "direct"}]
    verdict = judge(case, dossier_of(case), json.dumps(parsed).encode(),
                    schema={"type": "object"},
                    site_dependencies=site_dependencies_for(case))

    assert verdict.worst_outcome == REJECT

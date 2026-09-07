"""`104` §7 Phase 1 step 6's constraint, before any of its wiring.

Observe-only means two things at once and only one of them is about behaviour.
The behaviour is that B, C, D and E run and apply nothing. The CONSTRAINT is that
they run HERE and nowhere else: every prompt they would send is a D2 draft, the
packet's own status is `unratified`, and `104` §13 keeps a standing count of "0
cloud calls with unratified prompts".

A count nobody enforces is a hope, so the enforcement is in code and these are its
tests. They are written before the sites are wired on purpose: a guard added after
the callers exist is a guard whose first version was never the one under test.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
for _path in (str(_ROOT), str(_ROOT / "src")):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import cli  # noqa: E402
from llm_harness.prompt_library import (  # noqa: E402
    DraftNotInManifest, draft_bytes, draft_row, drafts_status,
)
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE,
)
from readers.model_deepseek import CLOUD  # noqa: E402
from readers.model_ollama import LOCAL  # noqa: E402

#: Read from the product, not repeated here. `cli.OBSERVE_TEMPLATE_ID` is the one
#: table that points a site at its text, and a copy in the tests would be a second
#: table to keep true -- which is the drift these tests exist to catch elsewhere.
#:
#: B IS ON v2 AND THE WAVE NAMED v3: `anchors-first-v3` is on the prompts branch
#: and has not merged, so it is in no manifest this branch can read. The
#: substitution is asserted below rather than left to a commit message.
WINNERS = cli.OBSERVE_TEMPLATE_ID


def test_the_observe_set_is_the_four_sites_that_have_no_ratified_text():
    assert cli.OBSERVE_CALL_SITES == frozenset(
        {B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE})


def test_a_site_is_never_both_wired_and_observed():
    """A site in both would apply its answer and discard it, and there is no run
    that could be correct. Asserted in the module as well, so the import fails
    before a corpus is read rather than here."""
    assert not (cli.WIRED_CALL_SITES & cli.OBSERVE_CALL_SITES)
    assert cli.WIRED_CALL_SITES == frozenset({A_FACT})


@pytest.mark.parametrize("site", sorted(WINNERS))
def test_an_observe_site_is_refused_a_cloud_model(site):
    """The count `104` §13 keeps, kept in code. Unratified text is text nobody has
    agreed to send: on this device that is a question of taste, and over the
    internet it is a person's dossier reaching a provider under a prompt their
    owner never approved, and it cannot be taken back."""
    assert cli.observe_locality_permits(site, LOCAL) is True
    assert cli.observe_locality_permits(site, CLOUD) is False
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget, match=site):
        cli.require_observe_locality(site, CLOUD)


def test_the_refusal_says_the_packet_is_unratified_in_the_packets_own_word():
    """Read from the manifest, never remembered here: if the owner ratifies the
    packet the sentence stops claiming otherwise without anyone editing it."""
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget) as caught:
        cli.require_observe_locality(C_PLACEMENT, CLOUD)

    assert drafts_status() in str(caught.value)
    assert cli.LOCAL_MODEL_NAME in str(caught.value)


def test_a_fact_is_untouched_and_may_still_be_asked_over_the_internet():
    """`A_fact`'s text is ratified (`planning/82` §0) and `WIRED_CALL_SITES` is
    what governs it. A guard that caught it too would have turned an observe-mode
    constraint into a cloud outage."""
    assert cli.observe_locality_permits(A_FACT, CLOUD) is True
    cli.require_observe_locality(A_FACT, CLOUD)


def test_the_packet_itself_says_it_is_unratified():
    assert drafts_status() == "unratified"


@pytest.mark.parametrize("site,template_id", sorted(WINNERS.items()))
def test_every_observe_sites_draft_loads_and_says_unratified_in_its_own_id(
        site, template_id):
    """A record written under one of these ids says on its face that the text was
    not ratified. That is what makes an observe run auditable after the fact: the
    id is in `llm_response` and `llm_verdict`, and it carries the word."""
    assert "unratified" in template_id
    assert draft_row(template_id)["site"] == site

    template, schema, policy = draft_bytes(template_id)

    assert template and schema and policy
    assert template.strip().startswith(b"#") or len(template) > 1000


def test_a_template_id_nobody_published_is_refused_and_names_what_there_is():
    """`84` §1: absent means refuse, never guess. A loader that fell back to a
    sibling draft would send text under an id no record could be checked against."""
    with pytest.raises(DraftNotInManifest, match="anchors-first-v9"):
        draft_bytes("b_group.unratified.anchors-first-v9.2026-09-06")


# --- the hook the four sites apply nothing through --------------------------

def test_an_observed_result_writes_no_accepted_state_and_keeps_what_it_saw():
    """`104` §7 Phase 1 step 6: record dossiers, responses and verdicts, apply
    nothing. The recording is P8's and has already happened by the time this
    exists -- `run_call` writes all three before returning. What `ObservedOnly`
    withholds is the APPLICATION: the memberships and the acceptance row that
    would turn a model's answer into a group the person sees.

    `_decision`'s defaults are `membership_ids=()` and no acceptance row, which is
    exactly the pass condition "no accepted group is written". The wrapped result
    is KEPT rather than discarded, so the outcome stays attributable and a reader
    can see what would have been applied."""
    from grouping.p8_seam import ObservedOnly

    observed = ObservedOnly(result="a verdict that will not be acted on")

    assert observed.result == "a verdict that will not be acted on"


def test_the_observe_hook_is_a_wrapper_and_not_a_flag():
    """A boolean travelling beside a result can be read by one branch and missed
    by another, and the two things that must not drift are "the call happened" and
    "nothing was applied". A type carries both at once: a caller that forgets to
    unwrap gets an object `apply_p8_verdict` refuses to treat as a verdict, rather
    than a verdict applied under a flag nobody checked."""
    import dataclasses

    from grouping.p8_seam import ObservedOnly

    assert dataclasses.is_dataclass(ObservedOnly)
    assert [f.name for f in dataclasses.fields(ObservedOnly)] == ["result"]
    assert ObservedOnly.__dataclass_params__.frozen


def test_b_is_asked_under_v3_now_that_its_manifest_row_is_here():
    """The substitution `104` §12.5 waited on: v3 (`105` §4.7, the G13 bracket
    defect gone) is in this branch's manifest since the prompts merge, so the id
    resolves and its bytes verify against the recorded digest. Still unratified."""
    assert cli.OBSERVE_TEMPLATE_ID[B_GROUP].endswith("anchors-first-v3.2026-09-06")
    assert draft_bytes(cli.OBSERVE_TEMPLATE_ID[B_GROUP])


@pytest.mark.parametrize("site", sorted(cli.OBSERVE_TEMPLATE_ID))
def test_the_prompt_each_observe_site_is_asked_under_says_unratified(site):
    """Every `llm_response` and `llm_verdict` row written at these sites carries
    the template id, so the id saying `unratified` is what makes an observe run
    auditable after the fact rather than on trust."""
    prompt = cli.observe_prompt(site)

    assert prompt.call_site == site
    assert "unratified" in prompt.template_id
    assert prompt.template_bytes and prompt.response_schema_bytes
    assert prompt.shaping_policy_bytes


def test_the_prompt_table_names_every_observe_site_and_no_other():
    """A site with no text would refuse at the first call rather than at the
    composition root, which is the half-injection the product refuses elsewhere."""
    assert set(cli.OBSERVE_TEMPLATE_ID) == cli.OBSERVE_CALL_SITES


# --- C and D: the seven injections, and the resolvers that must not be reached -

def test_the_seven_placement_fields_are_the_ones_r55_does_not_supply():
    """`sensitivity_policy` is the eighth and is supplied at `placement_inputs`
    whether or not a model is configured -- P8's two sensitivity checks refuse
    with it, and a refusal that needs no ratified prompt must not wait for one.
    Overwriting it from the observe builder would take a refusal away."""
    from model_placement import MODEL_PATH_FIELDS

    assert set(cli.OBSERVE_PLACEMENT_FIELDS) | {"sensitivity_policy"} == set(
        MODEL_PATH_FIELDS)
    assert "sensitivity_policy" not in cli.OBSERVE_PLACEMENT_FIELDS


@pytest.mark.parametrize("site", [C_PLACEMENT, D_RESIDUAL])
def test_an_observe_resolver_raises_rather_than_placing_a_file(site):
    """`model_path_available()` reads all eight as a set, so C and D need a
    `chosen_node_of` and a `residual_action_of` to run at all -- and the observe
    lever in `_judge_with_model` means neither is ever reached.

    They raise. A resolver that returned a plausible node would place a file on
    the strength of a validator `104` R-15 says is wrong about every real value,
    and it would do it silently the first time the lever moved. An unreachable
    branch owes the next person to make it reachable a loud failure."""
    resolve = cli._must_not_apply(site)

    with pytest.raises(cli.ObservedSiteMustNotApply, match=site):
        resolve(object())


def test_the_observe_lever_turns_a_verdict_into_an_abstention():
    """C and D apply nothing through the abstention path they already have.

    The real verdict is on disk before this runs -- `run_call` wrote it -- so what
    changes is only what P11 does next: an `ABSTAIN` outcome takes both callers
    down their existing abstention branch and neither resolver is consulted."""
    import dataclasses

    from llm_harness.vocabulary import ABSTAIN, SCHEMA_INVALID, SCOPE_NODE
    from llm_harness.records import P8Verdict, PromptDefinition
    from placement.pipeline import _observed_only

    placed = P8Verdict(
        verdict_id="v", dossier_id="d", claim_ref="c", outcome="accept_direct",
        disposition="llm_supported", reasons=(), may_propose=True,
        requires_review=False, citations_checked=(), scope=SCOPE_NODE,
        validator_version="vv", policy_version="pv", plan_version=None)
    unratified = cli.observe_prompt(C_PLACEMENT)
    # THE FIELD, not the id. A renamed draft must not start applying, and a
    # ratified prompt keeping a draft's id must not keep abstaining.
    ratified = dataclasses.replace(unratified, ratified=True)

    assert _observed_only(placed, prompt=unratified).outcome == ABSTAIN
    assert _observed_only(placed, prompt=unratified).may_propose is False
    # And a ratified site is untouched, which is what makes this reversible: the
    # loader sets the field and the site starts applying on the same run.
    assert _observed_only(placed, prompt=ratified) is placed


def test_a_refusal_is_not_rewritten_into_an_abstention():
    """A refusal, a failed call or a missing capability is already an outcome P11
    applies nothing to. Rewriting one would hide why it happened."""
    from llm_harness.records import ValidationUnavailable
    from placement.pipeline import _observed_only

    missing = ValidationUnavailable(missing=("prompt",))

    assert _observed_only(missing, prompt=cli.observe_prompt(C_PLACEMENT)) is missing


def test_the_signal_is_the_field_and_not_the_template_id():
    """The ruling in one assertion. A draft renamed to look ratified must still
    abstain, and a ratified prompt that kept a draft's id must still apply --
    otherwise the finish line's invariant rests on a naming habit."""
    import dataclasses

    from placement.pipeline import _observed_only

    draft = cli.observe_prompt(C_PLACEMENT)
    renamed = dataclasses.replace(draft, template_id="c_placement.ratified.2026")
    kept_id = dataclasses.replace(draft, ratified=True)

    from llm_harness.records import P8Verdict
    from llm_harness.vocabulary import SCOPE_NODE
    verdict = P8Verdict(
        verdict_id="v", dossier_id="d", claim_ref="c", outcome="accept_direct",
        disposition="llm_supported", reasons=(), may_propose=True,
        requires_review=False, citations_checked=(), scope=SCOPE_NODE,
        validator_version="vv", policy_version="pv", plan_version=None)

    assert _observed_only(verdict, prompt=renamed) is not verdict
    assert _observed_only(verdict, prompt=kept_id) is verdict


def test_the_fact_prompt_says_it_is_ratified_and_the_drafts_say_they_are_not():
    """`planning/82` §0 records the owner ratifying A's text; the packet's own
    `status` is `unratified`. Both are read rather than assumed."""
    assert cli.a_fact_prompt().ratified is True
    for site in cli.OBSERVE_CALL_SITES:
        assert cli.observe_prompt(site).ratified is False


# --- one seam, five sites, and no site under another's contract -------------------
#
# `104` R-05: "No ratified prompt, response schema or shaping policy for B, C, D,
# E". Four texts, four schemas and four policies now exist, and the danger the
# moment they do is that a site is asked under a NEIGHBOUR's contract: the dossier
# carries the prompt's own `response_schema` and `shaping_policy` bytes, and the
# validator dispatches on the request's site, so the two can disagree without
# anything saying so.

ALL_SITES = (A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE)

#: One valid, minimal response per site: the declining shape each site's own text
#: shows, with the enum placeholders filled from that site's own schema. Written
#: here rather than instantiated from a bench case because what is under test is
#: the SCHEMA-to-SITE binding, and a shape borrowed from the bench would be a third
#: thing that could drift.
SITE_RESPONSE = {
    A_FACT: {"claims": [{
        "payload": {"field": "subject"},
        "unknown": {"insufficiency_statement": "the text names no course"}}]},
    B_GROUP: {"claims": [{
        "payload": {"coherent": "insufficient", "basis": "generic-similarity",
                    "members": [], "outliers": []},
        "unknown": {"insufficiency_statement": "the anchors state nothing in common"}}]},
    C_PLACEMENT: {"claims": [{
        "payload": {"destination": "none", "alternatives": [],
                    "conflicts_considered": []},
        "unknown": {"insufficiency_statement": "two candidates stood and nothing separated them"}}]},
    D_RESIDUAL: {"claims": [{
        "payload": {"action": "abstain", "target": None,
                    "stop_reason": "no approved home fits",
                    "relationships_considered": []},
        "unknown": {"insufficiency_statement": "no approved home fits"}}]},
    E_TEMPLATE: {"claims": [{
        "payload": {"domain": "none"},
        "unknown": {"insufficiency_statement": "the evidence carries no dimension"}}]},
}


@pytest.mark.parametrize("site", ALL_SITES)
def test_every_call_site_resolves_its_own_prompt_through_one_seam(site):
    """`cli.prompt_for` is the one function that answers "what is this site asked
    under", for the ratified site and the four drafts alike. Two entry points would
    be two places for a site to be given the wrong text."""
    prompt = cli.prompt_for(site)

    assert prompt.call_site == site
    assert prompt.template_bytes and prompt.response_schema_bytes
    assert prompt.shaping_policy_bytes
    # Read off the definition, never parsed out of the id (`records.py`: "a string
    # test would make the invariant depend on a naming habit").
    assert prompt.ratified is (site in cli.WIRED_CALL_SITES)


def test_no_two_sites_share_a_template_a_schema_or_a_policy():
    prompts = {site: cli.prompt_for(site) for site in ALL_SITES}
    for name in ("template_id", "template_bytes", "response_schema_bytes",
                 "shaping_policy_bytes"):
        values = [getattr(prompt, name) for prompt in prompts.values()]
        assert len(set(values)) == len(ALL_SITES), name


@pytest.mark.parametrize("site", ALL_SITES)
def test_a_sites_schema_accepts_its_own_answer_and_rejects_every_other_sites(site):
    """The binding, measured rather than asserted by naming.

    A model shown one site's schema and judged against another's is "measured
    against one list and validated against another", which `model_facts` names as
    the failure that rejects a model for obeying its instructions.
    """
    import jsonschema

    own = json.loads(cli.prompt_for(site).response_schema_bytes)
    jsonschema.validate(SITE_RESPONSE[site], own)
    for other in ALL_SITES:
        if other == site:
            continue
        schema = json.loads(cli.prompt_for(other).response_schema_bytes)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(SITE_RESPONSE[site], schema)


def test_site_d_is_asked_under_site_ds_own_text(monkeypatch):
    """D was asked under C's prompt, and the comment said so.

    `_judge_with_model` serves both placement sites and read one `PipelineInputs.
    prompt`, so `observe_placement_injections` had to pick one -- and it picked C's
    template, C's response schema and C's shaping policy for a residual call. A
    residual answer names an action from a set of eight; C's schema has no `action`
    key at all, so every D answer would have been `SCHEMA_INVALID` for obeying the
    text it was shown, which was not its own either.
    """
    from placement.pipeline import PipelineInputs

    assert "residual_prompt" in PipelineInputs.__dataclass_fields__
    c_prompt = cli.prompt_for(C_PLACEMENT)
    d_prompt = cli.prompt_for(D_RESIDUAL)
    assert c_prompt.response_schema_bytes != d_prompt.response_schema_bytes
    assert c_prompt.shaping_policy_bytes != d_prompt.shaping_policy_bytes


def test_the_placement_injections_carry_a_prompt_for_each_of_the_two_sites():
    """`model_path_injections` hands over all or nothing, and "all" is now nine."""
    from model_placement import MODEL_PATH_FIELDS

    assert "prompt" in MODEL_PATH_FIELDS
    assert "residual_prompt" in MODEL_PATH_FIELDS
    assert set(cli.OBSERVE_PLACEMENT_FIELDS) | {"sensitivity_policy"} == set(
        MODEL_PATH_FIELDS)


def test_a_residual_call_with_no_residual_prompt_refuses_rather_than_borrowing_cs():
    """`None` is legal -- a deployment may wire C and not D, exactly as
    `residual_action_of` may be absent -- and the refusal happens at the moment a
    residual set actually asks for a model, which is the right moment. What must
    never happen is the fallback that was there: D asked under C's text."""
    from placement.pipeline import PipelineInputs, ResidualPromptRequired

    values = dict(
        plan_version="plan-1", tree=None, policy=None, limits=None,
        partition=None, ask_or_abstain=None, max_return_cycles=1,
        gate=object(), model_client=object(), prompt=cli.prompt_for(C_PLACEMENT),
        residual_prompt=None, call_dependencies=object(),
        model_call_request=object(), chosen_node_of=object(),
        residual_action_of=None, sensitivity_policy=object(),
        ask_about_file=None, chosen_by_user=None,
        fields_that_cannot_anchor_a_move=frozenset(),
        their_own_folder_made_for_what_it_holds={}, p2=None,
        the_folder_each_file_is_in={})
    inputs = object.__new__(PipelineInputs)
    for name, value in values.items():
        object.__setattr__(inputs, name, value)

    assert inputs.prompt_for(C_PLACEMENT) is values["prompt"]
    with pytest.raises(ResidualPromptRequired):
        inputs.prompt_for(D_RESIDUAL)
    # The control: wired, D is asked under D's own text.
    object.__setattr__(inputs, "residual_prompt", cli.prompt_for(D_RESIDUAL))
    assert inputs.prompt_for(D_RESIDUAL).call_site == D_RESIDUAL


# --- `ratified` read from the definition, at the group site too -------------------


@dataclasses.dataclass(frozen=True)
class _BDeps:
    """The two `CallDependencies` fields B's wrapper fills in per group."""

    basis_key: str = "group"
    learning_subject_id: str = "group"


def _b_result(monkeypatch, *, ratified: bool):
    """One turn of B's `p8_run_call`, with `run_call` stubbed to a token."""
    import cli as _cli

    monkeypatch.setattr(_cli, "run_call",
                        lambda *_a, **_k: "the verdict run_call produced")
    prompt = dataclasses.replace(_cli.observe_prompt(B_GROUP), ratified=ratified)
    return _cli.observed_run_call(
        None, SimpleNamespace(subject_ref="group:g-1"),
        gate=None, model_client=None, prompt=prompt,
        validation_dependencies=_BDeps(), observed_at=None)


def test_the_group_site_records_and_applies_nothing_while_its_text_is_a_draft(
        monkeypatch):
    """B's wrapper wrapped UNCONDITIONALLY and never read `prompt.ratified`.

    Every other site reads the field -- `_observed_only` at C and D,
    `PipelineInputs.model_decides` at P11 -- and B's answer was withheld by the
    SHAPE of the code instead. So the day the owner ratifies `anchors-first-v3`,
    A, C and D would start applying and B would go on discarding, and nothing in
    the product would say why."""
    from grouping.p8_seam import ObservedOnly

    result = _b_result(monkeypatch, ratified=False)

    assert isinstance(result, ObservedOnly)
    assert result.result == "the verdict run_call produced"


def test_the_group_site_applies_its_answer_once_the_owner_ratifies_the_text(
        monkeypatch):
    """The other half, and it is the reversibility the finish line needs: the
    loader sets the field from the manifest and the site starts applying on the
    same run, with no line of `cli.py` changing.

    A token that is not a `P8Verdict` has no answer to read, so it comes back
    wrapped -- "record and apply nothing" is the safe direction for anything this
    root cannot account for. `test_r16_*` below drives the same wrapper with a real
    verdict and a real response row."""
    from grouping.p8_seam import ObservedOnly

    result = _b_result(monkeypatch, ratified=True)

    assert isinstance(result, ObservedOnly)


# --- `104` R-16: the composition root reads the model's four answers -------------


def _b_verdict(dossier_id="ds-b1"):
    from llm_harness.records import P8Verdict

    return P8Verdict(
        verdict_id=f"{dossier_id}:claim-0", dossier_id=dossier_id,
        claim_ref="claim-0", outcome="accept_direct",
        disposition="direct_membership", reasons=(), may_propose=True,
        requires_review=False, citations_checked=(), scope="group",
        validator_version="vv", policy_version="pv", plan_version=None)


def _b_response(conn, dossier_id, payload, *, citations=None):
    from llm_harness.store import record_response

    body = {"payload": payload}
    if citations is not None:
        body["citations"] = citations
    record_response(
        conn, dossier_id=dossier_id,
        response_bytes=json.dumps({"claims": [body]}).encode("utf-8"),
        model_id="fixture", prompt_fingerprint="fp", release_audit_id=1,
        release_id="rel-1", observed_at="2026-09-07T00:00:00Z")


@pytest.fixture()
def harness_db(tmp_path):
    from database_agent.db import create_schema, open_database
    from llm_harness.schema import create_llm_schema

    conn = open_database(tmp_path / "b.sqlite")
    create_schema(conn)
    create_llm_schema(conn)
    try:
        yield conn
    finally:
        conn.close()


def test_r16_the_root_reads_the_models_four_answers_off_its_own_response(
        harness_db):
    """`P8Verdict` carries a `claim_ref` and no payload, so §4.5's four answers
    reach P9 only if whoever supplied the prompt reads them back. `src/grouping/`
    may not import `llm_harness.records` at all, which is why this is here."""
    from grouping.vocabulary import COHERENT, EXCLUDED, INCLUDED, UNCERTAIN

    _b_response(harness_db, "ds-b1", {
        "coherent": "yes", "basis": "direct-anchor", "category": "academic",
        "label": "PHYS1401 course materials",
        "members": [
            {"file_id": "lecture-08", "decision": "include", "why": "states it",
             "evidence_refs": []},
            {"file_id": "midterm", "decision": "exclude", "why": "another course",
             "evidence_refs": []},
            {"file_id": "hw-3", "decision": "uncertain", "why": "retrieved only",
             "evidence_refs": []}],
        "outliers": [], "merge_terms": []},
        citations=[{"evidence_ref": "obs-1", "cited_span": "PHYS1401",
                    "why_it_supports": "states the course"}])

    answer = cli.group_answer_of(harness_db, _b_verdict())

    assert answer.coherent == COHERENT
    assert answer.label == "PHYS1401 course materials"
    assert answer.category == "academic"
    assert answer.citations == ("obs-1",)
    assert [(m.file_id, m.decision) for m in answer.members] == [
        ("lecture-08", INCLUDED), ("midterm", EXCLUDED), ("hw-3", UNCERTAIN)]


def test_r16_the_two_vocabularies_are_translated_at_the_root_and_nowhere_else(
        harness_db):
    """The schema's words are `include`/`exclude`/`uncertain` and `yes`/`no`/
    `insufficient`; P9's are `MEMBERSHIP_DECISIONS` and `COHERENCE_VERDICTS`. A
    table inside `src/grouping/` would be a second copy of a contract the prompt
    owns, and `test_only_the_vocabulary_module_spells_a_closed_p9_value` refuses
    the literals there. `insufficient` is `abstained` and not `not-coherent`: "I
    could not tell" is a different answer from "these are not one group"."""
    from grouping.vocabulary import (
        ABSTAINED, COHERENCE_VERDICTS, MEMBERSHIP_DECISIONS, NOT_COHERENT,
    )

    assert set(cli.GROUP_MEMBER_DECISION.values()) == set(MEMBERSHIP_DECISIONS)
    assert set(cli.GROUP_COHERENCE.values()) <= set(COHERENCE_VERDICTS)
    assert cli.GROUP_COHERENCE["insufficient"] == ABSTAINED
    assert cli.GROUP_COHERENCE["no"] == NOT_COHERENT


def test_r16_an_answer_this_root_cannot_read_records_and_applies_nothing(
        harness_db, monkeypatch):
    """Every unreadable shape is one outcome and it is the safe one. Returning the
    bare verdict would put back exactly the blanket memberships R-16 names."""
    from grouping.p8_seam import ObservedOnly

    # No response row at all.
    assert cli.group_answer_of(harness_db, _b_verdict()) is None
    # A response that is not JSON.
    from llm_harness.store import record_response
    record_response(harness_db, dossier_id="ds-b2", response_bytes=b"not json",
                    model_id="m", prompt_fingerprint="fp", release_audit_id=1,
                    release_id="rel-2", observed_at="2026-09-07T00:00:00Z")
    assert cli.group_answer_of(harness_db, _b_verdict("ds-b2")) is None
    # And a verdict that is not one.
    assert cli.group_answer_of(harness_db, "a refusal") is None

    monkeypatch.setattr(cli, "run_call", lambda *_a, **_k: _b_verdict("ds-b3"))
    wrapped = cli.observed_run_call(
        harness_db, SimpleNamespace(subject_ref="group:g-1"),
        gate=None, model_client=None,
        prompt=dataclasses.replace(cli.observe_prompt(B_GROUP), ratified=True),
        validation_dependencies=_BDeps(), observed_at=None)
    assert isinstance(wrapped, ObservedOnly)


def test_r16_a_readable_answer_reaches_the_seam_as_answered(harness_db,
                                                            monkeypatch):
    """The whole boundary in one turn: `run_call` writes the response, this root
    reads it back at the moment it is the last one for that dossier, and the seam
    receives the verdict and the answer together."""
    from grouping.p8_seam import Answered

    _b_response(harness_db, "ds-b4", {
        "coherent": "yes", "basis": "direct-anchor", "category": "academic",
        "label": "PHYS1401 course materials",
        "members": [{"file_id": "lecture-08", "decision": "include",
                     "why": "states it", "evidence_refs": []}],
        "outliers": [], "merge_terms": []},
        citations=[{"evidence_ref": "obs-1", "cited_span": "PHYS1401",
                    "why_it_supports": "states the course"}])
    monkeypatch.setattr(cli, "run_call", lambda *_a, **_k: _b_verdict("ds-b4"))

    wrapped = cli.observed_run_call(
        harness_db, SimpleNamespace(subject_ref="group:g-1"),
        gate=None, model_client=None,
        prompt=dataclasses.replace(cli.observe_prompt(B_GROUP), ratified=True),
        validation_dependencies=_BDeps(), observed_at=None)

    assert isinstance(wrapped, Answered)
    assert wrapped.answer.label == "PHYS1401 course materials"
    assert wrapped.result.dossier_id == "ds-b4"

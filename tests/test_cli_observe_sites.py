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
    DRAFT_STATUS_WORDS, DraftNotInManifest, RATIFIED, RATIFIED_LOCAL,
    UNRATIFIED, draft_bytes, draft_row, draft_status, drafts_status,
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


@pytest.mark.parametrize("site", sorted(s for s in WINNERS if s != C_PLACEMENT))
def test_an_observe_site_is_refused_a_cloud_model(site):
    """The count `104` §13 keeps, kept in code. Unratified text is text nobody has
    agreed to send: on this device that is a question of taste, and over the
    internet it is a person's dossier reaching a provider under a prompt their
    owner never approved, and it cannot be taken back."""
    assert cli.observe_locality_permits(site, LOCAL) is True
    assert cli.observe_locality_permits(site, CLOUD) is False
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget, match=site):
        cli.require_observe_locality(site, CLOUD)


def test_the_refusal_says_this_drafts_status_in_the_manifests_own_word():
    """Read from the manifest, never remembered here: if the owner ratifies this
    draft the sentence stops claiming otherwise without anyone editing it.

    THE DRAFT'S WORD AND NOT THE PACKET'S. The packet's word is only the default a
    silent row inherits, so a sentence quoting it can be false about the row it is
    refusing; the inverse case is pinned below. Today the two coincide."""
    # B is the unratified site since C's row was ratified on 7 Sep 2026.
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget) as caught:
        cli.require_observe_locality(B_GROUP, CLOUD)

    assert repr(draft_status(WINNERS[B_GROUP])) in str(caught.value)
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
    # C's real row is ratified since 7 Sep 2026, so the unratified premise is set
    # on the field here rather than read off the manifest.
    unratified = dataclasses.replace(cli.observe_prompt(C_PLACEMENT), ratified=False)
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

    # An UNRATIFIED draft is the premise; C's real row is ratified since 7 Sep,
    # so the field is set here rather than read off the manifest.
    draft = dataclasses.replace(cli.observe_prompt(C_PLACEMENT), ratified=False)
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
    # 7 Sep 2026: the owner ratified C's eliminate-v2 row (manifest `status`
    # on that row); B, D and E stay under the packet's word.
    for site in cli.OBSERVE_CALL_SITES:
        assert cli.observe_prompt(site).ratified is (site == C_PLACEMENT)


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
    assert prompt.ratified is (site in cli.WIRED_CALL_SITES or site == C_PLACEMENT)


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
        the_folder_each_file_is_in={},
        a_move_the_person_has_not_permitted=None)
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


class _LocalClient:
    """A model on this device, as `observe_group_authorities` reads one."""

    model_target = SimpleNamespace(locality=LOCAL)


class _LocalRouting:
    """`TierRouting`, reduced to the two questions the B seam asks it."""

    def locality_for(self, _call_site: str) -> str:
        return LOCAL

    def client_for(self, _call_site: str):
        return _LocalClient()


def _fact_authorities_with(**overrides):
    """Site A's authorities, reduced to the fields B borrows from them."""
    borrowed = dict(
        gate=object(), evidence_resolver=lambda key: None,
        # A REAL `ScanBudget` since `104` R-131's merge, and the stub that was
        # here is why it has to be: the observe sites no longer take A's budget
        # object, they derive their own from it (`cli.observe_scan_budget`), so a
        # bare `object()` here stopped standing for the one field it stood for.
        scan_budget=_fact_budget("scan-stub"), estimated_cost=1, actual_cost=1,
        policy_version="pv", wire_handle_key=b"k", observed_at=lambda: "T",
        usage_recorder=None)
    borrowed.update(overrides)
    return SimpleNamespace(**borrowed)


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


def test_the_template_site_asks_nobody_when_there_is_no_model_on_this_device():
    """Packet G12's caller, and `None` is the ordinary deployment.

    Same three terms as site B's builder: no routing, or E's tier does not resolve
    to a model on this device. A run that asks nobody designs the branch exactly as
    it always has, and the C3 refusal still reaches the person through the report.
    """
    import cli as _cli

    assert _cli.observe_template_call(
        None, _fact_authorities_with(), routing=None, catalogue=object()) is None


def test_the_template_site_asks_under_its_own_text_and_applies_nothing(monkeypatch):
    """`104` R-05's seam at the fifth site, and `00`:97's own last sentence.

    Site E is the one site where observe-only is not a lever waiting to be moved:
    "valid shape is not activation -- the person reviews, edits and accepts or
    discards", and that canvas is Release 2. So the prompt is E's own, the call is
    made and recorded, and nothing this chain does reads a result -- the caller
    returns `None` by signature.
    """
    import cli as _cli
    from llm_harness.vocabulary import E_TEMPLATE as E

    seen = {}

    def spy(_conn, request, **keywords):
        seen["request"] = request
        seen["prompt"] = keywords["prompt"]
        seen["usage_recorder"] = keywords["usage_recorder"]
        return "recorded, applied to nothing"

    monkeypatch.setattr(_cli, "run_call", spy)
    monkeypatch.setattr(_cli, "template_request_for",
                        lambda *_a, **_k: SimpleNamespace(call_site=E))
    # A REAL `TemplateDependencies`, because `SiteDependencies` refuses anything
    # else by name -- P8 owns which validator runs at each site.
    from llm_harness.template_validation import TemplateDependencies

    monkeypatch.setattr(_cli, "template_dependencies", lambda _c: (
        TemplateDependencies(schema_validator=lambda _p: True,
                             published_fragment=lambda _i, _v: True)))
    monkeypatch.setattr(_cli, "allowed_vocabulary_for", lambda _c, **_k: ())

    mailbox = _cli.UsageMailbox()
    ask = _cli.observe_template_call(
        None, _fact_authorities_with(usage_recorder=mailbox),
        routing=_LocalRouting(), catalogue=object())
    assert ask is not None
    assert ask([SimpleNamespace(group_id="g-1", members=(), domain="academic")],
               "plan-1") is None

    assert seen["request"].call_site == E
    assert seen["prompt"].call_site == E
    assert seen["prompt"].template_id == cli.OBSERVE_TEMPLATE_ID[E]
    assert seen["usage_recorder"] is mailbox


def test_the_group_seam_hands_run_call_the_same_mailbox_site_a_reads(monkeypatch):
    """`104` R-71. B's response had no `llm_call_usage` row and A's had one each.

    The sink is A's own -- one mailbox, filled by the transport `model_route` built
    -- and it is bound at the seam rather than added to `ModelCallAuthorities`,
    because that bundle is exactly `run_call`'s keywords as P9 forwards them and P9
    can construct no mailbox. Both halves are asserted: the value reaches `run_call`
    under its own keyword, and the BUNDLE still does not carry it, which is what
    `NOT_P9_AUTHORITIES` says about P9 and must go on being true.
    """
    import dataclasses as _dc

    import cli as _cli
    from grouping.pipeline import ModelCallAuthorities

    mailbox = _cli.UsageMailbox()
    seen = {}

    def spy(_conn, _request, **keywords):
        seen.update(keywords)
        return "the verdict run_call produced"

    monkeypatch.setattr(_cli, "run_call", spy)
    p8_run_call, authorities = _cli.observe_group_authorities(
        _fact_authorities_with(usage_recorder=mailbox),
        routing=_LocalRouting(), situation="academic.coursework")

    # P9's own forwarding, spelled the way `grouping.pipeline` spells it.
    p8_run_call(
        None, SimpleNamespace(subject_ref="group:g-1"),
        gate=authorities.gate, model_client=authorities.model_client,
        prompt=authorities.prompt,
        validation_dependencies=authorities.validation_dependencies,
        observed_at=authorities.observed_at)

    assert seen["usage_recorder"] is mailbox
    assert "usage_recorder" not in {
        field.name for field in _dc.fields(ModelCallAuthorities)}


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


# --- P1: one status word per draft, so one site can be ratified alone --------
#
# `104` §15.1's first blocker. The packet manifest carried ONE `status` for B, C,
# D and E together and `observe_prompt` read it for every observe site, so the
# owner could not ratify C's `eliminate-v2` -- the one text with a measured row
# behind it -- without also ratifying D and E, which have never produced one.
#
# The fixture manifest is a COPY of the real library directory with the manifest
# JSON rewritten in place, so the digests in it still verify against the real
# bytes beside it and `draft_bytes` loads for real. Nothing under `src/` is
# touched by any test here, and the last test below is the pin that says so.


@pytest.fixture
def manifest_with(tmp_path, monkeypatch):
    """Point the library at a copy of itself whose manifest rows say what a test
    needs, and put it back afterwards.

    `_manifest` is `lru_cache`d, so the cache is cleared on BOTH sides: leaving a
    fixture manifest cached would make the next test read it instead of the real
    file, and under `pytest-randomly` the next test is not the one you wrote it
    after.
    """
    import shutil

    from llm_harness import prompt_library

    def point_at(mutate):
        library = tmp_path / "library"
        shutil.copytree(prompt_library.DRAFTS_FILE.parent, library)
        manifest = json.loads(
            prompt_library.DRAFTS_FILE.read_text(encoding="utf-8"))
        mutate(manifest)
        path = library / prompt_library.DRAFTS_FILE.name
        path.write_text(json.dumps(manifest), encoding="utf-8")
        monkeypatch.setattr(prompt_library, "DRAFTS_FILE", path)
        prompt_library._manifest.cache_clear()
        return path

    prompt_library._manifest.cache_clear()
    yield point_at
    prompt_library._manifest.cache_clear()


def _set_row_status(template_id, status):
    """A mutation for `manifest_with`: give one row its own `status` word."""
    def mutate(manifest):
        rows = [row for row in manifest["drafts"]
                if row.get("template_id") == template_id]
        assert rows, f"no row for {template_id} to give a status to"
        for row in rows:
            row["status"] = status
    return mutate


def test_a_ratified_row_ratifies_its_own_site_and_leaves_the_other_three(
        manifest_with):
    """`104` §15.1: C's `eliminate-v2` is the text with a measured row behind it
    and the shortest path to a real exact number. D and E have never produced one
    and must not start applying because C did. One word on one row, and the packet
    still says `unratified` over all of them."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED))

    assert drafts_status() == "unratified"
    assert cli.observe_prompt(C_PLACEMENT).ratified is True
    for site in (B_GROUP, D_RESIDUAL, E_TEMPLATE):
        assert cli.observe_prompt(site).ratified is False


def test_the_ratified_rows_id_still_says_unratified_and_still_loads_its_bytes(
        manifest_with):
    """The id names the FILE, not the file's standing. Renaming it on ratification
    would strand every record already written under the old id, so what a record
    says is WHICH TEXT was used and the manifest row says whether that text was
    ratified at the time."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED))

    prompt = cli.observe_prompt(C_PLACEMENT)

    assert "unratified" in prompt.template_id
    assert prompt.template_id == WINNERS[C_PLACEMENT]
    assert prompt.ratified is True
    assert draft_bytes(prompt.template_id)[0] == prompt.template_bytes


def test_a_row_with_no_status_of_its_own_is_under_the_packets_word(
        manifest_with):
    """Inheritance keeps the packet meaningful -- one line still moves every row
    that has not spoken for itself -- and it keeps the safe default, which is what
    the real manifest relies on today."""
    from llm_harness.prompt_library import draft_status

    silent = sorted(s for s in WINNERS if s != C_PLACEMENT)
    for site in silent:
        assert "status" not in draft_row(WINNERS[site])
        assert draft_status(WINNERS[site]) == "unratified"
    assert "status" in draft_row(WINNERS[C_PLACEMENT])  # ratified 7 Sep 2026

    def ratify_the_packet(manifest):
        manifest["status"] = "ratified"

    manifest_with(ratify_the_packet)

    assert drafts_status() == "ratified"
    for site in silent:
        assert draft_status(WINNERS[site]) == "ratified"
        assert cli.observe_prompt(site).ratified is True


def test_a_status_word_nobody_defined_is_refused_before_any_call(manifest_with):
    """`ratified` is read as an equality test, so `pending` is not a third state:
    it would read as 'not ratified' and look like a decision somebody made. The
    refusal names the row rather than the packet, so a reader knows which line to
    fix."""
    from llm_harness.prompt_library import draft_status

    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], "pending"))

    with pytest.raises(DraftNotInManifest, match="eliminate-v2") as caught:
        draft_status(WINNERS[C_PLACEMENT])
    assert "pending" in str(caught.value)

    # And the same refusal on the path a run actually takes, before a byte of a
    # person's file has been read.
    with pytest.raises(DraftNotInManifest, match="pending"):
        cli.observe_prompt(C_PLACEMENT)
    with pytest.raises(DraftNotInManifest, match="pending"):
        cli.observe_locality_permits(C_PLACEMENT, CLOUD)

    # A neighbour that said nothing is unharmed: one bad row is one bad row.
    assert cli.observe_prompt(B_GROUP).ratified is False


def test_a_packet_status_word_nobody_defined_is_refused_too(manifest_with):
    """The packet's word is the default every silent row inherits, so an
    unrecognised word there is the same defect wearing a wider hat."""
    from llm_harness.prompt_library import draft_status

    def mutate(manifest):
        manifest["status"] = "Ratified"

    manifest_with(mutate)

    with pytest.raises(DraftNotInManifest, match="Ratified"):
        drafts_status()
    # A row that carries its own word does not read the packet's, so the
    # inheriting site is the one that sees the bad packet word.
    with pytest.raises(DraftNotInManifest, match="Ratified"):
        draft_status(WINNERS[B_GROUP])


def test_two_rows_naming_one_text_and_disagreeing_about_status_is_refused(
        manifest_with):
    """Two rows may share an id -- A_fact's glossary arms are two glossaries over
    one template -- and that is not an error. Two rows sharing an id and
    DISAGREEING about status is, for the reason `draft_row` refuses rows that
    disagree about files: the pick between them would be arbitrary, and the thing
    being picked is whether the owner approved this text."""
    from llm_harness.prompt_library import (
        DraftManifestAmbiguous, draft_status,
    )

    a_fact_id = "a_fact.unratified.folder-levels.2026-09-04"

    def mutate(manifest):
        rows = [row for row in manifest["drafts"]
                if row.get("template_id") == a_fact_id]
        assert len(rows) > 1, "this test needs the shared-id rows to still exist"
        rows[0]["status"] = "ratified"
        rows[1]["status"] = "unratified"

    manifest_with(mutate)

    with pytest.raises(DraftManifestAmbiguous, match=a_fact_id):
        draft_status(a_fact_id)


def test_a_template_id_nobody_published_has_no_status_either():
    """Absent means refuse, never guess -- and a status invented for an id nobody
    published would be a standing the owner never gave any text."""
    from llm_harness.prompt_library import draft_status

    with pytest.raises(DraftNotInManifest, match="anchors-first-v9"):
        draft_status("b_group.unratified.anchors-first-v9.2026-09-06")


def test_the_cloud_refusal_lifts_for_the_ratified_site_and_holds_for_the_rest(
        manifest_with):
    """What `104` §13's count counts is CLOUD CALLS WITH UNRATIFIED PROMPTS, so
    the gate is the text's standing and not the site's name. `ratified` is the
    word that says these bytes may leave the device, and it says it about one
    draft."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED))

    assert cli.observe_locality_permits(C_PLACEMENT, CLOUD) is True
    cli.require_observe_locality(C_PLACEMENT, CLOUD)

    for site in (B_GROUP, D_RESIDUAL, E_TEMPLATE):
        assert cli.observe_locality_permits(site, CLOUD) is False
        with pytest.raises(cli.UnratifiedPromptOnACloudTarget, match=site):
            cli.require_observe_locality(site, CLOUD)

    # LOCAL is untouched on both sides of the line.
    for site in sorted(WINNERS):
        assert cli.observe_locality_permits(site, LOCAL) is True


def test_the_real_manifest_on_disk_ratifies_c_alone():
    """THE PIN. On 7 Sep 2026 the owner ratified C's eliminate-v2 row and nothing
    else, FOR THE LOCAL MODEL (`104` §15.1: the cloud waits on R-82), so the row's
    word is `ratified_local`: the packet's word stays `unratified`, B, D and E
    inherit it, and the manifest is the owner's to edit and nobody else's. C's
    cloud target is refused by this word, and not by whichever model happens to
    be configured -- the gate is the text's standing, in code."""
    from llm_harness.prompt_library import draft_status

    assert drafts_status() == UNRATIFIED
    for site in sorted(WINNERS):
        expected = site == C_PLACEMENT
        word = RATIFIED_LOCAL if expected else UNRATIFIED
        assert draft_status(WINNERS[site]) == word, site
        assert ("status" in draft_row(WINNERS[site])) is expected, site
        # The site acts on its answer, and its text still does not leave the
        # device: the local word applies and does not cross.
        assert cli.observe_prompt(site).ratified is expected, site
        assert cli.observe_locality_permits(site, LOCAL) is True, site
        assert cli.observe_locality_permits(site, CLOUD) is False, site


# --- P2: the real resolvers behind C and D, and the stub that guards a draft ------


def _cd_verdict(dossier_id, *, claim_ref="claim-0", scope="file",
                outcome="accept_direct", disposition="move_plan_eligible"):
    from llm_harness.records import P8Verdict

    return P8Verdict(
        verdict_id=f"{dossier_id}:{claim_ref}", dossier_id=dossier_id,
        claim_ref=claim_ref, outcome=outcome, disposition=disposition,
        reasons=(), may_propose=True, requires_review=False,
        citations_checked=(), scope=scope, validator_version="vv",
        policy_version="pv", plan_version="plan-1")


def _cd_response(conn, dossier_id, claims):
    from llm_harness.store import record_response

    record_response(
        conn, dossier_id=dossier_id,
        response_bytes=json.dumps({"claims": claims}).encode("utf-8"),
        model_id="fixture", prompt_fingerprint="fp", release_audit_id=1,
        release_id="rel-c", observed_at="2026-09-07T00:00:00Z")


def test_p2_the_c_resolver_reads_the_destination_off_the_validated_answer(
        harness_db):
    """`P8Verdict` names a `claim_ref` and not a destination, so which node the
    model chose can only be read by whoever supplied the prompt. This is site C's
    half of what `group_answer_of` does at site B, and it re-validates nothing:
    P8's `INVENTED_NODE` has already refused any destination outside the shortlist
    P11 showed the model."""
    _cd_response(harness_db, "ds-c1", [{
        "payload": {"destination": "n-course-shared", "support": 1,
                    "next_support": 0, "refinement": "not_applicable"}}])

    assert cli._chosen_node_of(harness_db)(_cd_verdict("ds-c1")) == (
        "n-course-shared")


def test_p2_the_resolver_reads_the_claim_the_verdict_judged_and_not_the_first(
        harness_db):
    """The verdict says WHICH claim it judged. Taking `claims[0]` by position is
    right for today's one-claim schema and wrong the day one allows two, and the
    effective ref is `validation._validate_claim`'s own rule -- the claim's own
    `claim_ref` when it has one, `claim-<index>` otherwise."""
    _cd_response(harness_db, "ds-c2", [
        {"payload": {"destination": "n-general"}},
        {"claim_ref": "second", "payload": {"destination": "n-course-shared"}}])

    resolve = cli._chosen_node_of(harness_db)

    assert resolve(_cd_verdict("ds-c2", claim_ref="claim-0")) == "n-general"
    assert resolve(_cd_verdict("ds-c2", claim_ref="second")) == "n-course-shared"


def test_p2_the_d_resolver_reads_the_action_and_the_target_it_names(harness_db):
    """§7.7's action is in the response and nowhere else: P8 rewrites it into a
    coarser `disposition` where `residual_destination` covers both the destination
    choice and the broad parent. `target` is passed through as the answer carries
    it, and `outcome_for_action` owns which actions may have one."""
    _cd_response(harness_db, "ds-d1", [{
        "payload": {"action": "choose_approved_residual_destination",
                    "target": "n-review-later", "stop_reason": "recorded"}}])
    _cd_response(harness_db, "ds-d2", [{
        "payload": {"action": "mark_review_later", "target": None,
                    "stop_reason": "recorded"}}])

    resolve = cli._residual_action_of(harness_db)

    assert resolve(_cd_verdict("ds-d1", scope="file")) == (
        "choose_approved_residual_destination", "n-review-later")
    assert resolve(_cd_verdict("ds-d2", scope="file")) == (
        "mark_review_later", None)


@pytest.mark.parametrize("resolver", ["_chosen_node_of", "_residual_action_of"])
def test_p2_an_answer_this_root_cannot_read_raises_rather_than_guessing(
        harness_db, resolver):
    """Unreachable unless the row `run_call` wrote is gone: a verdict P8 accepted
    was produced by parsing the response, and `issue` recorded the bytes before the
    validator ran. Raised rather than turned into an abstention, for the reason
    `place_file` already raises three lines below `chosen_node_of` -- naming one of
    §6.10's closed reasons would record a conclusion nothing reached, and placing
    on a guess would file a file the model never chose."""
    from llm_harness.store import record_response

    resolve = getattr(cli, resolver)(harness_db)

    # No response row for the dossier at all.
    with pytest.raises(cli.PlacementAnswerUnreadable):
        resolve(_cd_verdict("ds-missing"))
    # Bytes that no longer parse.
    record_response(harness_db, dossier_id="ds-bad", response_bytes=b"not json",
                    model_id="m", prompt_fingerprint="fp", release_audit_id=1,
                    release_id="rel-bad", observed_at="2026-09-07T00:00:00Z")
    with pytest.raises(cli.PlacementAnswerUnreadable):
        resolve(_cd_verdict("ds-bad"))
    # A response carrying no claim the verdict judged.
    _cd_response(harness_db, "ds-other", [{"claim_ref": "elsewhere",
                                           "payload": {"destination": "n-x",
                                                       "action": "abstain"}}])
    with pytest.raises(cli.PlacementAnswerUnreadable):
        resolve(_cd_verdict("ds-other", claim_ref="claim-0"))


def _placement_injections(monkeypatch, conn, *, ratified):
    """`observe_placement_injections` with C's and D's text ratified or not.

    The prompt is composed by `prompt_for`, and the FIELD is what every reader in
    the product tests -- `_observed_only`, `PipelineInputs.model_decides`,
    `observed_run_call`. So the lever moved here is the field and never the
    manifest, which is the owner's and not an agent's.
    """
    import cli as _cli

    monkeypatch.setattr(_cli, "prompt_for", lambda site: dataclasses.replace(
        _cli.observe_prompt(site), ratified=ratified))
    return _cli.observe_placement_injections(
        conn, _fact_authorities_with(contradicts=lambda *_a, **_k: False),
        routing=_LocalRouting(), plan_version="plan-1")


def test_p2_an_unratified_site_is_wired_to_the_stub_that_raises(harness_db,
                                                                monkeypatch):
    """The observe state, unchanged. Both resolvers are present -- `model_path_
    available()` reads them as a set and C and D could not run without them -- and
    both refuse to apply an answer, because the abstention that keeps them
    unreachable is in `_judge_with_model` and a resolver that returned a plausible
    node under text nobody approved would place a file silently."""
    built = _placement_injections(monkeypatch, harness_db, ratified=False)

    assert set(cli.OBSERVE_PLACEMENT_FIELDS) <= set(built)
    for field, site in (("chosen_node_of", C_PLACEMENT),
                        ("residual_action_of", D_RESIDUAL)):
        with pytest.raises(cli.ObservedSiteMustNotApply, match=site):
            built[field](object())


def test_p2_a_ratified_site_is_wired_to_the_resolver_that_reads_the_answer(
        harness_db, monkeypatch):
    """The last step of turning site C on, and the only one left after P1.

    The composition root picks per site off that site's OWN prompt, so ratifying
    C's text alone gives C the real reader and leaves D's stub in place. Asserted
    by behaviour and not by identity: the wired callable reads the response row
    `run_call` wrote and answers with the node the model named."""
    _cd_response(harness_db, "ds-c3", [{
        "payload": {"destination": "n-course-shared"}}])
    _cd_response(harness_db, "ds-d3", [{
        "payload": {"action": "leave_in_current_location", "target": None}}])

    built = _placement_injections(monkeypatch, harness_db, ratified=True)

    assert built["chosen_node_of"](_cd_verdict("ds-c3")) == "n-course-shared"
    assert built["residual_action_of"](_cd_verdict("ds-d3")) == (
        "leave_in_current_location", None)


def test_p2_each_site_is_turned_on_by_its_own_prompt_and_not_by_its_neighbours(
        harness_db, monkeypatch):
    """C and D are ratified separately -- that is the whole point of P1's per-draft
    status -- so one shared read of `ratified` would turn D on with C. Ratify C
    alone and D keeps the stub."""
    import cli as _cli

    monkeypatch.setattr(_cli, "prompt_for", lambda site: dataclasses.replace(
        _cli.observe_prompt(site), ratified=site == C_PLACEMENT))
    _cd_response(harness_db, "ds-c4", [{"payload": {"destination": "n-general"}}])

    built = _cli.observe_placement_injections(
        harness_db, _fact_authorities_with(contradicts=lambda *_a, **_k: False),
        routing=_LocalRouting(), plan_version="plan-1")

    assert built["chosen_node_of"](_cd_verdict("ds-c4")) == "n-general"
    with pytest.raises(cli.ObservedSiteMustNotApply, match=D_RESIDUAL):
        built["residual_action_of"](object())


# --- P1 follow-up: ratifying is not the same act as opening the cloud --------
#
# `104` §15.1 and `105` §12.1 put C's `eliminate-v2` to the owner FOR THE LOCAL
# MODEL, with the cloud waiting on R-82's signature. With one word for "approved"
# those are one act: the word that lets a site act on its answer is the word that
# lets its text cross the internet, so the owner would have to grant both to get
# either. `ratified_local` is the word that separates them.


def test_the_status_vocabulary_is_three_closed_words():
    """A word outside the list is not a further state -- every reader tests
    membership, so an unrecognised word reads as 'not approved'."""
    assert DRAFT_STATUS_WORDS == {UNRATIFIED, RATIFIED_LOCAL, RATIFIED}
    assert (UNRATIFIED, RATIFIED_LOCAL, RATIFIED) == (
        "unratified", "ratified_local", "ratified")


def test_what_each_word_buys_is_two_questions_and_not_one():
    """Asserted at `cli` import as well, so a typo is loud before a corpus is
    read: a mistyped set never matches, which is an approval that never takes
    effect or a gate that never opens, and a run would look normal throughout."""
    assert cli.STATUS_APPLIES == {RATIFIED_LOCAL, RATIFIED}
    assert cli.STATUS_MAY_CROSS_THE_INTERNET == {RATIFIED}
    assert cli.STATUS_APPLIES <= DRAFT_STATUS_WORDS
    # Crossing implies applying: text nobody will act on has no business on the
    # internet either.
    assert cli.STATUS_MAY_CROSS_THE_INTERNET < cli.STATUS_APPLIES
    assert UNRATIFIED not in cli.STATUS_APPLIES


def test_ratified_local_acts_on_its_answer_and_is_still_refused_the_cloud(
        manifest_with):
    """The word the owner was actually asked for. C acts on its placement here
    and its text does not leave the device; R-82 is the signature the cloud waits
    on, and it is a different question about a person's folder labels."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED_LOCAL))

    assert draft_status(WINNERS[C_PLACEMENT]) == RATIFIED_LOCAL
    assert cli.observe_prompt(C_PLACEMENT).ratified is True

    assert cli.observe_locality_permits(C_PLACEMENT, LOCAL) is True
    cli.require_observe_locality(C_PLACEMENT, LOCAL)

    assert cli.observe_locality_permits(C_PLACEMENT, CLOUD) is False
    with pytest.raises(cli.UnratifiedPromptOnACloudTarget, match=C_PLACEMENT):
        cli.require_observe_locality(C_PLACEMENT, CLOUD)


def test_ratified_local_ratifies_one_site_and_leaves_the_other_three_alone(
        manifest_with):
    """The per-draft rule and the per-reach rule are independent: one word on one
    row moves that row's site and nothing else, whichever of the two words it is.
    D and E have no measured row and must not start applying because C did."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED_LOCAL))

    for site in (B_GROUP, D_RESIDUAL, E_TEMPLATE):
        assert draft_status(WINNERS[site]) == UNRATIFIED
        assert cli.observe_prompt(site).ratified is False
        assert cli.observe_locality_permits(site, CLOUD) is False


def test_the_full_word_lifts_both_and_the_local_word_lifts_only_the_first(
        manifest_with):
    """The two words side by side, which is the whole of the difference: both
    apply, one crosses."""
    manifest_with(_set_row_status(WINNERS[C_PLACEMENT], RATIFIED))

    assert cli.observe_prompt(C_PLACEMENT).ratified is True
    assert cli.observe_locality_permits(C_PLACEMENT, CLOUD) is True
    cli.require_observe_locality(C_PLACEMENT, CLOUD)


def test_the_cloud_refusal_names_this_drafts_word_and_not_the_packets(
        manifest_with):
    """The inverse case, and the reason the sentence changed. A packet reading
    `ratified` over a row that says `unratified` would print "a D2 DRAFT
    ('ratified')" and send a reader to argue with the wrong line."""
    def packet_ratified_row_not(manifest):
        manifest["status"] = RATIFIED
        for row in manifest["drafts"]:
            if row.get("template_id") == WINNERS[C_PLACEMENT]:
                row["status"] = UNRATIFIED

    manifest_with(packet_ratified_row_not)

    assert drafts_status() == RATIFIED
    assert draft_status(WINNERS[C_PLACEMENT]) == UNRATIFIED

    with pytest.raises(cli.UnratifiedPromptOnACloudTarget) as caught:
        cli.require_observe_locality(C_PLACEMENT, CLOUD)

    sentence = str(caught.value)
    assert repr(UNRATIFIED) in sentence
    assert repr(RATIFIED) not in sentence


def test_a_ratified_local_row_is_refused_the_cloud_while_a_sibling_crosses(
        manifest_with):
    """Two words in one manifest at once. Neither site borrows the other's reach:
    the gate asks each draft its own word."""
    def two_words(manifest):
        for row in manifest["drafts"]:
            if row.get("template_id") == WINNERS[C_PLACEMENT]:
                row["status"] = RATIFIED_LOCAL
            elif row.get("template_id") == WINNERS[B_GROUP]:
                row["status"] = RATIFIED

    manifest_with(two_words)

    assert cli.observe_prompt(C_PLACEMENT).ratified is True
    assert cli.observe_prompt(B_GROUP).ratified is True
    assert cli.observe_locality_permits(C_PLACEMENT, CLOUD) is False
    assert cli.observe_locality_permits(B_GROUP, CLOUD) is True


# --- `104` R-131's merge: the observe sites' own ledger -----------------------

def _fact_budget(scan_id: str = "scan-1", *, files: int = 6):
    """The fact pass's budget as `cli.fact_call_authorities` builds one."""
    from llm_harness.budgets import ScanBudget

    return ScanBudget(
        scan_id=scan_id, corpus_file_count=files,
        max_calls_per_1000_files=cli.FACT_CALLS_PER_1000_FILES,
        max_estimated_cost=cli.FACT_CALLS_PER_SCAN_CEILING,
        min_calls_per_scan=cli.FACT_MIN_CALLS_PER_SCAN)


def test_a_run_that_spends_every_fact_call_can_still_place_what_it_learned(
        tmp_path):
    """The defect, as the arithmetic that produced it.

    Site A asks one call per FILE, so a corpus where every file has an open
    question spends every slot the run has -- and B, C and D drew from that same
    `ScanBudget`. Measured on the six-file corpus of `tests/integration/
    test_local_model_fact_pass.py`: five fact calls, then site B refused before a
    call and site C recording `BUDGET_EXHAUSTED`, so the sites that decide WHERE
    a file goes were starved by the site that decides WHAT it is.

    Exhausting the fact ledger here and then reserving from the observe one is
    that whole story in two reservations.
    """
    import sqlite3

    from llm_harness.budgets import (
        BudgetExhausted, allowed_calls, create_budget_schema, reserve_call,
    )

    conn = sqlite3.connect(tmp_path / "budgets.sqlite")
    conn.row_factory = sqlite3.Row
    create_budget_schema(conn)
    facts = _fact_budget()
    observe = cli.observe_scan_budget(facts)

    for _ in range(allowed_calls(facts)):
        reserve_call(conn, facts, estimated_cost=cli.FACT_CALL_COST)
    with pytest.raises(BudgetExhausted):
        reserve_call(conn, facts, estimated_cost=cli.FACT_CALL_COST)

    # The placement question the run could not put before this ruling.
    reserved = reserve_call(conn, observe, estimated_cost=cli.FACT_CALL_COST)
    assert reserved.scan_id == observe.scan_id


def test_the_two_ledgers_are_two_rows_and_not_one(tmp_path):
    """One `scan_id` was one purse. `llm_scan_budget` is keyed on that column and
    `llm_budget_reservation` is indexed on it, so two ids are two ledgers -- and
    the observe id is DERIVED from the fact one, so a reader can still see which
    run a row belongs to."""
    import sqlite3

    from llm_harness.budgets import create_budget_schema, reserve_call

    conn = sqlite3.connect(tmp_path / "budgets.sqlite")
    conn.row_factory = sqlite3.Row
    create_budget_schema(conn)
    facts = _fact_budget()
    observe = cli.observe_scan_budget(facts)

    reserve_call(conn, facts, estimated_cost=cli.FACT_CALL_COST)
    reserve_call(conn, observe, estimated_cost=cli.FACT_CALL_COST)

    rows = {row["scan_id"]: row["calls_reserved"]
            for row in conn.execute("SELECT * FROM llm_scan_budget")}
    assert rows == {facts.scan_id: 1, observe.scan_id: 1}
    assert observe.scan_id.startswith(facts.scan_id)


def test_the_observe_ledger_is_the_runs_own_and_the_rest_is_still_site_as(
        tmp_path):
    """What the second budget changes and what it deliberately does not.

    The scan and its file count are facts about the RUN, so they are carried; the
    rate, the floor and the ceiling are the purse, so they are the observe
    deployment's own. Everything else an observe site uses -- the gate, the costs,
    the policy version, the wire handle key -- is still taken from site A's
    authorities, because a second gate would be a second answer to what may leave
    this device.
    """
    facts = _fact_budget(files=199)
    observe = cli.observe_scan_budget(facts)

    assert observe.corpus_file_count == facts.corpus_file_count
    assert observe.scan_id != facts.scan_id
    assert observe.max_calls_per_1000_files == cli.OBSERVE_CALLS_PER_1000_FILES
    assert observe.min_calls_per_scan == cli.OBSERVE_MIN_CALLS_PER_SCAN
    assert observe.max_estimated_cost == cli.OBSERVE_CALLS_PER_SCAN_CEILING

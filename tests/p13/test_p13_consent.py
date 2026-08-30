"""§8.4 + B2: four options, always, and a pending request is never an abstention.

`74` §6 B7's named test is
`test_needs_consent_presents_all_four_options_and_never_maps_to_abstain` and its
negative twin is `test_a_surface_offering_three_options_is_refused`. The twin is
run once per option so that a guard which only noticed a missing `cloud_model`
would still fail -- the option most likely to be quietly dropped is
`no_model_use`, and it is the most consequential one.

SPEC Open question 5 is OPEN -- what outcome a user-chosen "no model use"
produces -- and nothing here answers it. The option is presented and collected
exactly like the other three, and P13 maps it to no outcome at all.
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from placement.vocabulary import BLOCKED_PENDING_USER
from privacy.consent import (
    CONSENT_OPTIONS,
    ConsentRequirement,
    IncompleteConsentOptions,
    NeedsConsent,
)
from privacy.display import RedactionSettings

from review_surface.consent_surface import (
    AWAITING_USER,
    FOUR_OPTIONS,
    ConsentIsNotAnAbstention,
    ConsentOptionsIncomplete,
    as_abstention,
    collect_consent_choice,
    consent_item,
)
from review_surface.presentation import record_presentation
from review_surface.vocabulary import (
    ACTION_SELECT_CONSENT_OPTION,
    SURFACE_CONSENT,
    OutOfVocabulary,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")

REQUIREMENT = ConsentRequirement(
    file_ids=("f-1",), handling_class="sensitive_personal",
    items=("excerpt: page 2 lines 4-9",),
    why="the residual recommendation needs the letter's body text")


def _needs(options=CONSENT_OPTIONS) -> NeedsConsent:
    return NeedsConsent(consent_request_id="cr-1", requirement=REQUIREMENT,
                        options=tuple(options))


@dataclasses.dataclass(frozen=True)
class _ShortRequest:
    """A consent request carrying fewer than four options.

    P7's own `NeedsConsent` refuses one at construction, so a short request
    cannot come from P7 -- which is the right place for that rule and is asserted
    below. This stand-in exists so P13's OWN refusal can be shown to fire: P13
    must not accept a short list from anywhere, and a guard that can only be
    reached through a constructor that already refuses is a guard nothing ever
    tests.
    """

    consent_request_id: str
    requirement: object
    options: tuple[str, ...]


@pytest.fixture()
def ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_CONSENT, subject_ref="cr-1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def test_needs_consent_presents_all_four_options_and_never_maps_to_abstain(
        p13_conn, ref):
    """`74` §6 B7's named test, and Done-means 16 including its negative half.

    Four options with four distinct sentences; the requirement states which items
    and why; the state is awaiting the user at `blocked_pending_user`, which is a
    live member of P11's `REVIEW_POLICIES`; and the one function that would map
    it to an abstention exists only to refuse, because the rendering is the last
    place B2's forbidden mapping could reappear.
    """
    assert FOUR_OPTIONS == CONSENT_OPTIONS
    assert FOUR_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                            "no_model_use")
    item = consent_item(_needs())
    assert item.options == FOUR_OPTIONS
    assert len({item.option_sentences[o] for o in FOUR_OPTIONS}) == 4
    assert item.requirement.items == ("excerpt: page 2 lines 4-9",)
    assert "body text" in item.requirement.why
    assert item.requirement.handling_class == "sensitive_personal"
    assert item.render_state == AWAITING_USER
    assert item.review_policy == BLOCKED_PENDING_USER
    with pytest.raises(ConsentIsNotAnAbstention) as caught:
        as_abstention(item)
    assert "B2" in str(caught.value)


def test_a_surface_offering_three_options_is_refused(p13_conn):
    """`74` §6 B7's negative twin, once per dropped option.

    SPEC:391-393: a surface that offers fewer has silently made the user's
    decision for them. Dropping any one of the four is refused, and the refusal
    names the missing option -- including `no_model_use`, which a surface trying
    to be helpful is the most likely to leave out and which is the option that
    matters most.
    """
    for dropped in FOUR_OPTIONS:
        three = tuple(o for o in FOUR_OPTIONS if o != dropped)
        with pytest.raises(ConsentOptionsIncomplete) as caught:
            consent_item(_ShortRequest("cr-1", REQUIREMENT, three))
        assert dropped in str(caught.value)
        # And P7 refuses the same list at its own boundary, so the rule holds on
        # both sides of the seam rather than only where it is easiest to test.
        with pytest.raises(IncompleteConsentOptions):
            NeedsConsent(consent_request_id="cr-1", requirement=REQUIREMENT,
                         options=three)
    with pytest.raises(ConsentOptionsIncomplete):
        consent_item(_ShortRequest("cr-1", REQUIREMENT, ()))


def test_choosing_an_option_is_collected_and_routed_to_p7(p13_conn, ref):
    """SPEC:397-398: P13 records the collection, not the grant."""
    action = collect_consent_choice(
        p13_conn, consent_item(_needs()), "redacted_prompt",
        action_id="a-consent", subject_ref="cr-1", plan_version="plan-1",
        session_id="s-1", correction_scope="file", presented_state_ref=ref,
        user_id="jy", acted_at=T0, component_version="p13-1")
    assert action.action == ACTION_SELECT_CONSENT_OPTION
    assert action.routed_to == ("P7",)
    assert action.payload["consent_option"] == "redacted_prompt"


def test_the_scope_is_presented_here_too_and_has_no_default(p13_conn, ref):
    """§8.7's rule holds on every surface, consent included.

    Departure from the P13 PLAN, which hard-coded `file` scope inside the consent
    collector. A scope P13 supplies is an inference wearing a keyword's clothes,
    and `collect`'s whole refusal is that no path exists by which one gets
    supplied. So the consent collector takes it too, with no default.
    """
    signature = inspect.signature(collect_consent_choice)
    scope = signature.parameters["correction_scope"]
    assert scope.default is inspect.Parameter.empty
    assert scope.kind is inspect.Parameter.KEYWORD_ONLY


def test_no_model_use_is_presented_and_collected_like_the_other_three(
        p13_conn, ref):
    """SPEC Open question 5 is OPEN. P13 maps it to no outcome at all."""
    action = collect_consent_choice(
        p13_conn, consent_item(_needs()), "no_model_use",
        action_id="a-none", subject_ref="cr-1", plan_version="plan-1",
        session_id="s-1", correction_scope="file", presented_state_ref=ref,
        user_id="jy", acted_at=T0, component_version="p13-1")
    assert action.payload["consent_option"] == "no_model_use"
    assert "outcome" not in action.payload
    assert action.routed_to == ("P7",)


def test_an_option_outside_the_four_is_refused(p13_conn, ref):
    with pytest.raises(OutOfVocabulary):
        collect_consent_choice(
            p13_conn, consent_item(_needs()), "just_do_it",
            action_id="a-x", subject_ref="cr-1", plan_version="plan-1",
            session_id="s-1", correction_scope="file",
            presented_state_ref=ref, user_id="jy", acted_at=T0,
            component_version="p13-1")

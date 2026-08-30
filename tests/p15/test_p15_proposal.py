# tests/p15/test_p15_proposal.py
"""§16's proposal step, and the four things `80` §7 now forbids.

`80` is the owner's ruling of 2026-08-31. It closes Options 3 and 4, opens Option 2 --
a LOCAL model proposes a shortlist and the person confirms -- and lists four things
that must now be impossible. Three of the four are pinned here and the fourth (R2, no
per-file re-confirmation) is in `test_p15_role_trigger.py`, beside the trigger it is
about:

  1. No path sends a self-description off-device.
  2. No model output activates anything.
  4. No presentation reintroduces ranking the data does not carry.

Every guard below has a twin that was proven by actually sabotaging the
implementation and watching it go red, not by reading it.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
import sqlite3

import pytest

from facts.domains import SCHEMA_IDS
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.items import AlwaysLocalRequested, MetadataField
from privacy.vocabulary import (
    ALWAYS_LOCAL, MODE_SEMANTICS, OPERATION_MODES, OutOfVocabulary,
)
from questions.proposal import (
    ProposalRefused, REASONING_TIER, REVOCATION_SENTENCE, RoleProposal,
    SELF_DESCRIPTION_ITEM, SelfDescriptionSending, propose_roles, sending_notice,
    shortlist_for_question,
)
from questions.roles import declare_role
from questions.schema import create_questions_schema
from questions.store import activated_schemas, gated_template

T0 = "2026-08-31T10:00:00+00:00"

#: `68` F6's person, in one sentence with three things in it. `80` §4 (R4): "If the
#: person mentions three things and the shortlist only reflects one, that's the moment
#: trust breaks, even if the one it picked is technically correct."
SENTENCE = ("I'm a graduate student in physics, I teach one undergraduate lab "
            "section, and I do the books for my mum's shop")

#: A stand-in for the local model this deployment does not have. It is a plain
#: callable because that is the whole of the seam: sentence in, members of the closed
#: list out. No test here asserts anything about how a real one would choose.
def _proposes(*candidates):
    return lambda sentence, offered: candidates


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


# --- 1. no path sends a self-description off-device ---------------------------------


def test_a_self_description_is_one_of_84s_always_local_items():
    """`80` §2, and the whole of requirement 1's first half.

    The ruling is recorded at the member in `privacy.vocabulary.ALWAYS_LOCAL`; this
    package names the same string rather than a second one, so a self-description is
    refused wherever §8.4's other eight are refused and by the same code.
    """
    assert SELF_DESCRIPTION_ITEM in ALWAYS_LOCAL


def test_no_transport_can_name_a_self_description():
    """The test `80` §7 asks for by name: "a test must fail if a transport can name
    it".

    `MetadataField` is, in P7's own words, "the single field in the product through
    which one of §8.4's nine could be NAMED", so this is the naming, at the one place
    naming happens. It is not constructible, which is stronger than denied: there is
    no request to consent around.
    """
    with pytest.raises(AlwaysLocalRequested, match="always-local"):
        MetadataField(name=SELF_DESCRIPTION_ITEM)


def test_a_mode_in_which_content_may_leave_the_device_may_not_run_this_step():
    """Requirement 1's second half, at this package's own seam.

    `80` §2: consent does not unlock it -- "Consent is the wrong tool for content
    whose sensitivity the person can't preview or bound in advance." So a
    `hybrid` or `cloud_assisted` deployment does not get a redacted proposal or a
    prompt; it gets no proposal.
    """
    for mode in OPERATION_MODES:
        if mode in LOCAL_FIRST_MODES:
            continue
        with pytest.raises(ProposalRefused, match="leave the device"):
            propose_roles(SENTENCE, offered=SCHEMA_IDS,
                          propose=_proposes("academic"), mode=mode)
    # ...and this is the whole of it: the refusal is the NO-OPT-IN path, unchanged
    # by `80` §8, which adds a second door rather than widening this one.


def test_the_two_local_modes_may_run_it():
    """The positive twin. A guard that refused every mode would pass the test above
    and ship a feature that never runs, which is the failure `records.py:46` names:
    a consequence nothing reads."""
    for mode in LOCAL_FIRST_MODES:
        proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                                 propose=_proposes("academic"), mode=mode)
        assert proposal.candidates == frozenset({"academic"})


def test_a_mode_outside_84s_four_is_refused_by_p7_and_not_by_this_module():
    """Imported, never respelled. The refusal is `check_mode`'s, so a P7 revision
    reaches this step by import rather than by memory."""
    with pytest.raises(OutOfVocabulary):
        propose_roles(SENTENCE, offered=SCHEMA_IDS, propose=None,
                      mode="local_model_but_slightly_cloudy")


def test_the_model_is_handed_the_sentence_and_the_closed_list_and_nothing_else():
    """`80` §1.3: "The model reads the whole sentence; it may propose only from the
    closed list." Both halves, observed at the call rather than asserted about it.

    The sentence arrives WHOLE -- unsplit, unnormalised, un-keyworded -- which is
    `62` §D's objection ("These should not just be directly matched") satisfied by
    there being no matching here to do.
    """
    seen = []

    def spy(sentence, offered):
        seen.append((sentence, offered))
        return ("academic",)

    propose_roles(SENTENCE, offered=SCHEMA_IDS, propose=spy, mode="local_model")

    assert seen == [(SENTENCE, frozenset(SCHEMA_IDS))]


# --- 2. no model output activates anything ------------------------------------------


def test_a_proposal_activates_nothing_and_only_the_persons_choice_does(qconn):
    """`80` §7's second forbidden thing, end to end.

    The model proposes two candidates. Nothing is on. The person confirms ONE of
    them through `declare_role` -- D3's single activation surface -- and that one is
    on. The other, which the model proposed just as strongly, never becomes anything.
    """
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                             propose=_proposes("academic", "research"),
                             mode="local_model")
    assert activated_schemas(qconn) == frozenset()

    declare_role(qconn, declaration_id="studying", scope="corpus",
                 schemas=shortlist_for_question(proposal, order=sorted),
                 chosen_schema="academic", user_id="jy", recorded_at=T0)

    assert activated_schemas(qconn) == frozenset({"academic"})
    assert gated_template(qconn, scope="corpus") is None


def test_the_proposal_step_cannot_reach_the_activation_surface():
    """The hard invariant `80` §7 asks for, as a property of the import graph.

    "Activation requires the person's confirmation, as a hard invariant rather than
    a default." A default is a line somebody can change; this is a module with no
    connection, no store and no writer in it, so there is no line to change without
    the change being visible in the imports.

    Checked over the parsed AST so a docstring cannot pass for an implementation, nor
    a mention fail for one -- the same treatment `test_p15_roles.py` gives §16:557.
    """
    tree = ast.parse(pathlib.Path("src/questions/proposal.py").read_text())

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    assert "sqlite3" not in modules
    assert not any(module.startswith("questions.") for module in modules), (
        f"the proposal step imports {sorted(m for m in modules if m.startswith('questions.'))}; "
        "it must be able to reach nothing that writes")

    named = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            named.add(node.id)
        elif isinstance(node, ast.Attribute):
            named.add(node.attr)
        elif isinstance(node, ast.keyword) and node.arg:
            named.add(node.arg)
    forbidden = {"declare_role", "skip_role", "record_answer", "record_question",
                 "activated_schemas", "gated_template", "selected_situation",
                 "activates_schema", "execute", "commit"}
    assert named & forbidden == set(), (
        f"the proposal step names {sorted(named & forbidden)}")


def test_the_activation_guard_fires_on_a_proposal_that_activated_something():
    """The sabotage fixture. A guard that cannot fire is not a guard."""
    sabotage = ("from questions.roles import declare_role\n"
                "def propose(conn, sentence):\n"
                "    return declare_role(conn, chosen_schema=sentence)\n")
    tree = ast.parse(sabotage)
    modules = {node.module for node in ast.walk(tree)
               if isinstance(node, ast.ImportFrom) and node.module}
    named = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    named |= {node.arg for node in ast.walk(tree)
              if isinstance(node, ast.keyword) and node.arg}
    assert any(module.startswith("questions.") for module in modules)
    assert named & {"declare_role", "chosen_schema"}


# --- the closed list, and what happens outside it -----------------------------------


def test_a_candidate_the_caller_did_not_offer_refuses_the_whole_proposal():
    """§16:547: "'I'm a sound engineer' must not silently activate an engineering or
    software-project schema merely because the words are superficially similar."

    The whole proposal is refused, not narrowed to the part that fits. A shortlist
    quietly one item shorter is the same wrong answer with the evidence removed.
    """
    with pytest.raises(ProposalRefused, match="sound_engineering"):
        propose_roles(SENTENCE, offered=SCHEMA_IDS,
                      propose=_proposes("academic", "sound_engineering"),
                      mode="local_model")


def test_nothing_matched_is_a_normal_outcome_and_not_an_error():
    """`80` §4 (R5): "'none of these' is a normal outcome, not an error." A model
    that matched nothing returns an empty shortlist and the step succeeds.

    The WORDING the person then sees is `80` §6's, reserved to the owner -- "No agent
    may author or approve it" -- so this asserts the structural fact and no string.
    """
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS, propose=_proposes(),
                             mode="local_model")

    assert proposal.nothing_matched is True
    assert proposal.candidates == frozenset()
    assert proposal.self_description == SENTENCE


def test_an_absent_model_is_option_1_and_not_a_refusal():
    """`80` §1: "Option 1 as the fallback whenever no local model is present."

    Absent refuses or falls back and never guesses. Here a good fallback exists --
    the person picks from the whole closed list, which is what they would have done
    anyway -- so absent falls back, and `from_model` records that it did.
    """
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS, propose=None,
                             mode="offline")

    assert proposal.candidates == frozenset(SCHEMA_IDS)
    assert proposal.from_model is False
    assert proposal.nothing_matched is False


def test_an_absent_candidate_list_refuses_rather_than_resolving_to_empty():
    """The other half of absent-means-refuse. An empty offered list would make
    `nothing_matched` true for every sentence anybody typed, which reads to the
    person as "we have no category for you" and is in fact a missing argument."""
    with pytest.raises(ProposalRefused, match="refuse"):
        propose_roles(SENTENCE, offered=(), propose=None, mode="offline")


def test_a_proposal_with_no_sentence_behind_it_is_refused():
    with pytest.raises(ProposalRefused, match="nothing to read"):
        propose_roles("", offered=SCHEMA_IDS, propose=_proposes("academic"),
                      mode="local_model")


# --- 4. no presentation that reintroduces ranking the data does not carry -----------


def test_the_shortlist_does_not_carry_the_order_the_model_returned():
    """`80` §5 (R7), and the sharpest form of it.

    The same three candidates, returned by two models in opposite orders. The
    proposals are equal and so is anything rendered from them. There is no path by
    which a model's ordering reaches a person, because the ordering is discarded at
    the boundary rather than ignored downstream.
    """
    forward = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                            propose=_proposes("academic", "research", "finance"),
                            mode="local_model")
    backward = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                             propose=_proposes("finance", "research", "academic"),
                             mode="local_model")

    assert forward.candidates == backward.candidates
    assert (shortlist_for_question(forward, order=sorted)
            == shortlist_for_question(backward, order=sorted))


def test_a_proposal_that_carries_an_order_is_refused():
    """The negative twin, on the RECORD rather than on a call.

    R7's own words: the mitigation "must be stronger than 'do not sort by
    confidence'". A convention is a thing to remember; a type that refuses a sequence
    is a thing that cannot be forgotten.
    """
    with pytest.raises(ProposalRefused, match="order"):
        RoleProposal(self_description=SENTENCE,
                     candidates=("academic", "research"), from_model=True)

    RoleProposal(self_description=SENTENCE,
                 candidates=frozenset({"academic", "research"}), from_model=True)


def test_a_shortlist_with_no_order_supplied_is_refused():
    """Injected with no default, because every default available here is wrong:
    alphabetical ranks by an irrelevance, insertion order is the model's, and set
    iteration is an order nobody chose and the only one that looks deliberate."""
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                             propose=_proposes("academic", "research"),
                             mode="local_model")

    with pytest.raises(ProposalRefused, match="does not carry"):
        shortlist_for_question(proposal, order=None)


def test_a_presentation_may_not_add_or_drop_a_candidate():
    """A renderer that could add one would be a second proposal step in the layer
    that is supposed to render the first one -- and it would be the layer with no
    closed list in front of it."""
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                             propose=_proposes("academic", "research"),
                             mode="local_model")

    with pytest.raises(ProposalRefused, match="second proposal step"):
        shortlist_for_question(proposal, order=lambda given: sorted(given) + ["medical"])
    with pytest.raises(ProposalRefused, match="second proposal step"):
        shortlist_for_question(proposal, order=lambda given: sorted(given)[:1])
    with pytest.raises(ProposalRefused, match="second proposal step"):
        shortlist_for_question(proposal, order=lambda given: sorted(given) * 2)


def test_an_order_that_only_arranges_is_accepted():
    """The positive twin: refusing every order would leave the shortlist
    unrenderable, which satisfies R7 by deleting the feature."""
    proposal = propose_roles(SENTENCE, offered=SCHEMA_IDS,
                             propose=_proposes("academic", "research", "finance"),
                             mode="local_model")

    shown = shortlist_for_question(proposal, order=lambda given: sorted(given,
                                                                       reverse=True))
    assert shown == ("research", "finance", "academic")


# ======================================================================================
# `80` §8 -- the amendment, and the three conditions that scope it
# ======================================================================================
#
# Joseph overruled §2's ENFORCEMENT for development on the day it was recorded. The
# classification is not withdrawn: a self-description is still a `user_edits` item,
# and the other eight always-local kinds are untouched. `80` §8.2 states the cost in
# terms that cannot be undone -- "There is no temporary about a sent sentence" -- so
# every fixture below is an INVENTED sentence. Nothing here is lifted from a corpus,
# and `68`'s Mara corpus in particular contains a client's passport.

#: A cloud deployment. `check_mode` is P7's and these are two of its four.
SENDING_MODE = "cloud_assisted"

INVENTED = ("I look after my father's paperwork, I'm halfway through a part-time "
            "diploma, and I do the accounts for a five-a-side league")


def _sending(*, announce, tier=REASONING_TIER, model_id="a-named-model"):
    return SelfDescriptionSending(model_tier=tier, model_id=model_id,
                                  announce=announce)


# --- C1: local is what happens by not choosing --------------------------------------


def test_the_amendment_is_off_unless_a_caller_asks_for_it():
    """C1, on the signature rather than on a call.

    "A developer who forgets this exception exists gets the safe behaviour." The
    only way that is true is if not-passing-anything is the safe path, so `sending`
    is the one default in this module and it defaults to nothing.
    """
    parameter = inspect.signature(propose_roles).parameters["sending"]
    assert parameter.default is None


def test_without_the_opt_in_a_cloud_mode_still_refuses():
    """C1's behavioural half. The pre-amendment refusal is not softened; it is left
    exactly where it was and a second, explicit door is added beside it."""
    with pytest.raises(ProposalRefused, match="local is what happens by not choosing"):
        propose_roles(INVENTED, offered=SCHEMA_IDS, propose=_proposes("academic"),
                      mode=SENDING_MODE)


def test_nothing_in_this_module_can_turn_sending_on_by_itself():
    """C1: "there is no environment variable or config default that quietly turns it
    on". Checked over the parsed AST, because the failure this prevents is a
    convenience somebody adds later and nobody reviews."""
    tree = ast.parse(pathlib.Path("src/questions/proposal.py").read_text())

    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    assert modules & {"os", "os.path", "pathlib", "configparser", "json",
                      "tomllib", "dotenv"} == set()

    named = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            named.add(node.id)
        elif isinstance(node, ast.Attribute):
            named.add(node.attr)
    assert named & {"environ", "getenv", "getenvb", "open", "read_text"} == set()


# --- C2: a run that sends says so, on screen, before it sends -----------------------


def test_the_person_is_told_before_the_sentence_goes():
    """C2, and the ORDER is the whole requirement.

    A notice after the send is a receipt, not a warning, and `00`:200's point is
    precisely that afterwards is too late. The order is a property of
    `propose_roles` rather than of a caller's discipline, so it is observed on one
    timeline covering both events.
    """
    happened = []
    proposal = propose_roles(
        INVENTED, offered=SCHEMA_IDS,
        propose=lambda sentence, offered: happened.append("sent") or ("academic",),
        mode=SENDING_MODE,
        sending=_sending(announce=lambda line: happened.append(("told", line))))

    assert [event[0] if isinstance(event, tuple) else event
            for event in happened] == ["told", "sent"]
    assert proposal.from_model is True


def test_the_notice_says_what_is_going_where_and_that_it_cannot_come_back():
    """C2's three content requirements. `00`:200 is quoted rather than paraphrased,
    because the notice must be "in the same breath" as it and a paraphrase of a
    sentence about irreversibility is how the irreversibility gets softened."""
    notice = sending_notice(_sending(announce=print, model_id="DeepSeek-V4-Pro"),
                            mode=SENDING_MODE)

    assert "DeepSeek-V4-Pro" in notice
    assert REVOCATION_SENTENCE in notice
    assert REVOCATION_SENTENCE == (
        "Revocation cannot necessarily retract data already sent to an external "
        "provider.")


def test_a_record_that_cannot_tell_the_person_cannot_be_built():
    """C2 at construction, which is earlier than the send and cannot be skipped by a
    branch. `80` §8.3 rules out the two easy substitutes by name: "Not in a log, not
    in a docstring: on the screen."""
    with pytest.raises(ProposalRefused, match="no way to tell the person"):
        SelfDescriptionSending(model_tier=REASONING_TIER, model_id="a-named-model",
                               announce=None)


def test_a_notice_that_fails_stops_the_send():
    """The failure direction that matters. If the product cannot tell the person, it
    does not send and then apologise -- it does not send."""
    sent = []

    def refuses(line):
        raise RuntimeError("no screen")

    with pytest.raises(RuntimeError):
        propose_roles(INVENTED, offered=SCHEMA_IDS,
                      propose=lambda sentence, offered: sent.append(sentence) or (),
                      mode=SENDING_MODE, sending=_sending(announce=refuses))

    assert sent == []


def test_the_notice_is_never_shown_to_the_model():
    """The notice is on-screen copy, not prompt text -- `80` §6 and §8.4 reserve
    prompt bytes to the owner. The model is handed the sentence and the closed list,
    exactly as it is on the local path, and nothing else."""
    seen = []
    propose_roles(INVENTED, offered=SCHEMA_IDS,
                  propose=lambda sentence, offered: seen.append(
                      (sentence, offered)) or ("academic",),
                  mode=SENDING_MODE, sending=_sending(announce=lambda line: None))

    assert seen == [(INVENTED, frozenset(SCHEMA_IDS))]


def test_a_run_that_asked_to_send_and_has_no_model_refuses():
    """Falling back to the local list here would reach the safer OUTCOME by the worse
    ROUTE: the person asked where their words were going and would be told nothing.
    Absent means refuse."""
    with pytest.raises(ProposalRefused, match="Absent means refuse"):
        propose_roles(INVENTED, offered=SCHEMA_IDS, propose=None, mode=SENDING_MODE,
                      sending=_sending(announce=lambda line: None))


def test_the_opt_in_does_not_make_a_developer_loosen_every_other_call_site():
    """The scope `80` §8.1 sets: "this suspension reaches nothing but the
    self-description".

    So the opt-in does not require `cloud_assisted`. If it did, a developer wanting
    the one scoped exception would have to change the deployment's operation mode,
    which loosens what may be sent for EVERY other call site -- `83` §4 forbids that
    trade from the routing side, and it is the opposite of a scoped suspension. The
    mode is left exactly as the deployment set it and nothing else gains permission.
    """
    for mode in LOCAL_FIRST_MODES:
        proposal = propose_roles(INVENTED, offered=SCHEMA_IDS,
                                 propose=_proposes("academic"), mode=mode,
                                 sending=_sending(announce=lambda line: None))
        assert proposal.candidates == frozenset({"academic"})


def test_under_a_local_mode_the_person_is_told_their_mode_is_being_excepted():
    """The other half, and the reason the test above is not a hole.

    `offline` promises "No content leaves the device". The amendment makes that
    untrue for one item. A person who chose that mode and is not told would keep
    reading it as meaning what it says, so the notice quotes P7's own promise and
    names the exception in the same breath -- and says nothing else is sent.
    """
    told = []
    propose_roles(INVENTED, offered=SCHEMA_IDS, propose=_proposes("academic"),
                  mode="offline", sending=_sending(announce=told.append))

    notice, = told
    assert "offline" in notice
    assert MODE_SEMANTICS["offline"] in notice
    assert "Nothing else about your files is sent." in notice
    assert REVOCATION_SENTENCE in notice


def test_a_cloud_mode_notice_claims_no_exception_it_is_not_making():
    """The negative twin. Under `cloud_assisted` the mode already permits a cloud
    model, so there is no exception to announce, and announcing one would be the
    overstatement that teaches a person to stop reading these."""
    told = []
    propose_roles(INVENTED, offered=SCHEMA_IDS, propose=_proposes("academic"),
                  mode=SENDING_MODE, sending=_sending(announce=told.append))

    notice, = told
    assert "one exception" not in notice
    assert REVOCATION_SENTENCE in notice


# --- `83`: the tier this site was routed to, and no cheaper one ---------------------


def test_a_cheaper_tier_is_refused_rather_than_answered():
    """`83` §4: "No silent downgrade." R4 -- the shortlist must read as having heard
    the WHOLE sentence -- is the judgement being bought, and it is exactly what a
    cheap model flattens to one keyword. A wrong answer from the wrong tier looks
    identical to a right one, which is why this refuses instead of preferring."""
    for cheaper in ("logic", "fast", "", "Reasoning"):
        with pytest.raises(ProposalRefused, match="tier"):
            SelfDescriptionSending(model_tier=cheaper, model_id="a-named-model",
                                   announce=print)


def test_the_sending_record_names_the_model_that_receives_it():
    """`00`:200's distinction is about a NAMED external provider. A person told only
    that their words went "to the cloud" has been told less than nothing they can
    act on."""
    with pytest.raises(ProposalRefused, match="names no model"):
        SelfDescriptionSending(model_tier=REASONING_TIER, model_id="",
                               announce=print)


# --- what the amendment did NOT change ----------------------------------------------


def test_the_classification_still_stands():
    """`80` §8.1: the ruling that a self-description is a `user_edits` item "is not
    withdrawn -- the classification stands, and the enforcement is suspended". So the
    member is still where it was and a transport still cannot name it."""
    assert SELF_DESCRIPTION_ITEM in ALWAYS_LOCAL
    with pytest.raises(AlwaysLocalRequested):
        MetadataField(name=SELF_DESCRIPTION_ITEM)


def test_the_amendment_reaches_nothing_but_the_self_description():
    """`80` §8.1: "The other eight always-local kinds are untouched." Nothing in this
    package can name one, and the opt-in does not widen what may be sent -- `83` §4
    says the same thing from the routing side: "No tier changes what may be SENT."
    """
    for item in ALWAYS_LOCAL:
        with pytest.raises(AlwaysLocalRequested):
            MetadataField(name=item)


def test_no_model_output_activates_anything_even_when_the_model_was_a_cloud_one(qconn):
    """The invariant that matters most, restated with the amendment on.

    A cloud provider does not weaken the ruling's argument for Option 2: the
    shortlist is still a proposal, the person still confirms, and nothing activates
    without them. What changed is only where the sentence goes.
    """
    proposal = propose_roles(INVENTED, offered=SCHEMA_IDS,
                             propose=_proposes("academic", "finance"),
                             mode=SENDING_MODE,
                             sending=_sending(announce=lambda line: None))
    assert activated_schemas(qconn) == frozenset()

    declare_role(qconn, declaration_id="diploma", scope="corpus",
                 schemas=shortlist_for_question(proposal, order=sorted),
                 chosen_schema="academic", user_id="jy", recorded_at=T0)

    assert activated_schemas(qconn) == frozenset({"academic"})


def test_the_shortlist_still_carries_no_order_when_it_came_from_the_cloud():
    """R7 is unchanged by the amendment -- `80` §8.4: "R1-R7 all still bind"."""
    forward = propose_roles(INVENTED, offered=SCHEMA_IDS,
                            propose=_proposes("academic", "finance", "legal"),
                            mode=SENDING_MODE,
                            sending=_sending(announce=lambda line: None))
    backward = propose_roles(INVENTED, offered=SCHEMA_IDS,
                             propose=_proposes("legal", "finance", "academic"),
                             mode=SENDING_MODE,
                             sending=_sending(announce=lambda line: None))

    assert forward.candidates == backward.candidates


# --- C3: designed for the revert ----------------------------------------------------


def test_the_local_path_needs_no_part_of_the_amendment():
    """C3: "when C3 fires, deleting the flag must leave a working product, not a
    hole".

    The local path is called with no `sending` argument at all, reaches no branch
    that mentions one, and is the same call it was before `80` §8. Deleting
    `SelfDescriptionSending`, `sending_notice` and the `sending` parameter leaves
    every local behaviour standing -- which is why the amendment is a parameter with
    a safe default rather than a mode the module is now in.
    """
    local = propose_roles(INVENTED, offered=SCHEMA_IDS,
                          propose=_proposes("academic", "finance"),
                          mode="local_model")
    assert local.candidates == frozenset({"academic", "finance"})
    assert local.from_model is True

    fallback = propose_roles(INVENTED, offered=SCHEMA_IDS, propose=None,
                             mode="offline")
    assert fallback.candidates == frozenset(SCHEMA_IDS)
    assert fallback.from_model is False


def test_the_amendment_added_exactly_one_parameter():
    """The surface a revert has to remove. One parameter, defaulting to the safe
    value, is the smallest shape this could take and the easiest to delete."""
    parameters = list(inspect.signature(propose_roles).parameters)
    assert parameters == ["self_description", "offered", "propose", "mode", "sending"]

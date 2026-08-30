# src/questions/proposal.py
"""§16's proposal step, on `80`'s terms: a LOCAL model proposes, the person confirms.

`80` is the owner's ruling of 2026-08-31. It lifts the gate `62` §D put on §16 and
replaces it with a shape, and the shape is what this module is:

> Option 2 -- a LOCAL model proposes a shortlist; the person confirms -- with Option
> 5 running underneath it continuously, and Option 1 as the fallback whenever no
> local model is present. (`80` §1)

> The model reads the whole sentence; it may propose only from the closed list; the
> person makes the decision. Nothing discards the sentence, and nothing lets an
> ungoverned judgement silently colour the rest of the system. (`80` §1.3)

Three sentences, and each is a refusal in the code below.

**The model reads the whole sentence.** `62` §D's objection was to discarding it --
"These should not just be directly matched" -- so the sentence goes in whole and is
kept whole. It is not tokenised, normalised, keyword-matched or shortened here:
this module holds no rule about words at all, and `propose` is injected.

**It may propose only from the closed list.** A candidate the caller did not offer
is refused rather than dropped, and the whole proposal is refused rather than
filtered. Filtering would be this module deciding which parts of a model's answer to
believe, which is a judgement nobody asked it to make; and a proposal quietly one
item shorter than the model gave is the "plausible wrong shortlist read as the
product's endorsement" risk (`78` §3.5) with the evidence removed.

**The person makes the decision.** NOTHING HERE WRITES. This module takes no
connection, imports no store, and names no activation: `roles.declare_role` is the
only path to `store.activated_schemas`, it takes the person's own choice, and
`80` §7's second forbidden thing -- "No model output activates anything" -- is
therefore a property of the import graph rather than a rule somebody has to keep.

**No local model is wired in this deployment**, and `propose=None` is not a defect.
It is Option 1: the person picks from the whole closed list, unnarrowed. Absent
refuses or falls back and never guesses, and here the fallback exists and is good,
so it falls back.

**A person's own sentence never leaves the device -- SUSPENDED, see below.** `80` §2
ruled it a `user_edits` item under `00`:186 -- always local, no exception, and consent
does not unlock it -- and the ruling is recorded at the member in
`privacy.vocabulary.ALWAYS_LOCAL`. Two consequences are enforced below: the item name
is imported rather than respelled, so a transport naming it is refused where §8.4's
other eight are refused; and a mode in which content may leave the device may not run
this step.

**`80` §8, the amendment of 2026-08-31.** Joseph overruled §2's ENFORCEMENT for
development, in his words: *"we are still building the product so right now its ok we
can just send it for now"*. The classification is NOT withdrawn -- a self-description
is still a `user_edits` item -- and the other eight always-local kinds are untouched
and unreachable from here. What is suspended is the enforcement, for this deployment,
for that one kind. `80` §8.2 states the cost and it is not recoverable: *"There is no
temporary about a sent sentence."*

Three conditions come with it, and two of them are this module's:

- **C1 -- local is still the DEFAULT.** `sending` is `None` unless a caller passes it,
  and `None` refuses every mode in which content may leave the device, exactly as
  before the amendment. This is the one default in this module, and it exists because
  C1 demands one: "a developer who forgets this exception exists gets the safe
  behaviour". There is no environment variable and no config here that can turn it on.
- **C2 -- a run that sends says so, on screen, before it sends.** `announce` is
  invoked with `sending_notice(...)` on the line before `propose` is called, so the
  order is a property of this function rather than of a caller's discipline. If
  `announce` raises, nothing is sent.
- **C3 -- it reverts before anyone who is not Joseph uses this.** The local path is
  untouched by all of the above: it takes no `sending` argument, reaches no branch
  that mentions one, and every test it had still passes. Deleting `SelfDescriptionSending`,
  `sending_notice` and the `sending` parameter leaves a working product rather than a
  hole. That is the shape C3 asks to be designed for, and it is checked by a test.

**Which model, and no other.** `83` §3 routes this call site to the REASONING tier,
because R4 requires the shortlist to read as having heard the WHOLE sentence, and
flattening a sentence to one keyword is the defect `62` §D objected to. `83` §4 forbids
a silent downgrade, so a sending record naming any other tier is refused here rather
than answered by a cheaper model.

**Order is not information this carries.** `80` §5 (R7): "Shortlist ORDER itself is
information the person will use whether or not you intend it to be ... position
seven versus position one still reads as ranked to a human." So the candidates are a
`frozenset` -- a sequence is refused by the record, not merely avoided by
convention -- and a caller that needs a sequence to render must inject the order it
renders in. Whether that injected order is random per render, or a layout with no
first item, belongs to the surface that renders it and is P13's to keep.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

# Imported, never respelled -- the rule `tree_design/vocabulary.py:13` states and
# `records.py` already follows for `HANDLING_CLASSES`. `LOCAL_FIRST_MODES` is P7's
# own `(offline, local_model)`, the two modes under which §8.4 promises no content
# leaves the device; a second spelling here is how two parts of one product come to
# disagree about whether a sentence was sent.
from privacy.defaults import LOCAL_FIRST_MODES
from privacy.vocabulary import ALWAYS_LOCAL, check_mode

#: Which of §8.4's nine always-local items a typed self-description IS. `80` §2:
#: "A person's typed description of themselves -- their roles, what they do -- is a
#: `user_edits` item", and the ruling is recorded at the member itself. Named here so
#: this package refers to the same string P7 refuses on, and checked at import so a
#: rename in P7 is an ImportError rather than a guard that silently stops guarding.
SELF_DESCRIPTION_ITEM: str = "user_edits"
if SELF_DESCRIPTION_ITEM not in ALWAYS_LOCAL:
    raise ImportError(
        f"{SELF_DESCRIPTION_ITEM!r} is not one of §8.4's always-local items "
        f"{ALWAYS_LOCAL}. `80` §2 rules a typed self-description to be one of them; "
        "if the member has been renamed, this constant must follow it rather than "
        "this package holding a second name for the same rule")


class ProposalRefused(ValueError):
    """A proposal step this design does not permit."""


#: What a local model is, as far as this module is concerned: it is handed the
#: person's whole sentence and the closed list, and it answers with members of that
#: list. It is given no connection, no file, no run and no corpus -- there is nothing
#: else for it to read, which is what makes "it may propose only from the closed
#: list" checkable rather than merely intended.
Proposer = Callable[[str, frozenset[str]], Iterable[str]]


#: `83` §3 routes this call site to the REASONING tier and gives the reason: R4
#: requires the shortlist to "read as having heard the WHOLE sentence", and that is
#: "exactly the judgement a cheap model flattens to one keyword, which is the failure
#: `62` §D objected to in the first place".
#:
#: The value is the tier's own word and not a model name: which model a tier resolves
#: to is a deployment choice that lives in `.env` and `src/cli.py`, and `83` opens by
#: saying so. THIS module names only which tier this site requires.
#:
#: A THIRD MEANING OF "tier" IN THIS REPO, and the two it is not. P6's resolver tiers
#: are `filesystem`, `native`, `ocr` -- how a fact was read. `llm_harness.vocabulary`'s
#: tier is a payload key on a Site-E proposal. This one is which model answers. The
#: repo already handles three such collisions by naming rather than by renaming
#: (`tree_design/vocabulary.py:4`); this is a fourth.
REASONING_TIER: str = "reasoning"


@dataclass(frozen=True, slots=True)
class SelfDescriptionSending:
    """`80` §8's suspension, made explicit at the one place it applies.

    A caller constructs this to say: *this run sends a person's own sentence about
    themselves to an external provider, and here is who is being told about it.* It
    exists as a RECORD rather than as a boolean because C1 and C2 are two halves of
    one act -- an opt-in that did not carry the way to tell the person would be an
    opt-in that could send silently, and a boolean is exactly that shape.

    It is never constructed inside this package. `propose_roles` takes it or does
    not, and takes `None` by default, which is C1: sending is what a person at the
    command line asks for, never what happens by not choosing.
    """

    #: `83` §4: "No tier is a default. A new call site names its tier or does not
    #: run." This site's tier is REASONING and a record naming any other is refused
    #: rather than answered, because "a cheap model answering a question the
    #: expensive one was chosen for is a wrong answer that looks like a right one".
    model_tier: str
    #: WHICH model, so the notice can name it. A person told that their sentence is
    #: going to "an external provider" has been told less than a person told it is
    #: going to a named one, and the audit `00`:200 is about is a record of a named
    #: recipient. This module does not choose it: the deployment does.
    model_id: str
    #: Where C2's words go. Injected with no default, because the only default
    #: available inside a part package is a logger, and `80` §8.3 rules a log out by
    #: name: "Not in a log, not in a docstring: on the screen."
    announce: Callable[[str], None]

    def __post_init__(self) -> None:
        if self.model_tier != REASONING_TIER:
            raise ProposalRefused(
                f"this call site is routed to the {REASONING_TIER!r} tier and the "
                f"sending record names {self.model_tier!r}. `83` §4 forbids the "
                "downgrade rather than discouraging it: a cheaper model answering "
                "the question the expensive one was chosen for is a wrong answer "
                "that looks like a right one, and R4 -- the shortlist must read as "
                "having heard the whole sentence -- is the judgement being bought")
        if not self.model_id:
            raise ProposalRefused(
                "a sending record names no model, so the person cannot be told who "
                "is receiving what they typed. `00`:200's distinction is about a "
                "named external provider and an unnamed one cannot be revoked from")
        if not callable(self.announce):
            raise ProposalRefused(
                "a sending record carries no way to tell the person. `80` §8.3 (C2): "
                "a run that sends says so, on screen, before it sends -- so a record "
                "that cannot say it is a record that must not send")


#: `00`:200, quoted. The clause and not a paraphrase, because it is the sentence the
#: whole condition is built around and `80` §8.3 requires the notice to be "in the
#: same breath" as it. The rest of `00`:200 -- "so the product must communicate that
#: distinction clearly" -- is an instruction to the product rather than words for a
#: person, and is the requirement this constant answers rather than part of it.
REVOCATION_SENTENCE: str = (
    "Revocation cannot necessarily retract data already sent to an external provider.")


def sending_notice(sending: SelfDescriptionSending) -> str:
    """The words C2 requires on screen, before a self-description is sent.

    NOT PROMPT TEXT. It is never given to a model, never fingerprinted, and reaches
    no audit record or cache key -- which is what `80` §6 and §8.4 reserve to the
    owner. It is on-screen copy, it is one named constant so there is one place to
    change it, and the owner may revise the wording without anything else moving.

    Three things, because C2 names three: what is about to happen, who receives it,
    and that it cannot be taken back. The third is `00`:200 verbatim.
    """
    return (
        f"What you typed about yourself is about to be sent to {sending.model_id}, "
        f"an external provider, so it can suggest which of this product's layouts "
        f"might fit. This is off by default and this run turned it on. "
        f"{REVOCATION_SENTENCE}")


@dataclass(frozen=True, slots=True)
class RoleProposal:
    """What a proposal step produced: a sentence, some candidates, and no decision."""

    #: The person's own words, whole. §16:555 requires them stored; `80` §2 requires
    #: them never sent. This field is the first half and `SELF_DESCRIPTION_ITEM` is
    #: the second.
    self_description: str
    #: Drawn only from the list the caller offered. A `frozenset` and not a sequence,
    #: because R7's mitigation "must be stronger than 'do not sort by confidence'":
    #: a type that cannot be indexed cannot hand a renderer a first item.
    candidates: frozenset[str]
    #: False when no local model was present and this is Option 1's fallback -- the
    #: whole closed list, unnarrowed, for the person to pick from. Recorded rather
    #: than inferred from the size of the set, because a model that happened to
    #: propose everything is a different fact about the run.
    from_model: bool

    def __post_init__(self) -> None:
        if not self.self_description:
            raise ProposalRefused(
                "a proposal with no sentence behind it is a guess. `80` §1.3: the "
                "model reads the whole sentence, and there is nothing to read")
        if not isinstance(self.candidates, frozenset):
            raise ProposalRefused(
                f"candidates is a {type(self.candidates).__name__}, which carries an "
                "order. `80` §5 (R7): shortlist order is information the person will "
                "use whether or not it is intended to be, and removing ranking from "
                "the data means the data cannot express one")
        if not isinstance(self.from_model, bool):
            raise ProposalRefused("`from_model` is a flag, not a value")

    @property
    def nothing_matched(self) -> bool:
        """`80` §4 (R5): "none of these" is a normal outcome, not an error.

        A structural fact and deliberately not a message. R5 is a CONTENT
        requirement -- same visual weight, same tone, no apology shape, the raw
        sentence still visible -- and `80` §6 reserves the wording to the owner:
        "No agent may author or approve it." So this says only that it happened.
        """
        return not self.candidates


def propose_roles(self_description: str, *, offered: Sequence[str],
                  propose: Proposer | None, mode: str,
                  sending: SelfDescriptionSending | None = None) -> RoleProposal:
    """One proposal, from one sentence, bounded by one closed list.

    `mode` and `propose` are required and neither has a default. `mode` is P7's
    operation mode for this deployment and it is checked twice: once against §8.4's
    closed four, and once against the two under which no content leaves the device.
    A `hybrid` or `cloud_assisted` deployment does not get a redacted version of this
    step or a consent prompt for it -- `80` §2 is explicit that consent is the wrong
    instrument here -- it gets `80` §8's opt-in or it gets nothing.

    **`sending` is the one default in this module and C1 is why.** Absent, this
    behaves exactly as it did before the amendment: no mode in which content may
    leave the device may run the step. Present, it is a deliberate act by whoever
    ran the command, and the person is told before anything goes. "A developer who
    forgets this exception exists gets the safe behaviour" is `80` §8.3's own
    sentence, and a default is the only construction that keeps it true.

    `propose=None` is Option 1 and not an error: every offered candidate comes back,
    unnarrowed, and `from_model` says so. The person then picks, which is what they
    would have done anyway; the model's only job was to make the list shorter. It IS
    an error together with `sending`, because a caller who asked for the sentence to
    be sent and got a silent local fallback has been misled about where their words
    went -- which is the one thing this whole condition exists to prevent.
    """
    # Before anything, and before any notice: an empty sentence has nothing to send,
    # and announcing a send that then refuses would tell a person their words had
    # gone when they had not.
    if not self_description:
        raise ProposalRefused(
            "a proposal with no sentence behind it is a guess. `80` §1.3: the model "
            "reads the whole sentence, and there is nothing to read")
    check_mode(mode)
    local = mode in LOCAL_FIRST_MODES
    if sending is None and not local:
        raise ProposalRefused(
            f"mode {mode!r} is one under which content may leave the device, and a "
            f"person's typed self-description may not: `80` §2 rules it a "
            f"{SELF_DESCRIPTION_ITEM!r} item under `00`:186, always local with no "
            f"exception, and consent does not unlock it. The modes that may run "
            f"this step are {LOCAL_FIRST_MODES}. `80` §8 suspends that enforcement "
            "for development, and only when the person running the command asks for "
            "it: local is what happens by not choosing")
    if sending is not None and local:
        raise ProposalRefused(
            f"mode {mode!r} sends nothing, and a sending record would have the "
            "product tell the person their words are leaving the device when they "
            "are not. `80` §8.3 (C2) requires a true notice, and a notice that "
            "overstates is worse than none: a person who learns it was untrue has "
            "no reason to believe the next one")
    closed = frozenset(offered)
    if not closed:
        raise ProposalRefused(
            "a proposal with no candidate list offered has nothing to propose FROM, "
            "and a model asked to answer from an empty list is being asked to "
            "invent. The closed vocabulary is the caller's to supply and absent "
            "must refuse rather than resolve to an empty list")
    if propose is None:
        if sending is not None:
            raise ProposalRefused(
                f"this run asked for the sentence to be sent to "
                f"{sending.model_id!r} and no model is configured to send it to. "
                "Falling back to the local list would be the safer OUTCOME reached "
                "by the worse ROUTE: the person asked where their words were going "
                "and would have been told nothing. Absent means refuse")
        return RoleProposal(self_description=self_description, candidates=closed,
                            from_model=False)
    if sending is not None:
        # `80` §8.3 (C2), and the ORDER is the requirement. On the line before the
        # send, so nothing between them can fail silently and leave a sentence gone
        # and a person untold. An `announce` that raises stops the send, which is
        # the right direction for this to fail in.
        sending.announce(sending_notice(sending))
    proposed = frozenset(propose(self_description, closed))
    invented = proposed - closed
    if invented:
        raise ProposalRefused(
            f"the proposal names {sorted(invented)}, which the caller did not offer. "
            "The whole proposal is refused rather than narrowed to the part that "
            "fits: dropping the rest would be this module choosing which of a "
            "model's answers to believe, and §16:547 -- 'an unmatched answer must "
            "remain unmatched' -- is not satisfied by a shortlist that quietly lost "
            "the item that showed it was wrong")
    return RoleProposal(self_description=self_description, candidates=proposed,
                        from_model=True)


def shortlist_for_question(proposal: RoleProposal, *,
                           order: Callable[[frozenset[str]], Iterable[str]],
                           ) -> tuple[str, ...]:
    """The candidates as a sequence, in an order the CALLER supplies.

    `roles.question_for_role_declaration` takes a sequence, and a sequence has a
    first item. R7's requirement is that the first item must not be information the
    data does not carry, so the order arrives from the surface that renders it and
    never from the model, and never from this module.

    Injected with no default, because every default available here is wrong. Sorted
    is alphabetical, which is a ranking by an irrelevance; insertion order is the
    model's, which is the ranking R7 exists to remove; and `frozenset` iteration is
    an order nobody chose, which is the worst of the three because it looks
    deliberate. Whether the caller's order randomises per render or renders a layout
    with no first item is the surface's to decide and P13's to keep.

    An order that adds or drops a candidate is refused. A renderer that could add one
    would be a second proposal step in the layer that is supposed to have none.
    """
    if order is None:
        raise ProposalRefused(
            "a shortlist with no order supplied would be rendered in whichever "
            "order this set happens to iterate, and `80` §5 (R7) forbids exactly "
            "that: a presentation must not encode an order the data does not carry")
    shown = tuple(order(proposal.candidates))
    if len(shown) != len(proposal.candidates) or frozenset(shown) != proposal.candidates:
        raise ProposalRefused(
            f"the order returned {sorted(shown)} for candidates "
            f"{sorted(proposal.candidates)}. An order arranges a shortlist; one that "
            "adds, drops or repeats a candidate is a second proposal step in the "
            "layer that renders the first one")
    return shown

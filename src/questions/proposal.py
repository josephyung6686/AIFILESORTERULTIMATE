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

**A person's own sentence never leaves the device.** `80` §2 ruled it a `user_edits`
item under `00`:186 -- always local, no exception, and consent does not unlock it --
and the ruling is recorded at the member in `privacy.vocabulary.ALWAYS_LOCAL`. Two
consequences are enforced below: the item name is imported rather than respelled, so
a transport naming it is refused where §8.4's other eight are refused; and a mode in
which content may leave the device may not run this step at all.

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
                  propose: Proposer | None, mode: str) -> RoleProposal:
    """One proposal, from one sentence, bounded by one closed list.

    `mode` and `propose` are required and neither has a default. `mode` is P7's
    operation mode for this deployment and it is checked twice: once against §8.4's
    closed four, and once against the two under which no content leaves the device.
    A `hybrid` or `cloud_assisted` deployment does not get a redacted version of this
    step or a consent prompt for it -- `80` §2 is explicit that consent is the wrong
    instrument here -- it does not get the step.

    `propose=None` is Option 1 and not an error: every offered candidate comes back,
    unnarrowed, and `from_model` says so. The person then picks, which is what they
    would have done anyway; the model's only job was to make the list shorter.
    """
    check_mode(mode)
    if mode not in LOCAL_FIRST_MODES:
        raise ProposalRefused(
            f"mode {mode!r} is one under which content may leave the device, and a "
            f"person's typed self-description may not: `80` §2 rules it a "
            f"{SELF_DESCRIPTION_ITEM!r} item under `00`:186, always local with no "
            f"exception, and consent does not unlock it. The modes that may run "
            f"this step are {LOCAL_FIRST_MODES}")
    closed = frozenset(offered)
    if not closed:
        raise ProposalRefused(
            "a proposal with no candidate list offered has nothing to propose FROM, "
            "and a model asked to answer from an empty list is being asked to "
            "invent. The closed vocabulary is the caller's to supply and absent "
            "must refuse rather than resolve to an empty list")
    if propose is None:
        return RoleProposal(self_description=self_description, candidates=closed,
                            from_model=False)
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

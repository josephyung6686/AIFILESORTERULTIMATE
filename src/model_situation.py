# src/model_situation.py
"""The seventh call site, built to the wall it stops at: which situation is this
file part of, and under what sensitivity class.

`104` R-32 and R-37 are one question and the lead ruled them one site. R-32 is that
the gate refuses every unclassified file a cloud call and 109 of the owner's 199
files are unclassified; R-37 is that the per-branch situation question was
registered, its trigger never fired and its reader never read. The question
`questions/triggers.py::question_for_situation` was written to ask a PERSON --
"Which of these is {branch_label}?", offering the library's own situation names --
is the question a model can be asked first, locally, and the person still confirms.

**LOCAL FIRST, and that is `00`:189-193 rather than a preference.** Hybrid mode's
own words are "Sensitive files remain LOCAL", and `privacy.denial.
unclassified_denies` refuses every CLOUD release of an unclassified file
unconditionally while permitting local ones. So an unclassified file is asked about
on the device, and only an ordinary verdict may then let it reach a provider. A file
this site declines to name stays local, which is the safe direction: a wrong
"ordinary" is what sends somebody's medical record away.

**THE MENU IS THE WHOLE LIBRARY, AND THE RECOGNISERS' CANDIDATES ARE EVIDENCE
(`00` amendment 7(c), 12 September 2026).** This module used to show the model
only the schemas a recogniser had raised, on the reading that a model naming a
schema nobody proposed would be `recognition/_CONTRACT.md` rule 5's invention
wearing a model's face. `104` §18.56 measured that reading on the owner's second
corpus and it does not hold: the shortlist held the key's own answer for 35 of 87
files, 28 menus offered one candidate plus the decline, the members offered most
often were `construction_property` (27) and `finance` (25) on a student's
Downloads folder, and 40 of the 60 abstentions were files whose answer was not on
the menu at all. A closed list that omits the answer three times in five is not
"valid options only"; it is the wrong question.

So the options are every member of `SCHEMA_IDS`, in the library's order, and then
the decline. Rule 5 is untouched -- the model still cannot name a class the
library does not have, which is what that rule is about -- and what the
recognisers raised is carried as EVIDENCE instead of as the cage: each candidate
item says whether the recognisers raised this schema for this file and on which
of the library's own terms, so the model reads the rules' opinion and is not
confined to it. `00`:39's "identify obvious candidate domains" is kept, as the
stage-two hint it was written as.

THE THREE WALLS ARE OPEN, 8 September 2026 (`104` §17.1), and this is what each
one turned into:

1. `llm_harness.vocabulary.CALL_SITES` carries seven members and the seventh is
   `G_situation_sensitivity`, recorded at the member on the sixth's own precedent.
   `SITUATION_SENSITIVITY` below is a RE-EXPORT of it, and
   `build_situation_request` builds a real `DossierRequest` rather than refusing.
2. `privacy.vocabulary.CLASSIFICATION_BASES` carries five and the fifth is
   `local_model_situation`. The owner's intent was that a model verdict must never
   be recorded as `detector`, and the spelling names the QUESTION because `96`
   §19's lesson is that a basis word must not overclaim what was checked.
3. A situation prompt is ratified LOCAL-ONLY, by the bakeoff of the two authored
   candidates under `103` §28.1. `ratified_local` is `prompt_library`'s own word
   for an approval to ACT on the answer with the cloud still shut.

WHAT THIS SITE IS ACTUALLY WORTH, and it is not what the register first said.
`104` §17.9 traced the fourth wall and found it does not exist: `privacy.denial.
UNCLASSIFIED_PERMITS_LOCAL` is `True`, so an unclassified file is NOT refused a
local call and never was. Nothing was silent. What happens instead is that
`cli.py` builds site A's activation as `ActivationSignal(schema_id=<the run's
--situation>, activates=lambda facts: True)` -- so every file is asked the
questions of the ONE situation the run was launched with, and a vaccination
record is asked which course it belongs to. That is R-23. **This site's job is
that each file is asked about ITS OWN situation instead of the run's**, and its
value shows up in spillover and in wrong-placement, not only in exact matches.

`tests/integration/test_situation_site_boundary.py` holds the record of each wall
opening; the tests were turned around rather than deleted.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.locator import serialize_locator
from evidence_shape.vocabulary import RELIABILITY_STATES
from facts.domains import SCHEMA_IDS
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import DossierRequest, EvidenceItem
from llm_harness.vocabulary import (
    CALL_SITES, DIRECT_ANCHOR, G_SITUATION_SENSITIVITY,
    MULTIPLE_PLAUSIBLE_DOMAINS, REMAINS_AMBIGUOUS,
)
from privacy.items import Excerpt
from privacy.release import ModelCallRequest, Target
#: `00` amendment 7(a)'s closed roster of identifier kinds, IMPORTED so
#: `_held_phrase` can tell a scheme's name from an authored work type without
#: keeping a second copy that stops matching the day a kind is renamed.
from extractors.entities import ENTITY_NAMESPACE, is_entity_extractor
from extractors.identifiers import KINDS as IDENTIFIER_KINDS
from recognition.detector import Precaution, SituationOutcome
from recognition.vocabulary import SAFETY_DOMAIN_IDS

#: P4's own word for a reading an extractor read explicitly, read off P4's tuple
#: rather than typed. A `candidate_schema` item and the abstention report are the
#: builder's own descriptions of what it knows for certain, so `direct` is the
#: truthful state for them -- and `EvidenceItem` checks membership, so a rename in
#: P4 goes red here rather than reaching a dossier as a word nothing recognises.
DIRECT: str = "direct"
if DIRECT not in RELIABILITY_STATES:  # pragma: no cover - a P4 rename
    raise ImportError(
        f"{DIRECT!r} is not one of P4's six reliability states "
        f"{RELIABILITY_STATES}; the states are P4's and this module reads them")

#: §8.5's per-stage decomposition needs a word for what this call is doing, and
#: this is the site's. Not `A_FACT`'s stage: an audit row saying `fact` for a call
#: that proposed no field would make the two indistinguishable in the one table
#: that records every release.
SITUATION_STAGE: str = "situation"

#: The recogniser's three reasons, in `00`:39's own words. Not a rule -- three
#: entries, each a translation between two vocabularies for one state.
#:
#: `ambiguous` is `multiple_plausible_domains` exactly: the schemas tied, which is
#: what "multiple plausible domains" says. `no_corroboration` and `no_evidence` are
#: a file that REMAINS AMBIGUOUS after the rules ran -- one term is not a domain and
#: no term is not a domain either.
_ELIGIBILITY_BY_REASON: dict[str, str] = {
    "ambiguous": MULTIPLE_PLAUSIBLE_DOMAINS,
    "no_corroboration": REMAINS_AMBIGUOUS,
    "no_evidence": REMAINS_AMBIGUOUS,
}

#: THE SEVENTH SITE'S NAME, AND IT IS NOW A MEMBER. The owner granted it on
#: 2026-09-08 (`104` §17.1) and the approval is recorded where a closed vocabulary
#: carries its own approval -- at the member, in `llm_harness.vocabulary`, on the
#: sixth member's own precedent. This is a RE-EXPORT and not a second spelling: one
#: call site with two string literals is two vocabularies, and the seam that decides
#: whether a request may be built would then have two answers.
#:
#: The spelling follows the six: a letter for the site and a word for what it asks
#: about. It asks TWO things that are one question -- which situation, and therefore
#: which sensitivity class -- because splitting them would ask a model to say a file
#: is medical without saying it is a medical record.
SITUATION_SENSITIVITY: str = G_SITUATION_SENSITIVITY

#: The structural option that makes the shortlist honest. Without it a closed list
#: is a forced choice, and `00`:42's "must return unknown where support is
#: insufficient" has nowhere to land. It is NOT a schema and never becomes one: the
#: validator scores it as a real answer, and the file stays local.
#:
#: Not a member of `SCHEMA_IDS`, deliberately, and `_require_schema` below is what
#: keeps it from being mistaken for one.
NONE_OF_THESE: str = "none_of_these"


class SituationSiteNotRatified(RuntimeError):
    """A request was asked for at a site the owner has not ratified."""


class NothingToAsk(ValueError):
    """No candidate was raised, so there is no question with valid options."""


@dataclass(frozen=True, slots=True)
class SituationQuestion:
    """One file's question, as the dossier will carry it.

    Everything here came from a recogniser outcome. Nothing is authored: the schema
    ids are the library's, the terms are what the file's own evidence matched, and
    the reason is the recogniser's own word for why it could not settle the case.
    """

    file_id: str
    content_hash: str
    #: The recogniser's own `ABSTENTION_REASONS` member -- `no_evidence`,
    #: `no_corroboration` or `ambiguous` on the owner's corpus -- or `None`
    #: because the recogniser did not abstain at all. See `recognised_as`.
    reason: str | None
    #: The closed list the model may answer from: since `00` amendment 7(c), every
    #: member of `SCHEMA_IDS` in the library's order, then `NONE_OF_THESE`.
    allowed_situations: tuple[str, ...]
    #: What the file matched, per candidate. A candidate the file matched nothing
    #: for is a candidate the semantic recogniser raised, and saying so is what
    #: keeps "near in vector space" from reading as "said this word".
    matched_terms: tuple[tuple[str, tuple[str, ...]], ...]
    #: The observation keys the candidates rest on, for the citation check.
    evidence_refs: tuple[str, ...]
    #: `104` §18 gap 24. THE HOLD THE RULES HAVE ALREADY TAKEN on this file, or
    #: `None` because they have taken none. `Detector.precaution_report`'s own
    #: answer, carried rather than re-derived: which of `00`'s four safety domains
    #: was read, which of its work types the file's evidence carries, and in which
    #: P4 zones. The model is being asked to judge a file the rules are holding,
    #: and until now the one thing it was never shown was that.
    precaution: Precaution | None = None
    #: `104` §18.26 gap 24b. The schema A RECOGNISER named for this file -- the
    #: term detector's own match, or, under `--semantic-model`, the composed
    #: recogniser's proposal where the rules abstained -- or `None` because none
    #: did. A recognised file is asked about only when the rules are ALSO holding
    #: it: `00`:110 still reserves the model for what the rules cannot settle, and
    #: `cli.ask_the_situation` is where that rule lives -- so this is never set
    #: without `precaution`, and what it adds to the question is the half the hold
    #: does not say: this file was named X and is held as Y, and the model is
    #: being asked which of the two it is.
    recognised_as: str | None = None

    #: WHAT THE RECOGNISERS ACTUALLY RAISED for this file -- the schemas they tied
    #: on, the near miss, the semantic recogniser's nearest and runner-up, and the
    #: domain any hold names. Since `00` amendment 7(c) this no longer decides
    #: WHICH options the model is shown; it decides what each option's item SAYS
    #: about itself. Empty for a file no recogniser raised anything for, which is
    #: now a question like any other rather than a file with nothing to ask.
    raised: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # EXACTLY ONE, because the recogniser either stopped or it named the file
        # and there is no third thing it can have done. Two nullable fields with
        # no invariant would let a question say both, and `_abstention_item` would
        # then have to choose which of two reports about one file to print.
        if (self.reason is None) == (self.recognised_as is None):
            raise ValueError(
                "a situation question states the recogniser's abstention reason "
                "or the schema it recognised, and exactly one of them: "
                f"reason={self.reason!r}, recognised_as={self.recognised_as!r}")
        # `104` §18.26 gap 24b's REFUSAL IS GONE, and `00` amendment 7(c) is the
        # act that removed it. It read: a file the recogniser RECOGNISED and the
        # rules are not holding is reserved from the model entirely, because
        # `00`:110 says "the LLM should not be called for direct, unique matches".
        # The owner has ruled that line no longer reserves the SITUATION from the
        # model, and the number is why: the rules' own measured top-1 accuracy on
        # the second corpus was 32.2% (`cli.SEMANTIC_MAX_ANCHOR_WORDS`' comment),
        # so two files in three that the rules "settled" were settled wrongly and
        # went to the cloud under a situation nobody had checked. A direct, unique
        # match is now the top-ranked candidate and not a bypass, which is exactly
        # what the constitution's placement ruling of 5 September already said
        # about the other site that used to skip the model.
        #
        # What replaces the refusal is not nothing: a recognised file's
        # `candidate_schema` item SAYS the recognisers raised that schema and on
        # which terms, so the rules' answer reaches the model as the strongest
        # thing on the page rather than as the only thing.
        if self.allowed_situations[-1:] != (NONE_OF_THESE,):
            raise NothingToAsk(
                f"the shortlist must end with {NONE_OF_THESE!r}; a closed list "
                "without it is a forced choice, and a model with no way to decline "
                "answers something about every file it is shown")
        # THE LIST-OF-ONE REFUSAL IS GONE TOO, for the same act and by
        # construction. It read: "a question whose only option is to decline is not
        # a question", and it was true of a menu built from what a recogniser
        # raised -- 60 of the owner's 112 lexical abstentions raised nothing at all
        # and got a list of one. Under `00` amendment 7(c) the list is the whole
        # library on every file, so there are always twenty-four options and the
        # condition it guarded cannot arise. The invariant is kept as a length
        # check rather than deleted, because what it was really defending is that
        # the model is given something to choose BETWEEN, and that is still the
        # property -- it now fails on a caller that built a shortlist by hand
        # rather than on a file the recognisers were quiet about.
        if len(self.allowed_situations) < 2:
            raise NothingToAsk(
                "a question whose only option is to decline is not a question. "
                "Since `00` amendment 7(c) the options are the whole library, so "
                "reaching this means a caller built the list itself rather than "
                "asking `shortlist_for` for it")


def _require_schema(schema_id: str) -> str:
    if schema_id not in SCHEMA_IDS:
        raise ValueError(
            f"{schema_id!r} is not one of the {len(SCHEMA_IDS)} schemas the "
            f"product recognises. A shortlist is built from the library's own "
            f"names or it is not a list of valid options."
        )
    return schema_id


def shortlist_for(outcome: SituationOutcome,
                  precaution: Precaution | None = None) -> tuple[str, ...]:
    """The valid options for one file: the whole library, then the decline.

    **THE LIST NO LONGER DEPENDS ON THE FILE, and `00` amendment 7(c) is the act.**
    This used to return only the schemas the recognisers had raised, plus any held
    safety domain, plus the decline -- and every argument for that is preserved
    below, because each of them was true and none of them survived measurement.

    * *"The candidates arrive raised"* (`104` §18.26). Still true, and still the
      one place a candidate is raised: `raised_for` reads the same projection this
      function used to filter by. What changed is what the raising is FOR -- it
      aims the question through the candidate items' own words instead of closing
      the list.
    * *"Measured on the owner's corpus ... 60 abstain `no_evidence` ... so the
      lexical side raises nothing for them and this returns a list of one, which
      `SituationQuestion` refuses."* That refusal is gone with the narrowing: a
      file the recognisers were quiet about now gets the same twenty-four options
      as every other file, which is the honest state -- the recognisers being quiet
      is a fact about the recognisers.
    * *"The hold is an option too."* Every safety domain is on the list on every
      file now, so a hold can no longer be the only way one of `00`'s four reaches
      it. The hold still rides in the dossier, on the `recogniser_abstention`
      item, where the model reads what the rules are holding this file as.

    **WHAT REPLACED IT IS THE MEASUREMENT.** `104` §18.56: the shortlist held the
    key's own answer for 35 of 87 files; 28 menus offered one candidate and the
    decline; 40 of 60 abstentions were files whose answer was not on the menu. A
    closed list is only "valid options only" while the answer is one of them.

    `NONE_OF_THESE` is still always last and always present, and is still the one
    member here that is not a schema. `outcome` and `precaution` are still taken:
    they are validated (`_require_schema` refuses a name the library does not
    have, which is the check that used to run on the way in) and `question_for`
    reads the raised set off the same pair.
    """
    for schema_id in outcome.candidates:
        _require_schema(schema_id)
    if precaution is not None:
        _require_schema(precaution.schema_id)
    return SCHEMA_IDS + (NONE_OF_THESE,)


def raised_for(outcome: SituationOutcome,
               precaution: Precaution | None = None) -> tuple[str, ...]:
    """The schemas the recognisers RAISED for this file, in `SCHEMA_IDS` order.

    What `shortlist_for` used to return, minus the decline, and it is now evidence
    rather than a menu: `_candidate_items` reads it to say, per option, whether the
    recognisers raised this schema for this file or whether it is a library member
    they did not. `00`:39's stage two -- "identify obvious candidate domains" -- is
    kept exactly here and nowhere else.

    **THE ORDER IS `SCHEMA_IDS`', not the order the candidates arrived in**, on the
    reason that survived the amendment unchanged: two recognisers contribute and
    their orders are their own, so a set whose order depended on which spoke first
    would be a different prompt for the same file (`104` R-58).

    The hold's domain is in it. A file the rules are holding as `medical` has had
    `medical` raised for it by the strongest thing the rules do, and an item saying
    the recognisers did not raise it would be false on the one file where the
    stakes are highest.
    """
    raised = {_require_schema(schema_id) for schema_id in outcome.candidates}
    if precaution is not None:
        raised.add(_require_schema(precaution.schema_id))
    return tuple(schema_id for schema_id in SCHEMA_IDS if schema_id in raised)


def question_for(outcome: SituationOutcome, *, file_id: str,
                 content_hash: str,
                 precaution: Precaution | None = None) -> SituationQuestion:
    """One file's question, or `NothingToAsk`.

    **REFUSING IS NO LONGER AN OUTCOME OF THIS FUNCTION, and `00` amendment 7(c)
    is why.** It used to be the common one: "a file the recognisers raised no
    candidate for has no question with valid options", which was 60 of the owner's
    112 lexical abstentions. The options are the whole library now, so every file
    has a question; `NothingToAsk` still exists and is still raised, one function
    down, for a file with no releasable READING -- which is `00`:42's own condition
    and a fact about the file rather than about the recognisers.

    `precaution` is SUPPLIED and never derived here. The hold is the detector's
    conclusion and this module reads no rules of its own -- the same discipline
    the outcome's own terms and refs arrive under.

    **ONE OUTCOME SHAPE, AND IT IS NOT THIS MODULE'S (`104` §18.26's owed row).**
    This took a `Recognition` or an `Abstention` and asked `isinstance` which it
    had -- so under `--semantic-model`, where the composed recogniser answers in
    records of its own, the test was false either way and site G asked nothing at
    all. `recognition.SituationOutcome` is the shape both recognisers project
    into, and every field below is read off it rather than being reconstructed
    from a record class. A third recogniser would need no line here.

    **A RECOGNITION IS A QUESTION LIKE ANY OTHER (`00` amendment 7(c)).** Gap 24b
    made a recognised file askable only through a hold, because `00`:110 reserved
    the model from a direct, unique match. The owner has ruled that line no longer
    reserves the SITUATION, on the measurement: the rules' top-1 accuracy on the
    second corpus was 32.2%, so "settled" meant "wrong two times in three and sent
    to the cloud anyway". WHICH files reach here is still `cli.ask_the_situation`'s
    ruling and not this module's -- and its answer is now every file on the roster.
    What the recogniser concluded is not lost: it reaches the model on its own
    schema's `candidate_schema` item and in the report item, as the rules' opinion
    rather than as the boundary of the question.
    """
    return SituationQuestion(
        file_id=file_id, content_hash=content_hash,
        reason=outcome.reason,
        recognised_as=outcome.recognised,
        allowed_situations=shortlist_for(outcome, precaution),
        raised=raised_for(outcome, precaution),
        matched_terms=outcome.matched_terms,
        evidence_refs=outcome.evidence_refs,
        precaution=precaution,
    )


#: The abstention report's own address on the wire. Not an observation key and not
#: a schema id: it is the ONE item of a situation dossier that is neither, and the
#: ratified prompt names it -- *"a `recogniser_abstention` item is the reason the
#: rules stopped ... It is a report, not a verdict: the rules aimed the question and
#: you answer it."*
#:
#: A constant rather than a per-file string, deliberately. `wire_handles.wire_ref`
#: leaves a non-observation reference raw, so whatever is here reaches the model
#: verbatim; a per-file address would put an identifier of this person's file into
#: the model-visible bytes through a slot nothing keys.
ABSTENTION_REF: str = "abstention"

#: What the model may cite. The abstention report and the candidate schemas are
#: REFERENCES the builder describes, not text P7 released, and the ratified prompt
#: says so in its own rule 2: *"Cite only keys that appear in `released_evidence`: a
#: candidate, the abstention report or a reading is not evidence and cannot be
#: cited."* Nothing here enforces that -- `validation._check_citation` already does,
#: by requiring the cited ref to be among the dossier's RELEASED items -- and the
#: two agreeing is the property, not a second check.
_REFERENCE_ONLY_KINDS: tuple[str, ...] = ("recogniser_abstention", "candidate_schema")


def _held_phrase(precaution: Precaution | None) -> str:
    """What the rules are holding this file as, in the rules' own words.

    **`104` §18 gap 24, and it goes through the DOSSIER rather than the prompt.**
    The owner's constraint is exact: the term list never appears in the template
    text -- it is this file's evidence, addressed like every other authority, and
    the model reads it where it reads the abstention report it already gets.

    Empty for a file the rules are not holding, which is most of them: an item
    that said "held: no" on every ordinary file would spend the shared prefix
    `104` R-58 exists to protect on a fact that is the absence of a fact.

    The terms are the LIBRARY's authored words and the zones are P4's own zone
    names -- the same class of value `matched` above already carries, and neither
    is a word out of the person's file.

    **AND SINCE `00` AMENDMENT 7(a), A TERM MAY BE AN IDENTIFIER KIND, which is a
    different sentence and is said differently.** `payment_card` is not a work type
    -- the document did not use the words, its digits passed Luhn -- and printing
    "on the work type payment_card" would tell the local model the file says
    something it does not say, on the one line that explains the hold. The two are
    told apart by `extractors.identifiers.KINDS`, which is that extractor's own
    closed roster, so nothing here keeps a second list. The kind is still not a word
    out of the person's file: it is the name of a numbering scheme.

    **AND SINCE 7(b), A TERM MAY BE AN ENTITY THE LOCAL ENCODER NAMED**, which is a
    third sentence: not a word the author wrote and not a checksum, but a model's
    reading of what a span IS. Those carry their own `entities.` prefix -- the label
    set is the deployment's, so there is no closed roster to check a bare kind
    against -- and are printed without it, so the model is told "on the entities
    person, medical_condition" and can weigh a pairing as a pairing.
    """
    if precaution is None:
        return ""
    entities = ", ".join(term[len(ENTITY_NAMESPACE):] for term in precaution.terms
                         if is_entity_extractor(term))
    kinds = ", ".join(term for term in precaution.terms
                      if term in IDENTIFIER_KINDS)
    terms = ", ".join(term for term in precaution.terms
                      if term not in IDENTIFIER_KINDS
                      and not is_entity_extractor(term))
    zones = ", ".join(precaution.zones)
    return (f" | held: the rules are holding this file as "
            f"{precaution.schema_id} material"
            + (f", on the work type {terms}" if terms else "")
            + (f", on the identifier {kinds}" if kinds else "")
            + (f", on the entities {entities}" if entities else "")
            + (f", found in {zones}" if zones else ""))


def _stopped_phrase(question: SituationQuestion) -> str:
    """WHERE THE RULES GOT TO on this file, in the rules' own words.

    Two states and no third: the recogniser abstained and says why, or it
    recognised the file and says as what. `104` §18.26 gap 24b added the second,
    because a file that is recognised AND held is now asked and the report it
    carries must not open with a word -- "abstention" -- that is not what
    happened. The register is the one the first state already set: the
    recogniser's own conclusion, its own schema ids, and no word out of the
    person's file.

    THE ITEM KIND DOES NOT MOVE and the phrase does. `recogniser_abstention` is
    the address the ratified prompt describes -- *"the reason the rules stopped
    ... a report, not a verdict: the rules aimed the question and you answer
    it"* -- and a recognition under a hold IS the rules stopping: they named the
    file and then held it as something else. A sibling kind would be an item the
    approved text never describes, met on exactly the files where the stakes are
    highest, which is `_abstention_item`'s own argument one function down.

    **IT SAYS "THE RECOGNISER" AND NOT "THE RULES" (`104` §18.26's owed row).**
    Under `--semantic-model` the schema named here can be the composed
    recogniser's nearest neighbour on a file the term detector abstained on, and
    "the rules recognised this file as X" would then be a false sentence in the
    one dossier where the model is judging a hold. The word that is true of both
    recognisers is the one the item is already addressed by.
    """
    if question.recognised_as is None:
        return f"recogniser abstention | reason: {question.reason}"
    return ("recogniser report | the recogniser recognised this file as "
            f"{question.recognised_as}")


def _abstention_item(question: SituationQuestion) -> EvidenceItem:
    """The recogniser's own report of why it stopped, as one reference item.

    Every word of `location` comes from the recogniser: where it got to
    (`_stopped_phrase` -- its reason and near miss, or, since `104` §18.26 gap
    24b, the schema it RECOGNISED where it did not abstain at all), the ids it
    tied on, the terms each candidate matched, and -- since `104` §18 gap 24 --
    the hold its precaution took and what raised it. Nothing is authored here and
    nothing about the person's file beyond what the recogniser already concluded
    reaches the bytes -- the matched terms are the LIBRARY's authored words,
    which is what `test_a_tie_is_a_question_for_the_model` asserts of them.

    THE HOLD RIDES ON THIS ITEM RATHER THAN A NEW ONE, and that is a choice about
    what the ratified prompt already says. Its rule for this item is *"a
    `recogniser_abstention` item is the reason the rules stopped ... It is a
    report, not a verdict: the rules aimed the question and you answer it"* -- and
    a precaution IS the rules stopping, in the strongest form they have. A sibling
    kind would be an item the approved text never describes, so the model would
    meet an unexplained kind on exactly the files where the stakes are highest.
    """
    matched = "; ".join(
        f"{schema_id}: {', '.join(terms)}" if terms else f"{schema_id}: no term"
        for schema_id, terms in question.matched_terms)
    return EvidenceItem(
        evidence_ref=ABSTENTION_REF,
        kind="recogniser_abstention",
        location=(
            _stopped_phrase(question)
            + f" | shortlist: {', '.join(question.allowed_situations)}"
            + (f" | matched: {matched}" if matched else "")
            + _held_phrase(question.precaution)),
        excerpt_span=None,
        reliability_state=DIRECT,
        basis=DIRECT_ANCHOR,
    )


def _named(schema_id: str, schema_names: Mapping[str, str]) -> str:
    """The schema's authored name beside its id, or nothing where the library
    carries none. 13 Sep 2026: the cloud judge was shown `nonprofit` and had no way
    to know it is the home of a club, a society or a student organisation; the
    ratified text told it to find "a student organisation stated by a club" and
    nothing on the menu said which member that was -- 47 wrong answers on the
    owner's corpus. The name is the schema row's own `name` and is composed by
    nobody here; it costs about a dozen tokens a member, measured in `104` §18.60.
    """
    name = schema_names.get(schema_id)
    return f"{name} | " if name and name != schema_id else ""


def _candidate_items(question: SituationQuestion,
                     safety_domain_ids: Sequence[str],
                     schema_names: Mapping[str, str] = MappingProxyType({}),
                     ) -> tuple[EvidenceItem, ...]:
    """One item per option -- the whole library and the decline -- and no option
    without one.

    **TWENTY-FOUR ITEMS SINCE `00` amendment 7(c)**, where there used to be as few
    as two. The menu is every member of `SCHEMA_IDS` in the library's order, then
    the decline, and the recognisers' candidates are carried HERE, in what each
    item says about itself, rather than by deciding which items exist.

    **EACH ITEM SAYS WHETHER THE RECOGNISERS RAISED IT, and that is the whole of
    what this function judges beyond the protected-kind note.** A raised schema
    says so and names the library's own terms the file matched for it; a raised
    schema with no term is the semantic recogniser's neighbour and says that, which
    is what keeps "near in vector space" from reading as "said this word"; a schema
    the recognisers did not raise says that too, because an item that was silent
    about it would leave the model to guess whether silence meant "not considered"
    or "considered and rejected". `00`:39's stage two survives exactly here: the
    obvious candidate domains are identified and shown, and they no longer close
    the list.

    **THE DECLINE GETS AN ITEM TOO**, unchanged: it is on `allowed_vocabulary`, so
    a model reading the vocabulary and then the items would otherwise find one
    option it was offered and never described -- the one the prompt most wants used
    when nothing on the list is stated.

    **`location` SAYS WHETHER THE KIND IS ONE OF THE FOUR THE PRODUCT PROTECTS**,
    read off `recognition.vocabulary.SAFETY_DOMAIN_IDS` rather than listed here:
    `00`:52's four are the recogniser's own list and a second copy would be a
    second answer to which material is protected.

    **THE COST, MEASURED, AND `104` §18.56 PRICED IT AT "about 1,200 more prompt
    tokens per dossier" BEFORE IT WAS BUILT.** Measured over the shipped library
    (23 schemas, four of them protected) on a two-candidate tie: the twenty-four
    items carry 1,524 characters of `location` text where the old three carried
    262, and 4,977 bytes of canonical item JSON where the old three carried 703 --
    +1,262 characters of description and +4,274 bytes of frame. The whole block is
    about 1,244 tokens at four characters a token, which is §18.56's estimate
    almost exactly, and at most 4,977 under `model_facts.dossier_tokens`' own
    character bound.

    The wording above is what holds it there and is why the descriptions are
    curt: an unraised member costs 40 characters plus its schema id, and on an
    ordinary file twenty-one of the twenty-four are unraised. A sentence per
    schema saying what that schema is FOR -- the obvious next thing to add --
    would multiply this block several times over on every file in the corpus, and
    what the model needs from an option it was not offered before is that it
    exists and that the rules did not point at it.

    **IT DOES NOT COME OUT OF `GROUPING_LIMITS.max_dossier_tokens`, which is what
    made the growth affordable.** That ceiling and the door's own
    `over_dossier_ceiling` both measure the RELEASED values, and a candidate item
    releases nothing -- `gate.REFERENCE_ONLY` is where that is decided and
    `_REFERENCE_ONLY_KINDS` above is this module's half of it. §18.56 read the
    growth as "the bound would need to give way or the descriptions shorten"; the
    bound did not have to, because the bound was never over this.
    """
    raised = set(question.raised)
    terms = {schema_id: matched for schema_id, matched in question.matched_terms}
    items = []
    for schema_id in question.allowed_situations:
        if schema_id == NONE_OF_THESE:
            where = ("no situation on this list | choosing this leaves the file "
                     "where the rules left it, on this device, for a person")
        elif schema_id in raised:
            matched = ", ".join(terms.get(schema_id, ()))
            where = (f"{schema_id} | {_named(schema_id, schema_names)}"
                     f"the recognisers raised this for this file"
                     + (f", on: {matched}" if matched else ", on no term"))
        else:
            where = (f"{schema_id} | {_named(schema_id, schema_names)}"
                     f"in the library; not raised for this file")
        if schema_id in safety_domain_ids:
            where += " | one of 00's four protected kinds"
        items.append(EvidenceItem(
            evidence_ref=schema_id, kind="candidate_schema", location=where,
            excerpt_span=None, reliability_state=DIRECT, basis=DIRECT_ANCHOR))
    return tuple(items)


def build_situation_request(
    question: SituationQuestion,
    observations: Sequence, *,
    model_target,
    prompt,
    max_dossier_tokens: int,
    safety_domain_ids: Sequence[str] = SAFETY_DOMAIN_IDS,
    schema_names: Mapping[str, str] = MappingProxyType({}),
) -> DossierRequest:
    """One file's situation question, as the reference-only request P7 decides on.

    THE WALL THAT USED TO BE HERE IS OPEN. This function raised
    `SituationSiteNotRatified` and counted what was waiting behind it; `104` §17.1
    is the owner's act that made the count zero. What replaces the refusal is the
    request the refusal described: `DossierRequest` validates `call_site` against
    `CALL_SITES`, which now carries this site, and `eligibility_reason` against
    `ELIGIBILITY_BY_SITE`, which gives it site A's three.

    **No text crosses this line.** Every field is a reference: the schema ids are
    the library's, the abstention report is the recogniser's own words about its own
    conclusion, and the file's readings are `Excerpt` items naming observation keys.
    What the model is shown of the file is whatever P7 decides to release for those
    keys, at the door, and this function cannot widen it.

    **The eligibility reason is the recogniser's reason, translated once.**
    `ambiguous` IS `00`:39's "multiple plausible domains" -- the same sentence, in
    two vocabularies -- and the other two reasons are a file that remains ambiguous.
    The mapping is `_ELIGIBILITY_BY_REASON` and it is three entries, not a rule.
    """
    if not observations:
        # NOT A DOSSIER WITH NOTHING IN IT. `DossierRequest` refuses an empty
        # `evidence_items` and `ModelCallRequest` refuses empty `requested_items`,
        # so a file whose readings were all withheld would raise at the constructor
        # -- correctly, but from a place that cannot say what happened. It is said
        # here: `00`:42's "must return unknown where support is insufficient" is
        # about the MODEL's answer, and a file with no releasable reading never gets
        # far enough to be asked. It stays where the rules left it, which is local.
        raise NothingToAsk(
            f"{question.file_id} has a shortlist and no releasable reading, so "
            f"there is nothing for a model to read the answer out of. A question "
            f"with valid options and no evidence is not a question `00`:42 permits "
            f"an answer to: the file stays where the rules left it.")
    return DossierRequest(
        call_site=SITUATION_SENSITIVITY,
        subject_ref=question.file_id,
        eligibility_reason=_ELIGIBILITY_BY_REASON.get(
            question.reason, REMAINS_AMBIGUOUS),
        # THE FRAME'S ITEMS FIRST and the file's after them. `104` R-58: the
        # dossier's shared prefix is what does not vary between two files of one
        # run, and for this site the candidates and the abstention's SHAPE are
        # nearly constant while the readings are not.
        evidence_items=_candidate_items(question, safety_domain_ids, schema_names)
        + (_abstention_item(question),)
        + tuple(
            EvidenceItem(
                evidence_ref=observation.observation_key,
                kind="excerpt",
                location=serialize_locator(observation.location),
                excerpt_span=(
                    None if observation.location.text_span is None else
                    (observation.location.text_span.start,
                     observation.location.text_span.end)),
                reliability_state=observation.reliability,
                basis=DIRECT_ANCHOR,
            )
            for observation in observations
        ),
        # This site asks about ONE file and retrieves no neighbours, so there is no
        # competing value for the engine to have recorded. The prompt says the same
        # thing to the model: "`field_glossary`, `folder_levels` and `conflicts` are
        # empty at this site."
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=SITUATION_STAGE,
            # ONE FILE AND NO NEIGHBOUR. Site A's target grows to hold the files a
            # context reading came from; this one cannot, because nothing here
            # gathers a neighbour's readings. A single id is also what makes
            # `gate._decisive` read this file's own handling class as the one the
            # release is judged under.
            target=Target(file_ids=(question.file_id,), group_id=None),
            model_target=model_target,
            requested_items=tuple(
                Excerpt(
                    observation_key=observation.observation_key,
                    span=observation.location.text_span,
                    reason="a reading of this file the situation may rest on",
                )
                for observation in observations
            ),
            prompt_template_id=prompt.template_id,
            # THE PROMPT'S OWN FINGERPRINT, never the dossier's address.
            # `transport.issue` recomputes this from the `PromptDefinition` it is
            # about to send and refuses the release when the two disagree, after P7
            # has already spent it. `model_facts.build_fact_request` records what
            # that cost at site B and the note is repeated here rather than left to
            # be rediscovered.
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens,
        ),
        plan_version=None,
        # C and D need one; this site proposes no destination in any tree, so it has
        # no snapshot to be judged against. `SITES_REQUIRING_EVIDENCE_SNAPSHOT` is
        # the list that decides it and this site is not on it.
        evidence_snapshot_id=None,
    )

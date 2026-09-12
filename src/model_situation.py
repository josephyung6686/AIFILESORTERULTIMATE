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

**VALID OPTIONS ONLY (constitution 3), and the classifier aims the question.** The
model is not shown the 23 schemas and asked to pick. It is shown the candidates the
recogniser itself raised -- the schemas it tied on, its near miss, the semantic
recogniser's nearest and runner-up -- plus one structural option meaning none of
them fits. `recognition/_CONTRACT.md` rule 5 forbids the recogniser inventing a
class to let the pipeline continue, and a model naming a schema nobody proposed
would be that same invention wearing a model's face.

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

from collections.abc import Sequence
from dataclasses import dataclass

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
    #: The closed list the model may answer from, `NONE_OF_THESE` last.
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
        if self.recognised_as is not None and self.precaution is None:
            raise ValueError(
                f"{self.file_id} was recognised as {self.recognised_as!r} and is "
                "not held, so `00`:110 reserves it from the model entirely -- "
                "\"the LLM should not be called for direct, unique matches\". "
                "A recognised file becomes a question only through a hold "
                "(`104` §18.26 gap 24b)")
        if self.allowed_situations[-1:] != (NONE_OF_THESE,):
            raise NothingToAsk(
                f"the shortlist must end with {NONE_OF_THESE!r}; a closed list "
                "without it is a forced choice, and a model with no way to decline "
                "answers something about every file it is shown")
        if len(self.allowed_situations) < 2:
            raise NothingToAsk(
                "a question whose only option is to decline is not a question. "
                "The recogniser raised no candidate for this file, so there is "
                "nothing for a model to choose BETWEEN, and asking anyway would "
                "invite it to invent one")


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
    """The valid options for one file, from what the recognisers actually raised.

    **The order is `SCHEMA_IDS`', not the order the candidates arrived in.** Two
    recognisers contribute and their orders are their own; a shortlist whose order
    depended on which one spoke first would be a different prompt for the same file,
    and `104` R-58 is the same argument about the dossier's bytes.

    `NONE_OF_THESE` is always last and always present. It is the only member here
    that is not a schema.

    **THE CANDIDATES ARRIVE RAISED, and that is `104` §18.26's owed row.** This
    used to take the recogniser's record and a second `semantic` object beside it
    and read candidates off both -- so a caller that forgot the second argument
    got a shortlist missing half of what had been raised, which is what site G
    did on every run: `cli.ask_the_situation` passed `semantic=None` always.
    `SituationOutcome.candidates` is now the ONE place a candidate is raised and
    both recognisers project into it. Measured on the owner's corpus, that is what
    the biggest bucket needed: of the 112 files the term detector abstains on, 60
    abstain `no_evidence` -- they carry no term any schema authored -- so the
    lexical side raises nothing for them and this returns a list of one, which
    `SituationQuestion` refuses. Those 60 become askable through the composed
    recogniser's own candidates, which is what makes the two mechanisms partners
    rather than alternatives.

    **THE HOLD IS AN OPTION TOO (`104` §18.26 gap 24b), and on a lexical
    abstention it is a no-op that is worth stating.** `Detector.precaution_report`
    reads an abstention's hold off `(schema_id, *tied_schema_ids)` -- which is
    exactly what that abstention's `candidates` are -- so adding the held domain
    can never widen the list there, and the argument changes nothing for the files
    gap 24 already asked about. On a RECOGNISED file it is the whole of what makes
    the question a question: the recogniser named ONE schema, the hold names
    another, and a shortlist of the winner alone would ask a model holding a
    passport whether it is coursework, with no way to say that it is not. It is
    also the only way one of `00`'s four ever reaches this list on the semantic
    path, which raises none of them.
    """
    raised = {_require_schema(schema_id) for schema_id in outcome.candidates}
    if precaution is not None:
        raised.add(_require_schema(precaution.schema_id))
    return tuple(
        schema_id for schema_id in SCHEMA_IDS if schema_id in raised
    ) + (NONE_OF_THESE,)


def question_for(outcome: SituationOutcome, *, file_id: str,
                 content_hash: str,
                 precaution: Precaution | None = None) -> SituationQuestion:
    """One file's question, or `NothingToAsk`.

    Refusing is a real outcome and the common one today: a file the recognisers
    raised no candidate for has no question with valid options, and `00`:259's
    "mark the deferred stage ... rather than guessing" is what happens to it.

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

    **A RECOGNITION IS A QUESTION ONLY BECAUSE OF THE HOLD (`104` §18.26 gap
    24b).** WHICH files reach here is `cli.ask_the_situation`'s ruling and not
    this module's; what this function owes such a file is the shortlist the
    owner's ruling names -- the schema the recogniser named, and the safety
    domain(s) the hold names -- so the model can answer the ordinary situation
    that was read, or a protected one, or none of them. The outcome raises only
    the recognised schema as a candidate in that case, so this stays true of a
    semantic proposal without a word here about which recogniser spoke.
    """
    return SituationQuestion(
        file_id=file_id, content_hash=content_hash,
        reason=outcome.reason,
        recognised_as=outcome.recognised,
        allowed_situations=shortlist_for(outcome, precaution),
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
    """
    if precaution is None:
        return ""
    kinds = ", ".join(term for term in precaution.terms
                      if term in IDENTIFIER_KINDS)
    terms = ", ".join(term for term in precaution.terms
                      if term not in IDENTIFIER_KINDS)
    zones = ", ".join(precaution.zones)
    return (f" | held: the rules are holding this file as "
            f"{precaution.schema_id} material"
            + (f", on the work type {terms}" if terms else "")
            + (f", on the identifier {kinds}" if kinds else "")
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


def _candidate_items(question: SituationQuestion,
                     safety_domain_ids: Sequence[str]) -> tuple[EvidenceItem, ...]:
    """One item per option, the decline included, and no option without one.

    THE DECLINE GETS AN ITEM TOO. It is on `allowed_vocabulary`, so a model reading
    the vocabulary and then the items would find one option it was offered and never
    described -- and the option it would find undescribed is the one the prompt most
    wants used when the two readings are close.

    **`location` says whether the kind is one of the four the product protects**, in
    the prompt's own terms, and that is the only judgement in this function. It is
    read off `recognition.vocabulary.SAFETY_DOMAIN_IDS` rather than listed here:
    `00`:52's four are the recogniser's own list and a second copy would be a second
    answer to which material is protected.
    """
    items = []
    for schema_id in question.allowed_situations:
        if schema_id == NONE_OF_THESE:
            where = ("no situation on this list | choosing this leaves the file "
                     "where the rules left it, on this device, for a person")
        else:
            where = f"{schema_id} | a situation the recogniser shortlisted for this file"
            if schema_id in safety_domain_ids:
                where += (" | one of 00's four protected kinds: material of this "
                          "kind is protected before any cloud or automated "
                          "placement decision is allowed")
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
        evidence_items=_candidate_items(question, safety_domain_ids)
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

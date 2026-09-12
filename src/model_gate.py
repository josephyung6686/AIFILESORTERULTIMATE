# src/model_gate.py
"""The eighth call site: which of the ten restricted kinds, if any, is this file?

`00` amendment 7(c), the owner's go of 12 September 2026. Site G was one call
asking two questions -- which situation, and which restricted kind -- and
`104` §18.56 measured what that cost on the owner's second corpus: the site was
asked about a minority of files, from a shortlist that held the right answer for
35 of 87; 60 of 83 verdicts abstained; and two health forms the rules had called
ordinary went to the cloud with no model ever reading them. The ruling splits the
call in two, and this module is the half that decides whether a file may leave.

**WHAT MAKES THIS A SITE OF ITS OWN.** The two questions have different
populations, different dossiers and different destinations. The gate runs for
EVERY file the deterministic layers could not settle either way, over a SHORT
dossier -- an identity number, a patient field, a booking reference and a balance
sit in the opening of a document and in its metadata -- and it runs on this
machine, always. The situation question runs for every file over the whole
library, and for a file this gate clears it may run on the cloud. One prompt
asking both put the protection axis on the back of a menu that omitted the answer
three times in five.

**THE MENU IS CLOSED AND IT IS NOT THIS MODULE'S.** `105` §13.3's ten kinds are
the owner's, ruled member by member, and the eleventh option is the structural
decline every closed list at this product needs (`00`:42: "must return unknown
where support is insufficient"). Both are read off the library's own schema
rather than spelled here -- see `restricted_kind_vocabulary` -- because a model
shown one list and validated against another is two vocabularies the moment they
are two literals.

**NOTHING IS AUTHORED IN A GATE DOSSIER.** It carries the file's own releasable
readings as `excerpt` items and nothing else: the ten kinds and what each one
means are in the ratified template, which is the same bytes on every file, so a
per-file item describing them would spend the shared prefix `104` R-58 protects
on text that never varies. That is also what keeps this dossier short, which is
the whole point of the split -- the gate is asked about every file in the corpus.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass

from evidence_shape.locator import serialize_locator
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.records import DossierRequest, EvidenceItem
from llm_harness.vocabulary import (
    DIRECT_ANCHOR, H_RESTRICTED_KIND, MULTIPLE_PLAUSIBLE_DOMAINS,
    REMAINS_AMBIGUOUS,
)
from model_situation import NONE_OF_THESE, NothingToAsk
from privacy.items import Excerpt
from privacy.release import ModelCallRequest, Target
from privacy.vocabulary import RESTRICTED_KINDS

#: THE EIGHTH SITE'S NAME, RE-EXPORTED and not respelled, on `model_situation.
#: SITUATION_SENSITIVITY`'s own argument: one call site with two string literals
#: is two vocabularies, and the seam that decides whether a request may be built
#: would then have two answers.
RESTRICTED_KIND: str = H_RESTRICTED_KIND

#: §8.5's per-stage decomposition needs a word for what this call is doing.
#: Not `situation`: an audit row saying `situation` for a call that named no
#: situation would make the two indistinguishable in the one table that records
#: every release, which is the argument `SITUATION_STAGE` already makes against
#: borrowing site A's word.
GATE_STAGE: str = "restricted_kind_gate"

#: Where the ten come from. `situation_response_schema.v2.json` is the file the
#: owner ratified the ten into on 9 September (`104` §18.7 S2), and reading them
#: off it is `observe_allowed_vocabulary`'s rule applied here: the model is shown
#: one list and validated against another the moment those are two literals.
_TEN_KINDS_SCHEMA: str = "situation_response_schema.v2.json"


def _library_file(name: str) -> bytes:
    from llm_harness.prompt_library import DRAFTS_FILE
    return (DRAFTS_FILE.parent / name).read_bytes()


def restricted_kind_vocabulary() -> tuple[str, ...]:
    """The eleven options the gate may answer with: the ten kinds, then the decline.

    **READ FROM THE SCHEMA AND NOT SPELLED HERE**, which is
    `cli.observe_allowed_vocabulary`'s own rule: "the model is shown one list and
    validated against another the moment those are two literals, and this is the
    file that would hold the second one." The ten are the enum the owner ratified
    into `situation_response_schema.v2.json`.

    **AND CHECKED AGAINST P7's OWN TUPLE, once, here.** `privacy.vocabulary.
    RESTRICTED_KINDS` is what `cli.restricted_kind_named_by_verdict` tests the
    answer against and what `privacy_class_for` turns into a class, so the schema
    and the vocabulary being one list is the property this site rests on. Two
    lists that agreed on the day this was written and drift later would clear a
    file for the cloud on a kind the store cannot record.

    `NONE_OF_THESE` is last and is `model_situation`'s own constant rather than a
    second spelling: the product has one word for a model declining to name
    something, and the file that stays local depends on which one a reader tested.
    """
    schema = json.loads(_library_file(_TEN_KINDS_SCHEMA).decode("utf-8"))
    payload = schema["properties"]["claims"]["items"]["properties"]["payload"]
    kinds = tuple(payload["properties"]["restricted_kind"]["enum"])
    if kinds != RESTRICTED_KINDS:
        raise ValueError(
            f"{_TEN_KINDS_SCHEMA} closes {kinds} and `privacy.vocabulary."
            f"RESTRICTED_KINDS` is {RESTRICTED_KINDS}. The gate shows the first "
            f"list to a model and the store records against the second; two "
            f"lists is a kind that can be named and not written down")
    return kinds + (NONE_OF_THESE,)


@dataclass(frozen=True, slots=True)
class GateQuestion:
    """One file's gate question, as the dossier will carry it.

    THREE FIELDS AND NO SHORTLIST, which is the difference from
    `SituationQuestion` and is the ruling rather than an economy. The options are
    the same eleven for every file in every corpus -- the ten kinds are the
    owner's closed list and the eleventh is the decline -- so there is nothing per
    file for a recogniser to raise, nothing to order, and no way for this question
    to be narrower on one file than on another. A gate whose menu varied with what
    the rules had noticed would be the shortlist defect (`104` §18.56) moved one
    site along.
    """

    file_id: str
    content_hash: str
    #: The recogniser's own `ABSTENTION_REASONS` member, or `None` because it did
    #: not abstain. Carried for the ELIGIBILITY REASON only: `DossierRequest`
    #: checks one against `ELIGIBILITY_BY_SITE`, and a file the rules recognised
    #: is still a file whose restricted kind remains open, which is
    #: `remains_ambiguous` in `00`:39's own words.
    reason: str | None = None
    #: The observation keys this question was built over -- the readings the gate
    #: was shown. `cli.gate_classification` cites them, because at this site they
    #: ARE what the verdict rests on: there is no recogniser shortlist behind a
    #: gate answer and no hold behind it either, only the file's own opening as the
    #: model read it. `situation_classification`'s rule stated for this site's one
    #: kind of row.
    evidence_refs: tuple[str, ...] = ()


#: What the model sees a masked identifier reading called. Not `excerpt`: the two
#: are different things to the reader the ratified gate template describes -- *"An
#: 'identifier' item, when present, reports that a deterministic check found the
#: shape of an identifier in the file (a card number, an account number, a passport
#: or identity number, a medical record number, a date of birth beside a name) and
#: where; its value is masked"* -- and an excerpt is a reference to text of the
#: file. The rule that the masked value is the only text a citation may quote
#: follows the kind.
IDENTIFIER_ITEM_KIND: str = "identifier"


def _item_kind(observation) -> str:
    """`excerpt`, or `identifier` for a reading `00` amendment 7(a)'s layer produced.

    **ASKED OF THE EXTRACTOR AND NOT SPELLED HERE.** `extractors.identifiers`
    publishes `is_identifier_extractor` precisely because two consumers must agree
    about which rows those are, and its own docstring names the cost of the second
    copy: `recognition.detector._matches` skips these rows because their normalized
    value prints the KIND, so a tokeniser reading `medical_record_number ...8842`
    finds the word `record` and holds the file by the wrong rule. A prefix written
    out here would be that second copy.

    Read off `extractor_name`, which P4 records on every observation, rather than
    off the value or the zone: what makes a reading an identifier report is which
    extractor concluded it, and a reader that guessed from the text would be a
    second, worse identifier recogniser sitting inside the dossier builder.
    """
    from extractors.identifiers import is_identifier_extractor

    return (IDENTIFIER_ITEM_KIND
            if is_identifier_extractor(getattr(observation, "extractor_name", "")
                                       or "")
            else "excerpt")


def _eligibility(reason: str | None) -> str:
    """`00`:39's three states, from the recogniser's own word for where it stopped.

    `model_situation._ELIGIBILITY_BY_REASON`'s two entries, and the default is the
    third: a file the rules RECOGNISED as an ordinary schema still has an open
    question here -- whether it is a record of one of the ten -- and "remains
    ambiguous" is the truthful word for it. §18.56's four health forms carrying
    basis `detector` with `protected = 0` are exactly that file.
    """
    return (MULTIPLE_PLAUSIBLE_DOMAINS if reason == "ambiguous"
            else REMAINS_AMBIGUOUS)


def build_gate_request(
    question: GateQuestion,
    observations: Sequence, *,
    model_target,
    prompt,
    max_dossier_tokens: int,
) -> DossierRequest:
    """One file's gate question, as the reference-only request P7 decides on.

    **No text crosses this line**, on `build_situation_request`'s own terms: every
    field is a reference, and what the model is shown of the file is whatever P7
    decides to release for those observation keys, at the door.

    **TWO ITEM KINDS AND BOTH ARE THE FILE'S OWN READINGS.** An `excerpt` is a
    reference to text of the file; an `identifier` is a reading the deterministic
    identifier layer produced (`00` amendment 7(a)), whose recorded value is masked
    and whose presence is itself the report. The gate's ratified template describes
    both, and `_item_kind` reads which one this is off P4's `extractor_name` rather
    than off the value.

    **NO FRAME ITEMS**, and that is this dossier's whole shape. Site G carries one
    `candidate_schema` item per option and one `recogniser_abstention` item,
    because its options vary per file and the report is the rules aiming the
    question. Here the options do not vary and there is no aim: the ten kinds and
    what each one means are in the ratified template, byte-identical on every
    file. An item repeating them would put the constant part of the prompt into
    the per-file part of the dossier -- the opposite of `104` R-58 -- and lengthen
    the one call this product makes about every file it scans.

    `NothingToAsk` for a file with no releasable reading, on the same rule site G
    states: `00`:42's "must return unknown where support is insufficient" is about
    the MODEL's answer, and a file with nothing for it to read never gets far
    enough to be asked. It stays where the rules left it, which is local -- and at
    this site that is the safe direction by construction, because an unanswered
    gate clears nothing.
    """
    if not observations:
        raise NothingToAsk(
            f"{question.file_id} has no releasable reading, so there is nothing "
            f"for the gate to read a restricted kind out of. The file is not "
            f"cleared and is not named: it stays where the rules left it, which "
            f"is on this device.")
    return DossierRequest(
        call_site=RESTRICTED_KIND,
        subject_ref=question.file_id,
        eligibility_reason=_eligibility(question.reason),
        evidence_items=tuple(
            EvidenceItem(
                evidence_ref=observation.observation_key,
                kind=_item_kind(observation),
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
        # One file, no neighbour, no tree: this site proposes no destination and
        # retrieves nothing, so there is no competing value for the engine to have
        # recorded and no snapshot to be judged against.
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=GATE_STAGE,
            target=Target(file_ids=(question.file_id,), group_id=None),
            model_target=model_target,
            requested_items=tuple(
                Excerpt(
                    observation_key=observation.observation_key,
                    span=observation.location.text_span,
                    reason="a reading of this file the restricted kind may rest on",
                )
                for observation in observations
            ),
            prompt_template_id=prompt.template_id,
            # THE PROMPT'S OWN FINGERPRINT, never the dossier's address:
            # `transport.issue` recomputes it and refuses the release when the two
            # disagree, after P7 has already spent it.
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens,
        ),
        plan_version=None,
        evidence_snapshot_id=None,
    )


__all__ = ["GATE_STAGE", "GateQuestion", "RESTRICTED_KIND", "build_gate_request",
           "restricted_kind_vocabulary"]

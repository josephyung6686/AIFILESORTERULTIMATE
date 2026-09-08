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

WHY THIS FILE STOPS SHORT OF A CALL, and the three walls are measured, not assumed:

1. `llm_harness.vocabulary.CALL_SITES` is a closed tuple of six. Its sixth member
   carries "THE SIXTH, ADDED 2026-09-02 WITH THE OWNER'S APPROVAL, RECORDED HERE",
   so a seventh is the owner's act. `SITUATION_SENSITIVITY` below is deliberately
   NOT in it, and `build_situation_request` refuses rather than pretending.
2. `privacy.vocabulary.CLASSIFICATION_BASES` is a closed tuple of four, and a
   verdict from a model on this device is none of them. Measured:
   `ClassificationRecord(basis="local_model", ...)` raises `OutOfVocabulary`.
   Writing one as `detector` would claim a deterministic rule concluded it, which
   is the untruth `96` §19 caught when `detector_no_safety_evidence` was read as
   "I checked and it is fine". So this module writes no record.
3. The prompt is the owner's to ratify, and the dossier needs slots
   (`allowed_situations`, the matched terms, the abstention's reason) that the
   ratified A_fact template does not name. The packet holds the request.

All three are pinned by `tests/integration/test_situation_site_boundary.py`, each
failing the day it opens.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from facts.domains import SCHEMA_IDS
from llm_harness.vocabulary import CALL_SITES, G_SITUATION_SENSITIVITY
from recognition.detector import Abstention

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
    #: `no_corroboration` or `ambiguous` on the owner's corpus.
    reason: str
    #: The closed list the model may answer from, `NONE_OF_THESE` last.
    allowed_situations: tuple[str, ...]
    #: What the file matched, per candidate. A candidate the file matched nothing
    #: for is a candidate the semantic recogniser raised, and saying so is what
    #: keeps "near in vector space" from reading as "said this word".
    matched_terms: tuple[tuple[str, tuple[str, ...]], ...]
    #: The observation keys the candidates rest on, for the citation check.
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
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


def shortlist_for(abstention: Abstention,
                  semantic: object | None = None) -> tuple[str, ...]:
    """The valid options for one file, from what the recognisers actually raised.

    **The order is `SCHEMA_IDS`', not the order the candidates arrived in.** Two
    recognisers contribute and their orders are their own; a shortlist whose order
    depended on which one spoke first would be a different prompt for the same file,
    and `104` R-58 is the same argument about the dossier's bytes.

    `NONE_OF_THESE` is always last and always present. It is the only member here
    that is not a schema.

    **The semantic argument is optional and is where the biggest bucket comes
    from.** Measured on the owner's corpus: of the 112 files today's recogniser
    abstains on, 60 abstain `no_evidence` -- meaning they carry no term any schema
    authored -- so the lexical side raises NO candidate for them and this returns a
    list of one, which `SituationQuestion` refuses. Those 60 become askable only
    when the semantic recogniser's nearest and runner-up are passed in, which is
    what `--semantic-model` turns on and what makes the two mechanisms partners
    rather than alternatives.
    """
    raised: set[str] = set()
    if abstention.schema_id is not None:
        raised.add(_require_schema(abstention.schema_id))
    for schema_id in abstention.tied_schema_ids:
        raised.add(_require_schema(schema_id))
    for name in ("schema_id", "runner_up"):
        value = getattr(semantic, name, None)
        if isinstance(value, str):
            raised.add(_require_schema(value))
    for schema_id in getattr(semantic, "tied_schema_ids", ()) or ():
        if isinstance(schema_id, str):
            raised.add(_require_schema(schema_id))
    return tuple(
        schema_id for schema_id in SCHEMA_IDS if schema_id in raised
    ) + (NONE_OF_THESE,)


def question_for(abstention: Abstention, *, file_id: str, content_hash: str,
                 matched_terms: Sequence[tuple[str, Sequence[str]]] = (),
                 evidence_refs: Sequence[str] = (),
                 semantic: object | None = None) -> SituationQuestion:
    """One file's question, or `NothingToAsk`.

    Refusing is a real outcome and the common one today: a file the recognisers
    raised no candidate for has no question with valid options, and `00`:259's
    "mark the deferred stage ... rather than guessing" is what happens to it.
    """
    return SituationQuestion(
        file_id=file_id, content_hash=content_hash, reason=abstention.reason,
        allowed_situations=shortlist_for(abstention, semantic),
        matched_terms=tuple(
            (schema_id, tuple(terms)) for schema_id, terms in matched_terms),
        evidence_refs=tuple(evidence_refs),
    )


def build_situation_request(questions: Sequence[SituationQuestion]) -> None:
    """THE WALL. Refuses, and says how much is waiting behind it.

    This is where a `DossierRequest` would be built and cannot be:
    `records.DossierRequest` validates `call_site` against `CALL_SITES`, which does
    not carry this site and will not until the owner ratifies it. Raising here rather
    than building something almost-right keeps the refusal at the place a reader
    looks for it, and the count is what makes the gap a number instead of a note.
    """
    raise SituationSiteNotRatified(
        f"{len(questions)} files have a question with valid options and none can "
        f"be asked: {SITUATION_SENSITIVITY!r} is not one of the {len(CALL_SITES)} "
        f"call sites the product carries, and a seventh is the owner's act -- the "
        f"sixth records that it was 'ADDED 2026-09-02 WITH THE OWNER'S APPROVAL'. "
        f"Two more walls stand behind this one: no prompt is ratified for the site, "
        f"and a verdict from a model on this device has no lawful basis to be "
        f"written under (`CLASSIFICATION_BASES` carries four and none of them names "
        f"a model). Q-M puts all three to the owner together."
    )

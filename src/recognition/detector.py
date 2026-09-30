# src/recognition/detector.py
"""RUNTIME. The `ClassificationProducer` P7 left empty and production requires.

`src/production.py` raises `MissingClassificationAuthority` -- *"P7 has no detector
default; production cannot classify without one"* -- because nothing in `src/`
implemented `orchestrator.ClassificationProducer`. This does.

**Two steps, not one, and the seam between them is a contract.** Recognition says
which domain schema a file version's own evidence makes plausible. Classification
says which handling class it carries. They are separate here because
`planning/domains/_CONTRACT.md` rule 5 forbids the research from joining them:
*"`sensitivity` is §2.9's phrase and nothing more. Handling classes are P7's (§8.4).
A catalogue that assigns one is inventing P7's vocabulary."* So the compiled rules
carry no class, and `handling_for` is an injected authority with no default. A
schema the caller states no handling for is RECOGNISED and not classified -- an
abstention with a reason, not a guess.

**Abstention is a result.** `explain` returns a `Recognition` or an `Abstention`;
`__call__` -- the seam the orchestrator binds -- turns the second into `None`, which
`privacy.classification.resolve_class` resolves to `unreadable_unclassified`, the
correct locked door. The reason is never lost: it is on the `Abstention`, together
with the schema's `needs_llm` readings, which are the cases the research recorded as
unsettleable by a deterministic rule and which a later P8 stage would pick up.

**One arity, and it is a word rather than a number.** All 358 rows carry a
`never_alone` array and all 358 set `file_kinds.never_alone: true`. Read literally,
"never alone" is two, and `00` states the same rule positively: *"BUSIB 4300 becomes
a course fact only when the engine finds a course-code pattern together with academic
context such as 'syllabus,' 'lecture,' 'credits,' 'instructor,' or 'semester.'"* This
module holds no other number: no score, no confidence, no weight and no threshold.
A tie between two schemas is broken by nothing, because `00` requires abstention
where two readings are both supported.

**Nothing here opens a file.** The detector reads P4 observations another part
already wrote, and it checks P3's protected-container rule FIRST, before it reads
even those. A protected container is MARKED AND COUNTED, NEVER OPENED: the abstention
names the file and says why, so it is present-but-untouched with a reachable
explanation rather than an error or a silent skip.
"""
from __future__ import annotations

import json as _json
import sqlite3
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import PurePath
from types import MappingProxyType

from database_agent.files_table import get_file

from evidence_shape.location import Segment
from evidence_shape.locator import serialize_container_path
from evidence_shape.store import is_derived_extractor

#: §2.4's "language where relevant" slot, IMPORTED rather than spelled. `_matches`
#: refuses term matches from it (see there), and a detector holding its own copy of
#: an extractor's field label is a rule that stops applying the day the label is
#: renamed, silently and in the permissive direction.
from extractors.structured_text import LANGUAGE_FIELD

#: WHICH FAMILY THIS FILE BELONGS TO, read off P5's own recorded decision rather
#: than re-derived here from an extension. `route` already answered the question --
#: detected format beats declared extension, and the answer is written down -- and
#: a detector holding a second extension table is `LANGUAGE_FIELD`'s rule again:
#: the day somebody adds `.heic` to the router, a private copy here goes on
#: saying no.
from extractors.router import routing_decisions

#: `00` amendment 7(a)'s deterministic extractor, IMPORTED for the same reason
#: `LANGUAGE_FIELD` is: the kinds and the namespace are the extractor's and a
#: detector holding its own copy of either is a rule that stops applying the day one
#: is renamed. `is_identifier_extractor` is asked in two places here and they mean
#: opposite things -- `_matches` refuses these rows, `_identifier_readings` reads
#: only them -- so one predicate serving both is what keeps them exact complements.
from extractors.identifiers import (
    CHECKSUMMED_KINDS, IDENTIFIERS_NAMESPACE, KINDS as IDENTIFIER_KINDS,
    is_identifier_extractor, kind_of,
)

#: `00` amendment 7(b)'s local entity reader, imported for 7(a)'s reason exactly.
#: THE PREFIX IS THE CONTRACT AND THE LABEL SET IS THE DEPLOYMENT'S -- that module's
#: own words -- so what is imported is the namespace and the slug rule, never a
#: roster: `cli.ENTITY_LABELS` may gain a twelfth label without an edit here, and a
#: label this rule names no domain for holds nothing, which is the honest answer.
from extractors.entities import (
    ENTITY_NAMESPACE, is_entity_extractor, label_slug,
)

from facts.domains import SCHEMA_IDS, UnknownSchema

from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.classification import UnbackedClassification
from privacy.vocabulary import (
    CLASSIFICATION_BASES, DETECTOR_NO_SAFETY_EVIDENCE, OutOfVocabulary,
)
from privacy.vocabulary import check_handling_class

from scan_agent.exclusion import is_protected_container

from recognition.rules import RecognitionRules, SchemaRules
from recognition.vocabulary import SAFETY_DOMAIN_IDS, check_abstention_reason

#: §3.13's weakest ranked state, and the honest one for this detector. D11's own
#: words for what produces a `possible` fact: "free text, OCR, a filename or any
#: unlabeled position" -- which is exactly where a compiled term match lands. It
#: is deliberately the floor: `classification_store.strongest` ranks
#: `user_confirmed`, `direct` and `validated` above it, so a user correction or a
#: labelled slot always wins over a term co-occurrence and never the other way.
RELIABILITY: str = "possible"


#: A FILE WITH NO WORDS IN IT IS STILL A FILE, and if it is a picture or a
#: recording then what it is, is a capture. `00`:110 sanctions a deterministic
#: answer for "a direct, unique match", and there is no more direct or more unique
#: one than this: the whole of the released evidence is a path, a mime type and an
#: extension, and the extension says JPEG.
#:
#: **MEASURED, on the owner's corpus of 13 Sep 2026 (lead-only).** Of the 242 files
#: the cloud situation judge was asked about, 50 carried no text at all -- 35
#: images and 16 audio files. This detector returned `no_evidence` for 45 of them,
#: because `photos` sets `file_kind_never_alone` and a JPEG with no words is one
#: signal; the judge, shown a mime type and nothing else, answered "none" for 36 of
#: them, honestly -- "the released values show only a mime type". Those files then
#: got no situation and no facts, out of a question nobody could have answered.
#:
#: `file_kind_never_alone` IS UNTOUCHED AND STILL MEANS WHAT IT MEANS. It is a rule
#: about the file KIND arriving as a second signal beside a term -- a `.jpg` that
#: says "statement" must not be `finance` on the strength of being a `.jpg`. This
#: branch is reached only where there is no term and no text to hold one, so there
#: is no first signal for the kind to be second to, and nothing here loosens the
#: arity rule for any file that has words.
CAPTURE_SCHEMA: str = "photos"

#: The two families a capture comes in, in `evidence_shape.vocabulary`'s spelling.
#: P5's router is what puts a file in one of them, and this reads its answer.
CAPTURE_SOURCE_TYPES: frozenset[str] = frozenset({"image", "audio_video"})

#: THE FAMILIES A FILE WITH NO TEXT CARRIES. `filesystem` is the name, the parent
#: folder, the extension and the mime type -- P3's §1.2 record, which every file on
#: the disk has; `image` and `audio_video` are container metadata. Any OTHER family
#: in the file's evidence means something read words out of it: `ocr` is an OCR run,
#: `text_document` a PDF or a `.txt`, `archive` a manifest. A file carrying one of
#: those HAS text, and this branch must not reach it -- an opaque image whose OCR
#: returned words is exactly `00`'s case for the model rather than for a rule, and
#: it stays one.
TEXTLESS_SOURCE_TYPES: frozenset[str] = frozenset(
    {"filesystem", "image", "audio_video"})


@dataclass(frozen=True, slots=True)
class Handling:
    """One schema's handling policy: the class, the flag, and the basis.

    `protected` is SUPPLIED and never derived. SPEC §2: *"Neighbouring parts should
    consume the `protected` flag, not infer it from the class"*, and P7 Open
    question 1 -- whether `protected` is exactly the top two classes -- is unsettled.
    Deriving one from the other here would answer it in an implementation.
    """

    handling_class: str
    protected: bool
    basis: str

    def __post_init__(self) -> None:
        check_handling_class(self.handling_class)
        if self.handling_class == UNREADABLE_UNCLASSIFIED:
            raise UnbackedClassification(
                f"{UNREADABLE_UNCLASSIFIED!r} is a gate OUTCOME, not a file fact "
                "(D2). A detector that could assign it would make 'nothing has "
                "looked' and 'this file carries nothing' the same value.")
        if self.basis not in CLASSIFICATION_BASES:
            raise OutOfVocabulary(
                f"basis {self.basis!r} is not one of {CLASSIFICATION_BASES}")
        if not isinstance(self.protected, bool):
            raise UnbackedClassification(
                f"protected is §8.4's flag and is a boolean, not {self.protected!r}")


#: `00`:52, in `00`'s own order: *"Finance, identity, medical, and legal material
#: should be implemented first as safety domains, meaning the system detects and
#: protects them before any cloud or automated placement decision is allowed."* And
#: `00`:185 for the flag: such material *"should enter a protected state
#: immediately"*.
#:
#: `sensitive_personal` is this detector's own hand-authored choice and is recorded
#: as one. `00` names five handling classes and never says which one a safety domain
#: carries, so no reading of `00` supplies it; what `00` does supply is `protected`,
#: which is the half that gates behaviour -- `may_move_automatically` and the cloud
#: egress rules read the FLAG. The class is set to §8.4's third rather than its
#: fourth because `highly_sensitive_credential_bearing` is §8.4's name for
#: credential-bearing material specifically, and a term co-occurrence has not
#: established a credential. It is deliberately not the strongest available claim:
#: at `possible` reliability, a later `direct` or `user_confirmed` record supersedes
#: it. This does NOT answer P7 Open question 1: nothing here says the flag and the
#: class stand in any general relation.
SAFETY_DOMAIN_HANDLING: Mapping[str, Handling] = MappingProxyType({
    schema_id: Handling(handling_class="sensitive_personal", protected=True,
                        basis="safety_domain")
    for schema_id in SAFETY_DOMAIN_IDS
})


#: WHICH OF `00`:52'S FOUR SAFETY DOMAINS EACH IDENTIFIER KIND IS A READING OF.
#:
#: `00`, Amendments of 2026-09-11, item 7(a), the owner's ruling of 12 Sep 2026:
#: identifier patterns with checksums are a deterministic extractor "whose
#: observations hold a file exactly as an authored safety term does". This table is
#: the whole of "exactly as": a `payment_card` reading is a `finance` reading, and
#: from here on it travels the paths an authored work type already travels --
#: `_safety_readings_in_evidence`, `precaution_report`, `_protect_as` -- so the file
#: is held `sensitive_personal, protected=True, basis='safety_domain'` by the same
#: three lines of code that hold a discharge summary. No new class, no new basis and
#: no new record shape: one more READER of the rule that already exists.
#:
#: THE MAPPING IS THE RULING'S OWN SENTENCE, split into its clauses. "card numbers,
#: account and IBAN shapes" -> finance; "national-identity and passport shapes" ->
#: identity; "medical record numbers" -> medical; "a date of birth beside a name" ->
#: identity, because a birth date is what an identity document and an identity check
#: are built on and `00` gives no other of its four a claim on it.
#:
#: `legal` HAS NO KIND, and the absence is a statement rather than an oversight: no
#: numbering scheme identifies a document as legal. A will and a deposition are named
#: by their words, which is what the authored library is for, and inventing a
#: "case number" shape here would be this module authoring the research.
IDENTIFIER_SAFETY_DOMAIN: Mapping[str, str] = MappingProxyType({
    "payment_card": "finance",
    "iban": "finance",
    "bank_account": "finance",
    "us_ssn": "identity",
    "passport_number": "identity",
    "hkid": "identity",
    "date_of_birth": "identity",
    "medical_record_number": "medical",
})
#: Checked against the extractor's own roster at import, on `SAFETY_DOMAIN_IDS`' own
#: pattern: a kind added there without a domain here would be extracted, masked,
#: stored -- and silently hold nothing, which is `104` §18.56's defect wearing a new
#: shape.
for _kind in IDENTIFIER_KINDS:
    if _kind not in IDENTIFIER_SAFETY_DOMAIN:
        raise UnknownSchema(
            f"{_kind!r} is one of `extractors.identifiers.KINDS` and this table names "
            "no safety domain for it. An identifier the product extracts and then "
            "counts as nothing is the miss amendment 7(a) exists to close.")
for _kind, _schema_id in IDENTIFIER_SAFETY_DOMAIN.items():
    if _kind not in IDENTIFIER_KINDS:
        raise UnknownSchema(
            f"{_kind!r} is not a kind `extractors.identifiers` extracts; a domain for "
            "a kind that never fires is a rule with nothing to apply to")
    if _schema_id not in SAFETY_DOMAIN_IDS:
        raise UnknownSchema(
            f"{_schema_id!r} is not one of `00`:52's four safety domains "
            f"{SAFETY_DOMAIN_IDS}; 7(a) says an identifier holds a file as an "
            "authored safety term does, and only those four have such a hold")


#: `00` AMENDMENT 7(b), THE OTHER HALF, AND THE SENTENCE IS THE OWNER'S:
#:
#:     "a small local entity encoder ... names people, diagnoses, dates of birth and
#:     identity numbers as observations, AND A PERSON BESIDE A DIAGNOSIS OR AN
#:     IDENTITY NUMBER HOLDS THE FILE WITHOUT A MODEL CALL."
#:
#: Two tables, because the ruling is two rules. THIS ONE IS THE PAIR: an entity of
#: this kind holds the file only where a PERSON is beside it, and the domain is the
#: one the pair names. A diagnosis with a person is somebody's health record; a
#: diagnosis without one is a paper about a disease -- and telling those apart is the
#: same distinction the authored library gets wrong, which is how the owner's own
#: design notes for this product were once locked on the phrase "discharge summary".
#:
#: `date_of_birth` IS IDENTITY AND NOT MEDICAL, on 7(a)'s own reading: a birth date is
#: what an identity document and an identity check are built on, and `00` gives no
#: other of its four a claim on it. The two layers then agree by construction -- one
#: date is `identity` whether the pattern layer's label found it or the encoder did.
ENTITY_BESIDE_A_PERSON: Mapping[str, str] = MappingProxyType({
    "medical_condition": "medical",
    "identity_document_number": "identity",
    "passport_number": "identity",
    "date_of_birth": "identity",
})

#: AND THIS ONE IS THE NUMBER THAT NEEDS NOBODY BESIDE IT. An account number and a
#: medical record number are not things a document mentions about somebody else: they
#: are issued to a holder and printed on that holder's own paper, so the number is
#: already about a person. They are also exactly the two kinds 7(a)'s pattern layer
#: holds a file on alone (`IDENTIFIER_SAFETY_DOMAIN`'s `bank_account` and
#: `medical_record_number`), and the two layers answering differently about one
#: number would be one rule with two homes.
ENTITY_ALONE: Mapping[str, str] = MappingProxyType({
    "account_number": "finance",
    "medical_record_number": "medical",
})

#: The kind whose presence turns the first table on. Spelled once.
PERSON_ENTITY: str = "person"
MEDICAL_CONDITION_ENTITY: str = "medical_condition"

#: A PERSON ALONE, AN ORGANISATION ALONE, AN EMAIL OR A PHONE ALONE HOLD NOTHING, and
#: their absence from both tables is the whole of how that is said. It is not an
#: omission to be tidied up later: every document a person owns names somebody, most
#: name an organisation, and a corpus where a name is a lock is a corpus with no
#: unlocked files in it -- the over-protection collapse `_precaution` records,
#: reached by the commonest entity there is. 7(b)'s sentence is about a person BESIDE
#: something, and the something is what carries the claim.
for _slug in (*ENTITY_BESIDE_A_PERSON, *ENTITY_ALONE, PERSON_ENTITY):
    if label_slug(_slug) != _slug:
        raise UnknownSchema(
            f"{_slug!r} is not the slug `extractors.entities` would write for any "
            "label, so no reading can ever carry it and this rule can never fire. "
            "The naming rule is that module's; this table only spells its answers.")
for _slug, _schema_id in (*ENTITY_BESIDE_A_PERSON.items(), *ENTITY_ALONE.items()):
    if _schema_id not in SAFETY_DOMAIN_IDS:
        raise UnknownSchema(
            f"{_schema_id!r} is not one of `00`:52's four safety domains "
            f"{SAFETY_DOMAIN_IDS}; 7(b) holds a file the way 7(a) does and the way "
            "an authored term does, and only those four have such a hold")


#: WHERE A DOCUMENT NAMES ITSELF. SPEC 2.2 ranks "a filename, title, or page-one
#: heading" as meaningful evidence, and `_matches` already quotes that ranking for a
#: different purpose. These are those three, plus the one that is one of them under
#: another name: `header_footer` is a running head -- a page-one heading, on page two.
#:
#: `metadata` USED TO BE HERE, on the claim that it is "the format's own title slot,
#: a document naming itself in its own words". That claim was false, and P4 is what
#: makes it false: `extractors/pdf.py`:135 routes a slot to `zone="title"` when it IS
#: a title slot and to `metadata` otherwise, so `metadata` is by construction
#: everything that is NOT the document naming itself. Measured over the owner's real
#: corpora, what lands there is `extension`, `mime_type`, `language`, `Producer`,
#: `CreationDate`, `ModDate`, `Creator`, `format`, `pixel dimensions` and `Trapped` --
#: the format talking about itself and about the software that wrote it.
#:
#: It cost accuracy rather than tidiness. `HW 9.pdf`'s ONLY authored term is
#: `retail_hospitality:build`, out of
#: `Producer = 'iOS Version 18.5 (Build 22F76) Quartz PDFContext'`, and it sat in a
#: zone asserting that a physics homework had named itself that. Nothing is lost by
#: removing it: `title` is already here and is P4's own zone for the real thing.
#:
#: `body`, `table`, `ocr`, `notes`, `annotation` and `reference_list` are deliberately
#: absent for the same reason. They are where a document mentions OTHER documents, and
#: the whole of this constant's job is to keep a mention from becoming a claim.
NAMING_ZONES: frozenset[str] = frozenset(
    {"filename", "title", "heading", "header_footer"})

#: SPEC 2.2's phrase is "page-ONE heading", and the page is the half that does the
#: work on a long document. `pdf.text` calls a line a heading when its type is
#: larger than the page's body size, which is a typographic guess and not a semantic
#: one: measured on a real corpus, `rp2040-datasheet.pdf` was locked
#: `sensitive_personal` on a page-2 "heading" reading "The next attempt to claim the
#: l...", and a World History textbook on "dispensation. Are you ready to receive
#: it? Will you". Both are body prose that happens to be set large.
#:
#: `Statement.pdf`'s heading -- "Statement of assets as of 09.01.2025" -- is on page
#: one, which is what the phrase is for.
FIRST_PAGE: int = 1


def _names_the_file(match: "TermMatch") -> bool:
    """Is this match somewhere the document NAMES ITSELF, in SPEC 2.2's sense?

    A page of `None` passes. That is not a missing page, it is a format that does
    not paginate -- a `.docx` heading and a filename both have no page, and reading
    absence as failure would quietly stop protecting every unpaginated format.
    """
    if match.zone not in NAMING_ZONES:
        return False
    return match.page is None or match.page == FIRST_PAGE


def _reported(schema_id: str, found: "tuple[TermMatch, ...]") -> "Precaution":
    """`Precaution`'s three fields, projected from the matches a writer held.

    ONE PROJECTION FOR EVERY WRITER (`104` §18.26 gap 24b). Three arms of this
    detector hold a file and each of them now says why; the arithmetic that turns
    matches into terms and zones is the same arithmetic for all three, and three
    copies of "found-order, deduplicated, a zoneless match contributes nothing"
    is how one of them would come to report a zone called "none".

    Nothing here reads the file: `found` is already the writer's own matches,
    narrowed by the writer's own rule.
    """
    return Precaution(
        schema_id=schema_id,
        terms=tuple(dict.fromkeys(match.term for match in found)),
        zones=tuple(dict.fromkeys(match.zone for match in found
                                  if match.zone is not None)),
        evidence_refs=tuple(dict.fromkeys(match.observation_key
                                          for match in found)))


@dataclass(frozen=True, slots=True)
class TermMatch:
    """One authored term, found in one observation, owned by one schema."""

    schema_id: str
    term: str
    observation_key: str
    #: P4's zone for the observation this term was found in. Recognition does not
    #: read it -- a term is a term wherever it sits, and narrowing THAT would
    #: narrow what the detector can recognise at all. Protection reads it, because
    #: protection is a claim about what the file IS. See `NAMING_ZONES`.
    zone: str | None = None
    #: Which page the observation sits on, from `container_path`'s `page` entry.
    #: `None` for a format that does not paginate -- a `.docx` heading is still a
    #: heading -- and for zones that have no page, like a filename.
    page: int | None = None
    #: Is this term the WHOLE observation, rather than a word inside it? Recorded
    #: where the text already is, so the corroboration gate never re-reads an
    #: observation to ask what it says. The gate is the only reader: an
    #: observation that is nothing but an authored term may not second the schema
    #: that term already named, because that is one signal read twice.
    whole: bool = False


@dataclass(frozen=True, slots=True)
class Precaution:
    """WHAT THE RULES THOUGHT WHEN THEY HELD A FILE, in the rules' own words.

    `104` §18 gap 24. `_precaution` marks a file `sensitive_personal,
    protected=True, basis='safety_domain'` and the record that reaches the store
    carries the CLASS and the observation keys -- not which safety domain was
    read, not which of its work types was found, and not where. Measured on r19:
    16 marks, 5 of them on hand-labelled protected files and 11 on ordinary ones,
    the false ones fired by `will`, `statement`, `receipt`, `consent form`,
    `medical record`, `visa`, `credit card` and `endorsement` in BODY prose. A
    person reading the report, and a model asked to judge the same file, could
    see the hold and not one word of the reason for it.

    So the reason is projected, and it is a PROJECTION of the matches
    `_precaution` already had in hand -- nothing here reads the file a second
    time and nothing here is a new rule. `_protect_as` produces the RECORD; this
    produces the REPORT, and they are computed from the one set of matches so
    the two can never say different things about the same file.

    `zones` is P4's own zone per match, deduplicated in the order the terms were
    found. It is REPORTED and never TESTED: `_names_the_file` is the winning
    schema branch's rule and applying it here was measured on r19 as dropping 7
    of the 11 false marks AND 2 of the 5 true ones (see `_precaution`, which
    records why the precaution deliberately skips that test). Saying where the
    term sits is what lets the local model weigh it; deciding on it here is what
    the measurement forbids.
    """

    #: The safety domain the file was held as -- `_protect_as`'s own choice, in
    #: `SCHEMA_IDS` order, so a file with two safety readings reports the one it
    #: was actually classified under rather than whichever was found first.
    schema_id: str
    #: The WORK TYPES of that domain the file's evidence carries, found-order,
    #: deduplicated. Never its context terms: `_safety_readings_in_evidence` is
    #: what refuses those and this reads its answer rather than a wider one.
    #:
    #: AND, SINCE `00` AMENDMENT 7(a), THE IDENTIFIER KINDS -- `payment_card`,
    #: `hkid`, `medical_record_number`. They stand here because the ruling puts them
    #: here: an identifier's observations hold a file "exactly as an authored safety
    #: term does", so what raised the hold is what this field reports, whichever of
    #: the two it was. A kind is distinguishable from a work type by being one of
    #: `extractors.identifiers.KINDS`, so a screen that wants to say "a card number"
    #: rather than "a discharge summary" can, without this field growing a second
    #: shape.
    terms: tuple[str, ...]
    #: P4's zone for each of those matches, found-order, deduplicated. A zoneless
    #: match contributes nothing rather than a placeholder -- an absent zone is a
    #: format that does not zone, not a zone called "none".
    zones: tuple[str, ...]
    #: THE OBSERVATIONS THOSE TERMS WERE FOUND IN (`104` §18.27, the owed row).
    #: Every `TermMatch` already knows its `observation_key`, so this is the same
    #: projection as `terms` one field along and reads the file no more than that
    #: one does.
    #:
    #: It exists because the hold's own citations are what G's row must carry when
    #: the local model CONFIRMS the hold. Until now that row cited
    #: `question.evidence_refs` -- which on a recognised file are the
    #: `Recognition`'s keys, the ordinary schema's evidence -- so a passport
    #: confirmed as an identity document was filed protected on the observations
    #: that made it look like coursework. A record cites what raised IT (§8.4),
    #: and what raised a confirmed hold is the hold.
    #:
    #: Empty exactly where `terms` is empty: a safety domain that won outright on
    #: its context terms alone names no work type, so it has no observation of its
    #: own to cite, and `104` §18.26 gap 24b's own reading applies -- there the
    #: hold IS the recognition and the recognition's citations are the hold's.
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Recognition:
    """One schema this file version's own evidence makes plausible."""

    schema_id: str
    matches: tuple[TermMatch, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Abstention:
    """A RESULT. The detector looked and declined, and this says why.

    `deferred_readings` carries the near-miss schema's `recognition.needs_llm`
    entries verbatim. They are not implemented anywhere and this is the whole of
    their wiring: the reason a deterministic rule could not settle the case,
    attached to the case it could not settle, for P8 to pick up.

    **`matched_terms` AND `evidence_refs` ARE R-166's, AND THEY ARE WHAT MAKES THE
    CASE ASKABLE.** `00`:39 gives the model a file that "remains ambiguous" or has
    "multiple plausible domains", and `00`:42 requires it to cite: *"A model that
    cannot cite sufficient evidence must return unknown."* Until now an abstention
    named the readings and not one observation behind them, so nothing downstream
    could put the question with a citation that resolves. Two readers were already
    reaching for these and finding nothing:

    * `model_situation.question_for` takes `matched_terms` and `evidence_refs` as
      arguments the CALLER must supply, because the outcome carried neither.
    * `questions.triggers.tied_readings_and_the_files_they_reach` reads
      `getattr(outcome, "evidence_refs", ())` and, finding none, cites the string
      `subject:<value>` instead -- its own comment says "an abstention carries no
      evidence refs of its own".

    Nothing here is a new observation and nothing is re-read: both fields are the
    matches `_decide` already had in hand, projected. `_protect_as`'s rule is
    unchanged and is a different rule -- a PROTECTION cites what raised it and
    re-runs `_matches` for the safety domain's own terms; this is a RECOGNITION
    saying what its readings rest on.

    Order is `SCHEMA_IDS`', not match order, for `shortlist_for`'s reason: the same
    file must put the same question however the matches arrived.
    """

    reason: str
    schema_id: str | None
    detail: str
    tied_schema_ids: tuple[str, ...] = ()
    deferred_readings: tuple[str, ...] = ()
    #: `(schema_id, terms)` for each reading this abstention names, in `SCHEMA_IDS`
    #: order, terms in the order they were found. What the file matched, per
    #: candidate -- which is what keeps "this schema was a leader" from having to be
    #: taken on trust.
    matched_terms: tuple[tuple[str, tuple[str, ...]], ...] = ()
    #: The observation keys those terms sit in, deduplicated, first occurrence
    #: first. A `Recognition` already carries this field under this name and these
    #: are the same keys, so a consumer that reads one reads the other.
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_abstention_reason(self.reason)
        if self.schema_id is not None and self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(self.schema_id)


def _named(cited: tuple[tuple[tuple[str, tuple[str, ...]], ...], tuple[str, ...]]
           ) -> dict[str, object]:
    """`_cited`'s pair as the two keyword arguments `Abstention` takes.

    Spelled once because four abstention sites pass it and a positional pair would
    be two fields whose order a reader has to remember at each of them.
    """
    matched_terms, evidence_refs = cited
    return {"matched_terms": matched_terms, "evidence_refs": evidence_refs}


@dataclass(frozen=True, slots=True)
class SituationOutcome:
    """WHERE A RECOGNISER GOT TO on one file, in the ONE shape site G reads.

    **`104` §18.26's owed row.** Two recognisers can answer about a file and until
    now they answered in two vocabularies. The term detector returns an
    `Abstention` or a `Recognition`; under `--semantic-model` the composed
    recogniser's `explain` returns a `SemanticAbstention` or a `SemanticProposal`,
    and `cli.ask_the_situation` tested for the first pair -- so on every run with
    the weights named, every file failed both tests, was counted `settled`, and
    site G asked nothing at all. The screen said the rules had settled 199 files
    they had settled nothing about.

    The fix is not a third test in the pass. A pass that names the record classes
    it will accept is a pass that must be edited every time a recogniser is added,
    and the edit that is forgotten is the one that silently turns a site off. So
    both recognisers project their own answer into this, and the pass reads this
    and nothing else.

    **`by_the_rules` IS WHY THIS IS A RECORD AND NOT A PROTOCOL.** The hold has
    exactly one author -- `Detector._precaution` and the two recognition arms
    beside it -- and `Detector.precaution_report` answers about the record that
    author wrote. Handing it a projection, or a semantic answer, would be a
    wrapper answering for a decision it is not allowed to make; handing it a
    synthesised `Abstention` whose `tied_schema_ids` carried semantic candidates
    would let a vector's nearest neighbour raise one of `00`'s four safety
    domains. So the term detector's own outcome rides here untouched, and it is
    what the hold is read off.

    Nothing in this record is authored: the schema ids are the library's, the
    terms are what the file's own evidence matched, and the reason is the
    recogniser's own word for why it could not settle the case.
    """

    #: The TERM DETECTOR's own answer about this file, always present and never a
    #: projection: the composed recogniser runs it first and carries it here. It
    #: is what `Detector.precaution_report` is asked about, and the only thing
    #: that may be.
    by_the_rules: "Abstention | Recognition"
    #: The recogniser's own reason for stopping, or `None` because it did not stop
    #: -- exactly one of this and `recognised`, on `SituationQuestion`'s own
    #: invariant, because a recogniser either named the file or said why it could
    #: not and there is no third thing it can have done.
    reason: str | None
    #: The schema this file was recognised as, or `None` because it was not. On
    #: the composed path this is the term detector's recognition where it made
    #: one and the semantic proposal where the rules abstained -- which is
    #: `SemanticRecogniser.__call__`'s own order of speaking, in the shape the
    #: question is put rather than the shape the record is written.
    recognised: str | None
    #: EVERY SCHEMA A RECOGNISER RAISED for this file: the tied leaders, the near
    #: miss, the nearest and the runner-up. Not a shortlist yet --
    #: `model_situation.shortlist_for` adds the held domain and the decline and
    #: puts them in `SCHEMA_IDS` order, because a question's options are that
    #: module's to shape and a recogniser's candidates are this one's to raise.
    candidates: tuple[str, ...] = ()
    #: `(schema_id, terms)` per candidate, in `SCHEMA_IDS` order. A candidate with
    #: an EMPTY term tuple is one no term raised -- the semantic recogniser's
    #: nearest neighbour -- and saying so is what keeps "near in vector space"
    #: from reaching the model as "said this word".
    matched_terms: tuple[tuple[str, tuple[str, ...]], ...] = ()
    #: The observation keys the candidates rest on. `00`:42 requires the answer to
    #: cite, and `privacy.classification` refuses a `local_model_situation` record
    #: that carries none, so a candidate raised from nothing citable is a question
    #: whose answer could not be written down.
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.by_the_rules, (Abstention, Recognition)):
            raise TypeError(
                "by_the_rules is the TERM detector's own outcome and nothing "
                f"else; {self.by_the_rules!r} is not an Abstention or a "
                "Recognition, and `precaution_report` may only be asked about "
                "the record its own author wrote")
        if (self.reason is None) == (self.recognised is None):
            raise ValueError(
                "a recogniser states why it stopped or the schema it recognised, "
                f"and exactly one of them: reason={self.reason!r}, "
                f"recognised={self.recognised!r}")
        for schema_id in (*self.candidates,
                          *(() if self.recognised is None else (self.recognised,))):
            if schema_id not in SCHEMA_IDS:
                raise UnknownSchema(schema_id)


def situation_outcome_of(outcome: "Abstention | Recognition") -> SituationOutcome:
    """The term detector's own answer, projected into the shape site G reads.

    THE PROJECTION IS PUBLIC because two callers need the same one: this
    detector's `situation_outcome`, and `SemanticRecogniser`'s, which starts from
    it and speaks only where the rules stopped. A second copy would be a second
    answer to "what did the rules raise for this file", which is the shape
    `precaution_report` was split out to avoid one paragraph up.

    A RECOGNITION RAISES ITSELF AND NOTHING ELSE, and it carries no matched terms.
    That is `00`:110 read literally: the rules made a direct, unique match, so
    what would be reported is not a list of things the file might be. Its
    `evidence_refs` are its own -- what the recognition rests on -- which is what
    the pass has always passed on for such a file.
    """
    if isinstance(outcome, Recognition):
        return SituationOutcome(
            by_the_rules=outcome, reason=None, recognised=outcome.schema_id,
            candidates=(outcome.schema_id,),
            evidence_refs=outcome.evidence_refs)
    return SituationOutcome(
        by_the_rules=outcome, reason=outcome.reason, recognised=None,
        candidates=tuple(
            schema_id for schema_id
            in (outcome.schema_id, *outcome.tied_schema_ids)
            if schema_id is not None),
        matched_terms=outcome.matched_terms,
        evidence_refs=outcome.evidence_refs)


def settled_by_file_kind(outcome: "Abstention | Recognition") -> bool:
    """Was this recognition made on the file's KIND alone, with no term at all?

    THE PREDICATE LIVES HERE BECAUSE THE RULE DOES. `cli.ask_the_situation` needs
    to tell a capture apart from a file the rules read words in, and the honest
    way to ask is to ask the part that decided. The alternative -- site G looking
    at zones and concluding for itself -- is a second recogniser in the caller,
    which is what `SituationOutcome` exists to stop.

    A term recognition always carries at least two matches: that is
    `file_kind_never_alone`'s arity, applied in `_decide` and never relaxed. So an
    empty `matches` on a `Recognition` is this branch and no other, and the test
    is the record rather than a flag beside it.
    """
    return isinstance(outcome, Recognition) and not outcome.matches


def _tokens(text: str) -> tuple[str, ...]:
    """Words, case-folded. Everything that is not a letter or digit separates.

    Not a regex: `str.isalnum` over code points is the same rule stated in the one
    place it is applied, and P7's own package is forbidden from importing `re` for
    exactly the reason that a pattern is a detection rule wearing a library's face.
    Applied to the rule side at compile time and to the evidence side here, so
    `problem set` and `Problem  Set,` are one term and one match.

    **ONE EXCEPTION TO "identically", ADDED 2026-09-05.** The run boundary below is
    EVIDENCE-SIDE ONLY, and not by choice: `recognition/compile.py` casefolds every
    authored term, so the manifest holds `hkid` and never `HKID` and no authored
    term can reach the boundary at all. Nothing is lost by that -- the authored
    terms are lowercase prose phrases, and the boundary exists to make a filename
    read like one of them -- but the sentence above used to say "identically" with
    no qualification, and it would now be untrue.
    """
    out: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            out.append("".join(current).casefold())
            current.clear()

    previous = ""
    for character in text:
        if not character.isalnum():
            flush()
            previous = ""
            continue
        # A RUN BOUNDARY INSIDE ONE ALPHANUMERIC SPAN: lower-or-digit followed by
        # an uppercase letter. `DisplayMedicalRecord` is three words a person reads
        # as three words, and on a file whose bytes carry nothing the filename is
        # the whole of the evidence. Measured case: `DisplayMedicalRecord.pdf` is a
        # 672-byte macOS Finder alias -- no document inside it, so no extractor can
        # ever help -- and it is one of the eight protected files in the ground
        # truth. Under the old rule its name was one token matching nothing, and
        # the product called the owner's medical record ordinary.
        #
        # AN ALL-CAPS RUN IS NOT SPLIT, and that is the half that has to hold.
        # `HKID` must stay one token or `identity`'s `hkid` term stops matching
        # `2025209423_Joseph_Yung_HKID.pdf` and a national identity card goes back
        # to `personal_non_sensitive, protected=0`. So this is only the
        # CONSERVATIVE half: `PDFReader` stays whole, because separating an acronym
        # from the word after it needs a rule about where an uppercase RUN ends,
        # and that rule is deliberately absent.
        #
        # WHAT IT COSTS, recorded here rather than discovered later. More tokens
        # mean more phrase candidates, and `never_alone` turns a second match into
        # an activated schema. `CB_OrderReceipt.pdf` now reads `cb order receipt`,
        # putting `receipt` -- a `finance` work type that is also ordinary English
        # -- into a naming zone. Over the 215-file corpus that cost nothing: the
        # over-marked SET was byte-identical, diffed file by file rather than
        # compared by count, and SORTING did not move. On a corpus with more
        # CamelCase filenames it could; `test_recognition_tokeniser.py` pins the
        # case so a future regression has a test to point at.
        if current and character.isupper() and (
                previous.islower() or previous.isdigit()):
            flush()
        current.append(character)
        previous = character
    flush()
    return tuple(out)


class Detector:
    """The compiled rules, applied to one file version's own P4 observations."""

    def __init__(self, rules: RecognitionRules, *,
                 handling_for: Mapping[str, Handling],
                 now: Callable[[], str],
                 is_protected: Callable[[PurePath], bool] | None = None,
                 corroborating_observations: Callable[
                     [sqlite3.Connection, str, str], Iterable[str]] | None = None,
                 settled_by_user: Callable[[], Iterable[str]] | None = None,
                 declared_lives: Callable[[], Iterable[str]] | None = None,
                 topic_condition_mentions: int | None = None
                 ) -> None:
        if not isinstance(rules, RecognitionRules):
            raise TypeError(
                "the compiled rule set is `recognition.rules.load_rules`'s output; "
                "this class does not locate, parse or default one")
        if not callable(now):
            raise TypeError("the clock is injected; §8.2 preserves an observed_at")
        for schema_id, handling in dict(handling_for).items():
            if schema_id not in SCHEMA_IDS:
                raise UnknownSchema(
                    f"the handling policy names {schema_id!r}, which is not one of "
                    f"the {len(SCHEMA_IDS)} schemas the product recognises")
            if not isinstance(handling, Handling):
                raise TypeError(f"{schema_id!r} maps to {handling!r}, not a Handling")
        self._rules = rules
        self._handling = dict(handling_for)
        self._now = now
        self._is_protected = is_protected
        #: WHICH of this file's observations are structured identifiers. Injected,
        #: because the DEPLOYMENT owns the patterns -- P5's SPEC puts them in its
        #: Deferred table and `src/recognition/` ships none -- and `SchemaRules`
        #: has no pattern field at all. Absent means "this deployment finds none",
        #: which is not the same as "none are present" and behaves exactly as
        #: before.
        self._corroborating = corroborating_observations
        #: Schemas the PERSON has confirmed, through P15's structural questions.
        #: Injected for the same reason everything else here is: P15 is another
        #: part's record and this module does not read another part's tables.
        #: Absent means "nobody has been asked", which is not "nobody agreed".
        self._settled_by_user = settled_by_user
        #: Schemas the person has declared as the lives this folder is about.
        #: Injected, like `settled_by_user`, because the profile is another part's
        #: record. Absent, and an empty set, both mean "no profile": the catalogue
        #: decides as it does today. A non-empty set is a closed allow-list. It is
        #: not a weight and it is not `settled_by_user`, which only breaks a tie
        #: among leaders the file already named.
        self._declared_lives = declared_lives
        self._topic_condition_mentions = topic_condition_mentions
        # term -> the schemas that authored it, in SCHEMA_IDS order. A term two
        # schemas authored discriminates between neither: both score it, they tie,
        # and a tie abstains. That is why no cross-schema weight is needed.
        #
        # Keyed by TOKEN TUPLE, with every proper prefix recorded beside it. The
        # phrase scan then extends a candidate only while some authored term still
        # begins that way, so the cost is the length of the longest phrase actually
        # present in the file rather than the length of the longest term in the
        # vocabulary. That distinction is not academic here: 1,616 of the 9,647
        # authored entries are six words or longer and 32 are twenty or longer,
        # because several rows used `work_types` and `proposed_context_terms` as a
        # notes field -- one `government` entry is a 77-word editorial aside. They
        # compile, they can never match, and with a fixed window they would have
        # widened every scan in the corpus by a factor of eighty for nothing.
        index: dict[tuple[str, ...], list[str]] = {}
        for schema_id in SCHEMA_IDS:
            schema = rules.schemas.get(schema_id)
            if schema is None:
                continue
            for term in schema.terms:
                tokens = _tokens(term)
                if not tokens:
                    continue
                index.setdefault(tokens, []).append(schema_id)
        self._index = {tokens: tuple(owners) for tokens, owners in index.items()}
        #: Authored work-type terms IN THE TOKENISER'S OWN SPELLING, per schema.
        #: `_tokens` "separates on everything that is not a letter or digit", and a
        #: `TermMatch.term` is already tokenised -- so comparing one against the raw
        #: authored strings tests `'after visit summary'` for membership of a list
        #: holding `'after-visit summary'` and answers no. Measured over the shipped
        #: library, 159 of 470 safety work-type spellings could never match, and a
        #: plaintext password-manager export ('password-manager export') reached the
        #: end of a run with no classification row at all. Built once here rather
        #: than per match, which also stops a 270-entry linear scan per term.
        self._work_types = {
            schema_id: frozenset(" ".join(_tokens(term))
                                 for term in schema.work_type_terms)
            for schema_id, schema in rules.schemas.items()}
        self._prefixes = {tokens[:length] for tokens in self._index
                          for length in range(1, len(tokens))}

    # --- reading -------------------------------------------------------------

    def _matches(self, conn: sqlite3.Connection, file_id: str,
                 content_hash: str) -> tuple[list[TermMatch], set[str]]:
        """Every authored term this file version's live observations carry.

        Reads `raw_value` and `normalized_value` -- the values P4 stores on the
        observation itself. It binds none of P4's text materialisers: a detector
        that pulled whole text units would be a second materialisation locus, which
        `tests/p7/test_p7_no_invention.py` guards repo-wide.

        **The absolute path is not one of the file's own words.** P4's `path`
        locator holds the whole ancestor chain, so without this every word of
        every directory above a file is evidence about it -- and two words in one
        folder name are two terms, which is `never_alone`'s arity. Measured
        against the shipped manifest: `IMG_4471.jpg`, an ordinary photograph
        carrying no evidence whatever of its own, sitting in a folder called
        `Passport and Visa Documents`, was recognised as `identity` and stored
        `sensitive_personal, protected=True`. Nothing about the photograph
        decided that, and every file in that folder got the same answer.

        Two narrower forms of this rule were already here and each was found the
        same way -- by running the product. Corroboration refused a path term
        because "every file on a disk sits under some words, and none of them are
        the file's own"; precaution refused one because a corpus under a folder
        called `Passport` protected a syllabus. Both left the sentence they share
        stated twice and applied nowhere else, and the door they did not cover is
        the one where a schema WINS. It is the same rule, so it is now read once,
        here, where the observations are.

        SPEC 2.2 ranks "a filename, title, or page-one heading" as meaningful
        evidence and says nothing about the machine's directory chain, so the
        file's own name is untouched.
        """
        found: list[TermMatch] = []
        source_types: set[str] = set()
        #: (schema, term) -> where its ONE match sits in `found`. An index rather
        #: than a set, because a later occurrence in a naming zone replaces an
        #: earlier one outside the naming zones -- see the replacement below.
        seen: dict[tuple[str, str], int] = {}
        for row in conn.execute(
                "SELECT observation_key, raw_value, normalized_value, source_type, "
                "location, extractor_name FROM evidence WHERE file_id = ? "
                "AND content_hash = ? AND superseded_by IS NULL ORDER BY rowid",
                (file_id, content_hash)):
            # `104` R-135: a DERIVED reading is an addressable copy of this file's own
            # words, minted so a model can CITE the line a course code sits on and so
            # another file's dossier can carry it as context. It is not a second thing
            # the file says about itself. `evidence_shape.store.is_derived_extractor`
            # is the one predicate, P4's, and it reads a namespace rather than a list,
            # so a producer written later opts in by naming itself.
            #
            # Measured: with the mint recording and without this, a course notebook
            # stopped being recognised as `code` and became `academic` -- the minted
            # line carries the course's NAME, which the code reading it was cut around
            # does not, so words that were never evidence about the notebook became
            # evidence about it.
            if is_derived_extractor(row["extractor_name"]):
                continue
            # AND A MASKED IDENTIFIER READING IS NOT A WORD THE FILE SAID EITHER
            # (`00` amendment 7(a)). These rows are read as safety readings in their
            # own right by `_identifier_readings`, and they must not ALSO arrive
            # here: their `normalized_value` prints the kind, so a tokeniser reading
            # `medical_record_number …8842` finds `record`, and `payment_card …4242`
            # would corroborate `finance` as though the document had used the word.
            # The file would then be held by the wrong rule and cite the wrong
            # evidence -- the exact shape `_safety_readings_in_evidence` was narrowed
            # to stop when `credit`, out of "credit hours", locked two syllabi. The
            # predicate is the extractor's own, on `is_derived_extractor`'s pattern.
            if is_identifier_extractor(row["extractor_name"]):
                continue
            # AND NEITHER IS AN ENTITY READING (`00` amendment 7(b)), for `104`
            # R-135's reason rather than for the line above's. An entity reading of
            # a named thing IS the document's own characters -- that is its contract
            # -- but it is a SECOND ADDRESS for text the host reading already
            # carries, cut out of it so the encoder's finding can be cited. Counting
            # both is counting one word twice, and `never_alone`'s arity is a count:
            # a file whose only academic word is inside a person's name would reach
            # two on one occurrence of it. It is the same sentence the derived
            # refusal above makes -- "not a second thing the file says about itself"
            # -- and `_entity_readings` is where these rows are read for what they
            # ARE, which is a pair the encoder found rather than a word an author
            # wrote.
            if is_entity_extractor(row["extractor_name"]):
                continue
            # The file KIND is a property of the file and not of the observation
            # that named it, so this is read before the refusal below: narrowing
            # which words count must not narrow `file_kind_plausible` as well.
            source_types.add(row["source_type"])
            where = _json.loads(row["location"])
            if where.get("locator") == "path":
                continue
            # AND THE NAME OF THE FILE'S FORMAT IS NOT ONE OF ITS WORDS EITHER.
            # `extractors.structured_text` emits the reader's `document.language`
            # -- §2.4's "language where relevant" -- as an observation of its own,
            # and for a notebook the reader fills it with `Jupyter notebook`. The
            # `code` schema ships `notebook` as a WORK TYPE, so every `.ipynb` in
            # existence carried a `code` term before one word of it was read.
            #
            # Measured on 2026-09-08 at `5ff35c0` and identically at `8eb41e0`: a
            # notebook whose entire content is the line `PYTHON 1006 Spring 2026`,
            # with an empty code cell and no prose, came back `Recognition(code)`.
            # Its only authored term was this observation; its second signal was
            # the corroboration gate seconding it with `PYTHON 1006` and
            # `Spring 2026`, which are evidence of COURSEWORK. The four
            # `Python 1006` notebooks of the owner's corpus -- the only files that
            # run placed -- were placed on that arithmetic.
            #
            # IT IS THE SAME RULE AS THE LINE ABOVE, and the same rule as
            # `_decide`'s. The path refusal is "every file on a disk sits under
            # some words, and none of them are the file's own"; every file on a
            # disk is also written in some FORMAT, and the format's name is the
            # reader's word rather than the document's. `_decide` already holds
            # that `file_kind_plausible` "is a constraint and never a signal", and
            # a term match on this slot is precisely the kind arriving as a
            # signal -- while the kind is still doing its constraining job, from
            # `source_types` gathered two lines above and from the extension.
            #
            # NARROW ON PURPOSE. §2.4's four STRUCTURAL MARKERS -- repository
            # markers, package manifests, notebook metadata, README files -- sit
            # in the same zone and are left alone: `00` asks code to "rely heavily
            # on local structural evidence, including repository roots and package
            # files", so those are evidence the design wants. None of them matches
            # an authored term today, and
            # `tests/recognition/test_recognition_serialisation_is_not_evidence.py`
            # fails the day one does, which is when this rule needs widening
            # rather than now.
            if where.get("locator") == f"metadata:field={LANGUAGE_FIELD}":
                continue
            key = row["observation_key"]
            zone = where.get("zone")
            page = next((step.get("index")
                         for step in where.get("container_path") or ()
                         if step.get("kind") == "page"), None)
            for text in (row["raw_value"], row["normalized_value"]):
                if not text:
                    continue
                observation_tokens = _tokens(text)
                for term, owners in self._terms_in(text):
                    # Is the term the WHOLE observation? `_terms_in` yields the
                    # tokeniser's own spelling, so this is a tuple comparison and
                    # never a second parse of the text.
                    whole = observation_tokens == tuple(term.split(" "))
                    for schema_id in owners:
                        match = TermMatch(schema_id=schema_id, term=term,
                                          observation_key=key, zone=zone,
                                          page=page, whole=whole)
                        at = seen.get((schema_id, term))
                        if at is None:
                            seen[(schema_id, term)] = len(found)
                            found.append(match)
                        elif (_names_the_file(match)
                              and not _names_the_file(found[at])):
                            # THE SAME TERM IN TWO PLACES IS STILL ONE TERM, and
                            # the arity rule is untouched by this -- what changes
                            # is WHICH occurrence the one match records. The
                            # first-wins rule kept whichever observation `rowid`
                            # happened to reach first, and P4 writes a body before
                            # a heading: a brokerage statement whose page-one
                            # heading reads "Statement of assets" and whose prose
                            # also says "statement" was filed at the BODY, so
                            # `_safety_readings_naming_the_file` found nothing in a
                            # naming zone and let the file go. Protection must not
                            # depend on the order P4 wrote its rows in, and adding
                            # ordinary prose to a file must not unprotect it.
                            found[at] = match
        return found, source_types

    def _terms_in(self, text: str) -> Iterable[tuple[str, tuple[str, ...]]]:
        """Authored terms present in this text as whole-word phrases.

        A SHORTER TERM INSIDE A LONGER ONE IS STILL YIELDED, and the attempt to
        suppress it was reverted after measurement. `personal statement` is
        `college_applications`' work type and `statement` is `finance`'s, so the
        owner's own `Chinese University Personal Statement.pdf` is sealed
        `sensitive_personal` -- a real over-protection, recorded in
        `planning/96`. Refusing the covered term fixes it and cannot be told from
        the case that breaks protection, because the difference is semantic:

          * `personal statement` is a DIFFERENT THING that contains the word.
          * `last will and testament` and `living will` are SPECIES of `will`, and
            both are authored as context terms, so suppressing `will` inside them
            releases a real will named by its own filename.

        Enumerated over the shipped library, 210 (safety work type, covering term)
        pairs leave no safety work type standing. Among them `financial statement`,
        `pay statement`, `earnings statement` and `statement period` cover
        `finance:statement`; `commercial invoice` and `invoice to` cover `invoice`;
        `photographed receipt or slip` covers `receipt`; and `government`'s
        passport, visa and driver-licence rows cover all three `identity` work
        types. An over-release is worse than an over-protection, so the covered
        term stays evidence and the cure belongs to the vocabulary.
        """
        tokens = _tokens(text)
        for start in range(len(tokens)):
            for end in range(start + 1, len(tokens) + 1):
                candidate = tokens[start:end]
                owners = self._index.get(candidate)
                if owners is not None:
                    yield " ".join(candidate), owners
                if candidate not in self._prefixes:
                    break

    def _plausible(self, schema: SchemaRules, *, extension: str | None,
                   source_types: set[str]) -> bool:
        """Rule 14's `file_kind_plausible`, used only to VETO.

        `file_kinds.never_alone` is `true` in all 358 rows, so a plausible kind is
        never evidence and never scores. It can only rule a schema out.
        """
        if extension and extension.casefold() in schema.extensions:
            return True
        return bool(source_types & schema.source_types)

    def _capture(self, conn: sqlite3.Connection, file_id: str,
                 content_hash: str, *,
                 source_types: set[str]) -> "Recognition | None":
        """`CAPTURE_SCHEMA`'s rule: a text-less picture or recording IS a capture.

        Three questions, and all three must answer yes. Each is asked of the part
        that owns it, so none of them is a rule this method invented.

        * **Does the library have this schema?** A hand-built rule set that never
          compiled `photos` cannot recognise anything as it, and `_handling` would
          raise on a schema the deployment never named.
        * **Has anything read words out of this file?** `TEXTLESS_SOURCE_TYPES` is
          the whole of it: the families in the file's own live evidence, gathered
          by `_matches` one call up rather than re-read here. An `ocr` or a
          `text_document` row means there was text, and a file with text is not
          this case whatever its extension says.
        * **Is it a picture or a recording?** P5's RECORDED routing decision, which
          is the only part that has answered "what family is this file" -- detected
          format over declared extension, written down at extract time. The
          `photos` schema's own compiled `extensions` would be the wrong list to
          ask: it holds `.csv`, `.eml` and `.dat` from the export rows, so a
          text-less spreadsheet would come back a photograph.

        **AND IT CITES.** §8.4 makes the classification evidence-backed and
        `ClassificationRecord` refuses a `detector` record with no references, so
        the recognition rests on the observations that ARE the answer -- P3's §1.2
        metadata rows, which is where the extension and the mime type live. A file
        with none of them is not recognised: there is nothing to point at, and a
        conclusion nothing can be pointed at for is the one thing this package
        never produces.
        """
        if CAPTURE_SCHEMA not in self._rules.schemas:
            return None
        if not source_types <= TEXTLESS_SOURCE_TYPES:
            return None
        decisions = routing_decisions(conn, file_id, content_hash)
        if not any(row["source_type"] in CAPTURE_SOURCE_TYPES
                   for row in decisions):
            return None
        refs = [row["observation_key"] for row in conn.execute(
            "SELECT observation_key, location FROM evidence WHERE file_id = ? "
            "AND content_hash = ? AND superseded_by IS NULL ORDER BY rowid",
            (file_id, content_hash))
            if _json.loads(row["location"]).get("zone") == "metadata"]
        if not refs:
            return None
        return Recognition(schema_id=CAPTURE_SCHEMA, matches=(),
                           evidence_refs=tuple(dict.fromkeys(refs)))

    # --- deciding ------------------------------------------------------------

    def explain(self, conn: sqlite3.Connection, file_id: str,
                content_hash: str) -> Recognition | Abstention:
        """What this detector concluded about one file version, and why."""
        file_row = get_file(conn, file_id)
        if file_row is None:
            return Abstention("no_evidence", None,
                              f"{file_id} has no P1 row to classify")
        path = PurePath(file_row["current_path"])
        # FIRST, and before any evidence is read: P3's rule is the one refusal
        # nothing overrides, and the predicate is P3's own rather than a second
        # copy of it. §4b: P3 "does not create a `files` row for anything inside
        # it", so this should be unreachable through a live scan -- it is here
        # because a detector must not be the part that makes it reachable.
        if is_protected_container(path, extra=self._is_protected):
            return Abstention(
                "protected_container", None,
                f"{file_id} at {path} is inside a protected container and is "
                "marked, counted and never opened; it is unclassified because "
                "nothing looked, not because nothing was found")

        matches, source_types = self._matches(conn, file_id, content_hash)
        if not matches:
            # BEFORE THE ABSTENTION, because for a picture or a recording with no
            # words in it there is nothing here to abstain about: the file kind IS
            # the answer, and `CAPTURE_SCHEMA` carries the whole argument.
            capture = self._capture(conn, file_id, content_hash,
                                    source_types=source_types)
            if capture is not None:
                return capture
            return Abstention("no_evidence", None,
                              f"{file_id} carries no term any schema authored")

        by_schema: dict[str, list[TermMatch]] = {}
        for match in matches:
            by_schema.setdefault(match.schema_id, []).append(match)
        # The unfiltered count. The gate below may drop schemas the person did
        # not declare; this copy is what a declined winner is cited from.
        catalogue = {
            schema_id: list(found) for schema_id, found in by_schema.items()}
        declared = self._declared()
        if declared:
            by_schema = {
                schema_id: found for schema_id, found in by_schema.items()
                if schema_id in declared}

        def finish(outcome: Recognition | Abstention) -> Recognition | Abstention:
            return self._cite_outside_declared(
                outcome, catalogue, declared, file_row=file_row,
                source_types=source_types)

        # An empty table has no leader. `max` on it would raise, and a file
        # that matched only undeclared schemas is an abstention, not a crash.
        if not by_schema:
            return finish(Abstention(
                "no_evidence", None,
                f"{file_id} matched no term of a life declared for this folder"))
        best = max(len(found) for found in by_schema.values())
        leaders = sorted(
            schema_id for schema_id, found in by_schema.items()
            if len(found) == best)

        # `never_alone`, read literally. One term is one signal and one signal
        # never activates a schema, whichever schema it is.
        # THE PERSON'S OWN ANSWER, which is not a signal about the file.
        #
        # `00` requires abstention where two readings are both supported BY
        # EVIDENCE, and that rule is untouched: this reads no evidence. `66` §13
        # puts it in the structural column in as many words -- a structural answer
        # "resolves a user relationship or policy fact that FILE EVIDENCE CANNOT
        # SAFELY DETERMINE", and may "resolve role ambiguity". The file is one
        # thing, its words support several readings, and the person knows which.
        #
        # It applies BEFORE the arity gate because that is where the ties actually
        # happen: two schemas at one term each is the common case (a deposition
        # transcript, a passport), and a resolution that only ran at two terms
        # would never fire on the files that raised the question.
        #
        # Three limits, and each has a test:
        #  * EXACTLY ONE settled reading among those tied. An answer naming both
        #    leaves the tie a tie, because choosing between two things the person
        #    confirmed would be the invented tie-breaker this package lacks.
        #  * ONLY AMONG THE LEADERS. An answer naming a reading the file never
        #    suggested decides nothing -- otherwise one confirmed schema would
        #    reach into every unrelated file on the disk, which is §13's "reused
        #    outside its stated scope" arriving as a recognition bug.
        #  * NEVER FROM NOTHING. A file whose words name no schema at all reaches
        #    `no_evidence` above and never gets here, so an answer cannot put a
        #    reading into a file that suggested none.
        #
        # The person's confirmation counts as the second signal for the schema it
        # names. `never_alone` is a rule about the DETECTOR concluding from one
        # signal; it was never a rule about what a person may tell the product,
        # and §13 explicitly permits a structural answer to activate a schema.
        if len(leaders) > 1 and self._settled_by_user is not None:
            settled = [schema_id for schema_id in leaders
                       if schema_id in frozenset(self._settled_by_user())]
            if len(settled) == 1:
                leaders = settled
                best = max(best, 2)
                by_schema[settled[0]] = list(by_schema[settled[0]])

        # §2.2's OTHER kind of signal. `00` states the rule as "a course-code
        # PATTERN TOGETHER WITH academic context such as 'syllabus,' 'lecture,'
        # 'credits,' 'instructor,' or 'semester'" -- one PATTERN and one TERM.
        # This module required two TERMS, and since `SchemaRules` carries no
        # pattern the course code contributed exactly zero: the sentence `00`
        # uses to define the whole mechanism described something the product
        # could not do.
        #
        # `never_alone` is unchanged and still literal -- one SIGNAL never
        # activates a schema. What changes is that a signal stops being assumed
        # to be a term.
        #
        # **A pattern CORROBORATES and never NOMINATES.** The identifier pattern
        # a deployment ships is schema-agnostic: `PHYS1401` and `X12345678` are
        # the same shape to it, so it cannot say WHICH schema a file belongs to
        # and is never allowed to try. It may only second a schema exactly one
        # term already named. That is what keeps it from inventing: a file whose
        # terms name two schemas still abstains, however many codes it carries.
        #
        # The identifier must also be an observation NO term matched, or a schema
        # whose authored term happens to be an identifier would corroborate
        # itself out of a single signal.
        if best < 2 and len(leaders) == 1 and self._corroborating is not None:
            # AN OBSERVATION THAT IS NOTHING BUT AN AUTHORED TERM, which is the
            # case the old rule was written for and the only one it should have
            # refused. Its comment says it: "a schema whose authored term happens
            # to be an identifier would corroborate itself out of a single
            # signal." A term that IS the whole observation is that -- one signal
            # read twice.
            #
            # The rule as written asked a wider question -- any observation ANY
            # term matched -- and that refused `00`'s own worked example. "BUSIB
            # 4300 becomes a course fact only when the engine finds a course-code
            # PATTERN TOGETHER WITH academic context such as 'syllabus'": on a
            # real file the pattern and the word are in the SAME observation,
            # because the filename is where both are written. Measured on the
            # owner's `Syllabus BUSIB 4300 Spring 2026 Haran Segram.pdf`, the
            # filename holds `syllabus` and `BUSIB 4300`, its key was in the
            # matched set, and the easiest file in the corpus abstained.
            #
            # The filename is also the ONE signal that never leaves the device --
            # `privacy.vocabulary.ALWAYS_LOCAL` holds `path` and `filename` -- so
            # a file refused here can never be rescued by a model either.
            one_signal_twice = {match.observation_key for match in matches
                                if match.whole}
            # The nominating term comes from the file ITSELF -- its text, its own
            # name -- and never from the absolute path it happens to sit under.
            # Found by running it: a corpus in a directory called
            # `.../test_a_placement_the_person_mu0/` matched the authored term
            # 'placement' out of the PATH observation, and an identifier in the
            # body then confirmed it, so four contentless files classified as
            # `creative`. That refusal is `_matches`'s now, applied to every door
            # rather than to this one, because the door where a schema WINS had
            # the same hole and a rule with two homes is this project's own named
            # defect.
            # AND IT MAY NOT SECOND A WORD THAT ONLY SURROUNDS A SAFETY DOMAIN.
            # `00`'s worked example is a course code together with academic
            # context -- 'syllabus', 'lecture', 'credits' -- and what it produces
            # is a course fact. For one of `00`'s four safety domains the same
            # arithmetic produces `protected=True`: a locked door, the heaviest
            # outcome this detector can reach. `_precaution` and the
            # winning-schema guard both already refuse that outcome on a term
            # that merely accompanies such a document -- the rule adopted after
            # `finance`'s context term `credit`, out of "credit hours", marked
            # two university syllabi `sensitive_personal`. This branch was the
            # one door left where that same evidence still got through, because
            # a corroborated term reaches arity and a schema at arity WINS.
            #
            # Measured against the shipped manifest: `IMG_4471.pdf`, whose whole
            # text is "Rome, the balance of light", carrying a reference code,
            # came back `sensitive_personal, protected=True`. One word that
            # surrounds a financial document, plus a code that says nothing about
            # which schema it belongs to.
            #
            # Only the safety domains are narrowed, and the narrowing is the
            # shape of the OUTCOME rather than a doubt about the evidence:
            # `00`'s example still executes unchanged for every ordinary schema.
            leader = leaders[0]
            corroborable = leader not in SAFETY_DOMAIN_IDS or leader in (
                self._safety_readings_in_evidence(conn, file_id, content_hash))
            if corroborable and any(
                    key not in one_signal_twice for key in
                    self._corroborating(conn, file_id, content_hash)):
                best = 2

        # THE KIND STILL ANSWERS WHEN THE ONLY SCHEMA THE TERMS RAISED IS THE ONE
        # THE KIND WOULD HAVE ANSWERED. `_capture` is asked above only where there
        # is no term at all, and that left a text-less picture whose own NAME says
        # `photos` worse off than one that says nothing: the filename and the file
        # kind both say picture, and the two agreeing cancelled each other.
        #
        # Measured 21 Sep 2026 over ten images written from two byte strings and
        # named the way DEVICES name them. Four were recognised; six abstained,
        # and every one of the six had matched a term `photos` itself authored --
        # `screenshot`, `photo`, `scan`, `panorama`. The pair that states it is one
        # picture under the two names Apple has shipped: `Screen Shot 2026-…png`,
        # the pre-Mojave default, is recognised, and `Screenshot 2026-…png`, the
        # default since, is not. A person who upgraded their laptop watched their
        # screenshots stop being recognised over a closed-up space.
        #
        # `file_kind_never_alone` IS UNTOUCHED, and the condition is what says so.
        # That rule forbids a KIND from activating a schema ALONE; here the kind is
        # not alone, the name is saying the same word, and the schema they both
        # name is one schema. So this asks for `leaders` to be exactly `photos` --
        # not `photos` among others, which is a tie and stays one, and not any
        # other schema, which is the passport below.
        #
        # AND IT WIDENS NOTHING. `photos` is the only schema a term can raise here
        # and the only one `_capture` answers, so no file that was held stops being
        # held: a text-less image whose name says `passport` raises `identity`,
        # never reaches this line, and goes on being held by `_precaution`. That
        # asymmetry is the whole reason this is a defect to close rather than a
        # design question to ask -- there are not two readings to choose between.
        if best < 2 and leaders == [CAPTURE_SCHEMA]:
            capture = self._capture(conn, file_id, content_hash,
                                    source_types=source_types)
            if capture is not None:
                return finish(capture)

        if best < 2:
            schema_id = leaders[0]
            # `leaders` is SORTED, so `leaders[0]` is the alphabetically first of
            # however many readings tied -- and reporting it alone threw the rest
            # away. On a file reading "Passport number X12345678. Client identity
            # document." the readings are `creative` (from 'client') and
            # `identity` (from 'passport'); `identity` is one of `00`'s four
            # safety domains and it lost a coin toss to alphabetical order. The
            # file's most alarming reading was in the evidence and no consumer
            # could ever see it.
            #
            # Nothing about the DECISION changes: still an abstention, still
            # `never_alone`, still the same arity. What changes is that the record
            # stops being lossy. `tied_schema_ids` is the field that already
            # exists for this and the `ambiguous` branch below already fills it;
            # a tie is a tie whether it happens at one term or at five.
            #
            # Left empty when there is only one reading, because one reading is
            # not a tie -- and a field filled unconditionally would be useless for
            # telling the two apart.
            return finish(Abstention(
                "no_corroboration", schema_id,
                f"{schema_id} matched one authored term "
                f"({by_schema[schema_id][0].term!r}) and every node row carries a "
                "`never_alone` rule; one signal does not activate a schema"
                + (f". {len(leaders)} readings matched one term each and none "
                   f"outranks another ({', '.join(leaders)})"
                   if len(leaders) > 1 else ""),
                tied_schema_ids=tuple(leaders) if len(leaders) > 1 else (),
                deferred_readings=self._readings(schema_id),
                # R-166: EVERY leader, not just the one named. A near miss of one
                # is a shortlist of one and still needs its citation; a tie of two
                # needs both sides or the question cannot say what either rests on.
                **_named(self._cited(by_schema, leaders))))

        plausible = [schema_id for schema_id in leaders
                     if self._plausible(self._rules.schemas[schema_id],
                                        extension=file_row["extension"],
                                        source_types=source_types)]
        if not plausible:
            schema_id = leaders[0]
            return finish(Abstention(
                "file_kind_implausible", schema_id,
                f"{schema_id} matched {best} authored terms on a file kind its "
                f"rows never name ({file_row['extension']!r}, "
                f"{sorted(source_types)}); `file_kind_plausible` is a constraint "
                "and never a signal",
                deferred_readings=self._readings(schema_id),
                **_named(self._cited(by_schema, leaders))))
        if len(plausible) > 1:
            # `00` requires abstention where two readings are both supported.
            # Nothing breaks this tie: a tie-breaker would be the invented
            # threshold this package exists without.
            return finish(Abstention(
                "ambiguous", None,
                f"{len(plausible)} schemas are supported by {best} authored terms "
                f"each ({', '.join(plausible)}); both readings are supported and "
                "`00` requires abstention rather than a winner",
                tied_schema_ids=tuple(plausible),
                deferred_readings=self._readings(plausible[0]),
                **_named(self._cited(by_schema, plausible))))

        schema_id = plausible[0]
        found = tuple(by_schema[schema_id])
        if schema_id not in self._handling:
            # Recognised and not classified, which are two different things.
            # `planning/domains/_CONTRACT.md` rule 5 forbids the research from
            # carrying a handling class, and `00` states one for no ordinary
            # domain, so this is the honest end of the road rather than a class
            # picked to let the pipeline continue.
            return finish(Abstention(
                "unassigned_handling", schema_id,
                f"{schema_id} was recognised from {len(found)} authored terms and "
                "the caller's handling policy states no class for it; recognition "
                "is not classification",
                deferred_readings=self._readings(schema_id),
                **_named(self._cited(by_schema, (schema_id,)))))
        refs: list[str] = []
        for match in found:
            if match.observation_key not in refs:
                refs.append(match.observation_key)
        return finish(Recognition(schema_id=schema_id, matches=found,
                                  evidence_refs=tuple(refs)))

    def _declared(self) -> frozenset[str]:
        """Lives the person confirmed. Empty means no profile, not an empty list."""
        if self._declared_lives is None:
            return frozenset()
        return frozenset(self._declared_lives())

    def _unique_assigned_winner(
            self, catalogue: Mapping[str, list["TermMatch"]], *,
            extension: str | None, source_types: set[str]) -> str | None:
        """The schema the unfiltered count would have named, or none.

        A unique plausible leader at two or more terms, with a handling class.
        A tie, a single term, an implausible kind, and an unassigned class are
        abstentions already, and this does not invent a winner for them.
        `settled_by_user` is not consulted: it breaks ties only among leaders
        that survived the gate.
        """
        if not catalogue:
            return None
        best = max(len(found) for found in catalogue.values())
        if best < 2:
            return None
        leaders = [schema_id for schema_id, found in catalogue.items()
                   if len(found) == best]
        plausible = [
            schema_id for schema_id in leaders
            if schema_id in self._rules.schemas and self._plausible(
                self._rules.schemas[schema_id], extension=extension,
                source_types=source_types)]
        if len(plausible) != 1:
            return None
        winner = plausible[0]
        if winner not in self._handling:
            return None
        return winner

    def _cite_outside_declared(
            self, outcome: "Recognition | Abstention",
            catalogue: Mapping[str, list["TermMatch"]],
            declared: frozenset[str], *, file_row, source_types: set[str]
            ) -> "Recognition | Abstention":
        """Cite a winner the allow-list declined, without offering it as a kind.

        An empty declaration is not a gate, and a recognition of a declared
        life stands. When the unfiltered count has one plausible winner the
        person did not declare, the abstention names that schema on
        `matched_terms` and in the detail string.

        `schema_id` stays `None` and `tied_schema_ids` stays empty. Do not
        "fix" that by copying the winner onto either field: `situation_outcome_of`
        builds folder candidates from those two, and a declined schema must
        not become a vote or a gist line.
        """
        if not declared or isinstance(outcome, Recognition):
            return outcome
        winner = self._unique_assigned_winner(
            catalogue, extension=file_row["extension"], source_types=source_types)
        if winner is None or winner in declared:
            return outcome
        found = catalogue[winner]
        return Abstention(
            "outside_declared_lives", None,
            f"{winner} matched {len(found)} authored terms and is not a life "
            "declared for this folder; the file stays unplaced",
            **_named(self._cited(catalogue, (winner,))))

    def situation_outcome(self, conn: sqlite3.Connection, file_id: str,
                          content_hash: str) -> SituationOutcome:
        """This file, as site G's pass reads it (`104` §18.26's owed row).

        `explain` and nothing more: this recogniser has one answer about a file
        and this is that answer wearing the shape a second recogniser can also
        wear. `SemanticRecogniser` implements the same method, calls this one
        first, and speaks only where these rules stopped -- which is the
        composition `__call__` already runs, put where the QUESTION is shaped
        rather than only where the record is written.
        """
        return situation_outcome_of(self.explain(conn, file_id, content_hash))

    def _precaution(self, conn: sqlite3.Connection, outcome: "Abstention", *,
                    file_id: str, content_hash: str
                    ) -> ClassificationRecord | None:
        """The file is not recognised, and it is still protected.

        **Corroboration governs what we CLAIM. Precaution governs what we
        EXPOSE.** `never_alone` is a rule about ACTIVATING A SCHEMA, and applying
        it to protection as well is what left a passport unprotected: "Passport
        number X12345678. Client identity document." matches `identity` on
        'passport' and `creative` on 'client', ties at one term each, abstains --
        and the file came back unclassified, unprotected, with its number free to
        become a folder name.

        `00`:52 states the opposite requirement for exactly these four domains:
        finance, identity, medical and legal are *"detected and protected BEFORE
        any cloud or automated placement decision is allowed"*, and `00`:185 says
        such material *"should enter a protected state immediately"*. Neither
        sentence asks for corroboration first.

        So the two questions get two answers about the same file, and that is
        correct: `explain` still ABSTAINS -- no schema is activated, the file
        stays honestly unrecognised, and nothing claims to know what it is --
        while the classification carries the safety domain's own handling with
        `basis='safety_domain'` saying exactly why.

        **This is not the over-protection collapse.** That one answered EVERY
        abstention with `highly_sensitive_credential_bearing, protected=True`, and
        `cli.py`'s `classifier` records the cost: it "made an unreadable scan and
        a passport identical in P7's store". This fires only where a safety-domain
        term is actually present in the file's own evidence. A file carrying no
        term at all is untouched -- "we deliberately did not look" and "we could
        not tell" stay different answers.

        The protected-container refusal is never overridden: `explain` returns
        that abstention before reading any evidence, so the matches this rests on
        are read only for a file that was already open to being read.

        **THE DECISION MOVED AND THE RULE DID NOT (`104` §18 gap 24).** Everything
        this method used to work out now lives in `precaution_report`, because the
        hold has a second reader -- `cli.ask_the_situation`, which puts every held
        file to the local model and needs to know WHY it is held to say so in the
        dossier. What is left here is the record: the report says which safety
        domain, and `_protect_as` writes the handling for it. Two answers computed
        apart would be the two-homed rule this package has paid for before.
        """
        report = self.precaution_report(conn, outcome, file_id=file_id,
                                        content_hash=content_hash)
        if report is None:
            return None
        return self._protect_as(conn, (report.schema_id,), file_id=file_id,
                                content_hash=content_hash)

    def precaution_report(self, conn: sqlite3.Connection,
                          outcome: "Recognition | Abstention", *,
                          file_id: str, content_hash: str) -> "Precaution | None":
        """WHY this file is held, or `None` because it is not.

        THE RULE HAS ONE HOME AND TWO READERS. `_precaution` used to hold this
        arithmetic and return only a record; `104` §18 gap 24 asks for the same
        conclusion in a form a dossier and a report can carry, and a second copy
        of "which safety domain is a tied leader and names the file" is exactly
        the two-homed rule this package has paid for before. So the decision is
        made here, `_precaution` reads the schema off it, and a `None` here and a
        `None` there are the same `None`.

        `precaution_report(...) is not None` is therefore the exact predicate for
        "the rules are holding this file" -- which is what `cli.ask_the_situation`
        needs to make the mark itself a reason to ask.

        **AND A RECOGNITION IS HELD TOO (`104` §18.26 gap 24b, the owner's ruling
        of 10 Sep 13:10).** `basis='safety_domain'` has THREE writers and gap 24
        could report only one of them. The other two sit on files this detector
        RECOGNISES -- the winning-schema branch in `__call__`, and a safety domain
        winning outright -- and on r19 eight of the eleven ordinary files wrongly
        held were of that kind, never asked because `00`:110 counts a recognised
        file settled. The predicate above is the same predicate for them: what
        changes is only which of `__call__`'s arms is asked, never a vocabulary, a
        floor or a zone rule. `_recognised_hold` is that arm and `__call__` reads
        it, so a hold and its report still cannot disagree about one file.
        """
        if isinstance(outcome, Recognition):
            return self._recognised_hold(conn, outcome, file_id=file_id,
                                         content_hash=content_hash)
        if outcome.reason == "protected_container":
            return None
        # A tied LEADER, and a term that says what the file IS. The leader test was
        # always here; the second half arrived with the outright-win branch and
        # belongs to both, because a tie is not evidence about which KIND of term
        # matched. Without it `finance`'s context term `statement` tied on a college
        # personal statement and marked it `sensitive_personal, protected=1`.
        says_what_it_is = self._safety_evidence(conn, file_id, content_hash)
        deterministic = self._deterministic_readings(conn, file_id, content_hash)
        # A TERM HOLDS WITH CORROBORATION; A CHECKSUM HOLDS ALONE (the owner's
        # ruling of 13 Sep 2026, 21:00: the ordinary files the rules held "MUST
        # NOT BE HELD"). Measured on the second corpus before the change: the rules
        # held 33 ordinary files and 14 of the 29 protected ones. Of the 33, eight
        # were club sign-up sheets held on a date of birth beside a name, ten were
        # essays and statements held on a person beside a condition, four were
        # held on the word `will`, and the rest on one word in a heading, a
        # filename or a table -- each one signal that is also ordinary English or
        # ordinary form-filling. Every protected file the rules caught carried a
        # word that says what the record is AND a second finding beside it: a
        # person, a date of birth, a diagnosis, a number. So the abstention arm now
        # asks for both, and the second finding may be either of the deterministic
        # layers' readings or a person the entity encoder named anywhere in the
        # file. The one signal that carries its own proof is a checksummed
        # identifier (`CHECKSUMMED_KINDS`: a card number, an IBAN, a bank pair, a
        # US SSN, an HKID): it holds alone, as 7(a) ruled. A date of birth, a
        # passport-shaped number and a medical record number are shapes without a
        # check and corroborate rather than hold, and 7(b)'s pair corroborates on
        # the same terms: a person beside a condition in a personal statement is a
        # sentence about a life, not a record of a diagnosis, and the corpus had
        # ten of those for every one that was a record. What the rules release
        # here is not sent anywhere on their word: the gate reads it next, at its
        # own ceiling, and the gate's prompt asks whose particulars the text shows.
        work_types = self._safety_work_type_matches(conn, file_id, content_hash)
        # Leaders already sit on `schema_id` and `tied_schema_ids`. The
        # declared-life gate deliberately leaves both empty and cites the
        # declined schema on `matched_terms` instead, so a vote cannot file
        # the file there. A safety domain in that citation is still a hold:
        # the gate decides what we claim, not what we expose.
        named: list[str | None] = [outcome.schema_id, *outcome.tied_schema_ids]
        if outcome.reason == "outside_declared_lives":
            named.extend(schema_id for schema_id, _terms in outcome.matched_terms)
        readings = [schema_id for schema_id in named
                    if schema_id in SAFETY_DOMAIN_IDS and schema_id in work_types
                    and (any(_names_the_file(match)
                             for match in work_types[schema_id])
                         or self._corroborated(conn, schema_id, deterministic,
                                               file_id=file_id,
                                               content_hash=content_hash))]
        readings += [schema_id for schema_id, matches in deterministic.items()
                     if schema_id not in readings
                     and any(match.term in CHECKSUMMED_KINDS for match in matches)]
        if not readings:
            return None
        # `SCHEMA_IDS` order, so two safety readings resolve the same way twice
        # rather than by whichever the abstention happened to name first. The same
        # choice `_protect_as` makes, made once and handed to it.
        schema_id = min(readings, key=SCHEMA_IDS.index)
        if self._handling.get(schema_id) is None:
            # The caller's policy states no class for this domain, so `_protect_as`
            # holds nothing -- and a report of a hold that was never taken would be
            # a screen saying a file is held when it is not.
            return None
        return _reported(schema_id, says_what_it_is[schema_id])

    def _recognised_hold(self, conn: sqlite3.Connection, outcome: "Recognition",
                         *, file_id: str, content_hash: str
                         ) -> "Precaution | None":
        """The hold on a file the rules RECOGNISED, in that hold's own terms.

        `104` §18.26 gap 24b. Two of the three writers of `basis='safety_domain'`
        run on a `Recognition`, and this reports each of them in ITS OWN words --
        it decides nothing the writer did not already decide, and every rule the
        writers stand on is untouched:

        * **A safety domain WON.** The record `__call__` returns is the winner's
          own handling and its basis is `safety_domain`, so the hold IS the
          recognition: the domain is `outcome.schema_id` and the terms are the
          WORK TYPES among the matches the recognition was built from.
          `Precaution.terms` is "the work types of that domain the file's
          evidence carries", and a domain that won on its CONTEXT terms alone --
          `finance` ships 216 of them -- reports an empty tuple rather than
          calling a word that merely accompanies such a document a work type.
          Empty and not `None`: the row says `safety_domain`, so a report of
          nothing would be a hold no screen counts, which is gap 24's own defect.
        * **Another schema won and a safety domain named the file anyway.** That
          is the winning-schema branch, and its rule is
          `_safety_readings_naming_the_file`: a work type of one of `00`'s four,
          in one of SPEC 2.2's naming zones. The terms and zones reported are
          exactly the matches that rule passed -- not the wider set `_precaution`
          reads on an abstention, because this is the OTHER writer and reporting
          its neighbour's working would describe a hold nobody took.

        `min(readings, key=SCHEMA_IDS.index)` is `_protect_as`'s own choice, made
        here once and handed to it, on the same terms as the abstention arm.
        """
        deterministic = self._deterministic_readings(conn, file_id, content_hash)
        if outcome.schema_id in SAFETY_DOMAIN_IDS:
            # The winner is the hold. `explain` returns `unassigned_handling`
            # rather than a `Recognition` where the policy states no class, so a
            # recognised schema always has one and there is nothing to check.
            #
            # Its own identifiers and entities join the report (`00` amendment 7)
            # and change no decision here: the file is already held as this domain.
            # What they change is what the report SAYS, which is gap 24's whole
            # subject -- a `finance` recognition on a statement that also prints a
            # card number reports the card, and the model reading the dossier is
            # told the hold rests on a number and not only on the word `statement`.
            return _reported(outcome.schema_id, tuple(
                match for match in outcome.matches
                if match.term in self._work_types.get(outcome.schema_id,
                                                      frozenset())
            ) + deterministic.get(outcome.schema_id, ()))
        readings = self._safety_readings_naming_the_file(
            conn, file_id, content_hash,
            in_evidence=self._safety_readings_in_evidence(
                conn, file_id, content_hash))
        # ANOTHER SCHEMA WON AND A CHECKSUM STILL HOLDS THE FILE (7(a)). This arm's
        # rule is the naming-zone one, written because five authored work types are
        # also ordinary English and a MENTION had to be told from a claim by where
        # it sat. An identifier is under no such doubt and sits where the document
        # printed it -- a passport page's number is in its BODY -- so requiring a
        # naming zone of it would release exactly the passport `_precaution`'s own
        # docstring opens with. `104` §18.56 measured what the release costs: a
        # health form the rules called ordinary went to the cloud on the rules' word.
        # AND SINCE 13 Sep 2026 ONLY A CHECKSUM JOINS THEM ALONE (the abstention
        # arm's rule, for its reason): a date of birth, a passport-shaped number
        # and a person beside a condition corroborate a term and hold nothing by
        # themselves, and the naming-zone readings above already hold alone.
        readings = list(readings) + [
            schema_id for schema_id, matches in deterministic.items()
            if schema_id not in readings
            and any(match.term in CHECKSUMMED_KINDS for match in matches)]
        if not readings:
            return None
        schema_id = min(readings, key=SCHEMA_IDS.index)
        if self._handling.get(schema_id) is None:
            # The caller's policy states no class for this domain, so `_protect_as`
            # holds nothing -- and a report of a hold that was never taken would be
            # a screen saying a file is held when it is not. The abstention arm
            # refuses on the same line for the same reason.
            return None
        work_types = self._work_types.get(schema_id, frozenset())
        matches, _ = self._matches(conn, file_id, content_hash)
        return _reported(schema_id, tuple(
            match for match in matches
            if match.schema_id == schema_id and match.term in work_types
            and _names_the_file(match)) + deterministic.get(schema_id, ()))

    def _safety_work_type_matches(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> dict[str, tuple["TermMatch", ...]]:
        """The same question `_safety_readings_in_evidence` asks, with its WORKING.

        Split out for `104` §18 gap 24: two callers want the schema ids and one
        wants the matches those ids were read off, and computing them apart would
        be two answers to "does this file's own words name it as one of `00`'s
        four" -- the shape that let a MENTION become a claim in the first place.
        Keyed in `sorted` order so the mapping's own iteration order is the tuple
        the readings method used to return.
        """
        matches, _ = self._matches(conn, file_id, content_hash)
        found: dict[str, list["TermMatch"]] = {}
        for match in matches:
            if (match.schema_id in SAFETY_DOMAIN_IDS
                    and match.term in self._work_types.get(match.schema_id,
                                                           frozenset())):
                found.setdefault(match.schema_id, []).append(match)
        return {schema_id: tuple(found[schema_id]) for schema_id in sorted(found)}

    def _identifier_readings(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> dict[str, tuple["TermMatch", ...]]:
        """The masked identifier readings this file version carries, by safety domain.

        `00` amendment 7(a). A checksummed card number, an IBAN that passes mod-97, a
        Hong Kong identity number whose check character is right -- each one is a
        reading of one of `00`:52's four, and the ruling says it holds the file
        "exactly as an authored safety term does".

        **IT COMES BACK AS A `TermMatch`, AND THAT IS THE WHOLE OF THE WIRING.** Every
        hold in this module is computed from matches and reported by `_reported`; a
        second record shape for the second kind of evidence would mean a second
        projection, a second `min(readings, key=SCHEMA_IDS.index)` and a second answer
        to "why is this file held" -- which is the two-homed rule this package has
        paid for before (`104` §18.26 gap 24b's own reason for existing). The `term`
        is the KIND, because that is what the reading actually says: not that the
        document used the word `passport`, but that the characters on its page are a
        passport number. `whole` is True because the reading IS the identifier and
        nothing else, so the corroboration gate treats it the way it treats any
        reading that is nothing but its own signal.

        **NO NAMING-ZONE TEST, and the checksum is why.** `_safety_readings_naming_the_file`
        exists because five authored work types -- `will`, `statement`, `receipt`,
        `invoice`, `passport` -- are also ordinary English, so a MENTION had to be
        told from a claim by where it sat. A number that passes Luhn, mod-97 or mod-11
        is not a mention of anything: an essay that discusses credit cards does not
        contain a valid card number, and a datasheet that uses the word `will` on
        every page contains no IBAN. The zone is still RECORDED on every match, so a
        report and a dossier can say where the number was found.

        Reads the same rows `_matches` refuses, through the same predicate, so the
        two sets are exact complements by construction.
        """
        found: dict[str, list["TermMatch"]] = {}
        for row in conn.execute(
                "SELECT observation_key, extractor_name, location FROM evidence "
                "WHERE file_id = ? AND content_hash = ? AND extractor_name LIKE ? "
                "AND superseded_by IS NULL ORDER BY rowid",
                (file_id, content_hash, IDENTIFIERS_NAMESPACE + "%")):
            if not is_identifier_extractor(row["extractor_name"]):
                # `LIKE` is the index's filter and the predicate is the rule; a name
                # that merely starts with the same characters under some other
                # collation is not one of these readings.
                continue
            schema_id = IDENTIFIER_SAFETY_DOMAIN.get(kind_of(row["extractor_name"]))
            if schema_id is None:
                # A kind this deployment's detector states no domain for. The import
                # guard above makes that impossible for a kind the shipped extractor
                # produces, so this can only be a row an older or a newer version
                # wrote -- and counting it as a domain of this module's choosing
                # would be inventing the ruling rather than reading it.
                continue
            where = _json.loads(row["location"])
            found.setdefault(schema_id, []).append(TermMatch(
                schema_id=schema_id, term=kind_of(row["extractor_name"]),
                observation_key=row["observation_key"], zone=where.get("zone"),
                page=next((step.get("index")
                           for step in where.get("container_path") or ()
                           if step.get("kind") == "page"), None),
                whole=True))
        return {schema_id: tuple(found[schema_id]) for schema_id in sorted(found)}

    def _corroborated(self, conn: sqlite3.Connection, schema_id: str,
                      deterministic: "Mapping[str, tuple[TermMatch, ...]]", *,
                      file_id: str, content_hash: str) -> bool:
        """Is a term of this domain corroborated by a second, independent finding?

        The second finding is a deterministic reading of the SAME domain (an
        identifier shape, a person beside a diagnosis or a date of birth, an
        account number) or a person the entity encoder named anywhere in the
        file: a record is about someone, and a document that names nobody and
        carries no number is a document about the topic.
        """
        if schema_id in deterministic:
            return True
        return conn.execute(
            "SELECT 1 FROM evidence WHERE file_id = ? AND content_hash = ? "
            "AND extractor_name = ? AND superseded_by IS NULL LIMIT 1",
            (file_id, content_hash, ENTITY_NAMESPACE + PERSON_ENTITY),
        ).fetchone() is not None

    def _entity_readings(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> dict[str, tuple["TermMatch", ...]]:
        """`00` amendment 7(b): what the local encoder found BESIDE what.

        The ruling is a sentence about two things in one place -- "a person beside a
        diagnosis or an identity number holds the file without a model call" -- so
        this is the only reader in this module that weighs a reading against another
        reading rather than on its own. `ENTITY_BESIDE_A_PERSON` and `ENTITY_ALONE`
        are the two halves; neither is decided here.

        **"BESIDE" IS STRUCTURAL AND IS NOT A NUMBER.** It means the same TEXT UNIT
        -- the same `container_path` -- which is `facts.anchor_statements`'
        `_containing_span_reading` asking the same kind of question the same way:
        that module's `_span_index` groups a file version's spanned readings by their
        serialized container path and calls the grouping structural, with the comment
        that it "needs no text and no parsing". Nothing here counts characters
        between two entities, because a character distance would be a threshold and
        this package holds none -- and a threshold would also be wrong: on an intake
        form a name and a diagnosis are two table cells and forty characters apart,
        while in a paragraph of prose two unrelated mentions can be adjacent.
        `extractors.entities` mints every reading onto the HOST's container path, so
        two entities share a path exactly when the encoder read them out of one unit.
        A page is a unit, a paragraph is a unit, a notebook cell is a unit: the
        document's own division, not this module's.

        THE ADDRESS IS P4'S OWN, through `serialize_container_path` over `Segment`s
        built from the stored location, and not a tuple assembled here. P4's rule 10
        compares paths that way -- "the comparison is on the ADDRESS and not on the
        record: segment-kind rule 2 makes a label descriptive only, so a labelled
        `slide=6` and a bare `slide=6` are one address" -- and "the same unit" has to
        mean what `text_units` means by it or this rule is measuring something else.

        THE RUN IS DELIBERATELY NOT PART OF THE ADDRESS, and it is the one place this
        is wider than `text_units`' own key. A PDF page read natively and the same
        page read by OCR are two units and one page; a person the native pass found
        on page one and a diagnosis the OCR pass found on page one are beside each
        other on that page, however the characters reached the database. Narrowing to
        `(run_id, path)` would release exactly the scanned health form this amendment
        was ruled for -- the one whose typed cover and photographed pages are read by
        two different extractors (`00` amendment 6).

        **WHAT A MATCH CITES.** A pair cites BOTH readings: the person and the thing
        beside them are jointly what raised the hold, and §8.4 says a record cites
        what raised it. A solo kind cites its own reading. The `term` is the reading's
        full `entities.<kind>` name rather than a bare kind, because -- unlike
        `IDENTIFIER_KINDS` -- the label set is the DEPLOYMENT's and there is no closed
        roster a reader could check a bare word against; the reading names itself,
        prefix and all, which is the contract `extractors.entities` publishes.

        Reads the rows `_matches` refuses, through the same predicate, so the two sets
        are exact complements by construction.
        """
        #: container address -> kind -> the matches found at it, in row order.
        by_unit: dict[str, dict[str, list[tuple[str, str | None, int | None]]]] = {}
        for row in conn.execute(
                "SELECT observation_key, extractor_name, location FROM evidence "
                "WHERE file_id = ? AND content_hash = ? AND extractor_name LIKE ? "
                "AND superseded_by IS NULL ORDER BY rowid",
                (file_id, content_hash, ENTITY_NAMESPACE + "%")):
            if not is_entity_extractor(row["extractor_name"]):
                # `LIKE` is the index's filter and the predicate is the rule.
                continue
            kind = row["extractor_name"][len(ENTITY_NAMESPACE):]
            if kind != PERSON_ENTITY and kind not in ENTITY_BESIDE_A_PERSON \
                    and kind not in ENTITY_ALONE:
                # An organisation, an email, a phone, a home address -- and any label
                # a later deployment adds. They hold nothing, which is the tables'
                # own statement, and skipping them here is that statement executing.
                continue
            where = _json.loads(row["location"])
            page = next((step.get("index")
                         for step in where.get("container_path") or ()
                         if step.get("kind") == "page"), None)
            address = serialize_container_path(tuple(
                Segment(step["kind"], step.get("index"), step.get("label"))
                for step in where.get("container_path") or ()))
            by_unit.setdefault(address, {}).setdefault(kind, []).append(
                (row["observation_key"], where.get("zone"), page))

        found: dict[str, list["TermMatch"]] = {}

        def _record(schema_id: str, kind: str, rows) -> None:
            for key, zone, page in rows:
                found.setdefault(schema_id, []).append(TermMatch(
                    schema_id=schema_id, term=ENTITY_NAMESPACE + kind,
                    observation_key=key, zone=zone, page=page, whole=True))

        for address in sorted(by_unit):
            kinds = by_unit[address]
            people = kinds.get(PERSON_ENTITY, [])
            for kind, schema_id in ENTITY_BESIDE_A_PERSON.items():
                if people and kind in kinds:
                    if (kind == MEDICAL_CONDITION_ENTITY
                            and self._topic_condition_mentions is not None
                            and len(kinds[kind]) >= self._topic_condition_mentions):
                        # A UNIT THAT NAMES THIS MANY CONDITIONS IS WRITING ABOUT
                        # THEM, not recording one person's (the owner's ruling of
                        # 13 Sep 2026; the deployment states the number and why).
                        continue
                    _record(schema_id, PERSON_ENTITY, people)
                    _record(schema_id, kind, kinds[kind])
            for kind, schema_id in ENTITY_ALONE.items():
                if kind in kinds:
                    _record(schema_id, kind, kinds[kind])
        return {schema_id: tuple(dict.fromkeys(found[schema_id]))
                for schema_id in sorted(found)}

    def _deterministic_readings(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> dict[str, tuple["TermMatch", ...]]:
        """Both deterministic layers' readings, by domain, in ONE answer.

        `00` amendment 7's first two items are two extractors and one conclusion:
        7(a)'s checksummed identifier and 7(b)'s person-beside-a-diagnosis each hold
        a file "without a model call", by the same three lines of code that hold a
        discharge summary. Every arm below asks this rather than either half, so a
        layer added to the amendment later is wired in one place -- and the four arms
        cannot come to disagree about one file, which is what this package has paid
        for most often.

        7(a) first within a domain, so a report that had both before 7(b) reads the
        way it read then.
        """
        merged = dict(self._identifier_readings(conn, file_id, content_hash))
        for schema_id, matches in self._entity_readings(
                conn, file_id, content_hash).items():
            merged[schema_id] = merged.get(schema_id, ()) + matches
        return {schema_id: merged[schema_id] for schema_id in sorted(merged)}

    def _safety_evidence(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> dict[str, tuple["TermMatch", ...]]:
        """EVERY kind of safety evidence this file carries, by domain, in one answer.

        The authored work types (`_safety_work_type_matches`) and the deterministic
        layers (`_deterministic_readings`), merged. `00` amendment 7 makes them one
        question -- "does this file's own evidence name it as one of `00`'s four" --
        and asking it in two places is how one of the four arms below would come to
        hold a file the other three release.

        Authored terms first within a domain, so a report reads the way it read
        before 7(a) for every file that has both, and `SCHEMA_IDS` order across
        domains is `_protect_as`'s own choice, made from this one mapping.
        """
        merged = dict(self._safety_work_type_matches(conn, file_id, content_hash))
        for schema_id, matches in self._deterministic_readings(
                conn, file_id, content_hash).items():
            merged[schema_id] = merged.get(schema_id, ()) + matches
        return {schema_id: merged[schema_id] for schema_id in sorted(merged)}

    def _safety_readings_in_evidence(
            self, conn: sqlite3.Connection, file_id: str,
            content_hash: str) -> tuple[str, ...]:
        """Safety domains whose OWN terms are in this file's evidence.

        Not the leaders, and not the winner: any safety domain the file's words
        actually name. `_precaution` asks the same question of an `Abstention`'s
        tied readings, which is the right set THERE because an abstention has no
        winner. Where a schema does win, the safety domain that lost is exactly the
        one at stake, so reading the leaders would ask a question whose answer is
        already known to be empty.

        **The term must say what the file IS, not merely surround it.** The library
        separates `work_type_terms` (a passport, a discharge summary) from
        `context_terms` (words that accompany such a document). `identity` ships
        `passport` as a WORK TYPE and carries no context terms at all, while
        `finance` carries 216 context terms including `credit`, `statement`, `total`
        and `receipt`.

        Without this the guard fired on one incidental word. Measured on a corpus of
        two course syllabi and nothing else: `academic` won ten terms to one and
        `credit` -- out of "credit hours" -- marked both files `sensitive_personal,
        protected=1`, removed the course folders and withheld every file from
        placement. A college personal statement was protected because it contains
        the word "statement". `cli.classifier` names that outcome in the file this guard
        lives beside: it "made an unreadable scan and a passport identical in P7's
        store". A safety domain that is merely MENTIONED is not a safety domain.

        This is `never_alone`'s discipline arriving in the form precaution can use.
        `_precaution` gets it for free by reading only an abstention's tied leaders;
        this branch, which runs when another schema WON, has no leaders to lean on
        and must say what it means directly.

        The term is also the FILE'S OWN and never a word in a directory above it.
        A corpus under a folder called `Passport` named `identity` for every file
        inside it -- measured, and it protected a syllabus. That refusal now lives
        in `_matches`, which is what these matches come from, because the same
        hole was open at the door where a schema WINS and one rule wants one home.

        **AND A CHECKSUMMED IDENTIFIER IS ONE OF THESE READINGS TOO** (`00` amendment
        7(a)). The question this answers is "does this file's own evidence name it as
        one of `00`'s four", and after 7(a) a file's evidence names a domain in two
        ways: with a word its author wrote, and with a number that passes the
        scheme's own arithmetic. `_safety_evidence` is the one place the two are put
        together, so every reader below -- the corroboration gate in `_decide`, the
        winning-schema branch, `__call__`'s `detector_no_safety_evidence` -- moves
        with the ruling at once. What that costs is stated rather than hidden: a
        `finance` leader on a file carrying a valid card number is now corroborable,
        which is exactly the sentence 7(a) asks for, and the guard that stopped
        `IMG_4471.pdf` -- a reference code, which is a code and no scheme's number --
        is untouched, because a reference code passes no checksum.
        """
        return tuple(self._safety_evidence(conn, file_id, content_hash))

    def _safety_readings_naming_the_file(
            self, conn: sqlite3.Connection, file_id: str, content_hash: str, *,
            in_evidence: tuple[str, ...]) -> tuple[str, ...]:
        """The same question, asked where a MENTION must not become a claim.

        `in_evidence` is the lenient answer, SUPPLIED rather than recomputed. It used
        to be asked for here, which meant `__call__` could not see it -- and seeing
        it is the whole of what `96` §20 asks for: *"the precondition would then be
        satisfied by evidence of having LOOKED"*. Passing it in also removes a scan
        rather than adding one; this method reads the file's matches once now, where
        it read them twice before.

        `_safety_readings_in_evidence` refuses a term that SURROUNDS a document.
        It cannot refuse a work type that is also ordinary English, and five of
        them are: `will`, `statement`, `receipt`, `invoice`, `passport`. Measured
        over a real 639-file corpus, one of those in body prose locked 33 files
        `sensitive_personal, protected=1` and withheld every one from placement --
        an Arduino `LICENSE.txt` on "receipt, statement, will", a 642-page chip
        datasheet on "will", and the owner's own design notes for THIS PRODUCT on
        the phrase "discharge summary".

        ARITY WAS TRIED FIRST AND IS THE WRONG CUT. Requiring two distinct work
        types keeps `LICENSE.txt` -- three generic words corroborate each other --
        and releases `Statement.pdf`, a real brokerage statement. Wrong in both
        directions. Of those 33 files exactly ONE carries its work type in a naming
        zone, and it is `Statement.pdf`. Zone separates them; count does not.

        `NAMING_ZONES` is SPEC 2.2's own ranking, which `_matches` already quotes
        for a different purpose, so this is the design's own rule read on the path
        that needed it -- not a threshold invented to fit one corpus.

        WHY ONLY THIS PATH, and this is the whole of the narrowing. The two other
        callers of the lenient question are asking something else:

        - `_precaution` reads an abstention's TIED LEADERS, so the safety domain
          already stood level with every other reading on the file's own terms.
          Its docstring says it gets `never_alone`'s discipline for free that way.
        - the corroboration gate in `_decide` uses it to keep a schema-agnostic
          identifier from seconding a word that merely accompanies a safety
          document. A passport scan whose OCR body reads "Passport. X12345678."
          must still be RECOGNISED, and narrowing that would buy an
          over-protection cure by making the safety domains unrecognisable --
          the trade `00` and this suite both forbid outright.

        The winning-schema override has neither of those. Its own comment says it
        "has no leaders to lean on and must say what it means directly." This is
        what it means directly.
        """
        matches, _ = self._matches(conn, file_id, content_hash)
        return tuple(sorted({
            reading for reading in in_evidence
            if any(match.schema_id == reading and _names_the_file(match)
                   and match.term in self._work_types.get(reading, frozenset())
                   for match in matches)}))

    def _protect_as(self, conn: sqlite3.Connection, readings: Iterable[str], *,
                    file_id: str, content_hash: str) -> ClassificationRecord | None:
        """The safety domain's own handling, cited to the terms that raised it."""
        if not readings:
            return None
        schema_id = min(readings, key=SCHEMA_IDS.index)
        handling = self._handling.get(schema_id)
        if handling is None:
            # The caller's policy states no class for this safety domain. `00`
            # supplies the FLAG and never the class, so inventing one here would
            # be this package authoring the design.
            return None
        # The evidence is the safety domain's own terms, not the whole file's:
        # a protection cites what raised it. `_matches` is re-run rather than
        # threaded through `Abstention`, which is a record of a RECOGNITION
        # decision and gains nothing by carrying a classification's citations.
        #
        # AND A DETERMINISTIC READING IS ONE OF THOSE CITATIONS (`00` amendment 7).
        # `_matches` refuses these rows -- rightly, they are not words the file said
        # -- so without this line a file held on a card number alone, or on a name
        # beside a diagnosis, reached the `if not refs` refusal below and came back
        # UNPROTECTED: the report said `medical`, the record said nothing, and §8.4's
        # flag that gates cloud egress stayed down. The one thing amendment 7 exists
        # to prevent, produced by the guard that exists to stop a classification
        # citing nothing.
        matches, _ = self._matches(conn, file_id, content_hash)
        refs: list[str] = []
        for match in (*matches, *self._deterministic_readings(
                conn, file_id, content_hash).get(schema_id, ())):
            if match.schema_id == schema_id and match.observation_key not in refs:
                refs.append(match.observation_key)
        if not refs:
            return None
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=handling.basis, evidence_refs=tuple(refs),
            reliability_state=RELIABILITY, observed_at=self._now())

    @staticmethod
    def _cited(by_schema: Mapping[str, list["TermMatch"]],
               schemas: Iterable[str]
               ) -> tuple[tuple[tuple[str, tuple[str, ...]], ...], tuple[str, ...]]:
        """`(matched_terms, evidence_refs)` for the readings an abstention names.

        A projection of matches the caller already holds. `SCHEMA_IDS` order for
        the schemas, found-order for the terms and the keys, and every key
        deduplicated -- one observation carrying two terms is one citation.
        """
        named = [schema_id for schema_id in SCHEMA_IDS if schema_id in set(schemas)]
        terms: list[tuple[str, tuple[str, ...]]] = []
        refs: list[str] = []
        for schema_id in named:
            found = by_schema.get(schema_id, ())
            terms.append((schema_id, tuple(dict.fromkeys(
                match.term for match in found))))
            for match in found:
                if match.observation_key not in refs:
                    refs.append(match.observation_key)
        return tuple(terms), tuple(refs)

    def _readings(self, schema_id: str) -> tuple[str, ...]:
        schema = self._rules.schemas.get(schema_id)
        return () if schema is None else schema.deferred_readings

    # --- the seam ------------------------------------------------------------

    def __call__(self, conn: sqlite3.Connection, file_id: str,
                 content_hash: str) -> ClassificationRecord | None:
        """`orchestrator.ClassificationProducer`. A candidate, or an abstention."""
        outcome = self.explain(conn, file_id, content_hash)
        if isinstance(outcome, Abstention):
            return self._precaution(conn, outcome, file_id=file_id,
                                    content_hash=content_hash)
        # A SCHEMA WON, AND THAT SETTLES ONLY WHAT WE CLAIM. Precaution was reached
        # through the abstention branch alone, so a file naming a safety domain was
        # protected when nothing described it and unprotected when something did --
        # and "another schema described this better" is not one of the exceptions
        # `00`:52 and `00`:185 allow. Measured before this guard existed: a passport
        # whose text said "scanned copy" matched `photos`, won outright, and was
        # stored `protected=0, auto_eligible` with its number offered as a folder.
        #
        # A safety domain that WON needs nothing here -- its own handling is already
        # the one below -- so this asks only about the domains that lost.
        handling = self._handling[outcome.schema_id]
        basis = handling.basis
        if outcome.schema_id not in SAFETY_DOMAIN_IDS:
            in_evidence = self._safety_readings_in_evidence(
                conn, file_id, content_hash)
            # THE REPORT DECIDES AND THIS WRITES THE RECORD, which is the shape
            # `_precaution` has had since `104` §18 gap 24 and is now this arm's
            # too (§18.26 gap 24b). The rule -- a work type of one of `00`'s four
            # in a naming zone -- did not move and is not spelled twice; what
            # moved is that `cli.ask_the_situation` can ask the same question of
            # the same file and be told the same answer.
            report = self.precaution_report(conn, outcome, file_id=file_id,
                                            content_hash=content_hash)
            protection = None if report is None else self._protect_as(
                conn, (report.schema_id,),
                file_id=file_id, content_hash=content_hash)
            if protection is not None:
                return protection
            # NOTHING SAFETY-RELATED WAS FOUND, AND SAYING SO IS THE POINT. `96` §19
            # measured what the previous line's silence cost: of 78 files stored
            # `personal_non_sensitive, protected=0`, 41 had matched no safety work
            # type at all -- among them a Hong Kong identity card read to 21
            # observations -- and every one of them left here carrying `detector`,
            # the same word as a file whose safety terms were examined and weighed.
            # §8.4 makes a handling class a precondition of a model call, so those
            # 41 went from "no class, door shut" to "ordinary class, door open"
            # without a single piece of evidence being gained.
            #
            # `96` §20's remedy, and its exact words: the precondition should be
            # satisfied by "evidence of having LOOKED, not merely by a class
            # existing". This is that distinction, which the detector could already
            # make and had no word for.
            #
            # THE RECOGNITION IS NOT IN DOUBT and nothing else moves. The schema won
            # on the file's own terms, the class is the deployment's, the protected
            # flag stays `False`, the evidence refs are the same. One field changes,
            # and it is SPEC §2's field for where a conclusion came from.
            #
            # An EMPTY tuple, not a falsy one: `in_evidence` is the lenient reading
            # -- any safety domain whose own WORK TYPE the file carries anywhere,
            # which is deliberately wider than the naming-zone rule two lines up. A
            # file that reaches here with a non-empty one was examined and released,
            # and that is a judgement worth the strong word.
            if not in_evidence:
                basis = DETECTOR_NO_SAFETY_EVIDENCE
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=basis, evidence_refs=outcome.evidence_refs,
            reliability_state=RELIABILITY, observed_at=self._now())

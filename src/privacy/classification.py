# src/privacy/classification.py
"""SPEC §2's classification record, and the resolution the design states twice.

"Absence of a classification resolves to `unreadable_unclassified`, never to
`public_low`." §8.6 gives the reason: "Cost exhaustion must never turn into
lower-quality automatic classification." The failure that sentence forbids is exactly
defaulting an unclassified file to public so the pipeline can continue, so there is no
default-to-public code path in this module or anywhere under `src/privacy/`.

**The record is authoritative and it is keyed on BYTES (D2).** `(file_id,
content_hash)` -- on the hash, because a classification is about the bytes, and new
bytes at a path are a new file version that inherits nothing.
`files.sensitivity_state` is this record's PROJECTION onto the current row, written
through P1's published `set_sensitivity_state`; that is Task 4's `mirror_state`, and
it is not here.

**`Unreadable or unclassified` is a GATE OUTCOME, not a file fact (D2), and this
module is where that becomes concrete.** `resolve_class` returns a string to a caller
and this file contains no writer at all: no function inserts or updates, no name
begins `set_`, `write_`, `record_`, `mirror_` or `update_`, and
`database_agent.files_table` is not imported. "Nothing has looked" and "this file
carries nothing" must never become the same value in the same column, and the durable
way to hold them apart is for the string meaning the first to be produced by a
decision function in a module that can reach no column.

`UNREADABLE_UNCLASSIFIED` is PUBLISHED rather than private. Task 4's store refuses it
on both sides of the projection -- as a stored row and as a `mirror_state` -- and a
refusal spelled with a literal in the module that enforces it would be a second home
for the one string this part must never store. The name is exported so the refusal
cites the same value `resolve_class` returns.

**No detector lives here (D2).** SPEC *Deferred*: "The design states *what* is
protected and never *how it is recognised*. The detector rule set, its signals, and
its thresholds are hand-authored. P7 publishes the vocabulary the detectors write
into." There is no regex, no gazetteer, no filename pattern and no keyword list.
`sensitivity_signal_keys` composes two readers P4 and P5 already publish and decides
nothing: it returns the citation handles a detector would pass as `evidence_refs`.
Until a detector is supplied, every real file resolves to `Denied(unclassified)` --
a correct, locked door with nobody holding a key, and the honest v1 posture.

**`105` §14.3's FOUR PRIVACY CLASSES ARE RESOLVED HERE AND RECOGNISED NOWHERE.**
`privacy_class_for` applies the owner's precedence -- protected, then always-local,
then ordinary -- over kind NAMES a detector already wrote, and `pending` is its
answer when the detector did not assess the file at all. That is a resolution over
`vocabulary`'s two closed lists, exactly as `resolve_class` is a resolution over the
five handling classes, and it adds no rule for recognising a receipt. The paragraph
above is unweakened: no regex, no gazetteer, no filename pattern, no keyword list.

**CLASSIFICATION PRECEDES THE MODEL CALL IT GOVERNS**, which is §14.3's fifth
sentence and a property of WHERE these functions are rather than of what they say. A
document is never sent to a model to discover its class: `privacy_class_for` reads
names and `privacy_class_of` reads a stored record, neither opens a file, and this
module imports no model client and no transport. The gate asserts the ordering it
depends on rather than assuming it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.observation import is_observation_key
from evidence_shape.store import runs_for_file

from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    CLASSIFICATION_BASES, DETECTOR as _DETECTOR,
    DETECTOR_NO_SAFETY_EVIDENCE as _DETECTOR_NO_SAFETY_EVIDENCE,
    LOCAL_MODEL_SITUATION as _LOCAL_MODEL_SITUATION,
    PRIVACY_CLASS_BY_KIND, PRIVACY_CLASS_ORDINARY,
    PRIVACY_CLASS_PENDING, PRIVACY_CLASS_PROTECTED, PRIVACY_CLASSES,
    OutOfVocabulary, check_handling_class, check_privacy_class,
)

#: SPEC §2's eight, in SPEC §2's order, and `105` §14.3's ninth after them.
#:
#: The ninth is LAST and outside the SPEC's order on purpose: the eight are the
#: design's own record and their sequence is quotable, while `privacy_class` is the
#: owner's 7 Sep 2026 addition. Appending keeps the first eight readable as the
#: SPEC's list rather than blending a later field into it.
CLASSIFICATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at", "privacy_class",
)

#: §8.4's fifth class, validated against Task 2's closed vocabulary at import: a
#: rename there becomes an ImportError here rather than a string that silently stops
#: matching. A value this module RETURNS and never stores, and Task 4's store refuses
#: it under this name rather than retyping the literal.
UNREADABLE_UNCLASSIFIED: str = check_handling_class("unreadable_unclassified")

#: The bases §8.4's "evidence-backed" binds. `user` needs no evidence -- the user's
#: act is the evidence -- and `safety_domain` is §3.15's rule about a domain, not a
#: reading of a span.
#:
#: BOTH DETECTOR BASES, and the second is here for the same reason as the first.
#: `detector_no_safety_evidence` is weaker about SAFETY and not weaker about
#: recognition: the schema still won on the file's own terms, and those terms are
#: what the record cites. A record on it carrying nothing would be the detector
#: asserting an ordinary class out of thin air, which is exactly what `96` §19
#: objected to -- so the weaker word must not become the way to skip the citation.
#: THE FIFTH BASIS IS HERE TOO, and it is the strictest case rather than a new
#: exemption. `00`:42 -- "A model that cannot cite sufficient evidence must return
#: unknown" -- means an uncited situation answer is not a record with no evidence;
#: it is an `unknown`, and an `unknown` writes no record at all
#: (`model_situation`). So a `local_model_situation` row that reached this
#: constructor with an empty `evidence_refs` is a wiring defect, and it is refused
#: here rather than stored as a model conclusion nobody can trace.
_EVIDENCE_REQUIRED_BASES: frozenset[str] = frozenset(
    {_DETECTOR, _DETECTOR_NO_SAFETY_EVIDENCE, _LOCAL_MODEL_SITUATION})



class UnbackedClassification(ValueError):
    """§8.4: the classification "is itself evidence-backed".

    Raised when a `detector` classification carries no evidence, when a reference is
    not a P4 `observation_key` (M14), or when a field of the record is not the kind of
    value §8.2 can preserve.
    """


#: M14's citation handle, shaped by asking P4 rather than by hard-coding a pattern.
#: The predicate lives beside the function that mints a key
#: (`evidence_shape.observation.is_observation_key`); P7 asks it, and so does the
#: module that decides which references may go to a model.
_is_observation_key = is_observation_key


@dataclass(frozen=True, slots=True)
class ClassificationRecord:
    """One handling class for one file VERSION. D2 makes this record authoritative.

    `protected` is supplied and never derived: SPEC §2, "Neighbouring parts should
    consume the `protected` flag, not infer it from the class", and Open question 1 --
    whether `protected` is exactly the top two classes -- is unsettled.

    `reliability_state` is P4's vocabulary (§3.13's six, shipped as
    `evidence_shape.vocabulary.RELIABILITY_STATES` and re-exported by Task 2) and is
    stored, not validated: Task 4 publishes the ordering and the `strongest`
    resolution over it, and two validators would be two vocabularies.
    """

    file_id: str
    content_hash: str
    handling_class: str
    protected: bool
    basis: str
    evidence_refs: tuple[str, ...]
    reliability_state: str
    observed_at: str
    #: `105` §14.3's privacy class for these bytes: `protected`, `always_local` or
    #: `ordinary`. NEVER `pending` -- the store refuses it on both sides of the
    #: projection, exactly as it refuses `unreadable_unclassified`, because the
    #: owner's ruling makes `pending` the reading of NO RECORD and a stored row
    #: saying it would claim as a fact what the absence of a row already says.
    #:
    #: **IT HAS A DEFAULT AND THE OTHER EIGHT DO NOT. Read this before copying the
    #: pattern.** A default in this package is normally the silent downgrade §8.6
    #: forbids by name, and every other required keyword in `check_item` exists to
    #: stop one. The argument for this one is narrow and it expires.
    #:
    #: A silent downgrade is a class the file HAD being replaced by a weaker one.
    #: Nothing in this product recognises a §13.3 document kind: `recognition/
    #: detector.py` works over `facts.domains.SCHEMA_IDS`, which are twenty-three
    #: DOMAINS -- academic, finance, medical -- and not kinds like `receipt` or
    #: `boarding_pass_or_ticket`. So a record written today has no restricted kind
    #: to be downgraded FROM, and `ordinary` is the accurate reading of what was
    #: assessed: §13.3's own "A kind on neither list is ordinary."
    #:
    #: The guard is at the WRITER instead, where it can work: a detector names a
    #: restricted kind through `vocabulary.check_restricted_kind` or one of the ten
    #: constants beside the lists, so a misspelling is a `NameError` there rather
    #: than an ordinary file three modules away.
    #:
    #: **THE DAY A KIND RECOGNIZER SHIPS, THIS DEFAULT IS WRONG** -- it would then be
    #: a real class being replaced by a weaker one, which is the failure this
    #: paragraph argues it is not. `tests/p7/test_p7_privacy_classes.py`'s
    #: `test_the_default_is_ordinary_and_this_is_the_condition_that_retires_it`
    #: pins it and names that condition.
    privacy_class: str = PRIVACY_CLASS_ORDINARY

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "reliability_state", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise UnbackedClassification(
                    f"{name} must be a non-empty string; §8.2 preserves a record and "
                    f"cannot preserve {value!r}")
        check_handling_class(self.handling_class)
        check_privacy_class(self.privacy_class)
        if self.privacy_class == PRIVACY_CLASS_PENDING:
            raise UnbackedClassification(
                f"{PRIVACY_CLASS_PENDING!r} is the reading of NO RECORD (`105` "
                "§14.3) and cannot be a field of one. A row saying it would claim, "
                "as a fact, exactly what the absence of a row already says -- and "
                "the two would then be able to disagree. This is D2's argument for "
                f"{UNREADABLE_UNCLASSIFIED!r}, one column along.")
        if self.basis not in CLASSIFICATION_BASES:
            raise OutOfVocabulary(
                f"basis {self.basis!r} is not one of {CLASSIFICATION_BASES}. P6's "
                "five §3.1 `origin` values are a different vocabulary and are never "
                "mapped onto this one.")
        if not isinstance(self.protected, bool):
            raise UnbackedClassification(
                f"protected is §8.4's flag and is a boolean, not {self.protected!r}. "
                "It is supplied by the caller and never derived from the handling "
                "class (SPEC §2, Open question 1).")
        refs = self.evidence_refs
        if isinstance(refs, str) or not isinstance(refs, Sequence):
            raise UnbackedClassification(
                "evidence_refs is a sequence of P4 observation keys; a bare string "
                f"would become {len(refs) if isinstance(refs, str) else 0} "
                "one-character references")
        refs = tuple(refs)
        object.__setattr__(self, "evidence_refs", refs)
        if self.basis in _EVIDENCE_REQUIRED_BASES and not refs:
            raise UnbackedClassification(
                f"a basis={self.basis!r} classification carries no evidence. §8.4: "
                "the classification 'is itself evidence-backed', on §3.1's principle "
                "that every fact preserves where it came from.")
        for ref in refs:
            if not _is_observation_key(ref):
                raise UnbackedClassification(
                    f"{ref!r} is not a P4 observation_key. M14: 'The key, not the id, "
                    "is what makes that durable' -- a per-row observation_id dies on "
                    "extractor upgrade, so a negative example recorded today would "
                    "silently stop resolving and the same false protection would "
                    "return.")


def resolve_class(record: ClassificationRecord | None) -> str:
    """The handling class a caller must treat this file version as carrying.

    A GATE OUTCOME (D2), returned to a caller and stored by nothing here. Absence
    resolves to `unreadable_unclassified` and never to `public_low` (SPEC §1, §8.4,
    §8.6): a file that has not been classified has not met §8.4's precondition for
    escalation -- "classify data into handling classes before LLM escalation" -- and
    the gate denies it rather than guessing at it downward.
    """
    if record is None:
        return UNREADABLE_UNCLASSIFIED
    if not isinstance(record, ClassificationRecord):
        raise TypeError(
            f"resolve_class takes a ClassificationRecord or None, not "
            f"{type(record).__name__}. A mapping that looks like one has not been "
            "through the evidence-backed check.")
    return record.handling_class


#: Per value, with the sentence that decides it, for each of P4's nine
#: `completeness` markings. Stated one at a time rather than as a membership test over
#: a set, because the set is what an author guesses and the sentences are what the
#: design says. Six imply unclassified; they are P4's own
#: ZERO_OBSERVATION_COMPLETENESS plus `unreadable`, and the test cross-checks that.
COMPLETENESS_RULE: Mapping[str, tuple[bool, str]] = MappingProxyType({
    "complete": (False,
        "The run finished on its own terms and the content was read. Whether a "
        "classification EXISTS is a separate question this function does not answer."),
    "capped": (False,
        "§2.7 requires that 'whether extraction was complete or capped' be preserved. "
        "Capped text exists and a detector can read it."),
    "partial": (False,
        "§2.5's 'partially inspected'. M3 keeps the metadata-level rows on a partial "
        "run, so content was read."),
    "metadata_only": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the stopping extractor emits nothing "
        "and the file stays indexed through its filesystem observations. No content "
        "was read, so no evidence-backed classification is possible."),
    "deferred": (True,
        "§8.6: 'If the budget is exhausted, the product should retain extracted "
        "evidence, mark the deferred stage, and leave the file or group in review "
        "rather than guessing.' The stage did not run."),
    "unsupported": (True,
        "§2.4: 'an empty extraction result is different from an extractor that does "
        "not yet exist.' No extractor looked, so nothing was seen."),
    "unreadable": (True,
        "§2.9: 'unsupported proprietary formats should be recorded as "
        "indexed-but-unreadable rather than silently treated as empty.' The SPEC maps "
        "an unreadable extraction result to this handling class by name."),
    "failed": (True,
        "In P4's ZERO_OBSERVATION_COMPLETENESS: the run did not complete and emitted "
        "nothing."),
    "dataless": (True,
        "11 §5: 'Do not materialize, hash, or extract.' C4: nothing was opened, so "
        "nothing was seen. The bytes are elsewhere and the row records that."),
})


def completeness_implies_unclassified(completeness: object) -> bool:
    """Whether a run at this marking leaves the file with nothing to classify.

    True does not mean the class was WRITTEN -- nothing writes it, and D2 forbids
    `unreadable_unclassified` from reaching `files.sensitivity_state`. It means no
    content was read, so no evidence-backed classification is possible and the gate's
    resolution for this file version is `unreadable_unclassified`.
    """
    try:
        implies, _ = COMPLETENESS_RULE[completeness]
    except (KeyError, TypeError):
        raise OutOfVocabulary(
            f"{completeness!r} is not one of P4's nine completeness markings "
            f"{tuple(COMPLETENESS_RULE)}. There is no marking literally named "
            "'indexed-but-unreadable': §2.9's phrase is spelled `unreadable`."
        ) from None
    return implies


def sensitivity_signal_keys(conn: sqlite3.Connection,
                            file_id: str) -> tuple[str, ...]:
    """P4 observation keys P5 marked "potentially sensitive" for this file.

    A detector INPUT and not a detector. It applies no rule, assigns no class and
    returns no value: only the citation handles a detector would pass as
    `evidence_refs`. P5's own docstring is explicit about who it is for -- "Email
    addresses, message content and every VCF value are marked POTENTIALLY SENSITIVE at
    emission, for P7 to act on. P5 assigns no handling class: section 8.4 gives
    classification to P7."

    P5's reader is keyed by `run_id` only, so this is the file-level walk P7 composes
    from the two readers P4 and P5 already publish; P7 adds no reader to P5. Keys are
    deduplicated in first-seen order, because a re-run of the same extractor at the
    same content hash produces the same key (MINOR 8) and listing it twice would make
    one observation look like two.
    """
    seen: dict[str, None] = {}
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                seen.setdefault(row["observation_key"], None)
    return tuple(seen)


# --- `105` §14.3: the four privacy classes, and the precedence between them ---


def privacy_class_for(kinds: Sequence[str] | None) -> str:
    """The privacy class the recognised document kinds of a file resolve to.

    THE OWNER'S RULING OF 7 SEPTEMBER 2026 (`105` §14.3): "Keep both lists, apply the
    most restrictive matching rule to the content and its derivatives regardless of
    file format, and classify unresolved cases as pending rather than ordinary."

    `kinds` is what a detector RECOGNISED, and the two arguments are different
    questions rather than two spellings of one:

      `None`  -- the detector did not assess this file. `pending`.
      `()`    -- the detector assessed it and matched no restricted kind. `ordinary`.

    §14.3 is explicit that those two must not collapse: "'On neither list'
    distinguishes an assessed ordinary document from one the detector failed to
    recognise, which is pending." The empty tuple is the whole of the distinction and
    it is why this function takes an optional sequence rather than a set.

    **PRECEDENCE, AND IT IS APPLIED TO THE CONTENT AND NOT TO THE FORMAT.** Protected
    beats always-local beats ordinary, so a file matching two lists takes the more
    restrictive one. A screenshot of a bank statement is protected although account
    screenshots are always-local; a receipt containing credentials is protected. Both
    are the owner's own examples, both arrive here as two kinds on one file, and the
    tuple order in `PRIVACY_CLASSES` is what decides them.

    **THIS RECOGNISES NOTHING.** SPEC *Deferred*: "The design states *what* is
    protected and never *how it is recognised*." It reads kind NAMES a detector
    already wrote and holds no regex, no keyword and no threshold; a caller that
    passed the wrong names gets the wrong class and this function cannot tell.

    An unrecognised kind name is ORDINARY and not an error, because §13.3 rules it so
    -- "A kind on neither list is ordinary" -- and because the universe of document
    kinds is open while the two restricted lists are closed. The guard against a
    misspelling is at the WRITER: `vocabulary.check_restricted_kind` and the ten
    named constants beside the lists, so a detector naming a restricted kind spells
    it once and a typo is a `NameError` there rather than a silent downgrade here.
    """
    if kinds is None:
        return PRIVACY_CLASS_PENDING
    if isinstance(kinds, str):
        raise TypeError(
            f"privacy_class_for takes a sequence of kind names or None, not the "
            f"bare string {kinds!r}, which would be read as "
            f"{len(kinds)} one-character kinds and resolve to 'ordinary'. `None` "
            "means the detector did not assess the file; an empty sequence means it "
            "assessed it and matched nothing.")
    if not isinstance(kinds, Sequence):
        raise TypeError(
            f"privacy_class_for takes a sequence of kind names or None, not "
            f"{type(kinds).__name__}. The distinction between 'assessed and matched "
            "nothing' and 'not assessed' is the empty sequence against `None`, and a "
            "type with no empty form cannot carry it.")
    found = {PRIVACY_CLASS_BY_KIND[kind] for kind in kinds
             if kind in PRIVACY_CLASS_BY_KIND}
    for privacy_class in PRIVACY_CLASSES:
        if privacy_class in found:
            return privacy_class
    return PRIVACY_CLASS_ORDINARY


def derivative_privacy_class(source_class: str) -> str:
    """The class an OCR text, an extracted excerpt or a summary carries.

    `105` §14.3: "OCR text, excerpts and summaries retain the source's restriction."
    So this returns the source's class unchanged, and the point of it being a
    function rather than an assumption is that the inheritance is then something a
    caller performs and a test can watch, instead of a property everyone believes.

    A released excerpt of a protected file is impossible; an excerpt of an
    always-local file is local only. Neither is a new rule about excerpts -- it is
    the file's own rule, arriving with the derivative.

    **THE FORMAT NEVER WEAKENS IT.** "regardless of file format" is in the ruling's
    own sentence: OCR read off a photograph of a tax return carries the tax return's
    restriction, and text extracted from a screenshot of a bank statement carries the
    bank statement's. A derivative is a second copy of the content, so the way a
    restriction is lost is by the copy being treated as a new thing with no history.

    There is deliberately no downgrade parameter and no second argument. A caller
    that wanted a derivative to be less restricted than its source would be asking
    this function for permission it cannot give.
    """
    return check_privacy_class(source_class)


def privacy_class_of(record: ClassificationRecord | None) -> str:
    """The privacy class a file VERSION carries, read off its classification record.

    Absence is `pending`, on the same argument `resolve_class` makes for
    `unreadable_unclassified` and never `public_low`: no record means nothing has
    assessed these bytes, and §14.3 rules an unassessed file pending rather than
    ordinary. The two answers agree by construction -- a file this returns `pending`
    for is exactly a file `resolve_class` returns `unreadable_unclassified` for --
    which is what lets `pending` be "treated like unclassified for every gate"
    without a second rule anywhere.

    **THE RECORD'S OWN FIELD, AND NOT THE `protected` FLAG.** The two are different
    questions and the owner ruled on 7 Sep 2026 that they stay different: the flag is
    §8.4's, it keeps §8.4's consent path exactly as it is, and a granted local scope
    still releases a flagged file. The class is §13.3's, it is about the document's
    recognised KIND, and a protected-kind file is shown to no model at all. So the
    two sets differ in both directions -- a file can be on the protected list without
    the flag, and carry the flag without being on the list -- and this function reads
    the field rather than deriving it from the flag, or the two could never disagree.

    SPEC §2's "Neighbouring parts should consume the `protected` flag, not infer it
    from the class" is untouched by that, and so is Open question 1. Nothing here
    reads `handling_class`.
    """
    if record is None:
        return PRIVACY_CLASS_PENDING
    if not isinstance(record, ClassificationRecord):
        raise TypeError(
            f"privacy_class_of takes a ClassificationRecord or None, not "
            f"{type(record).__name__}. A mapping that looks like one has not been "
            "through the evidence-backed check, and `None` here means something "
            "stronger than a missing argument: it means nothing assessed the bytes.")
    return record.privacy_class

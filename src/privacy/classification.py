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
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.observation import observation_key
from evidence_shape.store import runs_for_file

from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import (
    CLASSIFICATION_BASES, OutOfVocabulary, check_handling_class,
)

#: SPEC §2's eight, in SPEC §2's order.
CLASSIFICATION_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)

#: §8.4's fifth class, validated against Task 2's closed vocabulary at import: a
#: rename there becomes an ImportError here rather than a string that silently stops
#: matching. A value this module RETURNS and never stores, and Task 4's store refuses
#: it under this name rather than retyping the literal.
UNREADABLE_UNCLASSIFIED: str = check_handling_class("unreadable_unclassified")

#: The one basis §8.4's "evidence-backed" binds. `user` needs no evidence -- the
#: user's act is the evidence -- and `safety_domain` is §3.15's rule about a domain,
#: not a reading of a span.
_EVIDENCE_REQUIRED_BASIS: str = "detector"

#: M14's citation handle, shaped by asking P4 rather than by hard-coding a pattern.
#: One probe key at import yields the algorithm prefix and the digest width, so a
#: change in `evidence_shape.canonical.sha256_of` propagates instead of drifting.
_PROBE_KEY: str = observation_key(
    content_hash="", extractor_name="", locator="", raw_value="")
_KEY_PREFIX, _, _KEY_DIGEST = _PROBE_KEY.partition(":")
_HEX = frozenset("0123456789abcdef")


class UnbackedClassification(ValueError):
    """§8.4: the classification "is itself evidence-backed".

    Raised when a `detector` classification carries no evidence, when a reference is
    not a P4 `observation_key` (M14), or when a field of the record is not the kind of
    value §8.2 can preserve.
    """


def _is_observation_key(value: object) -> bool:
    """P4's content-addressed handle, never the per-row `observation_id` (M14).

    `evidence_shape.store.new_id()` mints `str(uuid.uuid4())` and P1's `content_hash`
    carries no algorithm prefix, so both are rejected by shape rather than by policy.
    """
    if not isinstance(value, str):
        return False
    prefix, separator, digest = value.partition(":")
    if not separator or prefix != _KEY_PREFIX or len(digest) != len(_KEY_DIGEST):
        return False
    return all(character in _HEX for character in digest)


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

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "reliability_state", "observed_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise UnbackedClassification(
                    f"{name} must be a non-empty string; §8.2 preserves a record and "
                    f"cannot preserve {value!r}")
        check_handling_class(self.handling_class)
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
        if self.basis == _EVIDENCE_REQUIRED_BASIS and not refs:
            raise UnbackedClassification(
                f"a basis={_EVIDENCE_REQUIRED_BASIS!r} classification carries no "
                "evidence. §8.4: the classification 'is itself evidence-backed', on "
                "§3.1's principle that every fact preserves where it came from.")
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

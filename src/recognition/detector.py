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

import sqlite3
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import PurePath
from types import MappingProxyType

from database_agent.files_table import get_file

from facts.domains import SCHEMA_IDS, UnknownSchema

from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.classification import UnbackedClassification
from privacy.vocabulary import CLASSIFICATION_BASES, OutOfVocabulary
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


@dataclass(frozen=True, slots=True)
class TermMatch:
    """One authored term, found in one observation, owned by one schema."""

    schema_id: str
    term: str
    observation_key: str


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
    """

    reason: str
    schema_id: str | None
    detail: str
    tied_schema_ids: tuple[str, ...] = ()
    deferred_readings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_abstention_reason(self.reason)
        if self.schema_id is not None and self.schema_id not in SCHEMA_IDS:
            raise UnknownSchema(self.schema_id)


def _tokens(text: str) -> tuple[str, ...]:
    """Words, case-folded. Everything that is not a letter or digit separates.

    Not a regex: `str.isalnum` over code points is the same rule stated in the one
    place it is applied, and P7's own package is forbidden from importing `re` for
    exactly the reason that a pattern is a detection rule wearing a library's face.
    Applied identically to the rule side at compile time and to the evidence side
    here, so `problem set` and `Problem  Set,` are one term and one match.
    """
    out: list[str] = []
    current: list[str] = []
    for character in text:
        if character.isalnum():
            current.append(character)
        elif current:
            out.append("".join(current).casefold())
            current = []
    if current:
        out.append("".join(current).casefold())
    return tuple(out)


class Detector:
    """The compiled rules, applied to one file version's own P4 observations."""

    def __init__(self, rules: RecognitionRules, *,
                 handling_for: Mapping[str, Handling],
                 now: Callable[[], str],
                 is_protected: Callable[[PurePath], bool] | None = None) -> None:
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
        """
        found: list[TermMatch] = []
        source_types: set[str] = set()
        seen: set[tuple[str, str]] = set()
        for row in conn.execute(
                "SELECT observation_key, raw_value, normalized_value, source_type "
                "FROM evidence WHERE file_id = ? AND content_hash = ? "
                "AND superseded_by IS NULL ORDER BY rowid",
                (file_id, content_hash)):
            source_types.add(row["source_type"])
            key = row["observation_key"]
            for text in (row["raw_value"], row["normalized_value"]):
                if not text:
                    continue
                for term, owners in self._terms_in(text):
                    for schema_id in owners:
                        if (schema_id, term) in seen:
                            continue
                        seen.add((schema_id, term))
                        found.append(TermMatch(schema_id=schema_id, term=term,
                                               observation_key=key))
        return found, source_types

    def _terms_in(self, text: str) -> Iterable[tuple[str, tuple[str, ...]]]:
        """Authored terms present in this text as whole-word phrases."""
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
            return Abstention("no_evidence", None,
                              f"{file_id} carries no term any schema authored")

        by_schema: dict[str, list[TermMatch]] = {}
        for match in matches:
            by_schema.setdefault(match.schema_id, []).append(match)
        best = max(len(found) for found in by_schema.values())
        leaders = sorted(
            schema_id for schema_id, found in by_schema.items()
            if len(found) == best)

        # `never_alone`, read literally. One term is one signal and one signal
        # never activates a schema, whichever schema it is.
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
            return Abstention(
                "no_corroboration", schema_id,
                f"{schema_id} matched one authored term "
                f"({by_schema[schema_id][0].term!r}) and every node row carries a "
                "`never_alone` rule; one signal does not activate a schema"
                + (f". {len(leaders)} readings matched one term each and none "
                   f"outranks another ({', '.join(leaders)})"
                   if len(leaders) > 1 else ""),
                tied_schema_ids=tuple(leaders) if len(leaders) > 1 else (),
                deferred_readings=self._readings(schema_id))

        plausible = [schema_id for schema_id in leaders
                     if self._plausible(self._rules.schemas[schema_id],
                                        extension=file_row["extension"],
                                        source_types=source_types)]
        if not plausible:
            schema_id = leaders[0]
            return Abstention(
                "file_kind_implausible", schema_id,
                f"{schema_id} matched {best} authored terms on a file kind its "
                f"rows never name ({file_row['extension']!r}, "
                f"{sorted(source_types)}); `file_kind_plausible` is a constraint "
                "and never a signal",
                deferred_readings=self._readings(schema_id))
        if len(plausible) > 1:
            # `00` requires abstention where two readings are both supported.
            # Nothing breaks this tie: a tie-breaker would be the invented
            # threshold this package exists without.
            return Abstention(
                "ambiguous", None,
                f"{len(plausible)} schemas are supported by {best} authored terms "
                f"each ({', '.join(plausible)}); both readings are supported and "
                "`00` requires abstention rather than a winner",
                tied_schema_ids=tuple(plausible),
                deferred_readings=self._readings(plausible[0]))

        schema_id = plausible[0]
        found = tuple(by_schema[schema_id])
        if schema_id not in self._handling:
            # Recognised and not classified, which are two different things.
            # `planning/domains/_CONTRACT.md` rule 5 forbids the research from
            # carrying a handling class, and `00` states one for no ordinary
            # domain, so this is the honest end of the road rather than a class
            # picked to let the pipeline continue.
            return Abstention(
                "unassigned_handling", schema_id,
                f"{schema_id} was recognised from {len(found)} authored terms and "
                "the caller's handling policy states no class for it; recognition "
                "is not classification",
                deferred_readings=self._readings(schema_id))
        refs: list[str] = []
        for match in found:
            if match.observation_key not in refs:
                refs.append(match.observation_key)
        return Recognition(schema_id=schema_id, matches=found,
                           evidence_refs=tuple(refs))

    def _readings(self, schema_id: str) -> tuple[str, ...]:
        schema = self._rules.schemas.get(schema_id)
        return () if schema is None else schema.deferred_readings

    # --- the seam ------------------------------------------------------------

    def __call__(self, conn: sqlite3.Connection, file_id: str,
                 content_hash: str) -> ClassificationRecord | None:
        """`orchestrator.ClassificationProducer`. A candidate, or an abstention."""
        outcome = self.explain(conn, file_id, content_hash)
        if isinstance(outcome, Abstention):
            return None
        handling = self._handling[outcome.schema_id]
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=handling.basis, evidence_refs=outcome.evidence_refs,
            reliability_state=RELIABILITY, observed_at=self._now())

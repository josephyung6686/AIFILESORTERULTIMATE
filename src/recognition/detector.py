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
                 is_protected: Callable[[PurePath], bool] | None = None,
                 corroborating_observations: Callable[
                     [sqlite3.Connection, str, str], Iterable[str]] | None = None,
                 settled_by_user: Callable[[], Iterable[str]] | None = None
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
        seen: set[tuple[str, str]] = set()
        for row in conn.execute(
                "SELECT observation_key, raw_value, normalized_value, source_type, "
                "location FROM evidence WHERE file_id = ? AND content_hash = ? "
                "AND superseded_by IS NULL ORDER BY rowid",
                (file_id, content_hash)):
            # The file KIND is a property of the file and not of the observation
            # that named it, so this is read before the refusal below: narrowing
            # which words count must not narrow `file_kind_plausible` as well.
            source_types.add(row["source_type"])
            if _json.loads(row["location"]).get("locator") == "path":
                continue
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
            matched_keys = {match.observation_key for match in matches}
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
                    key not in matched_keys for key in
                    self._corroborating(conn, file_id, content_hash)):
                best = 2

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
        that abstention before reading any evidence, so `_matches` below is
        reached only for a file that was already open to being read.
        """
        if outcome.reason == "protected_container":
            return None
        # A tied LEADER, and a term that says what the file IS. The leader test was
        # always here; the second half arrived with the outright-win branch and
        # belongs to both, because a tie is not evidence about which KIND of term
        # matched. Without it `finance`'s context term `statement` tied on a college
        # personal statement and marked it `sensitive_personal, protected=1`.
        says_what_it_is = set(self._safety_readings_in_evidence(
            conn, file_id, content_hash))
        readings = [schema_id for schema_id
                    in (outcome.schema_id, *outcome.tied_schema_ids)
                    if schema_id in SAFETY_DOMAIN_IDS and schema_id in says_what_it_is]
        if not readings:
            return None
        # `SCHEMA_IDS` order, so two safety readings resolve the same way twice
        # rather than by whichever the abstention happened to name first.
        return self._protect_as(conn, readings, file_id=file_id,
                                content_hash=content_hash)

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
        the word "statement". `cli.py:210` names that outcome in the file this guard
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
        """
        matches, _ = self._matches(conn, file_id, content_hash)

        def says_what_the_file_is(match: "TermMatch") -> bool:
            return match.term in self._work_types.get(match.schema_id, frozenset())

        return tuple(sorted({match.schema_id for match in matches
                             if match.schema_id in SAFETY_DOMAIN_IDS
                             and says_what_the_file_is(match)}))

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
        matches, _ = self._matches(conn, file_id, content_hash)
        refs: list[str] = []
        for match in matches:
            if match.schema_id == schema_id and match.observation_key not in refs:
                refs.append(match.observation_key)
        if not refs:
            return None
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=handling.basis, evidence_refs=tuple(refs),
            reliability_state=RELIABILITY, observed_at=self._now())

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
        if outcome.schema_id not in SAFETY_DOMAIN_IDS:
            protection = self._protect_as(
                conn,
                self._safety_readings_in_evidence(conn, file_id, content_hash),
                file_id=file_id, content_hash=content_hash)
            if protection is not None:
                return protection
        handling = self._handling[outcome.schema_id]
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling.handling_class, protected=handling.protected,
            basis=handling.basis, evidence_refs=outcome.evidence_refs,
            reliability_state=RELIABILITY, observed_at=self._now())

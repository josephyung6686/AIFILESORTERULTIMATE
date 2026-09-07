# src/facts/course_alias.py
"""`104` R-135 -- the course alias table: the code an anchor document states beside a
course's own name, and the resolution of a title into that code.

**The defect this exists for, measured.** On the owner's corpus, `d409f58`: of 43
labelled course codes, 2 were right, 22 wrong and 19 missing, and 19 of the 22 wrong
were the course's TITLE, or a single department word, recorded where the label expects
the code. The syllabus states both spellings on one line -- `COMS W3134: Data
Structures` -- so the corpus already contains the mapping the product was guessing at.
Nothing here invents it: an alias row exists only because one anchor document printed a
code and a name together, and the row cites the observation that read it.

**Three properties, and each one is a refusal somewhere else in this file.**

* *An alias is read from the document, never from the file's name.* The build side takes
  only readings the caller's `reads_in_document` predicate admits -- in this deployment
  `cli.reads_a_structured_string`, a SPAN inside a text zone, which excludes `filename`,
  `path`, `title` and every `metadata:*` zone by construction. A folder called `Data
  Structures` is what the product is trying to EXPLAIN; letting it define the alias would
  make the explanation circular.
* *An anchor is a document that is teaching the course, not one that mentions it.* The
  gate is `facts.rules.context_check` over the caller's anchor terms -- the same
  predicate and the same implementation §3.5 uses, so "the line was in a syllabus" is
  established the one way this codebase establishes it. `facts` authors no term here, for
  the reason `facts.rules` states about its own five: every other domain's vocabulary
  arrives on the caller's object.
* *Two spellings of one code are one course; two codes under one title are neither.* The
  discriminator is the ANCHOR. `COMS W3134`, `W3134` and a second code printed on the
  same anchor line are spellings of one course, which is `104` R-91's split
  (`CS3134`/`W3134`) closed at its source. The same title read from two DIFFERENT anchor
  versions naming two different codes is `AMBIGUOUS`, and the reason names both.

**What this module does not do.** It writes no `subject` fact it cannot cite twice --
once for the file's own reading and once for the anchor that supplied the code. It never
supersedes a `subject` fact another producer already wrote: `file_facts` has no
uniqueness constraint over (file_id, content_hash, field_key), and the failure of two
live facts in one field is the one the removed term slot was deleted over. And it holds
no pattern, no term, no bound and no number of its own -- every one of them is the
caller's, exactly as `Rule` takes its three.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Callable

from evidence_shape.canonical import sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import check

from facts.cache import pass_cache_key
from facts.evidence import cite, context_pair, observations_for_version
from facts.file_facts import RULE, facts_for_file, write_fact
from facts.rules import context_check
from facts.schema import COURSE_ALIASES_TABLE
from facts.states import VALIDATED
from facts.unresolved import NORMALIZATION_FAILED, RULE_ROUTE, write_unresolved
from facts.values import VALUE_ORIGINS, add_raw_variant, ensure_value

__all__ = [
    "ALIAS_KINDS",
    "AMBIGUOUS",
    "BARE_WORD",
    "CODE_SPELLING",
    "CourseAliases",
    "NAMED",
    "SUBJECT_OUTCOMES",
    "SubjectReading",
    "TITLE_ALIAS",
    "UNKNOWN",
    "build_course_aliases",
    "load_course_aliases",
    "resolve_subject_facts",
]

#: The two kinds of alias row, one named constant each. A TITLE is the course's own name
#: as the anchor printed it; a SPELLING is another way of writing the same CODE. They are
#: not interchangeable and the difference is load-bearing: two titles pointing at two
#: codes is an ambiguity, while two spellings pointing at one code is R-91's fix.
TITLE_ALIAS: str = "title"
CODE_SPELLING: str = "spelling"

#: The two above, for iteration and membership. To name one kind, import the constant.
ALIAS_KINDS: tuple[str, str] = (TITLE_ALIAS, CODE_SPELLING)

#: The four answers `CourseAliases.resolve` can give about a proposed subject value.
#: `NAMED` carries a code; the other three carry a reason and no code, and the two
#: REFUSALS carry the evidence that justifies refusing.
NAMED: str = "named"
UNKNOWN: str = "unknown"
AMBIGUOUS: str = "ambiguous"
BARE_WORD: str = "bare_word"

#: The four above, checked on every `SubjectReading` so a typo raises `NotInVocabulary`
#: rather than being returned. P6's own closed vocabularies are checked through P4's
#: `check`, and this is one.
SUBJECT_OUTCOMES: tuple[str, str, str, str] = (NAMED, UNKNOWN, AMBIGUOUS, BARE_WORD)


def _collapsed(text: str) -> str:
    """One spelling of "whitespace is not part of a value", used on both sides.

    `PHYS  1401` off a two-column page and `PHYS 1401` off a heading are one reading,
    and `cli.normalize_for_model` already collapses the same way. A second rule here
    would be `65` §4.2's several-spellings failure arriving through this table.
    """
    return " ".join(text.split())


def _fold(text: str) -> str:
    """The lookup key: collapsed and case-folded.

    A title is stored as the anchor PRINTED it (§2.8: "the raw observation remains
    exactly that wording") and matched case-insensitively, because the same course name
    reaches this table from a heading in title case and from a filename in lower case,
    and treating those as two courses is the failure the whole module exists to stop.
    """
    return _collapsed(text).casefold()


@dataclass(frozen=True, slots=True)
class SubjectReading:
    """One answer about one proposed `subject` value, with the evidence behind it.

    `reason` is a SENTENCE built at the call site, not a member of a vocabulary. P6's
    `unresolved` reasons are a closed thirteen and §3.6's check reasons are P8's; a
    fifth refusal word invented here would be this module adding to a vocabulary it does
    not own. What names the ambiguity is `evidence_refs`, which carries BOTH anchors'
    observation keys, so a reader of the refusal can see the two lines that disagreed.
    """

    outcome: str
    code: str | None
    reason: str | None
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.outcome, SUBJECT_OUTCOMES, name="subject outcome")


@dataclass(frozen=True, slots=True)
class CourseAliases:
    """One corpus's alias table, read once and asked many times.

    Built by `load_course_aliases` from the rows `build_course_aliases` wrote.

    **An EMPTY one is a legitimate table and is how a caller says "no aliases".** A
    corpus with no anchor document and a corpus that was never asked are the same
    question to `resolve`, and both must still get the bare-word refusal, which `104`
    R-135 rules unconditionally. `cli` keeps one empty instance for exactly that, so the
    shape test has a single home and no caller has to re-implement it for the absent
    case.
    """

    codes_by_title: Mapping[str, tuple[str, ...]]
    code_by_spelling: Mapping[str, str]
    refs_by_pair: Mapping[tuple[str, str], tuple[str, ...]]

    def canonical_spelling(self, code: str) -> str:
        """`COMS W3134` and `CS3134` answered as the one code their anchor line states.

        `104` R-91: one course split into `CS3134` and `W3134` and became two folders.
        The rule's own canonicaliser cannot close that -- it collapses a separator and
        nothing else, because `apply_rules` searches the raw value and a prefix that
        survives only in `context_before` is not in the value it is asked about. The
        anchor is what states the two are one, so this is where the two become one.

        A code the table has never seen is returned unchanged. An alias table is a
        source of identity, never a gate: a course no anchor names is still a course.
        """
        return self.code_by_spelling.get(_fold(code), code)

    def resolve(self, raw: str) -> SubjectReading:
        """Which course, if any, this value names. Never a guess, and never a folder.

        The order is the point. A SPELLING is asked first, because a value that is
        already a code needs no title lookup and must not be able to collide with one.
        Then the title. Then, only when nothing in the corpus names it, the one shape
        this deployment refuses outright.
        """
        text = _collapsed(raw)
        folded = _fold(text)
        spelled = self.code_by_spelling.get(folded)
        if spelled is not None:
            return SubjectReading(NAMED, spelled, None,
                                  self.refs_by_pair.get((folded, spelled), ()))
        codes = self.codes_by_title.get(folded, ())
        if len(codes) == 1:
            return SubjectReading(NAMED, codes[0], None,
                                  self.refs_by_pair.get((folded, codes[0]), ()))
        if len(codes) > 1:
            refs = tuple(sorted({ref for code in codes
                                 for ref in self.refs_by_pair.get((folded, code), ())}))
            return SubjectReading(
                AMBIGUOUS, None,
                f"{text!r} is the name of {len(codes)} courses in this corpus "
                f"({', '.join(codes)}); a subject that names two courses names neither",
                refs)
        if text and len(text.split(" ")) == 1:
            # `104` R-135, the nine single-word subjects: a department is not a course.
            # A SHAPE and not a list, because a list of department words would be a
            # gazetteer this module may not hold and could not be complete anyway. The
            # cost is stated rather than hidden: a genuinely one-word course name --
            # `Thermodynamics` is the measured one -- is refused UNLESS an anchor in
            # this corpus names it beside a code, which is the branch directly above.
            return SubjectReading(
                BARE_WORD, None,
                f"{text!r} is one word and no anchor document in this corpus names a "
                "course by it; a department name is not a course",
                ())
        return SubjectReading(UNKNOWN, None, None, ())


def _line_before(context_before: str) -> str:
    """The tail of the line the reading sits on, out of §2.8's BEFORE half alone."""
    return context_before.rsplit("\n", 1)[-1] if context_before else ""


def _line_after(context_after: str) -> str:
    """The head of the line the reading sits on, out of §2.8's AFTER half alone.

    The two halves are read separately and never concatenated (M5). P4 split them so
    §8.4 can redact a value without dropping its context, and joining them here would
    forge an adjacency the document does not contain -- which is exactly the mistake a
    module that wanted "the whole line" would make.
    """
    return context_after.split("\n", 1)[0] if context_after else ""


def _department_prefix(line: str, prefix_pattern: re.Pattern[str]) -> str | None:
    """The department word standing immediately before the code, or `None`.

    `COMS W3134` reaches P6 as the reading `W3134` -- `_STRUCTURED` claims one token and
    `COMS` survives only in `context_before`. This recovers it, under two conditions
    that together mean "the line BEGINS with this course":

    * the code is separated from the word by exactly one space, and
    * the word is the whole of what precedes it on the line.

    Both are needed, and the second is the one that matters. Without it `General
    Chemistry I 1403  Dr. Beer` offers `I` as a department -- the concatenation across a
    space that `_SUBJECT_IDENTIFIER`'s second lookahead already refuses, arriving by
    another door and filing three chemistry exams under a course called `I1403`.
    """
    if not line.endswith(" ") or line.endswith("  "):
        return None
    token = line.strip()
    return token if prefix_pattern.fullmatch(token) else None


def _title_on_line(line: str, *, separators: Sequence[str],
                   code_pattern: re.Pattern[str],
                   title_of: Callable[[str], str | None],
                   ) -> tuple[str, tuple[str, ...]] | None:
    """The course name this line states after its separator, and the codes before it.

    Returns `(title, co_spellings)` or `None`. `co_spellings` are the OTHER codes
    printed between this reading and the separator -- `COMS W3134 / CS3134: Data
    Structures` -- and they are what makes R-91's two spellings one course rather than
    an ambiguity.

    **What is between the code and the separator decides whether the line is an
    anchor.** Anything left after removing the other codes, the whitespace and the four
    marks a course line uses to hold two spellings apart is running text, and a line of
    running text that happens to end in a colon is not a course naming itself:
    `W3134 Problem Set 4: Chapter 2` leaves `Problem Set 4` and is refused here.
    """
    found = [(line.find(one), one) for one in separators if line.find(one) != -1]
    if not found:
        return None
    cut, separator = min(found)
    before, after = line[:cut], line[cut + len(separator):]
    co_spellings = tuple(match.group(0) for match in code_pattern.finditer(before))
    residue = code_pattern.sub(" ", before)
    if residue.strip(" \t/,()[]-"):
        return None
    title = title_of(after)
    if title is None:
        return None
    return title, co_spellings


def _alias_identity(*, scan_run_id: str, anchor_content_hash: str, canonical_code: str,
                    alias_text: str, alias_kind: str) -> str:
    """Content-addressed over exactly the UNIQUE constraint's columns.

    Two databases that saw the same corpus hold the same alias ids (§8.5's replay), and
    re-running a scan rewrites a row rather than adding a second one.
    """
    return sha256_of("facts.course_alias", scan_run_id, anchor_content_hash,
                     canonical_code, alias_text, alias_kind)


def _write_alias(conn: sqlite3.Connection, *, scan_run_id: str, observation: Observation,
                 canonical_code: str, alias_text: str, alias_kind: str) -> str:
    check(alias_kind, ALIAS_KINDS, name="alias kind")
    alias_id = _alias_identity(scan_run_id=scan_run_id,
                               anchor_content_hash=observation.content_hash,
                               canonical_code=canonical_code, alias_text=alias_text,
                               alias_kind=alias_kind)
    conn.execute(
        f"INSERT OR REPLACE INTO {COURSE_ALIASES_TABLE} "
        "(alias_id, scan_run_id, anchor_file_id, anchor_content_hash, canonical_code, "
        " alias_text, alias_kind, evidence_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (alias_id, scan_run_id, observation.file_id, observation.content_hash,
         canonical_code, alias_text, alias_kind, cite(observation)))
    return alias_id


def build_course_aliases(conn: sqlite3.Connection, *, scan_run_id: str,
                         file_versions: Sequence[tuple[str, str]],
                         code_pattern: re.Pattern[str],
                         is_code: Callable[[str], bool],
                         canonical: Callable[[str], str],
                         anchor_terms: Sequence[str],
                         separators: Sequence[str],
                         department_prefix: re.Pattern[str],
                         title_of: Callable[[str], str | None],
                         reads_in_document: Callable[[str], bool]) -> tuple[str, ...]:
    """Read every anchor line in the corpus and record what it said. Returns alias ids.

    A CORPUS producer, which is why it is not a `FactResolver` stage: the alias a
    syllabus states is about every other file of that course, and no stage that is asked
    about one file version at a time can see it. `facts.families` runs at the same place
    for the same reason.

    Nothing is authored here. Every argument is the deployment's -- the identifier
    pattern, the predicate that says a reading IS a course, the canonicaliser, the anchor
    vocabulary, the separators a course line uses, the department shape, the title shape,
    and the predicate that says which readings are the document's own words.
    `facts.rules` states the rule this follows: "Every other domain's terms arrive on the
    `Rule`, because the SPEC defers them."

    **`is_code` and `code_pattern` are two arguments because they are two questions.**
    `code_pattern` FINDS the other codes printed beside this one on the anchor line, and
    is the wide shape the product reads everywhere. `is_code` DECIDES that this reading
    is a course at all, and is the narrow one the deployment's rule asserts with. A
    builder that used the wide shape for both would admit `I 1403` off `General Chemistry
    I 1403` and `SPRING 2026` off a term -- the two readings the subject rule's own
    lookaheads exist to refuse -- and would then let either define a course name for
    every other file in the corpus.

    **A truncated context is not a silent refusal and not a claim either.** §8.6 forbids
    truncating silently, and a context P4 cut may have lost the anchor word; a line whose
    context check fails is simply not an anchor line and writes nothing. No `unresolved`
    row is written by this pass at all: an alias is not a FIELD anybody attempted, and
    B7's abstention is a record about a field.
    """
    written: list[str] = []
    for file_id, content_hash in sorted(set(file_versions)):
        for observation in observations_for_version(conn, file_id, content_hash):
            if not reads_in_document(observation.locator):
                continue
            reading = _collapsed(observation.raw_value)
            if not is_code(reading):
                continue
            before, after, _truncated = context_pair(observation)
            if not context_check(before, after, anchor_terms):
                continue
            found = _title_on_line(_line_after(after), separators=separators,
                                   code_pattern=code_pattern, title_of=title_of)
            if found is None:
                continue
            title, co_spellings = found
            code = canonical(reading)
            if not code:
                continue
            written.append(_write_alias(
                conn, scan_run_id=scan_run_id, observation=observation,
                canonical_code=code, alias_text=title, alias_kind=TITLE_ALIAS))
            spellings = {reading, *co_spellings}
            prefix = _department_prefix(_line_before(before), department_prefix)
            if prefix is not None:
                spellings.add(f"{prefix} {reading}")
            for spelling in sorted(spellings):
                canonical_spelling = canonical(spelling)
                if not canonical_spelling:
                    continue
                written.append(_write_alias(
                    conn, scan_run_id=scan_run_id, observation=observation,
                    canonical_code=code, alias_text=canonical_spelling,
                    alias_kind=CODE_SPELLING))
    return tuple(written)


def load_course_aliases(conn: sqlite3.Connection, scan_run_id: str) -> CourseAliases:
    """Every alias row of one scan, indexed for lookup. Ordering imposed, never inherited.

    The codes under one title are SORTED, so a corpus extracted in a different order
    produces the same ambiguity refusal naming the same two courses in the same order
    (§8.5's replay).
    """
    titles: dict[str, set[str]] = {}
    spellings: dict[str, set[str]] = {}
    refs: dict[tuple[str, str], set[str]] = {}
    rows = conn.execute(
        f"SELECT canonical_code, alias_text, alias_kind, evidence_ref "
        f"FROM {COURSE_ALIASES_TABLE} WHERE scan_run_id = ? "
        "ORDER BY canonical_code, alias_text, alias_kind, evidence_ref",
        (scan_run_id,)).fetchall()
    for row in rows:
        code, text, kind = row["canonical_code"], row["alias_text"], row["alias_kind"]
        folded = _fold(text)
        if kind == TITLE_ALIAS:
            titles.setdefault(folded, set()).add(code)
        else:
            spellings.setdefault(folded, set()).add(code)
        refs.setdefault((folded, code), set()).add(row["evidence_ref"])
    return CourseAliases(
        codes_by_title={key: tuple(sorted(value)) for key, value in titles.items()},
        # A SPELLING TWO CODES CLAIM IS DROPPED, not decided by which sorted first.
        # `W3134 / CS3134: Data Structures` in one anchor makes `CS3134` a spelling of
        # `W3134`; `CS3134: Algorithms` in another makes it a course in its own right.
        # Keeping either would re-spell a real course into a different one silently,
        # which is the one thing this table promises never to do. Dropped rather than
        # refused: `canonical_spelling` then returns the code unchanged and `resolve`
        # falls through to the title lookup, so the corpus loses an identity claim it
        # could not make and gains no wrong one.
        code_by_spelling={key: next(iter(value)) for key, value in spellings.items()
                          if len(value) == 1},
        refs_by_pair={key: tuple(sorted(value)) for key, value in refs.items()})


def _live_subject(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  field_key: str) -> bool:
    return any(row["field_key"] == field_key and row["active"]
               for row in facts_for_file(conn, file_id, content_hash))


def resolve_subject_facts(conn: sqlite3.Connection, aliases: CourseAliases, *,
                          file_versions: Sequence[tuple[str, str]],
                          field_key: str,
                          naming_zones: frozenset[str],
                          title_of: Callable[[str], str | None]) -> tuple[str, ...]:
    """§3.5's rule, one step out: a file whose NAME is a course the corpus explains.

    This is the rule-derived half of R-135, and it goes through the same `resolve` the
    model's normaliser goes through -- the two producers cannot disagree about what a
    course is, which is the property `cli.normalize_for_model`'s docstring already
    claims for the deterministic path and the model path.

    **It reads NAMING zones and the alias table reads none of them, and that pair is the
    whole design.** `NAMING_ZONES` is where a document names itself -- the filename, the
    title, a heading, a header. That is exactly where a course's TITLE is printed on the
    19 files the run left with no subject at all, and exactly where an alias must never
    be BUILT, because a folder called `Data Structures` is the thing being explained.

    **A file that already has a live `subject` fact is left alone.** `file_facts` has no
    uniqueness constraint over (file_id, content_hash, field_key), so writing here would
    give one file two live subjects, two reliability states and two folder levels -- the
    defect the removed term slot was deleted over. Superseding another producer's
    conclusion is §8.2's path and is not this change.

    **An ambiguity is a row; everything else this producer cannot answer is silence.**
    `apply_rules` fixes the distinction and this follows it: "a rule that does not
    apply is not a refusal, and writing one would fill `unresolved` with every field
    every rule could theoretically have produced". A one-word filename is most of a
    corpus, and a refusal row for each would be exactly that flood. What IS recorded is
    the case where the corpus answered and answered twice -- one title under two codes,
    or one file naming two courses -- under `NORMALIZATION_FAILED`, §3.6 check 3's own
    reason, citing BOTH anchors. That is how the refusal names both courses without
    inventing a fourteenth reason word.

    The bare-word refusal has a home and it is not here: a MODEL proposing `Physics` has
    made a proposal, and `cli.normalize_for_review` refuses it through check 3 with the
    reason `SubjectReading` carries. This producer proposed nothing.
    """
    written: list[str] = []
    for file_id, content_hash in sorted(set(file_versions)):
        if _live_subject(conn, file_id=file_id, content_hash=content_hash,
                         field_key=field_key):
            continue
        named: dict[str, tuple[str, tuple[str, ...]]] = {}
        refused: list[SubjectReading] = []
        own_refs: dict[str, str] = {}
        for observation in observations_for_version(conn, file_id, content_hash):
            if observation.zone not in naming_zones:
                continue
            title = title_of(observation.raw_value)
            if title is None:
                continue
            reading = aliases.resolve(title)
            if reading.outcome == NAMED and reading.code is not None:
                named.setdefault(reading.code, (title, reading.evidence_refs))
                own_refs.setdefault(reading.code, cite(observation))
            elif reading.outcome == AMBIGUOUS:
                refused.append(reading)
        cache_key = pass_cache_key(conn, file_id=file_id, content_hash=content_hash)
        if len(named) == 1:
            code, (title, anchor_refs) = next(iter(named.items()))
            value_id = ensure_value(conn, field_key=field_key, canonical_value=code,
                                    first_evidence_ref=anchor_refs[0] if anchor_refs
                                    else own_refs[code],
                                    origin=VALUE_ORIGINS[0])
            # §2.8's first rendering: "the raw observation remains exactly that
            # wording". The canonical value is a CODE the file never printed, so the
            # title is the only surviving evidence of what this document called it.
            add_raw_variant(conn, value_id, title)
            written.append(write_fact(
                conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
                value_id=value_id, reliability_state=VALIDATED, origin=RULE,
                evidence_refs=(own_refs[code], *anchor_refs), cache_key=cache_key,
                active=True))
            continue
        if len(named) > 1:
            refused.append(SubjectReading(
                AMBIGUOUS, None,
                f"this file names {len(named)} courses "
                f"({', '.join(sorted(named))}); a file has one subject",
                tuple(sorted(own_refs.values()))))
        for reading in refused:
            write_unresolved(
                conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
                reason=NORMALIZATION_FAILED, attempted_producers=(RULE_ROUTE,),
                evidence_refs=reading.evidence_refs, cache_key=cache_key)
    return tuple(written)

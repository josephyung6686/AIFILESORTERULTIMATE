# src/facts/kind.py
"""THE TYPE-KEY PRODUCER: one closed vocabulary, one field, ranked on the §3.7 path.

**One mechanism, not one field.** `60` H6.1 splits a single question -- what KIND of
thing is this file -- across three keys by the schema that asks it: "if the file IS
the work product of a bounded engagement or course -> `work_type`; if it is an OUTPUT
OF A MAKING PROCESS -> `artifact_type`. `record_type` is what remains." All three are
`value_kind = "enum"` in `facts.fields`, all three are closed, and the compiled
recognition release ships ONE vocabulary that feeds all three -- `work_type_terms`,
per schema, which routes to whichever type key that schema declares. So this module
takes the field key and the vocabulary as parameters and names neither: binding it to
a second key is a line in the composition root, not a change here.
`tests/p6/test_p6_kind.py` wires `artifact_type` through this same function to prove
that. The production root wired only `work_type` until `106` Phase 6.2 (18 Sep 2026),
for the reason recorded below; since then `cli.type_key_rule` binds `artifact_type`
and `record_type` too -- one key per schema, over that schema's own terms and never
the union (H6.3) -- as the `rule` stage of the MODEL pass's resolver, which is built
after site G has named a schema per file (`00` amendment 7(c)). `_rule_stage`, which
runs before any schema is named, still wires `work_type` alone.

WHY ONLY ONE WAS WIRED, AND IT WAS NOT A PROPERTY OF THIS CODE. H6.2 requires exactly
one type key per file, chosen by the ACTIVE SCHEMA: "a file whose routed type key is
not declared by the active schema returns unknown; it is never re-routed to the
nearest declared type key." The schema is not known when this runs --
`orchestrator.run_p1_p7` resolves facts before it classifies -- so a root that wired
all three would fill all three wherever the vocabularies overlap. Measured over the
199-file corpus: 15 files would carry `resume` under both `work_type` and
`record_type` and 2 would carry `cover letter` under all three, which is exactly the
cross-domain collision H6.3 names. The unblocking change is an ordering one in
`orchestrator.py`, not a producer one.

`def.subject-work-record` is why `work_type` is the one that shipped first. It binds
four folder levels and marks two REQUIRED -- `subject_anchor`, which the composition
root's identifier rule fills, and `artifact_kind`, which nothing filled. A required
level that never resolves cannot be built, so no file in the situation could be
placed at all: measured over the ground-truth corpus, 0.0% exact and 85.4% "not
placed".

**THE VOCABULARY IS THE LIBRARY'S AND THIS MODULE AUTHORS NONE OF IT.** The compiled
recognition release already ships `work_type_terms` per schema -- 124 of them for
`academic` -- and they are the same closed set the library's own example chains draw
on (`('Columbia', '2026-Spring', 'PHYS1401', 'Homework')`). Twelve of the thirteen
distinct leaf values the ground-truth labels use for `academic.coursework` are
members of that list verbatim. The list is passed in; there is no literal term in
this file and no route to a value that the caller's vocabulary did not supply.

**A MENTION IS NOT A CLAIM.** A type key answers what the file IS, and a term in
body prose is a document talking about some OTHER document -- an essay that discusses
the homework it accompanies is not a homework. The design already owns that
distinction: `recognition.detector.NAMING_ZONES` exists because "protection is a
claim about what the file IS", and its own comment says `body`, `table`, `ocr`,
`notes`, `annotation` and `reference_list` "are where a document mentions OTHER
documents, and the whole of this constant's job is to keep a mention from becoming a
claim." Measured over the ground-truth corpus: reading every zone fills 10 correctly
and 12 WRONGLY; reading only the naming zones keeps all 10 and leaves 5 wrong. The
zones arrive as a parameter -- this package reaches `recognition/` never -- so the
rule is the design's and the binding is the composition root's.

**THE LONGEST AUTHORED TERM CLAIMS THE SPAN, and that is not a threshold.**
`lecture` and `lecture slides` are both shipped. In `Lecture Slides Week 3.pdf` they
are not two rival readings, they are one reading at two granularities, and counting
both would put them level at 3.0 each so §3.7's margin would refuse a file whose name
says exactly what it is. Nine ground-truth files want `lecture slides`.
`recognition.detector._terms_in` deliberately does the opposite and yields the
covered term too, for a reason that is entirely about PROTECTION -- suppressing
`will` inside `living will` "releases a real will named by its own filename", and
"an over-release is worse than an over-protection". Filling a folder name is the
other direction: the more specific authored reading is the better one, and refusing
to choose it costs a file its folder rather than its seal.

**Two genuinely different terms still refuse.** `Quiz and Homework.pdf` reaches
§3.7's ranker as two candidates that tie, and the margin declines both. That is `00`'s
rule -- abstention where two readings are both supported -- and the reason this
producer's precision costs recall on purpose: one unplaced file is cheaper than a
wrong folder the owner has to find and undo.

**Nothing here is a number.** Every weight, threshold, zone and page is a required
keyword with no default (F8), and the ranking and the refusals are `facts.facets`',
unchanged and shared with §3.10's date producer -- so one reading of one band cannot
fill a field here and fail to fill one there.
"""
from __future__ import annotations

import re
import sqlite3
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.observation import Observation
from evidence_shape.store import is_derived

from facts.evidence import cite, observations_for_version
from facts.facets import Candidate, fill_or_abstain, rank

#: The cover pattern and the window it is read in are the composition root's,
#: injected per call like `facts.dates`' `DatePatterns` and for the same reason:
#: an expression naming a season, a title word or a teacher's honorific is this
#: deployment's reading of a page, not a rule this part may author. `cli`
#: authors both beside `_COVER_COURSE`, which reads the same opening.


class EmptyVocabulary(ValueError):
    """No authored terms. A load error, not a producer that finds nothing.

    F8's rule read on this path: a producer built on an empty vocabulary abstains
    on every file in the corpus and is indistinguishable from one that is working
    and finding nothing, so the failure would present as a quiet 0% rather than as
    a broken injection.
    """


def tokens(text: str) -> tuple[str, ...]:
    """Words, case-folded. Non-alphanumerics separate, AND SO DOES A DIGIT.

    `recognition.detector._tokens`' rule plus one boundary: inside a run of letters
    and digits, every transition between a digit and a non-digit separates too, so
    `lecture01` is `lecture` + `01` and `2024report` is `2024` + `report`. CASE IS
    NEVER READ, which is the whole safety of it -- `HKID` and `OrderReceipt` stay one
    token each, where a camel-case boundary would reduce the owner's identity card to
    `h` + `kid` and put ordinary English words into naming zones.

    WHY THE DETECTOR'S IS NOT CHANGED TO MATCH, and this is now a DELIBERATE
    divergence rather than the drift the old agreement test existed to catch. That
    tokeniser decides PROTECTION: it compares an observation's tokens WHOLE against a
    term, and its evidence side carries the structured identifiers that corroborate a
    schema -- `PHYS1401`, `E1006`, an HKID's own digits. Splitting a course code in
    two there would move the `whole` flag, the corroboration gate and the prefix
    index. Here the same split only names a folder: different consequence, different
    rule. `tests/p6/test_p6_kind.py` still asserts the two agree everywhere else and
    pins the one exception, so the divergence stays exactly one boundary wide.

    NOT §3.7'S FORBIDDEN SUBSTRING MATCH, which is the argument this boundary was
    once left open on. A substring match FINDS a shorter term inside a longer token,
    which is why `MIT` must not be found inside `submit` -- and `submit` carries no
    digit, so it is still one token and `examination` still never equals `exam`. This
    re-SEGMENTS at a change of character class and then matches whole tokens exactly
    as before; nothing that matched under the old rule stops matching.

    Not a regex, for that module's stated reason: `str.isalnum` and `str.isdigit`
    over code points are the same rule expressed in the one place it is applied.
    Applied identically to the vocabulary at compile time and to the evidence here,
    so `problem set` and `Problem-Set-4` are one term and one match. That symmetry is
    what keeps the rule from inventing a reading, and it is free: measured over every
    term of every schema declaring a type key, not one has a digit beside a letter,
    so the compiled key set is unchanged and the boundary fires on evidence alone.
    """
    out: list[str] = []
    current: list[str] = []
    for character in text:
        if not character.isalnum():
            if current:
                out.append("".join(current).casefold())
                current = []
            continue
        if current and character.isdigit() != current[-1].isdigit():
            out.append("".join(current).casefold())
            current = []
        current.append(character)
    if current:
        out.append("".join(current).casefold())
    return tuple(out)


@dataclass(frozen=True, slots=True)
class KindVocabulary:
    """One compiled closed vocabulary: the terms, and every proper prefix of them.

    `terms` is keyed by TOKEN TUPLE and carries the library's own spelling as the
    value, because that spelling becomes a folder name and the document's casing
    must not: `LECTURE SLIDES week 1.pdf` and `Lecture Slides Week 2.pdf` are one
    kind of work, and two spellings of one identity is `65` §4.2's recorded failure.

    `prefixes` is the detector's own optimisation and its reason carries over
    unchanged: the phrase scan extends a candidate only while some authored term
    still begins that way, so the cost is the length of the longest phrase actually
    present in the file rather than the longest term in the vocabulary. Several
    library rows used `work_types` as a notes field and one is a 77-word editorial
    aside; with a fixed window those would widen every scan in the corpus for
    readings that can never match.
    """

    terms: Mapping[tuple[str, ...], str]
    prefixes: frozenset[tuple[str, ...]]


def compile_vocabulary(terms: Iterable[str]) -> KindVocabulary:
    """Compile the caller's authored terms for phrase scanning.

    A term that tokenises to nothing is dropped rather than refused: the library
    carries punctuation-only and empty entries, and a release is not broken by one.
    A vocabulary that is empty AFTER that is refused -- see `EmptyVocabulary`.

    First spelling wins on a collision, and none exists in the shipped library: the
    942 terms the four schemas declaring this field author tokenise to 942 distinct
    keys. It is stated rather than enforced because a future library that spelled
    one term two ways should still load, and the two spellings would be one value.
    """
    compiled: dict[tuple[str, ...], str] = {}
    for term in terms:
        key = tokens(term)
        if key:
            compiled.setdefault(key, term)
    if not compiled:
        raise EmptyVocabulary(
            "the work-type vocabulary is the caller's and this producer authors "
            "none of it; an empty one abstains on every file and cannot be told "
            "from a producer that is working and finding nothing")
    prefixes = {key[:length] for key in compiled
                for length in range(1, len(key))}
    return KindVocabulary(terms=dict(compiled), prefixes=frozenset(prefixes))


def page_of(observation: Observation) -> int | None:
    """Which page this observation sits on, or `None` for an unpaginated format."""
    for segment in observation.location.container_path:
        if segment.kind == "page":
            return segment.index
    return None


def names_the_file(observation: Observation, *, naming_zones: Iterable[str],
                   first_page: int) -> bool:
    """Is this observation somewhere the document NAMES ITSELF (SPEC 2.2)?

    `recognition.detector._names_the_file`'s question, asked of a P6 observation.
    A page of `None` passes: that is not a missing page, it is a format that does
    not paginate -- a `.docx` heading and a filename both have no page, and reading
    absence as failure would stop this producer working on every unpaginated format.

    The page test is why `heading` can be admitted at all. `pdf.text` calls a line a
    heading when its type is larger than the page's body size, which is a
    typographic guess and not a semantic one; the detector measured a 642-page
    datasheet whose page-2 "heading" was body prose set large.
    """
    if observation.location.zone not in naming_zones:
        return False
    page = page_of(observation)
    return page is None or page == first_page


def terms_in(text: str, *, vocabulary: KindVocabulary) -> tuple[str, ...]:
    """The authored terms this text carries, longest first at each position.

    Maximal munch, and the scan resumes AFTER the span the winner claimed, so a
    shorter authored term lying inside a longer one is never also yielded. See the
    module docstring for why this producer parts company with the detector here.
    """
    found: list[str] = []
    words = tokens(text)
    start = 0
    while start < len(words):
        claimed: tuple[str, int] | None = None
        for end in range(start + 1, len(words) + 1):
            candidate = words[start:end]
            term = vocabulary.terms.get(candidate)
            if term is not None:
                claimed = (term, end)
            if candidate not in vocabulary.prefixes:
                break
        if claimed is None:
            start += 1
        else:
            found.append(claimed[0])
            start = claimed[1]
    return tuple(found)


def task_kind_on_a_taught_cover(observation: Observation, *,
                                vocabulary: KindVocabulary,
                                cover: re.Pattern[str],
                                opening: int) -> tuple[Candidate, ...]:
    """The kind a taught cover names on its own line, weighted as a title.

    The cover already names the course. The next line that is one catalogue
    term and a colon is the kind the file gives itself there (`Exercise:`).
    That line is body text, and a body mention weighs less than a filename, so
    a filename that says a different kind would win and the file would be filed
    as the filename's kind. The cover is where the file names what it is, so
    this one line weighs what a title weighs. A filename that names another
    kind then sits inside the margin and the field is refused, which is the
    two-kinds case rather than a guess.

    A colon line anywhere else is not this. A lecture that opens `Note:` has
    no taught cover, and this returns nothing for it.

    `cover` is the expression that recognises the cover and `opening` is how
    much of the reading it is looked for in. Both are the caller's: see the
    note above the imports.
    """
    if is_derived(observation):
        return ()
    window = (observation.raw_value or "")[:opening]
    course = cover.search(window)
    if course is None:
        return ()
    for line in window[course.end():].splitlines():
        head, sep, _rest = line.strip().partition(":")
        if not sep:
            continue
        matched = terms_in(head.strip(), vocabulary=vocabulary)
        if len(matched) == 1 and tokens(head.strip()) == tokens(matched[0]):
            return (Candidate(
                value=matched[0],
                score=float(observation.occurrence_count),
                evidence_refs=(cite(observation),),
                zone="title",
                signal_tier=observation.signal_tier),)
    return ()


def kind_candidates(observation: Observation, *,
                         vocabulary: KindVocabulary,
                         naming_zones: Iterable[str],
                         first_page: int) -> tuple[Candidate, ...]:
    """§3.7 candidates for one observation, or none where it names no file.

    The score is P4's `occurrence_count` and nothing else, exactly as
    `facts.dates.date_candidates` has it: §3.7's weights are applied by
    `facts.facets.rank` from an injected map, and a producer that pre-weighted its
    own candidates would be a second place those numbers live.
    """
    if not names_the_file(observation, naming_zones=naming_zones,
                          first_page=first_page):
        return ()
    reference = cite(observation)
    return tuple(
        Candidate(value=term, score=float(observation.occurrence_count),
                  evidence_refs=(reference,),
                  zone=observation.location.zone,
                  signal_tier=observation.signal_tier)
        for term in terms_in(observation.raw_value, vocabulary=vocabulary))


def kind_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    field_key: str, vocabulary: KindVocabulary,
                    naming_zones: Iterable[str], first_page: int,
                    zone_weight: Mapping[str, float],
                    tier_weight: Mapping[int, float],
                    minimum_score: float,
                    minimum_margin: float,
                    also: Callable[[Observation], Iterable[Candidate]] | None = None,
                    ) -> tuple[str, ...]:
    """One type key's facts for one version of one file. Returns the fact ids.

    At most one, because `fill_or_abstain` fills one facet from one ranked set: a
    file is one kind of work, and two kinds in one name is the case §3.7's margin
    exists to refuse rather than to guess between. The empty tuple is not a failure
    -- it is the abstention, and the `unresolved` row saying which of the three
    refusals happened is on disk.

    Only `raw_value` is read, which is `date_candidates`' choice and for the same
    reason: `normalized_value` is nullable, it is empty on every filename P4 writes,
    and scanning both would count one filename's term twice and distort the margin
    that decides whether the field is filled at all.
    """
    candidates: list[Candidate] = []
    stated_once: set[str] = set()
    for observation in observations_for_version(conn, file_id, content_hash):
        candidates.extend(kind_candidates(
            observation, vocabulary=vocabulary, naming_zones=naming_zones,
            first_page=first_page))
        # One cover stored twice is one statement. Counting both would let a
        # duplicated opening outvote the filename.
        if also is None:
            continue
        for extra in also(observation):
            if extra.value in stated_once:
                continue
            stated_once.add(extra.value)
            candidates.append(extra)
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=zone_weight,
                        tier_weight=tier_weight),
        minimum_score=minimum_score, minimum_margin=minimum_margin)
    return () if fact_id is None else (fact_id,)

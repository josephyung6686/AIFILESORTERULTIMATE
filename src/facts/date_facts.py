# src/facts/date_facts.py
"""§3.10's producer: the ranked-facet path for dates, joined end to end.

`facts.dates` published `date_candidates` and `facts.facets` published `rank` and
`fill_or_abstain`, and until this module existed **nothing in `src/` called any of
them**. The consequence was not theoretical and it was measured on 2026-08-31: of
Done-means 10's three written forms, `AY 2024-25` and `Michaelmas Term 2024` produced
no term fact at all -- so a person whose university writes either of them, which is
most of the UK and much of the US, got no term folder -- and the third, `Spring 2025`,
had been reimplemented inline at the composition root as a §3.5 DIRECT slot, which the
SPEC's production rules forbid in as many words:

    *"Filesystem timestamps are direct; dates recovered from text or filenames are
    not, and take the §3.10 path."*  (P6 SPEC:409-410)

This is that path, and it is ten lines because both halves already existed:

    every observation of the version
        -> `date_candidates`, one per span an explicit pattern claimed
        -> `rank`, which weights by P4's zone and sums the contributions per value
        -> `fill_or_abstain`, which fills at `validated` or records which refusal

**One term is one value, and that is decided upstream of the ranker.** A term written
`Spring 2026` in the syllabus and `2026-Spring` in the filename is one semester, and
if it reaches `rank` as two values it is two candidates that tie, which §3.7's margin
then refuses -- so the person gets no term rather than the wrong one. Worse, on the
`direct` path there is no margin at all and both survive: the run of 2026-08-31
proposed the folders `Spring2025` AND `2025Spring` for one semester. The collapse
therefore happens at `DatePattern.canonical`, per pattern, before a candidate exists.
This module does not perform it and does not know how; it only makes sure nothing
happens between the canonicalisation and the ranking.

**Nothing here is authored.** No expression, no weight, no threshold, no field key,
and no page number. §3.7's numbers and §3.10's catalogue are both Deferred, and every
one of them is a required keyword with no default: absent means refuse, never a
default that quietly answers a question the SPEC left open (F8).

**One refusal, and it belongs to this stage.** §8.6 fixes the order direct -> rule ->
LLM, and `facts.direct` deliberately writes no `unresolved` row because a field it did
not fill has not been refused, only not finished. Here it has been: this is the
deterministic producer for §3.10, and `fill_or_abstain` records which of the three
refusals happened -- `no_candidate_evidence`, `below_score_threshold`, `below_margin`.
§8.5 asks "Did it abstain when evidence was absent?" and one bucket cannot answer it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping

from facts.dates import DatePatterns, date_candidates
from facts.evidence import observations_for_version
from facts.facets import Candidate, fill_or_abstain, rank
from facts.kind import page_of


def date_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_key: str, patterns: DatePatterns, first_page: int,
               zone_weight: Mapping[str, float], tier_weight: Mapping[int, float],
               minimum_score: float, minimum_margin: float) -> tuple[str, ...]:
    """§3.10's facts for one version of one file. Returns the fact ids.

    At most one, because `fill_or_abstain` fills one facet from one ranked set: a
    file version has one term, and two terms in one file is the case §3.7's margin
    exists to refuse rather than to guess between. The empty tuple is not a failure --
    it is the abstention, and the `unresolved` row that says which one is on disk.

    Every ZONE of the version is offered to every pattern, whole zones included.
    That is deliberate and it is the difference from the direct slot this replaces:
    §3.10 identifies its candidates *with explicit regular expressions*, so the
    pattern claims a SPAN out of the text and the whole-page reading it came from can
    never become the value. A slot has no such protection -- it takes the reading
    entire -- which is why `cli.reads_a_structured_string` has to forbid span-less
    locators and why a term could only be read where the reading pass had already cut
    one out for it. A pattern needs no such permission and finds `Michaelmas Term
    2024` in the body text of a document nothing had cut a span from.

    **NOT EVERY PAGE, THOUGH, AND `first_page` IS WHY.** A term is a CLAIM ABOUT THIS
    FILE -- which semester's work it is -- and a season and a year printed deep inside
    a document is, overwhelmingly, a date the document MENTIONS. Measured on the
    owner's own 215-file corpus: `Downloads/Essay 2 Final Draft.pdf` is a Fall 2025
    essay, and the only season-and-year it prints is on page 2, in *"published in The
    New York Times Magazine Fall 2014 issue"* -- a citation. Unopposed, it won §3.7's
    ranking and put three files of one family under a term folder eleven years wrong.
    That is not one essay's problem: every essay with a bibliography cites dated work,
    and the document's own term is on its cover, not in its argument.

    THE TEST IS `facts.kind.names_the_file`'S PAGE HALF, AND ONLY ITS PAGE HALF. That
    function is a zone test AND a page test because a `work_type` is a claim about the
    file; a term is the same kind of claim and gets the same treatment -- but the ZONE
    half must not be borrowed. The one `term` fact the whole corpus gets right is in
    `body`: `Essay 2 Prompt as Text - 628 + 633.docx` opens "University Writing --
    Readings in Medical Humanities / Fall 2025 -- Dr. Sarah Wingerter", and a producer
    narrowed to `NAMING_ZONES` would delete the only correct answer to buy the
    refusal. So `page_of` is imported and `names_the_file` is not.

    A page of `None` PASSES, for `names_the_file`'s own stated reason: that is not a
    missing page, it is a format that does not paginate. The `.docx` above is exactly
    that case, and reading absence as failure would stop this producer working on
    every unpaginated format.

    `first_page` is a required keyword with no default, like every other number here.
    """
    candidates: list[Candidate] = []
    for observation in observations_for_version(conn, file_id, content_hash):
        page = page_of(observation)
        if page is not None and page != first_page:
            continue
        candidates.extend(date_candidates(observation, patterns=patterns))
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=zone_weight,
                        tier_weight=tier_weight),
        minimum_score=minimum_score, minimum_margin=minimum_margin)
    return () if fact_id is None else (fact_id,)

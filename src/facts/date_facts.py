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

**Nothing here is authored.** No expression, no weight, no threshold, no field key.
§3.7's numbers and §3.10's catalogue are both Deferred, and every one of them is a
required keyword with no default: absent means refuse, never a default that quietly
answers a question the SPEC left open (F8).

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


def date_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_key: str, patterns: DatePatterns,
               zone_weight: Mapping[str, float], tier_weight: Mapping[int, float],
               minimum_score: float, minimum_margin: float) -> tuple[str, ...]:
    """§3.10's facts for one version of one file. Returns the fact ids.

    At most one, because `fill_or_abstain` fills one facet from one ranked set: a
    file version has one term, and two terms in one file is the case §3.7's margin
    exists to refuse rather than to guess between. The empty tuple is not a failure --
    it is the abstention, and the `unresolved` row that says which one is on disk.

    Every observation of the version is offered to every pattern, whole zones
    included. That is deliberate and it is the difference from the direct slot this
    replaces: §3.10 identifies its candidates *with explicit regular expressions*, so
    the pattern claims a SPAN out of the text and the whole-page reading it came from
    can never become the value. A slot has no such protection -- it takes the reading
    entire -- which is why `cli.reads_a_structured_string` has to forbid span-less
    locators and why a term could only be read where the reading pass had already cut
    one out for it. A pattern needs no such permission and finds `Michaelmas Term
    2024` in the body text of a document nothing had cut a span from.
    """
    candidates: list[Candidate] = []
    for observation in observations_for_version(conn, file_id, content_hash):
        candidates.extend(date_candidates(observation, patterns=patterns))
    fact_id = fill_or_abstain(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        candidates=rank(candidates, zone_weight=zone_weight,
                        tier_weight=tier_weight),
        minimum_score=minimum_score, minimum_margin=minimum_margin)
    return () if fact_id is None else (fact_id,)

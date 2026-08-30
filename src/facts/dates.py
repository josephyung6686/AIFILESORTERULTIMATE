# src/facts/dates.py
"""§3.10 dates and academic terms: explicit patterns, and no fuzzy parsing anywhere.

§3.10, verbatim: *"Date extraction should be deliberately narrow. The product must not
use fuzzy date parsing because file names and documents frequently contain numbers
that look like years but are course identifiers, version numbers, build numbers, ZIP
codes, or other unrelated values. Date candidates should be identified with explicit
regular expressions and then parsed without fuzzy matching. Academic terms such as
Spring 2025, AY 2024-25, and Michaelmas Term 2024 require dedicated patterns rather
than generic parsing."*

Three consequences, and all three are structural rather than advisory:

* **A candidate exists only where a pattern matched.** There is no scanner, no
  four-digit-year fallback and no "looks like a date" branch. `parse_exact` refuses to
  produce a value without a pattern id, so the only way to a date fact is through a
  pattern that claimed the span.
* **The three named academic terms get three dedicated patterns**, identified by id.
  `Spring 2025` is not `AY 2024-25` parsed loosely, and the result carries which
  pattern claimed it so a test can assert dedication rather than coincidence.
* **The pattern bodies are injected.** Which seasons, which term names, which
  numeric formats -- that is the SPEC's *"Date and academic-term regex catalogue
  beyond the three named patterns"*, which is Deferred. This module authors the three
  **ids** the design names and not one character of regex.

"Parsed without fuzzy matching" is taken at its word: `parse_exact` collapses runs of
whitespace and returns the matched text and nothing else -- no month table, no locale,
no century expansion. What the CALLER may then do to it is `DatePattern.canonical`,
which is the same injected shape `DirectSlot.canonical` and `Rule.canonical` carry:
the per-field normalizer is still Deferred (*"Per-field normalizers and alias tables |
§2.8, §3.6"*), and this module still authors none. It only stops being unable to be
told one -- which matters because a term that reaches §3.7 in two spellings reaches it
as two candidates, and two candidates inside the margin fill nothing.

`facts.date_facts` is the producer that joins this module to §3.7's ranker.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Callable

from evidence_shape.observation import Observation

from facts.evidence import cite
from facts.facets import Candidate

#: The three academic-term patterns §3.10 names, as ids. The design states
#: `Spring 2025` (a season and a year), `AY 2024-25` (an academic-year range) and
#: `Michaelmas Term 2024` (a named term and a year) and requires "dedicated patterns
#: rather than generic parsing" for each. The ids are the design's three cases; the
#: expressions that recognise them are the caller's.
SEASON_YEAR = "season_year"
ACADEMIC_YEAR_RANGE = "academic_year_range"
NAMED_TERM_YEAR = "named_term_year"
REQUIRED_PATTERN_IDS: tuple[str, str, str] = (
    SEASON_YEAR, ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR)


class MissingRequiredPattern(ValueError):
    """A `DatePatterns` without one of §3.10's three named academic-term patterns."""


class NoPatternIdentity(ValueError):
    """A parse attempted without a pattern id -- the fuzzy path, refused."""


@dataclass(frozen=True, slots=True)
class DatePattern:
    """One explicit regular expression and the id that identifies it in a result."""

    pattern_id: str
    pattern: re.Pattern[str]
    #: How this pattern's matched span becomes the candidate's value. `None` keeps
    #: `parse_exact`'s output verbatim, which is what every caller got before this
    #: existed.
    #:
    #: IT IS PER PATTERN, AND THAT IS THE WHOLE DESIGN. One term must reach the
    #: ranker as ONE value however it was written -- `Spring 2026`, `Spring2026` and
    #: `2026-Spring` are one semester -- and a value that arrives as several
    #: spellings arrives as several candidates, which tie, which §3.7's margin then
    #: refuses. Measured on 2026-08-31: `Spring 2025` and `2025-Spring` in one corpus
    #: proposed the folders `Spring2025` AND `2025Spring`. `65` §4.2 records the same
    #: failure for course codes: "four files of one course became four one-file
    #: groups because one identity arrived as several spellings."
    #:
    #: A SINGLE canonicaliser for the whole field was rejected. §3.10 requires
    #: "dedicated patterns rather than generic parsing", and one `str -> str` over
    #: all three forms is handed no pattern id -- it would have to re-decide which
    #: of the three it was looking at, which is the generic parsing the design
    #: forbids, moved one step downstream of the patterns that already decided.
    #:
    #: The callable is the CALLER'S, exactly as `DirectSlot.canonical` and
    #: `Rule.canonical` are, and for the same recorded reason: round 4's C-5 leaves
    #: `normalize(field, raw_value)` owned by no part, so P6 gains no opinion about
    #: what a term looks like -- only the ability to be told. One that raises
    #: propagates; a broken injection must not arrive as a silent absence of facts
    #: (§8.6).
    canonical: Callable[[str], str] | None = None

    def __post_init__(self) -> None:
        if not self.pattern_id:
            raise NoPatternIdentity("a pattern is identified by a non-empty id")
        if not isinstance(self.pattern, re.Pattern):
            raise ValueError("§3.10 requires an explicit compiled regular expression")


@dataclass(frozen=True, slots=True)
class DatePatterns:
    """The injected catalogue. The three §3.10 names are required; the rest is the
    Deferred catalogue and is empty unless a caller supplies it."""

    patterns: tuple[DatePattern, ...]

    def __post_init__(self) -> None:
        ids = tuple(one.pattern_id for one in self.patterns)
        if len(set(ids)) != len(ids):
            raise ValueError(f"duplicate pattern ids: {ids}")
        missing = [name for name in REQUIRED_PATTERN_IDS if name not in ids]
        if missing:
            raise MissingRequiredPattern(
                f"§3.10 names three academic-term patterns and requires a dedicated "
                f"one for each; missing: {missing}")

    @property
    def pattern_ids(self) -> tuple[str, ...]:
        return tuple(one.pattern_id for one in self.patterns)

    @property
    def extra_pattern_ids(self) -> tuple[str, ...]:
        """Everything beyond §3.10's three -- the Deferred half, empty by default."""
        return tuple(name for name in self.pattern_ids
                     if name not in REQUIRED_PATTERN_IDS)

    def by_id(self, pattern_id: str) -> re.Pattern[str]:
        for one in self.patterns:
            if one.pattern_id == pattern_id:
                return one.pattern
        raise KeyError(pattern_id)


@dataclass(frozen=True, slots=True)
class DateMatch:
    """One pattern's claim on one span, carrying which pattern claimed it.

    Done-means 10 requires each of the three academic terms to be matched by a
    *dedicated* pattern "asserted by pattern identity in the result rather than by the
    value alone", and `Candidate` has no room for an id -- so the identity lives here
    and `date_candidates` is this record projected onto §3.7's shape.
    """

    pattern_id: str
    raw: str
    #: `parse_exact`'s output put through the pattern's own `canonical`, so the two
    #: spellings of one term are ONE value before anything ranks them.
    value: str
    evidence_ref: str
    zone: str
    signal_tier: int | None
    occurrence_count: int


def parse_exact(raw: str, *, pattern_id: str) -> str:
    """Return the matched text, whitespace-normalized, or refuse.

    This is the whole of "then parsed without fuzzy matching": no month table, no
    locale, no two-digit-year expansion, no reinterpretation of any kind. A caller
    with no pattern id has nothing that claimed the span, and there is no route from
    here to a value without one.
    """
    if not pattern_id:
        raise NoPatternIdentity(
            "§3.10 admits no candidate that a dedicated pattern did not claim")
    if not raw or not raw.strip():
        raise NoPatternIdentity(f"pattern {pattern_id!r} claimed an empty span")
    return " ".join(raw.split())


def date_matches(observation: Observation, *,
                 patterns: DatePatterns) -> tuple[DateMatch, ...]:
    """Every span of this observation's raw value that an explicit pattern claims."""
    found: list[DateMatch] = []
    for one in patterns.patterns:
        for match in one.pattern.finditer(observation.raw_value):
            parsed = parse_exact(match.group(0), pattern_id=one.pattern_id)
            found.append(DateMatch(
                pattern_id=one.pattern_id, raw=match.group(0),
                value=(parsed if one.canonical is None
                       else one.canonical(parsed)),
                evidence_ref=cite(observation), zone=observation.location.zone,
                signal_tier=observation.signal_tier,
                occurrence_count=observation.occurrence_count))
    return tuple(sorted(found, key=lambda one: (one.pattern_id, one.value)))


def date_candidates(observation: Observation, *,
                    patterns: DatePatterns) -> tuple[Candidate, ...]:
    """§3.7 candidates for §3.10 spans, so a date is ranked like any other facet.

    The score is P4's `occurrence_count` and nothing else: §3.7's weights are applied
    by `facts.facets.rank` from an injected map, and a producer that pre-weighted its
    own candidates would be a second place those numbers live.
    """
    return tuple(
        Candidate(value=one.value, score=float(one.occurrence_count),
                  evidence_refs=(one.evidence_ref,), zone=one.zone,
                  signal_tier=one.signal_tier)
        for one in date_matches(observation, patterns=patterns))

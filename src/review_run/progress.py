"""§8.6's progress line, as the lines a person reads.

    "The user interface should show the difference between completed work and
    deferred work." ... "This makes the product's limitations legible and avoids
    the false impression that an unprocessed file was understood and found
    unimportant."

`review_surface.progress` builds that line from P4's own extraction runs, refuses
to sum two states together, and raises when an indexed file reaches no entry. It
had no caller. `src/cli.py` prints folders, placements and holds, and says
nothing whatever about a file it could not open -- so the person reading a run
over a real disk was told about the files the product understood and told nothing
about the ones it did not.

**This module renders and adds nothing.** Every count comes off a `ProgressEntry`
and no two are added: the single blended figure is the thing §8.6 names as the
failure, and a renderer holding the entries in a list is exactly where it would
reappear.

**A deferral with no named cause says so out loud.** §8.6 requires the cause
NAMED rather than implied. Nothing in `src/` records which ceiling fired --
`database_agent.budget` publishes the seventeen keys and stores no record of one
being hit -- so `cause_for` answers `None` for every state in this build, and the
line prints the gap AS a gap. A count with a silent blank beside it reads as a
cause the person failed to notice.

**Names are never printed here.** `ProgressEntry.file_ids` exists so §8.6's rule
that no file is absent from every entry is checkable, and it stays inside the
record: a progress line is a count per state, and a protected file's name has no
business on it. That is why this module needs no redaction policy and takes none.

**Every policy is the composition root's.** `precedence` is Open question 4,
`awaiting_model_review` and `flagged_by_model_review` are the two populations
Open question 3 leaves unarbitrated, and `cause_for` is P1's configuration.
Not one has a default here.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence

from review_surface.progress import progress_line
from review_surface.records import INDEXED, ProgressEntry
from review_surface.vocabulary import STATE_COMPLETED

__all__ = ["progress_lines"]

#: Said once, where the count is, rather than left to a reader's charity. The
#: sentence is deferred copy like every other word P13 prints; what is
#: contractual is that a deferral whose cause nothing recorded does not print as
#: a bare number.
_NO_CAUSE = ("no ceiling is recorded as the cause, so this build cannot say "
             "which limit stopped it")


def _entry_line(entry: ProgressEntry) -> str:
    """One entry, with its state named, and its cause or the absence of one.

    Completed work is asked no cause: there is nothing to explain about a file
    the product finished reading, and printing "no ceiling is recorded" beside it
    would invent a limitation that did not occur.
    """
    said = f"  {entry.count} {entry.label}  ({entry.state})"
    if entry.state == STATE_COMPLETED:
        return said
    return f"{said} -- {entry.cause or _NO_CAUSE}"


def progress_lines(conn: sqlite3.Connection, *, scan_ref: str,
                   plan_version: str, rendered_at: str,
                   indexed_files: Mapping[str, str],
                   precedence: Sequence[str],
                   awaiting_model_review: Callable[[], Sequence[str]],
                   flagged_by_model_review: Callable[[], Sequence[str]],
                   cause_for: Callable[[str], str | None]) -> tuple[str, ...]:
    """§8.6's line, ready to print. Every argument is required.

    `FileAbsentFromEveryEntry` and `CompletenessPrecedenceRequired` are P13's and
    pass straight through. Catching either would turn a run that lost somebody's
    file into a shorter, perfectly readable paragraph, which is the failure mode
    §8.6's rule exists to make impossible.
    """
    line = progress_line(
        conn, scan_ref=scan_ref, plan_version=plan_version,
        rendered_at=rendered_at, indexed_files=indexed_files,
        precedence=precedence, awaiting_model_review=awaiting_model_review,
        flagged_by_model_review=flagged_by_model_review, cause_for=cause_for)

    indexed = next(entry for entry in line.entries if entry.label == INDEXED)
    rows = [_entry_line(entry) for entry in line.entries
            if entry.label != INDEXED]
    return (
        "",
        f"What this run could read: {indexed.count} files indexed.",
        *rows,
        "  A file counted here was not necessarily understood. Nothing above "
        "is added together: deferred work and completed work are different "
        "answers.",
    )

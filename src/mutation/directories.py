"""Contract out §7 -- reversing the directories one action created.

§8.3 requires every mutation to be reversible, and creating a directory for a
frozen node is a mutation P12 performed: §5.1 and §5.12 leave frozen nodes as
designed structure rather than folders on disk, so the folder only exists because
an apply made it. On undo it is removed **only** when all three hold:

* this journal entry recorded creating it,
* it is still empty, and
* no other journal entry that is still applied moved a file into it or beneath it.

Removal proceeds deepest-first through the chain this entry created and **stops
at the first directory that fails a condition** -- a directory whose child
survived is not empty, and going on would be asking a question whose answer is
already settled. Otherwise the directory is RETAINED and the retention and its
reason are recorded. **A retained directory is never a conflict**, because the
file reversal itself succeeded; a folder that stayed behind is a fact about the
folder, not a failure of the undo.

**Nothing here can remove anything of the person's.** §7.11's prohibition is
untouched: an empty directory contains no file, and a directory P12 did not
create is never a candidate. `os.rmdir` is the only removal primitive used, and
it is the whole reason "still empty" is safe -- the kernel refuses a non-empty
directory, so emptiness is guaranteed by the system call and not only by the
check above it. There is no path through this module that reaches a recursive
removal, because none is imported.

**This module performs no query.** The journal entry and the destinations of the
other still-applied entries both arrive as arguments, so the policy can be read
in one screen and exercised against any history a test cares to state, and so
`undo.py` -- which owns the journal reads -- is not imported back into by the
module it calls.

**No numeric literal beyond 0 and 1 appears in this file.**
"""
from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path

from mutation.execute import JournalEntry
from mutation.vocabulary import (
    DIR_REMOVED, DIR_RETAINED_NOT_CREATED, DIR_RETAINED_NOT_EMPTY,
    DIR_RETAINED_REFERENCED,
)


def _referenced(directory: Path, other_destinations: Sequence[str]) -> bool:
    """Did another still-applied entry put a file in this directory or beneath it?"""
    return any(Path(destination).is_relative_to(directory)
               for destination in other_destinations)


def reverse_directories(entry: JournalEntry, *,
                        other_destinations: Sequence[str],
                        ) -> tuple[tuple[str, str], ...]:
    """One outcome per directory this entry created, deepest first.

    `other_destinations` is where every OTHER still-applied entry put its file.
    "Still applied" is the load-bearing half: an entry whose own move has since
    been undone has no file there any more and must not go on holding a
    directory (Contract out §7).

    The reference question is asked BEFORE emptiness. Both would often be true
    at once, and asking emptiness first would leave
    `retained:referenced_by_other_entry` unreachable in every case that can
    actually arise -- a vocabulary member nothing can produce is
    indistinguishable from one that does not work.
    """
    outcomes: list[tuple[str, str]] = []
    stopped = False
    for path in reversed(entry.directories_created_by_this_action):
        directory = Path(path)
        if stopped:
            # The child survived, so this one is not empty either. Reported with
            # its true reason rather than left out of the record.
            outcomes.append((path, DIR_RETAINED_NOT_EMPTY))
            continue
        if not directory.is_dir():
            # Gone, or something else is at that path now. Whatever is there is
            # not the directory this entry created, so it is not this entry's to
            # remove.
            outcomes.append((path, DIR_RETAINED_NOT_CREATED))
            stopped = True
            continue
        if _referenced(directory, other_destinations):
            outcomes.append((path, DIR_RETAINED_REFERENCED))
            stopped = True
            continue
        try:
            os.rmdir(directory)
        except OSError:
            # Not empty, or a permission the product no longer has. Either way
            # the directory stays and nothing inside it is touched.
            outcomes.append((path, DIR_RETAINED_NOT_EMPTY))
            stopped = True
            continue
        outcomes.append((path, DIR_REMOVED))

    if not stopped and entry.directories_created_by_this_action:
        # The chain went all the way up to a directory P12 did not create.
        # Naming the boundary is what makes the stopping point legible instead
        # of the report simply ending.
        boundary = Path(entry.directories_created_by_this_action[0]).parent
        outcomes.append((str(boundary), DIR_RETAINED_NOT_CREATED))
    return tuple(outcomes)

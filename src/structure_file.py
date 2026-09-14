"""The proposed structure as a plain text file a person edits.

`00` "Amendments of 2026-09-14" item 2, the owner's own words: "we go directly
into a proposed file structure -- a general template and structure that they can
create and edit, with an AI proposal which is the templates we already created
based on what we see in their files; more customisation by the user on the
template side, so the file system does not have to auto-make everything."

The tree the design stage proposes IS that proposal. This module is the ONE way
it is edited: the outline is written to a text file, the person changes it, and
the changed file is read back as EDITS. It knows nothing about the database, the
plan tables or the gestures -- `cli` turns an edit into the gesture that already
exists for it, and refuses by name the edit no gesture can express.

**THE MARKER IS THE IDENTITY, AND THE LABEL IS THE THING BEING EDITED.** A line
carries `[n]`, which is that folder's place in the outline the product wrote.
Everything the person can change is on the same line as the marker: the words in
front of it are the folder's name, and deleting the whole line deletes the
folder. Nothing else in the file is read -- what follows the marker is the
product's own description, rewritten on every run, so a person who corrects a
sentence there has changed nothing and is told so by the header rather than by a
surprise.

A line with NO marker is a folder the person added. It has no place in the plan
yet, so it says what it is for: `situation: <id>`, the library's own id for one
of the lives this material can be. That is the only thing an added folder can
carry, because a branch declared for a situation is the only kind of folder a
gesture can add.
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from typing import Mapping, Sequence


class StructureRefused(RuntimeError):
    """The edited outline asks for something no gesture can express, or names a
    folder this plan does not have. Raised with the line, so the person can find
    it in the file they just edited."""


#: Two spaces per level, and the outline is indented with nothing else. A tab
#: would be ambiguous against it, and a person who indents by three spaces has
#: written a depth the file cannot state -- which is refused rather than rounded.
INDENT: str = "  "

#: `situation: <id>`, on an added folder's own line or on a line of its own under
#: a branch. Lower case with a single space, because that is how the outline
#: writes it and the person is copying what they read.
SITUATION_PREFIX: str = "situation:"

_MARKED = re.compile(r"^(?P<label>.*?)\s*\[(?P<marker>\d+)\](?P<words>.*)$")


@dataclass(frozen=True)
class StructureRow:
    """One folder, as the outline prints it.

    `words` is everything the product says about this folder -- what it is for,
    how many files would sit under it, the situation it is built from -- in one
    string, because this module composes no sentences: `cli` reads the library
    and the plan and writes the words, and a formatter that split them into
    fields here would be a second place where the screen's vocabulary lives.
    """

    depth: int
    label: str
    marker: int
    words: str
    #: What this folder is FOR, in the library's own sentence, or empty. It is a
    #: paragraph rather than a phrase, so it is written as wrapped `#` lines under
    #: the folder instead of running off the end of the one the person edits.
    note: str = ""


@dataclass(frozen=True)
class Renamed:
    """`[n]`'s label is not the label the plan gave it."""

    marker: int
    was: str
    now: str


@dataclass(frozen=True)
class Removed:
    """`[n]` is not in the edited file at all."""

    marker: int
    was: str


@dataclass(frozen=True)
class Added:
    """A line with no marker, under `parent` (or at the top when `None`)."""

    parent: int | None
    label: str
    situation: str | None


@dataclass(frozen=True)
class SituationSaid:
    """`situation: <id>` on a line of its own under `[n]`."""

    marker: int
    situation: str


@dataclass(frozen=True)
class Moved:
    """`[n]` sits under a different folder than the plan put it under.

    A REFUSAL CARRIED AS AN EDIT rather than raised while parsing, so the reader
    gets every edit in the file and `cli` can name this one beside the gestures
    that do exist. Nothing applies it: `00` gives no gesture that moves a folder,
    and inventing one here would be the second path to the plan tables this
    module exists to avoid.
    """

    marker: int
    label: str
    was_under: int | None
    now_under: int | None


def lines(rows: Sequence[StructureRow]) -> tuple[str, ...]:
    """The outline's body: one line per folder, and its sentence under it.

    ONE function, called by `render` for the file and by the screen for the
    block. The person reads the block, opens the file and has to recognise it,
    and two renderings of one proposal is one of them eventually being stale.
    """
    written: list[str] = []
    for row in rows:
        indent = INDENT * row.depth
        written.append(f"{indent}{row.label}  [{row.marker}]"
                       f"{'  -- ' + row.words if row.words else ''}")
        if row.note:
            # A COMMENT, so the sentence is not a line the parser could read as a
            # folder the person added. It is also how a long paragraph sits under
            # a short line without either being cut.
            written.extend(textwrap.wrap(
                row.note, width=76, initial_indent=f"{indent}# ",
                subsequent_indent=f"{indent}# ",
                break_on_hyphens=False, break_long_words=False))
    return tuple(written)


def render(rows: Sequence[StructureRow], *, path: str) -> str:
    """The outline, with the header that says what may be edited in it.

    The header is part of the file and not part of the screen. A person opens
    this in an editor hours later with nothing else in front of them, and a file
    whose rules live only in the terminal scrollback is a file whose rules are
    gone. `84` §6's rule applies to it whole: the command it names has to be one
    they can paste.
    """
    header = [
        "# The structure this run proposes for your files.",
        "# Edit this file, then hand it back on the next run with:",
        f"#     --structure {path}",
        "#",
        "# Rename a folder: change the words in front of its [n].",
        "# Leave a folder out: delete its whole line.",
        f"# Add a folder: write a new line under the one it belongs under, "
        f"indented two spaces further, ending `{SITUATION_PREFIX} <id>`.",
        f"# Say which of your lives a branch is: put `{SITUATION_PREFIX} <id>` "
        f"on a line of its own under it.",
        "#",
        "# The [n] is how the product finds the folder again -- leave it alone.",
        "# Everything after it is what the product read, rewritten every run:",
        "# changing those words changes nothing.",
        "",
    ]
    return "\n".join(header + list(lines(rows))) + "\n"


def _depth(line: str) -> int:
    lead = len(line) - len(line.lstrip(" "))
    if lead % len(INDENT):
        raise StructureRefused(
            f"{line.strip()!r} is indented {lead} spaces, and this outline is "
            f"indented {len(INDENT)} at a time. A depth between two levels does "
            f"not say which folder the line is under, and guessing at it would "
            f"put somebody's folder somewhere they did not ask for.")
    return lead // len(INDENT)


def read(text: str, *, labels: Mapping[int, str],
         parents: Mapping[int, int | None]) -> tuple[object, ...]:
    """Every edit in the file, against the outline the plan would print now.

    `labels` and `parents` are the plan's own answer to "what did we call `[n]`
    and what did we put it under". They are passed in because this module holds
    no database: the same two mappings build the outline and read it back, so a
    line the product wrote and did not change produces no edit at all.

    THE ORDER OF THE FILE IS NOT READ. A person who moves a line up or down
    within its parent has reordered folders on a screen, and `00` gives no
    gesture for the order of siblings; what is read is which folder each line IS
    (its marker), what it is CALLED and what it sits UNDER.
    """
    edits: list[object] = []
    seen: set[int] = set()
    #: `(marker, label, the marker it sat under)` per line, read in a second pass:
    #: whether a line MOVED cannot be answered until every line has been seen,
    #: because the answer depends on whether its own parent is still in the file.
    sat: list[tuple[int, str, int | None]] = []
    # The marker of the innermost line at each depth, so a child's parent is the
    # line above it that is one shallower -- which is what the indentation means.
    at_depth: dict[int, int | None] = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        depth = _depth(raw)
        body = raw.strip()
        if body.lower().startswith(SITUATION_PREFIX):
            situation = body[len(SITUATION_PREFIX):].strip()
            under = at_depth.get(depth - 1)
            if under is None or not situation:
                raise StructureRefused(
                    f"{body!r} says which situation a folder is, and there is no "
                    f"folder above it for it to be about. Put it on a line of "
                    f"its own, indented one level under the folder it answers "
                    f"for.")
            edits.append(SituationSaid(marker=under, situation=situation))
            continue
        matched = _MARKED.match(body)
        if matched is None:
            label, _, situation = body.partition(SITUATION_PREFIX)
            edits.append(Added(parent=at_depth.get(depth - 1),
                               label=label.strip(),
                               situation=situation.strip() or None))
            # An added folder can hold nothing yet, so nothing is recorded at its
            # depth: a line indented under it would be a second new folder under
            # a folder that does not exist, and there is no gesture for that.
            continue
        marker = int(matched.group("marker"))
        if marker not in labels:
            raise StructureRefused(
                f"{body!r} names folder [{marker}], and this plan has no folder "
                f"[{marker}]. The numbers are the product's own and are rewritten "
                f"every run, so an outline from an older run does not fit this "
                f"one: run the command again to get a current file.")
        if marker in seen:
            raise StructureRefused(
                f"folder [{marker}] is on two lines of this file. One folder is "
                f"one line, and two lines carrying one number would be two "
                f"answers to the same question.")
        seen.add(marker)
        at_depth[depth] = marker
        # Deeper entries are stale the moment a shallower line is read: the next
        # line at depth+1 is this line's child and not the previous branch's.
        for deeper in [d for d in at_depth if d > depth]:
            at_depth.pop(deeper)
        label = matched.group("label").strip()
        if label != labels[marker]:
            edits.append(Renamed(marker=marker, was=labels[marker], now=label))
        sat.append((marker, label, at_depth.get(depth - 1)))
    for marker in labels:
        if marker not in seen:
            edits.append(Removed(marker=marker, was=labels[marker]))
    for marker, label, under in sat:
        # A LINE WHOSE OWN PARENT THE PERSON DELETED HAS NOT MOVED. Deleting a
        # folder pulls everything under it up by one, and reading that as forty
        # moves would refuse the commonest edit in the file for something nobody
        # did. Those children are removed with their parent -- a folder with no
        # folder above it in the outline is not a folder the outline asks for --
        # and `Removed` above already says so for every one of them that is gone.
        was = parents.get(marker)
        if was is not None and was not in seen:
            edits.append(Removed(marker=marker, was=label))
        elif under != was:
            edits.append(Moved(marker=marker, label=label,
                               was_under=was, now_under=under))
    return tuple(edits)

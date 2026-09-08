"""The hand-made ground truth: what a careful person would want for each file.

Nothing in this module reads a file of the owner's. It reads a labels file --
one row per corpus-relative path -- and refuses the row shapes that would make
the scorecard lie:

  * a protected row carrying a destination, which would score the product for
    moving material it may only count;
  * a protected row carrying expected fields, which would score it for having
    opened one;
  * an `uncertain` row with no reason, which records that somebody hesitated
    without recording what about;
  * a situation the shipped library does not carry, whose scoring run could
    never be made;
  * two rows for one path, where whichever loaded last would silently win.

An honest `uncertain` is worth more than a guessed label, because a harness that
scores against a wrong label drives the product in the wrong direction for as
long as the label stands.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Mapping, Sequence


class LabelError(Exception):
    """A labels file that would make the scorecard lie."""


@dataclass(frozen=True)
class Label:
    """One hand-made judgement about one file."""

    path: str
    group: str
    situation: str
    #: The folder path BELOW the top-level `--label` folder, top-down. `None`
    #: for protected material and for a file whose home is genuinely unknown.
    destination: tuple[str, ...] | None
    #: Other destinations a person could reasonably want instead. A file that is
    #: two things at once has two right answers and the person picks.
    also_acceptable: tuple[tuple[str, ...], ...]
    expected_fields: Mapping[str, str]
    protected: bool
    #: The reason the right answer could not be established, or `None`.
    uncertain: str | None
    #: Files that are versions, copies or formats of one work share a family.
    family: str | None
    note: str | None
    #: `104` R-147. Per FIELD KEY, the other spellings that name this row's
    #: expected value -- `{"subject": ("ENGI E1006",)}` on a row whose label
    #: spells that course `PYTHON1006`. Resolved at load from the document's
    #: top-level `aliases`, so the scorer is handed the answer for this row
    #: instead of the whole table and a lookup.
    #:
    #: A SCORING EQUIVALENCE AND NOTHING ELSE. `00`'s 2026-09-05 amendment
    #: rules that "There are no alias tables or equivalence maps in code", so
    #: this lives in the labels file, which is the instrument's data and not the
    #: product's, and `score_fields` is the only reader. It says two spellings
    #: name one course. It never says one folder is another, and nothing that
    #: chooses a destination or renames a node can see it.
    aliases: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @property
    def is_uncertain(self) -> bool:
        return self.uncertain is not None

    @property
    def destinations(self) -> tuple[tuple[str, ...], ...]:
        """Every destination this label accepts, the labelled one first."""
        if self.destination is None:
            return ()
        return (self.destination, *self.also_acceptable)


class Labels(Mapping[str, Label]):
    """Every label, addressed by corpus-relative path."""

    def __init__(self, rows: Mapping[str, Label],
                 aliases: tuple[tuple[str, tuple[str, ...]], ...] = ()) -> None:
        self._rows = dict(rows)
        #: The groups AS DECLARED, `(field, spellings)` each, kept beside the
        #: rows they were resolved onto so a reader of the loaded object can see
        #: what the file asserted and not only what each row ended up carrying.
        self.aliases = aliases

    def __getitem__(self, key: str) -> Label:
        return self._rows[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def situations(self) -> tuple[str, ...]:
        """The situations that need a scoring run, each named once, sorted.

        One run per situation, because `--situation` is one answer applied to
        every file in the folder. A file is scored only against the run whose
        situation its label names.
        """
        return tuple(sorted({row.situation for row in self._rows.values()}))

    def for_situation(self, situation: str) -> tuple[Label, ...]:
        return tuple(row for row in self._rows.values() if row.situation == situation)


def _shipped_situation_names() -> frozenset[str]:
    """The situations the product actually carries, from the product itself."""
    import sys

    root = Path(__file__).resolve().parents[2]
    src = str(root / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from cli import load_shipped_catalogue, read_packaged_library_file
    from production import shipped_situations

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    return frozenset(row.name for row in shipped_situations(catalogue))


def _segments(value, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise LabelError(f"{where}: a destination is a list of folder names")
    if not value:
        raise LabelError(f"{where}: an empty destination is not an answer -- "
                         "use null and say why in `uncertain`")
    return tuple(value)


def _alias_groups(document) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """The document's `aliases`, checked for the shapes that would make it lie.

    `104` R-147, and the hole it names: §16.2 found the course code for 18 of
    the 43 labelled coursework files nowhere in the file's own bytes -- in the
    folder path, or on a neighbouring syllabus -- "under a spelling the label
    does not use", and 23 dossiers that held the code's digits all scored as
    misses. The documents of one course print `ENGI E1006` where the label
    spells it `PYTHON1006`. `_same` is already separator-blind, so a printed
    `Aaaaaa 9999` against a label's `AAAAAA9999` needed nothing; that a CODE and
    a NAME are one course is not a fact about the strings, and somebody has to
    say it. This is where a person says it.

    OPTIONAL, because every labels file written before R-147 must keep loading
    and its silence is not an empty ruling.
    """
    raw_groups = document.get("aliases")
    if raw_groups is None:
        return ()
    if not isinstance(raw_groups, list):
        raise LabelError("`aliases` is an array of {field, values} groups")

    groups: list[tuple[str, tuple[str, ...]]] = []
    claimed: dict[tuple[str, str], int] = {}
    for index, raw in enumerate(raw_groups):
        where = f"alias group {index}"
        if not isinstance(raw, dict):
            raise LabelError(f"{where}: a group is an object with `field` and `values`")
        key = raw.get("field")
        if not isinstance(key, str) or not key:
            raise LabelError(
                f"{where}: a group needs the `field` it speaks about. `essay` as a "
                "`work_type` and `essay` inside a subject are not one claim, and a "
                "group loose across fields would score an answer to the wrong "
                "question as agreement")
        values = raw.get("values")
        if not isinstance(values, list) or not all(isinstance(v, str) and v for v in values):
            raise LabelError(f"{where}: `values` is a list of spellings")
        if len(values) < 2:
            raise LabelError(
                f"{where}: a group needs at least two spellings. One asserts no "
                "equivalence while reading as though it did")
        for value in values:
            seen = claimed.get((key, value))
            if seen is not None:
                raise LabelError(
                    f"{where}: {value!r} is already in two alias groups for "
                    f"`{key}` (the first is group {seen}). Either they are one "
                    "group written twice or they are two different claims about "
                    "what that spelling means, and the scorer would take "
                    "whichever loaded last")
            claimed[(key, value)] = index
        groups.append((key, tuple(values)))
    return tuple(groups)


def _aliases_for(expected_fields: Mapping[str, str],
                 groups: Sequence[tuple[str, tuple[str, ...]]],
                 ) -> Mapping[str, tuple[str, ...]]:
    """This row's other spellings, resolved once at load.

    Compared here by exact string, and that is deliberate: this asks which GROUP
    the label's own value was written into, which is a question about the labels
    file agreeing with itself. Whether a fact matches any of the resulting
    spellings is `score_fields`'s question and is asked with `_same`, so the
    loose comparison happens in exactly one place.
    """
    resolved: dict[str, tuple[str, ...]] = {}
    for key, wanted in expected_fields.items():
        for field_key, values in groups:
            if field_key != key or wanted not in values:
                continue
            others = tuple(v for v in values if v != wanted)
            if others:
                resolved[key] = others
            break
    return resolved


def load_labels(path: str | Path, *, known_situations: frozenset[str] | None = None) -> Labels:
    """Read a labels file, refusing every shape that would make it lie."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, dict) or "files" not in document:
        raise LabelError("a labels file is an object with a `files` array")
    situations = _shipped_situation_names() if known_situations is None else known_situations
    groups = _alias_groups(document)

    rows: dict[str, Label] = {}
    for raw in document["files"]:
        where = raw.get("path", "<a row with no path>")
        if not isinstance(where, str) or not where:
            raise LabelError("every row needs a corpus-relative `path`")
        if where in rows:
            raise LabelError(f"{where}: labelled twice; whichever loaded last "
                             "would silently win")

        situation = raw.get("situation")
        if situation not in situations:
            raise LabelError(f"{where}: {situation!r} is not a shipped situation, "
                             "so the run that would score this file cannot be made")

        protected = bool(raw.get("protected"))
        destination = raw.get("destination")
        if destination is not None:
            destination = _segments(destination, where)
        expected_fields = raw.get("expected_fields") or {}
        if not isinstance(expected_fields, dict):
            raise LabelError(f"{where}: expected_fields is a field_key -> value object")

        if protected and destination is not None:
            raise LabelError(
                f"{where}: a protected label may not carry a destination. "
                "Protected material is marked and counted, never moved, so a "
                "destination here would score the product for doing the "
                "forbidden thing")
        if protected and expected_fields:
            raise LabelError(
                f"{where}: a protected label may not carry an expected field. "
                "Fields come from content, so expecting one is expecting the "
                "file to have been opened")

        uncertain = raw.get("uncertain")
        if uncertain is not None:
            if not isinstance(uncertain, str) or not uncertain.strip():
                raise LabelError(f"{where}: `uncertain` needs a reason. Recording "
                                 "that somebody hesitated without recording what "
                                 "about is not a label")

        also = tuple(_segments(alt, where) for alt in (raw.get("also_acceptable") or []))

        fields = {str(k): str(v) for k, v in expected_fields.items()}
        rows[where] = Label(
            path=where,
            group=raw.get("group") or "",
            situation=situation,
            destination=destination,
            also_acceptable=also,
            expected_fields=fields,
            protected=protected,
            uncertain=uncertain,
            family=raw.get("family"),
            note=raw.get("note"),
            aliases=_aliases_for(fields, groups),
        )
    return Labels(rows, groups)

"""What P13 must not ask for, and what it must not hand onward as a folder name.

`74` §5.6, from `69` §3 blocker 3: a client's passport number became a group's
`display_label` and, under per-group acceptance, printed as a proposed FOLDER
NAME. This module is the P13 half of closing that; P12's half is its own task.

**A folder name is not a display.** Redacting a filename on a screen is a display
decision and follows §8.4's policy. Putting protected material on the disk as a
directory is not: the directory outlives the screen, is visible to everyone with
the volume, and appears in every backup, sync client and search index thereafter.
So `proposed_folder_name` takes no `RedactionSettings` at all and refuses whether
names are shown or redacted.

**The refusal raises; it does not mask.** A function that returned `"A1****67"`
is a code path that received the material and hid some of it -- and both ends of
a passport number are still a passport number. The SPEC's rule is that P13 has no
code path which receives protected content and then hides it, so the boundary is
one function that says the caller should not have asked, carrying the aggregate
it may show instead.

**Protectedness is P7's flag, and P13 derives it from no class.** P7's own rule
is that the protected count follows the `protected` flag and never the handling
class, because a `highly_sensitive_credential_bearing` record with
`protected=False` is legal while P7's Open question 1 is unsettled. There is no
sensitive-class set in this module: publishing a second one would answer P7's
open question in P13's code.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from privacy.display import HANDLING_CLASSES

from review_surface.vocabulary import check


@dataclass(frozen=True)
class AggregateSafeLabel:
    """§8.4's aggregate, for one label or many: a number and a kind.

    Two fields, and **deliberately no field a label could occupy**. §8.4's own
    example is "11 protected identity records" -- a count and a class, and
    nothing of the material. Every WORD of that sentence is deferred by the
    SPEC's Deferred table, so `text` carries P7's class verbatim rather than
    inventing an English noun for it; the renderer that has copy may compose one
    from the same two fields.
    """

    count: int
    handling_class: str

    @property
    def text(self) -> str:
        return f"{self.count} protected {self.handling_class}"


class ProposedNameFromProtectedMaterial(RuntimeError):
    """A label derived from protected material, offered as a folder name.

    Carries the aggregate the caller may show instead, and NEVER the label: a
    refusal that printed the material would put it in whatever reads the message.
    """

    def __init__(self, message: str, *, aggregate: AggregateSafeLabel,
                 position: int | None = None) -> None:
        super().__init__(message)
        self.aggregate = aggregate
        self.position = position


def aggregate_safe_label(*, count: int,
                         handling_class: str) -> AggregateSafeLabel:
    """The safe form. It takes the count and the class, and no route for a label."""
    check(handling_class, HANDLING_CLASSES, name="handling class")
    return AggregateSafeLabel(count=count, handling_class=handling_class)


def _fragments(material: str) -> set[str]:
    """Every contiguous run of `material` longer than one character.

    A single character is not a leak: any text long enough to be read shares
    letters with any material. A run of two or more is how a masked form gives
    the reader the ends of the thing it claimed to hide.
    """
    runs: set[str] = set()
    for start in range(len(material)):
        for stop in range(start + 1, len(material)):
            runs.add(material[start:stop + 1])
    return runs


def carries_no_material(text: str, material: str) -> bool:
    """Whether `text` is free of every run of `material` longer than one char."""
    return not any(run in text for run in _fragments(material))


def proposed_folder_name(*, display_label: str, protected: bool,
                         handling_class: str) -> str:
    """The label, if it may become a directory. Otherwise a refusal.

    `protected` is a required keyword with no default. Absent means refuse: P13
    does not decide whether material is protected, and a default here would be
    P13 deciding it is not.
    """
    check(handling_class, HANDLING_CLASSES, name="handling class")
    if not protected:
        return display_label
    raise ProposedNameFromProtectedMaterial(
        "a display label derived from protected material was offered as a "
        "proposed folder name. A folder name is written to the volume and "
        "outlives every screen it was reviewed on, so the redaction policy does "
        "not reach it. The label is not repeated here; show the aggregate on "
        "this exception instead",
        aggregate=aggregate_safe_label(count=1, handling_class=handling_class))


def proposed_folder_chain(segments: Sequence[tuple[str, bool]], *,
                          handling_class: str) -> tuple[str, ...]:
    """Every segment of an ancestor chain, or a refusal naming which one failed.

    `69` §3's case was a chain: the group's label became a TOP-LEVEL folder, so a
    guard that only examined the leaf would have materialised it anyway.
    """
    names: list[str] = []
    for position, (display_label, protected) in enumerate(segments):
        try:
            names.append(proposed_folder_name(
                display_label=display_label, protected=protected,
                handling_class=handling_class))
        except ProposedNameFromProtectedMaterial as refusal:
            raise ProposedNameFromProtectedMaterial(
                f"segment {position} of this proposed chain is derived from "
                "protected material, so no part of the chain may be "
                "materialised. The segment is named by position rather than by "
                "value",
                aggregate=refusal.aggregate, position=position) from None
    return tuple(names)

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

**The question is about the LABEL'S PROVENANCE, not about the folder's contents,**
which is why the keyword is spelled `derived_from_protected_material` and not
`protected`. "Passport Scans" is a perfectly good name for a folder full of
protected documents; `A1234567` is not a good name for anything. A caller that
handed this the folder's protectedness would strip the name off every protected
folder a person already has -- their own words, taken away because of what is
inside. The keyword says which of the two it wants.
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


def proposed_folder_name(*, display_label: str,
                         derived_from_protected_material: bool,
                         handling_class: str) -> str:
    """The label, if it may become a directory. Otherwise a refusal.

    `derived_from_protected_material` is a required keyword with no default.
    Absent means refuse: P13 decides nothing about provenance, and a default here
    would be P13 deciding the label is safe.
    """
    check(handling_class, HANDLING_CLASSES, name="handling class")
    if not derived_from_protected_material:
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

    Each segment is `(display_label, derived_from_protected_material)`. `69` §3's
    case was a chain: the group's label became a TOP-LEVEL folder, so a guard
    that only examined the leaf would have materialised it anyway.
    """
    names: list[str] = []
    for position, (display_label, derived) in enumerate(segments):
        try:
            names.append(proposed_folder_name(
                display_label=display_label,
                derived_from_protected_material=derived,
                handling_class=handling_class))
        except ProposedNameFromProtectedMaterial as refusal:
            raise ProposedNameFromProtectedMaterial(
                f"segment {position} of this proposed chain is derived from "
                "protected material, so no part of the chain may be "
                "materialised. The segment is named by position rather than by "
                "value",
                aggregate=refusal.aggregate, position=position) from None
    return tuple(names)


# --------------------------------------------------------------------------
# §8.4's aggregate, the filename P13 never asks for, and the retraction limit.
#
# The rule above -- P13 has NO code path that receives protected content and then
# hides it -- is honoured here the same way: `name_for` RAISES. A function
# returning "[redacted]" would be exactly the forbidden path, because it received
# the name and hid it. A function that raises is one that says the caller should
# not have asked, and its message deliberately does not repeat the name.
#
# D11's two denominators are kept apart by construction. `count` is the PROTECTED
# count. `class_breakdown` is a census of the WHOLE SCOPE, zero-filled across
# `HANDLING_CLASSES`, so `sum(class_breakdown.values())` is `scope_total` and not
# `count`. A percentage built from the two would describe an unprotected file as
# protected -- and it is the sort of error a passing suite hides, because the
# arithmetic runs and the number looks reasonable.
#
# SCOPE: `privacy.display.display_policy(conn, *, plan_version)` takes NO scope
# argument, so nothing here takes one either. SPEC Open question 7 -- whether the
# setting is per-branch or global -- is P7's and is open; inventing a scope
# argument would answer it in P13's code.
# --------------------------------------------------------------------------

from privacy.display import ProtectedSummary  # noqa: E402
from privacy.revocation import PriorRelease, RevocationResult  # noqa: E402
from privacy.vocabulary import REDACTED, SHOWN  # noqa: E402


class NameRedacted(RuntimeError):
    """A filename was asked for that the display policy does not permit."""


class ProtectedSetNotExpandable(RuntimeError):
    """A protected aggregate was asked to become a list while names redact."""


def name_for(*, protected: bool, settings: RedactionSettings,
             filename: str) -> str:
    """The name, or a refusal. Never a mask.

    The refusal message does not contain `filename`. A message that quoted the
    name it refused would put it in a log, a traceback and an error surface --
    three places a redaction policy has no reach.
    """
    if protected and settings.names == REDACTED:
        raise NameRedacted(
            "the display policy redacts names and this file is protected. No "
            "surface -- canvas, placement review, residual screen, apply screen "
            "or evaluation view -- renders a filename for a protected file "
            "under this policy (§8.4). Show the protected aggregate instead")
    return filename


@dataclass(frozen=True)
class ProtectedAggregate:
    """§8.4's aggregate over a scope, with D11's two denominators kept apart."""

    count: int
    scope_total: int
    class_breakdown: Mapping[str, int]
    sentence: str
    expandable: bool

    def expand(self) -> tuple[str, ...]:
        """The member list, or a refusal. Never a partial list."""
        if not self.expandable:
            raise ProtectedSetNotExpandable(
                "this protected set cannot be expanded into a filename list "
                "while the display policy redacts names (§8.4, §7.5). §8.4's "
                "own example is that a summary may be safe to show where a "
                "visible list of passport filenames on a shared screen is not")
        # P13 holds no member list of its own. When the policy permits names the
        # caller asks P7 for them; an empty tuple here says "this object is not
        # where the names live", which is true and is better than inventing one.
        return ()


def protected_aggregate(summary: ProtectedSummary, *,
                        settings: RedactionSettings) -> ProtectedAggregate:
    """§8.4's aggregate form. The breakdown is zero-filled across every class.

    `67` §1: protected material is marked and COUNTED, and never silently
    omitted. A class absent from the breakdown would read as a class that does
    not exist rather than one with nothing in it.
    """
    breakdown = {klass: int(summary.class_breakdown.get(klass, 0))
                 for klass in HANDLING_CLASSES}
    return ProtectedAggregate(
        count=summary.count,
        scope_total=summary.scope_total,
        class_breakdown=breakdown,
        sentence=(
            f"{summary.count} protected item(s) are present and were not "
            f"opened, out of {summary.scope_total} file(s) in scope."),
        expandable=settings.names == SHOWN)


@dataclass(frozen=True)
class RetractionStatement:
    """§8.4's revocation limit, said about real releases rather than in general."""

    effective_from: str
    retraction_limit: str
    prior_releases: tuple[PriorRelease, ...]
    sentence: str
    is_generic: bool


def retraction_statement(result: RevocationResult) -> RetractionStatement:
    """Done-means 17: specific, listing the prior releases. Never a disclaimer.

    `is_generic` is always False and it is a FIELD rather than a constant so a
    consumer can assert on it. If a future change ever produces a generic
    statement, the flag is where that becomes visible instead of the sentence
    quietly getting shorter. P7's own limit sentence is included INSIDE the
    statement rather than replaced by it.
    """
    releases = tuple(result.prior_releases)
    if releases:
        listed = "; ".join(
            f"{release.model} at {release.provider} on {release.when} "
            f"({len(release.excerpts)} excerpt(s))" for release in releases)
        body = (f"{len(releases)} prior release(s) were made before this "
                f"revocation took effect on {result.effective_from}: {listed}.")
    else:
        body = ("No prior release was made before this revocation took effect "
                f"on {result.effective_from}.")
    return RetractionStatement(
        effective_from=result.effective_from,
        retraction_limit=result.retraction_limit,
        prior_releases=releases,
        sentence=f"{body} {result.retraction_limit}",
        is_generic=False)

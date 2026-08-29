# src/privacy/display.py
"""§8.4's UI privacy: the five configurable facets, and the aggregate-safe summary.

§8.4's paragraph gives both surfaces and both defaults. The facets are its own list --
"whether names, previews, thumbnails, OCR text, or location data are shown" -- and the
default direction is its own example: "A summary such as '11 protected identity
records' may be safe to show, while a visible list of passport filenames on a shared
screen may not be." The aggregate is the default; the expansion is the user's act.

`ProtectedSummary` says Done-means 10 -- "cannot return filenames or content" -- in
its TYPES: three fields, every one an `int` or a `Mapping[str, int]`, and no field a
filename could occupy. The cheapest way to make that true is for there to be nowhere
to put one.

**This module publishes no value vocabulary.** `SHOWN`, `REDACTED` and
`REDACTION_VALUES` are Task 2's, in `privacy.vocabulary`, and are imported from there.
They had three homes and three names across this plan -- `REDACTION_VALUES` in
`policy.py`, `SETTING_VALUES` here, `FACET_VALUES` in a sibling draft -- for one
two-member vocabulary SPEC §10 states once ("each `shown | redacted`"). One home, one
name; `SETTING_VALUES` is deleted rather than re-exported, because a second spelling
that resolves to the same tuple is exactly what makes a second home survive review.
Only the tuple is imported here, because only the tuple is used.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.defaults import MORE_REDACTING
from privacy.policy import current_policy
from privacy.vocabulary import DISPLAY_FACETS, HANDLING_CLASSES, REDACTION_VALUES


class UnknownDisplaySetting(ValueError):
    """A facet or a value outside §8.4's list. A load error, never a fallback."""


@dataclass(frozen=True)
class RedactionSettings:
    """§8.4's five configurable facets, in §8.4's order."""

    names: str
    previews: str
    thumbnails: str
    ocr_text: str
    location_data: str

    def facet(self, name: str) -> str:
        if name not in DISPLAY_FACETS:
            raise UnknownDisplaySetting(
                f"{name!r} is not one of §8.4's five display facets {DISPLAY_FACETS}")
        return getattr(self, name)


@dataclass(frozen=True)
class ProtectedSummary:
    """§8.4's aggregate: "11 protected identity records", and nothing that names a file.

    Three fields, all `int` or `Mapping[str, int]`, and **deliberately no field a
    filename could occupy**. There is no `examples`, no `file_ids` and no `filenames`,
    because Done-means 10 forbids returning one and a field that does not exist cannot
    be populated by a later caller in a hurry. The constraint is asserted with
    `typing.get_type_hints`, not by matching field names against a banned list: the
    types are what hold, and a name-based check passes any field nobody thought to ban.

    **Two denominators, and they are not interchangeable (D11).** `count` is the number
    of PROTECTED files in scope. `class_breakdown` is a census of the WHOLE scope by
    resolved class, zero-filled across `HANDLING_CLASSES` and keyed in that order, and
    `scope_total` is its denominator: `sum(class_breakdown.values()) == scope_total`,
    which is `len(files_in_scope(scope))` and is **not** `count`. A caller that rendered
    §8.4's "11 protected identity records" off the breakdown would describe an
    unprotected file as protected -- a `highly_sensitive_credential_bearing` record with
    `protected=False` is legal while Open question 1 is unsettled -- so the denominator
    is published rather than assumed.
    """

    count: int
    scope_total: int
    class_breakdown: Mapping[str, int]


def display_policy(conn: sqlite3.Connection, *,
                   plan_version: str) -> RedactionSettings:
    """The five facets as they resolve under the policy in force for `plan_version`.

    A facet the stored policy does not mention resolves through `MORE_REDACTING`, never
    to `shown`: §8.4's `must` is that the default posture be "local-first and
    data-minimizing", and §8.4's own example settles which direction that points. A
    plan version with NO policy at all is the same case with every facet absent, and it
    resolves to the same floor -- `defaults.resolve_default_policy(None, ...)` is where
    that rule is written down, and this reads it the same way rather than raising and
    leaving a caller to pick a posture.

    `plan_version` is a keyword because §8.8 places "Privacy and model-consent policies"
    inside the plan version. SPEC §10's published surface is `Gate.display_policy()`;
    the facade holds the plan version and supplies it here.

    A read (C4): no event, no policy version, no `UPDATE files`.
    """
    policy = current_policy(conn, plan_version=plan_version)
    stored = {} if policy is None else dict(policy.redaction_settings)
    unknown = [facet for facet in stored if facet not in DISPLAY_FACETS]
    if unknown:
        raise UnknownDisplaySetting(
            f"{sorted(unknown)} are not among §8.4's five display facets "
            f"{DISPLAY_FACETS}")
    resolved = {}
    for facet in DISPLAY_FACETS:
        value = stored.get(facet, MORE_REDACTING[facet])
        if value not in REDACTION_VALUES:
            raise UnknownDisplaySetting(
                f"{facet} = {value!r} is not one of {REDACTION_VALUES}; a value "
                "outside the set is a load error, not a fallback")
        resolved[facet] = value
    return RedactionSettings(**resolved)


def summarize_protected(conn: sqlite3.Connection, scope: str, *,
                        store: ClassificationStore,
                        files_in_scope: Callable[[str], Sequence[str]]
                        ) -> ProtectedSummary:
    """Counts only. §5.2: "avoid showing sensitive filenames"; §7.5: "11 protected
    personal records".

    `count` follows the `protected` flag, never the handling class (SPEC §2, Open
    question 1). `class_breakdown` covers every file in scope by its RESOLVED class,
    so a corpus nothing has classified reports `unreadable_unclassified` rather than
    disappearing -- which is today's ordinary state, since D2 leaves the detector
    unwritten -- and `scope_total` is the breakdown's denominator, which is the number
    of files in scope and NOT `count` (D11). The two are separated because they answer
    two questions, and one number cannot answer both without lying about one.

    Reads only (C4). No event, no policy version, no `UPDATE files`.

    `files_in_scope` has no default: Open question 3 leaves "corpus area" unnamed.
    """
    counts = {handling_class: 0 for handling_class in HANDLING_CLASSES}
    protected = 0
    in_scope = 0
    for file_id in files_in_scope(scope):
        record = store.current(file_id, get_file(conn, file_id)["content_hash"])
        counts[resolve_class(record)] += 1
        in_scope += 1
        if record is not None and record.protected:
            protected += 1
    return ProtectedSummary(count=protected, scope_total=in_scope,
                            class_breakdown=MappingProxyType(counts))

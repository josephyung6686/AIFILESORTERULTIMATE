"""The proposed folder tree, with P13's folder-name boundary applied to it.

`69` §3 blocker 3: a client's passport number became a group's `display_label`
and, under per-group acceptance, printed as a proposed FOLDER NAME.
`review_surface.redaction_boundary` is P13's half of closing that and shipped
complete -- and was called by nothing outside its own test, so the guard and the
hole were the same length. `src/cli.py`'s tree printer takes `node.display_label`
and prints it, which is exactly the sabotage that module's own docstring
describes. This is the join.

**A folder name is not a display.** Redacting a filename on a screen follows
§8.4's policy; a directory outlives the screen and appears in every backup, sync
client and search index thereafter. So nothing here takes `RedactionSettings`,
and `--show-protected` does not reach it: a person asking to see their own
protected FILENAMES has not asked for a passport number to become a folder.

**Provenance is a join, not a string search.** `grouping.naming.label_for` is
"the anchor values, deduplicated, in the order the facts carry them" -- so a
group's label is derived from protected material exactly when one of its anchor
facts stands on a file P7 flagged, and `AnchorFact.file_ids` carries that join
with nothing left to infer. `redaction_boundary.carries_no_material` is the
tempting shortcut and is the wrong tool: it refuses on any shared run of two
characters, which is what makes it a good check on a MASKED form and a
catastrophic one on provenance -- "Columbia 2026" beside a protected observation
reading "2026-01-01" shares "20", and a person's own folder name would come off
their tree with nothing on the screen saying why.

**Protectedness is P7's flag and is read live.** Never the handling class: a
`highly_sensitive_credential_bearing` record with `protected=False` is legal
while P7's Open question 1 is unsettled. A superseded classification is a claim
that was withdrawn and stops answering, which is why `superseded_by IS NULL` is
in the query rather than in a comment.

**The label is replaced, never dropped.** A node whose name is refused still
prints -- as `aggregate_safe_label`'s count and class -- because "marked and
counted, never silently omitted" has no exception for a folder. A blank line in a
tree is the same failure as a leak, in the other direction.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.records import Node

from review_surface.redaction_boundary import (
    ProposedNameFromProtectedMaterial,
    proposed_folder_name,
)

__all__ = ["ProtectedLabel", "folder_label", "protected_label_provenance"]


@dataclass(frozen=True)
class ProtectedLabel:
    """A group's label, and the class of the protected material it came from.

    Both halves are needed and neither is a substitute for the other. The class
    is what the aggregate may say. The label is how a node is matched to the
    group that authored its name -- see `folder_label` -- and matching on the
    group id alone would strip every template branch that merely HOLDS the group.
    """

    display_label: str
    handling_class: str


def protected_label_provenance(
        conn: sqlite3.Connection, *,
        group_ids: Sequence[str]) -> Mapping[str, ProtectedLabel]:
    """The groups whose `display_label` was minted from a protected file.

    A group with no live protected anchor file is simply absent. Absence means
    safe HERE and only here: the refusal itself lives in `proposed_folder_name`,
    which takes the answer as a required keyword with no default, so nothing
    downstream can arrive at "safe" by forgetting to ask.

    The handling class is the CLASSIFICATION'S, not the node's. The aggregate
    says "1 protected <class>", which is a statement about the material the label
    came from; the node's own class is P10's collapse over its members and would
    describe a different thing under the same words.

    A group whose label is NULL is skipped rather than defaulted. P9's schema
    permits `display_label IS NULL` on any group below §4.9's bar, and a group
    with no name has no name to refuse.
    """
    provenance: dict[str, ProtectedLabel] = {}
    for group_id in group_ids:
        row = conn.execute(
            "SELECT anchor_facts, display_label FROM groups "
            "WHERE group_id = ? AND superseded_by IS NULL",
            (group_id,)).fetchone()
        if row is None or not row[1]:
            continue
        file_ids = {file_id
                    for fact in json.loads(row[0] or "[]")
                    for file_id in fact.get("file_ids", ())}
        if not file_ids:
            continue
        marks = ",".join("?" * len(file_ids))
        found = conn.execute(
            "SELECT handling_class FROM classifications "
            f"WHERE file_id IN ({marks}) AND protected = 1 "
            "  AND superseded_by IS NULL "
            "ORDER BY observed_at, fact_id LIMIT 1",
            tuple(sorted(file_ids))).fetchone()
        if found is not None:
            provenance[group_id] = ProtectedLabel(
                display_label=row[1], handling_class=found[0])
    return provenance


def folder_label(node: Node, *,
                 provenance: Mapping[str, ProtectedLabel]) -> str:
    """The one string a tree may print for this node.

    A node's label came FROM a group exactly when it EQUALS that group's label:
    P10 copies `candidate.display_label` onto the node it builds
    (`tree_design/pipeline.py`), so the equality IS the provenance and not a
    guess about it. Refusing on association alone would strip the name off every
    template branch holding one protected file -- which is most people's
    corpus -- and the tree would be unreadable for the wrong reason.

    `provenance` is what `protected_label_provenance` returns and is a required
    keyword. A default of `{}` would make every caller that forgot it print every
    label, which is the state this module exists to end.
    """
    for group_id in node.associated_group_ids:
        protected = provenance.get(group_id)
        if protected is None or protected.display_label != node.display_label:
            continue
        try:
            return proposed_folder_name(
                display_label=node.display_label,
                derived_from_protected_material=True,
                handling_class=protected.handling_class)
        except ProposedNameFromProtectedMaterial as refusal:
            return refusal.aggregate.text
    return node.display_label

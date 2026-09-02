"""§8.3's `Requested destination node` -> `Resolved destination path`.

The two fields are separate in §8.3 precisely because the request is an ID and the
resolution is platform-specific. P10's tree is addressed by ID and holds no path
(`tree_design/records.py::_no_separator` says so and names P12 as the composer);
P12 composes downward from the one concrete anchor.

Five rules from the SPEC, each implemented once here:
 1. the anchor is the only path P12 is given
 2. an `existing` ancestor short-circuits the composition and its path is verbatim
 3. every composed segment is normalized as a path component
 4. resolution is evaluated against the TARGET volume's constraints
 5. two sibling labels normalizing to one filesystem name are REFUSED, never merged

**Amended by `74` §5.1.** The P12 PLAN's F1 says `root_anchor` has a consumer and
no producer, and treats the anchor as the base of every composition. `Node
.existing_path` is the narrower and truer answer: it is a real, observed path
carried on every `existing` node and refused on every other node type, and
`cli.py` adopts the person's own folders as `existing` nodes. So the base is the
NEAREST `existing` ancestor's path, and `root_anchor` is consulted only when no
ancestor on the chain is `existing`. F1 stands for that case and only that case.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json
from privacy.vocabulary import HANDLING_CLASSES
from tree_design.records import EXISTING, PROTECTED, Node

from mutation.constraints import FilesystemConstraints
from mutation.names import collation_key, resolve_name
from mutation.vocabulary import (
    CROSS_FOLDER_NOT_PERMITTED, CROSS_FOLDER_VERDICTS, CROSS_ROOT_PERMITTED,
    CROSS_ROOT_REFUSED, NODE_NOT_IN_FROZEN_TREE, NODE_PATH_COLLISION,
    PROTECTED_WITHOUT_POLICY, REFUSED_MOVE, SUBSYSTEM, WITHIN_ROOT, check,
    decline_message,
)


class ResolutionRefused(RuntimeError):
    """One of Contract out §5's refusal classes, raised during resolution."""

    def __init__(self, refusal_class: str, message: str, *,
                 detail: Mapping[str, object]) -> None:
        super().__init__(message)
        self.refusal_class = refusal_class
        self.detail = dict(detail)


class RootAnchorUnresolved(RuntimeError):
    """F1. A `root_anchor` with no path in the injected §1.1 folder landscape.

    NOT a refusal class: a refusal describes a plan that could not execute, and
    this is a missing input. Deriving the path here would put a real filesystem
    destination in P12's source, which §5.12 and §6.12 forbid.

    Raised only when the chain carries no `existing` ancestor either -- `74` §5.1.
    """


class ProtectedClassesRequired(RuntimeError):
    """The composition root's declaration of which handling classes are protected.

    Injected with NO default, and refused when empty or misspelled. P7 is
    explicit that a neighbour *"should consume the `protected` flag, not infer it
    from the class"* (`privacy/classification.py:110-113`), and `Node` carries a
    `handling_class` and no flag -- so P12 cannot derive this set without
    answering P7's own Open question 1 on its behalf. A7: absent means refuse,
    never guess.

    **What it no longer does is decide a refusal.** It was the proxy P12 used for
    "was this label composed from protected material", and `94` F1 is the record
    of that proxy being wrong: the field it was matched against is P10's FLOOR,
    which one protected member raises for a whole branch. `_refuse_protected_label`
    now reads `protected_label_classes`, which is provenance. This declaration is
    still validated here, still cannot be forgotten or emptied, and is now
    consumed by nothing in `src/mutation/`; retiring it is a change to
    `src/cli.py`'s `freeze(...)` call and to `apply_run.freeze`'s signature at
    the same instant, which is the composition root's to make and not P12's.
    """


class CyclicAncestorChain(RuntimeError):
    """A tree whose parent links loop. Corrupt structure, not a user outcome."""


class MalformedChain(RuntimeError):
    """An `existing` node carrying no `existing_path`. §5.10 guarantees one."""


@dataclass(frozen=True)
class Segment:
    node_id: str
    node_type: str
    intended_display_label: str
    filesystem_safe_segment: str
    normalizations_applied: tuple[str, ...]


@dataclass(frozen=True)
class PathResolution:
    resolution_id: str
    plan_version: str
    requested_destination_node: str
    root_anchor: str
    #: `None` when the chain resolved through an `existing` ancestor and the
    #: injected landscape does not carry this anchor. Not a gap: the anchor's
    #: path was not needed, and recording `None` says exactly that rather than
    #: implying one was found (`74` §5.1, F1).
    root_anchor_path: str | None
    ancestor_chain: tuple[tuple[str, str, str], ...]
    nearest_existing_ancestor: str | None
    nearest_existing_path: str | None
    segments_composed: tuple[Segment, ...]
    resolved_destination_directory: str
    directories_that_must_be_created: tuple[str, ...]
    target_volume: str
    cross_folder_verdict: str

    def __post_init__(self) -> None:
        check(self.cross_folder_verdict, CROSS_FOLDER_VERDICTS,
              name="cross_folder_verdict")


def _chain(node_id: str, by_id: Mapping[str, Node]) -> list[Node]:
    """Root-first ancestor chain, by walking `parent_node_id` upward (rule 1)."""
    walked: list[Node] = []
    seen: set[str] = set()
    current = by_id.get(node_id)
    if current is None:
        raise ResolutionRefused(
            NODE_NOT_IN_FROZEN_TREE,
            "the requested destination is not a node of this frozen tree",
            detail={"node_id": node_id})
    while current is not None:
        if current.node_id in seen:
            raise CyclicAncestorChain(
                f"parent links loop at {current.node_id!r}; this tree cannot be "
                "walked to a root")
        seen.add(current.node_id)
        walked.append(current)
        if current.parent_node_id is None:
            break
        parent = by_id.get(current.parent_node_id)
        if parent is None:
            raise ResolutionRefused(
                NODE_NOT_IN_FROZEN_TREE,
                "an ancestor of the requested destination is not in this frozen tree",
                detail={"node_id": node_id,
                        "missing_ancestor": current.parent_node_id})
        current = parent
    walked.reverse()
    return walked


def _require_protected_classes(value: object) -> frozenset[str]:
    if not isinstance(value, frozenset) or not value:
        raise ProtectedClassesRequired(
            "protected_handling_classes is a non-empty frozenset supplied by the "
            "composition root; it has no default and an empty set is not one")
    unknown = sorted(value - set(HANDLING_CLASSES))
    if unknown:
        raise ProtectedClassesRequired(
            f"not §8.4 handling classes: {unknown}. A misspelling here would "
            "match no node and disable the guard without failing")
    return value


def _refuse_protected_label(item: Node,
                            protected_label_classes: Mapping[str, str]) -> None:
    """`74` §5.6. A segment is never composed from a protected label.

    `69` §3 blocker 3: a client's passport number reached a group's
    `display_label` and printed as a proposed folder name. A folder name is the
    most durable and most visible place protected material can land -- it appears
    in every listing, every backup and every sync -- so composition refuses, and
    the refusal names the NODE. Putting the label in the refusal would move the
    protected material from one record into another.

    **The answer is PROVENANCE and is injected. It is not `Node.handling_class`,
    and reading that field here was `94` F1.** P10 writes a node's class as the
    collapse to the STRONGEST class among the branch's members (`src/cli.py`'s
    `collapse_handling_classes`, which is §5.2's privacy ordering and the floor
    that stops a passport landing somewhere weaker). Two parts then read one
    field two ways: to P10 it is *the floor for what may be filed here*, to this
    guard it was *this label was composed from protected material*. A branch
    called `Coursework` holding one passport scan is not composed from anything
    protected -- its floor is high because one member is -- and refusing it
    refused every ordinary file under it and told the person their coursework was
    the protected thing. One file in a folder made the whole folder unmovable.

    So the caller supplies the join it can actually make:
    `review_run.structure.protected_label_classes` matches a node's label against
    the label of the group that authored it, and that group's label against the
    anchor facts that composed it. `74` §5.6's C4 says "a segment whose source
    node carries a protected `handling_class`"; that sentence named the field
    available at the time and the guard it describes is unchanged -- what changed
    is that the field now means what the sentence says.

    An EMPTY mapping is a real and common answer -- most trees name nothing after
    protected material -- so unlike `protected_handling_classes` it is not
    refused. What is refused is its ABSENCE: it is a required keyword all the way
    up, so no caller arrives at "nothing here is protected" by forgetting to ask.

    Only COMPOSED segments are checked. An `existing` ancestor's path is a folder
    the person already has; P12 neither minted its name nor may rename it.
    """
    handling_class = protected_label_classes.get(item.node_id)
    if handling_class is not None:
        raise ResolutionRefused(
            PROTECTED_WITHOUT_POLICY,
            "a folder name for this level would be composed from protected "
            "material, so no path was composed",
            detail={"node_id": item.node_id,
                    "handling_class": handling_class,
                    "parent_node_id": item.parent_node_id})


def _refuse_protected_container(item: Node) -> None:
    """A marked container is never a folder on a composed path.

    `84` §1: a protected container is marked and counted and NEVER OPENED, and
    `tree_design.candidates.protected_area_nodes` mints it with
    `accepts_placement=False` so nothing may be filed IN it. Composing a path
    THROUGH it is the same act one level up -- it would create a directory
    inside a sealed bundle -- and it is refused here rather than being left to
    the fact that P10 builds no children under one today.

    Split from the label guard above because it is a different claim about a
    different thing: that guard asks where a NAME came from, this one asks what
    a NODE is. `node_type` is the answer to the second and always was; the class
    check that used to stand in for it is what `94` F1 was.
    """
    if item.node_type == PROTECTED:
        raise ResolutionRefused(
            PROTECTED_WITHOUT_POLICY,
            "this level is a protected container, which is marked and counted "
            "and is not a place anything can be filed, so no path was composed",
            detail={"node_id": item.node_id,
                    "handling_class": item.handling_class,
                    "parent_node_id": item.parent_node_id})


def _segment_key(label: str, constraints: FilesystemConstraints) -> str:
    """The name one label would occupy on the target volume."""
    return collation_key(
        resolve_name(label, constraints=constraints, directory_byte_length=0,
                     has_extension=False).filesystem_safe_name,
        constraints=constraints)


def _refuse_sibling_collision(child: Node, nodes: Sequence[Node],
                              constraints: FilesystemConstraints,
                              protected_label_classes: Mapping[str, str]) -> None:
    """Rule 5. Two sibling nodes whose distinct labels normalize to one name.

    Merging them would collapse two frozen nodes into one destination the user
    never approved -- which §6.12's *"No system component may invent a new
    destination after freeze"* forbids, and which the freeze guarantee contradicts
    because the legal destination set IS the set of frozen nodes (§5.12).
    """
    key = _segment_key(child.display_label, constraints)
    for other in nodes:
        if other.node_id == child.node_id:
            continue
        if other.parent_node_id != child.parent_node_id:
            continue
        if other.display_label == child.display_label:
            continue
        if _segment_key(other.display_label, constraints) == key:
            # The collision refusal names both labels so the person can rename
            # one. A protected sibling would put protected material into that
            # list, so `74` §5.6 wins and the label stays out of the record.
            _refuse_protected_label(other, protected_label_classes)
            raise ResolutionRefused(
                NODE_PATH_COLLISION,
                "two folders in this plan would become one folder on disk",
                detail={"labels": sorted((child.display_label,
                                          other.display_label)),
                        "node_ids": sorted((child.node_id, other.node_id)),
                        "colliding_name": key,
                        "parent_node_id": child.parent_node_id})


def _source_folder(source_path: Path,
                   high_level_folders: Mapping[str, Path]) -> str | None:
    """Which §1.1 high-level folder the source currently lives under.

    Longest match wins, so a nested named folder is reported rather than its
    parent. `None` means the source is under none of them -- see F11.
    """
    best: str | None = None
    best_length = -1
    for name, folder in high_level_folders.items():
        try:
            source_path.relative_to(folder)
        except ValueError:
            continue
        length = len(folder.parts)
        if length > best_length:
            best, best_length = name, length
    return best


def resolve_destination(*, plan_version: str, node_id: str,
                        nodes: Sequence[Node],
                        source_path: Path,
                        high_level_folders: Mapping[str, Path],
                        constraints: FilesystemConstraints,
                        cross_folder_moves: bool,
                        volume_of: Callable[[Path], str],
                        mint_resolution_id: Callable[[], str],
                        protected_handling_classes: frozenset[str],
                        protected_label_classes: Mapping[str, str],
                        ) -> PathResolution:
    protected_handling_classes = _require_protected_classes(
        protected_handling_classes)
    by_id = {item.node_id: item for item in nodes}
    chain = _chain(node_id, by_id)

    # Rule 2, as amended by `74` §5.1: the NEAREST `existing` ancestor -- the
    # deepest one on the chain -- short-circuits. Its path is used verbatim and
    # never recomposed from its `display_label`, because §5.10 preserves existing
    # folders as they are and a user alias over an existing folder must not
    # silently retarget the write.
    existing_index = max(
        (index for index, item in enumerate(chain) if item.node_type == EXISTING),
        default=-1)
    root_anchor = chain[0].root_anchor
    if existing_index >= 0:
        anchor_node = chain[existing_index]
        if not anchor_node.existing_path:
            raise MalformedChain(
                f"node {anchor_node.node_id!r} is `existing` and carries no "
                "`existing_path`; §5.10 guarantees one")
        base = Path(anchor_node.existing_path)
        nearest_existing_ancestor: str | None = anchor_node.node_id
        nearest_existing_path: str | None = anchor_node.existing_path
        below = chain[existing_index + 1:]
    else:
        if root_anchor not in high_level_folders:
            raise RootAnchorUnresolved(
                f"root_anchor {root_anchor!r} has no path in the injected §1.1 "
                "folder landscape, and no ancestor on this chain is `existing`, "
                "so nothing on it carries a real path. P10 publishes an "
                "identifier and P3 publishes bare paths; nothing joins them (F1). "
                "P12 refuses rather than deriving one, because a derived path is "
                "a destination nobody approved")
        base = high_level_folders[root_anchor]
        nearest_existing_ancestor = None
        nearest_existing_path = None
        below = chain

    # Rules 3 and 4: every composed segment is normalized as a path component
    # against the TARGET volume's constraints, and each keeps its intended label
    # beside its filesystem-safe form so a normalization change stays explainable
    # at any level of the path, not only the last.
    directory = base
    segments: list[Segment] = []
    created: list[str] = []
    for item in below:
        _refuse_protected_container(item)
        _refuse_protected_label(item, protected_label_classes)
        _refuse_sibling_collision(item, nodes, constraints,
                                  protected_label_classes)
        resolved = resolve_name(
            item.display_label, constraints=constraints,
            directory_byte_length=len(str(directory).encode("utf-8")),
            has_extension=False)
        segments.append(Segment(
            node_id=item.node_id, node_type=item.node_type,
            intended_display_label=item.display_label,
            filesystem_safe_segment=resolved.filesystem_safe_name,
            normalizations_applied=resolved.normalizations_applied))
        directory = directory / resolved.filesystem_safe_name
        created.append(str(directory))

    source_folder = _source_folder(source_path, high_level_folders)
    if source_folder == root_anchor:
        verdict = WITHIN_ROOT
    elif cross_folder_moves:
        verdict = CROSS_ROOT_PERMITTED
    else:
        verdict = CROSS_ROOT_REFUSED
    if verdict == CROSS_ROOT_REFUSED:
        raise ResolutionRefused(
            CROSS_FOLDER_NOT_PERMITTED,
            "§1.1's cross-folder movement permission is off and this move would "
            "cross a high-level folder",
            detail={"source_high_level_folder": source_folder,
                    "destination_root_anchor": root_anchor,
                    "source_path": str(source_path),
                    "cross_folder_moves": False})

    anchor_path = high_level_folders.get(root_anchor)
    return PathResolution(
        resolution_id=mint_resolution_id(),
        plan_version=plan_version,
        requested_destination_node=node_id,
        root_anchor=root_anchor,
        root_anchor_path=None if anchor_path is None else str(anchor_path),
        ancestor_chain=tuple(
            (item.node_id, item.node_type, item.display_label) for item in chain),
        nearest_existing_ancestor=nearest_existing_ancestor,
        nearest_existing_path=nearest_existing_path,
        segments_composed=tuple(segments),
        resolved_destination_directory=str(directory),
        directories_that_must_be_created=tuple(created),
        target_volume=volume_of(base),
        cross_folder_verdict=verdict,
    )


def record_resolution(conn: sqlite3.Connection, resolution: PathResolution, *,
                      created_at: str, record_id: str) -> str:
    """Append one resolution record. `payload` is its one home."""
    conn.execute(
        "INSERT INTO path_resolutions (record_id, resolution_id, plan_version, "
        "node_id, cross_folder_verdict, created_at, payload) VALUES (?,?,?,?,?,?,?)",
        (record_id, resolution.resolution_id, resolution.plan_version,
         resolution.requested_destination_node, resolution.cross_folder_verdict,
         created_at, canonical_json(asdict(resolution))))
    return record_id


def resolution_by_id(conn: sqlite3.Connection,
                     resolution_id: str) -> PathResolution | None:
    row = conn.execute(
        "SELECT payload FROM path_resolutions WHERE resolution_id = ? "
        "AND superseded_by IS NULL", (resolution_id,)).fetchone()
    if row is None:
        return None
    raw = json.loads(row[0])
    raw["ancestor_chain"] = tuple(tuple(item) for item in raw["ancestor_chain"])
    raw["segments_composed"] = tuple(
        Segment(**{**item,
                   "normalizations_applied": tuple(item["normalizations_applied"])})
        for item in raw["segments_composed"])
    raw["directories_that_must_be_created"] = tuple(
        raw["directories_that_must_be_created"])
    return PathResolution(**raw)


def record_resolution_refusal(conn: sqlite3.Connection,
                              refusal: ResolutionRefused, *,
                              observed_at: str,
                              component_version: str,
                              file_id: str | None = None,
                              content_hash: str | None = None,
                              user_id: str | None = None) -> int:
    """Append §8.2's `refused move` for one resolution refusal.

    `74` §5.2 closes PLAN F13: the name exists, P12 is its only writer, and every
    refusal in `74` §3.3 appends one. The `explanation` carries `66` §10's
    distinct sentence for the class plus the refusal's own detail, so the row a
    person reads says what occurred and what they can do about it.

    What the row must NOT carry is the protected material itself -- which is why
    `_refuse_protected_label` builds a detail naming the node and never the
    label. This function serializes whatever the refusal put in `detail`; the
    decision about what may be in there belongs to the refusal that raised.
    """
    return append_event(
        conn,
        event_type=REFUSED_MOVE,
        subsystem=SUBSYSTEM,
        component_version=component_version,
        observed_at=observed_at,
        file_id=file_id,
        content_hash=content_hash,
        user_id=user_id,
        explanation=(f"{decline_message(refusal.refusal_class)} "
                     f"{canonical_json(refusal.detail)}"),
    )

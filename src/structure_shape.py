"""Shape the proposed tree before the outline is written.

A scan adopts each folder it found, so Finder copies and CourseWorks exports
stay top-level peers of one another. This pass is the minute a person would
spend fixing that before they edit the outline. It does not mint a new plan
and it does not drop a node id the outline still shows: copies that collapse
away are the empty ones, and a folder that still holds files keeps its id.

`structure_rows` applies it to the outline `--structure-out` writes.
`structure_edits` applies the same pass, so the file handed back is the walk
that was written.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import replace

from tree_design.records import ExpectedValue, Node
from tree_design.vocabulary import ARCHIVE, PROPOSED, PROTECTED, REVIEW_AND_UNSORTED

__all__ = ["course_key", "is_course_code", "shape_proposed_tree"]

#: Finder's own copy marker, `Name (2)` or `Name(2)`, and the numbered form
#: `Name 2` that the same downloads leave behind.
_PAREN_COPY = re.compile(r"\s*\(\d+\)\s*$")
_NUMBERED_COPY = re.compile(r"\s+\d+\s*$")
#: CourseWorks appends `_export` or `__export` (and the spaced or hyphenated
#: form) to the folder it created. The id of the node stays what the plan minted.
_EXPORT = re.compile(r"(?:__export|_export|[\s-]+export)\s*$", re.IGNORECASE)

_ACADEMIC = "Academic"
_ACADEMIC_NAMES = frozenset({"academic", "academics"})
_KEPT_WHEN_EMPTY = frozenset({ARCHIVE, REVIEW_AND_UNSORTED})
#: Dump names a download leaves at the top of the folder. A real branch can be
#: empty in the outline's count and still be a branch; these are not.
_NOISE_STEMS = frozenset({"files", "starter"})
_SUBJECT = "subject"
_TERM = "term"
_WORK_TYPE = "work_type"
#: A course code is letters then a number (`COMS4701`, `CHEN 2100`). A term
#: like `2025-Spring` is not one: it starts with a digit.
_COURSE_CODE = re.compile(r"[a-z]{2,12}\d{3,4}[a-z0-9]*")


def course_key(text: str) -> str:
    """One spelling for a course. `CHEN 2100` and `CHEN2100` are the same key.

    Copy markers `(2)` and `_export` are noise. A trailing course number is
    not: `COMS 4701` must not be stripped down to `COMS`.
    """
    cleaned = _strip(text or "", numbered_copy=False)
    return re.sub(r"[^a-z0-9]", "", cleaned.casefold())


def is_course_code(text: str) -> bool:
    """Whether this label is a course code, not a term or a dump name."""
    key = course_key(text)
    return _COURSE_CODE.fullmatch(key) is not None


def shape_proposed_tree(nodes: Sequence[Node], *,
                        holds: Mapping[str, Sequence[str]] | None = None,
                        on_disk: Mapping[str, Sequence[str]] | None = None,
                        declared_courses: Sequence[str] = (),
                        ) -> tuple[Node, ...]:
    """The proposed folders, with obvious duplicates no longer top-level peers.

    `holds` is node id to the files the plan seated on that node. That count
    is placements. It is not emptiness.

    `on_disk` is node id to the files sitting in that directory. When it is
    passed, an existing directory is empty only when that map gives it and
    its children nothing. Zero placements do not park it and do not drop it.
    `None` means the caller did not measure the disk; disposal then follows
    `holds`, which is what the tests written before that measurement do.

    `declared_courses` are the person's own course strings. A leaf that
    matches one is not disposable empty noise. Spacing does not make a
    second course.
    """
    files_of = {node_id: tuple(file_ids)
                for node_id, file_ids in (holds or {}).items()}
    disk_of = None if on_disk is None else {
        node_id: tuple(file_ids) for node_id, file_ids in on_disk.items()}
    declared = tuple(declared_courses)
    by_id = {node.node_id: node for node in nodes}
    # Empty copy and export folders, remembered before their labels are cleaned.
    noise: set[str] = set()
    _collapse_finder_copies(by_id, files_of, noise, disk_of, declared)
    _collapse_same_course_labels(by_id, files_of, noise, disk_of, declared)
    _group_courses(by_id, files_of, declared)
    _collapse_finder_copies(by_id, files_of, noise, disk_of, declared)
    _remember_export_and_copy_labels(by_id, noise)
    _strip_export_noise(by_id)
    _park_empty_noise(by_id, files_of, noise, disk_of, declared)
    return tuple(by_id.values())


def _collapse_finder_copies(by_id: dict[str, Node],
                            files_of: Mapping[str, Sequence[str]],
                            noise: set[str],
                            disk_of: Mapping[str, Sequence[str]] | None,
                            declared: Sequence[str]) -> None:
    """One node per stem among siblings, unless their subjects disagree.

    The richest sibling keeps the id. Empty copies are dropped. A copy that
    still holds files is nested under the survivor so it is not a peer, and
    its files stay on the id the plan already has.
    """
    depths = {node_id: _depth(node_id, by_id) for node_id in list(by_id)}
    parents = sorted({node.parent_node_id for node in by_id.values()},
                     key=lambda parent: depths.get(parent or "", 0),
                     reverse=True)
    for parent_id in parents:
        siblings = [node for node in by_id.values()
                    if node.parent_node_id == parent_id
                    and node.node_type != PROTECTED]
        grouped: dict[str, list[Node]] = {}
        for node in siblings:
            grouped.setdefault(_stem_key(node.display_label), []).append(node)
        for group in grouped.values():
            if len(group) < 2:
                continue
            if len({_field(node, _SUBJECT) for node in group}) != 1:
                continue
            _collapse_group(by_id, files_of, group, noise, disk_of, declared)


def _collapse_same_course_labels(by_id: dict[str, Node],
                                 files_of: Mapping[str, Sequence[str]],
                                 noise: set[str],
                                 disk_of: Mapping[str, Sequence[str]] | None,
                                 declared: Sequence[str]) -> None:
    """Siblings whose labels are the same course code are one folder.

    `CHEN 2100` and `CHEN2100` do not share a stem, so the Finder-copy pass
    leaves them as peers. The course key does not.
    """
    depths = {node_id: _depth(node_id, by_id) for node_id in list(by_id)}
    parents = sorted({node.parent_node_id for node in by_id.values()},
                     key=lambda parent: depths.get(parent or "", 0),
                     reverse=True)
    for parent_id in parents:
        siblings = [node for node in by_id.values()
                    if node.parent_node_id == parent_id
                    and node.node_type != PROTECTED]
        grouped: dict[str, list[Node]] = {}
        for node in siblings:
            key = course_key(node.display_label)
            if not is_course_code(node.display_label):
                continue
            grouped.setdefault(key, []).append(node)
        for group in grouped.values():
            if len(group) < 2:
                continue
            subjects = {course_key(_field(node, _SUBJECT) or "") for node in group}
            subjects.discard("")
            if len(subjects) > 1:
                continue
            _collapse_group(by_id, files_of, group, noise, disk_of, declared)


def _collapse_group(by_id: dict[str, Node],
                    files_of: Mapping[str, Sequence[str]],
                    group: Sequence[Node], noise: set[str],
                    disk_of: Mapping[str, Sequence[str]] | None,
                    declared: Sequence[str]) -> None:
    present = [by_id[node.node_id] for node in group if node.node_id in by_id]
    if len(present) < 2:
        return
    winner = max(present, key=lambda node: (
        _richness(node, by_id, files_of), node.node_id))
    label = _display_for(present, by_id, files_of)
    by_id[winner.node_id] = _relabel(winner, label)
    if _disposable(winner.node_id, by_id, files_of, disk_of, declared):
        noise.add(winner.node_id)
    for loser in present:
        if loser.node_id == winner.node_id or loser.node_id not in by_id:
            continue
        loser = by_id[loser.node_id]
        if _disposable(loser.node_id, by_id, files_of, disk_of, declared) and (
                loser.display_label not in _KEPT_WHEN_EMPTY):
            for child in _children(loser.node_id, by_id):
                by_id[child.node_id] = _reparent(child, winner.node_id)
            del by_id[loser.node_id]
            continue
        by_id[loser.node_id] = _reparent(
            _relabel(loser, _strip(loser.display_label, numbered_copy=True)),
            winner.node_id)


def _group_courses(by_id: dict[str, Node],
                   files_of: Mapping[str, Sequence[str]],
                   declared: Sequence[str] = ()) -> None:
    """Subject, then term, then kind of work, when the files agree.

    Two peers that share a subject become one course. The same export stem
    with two subjects stays two courses, named by the course code, under
    Academic. A folder with no subject is left where it is.
    """
    top = [node for node in by_id.values()
           if node.parent_node_id is None and node.node_type != PROTECTED
           and node.display_label not in _KEPT_WHEN_EMPTY
           and node.display_label.casefold() not in _ACADEMIC_NAMES]
    by_stem: dict[str, list[Node]] = {}
    by_subject: dict[str, list[Node]] = {}
    for node in top:
        by_stem.setdefault(_stem_key(node.display_label), []).append(node)
        subject = _field(node, _SUBJECT)
        if subject:
            by_subject.setdefault(course_key(subject), []).append(node)

    place: set[str] = set()
    for group in by_stem.values():
        subjects = {_field(node, _SUBJECT) for node in group}
        if len(group) < 2 or len(subjects) < 2:
            continue
        place.update(node.node_id for node in group if _field(node, _SUBJECT))
    for key, group in by_subject.items():
        if len(group) >= 2 or _another_course_home(
                by_id, key, {node.node_id for node in group}):
            place.update(node.node_id for node in group)
    if not place:
        return

    members = [by_id[node_id] for node_id in place if node_id in by_id]
    academic = _academic_parent(by_id, donor=members[0])
    subject_count = {subject: len(group) for subject, group in by_subject.items()}
    for node in members:
        _place_in_course(by_id, node, academic=academic,
                         subject_count=subject_count, declared=declared)


def _place_in_course(by_id: dict[str, Node], node: Node, *,
                     academic: Node, subject_count: Mapping[str, int],
                     declared: Sequence[str] = ()) -> None:
    subject = _field(node, _SUBJECT)
    if not subject or node.node_id not in by_id:
        return
    node = by_id[node.node_id]
    term = _field(node, _TERM)
    work = _field(node, _WORK_TYPE)
    key = course_key(subject)
    label = _course_label(subject, declared, by_id, academic)
    sole = subject_count.get(key, 0) == 1
    # This folder's own name is the course. It is the home, not a child of a
    # second copy of the same name.
    if (is_course_code(node.display_label) and course_key(node.display_label) == key
            and not work and not term):
        by_id[node.node_id] = _retitle(
            node, label=label, parent=academic.node_id, dimension=_SUBJECT)
        return
    if sole and not term and not work:
        by_id[node.node_id] = _retitle(
            node, label=label, parent=academic.node_id, dimension=_SUBJECT)
        return
    course = _ensure_level(
        by_id, parent=academic, label=label, dimension=_SUBJECT,
        expected=((_SUBJECT, subject),), donor=node)
    parent = course
    if term:
        parent = _ensure_level(
            by_id, parent=course, label=term, dimension=_TERM,
            expected=((_SUBJECT, subject), (_TERM, term)), donor=node)
    if work:
        by_id[node.node_id] = _retitle(
            node, label=work, parent=parent.node_id, dimension=_WORK_TYPE)
        return
    by_id[node.node_id] = _reparent(
        _relabel(node, _strip(node.display_label, numbered_copy=True)),
        parent.node_id)


def _remember_export_and_copy_labels(by_id: Mapping[str, Node],
                                    noise: set[str]) -> None:
    for node in by_id.values():
        if _has_copy_suffix(node.display_label) or _has_export_suffix(
                node.display_label):
            noise.add(node.node_id)


def _strip_export_noise(by_id: dict[str, Node]) -> None:
    """Drop `_export` / `__export` and a trailing ` (n)` from what the person sees."""
    for node_id, node in list(by_id.items()):
        cleaned = _strip(node.display_label, numbered_copy=False)
        if cleaned != node.display_label:
            by_id[node_id] = _relabel(node, cleaned)


def _park_empty_noise(by_id: dict[str, Node],
                      files_of: Mapping[str, Sequence[str]],
                      noise: set[str],
                      disk_of: Mapping[str, Sequence[str]] | None = None,
                      declared: Sequence[str] = ()) -> None:
    """Finder copies, export leftovers, and dump names are not top-level peers.

    A branch the plan proposed can count as empty and still be the branch.
    What gets parked is a leaf the scan promoted: a collapsed copy, a
    CourseWorks export, a bare number, or `files` / `starter`. `99 Archive`
    and `98 Review and Unsorted` stay where they are.
    """
    parked = [node for node in by_id.values()
              if _is_empty_noise(node, by_id, files_of, noise, disk_of, declared)]
    if not parked:
        return
    archive = _archive_parent(by_id, donor=parked[0])
    for node in parked:
        if node.node_id == archive.node_id or node.node_id not in by_id:
            continue
        by_id[node.node_id] = _reparent(by_id[node.node_id], archive.node_id)


def _is_empty_noise(node: Node, by_id: Mapping[str, Node],
                    files_of: Mapping[str, Sequence[str]],
                    noise: set[str],
                    disk_of: Mapping[str, Sequence[str]] | None = None,
                    declared: Sequence[str] = ()) -> bool:
    if node.parent_node_id is not None or node.node_type == PROTECTED:
        return False
    if node.display_label in _KEPT_WHEN_EMPTY:
        return False
    if _children(node.node_id, by_id):
        return False
    if not _disposable(node.node_id, by_id, files_of, disk_of, declared):
        return False
    stem = _stem_key(node.display_label)
    return (node.node_id in noise or stem in _NOISE_STEMS or stem.isdigit())


def _disposable(node_id: str, by_id: Mapping[str, Node],
               files_of: Mapping[str, Sequence[str]],
               disk_of: Mapping[str, Sequence[str]] | None,
               declared: Sequence[str]) -> bool:
    """A folder can be parked or dropped only when it is actually empty.

    An existing directory is empty when `disk_of` was measured and the
    directory holds no file. Zero placements are not that measurement.
    A leaf that matches a declared course is not disposable.
    """
    node = by_id.get(node_id)
    if node is None or _matches_declared(node, declared):
        return False
    if disk_of is not None and getattr(node, "existing_path", None):
        return _disk_files(node_id, by_id, disk_of) == 0
    return _subtree_files(node_id, by_id, files_of) == 0


def _matches_declared(node: Node, declared: Sequence[str]) -> bool:
    keys = {course_key(item) for item in declared if item and course_key(item)}
    if not keys:
        return False
    subject = _field(node, _SUBJECT)
    if subject and course_key(subject) in keys:
        return True
    return course_key(node.display_label) in keys


def _disk_files(node_id: str, by_id: Mapping[str, Node],
                disk_of: Mapping[str, Sequence[str]]) -> int:
    seen: set[str] = set()

    def walk(current: str) -> int:
        if current in seen:
            return 0
        seen.add(current)
        total = len(disk_of.get(current, ()))
        for child in _children(current, by_id):
            total += walk(child.node_id)
        return total

    return walk(node_id)


def _another_course_home(by_id: Mapping[str, Node], key: str,
                         group_ids: set[str]) -> bool:
    """Whether this course already has a home outside this top-level group.

    A child of a group member is the same home, not a second one. That is
    what kept a course folder from being pulled under Academic just because
    a notes folder beneath it carries the same subject.
    """
    if not key:
        return False
    for node in by_id.values():
        if node.node_id in group_ids:
            continue
        if any(_is_ancestor(by_id, member, node.node_id) for member in group_ids):
            continue
        if _node_course_key(node) == key:
            return True
    return False


def _node_course_key(node: Node) -> str:
    subject = _field(node, _SUBJECT)
    if subject and course_key(subject):
        return course_key(subject)
    if is_course_code(node.display_label):
        return course_key(node.display_label)
    return ""


def _course_label(subject: str, declared: Sequence[str],
                  by_id: Mapping[str, Node], academic: Node) -> str:
    key = course_key(subject)
    for course in declared:
        if course and course_key(course) == key:
            return course.strip()
    for node in by_id.values():
        if (node.parent_node_id == academic.node_id
                and is_course_code(node.display_label)
                and course_key(node.display_label) == key):
            return node.display_label
    for node in by_id.values():
        if is_course_code(node.display_label) and course_key(node.display_label) == key:
            return node.display_label
    return subject


def _is_ancestor(by_id: Mapping[str, Node], ancestor_id: str, node_id: str) -> bool:
    seen: set[str] = set()
    current: str | None = node_id
    while current and current not in seen:
        if current == ancestor_id:
            return True
        seen.add(current)
        node = by_id.get(current)
        current = node.parent_node_id if node is not None else None
    return False


def _academic_parent(by_id: dict[str, Node], *, donor: Node) -> Node:
    for node in by_id.values():
        if (node.parent_node_id is None
                and node.display_label.casefold() in _ACADEMIC_NAMES):
            return node
    return _mint(by_id, donor=donor, node_id=f"shaped:academic:{donor.plan_version_id}",
                 label=_ACADEMIC, parent=None, dimension=None, expected=(),
                 explanation=("Courses named by their subject. Folders that "
                              "agreed on a subject sit under it."))


def _archive_parent(by_id: dict[str, Node], *, donor: Node) -> Node:
    for node in by_id.values():
        if node.parent_node_id is None and node.display_label == ARCHIVE:
            return node
    return _mint(by_id, donor=donor, node_id=f"shaped:archive:{donor.plan_version_id}",
                 label=ARCHIVE, parent=None, dimension=None, expected=(),
                 explanation=("Empty folders with nothing in them. They are "
                              "kept here so they are not peers of a folder "
                              "that holds files."))


def _ensure_level(by_id: dict[str, Node], *, parent: Node, label: str,
                  dimension: str, expected: Sequence[tuple[str, str]],
                  donor: Node) -> Node:
    wanted = course_key(label) if dimension == _SUBJECT else ""
    for node in by_id.values():
        if node.parent_node_id != parent.node_id:
            continue
        if node.display_label == label and node.dimension == dimension:
            return node
        if (wanted and is_course_code(node.display_label)
                and course_key(node.display_label) == wanted):
            return node
    if wanted:
        for node in list(by_id.values()):
            if node.node_id == parent.node_id:
                continue
            if not is_course_code(node.display_label):
                continue
            if course_key(node.display_label) != wanted:
                continue
            if _is_ancestor(by_id, node.node_id, parent.node_id):
                continue
            moved = node if node.parent_node_id == parent.node_id else _reparent(
                node, parent.node_id)
            by_id[node.node_id] = moved
            return by_id[node.node_id]
    node_id = f"shaped:{parent.node_id}:{dimension}:{label}"
    return _mint(by_id, donor=donor, node_id=node_id, label=label,
                 parent=parent.node_id, dimension=dimension, expected=expected,
                 explanation=(f"Every file grouped here names {dimension} "
                              f"{label}."))


def _mint(by_id: dict[str, Node], *, donor: Node, node_id: str, label: str,
          parent: str | None, dimension: str | None,
          expected: Sequence[tuple[str, str]], explanation: str) -> Node:
    node = Node(
        node_id=node_id, plan_version_id=donor.plan_version_id,
        node_type=PROPOSED, display_label=label, parent_node_id=parent,
        root_anchor=donor.root_anchor, ordinal=0, associated_group_ids=(),
        explanation=explanation, node_role=donor.node_role,
        accepts_placement=True, handling_class=donor.handling_class,
        origin_node_id=node_id, dimension_role=dimension, dimension=dimension,
        expected_values=tuple(ExpectedValue(field, value)
                              for field, value in expected))
    by_id[node.node_id] = node
    return node


def _display_for(group: Sequence[Node], by_id: Mapping[str, Node],
                 files_of: Mapping[str, Sequence[str]]) -> str:
    """The spelling without a copy marker, when one of the siblings has it."""
    clean = [node for node in group
             if not _has_copy_suffix(node.display_label)
             and not _has_export_suffix(node.display_label)]
    if clean:
        return max(clean, key=lambda node: (
            _richness(node, by_id, files_of), node.node_id)).display_label
    winner = max(group, key=lambda node: (
        _richness(node, by_id, files_of), node.node_id))
    return _strip(winner.display_label, numbered_copy=True)


def _richness(node: Node, by_id: Mapping[str, Node],
              files_of: Mapping[str, Sequence[str]]) -> tuple:
    return (
        _subtree_files(node.node_id, by_id, files_of),
        _descendant_count(node.node_id, by_id),
        1 if node.display_label in _KEPT_WHEN_EMPTY else 0,
        0 if _has_copy_suffix(node.display_label) else 1,
        0 if _has_export_suffix(node.display_label) else 1,
    )


def _relabel(node: Node, label: str) -> Node:
    if not label or label == node.display_label:
        return node
    return _replace(node, display_label=label)


def _reparent(node: Node, parent: str | None) -> Node:
    if parent == node.parent_node_id:
        return node
    return _replace(node, parent_node_id=parent)


def _retitle(node: Node, *, label: str, parent: str | None,
             dimension: str) -> Node:
    return _replace(node, display_label=label, parent_node_id=parent,
                    dimension=dimension, dimension_role=dimension)


def _replace(node: Node, **changes) -> Node:
    return replace(node, **changes)


def _field(node: Node, name: str) -> str | None:
    for item in node.expected_values:
        if item.field == name and item.value:
            return item.value
    return None


def _stem_key(label: str) -> str:
    cleaned = _strip(label, numbered_copy=True)
    cleaned = cleaned.replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip().casefold()
    return cleaned or label.casefold()


def _strip(label: str, *, numbered_copy: bool) -> str:
    current = label.strip()
    previous = None
    while current and current != previous:
        previous = current
        updated = _PAREN_COPY.sub("", current).strip()
        updated = _EXPORT.sub("", updated).strip()
        if numbered_copy:
            updated = _NUMBERED_COPY.sub("", updated).strip()
        current = updated
    return current or label


def _has_copy_suffix(label: str) -> bool:
    return _PAREN_COPY.search(label) is not None or _NUMBERED_COPY.search(label) is not None


def _has_export_suffix(label: str) -> bool:
    without_copy = _PAREN_COPY.sub("", label).strip()
    without_copy = _NUMBERED_COPY.sub("", without_copy).strip()
    return _EXPORT.search(without_copy) is not None


def _children(node_id: str, by_id: Mapping[str, Node]) -> tuple[Node, ...]:
    return tuple(node for node in by_id.values()
                 if node.parent_node_id == node_id)


def _depth(node_id: str | None, by_id: Mapping[str, Node]) -> int:
    depth = 0
    seen: set[str] = set()
    current = node_id
    while current and current not in seen:
        seen.add(current)
        node = by_id.get(current)
        current = node.parent_node_id if node is not None else None
        depth += 1
    return depth


def _subtree_files(node_id: str, by_id: Mapping[str, Node],
                   files_of: Mapping[str, Sequence[str]]) -> int:
    seen: set[str] = set()

    def walk(current: str) -> int:
        if current in seen:
            return 0
        seen.add(current)
        total = len(files_of.get(current, ()))
        for child in _children(current, by_id):
            total += walk(child.node_id)
        return total

    return walk(node_id)


def _descendant_count(node_id: str, by_id: Mapping[str, Node]) -> int:
    total = 0
    for child in _children(node_id, by_id):
        total += 1 + _descendant_count(child.node_id, by_id)
    return total

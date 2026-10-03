"""Seat understanding answers before the outline is written.

The rules may have placed nothing. A cached or just-returned answer still
names a life area, a course, a term, and a confidence. Those fields are a
placement input: a confident course that matches a folder is seated there,
and a file that abstained or still needs review is counted on review.
This is not a second scan and not a residuals pass.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from structure_shape import course_key, is_course_code
from tree_design.records import Node

__all__ = ["Seating", "seat_unplaced", "understandings_from_report"]

_PLACE = "place"


@dataclass(frozen=True)
class Seating:
    """Holds the outline counts, plus files that still need review.

    `holds` includes the rules' placements and any file understanding
    seated on a folder. `review_ids` are abstentions and needs-review
    answers that are not in `holds`. They are counted on the plan's own
    review folder. A folder the plan did not propose is not minted:
    an extra row would move the markers the person edits.
    """

    holds: dict[str, list[str]]
    review_ids: tuple[str, ...]
    extra_nodes: tuple[Node, ...]


def understandings_from_report(report) -> dict[str, object]:
    """file id to the answer the pass stored, including a cache hit."""
    found: dict[str, object] = {}
    for result in getattr(report, "results", ()) or ():
        understood = getattr(result, "understanding", None)
        file_id = getattr(result, "file_id", None)
        if understood is not None and file_id:
            found[str(file_id)] = understood
    return found


def seat_unplaced(nodes: Sequence[Node], *,
                  placement_holds: Mapping[str, Sequence[str]],
                  decisions: Sequence[object] = (),
                  understandings: Mapping[str, object] | None = None,
                  declared_courses: Sequence[str] = (),
                  ) -> Seating:
    """Place files the rules left unplaced, using understanding answers.

    A file the rules already placed stays where it was. A confident answer
    whose course matches a folder is seated on that folder. Needs-review,
    a low-confidence answer, and an abstention with no matching folder are
    held for review. The count of files in the result is therefore able to
    exceed the pre-understand placement count.
    """
    holds = {node_id: list(file_ids) for node_id, file_ids in placement_holds.items()}
    placed = {file_id for file_ids in holds.values() for file_id in file_ids}
    review: list[str] = []
    answers = understandings or {}
    node_list = list(nodes)

    def add(node_id: str, file_id: str) -> None:
        bucket = holds.setdefault(node_id, [])
        if file_id not in bucket:
            bucket.append(file_id)
        placed.add(file_id)

    for file_id, answer in answers.items():
        if file_id in placed:
            continue
        if answer is None or getattr(answer, "needs_review", True):
            review.append(file_id)
            continue
        home = _home_for(node_list, answer, declared_courses)
        if home is None:
            review.append(file_id)
            continue
        add(home, file_id)

    for decision in decisions:
        if getattr(decision, "outcome", None) == _PLACE and getattr(
                decision, "destination", None) is not None:
            continue
        for file_id in _file_ids(decision):
            if file_id not in placed and file_id not in review:
                review.append(file_id)

    return Seating(holds=holds, review_ids=tuple(review), extra_nodes=())


def _home_for(nodes: Sequence[Node], answer, declared: Sequence[str]) -> str | None:
    course = getattr(answer, "course", None)
    if isinstance(course, str) and course.strip():
        key = course_key(course)
        matches = [node for node in nodes if _matches_course(node, key)]
        if not matches:
            declared_key = {course_key(item) for item in declared}
            if key in declared_key:
                matches = [node for node in nodes if _matches_course(node, key)]
        if matches:
            matches.sort(key=lambda node: (
                0 if course_key(node.display_label) == key else 1,
                0 if node.parent_node_id is None else 1,
                node.node_id,
            ))
            return matches[0].node_id
    area = getattr(answer, "life_area", None)
    if isinstance(area, str) and area.strip() and area.casefold() != "needs_review":
        for node in nodes:
            if node.display_label.casefold() == area.casefold():
                return node.node_id
    return None


def _matches_course(node: Node, key: str) -> bool:
    if not key:
        return False
    if is_course_code(node.display_label) and course_key(node.display_label) == key:
        return True
    for item in node.expected_values:
        if item.field == "subject" and course_key(item.value) == key:
            return True
    return False


def _file_ids(decision) -> tuple[str, ...]:
    subject = getattr(decision, "subject", None)
    if subject is None:
        return ()
    file_id = getattr(subject, "file_id", None)
    if file_id:
        return (file_id,)
    return tuple(getattr(subject, "member_file_ids", ()) or ())



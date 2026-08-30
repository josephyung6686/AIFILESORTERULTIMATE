"""`66` §3's six states. Six DISTINCT things, never one flat list of paths.

    "These must not be collapsed into one ambiguous list of paths."
    "It should not describe a valid multi-purpose relationship as a confidence
    failure."

`67` §2 calls this model new and load-bearing, and names the case it exists for:
a research paper that is also school homework is TWO ACCEPTED RELATIONSHIPS AND
ONE PHYSICAL LOCATION. A product that renders that as "we are not sure where this
goes" has told the user their correct filing is a defect.

`as_flat_paths` exists and raises. A method that raises is a better answer than
no method: the collapse is the failure `66` §3 names, so the code says its name
out loud at the one place someone would reach for it.

`current_location` and `historical_location` carry an OPAQUE string the caller
supplies. P13 composes none of it. `66` §3's table says a current location is
"the actual path where the file exists now" and B3 says P13 renders no resolved
path; both cannot be literally true for a file that lives outside the destination
tree, which is every file before it is filed. The reconciliation is the owner's
-- either B3 narrows to "P13 COMPOSES no path", or `66` §3's first row narrows to
a node reference. It is not decided here.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from review_surface.labels import refuse_path_separator
from review_surface.vocabulary import check

CURRENT_LOCATION: str = "current_location"
FILED_HOME: str = "filed_home"
ALSO_RELATED_TO: str = "also_related_to"
SHARED_MATERIAL: str = "shared_material"
HISTORICAL_LOCATION: str = "historical_location"
POSSIBLE_PLACEMENT: str = "possible_placement"

#: In `66` §3's own table order, which is the order a result reads in.
LOCATION_STATES: tuple[str, ...] = (
    CURRENT_LOCATION, FILED_HOME, ALSO_RELATED_TO, SHARED_MATERIAL,
    HISTORICAL_LOCATION, POSSIBLE_PLACEMENT,
)


class LocationStatesCollapsed(RuntimeError):
    """Something asked for the six states as one list. `66` §3 forbids it."""


@dataclass(frozen=True)
class LocationElement:
    """One of the six, and it knows which one it is."""

    state: str
    label_chain: tuple[str, ...]
    node_id: str | None
    relationship_ref: str | None
    shared_policy: str | None
    opaque_current_location: str | None
    explanation: str

    def __post_init__(self) -> None:
        check(self.state, LOCATION_STATES, name="location state")
        if self.state == ALSO_RELATED_TO and not self.relationship_ref:
            raise ValueError(
                "an also-related-to element must name the accepted group, "
                "project, course, packet or event it relates to; `66` §3 calls "
                "it a relationship and an unnamed one is indistinguishable "
                "from uncertainty")
        if self.state == SHARED_MATERIAL and not self.shared_policy:
            raise ValueError(
                "`66` §3: a shared-material relationship is shown WITH the "
                "relevant shared policy; without it the user cannot tell an "
                "approved sharing arrangement from an unresolved second home")
        refuse_path_separator(self.label_chain, node_id=self.node_id or "")


@dataclass(frozen=True)
class SixStateView:
    subject_ref: str
    plan_version: str
    elements: tuple[LocationElement, ...]

    def by_state(self, state: str) -> tuple[LocationElement, ...]:
        check(state, LOCATION_STATES, name="location state")
        return tuple(e for e in self.elements if e.state == state)

    def as_flat_paths(self) -> None:
        raise LocationStatesCollapsed(
            "`66` §3: the six states must not be collapsed into one ambiguous "
            "list of paths. Ask `by_state(...)` for the one you mean -- a "
            "current location, a filed home, an accepted relationship, a "
            "shared-material arrangement, a historical path and an unaccepted "
            "candidate are six different claims and only one of them is where "
            "the file is")


def six_state_view(*, subject_ref: str, plan_version: str,
                   current: LocationElement | None,
                   filed_home: LocationElement | None,
                   also_related_to: Sequence[LocationElement],
                   shared_material: Sequence[LocationElement],
                   historical: Sequence[LocationElement],
                   possible: Sequence[LocationElement]) -> SixStateView:
    """Assemble the six, each in its own slot. A missing slot is empty, not absent.

    Every state is a separate keyword, so a caller cannot pass a mixed list and
    have P13 sort it out -- sorting it out is exactly the guess `66` §3 removes.
    """
    for element, expected in ((current, CURRENT_LOCATION),
                              (filed_home, FILED_HOME)):
        if element is not None and element.state != expected:
            raise ValueError(
                f"an element in the {expected} slot carries state "
                f"{element.state!r}")
    for group, expected in ((also_related_to, ALSO_RELATED_TO),
                            (shared_material, SHARED_MATERIAL),
                            (historical, HISTORICAL_LOCATION),
                            (possible, POSSIBLE_PLACEMENT)):
        for element in group:
            if element.state != expected:
                raise ValueError(
                    f"an element in the {expected} slot carries state "
                    f"{element.state!r}")
    ordered: list[LocationElement] = []
    if current is not None:
        ordered.append(current)
    if filed_home is not None:
        ordered.append(filed_home)
    ordered.extend(also_related_to)
    ordered.extend(shared_material)
    ordered.extend(historical)
    ordered.extend(possible)
    return SixStateView(subject_ref=subject_ref, plan_version=plan_version,
                        elements=tuple(ordered))

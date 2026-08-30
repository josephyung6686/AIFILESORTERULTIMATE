"""`66` §3: six DISTINCT states, never one flat list, never a confidence failure.

    "These must not be collapsed into one ambiguous list of paths."
    "It should not describe a valid multi-purpose relationship as a confidence
    failure."

`67` §2 names the case: a research paper that is also school homework is TWO
ACCEPTED RELATIONSHIPS AND ONE PHYSICAL LOCATION. A product that renders that as
"we are not sure where this goes" has told the user their correct filing is a
defect.
"""
from __future__ import annotations

import pytest

from review_surface.locations import (
    ALSO_RELATED_TO,
    CURRENT_LOCATION,
    FILED_HOME,
    HISTORICAL_LOCATION,
    LOCATION_STATES,
    POSSIBLE_PLACEMENT,
    SHARED_MATERIAL,
    LocationElement,
    LocationStatesCollapsed,
    six_state_view,
)


def _element(state, chain=(), **kw):
    values = dict(state=state, label_chain=chain, node_id=None,
                  relationship_ref=None, shared_policy=None,
                  opaque_current_location=None, explanation="fixture")
    values.update(kw)
    return LocationElement(**values)


def test_the_six_states_are_66_section_3_s_six_in_its_own_order():
    assert LOCATION_STATES == (
        "current_location", "filed_home", "also_related_to",
        "shared_material", "historical_location", "possible_placement")


def test_every_state_publishes_a_named_constant():
    """The brief's §11 applies to this vocabulary too."""
    import review_surface.locations as module

    named = {value for name, value in vars(module).items()
             if name.isupper() and isinstance(value, str)}
    for member in LOCATION_STATES:
        assert member in named


def test_the_paper_that_is_also_homework_is_two_relationships_and_one_location():
    """`67` §2: "that is two accepted relationships and one physical location,
    not a confidence failure"."""
    view = six_state_view(
        subject_ref="f-paper", plan_version="plan-1",
        current=_element(CURRENT_LOCATION,
                         opaque_current_location="Documents > Research > paper.pdf"),
        filed_home=_element(FILED_HOME, ("Research", "Fluids"), node_id="n-7"),
        also_related_to=(
            _element(ALSO_RELATED_TO, relationship_ref="g-phys1401"),
            _element(ALSO_RELATED_TO, relationship_ref="g-lab-notebook"),
        ),
        shared_material=(), historical=(), possible=())
    assert len(view.by_state(CURRENT_LOCATION)) == 1
    assert len(view.by_state(ALSO_RELATED_TO)) == 2
    assert view.by_state(POSSIBLE_PLACEMENT) == ()


def test_every_state_is_reachable_separately_and_none_is_merged():
    view = six_state_view(
        subject_ref="f-1", plan_version="plan-1",
        current=_element(CURRENT_LOCATION, opaque_current_location="X"),
        filed_home=_element(FILED_HOME, ("A",), node_id="n-1"),
        also_related_to=(_element(ALSO_RELATED_TO, relationship_ref="g-1"),),
        shared_material=(_element(SHARED_MATERIAL, ("Shared",),
                                  node_id="n-2", shared_policy="shared-branch"),),
        historical=(_element(HISTORICAL_LOCATION,
                             opaque_current_location="old"),),
        possible=(_element(POSSIBLE_PLACEMENT, ("B",), node_id="n-3"),))
    for state in LOCATION_STATES:
        assert view.by_state(state), f"{state} must be separately reachable"
    assert len(view.elements) == len(LOCATION_STATES)


def test_there_is_no_way_to_ask_for_one_flat_list_of_paths():
    """`66` §3: "These must not be collapsed into one ambiguous list of paths".

    The method exists AND raises. A method that raises is a better answer than
    no method: the collapse is the failure `66` §3 names, so the code says its
    name out loud at the one place someone would reach for it.
    """
    view = six_state_view(
        subject_ref="f-1", plan_version="plan-1",
        current=_element(CURRENT_LOCATION, opaque_current_location="X"),
        filed_home=None, also_related_to=(), shared_material=(),
        historical=(), possible=())
    with pytest.raises(LocationStatesCollapsed):
        view.as_flat_paths()


def test_a_possible_placement_is_never_offered_as_a_home():
    """`66` §3: "Available only in review or evidence details; never presented
    as a home"."""
    element = _element(POSSIBLE_PLACEMENT, ("B",), node_id="n-3")
    assert element.state != FILED_HOME
    assert element.state != CURRENT_LOCATION


def test_a_shared_material_element_must_name_its_policy():
    """`66` §3: "Shown with the relevant shared policy and relationship labels"."""
    with pytest.raises(ValueError):
        _element(SHARED_MATERIAL, ("Shared",), node_id="n-2",
                 shared_policy=None)


def test_an_also_related_to_element_must_name_the_relationship():
    """An unnamed relationship is indistinguishable from uncertainty, which is
    the reading `66` §3 forbids."""
    with pytest.raises(ValueError):
        _element(ALSO_RELATED_TO, relationship_ref=None)


def test_an_unknown_state_is_refused():
    from review_surface.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        _element("maybe_home")


def test_an_element_in_the_wrong_slot_is_refused():
    """A caller cannot pass a mixed list and have P13 sort it out; sorting it
    out is exactly the guess `66` §3 removes."""
    with pytest.raises(ValueError):
        six_state_view(
            subject_ref="f-1", plan_version="plan-1",
            current=_element(FILED_HOME, ("A",), node_id="n-1"),
            filed_home=None, also_related_to=(), shared_material=(),
            historical=(), possible=())
    with pytest.raises(ValueError):
        six_state_view(
            subject_ref="f-1", plan_version="plan-1", current=None,
            filed_home=None,
            also_related_to=(_element(POSSIBLE_PLACEMENT, ("B",),
                                      node_id="n-3"),),
            shared_material=(), historical=(), possible=())


def test_no_element_carries_a_composed_path():
    """B3. The one opaque string is supplied by the caller and P13 composes none
    of it; the label chain never contains a separator."""
    from review_surface.labels import LabelIsAPath

    element = _element(FILED_HOME, ("Academics", "Columbia"), node_id="n-2")
    for label in element.label_chain:
        assert "/" not in label and "\\" not in label
    with pytest.raises(LabelIsAPath):
        _element(FILED_HOME, ("Academics/Columbia",), node_id="n-2")


def test_an_absent_state_is_empty_rather_than_missing():
    """`67` §1's shape, applied to location: never silently omitted. A state
    with nothing in it answers "nothing here" rather than leaving silence."""
    view = six_state_view(
        subject_ref="f-1", plan_version="plan-1", current=None,
        filed_home=None, also_related_to=(), shared_material=(),
        historical=(), possible=())
    for state in LOCATION_STATES:
        assert view.by_state(state) == ()

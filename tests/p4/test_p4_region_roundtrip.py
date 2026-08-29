# tests/p4/test_p4_region_roundtrip.py
"""§2.7's bounding box, from the engine to `Region` and back.

P4's `Region` is `(x, y, w, h, unit)` and `REGION_UNITS` is `("px", "norm")`. Nothing
enforced that at the point a region is BUILT: `shape.location()` did a bare
`dict(region)`, so a wrong shape was accepted silently and only failed much later
inside `location_from_mapping` — as a bare `KeyError('w')`, the one part of a
location with no honest error message.

The cost was not hypothetical. The OCR extractor once emitted `width`/`height`, and
`tests/p5/p4_stub.py` still carries a comment saying it drops `region` for exactly
that reason. So the one field §8.4 redacts against was never round-tripped by any
test.
"""
import pytest

from evidence_shape.location import MalformedLocation, Region, region_from_mapping
from evidence_shape.vocabulary import REGION_UNITS

GOOD = {"x": 0.1, "y": 0.2, "w": 0.5, "h": 0.25, "unit": "norm"}


def test_a_well_formed_region_becomes_a_region():
    region = region_from_mapping(GOOD)
    assert isinstance(region, Region)
    assert (region.x, region.y, region.w, region.h, region.unit) == (
        0.1, 0.2, 0.5, 0.25, "norm")


def test_the_librarys_own_key_names_are_refused_with_a_readable_error():
    """`width`/`height` is what a real imaging library hands you, and it is the
    mistake this guard exists for. It must name the problem, not raise KeyError."""
    wrong = {"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.25, "unit": "norm"}
    with pytest.raises(MalformedLocation) as caught:
        region_from_mapping(wrong)
    message = str(caught.value)
    assert "w" in message and "h" in message


def test_an_unknown_region_field_is_refused_rather_than_silently_dropped():
    """A key P4 does not read would be stored by `location()` and then dropped by
    `location_from_mapping`, which reads exactly five — a value computed and
    discarded. Refusing it is what stops an adapter inventing a sixth field."""
    with pytest.raises(MalformedLocation):
        region_from_mapping({**GOOD, "origin": "bottom_left"})


def test_a_unit_outside_p4s_two_is_refused_as_a_vocabulary_violation():
    """`NotInVocabulary`, not `MalformedLocation`, and the difference is deliberate.

    A wrong SHAPE is malformed. A unit outside the closed set is a request to add a
    vocabulary member, which P4's own message calls "a P4 contract revision and a
    shape-version bump, not a local decision inside an extractor". Collapsing the two
    would lose exactly that distinction, so the test asserts the specific one.

    `normalized_bottom_left` is the value my Vision adapter first tried to emit, which
    is why it is the example here.
    """
    from evidence_shape.vocabulary import NotInVocabulary

    with pytest.raises(NotInVocabulary):
        region_from_mapping({**GOOD, "unit": "normalized_bottom_left"})
    assert set(REGION_UNITS) == {"px", "norm"}


def test_a_non_numeric_coordinate_is_refused():
    with pytest.raises(MalformedLocation):
        region_from_mapping({**GOOD, "x": "0.1"})


def test_the_emitter_refuses_a_bad_region_rather_than_the_writer(tmp_path):
    """P5 builds locations through `extractors.shape.location`. The rule is P4's and
    is invoked there, so a wrong shape fails where it is MADE — not three layers
    later during a database write, with every extraction already done."""
    from extractors.shape import location

    good = location(zone="ocr", region=dict(GOOD))
    assert good["region"] == GOOD

    with pytest.raises(MalformedLocation):
        location(zone="ocr", region={"x": 0.1, "y": 0.2, "width": 0.5,
                                     "height": 0.25, "unit": "norm"})


def test_a_region_survives_the_whole_path_to_a_parsed_location():
    """The round trip that had no test: built by P5, serialized into a location
    mapping, and parsed back by P4 into a `Region` with the same numbers."""
    from evidence_shape.locator import location_from_mapping
    from extractors.shape import location

    built = location(zone="ocr", region=dict(GOOD))
    parsed = location_from_mapping(built)
    assert parsed.region == Region(0.1, 0.2, 0.5, 0.25, "norm")

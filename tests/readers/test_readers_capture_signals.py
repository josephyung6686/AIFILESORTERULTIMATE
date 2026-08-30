# tests/readers/test_readers_capture_signals.py
"""§2.6's three injected catalogues, as the deployment actually compiles them.

`planning/deferred-catalogues/01`..`04` were complete on disk and read by nothing:
`grep -rn "deferred-catalogues" src` returned nothing, `read_image` was `_no_reader`,
and every image in a corpus came back `image.metadata: unsupported`. So a macOS
screenshot was not recognised as a screenshot on any path, under any situation --
including the one literally named `photos.screenshot-captures`.

These are the guards on the lift. They assert the two properties the catalogues
themselves say are load-bearing:

* **A convention never claims a file its content contradicts, and a folder's name
  decides nothing.** The matcher is given a FILENAME. The directory it sits under is
  not one of the file's own words, and the observation it produces carries
  `reliability: possible` and NO `signal_tier` -- so §3.7 weighs it below every
  camera-EXIF fact and it cannot outvote what the image actually says.
* **`design` provenance is a claim about the design, and it is checked.** Two of the
  115 producer strings are named by §2.2 in as many words; the other 113 are the
  catalogue's proposals. A row that claims the first while being the second is a
  load error, not a comment nobody reads.
"""
from __future__ import annotations

import json

import pytest

from readers.capture import (
    ProvenanceMisstated, compile_filename_patterns, compile_producer_strings,
    load_capture_catalogue, make_dimension_signal, make_filename_pattern,
    make_tool_producer_strings, metadata_property_names,
)

RATIO_TOLERANCE = 0.005          # catalogue 03's proposal; see `unc-tolerance-value`


@pytest.fixture
def filename_pattern():
    return make_filename_pattern(load_capture_catalogue("camera_filename_patterns"))


@pytest.fixture
def dimension_signal():
    return make_dimension_signal(load_capture_catalogue("screen_resolutions"),
                                 load_capture_catalogue("sensor_aspect_ratios"),
                                 tolerance=RATIO_TOLERANCE)


# --- catalogue 04: the naming conventions -----------------------------------

@pytest.mark.parametrize("filename,expected", [
    ("Screenshot 2026-08-14 at 11.03.47.png", "Screenshot 2026-08-14 at 11.03.47"),
    ("Screen Shot 2019-06-02 at 3.14.15 PM.png",
     "Screen Shot 2019-06-02 at 3.14.15 PM"),
    ("Screen Recording 2026-08-14 at 11.03.47.mov",
     "Screen Recording 2026-08-14 at 11.03.47"),
    ("Screenshot (42).png", "Screenshot (42)"),
    ("Screenshot_20260115-103045_Chrome.png", "Screenshot_20260115-103045"),
    ("IMG_20260812_223311.jpg", "IMG_20260812_223311"),
    ("IMG_4821.png", "IMG_4821"),
    ("DSC01234.ARW", "DSC01234"),
])
def test_the_shipped_conventions_return_the_source_substring(
        filename_pattern, filename, expected):
    """P4 RAW-1: `raw_value` is the source substring, never a value P5 built.

    P5 writes `emit(zone="filename", raw=matched)`, so `matched` BECOMES the
    observation's `raw_value` -- which settles catalogue 04's `unc-return-value`
    for this deployment in the direction the catalogue calls "the safer reading":
    return the `capture`, not the `pattern_label`. The label is the deployment's
    prose about the file; the capture is the file's own name.
    """
    assert filename_pattern(filename) == expected


@pytest.mark.parametrize("filename", [
    "MATH2010.png", "ECON1001.png", "BUSIB4300.pdf", "CHEM1220.jpg",
    "Screenshot of the enrollment error.png", "holiday.jpg", "IMG_final_v3.jpg",
])
def test_a_string_no_convention_claims_produces_nothing(filename_pattern, filename):
    """Catalogue 04's `ref-dcf-generic`: the standard's own generic shape
    `^[A-Z0-9_]{4}[0-9]{4}$` is REFUSED because it matches course codes, and a
    course code read as a camera filename is catastrophic in this corpus.
    "Absence is not evidence" -- no match, no observation, no signal."""
    assert filename_pattern(filename) is None


def test_a_folder_called_screenshots_decides_nothing_about_what_is_in_it(
        filename_pattern):
    """The defect this project has just fixed elsewhere, refused here in advance.

    `Detector._matches` skips every `path` observation because "the absolute path
    is not one of the file's own words" -- a photograph in a folder called
    `Passport and Visa Documents` was being stored `protected`. The same rule
    holds one layer up: this matcher is given the FILENAME, and a directory named
    `Screenshots` cannot make `holiday.jpg` a screen capture.
    """
    assert filename_pattern("Screenshots/holiday.jpg") is None
    assert filename_pattern("/Users/jy/Screenshots/holiday.jpg") is None
    assert filename_pattern("Screenshots/Screenshot 2026-08-14 at 11.03.47.png") is None


def test_no_shipped_convention_names_a_media_type():
    """Catalogue 04's first rule: "A pattern names a naming convention, never a
    media type." Whether the file IS a screenshot is `media_type`, a Photos-domain
    fact, and P6's alone -- so no label here may state the verdict."""
    for row in load_capture_catalogue("camera_filename_patterns")["entries"]:
        label = row["pattern_label"].lower()
        for verdict in ("is a photo", "is a screenshot", "photograph of",
                        "media type"):
            assert verdict not in label, row["id"]


# --- catalogues 02 and 03: the two readings of the pixel dimensions ---------

def test_an_exact_display_resolution_wins_over_the_ratio_it_also_is(
        dimension_signal):
    """Catalogue 02's arbitration, step 1. Every 16:9 display resolution is also
    16:9, so ratio-first would make catalogue 02 unreachable for its commonest
    members. Nothing is lost: a real photograph that happens to be exactly
    1920x1080 still carries camera EXIF, which is tier 1."""
    assert dimension_signal(1920, 1080) == "exact display resolution"
    assert dimension_signal(2560, 1600) == "exact display resolution"


def test_a_panel_is_one_row_in_either_orientation(dimension_signal):
    """Catalogue 02 matches the UNORDERED pair: a rotated tablet and a landscape
    phone grab carry the swapped numbers of one panel."""
    assert dimension_signal(1080, 1920) == "exact display resolution"


def test_a_sensor_shape_that_is_no_panel_reads_as_sensor_shaped(dimension_signal):
    """Catalogue 02's rule: "No entry may be a known sensor output size."
    `4032x3024` is catalogue 03's own 4:3 anchor and is never a catalogue 02 row."""
    assert dimension_signal(4032, 3024) == "sensor-shaped dimensions"
    assert dimension_signal(6000, 4000) == "sensor-shaped dimensions"


def test_the_tolerance_is_injected_and_a_near_miss_needs_it(dimension_signal):
    """The Pixel-class 12.5 MP binned output, 4080x3072, is 0.39 % off nominal 4:3
    -- the concrete case that motivates a tolerance existing at all. With no
    tolerance it is invisible, so the number cannot live in the library file."""
    assert dimension_signal(4080, 3072) == "sensor-shaped dimensions"
    exact_only = make_dimension_signal(load_capture_catalogue("screen_resolutions"),
                                       load_capture_catalogue("sensor_aspect_ratios"),
                                       tolerance=0)
    assert exact_only(4080, 3072) is None
    assert exact_only(4032, 3024) == "sensor-shaped dimensions"


def test_dimensions_that_are_neither_carry_no_signal(dimension_signal):
    """"Absence is not evidence." A ratio that matches nothing is not a screenshot
    signal; it produces a dimensions observation with no `signal_tier` at all."""
    assert dimension_signal(1000, 700) is None


def test_the_signal_names_are_the_two_the_extractor_publishes(dimension_signal):
    """§2.6 has exactly two readings of the pixel dimensions and `extract_image`
    raises `UnknownSignal` on a third. The catalogue supplies rows, never names."""
    from extractors.image import DIMENSION_SIGNALS
    seen = {dimension_signal(w, h) for w, h in
            ((1920, 1080), (4032, 3024), (1000, 700))}
    assert seen - {None} <= set(DIMENSION_SIGNALS)


# --- catalogue 01: the producer strings, and the provenance rule ------------

def test_the_two_strings_the_design_names_are_the_two_marked_design():
    """§2.2 names `python-docx` and `Mozilla/5.0` in as many words. The other 113
    rows are the catalogue's proposals from vendor and community sourcing, and
    saying so is the difference between quoting the design and citing an author."""
    rows = load_capture_catalogue("tool_producer_strings")["entries"]
    stated = [row["id"] for row in rows if row["provenance"] == "design"]
    assert stated == ["tps-python-docx", "tps-ua-mozilla-5"]
    assert {row["provenance"] for row in rows} == {"design", "proposal"}


def test_a_proposal_may_not_be_shipped_as_something_the_design_stated():
    """THE PROVENANCE RULE, and it is enforced rather than documented.

    A row marked `design` claims the design names its literal value. That is
    checkable: the value has to appear inside the quote the row cites. A row that
    claims it without carrying it is a load error -- because a proposal wearing the
    design's authority is exactly how an invented value gets ratified by nobody.
    """
    rows = load_capture_catalogue("tool_producer_strings")["entries"]
    lie = [dict(row, provenance="design") if row["id"] == "tps-itext" else row
           for row in rows]
    assert any(row["id"] == "tps-itext" for row in rows), "fixture row vanished"
    with pytest.raises(ProvenanceMisstated) as raised:
        compile_producer_strings({"entries": lie})
    assert "tps-itext" in str(raised.value)


def test_every_shipped_catalogue_passes_its_own_provenance_rule():
    for name in ("tool_producer_strings", "screen_resolutions",
                 "sensor_aspect_ratios", "camera_filename_patterns"):
        catalogue = load_capture_catalogue(name)
        for row in catalogue["entries"]:
            assert row["provenance"] in ("design", "proposal", "inference"), row["id"]
    compile_producer_strings(load_capture_catalogue("tool_producer_strings"))
    compile_filename_patterns(load_capture_catalogue("camera_filename_patterns"))


@pytest.mark.parametrize("value,suppressed", [
    ("python-docx", True),
    ("Mozilla/5.0 (Windows NT 10.0) Chrome/121.0.0.0", True),
    ("Skia/PDF m121", True),
    ("Jane Chen", False),
    ("Docx Family Trust", False),
    ("Microsoft Word skills certificate", False),
    ("Word Association Study", False),
    ("Adobe", False),
])
def test_the_compiled_predicates_are_the_catalogues_own_acceptance_cases(
        value, suppressed):
    """The boundary rule earns its keep here: a version tail must contain a digit,
    which is what stops `Microsoft Word` claiming `Microsoft Word skills
    certificate`. Five checks found real defects during authoring and this is one
    of them, kept where the compiling now happens."""
    predicates = make_tool_producer_strings()
    assert any(matches(value) for matches in predicates) is suppressed


def test_the_property_names_arrive_flat_and_in_the_catalogues_order():
    """`facts.discount`: "`metadata_property_names` arrives FLAT: the catalogue
    groups the names by format family, and consuming that mapping here would be a
    lookup keyed by format -- the branching §2.8 exists to prevent." """
    names = metadata_property_names()
    assert names[:3] == ("Producer", "Creator", "Author")
    assert "lastModifiedBy" in names and "meta:generator" in names
    assert len(names) == len(set(names))

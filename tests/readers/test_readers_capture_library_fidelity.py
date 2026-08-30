# tests/readers/test_readers_capture_library_fidelity.py
"""The shipped library is the authored catalogue, and every authored row behaves.

`src/readers/library/*.json` was lifted out of `planning/deferred-catalogues/`. A lift
can drop a row, reorder two that share a prefix, or lose the one field that makes a
`prefix` row safe -- and the shipped file would still parse. So this reads BOTH:
`planning/` for the authored rows and their own `example_true` / `example_false`, and
`src/` for what actually ships, and asserts they agree.

The examples are not decoration. Five checks found real defects during authoring:
naive `prefix` matching made `Microsoft Word` claim `Microsoft Word skills
certificate` across 68 rows; catalogue 04's `ref-dcf-generic` refusal is the only
thing standing between a course code and a camera filename. Running them through the
SHIPPED matcher is what makes them guards on the product rather than on a file.

**Only a test may read `planning/`.** `src/readers/capture.py` reaches it never --
the four `injection` fields say so in as many words, and `production.py` reads only
`src/`-relative paths.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from readers.capture import (
    compile_producer_strings, load_capture_catalogue, make_dimension_signal,
    make_filename_pattern, make_tool_producer_strings,
)

CATALOGUES = Path(__file__).resolve().parents[2] / "planning" / "deferred-catalogues"

LIFTED = {
    "01-tool-producer-strings": "tool_producer_strings",
    "02-screen-resolutions": "screen_resolutions",
    "03-sensor-aspect-ratios": "sensor_aspect_ratios",
    "04-camera-filename-patterns": "camera_filename_patterns",
}

RATIO_TOLERANCE = 0.005


def authored(name: str) -> dict:
    return json.loads((CATALOGUES / f"{name}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("authored_name,shipped_name", sorted(LIFTED.items()))
def test_every_authored_row_ships_once_in_the_authored_order(authored_name,
                                                             shipped_name):
    """Order is load-bearing in catalogue 04 -- "`IMG_20240115_103045` must be read
    as the Android timestamp convention, not as an Apple/DCF sequence" -- and a lift
    that sorted the rows would break it silently."""
    source = [row["id"] for row in authored(authored_name)["entries"]]
    shipped = [row["id"] for row in load_capture_catalogue(shipped_name)["entries"]]
    assert shipped == source


def test_every_producer_string_example_behaves_through_the_shipped_predicates():
    """Catalogue 01's `example_false` means "matches NO row anywhere in the file"."""
    predicates = make_tool_producer_strings()
    fired = lambda value: any(matches(value) for matches in predicates)
    for row in authored("01-tool-producer-strings")["entries"]:
        assert fired(row["example_true"]), f"{row['id']}: {row['example_true']!r}"
        assert not fired(row["example_false"]), f"{row['id']}: {row['example_false']!r}"
    for row in (authored("01-tool-producer-strings")["refused"]
                + authored("01-tool-producer-strings")["uncertain"]):
        assert not fired(row["example_false"]), (
            f"{row['id']} is refused or uncertain and {row['example_false']!r} "
            "matched a live row")


def test_every_filename_convention_example_behaves_through_the_shipped_matcher():
    """Catalogue 04's `example_false` means something narrower and it says so: the
    rows are sibling conventions sharing prefixes, so it proves THIS row does not
    claim a string another row rightly claims. Where that is the intent the row
    names the winner in `discriminates_from`, and the collision has to land on
    exactly that row -- a new collision, or one that moves, still fails."""
    pattern = make_filename_pattern()
    rows = authored("04-camera-filename-patterns")["entries"]
    by_id = {row["id"]: row for row in rows}
    for row in rows:
        expected = _capture(row, row["example_true"])
        assert pattern(row["example_true"]) == expected, row["id"]
        winner = row.get("discriminates_from")
        if winner is None:
            assert pattern(row["example_false"]) is None, row["id"]
        else:
            assert pattern(row["example_false"]) == _capture(
                by_id[winner], row["example_false"]), row["id"]


def _capture(row: dict, filename: str) -> str:
    import re
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    flags = 0 if row["case_sensitive"] else re.IGNORECASE
    return re.match(row["pattern"], stem, flags).group(row["capture"])


def test_a_course_code_reads_as_no_camera_convention_and_img_4821_reads_as_one():
    """The brief's own acceptance pair, and the reason `ref-dcf-generic` exists.
    `^[A-Z0-9_]{4}[0-9]{4}$` is the DCF standard's generic shape and it matches
    `MATH2010`. Two independently authored versions of this catalogue refused it
    without sight of each other."""
    pattern = make_filename_pattern()
    assert pattern("IMG_4821.png") == "IMG_4821"
    for course_code in ("MATH2010.png", "ECON1001.png", "FALL2024.png",
                        "NOTE2024.jpg", "CHEM1220.jpg", "BUSIB4300.pdf"):
        assert pattern(course_code) is None, course_code


def test_every_resolution_and_ratio_example_behaves_through_the_shipped_signal():
    signal = make_dimension_signal(tolerance=RATIO_TOLERANCE)
    for row in authored("02-screen-resolutions")["entries"]:
        for key in ("example_true", "example_true_2"):
            if row.get(key):
                width, height = (int(part) for part in row[key].split("x"))
                assert signal(width, height) == "exact display resolution", row["id"]
    for row in authored("03-sensor-aspect-ratios")["entries"]:
        width, height = (int(part) for part in row["example_true"].split("x"))
        assert signal(width, height) == "sensor-shaped dimensions", row["id"]


def test_no_display_resolution_is_a_known_sensor_output_size():
    """Catalogue 02's rule, and catalogue 03's `sensor_output_sizes` is the list it
    is measured against. `4032x3024` is a catalogue-03 anchor and never a
    catalogue-02 row -- if it were, every iPhone photograph would carry the
    screenshot band."""
    panels = {row["match"] for row in load_capture_catalogue("screen_resolutions")["entries"]}
    for size in authored("03-sensor-aspect-ratios")["sensor_output_sizes"]:
        value = size["match"]
        width, height = (int(part) for part in value.lower().split("x"))
        assert f"{max(width, height)}x{min(width, height)}" not in panels, value


def test_the_shipped_property_names_are_the_authored_ones_flattened():
    source = authored("01-tool-producer-strings")["property_names"]
    expected: list[str] = []
    for family in source.values():
        if isinstance(family, list):
            for name in family:
                if name not in expected:
                    expected.append(name)
    assert list(load_capture_catalogue("tool_producer_strings")["property_names"]) == expected


def test_the_lift_kept_the_field_that_makes_a_prefix_row_safe():
    """`tail_required` is carried on exactly the rows that set it. Dropping it
    would make those rows stop firing and 84 others keep firing -- a change no
    example in the file would catch, because the rows that set it are the ones
    whose tail has no digit."""
    source = {row["id"]: row.get("tail_required")
              for row in authored("01-tool-producer-strings")["entries"]}
    shipped = {row["id"]: row.get("tail_required")
               for row in load_capture_catalogue("tool_producer_strings")["entries"]}
    assert shipped == source
    assert [row for row, value in source.items() if value] == [
        "tps-reportlab", "tps-latex-hyperref"]


def test_no_number_beyond_zero_and_one_is_shipped_in_the_library():
    """The tolerance and the nominal decimals stayed in `planning/`; the capture
    group index is 1. Catalogue 03 says it of its own tolerance: "It is a number,
    so it must not live inside `src/extractors/` either." """
    def numbers(value):
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            yield value
        elif isinstance(value, dict):
            for item in value.values():
                yield from numbers(item)
        elif isinstance(value, list):
            for item in value:
                yield from numbers(item)

    for shipped_name in LIFTED.values():
        for found in numbers(load_capture_catalogue(shipped_name)):
            assert found in (0, 1), f"{shipped_name} ships {found!r}"

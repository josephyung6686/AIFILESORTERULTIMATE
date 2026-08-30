# tests/readers/test_readers_capture_reaches_the_extractor.py
"""The catalogues, through the shipped `Readers`, into E5's actual observations.

The gap this closes was never that the work was not done. Catalogues 01-04 were
complete, checked and committed on 2026-08-20; `src/extractors/image.py` declared
`dimension_signal` and `filename_pattern` as required keywords with no default so
they could be injected; and `readers/deployment.py` injected two lambdas returning
`None` behind a `read_image` that returned `None` first. So `extract_image` reached
its second line and stopped, every image in a corpus recorded
`image.metadata: unsupported`, and no test anywhere asserted otherwise -- because
every P5 test injects its own reader and its own catalogue stubs, which is exactly
the shape of defect that lets a whole shipped route be dead.

These tests use the DEPLOYMENT's readers, not stubs. That is the point of them.
"""
from __future__ import annotations

import struct
import zlib

import pytest

from extractors.image import extract_image
from extractors.safety import ProtectedContainerRefused, SafetyPolicy
from readers.deployment import macos_readers

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)


@pytest.fixture
def readers():
    return macos_readers(find_structured_strings=lambda text: ())


def png(path, width, height):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IEND", b""))
    return path


def run(readers, path, *, policy=OPEN_POLICY):
    file_row = {"file_id": "f1", "content_hash": "h1", "filename": path.name}
    return extract_image(file_row=file_row, path=path, policy=policy,
                         read_image=readers.read_image,
                         dimension_signal=readers.dimension_signal,
                         filename_pattern=readers.filename_pattern,
                         now="2026-08-31T00:00:00Z", context_window=0)


def slots(result):
    found = {}
    for one in result.observations:
        path = one["location"].get("container_path") or []
        label = path[0]["label"] if path else one["location"]["zone"]
        found[label] = (one["raw_value"], one.get("signal_tier"), one["reliability"])
    return found


def test_a_macos_screenshot_now_produces_section_2_6s_evidence(readers, tmp_path):
    """What the run used to produce for this file: nothing, and one
    `image.metadata: unsupported` row."""
    result = run(readers, png(tmp_path / "Screenshot 2026-08-14 at 11.03.47.png",
                              2560, 1600))
    assert result.run["completeness"] == "complete"
    found = slots(result)
    assert found["format"] == ("PNG", 3, "direct")
    assert found["pixel dimensions"] == ("2560x1600", 3, "direct")
    assert found["filename"] == ("Screenshot 2026-08-14 at 11.03.47", None, "possible")


def test_a_camera_shaped_image_carries_the_reinforcing_band(readers, tmp_path):
    """§2.6: "sensor-shaped dimensions reinforce it" -- tier 2, not tier 3. The
    difference decides whether §2.7 sends the file to OCR at all."""
    found = slots(run(readers, png(tmp_path / "IMG_20260812_223311.jpg", 4032, 3024)))
    assert found["pixel dimensions"] == ("4032x3024", 2, "direct")
    assert found["filename"] == ("IMG_20260812_223311", None, "possible")


def test_the_name_never_outranks_what_the_image_itself_says(readers, tmp_path):
    """THE FIRST NEGATIVE TWIN. A file called `Screenshot ...` whose pixels are a
    4:3 sensor readout: the convention still produces its observation, and it
    carries NO `signal_tier` -- so §3.7 ranks it below the tier-2 dimensions and
    below any tier-1 camera EXIF a richer reader would add. A filename cannot
    claim a file whose content says otherwise, because §2.6's tier table gives a
    filename no band to claim it from."""
    found = slots(run(readers, png(tmp_path / "Screenshot 2026-08-14 at 11.03.47.png",
                                   4032, 3024)))
    assert found["filename"][1] is None
    assert found["pixel dimensions"] == ("4032x3024", 2, "direct")


def test_a_folder_called_screenshots_makes_nothing_inside_it_a_screenshot(
        readers, tmp_path):
    """THE SECOND NEGATIVE TWIN, and the defect this project has just fixed one
    layer down. `Detector._matches` now skips every `path` observation because
    "the absolute path is not one of the file's own words" -- a contentless
    photograph in a folder called `Passport and Visa Documents` was being stored
    `sensitive_personal, protected=True`. The same rule holds here: `holiday.jpg`
    under `Screenshots/` produces no filename observation at all."""
    result = run(readers, png(tmp_path / "Screenshots" / "holiday.jpg", 4032, 3024))
    found = slots(result)
    assert "filename" not in found
    assert found["pixel dimensions"] == ("4032x3024", 2, "direct")


def test_a_protected_container_is_never_asked_what_its_filename_looks_like(
        readers, tmp_path):
    """THE STANDING RULE. A protected container is MARKED AND COUNTED, NEVER
    OPENED, and `admit` is the first statement of every extractor "before its
    reader is touched". A screenshot can contain anything, so a filename rule must
    not be the thing that reaches inside one -- and it is not even consulted."""
    asked: list[str] = []
    readers = macos_readers(
        find_structured_strings=lambda text: (),
        filename_pattern=lambda name: asked.append(name))
    path = png(tmp_path / "Photos.photoslibrary"
               / "Screenshot 2026-08-14 at 11.03.47.png", 2560, 1600)
    sealed = SafetyPolicy(
        is_protected_container=lambda p: ".photoslibrary" in str(p),
        is_dataless=lambda p: False)
    with pytest.raises(ProtectedContainerRefused):
        run(readers, path, policy=sealed)
    assert asked == []


def test_a_format_with_no_branch_is_still_unsupported(readers, tmp_path):
    """Wiring a reader must not turn "this product cannot open HEIC" into a claim
    that it read one. `tests/readers/test_readers_end_to_end.py` asserts the same
    property through the whole pipeline."""
    path = tmp_path / "scan.heic"
    path.write_bytes(b"\x00\x00\x00\x18ftypheic not really an image")
    result = run(readers, path)
    assert result.run["completeness"] == "unsupported"
    assert result.observations == ()

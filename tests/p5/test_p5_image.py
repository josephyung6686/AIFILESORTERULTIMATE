# tests/p5/test_p5_image.py
"""E5 - §2.6. Done-means 8: "HEIC extracts. The three §2.6 traps — stripped EXIF,
dense OCR text, conflicting signals — each produce abstention, and E5 emits no
photo/screenshot conclusion at all."
"""
import inspect
from pathlib import Path

import pytest

from extractors.image import (
    DIMENSIONS_FIELD, DIMENSION_SIGNALS, EXTRACTOR_NAME, ExifValue,
    FILENAME_PATTERN_FIELD, FORMAT_FIELD, ImageRecord, PERCEPTUAL_HASH_FIELD,
    SIGNAL_TIER, UnknownSignal, extract_image,
)
from extractors.safety import DatalessRefused, ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-img", "content_hash": "c977b477a6329f00518d55e10bb5c469fc6b24e8528f3fc1a9bbbbe94a6feada",
            "filename": "IMG_4821.heic"}

NO_DIMENSION_SIGNAL = lambda width, height: None
NO_PATTERN = lambda filename: None


def a_photo_heic() -> ImageRecord:
    """The SPEC's `photo.heic`."""
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        perceptual_hash="phash:8f3a",
        exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),
              ExifValue(name="Model", value="iPhone 15 Pro", kind="camera EXIF"),
              ExifValue(name="DateTimeOriginal", value="2026:07:17 14:03:22",
                        kind="capture time"),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS")),
        color={"ColorSpace": "sRGB"},
        software={"Software": "iOS 19.1"})


def run_it(record=None, *, dimension_signal=NO_DIMENSION_SIGNAL,
           filename_pattern=NO_PATTERN, file_row=None):
    # `.extraction`: E5 became a signal emitter against CR-05b, so it returns an
    # `ImageResult` -- the batch plus §8.4's always-local signals -- the way
    # `long_tail` already did. `tests/p5/test_p5_image_sensitivity.py` is the half of
    # that this file does not cover.
    return extract_image(
        file_row=file_row or FILE_ROW, path=Path("/corpus/IMG_4821.heic"),
        policy=OPEN_POLICY,
        read_image=lambda target: record if record is not None else a_photo_heic(),
        dimension_signal=dimension_signal, filename_pattern=filename_pattern,
        now=FIXED_CLOCK, context_window=20).extraction


def slots(rows):
    return {r["location"]["container_path"][0]["label"]: r
            for r in rows if r["location"]["container_path"]}


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_heic_extracts_and_its_camera_exif_is_tier_one(sink):
    # §2.6: "HEIC support must be included explicitly." A required test.
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows[FORMAT_FIELD]["raw_value"] == "HEIC"
    assert rows[DIMENSIONS_FIELD]["raw_value"] == "4032x3024"
    assert rows["Make"]["signal_tier"] == 1
    assert rows["Model"]["signal_tier"] == 1


def test_every_section_2_6_signal_carries_its_own_tier(sink):
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows["DateTimeOriginal"]["signal_tier"] == SIGNAL_TIER["capture time"] == 2
    assert rows["GPSLatitude"]["signal_tier"] == 2
    assert rows["Software"]["signal_tier"] == SIGNAL_TIER["software metadata"] == 3
    assert rows["ColorSpace"]["signal_tier"] is None


def test_the_perceptual_hash_is_emitted_and_the_content_hash_is_not(sink):
    # G5 gives duplicate and version families to P6, "from P1's content hashes and
    # P5's perceptual hashes". P5 supplies the second and recomputes the first never.
    run_id = sink.write(run_it())
    rows = slots(sink.observations_for(run_id))
    assert rows[PERCEPTUAL_HASH_FIELD]["raw_value"] == "phash:8f3a"
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == FILE_ROW["content_hash"]]


def test_file_size_and_filename_are_not_re_emitted(sink):
    # O5: they are P3's §1.2 record, surfaced by the `filesystem` run (Task 6).
    run_id = sink.write(run_it())
    labels = set(slots(sink.observations_for(run_id)))
    assert "file size" not in labels
    assert not [o for o in sink.observations_for(run_id)
                if o["raw_value"] == FILE_ROW["filename"]]


def test_png_format_is_section_2_6s_tier_three_signal(sink):
    record = ImageRecord(image_format="PNG", dimensions="2880x1800", width=2880,
                         height=1800)
    run_id = sink.write(run_it(record=record))
    assert slots(sink.observations_for(run_id))[FORMAT_FIELD]["signal_tier"] == 3


def test_stripped_exif_writes_nothing_at_all_about_the_absence(sink):
    # The SPEC's `whatsapp-stripped-exif.jpg`: a real photograph, EXIF removed.
    record = ImageRecord(image_format="JPEG", dimensions="1080x1440", width=1080,
                         height=1440)
    run_id = sink.write(run_it(record=record))
    rows = sink.observations_for(run_id)
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert all(o["signal_tier"] is None for o in rows), "a screenshot signal exists"
    joined = " ".join(o["raw_value"] for o in rows).lower()
    for word in ("absent", "missing", "stripped", "none", "no exif"):
        assert word not in joined
    sink.conforms()


def test_e5_is_given_no_text_so_text_density_cannot_become_a_signal():
    # §2.6: "OCR text density is also not a reliable screenshot detector." The
    # strongest available statement of that is that no text is in scope at all.
    parameters = set(inspect.signature(extract_image).parameters)
    assert not {"text", "ocr", "ocr_text", "recognized_text"} & parameters
    fields = set(inspect.signature(ImageRecord).parameters)
    assert not {"text", "ocr", "ocr_text", "text_density"} & fields


def test_conflicting_signals_are_two_observations_and_no_resolution(sink):
    # The SPEC's `conflicting-signals.png`: camera EXIF AND an exact display
    # resolution. Two raw values, so P4 D10 makes them two rows.
    record = ImageRecord(
        image_format="PNG", dimensions="1170x2532", width=1170, height=2532,
        exif=(ExifValue(name="Make", value="Canon", kind="camera EXIF"),))
    run_id = sink.write(run_it(
        record=record,
        dimension_signal=lambda width, height: "exact display resolution"))
    rows = slots(sink.observations_for(run_id))
    assert rows["Make"]["signal_tier"] == 1
    assert rows[DIMENSIONS_FIELD]["signal_tier"] == 3
    # No conflict row, no resolution, no classification.
    joined = " ".join(o["raw_value"] for o in sink.observations_for(run_id)).lower()
    for word in ("conflict", "screenshot", "photo", "resolved", "abstain"):
        assert word not in joined
    sink.conforms()


def test_e5_emits_no_photo_or_screenshot_conclusion(sink):
    # §3.11's `media type` is a Photos-domain FACT and belongs to P6.
    run_id = sink.write(run_it())
    for o in sink.observations_for(run_id):
        assert "media_type" not in o and "screenshot" not in o
        assert o["location"]["zone"] in ("metadata", "filename")


def test_the_resolution_list_and_the_aspect_ratios_are_the_callers():
    # §2.6 Deferred: "which resolutions" and "which aspect ratios qualify".
    for name in ("dimension_signal", "filename_pattern", "read_image"):
        parameter = inspect.signature(extract_image).parameters[name]
        assert parameter.default is inspect.Parameter.empty, name


def test_a_dimension_signal_section_2_6_does_not_name_is_refused():
    assert DIMENSION_SIGNALS == ("sensor-shaped dimensions",
                                 "exact display resolution")
    with pytest.raises(UnknownSignal):
        run_it(dimension_signal=lambda width, height: "retina-ish")


def test_an_exif_kind_section_2_6_does_not_name_is_refused():
    record = ImageRecord(image_format="JPEG", dimensions="1x1", width=1, height=1,
                         exif=(ExifValue(name="X", value="y", kind="vibes"),))
    with pytest.raises(UnknownSignal):
        run_it(record=record)


def test_the_filename_pattern_is_the_callers_match(sink):
    # §2.6's own example is `IMG_4821.png`; the pattern SET is Deferred.
    run_id = sink.write(run_it(filename_pattern=lambda name: "IMG_4821"))
    pattern = [o for o in sink.observations_for(run_id)
               if o["location"]["zone"] == "filename"][0]
    assert pattern["raw_value"] == "IMG_4821"
    assert pattern["signal_tier"] is None
    assert pattern["location"]["text_span"] is None


def test_the_same_image_produces_the_same_observations(sink):
    first, second = sink.write(run_it()), sink.write(run_it())
    strip = lambda rows: [{k: v for k, v in r.items() if k != "run_id"} for r in rows]
    assert strip(sink.observations_for(first)) == strip(sink.observations_for(second))


def test_no_extractor_is_reachable_inside_a_protected_container():
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_image(file_row=FILE_ROW,
                      path=Path("/Applications/Photos.app/Contents/a.heic"),
                      policy=policy,
                      read_image=lambda target: pytest.fail("reader reached"),
                      dimension_signal=NO_DIMENSION_SIGNAL,
                      filename_pattern=NO_PATTERN, now=FIXED_CLOCK,
                      context_window=20)


# --------------------------------------------------------------------------- #
# `104` §18.2 gap 18 -- the facts reach the store, and what was never read says so
# --------------------------------------------------------------------------- #


def test_every_capture_metadata_fact_is_a_metadata_row_a_citation_can_address(sink):
    """`00`:32's facts have to arrive somewhere a model can CITE them. A citation
    carries "exactly one of `cited_span` or `metadata_field_name`", and
    `metadata_field_name` "must equal that item's address exactly" -- so an image
    fact is usable at site A and site G only if it is in zone `metadata` with the
    format's own slot name as its address. Every one of §2.6's slots is."""
    run_id = sink.write(run_it())
    rows = sink.observations_for(run_id)
    addressed = slots(rows)

    for label in ("Make", "Model", "DateTimeOriginal", "GPSLatitude", "Software",
                  "ColorSpace", FORMAT_FIELD, DIMENSIONS_FIELD):
        row = addressed[label]
        assert row["location"]["zone"] == "metadata", label
        segment, = row["location"]["container_path"]
        assert segment["kind"] == "field" and segment["label"] == label
        # A metadata field is a whole slot, so there is no span to cite instead --
        # which is exactly why `metadata_field_name` is the citation form for it.
        assert row["location"]["text_span"] is None, label


def test_a_run_that_read_everything_it_can_says_so_and_stays_complete(sink):
    """The ordinary path. `unread` is present and `None`, so one image run has one
    config shape and a reader that read the file's metadata is never confused with
    one that could not."""
    run_id = sink.write(run_it())
    run = sink.run_for(run_id)
    assert run["completeness"] == "complete"
    assert run["config"]["unread"] is None


def test_what_was_never_read_is_named_on_the_run_and_never_in_a_row(sink):
    """§18.2 gap 18: "what a format cannot supply is recorded as the honest reason on
    the extraction run", and P4 decides where. `failure_reason` is gated to
    `unreadable` and `failed` -- this file WAS read -- and an absence may not be an
    observation ("the run record already says it, and an absence written as evidence
    is a value P6 can rank"). So the sentence lands in the run's `config`, the one
    run field P4 leaves schema-free, and the run is `partial`."""
    reason = ("the image stack recognises no image format in these bytes, so §2.6's "
              "EXIF, capture-time, GPS, colour and software slots were never looked "
              "at")
    record = ImageRecord(image_format="SVG", dimensions="240x120", width=240,
                         height=120, unread_reason=reason)
    run_id = sink.write(run_it(record=record))
    run = sink.run_for(run_id)

    assert run["completeness"] == "partial"
    assert run["config"]["unread"] == reason
    # The rows the file DID yield are still there -- `partial` is not a stop.
    assert slots(sink.observations_for(run_id))[FORMAT_FIELD]["raw_value"] == "SVG"
    # And nothing about the absence became evidence.
    joined = " ".join(o["raw_value"] for o in sink.observations_for(run_id))
    assert "never looked at" not in joined
    sink.conforms()


def test_two_runs_that_read_different_amounts_have_different_fingerprints(sink):
    """§3.4's key and §8.5's diff exist "so they can tell configs apart", and a run
    whose metadata route never ran was not configured the same way as one whose did.
    Recording the reason in `config` makes that difference visible instead of
    leaving two runs that read different things looking identical."""
    read_everything = sink.run_for(sink.write(run_it()))
    read_nothing = sink.run_for(sink.write(run_it(record=ImageRecord(
        image_format="SVG", dimensions="8x8", width=8, height=8,
        unread_reason="§2.6's slots were never looked at"))))
    assert (read_everything["config_fingerprint"]
            != read_nothing["config_fingerprint"])


def test_a_dataless_image_is_never_materialized():
    policy = SafetyPolicy(is_protected_container=lambda path: False,
                          is_dataless=lambda path: True)
    with pytest.raises(DatalessRefused):
        extract_image(file_row=FILE_ROW, path=Path("/corpus/IMG_4821.heic"),
                      policy=policy,
                      read_image=lambda target: pytest.fail("reader reached"),
                      dimension_signal=NO_DIMENSION_SIGNAL,
                      filename_pattern=NO_PATTERN, now=FIXED_CLOCK,
                      context_window=20)

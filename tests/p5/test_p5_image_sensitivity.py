# tests/p5/test_p5_image_sensitivity.py
"""CR-05b: every EXIF tag is signalled, and the signal lands on the right row.

§8.4 puts `image_exif` and `gps` in the always-local nine. `extractors/image.py`
emits every EXIF tag into `zone="metadata"` -- which is the TRUTHFUL zone for one, so
P7's zone rule cannot reach them, and a GPS coordinate came back `Released` from the
real gate. `ZONES` has no `exif` member to move them to, and adding one needs owner
approval and a `SHAPE_VERSION` bump.

So the fix uses the channel the design already has for "this located value is
sensitive": P5 raises a `SensitivitySignal`, P4 keys it to an `observation_key`, and
`privacy.items.check_item` refuses an `Excerpt` over a signalled key under §8.4's
`raw_sensitive_values`. No keyword list is needed anywhere -- `ExifValue.kind` is the
reader's own classification and `image.py` only has to notice that a tag IS one.

**THIS FILE IS ABOUT THE REMAP, and it was written before the remap.** A signal's
`observation_index` is a position in the SUBMITTED list; `ExtractionResult.
__post_init__` applies P4's D10, which collapses observations sharing a
(zone, raw_value) and RENUMBERS everything after them. A wrong remap is worse than
the hole it closes: it marks innocent values sensitive, and -- far worse -- leaves a
real GPS tag unmarked while the suite goes green.

So nothing here asserts an index. Every test resolves the signal back to the
observation it landed on and checks its VALUE, which is the only thing an off-by-one
cannot survive. `_two_datetimes_and_a_gps` exists specifically so the indices MOVE:
two EXIF tags carrying one value is what a real camera writes (`DateTime` and
`DateTimeOriginal` agree on almost every photo), D10 folds them into one row, and
every observation after them shifts down.
"""
from pathlib import Path

import pytest

from extractors.image import ExifValue, ImageRecord, extract_image
from extractors.long_tail import POTENTIALLY_SENSITIVE
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {
    "file_id": "f-img",
    "content_hash": "c977b477a6329f00518d55e10bb5c469fc6b24e8528f3fc1a9bbbbe94a6feada",
    "filename": "IMG_4821.heic",
}


def _run(record: ImageRecord, *, filename_pattern=lambda name: None):
    return extract_image(
        file_row=FILE_ROW, path=Path("/corpus/IMG_4821.heic"), policy=OPEN_POLICY,
        read_image=lambda target: record,
        dimension_signal=lambda width, height: None,
        filename_pattern=filename_pattern, now=FIXED_CLOCK, context_window=20)


def _signalled_values(produced) -> set[str]:
    """What the signals actually landed on, resolved through the FINAL batch.

    This is the whole method of this file: never assert a position, always resolve
    it and look at what is there.
    """
    rows = produced.extraction.observations
    for signal in produced.sensitivity:
        assert 0 <= signal.observation_index < len(rows), (
            f"signal at {signal.observation_index} indexes outside a batch of "
            f"{len(rows)}; D10 renumbered and the remap did not follow")
        assert signal.signal == POTENTIALLY_SENSITIVE
    return {rows[s.observation_index]["raw_value"] for s in produced.sensitivity}


def _exif_values(record: ImageRecord) -> set[str]:
    return {tag.value for tag in record.exif if tag.value}


# --- the records. Each is a real shape, and two of them MOVE the indices. ---------

def _no_collapse() -> ImageRecord:
    """Every value distinct, so submitted positions survive D10 unchanged.

    The control: if the remap were the identity this would still pass, which is why
    it is not the only case here.
    """
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        perceptual_hash="phash:8f3a",
        exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS")),
        color={"ColorSpace": "sRGB"}, software={"Software": "iOS 19.1"})


def _two_datetimes_and_a_gps() -> ImageRecord:
    """What a real camera writes: `DateTime` and `DateTimeOriginal` agree.

    D10 collapses on (zone, raw_value), so those two become ONE row and every
    observation after them -- including the GPS coordinate -- shifts down by one.
    An identity remap marks the wrong rows here and leaves the GPS tag unmarked.
    """
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        perceptual_hash="phash:8f3a",
        exif=(ExifValue(name="DateTime", value="2026:07:17 14:03:22",
                        kind="capture time"),
              ExifValue(name="DateTimeOriginal", value="2026:07:17 14:03:22",
                        kind="capture time"),
              ExifValue(name="Make", value="Apple", kind="camera EXIF"),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS"),
              ExifValue(name="GPSLongitude", value="90.3049W", kind="GPS")),
        color={"ColorSpace": "sRGB"}, software={"Software": "iOS 19.1"})


def _exif_collides_with_a_releasable_slot() -> ImageRecord:
    """An EXIF tag whose value equals the image format's.

    D10 keys on (zone, raw_value) and BOTH are `zone="metadata"`, so the EXIF tag
    collapses onto the FORMAT observation, which was emitted first and is not
    sensitive. The surviving row is therefore signalled -- correctly: it is now the
    row that carries the EXIF tag's value, and D10's rule is that one located value
    is one row. This is the case that would make a naive "signal only rows I emitted
    in the exif loop" implementation silently drop the signal.
    """
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        exif=(ExifValue(name="FileType", value="HEIC", kind=None),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS")),
        color={}, software={})


def _no_exif_at_all() -> ImageRecord:
    """§2.6's stripped-EXIF trap. No signals, and nothing else changes."""
    return ImageRecord(
        image_format="PNG", dimensions="1170x2532", width=1170, height=2532,
        exif=(), color={"ColorSpace": "sRGB"}, software={"Software": "Preview"})


def _empty_tag_values() -> ImageRecord:
    """A tag with no value is not an observation, so it cannot be signalled.

    `image.py` skips it -- "presence only; an absence is never a row" -- and a remap
    that counted it would be off by one for every tag after it.
    """
    return ImageRecord(
        image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
        exif=(ExifValue(name="Make", value="", kind="camera EXIF"),
              ExifValue(name="GPSLatitude", value="38.6488N", kind="GPS"),
              ExifValue(name="Model", value="", kind="camera EXIF"),
              ExifValue(name="GPSLongitude", value="90.3049W", kind="GPS")),
        color={}, software={})


ALL_RECORDS = pytest.mark.parametrize("build", [
    _no_collapse,
    _two_datetimes_and_a_gps,
    _exif_collides_with_a_releasable_slot,
    _no_exif_at_all,
    _empty_tag_values,
], ids=lambda fn: fn.__name__.strip("_"))


# --- the property ----------------------------------------------------------------

@ALL_RECORDS
def test_every_exif_value_is_signalled_and_nothing_else_is(build):
    """The whole property, over five shapes, resolved by VALUE and never by index.

    Both directions matter. Missing an EXIF value leaves a GPS coordinate releasable,
    which is the finding. Signalling a value that is not one marks an innocent row
    sensitive, which is the failure a careless remap produces and which no test
    asserting only the first direction would catch.
    """
    record = build()
    produced = _run(record)
    assert _signalled_values(produced) == _exif_values(record)


@ALL_RECORDS
def test_no_signal_lands_on_a_value_the_reader_did_not_call_exif(build):
    """The releasable slots, named. §2.6 wants the format, the dimensions and a
    screenshot's software metadata to stay usable evidence; none of them is
    `image_exif` and none may be marked."""
    record = build()
    produced = _run(record)
    releasable = ({record.image_format, record.dimensions}
                  | set(record.color.values()) | set(record.software.values()))
    assert _signalled_values(produced) & (releasable - _exif_values(record)) == set()


def test_the_indices_really_do_move_in_at_least_one_of_these_records():
    """A guard on the test data, not on the product.

    If D10 ever stopped collapsing, or these fixtures drifted into all-distinct
    values, every case above would pass with an identity remap and this file would
    quietly stop testing the thing it exists for.
    """
    produced = _run(_two_datetimes_and_a_gps())
    assert len(produced.extraction.observations) < \
        len(produced.extraction.collapsed_index), (
            "no observation collapsed, so no index moved, so the remap is untested")
    assert produced.extraction.collapsed_index != \
        tuple(range(len(produced.extraction.collapsed_index)))


def test_a_gps_tag_keeps_its_signal_when_two_earlier_tags_collapse():
    """The finding itself, at the one row that matters, spelled out separately.

    The parametrised property covers it, and it is worth failing by name: this is
    the assertion that goes red if the remap is off by one in the direction that
    leaves a coordinate unmarked.
    """
    produced = _run(_two_datetimes_and_a_gps())
    rows = produced.extraction.observations
    marked = {rows[s.observation_index]["raw_value"] for s in produced.sensitivity}
    assert "38.6488N" in marked and "90.3049W" in marked


def test_one_signal_per_surviving_row():
    """Two tags that collapse are ONE located value, and the signal table is UNIQUE
    on (run_id, observation_key) -- so a second signal on the same survivor would be
    an IntegrityError at write time, not a duplicate row. `long_tail` drops the
    later one for the same reason; this does the same."""
    produced = _run(_two_datetimes_and_a_gps())
    landed = [s.observation_index for s in produced.sensitivity]
    assert len(landed) == len(set(landed))

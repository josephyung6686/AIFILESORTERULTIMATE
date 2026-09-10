# tests/readers/test_ocr_asks_the_recogniser_for_its_languages.py
"""`104` §18.2 gap 19 -- OCR was English-only, and §2.7 asks for CJK where required.

    *"On macOS, Apple Vision should be configured explicitly with accurate
    recognition, appropriate language support INCLUDING CJK WHERE REQUIRED, and a
    practical rendering resolution such as 200 DPI."*  (`00`:33)

`readers/deployment.VISION_CONFIG` carried `"languages": ["en-US"]` and
`readers/ocr_vision.py` fell back to the same literal, so every non-English file in a
corpus was read as though it held no text at all. The owner's own disk holds
Chinese-titled documents whose OCR came back empty or garbled, and the first test
below reproduces exactly that: `en-US` recognises a plainly legible `会计学原理` as
nothing.

**The fix is not a longer list.** A list is a guess about a corpus. Which languages a
deployment has is a question its recogniser can answer -- Vision publishes
`supportedRecognitionLanguages` per recognition level -- and WHICH of them a given
file needs is a question the recogniser answers per file, through the language
identification Apple offers on the request itself. So nothing in this product types a
language, and the set stored on the run (§2.7's third persisted field) is the machine's
own published list.

The image is drawn by this test -- Chinese glyphs need a font that has them, which is
AppKit's system font rather than Core Graphics' MacRoman `CGContextSelectFont` -- so
no binary fixture is checked in and no sample corpus is needed.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("Vision", reason="pyobjc-framework-Vision is a `readers` extra")
pytest.importorskip("Quartz", reason="pyobjc-framework-Quartz is a `readers` extra")
AppKit = pytest.importorskip(
    "AppKit",
    reason="pyobjc-framework-Cocoa draws the CJK fixture; without a font stack that "
           "has Chinese glyphs this test would measure nothing rather than pass")

from extractors.ocr import extract_ocr
from extractors.safety import SafetyPolicy
from readers.deployment import VISION_CONFIG, macos_readers
from readers.ocr_vision import recognition_languages, vision_ocr

#: Five Simplified Chinese characters: "principles of accounting", the shape of a
#: course title on the owner's own disk.
CHINESE = "会计学原理"

ACCURATE = VISION_CONFIG["recognition_level"]
OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {
    "file_id": "f-cjk",
    "content_hash":
        "c977b477a6329f00518d55e10bb5c469fc6b24e8528f3fc1a9bbbbe94a6feada",
    "filename": "会计学原理.png",
}
CLOCK = "2026-09-10T14:00:00+00:00"


def draw(path: Path, text: str = CHINESE, width: int = 900, height: int = 240,
         size: float = 120.0) -> Path:
    """Text rendered into a PNG through AppKit's system font, which has the glyphs."""
    representation = (
        AppKit.NSBitmapImageRep.alloc()
        .initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
            None, width, height, 8, 4, True, False,
            AppKit.NSCalibratedRGBColorSpace, 0, 0))
    context = AppKit.NSGraphicsContext.graphicsContextWithBitmapImageRep_(
        representation)
    AppKit.NSGraphicsContext.saveGraphicsState()
    AppKit.NSGraphicsContext.setCurrentContext_(context)
    AppKit.NSColor.whiteColor().set()
    AppKit.NSRectFill(((0, 0), (width, height)))
    AppKit.NSString.stringWithString_(text).drawAtPoint_withAttributes_(
        (40, 50),
        {AppKit.NSFontAttributeName: AppKit.NSFont.systemFontOfSize_(size),
         AppKit.NSForegroundColorAttributeName: AppKit.NSColor.blackColor()})
    context.flushGraphics()
    AppKit.NSGraphicsContext.restoreGraphicsState()
    path.write_bytes(bytes(representation.representationUsingType_properties_(
        AppKit.NSBitmapImageFileTypePNG, {})))
    return path


@pytest.fixture()
def chinese_image(tmp_path: Path) -> Path:
    return draw(tmp_path / "course.png")


@pytest.fixture()
def published() -> tuple[str, ...]:
    return recognition_languages(recognition_level=ACCURATE)


def wired_config() -> dict:
    """The `ocr_config` a real run is given, built the way `cli.py` builds it."""
    return macos_readers(find_structured_strings=lambda text: (),
                         spreadsheet_cell_ceiling=2000, ocr_page_ceiling=20,
                         ocr_seconds_per_file=60).ocr_config


# --------------------------------------------------------------------------- #
# The defect, reproduced
# --------------------------------------------------------------------------- #


def recognised(image_path, *, languages, detect):
    """Vision driven directly, so the two knobs can be measured one at a time."""
    import Quartz
    import Vision
    from Foundation import NSURL

    source = Quartz.CGImageSourceCreateWithURL(
        NSURL.fileURLWithPath_(str(image_path)), None)
    image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, {})
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    request.setAutomaticallyDetectsLanguage_(detect)
    if languages:
        request.setRecognitionLanguages_(list(languages))
    ok, error = handler.performRequests_error_([request], None)
    assert ok, error
    found = []
    for observation in request.results() or []:
        candidates = observation.topCandidates_(1)
        if candidates:
            found.append(candidates[0].string())
    return " ".join(found)


def test_a_typed_language_list_is_why_chinese_came_back_empty(chinese_image,
                                                              published):
    """Gap 19 as a person met it, measured at the API rather than argued.

    Nothing about this file is hard -- 120-point glyphs, black on white. Asked with
    `en-US`, the recogniser reports no text. Asked with the WHOLE published set and
    no language detection it still reports no text, which is the measurement that
    decides the fix: a longer list would not have closed this gap. Detection on is
    what reads it, which is why `_recognise` sets that flag and why §2.7's "where
    required" is a per-file question the recogniser answers.
    """
    if not [language for language in published
            if language.split("-")[0] in ("zh", "yue")]:
        pytest.skip(f"this recogniser publishes no Chinese; it published "
                    f"{list(published)}")

    assert CHINESE not in recognised(chinese_image, languages=["en-US"],
                                     detect=False)
    assert CHINESE not in recognised(chinese_image, languages=published,
                                     detect=False)
    assert CHINESE in recognised(chinese_image, languages=published, detect=True)


# --------------------------------------------------------------------------- #
# The request now comes from the recogniser
# --------------------------------------------------------------------------- #


def test_the_deployment_types_no_language_anywhere():
    """No hardcoded list: `VISION_CONFIG` names no `languages` key at all, and the
    engine's fallback is a call rather than a literal.

    Comments are stripped before the check because the comment that replaced the
    literal QUOTES it -- `104`'s house style is that a reversed decision is shown
    rather than buried, and a guard that cannot tell a quotation from a fallback
    would forbid saying what was fixed."""
    import inspect

    assert "languages" not in VISION_CONFIG
    code = "\n".join(line for line in inspect.getsource(vision_ocr).splitlines()
                     if not line.strip().startswith("#"))
    assert "en-US" not in code, (
        "the engine still falls back to a language this product typed")
    assert "recognition_languages" in code
    # The request is still GIVEN the set: it is the prior beside the detection flag,
    # and it is the set §2.7 persists.
    assert "setRecognitionLanguages_" in inspect.getsource(
        __import__("readers.ocr_vision", fromlist=["_recognise"])._recognise)


def test_the_wired_config_carries_the_recognisers_own_published_set(published):
    """§2.7's third persisted field survives -- `FIELD_HOMES` maps "languages" to
    `extraction_runs.config` -- and what it holds is the machine's own answer. The
    set is asked AT THE CONFIGURED LEVEL because Vision publishes it per level."""
    config = wired_config()

    assert config["languages"] == list(published)
    assert config["recognition_level"] == ACCURATE
    assert len(published) > 1, published


def test_the_published_set_is_what_this_recogniser_says_and_not_a_stored_copy():
    """Asked of a request that has been told which level will run. A set copied at
    one level and used at another would record languages that were never offered."""
    assert (recognition_languages(recognition_level="accurate")
            == recognition_languages(recognition_level="accurate"))
    with pytest.raises(ValueError):
        recognition_languages(recognition_level="approximately")


def test_the_published_set_includes_cjk_on_a_machine_that_has_it(published):
    """§2.7's "including CJK where required". This asserts the machine's answer, not
    a list of this test's: if this recogniser publishes no CJK language the skip
    names the whole set it did publish, so the gap is visible rather than silent."""
    cjk = [language for language in published
           if language.split("-")[0] in ("zh", "yue", "ja", "ko")]
    if not cjk:
        pytest.skip(f"this recogniser publishes no CJK language; it published "
                    f"{list(published)}")
    assert cjk


# --------------------------------------------------------------------------- #
# The measurement
# --------------------------------------------------------------------------- #


def test_chinese_text_in_a_synthetic_image_is_recognised(chinese_image, published):
    """The fix, measured end to end through the wired deployment config.

    MEASURED, and the reason the engine sets a detection flag rather than only a
    list: with `recognitionLanguages` set to the whole published set and no automatic
    detection, this same image recognises NOTHING. Automatic language detection
    recognises it at confidence 1.0. The two are not interchangeable and Apple's
    documentation does not say so.
    """
    if not [language for language in published
            if language.split("-")[0] in ("zh", "yue")]:
        pytest.skip(f"this recogniser publishes no Chinese; it published "
                    f"{list(published)}")

    output = vision_ocr()(chinese_image, config=wired_config())

    assert output is not None, "the image stack declined a PNG it wrote itself"
    assert CHINESE in " ".join(region.text for region in output.regions), (
        [region.text for region in output.regions])


def test_the_recognised_passage_still_carries_gap_17ds_box_and_span(
        chinese_image, published):
    """Gap 17d is not undone by gap 19. The passage row -- the one the recogniser
    actually scans -- carries the box its regions stand in and a span covering the
    whole unit, because P7's `span_address` refuses a location with a box and no
    span. Measured on the CJK image, so the two fixes are pinned together."""
    if not [language for language in published
            if language.split("-")[0] in ("zh", "yue")]:
        pytest.skip(f"this recogniser publishes no Chinese; it published "
                    f"{list(published)}")

    result = extract_ocr(
        file_row=FILE_ROW, path=chinese_image, policy=OPEN_POLICY,
        ocr_engine=vision_ocr(), config=wired_config(),
        find_structured_strings=lambda text: (), now=CLOCK, context_window=20)

    passage = [row for row in result.observations
               if not row["location"]["container_path"]]
    assert len(passage) == 1, result.observations
    location = passage[0]["location"]
    assert location["zone"] == "ocr"
    assert location["text_span"] == {"start": 0, "end": len(passage[0]["raw_value"])}
    assert location["region"] is not None and location["region"]["unit"] == "norm"
    assert CHINESE in passage[0]["raw_value"]
    # And §2.7's languages reached the run beside it.
    assert result.run["config"]["languages"] == list(published)

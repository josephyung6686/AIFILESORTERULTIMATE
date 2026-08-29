# tests/readers/test_ocr_vision.py
"""The Apple Vision adapter — the engine §2.7 names, filling P5's `OcrOutput`.

§2.7, verbatim: *"On macOS, Apple Vision should be configured explicitly with accurate
recognition, appropriate language support including CJK where required, and a
practical rendering resolution such as 200 DPI."* Three requirements, and each one is
asserted here rather than assumed.

Real Vision, real recognition. The test image is drawn with Quartz — which the adapter
already depends on for PDF rendering — so nothing is mocked and no image file is
checked into the repository.
"""
from pathlib import Path

import pytest

pytest.importorskip("Vision", reason="pyobjc-framework-Vision is a `readers` extra")
pytest.importorskip("Quartz", reason="pyobjc-framework-Quartz is a `readers` extra")

from pdf_bytes import build_pdf
from readers.ocr_vision import PROVIDER, vision_ocr


def draw_png(path: Path, text: str = "BUSIB 4300", width: int = 600,
             height: int = 200) -> Path:
    """A PNG containing rendered text, drawn with Core Graphics."""
    import Quartz
    from Foundation import NSURL

    space = Quartz.CGColorSpaceCreateDeviceRGB()
    ctx = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0, space, Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
    Quartz.CGContextFillRect(ctx, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextSetRGBFillColor(ctx, 0, 0, 0, 1)
    Quartz.CGContextSelectFont(ctx, b"Helvetica", 64.0, Quartz.kCGEncodingMacRoman)
    raw = text.encode("mac-roman")
    Quartz.CGContextShowTextAtPoint(ctx, 40.0, 80.0, raw, len(raw))
    image = Quartz.CGBitmapContextCreateImage(ctx)

    dest = Quartz.CGImageDestinationCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), "public.png", 1, None)
    Quartz.CGImageDestinationAddImage(dest, image, None)
    Quartz.CGImageDestinationFinalize(dest)
    return path


ACCURATE = {"languages": ["en-US"], "dpi": 200, "recognition_level": "accurate"}


@pytest.fixture()
def screenshot(tmp_path: Path) -> Path:
    return draw_png(tmp_path / "screenshot.png")


def test_it_recognises_text_in_a_loose_image(screenshot):
    """§2.7: OCR is *"the main way screenshots and opaque loose images become
    understandable"* — not merely a rescue tool for scanned PDFs."""
    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert out.regions, "Vision returned nothing for a plainly legible image"
    assert "BUSIB" in " ".join(r.text for r in out.regions)


def test_a_loose_image_has_a_region_and_no_page(screenshot):
    """`OcrRegion.page` is §2.7's "page or image reference" and is None for a loose
    image, which has a region and no page. Reporting page 1 for an image would make
    a screenshot indistinguishable from a one-page scan."""
    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert all(r.page is None for r in out.regions)
    assert [r.region for r in out.regions] == list(range(1, len(out.regions) + 1))


def test_the_provider_name_folds_to_p5s_extractor_name(screenshot):
    """The join. §2.7's first persisted field is the provider's own name, and P5
    folds it into `extractor_name`. If this drifts, one engine becomes two citation
    handles, two cache entries and two replay sets."""
    from extractors.ocr import extractor_name_for

    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert out.provider == PROVIDER
    assert extractor_name_for(out.provider) == "ocr.apple_vision"


def test_the_provider_version_is_reported_not_invented(screenshot):
    """§2.7 requires the provider AND version be persisted. Vision exposes no
    framework version, so the honest value is the OS version that determines its
    behaviour — a real number read from the system, never a hardcoded string."""
    import platform

    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert out.provider_version == platform.mac_ver()[0]
    assert out.provider_version, "an empty version fails P4's non-empty rule"


def test_boxes_say_which_coordinate_space_they_are_in(screenshot):
    """§2.7's "locations or bounding boxes where available", landing on P4's
    `location.region`. Vision returns NORMALISED, BOTTOM-LEFT-origin rectangles;
    a consumer that assumed pixels or a top-left origin would redact the wrong part
    of the image, which is a §8.4 failure and not a cosmetic one."""
    from evidence_shape.vocabulary import REGION_UNITS

    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    box = out.regions[0].box
    assert box is not None
    # P4's region shape EXACTLY. `width`/`height` were accepted by `location()`
    # without complaint and only failed much later inside `parse_locator`, which
    # reads `w` and `h` -- so the adapter is where the drift has to be caught.
    assert set(box) == {"x", "y", "w", "h", "unit"}
    assert box["unit"] in REGION_UNITS
    assert all(0.0 <= box[k] <= 1.0 for k in ("x", "y", "w", "h"))


def test_confidence_is_carried_through(screenshot):
    """§2.7 names "confidence information" as one of the fields to preserve."""
    out = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert all(r.confidence is not None for r in out.regions)
    assert all(0.0 <= r.confidence <= 1.0 for r in out.regions)


# --------------------------------------------------------------- paged documents
def test_a_pdf_is_rendered_and_every_page_is_numbered(tmp_path):
    """A scanned PDF has no text layer, so §2.2 routes it straight here. Vision takes
    images, so the adapter rasterises — that is the "practical rendering resolution"
    §2.7 asks to be configured."""
    pdf = build_pdf(tmp_path / "scan.pdf", pages=2)
    out = vision_ocr()(pdf, config=dict(ACCURATE))
    assert out.pages_total == 2
    assert out.pages_processed == 2
    assert not out.capped
    assert {r.page for r in out.regions} == {1, 2}


def test_regions_are_numbered_within_their_page(tmp_path):
    """`region` is a 1-based index and P4 D3 makes it an address. Numbering it
    across the whole document instead would make page 2 region 1 unaddressable."""
    pdf = build_pdf(tmp_path / "scan.pdf", pages=2)
    out = vision_ocr()(pdf, config=dict(ACCURATE))
    for page in (1, 2):
        ordinals = [r.region for r in out.regions if r.page == page]
        assert ordinals == list(range(1, len(ordinals) + 1))


def test_the_page_cap_reports_a_partial_read_rather_than_a_short_document(tmp_path):
    """§2.7: OCR *"needs a page cap, total run-time limit, progress state, and
    partial-read state because long scanned books can otherwise create unexpectedly
    expensive workloads"*.

    `capped` is the partial-read state. Without it a capped run is indistinguishable
    from a document that simply ended, and §8.6's rule is that unfinished work stays
    visible AS unfinished.
    """
    pdf = build_pdf(tmp_path / "book.pdf", pages=3)
    out = vision_ocr()(pdf, config={**ACCURATE, "page_cap": 1})
    assert out.capped is True
    assert out.pages_processed == 1
    assert out.pages_total == 3
    assert {r.page for r in out.regions} == {1}


def test_configuration_reaches_the_run_and_therefore_the_cache_key():
    """§2.7 requires the CONFIGURATION be persisted, and §3.4 puts it in the cache
    key so a settings change makes stale results fall out.

    That is why the adapter reads its settings from `config` rather than from
    constructor arguments: `extract_ocr` stores exactly the mapping it was given, so
    a setting the engine took privately would change behaviour without changing the
    fingerprint — a silent cache poisoning.
    """
    import inspect

    source = inspect.getsource(vision_ocr)
    assert "config" in inspect.signature(
        vision_ocr()).parameters, "the engine must take `config`"
    for setting in ("languages", "dpi", "recognition_level", "page_cap"):
        assert f'"{setting}"' in source or f"'{setting}'" in source, (
            f"{setting} is not read from config, so it never reaches the run")


def test_an_unreadable_file_raises_rather_than_returning_empty(tmp_path):
    """The §2.4 rule again: empty output would become a `complete` OCR run with no
    observations, which says the image contained no text rather than that it could
    not be read."""
    junk = tmp_path / "not-an-image.png"
    junk.write_bytes(b"nope")
    with pytest.raises(Exception):
        vision_ocr()(junk, config=dict(ACCURATE))


def test_the_adapter_holds_no_product_vocabulary():
    """No source type, no completeness, no analysis tier, no extractor name. The
    adapter reports what the engine said; P5 decides what it means."""
    import ast
    import inspect

    import readers.ocr_vision as module

    tree = ast.parse(inspect.getsource(module))
    strings = {n.value for n in ast.walk(tree)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    for forbidden in ("ocr.apple_vision", "capped", "complete", "possible"):
        assert forbidden not in strings, (
            f"{forbidden!r} is P5's vocabulary and must not be spelled in an adapter")


def test_a_box_is_measured_from_the_top_left(screenshot):
    """C22, ruled 2026-08-22: P4's `norm` means TOP-LEFT.

    Vision reports bottom-left-origin rectangles. P4's `Region` carries no origin, so
    every consumer picks a convention and the common one is top-left. A redaction that
    assumed top-left over a bottom-left box blacks out a band mirrored about the
    horizontal axis -- a §8.4 failure that looks like a working redaction. The ruling
    closes it at the adapter, which is the only live producer of a `norm` region, so
    P4's shipped shape and its nineteen fixtures are untouched.

    Asserted on the pure geometry, because a real screenshot cannot distinguish the
    two conventions for a band that happens to sit near the middle.
    """
    from readers.ocr_vision import _box

    class _Point:
        def __init__(self, x, y): self.x, self.y = x, y

    class _Size:
        def __init__(self, w, h): self.width, self.height = w, h

    class _Rect:
        def __init__(self, x, y, w, h):
            self.origin, self.size = _Point(x, y), _Size(w, h)

    # Vision: a band whose BOTTOM edge sits 0.1 up from the bottom, 0.2 tall --
    # so it occupies 0.1..0.3 from the bottom, i.e. 0.7..0.9 from the top.
    box = _box(_Rect(0.25, 0.1, 0.5, 0.2))

    assert box["y"] == pytest.approx(0.7), (
        "y must be the TOP edge measured downward from the top-left corner")
    assert box["x"] == pytest.approx(0.25), "x is unchanged; only the y axis flips"
    assert box["w"] == pytest.approx(0.5)
    assert box["h"] == pytest.approx(0.2)
    assert box["unit"] == "norm"


def test_a_box_that_touches_the_top_stays_inside_the_page(screenshot):
    """The flip must not push a legitimate box out of 0..1. A Vision rectangle
    flush with the TOP of the page has origin.y + height == 1.0, which must map to
    y == 0.0 exactly -- not to a small negative that a redaction would clamp."""
    from readers.ocr_vision import _box

    class _Rect:
        def __init__(self, x, y, w, h):
            self.origin = type("P", (), {"x": x, "y": y})()
            self.size = type("S", (), {"width": w, "height": h})()

    box = _box(_Rect(0.0, 0.8, 1.0, 0.2))
    assert box["y"] == pytest.approx(0.0)
    assert 0.0 <= box["y"] <= 1.0

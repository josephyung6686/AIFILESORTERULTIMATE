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


def test_the_engine_reports_whether_this_machine_can_detect_language(
        screenshot, monkeypatch):
    """`104` §18.2 gap 19's open half, which was open in a COMMENT and is now on the
    record.

    Gap 19's measurement is that the language LIST decides nothing and the
    recogniser's own language identification decides everything: on a rendered
    `会计学原理`, the whole published set with detection off reads no text at all and
    detection on reads it at confidence 1.0. An older macOS's Vision has no such flag,
    so on that machine a Chinese-titled document still comes back empty -- and came
    back empty SILENTLY, indistinguishable in the record from a blank page.

    THE MACHINE RUNNING THIS TEST HAS THE FLAG, so the arm that matters is staged
    rather than waited for: what can be asserted here is the wiring, which is the
    half that could break quietly -- an engine that stopped reporting the capability
    would take the caveat off every run without failing anything. The recognition
    itself is untouched by this and the text still comes back.
    """
    import readers.ocr_vision as adapter

    assert vision_ocr()(screenshot, config=dict(ACCURATE)).detects_language is True

    monkeypatch.setattr(adapter, "_detects_language", lambda request: False)
    older = vision_ocr()(screenshot, config=dict(ACCURATE))
    assert older.detects_language is False, (
        "a recogniser that cannot identify a language has no way to say so")


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


def test_an_unreadable_file_never_comes_back_as_an_empty_reading(tmp_path):
    """The §2.4 rule: empty output would become a `complete` OCR run with no
    observations, which says the image contained no text rather than that it could
    not be read.

    It may come back as `None` -- §2.4's OTHER outcome, "no reader exists for this
    format in this deployment" -- and the two tests below say which is which. What it
    may never be is an `OcrOutput` with no regions.
    """
    junk = tmp_path / "not-an-image.png"
    junk.write_bytes(b"nope")
    try:
        out = vision_ocr()(junk, config=dict(ACCURATE))
    except Exception:
        return
    assert out is None, (
        "an unreadable file came back as a reading. An OcrOutput with no regions "
        "becomes a `complete` run carrying nothing, which is the one outcome §2.4 "
        "rules out absolutely")


def test_a_format_the_image_stack_cannot_decode_is_no_reader_not_a_failure(tmp_path):
    """§2.4's two words, and the line between them.

    > `unsupported` -- no reader exists for this format in this deployment
    > `failed`      -- a reader RAN and raised; a fact about the bytes

    An SVG is a perfectly valid, undamaged document that ImageIO ships no decoder
    for: `CGImageSourceGetType` returns NULL because no image format was recognised
    in the bytes at all. Raising there recorded seven undamaged vector logos as
    `ocr · failed · "no image could be decoded"` -- a statement that those files are
    corrupt, which is false, in a column every later stage trusts.

    `None` is how every other reader in this deployment says "no library for this"
    (`readers/deployment.py`: *"A format with no library returns `None`, never an
    exception"*), and the OCR engine is a reader like the rest.

    NOT AN SVG SPECIAL CASE, and deliberately not: the question asked is whether the
    IMAGE STACK recognised a format, so a `.psd`, an `.ai`, an `.eps` or any future
    vector container answers it the same way without a line being added.
    """
    vector = tmp_path / "logo.svg"
    vector.write_bytes(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="62" height="32">'
        b'<title>VISA</title></svg>')
    assert vision_ocr()(vector, config=dict(ACCURATE)) is None


def test_a_damaged_file_of_a_format_it_does_decode_still_raises(tmp_path):
    """The other side of the same line, so the fix above cannot swallow real damage.

    A truncated PNG carries a PNG signature and an IHDR, so ImageIO identifies the
    format (`public.png`) and then cannot build an image from what follows. That IS
    a fact about the bytes, and it stays `failed`.
    """
    broken = tmp_path / "half.png"
    broken.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR"
                       + b"\x00" * 13)
    with pytest.raises(Exception):
        vision_ocr()(broken, config=dict(ACCURATE))


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


# --- `104` R-L: the library's own noise ------------------------------------------

_QUIET_PROBE = """
import sys
sys.path.insert(0, {src!r})
from pathlib import Path
from readers.ocr_vision import vision_ocr

path = Path({path!r})
vision_ocr()(path, config={{"languages": ["en-US"], "dpi": 200,
                           "recognition_level": "accurate"}})
sys.stderr.write("PROBE-OWN-STDERR" + chr(10))
sys.stderr.flush()
"""


def test_a_file_that_is_not_a_pdf_prints_nothing_of_core_graphics_own(tmp_path):
    """`CoreGraphics PDF has logged an error` was the first thing a person saw.

    Five copies of it stood above every report, before the plan, before the tree,
    before the count of files -- one per extraction worker. It is not this
    product's message and it is not about the person's file: the engine hands
    every OCR candidate to `CGPDFDocumentCreateWithURL` to learn whether it is a
    PDF, and Core Graphics writes that line straight to file descriptor 2 the
    first time in a process that the answer is no.

    IN A SUBPROCESS, and that is the whole test rather than an implementation
    detail: Core Graphics logs this ONCE per process, so an in-process assertion
    would pass on the second test to run whether or not anything was fixed.

    The second assertion is the one that keeps the fix honest -- the product's own
    stderr still comes through. Silencing the run's own voice to hide a library's
    would be a worse defect than the one being fixed.
    """
    import subprocess
    import sys

    not_a_pdf = tmp_path / "Econ notes week 5.txt"
    not_a_pdf.write_text("Week 5: elasticity of demand.\n")
    src = str(Path(__file__).resolve().parents[2] / "src")

    done = subprocess.run(
        [sys.executable, "-c", _QUIET_PROBE.format(src=src, path=str(not_a_pdf))],
        capture_output=True, text=True, timeout=300)

    assert done.returncode == 0, done.stderr
    assert "CoreGraphics" not in done.stderr, done.stderr
    assert "PROBE-OWN-STDERR" in done.stderr


# --- R-112's wedge, at its cause: the race for a Metal cache slot -----------------


class _RanNothing:
    """Vision, reduced to the one call the turn is taken around.

    REAL VISION IS THE WRONG INSTRUMENT HERE and that is deliberate. A real
    recognition takes two to three seconds, so "did the call happen while the turn
    was held" would be a race against the recogniser's own cost rather than an
    assertion about the lock. What is being pinned is WHEN
    `performRequests_error_` is reached, and a fake reaches it instantly -- which
    is exactly what makes the failure sharp: before the fix the call lands while
    another process holds the turn, and the test says so in milliseconds.
    """

    def __init__(self) -> None:
        self.reached = __import__("threading").Event()

    # -- the two objects `_recognise` builds --------------------------------------
    @property
    def VNImageRequestHandler(self):
        outer = self

        class Handler:
            @staticmethod
            def alloc():
                return Handler()

            def initWithCGImage_options_(self, image, options):
                return self

            def performRequests_error_(self, requests, error):
                outer.reached.set()
                return True, None

        return Handler

    @property
    def VNRecognizeTextRequest(self):
        class Request:
            @staticmethod
            def alloc():
                return Request()

            def init(self):
                return self

            def setRecognitionLevel_(self, level):
                return None

            def setRecognitionLanguages_(self, languages):
                return None

            def results(self):
                return []

        return Request


def _hold_the_turn(path):
    """Take the machine-wide turn the way another process would, and give it back."""
    import fcntl
    import os

    handle = os.open(str(path), os.O_CREAT | os.O_RDWR, 0o600)
    fcntl.flock(handle, fcntl.LOCK_EX)

    def give_it_back():
        fcntl.flock(handle, fcntl.LOCK_UN)
        os.close(handle)

    return give_it_back


def test_the_first_call_into_vision_waits_for_the_process_holding_the_turn(
        tmp_path, monkeypatch):
    """R-112's wedge is a race for a cache slot, and this is the race being refused.

    `libCoreFSCache` gives each process an exclusive numbered slot of the Metal
    shader compiler's on-disk cache and picks the number by looking for a free one.
    Two processes that look at the same instant pick the same number: one takes the
    `flock`, the other blocks inside `MTLCompilerFSCache::openSync` with no timeout
    for as long as the winner lives. Measured 11 Sep 2026 on a stalled scan: two
    workers of one pool both held `libraries10.data` open, the winner idle in
    `sem_wait` waiting for its next file and the loser wedged in `flock`, four
    minutes and counting. `ProcessPool` consumes results in submission order, so the
    whole run stopped on the loser.

    913f647 is what made it constant rather than one run in eleven: every image and
    every sparse page now goes to OCR, so all seven workers make their first Vision
    call inside the same second. Measured over the same 44-file corpus, ten runs
    without this lock stalled seven times and six runs with it stalled none.

    So the turn is taken before the first call and the SECOND process waits. The
    assertion is that it waits -- not that it is fast.
    """
    import threading

    from readers import ocr_vision

    lock = tmp_path / "vision-first-call.lock"
    monkeypatch.setattr(ocr_vision, "_metal_first_call_lock", lambda: lock,
                        raising=False)
    monkeypatch.setattr(ocr_vision, "_BEEN_THROUGH_VISION", False, raising=False)
    vision = _RanNothing()
    monkeypatch.setattr(ocr_vision, "Vision", vision)

    give_it_back = _hold_the_turn(lock)
    reader = threading.Thread(
        target=ocr_vision._recognise,
        args=(object(),), kwargs={"languages": (), "level": None}, daemon=True)
    reader.start()
    try:
        assert not vision.reached.wait(2.0), (
            "the first call into Vision ran while another process held the turn; "
            "that is the slot race a worker wedges in")
    finally:
        give_it_back()

    assert vision.reached.wait(30.0), "the reading never happened once the turn came"
    reader.join(timeout=30.0)


def test_only_the_first_call_in_a_process_takes_a_turn(tmp_path, monkeypatch):
    """And every call after it goes straight through, which is the cost of the fix.

    The slot is claimed once per process, so a lock held per FILE would serialise
    every reading in the run behind one another -- seven workers reduced to one, on
    a product whose owner has already said local reading is too slow. The flag is
    what keeps the cost to one queue at the start of a run, and a fix whose cost
    grew with the corpus would be worse than the stall it ends.
    """
    import threading

    from readers import ocr_vision

    lock = tmp_path / "vision-first-call.lock"
    monkeypatch.setattr(ocr_vision, "_metal_first_call_lock", lambda: lock,
                        raising=False)
    monkeypatch.setattr(ocr_vision, "_BEEN_THROUGH_VISION", False, raising=False)
    first = _RanNothing()
    monkeypatch.setattr(ocr_vision, "Vision", first)

    ocr_vision._recognise(object(), languages=(), level=None)
    assert first.reached.is_set()

    second = _RanNothing()
    monkeypatch.setattr(ocr_vision, "Vision", second)
    give_it_back = _hold_the_turn(lock)
    try:
        again = threading.Thread(
            target=ocr_vision._recognise,
            args=(object(),), kwargs={"languages": (), "level": None}, daemon=True)
        again.start()
        assert second.reached.wait(10.0), (
            "a later reading queued behind the turn as well, which would serialise "
            "the whole run behind one worker")
        again.join(timeout=10.0)
    finally:
        give_it_back()

# src/readers/ocr_vision.py
"""`ocr_engine` backed by Apple Vision — the engine §2.7 names.

> *"On macOS, Apple Vision should be configured explicitly with accurate recognition,
> appropriate language support including CJK where required, and a practical
> rendering resolution such as 200 DPI. OCR also needs a page cap, total run-time
> limit, progress state, and partial-read state because long scanned books can
> otherwise create unexpectedly expensive workloads."*

Vision takes images, so a paged document is rasterised first — that is what the
rendering resolution is for. Everything else in that sentence is a setting, and
**every setting is read from `config`, never from a constructor argument.** §2.7
requires the configuration be persisted and §3.4 puts it in the cache key;
`extract_ocr` stores exactly the mapping it is handed, so a setting this engine took
privately would change results without changing the fingerprint. That is a silent
cache poisoning, and it is the reason the signature looks the way it does.

**This module reports; it does not judge.** It says what the engine returned, at what
confidence, in which box. Whether that is `complete`, `possible` or worth a fact is
P5's and P6's.
"""
from __future__ import annotations

import platform
import time
from pathlib import Path
from typing import Any, Callable, Mapping

import Quartz
import Vision
from Foundation import NSURL

from extractors.ocr import OcrOutput, OcrRegion

#: §2.7's first persisted field: the provider's own name for itself. P5 folds this
#: into `extractor_name` (`ocr.apple_vision`) and spells no provider of its own.
PROVIDER = "Apple Vision"

#: PDF user-space is 72 units to the inch, so a rendering scale is dpi/72.
_POINTS_PER_INCH = 72.0

#: What Vision was asked for, mapped to its own constants. A level it does not know
#: is a caller error and is raised rather than quietly downgraded -- silently running
#: fast recognition when accurate was configured would make §2.7's first requirement
#: untrue while every record still claimed it held.
_LEVELS = {
    "accurate": Vision.VNRequestTextRecognitionLevelAccurate,
    "fast": Vision.VNRequestTextRecognitionLevelFast,
}


def _provider_version() -> str:
    """Vision publishes no framework version, so the honest answer is the OS.

    Recognition behaviour is a property of the macOS release -- the models ship with
    it -- so the OS version is the thing that actually distinguishes two runs. It is
    read from the system, never hardcoded: §2.7 wants the version persisted, and a
    constant would make every machine claim the same one.
    """
    return platform.mac_ver()[0]


class _NoDecoder(Exception):
    """The image stack recognised no image format in these bytes at all.

    A statement about THIS DEPLOYMENT -- ImageIO ships 61 decoders and none of them
    reads this -- and never about the file, which may be a perfectly valid SVG, PSD,
    EPS or anything else nobody wrote a decoder for. `ocr_engine` turns it into
    §2.4's `None`, the same answer every other reader here gives for a format it has
    no library for.
    """


def _cg_image_from_file(path: Path):
    """The first page of an image file, or a refusal that says WHICH KIND it is.

    §2.4 gives two names to two different facts, and this function is where they are
    told apart:

        `unsupported`  no reader exists for this format in this deployment
        `failed`       a reader RAN and raised -- a fact about the bytes

    `CGImageSourceGetType` is the discriminator, and it is the framework's own
    answer to exactly this question: it returns the recognised type identifier, or
    NULL when the bytes match no format ImageIO knows. Measured: an SVG and a file
    of random bytes both give NULL (with status `kCGImageStatusUnknownType`); a
    TRUNCATED PNG gives `public.png` and then fails to produce an image. So a format
    with no decoder and a damaged file of a decodable format are distinguishable
    here, and only here -- one step later they are both just a missing image.

    NOTHING BELOW NAMES A FORMAT. The question asked is whether the image stack
    recognised one, so a `.psd`, an `.ai`, an `.eps` or a vector container invented
    next year is answered without a line being added. Before this, seven undamaged
    SVG logos on the owner's disk were recorded `ocr · failed`, which says a person's
    files are corrupt when they are not.

    UNIDENTIFIABLE BYTES GO TO `unsupported` TOO, and that is the deliberate half.
    A file whose format ImageIO cannot name might be a vector document or might be
    garbage, and this seam cannot tell. Of the two words, *"this deployment has no
    reader for whatever this is"* is true either way; *"a reader ran and the bytes
    are bad"* is true only in one. The word that is true in both cases is the one
    that gets recorded.
    """
    source = Quartz.CGImageSourceCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), None)
    if source is None or Quartz.CGImageSourceGetType(source) is None:
        raise _NoDecoder(
            f"the image stack recognises no image format in {path}")
    image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
    if image is None:
        # A format it DOES decode, and could not. §2.4: never silently an empty
        # document -- the raise becomes P5's `failed` run, which here is true.
        raise ValueError(f"no image could be decoded from {path}")
    return image


def _render_pdf_page(page, dpi: float):
    box = Quartz.CGPDFPageGetBoxRect(page, Quartz.kCGPDFMediaBox)
    scale = dpi / _POINTS_PER_INCH
    width = max(int(box.size.width * scale), 1)
    height = max(int(box.size.height * scale), 1)
    context = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0,
        Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedLast)
    # A PDF page is transparent where nothing is drawn, and Vision reads dark on
    # light. Without this fill the page arrives black-on-black and recognises nothing.
    Quartz.CGContextSetRGBFillColor(context, 1, 1, 1, 1)
    Quartz.CGContextFillRect(context, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextScaleCTM(context, scale, scale)
    Quartz.CGContextDrawPDFPage(context, page)
    return Quartz.CGBitmapContextCreateImage(context)


def _recognise(image, *, languages, level) -> list[tuple[str, float, Any]]:
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, {})
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(level)
    if languages:
        request.setRecognitionLanguages_(list(languages))
    ok, error = handler.performRequests_error_([request], None)
    if not ok:
        raise RuntimeError(f"Vision failed to process the image: {error}")
    found = []
    for observation in request.results() or []:
        candidates = observation.topCandidates_(1)
        if not candidates:
            continue
        found.append((candidates[0].string(), float(observation.confidence()),
                      observation.boundingBox()))
    return found


def _box(rect) -> dict[str, Any]:
    """Vision's rectangle, in P4's region shape exactly: `x`, `y`, `w`, `h`, `unit`.

    `unit` is `norm` -- one of P4's two (`px`, `norm`) -- because Vision reports
    normalised coordinates. The adapter uses P4's key names rather than the
    library's: `width`/`height` round-tripped through `location()` unvalidated and
    only exploded much later in `parse_locator`, which reads `w` and `h`.

    **Vision's origin is BOTTOM-LEFT; P4's `norm` is TOP-LEFT, and the flip happens
    here.** P4's `Region` carries no origin key, so every consumer picks a convention
    and the common one -- all image tooling, and P7's redaction -- is top-left. A
    consumer that assumed top-left over a bottom-left box would black out a band
    mirrored about the horizontal axis: a §8.4 failure that looks like a working
    redaction. NEEDS-JOSEPH C22, ruled 2026-08-22, closes it at the adapter rather
    than in P4, because this is the only live producer of a `norm` region and P4's
    shipped shape and its nineteen fixtures then stay untouched. An extra `origin`
    key was the alternative and was rejected: `location()` would store it and
    `parse_locator` would silently drop it.

    `y` is the box's TOP edge measured downward, so a rectangle flush with the top of
    the page (`origin.y + height == 1.0`) maps to exactly `0.0`. The top edge is
    summed BEFORE the subtraction -- `1.0 - (y + h)`, not `1.0 - y - h` -- because the
    two-step form leaves that flush case at `-5.6e-17`, and a box a hair outside 0..1
    is exactly what a range check exists to catch. Clamping was the alternative and
    was rejected: it would hide a genuinely out-of-range rectangle just as quietly.
    """
    return {"x": float(rect.origin.x),
            "y": 1.0 - (float(rect.origin.y) + float(rect.size.height)),
            "w": float(rect.size.width), "h": float(rect.size.height),
            "unit": "norm"}


def vision_ocr() -> Callable[..., OcrOutput]:
    """Build the `ocr_engine` callable `extractors.dispatch.Readers` takes."""

    def ocr_engine(path: Path,
                   config: Mapping[str, Any] | None = None) -> OcrOutput | None:
        settings = dict(config or {})
        languages = settings.get("languages") or ["en-US"]
        dpi = float(settings.get("dpi") or 200)
        level_name = settings.get("recognition_level") or "accurate"
        if level_name not in _LEVELS:
            raise ValueError(
                f"{level_name!r} is not a Vision recognition level; "
                f"choose one of {sorted(_LEVELS)}")
        level = _LEVELS[level_name]
        page_cap = settings.get("page_cap")
        time_limit = settings.get("time_limit_seconds")

        path = Path(path)
        document = Quartz.CGPDFDocumentCreateWithURL(
            NSURL.fileURLWithPath_(str(path)))
        total = (Quartz.CGPDFDocumentGetNumberOfPages(document)
                 if document is not None else 0)

        regions: list[OcrRegion] = []

        if total == 0:
            # A loose image: one image reference, no page. §2.7's "page or image
            # reference" is one field with two cases, and reporting page 1 here
            # would make a screenshot indistinguishable from a one-page scan.
            try:
                image = _cg_image_from_file(path)
            except _NoDecoder:
                # §2.4's `unsupported`, in the shape `readers/deployment.py` sets
                # for every reader in this deployment: *"A format with no library
                # returns `None`, never an exception."* The OCR engine is a reader
                # like the rest. `extract_ocr` reads this the way `extract_pdf`
                # reads a `None` document.
                return None
            for index, (text, confidence, rect) in enumerate(
                    _recognise(image, languages=languages, level=level), 1):
                regions.append(OcrRegion(page=None, region=index, text=text,
                                         box=_box(rect), confidence=confidence))
            return OcrOutput(provider=PROVIDER, provider_version=_provider_version(),
                             regions=tuple(regions), pages_processed=1, pages_total=1,
                             capped=False)

        started = time.monotonic()
        processed = 0
        stopped_early = False
        for number in range(1, total + 1):
            if page_cap is not None and processed >= page_cap:
                stopped_early = True
                break
            if time_limit is not None and time.monotonic() - started >= time_limit:
                stopped_early = True
                break
            page = Quartz.CGPDFDocumentGetPage(document, number)
            if page is None:
                continue
            for index, (text, confidence, rect) in enumerate(
                    _recognise(_render_pdf_page(page, dpi),
                               languages=languages, level=level), 1):
                # `region` is numbered WITHIN its page: P4 D3 makes it an address,
                # and a document-wide counter would leave page 2's first region
                # unaddressable as "page 2, region 1".
                regions.append(OcrRegion(page=number, region=index, text=text,
                                         box=_box(rect), confidence=confidence))
            processed += 1

        return OcrOutput(
            provider=PROVIDER, provider_version=_provider_version(),
            regions=tuple(regions), pages_processed=processed, pages_total=total,
            # §2.7's partial-read state. True only when a limit stopped the run --
            # a document that simply ended is not a partial read, and §8.6 needs the
            # two distinguishable so unfinished work stays visible as unfinished.
            capped=stopped_early)

    return ocr_engine

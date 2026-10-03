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

import contextlib
import fcntl
import os
import platform
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.ocr import OcrOutput, OcrRegion, pages_within_cap

#: Bound by `_apple` on the first call. The module itself must import on Linux:
#: these frameworks exist only on macOS, and importing them at module scope made
#: `import readers.ocr_vision` — and therefore every scan — refuse before a text
#: file was opened.
Quartz = None
Vision = None
NSURL = None

#: §2.7's first persisted field: the provider's own name for itself. P5 folds this
#: into `extractor_name` (`ocr.apple_vision`) and spells no provider of its own.
PROVIDER = "Apple Vision"

#: PDF user-space is 72 units to the inch, so a rendering scale is dpi/72.
_POINTS_PER_INCH = 72.0

#: What Vision was asked for, mapped to its own constants. A level it does not know
#: is a caller error and is raised rather than quietly downgraded -- silently running
#: fast recognition when accurate was configured would make §2.7's first requirement
#: untrue while every record still claimed it held.
_LEVELS = None


def _apple() -> None:
    """Load Vision, Quartz and Foundation, or name the missing module.

    On macOS a missing wheel raises `ModuleNotFoundError` from the import
    itself, which is the name a person can act on. On any other platform the
    same error is raised here, before the import, because the wheels cannot be
    installed and a scan of ordinary documents must not depend on them. Nothing
    catches that error inside this module.
    """
    global Quartz, Vision, NSURL, _LEVELS
    if _LEVELS is not None:
        return
    if sys.platform != "darwin":
        raise ModuleNotFoundError("No module named 'Quartz'")
    import Quartz as _Quartz
    import Vision as _Vision
    from Foundation import NSURL as _NSURL

    Quartz = _Quartz
    Vision = _Vision
    NSURL = _NSURL
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


@contextlib.contextmanager
def _core_graphics_kept_quiet():
    """File descriptor 2, redirected around the one call that makes Quartz talk.

    `104` R-L. `CoreGraphics PDF has logged an error. Set environment variable
    "CG_PDF_VERBOSE" to learn more.` stood above every report a person saw, five
    times -- once per extraction worker. Measured to a single cause: this engine
    asks `CGPDFDocumentCreateWithURL` whether a file is a PDF, and Core Graphics
    writes that line straight to fd 2 the first time in a process that the answer
    is no. Two of the corpus's OCR candidates are a `.txt` and a `.png`.

    **At the descriptor and not at `sys.stderr`.** The write comes from C inside
    Apple's framework and never passes through Python's stream, so
    `contextlib.redirect_stderr` cannot see it. There is no switch to turn it off:
    `CG_PDF_VERBOSE` makes it say MORE, and Apple publishes no counterpart.

    **Around the ONE call, and nothing else.** The window is a single C function
    that writes nothing of ours; the reader's own raises, this product's messages
    and pytest's output are all outside it. Silencing the run's own voice to hide
    a library's would be a worse defect than the one this fixes -- which is why
    the test asserts the product's stderr still arrives.

    **The one thing to know before reusing this.** A descriptor is process-wide,
    so anything else writing to fd 2 during the window loses that write. The
    window is one C call, and the only thread `src/` starts beside extraction is
    `extraction_pool`'s parent watchdog, which writes nothing -- but that is a
    fact about today's code rather than a guarantee, and widening the window is
    how it would stop being true. Restored in `finally` whatever happens,
    including an interrupt.
    """
    sys.stderr.flush()
    saved = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved, 2)
        os.close(saved)
        os.close(devnull)


def _pdf_document(path: Path):
    """The PDF at `path`, or `None` -- and Core Graphics keeps its opinion to itself.

    This IS the format test: a `None` here is how `ocr_engine` learns the file is a
    loose image rather than a document, so the call is made for every OCR candidate
    and the honest answer for most of them is the one that prints the line.
    """
    with _core_graphics_kept_quiet():
        return Quartz.CGPDFDocumentCreateWithURL(NSURL.fileURLWithPath_(str(path)))


def fitted_pixel_size(width: int, height: int,
                      long_edge: int | None) -> tuple[int, int, bool]:
    """The size to recognise, and whether that is smaller than the source.

    `long_edge` is the caller's. None leaves the image alone. A source whose
    longer side is already within the edge is unchanged. The shorter side keeps
    the source's aspect.
    """
    if not long_edge or width <= 0 or height <= 0:
        return width, height, False
    longest = width if width >= height else height
    if longest <= long_edge:
        return width, height, False
    # Integer arithmetic: a float scale drops a pixel (4032×3024 at 2200
    # became 2200×1649). The shorter side stays the source's aspect.
    return (max((width * long_edge) // longest, 1),
            max((height * long_edge) // longest, 1),
            True)


def _scaled_cg_image(image, long_edge):
    """The image Vision should see, shrunk when its long edge exceeds `long_edge`."""
    width = int(image.width())
    height = int(image.height())
    new_w, new_h, scaled = fitted_pixel_size(width, height, long_edge)
    if not scaled:
        return image, False
    context = Quartz.CGBitmapContextCreate(
        None, new_w, new_h, 8, 0,
        Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextDrawImage(
        context, Quartz.CGRectMake(0, 0, new_w, new_h), image)
    return Quartz.CGBitmapContextCreateImage(context), True


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


def recognition_languages(*, recognition_level: str) -> tuple[str, ...]:
    """The languages THIS recogniser publishes for that level. Never a typed list.

    `_apple` runs first so a caller on a platform without Vision hears the
    missing module by name, and so `_LEVELS` exists before it is read.

    `104` §18.2 gap 19. §2.7 asks for "appropriate language support INCLUDING CJK
    WHERE REQUIRED" and this deployment asked for `en-US` and nothing else, so the
    owner's Chinese-titled documents came back empty or garbled -- measured again
    here on a rendered `会计学原理`, which `en-US` recognises as no text at all.

    The fix is not a longer list. A list is a guess about a corpus, and the machine
    already knows the answer: `supportedRecognitionLanguagesAndReturnError_` is
    Vision's own published set, versioned with the OS the way `_provider_version`
    above says recognition itself is. It is asked of a request AT THE LEVEL that
    will run, because Apple documents the set as a property of the revision and the
    recognition level -- asking at one level and recognising at another would record
    a set that was never offered.

    `recognition_level` has NO DEFAULT: the level is `config`'s (§2.7 persists it,
    §3.4 keys the cache on it) and a default here would be a second, unreviewed
    setting quietly deciding what the first one asked about.
    """
    _apple()
    if recognition_level not in _LEVELS:
        raise ValueError(
            f"{recognition_level!r} is not a Vision recognition level; "
            f"choose one of {sorted(_LEVELS)}")
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(_LEVELS[recognition_level])
    published, error = request.supportedRecognitionLanguagesAndReturnError_(None)
    if published is None:
        raise RuntimeError(
            f"Vision published no recognition languages for {recognition_level!r}: "
            f"{error}")
    return tuple(str(language) for language in published)


def _detects_language(request) -> bool:
    """Whether THIS machine's recogniser can identify a language at all.

    `104` §18.2 gap 19 left exactly one thing open and said so: the automatic
    detection that makes CJK readable is a flag an older macOS's Vision does not
    have, and on such a machine the fix silently does nothing -- the published set is
    still asked for and still handed over, and a Chinese-titled document still comes
    back as no text at all. One question, asked in one place, so `_recognise` (which
    must ask it of the request it is about to run) and the engine below (which must
    report it on the run) cannot drift into disagreeing about the same machine.

    Asked of a REQUEST rather than of the class: the selector is an instance method,
    and a capability answered off the class object would be a guess about PyObjC's
    bridging rather than a statement about the object that will actually recognise.
    """
    return hasattr(request, "setAutomaticallyDetectsLanguage_")


#: WHETHER THIS PROCESS HAS ALREADY BEEN THROUGH VISION ONCE.
#:
#: The first call is the one that opens the Metal shader compiler's on-disk cache;
#: every call after it reuses the slot this process already holds. So the lock below
#: is taken once per process and never again -- a run of 5,760 files pays for it
#: once, on the file that happens to be first.
_BEEN_THROUGH_VISION = False



def _metal_first_call_lock() -> Path:
    """Where the turn is taken: one file, per user, for every run at once.

    The lock has to have the same reach as the thing it protects, and no more. The
    Metal cache is `/var/folders/<user>/C/org.python.python/com.apple.metal/`, which
    every Python process this user runs shares -- two concurrent scans collide with
    each other exactly as two workers of one scan do -- so a lock beside the database
    or inside the run's own directory would be too narrow.

    `tempfile.gettempdir()` is `/var/folders/<user>/T` on this platform: the cache
    directory's own sibling, under the same per-user folder, so it has precisely that
    reach. `os.confstr` was the first draft and it does not work -- CPython publishes
    no `CS_DARWIN_USER_CACHE_DIR` name and raises `ValueError` for it (executed) --
    which would have left this quietly on the fallback while the comment claimed
    otherwise.
    """
    return Path(tempfile.gettempdir()) / "graph-agent-vision-first-call.lock"


@contextlib.contextmanager
def _one_process_at_a_time_into_metal():
    """One process at a time makes its FIRST Vision call. R-112's wedge, at the cause.

    **THE WEDGE IS A RACE FOR A CACHE SLOT, and this is the whole of the fix.**
    `extraction_pool`'s R-50 note records a worker's main thread inside
    `-[VNImageRequestHandler performRequests:]` -> `-[CIContext render:toCVPixelBuffer:]`
    -> `CI::ProgramNode::mainProgram` -> `__DISPATCH_WAIT_FOR_QUEUE__`, with
    `CI::KernelCompileQueue` blocked in `flock()` inside `MTLCompilerFSCache::openSync`,
    and answered it with a ceiling and a retry because the cause was not known.

    It is known now. `libCoreFSCache` gives each process an exclusive numbered slot
    of that cache -- `libraries10.data`, `functions10.data` -- and CHOOSES the number
    by looking for one nobody holds. Two processes that look at the same instant
    choose the same number, one takes the exclusive `flock` and the other blocks in
    it, with no timeout, for as long as the winner lives. Measured 11 Sep 2026 while
    a scan was stalled: workers 28855 and 28861 both had `libraries10.data` open,
    28855 idle in `sem_wait` holding it, 28861 wedged in `flock` waiting for it, four
    minutes and counting. The winner had gone back to waiting for its next file, and
    a `ProcessPool` consumes results in submission order, so the run stopped.

    **WHAT MADE IT CONSTANT WAS 913f647, WHICH READS EVERY IMAGE.** The wedge was
    measured at one run in eleven when OCR ran on a handful of files. Once every
    image and every sparse page goes to OCR, all seven workers make their first
    Vision call within the same second of the pool starting, which is precisely the
    condition the slot race needs. Measured over a 44-file synthetic corpus: ten
    runs without this lock stalled seven times, and seven runs with it stalled
    none.

    So the turns are taken one at a time. A process that has already been through
    holds its own slot and never looks again, so this costs one queue at the start
    of a run and nothing afterwards.

    **AND THE WAIT CARRIES NO NUMBER.** A first draft bounded it at sixty seconds
    "so a holder that never returns cannot become a second way to hang". It cannot:
    `flock` is released by the kernel the moment its holder dies, and a holder that
    wedges inside its own first call is killed by `extraction_pool`'s ceiling
    (`cli.EXTRACTION_SECONDS_PER_FILE`), which is the one bound this product puts
    on an extraction. A second number here would be a guess about the first one.
    """
    global _BEEN_THROUGH_VISION
    if _BEEN_THROUGH_VISION:
        yield
        return
    try:
        handle = os.open(str(_metal_first_call_lock()),
                         os.O_CREAT | os.O_RDWR, 0o600)
    except OSError:                                 # pragma: no cover -- unwritable
        handle = None
    if handle is not None:
        fcntl.flock(handle, fcntl.LOCK_EX)
    try:
        yield
    finally:
        # SET WHATEVER HAPPENED. A first call that raised still opened the cache,
        # and a process that queued again on every failure would serialise a whole
        # run's worth of unreadable files behind one lock.
        _BEEN_THROUGH_VISION = True
        if handle is not None:
            try:
                fcntl.flock(handle, fcntl.LOCK_UN)
            finally:
                os.close(handle)


def _recognise(image, *, languages, level) -> list[tuple[str, float, Any]]:
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(image, {})
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(level)
    # §2.7's "including CJK where required", and WHERE REQUIRED is decided per FILE
    # by the recogniser rather than per deployment by a list. Apple offers language
    # identification on the request itself, so the file's own text chooses the model
    # and `recognitionLanguages` below stays what it is -- the recogniser's own
    # published set, from `recognition_languages`, never a set this product typed.
    #
    # MEASURED, because the two are not interchangeable and the docs do not say so:
    # on a rendered `会计学原理`, `recognitionLanguages` set to the whole published
    # set and no automatic detection recognises NOTHING, while automatic detection
    # recognises it at confidence 1.0 with or without the list. So the detection
    # flag is the load-bearing line and the list is the prior beside it.
    if _detects_language(request):
        request.setAutomaticallyDetectsLanguage_(True)
    if languages:
        request.setRecognitionLanguages_(list(languages))
    with _one_process_at_a_time_into_metal():
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
        _apple()
        settings = dict(config or {})
        dpi = float(settings.get("dpi") or 200)
        level_name = settings.get("recognition_level") or "accurate"
        if level_name not in _LEVELS:
            raise ValueError(
                f"{level_name!r} is not a Vision recognition level; "
                f"choose one of {sorted(_LEVELS)}")
        level = _LEVELS[level_name]
        # WAS `settings.get("languages") or ["en-US"]`, and that fallback is `104`
        # §18.2 gap 19 in one line: a caller who configured nothing got English, and
        # every non-English file in the corpus was read as though it held no text.
        # The recogniser's own published set is the answer to "which languages does
        # this deployment have", so a config that names none asks IT, never a
        # constant. The set still reaches the run's `config` (§2.7's third persisted
        # field) because `readers/deployment.py` puts it there before the call.
        languages = settings.get("languages") or recognition_languages(
            recognition_level=level_name)
        # `104` §18.2 gap 19's open half, now REPORTED instead of left in a comment.
        # Asked once, of a request built the way the ones below are built, so the run
        # records the capability the recognition actually had. `extract_ocr` writes
        # it onto the run only when it is False, and its comment says why.
        detects_language = _detects_language(
            Vision.VNRecognizeTextRequest.alloc().init())
        page_cap = settings.get("page_cap")
        time_limit = settings.get("time_limit_seconds")
        long_edge = settings.get("max_long_edge_px")

        path = Path(path)
        document = _pdf_document(path)
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
            image, scaled = _scaled_cg_image(image, long_edge)
            started = time.monotonic()
            for index, (text, confidence, rect) in enumerate(
                    _recognise(image, languages=languages, level=level), 1):
                regions.append(OcrRegion(page=None, region=index, text=text,
                                         box=_box(rect), confidence=confidence))
            elapsed = time.monotonic() - started
            # A loose image is one Vision call, so the time limit cannot stop it
            # mid-recognition. Crossing it is still recorded as a partial read.
            over_time = time_limit is not None and elapsed >= time_limit
            return OcrOutput(provider=PROVIDER, provider_version=_provider_version(),
                             regions=tuple(regions), pages_processed=1, pages_total=1,
                             capped=over_time, detects_language=detects_language,
                             scaled=scaled)

        started = time.monotonic()
        processed = 0
        scaled_any = False
        # `pages`: the subset the policy asked for (`ocr_policy.sparse_pages`), or
        # every page. A number outside the document is skipped, not an error.
        # `pages_within_cap` is the classification page cap. It holds no number;
        # the cap arrives on `config`.
        wanted = settings.get("pages")
        numbers = ([n for n in wanted if 1 <= n <= total] if wanted
                   else range(1, total + 1))
        chosen, page_capped = pages_within_cap(numbers, page_cap)
        stopped_early = page_capped
        for number in chosen:
            if time_limit is not None and time.monotonic() - started >= time_limit:
                stopped_early = True
                break
            page = Quartz.CGPDFDocumentGetPage(document, number)
            if page is None:
                continue
            rendered, scaled_page = _scaled_cg_image(
                _render_pdf_page(page, dpi), long_edge)
            scaled_any = scaled_any or scaled_page
            for index, (text, confidence, rect) in enumerate(
                    _recognise(rendered,
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
            capped=stopped_early, detects_language=detects_language,
            scaled=scaled_any)

    return ocr_engine

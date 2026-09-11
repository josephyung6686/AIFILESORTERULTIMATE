# tests/readers/test_readers_image_headers.py
"""The reader that made `filename_pattern` and `dimension_signal` reachable at all.

`read_image` was `_no_reader`, so `extract_image` returned `unsupported` on its second
line -- before `filename_pattern` was called and before `dimension_signal` was called.
Every image in a real corpus produced ZERO observations, and the two catalogue-fed
arguments P5 declares as required keywords were, in the shipped deployment, dead code
behind a missing library. Wiring the catalogues without wiring a reader would have
left them exactly as unreachable as they were in `planning/`.

This reader reads the container header for the format token and the pixel dimensions,
which are what catalogues 02, 03 and 04 need, **and it reads §2.6's metadata slots
through the image stack this deployment already ships** (`104` §18.2 gap 18). The
sentence that stood here said "**It does not read EXIF**, so §2.6's tier-1 band
('camera EXIF is strong photo evidence') and the capture-time and GPS halves of tier 2
stay unavailable in this deployment", which made `00`:32's promise -- a photograph
"stated by its capture metadata" -- unavailable everywhere in the product.

§2.6's own trap 1 still holds and is still the reason nothing is written about an
absence: "the system must not mistake the absence of EXIF for proof that an image is a
screenshot." A stripped photograph and a BMP, whose container has nowhere to put EXIF
at all, both yield no tags and no row saying so.

A format the reader does not know returns `None`, which §2.4 calls `unsupported`: the
bytes were never looked at. It is never `failed`, which means a reader ran and raised.
"""
from __future__ import annotations

import struct
import zlib

import pytest

from extractors.image import ImageRecord, SIGNAL_TIER
from readers.image_headers import (
    CAMERA_EXIF, CAPTURE_TIME, GPS, header_image_reader,
)
from readers.perceptual_hash import (
    HASH_ALGORITHM, NEAR_DUPLICATE_HASH_BITS, NEAR_DUPLICATE_MAX_DISTANCE,
    distance, near_block_keys, near_duplicate,
)

Quartz = pytest.importorskip(
    "Quartz",
    reason="ImageIO is this deployment's image-metadata library (pyproject's "
           "`readers` extra, macOS only); without it §2.6's slots are unreadable "
           "here and the pins below would pass by measuring nothing")
NSURL = pytest.importorskip("Foundation").NSURL


def png(path, width, height):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload)))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IEND", b""))
    return path


def jpeg(path, width, height):
    path.write_bytes(
        b"\xff\xd8"
        + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\xff\xc0" + struct.pack(">H", 11) + b"\x08"
        + struct.pack(">HH", height, width) + b"\x01\x01\x11\x00"
        + b"\xff\xd9")
    return path


def gif(path, width, height):
    path.write_bytes(b"GIF89a" + struct.pack("<HH", width, height)
                     + b"\x00\x00\x00" + b";")
    return path


@pytest.mark.parametrize("make,token", [(png, "PNG"), (jpeg, "JPEG"), (gif, "GIF")])
def test_the_header_gives_the_format_and_the_pixel_dimensions(tmp_path, make, token):
    read = header_image_reader()
    record = read(make(tmp_path / f"capture.{token.lower()}", 2560, 1600))
    assert isinstance(record, ImageRecord)
    assert record.image_format == token
    assert (record.width, record.height) == (2560, 1600)
    assert record.dimensions == "2560x1600"


def test_the_format_token_is_what_section_2_6_compares_png_against(tmp_path):
    """§2.6 names "PNG format" as a tier-3 signal and `extract_image` folds case on
    one word. A reader that answered `image/png` would silently stop that signal."""
    from extractors.image import PNG_FORMAT
    read = header_image_reader()
    record = read(png(tmp_path / "shot.png", 100, 100))
    assert record.image_format.strip().upper() == PNG_FORMAT


def test_a_format_this_reader_does_not_know_is_unsupported_not_failed(tmp_path):
    """§2.4's two outcomes are different answers to the user: "this product cannot
    open this kind of file" and "this file is damaged". Bytes that announce an ISO
    brand and then hold no image must give the first -- the brand is read, the image
    stack finds nothing to size, and the answer is `None` rather than a `0x0` record
    or a raise."""
    path = tmp_path / "scan.heic"
    path.write_bytes(b"\x00\x00\x00\x18ftypheic not really an image")
    assert header_image_reader()(path) is None


def test_bytes_that_claim_a_format_and_are_truncated_are_unsupported(tmp_path):
    """A truncated header is not a dimension of zero. Returning `ImageRecord(width=0)`
    would hand `dimension_signal` a pair it must then have an opinion about, and
    would put an invented value in `raw_value`."""
    path = tmp_path / "half.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    assert header_image_reader()(path) is None


def test_a_photograph_with_no_exif_carries_no_tag_saying_so(tmp_path):
    """§2.6's trap 1: "the system must not mistake the absence of EXIF for proof that
    an image is a screenshot." The SPEC's `whatsapp-stripped-exif.jpg` is this case,
    and the record states it by carrying no tags -- never by carrying a tag whose
    value is "absent", which P4 forbids outright ("the run record already says it,
    and an absence written as evidence is a value P6 can rank")."""
    record = header_image_reader()(jpeg(tmp_path / "photo.jpg", 4032, 3024))
    assert record.exif == ()
    assert record.software == {}
    assert record.perceptual_hash is None
    # And the run is NOT marked short of anything: the metadata route ran on this
    # file and found nothing, which is a different fact from never having run.
    assert record.unread_reason is None


# --------------------------------------------------------------------------- #
# SVG -- the one design/creative format the router sends here
# --------------------------------------------------------------------------- #

read = header_image_reader()


def svg(path, attributes: str, *, prologue: str = ""):
    path.write_bytes(f'{prologue}<svg xmlns="http://www.w3.org/2000/svg" '
                     f'{attributes}><rect/></svg>'.encode())
    return path


def test_an_svg_yields_its_canvas_size(tmp_path):
    """The router sends `.svg` here -- P5's SPEC routing table reads "E5
    (raster/SVG)" -- and this reader had no branch for it, so every SVG on the disk
    recorded `unsupported` and then had OCR run at it. §2.9's design-and-creative
    bullet asks for "dimensions or canvas properties" and an SVG carries both on its
    root element."""
    record = read(svg(tmp_path / "logo.svg", 'width="240" height="120"'))

    assert record == ImageRecord(image_format="SVG", dimensions="240x120",
                                 width=240, height=120,
                                 unread_reason=record.unread_reason)
    assert (record.image_format, record.width, record.height) == ("SVG", 240, 120)


@pytest.mark.parametrize("attributes", [
    'width="240px" height="120px"',            # CSS pixels, the customary spelling
    'width="240.0" height="120.0"',            # a number an editor rounded
    'width = "240"  height =\n"120"',          # XML permits space around the equals
    "width='240' height='120'",                # and either quote
])
def test_the_customary_spellings_of_a_pixel_size_are_all_read(tmp_path, attributes):
    record = read(svg(tmp_path / "logo.svg", attributes))
    assert (record.width, record.height) == (240, 120)


def test_a_percentage_size_falls_back_to_the_viewbox(tmp_path):
    """`width="100%"` is not a number of pixels -- it is a fraction of whatever
    contains the picture, which this reader cannot see. The `viewBox` is the canvas
    the design's own word names, so it answers instead."""
    record = read(svg(tmp_path / "icon.svg",
                      'width="100%" height="100%" viewBox="0 0 24 24"'))

    assert (record.width, record.height) == (24, 24)


def test_a_viewbox_only_svg_is_read(tmp_path):
    record = read(svg(tmp_path / "icon.svg", 'viewBox="0 0 16 16"'))
    assert (record.width, record.height) == (16, 16)


def test_an_svg_with_no_size_anywhere_is_unsupported_and_never_a_zero(tmp_path):
    """§2.4 again: nothing is invented. An SVG that states no size has none to
    report, and `0x0` would be a number nothing measured."""
    assert read(svg(tmp_path / "sizeless.svg", 'fill="red"')) is None


def test_an_xml_declaration_and_a_doctype_before_the_root_are_skipped(tmp_path):
    """Every SVG an editor writes begins with a declaration, a comment or both. A
    reader that only recognised a file starting `<svg` would answer `unsupported`
    for the ordinary case and `SVG` for the hand-written one."""
    prologue = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!-- Generator: some editor -->\n'
                '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "x.dtd">\n')
    record = read(svg(tmp_path / "export.svg", 'width="64" height="64"',
                      prologue=prologue))

    assert (record.image_format, record.width, record.height) == ("SVG", 64, 64)


def test_xml_that_is_not_an_svg_is_not_claimed(tmp_path):
    """An `.xml`, a `.plist` and an Illustrator file all begin with angle brackets.
    Only a document whose ROOT element is `svg` is one."""
    path = tmp_path / "settings.svg"
    path.write_bytes(b'<?xml version="1.0"?><plist width="10" height="10"/>')
    assert read(path) is None


def test_the_svg_branch_reads_no_exif_and_no_entity(tmp_path):
    """No XML parser is built here at all. The root element's own attributes are
    read out of the head of the file, so an entity declaration is bytes this reader
    walks past rather than something a parser expands."""
    path = tmp_path / "bomb.svg"
    path.write_bytes(b'<?xml version="1.0"?>'
                     b'<!DOCTYPE svg [<!ENTITY a "aaaaaaaaaa">]>'
                     b'<svg width="8" height="8">&a;</svg>')

    record = read(path)

    assert (record.width, record.height) == (8, 8)
    assert record.exif == () and record.software == {}


# --------------------------------------------------------------------------- #
# §2.6's metadata slots -- `104` §18.2 gap 18
#
# "For every supported image, the engine should store its format, pixel dimensions,
# ... EXIF camera make and model, lens data, ISO, focal length, capture time, GPS,
# orientation, software metadata, filename pattern, and OCR output where needed."
# (`00`:32.) None of it was available: the extractor was complete and the reader
# handed it a record with `exif=()`, `color={}` and `software={}` on every image.
#
# The fixtures are WRITTEN BY THE TEST through the same library the reader reads
# with, so no binary sample is checked in and the tags asserted below are the tags
# this file declared. What is measured is the round trip: the slots a person's camera
# writes come back out as `ExifValue`s carrying §2.6's own signal names.
# --------------------------------------------------------------------------- #

#: What a photograph carries, in ImageIO's own key names. Not a table of this test's:
#: every key is a `Quartz.kCGImageProperty*` constant, which is the external
#: vocabulary `ExifValue`'s docstring says the reader classifies against.
DECLARED = {
    Quartz.kCGImagePropertyTIFFDictionary: {
        Quartz.kCGImagePropertyTIFFMake: "Apple",
        Quartz.kCGImagePropertyTIFFModel: "iPhone 15 Pro",
        Quartz.kCGImagePropertyTIFFSoftware: "iOS 19.1",
    },
    Quartz.kCGImagePropertyExifDictionary: {
        Quartz.kCGImagePropertyExifDateTimeOriginal: "2026:07:17 14:03:22",
        Quartz.kCGImagePropertyExifLensModel: "iPhone 15 Pro back camera",
        Quartz.kCGImagePropertyExifISOSpeedRatings: [400],
        Quartz.kCGImagePropertyExifFocalLength: 6.86,
    },
    Quartz.kCGImagePropertyGPSDictionary: {
        Quartz.kCGImagePropertyGPSLatitude: 38.6488,
        Quartz.kCGImagePropertyGPSLatitudeRef: "N",
    },
}

#: The formats gap 18 names, at the type identifier ImageIO writes each with. HEIF
#: and AVIF are absent because this ImageIO writes neither -- see the docstring of
#: `test_every_format_gap_18_names_is_read`.
WRITABLE = {"JPEG": ("public.jpeg", "photo.jpg"),
            "PNG": ("public.png", "capture.png"),
            "HEIC": ("public.heic", "IMG_4821.heic"),
            "TIFF": ("public.tiff", "scan.tiff"),
            "BMP": ("com.microsoft.bmp", "old.bmp")}


def blank_image(width, height):
    context = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(context, 1, 1, 1, 1)
    Quartz.CGContextFillRect(context, Quartz.CGRectMake(0, 0, width, height))
    return Quartz.CGBitmapContextCreateImage(context)


def written(tmp_path, uti, name, properties=None, width=4032, height=3024):
    path = tmp_path / name
    destination = Quartz.CGImageDestinationCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), uti, 1, None)
    assert destination is not None, f"this ImageIO cannot write {uti}"
    Quartz.CGImageDestinationAddImage(destination, blank_image(width, height),
                                      properties)
    assert Quartz.CGImageDestinationFinalize(destination), uti
    return path


def by_name(record):
    return {tag.name: tag for tag in record.exif}


@pytest.mark.parametrize("token", sorted(WRITABLE))
def test_every_format_gap_18_names_is_read(tmp_path, token):
    """§2.6 requires HEIC by name -- "failing to configure the image stack for HEIC
    can silently exclude a meaningful portion of an Apple-centric corpus" -- and
    §18.2 gap 18 counts HEIC, HEIF, AVIF, TIFF and BMP as routed to a reader with no
    branch for them, so every one fell through to OCR. Each is read here for its
    format token and its pixel dimensions.

    HEIF and AVIF are not in this list because this ImageIO writes neither
    (`CGImageDestinationCopyTypeIdentifiers` publishes `public.heic` and no AVIF
    identifier), so no fixture for them can be built without checking a binary in.
    They share HEIC's branch exactly -- one call to `format_from_magic`, whose
    `_BRANDS` maps all three -- and `test_the_three_iso_brands_share_one_branch`
    below pins that the branch answers for all three tokens.
    """
    uti, name = WRITABLE[token]
    record = header_image_reader()(
        written(tmp_path, uti, name, DECLARED, width=4032, height=3024))

    assert record is not None, f"{token} still reads as nothing"
    assert record.image_format == token
    assert (record.width, record.height) == (4032, 3024)
    assert record.dimensions == "4032x3024"


def test_a_photographs_capture_metadata_comes_back_with_section_2_6s_tiers(tmp_path):
    """`00`:32's own promise, and the one site G quotes: a photograph is "stated by
    its capture metadata". Camera EXIF is §2.6's tier-1 band, capture time and GPS its
    tier-2 reinforcement, software metadata its tier-3 screenshot signal -- and the
    READER assigns each, because `ExifValue.kind` is where §2.6's tier is decided by
    the reader ("WHICH TAG IS WHICH is library knowledge")."""
    record = header_image_reader()(
        written(tmp_path, *WRITABLE["HEIC"], DECLARED))
    tags = by_name(record)

    assert tags["Make"].value == "Apple" and tags["Make"].kind == CAMERA_EXIF
    assert tags["Model"].value == "iPhone 15 Pro"
    assert tags["Model"].kind == CAMERA_EXIF
    assert tags["LensModel"].value == "iPhone 15 Pro back camera"
    assert tags["LensModel"].kind == CAMERA_EXIF
    assert tags["DateTimeOriginal"].value == "2026:07:17 14:03:22"
    assert tags["DateTimeOriginal"].kind == CAPTURE_TIME
    assert tags["Latitude"].value == "38.6488" and tags["Latitude"].kind == GPS
    assert tags["LatitudeRef"].kind == GPS
    # §2.6 lists orientation and ranks it nowhere -- `ExifValue`'s own example of a
    # tag that carries `kind=None` and therefore no tier.
    assert tags["Orientation"].kind is None
    # Software is not an EXIF tag and does not ride in `exif`: it is §2.6's tier-3
    # slot and `extract_image` tiers `software` itself.
    assert record.software == {"Software": "iOS 19.1"}
    assert "Software" not in tags


def test_one_tag_name_is_one_row_so_a_citation_addresses_one_thing(tmp_path):
    """`Orientation` is published twice on a HEIC -- at the top level and inside
    `{TIFF}` -- and `extract_image` addresses every metadata row by its tag name,
    which is the address a model cites with `metadata_field_name`. Two rows at one
    address is an ambiguous citation."""
    record = header_image_reader()(written(tmp_path, *WRITABLE["HEIC"], DECLARED))
    names = [tag.name for tag in record.exif]
    assert len(names) == len(set(names)), names


def test_a_screenshots_encoder_written_exif_is_not_strong_photo_evidence(tmp_path):
    """§2.6's hierarchy is FIVE NOUNS at tier 1 -- "EXIF camera make and model, lens
    data, ISO, focal length" -- and not "anything in the `{Exif}` dictionary".

    A macOS screenshot is a PNG whose `{Exif}` holds `PixelXDimension`,
    `PixelYDimension` and `UserComment`: tags every encoder writes and no camera is
    needed for. Ranking those tier 1 would put "camera EXIF is strong photo evidence"
    beside "PNG format ... may support a screenshot hypothesis" on every screenshot
    in the corpus, and §2.6's answer to conflicting signals is abstention -- so the
    `photos.screenshot-captures` situation would never fire for the file it names."""
    screenshot = written(tmp_path, *WRITABLE["PNG"], {
        Quartz.kCGImagePropertyExifDictionary: {
            Quartz.kCGImagePropertyExifPixelXDimension: 2880,
            Quartz.kCGImagePropertyExifPixelYDimension: 1800,
            Quartz.kCGImagePropertyExifUserComment: "Screenshot",
        },
        Quartz.kCGImagePropertyPNGDictionary: {
            Quartz.kCGImagePropertyPNGSoftware: "macOS 26.0",
        },
    }, width=2880, height=1800)
    record = header_image_reader()(screenshot)

    assert [tag.name for tag in record.exif if tag.kind == CAMERA_EXIF] == []
    # The screenshot's OWN §2.6 signal is still read, at its own tier.
    assert record.software == {"Software": "macOS 26.0"}
    # And the encoder-written tags are still evidence -- untiered, never dropped.
    assert {"PixelXDimension", "UserComment"} <= set(by_name(record))


def test_one_format_has_one_name_however_the_reader_reached_it(tmp_path):
    """A JPEG whose start-of-frame sits past the 64 KiB header window -- an iPhone
    photo with a large APP1, XMP and ICC run does -- is sized by the image stack
    rather than by `_jpeg`, and it must still be `JPEG`. Two spellings of one format
    in `image_format` would make §2.6's format comparison depend on how big the
    file's metadata happened to be."""
    from readers.image_headers import _image_format
    padded = tmp_path / "big-header.jpg"
    filler = b"\xff\xe1" + struct.pack(">H", 65535) + b"\x00" * 65533
    padded.write_bytes(
        b"\xff\xd8" + filler + filler
        + b"\xff\xc0" + struct.pack(">H", 11) + b"\x08"
        + struct.pack(">HH", 3024, 4032) + b"\x01\x01\x11\x00" + b"\xff\xd9")

    assert _image_format(padded.read_bytes()[:1 << 16]) == "JPEG"
    header_read = header_image_reader()(jpeg(tmp_path / "small.jpg", 4032, 3024))
    assert header_read.image_format == "JPEG"


def test_the_signal_names_the_reader_assigns_are_section_2_6s_own():
    """The reader classifies and P5 places, so a fourth name or a misspelling would
    reach `extract_image._tier` and raise `UnknownSignal` on a real photograph.
    `SIGNAL_TIER` is that gate, and these three are its keys."""
    assert {CAMERA_EXIF: 1, CAPTURE_TIME: 2, GPS: 2}.items() <= SIGNAL_TIER.items()


def test_a_list_valued_tag_is_one_string_and_not_an_objective_c_description(tmp_path):
    """`ISOSpeedRatings` is an array and arrives as an `NSArray`, whose own `str()` is
    a multi-line Objective-C description. RAW-1 forbids P5 constructing a raw value,
    so the READER renders it -- one way, once -- and `400` is what a person reads."""
    tags = by_name(header_image_reader()(
        written(tmp_path, *WRITABLE["JPEG"], DECLARED)))
    assert tags["ISOSpeedRatings"].value == "400"
    assert "\n" not in tags["ISOSpeedRatings"].value
    assert tags["FocalLength"].value == "6.86"


def test_colour_information_is_read_where_the_format_publishes_it(tmp_path):
    """§2.6's "color information where useful", at ImageIO's own key names. It is not
    EXIF, so it lands in `color`, which `extract_image` emits with no signal tier."""
    record = header_image_reader()(written(tmp_path, *WRITABLE["PNG"], DECLARED))
    assert record.color["ColorModel"] == "RGB"
    assert record.color["Depth"] == "8"


def test_a_bmp_publishes_no_capture_metadata_and_no_row_claims_it_did(tmp_path):
    """A BMP container has nowhere to put EXIF, and the same properties written into
    the other four formats come back out of it as nothing at all.

    THE RECORD SAYS SO BY BEING EMPTY, and the limit is worth stating out loud: this
    reader cannot tell "this container has no EXIF box" from "this photograph was
    stripped by a messaging app", and §2.6's trap 1 is that they must not be told
    apart by guessing. P4 settles what may be written either way -- an extractor "may
    not write an 'EXIF absent' ... observation" -- so neither case produces a row."""
    record = header_image_reader()(written(tmp_path, *WRITABLE["BMP"], DECLARED))

    assert record.image_format == "BMP"
    assert record.exif == () and record.software == {}
    # The metadata route RAN; there was nothing in the container for it to read.
    assert record.unread_reason is None


def test_a_file_whose_format_the_image_stack_cannot_name_says_which_slots_are_unread(
        tmp_path):
    """"What a format cannot supply is recorded as the honest reason", and the case
    this reader can state honestly is the one where the metadata route never ran at
    all: ImageIO recognises no format in an SVG, so §2.6's slots were not looked at
    rather than looked at and found empty.

    The sentence goes on the extraction run -- `extractors/image.py` puts it in the
    run's `config` and marks the run `partial` -- and never into an observation."""
    record = read(svg(tmp_path / "logo.svg", 'width="240" height="120"'))

    assert record.unread_reason is not None
    assert "never looked at" in record.unread_reason
    assert record.exif == () and record.color == {} and record.software == {}


def test_the_three_iso_brands_share_one_branch_and_it_is_the_signature_readers():
    """HEIC, HEIF and AVIF are one container with three brands, and the product
    already had the table that tells them apart. `104` §18.2 item 21 made
    `readers/signatures.py` the single answer to "what are these bytes"; the image
    reader asks IT rather than carrying a second brand table, and the ROUTER decides
    which of those tokens is an image."""
    from extractors.router import SOURCE_TYPE_BY_FORMAT
    from readers.image_headers import _image_format
    from readers.signatures import format_from_magic

    for brand, token in ((b"heic", "HEIC"), (b"mif1", "HEIC"), (b"msf1", "HEIF"),
                         (b"hevc", "HEIF"), (b"avif", "AVIF"), (b"avis", "AVIF")):
        head = b"\x00\x00\x00\x18ftyp" + brand + b"\x00" * 8
        assert format_from_magic(head) == token.lower()
        assert _image_format(head) == token

    # A brand the router does NOT call an image is not claimed here: a `.mov` screen
    # recording is the same box structure with a different brand.
    quicktime = b"\x00\x00\x00\x18ftypqt  " + b"\x00" * 8
    assert format_from_magic(quicktime) == "mov"
    assert _image_format(quicktime) is None
    assert SOURCE_TYPE_BY_FORMAT["mov"][0] != "image"


def test_a_pdf_and_a_psd_are_not_claimed_by_the_image_reader():
    """`format_from_magic` knows more than images -- it is the whole signature table
    -- so the filter is the router's own routing and not a format list here. A `.pdf`
    and a `.psd` have their own handlers and must not be answered for."""
    from readers.image_headers import _image_format
    assert _image_format(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3") is None
    assert _image_format(b"8BPS\x00\x01" + b"\x00" * 20) is None


# --------------------------------------------------------------------------- #
# §2.6's other hash -- `104` §18.43, the audit's item 10
#
# "Exact hashes and perceptual hashes can identify duplicates and near-duplicates."
# The exact half is P1's and needs nobody. The other half had NO CARRIER ANYWHERE in
# the deployment until the owner ruled on 11 Sep 2026: this reader supplied no
# `perceptual_hash`, so `extract_image` emitted no `perceptual hash` observation, so
# `facts.families._near_families` counted fewer than two carriers and returned before
# its loop on every corpus -- 0 measured on both real corpora (`cli.py`'s
# `_family_pass`). `98` was ratified as written and as written it named neither the
# algorithm (§3.1) nor the distance (§3.2, "the number is the owner's"); the ruling
# named both, and `readers/perceptual_hash.py` holds them together as §3.1 requires.
#
# The fixtures are written by the test through the same library the reader reads
# with, as everything above this line is. A re-encoding is a SECOND JPEG QUALITY over
# one raster: same picture, different bytes, so P1's content hashes differ and the
# exact half of `duplicate_family` correctly says nothing about the pair.
# --------------------------------------------------------------------------- #


def _patterned(width, height, boxes):
    """A raster with real structure in it, so two of them can genuinely differ.

    `blank_image` above is solid white, which is the right fixture for a dimension
    and the wrong one for a difference hash: every adjacent pair of cells is equal,
    so two unrelated blanks hash identically and a threshold test over them would
    measure nothing.
    """
    context = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(context, 1, 1, 1, 1)
    Quartz.CGContextFillRect(context, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextSetRGBFillColor(context, 0, 0, 0, 1)
    for left, bottom, wide, high in boxes:
        Quartz.CGContextFillRect(
            context, Quartz.CGRectMake(left, bottom, wide, high))
    return Quartz.CGBitmapContextCreateImage(context)


def _encoded(path, image, quality):
    destination = Quartz.CGImageDestinationCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), "public.jpeg", 1, None)
    assert destination is not None, "this ImageIO cannot write JPEG"
    Quartz.CGImageDestinationAddImage(
        destination, image,
        {Quartz.kCGImageDestinationLossyCompressionQuality: quality})
    assert Quartz.CGImageDestinationFinalize(destination), path
    return path


def test_the_reader_supplies_the_perceptual_hash_section_2_6_names(tmp_path):
    """§2.6's other hash, through the real reader and not an `ImageRecord` fixture.

    `tests/p5/test_p5_image.py::test_the_perceptual_hash_is_emitted_and_the_content
    _hash_is_not` pins `extract_image`'s side of the contract by HANDING it a record
    that carries `phash:8f3a`. What it could not see is whether anything in the
    deployment ever builds such a record. Until the owner's ruling of 11 Sep 2026
    nothing did, and `_near_families` measured 0 carriers on both real corpora.
    """
    record = header_image_reader()(written(tmp_path, *WRITABLE["JPEG"]))
    assert record is not None, "the JPEG fixture was not read at all"
    assert record.perceptual_hash is not None
    name, _, digits = record.perceptual_hash.partition(":")
    # The value states the algorithm it was computed under: `98` §3.1 requires the
    # metric to ship "together with the hash it assumes", and a bare hex string
    # would let a future algorithm's value be compared against this one bit for bit.
    assert name == HASH_ALGORITHM
    assert len(digits) * 4 == NEAR_DUPLICATE_HASH_BITS


def test_a_format_the_image_stack_will_not_decode_gets_no_hash_and_no_zero(tmp_path):
    """A refusal is `None`. A zero hash would be within distance 0 of every other.

    The SVG branch is read entirely out of the head of the file and never handed to
    ImageIO, so it is the reader's own case of a record with dimensions and no
    pixels decoded.
    """
    path = tmp_path / "diagram.svg"
    path.write_bytes(b'<svg width="120" height="80"></svg>')
    record = header_image_reader()(path)
    assert (record.width, record.height) == (120, 80)
    assert record.perceptual_hash is None


def test_a_re_encoding_is_near_and_a_different_picture_is_not(tmp_path):
    """The metric at the owner's threshold, over two encodings of one raster.

    `98` §4's own material -- "resized exports, screenshots of screenshots, and
    messaging-app re-encodes" -- is what byte identity cannot catch and what this
    number is for. Both directions are measured in one test on purpose: a threshold
    wide enough to satisfy the first half and narrow enough to satisfy the second is
    the whole of what `98` §3.2 asked the owner to choose.
    """
    read = header_image_reader()
    one = _patterned(640, 480, ((40, 40, 200, 160), (400, 300, 180, 120)))
    other = _patterned(640, 480, ((300, 60, 90, 380), (60, 380, 500, 60)))
    original = read(_encoded(tmp_path / "IMG_4821.jpg", one, 1.0)).perceptual_hash
    resaved = read(_encoded(tmp_path / "IMG_4821 (1).jpg", one, 0.55)).perceptual_hash
    different = read(_encoded(tmp_path / "IMG_5106.jpg", other, 1.0)).perceptual_hash

    assert distance(original, resaved) <= NEAR_DUPLICATE_MAX_DISTANCE
    assert near_duplicate(original, resaved)
    assert not near_duplicate(original, different)
    # And the banded key is a NECESSARY condition of the first, which is what makes
    # it safe for `_near_families` to block on: a pair within the threshold always
    # shares a band.
    assert set(near_block_keys(original)) & set(near_block_keys(resaved))


def test_a_value_this_algorithm_did_not_produce_is_refused_rather_than_compared():
    """`None`, not a distance, and no blocking key -- see `perceptual_hash.distance`.

    P5's own long-standing fixture spells `phash:8f3a`. Measuring a Hamming distance
    between that and a `dhash64` would be a number about nothing, and a False from
    `near_duplicate` is the safe side of `98` §3.2's asymmetry.
    """
    ours = f"{HASH_ALGORITHM}:{0:016x}"
    assert distance("phash:8f3a", ours) is None
    assert not near_duplicate("phash:8f3a", ours)
    assert near_block_keys("phash:8f3a") == ()

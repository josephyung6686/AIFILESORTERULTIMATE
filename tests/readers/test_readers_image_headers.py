# tests/readers/test_readers_image_headers.py
"""The reader that made `filename_pattern` and `dimension_signal` reachable at all.

`read_image` was `_no_reader`, so `extract_image` returned `unsupported` on its second
line -- before `filename_pattern` was called and before `dimension_signal` was called.
Every image in a real corpus produced ZERO observations, and the two catalogue-fed
arguments P5 declares as required keywords were, in the shipped deployment, dead code
behind a missing library. Wiring the catalogues without wiring a reader would have
left them exactly as unreachable as they were in `planning/`.

This reader reads the container header and nothing else: the format token and the
pixel dimensions, which are what catalogues 02, 03 and 04 need. **It does not read
EXIF**, so §2.6's tier-1 band ("camera EXIF is strong photo evidence") and the
capture-time and GPS halves of tier 2 stay unavailable in this deployment. That is a
stated limit, not an oversight -- and §2.6's own trap 1 is the reason it is safe to
state: "the system must not mistake the absence of EXIF for proof that an image is a
screenshot." An absence here is written nowhere.

A format the reader does not know returns `None`, which §2.4 calls `unsupported`: the
bytes were never looked at. It is never `failed`, which means a reader ran and raised.
"""
from __future__ import annotations

import struct
import zlib

import pytest

from extractors.image import ImageRecord
from readers.image_headers import header_image_reader


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
    open this kind of file" and "this file is damaged". A reader with no branch for
    HEIC must give the first."""
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


def test_the_reader_reads_no_exif_and_claims_none(tmp_path):
    """The stated limit, asserted so it cannot quietly become untrue. §2.6's tier-1
    band is unreachable in this deployment and the record says so by carrying no
    tags, rather than by carrying a tag that says "absent"."""
    record = header_image_reader()(jpeg(tmp_path / "photo.jpg", 4032, 3024))
    assert record.exif == ()
    assert record.software == {}
    assert record.perceptual_hash is None


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
                                 width=240, height=120)


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

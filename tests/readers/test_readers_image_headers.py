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

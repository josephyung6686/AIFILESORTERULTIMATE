"""Three declared formats the signature reader decides, locked in.

`104` §18.2 gap 21 put `readers/signatures` in front of every file, where before
a five-entry extension map answered first and the reader never ran for a known
extension. Three behaviours changed for files the owner has, and on 10 Sep 2026
the owner ruled "lock in and figure it out". This file is the lock: each test
states what the bytes are, what the reader says, and what the router does with
the disagreement, so a later change to any of the three is a change to a ruling
and not a drift.

Nothing here is a word list or a table of extensions deciding: the reader reads
the bytes, the router records the disagreement, and the declared extension is
kept beside the detected format on the routing decision (§2.9).
"""
from __future__ import annotations

import zipfile
from pathlib import Path

from extractors.router import SOURCE_TYPE_BY_FORMAT, route
from readers.signatures import signature_detector


def _detect():
    return signature_detector(is_protected_container=lambda path: False)


def _route(path: Path):
    return route(file_id="file", content_hash="hash", path=path,
                 extension=path.suffix, detect_format=_detect())


def test_a_numbers_document_is_the_zip_its_bytes_say_it_is(tmp_path):
    """A `.numbers` document is a ZIP bundle of iWork archives. No reader for
    the iWork archive ships, so the honest answer is the container: `zip`, routed
    to §2.5's archive family, whose manifest of member names is what the product
    can read of it. The disagreement with the declared extension is recorded."""
    path = tmp_path / "budget.numbers"
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("Index/Document.iwa", b"\x00" * 32)
        bundle.writestr("Metadata/Properties.plist", b"<plist/>")
    assert _detect()(path) == "zip"
    decision = _route(path)
    assert decision.detected_format == "zip"
    assert decision.disagree is True
    assert decision.source_type in SOURCE_TYPE_BY_FORMAT["zip"]


def test_an_illustrator_file_that_is_a_pdf_is_read_as_a_pdf(tmp_path):
    """A modern `.ai` file is PDF-compatible and opens with `%PDF-`. The bytes
    say `pdf`, so the text the PDF carries is read, where the declared extension
    alone routed it to the design family and read nothing. The disagreement is
    recorded, and the declared extension stays on the decision."""
    path = tmp_path / "poster.ai"
    path.write_bytes(b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
    assert _detect()(path) == "pdf"
    decision = _route(path)
    assert decision.detected_format == "pdf"
    assert decision.declared_extension == ".ai"
    assert decision.disagree is True
    assert decision.source_type in SOURCE_TYPE_BY_FORMAT["pdf"]


def test_a_camera_raw_names_no_format_and_falls_to_its_declared_extension(tmp_path):
    """A camera raw carries no signature this reader knows and is not text, so the
    reader says nothing (`None`), the router falls back to the declared
    extension, and the long-tail reader that extension names refuses binary
    (`test_a_camera_raw_is_still_not_a_spreadsheet`): the file is recorded
    unsupported, never a sheet of its own bytes and never an image the product
    cannot decode. No disagreement is recorded, because nothing was detected."""
    # Sensor bytes: control characters that decode as UTF-8 and open with no
    # signature this reader knows. (A `FF D8 FF` opening would be a JPEG, and
    # the reader would rightly say so.)
    path = tmp_path / "IMG_0001.raw"
    path.write_bytes((b"\x00\x01\x02rawsensor\x03" + bytes(range(4, 32))) * 64)
    assert _detect()(path) is None
    decision = _route(path)
    assert decision.detected_format is None
    assert decision.disagree is False
    assert decision.declared_extension == ".raw"
    assert decision.source_type in SOURCE_TYPE_BY_FORMAT["raw"]

# src/readers/doc_cocoa.py
"""The legacy `.doc` reader, through the framework this deployment already links.

A `.doc` is an OLE compound document -- the format `.docx` replaced in 2007 -- and
nothing in the standard library opens one. `readers/docx_python_docx.py` cannot
either: it opens a ZIP of XML parts, and this is neither.

Measured over the owner's 199-file corpus (`.groundtruth/baseline/scorecard.txt`,
2026-09-04): `.doc  0 of 2  0.0%`, recorded `unsupported`. Two General Chemistry
practice exams, 1,290 words each, whose labels want them under
`PHYS1403/practice test` -- and the course code that would put them there sat in
their first line, unread.

`unsupported` is §2.4's statement about the DEPLOYMENT: "no extractor exists for this
format in this deployment". `readers/deployment.py` is explicitly *"One `Readers` for
a macOS deployment"* and already links Quartz, Vision and Foundation; AppKit's
`NSAttributedString` reads this format. Answering `unsupported` while the framework
sat linked and unused was choosing the word rather than earning it.

**Why not `/usr/bin/textutil`.** That was the first version of this reader and
`tests/integration/test_single_egress.py` refused it, correctly. `subprocess` is on
that scan's `NETWORK_MODULES` -- added 2026-09-02, "Handing the bytes to `curl` is not
a future-SDK gap; it is the oldest way out of a process there is" -- and this is not a
provider module. The rule cost nothing here: `textutil` is a wrapper around this same
Cocoa call, so the in-process route is the shorter one, and it is measurably STRICTER
(see the third outcome below).

**The three outcomes, and they are not interchangeable.**

    not an OLE compound document  -> None, §2.4's `unsupported`
    AppKit is not installed       -> None, §2.4's `unsupported`
    OLE, and Cocoa refused it     -> raises, §2.4's `failed`

The signature check is what separates the first from the third. Cocoa returns the same
nil for a renamed text file and for a damaged Word document, and those are different
facts about different files: one is "we do not read this format", the other is "this
file is broken". Answering `unsupported` for both would file a damaged document under
a missing feature.

That third outcome is reachable only because Cocoa is strict. Measured 2026-09-04 on
the same bytes -- the first 2,000 of a real `.doc` -- `textutil` exited 0 and printed
2,579 characters of transcoded binary, which recorded `complete` is a file the product
claims to have read and has not. `NSAttributedString` returns nil.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from extractors.structured_text import TextDocument

#: The OLE2 / Compound File Binary Format header signature (MS-CFB §2.2). Every legacy
#: Word document begins with these eight bytes; nothing else this reader is asked
#: about does. A signature and not a heuristic, like `_PNG_SIGNATURE` in
#: `readers/image_headers.py`.
OLE_COMPOUND_FILE_SIGNATURE: bytes = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


class ConversionFailed(Exception):
    """Cocoa was asked to read a legacy Word document and would not. §2.4's `failed`.

    Deliberately NOT folded into the `None` path. `None` says no reader exists for
    this format in this deployment and the bytes were never looked at, which for a
    damaged `.doc` would report a corrupt file as a missing feature.
    """


def cocoa_doc_reader() -> Callable[[Path], TextDocument | None]:
    """Build a `read_doc` for `readers.text_documents.stdlib_text_document_reader`.

    No arguments, and none withheld: this reader holds no threshold, no ceiling and
    no policy. It asks the framework for the whole document and returns what comes
    back, so there is no number for `cli.py` to choose.
    """
    # Imported HERE and not at module scope, for the reason `readers/deployment.py`
    # gives about `ocr_vision`: a person running `--list-situations`, or any scan
    # with no legacy Word document in it, should not pay a framework's import for a
    # call their run never makes.
    import AppKit
    from Foundation import NSURL

    options = {AppKit.NSDocumentTypeDocumentOption: AppKit.NSDocFormatTextDocumentType}

    def read_doc(path: Path) -> TextDocument | None:
        path = Path(path)
        try:
            with open(path, "rb") as handle:
                header = handle.read(len(OLE_COMPOUND_FILE_SIGNATURE))
        except OSError:
            return None
        if header != OLE_COMPOUND_FILE_SIGNATURE:
            return None
        attributed, _attributes, error = (
            AppKit.NSAttributedString.alloc()
            .initWithURL_options_documentAttributes_error_(
                NSURL.fileURLWithPath_(str(path)), options, None, None))
        if attributed is None:
            raise ConversionFailed(
                f"Cocoa would not read {path} as a legacy Word document: {error}")
        # No headings and no language. This call returns styled runs, not an outline,
        # and `Region`'s contract forbids a caller inventing a heading from a line
        # being short or bold -- the same rule `readers/deployment.read_text_file`
        # obeys and the reason it "does not claim to be a Markdown reader".
        return TextDocument(text=str(attributed.string()))

    return read_doc

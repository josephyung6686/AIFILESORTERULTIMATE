# tests/readers/pdf_bytes.py
"""A real PDF, hand-assembled with stdlib only.

A module rather than a fixture in one of the test files, because both adapters need
it and they skip on DIFFERENT things: the pdfminer tests skip without pdfminer, the
Vision tests skip without Vision or off macOS. Importing the builder from either test
module would couple those two skips together and silently stop running one adapter's
tests whenever the other's library was missing.

Named `pdf_bytes` rather than `conftest` deliberately. pytest's prepend import mode
keys a rootless module on its BASENAME, so a second `conftest.py` claims
`sys.modules["conftest"]` and whichever directory imports first wins for the whole
session. That collision has cost this project a whole-suite outage twice.
"""
from pathlib import Path

#: Three sizes at three positions: the minimum that distinguishes a heading from
#: body text from a footer, which is the whole of what a zone adapter must decide.
_HEADING = "BUSIB 4300 Course Information"
_BODY = "This syllabus covers the spring term for BUSIB 4300."


def build_pdf(path: Path, *, title: str = "BUSIB 4300 Syllabus",
              pages: int = 1, matrix_scaled: bool = False) -> Path:
    """A valid PDF with correct xref offsets, `pages` pages long.

    Object numbering, which is the whole difficulty here: 1 catalog, 2 page tree,
    then one page object per page, then one contents stream per page, then the two
    fonts, then the info dictionary. A font reference pointing at the wrong object
    still parses -- pdfminer warns about the missing FontBBox and carries on -- and
    the only visible symptom is that every character reports the wrong size, which
    silently turns every heading into body text.
    """
    font_bold, font_plain = 3 + 2 * pages, 4 + 2 * pages

    objs: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"",                                        # 2: filled in below
    ]
    kids = " ".join(f"{3 + i} 0 R" for i in range(pages))
    objs[1] = (f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>").encode()

    contents_first = 3 + pages
    for i in range(pages):
        objs.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_bold} 0 R /F2 {font_plain} 0 R >> >> "
            f"/Contents {contents_first + i} 0 R >>".encode())
    for i in range(pages):
        # `matrix_scaled` writes THE SAME PAGE a different legal way: a 1-point font
        # with the size in the text matrix, which is what every PDF LaTeX produces.
        # It looks identical and reads identical, and a library that reports the
        # DECLARED size sees three lines of 1pt type with no heading among them.
        # `readers/pdf_pdfium.py` needs a document in this shape to be tested at all;
        # `Tm` replaces `Tf`+`Td` because the matrix carries both the scale and the
        # position.
        if matrix_scaled:
            stream = (
                f"BT /F1 1 Tf 24 0 0 24 72 700 Tm ({_HEADING}) Tj ET\n"
                f"BT /F2 1 Tf 11 0 0 11 72 650 Tm ({_BODY}) Tj ET\n"
                f"BT /F2 1 Tf 9 0 0 9 72 40 Tm (page {i + 1} of {pages}) Tj ET\n"
            ).encode()
        else:
            stream = (
                f"BT /F1 24 Tf 72 700 Td ({_HEADING}) Tj ET\n"
                f"BT /F2 11 Tf 72 650 Td ({_BODY}) Tj ET\n"
                f"BT /F2 9 Tf 72 40 Td (page {i + 1} of {pages}) Tj ET\n"
            ).encode()
        objs.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
                    + stream + b"endstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    info_num = len(objs) + 1
    objs.append(b"<< /Title (" + title.encode() + b") /Author (Registrar) "
                b"/Creator (hand) /CreationDate (D:20260821120000+00'00') >>")

    out = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj\n" + body + b"\nendobj\n"
    xref_at = len(out)
    size = len(objs) + 1
    out += b"xref\n0 " + str(size).encode() + b"\n0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode()
    out += (b"trailer\n<< /Size " + str(size).encode()
            + b" /Root 1 0 R /Info " + str(info_num).encode()
            + b" 0 R >>\nstartxref\n" + str(xref_at).encode() + b"\n%%EOF\n")
    path.write_bytes(bytes(out))
    return path

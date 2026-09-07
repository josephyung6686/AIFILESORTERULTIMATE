"""R-33: a format this deployment cannot read says so, in the record and on the screen.

Four shapes, measured through the whole command on 2026-09-06, and only one of the
four was actually wrong -- which is why this file pins all four rather than fixing a
category.

    diagram.svg     image.metadata / unsupported   already honest
    refs.ris        text.structured / complete     genuinely read; RIS is text
    capture.raw     text.structured / COMPLETE     a lie, and the defect
    opaque-noext    format.unrouted / unsupported  honest

`capture.raw` held `\\x00\\x01\\x02rawsensor\\x03`, which is binary and is also valid
UTF-8. `_read_delimited_if_text` guarded `.raw` and `.rlt` by decoding strictly, on
the stated ground that "text decodes, a photograph does not" -- true of the
invalid-UTF-8 header its own test uses and false of the C0 control block. So the
bytes decoded, became a one-cell spreadsheet holding themselves, and the run recorded
`complete`: §2.4's "never silently treat an unsupported format as an empty document"
broken in the other direction, and a file the run then counted as one it had READ.

The fix is `readers.signatures.looks_like_text`, which is `file(1)`'s control-
character test and was already the whole of that module's weak identification. One
question, one answer, in the layer that had it.

NOTHING VANISHES ON THE SCREEN EITHER, which is the other half of R-33's sentence
and was already true: every one of these files is named in the report with a reason.
Pinned here so it stays that way.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402

SVG = "diagram.svg"
RIS = "refs.ris"
RAW = "capture.raw"
NOEXT = "opaque-noext"
READABLE = "PHYS 1401 syllabus.txt"


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    root = tmp_path_factory.mktemp("r33")
    corpus = root / "corpus"
    corpus.mkdir()
    (corpus / SVG).write_text(
        '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg">'
        "<text>PHYS 1401</text></svg>")
    (corpus / RIS).write_text(
        "TY  - JOUR\nAU  - Lee, A\nTI  - On rotation\nPY  - 2026\nER  -\n")
    (corpus / RAW).write_bytes(b"\x00\x01\x02rawsensor\x03")
    (corpus / NOEXT).write_bytes(b"noextension binary\x00\x01\x02")
    (corpus / READABLE).write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")

    database = root / "plan.sqlite"
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "t",
                     "--database", str(database)], out=out) == 0, out.getvalue()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        yield conn, out.getvalue()
    finally:
        conn.close()


def _completeness(conn, filename: str) -> set[str]:
    return {row[0] for row in conn.execute(
        "SELECT e.completeness FROM extraction_runs e JOIN files f "
        "ON f.file_id = e.file_id "
        "WHERE f.filename = ? AND e.analysis_tier <> 'filesystem'", (filename,))}


def test_a_binary_file_under_a_spreadsheet_extension_is_not_recorded_as_read(run):
    """THE DEFECT. `complete` said the product had read a sensor file it had not."""
    conn, _ = run

    assert _completeness(conn, RAW) == {"unsupported"}


def test_the_binary_file_leaves_no_observation_holding_its_own_bytes(run):
    """The other half of the same lie: the cell it became.

    A `spreadsheet` observation whose value is the file's raw bytes is not merely
    useless. Recognition matches authored terms against evidence values, and
    `folders_nothing_could_be_read_from` asks whether a file has any observation
    that did not come from the filesystem -- so this row made a binary blob look
    like a file somebody could be asked a sensible question about.
    """
    conn, _ = run
    rows = conn.execute(
        "SELECT e.source_type FROM evidence e JOIN files f "
        "ON f.file_id = e.file_id WHERE f.filename = ?", (RAW,)).fetchall()

    assert {row[0] for row in rows} == {"filesystem"}


def test_the_three_that_were_already_honest_stay_that_way(run):
    """Fixing a category rather than a defect is how the honest ones break.

    An SVG has no reader here and says `unsupported`; an extensionless binary is
    unrouted and says the same; a RIS file IS text and is genuinely read, and a
    guard that made it `unsupported` would be a coverage regression wearing this
    fix's name.
    """
    conn, _ = run

    assert _completeness(conn, SVG) == {"unsupported"}
    assert _completeness(conn, NOEXT) == {"unsupported"}
    assert _completeness(conn, RIS) == {"complete"}
    assert _completeness(conn, READABLE) == {"complete"}


def test_every_one_of_them_is_named_on_the_screen(run):
    """`84` §1. A file the product could not read is still the person's file."""
    _, printed = run

    for name in (SVG, RIS, RAW, NOEXT, READABLE):
        assert name in printed, f"{name} is in no list:\n{printed}"

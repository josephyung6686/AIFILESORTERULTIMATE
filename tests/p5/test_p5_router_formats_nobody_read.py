# tests/p5/test_p5_router_formats_nobody_read.py
"""The formats that recovered NO TEXT AT ALL on the owner's real 199-file corpus.

Measured 2026-09-04, `.groundtruth/baseline/scorecard.txt`, "by format, weakest
first":

    .raw       0 of   2    0.0%
    .ris       0 of   1    0.0%
    .doc       0 of   2    0.0%
    .rlt       0 of   1    0.0%
    .code-workspace   0 of   1    0.0%
    (none)     0 of   9    0.0%

Every one of them recorded `unsupported`, which was TRUE -- no key, no handler, no
reader -- and it was true for a reason nobody had looked at. Four of the six are
plain text or a text container this deployment already reads; what was missing was
the routing key, not the ability.

The keys are added the way the thirteen code formats and the eleven image and
audio formats were: on ratification B6 (2026-08-20), *"Every file type is
extracted, and extracted correctly for its own type"*, with the format COUNTED on
the owner's real disk and declared in `test_p5_router.py`'s walk as well as in the
table, so the next addition still cannot arrive silently.

`.svg` is deliberately absent from this file. It is not one of these: it routes,
E5 reads it, and it records `complete` already -- see the module docstring of
`tests/readers/test_readers_formats_nobody_read.py`.
"""
from pathlib import Path

import pytest

from extractors.router import SOURCE_TYPE_BY_FORMAT, route

HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"


def decide(name, extension, detected):
    return route(file_id="f1", content_hash=HASH, path=Path("/corpus") / name,
                 extension=extension, detect_format=lambda _path: detected)


# --------------------------------------------------------------------------- #
# the five extensions
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fmt,family", [
    ("ris", "text_document"),        # a bibliography citation record: plain text
    ("doc", "text_document"),        # legacy Word, the binary `.docx` replaced
    ("rlt", "spreadsheet"),          # an Instron tensile-test export: quoted CSV
    ("raw", "spreadsheet"),          # the same instrument's other export extension
    ("code-workspace", "code_structured"),   # a VS Code workspace: JSON
])
def test_each_format_that_recovered_nothing_now_names_a_family(fmt, family):
    assert SOURCE_TYPE_BY_FORMAT[fmt][0] == family


@pytest.mark.parametrize("name,extension", [
    ("10.1007_s44217-025-00812-z-citation.ris", ".ris"),
    ("1403.Sample.Exam.1.No.2.w.Key_revised.doc", ".doc"),
    ("192K - allen.rlt", ".rlt"),
    ("10% PVA 0% RDP suture retention v1 7_18_24.raw", ".raw"),
    ("Python 1006.code-workspace", ".code-workspace"),
])
def test_each_reaches_e3_rather_than_the_unsupported_stop(name, extension):
    """The real filenames from `.groundtruth/corpus/`, by DECLARED extension.

    `cli._detect_format` answers None for all five, so the declared extension is
    what routes them -- which is §2.9's "and on the declared extension otherwise".
    """
    decision = decide(name, extension, None)
    assert decision.extractor_name == "text.structured"
    assert decision.unrouted_completeness is None


def test_the_instrument_extensions_are_the_spreadsheet_family_and_say_why():
    """`.rlt` and `.raw` are Instron's own export extensions and the bytes are CSV.

    Verified on the three real files: each opens `"Test Type","Manual"` CRLF, then
    a quoted key/value header block, then the force-extension table.

    `.raw` is AMBIGUOUS and the ambiguity is answered in the READER, not here: a
    camera raw carries the same extension and is not text, so
    `readers.long_tail_stdlib` decodes strictly and returns None for it, which is
    §2.4's `unsupported` -- "no reader exists for this format in this deployment".
    Guessing at the extension level would have recorded a photograph as a
    spreadsheet with mojibake cells and called it `complete`.
    """
    assert SOURCE_TYPE_BY_FORMAT["rlt"] == ("spreadsheet",)
    assert SOURCE_TYPE_BY_FORMAT["raw"] == ("spreadsheet",)


# --------------------------------------------------------------------------- #
# the nine files with no extension at all
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("fmt,family", [
    ("dockerfile", "code_structured"),
    ("makefile", "code_structured"),
])
def test_the_two_extensionless_build_files_are_code_and_not_prose(fmt, family):
    """§2.4 keeps code out of the prose path -- "rather than forcing semantic
    analysis to infer a project from arbitrary code text" -- and a Dockerfile and a
    Makefile are recipes, not documents. They route, their text is stored, and
    `structured_text` emits no `body` observation for them. That is the honest
    trade and it is the same one every `.py` on the disk already makes."""
    assert SOURCE_TYPE_BY_FORMAT[fmt][0] == family


def test_a_file_with_no_extension_cannot_disagree_with_what_was_detected():
    """`disagree` is "the detected format contradicts the declared extension".

    A file named `LICENSE` declares nothing, so there is nothing for a detection to
    contradict, and recording the pair as a disagreement would put seven false
    "this file is misnamed" rows in `extraction_routing` for the corpus's nine
    extensionless files. An absent extension is not a wrong one.
    """
    decision = decide("LICENSE", "", "txt")
    assert decision.detected_format == "txt"
    assert decision.declared_extension == ""
    assert decision.disagree is False
    assert decision.source_type == "text_document"
    assert decision.extractor_name == "text.structured"


def test_a_real_disagreement_is_still_recorded_as_one():
    """The guard on the line above: only the EMPTY extension is exempted."""
    decision = decide("report.txt", ".txt", "zip")
    assert decision.disagree is True

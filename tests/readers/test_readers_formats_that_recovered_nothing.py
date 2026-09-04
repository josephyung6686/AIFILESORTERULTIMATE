# tests/readers/test_readers_formats_that_recovered_nothing.py
"""The whole Wave-2 path over the formats that recovered NO TEXT AT ALL. Real readers.

`.groundtruth/baseline/scorecard.txt`, a real run over 199 of the owner's real files,
2026-09-04, "by format, weakest first":

    .raw       0 of   2    0.0%      .rlt       0 of   1    0.0%
    .ris       0 of   1    0.0%      .code-workspace   0 of   1    0.0%
    .doc       0 of   2    0.0%      (none)     0 of   9    0.0%

Sixteen files, no text between them. Every one recorded `unsupported`, which was the
honest word for a product with no key and no reader -- and which is a statement about
the PRODUCT that nobody had gone back and checked. Four of the six formats are plain
text or a text container this deployment already read.

Each fixture below is shaped like the real file it stands for, named like it, and the
docstrings say which. The router, the dispatcher, the readers and P4's tables are all
the real ones: this is the file that would go red if any of the six were connected to
nothing, which is `84` §5's dominant defect and is what unit tests of a routing table
cannot see.

`.svg` is not here. It was never in this list: it routes to E5, E5 reads its
dimensions, and it records `complete`. See `test_the_corpus_svgs_carry_no_text_to
_recover` at the bottom, which is the measurement rather than a fix.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

# Before the `readers.deployment` import, for the reason `test_readers_end_to_end.py`
# gives: `deployment` imports Vision and Quartz at module scope, so a machine without
# pyobjc would fail COLLECTION -- fatal to the whole run -- rather than skip.
pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")
pytest.importorskip("Vision", reason="pyobjc-framework-Vision is a `readers` extra")
pytest.importorskip("Quartz", reason="pyobjc-framework-Quartz is a `readers` extra")
pytest.importorskip("AppKit", reason="pyobjc-framework-Cocoa is a `readers` extra")

#: The fixture builder for the legacy `.doc`, and deliberately not the reader:
#: `readers/doc_cocoa.py` reads that format in-process because `subprocess` is on
#: `test_single_egress.NETWORK_MODULES`. A test may shell out; `src/` may not.
TEXTUTIL = "/usr/bin/textutil"

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from orchestrator import TARGETED_OCR_UNAVAILABLE, run_wave2  # noqa: E402
from readers.deployment import macos_readers  # noqa: E402

#: A cell ceiling high enough that no fixture here reaches it. `macos_readers`
#: refuses to pick one -- it is a policy and `cli.SPREADSHEET_CELL_CEILING` is
#: where the product picks it -- so every caller states the one it means.
CELL_CEILING_UNREACHED = 1_000_000
from scan_agent.corpus_source import FilesystemCorpusSource  # noqa: E402
from scan_agent.selection import record_selection  # noqa: E402


@pytest.fixture()
def db(conn):
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from evidence_shape.schema import create_evidence_schema
    from extractors.schema import create_extraction_schema
    from scan_agent.schema import create_scan_schema
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_eval_schema(conn)
    return conn


COURSE_CODE = re.compile(r"\b[A-Z]{2,5}\s?\d{3,4}\b")


def find_course_codes(text: str):
    from extractors.reading import StructuredString
    return tuple(StructuredString(kind="identifier", start=m.start(), end=m.end())
                 for m in COURSE_CODE.finditer(text))


#: The first lines of `10.1007_s44217-025-00812-z-citation.ris`, verbatim.
RIS = ("TY  - JOUR\n"
       "AU  - Ang, Chin-Siang\n"
       "PY  - 2025\n"
       "TI  - Developing AI literacy in healthcare education\n"
       "JO  - Discover Education\n"
       "AB  - The rapid integration of artificial intelligence into healthcare is "
       "reshaping clinical practice and the competencies practitioners need.\n")

#: The first lines of `192K - allen.rlt`, verbatim, CRLF and all.
INSTRON = ('"Test Type","Manual"\r\n'
           '"Name:","80PMMA20PBAT"\r\n'
           '"Operator ID:","kai"\r\n'
           '"Test date:","7/3/24"\r\n'
           '"Geometry:","Rectangular"\r\n'
           '"Extension","Load"\r\n'
           '0.00000,0.01526\r\n')

#: `Desktop/Python 1006/Python 1006.code-workspace`, whole. It really is this small.
WORKSPACE = '{\n\t"folders": [\n\t\t{\n\t\t\t"path": "."\n\t\t}\n\t]\n}\n'


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """One file per format, named and shaped like the corpus file it stands for."""
    root = tmp_path / "Downloads"
    root.mkdir()
    (root / "10.1007_s44217-025-00812-z-citation.ris").write_text(RIS,
                                                                  encoding="utf-8")
    (root / "192K - allen.rlt").write_text(INSTRON, encoding="utf-8", newline="")
    (root / "10% PVA 0% RDP suture retention v1 7_18_24.raw").write_text(
        INSTRON, encoding="utf-8", newline="")
    (root / "Python 1006.code-workspace").write_text(WORKSPACE, encoding="utf-8")
    # `Desktop/ThirdEye/LICENSE` and `Desktop/ThirdEye/gaze2/Dockerfile`: no
    # extension at all, which is the largest of the six buckets.
    (root / "LICENSE").write_text(
        "Apache License\nVersion 2.0, January 2004\n"
        "Licensed under the Apache License, Version 2.0.\n", encoding="utf-8")
    (root / "Dockerfile").write_text(
        "FROM python:3.12-slim\nRUN apt-get update\n", encoding="utf-8")
    if Path(TEXTUTIL).exists():
        source = tmp_path / "exam.txt"
        source.write_text("General Chemistry I 1403 Dr. Beer\n\n"
                          "Sample Exam 1 - No. 2\n\n"
                          "Provide the best possible answer to the question.\n",
                          encoding="utf-8")
        subprocess.run(
            [TEXTUTIL, "-convert", "doc", "-output",
             str(root / "1403.Sample.Exam.1.No.2.w.Key_revised.doc"), str(source)],
            check=True, capture_output=True)
    return root


def go(db, corpus):                                          # noqa: F811
    """`run_wave2` composed the way `cli.py` composes it: cli's own detector and
    the deployment's own readers, so nothing here is a fixture reader."""
    from evidence_shape.store import RunWriter
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    selection = record_selection(db, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        db, selection,
        source=FilesystemCorpusSource(),
        mime_type_for=cli._mime_type_for,
        scan_state="scanned", budget_exhausted=lambda: False,
        detect_format=cli._detect_format,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=macos_readers(find_structured_strings=find_course_codes,
                              spreadsheet_cell_ceiling=CELL_CEILING_UNREACHED),
        sink=RunWriter(db, author="P5"),
        now=lambda: "2026-09-04T12:00:00+00:00", context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


# --------------------------------------------------------------------------- #
# the measurement's own two lines, per file
# --------------------------------------------------------------------------- #

def runs_for(db, name: str) -> list[dict]:
    """Every extraction run for one file, by its corpus-relative name."""
    return [dict(row) for row in db.execute(
        "SELECT r.extractor_name, r.completeness, r.run_id FROM extraction_runs r "
        "JOIN files f ON f.file_id = r.file_id WHERE f.current_path LIKE ?", (f"%{name}",))]


def text_unit_count(db, name: str) -> int:
    return db.execute(
        "SELECT count(*) FROM text_units t JOIN extraction_runs r "
        "ON t.run_id = r.run_id JOIN files f ON f.file_id = r.file_id "
        "WHERE f.current_path LIKE ?", (f"%{name}",)).fetchone()[0]


def evidence_values(db, name: str) -> list[str]:
    """The values `tools/groundtruth` counts as a PROSE OBSERVATION: rows from a
    text-producing extractor, `filesystem.record` excluded because every file has
    four of those and counting them makes the number read 100% and say nothing."""
    return [row[0] for row in db.execute(
        "SELECT e.raw_value FROM evidence e JOIN files f ON f.file_id = e.file_id "
        "WHERE f.current_path LIKE ? AND e.extractor_name = 'text.structured' "
        "AND e.superseded_by IS NULL", (f"%{name}",))]


#: (the file, the words that prove the product read it). Every one of these formats
#: measured 0.0% text recovered on the owner's real corpus.
READ_AND_UNDERSTOOD = [
    ("citation.ris", "Discover Education"),
    ("192K - allen.rlt", "80PMMA20PBAT"),
    ("suture retention v1 7_18_24.raw", "80PMMA20PBAT"),
    ("LICENSE", "Apache License"),
]


@pytest.mark.parametrize("name,words", READ_AND_UNDERSTOOD)
def test_the_file_is_read_at_all(db, corpus, name, words):
    """The first EXTRACTION line: text recovered. `text.structured` is one of the
    extractors `tools/groundtruth.measure.TEXT_PRODUCING` counts, and a run of it
    that is `complete` with at least one text unit is what that line means."""
    go(db, corpus)
    runs = runs_for(db, name)

    assert any(r["extractor_name"] == "text.structured"
               and r["completeness"] == "complete" for r in runs), (
        f"{name} produced no complete text.structured run; got {runs}")
    assert text_unit_count(db, name) > 0, f"{name} stored no text"


@pytest.mark.parametrize("name,words", READ_AND_UNDERSTOOD)
def test_the_words_in_it_reach_the_evidence_table(db, corpus, name, words):
    """The second EXTRACTION line, and the one downstream can use.

    The recogniser scans OBSERVATIONS, never text units -- `recognition/detector.py`:
    "a detector that pulled whole text units would be a second materialisation
    locus" -- so a file whose words reached `text_units` and nothing else is a file
    the product stored and cannot read. That is why the scorecard reports the two
    lines separately, and why this test asserts the second one.
    """
    go(db, corpus)
    values = evidence_values(db, name)

    assert any(words in value for value in values), (
        f"{name!r} stored its text and no observation carries {words!r}; the "
        f"recogniser cannot reach it. Got {values}")


def test_the_instrument_export_carries_the_specimen_and_the_date_as_cells(db, corpus):
    """What a person filing these actually needs. `80PMMA20PBAT` says which polymer
    blend this run was and `7/3/24` says when -- the two facts that decide which
    experiment folder the file belongs in. Both were on disk and unreachable."""
    go(db, corpus)
    values = evidence_values(db, "192K - allen.rlt")

    assert "80PMMA20PBAT" in values
    assert "7/3/24" in values
    assert "Rectangular" in values


def test_the_citation_record_carries_its_abstract_and_not_just_its_tags(db, corpus):
    """A `.ris` is a bibliography record and the abstract is the half that says what
    the paper is ABOUT. `TY  - JOUR` would be a file read and not understood."""
    go(db, corpus)
    prose = [v for v in evidence_values(db, "citation.ris")
             if "reshaping clinical practice" in v]

    assert prose, "the abstract never became an observation"


# --------------------------------------------------------------------------- #
# the two that move the first line and not the second, said out loud
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["Python 1006.code-workspace", "Dockerfile"])
def test_the_code_files_are_read_and_deliberately_yield_no_body_prose(db, corpus,
                                                                     name):
    """§2.4 keeps code out of the prose path: structural evidence "rather than
    forcing semantic analysis to infer a project from arbitrary code text". A VS Code
    workspace and a Dockerfile are recipes, so their text is STORED -- the first
    EXTRACTION line moves -- and no `body` observation is emitted, so the second one
    does not. Routing them as documents to make both numbers move would be the
    product lying about what it understood, and this test is here so the trade is
    visible rather than discovered later in a scorecard.
    """
    go(db, corpus)
    runs = runs_for(db, name)

    assert any(r["extractor_name"] == "text.structured"
               and r["completeness"] == "complete" for r in runs), runs
    assert text_unit_count(db, name) > 0, f"{name} stored no text"
    assert not [v for v in evidence_values(db, name) if "FROM python" in v
                or '"folders"' in v], "code became body prose; §2.4 says it must not"


# --------------------------------------------------------------------------- #
# legacy Word
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not Path(TEXTUTIL).exists(),
                    reason=f"{TEXTUTIL} is a macOS system converter")
def test_a_legacy_doc_is_read_through_the_platforms_own_converter(db, corpus):
    """Two of these on the owner's disk, 1,290 words each, labelled
    `PHYS1403/practice test`. The course code that would file them was in the first
    line and the product had never opened one."""
    go(db, corpus)
    values = evidence_values(db, "1403.Sample.Exam.1.No.2.w.Key_revised.doc")

    assert any("General Chemistry I 1403" in v for v in values), values
    assert any(v == "1403" or "1403" in v for v in values)


# --------------------------------------------------------------------------- #
# the format that was ALREADY read, recorded so the claim is not repeated
# --------------------------------------------------------------------------- #

def test_the_corpus_svgs_carry_no_text_to_recover(tmp_path):
    """`.svg  0 of 7  0.0%` is NOT the same defect as the six above, and this test
    is the measurement that says so rather than a fix.

    All seven SVGs in the corpus are payment-brand icons in
    `【iV Angel】天使再生之源面膜_files/` -- visa, mastercard, JCB, UnionPay, LINE,
    FamilyMart, 7-Eleven. Every one is pure `<path d="...">` geometry: measured, the
    text content of all seven with tags stripped is the empty string. They already
    route (§2.9's design-and-creative bullet, `tests/p5/test_p5_router.py:172`), E5
    already reads their width and height, and they already record `complete`.

    What they do not have is text, and no extractor can recover text that is not
    there. Routing them to E3 to make the number move would store `<path
    d="M25.4654 9.26489L19.443 23.7731H15.5138">` as a document's prose -- the exact
    failure `readers/text_documents.py` was written to end. Their bottleneck is
    PLACEMENT, not extraction: the labels want all seven together under
    `iV Angel/page asset` and the family is already recognised.

    A `<text>` or `<title>` reader would be a real improvement for SVGs that have
    one. It would move zero files here, and it needs a `source_type` ruling first:
    `design_creative` is in neither half of E3.
    """
    import xml.etree.ElementTree as ElementTree

    icon = tmp_path / "visa.svg"
    icon.write_text(
        '<svg width="62" height="32" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="0.5" y="0.5" width="61" height="31" fill="white"/>'
        '<path d="M25.4654 9.26489L19.443 23.7731H15.5138Z"/></svg>',
        encoding="utf-8")

    root = ElementTree.fromstring(icon.read_text(encoding="utf-8"))
    assert "".join(root.itertext()).strip() == "", (
        "this fixture has text in it, which the seven real ones do not; the "
        "measurement it stands for is no longer the measurement")

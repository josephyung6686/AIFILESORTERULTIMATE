# tests/p5/test_p5_unsupported_reader.py
"""§2.4's `unsupported` outcome, reachable from every family that has a reader.

> *"A file with no extractor should be recorded as unsupported rather than silently
> treated as an empty document."*

`unsupported` and `failed` are different facts. `failed` says the reader ran and
raised — the bytes are bad. `unsupported` says this deployment ships no reader for
the format at all — the bytes were never looked at. A deployment wiring PDF and
leaving DOCX unwired is the ordinary case, not an exotic one, and it is exactly the
case `src/readers/` creates.

Two of six families honoured a `None` reader result and four crashed on it, so four
formats reported a deployment gap as a corrupt file.
"""
from pathlib import Path

import pytest

from extractors.archive import extract_archive
from extractors.docx import extract_docx
from extractors.image import extract_image
from extractors.pdf import extract_pdf
from extractors.safety import SafetyPolicy
from extractors.structured_text import extract_structured_text

NOW = "2026-08-21T12:00:00+00:00"


@pytest.fixture()
def policy():
    return SafetyPolicy(is_protected_container=lambda p: False,
                        is_dataless=lambda p: False)


@pytest.fixture()
def file_row(tmp_path):
    target = tmp_path / "thing.bin"
    target.write_bytes(b"whatever")
    return {"file_id": "f1", "content_hash": "a" * 64, "current_path": str(target)}


def _path(file_row) -> Path:
    return Path(file_row["current_path"])


NONE_READER = lambda *a, **k: None


def test_a_pdf_with_no_reader_is_unsupported_not_failed(file_row, policy):
    result = extract_pdf(file_row=file_row, path=_path(file_row), policy=policy,
                         read_pdf=NONE_READER, find_structured_strings=lambda t: (),
                         now=NOW, context_window=40)
    assert result.run["completeness"] == "unsupported"
    assert result.run["observation_count"] == 0


def test_a_docx_with_no_reader_is_unsupported_not_failed(file_row, policy):
    result = extract_docx(file_row=file_row, path=_path(file_row), policy=policy,
                          read_docx=NONE_READER, find_structured_strings=lambda t: (),
                          now=NOW, context_window=40)
    assert result.run["completeness"] == "unsupported"


def test_an_archive_with_no_reader_is_unsupported_not_failed(file_row, policy):
    result = extract_archive(file_row=file_row, path=_path(file_row), policy=policy,
                             read_manifest=NONE_READER,
                             recognize_markers=lambda names: (),
                             now=NOW, context_window=40)
    assert result.run["completeness"] == "unsupported"


def test_an_image_with_no_reader_is_unsupported_not_failed(file_row, policy):
    result = extract_image(file_row=file_row, path=_path(file_row), policy=policy,
                           read_image=NONE_READER, dimension_signal=lambda w, h: None,
                           filename_pattern=lambda n: None,
                           now=NOW, context_window=40).extraction
    assert result.run["completeness"] == "unsupported"


def test_the_unsupported_run_names_the_extractor_that_has_no_reader(file_row, policy):
    """The run must not claim a DIFFERENT extractor ran.

    `unsupported_result` used to hardcode `text.structured`'s name and version,
    because that is the only family it served. Reused unchanged, a PDF with no
    reader would produce a run saying `text.structured` ran on it — one value with
    two meanings, and a §3.4 cache key built from a name that never ran.
    """
    from extractors import pdf

    result = extract_pdf(file_row=file_row, path=_path(file_row), policy=policy,
                         read_pdf=NONE_READER, find_structured_strings=lambda t: (),
                         now=NOW, context_window=40)
    assert result.run["extractor_name"] == pdf.EXTRACTOR_NAME
    assert result.run["extractor_version"] == pdf.VERSION
    assert result.run["source_type"] == pdf.SOURCE_TYPE


def test_structured_text_still_reports_unsupported_after_the_move(file_row, policy):
    """The two families that already worked keep working, under their own names."""
    from extractors import structured_text

    result = extract_structured_text(
        file_row=file_row, path=_path(file_row), policy=policy,
        source_type="text_document", read_text_document=NONE_READER,
        find_structured_strings=lambda t: (), now=NOW, context_window=40)
    assert result.run["completeness"] == "unsupported"
    assert result.run["extractor_name"] == structured_text.EXTRACTOR_NAME

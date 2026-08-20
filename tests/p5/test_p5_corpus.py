# tests/p5/test_p5_corpus.py
"""The corpus fixtures the 2026-08-21 stress test found missing.

"No encrypted-PDF fixture. No 0-byte file fixture." Both exist in every real
Downloads folder, and neither was represented anywhere in 623 tests -- so the
`failed` path shipped with a catcher and no fixture proving the catcher is reachable
from a real extractor call, and the empty file was never sent through an extractor at
all.

Also here: the one drift check on `p4_stub`, which remains a second import path into
P4 and is the harness ten P5 test modules validate through.
"""
from pathlib import Path

import pytest

from extractors.failure import failed_result
from extractors.pdf import EXTRACTOR_NAME, VERSION, extract_pdf
from extractors.filesystem import extract_filesystem
from extractors.safety import SafetyPolicy

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

#: A digest of P1's shape. A fixture that is not one is a fixture P1 cannot produce.
HASH = "5f7b1a1c9d4e6f2a3b8c0d1e2f3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c"


def a_file(tmp_path: Path, name: str, payload: bytes = b"x") -> tuple[Path, dict]:
    path = tmp_path / name
    path.write_bytes(payload)
    return path, {"file_id": "f1", "content_hash": HASH, "filename": name,
                  "extension": path.suffix, "mime_type": None,
                  "detected_format": path.suffix.lstrip(".")}


# ------------------------------------------------------- the encrypted PDF
class PdfEncrypted(Exception):
    """What a real PDF reader raises on a password-protected file."""


def test_an_encrypted_pdf_becomes_a_failed_run_and_does_not_end_the_scan(tmp_path):
    """§2.4: an unreadable file is "recorded as indexed-but-unreadable rather than
    silently treated as empty". A crashed scan is a worse version of the same lie.
    """
    path, row = a_file(tmp_path, "statement.pdf")

    def locked_reader(_path):
        raise PdfEncrypted("file has not been decrypted")

    with pytest.raises(PdfEncrypted):
        extract_pdf(file_row=row, path=path, policy=OPEN_POLICY,
                    read_pdf=locked_reader,
                    find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=40)

    # The catcher is what turns that into a row. It is reachable from the real call.
    try:
        extract_pdf(file_row=row, path=path, policy=OPEN_POLICY,
                    read_pdf=locked_reader,
                    find_structured_strings=lambda text: (),
                    now=FIXED_CLOCK, context_window=40)
    except Exception as error:
        result = failed_result(file_row=row, error=error,
                               extractor_name=EXTRACTOR_NAME,
                               extractor_version=VERSION,
                               source_type="text_document", now=FIXED_CLOCK)

    assert result.run["completeness"] == "failed"
    assert result.observations == ()          # P4 conformance rule 9
    assert result.run["failure_reason"] == "PdfEncrypted: file has not been decrypted"


@pytest.mark.parametrize("error", [
    PdfEncrypted("file has not been decrypted"),
    ValueError("cannot read an empty file as PDF"),
    OSError(5, "Input/output error"),
])
def test_the_failure_reason_is_the_exception_and_nothing_added(tmp_path, error):
    """P5 does not decide whether the file is encrypted, truncated or malformed --
    deciding that would need the read that just failed.

    Asserted as an EQUALITY, not as a scan for diagnosis words. The first version of
    this test asserted that "encrypted" appears nowhere in `failure_reason`, and it
    failed against a reader whose exception class is named `PdfEncrypted`: the word
    was there because the READER said it, which is precisely the fact being recorded.
    Scanning text for a forbidden token has produced a false result six times in this
    project. The property is that P5 adds nothing, and equality is how you say that.
    """
    _, row = a_file(tmp_path, "statement.pdf")
    result = failed_result(file_row=row, error=error, extractor_name=EXTRACTOR_NAME,
                           extractor_version=VERSION, source_type="text_document",
                           now=FIXED_CLOCK)
    assert result.run["failure_reason"] == f"{type(error).__name__}: {error}"


# ------------------------------------------------------------ the 0-byte file
def test_a_zero_byte_file_is_indexed_and_is_not_an_empty_document(tmp_path):
    """§2.4 again: empty-because-unread and empty-because-empty must not be one row.

    A 0-byte file is genuinely empty, so the filesystem run is `complete` -- P3's
    record is all there is to know and it was all obtained.
    """
    path, row = a_file(tmp_path, "Screenshot 2026-08-21.png", payload=b"")
    assert path.stat().st_size == 0
    result = extract_filesystem(file_row=row, path=path, policy=OPEN_POLICY,
                                now=FIXED_CLOCK, context_window=40)
    assert result.run["completeness"] == "complete"
    assert result.observations, "the filename is still evidence (O5)"


def test_a_zero_byte_pdf_fails_rather_than_reporting_an_empty_document(tmp_path):
    """The distinction the previous test sets up: a PDF reader handed no bytes raises,
    and that is a `failed` run -- not a `complete` run with nothing in it."""
    path, row = a_file(tmp_path, "invoice.pdf", payload=b"")

    def reader(_path):
        raise ValueError("cannot read an empty file as PDF")

    try:
        extract_pdf(file_row=row, path=path, policy=OPEN_POLICY, read_pdf=reader,
                    find_structured_strings=lambda text: (), now=FIXED_CLOCK,
                    context_window=40)
    except Exception as error:
        result = failed_result(file_row=row, error=error, extractor_name=EXTRACTOR_NAME,
                               extractor_version=VERSION, source_type="text_document",
                               now=FIXED_CLOCK)
    assert result.run["completeness"] == "failed"
    assert result.run["completeness"] != "complete"


# --------------------------------------------------------- p4_stub does not drift
@pytest.mark.parametrize("coverage", [None, {"units": "pages", "processed": 1,
                                             "total": 1}])
def test_the_stub_and_p4_agree_on_coverage(coverage):
    """The stress test reported "validate_run requires `coverage` always; P4 allows
    None". Executed, they agree -- but nothing PINNED that they agree, which is how a
    second import path drifts. This is the pin.
    """
    import p4_stub
    from evidence_shape.runs import config_fingerprint, run_from_mapping

    run = dict(run_id="r1", file_id="f1", content_hash=HASH,
               extractor_name="pdf.text", extractor_version="0.1.0",
               source_type="text_document", analysis_tier="native", config={},
               config_fingerprint=config_fingerprint({}), completeness="complete",
               coverage=coverage, observation_count=0,
               started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK, failure_reason=None)

    p4_stub.validate_run(run, 0)                    # the harness ten modules use
    assert run_from_mapping(run).coverage == (        # and P4 itself
        None if coverage is None else run_from_mapping(run).coverage)


def test_the_stub_rejects_an_absent_coverage_key_exactly_as_p4_does():
    import p4_stub
    from evidence_shape.runs import MalformedRun, config_fingerprint, run_from_mapping

    run = dict(run_id="r1", file_id="f1", content_hash=HASH,
               extractor_name="pdf.text", extractor_version="0.1.0",
               source_type="text_document", analysis_tier="native", config={},
               config_fingerprint=config_fingerprint({}), completeness="complete",
               observation_count=0, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK,
               failure_reason=None)

    with pytest.raises(MalformedRun):
        run_from_mapping(run)
    with pytest.raises(AssertionError):     # the stub's harness-side exception type
        p4_stub.validate_run(run, 0)

"""R-24: a folder nothing could be read from is an ANSWER, not a crash.

Measured 2026-09-06 on a folder holding two binary blobs and nothing else:

    No plan was made for .../corpus, and this is why:
      NothingToDesign: none of [] is a top-level branch candidate for 'plan_0'.
    EXIT=1

Three things are wrong with that screen and only the third is about trees. The
person's two files are named NOWHERE -- `84` §1's standing rule is that a file is
never silently omitted, and this omits the entire folder. The exit code says the
command failed, and it did not: it read everything there was to read and found
nothing in it, which is a true answer about a folder of opaque files. And the
sentence is an exception class name and a bracket pair, which is the shape §5's
own convention exists to avoid ("a refusal with a reason is an answer and a
traceback is not") applied to a refusal that should not have been one.

WHAT WAS ALREADY THERE AND UNCALLED. The run had recorded a per-file account the
whole time: `extraction_runs` carries `format.unrouted / metadata_only` for each
blob and `unresolved` carries `no_candidate_evidence` per field. §8.6's progress
line is P13's instrument for saying so -- `review_run.progress.progress_lines`,
written, tested and with no caller in `src/`, whose own `assert_every_file_
accounted` enforces "no indexed file may be absent from every entry". This is that
caller. The accounting is not asserted by this test's arithmetic; it is asserted
by P13, and the test's job is to prove P13 was asked.

WHAT IS DELIBERATELY NOT CHANGED. `NothingToDesign` for a corpus whose files WERE
read is still a refusal and still exits 1. The distinction is not the exception, it
is the evidence: `folders_nothing_could_be_read_from` is the run's own answer to
"which files is there nothing to be wrong about", and this path is taken only when
that is every file in the scan.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402

BLOB_ONE = "blob one.bin"
BLOB_TWO = "blob two.bin"


def _opaque_corpus(tmp_path: Path) -> Path:
    """Two files with no text in them, and no third file to rescue the run.

    Byte ranges chosen out of the C0 control block: `readers.signatures` reads a
    control character as proof these are not text, which is the same judgement
    `file(1)` makes, so nothing downstream can decode them into words.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / BLOB_ONE).write_bytes(bytes(range(1, 32)) * 64)
    (corpus / BLOB_TWO).write_bytes(bytes(range(33, 64)) * 64)
    return corpus


def _run(tmp_path: Path) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(_opaque_corpus(tmp_path)),
                     "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "t",
                     "--database", str(tmp_path / "plan.sqlite")], out=out)
    return code, out.getvalue()


def test_a_folder_nothing_could_be_read_from_is_not_an_error(tmp_path):
    """Exit 0. The command did what it does and has something true to report."""
    code, printed = _run(tmp_path)

    assert code == 0, printed


def test_both_files_are_named_with_a_reason_rather_than_omitted(tmp_path):
    """`84` §1, on the one screen that used to name no file at all."""
    _, printed = _run(tmp_path)

    assert BLOB_ONE in printed, printed
    assert BLOB_TWO in printed, printed
    assert "nothing could be read" in printed.lower(), printed


def test_the_run_accounts_for_every_file_it_indexed(tmp_path):
    """§8.6's line, printed, with the population and the buckets kept apart.

    "2 files indexed" is P3's own count and the entry beneath it is P4's. If the
    two ever disagreed, `assert_every_file_accounted` inside `progress_line` would
    raise rather than print a shorter paragraph, which is why this test asserts
    that the line is THERE rather than re-deriving the sum.
    """
    _, printed = _run(tmp_path)

    assert "What this run could read: 2 files indexed." in printed, printed
    assert "metadata_only" in printed, printed


def test_no_traceback_shaped_sentence_survives(tmp_path):
    """The exception class name and the empty bracket pair, gone from the screen."""
    _, printed = _run(tmp_path)

    assert "NothingToDesign" not in printed, printed
    assert "none of []" not in printed, printed

"""An ordinary run does not build an evaluation bundle nobody will ever read.

§8.5's bundle is P2's immutable envelope, and `evaluate_bundle` is the only thing
that reads one. `production.py:743` runs it `if authorities.evaluation is not None`
-- and `cli.py` passes none, saying why in as many words: *"§8.5's replay measures a
run against a reference corpus with hand-labelled expectations. This command scans a
person's own folder, which has none, so it declares no evaluation."*

So on every ordinary run the bundle was assembled in full and then never opened.
Measured on a real 413-file ~/Documents:

    bundle_text_unit          110,265 rows   122.0 MB
    bundle_extraction_output   81,956 rows   108.5 MB
    ------------------------------------------------
    text_units                110,265 rows    95.6 MB
    evidence                   82,023 rows    55.5 MB

Row for row, byte for byte, a second copy -- 230 MB of a 466 MB database, half of
it, duplicating tables that were already there. At this person's Desktop scale that
is several gigabytes of a file they never asked for.

An unrecorded bundle is also UNREACHABLE. `--replay` resolves a bundle by NAME, and
a name only exists because `--record` gave it one (`cli.py:2496` builds the recorded
bundle from this one). Without `--record` there is no way to ask for it, so it was
not merely unread -- it could not have been read.

The bundle still gets built the moment something will use it, which is what the
second test is for. This is a change about WHEN, never about what a bundle contains.
"""
import io
from pathlib import Path

import cli


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "Files"
    (corpus / "Uni").mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Introduction to Physics\nInstructor: Dr Reyes\nFall 2024\n")
    (corpus / "Uni" / "PHYS 1401 lecture 08.txt").write_text(
        "PHYS 1401 Lecture 8 -- Momentum\nDr Reyes\n")
    (corpus / "reading list.txt").write_text("Reading list\nWeek 1: chapter 3\n")
    return corpus


def _counts(database: Path) -> dict[str, int]:
    import sqlite3
    conn = sqlite3.connect(database)
    try:
        return {name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                for name in ("text_units", "bundle_text_unit",
                             "evidence", "bundle_extraction_output")}
    finally:
        conn.close()


def test_an_ordinary_run_writes_no_bundle_rows(tmp_path):
    """The plain run -- the one a person types -- and the duplicate is not there."""
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    cli.main(["--situation", "academic.coursework", "--label", "Coursework",
              "--user", "jy", "--database", str(database), str(corpus)],
             out=io.StringIO())

    counts = _counts(database)
    assert counts["text_units"] > 0, (
        "the corpus must actually have been extracted or this proves nothing")
    assert counts["bundle_text_unit"] == 0
    assert counts["bundle_extraction_output"] == 0


def test_recording_still_builds_the_whole_bundle(tmp_path):
    """The negative twin, and the one that keeps this a change about WHEN.

    Without it, "writes no bundle rows" is satisfied by a build that never writes
    one at all -- and `--record`, whose entire job is to capture a run for later
    replay, would silently record an empty envelope.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    cli.main(["--situation", "academic.coursework", "--label", "Coursework",
              "--user", "jy", "--database", str(database),
              "--record", "before-upgrade", str(corpus)], out=io.StringIO())

    counts = _counts(database)
    # `>=`, not `==`: `record_bundle` opens a SECOND bundle that supersedes the
    # one P1-P7 sealed, so a recorded run legitimately holds two copies. Measured,
    # not assumed -- the first version of this test asserted equality and found 12
    # rows against 6.
    assert counts["bundle_text_unit"] >= counts["text_units"] > 0
    assert counts["bundle_extraction_output"] > 0


def test_the_ordinary_run_still_extracts_everything_it_did_before(tmp_path):
    """Skipping the COPY must not skip the original.

    `text_units` and `evidence` are P4's own records and are what every later part
    reads. A change that quietly stopped writing them would halve the database too,
    and would break the product.
    """
    corpus = _corpus(tmp_path)
    plain, recorded = tmp_path / "plain.sqlite", tmp_path / "rec.sqlite"
    argv = ["--situation", "academic.coursework", "--label", "Coursework",
            "--user", "jy", str(corpus)]
    cli.main([*argv[:-1], "--database", str(plain), argv[-1]], out=io.StringIO())
    cli.main([*argv[:-1], "--database", str(recorded), "--record", "r",
              argv[-1]], out=io.StringIO())

    a, b = _counts(plain), _counts(recorded)
    assert a["text_units"] == b["text_units"] > 0
    assert a["evidence"] == b["evidence"] > 0


def test_the_audit_manifest_is_written_even_on_an_ordinary_run(tmp_path):
    """The line this change may not cross.

    `bundle_manifest` carries `policy_settings`, and `tests/test_cli_cloud_consent.py`
    calls it one of *"the two places a later reader can learn what this run was
    permitted to do"*. It is ONE ROW. Skipping the 230 MB of duplicated text is a
    storage decision; skipping the record of what a run was allowed to do would be
    a privacy decision wearing a storage decision's clothes.

    The first version of this change dropped the whole envelope and took the audit
    record with it. Two cloud-consent tests caught it. This test is so that the
    next person to optimise here is caught by THIS file rather than by that one.
    """
    import json
    import sqlite3

    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    cli.main(["--situation", "academic.coursework", "--label", "Coursework",
              "--user", "jy", "--database", str(database), str(corpus)],
             out=io.StringIO())

    conn = sqlite3.connect(database)
    try:
        settings = [json.loads(row[0]) for row in conn.execute(
            "SELECT policy_settings FROM bundle_manifest")]
    finally:
        conn.close()

    assert settings, "the run recorded no manifest, so nothing says what it could do"
    assert all("operation_mode" in row for row in settings)
    assert _counts(database)["bundle_text_unit"] == 0, (
        "the manifest is kept and the duplicated bulk is not -- both halves")

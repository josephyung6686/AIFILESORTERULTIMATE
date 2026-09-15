# tests/integration/test_the_gist.py
"""The gist: what the scan found, said before anything has been judged.

`00` "Amendments of 2026-09-14" item 2, the owner's own words: *"after we parse
files we have a gist of what files they have; then we go directly into a proposed
file structure"*. This file pins the first beat -- the second is
`test_the_editable_structure`.

**THE DEPLOYMENT IS THE ONE THE OWNER CHOSE** (`104` §18.61): cloud only, no local
model, `readers.model_routing.deepseek_invoke` replaced by a recorder, so the
gate, the route, the transport and the whole of `cli.run` are the production
path. **THE CORPUS IS THE ELEVEN-FILE SYNTHETIC ONE** its sibling
`test_the_question_at_the_end_and_the_sort` authors -- six coursework files in the
folder root, three of a student society's records in a subfolder, and two the
rules hold. Nothing here reads the owner's disk.

**WHAT IS BEING PINNED.** The block prints the moment the scan finishes and above
every block reporting what a model made of these files; its kinds partition the
roster and the arithmetic is on the screen; the folders are named the way a person
reads them off their own disk; and **a protected file is inside the count on its
kind's line and named on none of them** -- `planning/93` and `00`:201, asked at the
one place they had never been asked, which is the first screen that lists
somebody's filenames.

**AND AGAIN AT THE END, with the judge's kinds in it.** The block at the top is
the rules alone because that is all that exists before the passes. Measured on
this corpus: the rules read three files as `Business operations` and named three
others not at all; the cloud judge then names the society's folder `Nonprofit,
civic and member organisations` and one more file `Academic`, so the second block
differs and is printed. A run whose judge changed nothing prints it once.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402

# The corpus, the cloud stub and the two held files, imported rather than
# rewritten: one synthetic disk described in one place, on the rule
# `test_the_question_at_the_end_and_the_sort` states for the stub it shares with
# its own siblings.
from test_the_question_at_the_end_and_the_sort import (
    dark_level_stage,  # noqa: E402
    CLUB, ENV, LABEL, SITUATION, _Cloud, _corpus, _on_disk,
)

#: The two headings, which are what a person looks for on the screen.
GIST = "What you have:"
JUDGED = "What you have, once it was looked at:"

#: Every file on the synthetic disk, stated here rather than computed the way the
#: product computes it: a sum checked against the product's own arithmetic proves
#: only that the product agrees with itself.
FILES = 11


def block(report: str, heading: str) -> list[str]:
    """The lines under one heading, up to the next blank line.

    Read off the SCREEN and not off an object. A block that counts correctly into
    a variable nobody shows is the defect this amendment exists to close.
    """
    lines = report.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(heading):
            found = []
            for rest in lines[index + 1:]:
                if not rest.strip():
                    break
                found.append(rest)
            return found
    raise AssertionError(f"the run printed no {heading!r} block:\n{report}")


def one_run(root: Path):
    """One run of the eleven-file corpus on the owner's deployment."""
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    before = _on_disk(corpus)
    cloud = _Cloud()
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", root / "absent.env")
        for name, value in ENV.items():
            patch.setenv(name, value)
        patch.setattr(model_routing, "deepseek_invoke", cloud.factory)
        dark_level_stage(patch)
        code = cli.main(
            [str(corpus), "--situation", SITUATION, "--label", LABEL,
             "--user", "t", "--database", str(database), "--enable-cloud",
             "--accept-groups"], out=out)
    said = out.getvalue()
    assert code == 0, said
    return {"corpus": corpus, "database": database, "said": said,
            "before": before, "after": _on_disk(corpus)}


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    return one_run(tmp_path_factory.mktemp("the_gist"))


def _kind_lines(said: str, heading: str) -> list[str]:
    """One line per kind. The examples and folders under a kind are indented six
    and the two tails -- protected, nothing to read -- two, so these are exactly
    the lines that partition the roster."""
    return [line.strip() for line in block(said, heading)
            if line.startswith("    ") and not line.startswith("      ")]


def test_the_gist_is_printed_above_everything_a_model_said(run):
    """The owner's sentence is an ORDER -- parse, the gist, a proposed structure,
    then filing -- and a gist under the judge's verdicts would be the product
    saying what it found after it had said what it concluded."""
    said = run["said"]
    assert GIST in said, said
    for later in ("What may be sent:", "Situations from a model:", "Coverage:"):
        assert later in said, said
        assert said.index(GIST) < said.index(later), later


def test_the_kinds_add_up_to_the_corpus(run):
    """The coverage block's own rule one stage earlier: a block that sums has to
    sum ON THE SCREEN, because a person cannot check a number they would have to
    add up themselves."""
    said = run["said"]
    heading = [line for line in said.splitlines() if line.startswith(GIST)][0]
    assert heading.strip() == f"What you have: {FILES} files."
    kinds = _kind_lines(said, GIST)
    assert kinds, said
    assert sum(int(line.split()[0]) for line in kinds) == FILES, kinds


def test_no_kind_names_more_than_three_files(run):
    """"Up to three example filenames per kind" -- the owner's own number. A gist
    is what a person reads to decide whether the product has understood their
    folder; three names settle that where a count does not and forty would bury
    it."""
    for line in block(run["said"], GIST):
        if line.strip().startswith("for example:"):
            named = line.strip()[len("for example:"):]
            assert named.count(",") <= 2, line


def test_the_gist_names_no_protected_file(run):
    """`planning/93` and `00`:201, on the first screen of the run.

    The files the rules hold are inside the counts and on none of the example
    lines: marked, counted, never named.
    """
    conn = sqlite3.connect(f"file:{run['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        held = cli._protected_file_ids(conn)
        names = {row["file_id"]: row["filename"]
                 for row in conn.execute("SELECT file_id, filename FROM files")}
    finally:
        conn.close()
    assert held, "this corpus is meant to hold two files"
    for heading in (GIST, JUDGED):
        said = "\n".join(block(run["said"], heading))
        for file_id in held:
            assert names[file_id] not in said, (heading, names[file_id], said)
        assert f"{len(held)} of them are protected" in said, said


def test_the_gist_says_which_folders_the_files_sit_in(run):
    """A gist that said what was found and not where it was would leave a person
    unable to check it against their own disk. The society's own subfolder is
    named, and the corpus root in words rather than as `.`."""
    said = "\n".join(block(run["said"], GIST))
    assert CLUB in said, said
    assert "the folder you scanned" in said, said


def test_the_gist_is_printed_again_with_the_judges_kinds(run):
    """`00` amendment 2's block twice: the rules first, the judge after.

    It differs on this corpus and that is the point -- the second block is what
    the run LEARNED. It still adds up to the same roster, because what changed is
    which line a file is on and never how many files there are.
    """
    said = run["said"]
    assert JUDGED in said, said
    assert said.index(GIST) < said.index(JUDGED)
    assert _kind_lines(said, JUDGED) != _kind_lines(said, GIST)
    assert sum(int(line.split()[0])
               for line in _kind_lines(said, JUDGED)) == FILES


def test_a_gist_the_judge_did_not_change_is_printed_once(tmp_path):
    """The block is reprinted only when it differs.

    A run with no model at all learns nothing between the two, and a block
    repeated word for word tells a person their run did something when it did
    not. Measured by running the same corpus with the cloud OFF.
    """
    corpus = _corpus(tmp_path)
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
        cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                  "--user", "t",
                  "--database", str(tmp_path / "holder" / "plan.sqlite"),
                  "--accept-groups"], out=out)
    said = out.getvalue()
    assert GIST in said, said
    assert JUDGED not in said, said


def test_a_file_nothing_could_be_read_out_of_is_counted_and_said(tmp_path):
    """The gist's other tail, and it needs a corpus the eleven-file one is not.

    Every file on that disk has text in it, so this line had never been printed
    by any run measured here. A picture with no words is the ordinary case the
    owner's amendment 5 of 13 Sep is about -- "a capture with no words is its
    kind" -- and it is the one file a person most needs told about, because
    nothing was read and the kind came from the file itself.

    Measured against the COVERAGE block on the same screen: that block counts one
    `unreadable`, and two blocks on one screen disagreeing about the same file is
    the defect the coverage sum exists to make impossible.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "snapshot.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t",
                         "--database", str(tmp_path / "holder" / "plan.sqlite"),
                         "--accept-groups"], out=out)
    said = out.getvalue()
    assert code == 0, said
    assert "1 of them had nothing to read" in said, said
    assert "    1 unreadable" in said, said


def test_the_gist_moves_no_file(run):
    """It is a screen. `--freeze` and `--apply` are what move files, and neither
    was typed, so the corpus is byte for byte what it was."""
    assert run["after"] == run["before"]

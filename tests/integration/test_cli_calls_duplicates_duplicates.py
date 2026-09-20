"""`104` R-K: two files with the same bytes are called that on the screen.

Measured on a 52-file corpus: four `(1)` twins -- a lecture PDF, a résumé, a photo
and a lab report -- each got an independent, identical decision, and no line of
the report said "same file as". The record knew: `duplicate_family` is a universal
fact (`00`:25/32, resolution G5), both members carry the same value, and P9's
`duplicate_or_version` reads it to type an edge. Only the person was not told.

`00`:128 is why this is a SENTENCE and not a gesture: the product "must never
delete or automatically expire" a file, and "may use ... duplicate status ... to
surface review suggestions, but it must not delete files, mark them disposable, or
move them out of a protected area without explicit user action." So the screen
says which files are the same bytes, says keeping one is probably what the person
wants, and says plainly that nothing here removes either.
"""
from __future__ import annotations

import io
import shutil
from pathlib import Path

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"

BODY = ("PHYS 1401 Lecture 05 - Newton's Laws\nSpring 2026\n"
        "Force equals mass times acceleration.\n")


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / "Lecture 05.txt").write_text(BODY)
    # THE SAME BYTES under a second name, which is what a browser's second
    # download of one file leaves behind and what the corpus that found this had.
    shutil.copyfile(corpus / "Lecture 05.txt", corpus / "Lecture 05 (1).txt")
    (corpus / "Lecture 06.txt").write_text(
        "PHYS 1401 Lecture 06 - Work and Energy\nSpring 2026\nWork is force "
        "times distance.\n")
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "jy", "--database", str(database),
                     "--accept-groups", *extra],
                    out=out)
    return code, out.getvalue()


def test_two_files_with_the_same_bytes_are_named_as_such(tmp_path):
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    flat = " ".join(report.split())
    assert "same bytes" in flat, report
    assert "Lecture 05.txt" in flat and "Lecture 05 (1).txt" in flat, report


def test_the_screen_proposes_keeping_one_and_promises_to_delete_neither(tmp_path):
    """`00`:128: a suggestion, and never a deletion.

    Both halves are asserted, because the first without the second is the
    product proposing something it will not do, and the second without the first
    is the silence this replaces.
    """
    corpus = _corpus(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    flat = " ".join(report.split())
    assert "Keeping one is probably what you want" in flat, report
    assert "nothing here deletes either" in flat, report


def test_a_file_with_no_twin_is_not_called_a_duplicate(tmp_path):
    """The negative twin: the sentence fires on the bytes, not on the name."""
    corpus = _corpus(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    lines = [line for line in report.splitlines()
             if "same bytes" in line and "Lecture 06.txt" in line]
    assert lines == [], report


def test_a_duplicate_pair_that_is_protected_is_still_not_named(tmp_path):
    """The blind spot this fix could have opened, closed by construction.

    A duplicate sentence is a sentence with filenames in it, and the owner ruled
    on 2026-09-02 that a protected file's name is not printed unless it is asked
    for (`93-PROTECTED-DISCLOSURE-RULING.md`). Two copies of somebody's passport
    are a duplicate family, and a line saying so by name would hand back exactly
    what `PROTECTED_SUMMARY` holds. The sentence reads the names this group
    PRINTED, which for a protected group is none of them.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee.\n")
    (corpus / "Passport scan.txt").write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Passport No. K12345678\nDate of birth: 1 January 1990\n")
    shutil.copyfile(corpus / "Passport scan.txt", corpus / "Passport copy.txt")

    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert "protected" in report.lower(), report
    assert "Passport scan.txt" not in report, report
    assert "same bytes" not in report, report

    # And with the names asked for, both the names and the sentence arrive.
    _, shown = _run(corpus, tmp_path / "holder" / "plan.sqlite",
                    "--show-protected")
    assert "Passport scan.txt" in shown, shown
    assert "same bytes" in shown, shown


def test_a_corpus_with_no_duplicates_says_nothing_about_them(tmp_path):
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee.\n")
    (corpus / "Lecture 05.txt").write_text(BODY)

    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert "same bytes" not in report, report


#: THREE copies, which is what a browser's third download leaves behind and what
#: the two-file fixture above could never produce. Found by running the product
#: on a mixed corpus rather than by reading it: the sentence is assembled once
#: and its prose was written for exactly two files.
def _three_copies(root: Path) -> Path:
    corpus = _corpus(root)
    shutil.copyfile(corpus / "Lecture 05.txt", corpus / "Lecture 05 (2).txt")
    return corpus


def test_three_files_with_the_same_bytes_are_not_called_two_documents(tmp_path):
    """`84` §6: what the screen tells a person has to be true.

    The sentence said "are the same bytes, not TWO documents ... nothing here
    deletes EITHER, and BOTH are filed the same way" over a list that is built by
    joining however many names share a digest. With three copies every one of
    those three words is false, and the person is reading a count that disagrees
    with the names printed immediately before it.

    SABOTAGE: restore the hardcoded "two ... either ... both". Red here, and the
    two-file test above stays green -- which is exactly why this went unnoticed.
    """
    corpus = _three_copies(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")
    flat = " ".join(report.split())

    assert "same bytes" in flat, report
    assert "not two documents" not in flat, (
        "three files were named and the sentence still says two: " + report)
    assert "deletes either" not in flat, report
    assert "and both are filed" not in flat, report


def test_the_three_are_named_as_a_list_and_not_chained_with_and(tmp_path):
    """The other half of the same sentence, and the same cause.

    `' and '.join(...)` reads as "A and B" for two names and "A and B and C" for
    three. A person scanning a report for their own filename reads a list; the
    chain reads as a sentence that lost its commas.

    SABOTAGE: join with " and " again. The names are still all there, so nothing
    else fails -- only a person's eye does.
    """
    corpus = _three_copies(tmp_path)
    _, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")
    flat = " ".join(report.split())

    assert ("Lecture 05 (1).txt, Lecture 05 (2).txt and Lecture 05.txt "
            "are the same bytes") in flat, (
        "three names should be listed, not chained with `and`: " + report)

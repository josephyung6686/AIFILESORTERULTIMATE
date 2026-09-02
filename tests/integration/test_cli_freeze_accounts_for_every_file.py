"""Add the two counts in the freeze block and get back the size of the folder.

`94` F22, as the person met it. Four files in one folder, and the block said:

    files in the folder : 4
    Frozen              : 2
    Not frozen          : 1
    ACCOUNTED FOR       : 3

`noextension` -- a plain text file with no extension -- was named nowhere in it.
Somebody counting their own files against that block finds one missing and has
nothing to search for, which is worse than an unhelpful reason because there is
no reason at all.

This test is the ARITHMETIC and not the number. It asserts that the two counts
the block prints sum to the number of files that went in, which is the property
that holds for any corpus; `tests/apply/test_freeze.py` proves the same property
against `freeze` over every outcome P11 publishes. Either one alone can be
satisfied without the property holding: the unit test would not see a file that
never became a decision at all, and this one would not see an outcome this
corpus happens not to reach.
"""
import io
import re
from pathlib import Path

import cli

#: The lead's corpus, and each file is in it for a reason. Two `.txt` naming one
#: course so that something is frozen and the sum is not trivially 0 + 4; a
#: `.docx` that no reader on this build opens; and the extensionless file that
#: `94` F22 was measured on -- `95` records that `readers/signatures.py` can
#: detect it by magic number and that `cli._detect_format` is not yet wired to
#: ask, so it arrives at the freeze unclassified. Whether it stays that way is
#: that work's business. Whether it is NAMED is this test's.
CORPUS = {
    "problem set 1.txt": "PHYS 1401 problem set 1\nMechanics homework, due "
                         "2024-02-10.\nStudent: jy\n",
    "problem set 2.txt": "PHYS 1401 problem set 2\nMechanics homework, due "
                         "2024-02-17.\nStudent: jy\n",
    "problem set 3.docx": "PHYS 1401 problem set 3\n",
    "noextension": "PHYS 1401 lab notes, and no extension on this "
                   "file.\nDue 2024-03-01.\n",
}

_FROZEN = re.compile(r"^Frozen: (\d+) file\(s\)", re.MULTILINE)
_HELD = re.compile(r"still exactly where they are -- (\d+) file\(s\)")


def _count(pattern: re.Pattern, text: str) -> int:
    """A block that is absent counts 0 -- which is the bug, when it is wrong."""
    found = pattern.search(text)
    return 0 if found is None else int(found.group(1))


def _freeze_block(text: str) -> str:
    """The screen this test is about, and not the run report above it.

    Scoped on purpose. `noextension` was named in the DECISIONS block all along
    -- "Waiting for you to say what these are" -- so a containment test against
    the whole output passes while the freeze block is still missing the file.
    Sabotage caught exactly that: the unscoped version of the test below was
    GREEN against the code that had the bug.
    """
    starts = [at for at in (text.find("\nFrozen: "),
                            text.find("\nNothing was frozen"))
              if at != -1]
    assert starts, f"the run printed no freeze block at all\n\n{text}"
    return text[min(starts):]


def _run(tmp_path: Path) -> str:
    corpus = tmp_path / "PHYS 1401"
    corpus.mkdir()
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)

    out = io.StringIO()
    cli.main(["--situation", "academic.coursework", "--label", "PHYS 1401",
              "--user", "jy", "--database", str(tmp_path / "plan.sqlite"),
              "--freeze", str(corpus)], out=out)
    return out.getvalue()


def test_the_freeze_block_accounts_for_every_file_that_went_in(tmp_path):
    text = _freeze_block(_run(tmp_path))
    frozen, held = _count(_FROZEN, text), _count(_HELD, text)

    assert frozen + held == len(CORPUS), (
        f"{len(CORPUS)} files went in; the freeze block accounts for "
        f"{frozen} + {held} = {frozen + held}\n\n{text}")
    # Not vacuous in either direction: a run that froze nothing would satisfy
    # the sum with one number, and so would one that froze everything.
    assert frozen and held


def test_the_file_with_no_extension_is_named_on_the_screen(tmp_path):
    """The count is the property; being able to FIND the file is the point.

    `84` §1 is marked AND counted. A person who reads "1 file is not frozen" and
    cannot tell which one has been told a true number and nothing they can act
    on. The one exception is protected material, which is counted and explained
    and deliberately not named -- there is none in this corpus, and
    `tests/apply/test_freeze_approval.py` is where that rule is proved.
    """
    assert "noextension" in _freeze_block(_run(tmp_path))

# tests/integration/test_a_folder_that_was_never_read.py
"""A folder whose every file was set aside is not a folder that said nothing.

**THE CASE, measured 21 Sep 2026.** A software project nested inside the folder
the person pointed at -- `README.md`, `package.json`, `Makefile`, `index.js` --
indexes zero files. That is still right: `package.json` makes that child a
project root, P3 leaves its descendants unread, and nobody wants that
repository reorganised. The `software project root descendant` verdicts are
written to `exclusion_verdicts`, so the database knows exactly what happened.

**THE SCAN ROOT, ruled 2026-09-30.** Pointing the tool at the project directory
itself reads that project's source files. A marker in the folder the person
named does not hide its siblings, and it does not hide the project's own
files when that project is the folder they named. The unread case this file
still owns is the nested one.

The SCREEN said something else:

    the folder was read and nothing in it said what kind of material it is: no
    file carries a kind-of-file word one situation owns, and the recogniser
    raised nothing about any of them.

Nothing was read. The recogniser was never asked about anything. The one
sentence the person gets blames the part of the product that never ran, and the
six files it skipped are named nowhere.

**WHY THE EXISTING GUARD DID NOT CATCH IT.** `cli._print_set_aside` exists for
precisely this -- its own comment reads *"a refused run that never said what it
had skipped is the silent omission the standing rule forbids"* -- and it is
placed early so that a later refusal cannot outrun it. But it sits at
`cli.py:20953` and this refusal is raised at `cli.py:19410`, fifteen hundred
lines upstream. The earliest refusal in the run is upstream of the block that
exists to make refusals honest.

So the fix is at the refusal: an empty roster is a different case from a vote
that named nothing, and it has to say so itself.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402


def _a_software_project(root: Path) -> Path:
    """A project nested in the folder a person would point the tool at."""
    corpus = root / "downloads" / "widget-kit"
    corpus.mkdir(parents=True)
    (corpus / "package.json").write_text(
        '{"name":"widget-kit","version":"1.4.0","dependencies":{"tslib":"^2.6.0"}}')
    (corpus / "README.md").write_text("# widget-kit\nA library for laying out widgets.\n")
    (corpus / "index.js").write_text("export function layout(c, items) { return items; }\n")
    (corpus / "Makefile").write_text("build:\n\tnpm run build\n")
    return corpus


def _run(corpus: Path, database: Path) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "t", "--database", str(database)],
                    out=out)
    return code, out.getvalue()


def test_a_folder_of_nothing_but_a_project_says_so_and_does_not_blame_the_recogniser(
        tmp_path):
    """The whole finding, as one assertion each way.

    SABOTAGE: delete the empty-roster branch from `_the_corpus_names_a_schema`.
    The run refuses with the vote's sentence again, and the first assertion goes
    red on a folder where no vote was ever taken.
    """
    project = _a_software_project(tmp_path)
    # The parent is what the person pointed at. The project is a child of it,
    # so its descendants stay unread. The plan file sits beside that parent.
    code, said = _run(project.parent, tmp_path / "plan.sqlite")
    said = " ".join(said.split())

    assert code != 0, "a run that indexed nothing reported success"
    # WHAT IT MUST SAY: that nothing was read, and why.
    assert "set aside" in said, said[-600:]
    assert "software project root descendant" in said, said[-600:]
    # AND WHAT IT MUST NOT: the recogniser did not run, so it cannot be the
    # reason. This is the half that was false, and the half a person acts on --
    # somebody told the recogniser raised nothing goes looking for better
    # filenames, when what they need is to scan somewhere that is not a project.
    assert "the recogniser raised nothing" not in said, said[-600:]
    assert "the folder was read and nothing in it" not in said, said[-600:]


def test_pointing_at_the_project_itself_reads_its_source_files(tmp_path):
    """A marker in the folder the person named does not make that folder unread.

    Ruled 2026-09-30. The nested case above is what stays set aside.
    """
    project = _a_software_project(tmp_path)
    code, said = _run(project, tmp_path / "plan-at.sqlite")
    said = " ".join(said.split())

    assert "software project root descendant" not in said, said[-600:]
    assert "index.js" in said, said[-600:]
    assert code != 0


def test_a_folder_with_files_in_it_still_gets_the_vote_s_own_sentence(tmp_path):
    """THE NEGATIVE TWIN, and without it the line above is satisfied by deleting
    the message rather than by correcting it.

    A folder the product COULD read, whose files name no schema any situation is
    carried for, is the case the original sentence was written for and it is
    still true of it: those files were read, and they said nothing.
    """
    corpus = tmp_path / "loose"
    corpus.mkdir()
    (corpus / "a.txt").write_text("qqqq wwww eeee rrrr\n")
    (corpus / "b.txt").write_text("tttt yyyy uuuu iiii\n")

    code, said = _run(corpus, tmp_path / "plan2.sqlite")
    said = " ".join(said.split())

    assert code != 0, said[-400:]
    assert "the folder was read and nothing in it said what kind of material" in said, (
        said[-600:])
    assert "set aside" not in said, said[-600:]

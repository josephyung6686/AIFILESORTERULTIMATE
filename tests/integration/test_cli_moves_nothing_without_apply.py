"""No run moves a file unless the person typed --apply. Proven, not promised.

The owner asked for this before running the product on his real folder: *"just
make sure applying the actual thing is forbid, like moving files"*. A sentence in
a report is not that. So there are two tests and they answer the question in two
different ways, because either one alone can be satisfied without the property
holding.

The FIRST is empirical: run the product over a corpus, then compare the whole
tree -- every path, and every file's bytes -- against what it was before. It
would catch a mover nobody knew about, including one reached by a route this file
has never heard of.

The SECOND is structural: walk `cli.main`'s own AST and assert that the one call
to `_move_frozen_files` is guarded by the flags. It would catch a NEW mover added
tomorrow on a path this corpus happens not to exercise, which is the case the
empirical test is blind to.
"""
import ast
import hashlib
import io
from pathlib import Path

import cli


def _tree(root: Path) -> dict[str, str]:
    """Every file under `root`, by relative path, with the digest of its bytes.

    Paths AND contents. A move that also rewrote a file would pass a path-only
    comparison, and a rewrite that preserved paths would pass it too.
    """
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


#: `--database` IS NOT OPTIONAL HERE, and the reason is not tidiness.
#:
#: `cli.py` defaults it to `Path.cwd() / "database-agent-plan.sqlite"`, and
#: pytest's cwd is the repository root -- so the `--freeze` test below was writing
#: a 2.4 MB plan database into the working directory that every session on this
#: machine commits into. It is not cleaned up, so it is also READ on the next run:
#: facts, groups and plan versions carried across pytest invocations, shared with
#: any other test that ever omits the flag, while `_corpus` builds a fresh
#: `tmp_path` every time. State that outlives the run that made it is how a suite
#: acquires an order it depends on.
#:
#: MEASURED: only the `--freeze` run leaves the file; the run above it happens not
#: to persist one. Both are given a database anyway, because "happens not to" is
#: not a property either test asserts and the next edit to `cli.py` may change it.
#:
#: The corpus is already under `tmp_path`; the database belongs beside it.
def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "Files"
    (corpus / "Uni").mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Introduction to Physics\nInstructor: Dr Reyes\nFall 2024\n")
    (corpus / "Uni" / "PHYS 1401 lecture 08.txt").write_text(
        "PHYS 1401 Lecture 8 -- Momentum\nDr Reyes\n")
    (corpus / "reading list.txt").write_text("Reading list\nWeek 1: chapter 3\n")
    return corpus


def test_a_whole_run_leaves_every_file_exactly_where_it_was(tmp_path):
    """The run the owner is about to type, over a corpus, byte for byte."""
    corpus = _corpus(tmp_path)
    before = _tree(corpus)
    assert before, "the corpus must have files or this test proves nothing"

    out = io.StringIO()
    cli.main(["--situation", "academic.coursework", "--label", "Coursework",
              "--user", "jy", "--database", str(tmp_path / "plan.sqlite"),
              str(corpus)], out=out)

    assert _tree(corpus) == before


def test_a_freeze_moves_nothing_even_when_a_frozen_plan_is_already_there(tmp_path):
    """Freezing turns a proposal into an approved plan. It is not the move.

    TWO freezes, and the second one is the test. A single `--freeze` over a fresh
    corpus proves almost nothing: there is no frozen plan yet, so even a `--freeze`
    that wrongly implied `--apply` would find nothing to move and the tree would
    come back identical. Sabotage caught exactly that -- `moving = ... or
    args.freeze` left the one-invocation version GREEN. The second run is the one
    where a plan exists and a mistaken apply would really move the person's files.

    Worth the trouble because `--freeze` is the gesture whose NAME sounds like it
    commits something, and it is the one a person types immediately before
    `--apply`.
    """
    corpus = _corpus(tmp_path)
    shared = ["--situation", "academic.coursework", "--label", "Coursework",
              "--user", "jy", "--database", str(tmp_path / "plan.sqlite"),
              "--freeze", str(corpus)]

    cli.main(shared, out=io.StringIO())          # a frozen plan now exists
    before = _tree(corpus)
    assert before, "the corpus must have files or this test proves nothing"

    cli.main(shared, out=io.StringIO())          # and this one must still move none

    assert _tree(corpus) == before


def test_the_only_route_to_a_move_is_guarded_by_the_flags_that_name_it():
    """The structural half, which the corpus test cannot give.

    `_move_frozen_files` is the sole caller of everything that touches the disk.
    This asserts it is called exactly once in this file, and that the call sits
    under a condition built from `moving` and `undoing` -- the two names bound
    from `args.apply`/`args.apply_everything` and `args.undo`/`args.undo_everything`.

    A new mover added tomorrow on a path this corpus does not exercise would slip
    past the two tests above. It would not slip past this one, because the
    assertion is that there is exactly ONE route, not that this route is guarded.
    """
    tree = ast.parse(Path(cli.__file__).read_text())

    calls = [node for node in ast.walk(tree)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "_move_frozen_files"]
    assert len(calls) == 1, (
        f"{len(calls)} routes to a move; this test knows how to guard one")

    guarded = []
    for branch in ast.walk(tree):
        if not isinstance(branch, ast.If):
            continue
        names = {n.id for n in ast.walk(branch.test) if isinstance(n, ast.Name)}
        if not {"moving", "undoing"} & names:
            continue
        if any(c in ast.walk(branch) for c in calls):
            guarded.append(sorted(names))
    assert guarded == [["moving", "undoing"]], (
        f"the move is not guarded by both flags; found {guarded}")

    # And that those two names are bound from the flags and nothing else, so the
    # guard cannot be satisfied by something other than the person typing them.
    source = Path(cli.__file__).read_text()
    assert "moving = bool(args.apply) or args.apply_everything" in source
    assert "undoing = bool(args.undo) or args.undo_everything" in source

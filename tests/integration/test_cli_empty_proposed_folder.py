"""Lock-in never refuses the whole plan because one proposed folder is empty.

The judge, round 3: "the proposed folder 'Photos and Media' has no file the
sorter can put in it, so it refuses the whole plan". The shape chosen for a
proposed branch built nothing, `apply_review_action` refused ("accepting X
produced no node") and the whole run ended. The branch now keeps its own node,
nothing is built inside it, the rest freezes, and a proposed folder that ends
up with no file is named once and not built.

The empty projection is forced by wrapping `project_branch_preview`; everything
else is the shipped command on a real corpus, with no model.
"""
from __future__ import annotations

import dataclasses
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from tree_design import pipeline  # noqa: E402

from test_cli_agreeing_corpus import AGREEING, _corpus, _nesting_answer  # noqa: E402


def _run(corpus: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "PHYS 1401", "--user", "jy",
                     "--database", str(corpus.parent / "plan.sqlite"),
                     "--accept-groups", *extra], out=out)
    return code, out.getvalue()


def test_a_shape_that_builds_nothing_does_not_refuse_the_plan(tmp_path,
                                                             monkeypatch):
    corpus = _corpus(tmp_path, AGREEING)
    _, first = _run(corpus)
    answer = _nesting_answer(first)

    real = pipeline.project_branch_preview

    def builds_nothing(*args, **kwargs):
        preview = real(*args, **kwargs)
        return dataclasses.replace(preview, nodes=(), branch_expectations=())

    monkeypatch.setattr(pipeline, "project_branch_preview", builds_nothing)
    code, frozen = _run(corpus, "--answer", answer, "--freeze")

    assert code == 0, frozen
    assert "produced no node" not in frozen, frozen
    assert ("Frozen:" in frozen) or ("Nothing was frozen" in frozen), frozen
    named = [line for line in frozen.splitlines()
             if line.startswith("Not built, because no file goes there:")]
    assert len(named) == 1, frozen
    assert "PHYS 1401" in named[0], frozen


def test_a_proposed_folder_that_gets_files_is_not_named_as_dropped(tmp_path):
    corpus = _corpus(tmp_path, AGREEING)
    _, first = _run(corpus)
    code, frozen = _run(corpus, "--answer", _nesting_answer(first), "--freeze")
    assert code == 0, frozen
    assert "Frozen: 3 file(s) are ready to move" in frozen, frozen
    assert "Not built, because no file goes there" not in frozen, frozen

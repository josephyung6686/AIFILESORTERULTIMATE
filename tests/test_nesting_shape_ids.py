"""A nesting question cannot carry two options with one id.

Two photo shapes both named `media_type>capture_year` refused the whole
cloud run before any outline was written. The question is asked of one
option per shape key.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from questions.triggers import question_for_nesting  # noqa: E402


class _Option:
    def __init__(self, counts: dict[str, int], marker: str):
        self.resulting_child_counts = counts
        self.marker = marker
        self.summary = marker
        self.children = ()
        self.warnings = ()
        self.validation = None


def test_two_shapes_with_one_chain_become_one_option():
    first = _Option({"media_type": 1, "capture_year": 2}, "first")
    second = _Option({"media_type": 1, "capture_year": 2}, "second")
    kept = _Option({"capture_year": 1}, "year")
    offered = cli._one_option_per_shape((first, second, kept))
    assert [item.marker for item in offered] == ["second", "year"]
    question = question_for_nesting(
        branch_label="Photos",
        choices=cli._nesting_choices(offered),
        file_count=4)
    ids = [option.option_id for option in question.options]
    assert len(ids) == len(set(ids))
    assert "media_type>capture_year" in ids
    assert "capture_year" in ids

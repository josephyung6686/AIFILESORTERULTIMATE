"""The ground-truth label file is the instrument's zero point. A label that is
wrong in a way nobody notices drives the product in the wrong direction for as
long as it stands, so the loader refuses the label shapes that would do that
rather than reading them and hoping.
"""


from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. This is done HERE, in each test module, rather than in a `conftest.py`:
# with no `__init__.py` in the tests tree, every conftest is imported under the
# bare module name `conftest`, and the last one collected wins. A `conftest.py`
# in this directory took that name away from `tests/p5/conftest.py`, whose tests
# do `from conftest import RecordingSink` at CALL time, so they got whichever
# module still held the name -- three failed repo-wide and passed in isolation.
# A harness that breaks the suite it exists to measure is worse than no harness,
# so this package contributes no conftest at all.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json

import pytest

from tools.groundtruth.labels import Label, LabelError, load_labels


def _write(tmp_path, rows):
    path = tmp_path / "labels.json"
    path.write_text(json.dumps({"files": rows}), encoding="utf-8")
    return path


def _row(**over):
    row = {
        "path": "Downloads/a.pdf",
        "group": "A_course_by_code",
        "situation": "academic.coursework",
        "destination": ["PHYS1403", "exam"],
        "also_acceptable": [],
        "expected_fields": {"subject": "PHYS1403"},
        "protected": False,
        "uncertain": None,
        "family": None,
        "note": None,
    }
    row.update(over)
    return row


def test_a_well_formed_label_file_loads(tmp_path):
    labels = load_labels(_write(tmp_path, [_row()]))
    assert list(labels) == ["Downloads/a.pdf"]
    one = labels["Downloads/a.pdf"]
    assert isinstance(one, Label)
    assert one.destination == ("PHYS1403", "exam")
    assert one.expected_fields == {"subject": "PHYS1403"}
    assert one.is_uncertain is False


def test_a_protected_label_may_not_carry_a_destination(tmp_path):
    # A destination is an instruction to move. Protected material is counted and
    # marked and never moved, so a label that names one for it is a label that
    # would score the product for doing the forbidden thing.
    path = _write(tmp_path, [_row(protected=True, destination=["Health", "records"])])
    with pytest.raises(LabelError, match="protected.*destination"):
        load_labels(path)


def test_a_protected_label_may_not_carry_expected_fields(tmp_path):
    # Fields come from content. Expecting a field of a protected file is
    # expecting the file to have been opened.
    path = _write(tmp_path, [_row(protected=True, destination=None,
                                  expected_fields={"subject": "x"})])
    with pytest.raises(LabelError, match="protected.*field"):
        load_labels(path)


def test_two_rows_for_one_path_are_refused(tmp_path):
    path = _write(tmp_path, [_row(), _row(destination=["OTHER"])])
    with pytest.raises(LabelError, match="twice"):
        load_labels(path)


def test_an_uncertain_label_is_marked_and_keeps_its_reason(tmp_path):
    labels = load_labels(_write(tmp_path, [
        _row(uncertain="no course is named anywhere in the file")]))
    one = labels["Downloads/a.pdf"]
    assert one.is_uncertain is True
    assert "no course" in one.uncertain


def test_an_uncertain_label_with_no_reason_is_refused(tmp_path):
    # `uncertain: true` with no words is the guess this file exists to prevent:
    # it records that somebody hesitated without recording what about.
    path = _write(tmp_path, [_row(uncertain="")])
    with pytest.raises(LabelError, match="reason"):
        load_labels(path)


def test_a_situation_outside_the_shipped_library_is_refused(tmp_path):
    # Labelling against a situation the product does not ship means the run that
    # would score the file can never be made.
    path = _write(tmp_path, [_row(situation="academic.invented-by-the-labeller")])
    with pytest.raises(LabelError, match="not a shipped situation"):
        load_labels(path)


def test_the_situations_needing_a_run_are_listed_once_each(tmp_path):
    labels = load_labels(_write(tmp_path, [
        _row(path="a", situation="academic.coursework"),
        _row(path="b", situation="academic.coursework"),
        _row(path="c", situation="research.dataset-analysis"),
    ]))
    assert labels.situations() == ("academic.coursework", "research.dataset-analysis")

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


def _write(tmp_path, rows, aliases=None):
    path = tmp_path / "labels.json"
    document = {"files": rows}
    if aliases is not None:
        document["aliases"] = aliases
    path.write_text(json.dumps(document), encoding="utf-8")
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


# ---------------------------------------------------------------------------
# `104` R-147 / `00`:17's taxonomy aliases: one course, two spellings
# ---------------------------------------------------------------------------
# §16.2 measured the hole. For 18 of the 43 labelled coursework files the course
# code is nowhere in the file's own bytes -- it is in the folder path, or on a
# neighbouring syllabus the anchor context did carry -- "under a spelling the
# label does not use". 23 dossiers held the code's digits and every one of them
# scored as a miss. The register's own example: the documents of one course
# print `ENGI E1006` and the label spells it `PYTHON1006`.
#
# `_same` is already separator-blind, which is why `AAAAAA9999` against a
# printed `Aaaaaa 9999` needed nothing. What it cannot do is know that a code
# and a name are one course, because that is not a fact about the strings.
# Somebody has to say so, and the labels file is where a person says things.


def test_an_alias_group_loads_onto_the_rows_it_names(tmp_path):
    labels = load_labels(_write(
        tmp_path, [_row()],
        aliases=[{"field": "subject", "values": ["PHYS1403", "Chemistry 1403"]}]))
    one = labels["Downloads/a.pdf"]
    # Keyed by the FIELD, and holding the other spellings of THIS row's value --
    # resolved at load so the scorer never carries the whole table around and
    # never has to ask which group a value is in.
    assert one.aliases == {"subject": ("Chemistry 1403",)}


def test_a_row_whose_value_is_in_no_group_carries_no_alias(tmp_path):
    labels = load_labels(_write(
        tmp_path, [_row()],
        aliases=[{"field": "subject", "values": ["PYTHON1006", "ENGI E1006"]}]))
    assert labels["Downloads/a.pdf"].aliases == {}


def test_a_group_reaches_only_the_field_it_names(tmp_path):
    """Scoped to one field on purpose. `essay` as a `work_type` and `essay` as
    part of a subject are not the same claim, and a group that leaked across
    fields would score a right answer to the wrong question as agreement."""
    labels = load_labels(_write(
        tmp_path, [_row(expected_fields={"subject": "PHYS1403",
                                         "work_type": "PHYS1403"})],
        aliases=[{"field": "subject", "values": ["PHYS1403", "Chemistry 1403"]}]))
    assert labels["Downloads/a.pdf"].aliases == {"subject": ("Chemistry 1403",)}


def test_a_group_with_one_spelling_is_refused(tmp_path):
    """A group of one asserts no equivalence and reads as though it did."""
    with pytest.raises(LabelError, match="at least two"):
        load_labels(_write(tmp_path, [_row()],
                           aliases=[{"field": "subject", "values": ["PHYS1403"]}]))


def test_a_group_with_no_field_is_refused(tmp_path):
    with pytest.raises(LabelError, match="field"):
        load_labels(_write(tmp_path, [_row()],
                           aliases=[{"values": ["PHYS1403", "Chemistry 1403"]}]))


def test_one_value_in_two_groups_of_a_field_is_refused(tmp_path):
    """Two groups sharing a spelling are one group written twice, or two
    different claims about what that spelling means. Either way the scorer
    would take whichever loaded last, which is the defect `two rows for one
    path` is refused for."""
    with pytest.raises(LabelError, match="two alias groups"):
        load_labels(_write(tmp_path, [_row()], aliases=[
            {"field": "subject", "values": ["PHYS1403", "Chemistry 1403"]},
            {"field": "subject", "values": ["PHYS1403", "Physics 1403"]},
        ]))


def test_a_labels_file_with_no_aliases_still_loads(tmp_path):
    """The key is optional, and its absence is not an empty ruling -- every
    labels file written before R-147 has to keep loading unchanged."""
    assert load_labels(_write(tmp_path, [_row()])).aliases == ()

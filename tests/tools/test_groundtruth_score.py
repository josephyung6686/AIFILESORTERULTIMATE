"""Scoring rules, checked against hand-built observations rather than a run.

The rules that matter are the ones that decide whether a number flatters the
product: what counts as the right folder, what an `uncertain` file may score,
and what makes the protected check fail outright.
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

import pytest

from tools.groundtruth.labels import Label
from tools.groundtruth.measure import Observation
from tools.groundtruth.score import (
    PLACED_EXACT,
    PLACED_FLAT,
    PLACED_PARENT,
    PLACED_WRONG,
    NOT_PLACED,
    NO_DECISION,
    ProtectedBreach,
    protected_verdict,
    score_fields,
    score_sorting,
)


def _label(**over):
    base = dict(path="p", group="g", situation="academic.coursework",
                destination=("PHYS1403", "exam"), also_acceptable=(),
                expected_fields={}, protected=False, uncertain=None,
                family=None, note=None)
    base.update(over)
    return Label(**base)


def _obs(**over):
    base = dict(path="p", indexed=True, excluded_by=None, opened=True, text_units=3, evidence_rows=2, prose_evidence_rows=2,
                extractors=("pdf.text",), completeness="complete",
                content_recovered=True, protected_marked=False,
                handling_class="personal_non_sensitive", fields={},
                field_origins={}, unresolved_fields=(), outcome="place",
                destination=("Coursework", "PHYS1403", "exam"), asked=False)
    base.update(over)
    return Observation(**base)


# --------------------------------------------------------------- sorting

def test_the_labelled_folder_reached_exactly_is_exact():
    assert score_sorting(_label(), _obs()) == PLACED_EXACT


def test_the_top_level_folder_is_not_credited_with_the_structure_below_it():
    # Today's product builds one flat folder. That is the right BRANCH and no
    # structure at all, and calling it "right parent" would read as partial
    # success. It gets its own bucket so it can never be mistaken for one.
    assert score_sorting(_label(), _obs(destination=("Coursework",))) == PLACED_FLAT


def test_the_right_parent_with_the_leaf_missing_is_its_own_bucket():
    obs = _obs(destination=("Coursework", "PHYS1403"))
    assert score_sorting(_label(), obs) == PLACED_PARENT


def test_a_different_course_is_wrong_not_partial():
    obs = _obs(destination=("Coursework", "PHYS1401", "exam"))
    assert score_sorting(_label(), obs) == PLACED_WRONG


def test_a_second_right_answer_counts_as_exact():
    # The north star: a research paper that is also homework has two right
    # destinations and the person picks. Reaching either one is reaching it.
    label = _label(destination=("Applications", "supporting material"),
                   also_acceptable=(("Research", "abstract"),))
    assert score_sorting(label, _obs(destination=("X", "Research", "abstract"))) == PLACED_EXACT


def test_spelling_of_a_folder_name_is_not_what_is_being_measured():
    # "PHYS 1403" and "phys1403" are the same folder to a person, and which one
    # the product mints is a normalisation decision, not a sorting decision.
    obs = _obs(destination=("Coursework", "PHYS 1403", "Exam"))
    assert score_sorting(_label(), obs) == PLACED_EXACT


def test_an_abstention_is_not_placed():
    assert score_sorting(_label(), _obs(outcome="abstain")) == NOT_PLACED


def test_a_file_that_never_reached_a_decision_is_recorded_as_such():
    assert score_sorting(_label(), _obs(outcome=None)) == NO_DECISION


def test_an_uncertain_label_passes_only_by_abstaining():
    # Where a person would have to be asked, a confident answer is a defect even
    # when it happens to look plausible, and abstaining is the successful outcome.
    label = _label(uncertain="no course is named anywhere in the file")
    assert score_sorting(label, _obs(outcome="abstain")) == NOT_PLACED
    assert score_sorting(label, _obs()) == PLACED_WRONG


# ---------------------------------------------------------------- fields

def test_only_labelled_fields_are_scored_and_a_match_is_a_match():
    label = _label(expected_fields={"subject": "PHYS1403", "work_type": "exam"})
    obs = _obs(fields={"subject": "PHYS1403", "work_type": "exam", "file_type": "pdf"})
    correct, wrong, missing, extra = score_fields(label, obs)
    assert (correct, wrong, missing) == (2, 0, 0)
    assert extra == 1  # reported, never counted against the product


def test_a_field_filled_with_the_wrong_value_is_worse_than_an_empty_one():
    label = _label(expected_fields={"subject": "PHYS1403"})
    filled_wrong = score_fields(label, _obs(fields={"subject": "PHYS1401"}))
    left_empty = score_fields(label, _obs(fields={}))
    assert filled_wrong[1] == 1 and filled_wrong[2] == 0
    assert left_empty[1] == 0 and left_empty[2] == 1


# ------------------------------------------------------------- protected

def test_a_protected_file_that_was_marked_and_left_shut_passes():
    label = _label(protected=True, destination=None)
    obs = _obs(protected_marked=True, opened=False, text_units=0, evidence_rows=0, prose_evidence_rows=0,
               extractors=("filesystem.record",), outcome=None, destination=())
    assert protected_verdict({label.path: label}, {label.path: obs}) == ()


def test_a_protected_file_that_was_never_marked_fails_outright():
    label = _label(protected=True, destination=None)
    obs = _obs(protected_marked=False, opened=False, text_units=0, evidence_rows=0, prose_evidence_rows=0,
               extractors=("filesystem.record",), outcome=None, destination=())
    breaches = protected_verdict({label.path: label}, {label.path: obs})
    assert [b.kind for b in breaches] == ["not marked"]


def test_a_protected_file_that_was_opened_fails_outright():
    # The rule is not "handled carefully". It is never opened, and a text unit
    # is the product's own record that it read one.
    label = _label(protected=True, destination=None)
    obs = _obs(protected_marked=True, opened=True, text_units=122,
               extractors=("filesystem.record", "pdf.text"), outcome=None, destination=())
    breaches = protected_verdict({label.path: label}, {label.path: obs})
    assert [b.kind for b in breaches] == ["opened"]
    assert breaches[0].detail.startswith("pdf.text")


def test_a_protected_file_that_was_placed_fails_outright():
    label = _label(protected=True, destination=None)
    obs = _obs(protected_marked=True, opened=False, text_units=0, evidence_rows=0, prose_evidence_rows=0,
               extractors=("filesystem.record",), outcome="place",
               destination=("Coursework",))
    breaches = protected_verdict({label.path: label}, {label.path: obs})
    assert [b.kind for b in breaches] == ["placed"]


def test_a_protected_file_missing_from_the_run_entirely_fails():
    # "never silently omitted" is the other half of the rule. A protected file
    # that simply is not there has not been counted.
    label = _label(protected=True, destination=None)
    breaches = protected_verdict({label.path: label}, {})
    assert [b.kind for b in breaches] == ["absent"]


def test_every_breach_names_the_file_so_the_failure_is_actionable():
    label = _label(path="Desktop/Vaccine records/x.pdf", protected=True, destination=None)
    breaches = protected_verdict({label.path: label}, {})
    assert isinstance(breaches[0], ProtectedBreach)
    assert breaches[0].path == "Desktop/Vaccine records/x.pdf"


def test_marking_a_file_protected_that_is_not_is_reported_separately():
    # A Visa logo called sensitive personal material is a defect too, but it is
    # a different one, and folding it into the hard pass/fail would hide both.
    from tools.groundtruth.score import over_marked

    label = _label(path="visa.svg", protected=False)
    obs = _obs(path="visa.svg", protected_marked=True)
    assert over_marked({label.path: label}, {obs.path: obs}) == ("visa.svg",)


# ------------------------------------------------------- the classify gate

def test_a_file_with_no_handling_class_is_not_classified():
    # SS8.4 makes a handling class a precondition of asking a model, so this one
    # property bounds every number that depends on the model. It is read off the
    # product's own classifications table and never inferred from anything else.
    assert _obs(handling_class=None).classified is False
    assert _obs(handling_class="personal_non_sensitive").classified is True


def test_a_field_records_which_half_of_the_pipeline_earned_it():
    # A value a rule guessed and a value a model cited are both "filled". Only
    # the origin separates them, and without it a wired model is unattributable.
    observation = _obs(fields={"subject": "PHYS1403"},
                       field_origins={"subject": "llm_interpretation"})
    assert observation.field_origins["subject"] == "llm_interpretation"

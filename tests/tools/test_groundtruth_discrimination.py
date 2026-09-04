"""Rules for the situation-discrimination measurement.

WRITTEN BUT NOT YET RUN: the machine was held quiet for wall-clock measurements
when these were authored, so they have never been executed. Run them before
believing anything the module says.

The rules worth pinning are the ones that decide whether a null result is real:
two absences agreeing is not stability, one observation is not stability, and a
file that is wrong the same way everywhere IS stable -- because the question is
whether the situation moves the answer, not whether the answer is good.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. Done HERE rather than in a `conftest.py`: with no `__init__.py` in the
# tests tree every conftest is imported under the bare name `conftest`, and the
# last one collected wins -- which once took that name from `tests/p5/conftest.py`
# and failed three of its tests repo-wide while they passed in isolation.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.groundtruth.discrimination import (          # noqa: E402
    report, situation_divergence, two_things_reachable,
)
from tools.groundtruth.labels import Label, Labels      # noqa: E402
from tools.groundtruth.measure import Observation, RunObservation  # noqa: E402


def _obs(path, **over):
    base = dict(path=path, indexed=True, excluded_by=None, opened=True, text_units=3, evidence_rows=2, prose_evidence_rows=2,
                extractors=("pdf.text",), completeness="complete",
                content_recovered=True, protected_marked=False,
                handling_class="personal_non_sensitive", fields={},
                field_origins={}, unresolved_fields=(), outcome="place",
                destination=("Coursework",), asked=False)
    base.update(over)
    return Observation(**base)


def _run(situation, *observations):
    return RunObservation(situation=situation, label=situation.split(".")[-1],
                          promised_levels=(), files={o.path: o for o in observations},
                          structural_questions=0, node_count=1, built_depth=0,
                          report="")


def _label(path, **over):
    base = dict(path=path, group="g", situation="academic.coursework",
                destination=("A",), also_acceptable=(), expected_fields={},
                protected=False, uncertain=None, family=None, note=None)
    base.update(over)
    return Label(**base)


def test_a_value_that_moves_with_the_situation_is_counted_as_differing():
    runs = [_run("academic.coursework", _obs("f", fields={"subject": "PHYS1403"})),
            _run("research.dataset-analysis", _obs("f", fields={"subject": "OTHER"}))]
    facts, _, _ = situation_divergence(runs)
    assert (facts.compared, facts.differing) == (1, 1)


def test_a_value_that_is_wrong_the_same_way_everywhere_is_stable():
    # The question is whether the SITUATION moves the answer, not whether the
    # answer is right. A file wrong identically under every situation is the
    # strongest possible evidence that the situation is not being consulted.
    runs = [_run("academic.coursework", _obs("f", fields={"subject": "U238"})),
            _run("research.dataset-analysis", _obs("f", fields={"subject": "U238"}))]
    facts, _, _ = situation_divergence(runs)
    assert (facts.compared, facts.differing) == (1, 0)


def test_two_absences_agreeing_is_not_evidence_of_stability():
    # The trap that would make this measurement lie. A corpus where the product
    # concludes nothing would show "0 files differ" and read as a finding, when
    # it is only the absence of data. Files with no facts are not compared.
    runs = [_run("academic.coursework", _obs("f", fields={})),
            _run("research.dataset-analysis", _obs("f", fields={}))]
    facts, _, _ = situation_divergence(runs)
    assert facts.compared == 0


def test_one_observation_is_never_evidence_that_a_value_is_stable():
    runs = [_run("academic.coursework", _obs("f", fields={"subject": "X"}))]
    facts, _, _ = situation_divergence(runs)
    assert facts.compared == 0


def test_a_file_the_scan_set_aside_is_not_compared():
    runs = [_run("academic.coursework", _obs("f", indexed=False, fields={"a": "1"})),
            _run("research.dataset-analysis", _obs("f", indexed=False, fields={"a": "2"}))]
    facts, _, _ = situation_divergence(runs)
    assert facts.compared == 0


def test_the_three_dimensions_are_reported_separately():
    runs = [_run("academic.coursework",
                 _obs("f", fields={"a": "1"}, handling_class="public_low",
                      outcome="place")),
            _run("research.dataset-analysis",
                 _obs("f", fields={"a": "1"}, handling_class="sensitive_personal",
                      outcome="abstain"))]
    facts, handling, outcome = situation_divergence(runs)
    assert facts.differing == 0        # the facts held
    assert handling.differing == 1     # the class moved
    assert outcome.differing == 1      # and so did the decision


# --------------------------------------------------------- the north star

def test_a_file_reaching_both_of_its_right_answers_is_the_finding():
    label = _label("f", destination=("Applications", "supporting material"),
                   also_acceptable=(("Research", "abstract"),))
    runs = [_run("applications.undergraduate-packet",
                 _obs("f", destination=("X", "Applications", "supporting material"))),
            _run("research.manuscript-publication",
                 _obs("f", destination=("X", "Research", "abstract")))]
    found = two_things_reachable(runs, Labels({label.path: label}))
    assert len(found) == 1
    assert found[0].both_readings_reachable is True
    assert len(found[0].reached) == 2


def test_a_file_that_only_ever_reaches_one_reading_is_not_a_ui_problem():
    # If the second reading never fires under any situation, the evidence does
    # not carry it, and no amount of offering the person a choice would help.
    label = _label("f", destination=("Applications", "supporting material"),
                   also_acceptable=(("Research", "abstract"),))
    runs = [_run("applications.undergraduate-packet",
                 _obs("f", destination=("X", "Applications", "supporting material"))),
            _run("research.manuscript-publication",
                 _obs("f", destination=("X", "Somewhere", "else")))]
    found = two_things_reachable(runs, Labels({label.path: label}))
    assert found[0].both_readings_reachable is False
    assert found[0].reached == ("Applications/supporting material",)


def test_a_file_with_one_right_answer_is_not_asked_about():
    label = _label("f", destination=("A",), also_acceptable=())
    runs = [_run("academic.coursework", _obs("f"))]
    assert two_things_reachable(runs, Labels({label.path: label})) == ()


def test_protected_files_are_never_part_of_this_measurement():
    label = _label("f", protected=True, destination=None,
                   also_acceptable=(("Research", "abstract"),))
    runs = [_run("academic.coursework", _obs("f"))]
    assert two_things_reachable(runs, Labels({label.path: label})) == ()


def test_a_zero_is_not_reported_as_evidence_about_the_readings():
    # The null this measurement will most likely produce, and the easiest to
    # over-read. A file that was never placed was never asked the question, so
    # "0 reached more than one" says nothing about whether the evidence carries
    # a second reading -- it says placement did not happen.
    label = _label("f", destination=("A",), also_acceptable=(("B",),))
    runs = [_run("academic.coursework", _obs("f", outcome="abstain"))]
    text = report(runs, Labels({label.path: label}))
    assert "NOT MEASURED" in text
    assert "NOT evidence that the evidence carries" in text.replace("\n", " ").replace("  ", " ")


def test_placed_but_never_reaching_a_second_reading_is_a_real_finding():
    label = _label("f", destination=("A",), also_acceptable=(("B",),))
    runs = [_run("academic.coursework", _obs("f", destination=("X", "A")))]
    text = report(runs, Labels({label.path: label}))
    assert "NOT MEASURED" not in text
    assert "not there to be offered" in text

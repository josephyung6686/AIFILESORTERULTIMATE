"""Rules for the starvation-versus-vocabulary experiment.

WRITTEN BUT NOT YET RUN: the machine was held quiet for wall-clock measurements
when these were authored. Run them before believing anything the module says.

The rules worth pinning are the ones that stop the experiment being fitted to
its own result: a file with no text cannot test a vocabulary, the reading taken
is the one most favourable to the hypothesis under test, and the verdict is
decided by a rule set in advance rather than by whoever reads the table.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. Done HERE rather than in a `conftest.py`: with no `__init__.py` in the
# tests tree every conftest is imported under the bare name `conftest`, and the
# last one collected wins -- which once took that name from `tests/p5/conftest.py`.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.groundtruth.labels import Label, Labels                  # noqa: E402
from tools.groundtruth.measure import Observation, RunObservation   # noqa: E402
from tools.groundtruth.protected_evidence import (                  # noqa: E402
    PRIOR_MARKED, protected_evidence, three_way, verdict,
)


def _obs(path, **over):
    base = dict(path=path, indexed=True, excluded_by=None, opened=True, text_units=0, evidence_rows=0, prose_evidence_rows=0,
                extractors=("pdf.text",), completeness="complete",
                content_recovered=False, protected_marked=False,
                handling_class=None, fields={}, field_origins={},
                unresolved_fields=(), outcome=None, destination=(), asked=False)
    base.update(over)
    return Observation(**base)


def _run(situation, *observations):
    return RunObservation(situation=situation, label="L", promised_levels=(),
                          files={o.path: o for o in observations},
                          structural_questions=0, node_count=1, built_depth=0,
                          report="")


def _protected(path):
    return Label(path=path, group="F_protected", situation="academic.coursework",
                 destination=None, also_acceptable=(), expected_fields={},
                 protected=True, uncertain=None, family=None, note=None)


def _labels(*paths):
    return Labels({p: _protected(p) for p in paths})


def test_the_reading_taken_is_the_run_that_saw_the_most_text():
    # Deliberately the most favourable reading for the vocabulary hypothesis: if
    # the detector still did not mark a file when shown the most text any run
    # recovered, starvation cannot be the explanation.
    runs = [_run("a", _obs("f", prose_evidence_rows=3)),
            _run("b", _obs("f", prose_evidence_rows=122)),
            _run("c", _obs("f", prose_evidence_rows=0))]
    row, = protected_evidence(runs, _labels("f"))
    assert row.prose_evidence_rows == 122


def test_a_file_whose_only_units_are_the_filesystem_record_is_starved():
    # THE BUG THIS GUARD MISSED. `had_evidence` asked `text_units > 0`, and
    # every file carries units and four observations from `filesystem.record`
    # alone. Two genuinely starved medical files therefore landed in the
    # vocabulary's column -- the exact accusation the three-way split exists to
    # prevent, made by the code that exists to prevent it. Prose observations,
    # not units, are what a vocabulary can be shown.
    rows = protected_evidence(
        [_run("a", _obs("starved", text_units=1, evidence_rows=0,
                        prose_evidence_rows=0))],
        _labels("starved"))
    assert rows[0].had_evidence is False
    assert [r.path for r in three_way(rows)["never testable"]] == ["starved"]


def test_exif_is_an_observation_and_is_not_prose():
    # A JPEG yields EXIF: a real observation, and nothing a word list matches.
    rows = protected_evidence(
        [_run("a", _obs("photo", text_units=1, evidence_rows=2,
                        prose_evidence_rows=0))],
        _labels("photo"))
    assert rows[0].had_evidence is False


def test_a_file_with_no_text_cannot_test_a_vocabulary():
    # The mistake the whole module exists to prevent. Two of the eight had zero
    # text-bearing observations, so "the vocabulary has no word for it" was
    # never testable for them and must not be counted against the vocabulary.
    row, = protected_evidence([_run("a", _obs("f", prose_evidence_rows=0))],
                              _labels("f"))
    assert row.had_evidence is False
    row, = protected_evidence([_run("a", _obs("f", prose_evidence_rows=1))],
                              _labels("f"))
    assert row.had_evidence is True


def test_a_protected_file_absent_from_every_run_is_still_a_row():
    # "Never silently omitted" applies to the experiment too: a protected file
    # missing from the runs must not quietly shrink the denominator.
    rows = protected_evidence([_run("a")], _labels("gone"))
    assert len(rows) == 1
    assert rows[0].text_units == 0 and rows[0].marked is False


def test_only_protected_files_are_in_the_experiment():
    labels = Labels({"p": _protected("p"),
                     "q": Label(path="q", group="g", situation="academic.coursework",
                                destination=("A",), also_acceptable=(),
                                expected_fields={}, protected=False,
                                uncertain=None, family=None, note=None)})
    rows = protected_evidence([_run("a", _obs("p"), _obs("q"))], labels)
    assert [r.path for r in rows] == ["p"]


# ------------------------------------------------------------- the verdict

def test_any_improvement_falsifies_the_prediction():
    rows = protected_evidence(
        [_run("a", _obs("f", text_units=10, prose_evidence_rows=10, protected_marked=True))], _labels("f"))
    assert verdict(rows).startswith("PREDICTION WRONG")
    assert PRIOR_MARKED == 0


def test_no_text_anywhere_means_neither_hypothesis_was_tested():
    # The outcome that would look like a confirmation and is not one.
    rows = protected_evidence([_run("a", _obs("f", text_units=0, prose_evidence_rows=0))], _labels("f"))
    assert verdict(rows).startswith("STILL UNTESTABLE")


def test_text_present_and_still_unmarked_is_the_hard_test_the_vocabulary_fails():
    rows = protected_evidence(
        [_run("a", _obs("f", text_units=122, prose_evidence_rows=122), _obs("g", text_units=88, prose_evidence_rows=88))],
        _labels("f", "g"))
    assert verdict(rows).startswith("PREDICTION HELD")
    assert "starvation is excluded" in verdict(rows)


def test_a_mixed_result_says_which_files_do_not_count_against_the_vocabulary():
    rows = protected_evidence(
        [_run("a", _obs("f", text_units=122, prose_evidence_rows=122), _obs("g", text_units=0, prose_evidence_rows=0))],
        _labels("f", "g"))
    answer = verdict(rows)
    assert answer.startswith("PREDICTION HELD, PARTLY")
    assert "do not count those against the vocabulary" in answer


def test_a_starved_file_never_folds_into_the_vocabulary_column():
    # The standing shape. "Unmarked" is an accusation against the vocabulary,
    # and it is only fair about a file the vocabulary was actually shown. A
    # future extractor giving a starved file one unit of text must not silently
    # move it into the column that counts against the library.
    rows = protected_evidence(
        [_run("a", _obs("shown", text_units=99, prose_evidence_rows=99), _obs("starved", text_units=0, prose_evidence_rows=0))],
        _labels("shown", "starved"))
    buckets = three_way(rows)
    assert [r.path for r in buckets["vocabulary failed"]] == ["shown"]
    assert [r.path for r in buckets["never testable"]] == ["starved"]
    assert buckets["marked"] == ()


def test_the_three_buckets_are_exhaustive_and_disjoint():
    # No file may quietly leave the denominator.
    rows = protected_evidence(
        [_run("a", _obs("m", text_units=5, prose_evidence_rows=5, protected_marked=True),
              _obs("v", text_units=5, prose_evidence_rows=5), _obs("n", text_units=0, prose_evidence_rows=0))],
        _labels("m", "v", "n"))
    buckets = three_way(rows)
    seen = [r.path for members in buckets.values() for r in members]
    assert sorted(seen) == ["m", "n", "v"]
    assert len(seen) == len(set(seen)) == len(rows)

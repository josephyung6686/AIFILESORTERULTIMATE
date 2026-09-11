"""The harness against the real product, over a synthetic corpus in this tree.

Synthetic on purpose. The corpus the harness was built for is two hundred of the
owner's own files, and no test may depend on a path outside the repository or
carry his content into one. Eight invented files are enough to prove that the
measurement reads a real plan database correctly -- which is the part that
breaks silently when a table changes underneath it.
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

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.groundtruth.labels import load_labels
from tools.groundtruth.measure import observe_run
from tools.groundtruth.report import ACCEPTANCE_NOTE, measured_under
from tools.groundtruth.run import label_for, run_situations
from tools.groundtruth.score import (
    PROTECTED_BREACH_KINDS,
    protected_verdict,
    score_situation,
)

CORPUS = Path(__file__).resolve().parent / "fixture_corpus"
ROOT = Path(__file__).resolve().parents[2]

LABELS = {"files": [
    {"path": "Coursework/PHYS 1403 homework 2.txt", "group": "fixture",
     "situation": "academic.coursework", "destination": ["PHYS1403", "homework"],
     "expected_fields": {"subject": "PHYS1403"}, "family": "hw2"},
    {"path": "Coursework/PHYS 1403 homework 2 copy.txt", "group": "fixture",
     "situation": "academic.coursework", "destination": ["PHYS1403", "homework"],
     "expected_fields": {"subject": "PHYS1403"}, "family": "hw2"},
    {"path": "Coursework/PHYS 1403 syllabus.txt", "group": "fixture",
     "situation": "academic.coursework", "destination": ["PHYS1403", "syllabus"],
     "expected_fields": {"subject": "PHYS1403"}},
    {"path": "Coursework/PHYS 1401 exam equations.txt", "group": "fixture",
     "situation": "academic.coursework", "destination": ["PHYS1401", "exam"],
     "expected_fields": {"subject": "PHYS1401"}},
    {"path": "Loose/logo.svg", "group": "fixture",
     "situation": "academic.coursework", "destination": None,
     "uncertain": "a logo with no course anywhere near it"},
    {"path": "Loose/page.html", "group": "fixture",
     "situation": "academic.coursework", "destination": None,
     "uncertain": "a saved page; nothing says what it was saved for"},
    {"path": "Loose/LICENSE", "group": "fixture",
     "situation": "academic.coursework", "destination": None,
     "uncertain": "an extensionless licence file"},
    {"path": "Loose/vaccination record.txt", "group": "fixture",
     "situation": "academic.coursework", "destination": None, "protected": True},
    {"path": "Project/requirements.txt", "group": "fixture",
     "situation": "code.notebooks-experiments", "destination": ["Project", "manifest"]},
    {"path": "Project/main.py", "group": "fixture",
     "situation": "code.notebooks-experiments", "destination": ["Project", "source file"]},
]}


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("groundtruth")
    # `force=True` deliberately: this is a FUNCTIONAL test, not a timing
    # measurement. It must give the same answer on a loaded machine as on an
    # idle one, so the load guard -- which exists to protect measurements --
    # would be protecting nothing here and would make the suite fail for a
    # reason that has nothing to do with the code under test.
    results = run_situations(CORPUS, ["academic.coursework"], out, workers=1,
                             load_ceiling=0.0, force=True)
    assert results[0].exit_code == 0, results[0].stderr
    return observe_run(results[0].database, CORPUS,
                       situation="academic.coursework",
                       label=label_for("academic.coursework"),
                       promised_levels=("My school", "Semester", "Course",
                                        "Kind of work"),
                       report=results[0].report.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def labels(tmp_path_factory):
    path = tmp_path_factory.mktemp("labels") / "labels.json"
    path.write_text(json.dumps(LABELS), encoding="utf-8")
    return load_labels(path)


def test_every_file_in_the_corpus_is_observed_including_the_ones_set_aside(run):
    # "never silently omitted" is a standing rule about the report, and it is a
    # rule about the scorecard for the same reason: a file the scan set aside
    # before reading it never becomes a `files` row, and a harness that reads
    # only that table would report a corpus smaller than the person's.
    on_disk = {str(p.relative_to(CORPUS)) for p in CORPUS.rglob("*") if p.is_file()}
    assert set(run.files) == on_disk
    set_aside = [o for o in run.files.values() if o.excluded_by]
    assert {o.path for o in set_aside} == {"Project/requirements.txt", "Project/main.py"}
    assert all(o.indexed is False and o.opened is False for o in set_aside)


def test_a_text_file_reports_its_content_recovered_and_the_extractor_that_did_it(run):
    one = run.files["Coursework/PHYS 1403 homework 2.txt"]
    assert one.completeness == "complete"
    assert one.content_recovered is True
    assert "text.structured" in one.extractors
    assert one.text_units > 0


def test_opened_follows_the_extractors_and_not_a_guess(run):
    # `opened` is the whole protected check, so it is read off the product's own
    # record of which extractors it ran, never inferred from anything else.
    for observation in run.files.values():
        beyond_the_directory_entry = [e for e in observation.extractors
                                      if e != "filesystem.record"]
        assert observation.opened == (bool(beyond_the_directory_entry)
                                      or observation.text_units > 0)


def test_the_harness_never_reads_the_text_it_counts(run):
    # `complete_extracted_text` is in ALWAYS_LOCAL. The harness needs how many
    # units there are and never what is in them, and an Observation has nowhere
    # to put one.
    from dataclasses import fields as dataclass_fields

    from tools.groundtruth.measure import Observation

    names = {f.name for f in dataclass_fields(Observation)}
    assert "text" not in names and "excerpt" not in names
    assert "text_units" in names


def test_a_destination_is_read_back_as_a_folder_chain(run):
    placed = [o for o in run.files.values() if o.outcome == "place"]
    assert placed, "the fixture corpus placed nothing at all"
    for observation in placed:
        assert observation.destination
        assert all(isinstance(segment, str) for segment in observation.destination)


def test_the_situation_scores_against_only_its_own_labelled_files(run, labels):
    score = score_situation(run, labels)
    # Eight labelled, one of them protected and so not sorted.
    assert score.scored == 7
    assert sum(score.sorting.values()) == 7


def test_the_protected_verdict_names_the_file_when_it_fails(run, labels):
    """SABOTAGE: re-spell the kinds here instead of importing them. This pin held
    a literal `{"absent", "not marked", "opened", "placed"}` and would have gone
    on passing after `104` §18.7 renamed two of them -- an empty breach list
    satisfies `all(...)`, so a scorer that reported nothing at all read as clean.
    The kinds come from the module that mints them."""
    breaches = protected_verdict(labels, run.files)
    # Whatever today's product does, the verdict is about ONE named file and is
    # a list of breaches rather than a rate.
    assert all(b.path == "Loose/vaccination record.txt" for b in breaches)
    assert all(b.kind in PROTECTED_BREACH_KINDS for b in breaches)
    # And reading this file on this machine is not one of them: §18.7 rules that
    # protected material is opened locally for the local model.
    observation = run.files["Loose/vaccination record.txt"]
    assert not observation.released_to_cloud
    assert not any(b.kind == "opened" for b in breaches)


def test_the_command_a_person_types_produces_a_scorecard(tmp_path):
    labels_path = tmp_path / "labels.json"
    labels_path.write_text(json.dumps(LABELS), encoding="utf-8")
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, "-m", "tools.groundtruth", "--corpus", str(CORPUS),
         "--labels", str(labels_path), "--out", str(out), "--workers", "1",
         "--force"],
        cwd=ROOT, capture_output=True, text=True)
    assert completed.returncode in (0, 1), completed.stderr   # 1 = protected failed
    card = (out / "scorecard.txt").read_text(encoding="utf-8")
    assert "GROUND TRUTH SCORECARD" in card
    assert "PROTECTED" in card
    assert "SORTING" in card
    table = (out / "per-file.tsv").read_text(encoding="utf-8").splitlines()
    assert len(table) == 1 + len(LABELS["files"])

    # `104` §12.12 and §12.7: WHICH PROMPT ROWS AND WHICH SEMANTIC SETTING THIS
    # CARD MEASURED. The digest is computed here from the manifest itself rather
    # than copied from the tool, so the two are independent readings of one claim,
    # and it is the run's note that the card prints -- `--score-only` below reads
    # the same note back out of the directory.
    from llm_harness.prompt_library import DRAFTS_FILE
    digest = hashlib.sha256(DRAFTS_FILE.read_bytes()).hexdigest()
    assert f"prompt rows: {DRAFTS_FILE.name} {digest[:16]}" in card
    # The environment names no weights in a test run, and "off" is the fact rather
    # than a line left out for the reader to assume.
    assert "semantic recognition: off" in card

    rescored = subprocess.run(
        [sys.executable, "-m", "tools.groundtruth", "--corpus", str(CORPUS),
         "--labels", str(labels_path), "--out", str(out), "--score-only"],
        cwd=ROOT, capture_output=True, text=True)
    assert rescored.returncode in (0, 1), rescored.stderr
    assert f"prompt rows: {DRAFTS_FILE.name} {digest[:16]}" in (
        out / "scorecard.txt").read_text(encoding="utf-8")


def test_a_directory_written_before_the_note_carried_them_says_so():
    """The honest word for a scorecard that cannot know. R-151's precedent.

    A directory of databases from before these two facts were recorded -- and a
    directory whose note this checkout cannot read -- must not print a digest
    taken from the scorer's own library or a setting read out of the scorer's own
    shell. Both would describe the scoring rather than the runs, and would look
    exactly like a card that knew.
    """
    lines = measured_under({})
    assert lines == ["prompt rows: not recorded by the run that wrote these "
                     "databases",
                     "semantic recognition: not recorded by the run that wrote "
                     "these databases",
                     # `104` SF-3's line is NOT read from the note and is never
                     # "not recorded": it is a fact about this harness rather than
                     # about the run being scored, true of every directory it has
                     # ever written, so a card scoring an old one still says who
                     # accepted the groups those numbers rest on.
                     *ACCEPTANCE_NOTE]
    assert measured_under({"prompt_library": "drafts.json",
                           "prompt_library_sha256": "0" * 64,
                           "semantic_model": "/weights/encoder"}) == [
        f"prompt rows: drafts.json {'0' * 16}",
        "semantic recognition: /weights/encoder",
        *ACCEPTANCE_NOTE]

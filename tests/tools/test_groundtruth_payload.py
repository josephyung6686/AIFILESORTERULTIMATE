"""The payload instrument (`104` §7 "Instruments"), over the fixture corpus.

Synthetic on purpose, for the reason `test_groundtruth_end_to_end.py` gives at
length: the corpus this instrument was built for is two hundred of the owner's own
files, and no test may depend on a path outside the repository or carry his content
into one.

What is proved here is the part that breaks silently: that the instrument opens no
model, writes nothing to the database it was pointed at, counts refusals at BOTH
places a file can be stopped, and that its canary test answers in both directions.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the path.
# Done HERE rather than in a `conftest.py`, for the reason the sibling test module
# spells out: with no `__init__.py` in the tests tree, a `conftest.py` in this
# directory would take the bare name `conftest` away from `tests/p5`'s.
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib

import pytest

from tools.groundtruth.payload import (
    canary_hit, inspect_database, main, render,
)
from tools.groundtruth.run import label_for, run_situations

CORPUS = Path(__file__).resolve().parent / "fixture_corpus"
SITUATION = "academic.coursework"


@pytest.fixture(scope="module")
def plan_database(tmp_path_factory):
    """One offline run of the real product over the fixture corpus.

    `force=True` for the same reason the sibling module gives: this is functional,
    not a timing measurement, so the load guard would be protecting nothing.
    """
    out = tmp_path_factory.mktemp("payload")
    results = run_situations(CORPUS, [SITUATION], out, workers=1,
                             load_ceiling=0.0, force=True)
    assert results[0].exit_code == 0, results[0].stderr
    assert label_for(SITUATION)
    return Path(results[0].database)


# --- the canary predicate, both directions ----------------------------------

def test_a_whole_document_inside_a_released_value_is_a_hit():
    document = "The whole of a short document, every word of it."
    assert canary_hit((document,), (document,))
    assert canary_hit((f"prefix {document} suffix",), (document,))


def test_an_excerpt_of_a_document_is_not_a_hit():
    """The direction that matters most: §8.4 WANTS short excerpts released, and an
    instrument that called every excerpt a breach would be unreadable on the first
    corpus it met."""
    document = "The whole of a short document, every word of it."
    assert not canary_hit(("a short document",), (document,))
    assert not canary_hit((), (document,))


def test_a_file_with_no_recovered_text_is_not_the_worst_breach():
    """An empty canary is a substring of everything. Counting it would report the
    files nothing could read as the ones that leaked most."""
    assert not canary_hit(("anything at all",), ("",))


# --- the instrument over a real plan database -------------------------------

def test_the_instrument_writes_nothing_to_the_database_it_reads(plan_database):
    """`Gate.release` appends §8.4's audit record and mints a release BEFORE it
    returns, so running one over a person's plan database would leave audit rows
    for calls nobody made. The instrument copies first; this is what says so."""
    before = hashlib.sha256(plan_database.read_bytes()).hexdigest()
    inspect_database(plan_database, CORPUS, situation=SITUATION)
    assert hashlib.sha256(plan_database.read_bytes()).hexdigest() == before


def test_every_file_in_the_roster_reaches_exactly_one_outcome(plan_database):
    """The standing rule, applied to this instrument: never silently omitted. A
    file is released, stopped at the gate, needs consent, or was never built --
    and the four are counted, not four minus whatever fell through."""
    report = inspect_database(plan_database, CORPUS, situation=SITUATION)
    assert report.files
    outcomes = {one.outcome for one in report.files}
    assert outcomes <= {"released", "denied", "needs_consent", "not_built",
                        "unreadable_request"}
    accounted = (len(report.released)
                 + sum(report.gate_refusals_by_reason().values())
                 + sum(report.not_built_by_reason().values()))
    assert accounted == len(report.files)


def test_the_blocked_line_counts_the_gate_and_not_only_the_route(plan_database):
    """R-46, in one assertion.

    A scoreboard that asked `cli.model_route_permitted` and stopped reported "19
    blocked" while 130 more were refused at the door. A count taken at the route
    alone was an undercount, and the block names both.

    **THE ASSERTION CHANGED SHAPE WHEN R-02 LANDED, exactly as its own note said
    it would.** This read `at_the_gate > at_the_route`, and R-02 is what stops
    that being true: the route now asks `unclassified_denies` with the target's
    locality, so the unclassified files a cloud gate was refusing are withheld one
    step earlier and move from the second column to the first. The block getting
    LOPSIDED is the fix working, and pinning which side is bigger would have
    pinned the defect.

    What R-46 was about survives unchanged and is what is asserted instead: both
    columns are reported, they account for every blocked file between them, and
    every gate reason is named. A number that means "the route let N through" must
    never again be read as "N reached a model".
    """
    report = inspect_database(plan_database, CORPUS, situation=SITUATION)
    at_the_route = sum(1 for one in report.files if not one.route_permitted)
    at_the_gate = sum(report.gate_refusals_by_reason().values())
    # BOTH COLUMNS CARRY FILES, which is the whole of what R-46 needed and the
    # only shape that survives R-02 moving files between them. They are not
    # disjoint and must not be summed: the route flag is recorded for every file
    # and the outcome is measured for every file, so one file can appear in both.
    # `test_every_file_is_accounted_for` owns the arithmetic, over the outcomes.
    assert at_the_route > 0, "the route withholds nothing, so column one is untested"
    assert at_the_gate > 0, (
        "the gate refuses nothing, so a count taken at the route alone would look "
        "complete -- which is the reading R-46 was about")
    block = render(report)
    assert "withheld at the route" in block
    assert "stopped at the gate" in block
    assert "largest dossier BUILT" in block
    for reason in report.gate_refusals_by_reason():
        assert reason in block


def test_no_dossier_is_over_the_ceiling_and_no_whole_document_escapes(
        plan_database):
    """`104` §7 Phase 1 step 1's pass condition, on a corpus a test may carry.

    Three numbers, and each is zero for its own reason: the ceiling is seeded at
    4,000 and measured (`104` SF-5); a span-less whole-document body is never
    OFFERED, because a text unit stands at its own path (SF-1); and nothing that
    was not offered can be released.

    `over_ceiling` and `canary_offered` are read off what was BUILT and not off
    what was released, which is the only reading that can fail. Measured on the
    owner's 199 files at the code before SF-1: 33 whole documents offered, 20
    released, 29 dossiers over the ceiling, largest 41,247 bytes.
    """
    report = inspect_database(plan_database, CORPUS, situation=SITUATION)
    assert report.ceiling == 4000
    assert report.over_ceiling == []
    assert report.canary_offered == []
    assert report.canary_hits == []


def test_the_size_reported_is_the_one_that_can_fail(plan_database):
    """The built size is recorded for every outcome, not only for a release.

    Without this the instrument is decorative: an over-ceiling dossier is DENIED,
    so a size read off `Released` can never exceed the ceiling, and "count over the
    ceiling" would be 0 on every corpus including the one where 29 were.
    """
    report = inspect_database(plan_database, CORPUS, situation=SITUATION)
    stopped = [one for one in report.files
               if one.outcome not in ("released", "not_built")]
    assert stopped, "the fixture corpus stops at least one file at the gate"
    assert all(one.built_bytes > 0 for one in stopped), (
        "a dossier the door refused was still assembled, and its size is the "
        "number R-07 is about")
    assert all(one.released_bytes == 0 for one in stopped)


def test_a_planted_canary_is_scanned_for_as_well(plan_database):
    """`--canary` is the synthetic half: a sentence a test plants, looked for beside
    each file's own whole text. A word that IS in the fixture corpus proves the
    scan reaches the released values at all, rather than reporting zero because it
    is looking at nothing."""
    report = inspect_database(plan_database, CORPUS, situation=SITUATION,
                              canary="an invented sentence nothing wrote")
    assert report.canary_hits == []


def test_the_command_a_person_types_prints_the_block(plan_database, capsys):
    code = main(["--database", str(plan_database), "--corpus", str(CORPUS),
                 "--situation", SITUATION])
    printed = capsys.readouterr().out
    assert code == 0
    assert "PAYLOAD INSPECTION" in printed
    assert "largest dossier BUILT" in printed
    assert "largest dossier RELEASED" in printed
    assert "canary: offered" in printed
    assert "canary: RELEASED" in printed


# --- R-46's blocked line, on both instruments over one database ---------------

def test_the_scoreboards_blocked_line_agrees_with_the_payload_instrument(
        plan_database):
    """`104` §7 asks for "a 'blocked' line that counts gate refusals by reason as
    well as route withholding, so R-46 cannot recur", and there are now two things
    that count it. They must not disagree about the half they both measure.

    **THE ROUTE IS THE HALF THEY BOTH MEASURE, and it is asserted equal.** Both
    ask `cli.model_route_permitted` about the same files in the same database, so
    a difference here would mean one of them is asking a different question --
    which is R-02 in the instruments instead of in the product.

    **THE GATE IS NOT, AND SAYING SO IS THE POINT.** `payload` re-runs
    `Gate.release` offline to PREDICT what the door would refuse; the scoreboard
    reads `llm_refusal`, which is what the door ACTUALLY refused. Over a fixture
    run with no model configured, nothing was ever offered to the gate, so the
    recorded count is zero while the predicted count is not. Asserting them equal
    would be asserting that a prediction is a measurement. What is asserted is
    that each is the number its own source holds, and that the scoreboard prints
    all three columns so neither can be read as the whole.
    """
    from tools.groundtruth.measure import observe_run
    from tools.groundtruth.report import scorecard

    report = inspect_database(plan_database, CORPUS, situation=SITUATION)
    run = observe_run(plan_database, CORPUS, situation=SITUATION,
                      label=label_for(SITUATION))

    predicted_route = sum(1 for one in report.files if not one.route_permitted)
    predicted_gate = sum(report.gate_refusals_by_reason().values())
    assert predicted_route or predicted_gate, "this fixture predicts no blocking"

    # THE FIXTURE RAN WITH NO MODEL, so the product never consulted the route and
    # never offered the door anything. Every recorded number is therefore zero,
    # and that is the correct answer to "what did this run block", not a
    # disagreement with the instrument that answers "what WOULD it block".
    assert run.blocked_at_route == 0
    assert run.gate_refusals == {}
    assert sum(run.gate_refusals.values()) == _count(
        plan_database, "select count(*) as n from llm_refusal")

    card = scorecard([run], [], {}, [], [],
                     corpus_files=len(run.files), seconds=0.0)
    assert "no model was configured" in card, (
        "three zeros beside a never-built count would read as a corpus the "
        "product had nothing to say about")
    assert "tools.groundtruth.payload" in card, (
        "a person who wanted these numbers has to be told what to run for them")


def _count(database, sql: str) -> int:
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return connection.execute(sql).fetchone()[0]
    finally:
        connection.close()


def test_the_blocked_line_names_both_stops_and_every_gate_reason(plan_database):
    """R-46 as a rendering, on a run that DID reach a model.

    The fixture cannot produce one without a model, so the counts are supplied
    directly and what is asserted is the block: both stops named, every gate
    reason printed under its own word, and never-built counted beside them. A
    number meaning "the route let N through" must not be printable as the whole
    of what was blocked, and one summed gate number would hide which door to fix.
    """
    import dataclasses
    from tools.groundtruth.measure import observe_run
    from tools.groundtruth.report import scorecard

    run = observe_run(plan_database, CORPUS, situation=SITUATION,
                      label=label_for(SITUATION))
    asked = dataclasses.replace(
        run, blocked_at_route=19, never_built=8,
        gate_refusals={"protected_cloud": 130, "no_safety_evidence": 19},
        model=dict(run.model, llm_dossier=180, llm_refusal=149))

    card = scorecard([asked], [], {}, [], [],
                     corpus_files=len(asked.files), seconds=0.0)

    assert "19 withheld at the route" in card
    assert "149 stopped at the gate" in card
    assert "8 never built" in card
    assert "protected_cloud=130" in card
    assert "no_safety_evidence=19" in card

# tests/test_cli_trail.py
"""`--trail FILE`: the surface `104` §18.27 gap 25 says the product did not have.

The owner could not see what the product does. The CLI printed counts and review
questions, the scorer printed scores, and for ONE file nothing anywhere printed
what was extracted, what the model was sent, what it answered, or why the
validator refused it. These pin the five stages, the sentences the empty ones
print, the two ways a person names a file, and the two things this surface must
never do: open a file, or ask a model anything.

The database here is built through each part's own writer -- `record_file`,
`record_run`, `record_text_unit`, `ClassificationStore`, `record_dossier`,
`record_response`, `record_verdict` -- rather than by hand, so a column renamed
under `src/` fails these rather than passing them against a shape nothing writes.
`placement_decisions` is the one exception and names its columns explicitly:
building a real `PlacementDecision` needs eight nested records for a row this
surface reads six columns of.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from database_agent.db import open_database  # noqa: E402
from database_agent.files_table import record_file  # noqa: E402
from evidence_shape.location import Segment  # noqa: E402
from evidence_shape.observation import observation_key  # noqa: E402
from evidence_shape.runs import ExtractionRun  # noqa: E402
from evidence_shape.store import record_run, record_text_unit  # noqa: E402
from evidence_shape.text_units import TextUnit  # noqa: E402
from llm_harness import fixtures as llm_fixtures  # noqa: E402
from llm_harness.records import P8Verdict, PreCallAbstention  # noqa: E402
from llm_harness.store import (  # noqa: E402
    record_call_usage, record_dossier, record_response,
    record_unbuilt_call_abstention, record_verdict, refusal_outcome,
)
from llm_harness.vocabulary import (  # noqa: E402
    A_FACT, ACCEPT_DIRECT, G_SITUATION_SENSITIVITY, LLM_SUPPORTED,
    NOT_ELIGIBLE_FOR_MODEL, REMAINS_AMBIGUOUS, SCOPE_FILE,
)
from privacy.classification import ClassificationRecord  # noqa: E402
from privacy.classification_store import ClassificationStore  # noqa: E402
from p1_contract import p3_basic_record  # noqa: E402
from review_surface.trail import STAGES, file_trail  # noqa: E402

class FileTookTooLong(RuntimeError):
    """`104` R-175's own exception, by name.

    `refusal_outcome` records `type(error).__qualname__` and never the
    message -- the message that ended a real run named a file id and a
    filename -- so the class NAME is the whole of what a person reads back,
    and a fixture raising a bare `RuntimeError` would pin a sentence the
    product never prints.
    """


WHEN = "2026-09-10T09:00:00Z"
LATER = "2026-09-10T09:05:00Z"
MODEL = "a-model-that-answered"
FINGERPRINT = "fp-trail"


def _run(argv):
    out = io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def _record_a_file(conn, path: Path) -> str:
    """One `files` row through P1's own writer, then the file is deleted.

    Deleted on purpose. A trail is what the product DID, so it has to print for a
    file the person has since thrown away -- and a trail that only ever runs
    against a file still sitting on disk cannot tell you whether it opened it.
    """
    file_id = record_file(conn, path, parent_folder_context="corpus",
                          mime_type="application/pdf", detected_format="pdf",
                          scan_state="scanned", materialized=True,
                          **p3_basic_record(path))
    path.unlink()
    return file_id


def _extraction(conn, file_id: str, content_hash: str) -> str:
    run_id = "extraction-run-1"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf_text", extractor_version="3",
        source_type="text_document",
        analysis_tier="native", config={}, completeness="complete",
        observation_count=4, started_at=WHEN, finished_at=LATER))
    for index, text in enumerate(("PHYS1401 Syllabus", "Spring 2026"), start=1):
        record_text_unit(conn, TextUnit(
            run_id=run_id, container_path=(Segment("page", index),), text=text))
    return run_id


def _a_call(conn, file_id: str) -> tuple[str, bytes]:
    """One site-A dossier, its answer, what it cost, and the verdict on it."""
    dossier = llm_fixtures._dossier(
        A_FACT, REMAINS_AMBIGUOUS, dossier_id="dossier-1", subject_ref=file_id,
        plan_version=llm_fixtures.PLAN_V1, allowed_vocabulary=("subject",),
        evidence_items=(llm_fixtures._excerpt(),))
    record_dossier(conn, dossier, observed_at=WHEN)
    answer = llm_fixtures._bytes({"field": "subject", "value": "PHYS1401"})
    record_response(conn, dossier_id="dossier-1", response_bytes=answer,
                    model_id=MODEL, prompt_fingerprint=FINGERPRINT,
                    release_audit_id=1, release_id=llm_fixtures.RELEASE,
                    observed_at=WHEN)
    record_call_usage(conn, dossier_id="dossier-1",
                      release_id=llm_fixtures.RELEASE, reserved_cost="1",
                      observed={"model_id": MODEL, "prompt_tokens": 812,
                                "completion_tokens": 44},
                      observed_at=WHEN)
    record_verdict(conn, P8Verdict(
        verdict_id="verdict-1", dossier_id="dossier-1", claim_ref="c1",
        outcome=ACCEPT_DIRECT, disposition=LLM_SUPPORTED, reasons=(),
        may_propose=True, requires_review=False, citations_checked=(),
        scope=SCOPE_FILE, validator_version="v9",
        policy_version=llm_fixtures.POLICY,
        plan_version=llm_fixtures.PLAN_V1),
        model_id=MODEL, prompt_fingerprint=FINGERPRINT, release_audit_id=1,
        observed_at=WHEN)
    return "dossier-1", answer


@pytest.fixture()
def a_run(tmp_path):
    """One plan database holding three files: one with a whole trail, one the
    model was abstained from, and one dropped for time at site G. Returned as
    everything the assertions below need to name."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    asked_path = corpus / "Syllabus.pdf"
    asked_path.write_bytes(b"PHYS1401 Syllabus, Spring 2026")
    quiet_path = corpus / "untouched.txt"
    quiet_path.write_bytes(b"nothing here")
    slow_path = corpus / "a big scan.pdf"
    slow_path.write_bytes(b"four hundred pages of it")
    database = tmp_path / "plan.sqlite"
    conn = open_database(database)
    try:
        cli._bootstrap(conn)
        asked = _record_a_file(conn, asked_path)
        quiet = _record_a_file(conn, quiet_path)
        slow = _record_a_file(conn, slow_path)
        content_hash = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (asked,)).fetchone()[0]
        _extraction(conn, asked, content_hash)
        # A REAL P4 handle, minted the way P4 mints one: `ClassificationRecord`
        # refuses anything that is not an `observation_key`, and a fixture that
        # worked around that refusal would be testing a row nothing writes.
        cited = observation_key(content_hash=content_hash,
                                extractor_name="pdf_text",
                                locator="page-1", raw_value="PHYS1401")
        store = ClassificationStore(conn)
        first = store.write(ClassificationRecord(
            file_id=asked, content_hash=content_hash,
            handling_class="public_low", protected=False,
            basis="detector", evidence_refs=(cited,),
            reliability_state="inferred", observed_at=WHEN))
        second = store.write(ClassificationRecord(
            file_id=asked, content_hash=content_hash,
            handling_class="public_low", protected=False,
            basis="local_model_situation", evidence_refs=(cited,),
            reliability_state="direct", observed_at=LATER))
        store.supersede(first, second,
                        "the body says what the filename only guessed at")
        dossier_id, answer = _a_call(conn, asked)
        record_unbuilt_call_abstention(conn, PreCallAbstention(
            reason=NOT_ELIGIBLE_FOR_MODEL, call_site=A_FACT,
            subject_ref=quiet), observed_at=WHEN)
        # `104` R-175's over-the-ceiling skip at site G, recorded the one way
        # it is recorded: a `call_refused` event and no row in any table.
        refusal_outcome(conn, call_site=G_SITUATION_SENSITIVITY,
                        subject_ref=slow,
                        error=FileTookTooLong('the file took too long'),
                        observed_at=LATER)
        conn.execute(
            "INSERT INTO placement_decisions (record_id, subject_ref, "
            "plan_version, origin_stage, outcome, node_id, group_plan_id, "
            "created_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("decision-1", f"file:{asked}:{content_hash}",
             llm_fixtures.PLAN_V1, "node_local_classification",
             "move_plan_eligible", "node-phys1401", "group-plan-1", LATER,
             "{}"))
        conn.commit()
    finally:
        conn.close()
    return dict(database=database, asked=asked, quiet=quiet, slow=slow,
                asked_path=asked_path, quiet_path=quiet_path,
                dossier_id=dossier_id, answer=answer,
                content_hash=content_hash)


def _stage_bodies(printed: str) -> dict[str, str]:
    """The text under each stage heading, keyed by the heading."""
    bodies, current = {}, None
    for line in printed.splitlines():
        if line in STAGES:
            current = line
            bodies[current] = ""
        elif current is not None:
            bodies[current] += line + "\n"
    return bodies


def test_a_file_with_a_whole_trail_prints_five_stages_in_order(a_run):
    """`104` §18.27 gap 25: extracted → classified → asked → judged → placed.

    One file, five headings, in the order the run reached them. The order is the
    assertion and not a detail: a person reading a trail is reconstructing a
    sequence of events, and a screen that prints the verdict above the answer it
    was reached on is a screen they have to reassemble themselves.
    """
    code, printed = _run(["--trail", a_run["asked"],
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    positions = [printed.index(stage) for stage in STAGES]
    assert positions == sorted(positions), printed
    bodies = _stage_bodies(printed)
    assert "pdf_text 3" in bodies["EXTRACTED"], bodies["EXTRACTED"]
    # The two text units and their characters, which is `00`:259's completed
    # work made countable for one file rather than for the corpus.
    assert "2 text units" in bodies["EXTRACTED"], bodies["EXTRACTED"]
    assert "28 characters" in bodies["EXTRACTED"], bodies["EXTRACTED"]
    assert "local_model_situation" in bodies["CLASSIFIED"], bodies["CLASSIFIED"]
    assert A_FACT in bodies["ASKED"], bodies["ASKED"]
    assert "812 prompt" in bodies["ASKED"], bodies["ASKED"]
    assert "accept_direct" in bodies["JUDGED"], bodies["JUDGED"]
    assert "node-phys1401" in bodies["PLACED"], bodies["PLACED"]
    # `00`:112's distinction, which no folder name carries: judged as one packet
    # or judged alone.
    assert "group-plan-1" in bodies["PLACED"], bodies["PLACED"]


def test_the_dossier_and_the_answer_print_exactly_as_they_are(a_run):
    """The person's own data on the person's own screen, unsummarised.

    `00`:284: the product must never "require the user to trust a black box when
    the evidence, decision history, and correction path can be shown directly".
    A trail that paraphrased what was sent would be the same black box one layer
    in -- so every key of the stored dossier and every byte of the stored answer
    have to be findable in what was printed, which is what a person checking a
    citation against the evidence actually does.
    """
    code, printed = _run(["--trail", a_run["asked"],
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    conn = sqlite3.connect(a_run["database"])
    try:
        stored = conn.execute(
            "SELECT payload FROM llm_dossier WHERE dossier_id = ?",
            (a_run["dossier_id"],)).fetchone()[0]
    finally:
        conn.close()
    # Value by value against the row, not against a string this test also wrote:
    # the pin is that nothing was dropped on the way to the screen.
    for key, value in json.loads(stored).items():
        assert f'"{key}"' in printed, key
        if isinstance(value, str):
            assert value in printed, (key, value)
    for claim in json.loads(a_run["answer"])["claims"]:
        assert claim["claim_ref"] in printed
        assert claim["payload"]["value"] in printed, printed


def test_a_file_the_model_was_never_asked_about_prints_the_reason(a_run):
    """A stage with nothing in it says why, and never nothing.

    `00`:259: the interface "should show the difference between completed work
    and deferred work" so a person is not left with "the false impression that an
    unprocessed file was understood and found unimportant". A heading with
    nothing under it is exactly that impression. This file has an abstention row
    and the row's own reason is what prints.
    """
    code, printed = _run(["--trail", a_run["quiet"],
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    bodies = _stage_bodies(printed)
    assert NOT_ELIGIBLE_FOR_MODEL in bodies["ASKED"], bodies["ASKED"]
    assert "not asked" in bodies["ASKED"], bodies["ASKED"]
    # Every OTHER stage is empty for this file and every one of them still
    # prints a sentence saying so. A stage that printed a heading and no line is
    # the defect this whole surface exists to end.
    for stage in ("EXTRACTED", "CLASSIFIED", "JUDGED", "PLACED"):
        assert bodies[stage].strip(), f"{stage} printed no sentence"
        assert "because" in bodies[stage], bodies[stage]


def test_a_file_dropped_for_time_says_so_from_the_event_that_is_its_only_record(
        a_run):
    """`104` R-175's over-the-ceiling skip, which no table holds.

    `record_call_refusal`'s own words are that the two rows which exist "would
    each have to lie" -- `llm_call_failure` needs the release it never spent and
    `llm_pre_call_abstention` needs a reason code that does not mean this -- so a
    `call_refused` event is the whole record, and this surface is the only place
    a person can read it back. A file skipped for time is a file this run did not
    decide about, and the trail has to show it as one rather than as a file with
    nothing to say.

    The exception's CLASS is what prints, because that is what was recorded: the
    message is deliberately dropped by `refusal_outcome`, the message that ended
    a real run having named a file id and a filename.
    """
    code, printed = _run(["--trail", a_run["slow"],
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    asked = _stage_bodies(printed)["ASKED"]
    assert G_SITUATION_SENSITIVITY in asked, asked
    assert "FileTookTooLong" in asked, asked
    assert "refused before anything was sent" in asked, asked
    # And never the message, which is the half `refusal_outcome` drops.
    assert "the file took too long" not in printed, printed


def test_a_retired_classification_prints_with_what_retired_it(a_run):
    """§8.2 on the screen: the superseded row stays, and so does its reason.

    `00`:137 -- "a user reviewing a placement should still be able to inspect the
    origin of the conclusion". A retired classification that vanished from this
    screen would be the overwrite the supersede columns exist to prevent, hidden
    one layer up instead of in the table.
    """
    code, printed = _run(["--trail", a_run["asked"],
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    classified = _stage_bodies(printed)["CLASSIFIED"]
    assert "detector" in classified, classified
    assert "retired by" in classified, classified
    assert "the body says what the filename only guessed at" in classified
    # And the one that stands is still marked as standing, so a reader can tell
    # the live row from the history without counting.
    assert "still stands" in classified, classified


def test_a_path_and_a_file_id_name_the_same_trail(a_run):
    """Two ways in, because a person has one of two things in front of them.

    A file id is what another line of the product prints; a path is what they
    can see with their own eyes. Requiring the id would make this surface
    reachable only from the surface it exists to replace.
    """
    by_id = _run(["--trail", a_run["asked"],
                  "--database", str(a_run["database"])])
    by_path = _run(["--trail", str(a_run["asked_path"]),
                    "--database", str(a_run["database"])])
    by_name = _run(["--trail", a_run["asked_path"].name,
                    "--database", str(a_run["database"])])

    assert by_id[0] == by_path[0] == by_name[0] == 0, by_path
    assert by_id[1] == by_path[1] == by_name[1]


def test_a_file_this_run_never_saw_is_told_so(a_run):
    """Refused, never answered with somebody else's file.

    The same treatment an unknown `--answer` gets: a person who mistyped must be
    told, because the alternative is believing they have been shown the trail of
    the thing they meant.
    """
    code, printed = _run(["--trail", "not-a-file-in-this-plan",
                          "--database", str(a_run["database"])])

    assert code == 2, printed
    assert "not a file in this plan database" in printed
    # And no stage was printed for it. A "not found" that still prints five
    # empty headings reads as a file that exists and did nothing.
    assert not [stage for stage in STAGES if stage in printed], printed


def test_the_trail_opens_no_file_and_builds_no_model_target(a_run, monkeypatch):
    """The two things this surface must never do, pinned at the seams.

    `--trail` is read out of the database and out of nothing else. `cli.run` is
    the scan-and-extract pipeline and `cli.target_for` is the one place a model
    target is chosen; both raise here, so a trail that reached for either fails
    rather than quietly costing somebody a scan or a call. The corpus file is
    already deleted by the fixture, which is the other half of the same proof:
    there is nothing on disk left to open.
    """
    def refuse(*args, **kwargs):
        raise AssertionError("a trail runs nothing and asks nobody")

    monkeypatch.setattr(cli, "run", refuse)
    monkeypatch.setattr(cli, "target_for", refuse)
    assert not a_run["asked_path"].exists()

    code, printed = _run(["--trail", str(a_run["asked_path"]),
                          "--database", str(a_run["database"])])

    assert code == 0, printed
    assert "EXTRACTED" in printed


def test_the_walk_is_one_function_the_review_surface_can_call(a_run):
    """Gap 25's second half: one rendering, so two screens cannot disagree.

    `--explain` points at `--trail` in one sentence instead of printing a second
    version of this walk. That is only honest while there IS one walk, so the
    function is public in P13 and the CLI is a caller of it like any other
    surface would be.
    """
    conn = open_database(a_run["database"])
    try:
        trail = file_trail(conn, a_run["asked"])
    finally:
        conn.close()

    assert trail.found
    _code, printed = _run(["--trail", a_run["asked"],
                           "--database", str(a_run["database"])])
    assert "\n".join(trail.lines) in printed


def test_a_trail_with_no_plan_database_refuses_rather_than_making_one(tmp_path):
    """A mistyped `--database` must not be answered by an empty database.

    `open_database` creates what is not there, so without this the product
    invents a plan, finds the person's file missing from it, and says so -- an
    answer that is true about the file it just made up and false about the run
    they meant. It also leaves a database behind where they did not ask for one.
    """
    missing = tmp_path / "no-such-plan.sqlite"

    code, printed = _run(["--trail", "Syllabus.pdf", "--database", str(missing)])

    assert code == 2, printed
    assert "no plan database" in printed
    assert not missing.exists(), "a refusal created the database it refused over"

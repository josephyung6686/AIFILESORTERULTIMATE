# tests/integration/test_site_e_reuses_its_answer.py
"""`104` §18.31: a second run does not buy site E's answers a second time.

**The defect, in the register's own words.** §18.31, of the site E build: *"the E
store is run-local (a second run re-asks)"*, and §18.33 restates it as the row
owed. The verdict rows were durable all along -- an `llm_dossier`, an
`llm_response` and an `llm_verdict` per answered file -- and `template_named_by_
verdict` read them only for the verdict the call in hand had just produced. So a
person who ran the product twice over the same folder paid for a local template
call for every unfitting file both times, and on a real corpus most files lack
`work_type`, which is most of the roster.

**The rule is site A's and there is no second one.** `104` R-13 and `00`:44: an
answer is *"tied to the content hash and the exact process that produced it"*, and
the key is `store.CALL_IDENTITY_DIMENSIONS` -- ten terms, refused if one is missing
and refused if an eleventh appears. `cli.template_call_identity` says what each of
the ten is at site E; `prior_call` finds the dossier that identity last reached;
`cli.template_named_before` reads the standing accepted verdict off it; and
`record_call_reuse` writes the row that says a question was not asked again.

**WHY THE VALIDATOR HALF IS PINNED ON THE READER AND NOT THROUGH A FOURTH RUN.**
`104` R-127 asks that a validator change re-evaluate cached responses rather than
retain obsolete verdicts, and at this site that means asking again. Measuring it
end to end would mean re-asking under a moved validator over a dossier whose bytes
did not change -- and a generic site's `verdict_id` is `{dossier_id}:{claim_ref}`
with no term for the judge (site A adds `fact_validation.version_address`, this
site has none), so the second conclusion arrives at the first one's address and
`record_verdict` refuses it, correctly. The rule is therefore stated where it is
decided: `template_named_before`, with the version moved the way
`test_a_fact_revalidates_under_a_new_validator._bump` moves site A's -- patching
the one name that both the stamp and the comparison read at call time.

**NO OLLAMA AND NO NETWORK.** The stub server, the corpus and the answers are
`test_site_e_per_file_template`'s, imported rather than copied so the two files
cannot drift into measuring two different site Es.
"""
from __future__ import annotations

import dataclasses
import io
import os
import re
import sqlite3
from pathlib import Path

import pytest

import cli
from llm_harness import validation as p8_validation
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from review_surface.trail import file_trail
from test_local_model_fact_pass import MODEL_ID, StubOllama, _corpus, dossier_in
from test_site_e_per_file_template import (
    DESIGNED, LABEL, SITUATION, _dispatching, _template_answer,
)


def _one_run(corpus: Path, database: Path) -> tuple[str, tuple[str, ...]]:
    """One `cli.main` over `corpus` into `database`, with the stub answering.

    The environment is set and put back per run rather than once per module: two
    runs of one product is what this file is about, and a fixture that left the
    stub's URL behind would make the second run's result depend on the first
    run's teardown.
    """
    with StubOllama(answer=_dispatching(_template_answer)) as stub:
        previous = {key: os.environ.get(key)
                    for key in (LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME)}
        os.environ[LOCAL_MODEL_NAME] = MODEL_ID
        os.environ[LOCAL_BASE_URL_NAME] = stub.base_url
        try:
            out = io.StringIO()
            code = cli.main(
                [str(corpus), "--situation", SITUATION, "--label", LABEL,
                 "--user", "t", "--database", str(database)], out=out)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    assert code == 0, out.getvalue()
    return out.getvalue(), tuple(stub.prompts())


def _asked_at_e(prompts: tuple[str, ...]) -> int:
    """How many site-E dossiers actually crossed the seam on this run.

    Counted off the BYTES the stub received, because the claim is that no call was
    made -- a count taken from the store would be counting rows the reuse
    deliberately does not write and would pass if the call were made and the row
    were simply dropped.
    """
    return sum(1 for prompt in prompts
               if dossier_in(prompt).get("call_site") == cli.E_TEMPLATE)


def _rows(database: Path, sql: str, *params) -> list[sqlite3.Row]:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


class _Twice:
    """Two runs of one command over one corpus and one database."""

    def __init__(self, database: Path, first, second) -> None:
        self.database = database
        self.first_report, self.first_prompts = first
        self.second_report, self.second_prompts = second


@pytest.fixture(scope="module")
def twice(tmp_path_factory) -> _Twice:
    """MODULE-SCOPED for `test_site_e_per_file_template._Run`'s reason: every
    test below asks a different question of the SAME pair of runs, and two
    corpora would let one test drift into measuring different files from its
    neighbour. The pair is what is under test, so it is built once."""
    corpus = _corpus(tmp_path_factory.mktemp("twice"))
    database = corpus.parent / "plan.sqlite"
    first = _one_run(corpus, database)
    second = _one_run(corpus, database)
    return _Twice(database, first, second)


# --- the defect itself ----------------------------------------------------------

def test_a_second_run_over_the_same_corpus_asks_site_e_nothing(twice):
    """`104` §18.31, stated as an assertion: the answers are not bought twice.

    SABOTAGE: delete the `prior_call` lookup in `ask_for_a_template`, or let the
    identity carry a term that moves between two runs of one checkout (a minted
    id, a timestamp, the policy's VERSION rather than its content). The second
    count goes back up to the first and this goes red.
    """
    assert _asked_at_e(twice.first_prompts) > 0, (
        "no file was asked for a template of its own on the first run, so this "
        "file is measuring a reuse of nothing")
    assert _asked_at_e(twice.second_prompts) == 0, (
        "the second run over the same corpus, the same bytes, the same prompt "
        "and the same model asked site E again -- which is the whole of `104` "
        "§18.31: the verdict rows are durable and nothing read them back")


def test_the_answers_are_still_there_on_the_second_run(twice):
    """A reuse is not a silence. The file is still held under the template the
    model designed for it, which is what `template_for` answers and what the
    gate's §7.3 arm reads -- so the second run's screen names as many templates
    as the first, and no call behind them."""
    designed = twice.second_report.count(DESIGNED)
    assert "Templates of their own:" in twice.second_report
    assert designed == twice.first_report.count(DESIGNED), (
        "the second run named a different number of templates from the first, "
        "so the reuse changed the answer rather than the spend")


def test_the_second_run_says_the_answers_were_not_bought_again(twice):
    """`00`:259 for spend rather than for coverage. `store.record_call_reuse`:
    *"a run that quietly makes fewer calls than the last one is
    indistinguishable from a run that silently dropped files"*. The block reads
    `0 of N files were asked` on the second run, so the header has to say where
    the templates came from or the two numbers in it look like a contradiction.

    SABOTAGE: drop the `reused` line from `_print_template_pass`, or fold
    `reused` into the loop that prints the five partitioning sentences. The
    first goes red here; the second double-counts a file and goes red in
    `test_the_five_sentences_still_partition_the_roster`.
    """
    said = " ".join(twice.second_report.split())
    reused = len(_rows(twice.database,
                       "SELECT reuse_id FROM llm_call_reuse WHERE call_site = ?",
                       cli.E_TEMPLATE))
    files = len(_rows(twice.database, "SELECT file_id FROM files"))
    assert reused > 0
    assert f"{reused} of those answers" in said and "not bought again" in said, (
        f"the second run reused {reused} answers and its report does not say so")
    assert f"0 of {files} files were asked for a folder template" in said, (
        "the header counts a reused answer as a file this run asked about")


def test_the_reuse_row_names_the_answer_it_reused(twice):
    """One row per question not asked, and it names WHICH answer stood in for it.

    The row is `llm_call_reuse` -- site A's own, at another site -- so a person
    counting a run's spend finds both sites' savings in one table, and the
    `prior_dossier_id` on it is a dossier this database actually holds.
    """
    rows = _rows(twice.database,
                 "SELECT * FROM llm_call_reuse WHERE call_site = ? "
                 "ORDER BY rowid", cli.E_TEMPLATE)
    dossiers = {row["dossier_id"] for row in _rows(
        twice.database, "SELECT dossier_id FROM llm_dossier WHERE call_site = ?",
        cli.E_TEMPLATE)}
    assert rows, "no reuse row was written for a run that asked nothing at site E"
    for row in rows:
        assert row["prior_dossier_id"] in dossiers, (
            "the reuse names a dossier this plan database does not hold")
        assert row["subject_ref"] in {
            file["file_id"] for file in _rows(
                twice.database, "SELECT file_id FROM files")}


def test_the_trail_of_a_reused_file_says_it_was_not_asked_again(twice):
    """`104` §18.33 gap 25's surface, reading gap 25's own table. A person who
    opens the file's trail sees the second run's non-call beside the first run's
    call, rather than a gap where a second call used to be."""
    subject = _rows(twice.database,
                    "SELECT subject_ref FROM llm_call_reuse WHERE call_site = ?",
                    cli.E_TEMPLATE)[0]["subject_ref"]
    conn = sqlite3.connect(f"file:{twice.database}?mode=ro", uri=True)
    try:
        trail = file_trail(conn, subject)
    finally:
        conn.close()
    printed = " ".join("\n".join(trail.lines).split())
    assert trail.found
    assert f"{cli.E_TEMPLATE} was not asked again" in printed, printed


def test_the_five_sentences_still_partition_the_roster(twice):
    """`reused` is a sub-count of `chosen` and not a sixth bucket, so the five
    lines under the header plus the answers still add up to the roster.

    Read off the run's own report rather than off a `TemplatePass` built here: a
    partition asserted on a hand-made record is a claim about a constructor.

    THE BLOCK AND NOT THE REPORT. Site G's block prints four of these five
    phrases about its own counters and prints them EARLIER on the screen, which
    is the shape `_print_template_pass` deliberately shares with it -- so a
    search over the whole report answers with site G's numbers and measures
    nothing here.
    """
    said = " ".join(
        twice.second_report.split("Templates of their own:")[1].split())

    header = re.search(
        r"^ ?(\d+) of (\d+) files? (?:was|were) asked .*? "
        r"and (\d+) (?:was|were) given one", said)
    assert header, said
    _asked, files, named = (int(header.group(index)) for index in (1, 2, 3))
    counted = named + sum(
        int(re.search(rf"(\d+) {word}", said).group(1))
        for word in ("already fit", "not asked, nothing to read",
                     "asked and left alone", "no target", "out of time"))
    assert counted == files, (
        f"the block accounts for {counted} of {files} files: a counter is being "
        f"printed twice or not at all")


# --- what makes it a fresh question ---------------------------------------------

def test_a_changed_prompt_row_asks_again(twice, tmp_path_factory):
    """`00`:44's second sentence: the key *"makes model or prompt changes
    auditable"*. A new text is a new question, whatever the file says.

    The prompt is moved the way a prompt row moves -- its `call_site_version`,
    one of the six terms `fingerprint.prompt_fingerprint` hashes -- and only site
    E's, because `observe_prompt` serves four sites and moving all four would
    measure the run rather than this site.

    SABOTAGE: drop `prompt_fingerprint` from `template_call_identity`. The
    reuse then survives a prompt nobody approved and this goes red.
    """
    corpus = _corpus(tmp_path_factory.mktemp("prompt_moved"))
    database = corpus.parent / "plan.sqlite"
    first = _one_run(corpus, database)
    assert _asked_at_e(first[1]) > 0

    real = cli.observe_prompt

    def moved(call_site: str):
        row = real(call_site)
        if call_site != cli.E_TEMPLATE:
            return row
        return dataclasses.replace(
            row, call_site_version=f"{row.call_site_version}+moved")

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "observe_prompt", moved)
        second = _one_run(corpus, database)

    assert _asked_at_e(second[1]) == _asked_at_e(first[1]), (
        "site E reused an answer given under a different prompt, so the run "
        "reports what the OLD text designed as though this text had designed it")


def test_a_verdict_another_validator_wrote_is_not_reused(twice):
    """`104` R-127 / `105` §14.7: *"validator or normalisation changes must
    re-evaluate cached responses rather than retain obsolete verdicts"*.

    Read on the run's own rows: the standing accepted verdict names the template
    it named, and the same row under a moved validator names nothing -- so the
    caller asks. The version is moved at the ONE name both the stamp
    (`validation._make_verdict`) and this comparison read at call time; patching
    only one of them would test a fixture rather than the rule, which is
    `test_a_fact_revalidates_under_a_new_validator._bump`'s own argument.

    SABOTAGE: compare against a constant captured at import, or drop the version
    check entirely. The second assertion goes red.
    """
    dossier_id = _rows(
        twice.database,
        "SELECT d.dossier_id AS dossier_id FROM llm_dossier d "
        "JOIN llm_verdict v ON v.dossier_id = d.dossier_id "
        "WHERE d.call_site = ? AND v.superseded_by IS NULL "
        "AND v.outcome IN (?, ?) ORDER BY d.rowid",
        cli.E_TEMPLATE, cli.ACCEPT_DIRECT, cli.ACCEPT_CONTEXT_SUPPORTED,
    )[0]["dossier_id"]
    conn = sqlite3.connect(f"file:{twice.database}?mode=ro", uri=True)
    # THE FACTORY THE PRODUCT'S OWN CONNECTION CARRIES. `store.standing_verdicts`
    # reads its rows by NAME, as every reader in `llm_harness` does, so a
    # connection opened here without it would be asking the reader to work
    # against a shape the product never hands it.
    conn.row_factory = sqlite3.Row
    try:
        answered = cli.template_named_before(conn, dossier_id)
        assert answered is not None and answered[1] == DESIGNED

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(
                p8_validation, "COMPONENT_VERSION",
                f"{p8_validation.COMPONENT_VERSION}+r127")
            assert cli.template_named_before(conn, dossier_id) is None, (
                "a verdict written by a validator this checkout no longer runs "
                "went on suppressing the question under a conclusion this "
                "validator does not reach")
    finally:
        conn.close()

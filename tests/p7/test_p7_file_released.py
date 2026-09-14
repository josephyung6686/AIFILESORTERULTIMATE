# tests/p7/test_p7_file_released.py
"""THE RULING (the owner, 13 Sep 2026, late): *"for these situations it is ok to
just ask the person: a mechanism like 'we found these files, should we not upload
them to the cloud?' -- totally doable."*

`--file-held` (beside this, in `test_p7_file_held.py`) was half the answer: it let
a person file a held record by hand and deliberately opened no door. This is the
other half. A run that holds files now PUTS THE QUESTION at the end of its report,
and `--release FILE_ID` is the answer that says the file is not what the rules took
it for -- it is ordinary, and it may be sent.

Four facts pin it, and each is a rule this gesture must satisfy rather than a new
one it invents:

* THE ROW IS THE PERSON'S OWN. `learning_seam.reclassify` writes `basis="user"` at
  `reliability_state="user_confirmed"`, which `classification_store.strongest`
  ranks above every system state, so `_outranked_by` lets it retire the rules' hold
  and lets no later run of the rules retire it back.
* THE CLOUD DOOR OPENS BY ITSELF. `"user"` is already a `CLOUD_CLEARING_BASES`
  member, so the released file gets a cloud target at the situation site where a
  held one has none -- and `src/privacy` is untouched by this change.
* A FILE NOTHING IS HOLDING IS REFUSED, by a sentence, the way `apply_file_held`
  refuses a file id no run has recorded. Releasing what was never held would hand
  an ordinary file a clearance nobody offered the person.
* THE SCREEN ASKS. The run's closing block names each held file, says why in one
  phrase, and prints both gestures with the real id -- and stops naming a file the
  person has released.

THE RUN AT THE TOP OF THIS FILE IS REAL AND USES NO MODEL. `cli.main` over two
text files with no key and no local model: the rules hold `Passport syllabus.txt`
on `identity`'s own work type in a naming zone, which is a hold written by
`classifier` during P1-P7 and needs nobody's model. One run, shared, because a
`cli.main` run is the most expensive thing in this file and every test below asks
about the same two files.
"""
from __future__ import annotations

import io
import shutil

import pytest

import cli
from database_agent.db import open_database
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import G_SITUATION_SENSITIVITY
from privacy.classification_store import ClassificationStore
from privacy.release import ModelTarget
from privacy.vocabulary import USER, USER_CONFIRMED
from readers.model_deepseek import CLOUD, PROVIDER
from readers.model_routing import FAST, LOGIC, REASONING, TierRouting

#: The file the rules hold: `passport` is one of `identity`'s work types and it
#: is in the filename, which is a naming zone -- the one place a single term
#: still takes a hold since the corroboration rule of 13 Sep 2026.
HELD_NAME = "Passport syllabus.txt"
#: Its twin, held by nothing, so a test that finds one held file is finding a
#: hold rather than finding a run that held everything.
FREE_NAME = "PHYS 1401 syllabus.txt"

SITUATION = "academic.coursework"
LABEL = "School"


def _corpus(root):
    corpus = root / "corpus"
    corpus.mkdir(parents=True)
    (corpus / FREE_NAME).write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / HELD_NAME).write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Date of birth: 1 January 1990\n")
    return corpus


@pytest.fixture(scope="module")
def a_run_that_held_a_file(tmp_path_factory):
    """One `cli.main` run over the two files, and what it printed.

    NO MODEL OF ANY KIND. `tests/conftest.py` removes the key and the local model
    name from the environment for the whole suite, and this run wants neither: the
    hold is the rules' own and the screen it produces is the thing under test.
    """
    root = tmp_path_factory.mktemp("released")
    corpus = _corpus(root)
    database = root / "plan.sqlite"
    out = io.StringIO()
    code = cli.main(
        [str(corpus), "--situation", SITUATION, "--label", LABEL,
         "--user", "t", "--database", str(database)], out=out)
    assert code == 0, out.getvalue()
    return database, out.getvalue()


@pytest.fixture()
def database(a_run_that_held_a_file, tmp_path):
    """A WRITABLE COPY of that run's database, one per test.

    `--release` supersedes a row, so a test that ran against the shared database
    would decide what the next test starts from -- and the suite is run in a
    random order, so which test that is would change between runs.
    """
    source, _said = a_run_that_held_a_file
    copy = tmp_path / "plan.sqlite"
    shutil.copyfile(source, copy)
    conn = open_database(copy)
    yield conn
    conn.close()


def _file_id(conn, filename: str) -> str:
    (row,) = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                          (filename,)).fetchall()
    return row["file_id"]


def _current(conn, file_id: str):
    (row,) = conn.execute("SELECT content_hash FROM files WHERE file_id = ?",
                          (file_id,)).fetchall()
    return ClassificationStore(conn).current(file_id, row["content_hash"])


def _scan_run_id(conn) -> str:
    (row,) = conn.execute(
        "SELECT DISTINCT scan_run_id FROM stat_cache_verdicts").fetchall()
    return row["scan_run_id"]


def _no_outcome(_conn, _file_id, _content_hash):
    """The detector's `explain`, stubbed: the screen's store read is what is
    under test and re-running the recogniser would measure it instead."""
    return None


def _no_precaution(_conn, _outcome, *, file_id, content_hash):
    """`precaution_report` answering "no domain", which is the arm
    `_why_a_file_is_held` shortens the phrase for rather than guessing."""
    return None


def _cloud_only() -> TierRouting:
    """A key and no local model, so a file the cloud may not see gets NO target.

    That is what makes "a cloud target where it had none" a measurement rather
    than a change of destination: on this routing the held file's answer is
    `None`, not `LOCAL`.
    """
    client = ModelClient(
        model_target=ModelTarget(locality=CLOUD, model_id="a-logician",
                                 provider=PROVIDER),
        invoke=lambda payload: b'{"claims": []}')
    return TierRouting(tier_of_call_site=cli.TIER_OF_CALL_SITE,
                       client_of_tier={REASONING: client, LOGIC: client,
                                       FAST: client})


# --- the run asks, and the question names both gestures -------------------------


def test_the_closing_screen_names_the_held_file_and_both_gestures(
        a_run_that_held_a_file):
    """THE OWNER'S RULING, on the screen. Until it, a held file was counted and
    never asked about: `_print_the_holds` said "held and not asked ... They stay
    protected and stay on this device", which was the whole of the person's part
    in it.

    THE ID AND NOT `FILE_ID`, because a person cannot type `FILE_ID`. The header
    names the placeholder once, exactly as `--answer`'s help does, and every line
    under a file carries that file's own id.

    SABOTAGE: drop the `_the_files_being_held` call from `downstream` and every
    line below goes red at once.
    """
    database, said = a_run_that_held_a_file
    conn = open_database(database)
    try:
        held = _file_id(conn, HELD_NAME)
        free = _file_id(conn, FREE_NAME)
    finally:
        conn.close()
    flat = " ".join(said.split())

    assert "1 file is being held here" in flat, (
        "the run held a file and the closing block did not say so")
    assert HELD_NAME in said
    assert f"--file-held {held}" in said, "the keep-it-here gesture, typable"
    assert f"--release {held}" in said, "the it-is-ordinary gesture, typable"
    assert "identity material" in flat, (
        "the phrase says WHY, and for a rules hold that is the safety domain "
        "the detector names -- not a bare 'protected'")
    # The twin is held by nothing, so the block is about a hold and not about
    # the corpus.
    assert f"--release {free}" not in said


def test_no_block_is_printed_where_nothing_is_held(tmp_path):
    """`_print_the_holds`' own rule at the site one along: a heading over a hold
    nobody has invites a person to wonder which of their files it is about, and
    the answer is none of them."""
    corpus = tmp_path / "free"
    corpus.mkdir()
    (corpus / FREE_NAME).write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    out = io.StringIO()
    code = cli.main(
        [str(corpus), "--situation", SITUATION, "--label", LABEL, "--user", "t",
         "--database", str(tmp_path / "plan.sqlite")], out=out)
    assert code == 0, out.getvalue()
    assert "being held here" not in out.getvalue()


# --- the gesture writes the person's own row ------------------------------------


def test_release_writes_a_user_row_that_supersedes_the_rules_hold(database):
    """§8.4's "can be revised by the user", through P7's own seam.

    EVERY FIELD IS CHECKED, because each is a separate claim: the basis is the
    person's, the state is the one the store ranks highest, the flag is down, the
    class is the ordinary one this deployment names, and the evidence is the
    hold's own -- the keys the rules cited are exactly what the person is
    contradicting.

    SUPERSEDED AND NOT DELETED (§8.2): the `safety_domain` row is still in the
    table with the new row's fact id against it.
    """
    file_id = _file_id(database, HELD_NAME)
    hold = _current(database, file_id)
    assert hold.protected is True and hold.basis == "safety_domain"

    settled = cli.apply_release(database, [file_id], user_id="t",
                                recorded_at="2026-09-13T00:00:00+00:00")
    assert settled == (file_id,)

    after = _current(database, file_id)
    assert after.basis == USER
    assert after.reliability_state == USER_CONFIRMED
    assert after.protected is False
    assert after.handling_class == cli.ORDINARY_CLASS
    assert after.evidence_refs == hold.evidence_refs
    # `00`'s rule that a protected file is never quietly dropped: the hold is
    # still on the table, retired rather than gone.
    retired = database.execute(
        "SELECT superseded_by FROM classifications "
        "WHERE file_id = ? AND basis = 'safety_domain'", (file_id,)).fetchall()
    assert [row["superseded_by"] for row in retired] != [None]


def test_a_released_file_gets_a_cloud_target_where_it_had_none(database):
    """THE CONSEQUENCE THE PERSON WAS ASKED ABOUT, at the site that asks what a
    file is. `CLOUD_CLEARING_BASES` already carries `"user"`, so nothing in
    `src/privacy` changes: the door reads the row the gesture wrote.

    The routing is a key with NO local model on purpose. A held file's answer
    there is `None` -- no target at all -- so the flip below is a file gaining a
    destination rather than changing one.
    """
    file_id = _file_id(database, HELD_NAME)
    routing = _cloud_only()

    before = cli.target_for(database, routing, G_SITUATION_SENSITIVITY,
                            operation_mode=cli.CLOUD_ENABLED_MODE)
    assert before(file_id) is None, (
        "a held file has no target on a cloud-only routing, which is what "
        "makes the line below a measurement")

    cli.apply_release(database, [file_id], user_id="t",
                      recorded_at="2026-09-13T00:00:00+00:00")

    after = cli.target_for(database, routing, G_SITUATION_SENSITIVITY,
                           operation_mode=cli.CLOUD_ENABLED_MODE)
    chosen = after(file_id)
    assert chosen is not None, (
        "the person said the file is ordinary and the site that asks what a "
        "file is still had nowhere to ask")
    assert chosen[1].locality == CLOUD


def test_the_screen_stops_naming_a_file_the_person_released(database):
    """THE STORE IS READ AT SCREEN TIME and not off a tally the pass kept, so the
    question is not put a second time about a file that has already answered it.

    `_the_files_being_held` is asked with the detector's own pair, exactly as
    `downstream` asks it. The `explain`/`precaution_of` stubs stand in for the
    detector because what is under test here is the STORE read: the detector's
    terms have not changed, and a screen that still named this file would be
    reading the rules rather than the person's answer.
    """
    file_id = _file_id(database, HELD_NAME)
    scan_run_id = _scan_run_id(database)
    names = {file_id: HELD_NAME}

    before = cli._the_files_being_held(
        database, scan_run_id, store=ClassificationStore(database),
        explain=_no_outcome, precaution_of=_no_precaution, names=names)
    assert [row[2] for row in before] == [file_id]

    cli.apply_release(database, [file_id], user_id="t",
                      recorded_at="2026-09-13T00:00:00+00:00")

    after = cli._the_files_being_held(
        database, scan_run_id, store=ClassificationStore(database),
        explain=_no_outcome, precaution_of=_no_precaution, names=names)
    assert after == (), (
        "the person answered and the run asked them again, which is the "
        "screen reading a tally instead of the store")


# --- and it refuses, by name ----------------------------------------------------


def test_a_file_nothing_is_holding_is_refused_rather_than_released(database):
    """The refusal that matters. A `user` row on a file no rule held would be a
    cloud clearance the person was never offered and never meant to give."""
    with pytest.raises(cli.ReleaseRefused):
        cli.apply_release(database, [_file_id(database, FREE_NAME)],
                          user_id="t", recorded_at="2026-09-13T00:00:00+00:00")


def test_an_unrecorded_file_id_is_refused_by_name(database):
    """`apply_file_held`'s rule beside it: a person believes they have told the
    product something, and a silently dropped gesture is worse than a loud one."""
    with pytest.raises(cli.ReleaseRefused):
        cli.apply_release(database, ["no-such-file"], user_id="t",
                          recorded_at="2026-09-13T00:00:00+00:00")


def test_the_next_run_does_not_take_the_release_back(a_run_that_held_a_file,
                                                     tmp_path):
    """THE SENTENCE `--release`'s OWN HELP PRINTS -- "no later run of the rules
    takes it back" -- measured rather than reasoned about, because it is a claim
    made to a person on a screen (`84` §6).

    THE SAME COMMAND THE SCREEN TELLS THEM TO TYPE, over the same folder and the
    same database. The detector's terms have not changed: `passport` is still in
    that filename, so `classifier` and `_reclassify_on_entities` both meet a file
    the rules would hold and a row saying the person has already said otherwise.

    ONE LIVE ROW IS THE HALF THAT MATTERS. `learning_seam.assign` refuses to
    retire a stronger prior, but a second write that did not go through it would
    leave two unsuperseded rows at one `(file_id, content_hash)` and
    `AmbiguousCurrentClassification` would then wedge the store for good --
    `current`, `may_move_automatically` and even the person's own `reclassify` all
    read the current row first, so nothing would be left that could repair it.
    """
    source, _said = a_run_that_held_a_file
    database = tmp_path / "plan.sqlite"
    shutil.copyfile(source, database)
    conn = open_database(database)
    try:
        file_id = _file_id(conn, HELD_NAME)
    finally:
        conn.close()
    # The corpus this database was scanned from is still there: the module-scoped
    # run built it under `tmp_path_factory` and nothing removes it.
    corpus = source.parent / "corpus"

    out = io.StringIO()
    code = cli.main(
        [str(corpus), "--situation", SITUATION, "--label", LABEL, "--user", "t",
         "--database", str(database), "--release", file_id], out=out)
    assert code == 0, out.getvalue()
    assert "being held here" not in out.getvalue(), (
        "the run asked again about a file the person had just answered")

    conn = open_database(database)
    try:
        after = _current(conn, file_id)
        assert after.basis == USER
        assert after.protected is False
        live = conn.execute(
            "SELECT COUNT(*) FROM classifications "
            "WHERE file_id = ? AND superseded_by IS NULL", (file_id,)).fetchone()
        assert live[0] == 1, (
            "two live rows at one file version is the state that wedges the "
            "store; every repair path has to read the current row first")
    finally:
        conn.close()


def test_releasing_twice_is_refused_because_the_second_has_no_hold_to_lift(
        database):
    """The same refusal read from the other side, and the reason the gesture
    checks the STORE rather than a list on a screen: after the first release the
    file is ordinary, and the second `--release` is a gesture with nothing to
    act on."""
    file_id = _file_id(database, HELD_NAME)
    cli.apply_release(database, [file_id], user_id="t",
                      recorded_at="2026-09-13T00:00:00+00:00")
    with pytest.raises(cli.ReleaseRefused):
        cli.apply_release(database, [file_id], user_id="t",
                          recorded_at="2026-09-13T00:00:00+00:00")

# tests/integration/test_the_question_at_the_end_and_the_sort.py
"""The end of a run, the person's two answers, and the sort -- one corpus, one
database, three runs, and NO LOCAL MODEL ANYWHERE.

This is `104` §18.60's build order items 5 and 6 driven end to end: *"the owner
answers the closing question and the branch questions (`--release`,
`--file-held`, `--answer situation:<schema>=...`), then one more run to apply
them"*, and then *"the sort run: grouping, placement, the plan"*. Items 1-4 are
built and merged; nothing below rebuilds them. What had no single pin is the
JOIN -- that the two closing questions a run prints are answerable, that the
answers reach the passes that asked, and that the sort then runs over that state
and moves nothing.

**THE DEPLOYMENT IS THE ONE THE OWNER CHOSE** (14 Sep 01:30, `104` §18.60): *"don't
use the local model unless absolutely necessary; use the cloud"*. A cloud key,
no local model, and `readers.model_routing.deepseek_invoke` replaced by a
recorder -- the documented deployment seam, so the gate, the route, the
transport, the validator and the whole of `cli.run` are the production path. The
gate therefore clears on the rules' word (`GatePass.cleared_by_rules`), the held
files are the person's question, and the judge that names each file's schema is
the CLOUD one.

**THE CORPUS IS ELEVEN FILES A PERSON COULD HAVE.** Six coursework files in the
folder root, three of a student society's records in a subfolder of their own,
and two the rules hold -- one identity, one medical. It is synthetic and it is
authored here rather than fetched: nothing below reads the owner's disk.

**WHY THE SUBFOLDER IS THE ONLY THING THE JUDGE CAN TELL FILES APART BY.** Measured
by the two sibling pins and true here: a site-G dossier for a short text file
releases the folder path, the mime type and the extension, and `filename` is
never released to any model. So the society's records sit in one folder, the
stub reads the path, and every other file is answered `academic`.

**THE THREE SCENES, AND WHAT EACH ONE IS OF `00`.**

1. *The closing question* (`00` amendment 2 of 13 Sep). Run 1 clears nine files
   on the rules' word, asks the cloud judge about eight of them, holds two, and
   ends by NAMING those two with both gestures. Run 2 answers: `--release` on the
   identity file and `--file-held` on the medical one. Measured on run 2: the
   cloud opens to the released file and to it alone -- its wire handle is the one
   subject site G is given -- and the file kept back is asked of nobody.

2. *The branch question* (`00` amendment 6 of 13 Sep, and amendment 2 of 11 Sep).
   The judge names `nonprofit` for the society's three files. The shipped library
   carries two situations under it and no recogniser raised either, so
   `branch_situation.the_one_situation` names neither: the run prints "Which of
   these is nonprofit?" at the END, exits 0, asks those files the SCHEMA's own
   four fields, and files them nowhere. Run 3 answers it. And the typed
   `--situation` overrides: the judge names `academic` for the coursework files,
   which is the schema the person already typed, so no question is asked about
   them and their folders are the ones they typed.

3. *The sort in run 10's shape* (`00` §grouping, §user-selection). Every run here
   carries `--accept-groups` and neither `--apply` nor `--freeze`, so groups,
   memberships, a tree, placement decisions and plan versions land in the
   database and NOTHING moves: `move_plans` and `move_journal` are empty and the
   corpus on disk is byte-for-byte what it was before run 1.

**THE ONE THING THAT DOES NOT WORK, AND IT IS PINNED xfail RATHER THAN FIXED.**
Site C, the placement judge, is the only site whose route is built without the
gate pass. `cli.target_for(conn, routing, C_PLACEMENT, ...)` is called at two
places with no `cloud_cleared`, where sites A, G and H all pass
`lambda file_id: file_id in gate_pass.cleared_files`. `model_route_permitted`
then falls through to `record.basis in CLOUD_CLEARING_BASES`, and a
rules-cleared file's current row reads `detector_no_safety_evidence` or
`local_model_situation` -- neither of which is a member. Measured on this
corpus's own database, `target_for(C_PLACEMENT)` per file, as built and with the
gate's clearance supplied:

    file                                as built    with the gate
    Annual meeting agenda.txt           none        cloud
    Committee minutes June.txt          none        cloud
    Committee minutes March.txt         none        cloud
    ECON 2010 lecture 01.txt            none        none   (unclassified)
    ECON 2010 syllabus.txt              none        cloud
    Medical record summary.txt          none        none   (held, correct)
    PHYS 1401 lecture 03.txt            none        cloud
    PHYS 1401 midterm.txt               none        cloud
    PHYS 1401 problem set 2.txt         none        cloud
    PHYS 1401 syllabus.txt              none        cloud
    Passport renewal notes.txt          cloud       cloud   (the person's row)

So on the deployment the owner chose, the ONLY file the placement judge may be
asked about is the one the person released by hand, and every other file
abstains `no_model_judgement` -- a call that never happened. Threading the gate
into that route sends nine more files' placement dossiers off this device, which
is a change to what leaves the machine and is the owner's to make, not this
pin's. It is pinned `xfail(strict=True)` below and reported.
"""
from __future__ import annotations

import io
import json
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
from facts.domains import DOMAIN_FIELDS  # noqa: E402
from llm_harness.wire_handles import wire_handle  # noqa: E402
from placement.vocabulary import NO_MODEL_JUDGEMENT  # noqa: E402
from privacy.vocabulary import USER, USER_CONFIRMED  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402

# The stub's three answers, imported rather than rewritten, on the rule
# `test_a_fact_call_cache` states for the local half: one stub speaking one
# protocol, so this file and the pins that own those shapes cannot drift into
# describing two different models.
from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _abstentions, _names, _placed, _released, _the_deterministic_winner,
)
from test_local_model_fact_pass import _answer_for  # noqa: E402

#: What the person typed. The run's own situation, and the thing amendment 2 of
#: 11 Sep says overrides the judge.
SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The society's folder. The one released item that differs per file at site G,
#: and therefore the only thing the stub may read to tell these files apart.
CLUB = "Debate Society"

#: The schema the judge names for that folder. Chosen by MEASUREMENT and not by
#: taste: of the twenty-three schemas the shipped library carries, `nonprofit` is
#: the only one with exactly two situations beneath it, which is the state
#: `00` amendment 6 of 13 Sep is about -- more than one, and nothing to tell them
#: apart. It is also the row the owner asked for on 13 Sep ("a club, a society or
#: a student organisation -- add that").
SCHEMA = "nonprofit"
#: The two the question offers, and the one the person picks. Deliberately the
#: SECOND: an answer that agreed with `situations_of(schema)[0]` would prove
#: nothing about the alphabetical pick being gone.
BOTH_SITUATIONS = ("nonprofit", "nonprofit.member-association")
CHOSEN = "nonprofit.member-association"
ANSWER = f"situation:{SCHEMA}={CHOSEN}"

#: The two files the rules hold, and what the person says about each. `passport`
#: and `medical record` are work types of `identity` and `medical` in a NAMING
#: ZONE -- the filename and the first heading -- which is the one place a single
#: term still takes a hold since the corroboration rule of 13 Sep 2026.
RELEASED = "Passport renewal notes.txt"
KEPT = "Medical record summary.txt"

#: The four fields `academic`'s levels ask a coursework file, and the witness that
#: the society's files are not being asked the run's own questions.
COURSEWORK_FIELDS = frozenset({"school", "subject", "term", "work_type"})

ROOT_FILES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n",
    "PHYS 1401 lecture 03.txt":
        "Lecture 03 - Rotational Dynamics\nPHYS 1401\nSpring 2026. "
        "Instructor: Dr. Lee.\n",
    "PHYS 1401 problem set 2.txt":
        "Problem Set 2\nPHYS 1401 Spring 2026. Instructor: Dr. Lee.\n"
        "Hand in on Thursday.\n",
    "PHYS 1401 midterm.txt":
        "Midterm exam paper\nPHYS 1401 Spring 2026. Instructor: Dr. Lee.\n"
        "Answer four of six.\n",
    "ECON 2010 syllabus.txt":
        "ECON 2010 Syllabus\n\nFall 2025. Instructor: Dr. Ruiz. Credits: 4.\n",
    "ECON 2010 lecture 01.txt":
        "Lecture 01 - Aggregate demand\nECON 2010\nFall 2025. "
        "Instructor: Dr. Ruiz.\n",
    RELEASED:
        "Passport\nNotes on renewing the travel document before the trip.\n",
    KEPT:
        "Medical record\nNotes kept after the appointment last month.\n",
}

#: Three of the society's own records. All three carry a document kind the term
#: detector recognises (`minutes`, `agenda`), which is what gives them a
#: classification and therefore a cloud target at the site that asks what they
#: are -- a file nothing has classified is never put to a model at all.
CLUB_FILES = {
    "Committee minutes March.txt":
        "Minutes of the March committee meeting.\nThe committee agreed the "
        "programme for the coming term.\n",
    "Committee minutes June.txt":
        "Minutes of the June committee meeting.\nThe committee reviewed the "
        "year and thanked the outgoing chair.\n",
    "Annual meeting agenda.txt":
        "Agenda for the annual general meeting\n\n1. Chair's report. "
        "2. Treasurer's report. 3. Elections.\n",
}

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}


# --- the cloud, stubbed at the deployment seam ----------------------------------


class _Cloud:
    """Every call this run put on the wire, and the dossier each one carried.

    `test_a_fact_call_cache._Socket` in shape and for its reason -- the payload's
    JSON half is what the model would read -- with the site answers of
    `test_each_file_is_filed_under_its_own_situation` behind it. There is no site
    H answer because a deployment with no local model builds NO gate dossier: the
    rules clear, and that is the arm
    `test_the_rules_clear_without_a_local_model` pins.
    """

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def forget(self) -> None:
        self.payloads = []

    @staticmethod
    def _body(payload: bytes) -> dict:
        return json.loads(
            payload.decode("utf-8").split("The dossier follows.", 1)[1])

    def subjects_at(self, call_site: str) -> list[str]:
        return [self._body(p)["subject_ref"] for p in self.payloads
                if self._body(p)["call_site"] == call_site]

    def sites(self) -> Counter:
        return Counter(self._body(p)["call_site"] for p in self.payloads)

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            body = self._body(payload)
            site = body["call_site"]
            if site == cli.G_SITUATION_SENSITIVITY:
                where = " ".join(item["value"] for item in _released(body))
                return _names(SCHEMA if CLUB in where else "academic",
                              body).encode("utf-8")
            if site == cli.C_PLACEMENT:
                return _the_deterministic_winner(body).encode("utf-8")
            return _answer_for(payload.decode("utf-8")).encode("utf-8")
        return invoke


# --- one corpus, three runs -----------------------------------------------------


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in ROOT_FILES.items():
        (corpus / name).write_text(body)
    (corpus / CLUB).mkdir()
    for name, body in CLUB_FILES.items():
        (corpus / CLUB / name).write_text(body)
    return corpus


def _on_disk(corpus: Path) -> dict[str, tuple[int, int]]:
    """Every path under the folder, with its size and its modification time.

    The whole of "nothing moved", taken before the first run and again after the
    last: a plan that renamed, moved or rewrote one byte of somebody's folder
    without `--freeze` and `--apply` would show here.
    """
    return {str(path.relative_to(corpus)):
            (path.stat().st_size, path.stat().st_mtime_ns)
            for path in sorted(corpus.rglob("*"))}


def _file_ids(database: Path) -> dict[str, str]:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return {row["filename"]: row["file_id"]
                for row in conn.execute("SELECT file_id, filename FROM files")}
    finally:
        conn.close()


def _rows(database: Path, table: str) -> int:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def _fields_asked(database: Path) -> dict[str, set[str]]:
    """filename -> every field any A_fact call MADE about it offered.

    `test_r37_per_branch_situation._call_log` read off the product's own record,
    with the subject resolved through THIS DATABASE'S WIRE HANDLE KEY. That is
    the difference a cloud run makes: `llm_dossier.subject_ref` is
    `HMAC-SHA256(key, file_id)` once a call has gone out keyed, so a reader that
    looks the raw id up in `files` finds nothing and reports an empty log.
    """
    key = cli.wire_handle_key_for(database)
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        named = {row["file_id"]: row["filename"]
                 for row in conn.execute("SELECT file_id, filename FROM files")}
        handles = {wire_handle(file_id, key=key): name
                   for file_id, name in named.items()}
        log: dict[str, set[str]] = {}
        for row in conn.execute(
                "SELECT d.subject_ref, d.payload FROM llm_dossier d "
                "JOIN llm_response r ON r.dossier_id = d.dossier_id "
                "WHERE d.call_site = ? ORDER BY r.rowid", (cli.A_FACT,)):
            subject = row["subject_ref"]
            name = handles.get(subject, named.get(subject, subject))
            log.setdefault(name, set()).update(
                json.loads(row["payload"]).get("allowed_vocabulary", ()))
        return log
    finally:
        conn.close()


@pytest.fixture(scope="module")
def three_runs(tmp_path_factory):
    """The whole story, once: the run that asks, the run that answers the holds,
    and the run that answers the branch and sorts.

    MODULE SCOPED AND CHAINED, for `test_a_silent_file_is_asked_and_filed_under_
    one_situation`'s reason: `apply_answers` refuses an answer to a question no
    run has asked, and `apply_release` refuses a file nothing is holding, so each
    gesture below has to follow the run that offered it. One `cli.main` is the
    most expensive thing in this file and every test asks about the same eleven
    files.
    """
    root = tmp_path_factory.mktemp("question_and_sort")
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    before = _on_disk(corpus)
    cloud = _Cloud()
    said: list[str] = []
    calls: list[Counter] = []
    subjects: list[list[str]] = []

    with pytest.MonkeyPatch.context() as patch:
        # NO KEY AND NO LOCAL MODEL FROM THE MACHINE THIS RUNS ON. A developer
        # with ollama resident would otherwise get a different deployment -- a
        # gate that runs, a local target at every site -- and the counts below
        # would be about their machine rather than about the product.
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", root / "absent.env")
        for name, value in ENV.items():
            patch.setenv(name, value)
        patch.setattr(model_routing, "deepseek_invoke", cloud.factory)

        def once(*extra: str) -> None:
            cloud.forget()
            out = io.StringIO()
            code = cli.main(
                [str(corpus), "--situation", SITUATION, "--label", LABEL,
                 "--user", "t", "--database", str(database), "--enable-cloud",
                 "--accept-groups", *extra], out=out)
            assert code == 0, out.getvalue()
            said.append(out.getvalue())
            calls.append(cloud.sites())
            subjects.append(cloud.subjects_at(cli.G_SITUATION_SENSITIVITY))

        once()
        ids = _file_ids(database)
        once("--release", ids[RELEASED], "--file-held", ids[KEPT])
        once("--answer", ANSWER)

    return {"corpus": corpus, "database": database, "ids": ids,
            "said": said, "calls": calls, "asked_off_device": subjects,
            "before": before, "after": _on_disk(corpus)}


def _handle(state, filename: str) -> str:
    return wire_handle(state["ids"][filename],
                       key=cli.wire_handle_key_for(state["database"]))


# --- scene 1: the closing question, and the person's two answers ----------------


def test_the_rules_clear_the_corpus_and_the_two_held_files_are_the_question(
        three_runs):
    """`00` amendment 2 of 13 Sep, on the screen of a run with no local model.

    The gate has no model to ask, so every file the rules did not hold is
    cleared on the rules' own word and its situation may be asked off the device
    -- and the two the rules DO hold are put to the person, by name, with both
    gestures typed out with the real id, because nobody can type `FILE_ID`.

    THE WHY IS THE SAFETY DOMAIN AND NOT A BARE "PROTECTED": one phrase per file,
    and the two here are different phrases because the two files are different
    kinds of record.
    """
    state = three_runs
    said = state["said"][0]
    flat = " ".join(said.split())
    assert "9 cleared on the rules' word alone" in flat, said
    assert "2 files are being held here" in flat, said
    for name, why in ((RELEASED, "identity material"), (KEPT, "medical material")):
        file_id = state["ids"][name]
        assert name in said, said
        assert f"--file-held {file_id}" in said, "the keep-it-here gesture"
        assert f"--release {file_id}" in said, "the it-is-ordinary gesture"
        assert why in flat, why
    # And no other file is offered the gesture: the block is about a hold, not
    # about the corpus.
    for name in ("PHYS 1401 syllabus.txt", "Committee minutes March.txt"):
        assert f"--release {state['ids'][name]}" not in said, name


def test_neither_held_file_is_asked_of_the_cloud_and_the_cleared_ones_are(
        three_runs):
    """`00` amendment 5 of 11 Sep: a protected file never reaches a cloud model.

    READ THROUGH THE WIRE HANDLE, which is the whole reason this assertion is
    worth making twice. `llm_dossier.subject_ref` on a cloud call is
    `HMAC-SHA256(key, file_id)`, so `held_id not in subjects_at(G)` is true of
    every run ever made and measures nothing. The handles are computed here from
    this database's own key, so a held file appearing at that site would turn
    this red.
    """
    state = three_runs
    asked = set(state["asked_off_device"][0])
    assert _handle(state, RELEASED) not in asked, "a held file reached the cloud"
    assert _handle(state, KEPT) not in asked, "a held file reached the cloud"
    for name in CLUB_FILES:
        assert _handle(state, name) in asked, f"{name} was never asked"
    assert len(asked) == 8, sorted(state["asked_off_device"][0])


def test_release_opens_the_cloud_to_that_file_and_to_no_other_held_one(three_runs):
    """THE ANSWER'S CONSEQUENCE, measured at the site that asks what a file is.

    `--release` writes the person's own classification row and `"user"` is
    already a `CLOUD_CLEARING_BASES` member, so the door opens by itself and
    `src/privacy` is untouched. The gesture is applied BEFORE the run's own
    passes (`cli.main`), so it is this invocation that asks -- a person who has
    just said their file is ordinary sees it on this run rather than the next.

    THE FILE WAS NOT ASKED ABOUT BEFORE AND IS NOW, which is the whole of what
    the person's word changed, and the other held file is asked about on neither
    run. The COUNT on run 2 is not asserted and the reason is worth writing down:
    the policy is one of `store.CALL_IDENTITY_DIMENSIONS`, and `--file-held`
    changes the policy (it grants one move permission), so run 2's identities
    move once and the whole roster is re-asked instead of reused. Measured: 1
    call at this site before the grant was carried, 9 after. That is the answer
    cache doing what it is for -- the policy really did change -- and it happens
    once, not per run: run 3 makes no call at this site at all.
    """
    state = three_runs
    asked = state["asked_off_device"][1]
    assert _handle(state, RELEASED) in asked, (
        "the person said the file is ordinary and the site that asks what a "
        "file is still had nowhere to ask")
    assert _handle(state, RELEASED) not in state["asked_off_device"][0], (
        "the file was already being asked about, so this measures nothing")
    assert _handle(state, KEPT) not in asked
    assert not state["asked_off_device"][2], state["asked_off_device"][2]


def test_the_released_file_carries_the_persons_own_row_and_is_no_longer_held(
        three_runs):
    """The row `--release` wrote, read back off the store after all three runs.

    Every field is a separate claim: the basis is the person's, the state is the
    one `classification_store.strongest` ranks above every system state, and the
    hold is down -- so no later run of the rules takes it back.
    """
    state = three_runs
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        from privacy.classification_store import ClassificationStore
        (row,) = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (state["ids"][RELEASED],)).fetchall()
        current = ClassificationStore(conn).current(
            state["ids"][RELEASED], row["content_hash"])
    finally:
        conn.close()
    assert current.basis == USER
    assert current.reliability_state == USER_CONFIRMED
    assert current.protected is False


def test_the_file_kept_back_stays_held_and_stays_unasked(three_runs):
    """`--file-held`: the other answer to the same question.

    It writes ONE move permission and deliberately no classification row -- a
    person filing their own medical record has said where it goes, not what a
    model may see of it -- so the file is still protected, still held, and still
    put to no model on this or any later run.
    """
    state = three_runs
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        assert state["ids"][KEPT] in cli._protected_file_ids(conn)
    finally:
        conn.close()
    for run_index in (1, 2):
        assert _handle(state, KEPT) not in state["asked_off_device"][run_index]


def test_the_question_is_not_put_a_second_time_about_a_file_already_answered(
        three_runs):
    """ONE QUESTION, and both gestures are answers to it (`00` amendment 2 of
    13 Sep: the held files are put to the person as ONE question at the end of
    the run, with two gestures).

    `test_p7_file_released.test_the_screen_stops_naming_a_file_the_person_
    released` pins this half for `--release`, which gets it for free: the
    person's row supersedes the hold, so the store read at screen time no longer
    finds one. `--file-held` writes no classification row BY DESIGN, so the
    screen used to ask again -- and the header it asked under says "nobody has
    been asked", which had stopped being true. `cli.main`'s own comment beside
    the gesture says what it is for: "a person who has just filed a protected
    file themselves should not have to run the command again to see that it
    took".

    SABOTAGE: drop `filed_by_hand` from the `_the_files_being_held` call in
    `downstream` and run 3's report names the medical file with both gestures
    under a sentence saying nobody has been asked about it.
    """
    state = three_runs
    third = state["said"][2]
    assert "being held here" not in third, (
        "the run asked again about files the person had already answered")
    assert f"--file-held {state['ids'][KEPT]}" not in third, third
    assert f"--release {state['ids'][KEPT]}" not in third, third


# --- scene 2: the branch question, and the person's answer ----------------------


def test_the_judge_names_a_schema_with_two_situations_and_the_run_asks_which(
        three_runs):
    """`00` amendment 6 of 13 Sep: *"a schema the judge names resolves to a
    situation only through the recognisers' one raised situation or the person's
    answer, never the alphabetically first"*.

    The shipped library carries `nonprofit` and `nonprofit.member-association`
    under `nonprofit` and no recogniser raised either for these files, so
    `branch_situation.the_one_situation` names neither and the person is asked.
    THE QUESTION IS PRINTED AT THE END AND THE RUN RETURNS 0 (amendment 2 of
    11 Sep: a situation is not demanded of the person before a file is opened) --
    the `assert code == 0` in the fixture is that half, made here rather than
    left implicit.

    BOTH OPTIONS ARE OFFERED IN THE LIBRARY'S OWN WORDS and each is typable.
    """
    said = three_runs["said"][0]
    assert f"Which of these is {SCHEMA}?" in said, said
    for situation in BOTH_SITUATIONS:
        assert f"--answer situation:{SCHEMA}={situation}" in said, said
    assert f"3 files sit under {SCHEMA}" in " ".join(said.split()), said


def test_those_files_are_asked_the_schemas_own_fields_and_not_the_runs(three_runs):
    """The other half of amendment 6: *"meanwhile the file is asked its schema's
    fields and is not placed"*.

    An unresolved SITUATION withholds the folder levels and the template. It does
    not withhold the QUESTION: the schema is known, so the file is asked the
    schema's own fields with no levels shown. Withholding both cost a whole facts
    column the first time this was tried.

    AND NOT THE RUN'S OWN. `academic`'s four level fields are what
    `--situation academic.coursework` asks a coursework file, and not one of them
    is offered to a file of the society's.
    """
    asked = _fields_asked(three_runs["database"])
    for name in CLUB_FILES:
        offered = asked.get(name, set())
        assert offered, (name, sorted(asked))
        assert offered >= set(DOMAIN_FIELDS[SCHEMA]), (name, sorted(offered))
        assert not offered & COURSEWORK_FIELDS, (name, sorted(offered))
    # The control: a file under the situation the person typed IS asked those
    # four, so the line above is measuring the schema and not an empty allowlist.
    assert asked["PHYS 1401 syllabus.txt"] >= COURSEWORK_FIELDS, asked


def test_and_they_are_filed_nowhere_while_the_situation_is_open(three_runs):
    """A folder needs a situation and nobody has named one, so P11 abstains.

    The reason word is the one that says a call happened and left this file
    unjudged, and it is the same word for all three -- which is what makes it a
    property of the open situation rather than of one file's evidence.
    """
    state = three_runs
    run = (state["corpus"], state["database"], state["said"][0])
    placed, abstained = _placed(run), _abstentions(run)
    for name in CLUB_FILES:
        where = f"{CLUB}/{name}"
        assert where not in placed, placed.get(where)
        assert abstained[where] == NO_MODEL_JUDGEMENT, abstained[where]


def test_the_answer_is_recorded_at_the_branchs_own_scope_and_the_question_stops(
        three_runs):
    """`00` amendment 6: *"every applied answer is a learning record at the
    question's scope"*, and the scope of this question is the branch the judge
    opened.

    `_the_situation_the_person_chose` reads `selected_situation` at
    `branch:<schema>`, ahead of both library arms, so the answer is what resolves
    the situation for every file that branch was opened for -- and the run stops
    asking, which is the observable half of the same fact.
    """
    state = three_runs
    assert f"Which of these is {SCHEMA}?" in state["said"][1], (
        "the second run should still be asking -- nothing had answered yet")
    assert f"Which of these is {SCHEMA}?" not in state["said"][2], state["said"][2]
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        (row,) = conn.execute(
            "SELECT option_id, state, scope, user_id FROM structural_answers "
            "WHERE question_id = ?", (f"situation:{SCHEMA}",)).fetchall()
    finally:
        conn.close()
    assert row["option_id"] == CHOSEN
    assert row["state"] == "confirmed"
    assert row["scope"] == f"branch:{SCHEMA}"
    assert row["user_id"] == "t"


def test_the_answer_reaches_the_files_the_branch_was_opened_for(three_runs):
    """AND IT REACHES THE FILES, which the answer row on its own does not say.

    `00` amendment 6: a schema resolves to a situation through the person's
    answer, and `_the_situation_the_person_chose` reads it at the branch's own
    scope for every file the judge named that schema for. The observable is the
    review set those three files are in. Before the answer they are a set of
    their own whose sentence names the question and prints both of its answers
    against these files -- "Saying what these are is 'Which of these is
    nonprofit?' below, and each of these answers reaches these files". After it
    they are in the general set for a file the model gave no answer about, and
    the pointer is gone: the question that was theirs has one.

    THE SET IS STILL THERE, which is the honest half. The answer settles what
    kind of material these are; it does not file them, and the reason it does
    not is the site-C route pinned `xfail` above.
    """
    state = three_runs
    first, third = state["said"][0], state["said"][2]
    pointer = f"Saying what these are is \"Which of these is {SCHEMA}?\""
    assert pointer in " ".join(first.split()), first
    assert pointer not in " ".join(third.split()), third
    for name in CLUB_FILES:
        assert f"{CLUB}/{name}" in third, name


def test_a_typed_situation_overrides_the_judges_name_for_the_same_schema(
        three_runs):
    """`00` amendment 2 of 11 Sep: *"a situation the person types overrides it"*.

    The stub answers `academic` for every file outside the society's folder --
    the same SCHEMA the person's own `--situation academic.coursework` is under.
    `_the_schema_named_for_this_file` drops a name equal to the run's own schema,
    so those files are not sent back to the person as a question with eleven
    `academic.*` situations to choose between: they keep the situation that was
    typed, and their folders are built from its levels.

    THE PROOF IS TWO-SIDED. No question is asked about `academic`, and the tree
    the run proposes is the typed situation's own -- school, term, subject, kind
    of work -- with the person's label at its root.
    """
    said = three_runs["said"][0]
    assert "Which of these is academic?" not in said, said
    flat = " ".join(said.split())
    for folder in (f"{LABEL}/Spring2026/PHYS1401", f"{LABEL}/Fall2025/ECON2010"):
        crumbs = folder.split("/")
        assert all(crumb in said for crumb in crumbs), (folder, said)
    assert "Kind of work -- academic:artifact_kind:work_type" in flat, said


@pytest.mark.xfail(strict=True, reason=(
    "SITE C'S ROUTE NEVER ASKS THE GATE. `cli.target_for(conn, routing, "
    "C_PLACEMENT, ...)` is built with no `cloud_cleared`, where sites A, G and H "
    "all pass `lambda file_id: file_id in gate_pass.cleared_files`, so "
    "`model_route_permitted` falls through to the current row's basis -- "
    "`local_model_situation` here, which is not a `CLOUD_CLEARING_BASES` member "
    "since 13 Sep. Measured on this database: nine of eleven files have no "
    "destination at site C as built and a cloud one with the gate supplied. "
    "Threading it sends nine more placement dossiers off the device, which is "
    "the owner's call and not this pin's."))
def test_the_answered_files_are_placed_once_the_person_has_said_which(three_runs):
    """The way out of the open situation, and what item 5 of the build order is
    for: the person answers, and the next run files what the answer unlocked."""
    state = three_runs
    run = (state["corpus"], state["database"], state["said"][2])
    placed = _placed(run)
    for name in CLUB_FILES:
        assert f"{CLUB}/{name}" in placed, sorted(placed)


# --- scene 3: the sort, in run 10's shape ---------------------------------------


def test_the_sort_writes_groups_a_tree_and_a_plan(three_runs):
    """`--accept-groups` with neither `--apply` nor `--freeze`, which is
    `run10.sh`'s own shape: P9 groups, P10 designs the tree, P11 decides, and all
    of it lands in the database as a PROPOSAL.

    Counted rather than described, because the point of this line is that the
    sort stages ran at all on a deployment with no local model in it.
    """
    database = three_runs["database"]
    for table in ("groups", "memberships", "placement_decisions",
                  "plan_versions", "tree_nodes"):
        assert _rows(database, table) > 0, table
    # One decision per file per run, and every file is on exactly one of them.
    assert _rows(database, "placement_decisions") == 11 * 3


def test_nothing_moved_and_no_move_was_even_planned(three_runs):
    """`00`: freezing is the person's approval and moving is a separate third
    invocation. Neither was given here, so the plan is a proposal and the
    person's folder is untouched -- byte for byte, mtime for mtime, over three
    runs that read every file in it.
    """
    state = three_runs
    assert _rows(state["database"], "move_plans") == 0
    assert _rows(state["database"], "move_journal") == 0
    assert state["after"] == state["before"], "the run changed somebody's folder"
    assert "Nothing was moved." in state["said"][2], state["said"][2]


def test_the_held_file_is_not_placed_and_the_released_one_is(three_runs):
    """The two answers, read at the end of the sort.

    The file the person kept has no supported destination -- it was shown to no
    model, so nothing proposed a folder for it, and it stays exactly where it is
    on its own path. The file they released is ordinary from that moment and the
    sort files it like any other.
    """
    state = three_runs
    run = (state["corpus"], state["database"], state["said"][2])
    placed, abstained = _placed(run), _abstentions(run)
    assert KEPT not in placed, placed.get(KEPT)
    assert abstained[KEPT] == "no_supported_destination", abstained[KEPT]
    assert (state["corpus"] / KEPT).is_file(), "the held file left its own path"
    assert placed[RELEASED] == LABEL, placed.get(RELEASED)


def test_the_persons_own_folder_is_in_the_plan_as_theirs(three_runs):
    """`00` §user-selection: existing folders are shown as the person's own and
    nothing of theirs is moved, renamed or merged without being asked.

    The society's folder is in the proposal under its own name, marked as theirs
    -- not absorbed into the branch the judge named for the files inside it.
    """
    said = three_runs["said"][2]
    assert f"{CLUB}   [yours already]" in said, said

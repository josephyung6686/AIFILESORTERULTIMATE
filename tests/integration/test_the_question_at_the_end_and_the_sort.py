# tests/integration/test_the_question_at_the_end_and_the_sort.py
"""The end of a run, the person's answers, and the sort -- one corpus, one
database, four runs, and NO LOCAL MODEL ANYWHERE.

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

1. *The closing question* (`00` amendment 2 of 13 Sep, asked inside the owner's
   ruling of 2 Sep, `planning/93`). Run 1 clears nine files on the rules' word,
   asks the cloud judge about eight of them, holds two, and ends by asking about
   the two WITHOUT naming them: the count, what each gesture means, and
   `--show-protected`. Run 2 is that flag, and it is the screen the person
   answers from -- each file by name, why in one phrase, both commands typed out
   with the real id. Run 3 answers, three ways at once: `--release` on the
   identity file, `--file-held` on the medical one, and `--file-held` on a file
   the RULES CLEARED and the person knows is theirs to keep. Measured: the cloud
   opens to the released file, stays shut to the file kept back, and shuts to the
   cleared one from that run on.

2. *The branch question* (`00` amendment 6 of 13 Sep, and amendment 2 of 11 Sep).
   The judge names `nonprofit` for the society's three files. The shipped library
   carries two situations under it and no recogniser raised either, so
   `branch_situation.the_one_situation` names neither: run 1 prints "Which of
   these is nonprofit?" at the END, exits 0, asks those files the SCHEMA's own
   four fields, and files them nowhere. Run 4 answers it, and on that run the
   placement judge is asked about each of the three and each is filed. And the
   typed `--situation` overrides: the judge names `academic` for the coursework
   files, which is the schema the person already typed, so no question is asked
   about them and their folders are the ones they typed.

3. *The sort in run 10's shape* (`00` §grouping, §user-selection). Every run here
   carries `--accept-groups` and neither `--apply` nor `--freeze`, so groups,
   memberships, a tree, placement decisions and plan versions land in the
   database and NOTHING moves: `move_plans` and `move_journal` are empty and the
   corpus on disk is byte-for-byte what it was before run 1.

**THE TWO DEFECTS THIS CORPUS FOUND, BOTH NOW FIXED IN `src/cli.py`.**

*Site C's route never asked the gate.* `cli.target_for(conn, routing,
C_PLACEMENT, ...)` was built at two places with no `cloud_cleared`, where sites
A, G and H all pass `lambda file_id: file_id in gate_pass.cleared_files`.
`model_route_permitted` then falls through to `record.basis in
CLOUD_CLEARING_BASES`, and a rules-cleared file's current row reads
`local_model_situation` -- the situation judge's own answer, written over the
gate's clearance row and not a member of that tuple since 13 Sep. Measured on
this corpus, `target_for(C_PLACEMENT)` per file, before the fix and after:

    file                                before      after
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

Before it, the only file the placement judge could be asked about on this
deployment was the one the person had released by hand: every other file
abstained `no_model_judgement`, a call that never happened, on a run with a key
and the person's consent. `00`'s "every placement goes through the model" cannot
hold through a door that never asks the thing that opened it. The two files that
answer `none` after the fix are right to: one is held, and one is unclassified,
which amendment 7(c) keeps on this machine.

*The person's `--file-held` grant did not survive its own run, and was read at a
plan version it was never written to.* `apply_file_held` writes one
`automatic_move_permissions` grant at `cli.PLAN_VERSION`; the run's own two
policy writers reset that field to `{}` fifteen milliseconds later, and P11 asks
`automatic_move_permitted_for` at the run's own `version_*`.
`_permissions_in_force` is now the one reader all three writers share, and a
plan version carrying no grants of its own inherits the standing ones.
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
from placement.store import decisions_for_plan  # noqa: E402
from placement.vocabulary import PLACE  # noqa: E402
from tree_design.store import nodes_for_version  # noqa: E402
from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _names, _released, _the_deterministic_winner,
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
#: A file the rules CLEARED and the person keeps anyway -- the arm of 14 Sep:
#: on a deployment with no local model the rules are the only gate before the
#: cloud, they miss protected records, and this is the sentence the person has
#: for one they know is theirs to keep.
CLEARED_KEPT = "ECON 2010 syllabus.txt"

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


# --- one corpus, four runs ------------------------------------------------------


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


def _plan_version_in(report: str) -> str:
    """The proposal this run saved, off the line the run prints for the person.

    READ PER RUN AND NOT "THE LAST ONE IN THE TABLE", which is the difference
    between asking what run 1 decided and asking what run 4 did. Four runs write
    four plans into one database, and a reader that takes the newest answers
    every question with run 4's answer -- so "the file is not placed while the
    situation is open" would have been measured against a run in which the
    person had already closed it.
    """
    for line in report.splitlines():
        if line.startswith("Plan version: "):
            return line.split()[2]
    raise AssertionError("the run printed no plan version")


def _decisions_at(database: Path, corpus: Path, plan_version: str):
    """`(placed, abstained)` for ONE run's proposal, by corpus-relative name."""
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        nodes = {node.node_id: node
                 for node in nodes_for_version(conn, plan_version)}
        named = {row["file_id"]: row["current_path"]
                 for row in conn.execute(
                     "SELECT file_id, current_path FROM files")}
        decisions = tuple(decisions_for_plan(conn, plan_version=plan_version))
    finally:
        conn.close()

    def chain(node_id: str) -> str:
        parts: list[str] = []
        while node_id in nodes:
            parts.append(nodes[node_id].display_label)
            node_id = nodes[node_id].parent_node_id
        return "/".join(reversed(parts))

    def where(decision) -> str:
        return str(Path(named[decision.subject.file_id]).relative_to(corpus))

    placed = {where(d): chain(d.destination.node_id) for d in decisions
              if d.subject.kind == "file" and d.outcome == PLACE}
    abstained = {where(d): d.abstention_reason for d in decisions
                 if d.subject.kind == "file" and d.outcome != PLACE}
    return placed, abstained


def _run_decisions(state, index: int):
    return _decisions_at(state["database"], state["corpus"],
                         state["plans"][index])


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
    """The whole story, once, in four runs.

    1. the run that ASKS: the closing question and the branch question;
    2. the same run with `--show-protected`, which is the only screen that names
       a held file (the owner's ruling of 2 Sep, `planning/93`);
    3. the person's three answers to the closing question: `--release` on the
       identity file, `--file-held` on the medical one, and `--file-held` on a
       file the rules CLEARED and they know is theirs to keep;
    4. the person's answer to the branch question, which is also the sort run.

    MODULE SCOPED AND CHAINED, for `test_a_silent_file_is_asked_and_filed_under_
    one_situation`'s reason: `apply_answers` refuses an answer to a question no
    run has asked and `apply_release` refuses a file nothing is holding, so each
    gesture follows the run that offered it.
    """
    root = tmp_path_factory.mktemp("question_and_sort")
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    before = _on_disk(corpus)
    cloud = _Cloud()
    said: list[str] = []
    calls: list[Counter] = []
    asked: list[list[str]] = []
    placed_by: list[list[str]] = []

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
            asked.append(cloud.subjects_at(cli.G_SITUATION_SENSITIVITY))
            placed_by.append(cloud.subjects_at(cli.C_PLACEMENT))

        once()
        ids = _file_ids(database)
        once("--show-protected")
        once("--release", ids[RELEASED],
             "--file-held", ids[KEPT], "--file-held", ids[CLEARED_KEPT])
        once("--answer", ANSWER)

    return {"corpus": corpus, "database": database, "ids": ids,
            "said": said, "calls": calls, "asked_off_device": asked,
            "judged_for_placement": placed_by,
            "plans": [_plan_version_in(report) for report in said],
            "before": before, "after": _on_disk(corpus)}


def _handle(state, filename: str) -> str:
    """What the model was shown instead of this file's id."""
    return wire_handle(state["ids"][filename],
                       key=cli.wire_handle_key_for(state["database"]))


def _placement_handle(state, filename: str) -> str:
    """What the PLACEMENT judge was shown instead of this file version's address.

    Site C's subject is not the file id. `placement.store` addresses a decision
    as `file:<file_id>:<content_hash>`, because §8.8 versions the plan and §8.2
    versions the file, and it is that whole string the wire handle keys. A test
    that looked for `wire_handle(file_id)` among C's subjects would find nothing
    and would say the judge had never been asked.
    """
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        (row,) = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (state["ids"][filename],)).fetchall()
    finally:
        conn.close()
    return wire_handle(f"file:{state['ids'][filename]}:{row['content_hash']}",
                       key=cli.wire_handle_key_for(state["database"]))


def _classification(state, filename: str):
    """The live classification row for one file, off the store."""
    from privacy.classification_store import ClassificationStore
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        (row,) = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (state["ids"][filename],)).fetchall()
        return ClassificationStore(conn).current(
            state["ids"][filename], row["content_hash"])
    finally:
        conn.close()


# --- scene 1: the closing question, and the person's three answers --------------


def test_the_plain_report_asks_without_naming_anybodys_protected_files(
        three_runs):
    """`00` amendment 2 of 13 Sep asked INSIDE the owner's ruling of 2 Sep
    (`planning/93`): the question is put on every report, and the FILENAMES are
    printed only when the person asks for them.

    So the plain report says how many are held, what each gesture means, and the
    one command that shows each file with its own two commands typed out. No
    name, and no id -- a person reading a run's report over somebody's shoulder
    does not learn which of their files are medical records.
    """
    state = three_runs
    flat = " ".join(state["said"][0].split())
    assert "9 cleared on the rules' word alone" in flat, state["said"][0]
    assert "2 files are being held here" in flat, state["said"][0]
    assert "--file-held FILE_ID keeps a file here" in flat, state["said"][0]
    assert "--release FILE_ID says it is ordinary" in flat, state["said"][0]
    assert "--show-protected" in state["said"][0]
    for name in (RELEASED, KEPT):
        assert name not in state["said"][0], (
            "the plain report named somebody's protected file")
        assert state["ids"][name] not in state["said"][0], name


def test_and_under_the_flag_each_held_file_is_named_with_both_gestures(
        three_runs):
    """The screen the person answers from, and the reason it is a second command.

    Each file by its own name, one phrase saying WHY -- the safety domain the
    detector named, not a bare "protected" -- and both gestures typed out with
    the real id, because nobody can type `FILE_ID`.
    """
    state = three_runs
    shown = state["said"][1]
    flat = " ".join(shown.split())
    for name, why in ((RELEASED, "identity material"), (KEPT, "medical material")):
        file_id = state["ids"][name]
        assert name in shown, name
        assert f"--file-held {file_id}" in shown, "the keep-it-here gesture"
        assert f"--release {file_id}" in shown, "the it-is-ordinary gesture"
        assert why in flat, why
    # The gesture is offered for a held file and for no other.
    for name in ("PHYS 1401 syllabus.txt", "Committee minutes March.txt"):
        assert f"--release {state['ids'][name]}" not in shown, name


def test_neither_held_file_is_asked_of_the_cloud_and_the_cleared_ones_are(
        three_runs):
    """`00` amendment 5 of 11 Sep: a protected file never reaches a cloud model.

    READ THROUGH THE WIRE HANDLE, which is the whole reason this assertion is
    worth making. `llm_dossier.subject_ref` on a cloud call is
    `HMAC-SHA256(key, file_id)`, so `held_id not in subjects_at(G)` is true of
    every run ever made and measures nothing. The handles are computed from this
    database's own key, so a held file appearing at that site turns this red.
    """
    state = three_runs
    asked = set(state["asked_off_device"][0])
    assert _handle(state, RELEASED) not in asked, "a held file reached the cloud"
    assert _handle(state, KEPT) not in asked, "a held file reached the cloud"
    for name in CLUB_FILES:
        assert _handle(state, name) in asked, f"{name} was never asked"
    assert len(asked) == 8, sorted(state["asked_off_device"][0])


def test_release_opens_the_cloud_to_that_file_and_to_no_other_held_one(
        three_runs):
    """THE ANSWER'S CONSEQUENCE, measured at the site that asks what a file is.

    `--release` writes the person's own classification row and `"user"` is
    already a `CLOUD_CLEARING_BASES` member, so the door opens by itself and
    `src/privacy` is untouched. The gesture is applied BEFORE the run's own
    passes, so it is this invocation that asks -- a person who has just said
    their file is ordinary sees it on this run rather than the next.

    THE FILE WAS NOT ASKED ABOUT BEFORE AND IS NOW. The COUNT is not asserted and
    the reason is worth writing down: the policy is one of
    `store.CALL_IDENTITY_DIMENSIONS` and `--file-held` changes the policy, so the
    identities move once on the run that carries the grant and the roster is
    re-asked instead of reused. That happens once, not per run.
    """
    state = three_runs
    answered = state["asked_off_device"][2]
    assert _handle(state, RELEASED) in answered, (
        "the person said the file is ordinary and the site that asks what a "
        "file is still had nowhere to ask")
    assert _handle(state, RELEASED) not in state["asked_off_device"][0], (
        "the file was already being asked about, so this measures nothing")
    assert _handle(state, KEPT) not in answered


def test_the_released_file_carries_the_persons_own_row_and_is_no_longer_held(
        three_runs):
    """The row `--release` wrote, read back off the store after every run.

    Every field is a separate claim: the basis is the person's, the state is the
    one `classification_store.strongest` ranks above every system state, and the
    hold is down -- so no later run of the rules takes it back.
    """
    state = three_runs
    current = _classification(state, RELEASED)
    assert current.basis == USER
    assert current.reliability_state == USER_CONFIRMED
    assert current.protected is False


def test_the_file_kept_back_stays_held_and_stays_unasked(three_runs):
    """`--file-held` on a file the rules HELD: the other answer to one question.

    It writes one move permission and deliberately no classification row -- a
    person filing their own medical record has said where it goes, not what a
    model may see of it -- so the file is still protected, still held by the
    rules' own basis, and still put to no model on this or any later run.
    """
    state = three_runs
    current = _classification(state, KEPT)
    assert current.protected is True
    assert current.basis in cli.SAFETY_DOMAIN_BASES, current.basis
    for run_index in range(4):
        assert _handle(state, KEPT) not in state["asked_off_device"][run_index]
        assert (_placement_handle(state, KEPT)
                not in state["judged_for_placement"][run_index])


def test_file_held_on_a_file_the_rules_cleared_shuts_the_cloud_to_it(three_runs):
    """THE ARM OF 14 SEP, and the one the second corpus asked for: on a machine
    with no local model the rules are the only gate before the cloud, and they
    miss protected records. `--file-held` is the sentence the person has for one
    they know is theirs to keep.

    THE ROW SHUTS THE DOOR RATHER THAN OPENING IT, which is why a `user` row is
    safe here and would not be on an ordinary file: `model_route_permitted` reads
    the `protected` flag before it reads any basis, so a protected `user` row is
    refused the cloud at every site -- and the rules never retire a user row.

    MEASURED ACROSS THE FOUR RUNS. This file's situation was asked off the device
    on run 1, when the rules had cleared it. From the run that carries the
    gesture onward nothing about it is sent anywhere, at either site.
    """
    state = three_runs
    handle = _handle(state, CLEARED_KEPT)
    assert handle in state["asked_off_device"][0], (
        "the rules cleared this file and it was never asked about, so keeping "
        "it back measures nothing")
    current = _classification(state, CLEARED_KEPT)
    assert current.protected is True
    assert current.basis == USER
    assert current.reliability_state == USER_CONFIRMED
    placement = _placement_handle(state, CLEARED_KEPT)
    for run_index in (2, 3):
        assert handle not in state["asked_off_device"][run_index], run_index
        assert placement not in state["judged_for_placement"][run_index], run_index


def test_the_question_is_not_put_a_second_time_about_a_file_already_answered(
        three_runs):
    """ONE QUESTION, and both gestures are answers to it (`00` amendment 2 of
    13 Sep: the held files are put to the person as ONE question at the end of
    the run, with two gestures).

    `test_p7_file_released.test_the_screen_stops_naming_a_file_the_person_
    released` pins this half for `--release`, which gets it for free: the
    person's row supersedes the hold, so the store read at screen time no longer
    finds one. `--file-held` writes no classification row for a file the rules
    held, BY DESIGN, so the screen used to ask again -- under a header that says
    "nobody has been asked", which had stopped being true. `cli.main`'s own
    comment beside the gesture says what it is for: "a person who has just filed
    a protected file themselves should not have to run the command again to see
    that it took".

    SABOTAGE: drop `filed_by_hand` from the `_the_files_being_held` call in
    `downstream` and run 4's report asks about the medical record again.
    """
    state = three_runs
    fourth = state["said"][3]
    assert "being held here" not in fourth, (
        "the run asked again about files the person had already answered")
    assert f"--file-held {state['ids'][KEPT]}" not in fourth, fourth


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
    the `assert code == 0` in the fixture is that half.

    BOTH OPTIONS ARE OFFERED IN THE LIBRARY'S OWN WORDS and each is typable.
    """
    said = three_runs["said"][0]
    assert f"Which of these is {SCHEMA}?" in said, said
    for situation in BOTH_SITUATIONS:
        assert f"--answer situation:{SCHEMA}={situation}" in said, said
    assert f"3 files sit under {SCHEMA}" in " ".join(said.split()), said


def test_those_files_are_asked_the_schemas_own_fields_and_not_the_runs(
        three_runs):
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

    READ AT RUN 1'S OWN PLAN VERSION. Four runs write four proposals into one
    database, and this question is about the run in which the question was still
    open: by run 4 the person has answered it and these files ARE filed, which
    is the test below.

    The reason word is the one that says a call happened and left this file
    unjudged, and it is the same word for all three -- a property of the open
    situation rather than of one file's evidence.
    """
    placed, abstained = _run_decisions(three_runs, 0)
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
    assert f"Which of these is {SCHEMA}?" in state["said"][2], (
        "the run before the answer should still be asking")
    assert f"Which of these is {SCHEMA}?" not in state["said"][3], state["said"][3]
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


def test_the_answer_carries_the_situation_to_the_files_and_they_are_filed(
        three_runs):
    """THE WAY OUT, and what `104` §18.60 item 5 is for: the person answers the
    branch question and the next run files what the answer unlocked.

    THIS IS THE PIN THAT WAS xfail BEFORE THE ROUTE WAS FIXED. Site C, the
    placement judge, was the one model site whose route was built without the
    gate pass, so on a cloud-only deployment the only file it could be asked
    about was one carrying the person's own `user` row -- and these three
    abstained `no_model_judgement`, a call that never happened, however the
    person answered. Both halves are asserted: the judge WAS asked about each of
    them on the run that carries the answer, and each is filed.

    THE DESTINATION IS THE PERSON'S OWN FOLDER, and that is `00` §user-selection
    rather than a shortfall: the society's records carry no fact that fills
    `nonprofit.member-association`'s one folder level, so the best-supported node
    on the shortlist is the folder they are already in, and the model takes it.
    Nothing about them moves.
    """
    state = three_runs
    judged = set(state["judged_for_placement"][3])
    placed, abstained = _run_decisions(state, 3)
    for name in CLUB_FILES:
        assert _placement_handle(state, name) in judged, (
            f"the placement judge was never asked about {name}")
        where = f"{CLUB}/{name}"
        assert where in placed, abstained.get(where)
        assert placed[where] == CLUB, placed[where]


def test_the_answer_reaches_the_files_the_branch_was_opened_for(three_runs):
    """AND THE SCREEN SAYS SO, which the answer row on its own does not.

    The observable is the review set those three files are in. Before the answer
    they are a set of their own whose sentence names the question and prints both
    of its answers against these files -- "Saying what these are is 'Which of
    these is nonprofit?' below". After it the pointer is gone, because the
    question that was theirs has an answer.
    """
    state = three_runs
    pointer = f"Saying what these are is \"Which of these is {SCHEMA}?\""
    assert pointer in " ".join(state["said"][0].split()), state["said"][0]
    assert pointer not in " ".join(state["said"][3].split()), state["said"][3]


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
        assert all(crumb in said for crumb in folder.split("/")), (folder, said)
    assert "Kind of work -- academic:artifact_kind:work_type" in flat, said


# --- scene 3: the sort, in run 10's shape ---------------------------------------


def test_the_sort_writes_groups_a_tree_and_a_plan(three_runs):
    """`--accept-groups` with neither `--apply` nor `--freeze`, which is
    `run10.sh`'s own shape: P9 groups, P10 designs the tree, P11 decides, and all
    of it lands in the database as a PROPOSAL.

    FOUR GROUPS AND THEY ARE NAMED HERE, because a bare "more than none" would
    pass on one junk group: the two courses P9 seeded off a validated `subject`,
    the `work_type` seed the released file's own reading opened, and the branch
    group `--accept-groups` accepted under the person's label.

    THE FILES IN NO GROUP ARE NAMED TOO. A group needs an ANCHOR -- a validated
    fact two files share -- and the society's three records carry none: their
    fields are a model's proposals, which propose and settle nothing (`00`:42).
    They are filed all the same, by the judge, off the shortlist; grouping is
    where a file gets company, not where it gets a home.
    """
    state = three_runs
    database = state["database"]
    for table in ("groups", "memberships", "placement_decisions",
                  "plan_versions", "tree_nodes"):
        assert _rows(database, table) > 0, table
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        bases = sorted(row["proposed_basis"].split(";")[0][:20]
                       for row in conn.execute(
                           "SELECT proposed_basis FROM groups"))
        grouped = {row["file_id"] for row in conn.execute(
            "SELECT DISTINCT file_id FROM memberships")}
    finally:
        conn.close()
    assert len(bases) == 4, bases
    assert "subject=ECON2010" in bases and "subject=PHYS1401" in bases, bases
    ungrouped = {name for name, file_id in state["ids"].items()
                 if file_id not in grouped}
    assert set(CLUB_FILES) <= ungrouped, sorted(ungrouped)
    # One decision per file per run, and every file is on exactly one of them.
    assert _rows(database, "placement_decisions") == 11 * 4


def test_nothing_moved_and_no_move_was_even_planned(three_runs):
    """`00`: freezing the plan is the person's approval and moving files is a
    separate third invocation. Neither was given here, so the plan is a proposal
    and the person's folder is untouched -- byte for byte, mtime for mtime, over
    four runs that read every file in it.
    """
    state = three_runs
    assert _rows(state["database"], "move_plans") == 0
    assert _rows(state["database"], "move_journal") == 0
    assert state["after"] == state["before"], "the run changed somebody's folder"
    assert "Nothing was moved." in state["said"][3], state["said"][3]


def test_the_held_file_is_not_placed_and_the_released_one_is(three_runs):
    """The person's two answers, read at the end of the sort.

    The file they kept was shown to no model, so nothing proposed a folder for
    it, and it stays exactly where it is on its own path. The file they released
    is ordinary from that moment and the sort files it like any other.
    """
    state = three_runs
    placed, abstained = _run_decisions(state, 3)
    assert KEPT not in placed, placed.get(KEPT)
    assert abstained[KEPT] == "no_supported_destination", abstained[KEPT]
    assert (state["corpus"] / KEPT).is_file(), "the held file left its own path"
    assert placed[RELEASED] == LABEL, placed.get(RELEASED)


def test_the_grant_the_gesture_wrote_is_live_and_reaches_the_move_question(
        three_runs):
    """`--file-held`'s effect on where a file may go, end to end.

    TWO WRITES USED TO UNDO IT AND ONE READ USED TO MISS IT. `apply_file_held`
    writes one `automatic_move_permissions` grant at `cli.PLAN_VERSION`; the
    run's own two policy writes reset that field to `{}` fifteen milliseconds
    later, and P11 asks `automatic_move_permitted_for` at the run's own plan
    version, where the grant had never been written at all. So the person's
    answer neither survived the invocation that carried it nor reached the read
    that acts on it. `_permissions_in_force` is the one reader all three writers
    now share, and a plan version with no grants of its own inherits the standing
    ones -- because §8.4 makes the permission a statement about a FILE and
    amendment 2 of 13 Sep makes it the person's own answer, not a fact about a
    version number they never saw.
    """
    state = three_runs
    from privacy.moves import may_move_automatically
    from privacy.policy import current_policy
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        standing = current_policy(conn, plan_version=cli.PLAN_VERSION)
        verdicts = {name: may_move_automatically(
            conn, state["ids"][name], state["plans"][3])
            for name in (KEPT, CLEARED_KEPT, "PHYS 1401 syllabus.txt")}
    finally:
        conn.close()
    assert standing is not None
    assert standing.automatic_move_permissions == {
        state["ids"][KEPT]: True, state["ids"][CLEARED_KEPT]: True}, (
        standing.automatic_move_permissions)
    # The read P11 makes, at the plan the sort actually wrote.
    assert verdicts[KEPT].allowed, verdicts[KEPT].reason
    assert verdicts[CLEARED_KEPT].allowed, verdicts[CLEARED_KEPT].reason
    # And a file nobody granted anything for is unaffected either way: it is not
    # protected, so §8.4 never asked for a permission in the first place.
    assert verdicts["PHYS 1401 syllabus.txt"].allowed


def test_the_persons_own_folder_is_in_the_plan_as_theirs(three_runs):
    """`00` §user-selection: existing folders are shown as the person's own and
    nothing of theirs is moved, renamed or merged without being asked.

    The society's folder is in the proposal under its own name, marked as theirs
    -- not absorbed into the branch the judge named for the files inside it.
    """
    said = three_runs["said"][3]
    assert f"{CLUB}   [yours already]" in said, said


def test_every_answer_the_person_gave_is_a_learning_record_at_its_own_scope(
        three_runs):
    """`00` amendment 6 of 13 Sep: *"a person's answers are the product's memory
    of them. Every applied answer is a learning record at the question's
    scope"*.

    THREE ANSWERS AND THREE SCOPES, read back through the reader the product
    itself uses (`database_agent.learning.learning_records`) rather than off the
    tables it writes. The branch question's scope is `branch` and its subject is
    the schema the judge named; the two gestures that write a classification are
    the person's word about one FILE and are recorded at `file` against its id.

    THE FOURTH ANSWER IS DELIBERATELY NOT ONE, and it is worth stating so that a
    later reader does not add it: `--file-held` on a file the rules ALREADY held
    writes no classification row -- filing your own medical record says where it
    goes, not what a model may see of it -- so there is no reclassification to
    remember. What that answer leaves behind is the move permission asserted
    above and the question no longer being asked.
    """
    state = three_runs
    from database_agent.learning import learning_records
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        branch = learning_records(conn, "branch", SCHEMA)
        released = learning_records(conn, "file", state["ids"][RELEASED])
        kept_cleared = learning_records(conn, "file", state["ids"][CLEARED_KEPT])
        kept_held = learning_records(conn, "file", state["ids"][KEPT])
    finally:
        conn.close()
    assert branch, "the branch answer left no memory of the person"
    assert all(row["user_id"] == "t" for row in branch), [
        dict(row) for row in branch]
    assert released, "--release left no memory of the person"
    assert kept_cleared, "--file-held on a cleared file left no memory"
    assert not kept_held, (
        "--file-held on an already-held file wrote a classification row, which "
        "is the one thing its own pin says it must not do")

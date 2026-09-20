# tests/integration/test_the_sort_is_frozen_and_applied_on_a_copy.py
"""The five things the owner will type tomorrow morning, in order, on one
corpus and one database: the run, the answers, `--accept-groups`, `--freeze`,
`--apply`, `--apply-everything`, `--undo`, `--undo-everything`.

`00` amendment 5 of 9 Sep -- *"freezing the plan is the person's approval,
bounded by what the report named; moving files is a separate third invocation"*
-- is three sentences, and until this file there was no single pin that ran all
three against a disk. The pieces each had one: `tests/apply/test_freeze.py` owns
what a freeze record holds, `tests/apply/test_apply_and_undo.py` owns the move
round trip over hand-built plans, and
`tests/integration/test_cli_moves_nothing_without_apply.py` owns the negative.
What none of them does is drive `cli.main` from a folder of somebody's files
through to that folder rearranged and then back again, and assert at every step
on BOTH the database and the bytes on disk. That is what the owner is about to
do to a copy of their own folder, so that is what is pinned here.

**THE DEPLOYMENT IS THE OWNER'S** (`00` amendment 3 of 14 Sep, "cloud-only").
A cloud key, no local model, and `readers.model_routing.deepseek_invoke`
replaced by a recorder at the documented seam -- so the gate, the route, the
transport, the validator, the tree, the placement judge and the whole of
`cli.run` are the production path. Shape and stub are
`test_the_question_at_the_end_and_the_sort`'s, imported rather than rewritten,
for that file's own reason: one stub speaking one protocol.

**THE CORPUS IS FIFTEEN FILES A PERSON COULD HAVE, IN FOUR SITUATIONS.**

1. *`academic.coursework`, the one the person typed.* Seven coursework files in
   the folder root, across two courses and two terms.
2. *`nonprofit`, which the judge names and the person settles.* Three of a
   student society's records in a subfolder THE PERSON BUILT. The shipped
   library carries two situations under that schema and no recogniser raised
   either, so the run asks "Which of these is `nonprofit`?" and
   `--answer situation:nonprofit=nonprofit.member-association` is the answer.
3. *`research`, which the judge names and the person does NOT settle.* Three
   conference files in a second subfolder of theirs. Eight situations under the
   schema, no recogniser, no answer -- so `00` amendment 6 of 13 Sep holds and
   the files ARE NOT PLACED. They are the arm that proves a freeze cannot
   approve a file the run declined to place.
4. *The two the rules hold, and the third the person holds.* A passport note
   the person RELEASES (`--release`); a medical note the rules hold and the
   person LEAVES held, with no grant of any kind; and `ECON 2010 syllabus.txt`
   -- which the rules CLEARED and the person keeps anyway (`--file-held`), the
   arm of 14 Sep. The two held files differ in exactly one thing, the person's
   grant, which is what lets the assertions below say what the grant does.

**WHY THE SUBFOLDERS ARE THE ONLY THING THE JUDGE CAN TELL FILES APART BY.**
Measured by the sibling pins and true here: a site-G dossier for a short text
file releases the folder path, the mime type and the extension, and `filename`
is never released to any model. So each situation gets a folder of its own, the
stub reads the path, and everything in the root is answered `academic`.

**THE COLLISION IS PLANTED BETWEEN THE FREEZE AND THE APPLY, ON PURPOSE.**
`00`:171 is that the source is rechecked *immediately before* applying, and
`00`:172 that "the engine should never silently overwrite an existing file".
The way a person meets that is not a corpus built to collide: it is a file they
put in the destination folder themselves in the minutes between approving the
plan and running it. So this test writes
`Coursework/Spring2026/PHYS1401/syllabus/PHYS 1401 syllabus.txt`, with words of
its own, after `--freeze` has already printed the line that would move a file
of that name there -- and then asserts the plan stops rather than resolves.

**WHAT THIS FILE MEASURED, AND WHAT IT FOUND.** Every step below does what `00`
says. The four that are worth naming because they could each have gone the
other way:

  step                          what `00` says            what the code did
  --accept-groups               nothing moves             nothing moved
  --freeze                      approval, not the move    8 plans, 0 journal
  --apply <one branch>          only that branch          2 of 8, exactly
  --undo-everything             byte-for-byte back        byte-for-byte back

and the person's two gestures survive the runs after the one they were typed
on: the medical file is counted and never frozen, and the file they kept by
hand is frozen and moved because their own grant
(`privacy.moves.POLICY_PERMITS`, written by `apply_file_held`) says it may be.
NO PRODUCTION CODE IS CHANGED BY THIS COMMIT. The pin is the deliverable, and
what it pins is the product as it stands.
"""
from __future__ import annotations

import hashlib
import io
import json
import shlex
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
from test_the_question_at_the_end_and_the_sort import dark_level_stage  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from placement.vocabulary import PLACE  # noqa: E402
from privacy.moves import may_move_automatically  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from tree_design.store import nodes_for_version  # noqa: E402

# The stub's answers, imported and not rewritten, on the rule
# `test_a_fact_call_cache` states: one stub speaking one protocol, so this file
# and the pins that own those shapes cannot drift into describing two models.
from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _names, _released, _the_deterministic_winner,
)
from test_local_model_fact_pass import _answer_for  # noqa: E402

#: What the person typed on every run.
SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The two folders the person built. The one released item that differs per file
#: at site G, and therefore the only thing the stub may read to tell these files
#: apart.
CLUB = "Debate Society"
CONFERENCE = "NeurIPS 2026"

#: The schema the judge names for the society's folder, the two situations the
#: library carries under it, and the one the person picks. Deliberately the
#: SECOND: an answer that agreed with `situations_of(schema)[0]` would prove
#: nothing about the alphabetical pick being gone.
SCHEMA = "nonprofit"
CHOSEN = "nonprofit.member-association"
ANSWER = f"situation:{SCHEMA}={CHOSEN}"

#: The schema the judge names for the conference folder, and the one NOBODY
#: answers. Eight situations under it in the shipped library and no recogniser
#: raising any of them, which is exactly the state `00` amendment 6 of 13 Sep
#: says leaves a file unplaced.
RESEARCH_SCHEMA = "research"

#: The three files the person's two gestures are about.
RELEASED = "Passport renewal notes.txt"
KEPT = "Medical record summary.txt"
CLEARED_KEPT = "ECON 2010 syllabus.txt"

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
    CLEARED_KEPT:
        "ECON 2010 Syllabus\n\nFall 2025. Instructor: Dr. Ruiz. Credits: 4.\n",
    "ECON 2010 lecture 01.txt":
        "Lecture 01 - Aggregate demand\nECON 2010\nFall 2025. "
        "Instructor: Dr. Ruiz.\n",
    "ECON 2010 lecture 02.txt":
        "Lecture 02 - Money and banking\nECON 2010\nFall 2025. "
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

CONFERENCE_FILES = {
    "poster abstract.txt":
        "Poster abstract for the attention study.\nSubmitted to the poster "
        "track. Vision lab.\n",
    "talk slides notes.txt":
        "Speaker notes for the attention study talk.\nSpotlight session, "
        "twelve slides. Vision lab.\n",
    "PHYS 1401 poster.txt":
        "PHYS 1401 conference poster\nSpring 2026. Instructor: Dr. Lee. "
        "The term project, redrawn at A0 for the poster track.\n",
}

#: The branch whose line the person types first, and the file the collision is
#: planted against. Named here rather than picked out of the report by index, so
#: a reshaped tree fails loudly instead of testing a different branch quietly.
ONE_BRANCH = "Coursework/Spring2026/PHYS1401/lecture"
CLASH_BRANCH = "Coursework/Spring2026/PHYS1401/syllabus"
CLASHES_WITH = "PHYS 1401 syllabus.txt"
CLASH_WORDS = "A syllabus already filed here by hand, with different words.\n"

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}


# --- the cloud, stubbed at the deployment seam ----------------------------------


class _Cloud:
    """Every call this run put on the wire, and the dossier each one carried."""

    def __init__(self) -> None:
        self.payloads: list[bytes] = []

    def forget(self) -> None:
        self.payloads = []

    @staticmethod
    def _body(payload: bytes) -> dict:
        return json.loads(
            payload.decode("utf-8").split("The dossier follows.", 1)[1])

    def sites(self) -> Counter:
        return Counter(self._body(p)["call_site"] for p in self.payloads)

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            body = self._body(payload)
            site = body["call_site"]
            if site == cli.G_SITUATION_SENSITIVITY:
                where = " ".join(item["value"] for item in _released(body))
                if CLUB in where:
                    return _names(SCHEMA, body).encode("utf-8")
                if CONFERENCE in where:
                    return _names(RESEARCH_SCHEMA, body).encode("utf-8")
                return _names("academic", body).encode("utf-8")
            if site == cli.C_PLACEMENT:
                return _the_deterministic_winner(body).encode("utf-8")
            return _answer_for(payload.decode("utf-8")).encode("utf-8")
        return invoke


# --- the folder, and what is in it at any moment ---------------------------------


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in ROOT_FILES.items():
        (corpus / name).write_text(body)
    for folder, files in ((CLUB, CLUB_FILES), (CONFERENCE, CONFERENCE_FILES)):
        (corpus / folder).mkdir()
        for name, body in files.items():
            (corpus / folder / name).write_text(body)
    return corpus


def _on_disk(corpus: Path) -> dict[str, tuple]:
    """Every path under the folder: the folders, and each file's size, mtime and
    the digest of its bytes.

    THE DIGEST AS WELL AS THE SIZE AND THE MTIME, which
    `test_the_question_at_the_end_and_the_sort._on_disk` does not need and this
    one does: that file asserts nothing moved, and a move is visible in the
    paths alone. This one asserts that after an undo the folder is what it was,
    and a rewrite that preserved a path, a length and a timestamp would pass a
    comparison of those three.

    THE FOLDERS TOO, with a trailing `/`. `--undo` removes the folders the
    product made and must leave the ones the person made, and a file-only
    reading cannot tell an empty folder of theirs from one that is gone.
    """
    out: dict[str, tuple] = {}
    for path in sorted(corpus.rglob("*")):
        key = str(path.relative_to(corpus))
        if path.is_dir():
            out[key + "/"] = ("folder",)
        else:
            stat = path.stat()
            out[key] = (stat.st_size, stat.st_mtime_ns,
                        hashlib.sha256(path.read_bytes()).hexdigest())
    return out


def _files_on_disk(snapshot: dict[str, tuple]) -> set[str]:
    return {key for key in snapshot if not key.endswith("/")}


# --- what the database holds -----------------------------------------------------


def _rows(database: Path, table: str) -> int:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def _table(database: Path, sql: str, *params) -> list[sqlite3.Row]:
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return list(conn.execute(sql, params))
    finally:
        conn.close()


def _file_ids(database: Path) -> dict[str, str]:
    return {row["filename"]: row["file_id"]
            for row in _table(database, "SELECT file_id, filename FROM files")}


def _plan_version_in(report: str) -> str:
    """The proposal this run saved, off the line the run prints for the person.

    READ PER RUN AND NOT "THE LAST ONE IN THE TABLE", which is the difference
    between asking what the sort run decided and asking what the freeze did.
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


def _frozen_plans(database: Path, corpus: Path) -> dict[str, str]:
    """filename -> the path the frozen plan resolved for it.

    Straight off `move_plans`, which is `00`:156-170's record of what was
    approved, joined to `files` so the assertions below read in names rather
    than in uuids.
    """
    named = {row["file_id"]: row["filename"]
             for row in _table(database, "SELECT file_id, filename FROM files")}
    out: dict[str, str] = {}
    for row in _table(database,
                      "SELECT file_id, payload FROM move_plans "
                      "WHERE superseded_by IS NULL"):
        payload = json.loads(row["payload"])
        resolved = payload.get("resolved_destination_path")
        out[named[row["file_id"]]] = (
            str(Path(resolved).relative_to(corpus)) if resolved else "")
    return out


def _journal(database: Path, corpus: Path) -> list[dict]:
    """Every journal entry, newest last, in the words this test asserts in."""
    named = {row["file_id"]: row["filename"]
             for row in _table(database, "SELECT file_id, filename FROM files")}

    def under(path: str) -> str:
        return str(Path(path).relative_to(corpus))

    return [{"file": named[row["file_id"]],
             "kind": row["entry_kind"],
             "reverses": row["reverses_entry_id"],
             "entry_id": row["entry_id"],
             "from": under(row["original_source_path"]),
             "to": under(row["destination_path"]),
             "hash": row["content_hash"]}
            for row in _table(
                database,
                "SELECT entry_id, entry_kind, reverses_entry_id, file_id, "
                "original_source_path, destination_path, content_hash "
                "FROM move_journal ORDER BY rowid")]


# --- one corpus, one database, the whole morning ---------------------------------


@pytest.fixture(scope="module")
def the_morning(tmp_path_factory):
    """Four pipeline runs and four typed commands, chained on one database.

    MODULE SCOPED AND CHAINED for `test_the_question_at_the_end_and_the_sort`'s
    reason: `apply_answers` refuses an answer to a question no run has asked and
    `apply_release` refuses a file nothing is holding, so each gesture follows
    the run that offered it -- and `--apply` needs the plan `--freeze` wrote.

    THE ANSWER IS TYPED ONCE, on the sort run, and NOT repeated on the freeze.
    That is the question this arrangement asks: a gesture that only worked on
    the invocation it was typed on is the defect the sibling pin found in
    `--file-held`, and an answer re-typed every run would hide the same defect
    here.
    """
    root = tmp_path_factory.mktemp("frozen_and_applied")
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    before = _on_disk(corpus)
    cloud = _Cloud()
    said: list[str] = []
    typed_said: list[str] = []

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
        dark_level_stage(patch)

        def once(*extra: str) -> str:
            cloud.forget()
            out = io.StringIO()
            code = cli.main(
                [str(corpus), "--situation", SITUATION, "--label", LABEL,
                 "--user", "t", "--database", str(database), "--enable-cloud",
                 "--accept-groups", *extra], out=out)
            assert code == 0, out.getvalue()
            said.append(out.getvalue())
            return out.getvalue()

        def typed(command: str) -> str:
            """One line the product itself printed, run exactly as printed.

            `shlex.split(...)[1:]` and nothing else: the first word is the
            program name. Anything this test added or removed would be a test of
            a command the person was never shown.
            """
            out = io.StringIO()
            code = cli.main(shlex.split(command)[1:], out=out)
            assert code == 0, out.getvalue()
            typed_said.append(out.getvalue())
            return out.getvalue()

        once()                                            # the run that asks
        ids = _file_ids(database)
        # `--file-held` ON THE CLEARED FILE ONLY, and that is the whole point
        # of the arrangement. The medical note is left held by the RULES, with
        # no grant of any kind, so the two held files differ in exactly one
        # thing and the assertions below can tell which of them the grant is
        # doing the work for. Giving both the gesture -- which the sibling pin
        # does, for its own reason -- would leave this corpus with no
        # held-without-a-grant file at all.
        once("--release", ids[RELEASED], "--file-held", ids[CLEARED_KEPT])
        sort_report = once("--answer", ANSWER)            # step 2: the proposal
        after_sort = _on_disk(corpus)
        sorted_plans = _frozen_plans(database, corpus)
        freeze_report = once("--freeze")                  # step 3: the approval
        after_freeze = _on_disk(corpus)
        frozen = _frozen_plans(database, corpus)
        # READ NOW AND NOT AT THE END OF THE MODULE. The fixture is one chained
        # story and the journal fills up further down it; a test that asked "did
        # the freeze move anything?" after the applies had run would be asking
        # about the applies.
        at_freeze = {table: _rows(database, table) for table in
                     ("move_journal", "execution_records",
                      "collision_resolutions")}

        by_branch = {}
        for line in freeze_report.splitlines():
            if "Move these:" in line:
                command = line.split("Move these:")[1].strip()
                by_branch[shlex.split(command)[-1]] = command
        everything = next(
            line.strip() for line in freeze_report.splitlines()
            if "--apply-everything" in line)

        # THE COLLISION, planted in the minutes between approving the plan and
        # running it -- `00`:171's recheck is about exactly this window.
        clash = corpus / CLASH_BRANCH
        clash.mkdir(parents=True)
        (clash / CLASHES_WITH).write_text(CLASH_WORDS)
        before_apply = _on_disk(corpus)

        typed(by_branch[ONE_BRANCH])                      # step 4a: one branch
        after_one = _on_disk(corpus)
        journal_after_one = _journal(database, corpus)
        typed(everything)                                 # step 4b: the rest
        after_all = _on_disk(corpus)
        journal_after_all = _journal(database, corpus)
        typed(by_branch[ONE_BRANCH].replace("--apply ", "--undo "))
        after_undo_one = _on_disk(corpus)                 # step 5a
        typed(everything.replace("--apply-everything", "--undo-everything"))
        after_undo_all = _on_disk(corpus)                 # step 5b

    return {
        "corpus": corpus, "database": database, "ids": ids,
        "said": said, "typed": typed_said,
        "sort_report": sort_report, "freeze_report": freeze_report,
        "by_branch": by_branch, "apply_everything": everything,
        "sort_plan": _plan_version_in(sort_report),
        "freeze_plan": _plan_version_in(freeze_report),
        "sorted_plans": sorted_plans, "frozen": frozen,
        "at_freeze": at_freeze,
        "before": before, "after_sort": after_sort, "after_freeze": after_freeze,
        "before_apply": before_apply, "after_one": after_one,
        "after_all": after_all, "after_undo_one": after_undo_one,
        "after_undo_all": after_undo_all,
        "journal_after_one": journal_after_one,
        "journal_after_all": journal_after_all,
    }


# --- step 1: the classification runs and the person's answers --------------------


def test_the_person_gestures_reach_the_files_they_named(the_morning):
    """`00` amendment 2 of 13 Sep, and the arm of 14 Sep item 4.

    Two gestures typed on ONE run, read two runs later, and three different
    verdicts out of `privacy.moves.may_move_automatically` -- which is the one
    reader that decides whether this product may move a file on its own.

    The passport is ordinary on the person's word. The medical note carries no
    grant and may not be moved. The file the RULES CLEARED is protected on the
    person's word AND carries their grant, which is the whole of
    `apply_file_held`: the row shuts the cloud door, the grant opens the move.
    """
    state = the_morning
    database, plan = state["database"], state["freeze_plan"]
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        verdicts = {name: may_move_automatically(conn, state["ids"][name], plan)
                    for name in (RELEASED, KEPT, CLEARED_KEPT)}
    finally:
        conn.close()
    assert (verdicts[RELEASED].allowed, verdicts[RELEASED].reason) == \
        (True, "not_protected"), verdicts[RELEASED]
    assert (verdicts[KEPT].allowed, verdicts[KEPT].reason) == \
        (False, "protected_without_permitting_policy"), verdicts[KEPT]
    assert (verdicts[CLEARED_KEPT].allowed, verdicts[CLEARED_KEPT].reason) == \
        (True, "policy_permits"), verdicts[CLEARED_KEPT]


def test_what_file_held_actually_does_to_a_file(the_morning):
    """WHAT THE OWNER WILL SEE TOMORROW IF THEY TYPE `--file-held`, measured.

    The gesture does TWO things and only one of them is in its own help text:

    1. it shuts the cloud door on the file (a `user` row, `protected=True`,
       read by `protected_cloud_denies` before any basis), and
    2. it GRANTS `privacy.moves.POLICY_PERMITS`, which is permission for this
       product to move the file into the tree.

    `apply_file_held`'s docstring says so in as many words and argues for it. It
    is repeated here because it is the opposite of what the same gesture's help
    text says -- "--file-held FILE_ID keeps a file here" -- and of how `00`
    amendment 2 of 13 Sep names it: "(keep it here, file it by hand)".

    So whether a file the person said "keep this one" about actually stays put
    turns on something they were never told: WHETHER THE RUN COULD PLACE IT.
    Both files below carry the identical grant. The medical note stays where it
    is because a protected file assembles no dossier, reaches no model and
    therefore reaches no destination. `ECON 2010 syllabus.txt` names its course,
    its term and its kind in its own first line, which is a unique direct match
    the deterministic path can place without a model -- so it is frozen, and
    `--apply-everything` moves it.

    Neither half of that is a bug in the code that produced it; the question of
    what `--file-held` should mean is the owner's, and this pin exists so that
    the answer is on the record before they type it on their own folder rather
    than after. `test_00_says_a_file_the_person_kept_is_not_moved` below is the
    other reading, marked `xfail(strict=True)`, so the day it is settled one of
    these two fails loudly.
    """
    state = the_morning
    assert KEPT not in state["frozen"], "the medical note was approved for a move"
    assert state["after_undo_all"][KEPT] == state["before"][KEPT]
    assert CLEARED_KEPT in state["frozen"], (
        "the file the person kept was not approved; the measurement above has "
        "changed and the sentence in this docstring with it")
    assert state["frozen"][CLEARED_KEPT] == "Coursework/Fall2025/ECON2010/" \
        + CLEARED_KEPT
    assert CLEARED_KEPT not in _files_on_disk(state["after_all"]), (
        "the file the person kept did not move, so the grant did nothing")


@pytest.mark.xfail(strict=True, reason=(
    "THE HELP-TEXT READING, which the product does not implement. `cli.py`'s "
    "own line is '--file-held FILE_ID keeps a file here', and `00` amendment 2 "
    "of 13 Sep glosses the gesture '(keep it here, file it by hand)' -- both of "
    "which a person reads as 'this one stays put'. `apply_file_held` instead "
    "grants POLICY_PERMITS, and so does the brief this pin was written from. "
    "The two readings are not reconciled anywhere, and nothing on the screen "
    "tells the person which one they are getting. NOT DECIDED HERE: the grant "
    "is deliberate and argued in that function's docstring, and withdrawing it "
    "would change which of the owner's files move on their real folder. This "
    "is a tripwire so the question cannot be lost, not a verdict on it."))
def test_the_help_text_reading_of_file_held(the_morning):
    """A file the help text says is kept here, pinned against what happens."""
    state = the_morning
    assert CLEARED_KEPT not in state["frozen"], (
        "a file the person said to keep here was approved for a move")


def test_the_branch_answer_survives_the_run_it_was_typed_on(the_morning):
    """`00` amendment 6 of 13 Sep: "a person's answers are the product's memory
    of them". Typed on the sort run, NOT repeated on the freeze, and the society's
    three files are settled on both.

    The sibling pin found a gesture that did not survive its own run. This is the
    same question asked of the other gesture, one run later.
    """
    state = the_morning
    for plan in (state["sort_plan"], state["freeze_plan"]):
        placed, abstained = _decisions_at(state["database"], state["corpus"],
                                          plan)
        for name in CLUB_FILES:
            key = f"{CLUB}/{name}"
            assert key in placed, (
                f"{key} is unplaced at {plan}; the person's answer did not "
                f"reach it -- {abstained.get(key)}")


def test_the_files_nobody_answered_for_are_not_placed(the_morning):
    """`00` amendment 6 of 13 Sep: a schema the judge names resolves to a
    situation only through a recogniser or the person's answer, "meanwhile the
    file is asked its schema's fields and is not placed".

    Nobody answered "Which of these is research?", so the conference folder's
    three files carry a reason and no destination -- on the sort run and on the
    freeze. This is the arm that gives the freeze below something it must refuse
    to approve.
    """
    state = the_morning
    placed, abstained = _decisions_at(state["database"], state["corpus"],
                                      state["freeze_plan"])
    for name in CONFERENCE_FILES:
        key = f"{CONFERENCE}/{name}"
        assert key not in placed, f"{key} was placed with the question open"
        assert abstained.get(key), f"{key} has no reason for not being placed"
    assert f"situation:{RESEARCH_SCHEMA}=" in state["sort_report"], (
        "the report does not offer the answer that would settle them")


# --- step 2: --accept-groups, the proposal that moves nothing --------------------


def test_the_sort_run_lands_a_proposal_and_moves_not_one_byte(the_morning):
    """`00` amendment 5 of 9 Sep, first sentence. A run with `--accept-groups`
    and neither `--freeze` nor `--apply` writes a tree, decisions and a plan
    version, and leaves the folder exactly as it found it.
    """
    state = the_morning
    database = state["database"]
    assert _rows(database, "plan_versions") > 0
    assert _rows(database, "tree_nodes") > 0
    assert _rows(database, "placement_decisions") > 0
    assert state["sorted_plans"] == {}, (
        "a run nobody froze wrote move plans")
    assert state["after_sort"] == state["before"], (
        "the sort run changed the folder")
    assert "Nothing was moved." in state["sort_report"]


def test_the_proposal_prints_every_branch_and_where_each_file_would_go(
        the_morning):
    """`00` §"the output of this stage is a proposed destination tree", read as
    a person reads it: the folders this plan would build, and under them the
    name of every file and the folder it would go into.

    The protected file is the exception `00` amendment 6 of 9 Sep makes and the
    owner ruled on 2 Sep: counted on the screen with its destination named, and
    its filename behind `--show-protected`.
    """
    state = the_morning
    report = state["sort_report"]
    placed, _ = _decisions_at(state["database"], state["corpus"],
                              state["sort_plan"])

    assert "Folders in this plan:" in report
    for leaf in ("Coursework", "Fall2025", "ECON2010", "Spring2026",
                 "PHYS1401", "lecture", "problem set", "syllabus"):
        assert leaf in report, leaf

    # Every placed file is named on the screen with the folder it would go to --
    # except a PROTECTED one, which is counted with its destination named and
    # its filename left off. Both of the two are protected here: the medical
    # note by the rules, and `ECON 2010 syllabus.txt` because the person's own
    # `--file-held` wrote a `user` row saying so.
    for name, chain in placed.items():
        leaf = chain.rsplit("/", 1)[-1]
        if Path(name).name in (KEPT, CLEARED_KEPT):
            continue
        assert Path(name).name in report, name
        assert f"file into {leaf}" in report or "belongs there" in report, chain
    for name in (KEPT, CLEARED_KEPT):
        assert name not in report, (
            f"the proposal named {name}, which is protected material")
    assert "protected file" in report and "--show-protected" in report


# --- step 3: --freeze, the approval that still moves nothing ---------------------


def test_freezing_writes_a_frozen_tree_and_a_plan_version_and_moves_nothing(
        the_morning):
    """`00` amendment 5 of 9 Sep, second sentence: freezing the plan is the
    person's approval, and moving files is a separate third invocation.

    So: a `frozen_trees` row against this run's plan version, a `move_plans` row
    per approved file, an EMPTY journal, and a folder untouched.
    """
    state = the_morning
    database = state["database"]
    frozen_versions = {row["plan_version_id"] for row in
                       _table(database, "SELECT plan_version_id FROM frozen_trees")}
    assert state["freeze_plan"] in frozen_versions, (
        f"{state['freeze_plan']} has no frozen tree")
    assert state["frozen"], "the freeze approved nothing"
    assert state["at_freeze"]["move_journal"] == 0, "a freeze moved a file"
    assert state["at_freeze"]["execution_records"] == 0
    assert state["at_freeze"]["collision_resolutions"] == 0
    assert state["after_freeze"] == state["before"], (
        "the freeze changed the folder")


def test_the_freeze_prints_one_line_per_branch_saying_what_to_type(the_morning):
    """`--freeze`'s own promise, in `cli.py`'s help: "what it prints is one line
    per branch saying exactly what to type to move that branch".

    Every branch that froze a file has a line, every line names that branch, and
    the one that moves all of it is printed too. `typed()` runs these verbatim
    below, so a line that was not runnable would fail the fixture rather than a
    string comparison here.
    """
    state = the_morning
    branches = state["by_branch"]
    assert branches, "the freeze printed no line to type"
    assert ONE_BRANCH in branches, sorted(branches)
    assert CLASH_BRANCH in branches, sorted(branches)
    for branch, command in branches.items():
        assert "--apply" in command and shlex.split(command)[-1] == branch
        assert str(state["corpus"]) in command
        assert str(state["database"]) in command
    assert "--apply-everything" in state["apply_everything"]
    assert "Nothing has moved yet." in state["freeze_report"]

    # One line per branch that froze something, and no line for one that did not.
    frozen_branches = {Path(path).parent.as_posix()
                       for path in state["frozen"].values() if path}
    assert frozen_branches <= set(branches), (
        f"{frozen_branches - set(branches)} froze files and got no line")


def test_the_freeze_refuses_the_protected_file_and_the_unplaced_ones(
        the_morning):
    """Two different refusals, and `00` gives each a different reason.

    The medical note is protected with no grant, so amendment 6 of 9 Sep counts
    it and does not name it -- freezing is not permission to move a protected
    file. The conference folder's three are simply not placed, so there is
    nothing to approve. Neither is silently omitted: both are on the screen.
    """
    state = the_morning
    report = state["freeze_report"]
    assert KEPT not in state["frozen"], (
        "a protected file with no grant was approved for a move")
    assert "protected file(s), counted here and not named" in report
    assert KEPT not in report, "the freeze named somebody's protected file"
    for name in CONFERENCE_FILES:
        assert name not in state["frozen"], f"{name} was approved unplaced"
        assert f"{CONFERENCE}/{name}" in report, (
            "a file the freeze left out is not on the screen")


def test_the_freeze_carries_the_file_the_person_kept_because_the_grant_says_so(
        the_morning):
    """The arm of 14 Sep, and the difference between the two held files.

    Both are protected. One carries the person's grant and one does not, and
    `privacy.moves.may_move_automatically` is the only thing that separates
    them -- so the freeze approves one and refuses the other.
    """
    state = the_morning
    assert CLEARED_KEPT in state["frozen"], (
        "the person's grant did not reach the freeze")
    assert KEPT not in state["frozen"]


# --- step 4: --apply for one branch, then --apply-everything ---------------------


def test_one_branch_moves_exactly_the_files_that_branch_froze(the_morning):
    """`--apply BRANCH`: "move the files frozen for one branch", and no others.

    The whole of it: the two files that branch froze are at their frozen paths,
    every other file is where it was, and the count on the screen is two.
    """
    state = the_morning
    mine = {name for name, path in state["frozen"].items()
            if path and Path(path).parent.as_posix() == ONE_BRANCH}
    assert mine, f"nothing froze for {ONE_BRANCH}"

    moved = _files_on_disk(state["after_one"])
    untouched = _files_on_disk(state["before_apply"]) - {
        name for name in _files_on_disk(state["before_apply"])
        if Path(name).name in mine}
    for name in mine:
        assert state["frozen"][name] in moved, name
        assert name not in moved, f"{name} is still in the corpus root"
    assert untouched <= moved, (
        f"{untouched - moved} moved and no line of the person's named it")
    assert f"Moved: {len(mine)} file(s). Not moved: 0." in state["typed"][0]


def test_apply_everything_moves_the_rest_and_the_disk_equals_the_plan(
        the_morning):
    """`00`:155: the plan is what was approved, and the disk after is the plan.

    Every frozen plan except the one the collision stopped has its file at the
    path the plan resolved, and nothing else in the folder moved. This is the
    assertion the owner is really buying: the folder they get is the folder the
    report showed them.
    """
    state = the_morning
    on_disk = _files_on_disk(state["after_all"])
    stopped = {CLASHES_WITH}
    for name, path in state["frozen"].items():
        if not path or name in stopped:
            continue
        assert path in on_disk, f"{name} is not at {path}"
        assert name not in on_disk, f"{name} is still where it started"

    # And the folder holds exactly what it held: the same files, renamed by
    # their new paths and nothing else added or lost.
    assert len(on_disk) == len(_files_on_disk(state["before_apply"])), (
        "applying the plan changed how many files the folder holds")


def test_the_journal_records_every_move_with_the_path_it_came_from(the_morning):
    """`00`:175: "an undo entry should include the original source path,
    destination path, content hash at the time of movement".

    One entry per move, each naming where the file came from and where it went,
    with the hash it had when it was moved -- which is what makes the undo
    conditional rather than destructive.
    """
    state = the_morning
    applied = [entry for entry in state["journal_after_all"]
               if entry["reverses"] is None]
    moved = {entry["file"]: entry for entry in applied}
    expected = {name: path for name, path in state["frozen"].items()
                if path and name != CLASHES_WITH}
    assert set(moved) == set(expected), (
        f"the journal and the plan disagree about what moved: "
        f"{set(moved) ^ set(expected)}")
    for name, path in expected.items():
        entry = moved[name]
        assert entry["to"] == path, (name, entry["to"], path)
        assert entry["from"] == name, (
            f"{name} came from {entry['from']}, not from where it was")
        assert len(entry["hash"]) == 64, entry["hash"]
    assert _rows(state["database"], "execution_records") == len(state["frozen"]), (
        "every plan the apply considered gets an execution record, stopped or not")


def test_the_collision_is_recorded_and_nothing_is_written_over(the_morning):
    """`00`:172: "the engine should never silently overwrite an existing file",
    and the collision is a record, not a resolution somebody made for you.

    The file the person put in the destination folder by hand is byte-for-byte
    what they wrote. The file the plan would have moved there is still where it
    started. One `collision_resolutions` row says so, and the screen says it in
    words a person can act on.
    """
    state = the_morning
    corpus = state["corpus"]
    landed = corpus / CLASH_BRANCH / CLASHES_WITH
    assert landed.read_text() == CLASH_WORDS, (
        "the person's own file was written over")
    assert CLASHES_WITH in _files_on_disk(state["after_all"]), (
        "the stopped file did not stay where it was")

    rows = _table(state["database"],
                  "SELECT colliding_destination_path, collision_kind, "
                  "behaviour_applied, outcome FROM collision_resolutions")
    assert len(rows) == 1, [dict(row) for row in rows]
    (row,) = rows
    assert Path(row["colliding_destination_path"]).name == CLASHES_WITH
    assert row["outcome"] != "applied", dict(row)
    assert "already in that folder" in state["typed"][1]
    assert "Nothing was moved or written over." in state["typed"][1]
    assert CLASHES_WITH not in {entry["file"] for entry
                                in state["journal_after_all"]}


def test_the_protected_file_the_person_kept_never_moved(the_morning):
    """The security constraint, on disk rather than in a table.

    `00` amendment 6 of 9 Sep and the owner's ruling of 14 Sep item 4: a
    protected file with no grant from the person is counted and left. Through a
    freeze, two applies and two undos, it never leaves the folder it was in.
    """
    state = the_morning
    for moment in ("after_freeze", "before_apply", "after_one", "after_all",
                   "after_undo_one", "after_undo_all"):
        assert KEPT in _files_on_disk(state[moment]), (
            f"the protected file left the corpus root at {moment}")
        assert state[moment][KEPT] == state["before"][KEPT], (
            f"the protected file changed at {moment}")
    assert KEPT not in {entry["file"] for entry in state["journal_after_all"]}


# --- step 5: --undo of one move, and --undo-everything ---------------------------


def test_undo_of_one_branch_puts_exactly_those_files_back(the_morning):
    """`--undo BRANCH`: "put every file this product moved into one branch back
    exactly where it came from". One branch, and the rest still filed.
    """
    state = the_morning
    mine = {name for name, path in state["frozen"].items()
            if path and Path(path).parent.as_posix() == ONE_BRANCH}
    back = _files_on_disk(state["after_undo_one"])
    for name in mine:
        assert name in back, f"{name} did not come back"
        assert state["after_undo_one"][name] == state["before"][name], (
            f"{name} came back changed")
    others = {path for name, path in state["frozen"].items()
              if path and name not in mine and name != CLASHES_WITH}
    assert others <= back, (
        f"{others - back} was put back and nobody asked for it")
    assert f"Put back: {len(mine)} file(s). Could not be put back: 0." \
        in state["typed"][2]


def test_undo_everything_restores_the_corpus_byte_for_byte(the_morning):
    """`00`:175, and the sentence the owner needs before they run this on their
    own folder: after taking it all back, the folder is what it was.

    Byte for byte, path for path, folder for folder -- INCLUDING the folder the
    person made themselves between the freeze and the apply, which `--undo` must
    leave and does ("No folder you made was removed"), and the file they put in
    it, which never moved.
    """
    state = the_morning
    assert state["after_undo_all"] == state["before_apply"], {
        key: (state["before_apply"].get(key), state["after_undo_all"].get(key))
        for key in set(state["before_apply"]) | set(state["after_undo_all"])
        if state["before_apply"].get(key) != state["after_undo_all"].get(key)}
    # And that is the original corpus plus exactly the two things the person
    # added by hand, so the comparison above is not passing on an empty folder.
    added = set(state["before_apply"]) - set(state["before"])
    assert added == {f"{CLASH_BRANCH}/{CLASHES_WITH}"} | {
        f"{parent}/" for parent in
        ("Coursework", "Coursework/Spring2026",
         "Coursework/Spring2026/PHYS1401",
         "Coursework/Spring2026/PHYS1401/syllabus")}, sorted(added)
    for name in (*ROOT_FILES, *(f"{CLUB}/{n}" for n in CLUB_FILES),
                 *(f"{CONFERENCE}/{n}" for n in CONFERENCE_FILES)):
        assert state["after_undo_all"][name] == state["before"][name], name


def test_the_journal_says_every_move_was_reversed(the_morning):
    """`00`:136's append-only provenance log, read at the end of the morning.

    Nothing was deleted to undo a move: every applied entry is still there and
    each has a reversing entry pointing at it by id. A journal that recorded the
    move and then forgot it would leave the person unable to say what happened.
    """
    state = the_morning
    entries = state["journal_after_all"] and _journal(state["database"],
                                                      state["corpus"])
    applied = [entry for entry in entries if entry["reverses"] is None]
    reversals = [entry for entry in entries if entry["reverses"] is not None]
    assert applied, "no move was recorded"
    assert {entry["reverses"] for entry in reversals} == {
        entry["entry_id"] for entry in applied}, (
        "the journal does not say every move was put back")
    assert len(entries) == len(applied) + len(reversals)
    # And each reversal names the same two paths as the move it undoes, so the
    # log reads as a round trip rather than as two unrelated events.
    by_id = {entry["entry_id"]: entry for entry in applied}
    for entry in reversals:
        moved = by_id[entry["reverses"]]
        assert {entry["from"], entry["to"]} == {moved["from"], moved["to"]}, (
            entry, moved)
        assert moved["from"] in _files_on_disk(state["after_undo_all"]), (
            f"{entry['file']} is not back at {moved['from']}")
        assert moved["to"] not in _files_on_disk(state["after_undo_all"]), (
            f"{entry['file']} is still at {moved['to']}")


# --- what this corpus found on the way, and the fix it is the pin for ------------


def _values_block(database: Path, protected: set[str], *,
                  show_protected: bool = False) -> str:
    """`cli._print_values_to_confirm` over THIS run's database, with a set of
    files declared protected.

    The patch is on `_protected_file_ids`, which is the function's own reader and
    the one `104` §18.2 gap 10 made the single source for the screen's protected
    counts. Patching it rather than writing classification rows is what makes
    this deterministic: the defect below depended on which file id sorted first
    among the files carrying a value, and a uuid is not something a test can
    arrange.
    """
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    out = io.StringIO()
    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(cli, "_protected_file_ids", lambda _conn: set(protected))
            cli._print_values_to_confirm(conn, out,
                                         show_protected=show_protected)
    finally:
        conn.close()
    return out.getvalue()


def test_the_new_values_block_never_names_a_protected_file(the_morning):
    """THE DEFECT THIS CORPUS FOUND, AND IT IS A PRIVACY ONE.

    "New values the model proposed, waiting on you" names one file per proposed
    value -- in its heading, in a quoted line of that file's own text, and inside
    each of the three commands the person is told to type. The file it named was
    `sorted(...)[0]` over `(file_id, fact_id)`, and a file id is a uuid: WHICH of
    the files carrying a value got named was effectively random, and a protected
    one was named whenever the draw fell that way.

    Measured on this corpus before the fix: `ECON 2010 syllabus.txt` -- protected
    because the person's own `--file-held` said so -- was printed five times, with
    a line of its text, in THREE RUNS IN TWELVE. The owner's ruling of 2 Sep has
    no exception for this block, and the rest of the same report already obeys it.

    The fix is to name a file that may be named. Three assertions, and the second
    is the one that keeps the fix honest rather than merely quiet: the value is
    still on the screen, and the count still counts every file.
    """
    state = the_morning
    database = state["database"]
    open_block = _values_block(database, protected=set())
    assert "New values the model proposed" in open_block, (
        "this corpus proposed no value, so this test proves nothing")

    # Every file carrying a proposed value declared protected: the value stays,
    # the count stays, no name and no command are printed, and the one command
    # that would show the person their own files is offered instead.
    everything = set(_file_ids(database).values())
    shut = _values_block(database, protected=everything)
    for name in (*ROOT_FILES, *CLUB_FILES, *CONFERENCE_FILES):
        assert name not in shut, f"{name} was named in a shut block"
    assert "protected and counted here rather than named" in shut
    assert "--show-protected" in shut
    for gesture in ("--reject", "--confirm", "--rename"):
        assert gesture not in shut, (
            f"{gesture} was offered with no filename to put in it")
    assert "-- on " in shut, "the count went off the screen with the name"
    # AND THE ONE SENTENCE ON THIS SCREEN THAT IS NOT A NAME. `104` §18.2 gap 1
    # prints what the rules read for a field the model disagreed with, and it
    # names two VALUES and no file -- so it belongs in this arm too, which is
    # the arm where the person has least else to go on.
    assert "The rules read" in open_block, (
        "this corpus has no disagreement, so the next assertion proves nothing")
    assert "The rules read" in shut, (
        "the rules' own value was withheld along with the filenames")

    # `--show-protected` IS HONOURED, because the arm above offers it. A flag
    # this block told the person to type and then ignored would be `84` §6's
    # own failure one line later.
    asked = _values_block(database, protected=everything, show_protected=True)
    assert "protected and counted here rather than named" not in asked
    assert "--confirm " in asked, (
        "--show-protected did not give the person back the gestures")

    # And with ONLY the protected one shut, the block still answers the question:
    # it names one of the other files carrying the same value, so the person can
    # still type a gesture.
    one = {state["ids"][CLEARED_KEPT]}
    partly = _values_block(database, protected=one)
    assert CLEARED_KEPT not in partly, (
        "the protected file was named although another file carried the value")
    assert "--confirm " in partly, (
        "the question stopped being answerable although a nameable file carried "
        "the value")


# --- one file, two destinations, one approved set --------------------------------
#
# WHAT `110` §3.3 SAYS IS NOT WHAT THE CODE DOES, and this block is the pin for
# the difference. §3.3 reads `cli.py`'s `--apply` unioning "the nodes of EVERY
# frozen version" and concludes that freezing twice leaves both trees live. It
# read the union and not its input. `apply_run.freeze.frozen_plans` takes
# `MAX(created_at) WHERE superseded_by IS NULL` and then the rows carrying
# exactly that value, `cli.py`'s clock is `datetime.now(timezone.utc)` so two
# invocations cannot share one, and `tests/apply/test_freeze.py`'s
# `test_freezing_again_replaces_the_earlier_proposal` already pins the result:
# after a second freeze, reading back gives the second proposal ONLY.
# `freeze.py`'s own module docstring says the same thing in words -- "re-freezing
# does not have to supersede anything ... they are simply no longer the approved
# set". So a second freeze is not the defect, and `plan_versions.state` going
# unwritten is a documented consequence of that design rather than a gap.
#
# THE SHAPE §3.3 WAS REACHING FOR IS REAL, and it arrives through a different
# door: ONE approved set that names ONE file TWICE, for two different folders.
# `apply_run.freeze.freeze` walks the decisions it is handed and writes one plan
# per placement, and it is the only reader of that list which does NOT first take
# `placement.versions._current`. `_current`'s own docstring says what the raw
# list can hold -- "a subject can be decided twice in one pass -- a group member
# placed by its packet and then resolved again as shared material is the shape
# that does it" -- and `carry_onto` and `scoped_general_demand`, the two readers
# that do take it, exist because of that. So a run that reaches the freeze with a
# withdrawn row still in the list freezes the withdrawn placement beside the one
# that stands, and `--apply-everything` then has two contradicting instructions
# for one of somebody's files and no way to tell which they meant.
#
# THE ROOT CAUSE IS NOT FIXED HERE and deliberately so. Taking `_current` in
# `freeze` would drop the earlier row -- which is a decision about WHICH plan
# governs, and that is `110`'s Decision 5, the owner's. What is built here is the
# last gate before bytes move: `--apply` refuses, names what is in conflict, and
# moves nothing.


#: The two branches the small world below files into. They do not share a parent,
#: for `tests/apply/conftest.py`'s reason: a world whose branches nest inside one
#: another cannot tell "two destinations" from "one destination and its parent".
_TWO_BRANCHES = (("n-course", "Coursework", None),
                 ("n-read", "Reading Inbox", None))

#: The two files. `_CONTESTED` is the one the freeze is made to name twice.
_CONTESTED = "PHYS 1401 syllabus.txt"
_UNCONTESTED = "saved article.txt"
_SMALL_CORPUS = {
    _CONTESTED: "PHYS 1401, spring term, week one.\n",
    _UNCONTESTED: "an article kept to read later.\n",
}


def _freeze_a_small_world(root: Path, *, contested: bool):
    """A corpus, a database and ONE freeze, written by the product's own `freeze`.

    NOT THROUGH `cli.main`, and that is the honest limit of this fixture. The
    double decision comes out of a group pass resolving one member twice
    (`placement.versions._current`), which this file's stubbed cloud corpus has
    no deterministic way to provoke -- so the shape is staged at the seam that
    produces it, `apply_run.freeze.freeze`, with two `PlacementDecision`s for one
    subject. Everything downstream of that seam is the product: the plans are
    written by `record_plan`, the database is the one `--apply` opens, and the
    move is driven by `cli.main` exactly as a person would type it.

    `contested=False` builds the same world with the twin decision left out, so
    the two arms differ in exactly one thing and the green arm below can say
    that the refusal is about the conflict rather than about this small world.
    """
    import dataclasses
    from itertools import count

    from database_agent.db import create_schema, open_database
    from database_agent.files_table import record_file
    from eval_harness.store import create_eval_schema
    from grouping.schema import create_grouping_schema
    from mutation.constraints import FilesystemConstraints
    from mutation.schema import create_mutation_schema
    from mutation.vocabulary import STOP_AND_ASK
    from placement.fixtures import EXACT_PLACEMENT
    from placement.records import Destination, PrivacyState, Subject
    from placement.schema import create_placement_schema
    from placement.vocabulary import AUTO_ELIGIBLE, ORDINARY
    from privacy.classification_store import (
        ClassificationRecord, ClassificationStore,
    )
    from privacy.schema import create_privacy_schema
    from tree_design.records import Node, PlanVersion
    from tree_design.schema import create_tree_schema
    from tree_design.store import (
        freeze_version, write_node, write_plan_version,
    )

    from apply_run.freeze import freeze

    version = "plan-one-file-twice"
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in _SMALL_CORPUS.items():
        (corpus / name).write_text(body)

    database = root / "holder" / "plan.sqlite"
    conn = open_database(database, scan_roots=[corpus])
    for create in (create_schema, create_eval_schema, create_privacy_schema,
                   create_placement_schema, create_mutation_schema,
                   create_grouping_schema, create_tree_schema):
        create(conn)

    # The tree, written where `--apply` reads it back from. `nodes_for_version`
    # is what the green arm reaches once nothing is in conflict, and a world with
    # no `tree_nodes` rows would refuse there for a reason that is not this one.
    #
    # DRAFT FIRST AND FROZEN AFTER, because `write_node` refuses a frozen version
    # outright (§8.8: an edit opens a draft). That is the product's own order and
    # not a workaround: a tree is built and then approved.
    write_plan_version(conn, PlanVersion(
        plan_version_id=version, predecessor_id=None, state="draft",
        created_at="2026-09-20T00:00:00+00:00", cross_folder_moves=True,
        selection_id="selection-one-file-twice"))
    nodes = []
    for ordinal, (node_id, label, parent) in enumerate(_TWO_BRANCHES):
        node = Node(
            node_id=node_id, plan_version_id=version, node_type="proposed",
            display_label=label, parent_node_id=parent,
            root_anchor="root_documents", ordinal=ordinal,
            associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="personal_non_sensitive", origin_node_id=node_id)
        write_node(conn, node)
        nodes.append(node)
    freeze_version(conn, version)

    ids = {}
    decisions = []
    for index, (name, node_id) in enumerate(
            ((_CONTESTED, "n-course"), (_UNCONTESTED, "n-read"))):
        source = corpus / name
        stat = source.stat()
        file_id = record_file(
            conn, source, filename=name, normalized_filename=name.lower(),
            extension=".txt", observed_size=stat.st_size,
            observed_timestamps=str(stat.st_mtime),
            parent_folder_context=corpus.name, mime_type="text/plain",
            detected_format="txt", scan_state="included", materialized=True)
        ids[name] = file_id
        content_hash = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (file_id,)).fetchone()[0]
        ClassificationStore(conn).write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="personal_non_sensitive", protected=False,
            basis="user", evidence_refs=(), reliability_state="direct",
            observed_at="2026-09-20T00:00:00+00:00"))
        decisions.append(dataclasses.replace(
            EXACT_PLACEMENT, decision_id=f"decision-{index}",
            plan_version=version,
            destination=Destination(node_id=node_id, node_role=ORDINARY),
            subject=Subject(kind="file", file_id=file_id,
                            content_hash=content_hash, group_id=None,
                            member_file_ids=()),
            privacy=PrivacyState(handling_class="personal_non_sensitive",
                                 protected=False,
                                 model_eligibility="local_only",
                                 consent_audit_ref=None),
            review_policy=AUTO_ELIGIBLE))

    if contested:
        # THE WITHDRAWN ROW, STILL IN THE LIST. This is the second decision the
        # pass reached for one subject; `_current` would have dropped it and
        # `freeze` never asks for `_current`.
        decisions.append(dataclasses.replace(
            decisions[0], decision_id="decision-withdrawn",
            destination=Destination(node_id="n-read", node_role=ORDINARY)))

    counter = count()

    proposal = freeze(
        conn, tuple(decisions), nodes=tuple(nodes),
        legal_destination_ids=frozenset(node.node_id for node in nodes),
        cross_folder_moves=True,
        constraints=FilesystemConstraints(
            unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
            max_path_bytes=4096, prohibited_characters=frozenset(),
            reserved_names=frozenset(), replacement_character="_"),
        high_level_folders={"root_documents": corpus},
        volume_of=lambda path: "vol-main",
        protected_handling_classes=frozenset({"sensitive_personal"}),
        collision_policy=STOP_AND_ASK,
        expiration_state="no expiry configured",
        shown_file_ids=frozenset(ids.values()),
        approve_reviewed=lambda plan, at: None,
        component_version="conflict-test",
        now=lambda: "2026-09-20T01:00:00+00:00",
        mint_id=lambda: f"plan-{next(counter)}")
    conn.commit()
    conn.close()
    return {"corpus": corpus, "database": database, "ids": ids,
            "proposal": proposal, "version": version}


def _apply_everything(world) -> tuple[int, str]:
    """`--apply-everything` over that folder, in the words `_typed` prints."""
    out = io.StringIO()
    code = cli.main([str(world["corpus"]), "--database", str(world["database"]),
                     "--apply-everything"], out=out)
    return code, out.getvalue()


@pytest.fixture(scope="module")
def the_contested_file(tmp_path_factory):
    """The approved set that names one file twice, and what `--apply` does to it."""
    root = tmp_path_factory.mktemp("one_file_twice")
    world = _freeze_a_small_world(root, contested=True)
    before = _on_disk(world["corpus"])
    code, said = _apply_everything(world)
    return {**world, "before": before, "after": _on_disk(world["corpus"]),
            "code": code, "said": said}


@pytest.fixture(scope="module")
def the_uncontested_file(tmp_path_factory):
    """The same world with nothing in conflict: the moves must still happen."""
    root = tmp_path_factory.mktemp("one_file_once")
    world = _freeze_a_small_world(root, contested=False)
    before = _on_disk(world["corpus"])
    code, said = _apply_everything(world)
    return {**world, "before": before, "after": _on_disk(world["corpus"]),
            "code": code, "said": said}


def test_the_freeze_really_did_approve_one_file_for_two_folders(
        the_contested_file):
    """The premise, asserted before anything is asked of `--apply`.

    Without this the refusal below could be passing because the world is empty.
    Three plans over two files, and the contested one has two destinations that
    are not the same string.
    """
    state = the_contested_file
    plans = state["proposal"].plans
    assert len(plans) == 3, [plan.resolved_destination_path for plan in plans]
    contested = state["ids"][_CONTESTED]
    where = {plan.resolved_destination_path for plan in plans
             if plan.file_id == contested}
    assert len(where) == 2, where
    # And BOTH are in the approved set the apply run reads back, under one
    # version -- which is why the refusal below names one version and not two.
    assert {plan.organization_plan_version for plan in plans} == {
        state["version"]}


def test_apply_everything_refuses_an_approved_set_that_names_a_file_twice(
        the_contested_file):
    """`--apply-everything` over a self-contradicting plan: refuse, move nothing.

    The assertion that matters is the third: NOT ONE BYTE. An exit code on its
    own would pass for a run that moved four files and then failed, which is the
    outcome this exists to prevent.
    """
    state = the_contested_file
    assert state["code"] == 2, state["said"]
    assert state["after"] == state["before"], (
        "the folder changed although the run refused: "
        f"{set(state['after'].items()) ^ set(state['before'].items())}")
    assert _rows(state["database"], "move_journal") == 0, (
        "a move was journalled by a run that refused")
    assert _rows(state["database"], "execution_records") == 0


def test_the_refusal_names_the_file_and_both_folders_it_was_approved_for(
        the_contested_file):
    """`84` §6, and `84` §1's marked-and-counted rule.

    What is in conflict is named -- the file by the name its owner calls it, and
    BOTH destinations in full -- and no command is printed, because the command
    that would settle it does not exist: which plan governs is unruled. The
    no-frozen-plan block a few lines above in `cli.py` prints no command for the
    same reason and says so.
    """
    state = the_contested_file
    said = state["said"]
    assert _CONTESTED in said, said
    for plan in state["proposal"].plans:
        if plan.file_id == state["ids"][_CONTESTED]:
            assert plan.resolved_destination_path in said, (
                f"{plan.resolved_destination_path} was not on the screen")
    assert state["version"] in said, "the plan version was not named"
    # NOT ONE OF THE PRODUCT'S OWN COMMANDS, because none of them settles this.
    assert "database-agent " not in said, (
        "a command was printed for a question the product cannot answer yet")
    # And the file that was NOT in conflict is not reported as though it were.
    assert said.count(_UNCONTESTED) == 0, (
        "a file with one destination was named among the contested ones")


def test_the_conflict_never_blocks_taking_a_move_back(the_contested_file):
    """`--undo` is not about the frozen set, so the refusal must not reach it.

    THE TRAP THIS EXISTS TO CLOSE. The guard sits above the point where `--apply`
    and `--undo` part company, so the first version of it refused BOTH. A person
    whose files had already moved under an earlier approval and who then froze a
    contradictory one would have had the moves done and the one gesture that puts
    them back taken away -- a refusal doing more damage than the defect. `--undo`
    reads `applied_entries`, which is the journal of what actually happened, and
    a contradictory approved set says nothing about whether a move can be
    reversed.
    """
    state = the_contested_file
    out = io.StringIO()
    code = cli.main([str(state["corpus"]), "--database", str(state["database"]),
                     "--undo-everything"], out=out)
    said = out.getvalue()
    assert "two different folders" not in said, (
        "the apply-side refusal reached the undo path")
    assert code == 0, said


def test_the_same_world_with_nothing_in_conflict_still_moves_its_files(
        the_uncontested_file):
    """THE COMPANION THE REFUSAL MUST NOT SWALLOW.

    Two files, two branches, one approved set, nothing named twice -- which is
    the ordinary shape of every freeze -- and `--apply-everything` moves them.
    This world differs from the contested one in exactly one decision, so a
    guard that refused here would be refusing plurality rather than conflict.
    """
    state = the_uncontested_file
    assert state["code"] == 0, state["said"]
    moved = _files_on_disk(state["after"])
    assert _CONTESTED not in moved, "the file never left the folder root"
    assert f"Coursework/{_CONTESTED}" in moved, moved
    assert f"Reading Inbox/{_UNCONTESTED}" in moved, moved
    assert _rows(state["database"], "move_journal") == 2

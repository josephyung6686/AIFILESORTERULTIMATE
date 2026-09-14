# tests/integration/test_the_judge_names_the_situation.py
"""`00` amendment 1 of 14 Sep: the judge names the situation, not the person.

Run 12 printed nine branch questions offering 80 situation identifiers -- "Which
of these is Downloads?" over three career situations for a folder of 326 mixed
files -- and the owner read them: *"how am I even supposed to answer this? there
is no question and no answer. These cannot be the questions we ask the user."*
The ruling is that the judge names the situation itself, from the schema's own
list with each situation's name and one line of what it is, and the person is
asked only where the judge cannot.

**THE SECOND STAGE IS SITE G'S SECOND QUESTION**, asked in the same loop, on the
same turn, over the same released items as the call that named the file's kind.
These four pins are what that means in a run.

**THE DEPLOYMENT IS THE ONE THE OWNER CHOSE** (`00` amendment 3 of 14 Sep: *"I
feel like cloud only"*): a cloud key, no local model, and `readers.model_routing.
deepseek_invoke` replaced by a recorder -- the documented seam, so the gate, the
route, the transport, the validator and the whole of `cli.run` are the production
path. `test_the_question_at_the_end_and_the_sort` is the sibling this corpus and
this stub are modelled on, and the two files share their answer shapes rather
than describing two different models.

**THE CORPUS IS SIX FILES A PERSON COULD HAVE.** Two coursework files in the
folder root, three of a student society's records in a subfolder of their own,
and one the rules hold. `nonprofit` is the society's schema and is chosen by
MEASUREMENT: of the twenty-three the shipped library carries, it is the one with
exactly two situations beneath it and no recogniser raises either -- which is the
state the amendment is about, more than one and nothing to tell them apart.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cli  # noqa: E402
from facts.domains import DOMAIN_FIELDS  # noqa: E402
from llm_harness import prompt_library  # noqa: E402
from llm_harness.prompt_library import RATIFIED  # noqa: E402
from llm_harness.wire_handles import wire_handle  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from placement.vocabulary import PLACE  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from production import folder_levels_for, group_level_fields_for  # noqa: E402

from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _names, _released, _the_deterministic_winner,
)
from test_local_model_fact_pass import _answer_for  # noqa: E402
from test_site_g_end_to_end import _decline  # noqa: E402

#: What the person typed, and the thing that must keep overriding the judge.
SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The society's folder, and the one released value that differs per file at site
#: G -- so it is the only thing the stub may read to tell these files apart.
CLUB = "Debate Society"
SCHEMA = "nonprofit"
#: The two situations the library carries under it, and the one the judge names.
#: Deliberately the SECOND: an answer that agreed with `situations_of(schema)[0]`
#: would prove nothing about the alphabetical pick being gone.
CHOSEN = "nonprofit.member-association"

#: The word the stub declines the SITUATION question on, for pin (c). It is in one
#: club file's own text, so the decline is aimed the only way a stub can aim
#: anything at this site: by reading what was released.
DECLINE_ON = "annual general meeting"

#: The file the rules hold. `medical record` is a work type of `medical` in a
#: naming zone -- the filename and the first heading -- which is the one place a
#: single term still takes a hold since the corroboration rule of 13 Sep 2026.
HELD = "Medical record summary.txt"

ROOT_FILES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n",
    "ECON 2010 syllabus.txt":
        "ECON 2010 Syllabus\n\nFall 2025. Instructor: Dr. Ruiz. Credits: 4.\n",
    HELD:
        "Medical record\nNotes kept after the appointment last month.\n",
}

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

#: The one the stub declines for, by the word above.
DECLINED_FILE = "Annual meeting agenda.txt"

#: `academic`'s four level fields: what `--situation academic.coursework` asks a
#: coursework file, and the witness that the society's files are not asked the
#: run's own questions.
COURSEWORK_FIELDS = frozenset({"school", "subject", "term", "work_type"})

ENV = {
    CREDENTIAL_NAME: "sk-not-a-real-key",
    BASE_URL_NAME: "https://api.example",
    MODEL_NAME_OF_TIER["reasoning"]: "a-reasoner",
    MODEL_NAME_OF_TIER["logic"]: "a-logician",
    MODEL_NAME_OF_TIER["fast"]: "a-sprinter",
}


# --- the cloud, stubbed at the deployment seam ----------------------------------


def _is_the_situation_question(body: dict) -> bool:
    """Which of site G's two questions this dossier is.

    Read off the MENU and not off the prompt id, because the menu is what the two
    questions differ by: the kind call offers `candidate_schema` items, one per
    schema of the library, and the situation call offers `candidate_situation`
    items, one per situation of the kind a first judge named. A stub that keyed on
    anything else would still answer if the two calls ever stopped differing.
    """
    return any(item.get("kind") == "candidate_situation"
               for item in body.get("evidence_items", ()))


class _Cloud:
    """Every call this run put on the wire, and the dossier each one carried."""

    def __init__(self, *, decline_on: str | None = None) -> None:
        self.payloads: list[bytes] = []
        self.decline_on = decline_on

    @staticmethod
    def _body(payload: bytes) -> dict:
        return json.loads(
            payload.decode("utf-8").split("The dossier follows.", 1)[1])

    def dossiers_at(self, call_site: str) -> list[dict]:
        return [self._body(p) for p in self.payloads
                if self._body(p)["call_site"] == call_site]

    def kind_calls(self) -> list[dict]:
        return [body for body in self.dossiers_at(cli.G_SITUATION_SENSITIVITY)
                if not _is_the_situation_question(body)]

    def situation_calls(self) -> list[dict]:
        return [body for body in self.dossiers_at(cli.G_SITUATION_SENSITIVITY)
                if _is_the_situation_question(body)]

    def factory(self, **_unused):
        def invoke(payload: bytes) -> bytes:
            self.payloads.append(payload)
            body = self._body(payload)
            site = body["call_site"]
            if site == cli.G_SITUATION_SENSITIVITY:
                where = " ".join(item["value"] for item in _released(body))
                if not _is_the_situation_question(body):
                    return _names(SCHEMA if CLUB in where else "academic",
                                  body).encode("utf-8")
                if self.decline_on and self.decline_on in where:
                    return _decline(body).encode("utf-8")
                return _names(CHOSEN, body).encode("utf-8")
            if site == cli.C_PLACEMENT:
                return _the_deterministic_winner(body).encode("utf-8")
            return _answer_for(payload.decode("utf-8")).encode("utf-8")
        return invoke


# --- one corpus, one run ---------------------------------------------------------


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in ROOT_FILES.items():
        (corpus / name).write_text(body)
    (corpus / CLUB).mkdir()
    for name, body in CLUB_FILES.items():
        (corpus / CLUB / name).write_text(body)
    return corpus


#: The id and candidate of the row this test's own manifest carries, so the real
#: packet's word never speaks for it and this file can ratify a text the owner
#: has not. `tests/test_cli_a_fact_row.py::_pointed_at` is the pattern.
TEST_ROW = ("situation.unratified.situation-level-v1-pin.2026-09-14",
            "situation-level-v1-pin")


def _ratified(patch) -> None:
    """Point the second stage at a row that exists only in this test's manifest.

    The shipped row is `unratified` and stays that way until the owner has read
    the text and the lead has measured it. A pin for what the stage does when it
    is ratified cannot wait for that and must not change it, so the manifest is
    copied, one row naming the same three files is added under a NEW id with
    `status` ratified, and `cli.SITUATION_LEVEL_ROW` is pointed at it.

    `prompt_library._manifest` is `lru_cache`d and this replaces the function, so
    the cache is bypassed rather than poisoned; `digests` comes across with the
    copy, so the bytes are still verified against what the packet recorded.
    """
    manifest = {key: (list(value) if isinstance(value, list) else value)
                for key, value in prompt_library._manifest().items()}
    shipped = prompt_library.draft_row(cli.SITUATION_LEVEL_ROW[0])
    manifest["drafts"] = manifest["drafts"] + [
        {**shipped, "candidate": TEST_ROW[1], "template_id": TEST_ROW[0],
         "status": RATIFIED}]
    patch.setattr(prompt_library, "_manifest", lambda: manifest)
    patch.setattr(cli, "SITUATION_LEVEL_ROW", TEST_ROW)


def _run(tmp_path: Path, *, ratify: bool, decline_on: str | None = None,
         twice: bool = False) -> dict:
    """One cloud-only run over the corpus, with the cloud recorded.

    `twice` runs the same command again over the same database and reports the
    SECOND run, with its own recorder -- which is how the question "does this
    answer survive a run" is asked of the product rather than of a table.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    cloud = _Cloud(decline_on=decline_on)
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        # NO KEY AND NO LOCAL MODEL FROM THE MACHINE THIS RUNS ON. A developer
        # with a local model resident would otherwise get a different deployment
        # -- a gate that runs, a local target at every site -- and these pins
        # would be about their machine rather than about the product.
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
        for name, value in ENV.items():
            patch.setenv(name, value)
        patch.setattr(model_routing, "deepseek_invoke", cloud.factory)
        if ratify:
            _ratified(patch)
        argv = [str(corpus), "--situation", SITUATION, "--label", LABEL,
                "--user", "t", "--database", str(database), "--enable-cloud",
                "--accept-groups"]
        code = cli.main(argv, out=out)
        assert code == 0, out.getvalue()
        if twice:
            cloud = _Cloud(decline_on=decline_on)
            patch.setattr(model_routing, "deepseek_invoke", cloud.factory)
            out = io.StringIO()
            code = cli.main(argv, out=out)
    assert code == 0, out.getvalue()
    return {"corpus": corpus, "database": database, "cloud": cloud,
            "said": out.getvalue(),
            "plan": _plan_version_in(out.getvalue())}


def _plan_version_in(report: str) -> str:
    for line in report.splitlines():
        if line.startswith("Plan version: "):
            return line.split()[2]
    raise AssertionError("the run printed no plan version")


def _decisions(state) -> tuple[dict, dict]:
    """`(placed, abstained)` for this run's proposal, by corpus-relative name."""
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        named = {row["file_id"]: row["current_path"]
                 for row in conn.execute(
                     "SELECT file_id, current_path FROM files")}
        decisions = tuple(decisions_for_plan(conn, plan_version=state["plan"]))
    finally:
        conn.close()

    def where(decision) -> str:
        return str(Path(named[decision.subject.file_id])
                   .relative_to(state["corpus"]))

    placed = {where(d) for d in decisions
              if d.subject.kind == "file" and d.outcome == PLACE}
    abstained = {where(d): d.abstention_reason for d in decisions
                 if d.subject.kind == "file" and d.outcome != PLACE}
    return placed, abstained


def _fields_asked(database: Path) -> dict[str, set[str]]:
    """filename -> every field any A_fact call MADE about it offered.

    Through THIS DATABASE'S WIRE HANDLE KEY: `llm_dossier.subject_ref` is
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


def _situation_verdicts(database: Path) -> int:
    """How many responses this database holds for the SITUATION question.

    Read off the dossier payload, which is the bytes the model was shown, so a
    call that was made and whose answer was thrown away is still counted -- which
    is the whole of what "recorded and not acted on" means.
    """
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return sum(
            1 for row in conn.execute(
                "SELECT d.payload FROM llm_dossier d "
                "JOIN llm_response r ON r.dossier_id = d.dossier_id "
                "WHERE d.call_site = ?", (cli.G_SITUATION_SENSITIVITY,))
            if _is_the_situation_question(json.loads(row["payload"])))
    finally:
        conn.close()


@pytest.fixture(scope="module")
def observing(tmp_path_factory):
    """The run as it ships today: the second stage's row is unratified."""
    return _run(tmp_path_factory.mktemp("observing"), ratify=False)


@pytest.fixture(scope="module")
def deciding(tmp_path_factory):
    """The same run with the row ratified in this test's own manifest."""
    return _run(tmp_path_factory.mktemp("deciding"), ratify=True)


@pytest.fixture(scope="module")
def declining(tmp_path_factory):
    """Ratified, and the judge declines for one file of the society's branch."""
    return _run(tmp_path_factory.mktemp("declining"), ratify=True,
                decline_on=DECLINE_ON)


# --- (a) under the unratified row: asked, recorded, and nothing changes ----------


def test_the_judge_is_asked_which_situation_and_the_menu_is_the_kinds_own(
        deciding):
    """The second question is put for exactly the files the person would have
    been asked about, with the library's own words on the menu.

    Three club files, three kind calls naming `nonprofit`, three situation calls.
    The coursework files get none: the person typed `academic.coursework`, so
    `_the_situation_already_settled` answers for that kind and a call whose answer
    is outranked before it is made is never made.

    THE MENU IS THE KIND'S SITUATIONS AND EACH CARRIES ITS OWN LINE, which is the
    amendment's own sentence -- "with each situation's name and one line of what
    it is" -- and the whole of what makes this a question rather than the
    identifier quiz the owner struck out.

    SABOTAGE: drop `described_of` at the call site and the menu is bare
    identifiers again; drop `settled_situation_of` and the coursework files are
    asked too.
    """
    situation_calls = deciding["cloud"].situation_calls()
    assert len(situation_calls) == len(CLUB_FILES), [
        body["subject_ref"] for body in situation_calls]
    kinds = deciding["cloud"].kind_calls()
    named = len(ROOT_FILES) - 1 + len(CLUB_FILES)
    assert len(kinds) == named, len(kinds)
    # THE SCREEN'S OWN ARITHMETIC, which is where the reason is legible. Five
    # files had their kind named; three were asked which situation of that kind;
    # two were not, and those two are the coursework files the person typed the
    # situation for.
    block = " ".join(deciding["said"].split())
    # On the ratified row the society's three are given their situation by the
    # judge and none stays open (the lead, 14 Sep 2026: the stage is dark under an
    # unratified row, so this reads the ratified fixture).
    assert f"Which situation, of the kind: {len(CLUB_FILES)} of {named} files" in block, block
    assert "0 asked and still open" in block, block
    assert f"{named - len(CLUB_FILES)} not asked" in block, block
    for body in situation_calls:
        offered = [item for item in body["evidence_items"]
                   if item["kind"] == "candidate_situation"]
        assert {item["evidence_ref"] for item in offered} == {
            SCHEMA, CHOSEN, cli.NONE_OF_THESE}, offered
        assert body["allowed_vocabulary"][-1] == cli.NONE_OF_THESE
        for item in offered:
            if item["evidence_ref"] == CHOSEN:
                # The library's own name, then its own line of what it is.
                assert "Membership roll" in item["location"], item["location"]
                assert "WHO BELONGS TO IT" in item["location"], item["location"]
        (kind,) = [item for item in body["evidence_items"]
                   if item["kind"] == "named_kind"]
        assert SCHEMA in kind["location"], kind["location"]


def test_the_answer_is_recorded_and_the_run_is_the_run_it_was(observing):
    """`104` §7 Phase 1 step 6: under an unratified text the verdict is stored and
    nothing is applied.

    All three halves are asserted, because "recorded and changes nothing" is three
    claims: the responses exist; the branch question still prints with both of the
    library's options typable; and the society's files are still filed nowhere.

    SABOTAGE: read `situation_named_by_verdict` without asking `prompt.ratified`
    and the question below disappears from a screen the owner never approved the
    text for.
    """
    # THE STAGE IS DARK UNDER AN UNRATIFIED ROW (the lead, 14 Sep 2026): no level
    # dossier, no call -- an unratified text never crosses the internet under
    # another row's word. The text is measured by the lead's replay over
    # already-released dossiers, and the owner ratifies before the stage runs.
    assert _situation_verdicts(observing["database"]) == 0
    said = observing["said"]
    assert f"Which of these is {SCHEMA}?" in said, said
    for option in (SCHEMA, CHOSEN):
        assert f"--answer situation:{SCHEMA}={option}" in said, said
    placed, abstained = _decisions(observing)
    for name in CLUB_FILES:
        where = f"{CLUB}/{name}"
        assert where not in placed, where
        assert abstained[where], where


# --- (b) with the row ratified: the judge's situation resolves the file ----------


def test_the_judges_situation_resolves_the_file_and_the_question_is_not_asked(
        deciding):
    """The amendment, working: the judge names the situation and the person is
    not asked about that branch at all.

    SABOTAGE: drop `_the_situation_the_judge_named` from `_the_situation_this_
    file_is_under`, or the `_settled_by_the_judge` arm from `partition_by_branch`,
    and the question comes back.
    """
    said = deciding["said"]
    assert f"Which of these is {SCHEMA}?" not in said, said
    assert f"--answer situation:{SCHEMA}=" not in said, said
    # And the person's own answer is still the person's: the run's typed
    # situation was never put to the judge and never questioned.
    assert "Which of these is academic?" not in said, said


def _the_situations_own_levels() -> set[str]:
    """The fields `nonprofit.member-association`'s own folders are built from.

    Asked of the library rather than written here, because it is the library's
    answer and a copy would go stale the day a row is re-authored. It is the same
    join `cli` makes when it builds a resolver for a settled branch: the
    situation's folder levels, less the ones the GROUP carries.
    """
    catalogue = cli.load_shipped_catalogue(cli.read_packaged_library_file)
    group_levels = group_level_fields_for(catalogue, CHOSEN)
    return {level.field for level in folder_levels_for(catalogue, CHOSEN)
            if level.field not in group_levels}


def test_those_files_are_asked_their_situations_fields_and_are_placed(
        deciding, observing):
    """The two halves the amendment's own sentence asks for -- the fact pass asks
    the file its SITUATION's fields, and placement proceeds.

    **THE CONTRAST IS THE MEASUREMENT AND ONE RUN ALONE WOULD NOT BE.** A file
    whose situation is open is asked its SCHEMA's whole field set with no folder
    levels at all (`no_levels_by_schema`, built for exactly that state), and a
    file whose situation is settled is asked that situation's own levels -- which
    for the society's records is the period their record covers. So the same
    three files are read out of both runs: four fields and no folders under the
    unratified row, the situation's own level under the ratified one.

    The destination is the person's own folder, which is `00` §user-selection
    rather than a shortfall: the society's records carry no fact that fills that
    level, so the best-supported node on the shortlist is the folder they are
    already in and nothing moves.

    SABOTAGE: leave `by_situation` without a row for a judge-named situation and
    `resolver_for` raises; leave the branch unsettled and P11 abstains for all
    three.
    """
    levels = _the_situations_own_levels()
    assert levels, "the library carries no folder level for this situation"
    open_situation = _fields_asked(observing["database"])
    settled = _fields_asked(deciding["database"])
    for name in CLUB_FILES:
        # The situation was open: the schema's own questions, no folder levels.
        assert open_situation.get(name, set()) >= set(DOMAIN_FIELDS[SCHEMA]), (
            name, sorted(open_situation.get(name, ())))
        # The judge settled it: the situation's own level, and not the run's four.
        offered = settled.get(name, set())
        assert offered == levels, (name, sorted(offered), sorted(levels))
        assert not offered & COURSEWORK_FIELDS, (name, sorted(offered))
    # The control: a file under the situation the person typed IS asked those
    # four on both runs, so the lines above are measuring the society's situation
    # and not an allowlist that emptied for everybody.
    for state in (open_situation, settled):
        assert state["PHYS 1401 syllabus.txt"] >= COURSEWORK_FIELDS, state
    placed, abstained = _decisions(deciding)
    for name in CLUB_FILES:
        where = f"{CLUB}/{name}"
        assert where in placed, abstained.get(where)


# --- (c) a file the judge declines still goes to the person ---------------------


def test_a_branch_the_judge_could_not_finish_is_still_the_persons_question(
        declining):
    """*"The person is asked only where the judge cannot."* One file of the three
    the judge declines is one file whose situation the person still has to settle,
    and the question they are asked is the BRANCH's -- so the branch stays
    unsettled and the question prints.

    UNANIMOUS OVER EVERY FILE AND NOT OVER EVERY ANSWERED FILE, which is the
    whole of `_settled_by_the_judge`: settling this branch on the two the judge
    did answer would file the third under a situation nothing said it was.

    SABOTAGE: change `_settled_by_the_judge` to ignore the files it has no answer
    for and this question disappears while a file it is about stays unresolved.
    """
    said = declining["said"]
    assert f"Which of these is {SCHEMA}?" in said, said
    # The judge was asked about all three and answered two of them: the decline
    # is a decline, not a call that never happened.
    assert len(declining["cloud"].situation_calls()) == len(CLUB_FILES)
    placed, abstained = _decisions(declining)
    assert f"{CLUB}/{DECLINED_FILE}" not in placed


# --- (d) the same released items, and never the held file -----------------------


def test_the_two_questions_show_the_model_the_same_reading_of_one_file(
        deciding):
    """The second dossier's released items are the first's, byte for byte.

    `ask_the_situation` hands the second call the observations the first was
    built from rather than asking `releasable_observations` again, so the two
    questions about one file show the model one reading of it. A second read
    would be a second answer to what P7 released, and the two would part the day
    a bound moved between them.

    SABOTAGE: rebuild the offer inside `_ask_which_situation_of_the_kind` and
    this goes red the moment the two reads disagree about anything -- an order, a
    span, a ceiling.
    """
    by_subject: dict[str, list[dict]] = {}
    for body in deciding["cloud"].kind_calls():
        by_subject.setdefault(body["subject_ref"], []).append(body)
    asked_twice = 0
    for body in deciding["cloud"].situation_calls():
        (kind,) = by_subject[body["subject_ref"]]
        assert body["released_evidence"] == kind["released_evidence"], (
            body["subject_ref"])
        assert body["reduction_rung"] == kind["reduction_rung"]
        assert body["max_dossier_tokens"] == kind["max_dossier_tokens"]
        asked_twice += 1
    assert asked_twice == len(CLUB_FILES)


def test_the_held_file_is_never_the_subject_of_either_question(observing):
    """A protected record is filed by the person (13 Sep 2026), so it is not put
    to either judge -- and the second stage is reached only from inside the first,
    after the hold has already turned the file away.

    SABOTAGE: move the second stage out of `ask_the_situation`'s loop into a pass
    of its own over the roster and this is the first thing that breaks.
    """
    key = cli.wire_handle_key_for(observing["database"])
    conn = sqlite3.connect(f"file:{observing['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        (held_id,) = [row["file_id"] for row in conn.execute(
            "SELECT file_id, filename FROM files") if row["filename"] == HELD]
    finally:
        conn.close()
    handle = wire_handle(held_id, key=key)
    subjects = [body["subject_ref"] for body
                in observing["cloud"].dossiers_at(cli.G_SITUATION_SENSITIVITY)]
    assert subjects, "site G was never asked about anything"
    assert handle not in subjects, HELD


# --- the answer survives the run it was given in --------------------------------


@pytest.fixture(scope="module")
def again(tmp_path_factory):
    """The ratified run, then the same command again over the same database."""
    return _run(tmp_path_factory.mktemp("again"), ratify=True, twice=True)


def test_the_situation_survives_the_run_without_a_second_call_or_a_table(again):
    """WHERE THE ANSWER IS KEPT, asked of the product.

    The judge's situation is held in `SituationPass.situations`, beside the kind
    in `named`, and it is written to no classification row and no table of its
    own. A classification row says which CLASS of material a file is -- it
    carries `protected`, a privacy class and the gate's own bases -- and a
    situation is not one: it decides the file's fields and its folders and
    decides nothing about what may leave this device. Putting it there would add
    a second, finer vocabulary to the one column every privacy reader tests.

    What carries it across a run is what carries the KIND across one: the verdict
    the call recorded, replayed by `104` §18.31's reuse against the same file,
    reader, prompt, model and list of situations. So the second run over this
    database spends NO call at site G -- neither question -- and still does not
    ask the person about the society's folder.

    SABOTAGE: leave the situation list out of `_per_file_call_identity`'s
    `schema_ids` and the two questions collide on one identity; write the answer
    to a classification row instead and this pin still passes while the privacy
    column gains 208 new values.
    """
    assert again["cloud"].kind_calls() == []
    assert again["cloud"].situation_calls() == []
    assert f"Which of these is {SCHEMA}?" not in again["said"], again["said"]
    placed, abstained = _decisions(again)
    for name in CLUB_FILES:
        assert f"{CLUB}/{name}" in placed, abstained.get(f"{CLUB}/{name}")

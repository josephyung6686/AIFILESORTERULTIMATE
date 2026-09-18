# tests/integration/test_each_file_is_filed_under_its_own_situation.py
"""`00` amendment 7 driven END TO END through `cli.main`, on one placing run.

`104` §18.58 left exactly this open: *"the end-to-end hand-off (second partition
-> placement inputs -> filter) has no single pin, because no harness drives a
placing corpus through a stub local model"*. The unit pins exist -- `branch_
situation.named_by_the_model` opens a branch, `cli._the_situation_its_folders_
are_chosen_under` fills `PipelineInputs.situation_of`, `placement.pipeline.
_only_this_files_own_branch` drops a candidate under another situation's root --
and each is pinned where it lives. This is the run that makes the four one act:
site G names a situation PER FILE, the fact pass asks that file's own fields, the
partition is made AGAIN with G's names in it, the tree grows a root for a branch
no anchor could have opened, and P11 refuses a course to the file that is not in
one. Everything asserted below is read off the plan database after the run.

**THE SHARPEST LINE IS `PHYS 1401 poster.txt`.** It carries the same course code,
the same term and the same instructor as the four coursework files that DO go
into `Coursework/Spring2026/PHYS1401`; the only thing that differs is that site G
named it `research`. Measured with `_only_this_files_own_branch` replaced by the
identity, it is filed into `Coursework/Spring2026/PHYS1401/exam` -- §18.58 gap 3's
own sentence, "a research paper in a coursework run was filed into a course" --
and with the rule in force its five coursework candidates are dropped (5 -> 1) and
it stays in the person's own conference folder. That is the SABOTAGE for this
file: the rule earns its place on this corpus rather than being inert on it.

**NO OLLAMA AND NO NETWORK.** The stub HTTP server is `test_local_model_fact_
pass`'s, imported rather than copied, and the answer function reads each dossier's
own `call_site`: the gate (H) clears, as in `test_site_h_gate`; the situation (G)
names `research` for the conference folder and DECLINES everywhere else, which are
the two shapes `test_site_g_end_to_end` pins; site A answers by copying, which is
`_answer_for`; and site C names the deterministic winner.

**WHY SITE C HAS AN ANSWER HERE AT ALL, and it is not decoration.** `cli.prompt_
for(C_PLACEMENT).ratified` is `True` at this head, so `PipelineInputs.model_
decides()` is true the moment a local model is configured and §13.5's ruling
applies: every placeable file goes to site C and the verdict decides. A stub that
left C to `_answer_for` was measured on this corpus placing NOTHING -- every file
abstaining -- because a field-shaped answer is not a placement answer. So the
C answer is the shape `tests/integration/test_p11_pipeline_live._places_at`
builds, written out here rather than imported: that module imports `p11.conftest`,
which is not on this package's path.

**WHY SITE G CAN TELL ONE FILE FROM ANOTHER, and only this way.** Measured on this
corpus, a site-G dossier for a short text file releases three items: the folder
path, the mime type and the extension. `filename` is never released to any model
(`model_facts.releasable_observations`), and a file whose rules settle nothing has
no reading to release either -- so the ONLY thing that differs per file at this
site is which folder it is in. The three research files therefore sit in one, and
the stub reads the path. A stub keyed on anything else would be answering from
bytes the model was not shown.

**OBSERVED AND DELIBERATELY NOT ASSERTED.** `cli`'s `branch_votes` runs over the
FIRST partition, where all twenty files are under the default branch and only the
three the model named have a name at all -- so the default branch's vote is
`research` 3-0 and every coursework file is offered `venue`/`project`/
`artifact_type` at site A. Nothing here depends on that: the stub's site-A answers
are proposals that file nothing, and the situation each file's FOLDERS are chosen
under is a different question (`_the_situation_its_folders_are_chosen_under`),
which is what the placements below read. It is written down because a reader of
this run's call log will see it and should not have to rediscover it.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pytest

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. Done here rather than in a `conftest.py` for the reason
# `tests/tools/test_groundtruth_end_to_end.py` records at length: with no
# `__init__.py` in the tests tree every conftest is imported as `conftest`, and
# the last one collected wins.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402
from facts.domains import DOMAIN_FIELDS  # noqa: E402
from placement.vocabulary import PLACE, SITUATION_UNANSWERED  # noqa: E402
from privacy.vocabulary import LOCAL_MODEL_SITUATION  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from tree_design.store import nodes_for_version  # noqa: E402

from test_local_model_fact_pass import (  # noqa: E402
    MODEL_ID, StubOllama, _answer_for, dossier_in,
)
from test_r37_per_branch_situation import TWO_LIVES, _call_log  # noqa: E402
from test_site_g_end_to_end import _decline  # noqa: E402
from test_site_h_gate import _clear  # noqa: E402

from tools.groundtruth.labels import load_labels  # noqa: E402
from tools.groundtruth.measure import observe_run  # noqa: E402
from tools.groundtruth.score import score_situation  # noqa: E402

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The schema site G names for the conference folder's files, and the situation
#: `branch_situation.partition_by_branch` settles that branch on -- the library's
#: first for the schema, which is the same resolution `cli._situation_of` makes.
RESEARCH_SCHEMA = "research"
RESEARCH_SITUATION = "research.conference-presentation"

#: The person's own folder. Its name is the marker the stub reads, because the
#: folder path is the one released item that differs per file at site G.
CONFERENCE = "NeurIPS 2026"


def _root_name(schema_id: str) -> str:
    """What a branch opened for this schema is CALLED on the tree.

    **THE OWNER'S RULING OF 18 Sep 2026**: *"the names and folder and stuff all
    human readable and not machine readable."* A branch site G opens used to be
    labelled with the raw schema id, so the person's disk grew folders called
    `career` and `research`. It now wears the name the recognition rules author
    for that schema, and the SCOPE is untouched -- `--answer situation:career=`
    is unchanged, because the label is the key and `display_name` is the folder.

    ASKED OF THE LIBRARY rather than spelled here, so a re-authored name does not
    quietly turn this file red.
    """
    rules = cli.load_rules(cli._RECOGNITION_MANIFEST.read_text)
    schema = rules.schemas.get(schema_id)
    return cli.folder_name_for_schema(getattr(schema, "name", None), schema_id)

#: Three files in it. Two state nothing a coursework rule reads, and are what
#: gives the branch a group to be built from; the third states its course beside
#: `Instructor`, which is one of §3.5's context terms, so the deterministic pass
#: settles `subject = PHYS1401` on it and it retrieves the coursework tree.
RESEARCH_FILES = {
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

#: The course-coded one, named once so the assertions about it cannot drift from
#: the corpus.
THE_POSTER = f"{CONFERENCE}/PHYS 1401 poster.txt"

#: What the coursework branch files, unchanged from
#: `test_r37_per_branch_situation.COURSEWORK_CHAINS_BEFORE`. It is repeated rather
#: than imported: that constant is a measurement of a run with no model in it, and
#: this is a measurement of a run with one. They agree today, and the day they
#: stop agreeing the two pins must be able to say so separately.
COURSEWORK_CHAINS = {
    "Coursework/Spring2026/PHYS1401/syllabus": 1,
    "Coursework/Spring2026/PHYS1401/lecture": 1,
    "Coursework/Spring2026/PHYS1401/homework": 1,
    "Coursework/Spring2026/PHYS1401/exam": 1,
    "Coursework/Fall2025/ECON2010/syllabus": 1,
    "Coursework/Fall2025/ECON2010/lecture": 1,
    "Coursework/Fall2025/ECON2010/homework": 1,
    "Coursework/Fall2025/ECON2010/exam": 1,
    "Coursework/Fall2025/MATH2000": 3,
}


# --- the model, answering each of its four sites --------------------------------


def _released(dossier: dict) -> list[dict]:
    return [item for item in dossier.get("released_evidence", ())
            if isinstance(item, dict) and isinstance(item.get("value"), str)
            and item["value"].strip()]


def _names(schema: str, dossier: dict) -> str:
    """Site G's answer naming one schema, cited out of the dossier's own text.

    The citation is COPIED, for `test_site_g_end_to_end`'s reason: `validation.
    check_citations` requires the reference to be a released item of this dossier
    and the span to appear in the value the model was shown, so an invented answer
    would measure the validator instead of the wiring.
    """
    released = _released(dossier)
    if not released:
        return _decline(dossier)
    item = released[0]
    return json.dumps({"claims": [{
        "payload": {"situation": schema, "alternatives": []},
        "citations": [{"evidence_ref": item["observation_key"],
                       "cited_span": item["value"].strip().splitlines()[0],
                       "why_it_supports": "this folder is what the file is part of"}],
    }]})


def _situation_answer(dossier: dict) -> str:
    """`research` for the conference folder, a decline for everything else."""
    where = " ".join(item["value"] for item in _released(dossier))
    if CONFERENCE in where:
        return _names(RESEARCH_SCHEMA, dossier)
    return _decline(dossier)


def _the_deterministic_winner(dossier: dict) -> str:
    """Site C's answer: the top of the shortlist P11 ranked, with its reasons.

    Every value is read out of the dossier -- the destination from
    `allowed_vocabulary`, the citation from what P7 released, the conflict ids
    from the conflicts the dossier carries -- because the shortlist, the wire
    handles and the conflict ids are all minted by the run and knowable no other
    way. Choosing `[0]` is the model agreeing with §6.10's arithmetic, which is
    what makes the placements below the rules' own and the ONE thing that differs
    between two files the situation.
    """
    ranked = dossier.get("allowed_vocabulary") or ()
    released = _released(dossier)
    if not ranked or not released:
        return json.dumps({"claims": [{
            "payload": {"destination": "none", "conflicts_considered": []},
            "unknown": {"insufficiency_statement":
                        "the shortlist or the evidence is empty"}}]})
    item = released[0]
    return json.dumps({"claims": [{
        "payload": {
            "destination": ranked[0],
            "per_dimension_support": [{"dimension": "subject",
                                       "value": item["value"],
                                       "support": "direct"}],
            "alternatives": [],
            "conflicts_considered": [conflict["conflict_id"]
                                     for conflict in dossier.get("conflicts", ())],
            "support": 1, "next_support": 0, "refinement": "not_applicable"},
        "citations": [{"evidence_ref": item["observation_key"],
                       "cited_span": item["value"],
                       "why_it_supports": "the file states this"}],
    }]})


def _answer(payload: str) -> str:
    dossier = dossier_in(payload)
    site = dossier.get("call_site")
    if site == cli.H_RESTRICTED_KIND:
        return _clear(dossier)
    if site == cli.G_SITUATION_SENSITIVITY:
        return _situation_answer(dossier)
    if site == cli.C_PLACEMENT:
        return _the_deterministic_winner(dossier)
    return _answer_for(payload)


# --- one run, read four ways ----------------------------------------------------


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    (corpus / CONFERENCE).mkdir()
    for name, body in RESEARCH_FILES.items():
        (corpus / CONFERENCE / name).write_text(body)
    return corpus


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    """One `cli.main` over the corpus, with the stub answering all four sites."""
    root = tmp_path_factory.mktemp("handoff")
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch, StubOllama(answer=_answer) as stub:
        patch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        patch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(database),
                         "--accept-groups"], out=out)
    assert code == 0, out.getvalue()
    return corpus, database, out.getvalue()


def _plan(database: Path):
    """The last plan version's nodes and decisions, plus the file names."""
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        plan_version = conn.execute(
            "SELECT plan_version FROM placement_decisions "
            "ORDER BY rowid DESC LIMIT 1").fetchone()[0]
        nodes = {node.node_id: node
                 for node in nodes_for_version(conn, plan_version)}
        names = {row["file_id"]: row["current_path"]
                 for row in conn.execute(
                     "SELECT file_id, current_path FROM files")}
        return nodes, tuple(decisions_for_plan(
            conn, plan_version=plan_version)), names
    finally:
        conn.close()


def _chain(node_id: str, nodes) -> str:
    parts: list[str] = []
    while node_id in nodes:
        parts.append(nodes[node_id].display_label)
        node_id = nodes[node_id].parent_node_id
    return "/".join(reversed(parts))


def _placed(run) -> dict[str, str]:
    """corpus-relative path -> destination chain, for every file this run placed."""
    corpus, database, _report = run
    nodes, decisions, names = _plan(database)
    return {str(Path(names[decision.subject.file_id]).relative_to(corpus)):
            _chain(decision.destination.node_id, nodes)
            for decision in decisions
            if decision.subject.kind == "file" and decision.outcome == PLACE}


def _abstentions(run) -> dict[str, str | None]:
    corpus, database, _report = run
    _nodes, decisions, names = _plan(database)
    return {str(Path(names[decision.subject.file_id]).relative_to(corpus)):
            decision.abstention_reason
            for decision in decisions
            if decision.subject.kind == "file" and decision.outcome != PLACE}


# --- (1) the second partition reached the tree ----------------------------------


def test_the_tree_grows_a_root_for_a_branch_only_site_g_could_open(run):
    """`branch_situation.named_by_the_model`, as a row in `tree_nodes`.

    A branch is opened by an ANCHOR -- a validated `work_type` whose term exactly
    one schema authored -- and `research` owns no such term in this corpus: the
    three files in the conference folder carry `poster`, `abstract` and `speaker
    notes`, none of which is a single-owner kind word. So a `research` root can
    only be here because the partition was made a SECOND time, after site G spoke,
    which is the hand-off this file exists for.

    Beside it stand the branch the person typed, the branch the career anchors
    opened, and the folder the person already had.
    """
    _corpus, database, _report = run
    nodes, _decisions, _names = _plan(database)
    roots = sorted(node.display_label for node in nodes.values()
                   if node.parent_node_id is None)
    assert roots == sorted([LABEL, _root_name("career"),
                            _root_name(RESEARCH_SCHEMA), CONFERENCE]), roots


def test_site_g_named_exactly_the_conference_folder_and_nothing_else(run):
    """The classification store, which is what the second partition reads.

    Three rows and three files: a model verdict about a file's situation writes a
    `local_model_situation` row (`104` §17.1's second wall), and a decline writes
    nothing at all. If a fourth file had a row the run would be one this pin's
    story does not describe.
    """
    corpus, database, _report = run
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        named = {str(Path(row["current_path"]).relative_to(corpus))
                 for row in conn.execute(
                     "SELECT f.current_path FROM classifications c "
                     "JOIN files f ON f.file_id = c.file_id WHERE c.basis = ?",
                     (LOCAL_MODEL_SITUATION,))}
    finally:
        conn.close()
    assert named == {f"{CONFERENCE}/{name}" for name in RESEARCH_FILES}


# --- (2) the decisions, which is what a person actually gets --------------------


def test_the_coursework_branch_files_its_courses_and_terms_as_before(run):
    """The run PLACES, and it places what a run with no model in it places.

    Asserted first because every claim below it is vacuous on a run that placed
    nothing -- which is the state this corpus was measured in before site C had an
    answer, and is one `assert placed` away from being invisible.
    """
    placed = _placed(run)
    assert placed, _abstentions(run)
    coursework = Counter(chain for chain in placed.values()
                         if chain.startswith(LABEL))
    assert dict(coursework) == COURSEWORK_CHAINS, placed


def test_no_placed_file_sits_under_a_root_carrying_another_situation(run):
    """`_only_this_files_own_branch`'s own guarantee, over the whole run.

    Not "every file is under its own situation's branch", which is not what the
    rule promises and is false here for a good reason: `career`'s situation is
    unsettled -- the library carries three and the person has answered none -- and
    a branch that names no situation takes nothing away from a file, exactly as
    the person's own `NeurIPS 2026` folder does not.

    So the claim is the rule's: a file is never under a root whose branch carries a
    situation that is not the file's own.
    """
    placed = _placed(run)
    #: The situation each root carries. `Coursework` is the person's typed answer;
    #: `research` is the one G's name settled the branch on; `career` is unsettled
    #: and `NeurIPS 2026` is not a branch at all, so neither names one.
    of_the_root = {LABEL: SITUATION,
                   _root_name(RESEARCH_SCHEMA): RESEARCH_SITUATION,
                   _root_name("career"): None, CONFERENCE: None}
    for path, chain in placed.items():
        own = (RESEARCH_SITUATION if path.startswith(f"{CONFERENCE}/")
               else SITUATION)
        root = chain.split("/", 1)[0]
        assert of_the_root[root] in (None, own), (path, chain, own)


def test_the_poster_shares_its_course_with_four_placed_files_and_not_their_folder(
        run):
    """§18.58 gap 3's own example, and the one file the rule is measured on.

    `PHYS 1401 poster.txt` states the course, the term and the instructor the four
    PHYS files state, and those four are filed under `Coursework/Spring2026/
    PHYS1401`. The poster is not, because site G named it `research` and step 6
    dropped every candidate under the coursework root: measured on this corpus,
    five candidates in and one out.

    SABOTAGE: replace `placement.pipeline._only_this_files_own_branch` with the
    identity and this file is placed in `Coursework/Spring2026/PHYS1401/exam` --
    the whole corpus otherwise unchanged, which is what makes the situation and
    not the evidence the thing that moved it.

    **AND SINCE `the_one_situation` IT IS NOT FILED AT ALL, which is the same
    finding one step further.** Site G named `research`; the shipped library
    carries EIGHT situations under `research` and the recognisers raised none of
    them for this file, so which of the eight it is has not been answered by
    anybody. It used to be answered by `situations_of("research")[0]` --
    `research.conference-presentation`, alphabetically first -- and this file
    then landed in the person's own `NeurIPS 2026` folder on that pick. Now its
    situation is unresolved, P11 abstains `situation_unanswered` for it, and the
    person is asked which of the eight `research` is. The claim this test makes
    is unchanged in the half that matters: the poster does NOT go into the course
    its four siblings go into.
    """
    placed = _placed(run)
    abstained = _abstentions(run)
    assert THE_POSTER not in placed, placed[THE_POSTER]
    assert abstained[THE_POSTER] == SITUATION_UNANSWERED, abstained[THE_POSTER]
    # The control: the same course, the same term, the same instructor line, and
    # no site-G name -- so the coursework folder is exactly where it goes.
    assert placed["PHYS 1401 syllabus.txt"].startswith(
        f"{LABEL}/Spring2026/PHYS1401")
    # And neither of the other two conference files reached a course either: G
    # named them `research` too, so all three are in the same unresolved state.
    for name in RESEARCH_FILES:
        path = f"{CONFERENCE}/{name}"
        assert path not in placed, placed[path]
        assert abstained[path] == SITUATION_UNANSWERED, abstained[path]


def test_a_judge_named_file_with_no_situation_is_still_asked_its_schemas_fields(
        run):
    """THE HALF THAT IS NOT WITHHELD, counted off the run's own A_fact calls.

    An unresolved SITUATION withholds the folder levels and the template. It does
    NOT withhold the question: `facts.domains.DOMAIN_FIELDS["research"]` is the
    schema's, site G named that schema for these three files, and the schema is
    what the field allowlist is computed from. The first cut of this change
    withheld the fields as well and the measurement was immediate -- every file
    the judge had read correctly came out of the pass with an empty facts column,
    which is the complaint that reopened it.

    So: a call PER named file, carrying that schema's own fields (`stage` among
    them, which no `research.conference-presentation` level binds and which the
    situation-narrowed question therefore never offered), and not one of them
    placed. `model_facts.open_question`'s `None` arm is where the two part.
    """
    _corpus, database, _report = run
    log = _call_log(database)
    placed = _placed(run)
    for name in RESEARCH_FILES:
        path = f"{CONFERENCE}/{name}"
        offered = frozenset().union(*log.get(name, [frozenset()]))
        assert len(log.get(name, ())) >= 1, (name, sorted(log))
        assert offered >= set(DOMAIN_FIELDS["research"]), (name, offered)
        assert "stage" in offered, (name, offered)
        assert path not in placed, placed[path]


# --- (3) the scoreboard, over this one run against every label ------------------


def _labels(root: Path):
    """One label per file in the corpus, keyed by corpus-relative path.

    EVERY file, because `score_situation` only looks at paths it has a label for
    and an unlabelled misplacement would be invisible to it. Destinations are
    given only where this run's `--label` folder is where the file belongs; a
    career file and a conference file belong outside it, and a label's destination
    is read as a path BELOW the top-level folder, so `null` with a reason is the
    honest row rather than a chain that means something else.
    """
    def coursework(term, course, kind):
        return {"situation": SITUATION, "destination": [term, course, kind]}

    outside = {"destination": None,
               "uncertain": "this run's --label folder is not where it belongs"}
    rows = {
        "PHYS 1401 syllabus.txt": coursework("Spring2026", "PHYS1401", "syllabus"),
        "PHYS 1401 lecture 08.txt": coursework("Spring2026", "PHYS1401", "lecture"),
        "PHYS 1401 homework 3.txt": coursework("Spring2026", "PHYS1401", "homework"),
        "PHYS 1401 midterm exam.txt": coursework("Spring2026", "PHYS1401", "exam"),
        "ECON 2010 syllabus.txt": coursework("Fall2025", "ECON2010", "syllabus"),
        "ECON 2010 lecture 02.txt": coursework("Fall2025", "ECON2010", "lecture"),
        "ECON 2010 homework 1.txt": coursework("Fall2025", "ECON2010", "homework"),
        "ECON 2010 final exam.txt": coursework("Fall2025", "ECON2010", "exam"),
        "MATH 2000 week 1.txt": {"situation": SITUATION,
                                 "destination": ["Fall2025", "MATH2000"]},
        "MATH 2000 week 2.txt": {"situation": SITUATION,
                                 "destination": ["Fall2025", "MATH2000"]},
        "MATH 2000 week 3.txt": {"situation": SITUATION,
                                 "destination": ["Fall2025", "MATH2000"]},
        "HW 3.txt": {"situation": SITUATION, "destination": None,
                     "uncertain": "it states no course, so no course is its home"},
        "survey results.txt": {"situation": SITUATION, "destination": None,
                               "uncertain": "nothing says what it was saved for"},
        "Cover letter Acme.txt": {"situation": "career.recruiting", **outside},
        "Cover letter Beta.txt": {"situation": "career.recruiting", **outside},
        "Jane Doe resume.txt": {"situation": "career.recruiting", **outside},
        "Job posting Acme.txt": {"situation": "career.recruiting", **outside},
    }
    for name in RESEARCH_FILES:
        rows[f"{CONFERENCE}/{name}"] = {"situation": RESEARCH_SITUATION, **outside}

    document = {"files": [dict(row, path=path, group="handoff")
                          for path, row in rows.items()]}
    path = root / "labels.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return load_labels(path)


def test_the_scoreboard_reads_this_one_run_against_every_label_and_finds_no_spill(
        run, tmp_path):
    """`score.score_situation`'s redefined `contaminated`, on a real run.

    The count is "placed under a branch that is not this file's label's", in both
    directions -- a file of another life under `--situation`'s own branch, and a
    file of this situation placed outside it. `00` amendment 7 is what makes ONE
    run scoreable against EVERY label, so this is the whole corpus and not the
    coursework slice of it.
    """
    corpus, database, report = run
    labels = _labels(tmp_path)
    observed = observe_run(database, corpus, situation=SITUATION, label=LABEL,
                           report=report)
    # Every file the run saw has a label, or the count below is measuring a
    # smaller corpus than the person's.
    assert set(labels) == set(observed.files), (
        set(observed.files) ^ set(labels))

    score = score_situation(observed, labels)
    assert score.scored == len(labels)
    assert score.contaminated_of == len(labels)
    assert score.contaminated == 0, {
        path: observed.files[path].destination for path, label in labels.items()
        if observed.files[path].outcome == PLACE}

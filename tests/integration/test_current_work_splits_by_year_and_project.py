# tests/integration/test_current_work_splits_by_year_and_project.py
"""`00` amendments 41 and 42, measured against a real run.

`107`'s branch-template table gives Current work as *Employer -> year -> project or
activity -> stage*, and `00` amendment 22 named it as one of the two trees `year` is
bound on. It was buildable by nothing until 20 Sep: `career` declared neither
`project` nor `stage` (amendment 41 declares both), and there was no situation for a
row to be a row FOR (amendment 42 mints `career.current-work`). This run is that
order, built.

**WHY A REAL RUN AND NOT A UNIT TEST OF THE LIBRARY ROW.**
`tests/p10/test_library_career_current_work.py` is this change's gate test and it
proves the row's and the definition's SHAPE. It cannot prove those levels ever
divide a real plan, because two separate things have to be true at once:
`model_facts.open_question` narrows the question to the situation's OWN folder
levels, so a field that is not a level is never asked -- and the answers then have
to DISAGREE across the corpus, or `00`:57's rule keeps the level recorded and
unbuilt. Both are reachable only through `cli.main`.

**THIS CORPUS SPANS TWO YEARS AND TWO PROJECTS ON PURPOSE**, which is `00` amendment
31's first condition read against a four-level order. `00`:57: *"a level your files
did not actually divide is measured and not built. A level your files DO divide is
always built."* One year, or one project, would RECORD that level and build no
folder -- correct, and a measurement of nothing. So the same person works for the
same employer across two years on two projects, and the two levels `107` puts in the
middle are the two that divide.

**AND THE LEVELS AT EITHER END ARE THE CONTROLS.** The employer is deliberately
CONSTANT and so is the stage, so `00`:57 must leave BOTH out -- which is what makes
the year and project folders below attributable to this change and not to a tree
that split on everything it was handed. A build that opened four levels for four
files would satisfy a "the year divides" assertion and be wrong.

**WHERE THE FACTS COME FROM HERE, STATED RATHER THAN IMPLIED.** Every one of the
four LEVEL values is lifted from the document's own body text by the stub model and
canonicalised through the ordinary site-A path; not one of them is in a filename, so
a folder below can only have come from the document's own words. `year` has two
producers and this run takes the second, for
`test_two_years_of_applications_split_by_year`'s reason: `cli.year_facts` derives it
from a `creation_date` fact, `creation_date` is a folder level of no situation, so
`open_question` never offers it and a synthetic corpus under a chosen situation
cannot reach the derived path at all. What this file measures is the LEVELS.

**WHAT *IS* IN THE FILENAME IS THE KIND, AND THAT IS NOT DECORATION.** `status
report` is a `career` work type in the compiled recognition release, so `work_type`
settles off each file's own name by rule. It is there because the run does not reach
a plan without it: P9 forms no group from four files that settle nothing, and §5.3
*"builds the top level out of accepted groups, existing folders and user labels"* --
measured, by removing it and watching `NothingToDesign: none of []` come back. `104`
R-131 is the sentence behind that: *"a file's own settled kind is what buys the right
to be asked."*

**AND IT COSTS A SITE-E CALL PER FILE, WHICH IS ASSERTED BELOW RATHER THAN LEFT TO
BE FOUND.** `work_type` is destination-eligible and `career.current-work` binds NO
kind level -- `107` gives Current work four levels and a document kind is not one of
them -- so `model_template.file_fits_its_situation` makes every one of these files
UNFIT: *"a fact with no level"*. This is `00` amendment 42's own named cost, and the
half of it the row does not remove. It removes the cost for `project` and `stage`,
which now have levels; it buys one for career's kind keys, which on every OTHER
career row are a level. Nothing here is broken by it -- no template is adopted and
the tree is unaffected -- and it is measured so that the owner is told rather than
the next reader discovering it.

**`GROUP_LEVEL_ROLES` CARRIES NOTHING FOR `career`**, so every level here is read
once per FILE. That is what lets one accepted group under one `--label` divide twice.
"""
from __future__ import annotations

import io
import json
import re
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli

SITUATION = "career.current-work"
LABEL = "Current work"

#: `107`'s own example person is an employee -- *"product designer at Northstar
#: Health"* -- which is the corpus shape this template is for, and the reason
#: `client` is not the employer wearing another name: an in-house corpus has one
#: organisation and it is the holder's own.
EMPLOYER = "Northstar Health"

#: THE TWO LEVELS THAT DIVIDE.
YEARS = ("2024", "2026")
PROJECTS = ("Atlas Redesign", "Beacon Rollout")

#: THE LEVEL AT THE LEAF THAT DOES NOT. One value across the whole corpus, so
#: `00`:57 must record it and build nothing -- the second control.
STAGE = "In review"

#: One document per (year, project). The year, the employer, the project and the
#: stage are each stated in the BODY, once, and none of them is in a filename, so a
#: folder below can only have come from the document's own words.
BODY = (
    "Status report\n\n"
    f"Prepared by the design team at {EMPLOYER}.\n"
    "Work year {year}.\n"
    "Project or activity: {project}.\n"
    "Workstream: platform.\n"
    f"Stage: {STAGE}.\n"
    "Next steps: continue into the following quarter.\n"
)


def _filename(year_index: int, project: str) -> str:
    """The KIND is in the name and nothing else is. `status report` is a `career`
    work type, so `work_type` settles `validated` by rule and P9 has an anchor to
    form a group from; neither the year nor the project value appears, so no folder
    below can be satisfied by a filename rule."""
    return (f"Status report {'first second'.split()[year_index]} "
            f"{project.split()[0].lower()}.txt")


def _local_model():
    """`test_two_years_of_applications_split_by_year`'s own loader: the sibling stub
    module is LOADED rather than copied, so there is one answer in this suite to
    "what does a model reply look like" and not two to drift apart."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "local_model_fact_pass",
        Path(__file__).resolve().parent / "test_local_model_fact_pass.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_YEAR_IN_TEXT = re.compile(r"(?<!\d)(20[0-9]{2})(?!\d)")


def _answers_from_the_files_own_words(local):
    """The four claims this corpus supports, each GROUNDED in a span the dossier
    released, and `unknown` for every other field offered.

    Nothing is invented and nothing is answered by position in the vocabulary:
    `llm_harness.value_grounding` requires a claim's value to be a whole-token run
    of a released value the claim cites, so an invented answer would be rejected and
    this file would be measuring the validator instead of the level.

    NOTE WHAT THIS ALSO PROVES: the dossier's vocabulary is the union of the SCHEMA's
    rows, so a current-work file is offered `target_employer`, `recruiting_cycle` and
    the rest of career's keys too. Every one of them comes back `unknown` here, which
    is the ordinary answer and the reason amendment 42 insisted the fields and the
    row land together -- a key with no level is a question with nowhere to put the
    answer.
    """
    def answer(payload: str) -> str:
        dossier = local.dossier_in(payload)
        fields = [field for field in dossier.get("allowed_vocabulary", ())
                  if isinstance(field, str)]
        released = [item for item in dossier.get("released_evidence", ())
                    if isinstance(item, dict)
                    and isinstance(item.get("value"), str)]

        def cite(value, item):
            return {"payload": {"field": None, "value": value},
                    "citations": [{"evidence_ref": item["observation_key"],
                                   "cited_span": value,
                                   "why_it_supports":
                                       "the value is copied from this span"}]}

        supported = {}
        for item in released:
            text = item["value"]
            found = _YEAR_IN_TEXT.search(text)
            if found is not None and "year" not in supported:
                supported["year"] = cite(found.group(1), item)
            if EMPLOYER in text and "employer" not in supported:
                supported["employer"] = cite(EMPLOYER, item)
            if STAGE in text and "stage" not in supported:
                supported["stage"] = cite(STAGE, item)
            for project in PROJECTS:
                if project in text and "project" not in supported:
                    supported["project"] = cite(project, item)

        claims = []
        for field in fields:
            if field in supported:
                claim = supported[field]
                claim["payload"]["field"] = field
                claims.append(claim)
            else:
                claims.append({
                    "payload": {"field": field},
                    "unknown": {"insufficiency_statement":
                                "no released evidence carries this field"}})
        if not claims:
            return local._answer_for(payload)
        return json.dumps({"claims": claims})
    return answer


@pytest.fixture()
def run(tmp_path):
    """One corpus, one `--label`, four status notes: two years by two projects."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for index, year in enumerate(YEARS):
        for project in PROJECTS:
            (corpus / _filename(index, project)).write_text(
                BODY.format(year=year, project=project), encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()

    local = _local_model()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv(local.LOCAL_MODEL_NAME, local.MODEL_ID)
    try:
        with local.StubOllama(
                answer=_answers_from_the_files_own_words(local)) as stub:
            monkeypatch.setenv(local.LOCAL_BASE_URL_NAME, stub.base_url)
            cli.main([str(corpus), "--situation", SITUATION,
                      "--label", LABEL, "--user", "jy",
                      "--accept-groups",
                      "--database", str(database)], out=out)
    finally:
        monkeypatch.undo()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    yield conn, out.getvalue()
    conn.close()


def _facts(conn, field_key):
    return {row["canonical_value"]: row["reliability_state"]
            for row in conn.execute(
                'SELECT DISTINCT v.canonical_value, ff.reliability_state '
                'FROM file_facts ff JOIN "values" v USING (value_id) '
                "WHERE ff.field_key = ? AND ff.active", (field_key,))}


def _latest_plan_version(conn):
    return conn.execute(
        "SELECT plan_version_id FROM tree_nodes ORDER BY rowid DESC LIMIT 1"
    ).fetchone()["plan_version_id"]


def _final_tree(conn):
    """The nodes of the LAST plan version this run wrote. A run writes a version per
    refinement pass and each keeps its own nodes, so reading `tree_nodes` whole
    would count one folder several times."""
    return list(conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? ORDER BY rowid",
        (_latest_plan_version(conn),)))


def _recorded(conn, field_key):
    """Every value `tree_design.materialise` recorded on ANY node of the final plan
    version -- present whether or not a child folder was built for it, which is
    `00`:57's own distinction."""
    return {row["value"] for row in conn.execute(
        "SELECT value FROM node_expected_values "
        "WHERE plan_version_id = ? AND field_key = ?",
        (_latest_plan_version(conn), field_key))}


# --- the premises, so nothing below measures nothing --------------------------

def test_the_premise_the_row_admits_all_four_levels_to_the_situation():
    """The wiring itself, read off the shipped library rather than off the run.
    Before amendments 41 and 42 this raised: `career.current-work` named no
    situation in the release at all, so `open_question` could never offer any of
    these fields to a file that had a situation."""
    import production
    catalogue = production.load_shipped_catalogue(
        production.read_packaged_library_file)
    levels = production.folder_levels_for(catalogue, SITUATION)
    assert [level.field for level in levels] == [
        "employer", "year", "project", "stage"]
    assert production.group_level_fields_for(catalogue, SITUATION) == frozenset()


def test_the_premise_every_file_answers_all_four_from_its_own_body(run):
    """If this fails the corpus is not exercising the row at all and everything
    below measures nothing (`84` §5.3's failure mode)."""
    conn, _out = run
    assert set(_facts(conn, "employer")) == {EMPLOYER}
    assert set(_facts(conn, "year")) == set(YEARS)
    assert set(_facts(conn, "project")) == set(PROJECTS)
    assert set(_facts(conn, "stage")) == {STAGE}
    # And the kind settles off the NAME by rule, which is what buys the group the
    # tree is built out of. `validated` is the rule's own state, not a model's.
    assert _facts(conn, "work_type") == {"status report": "validated"}


def test_the_kind_has_no_level_here_and_that_costs_one_site_e_call_per_file(run):
    """`00` AMENDMENT 42'S NAMED COST, MEASURED — the half of it this row does not
    remove.

    The amendment's argument for landing the fields and the row together is that
    *"a proposal-eligible fact with no level in the file's situation"* is UNFIT at
    site E, *"one template call per file, for a fact with nowhere to live."* The row
    gives `project` and `stage` their levels and removes that cost for them. It does
    NOT remove it for career's KIND keys: `work_type` is destination-eligible, every
    other career row binds a kind level (`work_type` on recruiting, `record_type` on
    the tenure and employer-side rows), and this one binds none — because `107` gives
    Current work four levels and a document kind is not among them.

    ASSERTED RATHER THAN NOTED, so the day somebody adds a fifth level or reorders
    the row this number moves and is read. NOTHING IS BROKEN BY IT: no template is
    adopted, the tree below is unaffected, and the call is the product doing exactly
    what it says it does when a file states something its situation has no folder
    for. What it is not is free, and the owner is owed that in a number.
    """
    _conn, report = run
    printed = " ".join(report.split())
    assert "4 of 4 files were asked for a folder template of their own" in printed
    assert "and 0 were given one" in printed


# --- the two controls ---------------------------------------------------------

def test_the_employer_is_constant_so_00_57_leaves_its_level_out(run):
    """THE FIRST CONTROL, at the HEAD of `107`'s order. *"Any level your files did
    not actually divide is measured and not built."* One employer across four files
    is a level with one value, so no employer folder is built -- and a year folder
    therefore cannot be an employer folder wearing a year.

    NOR IS IT RECORDED. `career` names no group-level role
    (`production.GROUP_LEVEL_ROLES`), so an undivided per-file level is simply left
    out: the fact stays on the files and nothing on the plan claims it. The
    teaching row's undivided level IS recorded, because `school` there is a GROUP
    role -- which is why this is asserted rather than assumed.
    """
    conn, _out = run
    employer_nodes = [node for node in _final_tree(conn)
                      if node["dimension"] == "employer"]
    assert employer_nodes == []
    assert _recorded(conn, "employer") == set()


def test_the_stage_is_constant_so_00_57_leaves_its_level_out_too(run):
    """THE SECOND CONTROL, at the LEAF. The two controls sit at either END of
    `107`'s order on purpose: a build that opened a folder for every level it was
    handed would pass a "the year divides" assertion and be wrong, and a build that
    only ever opened the levels in the middle would pass one control and fail this
    one."""
    conn, _out = run
    stage_nodes = [node for node in _final_tree(conn)
                   if node["dimension"] == "stage"]
    assert stage_nodes == []
    assert _recorded(conn, "stage") == set()


# --- the measured outcome -----------------------------------------------------

def test_the_two_years_become_two_folders(run):
    """Read off `dimension_role` as well as `dimension`, so a run that happened to
    put those strings somewhere else in the tree cannot satisfy it: the level has to
    be the one the library binds `capture_time` to."""
    conn, _out = run
    year_nodes = [node for node in _final_tree(conn)
                  if node["dimension_role"] == "capture_time"]
    assert [node["dimension"] for node in year_nodes] == ["year", "year"]
    assert sorted(node["display_label"] for node in year_nodes) == sorted(YEARS)
    assert _recorded(conn, "year") == set(YEARS)


def test_each_year_divides_again_into_its_two_projects(run):
    """THE LEVEL AMENDMENT 41 PAID FOR. `project` is the key `career` did not
    declare, and this is the folder it buys: two projects under each of two years,
    bound to `project_anchor` so the level is the library's and not a coincidence.

    THE NESTING IS THE ASSERTION, not the count. Four project folders in a flat
    list would also be four project folders; what `107` asks for is the project
    BENEATH the year, so every project node's parent is checked to be a year node.
    """
    conn, _out = run
    nodes = _final_tree(conn)
    year_nodes = {node["node_id"]: node for node in nodes
                  if node["dimension"] == "year"}
    project_nodes = [node for node in nodes
                     if node["dimension_role"] == "project_anchor"]
    assert len(project_nodes) == 4, [n["display_label"] for n in project_nodes]
    assert {node["dimension"] for node in project_nodes} == {"project"}
    assert {node["parent_node_id"] for node in project_nodes} == set(year_nodes)
    for node_id in year_nodes:
        beneath = sorted(node["display_label"] for node in project_nodes
                         if node["parent_node_id"] == node_id)
        assert beneath == sorted(PROJECTS), beneath
    assert _recorded(conn, "project") == set(PROJECTS)


def test_no_document_reaches_the_other_years_project_folder(run):
    """The discriminating twin. Four folders are worth nothing if the files are
    split across them: a person would open 2024's Atlas Redesign and find 2026's
    note inside it, which is worse than one merged folder because it looks right."""
    conn, _out = run
    nodes = _final_tree(conn)
    year_nodes = {node["node_id"]: node for node in nodes
                  if node["dimension"] == "year"}
    assert len(year_nodes) == 2

    expected = {}
    for row in conn.execute(
            "SELECT node_id, field_key, value FROM node_expected_values "
            "WHERE plan_version_id = ?", (_latest_plan_version(conn),)):
        expected.setdefault(row["node_id"], {}).setdefault(
            row["field_key"], set()).add(row["value"])

    leaves = [node for node in nodes if node["dimension"] == "project"]
    assert len(leaves) == 4
    for leaf in leaves:
        parent = year_nodes[leaf["parent_node_id"]]
        assert expected[leaf["node_id"]]["year"] == {parent["display_label"]}
        assert expected[leaf["node_id"]]["project"] == {leaf["display_label"]}


def test_the_branch_offers_107s_order_in_the_products_own_words(run):
    """The shape the run PRINTS for this branch, which is what a person is actually
    shown and what they would type to keep it. `107`: *Employer -> year -> project
    or activity -> stage*. All four are printed, including the two `00`:57 declined
    to build -- the offer is the situation's levels and the tree is what the files
    supported."""
    _conn, report = run
    assert (f"branch:{LABEL}=employer>year>project>stage"
            in " ".join(report.split())), report

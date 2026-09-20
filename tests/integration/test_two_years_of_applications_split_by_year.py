# tests/integration/test_two_years_of_applications_split_by_year.py
"""`00` amendment 33's second half, measured against a real run.

`107`'s branch-template table gives Career applications as *Year -> organization
and role -> application stage*, and until amendment 33 `year` was bound in NO
shipped row: `00` amendment 22 ratified where it goes and nothing wired it. This
run is the level, built.

**WHY A REAL RUN AND NOT A UNIT TEST OF THE LIBRARY ROW.**
`tests/p10/test_library_career_recruiting.py` (this change's gate test) proves the
row's and the definition's SHAPE. It cannot prove `year` ever divides a real plan,
because two separate things have to be true at once for that: the field has to be
OFFERED to the file at all -- `model_facts.open_question` narrows the question to
the situation's OWN folder levels, so a field that is not a level is never asked --
and the answers have to disagree across the corpus, or `00`:57's rule keeps the
level recorded and unbuilt. Both are reachable only through `cli.main`.

**THIS CORPUS SPANS TWO YEARS ON PURPOSE.** `00`:57: *"a level your files did not
actually divide is measured and not built. A level your files DO divide is always
built."* One year of applications would RECORD the year on the branch and build no
folder, which would be correct and would measure nothing about a level. So the same
person applies to the same employer twice, two years apart, and the only thing that
differs between the two halves of the corpus is the year -- which is what makes the
two `Year` folders below attributable to this change and to nothing else. The
employer is deliberately CONSTANT, so the level above it in `107`'s order is the one
that divides and the employer level is the one `00`:57 records instead.

**WHERE THE YEAR FACT COMES FROM HERE, STATED RATHER THAN IMPLIED.** `year` has two
producers. `cli.year_facts` derives it from the file's own `creation_date` fact --
amendment 33's FIRST half, repaired and measured separately (4 of 47 real
`creation_date` facts before, 47 of 47 after) -- and `cli.normalize_for_model`
canonicalises a model's own answer through that same `year_of`, because *"`year` is
universal, so it is in site A's allowlist and a model may be asked it"*. This run
takes the second path, and it is not a convenience: `creation_date` is NOT a folder
level of any situation, so `open_question` never offers it to a file that has one,
and no rule or direct slot writes it (`facts.direct`'s only slot is EXIF's
`capture_year`). A synthetic corpus under a chosen situation therefore cannot reach
the derived path at all, and reaching for it would be measuring the stub rather than
the level. What this file measures is the LEVEL: that the year a file carries
becomes the folder `107` asks for.

**`GROUP_LEVEL_ROLES` CARRIES NOTHING FOR `career`**, so unlike `school` on the
teaching row the year is read once per FILE. That is what lets one accepted group
under one `--label` still divide.
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

SITUATION = "career.recruiting"
EMPLOYER = "Northwind Systems"
YEARS = ("2024", "2026")

#: Two documents per application, and the pair that a job search actually produces:
#: `cover letter` and `resume` are both members of the compiled recognition
#: release's `work_type_terms` for `career`, so `work_type` -- the row's other
#: REQUIRED level -- settles `validated` off each file's own NAME by rule, with no
#: model needed (`104` R-131: "a file's own settled kind is what buys the right to
#: be asked").
#:
#: The YEAR is never in a filename. It is stated in the body, once per file, so the
#: folder below can only have come from the document's own words.
COVER_LETTER = (
    "Cover letter\n\n"
    "Dear Hiring Team,\n\n"
    f"I am writing about the Systems Engineer opening at {EMPLOYER}.\n"
    "I am submitting this application in the spring of {year}.\n"
)
RESUME = (
    "Resume\n\n"
    "Systems Engineer. Five years of platform work.\n"
    f"Prepared for the {EMPLOYER} application of {{year}}.\n"
)

#: `(filename, body template)` per year. Two rounds at ONE employer.
ROUNDS = (
    ("Cover letter Northwind first attempt.txt", COVER_LETTER),
    ("Engineering resume first attempt.txt", RESUME),
)
SECOND = (
    ("Cover letter Northwind second attempt.txt", COVER_LETTER),
    ("Engineering resume second attempt.txt", RESUME),
)


def _local_model():
    """`test_a_teaching_syllabus_lands_under_its_school.py`'s own loader, which is
    `test_two_courses_keep_two_terms.py`'s before it: the sibling stub module is
    LOADED rather than copied, so there is one answer in this suite to "what does
    a model reply look like" and not two to drift apart."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "local_model_fact_pass",
        Path(__file__).resolve().parent / "test_local_model_fact_pass.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_YEAR_IN_TEXT = re.compile(r"(?<!\d)(20[0-9]{2})(?!\d)")


def _answers_from_the_files_own_words(local):
    """The two claims this corpus actually supports, each GROUNDED in a span the
    dossier released, and `unknown` for every other field offered.

    Nothing is invented and nothing is answered by position in the vocabulary:
    `llm_harness.value_grounding` requires a claim's value to be a whole-token run
    of a released value the claim cites, so an invented answer would be rejected and
    this file would be measuring the validator. The year is lifted from whichever
    released item prints one, and the employer from whichever prints its name --
    which is what a real model's correct answer would look like on these files too.
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
            found = _YEAR_IN_TEXT.search(item["value"])
            if found is not None and "year" not in supported:
                supported["year"] = cite(found.group(1), item)
            if EMPLOYER in item["value"] and "target_employer" not in supported:
                supported["target_employer"] = cite(EMPLOYER, item)

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
    """One corpus, one `--label`, two application rounds two years apart."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for year, files in zip(YEARS, (ROUNDS, SECOND)):
        for name, body in files:
            (corpus / name).write_text(body.format(year=year), encoding="utf-8")
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
                      "--label", "Job applications", "--user", "jy",
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
    """The nodes of the LAST plan version this run wrote. A run writes a version
    per refinement pass and each keeps its own nodes, so reading `tree_nodes`
    whole would count one folder several times."""
    return list(conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? ORDER BY rowid",
        (_latest_plan_version(conn),)))


def _recorded(conn, field_key):
    """Every value `tree_design.materialise` recorded on ANY node of the final
    plan version -- present whether or not a child folder was built for it, which
    is `00`:57's own distinction."""
    return {row["value"] for row in conn.execute(
        "SELECT value FROM node_expected_values "
        "WHERE plan_version_id = ? AND field_key = ?",
        (_latest_plan_version(conn), field_key))}


def test_the_premise_every_file_settles_its_kind_by_rule(run):
    """If this fails the corpus is not exercising the recruiting row at all and
    everything below measures nothing (`84` §5.3's failure mode): `work_type` is
    one of the row's two REQUIRED levels and it settles off the filename."""
    conn, _out = run
    kinds = _facts(conn, "work_type")
    assert set(kinds) == {"cover letter", "resume"}, kinds
    assert set(kinds.values()) == {"validated"}, kinds


def test_the_premise_the_two_rounds_carry_two_different_years(run):
    """The year is the ONLY thing that differs between the two halves of this
    corpus, so this is the premise the folder assertion rests on."""
    conn, _out = run
    years = _facts(conn, "year")
    assert set(years) == set(YEARS), years


def test_the_employer_is_constant_so_00_57_leaves_its_level_out(run):
    """The control, and the answer is `00`:57's own: *"any level your files did
    not actually divide ... is measured and not built"*, which the run prints
    among the decisions it made for nobody. One employer across four files is a
    level with one value, so no employer folder is built -- and a `Year` folder
    therefore cannot be an employer folder wearing a year.

    NOR IS IT RECORDED, and that is worth stating because the teaching row's
    undivided level WAS. `school` there is a GROUP-level role
    (`production.GROUP_LEVEL_ROLES["academic"]`), and a group's value is written
    to `node_expected_values` on the branch whether or not it divides. `career`
    names no group-level role, so an undivided per-file level is simply left out
    -- the fact stays on the files and nothing on the plan claims it.
    """
    conn, _out = run
    assert set(_facts(conn, "target_employer")) == {EMPLOYER}
    employer_nodes = [node for node in _final_tree(conn)
                      if node["dimension"] == "target_employer"]
    assert employer_nodes == []
    assert _recorded(conn, "target_employer") == set()


def test_the_row_now_admits_year_to_the_situations_own_levels():
    """The wiring itself, read off the shipped library rather than off the run.
    Before amendment 33 was wired this assertion failed -- `year` was absent from
    `folder_levels_for(catalogue, 'career.recruiting')`, so
    `model_facts.open_question` never offered the field and no year fact could
    exist on a file that had a situation at all."""
    import production
    catalogue = production.load_shipped_catalogue(
        production.read_packaged_library_file)
    levels = production.folder_levels_for(catalogue, SITUATION)
    assert levels[0].field == "year", [level.field for level in levels]
    assert production.group_level_fields_for(catalogue, SITUATION) == frozenset()


def test_the_two_years_become_two_folders(run):
    """THE MEASURED OUTCOME. Read off `dimension_role` as well as `dimension`, so
    a run that happened to put those two strings somewhere else in the tree cannot
    satisfy it: the level has to be the one the library binds `capture_time` to."""
    conn, _out = run
    year_nodes = [node for node in _final_tree(conn)
                  if node["dimension_role"] == "capture_time"]
    assert [node["dimension"] for node in year_nodes] == ["year", "year"]
    assert sorted(node["display_label"] for node in year_nodes) == sorted(YEARS)
    assert _recorded(conn, "year") == set(YEARS)


def test_no_round_reaches_the_other_years_folder(run):
    """The discriminating twin. Two folders are worth nothing if the files are
    split across them: a person would open the earlier year and find this year's
    application inside it, which is worse than one merged folder because it looks
    right."""
    conn, _out = run
    nodes = _final_tree(conn)
    year_nodes = {node["node_id"]: node for node in nodes
                  if node["dimension"] == "year"}
    assert len(year_nodes) == 2

    #: Every leaf the run built sits under ONE year, and the year it inherits is
    #: the one `materialise` recorded on it -- so a `cover letter` folder under
    #: 2024 expects 2024 and cannot also be reached from 2026.
    expected = {}
    for row in conn.execute(
            "SELECT node_id, value FROM node_expected_values "
            "WHERE plan_version_id = ? AND field_key = 'year'",
            (_latest_plan_version(conn),)):
        expected.setdefault(row["node_id"], set()).add(row["value"])

    leaves = [node for node in nodes if node["dimension"] == "work_type"]
    assert len(leaves) == 4
    for leaf in leaves:
        parent = year_nodes[leaf["parent_node_id"]]
        assert expected[leaf["node_id"]] == {parent["display_label"]}, (
            leaf["display_label"], parent["display_label"])
    assert {leaf["parent_node_id"] for leaf in leaves} == set(year_nodes)


def test_the_branch_offers_107s_order_in_the_products_own_words(run):
    """The shape the run PRINTS for this branch, which is what a person is
    actually shown and what they would type to keep it. `107`: *Year ->
    organization and role -> application stage*."""
    _conn, report = run
    assert ("branch:Job applications="
            "year>target_employer>job_title>recruiting_cycle>work_type"
            in " ".join(report.split())), report

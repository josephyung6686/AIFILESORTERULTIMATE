# tests/integration/test_a_teaching_syllabus_lands_under_its_school.py
"""Amendment 31's first authorised use, measured against a real run.

`00` amendment 31: `academic.teaching` v2 binds the institution level -- `school ->
term -> subject -> work_type`, which is `107`'s *institution -> term -> course ->
teaching function*. The shipped v1 row binds no institution at all, though
`def.subject-work-record.third-party` already declares `holder_institution` as an
OPTIONAL dimension and `academic.coursework`'s OWN row already binds it to `school`
under the label "My school" -- so wiring v2 asks nothing of the pipeline that is not
already proven for coursework; it only extends the same binding to teaching.

**WHY A REAL RUN AND NOT A UNIT TEST OF THE LIBRARY ROW.** `tests/p10/test_library_
academic_teaching.py` (this wave's gate test) proves the row's own SHAPE; it cannot
prove `school` ever reaches a real plan, because the school level is `105` §14.4's
TWO-ANCHOR rule -- two independently originating documents about one course must
agree before the field resolves at all -- and that rule is wired at
`cli.design_authorities`, reached only through `cli.main`. A row that parses but
whose bound field the two-anchor reader never sees would pass every unit test in the
library and still record nothing.

**WHAT "LANDS" MEANS HERE, MEASURED RATHER THAN ASSUMED.** `holder_institution` is a
GROUP-level role (`production.GROUP_LEVEL_ROLES["academic"]`), so `school` is read
ONCE PER ACCEPTED GROUP, not once per file -- the same reason `test_two_courses_
keep_two_terms.py` can split `term` per file but never asks the same of `school`.
`--accept-groups` with one `--label` writes ONE accepted group; a single course's two
syllabi agreeing on one school is a level with exactly one value, and `00`:57's own
rule -- "a level your files did not actually divide is measured and not built" -- is
why this run builds no CHILD FOLDER for it. It still RECORDS the value: a real run
against this corpus prints "The branch records school Columbia University ... instead
[of a folder]", and `tree_design.materialise` writes that recording to
`node_expected_values`. That row is what v1 could never produce (`anchor_only` is
`None` without the binding, so the model is never asked and no `school` fact exists
at all) and what v2 does -- so it is what this test measures.

A second course at a second school, so `school` genuinely has two values and a
FOLDER too, requires the two schools' accepted groups to stay scope-isolated
(`105` §14.4's own `scope_field=subject`); `--accept-groups` gives every course under
one `--label` ONE shared group, and two schools sharing that one group's scope is the
mirror image of `tests/p10/test_p10_school_two_anchors.py::test_two_anchors_in_one_
group_stating_two_courses_are_not_in_scope` -- the anchors would DISAGREE about one
scope's school rather than name two scopes' two schools. Building an actual two-school
folder through `cli.main` needs per-course groups (`00`'s "B", unratified as of this
wave), and that gap is reported in this wave's commit rather than worked around here.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli

SITUATION = "academic.teaching"
INSTITUTION = "Columbia University"

#: Two independent syllabi of ONE course, so they share the scope the two-anchor
#: rule asks for (`105` §14.4's `scope_field` is `subject`). `work_type` settles
#: to `syllabus` off each file's OWN NAME (`facts.kind`'s closed vocabulary, in
#: `NAMING_ZONES` -- no model needed), which is what admits a file to the
#: `school` question at all (`104` R-131: "a file's own settled kind is what
#: buys the right to be asked"). `subject` and `term` settle off the body
#: through the shipped rule and the date pass, exactly as `test_two_courses_
#: keep_two_terms.py` already measures. Only `school` needs the model: each
#: syllabus independently states "Columbia University" in body text the model
#: was never asked to invent, so the school comes back a GROUNDED
#: `llm_supported` fact on each file (`llm_harness.value_grounding` requires the
#: answer to be a whole-token run of a released value the claim cites) and the
#: two anchors AGREE.
#:
#: The `Instructor:` line is shared, because two syllabi of the same course
#: legitimately print the same instructor and term -- `105` §14.4's independence
#: test is about the DOCUMENTS' own bytes
#: (`_a_syllabus_and_its_copy_are_one_source` in `tests/p10/test_p10_school_two_
#: anchors.py`), not about every line inside them agreeing -- and each file
#: below carries its own sentence naming the school that its course-mate does
#: not share a word of.
SYLLABUS_A = (
    "PHYS 1401 Syllabus -- Fall 2024\n\n"
    "Instructor: R. Feynman. Section 1, Fall 2024.\n"
    "Meets Tuesday and Thursday.\n"
    f"{INSTITUTION} Department of Physics.\n"
)
SYLLABUS_B = (
    "PHYS 1401 Syllabus -- Fall 2024 (Room Change)\n\n"
    "Instructor: R. Feynman. Section 1, Fall 2024.\n"
    "The lecture hall has moved to Pupin Hall.\n"
    f"{INSTITUTION} confirms this schedule by email.\n"
)


def _local_model():
    """`test_two_courses_keep_two_terms.py`'s own loader, unchanged.

    A second ollama stub would be a second answer to "what does a model reply
    look like", and the two would drift -- so the sibling module is loaded rather
    than copied, exactly as that file's own docstring explains.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "local_model_fact_pass",
        Path(__file__).resolve().parent / "test_local_model_fact_pass.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _answers_school_from_its_own_sentence(local):
    """One claim, `school`, grounded in the institution SENTENCE the dossier
    actually released -- never in the filename, and never invented.

    Answering by POSITION in `allowed_vocabulary` (the sibling stub's own general
    rule) is not used here: `released_evidence` also carries the file's name and
    its directory, both of which tokenize to more than the two words the general
    stub lifts, and either could be picked before the sentence that actually
    names the school. This answers the one field `105` §14.4 is actually asking
    about and cites the one item that actually supports it, which is what a real
    model's correct answer would look like too.
    """
    def answer(payload: str) -> str:
        dossier = local.dossier_in(payload)
        fields = [field for field in dossier.get("allowed_vocabulary", ())
                  if isinstance(field, str)]
        if "school" not in fields:
            return local._answer_for(payload)
        released = [item for item in dossier.get("released_evidence", ())
                    if isinstance(item, dict)
                    and isinstance(item.get("value"), str)]
        named = next(
            (item for item in released if INSTITUTION in item["value"]), None)
        if named is None:
            return local._answer_for(payload)
        return json.dumps({"claims": [{
            "payload": {"field": "school", "value": INSTITUTION},
            "citations": [{"evidence_ref": named["observation_key"],
                          "cited_span": INSTITUTION,
                          "why_it_supports":
                              "the value is copied from this span"}],
        }]})
    return answer


@pytest.fixture()
def run(tmp_path):
    """One corpus, two independent teaching syllabi of one course, one local
    model answering only the question `105` §14.4 actually opens."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 Syllabus A.txt").write_text(SYLLABUS_A, encoding="utf-8")
    (corpus / "PHYS 1401 Syllabus B.txt").write_text(SYLLABUS_B, encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()

    local = _local_model()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv(local.LOCAL_MODEL_NAME, local.MODEL_ID)
    try:
        with local.StubOllama(
                answer=_answers_school_from_its_own_sentence(local)) as stub:
            monkeypatch.setenv(local.LOCAL_BASE_URL_NAME, stub.base_url)
            cli.main([str(corpus), "--situation", SITUATION,
                      "--label", "Teaching", "--user", "jy",
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


def _recorded_school_values(conn):
    """Every `school` value `tree_design.materialise` recorded on ANY node of
    the run's final plan version -- present whether or not a child folder was
    built for it, which is exactly the distinction this row's absence/presence
    makes (`00`:57: an undivided level is recorded, not folder-ised)."""
    plan_version_id = _latest_plan_version(conn)
    return {row["value"] for row in conn.execute(
        "SELECT value FROM node_expected_values "
        "WHERE plan_version_id = ? AND field_key = 'school'",
        (plan_version_id,))}


def test_the_premise_both_syllabi_settle_one_course_by_rule(run):
    """If this fails the corpus is not exercising `105` §14.4 at all and the
    tests below measure nothing (`84` §5.3's failure mode).

    `in` rather than exact equality: the filename repeats the body's own course
    code, which flags a genuine `subject`/`term`/`work_type` conflict for the
    model's second opinion beside the rule's own answer, and the sibling stub's
    generic fallback (used here for every call that is not about `school`) can
    write a `possible`-tier guess alongside it. `00`:42's own ladder keeps that
    below the rule's `validated` answer and neither test below reads it -- this
    premise asks only that the RULE's answer is the one that is there.
    """
    conn, _out = run
    assert _facts(conn, "work_type").get("syllabus") == "validated"
    assert _facts(conn, "subject").get("PHYS1401") == "validated"
    assert _facts(conn, "term").get("Fall2024") == "validated"


def test_each_syllabus_independently_names_the_school(run):
    """The two anchors, GROUNDED and AGREEING -- the premise `105` §14.4 asks
    for, measured before asking what the row does with it."""
    conn, _out = run
    schools = _facts(conn, "school")
    assert schools == {INSTITUTION: "llm_supported"}


def test_the_row_now_admits_school_to_the_situations_own_levels():
    """The wiring itself, read off the shipped library rather than off the run:
    `academic.teaching` now carries `school` among its group-level fields, which
    is what `cli._the_situation_of_a_run` turns into the anchor question at all.
    Before amendment 31 was wired this assertion failed -- `school` was absent
    from `folder_levels_for(catalogue, 'academic.teaching')` and the two agreeing
    anchors measured above had no question to answer and no field to land in."""
    import production
    catalogue = production.load_shipped_catalogue(
        production.read_packaged_library_file)
    fields = {level.field for level in
              production.folder_levels_for(catalogue, SITUATION)}
    assert "school" in fields
    assert "school" in production.group_level_fields_for(catalogue, SITUATION)


def test_the_agreed_school_is_recorded_on_the_plan(run):
    """THE MEASURED OUTCOME. Before the row bound `holder_institution`,
    `anchor_only` was `None` for `academic.teaching`: no anchor question was
    ever asked, no `school` fact ever existed, and `node_expected_values` carried
    no `school` row for any node of any plan this situation built -- `104` R-102's
    own finding, "nothing writes a `school` fact any more, so the coursework tree
    has no school level on any corpus", true of teaching too until this row.

    Now the two anchors' agreed `Columbia University` is recorded on the plan
    the run actually wrote. `00`:57's own rule keeps this single-school corpus
    from also getting a CHILD FOLDER for it -- one value does not divide a
    branch -- so the row's effect is measured at the level `materialise_branch`
    actually writes to (`node_expected_values`), not assumed from a folder that
    a one-school corpus was never going to need.
    """
    conn, _out = run
    assert _recorded_school_values(conn) == {INSTITUTION}

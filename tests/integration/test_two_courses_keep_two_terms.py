# tests/integration/test_two_courses_keep_two_terms.py
"""Two courses, two calendars, two `Semester` folders -- through `cli.main`.

`105` §14.2 is three rulings about one field and only the third can be asked here:
*"the result is bound to the relevant course"*, and *"infer no equivalence between
numbered terms, semesters, or seasons without evidence for that course's calendar"*.
A unit test can prove a canonicaliser keeps two strings apart; only a run can prove
that the two strings become two folders and that each course's files are under its
own.

**HALF OF THIS CORPUS WAS UNREADABLE BEFORE 7 SEP 2026.** `104` R-101 counted the
owner's real run: 114 `term` answers refused, and the single commonest refused shape
was `2023-2024 Term 1`, fifteen times, with `2023-2024` thirteen more. That is one
university writing its own two-term calendar, and this product had no pattern for it,
so those files reached no `Semester` level at all. `CHEM2100` below is that course.
The test is therefore not a rearrangement of an existing one: run it against the
previous vocabulary and the second course has no term.

**AND THE MERGE IT RULES OUT IS REAL AND IS STILL SWITCHED OFF.**
`production.GROUP_LEVEL_ROLES` deliberately does not carry `cycle_period`.
`cli._merge_reviewed_groups` writes ONE accepted group per `--label` -- both courses
below are in it -- so "the group's term" would be a disagreement between `Fall2024`
and `2023-2024Semester1`, `group_level_value` would answer `None`, and BOTH folders
would disappear. The term stays the FILE's own value, and a file belongs to one
course. That is the binding §14.2 asks for at the only grain that exists until B is
ratified and groups are per course.

Written through `cli.main` rather than a hand-built fixture, for `85` §6.4 and `84`
§5.5's reason: a part's own suite cannot see this defect class, because every part
builds its own fixture and sets up the state the run never reaches.
`tests/integration/test_production_corpus.py` cannot ask it either -- its `_stage`
splits a filename on spaces and assigns the tokens to fields positionally, so no
term pattern runs there at all.
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


#: One syllabus, printing its course and its term the way a syllabus does.
#: `Instructor:` is load-bearing: `cli.SUBJECT_RULE` is §3.5's rule and a course code
#: is a fact only "together with academic context such as 'syllabus,' 'lecture,'
#: 'credits,' 'instructor,' or 'semester'". Without a subject there is no course to
#: bind the term TO, and the test would pass for the wrong reason.
#:
#: **THE SECTION NUMBER WAS `Section 001` UNTIL 2026-09-08 AND IT IS `Section 1` NOW,
#: FOR A REASON THAT IS NOT COSMETIC AND IS PINNED BELOW.** A three-digit section
#: number beside `Instructor:` is a second `validated` `subject` on every file of this
#: corpus, the subject level then settles on nothing, and all four assertions about
#: courses fail while the ones about terms pass. That is a real defect and it is NOT
#: `104` R-146's: measured at `9cd52c6` with this same fixture written `SECTION 001`,
#: the run at the previous uppercase-only recogniser produces exactly the same two
#: facts per file (`PHYS1401` and `SECTION001`). R-146 changed only how often a real
#: document reaches it, by making a title-case word readable. So this fixture is put
#: back to asking its own question -- two courses, two calendars -- and the defect it
#: stumbled into is asked separately, by `test_a_second_code_shaped_reading_...`
#: below, where it can be measured instead of taking four tests down with it.
SYLLABUS = """{code} Syllabus -- {term}

Instructor: R. Feynman. Section 1, {term}.
Meets Tuesday and Thursday.
"""

#: THE TWO CALENDARS. `Fall 2024` is a season and a year, which this product has read
#: since it could read a term at all. `2023-2024 Semester 1` is the two-term academic
#: year's own spelling, which `105` §14.2 ruled in.
#:
#: They are very probably the SAME PART of the year at two universities, and that is
#: exactly what the ruling forbids inferring: a two-term year's first semester is
#: autumn in the northern hemisphere and is not in the southern one, and this product
#: has no evidence about either course's calendar. So they stay two.
COURSES = (
    ("phys", "PHYS 1401", "PHYS1401", "Fall 2024", "Fall2024"),
    ("chem", "CHEM 2100", "CHEM2100", "2023-2024 Semester 1", "2023-2024Semester1"),
)


@pytest.fixture()
def run(tmp_path):
    """One corpus, one `--label`, two courses on two calendars, two files each."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for stem, code, _, term, _ in COURSES:
        for index in range(2):
            (corpus / f"{stem} syllabus {index}.txt").write_text(
                SYLLABUS.format(code=code, term=term), encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--accept-groups",
              "--database", str(database)], out=out)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _values(conn, field_key):
    return {row["canonical_value"]: json.loads(row["raw_variants"])
            for row in conn.execute(
                'SELECT canonical_value, raw_variants FROM "values" '
                "WHERE field_key = ? ORDER BY canonical_value", (field_key,))}


def _final_tree(conn):
    """The nodes of the LAST plan version this run wrote.

    A run writes a plan version per refinement pass and every pass keeps its own
    nodes, so reading `tree_nodes` whole would count one folder several times. The
    last version is the tree the person is shown.
    """
    latest = conn.execute(
        "SELECT plan_version_id FROM tree_nodes ORDER BY rowid DESC LIMIT 1"
    ).fetchone()["plan_version_id"]
    return list(conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? ORDER BY rowid",
        (latest,)))


def test_both_courses_settle_a_term_and_the_new_form_is_one_of_them(run):
    """The premise. If this fails the corpus has stopped exercising the ruling and
    everything below is measuring nothing -- the failure mode `84` §5.3 names."""
    assert set(_values(run, "term")) == {"Fall2024", "2023-2024Semester1"}
    assert set(_values(run, "subject")) == {"PHYS1401", "CHEM2100"}


def test_each_terms_own_spelling_survives_the_run(run):
    """§14.2: "The original spelling is preserved alongside the normalized
    identity." Asserted on a real run because `facts.date_facts` is the only writer
    and nothing between it and the database was hand-assembled here.

    The canonical form is what a folder is called and the raw is what the document
    printed; a person asked to confirm `2023-2024Semester1` is being asked about a
    word their syllabus never used, and this column is the only place the word they
    did use still exists.
    """
    assert _values(run, "term") == {
        "Fall2024": ["Fall 2024"],
        "2023-2024Semester1": ["2023-2024 Semester 1"],
    }


def test_the_two_calendars_do_not_merge_into_one_semester_level(run):
    """TWO `Semester` folders, and the level is the one the library binds
    `cycle_period` to.

    Read off `dimension_role` rather than off the labels, so a run that happened to
    put those two strings somewhere else in the tree cannot satisfy it.
    """
    semester = [node for node in _final_tree(run)
                if node["dimension_role"] == "cycle_period"]

    assert [node["dimension"] for node in semester] == ["term", "term"]
    assert sorted(node["display_label"] for node in semester) == [
        "2023-2024Semester1", "Fall2024"]


def test_each_course_sits_under_its_own_term(run):
    """The binding itself: the Semester level over each course is the term THAT
    COURSE's files carry.

    This is the assertion that would fail if the term were read off the group. Both
    courses are in one accepted group -- one per `--label` -- so a group-grain term
    is a disagreement, and the person loses both folders rather than getting the
    wrong one. Either way `CHEM2100` would not be under `2023-2024Semester1`.
    """
    nodes = _final_tree(run)
    by_id = {node["node_id"]: node for node in nodes}

    for _, _, course, _, term in COURSES:
        node = next(one for one in nodes if one["display_label"] == course)
        parent = by_id[node["parent_node_id"]]
        assert parent["display_label"] == term, (
            f"{course} was filed under {parent['display_label']!r} "
            f"rather than {term!r}")
        assert parent["dimension"] == "term"


def test_no_file_reaches_the_other_courses_term(run):
    """The discriminating twin. Keeping two folders is worth nothing if the files
    are split across them: a person would open `Fall2024` and find the chemistry
    course inside it, which is worse than one merged folder because it looks
    right."""
    nodes = _final_tree(run)
    by_id = {node["node_id"]: node for node in nodes}
    course_nodes = [one for one in nodes if one["dimension"] == "subject"]

    parents = {one["display_label"]: by_id[one["parent_node_id"]]["display_label"]
               for one in course_nodes}
    assert parents == {"PHYS1401": "Fall2024",
                       "CHEM2100": "2023-2024Semester1"}


# ----------------------------------------------------------------------------
# The defect this fixture used to stumble into, asked on purpose
# ----------------------------------------------------------------------------

#: The same syllabus with a THREE-digit section number, which is what `SYLLABUS`
#: above said until 2026-09-08. `Section 001` is a capitalised word and three digits,
#: so `cli._STRUCTURED` reads it, and `Instructor:` and `Syllabus` are two of §3.5's
#: five context terms -- so §3.5's rule validates it and the file carries TWO courses.
SECTIONED = """{code} Syllabus -- {term}

Instructor: R. Feynman. Section 001, {term}.
Meets Tuesday and Thursday.
"""


@pytest.fixture()
def sectioned_run(tmp_path):
    """The same corpus, the same run, one more digit in the section number."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for stem, code, _, term, _ in COURSES:
        for index in range(2):
            (corpus / f"{stem} syllabus {index}.txt").write_text(
                SECTIONED.format(code=code, term=term), encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--accept-groups",
              "--database", str(database)], out=out)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _local_model():
    """`test_local_model_fact_pass`'s ollama stub, loaded rather than copied.

    `test_r37_single_branch_is_byte_identical.py` sets the precedent for loading a
    sibling test module here, and the reason is the same one: a second stub would be
    a second answer to "what does a model reply look like", and the two would drift.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "local_model_fact_pass",
        Path(__file__).resolve().parent / "test_local_model_fact_pass.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a_second_code_shaped_reading_makes_the_rule_decline_and_ask_the_model(
        sectioned_run):
    """`104` R-37's principle one layer down, on a real run.

    A syllabus that prints `Section 001` on the same line as `Instructor:` gives
    §3.5's rule two candidates it cannot tell apart. Both clear the context check --
    the teaching words are beside both -- so neither the vocabulary nor the shape
    can separate them, and nothing but a list of department words could. THE RULE
    THEREFORE DECLINES, and says so: no `subject` fact, no `subject` value, and one
    `unresolved` row per candidate reading, each citing its own.

    **THIS TEST USED TO ASSERT THE OPPOSITE AND THE OPPOSITE WAS THE DEFECT.**
    Until 2026-09-08 `apply_rules` wrote one validated fact per matching
    observation, so this corpus carried two courses per file, §3.7 settled on
    neither, and the run produced both `term` folders and NO course folder -- a
    person losing the level the product is for, with no row saying why. Measured at
    `9cd52c6` with this text in capitals, the older uppercase-only recogniser did
    exactly the same thing, so the defect was never `104` R-146's; R-146 only made
    a title-case word readable, which is how often a real document reaches it.

    **THE DOCUMENT HAS NOT GONE QUIET.** `record_anchor_statements` carries its own
    `is_code` and runs before the rule pass, so the syllabus still STATES both
    readings and a neighbour still receives both lines as context. That is the same
    answer the rule is giving -- the model is shown both and judges -- and it is
    asserted below so nobody reads a decline as a silence.
    """
    subjects = list(sectioned_run.execute(
        "SELECT ff.field_key FROM file_facts ff WHERE ff.field_key = 'subject'"))
    assert subjects == []
    assert [row["canonical_value"] for row in sectioned_run.execute(
        'SELECT canonical_value FROM "values" WHERE field_key = ?', ("subject",))
    ] == []

    reasons = [row["reason"] for row in sectioned_run.execute(
        "SELECT reason FROM unresolved WHERE field_key = 'subject'")]
    assert reasons and set(reasons) == {"rule_found_several_values"}
    # Two candidates per file across four files, each cited by its own row.
    assert len(reasons) == 8

    # The term level is untouched: the loss was specific, not a run falling over.
    nodes = _final_tree(sectioned_run)
    assert sorted(one["display_label"] for one in nodes
                  if one["dimension_role"] == "cycle_period") == [
        "2023-2024Semester1", "Fall2024"]

    # And each syllabus still STATES both codes for its neighbours to be shown.
    stated = {row["canonical_code"] for row in sectioned_run.execute(
        "SELECT canonical_code FROM anchor_statements")}
    assert stated == {"PHYS1401", "CHEM2100", "Section 001"}


def _asked_about_the_declined_field(local):
    """`test_local_model_fact_pass`'s own answer, asked about `subject` first.

    **Why this exists, and it is `104` §18.2 gap 1 rather than a preference.** The
    sibling stub answers "one claim per allowed field: the first supported, the rest
    declined", and the field it supports is `allowed_vocabulary[0]`. That was
    `subject` until gap 1 merged (dcda7d0, `104` §18.14): `model_facts.open_question`
    now asks `pending ∪ settled`, so a level field a RULE holds is offered again WITH
    its conflict for the model to reconcile -- and on this corpus the rules hold
    `term` from the sectioned line, so `term` is now what the vocabulary lists first
    and what the stub answers. The model then says nothing about `subject`, which is
    the one field this test is about, and the test measured the stub's field-picking
    rule instead of the handoff.

    So the stub is TOLD which field to answer, and nothing else about it changes: it
    is the same function, given the same dossier with `subject` moved to the head of
    the vocabulary, so the value is still a span COPIED out of the released evidence,
    still cited to the reading it was copied from, and every other field still comes
    back declined. Reordering a closed list the model may propose from is not an
    answer -- the product hands the model all four either way.

    A real model would answer both, and that is exactly what a one-claim stub cannot
    do; `test_local_model_fact_pass` is where the stub's own rule is pinned, and this
    module has no business asserting through it.

    Takes the already-loaded module and closes over it: `_local_model` re-executes the
    sibling file, and the stub answers on the request thread, so looking it up per
    request would re-import it once per model call.
    """
    def answer(payload: str) -> str:
        head, dossier_text = payload.split(local.DOSSIER_FOLLOWS, 1)
        dossier = json.loads(dossier_text)
        fields = [field for field in dossier.get("allowed_vocabulary", ())
                  if isinstance(field, str)]
        if "subject" in fields:
            dossier["allowed_vocabulary"] = ["subject"] + [
                field for field in fields if field != "subject"]
        return local._answer_for(
            head + local.DOSSIER_FOLLOWS + json.dumps(dossier))

    return answer


def test_with_a_model_answering_the_declined_field_the_course_folder_comes_back(
        tmp_path, monkeypatch):
    """The other half of the handoff, and the half that makes it a repair.

    A rule that declines and stops would have traded one bad folder for no folder.
    It does not stop: the field is left absent from `file_facts`, so
    `model_facts.pending_fields_for` keeps `subject` PENDING, the file's own
    readings reach site A, and a model answering with the course it can see puts
    the level back. The model here is `test_local_model_fact_pass`'s ollama stub,
    which answers by COPYING a span out of the released evidence -- so what it says
    is the document's own words, exactly as a real model's accepted answer must be.

    Asserted on the shipped run rather than on the seam: the value arrives
    `llm_supported`, which `00`:42 makes weaker than a rule and overrulable by the
    person, and the course folder exists again in the tree the person is shown.

    **The stub is now asked about `subject` explicitly, and the reason is checked
    rather than asserted in prose.** `104` §18.2 gap 1 widened the question this file
    is asked -- see `_asked_about_the_declined_field` -- and the block below reads the
    dossier the run actually sent and pins the two things that made the old fixture
    stop measuring the handoff: `term` is in the offered vocabulary although a rule
    settled it, and it is offered carrying a conflict. If gap 1 is ever reverted those
    two lines fail and the reordering above becomes dead weight that says so, rather
    than a silent crutch.
    """
    local = _local_model()
    monkeypatch.setenv(local.LOCAL_MODEL_NAME, local.MODEL_ID)
    with local.StubOllama(answer=_asked_about_the_declined_field(local)) as stub:
        monkeypatch.setenv(local.LOCAL_BASE_URL_NAME, stub.base_url)
        holder = tmp_path / "holder"
        corpus = holder / "corpus"
        corpus.mkdir(parents=True)
        # NAMED AFTER THE COURSE, which is what makes this a test of the handoff
        # and not of the stub. `test_local_model_fact_pass._corpus`'s own docstring
        # records that its corpus releases the file's NAME to the model and that
        # the stub answers by copying a span out of what it was released; with the
        # neutral names this module's other fixtures use, the stub answers
        # `phys syllabus` and the question of whether a model's answer can rebuild
        # the level is never reached. A person whose syllabus file is called after
        # its course is also the ordinary case.
        # ONE MORE LINE PER FILE, and it is not decoration. `84` §5.3's failure mode
        # in this module's own words: two files whose bytes are identical share a
        # content hash and therefore a call-cache slot, so the model is asked ONCE,
        # one of the pair carries the answer, and the level does not settle. The
        # test then fails for a reason that has nothing to do with what it asks.
        for _stem, code, _, term, _ in COURSES:
            for index in range(2):
                (corpus / f"{code} syllabus {index}.txt").write_text(
                    SECTIONED.format(code=code, term=term)
                    + f"Week {index + 1} reading.\n", encoding="utf-8")
        database = holder / "plan.sqlite"
        out = io.StringIO()
        cli.main([str(corpus), "--situation", "academic.coursework",
                  "--label", "Coursework", "--user", "jy",
                  "--accept-groups",
                  "--database", str(database)], out=out)

    # `104` §18.2 gap 1, read off the question the run actually asked. A settled
    # LEVEL field is offered again and it is offered WITH its flag, so `term` -- which
    # the rules answered from the sectioned line -- is in the vocabulary and carries a
    # conflict. This is what puts a field other than `subject` at the head of the list
    # and why the stub above is told which field to answer.
    asked = [local.dossier_in(prompt) for prompt in stub.prompts()
             if local.DOSSIER_FOLLOWS in prompt]
    a_fact = [one for one in asked if one.get("call_site") == cli.A_FACT]
    assert a_fact, "site A was never asked, so this proves nothing"
    for dossier in a_fact:
        assert "subject" in dossier["allowed_vocabulary"]
        assert "term" in dossier["allowed_vocabulary"], (
            "a rule-settled level field is no longer offered -- gap 1 was reverted "
            "and the reordering in `_asked_about_the_declined_field` is now dead")
        assert any(conflict["kind"] == "term"
                   for conflict in dossier["conflicts"]), dossier["conflicts"]

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        # The rule still declined -- that is the premise, and if it stopped
        # declining this test would be measuring the old behaviour.
        reasons = {row["reason"] for row in conn.execute(
            "SELECT DISTINCT reason FROM unresolved WHERE field_key = 'subject'")}
        assert "rule_found_several_values" in reasons, reasons

        # And the model was asked, and answered, and the answer is a subject fact
        # at the strength a model's answer carries.
        answered = [(row["canonical_value"], row["reliability_state"])
                    for row in conn.execute(
                        "SELECT v.canonical_value, ff.reliability_state "
                        "FROM file_facts ff "
                        'JOIN "values" v USING (value_id) '
                        "WHERE ff.field_key = 'subject' AND ff.active")]
        assert answered, "the model was never asked, so this proves nothing"
        assert {state for _value, state in answered} == {"llm_supported"}

        assert {value for value, _state in answered} == {"PHYS1401", "CHEM2100"}

        courses = sorted(one["display_label"] for one in _final_tree(conn)
                         if one["dimension"] == "subject")
        assert courses == ["CHEM2100", "PHYS1401"], "the course level did not come back"
    finally:
        conn.close()

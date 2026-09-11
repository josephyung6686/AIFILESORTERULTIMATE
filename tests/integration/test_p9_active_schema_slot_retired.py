# tests/integration/test_p9_active_schema_slot_retired.py
"""R-09, closed by measurement rather than by the fix the register names.

**The register entry said the wrong thing and the run says so.** `104` §4.1 R-09
reads: *"P9 `active_schema_for` is a hand-kept tuple; a model fact outside four
fields never seeds a group"*, and `104` §7 Phase 1 step 5 asked for the tuple to be
derived from the library's `role_bindings`. Two measurements taken before anything
was built say the sentence has two halves and neither holds.

**Half one: the tuple was not four fields.** `fd68cb6` emptied `DIRECT_SLOTS`, so
the literal in `cli.run` --

    tuple(slot.field_key for slot in DIRECT_SLOTS.slots)
        + (TERM_FIELD, MEDIA_TYPE_FIELD, WORK_TYPE_FIELD)

-- evaluated to `('term', 'media_type', 'work_type')`. Three fields, and the two it
had lost were `school` and `subject`, which is exactly where `104` R-10's 22
`llm_supported` facts landed (20 `school`, 2 `subject`).

**Half two: nothing read it.** `active_schema_for` had no caller anywhere in `src/`.
`grouping.dossier._require_knowledge` checked that it was callable and
`assemble_group_dossier` never invoked it, which is the shape `104` §14.2 records
for `signal_evaluator_for`. Measured before deleting it: with the three P9 suites
that supply the slot patched to hand in

    lambda *_a, **_k: (_ for _ in ()).throw(AssertionError(...))

**57 of 57 tests passed** (`tests/p9/test_p9_pipeline.py`,
`tests/p9/test_p9_dossier.py`, `tests/integration/test_p9_p8_group_seam.py`). A
callable that raises on any call cannot be called.

**So what does decide whether a fact seeds a group?** `grouping.seeds.ANCHOR_STATES`
-- `reliability_state in {direct, validated}` -- and it is field-INDEPENDENT. A model
fact is `llm_supported` and never seeds a group whatever the schema says, which
`seeds.py` defends from `00`:42 in its own words: letting one anchor "lets the model
confirm its own earlier guess". Deriving the dead tuple from the library would have
produced a correct value that still changed nothing, and wiring it into the seed path
to give it a purpose would have widened the anchor bar behind a schema fix -- a design
ruling, not a wiring one, and the lead holds it until the A glossary is ratified and
site B is wired.

The slot is therefore RETIRED, not derived. What replaces it is this file.
"""
from __future__ import annotations

import dataclasses
import inspect
import io
import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

_SRC = pathlib.Path(cli.__file__).resolve().parent


def test_no_module_under_src_still_names_the_slot_in_code():
    """The whole of the deletion, checked where a re-introduction would appear.

    A grep and not an import, because the failure this guards against is a new
    caller in a module nothing here imports.

    COMMENT LINES ARE EXEMPT AND DELIBERATELY SO. Three modules keep a note where
    the slot stood, saying what it was and why it went, which is how the next
    reader of `104` R-09 finds the measurement instead of re-adding the field. A
    note is not a caller; a line of code is.
    """
    offenders = [
        f"{path.relative_to(_SRC)}:{number}: {line.strip()}"
        for path in sorted(_SRC.rglob("*.py"))
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1)
        if ("active_schema_for" in line or "ActiveSchemaFor" in line)
        and not line.lstrip().startswith("#")
    ]
    assert offenders == [], offenders


def test_the_dossier_assembly_no_longer_takes_it():
    from grouping.dossier import assemble_group_dossier

    parameters = inspect.signature(assemble_group_dossier).parameters
    assert "active_schema_for" not in parameters
    # The two that stayed, and the reason they did: both are CALLED.
    # `classification_store` resolves a handling class for every file in the graph
    # and `signal_evaluator_for` is P9's own unresolved seam (`104` §14.2), which
    # this deletion is not authorised to touch.
    assert parameters["classification_store"].default is inspect.Parameter.empty
    assert "signal_evaluator_for" in parameters


def test_the_knowledge_bundle_no_longer_carries_it():
    from grouping.pipeline import GroupingKnowledge

    names = {item.name for item in dataclasses.fields(GroupingKnowledge)}
    assert "active_schema_for" not in names
    assert {"retrieval", "signal_evaluator_for", "classification_store",
            "conflicts_for", "duplicate_or_version"} <= names


def test_a_run_still_forms_the_same_group_without_the_slot(tmp_path):
    """Execute, then assert. The number is the one measured before the deletion.

    A three-file corpus that agrees on everything (the shape
    `test_cli_agreeing_corpus` uses) produced **2 rows in `groups`**, one of them
    `proposed_basis='subject=PHYS1401'` at state `supported`, with the slot present
    and hand-kept. It produces the same two with the slot gone, which is what
    "nothing consumed it" means in the live command rather than in a unit fixture.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 - Introduction to Mechanics\nFall 2024 Syllabus\n\n"
        "Instructor: Professor R. Villanueva\n"
        "Office hours: Wednesday 3:00-5:00 p.m.\nCredits: 3\n"
        "Lecture: Tuesday and Thursday 10:10-11:25 a.m.\n\nCOURSE DESCRIPTION\n"
        "Kinematics, Newton's laws, work and energy, momentum, rotational motion.\n\n"
        "GRADING\nProblem sets 30%. Midterm 30%. Final examination 40%.\n"
        "Readings are assigned from the course textbook each week.\n")
    (corpus / "PHYS 1401 lecture 08.txt").write_text(
        "PHYS 1401 - Lecture 08: Work and Energy\nFall 2024\n"
        "Professor R. Villanueva\n\n"
        "Lecture notes for the eighth meeting of the course.\n\n"
        "The work done by a constant force is the dot product of force and "
        "displacement.\n"
        "Worked examples are drawn from the assigned reading for this seminar.\n")
    (corpus / "PHYS 1401 problem set 3.txt").write_text(
        "PHYS 1401 - Problem Set 3\nFall 2024\n"
        "Due: Thursday October 17, 2024 at the start of lecture\n"
        "Professor R. Villanueva\n\n"
        "1. A block of mass 2.0 kg slides down a frictionless incline.\n"
        "This assignment is graded coursework for the course.\n")

    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "PHYS 1401", "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite")], out=io.StringIO())

    conn = sqlite3.connect(corpus.parent / "plan.sqlite")
    conn.row_factory = sqlite3.Row
    rows = [dict(row) for row in conn.execute(
        "SELECT proposed_basis, state FROM groups ORDER BY group_id")]
    conn.close()

    assert len(rows) == 2, rows
    assert {"subject=PHYS1401"} <= {row["proposed_basis"] for row in rows}, rows
    assert {row["state"] for row in rows} == {"supported"}, rows


def test_what_actually_bars_a_model_fact_from_seeding_is_the_state_bar():
    """The mechanism R-09 named, stated where the next reader will look for it.

    Field-independent, so no schema derivation could have changed it. Pinned here
    as well as in `tests/p9/test_p9_connections.py` because that file's version
    reads as a P6/P9 vocabulary agreement, and this one records WHY the schema slot
    was not the lever.
    """
    from facts.states import LLM_SUPPORTED
    from grouping.seeds import ANCHOR_STATES

    assert LLM_SUPPORTED not in ANCHOR_STATES
    assert ANCHOR_STATES == frozenset({"direct", "validated"})


# --- the slot that STAYED and is still answered with nothing ----------------------


@pytest.mark.xfail(strict=True, reason=(
    "OWNER'S WORD OWED, AND IT IS A FIELD SET. `cli.py`'s composition root answers "
    "`conflicts_for` with `lambda file_ids: ()`, so three things nothing else can "
    "reach are dead in every real run: `Group.conflicts` and `Membership.conflicts` "
    "are empty on every stored row, site B's dossier carries `conflicts=()` (which "
    "is what makes `llm_harness/group_validation.py`'s target-institution check "
    "unreachable from P9 -- `grouping/p8_seam.py`'s own comment says so), and SR4, "
    "the stop rule for irreconcilable facts, can never fire. The MECHANISM is "
    "entirely built and tested against an injected oracle on both sides; what is "
    "missing is the one answer P9 may not author. `00`:63 names the stop rule's "
    "field set in the design's own words -- 'when members carry irreconcilable "
    "COURSE, INSTITUTION, PROJECT, TERM, or PURPOSE facts' -- and those five words "
    "are not P6 field keys or library role refs. They have to be named as role refs "
    "(the library's own vocabulary: `holder_institution`, `cycle_period`, "
    "`subject_anchor`, `artifact_kind`, ...), because the reader then resolves them "
    "to field keys through the applicability row's `role_bindings` exactly as "
    "`production.group_level_fields_for` resolves `GROUP_LEVEL_ROLES`. It CANNOT be "
    "every field: `00`:112's own packet mixes an essay, a checklist, a screenshot "
    "and a transcript, so a reader that fired on `artifact_kind` would stop every "
    "real packet from forming, and choosing which of the library's roles those five "
    "words mean is a deciding word list P9 does not own. Once the owner names them, "
    "the reader is one query over `file_facts` joined to `values` -- the same read "
    "`cli.evidence_for` makes -- grouped by field over the member file ids, one "
    "`Conflict(kind=<field key>, competing_values=..., file_ids=...)` per field "
    "holding two or more canonical values among P9's own `ANCHOR_STATES`, and one "
    "line at `cli.py`'s `conflicts_for=`."))
def test_the_conflicts_oracle_is_answered_by_the_live_run(tmp_path):
    """The composition root supplies a REAL conflict reader, not an empty tuple.

    Read off the run's own wiring rather than off a fixture, because a fixture can
    pass its own oracle and every P9 test does -- which is exactly how a slot stays
    green for a year while the product answers it with nothing.
    """
    import cli

    source = pathlib.Path(inspect.getsourcefile(cli)).read_text(encoding="utf-8")
    assert "conflicts_for=lambda file_ids: ()" not in source

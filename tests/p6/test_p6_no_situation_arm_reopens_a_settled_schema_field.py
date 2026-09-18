# tests/p6/test_p6_no_situation_arm_reopens_a_settled_schema_field.py
"""The no-situation arm asks a rule-settled SCHEMA field again, with its flag.

**THE INVARIANT.** A file whose SCHEMA the judge named but whose SITUATION is open is
offered EVERY field its schema declares and no other schema's (`tests/integration/
test_each_file_is_filed_under_its_own_situation.py`, `test_a_silent_file_is_asked_
and_filed_under_one_situation.py`). `104` §18.2 gap 1 adds: a field the rules
settled is asked AGAIN, flagged, never dropped -- "the field that decides where the
file goes was decided by a pattern, silently" is the failure it ends.

**HOW IT BROKE, 18 Sep 2026.** The stage hands `open_question` the settled fields
that are LEVELS of the run's situation (`settled ∩ folder_levels`), so an anchor-only
`school` can never re-enter through the settled half. With no situation there are no
levels, the intersection is empty, and every rule-settled field vanished from the flat
question. Nothing noticed until `106` Phase 6.2 gave `research` a rule-settled field:
`cover letter` is a shipped `research` term, so a silent file of that name carries a
`validated` `artifact_type` and was asked seven of its schema's eight fields.

**AND THE FIRST FIX WAS TOO WIDE.** Re-opening the WHOLE settled set put `work_type`
-- settled on the same file by the same filename, corpus-wide, by `_rule_stage` --
into a research file's question, and the integration test that says a research file
is never asked a coursework field went red. With no situation the settled half is the
settled fields the SCHEMA DECLARES: the schema's own question, which is what the
flat arm is. `open_question`'s `None` arm still strips the group-level fields, so the
withdrawn per-file `school` question (`00` amendment 15) stays withdrawn -- that arm
is pinned by `test_p6_no_situation_arm_withholds_group_levels.py` and is not touched.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_harness.records import FolderLevel  # noqa: E402
from model_facts import open_question, settled_half_of_the_question  # noqa: E402

RESEARCH = ("project", "stage", "artifact_type", "lab", "venue", "institution")


def test_with_no_situation_a_settled_field_the_schema_declares_is_re_opened():
    """SABOTAGE: `folder_levels or ()` -- the intersection with nothing is nothing,
    and a rule-settled `artifact_type` is asked of no model."""
    assert settled_half_of_the_question(
        ("artifact_type",), None, RESEARCH) == ("artifact_type",)


def test_with_no_situation_a_settled_field_another_schema_declares_stays_closed():
    """`cover letter` settles `work_type` on the same file. SABOTAGE: return
    `settled` whole in the `None` state -- a research file is asked a coursework
    field, which `test_a_silent_file_is_asked_and_filed_under_one_situation.py`
    forbids by name."""
    assert settled_half_of_the_question(
        ("work_type", "artifact_type"), None, RESEARCH) == ("artifact_type",)


def test_a_bundle_not_told_its_schema_re_opens_nothing_in_that_arm():
    """The default is empty, like `group_level_fields`: the arm behaves as it did
    before 18 Sep for a caller that has not been told the schema."""
    assert settled_half_of_the_question(("artifact_type",), None) == ()


def test_with_a_situation_only_its_levels_are_re_opened():
    """`104` R-131: a settled `school` that is not a level of the run's situation is
    not re-opened through the settled half, and the schema's fields play no part.
    SABOTAGE: intersect with `schema_fields` in both states."""
    levels = (FolderLevel(field="subject", label="Course", requirement="required"),
              FolderLevel(field="work_type", label="Kind", requirement="required"))
    assert settled_half_of_the_question(
        ("school", "work_type", "subject"), levels,
        ("school", "subject", "work_type", "term")) == ("work_type", "subject")


def test_the_flat_question_carries_the_re_opened_field_and_still_withholds_school():
    """End to end through `open_question`'s `None` arm: the settled schema field is
    in the vocabulary, the group-level field is not."""
    vocabulary, levels = open_question(
        pending=("project", "stage", "venue"),
        folder_levels=None,
        settled=settled_half_of_the_question(
            ("artifact_type", "school"), None, (*RESEARCH, "school")),
        group_level=("school",))
    assert "artifact_type" in vocabulary
    assert "school" not in vocabulary
    assert levels == ()

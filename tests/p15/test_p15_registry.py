# tests/p15/test_p15_registry.py
"""§21's first obligation: the question KINDS are enumerable, and each names its reader.

`66` §21:665 lists nine things the structural-question system owes, and the first
is "a registry of questions". `triggers.py` argues -- correctly -- that no QUESTION
may be written down: each is derived from a blocked decision in a specific run, and
a written-down question is the "generic list of questions such as 'What do you do?'"
§12 rejects by name.

That argument is about questions. It is not about KINDS. §21's very next sentence is
"Questions must be wired into those mechanisms intentionally", and until this module
existed nothing could enumerate the kinds, so nothing could assert that each kind has
a mechanism that reads it. A consequence with no reader is a question asked for no
reason, which `records.py` already names as the failure to avoid.

Every test below is therefore a RATCHET over the shipped kinds rather than a check of
one value: it fails the day a consequence is added without the reader that consumes it.
"""
from __future__ import annotations

import dataclasses

import pytest

from questions.records import QuestionOption
from questions.registry import (
    QUESTION_KINDS, KindNotPermitted, QuestionKind, kind_of,
)
from questions.triggers import (
    NestingChoice, question_for_nesting, question_for_tied_reading,
)
from questions.vocabulary import SCOPES


def test_every_question_kind_names_the_consequence_that_reads_it():
    """§21's ninth obligation, made checkable by §21's first.

    For each kind: the consequence it may set is a real field of `QuestionOption`,
    and the reader is a callable that exists. Neither half is worth anything alone
    -- a field with no reader is an unwired consequence, and a reader for a field
    that does not exist is a mechanism nothing can reach.
    """
    assert QUESTION_KINDS, "a registry with no kinds asserts nothing"
    option_fields = {field.name for field in dataclasses.fields(QuestionOption)}
    for kind in QUESTION_KINDS:
        assert kind.consequence_field in option_fields, (
            f"{kind.kind_id} sets {kind.consequence_field!r}, which is not a field "
            f"of QuestionOption")
        assert callable(kind.reader), f"{kind.kind_id} has no reader"
        assert kind.scope_kind in SCOPES


def test_every_consequence_an_option_can_carry_belongs_to_a_registered_kind():
    """The ratchet. It fails the day someone adds a consequence and no kind.

    `QuestionOption`'s fields beyond its own identity ARE §13's list of five
    permitted consequences. A field that no kind claims is a consequence that
    could be set by a question nobody can enumerate and read by nothing.
    """
    identity = {"option_id", "label"}
    consequences = {field.name for field in dataclasses.fields(QuestionOption)
                    if field.name not in identity}
    claimed = {kind.consequence_field for kind in QUESTION_KINDS}
    assert consequences == claimed, (
        f"unclaimed consequences: {sorted(consequences - claimed)}; "
        f"kinds claiming a field that no longer exists: {sorted(claimed - consequences)}")


def test_each_shipped_builder_produces_a_question_of_a_registered_kind():
    """The two builders `triggers.py` ships, resolved through the registry."""
    reading = question_for_tied_reading(
        subject_value="PHYS1401",
        tied_schema_ids=("academic", "legal"),
        file_count=1, evidence_refs=("obs:1",))
    nesting = question_for_nesting(
        branch_label="Coursework",
        choices=(NestingChoice(("subject",), "by subject", (), ()),
                 NestingChoice(("work_type",), "by work type", (), ())),
        file_count=1)
    for question in (reading, nesting):
        kind = kind_of(question.question_id)
        assert kind is not None, f"{question.question_id!r} belongs to no kind"
        assert question.scope.split(":", 1)[0] == kind.scope_kind


def test_a_kind_whose_consequence_has_no_reader_is_refused():
    """The negative twin. Delete the check and this test passes.

    A kind carrying `reader=None` is exactly the state §21 warns about: a
    consequence that a question may set and nothing consumes.
    """
    with pytest.raises(KindNotPermitted):
        QuestionKind(kind_id="orphan", scope_kind="corpus",
                     consequence_field="activates_schema", reader=None)


def test_a_kind_naming_a_consequence_that_is_not_an_option_field_is_refused():
    with pytest.raises(KindNotPermitted):
        QuestionKind(kind_id="ghost", scope_kind="corpus",
                     consequence_field="does_not_exist", reader=len)


def test_a_kind_with_a_scope_outside_the_closed_set_is_refused():
    from questions.vocabulary import OutOfVocabulary
    with pytest.raises(OutOfVocabulary):
        QuestionKind(kind_id="wide", scope_kind="everywhere",
                     consequence_field="activates_schema", reader=len)


def test_an_unregistered_question_id_resolves_to_no_kind():
    """`kind_of` reports absence rather than guessing the nearest kind."""
    assert kind_of("something.nobody:registered") is None

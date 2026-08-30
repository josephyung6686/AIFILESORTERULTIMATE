# tests/p15/test_p15_gates_held_shut.py
"""Two things `75` deliberately does NOT build, and the guards that keep them unbuilt.

A plan that says "we did not build X" is a sentence in a document. A test that fails
the day someone builds X is the same sentence, executable. `63` §0 G8 and
`tests/p10/test_p10_no_invention.py` already use this shape on this project, and
each guard below is paired with a SABOTAGE FIXTURE so that "the guard found nothing"
is distinguishable from "the guard cannot find anything".

**B3 -- `requires_review`.** §13 permits a structural answer five consequences and
the fifth is "require review". The only honest consumers are `REVIEW_ONLY`,
`MANDATORY_REVIEW` and P13's review queue, and P13 is not built. Shipping the field
now would be a consequence with no reader, which `records.py` names by name as "how
a question comes to be asked for no reason". **Delete this guard in the same commit
that adds P13's reader.**

**D4 -- free text becoming a schema.** `66` §16:547 requires that "'I'm a sound
engineer' must not silently activate an engineering or software-project schema
merely because the words are superficially similar", and `62` §D is an owner ruling
that overturns the rule-based matcher outright: "These should not just be directly
matched -- the LLM uses that information to judge... Nothing here should be built
until it arrives." A3 made raw wording storable. This guard is why storing it is
safe: nothing in `src/questions/` may read a person's wording and produce a schema.
"""
from __future__ import annotations

import ast
import dataclasses
import pathlib

import pytest

import questions
from questions.records import QuestionOption

SRC = pathlib.Path(questions.__file__).resolve().parent
MODULES = sorted(SRC.glob("*.py"))

#: Names that would make a person's own wording into a schema activation.
ACTIVATION_NAMES = frozenset({"activates_schema", "activated_schemas", "SCHEMA_IDS"})
WORDING_NAMES = frozenset({"raw_wording"})


def _identifiers(node: ast.AST) -> set[str]:
    """Every name this node mentions, however it mentions it.

    `ast.keyword` is here because the first run of this guard without it passed
    against the sabotage fixture below: `QuestionOption(..., activates_schema=...)`
    names the field as a KEYWORD ARGUMENT, which is neither a `Name` nor an
    `Attribute`, so the guard could not see the one construction it exists to
    forbid. That is exactly the failure the fixture is for.
    """
    out: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            out.add(child.id)
        elif isinstance(child, ast.Attribute):
            out.add(child.attr)
        elif isinstance(child, ast.keyword) and child.arg:
            out.add(child.arg)
        elif isinstance(child, ast.arg):
            out.add(child.arg)
        elif isinstance(child, ast.Constant) and isinstance(child.value, str):
            out.add(child.value)
    return out


def _functions_touching_both(source: str) -> list[str]:
    """Every function whose BODY reads wording and names an activation.

    Over the parsed AST and not a text search, for the reason
    `test_p10_no_invention.py` gives: a text search matches docstrings, and on this
    project that has produced a false result more than once -- including a guard
    whose own banned word appeared in its own docstring. Docstrings are `Constant`
    nodes here too, so they are stripped before the comparison.
    """
    offenders: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = list(node.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(
                body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
        seen: set[str] = _identifiers(node.args)
        for statement in body:
            seen |= _identifiers(statement)
        if seen & WORDING_NAMES and seen & ACTIVATION_NAMES:
            offenders.append(node.name)
    return offenders


# --- B3: §13's fifth consequence stays absent while nothing reads it ---------------


def test_no_question_option_requires_review_while_nothing_reads_it():
    """It fails the day someone adds the field. Delete it with P13's reader.

    `records.py` states the discipline: the unwired consequences are "absent rather
    than stubbed, because shipping a consequence that does nothing is how a question
    comes to be asked for no reason". P13's review queue is not started, so there is
    nothing for `requires_review` to require review OF.
    """
    fields = {field.name for field in dataclasses.fields(QuestionOption)}
    review_shaped = sorted(name for name in fields if "review" in name)
    assert review_shaped == [], (
        f"QuestionOption gained {review_shaped}. §13's fifth consequence is "
        "'require review', and its only honest readers are P13's review queue and "
        "the REVIEW_ONLY / MANDATORY_REVIEW policies. If P13 now exists, delete "
        "this test in the commit that adds the reader -- not before.")


def test_the_review_guard_can_see_a_review_field(monkeypatch):
    """The sabotage fixture. A guard that cannot fire is not a guard."""
    @dataclasses.dataclass(frozen=True)
    class SabotagedOption:
        option_id: str
        label: str
        requires_review: bool = False

    fields = {field.name for field in dataclasses.fields(SabotagedOption)}
    assert sorted(name for name in fields if "review" in name) == ["requires_review"]


# --- D4: nothing turns a person's words into a schema ------------------------------


def test_nothing_maps_free_text_to_a_schema_without_an_explicit_confirmation():
    """§16:547 and `62` §D, executable. It fails the day someone adds a mapping.

    The confirmation path that IS permitted goes the other way round: the person
    picks an option the product offered, and `activates_schema` is on that option.
    Wording never becomes an activation, in either direction, anywhere in P15.
    """
    offenders: dict[str, list[str]] = {}
    for module in MODULES:
        found = _functions_touching_both(module.read_text())
        if found:
            offenders[module.name] = found
    assert offenders == {}, (
        f"{offenders} reads a person's own wording and names a schema activation. "
        "§16:547: 'An unmatched answer must remain unmatched.' `62` §D is an owner "
        "ruling that this cannot be rule based and that fuller guidance is owed: "
        "'Nothing here should be built until it arrives.'")


SABOTAGE = '''
def match_role_to_schema(answer):
    """Innocuous docstring mentioning nothing at all."""
    words = answer.raw_wording.lower()
    if "engineer" in words:
        return QuestionOption("x", "X", activates_schema="software_project")
    return None
'''


def test_the_matcher_guard_fires_on_a_matcher():
    """The sabotage fixture: the exact function §16:547 forbids, and the guard
    must reject it. Without this, a guard whose identifier set was misspelled
    would pass forever and prove nothing."""
    assert _functions_touching_both(SABOTAGE) == ["match_role_to_schema"]


DOCSTRING_ONLY = '''
def explain_the_rule():
    """This function mentions raw_wording and activates_schema in prose only."""
    return None
'''


def test_the_matcher_guard_does_not_fire_on_prose():
    """The other half of the fixture. A guard that also rejects the DOCUMENTATION
    of the rule would make the rule undocumentable, and would be turned off."""
    assert _functions_touching_both(DOCSTRING_ONLY) == []

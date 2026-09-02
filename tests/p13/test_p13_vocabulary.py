"""Every closed vocabulary P13 publishes, both ways, and nowhere else.

The authoring brief's §11: a closed vocabulary is published as a `tuple` for
iteration and membership AND as one named constant per member, and every
consumer imports the named constant. A bare string in another module is a second
home for the vocabulary; an index is single-homed but couples the reader to the
tuple's ORDER, so reordering the tuple would change meanings with no test failing.

The pair at the bottom is the house pattern from `tests/p10/test_p10_no_invention.py`
:13-16: a guard is asserted against the real package AND against a deliberately
sabotaged module, so that "the guard found nothing" is distinguishable from "the
guard cannot find anything".
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

from database_agent.events import CORRECTION_SCOPES as P1_SCOPES

from review_surface import vocabulary as v
from review_surface.schema import _DDL


def test_the_twelve_surfaces_are_the_spec_s_twelve():
    assert v.SURFACES == (
        "placement", "group_plan", "residual_set", "residual_file", "canvas",
        "apply", "undo_conflict", "consent", "privacy_settings", "evaluation",
        "learning", "plan_version",
    )


def test_the_twenty_four_actions_are_the_spec_s_twenty_four():
    """Eighteen until 2026-09-02, when the owner approved six of §8.7's gestures.

    The name of this test carries the count deliberately: it was
    `test_the_eighteen_actions_are_the_spec_s_eighteen` and would have been a lie
    the moment there were twenty-four.
    """
    assert v.ACTIONS == (
        "accept", "accept_bulk", "change_destination",
        "return_to_accepted_group", "create_custom_folder", "mark_private",
        "defer", "leave_untouched", "reject", "edit_recommendation",
        "disable_suggestion_type", "refresh_plan", "approve_for_apply",
        "select_consent_option", "set_redaction", "adopt_version",
        "restore_version", "reset_learning",
        "exclude_from_packet", "rename", "merge", "split", "reorder",
        "set_refinement_disposition",
    )


def test_every_action_the_spec_prints_is_present():
    for name in ("accept", "accept_bulk", "change_destination",
                 "return_to_accepted_group", "create_custom_folder",
                 "mark_private", "defer", "leave_untouched", "reject",
                 "edit_recommendation", "disable_suggestion_type",
                 "refresh_plan", "approve_for_apply", "select_consent_option",
                 "set_redaction", "adopt_version", "restore_version",
                 "reset_learning", "exclude_from_packet", "rename", "merge",
                 "split", "reorder", "set_refinement_disposition"):
        assert name in v.ACTIONS, f"{name} is one of P13 SPEC's printed actions"


def test_the_four_approval_verdicts():
    assert v.VERDICTS == ("approved", "rejected", "deferred", "refresh_required")


def test_the_three_progress_states_and_three_sources():
    assert v.PROGRESS_STATES == ("completed", "deferred", "blocked")
    assert v.PROGRESS_SOURCES == ("P3.R5", "P4.extraction_runs", "P8")


def test_correction_scopes_are_p1_s_and_not_a_second_copy():
    """P1's writer validates against this tuple and P1's learning store reads
    against it. A scope one accepted and the other rejected would be storable
    and permanently unreadable."""
    assert v.CORRECTION_SCOPES is P1_SCOPES


#: The five closed vocabularies A1 publishes. Named here so the guard below and
#: the both-ways test agree on the list rather than each carrying its own.
CLOSED_VOCABULARIES = (
    "SURFACES", "ACTIONS", "VERDICTS", "PROGRESS_STATES", "PROGRESS_SOURCES")


def test_every_vocabulary_publishes_a_named_constant_per_member():
    """`74` §6 A1's named test. Brief §11: a bare string is a second home and an
    index is unreadable."""
    named = {value for name, value in vars(v).items()
             if name.isupper() and isinstance(value, str)}
    for tuple_name in CLOSED_VOCABULARIES:
        for member in getattr(v, tuple_name):
            assert member in named, (
                f"{member!r} in {tuple_name} has no named constant; consumers "
                "would have to write the literal or an index")


# --------------------------------------------------------------------------
# The guard, and its sabotage fixture. `74` §6 A1's negative twin.
# --------------------------------------------------------------------------

def _package_modules() -> list[tuple[pathlib.Path, ast.Module]]:
    import review_surface
    root = pathlib.Path(review_surface.__file__).resolve().parent
    return [(path, ast.parse(path.read_text()))
            for path in sorted(root.glob("*.py"))]


def _fake(source: str, name: str = "offender.py"):
    """One parsed module that is NOT on disk, for the negative half of a pair."""
    return [(pathlib.Path(name), ast.parse(source))]


#: Every value in every one of P13's five closed vocabularies. A module outside
#: `vocabulary.py` that binds a collection of these has respelled the vocabulary.
def _all_members() -> frozenset[str]:
    members: set[str] = set()
    for tuple_name in CLOSED_VOCABULARIES:
        members.update(getattr(v, tuple_name))
    return frozenset(members)


def _documentation_strings(tree: ast.Module) -> set[int]:
    """Every string that is a docstring or a bare expression statement.

    A text search matches comments and docstrings, and on this project that has
    produced a false result repeatedly -- including the guard whose own banned
    word appeared in its own docstring. So prose is excluded by NODE IDENTITY,
    not by a second regex.
    """
    documentation: set[int] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)):
            documentation.add(id(node.value))
    return documentation


def _schema_columns() -> frozenset[str]:
    """Every column P13's own DDL declares.

    A vocabulary member and a column name can be the same string and mean two
    different things: `plan_version` is both a SURFACE and a column on all three
    tables. `row["plan_version"]` is a column reference, so the guard must judge
    by ROLE, not by spelling -- narrowing it any other way would make the two
    drift apart, which is the thing the guard exists to stop.
    """
    return frozenset(re.findall(r"^\s{4}(\w+)\s+(?:TEXT|INTEGER)", _DDL,
                                re.MULTILINE))


def _column_reference_keys(tree: ast.Module) -> set[int]:
    """Every string constant used as a COLUMN KEY that names one of P13's columns.

    Two syntactic roles carry that meaning, and both are exempted by node
    identity rather than by a second regex:

    * a subscript key -- `row["plan_version"]` reads the column off a row;
    * a dict-literal key -- the `review presentation` event's explanation payload
      mirrors the row it is written beside, key for key.

    The exemption stays as narrow as it was. `plan_version` is both a SURFACE and
    a column on all three tables, so the guard must judge by ROLE; a dict key that
    is NOT one of P13's columns is still a respelling and is still caught, which
    the twin below asserts in both directions.
    """
    columns = _schema_columns()
    keys: set[int] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in columns):
            keys.add(id(node.slice))
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if (isinstance(key, ast.Constant)
                        and isinstance(key.value, str)
                        and key.value in columns):
                    keys.add(id(key))
    return keys


def _bare_vocabulary_bindings(trees, *, home="vocabulary.py"):
    """Modules spelling a vocabulary member as a bare string.

    Parsed, not grepped. The member's HOME is `vocabulary.py`; anywhere else the
    same string is a second home, and the two drift silently.
    """
    members = _all_members()
    offenders = []
    for path, tree in trees:
        if path.name == home:
            continue
        documentation = _documentation_strings(tree)
        columns = _column_reference_keys(tree)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Constant)
                    and isinstance(node.value, str)
                    and node.value in members
                    and id(node) not in documentation
                    and id(node) not in columns):
                offenders.append(f"{path.name}:{node.lineno} {node.value!r}")
    return offenders


def test_a_module_binding_a_bare_vocabulary_member_is_rejected():
    """`74` §6 A1's negative twin, with its sabotage fixture.

    The guard must REJECT a module that respells a vocabulary member as a bare
    string, and must find nothing in the real package. Asserting only the second
    half would pass just as well if `_all_members()` were empty.
    """
    assert _bare_vocabulary_bindings(_package_modules()) == []
    assert _bare_vocabulary_bindings(_fake('POLICIES = ("accept",)\n'))
    assert _bare_vocabulary_bindings(
        _fake('SURFACES = ["placement", "canvas"]\n'))
    assert _bare_vocabulary_bindings(_fake('if surface == "canvas": pass\n'))
    # And the exemption is real: `vocabulary.py` is where the strings live, so
    # dropping the exemption must report it and nothing else. An exemption
    # nobody re-checks is how a hole widens.
    without = {entry.split(":")[0]
               for entry in _bare_vocabulary_bindings(_package_modules(), home=None)}
    assert without == {"vocabulary.py"}, (
        f"the vocabulary's one home is meant to be vocabulary.py; got {without}")
    # The column exemption is real too, and narrow. A subscript key that is one
    # of P13's columns is a column reference; a subscript key that is NOT is
    # still a respelling and still caught.
    assert not _bare_vocabulary_bindings(_fake('x = row["plan_version"]\n'))
    assert _bare_vocabulary_bindings(_fake('x = table["canvas"]\n'))
    # The same narrowness for a dict-literal key. An event explanation payload
    # mirrors the row it is written beside, key for key, so its keys are column
    # references in the same sense; a key that is not a column is not.
    assert not _bare_vocabulary_bindings(_fake('x = {"plan_version": v}\n'))
    assert _bare_vocabulary_bindings(_fake('x = {"canvas": v}\n'))
    assert "plan_version" in _schema_columns()
    assert "canvas" not in _schema_columns()


def test_the_three_event_names_are_the_registered_ones():
    """P13 registers nothing: registration is a spec-level act with no run-time
    call, and all three names are already in P1's registry."""
    from database_agent.events import EVENT_TYPES
    for name in (v.EVENT_PRESENTATION, v.EVENT_ACTION_ROUTED, v.EVENT_APPROVAL):
        assert name in EVENT_TYPES, (
            f"{name!r} must already be registered; P13 registers nothing")


def test_check_accepts_a_member_and_names_the_vocabulary_on_a_miss():
    assert v.check("placement", v.SURFACES, name="surface") == "placement"
    with pytest.raises(v.OutOfVocabulary) as caught:
        v.check("dashboard", v.SURFACES, name="surface")
    assert "surface" in str(caught.value)
    assert "dashboard" in str(caught.value)


def test_untouched_protected_is_not_a_surface_and_not_an_action():
    """P13 SPEC:260-262 -- it carries no action at all, so it is not a surface
    either: a surface is a place a gesture can be made."""
    assert v.UNTOUCHED_PROTECTED not in v.SURFACES
    assert v.UNTOUCHED_PROTECTED not in v.ACTIONS

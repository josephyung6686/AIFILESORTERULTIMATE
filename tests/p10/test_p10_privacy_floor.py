"""P10 Amendment C — per-context privacy, entering the gate that already exists.

The problem it solves: `TemplateApplicability` had NO privacy field, so the only
way to ship one recipe at two exposures was to ship two definitions. That is why
there are 29 definitions where 21 recipes exist — eight of them differ in
nothing but exposure.

**What this amendment deliberately does NOT do.** The obvious fix is to give
applicability a privacy field and stop. `TemplateDefinition.sensitivity_policy_ref`
is what that looks like after the fact: it is declared, it is checked for being a
non-empty string in three places, it is copied out of JSON by the loader — and
NO GATE EVER RESOLVES IT. Its value could be `"policy.banana"` and every test in
this repository would still pass. A second field of that kind, added on purpose,
is worse than the first, which was at least an accident.

So the floor added here enters `merge_fragment_constraints` beside the fragments'
and the definition's, and C7 takes the strongest exactly as it already does. No
new reader, no new rule — the existing one, given one more input.

**Monotone in one direction only.** A row may RAISE the composition's floor and
may never lower it. C7's sentence is "the combined privacy is no weaker than any
included restriction", and a per-context row that could weaken a fragment's floor
would let the narrower context release material the broader one protects. This
is the same shape as a per-schema narrowing that may only subtract.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from tree_design.routing import evaluate_composition
from tree_design.templates import (
    FragmentRef,
    MalformedTemplateRecord,
    TemplateApplicability,
    merge_fragment_constraints,
)

from p10.test_p10_routing import (
    ALWAYS, KIND, RANK, SUBJECT, _catalogue, _context, _definition, _group, _row,
)

#: Two floors and their strength under `RANK`, which is the fixture's ordering:
#: `policy.public` is 0 and `policy.sensitive` is 1, so "sensitive" is STRONGER.
PUBLIC = "policy.public"
SENSITIVE = "policy.sensitive"


def _row_with_floor(applicability_id, schema, floor, role="artifact_kind",
                    field="work_type"):
    row = _row(applicability_id, "t.fixture", schema,
               [(role, field, "Assignment type")])
    return TemplateApplicability(
        **{**row.__dict__, "privacy_floor": floor})


def _compose(conn, rows, roles=("artifact_kind",), fragment=KIND,
             domains=("academic",), groups=None):
    definition = _definition(
        "t.fixture", (FragmentRef(fragment.fragment_id, 1),), roles)
    catalogue = _catalogue((SUBJECT, KIND), (definition,), rows)
    groups = groups or (_group("g1", domains[0], ("f1",)),)
    return evaluate_composition(
        conn, catalogue, _context(domains, groups), rows,
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)


# --------------------------------------------------------------------------
# The record.
# --------------------------------------------------------------------------

def test_an_applicability_row_may_state_its_own_privacy_floor():
    row = _row_with_floor("a.sensitive", "academic", SENSITIVE)
    assert row.privacy_floor == SENSITIVE


def test_a_row_that_states_no_floor_is_legal_and_means_it_adds_none():
    """`None` is a MARKER here, not a missing value. Most rows do not change the
    exposure of the recipe they bind, and forcing every author to restate the
    fragment's floor would make the common row carry a copy that can drift."""
    row = _row("a.plain", "t.fixture", "academic",
               [("artifact_kind", "work_type", "Assignment type")])
    assert row.privacy_floor is None


def test_a_floor_that_is_present_but_blank_is_refused():
    """The pair for the marker above: absent means "adds none", and blank means
    an author meant to say something and said nothing. They are different and
    the record refuses to treat the second as the first."""
    row = _row("a.blank", "t.fixture", "academic",
               [("artifact_kind", "work_type", "Assignment type")])
    with pytest.raises(MalformedTemplateRecord):
        TemplateApplicability(**{**row.__dict__, "privacy_floor": "   "})


# --------------------------------------------------------------------------
# The gate. This is the half that makes the field real.
# --------------------------------------------------------------------------

def test_a_stronger_row_floor_raises_the_compositions_floor(conn):
    """The fragment is `policy.public`; the row asks for `policy.sensitive`.
    C7 keeps the strongest included restriction, so the composition is
    sensitive."""
    candidate = _compose(conn, (_row_with_floor("a.s", "academic", SENSITIVE),))
    assert candidate.privacy_floor == SENSITIVE


def test_a_weaker_row_floor_does_not_lower_the_compositions_floor(conn):
    """THE discriminating twin, and the reason the pair is not optional.

    A composer that simply took the row's floor would pass the test above and
    fail here — it would let a per-context row release material the fragment it
    binds protects. Monotone upward only.
    """
    strict = KIND.__class__(**{**KIND.__dict__, "privacy_floor": SENSITIVE})
    definition = _definition(
        "t.fixture", (FragmentRef(strict.fragment_id, 1),), ("artifact_kind",))
    catalogue = _catalogue((SUBJECT, strict), (definition,),
                           (_row_with_floor("a.w", "academic", PUBLIC),))
    candidate = evaluate_composition(
        conn, catalogue, _context(("academic",), (_group("g1", "academic", ("f1",)),)),
        (_row_with_floor("a.w", "academic", PUBLIC),),
        privacy_rank=RANK, satisfies_purpose_profile=ALWAYS)
    assert candidate.privacy_floor == SENSITIVE


def test_a_row_with_no_floor_leaves_the_fragments_floor_untouched(conn):
    """The third leg: absent is not zero. A row stating nothing must not be read
    as a row asking for the weakest available floor."""
    candidate = _compose(conn, (_row("a.plain", "t.fixture", "academic",
                                     [("artifact_kind", "work_type",
                                       "Assignment type")]),))
    assert candidate.privacy_floor == PUBLIC


def test_the_strongest_of_several_rows_wins(conn):
    """Two contexts in one branch, two exposures. The composition takes the
    stronger, because it holds material from both."""
    rows = (_row_with_floor("a.pub", "academic", PUBLIC),
            _row_with_floor("a.sen", "research", SENSITIVE))
    groups = (_group("g1", "academic", ("f1",)),
              _group("g2", "research", ("f2",)))
    candidate = _compose(conn, rows, domains=("academic", "research"),
                         groups=groups)
    assert candidate.privacy_floor == SENSITIVE


# --------------------------------------------------------------------------
# Reachability. The field must reach the gate, not merely exist.
# --------------------------------------------------------------------------

def test_the_merge_accepts_applicability_floors_at_all():
    """The callee half of the seam, bound against the LIVE signature."""
    assert "applicability_floors" in inspect.signature(
        merge_fragment_constraints).parameters


def test_routing_actually_passes_the_row_floors_into_the_merge():
    """The caller half, and the guard the ruling required.

    A field can be declared, stored, loaded and even asserted on in a record
    test while never reaching a gate — that is precisely
    `sensitivity_policy_ref`. So this parses `routing.py` and asserts the
    `merge_fragment_constraints` CALL carries `applicability_floors`. Passing
    the field to the record is not the same as passing it to the gate.
    """
    source = inspect.getsource(__import__("tree_design.routing",
                                          fromlist=["routing"]))
    calls = [node for node in ast.walk(ast.parse(source))
             if isinstance(node, ast.Call)
             and getattr(node.func, "id", None) == "merge_fragment_constraints"]
    assert calls, "routing.py no longer calls the merge at all"
    assert all(any(kw.arg == "applicability_floors" for kw in call.keywords)
               for call in calls), (
        "a merge_fragment_constraints call in routing.py omits "
        "applicability_floors, so a row's floor never reaches C7")


def test_the_release_loader_drops_no_field_of_an_applicability_row():
    """The same technique that caught two dropped definition fields.

    `catalogue._applicability` rebuilds the row field by field from JSON, so a
    field added to the record and not to the loader is silently dropped and the
    row the composer sees is not the row the release shipped. Comparing field
    NAMES rather than a hand-written list is what makes this survive the next
    field.
    """
    import dataclasses

    from tree_design import catalogue

    source = inspect.getsource(catalogue._applicability)
    for field in dataclasses.fields(TemplateApplicability):
        assert f"{field.name}=" in source, (
            f"catalogue._applicability drops {field.name!r}; a release would "
            "ship a row the composer never sees")

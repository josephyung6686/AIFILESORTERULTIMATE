"""P11's closed sets, and the two ways a value can be another part's."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from placement import vocabulary as v

PLACEMENT_ROOT = Path(__file__).resolve().parents[2] / "src" / "placement"


def test_every_closed_set_has_one_named_constant_per_member():
    sets = {
        "OUTCOMES": v.OUTCOMES, "ORIGIN_STAGES": v.ORIGIN_STAGES,
        "SUBJECT_KINDS": v.SUBJECT_KINDS, "NODE_ROLES": v.NODE_ROLES,
        "RETURN_TARGET_KINDS": v.RETURN_TARGET_KINDS,
        "MARKED_STATES": v.MARKED_STATES, "EVIDENCE_TYPES": v.EVIDENCE_TYPES,
        "CONFIDENCE_CLASSES": v.CONFIDENCE_CLASSES,
        "MEETS_MARGIN_VALUES": v.MEETS_MARGIN_VALUES, "VERDICTS": v.VERDICTS,
        "ABSTENTION_REASONS": v.ABSTENTION_REASONS,
        "MODEL_ELIGIBILITY": v.MODEL_ELIGIBILITY,
        "REVIEW_POLICIES": v.REVIEW_POLICIES, "SET_CHOICES": v.SET_CHOICES,
        "OUTLIER_ROUTES": v.OUTLIER_ROUTES, "STAGE_IDS": v.STAGE_IDS,
        "REVIEW_SURFACES": v.REVIEW_SURFACES,
        "REVIEW_ACTIONS": v.REVIEW_ACTIONS,
    }
    bound = {name: value for name, value in vars(v).items()
             if isinstance(value, str) and not name.startswith("_")}
    for set_name, members in sets.items():
        assert len(set(members)) == len(members), set_name
        for member in members:
            assert member in bound.values(), (set_name, member)


def test_p11_outcomes_are_exactly_the_seven_p2_already_refuses():
    # P2 enumerated P11's record outcomes before P11 existed, to refuse them in
    # the envelope. Two lists of one vocabulary is the drift this pins shut.
    from eval_harness.stage_output import _FOREIGN_OUTCOMES
    assert set(v.OUTCOMES) == set(_FOREIGN_OUTCOMES)
    assert len(v.OUTCOMES) == 7


def test_the_four_colliding_spellings_stay_equal_to_p8s():
    # Same string, different axis: P8's are dispositions and actions, P11's are
    # outcomes. They are not imported, so a change on either side must break here.
    from llm_harness import vocabulary as p8
    assert v.RETURN_TO_PLACEMENT == p8.RETURN_TO_PLACEMENT
    assert v.LEAVE_IN_PLACE == p8.LEAVE_IN_PLACE
    assert v.ABSTAIN == p8.ABSTAIN
    assert v.MARK_REVIEW_LATER == p8.MARK_REVIEW_LATER


def test_the_verdict_vocabulary_is_p8s_object_and_not_a_copy():
    from llm_harness.vocabulary import OUTCOMES as P8_OUTCOMES
    assert v.VERDICTS is P8_OUTCOMES


def test_evidence_types_are_the_live_spellings_not_the_specs():
    # SPEC:335-336 hyphenates `user-confirmed` and `llm-supported`; the live
    # reliability states are snake_case and P11 re-spells neither owner.
    from evidence_shape.vocabulary import RELIABILITY_STATES
    from llm_harness.vocabulary import CONTEXT_SUPPORTED
    dropped = v.DROPPED_RELIABILITY_STATE
    assert dropped == "rejected"
    assert set(v.EVIDENCE_TYPES) == (set(RELIABILITY_STATES) - {dropped}) | {
        CONTEXT_SUPPORTED,
    }
    assert dropped not in v.EVIDENCE_TYPES


def _owned_values() -> set[str]:
    """Every value another part owns the spelling of.

    MINOR 6: "P10 owns the tree, so P10 names its node kinds. P11 carries these
    verbatim and publishes no parallel vocabulary." P10 ships now, so its five
    closed tree sets belong here beside P8's two -- this test read only P8's
    until today, which is why `groups.py` could hold its own spelling of §6.9's
    four shared-material policies for as long as it did.

    The sets are named one by one rather than swept from the module.
    `tree_design.vocabulary` also publishes P1's correction scopes and P13's
    action names, which are not P10's to own and which P11 legitimately spells on
    its own axes.
    """
    from llm_harness.vocabulary import RESIDUAL_ACTIONS
    from llm_harness.vocabulary import OUTCOMES as P8_OUTCOMES
    from tree_design.vocabulary import (
        BRANCH_BEARING_SHARED_POLICIES, NODE_ROLES, NODE_TYPES,
        RESIDUAL_DISPOSITIONS, SHARED_MATERIAL_POLICIES,
    )
    return (set(P8_OUTCOMES) | set(RESIDUAL_ACTIONS) | set(NODE_ROLES)
            | set(NODE_TYPES) | set(RESIDUAL_DISPOSITIONS)
            | set(SHARED_MATERIAL_POLICIES)
            | set(BRANCH_BEARING_SHARED_POLICIES))


def _p11_field_names() -> set[str]:
    """Every field name P11 publishes on a record.

    This is the set that makes the key exemption below safe. A string in
    `body["residual"]` is a FIELD NAME that happens to share a spelling with one
    of P10's node kinds; a string like `"mark_review_later"` used as a dict key is
    not a field of anything, so reading it as one would exempt exactly the place a
    respelling hides -- the KEYS of a mapping over another part's closed set.
    That hole was real: `residual.ACTION_OUTCOME` is keyed on P8's eight residual
    actions, and a literal respelling of one of them passed this guard.
    """
    import dataclasses

    import placement.groups as groups
    import placement.index as index
    import placement.pipeline as pipeline
    import placement.records as records
    import placement.residual as residual
    import placement.retrieval as retrieval

    names: set[str] = set()
    for module in (records, index, residual, groups, retrieval, pipeline):
        for value in vars(module).values():
            if isinstance(value, type) and dataclasses.is_dataclass(value):
                names |= {f.name for f in dataclasses.fields(value)}
    return names


def _borrowed_value_literals(tree: ast.AST, owned: set[str]) -> list[tuple[int, str]]:
    """String literals in a VALUE position that spell a value another part owns.

    By AST over string constants, because a text search matches docstrings. But
    not over every constant: a subscript or dict key that names a PUBLISHED FIELD
    is a field read and not a spelling. A key that is not a field name of any P11
    record gets no exemption, because a mapping keyed on another part's closed set
    is precisely where a second spelling hides.
    """
    fields = _p11_field_names()
    identifiers = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and node.slice.value in fields):
            identifiers.add(id(node.slice))
        if isinstance(node, ast.Dict):
            identifiers.update(id(key) for key in node.keys
                               if isinstance(key, ast.Constant)
                               and key.value in fields)
    return [
        (node.lineno, node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and node.value in owned and id(node) not in identifiers
    ]


def test_the_boundary_check_reads_values_and_not_field_names():
    # The negative twin, and the reason this guard can be trusted when it stays
    # silent. A check that flagged `body["residual"]` would report a defect on
    # every module that reads a record field, and one that flagged nothing would
    # report a clean boundary on a module that redefined P10's whole vocabulary.
    # `residual` IS a published field of `PlacementDecision`, so it is exempt as a
    # key; `shared-branch` is not a field of anything, so it is not.
    owned = {"residual", "shared-branch"}
    borrowed = _borrowed_value_literals(ast.parse(
        'SHARED_BRANCH = "shared-branch"\n'
        'value = body["residual"]\n'
        'mapping = {"residual": 1}\n'), owned)
    assert borrowed == [(1, "shared-branch")]


def test_a_key_that_names_no_published_field_gets_no_exemption():
    # The half that was missing, and the reason `residual.ACTION_OUTCOME` could
    # have carried a respelling of one of P8's eight actions unnoticed. A dict
    # keyed on another part's closed set is a mapping over VALUES, not a record.
    owned = {"mark_review_later"}
    borrowed = _borrowed_value_literals(
        ast.parse('ACTION_OUTCOME = {"mark_review_later": X}\n'), owned)
    assert borrowed == [(1, "mark_review_later")]


def test_no_placement_module_spells_a_value_another_part_owns():
    owned = _owned_values()
    offenders = []
    for path in sorted(PLACEMENT_ROOT.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        offenders.extend((path.name, lineno, value) for lineno, value
                         in _borrowed_value_literals(tree, owned))
    assert offenders == []


def test_check_names_the_set_and_never_the_nearest_match():
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("plase", v.OUTCOMES, name="outcome")
    assert "place" not in str(excinfo.value)
    assert str(len(v.OUTCOMES)) in str(excinfo.value)


def test_p11s_node_vocabulary_is_p10s_objects_and_not_a_second_spelling():
    """MINOR 6 for the node vocabulary, by identity, as `groups.py` now is.

    `placement/vocabulary.py` wrote the promise itself: *"P10 is unbuilt, so the
    values are spelled here from P10's SPEC and this module is the one home until
    P10 publishes them, at which point this becomes a re-export."* P10 publishes
    them now, so the re-export is due.

    Identity and not equality. All fifteen values agree today; three of them are
    closed TUPLES, and a tuple that merely agrees is one P10 edit away from
    disagreeing -- at which point `index.py` would refuse a node role P10 had just
    added, and the refusal would read as a malformed tree rather than as two
    parts holding different lists.

    The local NAMES stay. P11 has its own `RESIDUAL` origin stage, its own
    `LEAVE_IN_PLACE` outcome and its own `PROTECTED` marked state, all on
    different axes from P10's node kinds, so `RESIDUAL_ROLE`,
    `LEAVE_IN_PLACE_DISPOSITION` and `PROTECTED_NODE` are what keeps a reader of
    one axis from reaching for the other's constant. A distinct name bound to
    P10's object is carrying; a distinct name bound to a fresh string is the
    parallel vocabulary MINOR 6 forbids.
    """
    from tree_design import vocabulary as p10

    # The twelve scalars are checked by AST and NOT by `is`. Python interns short
    # string literals, so `RESIDUAL_ROLE = "residual"` -- a fresh spelling, the
    # exact thing MINOR 6 forbids -- satisfies `is p10.RESIDUAL` and this test
    # passed over it. Binding to a NAME rather than to a CONSTANT is the property
    # that actually distinguishes carrying from respelling, and interning cannot
    # defeat it.
    source = ast.parse(
        (PLACEMENT_ROOT / "vocabulary.py").read_text(encoding="utf-8"))
    bound_to = {}
    for node in source.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            targets = (node.targets if isinstance(node, ast.Assign)
                       else [node.target])
            for target in targets:
                if isinstance(target, ast.Name):
                    bound_to[target.id] = node.value

    assert v.NODE_ROLES is p10.NODE_ROLES
    assert v.DISPOSITIONS is p10.RESIDUAL_DISPOSITIONS
    assert v.NODE_TYPES is p10.NODE_TYPES
    for ours, theirs in (
            ("ORDINARY", "ORDINARY"), ("SCOPED_GENERAL", "SCOPED_GENERAL"),
            ("RESIDUAL_ROLE", "RESIDUAL"), ("SHARED_MATERIAL", "SHARED_MATERIAL"),
            ("PHYSICAL_DESTINATION", "PHYSICAL_DESTINATION"),
            ("REVIEW_ONLY", "REVIEW_ONLY"),
            ("LEAVE_IN_PLACE_DISPOSITION", "LEAVE_IN_PLACE"),
            ("EXISTING", "EXISTING"), ("PROPOSED", "PROPOSED"),
            ("USER_CREATED", "USER_CREATED"), ("PROTECTED_NODE", "PROTECTED"),
            ("IGNORED", "IGNORED")):
        assert getattr(v, ours) == getattr(p10, theirs), (ours, theirs)
        assert isinstance(bound_to[ours], ast.Name), (
            f"{ours} is bound to a literal, not to P10's name; string interning "
            f"makes an `is` check pass over exactly that")


def test_the_borrowed_node_names_stay_distinct_from_p11s_own_axes():
    # The negative twin of the re-export. Binding `RESIDUAL_ROLE` to P10's node
    # kind must not merge it with P11's `RESIDUAL` origin stage, nor
    # `PROTECTED_NODE` with the `PROTECTED` marked state: they are equal strings
    # on unrelated axes, and this module's opening rule is that a module reading
    # one must never reach for the other's constant.
    # The strings are shared; the axes are not, and each name lives on exactly
    # one of them. `RESIDUAL_ROLE` is a node kind and `RESIDUAL` an origin stage;
    # they spell the same word and belong to different closed sets.
    assert v.RESIDUAL_ROLE == v.RESIDUAL
    assert v.RESIDUAL_ROLE in v.NODE_ROLES and v.RESIDUAL not in v.NODE_TYPES
    assert v.RESIDUAL in v.ORIGIN_STAGES and v.RESIDUAL_ROLE not in v.ORIGIN_STAGES[:1]
    assert v.PROTECTED_NODE == v.PROTECTED
    assert v.PROTECTED_NODE in v.NODE_TYPES and v.PROTECTED in v.MARKED_STATES
    assert v.MARKED_STATES != v.NODE_TYPES
    # These two do not even share a spelling: P10 hyphenates its dispositions and
    # P8 (whose value P11's outcome is) underscores. Binding one to the other
    # would be a silent respelling, not a re-export.
    assert v.LEAVE_IN_PLACE_DISPOSITION == "leave-in-place"
    assert v.LEAVE_IN_PLACE == "leave_in_place"
    assert v.LEAVE_IN_PLACE_DISPOSITION in v.DISPOSITIONS
    assert v.LEAVE_IN_PLACE in v.OUTCOMES and v.LEAVE_IN_PLACE not in v.DISPOSITIONS

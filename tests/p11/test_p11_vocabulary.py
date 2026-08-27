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


def test_no_placement_module_spells_a_value_another_part_owns():
    # By AST over string constants, because a text search matches docstrings.
    from llm_harness.vocabulary import RESIDUAL_ACTIONS
    from llm_harness.vocabulary import OUTCOMES as P8_OUTCOMES
    owned = set(P8_OUTCOMES) | set(RESIDUAL_ACTIONS)
    offenders = []
    for path in sorted(PLACEMENT_ROOT.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in owned:
                    offenders.append((path.name, node.lineno, node.value))
    assert offenders == []


def test_check_names_the_set_and_never_the_nearest_match():
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("plase", v.OUTCOMES, name="outcome")
    assert "place" not in str(excinfo.value)
    assert str(len(v.OUTCOMES)) in str(excinfo.value)

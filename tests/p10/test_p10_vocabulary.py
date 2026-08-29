# tests/p10/test_p10_vocabulary.py
"""P10 Task 1 — one home per closed value.

Two rules are load-bearing here. First, a borrowed vocabulary is IMPORTED, never
respelled: `handling_class` and `operation_mode` are P7's, and a second copy that
P7 later widens becomes a value P10 rejects and P7 accepts. Second, `draft` means
two different things in P10 — a template's publication lifecycle and a branch
binding's workflow state — so neither is spelled `DRAFT`.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from database_agent.events import CORRECTION_SCOPES, RESERVED_EVENT_TYPES
from eval_harness.vocabulary import BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS
from grouping.vocabulary import MEMBERSHIP_BASES
from llm_harness.vocabulary import E_TEMPLATE
from privacy.vocabulary import HANDLING_CLASSES, OPERATION_MODES
from scan_agent.inventory import CURATION_SIGNAL_VALUES
from tree_design import vocabulary as v

SRC = Path(__file__).resolve().parents[2] / "src" / "tree_design"


def test_every_p10_set_is_published_both_ways():
    """A tuple for membership, a named constant for every member (BRIEF:232-234).

    The walk is over `P10_OWNED_SETS`, not `P10_CLOSED_SETS`. The plan printed
    the latter, and the two disagree: a borrowed set's members are named by their
    OWNER, and minting `DIRECT_ANCHOR = "direct-anchor"` here would be the second
    home the very next test forbids. BRIEF §11 scopes the rule to "every closed
    vocabulary EITHER PART PUBLISHES", and the plan's own Interfaces line says
    "one named constant per value ... for twenty-three P10-owned sets, plus
    eleven borrowed sets re-exported under P10 names". So: owned sets are named
    both ways, borrowed sets are re-exported whole and named by nobody here.
    """
    assert set(v.P10_CLOSED_SETS) == set(v.P10_OWNED_SETS) | set(v.BORROWED_SETS)
    assert not set(v.P10_OWNED_SETS) & set(v.BORROWED_SETS)
    for name, closed in v.P10_OWNED_SETS.items():
        assert isinstance(closed, tuple) and closed, name
        assert len(set(closed)) == len(closed), f"{name} repeats a value"
        for value in closed:
            constants = [
                k for k, obj in vars(v).items()
                if isinstance(obj, str) and obj == value and k.isupper()
            ]
            assert constants, f"{value!r} in {name} has no named constant"


def test_every_borrowed_set_is_the_owners_object_under_a_p10_name():
    """The other half of the split: a borrowed set is re-exported, never rebuilt.

    `is` rather than `==`, because a tuple that merely equals P7's today is a
    tuple that silently disagrees with it the day P7 adds a class.
    """
    owners = {
        "membership_basis": MEMBERSHIP_BASES,
        "handling_class": HANDLING_CLASSES,
        "operation_mode": OPERATION_MODES,
        "correction_scope": CORRECTION_SCOPES,
        "curation_signal": CURATION_SIGNAL_VALUES,
        "outcome": OUTCOMES,
        "budget_state": BUDGET_STATES,
    }
    for field, owned_by_upstream in owners.items():
        assert v.BORROWED_SETS[field] is owned_by_upstream, field


def test_the_five_node_types_are_512s_five_in_512s_order():
    assert v.NODE_TYPES == (
        v.EXISTING, v.PROPOSED, v.USER_CREATED, v.PROTECTED, v.IGNORED,
    )
    assert v.NODE_TYPES == (
        "existing", "proposed", "user-created", "protected", "ignored",
    )


def test_the_four_node_roles_and_three_dispositions():
    assert v.NODE_ROLES == (
        v.ORDINARY, v.SCOPED_GENERAL, v.RESIDUAL, v.SHARED_MATERIAL,
    )
    assert v.RESIDUAL_DISPOSITIONS == (
        "physical-destination", "review-only", "leave-in-place",
    )


def test_draft_is_never_a_bare_name_because_it_means_two_things():
    """`publication_state = draft` is a library lifecycle; `state = draft` is a
    branch's workflow. Same word, different owners, so neither gets `DRAFT`."""
    assert not hasattr(v, "DRAFT")
    assert v.PUBLICATION_DRAFT == "draft"
    assert v.WORKFLOW_DRAFT == "draft"
    assert v.PUBLICATION_STATES == ("draft", "published", "retired")
    assert v.BINDING_STATES == ("draft", "reviewed", "approved")


def test_the_nine_residual_names_and_eight_slots_are_73s_lists():
    assert v.RESIDUAL_TEMPLATE_NAMES == (
        "Temporary Screenshots", "One-Off Images", "Reference Clips",
        "Independent Records", "Receipts and Confirmations", "Reading Inbox",
        "Review Later", "Unsupported or Encrypted", "Protected Records",
    )
    assert v.RESIDUAL_SLOTS == (
        "display_name", "default_parent_location", "accepted_evidence_patterns",
        "expected_file_types", "sensitivity_restrictions",
        "optional_shallow_subfolders", "max_permitted_depth", "treatment",
    )


def test_gates_and_checks_are_two_separate_eight_and_six_item_lists():
    assert v.COMPOSITION_GATES == ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8")
    assert v.TEMPLATE_CHECKS == ("V1", "V2", "V3", "V4", "V5", "V6")
    # P1's V1-V4 are §8.2 checksum points and share nothing but the letter.
    assert v.TEMPLATE_CHECK_MEANINGS["V4"].startswith("author or organization")


def test_borrowed_sets_are_the_owners_objects_not_copies():
    assert v.MEMBERSHIP_BASES is MEMBERSHIP_BASES
    assert v.HANDLING_CLASSES is HANDLING_CLASSES
    assert v.OPERATION_MODES is OPERATION_MODES
    assert v.CORRECTION_SCOPES is CORRECTION_SCOPES
    assert v.CURATION_SIGNAL_VALUES is CURATION_SIGNAL_VALUES
    assert v.P2_OUTCOMES is OUTCOMES
    assert v.P2_BUDGET_STATES is BUDGET_STATES


def test_p10s_two_stages_and_two_dimensions_belong_to_p2s_closed_lists():
    assert v.P10_STAGE_IDS == ("template_generation", "tree_design")
    assert all(stage in STAGE_IDS for stage in v.P10_STAGE_IDS)
    assert v.P10_DIMENSIONS == ("template", "tree")
    assert all(dimension in DIMENSIONS for dimension in v.P10_DIMENSIONS)
    assert "P10" not in STAGE_IDS


def test_p10s_two_event_names_are_82_reserved_names():
    assert v.TEMPLATE_APPLICATION in RESERVED_EVENT_TYPES
    assert v.DESTINATION_TREE_EDIT in RESERVED_EVENT_TYPES
    assert v.P10_EVENT_TYPES == (v.TEMPLATE_APPLICATION, v.DESTINATION_TREE_EDIT)


def test_the_site_p10_calls_is_p8s_named_one():
    assert v.CALL_SITE_TEMPLATE is E_TEMPLATE


def test_check_names_the_closed_set_and_refuses_a_near_miss():
    assert v.check("proposed", v.NODE_TYPES, name="node_type") == "proposed"
    with pytest.raises(v.OutOfVocabulary) as excinfo:
        v.check("propose", v.NODE_TYPES, name="node_type")
    assert "node_type" in str(excinfo.value)
    assert "propose" not in str(excinfo.value).replace("'propose'", "")


def test_no_module_outside_the_vocabulary_spells_a_closed_value():
    """A second home for a closed value is the defect this project keeps hitting.

    The check is over parsed string literals, not source text, because a text
    search matches comments and docstrings and has produced a false result on
    this project nine times.
    """
    every_value = {value for closed in v.P10_CLOSED_SETS.values() for value in closed}
    # Single characters and pure identifiers are excluded: `C1` and `V1` are also
    # plausible local names, and a dict key spelling a slot name is the record
    # field itself, not a second home for the vocabulary.
    guarded = {value for value in every_value if " " in value or "-" in value}
    offenders = []
    for path in sorted(SRC.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Constant) and node.value in guarded:
                offenders.append(f"{path.name}:{node.lineno} {node.value!r}")
    assert offenders == []

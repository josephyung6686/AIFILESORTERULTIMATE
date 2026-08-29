# tests/p9/test_p9_vocabulary.py
"""P9 Task 2 — every closed P9 value has one named home.

Two names in this part are one word apart and mean different things, and the SPEC
says so twice: `Membership.basis` is the direct/context/user axis P8's dossier
`evidence_items[].basis` draws from, and `Membership.support[].support_kind` is
the retrieval channel. They are not merged here.
"""
from __future__ import annotations

import ast
import pathlib

import grouping.vocabulary as vocabulary
from grouping.vocabulary import (
    ACCEPTANCES,
    CANDIDATE,
    CONTEXT_SUPPORTED,
    DECISION_SOURCES,
    DIRECT_ANCHOR,
    EDGE_TYPES,
    EXCLUDED,
    FAILURE_STAGES,
    GROUP_STATES,
    INCLUDED,
    LABEL_SOURCES,
    MEMBERSHIP_BASES,
    MEMBERSHIP_DECISIONS,
    OUTLIER_FLAGS,
    REVIEW_STATES,
    SEED_KINDS,
    STOP_RULES,
    SUPPORT_KINDS,
    SUPPORTED,
    TENTATIVE_DISCOVERY,
    UNCERTAIN,
    UNRESOLVED,
    USER_ATTACHED,
)

GROUPING_ROOT = pathlib.Path(vocabulary.__file__).resolve().parent


def test_group_states_are_the_four_shared_lifecycle_values():
    """`accepted` and `rejected` are resolved as of a plan version, never stored."""
    assert GROUP_STATES == (CANDIDATE, SUPPORTED, TENTATIVE_DISCOVERY, UNRESOLVED)
    assert "accepted" not in GROUP_STATES
    assert "rejected" not in GROUP_STATES


def test_membership_bases_are_p9s_own_three():
    assert MEMBERSHIP_BASES == (DIRECT_ANCHOR, CONTEXT_SUPPORTED, USER_ATTACHED)


def test_membership_decisions_are_the_three_site_b_values():
    assert MEMBERSHIP_DECISIONS == (INCLUDED, EXCLUDED, UNCERTAIN)


def test_support_kind_is_the_six_retrieval_channels_and_not_basis():
    assert SUPPORT_KINDS == (
        "shared-validated-fact",
        "duplicate-or-version-link",
        "compatible-document-type",
        "existing-related-folder",
        "bounded-session",
        "mutual-semantic-retrieval",
    )
    assert not set(SUPPORT_KINDS) & set(MEMBERSHIP_BASES)


def test_edge_types_are_the_seven_typed_edges():
    assert EDGE_TYPES == (
        "shared-validated-fact",
        "duplicate",
        "version-family",
        "compatible-document-type",
        "existing-related-folder",
        "bounded-session",
        "mutual-semantic-retrieval",
    )


def test_seed_kinds_are_the_four_the_design_names():
    assert SEED_KINDS == (
        "strongly-identified-file",
        "validated-shared-fact",
        "structural-family",
        "user-created-starting-point",
    )


def test_stop_rules_are_sr1_through_sr6():
    assert STOP_RULES == ("SR1", "SR2", "SR3", "SR4", "SR5", "SR6")


def test_failure_stages_are_the_six_separately_logged_stages():
    """A single collapsed error class is a contract violation."""
    assert FAILURE_STAGES == (
        "retrieval", "graph", "interpretation", "validation", "label",
        "user-rejection",
    )


def test_acceptance_and_review_state_are_different_closed_sets():
    assert ACCEPTANCES == ("accepted", "rejected", "pending-review", "deferred")
    assert REVIEW_STATES == (
        "not-required", "pending-review", "user-accepted", "user-rejected",
        "user-excluded-from-packet", "deferred",
    )
    assert ACCEPTANCES != REVIEW_STATES


def test_label_sources_outlier_flags_and_decision_sources():
    assert LABEL_SOURCES == ("engine", "llm-proposed", "user-edited")
    assert OUTLIER_FLAGS == ("engine-flagged", "model-flagged", "both", "none")
    assert DECISION_SOURCES == ("rules", "llm", "validator", "user")


def test_p9_publishes_no_verdict_enum_of_its_own():
    """P8's outcome registry is the one vocabulary; P9 adds no second one."""
    names = {name for name in dir(vocabulary) if not name.startswith("_")}
    for banned in ("VERDICTS", "VERDICT_OUTCOMES", "OUTCOMES", "VALIDATION_OUTCOMES"):
        assert banned not in names, banned
    for banned in ("valid-direct", "valid-context-supported", "contradicted",
                   "generic-similarity-only", "unsupported"):
        assert banned not in vocabulary.__dict__.values(), banned


def test_p9_names_no_destination_tree_or_placement_concept():
    """P10/P11 own those. No tree concept enters `src/grouping/`."""
    names = {name.lower() for name in dir(vocabulary) if not name.startswith("_")}
    for banned in ("destination", "node", "tree", "placement", "folder_path",
                   "branch", "template"):
        assert not any(banned in name for name in names), banned


def test_every_closed_value_is_a_named_constant_in_this_module():
    """A closed value spelled inline in another module is a second home for it."""
    closed = {
        value
        for name, member in vars(vocabulary).items()
        if name.isupper() and isinstance(member, tuple)
        for value in member
    }
    inline = []
    for path in sorted(GROUPING_ROOT.glob("*.py")):
        if path.name == "vocabulary.py":
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value in closed:
                inline.append(f"{path.name}:{node.lineno}:{node.value!r}")
    assert inline == [], inline


def test_every_borrowed_p2_value_is_still_a_member_of_p2s_own_tuple():
    """P2 publishes its vocabularies as tuples of literals with no named constant
    per member, so a consumer either spells them or indexes them. P9 names each
    one it uses -- and this is what makes a P2 rename a failure here rather than a
    drift that shows up as a stage nobody records."""
    from eval_harness.vocabulary import (
        BUDGET_STATES,
        DIMENSIONS,
        OUTCOMES,
        STAGE_IDS,
    )

    from grouping import vocabulary as p9

    for name, owner in (
        ("P2_RETRIEVAL_STAGE", STAGE_IDS),
        ("P2_GRAPH_STAGE", STAGE_IDS),
        ("P2_GROUPING_STAGE", STAGE_IDS),
        ("P2_MODEL_CALL_STAGE", STAGE_IDS),
        ("P2_RETRIEVAL_DIMENSION", DIMENSIONS),
        ("P2_GRAPH_DIMENSION", DIMENSIONS),
        ("P2_GROUPING_DIMENSION", DIMENSIONS),
        ("P2_PRODUCED", OUTCOMES),
        ("P2_ABSTAINED", OUTCOMES),
        ("P2_DEFERRED", OUTCOMES),
        ("P2_WITHIN_CEILING", BUDGET_STATES),
        ("P2_CEILING_REACHED", BUDGET_STATES),
    ):
        assert getattr(p9, name) in owner, name


def test_the_two_colliding_words_are_named_apart():
    """P2's `retrieval` dimension and P9's `RETRIEVAL` failure stage are the same
    spelling for different concepts, and so are `graph` and `GRAPH`. Named apart,
    the way the borrowed P1 scan state is."""
    from grouping import vocabulary as p9

    assert p9.P2_RETRIEVAL_DIMENSION == p9.RETRIEVAL
    assert p9.P2_GRAPH_DIMENSION == p9.GRAPH
    assert p9.RETRIEVAL in p9.FAILURE_STAGES
    assert p9.GRAPH in p9.FAILURE_STAGES
    # And the collision is real, which is why they needed naming apart: a reader
    # seeing the bare string cannot tell which of the two it is.
    assert p9.P2_GRAPH_STAGE != p9.P2_GRAPH_DIMENSION

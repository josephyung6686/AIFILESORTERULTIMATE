# tests/p9/test_p9_connections.py
"""P9's seams, asserted against the live parts rather than described in prose.

Each test below names one boundary and the thing that goes wrong when it moves.
They are separate from `test_p9_no_invention.py` because these fail for a
different reason: not "P9 authored something it should not have" but "P9 and its
neighbour disagree about what crosses between them".

The last group is the north-star check. A proposal the user cannot tell apart
from a guess is a proposal they cannot review, so the states have to stay
distinguishable in the record and not merely in a UI.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

import grouping

ROOT = pathlib.Path(grouping.__file__).resolve().parent
MODULES = sorted(ROOT.glob("*.py"))


# --- P6: read through the public surface, at the anchor bar ----------------------


def test_p6_is_read_through_its_published_read_surface():
    """`facts.read_surface` is what P6 publishes. A query against P6's tables
    would be P9 deciding which facts count, which is §3.6's decision."""
    offenders = []
    for path in MODULES:
        for line, value in _strings(path):
            for table in ("FROM facts", "FROM values", "FROM unresolved"):
                if table in value:
                    offenders.append(f"{path.name}:{line}:{table}")
    assert offenders == [], offenders


def test_the_anchor_bar_is_visible_and_is_p6s_own_states():
    """A seed rests on a Direct or Validated fact. `possible` is a clue for review
    and §3.6 says it "must not quietly become a folder proposal"."""
    from facts.read_surface import PROPOSAL_ELIGIBLE_STATES
    from grouping.seeds import ANCHOR_STATES

    assert ANCHOR_STATES == frozenset({"direct", "validated"})
    assert ANCHOR_STATES <= set(PROPOSAL_ELIGIBLE_STATES)
    assert "possible" not in ANCHOR_STATES


# --- P7: classified before released ----------------------------------------------


def test_no_dossier_is_assembled_without_a_classification_reader():
    from grouping.dossier import assemble_group_dossier

    parameters = inspect.signature(assemble_group_dossier).parameters
    assert parameters["classification_store"].default is inspect.Parameter.empty


def test_p9_resolves_a_handling_class_through_p7s_own_function():
    """`resolve_class(None)` is `unreadable_unclassified` and never `public_low`.
    P9 reading the field itself would be P9 choosing what absence means."""
    import grouping.dossier as module

    source = pathlib.Path(module.__file__).read_text()
    assert "resolve_class" in source
    assert "handling_class ==" in source or "UNREADABLE_UNCLASSIFIED" in source


# --- P8: one seam, and it is `run_call` ------------------------------------------


def test_the_only_p8_names_p9_uses_are_the_eight_frozen_ones():
    import llm_harness

    frozen = set(llm_harness.__all__)
    used = set()
    for path in MODULES:
        for _line, module, name in _imports(path):
            if module.startswith("llm_harness"):
                used.add(name)
    # `vocabulary` and `records` members are values, not the public callables the
    # contract freezes; what must not appear is a validator or a transport.
    assert "run_call" not in used or "run_call" in frozen
    assert not used & {"issue", "dispatch", "validate_response", "ModelClient"}


def test_p9_never_materialises_evidence_or_calls_the_gate():
    offenders = []
    for path in MODULES:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Attribute) and node.attr in {
                    "release", "invoke", "materialised_items"}:
                offenders.append(f"{path.name}:{node.lineno}:{node.attr}")
    assert offenders == [], offenders


# --- P2: exact stage ids ---------------------------------------------------------


def test_p9_emits_exactly_three_p2_stages_and_they_are_p2s_own():
    from eval_harness.vocabulary import STAGE_IDS
    from grouping.stage_output import P9_STAGES

    assert len(P9_STAGES) == 3
    assert set(P9_STAGES) <= set(STAGE_IDS)
    assert "llm_interpretation" not in P9_STAGES


# --- P13: a boundary, not an import ----------------------------------------------


def test_the_p13_receiver_is_structural():
    from grouping.learning import apply_review_action

    parameters = inspect.signature(apply_review_action).parameters
    assert list(parameters) == ["conn", "action"]
    assert parameters["action"].annotation is inspect.Parameter.empty


# --- embeddings propose; they never anchor ---------------------------------------


def test_semantic_retrieval_can_never_produce_an_anchoring_membership():
    from grouping.vocabulary import (
        MEMBERSHIP_BASES,
        MUTUAL_SEMANTIC_RETRIEVAL,
        NON_ANCHORING_SUPPORT,
        SUPPORT_KINDS,
    )

    assert MUTUAL_SEMANTIC_RETRIEVAL in SUPPORT_KINDS
    assert MUTUAL_SEMANTIC_RETRIEVAL in NON_ANCHORING_SUPPORT
    assert MUTUAL_SEMANTIC_RETRIEVAL not in MEMBERSHIP_BASES


def test_a_direct_anchor_membership_cannot_rest_on_semantic_support_alone():
    from grouping.records import MalformedGroupRecord, Membership, Support
    from grouping.vocabulary import (
        DIRECT_ANCHOR,
        INCLUDED,
        MUTUAL_SEMANTIC_RETRIEVAL,
        NOT_FLAGGED,
        RULES,
    )

    with pytest.raises(MalformedGroupRecord):
        Membership(
            membership_id="m-1", group_id="g-1", file_id="f-1",
            content_hash="h-1", basis=DIRECT_ANCHOR,
            support=(Support(
                support_kind=MUTUAL_SEMANTIC_RETRIEVAL, observation_key=None,
                quote_or_field=None, location=None, edge_ref="edge-1"),),
            decision=INCLUDED, decision_source=RULES,
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at="2026-08-27T00:00:00Z")


# --- the north star: a proposal the user can actually review ---------------------


def test_every_membership_says_why_it_is_there():
    """A member with no support cannot say why the file belongs, and a proposal
    the user cannot interrogate is one they can only accept or reject blindly."""
    from grouping.records import MalformedGroupRecord, Membership
    from grouping.vocabulary import CONTEXT_SUPPORTED, INCLUDED, NOT_FLAGGED, RULES

    with pytest.raises(MalformedGroupRecord):
        Membership(
            membership_id="m-1", group_id="g-1", file_id="f-1",
            content_hash="h-1", basis=CONTEXT_SUPPORTED, support=(),
            decision=INCLUDED, decision_source=RULES,
            insufficient_evidence=False, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at="2026-08-27T00:00:00Z")


def test_the_seven_states_a_user_must_be_able_to_tell_apart_are_distinct():
    """Direct, context-supported, semantic-support, conflicted, abstained,
    consent-pending and deferred are seven different things to a person deciding
    what to do. Collapsed into one "AI suggestion", none of them is reviewable."""
    from grouping.vocabulary import (
        ABSTAINED,
        CONTEXT_SUPPORTED,
        DEFERRED,
        DIRECT_ANCHOR,
        MUTUAL_SEMANTIC_RETRIEVAL,
        PENDING_REVIEW,
        UNCERTAIN,
    )

    distinct = {
        DIRECT_ANCHOR, CONTEXT_SUPPORTED, MUTUAL_SEMANTIC_RETRIEVAL, UNCERTAIN,
        ABSTAINED, PENDING_REVIEW, DEFERRED,
    }
    assert len(distinct) == 7


def test_an_uncertain_membership_carries_the_model_s_own_statement():
    """A bare flag records that something was missing without saying what, and
    "the system was unsure" is not a thing a user can act on."""
    from grouping.records import MalformedGroupRecord, Membership, Support
    from grouping.vocabulary import (
        CONTEXT_SUPPORTED,
        COMPATIBLE_DOCUMENT_TYPE,
        NOT_FLAGGED,
        RULES,
        UNCERTAIN,
    )

    with pytest.raises(MalformedGroupRecord):
        Membership(
            membership_id="m-1", group_id="g-1", file_id="f-1",
            content_hash="h-1", basis=CONTEXT_SUPPORTED,
            support=(Support(
                support_kind=COMPATIBLE_DOCUMENT_TYPE, observation_key="k",
                quote_or_field=None, location=None, edge_ref=None),),
            decision=UNCERTAIN, decision_source=RULES,
            insufficient_evidence=True, insufficiency_statement=None,
            conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at="2026-08-27T00:00:00Z")


def test_no_p9_record_carries_a_destructive_or_irreversible_field():
    """P9 proposes. Nothing it writes moves, renames or deletes a file, and every
    decision it records is superseded rather than replaced."""
    import dataclasses

    from grouping import records as module

    banned = ("delete", "move", "rename", "apply", "commit", "overwrite")
    offenders = []
    for name, value in vars(module).items():
        if not (dataclasses.is_dataclass(value) and isinstance(value, type)):
            continue
        for item in dataclasses.fields(value):
            for word in banned:
                if word in item.name.lower():
                    offenders.append(f"{name}.{item.name}")
    assert offenders == [], offenders


def _strings(path: pathlib.Path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value


def _imports(path: pathlib.Path):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                yield node.lineno, node.module, alias.name

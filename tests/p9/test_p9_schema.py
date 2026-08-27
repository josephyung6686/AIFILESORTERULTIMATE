# tests/p9/test_p9_schema.py
"""P9 Task 2 — frozen records and the idempotent P9 schema.

The load-bearing shape rule: `plan_version_id` appears on exactly ONE P9 table.
Groups, memberships, dossiers and edges live in the shared evidence database and
survive every plan version; what a plan version captures is a STATE ABOUT them.
Carrying `plan_version_id` on `Group` would force the whole group, its dossier,
its model response and its evidence to be duplicated per version.

`Membership` deliberately has no `review_state` column either: review state is
resolved as of a plan version from `group_acceptance`, and a stored copy would be
a second home for it.
"""
from __future__ import annotations

import dataclasses
import sqlite3

import pytest

from grouping.records import (
    AnchorFact,
    Conflict,
    Group,
    GroupAcceptance,
    MalformedGroupRecord,
    Membership,
    Support,
    TypedEdge,
)
from grouping.schema import P9_TABLES, create_grouping_schema
from grouping.vocabulary import (
    CANDIDATE,
    COHERENT,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    ENGINE,
    INCLUDED,
    MUTUAL_SEMANTIC_RETRIEVAL,
    NOT_FLAGGED,
    OutOfVocabulary,
    RULES,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
)


@pytest.fixture()
def p9_conn(conn):
    from database_agent.db import create_schema

    create_schema(conn)
    create_grouping_schema(conn)
    return conn


def _columns(conn, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _field_names(cls) -> tuple[str, ...]:
    return tuple(field.name for field in dataclasses.fields(cls))


# --- the tables -----------------------------------------------------------------


def test_the_seven_p9_tables_exist(p9_conn):
    assert P9_TABLES == (
        "groups", "memberships", "group_dossiers", "group_edges",
        "stop_rule_outcomes", "group_failure_points", "group_acceptance",
    )
    present = {
        row["name"]
        for row in p9_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    for table in P9_TABLES:
        assert table in present, table


def test_creating_the_schema_twice_is_idempotent(p9_conn):
    create_grouping_schema(p9_conn)
    assert "groups" in {
        row["name"]
        for row in p9_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }


def test_only_group_acceptance_carries_a_plan_version(p9_conn):
    """Acceptance is per plan version. The records it is about are shared."""
    assert "plan_version_id" in _columns(p9_conn, "group_acceptance")
    for table in P9_TABLES:
        if table == "group_acceptance":
            continue
        assert "plan_version_id" not in _columns(p9_conn, table), table


def test_every_supersedable_table_carries_the_three_shared_columns(p9_conn):
    for table in ("groups", "memberships", "group_edges", "group_acceptance"):
        columns = _columns(p9_conn, table)
        for name in ("supersedes", "superseded_by", "supersede_reason"):
            assert name in columns, (table, name)


def test_every_membership_names_a_file_version(p9_conn):
    columns = _columns(p9_conn, "memberships")
    assert "file_id" in columns
    assert "content_hash" in columns


def test_no_p9_table_names_a_destination_or_a_path(p9_conn):
    for table in P9_TABLES:
        for column in _columns(p9_conn, table):
            for banned in ("destination", "node", "path", "folder", "tree"):
                assert banned not in column, (table, column)


# --- the records ----------------------------------------------------------------


def test_group_carries_no_plan_version_and_no_review_state():
    names = set(_field_names(Group))
    assert "plan_version_id" not in names
    assert "review_state" not in names
    assert "destination" not in repr(Group.__annotations__).lower()


def test_membership_carries_no_plan_version_and_no_review_state():
    """`review_state` is resolved as of a plan version, not stored beside it."""
    names = set(_field_names(Membership))
    assert "plan_version_id" not in names
    assert "review_state" not in names


def test_group_acceptance_carries_both():
    names = set(_field_names(GroupAcceptance))
    assert "plan_version_id" in names
    assert "review_state" in names
    assert "acceptance" in names


def test_group_records_are_frozen(p9_conn):
    group = _group()
    assert dataclasses.is_dataclass(group)
    with pytest.raises(dataclasses.FrozenInstanceError):
        group.state = "supported"  # type: ignore[misc]


# --- construction-time contract -------------------------------------------------


def _group(**overrides) -> Group:
    values = dict(
        group_id="g1",
        seed_ref="file-1",
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="PHYS1401 course materials",
        anchor_facts=(
            AnchorFact(
                field="course_code", value="PHYS1401", file_ids=("file-1",),
                reliability_state="validated", observation_key="sha256:obs-1",
            ),
        ),
        pre_model_signals={"independent_anchor_count": 2},
        anchor_count=2,
        coherence_verdict=None,
        coherence_citations=(),
        group_category=None,
        display_label=None,
        label_source=None,
        conflicts=(),
        stop_rule_hits=(),
        state=CANDIDATE,
        sensitivity_state="public_low",
        dossier_id=None,
        llm_response_ref=None,
        validation_verdict_ref=None,
        created_by=RULES,
        created_at="2026-08-26T00:00:00Z",
    )
    values.update(overrides)
    return Group(**values)


def _membership(**overrides) -> Membership:
    values = dict(
        membership_id="m1",
        group_id="g1",
        file_id="file-2",
        content_hash="hash-2",
        basis=DIRECT_ANCHOR,
        decision=INCLUDED,
        decision_source=RULES,
        support=(
            Support(
                support_kind=SHARED_VALIDATED_FACT,
                observation_key="sha256:obs-1",
                quote_or_field="PHYS1401",
                location="heading",
                edge_ref=None,
            ),
        ),
        insufficient_evidence=False,
        insufficiency_statement=None,
        conflicts=(),
        outlier_flag=NOT_FLAGGED,
        validation_verdict_ref=None,
        created_at="2026-08-26T00:00:00Z",
    )
    values.update(overrides)
    return Membership(**values)


def test_a_label_without_coherence_is_refused():
    """`display_label` and `group_category` are absent, not empty, unless coherent."""
    with pytest.raises(MalformedGroupRecord):
        _group(display_label="PHYS1401 - Spring 2026", label_source=ENGINE)
    with pytest.raises(MalformedGroupRecord):
        _group(group_category="academic")
    labelled = _group(
        coherence_verdict=COHERENT,
        coherence_citations=("sha256:obs-1",),
        display_label="PHYS1401 - Spring 2026",
        label_source=ENGINE,
        group_category="academic",
    )
    assert labelled.display_label == "PHYS1401 - Spring 2026"


def test_a_direct_anchor_membership_needs_a_shared_validated_fact():
    """Invariant 1: `direct-anchor` requires a shared-validated-fact support."""
    with pytest.raises(MalformedGroupRecord):
        _membership(
            basis=DIRECT_ANCHOR,
            support=(
                Support(
                    support_kind=MUTUAL_SEMANTIC_RETRIEVAL,
                    observation_key="sha256:obs-1",
                    quote_or_field=None,
                    location=None,
                    edge_ref="e1",
                ),
            ),
        )


def test_semantic_and_session_support_alone_can_never_be_direct_anchor():
    """Invariant 2. Embeddings may propose a neighbour; they never anchor one."""
    from grouping.vocabulary import BOUNDED_SESSION

    for kind in (MUTUAL_SEMANTIC_RETRIEVAL, BOUNDED_SESSION):
        with pytest.raises(MalformedGroupRecord):
            _membership(
                basis=DIRECT_ANCHOR,
                support=(
                    Support(
                        support_kind=kind, observation_key="sha256:obs-1",
                        quote_or_field=None, location=None, edge_ref="e1",
                    ),
                ),
            )
    context = _membership(
        basis=CONTEXT_SUPPORTED,
        support=(
            Support(
                support_kind=MUTUAL_SEMANTIC_RETRIEVAL,
                observation_key="sha256:obs-1",
                quote_or_field=None, location=None, edge_ref="e1",
            ),
        ),
    )
    assert context.basis == CONTEXT_SUPPORTED


def test_a_membership_with_no_support_at_all_is_refused():
    with pytest.raises(MalformedGroupRecord):
        _membership(support=())


def test_insufficient_evidence_carries_the_models_own_statement():
    with pytest.raises(MalformedGroupRecord):
        _membership(insufficient_evidence=True, insufficiency_statement=None)
    flagged = _membership(
        insufficient_evidence=True,
        insufficiency_statement="no term evidence on this file",
        decision="uncertain",
    )
    assert flagged.insufficiency_statement


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed_kind", "invented-seed"),
        ("state", "accepted"),
        ("created_by", "magic"),
    ],
)
def test_group_refuses_a_value_outside_its_closed_set(field, value):
    with pytest.raises((OutOfVocabulary, MalformedGroupRecord)):
        _group(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("basis", "invented-basis"),
        ("decision", "maybe"),
        ("decision_source", "vibes"),
        ("outlier_flag", "sort-of"),
    ],
)
def test_membership_refuses_a_value_outside_its_closed_set(field, value):
    with pytest.raises((OutOfVocabulary, MalformedGroupRecord)):
        _membership(**{field: value})


def test_a_typed_edge_names_its_evidence():
    with pytest.raises(MalformedGroupRecord):
        TypedEdge(
            edge_id="e1", from_file_id="a", to_file_id="b",
            edge_type=SHARED_VALIDATED_FACT, evidence_ref="", weight=None,
            bridge_entity_ref=None, hub_suppressed=False,
            created_at="2026-08-26T00:00:00Z",
        )


def test_a_conflict_names_its_competing_values():
    with pytest.raises(MalformedGroupRecord):
        Conflict(kind="target_institution", competing_values=(), file_ids=("f1",))


def test_no_record_stores_a_verdict_enum_of_its_own():
    """P9 references P8's verdict; it does not restate the outcome."""
    for cls in (Group, Membership):
        for field in dataclasses.fields(cls):
            assert field.name != "outcome", cls
            assert field.name != "verdict", cls
    assert "validation_verdict_ref" in _field_names(Membership)


# --- the candidate group dossier ------------------------------------------------
#
# The actual input to the LLM. It must not contain every file in full: "a large,
# noisy prompt encourages the model to find patterns that are not real" (§4.4).


def _excerpt(**overrides):
    from grouping.records import Excerpt

    values = dict(
        observation_key="sha256:obs-1",
        location="heading",
        text="PHYS1401 Syllabus",
        # The observation's own span. Required rather than defaulted: `None` is a
        # real value here ("the whole citation"), so a default would make
        # "nobody supplied one" indistinguishable from "the whole citation".
        text_span=(0, 17),
    )
    values.update(overrides)
    return Excerpt(**values)


def _dossier_file(**overrides):
    from grouping.records import DossierFile

    values = dict(
        file_id="lecture-08",
        content_hash="hash-lecture",
        document_type="lecture",
        basis=DIRECT_ANCHOR,
        key_facts=(
            AnchorFact(
                field="course_code", value="PHYS1401", file_ids=("lecture-08",),
                reliability_state="validated", observation_key="sha256:obs-1",
            ),
        ),
        excerpts=(_excerpt(),),
        why_retrieved=None,
    )
    values.update(overrides)
    return DossierFile(**values)


def _candidate_dossier(**overrides):
    from grouping.records import (
        BudgetSummary,
        CandidateGroupDossier,
        Omissions,
        PrivacySummary,
    )

    values = dict(
        dossier_id="d1",
        group_id="g1",
        proposed_basis="PHYS1401 course materials",
        anchor_files=(_dossier_file(),),
        candidate_files=(
            _dossier_file(
                file_id="hw-3", content_hash="hash-hw", document_type="homework",
                basis=CONTEXT_SUPPORTED, key_facts=(),
                why_retrieved="mutual-semantic-retrieval via e1",
            ),
        ),
        typed_edges=(),
        key_facts=(),
        excerpts=(_excerpt(),),
        conflicts=(),
        engine_flagged_outliers=(),
        omissions=Omissions(
            budget_cap_dropped=(), privacy_redacted=(), neighbourhood_capped=(),
        ),
        privacy=PrivacySummary(
            handling_classes=("public_low",), redactions_applied=0,
            release_decision_ref=None,
        ),
        budget=BudgetSummary(
            token_ceiling=4000, neighbour_cap=25, files_dropped=0,
        ),
        dossier_fingerprint="sha256:fingerprint",
        created_at="2026-08-26T00:00:00Z",
    )
    values.update(overrides)
    return CandidateGroupDossier(**values)


def test_anchor_and_candidate_files_are_separate_arrays():
    """§4.4: the dossier explicitly distinguishes direct evidence from context."""
    dossier = _candidate_dossier()
    assert {item.basis for item in dossier.anchor_files} == {DIRECT_ANCHOR}
    assert [item.file_id for item in dossier.candidate_files] == ["hw-3"]
    assert dossier.candidate_files[0].basis == CONTEXT_SUPPORTED
    names = {field.name for field in dataclasses.fields(type(dossier))}
    assert "files" not in names
    assert "members" not in names


def test_an_anchor_file_may_not_be_context_supported():
    with pytest.raises(MalformedGroupRecord):
        _candidate_dossier(anchor_files=(_dossier_file(basis=CONTEXT_SUPPORTED),))


def test_a_candidate_file_says_which_channel_retrieved_it():
    with pytest.raises(MalformedGroupRecord):
        _candidate_dossier(
            candidate_files=(
                _dossier_file(basis=CONTEXT_SUPPORTED, why_retrieved=None),
            ),
        )


def test_the_same_file_cannot_be_both_an_anchor_and_a_candidate():
    with pytest.raises(MalformedGroupRecord):
        _candidate_dossier(
            candidate_files=(
                _dossier_file(basis=CONTEXT_SUPPORTED, why_retrieved="edge e1"),
            ),
        )


def test_every_excerpt_names_the_observation_it_came_from():
    """P8 cannot verify a citation whose span resolves to nothing (§4.8)."""
    with pytest.raises(MalformedGroupRecord):
        _candidate_dossier(excerpts=(_excerpt(observation_key=""),))


def test_a_dossier_with_no_anchor_file_is_refused():
    """SR1: no valid anchor means no supported group, so no dossier either."""
    with pytest.raises(MalformedGroupRecord):
        _candidate_dossier(anchor_files=())


def test_the_dossier_carries_its_own_omissions_privacy_and_budget():
    dossier = _candidate_dossier()
    names = {field.name for field in dataclasses.fields(type(dossier))}
    for required in ("omissions", "privacy", "budget", "dossier_fingerprint"):
        assert required in names, required


def test_the_dossier_names_no_destination_and_no_folder():
    from grouping.records import CandidateGroupDossier

    names = {field.name for field in dataclasses.fields(CandidateGroupDossier)}
    for banned in ("destination", "node", "path", "folder", "tree", "label"):
        assert not any(banned in name for name in names), banned

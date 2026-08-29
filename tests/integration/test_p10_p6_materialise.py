"""P6 facts -> materialised levels -> nodes, over a real database.

Task 11's `vertical_options` takes `materialise` and `validate` as parameters and
implements neither. This is the test that says what fills them, and it is the
only place the whole chain — accepted group, composition, real P6 values,
V1-V6, `Node` records with `expected_values` — runs end to end.
"""
from __future__ import annotations

from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields
from p10.p6_fixtures import seed_academics
from tree_design.materialise import child_counts, materialise_branch


def test_the_worked_academics_example_produces_the_counts_55_promises(conn, tmp_path):
    """§5.5's Option A over real facts. One school, two courses, two work types —
    and the numbers the user sees are those, not their product."""
    # `tests/integration/` has no conftest, so `conn` is the ROOT fixture: P1's
    # eight tables and nothing else. P6's catalogue and P4's tables are this
    # test's to create, the way `tests/integration/test_p8_p2_replay.py:91-99`
    # layers its own.
    create_fields(conn)
    create_evidence_schema(conn)
    corpus = seed_academics(conn, tmp_path)
    from p10.test_p10_materialise import (
        ONE_CLASS,
        PROTECTED_CLASSES,
        _candidate,
    )

    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics",
        members=corpus.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    assert child_counts(evidence) == {"school": 1, "subject": 2, "work_type": 2}
    assert evidence.unresolved_by_field["work_type"] == frozenset({corpus.file_id("lab")})


def test_accepting_a_branch_drives_the_real_projection_into_the_store(conn, tmp_path):
    """The `accept` seam, with nothing stubbed.

    `apply_review_action` takes `project` as an injected callable and every unit
    test hands it a lambda returning hand-built nodes. That proves the store
    writes what it is given; it proves nothing about whether the thing a caller
    would actually bind — Task 12's `project_branch_nodes` — can be bound at all.
    This binds it, against real P6 facts, and drives one accept end to end.

    The binding is where §8.8's identity rule bites. `open_draft` mints NEW node
    ids for the whole copied tree, so the parent handed to the projection has to
    be looked up in the DRAFT by `origin_node_id`. A caller that passed the
    pre-draft parent would project children onto a parent id the new version does
    not contain, and every one of them would hang off nothing.
    """
    import dataclasses

    from p10 import p13_fixtures
    from p10.test_p10_materialise import (
        ALWAYS_ORDINARY,
        NO_CONTEXT,
        ONE_CLASS,
        PROTECTED_CLASSES,
        _candidate,
        _parent,
    )
    from tree_design.diff import diff_versions
    from tree_design.materialise import project_branch_nodes
    from tree_design.records import PlanVersion
    from tree_design.schema import create_tree_schema
    from tree_design.store import (
        apply_review_action,
        nodes_for_version,
        write_node,
        write_plan_version,
    )
    from tree_design.validation import ValidationReport
    from tree_design.vocabulary import DIFF_ADDED, DIFF_REPARENTED

    create_fields(conn)
    create_evidence_schema(conn)
    create_tree_schema(conn)
    corpus = seed_academics(conn, tmp_path)

    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at="2026-08-27T00:00:00Z", cross_folder_moves=False,
        selection_id="sel_1"))
    write_node(conn, _parent())

    _, evidence = materialise_branch(
        conn, _candidate(("school", "school"), ("subject", "subject"),
                         ("work_type", "work_type")),
        branch_node_id="n_academics",
        members=corpus.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    report = ValidationReport(report_id="vr_1", passed=("V1",), failures=())

    minted = iter(range(100))

    def project(_action, plan_version_id):
        # §8.8: the draft's copy of the branch, found by LINEAGE. Matching on
        # `node_id` finds nothing, because the draft minted a new one.
        draft_parent = next(
            node for node in nodes_for_version(conn, plan_version_id)
            if node.origin_node_id == "n_academics")
        return project_branch_nodes(
            evidence, report, parent=draft_parent,
            plan_version_id=plan_version_id,
            mint_node_id=lambda: f"proj_{next(minted)}",
            handling_class_for=ALWAYS_ORDINARY, template_context_for=NO_CONTEXT)

    new_version = apply_review_action(
        conn, p13_fixtures.accept("cand_academics", plan_version="plan_1"),
        new_version_id="plan_2", created_at="2026-08-27T01:00:00Z",
        mint_node_id=lambda: f"n2_{next(minted)}", component_version="p10-1",
        project=project)

    stored = nodes_for_version(conn, new_version)
    by_label = {node.display_label: node for node in stored}
    assert {"Columbia", "BUSIB 4300", "PHYS1401", "Syllabus", "Homework"} <= set(by_label)

    # Every stored node's parent exists in the SAME version. This is the assertion
    # that fails if the projection is handed a pre-draft parent.
    ids = {node.node_id for node in stored}
    dangling = [node.display_label for node in stored
                if node.parent_node_id is not None and node.parent_node_id not in ids]
    assert dangling == []
    assert by_label["Syllabus"].parent_node_id == by_label["BUSIB 4300"].node_id

    # §5.11: `lab` carries no work_type and is left unresolved rather than given
    # an invented one. Accepting the branch does not manufacture a home for it.
    assert corpus.file_id("lab") in evidence.unresolved_by_field["work_type"]

    entries = diff_versions(conn, before="plan_1", after=new_version)
    added = {e.origin_node_id for e in entries if e.kind == DIFF_ADDED}
    assert {by_label[label].origin_node_id for label in ("Columbia", "Homework")} <= added
    assert not [e for e in entries if e.kind == DIFF_REPARENTED]

    row = conn.execute(
        "SELECT * FROM events WHERE event_type = 'destination-tree edit' "
        "AND correction_subject = 'cand_academics'").fetchone()
    assert row is not None and row["subsystem"] == "P10"

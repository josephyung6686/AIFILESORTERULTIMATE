"""P10 Task 18 — the whole package observed at once, against `00` not the plan.

Verified against `planning/00-database-agent-product-design.md`, deliberately.
The plan has been wrong repeatedly — including a test of its own that could not
catch the defect in the code that same plan specified. `00` has not been wrong.

Each test below quotes the sentence it enforces and checks it END TO END over
the published package, rather than over one module's unit. That is what makes
this the last file: every other suite proves a part behaves; this one proves the
product keeps a promise that spans parts.

STANDING ITEMS THIS VERIFICATION RECORDS RATHER THAN ENFORCES
-------------------------------------------------------------
Two things are true of P10 at freeze and neither should be a failing test. A
test that fails for a scheduled gap trains people to ignore red, and a test that
fails for a defect nobody is fixing today is a defect nobody reads twice.

1. `TemplateDefinition.sensitivity_policy_ref` IS AN UNREAD COLUMN. It has one
   field declaration, three non-empty-string checks, one name in a list and one
   JSON copy in the loader, and NO GATE EVER RESOLVES IT — its value could be
   `"policy.banana"` and this whole suite would pass. It is INHERITED, not
   created here. Amendment C deliberately did not repeat the shape: the
   per-context floor it added enters `merge_fragment_constraints` and is read by
   the C7 maximum that already existed. Once applicability carries a real floor
   this ref is redundant rather than dangerous, and removing a shipped field is
   wider than that amendment — so it is named here to be inherited knowingly.

2. SIX P2 STAGE EMITTERS HAVE NO `src/` CALLER, across four parts:
   `grouping.emit_retrieval_stage`, `emit_graph_stage`, `emit_grouping_stage`,
   `placement.emit_retrieval_stage`, `emit_scoring_stage`, and P10's own two.
   That is DELIBERATE and the reason is in P9's code at
   `grouping/stage_output.py:16` — "Replay only. Emitting from ordinary
   ingestion would put a measurement in the harness for a run nobody asked to
   evaluate." The test that settles it: would wiring the consumer today be
   correct? No — so this is a scheduled gap, not the inert-concept defect.

   THE RISK, stated so it is not rediscovered: "deliberate" decays into
   "forgotten" if P2's replay driver is never built. Six emitters across four
   parts would then be dead weight every future reader has to re-litigate. That
   is a scheduling question and it belongs to whoever schedules P2.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

import tree_design
from tree_design.fixtures import (
    frozen_tree_fixture,
    realistic_tree,
    store_fixture_tree,
    walking_skeleton_tree,
)
from tree_design.freeze import is_legal_destination
from tree_design.vocabulary import IGNORED, PROTECTED

SRC = pathlib.Path(tree_design.__file__).resolve().parent


def test_every_node_states_the_facts_that_caused_it_to_appear():
    """§5.12. An unexplained node is one the user cannot judge.

    Checked over every published node rather than at the record, because
    `Node.__post_init__` only refuses an EMPTY explanation — a node explaining
    itself as `"x"` would satisfy it. The product promise is that a person can
    read why the folder is there.
    """
    for tree in (walking_skeleton_tree(), realistic_tree()):
        for node in tree:
            assert len(node.explanation.split()) >= 5, (
                f"{node.node_id} explains itself in "
                f"{node.explanation!r}, which no user can act on")


def test_no_surface_in_the_package_shows_a_confidence_score():
    """`00` §5: no surface shows a confidence score. The proposal states the
    facts that produced it in prose instead.

    Parsed rather than grepped, and over identifiers rather than strings,
    because the word "confidence" appears legitimately in prose explaining why
    it is absent — a guard whose banned word appears in its own docstring is a
    defect this project has already hit.
    """
    offenders = []
    banned = {"confidence", "confidence_score", "score", "certainty"}
    for path in sorted(SRC.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in banned:
                offenders.append(f"{path.name}:{node.lineno} {node.id}")
            elif isinstance(node, ast.Attribute) and node.attr in banned:
                offenders.append(f"{path.name}:{node.lineno} .{node.attr}")
            elif isinstance(node, ast.arg) and node.arg in banned:
                offenders.append(f"{path.name}:{node.lineno} arg {node.arg}")
    assert offenders == []


def test_protected_material_is_present_counted_and_never_a_destination(conn):
    """The standing rule, end to end through the real store and freeze.

    "Reports, apps and system files MUST NOT BE MOVED OR READ." The product
    answer is present-but-untouched: MARKED and COUNTED, never removed, with a
    reachable explanation. Removal would make them uncounted, which is worse.
    """
    tree = store_fixture_tree(conn)
    protected = [n for n in tree.nodes if n.node_type == PROTECTED]
    assert protected, "the verification needs protected material to verify"
    for node in protected:
        # Present, and counted.
        assert node.node_id in tree.freeze_record.node_ids
        # Explained, so the interface can say why it is untouched.
        assert node.explanation.strip()
        # And not somewhere P11 may place into.
        assert not is_legal_destination(tree.freeze_record, node.node_id)


def test_an_ordinary_node_in_the_same_tree_IS_a_destination(conn):
    """The twin. Without it a freeze that made NOTHING a legal destination
    would pass the test above — right answer, wrong reason."""
    tree = store_fixture_tree(conn)
    placeable = [n for n in tree.nodes
                 if n.node_type not in (PROTECTED, IGNORED)]
    assert any(is_legal_destination(tree.freeze_record, n.node_id)
               for n in placeable)


def test_freeze_is_a_view_over_the_evidence_and_never_a_rewrite_of_it():
    """§3.14. "The user can rearrange the same facts into a different tree
    tomorrow without losing a single observation."

    Enforced structurally: no module in the package imports a writer of a fact,
    a classification or a group. P10 reads all three and writes none.
    """
    forbidden = {"facts.file_facts", "facts.values",
                 "privacy.classification_store", "grouping.store"}
    offenders = []
    for path in sorted(SRC.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module in forbidden:
                offenders.append(f"{path.name}:{node.lineno} {node.module}")
    assert offenders == []


def test_the_published_fixture_and_the_live_read_cannot_drift(conn):
    """The P10 -> P11 seam, verified from the package rather than from P11.

    P11 builds against `tree_design.fixtures`; if a fixture stopped matching
    what `freeze.frozen_tree` returns, P11 would go red for a reason that lives
    here. So the equality is asserted on P10's side.
    """
    assert frozen_tree_fixture() == store_fixture_tree(conn)


def test_p10_publishes_the_fixtures_its_consumers_build_against():
    """MINOR 6: P10 owns the tree, so P10 publishes the fixtures.

    A consumer hand-building P10's records — as `tests/p11/p10_fixtures.py`
    did, declaring its OWN `FrozenTree` and `DestinationProfile` — is green
    until the two definitions disagree, and nothing says when. This asserts the
    published surface exists so the consumer has something to import instead.
    """
    from tree_design import fixtures

    for name in ("walking_skeleton_tree", "realistic_tree",
                 "residual_library_fixture", "template_library_fixture",
                 "two_version_pair", "frozen_tree_fixture"):
        assert callable(getattr(fixtures, name)), (
            f"tree_design.fixtures.{name} is the published surface P11 imports")

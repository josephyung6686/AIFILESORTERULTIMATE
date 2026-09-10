"""`104` §18.2 gap 16: the product compares by ONE canonicaliser, the validator's.

The gap's ruling is a sentence about identity, not about placement: "compares
values through the product's existing canonicaliser, the same one the validator
uses... No new normaliser, no alias table." A second canonicaliser is not a
theoretical worry on this project -- `65` §4.2 records four files of one course
becoming four one-file groups because one identity arrived as several spellings,
and `cli.normalize_for_model`'s own docstring says why it exists at all: "the
model's value is canonicalised by the SAME rule the deterministic slot uses for
that field, so `PHYS 1401` proposed by a model and `PHYS1401` read from a heading
cannot become two courses."

So the wiring is pinned as well as the behaviour. Both sides of §6.3's comparison
-- the tree, when the index is built, and the file's facts, when it is read --
have to arrive at the SAME callable, and it has to be the one §3.6's check 4
already compares by. A test that only measured the behaviour would keep passing
the day somebody threaded a second, agreeing canonicaliser through one side, and
would say nothing until the two disagreed on a corpus.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

SRC = Path(__file__).resolve().parents[2] / "src"

# P11's own database fixture, which creates the tables the seam test below
# reads for real. Imported by name because `tests/integration/` has no
# conftest of its own that builds one, and a second builder would be a
# second opinion about which schemas a placement run needs.
from p11.conftest import p11_conn  # noqa: E402,F401


def _tree_of(path: Path) -> ast.Module:
    return ast.parse(path.read_text())


def _keyword_of(call: ast.Call, name: str):
    return next((one.value for one in call.keywords if one.arg == name), None)


def _calls_named(tree: ast.Module, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            function = node.func
            if isinstance(function, ast.Name) and function.id == name:
                yield node
            elif isinstance(function, ast.Attribute) and function.attr == name:
                yield node


def test_the_placement_pass_is_handed_the_canonicaliser_the_validator_uses():
    """`cli` passes `normalize_for_model`, and `contradicts_stronger` reads it.

    Two assertions and they are one claim. The first is that P11's authority is
    that function; the second is that §3.6's check 4 -- "does a stronger fact
    contradict this proposal?", which the gap names as "the validator" -- decides
    by the same one. Either alone would let the two drift.
    """
    tree = _tree_of(SRC / "cli.py")
    passed = [
        _keyword_of(call, "canonical_value")
        for call in _calls_named(tree, "PipelineInputs")
        if _keyword_of(call, "canonical_value") is not None
    ]
    assert passed, "the placement pass hands P11 no canonicaliser at all"
    assert {node.id for node in passed if isinstance(node, ast.Name)} == {
        "normalize_for_model"}

    validator = next(node for node in ast.walk(tree)
                     if isinstance(node, ast.FunctionDef)
                     and node.name == "contradicts_stronger")
    assert "normalize_for_model" in {
        node.id for node in ast.walk(validator) if isinstance(node, ast.Name)}


def test_the_index_is_built_with_the_canonicaliser_the_retrieval_will_read_it_by():
    """And the two sides cannot be handed different ones.

    `production` takes `canonical` OFF the placement inputs rather than being
    given it a second time. Two arguments could arrive different, and the symptom
    would be silent: a folder ruled out by the spelling of the course it was built
    for, on a run where every part looked correctly wired.
    """
    tree = _tree_of(SRC / "production.py")
    call = next(_calls_named(tree, "build_destination_index"))
    canonical = _keyword_of(call, "canonical")
    assert isinstance(canonical, ast.Attribute)
    assert canonical.attr == "canonical_value"


def test_no_second_canonicaliser_reaches_the_placement_package():
    """`src/placement/` authors none of its own, which is the gap's own rule.

    The package takes the callable and applies it; a `def` here that decided what
    two values have in common would be P11 answering `00`:298's question about the
    person's vocabulary, and it would answer it differently from `cli` the first
    time either changed.
    """
    authored = set()
    for path in sorted((SRC / "placement").glob("*.py")):
        for node in ast.walk(_tree_of(path)):
            if isinstance(node, ast.FunctionDef) and (
                    "canonical" in node.name or "normalize" in node.name):
                authored.add(f"{path.name}:{node.name}")
    assert authored == set()


# --- and the behaviour, through the real one ---------------------------------------


@pytest.mark.parametrize("field_key,written,expected", [
    # `104` §18.2 gap 16's own example, in both directions.
    ("subject", "CS 1006", "CS1006"),
    ("subject", "CS1006", "CS1006"),
    # `00`'s Spring 2025 / Spring 2026 case: three spellings, one semester.
    ("term", "Spring 2026", "Spring2026"),
    ("term", "Spring2026", "Spring2026"),
    ("term", "2026-Spring", "Spring2026"),
])
def test_the_products_canonicaliser_makes_these_spellings_one_value(
        field_key, written, expected):
    """The rule this deployment actually holds, stated rather than assumed.

    The pins below are about the WIRING; this is what the wiring carries. If a
    later deployment changes what these spellings mean, this fails here rather
    than turning into a placement nobody can explain.
    """
    from cli import normalize_for_model

    assert normalize_for_model(field_key, written) == expected


def test_a_folder_and_a_file_that_spell_one_course_differently_are_one_value(
        p11_conn):
    """End to end, through `cli`'s own canonicaliser: the seam gap 16 closes.

    The folder was built from `CS1006` and the file states `CS 1006`. Before the
    gap closed this retrieved nothing and recorded a CONFLICT -- the file's own
    course ruling out the folder built for it. It is now a candidate, and the
    evidence on it is still the file's own spelling.
    """
    from dataclasses import replace

    from cli import normalize_for_model
    from placement import vocabulary as pv
    from placement.config import PlacementLimits
    from placement.index import build_destination_index
    from placement.records import MatchingFact, Subject
    from placement.retrieval import retrieve
    from p11.p10_fixtures import (
        ExpectedValue, FREEZE_RECORD, _node, _profile, tree_with,
    )

    nodes = (
        _node(node_id="n-root", display_label="Coursework",
              parent_node_id=None, ordinal=0, associated_group_ids=(),
              dimension_role=None, dimension=None, expected_values=(),
              refinement_disposition="shallow-by-choice",
              refinement_reason="Flat by design."),
        _node(node_id="n-cs", display_label="CS1006", parent_node_id="n-root",
              ordinal=1, associated_group_ids=(), dimension_role="course",
              dimension="subject",
              expected_values=(ExpectedValue(field="subject",
                                             value="CS1006"),)),
    )
    tree = tree_with(
        nodes=nodes, profiles=tuple(_profile(node) for node in nodes),
        freeze_record=replace(
            FREEZE_RECORD, node_ids=tuple(node.node_id for node in nodes),
            legal_destination_ids=frozenset(
                node.node_id for node in nodes if node.accepts_placement)))
    build_destination_index(p11_conn, tree, component_version="seam",
                            observed_at="2026-09-10T00:00:00Z",
                            canonical=normalize_for_model)
    result = retrieve(
        p11_conn,
        subject=Subject(kind=pv.FILE, file_id="f1", content_hash="h1",
                        group_id=None, member_file_ids=()),
        plan_version=tree.plan_version_id,
        limits=PlacementLimits(
            max_retrieved_neighbors=4, max_local_graph_neighborhood=8,
            max_candidate_cluster_size=6, max_residual_files_per_batch=50,
            max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
            max_cost_per_scan=5),
        facts=(MatchingFact(file_fact_id="ff1", field="subject",
                            value="CS 1006", reliability=pv.DIRECT,
                            evidence_ref="obs-1"),),
        group_ids=(), curated_folder_labels=(), semantic_neighbours=(),
        canonical=normalize_for_model, component_version="seam",
        observed_at="2026-09-10T00:00:00Z")

    assert [candidate.node_id for candidate in result.candidates] == ["n-cs"]
    assert result.conflicts == ()
    assert result.candidates[0].matching_facts[0].value == "CS 1006"

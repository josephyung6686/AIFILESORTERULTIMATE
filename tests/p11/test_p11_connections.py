"""Every seam P11 has, named, and every seam it must not have, refused.

Two kinds of guard live here and they answer different questions.

A BOUNDARY guard says a part is reached only through the surface it published.
It is written against the LIVE import graph, module by module, so an import that
appears tomorrow fails here rather than passing as "probably fine".

A REACHABILITY guard says a producer has a consumer that actually CALLS it.
Imported-but-never-invoked passes a reference check and fails this one, which is
the shape of every concept this project shipped fully tested and connected to
nothing.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from placement import vocabulary as v

PLACEMENT_ROOT = Path(__file__).resolve().parents[2] / "src" / "placement"


def _modules() -> dict[str, ast.Module]:
    return {path.name: ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(PLACEMENT_ROOT.glob("*.py"))}


def _imports(tree: ast.Module) -> set[str]:
    """Every dotted name imported, as `module` and as `module.name`."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


def _importers_of(prefix: str) -> dict[str, set[str]]:
    """Which modules import anything under `prefix`, and exactly what."""
    found = {}
    for name, tree in _modules().items():
        reached = {item for item in _imports(tree)
                   if item == prefix or item.startswith(prefix + ".")}
        if reached:
            found[name] = reached
    return found


def _calls(tree: ast.Module) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return names


def _callers_of(function_name: str) -> set[str]:
    return {name for name, tree in _modules().items()
            if function_name in _calls(tree)}


def test_the_import_scan_sees_both_import_forms():
    # The negative twin for every boundary guard below: a scan that missed
    # `import x.y` or missed `from x import y` would report a clean boundary on a
    # module that had crossed it.
    tree = ast.parse("import shutil\nfrom llm_harness.harness import run_call\n")
    assert _imports(tree) == {"shutil", "llm_harness.harness",
                              "llm_harness.harness.run_call"}


# --- P8: one seam module, and one exception that names itself ------------------------


def test_p8s_mechanism_is_reached_from_p8_seam_and_versions_and_nowhere_else():
    """`run_call` from one module; the validator from two, and the second says why.

    `p8_seam.py` owns Site C and Site D. `versions.py` reaches
    `revalidate_for_plan` because §8.8 asks a DIFFERENT question -- does a stored
    verdict still hold against a new plan version -- and answering it by re-running
    `run_call` would issue a second spend for a call that already happened.
    """
    assert set(_importers_of("llm_harness.harness")) == {"p8_seam.py"}
    assert set(_importers_of("llm_harness.placement_validation")) == {
        "p8_seam.py", "versions.py"}
    validators = _importers_of("llm_harness.placement_validation")
    assert validators["versions.py"] <= {
        "llm_harness.placement_validation",
        "llm_harness.placement_validation.revalidate_for_plan"}


def test_p11_never_builds_a_dossier_or_touches_p8s_transport():
    # P11 assembles a REQUEST. `Dossier` is what P8 builds from it, behind the
    # release, and `transport` is how P8 reaches a model.
    assert _importers_of("llm_harness.transport") == {}
    assert _importers_of("llm_harness.dossier") == {}
    for name, tree in _modules().items():
        assert "llm_harness.records.Dossier" not in _imports(tree), name
        assert "Dossier" not in _calls(tree), name


def test_p11_records_no_cd_verdict_of_its_own():
    # `harness.py:245-253` calls `record_cd_verdict` for every C and D verdict and
    # `placement_validation.py:614` does it again on revalidation. A P11 call
    # would write the row twice.
    assert _callers_of("record_cd_verdict") == set()


# --- P7: the gate is held and never exercised ------------------------------------------


def test_p7_is_reached_only_through_the_four_surfaces_it_published():
    reached = _importers_of("privacy")
    assert set(reached) == {"privacy.py", "vocabulary.py"}
    assert reached["privacy.py"] == {
        "privacy.classification_store", "privacy.classification_store.ClassificationStore",
        "privacy.denial", "privacy.denial.mode_forbids",
        "privacy.moves", "privacy.moves.may_move_automatically",
        "privacy.policy", "privacy.policy.current_policy",
        "privacy.release", "privacy.release.LOCALITIES",
    }
    assert reached["vocabulary.py"] == {
        "privacy.vocabulary", "privacy.vocabulary.HANDLING_CLASSES"}


def test_p11_holds_a_gate_and_never_releases_through_it():
    # §8.4: P11 supplies `run_call` a `Gate` because `run_call` requires one, and
    # P8 calls `release` inside, after the eligibility and reduction decisions.
    # Holding a capability and exercising it are different things.
    assert _importers_of("privacy.gate") == {}
    assert _callers_of("release") == set()
    assert _callers_of("Gate") == set()


# --- P6, P4: facts by their published surface, cited by observation key ------------------


def test_p6_is_reached_only_through_its_read_surface():
    reached = _importers_of("facts")
    assert set(reached) == {"retrieval.py", "vocabulary.py"}
    assert reached["retrieval.py"] == {"facts.read_surface",
                                       "facts.read_surface.is_destination_eligible"}


def test_no_p11_field_is_named_for_a_per_row_observation_id():
    # M14, P4: a citation is a content-addressed `observation_key`, which survives
    # a re-extraction. A per-row `observation_id` does not, and a record carrying
    # one would cite evidence that stopped existing when the extractor re-ran.
    import dataclasses

    import placement.index as index
    import placement.pipeline as pipeline
    import placement.records as records
    import placement.residual as residual
    import placement.retrieval as retrieval

    for module in (records, index, residual, retrieval, pipeline):
        for value in vars(module).values():
            if isinstance(value, type) and dataclasses.is_dataclass(value):
                names = {f.name for f in dataclasses.fields(value)}
                assert "observation_id" not in names, value.__name__


# --- P2: two stages, and the outcome vocabulary P2 already refuses -----------------------


def test_p2_is_reached_only_from_the_stage_module():
    reached = _importers_of("eval_harness")
    assert set(reached) == {"stage_output.py", "vocabulary.py"}


def test_p11_emits_exactly_two_stage_ids():
    assert v.STAGE_IDS == (v.CANDIDATE_NODE_RETRIEVAL, v.PLACEMENT_SCORING)


def test_p2s_foreign_outcome_list_still_equals_p11s_own():
    # P2 enumerated P11's seven record outcomes before P11 existed, in order to
    # REFUSE them in the envelope. Two lists of one vocabulary is drift.
    from eval_harness.stage_output import _FOREIGN_OUTCOMES

    assert set(_FOREIGN_OUTCOMES) == set(v.OUTCOMES)


# --- P9 and P10: read, never reconstructed -------------------------------------------------


def test_p9_is_reached_only_through_its_two_reads_and_its_vocabulary():
    reached = _importers_of("grouping")
    assert set(reached) == {"groups.py", "pipeline.py", "records.py"}
    assert reached["groups.py"] == {
        "grouping.acceptance", "grouping.acceptance.group_state_as_of",
        "grouping.store", "grouping.store.memberships_for_group",
        "grouping.vocabulary", "grouping.vocabulary.ACCEPTED",
        "grouping.vocabulary.NOT_FLAGGED",
    }
    # `pipeline.py` and `records.py` carry a P9 VALUE and call nothing.
    for name in ("pipeline.py", "records.py"):
        assert all(item.startswith("grouping.vocabulary")
                   for item in reached[name]), name


def test_p10_is_carried_as_vocabulary_and_never_as_a_record():
    reached = _importers_of("tree_design")
    assert set(reached) == {"groups.py", "vocabulary.py"}
    for name, items in reached.items():
        assert all(item.startswith("tree_design.vocabulary")
                   for item in items), (name, items)


# --- one database, and it is P11's own ------------------------------------------------------

#: Case-SENSITIVE on purpose. Every SQL string in `src/placement/` writes its
#: keywords in upper case, and prose does not -- so an uppercase `FROM` is the
#: signal that separates a query from a docstring sentence containing "from the".
_TABLE_RE = re.compile(r"\b(?:FROM|INTO|UPDATE|JOIN)\s+([a-z_][a-z0-9_]*)")
_SQL_RE = re.compile(r"\b(?:SELECT|INSERT|UPDATE|CREATE|DELETE)\b")


def _tables_named_in(tree: ast.Module) -> set[str]:
    """Every table name a SQL string in this module reads or writes."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and _SQL_RE.search(node.value)):
            found.update(match.lower() for match in _TABLE_RE.findall(node.value))
    return found


def test_no_placement_module_queries_another_parts_table():
    """The strongest form of every boundary above, in one assertion.

    A part reached through an import can still be reached around it, by naming
    its table in a SQL string -- and that is the reach no import scan sees. P11's
    own five are the whole allowed set: `files` is P1's, `classifications` and
    `policies` are P7's, `memberships` and `group_acceptance` are P9's, and
    `llm_verdict` is P8's, and every one of them is asked through its owner's
    function instead.
    """
    from placement.schema import P11_TABLES

    offenders = {name: sorted(_tables_named_in(tree) - set(P11_TABLES))
                 for name, tree in _modules().items()}
    assert {name: hits for name, hits in offenders.items() if hits} == {}


def test_the_table_scan_would_catch_a_foreign_query():
    # The negative twin. A regex that matched nothing would report a clean
    # boundary over a module reading P1's files table directly -- and one that
    # matched too much would fire on the word "from" in a docstring, which is how
    # a boundary test stops being read.
    tree = ast.parse('q = "SELECT content_hash FROM files WHERE file_id = ?"')
    assert _tables_named_in(tree) == {"files"}
    prose = ast.parse('"""Read from the frozen tree, joined to the index."""')
    assert _tables_named_in(prose) == set()


# --- no test fixture ever reaches production code --------------------------------------------


def test_no_source_module_imports_a_test_fixture():
    # `tests/p11/` is importable as `p11.*` because the directory is a package, so
    # `from p11.p10_fixtures import FROZEN_TREE` would resolve inside `src/` and
    # a P10 stand-in would become the product's idea of what a node is.
    for name, tree in _modules().items():
        imported = _imports(tree)
        assert not {item for item in imported
                    if item.split(".")[0] in {"p11", "p9", "p10", "tests"}}, name


def test_the_fixture_scan_would_catch_one():
    tree = ast.parse("from p11.p10_fixtures import FROZEN_TREE\n")
    assert {item for item in _imports(tree)
            if item.split(".")[0] in {"p11", "tests"}}


def test_p11s_own_golden_fixtures_reach_out_to_nothing_and_nothing_reaches_in():
    # `fixtures.py` is P12's and P13's entry point. It imports only P11's records
    # and P11's vocabulary, so a downstream part building against it is building
    # against the live shape -- and no P11 module imports it back, so a fixture
    # can never become a production answer.
    trees = _modules()
    assert all(item.startswith(("placement", "__future__"))
               for item in _imports(trees["fixtures.py"]))
    for name, tree in trees.items():
        if name == "fixtures.py":
            continue
        assert "placement.fixtures" not in _imports(tree), name


# --- reachability: a producer with a consumer that actually calls it -----------------------

#: Every §6.12 / §7 component and the module that must CALL it. An import is not a
#: use: the nine concepts this project shipped fully tested and connected to
#: nothing all had references pointing at them.
_PRODUCER_CONSUMER: tuple[tuple[str, str], ...] = (
    ("build_node_local_graph", "pipeline.py"),
    ("retrieve", "pipeline.py"),
    ("assess", "pipeline.py"),
    ("needs_model_call", "pipeline.py"),
    ("suppressed_nodes", "pipeline.py"),
    ("privacy_state_for", "pipeline.py"),
    ("may_assemble_dossier", "pipeline.py"),
    ("automatic_move_permitted_for", "pipeline.py"),
    ("review_policy_for", "pipeline.py"),
    ("entry_for", "pipeline.py"),
    ("legal_node_ids", "pipeline.py"),
    ("call_placement", "pipeline.py"),
    ("placement_authorities", "pipeline.py"),
    ("residual_authorities", "pipeline.py"),
    ("site_dependencies", "pipeline.py"),
    ("to_p8_conflicts", "pipeline.py"),
    ("transcribe", "pipeline.py"),
    ("evidence_snapshot_id_for", "pipeline.py"),
    ("basis_key_for", "pipeline.py"),
    ("record_decision", "pipeline.py"),
    ("current_decision", "pipeline.py"),
    ("accepted_group_as_of", "pipeline.py"),
    ("confirm_shared_parent", "pipeline.py"),
    ("excluded_outlier_for", "pipeline.py"),
    ("resolve_multi_home", "pipeline.py"),
    ("group_plan_emitted", "pipeline.py"),
    ("surface_residual_sets", "pipeline.py"),
    ("require_set_decision", "pipeline.py"),
    ("model_calls_permitted", "pipeline.py"),
    ("require_model_call_permitted", "pipeline.py"),
    ("outcome_for_action", "pipeline.py"),
    ("check_return_cycle", "pipeline.py"),
    ("link_return", "pipeline.py"),
    ("emit_retrieval_stage", "pipeline.py"),
    ("emit_scoring_stage", "pipeline.py"),
    ("moves_files", "privacy.py"),
    ("is_typed_support", "scoring.py"),
    ("subject_ref_of", "pipeline.py"),
    ("mark_superseded", "store.py"),
)


@pytest.mark.parametrize("producer,consumer", _PRODUCER_CONSUMER)
def test_every_producer_has_a_consumer_that_calls_it(producer, consumer):
    trees = _modules()
    assert producer in _calls(trees[consumer]), (
        f"{consumer} does not call {producer}")


def test_the_reachability_check_fails_on_an_import_that_is_never_invoked():
    # The negative twin, and the whole reason this is a CALL check. A module that
    # imports a producer and never invokes it passes every reference check ever
    # written and fails this one.
    tree = ast.parse("from placement.retrieval import retrieve\nX = retrieve\n")
    assert "retrieve" not in _calls(tree)
    assert "placement.retrieval.retrieve" in _imports(tree)


# --- the known gaps, asserted rather than described -------------------------------------------


def test_apply_review_action_still_has_no_caller_in_src():
    """P13's entry point, waiting for P13.

    `review.apply_review_action` takes a `decision_factory` the pipeline is meant
    to supply, and it is driven by a P13 review gesture rather than by a corpus
    run -- so §6.12's nine steps do not reach it and must not pretend to. It is
    exercised end to end in `tests/p11/test_p11_review.py` against a factory the
    test supplies.

    This is a KNOWN GAP, named so that the day a caller appears in `src/` this
    assertion fails and somebody has to decide whether the wiring is right.
    """
    assert _callers_of("apply_review_action") == set()
    assert _callers_of("record_correction") == {"review.py"}


def test_reproject_and_blocked_policy_still_have_no_caller_in_src():
    """§8.8's diff and §6.11's blocked policy, both waiting for their caller.

    `reproject` answers "what does adopting plan-2 do to plan-1's decisions?",
    which nothing in a single-version corpus run asks. `blocked_policy` is the
    review policy for a decision whose subject P7 has not classified -- and
    `privacy_state_for` RAISES on that case rather than building one, so today
    there is no decision for it to be the policy OF.

    Both fail the day a producer appears, which is the point.
    """
    assert _callers_of("reproject") == set()
    assert _callers_of("blocked_policy") == set()
    assert _callers_of("learned_preferences_still_applicable") == set()

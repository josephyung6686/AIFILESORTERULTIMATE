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


def test_p7_is_reached_only_through_the_surfaces_it_published():
    """Every P7 name P11 reads is one P7 published for a reader.

    `privacy.classification` joined the list when the unclassified case stopped
    being a refusal: `resolve_class` is P7's own answer for a file with no record
    and `UNREADABLE_UNCLASSIFIED` is PUBLISHED rather than private by that
    module's own docstring, so reading them is the opposite of P11 inventing a
    policy for absence. `unclassified_denies` is the matching gate predicate,
    beside `mode_forbids` and owned by the same module.

    `privacy.denial.UNCLASSIFIED_PERMITS_LOCAL` joined it for `104` R-121. P11
    used to pin its own answer to P7 SPEC Open question 5 while `cli.py` pinned
    the opposite one; the owner ruled one answer under one name (`104` §15.3), so
    P11 now READS P7's published answer instead of holding a second. One more
    name from P7 is the shape of the fix, not a widening of the surface.
    """
    reached = _importers_of("privacy")
    assert set(reached) == {"privacy.py", "vocabulary.py"}
    assert reached["privacy.py"] == {
        "privacy.classification",
        "privacy.classification.UNREADABLE_UNCLASSIFIED",
        "privacy.classification.resolve_class",
        "privacy.classification_store", "privacy.classification_store.ClassificationStore",
        "privacy.denial", "privacy.denial.mode_forbids",
        "privacy.denial.unclassified_denies",
        "privacy.denial.UNCLASSIFIED_PERMITS_LOCAL",
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
        # P9's word for a membership it has withdrawn. `memberships_for_group`
        # returns every live row and `Membership.decision` says which of them are
        # members; P11 read the rows and never asked, so a file P9 had excluded
        # was handed to `place_group` and given a destination. Reading the field
        # means naming its value, and naming it out of P9's own vocabulary is the
        # thing this test is for -- a literal `"excluded"` in `groups.py` would
        # be P11 keeping its own spelling of a word P9 owns.
        "grouping.vocabulary.EXCLUDED",
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
    # `104` §18.15: the seam's suspendable form, which is the one the
    # per-file pass drives on a lane. `call_placement` is the same call
    # driven inline and is what `place_group` still reaches.
    ("call_placement_steps", "pipeline.py"),
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


def test_reproject_still_has_no_caller_and_blocked_policy_now_does():
    """§8.8's diff still waits for its caller; §6.11's blocked policy found one.

    `reproject` answers "what does adopting plan-2 do to plan-1's decisions?",
    which nothing in a single-version corpus run asks. It is a KNOWN GAP, named so
    that the day a caller appears in `src/` this assertion fails and somebody has
    to decide whether the wiring is right.

    `blocked_policy` was in the same state for the opposite reason:
    `privacy_state_for` RAISED on an unclassified file rather than building a
    state for it, so there was no decision for it to be the policy OF -- and one
    file the detector honestly declined to guess about refused the whole corpus.
    Now absence resolves through P7's `resolve_class` and `review_policy_for` is
    its one caller, which is what stops an unclassified file being placed as an
    ordinary one.
    """
    assert _callers_of("reproject") == set()
    assert _callers_of("blocked_policy") == {"privacy.py"}
    assert _callers_of("learned_preferences_still_applicable") == set()


def test_no_unfinished_knowledge_source_gained_an_implementation_default():
    """§6.10's thresholds, §8.6's ceilings, and the four open selectors.

    Every one of them is a question the design leaves open, and every one arrives
    on `PipelineInputs` with NO default -- so a caller that has not chosen cannot
    silently get P11's guess. A field gaining a default here is P11 answering a
    question the design says is the user's or the deployment's.
    """
    import dataclasses

    from placement.pipeline import PipelineInputs

    for field in dataclasses.fields(PipelineInputs):
        assert field.default is dataclasses.MISSING, field.name
        assert field.default_factory is dataclasses.MISSING, field.name
    names = {field.name for field in dataclasses.fields(PipelineInputs)}
    # The five the design leaves open, named so a deletion is visible.
    assert {"policy", "limits", "partition", "ask_or_abstain",
            "max_return_cycles"} <= names


def test_a_run_without_a_support_policy_or_limits_refuses(p11_conn):
    # The discriminating twin: absence must REFUSE, not fall through to a guess.
    # A required input with no test for its absence is not required.
    import dataclasses

    import pytest as _pytest

    from placement.config import ConfigurationRequired, placement_limits
    from placement.pipeline import PipelineInputs

    from database_agent.budget import set_ceiling
    from placement.config import CEILINGS

    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    good = dict(
        plan_version="plan-1", tree=object(),
        policy=__import__("placement.config", fromlist=["SupportPolicy"]
                          ).SupportPolicy(policy_id="p", support_scale_max=1.0,
                                          minimum_support_threshold=0.5,
                                          margin_threshold=0.2),
        limits=placement_limits(p11_conn), partition=None,
        ask_or_abstain=None, max_return_cycles=None, gate=None,
        model_client=None, prompt=None, residual_prompt=None, call_dependencies=None,
        model_call_request=None, chosen_node_of=None, residual_action_of=None,
        sensitivity_policy=None, model_target=None, route_for=None,
        usage_recorder=None,
        # `104` §18.15: one at a time, which is what this pass did before the
        # lane existed. Stated rather than defaulted, like every field here.
        calls_at_once=1,
        ask_about_file=lambda subject: None,
        chosen_by_user=lambda subject: None,
        fields_that_cannot_anchor_a_move=frozenset(),
        their_own_folder_made_for_what_it_holds={}, p2=None,
        canonical_value=lambda field_key, value: None,
        the_folder_each_file_is_in={},
        a_move_the_person_has_not_permitted=None)
    PipelineInputs(**good)                     # the control: this one builds
    with _pytest.raises(ConfigurationRequired):
        PipelineInputs(**{**good, "policy": None})
    with _pytest.raises(ValueError):
        PipelineInputs(**{**good, "limits": None})
    # §6.3's third suppression is injected on the same terms. Absent, every
    # candidate matched on an artifact kind alone would be a legal destination
    # again, so a run that did not state it must refuse rather than fall through.
    with _pytest.raises(ValueError):
        PipelineInputs(**{**good, "fields_that_cannot_anchor_a_move": None})


# --- what §6.12's pipeline still does NOT reach -----------------------------------


def test_the_scoped_general_role_is_described_to_the_model_and_offered_to_it():
    """§5.9's scoped fallback is told to the model AND put on its menu.

    This asserted `readers == set()`, then `{"index.py"}`, and each step was a
    known gap closing. `SCOPED_GENERAL` was carried from P10 and no module in
    `src/placement/` treated a `scoped-general` node differently from an ordinary
    one, so §6.7's "scoped fallback under a meaningful parent" had no expression
    at all. `index.node_profile` closed R-17's half: the C draft's own HOW TO
    DECIDE says "a candidate described as a scoped fallback under a parent stands
    when the parent's levels are supported and no child's deeper level is", and a
    model shown an opaque id cannot tell which candidate that is.

    **`pipeline.py` IS THE READER THAT APPEARED, AND `104` §18.2 GAP 11 IS THE
    RULING THAT PUT IT THERE.** The sentence this test used to end on -- "the day
    a decision branches on the role, this fails and somebody decides whether the
    branch is the right one" -- is that day, and the owner ruled it on 10 Sep. A
    folder the prompt describes and no shortlist can contain is an option the
    model cannot take: `00`:110 lists "an approved scoped fallback such as
    General" among the four answers the judge chooses between, and `00`:111 says
    when it is the right one. So `_the_parents_own_general_is_offered` puts a
    contender's own General on the menu as a set-aside candidate.

    **It is still not a RULE.** Nothing here places a file in a General; the
    engine offers it with a sentence and the model decides, which is §13.5's
    "model decides, rules validate" and the reason it arrives as a `SetAside`
    rather than as a contender -- a General scored as a rival would win every tie
    on an offline run and file the corpus into catch-alls.
    """
    readers = {name for name, tree in _modules().items()
               if name != "vocabulary.py"
               and "SCOPED_GENERAL" in {node.id for node in ast.walk(tree)
                                        if isinstance(node, ast.Name)}}
    assert readers == {"index.py", "pipeline.py"}


def test_one_producer_fills_decision_depths_unsupported_levels():
    """§6.7's broad-parent case has a writer, and exactly one.

    `DecisionDepth.unsupported_levels` is "the broad-parent case's whole
    expression" (SPEC:401-404): a decision whose evidence reaches deeper than the
    node chosen names the levels it deliberately left unfilled. This asserted
    `filled == set()` and said so as a known gap -- every decision the pipeline
    wrote set `supported_depth == node_depth` and an EMPTY tuple, so a placement
    on a shallower approved parent was byte-identical to one on a fully-supported
    child, which is `104` §18.2 gap 11's own sentence: "the shallow-decision
    fields are identical at all six writers".

    `place_file_steps` is the producer, through `_levels_not_filled`, and the
    other five writers are unchanged: an abstention, a residual decision and a
    decision the person made are none of them a file filed short of the chain the
    rules built. ONE is asserted rather than merely non-zero, because a second
    writer would be a second answer to "which levels were left unfilled" and the
    two would drift.
    """
    from placement.records import DecisionDepth

    trees = _modules()
    filled = set()
    for name, tree in trees.items():
        for node in ast.walk(tree):
            if (isinstance(node, ast.keyword)
                    and node.arg == "unsupported_levels"
                    and not (isinstance(node.value, ast.Tuple)
                             and not node.value.elts)):
                filled.add(name)
    assert filled == {"pipeline.py"}
    # The record's own refusal, unchanged and still asserted: the producer fills
    # the levels WITHOUT moving `supported_depth` past `node_depth`, so the shape
    # the record calls malformed stays malformed.
    with pytest.raises(Exception):
        DecisionDepth(node_depth=1, supported_depth=2, unsupported_levels=())


# --- P11 declares none of P10's record types ------------------------------------


def test_p11s_p10_fixture_declares_no_record_class_of_its_own():
    """The hand-built double, at P11's own boundary.

    `tests/p11/p10_fixtures.py` DECLARED six of P10's record classes --
    `NodeContext`, `AnchorExcerpt`, `Restrictions`, `DestinationProfile`,
    `FreezeRecord`, `FrozenTree` -- while `tree_design.profiles` and
    `tree_design.freeze` were unbuilt. Field for field identical to P10's, and
    therefore green: P11's whole suite could have gone on passing against a shape
    P10 had changed, and nothing anywhere would have said so. That is the "test
    that builds its own record instead of using the production builder" shape,
    and it is the one this project has paid for repeatedly.

    P10 ships them now. The check is on `__module__` rather than on `is`, for the
    reason `test_p11_vocabulary.py` records: identity is not stable across a
    re-import, and `__module__` says exactly the thing that matters -- who
    DECLARED this type.
    """
    from p11 import p10_fixtures

    owners = {
        "NodeContext": "tree_design.profiles",
        "AnchorExcerpt": "tree_design.profiles",
        "Restrictions": "tree_design.profiles",
        "DestinationProfile": "tree_design.profiles",
        "FreezeRecord": "tree_design.freeze",
        "FrozenTree": "tree_design.freeze",
        "Node": "tree_design.records",
        "ExpectedValue": "tree_design.records",
        "TemplateContext": "tree_design.records",
    }
    for name, owner in owners.items():
        assert getattr(p10_fixtures, name).__module__ == owner, name

    # And structurally: the file declares no class at all, so a seventh mirror
    # cannot appear beside the six that were removed.
    source = ast.parse(
        (Path(__file__).resolve().parent / "p10_fixtures.py").read_text(
            encoding="utf-8"))
    assert [node.name for node in ast.walk(source)
            if isinstance(node, ast.ClassDef)] == []


def test_the_mirror_scan_would_catch_a_redeclared_record():
    # The negative twin. A check keyed on the NAME being importable would pass
    # over a local class of the same name, which is precisely what was there.
    tree = ast.parse("@dataclass(frozen=True)\nclass FrozenTree:\n    nodes: tuple\n")
    assert [node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)] == ["FrozenTree"]

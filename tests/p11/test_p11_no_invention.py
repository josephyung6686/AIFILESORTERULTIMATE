"""SPEC:24-27's three prohibitions, enforced over every module in `src/placement/`.

By AST and by runtime introspection, never by text search. A text search matches
comments and docstrings, and scanning source text for a token has produced a false
result nine times on this project -- so every scan below excludes docstrings by
node identity and says which nodes it excluded.

Each guard has a NEGATIVE TWIN. A guard that fires on a violation also passes when
it fires on everything, and only the twin tells the two apart.
"""
from __future__ import annotations

import ast
import dataclasses
from pathlib import Path

import pytest

from placement import vocabulary as v

PLACEMENT_ROOT = Path(__file__).resolve().parents[2] / "src" / "placement"


def _modules() -> dict[str, ast.Module]:
    return {path.name: ast.parse(path.read_text(encoding="utf-8"))
            for path in sorted(PLACEMENT_ROOT.glob("*.py"))}


def _docstring_ids(tree: ast.AST) -> set[int]:
    """The string constants that are DOCSTRINGS, by node identity.

    Excluding them is what makes an AST scan different from a grep: a module that
    merely names `several_legal_nodes_plausible` in prose has not spelled it.
    """
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                ids.add(id(body[0].value))
    return ids


def _key_ids(tree: ast.AST) -> set[int]:
    """Dict keys and subscript keys: FIELD NAMES that happen to share a spelling."""
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            ids.add(id(node.slice))
        if isinstance(node, ast.Dict):
            ids.update(id(key) for key in node.keys
                       if isinstance(key, ast.Constant))
    return ids


def _calls(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return names


def _imports(tree: ast.AST) -> set[str]:
    """Every dotted name this module imports, as `module.name` and as `module`."""
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
            found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


# --- no invented number ------------------------------------------------------------

#: The exemptions, by BINDING and not by file. An exemption granted to a whole
#: module is a hole the size of the module: exempting `scoring.py` outright let a
#: threshold hide in `needs_model_call`'s signature and this guard stayed green,
#: which is how it was found.
#:
#: `scoring._CHANNEL_WEIGHT` binds structural weights over §6.3's channels -- "a
#: direct fact outweighs a group membership outweighs a relationship, which is
#: §3.13's own ordering" -- and the values are PINNED below.
#: `fixtures.py` binds golden RECORDS whose witness figures are data, and the
#: test below proves nothing importable from it can be read as configuration.
_DECLARED_MODULE_NUMBERS: dict[str, set[str]] = {
    "scoring.py": {"_CHANNEL_WEIGHT"},
    "fixtures.py": {"EXACT_PLACEMENT", "CORRECT_ABSTENTION",
                    "RESIDUAL_LEAVE_IN_PLACE", "BUDGET_DEFERRAL",
                    "PROTECTED_PLACEMENT"},
}


def _targets_of(node: ast.stmt) -> set[str]:
    names = set()
    for target in (node.targets if isinstance(node, ast.Assign)
                   else [node.target]):
        if isinstance(target, ast.Name):
            names.add(target.id)
    return names


def _bound_numbers(tree: ast.Module, exempt: set[str] = frozenset()
                   ) -> list[tuple[int, object]]:
    """Numbers bound at module level or as a default argument.

    Those are the two places a threshold can hide and still be reachable from
    every call: a module constant is read by every function in the file, and a
    default is applied to every caller that forgot the argument. §6.10's two
    thresholds and §8.6's seven ceilings are injected precisely so that neither
    can happen, and this is the guard that says so.
    """
    hits = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            if _targets_of(node) & exempt:
                continue
            hits.extend(
                (child.lineno, child.value) for child in ast.walk(node)
                if isinstance(child, ast.Constant)
                and isinstance(child.value, (int, float))
                and not isinstance(child.value, bool)
                and child.value not in (0, 1))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defaults = list(node.args.defaults) + [
                item for item in node.args.kw_defaults if item is not None]
            for default in defaults:
                hits.extend(
                    (child.lineno, child.value) for child in ast.walk(default)
                    if isinstance(child, ast.Constant)
                    and isinstance(child.value, (int, float))
                    and not isinstance(child.value, bool)
                    and child.value not in (0, 1))
    return hits


def test_no_threshold_ceiling_or_weight_hides_in_a_constant_or_a_default():
    offenders = {
        name: _bound_numbers(tree, _DECLARED_MODULE_NUMBERS.get(name, frozenset()))
        for name, tree in _modules().items()}
    assert {name: hits for name, hits in offenders.items() if hits} == {}


def test_the_exemptions_are_bindings_and_never_whole_modules():
    # The negative twin for the exemption itself. Every exempt name must still be
    # a real module-level binding, so an exemption cannot outlive the constant it
    # was granted for and start covering something new.
    trees = _modules()
    for name, exempt in _DECLARED_MODULE_NUMBERS.items():
        bound = set()
        for node in trees[name].body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                bound |= _targets_of(node)
        assert exempt <= bound, (name, exempt - bound)


def test_the_one_exemption_is_declared_and_its_values_are_pinned():
    # The exemption is not a hole: §6.3's channel weights are named, documented
    # as structural rather than tuned, and pinned here -- so a change to one of
    # them breaks this test instead of silently re-ranking every candidate.
    from placement.scoring import _CHANNEL_WEIGHT, _MAX_WEIGHT
    from placement.retrieval import (
        ACCEPTED_GROUP, DIRECT_FACT, GRAPH_RELATIONSHIP, NON_DECIDING_CHANNELS,
        STRUCTURAL_RELATIONSHIP,
    )

    assert _CHANNEL_WEIGHT == {DIRECT_FACT: 3, ACCEPTED_GROUP: 2,
                               GRAPH_RELATIONSHIP: 1, STRUCTURAL_RELATIONSHIP: 1}
    assert _MAX_WEIGHT == 7
    # The two non-deciding channels contribute nothing at all, which is §6.5's
    # rule and not a weight of zero somebody could raise.
    assert not set(NON_DECIDING_CHANNELS) & set(_CHANNEL_WEIGHT)


def test_the_number_scan_would_catch_a_threshold_in_a_signature():
    # The negative twin. A scan that only looked at module level would pass over
    # a default argument, which is the harder of the two to notice on review.
    tree = ast.parse("def place(conn, *, threshold=0.62):\n    return threshold\n")
    assert _bound_numbers(tree) == [(1, 0.62)]
    assert _bound_numbers(ast.parse("SCALE = 1\nZERO = 0\n")) == []


def test_the_golden_fixtures_publish_records_and_never_a_number():
    # `fixtures.py` is exempt from the scan above because its records carry
    # witness figures. That is only safe if nothing importable from it can be
    # read as configuration, so every public binding is a record, a tuple of
    # records, or a string.
    from placement import fixtures
    from placement.records import PlacementDecision

    for name, value in vars(fixtures).items():
        if name.startswith("_") or callable(value) or isinstance(value, type):
            continue
        if name in {"annotations"}:
            continue
        assert isinstance(value, (str, PlacementDecision, tuple)), (name, value)


# --- no second spelling of another part's value --------------------------------------


def _p8_reason_codes() -> set[str]:
    from llm_harness.vocabulary import (
        ALL_REASON_CODES, SITE_C_REASON_CODES, SITE_D_REASON_CODES,
    )

    return set(ALL_REASON_CODES) | set(SITE_C_REASON_CODES) | set(SITE_D_REASON_CODES)


def _value_literals(tree: ast.Module, wanted: set[str]) -> list[tuple[int, str]]:
    skip = _docstring_ids(tree) | _key_ids(tree)
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and node.value in wanted and id(node) not in skip]


def test_no_placement_module_spells_one_of_p8s_reason_codes():
    # P8 owns Site C's fifteen checks and Site D's; a P11 module spelling one of
    # their codes is a second opinion with no way to be reconciled. `p8_seam.py`
    # IMPORTS three of them by name, which is carrying and not spelling.
    codes = _p8_reason_codes()
    offenders = {name: _value_literals(tree, codes)
                 for name, tree in _modules().items()}
    assert {name: hits for name, hits in offenders.items() if hits} == {}


def _p11_closed_values() -> set[str]:
    """Every value P11 publishes in one of its own closed vocabularies."""
    found: set[str] = set()
    for name, value in vars(v).items():
        if name.startswith("_"):
            continue
        if isinstance(value, tuple) and value and all(
                isinstance(item, str) for item in value):
            found |= set(value)
    return found


def _module_level_bindings(tree: ast.Module) -> set[int]:
    """String constants bound directly to a module-level name.

    That is the "pinned, not bound" pattern `learning.py` uses for P1's
    correction scopes and `fixtures.py` for P7's handling classes: the owner
    publishes a closed tuple and no per-member constant, so the value is spelled
    ONCE, at module level, beside an assertion that it is still a member. What
    the guard forbids is the other case -- a literal inside a call, a comparison
    or a record construction, where it is a spelling nobody declared.
    """
    ids = set()
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            if isinstance(node.value, ast.Constant):
                ids.add(id(node.value))
    return ids


def test_no_placement_module_respells_a_p11_closed_value_in_a_call():
    owned = _p11_closed_values()
    offenders = {}
    for name, tree in _modules().items():
        if name == "vocabulary.py":
            continue
        skip = _module_level_bindings(tree)
        hits = [hit for hit in _value_literals(tree, owned)
                if hit not in [(node.lineno, node.value)
                               for node in ast.walk(tree)
                               if isinstance(node, ast.Constant)
                               and id(node) in skip]]
        if hits:
            offenders[name] = hits
    assert offenders == {}


def test_the_declared_spellings_are_pinned_to_their_owners_tuples():
    # The other half. A declared spelling is only safe while it is still a member
    # of the set it was declared from, and both modules assert that at import --
    # so this test proves the assertions exist rather than trusting the comment.
    from database_agent.events import CORRECTION_SCOPES
    from placement import fixtures, learning

    assert {learning.CORPUS, learning.NODE} <= set(CORRECTION_SCOPES)
    assert {fixtures.PERSONAL_NON_SENSITIVE,
            fixtures.SENSITIVE_PERSONAL} <= set(v.CLASSES)


def test_the_respelling_scan_reads_values_and_not_field_names():
    # The negative twin, and the reason this guard can be trusted when it stays
    # silent. A check that flagged `body["residual"]` would report a defect on
    # every module that reads a record field.
    tree = ast.parse('X = "place"\nvalue = body["place"]\nf(outcome="place")\n')
    skip = _module_level_bindings(tree)
    hits = _value_literals(tree, {"place"})
    assert [line for line, _ in hits] == [1, 3]
    assert len(skip) == 1


# --- no path, no deletion, no expiry -------------------------------------------------

_FORBIDDEN_FIELDS = {
    "path", "resolved_path", "existing_path", "filesystem_path", "delete",
    "deleted", "disposable", "expiry", "expires_at", "ttl", "lifetime",
}


def _published_records() -> list[type]:
    import placement.groups as groups
    import placement.index as index
    import placement.pipeline as pipeline
    import placement.records as records
    import placement.residual as residual
    import placement.retrieval as retrieval

    found = []
    for module in (records, index, residual, groups, retrieval, pipeline):
        for value in vars(module).values():
            if isinstance(value, type) and dataclasses.is_dataclass(value):
                found.append(value)
    return found


def test_no_published_record_can_hold_a_path_a_deletion_or_an_expiry():
    # §7.11 and B3: P11 names a node and P12 resolves a path; deletion and expiry
    # are forbidden outright. The record SHAPE is what makes that structural --
    # a field that cannot exist cannot be filled in by a later edit.
    assert _published_records(), "the record scan found no dataclasses at all"
    for record in _published_records():
        names = {f.name for f in dataclasses.fields(record)}
        assert not names & _FORBIDDEN_FIELDS, (record.__name__,
                                               names & _FORBIDDEN_FIELDS)


def test_the_record_scan_would_catch_a_path_field():
    @dataclasses.dataclass(frozen=True)
    class _Leaky:
        node_id: str
        resolved_path: str

    names = {f.name for f in dataclasses.fields(_Leaky)}
    assert names & _FORBIDDEN_FIELDS == {"resolved_path"}


_FILESYSTEM_MUTATIONS = {
    "rename", "replace", "move", "unlink", "rmtree", "remove", "rmdir",
    "mkdir", "write_text", "write_bytes", "copy", "copy2", "copyfile", "chmod",
}


def test_no_placement_module_can_move_delete_or_write_a_file():
    # P11 moves nothing. `dataclasses.replace` is not a filesystem call and is
    # excluded by NAME rather than by hope: it is reached as `dataclasses.replace`
    # or as a bare `replace`, and both are checked below.
    offenders = {}
    for name, tree in _modules().items():
        mutating = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Attribute):
                base = func.value
                owner = base.id if isinstance(base, ast.Name) else None
                if owner in {"dataclasses", "dc"}:
                    continue
                if func.attr in _FILESYSTEM_MUTATIONS:
                    mutating.add((node.lineno, func.attr))
            elif isinstance(func, ast.Name) and func.id == "open":
                mutating.add((node.lineno, "open"))
        if mutating:
            offenders[name] = sorted(mutating)
    assert offenders == {}


def test_the_filesystem_scan_would_catch_a_move():
    tree = ast.parse("import shutil\nshutil.move(a, b)\ndataclasses.replace(x)\n")
    mutating = [node.func.attr for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _FILESYSTEM_MUTATIONS
                and not (isinstance(node.func.value, ast.Name)
                         and node.func.value.id == "dataclasses")]
    assert mutating == ["move"]


# --- no construction of another part's record ------------------------------------------

_NOT_OURS_TO_BUILD = {
    "Node", "ExpectedValue", "FrozenTree", "DestinationProfile", "FreezeRecord",
    "Group", "Membership", "GroupAcceptance", "AnchorFact",
    "Dossier", "ClassificationRecord", "Policy",
}


def test_no_placement_module_constructs_a_p7_p9_p10_or_p8_record():
    # P11 reads these and never mints one. P10 decides what a node is, P9 what a
    # group is, P7 what a classification is, and P8 what a dossier is.
    offenders = {name: sorted(_calls(tree) & _NOT_OURS_TO_BUILD)
                 for name, tree in _modules().items()}
    assert {name: hits for name, hits in offenders.items() if hits} == {}


def test_the_construction_scan_would_catch_a_minted_node():
    assert _calls(ast.parse("x = Node(node_id='n')")) & _NOT_OURS_TO_BUILD == {"Node"}


# --- one author, one subsystem ---------------------------------------------------------


def test_the_subsystem_name_is_written_in_exactly_one_place():
    # M8: P1 writes the event, P11 authors it. A second module spelling `P11`
    # into an append would make two authors of one subsystem's log.
    homes = {name for name, tree in _modules().items()
             if _value_literals(tree, {"P11"})}
    assert homes == {"events.py"}
    from placement.events import SUBSYSTEM

    assert SUBSYSTEM == "P11"


# --- the mission, over every record P11 publishes -----------------------------------------
#
# Done-means 2, 5 and 15 as prohibitions rather than behaviours, asserted over the
# golden fixtures AND over the decisions the pipeline actually produced. Fixtures
# alone would prove only that somebody can hand-build a compliant record.


def _every_decision(conn) -> list:
    from placement.fixtures import GOLDEN_DECISIONS
    from placement.store import decisions_for_plan

    produced = list(decisions_for_plan(conn, plan_version="plan-1"))
    assert produced, "the run under test wrote no decision at all"
    return list(GOLDEN_DECISIONS) + produced


@pytest.fixture()
def a_real_run(p11_conn):
    """A corpus actually run, so the mission guards judge produced records."""
    from p11.test_p11_pipeline import (
        _corpus, _decide, _partition, _policy, _classify, _seeded, _review,
        _sites, _verdict, _inputs, _evidence,
    )
    from database_agent.budget import set_ceiling
    from llm_harness.budgets import create_budget_schema
    from llm_harness.schema import create_llm_schema
    from placement.config import CEILINGS
    from placement.index import build_destination_index
    from p11.conftest import FIXED_CLOCK
    from p11.p10_fixtures import FROZEN_TREE

    create_llm_schema(p11_conn)
    create_budget_schema(p11_conn)
    for key in CEILINGS.values():
        set_ceiling(p11_conn, key, 8)
    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=FIXED_CLOCK)
    _seeded(p11_conn)
    _corpus(p11_conn, group_ids=("g-columbia",),
            evidence_for=lambda file_id: _evidence())
    return p11_conn


def test_every_decision_shows_evidence_reason_uncertainty_and_reversibility(
        a_real_run):
    import dataclasses

    for decision in _every_decision(a_real_run):
        # Three ways a decision can show its basis, and every decision must
        # have one. Evidence for a placement; an abstention reason for a refusal;
        # and, for a §7 decision that deliberately does nothing, the residual
        # context -- which names the set and the CHOICE THE USER MADE about it.
        # `leave_in_place` has no evidence and is not an abstention, and its
        # reason is exactly that the user asked for the set to be reviewed.
        shown = bool(decision.matching_facts or decision.group_support
                     or decision.graph_anchors)
        assert (shown or decision.abstention_reason is not None
                or decision.residual is not None), decision.decision_id
        assert decision.explanation.strip(), decision.decision_id
        assert decision.two_condition is not None, decision.decision_id
        assert decision.review_policy in v.REVIEW_POLICIES, decision.decision_id
        names = {f.name for f in dataclasses.fields(decision)}
        assert {"supersedes", "superseded_by", "supersede_reason"} <= names


def test_an_abstention_is_a_complete_record_and_never_an_empty_one(a_real_run):
    # §6.10: correct abstention is a SUCCESSFUL outcome. A record that merely
    # said "no" would be silence with a field name on it.
    abstentions = [d for d in _every_decision(a_real_run)
                   if d.outcome == v.ABSTAIN]
    assert abstentions, "the run produced no abstention to judge"
    for decision in abstentions:
        assert decision.abstention_reason in v.ABSTENTION_REASONS
        assert decision.destination is None
        assert decision.two_condition.support_threshold > 0
        assert decision.explanation.strip()
        # What it looked at is still on the record, so a reviewer can ask why.
        assert decision.alternatives is not None
        assert decision.conflicts_considered is not None


def test_a_decision_resting_on_protected_material_is_never_auto_eligible(
        a_real_run):
    for decision in _every_decision(a_real_run):
        if decision.privacy.protected:
            assert decision.review_policy != v.AUTO_ELIGIBLE, decision.decision_id


def test_the_protected_check_has_a_protected_record_to_judge():
    # The negative twin. Without one protected decision in the set, the guard
    # above passes over a corpus in which nothing was ever protected.
    from placement.fixtures import GOLDEN_DECISIONS

    assert any(d.privacy.protected for d in GOLDEN_DECISIONS)


def test_a_budget_deferral_renders_differently_from_an_evidential_abstention():
    # §8.6, and the two halves that make it structural: the record pairs
    # `deferred_stage` with `budget_deferred` both ways, and P2's envelope
    # carries a THIRD result so a deferral is never graded as a judgement.
    from placement.fixtures import BUDGET_DEFERRAL, CORRECT_ABSTENTION
    from placement.stage_output import envelope_for, result_of

    assert BUDGET_DEFERRAL.abstention_reason == v.BUDGET_DEFERRED
    assert BUDGET_DEFERRAL.deferred_stage == v.PLACEMENT_SCORING
    assert CORRECT_ABSTENTION.deferred_stage is None
    assert result_of(BUDGET_DEFERRAL) != result_of(CORRECT_ABSTENTION)
    assert envelope_for(BUDGET_DEFERRAL) != envelope_for(CORRECT_ABSTENTION)
    assert envelope_for(BUDGET_DEFERRAL) == (v.P2_DEFERRED, v.P2_CEILING_REACHED)


def test_no_decision_expresses_a_deletion_an_expiry_or_a_path(a_real_run):
    # §7.11. Checked over the VALUES and not only the field names: a record whose
    # shape cannot hold a path can still carry one inside an explanation string,
    # and P12 is the part that resolves a path.
    import json
    import dataclasses

    for decision in _every_decision(a_real_run):
        body = json.dumps(dataclasses.asdict(decision))
        assert "/Users/" not in body, decision.decision_id
        assert not any(token in body for token in
                       ('"path"', '"expiry"', '"ttl"', '"disposable"')), (
            decision.decision_id)


def test_every_place_names_a_node_the_frozen_tree_accepts(a_real_run):
    # Done-means 2: no destination was invented. Every `place` names a node in
    # `legal_destination_ids`, and an `ignored` node was never retrievable.
    from placement.index import legal_node_ids
    from placement.store import decisions_for_plan

    legal = legal_node_ids(a_real_run, plan_version="plan-1")
    assert "n-ignored" not in legal
    placed = [d for d in decisions_for_plan(a_real_run, plan_version="plan-1")
              if d.outcome == v.PLACE]
    for decision in placed:
        assert decision.destination.node_id in legal, decision.decision_id

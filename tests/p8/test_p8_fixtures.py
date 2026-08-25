"""P8-owned neighbour fixtures: recorded pairs, no P9/P10/P11, injections fail closed."""
from __future__ import annotations

import ast
import inspect
from collections import Counter
from pathlib import Path

import llm_harness
from llm_harness.fixtures import (
    SITE_B_OUTCOME_PAIRS,
    SITE_B_REASON_PAIRS,
    SITE_C_OUTCOME_PAIRS,
    SITE_C_REASON_PAIRS,
    SITE_D_OUTCOME_PAIRS,
    SITE_D_REASON_PAIRS,
    SITE_D_SUPPORT_RULE_PAIR,
    SITE_E_OUTCOME_PAIRS,
)
from llm_harness.group_validation import validate_group_response
from llm_harness.placement_validation import (
    PlacementDependencies,
    ResidualDependencies,
    revalidate_for_plan,
    validate_placement_response,
    validate_residual_response,
)
from llm_harness.template_validation import (
    TemplateDependencies,
    validate_template_response,
)
from llm_harness.vocabulary import (
    RESIDUAL_ACTIONS,
    SITE_B_REASON_CODES,
    SITE_C_REASON_CODES,
    SITE_D_REASON_CODES,
)

_SRC = Path(__file__).resolve().parents[2] / "src" / "llm_harness"
_BANNED_NEIGHBOURS = frozenset({
    "grouping", "placement", "templates", "tree_design", "p9", "p10", "p11",
})


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_public_surface_is_unchanged():
    assert llm_harness.__all__ == [
        "Dossier",
        "P8Verdict",
        "Refusal",
        "ValidationUnavailable",
        "NeedsConsent",
    ]
    assert not hasattr(llm_harness, "run_call")


def test_fixtures_do_not_import_p9_p10_p11():
    roots = _imported_roots(_SRC / "fixtures.py")
    assert roots.isdisjoint(_BANNED_NEIGHBOURS)
    for name in ("grouping", "placement", "templates"):
        assert name not in roots


def test_site_validators_do_not_import_p9_p10_p11():
    for filename in (
        "group_validation.py", "placement_validation.py", "template_validation.py",
    ):
        roots = _imported_roots(_SRC / filename)
        assert roots.isdisjoint(_BANNED_NEIGHBOURS), filename


def test_one_recorded_pair_per_site_b_reason_code():
    assert tuple(pair.expected_reasons[0] for pair in SITE_B_REASON_PAIRS) == (
        SITE_B_REASON_CODES
    )
    assert Counter(pair.expected_reasons[0] for pair in SITE_B_REASON_PAIRS) == (
        Counter(SITE_B_REASON_CODES)
    )


def test_one_recorded_pair_per_site_c_reason_code():
    assert tuple(pair.expected_reasons[0] for pair in SITE_C_REASON_PAIRS) == (
        SITE_C_REASON_CODES
    )


def test_one_recorded_pair_per_site_d_reason_code():
    assert tuple(pair.expected_reasons[0] for pair in SITE_D_REASON_PAIRS) == (
        SITE_D_REASON_CODES
    )


def test_each_site_has_direct_context_weak_reject_and_unknown_pairs():
    for pairs in (
        SITE_B_OUTCOME_PAIRS,
        SITE_C_OUTCOME_PAIRS,
        SITE_D_OUTCOME_PAIRS,
        SITE_E_OUTCOME_PAIRS,
    ):
        names = tuple(pair.name for pair in pairs)
        assert names == (
            "direct_accept", "context_accept", "weak", "reject", "unknown",
        )


def test_site_d_support_rule_fixture_is_present_and_not_a_reason_code():
    assert SITE_D_SUPPORT_RULE_PAIR.name == "site_d_support_rule"
    assert SITE_D_SUPPORT_RULE_PAIR.expected_reasons == ()


def test_placement_injections_have_no_defaults():
    for cls in (PlacementDependencies, ResidualDependencies, TemplateDependencies):
        for field in inspect.signature(cls).parameters.values():
            assert field.default is inspect.Parameter.empty, (cls, field.name)


def test_validate_placement_requires_dependencies_with_no_default():
    params = inspect.signature(validate_placement_response).parameters
    assert params["dependencies"].default is inspect.Parameter.empty
    assert params["dependencies"].kind is inspect.Parameter.KEYWORD_ONLY


def test_validate_residual_requires_dependencies_with_no_default():
    params = inspect.signature(validate_residual_response).parameters
    assert params["dependencies"].default is inspect.Parameter.empty
    assert "residual_actions" not in params
    assert "controlled_actions" not in params


def test_validate_template_requires_schema_validator_with_no_default():
    params = inspect.signature(validate_template_response).parameters
    assert params["dependencies"].default is inspect.Parameter.empty


def test_revalidate_for_plan_requires_current_identities_with_no_defaults():
    params = inspect.signature(revalidate_for_plan).parameters
    for name in (
        "current_plan_version",
        "current_evidence_snapshot_id",
        "dependencies",
    ):
        assert params[name].default is inspect.Parameter.empty
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY


def test_residual_controlled_set_is_the_task1_constants():
    assert RESIDUAL_ACTIONS == (
        "return_to_confirmed_domain_group",
        "return_to_accepted_graph_or_purpose_packet",
        "choose_approved_residual_destination",
        "choose_approved_broad_parent_branch",
        "mark_review_later",
        "leave_in_current_location",
        "mark_protected_or_unsupported",
        "abstain",
    )


def test_site_validators_import_universal_validation_and_do_not_copy_it():
    for filename in (
        "group_validation.py", "placement_validation.py", "template_validation.py",
    ):
        source = (_SRC / filename).read_text()
        assert "from llm_harness.validation import" in source
        assert "def validate_response(" not in source


def test_group_validation_does_not_take_tree_oracles():
    params = inspect.signature(validate_group_response).parameters
    for name in (
        "node_exists", "support_threshold", "margin_predicate",
        "sensitivity_policy", "approved_target_ids",
    ):
        assert name not in params

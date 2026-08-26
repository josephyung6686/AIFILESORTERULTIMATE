# tests/p8/test_p8_sites.py
"""P8 repair R3: one P8-owned site dispatcher, no caller-authored acceptance.

Before this task `run_call` passed `deps.site_validator` straight into
`validate_response`. A caller could hand in `lambda *a, **k: None` and every
site-specific check — invented Site-B member, invented Site-C node, invalid
Site-E schema — was skipped, while the universal citation checks still ran and
the result still looked like a real P8 verdict.

The dispatcher is now P8's. Callers inject typed *authorities* (`node_exists`,
`schema_validator`, the P6 `FactRequest`) and never an acceptance callback.
Missing or malformed authorities are `ValidationUnavailable`, never a pass.
"""
from __future__ import annotations

import ast
import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from llm_harness.fixtures import (
    SITE_B_OUTCOME_PAIRS,
    SITE_C_OUTCOME_PAIRS,
    SITE_D_OUTCOME_PAIRS,
    SITE_E_OUTCOME_PAIRS,
)
from llm_harness.records import ValidationUnavailable
from llm_harness.sites import SiteDependencies, dispatch
from llm_harness.vocabulary import (
    B_GROUP,
    C_PLACEMENT,
    D_RESIDUAL,
    E_TEMPLATE,
    REJECT,
)

HARNESS_ROOT = Path(__file__).resolve().parents[2] / "src" / "llm_harness"
RELEASED = "span-1"


def _resolver(observation_key: str) -> str | None:
    return RELEASED if observation_key.startswith("obs-") else None


def _never_contradicts(*_a, **_k) -> bool:
    return False


def _placement_dependencies(**overrides):
    from llm_harness.placement_validation import PlacementDependencies

    values = dict(
        node_exists=lambda node_id, _plan: node_id in {
            "node-legal", "node-alt", "node-hub",
        },
        support_threshold=0.0,
        margin_predicate=lambda *_a, **_k: True,
        sensitivity_policy=lambda *_a, **_k: True,
    )
    values.update(overrides)
    return PlacementDependencies(**values)


def _residual_dependencies(**overrides):
    from llm_harness.placement_validation import ResidualDependencies

    values = dict(
        node_exists=lambda node_id, _plan: node_id in {
            "node-legal", "node-parent", "group-1",
        },
        sensitivity_policy=lambda *_a, **_k: True,
        approved_target_ids=("node-legal", "node-parent", "group-1"),
    )
    values.update(overrides)
    return ResidualDependencies(**values)


def _template_dependencies(**overrides):
    from llm_harness.template_validation import TemplateDependencies

    values = dict(schema_validator=lambda payload: True)
    values.update(overrides)
    return TemplateDependencies(**values)


def _site_dependencies(**overrides) -> SiteDependencies:
    values = dict(
        fact=None,
        placement=_placement_dependencies(),
        residual=_residual_dependencies(),
        template=_template_dependencies(),
    )
    values.update(overrides)
    return SiteDependencies(**values)


def _dispatch(dossier, response_bytes, *, conn=None, site_dependencies=None, **overrides):
    values = dict(
        evidence_resolver=_resolver,
        contradicts=_never_contradicts,
        model_id="fixture-model",
        prompt_fingerprint="fp-1",
        dossier_builder="fixture",
        release_audit_id=17,
        policy_version="policy-1",
        apply_consequence=True,
    )
    values.update(overrides)
    return dispatch(
        conn,
        dossier,
        response_bytes,
        site_dependencies=site_dependencies or _site_dependencies(),
        **values,
    )


def _first(pairs, site):
    return next(pair for pair in pairs if pair.site == site)


def _permissive(*_a, **_k):
    """The exact callback shape a caller used to be able to inject."""
    return None


# --- the public path carries no acceptance callback ------------------------------


def test_call_dependencies_no_longer_carry_a_site_validator():
    from llm_harness.harness import CallDependencies

    names = {field.name for field in dataclasses.fields(CallDependencies)}
    assert "site_validator" not in names
    assert "site_dependencies" in names


def test_no_public_p8_callable_accepts_a_site_validator():
    import llm_harness

    for name in llm_harness.__all__:
        member = getattr(llm_harness, name)
        if not callable(member) or isinstance(member, type):
            continue
        assert "site_validator" not in inspect.signature(member).parameters, name


def test_replay_takes_typed_authorities_and_not_a_validator_callback():
    from llm_harness.stage_output import replay_recorded_response

    parameters = inspect.signature(replay_recorded_response).parameters
    assert "site_validator" not in parameters
    assert "site_dependencies" in parameters


def test_no_site_validator_argument_comes_from_outside_p8():
    """`validate_response` keeps the parameter; only P8's own functions may fill it.

    A `site_validator=` whose value is a lambda, or a parameter of the enclosing
    function, or an attribute of one (`deps.site_validator`), is a caller-authored
    acceptance callback wearing P8's argument name.
    """
    offenders = []
    for path in sorted(HARNESS_ROOT.glob("*.py")):
        if path.name == "validation.py":
            continue
        tree = ast.parse(path.read_text())
        for owner in ast.walk(tree):
            if not isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = {
                arg.arg
                for group in (owner.args.args, owner.args.kwonlyargs,
                              owner.args.posonlyargs)
                for arg in group
            }
            for node in ast.walk(owner):
                if not (isinstance(node, ast.keyword) and node.arg == "site_validator"):
                    continue
                value = node.value
                bad = (
                    isinstance(value, ast.Lambda)
                    or (isinstance(value, ast.Name) and value.id in params)
                    or (isinstance(value, ast.Attribute)
                        and isinstance(value.value, ast.Name)
                        and value.value.id in params)
                )
                if bad:
                    offenders.append(f"{path.name}:{value.lineno}")
    assert offenders == [], offenders


# --- one adversarial bypass test per site ----------------------------------------


def test_a_permissive_callback_cannot_reach_site_b(tmp_path):
    """Site B: an invented member must be rejected however the caller is shaped."""
    pair = _first(SITE_B_OUTCOME_PAIRS, B_GROUP)
    body = json.loads(pair.response_bytes)
    body["claims"][0]["payload"]["members"] = [{"file_id": "file-invented"}]
    result = _dispatch(
        pair.dossier,
        json.dumps(body, separators=(",", ":")).encode("utf-8"),
        site_dependencies=_site_dependencies(),
    )
    verdicts, _ = result
    assert verdicts[0].outcome == REJECT
    # And the old bypass shape is not accepted as a dependency at all.
    with pytest.raises((TypeError, ValueError)):
        SiteDependencies(
            fact=None, placement=_permissive, residual=None, template=None,
        )


def test_site_c_invented_node_is_rejected_by_the_built_in_dispatcher():
    pair = _first(SITE_C_OUTCOME_PAIRS, C_PLACEMENT)
    body = json.loads(pair.response_bytes)
    body["claims"][0]["payload"]["destination"] = "node-invented"
    verdicts, _ = _dispatch(
        pair.dossier, json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )
    assert verdicts[0].outcome == REJECT


def test_site_e_invalid_schema_is_rejected_by_the_built_in_dispatcher():
    pair = _first(SITE_E_OUTCOME_PAIRS, E_TEMPLATE)
    verdicts, _ = _dispatch(
        pair.dossier,
        pair.response_bytes,
        site_dependencies=_site_dependencies(
            template=_template_dependencies(schema_validator=lambda payload: False),
        ),
    )
    assert verdicts[0].outcome == REJECT


def test_site_d_invented_target_is_rejected_by_the_built_in_dispatcher():
    pair = _first(SITE_D_OUTCOME_PAIRS, D_RESIDUAL)
    body = json.loads(pair.response_bytes)
    body["claims"][0]["payload"]["target"] = "node-invented"
    verdicts, _ = _dispatch(
        pair.dossier, json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )
    assert verdicts[0].outcome == REJECT


# --- missing authorities are unavailable, never a pass ---------------------------


@pytest.mark.parametrize(
    ("site", "pairs", "cleared"),
    [
        (C_PLACEMENT, SITE_C_OUTCOME_PAIRS, "placement"),
        (D_RESIDUAL, SITE_D_OUTCOME_PAIRS, "residual"),
        (E_TEMPLATE, SITE_E_OUTCOME_PAIRS, "template"),
    ],
)
def test_missing_site_authorities_are_validation_unavailable(site, pairs, cleared):
    pair = _first(pairs, site)
    result = _dispatch(
        pair.dossier,
        pair.response_bytes,
        site_dependencies=_site_dependencies(**{cleared: None}),
    )
    assert isinstance(result, ValidationUnavailable)
    assert cleared in " ".join(result.missing)


def test_a_malformed_authority_bundle_is_unavailable_not_a_pass():
    pair = _first(SITE_C_OUTCOME_PAIRS, C_PLACEMENT)
    result = _dispatch(
        pair.dossier,
        pair.response_bytes,
        site_dependencies=_site_dependencies(
            placement=_placement_dependencies(node_exists=None),
        ),
    )
    assert isinstance(result, ValidationUnavailable)


def test_an_unknown_call_site_has_no_validator_and_is_unavailable():
    pair = _first(SITE_B_OUTCOME_PAIRS, B_GROUP)
    dossier = pair.dossier
    forged = object.__new__(type(dossier))
    for field in dataclasses.fields(dossier):
        object.__setattr__(forged, field.name, getattr(dossier, field.name))
    object.__setattr__(forged, "call_site", "Z_invented")
    result = _dispatch(forged, pair.response_bytes)
    assert isinstance(result, ValidationUnavailable)
    assert "site_validator" in " ".join(result.missing)


# --- Site A goes through P6, exactly once ----------------------------------------


def test_site_a_without_a_fact_request_is_unavailable():
    from llm_harness.sites import FactSiteDependencies

    assert "fact_request" in {
        field.name for field in dataclasses.fields(FactSiteDependencies)
    }


def test_site_a_bundle_rejects_a_bare_callable():
    from llm_harness.sites import FactSiteDependencies

    with pytest.raises((TypeError, ValueError)):
        FactSiteDependencies(fact_request=_permissive, fact_dependencies=_permissive)


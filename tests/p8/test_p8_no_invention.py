"""P8 Task 11 — no-invention guards.

P8 does not author detectors, redactors, normalizers, contradiction oracles,
tree builders, or neighbour producers. Closed vocabularies live in
`vocabulary.py` as named constants. Configurable callbacks, thresholds, and
prompts have no defaults. AST only: a comment that names `normalize(` is not
an implementation.
"""
from __future__ import annotations

import ast
import dataclasses
import importlib
import inspect
import pkgutil
import pathlib
from types import MappingProxyType

import llm_harness
from llm_harness.budgets import ScanBudget, plan_reduction
from llm_harness.eligibility import assess_call
from llm_harness.fact_validation import FactValidationDependencies, validate_fact_proposal
from llm_harness.group_validation import validate_group_response
from llm_harness.harness import CallDependencies, run_call
from llm_harness.placement_validation import (
    PlacementDependencies,
    ResidualDependencies,
    validate_placement_response,
    validate_residual_response,
)
from llm_harness.records import PromptDefinition
from llm_harness.template_validation import TemplateDependencies, validate_template_response
from llm_harness.transport import issue
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ALL_ELIGIBILITY,
    ALL_REASON_CODES,
    CALL_SITES,
    OUTCOMES,
    REDUCTION_RUNGS,
    RESIDUAL_ACTIONS,
)


HARNESS_ROOT = pathlib.Path(llm_harness.__file__).resolve().parent

#: Injection slots. A default on any of these is an authored policy.
CONFIG_PARAMETERS = frozenset({
    "normalize",
    "contradicts",
    "evidence_resolver",
    "site_validator",
    "site_dependencies",
    "fact_request",
    "fact_dependencies",
    "policy_version",
    "schema_validator",
    "model_client",
    "prompt",
    "support_threshold",
    "margin_predicate",
    "node_exists",
    "sensitivity_policy",
    "unreduced_fits",
    "summarized_fits",
    "anchors_fit",
    "split_shard_fits",
    "split_shards",
    "template_bytes",
    "response_schema_bytes",
    "shaping_policy_bytes",
    "gazetteer",
    "detector",
    "redactor",
    "max_calls_per_1000_files",
    "max_estimated_cost",
    "validation_dependencies",
    "dependencies",
})

#: Closed vocabularies are local constants. Injecting the set itself is a second home.
VOCABULARY_PARAMETERS = frozenset({
    "residual_actions",
    "controlled_actions",
    "outcomes",
    "reason_codes",
    "eligibility_reasons",
    "call_sites",
    "reduction_rungs",
    "all_reason_codes",
})

INVENTED_AUTHORITIES = frozenset({
    "detect", "detector", "Detector",
    "redact", "redactor", "Redactor", "apply_redaction",
    "normalize", "normalizer", "Normalizer",
    "contradicts", "contradiction_rule",
    "build_tree", "TreeBuilder", "freeze_tree",
    "produce_group", "build_group", "GroupProducer", "group_seed",
    "produce_placement", "place_file", "PlacementProducer",
})



def modules() -> list[pathlib.Path]:
    return sorted(HARNESS_ROOT.glob("*.py"))


def imported_modules():
    found = [llm_harness]
    for info in pkgutil.iter_modules(llm_harness.__path__):
        found.append(importlib.import_module(f"llm_harness.{info.name}"))
    return found


#: The registries below were hand-listed, which meant a new public callable or a
#: new dependency bundle simply got no no-invention check. `sites.dispatch`,
#: `dossier.build_dossier`, `SiteDependencies` and `FactSiteDependencies` were all
#: added by the live-composition repair and were all missing from the old lists.
#: They are derived now, so the sweep cannot fall behind the package.

def _p8_functions():
    """Every public function P8 defines, in the module that defines it."""
    found = {}
    for module in imported_modules():
        for name, member in vars(module).items():
            if name.startswith("_") or not inspect.isfunction(member):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue  # a re-export, counted where it is defined
            found[f"{module.__name__}.{name}"] = member
    return found


def _p8_dependency_types():
    """Every frozen authority bundle. The naming rule is the registry."""
    found = {}
    for module in imported_modules():
        for name, member in vars(module).items():
            if not (inspect.isclass(member) and dataclasses.is_dataclass(member)):
                continue
            if getattr(member, "__module__", None) != module.__name__:
                continue
            if name.endswith("Dependencies"):
                found[name] = member
    return found


DEPENDENCY_TYPES = tuple(_p8_dependency_types().values())

PUBLIC_CALLABLES = tuple(_p8_functions().values())


def _docstrings(tree: ast.AST) -> set[int]:
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                found.add(id(body[0].value))
    return found


def defined_names(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def module_level_string_bindings(path: pathlib.Path) -> dict[str, str]:
    """Public names this module *binds* to a string literal. Docstrings excluded."""
    tree = ast.parse(path.read_text(), filename=str(path))
    skip = _docstrings(tree)
    bound: dict[str, str] = {}
    for node in tree.body:
        target = None
        value = None
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target, value = node.target.id, node.value
        elif (isinstance(node, ast.Assign) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Name)):
            target, value = node.targets[0].id, node.value
        if target is None or target.startswith("_"):
            continue
        if (isinstance(value, ast.Constant) and id(value) not in skip
                and isinstance(value.value, str)):
            bound[target] = value.value
    return bound


def function_defs_named(path: pathlib.Path, names: set[str]) -> list[tuple[str, str, int]]:
    tree = ast.parse(path.read_text(), filename=str(path))
    found: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in names:
                found.append((path.name, node.name, node.lineno))
    return found


def test_the_invention_helpers_fail_on_planted_violations(tmp_path):
    planted = tmp_path / "planted_invention.py"
    planted.write_text(
        'ACCEPT_DIRECT: str = "accept_direct"\n'
        "def normalize(field, raw):\n"
        "    return raw\n"
        "def contradicts(claim, fact):\n"
        "    return False\n"
        "class Detector:\n"
        "    pass\n",
        encoding="utf-8",
    )
    assert function_defs_named(planted, {"normalize", "contradicts", "Detector"}) == [
        ("planted_invention.py", "normalize", 2),
        ("planted_invention.py", "contradicts", 4),
        ("planted_invention.py", "Detector", 6),
    ]
    bound = module_level_string_bindings(planted)
    assert bound["ACCEPT_DIRECT"] == "accept_direct"
    # A docstring mentioning normalize( must not count as a FunctionDef.
    prose = tmp_path / "prose.py"
    prose.write_text(
        '"""P8 does not invent normalize( or contradicts( implementations."""\n'
        "X = 1\n",
        encoding="utf-8",
    )
    assert function_defs_named(prose, {"normalize", "contradicts"}) == []
    assert "normalize(" not in module_level_string_bindings(prose).values()


def test_no_module_defines_normalize_or_contradicts():
    invented = []
    for path in modules():
        invented.extend(function_defs_named(path, {"normalize", "contradicts"}))
    assert invented == [], invented


def test_configurable_callbacks_thresholds_and_prompts_have_no_defaults():
    for cls in DEPENDENCY_TYPES:
        for field in dataclasses.fields(cls):
            assert field.default is dataclasses.MISSING, (cls, field.name)
            assert field.default_factory is dataclasses.MISSING, (cls, field.name)

    for field in dataclasses.fields(PromptDefinition):
        if field.name in CONFIG_PARAMETERS:
            assert field.default is dataclasses.MISSING, field.name
            assert field.default_factory is dataclasses.MISSING, field.name

    for field in dataclasses.fields(ScanBudget):
        if field.name in CONFIG_PARAMETERS:
            assert field.default is dataclasses.MISSING, field.name
            assert field.default_factory is dataclasses.MISSING, field.name

    missing_defaults = []
    for fn in PUBLIC_CALLABLES:
        for parameter in inspect.signature(fn).parameters.values():
            if parameter.name not in CONFIG_PARAMETERS:
                continue
            if parameter.default is not inspect.Parameter.empty:
                missing_defaults.append(
                    (fn.__module__, fn.__name__, parameter.name, parameter.default)
                )
    assert missing_defaults == [], missing_defaults


def test_closed_vocabularies_are_local_constants_and_are_never_injected():
    injected = []
    for fn in PUBLIC_CALLABLES:
        for parameter in inspect.signature(fn).parameters.values():
            if parameter.name in VOCABULARY_PARAMETERS:
                injected.append((fn.__name__, parameter.name))
    for cls in DEPENDENCY_TYPES:
        for field in dataclasses.fields(cls):
            if field.name in VOCABULARY_PARAMETERS:
                injected.append((cls.__name__, field.name))
    assert injected == [], injected
    assert inspect.signature(validate_residual_response).parameters.get(
        "residual_actions"
    ) is None


def test_p8_exports_no_detector_redactor_normalizer_or_producer():
    exported = set(llm_harness.__all__)
    assert exported.isdisjoint(INVENTED_AUTHORITIES)
    assert "Verdict" not in exported
    assert "ModelClient" not in exported
    assert "issue" not in exported
    defined = []
    for path in modules():
        for name in defined_names(path):
            if name in INVENTED_AUTHORITIES:
                defined.append((path.name, name))
    assert defined == [], defined
    for module in imported_modules():
        for name in vars(module):
            if name.startswith("_"):
                continue
            if name in INVENTED_AUTHORITIES:
                value = getattr(module, name)
                if inspect.isfunction(value) or inspect.isclass(value):
                    raise AssertionError((module.__name__, name))


def test_every_reason_outcome_site_reduction_value_has_one_named_home():
    vocabulary = importlib.import_module("llm_harness.vocabulary")
    home = module_level_string_bindings(HARNESS_ROOT / "vocabulary.py")
    owned = (
        set(CALL_SITES) | set(OUTCOMES) | set(REDUCTION_RUNGS)
        | set(ALL_REASON_CODES) | set(ALL_ELIGIBILITY) | set(RESIDUAL_ACTIONS)
    )
    published = {value for value in home.values() if value in owned}
    assert published == owned, owned - published

    duplicates = []
    for path in modules():
        if path.name == "vocabulary.py":
            continue
        for name, value in module_level_string_bindings(path).items():
            if value in owned:
                duplicates.append((path.name, name, value))
    assert duplicates == [], duplicates

    for module in imported_modules():
        if module.__name__ == "llm_harness.vocabulary":
            continue
        for name in (
            "CALL_SITES", "OUTCOMES", "REDUCTION_RUNGS", "ALL_REASON_CODES",
            "RESIDUAL_ACTIONS",
        ):
            if name not in vars(module):
                continue
            assert getattr(module, name) is getattr(vocabulary, name), (
                module.__name__, name,
            )


def test_no_module_holds_a_numeric_threshold_or_gazetteer():
    holders = []
    gazetteers = []
    for module in imported_modules():
        if module.__name__ == "llm_harness.fixtures":
            continue
        for name, value in vars(module).items():
            if name.startswith("_"):
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                holders.append((module.__name__, name, value))
            if isinstance(value, (tuple, list, set, frozenset, dict, MappingProxyType)):
                if value is ALL_REASON_CODES:
                    continue
                if len(value) > 20:
                    gazetteers.append((module.__name__, name, len(value)))
    assert holders == [], holders
    assert gazetteers == [], gazetteers
    assert RESIDUAL_ACTIONS  # identity home is vocabulary; used, not reinvented


def test_every_dependency_bundle_and_public_callable_is_swept():
    """R6: the sweep is derived from the package, and covers what it used to list.

    A hand-maintained registry is one contract in two places, and the second copy
    is the one that goes stale. These names were the old list; the derived sweep
    must still contain every one of them, and it must also have found the ones the
    repair added.
    """
    dependencies = _p8_dependency_types()
    for name in (
        "CallDependencies", "FactValidationDependencies", "PlacementDependencies",
        "ResidualDependencies", "TemplateDependencies",
    ):
        assert name in dependencies, name
    assert "SiteDependencies" in dependencies

    callables = _p8_functions()
    for name in (
        "llm_harness.harness.run_call",
        "llm_harness.transport.issue",
        "llm_harness.validation.validate_response",
        "llm_harness.fact_validation.validate_fact_proposal",
        "llm_harness.group_validation.validate_group_response",
        "llm_harness.placement_validation.validate_placement_response",
        "llm_harness.placement_validation.validate_residual_response",
        "llm_harness.template_validation.validate_template_response",
        "llm_harness.budgets.plan_reduction",
        "llm_harness.eligibility.assess_call",
    ):
        assert name in callables, name
    for name in (
        "llm_harness.sites.dispatch",
        "llm_harness.dossier.build_dossier",
        "llm_harness.dossier.canonical_dossier_bytes",
        "llm_harness.stage_output.replay_recorded_response",
    ):
        assert name in callables, f"the repair added {name} and the sweep missed it"

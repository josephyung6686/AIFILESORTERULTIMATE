# tests/p6/test_p6_deterministic.py
"""Done-means 17 -- every fact-producing path, with P8 absent and no model configured.

`02-segmentation-map.md`'s Wave 2 line is `P4 -> P5 -> P6  (deterministic only, no
model)`. This file is the assertion that the parenthesis is a property of the code
rather than of the diagram.

**"P8 absent" is trivially true and therefore worth nothing on its own.** There is no
P8 package in this repository, so every test in `tests/p6/` already runs with P8
absent in the same sense that it runs without a Mars lander. The three non-trivial
claims are asserted separately below: no deterministic producer TAKES a model
parameter, no deterministic producer can REACH the P8 seam, and `llm_supported` is
supplied by exactly one module.

**One thing that looks like a violation and is not.** §3.4's cache key has five parts
and two are the model's, so a deterministic fact records them as `None` rather than
omitting them, and those two names appear across `src/facts/`. They appear as
`ast.keyword` argument names, which the AST guard below does not collect, and the
signature guard is the one that binds: no producer ACCEPTS either name.

**Where this file departs from its plan section, and why.** The plan's Task 27 asserts
`propose` and `validate` are parameters of `FactResolver.__init__`. The shipped
resolver (Task 20, and Task 20's own plan text) takes no such parameters: the three
producers arrive as one `stages: Mapping[str, Stage | None]` whose key set must be
exactly `DEGRADATION_ORDER`, so the LLM route is *present-and-None*, never omitted.
Shipped code outranks the task body, so the claim is asserted in the shape the code
actually has -- and asserted by CONSTRUCTION rather than by signature, which is
stronger than the sentence it replaces.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import os
import subprocess
import sys
from pathlib import Path

import pytest

from facts.budgets import DEGRADATION_ORDER
from facts.resolver import FactResolver, StageSetInvalid
from facts.states import LLM_SUPPORTED

TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parents[1]

#: Set in the child run so the recursive test skips itself. Everything else in this
#: file is cheap and runs in both.
CHILD_MARKER = "P6_DETERMINISTIC_SUITE_CHILD"

#: Every fact-producing entry point in `facts`, module and function. This is the
#: plan's task list read off -- Tasks 8-16, 18 and 19 publish exactly these. It is
#: written out rather than discovered because a producer added later without being
#: added here would be exempt from both guards;
#: `test_the_producer_list_is_the_whole_of_facts` is the guard on that.
PRODUCERS = (
    ("facts.direct", "direct_facts"),
    ("facts.discount", "discount"),
    ("facts.rules", "apply_rules"),
    ("facts.facets", "fill_or_abstain"),
    ("facts.dates", "date_candidates"),
    ("facts.domains", "active_domains"),
    ("facts.families", "duplicate_family"),
    ("facts.families", "version_family"),
    ("facts.session", "bounded_sessions"),
    ("facts.photo_event", "photo_events"),
    ("facts.photo_event", "media_type"),
    ("facts.supersede", "supersede_fact"),
    ("facts.usable", "no_usable_facts_for"),
)

#: Modules in `facts` that are not producers: the tables, the vocabularies, the
#: reads, the seam, and the sequencer. Every module under `src/facts/` is in exactly
#: one of these two lists. `read_surface` is Task 24's and may or may not have landed
#: yet; it is a non-producer either way, and the difference below is one-sided so an
#: absent module is not an error.
NON_PRODUCERS = frozenset({
    "authorship", "budgets", "cache", "evidence", "fields", "file_facts",
    "learning", "llm_seam", "plan_versions", "read_surface", "resolver", "schema",
    "states", "stage_output", "unresolved", "values", "vocabulary",
})

#: The four names that would carry a model into a deterministic producer.
MODEL_PARAMETERS = ("propose", "validate", "model_identifier", "prompt_fingerprint")


def _facts_dir() -> Path:
    return Path(inspect.getfile(importlib.import_module("facts"))).resolve().parent


def _producer_module_names() -> set[str]:
    return {name.split(".")[1] for name, _ in PRODUCERS}


def _names_in(source: str) -> set[str]:
    """Every name a piece of CODE mentions.

    An AST walk, never a text search: a text search matches comments and docstrings.
    Keyword ARGUMENT names are deliberately not collected -- see the module docstring.
    """
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
            names.update(alias.name for alias in node.names)
    return names


def _mentioned_names(module) -> set[str]:
    return _names_in(inspect.getsource(module))


def test_no_deterministic_producer_takes_a_model_parameter():
    # "no model configured", proved from the SIGNATURES rather than from one call.
    # A producer that accepted `propose` would be a fact path a caller could turn
    # into a model path without P8 existing, which §3.3 forbids outright.
    offences = []
    for module_name, function_name in PRODUCERS:
        module = importlib.import_module(module_name)
        parameters = inspect.signature(getattr(module, function_name)).parameters
        for name in MODEL_PARAMETERS:
            if name in parameters:
                offences.append(f"{module_name}.{function_name}({name}=...)")
    assert offences == []


def test_the_model_parameter_guard_can_fail():
    # Step 5's teeth proof, kept as a test rather than as a one-off manual run: the
    # guard above is run once more with `facts.llm_seam.apply_verdict` -- the one
    # entry point that legitimately takes P8's two names -- spliced into the producer
    # list, and it is REQUIRED to report it. A guard that stays green with the seam
    # in the list is asserting nothing, and Done-means 17 is the plan's largest
    # single claim.
    module = importlib.import_module("facts.llm_seam")
    parameters = inspect.signature(module.apply_verdict).parameters
    caught = [name for name in MODEL_PARAMETERS if name in parameters]
    assert caught == ["model_identifier", "prompt_fingerprint"]


def test_no_deterministic_producer_reaches_the_p8_seam():
    # §3.3: every model call is P8's. A producer that can IMPORT the seam has a path
    # to a proposal, and Done-means 17 would then rest on that path not being taken
    # rather than on it not existing.
    for module_name in sorted({name for name, _ in PRODUCERS}):
        mentioned = _mentioned_names(importlib.import_module(module_name))
        assert "facts.llm_seam" not in mentioned, module_name
        assert "llm_seam" not in mentioned, module_name


def test_the_seam_guard_can_fail():
    # The teeth of the guard above, for the same reason as `test_the_model_parameter_
    # guard_can_fail`: the collector must actually be able to SEE an `llm_seam`
    # import, in each of the three shapes one could be written in. If it cannot, the
    # guard passes over every producer for the wrong reason.
    assert "facts.llm_seam" in _names_in("import facts.llm_seam")
    assert "llm_seam" in _names_in("from facts import llm_seam")
    assert "facts.llm_seam" in _names_in("from facts.llm_seam import apply_verdict")
    # And it does NOT see the two keyword-argument names §3.4's cache key requires --
    # the false positive the module docstring warns about.
    keyword_call = "fact_cache_key(x, model_identifier=None, prompt_fingerprint=None)"
    assert "model_identifier" not in _names_in(keyword_call)
    assert "prompt_fingerprint" not in _names_in(keyword_call)


def test_only_one_module_can_supply_the_llm_supported_state():
    # §3.5: "A file fact is not inherently rule-based or LLM-based. It is the common
    # format into which both systems write their conclusions." One format, one table,
    # and the producer is a COLUMN -- so `llm_supported` is a value, and the only
    # assertion available is about which module can supply it.
    reaching: set[str] = set()
    for path in sorted(_facts_dir().glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == LLM_SUPPORTED:
                reaching.add(path.stem)
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.value, ast.Name)
                    and node.value.id in {"RELIABILITY_STATES", "STATES"}):
                reaching.add(path.stem)
    # `states` publishes the six once (Task 1); `llm_seam` is the module P8 talks to.
    assert reaching <= {"states", "llm_seam"}
    # And the guard is not vacuous: at least one module does spell it.
    assert reaching


def test_the_producer_list_is_the_whole_of_facts():
    # A guard on the two guards above: a producer module added to `src/facts/`
    # without being added to PRODUCERS would be exempt from both, silently.
    modules = {path.stem for path in _facts_dir().glob("*.py")} - {"__init__"}
    assert modules - NON_PRODUCERS == _producer_module_names()
    assert not (NON_PRODUCERS & _producer_module_names())


def test_an_absent_p8_is_an_explicit_none_and_never_an_omitted_argument():
    # Skeleton rule 4: every threshold and every injected surface is a required
    # keyword with no default. P8's route is where a default would be most tempting
    # and most wrong -- a defaulted LLM stage is a model path nobody chose to enable.
    parameters = inspect.signature(FactResolver.__init__).parameters
    for name, parameter in parameters.items():
        if name == "self":
            continue
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY, name
        assert parameter.default is inspect.Parameter.empty, name
    assert "stages" in parameters
    # Asserted by construction, not by signature: the LLM route is a KEY that must be
    # present, and `None` is how a caller says "no model configured". Omitting it is
    # refused rather than silently defaulted.
    assert "llm" in DEGRADATION_ORDER
    with pytest.raises(StageSetInvalid):
        FactResolver(**_resolver_arguments(
            stages={name: None for name in DEGRADATION_ORDER if name != "llm"}))
    resolver = FactResolver(**_resolver_arguments(
        stages={name: None for name in DEGRADATION_ORDER}))
    assert isinstance(resolver, FactResolver)


def _resolver_arguments(*, stages):
    """Every injected surface `FactResolver` requires, so the two constructions above
    differ in exactly one thing: whether the LLM route was named."""
    return {
        "stages": stages,
        "pending_fields": lambda conn, file_id, content_hash: (),
        "budget_exhausted": lambda ceiling: False,
        "model_route_permitted": lambda field_key: False,
        "record_pass": lambda conn, **kwargs: None,
        "cache_key_for": lambda file_id, content_hash: "key",
        "screen_metadata": lambda conn, file_id, content_hash: None,
    }


def test_no_p8_package_is_importable():
    # The trivial half, kept because it is Done-means 17's own words and because it
    # is what makes the three non-trivial halves above the interesting ones.
    assert importlib.util.find_spec("p8") is None
    assert importlib.util.find_spec("llm_harness") is None


@pytest.mark.skipif(os.environ.get(CHILD_MARKER) == "1",
                    reason="this IS the child run; the parent asserts on its exit code")
def test_the_whole_p6_suite_passes_with_p8_absent_and_no_model_configured():
    # Done-means 17 in its own words: "The whole of items 4-10, 13-16 and 18-27 pass
    # with P8 absent and no model configured." The only honest way to assert "the
    # whole suite" is to run the whole suite, so it is run -- in a child process, with
    # a marker that stops this one test from recursing.
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", str(TEST_DIR), "-q",
         "-p", "no:cacheprovider"],
        cwd=REPO_ROOT, env=dict(os.environ, **{CHILD_MARKER: "1"}),
        capture_output=True, text=True, timeout=900, check=False)
    assert completed.returncode == 0, completed.stdout[-4000:]
    assert " failed" not in completed.stdout

# tests/readers/test_model_routing.py
"""`83`'s three tiers, and the refusal that makes tiering mean anything.

The whole value of routing one model per kind of judgement is destroyed the first
time a call site quietly gets a tier it did not choose. `83` §4 says so in one
sentence -- *"a cheap model answering a question the expensive one was chosen for
is a wrong answer that looks exactly like a right one"* -- and every test below is
that sentence made mechanical.

So the interesting assertions here are all NEGATIVE: an unlisted call site gets a
refusal rather than a tier, a tier with no client gets a refusal rather than
another tier's client, and nothing in the module has a default to fall back to.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from llm_harness.transport import ModelClient
from llm_harness.vocabulary import A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE
from privacy.release import LOCALITIES, ModelTarget
from questions.proposal import REASONING_TIER
from readers.model_deepseek import CLOUD, PROVIDER
from readers.model_routing import (
    FAST,
    LOGIC,
    MODEL_NAME_OF_TIER,
    REASONING,
    TIERS,
    ModelRouteRefused,
    TierRouting,
    TierUnavailable,
    UnroutedCallSite,
    deepseek_routing,
)

ENDPOINT = "https://api.deepseek.example"
IDS = {REASONING: "a-reasoner", LOGIC: "a-logician", FAST: "a-sprinter"}

#: `83` §3's table, as far as the call sites that exist today. Written HERE in the
#: test and not in the module, because it is exactly the policy the composition
#: root owns: this file proves the SHAPE carries it, never that the shape knows it.
TABLE = {A_FACT: REASONING, B_GROUP: LOGIC, C_PLACEMENT: LOGIC,
         E_TEMPLATE: LOGIC, D_RESIDUAL: FAST}

ONE_TOKEN = 1


def _routing(table=None, **overrides):
    arguments = dict(api_key="k", base_url=ENDPOINT, model_id_of_tier=IDS,
                     tier_of_call_site=TABLE if table is None else table,
                     max_response_tokens=ONE_TOKEN)
    arguments.update(overrides)
    return deepseek_routing(**arguments)


# --- the tier words are `83`'s, and the repo already has one of them -----------

def test_the_three_tiers_are_the_ones_the_policy_names():
    assert TIERS == (REASONING, LOGIC, FAST)
    assert (REASONING, LOGIC, FAST) == ("reasoning", "logic", "fast")


def test_the_reasoning_tier_is_the_word_the_questions_package_already_refuses_on():
    """`questions/proposal.py` spells this tier itself, so that the role-shortlist
    site can refuse a sending record naming any other one. Two spellings of one
    tier is a silent downgrade waiting to happen -- the site would refuse the word
    this module hands it -- so the two are checked equal rather than assumed."""
    assert REASONING == REASONING_TIER


def test_every_tier_has_an_environment_name_and_no_tier_has_two():
    """The refusal has to be able to say what to set. Named here rather than in
    `src/cli.py` so there is ONE spelling of each name in the repo: the reading and
    the refusal cannot drift if they are the same constant."""
    assert set(MODEL_NAME_OF_TIER) == set(TIERS)
    assert len(set(MODEL_NAME_OF_TIER.values())) == len(TIERS)
    assert all(name.startswith("DEEPSEEK_MODEL_")
               for name in MODEL_NAME_OF_TIER.values())


def test_the_tier_table_cannot_be_edited_after_import():
    with pytest.raises(TypeError):
        MODEL_NAME_OF_TIER[REASONING] = "somebody-elses-model"


# --- an unrouted call site refuses, and that IS the feature --------------------

def test_a_call_site_the_policy_does_not_list_refuses_and_names_itself():
    """`83` §3's last row: *"Anything not listed -- refuses. A new call site names
    its tier or does not run."* The failure this prevents is the one that cannot be
    seen: a site added next month picking up whichever tier happened to be handy,
    and answering for months with a model nobody chose for it."""
    routing = _routing()
    with pytest.raises(UnroutedCallSite) as raised:
        routing.client_for("F_something_new")
    message = str(raised.value)
    assert "F_something_new" in message
    for site in TABLE:
        assert site in message


def test_an_unrouted_site_refuses_from_every_door():
    routing = _routing()
    for lookup in (routing.tier_for, routing.client_for, routing.model_id_for):
        with pytest.raises(UnroutedCallSite):
            lookup("F_something_new")


def test_a_tier_with_no_client_refuses_rather_than_borrowing_another():
    """`83` §4: *"A tier that is unavailable, rate-limited or misnamed produces a
    refusal that names it. It does not quietly answer from another tier."*"""
    routing = TierRouting(tier_of_call_site=TABLE,
                          client_of_tier={REASONING: _routing().client_for(A_FACT)})
    assert routing.client_for(A_FACT) is not None
    with pytest.raises(TierUnavailable) as raised:
        routing.client_for(D_RESIDUAL)
    assert FAST in str(raised.value)
    assert MODEL_NAME_OF_TIER[FAST] in str(raised.value)


def test_both_refusals_are_catchable_as_one_thing():
    """A caller that wants "there is no model for this site" should not have to
    know which of the two reasons applied."""
    assert issubclass(UnroutedCallSite, ModelRouteRefused)
    assert issubclass(TierUnavailable, ModelRouteRefused)


def test_no_lookup_in_the_module_has_a_fallback():
    """By AST, because the failure this prevents is a convenience somebody adds
    later and nobody reviews: one `.get(site, something)` and the whole policy is
    decoration. A two-argument `.get` is what a silent downgrade looks like in
    code, so there are none."""
    tree = ast.parse(inspect.getsource(
        __import__("readers.model_routing", fromlist=["x"])))
    gets = [node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"]
    assert [node.lineno for node in gets if len(node.args) > 1] == []


# --- a malformed table stops before the scan, not during it -------------------

def test_a_tier_that_is_not_one_of_the_three_is_a_load_error():
    with pytest.raises(ValueError, match="cheap"):
        _routing(table={A_FACT: "reasoning-ish"})


def test_a_call_site_with_no_name_is_a_load_error():
    for empty in ("", "   "):
        with pytest.raises(ValueError):
            _routing(table={empty: REASONING})


def test_an_empty_table_routes_nothing_and_says_so():
    """Not an error to construct -- a deployment may wire no site at all -- but
    every lookup then refuses. What it must never be is a table that answers."""
    routing = TierRouting(tier_of_call_site={}, client_of_tier={})
    with pytest.raises(UnroutedCallSite):
        routing.client_for(A_FACT)


def test_a_client_that_is_not_a_model_client_is_a_load_error():
    with pytest.raises(ValueError):
        TierRouting(tier_of_call_site=TABLE,
                    client_of_tier={REASONING: lambda payload: b"{}"})


def test_a_tier_nobody_has_heard_of_cannot_be_given_a_client():
    with pytest.raises(ValueError):
        TierRouting(tier_of_call_site={},
                    client_of_tier={"cheapest": _routing().client_for(A_FACT)})


# --- what the DeepSeek assembly builds ----------------------------------------

def test_each_tier_gets_its_own_model_and_they_are_not_shared():
    routing = _routing()
    assert routing.model_id_for(A_FACT) == IDS[REASONING]
    assert routing.model_id_for(C_PLACEMENT) == IDS[LOGIC]
    assert routing.model_id_for(D_RESIDUAL) == IDS[FAST]
    assert routing.client_for(A_FACT) is not routing.client_for(D_RESIDUAL)


def test_the_two_logic_sites_share_one_client():
    """Same tier, same client. Three clients for three tiers, not one per site:
    `transport.issue` audits `model_target`, and two objects claiming one model
    would be two rows in §8.4's record describing one destination."""
    routing = _routing()
    assert routing.client_for(C_PLACEMENT) is routing.client_for(E_TEMPLATE)


def test_every_client_carries_the_target_the_transport_will_accept():
    """The `ModelTarget` is what `Gate.release` decides on and what §8.4 records.
    Built wrong here it would be refused by `deepseek_invoke` -- which is the
    intended failure -- but it would be refused DURING a scan, and the point of
    building the clients at the root is that a mislabelled one stops before it."""
    routing = _routing()
    for site in TABLE:
        target = routing.client_for(site).model_target
        assert isinstance(target, ModelTarget)
        assert target.provider == PROVIDER
        assert target.locality == CLOUD == LOCALITIES[1]


def test_a_tier_with_no_model_id_refuses_and_names_the_variable_to_set():
    """Absent means refuse, never guess -- and the refusal has to be actionable.
    A person told "the logic tier is not configured" has been told less than a
    person told to set `DEEPSEEK_MODEL_LOGIC`."""
    for absent in ({REASONING: "r", FAST: "f"},
                   {REASONING: "r", LOGIC: "", FAST: "f"},
                   {REASONING: "r", LOGIC: "  ", FAST: "f"}):
        with pytest.raises(ValueError) as raised:
            _routing(model_id_of_tier=absent)
        assert MODEL_NAME_OF_TIER[LOGIC] in str(raised.value)


def test_the_credential_and_endpoint_refusals_are_the_transports_own():
    """Not re-implemented here. `model_deepseek` raises at client construction,
    and building three clients means the refusal arrives once, at the root,
    before the scan -- which is the whole reason the clients are built early."""
    from readers.model_deepseek import ModelCredentialMissing, ModelEndpointMissing

    with pytest.raises(ModelCredentialMissing):
        _routing(api_key=None)
    with pytest.raises(ModelEndpointMissing):
        _routing(base_url=None)


def test_the_ceiling_reaches_every_tier():
    """One ceiling, injected, applied to all three. A tier built without it would
    be the one place §8.6's bound did not hold, and it would be the cheap tier --
    the high-volume one -- if the loop had been written per-site."""
    for bad in (0, -1, None):
        with pytest.raises(ValueError, match="max_response_tokens"):
            _routing(max_response_tokens=bad)


# --- the shape of the module itself -------------------------------------------

def test_the_router_holds_clients_and_can_never_read_a_corpus():
    """It is composition, not a part: it may name `ModelClient` and `ModelTarget`
    and nothing else from `src/`. A router that could reach `extractors` or
    `facts` would be a second place able to decide what goes into a call."""
    import readers.model_routing as module

    tree = ast.parse(inspect.getsource(module))
    runtime: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            runtime.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            runtime.add(node.module)
    src = {path.stem if path.is_file() else path.name
           for path in pathlib.Path("src").iterdir()}
    assert {name for name in runtime if name.split(".")[0] in src} == {
        "llm_harness.transport", "privacy.release", "readers.model_deepseek"}


def test_no_model_name_and_no_number_lives_in_this_module():
    """`84` §1: `src/cli.py` is the sole composition root and picks every number
    and every policy. A model name written here would be a deployment choice made
    in `src/`, and it would be the one place `83`'s "no silent downgrade" could be
    defeated without anybody editing `.env`."""
    tree = ast.parse(inspect.getsource(
        __import__("readers.model_routing", fromlist=["x"])))
    numbers = [node.value for node in ast.walk(tree)
               if isinstance(node, ast.Constant)
               and isinstance(node.value, (int, float))
               and not isinstance(node.value, bool)]
    assert set(numbers) <= {0, 1}, numbers
    assert "DeepSeek-" not in inspect.getsource(
        __import__("readers.model_routing", fromlist=["x"]))

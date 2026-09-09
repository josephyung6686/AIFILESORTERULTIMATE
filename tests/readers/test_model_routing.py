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
import json
import pathlib

import pytest

from llm_harness.transport import ModelClient
from llm_harness.vocabulary import A_FACT, B_GROUP, C_PLACEMENT, D_RESIDUAL, E_TEMPLATE
from privacy.release import LOCALITIES, MalformedRequest, ModelTarget
from questions.proposal import REASONING_TIER
from readers.model_deepseek import CLOUD, PROVIDER
from readers.model_ollama import LOCAL, MODEL_NAME as LOCAL_MODEL_NAME
from readers.model_ollama import DEFAULT_BASE_URL as LOCAL_DEFAULT_BASE_URL
from readers.model_ollama import ollama_invoke
from readers.model_ollama import PROVIDER as LOCAL_PROVIDER
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
    cloud_and_local_routing,
    deepseek_routing,
    ollama_routing,
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
                     max_response_tokens=ONE_TOKEN, timeout_seconds=30)
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
            _routing(max_response_tokens=bad, timeout_seconds=30)


# --- the shape of the module itself -------------------------------------------

def test_the_router_holds_clients_and_can_never_read_a_corpus():
    """It is composition, not a part: it may name `ModelClient`, `ModelTarget` and
    THE TRANSPORTS IT ASSEMBLES, and nothing else from `src/`. A router that could
    reach `extractors` or `facts` would be a second place able to decide what goes
    into a call.

    `readers.model_ollama` joined `readers.model_deepseek` here when D1's local
    half landed, and it is the same kind of name: a transport this router builds a
    client out of. The set is written out rather than pattern-matched so that a
    module of a DIFFERENT kind cannot arrive under a transport's cover."""
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
        "llm_harness.transport", "privacy.release",
        "readers.model_deepseek", "readers.model_ollama"}


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


# --- `00`:189-193's second mode: the model the person installed themselves -----
#
# D1's local half. `104` §7 Phase 0a: "Wire `readers.model_ollama` for A_fact under
# `local_model`". These tests are about WHICH client each site gets, never about
# what a model says -- no ollama runs here, for the reason
# `tests/readers/test_model_ollama.py` gives.

LOCAL_TABLE = {A_FACT: LOGIC, B_GROUP: LOGIC, C_PLACEMENT: LOGIC,
               E_TEMPLATE: LOGIC, D_RESIDUAL: FAST}


def _local(**overrides):
    settings = dict(model_id="qwen3:8b", base_url=None,
                    tier_of_call_site=LOCAL_TABLE, max_response_tokens=2048,
                    context_ceiling=32768, timeout_seconds=600.0)
    settings.update(overrides)
    return ollama_routing(**settings)


def test_a_local_model_alone_answers_every_site_and_says_it_is_local():
    """A deployment with one installed model has one destination for every
    question it can ask. `83` §4 forbids the substitution NOBODY SEES -- a cheap
    model quietly answering the expensive one's question -- and this is the
    opposite: the person chose the one model, and every site names it.

    The alternative, refusing REASONING and FAST, would make the pre-scan
    announcement raise on a deployment that is correctly configured."""
    routing = _local()

    for site in LOCAL_TABLE:
        target = routing.client_for(site).model_target
        assert target.locality == LOCAL
        assert target.provider == LOCAL_PROVIDER
        assert target.model_id == "qwen3:8b"


def test_one_client_object_serves_every_tier():
    """`transport.issue` audits `model_target`, and two clients claiming one model
    would be two descriptions of one destination in §8.4's record."""
    routing = _local()

    assert len({id(client) for client in routing.client_of_tier.values()}) == 1


def test_the_local_model_takes_only_its_own_sites_tier_beside_a_cloud_routing():
    """D1 in one assertion: **local model first**, for the site `104` §7 Phase 0a
    names, with every other tier still the cloud one the key paid for.

    Which site is policy and arrives as an argument -- `src/cli.py` picks it --
    because `83` §3's table is the only place a site-to-tier judgement lives and
    this must not become a second one."""
    cloud = _routing(table=LOCAL_TABLE)
    both = _local(beside=cloud, serves=A_FACT)

    assert both.client_for(A_FACT).model_target.locality == LOCAL
    assert both.model_id_for(A_FACT) == "qwen3:8b"
    # FAST is untouched: D_residual still goes to the model the key paid for.
    assert both.client_for(D_RESIDUAL).model_target.locality == CLOUD
    assert both.model_id_for(D_RESIDUAL) == "a-sprinter"


def test_the_sites_sharing_a_tier_with_a_fact_follow_it_and_that_is_said_out_loud():
    """B_group, C_placement and E_template are routed to A_fact's own tier by
    `83` §3, so a local model taking that tier takes them with it. That is
    TRUE rather than accidental -- if those sites were wired tomorrow, with this
    configuration they would go to the local model -- and the screen has to be
    able to say so, which is why it is asserted rather than left to be noticed."""
    both = _local(beside=_routing(table=LOCAL_TABLE), serves=A_FACT)

    for sharing in (B_GROUP, C_PLACEMENT, E_TEMPLATE):
        assert both.client_for(sharing).model_target.locality == LOCAL


def test_a_deployment_that_names_no_local_model_refuses_by_name():
    """Absent means refuse, never guess. There is no model this module would pick
    on a person's behalf."""
    for absent in (None, "", "   "):
        with pytest.raises(ValueError, match=LOCAL_MODEL_NAME):
            _local(model_id=absent)


def test_a_local_model_serving_an_unrouted_site_is_a_load_error():
    """`83` §3's last row refuses an unlisted site rather than inventing a tier
    for it, and a local model aimed at one would be aimed at nothing."""
    with pytest.raises(UnroutedCallSite, match="A_nowhere"):
        _local(beside=_routing(table=LOCAL_TABLE), serves="A_nowhere")


def test_a_local_model_beside_a_cloud_one_must_say_which_site_it_serves():
    """Otherwise it is a model this machine loaded, paid the memory for, and
    nothing can reach."""
    with pytest.raises(ValueError, match="serving nothing|no call site"):
        _local(beside=_routing(table=LOCAL_TABLE))


def test_the_local_locality_is_p7s_own_value_and_not_a_second_spelling():
    """`Gate.release` decides by `model_target.locality`. A second string that
    happened to look the same would be authorized by nothing."""
    assert LOCAL == LOCALITIES[0]


# --- the window, in the row that says what the model was given ----------------

def test_the_local_target_carries_the_window_the_audit_record_needs():
    """§8.4 audits what the model was given, and for a local model the window is
    part of that: the same dossier under two windows is not the same question,
    because a window that does not hold the prompt is answered from what fits.

    It rides on the TARGET rather than on a record of one call because it is a
    deployment fact and behaves like one -- ollama holds one context length per
    loaded model, so the number is fixed for the life of the run and every call
    in that run is given it. `binding._target_form` serialises the target into
    `release_ledger.model_target`, so putting it here is what puts it in the row
    beside the model id, the locality and the provider."""
    target = _local(context_ceiling=32768).client_for(A_FACT).model_target

    assert target.context_tokens == 32768
    assert target.to_mapping() == {
        "locality": LOCAL, "model_id": "qwen3:8b",
        "provider": LOCAL_PROVIDER, "context_tokens": 32768}


def test_the_number_in_the_row_is_the_number_the_request_carries():
    """THE ROW HAS TO BE TRUE, which is a different claim from the row existing.

    A window recorded beside the model id is read as a statement of fact about
    what the model was shown. If the target said one number and `num_ctx` sent
    another, the audit record would describe a call that never happened, and it
    would do so in the one place a person or a replay has to trust. So the two
    are asserted to be one number rather than two that happen to agree today."""
    captured: dict[str, object] = {}

    def post(url, body, *, timeout):
        captured["body"] = json.loads(body)
        return json.dumps({
            "model": "qwen3:8b", "message": {"role": "assistant", "content": "{}"},
            "done": True, "done_reason": "stop", "prompt_eval_count": 8,
        }).encode("utf-8")

    target = ModelTarget(locality=LOCAL, model_id="qwen3:8b",
                         provider=LOCAL_PROVIDER, context_tokens=4096)
    invoke = ollama_invoke(model_target=target, base_url=LOCAL_DEFAULT_BASE_URL,
                           max_response_tokens=256, context_ceiling=4096,
                           timeout_seconds=30.0, post=post)
    invoke(b"a dossier")

    assert captured["body"]["options"]["num_ctx"] == target.context_tokens
    assert invoke.context_tokens == target.context_tokens


def test_a_cloud_target_stores_the_three_keys_it_has_always_stored():
    """THE UNCHANGED HALF, pinned. A provider's window is the provider's and not
    this deployment's, so a cloud target names none -- and the stored form omits
    the key entirely rather than writing a null, which is what keeps every row
    this ledger already holds the same bytes it was written as."""
    target = _routing(table=LOCAL_TABLE).client_for(A_FACT).model_target

    assert target.context_tokens is None
    assert target.to_mapping() == {
        "locality": CLOUD, "model_id": "a-logician", "provider": PROVIDER}


def test_the_ledger_stores_the_targets_own_form_and_not_a_second_one():
    """One spelling of the stored form. `binding._target_form` used to serialise
    every dataclass field whether or not it held anything, so an optional field
    on `ModelTarget` would have added a null key to every cloud row in the ledger
    without a line of `binding.py` changing. The target says how it is stored and
    both readers ask it."""
    from privacy.binding import _target_form

    local = _local().client_for(A_FACT).model_target
    cloud = _routing(table=LOCAL_TABLE).client_for(A_FACT).model_target

    assert json.loads(_target_form(local)) == local.to_mapping()
    assert json.loads(_target_form(cloud)) == cloud.to_mapping()
    assert "context_tokens" not in json.loads(_target_form(cloud))


@pytest.mark.parametrize("window", [0, -1, True, 2.5, "32768"])
def test_a_window_that_could_not_have_been_sent_is_refused(window):
    """A number that could not have been a `num_ctx` makes the audit record false
    where it is written, and the record is the product's own evidence about what
    happened to someone's file. `84` §1: absent means refuse, never guess --
    `None` is how a target says it has no window of ours to state, and anything
    else is a load error rather than a value to be stored and believed."""
    with pytest.raises(MalformedRequest, match="context_tokens"):
        ModelTarget(locality=LOCAL, model_id="qwen3:8b",
                    provider=LOCAL_PROVIDER, context_tokens=window)


# --- `104` §17.13 ruling 3: both models at once, chosen per FILE ---------------
#
# The per-SITE split above (`serves=`) gives one call site to the local model and
# leaves the rest on the cloud key. The ruling is finer than that: ONE site is two
# destinations, and which one a given file gets is a question about that file's
# classification. These tests are about the SHAPE that can carry it -- which
# client comes back for `cloud_permitted=True` and for `False` -- and never about
# which files those are, which is `cli.target_for`'s and is tested there.

def _both(**overrides):
    settings = dict(beside=_routing(table=LOCAL_TABLE), model_id="qwen3:8b",
                    base_url=None, max_response_tokens=2048,
                    context_ceiling=32768, timeout_seconds=600.0)
    settings.update(overrides)
    return cloud_and_local_routing(**settings)


def test_both_clients_are_held_at_once_and_the_site_is_not_given_away():
    """The difference from `serves=`: A_fact keeps its cloud client AND gains a
    local one, rather than trading the first for the second."""
    both = _both()

    cloud_client, cloud_target = both.route_for(A_FACT, cloud_permitted=True)
    local_client, local_target = both.route_for(A_FACT, cloud_permitted=False)

    assert cloud_target.locality == CLOUD
    assert cloud_target.model_id == IDS[LOGIC]
    assert local_target.locality == LOCAL
    assert local_target.model_id == "qwen3:8b"
    assert cloud_client is not local_client


def test_the_target_returned_is_the_clients_own_and_never_a_second_one():
    """`FactCallAuthorities.__post_init__`'s rule, kept true at the source: two
    values would authorise one destination and deliver to a different one."""
    both = _both()

    for permitted in (True, False):
        client, target = both.route_for(A_FACT, cloud_permitted=permitted)
        assert client.model_target is target


def test_every_tier_gains_the_local_half_and_the_cloud_half_keeps_its_own_model():
    """One local client for all three tiers -- there is one installed model -- and
    the cloud side still resolves each tier to the model its own name paid for."""
    both = _both()

    assert len({id(client)
                for client in both.local_client_of_tier.values()}) == 1
    assert both.route_for(
        D_RESIDUAL, cloud_permitted=True)[1].model_id == IDS[FAST]
    assert both.route_for(
        D_RESIDUAL, cloud_permitted=False)[1].model_id == "qwen3:8b"


def test_the_ordinary_reads_still_describe_the_cloud_half():
    """`client_for`, `model_id_for` and `locality_for` are what the screen and the
    observe gates ask, and on a two-target deployment they answer about the
    destination that is not this machine. A caller that needs the other half says
    so, which is the whole point of `route_for` taking an argument."""
    both = _both()

    assert both.locality_for(A_FACT) == CLOUD
    assert both.model_id_for(A_FACT) == IDS[LOGIC]
    assert both.client_for(A_FACT) is both.route_for(
        A_FACT, cloud_permitted=True)[0]


def test_one_cloud_model_alone_answers_both_ways_and_says_it_is_cloud():
    """A deployment with a key and no local model is unchanged, and this is the
    assertion that stops `cloud_permitted=False` from being read as "went local":
    the LOCALITY of the returned target is the answer, and here it is CLOUD both
    times. `cli.target_for` is what refuses to send on that answer."""
    cloud = _routing(table=LOCAL_TABLE)

    for permitted in (True, False):
        client, target = cloud.route_for(A_FACT, cloud_permitted=permitted)
        assert target.locality == CLOUD
        assert client is cloud.client_for(A_FACT)


def test_one_local_model_alone_answers_both_ways_and_says_it_is_local():
    """The mirror, and the one that keeps D1's deployment behaving exactly as it
    did: one installed model is the destination for every question, and asking for
    a cloud-permitted route does not conjure a cloud client."""
    local = _local()

    for permitted in (True, False):
        client, target = local.route_for(A_FACT, cloud_permitted=permitted)
        assert target.locality == LOCAL
        assert client is local.client_for(A_FACT)


def test_an_unrouted_site_refuses_from_the_per_file_door_too():
    """`83` §3's last row is not weakened by a second entry point: a site nobody
    routed gets the refusal that names it, whichever way it is asked."""
    both = _both()

    for permitted in (True, False):
        with pytest.raises(UnroutedCallSite, match="A_nowhere"):
            both.route_for("A_nowhere", cloud_permitted=permitted)


def test_a_tier_with_no_client_on_either_half_refuses_rather_than_borrowing():
    """The local half is not a fallback for a cloud tier the deployment never
    configured: with the local mapping empty, a missing tier refuses by name."""
    routing = TierRouting(tier_of_call_site={A_FACT: LOGIC, D_RESIDUAL: FAST},
                          client_of_tier={LOGIC: _routing().client_of_tier[LOGIC]})

    with pytest.raises(TierUnavailable, match=MODEL_NAME_OF_TIER[FAST]):
        routing.route_for(D_RESIDUAL, cloud_permitted=True)


def test_the_two_halves_share_one_tier_table_and_cannot_be_two_policies():
    """A second table would let one site be one tier on the cloud and another on
    this machine, which is the same site being two policies. `83` §3 has one
    answer per site and the composition keeps it one."""
    cloud = _routing(table=LOCAL_TABLE)
    both = _both(beside=cloud)

    assert both.tier_of_call_site == cloud.tier_of_call_site

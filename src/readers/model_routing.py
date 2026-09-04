# src/readers/model_routing.py
"""`83`'s three tiers, carried from the composition root to the call sites.

**What this module is.** A shape and a refusal. `83` decides that one model per
KIND OF JUDGEMENT is worth the trouble -- heavy reasoning where being wrong is
expensive and hard to notice, cheap step-by-step logic where the answer is
checkable, fast and cheap where an individual mistake costs a person nothing they
cannot undo in one gesture. Which model each tier resolves to is a deployment fact
that lives in `.env`; which tier each call site requires is a policy that lives in
`src/cli.py`. Neither is here. What is here is the object that carries both, and
the guarantee that a call site nobody routed gets a refusal instead of whichever
model happened to be nearby.

**Why the refusal is the whole point.** `83` §4: *"A tier that is unavailable,
rate-limited or misnamed produces a refusal that names it. It does not quietly
answer from another tier."* And §1's caveat, which is the sentence this module
exists to make mechanical: *"a cheap model answering a question the expensive one
was chosen for is a wrong answer that looks exactly like a right one, and the whole
point of tiering is defeated the first time it happens silently."* A default here
would not be a convenience; it would be the failure, spelled as a feature. So there
is no two-argument `.get` in this file and
`tests/readers/test_model_routing.py::test_no_lookup_in_the_module_has_a_fallback`
checks the parsed source rather than trusting this paragraph.

**Where it lives, and why not in `src/llm_harness/`.** P8 owns `run_call`, which
takes ONE `model_client` -- so choosing WHICH client is the caller's, one layer up,
and `tests/p8/test_p8_architecture.py` forbids every P8 module from importing
`readers` at all. `src/readers/` is the deployment layer (`deployment.py` assembles
one `Readers` for one machine for the same reason), and a tier-to-transport map is
the same kind of fact: it is about what this deployment installed, not about what
the product decides.

**Three clients, not one per site.** Two sites on one tier share one `ModelClient`,
because `transport.issue` audits `model_target` and two objects claiming one model
would be two descriptions of one destination in §8.4's record.

**The environment names are spelled here and read in `src/cli.py`.** One spelling
in the repo, so the reading and the refusal cannot drift: a person whose logic tier
is unset is told to set `DEEPSEEK_MODEL_LOGIC`, in the same words the root looked
for. The module never reads the environment itself -- the same rule
`model_deepseek.CREDENTIAL_NAME` follows, for the same reason: a module that
reaches for its own configuration can acquire configuration nobody chose to give it.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from llm_harness.transport import ModelClient
from privacy.release import ModelTarget

from readers.model_deepseek import CLOUD, PROVIDER, deepseek_invoke

#: `83` §2's three, in the policy's own words. `reasoning` is also spelled by
#: `questions/proposal.py`, which refuses a sending record naming any other tier;
#: the test asserts the two are one string rather than two that happen to match.
REASONING: str = "reasoning"
LOGIC: str = "logic"
FAST: str = "fast"

TIERS: tuple[str, str, str] = (REASONING, LOGIC, FAST)

#: Where a deployment names the model each tier resolves to. `83` §4: *"`DEEPSEEK_MODEL`
#: as a single catch-all name is deliberately NOT read any more; three names replace
#: it so that no call site can inherit a tier it never chose."*
MODEL_NAME_OF_TIER: Mapping[str, str] = MappingProxyType({
    REASONING: "DEEPSEEK_MODEL_REASONING",
    LOGIC: "DEEPSEEK_MODEL_LOGIC",
    FAST: "DEEPSEEK_MODEL_FAST",
})


class ModelRouteRefused(RuntimeError):
    """There is no model for this call site, and none was substituted."""


class UnroutedCallSite(ModelRouteRefused):
    """The policy does not say which tier answers here, so nothing does."""


class TierUnavailable(ModelRouteRefused):
    """The tier this site requires has no client in this deployment."""


def _checked_table(tier_of_call_site: Mapping[str, str]) -> Mapping[str, str]:
    for call_site, tier in tier_of_call_site.items():
        if not isinstance(call_site, str) or not call_site.strip():
            raise ValueError(
                f"a routing row is keyed by {call_site!r}, which names no call "
                f"site. A row nothing can look up is a tier assignment that was "
                f"written and never applied.")
        if tier not in TIERS:
            raise ValueError(
                f"call site {call_site!r} is routed to {tier!r}, which is not one "
                f"of {TIERS}. A tier outside the closed set is a load error and "
                f"not a fallback: `83` §1 is that a cheap model answering the "
                f"question the expensive one was chosen for is a wrong answer that "
                f"looks exactly like a right one, and this stops before the scan "
                f"rather than during it.")
    return MappingProxyType(dict(tier_of_call_site))


def _checked_clients(
        client_of_tier: Mapping[str, ModelClient]) -> Mapping[str, ModelClient]:
    for tier, client in client_of_tier.items():
        if tier not in TIERS:
            raise ValueError(
                f"a client was supplied for {tier!r}, which is not one of {TIERS}. "
                f"No call site can ask for it, so it is a model this deployment "
                f"pays for and never reaches.")
        if not isinstance(client, ModelClient):
            raise ValueError(
                f"the {tier!r} client is {type(client).__name__}, not a "
                f"ModelClient. `run_call` requires the target-bound capability: a "
                f"bare callable carries no `model_target`, and §8.4's record of "
                f"which model received the data would have nothing to write.")
    return MappingProxyType(dict(client_of_tier))


@dataclass(frozen=True, slots=True)
class TierRouting:
    """Which tier answers at which call site, and which client each tier is.

    Both mappings are injected. This object holds no policy of its own and has no
    default for either question -- it is the thing that makes "absent means refuse"
    true at the moment a call site asks for a model.
    """

    tier_of_call_site: Mapping[str, str]
    client_of_tier: Mapping[str, ModelClient]

    def __post_init__(self) -> None:
        object.__setattr__(self, "tier_of_call_site",
                           _checked_table(self.tier_of_call_site))
        object.__setattr__(self, "client_of_tier",
                           _checked_clients(self.client_of_tier))

    def tier_for(self, call_site: str) -> str:
        """Which tier `83` §3 routes this site to, or a refusal naming the site."""
        if call_site not in self.tier_of_call_site:
            raise UnroutedCallSite(
                f"call site {call_site!r} is not routed to a tier. `83` §3's last "
                f"row is that anything unlisted refuses: a new call site names its "
                f"tier or does not run, because a site that inherited one would be "
                f"answered for months by a model nobody chose for it. The routed "
                f"sites are {sorted(self.tier_of_call_site)}.")
        return self.tier_of_call_site[call_site]

    def client_for(self, call_site: str) -> ModelClient:
        """The one client this site may use. Never another tier's."""
        tier = self.tier_for(call_site)
        if tier not in self.client_of_tier:
            raise TierUnavailable(
                f"call site {call_site!r} requires the {tier!r} tier and this "
                f"deployment has no client for it. `83` §4 forbids answering from "
                f"another tier rather than discouraging it. Set "
                f"{MODEL_NAME_OF_TIER[tier]} and re-run.")
        return self.client_of_tier[tier]

    def model_id_for(self, call_site: str) -> str:
        """WHICH model, so a person can be told the name of who receives what.

        `questions/proposal.SelfDescriptionSending` needs exactly this and does not
        take a client: *"A person told that their sentence is going to 'an external
        provider' has been told less than a person told it is going to a named
        one."*
        """
        return self.client_for(call_site).model_target.model_id


def deepseek_routing(*, api_key: str | None, base_url: str | None,
                     model_id_of_tier: Mapping[str, str],
                     tier_of_call_site: Mapping[str, str],
                     max_response_tokens: int,
                     timeout_seconds: float) -> TierRouting:
    """Three cloud clients, one per tier, from three injected model names.

    Every refusal this can produce fires HERE, at the root, before the scan: no
    key, no endpoint, an unnamed tier, a tier routed to a word that is not a tier.
    That is the reason the clients are built early rather than at the first call --
    a deployment that is going to refuse should refuse before it has read a
    person's folder, not in the middle of doing so.

    `timeout_seconds` is threaded through for the same reason as every other
    number here: `deepseek_invoke` refuses to invent one, because a client with
    no timeout can hold a scan open for ever. It is `cli.py` that picks it.
    """
    table = _checked_table(tier_of_call_site)
    clients: dict[str, ModelClient] = {}
    for tier in TIERS:
        model_id = model_id_of_tier.get(tier)
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError(
                f"the {tier!r} tier names no model. Set "
                f"{MODEL_NAME_OF_TIER[tier]} in the environment this run starts "
                f"from. Absent means refuse, never guess: `83` §4 is that no tier "
                f"is a default, and a tier resolved from another tier's name is "
                f"the silent downgrade the policy exists to forbid.")
        target = ModelTarget(locality=CLOUD, model_id=model_id, provider=PROVIDER)
        clients[tier] = ModelClient(
            model_target=target,
            invoke=deepseek_invoke(
                api_key=api_key, base_url=base_url, model_target=target,
                max_response_tokens=max_response_tokens,
                timeout_seconds=timeout_seconds),
        )
    return TierRouting(tier_of_call_site=table, client_of_tier=clients)

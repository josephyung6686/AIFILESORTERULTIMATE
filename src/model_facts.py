# src/model_facts.py
"""P6's §8.6 `llm` producer: one A_fact call for one file version.

**Why this file exists at all.** `facts.resolver` takes three producers and the
third is a `Stage` -- `(conn, file_id, content_hash) -> tuple[fact_id, ...]`. Every
deployment so far has passed `None` for it, and `FactResolver`'s docstring names
that as "the ordinary case for `llm`, because P8 does not exist". P8 exists now, and
nothing in `src/` turned a file into a `DossierRequest` at site A: `p8_seam.py` does
it for P9's groups and there is no counterpart for P6's files. That gap is the whole
of why the product filled 2 of its 56 declared fields on a real folder.

**Why it is not in `facts/` and not in `llm_harness/`.** `llm_harness.fact_validation`
imports `facts.llm_seam`, so a builder inside `facts/` that reached for
`llm_harness.records` would invert the layer P8 already depends on --
`tests/p8/test_p8_architecture.py` reads those directions. And P8 does not build
dossier requests for its callers: `run_call` takes one. So this is the deployment
layer, a sibling of `production.py`, which is where the same argument put the P1-P7
composition.

**Nothing here is a number and nothing here is a policy.** Every threshold, cap,
budget, clock, model, prompt, normaliser and oracle arrives in `FactCallAuthorities`
with no default, and `src/cli.py` is the only file that fills one in. What this
module owns is the SHAPE of the request and the order the checks run in.

**The three refusals that happen before a call is built**, each because the
alternative is worse than not asking:

  * nothing pending -- every field the schema allows is already settled, so the
    question has no content and the spend buys a repetition of what is known;
  * nothing releasable -- every observation is in an always-local zone, is
    unbounded, or was signalled sensitive, so the dossier would be empty and the
    model would be asked to answer from nothing;
  * no allowlist -- no domain activated and no universal field remains, so §3.5's
    closed vocabulary is empty and every answer would be out of schema.

Each returns `()` and leaves no `unresolved` row: they are not refusals ABOUT the
file, they are the absence of a question. The refusals that ARE about the file --
the privacy bar and the budget bar -- belong to `FactResolver`, which writes them,
and to `Gate`, which records its own.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from evidence_shape.locator import serialize_locator
from evidence_shape.store import unit_length_for_observation
from facts.domains import ActivationSignals, active_field_allowlist
from facts.file_facts import facts_for_file
from facts.evidence import observations_for_version
from facts.llm_seam import FactRequest, build_request
from facts.states import EXCLUDED_STATE
from llm_harness.budgets import ScanBudget
from llm_harness.fact_validation import FactValidationDependencies
from llm_harness.fingerprint import prompt_fingerprint
from llm_harness.harness import CallDependencies, run_call
from llm_harness.records import DossierRequest, EvidenceItem, PromptDefinition
from llm_harness.sites import FactSiteDependencies, SiteDependencies
from llm_harness.transport import ModelClient
from llm_harness.vocabulary import A_FACT, DIRECT_ANCHOR, REMAINS_AMBIGUOUS
from privacy.gate import Gate
from privacy.items import Excerpt, sensitive_observation_keys
from privacy.release import ModelCallRequest, ModelTarget, Target
from privacy.vocabulary import ALWAYS_LOCAL_ZONES

#: P8's own stage name for a fact call, and the `ModelCallRequest.stage` §8.4's audit
#: record carries. P9 spells its own as `group_interpretation` in `p8_seam.py`.
FACT_STAGE: str = "fact_interpretation"

#: §8.7's scope this call's learning suppression is read at, and the class of
#: proposal it is. One call covers every pending field of one file, so the basis is
#: the file VERSION and not a field=value pair.
#:
#: KNOWN LIMITATION, written here rather than solved: a person who rejects one
#: field's value records a narrower basis than this, so `assess_call`'s
#: `USER_REJECTED_EQUIVALENT` will not fire for an A_fact call the way it does for a
#: group. Making it fire means a per-field call or a per-field basis, and both are
#: decisions about what a call IS -- the owner's, not this module's.
LEARNING_SCOPE: str = "file"
PROPOSAL_CLASS: str = "fact.llm_extraction"

#: The zones §2.2 ranks as meaningful evidence, most placed first. A dossier is
#: capped, so WHICH observations survive the cap is a real choice: a title or a
#: page-one heading carries more meaning than a late body reference, which is §3.7's
#: own sentence. Zones outside this list keep their stored order behind it.
_ZONE_PREFERENCE: tuple[str, ...] = (
    "title", "heading", "metadata", "body", "table", "notes",
)


@dataclass(frozen=True)
class FactCallAuthorities:
    """Everything one A_fact call needs and this module authors none of.

    `evidence_resolver` answers "does this observation key still resolve in the
    store" for §3.6 check 2's coarse half; `normalize` and `contradicts` are the
    C-5 pair neither P6 nor P8 owns, which `cli.normalize_for_model` and
    `cli.contradicts_stronger` answer for this deployment.

    `on_result` is a reporting sink, not an authority: it is handed the file id and
    the object `run_call` returned, so the composition root can count refusals,
    abstentions and failed calls for the screen. `None` means nobody is counting.
    """

    gate: Gate
    model_client: ModelClient
    prompt: PromptDefinition
    model_target: ModelTarget
    activation_signals: ActivationSignals
    normalizers: Mapping[str, Callable[[str], Any]]
    normalize: Callable[[str, str], object]
    contradicts: Callable[..., bool]
    evidence_resolver: Callable[[str], object]
    scan_budget: ScanBudget
    estimated_cost: Decimal
    actual_cost: Decimal
    policy_version: str
    wire_handle_key: bytes
    max_released_observations: int
    max_dossier_tokens: int
    observed_at: Callable[[], str]
    on_result: Callable[[str, object], None] | None

    def __post_init__(self) -> None:
        if self.max_released_observations < 1:
            raise ValueError(
                "a dossier with no released evidence is a model asked to answer "
                "from nothing; the cap is a bound on what is sent, not a switch")
        if self.model_client.model_target != self.model_target:
            # The gate decides about one destination and the transport sends to
            # another. `test_live_path` names the same rule at site B.
            raise ValueError(
                "the gate is asked about `model_target` and the client sends to "
                "`model_client.model_target`; two values here would authorise one "
                "destination and deliver to a different one")


def pending_fields_for(conn: sqlite3.Connection, *, file_id: str,
                       content_hash: str,
                       activation_signals: ActivationSignals) -> tuple[str, ...]:
    """Fields the active schema allows that this file version does not yet carry.

    The allowlist is `active_field_allowlist`, which is §3.5's ONE computation and
    is also what the dossier's `allowed_vocabulary` is built from -- a model
    measured against one list and validated against another can be rejected for
    obeying its instructions.

    A field with a `rejected` fact is still pending: §3.13 makes `rejected` an
    exclusion rather than a value, so the field is open and nothing holds it.
    """
    allowed = active_field_allowlist(
        conn, file_id=file_id, content_hash=content_hash,
        activation_signals=activation_signals)
    settled = {row["field_key"] for row in facts_for_file(conn, file_id, content_hash)
               if row["active"] and row["reliability_state"] != EXCLUDED_STATE}
    return tuple(field for field in allowed if field not in settled)


def releasable_observations(conn: sqlite3.Connection, *, file_id: str,
                            content_hash: str, limit: int) -> tuple:
    """The observations this file may offer a model, most placed first, capped.

    Four exclusions, and each is one of the gate's own refusals applied a step early
    so the call is never BUILT rather than built and denied. Every one of them
    refuses the WHOLE request, not the item -- one bad observation among eight costs
    the file its call -- which is why they are read here and not left to the door:

      * `ALWAYS_LOCAL_ZONES` -- `path` and `filename`, the two zones §8.4's members
        1 and 6 have a route out through. The filesystem extractor writes one
        observation per file whose raw value is the parent directory.
        `Denied(always_local_item)`.
      * `sensitive_observation_keys` -- P5's per-value signal.
        `ProtectedItemRequested`.
      * a span that covers the whole of its text unit, and a span-less observation
        whose value is at least as long as the unit standing at its own path. That
        is `items.is_whole_document` read against P4's own length-only lookup,
        and §8.4's sentence behind it: the engine "should not send full documents
        where a short heading or OCR excerpt is enough to resolve the question."
        `Denied(whole_document_requested)`, and it fires AFTER the text has been
        resolved, so leaving it to the gate means paying to materialise a document
        in order to refuse it.
      * a span-less observation with no unit at its path is offered, because that is
        §2.3's cell and §2.8's EXIF field -- the shape where the address IS the
        whole citation and there is no document for it to be the whole of.

    The span is the observation's OWN, never a synthesised `(0, len(value))`:
    `p8_seam` records what that cost at site B -- every unbounded observation
    refused with `UnresolvableSpan` after the release had been minted.
    """
    sensitive = sensitive_observation_keys(conn, file_id)
    offered = []
    for observation in observations_for_version(conn, file_id, content_hash):
        where = observation.location
        if where.zone in ALWAYS_LOCAL_ZONES:
            continue
        if observation.observation_key in sensitive:
            continue
        if not observation.raw_value:
            continue
        unit_length = unit_length_for_observation(conn, observation)
        if where.text_span is None:
            # The two span-less shapes, told apart exactly as `resolve.materialise`
            # tells them apart: by the unit at the observation's own path.
            if (unit_length is not None
                    and len(observation.raw_value) >= unit_length):
                continue
        else:
            if unit_length is None:
                # `materialise` raises `UnresolvableSpan` here rather than denying:
                # a span with nothing to take a substring of is a contract failure,
                # and this call is not the place to discover it.
                continue
            if (where.text_span.start <= 0
                    and where.text_span.end >= unit_length):
                continue
        offered.append(observation)

    def placed(observation) -> tuple[int, str]:
        zone = observation.location.zone
        rank = (_ZONE_PREFERENCE.index(zone) if zone in _ZONE_PREFERENCE
                else len(_ZONE_PREFERENCE))
        return (rank, observation.observation_key)

    return tuple(sorted(offered, key=placed)[:limit])


def _evidence_items(observations: Sequence) -> tuple[EvidenceItem, ...]:
    """The builder's reference metadata, one per offered observation.

    `build_dossier` requires every released key to have one of these: without it P8
    would have to invent `kind`, `location`, `reliability_state` and `basis`, which
    §1 forbids. `basis` is `direct_anchor` because these are P4's own readings of
    the file, not a neighbour's inference about it.
    """
    return tuple(
        EvidenceItem(
            evidence_ref=observation.observation_key,
            kind="excerpt",
            location=serialize_locator(observation.location),
            excerpt_span=(None if observation.location.text_span is None else
                          (observation.location.text_span.start,
                           observation.location.text_span.end)),
            reliability_state=observation.reliability,
            basis=DIRECT_ANCHOR,
        )
        for observation in observations
    )


def build_fact_request(
    request: FactRequest,
    observations: Sequence, *,
    model_target: ModelTarget,
    prompt: PromptDefinition,
    max_dossier_tokens: int,
) -> DossierRequest:
    """A reference-shape conversion and nothing else. No text crosses this line.

    `prompt_fingerprint` is the PROMPT's. `transport.issue` recomputes it from the
    `PromptDefinition` it is about to send and refuses the release when the two
    disagree, so a request bound to anything else -- the dossier's own address, say
    -- raises `BindingMismatch` after P7 has already spent the release. That is the
    defect that kept P9's first real group call from ever reaching a model, and it
    is written down here so site A does not rediscover it.
    """
    return DossierRequest(
        call_site=A_FACT,
        # The FILE, because `validate_fact_proposal` refuses a dossier whose
        # `subject_ref` is not the `FactRequest`'s `file_id`: a dossier describing
        # one file must not write a fact onto another.
        subject_ref=request.file_id,
        # §3.5's own words for why a model is asked at all: the deterministic
        # producers ran first and left these fields open. `remains_ambiguous` is the
        # first of FACT_ELIGIBILITY's three and is the one that is true of every
        # file that reaches here.
        eligibility_reason=REMAINS_AMBIGUOUS,
        evidence_items=_evidence_items(observations),
        # P6 holds no conflict record of its own; §3.7's competing-value case is
        # settled by the ranking before a model is asked, so a file that reaches
        # here has none to declare.
        conflicts=(),
        model_call_request=ModelCallRequest(
            stage=FACT_STAGE,
            target=Target(file_ids=(request.file_id,), group_id=None),
            model_target=model_target,
            requested_items=tuple(
                Excerpt(
                    observation_key=observation.observation_key,
                    span=observation.location.text_span,
                    reason="a reading of this file the fields may rest on",
                )
                for observation in observations
            ),
            prompt_template_id=prompt.template_id,
            prompt_fingerprint=prompt_fingerprint(prompt),
            max_dossier_tokens=max_dossier_tokens,
        ),
        # Null at A and B (`records._require_plan_version`): a fact is about a file
        # version and not about a plan, and the same fact survives a re-plan.
        plan_version=None,
        evidence_snapshot_id=None,
    )


def _call_dependencies(
    request: FactRequest,
    allowed_vocabulary: Sequence[str], *,
    authorities: FactCallAuthorities,
) -> CallDependencies:
    return CallDependencies(
        proposal_class=PROPOSAL_CLASS,
        basis_key=request.content_hash,
        learning_scope=LEARNING_SCOPE,
        learning_subject_id=request.file_id,
        evidence_resolver=authorities.evidence_resolver,
        site_dependencies=SiteDependencies(
            fact=FactSiteDependencies(
                fact_request=request,
                fact_dependencies=FactValidationDependencies(
                    normalize=authorities.normalize,
                    contradicts=authorities.contradicts)),
            placement=None, residual=None, template=None),
        contradicts=authorities.contradicts,
        # The dossier is built at the cap already; there is no second, smaller shape
        # of it to fall back to, so the ladder's first rung is the only one this
        # deployment can stand on and the rest are honestly absent. M9's summarize ->
        # preserve anchors -> split is `run_call`'s and needs a caller that can
        # produce those shapes; nothing here pretends to.
        unreduced_fits=True, summarized_fits=False, anchors_fit=False,
        split_shard_fits=(), split_shards=(),
        scan_budget=authorities.scan_budget,
        estimated_cost=authorities.estimated_cost,
        actual_cost=authorities.actual_cost,
        allowed_vocabulary=tuple(allowed_vocabulary),
        policy_version=authorities.policy_version,
        wire_handle_key=authorities.wire_handle_key,
    )


def fact_call_stage(authorities: FactCallAuthorities):
    """One `facts.resolver.Stage`: the §8.6 `llm` producer, wired to a real model.

    Returns the ids of the facts THIS call wrote, read back by diffing the version's
    fact rows -- `validate_fact_proposal` calls `apply_verdict` and discards the id
    it returns, and a stage that answered `()` would tell `ResolveResult` the model
    contributed nothing while its facts sat on disk.

    It never swallows an exception, for the reason `FactResolver.resolve` gives:
    P6's failures are `ContractViolation`s and a caller that catches one still owes
    P2 an envelope. Every outcome `run_call` can RETURN -- a refusal, an abstention,
    a call failure, an unavailable validation -- is already a record on disk by the
    time it comes back, and is handed to `on_result` for counting.
    """

    def stage(conn: sqlite3.Connection, file_id: str,
              content_hash: str) -> tuple[str, ...]:
        pending = pending_fields_for(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals)
        if not pending:
            return ()
        observations = releasable_observations(
            conn, file_id=file_id, content_hash=content_hash,
            limit=authorities.max_released_observations)
        if not observations:
            return ()
        request = build_request(
            conn, file_id=file_id, content_hash=content_hash,
            activation_signals=authorities.activation_signals,
            normalizers=authorities.normalizers)
        if not request.allowlist:
            return ()

        before = {row["fact_id"] for row in facts_for_file(
            conn, file_id, content_hash)}
        result = run_call(
            conn,
            build_fact_request(
                request, observations,
                model_target=authorities.model_target,
                prompt=authorities.prompt,
                max_dossier_tokens=authorities.max_dossier_tokens),
            gate=authorities.gate,
            model_client=authorities.model_client,
            prompt=authorities.prompt,
            validation_dependencies=_call_dependencies(
                request, request.allowlist, authorities=authorities),
            observed_at=authorities.observed_at,
        )
        if authorities.on_result is not None:
            authorities.on_result(file_id, result)
        return tuple(row["fact_id"] for row in facts_for_file(
            conn, file_id, content_hash) if row["fact_id"] not in before)

    return stage

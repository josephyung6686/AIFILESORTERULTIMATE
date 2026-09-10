"""P11's side of Sites C and D. Authorities in, verdict out, no second validator.

Resolution O7 settles the split: P8 owns the validator mechanism and the verdict
shape; P11 owns the destination-specific checks and the record they populate.
"Destination-specific checks" means the ORACLES -- does this node exist in this
frozen plan version, what is the support threshold, what counts as a margin, is
this release permitted -- not the validation. Every one of Site C's checks stays in
`llm_harness/placement_validation.py`, and a P11 module spelling one of its reason
codes is a second opinion with no way to be reconciled. A test walks this package's
AST and fails on any of P8's eleven Site C codes appearing as a literal here.

`node_exists` closes over P11's own index, so the question P8 asks and the
question P11 answers when it validates a destination itself are literally the same
function. Two sources could disagree, and the disagreement would surface as a
model error.

P11 constructs no `Dossier`, calls no `Gate.release` and imports no model client.
It does hold and pass a `Gate`, a `ModelClient` and a `PromptDefinition`, because
`run_call` requires all three -- holding a capability and exercising it are
different things, and P7 owns the exercise.
"""
from __future__ import annotations

import hashlib
import sqlite3

#: `104` §18.15: P8's two drivers, RE-EXPORTED HERE ON PURPOSE. P11 reaches
#: P8's mechanism through this module and no other -- `tests/p11/
#: test_p11_connections.py` walks the package and fails on a second importer --
#: and the lane is P8's mechanism: what it holds open is `run_call_steps`'
#: round trip. `pipeline` takes them from here, which is the same boundary the
#: verdict and the validator already cross.
from llm_harness.harness import (
    CallLane, drive_inline, in_walk_order, run_call_steps,
)
from llm_harness.placement_validation import (
    PlacementDependencies, ResidualDependencies,
)
from llm_harness.records import Conflict as P8Conflict
from llm_harness.sites import SiteDependencies
from llm_harness.vocabulary import (
    ABSTAIN, ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, BELOW_SUPPORT_THRESHOLD,
    BUDGET_EXHAUSTED, GENERIC_HUB_ONLY as P8_GENERIC_HUB_ONLY,
    INSUFFICIENT_MARGIN, REJECT, WEAK,
)

from placement.config import SupportPolicy, require_policy
from placement.index import node_exists as index_node_exists
from placement.vocabulary import (
    ABSTAIN as P11_ABSTAIN, BUDGET_DEFERRED, GENERIC_HUB_ONLY, LOW_MARGIN,
    NO_SUPPORTED_DESTINATION, PLACE, PLACEMENT_SCORING,
)

#: How a P8 Site C reason becomes one of §6.10's own abstention reasons. Both are
#: closed sets. `BUDGET_EXHAUSTED` is deliberately NOT a member: §8.6 makes it a
#: deferral rather than a judgement, it is decided by its own branch below, and a
#: duplicate entry here would produce the same reason with no `deferred_stage` --
#: a decision `PlacementDecision` refuses to construct.
_REASON_TO_ABSTENTION: dict[str, str] = {
    BELOW_SUPPORT_THRESHOLD: NO_SUPPORTED_DESTINATION,
    INSUFFICIENT_MARGIN: LOW_MARGIN,
    P8_GENERIC_HUB_ONLY: GENERIC_HUB_ONLY,
}
assert BUDGET_EXHAUSTED not in _REASON_TO_ABSTENTION

#: The separator inside a content address. Chosen because no node id, plan version
#: or P4 observation key can contain it, so two different inputs cannot be joined
#: into one identical string.
_JOIN: str = "‖"


class ModelPathUnavailable(RuntimeError):
    """The model path was asked for without the injections `run_call` requires.

    A deterministic-only run is a legal run (§6.6 decides a unique direct match
    with zero model calls), so this is raised only when a caller asked for a call
    it cannot make -- never as the ordinary state of a model-disabled run.
    """


class EvidenceSnapshotRequired(ValueError):
    """A snapshot id was asked for over no evidence at all."""


def placement_authorities(conn: sqlite3.Connection, *, plan_version: str,
                          policy: SupportPolicy,
                          sensitivity_policy) -> PlacementDependencies:
    """Site C's four. Each is a question P11 can answer and P8 cannot."""
    require_policy(policy)
    _require_sensitivity_policy(sensitivity_policy)
    return PlacementDependencies(
        node_exists=index_node_exists(conn, plan_version=plan_version),
        support_threshold=policy.minimum_support_threshold,
        margin_predicate=policy.margin_predicate,
        sensitivity_policy=sensitivity_policy,
    )


def residual_authorities(conn: sqlite3.Connection, *, plan_version: str,
                         approved_target_ids,
                         sensitivity_policy) -> ResidualDependencies:
    """Site D's three. `approved_target_ids` is the enabled residual set (§7.4)."""
    _require_sensitivity_policy(sensitivity_policy)
    return ResidualDependencies(
        node_exists=index_node_exists(conn, plan_version=plan_version),
        sensitivity_policy=sensitivity_policy,
        approved_target_ids=tuple(approved_target_ids),
    )


def _require_sensitivity_policy(sensitivity_policy) -> None:
    if not callable(sensitivity_policy):
        raise ModelPathUnavailable(
            "the sensitivity authority is P7's answer about this release and is "
            "injected; P8 returns ValidationUnavailable without it and P11 "
            "invents no permission"
        )


def site_dependencies(*, placement=None, residual=None) -> SiteDependencies:
    """One bundle, with the sites P11 does not own left None.

    `SiteDependencies.__post_init__` rejects a bare callable in any slot, which is
    the repair that closed the acceptance-callback hole; passing None for A, B and
    E is how P11 says it has no authority to offer there.
    """
    return SiteDependencies(fact=None, placement=placement, residual=residual,
                            template=None)


def to_p8_conflicts(conflicts) -> tuple[P8Conflict, ...]:
    """P11's `ConflictConsidered` as P8's `(conflict_id, kind)`.

    Site C rejects a response that ignored a dossier conflict, so the ids must be
    stable across the request and the response. They are derived from the
    conflict's own content rather than minted, so a replay of the same evidence
    produces the same ids -- and two conflicts that differ in any field get two
    ids, because a collision would let a model ignore one of them and be accepted
    for having addressed the other.
    """
    converted = []
    for conflict in conflicts:
        address = hashlib.sha256(_JOIN.join(
            (conflict.kind, conflict.conflicting_value, conflict.evidence_ref,
             # The count is part of the address for the same reason every other
             # field is: two conflicts that ruled out different numbers of
             # branches are different conflicts, and sharing an id would let a
             # model address one and be accepted for the other.
             str(conflict.suppressed_node_count),
             *conflict.suppressed_node_ids)).encode("utf-8")).hexdigest()[:16]
        converted.append(P8Conflict(conflict_id=f"conflict-{address}",
                                    kind=conflict.kind))
    return tuple(converted)


#: The `EvidenceItem` kinds whose `evidence_ref` is a PLAN identifier rather than an
#: address of the file's own text: `00`:110's node profile for every destination the
#: model may answer with -- `candidate` at C, `residual_area` and `branch` at D --
#: and the groups the person accepted the file into. The ratified C text says what
#: they are and what may not be done with them: a candidate's ref "is an identifier
#: from allowed_vocabulary", and of a group, "A group is support for a level and
#: never a citation ... A citation whose evidence_ref is a group's identifier
#: destroys the whole answer."
#:
#: `pipeline._offered_items` and `pipeline._accepted_group_items` MINT from these
#: names rather than spelling them, so the set cannot drift from the two producers
#: that write them.
CANDIDATE_ITEM: str = "candidate"
RESIDUAL_AREA_ITEM: str = "residual_area"
BRANCH_ITEM: str = "branch"
ACCEPTED_GROUP_ITEM: str = "accepted_group"
UNCITABLE_ITEM_KINDS: frozenset[str] = frozenset(
    {CANDIDATE_ITEM, RESIDUAL_AREA_ITEM, BRANCH_ITEM, ACCEPTED_GROUP_ITEM})


def snapshot_observation_keys(evidence_items) -> tuple[str, ...]:
    """The keys an evidence snapshot addresses: the ones the DOSSIER carries.

    `104` R-155. There were two spellings of this and they addressed different
    sets. `_judge_with_model` read the items it is about to hand
    `model_call_request` -- R-148's ruling, and the one the docstring below has
    always described -- while `versions._revalidates` read the matched FACTS. So a
    file whose dossier changed and whose facts did not revalidated against a hash
    of something the dossier no longer cites, and a file whose facts changed and
    whose dossier did not re-validated against a change nothing was shown. One
    could miss a change; the other could fire on none.

    There is one question here -- *what did the model see* -- so there is one
    function, and both callers pass the same thing to it: the `EvidenceItem`
    tuple, which `build_dossier` copies onto the `Dossier` verbatim and which a
    revalidation therefore has at hand on the dossier it is re-validating.

    **THE FOLDERS AND THE GROUPS ARE NOT ADDRESSED**, and that is why this is a
    function rather than an attribute read. `_judge_with_model` minted from the
    builder's items before appending its own offers; the STORED dossier carries
    all of them together (`pipeline` line 2133), so a revalidation reading
    `dossier.evidence_items` raw would hash node ids the original never did and
    the two paths would go on disagreeing for a new reason. An evidence snapshot
    addresses "what the dossier actually cites", and `UNCITABLE_ITEM_KINDS` is
    exactly what may not be cited -- the ratified C text's own ruling, and the
    pipeline's own sentence for the same exclusion: "a folder is not an
    observation, it carries no key P7 could resolve, and addressing one would put
    a plan id in a citation record". A plan id in the snapshot would also make the
    id move with the TREE, which `plan_version` already addresses on its own.

    The exclusion is a REFUSAL LIST and not an allow-list, deliberately. A new
    kind of reading of the file would be addressed by default, which is right --
    the snapshot must not silently stop covering something the dossier cites --
    while a new kind of OFFER is written in `pipeline` beside the constants above
    and joins them there.

    A refless item is dropped rather than addressed as an empty string, which is
    `EvidenceItem`'s own rule read forward: the ref is required non-empty today,
    so this cannot fire on any item shape that exists, and it is here for the
    day an item kind arrives with no address. The result is `evidence_snapshot_
    id_for`'s input and nothing else -- the sort and the de-duplication are its,
    because the order two callers happen to build their items in is not part of
    what the model saw.
    """
    return tuple(item.evidence_ref for item in evidence_items
                 if item.evidence_ref and item.kind not in UNCITABLE_ITEM_KINDS)


def evidence_snapshot_id_for(*, plan_version: str, observation_keys) -> str:
    """The id C and D require, minted from what the dossier actually cites.

    `record_cd_verdict` requires it and `run_call` refuses a C or D request
    without one BEFORE the spend. No SPEC assigns a producer, so P11 mints it as a
    content address: two dossiers over the same evidence at the same plan version
    share one id, which is what makes a replay recognisable as a replay, and a
    changed snapshot is what `revalidate_for_plan` keys a re-validation on.

    An empty citation set is refused rather than addressed. One id shared by every
    evidence-free dossier in a corpus would make each of them look like a replay
    of the last, which is the opposite of what the id is for.
    """
    keys = sorted(set(observation_keys))
    if not keys:
        raise EvidenceSnapshotRequired(
            "an evidence snapshot addresses the evidence a dossier cites, and "
            "this one cites none; a shared id over nothing would make every "
            "evidence-free dossier look like a replay of the last"
        )
    return "snap-" + hashlib.sha256(
        _JOIN.join((plan_version, *keys)).encode("utf-8")).hexdigest()[:32]


def transcribe(verdict, *, assessment) -> tuple[str, str | None, str | None]:
    """P8's verdict as (outcome, abstention_reason, deferred_stage).

    This is transcription, not interpretation. `accept_direct` and
    `accept_context_supported` are placements -- the difference between them is
    `requires_review`, which gates `review_policy` and not the outcome. `weak`,
    `reject` and `abstain` are all abstentions with a named reason, because
    §6.10's hierarchy is that an unresolved match stays unresolved and correct
    abstention is a successful outcome rather than a deferred move.
    """
    if verdict.outcome in (ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED):
        return PLACE, None, None
    if BUDGET_EXHAUSTED in verdict.reasons:
        # §8.6: cost exhaustion must never turn into a judgement about evidence.
        # It is the one abstention that names the stage it was cut short at.
        return P11_ABSTAIN, BUDGET_DEFERRED, PLACEMENT_SCORING
    if verdict.outcome not in (WEAK, REJECT, ABSTAIN):
        raise ValueError(f"{verdict.outcome!r} is outside P8's verdict vocabulary")
    for reason in verdict.reasons:
        mapped = _REASON_TO_ABSTENTION.get(reason)
        if mapped is not None:
            return P11_ABSTAIN, mapped, None
    if assessment is not None and assessment.abstention_reason is not None:
        return P11_ABSTAIN, assessment.abstention_reason, None
    return P11_ABSTAIN, NO_SUPPORTED_DESTINATION, None


def call_placement(conn, request, *, gate, model_client, prompt,
                   call_dependencies, observed_at, usage_recorder=None):
    """One Site C call, made here and answered here. `104` §18.15's serial form.

    `call_placement_steps` is the same call with the round trip left for a driver
    to run, and this is it driven inline: one call, one answer, on this thread.
    Kept as the seam's own callable because a caller that walks one subject at a
    time should not have to own a lane to ask a question.
    """
    return drive_inline(call_placement_steps(
        conn, request, gate=gate, model_client=model_client, prompt=prompt,
        call_dependencies=call_dependencies, observed_at=observed_at,
        usage_recorder=usage_recorder))


def call_placement_steps(conn, request, *, gate, model_client, prompt,
                         call_dependencies, observed_at, usage_recorder=None):
    """One Site C call. Every argument `run_call` requires, and nothing more.

    P11 supplies `gate`, `model_client` and `prompt` because `run_call` requires
    them. It never calls `gate.release` itself -- P8 does, inside `run_call`,
    after the eligibility and reduction decisions -- and it imports no concrete
    model client, only the capability the caller injected.

    `NeedsConsent` comes back unchanged and is handed to the review boundary. It
    is not an outcome, writes no P11 decision and no P2 row (B2).
    """
    missing = [name for name, value in (
        ("request", request), ("gate", gate), ("model_client", model_client),
        ("prompt", prompt), ("call_dependencies", call_dependencies),
    ) if value is None]
    if missing:
        raise ModelPathUnavailable(
            f"the model path needs {missing}; a run without them is a "
            "deterministic-only run and must be requested as one, not attempted "
            "and failed"
        )
    # `usage_recorder` is optional here for `run_call`'s own reason: the mailbox
    # is `104` R-14's and a transport that reports no usage is a real deployment.
    #
    # `104` §18.15: `yield from`, so the round trip this call makes is one the
    # caller may run beside its neighbours' on the cloud lane. Nothing else about
    # the call moves -- the gate, the reservation, the ledger and the verdicts are
    # all inside `run_call_steps`, on whichever thread asked.
    return (yield from run_call_steps(
        conn, request, gate=gate, model_client=model_client,
        prompt=prompt, validation_dependencies=call_dependencies,
        observed_at=observed_at, usage_recorder=usage_recorder))

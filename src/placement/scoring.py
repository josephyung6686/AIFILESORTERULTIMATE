"""§6.10's two conditions, computed deterministically and recorded in full.

The score is a weighted count of independent channels, normalised to the policy's
declared scale. It is deliberately simple and deliberately declared: SPEC Open
question 2 records that the design names "deterministic scores" and a "minimum
support threshold" without defining a scale, so the scale lives in the injected
`SupportPolicy` and is recorded on the decision, which is what lets a P2 replay
compare two runs and a reviewer see that a threshold changed.

Nothing here re-implements a P8 check. Site C's `BELOW_SUPPORT_THRESHOLD`,
`INSUFFICIENT_MARGIN` and `GENERIC_HUB_ONLY` judge a MODEL's answer. This module
judges P11's own evidence, produces the `support` and `next_support` the dossier
carries, and produces the verdict for the case §6.6 forbids a model call in.

The degenerate case is the walking skeleton's own shape (B8(b)). With one legal
candidate the margin is satisfied vacuously and the support threshold is the sole
gate -- and stays binding, because the scarcity of destinations is not evidence
about the file and a tree with one branch must not become a funnel.
"""
from __future__ import annotations

from dataclasses import dataclass

from placement.config import SupportPolicy, require_policy
from placement.graph import is_typed_support
from placement.records import Alternative, TwoCondition
from placement.retrieval import (
    ACCEPTED_GROUP, DIRECT_FACT, GRAPH_RELATIONSHIP, STRUCTURAL_RELATIONSHIP,
)
from placement.vocabulary import (
    ABSTAIN_NO_SUPPORTED_DESTINATION, ABSTAIN_VERDICT, ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT, CONFLICTING_FACTS, CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH, GENERIC_HUB_ONLY, LOW_MARGIN, MARGIN_FALSE, MARGIN_TRUE,
    MARGIN_TRUE_VACUOUS, NO_SUPPORTED_DESTINATION, SEMANTIC_ONLY, WEAK,
)

#: How much each channel contributes, before normalisation by the policy's scale.
#: These are structural weights over §6.3's channels, not tuned numbers: a direct
#: fact outweighs a group membership outweighs a relationship, which is §3.13's
#: own ordering, and the two non-deciding channels contribute nothing at all.
_CHANNEL_WEIGHT: dict[str, int] = {
    DIRECT_FACT: 3,
    ACCEPTED_GROUP: 2,
    GRAPH_RELATIONSHIP: 1,
    STRUCTURAL_RELATIONSHIP: 1,
}
_MAX_WEIGHT: int = sum(_CHANNEL_WEIGHT.values())


@dataclass(frozen=True)
class Scored:
    node_id: str
    support_score: float
    typed_support: bool
    semantic_only: bool
    generic_hub: bool


@dataclass(frozen=True)
class Assessment:
    scored: tuple[Scored, ...]
    two_condition: TwoCondition
    alternatives: tuple[Alternative, ...]
    unique_direct_match: bool
    abstention_reason: str | None
    confidence_class: str


def score_candidates(retrieval, graphs, *, policy: SupportPolicy) -> tuple[Scored, ...]:
    require_policy(policy)
    scored: list[Scored] = []
    for candidate in retrieval.candidates:
        graph = graphs.get(candidate.node_id)
        weight = sum(_CHANNEL_WEIGHT.get(channel, 0) for channel in candidate.channels)
        typed = graph is not None and is_typed_support(graph)
        semantic_only = candidate.node_id in retrieval.semantic_only_node_ids
        hub = graph is not None and bool(graph.anchors) and not typed
        scored.append(Scored(
            node_id=candidate.node_id,
            support_score=policy.support_scale_max * weight / _MAX_WEIGHT,
            typed_support=typed, semantic_only=semantic_only, generic_hub=hub,
        ))
    return tuple(sorted(scored, key=lambda s: (-s.support_score, s.node_id)))


def _reason(best: Scored | None, retrieval, meets_threshold: bool,
            meets_margin: str) -> str | None:
    """Why this could not become a placement, named from §6.10's own failure modes."""
    if best is None:
        return CONFLICTING_FACTS if retrieval.conflicts else NO_SUPPORTED_DESTINATION
    if meets_margin == MARGIN_FALSE:
        return LOW_MARGIN
    if meets_threshold:
        return None
    if best.semantic_only:
        return SEMANTIC_ONLY
    if best.generic_hub:
        return GENERIC_HUB_ONLY
    return NO_SUPPORTED_DESTINATION


def assess(retrieval, graphs, *, policy: SupportPolicy) -> Assessment:
    # `score_candidates` is the one place the policy is required, and `assess`
    # calls it before reading a single threshold. A second `require_policy` here
    # would be a guard that cannot fail -- the first line already refused -- and
    # would read as a rule this function enforces when it enforces nothing.
    scored = score_candidates(retrieval, graphs, policy=policy)
    best = scored[0] if scored else None
    runner_up = scored[1] if len(scored) > 1 else None

    meets_threshold = bool(best and best.support_score >= policy.minimum_support_threshold)
    if runner_up is None:
        # B8(b). No next-best exists, so there is nothing to measure and
        # `margin_over_next` has no value to hold. Recorded as vacuous so a
        # reviewer and a replay can tell it from a measured margin.
        margin_over_next = None
        meets_margin = MARGIN_TRUE_VACUOUS
    else:
        margin_over_next = best.support_score - runner_up.support_score
        meets_margin = (
            MARGIN_TRUE if policy.margin_predicate(best.support_score,
                                                   runner_up.support_score)
            else MARGIN_FALSE
        )

    reason = _reason(best, retrieval, meets_threshold, meets_margin)
    # §6.6's own words: "If a file's validated facts UNIQUELY MATCH ONE FROZEN
    # PATH, deterministic matching is faster, cheaper, and more stable"
    # (`planning/01-product-design-structured.md:1189-1191`). Uniqueness is a
    # property of the FACTS -- exactly one candidate carries the direct-fact
    # channel -- not of the candidate set's size. Keying it on "there was only
    # one candidate at all" would make B8(b) unsatisfiable: B8(b) requires the
    # skeleton to carry a second node so the margin is exercised rather than
    # vacuous, and no assessment can have both a measured margin and a candidate
    # set of one.
    #
    # `typed_support` is deliberately NOT required. §6.5's bar is about a target
    # "connected ONLY by generic similarity or one high-frequency entity"
    # (`:1183-1185`) -- it disqualifies similarity-based support, not a direct
    # fact match. Requiring a graph anchor here would mean a syllabus whose
    # subject fact names exactly one course could never be decided
    # deterministically, which is the case §6.6 exists to keep off the model.
    # Semantic-only and generic-hub candidates remain excluded because neither
    # carries `DIRECT_FACT` at all.
    #
    # Both §6.10 conditions still gate it: a unique direct match that falls short
    # of the support threshold, or that a runner-up crowds inside the margin, is
    # not decided here and goes to the model or abstains.
    direct_fact_candidates = tuple(
        candidate for candidate in retrieval.candidates
        if DIRECT_FACT in candidate.channels
    )
    unique_direct = bool(
        best is not None
        and len(direct_fact_candidates) == 1
        and direct_fact_candidates[0].node_id == best.node_id
        and meets_threshold
        and meets_margin != MARGIN_FALSE
    )

    if reason is None:
        # Both §6.10 conditions are met, so this is an acceptance -- but WHICH
        # acceptance is P8's own distinction and P11 records it truthfully. A
        # candidate that cleared the threshold on group and relationship evidence
        # with no direct fact anywhere is `accept_context_supported`, and calling
        # it `accept_direct` would name a fact match that never happened. P8's
        # own rule that `accept_context_supported` always requires review is
        # `TwoCondition`'s to enforce, and `requires_review` below satisfies it.
        verdict = ACCEPT_DIRECT if unique_direct else ACCEPT_CONTEXT_SUPPORTED
        confidence = EXACT_FACT_MATCH if unique_direct else CONTEXT_SUPPORTED_GROUP_MATCH
        requires_review = not unique_direct
    elif best is None:
        verdict = ABSTAIN_VERDICT
        confidence = ABSTAIN_NO_SUPPORTED_DESTINATION
        requires_review = True
    else:
        verdict = WEAK
        confidence = ABSTAIN_NO_SUPPORTED_DESTINATION
        requires_review = True

    two_condition = TwoCondition(
        support_score=best.support_score if best else 0.0,
        support_threshold=policy.minimum_support_threshold,
        meets_threshold=meets_threshold,
        margin_over_next=margin_over_next,
        margin_threshold=policy.margin_threshold,
        meets_margin=meets_margin,
        verdict=verdict,
        requires_review=requires_review,
    )
    alternatives = tuple(
        Alternative(node_id=item.node_id, support_score=item.support_score,
                    rank=rank)
        for rank, item in enumerate(scored, start=1)
    )
    return Assessment(
        scored=scored, two_condition=two_condition, alternatives=alternatives,
        unique_direct_match=unique_direct, abstention_reason=reason,
        confidence_class=confidence,
    )


def needs_model_call(assessment: Assessment) -> bool:
    """§6.6: never for a direct unique match; only for a bounded ambiguity.

    An assessment with no candidate at all also needs no call: there is nothing
    for a model to choose between, and asking one would be inviting it to invent.
    """
    if assessment.unique_direct_match or not assessment.scored:
        return False
    return True

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
    ACCEPTED_GROUP, CURATED_FOLDER, DIRECT_FACT, GRAPH_RELATIONSHIP,
    STRUCTURAL_RELATIONSHIP,
)
from placement.vocabulary import (
    ABSTAIN_NO_SUPPORTED_DESTINATION, ABSTAIN_VERDICT, ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT, CONFLICTING_FACTS, CONTEXT_SUPPORTED_GROUP_MATCH,
    EXACT_FACT_MATCH, GENERIC_HUB_ONLY, LOW_MARGIN, MARGIN_FALSE, MARGIN_TRUE,
    MARGIN_TRUE_VACUOUS, MULTIPLE_SUPPORTED_HOMES, NO_SUPPORTED_DESTINATION,
    SEMANTIC_ONLY, WEAK,
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
    #: Whether this candidate IS the folder the file is already sitting in.
    #: Carried, never weighted -- `_CHANNEL_WEIGHT` has no entry for
    #: `CURATED_FOLDER` and must not gain one. `assess` reads this only to
    #: decline to move a file, never to support moving one.
    already_there: bool = False


@dataclass(frozen=True)
class Assessment:
    scored: tuple[Scored, ...]
    two_condition: TwoCondition
    alternatives: tuple[Alternative, ...]
    unique_direct_match: bool
    abstention_reason: str | None
    confidence_class: str
    #: True only when `_staying_put_wins_a_tie` actually resolved a tie in favour
    #: of the folder the file is ALREADY IN. `needs_model_call` reads this and
    #: nothing else, so a caller that did not say which folders are the person's
    #: own gets exactly the behaviour it got before the rule existed.
    stays_put: bool = False


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
            already_there=CURATED_FOLDER in candidate.channels,
        ))
    return tuple(sorted(scored, key=lambda s: (-s.support_score, s.node_id)))


def _reason(best: Scored | None, retrieval, meets_threshold: bool,
            meets_margin: str, *, supported_count: int) -> str | None:
    """Why this could not become a placement, named from §6.10's own failure modes.

    A failed margin has two different causes and the user needs them told apart.

    `supported_count` is how many candidates cleared the support threshold ON
    THEIR OWN. When two or more did and nothing separates them, the file has more
    than one supported home and the sentence the user is owed is "these both fit;
    which is it?" -- a genuine choice, not a defect. When only the best one did
    (or none did), the margin failed against a rival the evidence never backed,
    and `low_margin` is the true name: the evidence is not decisive.

    Calling the first case `low_margin` was the defect `planning/59-FINAL-UX-
    EVALUATION.md` §3a records -- a research paper that is also school homework,
    reported as an evidence-quality complaint. Nothing about the ROUTING changes
    here: both are `weak`, both require review, and neither moves a file. What
    changes is which of two true sentences the person is told, because one makes
    them distrust the extraction and the other lets them just pick.
    """
    if best is None:
        return CONFLICTING_FACTS if retrieval.conflicts else NO_SUPPORTED_DESTINATION
    if meets_margin == MARGIN_FALSE:
        return MULTIPLE_SUPPORTED_HOMES if supported_count >= 2 else LOW_MARGIN
    if meets_threshold:
        return None
    if best.semantic_only:
        return SEMANTIC_ONLY
    if best.generic_hub:
        return GENERIC_HUB_ONLY
    return NO_SUPPORTED_DESTINATION


def _staying_put_wins_a_tie(
        scored: tuple[Scored, ...],
        their_own_folder_node_ids: frozenset[str] | None,
        refinements: frozenset[str] = frozenset(),
) -> tuple[tuple[Scored, ...], Scored | None, Scored | None, bool]:
    """THE FOLDER A FILE IS ALREADY IN IS NOT A RIVAL HOME; IT IS THE STATUS QUO.

    Returns the candidates in decision order, the best, the runner-up the margin
    is measured against, and whether this rule is what chose the best.

    `their_own_folder_node_ids` is `None` when the caller did not say which nodes
    are folders the person already has, and then this rule DOES NOT RUN. It is a
    rule about telling a proposal from a home, so without that it has nothing to
    tell apart, and guessing would be the over-refusal's mirror image. Every
    caller that does not supply it gets exactly the behaviour it had before this
    function existed.

    §6.9 abstains when a file has two homes, because choosing one institution
    over another is the failure it exists to prevent. That is a rule about two
    places a file could be MOVED to. When one of the tied candidates is the
    folder the file is ALREADY SITTING IN, the choice is not between two
    institutions -- it is between moving the file and leaving it alone, and a tie
    is not a reason to move somebody's file. So a candidate that merely ties with
    where the file already is is not a rival, and the margin is measured against
    the best candidate that actually scores LOWER.

    AND ONLY THEN. If ANOTHER tied candidate is also a folder the person MADE,
    this is §6.9 exactly as written -- material that belongs to two folders they
    actually have -- and it goes back to being asked. A syllabus in `Uni` that
    `Saved` claims just as strongly is a real question about two of their homes;
    the same syllabus against a `Coursework/PHYS1401/syllabus` this run would
    like to create is not, because a proposal is not a home yet.
    `tests/integration/test_cli_agreeing_corpus.py::test_two_folders_that_both_
    claim_the_value_still_have_to_ask` is that control and it stays green: "a fix
    that files everything is as wrong as one that files nothing".

    WHY THIS BECAME NECESSARY ON 2026-09-05. `_CHANNEL_WEIGHT` sums DEDUPLICATED
    channels, so a node expecting `term` and `work_type` scores exactly what a
    node expecting `term` alone scores. Until `work_type` gained a producer no
    node had ever expected two fields, and the tie could not arise. The day it
    could, a law student's own `Fall 2026` folder tied with a proposed
    `Coursework/Fall2026/syllabus`, the margin came out 0.0, and all five files
    in `_two_lives_one_semester_corpus` abstained -- the product stopped placing
    ANYTHING rather than place the wrong thing. That is the over-refusal failure
    mode: measured on the real 199-file corpus, silencing a producer cut wrong
    fields 17 -> 3 and pushed "not placed" from 85.4% to 97.6%.

    THIS IS NOT A WEIGHT AND MUST NOT BECOME ONE. §6.5 forbids a destination
    reached ONLY by generic similarity or a curated name, and `retrieval` already
    drops any candidate whose channels are all non-deciding -- so a curated
    folder can never BE a destination on its own, and this function never lets it
    become one. Every candidate here has already cleared the support threshold on
    §6.3's deciding channels. All this adds is which of two equals a person would
    rather the product chose, and the answer is the one that moves nothing.
    `tests/p11/test_p11_no_invention.py` pins `CURATED_FOLDER` out of
    `_CHANNEL_WEIGHT` and stays green, which is the point: the score is
    unchanged and only the tie is broken.

    Exact float equality is the right comparison and not a hazard: two tied
    candidates reach `support_score` through the identical expression on the
    identical weight, so they are the same float or they are not tied at all.

    **A TIED CHILD OF WHERE THE FILE ALREADY IS IS NOT A RIVAL TO STAYING; IT IS
    WHERE STAYING LEADS.** `refinements` names the candidates that lie INSIDE the
    folder this file is in. Everything above is about telling a proposal from a
    home, and a folder inside the person's own folder is neither: it is the same
    home, one level down. `00`'s amendment of line 22 makes going deeper inside
    the branch a file already sits in the model's call rather than a move to be
    refused, and this rule was refusing it -- a `Python 1006/lecture` that ties
    with `Python 1006` lost the tie to the parent and the file stopped one level
    short (`104` §11.1's sixth row, R-48).

    So a tied refinement wins the tie instead, and the margin is measured the way
    it is for any other winner. EXACTLY ONE, and two is not a near miss: the
    exemption says a deeper level is reachable and says nothing about WHICH, so
    two tied children fall through and staying put wins as it did before. That is
    `00`:111 -- "if the system cannot distinguish Spring 2025 from Spring 2026 but
    a parent path exists, the model should choose the approved shallower path" --
    and picking either child would be §6.9's arbitrary choice made one level down.
    """
    if not scored:
        return scored, None, None, False
    best = scored[0]
    runner_up = scored[1] if len(scored) > 1 else None
    if their_own_folder_node_ids is None:
        return scored, best, runner_up, False
    tied = tuple(item for item in scored
                 if item.support_score == best.support_score)
    refined = tuple(item for item in tied if item.node_id in refinements)
    if len(refined) == 1:
        # Refinement, not removal. The file goes deeper inside the folder it is
        # already in, so there is no status quo left to protect -- and recording
        # `stays_put` here would tell `needs_model_call` the opposite of what
        # happened.
        chosen = refined[0]
        lower = tuple(item for item in scored
                      if item.support_score < chosen.support_score)
        others = tuple(item for item in tied if item.node_id != chosen.node_id)
        return ((chosen,) + others + lower, chosen,
                (lower[0] if lower else None), False)
    staying = next((item for item in tied if item.already_there), None)
    rival_home = staying is not None and any(
        item.node_id in their_own_folder_node_ids
        and item.node_id != staying.node_id
        for item in tied)
    if staying is None or len(tied) == 1 or rival_home:
        return scored, best, runner_up, False
    # Recorded in decision order, so `alternatives` on the stored decision names
    # the chosen destination first and a replay can see why.
    lower = tuple(item for item in scored
                  if item.support_score < staying.support_score)
    others = tuple(item for item in tied if item.node_id != staying.node_id)
    return ((staying,) + others + lower, staying,
            (lower[0] if lower else None), True)


def assess(retrieval, graphs, *, policy: SupportPolicy,
           their_own_folder_node_ids: frozenset[str] | None = None,
           refinements: frozenset[str] = frozenset()) -> Assessment:
    # `score_candidates` is the one place the policy is required, and `assess`
    # calls it before reading a single threshold. A second `require_policy` here
    # would be a guard that cannot fail -- the first line already refused -- and
    # would read as a rule this function enforces when it enforces nothing.
    scored = score_candidates(retrieval, graphs, policy=policy)
    scored, best, runner_up, stays_put = _staying_put_wins_a_tie(
        scored, their_own_folder_node_ids, refinements)

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

    # Counted over ALL candidates rather than the top two, so three tied homes
    # read the same as two. `meets_threshold` above is the same predicate asked
    # of the best one; asking it of each is what tells "two homes" from "one home
    # and a rival nothing supports".
    supported_count = sum(
        1 for item in scored
        if item.support_score >= policy.minimum_support_threshold
    )
    reason = _reason(best, retrieval, meets_threshold, meets_margin,
                     supported_count=supported_count)
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
        confidence_class=confidence, stays_put=stays_put,
    )


def needs_model_call(assessment: Assessment, *, model_decides: bool = False) -> bool:
    """§6.6: never for a direct unique match; only for a bounded ambiguity.

    **UNLESS A MODEL DECIDES, WHICH IS R-19 AND THE OWNER'S Q-A RULING.** `104`
    §13.5 and `00`'s placement amendment, in the same words: "A unique direct
    match and the score-and-margin threshold no longer place a file without a
    model call. Every placement goes through the model. Deterministic scores rank
    and shortlist the candidates the model is shown... A unique direct match is
    the top-ranked candidate, not a bypass." So the two clauses below stop being
    reasons to skip the question and become reasons the answer is cheap to get
    right: the file arrives at site C with the deterministic winner ranked first.

    `model_decides` is the CALLER's fact and not this module's: a model is
    configured AND its text is ratified (`PipelineInputs.model_decides`). It
    defaults to False, so the offline path -- and every caller that has not
    stated a position -- gets exactly the routing it had. That is `00`'s own
    fallback: "with no model configured, the deterministic path remains the
    fallback and places only what it can validate."

    ONE CLAUSE DOES NOT MOVE, and it is the first line below: an assessment with
    no candidate at all is asked of nobody. `00`:106 forbids inventing a
    destination after freeze, so a file with no legal candidate has nothing for a
    model to CHOOSE between, and sending it is inviting the invention the whole
    of §6 exists to prevent. "Every placeable file" is the ruling's own scope.

    An assessment with no candidate at all also needs no call: there is nothing
    for a model to choose between, and asking one would be inviting it to invent.

    NEITHER IS A FILE THAT IS ALREADY WHERE THE ANSWER SAYS IT BELONGS. When both
    §6.10 conditions are met (`abstention_reason is None`) and the destination the
    assessment chose is the folder the file is ALREADY SITTING IN, the decision
    moves nothing. The only question a model could be asked is "should this file
    stay where it is?", which this assessment has just answered deterministically,
    and asking it anyway is what turned five files into five abstentions on
    `_two_lives_one_semester_corpus`: three of a law student's own coursework
    stopped being recognised as already filed, and the run placed NOTHING. A
    model call that cannot change the outcome is not a bounded ambiguity; it is a
    round trip whose only possible effects are cost, delay, and -- when no model
    is reachable, which is the offline default -- a refusal.

    `unique_direct_match` stays the first clause and is untouched. This adds the
    one case §6.6's "bounded ambiguity" was never about: there is no ambiguity
    between moving a file and leaving it exactly where its owner put it.
    `_staying_put_wins_a_tie` above is what makes `scored[0]` the answer here.
    """
    if not assessment.scored:
        return False
    if model_decides:
        return True
    if assessment.unique_direct_match:
        return False
    if assessment.stays_put and assessment.abstention_reason is None:
        return False
    return True

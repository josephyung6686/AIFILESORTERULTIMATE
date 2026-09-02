# src/eval_harness/vocabulary.py
"""Contract out §1 and §2 — the ten attribution stages and the ten measured
dimensions, which are two different ten-item lists (§8.5).

They are NOT merged here and no mapping between them is derived. `factual_validation`
and `candidate_node_retrieval` are stages with no same-named dimension; `residual` is
a dimension with no same-named stage. That is SPEC Open question 1, and it is open:
whether §7 residual handling gets its own attribution stage, and whether §6.2
candidate-node retrieval gets its own dimension, is for the design to settle. A
dimension value reaches a stage because the emitting stage names itself, never
because this module looked it up.
"""
from __future__ import annotations

#: §8.5's attribution stages, in §8.5's order — which is also the pipeline order of
#: §4.10 and §6.12. The order is used as the tie-break in earliest-divergence
#: attribution (Task 11), so it is a contract, not formatting.
STAGE_IDS: tuple[str, ...] = (
    "extraction",               # P5 (§2), shape from P4 (§2.8)
    "factual_validation",       # P6 (§3.5, §3.6)
    "retrieval",                # P9 (§4.2)
    "graph_construction",       # P9 (§4.3)
    "llm_interpretation",       # P8 (§3.3, §4.5)
    "grouping",                 # P9 (§4)
    "template_generation",      # P10 (§5.4, §5.7)
    "tree_design",              # P10 (§5)
    "candidate_node_retrieval", # P11 (§6.2)
    "placement_scoring",        # P11 (§6.10)
)

#: §8.5's measured dimensions. A separate list from the one above.
DIMENSIONS: tuple[str, ...] = (
    "extraction",     # "Did the expected text, metadata, table values, OCR text, or image facts appear?"
    "fact",           # "Did the system create the correct direct and validated facts? Did it abstain...?"
    "retrieval",      # "For sparse files, did the correct anchors appear in the top candidate neighborhood?"
    "graph",          # "Did edges reflect meaningful typed relationships? Did generic hubs create false...?"
    "llm_grounding",  # "Did every cited excerpt exist? Did the model return unknown...?"
    "grouping",       # "Did candidate groups include correct members, exclude outliers...?"
    "template",       # "Did a template generate useful real branches without needless depth?"
    "tree",           # "Did users accept, rename, merge, split, or reject proposed branches?"
    "placement",      # "Did the engine choose the correct frozen node, an appropriate shallow fallback, or abstain?"
    "residual",       # "Did the system avoid inventing associations for isolated files?"
)

#: §8.8: the destination tree and user policy define which projections are valid in
#: each version, while "the evidence database remains shared across plan versions."
PLAN_SCOPED_DIMENSIONS = frozenset({"grouping", "template", "tree", "placement", "residual"})
SHARED_EVIDENCE_DIMENSIONS = frozenset({"extraction", "fact", "retrieval", "graph", "llm_grounding"})

#: Contract out §4, one name each. A tuple alone cannot be CARRIED: there is no
#: name to import for one member, so every reader needing a single outcome
#: respells it, and a respelling is the second home MINOR 6 forbids. P5 is the one
#: deliberate exception and says so in its own docstring -- it imports no part of
#: P2, so it re-spells all five under a stated reason.
OUTCOME_PRODUCED = "produced"
OUTCOME_ABSTAINED = "abstained"
OUTCOME_DEFERRED = "deferred"
#: What makes the harness runnable before the stages exist (02-segmentation-map.md,
#: Order): a stage with no adapter reports this and its dimension scores `not_run`.
OUTCOME_NOT_IMPLEMENTED = "not_implemented"
#: A crash. Distinct from an abstention and from a deferral, and never either.
OUTCOME_ERROR = "error"

#: Contract out §4, closed. Built from the five above so the names and the tuple
#: cannot drift apart.
OUTCOMES: tuple[str, ...] = (OUTCOME_PRODUCED, OUTCOME_ABSTAINED, OUTCOME_DEFERRED,
                             OUTCOME_NOT_IMPLEMENTED, OUTCOME_ERROR)
BUDGET_STATES: tuple[str, ...] = ("within_ceiling", "ceiling_reached")

#: Contract out §6. Seven, exactly. `abstained_correctly` is a PASS (§6.10);
#: `deferred` is a budget event and never a divergence (§8.6).
VERDICTS: tuple[str, ...] = (
    "match", "divergent", "abstained_correctly", "abstained_incorrectly",
    "asserted_incorrectly", "deferred", "not_run",
)

RUN_KINDS: tuple[str, ...] = ("replay", "shadow", "adversarial")            # §8.5
CORPUS_FORMS: tuple[str, ...] = ("snapshot", "metadata_safe")               # §8.5
EXPECTED_OUTCOME_KINDS: tuple[str, ...] = ("produced", "abstained", "not-applicable")
EXPECTATION_SOURCES: tuple[str, ...] = (
    "hand-labelled", "captured-from-accepted-user-decision",
)

_STAGE_ORDER = {name: i for i, name in enumerate(STAGE_IDS)}


class UnknownStage(Exception):
    """A stage_id outside §8.5's closed ten."""


class UnknownDimension(Exception):
    """A dimension outside §8.5's closed ten."""


def check_stage(stage_id: str) -> str:
    if stage_id not in _STAGE_ORDER:
        raise UnknownStage(f"{stage_id!r} is not one of §8.5's ten attribution stages")
    return stage_id


def check_dimension(dimension: str) -> str:
    if dimension not in DIMENSIONS:
        raise UnknownDimension(f"{dimension!r} is not one of §8.5's ten measured dimensions")
    return dimension


def stage_order(stage_id: str) -> int:
    """Position in §8.5's list, which is §4.10's and §6.12's pipeline order."""
    return _STAGE_ORDER[check_stage(stage_id)]

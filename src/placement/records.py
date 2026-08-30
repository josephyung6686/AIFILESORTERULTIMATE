"""P11's frozen records. One shape for the §6 path and the §7 path.

The single most load-bearing rule: a consumer parses a residual decision with no
residual-specific branch (SPEC:610-612). Everything §7.7's eight actions need is
already a field the §6 path has, because two pairs of actions differ only by a
qualifier -- `return_target.kind` and `marked_state` -- and both are on the one
shape.

`decision_depth` is not detail. It is what replaced a deleted `destination.kind`
(SPEC:414-417): an empty `unsupported_levels` is the fully-supported child case, a
non-empty one is the deliberately shallower parent and names which levels were not
filled. Without it §6.7 has no expression in the record at all.

No field here can hold a filesystem path, a deletion, or an expiry. P11 names a
node; P12 resolves a path (B3), and §7.11 forbids the other two outright.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields

#: P9's third membership basis, in P9's spelling and from P9's own module. It is
#: not in P8's `EVIDENCE_BASES` (which has two), so it cannot come from there, and
#: M12 makes it mandatory. Imported rather than re-spelled: `grouping/vocabulary.py`
#: is its one home, and a second copy here is exactly the drift this project pays
#: for -- P9 could rename it and every check below would silently stop firing.
from grouping.vocabulary import USER_ATTACHED

from placement.vocabulary import (
    ABSTAIN, ABSTENTION_REASONS, ACCEPT_CONTEXT_SUPPORTED, ASK_USER,
    AUTO_ELIGIBLE, BUDGET_DEFERRED, CLASSES, CONFIDENCE_CLASSES, EVIDENCE_TYPES,
    FILE, MARGIN_TRUE_VACUOUS, MARKED_STATES, MARK_STATE, MEETS_MARGIN_VALUES,
    MODEL_ELIGIBILITY, NODE_ROLES, ORIGIN_STAGES, OUTCOMES, PLACE, PLACEMENT,
    RESIDUAL, RETURN_TARGET_KINDS, RETURN_TO_PLACEMENT, REVIEW_POLICIES,
    SET_CHOICES, STAGE_IDS, SUBJECT_KINDS, VALIDATED, VERDICTS, check,
)


class MalformedPlacementRecord(ValueError):
    """A P11 contract constructed in a shape P11 does not permit."""


def _freeze(instance: object, name: str) -> tuple:
    value = getattr(instance, name)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise MalformedPlacementRecord(
            f"{name} is a sequence; a bare string would become one entry per "
            "character"
        )
    frozen = tuple(value)
    object.__setattr__(instance, name, frozen)
    return frozen


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedPlacementRecord(f"{name} is required and must be non-empty")
    return value


def _number(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MalformedPlacementRecord(f"{name} must be a real number, not {value!r}")
    return float(value)


@dataclass(frozen=True)
class Subject:
    """What the decision is about. A file version, or an accepted group."""

    kind: str
    file_id: str | None
    content_hash: str | None
    group_id: str | None
    member_file_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        check(self.kind, SUBJECT_KINDS, name="kind")
        _freeze(self, "member_file_ids")
        if self.kind == FILE:
            _require(self.file_id, name="file_id")
            _require(self.content_hash, name="content_hash")
        else:
            _require(self.group_id, name="group_id")
            if not self.member_file_ids:
                raise MalformedPlacementRecord(
                    "a group decision names the members it covers; an empty group "
                    "plan would move nothing and explain nothing"
                )


@dataclass(frozen=True)
class Destination:
    """A node in the frozen tree. Never a path string (§5.12, B3)."""

    node_id: str
    node_role: str

    def __post_init__(self) -> None:
        _require(self.node_id, name="node_id")
        check(self.node_role, NODE_ROLES, name="node_role")


@dataclass(frozen=True)
class ReturnTarget:
    kind: str
    id: str

    def __post_init__(self) -> None:
        check(self.kind, RETURN_TARGET_KINDS, name="kind")
        _require(self.id, name="id")


@dataclass(frozen=True)
class Ask:
    """§6.9's question. Options are node ids, because the user picks a home."""

    question: str
    options: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.question, name="question")
        if len(_freeze(self, "options")) < 2:
            raise MalformedPlacementRecord(
                "asking the user to choose needs at least two options; one option "
                "is a placement wearing a question mark"
            )


@dataclass(frozen=True)
class DecisionDepth:
    """SPEC:332-334, and §6.7's rule in both directions.

    `node_depth` is the depth of the chosen node; `supported_depth` is the deepest
    level the evidence actually supports; `unsupported_levels` names the levels
    deliberately not filled.

    Two things are malformed, and they are not the same thing:

    * `node_depth > supported_depth` is §6.7's filled slot -- a level invented
      because a complete-looking path looked better than a true one.
    * `supported_depth > node_depth` with an EMPTY `unsupported_levels` is the
      broad-parent case with its record missing. SPEC:401-404 requires the levels
      deliberately not filled to be listed there, and without them the record
      cannot be told apart from a fully-supported child (SPEC:414-417) -- which is
      the one distinction this field exists to publish.
    """

    node_depth: int
    supported_depth: int
    unsupported_levels: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("node_depth", "supported_depth"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise MalformedPlacementRecord(f"{name} is a depth, not {value!r}")
        _freeze(self, "unsupported_levels")
        if self.node_depth > self.supported_depth:
            raise MalformedPlacementRecord(
                "a node deeper than the evidence supports is a filled slot, which "
                "§6.7 forbids; the shallower approved node is the answer"
            )
        if self.supported_depth > self.node_depth and not self.unsupported_levels:
            raise MalformedPlacementRecord(
                "the evidence reaches deeper than the node chosen, and the record "
                "names no level it deliberately left unfilled; SPEC:401-404 makes "
                "`unsupported_levels` the broad-parent case's whole expression, "
                "and an empty one here reads as a fully-supported child"
            )


@dataclass(frozen=True)
class MatchingFact:
    file_fact_id: str
    field: str
    value: str
    reliability: str
    evidence_ref: str

    def __post_init__(self) -> None:
        for name in ("file_fact_id", "field", "value", "reliability", "evidence_ref"):
            _require(getattr(self, name), name=name)
        # Against the CLOSED set, and not just for emptiness. `EVIDENCE_TYPES` is
        # five of P6's reliability states plus P9's membership basis, and the one
        # P6 state it leaves out is `rejected` -- named in the vocabulary as
        # `DROPPED_RELIABILITY_STATE` so that the exclusion reads as a decision.
        # The SPEC's reason: "a rejected fact cannot support a placement, so a
        # record resting on one would be a contradiction rather than a
        # low-confidence decision -- the correct expression is `outcome =
        # abstain`."
        #
        # Nothing enforced it. This field took any non-empty string, so a caller
        # that read a retracted row out of `file_facts` and passed it here got a
        # placement scored on a claim the person had already rejected, with
        # `exact fact match` printed beside it on their screen. Two asserts in
        # the vocabulary described a rule P11 could not apply.
        check(self.reliability, EVIDENCE_TYPES, name="reliability")


@dataclass(frozen=True)
class GroupSupport:
    group_id: str
    membership: str

    def __post_init__(self) -> None:
        _require(self.group_id, name="group_id")
        _require(self.membership, name="membership")


@dataclass(frozen=True)
class GraphAnchor:
    """One typed edge in the node-local graph that carried support (§6.5)."""

    edge_type: str
    from_file_id: str
    to_file_id: str
    anchor_file_id: str

    def __post_init__(self) -> None:
        for name in ("edge_type", "from_file_id", "to_file_id", "anchor_file_id"):
            _require(getattr(self, name), name=name)


@dataclass(frozen=True)
class ConflictConsidered:
    """§6.3's suppression, named in part and counted in full.

    `suppressed_node_ids` are the nodes some retrieval channel was pulling the
    subject towards and this conflict removed -- `00`:107's Columbia application
    branches, which the essay evidence reached and the Duke fact ruled out.

    `suppressed_node_count` is every node the conflicting value rules out,
    including the ones nothing was pulling towards. The two differ because naming
    the second set costs one row per node per file: on an 800-node tree where
    every branch states a course code, a 10,000-file corpus would record eight
    million node ids and hand the review surface a list of every folder the user
    owns (`planning/58-SCALE-STRESS.md` §2). Counted and unnamed is the same
    treatment §7's protected sets get -- present, explained, never silently
    omitted -- and it is the reason the count is a required part of the record
    rather than a convenience.

    It defaults to the length of the list, so a conflict built from a list ALONE
    still states a true count and no caller can produce a record where the number
    is smaller than the names.
    """

    kind: str
    conflicting_value: str
    suppressed_node_ids: tuple[str, ...]
    evidence_ref: str
    suppressed_node_count: int | None = None

    def __post_init__(self) -> None:
        for name in ("kind", "conflicting_value", "evidence_ref"):
            _require(getattr(self, name), name=name)
        _freeze(self, "suppressed_node_ids")
        if self.suppressed_node_count is None:
            object.__setattr__(self, "suppressed_node_count",
                               len(self.suppressed_node_ids))
        if not isinstance(self.suppressed_node_count, int) or (
                isinstance(self.suppressed_node_count, bool)):
            raise MalformedPlacementRecord(
                "suppressed_node_count is how many nodes the conflicting value "
                "ruled out; a non-integer is not a count"
            )
        if self.suppressed_node_count < len(self.suppressed_node_ids):
            raise MalformedPlacementRecord(
                f"this conflict names {len(self.suppressed_node_ids)} suppressed "
                f"nodes and claims {self.suppressed_node_count}; the named ones "
                "are a SUBSET of the counted ones, and a count below them would "
                "make the summary contradict the list beside it"
            )
        if self.suppressed_node_count <= 0:
            raise MalformedPlacementRecord(
                "a conflict that suppressed nothing did not act; §6.3 records the "
                "nodes it removed so the review surface can show what was ruled out"
            )


@dataclass(frozen=True)
class Alternative:
    node_id: str
    support_score: float
    rank: int

    def __post_init__(self) -> None:
        _require(self.node_id, name="node_id")
        object.__setattr__(self, "support_score",
                           _number(self.support_score, name="support_score"))
        if isinstance(self.rank, bool) or not isinstance(self.rank, int) or self.rank < 1:
            raise MalformedPlacementRecord("rank counts from 1")


@dataclass(frozen=True)
class TwoCondition:
    """§6.10 recorded, not merely applied (Done-means 10).

    `meets_margin` is three-valued because B8(b) requires an unopposed candidate to
    be distinguishable from a measured one: a reviewer and a P2 replay must be able
    to tell a genuine margin from a vacuous one, and a bare `True` cannot.
    """

    support_score: float
    support_threshold: float
    meets_threshold: bool
    margin_over_next: float | None
    margin_threshold: float
    meets_margin: str
    verdict: str
    requires_review: bool

    def __post_init__(self) -> None:
        for name in ("support_score", "support_threshold", "margin_threshold"):
            object.__setattr__(self, name, _number(getattr(self, name), name=name))
        if self.margin_over_next is not None:
            object.__setattr__(self, "margin_over_next",
                               _number(self.margin_over_next, name="margin_over_next"))
        check(self.meets_margin, MEETS_MARGIN_VALUES, name="meets_margin")
        check(self.verdict, VERDICTS, name="verdict")
        for name in ("meets_threshold", "requires_review"):
            if not isinstance(getattr(self, name), bool):
                raise MalformedPlacementRecord(f"{name} is a boolean")
        vacuous = self.meets_margin == MARGIN_TRUE_VACUOUS
        if vacuous and self.margin_over_next is not None:
            raise MalformedPlacementRecord(
                "a vacuous margin has no next-best to measure against; a number "
                "here would make an unopposed candidate look compared"
            )
        if not vacuous and self.margin_over_next is None:
            raise MalformedPlacementRecord(
                "a measured margin needs the value it measured; only B8(b)'s "
                "single-candidate case may leave it null, and it is `true_vacuous`"
            )
        if self.verdict == ACCEPT_CONTEXT_SUPPORTED and not self.requires_review:
            raise MalformedPlacementRecord(
                "accept_context_supported always requires review (§4.8, §6.10); "
                "P8's own verdict raises on the same shape"
            )


@dataclass(frozen=True)
class PrivacyState:
    """P7's answer, carried. `protected` is a FIELD and not an inference.

    §8.4 Open question 1 leaves the relation between the flag and the five
    handling classes unsettled and states that neighbouring parts consume the flag
    rather than infer it from the class. A record that carried only the class
    would leave every consumer no way to obey that, so the flag travels with it --
    which is also what keeps a protected container marked rather than quietly
    re-derived as ordinary further down the pipeline.
    """

    handling_class: str
    protected: bool
    model_eligibility: str
    consent_audit_ref: int | None

    def __post_init__(self) -> None:
        check(self.handling_class, CLASSES, name="handling_class")
        check(self.model_eligibility, MODEL_ELIGIBILITY, name="model_eligibility")
        if not isinstance(self.protected, bool):
            raise MalformedPlacementRecord(
                "`protected` is P7's flag and is a boolean; a null here would be "
                "read as `false` by every consumer that tests it"
            )


@dataclass(frozen=True)
class ResidualContext:
    set_id: str
    set_decision: str
    lifecycle_policy_ref: str | None

    def __post_init__(self) -> None:
        _require(self.set_id, name="set_id")
        check(self.set_decision, SET_CHOICES, name="set_decision")


@dataclass(frozen=True)
class PlacementDecision:
    decision_id: str
    plan_version: str
    supersedes: str | None
    superseded_by: str | None
    supersede_reason: str | None
    created_at: str
    origin_stage: str
    returned_from: str | None
    subject: Subject
    group_plan_id: str | None
    outcome: str
    destination: Destination | None
    return_target: ReturnTarget | None
    marked_state: str | None
    ask: Ask | None
    decision_depth: DecisionDepth
    evidence_type: str
    confidence_class: str
    matching_facts: tuple[MatchingFact, ...]
    group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]
    two_condition: TwoCondition
    abstention_reason: str | None
    deferred_stage: str | None
    privacy: PrivacyState
    review_policy: str
    explanation: str
    residual: ResidualContext | None

    def __post_init__(self) -> None:
        for name in ("decision_id", "plan_version", "created_at", "explanation"):
            _require(getattr(self, name), name=name)
        check(self.origin_stage, ORIGIN_STAGES, name="origin_stage")
        check(self.outcome, OUTCOMES, name="outcome")
        check(self.evidence_type, EVIDENCE_TYPES, name="evidence_type")
        check(self.confidence_class, CONFIDENCE_CLASSES, name="confidence_class")
        check(self.review_policy, REVIEW_POLICIES, name="review_policy")
        for name in ("matching_facts", "graph_anchors", "conflicts_considered",
                     "alternatives"):
            _freeze(self, name)
        if self.marked_state is not None:
            check(self.marked_state, MARKED_STATES, name="marked_state")
        if self.abstention_reason is not None:
            check(self.abstention_reason, ABSTENTION_REASONS, name="abstention_reason")
        if self.deferred_stage is not None:
            check(self.deferred_stage, STAGE_IDS, name="deferred_stage")

        # Outcome-shaped fields. Presence IS the contract (SPEC:319-329).
        if (self.destination is None) is (self.outcome == PLACE):
            raise MalformedPlacementRecord(
                "`destination` is present exactly when outcome is `place`; every "
                "other outcome names no node and produces no plan (M13)"
            )
        if (self.return_target is None) is (self.outcome == RETURN_TO_PLACEMENT):
            raise MalformedPlacementRecord(
                "`return_target` is present exactly on `return_to_placement`"
            )
        if (self.marked_state is None) is (self.outcome == MARK_STATE):
            raise MalformedPlacementRecord(
                "`marked_state` is present exactly on `mark_state`"
            )
        if (self.ask is None) is (self.outcome == ASK_USER):
            raise MalformedPlacementRecord("`ask` is present exactly on `ask_user`")
        if (self.abstention_reason is None) is (self.outcome == ABSTAIN):
            raise MalformedPlacementRecord(
                "an abstention names why (§6.10); an unexplained one is silence, "
                "and a reason on any other outcome contradicts the decision"
            )

        # Path exclusivity (SPEC:437-445). This is the only place the two paths differ.
        if self.outcome == RETURN_TO_PLACEMENT and self.origin_stage != RESIDUAL:
            raise MalformedPlacementRecord(
                "`return_to_placement` is the §7.9 loop and is emitted only on the "
                "residual path; §6 IS the placement engine and does not hand back "
                "to itself"
            )
        if self.outcome == ASK_USER and self.origin_stage != PLACEMENT:
            raise MalformedPlacementRecord(
                "`ask_user` is §6.9's multi-home question; the residual path is "
                "closed to the eight §7.7 actions and none of them asks"
            )
        if (self.residual is None) is (self.origin_stage == RESIDUAL):
            raise MalformedPlacementRecord(
                "`residual` is present exactly when origin_stage is `residual`"
            )

        if (self.abstention_reason == BUDGET_DEFERRED) != (self.deferred_stage is not None):
            raise MalformedPlacementRecord(
                "a budget deferral names the stage it was cut short at, and only a "
                "budget deferral has one: §8.6 requires deferred work to render "
                "differently from an evidential abstention"
            )

        if self.review_policy == AUTO_ELIGIBLE:
            if self.two_condition.requires_review:
                raise MalformedPlacementRecord(
                    "a verdict that requires review is never auto-eligible (§6.10)"
                )
            if self.group_support is not None and self.group_support.membership == USER_ATTACHED:
                raise MalformedPlacementRecord(
                    "a decision resting on a manual attachment is never automatic: "
                    "nothing was read from the file (M12, §4.9)"
                )
        if (self.group_support is not None
                and self.group_support.membership == USER_ATTACHED
                and self.evidence_type == VALIDATED):
            raise MalformedPlacementRecord(
                "a `user-attached` member never yields `validated`; nothing was "
                "read from the file to validate (M12)"
            )


#: Every field name the record publishes, in declaration order. `store` builds its
#: columns from this, so a field added here cannot be silently unstored.
DECISION_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(PlacementDecision))

# src/grouping/records.py
"""P9's frozen records. Shapes freeze here; later tasks must not rename them.

Two shape rules carry most of the weight.

`plan_version_id` lives on `GroupAcceptance` and nowhere else. Groups,
memberships, dossiers, edges and vectors live in the shared evidence database and
survive every plan version; what a plan version captures is a state ABOUT them.
The same candidate group can be accepted in version 2 and rejected in version 3
with neither decision destroying the other, and without duplicating the group,
its dossier, its model response, or a line of its evidence.

`Membership` carries no `review_state` for the same reason: it is resolved as of a
plan version from `group_acceptance`, and a stored copy would be a second home for
it that could disagree with the first.

P9 publishes no verdict enum. A membership references P8's verdict; it does not
restate the outcome.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from grouping.vocabulary import (
    COHERENCE_VERDICTS,
    COHERENT,
    CREATED_BY,
    DECIDED_BY,
    DECISION_SOURCES,
    DETECTED_BY,
    DIRECT_ANCHOR,
    EDGE_TYPES,
    FAILURE_STAGES,
    GROUP_STATES,
    LABEL_SOURCES,
    MEMBERSHIP_BASES,
    MEMBERSHIP_DECISIONS,
    NON_ANCHORING_SUPPORT,
    OUTLIER_FLAGS,
    REVIEW_STATES,
    SEED_KINDS,
    SHARED_VALIDATED_FACT,
    STOP_RULE_OUTCOMES,
    STOP_RULES,
    SUPPORT_KINDS,
    ACCEPTANCES,
    check,
)


class MalformedGroupRecord(ValueError):
    """A frozen P9 contract was constructed in a shape P9 does not permit."""


def _freeze(instance: object, name: str) -> tuple:
    value = getattr(instance, name)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise MalformedGroupRecord(
            f"{name} is a sequence; a bare string would become one entry per "
            "character"
        )
    frozen = tuple(value)
    object.__setattr__(instance, name, frozen)
    return frozen


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise MalformedGroupRecord(f"{name} is required and must be non-empty")
    return value


# --- the pieces -----------------------------------------------------------------


@dataclass(frozen=True)
class AnchorFact:
    """A fact that independently states the group's basis value.

    P10 asks for this under the name `anchor_facts[]`; it was `basis_facts[]` and
    is renamed here, not duplicated.
    """

    field: str
    value: str
    file_ids: tuple[str, ...]
    reliability_state: str
    observation_key: str

    def __post_init__(self) -> None:
        _require(self.field, name="field")
        _require(self.value, name="value")
        _require(self.reliability_state, name="reliability_state")
        _require(self.observation_key, name="observation_key")
        if not _freeze(self, "file_ids"):
            raise MalformedGroupRecord(
                "an anchor fact no file states is not an anchor"
            )


@dataclass(frozen=True)
class Support:
    """One retrieval channel that supports a membership.

    `support_kind` is the CHANNEL. It is not `Membership.basis`, which is the
    direct / context / user axis; the two were one name once and a validator
    checking "the" vocabulary rejected every valid value from the other side.
    """

    support_kind: str
    observation_key: str | None
    quote_or_field: str | None
    location: str | None
    edge_ref: str | None

    def __post_init__(self) -> None:
        check(self.support_kind, SUPPORT_KINDS, name="support_kind")
        if self.observation_key is None and self.edge_ref is None:
            raise MalformedGroupRecord(
                "a support resolves through an observation key or an edge; one "
                "that names neither cannot be cited or replayed"
            )


@dataclass(frozen=True)
class Conflict:
    """Competing course, institution, term, project, purpose or document-type facts."""

    kind: str
    competing_values: tuple[str, ...]
    file_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require(self.kind, name="kind")
        if len(_freeze(self, "competing_values")) < 2:
            raise MalformedGroupRecord(
                "a conflict names the values that compete; fewer than two is not a "
                "conflict"
            )
        _freeze(self, "file_ids")


# --- the records ----------------------------------------------------------------


@dataclass(frozen=True)
class Group:
    group_id: str
    seed_ref: str
    seed_kind: str
    proposed_basis: str
    anchor_facts: tuple[AnchorFact, ...]
    pre_model_signals: Mapping[str, object]
    anchor_count: int
    coherence_verdict: str | None
    coherence_citations: tuple[str, ...]
    group_category: str | None
    display_label: str | None
    label_source: str | None
    conflicts: tuple[Conflict, ...]
    stop_rule_hits: tuple[str, ...]
    state: str
    sensitivity_state: str
    dossier_id: str | None
    llm_response_ref: str | None
    validation_verdict_ref: str | None
    created_by: str
    created_at: str
    supersedes: str | None = None
    superseded_by: str | None = None
    supersede_reason: str | None = None

    def __post_init__(self) -> None:
        _require(self.group_id, name="group_id")
        _require(self.seed_ref, name="seed_ref")
        _require(self.created_at, name="created_at")
        _require(self.sensitivity_state, name="sensitivity_state")
        check(self.seed_kind, SEED_KINDS, name="seed_kind")
        check(self.state, GROUP_STATES, name="state")
        check(self.created_by, CREATED_BY, name="created_by")
        if not self.proposed_basis:
            raise MalformedGroupRecord(
                "the engine writes the reason a group exists BEFORE the model sees "
                "anything; a group with no proposed basis has none"
            )
        object.__setattr__(
            self, "pre_model_signals", MappingProxyType(dict(self.pre_model_signals)),
        )
        _freeze(self, "anchor_facts")
        _freeze(self, "coherence_citations")
        _freeze(self, "conflicts")
        for rule in _freeze(self, "stop_rule_hits"):
            check(rule, STOP_RULES, name="stop_rule_hits")
        if self.coherence_verdict is not None:
            check(self.coherence_verdict, COHERENCE_VERDICTS, name="coherence_verdict")
        if self.label_source is not None:
            check(self.label_source, LABEL_SOURCES, name="label_source")
        if not isinstance(self.anchor_count, int) or self.anchor_count < 0:
            raise MalformedGroupRecord("anchor_count is a non-negative count")

        # The label is conditional on coherence: absent, not empty.
        coherent = self.coherence_verdict == COHERENT
        if not coherent and (self.display_label or self.group_category):
            raise MalformedGroupRecord(
                "display_label and group_category are set only when "
                "coherence_verdict is 'coherent'; an uncoherent group carries no "
                "label rather than an empty one"
            )
        if self.display_label and self.label_source is None:
            raise MalformedGroupRecord(
                "a label without a label_source cannot say who proposed it"
            )


@dataclass(frozen=True)
class Membership:
    membership_id: str
    group_id: str
    file_id: str
    content_hash: str
    basis: str
    decision: str
    decision_source: str
    support: tuple[Support, ...]
    insufficient_evidence: bool
    insufficiency_statement: str | None
    conflicts: tuple[Conflict, ...]
    outlier_flag: str
    validation_verdict_ref: str | None
    created_at: str
    supersedes: str | None = None
    superseded_by: str | None = None
    supersede_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("membership_id", "group_id", "file_id", "content_hash",
                     "created_at"):
            _require(getattr(self, name), name=name)
        check(self.basis, MEMBERSHIP_BASES, name="basis")
        check(self.decision, MEMBERSHIP_DECISIONS, name="decision")
        check(self.decision_source, DECISION_SOURCES, name="decision_source")
        check(self.outlier_flag, OUTLIER_FLAGS, name="outlier_flag")
        _freeze(self, "conflicts")
        support = _freeze(self, "support")
        if not support:
            raise MalformedGroupRecord(
                "a membership with no support cannot say why the file belongs"
            )
        if any(not isinstance(item, Support) for item in support):
            raise MalformedGroupRecord("support entries must be Support records")

        if self.basis == DIRECT_ANCHOR:
            kinds = {item.support_kind for item in support}
            if SHARED_VALIDATED_FACT not in kinds:
                raise MalformedGroupRecord(
                    "direct-anchor requires a shared-validated-fact support "
                    "resolving to a Direct or Validated fact on this file"
                )
            if kinds <= set(NON_ANCHORING_SUPPORT):
                raise MalformedGroupRecord(
                    "semantic retrieval and bounded session can propose a "
                    "neighbour; they never anchor one"
                )
        if not isinstance(self.insufficient_evidence, bool):
            raise MalformedGroupRecord("insufficient_evidence is a boolean")
        if self.insufficient_evidence and not self.insufficiency_statement:
            raise MalformedGroupRecord(
                "insufficient_evidence carries the model's own statement; a bare "
                "flag records that something was missing without saying what"
            )


@dataclass(frozen=True)
class TypedEdge:
    edge_id: str
    from_file_id: str
    to_file_id: str
    edge_type: str
    evidence_ref: str
    weight: float | None
    bridge_entity_ref: str | None
    hub_suppressed: bool
    created_at: str
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        for name in ("edge_id", "from_file_id", "to_file_id", "evidence_ref",
                     "created_at"):
            _require(getattr(self, name), name=name)
        check(self.edge_type, EDGE_TYPES, name="edge_type")
        if not isinstance(self.hub_suppressed, bool):
            raise MalformedGroupRecord("hub_suppressed is a boolean")
        if self.from_file_id == self.to_file_id:
            raise MalformedGroupRecord("an edge from a file to itself relates nothing")


@dataclass(frozen=True)
class StopRuleOutcome:
    group_id: str
    rules_fired: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    outcome: str

    def __post_init__(self) -> None:
        _require(self.group_id, name="group_id")
        check(self.outcome, STOP_RULE_OUTCOMES, name="outcome")
        fired = _freeze(self, "rules_fired")
        _freeze(self, "evidence_refs")
        for rule in fired:
            check(rule, STOP_RULES, name="rules_fired")
        if not fired:
            raise MalformedGroupRecord(
                "a stop-rule outcome names the rules that fired; none is not an "
                "outcome, it is the absence of one"
            )


@dataclass(frozen=True)
class FailurePoint:
    """Six stages, logged separately. A collapsed error class is a violation.

    A bad group can fail because retrieval brought irrelevant neighbours, because
    the model overgeneralised from a good neighbourhood, or because the label was
    simply not useful, and consumers must be able to tell those apart without
    re-deriving which stage failed.
    """

    group_id: str
    dossier_id: str | None
    membership_id: str | None
    stage: str
    cause_code: str
    evidence_ref: str | None
    detected_by: str

    def __post_init__(self) -> None:
        _require(self.group_id, name="group_id")
        _require(self.cause_code, name="cause_code")
        check(self.stage, FAILURE_STAGES, name="stage")
        check(self.detected_by, DETECTED_BY, name="detected_by")


@dataclass(frozen=True)
class GroupAcceptance:
    """The ONLY plan-versioned record P9 publishes."""

    acceptance_id: str
    plan_version_id: str
    group_id: str
    membership_id: str | None
    acceptance: str
    review_state: str
    user_edited_label: str | None
    aliases: tuple[str, ...]
    review_decision_ref: str | None
    decided_by: str
    created_at: str
    supersedes: str | None = None
    superseded_by: str | None = None
    supersede_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("acceptance_id", "plan_version_id", "group_id", "created_at"):
            _require(getattr(self, name), name=name)
        check(self.acceptance, ACCEPTANCES, name="acceptance")
        check(self.review_state, REVIEW_STATES, name="review_state")
        check(self.decided_by, DECIDED_BY, name="decided_by")
        _freeze(self, "aliases")


# --- the candidate group dossier ------------------------------------------------
#
# The actual input to the LLM. It must not contain every file in full: "a large,
# noisy prompt encourages the model to find patterns that are not real" (§4.4).
#
# P9 assembles this. P8 materialises its own `Dossier` after P7 releases; the two
# are different records and P9 never constructs the second.


@dataclass(frozen=True)
class Excerpt:
    """A SHORT span, with the observation it came from.

    An excerpt whose key resolves to nothing cannot be verified by P8, and a key
    that survives an extractor upgrade is what lets a rejected dossier still
    resolve as a negative example afterwards.
    """

    observation_key: str
    location: str
    text: str

    def __post_init__(self) -> None:
        _require(self.observation_key, name="observation_key")
        _require(self.location, name="location")
        _require(self.text, name="text")


@dataclass(frozen=True)
class DossierFile:
    """One file in the dossier, on one side of the direct/context line."""

    file_id: str
    content_hash: str
    document_type: str
    basis: str
    key_facts: tuple[AnchorFact, ...]
    excerpts: tuple[Excerpt, ...]
    why_retrieved: str | None

    def __post_init__(self) -> None:
        for name in ("file_id", "content_hash", "document_type"):
            _require(getattr(self, name), name=name)
        check(self.basis, MEMBERSHIP_BASES, name="basis")
        _freeze(self, "key_facts")
        _freeze(self, "excerpts")


@dataclass(frozen=True)
class Omissions:
    """What was withheld, and why. Silence about a dropped file is the failure."""

    budget_cap_dropped: tuple[str, ...]
    privacy_redacted: tuple[str, ...]
    neighbourhood_capped: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("budget_cap_dropped", "privacy_redacted",
                     "neighbourhood_capped"):
            _freeze(self, name)


@dataclass(frozen=True)
class PrivacySummary:
    handling_classes: tuple[str, ...]
    redactions_applied: int
    release_decision_ref: str | None

    def __post_init__(self) -> None:
        _freeze(self, "handling_classes")
        if not isinstance(self.redactions_applied, int) or (
                self.redactions_applied < 0):
            raise MalformedGroupRecord("redactions_applied is a non-negative count")


@dataclass(frozen=True)
class BudgetSummary:
    token_ceiling: int
    neighbour_cap: int
    files_dropped: int

    def __post_init__(self) -> None:
        for name in ("token_ceiling", "neighbour_cap", "files_dropped"):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise MalformedGroupRecord(f"{name} is a non-negative count")


@dataclass(frozen=True)
class CandidateGroupDossier:
    dossier_id: str
    group_id: str
    proposed_basis: str
    anchor_files: tuple[DossierFile, ...]
    candidate_files: tuple[DossierFile, ...]
    typed_edges: tuple[TypedEdge, ...]
    key_facts: tuple[AnchorFact, ...]
    excerpts: tuple[Excerpt, ...]
    conflicts: tuple[Conflict, ...]
    engine_flagged_outliers: tuple[str, ...]
    omissions: Omissions
    privacy: PrivacySummary
    budget: BudgetSummary
    dossier_fingerprint: str
    created_at: str

    def __post_init__(self) -> None:
        for name in ("dossier_id", "group_id", "proposed_basis",
                     "dossier_fingerprint", "created_at"):
            _require(getattr(self, name), name=name)
        for name in ("anchor_files", "candidate_files", "typed_edges", "key_facts",
                     "excerpts", "conflicts", "engine_flagged_outliers"):
            _freeze(self, name)

        # The two arrays are never merged: the model must be able to call a group
        # coherent while still marking particular members uncertain, and it can
        # only do that if direct evidence and inferred context arrive apart.
        if not self.anchor_files:
            raise MalformedGroupRecord(
                "a dossier with no anchor file has no direct evidence to judge; "
                "SR1 stops before this record is built"
            )
        for item in self.anchor_files:
            if item.basis != DIRECT_ANCHOR:
                raise MalformedGroupRecord(
                    "an anchor file carries direct evidence by definition; a "
                    "context-supported file belongs in candidate_files"
                )
        for item in self.candidate_files:
            if item.basis == DIRECT_ANCHOR:
                raise MalformedGroupRecord(
                    "a direct-anchor file belongs in anchor_files"
                )
            if not item.why_retrieved:
                raise MalformedGroupRecord(
                    "a candidate file says which channel retrieved it; without that "
                    "a reviewer cannot tell a shared fact from a semantic guess"
                )
        anchors = {item.file_id for item in self.anchor_files}
        both = anchors & {item.file_id for item in self.candidate_files}
        if both:
            raise MalformedGroupRecord(
                f"{sorted(both)} appear as both anchor and candidate; one file is "
                "on one side of the direct/context line"
            )

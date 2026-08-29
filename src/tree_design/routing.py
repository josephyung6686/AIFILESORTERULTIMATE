# src/tree_design/routing.py
"""Branch evidence in; a small explained candidate set out. No nodes.

The route is deterministic and evidence-bound:

    accepted scaffold branch
      -> branch context (groups, domains, facts, purpose, privacy, the
         situations the evidence recognises)
      -> eligible applicability rows (schema AND detection signal)
      -> candidate compositions
      -> C1-C8 against the branch's actual evidence
      -> a bounded, ranked, INERT candidate set

Domain is one applicability signal, never a one-template ownership key. A row
makes a recipe eligible to PREVIEW; nothing here activates one, and nothing here
writes a node. C8 is the gate that says so, and it is the last one because every
earlier gate can still turn a plausible recipe into a refusal.

THE GATES DO NOT SHARE ONE CONSEQUENCE (owner ruling). Six refuse and cannot be
overridden: a missing artefact (C1), a minted field (C2), evidence that does not
support the recipe (C3), material a "successful" preview would drop (C6), a
privacy floor weaker than an included fragment's (C7), and a template that
activated itself (C8). Two surface a CHOICE the user resolves: which field an
ambiguous role means (C4) and which nesting two disagreeing partial orders
should become (C5). `CompositionOverride` can only be constructed for the second
kind — a refusal is not overridable at the point where an override would be
written down, not merely at the point where it would be honoured.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from tree_design.catalogue import TemplateCatalogue
from tree_design.config import TreeLimits
from tree_design.templates import (
    ApplicabilityRef,
    CompositionConflict,
    PurposeProfileRef,
    ResolvedDimension,
    TemplateApplicability,
    merge_fragment_constraints,
    resolve_fragment_imports,
)
from tree_design.upstream import AcceptedGroup, UpstreamUnavailable, resolve_role_to_field
from tree_design.user_edits import (
    UnappliedUserEdit, UserLevelEdit, apply_user_level_edits, describe_applied_edits,
)
from tree_design.vocabulary import (
    ACTION_SELECTED,
    SCOPE_SCHEMA_FIELD,
    C1,
    C2,
    C3,
    C4,
    C5,
    C6,
    COMPOSITION_GATES,
    GATE_WARN,
    OVERRIDABLE_GATES,
)


@dataclass(frozen=True)
class BranchContext:
    """Everything the router may consider. Nothing here is a domain label alone."""

    branch_node_id: str
    domains: tuple[str, ...]
    accepted_groups: tuple[AcceptedGroup, ...]
    member_file_ids: frozenset[str]
    handling_classes: frozenset[str]
    purpose_profile_refs: tuple[PurposeProfileRef, ...] = ()
    #: Which SITUATIONS this branch's evidence recognises, as the detection
    #: signals an applicability row cites. Carried in, never derived here — the
    #: same treatment `domains` gets from P9's `group_category` and
    #: `handling_classes` gets from P7.
    #:
    #: A signal is spelled `recognition:{row_id}` and names one compiled row in
    #: `src/recognition/library/recognition.json` — one of the 358 researched
    #: situations, `academic.coursework` beside `academic.study-abroad`.
    #: `51-LAUNCH-TEMPLATE-DRAFT.md` §5 fixes that binding: the refs "point at
    #: the node's own `recognition` block — R2 owns the actual patterns and this
    #: draft writes none". P10 writes none either: it reads the reference and
    #: asks whether the branch's evidence carried it.
    #:
    #: EMPTY IS A REAL ANSWER, and it is fail-closed: a branch whose evidence
    #: recognises no situation selects no row that claims one. It is not a
    #: licence to fall back to every row sharing a schema, which is the state
    #: this field exists to end.
    detection_signals: frozenset[str] = frozenset()


@dataclass(frozen=True)
class CompositionOverride:
    """One WARN-class gate the user resolved, and the decision they made.

    Constructing one for a REFUSE-class gate raises. That is deliberate: a
    record that CAN hold `gate="C7"` is one click from honouring it, and the
    owner ruling is that privacy and safety gates are not overridable at all.

    `approved_by` names the recorded user action. An override with no recorded
    action is the same defect C8 exists to prevent, one gate earlier.
    """

    gate: str
    approved_by: str
    #: C4: the field the user meant, per ambiguous role. Every choice must be one
    #: of the fields the applicability rows actually offered for that role.
    role_choices: Mapping[str, str] = field(default_factory=dict)
    #: C5: the nesting the user picked when the combined partial orders cycled.
    role_order: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.gate not in OVERRIDABLE_GATES:
            raise CompositionConflict(
                self.gate, [self.gate],
                "this gate refuses and is not overridable. A privacy, evidence, "
                "coverage, identity or activation failure is not a tidiness "
                "preference, and no recorded approval turns it into one"
            )
        if not self.approved_by or not str(self.approved_by).strip():
            raise CompositionConflict(
                self.gate, [self.gate],
                "an override names the recorded user action that authorised it; "
                "an unattributed override is indistinguishable from the system "
                "deciding for the user"
            )
        object.__setattr__(self, "role_choices",
                           MappingProxyType(dict(self.role_choices)))
        object.__setattr__(self, "role_order", tuple(self.role_order))


@dataclass(frozen=True)
class CompositionCandidate:
    applicability_refs: tuple[ApplicabilityRef, ...]
    resolved_dimensions: tuple[ResolvedDimension, ...]
    privacy_floor: str
    covered_file_ids: frozenset[str]
    gates_passed: tuple[str, ...]
    #: The WARN-class gates a recorded user decision resolved. Empty on a
    #: candidate that passed every gate outright, so "the user had to choose" is
    #: visible in the preview rather than buried in the log.
    overridden_gates: tuple[str, ...]
    explanation: str
    #: The `(template_id, template_version)` pairs this composition's rows named.
    #: `64` §5a puts the set of these on the frozen tree, so a tree can say which
    #: RECIPES built it and not only which library shipped them.
    template_refs: tuple[tuple[str, int], ...] = ()
    #: The user's own edits this composition could not honour (`64` §5c). A
    #: structural conflict is SURFACED, not resolved: if the release removed a
    #: level the user renamed, or resolves its role to another field, that is a
    #: question for the user rather than a decision for the product.
    unapplied_user_edits: tuple[UnappliedUserEdit, ...] = ()


@dataclass(frozen=True)
class RoutingReport:
    candidates: tuple[CompositionCandidate, ...]
    conflicts: tuple[CompositionConflict, ...]
    deferred: int

    @property
    def refusals(self) -> tuple[CompositionConflict, ...]:
        """The conflicts no user gesture can clear. Derived from the gate."""
        return tuple(c for c in self.conflicts if not c.overridable)

    @property
    def resolvable(self) -> tuple[CompositionConflict, ...]:
        """The conflicts that are choices. The surface offers these; it must not
        offer the refusals, and deriving both from one list is what keeps the two
        halves from drifting apart."""
        return tuple(c for c in self.conflicts if c.overridable)


def eligible_rows(catalogue: TemplateCatalogue,
                  context: BranchContext) -> tuple[TemplateApplicability, ...]:
    """Every row whose schema is one of this branch's domains AND whose
    detection signal this branch's evidence supports.

    THE SCHEMA IS THE WRONG GRAIN ON ITS OWN, and reading it alone was the
    defect. `uses_schema` says which SUBJECT a row speaks about; it does not say
    which SITUATION the row recognises, and one schema holds many. `academic`
    holds coursework, continuing education, an online course, a term abroad and
    a standardized test; eleven of the launch library's rows are `academic` and
    five of those share one definition. Collecting on the schema handed all five
    to one composition, and the five then named `school` "My school", "Course
    provider", "Course platform" and "Host university" — four correct names for
    four different audiences, merged into one recipe that necessarily refused at
    C4. Twenty-nine of the shipped library's fifty-four rows sat inside such a
    refusal. Nothing was wrong with the labels; the branch was simply never
    asked which situation it was in.

    `detection_signal_refs` is the field that answers that, and until now it had
    no reader anywhere in `src/`. This is the reader.

    THE TWO CASES ARE NOT SYMMETRIC, deliberately:

    * A row that CITES detection signals is selected only when the branch's
      evidence supports at least one of them. Several may match, and several is
      legitimate — a branch really can hold coursework beside a term abroad —
      so this narrows the merge without forbidding one.
    * A row that cites NONE states no situation at all, and stays eligible on
      its schema. An empty list is the row saying "wherever this schema is, I
      apply"; reading it as "nothing recognises me" would silently retire every
      such row, which is a library change made by a router.

    Eligibility is still not selection. A row here has earned only the right to
    be checked against the branch's actual evidence by C1-C8, and C4 still
    refuses when two rows a branch GENUINELY recognises name one field two ways
    — which is an authoring conflict in the library, and is the thing C4 was for
    before the framework's own over-collection drowned it.
    """
    rows: list[TemplateApplicability] = []
    for domain in context.domains:
        for row in catalogue.rows_for_schema(domain):
            if row.detection_signal_refs and not any(
                    signal in context.detection_signals
                    for signal in row.detection_signal_refs):
                continue
            rows.append(row)
    return tuple(rows)


def _overrides_by_gate(
        overrides: Sequence[CompositionOverride]) -> dict[str, CompositionOverride]:
    by_gate: dict[str, CompositionOverride] = {}
    for override in overrides:
        if override.gate in by_gate:
            raise CompositionConflict(
                override.gate, [override.gate],
                "two overrides answer one gate; a question with two answers has "
                "none")
        by_gate[override.gate] = override
    return by_gate


def _single_definition(catalogue: TemplateCatalogue,
                       rows: Sequence[TemplateApplicability]):
    """The one definition in play, or nothing when the rows name several.

    Its own dimensions and `relative_order` join the merge so a DEFINITION-LOCAL
    role — one no fragment mentions — takes the position the recipe authored
    rather than falling to `len(position)` and sorting last.

    With several definitions there is no single local ordering to apply, and
    choosing one would be the arbitrary pick this whole amendment removes.
    """
    seen = []
    for row in rows:
        definition = catalogue.definitions.get(
            (row.template_id, row.template_version))
        if definition is not None and definition not in seen:
            seen.append(definition)
    return seen[0] if len(seen) == 1 else None


def _recommended_order(catalogue: TemplateCatalogue,
                       rows: Sequence[TemplateApplicability]) -> tuple[str, ...]:
    """The nesting the DEFINITIONS in play recommend, or nothing.

    `routing.py` read none of `candidate_orders`, `chosen_order_id`,
    `default_order` or `.dimensions`: the whole runtime-ordering mechanism §5.3
    and §5.8 turn on was built, tested, and wired to nothing, so there was no
    code path by which a recipe's recommendation could win. This is that path.

    It is a RECOMMENDATION and it only breaks ties the fragment constraints leave
    open — it cannot override an edge a fragment states, because a fragment's
    relative order is a safety-and-meaning constraint and a recommendation is
    not. When several definitions are in play they must agree; two recipes
    recommending different nestings for the same branch is a conflict the user
    resolves, not one this function averages.
    """
    sequences = []
    for row in rows:
        definition = catalogue.definitions.get(
            (row.template_id, row.template_version))
        if definition is None:
            continue
        sequence = tuple(
            dimension.role_ref
            for dimension in sorted(definition.default_order.dimensions,
                                    key=lambda d: d.order_index))
        if sequence not in sequences:
            sequences.append(sequence)
    if len(sequences) != 1:
        return ()
    return sequences[0]


def evaluate_composition(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    rows: Sequence[TemplateApplicability],
    *,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
    overrides: Sequence[CompositionOverride] = (),
    user_edits: Sequence[UserLevelEdit] = (),
) -> CompositionCandidate:
    """Run C1-C8 over one candidate set of rows. Raise or return; never both.

    `user_edits` is applied AT THE END and never at the start (`64` §4). The
    gates must go on judging THE RECIPE rather than the recipe-as-the-user-
    rewrote-it: two rows that name one role two ways is a C4 refusal, and a
    rename applied first would collapse them into the user's single name and let
    a composition C4 exists to refuse ship as valid.
    """
    if not rows:
        raise CompositionConflict(
            C3, [*context.domains],
            "no applicability row makes any recipe eligible for this branch's "
            "domains, and there is no generic fallback to invent")

    by_gate = _overrides_by_gate(overrides)
    overridden: list[str] = []

    # C1 — identity. Every template, fragment and version the rows name exists.
    fragments = []
    for row in rows:
        definition = catalogue.definitions.get((row.template_id, row.template_version))
        if definition is None:
            raise CompositionConflict(
                C1, [f"{row.template_id}@{row.template_version}"],
                "the packaged release does not contain this definition version")
        for ref in definition.fragment_refs:
            fragments.extend(resolve_fragment_imports(catalogue, ref))
    # Deduplicate by exact identity, preserving import order.
    seen: set[tuple[str, int]] = set()
    ordered = []
    for fragment in fragments:
        key = (fragment.fragment_id, fragment.fragment_version)
        if key not in seen:
            seen.add(key)
            ordered.append(fragment)

    # C3 — applicability from evidence, not from a domain label. Run before C2
    # so a branch that was never eligible does not spend field lookups.
    for row in rows:
        if row.purpose_profile_ref is None:
            continue
        if not satisfies_purpose_profile(row.purpose_profile_ref,
                                         context.accepted_groups):
            raise CompositionConflict(
                C3, [row.purpose_profile_ref.purpose_profile_id, row.applicability_id],
                "the branch's accepted groups do not satisfy this authored purpose "
                "profile; a domain name alone is insufficient")

    # C4 — a required role resolves once. Competing mappings are SURFACED, and
    # the user resolves them; the router still picks none by itself.
    offered: dict[str, set[str]] = {}
    #: How each (role, field) pair is NAMED, per row. Keyed on the pair and not
    #: on the role alone: when C4 surfaces two fields for one role and the user
    #: picks one, the label that ships is the one authored beside the field they
    #: picked, not a name belonging to the mapping they rejected.
    offered_labels: dict[tuple[str, str], set[str]] = {}
    #: WHICH SCHEMAS bound each pair. A user edit is keyed per schema (`64` §3),
    #: and one recipe may serve two through two one-schema rows, so "does this
    #: rename speak about this level" is answered by the row that offered it and
    #: not by the composition as a whole.
    binding_schemas: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        for binding in row.role_bindings:
            offered.setdefault(binding.role_ref, set()).add(binding.field_ref)
            offered_labels.setdefault(
                (binding.role_ref, binding.field_ref), set()).add(binding.label)
            binding_schemas.setdefault(
                (binding.role_ref, binding.field_ref), set()).add(row.uses_schema)
    ambiguous = sorted(role for role, fields in offered.items() if len(fields) > 1)
    chosen: dict[str, str] = {
        role: next(iter(fields)) for role, fields in offered.items()
        if len(fields) == 1
    }
    if ambiguous:
        detail = "; ".join(f"{role} -> {sorted(offered[role])}" for role in ambiguous)
        override = by_gate.get(C4)
        if override is None:
            raise CompositionConflict(
                C4, ambiguous,
                f"a role resolves to more than one field ({detail}) and P10 picks "
                "none silently")
        for role in ambiguous:
            picked = override.role_choices.get(role)
            if picked not in offered[role]:
                raise CompositionConflict(
                    C4, [role],
                    f"the override chose {picked!r} for {role!r}, which no "
                    f"applicability row offered ({sorted(offered[role])}). An "
                    "override resolves an ambiguity the rows created; it is not a "
                    "second door into a field no row allows")
            chosen[role] = picked
        overridden.append(C4)

    # C2 — every resolved role maps to a live, destination-eligible P6 field.
    for role, field_ref in sorted(chosen.items()):
        try:
            resolve_role_to_field(conn, role_ref=role, field_ref=field_ref)
        except UpstreamUnavailable as exc:
            raise CompositionConflict(C2, [role, field_ref], str(exc)) from exc

    # C5 — combined order is acyclic, and the merge is intersection, not
    # last-writer-wins. `merge_fragment_constraints` raises C5 on either failure;
    # only the order half can be resolved by the user's chosen nesting.
    order_override = by_gate.get(C5)
    merged = merge_fragment_constraints(
        ordered, privacy_rank=privacy_rank,
        role_order=order_override.role_order if order_override else None,
        preferred_order=_recommended_order(catalogue, rows),
        definition=_single_definition(catalogue, rows),
        # C7, Amendment C: the exposure each SELECTED context requires. Only the
        # rows that survived C1-C6 contribute, because a floor from a row this
        # branch did not use would raise the protection of a context that is not
        # here.
        applicability_floors=tuple(
            row.privacy_floor for row in rows if row.privacy_floor))
    if merged.order_was_overridden:
        overridden.append(C5)
    position = {role: index for index, role in enumerate(merged.ordered_roles)}
    # THE FALLBACK IS GONE, and its absence is the fix. `position.get(role,
    # len(position))` sorted any role the merge did not order to LAST, silently
    # and with ties — so a definition-local dimension, or a role left unordered
    # because several recipes disagree, quietly became the leaf. A recipe asking
    # for venue first got venue last and nothing raised.
    #
    # A role whose nesting nothing decides is refused by name, the same answer
    # `merge_fragment_constraints` gives for an under-determined tie.
    unordered = sorted(set(chosen) - set(position))
    if unordered:
        raise CompositionConflict(
            C5, unordered,
            f"{', '.join(unordered)} resolved to a live field but nothing orders "
            "them: no fragment constrains them and no single recipe's own "
            "ordering applies, so where they nest is undefined")
    # The shipped name for each level, settled the same way the field was: by
    # agreement, never by picking. Two rows may both bind `artifact_kind` to
    # `work_type` and call it "Assignment type" and "Figure or draft" — one
    # field, two audiences, and nothing in the branch says whose words the
    # folder wears. That is C4's shape (a role resolving more than one way), so
    # it gets C4's answer: surface it and choose nothing. Taking the first would
    # make the user-visible name depend on the order the rows were listed in.
    labels: dict[str, str] = {}
    for role, field in chosen.items():
        names = offered_labels[(role, field)]
        if len(names) > 1:
            raise CompositionConflict(
                C4, [role],
                f"{role!r} resolves to {field!r} under more than one name "
                f"({sorted(names)}) and P10 names none silently")
        labels[role] = next(iter(names))

    resolved = tuple(
        ResolvedDimension(
            role_ref=role,
            field_ref=chosen[role],
            # A preview records `selected`: the user has chosen among what the
            # recipe offered, and has not yet acted on the branch. The edit
            # actions (`reordered`, `renamed`, ...) belong to the binding, after
            # the branch exists.
            action=ACTION_SELECTED,
            order_index=position[role],
            # The authored, per-schema name of this level. It was `None` here,
            # which made the only producer of the field a placeholder and left
            # the internal role key to reach the interface as the shipped
            # string. `materialise` reads it into every node's §5.12
            # explanation.
            display_label=labels[role],
            # Every dimension the ROUTER resolves came from an applicability
            # row's role binding and passed C2, so it is schema-field by
            # construction. A template-local level has no row and no field; it
            # arrives from an approved Site-E proposal, not from routing.
            scope=SCOPE_SCHEMA_FIELD,
        )
        for role in sorted(chosen, key=lambda r: position[r])
    )

    # C6 — coverage. Every member of every accepted group in this branch is
    # reachable through one of the selected rows' schemas.
    schemas = {row.uses_schema for row in rows}
    covered: set[str] = set()
    dropped: list[str] = []
    for group in context.accepted_groups:
        if group.domain in schemas:
            covered.update(member.file_id for member in group.members)
        else:
            dropped.extend(member.file_id for member in group.members)
    if dropped:
        raise CompositionConflict(
            C6, sorted(dropped),
            "this composition covers no schema for these members, so a preview "
            "would silently drop them")

    # C7 — the strongest included restriction survives the merge.
    floor = merged.privacy_floor

    # C8 — activation. Reaching here produces a preview and nothing else.

    # THE LAST STEP, and its position is the design (`64` §4). Every gate above
    # judged the recipe the library composed; this applies what the user said
    # about how the result is NAMED. A rename is the last word about
    # presentation and never a way to smuggle a change past a gate — which is
    # why nothing below it can refuse, and why nothing above it can see it.
    resolved, unapplied = apply_user_level_edits(
        resolved, user_edits, schemas_for_binding={
            key: frozenset(value) for key, value in binding_schemas.items()},
        composition_schemas=frozenset(schemas))

    explanation = (
        f"{len(rows)} applicability row(s) across {sorted(schemas)} resolve "
        f"{len(resolved)} dimension(s) from this branch's accepted groups; the "
        f"combined privacy floor is {floor}."
    )
    if overridden:
        explanation += (
            f" The user resolved {', '.join(overridden)} by recorded decision."
        )
    explanation += describe_applied_edits(resolved)
    return CompositionCandidate(
        applicability_refs=tuple(
            ApplicabilityRef(row.applicability_id, row.applicability_version)
            for row in rows),
        resolved_dimensions=resolved,
        privacy_floor=floor,
        covered_file_ids=frozenset(covered),
        gates_passed=tuple(COMPOSITION_GATES),
        overridden_gates=tuple(overridden),
        explanation=explanation,
        template_refs=tuple(sorted(
            {(row.template_id, row.template_version) for row in rows})),
        unapplied_user_edits=unapplied,
    )


def route_branch(
    conn: sqlite3.Connection,
    catalogue: TemplateCatalogue,
    context: BranchContext,
    *,
    limits: TreeLimits | None,
    privacy_rank: Callable[[str], int],
    satisfies_purpose_profile: Callable[[PurposeProfileRef, Sequence[AcceptedGroup]], bool],
    rank_candidates: Callable[[Sequence[CompositionCandidate]], Sequence[CompositionCandidate]],
    overrides: Sequence[CompositionOverride] = (),
    user_edits: Sequence[UserLevelEdit] = (),
) -> RoutingReport:
    """One candidate per eligible recipe AND the groups that recipe covers.

    A branch may hold more than one life. §5.3's card names "which accepted
    groups would live beneath" a top-level branch, plural, and `BranchContext`
    carries them plural — so the branch a person actually has spans several
    schemas, and a recipe authored for one of them covers some of its groups and
    not others. Each recipe is therefore asked about the groups it can reach, and
    a group no recipe reaches comes back as a NAMED C6 refusal rather than as a
    refusal on every candidate.

    Ranking is injected because the design fixes no weights, and the ceiling is
    P1's `tree.max_folder_proposals`. Surplus candidates are DEFERRED
    and counted, never silently dropped: §8.6 requires the interface to "show the
    difference between completed work and deferred work".

    Conflicts come back whole. The report splits them into `refusals` and
    `resolvable` by reading each gate's consequence, so a surface can offer the
    user the choices and only the choices.
    """
    candidates: list[CompositionCandidate] = []
    conflicts: list[CompositionConflict] = []

    rows = eligible_rows(catalogue, context)
    by_template: dict[tuple[str, int], list[TemplateApplicability]] = {}
    for row in rows:
        by_template.setdefault((row.template_id, row.template_version), []).append(row)

    if not by_template:
        # TWO DIFFERENT ABSENCES, told apart by name. "This library holds
        # nothing for finance" and "this library holds eighteen finance recipes
        # and this branch's evidence recognises none of their situations" send
        # the reader to different places — the first to the catalogue, the
        # second to the recognition rules and the branch's own files — and one
        # message for both would send them to the wrong one half the time.
        unselected = sorted(
            row.applicability_id
            for domain in context.domains
            for row in catalogue.rows_for_schema(domain))
        if unselected:
            conflicts.append(CompositionConflict(
                C3, unselected,
                f"{len(unselected)} applicability row(s) are authored for this "
                f"branch's domains {sorted(context.domains)} and this branch's "
                "evidence supports none of their detection signals, so no "
                "recipe recognises the situation these files are in. Widening "
                "to every row sharing a schema is what this gate exists to "
                "prevent"))
        else:
            conflicts.append(CompositionConflict(
                C3, [*context.domains],
                "no applicability row makes any recipe eligible for this "
                "branch's domains, and there is no generic fallback to invent"))

    # ONE COMPOSITION PER COVERAGE, not one per template over the whole branch.
    #
    # `59` §2: a branch holding a practice beside a degree beside a child's
    # health records "is not a two-branch outcome. It is a HARD ERROR on every
    # candidate" — because every template was handed EVERY group, and C6 refuses
    # any composition that would drop one. The fix is not to weaken C6. C6 means
    # "a successful preview loses nothing", it refuses for a good reason, and
    # material vanishing from a preview the user approved is the one outcome the
    # owner's standing rule forbids.
    #
    # The fix is that a multi-domain branch was handed to ONE composition at
    # all. `evaluate_composition`'s own comment says what it assumes — "Every
    # member of every accepted group IN THIS BRANCH" — which presupposes the
    # branch is a coverage. So the coverage is made here: each recipe is asked
    # about the groups its schemas actually reach, and a life the recipe does not
    # speak for is another recipe's candidate rather than this one's refusal.
    #
    # C6 keeps its teeth on both sides of that line. Inside a composition it is
    # unchanged and still refuses. Outside, material that reaches NO recipe is
    # not quietly absent from the candidate set: it is a C6 refusal of its own,
    # named by file, non-overridable, and — unlike before — it no longer
    # annihilates the candidates that do cover the rest of the branch.
    attempted: set[str] = set()
    for template_rows in by_template.values():
        schemas = {row.uses_schema for row in template_rows}
        covers = tuple(group for group in context.accepted_groups
                       if group.domain in schemas)
        if context.accepted_groups and not covers:
            # This recipe is eligible for a schema this branch has no group in.
            # That is not a refusal — nothing was dropped, because there was
            # nothing here for it to hold — so it is simply not a candidate.
            continue
        attempted.update(group.group_id for group in covers)
        try:
            candidates.append(evaluate_composition(
                conn, catalogue,
                # Only `accepted_groups` is narrowed. `domains` stays the whole
                # branch's because it is what the C3 message reports, and
                # `member_file_ids` stays whole because a candidate's coverage is
                # read off `covered_file_ids`, which `evaluate_composition`
                # derives from the groups it was actually asked about.
                dataclasses.replace(context, accepted_groups=covers),
                template_rows, privacy_rank=privacy_rank,
                satisfies_purpose_profile=satisfies_purpose_profile,
                overrides=overrides, user_edits=user_edits))
        except CompositionConflict as conflict:
            conflicts.append(conflict)

    # With NO eligible row at all, C3 above has already said so for the whole
    # branch, and a C6 naming the same files would be the same fact twice.
    unreached = tuple(group for group in context.accepted_groups
                      if group.group_id not in attempted) if by_template else ()
    if unreached:
        conflicts.append(CompositionConflict(
            C6,
            sorted(member.file_id
                   for group in unreached for member in group.members),
            "no recipe eligible for this branch covers "
            f"{', '.join(sorted(group.label for group in unreached))}: their "
            "domain is not one any applicable row is authored for. These files "
            "are named rather than dropped, and the candidates above cover the "
            "rest of the branch"))

    ranked = list(rank_candidates(candidates))
    deferred = 0
    if limits is not None and len(ranked) > limits.max_folder_proposals:
        deferred = len(ranked) - limits.max_folder_proposals
        ranked = ranked[:limits.max_folder_proposals]

    return RoutingReport(
        candidates=tuple(ranked),
        conflicts=tuple(conflicts),
        deferred=deferred,
    )

# src/tree_design/materialise.py
"""§5.4's populate step. The one module where evidence becomes structure.

The design sentence this module exists for is §5.4's: "Each template is populated
from the facts and accepted groups that already exist in the evidence database.
The system does not invent PHYS1401, UChicago, Spring 2026, or PVA/RDP; those
names emerge from validated facts, user-confirmed groups, and accepted labels.
The template simply determines how those real values could be arranged as
branches."

Everything here follows from that. A dimension contributes the DISTINCT settled
values its files actually carry, in P6's own spelling. A file with no settled
value at a level is unresolved at that level and produces no branch — §5.11
allows a tree to "be accepted even if some files remain unresolved", and the only
alternative is invention. A value nests under a parent value only when the same
files carry both, so the counts the user sees are intersections and never
products: §5.5's "three schools, five terms, and twelve course branches" is
twelve real combinations, not one hundred and eighty cells.

Two views come out of ONE pass, deliberately. `MaterialisedCandidate` is what
Task 9's V1-V6 judge; `BranchEvidence` is what the projection builds from. They
are returned together because a validator that saw a different shape from the
builder would pass a tree that cannot be built, or refuse one that can.

This module imports no other part's names. It reads P6 through
`tree_design.upstream`, which is the only module permitted to spell them.
"""
from __future__ import annotations

import dataclasses
import re
import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.node_key import level_key
from tree_design.records import ExpectedValue, Node, derive_accepts_placement
from tree_design.routing import CompositionCandidate
from tree_design.upstream import (
    FieldValue,
    GroupMember,
    anchors_a_level,
    preferred_value_for,
    resolve_role_to_field,
)
from tree_design.validation import (
    MaterialisedCandidate,
    MaterialisedLevel,
    ValidationReport,
)
from tree_design.vocabulary import (
    ACTION_OMITTED, FOLDED_ONE_FOR_ALL, FOLDED_ONE_PER_FILE, ORDINARY, PROPOSED,
    SCOPE_TEMPLATE_LOCAL,
)


class MaterialisationRefused(RuntimeError):
    """A branch cannot become nodes: its checks failed, or its inputs disagree."""


@dataclass(frozen=True)
class LevelEvidence:
    """One level, with the file sets `MaterialisedLevel` reduces to counts.

    `MaterialisedLevel.members_by_value` is `Mapping[str, int]` because V1-V6 ask
    "how many", never "which". The projection asks "which", because nesting is an
    intersection. Keeping both avoids widening Task 9's record for a question its
    checks do not ask.
    """

    dimension_role: str
    #: `None` on a template-local level. Contract W5 pairs the two: a level with
    #: no P6 field is one whose children came from accepted groups, and C2 is
    #: deliberately not run for it.
    field_ref: str | None
    order_index: int
    metadata_only: bool
    display_labels: Mapping[str, str]
    members_by_value: Mapping[str, frozenset[str]]
    handling_classes_by_value: Mapping[str, frozenset[str]]
    #: What this level is CALLED, in the words of the schema that bound it
    #: (Amendment A). Authored on `TemplateApplicability.role_bindings` and
    #: carried here by `ResolvedDimension.display_label`.
    #:
    #: It carries a default because `None` is a real value with a real meaning —
    #: "this level was composed without a binding, so nobody authored a name for
    #: it" — and `_label_of` answers for it. Every level the ROUTER builds has a
    #: label, because `RoleBinding.label` is required; a level built directly,
    #: as the suite's own fixtures do, has none.
    dimension_label: str | None = None
    #: `110` §2.2: the person said to leave this level out. A THIRD thing, kept
    #: apart from the two beside it for the reason `divides` gives about those
    #: two -- `metadata_only` is the TEMPLATE saying a dimension is measured and
    #: never built, `divides` is a fact about the corpus in front of us, and this
    #: is the person overruling both. A reader has to be able to tell "the design
    #: says this is metadata" from "your files only had one of these" from "you
    #: left it out", and one flag standing for all three could say none of them.
    omitted: bool = False

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(sorted(self.members_by_value))

    @property
    def divides(self) -> bool:
        """Whether building this level would actually separate anything.

        A level with one value produces "a folder the user opens to find one
        folder" -- V2's own words, and they are right. What was wrong is what V2
        DID about it: it failed the WHOLE candidate, so a household whose files
        carry one term and two subjects got no tree at all rather than a tree
        without the redundant term level. That is the third instance of one
        mistake -- V5 and `_project`'s truncation were the other two -- where a
        fault about ONE LEVEL is applied to a whole composition. `00`:97 asks only
        that a template not CREATE a meaningless one-child level; not building it
        satisfies that, and refusing the tree never did.

        Computed rather than stored, and kept SEPARATE from `metadata_only`: that
        flag means the TEMPLATE said this dimension is measured and never built,
        which is a fact about the recipe. This is a fact about the corpus in front
        of us, and a reader must be able to tell "the design says this is
        metadata" from "your files only had one of these".

        Counted over the level's own values, exactly as V2 counts them, and not
        over the members reaching one parent: a level that really does divide the
        corpus routinely offers one child under a particular parent -- `Columbia`
        with a single course under it is `00`:78's own tree -- and skipping those
        would flatten every branch that happens to be narrow.
        """
        return len(self.values) > 1


@dataclass(frozen=True)
class BranchEvidence:
    branch_node_id: str
    levels: tuple[LevelEvidence, ...]
    member_file_ids: frozenset[str]
    unresolved_by_field: Mapping[str, frozenset[str]]
    #: Members of this branch whose handling class is protected. They are IN
    #: `member_file_ids` and in every count — marked, not removed. `00`:101 asks
    #: tree health to show "where sensitive material has been isolated", and
    #: naming them is how the interface shows it. Removing them would be the
    #: silent omission the standing rule forbids.
    protected_file_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class FoldedLevel:
    """One level measured under one parent and not built, and why (`00`:98).

    Carried as DATA on the preview so the sentence is composed once, in
    `candidates.vertical_options`, and the node's own explanation says the same
    thing in the same words: two spellings of one fold is how a screen comes to
    promise a folder the tree does not hold. `106` Phase 7 §B.3: silence here
    is the product deciding something and not saying so.
    """

    parent_node_id: str
    parent_label: str
    dimension_role: str
    label: str
    values: tuple[str, ...]
    file_count: int
    reason: str


def folded_sentence(fold: FoldedLevel) -> str:
    """The one clause both the option and the node say about a fold."""
    if fold.reason == FOLDED_ONE_PER_FILE:
        return (f"{fold.label} was not made a folder under {fold.parent_label!r}: "
                f"each of its {fold.file_count} files would have had a folder of "
                "its own")
    return (f"{fold.label} {' / '.join(repr(v) for v in fold.values)} was not made "
            f"a folder under {fold.parent_label!r}: every file there carries it, "
            "so it would be a folder you open to find one folder")


def materialise_branch(
    conn: sqlite3.Connection,
    candidate: CompositionCandidate,
    *,
    branch_node_id: str,
    members: Sequence[GroupMember],
    ancestor_field_refs: Sequence[str],
    ancestor_depth: int,
    handling_class_for_member: Callable[[GroupMember], str],
    protected_handling_classes: frozenset[str] | None,
    metadata_only_roles: frozenset[str] = frozenset(),
    group_label_for_member: Callable[[GroupMember], tuple[str, str]] | None = None,
    group_level_roles: frozenset[str] = frozenset(),
    group_value_for_member: Callable[
        [GroupMember, str], FieldValue | None] | None = None,
) -> tuple[MaterialisedCandidate, BranchEvidence]:
    """Populate one composition from the branch's own files.

    `handling_class_for_member` is injected rather than read here because P7's
    store is another part's record and `upstream.py` is the only module allowed
    to name it. The caller passes `upstream.handling_class_for` already bound to
    a `ClassificationStore`.

    `protected_handling_classes` MARKS rather than removes, and the distinction
    is the whole point. The standing rule is that protected material is MARKED
    AND COUNTED, never opened, NEVER SILENTLY OMITTED — so a protected member
    stays a member, stays under its value, and stays in the counts the user
    reads. It is named in `protected_file_ids` so the interface can say "this
    branch holds one protected file and it will not be moved".

    Removing it would be the omission the rule forbids: a file dropped out of the
    evidence is uncounted, and uncounted is worse than present-but-untouched.

    The safety property does not depend on removal.
    `placement.privacy.automatic_move_permitted_for` delegates to P7's
    `may_move_automatically`, which refuses a protected file — and an
    unclassified one — unless an explicit policy permits it. P11 will not move
    it whether or not P10 counts it.

    What this ISN'T is a reason to refuse the branch. `handling_classes_by_value`
    is still the union of the members' classes, and V5 no longer reads it: one
    passport under `Columbia` used to give the STRING "Columbia" a protected
    class and refuse the whole composition, so the user lost the organisation and
    kept none of the protection.

    `group_label_for_member` returns `(group_id, label)` for one file and is
    required only when the candidate carries a template-local level. Such a
    level has no P6 field, so its children come from the accepted P9 groups
    (§2.3, E4) rather than from fact values. It is injected for the same reason
    as the handling class: the accepted group is P9's record, and inventing a
    label here would be P10 authoring the user's vocabulary.

    `group_level_roles` and `group_value_for_member` are the same shape one level
    over, and they are `104` §11.2 step 2. A group-level role -- coursework's
    `holder_institution` and `cycle_period` -- IS a P6 field and does resolve
    through C2, but its VALUE is the group's rather than each member's, because
    `00`:57 puts the course's school and term on the syllabus anchor and has the
    group carry the sparse members. So the loop below asks the group for it, once
    per member, through a reader `upstream` supplies; a member in no group gets no
    value and is unresolved at that level, which is exactly what "an essay outside
    any group gets no school level" means.

    Both default to "no level is the group's", which is true of 22 of the 23
    schemas and of every caller that predates the split.
    """
    if protected_handling_classes is None:
        raise ConfigurationRequired(
            "the set of handling classes that count as protected is injected "
            "configuration with no default: P7 owns HANDLING_CLASSES and has "
            "published no ordering, and a set chosen here would let P10 decide "
            "which of a user's material is isolated from the tree"
        )
    classes = {member.file_id: handling_class_for_member(member)
               for member in members}
    # Marked, NOT removed. These files stay members and stay counted; the name
    # is what lets the interface show them as present-but-not-movable.
    protected = frozenset(
        file_id for file_id, handling in classes.items()
        if handling in protected_handling_classes)
    member_ids = frozenset(member.file_id for member in members)

    levels: list[LevelEvidence] = []
    unresolved: dict[str, frozenset[str]] = {}
    ordered = sorted(candidate.resolved_dimensions, key=lambda d: d.order_index)
    for dimension in ordered:
        local = dimension.scope == SCOPE_TEMPLATE_LOCAL
        # `104` §11.2 step 2. NOT `local`: this level has a P6 field and passes C2
        # like any other, and only the SOURCE of its value moves from the file to
        # the group. Written as its own predicate rather than folded into `local`
        # because a template-local level has no field at all, and conflating the
        # two would skip C2 on a level that needs it.
        from_group = (not local) and dimension.role_ref in group_level_roles
        if local and group_label_for_member is None:
            raise ConfigurationRequired(
                f"level {dimension.role_ref!r} is template-local, so its children "
                "come from the branch's accepted groups; no reader for them was "
                "supplied and P10 invents no label"
            )
        if from_group and group_value_for_member is None:
            raise ConfigurationRequired(
                f"level {dimension.role_ref!r} takes its value from the accepted "
                "group this file belongs to (`00`:57), and no reader for one was "
                "supplied. Falling back to the file's own value is the collector "
                "`104` §11.1 measured -- five essays from a university course "
                "filed under a high school -- so it is refused instead"
            )
        if not local:
            # C2 again, at the point of USE. Task 7 resolves roles when it routes,
            # but a candidate reaching here with a field P6 does not define would
            # produce an empty level and a silently missing folder rather than a
            # refusal — and §3.12's "should not invent new fields automatically" is
            # exactly the rule a silent empty level breaks quietly. Fail closed.
            #
            # It is NOT run for a template-local level (Contract W5): that level
            # deliberately has no field, and asking P6 to define one would refuse
            # the whole novel-domain path at the gate meant to guard fact-backed
            # levels only.
            resolve_role_to_field(conn, role_ref=dimension.role_ref,
                                  field_ref=dimension.field_ref)
        by_value: dict[str, set[str]] = {}
        labels: dict[str, str] = {}
        classes_by_value: dict[str, set[str]] = {}
        missing: set[str] = set()
        #: Whether ANY member stated each value strongly enough to anchor a level
        #: on its own, which is what `_unanchored_single_values` needs and
        #: `by_value` cannot say.
        anchored: dict[str, bool] = {}
        for member in members:
            if local:
                # A group id is the child's identity and the group's own label is
                # its display name. Neither is a fact value, which is why no
                # `ExpectedValue` is written for this level (Contract W4.2-4.3).
                key, label = group_label_for_member(member)
                if not key:
                    missing.add(member.file_id)
                    continue
                by_value.setdefault(key, set()).add(member.file_id)
                labels.setdefault(key, label)
                classes_by_value.setdefault(key, set()).add(classes[member.file_id])
                continue
            # THE GROUP'S VALUE, OR THE FILE'S, and never one standing in for the
            # other. `00`:57: the course's school and term are on the syllabus
            # anchor and the group carries the sparse members, so an essay in the
            # course group takes the course's school and an essay in no group
            # takes none -- it joins `missing` and is unresolved at this level,
            # which §5.11 permits.
            settled = (
                group_value_for_member(member, dimension.field_ref) if from_group
                else preferred_value_for(
                    conn, file_id=member.file_id, field_ref=dimension.field_ref))
            if settled is None:
                missing.add(member.file_id)
                continue
            by_value.setdefault(settled.canonical_value, set()).add(member.file_id)
            labels.setdefault(settled.canonical_value, settled.display_label)
            anchored[settled.canonical_value] = (
                anchored.get(settled.canonical_value, False)
                or anchors_a_level(settled.reliability))
            classes_by_value.setdefault(settled.canonical_value, set()).add(
                classes[member.file_id])
        # NOT ON A TEMPLATE-LOCAL LEVEL, and the exemption is the rule's own
        # premise rather than a special case. That level's children ARE accepted
        # groups (Contract W4.2-4.3): the loop above `continue`s past
        # `preferred_value_for` for it, so no value there has a reliability to
        # weigh, and there is no fact for `00`:42's sentence to be about. Reading
        # the absent reliability as "unanchored" deleted a one-group level
        # outright, which `test_a_template_local_level_reaches_materialisation_
        # without_calling_c2` caught: a novel domain whose whole tree is one
        # accepted group is exactly the case that has one member and no fact.
        stopped = () if local else _unanchored_single_values(by_value, anchored)
        for value in stopped:
            # NOT A LEVEL, AND NOT A LOSS EITHER. The value stays on the file as
            # P6 wrote it and the file becomes unresolved AT THIS LEVEL, which is
            # §5.11's own state ("a tree can be accepted even if some files remain
            # unresolved") and reaches the person as "waiting for you to say what
            # this is". `00`:42's sentence is honoured exactly: the clue is kept
            # for review, and it does not quietly become a folder.
            missing.update(by_value.pop(value))
            labels.pop(value, None)
            classes_by_value.pop(value, None)
        unresolved[dimension.field_ref or dimension.role_ref] = frozenset(missing)
        levels.append(LevelEvidence(
            dimension_role=dimension.role_ref,
            field_ref=dimension.field_ref,
            order_index=dimension.order_index,
            metadata_only=dimension.role_ref in metadata_only_roles,
            # `110` §2.2. `apply_user_level_edits` marked the dimension rather
            # than deleting it, so the level is still measured here and its
            # values are still counted; what this flag decides is whether a
            # folder is built from them.
            omitted=dimension.action == ACTION_OMITTED,
            dimension_label=dimension.display_label,
            display_labels=dict(labels),
            members_by_value={value: frozenset(files)
                              for value, files in by_value.items()},
            handling_classes_by_value={value: frozenset(found)
                                       for value, found in classes_by_value.items()},
        ))

    evidence = BranchEvidence(
        branch_node_id=branch_node_id, levels=tuple(levels),
        member_file_ids=member_ids, unresolved_by_field=dict(unresolved),
        protected_file_ids=protected)
    return _for_validation(evidence, ancestor_field_refs, ancestor_depth), evidence


def _unanchored_single_values(by_value: Mapping[str, set[str]],
                              anchored: Mapping[str, bool]) -> tuple[str, ...]:
    """Values ONE file offered, on a model's word, with nothing behind them.

    `00`:42: a model output "that is useful but too weak to establish a fact may
    remain a possible clue for review; it must NOT quietly become a folder
    proposal or an asserted file property". `PROPOSAL_ELIGIBLE_STATES` admits
    everything above `possible`, which is the right bar for a value several files
    carry and far too low for one file saying something once -- and a LEVEL is the
    strongest assertion this product makes about a value, because it becomes a
    folder the person is shown and offered.

    Two ways out, and a value needs only one: **an anchor** -- some file states it
    at a state stronger than the weakest admissible one, which is `00`:63's
    "direct or validated anchor" -- or **a group** -- more than one file states it,
    which is the same evidence shape §5.4 relies on when it says names "emerge
    from validated facts". A value with neither is one model answer about one
    file.

    MEASURED ON THE OWNER'S 199 FILES (the `gt-cloud` run behind `104` §11).
    EVERY `school` value in that run is `llm_supported` and eight of the twelve
    were stated by exactly one file: the tree grew a `Cliffs Notes` level (a
    study-guide publisher), a `Dr. Beer` and a `Robert Beer` (an instructor), a
    `Hong Kong` (a place), a `DF 205` and a `University Writing`. Each became a
    folder a person was offered, and `Coursework/Cliffs Notes/notes` is where two
    PDFs that should have stayed "ask the person" were sent. Against that,
    `subject` carried `E1006` on five files and `ELTU3017` on three, both
    `validated` -- anchored, and untouched by this.

    WHAT IT DELIBERATELY DOES NOT TOUCH. `Georgetown Preparatory School` is
    `llm_supported` on SEVEN files, so it has a group and survives -- and it is
    the wrong level for five university essays. That is a different defect with a
    different fix (`104` §11.2 step 1: the `school` glossary entry means the
    institution offering the course, not any school the person attended), and
    silently taking it here would have made this rule look like it worked while
    hiding the one that matters.

    NO THRESHOLD IS INTRODUCED AND NO STATE IS SPELLED. "More than one" is not a
    tuned band -- it is the difference between a value and a single utterance --
    and the anchor bar is `upstream.anchors_a_level`, read off P6's own ladder at
    P10's declared seam onto it. Nothing here names a field, a word or a value.

    NOT CALLED FOR A TEMPLATE-LOCAL LEVEL. Its children are accepted groups and
    carry no reliability at all, so there is no fact for `00`:42's sentence to be
    about; the caller holds that guard and states why.
    """
    return tuple(
        value for value, files in by_value.items()
        if len(files) == 1 and not anchored.get(value, False))


def _label_of(level: LevelEvidence) -> str:
    """What to call this level in the sentence a user reads (Amendment A).

    The authored per-schema name when a binding supplied one; otherwise the P6
    field key, which is what every node said before the amendment and is still
    the honest answer for a level composed without a binding.

    The last fallback is the ROLE, not the null. A template-local level has no
    field by construction (Contract W5), so `field_ref or ...` alone would put
    the four characters `None` into every one of those nodes' explanations —
    §5.12 asks each node to state what caused it to appear, and "record None =
    'Physics Homework'" states nothing.
    """
    return level.dimension_label or level.field_ref or level.dimension_role


def _for_validation(evidence: BranchEvidence,
                    ancestor_field_refs: Sequence[str],
                    ancestor_depth: int) -> MaterialisedCandidate:
    """The same pass, in the shape V1-V6 read."""
    return MaterialisedCandidate(
        branch_node_id=evidence.branch_node_id,
        ancestor_field_refs=tuple(ancestor_field_refs),
        ancestor_depth=ancestor_depth,
        member_file_ids=evidence.member_file_ids,
        levels=tuple(
            MaterialisedLevel(
                dimension_role=level.dimension_role,
                field_ref=level.field_ref,
                order_index=level.order_index,
                metadata_only=level.metadata_only,
                values=level.values,
                members_by_value={value: len(files)
                                  for value, files in level.members_by_value.items()},
                handling_classes_by_value=dict(level.handling_classes_by_value),
            )
            for level in evidence.levels),
    )


def child_counts(evidence: BranchEvidence) -> Mapping[str, int]:
    """§5.5: "The user sees the actual branch counts before committing."

    One entry per level, holding the number of DISTINCT values that level would
    produce. This is the number the canvas states before an option is chosen.

    Keyed `field_ref or dimension_role`, the same pairing `unresolved_by_field`
    uses. A template-local level HAS no field, so keying on `field_ref` alone put
    every such level under one `None` key and the second silently overwrote the
    first — and two template-local levels are legal, which is why V1 exists to
    tell them apart from a repeated role. The user would then read one count for
    two levels.
    """
    return {level.field_ref or level.dimension_role: len(level.members_by_value)
            for level in evidence.levels
            if not level.metadata_only and not level.omitted}


def branch_expectations(evidence: BranchEvidence) -> tuple[ExpectedValue, ...]:
    """What a branch holds, when none of its levels was worth a folder.

    §5.4 measures every level and builds only the ones that divide -- "if every
    file names the same term, a folder for it would hold all of them and you
    would open it to find one folder" is the command's own disclosure and it is
    right. What was wrong is what happened to the measurement: nothing. A value
    measured and then written down nowhere has not been measured, it has been
    discarded.

    `_top_level_node` states the contract this fills: a proposed branch's
    "expectations are composed by `_project` from the branch's evidence".
    `_project` composed them onto CHILDREN, so a branch that built no child
    stated nothing at all -- and a destination that states nothing cannot be
    reached by a fact. Three files whose `subject` names the very branch they sit
    under scored on their group membership alone, short of §6.10's support
    threshold, and P11 reported that deciding them needed a model with the answer
    already sitting in `file_facts`.

    Exclusive with building, by construction rather than by care: `divides` is
    `len(values) > 1`, so a value stated here is one no folder was built for and
    no folder can be built for.

    Only the BRANCH, and never the chain beneath it. A child built from a
    dividing value already carries its own expected value and is already
    reachable; adding the undivided levels to its chain would make
    `Coursework/PHYS1401` claim `term = Spring2026` as well, which is a level
    deliberately not built made to discriminate after all -- and the next term's
    files would then be pushed off the course folder that is plainly theirs.

    A value carried by nothing but protected material is left out, exactly as
    `_project` leaves such a value out of a folder NAME. An expectation is spoken
    too: it reaches the placement index, the dossier, and every sentence that
    names a destination. The files stay members and stay counted -- what they
    lose is a claim of their own.
    """
    return tuple(
        ExpectedValue(field=level.field_ref, value=level.values[0])
        for level in evidence.levels
        if level.field_ref is not None
        and not level.metadata_only
        and not level.divides
        and level.values
        and not (level.members_by_value[level.values[0]]
                 <= evidence.protected_file_ids)
    )


def project_branch_nodes(
    evidence: BranchEvidence,
    report: ValidationReport,
    *,
    parent: Node,
    plan_version_id: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[frozenset[str]], str] | None,
    template_context_for: Callable[[str, int], object | None],
    protected_movement_permitted: bool = False,
) -> tuple[Node, ...]:
    """Turn a validated, populated branch into `Node` records.

    Nesting is by shared files. A value becomes a child of a parent value only
    when the same files carry both, which is what keeps the tree the size of the
    evidence rather than the size of the product of its dimensions.

    `handling_class_for` collapses the classes present under one value into the
    node's single class. It is injected with NO default: P7 publishes
    `HANDLING_CLASSES` as a set, not as an ordering, and a rank invented here
    could give a branch a weaker floor than one of its own files requires. This
    is the same treatment `privacy_rank` gets in Task 7.
    """
    if not report.accepted:
        raise MaterialisationRefused(
            f"branch {evidence.branch_node_id!r} failed "
            f"{', '.join(failure.check for failure in report.failures)}; §5.7's "
            "checks gate the build, not only the preview")
    if handling_class_for is None:
        raise ConfigurationRequired(
            "the handling-class collapse for a branch node is injected "
            "configuration with no default: P7 owns the ordering of "
            "HANDLING_CLASSES and has published none, and a rank chosen here "
            "could give a node a weaker floor than one of its files requires")

    return project_branch_preview(
        evidence, report, parent=parent, plan_version_id=plan_version_id,
        mint_node_id=mint_node_id, handling_class_for=handling_class_for,
        template_context_for=template_context_for,
        protected_movement_permitted=protected_movement_permitted).projected


@dataclass(frozen=True)
class BranchPreview:
    """The tree one option WOULD create, with the files that would sit in it.

    `00`:99 asks the interface to show, BEFORE the user chooses a split, "the
    resulting number of child branches, THE NUMBER OF FILES UNDER EACH CHILD,
    example members, unresolved files, and any evidence gaps", and to warn on the
    §5.9 conditions. `members_by_node` is the files-per-child half: without it
    `WARN_TINY_FOLDERS` cannot be computed at all, because `child_counts` answers
    how many BRANCHES a level makes and never how many FILES are under each.

    `parent` is kept apart from `nodes` on purpose. `nodes` is exactly what would
    be written, which is what `project_branch_nodes` returns and what the store
    persists; `tree` adds the branch being split, which is what §5.9 has to read
    — a level that produces one child is a fact about the PARENT, and a preview
    that omitted it could never fire `WARN_ONE_CHILD` on the first level.
    """

    parent: Node
    nodes: tuple[Node, ...]
    members_by_node: Mapping[str, frozenset[str]]
    #: The values `branch_expectations` put ON `parent`, empty whenever a child
    #: was built. Carried separately from `parent.expected_values` because an
    #: adopted folder arrives with observed ones and a reader has to be able to
    #: tell what this branch was MEASURED to hold from what its directory was
    #: seen to hold.
    branch_expectations: tuple[ExpectedValue, ...] = ()
    #: `106` Phase 7 §B. Every level the walk measured under a built node and
    #: did not build, with the reason. Empty is the common case.
    folded: tuple[FoldedLevel, ...] = ()

    @property
    def tree(self) -> tuple[Node, ...]:
        return (self.parent, *self.nodes)

    @property
    def projected(self) -> tuple[Node, ...]:
        """Exactly the nodes `project_branch_nodes` writes -- the rule, once.

        The branch itself is included when the composition put its values THERE
        rather than into a folder. It is a REWRITE of a node that already exists
        and creates nothing: `write_node` replaces the row and the expected values
        are added to it. Returning nothing here is what made `apply_review_action`
        refuse the whole run -- "accepting X produced no node" -- for a corpus
        whose files agreed on every dimension, which is the easiest corpus there
        is.

        It is a property on the preview rather than three lines inside
        `project_branch_nodes` because a caller that needs `members_by_node` --
        §5.8's answer is a claim about how many files a node holds -- has to take
        the preview, and would otherwise restate this rule beside it. Two copies
        of it is one copy too many: the day the branch is included on a second
        condition, one of them is wrong.
        """
        if self.branch_expectations:
            return (self.parent, *self.nodes)
        return self.nodes


def project_branch_preview(
    evidence: BranchEvidence,
    report: ValidationReport,
    *,
    parent: Node,
    plan_version_id: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[frozenset[str]], str] | None,
    template_context_for: Callable[[str, int], object | None],
    protected_movement_permitted: bool = False,
) -> BranchPreview:
    """`project_branch_nodes`, plus the member set behind each node.

    One traversal, one nesting rule. The member sets are recorded where they are
    already computed rather than recovered afterwards, so the preview's counts
    cannot disagree with the tree the projection would actually build.
    """
    if not report.accepted:
        raise MaterialisationRefused(
            f"branch {evidence.branch_node_id!r} failed "
            f"{', '.join(failure.check for failure in report.failures)}; §5.7's "
            "checks gate the build, not only the preview")
    if handling_class_for is None:
        raise ConfigurationRequired(
            "the handling-class collapse for a branch node is injected "
            "configuration with no default: P7 owns the ordering of "
            "HANDLING_CLASSES and has published none, and a rank chosen here "
            "could give a node a weaker floor than one of its files requires")

    nodes: list[Node] = []
    members: dict[str, frozenset[str]] = {}
    folded: list[FoldedLevel] = []
    _project(evidence, level_index=0, parent=parent,
             eligible=evidence.member_file_ids, chain=(),
             plan_version_id=plan_version_id, mint_node_id=mint_node_id,
             handling_class_for=handling_class_for,
             template_context_for=template_context_for,
             protected_movement_permitted=protected_movement_permitted,
             out=nodes, members_out=members,
             under_built=False, folded_out=folded)
    # `106` Phase 7 §B.2 after the walk, because "nothing beneath divides" is
    # a fact about a subtree the walk has not finished at the top of a chain.
    nodes = _fold_single_child_runs(nodes, members, folded, evidence)
    # §B.3: every fold is SAID on the folder that kept the files, so the
    # frozen tree carries the reason and the canvas can show it.
    said: dict[str, list[FoldedLevel]] = {}
    for fold in folded:
        said.setdefault(fold.parent_node_id, []).append(fold)
    nodes = [
        dataclasses.replace(node, explanation=node.explanation + "".join(
            f" {folded_sentence(fold)}." for fold in said[node.node_id]))
        if node.node_id in said else node
        for node in nodes]
    # Only when the walk built nothing. A branch with a child has reachable
    # destinations already, and a second claim on the parent would give one file
    # two direct-fact homes where its evidence names one.
    stated = () if nodes else tuple(
        expected for expected in branch_expectations(evidence)
        if expected.field not in {
            observed.field for observed in parent.expected_values})
    if stated:
        parent = dataclasses.replace(
            parent, expected_values=parent.expected_values + stated)
    return BranchPreview(
        parent=parent, nodes=tuple(nodes),
        members_by_node={parent.node_id: evidence.member_file_ids, **members},
        branch_expectations=stated, folded=tuple(folded))


#: The path a course sits on. `00`:78's tree is school, then term, then
#: subject, and a kind of work that actually splits hangs under that path.
#: A constant employer or a constant stage is not this path: `00`:57 still
#: measures those and does not build them.
_PATH_TO_A_SPLIT = frozenset({"school", "term", "subject"})


def _kept_as_the_path_to_a_split(evidence, level, level_index: int) -> bool:
    """One shared school, term, or subject, kept because a later level splits.

    A term both files name is not a split. It is the folder the split sits
    in: Spring 2026, then the one course, then homework beside syllabus.
    Nothing later that splits, or a field that is not this path, stays an
    expectation on the branch -- a level that divides nothing, as it was.
    """
    if level.field_ref not in _PATH_TO_A_SPLIT:
        return False
    if level.metadata_only or level.omitted or level.divides:
        return False
    if len(level.values) != 1:
        return False
    members = level.members_by_value.get(level.values[0])
    if not members:
        return False
    # The later split has to be among THESE files. A term one file names is
    # not the path to a course the other files named: keeping it buried the
    # courses under a folder they are not in, and the courses were never built.
    return any(
        later.divides and not later.metadata_only and not later.omitted
        and sum(1 for value in later.values
                if later.members_by_value.get(value, ()) & members) > 1
        for later in evidence.levels[level_index + 1:])


def _project(evidence, *, level_index, parent, eligible, chain, plan_version_id,
             mint_node_id, handling_class_for, template_context_for,
             protected_movement_permitted, out, members_out,
             under_built: bool = False, folded_out: list | None = None) -> None:
    """One level under one parent, then the next level under each child.

    `under_built` says whether `parent` is a node THIS walk minted rather than
    the branch's own node: `106` Phase 7 §B.1's fold applies only beneath a
    built node, and `folded_out` collects what was measured and not built.
    """
    if folded_out is None:
        folded_out = []
    if level_index >= len(evidence.levels):
        return
    level = evidence.levels[level_index]
    # A level that does not divide is still the PATH to one that does.
    # `00`:78's own tree is Academics / Columbia / 2026-Spring / PHYS1401, and
    # a term every file shares is that path when the kind of work beneath it
    # splits the files. Skipping it left the split hanging off the life
    # (`Education / homework`) and threw away the term and the subject the
    # files had already named. A level nothing later divides, a metadata
    # level, and a level the person left out stay unbuilt: a folder you open
    # to find one folder, with no split under it, is still not a folder.
    if ((level.metadata_only or level.omitted or not level.divides)
            and not _kept_as_the_path_to_a_split(evidence, level, level_index)):
        # §5.4: a metadata-only dimension is measured and never becomes a folder.
        # `110` §2.2 adds the person's own reason to the same branch, and adds it
        # HERE rather than anywhere new: the walk already knows how to carry a
        # measured-and-unbuilt level's members down to the next level under the
        # same parent, which is exactly what "keep them all directly under this
        # folder instead of splitting by purpose" asks for.
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain, plan_version_id=plan_version_id,
                 mint_node_id=mint_node_id, handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out,
                 under_built=under_built, folded_out=folded_out)
        return

    children: list[tuple[str, frozenset[str]]] = []
    for value in level.values:
        members = level.members_by_value[value] & eligible
        if not members:
            continue
        if members <= evidence.protected_file_ids:
            # MARKED, COUNTED, NEVER OPENED -- and never SPOKEN. A folder name is
            # public: visible in the filesystem and in every prompt that names a
            # destination. A name carried by NOTHING BUT protected material
            # publishes that material, and `X12345678`, a client's passport
            # number, was a proposed folder on a real corpus.
            #
            # This does not remove the file and does not uncount it. Its members
            # stay in `eligible`, so they stay under this parent, stay in its
            # counts, and stay in `protected_file_ids` for §5.9 to report -- the
            # standing rule's "never silently omitted" is about the FILE, and the
            # file is still here. What it loses is a NAME of its own.
            #
            # Neither existing lever could do this. `protected_handling_classes`
            # marks rather than removes on purpose -- "uncounted is worse than
            # present-but-untouched" -- and V5 refuses the WHOLE composition,
            # which is the failure its own docstring records: "the user lost the
            # organisation and kept none of the protection".
            #
            # `<=`, not `&`: a value ANY ordinary file also carries is untouched,
            # because then the name is not derived from protected material. A
            # matter number shared with four ordinary documents stays a folder;
            # a passport number that appears nowhere else does not.
            continue
        children.append((value, members))

    # `106` Phase 7 §B.1, `00`:98: "a two-file application packet may remain a
    # single folder". Beneath a built node -- and only there, because at the
    # root there is no chain a folded file could still be reached by -- a level
    # that would give every file a folder of its own is measured and not built.
    # The files stay members of `parent`; the fold is recorded so the option
    # and the node both say it. `len(members) == 1` is the degenerate
    # partition, not a threshold.
    #
    # NOT a template-local level (Contract W5, `field_ref is None`): its
    # children are the person's own ACCEPTED GROUPS, not fact values, and
    # `00`:68 forbids silently reorganising what the person made. A rule
    # about which facts earn a folder does not reach a folder the person
    # asked for by accepting a group.
    # RETIRED BY `00` AMENDMENT 27 (the owner, 19 Sep, asked with both trees
    # drawn): a level every value splits IS built, even where every folder holds
    # one file. The refusal stood here and read:
    #
    #     if under_built and level.field_ref is not None and len(children) > 1
    #             and all(len(members) == 1 for _value, members in children):
    #
    # -- so a course holding an exam, a homework, notes and a syllabus, one of
    # each, showed four loose files and no kinds at all.
    #
    # WHAT IT READ TOO WIDELY. It cited `107`'s "a single unusual file may remain
    # at the closest meaningful parent rather than creating a one-file leaf", but
    # that sentence is about ONE unusual file resting at its parent -- not about
    # refusing a complete split where every kind happens to hold a single file.
    # `00`:98's "a two-file application packet MAY remain a single folder" is
    # permissive and licenses leaving a packet whole; it does not require refusing
    # a level the person's own kinds divide cleanly.
    #
    # THE NARROWNESS IS WHY LIFTING IT IS SAFE: the rule fired only where EVERY
    # child held exactly one file, so this reaches that case and no other. An
    # outlier beside crowded siblings was never in its scope.
    #
    # `FOLDED_ONE_PER_FILE` and `folded_sentence`'s arm for it are now unreachable
    # from here. They are LEFT IN PLACE, not deleted: plan databases written
    # before today hold rows carrying that reason, and a reader that cannot spell
    # them could not read an existing plan.

    ordinal = 0
    for value, members in children:
        node_id = mint_node_id()
        label = level.display_labels.get(value, value)
        # Contract W4.2-4.3: a template-local level writes NO expected value.
        # Its children are accepted group labels, which are not fact values, so
        # the node inherits only what its schema-field ancestors settled and its
        # own `dimension` stays null. Writing one here would assert a fact P6
        # never made, and P11 would then match files against it.
        expected = chain if level.field_ref is None else chain + (
            ExpectedValue(field=level.field_ref, value=value),)
        node = Node(
            node_id=node_id,
            plan_version_id=plan_version_id,
            node_type=PROPOSED,
            display_label=label,
            parent_node_id=parent.node_id,
            root_anchor=parent.root_anchor,
            ordinal=ordinal,
            associated_group_ids=parent.associated_group_ids,
            explanation=(
                f"{len(members)} of this branch's files record "
                f"{_label_of(level)} = {label!r}. P6 settled that value; P10 "
                f"placed it under {parent.display_label!r} and composed nothing."),
            node_role=ORDINARY,
            accepts_placement=derive_accepts_placement(
                PROPOSED,
                protected_movement_permitted=protected_movement_permitted),
            handling_class=handling_class_for(level.handling_classes_by_value[value]),
            # `106` Phase 5.1 (SPEC OQ5 closed): the origin is the node's KEY --
            # the parent's key and what this folder is named by -- so a re-run
            # that builds the same folder writes the same origin, and every
            # cross-version reader that already compares origins works across
            # runs. `node_id` above is still minted per version.
            origin_node_id=level_key(parent.origin_node_id, field=level.field_ref,
                                     value=value, role=level.dimension_role),
            template_context=template_context_for(level.field_ref, level.order_index),
            dimension_role=level.dimension_role,
            dimension=level.field_ref,
            expected_values=expected,
            protected_movement_permitted=protected_movement_permitted,
        )
        out.append(node)
        members_out[node_id] = members
        ordinal += 1
        _project(evidence, level_index=level_index + 1, parent=node,
                 eligible=members, chain=expected,
                 plan_version_id=plan_version_id, mint_node_id=mint_node_id,
                 handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out,
                 under_built=True, folded_out=folded_out)

    if ordinal == 0:
        # This level said NOTHING about these files -- either it settled no value
        # at all, or none of its values reach this parent's members. Skip it, the
        # way `metadata_only` above is skipped, and let the next level try.
        #
        # It used to fall off the end of the function here, which took every level
        # BENEATH it down as well: the loop was the only thing that recursed, so a
        # level with nothing to say silently truncated the branch. That is the
        # product discarding knowledge it HAS because of knowledge it LACKS --
        # `ap.academic.coursework` resolves school, term, subject, work_type in
        # that order, and a person whose files state a course code and nothing
        # else answers only the third, so their tree came back one folder deep
        # with `PHYS1401` sitting in the evidence unused.
        #
        # `00`:51 is why skipping is the reading that matches the design: the same
        # facts may be organised `Academics/Columbia/2026-Spring/BUSIB 4300` or
        # `Academics/BUSIB 4300/Spring 2026`. The ORDER of levels is not rigid, so
        # a hole in it is a hole and not a floor.
        #
        # Nesting is still by shared files and no level is invented: the children
        # that appear are exactly the ones a later level's own values produce, and
        # they hang off the nearest ancestor that settled something.
        _project(evidence, level_index=level_index + 1, parent=parent,
                 eligible=eligible, chain=chain,
                 plan_version_id=plan_version_id, mint_node_id=mint_node_id,
                 handling_class_for=handling_class_for,
                 template_context_for=template_context_for,
                 protected_movement_permitted=protected_movement_permitted,
                 out=out, members_out=members_out,
                 under_built=under_built, folded_out=folded_out)


def _fold_single_child_runs(nodes: list[Node], members: dict[str, frozenset[str]],
                            folded: list[FoldedLevel],
                            evidence: BranchEvidence) -> list[Node]:
    """`106` Phase 7 §B.2, `00`:98: a run of single children that never divides.

    A node with ONE child holding EVERY one of its files, whose child has one
    such child, and so on to a node with no children, is a chain of folders a
    person opens to find one folder each. The chain folds into its top: the
    top keeps the files and gains the folded values on its own chain, so a
    fact still reaches it (`00`:110). A child holding a strict subset divides
    the parent's files from the rest and is NOT folded -- `WARN_ONE_CHILD`
    is the advice about that one. `00`:78's own path is untouched because
    something divides beneath it. The branch root is never a top: it is not
    in `nodes`, and at the root there is no chain a folded value could be
    reached by.

    Post-order by construction: `nodes` is in creation order, so a top is
    visited before anything beneath it, and a run's members are removed
    before a later node could treat one of them as a top.

    A §B.1 fold said against a node this removes is re-said against the top
    that kept its files, so every fold still names a folder that exists.
    """
    labels = {level.dimension_role: _label_of(level) for level in evidence.levels}
    kids: dict[str | None, list[Node]] = {}
    for node in nodes:
        kids.setdefault(node.parent_node_id, []).append(node)
    removed: set[str] = set()
    top_of: dict[str, str] = {}
    rewritten: dict[str, Node] = {}
    for top in nodes:
        if top.node_id in removed:
            continue
        run: list[Node] = []
        current = top
        while True:
            below = [kid for kid in kids.get(current.node_id, ())
                     if kid.node_id not in removed]
            if len(below) != 1 or members[below[0].node_id] != members[current.node_id]:
                break
            if below[0].dimension is None:
                # A template-local node (Contract W5) is an accepted group of
                # the person's: it carries no value to fold onto the top, so
                # folding it would delete their name from the tree. It stays,
                # and it ends the run for the same reason §B.1 skips it.
                break
            run.append(below[0])
            current = below[0]
        if not run or below:
            continue
        # THE OWNER'S RULING OF 19 SEP: a folder that holds real files is kept
        # even where it is its parent's only child. Asked as "keep a course
        # folder when a term holds one course?", answered yes.
        #
        # THE FLOOR IS `107`'S OWN SENTENCE, not a number picked here: "a single
        # unusual file may remain at the closest meaningful parent rather than
        # creating a one-file leaf". ONE file. A chain whose top holds two or
        # more is a folder with contents and it stays; the one-file leaf `107`
        # names still folds.
        #
        # THIS DOES NOT REOPEN "a folder you open to find one folder" GENERALLY.
        # A level whose values do not divide the corpus is never BUILT (§B.1 and
        # the `ordinal == 0` skip), so a single-child run can only arise where
        # the level divides somewhere else and not under this parent -- a term
        # holding one of several courses, which is the case just ruled on.
        if len(members[top.node_id]) > 1:
            continue
        extra = run[-1].expected_values[len(top.expected_values):]
        folded.extend(FoldedLevel(
            parent_node_id=top.node_id, parent_label=top.display_label,
            dimension_role=node.dimension_role or "",
            label=labels.get(node.dimension_role, node.dimension_role or ""),
            values=(node.display_label,), file_count=len(members[top.node_id]),
            reason=FOLDED_ONE_FOR_ALL) for node in run)
        rewritten[top.node_id] = dataclasses.replace(
            top, expected_values=top.expected_values + extra)
        for node in run:
            removed.add(node.node_id)
            top_of[node.node_id] = top.node_id
            members.pop(node.node_id, None)
    for index, fold in enumerate(folded):
        if fold.parent_node_id in top_of:
            top = rewritten[top_of[fold.parent_node_id]]
            folded[index] = dataclasses.replace(
                fold, parent_node_id=top.node_id, parent_label=top.display_label)
    return [rewritten.get(node.node_id, node) for node in nodes
            if node.node_id not in removed]


#: A value that is a whole calendar day, and a value that is a whole month. Both
#: are matched WHOLE and strictly: `2026-Spring` is a term and not a month, and a
#: level of terms must not be read as a level of dates.
_DAY = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_MONTH = re.compile(r"^(\d{4})-(\d{2})$")

#: day -> month -> year. Each step is a PREFIX of the value the fact already
#: carries, so no label is invented: `2026-03-14` really does record 2026.
#: Each step drops the last hyphen-separated component, which is a PREFIX of the
#: value the fact already carries: `2026-03-14` really does record `2026-03`, and
#: `2026-03` really does record `2026`. No label is invented and no file moves
#: out of the branch — it lands in a coarser folder, which is the only narrowing
#: that costs the user nothing.
_COARSER: tuple[tuple[object, object], ...] = (
    (_DAY, lambda value: value.rsplit("-", 1)[0]),
    (_MONTH, lambda value: value.rsplit("-", 1)[0]),
)


def _coarsen(level: LevelEvidence, key_of) -> LevelEvidence:
    members: dict[str, frozenset[str]] = {}
    classes: dict[str, frozenset[str]] = {}
    for value, files in level.members_by_value.items():
        key = key_of(value)
        members[key] = members.get(key, frozenset()) | files
        classes[key] = (classes.get(key, frozenset())
                        | level.handling_classes_by_value.get(value, frozenset()))
    return dataclasses.replace(
        level,
        display_labels={key: key for key in members},
        members_by_value=members,
        handling_classes_by_value=classes,
    )


def narrow_wide_date_levels(
    evidence: BranchEvidence, *, max_folders: int,
) -> BranchEvidence:
    """Coarsen a date level that would otherwise propose a folder per day.

    NOTHING BOUNDED HOW WIDE A SPLIT WAS. §8.6's ceiling is called "Maximum
    folder proposals and maximum depth"; P10 read it as how many OPTIONS to offer
    and how DEEP one may go, and never as how many FOLDERS a proposal creates —
    which is the reading its own words most plainly carry. A capture-date split
    on a real photo library proposed 337 folders with that ceiling set to six,
    and `00`:88 recommends exactly that split: "Photos and capture-based media
    are the major exception: time often belongs first."

    A CEILING IS THE WRONG INSTRUMENT ANYWAY, and this is why only dates are
    touched. Capping a level of 400 courses at 100 folders means either dropping
    300 courses, which is the silent omission the standing rule forbids, or
    merging them by something the evidence never said, which is invention. There
    is no third option for values with no structure, so a level of opaque values
    passes through at whatever width its evidence produced. A DATE has structure
    the fact already carries: `00`:88's own Photos template "may define year →
    event", and every file keeps a folder — a coarser one, named by a prefix of
    the value P6 settled, with nothing dropped and nothing invented.
    """
    if max_folders < 1:
        return evidence
    levels = []
    changed = False
    for level in evidence.levels:
        current = level
        for pattern, key_of in _COARSER:
            values = tuple(current.members_by_value)
            if len(values) <= max_folders:
                break
            if not values or not all(pattern.match(value) for value in values):
                continue
            coarser = _coarsen(current, key_of)
            if len(coarser.members_by_value) < len(current.members_by_value):
                current = coarser
                changed = True
        levels.append(current)
    if not changed:
        return evidence
    return dataclasses.replace(evidence, levels=tuple(levels))

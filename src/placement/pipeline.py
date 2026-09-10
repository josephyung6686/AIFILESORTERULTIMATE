"""§6.12's nine steps, in §6.12's order, and §7's separate stage after them.

The design's own list (`planning/01-product-design-structured.md:1295-1306`) is the
spine, and `STEPS` names it so the shape is checkable against the design rather
than against this file. Steps 1 and 2 belong to P10 and step 8 to P8; this module
orchestrates 3 through 7 and produces 9.

Every injection arrives on `PipelineInputs` and none has a default. A run with no
model injections is a legal run -- §6.6 decides a unique direct match with zero
model calls -- and a run with no support policy is not, because §6.10's thresholds
are unsettled by the design and guessing one would place files under a bar nobody
chose.

The order inside `place_file` is not arbitrary. §8.4's privacy gate is consulted
before any dossier could be assembled, and §8.7's learning store is consulted
before `place` is emitted. Both are preconditions rather than filters, and moving
either later would make a spend or a placement happen first.

**Three questions P11 cannot answer from a `P8Verdict` are injected**, and each
one is injected because the verdict carries a `claim_ref` and not the answer:

* `chosen_node_of` -- which of P11's candidates a Site C verdict chose;
* `residual_action_of` -- which of §7.7's eight actions a Site D verdict carried,
  and its target. P8 validates `payload["action"]` against `RESIDUAL_ACTIONS`
  (`placement_validation.py:311-312`) but the verdict's own `disposition` is
  P8's coarser vocabulary: `residual_destination` cannot say whether the model
  chose a residual destination or a broad parent, and `return_to_placement`
  cannot say whether it named a confirmed group or an accepted packet -- which is
  exactly what `ReturnTarget.kind` has to record. The caller holds the response
  and hands back the pair;
* `sensitivity_policy` -- P7's answer about this release.

**P11 never calls `record_cd_verdict`.** `harness.py:245-253` calls it for every C
and D verdict and `placement_validation.py:614` does the same on revalidation; a
second call would write the row twice. What P11 owes is the input that call needs
-- `DossierRequest.evidence_snapshot_id`, which `run_call` refuses a C or D
request without BEFORE the spend -- and `_judge_with_model` mints it.
"""
from __future__ import annotations

import dataclasses
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType

from database_agent.supersede import mark_superseded
from llm_harness import P8Verdict, Refusal
from llm_harness.vocabulary import ABSTAIN as P8_ABSTAIN
from llm_harness.records import (
    REFUSAL_EXCEPTIONS, CallFailed, CallRefused, DossierRequest, EvidenceItem,
    # `104` R-149 reads P7's raise, and reads it THROUGH THE RECORDS MODULE.
    # `tests/p11/test_p11_connections.py` pins the whole of P11's `privacy` import
    # surface to two files, neither of them this one, and `REFUSAL_EXCEPTIONS` is
    # re-exported one line below for that same reason: "the records module is the
    # surface every one of them already reads".
    MalformedRequest,
    PreCallAbstention,
    ValidationUnavailable,
)
from llm_harness.store import record_unbuilt_call_abstention, refusal_outcome
from llm_harness.vocabulary import (
    C_PLACEMENT, CHOOSE_RESIDUAL_DESTINATION, NOT_ELIGIBLE_FOR_MODEL,
    CONTEXT_SUPPORTED as P8_CONTEXT_SUPPORTED, D_RESIDUAL,
    DIRECT_ANCHOR as P8_DIRECT_ANCHOR, REJECT as P8_REJECT,
    SEVERAL_LEGAL_NODES_PLAUSIBLE, USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW,
)

from grouping.vocabulary import NOT_FLAGGED

from placement import events as placement_events
from placement.config import PlacementLimits, SupportPolicy, require_policy
from placement.graph import EDGE_PRODUCER, build_node_local_graph, is_typed_support
from placement.groups import (
    AcceptedGroup, ExcludedOutlier, GroupPlan, accepted_group_as_of,
    confirm_shared_parent, excluded_outlier_for, resolve_multi_home,
)
from placement.index import (
    entries_for_plan, entry_for, legal_node_ids, node_profile, sibling_counts,
)
from placement.learning import basis_key_for, suppressed_nodes
from placement.p8_seam import (
    ACCEPTED_GROUP_ITEM, BRANCH_ITEM, CANDIDATE_ITEM, GRAPH_EDGE_ITEM,
    RESIDUAL_AREA_ITEM,
    # `104` §18.15: the driver for one call and the driver for many, taken
    # from P11's own seam onto P8 rather than from P8 directly. The lane is
    # P8's mechanism -- what it holds open is P8's round trip -- and this
    # package reaches that mechanism through one module.
    CallLane, drive_inline, in_walk_order,
    call_placement_steps, evidence_snapshot_id_for, placement_authorities,
    residual_authorities, site_dependencies, snapshot_observation_keys,
    to_p8_conflicts, transcribe,
)
from placement.privacy import (
    LOCAL, automatic_move_permitted_for, is_unclassified, may_assemble_dossier,
    privacy_state_for, review_policy_for,
)
from placement.records import (
    Ask, DecisionDepth, Destination, GroupSupport, PlacementDecision,
    ResidualContext, ReturnTarget, Subject, TwoCondition,
)
from placement.residual import (
    ACTION_OUTCOME, ResidualSet, ResidualSetDecision, SetDecisionRequired,
    check_return_cycle, link_return, model_calls_permitted, outcome_for_action,
    record_set_decision, require_model_call_permitted, require_set_actionable,
    require_set_decision, surface_residual_sets,
)
from placement.retrieval import (
    CURATED_FOLDER, GRAPH_RELATIONSHIP, NON_DECIDING_CHANNELS, Candidate,
    Retrieval, SetAside, retrieve,
)
from placement.scoring import assess, needs_model_call, score_candidates
from placement.stage_output import emit_retrieval_stage, emit_scoring_stage
from placement.store import current_decision, record_decision, subject_ref_of
from placement.vocabulary import (
    ABSTAIN, ABSTAIN_NO_SUPPORTED_DESTINATION, ASK_USER,
    BLOCKED_PENDING_USER, BUDGET_DEFERRED,
    CONFLICTING_FACTS, CONTEXT_SUPPORTED, CONTEXT_SUPPORTED_GROUP_MATCH,
    DECIDED_BY_MODEL, DECIDED_BY_RULE, DECIDED_BY_USER, DIRECT,
    EXISTING, FILE, GENERIC_HUB_ONLY, GROUP, LOW_MARGIN,
    MARGIN_TRUE_VACUOUS, MARK_STATE, NO_SHARED_BRANCH, SEMANTIC_ONLY,
    MULTIPLE_SUPPORTED_HOMES, NO_SUPPORTED_DESTINATION, PLACE, PLACEMENT,
    POSSIBLE, PRIVACY_BLOCKED, RESIDUAL, RESIDUAL_ROLE, REVIEW_WITH_MODEL,
    RETURN_TO_PLACEMENT, SEND_TO_APPROVED_NODE, SHARED_MATERIAL,
    SHARED_MATERIAL_DECISION, USER_CHOSE_DESTINATION, USER_CONFIRMED, WEAK,
)

#: §6.12's nine, in §6.12's order. Steps 1-2 are P10's and step 8 is P8's; naming
#: them anyway is what makes the pipeline auditable against the design.
STEPS: tuple[str, ...] = (
    "freeze_approved_tree",                     # 1, P10
    "profile_each_node",                        # 2, P10
    "retrieve_legal_candidates",                # 3
    "build_local_graph",                        # 4
    "suppress_impossible_nodes",                # 5
    "identify_child_parent_fallback_or_none",   # 6
    "judge_bounded_ambiguity",                  # 7
    "validate_evidence_and_constraints",        # 8, P8
    "reviewable_plan_of_placements",            # 9
)


#: WHAT EACH STEP-6 RULE SAYS ABOUT A FOLDER IT RANKED BELOW THE CONTENDERS.
#:
#: `104` §18.2 gap 2. Every one of these used to be a DELETION and is now a
#: sentence the model reads inside the folder's own description. They are written
#: for the person's model rather than for the log: no section numbers, no engine
#: words, and no instruction -- each says what the engine noticed and stops,
#: because the sentence that told the model what to conclude would be the deletion
#: again in a longer form.
#:
#: **They decide nothing and they are not a word list.** No branch anywhere reads
#: these strings; `SetAside.because` carries whichever one the rule that set the
#: candidate aside wrote, and the only thing that ever happens to it is that
#: `_offered_items` appends it to that candidate's `location` and `_explain`
#: repeats it to the person if the model picks the folder anyway.
_RANKED_BELOW_ANCESTOR: str = (
    "the engine ranked this folder below another: a folder further down this same "
    "chain is also on this list, and a file filed in the deeper one is filed in "
    "this one too"
)
_RANKED_BELOW_VAGUER_COPY: str = (
    "the engine ranked this folder below another: it is a folder this run would "
    "create, and a folder the person already made expects everything it expects"
)
#: NO CLAUSE ABOUT CARRYING THE FILE OUT OF WHERE IT IS, though the rule that
#: writes this is named for exactly that. `_without_kind_only_moves` reads the
#: stay off `CURATED_FOLDER`, which is a LABEL match -- so a folder whose name
#: does not agree with the file, reached on `DIRECT_FACT` alone, is the file's own
#: folder and the channel is silent about it. That is the `Kid` shape
#: `_a_folder_made_for_this_keeps_it` records from the other side ("a first draft
#: of this rule, reading the channel, dropped the file's own folder along with the
#: rivals"). As a deletion the mistake cost the candidate; as a SENTENCE it would
#: be a false statement in front of the model, which is worse. What the rule
#: actually measured is the agreement, and that is all this says.
_RANKED_BELOW_KIND_ONLY: str = (
    "the engine ranked this folder below the others: everything it agrees with "
    "this file about is what kind of thing the file is, or when it was made"
)
_RANKED_BELOW_COVERED_FOLDER: str = (
    "the engine ranked this folder below the others: the folder this file is in "
    "now was made for what it holds -- every file in it agrees about something -- "
    "and this folder's only agreement with the file is what kind of thing it is, "
    "or when it was made"
)


def _ranked_below(retrieval: Retrieval, node_ids, because: str) -> Retrieval:
    """Move these candidates off the contender list and onto the shortlist's tail.

    `104` §18.2 gap 2's whole mechanism, in one function so that the four rules
    below share it and none of them can drop a candidate on the floor by writing
    the `dataclasses.replace` slightly differently.

    `dataclasses.replace`, not a field-by-field rebuild. Every one of these rules
    changes exactly TWO fields and copies the rest by name, and a rebuild that
    names them silently RESETS any field added later. For `producible_channels`
    that would mean a ranked retrieval scored against a denominator that is not
    the one that built it, which is `104` §18.2 gap 13 re-opened one function
    further down.
    """
    if not node_ids:
        return retrieval
    moved = tuple(candidate for candidate in retrieval.candidates
                  if candidate.node_id in node_ids)
    return dataclasses.replace(
        retrieval,
        candidates=tuple(candidate for candidate in retrieval.candidates
                         if candidate.node_id not in node_ids),
        set_aside=retrieval.set_aside + tuple(
            SetAside(candidate=candidate, because=because) for candidate in moved),
    )


def _ranked_set_aside(retrieval: Retrieval, graphs, *, policy) -> tuple[SetAside, ...]:
    """The set-aside tail of the shortlist, in the SCORES' own order.

    `00`'s amendment says deterministic scores RANK and shortlist. The contenders
    are ranked by `assess`; this is the same arithmetic asked of the folders the
    step-6 rules moved off the contender list, so "ranked below" is a ranking and
    not an insertion order that happened to fall out of the order four rules ran
    in.

    **It is offer-only and never reaches `assess`.** The `Retrieval` built here is
    a scratch record whose `candidates` are the set-aside ones; nothing keeps it,
    nothing scores a contender against it, and `producible_channels` is copied so
    the tail is scored against the same denominator the contenders were
    (`104` §18.2 gap 13).

    The order is invisible to the model -- the prompt says "the order of the items
    carries no meaning" -- and that is not a reason to leave it arbitrary: it
    decides `offered[0]`, which is the `basis_key` a past rejection is filed
    against, and on a file whose every candidate was set aside it is the only
    ranking there is.
    """
    if not retrieval.set_aside:
        return ()
    by_id = {item.candidate.node_id: item for item in retrieval.set_aside}
    scored = score_candidates(
        dataclasses.replace(
            retrieval,
            candidates=tuple(item.candidate for item in retrieval.set_aside),
            set_aside=()),
        graphs, policy=policy)
    return tuple(by_id[item.node_id] for item in scored)


def _without_superseded_ancestors(conn: sqlite3.Connection, retrieval: Retrieval,
                                  *, plan_version: str) -> Retrieval:
    """Step 6's first half: an ANCESTOR of another candidate is not a rival.

    A nested tree means a file's facts match its whole chain. Given
    `Coursework/Columbia/PHYS1401/Homework`, a file settling school, subject and
    work_type matches all three folders, and P11 scored them as competitors: they
    tied at 0.714 apiece, `assess` returned `multiple_supported_homes`, and the
    tie went to a model that offline mode forbids -- so the file abstained
    `privacy_blocked`. Four personas, four one-folder trees, nothing ever filed.

    They are not multiple homes. Filing something in `Columbia/PHYS1401/Homework`
    files it in `Columbia` and in `PHYS1401` too; that is what nesting MEANS, and
    §6.7 asks for the deepest node the evidence actually supports. So a candidate
    that is a strict ancestor of another candidate stops being a CONTENDER -- not
    judged, not rejected, superseded by a more specific form of itself.

    **AND IT IS STILL OFFERED, WHICH IS `104` §18.2 GAP 11'S FIRST HALF.** Until
    this it was deleted, and the shallower approved parent then could not be
    chosen by anybody: `00`:111 asks for exactly that choice -- "if the system
    cannot distinguish Spring 2025 from Spring 2026 but a parent path such as
    `Academics/Columbia/PHYS1401/Homework` exists, the model should choose the
    approved shallower path" -- and the prompt invites it in as many words
    ("A candidate with an unfilled level is struck; if a shallower candidate on
    the same chain has all its levels supported, that shallower one stands",
    `c_placement_template.eliminate-v2.txt`:43). The menu could not contain the
    option the text offered. The deepest candidate is supported BY CONSTRUCTION
    only in the sense that its expected values matched SOME fact; whether every
    level of it is supported is the model's question, and the parent has to be on
    the list for its answer to be reachable. So the ancestor is ranked below and
    described, and the sentence it carries says what the ranking means.

    **Only strict ancestors, and only within one chain.** Two candidates on
    different branches are genuinely two homes and stay two homes: that is the
    §6.10 ambiguity the model call exists for, and collapsing it would be P11
    picking an institution for the user, which `00` forbids in as many words.

    **The broad-parent case survives.** A node is a candidate only because its
    expected values matched, so the deepest surviving candidate is supported by
    construction. Where the tree stops shallower than the evidence reaches, the
    parent IS the deepest candidate and is what this returns -- which is the case
    `DecisionDepth.unsupported_levels` was written for.
    """
    node_ids = {candidate.node_id for candidate in retrieval.candidates}
    if len(node_ids) < 2:
        return retrieval

    superseded: set[str] = set()
    for node_id in node_ids:
        cursor = entry_for(conn, plan_version=plan_version,
                           node_id=node_id).parent_node_id
        # Walk to the root marking every ancestor that is ALSO a candidate. A
        # cycle cannot occur -- `build_destination_index` refuses a node whose
        # parent the frozen tree does not contain -- and the walk is bounded by
        # the tree's depth, which §7.2 caps.
        while cursor is not None:
            if cursor in node_ids:
                superseded.add(cursor)
            cursor = entry_for(conn, plan_version=plan_version,
                               node_id=cursor).parent_node_id
    return _ranked_below(retrieval, superseded, _RANKED_BELOW_ANCESTOR)


def _without_duplicated_proposals(conn: sqlite3.Connection, retrieval: Retrieval,
                                  *, plan_version: str) -> Retrieval:
    """Step 6's second half: a vaguer COPY of the person's folder is not a rival.

    `00`:100 says a folder the person made "should be treated as a strong
    expression of user intent". Once those folders are adopted, the engine's own
    proposal for the same material stands beside them -- `Uni/CHEM1500` and
    `Coursework/CHEM1500`, the same name twice on one screen -- and the two tie at
    every file. §6.10 sends a tie to a model, offline mode forbids the call, and
    the file abstains `privacy_blocked`. Measured: six files that had been placing
    fine went back to abstaining the day folders were adopted.

    This is not P11 picking between two homes. The rule is the ancestor rule's
    own -- superseded by a more specific form of itself -- and the specificity is
    measured, not assumed: the proposal is dropped only when the person's folder
    expects EVERYTHING it expects. `Uni/CHEM1500`'s files agree on the term as
    well as the subject, so it is strictly the better-supported destination, and
    the proposal is a vaguer copy of a folder that already exists.

    **Three refusals hold the rule to that.**

    * A proposal expecting NOTHING is never dropped. An empty set is a subset of
      everything, so without this any adopted folder would supersede every
      unexpectant proposal in the tree -- the person's `Downloads` swallowing a
      branch it has no relationship with.
    * The person's folder must expect a SUPERSET, not merely overlap. Two folders
      that share one field and differ on another are genuinely two homes, and
      §6.10's ambiguity is what the model call exists for.
    * Only a PROPOSAL is set aside. Two of the person's own folders competing is
      their business, and resolving it here would be the product overruling one
      of their decisions with another.

    **`104` §18.2 gap 2: THIS RANKS, IT NO LONGER DELETES.** The vaguer copy stays
    on the shortlist below the person's own folder, carrying
    `_RANKED_BELOW_VAGUER_COPY`, because "a folder this run would create" is a
    judgement about which of two names for one place a person would rather see,
    and `00`'s amendment gives that judgement to the model.
    """
    entries = {candidate.node_id: entry_for(conn, plan_version=plan_version,
                                            node_id=candidate.node_id)
               for candidate in retrieval.candidates}
    if len(entries) < 2:
        return retrieval

    adopted = [entry for entry in entries.values()
               if entry.node_type == EXISTING]
    if not adopted:
        return retrieval

    superseded = {
        node_id for node_id, entry in entries.items()
        if entry.node_type != EXISTING and entry.expected_values
        and any(set(entry.expected_values) <= set(folder.expected_values)
                for folder in adopted)}
    return _ranked_below(retrieval, superseded, _RANKED_BELOW_VAGUER_COPY)


def _refinements_of(their_own_folder: str | None,
                    parent_of: Mapping[str, str | None],
                    node_ids) -> frozenset[str]:
    """Which of these nodes lie INSIDE the folder the file is already in.

    A move into one of them is refinement -- the file goes deeper inside the
    branch it already sits in -- and `00`'s amendment of line 22 makes that the
    model's call. A move to anything else is removal from the person's existing
    arrangement, which stays a constraint surfaced to them (`104` §13.8).

    STRICT descendants. The folder itself is not a refinement of itself: staying
    put is the status quo, which is what `_staying_put_wins_a_tie` is about, and
    counting it here would make that rule's tie unreachable.

    Empty when the caller named no folder for this file, which is every file that
    is not in one of the person's own folders and every caller that does not
    supply the mapping. The walk is bounded by the chain it is walking and cannot
    loop: `seen` stops a parent cycle, which P10 does not build but which this
    function must not hang on if it ever did.
    """
    if their_own_folder is None:
        return frozenset()
    inside: set[str] = set()
    for node_id in node_ids:
        seen: set[str] = set()
        walker = parent_of.get(node_id)
        while walker is not None and walker not in seen:
            if walker == their_own_folder:
                inside.add(node_id)
                break
            seen.add(walker)
            walker = parent_of.get(walker)
    return frozenset(inside)


def _without_kind_only_moves(
        retrieval: Retrieval, *, dimension_of: Mapping[str, str | None],
        fields_that_cannot_anchor_a_move: frozenset[str],
        refinements: frozenset[str] = frozenset()) -> Retrieval:
    """Step 6's third half: AN ARTIFACT KIND IS NOT AN IDENTITY.

    "This is an exam" says WHAT a file is. It never says whose it is, or which
    body of work it belongs to, and every exam anybody has ever written matches
    it. A destination reached on that agreement ALONE is not a destination the
    evidence chose; it is the first folder in the tree that happened to hold the
    same kind of thing.

    MEASURED, ON THE OWNER'S OWN 199 FILES, 2026-09-05. Six university physics
    papers -- two copies of `1403.Exam.1.Equations`, three `1403.Sample.Exam`
    files and an exam seating chart -- were placed into `Desktop/AP world`, a
    high-school history folder, with `support 0.71 against a threshold of 0.50`
    and no review required. `work_type = exam` was the whole of both sides:
    the papers state nothing else, and the folder's ONLY expectation is that one
    word, because its own files all agree on it, so P10 built no child and
    recorded the expectation on the folder itself (`materialise._project`'s
    `stated`). A seventh file went the same way on `term = Fall2024` alone.

    THIS IS THE REPORT CARD READ ONE FIELD OVER.
    `test_a_childs_report_card_is_not_filed_into_the_law_school_semester` is the
    same shape on `cycle_period`: "the anchoring field is absent and the file is
    placed on the period alone, which is 'absent means refuse, never guess' read
    the other way round". `artifact_kind` is the second role that can say only
    what-or-when, and the library's own role vocabulary is where the two are
    named. WHICH fields play those roles is the composition root's to say and is
    injected; a set chosen here would be this package holding an opinion about a
    catalogue it does not own.

    **A STAY IS NOT A MOVE, AND THAT IS THE WHOLE OF THE DISCRIMINATION.**
    `AP world`'s own practice exam is already in `AP world`. Nothing is carried
    anywhere, the artifact kind is the person's OWN filing rather than a guess
    about it, and the plan still has to say the file belongs where it sits --
    otherwise this rule buys the misfiling back with silence, which is the
    failure `_staying_put_wins_a_tie` records from the other side ("the product
    stopped placing ANYTHING rather than place the wrong thing"). The stay is
    read off `CURATED_FOLDER`, the same channel `Scored.already_there` reads and
    for the same reason: the file is IN that folder right now.

    **Only a candidate the FACTS carried.** A candidate with no matching fact at
    all is not this case -- it reached the file through a group or a relationship,
    which §6.5 already judges -- and dropping it here would be this rule
    answering a question nobody asked it.

    **AND ONLY A FOLDER THAT IS SOMETHING ELSE. `dimension_of` IS THE WHOLE OF
    THAT TEST AND THE RULE IS WRONG WITHOUT IT.** P10 builds `PHYS 1401/syllabus`
    as the `work_type` LEVEL of a branch: the folder's own dimension IS the field,
    the folder means "the syllabus one", and a file matching `work_type =
    syllabus` matches what that folder is FOR. Refusing it took
    `tests/integration/test_cli_agreeing_corpus.py` from three files filed to
    three abstentions -- the easiest corpus there is, placing nothing -- which is
    the over-refusal this package has now met three times.

    `Desktop/AP world` is the other shape and carries no dimension at all. Its
    `work_type = exam` was ABSORBED onto it by `materialise._project`'s `stated`,
    because the level did not divide and there was no child to put it on. The
    folder still means "AP World History"; the expectation is only what its files
    happened to have in common. So: a folder may claim a file on what-kind-or-when
    alone exactly when THAT IS WHAT THE FOLDER IS, and never when it is something
    else that merely holds some.

    Read from P10's own `Node.dimension` through the caller's tree, the same
    object `their_own_folder_node_ids` is read from, so the two halves of this
    step see one tree and not two.

    **AND A MOVE INSIDE THE FILE'S OWN FOLDER IS NOT A MOVE OUT OF IT.** This
    rule is named for what it refuses -- carrying a file OUT of where it is on an
    artifact kind alone -- and until `refinements` existed it could not tell that
    from putting the file one level DEEPER in the same folder. `00`'s amendment of
    line 22 splits them: refinement, moving a file deeper inside the branch it
    already sits in, is allowed and is the model's call; removal, moving it out of
    the person's existing arrangement, stays the constraint this rule is
    (`104` §13.8, ruled by the owner 2026-09-05).

    The exemption is narrow on purpose, and `Desktop/AP world` is why. Its six
    physics papers are the measurement above, and `AP world` IS one of the
    person's own folders -- so "a descendant of any folder they have" would
    readmit every one of them through the child the exemption opens. What is
    exempt is a descendant of the folder THIS FILE IS IN, which `AP world` is not
    for a paper sitting on the Desktop. `_refinements_of` is the whole of that
    test and the caller supplies the folder.

    **`104` §18.2 gap 2: THIS RANKS, IT NO LONGER DELETES.** `Desktop/AP world`
    stays on the shortlist under `_RANKED_BELOW_KIND_ONLY`, and the six physics
    papers are still safe: the sentence tells the model that the folder's only
    agreement with the file is a kind or a period, the model has the folder's own
    profile beside it, and if it places the file there anyway the placement
    carries `requires_review` and the sentence into the plan the person reads
    (`_place_one`, `_explain`). What is gone is the case this rule could never
    tell from those six -- a folder whose kind-only agreement IS the right answer,
    which under a deletion had no way to be said at all.
    """
    carried = {
        candidate.node_id for candidate in retrieval.candidates
        if CURATED_FOLDER not in candidate.channels
        and candidate.node_id not in refinements
        and candidate.matching_facts
        and all(fact.field in fields_that_cannot_anchor_a_move
                for fact in candidate.matching_facts)
        and dimension_of.get(candidate.node_id) not in {
            fact.field for fact in candidate.matching_facts}}
    return _ranked_below(retrieval, carried, _RANKED_BELOW_KIND_ONLY)


def _a_folder_made_for_this_keeps_it(
        retrieval: Retrieval, *, its_own_folder: str | None,
        fields_that_cannot_anchor_a_move: frozenset[str]) -> Retrieval:
    """Step 6's fourth half: COVERAGE, NOT CURATION.

    `_without_kind_only_moves` above lets a folder claim a file on what-kind-or-
    when alone exactly when THAT IS WHAT THE FOLDER IS -- a `work_type` LEVEL
    means "the syllabus one", and refusing it placed nothing on the easiest
    corpus there is. This is the other side of that permission: the level is
    entitled to the file only if nobody else already has a better claim on it,
    and the person's own filing is that claim.

    THE FILE THIS EXISTS FOR, MEASURED 2026-09-05 ON A CORPUS SMALL ENOUGH TO
    READ. A part-time law student who is also a parent. Her child's report card
    sits in `Kid`; the run proposes `Coursework/Fall2026/report card`, a
    `work_type` level, and the file states `work_type = report card` and `term =
    Fall2026` and NOTHING about whose work it is. Every guard above allows it,
    and the product offers to put a child's school record in the parent's
    Contracts folder -- the one defect this product exists to not have.

    TWO EARLIER DISCRIMINATIONS WERE BUILT AND MEASURED AND BOTH WERE WRONG, and
    they are recorded because each is a rule somebody will propose again:

    * "Refuse a move when the file states no anchoring fact." It equally refuses
      the nine résumés into `Coursework/Spring2023/resume`, measured exact at 9
      of 9. A résumé states a kind and a period and nothing about whose work it
      is: it has the SAME evidence shape as the report card, and no rule reading
      only the file can tell them apart.
    * "Refuse a move out of a folder the person made that holds files like it."
      `Desktop` holds four résumés directly, so the product's own evidence
      describes `Desktop` as a folder its owner made which holds files like the
      file. Four of the nine exact placements went back to abstaining.

    WHAT SEPARATES THEM IS COVERAGE. `Kid` holds two files and BOTH are report
    cards. `Desktop` holds résumés among a great many other things. A folder
    whose every file is one kind was made for that kind; a folder where one kind
    wins a plurality is a place things land. Five of the nine résumés sit alone
    in a folder of their own, and the floor inside
    `settled_values_stated_by_every_file` -- a set of one is always unanimous --
    already refuses to call those made for anything, so the rule does not reach
    them either.

    **IT IS NOT A FIELD MATCH, AND THAT IS DELIBERATE.** What the folder was made
    for need not be what the rival matched on. The law student's own `Fall 2026`
    holds three files that all state that term, and the rival that claims one of
    them is a `syllabus` level -- a different field entirely. A folder every one
    of whose files agrees about something is a folder somebody built, and a file
    is not carried out of it on what-kind-or-when alone whatever the coincidence
    is. WHICH files are in such a folder is the composition root's to say and is
    injected, for the same reason `fields_that_cannot_anchor_a_move` is: the band
    beneath "every file" is a number P11 does not own.

    **A CHILD IS NOT AN ESCAPE AND DOES NOT NEED TO BE ONE.** A level built on
    the field the folder is covered by cannot exist -- a value every file states
    does not divide, so §5.4 measures it and builds nothing -- and a level built
    on any other field is a rival like any other. `Desktop/Python 1006` states
    `lecture` five times in twenty-one files and is covered by nothing, so this
    rule does not touch its files at all.

    **WHAT IT DOES TODAY, STATED PLAINLY.** Measured on the owner's 199 files on
    2026-09-05: NO folder in either the `academic.coursework` or the
    `career.recruiting` run is covered by anything -- 0 of 29 directories -- so
    this rule fires on none of them and both scorecards are unchanged by it. The
    rival it drops in the law-school corpus is one `_staying_put_wins_a_tie`
    also holds today. The report card escapes, `Fall 2026/syllabus` exists to
    claim a file, and every guard above allows the move ONLY under the contract
    change recorded in `test_cli.py`'s xfail on
    `test_the_lectures_get_a_folder_of_their_own_inside_the_folder_they_are_in`
    -- which was built, measured on the full corpus and reverted. This rule is
    the discrimination that change needs, kept so it can be retried without
    re-opening the defect, and `test_a_kind_that_merely_leads_is_an_expectation_
    but_not_what_a_folder_is_for` is what pins it in the meantime.

    **THE FOLDER IS NAMED, NOT INFERRED FROM `CURATED_FOLDER`.** The rule above
    reads the stay off that channel, and it is the wrong instrument here: the
    channel is a LABEL match (`retrieval.label_matches`), so it fires for a
    folder whose NAME agrees with the file and is silent for one whose name does
    not. `Kid` is called "Kid" and a report card says nothing about a kid, so the
    folder the file is actually sitting in reached it on `DIRECT_FACT` alone --
    and a first draft of this rule, reading the channel, dropped the file's own
    folder along with the rivals and abstained on all five files. The caller
    names the node instead.

    Nothing is set aside when the file's own folder was made for nothing, which is
    every file in a folder that is merely a place things land, and every file
    that is not in one of the person's folders at all.

    **`104` §18.2 gap 2: THIS RANKS, IT NO LONGER DELETES.** The rival stays on
    the shortlist under `_RANKED_BELOW_COVERED_FOLDER`. The report card is still
    safe for the reason it always was -- the sentence names the coverage the rule
    measured, and a model that carries the child's school record into the law
    student's `Coursework/Fall2026/report card` anyway does it in front of a
    person, with the reason printed beside it -- and the discrimination this rule
    exists to keep alive for the xfail'd contract change is measured exactly as
    before, because `assess` never sees what this sets aside.
    """
    if its_own_folder is None:
        return retrieval
    carried = {
        candidate.node_id for candidate in retrieval.candidates
        if candidate.node_id != its_own_folder
        and candidate.matching_facts
        and all(fact.field in fields_that_cannot_anchor_a_move
                for fact in candidate.matching_facts)}
    return _ranked_below(retrieval, carried, _RANKED_BELOW_COVERED_FOLDER)


class ModelJudgementUnavailable(RuntimeError):
    """`run_call` came back with something that is not a verdict.

    P8 declares five return types and only one of them is a judgement.
    `Refusal` is P7 denying the release, which IS §8.4's `privacy_blocked` and is
    recorded as that. `ValidationUnavailable` and `CallFailed` are not judgements
    about evidence, and §6.10's abstention reasons are a closed set with no member
    for "the call did not happen"; since `104` R-173 (9 Sep 2026) neither names
    one -- the file falls through to §13.5's no-model fallback with the failure
    recorded as its own event, and the run goes on. `NeedsConsent` alone reaches
    this: it is the gate asking the person a question, and B2 says it writes no
    P11 decision and no P2 row, so this raises and the caller decides.
    """


class ResidualActionUnavailable(RuntimeError):
    """A Site D verdict arrived with no way to recover §7.7's action."""


class ResidualPromptRequired(RuntimeError):
    """A residual set asked for a model and this deployment wired D no text.

    NEVER site C's. C's response schema has no `action` key and its shaping policy
    describes a different question, so a residual answer sent under it is rejected
    for obeying an instruction that was not its own.
    """


class ScanBudgetRequired(RuntimeError):
    """A model call was about to be made with no scan to charge it to.

    §8.6's two spend ceilings are per SCAN -- calls per thousand files, cost per
    scan -- so they need the scan's identity and its file count, which belong to
    the scan and not to P11. P11 supplies the ceilings; the caller supplies what
    they are ceilings ON. Absent, `run_call` would reserve against nothing and
    the run would spend without a bound, which is the state §8.6 exists to make
    impossible.
    """


@dataclass(frozen=True)
class P2Run:
    """P2's three coordinates for one measured run, or nothing at all.

    They travel together because `emit_scoring_stage` needs all three and a
    partial injection would silently emit no row -- a run that looks measured and
    is not. `eval_harness` measures replays, shadows and adversarial runs, so an
    ordinary run supplies no `P2Run` and writes no stage output; that is a state,
    not a gap.
    """

    run_id: str
    version_tuple_ref: str
    upstream_stage_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("run_id", "version_tuple_ref"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} is required on a P2Run; half an injection emits no "
                    "row at all and makes an unmeasured run look measured"
                )
        object.__setattr__(self, "upstream_stage_refs",
                           tuple(self.upstream_stage_refs))


@dataclass(frozen=True)
class PipelineInputs:
    plan_version: str
    tree: object
    policy: SupportPolicy
    limits: PlacementLimits
    partition: object
    ask_or_abstain: object
    max_return_cycles: int | None
    gate: object
    model_client: object
    #: SITE C's prompt. `prompt_for` is what reads it, and `residual_prompt` below
    #: is site D's -- two sites, two texts, two response schemas, two shaping
    #: policies, and `_judge_with_model` picks by call site.
    prompt: object
    #: SITE D's prompt, or `None` for a deployment that wired C and not D. Required
    #: with no default, exactly as `residual_action_of` is: a field gaining one here
    #: would be P11 answering a question the composition root owns.
    residual_prompt: object
    call_dependencies: object
    model_call_request: object
    chosen_node_of: object
    residual_action_of: object
    sensitivity_policy: object
    #: WHICH MODEL WOULD BE ASKED -- P7's `ModelTarget`, or `None` when no model
    #: is configured. `104` R-118: §8.4's gate has to know the target's locality
    #: BEFORE a dossier exists, because a file the mode keeps off the cloud may
    #: still be given to a local model, and until this field existed the only
    #: place the target lived was inside `model_call_request`'s closure, which is
    #: only ever called after the gate has answered. One target for both
    #: placement sites, exactly as `PlacementCallAuthorities.model_target` is
    #: one. Required with no default, and one of the nine that arrive together
    #: or not at all.
    model_target: object
    #: WHICH MODEL WOULD BE ASKED ABOUT ONE FILE -- `callable(file_id)` returning
    #: the `(client, target)` pair or `None`, or `None` itself for a deployment
    #: whose destination is the single pair above. `104` §17.13 ruling 3: the cloud
    #: model where the cloud gate permits the file, the local one where it does
    #: not, and no call where neither does. One site is two destinations now, so a
    #: single pair can no longer describe the run, and `route_in_force` below is
    #: the only read of either spelling.
    #:
    #: REQUIRED WITH NO DEFAULT like every field here, and
    #: `test_no_unfinished_knowledge_source_gained_an_implementation_default` is
    #: the guard: which files may cross to a provider is the deployment's question
    #: and a caller that has not answered it must not silently get "the one pair,
    #: for everything". A run with one destination passes `None` and says so.
    route_for: object
    #: `104` R-14's one-slot usage mailbox, or `None`. `104` R-145: site C's calls
    #: recorded no `llm_call_usage` row because this path was never handed the
    #: mailbox site A and site B's `run_call` take from -- invisible while site C
    #: never reached a call, and the standing "every response has its usage
    #: beside it" test failed the moment it did. Required with no default like
    #: every field here: `None` is the deployment whose transport reports no
    #: usage, said by the caller and not assumed by P11.
    usage_recorder: object
    #: `104` §18.15. HOW MANY OF THIS PASS'S CLOUD ROUND TRIPS MAY BE OPEN AT ONCE,
    #: and the number is NOT CHOSEN HERE. The owner's direction is that the cloud
    #: lane runs wide while the local lane stays serial; how much of this machine
    #: one run may take at a time is a deployment fact the composition root already
    #: answered once, when it chose how many processes read files at once
    #: (`cli.EXTRACTION_WORKERS`), and that is the count it passes. A number P11
    #: picked for itself would be a second answer to one question, invisible to
    #: whoever changed their mind about the first.
    #:
    #: Required with no default like every field here, and
    #: `test_no_unfinished_knowledge_source_gained_an_implementation_default` is
    #: the guard. `1` is a real answer and means "one at a time", which is what
    #: this pass did before the lane existed; a caller that has not thought about
    #: it says so by saying one, rather than being given seven by P11.
    calls_at_once: int
    #: The question to put to the person about ONE file, or `None` for the files
    #: there is nothing to ask about. Called with the subject; answered with a
    #: `(question, node ids)` PAIR and never with an `Ask`.
    #:
    #: **The pair, not the record, and the distinction is load-bearing.** `Ask` is
    #: P11's, and `tests/integration/test_ambiguity_cases.py` asserts that
    #: `pipeline.py` is its only builder -- the guard that was written when §6.9's
    #: question had a shape and no producer. A composition root minting one would
    #: put the record's invariants (at least two options, a non-empty question) in a
    #: second place, and the review surface reads `Ask` as P11's account of what it
    #: asked. So the caller supplies the WORDS and the DESTINATIONS, which are
    #: policy, and this package builds the record, which is not.
    #:
    #: WHICH files are worth a person's attention stays entirely the caller's: §6.10
    #: records the cost of getting that wrong from the other side -- 73% of a real
    #: corpus goes unplaced, and a run that asked about all of it would be worse than
    #: the silence it replaced, because nobody answers a hundred and forty-five
    #: questions.
    #:
    #: Required, with no default, exactly as `ask_or_abstain` is and for the same
    #: sentence: absent means refuse, never guess. A caller with nothing to ask
    #: passes a callable that answers `None`, which is a decision it has made rather
    #: than one this dataclass made for it.
    ask_about_file: object
    #: The destination the person already named for this file, or `None`. Read
    #: BEFORE retrieval, because a file whose home the person has given is not a
    #: file the engine is still deciding about -- scoring it again and hoping the
    #: numbers agree is how an answer comes to be quietly overruled by the evidence
    #: it was asked to settle.
    #:
    #: P15's `store.chosen_node` is what a caller passes, injected rather than
    #: imported for the reason every authority here arrives from the caller: P11
    #: does not read another part's tables, and a package that read the answer store
    #: directly would be the place where a placement started depending on a question
    #: having been asked.
    chosen_by_user: object
    #: The fields that may not, on their own, carry a file OUT of the folder it
    #: is in. `_without_kind_only_moves` is the rule and carries the measurement;
    #: this is where the deployment says which of P6's fields play a role that
    #: can only ever answer what-or-when. The library's role vocabulary names two
    #: -- `artifact_kind` and `cycle_period` -- and which FIELD each binds to is a
    #: fact about a catalogue P11 does not own.
    #:
    #: Required, with no default, exactly as `ask_about_file` and `chosen_by_user`
    #: are: absent means refuse, never guess. A deployment that has decided every
    #: one of its fields can anchor a move passes an empty set, which is a
    #: position it has taken rather than one this dataclass took for it.
    fields_that_cannot_anchor_a_move: frozenset[str]
    #: For each file whose OWN folder was made for what it holds -- every one of
    #: its files agreeing about a field, not merely the ones that spoke -- the
    #: node that folder became. `_a_folder_made_for_this_keeps_it` is the rule
    #: and carries the measurement; this is where the deployment says which
    #: folders clear the band, because "every file" needs a floor beneath it and
    #: a count is a number P11 does not own.
    #:
    #: A MAPPING AND NOT A SET, because the rule has to keep the folder it is
    #: protecting: a set would leave P11 to work out which candidate is the
    #: file's own folder, and the only channel it could ask is a LABEL match
    #: that is silent for a folder whose name says nothing about its contents.
    #:
    #: Required, with no default, for the same reason as the set above: a run
    #: that did not state it would carry a child's report card out of the folder
    #: their parent keeps it in, on an artifact kind and a term. A deployment
    #: with no folders of the person's own passes an empty mapping, which is a
    #: position it has taken rather than one this dataclass took for it.
    their_own_folder_made_for_what_it_holds: Mapping[str, str]
    p2: P2Run | None
    #: The node for the folder each file IS IN, for every file sitting in one of
    #: the person's own folders -- not only the ones that folder was made for.
    #: This is what tells REFINEMENT from REMOVAL (`00`'s amendment of line 22,
    #: `104` §13.8): a file going deeper inside the branch it already sits in is
    #: refinement and is allowed; a file going somewhere else is removal and stays
    #: constrained. `_without_kind_only_moves` and `_staying_put_wins_a_tie` are
    #: the two rules that read it.
    #:
    #: NOT `their_own_folder_made_for_what_it_holds`, and the six `Python 1006`
    #: files are why: that mapping is gated on coverage -- every file in the folder
    #: agreeing about a field -- and `Python 1006` holds twenty-one files that
    #: agree about nothing, so it is absent from that mapping and present in this
    #: one. Two questions, two mappings: "was this folder built for this kind of
    #: thing" and "is this where the file lives".
    #:
    #: NOR the `CURATED_FOLDER` channel, which is the instrument both rules reach
    #: for and neither should: it is a LABEL match, so it fires for a folder whose
    #: NAME agrees with the file and is silent for one whose name does not.
    #: `_a_folder_made_for_this_keeps_it` records the measurement -- a first draft
    #: reading the channel abstained on all five files of a corpus small enough to
    #: read, because `Kid` is called "Kid" and a report card says nothing about a
    #: kid.
    #:
    #: Required, with no default, exactly as the two authorities above it are.
    #: `test_no_unfinished_knowledge_source_gained_an_implementation_default` is
    #: categorical about it -- "a field gaining a default here is P11 answering a
    #: question the design says is the user's or the deployment's" -- and which of
    #: P10's nodes is a folder the person already has, and which files are inside
    #: it, are reads of P1's paths that P11 does not make.
    #:
    #: An EMPTY MAPPING is the answer for a deployment with no folders of the
    #: person's own, and then neither rule changes: no candidate is inside
    #: anything, nothing is exempt, and both behave exactly as they did before
    #: this field existed. That is a position the caller has taken rather than one
    #: this dataclass took for it.
    the_folder_each_file_is_in: Mapping[str, str]
    #: `104` R-113. `(file_id, node_id) -> the folder the file is in now`, or
    #: `None`, for a proposed move that would cross one of the person's own
    #: top-level folders. `00`:20 makes crossing their choice and P12's freeze
    #: refuses a move they have not made -- so a placement this answers is one
    #: with a destination it cannot reach, and it belongs in a review set beside
    #: the files nothing placed at all rather than on the "ready to file" line.
    #:
    #: INJECTED, and this is the one authority here that P11 could not derive if
    #: it tried: the answer needs §1.1's folder landscape, which is a fact about
    #: the command the run was typed in, not about the corpus.
    #:
    #: REQUIRED, WITH NO DEFAULT, exactly as `ask_about_file` and the two beside
    #: it are, and `test_no_unfinished_knowledge_source_gained_an_implementation_
    #: default` is the guard that says so: a field with a default here is P11
    #: answering a question the design leaves to the deployment. Whether a person
    #: has permitted moves across their own top-level folders is such a question,
    #: and a caller that has not answered it must not silently get "yes, nothing
    #: is held". A run that holds no move passes `None`, which is the same answer
    #: `--may-cross-folders` gives, and it is a position that caller has taken.
    a_move_the_person_has_not_permitted: object

    def __post_init__(self) -> None:
        require_policy(self.policy)
        if not isinstance(self.fields_that_cannot_anchor_a_move, frozenset):
            raise ValueError(
                "`fields_that_cannot_anchor_a_move` is a frozenset of field "
                "keys, given by the composition root: which of P6's fields can "
                "only say what-or-when is a fact about a catalogue P11 does not "
                "own, and a run that did not state it would move files on an "
                "artifact kind alone")
        if not isinstance(self.their_own_folder_made_for_what_it_holds, Mapping):
            raise ValueError(
                "`their_own_folder_made_for_what_it_holds` maps a file id to "
                "the node its own folder became, given by the composition root: "
                "how many files a folder needs before every one of them "
                "agreeing means it was built for that is a band P11 does not "
                "own, and a run that did not state it would carry a file out of "
                "the folder its owner keeps it in on an artifact kind alone")
        if not isinstance(self.the_folder_each_file_is_in, Mapping):
            raise ValueError(
                "`the_folder_each_file_is_in` maps a file id to the node for "
                "the folder that file is in, given by the composition root: "
                "which of P10's nodes is a folder the person already has, and "
                "which files are in it, are reads of P1's paths that P11 does "
                "not make. A deployment with none passes an empty mapping, and "
                "then no move is treated as a refinement")
        if not isinstance(self.limits, PlacementLimits):
            raise ValueError(
                "the pipeline runs under P1's seven ceilings and reads them "
                "through `placement.config.placement_limits`; a run with no "
                "limits is a run under a bound nobody chose"
            )
        if self.p2 is not None and not isinstance(self.p2, P2Run):
            raise ValueError("`p2` is a P2Run or None; P11 assembles neither half")
        if (not isinstance(self.calls_at_once, int)
                or isinstance(self.calls_at_once, bool)
                or self.calls_at_once < 1):
            raise ValueError(
                "`calls_at_once` is how many of this pass's cloud round trips may "
                "be open at once, given by the composition root out of the count "
                "it already chose for how much of this machine one run may take. "
                "One is a real answer and means one at a time; zero is not a "
                "narrow lane but a pass that prepares every call and sends none")

    def model_path_available(self) -> bool:
        """Whether step 7 can run at all. A deterministic-only run is legal.

        §6.6 decides a unique direct match with zero model calls, so a run with
        no model injections is a correct run and must not look like a failure.
        What is NOT legal is discovering the injections are missing after a
        dossier has been assembled, which is why this is asked before one is.

        The destination is asked through `route_in_force` rather than as two
        members of the set, because `104` §17.13 makes it one question with two
        spellings: a deployment states its one pair, or it states the route that
        picks per file. Either is a destination; neither present is not.
        """
        return (None not in (self.gate, self.prompt, self.call_dependencies,
                             self.model_call_request, self.chosen_node_of,
                             self.sensitivity_policy)
                and self.route_in_force() is not None)

    def route_in_force(self):
        """The one callable answering "which model for this file", or `None`.

        `104` §17.13 ruling 3 gives a call site two destinations, so the single
        `model_client`/`model_target` pair can no longer be read directly. This is
        where the two spellings become one: a caller that stated the pair gets it
        back as a route that answers the same thing for every file, and a caller
        that stated a route gets its own. `None` is a run with no model path at
        all, which is a correct run.
        """
        if self.route_for is not None:
            return self.route_for
        if self.model_client is None or self.model_target is None:
            return None
        pair = (self.model_client, self.model_target)
        return lambda _file_id: pair

    def route(self, file_id: str):
        """The `(client, target)` pair this FILE is answered by, or `None`.

        `None` covers both "no model path in this run" and "no model this file may
        reach", and the callers want the same thing of each: assemble nothing and
        say so. The two are told apart where the difference matters, by
        `route_in_force`, which is what `_abstention_explanation` asks before it
        claims no model is set up.
        """
        route = self.route_in_force()
        if route is None:
            return None
        return route(file_id)

    def target_locality(self, file_id: str) -> str | None:
        """Where the model asked about THIS FILE runs, or `None` if none would be.

        Read off the route and nowhere else: the request builder closes over the
        same answer, but it is called only after §8.4's gate has answered, and the
        gate is what needs this (`104` R-118).

        **It takes a file id since `104` §17.13 ruling 3**, because the answer
        stopped being one value for the run: the same site sends one file to a
        cloud model and the next to a local one, and a locality read without a
        file would authorise a dossier for a destination that file never had.
        """
        chosen = self.route(file_id)
        if chosen is None:
            return None
        return chosen[1].locality

    def prompt_for(self, call_site: str) -> object:
        """The text THIS site is asked under. One field per site, never a shared one.

        `_judge_with_model` assembles the request for both placement sites, and it
        read `self.prompt` for both -- so a residual call went out under site C's
        template, C's response schema and C's shaping policy. A D answer names one
        of §7.7's eight actions and C's schema has no `action` key, so every
        residual answer was heading for `SCHEMA_INVALID`, rejected for obeying an
        instruction that was not its own either.

        REFUSES rather than falling back to C's, which is the whole point: a
        fallback here is the defect with a friendlier face. `run_call` refuses the
        same mistake from the other side (`_missing_configuration`'s
        `prompt_call_site`), and two walls around one error is what the model path
        is owed -- this one names the deployment that has not wired D, that one
        names any other route to the same request.
        """
        if call_site != D_RESIDUAL:
            return self.prompt
        if self.residual_prompt is None:
            raise ResidualPromptRequired(
                "§7.7's residual call has its own text, its own response schema "
                "and its own shaping policy, and this deployment supplied none. "
                "A deployment may wire C and not D -- that is what `None` says -- "
                "and then a residual set that asks for a model is refused here "
                "rather than asked under site C's prompt, which is what site C's "
                "schema would then reject it for.")
        return self.residual_prompt

    def model_decides(self) -> bool:
        """Whether this run's model DECIDES placements, which is R-19's condition.

        Two facts, and both are needed. The path has to exist -- `00`'s amendment
        governs "whenever a model is configured", and with none the deterministic
        path remains the fallback. And the text has to be RATIFIED, read off the
        prompt's own field the way `_observed_only` reads it, because a site
        running under text nobody approved records its answer and applies
        nothing: routing every placeable file to a site whose verdict is
        rewritten to `abstain` would replace each exact placement with a file
        that has no home, which is the opposite of what the ruling asks for.

        A METHOD and not a field. `PipelineInputs` fields carry no defaults on
        purpose -- a field gaining one is P11 answering a question the design
        says is the deployment's -- and this answers nothing: it reads two things
        the caller already stated.
        """
        return self.model_path_available() and bool(
            getattr(self.prompt, "ratified", False))


@dataclass(frozen=True)
class CorpusResult:
    """§6.12 step 9 -- "a reviewable plan of exact placements, shallow placements,
    scoped fallbacks, and abstentions" -- plus what §7 then did with the rest.

    One object, so a review surface does not have to run the pipeline twice to
    learn what happened, and so `unplaced_file_ids` is a fact the run produced
    rather than something the caller re-derives by filtering.
    """

    decisions: tuple[PlacementDecision, ...]
    group_plans: tuple[GroupPlan, ...]
    residual_sets: tuple[ResidualSet, ...]
    unplaced_file_ids: tuple[str, ...]
    #: Every subject the run knew about, by file id -- the ones handed in and the
    #: members P9 supplied. `review_residual_sets` needs them and re-deriving a
    #: content hash from P1 afterwards would be a second copy of P1's identity.
    subjects: dict
    #: `104` §18.15. THE MOST OF THIS PASS'S CLOUD ROUND TRIPS THAT WERE EVER
    #: OPEN AT ONCE -- a MEASUREMENT of the run and never the setting, which is
    #: `PipelineInputs.calls_at_once`. It is on the result for the reason this
    #: whole record is: the report reads what the run did rather than running the
    #: pipeline again to find out. A pass whose files never sat next to each
    #: other on the cloud opens windows of one and this says one; a pass that
    #: reached no model at all says nought. Both are the honest reading, and the
    #: screen prints the number only when it is more than one.
    calls_at_once: int


# --- identity and the supersede link ----------------------------------------------


def _identity(conn: sqlite3.Connection, *, plan_version: str, subject_ref: str,
              observed_at: str, suffix: str = "") -> tuple[str, str | None]:
    """This decision's id, and the live decision it revises.

    `one_current_placement_decision` is a partial unique index over unsuperseded
    rows, so a second live decision about one subject is refused by SQLite. Every
    writer here therefore links rather than remembering to: §8.2's rule is that a
    revised decision is a NEW row whose `supersedes` names the prior one, and the
    prior row keeps its evidence.

    The id gains a counter only when the plain one is already taken, because
    `mark_superseded` refuses a self-supersede and a fixed clock would otherwise
    produce the same id twice for one subject.
    """
    live = current_decision(conn, plan_version=plan_version,
                            subject_ref=subject_ref)
    taken = {row["record_id"] for row in conn.execute(
        "SELECT record_id FROM placement_decisions WHERE plan_version = ? AND "
        "subject_ref = ?", (plan_version, subject_ref))}
    decision_id = f"{plan_version}:{subject_ref}:{observed_at}{suffix}"
    if decision_id in taken:
        decision_id = f"{decision_id}#{len(taken)}"
    return decision_id, (live.decision_id if live is not None else None)


def _write(conn: sqlite3.Connection, decision: PlacementDecision, *, inputs,
           reason: str, component_version: str, observed_at: str) -> PlacementDecision:
    """Append the decision, then measure it. One place, so nothing is unmeasured."""
    record_decision(conn, decision, component_version=component_version,
                    observed_at=observed_at,
                    supersede_reason=reason if decision.supersedes else None)
    if inputs.p2 is not None:
        emit_scoring_stage(conn, run_id=inputs.p2.run_id, decision=decision,
                           version_tuple_ref=inputs.p2.version_tuple_ref,
                           inputs=inputs.p2.upstream_stage_refs)
    return decision


# --- §6.12 steps 3 to 9, for one subject -------------------------------------------


def _learning_subject_id(subject) -> str:
    """§8.7's subject id for the scope its kind names. One read, two kinds."""
    return subject.file_id if subject.kind == FILE else subject.group_id


#: `104` §18.2 gap 14 × §8.6: THE GROUP'S CALL SPENDS FROM ITS OWN LEDGER. The
#: per-file placement purse is sized per file, and a packet's one question is not
#: one of those files: measured on the six-file corpus of
#: `tests/integration/test_local_model_fact_pass.py`, the group's call plus a
#: template call emptied the observe purse and the last file -- the factless one
#: site C exists for -- recorded `BUDGET_EXHAUSTED` with nothing in the run saying
#: why. `cli.situation_scan_budget` and `cli.template_scan_budget` make the same
#: argument for sites G and E: the rate, floor and ceiling are the per-file ones
#: and are not new numbers; what the group's call owns is the `scan_id`.
GROUP_BUDGET_SUFFIX: str = ":group"


@dataclass(frozen=True)
class GroupAnswer:
    """What the model said about the GROUP, carried to the member it decides.

    `104` §18.2 gap 14, `00`:112: *"The placement engine should FIRST confirm the
    shared parent branch ... It can then classify members within that branch."*
    One call took the whole group; this is that call's answer, handed to
    `place_file` so that a member placed by it is written by the one function that
    writes every placement row -- same privacy state, same review policy, same
    supersession, same table.

    `membership` is P9's own decision word for this file's membership, copied onto
    `GroupSupport` rather than minted here: whether the file is IN the group is
    P9's finding and P11 does not re-decide belonging.

    `sits_apart` is P9's OUTLIER FLAG, carried for the same reason and doing the
    same work one step later. A member P9 flagged sits apart from the group, so
    the group's answer is not its answer -- and a row that claimed `group_support`
    for a file the plan then EXCLUDES as an outlier would be one record saying
    both things at once. It is judged on its own with the group's folder offered,
    which is what happens to a member that contradicts the answer, because it is
    the same situation reached from P9's evidence rather than from this file's.

    There is no `contradicted` field, and the absence is the point. Whether a
    member's own evidence rules the group's folder out is answered from the
    member's OWN retrieval, inside `place_file`, off §6.3's suppression -- the
    check that already exists and already records what it suppressed and why.
    Carrying a flag computed elsewhere would be a second opinion about the same
    file, reached from a second retrieval, free to disagree with the one on the
    record. `sits_apart` is not that: it is a finding P9 already made and already
    published, copied and never re-derived.
    """

    group_id: str
    node_id: str
    membership: str
    sits_apart: bool = False


#: The sentence a contradicting member's dossier carries beside the group's folder
#: (`104` §18.2 gap 2's channel: the rule's own words inside the candidate's
#: `location`, never a sixteenth dossier key). It says what was noticed and not
#: what to conclude -- the folder is on `allowed_vocabulary` and the model may
#: still answer with it.
RANKED_BELOW_BECAUSE_THE_FILE_DISAGREES: str = (
    "the group this file was accepted into was placed here, and this file's own "
    "stated values rule that folder out"
)

#: The same channel for the other way a member sits apart from its group's answer:
#: the grouping stage itself flagged this file as an outlier of the packet.
RANKED_BELOW_BECAUSE_THE_GROUPING_SET_IT_APART: str = (
    "the group this file was accepted into was placed here, and the grouping "
    "stage set this file apart from that group"
)


def _with_the_graphs_own_channel(retrieval: Retrieval, graphs) -> Retrieval:
    """`104` §18.2 gap 12's scoring half: §6.3's graph channel, finally produced.

    `00`:107 lists graph relationships among the six things that retrieve a node,
    `scoring._CHANNEL_WEIGHT` has weighed `graph_relationship` at 1 since the
    module was written, and NOTHING PUT IT ON A CANDIDATE -- so
    `retrieval.PRODUCED_CHANNELS` truthfully declared four channels, gap 13's
    denominator counted 5, and a candidate whose whole case was a typed
    relationship to a file already accepted in it scored zero for it. That is the
    half of gap 12 the scorer owns.

    **THE WEIGHT IS THE ONE ALREADY THERE, AND IT STAYS 1.** `00`:109-110 name
    the relationships and give no numbers, so the fallback would be the nearest
    channel's weight -- except that a weight is not missing here. `_CHANNEL_
    WEIGHT`'s own argument is §3.13's ordering ("a direct fact outweighs a group
    membership outweighs a relationship") and gap 13's note says in terms that
    the relative order must stay unchanged. Raising it to the accepted group's 2
    would put a relationship level with a membership, which §3.13 does not, and
    would make a direct fact alone score 3/7 -- gap 13's headline defect,
    reopened by the fix for gap 12.

    **THE DECLARATION IS THIS RETRIEVAL'S, NOT A CONSTANT, AND THE ARITHMETIC IS
    WHY.** `Retrieval.producible_channels` is per retrieval and required with no
    default precisely so "a caller that retrieves through a narrower path than
    `retrieve`" declares its own; the object that PUTS the channel on a candidate
    is the object that declares it, which is exactly the invariant `score_
    candidates` checks. Declaring it for every retrieval instead would move the
    denominator from 5 to 6 for every file in the corpus, and `(3 - 2) / 6 =
    0.1667` is below the wired 0.20 margin -- so a file whose direct facts match
    one node against a rival reached by an accepted group alone would abstain
    `low_margin`, which is `_exact_margin`'s own worked example and the pair
    `test_a_measured_margin_over_the_threshold_reads_true_not_vacuous` pins. No
    positive weight avoids it: `(3 - 2) / (5 + w) >= 0.20` has no solution for
    `w > 0`. A file with no typed edge therefore scores byte-identically to
    before, and the run-wide change stays what it is -- a policy number, `cli-
    support-v2`'s 0.20, which is the owner's to re-set.

    **What it buys, on a file that HAS one.** The denominator is 6, so a node
    reached by an accepted group AND a typed edge scores 3/6 and meets the 0.50
    bar that a group alone (2/6) does not: `00`:109's own example, where `HW
    3.pdf` is compared "against the PHYS1401 node's syllabus, lectures, midterm,
    accepted problem sets". A node reached by a typed edge alone scores 1/6 and
    still cannot place, which is §6.5's "a target file connected only by generic
    similarity or one high-frequency entity must remain uncertain".

    `is_typed_support` and not `graph.anchors` is the test, and it is §6.5's:
    anchors held together by one everywhere-entity are a generic hub, and
    `score_candidates` already reports that node as `generic_hub`. A channel
    granted on the hub would score the hub.

    `semantic_only_node_ids` is recomputed rather than carried, because it is the
    same question asked of the new channel set: a node reached only by an
    embedding that turns out to hold a typed relationship is no longer supported
    by an embedding alone, and `score_candidates` reads that set directly to
    decide `semantic_only`. Leaving it would report a node with a typed edge as
    semantic-only and `_reason` would abstain it on that word.
    """
    supported = frozenset(
        node_id for node_id, graph in graphs.items() if is_typed_support(graph))
    if not supported:
        return retrieval
    candidates = tuple(
        candidate if candidate.node_id not in supported
        else dataclasses.replace(
            candidate,
            channels=tuple(dict.fromkeys(
                candidate.channels + (GRAPH_RELATIONSHIP,))))
        for candidate in retrieval.candidates
    )
    return dataclasses.replace(
        retrieval, candidates=candidates,
        producible_channels=tuple(dict.fromkeys(
            tuple(retrieval.producible_channels) + (GRAPH_RELATIONSHIP,))),
        semantic_only_node_ids=frozenset(
            candidate.node_id for candidate in candidates
            if set(candidate.channels) <= set(NON_DECIDING_CHANNELS)),
    )


def place_file(conn: sqlite3.Connection, *, subject, inputs: PipelineInputs,
               evidence, component_version: str, observed_at: str,
               group_plan_id: str | None = None,
               returned_from: str | None = None,
               group_answer: GroupAnswer | None = None) -> PlacementDecision:
    """One file placed here, on this thread, from step 3 to step 9.

    `104` §18.15 split the body into `place_file_steps` so the corpus pass can hold
    several files' round trips at once. This is that generator driven inline, and
    it is what every caller that places one file at a time still gets -- the
    multi-home branch of `run_corpus`, `review_residual_sets`, and P12's returns.
    """
    return drive_inline(place_file_steps(
        conn, subject=subject, inputs=inputs, evidence=evidence,
        component_version=component_version, observed_at=observed_at,
        group_plan_id=group_plan_id, returned_from=returned_from,
        group_answer=group_answer))


def place_file_steps(conn: sqlite3.Connection, *, subject,
                     inputs: PipelineInputs, evidence, component_version: str,
                     observed_at: str, group_plan_id: str | None = None,
                     returned_from: str | None = None,
                     group_answer: GroupAnswer | None = None):
    """One file through steps 3-7 and 9. Step 8 runs inside P8 when it is needed.

    `group_plan_id` is passed in rather than patched on afterwards, because the
    STORED row has to carry it: `GroupPlan` asserts every member decision shares
    the plan's id, and a row written without it would make the review surface show
    several unrelated file moves while the in-memory plan looked correct.

    `returned_from` is §7.9's link: the residual decision that handed this file
    back. Without it `link_return` refuses, and §8.8's diff cannot walk the loop.

    **`104` §18.15: A GENERATOR, AND THE ONE `yield` IS SITE C's SOCKET.** Every
    statement here reads or writes the database and stays on the calling thread in
    the order it is written; the round trip is the only thing that may run
    elsewhere, and only when the route sent this file to the cloud.

    `group_answer` is `104` §18.2 gap 14's whole direction of travel: the model
    was asked about this file's GROUP, and this file is being placed FROM that
    answer rather than the answer being read back off this file. Two outcomes, and
    the member's own evidence decides which:

    * its stated values do NOT rule the group's folder out -- it goes with the
      group. No second call is made about it: the model has already answered about
      this file, as one of the files it was shown, and asking again would be
      paying twice for one question and inviting two answers to it. The row says
      `decided_by=model`, because the group's answer IS the model's, and carries
      `group_support` naming the group and P9's membership word.
    * its stated values DO rule it out -- §6.3 suppressed that folder for this
      file. It is an outlier of the group's answer, it is placed singly by the
      ordinary per-file call, and the group's folder is OFFERED to that call on
      the shortlist's tail with the disagreement as its reason. `00`:112's own
      worked example is this: *"It can identify that a Duke essay is an outlier
      because of its conflicting target-institution fact, exclude it from the
      Columbia packet, and route it to a separate legal branch or review queue."*
    """
    subject_ref = subject_ref_of(subject)

    # §8.4, before anything a model could see exists.
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    # §13's fourth consequence, read BEFORE step 3. A file whose destination the
    # person has already named is not a file this pipeline is still deciding about,
    # and running retrieval and scoring over it anyway would leave the answer
    # standing beside a support score that could disagree with it -- which is how a
    # correction comes to be silently overruled by the evidence it was asked to
    # settle. `66` §12 makes an answer something that outlives the run; an answer
    # the next run re-argues has not outlived anything.
    #
    # The node is still checked against the index, exactly as a model-chosen one is
    # three steps below and for the identical reason: `legal_node_ids` is the one
    # authority on what this plan version contains, and a destination that is not in
    # it is a typo, a stale answer from a tree that has been rebuilt, or a node the
    # person's answer named before it was superseded. None of those is a placement.
    named = inputs.chosen_by_user(subject)
    if named is not None:
        return _user_chose(conn, subject=subject, inputs=inputs, node_id=named,
                           privacy=privacy, group_plan_id=group_plan_id,
                           returned_from=returned_from,
                           component_version=component_version,
                           observed_at=observed_at)
    # Design:185 -- protected material "should not be moved automatically without a
    # user policy that explicitly permits it". P7 publishes the predicate and P11
    # asks it; asking only for protected material is not an optimisation, it is the
    # only case the answer can change. `may_move_automatically` reads P1's `files`
    # row, and a file P1 has never seen has no automatic move to permit.
    automatic_move_permitted = (
        automatic_move_permitted_for(conn, file_id=subject.file_id,
                                     plan_version=inputs.plan_version)
        if privacy.protected else False
    )

    # Step 3, and half of step 5 with it: retrieval suppresses as it goes, because
    # §6.3 makes suppression part of retrieval rather than a later filter.
    retrieval = retrieve(
        conn, subject=subject, plan_version=inputs.plan_version,
        limits=inputs.limits, facts=evidence["facts"],
        group_ids=evidence["group_ids"],
        curated_folder_labels=evidence["curated_folder_labels"],
        semantic_neighbours=evidence["semantic_neighbours"],
        component_version=component_version, observed_at=observed_at,
    )

    # §8.7, before any `place` is emitted.
    # `file` only. `learning._subject_ids` keys the file scope on the file id and
    # refuses `template` and `domain` outright, because P11 cannot know which
    # template or domain a user meant. `node` and `corpus` need a subject the
    # caller names; asking for them here would look like a wider check and
    # perform none.
    rejected = {
        hit.node_id for hit in suppressed_nodes(
            conn, subject_ref=subject_ref,
            node_ids=tuple(c.node_id for c in retrieval.candidates),
            scopes=(FILE,),
        )
    }
    if rejected:
        retrieval = dataclasses.replace(
            retrieval,
            candidates=tuple(c for c in retrieval.candidates
                             if c.node_id not in rejected))
    if inputs.p2 is not None:
        emit_retrieval_stage(conn, run_id=inputs.p2.run_id, retrieval=retrieval,
                             version_tuple_ref=inputs.p2.version_tuple_ref,
                             inputs=inputs.p2.upstream_stage_refs)

    # Step 4.
    graphs = {
        candidate.node_id: build_node_local_graph(
            subject=subject, candidate=candidate,
            entry=entry_for(conn, plan_version=inputs.plan_version,
                            node_id=candidate.node_id),
            related_files=evidence["related_files"], limits=inputs.limits,
            entity_frequency=evidence["entity_frequency"],
            generic_entity_frequency=evidence["generic_entity_frequency"],
        )
        for candidate in retrieval.candidates
    }
    # AFTER `emit_retrieval_stage`, deliberately. §6.2's stage is what RETRIEVAL
    # answered, and its `semantic_only` is retrieval's own; the graph is step 4's
    # and can only be known once the entries are read. What the SCORE used is on
    # every `Scored` row (`producible_weight`), so a P2 replay reads the scale
    # from the thing that was scored rather than from the stage before it.
    retrieval = _with_the_graphs_own_channel(retrieval, graphs)

    # Step 6. FIRST, BEFORE THE COLLAPSES, AND THE ORDER IS THE RULE. A folder
    # every one of whose files agrees about something was built for that, and
    # nothing carries a file out of it on what-kind-or-when alone. It runs ahead
    # of the two collapses below because they both read the candidate SET: the
    # ancestor collapse drops a folder the moment one of its own children is also
    # a candidate, so run afterwards this rule found the file's own folder
    # already gone and dropped the rest, and all five files in
    # `_two_lives_one_semester_corpus` abstained `conflicting_facts`. Measured
    # 2026-09-05 under the adopted-branch change that xfail records -- the only
    # state in which that folder HAS children -- and it is why this is the first
    # thing step 6 does.
    retrieval = _a_folder_made_for_this_keeps_it(
        retrieval,
        its_own_folder=inputs.their_own_folder_made_for_what_it_holds.get(
            subject.file_id),
        fields_that_cannot_anchor_a_move=inputs.fields_that_cannot_anchor_a_move)
    # Then both halves of the collapse. `identify_child_parent_fallback_or_none`
    # names the first one and it had no implementation until 2026-08-29.
    retrieval = _without_superseded_ancestors(
        conn, retrieval, plan_version=inputs.plan_version)
    # And the same collapse across branches, where the rival is the engine's own
    # vaguer copy of a folder the person already made (`00`:100).
    retrieval = _without_duplicated_proposals(
        conn, retrieval, plan_version=inputs.plan_version)
    # P10'S TWO FACTS ABOUT EVERY NODE, READ IN ONE WALK. The rule below needs
    # each node's `dimension`; §6.10's margin needs to know which nodes are
    # folders the person already has. Both are facts about the same nodes, and
    # two comprehensions over `inputs.tree.nodes` is two walks of the whole tree
    # PER FILE -- the O(files x nodes) shape `planning/58-SCALE-STRESS.md` §2
    # measured and `reachable_entries` was written to stop. One walk is not a fix
    # for that shape; it is simply not a second copy of it.
    #
    # Read by name, because `PipelineInputs.tree` is typed `object` on purpose --
    # P11 does not own P10's record -- and this is how `cli.py` reads the same
    # two attributes off the same nodes.
    # `parent_of` joins them, in the same walk and for the same reason: telling
    # refinement from removal is a question about the CHAIN, and a third
    # comprehension over the tree per file is the O(files x nodes) shape again.
    dimension_of: dict[str, str | None] = {}
    parent_of: dict[str, str | None] = {}
    their_own_folders: set[str] = set()
    for node in getattr(inputs.tree, "nodes"):
        dimension_of[node.node_id] = getattr(node, "dimension", None)
        parent_of[node.node_id] = getattr(node, "parent_node_id", None)
        if getattr(node, "existing_path", None) is not None:
            their_own_folders.add(node.node_id)

    # WHICH CANDIDATES ARE INSIDE THE FOLDER THIS FILE IS ALREADY IN. `00`'s
    # amendment of line 22: a move deeper inside the branch the file already sits
    # in is REFINEMENT and is allowed; a move out of the person's arrangement is
    # REMOVAL and stays constrained. Both rules below were refusing the first as
    # if it were the second, which is R-48 -- the file stops one level short of
    # the child built for it.
    refinements = _refinements_of(
        (inputs.the_folder_each_file_is_in or {}).get(subject.file_id),
        parent_of, tuple(c.node_id for c in retrieval.candidates))

    # And the last: a folder reached only because it holds the same KIND of
    # thing is not a home this file's evidence chose.
    retrieval = _without_kind_only_moves(
        retrieval, dimension_of=dimension_of,
        fields_that_cannot_anchor_a_move=inputs.fields_that_cannot_anchor_a_move,
        refinements=refinements)
    # THE SET-ASIDE NODES KEEP THEIR GRAPHS (`104` §18.2 gap 2). They were built
    # one step above, over every retrieved candidate, before any step-6 rule ran;
    # throwing them away now would mean a file the MODEL places on a set-aside
    # folder records `graph_anchors=()` for a graph this run actually built, and
    # `_ranked_set_aside` below could not order the tail by its real scores.
    # `assess` is unaffected either way: `score_candidates` walks
    # `retrieval.candidates` and asks `graphs.get`, so a key it does not walk to
    # is a key it never reads.
    offer_ids = {c.node_id for c in retrieval.candidates} | {
        item.candidate.node_id for item in retrieval.set_aside}
    graphs = {node_id: graph for node_id, graph in graphs.items()
              if node_id in offer_ids}
    # WHICH CANDIDATES ARE FOLDERS THE PERSON ALREADY HAS. `existing_path` is set
    # only on an adopted node and is the same fact P10's report reads to print
    # "[yours already]", so this is not a second opinion about it. §6.10's margin
    # needs it to tell a tie between two of somebody's own folders -- which is
    # §6.9's question and is asked -- from a tie between where a file already sits
    # and a folder this run would like to create, which is not a question at all.
    assessment = assess(
        retrieval, graphs, policy=inputs.policy,
        their_own_folder_node_ids=frozenset(their_own_folders),
        refinements=refinements)

    context = _Context(subject=subject, subject_ref=subject_ref, inputs=inputs,
                       privacy=privacy, retrieval=retrieval,
                       assessment=assessment, graphs=graphs,
                       automatic_move_permitted=automatic_move_permitted,
                       group_plan_id=group_plan_id, returned_from=returned_from,
                       component_version=component_version,
                       observed_at=observed_at)

    # Steps 7 and 8. Only for a bounded ambiguity, only if §8.4's gate allows a
    # dossier, and only if the caller supplied the model path. Step 8 -- the
    # validator -- runs INSIDE `run_call`; P11 supplies authorities and reads a
    # verdict, and re-checks none of Site C's fifteen.
    chosen_node_id: str | None = None
    #: The model's own answer, when there was one. Hoisted out of the branch for
    #: `104` R-75: `two_condition` below has to be able to read `requires_review`
    #: off it, and inside the branch there was nowhere for the record to see it.
    verdict = None
    #: Whether this file reached the model path and was turned away by §8.4 --
    #: `104` R-74's own condition, carried to the explanation so the record names
    #: the rules as the actor rather than saying nothing about why no judge spoke.
    gate_refused = False
    # `104` §18.2 gap 2's own case in the routing: a file whose every candidate
    # step 6 ranked below the contenders still has a shortlist, and the model is
    # the one `00`'s amendment gives that question to.
    set_aside = _ranked_set_aside(retrieval, graphs, policy=inputs.policy)
    #: `104` §18.2 GAP 14. DOES THIS MEMBER'S OWN EVIDENCE RULE THE GROUP'S FOLDER
    #: OUT? Asked of §6.3's suppression and of nothing else: `retrieve` records one
    #: `ConflictConsidered` per value this file states, naming the branches that
    #: value pulled it away from, and a folder among them is a folder this file
    #: contradicts. P11 writes no second comparison of facts against a node -- one
    #: would be free to disagree with the one already on the record, and `104`
    #: §18.2 gap 16 is what that comparison is; inherited here, not re-opened.
    #:
    #: P9'S FLAG IS THE OTHER WAY TO SIT APART FROM THE ANSWER, and it is read
    #: rather than re-derived. A member P9 called an outlier is excluded from the
    #: plan (`place_group` step three), so placing it BY the group's answer would
    #: write `group_support` on a file the same plan says the group left out.
    contradicts_the_group = group_answer is not None and (
        group_answer.sits_apart or group_answer.node_id in {
            node_id for conflict in retrieval.conflicts
            for node_id in conflict.suppressed_node_ids
        })
    if group_answer is not None and not contradicts_the_group:
        # THE GROUP'S ANSWER IS THIS FILE'S ANSWER, and no second call is made.
        # Checked against the index for the reason a model-chosen node is checked
        # three steps below: `legal_node_ids` is the one authority on what this
        # plan version contains, and P11 places nothing on a disagreement with it.
        if group_answer.node_id not in legal_node_ids(
                conn, plan_version=inputs.plan_version):
            raise ValueError(
                f"{group_answer.node_id!r} is not a legal destination of "
                f"{inputs.plan_version!r}. The group's own call already had its "
                "answer checked against the index; reaching here means the tree "
                "changed underneath the plan, and P11 places nothing on that"
            )
        chosen_node_id = group_answer.node_id
    elif contradicts_the_group:
        # OFFERED, NOT FORCED (`00`:112's outlier, and gap 2's channel). The folder
        # §6.3 suppressed for this file goes back on the shortlist's TAIL, carrying
        # the disagreement as its reason, and the model decides what the
        # disagreement means. It cannot already be a contender -- retrieval
        # suppressed it -- and the guard is here for the day some other rule puts
        # it back rather than for a state that exists.
        already = ({candidate.node_id for candidate in retrieval.candidates}
                   | {item.candidate.node_id for item in set_aside})
        if group_answer.node_id not in already:
            set_aside = set_aside + (SetAside(
                candidate=Candidate(node_id=group_answer.node_id, channels=(),
                                    matching_facts=(),
                                    group_ids=(group_answer.group_id,)),
                because=(RANKED_BELOW_BECAUSE_THE_GROUPING_SET_IT_APART
                         if group_answer.sits_apart
                         else RANKED_BELOW_BECAUSE_THE_FILE_DISAGREES)),)
    if chosen_node_id is None and needs_model_call(
            assessment, model_decides=inputs.model_decides(),
            set_aside_candidates=bool(set_aside)):
        # `104` R-74. WHETHER THE DETERMINISTIC PATH WOULD HAVE PLACED THIS FILE,
        # asked of the same function with the model taken out of it. R-19 sends
        # every placeable file to site C, so a protected file with a unique direct
        # match now reaches the gate for the first time -- and the gate refuses,
        # correctly, and the file abstained `privacy_blocked` where offline it
        # went home.
        #
        # §13.5's own clause is the answer: "with no model configured the
        # deterministic path remains the fallback". A gate refusal is that
        # condition arriving one step later -- there is no model answer to be had
        # about this file -- so the file takes the placement the rules can defend
        # rather than losing its home to a question nobody could ask.
        #
        # NOT a widening of what may be sent. Nothing about the file is assembled
        # and nothing leaves; what changes is only what the run does with the
        # refusal it already had. And it is `False` here, not `True`: a file the
        # deterministic path called a BOUNDED AMBIGUITY has no answer to fall back
        # to either, and its abstention is the same one an offline run makes.
        #
        # `bool(assessment.scored) and` is `104` §18.2 gap 2's arrival here.
        # Before it, this line was reachable only with a non-empty assessment --
        # `needs_model_call`'s first clause turned an empty one away -- so
        # "offline would place" and "offline would not need a model" were the same
        # sentence. They are not the same sentence for a file whose every
        # candidate was ranked below the contenders: no model is needed offline
        # because there is nothing offline can do with it, and reading that as
        # "the rules had a home for this file" would hand R-74 a placement that
        # does not exist.
        offline_would_place = bool(assessment.scored) and not needs_model_call(
            assessment, model_decides=False)
        # `104` R-118: asked about the target that would be sent to. A file the
        # mode keeps off the cloud is a file a LOCAL model may be asked about.
        # `104` §17.13 ruling 3: THIS FILE's target, not the run's. The same site
        # sends one file to a cloud model and the next to a local one, so a
        # locality read without a file would authorise a dossier for a destination
        # this file never had.
        if not may_assemble_dossier(
                privacy, target_locality=inputs.target_locality(
                    subject.file_id)):
            if not offline_would_place:
                return _abstention(conn, context, reason=PRIVACY_BLOCKED)
            gate_refused = True
        elif inputs.model_path_available():
            # `104` R-O's wrapper around R-74's call: a refusal RAISED inside the
            # call comes back as a `CallRefused` rather than ending the run, and
            # everything R-74 does with a refusal the gate DECIDED is unchanged.
            # `104` §18.15: `yield from`, so this file's round trip may be one of
            # several the corpus pass holds open at once. What the wrapper does
            # with a refusal, and what this branch does with the result, are
            # unchanged.
            result = yield from _judged_or_refused_steps(
                conn, subject=subject, inputs=inputs, retrieval=retrieval,
                evidence=evidence, call_site=C_PLACEMENT,
                observed_at=observed_at,
                # §13.5's ranking, handed over as the shortlist. `assess` has
                # already applied §6.10's arithmetic, `_staying_put_wins_a_tie`
                # and the refinement exemption, so `scored[0]` is the
                # deterministic winner -- including the unique direct match,
                # which is now the top-ranked candidate rather than a bypass.
                ranked=tuple(item.node_id for item in assessment.scored),
                # AND THE TAIL OF THE SAME SHORTLIST (`104` §18.2 gap 2). Ranked
                # below every contender, described exactly as a contender is, and
                # each one carrying the sentence the rule that ranked it wrote.
                set_aside=set_aside,
                own_folder_node_id=(
                    inputs.the_folder_each_file_is_in or {}).get(subject.file_id),
                # `104` §18.2 gap 12: step 4's graphs, carried to step 7 so the
                # relationships that scored the candidates are also the ones the
                # model is shown. They were built and read by nobody but the
                # scorer and the decision record.
                graphs=graphs,
            )
            if isinstance(result, Refusal):
                # P7 denied the release, from inside `run_call`. That is §8.4's
                # own answer arrived at from the other direction -- and `104`
                # R-74 applies to it for the same reason it applies to the gate
                # above: a file the deterministic path could place keeps that
                # placement rather than losing its home because the question could
                # not be asked. A bounded ambiguity still abstains.
                if not offline_would_place:
                    return _abstention(conn, context, reason=PRIVACY_BLOCKED)
                gate_refused = True
            # `104` R-O. A REFUSED CALL IS NOT AN ANSWER ABOUT THIS FILE, and
            # `_require_verdict` says why in its own words: "§6.10's abstention
            # reasons are a closed set and none of them means 'the call did not
            # happen'; naming one would record a conclusion nothing reached". So
            # nothing below runs, `chosen_node_id` stays `None`, and step 9 places
            # the file the way a run with no model configured would -- which is
            # exactly what §13.5's Q-A clause names as the fallback: "with no
            # model configured the deterministic path remains the fallback". The
            # refusal is already a `call_refused` event; what it is not is a
            # reason to take this file's home away, nor -- as it was until now --
            # a `ModelJudgementUnavailable` that ends the run on every file after
            # it too. NOT `gate_refused`: §8.4 decided nothing here, and saying it
            # did would name the wrong actor in the record.
            # `104` R-136 joins R-O here. A call that was never BUILT is not an
            # answer about this file either, and it reaches step 9 by the same
            # door: `chosen_node_id` stays `None` and the file is placed the way a
            # run with no model configured would place it.
            #
            # `104` R-173 (9 Sep 2026): A CALL THAT FAILED FALLS THROUGH THE SAME
            # DOOR. `CallFailed` (the provider did not answer: a connection
            # error, a timeout) and `ValidationUnavailable` (the answer could not
            # be judged) are a call that happened and came back with no
            # judgement, and until this ruling they raised
            # `ModelJudgementUnavailable` here and ENDED THE RUN on every file
            # after them. The first cloud run is two hours over a network; one
            # blip at one file would have cost every file behind it its answer,
            # which is the coverage loss the constitution forbids for the sake of
            # a record's tidiness. The record stays exact: the failure is already
            # written as its own event and nothing below names a §6.10 reason
            # for it -- `chosen_node_id` stays `None` and step 9 places the file
            # the way a run with no model configured would, §13.5's own fallback.
            # `NeedsConsent` alone still raises: it is not "the call did not
            # happen", it is the gate asking the person a question, and a run
            # that answered it for them would be worse than one that stopped.
            elif not isinstance(result, (CallRefused, PreCallAbstention,
                                         CallFailed, ValidationUnavailable)):
                verdict = _require_verdict(result, call_site=C_PLACEMENT)
                outcome, reason, deferred = transcribe(
                    verdict, assessment=assessment)
                if outcome != PLACE:
                    return _abstention(conn, context, reason=reason,
                                       deferred_stage=deferred)
                # The model chose among P11's candidates; which one it chose is
                # read back through the injected resolver, because `P8Verdict`
                # names a `claim_ref` and not a destination.
                chosen_node_id = inputs.chosen_node_of(verdict)
                if chosen_node_id not in legal_node_ids(
                        conn, plan_version=inputs.plan_version):
                    raise ValueError(
                        f"{chosen_node_id!r} is not a legal destination of "
                        f"{inputs.plan_version!r}. P8 already refuses an invented "
                        "node; reaching here means the resolver disagreed with "
                        "the index, and P11 places nothing on a disagreement"
                    )

    # Step 9.
    if chosen_node_id is None and assessment.abstention_reason is not None:
        return _abstention(conn, context, reason=assessment.abstention_reason)

    node_id = chosen_node_id or assessment.scored[0].node_id
    entry = entry_for(conn, plan_version=inputs.plan_version, node_id=node_id)
    # WHAT THE PLACED NODE ACTUALLY IS, asked once and read four times below.
    #
    # This used to be `chosen_node_id is not None` and it rested on a sentence
    # R-19 made false: "the deterministic path had already declined to call it an
    # exact match, which is the only reason a model was asked". Under Q-A a
    # unique direct match is asked too (`00` Amendments, `104` §13.5), so "a
    # model was asked" no longer says anything about the evidence -- and the
    # record must not get worse for having been checked. A model that confirms
    # the top-ranked candidate on a unique direct match placed an exact fact
    # match, and calling it context-supported would name a fact match that did
    # happen as one that did not.
    #
    # The other direction is what the same predicate closes: when the model
    # chooses a DIFFERENT node, `evidence_type` used to read `direct` off
    # `unique_direct_match` while `confidence_class` said context-supported --
    # one record, two answers. Unreachable before R-19, reachable now.
    direct = (assessment.unique_direct_match
              and node_id == assessment.scored[0].node_id)
    confidence = (assessment.confidence_class if direct
                  else CONTEXT_SUPPORTED_GROUP_MATCH)
    #: `00`:112'S SUPPORT, ON THE FIELD `00`:114 MADE FOR IT. `104` §18.2 gap 14:
    #: "group support null at every writer". This is the writer -- the file went
    #: where it went because the group it belongs to went there -- and P9's own
    #: membership word is copied rather than re-derived. `None` when the file was
    #: not placed by its group's answer, including the member that contradicted it
    #: and was placed singly: that file's home is its own evidence's, and saying
    #: the group supported it would be the post-hoc aggregation this gap closes,
    #: written the other way round.
    group_support = (
        None if chosen_node_id is None or group_answer is None
        or chosen_node_id != group_answer.node_id or contradicts_the_group
        else GroupSupport(group_id=group_answer.group_id,
                          membership=group_answer.membership))
    two = (assessment.two_condition if direct
           else dataclasses.replace(assessment.two_condition,
                                    requires_review=True))
    # `104` R-75. THE MODEL'S OWN REVIEW CLASS, READ AND NEVER OVERWRITTEN.
    #
    # `requires_review` is what separates P8's two acceptances: `accept_direct` and
    # `accept_context_supported` are both placements and `p8_seam.transcribe` says
    # so -- "the difference between them is `requires_review`, which gates
    # `review_policy` and not the outcome". P11 never read it. So a model that
    # confirmed the top node on a unique direct match, and answered
    # `accept_context_supported` because its own evidence was context, kept P11's
    # exact-fact-match `two_condition` and came out `auto_eligible`: the model
    # asked for a look and the record said none was needed.
    #
    # Reachable only since R-19 put a unique direct match through site C at all.
    #
    # OR, NEVER ASSIGNMENT. `104` §13.5 is "model decides, rules validate", and
    # rules that could CLEAR a review the model asked for would be validating in
    # the wrong direction; the deterministic reasons for review stand whatever the
    # model said. An offline run has no verdict and is untouched.
    if verdict is not None and verdict.requires_review:
        two = dataclasses.replace(two, requires_review=True)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version, subject_ref=subject_ref,
        observed_at=observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=PLACEMENT,
        returned_from=returned_from, subject=subject,
        group_plan_id=group_plan_id, outcome=PLACE,
        destination=Destination(node_id=entry.node_id, node_role=entry.node_role),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=entry.depth,
                                     supported_depth=entry.depth,
                                     unsupported_levels=()),
        evidence_type=DIRECT if direct else CONTEXT_SUPPORTED,
        confidence_class=confidence,
        matching_facts=_facts_of(retrieval, entry.node_id),
        group_support=group_support,
        # A model-chosen node need not be one P11 CONTENDED, so the node-local
        # graph may not exist, and claiming anchors it does not have would be
        # evidence the file was never shown to carry.
        #
        # **THIS COMMENT WAS FALSE AND `104` §18.2 GAP 2 NAMES IT.** It read
        # "`allowed_vocabulary` is every legal destination, which is what stops
        # Site C rejecting a correct answer P11's six channels happened to miss"
        # -- true until R-17 narrowed the vocabulary to the ranked shortlist, and
        # left standing for the seven weeks in which the opposite was true: a real
        # folder off the shortlist came back `INVENTED_NODE`. What stops that now
        # is not the vocabulary but the validator, which rejects on `node_exists`
        # and flags membership (`placement_validation._placement_site`).
        #
        # Two ways to reach this line with no graph, and both are real: a node the
        # model named that retrieval never reached at all, and a node step 6
        # ranked below the contenders -- the second of which DOES have a graph,
        # because `_place_one` stopped throwing those away in the same commit.
        graph_anchors=(graphs[entry.node_id].anchors
                       if entry.node_id in graphs else ()),
        conflicts_considered=retrieval.conflicts,
        alternatives=assessment.alternatives,
        two_condition=two, abstention_reason=None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two,
            group_support=group_support,
            unique_direct_match=direct,
            destination_disposition=entry.disposition,
            automatic_move_permitted=automatic_move_permitted),
        explanation=_explain(entry, assessment, retrieval,
                             model_decided=chosen_node_id is not None,
                             gate_refused=gate_refused,
                             refinements=refinements,
                             group_support=group_support,
                             disagreed_with_group=(
                                 group_answer.group_id
                                 if contradicts_the_group
                                 and not group_answer.sits_apart else None),
                             flagged_out_of_group=(
                                 group_answer.group_id
                                 if contradicts_the_group
                                 and group_answer.sits_apart else None)),
        residual=None,
        # `104` R-165. THE SAME PREDICATE THE SENTENCE ABOVE IS BUILT FROM, on a
        # field something can count. `chosen_node_id` is not None exactly when a
        # site-C verdict P8 validated named this node; every other way of reaching
        # this line placed the file on `assessment.scored[0]`, which is §6.10's
        # arithmetic and nobody's judgement. That covers the deterministic path,
        # the offline install, R-74's gate refusal and R-O's refused call alike --
        # four routes to one fact, which is that the rules decided.
        #
        # **AND `104` §18.2 GAP 14 IS A FIFTH ROUTE TO THE FIRST ANSWER.** A member
        # placed by its group's answer has `chosen_node_id` set and made no call of
        # its own: the model decided, in the one call that took the group, and a
        # row that said `rule` about it would credit §6.10's arithmetic with a
        # judgement no arithmetic reached.
        decided_by=DECIDED_BY_MODEL if chosen_node_id is not None
        else DECIDED_BY_RULE,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later placement of the same file version supersedes "
                         "this one (§8.2)",
                  component_version=component_version, observed_at=observed_at)


@dataclass(frozen=True)
class _Context:
    """Everything an abstention needs, gathered once so no builder re-derives it."""

    subject: object
    subject_ref: str
    inputs: PipelineInputs
    privacy: object
    retrieval: object
    assessment: object
    graphs: dict
    automatic_move_permitted: bool
    group_plan_id: str | None
    returned_from: str | None
    component_version: str
    observed_at: str


def _facts_of(retrieval, node_id: str) -> tuple:
    """This file's facts that matched THIS node, contender or not.

    `104` §18.2 gap 2. The set-aside half of the shortlist is searched too, and it
    has to be: a folder a step-6 rule ranked below the contenders is one the facts
    reached -- `_without_kind_only_moves` and `_a_folder_made_for_this_keeps_it`
    only ever set aside a candidate WITH `matching_facts` -- so reading `()` for a
    node the model placed the file on would write a decision claiming no fact
    matched when the run has the facts in hand.
    """
    for candidate in retrieval.candidates:
        if candidate.node_id == node_id:
            return candidate.matching_facts
    for item in retrieval.set_aside:
        if item.candidate.node_id == node_id:
            return item.candidate.matching_facts
    return ()


def _explain(entry, assessment, retrieval, *, model_decided: bool = False,
             gate_refused: bool = False,
             refinements: frozenset[str] = frozenset(),
             group_support=None,
             disagreed_with_group: str | None = None,
             flagged_out_of_group: str | None = None) -> str:
    """§6.4 and §6.11: state the actual basis, claim no evidence the file lacks.

    **AND WHICH SUBJECT THE JUDGE WAS ACTUALLY ASKED ABOUT** (`104` §18.2 gap 14).
    A member placed by its group's answer was never asked about on its own, and a
    record that said only "chosen by the hierarchical destination judge" would let
    a person read that as a judgement about this file's own evidence. So the
    sentence says the group decided it; and where the file DISAGREED with its
    group and was placed singly, it says that too, because a plan that quietly
    filed one file of a packet somewhere else owes the person the reason.

    `gate_refused` is `104` R-74's half of §6.4, and it is the ACTOR that has to be
    right. Nothing was sent about this file, no model saw it and nobody was asked;
    the rules placed it on evidence the rules can defend. R-28's rule is that a
    record must not say the model or the person when the rules decided, so the
    sentence names the rules and the gate, and `model_decided` is `False` beside
    it because no judge was consulted.

    **AND WHEN THE MODEL PICKED A FOLDER THE RULES HAD RANKED BELOW, THE PERSON IS
    TOLD WHAT THE RULES SAID** (`104` §18.2 gap 2). That sentence is the whole
    safety of turning four deletions into four rankings: `Desktop/AP world` and
    the law student's `Coursework/Fall2026/report card` can now be chosen, and the
    plan that offers to move a file there prints the reason the engine ranked the
    folder below the others, in the same words the model read, beside a placement
    that already carries `requires_review` (a set-aside node is never
    `assessment.scored[0]`, so `_place_one`'s `direct` is False and the review flag
    is set). Read off the retrieval rather than passed in, because the record must
    not be able to disagree with the shortlist that was sent.
    """
    parts = [f"{entry.display_label} expects "
             + (", ".join(f"{field} = {value}"
                          for field, value in entry.expected_values)
                or "no stated value")]
    for item in retrieval.set_aside:
        if item.candidate.node_id == entry.node_id:
            parts.append(item.because)
            break
    if entry.node_id in refinements:
        # `00`'s amendment of line 22 separates refinement from removal, and a
        # person reading the plan is owed the same distinction: nothing is being
        # taken out of the arrangement they built, the file is going one level
        # deeper inside it. Said in their words, not "refinement" -- `84` §6.
        parts.append("inside the folder this file is already in, so nothing "
                     "leaves the arrangement you have")
    if flagged_out_of_group is not None:
        # P9's finding, said in the person's words. Not "outlier_flag": `84` §6.
        parts.append(
            f"this file was set apart from the {flagged_out_of_group} group when "
            f"the group was formed, so it was judged on its own with the folder "
            f"that group went to offered and the disagreement on the record")
    elif disagreed_with_group is not None:
        parts.append(
            f"this file's own stated values rule out the folder its group "
            f"({disagreed_with_group}) was placed in, so it was judged on its "
            f"own with that folder offered and the disagreement on the record")
    if model_decided and group_support is not None:
        parts.append(
            f"chosen by the hierarchical destination judge for the whole of "
            f"{group_support.group_id}, which this file belongs to, and "
            f"validated by P8")
    elif model_decided:
        # The user is entitled to know a model was involved: §6.11 says a direct
        # and a context-supported placement "should not demand the same level of
        # trust", which a reviewer can only apply if the record says which it is.
        parts.append("chosen by the hierarchical destination judge from P11's "
                     "legal candidates, and validated by P8")
    if gate_refused:
        # `104` R-74 and `00`'s amendment of line 110: the model decides whenever
        # one can be asked, and the deterministic path is the fallback when one
        # cannot. Said in the rules' own voice -- no "you", no model -- because
        # that is who decided.
        parts.append("placed by the rules on this file's own direct match, "
                     "because nothing about it may be assembled for a model "
                     "(§8.4) and the deterministic path is what remains")
    if retrieval.conflicts:
        # Named first, counted always. The named ones are the branches something
        # was pulling this file towards; the count is every branch the conflict
        # ruled out. A sentence that listed all of them would name every folder in
        # the tree on a corpus like `planning/58-SCALE-STRESS.md` §2's, which is
        # the failure that document records for §5.9's warnings under its own
        # heading -- "the warning list outgrows the tree it describes".
        named = [node for conflict in retrieval.conflicts
                 for node in conflict.suppressed_node_ids]
        total = sum(conflict.suppressed_node_count
                    for conflict in retrieval.conflicts)
        if named:
            unnamed = total - len(named)
            parts.append(
                "ruled out " + ", ".join(named)
                + (f" and {unnamed} further destination"
                   f"{'' if unnamed == 1 else 's'}" if unnamed else "")
                + " on conflicting evidence")
        else:
            parts.append(
                f"ruled out {total} destination{'' if total == 1 else 's'} on "
                "conflicting evidence, none of which this file's evidence "
                "reached")
    parts.append(
        f"support {assessment.two_condition.support_score:.2f} against a "
        f"threshold of {assessment.two_condition.support_threshold:.2f}")
    return "; ".join(parts) + "."


def _supported_homes(context: _Context) -> tuple[str, ...]:
    """The destinations that cleared §6.10's support threshold on their own."""
    threshold = context.assessment.two_condition.support_threshold
    return tuple(item.node_id for item in context.assessment.scored
                 if item.support_score >= threshold)


#: `104` R-M. WHAT EACH ABSTENTION MEANS, in the person's words.
#:
#: The screen used to end every one of these with "No legal destination cleared
#: §6.10's conditions ({reason})" -- a paragraph number and an engine word, on the
#: screen of somebody looking at their own folder. Measured by a fresh session on
#: a 52-file corpus: 31 occurrences of "§6.10's" on one report.
#:
#: **The section reference is not lost by coming off the screen.** It is in the
#: RECORD, structurally rather than as prose: `PlacementDecision.two_condition` IS
#: §6.10's measurement -- support, margin, the threshold and the policy that set
#: them -- `privacy` is §8.4's class, and `abstention_reason` is the closed code
#: for which condition failed. The person reads the sentence; a lead reads the row.
#:
#: One sentence per member of `ABSTENTION_REASONS`, and `_abstention_explanation`
#: falls back to the general one for a member added without a sentence, so a new
#: code can never reach a person as a bare word.
REASON_IN_WORDS: Mapping[str, str] = MappingProxyType({
    NO_SUPPORTED_DESTINATION:
        "No folder in this plan matched it well enough to be worth proposing.",
    LOW_MARGIN:
        "Two folders in this plan fit it about equally well, so picking one "
        "would have been a guess rather than a decision.",
    SEMANTIC_ONLY:
        "The only thing linking it to a folder was that they read alike, which "
        "is not enough on its own to move a file.",
    GENERIC_HUB_ONLY:
        "The only thing it shares with a folder is a word many of your files "
        "share, which says nothing about where this one belongs.",
    CONFLICTING_FACTS:
        "What this run read about it points at more than one folder, and the "
        "readings disagree with each other.",
    NO_SHARED_BRANCH:
        "The files it belongs with are not all under one branch, so there is no "
        "single home to propose for them.",
})


def _abstention_explanation(context: _Context, *, reason: str) -> str:
    """What the person is told, which is not always what the machine recorded.

    Two abstentions are correct decisions that the default sentence describes
    falsely, and `planning/59-FINAL-UX-EVALUATION.md` finds both.

    * `multiple_supported_homes` (§3a): two legal destinations DID clear §6.10's
      support condition. "No legal destination cleared" is simply untrue of this
      file, and a user told it will distrust the extraction rather than make the
      choice that is actually theirs to make.
    * `privacy_blocked` (§3c, finding 9): the product declined to assemble a
      dossier ON PURPOSE. `00` on this material -- "sensitive personal material
      is not the same thing as `Numbers.app`" -- and a person told their passport
      failed to place concludes the product is broken rather than careful.

    Every other reason keeps the sentence it had. A correct abstention over thin
    evidence IS "no legal destination cleared §6.10's conditions", and giving all
    of them a reassuring new voice would erase the one honest report of a genuine
    evidence failure.
    """
    if reason == MULTIPLE_SUPPORTED_HOMES:
        homes = _supported_homes(context)
        return (
            f"{', '.join(homes)} each match this file well enough on their own, "
            "and nothing in the evidence separates them, so it has more than "
            "one supported home. Nothing moved: which one is its home is a "
            "choice about your material, not a gap in the evidence."
        )
    if context.privacy.protected:
        # PROTECTED OUTRANKS EVERY OTHER TRUE SENTENCE, and this check moved above
        # the reason switch rather than living inside `PRIVACY_BLOCKED`.
        #
        # Found when `branch_expectations` landed: a branch that now states
        # `subject = PHYS1401` is contradicted by a passport whose own `subject`
        # is its document number, so the file abstained on `conflicting_facts` and
        # took the §6.10 sentence at the bottom of this function. Nothing leaked
        # and the outcome was unchanged -- but the person was told their passport
        # had competing destinations, which describes a subordinate mechanism,
        # when the governing fact is that this product does not file protected
        # material at all. `66` §4 forbids exactly that collapse.
        #
        # It is not a choice between two equally true sentences. One of them names
        # the rule that decided the outcome; the other names a step that ran on
        # the way there and would still have refused if it had agreed.
        return (
            "This file is protected material, so nothing about it was "
            "assembled for a model and it was left exactly where it is. That "
            "is a deliberate decision about sensitivity, not a failure to "
            "find a destination."
        )
    if reason == PRIVACY_BLOCKED:
        if is_unclassified(context.privacy):
            # The third cause, and the one a corpus produces most. Neither of the
            # sentences below is true of it: nothing marked this file sensitive,
            # and the evidence never got as far as being weighed. `00` --
            # "sensitive personal material is not the same thing as `Numbers.app`"
            # -- and a file nothing could read is a third thing again.
            #
            # It used to end that thought with "nothing has been able to read
            # enough of it", and `65` §4.1 caught that on a live run: all four
            # files had a `direct` fact in `file_facts` and zero rows in
            # `classifications`. Reading is the step that WORKED and it was the
            # step the sentence blamed. `66` §4 forbids it -- "protected",
            # "unreadable", "unsupported format", "still indexing" and "no strong
            # match" may never share one message, and that was two of them
            # sharing one.
            #
            # P11 knows nothing classified this file. Whether it was READABLE is
            # P4's `extraction_runs` (B1: THE extraction-outcome record for the
            # whole system), which P11 does not read and must not guess at. So
            # the sentence names the step that stopped and claims nothing about
            # the one before it.
            return (
                "This file has not been classified -- nothing has yet said what "
                "kind of material it is -- so it was not shown to a model and "
                "nothing moved. It is waiting for you to say what it is, not "
                "marked sensitive and not judged on thin evidence."
            )
        # `route_in_force` and not this file's own route: the sentence below says
        # NO MODEL IS SET UP, which is a fact about the deployment. A protected
        # file on a machine with a local model reaches here too, and its route is
        # `None` while a model very much is set up -- it takes the last sentence,
        # which names the settings rather than the absence.
        if context.inputs.route_in_force() is None:
            # `104` R-118's third sentence. The only reason left for this state
            # is the operation mode, and the mode forbids the CLOUD: a model on
            # this device could be asked, and none is set up. The sentence
            # below claims the settings forbid any model, which stopped being
            # true the day a local one could be given a dossier.
            return (
                "Deciding this file needed a model, and this folder's privacy "
                "settings only let one that runs on this device be asked about "
                "it; none is set up. Nothing about it left this device and "
                "nothing moved; the evidence is retained."
            )
        return (
            "Deciding this file needed a model, and this folder's privacy "
            "settings do not let one be asked about it. Nothing about it left "
            "this device and nothing moved; the evidence is retained."
        )
    return (
        f"{REASON_IN_WORDS.get(reason, 'No folder in this plan was a supported home for it.')} "
        "Declining to place it is the right answer rather than a failure: "
        "nothing moved, and everything this run read about it is kept."
    )


def _abstention(conn: sqlite3.Connection, context: _Context, *, reason: str,
                deferred_stage: str | None = None) -> PlacementDecision:
    """§6.10: a correct abstention is a successful outcome, and is recorded as one.

    `deferred_stage` is set only when `reason` is `budget_deferred`, and the record
    enforces the pairing both ways. §8.6 requires a ceiling-truncated run to render
    differently from "I looked and could not tell", and a deferral recorded as a
    plain abstention is exactly the "understood and found unimportant" impression
    the design forbids.
    """
    if (reason == BUDGET_DEFERRED) != (deferred_stage is not None):
        raise ValueError(
            "a budget deferral names the stage it was cut short at, and only a "
            "budget deferral has one (§8.6)"
        )
    inputs = context.inputs
    # **THE ONE PLACE "this file was not placed" IS DECIDED, AND SO THE ONE PLACE
    # "...and here is the question instead" BELONGS.** It was tried at step 9
    # first, on the reasoning that a question replaces §6.10's abstention. On a
    # real 199-file corpus that branch was reached four times: 181 of the 186
    # abstentions are `privacy_blocked`, raised at step 7 before step 9 exists.
    # A hook that fires on 2% of the case it was written for is a hook that is
    # not wired, and it looked wired.
    #
    # WHICH files are worth a person's attention is the caller's, not this
    # package's: `ask_about_file` answers `None` for everything it has nothing to
    # ask about, which on that corpus is 175 of the 179 unprotected abstentions.
    # §6.9 already takes its policy from the caller the same way.
    #
    # A BUDGET DEFERRAL IS NEVER A QUESTION. §8.6 requires a ceiling-truncated run
    # to render differently from "I looked and could not tell", and a question is
    # the strongest possible claim that the product looked. The person's answer
    # would also be wasted: the run stopped early, so the next one resumes and
    # decides it without them.
    if reason != BUDGET_DEFERRED:
        asked = inputs.ask_about_file(context.subject)
        if asked is not None:
            question, options = asked
            return _asking(conn, context,
                           ask=Ask(question=question, options=tuple(options)))
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version, subject_ref=context.subject_ref,
        observed_at=context.observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=context.observed_at, origin_stage=PLACEMENT,
        returned_from=context.returned_from, subject=context.subject,
        group_plan_id=context.group_plan_id, outcome=ABSTAIN,
        destination=None, return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=context.retrieval.conflicts,
        alternatives=context.assessment.alternatives,
        two_condition=context.assessment.two_condition, abstention_reason=reason,
        deferred_stage=deferred_stage, privacy=context.privacy,
        review_policy=review_policy_for(
            privacy_state=context.privacy,
            two_condition=context.assessment.two_condition, group_support=None,
            unique_direct_match=False, destination_disposition=None,
            automatic_move_permitted=context.automatic_move_permitted),
        explanation=_abstention_explanation(context, reason=reason),
        residual=None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later decision about the same file version "
                         "supersedes this abstention (§8.2)",
                  component_version=context.component_version,
                  observed_at=context.observed_at)


def _asking(conn: sqlite3.Connection, context: _Context, *,
            ask: Ask) -> PlacementDecision:
    """The abstention this run turned into a question. §6.10's third answer.

    **What this changes and what it does not.** Nothing about the file moves, and
    nothing about the evidence is claimed: the two-condition figures, the
    alternatives and the conflicts are the assessment's own, carried through
    unaltered, because asking is not a second opinion about the evidence -- it is
    the admission that the evidence ran out. `requires_review` was already true on
    every record that reaches here.

    What it changes is that the person can see it and answer it. An abstention says
    "I could not tell" to a report; `ask_user` says "I could not tell, and here is
    the question" to a person, and `00`'s standing complaint about this product was
    that it had the first and not the second.

    `abstention_reason` is deliberately absent, and the record enforces that: an
    `ask_user` carrying one would be two outcomes in one row, and the reason a file
    was not placed would read as the reason it was asked about.
    """
    if context.privacy.protected:
        raise ProtectedMaterialIsNotAQuestion(
            "P7 marked this file protected, and an `ask_user` decision is a "
            "REQUEST FOR ATTENTION: a review surface lists what it holds, and "
            "`00`:201 says a visible list of protected specifics may not be safe "
            "to have on a screen somebody else can see. The caller's policy is "
            "expected to exclude protected material before it gets here; this is "
            "the second lock, because the first one is a lambda in the "
            "composition root and the cost of it being wrong is a passport on a "
            "screen. Refused rather than downgraded to an abstention: a policy "
            "that reaches here is broken and has to be found, not worked around"
        )
    inputs = context.inputs
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version, subject_ref=context.subject_ref,
        observed_at=context.observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=context.observed_at, origin_stage=PLACEMENT,
        returned_from=context.returned_from, subject=context.subject,
        group_plan_id=context.group_plan_id, outcome=ASK_USER,
        destination=None, return_target=None, marked_state=None, ask=ask,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=context.retrieval.conflicts,
        alternatives=context.assessment.alternatives,
        two_condition=context.assessment.two_condition, abstention_reason=None,
        deferred_stage=None, privacy=context.privacy,
        review_policy=review_policy_for(
            privacy_state=context.privacy,
            two_condition=context.assessment.two_condition, group_support=None,
            unique_direct_match=False, destination_disposition=None,
            automatic_move_permitted=context.automatic_move_permitted),
        explanation=(
            "No destination in this plan was supported well enough to decide, and "
            "nothing this run could read says what this file is. That is a "
            "question for you rather than a judgement to make on thin evidence; "
            "nothing has moved and the evidence is retained."),
        residual=None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later decision about the same file version "
                         "supersedes this question (§8.2)",
                  component_version=context.component_version,
                  observed_at=context.observed_at)


# --- step 7: the hierarchical destination judge -----------------------------------


def _not_asked(conn, *, call_site: str, subject, observed_at: str,
               because: str) -> PreCallAbstention:
    """One file the model is not asked about, recorded and handed back (R-136).

    `PreCallAbstention` is P8's own record of a call that does not happen, and
    `NOT_ELIGIBLE_FOR_MODEL` is P8's own word for it: `eligibility.
    not_reserved_for_llm` returns exactly this pair for a subject the model is not
    reserved for. §6.10's abstention reasons stay untouched -- this is not one of
    them and does not pretend to be, which is what `_require_verdict` says in its
    own words about naming a reason nothing reached.

    `because` is the sentence each raise carried, kept at the call sites and NOT
    put on the record: `PreCallAbstention` is P8's closed three-field shape --
    reason, call site, subject -- and widening it here would be P11 authoring a
    record another part owns. Which of the two states a file was in is readable
    from the file itself, since one has no settled fact and the other has no
    retrievable destination.
    """
    del because
    subject_ref = subject_ref_of(subject)
    abstention = PreCallAbstention(
        reason=NOT_ELIGIBLE_FOR_MODEL, call_site=call_site,
        subject_ref=subject_ref)
    record_unbuilt_call_abstention(conn, abstention, observed_at=observed_at)
    return abstention


def _require_verdict(result, *, call_site: str) -> P8Verdict:
    if isinstance(result, P8Verdict):
        return result
    raise ModelJudgementUnavailable(
        f"{call_site} came back with {type(result).__name__}, which is not a "
        "judgement about this file. §6.10's abstention reasons are a closed set "
        "and none of them means 'the call did not happen'; naming one would "
        "record a conclusion nothing reached"
    )


#: THE WORD EVERY UNRATIFIED TEMPLATE ID CARRIES. `104` §7 Phase 1 step 6 runs C
#: and D in observe mode -- the call happens, the dossier, response and verdict are
#: recorded, and nothing is applied -- until Phase 3 fixes R-15 and R-16.
#:
#: READ OFF THE PROMPT'S OWN FIELD, which the loader sets from the packet
#: manifest. Not a set of site names imported from the composition root, which
#: would point the dependency the wrong way -- P11 would learn which sites are
#: provisional from the file that assembles it. And not a test on the id string,
#: which would make the invariant depend on a naming habit and start applying the
#: moment a draft was renamed.
#:
#: A site running under text nobody ratified must not act on the answer. Ratify
#: the text, the loader sets the field, and the site starts applying on the same
#: run.


def _observed_only(result, *, prompt):
    """The model's answer, recorded and then set aside. §6.12's abstention path.

    RATIFICATION IS WHY, and it is the whole of why: prompt text is the owner's
    to approve, and a verdict produced under text nobody approved is a reading of
    a question the product has not agreed to ask. R-15 was the second reason and
    is gone -- `_invented_dimension` now grounds a level's value in the file's own
    evidence rather than looking it up in the legal node ids -- and R-16 is still
    that shape at B.

    The verdict is REWRITTEN rather than dropped, and the difference matters: the
    real one is already on disk, written by `run_call` before this returns, so what
    changes is only what P11 does next. An `ABSTAIN` outcome takes both callers
    down the abstention path they already have -- `chosen_node_of` and
    `residual_action_of` are never consulted, and no move plan, placement decision
    or residual action is written.

    Not a `Refusal`: the gate permitted this and P7 refused nothing, and a refusal
    row would say the door stopped a call the door allowed.
    """
    if getattr(prompt, "ratified", False):
        return result
    if not isinstance(result, P8Verdict):
        # A refusal, a failed call or a missing capability is already an outcome
        # P11 applies nothing to. Rewriting one would hide why it happened.
        return result
    return dataclasses.replace(
        result, outcome=P8_ABSTAIN, disposition=P8_ABSTAIN, may_propose=False)


#: What a `candidate` item's role makes it at site D. The C draft names one kind of
#: offered folder (`candidate`); the D draft names two, and the difference is the
#: one the person made: a `residual_area` is a home for material that belongs to no
#: folder in particular (`00`:120), a `branch` is a branch of the main tree that a
#: return sends the file back to (`00`:107). P11 does not decide which a node is --
#: P10's `node_role` already did -- so this is a lookup and not a judgement.
#: The kinds are `p8_seam`'s, where `snapshot_observation_keys` excludes them from
#: the evidence snapshot: a folder is a destination the model may answer with and
#: never a citation, so the producer and the exclusion read one set of names.
_D_ITEM_KIND: dict[str, str] = {RESIDUAL_ROLE: RESIDUAL_AREA_ITEM}


def _offered_items(conn, *, plan_version: str, node_ids, call_site: str,
                   own_folder_node_id: str | None,
                   ranked_below: Mapping[str, str] | None = None,
                   ) -> tuple[EvidenceItem, ...]:
    """`00`:105's destination profile for every node the model may answer with.

    **`104` R-17 and packet §7 G3.** The dossier used to carry the node ids alone:
    "the live dossier carries `allowed_vocabulary` = legal node ids (minted,
    opaque) and nothing about them: no label chain, no expected values, no known
    document types, no 'this is the file's own folder'". Both drafts DESCRIBE these
    items -- "its `evidence_ref` is an identifier from `allowed_vocabulary`, and its
    `location` describes that folder, from the top of the tree down to the folder
    itself, with the values a file in it is expected to carry" -- so the text the
    owner is asked to ratify was true of the bench's dossier and false of the
    product's. This is the builder change G3 names, and it is a READ of P10's
    profile through `index.node_profile`; P11 authors no line of it.

    One `entries_for_plan` per call, which is one query: the profile needs the
    ancestors' labels and how many folders stand beside each candidate, and neither
    is answerable from an entry alone.

    **`ranked_below` IS `104` §18.2 GAP 2'S CHANNEL, AND IT IS DELIBERATELY NOT A
    NEW KEY.** The C template's own inventory is closed -- "the dossier has these
    keys and no others" -- and a `candidate` item's shape is closed with it: an
    `evidence_ref`, a `kind`, and a `location` that "describes that folder, from
    the top of the tree down to the folder itself, with the values a file in it is
    expected to carry, and sometimes what it holds". A sixteenth dossier key, or a
    seventh field on an item, would be the model instructed to read something the
    text it was given never mentions.

    So the rule's sentence goes INSIDE `location`, which is where the one other
    non-descriptive thing the model is told about a folder already goes: "the file
    sits in this folder now" (`index.node_profile`'s `own_folder`), which the
    template names in that same paragraph and which the model reads without any
    key of its own. The sentence is a description of the folder's standing in this
    shortlist, in the same string, separated by the same `|`.

    **The owner is owed one sentence of prompt text for this**, and it is written
    out in the report rather than applied here: the template is the library's and
    a builder that writes something the ratified text does not describe is the
    same defect as a key it does not name, one layer down. What stops that being a
    silent change in the meantime is that the sentence says only what was noticed,
    never what to conclude -- a folder ranked below is still on `allowed_vocabulary`
    and the model may answer with it.
    """
    ranked_below = ranked_below or {}
    entries = entries_for_plan(conn, plan_version=plan_version)
    by_id = {entry.node_id: entry for entry in entries}
    beside = sibling_counts(entries)
    items: list[EvidenceItem] = []
    for node_id in node_ids:
        entry = by_id.get(node_id)
        if entry is None:
            # Offered by a caller and absent from the index. `legal_node_ids` and
            # this read the same rows, so this is unreachable today; describing a
            # node the index does not hold would be P11 inventing a folder.
            continue
        kind = (CANDIDATE_ITEM if call_site == C_PLACEMENT
                else _D_ITEM_KIND.get(entry.node_role, BRANCH_ITEM))
        profile = node_profile(
            entry, siblings=beside.get(entry.parent_node_id, 1),
            own_folder=entry.node_id == own_folder_node_id)
        because = ranked_below.get(entry.node_id)
        if because:
            profile = f"{profile} | {because}"
        items.append(EvidenceItem(
            evidence_ref=entry.node_id, kind=kind,
            location=profile,
            # A folder is not an excerpt of the file. It carries no span, it is
            # never in `released_evidence`, and P7 releases none of it.
            excerpt_span=None, reliability_state=DIRECT,
            basis=P8_DIRECT_ANCHOR))
    return tuple(items)


def _residual_areas(conn, *, plan_version: str) -> tuple[str, ...]:
    """`00`:120's approved residual library, in the index's own order.

    The D draft says every id in `allowed_vocabulary` is described in
    `evidence_items`, so the offer and the descriptions are one list. These are the
    homes §7's own screen offers; the branches a return goes back to come from
    retrieval beside them.
    """
    return tuple(entry.node_id
                 for entry in entries_for_plan(conn, plan_version=plan_version)
                 if entry.node_role == RESIDUAL_ROLE)


def _accepted_group_items(group_ids) -> tuple[EvidenceItem, ...]:
    """The groups the person accepted this file into, as the drafts describe them.

    `00`:111's own example rests on this: `HW 3.pdf` is placed under a course it
    never names, because an accepted group carries the level the file's text does
    not. `_invented_dimension` exempts a `context` level from grounding for exactly
    that reason, and the exemption's docstring names the absence this closes --
    "the dossier carries no group values to ground it against (packet §7 G3)".

    Every id here comes from `accepted_memberships_of`, so every one of them IS
    accepted; the drafts' other case (a group the file was merely retrieved as a
    candidate member of) has no producer at this seam and no item is written
    claiming otherwise.
    """
    return tuple(
        EvidenceItem(
            evidence_ref=group_id, kind=ACCEPTED_GROUP_ITEM,
            location="a group the person accepted this file into",
            excerpt_span=None, reliability_state=POSSIBLE,
            basis=P8_CONTEXT_SUPPORTED)
        for group_id in group_ids
    )


def _graph_items(conn, *, subject, plan_version: str, graphs, related_files,
                 offered, target_locality) -> tuple[EvidenceItem, ...]:
    """`104` §18.2 gap 12: the node-local typed graph, IN THE DOSSIER at last.

    `00`:110 lists what a placement dossier carries and "graph anchor evidence"
    is on it, between the accepted group memberships and the top legal
    candidates. It was the one entry with no producer: the graph was built at
    step 4, read for two flags, recorded on the decision, and never shown to the
    model -- so a file whose relationship to another file IS the reason it
    belongs somewhere was judged as though that relationship did not exist, and
    the model could not have cited it if it had wanted to.

    **REFERENCE-ONLY, AND UNCITABLE, WHICH IS THE SAME SHAPE AS AN ACCEPTED
    GROUP.** The item carries a kind, a location, no span and a basis, and its
    `evidence_ref` is this function's own address for the edge. Nothing about it
    is in `released_evidence`, so `validation._check_citation` answers
    `CITATION_NOT_IN_DOSSIER` to a citation of it exactly as it does to a
    citation of a group -- P8 gains no check, which is gap 12's own instruction,
    and the ratified C text already says the rule in its own words ("a candidate,
    a group or a conflict is not evidence and cannot be cited"). **The owner is
    owed one sentence of that text** naming this fourth kind, written out in the
    report rather than applied here: the template is the library's, and the
    dossier's own inventory of keys is unchanged.

    **WHAT NAMES THE OTHER FILE.** Site C releases no filename -- `model_facts.
    may_be_released` refuses a `filename`-zone reading to both localities,
    checked again for this -- so the other end is named the way `00`:112's group
    dossier names a member: by its accepted facts, through `cli.evidence_for`'s
    `to_describes`, which carries only fields P6 calls destination dimensions and
    only where the door would release a citation of them under the strictest
    target. A neighbour with nothing describable gets NO ITEM: a reference to a
    file the dossier may not describe is a reference to nothing.

    **AND THE GATE IS ASKED PER FILE THIS DESCRIBES.** `may_assemble_dossier` is
    §8.4's own per-file predicate, and it is asked here about the NEIGHBOUR
    against the target this call was actually routed to -- the same two lines
    `_one_destination_every_member_may_use` runs per group member. A protected or
    held neighbour is refused for both localities and is never described to any
    model; a neighbour this run may not describe to the cloud is dropped from a
    cloud dossier and kept in a local one. Nothing crosses that would not cross
    for that file's own call to the same target.

    **THE UNION OF THE GRAPHS, ONE ITEM PER EDGE.** One edge can survive in
    several candidates' neighbourhoods, and the model does not need it told
    several times; what it needs is which of the offered folders the other file
    is already accepted in, so those node ids are collected into the one item's
    `location`. They are ids the model already holds -- every one is on
    `allowed_vocabulary` and described by a `candidate` item -- so this adds a
    relationship and no new vocabulary.

    §8.6's two ceilings are already spent by the time this runs: the items are
    built from `NodeLocalGraph.anchors`, which is what survived
    `max_candidate_cluster_size` and `max_local_graph_neighborhood`. No count of
    its own is invented here.

    The `evidence_ref` carries two `file_id`s in the clear, and that is
    `wire_handles.wire_ref`'s own rule rather than an oversight: it keys a
    reference only when it is a P4 `observation_key`, because "a `file_id` is
    `uuid.uuid4()` ... derived from nothing, inverting to nothing", and a node id
    already crosses the same way on every `candidate` item.
    """
    described = {edge["to_file_id"]: edge.get("to_describes")
                 for edge in related_files or ()}
    hashes = {edge["to_file_id"]: edge.get("to_content_hash")
              for edge in related_files or ()}
    allowed = set(offered)
    reached: dict[tuple[str, str, str], list[str]] = {}
    for node_id, graph in (graphs or {}).items():
        for anchor in graph.anchors:
            key = (anchor.edge_type, anchor.to_file_id, anchor.anchor_file_id)
            names = reached.setdefault(key, [])
            if node_id in allowed and node_id not in names:
                names.append(node_id)
    items: list[EvidenceItem] = []
    permitted: dict[str, bool] = {}
    for (edge_type, other, anchor_file_id), node_ids in reached.items():
        summary = described.get(other)
        content_hash = hashes.get(other)
        if not summary or not content_hash or other == subject.file_id:
            continue
        if other not in permitted:
            permitted[other] = may_assemble_dossier(
                privacy_state_for(conn, file_id=other,
                                  content_hash=content_hash,
                                  plan_version=plan_version),
                target_locality=target_locality)
        if not permitted[other]:
            continue
        where = (f"already accepted in {', '.join(node_ids)}" if node_ids
                 else "not accepted in any folder on this list")
        items.append(EvidenceItem(
            evidence_ref=f"edge:{edge_type}:{anchor_file_id}:{other}",
            kind=GRAPH_EDGE_ITEM,
            location=" | ".join((
                f"a {edge_type.replace('_', ' ')} relationship to another file",
                f"that file's accepted facts: {summary}",
                where,
                f"found by {EDGE_PRODUCER[edge_type]}")),
            excerpt_span=None, reliability_state=POSSIBLE,
            basis=P8_CONTEXT_SUPPORTED))
    return tuple(items)


def _judge_with_model_steps(conn, *, subject, inputs: PipelineInputs, retrieval,
                            evidence, call_site: str, observed_at: str,
                            ranked: tuple[str, ...] = (),
                            set_aside: tuple[SetAside, ...] = (),
                            own_folder_node_id: str | None = None,
                            route_pair: object | None = None,
                            graphs=None):
    """§6.12 step 7, and step 8 with it. P11 assembles the REQUEST, never a check.

    **`104` §18.15: A GENERATOR, AND THE ONE `yield` IS THE SOCKET.** Every line
    below reads or writes the database and stays on the thread that owns it, in the
    order it is written here; what the caller may run elsewhere is the round trip
    `call_placement_steps` hands up. Read it as the straight line it still is.

    **THE SUBJECT MAY BE A GROUP** (`104` §18.2 gap 14, `00`:112). Everything below
    is about "the subject", and three lines used to read `subject.file_id` as
    though there were always one: the learning pair, the `basis_key` a past
    rejection is filed against, and the route. A group subject carries no
    `file_id`, so each of them now asks the subject what it is -- `learning_scope`
    is `group` beside the group id exactly as site B's own `CallDependencies`
    spells it, and the route is the one destination `place_group` has already
    proved every member may use, handed over in `route_pair` rather than looked up
    a second time. A second lookup would be a second answer to "where may this
    call go", asked after §8.4's gate had answered the first.

    Everything here is either P11's own answer or a caller injection. The four
    Site C authorities come from `p8_seam.placement_authorities`; the fifteen Site
    C checks stay in `llm_harness/placement_validation.py` and P11 spells none of
    their reason codes.

    `allowed_vocabulary` is the SHORTLIST: the folders this file's own evidence
    reached, ranked, every one of them described. It is set here rather than taken
    from the caller's `CallDependencies`, because a caller-supplied vocabulary is a
    caller-supplied answer to "which nodes may this file go to", which is the
    index's question and the scores'.

    **AND IT IS NO LONGER A WALL** (`104` §18.2 gap 2). Site C used to reject any
    destination outside this list as `INVENTED_NODE`, which made a SHORTLIST into
    a set of legal answers -- so a real, frozen, approved folder that P11's six
    channels happened to miss came back to the person as an invention. `00`'s
    amendment of 2026-09-05 says what a rejection is for: "deterministic validation
    rejects only a structurally invalid answer: A NODE THAT IS NOT IN THE FROZEN
    TREE, or a cited fact that is not in the evidence". Membership of the list P11
    chose to show is not that sentence. `placement_validation._placement_site` now
    asks `node_exists` first and rejects on it; a real node off this list is
    flagged `INVENTED_NODE` and sent to a person, and only a node the frozen tree
    does not contain is refused.

    **IT WAS `sorted(legal_node_ids(...))`, WHICH IS `104` R-17 AND PACKET G3.**
    Every legal node in the plan, alphabetically, with nothing said about any of
    them. `00`:110 asks for something narrower and richer -- "the small set of TOP
    LEGAL DESTINATION CANDIDATES, each candidate's node profile" -- and `104` §13.5
    says who ranks them: "Deterministic scores rank and shortlist the candidates
    the model is shown... A unique direct match is the top-ranked candidate, not a
    bypass." So `ranked` is `Assessment.scored`'s order, winner first, and
    `_offered_items` describes every entry on it.

    **`set_aside` IS THE REST OF THAT SHORTLIST** (`104` §18.2 gap 2, and gap 11's
    first half). `ranked` is what step 6's four rules left CONTENDING; `set_aside`
    is what they moved below -- the shallower approved parent, the person's-folder
    duplicate, the folder whose only agreement is a kind or a period -- each one
    ranked among its own kind by `_ranked_set_aside` and described by
    `_offered_items` with the rule's sentence inside its `location`. The rules keep
    their ordering and lose their veto, which is `00`'s amendment in one line:
    "Deterministic scores RANK AND SHORTLIST the candidates the model is shown."

    **THE BOUND IS THE ONE §8.6 ALREADY SET AND NO NUMBER IS INVENTED HERE.** Every
    entry on both halves came out of `retrieve`, whose candidate list is cut to
    `limits.max_retrieved_neighbors` (`retrieval.retrieve`'s `ordered` slice) --
    P11's own §8.6 ceiling, read from P1 by `config.placement_limits` and never
    defaulted. Setting a candidate aside cannot grow the offer past what retrieval
    already handed over, so the shortlist is bounded by a configured ceiling rather
    than by a rule deleting the folders it disagrees with; the dossier's own
    `max_dossier_tokens` and its reduction rungs bound the BYTES on top of that.

    **The two walls are now one wall and a flag.** `NODE_NOT_IN_FROZEN_TREE` asks
    `node_exists`, which is the whole frozen tree, and it is the structural refusal
    `00`'s amendment names; `INVENTED_NODE` asks whether the answer was on the list
    the model was shown, which is a fact about P11's retrieval and not about the
    answer's validity, so it is carried as a flag and the placement goes to a
    person. `place_file` then re-checks the resolved node against `legal_node_ids`
    before it writes anything, and `_place_one` raises if the resolver disagrees
    with the index -- so nothing is placed on a folder the plan does not hold, by
    two mechanisms that survive this change untouched.

    **`104` R-56's second abstention mechanism is narrowed, deliberately.** It was
    "the deterministic shortlist refusing an ungrounded choice": a model naming a
    real folder it was not shown lost the file. That is precisely the case §18.2
    gap 2 is opened for -- the folder was real, approved and frozen, and the only
    thing wrong with it was that six retrieval channels missed it -- so what
    remains of the mechanism is a REVIEW rather than a refusal. The first
    mechanism, the drafts' own `none`, is untouched and `_placement_site` still
    scores it as `ABSTAIN`.

    `ranked` EMPTY falls back to retrieval order, and that is the residual path:
    §7.7 runs no `assess`, so D has no ranking of its own and its offer is the
    approved residual library plus the branches retrieval reached.

    `evidence_snapshot_id` is minted here because nothing else mints one and
    `run_call` refuses a C or D request without it BEFORE the spend.
    """
    # `104` R-136. NEITHER OF THESE IS A JUDGEMENT AND NEITHER ENDS THE RUN. Both
    # are answers about ONE file, reached before a call is built: there is nothing
    # to send, or nothing to choose between. They used to raise
    # `ModelJudgementUnavailable`, which is not in `REFUSAL_EXCEPTIONS`, so
    # `_judged_or_refused` did not catch it and the corpus run died at the first
    # file that hit either -- measured on the C-live run r4, 50 placements in with
    # 0 site-C dossiers, on a corpus whose `subject` was missing on 19 files. Most
    # coursework files ARE that file, so the exception was the common case.
    #
    # A pre-call abstention is what P8 already calls this, and the reason word is
    # its own: `NOT_ELIGIBLE_FOR_MODEL` says the model is not reserved for this
    # subject, which is true of a file with nothing to send and of one with
    # nowhere to send it. No reason is invented, no budget is reserved -- the
    # abstention is decided before `reserve_call` -- and the file falls to step 9,
    # which places it the way a run with no model configured would.
    if not evidence.get("evidence_items"):
        return _not_asked(
            conn, call_site=call_site, subject=subject, observed_at=observed_at,
            because="a model call needs the reference-only evidence metadata the "
                    "dossier builder supplies, and this file version has no "
                    "settled fact to build one from; P11 synthesises no kind, "
                    "location, span or basis of its own")
    # `104` §18.2 gap 2 moved the second half of this condition. A file whose
    # every candidate a step-6 rule ranked below the contenders HAS a shortlist,
    # and it is made of frozen, approved destinations -- so the sentence below is
    # false about it in both halves: there is something for the judge to choose
    # between, and nothing about a list of approved folders invites an invention.
    # It was the case the rules answered on the model's behalf, which is the gap.
    if not retrieval.candidates and not set_aside:
        return _not_asked(
            conn, call_site=call_site, subject=subject, observed_at=observed_at,
            because="no legal destination was retrievable for this subject, so "
                    "there is nothing for the judge to choose between and asking "
                    "one would be inviting it to invent (§6.6)")
    # The keys the DOSSIER cites, which is `evidence_items` below and not the
    # subset that happened to match a node. `evidence_snapshot_id_for` addresses
    # what the dossier carries, so drawing from the matched facts alone would
    # address a different set from the one that was sent -- and would refuse to
    # mint at all for a call whose candidates were reached by group evidence.
    #
    # **AND IT NOW READS THE ITEMS, WHICH IS WHAT THAT PARAGRAPH ALWAYS SAID.**
    # `104` R-148. The expression under it was `evidence["facts"]` from the first
    # commit of this function, and `MatchingFact` forbids an empty `evidence_ref`
    # -- so the tuple was empty in exactly one case, a subject with NO settled
    # fact, and R-143's guard below turned every one of those into
    # `NOT_ELIGIBLE_FOR_MODEL`. That is 103 of the owner's 199 files on r12 and it
    # is the second half of R-148: `cli.evidence_for` now offers a factless file
    # its own releasable readings, and without this line the call would still not
    # be built -- the same abstention row, from a gate one paragraph further down.
    #
    # `model_call_request` below is handed `evidence["evidence_items"]` and
    # nothing else, so these ARE the keys the release request names and the ones
    # the dossier will cite. The node profiles and accepted groups are not here
    # for the same reason they are not there: a folder is not an observation, it
    # carries no key P7 could resolve, and addressing one would put a plan id in a
    # citation record. `snapshot_observation_keys` now states that exclusion by
    # kind rather than leaving it to WHEN this line runs -- the dossier below
    # carries the offers beside the readings, so a caller reading the finished
    # dossier has to be able to reach the same set.
    #
    # **AND THE DERIVATION IS ONE FUNCTION** (`104` R-155). The expression that
    # was written out here had a second spelling in `versions._revalidates`, over
    # the matched FACTS rather than the items -- so the snapshot a re-validation
    # compared against addressed a different set from the one that was sent.
    # `snapshot_observation_keys` is the single answer to "what did the model
    # see", asked here with the items about to be sent and there with the items
    # the stored dossier carried.
    observation_keys = snapshot_observation_keys(evidence["evidence_items"])
    # `104` R-143, and it is R-136's door for a third pre-call state. A dossier
    # whose items address nothing makes `evidence_snapshot_id_for` raise
    # `EvidenceSnapshotRequired` -- "an evidence snapshot addresses the evidence a
    # dossier cites, and this one cites none". That raise is not in
    # `REFUSAL_EXCEPTIONS` either, so it ended the corpus run exactly as R-136's
    # did: measured on r11, 113 minutes in, 0 site-C dossiers.
    #
    # The same reason word is true here for the same reading: the model is not
    # reserved for a subject whose evidence nothing can address. A snapshot that
    # addressed an empty set would be a citation record citing nothing, which is
    # what the raise refuses and what this must not fake.
    #
    # KEPT THOUGH `EvidenceItem.evidence_ref` IS REQUIRED NON-EMPTY, so with the
    # check above this cannot fire on any item shape that exists today. What it
    # guards is the RAISE, not a state -- an unhandled `EvidenceSnapshotRequired`
    # ends the run for every file after it, and that is too expensive an answer to
    # "someone added an item kind with no address" to leave to the stack trace.
    if not observation_keys:
        return _not_asked(
            conn, call_site=call_site, subject=subject, observed_at=observed_at,
            because="nothing this dossier would carry has an address this run can "
                    "resolve, so an evidence snapshot would address nothing and "
                    "the dossier would cite nothing")
    snapshot = evidence_snapshot_id_for(plan_version=inputs.plan_version,
                                        observation_keys=observation_keys)
    subject_ref = subject_ref_of(subject)
    legal = sorted(legal_node_ids(conn, plan_version=inputs.plan_version))
    retrieved = tuple(dict.fromkeys(
        candidate.node_id for candidate in retrieval.candidates))
    #: WHICH OFFERED FOLDERS A STEP-6 RULE RANKED BELOW THE CONTENDERS, and the
    #: sentence each one carries (`104` §18.2 gap 2). Empty at site D, which runs
    #: no `assess` and no step 6.
    ranked_below = {item.candidate.node_id: item.because for item in set_aside}
    if call_site == C_PLACEMENT:
        # The scores' order, and every candidate on it -- CONTENDERS FIRST, then
        # the folders step 6 ranked below them, each in its own scored order.
        # `dict.fromkeys` rather than a set: this is a RANKING and a set has no
        # first element, and `basis_key` below reads that first element.
        offered = tuple(dict.fromkeys(
            tuple(ranked) + tuple(ranked_below))) or retrieved
        sites = site_dependencies(placement=placement_authorities(
            conn, plan_version=inputs.plan_version, policy=inputs.policy,
            sensitivity_policy=inputs.sensitivity_policy))
    else:
        # §7.7's own answer space, and the D draft's two item kinds: "the approved
        # homes it may go to" (`00`:120's residual library, every residual node of
        # the plan) and the branches a return could send it back to (`00`:107),
        # which is what retrieval reached. `approved_target_ids` STAYS the whole
        # legal set, so the validator accepts exactly what it accepted before and
        # only what the model is SHOWN narrows.
        offered = tuple(dict.fromkeys(
            _residual_areas(conn, plan_version=inputs.plan_version) + retrieved))
        sites = site_dependencies(residual=residual_authorities(
            conn, plan_version=inputs.plan_version, approved_target_ids=legal,
            sensitivity_policy=inputs.sensitivity_policy))
    profiles = _offered_items(
        conn, plan_version=inputs.plan_version, node_ids=offered,
        call_site=call_site, own_folder_node_id=own_folder_node_id,
        ranked_below=ranked_below)

    # §8.6's two spend ceilings, put on the budget P8 reserves against.
    #
    # They are set here for the same reason `allowed_vocabulary` is, and the
    # argument is the same sentence with two words changed: a caller-supplied
    # BUDGET is a caller-supplied answer to "what did the user agree to spend",
    # which is P1's question and is already answered in
    # `model.max_llm_calls_per_thousand_files` and `model.max_cost_per_scan`.
    # Before this, `PlacementLimits` carried both and no module read either
    # (`planning/58-SCALE-STRESS.md` item 8), so the only thing bounding a scan's
    # model spend was whatever number the caller happened to construct.
    #
    # What is NOT taken from P11 is the scan itself. `scan_id` and
    # `corpus_file_count` describe the run and belong to it; P11 knows the
    # ceilings and not how many files the disk holds. So the two are replaced and
    # the two are kept.
    #
    # Enforcement is P8's and stays P8's: `reserve_call` refuses past either
    # ceiling, `run_call` turns the refusal into `BUDGET_EXHAUSTED`, and
    # `p8_seam.transcribe` records it as `budget_deferred` with a
    # `deferred_stage` -- §8.6's "retain extracted evidence, mark the deferred
    # stage, and leave the file in review", never a cheaper placement.
    budget = inputs.call_dependencies.scan_budget
    if budget is None:
        raise ScanBudgetRequired(
            "§8.6 bounds model spend per scan, and this request names no scan to "
            "charge against; P11 supplies the two ceilings and the caller "
            "supplies the scan they apply to"
        )
    dependencies = dataclasses.replace(
        inputs.call_dependencies,
        site_dependencies=sites,
        scan_budget=dataclasses.replace(
            budget,
            max_calls_per_1000_files=inputs.limits.max_llm_calls_per_thousand_files,
            max_estimated_cost=Decimal(inputs.limits.max_cost_per_scan)),
        allowed_vocabulary=list(offered),
        proposal_class=PLACEMENT if call_site == C_PLACEMENT else RESIDUAL,
        # THE RANKED WINNER, not `retrieval.candidates[0]`. `basis_key` is what a
        # past rejection is keyed on (`learning.basis_key_for`), so it has to name
        # the node this call is really about -- and that is the head of the
        # shortlist the model was shown. Retrieval's order is the order six
        # channels happened to answer in; `_staying_put_wins_a_tie` and §6.10's
        # arithmetic can both put a different node first, and when they do, the
        # rejection was being filed against a node nobody proposed.
        #
        # AND THE SUBJECT SAYS WHICH IT IS. §8.7's scope vocabulary is closed --
        # file, group, node, template, domain, corpus -- and the convention both
        # other sites keep is that the scope names the KIND of subject and
        # `learning_subject_id` is that subject's id. A group verdict is about a
        # group, so the pair is `group` beside the group id, which is also what
        # keeps a rejection of one group from suppressing another (site B's own
        # sentence, `cli.observe_group_authorities`).
        basis_key=basis_key_for(subject_id=_learning_subject_id(subject),
                                node_id=offered[0]),
        learning_scope=FILE if subject.kind == FILE else GROUP,
        learning_subject_id=_learning_subject_id(subject),
    )
    # `104` R-149. THE BUILDER'S RAISE, CAUGHT WHERE IT IS STILL A PRE-CALL STATE.
    #
    # `model_placement.releasable_excerpts` applies P7's five refusals a step early,
    # and the first of them drops every reading whose zone is always-local -- so a
    # file whose cited readings are all `path` or `filename` leaves this request
    # with NO items and `ModelCallRequest.__post_init__` refuses it: "a request with
    # no items has nothing to release". Measured on the six-file stub corpus of
    # `tests/integration/test_local_model_fact_pass.py` before R-148: one file, one
    # fact, a filename-only citation, and it went to the deterministic fallback with
    # no row in `llm_pre_call_abstention` and none in `llm_refusal` -- so r12's 104
    # `NOT_ELIGIBLE_FOR_MODEL` was a FLOOR on the silent site-C losses rather than
    # the total. R-148 lifts that particular file; a file with no body reading at
    # all is still this file, and any narrowing of the item set re-opens the hole.
    #
    # **The reason word is R-136's, for R-136's reading of it.**
    # `NOT_ELIGIBLE_FOR_MODEL` is what `eligibility.not_reserved_for_llm` returns
    # for a subject the model is not reserved for, and the model is not reserved for
    # a file with nothing releasable to send. Nothing is minted: §6.10's abstention
    # reasons stay closed and `PRE_CALL_REASON_CODES` gains no fourth member, which
    # is a spec-level act and the owner's.
    #
    # It is the reason that is TRUE of the file, and the other refusals
    # `__post_init__` makes are why: the stage, the target, the model target and the
    # template id are fixed for the run, and `max_dossier_tokens` is a deployment
    # number -- each would refuse every file of the corpus alike. The ITEM SET is
    # the only one of them that varies per file, so a per-file reason is a reason
    # about the item set.
    #
    # **NOT a `CallRefused`, and only the BUILDER's raise.** The `try` stops at this
    # expression: a `MalformedRequest` from inside `call_placement` is P7 unable to
    # evaluate a request that was built, which is R-O's refusal and stays one.
    # `record_unbuilt_call_abstention` states the rest -- "nothing was ever grounded,
    # and nothing refused a call that was never built" -- so no `call_refused` event
    # is appended beside the row and a reader counting refusals counts this once.
    # THE CLIENT THIS SUBJECT WAS ROUTED TO. `may_assemble_dossier` has already
    # answered about the same subject's target, so a pair is here; a second read of
    # a single field would send to a destination the gate never decided about. A
    # GROUP's pair is `place_group`'s, resolved once over every member and handed
    # in, for that same sentence read over a subject that is not one file.
    chosen = route_pair if route_pair is not None else inputs.route(subject.file_id)
    if chosen is None:
        return _not_asked(
            conn, call_site=call_site, subject=subject, observed_at=observed_at,
            because="no model in this run may be asked about this subject, so "
                    "nothing about it was assembled and nothing was sent")
    # THE MEMBERS AND THE TARGET THE GATE ALREADY DECIDED ABOUT, for a group and
    # only for a group. A placement release names the files it is about, and a
    # group's request names every member (`Target(file_ids=..., group_id=...)`,
    # the shape site B has always built); the target is the one this call was
    # routed to above, so the builder resolves no second destination of its own.
    # Absent for a file, so the file path builds byte-identically to before and a
    # caller-supplied builder that predates groups keeps working unchanged.
    group_release = (
        {} if subject.kind == FILE
        else {"member_file_ids": tuple(subject.member_file_ids),
              "model_target": chosen[1]})
    try:
        release_request = inputs.model_call_request(
            subject_ref=subject_ref,
            evidence_items=tuple(evidence["evidence_items"]),
            max_dossier_tokens=inputs.limits.max_dossier_tokens,
            **group_release)
    except MalformedRequest:
        return _not_asked(
            conn, call_site=call_site, subject=subject, observed_at=observed_at,
            because="P7 will not form a release request for this file: every "
                    "reading its evidence cites was dropped before the door, so "
                    "the call would carry nothing for the model to look at")
    request = DossierRequest(
        call_site=call_site, subject_ref=subject_ref,
        # P8's controlled reason, imported and not retyped. §6.6 lists six
        # circumstances that make a call eligible and P8 publishes a constant for
        # each; spelling one here would be a seventh vocabulary.
        eligibility_reason=(SEVERAL_LEGAL_NODES_PLAUSIBLE
                            if call_site == C_PLACEMENT
                            else USER_OPTED_RESIDUAL_SET_INTO_AI_REVIEW),
        # P8's reference-only `EvidenceItem`s, supplied by the dossier builder
        # and never synthesised here. P11's `MatchingFact` carries a field, a
        # value and an observation key; P8's item carries a kind, a location, an
        # excerpt span and a basis, and `records.py:204-207` says in terms that
        # "P8 does not synthesise kind, location, reliability or basis". A
        # conversion here would have to invent three of them, so the caller that
        # built the evidence hands them over instead.
        #
        # The FOLDERS are P11's, and they are the one thing here that is not the
        # file's evidence: `00`:110's node profiles and accepted groups (R-17,
        # G3). They carry no span, no observation key and no released text, so
        # `build_dossier`'s three-key agreement is untouched -- it checks that
        # every RELEASED key has builder metadata, and adds nothing about items
        # that were never released.
        evidence_items=(tuple(evidence["evidence_items"]) + profiles
                        + _accepted_group_items(evidence.get("group_ids", ()))
                        # `104` §18.2 gap 12. Beside the groups and for the same
                        # reason: `00`:110 lists "accepted group memberships,
                        # GRAPH ANCHOR EVIDENCE, the small set of top legal
                        # destination candidates" as three things one dossier
                        # carries, and two of the three were here.
                        + _graph_items(
                            conn, subject=subject,
                            plan_version=inputs.plan_version, graphs=graphs,
                            related_files=evidence.get("related_files", ()),
                            offered=offered,
                            target_locality=getattr(chosen[1], "locality",
                                                    None))),
        conflicts=to_p8_conflicts(retrieval.conflicts),
        # P7 builds the release request; P11 holds the builder and never a `Gate`.
        # Assembling it above, after `may_assemble_dossier` answered, is what keeps
        # §8.4's gate on the right side of the spend.
        model_call_request=release_request,
        plan_version=inputs.plan_version, evidence_snapshot_id=snapshot,
    )
    # THIS SITE'S OWN TEXT, and the observe lever reads the same one. Asking under
    # C's prompt and then checking C's `ratified` for a D call would have been two
    # wrong answers agreeing with each other.
    prompt = inputs.prompt_for(call_site)
    return _observed_only((yield from call_placement_steps(
        conn, request, gate=inputs.gate, model_client=chosen[0],
        prompt=prompt, call_dependencies=dependencies,
        observed_at=lambda: observed_at,
        usage_recorder=inputs.usage_recorder,
    )), prompt=prompt)


def _judged_or_refused(conn, **kwargs):
    """One subject judged here, on this thread. `104` §18.15's serial form.

    `place_group`'s member loop and every caller that walks one subject at a time
    reach the model through this; `run_corpus`'s per-file pass drives
    `_judged_or_refused_steps` on a lane instead.
    """
    return drive_inline(_judged_or_refused_steps(conn, **kwargs))


def _judged_or_refused_steps(conn, **kwargs):
    """`_judge_with_model`, with `104` R-O's one difference: a refusal comes back.

    The `try` covers the REQUEST BUILD as well as the call, because a raise while
    an argument is being built never reaches `run_call`'s own `try`. It stays that
    wide though this deployment's own builder no longer reaches it: `inputs.model_
    call_request` is INJECTED, so P11 cannot know what a builder raises, and
    `resolve`'s two spellings of "this span cannot be taken" are in
    `REFUSAL_EXCEPTIONS` because a builder that materialises anything raises them.

    **`MalformedRequest` FROM THE BUILDER NO LONGER ARRIVES HERE** (`104` R-149).
    `_judge_with_model` catches that one at the expression that raises it and
    returns a pre-call abstention instead, because a request P7 will not FORM is a
    call that never happened rather than a call something refused -- and this
    function recorded it as neither: an event, and no row in `llm_pre_call_
    abstention` or `llm_refusal`.

    It was the ONLY member of the three the placement builder could raise:
    `model_placement.releasable_excerpts` selects rows, reads unit lengths and
    reads P5's signal, and materialises nothing, so neither span refusal is
    reachable from it -- the door raises those, and the door is past `run_call`'s
    own `try`. So at these two sites what this `except` still sees is P7 refusing a
    request that WAS built, from inside `call_placement`, which is a refusal and is
    recorded as one.

    Recorded here rather than swallowed: the same `call_refused` event site A
    writes, so one query over the run counts every refusal wherever it was raised.
    """
    try:
        # `104` §18.15: `yield from`, so a refusal raised on the far side of the
        # socket still lands in this `try`. An exception carried back through a
        # resume propagates out of the sub-generator exactly as one raised inside
        # the call did, which is what keeps R-O's record intact.
        return (yield from _judge_with_model_steps(conn, **kwargs))
    except REFUSAL_EXCEPTIONS as refusal:
        subject = kwargs["subject"]
        return refusal_outcome(
            conn, call_site=kwargs["call_site"],
            subject_ref=subject_ref_of(subject),
            error=refusal, observed_at=kwargs["observed_at"])


# --- §6.8 and §6.9: the group plan -------------------------------------------------


def _group_subject(accepted: AcceptedGroup, memberships) -> Subject:
    """The group, as the one subject a placement call is about."""
    return Subject(kind=GROUP, file_id=None, content_hash=None,
                   group_id=accepted.group_id,
                   member_file_ids=tuple(m.file_id for m in memberships))


def _one_destination_every_member_may_use(conn, *, memberships,
                                          inputs: PipelineInputs):
    """§8.4's gate, asked of a subject that is not one file. The pair, or `None`.

    **THE RULE IS THE WEAKEST MEMBER'S, AND IT IS NOT NEW.** A group dossier
    carries evidence from every member, so a destination it may be sent to is one
    that EVERY member may be sent to -- site B says the same sentence about the
    same shape ("cloud only if every member is cloud-permitted, else local"), and
    `may_assemble_dossier` is the same per-file predicate asked once per member
    rather than a group-shaped question added to `src/privacy/`.

    Three answers, in order:

    * a member this run may ask no model about at all -- no group call. Not "ask
      about the rest": the group's question is about these files together, and a
      dossier that quietly left one out would be a call about a different group
      than the one the plan names.
    * ANY member routed to a local model -- the whole call is local. One protected
      or unclassified member makes the group call local-only exactly as that
      member alone would be, and a member that may not be described to a cloud
      target is never described to one.
    * every member routed to the cloud -- the cloud, and then only if the gate
      admits every one of them for it.

    A protected member fails the last check for BOTH localities
    (`may_assemble_dossier` refuses `protected` whatever the target), so a group
    holding one is WITHHELD rather than downgraded -- again exactly as that member
    alone would be. The members are still placed: `place_group` falls back to the
    per-file pass, where each file meets the same gate on its own.
    """
    routes = {}
    for membership in memberships:
        chosen = inputs.route(membership.file_id)
        if chosen is None:
            return None
        routes[membership.file_id] = chosen
    local = [pair for pair in routes.values()
             if getattr(pair[1], "locality", None) == LOCAL]
    pair = local[0] if local else next(iter(routes.values()))
    locality = getattr(pair[1], "locality", None)
    for membership in memberships:
        state = privacy_state_for(conn, file_id=membership.file_id,
                                  content_hash=membership.content_hash,
                                  plan_version=inputs.plan_version)
        if not may_assemble_dossier(state, target_locality=locality):
            return None
    return pair


def _group_evidence(evidence_for, memberships, *, group_id: str) -> dict:
    """§6.3's evidence for a GROUP: each member's ACCEPTED FACTS, and nothing else.

    `104` §18.2 gap 14 and `00`:112. The subject is the packet, so the evidence is
    the packet's -- but a dossier that carried every member's readings would be one
    file's dossier multiplied by the size of the group, and §8.6's ceiling would
    cut it somewhere nobody chose. So the cut is made HERE and it is made by kind
    rather than by length: an item is carried when an accepted fact of that member
    cites it, and not otherwise. The member's anchor lines and its body readings --
    the two producers `cli.evidence_for` adds beneath the facts -- stay with the
    member's own call, where they are what that one file is judged on.

    Nothing is widened by this. Every item here is one the SAME member's own
    site-C call would have carried, already passed through the door's own
    predicate by `cli.evidence_for`, and the gate is asked again per item at the
    door. The group call sees a subset of the union, never a byte the per-file
    calls could not have sent.

    **WHAT IS NOT HERE, AND IT IS OWED RATHER THAN OMITTED.** The brief asks for
    each member's released FILENAME row beside its facts, and site C releases no
    filename today: `model_facts.may_be_released` refuses a `filename`-zone
    reading to BOTH localities (`ALWAYS_LOCAL_ZONES_FOR_EVERY_TARGET`) because the
    name has its own door -- §7.7's `Filename` item, which site A's request builds
    and site C's does not. Opening that door at C would send a name where none
    goes today, which is a release decision and the owner's. Recorded in the
    report; not taken here.

    The frequencies are the corpus's, not the subject's, so the first member's are
    the group's; `entity_frequency` is merged by the larger count, because a fact
    §4.3 would call a hub for one member is a hub for the group that holds it.
    """
    facts: list = []
    items: list = []
    group_ids: list[str] = [group_id]
    labels: list[str] = []
    neighbours: list[str] = []
    related: list = []
    entity_frequency: dict = {}
    generic = 0
    seen_facts: set = set()
    seen_items: set = set()
    for membership in memberships:
        evidence = evidence_for(membership.file_id)
        cited = set()
        for fact in evidence["facts"]:
            cited.add(fact.evidence_ref)
            key = (fact.field, fact.value, fact.evidence_ref)
            if key in seen_facts:
                continue
            seen_facts.add(key)
            facts.append(fact)
        for item in evidence["evidence_items"]:
            if item.evidence_ref not in cited:
                continue
            key = (item.evidence_ref, item.kind, item.excerpt_span)
            if key in seen_items:
                continue
            seen_items.add(key)
            items.append(item)
        group_ids.extend(evidence.get("group_ids", ()))
        labels.extend(evidence.get("curated_folder_labels", ()))
        neighbours.extend(evidence.get("semantic_neighbours", ()))
        related.extend(evidence.get("related_files", ()))
        for name, count in (evidence.get("entity_frequency") or {}).items():
            entity_frequency[name] = max(entity_frequency.get(name, 0), count)
        generic = max(generic, evidence.get("generic_entity_frequency") or 0)
    return dict(
        facts=tuple(facts), evidence_items=tuple(items),
        group_ids=tuple(dict.fromkeys(group_ids)),
        curated_folder_labels=tuple(dict.fromkeys(labels)),
        semantic_neighbours=tuple(dict.fromkeys(neighbours)),
        related_files=tuple(related), entity_frequency=entity_frequency,
        generic_entity_frequency=generic,
    )


def _the_groups_own_answer(conn, *, accepted: AcceptedGroup, memberships,
                           inputs: PipelineInputs, evidence_for,
                           component_version: str,
                           observed_at: str) -> str | None:
    """ONE site-C call whose subject is the GROUP. The node it chose, or `None`.

    `104` §18.2 gap 14, closing `00`:112: *"Group-level placement should be a
    first-class capability. Related files often explain one another more
    accurately when considered together than when classified independently ...
    The placement engine should FIRST confirm the shared parent branch."*

    `None` is every way this call does not produce an answer, and each of them
    leaves the members to the per-file pass exactly as a run with no model
    configured would (§13.5's own fallback, and the shape `place_file` already
    keeps for R-O, R-136 and R-173):

    * no model path, or a run whose site-C text is not ratified to act on
      (`model_decides`);
    * §8.4 admitting no one destination every member may use;
    * nothing retrievable to choose between -- asking then would be inviting an
      invention (§6.6);
    * a refusal, an unbuilt call, a failed call or an unjudgeable answer;
    * the model's own "none". An abstention about the group is not an abstention
      about its members: each still gets its own question, which is what the
      product did for all of them before this call existed.

    `00`:110 makes a group its own reason to ask -- the LLM is invoked "when a
    group may need to be placed together" -- so this is not gated on
    `needs_model_call`, which asks whether ONE file's candidates are ambiguous. A
    group with one legal candidate still has the question `00`:112 poses: does
    this packet belong there TOGETHER.
    """
    if not memberships:
        return None
    if not inputs.model_path_available() or not inputs.model_decides():
        return None
    route_pair = _one_destination_every_member_may_use(
        conn, memberships=memberships, inputs=inputs)
    if route_pair is None:
        return None
    subject = _group_subject(accepted, memberships)
    evidence = _group_evidence(evidence_for, memberships,
                               group_id=accepted.group_id)
    # Steps 3 to 6, over the group's own evidence: the union of the members'
    # legal candidates, because a node any member's fact reaches is a node the
    # union reaches, and §6.10's arithmetic over the group's accepted facts.
    retrieval = retrieve(
        conn, subject=subject, plan_version=inputs.plan_version,
        limits=inputs.limits, facts=evidence["facts"],
        group_ids=evidence["group_ids"],
        curated_folder_labels=evidence["curated_folder_labels"],
        semantic_neighbours=evidence["semantic_neighbours"],
        component_version=component_version, observed_at=observed_at)
    # The two collapses that are questions about the TREE rather than about one
    # file's own folder. The other two step-6 rules are per-file by construction
    # -- the folder this file sits in, and the refinement exemption that reads it
    # -- and a group has no such folder, so they are not asked rather than asked
    # with a `None` that would answer them by accident.
    retrieval = _without_superseded_ancestors(
        conn, retrieval, plan_version=inputs.plan_version)
    retrieval = _without_duplicated_proposals(
        conn, retrieval, plan_version=inputs.plan_version)
    # NO NODE-LOCAL GRAPH FOR A GROUP, and it is a refusal `placement.graph`
    # already writes down rather than an omission: every `GraphAnchor` names the
    # file the edge came FROM, and `build_node_local_graph` passes
    # `subject.file_id` through uncoerced precisely so that "a group subject has
    # no single originating file and fails here by name rather than storing one".
    # A group of four files has four originating files and no one of them is the
    # anchor's; a `""` or a first-member stand-in would be a placeholder
    # satisfying a type, and it would be recorded as evidence.
    #
    # Nothing is lost from the SCORE by this. `score_candidates` reads the graph
    # for two FLAGS only -- `typed_support` and `generic_hub` -- and takes every
    # point of support from `candidate.channels`, so the group's ranking is the
    # same arithmetic over the same channels either way; what the empty map says
    # is that this call claims neither flag, which is true of it.
    #
    # **AND GAP 12 DOES NOT CHANGE IT.** The graph now carries a support channel
    # and reaches the dossier as reference-only items; both are read off `graphs`,
    # so an empty map means the group's call declares no `graph_relationship` (its
    # denominator stays 5) and carries no edge item. That is the honest reading of
    # a subject with no graph, and it is `build_node_local_graph`'s refusal above
    # rather than a second decision: a group of four files has four originating
    # files and no one of them is the anchor's. The MEMBERS still get theirs, on
    # their own calls, where the anchor is the file the edge came from.
    graphs: dict = {}
    assessment = assess(retrieval, graphs, policy=inputs.policy,
                        their_own_folder_node_ids=frozenset(),
                        refinements=frozenset())
    set_aside = _ranked_set_aside(retrieval, graphs, policy=inputs.policy)
    # THE GROUP'S OWN LEDGER (`GROUP_BUDGET_SUFFIX`), so this one question is
    # never the call that empties a member's per-file purse.
    budget = inputs.call_dependencies.scan_budget
    inputs = inputs if budget is None else dataclasses.replace(
        inputs, call_dependencies=dataclasses.replace(
            inputs.call_dependencies,
            scan_budget=dataclasses.replace(
                budget, scan_id=budget.scan_id + GROUP_BUDGET_SUFFIX)))
    result = _judged_or_refused(
        conn, subject=subject, inputs=inputs, retrieval=retrieval,
        evidence=evidence, call_site=C_PLACEMENT, observed_at=observed_at,
        ranked=tuple(item.node_id for item in assessment.scored),
        set_aside=set_aside, own_folder_node_id=None, route_pair=route_pair)
    if isinstance(result, (Refusal, CallRefused, PreCallAbstention, CallFailed,
                           ValidationUnavailable)):
        return None
    verdict = _require_verdict(result, call_site=C_PLACEMENT)
    outcome, _reason, _deferred = transcribe(verdict, assessment=assessment)
    if outcome != PLACE:
        return None
    node_id = inputs.chosen_node_of(verdict)
    if node_id not in legal_node_ids(conn, plan_version=inputs.plan_version):
        raise ValueError(
            f"{node_id!r} is not a legal destination of {inputs.plan_version!r}. "
            "P8 already refuses an invented node; reaching here means the "
            "resolver disagreed with the index, and P11 places no group on a "
            "disagreement"
        )
    return node_id


def place_group(conn: sqlite3.Connection, *, group_id: str,
                inputs: PipelineInputs, evidence_for,
                component_version: str, observed_at: str,
                skip_file_ids: frozenset[str] = frozenset(),
                #: `104` §18.15: THE PASS'S OWN LANE, so the width the run
                #: reports is the widest window the whole placement pass opened
                #: and not one group's. A caller placing a group by itself is
                #: given a lane of one, which is what this pass did before the
                #: lane existed.
                lane: CallLane | None = None) -> GroupPlan:
    """§6.8 and `00`:112: ONE call takes the group, then the members follow it.

    **THIS COMMENT USED TO SAY THE OPPOSITE OF WHAT THE CODE DID, AND `104` §18.2
    GAP 14 IS THAT SENTENCE.** It read "confirm the shared parent FIRST, then
    classify members beneath it ... a member classified before the parent is
    classified against no shared context" -- and the code placed every member
    singly and then read the parent off the results, which is precisely a member
    classified against no shared context. `confirm_shared_parent` returned a
    parent only when every single placement happened to agree, no model call ever
    took a group, and `00`:112's *"related files often explain one another more
    accurately when considered together"* had no implementation at all.

    The order is now the order the sentence claims:

    1. ONE site-C dossier whose subject is the group -- the members' accepted
       facts, the union of their legal candidates scored over those facts, the
       same folder levels, vocabulary and shaping policy one file's call has --
       and the model answers the group's destination with citations, or abstains.
       §8.4 is asked first, over every member, and one member it refuses withholds
       the whole call rather than describing that member to a target it may not
       reach (`_one_destination_every_member_may_use`).
    2. Every member is then placed FROM that answer: a member whose own stated
       values do not rule the folder out goes with the group and its row says the
       MODEL decided, because the group's answer is the model's; a member that
       contradicts it is an outlier of the answer and is placed by its own
       per-file call, with the group's folder offered on the shortlist and the
       disagreement recorded (`place_file`'s `group_answer`).
    3. Where the group produced no answer -- no model path, a gate refusal, a
       refused or failed call, or the model's own "none" -- every member is placed
       exactly as it is today, singly, and `confirm_shared_parent` reads the
       parent off those results. That is the fallback and it is unchanged: nothing
       here makes a run WITHOUT a model worse than it was.

    P9's outlier flags are a different thing from step 2's contradiction and both
    survive. `outlier_flag` is P9's finding that the file sits apart from the
    GROUP; step 2's is this file's own evidence against the folder the model
    chose. A member P9 flagged is excluded from the plan whatever the model said,
    because P11 does not re-decide belonging.

    Acceptance is read through P9 as of P10's frozen version
    (`accepted_group_as_of`), never off `Group.state`.

    `skip_file_ids` names the members §6.9 resolves instead: a file with accepted
    membership in two packets belongs to neither plan alone, and placing it inside
    one of them IS choosing between them.
    """
    accepted: AcceptedGroup = accepted_group_as_of(
        conn, group_id=group_id, plan_version=inputs.plan_version)
    # The address carries `observed_at`, for `residual.record_set_decision`'s own
    # reason: `one_current_group_plan` is a partial unique index over UNSUPERSEDED
    # rows, so it already forbids two live plans for one group in one version.
    # Addressing the row as `plan_version:group_id` as well would forbid a SECOND
    # ROW OF ANY KIND -- including the superseding one -- and the three supersede
    # columns on that table would be columns no writer could ever reach.
    group_plan_id = f"{inputs.plan_version}:{group_id}:{observed_at}"
    memberships = tuple(m for m in accepted.memberships
                        if m.file_id not in skip_file_ids)

    # Step one: the group's own question, asked of the model as one subject.
    answered = _the_groups_own_answer(
        conn, accepted=accepted, memberships=memberships, inputs=inputs,
        evidence_for=evidence_for, component_version=component_version,
        observed_at=observed_at)

    # Step two: every member, FROM that answer. `place_file_steps` writes the row
    # -- one writer for every placement, so a member of a group meets the same
    # privacy state, the same review policy and the same supersession as any
    # other file. `104` §18.15: the members' own calls, where a member needs one
    # (an outlier, or a group the model declined), run several cloud round trips
    # at a time through the pass's lane; a member that goes with the group makes
    # no call and settles at once. Walked in the order the accepted group lists
    # them and every row is written on this thread in that order; a member routed
    # local is settled by itself, because one Ollama server holds one model.
    member_parents: dict[str, str | None] = {}
    placed: dict[str, PlacementDecision] = {}
    asked = ((membership.file_id, place_file_steps(
        conn, subject=_member_subject(membership), inputs=inputs,
        evidence=evidence_for(membership.file_id),
        group_plan_id=group_plan_id,
        group_answer=(None if answered is None else GroupAnswer(
            group_id=group_id, node_id=answered,
            membership=membership.decision,
            sits_apart=membership.outlier_flag != NOT_FLAGGED)),
        component_version=component_version, observed_at=observed_at))
        for membership in memberships)
    for file_id, decision in in_walk_order(
            asked, lane=lane if lane is not None else CallLane(width=1)):
        placed[file_id] = decision
        member_parents[file_id] = (
            decision.destination.node_id if decision.destination else None)

    # THE RULES' ANSWER IS STILL COMPUTED, and it is still the one used when the
    # model produced none. `confirm_shared_parent` also carries §6.9's refusal of
    # a tree with no shared-material policy, which must fire whether or not a
    # model answered -- a plan built on an unstated policy is refused either way.
    by_the_rules = confirm_shared_parent(
        member_parents, policy=inputs.tree.shared_material_policy)
    shared_parent = answered if answered is not None else by_the_rules

    # Step three: outliers are excluded and explained, never forced in. P9 already
    # flagged them and already holds the competing values; P11 records what P9
    # found and routes the file (§6.8).
    outliers: list[ExcludedOutlier] = []
    members: list[PlacementDecision] = []
    for membership in memberships:
        decision = placed[membership.file_id]
        if membership.outlier_flag != NOT_FLAGGED:
            outliers.append(excluded_outlier_for(
                membership,
                routed_node_id=(decision.destination.node_id
                                if decision.destination else None)))
            continue
        members.append(decision)   # already carries `group_plan_id`, in the row

    plan = GroupPlan(
        group_plan_id=group_plan_id, plan_version=inputs.plan_version,
        group_id=group_id, shared_parent_node_id=shared_parent,
        member_decisions=tuple(members), excluded_outliers=tuple(outliers))
    _record_group_plan(conn, plan, component_version=component_version,
                       observed_at=observed_at)
    return plan


def _record_group_plan(conn: sqlite3.Connection, plan: GroupPlan, *,
                       component_version: str, observed_at: str) -> None:
    """§6.8's plan, in the table the schema made for it.

    Without this the plan exists only in the caller's memory: `placement_group_plans`
    had no writer at all, so a review surface reopened a day later would find four
    file decisions and no evidence they were ever one plan.
    """
    import json

    live = conn.execute(
        "SELECT record_id FROM placement_group_plans WHERE plan_version = ? AND "
        "group_id = ? AND superseded_by IS NULL",
        (plan.plan_version, plan.group_id),
    ).fetchone()
    if live is not None and live["record_id"] != plan.group_plan_id:
        # Supersede first, then insert: the unique index is over unsuperseded
        # rows, so linking after the insert would put two current plans for one
        # group in the table for the length of one statement.
        mark_superseded(
            conn, "placement_group_plans", old_id=live["record_id"],
            new_id=plan.group_plan_id,
            reason="§6.8's plan for this group was recomputed (§8.2)")
    conn.execute(
        "INSERT INTO placement_group_plans (record_id, plan_version, group_id, "
        "shared_parent_node_id, payload, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (plan.group_plan_id, plan.plan_version, plan.group_id,
         plan.shared_parent_node_id,
         json.dumps({
             "group_plan_id": plan.group_plan_id,
             "member_decision_ids": [d.decision_id for d in plan.member_decisions],
             "excluded_outliers": [dataclasses.asdict(o)
                                   for o in plan.excluded_outliers],
         }, sort_keys=True),
         observed_at),
    )
    placement_events.group_plan_emitted(
        conn, group_plan_id=plan.group_plan_id, group_id=plan.group_id,
        shared_parent_node_id=plan.shared_parent_node_id,
        component_version=component_version, observed_at=observed_at)


def _member_subject(membership) -> Subject:
    return Subject(kind=FILE, file_id=membership.file_id,
                   content_hash=membership.content_hash, group_id=None,
                   member_file_ids=())


def _shared_branch_of(tree) -> str | None:
    """The frozen tree's shared-material node, if it froze one. P11 mints none.

    §6.9's worked example: *"If no shared branch exists, the system should not
    arbitrarily choose one university."* So absence is answered with None and the
    policy decides what happens next, rather than P11 producing a branch.
    """
    for node in tree.nodes:
        if node.node_role == SHARED_MATERIAL and node.accepts_placement:
            return node.node_id
    return None


def _flat_two_condition(inputs: PipelineInputs) -> TwoCondition:
    """§6.10's figures on a record §6.10 did not decide. One shape, one set of
    figures.

    SPEC:473-475 makes `verdict` a P11 field on every decision, so a §7 decision
    and a §6.9 decision carry the thresholds they were judged under even though
    the judgement was P8's or the user's. `meets_margin` is vacuous because
    neither path compares against a next-best destination.
    """
    return TwoCondition(
        support_score=0.0,
        support_threshold=inputs.policy.minimum_support_threshold,
        meets_threshold=False, margin_over_next=None,
        margin_threshold=inputs.policy.margin_threshold,
        meets_margin=MARGIN_TRUE_VACUOUS, verdict=WEAK,
        requires_review=True)


def _protected_material_is_never_a_question(node_ids) -> str:
    """§6.9's selector, overridden for a file P7 marked protected.

    The second lock that had to come with `104` §18.2 gap 15.

    **ABSTAINS RATHER THAN RAISING, AND THE DIFFERENCE FROM `_asking` IS REAL.**
    `_asking` refuses outright, because reaching it means the caller's policy is
    broken and a broken policy has to be FOUND. This is not that: nothing is
    broken when a protected file turns out to belong to two packets, and the
    injected selector is not wrong to want to ask about ordinary material. Two
    homes on a protected file is an ordinary outcome with one option removed, and
    §6.9 already names abstention as one of its three legal answers -- so the
    answer is the legal one, not a traceback that stops the run.

    **THE FILE IS NOT LOST BY IT.** The screen puts every protected file into its
    own review set off P7's flag (`cli._protected_among`) before it ever reads a
    decision's reason, so it is named and counted exactly as it would have been. What does not
    happen is an `Ask` naming two packets -- "Applications/UChicago or
    Applications/Columbia?" beside a passport scan -- which is the specific
    disclosure `00`:201 is about. Marked, counted, never opened, never silently
    omitted, and never turned into a question.

    `node_ids` is accepted and ignored: `resolve_multi_home` calls its selector
    with the competing ids and this function's answer does not depend on them.
    """
    del node_ids
    return ABSTAIN


def _multi_home_decision(conn, *, subject, inputs: PipelineInputs, outcome,
                         payload, privacy, automatic_move_permitted: bool,
                         component_version: str,
                         observed_at: str) -> PlacementDecision:
    """§6.9's answer as one decision: a shared branch, a question, or an abstention.

    `payload` is the shared branch's node id for `place`, the competing ids for
    `ask_user`, and `no_shared_branch` for `abstain` -- and it is NEVER one of the
    competing packets, because `resolve_multi_home` has no branch that returns one.
    """
    two = _flat_two_condition(inputs)
    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=payload)
             if outcome == PLACE else None)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version,
        subject_ref=subject_ref_of(subject), observed_at=observed_at,
        suffix=":mh")
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=PLACEMENT, returned_from=None,
        subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=None, marked_state=None,
        ask=(Ask(question="Which packet is this file's primary home?",
                 options=tuple(payload)) if outcome == ASK_USER else None),
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(SHARED_MATERIAL_DECISION if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=two,
        abstention_reason=(NO_SHARED_BRANCH if outcome == ABSTAIN else None),
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            destination_disposition=entry.disposition if entry else None,
            automatic_move_permitted=automatic_move_permitted),
        explanation=(
            "This file has accepted membership in more than one packet. §6.9 "
            "permits a shared branch, a question, or an abstention, and never an "
            "arbitrary choice between the packets."),
        residual=None,
        # `104` R-165. §6.9's `place` is `resolve_multi_home` returning the shared
        # branch, which it reaches from the shared-material POLICY and the branch
        # node id it was handed -- no model call, no per-file answer from the
        # person, and it refuses outright to return one of the competing homes. So
        # the rules decided. The other two outcomes chose no destination at all:
        # `ask_user` IS the question, and `abstain` is `no_shared_branch`.
        decided_by=DECIDED_BY_RULE if outcome == PLACE else None,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="§6.9 resolved this file's multiple homes (§8.2)",
                  component_version=component_version, observed_at=observed_at)


class DestinationTheUserNamedIsNotInThisPlan(ValueError):
    """The person's answer names a node this plan version does not contain."""


class ProtectedMaterialIsNotAQuestion(RuntimeError):
    """Something tried to raise a per-file question about protected material."""


def _user_chose(conn: sqlite3.Connection, *, subject, inputs: PipelineInputs,
                node_id: str, privacy, group_plan_id: str | None,
                returned_from: str | None, component_version: str,
                observed_at: str) -> PlacementDecision:
    """The person answered `ask_user`, and this is that answer as a decision.

    **Every figure on this record says the person decided, and none of them
    imitates a measurement.** `support_score` is zero, `meets_margin` is vacuous and
    `verdict` is `weak`, because that is what `_flat_two_condition` already means
    and it is TRUE here: no candidate was scored, none was beaten, and nothing about
    the evidence changed when the person spoke. Filling those in with numbers that
    made the record look confident is the failure §6.10 exists to prevent, arriving
    from the one direction §6.10 does not watch.

    `requires_review` therefore stays true and `review_policy_for` is asked exactly
    as it is on every other path. A destination the person named is not a move they
    authorised: `00` keeps those two apart everywhere else, and P12's freeze is
    still the gesture that files anything.

    **The evidence type is `user_confirmed`**, which P6 publishes and P11 has never
    had a producer for. It is the one line on this record that is a fact about where
    the answer came from rather than about what was read.
    """
    if node_id not in legal_node_ids(conn, plan_version=inputs.plan_version):
        raise DestinationTheUserNamedIsNotInThisPlan(
            f"{node_id!r} is not a legal destination of {inputs.plan_version!r}. "
            "An answer names a node in the tree it was asked about, and a tree "
            "that has been rebuilt since is a different tree -- placing on a stale "
            "id would file a person's material somewhere they never saw"
        )
    entry = entry_for(conn, plan_version=inputs.plan_version, node_id=node_id)
    two = _flat_two_condition(inputs)
    automatic_move_permitted = (
        automatic_move_permitted_for(conn, file_id=subject.file_id,
                                     plan_version=inputs.plan_version)
        if privacy.protected else False
    )
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version,
        subject_ref=subject_ref_of(subject), observed_at=observed_at)
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=PLACEMENT,
        returned_from=returned_from, subject=subject,
        group_plan_id=group_plan_id, outcome=PLACE,
        destination=Destination(node_id=entry.node_id, node_role=entry.node_role),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=entry.depth,
                                     supported_depth=entry.depth,
                                     unsupported_levels=()),
        evidence_type=USER_CONFIRMED,
        confidence_class=USER_CHOSE_DESTINATION,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(), two_condition=two,
        abstention_reason=None, deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            destination_disposition=entry.disposition,
            automatic_move_permitted=automatic_move_permitted),
        explanation=(
            "You said where this file goes. Nothing this run could read said what "
            "it is, so this destination is yours and not a judgement the engine "
            "made -- it can be changed by answering the question again."),
        residual=None,
        # `104` R-165, and the sentence directly above is the argument: the
        # destination is the person's answer, read from `chosen_by_user` before
        # retrieval or scoring ran at all. `evidence_type` already says
        # `user_confirmed`; this says the same thing about the CHOICE rather than
        # about the evidence, which is what a count of the model's share needs.
        decided_by=DECIDED_BY_USER,
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later answer about the same file version supersedes "
                         "this one (§8.2)",
                  component_version=component_version, observed_at=observed_at)


# --- §7: the residual stage ---------------------------------------------------------


def run_residual_file(conn: sqlite3.Connection, *, subject, set_id: str,
                      inputs: PipelineInputs, evidence, action: str, target,
                      component_version: str,
                      observed_at: str) -> PlacementDecision:
    """One §7.7 action, as one decision on the ONE record shape.

    §7.6's gate is checked first and by refusal: `require_set_decision` raises when
    the set has no decision. §7.9's loop is bounded by an injection:
    `check_return_cycle` refuses without `max_return_cycles`, because SPEC Open
    question 8 states no bound and an unbounded loop is a replay that never
    terminates.
    """
    set_decision = require_set_decision(conn, plan_version=inputs.plan_version,
                                        set_id=set_id)
    outcome, qualifier = outcome_for_action(action, target=target)
    if outcome == RETURN_TO_PLACEMENT:
        check_return_cycle(conn, subject_ref=subject_ref_of(subject),
                           max_return_cycles=inputs.max_return_cycles)
    context = ResidualContext(set_id=set_id, set_decision=set_decision.choice,
                              lifecycle_policy_ref=None)
    return _residual_decision(
        conn, subject=subject, inputs=inputs, outcome=outcome,
        qualifier=qualifier, residual=context, evidence=evidence,
        component_version=component_version, observed_at=observed_at)


def _residual_decision(conn, *, subject, inputs: PipelineInputs, outcome,
                       qualifier, residual, evidence, component_version,
                       observed_at) -> PlacementDecision:
    """One §7 decision on the SAME thirty-one-field shape §6 uses (Done-means 1).

    Exactly one outcome-shaped field is filled, chosen by `outcome`, because the
    record refuses any other combination: `destination` on `place`,
    `return_target` on `return_to_placement`, `marked_state` on `mark_state`,
    `abstention_reason` on `abstain`, and none of the four on `leave_in_place` or
    `mark_review_later` -- whether those two result in a move is the Review Later
    node's `disposition` (§7.4, set by P10), not this record's decision.
    """
    entry = (entry_for(conn, plan_version=inputs.plan_version, node_id=qualifier)
             if outcome == PLACE else None)
    if outcome == PLACE and entry is None:
        raise ValueError(
            f"{qualifier!r} is not a legal destination of "
            f"{inputs.plan_version!r}; §7.7 chooses among APPROVED residual "
            "targets and P11 places nothing outside the frozen tree"
        )
    privacy = privacy_state_for(conn, file_id=subject.file_id,
                                content_hash=subject.content_hash,
                                plan_version=inputs.plan_version)
    automatic_move_permitted = (
        automatic_move_permitted_for(conn, file_id=subject.file_id,
                                     plan_version=inputs.plan_version)
        if privacy.protected else False
    )
    two = _flat_two_condition(inputs)
    decision_id, supersedes = _identity(
        conn, plan_version=inputs.plan_version,
        subject_ref=subject_ref_of(subject), observed_at=observed_at, suffix=":r")
    decision = PlacementDecision(
        decision_id=decision_id, plan_version=inputs.plan_version,
        supersedes=supersedes, superseded_by=None, supersede_reason=None,
        created_at=observed_at, origin_stage=RESIDUAL, returned_from=None,
        subject=subject, group_plan_id=None, outcome=outcome,
        destination=(Destination(node_id=entry.node_id,
                                 node_role=entry.node_role)
                     if entry is not None else None),
        return_target=(ReturnTarget(kind=qualifier, id=subject.file_id)
                       if outcome == RETURN_TO_PLACEMENT else None),
        marked_state=qualifier if outcome == MARK_STATE else None, ask=None,
        decision_depth=DecisionDepth(
            node_depth=entry.depth if entry else 0,
            supported_depth=entry.depth if entry else 0, unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=(CONTEXT_SUPPORTED_GROUP_MATCH if entry is not None
                          else ABSTAIN_NO_SUPPORTED_DESTINATION),
        matching_facts=tuple(evidence["facts"]) if entry is not None else (),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=two,
        abstention_reason=qualifier if outcome == ABSTAIN else None,
        deferred_stage=None, privacy=privacy,
        review_policy=review_policy_for(
            privacy_state=privacy, two_condition=two, group_support=None,
            unique_direct_match=False,
            destination_disposition=entry.disposition if entry else None,
            automatic_move_permitted=automatic_move_permitted),
        explanation=_residual_explanation(residual, outcome, entry),
        residual=residual,
        decided_by=_residual_decider(residual, outcome),
    )
    return _write(conn, decision, inputs=inputs,
                  reason="a later decision about the same file version "
                         "supersedes this residual one (§8.2)",
                  component_version=component_version, observed_at=observed_at)


def _residual_decider(residual: ResidualContext, outcome: str) -> str | None:
    """`104` R-165 on the §7 path: WHO chose a residual destination.

    Read from the set decision, which is the same value `_residual_explanation`
    below already branches on -- so this adds no judgement, it stops throwing one
    away. §7.6's two acting choices are the two actors, and `review_residual_sets`
    lets no other choice reach a decision at all: `send_to_approved_node` writes
    the node the PERSON'S answer already named, with no dossier and no model, and
    `review_with_model_against_approved_residual_folders` writes the action a site
    D verdict carried, which P8 validated exactly as it validates site C's.

    **This is where the register row's own enumeration is departed from**, and
    deliberately. `104` R-165 names site C, `_user_chose` and "`rule` for every
    other `place`", which was written with §6's three exits in view. Applied here
    it would stamp `rule` on a placement whose explanation sentence reads *"Your
    answer names the destination, so nothing was read and no model was asked"* --
    one record with two answers, which is the defect R-165 exists to close, and
    the model's share would be under-counted by every set a person sent to review.

    `None` for any other set decision rather than a guess. `leave_in_place` and
    `create_custom_branch` produce no decision here, so reaching this line with
    one means a caller drove `run_residual_file` past `review_residual_sets`, and
    the honest record of who decided is then "not on the record" -- which is what
    `None` means everywhere else on this field.
    """
    if outcome != PLACE:
        return None
    if residual.set_decision == SEND_TO_APPROVED_NODE:
        return DECIDED_BY_USER
    if residual.set_decision == REVIEW_WITH_MODEL:
        return DECIDED_BY_MODEL
    return None


def _residual_explanation(residual: ResidualContext, outcome: str, entry) -> str:
    """What the person is told about a §7 decision, in the words of the choice
    they made.

    A set sent to an approved node was reviewed by nothing. §7.6 makes
    `send_to_approved_node` a choice that "is already a decision and needs no
    interpretation", so the sentence a person reads under it must not describe a
    residual review returning a verdict -- there was no review, no dossier and no
    model, and saying otherwise would credit a judgement nobody made.
    """
    if residual.set_decision == SEND_TO_APPROVED_NODE and entry is not None:
        return (
            f"You sent this whole review set to {entry.display_label}. Your "
            "answer names the destination, so nothing was read and no model was "
            "asked about these files. Nothing has moved yet.")
    return (f"Residual review of set {residual.set_id} returned {outcome!r}. "
            "The set-level decision authorised this review and the file has not "
            "moved.")


def _residual_action_and_target(inputs: PipelineInputs, verdict) -> tuple[str, object]:
    """§7.7's action and its target, read back through the injected resolver.

    P8 validates `payload["action"]` against `RESIDUAL_ACTIONS` and rewrites the
    verdict's `disposition` into its own coarser vocabulary, so the verdict cannot
    say which of the eight the model chose: `residual_destination` covers both the
    destination choice and the broad parent, and `return_to_placement` covers both
    returns -- and it is the return's KIND that `ReturnTarget` has to record.
    """
    resolver = inputs.residual_action_of
    if not callable(resolver):
        raise ResidualActionUnavailable(
            "§7.7's action lives in the model's response, which P8 validates and "
            "P11 never holds; `residual_action_of` is injected by the caller that "
            "made the call, and absent means refuse rather than guess"
        )
    action, target = resolver(verdict)
    if action not in ACTION_OUTCOME:
        raise ResidualActionUnavailable(
            f"{action!r} is not one of §7.7's eight actions; P8 already refuses "
            "an action outside its controlled set, so reaching here means the "
            "resolver disagreed with P8"
        )
    return action, target


def _review_set_with_model(conn, *, item: ResidualSet, inputs: PipelineInputs,
                           subjects: dict, evidence_for, component_version: str,
                           observed_at: str) -> list[PlacementDecision]:
    """§7.7, per file, for a set whose decision asked for it and no other.

    Site D is P8's; P11 supplies `approved_target_ids` and reads an action.
    `outcome_for_action` maps that action onto one of §6's outcomes, which is why
    a residual decision needs no field the §6 path does not already have.
    """
    written: list[PlacementDecision] = []
    for file_id in item.member_file_ids:
        subject = subjects[file_id]
        privacy = privacy_state_for(conn, file_id=file_id,
                                    content_hash=subject.content_hash,
                                    plan_version=inputs.plan_version)
        evidence = evidence_for(file_id)
        residual = ResidualContext(
            set_id=item.set_id,
            set_decision=require_set_decision(
                conn, plan_version=inputs.plan_version,
                set_id=item.set_id).choice,
            lifecycle_policy_ref=None)
        if not may_assemble_dossier(
                privacy, target_locality=inputs.target_locality(file_id)):
            # §8.4 before the dossier, on the residual path exactly as on the
            # placement path. Protected material does not become releasable
            # because the file reached §7 instead of §6 -- and it is RECORDED
            # rather than skipped, so the file is present-but-untouched and never
            # silently omitted from the review screen.
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=PRIVACY_BLOCKED, residual=residual,
                evidence=evidence, component_version=component_version,
                observed_at=observed_at))
            continue
        retrieval = retrieve(
            conn, subject=subject, plan_version=inputs.plan_version,
            limits=inputs.limits, facts=evidence["facts"],
            group_ids=evidence["group_ids"],
            curated_folder_labels=evidence["curated_folder_labels"],
            semantic_neighbours=evidence["semantic_neighbours"],
            component_version=component_version, observed_at=observed_at)
        result = _judged_or_refused(
            conn, subject=subject, inputs=inputs, retrieval=retrieval,
            evidence=evidence, call_site=D_RESIDUAL, observed_at=observed_at,
            own_folder_node_id=(
                inputs.the_folder_each_file_is_in or {}).get(file_id))
        if isinstance(result, Refusal):
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=PRIVACY_BLOCKED, residual=residual, evidence=evidence,
                component_version=component_version, observed_at=observed_at))
            continue
        if isinstance(result, (CallRefused, PreCallAbstention,
                               CallFailed, ValidationUnavailable)):
            # `104` R-173: a call that failed or could not be judged joins the
            # two below at this site, for the reason given at site C -- the run
            # does not die on the set, and D proposed no destination.
            #
            # `104` R-O, and the residual half of what site C does above: the
            # file stays where the person's own decision put it, recorded and
            # named, rather than the run ending on the set it belongs to.
            # `NO_SUPPORTED_DESTINATION` is the honest qualifier -- D proposes a
            # destination and none was proposed -- and `PRIVACY_BLOCKED` would be
            # the untruth, because §8.4 allowed this dossier.
            #
            # **`PreCallAbstention` JOINS IT HERE** (`104` R-149), and it closes a
            # hole R-136 left open at this site. `_judge_with_model` serves C and
            # D alike, so R-136's three guards could already hand D a
            # `PreCallAbstention` -- and D read only the two types above, so
            # `_require_verdict` raised `ModelJudgementUnavailable` and the run
            # died on the set. Site C has read both since R-136; this is D saying
            # the same sentence. The qualifier's own argument carries over
            # unchanged: D proposes a destination, and a call that was never built
            # proposed none.
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=NO_SUPPORTED_DESTINATION, residual=residual,
                evidence=evidence, component_version=component_version,
                observed_at=observed_at))
            continue
        verdict = _require_verdict(result, call_site=D_RESIDUAL)
        if verdict.outcome in (P8_REJECT, P8_ABSTAIN):
            # P8 refused the model's answer, or there was no answer to act on.
            # Acting on the action anyway would carry out a proposal the validator
            # threw away.
            #
            # `P8_ABSTAIN` IS SITE D'S HALF OF THE OBSERVE LEVER, and it was
            # missing. `_observed_only` rewrites an unratified site's verdict to
            # `abstain` and says both callers then "take their existing abstention
            # path without consulting a resolver" -- which was true at C, where
            # `transcribe` turns every non-`place` outcome into an abstention, and
            # false here: `abstain` is not `reject`, so an unratified D reached
            # `residual_action_of` and the raising stub ended the run on the first
            # file of a set the person had sent to a model. That is the site D twin
            # of the defect `104` §15.1 names at C.
            #
            # Behaviour-preserving for a RATIFIED D, which is why it is a guard and
            # not a new outcome: `_residual_site` rewrites the model's own
            # `abstain` action to this same verdict, and `outcome_for_action`
            # answers `(abstain, NO_SUPPORTED_DESTINATION)` for it, so the decision
            # written here is the decision the resolver path wrote. `weak` is NOT a
            # member: `mark_review_later` arrives as `weak` and is an action the
            # resolver must read.
            written.append(_residual_decision(
                conn, subject=subject, inputs=inputs, outcome=ABSTAIN,
                qualifier=NO_SUPPORTED_DESTINATION, residual=residual,
                evidence=evidence, component_version=component_version,
                observed_at=observed_at))
            continue
        action, target = _residual_action_and_target(inputs, verdict)
        decision = run_residual_file(
            conn, subject=subject, set_id=item.set_id, inputs=inputs,
            evidence=evidence, action=action, target=target,
            component_version=component_version, observed_at=observed_at)
        written.append(decision)
        if decision.outcome == RETURN_TO_PLACEMENT:
            # §7.9: the file actually goes back through §6, and the placement it
            # produces names the residual decision that handed it back. Both
            # records persist; `link_return` refuses if the link is missing.
            placed = place_file(
                conn, subject=subject, inputs=inputs, evidence=evidence,
                returned_from=decision.decision_id,
                component_version=component_version, observed_at=observed_at)
            link_return(conn, residual_decision=decision,
                        placement_decision=placed,
                        component_version=component_version,
                        observed_at=observed_at)
            written.append(placed)
    return written


# --- §6.12 step 9, over a corpus, and §7 after it ------------------------------------


def run_corpus(conn: sqlite3.Connection, *, subjects, group_ids,
               inputs: PipelineInputs, evidence_for, component_version: str,
               observed_at: str) -> CorpusResult:
    """§6 for every subject and every accepted group, then §7 for what is left.

    The two-pass order is contractual, not stylistic. §7.1: residual is *"a
    separate stage that runs only after normal group-aware classification has been
    attempted"*, so every file and every accepted group goes through §6 first and
    only what §6 could not place reaches §7. `surface_residual_sets` refuses a
    `placement_pass_complete=False` caller, so the ordering is enforced by a raise
    rather than by this function remembering to do it.
    """
    decisions: list[PlacementDecision] = []
    plans: list[GroupPlan] = []
    known: dict[str, Subject] = {s.file_id: s for s in subjects if s.file_id}

    # §6.9, detected BEFORE anything is placed. A file with accepted membership in
    # two packets belongs to neither plan alone, and the design is explicit that
    # the engine "should not arbitrarily choose one university"
    # (`01-product-design-structured.md:1255-1259`). Placing it inside the first
    # plan and correcting afterwards would mean the arbitrary choice was made and
    # then withdrawn, which is not the same as never making it.
    accepted = {group_id: accepted_group_as_of(
        conn, group_id=group_id, plan_version=inputs.plan_version)
        for group_id in group_ids}
    homes: dict[str, list[str]] = {}
    for group_id, group in accepted.items():
        for membership in group.memberships:
            known.setdefault(membership.file_id, _member_subject(membership))
            homes.setdefault(membership.file_id, []).append(group_id)
    multi_home = frozenset(file_id for file_id, ids in homes.items()
                           if len(set(ids)) > 1)

    # §6.8 before the per-file pass: a member's decision belongs to its group's
    # plan, and a file placed alone first would be placed against no shared
    # context. `place_group` writes the member decisions itself.
    covered: set[str] = set(multi_home)
    lane = CallLane(width=inputs.calls_at_once)
    for group_id in group_ids:
        plan = place_group(conn, group_id=group_id, inputs=inputs,
                           evidence_for=evidence_for,
                           component_version=component_version,
                           observed_at=observed_at, skip_file_ids=multi_home,
                           lane=lane)
        plans.append(plan)
        decisions.extend(plan.member_decisions)
        covered.update(d.subject.file_id for d in plan.member_decisions)
        covered.update(o.file_id for o in plan.excluded_outliers)

    by_group = {plan.group_id: plan for plan in plans}
    for file_id in sorted(multi_home):
        subject = known[file_id]
        parents = sorted({by_group[group_id].shared_parent_node_id
                          for group_id in homes[file_id]
                          if by_group[group_id].shared_parent_node_id})
        if len(parents) < 2:
            # The packets agree, or neither settled a parent, so there is no
            # competition to resolve and the ordinary path applies.
            decisions.append(place_file(
                conn, subject=subject, inputs=inputs,
                evidence=evidence_for(file_id),
                component_version=component_version, observed_at=observed_at))
            continue
        privacy = privacy_state_for(conn, file_id=file_id,
                                    content_hash=subject.content_hash,
                                    plan_version=inputs.plan_version)
        outcome, payload = resolve_multi_home(
            candidate_node_ids=tuple(parents),
            shared_material_policy=inputs.tree.shared_material_policy,
            shared_branch_node_id=_shared_branch_of(inputs.tree),
            # THE SECOND LOCK, and `_asking` already carries the argument for
            # why there is one: an `ask_user` decision is A REQUEST FOR
            # ATTENTION, a review surface lists what it holds, and `00`:201 says
            # a visible list of protected specifics may not be safe to have on a
            # screen somebody else can see. `104` §18.2 gap 15 turned the
            # composition root's selector from "always abstain" into one that
            # asks, and the selector is handed node ids and nothing else -- it
            # cannot see that this file is a passport. The privacy state is
            # right here, so the refusal is here.
            ask_or_abstain=(_protected_material_is_never_a_question
                            if privacy.protected else inputs.ask_or_abstain))
        decisions.append(_multi_home_decision(
            conn, subject=subject, inputs=inputs, outcome=outcome,
            payload=payload, privacy=privacy,
            automatic_move_permitted=(
                automatic_move_permitted_for(conn, file_id=file_id,
                                             plan_version=inputs.plan_version)
                if privacy.protected else False),
            component_version=component_version, observed_at=observed_at))

    # `104` §18.15: THE PER-FILE PASS, WITH ITS CLOUD ROUND TRIPS SEVERAL AT A
    # TIME. The subjects are walked in the order they arrived and every statement
    # that touches the database still runs on this thread in that order; what the
    # lane holds open is the socket, and only for a file the route sent to the
    # cloud. A file routed local -- protected, or unclassified (§17.13 ruling 3) --
    # is settled by itself before the walk goes on, because one Ollama server
    # holds one model in memory.
    #
    # THE GROUP PASS ABOVE HAS A LANE OF ITS OWN, over its members, for the same
    # reason and in the same shape. THE MULTI-HOME LOOP STAYS SERIAL, and that is
    # not an omission: §6.9 puts a question to the person's own selector between
    # two parents, which is a question with somebody waiting on it, and a file with
    # two homes is a handful of a corpus rather than most of it.
    remaining = ((subject.file_id, place_file_steps(
        conn, subject=subject, inputs=inputs,
        evidence=evidence_for(subject.file_id),
        component_version=component_version, observed_at=observed_at))
        for subject in subjects if subject.file_id not in covered)
    for _file_id, decision in in_walk_order(remaining, lane=lane):
        decisions.append(decision)

    unplaced = tuple(d.subject.file_id for d in decisions
                     if d.outcome != PLACE and d.subject.file_id)

    # `104` R-113. AND EVERY PLACEMENT A POLICY IS HOLDING, which is not the
    # same thing as an unplaced file and belongs on the same screen.
    #
    # A decision can name a destination and still move nothing: an unclassified
    # subject's placement carries `blocked_pending_user` (`review_policy_for`'s
    # first rule), and a move the person has not permitted across their own
    # top-level folders is refused by P12 when the freeze reaches it. Both are
    # `place`, so neither was in `unplaced`, so neither was in any review set --
    # and the review sets are what `--send-set` addresses. The residual screen
    # named these files and offered no gesture that could reach them.
    #
    # `unplaced_file_ids` STAYS NARROW. It is this pipeline's answer to "what
    # did the run fail to place", read by callers that mean exactly that, and a
    # placement with a destination is not one of them. What widens is the list
    # handed to the review screen, which is a different question with a
    # different name.
    held_by_a_policy = tuple(
        d.subject.file_id for d in decisions
        if d.outcome == PLACE and d.subject.file_id
        and (d.review_policy == BLOCKED_PENDING_USER
             or (inputs.a_move_the_person_has_not_permitted is not None
                 and d.destination is not None
                 and inputs.a_move_the_person_has_not_permitted(
                     d.subject.file_id, d.destination.node_id) is not None)))

    # §7.5. The §6 pass is complete for the corpus, which is the only condition
    # under which a file may be called residual.
    sets: tuple[ResidualSet, ...] = surface_residual_sets(
        conn, plan_version=inputs.plan_version,
        unplaced=unplaced + held_by_a_policy,
        partition=inputs.partition, limits=inputs.limits,
        placement_pass_complete=True, component_version=component_version,
        observed_at=observed_at)

    return CorpusResult(
        decisions=tuple(decisions), group_plans=tuple(plans),
        residual_sets=sets, unplaced_file_ids=unplaced, subjects=known,
        # `104` §18.15: WHAT THE LANE ACTUALLY DID, not what it was allowed to
        # do. `calls_at_once` on the inputs is the setting; this is the
        # measurement, and the report prints this one.
        calls_at_once=lane.at_once)


def review_residual_sets(conn: sqlite3.Connection, *, result: CorpusResult,
                         inputs: PipelineInputs, evidence_for,
                         component_version: str,
                         observed_at: str) -> tuple[PlacementDecision, ...]:
    """§7.6 and §7.7, for the sets the user decided and no others.

    This is a SECOND call and not the tail of `run_corpus`, because the user
    decides between the two. §7.6's gate is "no per-file residual model call may
    be issued for a set until that set has a decision", and the decision arrives
    from the review screen after the sets were surfaced -- so a single pass that
    surfaced and reviewed in one breath could only ever be reviewing a decision
    made about some earlier run's sets.

    Two of §7.6's four choices reach a file here, and only one of them costs
    anything. `review_with_model_against_approved_residual_folders` runs §7.7 per
    file; `send_to_approved_node` writes the placement the answer already named,
    with no dossier and no model. The other two produce nothing HERE and that is
    the whole of their meaning: `leave_in_place` is zero calls and no move by the
    user's own choice (SPEC:547), and `create_custom_branch` is a tree edit routed
    to P10 that mints a new plan version, so this version's review of that set is
    over.
    """
    written: list[PlacementDecision] = []
    for item in result.residual_sets:
        # Surfaced and not yet decided is the state §7.6's gate exists to make
        # visible. It is left alone rather than refused: a review screen full of
        # undecided sets is the ordinary one, not a broken run.
        try:
            set_decision = require_set_decision(
                conn, plan_version=inputs.plan_version, set_id=item.set_id)
        except SetDecisionRequired:
            continue
        if not (model_calls_permitted(set_decision)
                or set_decision.choice == SEND_TO_APPROVED_NODE):
            continue
        # One gate per branch, and both begin at `require_set_actionable`, so
        # protection is checked FIRST whichever way the set is being acted on.
        # `ProtectedSetNotReadable` is deliberately NOT caught: it fires only when
        # a decision asked to act on a protected set, and answering that by
        # skipping would record it as understood and found unimportant -- which is
        # exactly what the set stays on the review screen, counted and explained,
        # to prevent. A protected set nobody decided never reaches these lines.
        if set_decision.choice == SEND_TO_APPROVED_NODE:
            require_set_actionable(conn, plan_version=inputs.plan_version,
                                   residual_set=item)
            written.extend(_send_set_to_approved_node(
                conn, item=item, decision=set_decision, inputs=inputs,
                subjects=result.subjects, evidence_for=evidence_for,
                component_version=component_version, observed_at=observed_at))
            continue
        require_model_call_permitted(conn, plan_version=inputs.plan_version,
                                     residual_set=item)
        written.extend(_review_set_with_model(
            conn, item=item, inputs=inputs, subjects=result.subjects,
            evidence_for=evidence_for, component_version=component_version,
            observed_at=observed_at))
    return tuple(written)


class ResidualSendRefused(RuntimeError):
    """A §7.6 set answer named a review set or a residual area this run has not.

    A misspelling that quietly sent nothing would be the run reporting success
    for work it did not do, and the person would find out by looking for files
    that are not there. So it refuses -- and names what this run DID surface,
    because a refusal that does not say what to type is half a refusal.
    """


def approved_residual_area(conn: sqlite3.Connection, *, plan_version: str,
                           display_label: str):
    """One enabled residual area of THIS plan version, by the name a person reads.

    §7.4 makes an approved residual branch an ordinary legal node carrying
    `node_role = residual`, so the lookup is over the frozen index and is filtered
    by that role. An ordinary domain branch is a legal destination and is NOT a
    residual area: §7.6's choice is `send_to_approved_node` among the residual
    homes the user enabled, and letting it name `Academics` would file every
    unplaced file into the main tree -- the pollution §7.1 and §7.12 exist to
    prevent.
    """
    areas = tuple(entry for entry in entries_for_plan(conn,
                                                      plan_version=plan_version)
                  if entry.node_role == RESIDUAL_ROLE)
    named = sorted({entry.display_label for entry in areas})
    matches = tuple(entry for entry in areas
                    if entry.display_label == display_label)
    if len(matches) > 1:
        raise ResidualSendRefused(
            f"{display_label!r} names {len(matches)} residual areas of "
            f"{plan_version!r} and §7.6 sends a set to ONE approved node; "
            "choosing between them here would be P11 picking the destination")
    if not matches:
        raise ResidualSendRefused(
            f"{display_label!r} is not a residual area of this plan. It has "
            + (", ".join(repr(name) for name in named) if named else
               "none -- enable one first, and nothing can be sent to an area "
               "that does not exist"))
    return matches[0]


def _send_set_to_approved_node(conn: sqlite3.Connection, *, item: ResidualSet,
                               decision: ResidualSetDecision,
                               inputs: PipelineInputs, subjects: dict,
                               evidence_for, component_version: str,
                               observed_at: str) -> list[PlacementDecision]:
    """§7.6's `send_to_approved_node`, carried out, with ZERO model calls.

    The action recorded is §7.7's third -- "choose one approved residual
    destination" -- because that is what the record has to say happened, and the
    residual context on every one of these decisions carries
    `set_decision = send_to_approved_node`, which is what says WHO chose it. A
    reader can tell a set the person filed from a set a model interpreted without
    reading a second table.
    """
    return [
        run_residual_file(
            conn, subject=subjects[file_id], set_id=item.set_id, inputs=inputs,
            evidence=evidence_for(file_id), action=CHOOSE_RESIDUAL_DESTINATION,
            target=decision.node_id, component_version=component_version,
            observed_at=observed_at)
        for file_id in item.member_file_ids
    ]


def act_on_residual_sets(conn: sqlite3.Connection, *, result: CorpusResult,
                         inputs: PipelineInputs, sends, evidence_for,
                         component_version: str, observed_at: str,
                         user_id: str) -> CorpusResult:
    """§7.6's set answers for THIS plan version, recorded and then carried out.

    `sends` maps a surfaced set's LABEL -- the words the person read on the review
    screen -- to the display label of an enabled residual area, and it is not a
    remembered preference. SPEC "Plan versioning" puts residual set decisions IN a
    plan version, *"not [in] the shared evidence database"*, and every run mints a
    new one. So an answer given about one run's sets is not an answer about
    another's, and it is asked for again rather than carried forward: the thing it
    authorises is a destination for files the person has just been shown, and
    applying it unseen to a set surfaced by a later tree would be this product
    filing material against a screen nobody read.

    That is why the address is the LABEL and not the `set_id`. §7.5's set carries
    both; the `set_id` is minted as `plan_version:label` and so is different in
    every run, while the label is what §7.5 puts on the screen and what a person
    can type back. P11 invents no third identity, and there is no stable
    cross-version one to invent.

    Returns the corpus result the report should be written from: the same sets,
    counted and never dropped, with the decisions these answers replaced.
    """
    by_label: dict[str, list[ResidualSet]] = {}
    for item in result.residual_sets:
        by_label.setdefault(item.label, []).append(item)
    # EVERY pair is resolved before ANY is recorded. Recording as it goes would
    # let `--send-set A --send-set typo` file A and then refuse the run, leaving
    # an answer standing for a plan the person was never shown -- a refusal that
    # half happened is the one thing worse than a refusal.
    resolved: list[tuple[ResidualSet, str]] = []
    for label, area_label in sends.items():
        if label not in by_label:
            raise ResidualSendRefused(
                f"{label!r} is not a review set this run surfaced. It surfaced "
                + (", ".join(repr(name) for name in sorted(by_label))
                   if by_label else "none, so there is nothing to send"))
        area = approved_residual_area(conn, plan_version=inputs.plan_version,
                                      display_label=area_label)
        resolved.extend((item, area.node_id) for item in by_label[label])
    for item, node_id in resolved:
        record_set_decision(
            conn,
            ResidualSetDecision(set_id=item.set_id,
                                plan_version=inputs.plan_version,
                                choice=SEND_TO_APPROVED_NODE, node_id=node_id,
                                decided_at=observed_at),
            component_version=component_version, observed_at=observed_at,
            user_id=user_id)
    written = review_residual_sets(
        conn, result=result, inputs=inputs, evidence_for=evidence_for,
        component_version=component_version, observed_at=observed_at)
    if not written:
        return result
    # The §6 decision these replaced is superseded in the table by `_identity`;
    # the returned result has to agree with the table or the report describes a
    # run that no longer exists. The SETS are untouched: one was surfaced, counted
    # and explained, and a screen that deletes a set once it is acted on cannot
    # show what happened to it.
    revised = {decision.subject.file_id for decision in written}
    kept = tuple(decision for decision in result.decisions
                 if decision.subject.file_id not in revised)
    decisions = kept + tuple(written)
    return dataclasses.replace(
        result, decisions=decisions,
        unplaced_file_ids=tuple(
            decision.subject.file_id for decision in decisions
            if decision.outcome != PLACE and decision.subject.file_id))

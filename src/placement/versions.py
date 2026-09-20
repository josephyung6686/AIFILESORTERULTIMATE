"""§8.8's re-projection. It marks, and it never matches.

A placement decision belongs to a plan version because it is a projection of one
frozen tree. When a new version is adopted, every decision is re-examined against
the new legal set and exactly one thing can happen to it: its node still exists
and the decision carries, or its node is gone and the decision is marked as
requiring renewed review.

There is deliberately no third branch. A removed node often has a plausible
survivor -- the whole reason a node was removed is usually that another one
replaced it -- and matching onto it is the "silent reclassification" §8.8
prohibits by name. §8.8's own example is a COUNT of files needing review, not a
count of files quietly moved.

"Still exists" is a question about LINEAGE, not about `node_id`. P10 mints a new
`node_id` for every plan version and records the lineage in `origin_node_id`
(its OQ5; `planning/38-p10-p11-connection-contract.md` §5.2). Matching on
`node_id` would therefore find no successor for ANY node and mark every decision
for renewed review after any tree edit at all -- including a pure rename, which
§8.8 forbids by name. So the match runs
`decision.destination.node_id -> from-version entry -> origin_node_id ->
to-version entry`, and a decision is marked only when NO successor shares that
origin.

A rename is not a removal, and neither is a move. P10 rewrites `display_label`
(or `parent_node_id`) and mints a new id; the origin is unchanged, so the decision
carries and produces no review at all. The label and path the user now sees are
composed by P12 from the new chain.

**The mark is the diff, and the diff is computed.** `reproject` writes nothing.
`store.py` is append-only by doctrine -- "Nothing here rewrites a decision" -- so
stamping `review_policy` onto an existing row would be the one mutation the store
exists to forbid, and it would make §8.8's answer depend on when it was last run
rather than on the two versions themselves.

**`carry_onto` is the other half of the same sentence, and it appends.** §8.8's
"the decision carries" had never been WRITTEN: `reproject` says which decisions
survive a new version and nothing put them there, so a run that edited its own
plan after placing (`104` §18.2 gap 11c) left half its decisions addressing a
tree the person is no longer being shown -- the report joins labels to decisions
by `node_id`, and a decision naming the old version's id joins to nothing. So the
carry is a NEW row per decision whose `supersedes` names the old one, which is
§8.2's rule and not an exception to it. Nothing is rewritten here either.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from placement.index import IndexEntry, entries_for_plan
from placement.records import Destination, PlacementDecision
from placement.store import decisions_for_plan, record_decision, subject_ref_of
from placement.vocabulary import (
    ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, PLACE, SCOPED_GENERAL,
)

#: The two verdict outcomes that still support a placement. Named, not sliced out
#: of `VERDICTS`: a slice silently changes meaning the day P8 reorders its tuple,
#: and the two it would then admit are `weak` and `reject`.
_STILL_SUPPORTS: frozenset[str] = frozenset(
    {ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED})


@dataclass(frozen=True)
class VersionDiff:
    from_plan_version: str
    to_plan_version: str
    requiring_renewed_review: tuple[str, ...]
    carried_unchanged: tuple[str, ...]
    removed_node_ids: tuple[str, ...]

    @property
    def renewed_review_count(self) -> int:
        """§8.8's sentence is a count; the caller should not have to derive one."""
        return len(self.requiring_renewed_review)


def reproject(conn: sqlite3.Connection, *, from_plan_version: str,
              to_plan_version: str, revalidation_inputs=None) -> VersionDiff:
    """Which decisions survive the new version, and which need the user again.

    `revalidation_inputs` is an optional mapping `decision_id -> dict`, one entry
    per decision that was decided by a MODEL. A deterministic decision has no P8
    verdict and nothing to re-validate, which is why the mapping is sparse rather
    than a field on every record. Each entry supplies exactly the keywords
    `llm_harness.placement_validation.revalidate_for_plan` requires --
    `previous_verdict_id`, `dossier`, `response_bytes`, `evidence_resolver`,
    `contradicts`, `dependencies`, `model_id`, `prompt_fingerprint`,
    `dossier_builder`, `release_audit_id`, `handle_key` and `observed_at` --
    because P11 stores none of them and the caller that made the call holds them
    all. `handle_key` is the local-only key the dossier's bytes were built with
    (`llm_harness.wire_handles`): the stored response cites the handles the model
    was shown, and without the key there is no way back to what they name.

    A verdict that re-validates as unavailable or refused joins
    `requiring_renewed_review` beside the removed-node cases: the node survived,
    but the judgement about it did not, and §8.8 says a new plan never silently
    carries a placement whose basis no longer holds.
    """
    # The two maps this whole function turns on. `origin_of` reads the version
    # the decisions were made against; `successors` reads the new one. Neither is
    # keyed on `node_id` across the boundary, because P10 mints a new one per
    # version and an id match would find nothing for any node.
    origin_of = {entry.node_id: entry.origin_node_id
                 for entry in entries_for_plan(conn,
                                               plan_version=from_plan_version)}
    successors = {entry.origin_node_id
                  for entry in entries_for_plan(conn,
                                                plan_version=to_plan_version)}
    needs_review: list[str] = []
    carried: list[str] = []
    removed: set[str] = set()
    for decision in decisions_for_plan(conn, plan_version=from_plan_version):
        if decision.outcome != PLACE or decision.destination is None:
            # It named no node, so no node's removal invalidates it. An
            # abstention under the old tree is still an abstention under the new
            # one until the evidence changes.
            continue
        node_id = decision.destination.node_id
        # A decision whose own node is not in the from-version index at all has
        # no lineage to follow, which is itself a reason to ask the user again.
        origin = origin_of.get(node_id)
        if origin is None or origin not in successors:
            needs_review.append(decision.decision_id)
            removed.add(node_id)
            continue
        if _revalidates(conn, decision, to_plan_version, revalidation_inputs):
            carried.append(decision.decision_id)
        else:
            needs_review.append(decision.decision_id)
    return VersionDiff(
        from_plan_version=from_plan_version, to_plan_version=to_plan_version,
        requiring_renewed_review=tuple(needs_review),
        carried_unchanged=tuple(carried),
        removed_node_ids=tuple(sorted(removed)),
    )


def _revalidates(conn, decision, to_plan_version: str, inputs) -> bool:
    """P8 re-checks its own verdict against the new version. P11 re-checks nothing.

    `revalidate_for_plan` is P8's (`placement_validation.py`) and records the new
    verdict itself. P11 supplies the current plan version and the current evidence
    snapshot and reads the answer -- the same authorities-in, verdict-out shape as
    Site C, one version later.

    **THE SNAPSHOT IS THE DOSSIER'S, NOT THE FACTS'** (`104` R-155). This minted
    the current snapshot from `decision.matching_facts` while `_judge_with_model`
    minted the original from the dossier's `evidence_items` (R-148), so the two
    ids addressed different sets and `revalidate_for_plan`'s "has the snapshot
    changed" compared a hash of one thing with a hash of another. Both directions
    were wrong: a dossier that gained a reading and kept its facts looked
    unchanged and was carried without re-validation, and a file whose facts moved
    while its dossier stood still re-validated against a change the model was
    never shown -- a fresh verdict, a superseded old one, and a model call's worth
    of work for nothing.

    The items are AT HAND here and were the whole time. `entry["dossier"]` is the
    `Dossier` `revalidate_for_plan` requires two lines below, `build_dossier`
    copies `request.evidence_items` onto it verbatim, and `_judge_with_model`
    builds the request from the same tuple -- so the stored dossier's items ARE
    what the model saw, read back rather than reconstructed.
    """
    entry = (inputs or {}).get(decision.decision_id)
    if entry is None:
        # No model verdict backs this decision, so there is nothing to
        # re-validate and the node's survival is the whole question. NOTHING IS
        # HASHED on this branch and that is the honest answer to "what does the
        # revalidation path address when no dossier exists" (`104` R-155): a
        # decision reached without a model has no dossier, no verdict and no
        # snapshot, so there is no evidence set for a snapshot to address and
        # minting one over the facts would be P11 addressing a call nobody made.
        return True
    from llm_harness.placement_validation import revalidate_for_plan
    from llm_harness.records import ValidationUnavailable

    from placement.p8_seam import evidence_snapshot_id_for, snapshot_observation_keys

    result = revalidate_for_plan(
        conn, current_plan_version=to_plan_version,
        current_evidence_snapshot_id=evidence_snapshot_id_for(
            plan_version=to_plan_version,
            observation_keys=snapshot_observation_keys(
                entry["dossier"].evidence_items)),
        observed_at=entry["observed_at"], **{
            key: entry[key] for key in (
                "previous_verdict_id", "dossier", "response_bytes",
                "evidence_resolver", "contradicts", "dependencies", "model_id",
                "prompt_fingerprint", "dossier_builder", "release_audit_id",
                # The key the dossier's bytes were built with. A re-validation
                # reads the model's references, so it needs the way back from
                # what the model saw; absent, `revalidate_for_plan` refuses.
                "handle_key")
        })
    if isinstance(result, ValidationUnavailable):
        return False
    return result.outcome in _STILL_SUPPORTS


class NodeHasNoSuccessor(RuntimeError):
    """A decision names a node the new version has no lineage for."""


#: What the person is told when a folder was created because their own file
#: needed it. `84` §6: no section number, no field word, and the actor named --
#: the branch gained the folder, and it gained it FOR THIS FILE.
_MINTED_FOR_THIS_FILE: str = (
    "the catch-all inside that folder was created for this file, because this "
    "file belongs in that folder and in none of the folders beside it"
)

#: §8.2 requires a reason on every supersede, and the two are different facts: one
#: decision changed where the file goes, and the rest changed only which version
#: of the plan they are about.
_CARRIED: str = (
    "the plan gained a folder after this decision was made, and §8.8 re-projects "
    "every decision onto the version the person is shown"
)
_MOVED_INTO_THE_GENERAL: str = (
    "this branch's catch-all folder was created because of this file, so the "
    "file goes into it rather than staying at the folder above it (`00`:99)"
)


def _current(decisions: Sequence[PlacementDecision],
             ) -> tuple[PlacementDecision, ...]:
    """One decision per subject: the LAST the pass reached, in first-seen order.

    `run_corpus` returns what it decided in the order it decided it, and a subject
    can be decided twice in one pass -- a group member placed by its packet and
    then resolved again as shared material is the shape that does it. The second
    row supersedes the first, so the earlier one is a decision the run itself
    withdrew: reading demand from it would mint a folder for a placement that no
    longer stands, and re-projecting it would make it live again in the new
    version. `store.record_decision`'s own index says the same thing from the
    other side -- one live decision per subject per version -- and `mark_superseded`
    refuses to link a row that is already linked, so a run that reached here with
    a withdrawn row would end rather than quietly resurrect it.

    First-seen order, not last: the run's own order is what the report prints, and
    a file changing places in the list because it was decided twice is a screen
    that reorders itself for a reason nobody reading it can see.
    """
    latest: dict[str, PlacementDecision] = {}
    for decision in decisions:
        latest[subject_ref_of(decision.subject)] = decision
    return tuple(latest.values())


def scoped_general_demand(decisions: Sequence[PlacementDecision], *,
                          tree) -> dict[str, tuple[str, ...]]:
    """Which parents the placement pass proved owe a scoped General, and to whom.

    `104` §18.2 gap 11c and the owner's ruling of 10 Sep: the General is minted ON
    DEMAND, only under a parent that actually has a file whose accepted facts
    support the parent and no leaf, never under every branch. `00`:99 makes the
    branch optional -- "the future tree CAN include
    Academics/Columbia/2026-Spring/General" -- and `cli.py` answered it with `()`
    for the reason it recorded: an unasked question answered by default is a
    folder nobody wanted. This is the question finally being ASKED, by the only
    pass that is in a position to answer it.

    **DEMAND IS A PLACEMENT OUTCOME AND CANNOT BE ANYTHING ELSE.** The file that
    wants a General is the one gap 11b's decision half already names: placed on an
    ancestor the shortlist offered, with `unsupported_levels` filled, which is
    SPEC:401-404's record of a decision that deliberately left the levels below it
    unfilled. The tree pass runs BEFORE placement, so nothing earlier in the run
    knows it -- which is the ordering question §18.30 put to the owner and this
    function is the answer to.

    Keyed on `origin_node_id`, because that is the identity a review action names
    (`tree_design.store._write_overlap_answer` matches the parent by lineage) and
    because minting opens a draft, which mints a new `node_id` for every node.

    **A PARENT THAT ALREADY HAS A GENERAL IS NOT IN DEMAND.** That General was on
    this file's own shortlist as a set-aside
    (`pipeline._the_parents_own_general_is_offered`) and whoever decided placed
    the file on the parent anyway. Minting a second one -- or moving the file into
    the first -- would be this function overruling the judgement it asked for.

    Values are file ids in the order they were decided, deduplicated; keys are
    sorted, so two runs over one corpus mint the same Generals in the same order.
    """
    by_id = {node.node_id: node for node in tree.nodes}
    already = {node.parent_node_id for node in tree.nodes
               if getattr(node, "node_role", None) == SCOPED_GENERAL}
    demand: dict[str, list[str]] = {}
    for decision in _current(decisions):
        if decision.outcome != PLACE or decision.destination is None:
            continue
        # The shallow-decision record, and nothing else. An empty tuple is a file
        # filed as deep as its evidence goes, which wants no catch-all.
        if not decision.decision_depth.unsupported_levels:
            continue
        file_id = decision.subject.file_id
        node = by_id.get(decision.destination.node_id)
        if not file_id or node is None or node.node_id in already:
            continue
        # A file already IN a General carries the levels its siblings bind, which
        # is the same field saying something else entirely. A General under a
        # General is the global catch-all `00`:99 refuses, one level down.
        if getattr(node, "node_role", None) == SCOPED_GENERAL:
            continue
        demand.setdefault(node.origin_node_id, []).append(file_id)
    return {origin: tuple(dict.fromkeys(files))
            for origin, files in sorted(demand.items())}


def carry_onto(conn: sqlite3.Connection, *,
               decisions: Sequence[PlacementDecision],
               from_tree, to_tree,
               into_general: Mapping[str, IndexEntry],
               component_version: str,
               observed_at: str) -> tuple[PlacementDecision, ...]:
    """§8.8's "the decision carries", written: every decision onto the new version.

    One appended row per decision, whose `supersedes` names the row it re-projects
    and whose destination is the SAME NODE under the new version's id -- found the
    way `reproject` finds it, `node_id -> origin_node_id -> node_id`, because P10
    mints a new id per version and an id match would find nothing for any node.

    **EVERY NODE ID ON THE RECORD IS REMAPPED, not only the destination.** The
    alternatives, the suppressed nodes and their `found_on` pairs, and an `ask`'s
    options are all node ids of the version the decision was made against; a
    carried record that kept them would cite folders the new version does not
    have, on the same screen as a destination that does. `graph_anchors` and
    `matching_facts` are file and fact ids and are untouched.

    **`into_general` IS THE ONE THING THAT CHANGES, and it changes one field.**
    A file whose demand minted a General goes into it: the destination becomes the
    General and the depth becomes the General's own. `decided_by` is carried
    UNCHANGED from whoever decided the shallow placement -- the model or the rules
    chose that branch and this does not revisit that; what changed is that the
    branch now has the folder `00`:99 says the file belongs in. Every other field
    -- the evidence, the two-condition measurement, the review policy -- is the
    same evidence it was, so it is copied rather than re-derived.

    `supported_depth` becomes the General's depth beside `node_depth`, and that is
    the record's own arithmetic rather than a claim about the evidence:
    `DecisionDepth` refuses `node_depth > supported_depth` as a filled slot, and a
    General fills no slot -- it states no expected value and binds no level. It is
    what `_place_one` already writes when the judge picks a General for itself.
    `unsupported_levels` is carried untouched: the levels this file did not settle
    are the same levels, whichever side of the branch's catch-all it is filed on.

    **THE LINEAGE IS READ OFF THE TWO FROZEN TREES AND NOT OFF THE INDEX**, which
    is the one place this differs from `reproject` above and it is not a
    preference. The index holds LEGAL nodes only, and a record's node ids are not
    all legal ones: `index._terms_of` writes a `parent_node_id` term whose key is
    the PARENT of a legal node, so `_chain_around`'s walk up can name an ancestor
    that accepts no placement, and gap 16's `found_on` can carry it into a
    conflict. Looked up in the index that id has no successor -- and raising here
    would end a run AFTER every model call in it was spent, with the new version
    frozen and half the decisions carried. A frozen tree carries every node P10
    wrote, legal or not, which is the same set `open_draft` copies, so every id a
    record can hold has an answer.

    Raises rather than guessing when a node has no successor even so. Nothing is
    REMOVED by minting a General, so a missing successor means the two versions
    disagree about the tree, and a decision quietly dropped or matched onto a
    plausible neighbour is §8.8's "silent reclassification" by name.

    **ONE ROW PER SUBJECT, AND IT IS THE ONE THE PASS ENDED ON** -- `_current`,
    the same reading `scoped_general_demand` takes, so the folder that was minted
    and the decision that lands in it can never be answering two different states
    of the same run.
    """
    to_plan_version = to_tree.plan_version_id
    origin_of = {node.node_id: node.origin_node_id for node in from_tree.nodes}
    successors = {node.origin_node_id: node for node in to_tree.nodes}

    def _successor(node_id: str):
        node = successors.get(origin_of.get(node_id, ""))
        if node is None:
            raise NodeHasNoSuccessor(
                f"{node_id!r} is named by a decision in "
                f"{from_tree.plan_version_id!r} and {to_plan_version!r} carries "
                "no node with its lineage. A plan that gained a folder removed "
                "none, so the two versions disagree about the tree -- and "
                "carrying the decision onto a plausible survivor is the silent "
                "reclassification §8.8 forbids"
            )
        return node

    carried: list[PlacementDecision] = []
    for decision in _current(decisions):
        general = (into_general.get(decision.subject.file_id or "")
                   if decision.outcome == PLACE else None)
        destination, depth, explanation = (
            decision.destination, decision.decision_depth, decision.explanation)
        reason = _CARRIED
        if general is not None:
            destination = Destination(node_id=general.node_id,
                                      node_role=general.node_role)
            depth = dataclasses.replace(depth, node_depth=general.depth,
                                        supported_depth=general.depth)
            explanation = (explanation.rstrip(".") + "; "
                           + _MINTED_FOR_THIS_FILE + ".")
            reason = _MOVED_INTO_THE_GENERAL
        elif destination is not None:
            entry = _successor(destination.node_id)
            destination = Destination(node_id=entry.node_id,
                                      node_role=entry.node_role)
        subject_ref = subject_ref_of(decision.subject)
        moved = dataclasses.replace(
            decision,
            decision_id=f"{to_plan_version}:{subject_ref}:{observed_at}",
            plan_version=to_plan_version,
            supersedes=decision.decision_id,
            superseded_by=None, supersede_reason=None,
            destination=destination, decision_depth=depth,
            explanation=explanation,
            ask=None if decision.ask is None else dataclasses.replace(
                decision.ask,
                options=tuple(_successor(node).node_id
                              for node in decision.ask.options)),
            conflicts_considered=tuple(
                dataclasses.replace(
                    conflict,
                    suppressed_node_ids=tuple(
                        _successor(node).node_id
                        for node in conflict.suppressed_node_ids),
                    found_on=tuple(
                        (_successor(ruled).node_id, _successor(found).node_id)
                        for ruled, found in conflict.found_on))
                for conflict in decision.conflicts_considered),
            alternatives=tuple(
                dataclasses.replace(item,
                                    node_id=_successor(item.node_id).node_id)
                for item in decision.alternatives),
        )
        record_decision(conn, moved, component_version=component_version,
                        observed_at=observed_at, supersede_reason=reason)
        carried.append(moved)
    return tuple(carried)


def learned_preferences_still_applicable(conn: sqlite3.Connection, *,
                                         plan_version: str,
                                         suppressions) -> tuple:
    """§8.8: preferences carry across versions, filtered by node existence.

    A rejection of a node that no longer exists is still a true fact about what
    the user decided, and it is preserved -- it is simply not applied, because
    there is nothing left for it to suppress. Deleting it instead would lose the
    reason if the node ever came back.

    "Still exists" is the same lineage question `reproject` asks, and for the same
    reason: a suppression recorded against an earlier version names that version's
    `node_id`, which P10's per-version minting guarantees is absent from the new
    one. Filtered on `node_id`, EVERY learned preference would silently stop
    applying at the first tree edit -- the opposite of "preferences carry across
    versions". So the filter matches either identity: a suppression whose id is a
    current node id, or one whose id is an earlier node with a surviving origin.

    **The earlier node's id is RESOLVED, not compared.** Testing
    `item.node_id in surviving_origins` reads correctly and is only true when the
    earlier node's id happens to equal its own origin -- which held for the FIRST
    plan version and for no other, because every later version mints, and since
    `106` Phase 5.1 holds for NO version at all: an origin is a composed key
    (`tree_design.node_key`) and a `node_id` is a per-run mint, so the two can no
    longer coincide even there. So a preference recorded against plan-2 and
    filtered against plan-3 was matched against neither identity and was dropped
    in silence. `_origins_by_node_id`
    does the resolution the sentence describes: earlier `node_id` -> that
    version's `origin_node_id` -> does the new version still carry it.

    A node id that appears in two versions with different lineage is ambiguous
    rather than wrong, so every origin it ever had is considered and the
    preference applies if ANY of them survives. Keeping the preference is the
    safe side of that ambiguity: §8.7 exists so a rejected destination is not
    resurfaced, and dropping one silently is the failure it names.
    """
    entries = entries_for_plan(conn, plan_version=plan_version)
    surviving_ids = {entry.node_id for entry in entries}
    surviving_origins = {entry.origin_node_id for entry in entries}
    origins = _origins_by_node_id(conn)
    return tuple(item for item in suppressions
                 if item.node_id in surviving_ids
                 or item.node_id in surviving_origins
                 or origins.get(item.node_id, frozenset()) & surviving_origins)


def _origins_by_node_id(conn: sqlite3.Connection) -> dict[str, frozenset[str]]:
    """Every indexed node id, and the lineage it carried in each version.

    Read from the index rather than from P10's `tree_nodes`, for the reason
    `legal_node_ids` gives: P11 answers identity questions from its own
    projection of the frozen tree, and a second source could disagree with the
    one P8's `node_exists` is closed over.
    """
    found: dict[str, set[str]] = {}
    for row in conn.execute(
            "SELECT node_id, payload FROM placement_index_entries"):
        origin = json.loads(row["payload"])["origin_node_id"]
        found.setdefault(row["node_id"], set()).add(origin)
    return {node_id: frozenset(items) for node_id, items in found.items()}

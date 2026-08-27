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

**The mark is the diff, and the diff is computed.** Nothing here writes to
`placement_decisions`. `store.py` is append-only by doctrine -- "Nothing here
rewrites a decision" -- so stamping `review_policy` onto an existing row would be
the one mutation the store exists to forbid, and it would make §8.8's answer
depend on when it was last run rather than on the two versions themselves.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from placement.index import entries_for_plan
from placement.store import decisions_for_plan
from placement.vocabulary import ACCEPT_CONTEXT_SUPPORTED, ACCEPT_DIRECT, PLACE

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
    `dossier_builder`, `release_audit_id` and `observed_at` -- because P11 stores
    none of them and the caller that made the call holds them all.

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
    """
    entry = (inputs or {}).get(decision.decision_id)
    if entry is None:
        # No model verdict backs this decision, so there is nothing to
        # re-validate and the node's survival is the whole question.
        return True
    from llm_harness.placement_validation import revalidate_for_plan
    from llm_harness.records import ValidationUnavailable

    from placement.p8_seam import evidence_snapshot_id_for

    result = revalidate_for_plan(
        conn, current_plan_version=to_plan_version,
        current_evidence_snapshot_id=evidence_snapshot_id_for(
            plan_version=to_plan_version,
            observation_keys=tuple(fact.evidence_ref
                                   for fact in decision.matching_facts)),
        observed_at=entry["observed_at"], **{
            key: entry[key] for key in (
                "previous_verdict_id", "dossier", "response_bytes",
                "evidence_resolver", "contradicts", "dependencies", "model_id",
                "prompt_fingerprint", "dossier_builder", "release_audit_id")
        })
    if isinstance(result, ValidationUnavailable):
        return False
    return result.outcome in _STILL_SUPPORTS


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
    """
    entries = entries_for_plan(conn, plan_version=plan_version)
    surviving_ids = {entry.node_id for entry in entries}
    surviving_origins = {entry.origin_node_id for entry in entries}
    return tuple(item for item in suppressions
                 if item.node_id in surviving_ids
                 or item.node_id in surviving_origins)

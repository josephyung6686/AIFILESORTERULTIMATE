# src/tree_design/store.py
"""Versioned writes and current reads. A frozen version is immutable.

§8.8 is the whole contract: an edit opens a draft, the draft is comparable to its
predecessor by a node-level diff, the user may restore an earlier version or
adopt the new one, and adoption "never silently reclassifies or moves old files".

Node identity is minted per version, with `origin_node_id` carrying the lineage,
because SPEC open question 5 is open. That choice is deliberately the reversible
one: if node ids turn out to be stable across versions, `origin_node_id` becomes
`node_id` and nothing else changes; the other choice cannot be undone.
"""
from __future__ import annotations

import contextlib
import dataclasses
import sqlite3
from collections.abc import Callable, Iterator, Sequence

from evidence_shape.canonical import canonical_json
from tree_design.records import (
    ExpectedValue,
    derive_accepts_placement,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
    TemplateContext,
)
from tree_design.provenance import (
    actor_phrase,
    record_plan_version_adoption,
    record_tree_edit,
    surface_phrase,
)
from tree_design.vocabulary import (
    ACCEPT,
    ADD_SCOPED_GENERAL,
    ADOPT_EXISTING,
    BRANCH_BEARING_SHARED_POLICIES,
    CREATE_MANUALLY,
    DELETE,
    DISABLE_RESIDUAL,
    ENABLE_RESIDUAL,
    IGNORE,
    MERGE,
    NEST,
    RENAME,
    REORDER,
    REPARENT,
    SCOPED_GENERAL,
    SET_SHARED_MATERIAL_POLICY,
    SHARED_MATERIAL,
    SHARED_MATERIAL_POLICIES,
    SPLIT,
    USER_CREATED,
    TREE_EDIT_ACTIONS,
    VERSION_ACTIONS,
    check,
)

_NODE_COLUMNS = (
    "node_id", "plan_version_id", "origin_node_id", "node_type", "display_label",
    "parent_node_id", "root_anchor", "ordinal", "associated_group_ids",
    "explanation", "node_role", "accepts_placement",
    "protected_movement_permitted", "handling_class", "template_context",
    "dimension_role", "dimension", "existing_path", "disposition",
    "refinement_disposition", "refinement_reason",
)


class FrozenVersionImmutable(RuntimeError):
    """§8.8: a frozen version is never amended in place. An edit opens a draft.

    This names exactly one condition: a write reached a version whose state is
    `frozen`. It is NOT the refusal for an action that cannot be applied — a
    caller that catches this to mean "open a draft and retry" would retry forever
    on an action that has no writer at all.
    """


class ReviewActionRefused(RuntimeError):
    """One review action was not applied, and no plan version was created.

    Separate from `FrozenVersionImmutable` because the two ask for opposite
    things from a caller: a frozen version says "edit a draft instead", a refused
    action says "this edit cannot be made at all".
    """


class UnknownPlanVersion(RuntimeError):
    """A plan version id that no row carries.

    `UPDATE ... WHERE plan_version_id = ?` and `SELECT ... WHERE
    plan_version_id = ?` both succeed quietly against an absent id, so a mistyped
    version froze nothing and reported success.
    """


#: The five tree edits this module writes.
ACTIONS_WITH_A_WRITER: frozenset[str] = frozenset({
    ACCEPT, RENAME, IGNORE, ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY,
})

#: The twelve that do not have one yet, SPELLED OUT rather than derived by
#: subtraction. Deriving them would make the "every action is in one set or the
#: other" test a tautology — a check that can never fire — and the point of the
#: check is that a sixteenth member of `TREE_EDIT_ACTIONS` cannot quietly inherit
#: a refusal nobody decided on.
#:
#: Each is a canvas gesture whose semantics are §5.2's and §5.10's; none is
#: blocked on an upstream part. They are the honest remaining scope, and they are
#: refused by name BEFORE anything is written, because a refusal that arrives
#: after the draft is open leaves the user a new version that changed nothing.
ACTIONS_WITH_NO_WRITER: frozenset[str] = frozenset({
    MERGE, SPLIT, NEST, REPARENT, REORDER, DELETE, CREATE_MANUALLY,
    ADOPT_EXISTING, ENABLE_RESIDUAL, DISABLE_RESIDUAL,
})


@contextlib.contextmanager
def one_transaction(conn: sqlite3.Connection) -> Iterator[None]:
    """Every write of one edit, or none of them. Public: `freeze` uses it too.

    `open_database` connects with `isolation_level=None`, so each statement
    commits on its own. Without this boundary a refusal raised after `open_draft`
    left the draft version and its whole copied tree COMMITTED — one accepted
    edit becoming one plan version regardless of whether the edit happened.

    A caller that already owns a transaction keeps it; nesting here would either
    fail outright or commit that caller's work early.
    """
    if conn.in_transaction:
        yield
        return
    conn.execute("BEGIN")
    try:
        yield
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


def _require_version(conn: sqlite3.Connection, plan_version_id: str) -> str:
    state = _state(conn, plan_version_id)
    if state is None:
        raise UnknownPlanVersion(
            f"no plan version {plan_version_id!r} exists. A version id that "
            "matches no row is a typo or a stale reference, and answering it "
            "with silence lets a caller believe a version it named was acted on."
        )
    return state


def _state(conn: sqlite3.Connection, plan_version_id: str) -> str | None:
    row = conn.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = ?",
        (plan_version_id,)).fetchone()
    return None if row is None else row["state"]


def write_plan_version(conn: sqlite3.Connection, version: PlanVersion) -> None:
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) VALUES (?, ?, ?, ?, ?, ?)",
        (version.plan_version_id, version.predecessor_id, version.state,
         version.created_at, int(version.cross_folder_moves), version.selection_id),
    )


def write_node(conn: sqlite3.Connection, node: Node) -> None:
    if _state(conn, node.plan_version_id) == "frozen":
        raise FrozenVersionImmutable(
            f"plan version {node.plan_version_id!r} is frozen. §8.8 requires an "
            "edit to open a DRAFT version and show a diff; amending a frozen "
            "version in place would change what the user already approved."
        )
    values = (
        node.node_id, node.plan_version_id, node.origin_node_id, node.node_type,
        node.display_label, node.parent_node_id, node.root_anchor, node.ordinal,
        canonical_json(list(node.associated_group_ids)), node.explanation,
        node.node_role, int(node.accepts_placement),
        int(node.protected_movement_permitted), node.handling_class,
        None if node.template_context is None else canonical_json({
            "binding_id": node.template_context.binding_id,
            "template_id": node.template_context.template_id,
            "template_version": node.template_context.template_version,
            "dimension_index": node.template_context.dimension_index,
            "fragment_id": node.template_context.fragment_id,
            "fragment_version": node.template_context.fragment_version,
        }),
        node.dimension_role, node.dimension, node.existing_path, node.disposition,
        node.refinement_disposition, node.refinement_reason,
    )
    conn.execute(
        f"INSERT OR REPLACE INTO tree_nodes ({','.join(_NODE_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(_NODE_COLUMNS))})",
        values,
    )
    for expected in node.expected_values:
        conn.execute(
            "INSERT OR IGNORE INTO node_expected_values "
            "(plan_version_id, node_id, field_key, value) VALUES (?, ?, ?, ?)",
            (node.plan_version_id, node.node_id, expected.field, expected.value),
        )


def _row_to_node(conn: sqlite3.Connection, row: sqlite3.Row) -> Node:
    import json

    context = row["template_context"]
    expected = conn.execute(
        "SELECT field_key, value FROM node_expected_values "
        "WHERE plan_version_id = ? AND node_id = ? ORDER BY field_key, value",
        (row["plan_version_id"], row["node_id"])).fetchall()
    return Node(
        node_id=row["node_id"],
        plan_version_id=row["plan_version_id"],
        origin_node_id=row["origin_node_id"],
        node_type=row["node_type"],
        display_label=row["display_label"],
        parent_node_id=row["parent_node_id"],
        root_anchor=row["root_anchor"],
        ordinal=row["ordinal"],
        associated_group_ids=tuple(json.loads(row["associated_group_ids"])),
        explanation=row["explanation"],
        node_role=row["node_role"],
        accepts_placement=bool(row["accepts_placement"]),
        protected_movement_permitted=bool(row["protected_movement_permitted"]),
        handling_class=row["handling_class"],
        template_context=None if context is None else TemplateContext(
            **json.loads(context)),
        dimension_role=row["dimension_role"],
        dimension=row["dimension"],
        expected_values=tuple(
            ExpectedValue(field=e["field_key"], value=e["value"]) for e in expected),
        existing_path=row["existing_path"],
        disposition=row["disposition"],
        refinement_disposition=row["refinement_disposition"],
        refinement_reason=row["refinement_reason"],
    )


def nodes_for_version(conn: sqlite3.Connection,
                      plan_version_id: str) -> tuple[Node, ...]:
    rows = conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? "
        "ORDER BY ordinal, node_id", (plan_version_id,)).fetchall()
    return tuple(_row_to_node(conn, row) for row in rows)


def freeze_version(conn: sqlite3.Connection, plan_version_id: str) -> None:
    """Mark a version frozen. Task 16 owns the validation that precedes this."""
    _require_version(conn, plan_version_id)
    conn.execute(
        "UPDATE plan_versions SET state = 'frozen' WHERE plan_version_id = ?",
        (plan_version_id,))


def set_shared_material_policy(conn: sqlite3.Connection,
                               policy: SharedMaterialPolicy) -> None:
    """§6.9's policy. `policy_scope IS NULL` means tree-global, and the schema's
    partial unique index allows exactly one of those per version."""
    conn.execute(
        "INSERT INTO shared_material_policies "
        "(policy_id, plan_version_id, policy, policy_scope, reason) "
        "VALUES (?, ?, ?, ?, ?)",
        (policy.policy_id, policy.plan_version_id, policy.policy,
         policy.policy_scope, policy.reason),
    )


def _carry_shared_material(conn: sqlite3.Connection, *, from_version: str,
                           new_version_id: str) -> None:
    """§6.9's policy travels with the version it was chosen for.

    `open_draft` copied the NODES and left this behind, and the consequence was
    not local. `freeze._shared_material` reads
    `shared_material_policies WHERE plan_version_id = ?`; a draft with no row
    made `validate_for_freeze` refuse with "this plan version carries no §6.9
    shared-material policy" — about a version whose predecessor carries one and
    whose shared-material NODE had just been copied across intact. A user who
    chose `primary-home` and then renamed one folder was told they had chosen
    nothing.

    A COPY, with a new `policy_id`, not a shared row: `policy_id` is the primary
    key, and §8.8 makes the predecessor immutable, so the two versions each keep
    their own record and a later change to one cannot rewrite the other.

    `policy_scope` is carried verbatim. P10's OQ9 — tree-global or per-branch —
    is open, and flattening every row to global here would settle it.
    """
    rows = conn.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = ? "
        "ORDER BY policy_id", (from_version,)).fetchall()
    for index, row in enumerate(rows):
        conn.execute(
            "INSERT INTO shared_material_policies "
            "(policy_id, plan_version_id, policy, policy_scope, reason) "
            "VALUES (?, ?, ?, ?, ?)",
            (f"{new_version_id}:smp{index}", new_version_id, row["policy"],
             row["policy_scope"], row["reason"]),
        )


def open_draft(conn: sqlite3.Connection, *, from_version: str,
               new_version_id: str, created_at: str,
               mint_node_id: Callable[[], str]) -> PlanVersion:
    """Copy a version's tree into a new draft, preserving lineage and shape."""
    row = conn.execute(
        "SELECT * FROM plan_versions WHERE plan_version_id = ?",
        (from_version,)).fetchone()
    if row is None:
        raise UnknownPlanVersion(
            f"plan version {from_version!r} does not exist; a draft is opened "
            "FROM something")
    draft = PlanVersion(
        plan_version_id=new_version_id, predecessor_id=from_version,
        state="draft", created_at=created_at,
        cross_folder_moves=bool(row["cross_folder_moves"]),
        selection_id=row["selection_id"],
    )
    write_plan_version(conn, draft)

    source = nodes_for_version(conn, from_version)
    remap = {node.node_id: mint_node_id() for node in source}
    for node in source:
        copied = dataclasses.replace(
            node,
            node_id=remap[node.node_id],
            plan_version_id=new_version_id,
            parent_node_id=(None if node.parent_node_id is None
                            else remap[node.parent_node_id]),
        )
        write_node(conn, copied)
    _carry_shared_material(conn, from_version=from_version,
                           new_version_id=new_version_id)
    return draft


def _write_overlap_answer(conn: sqlite3.Connection, action, *, draft: PlanVersion,
                          mint_node_id: Callable[[], str],
                          component_version: str) -> str:
    """§6.9's shared branch and `00`:99's scoped General — the design's two named
    answers to "this file belongs in more than one place, or in none of them".

    Both were deferred as ordinary canvas gestures. They are not: `SCOPED_GENERAL`
    and `SHARED_MATERIAL` are two of P10's four node roles, both were carried on
    `Node` and checked by `NODE_ROLES`, and NEITHER HAD A WRITER — so §6.9's
    `shared-branch`, `primary-home` and `reference-or-alias` all reached P11 with
    no `shared_branch_node_id` and fell through to the same ask-or-abstain as
    `mandatory-review`. Three of four policies collapsed into one.

    The parent is `action.subject_ref`, matched by lineage. Both roles are
    SCOPED: `00`:99 asks for "a scoped General or Other branch WITHIN A
    MEANINGFUL PARENT" and adds that "a global catch-all folder should not become
    the product's default answer to ambiguity", and §6.9's shared branch has to
    sit ABOVE the competing homes — `placement.groups.resolve_multi_home` refuses
    a `shared_branch_node_id` that is one of the candidates, because placing
    there IS choosing between them.
    """
    parent = next(
        (node for node in nodes_for_version(conn, draft.plan_version_id)
         if node.origin_node_id == action.subject_ref), None)
    if parent is None:
        raise ReviewActionRefused(
            f"review action {action.review_action_id!r} puts a "
            f"{action.action!r} branch under {action.subject_ref!r}, which this "
            "version does not contain. Both roles are SCOPED to a parent, and a "
            "global catch-all folder is what the design refuses"
        )

    if action.action == ADD_SCOPED_GENERAL:
        role, label = SCOPED_GENERAL, action.payload.get("display_label", "General")
        explanation = (
            f"{actor_phrase(action.surface)} added a scoped {label!r} inside "
            f"{parent.display_label!r} for files that belong to this branch but "
            "settle no value at the level below it."
        )
    else:
        policy = check(action.payload["policy"], SHARED_MATERIAL_POLICIES,
                       name="shared material policy")
        reason = action.payload.get("reason") or ""
        if not reason.strip():
            raise ReviewActionRefused(
                f"§6.9's policy for {action.subject_ref!r} carries no reason. The "
                "policy decides what happens to a file that belongs in two "
                "places, and one recorded without a reason cannot be reviewed"
            )
        scope = action.payload.get("policy_scope")
        # The draft already carries the predecessor's answer, because
        # `_carry_shared_material` copied it. This action IS the user changing
        # that answer, so the carried row for the same scope is replaced rather
        # than joined: `one_global_shared_material_policy` is a partial unique
        # index and a second global row raises `IntegrityError`, which would
        # leave the user unable to revise a policy they had already given.
        #
        # The DELETE is scoped to this draft. Every earlier version keeps its
        # own row, which is §8.8's immutability: what the user chose then is
        # still what that frozen version was adopted under.
        conn.execute(
            "DELETE FROM shared_material_policies WHERE plan_version_id = ? "
            "AND policy_scope IS ?", (draft.plan_version_id, scope))
        set_shared_material_policy(conn, SharedMaterialPolicy(
            policy_id=f"smp_{draft.plan_version_id}_{action.review_action_id}",
            plan_version_id=draft.plan_version_id, policy=policy,
            policy_scope=scope, reason=reason))
        if policy not in BRANCH_BEARING_SHARED_POLICIES:
            # `mandatory-review` is the one policy that does NOT resolve to a
            # destination: it means ask the user. A branch for it would answer
            # the question the policy exists to keep open.
            _record_overlap_edit(conn, action, draft=draft, node_id=parent.node_id,
                                 label=parent.display_label,
                                 component_version=component_version,
                                 explanation=(
                                     f"{actor_phrase(action.surface)} set "
                                     f"§6.9's {policy!r} policy, which sends "
                                     "shared material to review rather than to "
                                     "a branch."))
            return draft.plan_version_id
        role = SHARED_MATERIAL
        label = action.payload.get("display_label", "Shared Material")
        explanation = (
            f"{actor_phrase(action.surface)} set §6.9's {policy!r} policy and "
            f"this branch is where material belonging to more than one home "
            f"under {parent.display_label!r} goes, so no single home is chosen "
            "for it."
        )

    node_id = mint_node_id()
    node = Node(
        node_id=node_id, plan_version_id=draft.plan_version_id,
        node_type=USER_CREATED, display_label=label,
        parent_node_id=parent.node_id, root_anchor=parent.root_anchor,
        ordinal=parent.ordinal + 1, associated_group_ids=(),
        explanation=explanation, node_role=role,
        accepts_placement=derive_accepts_placement(
            USER_CREATED, protected_movement_permitted=False),
        handling_class=parent.handling_class, origin_node_id=node_id,
        refinement_disposition=parent.refinement_disposition,
        refinement_reason=parent.refinement_reason,
    )
    write_node(conn, node)
    _record_overlap_edit(conn, action, draft=draft, node_id=node_id, label=label,
                         component_version=component_version,
                         explanation=explanation)
    return draft.plan_version_id


def _record_overlap_edit(conn, action, *, draft, node_id, label,
                         component_version, explanation) -> None:
    record_tree_edit(
        conn, action=action.action, node_id=node_id,
        plan_version_id=draft.plan_version_id, before={},
        after={"display_label": label},
        explanation=explanation, observed_at=action.observed_at,
        user_id=action.user_id, component_version=component_version,
        correction_scope=action.correction_scope,
        correction_subject=action.subject_ref, polarity="accept")


def apply_review_action(conn: sqlite3.Connection, action, *,
                        new_version_id: str, created_at: str,
                        mint_node_id: Callable[[], str],
                        component_version: str,
                        project: Callable[[object, str], Sequence[Node]] | None = None,
                        ) -> str:
    """One accepted edit, one new plan version (M8, §8.8) — or neither.

    P13 presents and collects; it decides nothing. P10 authors the edit, the edit
    produces a version, and P1 writes the event.

    `project` is how an ACCEPT becomes nodes. It is injected rather than imported
    because `store.py` writes records and does not build them: the caller binds
    `materialise.project_branch_nodes` (Task 12) to the branch's evidence and its
    validation report, and this module writes whatever comes back. Passing `None`
    is legal for every other action and refused for `accept`, so a caller that
    forgets it gets a refusal rather than an accepted branch with no folders —
    which is the failure this seam exists to make impossible.

    **Every action is refused before it is begun, or written inside one
    transaction.** The order matters and it is the repair this function most
    needed. Every check that can be made without touching the database is made
    first: the action name against `TREE_EDIT_ACTIONS`, then against
    `ACTIONS_WITH_NO_WRITER`, then `project` for an `accept`. Only then is a
    draft opened, and it is opened inside `one_transaction`, so a refusal that
    can only be discovered later — an empty projection, a subject this version
    does not hold — rolls the draft back rather than leaving the user a new plan
    version with a full copy of the tree and no edit in it.

    **The twelve actions with no writer.** `TREE_EDIT_ACTIONS` has fifteen
    members and this function writes three. The other twelve are named in
    `ACTIONS_WITH_NO_WRITER` and refused by name, before any lookup, so `merge`
    against a node this version does not contain reports that `merge` has no
    writer rather than complaining about the node. A misspelling is a different
    failure again and raises `OutOfVocabulary`, because "a rename with no writer"
    is the wrong description of a name P10 does not define.
    """
    if action.action in VERSION_ACTIONS:
        with one_transaction(conn):
            draft = open_draft(conn, from_version=action.subject_ref,
                               new_version_id=new_version_id,
                               created_at=created_at, mint_node_id=mint_node_id)
            record_plan_version_adoption(
                conn, plan_version_id=draft.plan_version_id,
                action=action.action,
                explanation=(
                    f"The user chose to {action.action.replace('_', ' ')} "
                    f"{action.subject_ref!r}, which opens a new draft."),
                observed_at=action.observed_at, user_id=action.user_id,
                component_version=component_version)
        return draft.plan_version_id

    # A name outside the closed set is a load error, not an unbuilt gesture.
    check(action.action, TREE_EDIT_ACTIONS, name="tree edit action")

    if action.action in ACTIONS_WITH_NO_WRITER:
        raise ReviewActionRefused(
            f"{action.action!r} is one of the {len(ACTIONS_WITH_NO_WRITER)} tree "
            "edit actions P10 defines and has not built a writer for. It is "
            "refused here, before anything is written: a silent no-op still "
            "opens a draft, and the user would see a new plan version that "
            "changed nothing."
        )

    if action.action == ACCEPT and project is None:
        raise ReviewActionRefused(
            f"review action {action.review_action_id!r} accepts "
            f"{action.subject_ref!r} but no projection was supplied; an accepted "
            "branch that writes no node is a silent no-op"
        )

    with one_transaction(conn):
        draft = open_draft(conn, from_version=action.plan_version,
                           new_version_id=new_version_id, created_at=created_at,
                           mint_node_id=mint_node_id)

        if action.action == ACCEPT:
            # §5.12's "evidence-backed proposed branches" enter the tree HERE and
            # nowhere else. The subject is a candidate, not yet a node, so there
            # is no `target` to look up.
            projected = tuple(project(action, draft.plan_version_id))
            if not projected:
                raise ReviewActionRefused(
                    f"accepting {action.subject_ref!r} produced no node. §5.4 "
                    "populates a template from facts that already exist; when "
                    "none of the branch's files carry a settled value at any "
                    "dimension there is nothing to build, and the branch stays a "
                    "candidate"
                )
            for node in projected:
                write_node(conn, node)
            record_tree_edit(
                conn, action=ACCEPT, node_id=projected[0].node_id,
                plan_version_id=draft.plan_version_id, before={},
                after={"display_label": projected[0].display_label,
                       "node_count": len(projected)},
                explanation=(
                    f"{actor_phrase(action.surface)} accepted "
                    f"{action.subject_ref!r}"
                    f"{surface_phrase(action.surface)}; it became "
                    f"{len(projected)} node(s) built from facts P6 had already "
                    "settled."),
                observed_at=action.observed_at, user_id=action.user_id,
                component_version=component_version,
                correction_scope=action.correction_scope,
                correction_subject=action.subject_ref, polarity="accept")
            return draft.plan_version_id

        if action.action in (ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY):
            return _write_overlap_answer(
                conn, action, draft=draft, mint_node_id=mint_node_id,
                component_version=component_version)

        # §8.8 IDENTITY: the draft minted new node ids, so the action's subject is
        # matched on `origin_node_id`. Matching on `node_id` would fail to find
        # the very node the user acted on.
        target = next(
            (node for node in nodes_for_version(conn, draft.plan_version_id)
             if node.origin_node_id == action.subject_ref), None)
        if target is None:
            raise ReviewActionRefused(
                f"review action {action.review_action_id!r} names node "
                f"{action.subject_ref!r}, which this version does not contain")

        before = {"display_label": target.display_label,
                  "node_type": target.node_type}
        if action.action == RENAME:
            edited = dataclasses.replace(
                target, display_label=action.payload["display_label"])
        else:
            # IGNORE. `ACTIONS_WITH_A_WRITER` has three members, `accept` returned
            # above and `rename` is handled above, so this branch is `ignore` and
            # nothing else: every other name was refused before the draft opened.
            edited = dataclasses.replace(
                target, node_type="ignored", accepts_placement=False,
                existing_path=None)
        write_node(conn, edited)
        record_tree_edit(
            conn, action=action.action, node_id=edited.node_id,
            plan_version_id=draft.plan_version_id, before=before,
            after={"display_label": edited.display_label,
                   "node_type": edited.node_type},
            explanation=(
                f"{actor_phrase(action.surface)} applied {action.action!r} to "
                f"{before['display_label']!r}"
                f"{surface_phrase(action.surface)}."),
            observed_at=action.observed_at, user_id=action.user_id,
            component_version=component_version,
            correction_scope=action.correction_scope,
            correction_subject=action.subject_ref, polarity="accept")
        return draft.plan_version_id

"""The transaction. `00`:153-156's four verification points around one move.

*"Treat every filesystem mutation as a transaction with preconditions, execution
steps, verification, and a reversible journal entry"* (`00`:155). This module is
that sentence: it evaluates the precondition twice, creates only the directories
the frozen node needs, performs one move, tells P1 where the file went, verifies
it there, and appends a journal entry that makes the move reversible. It decides
nothing about where a file belongs.

**The one ordering that is not interchangeable, and the reason this module has a
suite of its own.** P1's `verify_content(conn, file_id, expected_hash)` hashes
`files.current_path` (`database_agent/verify.py:45-49`). It takes no path,
because P1 owns identity and a caller passing a path could ask P1 to certify a
file P1 does not know. So V3 -- *"after completing the action"* -- can only be
asked AFTER `observe_path` has moved `current_path` to the destination. Asked a
moment earlier it hashes the source path the rename just emptied, `hash_file`
raises `OSError`, `verify_content` turns that into `"mismatch"`, and a move that
completed perfectly is recorded as `failed:v3_hash_mismatch`. The move is
therefore: rename -> `observe_path` -> V3, and never any other order.

**Nothing here overwrites, and that is now the system call's guarantee rather
than a check's.** `collision.py` guarantees the executor never receives an
occupied destination and this module re-checks it immediately before the move
anyway -- but both checks read a `FilesystemConstraints` table that describes one
process, not one disk, and under `os.rename` a table that is wrong about the
volume is a destroyed file rather than a wrong answer. The move is therefore
`mutation.movement.move_onto_free_path`, which fails atomically on an occupied
destination under the VOLUME's own folding rules. That closes the window this
docstring used to name.

The earlier text ruled the fix out on §7.11 -- that hard-linking adds an `unlink`
to a part whose only permitted `unlink` is the cross-volume source removal. The
plan had already answered that (F14, `2026-08-29-p12-apply-undo.md`:5316): after
a successful `os.link` the two paths are the same inode, so unlinking one removes
a NAME and not a file, and §7.11 forbids deleting a file. `os.link` + `os.unlink`
is what the plan specified for this branch; the implementation drifted to
`os.rename` and this is the drift undone.

**A destination that is taken is `stale:destination_changed`** -- §8.3's own name
for it, and the plan's. It is a recorded stop with a sentence, never a traceback:
`_create_directories` has already run by then, so a `FileExistsError` escaping
`apply_plan` would leave folders behind with no execution record explaining them.

**No numeric literal beyond 0 and 1 appears in this file.** Every bound, clock,
name and policy arrives injected; absent means refuse (A7).
"""
from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Callable, Mapping, Sequence
import dataclasses
from dataclasses import asdict, dataclass
from pathlib import Path
from types import MappingProxyType

from database_agent.files_table import get_file, observe_path
from database_agent.verify import VerificationPoint, verify_content
from evidence_shape.canonical import canonical_json
from scan_agent.basic_record import parent_folder_context

from mutation.approval import ReviewApproval, approval_verdict, protection_verdict
from mutation.collision import find_collision, record_collision, resolve_collision
from mutation.constraints import FilesystemConstraints
from mutation.cross_volume import (
    UnverifiedCopyDispositionRequired, copy_and_confirm,
)
from mutation.events import (
    record_executed_move, record_failed_move, record_refused_move,
)
from mutation.movement import move_onto_free_path
from mutation.plan import MovePlan
from mutation.preconditions import evaluate_preconditions
from mutation.special import inspect_objects
from mutation.vocabulary import (
    APPLIED, ATOMIC_RENAME, AWAITING_COLLISION_DECISION,
    CROSS_VOLUME_COPY_AND_DELETE, DESTINATION_CHANGED, ENTRY_APPLIED,
    EXECUTION_MODES, FAILED, FAILURE_CLASSES, JOURNAL_ENTRY_KINDS,
    NODE_REFUSES_PLACEMENT, PAUSE_REASONS, PAUSED, PRE_APPLY, PREPARE,
    REFUSAL_CLASSES, REFUSED, RESULT_KINDS, STALE, STALENESS_TRIGGERS,
    SUBSYSTEM, V3_HASH_MISMATCH, V4_DESTINATION_UNCONFIRMED, check,
)

#: Which vocabulary a `<kind>:<detail>` result's detail half belongs to. `applied`
#: is absent because it has no detail half -- there is one way for a move to have
#: worked and four families of ways for it not to have.
_RESULT_DETAILS: Mapping[str, tuple[str, ...]] = {
    REFUSED: REFUSAL_CLASSES,
    STALE: STALENESS_TRIGGERS,
    PAUSED: PAUSE_REASONS,
    FAILED: FAILURE_CLASSES,
}


#: An empty, immutable detail. A default argument that is a fresh `{}` would be
#: a mutable default; a module-level `{}` would be one any caller could fill.
_NO_DETAIL: Mapping[str, object] = MappingProxyType({})


class BatchPolicyRequired(RuntimeError):
    """`74` §8 Q6's bound or halt rule is absent, or the batch exceeds the bound.

    NOT a refusal class. A refusal describes a plan that could not execute and
    carries a sentence for the person; this is the composition root having failed
    to state a policy that is its own to state, and dressing it as a refusal would
    put a message about the person's files in front of a wiring mistake.
    """


def result_of(kind: str, detail: str | None = None) -> str:
    """Contract out §5's `Result`, as one checked string."""
    check(kind, RESULT_KINDS, name="result kind")
    if kind == APPLIED:
        if detail is not None:
            raise ValueError("`applied` carries no detail; a move either worked "
                             "or it is one of the other four kinds")
        return APPLIED
    check(detail, _RESULT_DETAILS[kind], name=f"{kind} detail")
    return f"{kind}:{detail}"


@dataclass(frozen=True)
class ExecutionRecord:
    """Contract out §5. The transaction result, carrying P1's four points."""

    plan_id: str
    #: `None` when the run stopped before a move was ever attempted -- there was
    #: no rename and no copy, so there is no mode it was performed in.
    mode: str | None
    hash_at_preparation: str | None
    hash_immediately_before_move: str | None
    #: P1's `"match"` / `"mismatch"` at V3, or `None` when nothing was moved.
    hash_after_completion: str | None
    #: Cross-volume only. `None` on every same-volume action, which is not a
    #: failure to confirm but a question that was never asked.
    destination_confirmed_pre_removal: bool | None
    result: str
    final_destination_path: str | None
    directories_created_by_this_action: tuple[str, ...]
    started_at: str
    finished_at: str
    #: What the gate that stopped this move knew, beyond its class. Empty on an
    #: applied move and on every stop whose class already says everything.
    #:
    #: **This exists because `protection_verdict`'s docstring promised it and
    #: nothing carried it.** Contract out §5 gives ONE refusal class for §8.4 --
    #: `protected_without_policy` -- and two very different things land on it:
    #: *"this file is protected and no policy permits it"* and *"nothing has
    #: looked at this file"*. The reason travelled as far as the event and
    #: stopped, because this record had nowhere to put it, so a person whose
    #: file nothing had classified read "This item is protected by your privacy
    #: policy". On a corpus with no detector that is the ORDINARY state and the
    #: most confusing possible thing to say about it.
    #:
    #: A second refusal CLASS would have been the tidier shape, and it is not
    #: available: `REFUSAL_CLASSES` is closed and adding a member needs the
    #: owner's approval recorded at the member. Carrying the detail says the
    #: same thing without inventing vocabulary, and it is the half
    #: `apply_run.report` needs to say two sentences.
    detail: Mapping[str, object] = _NO_DETAIL

    def __post_init__(self) -> None:
        kind, _, detail = self.result.partition(":")
        result_of(kind, detail or None)
        if self.mode is not None:
            check(self.mode, EXECUTION_MODES, name="execution mode")

    @property
    def applied(self) -> bool:
        return self.result == APPLIED


@dataclass(frozen=True)
class JournalEntry:
    """Contract out §6 -- §8.3's five, plus what reversal needs.

    Append-only: an undo appends a reversal entry and this one stays exactly as
    written (§8.2). That is why there is no `superseded` notion here and no
    `one_current` index on `move_journal` (`schema.py`).
    """

    entry_id: str
    entry_kind: str
    reverses_entry_id: str | None
    plan_id: str
    plan_version: str
    file_id: str
    hash_algorithm: str
    original_source_path: str
    destination_path: str
    content_hash_at_movement: str
    collision_behaviour: str
    post_move_verification_result: str
    source_volume: str
    destination_volume: str
    execution_mode: str
    directories_created_by_this_action: tuple[str, ...]
    intended_display_name: str
    filesystem_safe_name: str
    time_of_execution: str

    def __post_init__(self) -> None:
        check(self.entry_kind, JOURNAL_ENTRY_KINDS, name="journal entry kind")
        check(self.execution_mode, EXECUTION_MODES, name="execution mode")

    @classmethod
    def for_plan(cls, conn: sqlite3.Connection,
                 plan_id: str) -> "JournalEntry | None":
        row = conn.execute(
            "SELECT payload FROM move_journal WHERE plan_id = ? "
            "AND entry_kind = ? ORDER BY record_id LIMIT 1",
            (plan_id, ENTRY_APPLIED)).fetchone()
        return None if row is None else cls._from_payload(row[0])

    @classmethod
    def _from_payload(cls, payload: str) -> "JournalEntry":
        raw = json.loads(payload)
        raw["directories_created_by_this_action"] = tuple(
            raw["directories_created_by_this_action"])
        return cls(**raw)


def record_execution(conn: sqlite3.Connection, record: ExecutionRecord, *,
                     plan_version: str, record_id: str) -> str:
    conn.execute(
        "INSERT INTO execution_records (record_id, plan_id, plan_version, "
        "result, mode, final_destination_path, finished_at, payload) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (record_id, record.plan_id, plan_version, record.result, record.mode,
         record.final_destination_path, record.finished_at,
         # `asdict` deep-copies, and a `mappingproxy` cannot be copied. The
         # detail is unwrapped to the plain mapping it wraps for the write; the
         # read side wraps it again, so no caller ever holds a mutable one.
         canonical_json({**asdict(dataclasses.replace(record, detail={})),
                         "detail": dict(record.detail)})))
    return record_id


def record_journal_entry(conn: sqlite3.Connection, entry: JournalEntry, *,
                         record_id: str) -> str:
    conn.execute(
        "INSERT INTO move_journal (record_id, entry_id, entry_kind, "
        "reverses_entry_id, plan_id, plan_version, file_id, "
        "original_source_path, destination_path, content_hash, "
        "time_of_execution, payload) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (record_id, entry.entry_id, entry.entry_kind, entry.reverses_entry_id,
         entry.plan_id, entry.plan_version, entry.file_id,
         entry.original_source_path, entry.destination_path,
         entry.content_hash_at_movement, entry.time_of_execution,
         canonical_json(asdict(entry))))
    return record_id


def directories_to_create(directory: Path) -> tuple[Path, ...]:
    """The ancestors of `directory` that do not exist, shallowest first.

    Shallowest first is what a reversal needs: F2 removes them deepest-first, so
    the order recorded here is the order to walk backwards.
    """
    missing: list[Path] = []
    current = directory
    while not current.exists() and current != current.parent:
        missing.append(current)
        current = current.parent
    return tuple(reversed(missing))


def _create_directories(directory: Path) -> tuple[str, ...]:
    """Create them, and return exactly the ones THIS call created.

    `mkdir()` without `exist_ok`: a directory that appeared between the check and
    the call was not created here, and recording it as though it were would make
    a reversal a candidate to remove somebody else's folder.
    """
    created: list[str] = []
    for path in directories_to_create(directory):
        path.mkdir()
        created.append(str(path))
    return tuple(created)


def _observe_at(conn: sqlite3.Connection, plan: MovePlan, destination: Path, *,
                normalize_filename: Callable[[str], str], scan_state: str,
                materialized: bool, component_version: str) -> None:
    """Tell P1 the file is at `destination`. This is what makes V3 answerable.

    `observe_path` resolves the same bytes at a new path whose old path is gone
    to the SAME file version and updates `current_path`
    (`files_table.py:426-443`); on that branch the descriptive arguments are not
    read at all. They are supplied truthfully anyway, from P1's own current row,
    because a caller must not depend on which branch it will take:

    * `observed_size` and `observed_timestamps` are carried forward unchanged.
      A rename preserves both, and P3's timestamp REPRESENTATION is its open
      Q2 -- re-encoding a stat here would author a format P3 declined to.
    * `normalize_filename` is injected with no default for the same reason. P3
      SPEC Q1 is open on Unicode form, case folding and separator collapse, so
      P3 passes the name through unchanged and P12 may not choose differently.
      The composition root supplies P3's answer, whatever it becomes.
    * `parent_folder_context` is imported from P3 rather than recomputed. A
      second derivation of a published field is the drift P3's own Task 10 test
      exists to catch.
    """
    row = get_file(conn, plan.file_id)
    observe_path(
        conn, destination, author=SUBSYSTEM, component_version=component_version,
        filename=destination.name,
        normalized_filename=normalize_filename(destination.name),
        extension=row["extension"], observed_size=row["observed_size"],
        observed_timestamps=row["observed_timestamps"],
        parent_folder_context=parent_folder_context(destination),
        mime_type=row["mime_type"], detected_format=row["detected_format"],
        scan_state=scan_state, materialized=materialized)


def _inside(candidate: Path, root: Path) -> bool:
    """Whether `candidate` really lands under `root`, `..` collapsed.

    `strict=False` throughout: neither path need exist yet -- the destination
    directory is created later and the root may be a folder the person has not
    made -- and a non-existent path still resolves its `..` components. A root
    that cannot be resolved at all is not a root this move may land in, so the
    `OSError` is False rather than an exception: a person with a broken symlink
    on the path gets a refusal with a sentence, not a traceback.
    """
    try:
        return candidate.resolve(strict=False).is_relative_to(
            root.resolve(strict=False))
    except OSError:
        return False


def _atomic_rename(source: Path, destination: Path, *,
                   constraints: FilesystemConstraints) -> None:
    """One same-volume move that never lands on an occupied path.

    Two answers to the same question, deliberately. The first is by
    `find_collision`, not `Path.exists()`: on a case-insensitive volume
    `exists()` misses an NFC/NFD twin, and it is exactly the twin a person
    cannot tell apart that must not be written over -- and it names WHICH entry
    collided, which `move_onto_free_path` cannot. The second is the move itself,
    which refuses an occupied destination under the volume's rules rather than
    the declared ones. The first is the better diagnosis; the second is the one
    that holds when the declaration is wrong.

    Both raise `FileExistsError`, so `apply_plan` has one branch to catch.
    """
    if find_collision(destination.parent, destination.name,
                      constraints=constraints) is not None:
        raise FileExistsError(
            f"{destination} is occupied; the executor is never handed an "
            "occupied path (§8.3, `00`:172)")
    move_onto_free_path(source, destination)


def apply_plan(conn: sqlite3.Connection, plan: MovePlan, *,
               legal_destination_ids: frozenset[str],
               source_root: Path,
               destination_root: Path,
               extra_protected: Callable[[Path], bool] | None,
               conflict_copies: Callable[[Path], tuple[str, ...]],
               dataless_of: Callable[[Path], bool],
               approval_for: Callable[[str], ReviewApproval | None],
               constraints: FilesystemConstraints,
               suffix_for: Callable[[str, int], str],
               max_suffix_attempts: int,
               normalize_filename: Callable[[str], str],
               unverified_copy_disposition: str | None,
               scan_state: str,
               materialized: bool,
               component_version: str,
               user_id: str | None,
               now: Callable[[], str],
               mint_id: Callable[[], str]) -> ExecutionRecord:
    """One transaction for one plan. Returns its record; writes it and its events.

    The order is `00`:153-156's and is not rearrangeable: special objects, then
    §8.4's permission to move this file at all, then the precondition at V1,
    then the collision, then the precondition again at V2, then P13's approval,
    then the directories, then the move, then P1's observation, then V3, then
    the journal. Every stop before the move leaves the disk exactly as it was.

    **Where the approval gate sits is load-bearing.** Contract out §5:
    `review_policy_unsatisfied` is evaluated at the pre-apply recheck ONLY,
    because §8.3 requires the plan to be built so it can be shown. Putting it
    after V2 is also what makes SPEC rule 3 true by construction -- a plan that
    is also stale never reaches the approval question at all, so an approval
    cannot lift a staleness refusal even if someone wanted it to.

    `approval_for` is injected and returns `None` when nobody has answered. That
    `None` is the refusal: absence is never a default (SPEC, From P13).
    """
    started = now()
    source = Path(plan.expected_source_path)
    destination = Path(plan.resolved_destination_path)
    created: tuple[str, ...] = ()
    # Decided from the plan's own two volume fields, so it is known before
    # anything is touched: `74` §8 Q7's disposition is demanded up front, and a
    # cross-volume plan with no answer to it stops with the disk untouched
    # rather than part-way through a copy nobody can account for.
    mode = (ATOMIC_RENAME
            if plan.expected_source_volume == plan.expected_destination_volume
            else CROSS_VOLUME_COPY_AND_DELETE)
    if mode == CROSS_VOLUME_COPY_AND_DELETE and (
            unverified_copy_disposition is None):
        raise UnverifiedCopyDispositionRequired(
            "`74` §8 Q7 is open: this plan crosses volumes, so it may leave an "
            "unconfirmed copy, and P12 does not create one until the "
            "composition root has said what the person is told about it")

    def stopped(result: str, *, mode: str | None = None,
                v1: str | None = None, v2: str | None = None,
                v4: bool | None = None,
                final: str | None = None,
                detail: Mapping[str, object] = _NO_DETAIL,
                announce: bool = True) -> ExecutionRecord:
        """Record one stop, and tell the person about it.

        `announce` is False only where a `failed move` has already been
        appended: `66` §19 wants every movement action visible afterwards, and
        two rows for one stop would make the activity list say it happened
        twice.
        """
        record = ExecutionRecord(
            plan_id=plan.plan_id, mode=mode, hash_at_preparation=v1,
            hash_immediately_before_move=v2, hash_after_completion=None,
            destination_confirmed_pre_removal=v4, result=result,
            final_destination_path=final,
            directories_created_by_this_action=created, started_at=started,
            finished_at=now(), detail=detail)
        record_execution(conn, record, plan_version=plan.organization_plan_version,
                         record_id=mint_id())
        if announce:
            kind, _, tail = result.partition(":")
            record_refused_move(
                conn, outcome=(tail if kind == REFUSED else result),
                file_id=plan.file_id, content_hash=plan.expected_content_hash,
                source_path=plan.expected_source_path,
                destination_path=plan.resolved_destination_path,
                observed_at=record.finished_at,
                component_version=component_version, user_id=user_id,
                detail={"plan_id": plan.plan_id,
                        "plan_version": plan.organization_plan_version,
                        "result": result, **dict(detail)})
        return record

    objects = inspect_objects(
        source=source, destination_directory=destination.parent,
        source_root=source_root, destination_root=destination_root,
        extra_protected=extra_protected, conflict_copies=conflict_copies,
        dataless_of=dataless_of)
    if objects.refusal_class is not None:
        return stopped(result_of(REFUSED, objects.refusal_class),
                       detail=objects.detail)
    if objects.pause_reason is not None:
        return stopped(result_of(PAUSED, objects.pause_reason),
                       detail=objects.detail)

    # **The destination is inside the destination root.** Nothing checked this:
    # `destination_root` reached `inspect_objects` and was used there for
    # `if not root.exists()` and nothing else, so no code anywhere asserted that
    # `plan.resolved_destination_path` was under the root the run was pointed at.
    #
    # **Both sides are resolved, and that is the whole check.**
    # `Path.is_relative_to` is LEXICAL: it does not collapse `..`, so
    # `<root>/Documents/Coursework/../../../OUTSIDE/x` IS `is_relative_to(root)`
    # and the move lands outside anyway. Written the obvious way this check would
    # pass a traversal while looking like the property had been verified, which
    # is worse than not checking at all. `.resolve()` on both sides catches it.
    #
    # **Why here and not first.** Everything above only reads, and nothing in
    # this function writes to the disk until `_create_directories` far below, so
    # the boundary is established long before a `mkdir` could act on an escaping
    # path. It sits AFTER §8.1's object inspection because that step answers
    # whether the drive is even mounted, and a person whose external drive is
    # unplugged should be told to reconnect it rather than told their folder plan
    # is wrong. `00`:153-156's order keeps its first step.
    if not _inside(destination, destination_root):
        return stopped(result_of(REFUSED, NODE_REFUSES_PLACEMENT),
                       detail={"escaped": str(destination),
                               "destination_root": str(destination_root)})

    # §8.4, before anything is hashed: may this file be moved automatically at
    # all? P7 decides; P12 reports and picks no winner (`74` §5.3, §5.4).
    protection = protection_verdict(conn, plan)
    if not protection.satisfied:
        return stopped(result_of(REFUSED, protection.refusal_class),
                       detail=protection.detail)

    prepare = evaluate_preconditions(
        conn, plan, checkpoint=PREPARE,
        legal_destination_ids=legal_destination_ids, occupant_at_prepare=None,
        component_version=component_version, materialized=materialized, now=now)
    if not prepare.is_fresh:
        return stopped(result_of(STALE, prepare.trigger))

    final = destination
    incumbent = find_collision(destination.parent, destination.name,
                               constraints=constraints)
    if incumbent is not None:
        collision = resolve_collision(
            plan, incumbent=incumbent, incoming_path=source,
            incoming_hash=plan.expected_content_hash,
            behaviour=plan.collision_policy, constraints=constraints,
            suffix_for=suffix_for, max_suffix_attempts=max_suffix_attempts,
            materialized=materialized, mint_id=mint_id)
        record_collision(conn, collision, file_id=plan.file_id,
                         created_at=now(), component_version=component_version,
                         record_id=mint_id())
        if collision.final_destination_path is None:
            # Every behaviour that writes nothing means the same thing to the
            # person -- this collision needs your decision -- and WHICH of the
            # three it was is on the collision record, its one home.
            return stopped(result_of(PAUSED, AWAITING_COLLISION_DECISION),
                           v1=prepare.checkpoint_hash)
        final = Path(collision.final_destination_path)
        # The containment answer above was about `destination`. A collision
        # behaviour may only rename WITHIN the directory, so `final` inherits
        # it -- asserted rather than re-checked, because two containment checks
        # are two things that can disagree.
        assert final.parent == destination.parent, (
            "a collision behaviour changed the destination DIRECTORY; the "
            "containment check above no longer covers where this would land")

    pre_apply = evaluate_preconditions(
        conn, plan, checkpoint=PRE_APPLY,
        legal_destination_ids=legal_destination_ids,
        occupant_at_prepare=prepare.destination_occupant_hash,
        component_version=component_version, materialized=materialized, now=now)
    if not pre_apply.is_fresh:
        return stopped(result_of(STALE, pre_apply.trigger),
                       v1=prepare.checkpoint_hash)

    approval = approval_verdict(plan, approval_for(plan.plan_id))
    if not approval.satisfied:
        return stopped(result_of(REFUSED, approval.refusal_class),
                       v1=prepare.checkpoint_hash,
                       v2=pre_apply.checkpoint_hash, detail=approval.detail)

    created = _create_directories(final.parent)

    confirmed: bool | None = None
    if mode == ATOMIC_RENAME:
        try:
            _atomic_rename(source, final, constraints=constraints)
        except FileExistsError:
            # Something is at the destination that neither `find_collision` at
            # plan time nor `find_collision` a line ago could see -- because it
            # arrived in between, or because the declared table does not
            # describe this volume. §8.3 already has the name for that and the
            # disk is exactly as it was: the move did not happen.
            return stopped(result_of(STALE, DESTINATION_CHANGED), mode=mode,
                           v1=prepare.checkpoint_hash,
                           v2=pre_apply.checkpoint_hash,
                           detail={"trigger": DESTINATION_CHANGED,
                                   "target": str(final),
                                   "detected": "at the move, between the "
                                               "recheck and the move itself"})
    else:
        outcome = copy_and_confirm(
            conn, source=source, destination=final,
            expected_hash=plan.expected_content_hash, constraints=constraints,
            unverified_copy_disposition=unverified_copy_disposition,
            component_version=component_version, materialized=materialized)
        confirmed = outcome.destination_confirmed
        if not confirmed:
            # Nothing moved. The source is where it was, the copy P12 made is
            # where it landed, and NEITHER is removed -- §8.2 forbids the first
            # and §7.11 the second. Both paths and the composition root's
            # sentence about the copy go on the record and on the event, so the
            # state is reported rather than merely survived (`74` §8 Q7).
            stop = stopped(result_of(FAILED, V4_DESTINATION_UNCONFIRMED),
                           mode=mode, v1=prepare.checkpoint_hash,
                           v2=pre_apply.checkpoint_hash, v4=False,
                           final=outcome.unverified_copy_path, announce=False)
            record_failed_move(
                conn, failure_class=V4_DESTINATION_UNCONFIRMED,
                file_id=plan.file_id,
                content_hash=plan.expected_content_hash,
                source_path=str(source), destination_path=str(final),
                observed_at=stop.finished_at,
                component_version=component_version, user_id=user_id,
                detail={"plan_id": plan.plan_id, "mode": mode,
                        "source_path_retained": str(source),
                        "unverified_copy_path": outcome.unverified_copy_path,
                        "unverified_copy_disposition": outcome.disposition,
                        "directories_created_by_this_action": list(created)})
            return stop

    _observe_at(conn, plan, final, normalize_filename=normalize_filename,
                scan_state=scan_state, materialized=materialized,
                component_version=component_version)
    after = verify_content(
        conn, plan.file_id, plan.expected_content_hash,
        point=VerificationPoint.V3, author=SUBSYSTEM,
        component_version=component_version, materialized=materialized)

    applied = after == "match"
    finished = now()
    record = ExecutionRecord(
        plan_id=plan.plan_id, mode=mode,
        hash_at_preparation=prepare.checkpoint_hash,
        hash_immediately_before_move=pre_apply.checkpoint_hash,
        hash_after_completion=after, destination_confirmed_pre_removal=confirmed,
        result=(APPLIED if applied
                else result_of(FAILED, V3_HASH_MISMATCH)),
        final_destination_path=str(final),
        directories_created_by_this_action=created, started_at=started,
        finished_at=finished)
    record_execution(conn, record, plan_version=plan.organization_plan_version,
                     record_id=mint_id())

    # The journal entry is appended whichever way V3 answered, because the file
    # DID move: a mismatch means somebody changed it at the destination, not
    # that it is still at the source. Undo needs the entry either way, and
    # `post_move_verification_result` is where the mismatch is recorded (§8.3).
    entry = JournalEntry(
        entry_id=mint_id(), entry_kind=ENTRY_APPLIED, reverses_entry_id=None,
        plan_id=plan.plan_id, plan_version=plan.organization_plan_version,
        file_id=plan.file_id,
        hash_algorithm=get_file(conn, plan.file_id)["hash_algorithm"],
        original_source_path=str(source), destination_path=str(final),
        content_hash_at_movement=plan.expected_content_hash,
        collision_behaviour=plan.collision_policy,
        post_move_verification_result=after,
        source_volume=plan.expected_source_volume,
        destination_volume=plan.expected_destination_volume,
        execution_mode=mode, directories_created_by_this_action=created,
        intended_display_name=plan.intended_display_name,
        filesystem_safe_name=plan.filesystem_safe_name,
        time_of_execution=finished)
    record_journal_entry(conn, entry, record_id=mint_id())

    detail = {"plan_id": plan.plan_id, "mode": mode,
              "journal_entry_id": entry.entry_id,
              "plan_version": plan.organization_plan_version,
              "directories_created_by_this_action": list(created)}
    if applied:
        record_executed_move(
            conn, file_id=plan.file_id, content_hash=plan.expected_content_hash,
            source_path=str(source), destination_path=str(final),
            observed_at=finished, component_version=component_version,
            user_id=user_id, detail=detail)
    else:
        record_failed_move(
            conn, failure_class=V3_HASH_MISMATCH, file_id=plan.file_id,
            content_hash=plan.expected_content_hash, source_path=str(source),
            destination_path=str(final), observed_at=finished,
            component_version=component_version, user_id=user_id, detail=detail)
    return record


def apply_batch(conn: sqlite3.Connection, plans: Sequence[MovePlan], *,
                batch_bound: int | None,
                halts_run: Callable[[ExecutionRecord], bool] | None,
                **applying: object) -> tuple[ExecutionRecord, ...]:
    """§8.3's *"one action at a time or in a safely bounded batch"*.

    **`74` §8 Q6 is the owner's and is open.** §8.3 permits a bounded batch and
    bounds it nowhere; `00`:155 names only a sync conflict as pause-worthy. So
    `batch_bound` and `halts_run` are injected with NO default and no module
    constant stands in for either -- *"a number a person feels"* is not P12's to
    feel. Absent means refuse, and a batch larger than the stated bound is
    refused rather than silently truncated, because truncating would apply some
    of the person's moves and drop the rest without saying which.

    A batch is a bounded SEQUENCE of transactions, never one atomic unit: an
    all-or-nothing rollback would contradict undo being conditional and per-entry
    (SPEC §10). The one halt the design DOES settle is not injected -- a paused
    run stops, because *"pause when sync conflicts appear"* is `00`:174's own.
    """
    if batch_bound is None or halts_run is None:
        raise BatchPolicyRequired(
            "`74` §8 Q6 is open: the batch bound and the halt rule are the "
            "composition root's to state and P12 has no default for either")
    if (not isinstance(batch_bound, int) or isinstance(batch_bound, bool)
            or batch_bound <= 0):
        raise BatchPolicyRequired("the batch bound is a positive count of moves")
    ordered = tuple(plans)
    if len(ordered) > batch_bound:
        raise BatchPolicyRequired(
            f"{len(ordered)} moves were handed to a run bounded at "
            f"{batch_bound}; P12 refuses rather than applying some of them and "
            "dropping the rest")

    records: list[ExecutionRecord] = []
    for plan in ordered:
        record = apply_plan(conn, plan, **applying)  # type: ignore[arg-type]
        records.append(record)
        if record.result.startswith(f"{PAUSED}:") or halts_run(record):
            break
    return tuple(records)


def executions_for(conn: sqlite3.Connection,
                   plan_id: str) -> tuple[ExecutionRecord, ...]:
    rows = conn.execute(
        "SELECT payload FROM execution_records WHERE plan_id = ? "
        "ORDER BY record_id", (plan_id,)).fetchall()
    out: list[ExecutionRecord] = []
    for row in rows:
        raw = json.loads(row[0])
        raw["directories_created_by_this_action"] = tuple(
            raw["directories_created_by_this_action"])
        # A row written before `detail` existed has no key, and one written
        # after has a plain dict. Both become the same read-only mapping, so a
        # caller cannot tell which era a record came from and cannot mutate it.
        raw["detail"] = MappingProxyType(dict(raw.get("detail") or {}))
        out.append(ExecutionRecord(**raw))
    return tuple(out)

"""What P13 owes P2, and what it does not.

    P13 SPEC:400-407: P13 emits no `stage_output`. It is not one of §8.5's ten
    attribution stages, it decides nothing that could diverge, and inventing an
    eleventh stage would corrupt P2's closed `stage_id` enumeration.

So `stage_output` exists here and always raises -- the same pattern as
`states.one_message_for` and `locations.as_flat_paths`, placed exactly where
someone would reach for it.

What P13 DOES owe is that every surface is renderable from a replay bundle, so a
review screen can be reconstructed for a past run without the live database and
without a live filesystem, and that `presented_state_ref` serializes into and
re-asserts from a bundle.

**The ref is deterministic by construction**, so re-asserting a payload in a
replay database mints the same ref. That is why `reassert_presented_state` can
VERIFY rather than trust: a payload whose stated ref does not match a re-hash of
its own content is not the moment it claims to be. The alteration that matters
most is a changed redaction policy, which §8.4 makes consequential and which the
ref covers.

**`assert_reads_only` is a real tripwire, not a promise.** It installs SQLite's
own authorizer for the duration of one build and records every table read. A
surface that reaches outside the bundle -- for a live `files` row, for a scan that
is not in it -- is reported by name. The authorizer is removed in a `finally`, and
a test drives the tripwire against a builder that genuinely reads outside, because
a guard that cannot fire is the shape this project has been bitten by repeatedly.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Iterable, Mapping
from typing import NoReturn

from review_surface.presentation import PresentedState, presented_state


class NoStageOutputHere(RuntimeError):
    """Something asked P13 for a P2 stage output. P13 is not a stage."""


class NotRenderableFromABundle(RuntimeError):
    """A surface read outside the bundle, or a payload did not re-assert."""


def stage_output(*args: object, **kwargs: object) -> NoReturn:
    """Always raises. P13 is not one of §8.5's ten attribution stages."""
    raise NoStageOutputHere(
        "P13 emits no stage_output. It is not one of §8.5's ten attribution "
        "stages, it decides nothing that could diverge, and inventing an "
        "eleventh stage would corrupt P2's closed stage_id enumeration. What "
        "P13 owes P2 is that every surface is renderable from a replay bundle")


def serialize_presented_state(state: PresentedState) -> dict:
    """The bundle form. Plain JSON types only.

    `event_id` is a monotonic id LOCAL TO ONE DATABASE. It is carried so a bundle
    can point back at the original log, and it is deliberately not part of the
    ref: a replay database mints its own ids, and hashing one in would make the
    same moment un-round-trippable.
    """
    return {
        "presented_state_ref": state.presented_state_ref,
        "surface": state.surface,
        "subject_ref": state.subject_ref,
        "plan_version": state.plan_version,
        "session_id": state.session_id,
        "redaction_policy": dict(state.redaction_policy),
        "evidence_refs": list(state.evidence_refs),
        "user_id": state.user_id,
        "rendered_at": state.rendered_at,
        "event_id": state.event_id,
    }


def deserialize_presented_state(payload: Mapping[str, object]) -> PresentedState:
    """The record form, unchanged."""
    return PresentedState(
        presented_state_ref=str(payload["presented_state_ref"]),
        event_id=int(payload["event_id"]),  # type: ignore[arg-type]
        surface=str(payload["surface"]),
        subject_ref=str(payload["subject_ref"]),
        plan_version=str(payload["plan_version"]),
        session_id=str(payload["session_id"]),
        redaction_policy=dict(payload["redaction_policy"]),  # type: ignore[arg-type]
        evidence_refs=tuple(payload["evidence_refs"]),  # type: ignore[arg-type]
        user_id=payload.get("user_id"),  # type: ignore[arg-type]
        rendered_at=str(payload["rendered_at"]))


def reassert_presented_state(conn: sqlite3.Connection,
                             payload: Mapping[str, object]) -> PresentedState:
    """Re-assert a bundled presentation into a replay database, verifying its ref.

    The ref is re-derived from the payload's own content. A mismatch means the
    payload has been altered since it was minted -- most importantly a changed
    redaction policy, which is exactly the alteration §8.4 makes consequential.
    """
    from review_surface.presentation import _ref

    state = deserialize_presented_state(payload)
    expected = _ref(state.surface, state.subject_ref, state.plan_version,
                    state.session_id, state.redaction_policy,
                    state.evidence_refs, state.rendered_at)
    if expected != state.presented_state_ref:
        raise NotRenderableFromABundle(
            f"the bundled presentation claims ref {state.presented_state_ref!r} "
            f"but its own content hashes to {expected!r}. The ref covers the "
            "surface, subject, plan version, session, redaction policy, "
            "evidence references and time, so a mismatch means this is not the "
            "moment it says it is")
    existing = presented_state(conn, state.presented_state_ref)
    if existing is not None:
        return existing
    conn.execute(
        "INSERT INTO review_presentations "
        "(presented_state_ref, event_id, surface, subject_ref, plan_version, "
        " session_id, redaction_policy, evidence_refs, user_id, rendered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (state.presented_state_ref, state.event_id, state.surface,
         state.subject_ref, state.plan_version, state.session_id,
         json.dumps(dict(state.redaction_policy)),
         json.dumps(list(state.evidence_refs)), state.user_id,
         state.rendered_at))
    conn.commit()
    return state


def tables_read(conn: sqlite3.Connection,
                build: Callable[[], object]) -> tuple[object, tuple[str, ...]]:
    """Run `build` and report every table it read, using SQLite's own authorizer.

    Returned rather than judged, so the same mechanism serves both the bundle
    check below and any caller that simply wants to know. The authorizer is
    removed in a `finally`: leaving one installed would silently change how every
    later query on this connection behaves.
    """
    seen: set[str] = set()

    def _authorize(action, arg1, arg2, dbname, trigger):
        if action == sqlite3.SQLITE_READ and arg1:
            seen.add(arg1)
        return sqlite3.SQLITE_OK

    conn.set_authorizer(_authorize)
    try:
        result = build()
    finally:
        conn.set_authorizer(None)
    return result, tuple(sorted(seen))


def assert_reads_only(conn: sqlite3.Connection, bundle_tables: Iterable[str],
                      build: Callable[[], object]) -> object:
    """Run `build` and refuse if it read a table the bundle does not carry.

    §8.5's requirement is that a review screen can be reconstructed for a PAST
    run. A surface that reaches for a live row outside the bundle would render
    today's answer under a past run's heading -- which looks like a faithful
    reconstruction and is not one.
    """
    allowed = set(bundle_tables)
    result, read = tables_read(conn, build)
    outside = sorted(table for table in read if table not in allowed)
    if outside:
        raise NotRenderableFromABundle(
            f"this surface read {outside}, which the replay bundle does not "
            f"carry. §8.5 requires every surface to be reconstructable for a "
            "past run; a surface reaching outside the bundle renders today's "
            "answer under that run's heading, which looks faithful and is not")
    return result

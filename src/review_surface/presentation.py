"""What the user was ACTUALLY shown, under the redaction policy then in force.

P13 SPEC:509-512 is the reason this is a distinct event and not noise: §8.4 makes
what was displayed a privacy-relevant fact, and §8.7 requires a stored negative
example to carry the evidence that produced it. A rejection is only interpretable
against what the user saw -- a file rejected while its OCR text was redacted is a
different signal from one rejected with the evidence visible.

`assert_still_current` is the mechanism behind Done-means 14's second clause.
A `presented_state_ref` is a claim about a POLICY as well as about a subject, so a
ref minted while names were shown cannot be re-used to justify a display after the
user redacts them. The check compares the WHOLE policy, never the one facet a
caller happens to care about: a facet-by-facet check would pass a ref minted under
three loosened facets as long as the fourth matched.

The ref is a digest of everything that made the presentation what it was, so a
replayed bundle mints the SAME ref for the same moment and Done-means 23's
round-trip is an equality rather than a re-keying. The whole digest is kept: a
truncation would be a number this package has no authority to choose.

There is no `superseded_by` here and no update path. A presentation is a
historical fact about a moment; a later moment is a later row.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from database_agent.events import append_event
from privacy.display import DISPLAY_FACETS, RedactionSettings

from review_surface.vocabulary import (
    EVENT_PRESENTATION,
    SUBSYSTEM,
    SURFACES,
    check,
)

#: The one place the ref's prefix is spelled.
REF_PREFIX: str = "ps-"


class PresentationPolicyMismatch(RuntimeError):
    """A stored presentation was made under a policy no longer in force."""


@dataclass(frozen=True)
class PresentedState:
    """One recorded moment of display. It adds no judgement of any kind."""

    presented_state_ref: str
    event_id: int
    surface: str
    subject_ref: str
    plan_version: str
    session_id: str
    redaction_policy: Mapping[str, str]
    evidence_refs: tuple[str, ...]
    user_id: str | None
    rendered_at: str


def policy_of(settings: RedactionSettings) -> dict[str, str]:
    """P7's five facets as a plain mapping, in P7's own order.

    Read off `DISPLAY_FACETS` rather than off the dataclass's field order, so a
    facet P7 adds appears here the day P7 adds it instead of silently vanishing
    from every stored policy.
    """
    return {facet: getattr(settings, facet) for facet in DISPLAY_FACETS}


def _ref(surface: str, subject_ref: str, plan_version: str, session_id: str,
         policy: Mapping[str, str], evidence_refs: Sequence[str],
         rendered_at: str) -> str:
    """A deterministic ref over everything that makes this presentation what it was."""
    payload = json.dumps(
        [surface, subject_ref, plan_version, session_id, dict(policy),
         list(evidence_refs), rendered_at],
        sort_keys=True, separators=(",", ":"))
    return REF_PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record_presentation(conn: sqlite3.Connection, *, surface: str,
                        subject_ref: str, plan_version: str, session_id: str,
                        settings: RedactionSettings,
                        evidence_refs: Sequence[str], user_id: str | None,
                        component_version: str,
                        rendered_at: str) -> PresentedState:
    """Append the §8.2 event, store the row, return the state. Vocabulary first.

    `evidence_refs` are the `observation_key`s ACTUALLY shown, and an empty tuple
    is a real answer: a residual card, a progress line and a protected aggregate
    display no evidence, and refusing them would make the surfaces that show none
    the only unrecordable ones.
    """
    check(surface, SURFACES, name="surface")
    policy = policy_of(settings)
    refs = tuple(evidence_refs)
    ref = _ref(surface, subject_ref, plan_version, session_id, policy, refs,
               rendered_at)
    explanation = json.dumps(
        {"surface": surface, "subject_ref": subject_ref,
         "plan_version": plan_version, "session_id": session_id,
         "redaction_policy": policy, "evidence_refs": list(refs),
         "presented_state_ref": ref},
        sort_keys=True)
    event_id = append_event(
        conn, event_type=EVENT_PRESENTATION, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=rendered_at,
        user_id=user_id, explanation=explanation)
    conn.execute(
        "INSERT OR REPLACE INTO review_presentations "
        "(presented_state_ref, event_id, surface, subject_ref, plan_version, "
        " session_id, redaction_policy, evidence_refs, user_id, rendered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        # NOT `sort_keys`: the stored policy keeps P7's facet ORDER, so a
        # reader sees the facets in the order P7 publishes them rather than in
        # alphabetical order, which is a different and meaningless one.
        (ref, event_id, surface, subject_ref, plan_version, session_id,
         json.dumps(policy), json.dumps(list(refs)), user_id,
         rendered_at))
    conn.commit()
    return PresentedState(
        presented_state_ref=ref, event_id=event_id, surface=surface,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, redaction_policy=policy, evidence_refs=refs,
        user_id=user_id, rendered_at=rendered_at)


def presented_state(conn: sqlite3.Connection,
                    presented_state_ref: str) -> PresentedState | None:
    """The recorded moment, or None. A read, never a mint."""
    row = conn.execute(
        "SELECT * FROM review_presentations WHERE presented_state_ref = ?",
        (presented_state_ref,)).fetchone()
    if row is None:
        return None
    return PresentedState(
        presented_state_ref=row["presented_state_ref"],
        event_id=row["event_id"], surface=row["surface"],
        subject_ref=row["subject_ref"], plan_version=row["plan_version"],
        session_id=row["session_id"],
        redaction_policy=json.loads(row["redaction_policy"]),
        evidence_refs=tuple(json.loads(row["evidence_refs"])),
        user_id=row["user_id"], rendered_at=row["rendered_at"])


def assert_still_current(conn: sqlite3.Connection, presented_state_ref: str, *,
                         settings: RedactionSettings) -> PresentedState:
    """Done-means 14, second clause: a cached rendering does not survive a change.

    An unknown ref is a mismatch and not a pass. A caller holding a ref this
    database has never seen is holding a claim about a display nobody recorded,
    which is exactly the state the check exists to refuse.
    """
    state = presented_state(conn, presented_state_ref)
    if state is None:
        raise PresentationPolicyMismatch(
            f"{presented_state_ref!r} names no recorded presentation, so there "
            "is nothing to say what the user was shown or under what policy")
    wanted = policy_of(settings)
    if dict(state.redaction_policy) != wanted:
        changed = [facet for facet in DISPLAY_FACETS
                   if state.redaction_policy.get(facet) != wanted[facet]]
        raise PresentationPolicyMismatch(
            f"{presented_state_ref!r} was rendered under a policy that differs "
            f"on {changed}; a rendering cached before a policy change must not "
            "survive it (§8.4)")
    return state

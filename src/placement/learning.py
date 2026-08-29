"""§8.7's negative examples, asked before every proposal.

A rejected destination is stored WITH the evidence that produced it so the same
attractive-but-wrong node is not resurfaced. P11 keeps no second learning store:
P1 owns `events` and its §8.7 columns, and `learning_records` already honours a
reset as a cutoff without deleting anything (R6).

Scope is the whole safety property. §8.7's governing example is that a user
saying ONE transcript belongs in a Columbia packet must not teach the engine that
ALL transcripts do, so a suppression applies at the scope the user chose and
nowhere else. P11 widens no scope and infers none.

**A scope P11 cannot address refuses instead of returning nothing.** Four of §8.7's
six scopes name a subject P11 can derive -- the file, the group, and each candidate
node -- and `corpus` names one only the caller knows. `template` and `domain` name
neither, and answering `()` for them would report "the user rejected nothing" for a
question that was never asked. That is the difference between a suppression that is
absent and one that was never looked for, and only one of them is safe to
auto-place on.

`basis_key` pairs the SCOPE'S SUBJECT with the node, which is the pair SPEC:753-755
names: *"`placement` / `(subject_id, node_id)`"*. It deliberately does not carry the
content hash. §8.7 is about what the user decided, and editing a file does not
un-decide it -- a versioned key would silently stop matching on the next save and
resurface exactly the destination the user rejected.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from database_agent.events import CORRECTION_SCOPES
from database_agent.learning import learning_records

from placement import events as placement_events
from placement.vocabulary import (
    FILE, GROUP, PLACEMENT, POLARITIES, POLARITY_ACCEPT, POLARITY_REJECT,
    RESIDUAL,
)

#: The two `proposal_class` values P11 writes and reads. A rejection recorded by
#: another part under another class is that part's fact, not a placement fact.
PROPOSAL_CLASSES: tuple[str, ...] = (PLACEMENT, RESIDUAL)

#: §8.2's two polarities. Bound from `placement.vocabulary`, which is their one
#: home: `reject` is also P8's verdict outcome, and a literal here would be this
#: module choosing a spelling on an axis it does not own.
REJECT: str = POLARITY_REJECT
ACCEPT: str = POLARITY_ACCEPT

#: The scope naming the whole corpus. Its subject is the caller's to name, because
#: what a corpus is called is a deployment fact and not a P11 one.
CORPUS: str = "corpus"

#: The scope keyed on the destination node itself, rather than on the subject the
#: decision is about.
NODE: str = "node"

assert {FILE, GROUP, NODE, CORPUS} <= set(CORRECTION_SCOPES)


class ScopeSubjectRequired(ValueError):
    """A scope was asked about that P11 has no subject to query it with."""


@dataclass(frozen=True)
class Suppression:
    node_id: str
    scope: str
    subject_id: str
    basis_key: str
    event_id: int


def basis_key_for(*, subject_id: str, node_id: str) -> str:
    """The evidence pattern one rejection was about: SPEC:753-755's pair."""
    return f"{subject_id}->{node_id}"


def _subject_ids(scope: str, *, subject_ref: str, node_ids: Sequence[str],
                 corpus_subject_id: str | None) -> tuple[str, ...]:
    """Which `correction_subject` this scope is keyed on for this query.

    `file` and `group` come from the subject ref, whose kind prefix says which one
    the decision is about; a file-scoped question about a group subject has no
    subject and refuses rather than reading the group id as a file id.
    """
    kind, _, remainder = subject_ref.partition(":")
    if scope == FILE:
        if kind != FILE:
            raise ScopeSubjectRequired(
                f"the `file` scope was asked about {subject_ref!r}, which is a "
                f"{kind!r} subject; reading its id as a file id would query one "
                "user's decision under another's name"
            )
        return (remainder.partition(":")[0],)
    if scope == GROUP:
        if kind != GROUP:
            raise ScopeSubjectRequired(
                f"the `group` scope was asked about {subject_ref!r}, which names "
                "no group"
            )
        return (remainder,)
    if scope == NODE:
        # The subject IS each candidate. A node-scoped rejection is about the
        # destination, so it applies whatever file is being placed.
        return tuple(node_ids)
    if scope == CORPUS:
        if not corpus_subject_id:
            raise ScopeSubjectRequired(
                "the `corpus` scope names a subject only the caller knows; "
                "querying it without one would look nothing up and report that "
                "the user had rejected nothing"
            )
        return (corpus_subject_id,)
    raise ScopeSubjectRequired(
        f"P11 has no subject for the {scope!r} scope: which template or domain a "
        "user meant is theirs to name, and answering () here would be a "
        "suppression that was never looked for reported as one that is absent"
    )


def suppressed_nodes(conn: sqlite3.Connection, *, subject_ref: str,
                     node_ids: Iterable[str], scopes: Iterable[str],
                     corpus_subject_id: str | None = None,
                     proposal_class: str = PLACEMENT) -> tuple[Suppression, ...]:
    """Which of these nodes the user has already rejected, at these scopes.

    Called before `outcome = place` is emitted. A hit means the node is skipped
    -- never auto-placed and never silently re-ranked, because a silent re-rank
    would hide from the user that their own correction was the reason.
    """
    candidates = tuple(node_ids)
    order = {node_id: rank for rank, node_id in enumerate(candidates)}
    found: dict[str, Suppression] = {}
    for scope in scopes:
        if scope not in CORRECTION_SCOPES:
            raise ValueError(
                f"{scope!r} is not one of §8.7's six scopes {CORRECTION_SCOPES}"
            )
        for subject_id in _subject_ids(scope, subject_ref=subject_ref,
                                       node_ids=candidates,
                                       corpus_subject_id=corpus_subject_id):
            wanted = {
                basis_key_for(subject_id=subject_id, node_id=node_id): node_id
                for node_id in candidates
            }
            for row in learning_records(conn, scope, subject_id):
                if row["polarity"] != REJECT:
                    continue
                if row["proposal_class"] != proposal_class:
                    continue
                node_id = wanted.get(row["basis_key"])
                if node_id is None:
                    continue
                # One node suppressed at two scopes is one suppression for the
                # caller; the first scope asked about is the one reported.
                found.setdefault(node_id, Suppression(
                    node_id=node_id, scope=scope, subject_id=subject_id,
                    basis_key=row["basis_key"], event_id=row["event_id"],
                ))
    return tuple(found[node_id] for node_id in sorted(found, key=order.__getitem__))


def record_correction(conn: sqlite3.Connection, *, decision, action: str,
                      polarity: str, scope: str, subject_id: str,
                      basis_key: str, user_id: str, component_version: str,
                      observed_at: str, explanation: str,
                      proposal_class: str = PLACEMENT) -> int:
    """Store one user action with its scope, its polarity and its basis.

    §8.7's list of what is recorded runs to thirteen actions; `action` carries
    the one the user took and P13's `review_action.action` is its vocabulary.
    P11 stores it rather than interpreting it, and derives no preference here:
    a preference is what the suppression read above computes from the stored
    facts, so there is no second, silently-trained copy.
    """
    if polarity not in POLARITIES:
        raise ValueError(f"polarity is {ACCEPT!r} or {REJECT!r}, not {polarity!r}")
    if proposal_class not in PROPOSAL_CLASSES:
        raise ValueError(f"{proposal_class!r} is not one of {PROPOSAL_CLASSES}")
    if scope not in CORRECTION_SCOPES:
        raise ValueError(f"{scope!r} is not one of {CORRECTION_SCOPES}")
    from placement.store import subject_ref_of

    return placement_events.review_decision(
        conn, subject_ref=subject_ref_of(decision.subject), action=action,
        component_version=component_version, observed_at=observed_at,
        user_id=user_id, correction_scope=scope, correction_subject=subject_id,
        polarity=polarity, proposal_class=proposal_class, basis_key=basis_key,
        explanation=explanation, file_id=decision.subject.file_id,
        content_hash=decision.subject.content_hash,
    )

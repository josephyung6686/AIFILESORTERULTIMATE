# src/facts/session.py
"""G6 — §3.9's tightly bounded download session, pinned at `possible` (§4.2).

§3.9, and every clause binds:

    "It may be supported more weakly by a tightly bounded download session. A session
     should never be treated as proof of topic, and it should not carry the same
     confidence as a hash match or a directly extracted document fact. It is a
     purpose clue and a review aid, not a basis for automatic semantic propagation."

§4.7 is the other half of the ceiling: "A tight download session alone is never
sufficient: it is a retrieval clue that may bring the files together, but not proof of
their shared purpose."

So:

- the ceiling is a FUNCTION, not a call site. `require_possible` is the only gate to
  a `download_session` write and it raises on anything else, so no rule can promote
  the field and no §3.7 margin can reach it;
- being `possible` is what keeps it out of §3.6's proposal-eligible read. There is no
  second mechanism, and nothing to remember to switch off;
- the fact is written for the member file and copies nothing. §4.1: the graph "does
  not automatically copy those missing facts onto sparse files".

**What is citable and what is not.** §3.9's two inputs are the timestamps and the
parent-folder context. P5 emits the parent-folder context as an ordinary observation
at `zone = "path"`; it deliberately emits NO timestamp observation, because G6 hands
the session to P6 "computed from P3 timestamps" and a second copy would be two homes
for one value. The mtime is therefore read from P1's `files` row and is not citable,
and a member with no `path` observation has nothing to cite at all: it abstains
rather than asserting a clue nobody can inspect.

**The session's name is a digest.** A name built from the parent folder would put a
path fragment inside a value, which is §3.14's mistake one layer down. The canonical
value is `sha256_of(canonical_json(sorted(member file ids)))`: deterministic,
inspectable, and carrying nothing about where the files sat. Adding a member renames
the session, which is acceptable for a clue that may never exceed `possible` and is
stated here rather than hidden.

**Silence is not a refusal.** A file whose two inputs exist but which lands in no
session gets no fact and no `unresolved` row: the abstention record names "the field
that was attempted", and a window that simply contained one file was never a
proposal.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Mapping

from database_agent.files_table import get_file

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS, ZONES, check

from facts.cache import fact_cache_key
from facts.evidence import analysis_tier_for_observation, cite, observations_for_version
from facts.file_facts import DETERMINISTIC_EXTRACTOR, write_fact
from facts.unresolved import DIRECT_ROUTE, NO_CANDIDATE_EVIDENCE, write_unresolved
from facts.values import VALUE_ORIGINS, ensure_value

#: The one universal field this part adds beyond §3.11's six, because §3.9 requires a
#: representation and §4.2 requires it to be retrievable. It is not `purpose`: the
#: session names no purpose value. The catalogue row is Task 2's, and it carries
#: `destination_eligible = FALSE` -- a folder level built from a download window
#: would put the window into the tree.
DOWNLOAD_SESSION_FIELD: str = "download_session"

#: §3.13's own example of a `possible` fact is "membership in a short download
#: session". The ceiling and the floor are the same value. Task 1 owns the spelling;
#: this is never an index into `STATES`.
SESSION_STATE: str = "possible"

#: P4's zone for §2.9's parent-folder context, as P5 writes it. Validated against
#: P4's published vocabulary at import -- the same guard `facts.discount` puts on
#: `metadata` -- so a rename upstream is a load error rather than a clue that
#: silently stops being citable. Read from the zone, never from an extractor name:
#: no P6 module branches on `source_type` or `extractor_name`.
PARENT_FOLDER_ZONE: str = check("path", ZONES, name="zone")


class SessionNeverPromoted(ValueError):
    """§3.9's ceiling, raised rather than documented."""


@dataclass(frozen=True)
class SessionBoundary:
    """What makes a session "tightly bounded". Injected; the design states none.

    Every field is required. §3.9 asks for the clue and gives no window, no folder
    rule and no minimum, so a default here would be P6 answering a deferred question
    inside an implementation.
    """

    window_seconds: float
    require_same_parent_folder_context: bool
    minimum_members: int


def require_possible(reliability_state: str) -> str:
    """The only gate to a `download_session` write.

    §3.9: a session "should not carry the same confidence as a hash match or a
    directly extracted document fact". That is a statement about every route, so it
    is enforced where every route has to pass rather than at the one call this module
    makes -- a test can attempt the promotion and require the raise, which inspecting
    a call site cannot give.
    """
    if reliability_state != SESSION_STATE:
        raise SessionNeverPromoted(
            f"§3.9 pins a download-session clue at {SESSION_STATE!r}; "
            f"{reliability_state!r} would give a retrieval clue the confidence of a "
            "hash match or a directly extracted document fact"
        )
    return reliability_state


@dataclass(frozen=True)
class _Member:
    file_id: str
    content_hash: str
    mtime: float
    parent_folder_context: str
    observations: tuple[Observation, ...]

    @property
    def citable(self) -> tuple[Observation, ...]:
        return tuple(one for one in self.observations
                     if one.zone == PARENT_FOLDER_ZONE)


def _members(conn: sqlite3.Connection,
             file_ids: Iterable[str]) -> tuple[_Member, ...]:
    """Every file that carries §3.9's two inputs, ordered by time then by file id.

    The secondary key is not decoration: two files written in the same second must
    fall in one order for one corpus regardless of the order P4 stored them in.
    """
    members: list[_Member] = []
    for file_id in sorted(set(file_ids)):
        row = dict(get_file(conn, file_id))
        parent = row["directory_position"]
        stamps = json.loads(row["observed_timestamps"] or "{}")
        mtime = stamps.get("mtime")
        if parent is None or mtime is None:
            continue          # §3.9's inputs are absent; nothing was proposed
        content_hash = row["content_hash"]
        members.append(_Member(
            file_id=file_id, content_hash=content_hash, mtime=float(mtime),
            parent_folder_context=parent,
            observations=tuple(observations_for_version(conn, file_id,
                                                        content_hash))))
    return tuple(sorted(members, key=lambda m: (m.mtime, m.file_id)))


def _joins(previous: _Member, candidate: _Member,
           boundary: SessionBoundary) -> bool:
    if candidate.mtime - previous.mtime > boundary.window_seconds:
        return False
    if (boundary.require_same_parent_folder_context
            and previous.parent_folder_context
            != candidate.parent_folder_context):
        return False
    return True


def _windows(members: tuple[_Member, ...],
             boundary: SessionBoundary) -> list[list[_Member]]:
    """Consecutive members inside the injected window, as one chain each."""
    runs: list[list[_Member]] = []
    for member in members:
        if runs and _joins(runs[-1][-1], member, boundary):
            runs[-1].append(member)
        else:
            runs.append([member])
    return [run for run in runs if len(run) >= boundary.minimum_members]


def _pass_cache_key(conn: sqlite3.Connection, member: _Member) -> str:
    """§3.4's key for one deterministic pass over one file version.

    Preamble §3.2, and it is deliberately NOT "the observations the fact cites":
    `extractor_version` is the canonical JSON of the sorted distinct
    `(name, version)` pairs of EVERY observation of that file version, and the key is
    computed per (file version, deterministic pass). The deciding argument is the
    abstention -- the SPEC gives an `unresolved` row the "same composition as
    `file_facts` (§3.4)", and an abstention with no citations has no cited
    observations to compute a key from. One key per pass answers both, so the fact
    this module writes and the refusal it writes instead share one slot.

    The tier is the LAST one present in `ANALYSIS_TIERS` order -- filesystem <
    native < ocr < llm -- so a later, richer pass supersedes rather than overwrites.
    A member with no observation at all still gets a key: this module's abstention
    fires exactly there, so the earliest tier in the ordering stands in rather than
    the pass being unrecordable.
    """
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in member.observations})
    tiers = {analysis_tier_for_observation(conn, one)
             for one in member.observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    return fact_cache_key(
        content_hash=member.content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1] if present else ANALYSIS_TIERS[0],
        model_identifier=None, prompt_fingerprint=None)


def bounded_sessions(conn: sqlite3.Connection, *, file_ids: Iterable[str],
                     boundary: SessionBoundary) -> Mapping[str, str]:
    """Done-means 25. `file_id -> fact_id` for every member of a bounded session.

    A file whose two §3.9 inputs exist but which lands in no session gets no fact and
    no `unresolved` row: the abstention record names "the field that was attempted",
    and a window that contained one file was never a proposal. A file that IS in a
    session but has nothing to cite abstains, because a clue nobody can inspect is
    not a clue.
    """
    written: dict[str, str] = {}
    for window in _windows(_members(conn, file_ids), boundary):
        citable = {member.file_id: member.citable for member in window}
        if not all(citable.values()):
            for member in window:
                write_unresolved(
                    conn, file_id=member.file_id,
                    content_hash=member.content_hash,
                    field_key=DOWNLOAD_SESSION_FIELD,
                    reason=NO_CANDIDATE_EVIDENCE,
                    attempted_producers=(DIRECT_ROUTE,),
                    evidence_refs=(),
                    cache_key=_pass_cache_key(conn, member))
            continue
        canonical_value = sha256_of(canonical_json(
            sorted(member.file_id for member in window)))
        for member in window:
            refs = tuple(sorted(cite(one) for one in citable[member.file_id]))
            value_id = ensure_value(
                conn, field_key=DOWNLOAD_SESSION_FIELD,
                canonical_value=canonical_value, first_evidence_ref=refs[0],
                origin=VALUE_ORIGINS[0])
            written[member.file_id] = write_fact(
                conn, file_id=member.file_id, content_hash=member.content_hash,
                field_key=DOWNLOAD_SESSION_FIELD, value_id=value_id,
                reliability_state=require_possible(SESSION_STATE),
                origin=DETERMINISTIC_EXTRACTOR, evidence_refs=refs,
                cache_key=_pass_cache_key(conn, member),
                active=True)
    return written

"""Thin connector: propose inferred / name-witnessed life links.

Never writes ``state = approved``. Never imports mutation. Semantic
``group_edges`` are not projected here (see ``relationships.py``).

Rules (item plan §10):

- ``member-of`` when a typed academic file's label contains a declared course
  name (casefold). Confidence ``witnessed`` when the course token is in the
  filename; otherwise ``inferred`` only if at least two declared lives exist.
- ``about`` when a file label contains a declared project name and two
  declared lives exist (inferred).
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from items.decisions import basis_is_rejected
from items.schema import create_items_schema
from questions.store import declared_lives, named_courses, named_projects

CONFIDENCE_INFERRED = "inferred"
CONFIDENCE_WITNESSED = "witnessed"
STATE_PROPOSED = "proposed"
SOURCE_CONNECTOR = "connector"
REL_MEMBER = "member-of"
REL_ABOUT = "about"


def propose_inferred_links(conn: sqlite3.Connection) -> int:
    """Insert proposed links. Returns how many new rows were written."""
    if not _items_installed(conn):
        return 0
    create_items_schema(conn)
    lives = declared_lives(conn)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    written = 0
    written += _member_of_courses(conn, lives=lives, now=now)
    written += _about_projects(conn, lives=lives, now=now)
    return written


def _member_of_courses(conn, *, lives: frozenset[str], now: str) -> int:
    courses = list(named_courses(conn))
    if not courses:
        return 0
    files = conn.execute(
        "SELECT item_id, display_label, open_target, type_schema, typing_state "
        "FROM items WHERE item_type = 'file' AND presence = 'live' "
        "AND superseded_by IS NULL AND typing_state = 'typed' "
        "AND type_schema = 'academic'"
    ).fetchall()
    hubs = {
        row["display_label"]: row["item_id"]
        for row in conn.execute(
            "SELECT item_id, display_label FROM items "
            "WHERE item_type = 'course' AND presence = 'live' "
            "AND superseded_by IS NULL")
    }
    written = 0
    for course in courses:
        hub = hubs.get(course)
        if hub is None:
            continue
        token = course.casefold()
        for file_row in files:
            hay = f"{file_row['display_label']} {file_row['open_target'] or ''}".casefold()
            if token not in hay:
                continue
            # Name match is witnessed. Broader inference needs two lives.
            if token in (file_row["display_label"] or "").casefold():
                confidence = CONFIDENCE_WITNESSED
            elif len(lives) >= 2:
                confidence = CONFIDENCE_INFERRED
            else:
                continue
            if _insert(
                    conn, rel_type=REL_MEMBER,
                    left=file_row["item_id"], right=hub,
                    confidence=confidence,
                    evidence_refs=[f"course_name:{course}",
                                   f"file:{file_row['item_id']}"],
                    now=now):
                written += 1
    return written


def _about_projects(conn, *, lives: frozenset[str], now: str) -> int:
    if len(lives) < 2:
        return 0
    projects = list(named_projects(conn))
    if not projects:
        return 0
    hubs = {
        row["display_label"]: row["item_id"]
        for row in conn.execute(
            "SELECT item_id, display_label FROM items "
            "WHERE item_type = 'project' AND presence = 'live' "
            "AND superseded_by IS NULL")
    }
    candidates = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_type = 'file' AND presence = 'live' "
        "AND superseded_by IS NULL"
    ).fetchall()
    written = 0
    for project in projects:
        hub = hubs.get(project)
        if hub is None:
            continue
        token = project.casefold()
        for row in candidates:
            if token not in (row["display_label"] or "").casefold():
                continue
            if row["item_id"] == hub:
                continue
            if _insert(
                    conn, rel_type=REL_ABOUT,
                    left=row["item_id"], right=hub,
                    confidence=CONFIDENCE_INFERRED,
                    evidence_refs=[f"project_name:{project}",
                                   f"item:{row['item_id']}"],
                    now=now):
                written += 1
    return written


def _insert(conn, *, rel_type: str, left: str, right: str, confidence: str,
            evidence_refs: list[str], now: str) -> bool:
    fingerprint = sorted(evidence_refs)
    if not fingerprint or any(not ref for ref in fingerprint):
        raise ValueError("connector refuses empty evidence")
    basis = json.dumps(
        {"rel_type": rel_type, "from": left, "to": right,
         "evidence": fingerprint},
        sort_keys=True,
    )
    if basis_is_rejected(conn, basis):
        return False
    existing = conn.execute(
        "SELECT relationship_id FROM relationships WHERE basis_key = ? "
        "AND superseded_by IS NULL",
        (basis,),
    ).fetchone()
    if existing is not None:
        return False
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)",
        (
            str(uuid.uuid4()), rel_type, left, right, confidence,
            SOURCE_CONNECTOR, STATE_PROPOSED,
            json.dumps(fingerprint, sort_keys=True), basis, now,
        ),
    )
    return True


def _items_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
    ).fetchone() is not None

"""Read-only mail and calendar headers, stored as local items.

The live Gmail and Calendar APIs are not connected. A `MailboxSource` is the
interface a later macOS or provider connector would implement. This module's
only source is a JSON fixture on disk. It does not open a socket.

Stored: ids, addresses, subject or title, attachment filenames and hashes,
event start, end, calendar id, and status. Not stored: message bodies,
calendar descriptions, attachment bytes, and OAuth tokens. Tokens are not a
column. A fixture that carries them is ingested without writing them.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from items.schema import create_items_schema

ITEM_EMAIL = "email"

#: Path parts that are private even when nobody typed them. A name-only walk
#: can see these without opening the file. Kept here so mailbox does not
#: depend on the understanding package (which is not on every branch).
_PROTECTED_PARTS: frozenset[str] = frozenset({
    ".ssh", ".gnupg", "keychains", "cookies", "passwords",
})
_PROTECTED_EXTENSIONS: frozenset[str] = frozenset({
    ".pem", ".key", ".p12", ".kdbx", ".keystore",
})


def path_is_protected(path: str) -> bool:
    parts = {part.casefold() for part in path.replace("\\", "/").split("/")}
    if parts & _PROTECTED_PARTS:
        return True
    lower = path.casefold()
    return any(lower.endswith(ext) for ext in _PROTECTED_EXTENSIONS)


ITEM_EVENT = "event"
PRESENCE_LIVE = "live"
HELD = "held"
UNPLACED = "unplaced"

_DROPPED = frozenset({
    "body", "description", "raw", "rfc822", "token", "tokens",
    "access_token", "refresh_token", "oauth", "authorization",
})

STORED_EMAIL_FIELDS = (
    "message_id", "thread_id", "internal_date", "from", "to", "subject",
    "attachment_filename", "attachment_hash",
)
STORED_EVENT_FIELDS = (
    "event_id", "calendar_id", "start", "end", "title", "status",
)
NOT_STORED = ("body", "description", "token", "attachment bytes")


class MailboxRefused(ValueError):
    """The fixture is not a header export. Nothing was stored."""


def load_fixture(path: Path) -> dict:
    """JSON from disk. A missing file is a refusal, not a network fetch."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as problem:
        raise MailboxRefused(
            "the fixture could not be read as JSON. Nothing was stored.") from problem
    if not isinstance(data, dict):
        raise MailboxRefused("the fixture must be a JSON object. Nothing was stored.")
    return data


def dry_run_plan(data: dict, *, kind: str) -> dict:
    """What a sync would store. Does not open a database."""
    if kind == "gmail":
        rows = _messages(data)
        fields = STORED_EMAIL_FIELDS
    elif kind == "calendar":
        rows = _events(data)
        fields = STORED_EVENT_FIELDS
    else:
        raise MailboxRefused(f"{kind!r} is not gmail or calendar.")
    return {
        "kind": kind,
        "count": len(rows),
        "fields": list(fields),
        "not_stored": list(NOT_STORED),
        "sent": False,
        "stored": False,
    }


def ingest_fixture(conn: sqlite3.Connection, data: dict, *, kind: str,
                   recorded_at: str | None = None) -> dict:
    """Write header items. Returns counts. Does not approve a link."""
    create_items_schema(conn)
    now = recorded_at or datetime.now(timezone.utc).isoformat()
    if kind == "gmail":
        written = [_upsert_email(conn, message, now) for message in _messages(data)]
    elif kind == "calendar":
        written = [_upsert_event(conn, event, now) for event in _events(data)]
    else:
        raise MailboxRefused(f"{kind!r} is not gmail or calendar.")
    held = sum(1 for item in written if item["typing_state"] == HELD)
    unplaced = sum(1 for item in written if item["typing_state"] == UNPLACED)
    return {
        "kind": kind,
        "stored": len(written),
        "held": held,
        "unplaced": unplaced,
        "approved": 0,
    }


def model_fields(conn: sqlite3.Connection, item_id: str) -> dict:
    """Fields a cloud call may see. A held item contributes nothing.

    Bodies are not in the database, so they cannot be returned from here.
    """
    create_items_schema(conn)
    row = conn.execute(
        "SELECT item_id, item_type, display_label, typing_state FROM items "
        "WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None or row["typing_state"] == HELD:
        return {}
    return {
        "item_id": row["item_id"],
        "item_type": row["item_type"],
        "label": row["display_label"],
    }


def _messages(data: dict) -> list[dict]:
    rows = data.get("messages") or []
    if not isinstance(rows, list):
        raise MailboxRefused("messages must be a list. Nothing was stored.")
    return [row for row in rows if isinstance(row, dict)]


def _events(data: dict) -> list[dict]:
    rows = data.get("events") or []
    if not isinstance(rows, list):
        raise MailboxRefused("events must be a list. Nothing was stored.")
    return [row for row in rows if isinstance(row, dict)]


def _text(row: dict, key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        return ""
    return value.strip()


def _upsert_email(conn, message: dict, now: str) -> dict:
    message_id = _text(message, "message_id")
    if not message_id:
        raise MailboxRefused("a message needs a message_id. Nothing else was stored.")
    account = _text(message, "account_label") or _text(message, "account") or "local"
    subject = _text(message, "subject") or "(no subject)"
    names, hashes = _attachments(message)
    matches = _files_for_hashes(conn, hashes)
    held = any(path_is_protected(match["current_path"]) for match in matches)
    file_id = matches[0]["file_id"] if matches else None
    typing = HELD if held else UNPLACED
    external = f"gmail:{account}:{message_id}"
    item_id = _upsert_item(
        conn, item_type=ITEM_EMAIL, label=subject, file_id=file_id,
        external_key=external, typing_state=typing, now=now)
    addresses = message.get("to") or []
    if isinstance(addresses, str):
        to_text = addresses
    elif isinstance(addresses, list):
        to_text = ", ".join(
            part.strip() for part in addresses if isinstance(part, str) and part.strip())
    else:
        to_text = ""
    _write_header(
        conn, item_id, kind="email", external_id=message_id,
        thread_id=_text(message, "thread_id"), account_label=account,
        happened_at=_text(message, "internal_date"), ended_at="",
        address_from=_text(message, "from"), address_to=to_text,
        calendar_id="", status="",
        attachment_names=json.dumps(names),
        attachment_hashes=json.dumps(hashes))
    for match in matches:
        _propose_attachment(conn, item_id, match, now)
    return {"item_id": item_id, "typing_state": typing}


def _upsert_event(conn, event: dict, now: str) -> dict:
    event_id = _text(event, "event_id")
    if not event_id:
        raise MailboxRefused("an event needs an event_id. Nothing else was stored.")
    account = _text(event, "account_label") or "local"
    title = _text(event, "title") or "(no title)"
    external = f"calendar:{account}:{event_id}"
    item_id = _upsert_item(
        conn, item_type=ITEM_EVENT, label=title, file_id=None,
        external_key=external, typing_state=UNPLACED, now=now)
    _write_header(
        conn, item_id, kind="event", external_id=event_id,
        thread_id="", account_label=account,
        happened_at=_text(event, "start"), ended_at=_text(event, "end"),
        address_from="", address_to="",
        calendar_id=_text(event, "calendar_id"), status=_text(event, "status"),
        attachment_names="[]", attachment_hashes="[]")
    return {"item_id": item_id, "typing_state": UNPLACED}


def _attachments(message: dict) -> tuple[list[str], list[str]]:
    raw = message.get("attachments") or []
    names: list[str] = []
    hashes: list[str] = []
    if not isinstance(raw, list):
        return names, hashes
    for part in raw:
        if not isinstance(part, dict):
            continue
        name = part.get("filename")
        digest = part.get("sha256") or part.get("hash")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
        if isinstance(digest, str) and digest.strip():
            hashes.append(digest.strip().lower())
    return names, hashes


def _files_for_hashes(conn, hashes: list[str]) -> list[sqlite3.Row]:
    found = []
    seen: set[str] = set()
    for digest in hashes:
        try:
            rows = conn.execute(
                "SELECT file_id, current_path, content_hash FROM files "
                "WHERE content_hash = ?",
                (digest,),
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        for row in rows:
            if row["file_id"] not in seen:
                seen.add(row["file_id"])
                found.append(row)
    return found


def _upsert_item(conn, *, item_type: str, label: str, file_id: str | None,
                 external_key: str, typing_state: str, now: str) -> str:
    existing = conn.execute(
        "SELECT item_id FROM items WHERE external_key = ? AND item_type = ?",
        (external_key, item_type),
    ).fetchone()
    if existing is not None:
        conn.execute(
            "UPDATE items SET display_label = ?, file_id = ?, typing_state = ?, "
            "presence = ? WHERE item_id = ?",
            (label, file_id, typing_state, PRESENCE_LIVE, existing["item_id"]),
        )
        return existing["item_id"]
    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, ?, ?, ?, NULL, ?, ?, ?, NULL, NULL, ?, NULL)",
        (item_id, item_type, label, file_id, external_key,
         PRESENCE_LIVE, typing_state, now),
    )
    return item_id


def _write_header(conn, item_id: str, **fields) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO item_headers ("
        "item_id, kind, external_id, thread_id, account_label, happened_at, "
        "ended_at, address_from, address_to, calendar_id, status, "
        "attachment_names, attachment_hashes"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            item_id, fields["kind"], fields["external_id"], fields["thread_id"],
            fields["account_label"], fields["happened_at"], fields["ended_at"],
            fields["address_from"], fields["address_to"], fields["calendar_id"],
            fields["status"], fields["attachment_names"], fields["attachment_hashes"],
        ),
    )


def _file_item(conn, file_id: str, path: str, now: str) -> str:
    row = conn.execute(
        "SELECT item_id FROM items WHERE file_id = ? AND item_type = 'file'",
        (file_id,),
    ).fetchone()
    if row is not None:
        return row["item_id"]
    item_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, external_key, "
        "presence, typing_state, type_schema, profile_id, created_at, superseded_by"
        ") VALUES (?, 'file', ?, ?, ?, NULL, ?, ?, NULL, NULL, ?, NULL)",
        (item_id, Path(path).name, file_id, path, PRESENCE_LIVE, UNPLACED, now),
    )
    return item_id


def _propose_attachment(conn, email_item: str, match, now: str) -> None:
    """A witnessed attachment link, proposed, never approved."""
    target = _file_item(conn, match["file_id"], match["current_path"], now)
    basis = json.dumps(
        {"rel_type": "attached-to", "from": email_item, "to": target,
         "hash": match["content_hash"]},
        sort_keys=True)
    existing = conn.execute(
        "SELECT relationship_id FROM relationships WHERE basis_key = ?",
        (basis,),
    ).fetchone()
    if existing is not None:
        return
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, rel_type, from_item_id, to_item_id, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by"
        ") VALUES (?, 'attached-to', ?, ?, 'witnessed', 'gmail', 'proposed', "
        "?, ?, ?, NULL, NULL)",
        (
            str(uuid.uuid4()), email_item, target,
            json.dumps(["content_hash"], sort_keys=True), basis, now,
        ),
    )

"""Recent conversations, kept on this Mac so the next session remembers.

Only the person's words and the assistant's replies are stored -- never tool
payloads, and never a line that names a protected file.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from items.file_identity import item_is_sensitive

DDL = """
CREATE TABLE IF NOT EXISTS conversation_turns (
    session_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    text TEXT NOT NULL,
    ts TEXT NOT NULL,
    PRIMARY KEY (session_id, seq)
);
"""


def _ensure(conn: sqlite3.Connection) -> None:
    conn.execute(DDL)


def names_a_protected_file(conn: sqlite3.Connection, text: str) -> bool:
    try:
        rows = conn.execute(
            "SELECT item_id FROM items WHERE length(display_label) >= 3 "
            "AND instr(lower(?), lower(display_label)) > 0",
            (text,)).fetchall()
    except sqlite3.Error:
        return False
    return any(item_is_sensitive(conn, r[0]) for r in rows)


def save_turn(conn: sqlite3.Connection, session_id: str, role: str,
              text: str) -> bool:
    """Store one line; False (and nothing stored) when it names a protected
    file or is not a person/assistant line."""
    if role not in ("user", "assistant") or not text.strip():
        return False
    if names_a_protected_file(conn, text):
        return False
    _ensure(conn)
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 FROM conversation_turns "
        "WHERE session_id = ?", (session_id,)).fetchone()[0]
    conn.execute(
        "INSERT INTO conversation_turns (session_id, seq, role, text, ts) "
        "VALUES (?, ?, ?, ?, ?)",
        (session_id, seq, role, text,
         datetime.now(timezone.utc).isoformat()))
    conn.commit()
    return True


def recent(conn: sqlite3.Connection, sessions: int = 5,
           exchanges: int = 20) -> list[dict]:
    """The last `exchanges` exchanges from the last `sessions` sessions, as
    chat messages, oldest first."""
    _ensure(conn)
    ids = [r[0] for r in conn.execute(
        "SELECT session_id FROM conversation_turns GROUP BY session_id "
        "ORDER BY MAX(ts) DESC LIMIT ?", (sessions,)).fetchall()]
    if not ids:
        return []
    marks = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT role, text FROM conversation_turns "
        f"WHERE session_id IN ({marks}) ORDER BY ts DESC, seq DESC LIMIT ?",
        (*ids, exchanges * 2)).fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


FORGOT_AT = "conversation_memory_cleared"


def forget(conn: sqlite3.Connection) -> int:
    """Delete every remembered turn, and record when, so a later session
    knows the empty memory was the person's choice."""
    from datetime import datetime, timezone
    from assistant.engine_tools import put_setting
    _ensure(conn)
    n = conn.execute("DELETE FROM conversation_turns").rowcount
    put_setting(conn, FORGOT_AT, datetime.now(timezone.utc).isoformat())
    conn.commit()
    return n


def forgot_line(conn: sqlite3.Connection) -> str:
    """The system-prompt sentence about the last forget, in local time, or
    "" when the person never cleared the memory."""
    from datetime import datetime
    from assistant.engine_tools import get_setting
    try:
        when = get_setting(conn, FORGOT_AT, "")
        local = datetime.fromisoformat(when).astimezone() if when else None
    except (sqlite3.Error, ValueError):
        return ""
    if local is None:
        return ""
    return ("The person cleared conversation memory on "
            f"{local.strftime('%-d %B %Y at %H:%M')} (their local time); you "
            "have no record before that. If asked, say it was cleared then.")

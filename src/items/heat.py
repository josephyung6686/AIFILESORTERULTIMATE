"""Item heat — user opens vs agent touches (Addendum T-P4-02).

Only ``user_heat`` may steer ranking additives. Agent touches are audited
separately and never inflate user heat.
"""
from __future__ import annotations

import sqlite3

HEAT_DDL = """
CREATE TABLE IF NOT EXISTS item_heat (
    item_id TEXT PRIMARY KEY,
    user_heat INTEGER NOT NULL DEFAULT 0,
    agent_touch INTEGER NOT NULL DEFAULT 0
);
"""


def ensure_heat_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(HEAT_DDL)


def bump_user_heat(conn: sqlite3.Connection, item_id: str, *, n: int = 1) -> int:
    ensure_heat_schema(conn)
    conn.execute(
        "INSERT INTO item_heat (item_id, user_heat, agent_touch) "
        "VALUES (?, ?, 0) ON CONFLICT(item_id) DO UPDATE SET "
        "user_heat = user_heat + excluded.user_heat",
        (item_id, n),
    )
    row = conn.execute(
        "SELECT user_heat FROM item_heat WHERE item_id = ?", (item_id,)
    ).fetchone()
    return int(row["user_heat"])


def bump_agent_touch(conn: sqlite3.Connection, item_id: str, *, n: int = 1) -> int:
    ensure_heat_schema(conn)
    conn.execute(
        "INSERT INTO item_heat (item_id, user_heat, agent_touch) "
        "VALUES (?, 0, ?) ON CONFLICT(item_id) DO UPDATE SET "
        "agent_touch = agent_touch + excluded.agent_touch",
        (item_id, n),
    )
    row = conn.execute(
        "SELECT agent_touch FROM item_heat WHERE item_id = ?", (item_id,)
    ).fetchone()
    return int(row["agent_touch"])


def user_heat(conn: sqlite3.Connection, item_id: str) -> int:
    ensure_heat_schema(conn)
    row = conn.execute(
        "SELECT user_heat FROM item_heat WHERE item_id = ?", (item_id,)
    ).fetchone()
    return int(row["user_heat"]) if row else 0

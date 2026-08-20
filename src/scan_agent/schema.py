# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL
from scan_agent.dataless import DATALESS_DDL
from scan_agent.deferrals import DEFERRALS_DDL
from scan_agent.stat_cache import STAT_CACHE_DDL
from scan_agent.inventory import INVENTORY_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(DATALESS_DDL)
    conn.executescript(DEFERRALS_DDL)
    conn.executescript(STAT_CACHE_DDL)
    conn.executescript(INVENTORY_DDL)

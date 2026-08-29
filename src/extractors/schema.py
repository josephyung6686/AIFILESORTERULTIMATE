# src/extractors/schema.py
"""P5's own tables. They live inside P1's single local SQLite database (section 0);
P1 owns the handle, the transaction boundary, `files` and `events`.

P5 creates NO P4 table: `evidence`, `extraction_runs` and `text_units` are P4's, and
P5 writes them through the sink (src/extractors/sink.py).
"""
from __future__ import annotations

import sqlite3

from extractors.router import ROUTING_DDL
from extractors.long_tail import SENSITIVITY_DDL


def create_extraction_schema(conn: sqlite3.Connection) -> None:
    """Create every P5-owned table. Idempotent. P1's `create_schema` runs first.

    Two tables, both P5's own: the routing decision per file (section 2.9) and the
    sensitivity signal per located value (section 2.9, section 8.4). P4's `evidence`,
    `extraction_runs` and `text_units` are created here never.
    """
    conn.executescript(ROUTING_DDL)
    conn.executescript(SENSITIVITY_DDL)

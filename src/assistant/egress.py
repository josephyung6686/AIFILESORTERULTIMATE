"""Persistent egress ledger — user-viewable cloud turn audit.

One ledger row per provider request. Bytes come from serialized
request + response envelopes. Session totals derive from those rows.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

from assistant.policy import envelope_bytes

EGRESS_DDL = """
CREATE TABLE IF NOT EXISTS egress_ledger (
    turn_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    item_ids_json TEXT NOT NULL,
    bytes INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    question TEXT
);
CREATE INDEX IF NOT EXISTS egress_ledger_by_session
    ON egress_ledger(session_id, ts);
"""


def ensure_egress_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(EGRESS_DDL)


@dataclass(frozen=True)
class EgressRow:
    turn_id: str
    ts: str
    provider: str
    model: str
    item_ids: tuple[str, ...]
    bytes: int
    session_id: str
    question: str | None = None
    bytes_in: int = 0
    bytes_out: int = 0
    egress_class: str = "cloud"


class PersistentEgress:
    """Append-only ledger. Never stores file bodies.

    One row per provider request. ``bytes`` = request envelope + response
    envelope sizes. Session summary is the sum of those rows.
    """

    def __init__(self, conn: sqlite3.Connection, *,
                 session_id: str | None = None) -> None:
        ensure_egress_schema(conn)
        self.conn = conn
        self.session_id = session_id or str(uuid.uuid4())
        self.rows: list[EgressRow] = []

    def add(
            self, *,
            provider: str,
            model: str,
            item_ids: Sequence[str],
            bytes_out: int,
            question: str | None = None,
            bytes_in: int = 0,
            egress_class: str = "cloud",
    ) -> EgressRow:
        total = int(bytes_in) + int(bytes_out)
        row = EgressRow(
            turn_id=str(uuid.uuid4()),
            ts=datetime.now(timezone.utc).isoformat(),
            provider=provider,
            model=model,
            item_ids=tuple(item_ids),
            bytes=total,
            session_id=self.session_id,
            question=question,
            bytes_in=int(bytes_in),
            bytes_out=int(bytes_out),
            egress_class=egress_class,
        )
        self.conn.execute(
            "INSERT INTO egress_ledger ("
            "turn_id, ts, provider, model, item_ids_json, bytes, "
            "session_id, question) VALUES (?,?,?,?,?,?,?,?)",
            (
                row.turn_id, row.ts, row.provider, row.model,
                json.dumps(list(row.item_ids)), row.bytes,
                row.session_id, row.question,
            ),
        )
        self.rows.append(row)
        return row

    def add_provider_request(
            self, *,
            provider: str,
            model: str,
            request_envelope: Any,
            response_envelope: Any,
            item_ids: Sequence[str] = (),
            question: str | None = None,
            egress_class: str = "cloud",
    ) -> EgressRow:
        """Record one provider round-trip from serialized envelopes."""
        bin_ = envelope_bytes(request_envelope)
        bout = envelope_bytes(response_envelope)
        return self.add(
            provider=provider,
            model=model,
            item_ids=item_ids,
            bytes_in=bin_,
            bytes_out=bout,
            question=question,
            egress_class=egress_class,
        )

    def session_rows(self) -> list[dict[str, Any]]:
        out = []
        for row in self.conn.execute(
            "SELECT turn_id, ts, provider, model, item_ids_json, bytes, "
            "session_id, question FROM egress_ledger "
            "WHERE session_id = ? ORDER BY ts",
            (self.session_id,),
        ):
            out.append({
                "turn_id": row["turn_id"],
                "ts": row["ts"],
                "provider": row["provider"],
                "model": row["model"],
                "item_ids": json.loads(row["item_ids_json"] or "[]"),
                "bytes": row["bytes"],
                "session_id": row["session_id"],
                "question": row["question"],
            })
        return out

    def total_bytes(self) -> int:
        """Session summary derived from per-request ledger rows."""
        if self.rows:
            return sum(r.bytes for r in self.rows)
        rows = self.session_rows()
        return sum(int(r["bytes"]) for r in rows)

    def session_summary(self) -> dict[str, Any]:
        rows = self.session_rows()
        return {
            "session_id": self.session_id,
            "request_count": len(rows),
            "total_bytes": sum(int(r["bytes"]) for r in rows),
            "rows": rows,
        }

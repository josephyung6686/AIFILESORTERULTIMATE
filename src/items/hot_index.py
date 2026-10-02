"""Hot index for product find: FTS5 + stored vectors + RRF fusion.

Rebuilds ``item_fts`` from live items (+ short evidence text). Vector search
uses existing ``vector_embeddings`` rows and an optional MiniLM query encoder.
Never moves files. Never writes relationships.
"""
from __future__ import annotations

import re
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from items.mailbox import path_is_protected

RRF_K = 60
DEFAULT_LIMIT = 20
CHUNK_CHARS = 800
FTS_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS item_fts USING fts5(
    item_id UNINDEXED,
    label,
    path,
    body,
    tokenize = 'porter unicode61'
);
"""
CHUNKS_DDL = """
CREATE TABLE IF NOT EXISTS item_chunks (
    chunk_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    text TEXT NOT NULL,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS item_chunks_by_item
    ON item_chunks(item_id, ordinal);
"""
_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]+")
_SAFE = re.compile(r"[^\w\s./\-]+", re.UNICODE)
_ENCODER_CACHE: dict[str, object] = {}


@dataclass(frozen=True)
class FindHit:
    item_id: str
    display_label: str
    open_target: str | None
    typing_state: str
    score: float
    channels: tuple[str, ...]
    protected: bool
    citations: tuple[str, ...]


@dataclass(frozen=True)
class FindResult:
    hits: tuple[FindHit, ...]
    protected_count: int
    fts_ms: float
    vector_ms: float
    total_ms: float
    fts_used: bool
    vector_used: bool
    moved: bool = False


def ensure_fts(conn: sqlite3.Connection) -> None:
    conn.executescript(FTS_DDL)
    conn.executescript(CHUNKS_DDL)


def cjk_bigrams(text: str) -> str:
    """Space-separated CJK bigrams (+ unigrams) for unicode61 FTS."""
    parts: list[str] = []
    for run in _CJK.findall(text or ""):
        if len(run) == 1:
            parts.append(run)
            continue
        parts.extend(run[i:i + 2] for i in range(len(run) - 1))
        parts.extend(list(run))  # unigrams for 1–2 char queries
    return " ".join(parts)


def _chunk_text(text: str, *, size: int = CHUNK_CHARS) -> list[tuple[int, int, str]]:
    text = text or ""
    if not text:
        return []
    out = []
    i = 0
    ord_n = 0
    while i < len(text):
        piece = text[i:i + size]
        out.append((i, i + len(piece), piece))
        i += size
        ord_n += 1
        if ord_n > 40:
            break
    return out


def rebuild_fts(conn: sqlite3.Connection, *, evidence_chars: int = 4000) -> int:
    """Rebuild FTS + item_chunks from live items. Returns FTS row count."""
    ensure_fts(conn)
    conn.execute("DELETE FROM item_fts")
    conn.execute("DELETE FROM item_chunks")
    rows = conn.execute(
        "SELECT item_id, display_label, open_target, file_id FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL"
    ).fetchall()
    n = 0
    for row in rows:
        body = ""
        if row["file_id"]:
            body = _evidence_snippet(conn, row["file_id"], evidence_chars)
        label = row["display_label"] or ""
        path = row["open_target"] or ""
        cjk_extra = cjk_bigrams(f"{label} {path} {body}")
        indexed_body = body
        if cjk_extra:
            indexed_body = f"{body}\n{cjk_extra}".strip()
        conn.execute(
            "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
            (row["item_id"], f"{label} {cjk_bigrams(label)}".strip(),
             f"{path} {cjk_bigrams(path)}".strip(), indexed_body),
        )
        for ordinal, (start, end, piece) in enumerate(
                _chunk_text(body or label)):
            chunk_id = f"{row['item_id']}:{ordinal}"
            conn.execute(
                "INSERT INTO item_chunks ("
                "chunk_id, item_id, ordinal, text, char_start, char_end) "
                "VALUES (?,?,?,?,?,?)",
                (chunk_id, row["item_id"], ordinal, piece, start, end),
            )
        n += 1
    return n


def find_files(
        conn: sqlite3.Connection,
        query: str,
        *,
        limit: int = DEFAULT_LIMIT,
        model_dir: Path | None = None,
) -> FindResult:
    """Hybrid find. Product hot path."""
    started = time.perf_counter()
    if limit <= 0:
        raise ValueError("limit must be positive")
    q = (query or "").strip()
    if not q:
        return FindResult((), 0, 0.0, 0.0, 0.0, False, False)

    ensure_fts(conn)
    # Auto-build if empty.
    if conn.execute("SELECT COUNT(*) FROM item_fts").fetchone()[0] == 0:
        rebuild_fts(conn)

    t0 = time.perf_counter()
    fts_ranks = _fts_search(conn, q, limit=max(limit * 5, 50))
    fts_ms = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    vec_ranks, vector_used = _vector_search(
        conn, q, limit=max(limit * 5, 50), model_dir=model_dir)
    vector_ms = (time.perf_counter() - t1) * 1000.0

    fused = _rrf([fts_ranks, vec_ranks], k=RRF_K)
    hits: list[FindHit] = []
    protected_count = 0
    for item_id, score in fused[:limit]:
        row = conn.execute(
            "SELECT item_id, display_label, open_target, typing_state "
            "FROM items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            continue
        protected = bool(
            row["open_target"] and path_is_protected(row["open_target"]))
        if protected:
            protected_count += 1
        channels = []
        if item_id in fts_ranks:
            channels.append("fts")
        if item_id in vec_ranks:
            channels.append("vector")
        hits.append(FindHit(
            item_id=row["item_id"],
            display_label=row["display_label"],
            open_target=None if protected else row["open_target"],
            typing_state=row["typing_state"],
            score=score,
            channels=tuple(channels),
            protected=protected,
            citations=(row["item_id"],),
        ))
    total_ms = (time.perf_counter() - started) * 1000.0
    return FindResult(
        hits=tuple(hits),
        protected_count=protected_count,
        fts_ms=fts_ms,
        vector_ms=vector_ms,
        total_ms=total_ms,
        fts_used=bool(fts_ranks),
        vector_used=vector_used,
    )


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,),
    ).fetchone()
    return row is not None


def _evidence_snippet(conn, file_id: str, n: int) -> str:
    if not file_id or not _table_exists(conn, "evidence"):
        return ""
    parts = []
    size = 0
    for row in conn.execute(
        "SELECT raw_value FROM evidence WHERE file_id = ? "
        "AND superseded_by IS NULL AND raw_value IS NOT NULL "
        "ORDER BY rowid LIMIT 40",
        (file_id,),
    ):
        text = (row["raw_value"] or "").strip()
        if len(text) < 8:
            continue
        # Take as much of this row as remaining budget allows (was capped at
        # 400 chars/row, which collapsed long PDFs to one chunk).
        take = text[: max(0, n - size)]
        if not take:
            break
        parts.append(take)
        size += len(take)
        if size >= n:
            break
    return "\n".join(parts)[:n]


def _fts_search(conn, query: str, *, limit: int) -> dict[str, int]:
    # Latin tokens + CJK bigrams/unigrams for unicode61 FTS.
    latin = [t for t in _SAFE.sub(" ", query).split() if t]
    cjk_terms = cjk_bigrams(query).split()
    tokens = list(dict.fromkeys(latin + cjk_terms))[:24]
    ranks: dict[str, int] = {}
    if tokens:
        match = " OR ".join(f'"{t}"' for t in tokens)
        try:
            rows = conn.execute(
                "SELECT item_id FROM item_fts WHERE item_fts MATCH ? "
                "ORDER BY bm25(item_fts) LIMIT ?",
                (match, limit),
            ).fetchall()
            ranks = {
                row["item_id"]: rank for rank, row in enumerate(rows, start=1)
            }
        except sqlite3.OperationalError:
            try:
                rows = conn.execute(
                    "SELECT item_id FROM item_fts WHERE item_fts MATCH ? "
                    "LIMIT ?",
                    (" OR ".join(tokens), limit),
                ).fetchall()
                ranks = {
                    row["item_id"]: rank
                    for rank, row in enumerate(rows, start=1)
                }
            except sqlite3.OperationalError:
                ranks = {}

    # Kill criterion: 1–2 char CJK must not return empty when label contains them.
    cjk_runs = _CJK.findall(query)
    short = [r for r in cjk_runs if 1 <= len(r) <= 2]
    if short and len(ranks) < limit:
        for needle in short:
            like = f"%{needle}%"
            rows = conn.execute(
                "SELECT item_id FROM items WHERE presence = 'live' "
                "AND superseded_by IS NULL AND ("
                "display_label LIKE ? OR IFNULL(open_target,'') LIKE ?) "
                "LIMIT ?",
                (like, like, limit),
            ).fetchall()
            for row in rows:
                if row["item_id"] not in ranks:
                    ranks[row["item_id"]] = len(ranks) + 1
    return ranks


def _vector_search(conn, query: str, *, limit: int,
                   model_dir: Path | None) -> tuple[dict[str, int], bool]:
    if not _table_exists(conn, "vector_embeddings"):
        return {}, False
    rows = conn.execute(
        "SELECT v.file_id, v.array_bytes, v.dimension, i.item_id "
        "FROM vector_embeddings v "
        "JOIN items i ON i.file_id = v.file_id "
        "WHERE v.superseded_by IS NULL AND i.presence = 'live' "
        "AND i.superseded_by IS NULL AND i.item_type = 'file'"
    ).fetchall()
    if not rows:
        return {}, False
    try:
        import numpy
        from readers.embedding_minilm import MiniLmEncoder, ModelUnavailable
    except Exception:
        return {}, False
    directory = model_dir or (
        Path.home() / ".graph-agent" / "models" / "minilm")
    key = str(directory.resolve()) if directory.exists() else str(directory)
    encoder = _ENCODER_CACHE.get(key)
    if encoder is None:
        try:
            encoder = MiniLmEncoder(
                directory, max_tokens=256, batch=16, threads=2)
        except Exception:
            return {}, False
        _ENCODER_CACHE[key] = encoder
    try:
        q = encoder.encode([query])[0]
    except Exception:
        return {}, False

    scored: list[tuple[float, str]] = []
    for row in rows:
        dim = int(row["dimension"])
        blob = row["array_bytes"]
        if len(blob) != dim * 4:
            continue
        vec = numpy.frombuffer(blob, dtype="<f4")
        if vec.shape[0] != dim or q.shape[0] != dim:
            continue
        score = float(numpy.dot(q, vec))  # both unit-norm → cosine
        scored.append((score, row["item_id"]))
    scored.sort(reverse=True)
    ranks = {item_id: rank for rank, (_s, item_id) in enumerate(scored[:limit], 1)}
    return ranks, True


def _rrf(rank_maps: list[dict[str, int]], *, k: int) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranks in rank_maps:
        for item_id, rank in ranks.items():
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

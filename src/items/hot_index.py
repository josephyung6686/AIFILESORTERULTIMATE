"""Hot index for product find: chunk FTS5 + vectors + RRF fusion.

Rebuilds ``item_fts`` / ``item_chunks`` / ``item_chunk_fts`` from live items.
Search aggregates chunk ranks to item ranks and retains the best matching
chunk citation. Filename/path matches are never reported as body matches.
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
MAX_CHUNKS_PER_ITEM = 40
# Index past the historical 4k evidence cap so late markers remain findable.
MAX_BODY_CHARS = CHUNK_CHARS * MAX_CHUNKS_PER_ITEM
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
    char_end INTEGER NOT NULL,
    source_id TEXT
);
CREATE INDEX IF NOT EXISTS item_chunks_by_item
    ON item_chunks(item_id, ordinal);
"""
CHUNK_FTS_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS item_chunk_fts USING fts5(
    chunk_id UNINDEXED,
    item_id UNINDEXED,
    text,
    tokenize = 'porter unicode61'
);
"""
CHUNK_VEC_DDL = """
CREATE TABLE IF NOT EXISTS item_chunk_embeddings (
    chunk_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding_model_id TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    array_bytes BLOB NOT NULL,
    PRIMARY KEY (chunk_id, embedding_model_id)
);
CREATE INDEX IF NOT EXISTS item_chunk_embeddings_by_item
    ON item_chunk_embeddings(item_id);
"""
_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]+")
_SAFE = re.compile(r"[^\w\s./\-]+", re.UNICODE)
_ENCODER_CACHE: dict[str, object] = {}

# Freshness states that must never appear as live search hits.
_NOT_LIVE_FRESHNESS = frozenset({"missing", "conflicted"})


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
    match_fields: tuple[str, ...] = ()
    best_chunk_id: str | None = None
    source_ids: tuple[str, ...] = ()
    claims_body_match: bool = False


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
    mode: str = "hybrid"


def ensure_fts(conn: sqlite3.Connection) -> None:
    conn.executescript(FTS_DDL)
    conn.executescript(CHUNKS_DDL)
    conn.executescript(CHUNK_FTS_DDL)
    conn.executescript(CHUNK_VEC_DDL)
    _ensure_chunk_source_column(conn)


def _ensure_chunk_source_column(conn: sqlite3.Connection) -> None:
    cols = {
        row[1]
        for row in conn.execute("PRAGMA table_info(item_chunks)").fetchall()
    }
    if cols and "source_id" not in cols:
        conn.execute("ALTER TABLE item_chunks ADD COLUMN source_id TEXT")


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
        if ord_n >= MAX_CHUNKS_PER_ITEM:
            break
    return out


def _query_tokens(query: str) -> list[str]:
    latin = [t for t in _SAFE.sub(" ", query).split() if t]
    cjk_terms = cjk_bigrams(query).split()
    return list(dict.fromkeys(latin + cjk_terms))[:24]


def _match_expr(tokens: list[str]) -> str:
    return " OR ".join(f'"{t}"' for t in tokens)


def write_chunks_for_item(
        conn: sqlite3.Connection,
        item_id: str,
        body: str,
        *,
        label: str = "",
        source_ids: list[str] | None = None,
) -> list[str]:
    """Persist chunks + chunk FTS for one item. Returns chunk_ids written."""
    ensure_fts(conn)
    text = body if body else (label or "")
    chunk_ids: list[str] = []
    primary_source = (source_ids or [None])[0]
    for ordinal, (start, end, piece) in enumerate(_chunk_text(text)):
        chunk_id = f"{item_id}:{ordinal}"
        cjk_extra = cjk_bigrams(piece)
        indexed = f"{piece}\n{cjk_extra}".strip() if cjk_extra else piece
        conn.execute(
            "INSERT INTO item_chunks ("
            "chunk_id, item_id, ordinal, text, char_start, char_end, source_id) "
            "VALUES (?,?,?,?,?,?,?)",
            (chunk_id, item_id, ordinal, piece, start, end, primary_source),
        )
        conn.execute(
            "INSERT INTO item_chunk_fts (chunk_id, item_id, text) VALUES (?,?,?)",
            (chunk_id, item_id, indexed),
        )
        chunk_ids.append(chunk_id)
    return chunk_ids


def delete_chunks_for_item(conn: sqlite3.Connection, item_id: str) -> None:
    ensure_fts(conn)
    try:
        conn.execute(
            "DELETE FROM item_chunk_fts WHERE item_id = ?", (item_id,))
    except sqlite3.OperationalError:
        pass
    conn.execute("DELETE FROM item_chunks WHERE item_id = ?", (item_id,))
    conn.execute(
        "DELETE FROM item_chunk_embeddings WHERE item_id = ?", (item_id,))


def rebuild_fts(
        conn: sqlite3.Connection,
        *,
        evidence_chars: int = MAX_BODY_CHARS,
        embed_chunks: bool = False,
        model_dir: Path | None = None,
) -> int:
    """Full rebuild of FTS + item_chunks from live items. Returns FTS row count.

    Prefer ``items.index_refresh`` for incremental catch-up; this remains the
    explicit rebuild path (CLI / maintenance).
    """
    from items.freshness import mark_indexed
    from items.index_refresh import (
        _body_for_item,
        _evidence_source_ids,
        ensure_refresh_schema,
        set_index_state,
        READY,
    )

    ensure_fts(conn)
    ensure_refresh_schema(conn)
    conn.execute("DELETE FROM item_fts")
    conn.execute("DELETE FROM item_chunks")
    conn.execute("DELETE FROM item_chunk_embeddings")
    try:
        conn.execute("DELETE FROM item_chunk_fts")
    except sqlite3.OperationalError:
        conn.execute("DROP TABLE IF EXISTS item_chunk_fts")
        conn.executescript(CHUNK_FTS_DDL)
    rows = conn.execute(
        "SELECT item_id, display_label, open_target, file_id, content_hash "
        "FROM items "
        "WHERE presence = 'live' AND superseded_by IS NULL"
    ).fetchall()
    n = 0
    pending_embed: list[tuple[str, str, str, str]] = []
    for row in rows:
        body = _body_for_item(conn, row, evidence_chars=evidence_chars)
        label = row["display_label"] or ""
        path = row["open_target"] or ""
        source_ids = (
            _evidence_source_ids(conn, row["file_id"]) if row["file_id"] else []
        )
        cjk_extra = cjk_bigrams(f"{label} {path} {body}")
        indexed_body = body
        if cjk_extra:
            indexed_body = f"{body}\n{cjk_extra}".strip()
        conn.execute(
            "INSERT INTO item_fts (item_id, label, path, body) VALUES (?,?,?,?)",
            (row["item_id"], f"{label} {cjk_bigrams(label)}".strip(),
             f"{path} {cjk_bigrams(path)}".strip(), indexed_body),
        )
        chunk_ids = write_chunks_for_item(
            conn, row["item_id"], body, label=label, source_ids=source_ids)
        digest = row["content_hash"] or ""
        if embed_chunks and digest:
            for chunk_id in chunk_ids:
                text = conn.execute(
                    "SELECT text FROM item_chunks WHERE chunk_id = ?",
                    (chunk_id,),
                ).fetchone()["text"]
                pending_embed.append(
                    (chunk_id, row["item_id"], digest, text))
        if digest:
            mark_indexed(conn, row["item_id"], digest, reason="full_rebuild")
        n += 1
    if pending_embed:
        _store_chunk_embeddings(conn, pending_embed, model_dir=model_dir)
    # Clear refresh queue — full rebuild is authoritative.
    conn.execute("DELETE FROM index_refresh_queue")
    set_index_state(conn, READY)
    return n


def find_files(
        conn: sqlite3.Connection,
        query: str,
        *,
        limit: int = DEFAULT_LIMIT,
        model_dir: Path | None = None,
        mode: str | None = None,
) -> FindResult:
    """Hybrid find (chunk FTS + vectors) or FTS-only. Product hot path."""
    started = time.perf_counter()
    if limit <= 0:
        raise ValueError("limit must be positive")
    q = (query or "").strip()
    if not q:
        return FindResult((), 0, 0.0, 0.0, 0.0, False, False)

    from items.search_mode import resolve_search_mode
    search_mode = resolve_search_mode(mode)

    ensure_fts(conn)
    # Catch up the refresh queue before answering — never serve stale as fresh.
    from items.index_refresh import ensure_search_ready
    ensure_search_ready(conn)

    fetch_n = max(limit * 5, 50)
    t0 = time.perf_counter()
    chunk_ranks, best_chunks = _chunk_fts_search(conn, q, limit=fetch_n)
    filename_ranks = _filename_fts_search(conn, q, limit=fetch_n)
    # Legacy item-level body FTS as a backstop (short docs / label-only chunks).
    item_ranks = _fts_search(conn, q, limit=fetch_n)
    fts_ms = (time.perf_counter() - t0) * 1000.0

    # Prefer chunk ranks for lexical body; merge filename + item for coverage.
    fts_ranks: dict[str, int] = {}
    for ranks in (chunk_ranks, filename_ranks, item_ranks):
        for item_id, rank in ranks.items():
            prev = fts_ranks.get(item_id)
            if prev is None or rank < prev:
                fts_ranks[item_id] = rank
    # Re-number densely for RRF stability.
    fts_ranks = {
        item_id: rank
        for rank, (item_id, _) in enumerate(
            sorted(fts_ranks.items(), key=lambda kv: kv[1]), start=1)
    }

    t1 = time.perf_counter()
    vec_ranks: dict[str, int] = {}
    vec_best_chunks: dict[str, str] = {}
    vector_used = False
    if search_mode == "hybrid":
        vec_ranks, vec_best_chunks, vector_used = _chunk_vector_search(
            conn, q, limit=fetch_n, model_dir=model_dir)
        if not vector_used:
            file_ranks, vector_used = _vector_search(
                conn, q, limit=fetch_n, model_dir=model_dir)
            vec_ranks = file_ranks
    vector_ms = (time.perf_counter() - t1) * 1000.0

    if search_mode == "fts":
        fused = _rrf([fts_ranks], k=RRF_K)
        vector_used = False
    else:
        fused = _rrf([fts_ranks, vec_ranks], k=RRF_K)

    hits: list[FindHit] = []
    protected_count = 0
    for item_id, score in fused:
        if len(hits) >= limit:
            break
        row = conn.execute(
            "SELECT item_id, display_label, open_target, typing_state, "
            "presence, freshness_state, content_hash, last_indexed_hash "
            "FROM items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        if row is None or not _is_live_searchable(row):
            continue
        protected = bool(
            row["open_target"] and path_is_protected(row["open_target"]))
        if protected:
            protected_count += 1

        chunk_id = best_chunks.get(item_id) or vec_best_chunks.get(item_id)
        in_chunk = item_id in chunk_ranks or item_id in vec_best_chunks
        in_filename = item_id in filename_ranks
        in_item_fts = item_id in item_ranks

        match_fields: list[str] = []
        if in_filename:
            match_fields.append("filename")
        if in_chunk:
            match_fields.append("chunk")
        elif in_item_fts and not in_filename:
            # Item FTS body hit without a chunk row (e.g. empty body/label path).
            match_fields.append("evidence")
        elif in_item_fts and in_filename and item_id not in chunk_ranks:
            # Could be path-only; do not claim body.
            pass

        claims_body = "chunk" in match_fields or "evidence" in match_fields
        source_ids = _source_ids_for_hit(conn, item_id, chunk_id)
        if source_ids and claims_body and "evidence" not in match_fields:
            match_fields.append("evidence")

        citations: list[str] = [row["item_id"]]
        if claims_body and chunk_id:
            citations.append(chunk_id)
        citations.extend(source_ids)

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
            citations=tuple(dict.fromkeys(citations)),
            match_fields=tuple(match_fields) or (
                ("filename",) if in_filename else ()),
            best_chunk_id=chunk_id if claims_body else None,
            source_ids=tuple(source_ids),
            claims_body_match=claims_body,
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
        mode=search_mode,
    )


def _row_get(row, key: str, default=None):
    try:
        keys = row.keys()
    except Exception:
        return default
    return row[key] if key in keys else default


def _is_live_searchable(row) -> bool:
    """Deleted / missing / stale indexed evidence must not surface as live hits."""
    if _row_get(row, "presence") != "live":
        return False
    state = _row_get(row, "freshness_state")
    if state in _NOT_LIVE_FRESHNESS:
        return False
    content_hash = _row_get(row, "content_hash") or _row_get(row, "item_hash")
    indexed = _row_get(row, "last_indexed_hash")
    # Stale: disk hash diverged from what the index was built from.
    if content_hash and indexed and content_hash != indexed:
        return False
    return True


def _source_ids_for_hit(
        conn: sqlite3.Connection, item_id: str, chunk_id: str | None,
) -> list[str]:
    ids: list[str] = []
    if chunk_id:
        row = conn.execute(
            "SELECT source_id FROM item_chunks WHERE chunk_id = ?",
            (chunk_id,),
        ).fetchone()
        if row and row["source_id"]:
            ids.append(row["source_id"])
    item = conn.execute(
        "SELECT file_id FROM items WHERE item_id = ?", (item_id,),
    ).fetchone()
    if item and item["file_id"] and _table_exists(conn, "evidence"):
        for erow in conn.execute(
            "SELECT * FROM evidence WHERE file_id = ? "
            "AND superseded_by IS NULL LIMIT 8",
            (item["file_id"],),
        ):
            # Support both evidence_id and observation_id schemas.
            eid = None
            keys = erow.keys()
            if "evidence_id" in keys:
                eid = erow["evidence_id"]
            elif "observation_id" in keys:
                eid = erow["observation_id"]
            if eid and eid not in ids:
                ids.append(eid)
    return ids


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type IN ('table','view') "
        "AND name = ?",
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
        take = text[: max(0, n - size)]
        if not take:
            break
        parts.append(take)
        size += len(take)
        if size >= n:
            break
    return "\n".join(parts)[:n]


def _filename_fts_search(conn, query: str, *, limit: int) -> dict[str, int]:
    """Match label/path columns only — never implies a body citation."""
    tokens = _query_tokens(query)
    ranks: dict[str, int] = {}
    if tokens:
        # FTS5 column filter: label:"tok" OR path:"tok"
        col_parts = []
        for t in tokens:
            col_parts.append(f'label:"{t}"')
            col_parts.append(f'path:"{t}"')
        col_match = " OR ".join(col_parts)
        try:
            rows = conn.execute(
                "SELECT item_id FROM item_fts WHERE item_fts MATCH ? "
                "ORDER BY bm25(item_fts) LIMIT ?",
                (col_match, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
        for row in rows:
            if row["item_id"] not in ranks:
                ranks[row["item_id"]] = len(ranks) + 1

    cjk_runs = _CJK.findall(query)
    short = [r for r in cjk_runs if 1 <= len(r) <= 2]
    if short and len(ranks) < limit:
        for needle in short:
            like = f"%{needle}%"
            rows = conn.execute(
                "SELECT item_id FROM items WHERE presence = 'live' "
                "AND superseded_by IS NULL AND ("
                "display_label LIKE ? OR IFNULL(open_target,'') LIKE ?) "
                "AND freshness_state NOT IN ('missing','conflicted') "
                "LIMIT ?",
                (like, like, limit),
            ).fetchall()
            for row in rows:
                if row["item_id"] not in ranks:
                    ranks[row["item_id"]] = len(ranks) + 1
    return ranks


def _chunk_fts_search(
        conn, query: str, *, limit: int,
) -> tuple[dict[str, int], dict[str, str]]:
    """Search item_chunk_fts; aggregate to item ranks; keep best chunk_id."""
    tokens = _query_tokens(query)
    ranks: dict[str, int] = {}
    best: dict[str, str] = {}
    if not tokens or not _table_exists(conn, "item_chunk_fts"):
        return ranks, best
    match = _match_expr(tokens)
    rows = []
    try:
        rows = conn.execute(
            "SELECT chunk_id, item_id FROM item_chunk_fts "
            "WHERE item_chunk_fts MATCH ? "
            "ORDER BY bm25(item_chunk_fts) LIMIT ?",
            (match, max(limit * 4, 80)),
        ).fetchall()
    except sqlite3.OperationalError:
        try:
            rows = conn.execute(
                "SELECT chunk_id, item_id FROM item_chunk_fts "
                "WHERE item_chunk_fts MATCH ? LIMIT ?",
                (" OR ".join(tokens), max(limit * 4, 80)),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = []
    for row in rows:
        item_id = row["item_id"]
        if item_id in ranks:
            continue
        ranks[item_id] = len(ranks) + 1
        best[item_id] = row["chunk_id"]
        if len(ranks) >= limit:
            break
    return ranks, best


def _fts_search(conn, query: str, *, limit: int) -> dict[str, int]:
    """Item-level FTS (label/path/body). Used as coverage backstop."""
    tokens = _query_tokens(query)
    ranks: dict[str, int] = {}
    if tokens:
        match = _match_expr(tokens)
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


def _get_encoder(model_dir: Path | None):
    try:
        from readers.embedding_minilm import MiniLmEncoder
    except Exception:
        return None
    directory = model_dir or (
        Path.home() / ".graph-agent" / "models" / "minilm")
    key = str(directory.resolve()) if directory.exists() else str(directory)
    encoder = _ENCODER_CACHE.get(key)
    if encoder is None:
        try:
            encoder = MiniLmEncoder(
                directory, max_tokens=256, batch=16, threads=2)
        except Exception:
            return None
        _ENCODER_CACHE[key] = encoder
    return encoder


def _store_chunk_embeddings(
        conn: sqlite3.Connection,
        rows: list[tuple],
        *,
        model_dir: Path | None = None,
) -> int:
    """rows: (chunk_id, item_id, content_hash, text)."""
    encoder = _get_encoder(model_dir)
    if encoder is None or not rows:
        return 0
    try:
        import numpy
    except Exception:
        return 0
    texts = [r[3] for r in rows]
    try:
        vectors = encoder.encode(texts)
    except Exception:
        return 0
    model_id = "minilm"
    n = 0
    for (chunk_id, item_id, content_hash, _text), vec in zip(rows, vectors):
        blob = numpy.asarray(vec, dtype="<f4").tobytes()
        conn.execute(
            "INSERT OR REPLACE INTO item_chunk_embeddings ("
            "chunk_id, item_id, content_hash, embedding_model_id, "
            "dimension, array_bytes) VALUES (?,?,?,?,?,?)",
            (chunk_id, item_id, content_hash, model_id, int(vec.shape[0]), blob),
        )
        n += 1
    return n


def embed_all_chunks(
        conn: sqlite3.Connection, *, model_dir: Path | None = None,
) -> int:
    """Embed every current chunk. Used by evaluate_search / bakeoff."""
    ensure_fts(conn)
    rows = conn.execute(
        "SELECT c.chunk_id, c.item_id, c.text, i.content_hash "
        "FROM item_chunks c "
        "JOIN items i ON i.item_id = c.item_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL"
    ).fetchall()
    payload = [
        (r["chunk_id"], r["item_id"], r["content_hash"] or "", r["text"])
        for r in rows
    ]
    return _store_chunk_embeddings(conn, payload, model_dir=model_dir)


def _chunk_vector_search(
        conn, query: str, *, limit: int, model_dir: Path | None,
) -> tuple[dict[str, int], dict[str, str], bool]:
    if not _table_exists(conn, "item_chunk_embeddings"):
        return {}, {}, False
    rows = conn.execute(
        "SELECT e.chunk_id, e.item_id, e.array_bytes, e.dimension, "
        "e.content_hash AS embed_hash, i.content_hash, i.presence, "
        "i.freshness_state, i.last_indexed_hash "
        "FROM item_chunk_embeddings e "
        "JOIN items i ON i.item_id = e.item_id "
        "WHERE i.presence = 'live' AND i.superseded_by IS NULL"
    ).fetchall()
    if not rows:
        return {}, {}, False
    encoder = _get_encoder(model_dir)
    if encoder is None:
        return {}, {}, False
    try:
        import numpy
        q = encoder.encode([query])[0]
    except Exception:
        return {}, {}, False

    scored: list[tuple[float, str, str]] = []
    for row in rows:
        if not _is_live_searchable(row):
            continue
        # Drop embeddings built against a prior content hash.
        if row["embed_hash"] and row["content_hash"] and (
                row["embed_hash"] != row["content_hash"]):
            continue
        dim = int(row["dimension"])
        blob = row["array_bytes"]
        if len(blob) != dim * 4:
            continue
        vec = numpy.frombuffer(blob, dtype="<f4")
        if vec.shape[0] != dim or q.shape[0] != dim:
            continue
        score = float(numpy.dot(q, vec))
        scored.append((score, row["item_id"], row["chunk_id"]))
    scored.sort(reverse=True)
    ranks: dict[str, int] = {}
    best: dict[str, str] = {}
    for score, item_id, chunk_id in scored:
        if item_id in ranks:
            continue
        ranks[item_id] = len(ranks) + 1
        best[item_id] = chunk_id
        if len(ranks) >= limit:
            break
    return ranks, best, True


def _vector_search(conn, query: str, *, limit: int,
                   model_dir: Path | None) -> tuple[dict[str, int], bool]:
    if not _table_exists(conn, "vector_embeddings"):
        return {}, False
    rows = conn.execute(
        "SELECT v.file_id, v.array_bytes, v.dimension, i.item_id, "
        "i.presence, i.freshness_state, i.content_hash, i.last_indexed_hash "
        "FROM vector_embeddings v "
        "JOIN items i ON i.file_id = v.file_id "
        "WHERE v.superseded_by IS NULL AND i.presence = 'live' "
        "AND i.superseded_by IS NULL AND i.item_type = 'file'"
    ).fetchall()
    if not rows:
        return {}, False
    encoder = _get_encoder(model_dir)
    if encoder is None:
        return {}, False
    try:
        import numpy
        q = encoder.encode([query])[0]
    except Exception:
        return {}, False

    scored: list[tuple[float, str]] = []
    for row in rows:
        if not _is_live_searchable(row):
            continue
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
    ranks = {
        item_id: rank for rank, (_s, item_id) in enumerate(scored[:limit], 1)
    }
    return ranks, True


def _rrf(rank_maps: list[dict[str, int]], *, k: int) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranks in rank_maps:
        for item_id, rank in ranks.items():
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))

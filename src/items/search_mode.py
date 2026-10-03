"""Search mode decision: hybrid vs FTS-only.

Task 4 requires hybrid to beat FTS-only on paraphrases without regressing CJK.
When that fails, ship FTS-only and record the decision artifact.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# Default product mode until evaluate_search records a decision.
DEFAULT_MODE = "hybrid"
VALID_MODES = frozenset({"hybrid", "fts"})

_DECISION_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "superpowers"
    / "measurements"
    / "2026-10-03-search-retrieval-decision.json"
)


def resolve_search_mode(explicit: str | None = None) -> str:
    if explicit:
        mode = explicit.strip().lower()
        if mode in ("fts", "fts-only", "fts_only"):
            return "fts"
        if mode == "hybrid":
            return "hybrid"
        raise ValueError(f"unknown search mode: {explicit!r}")
    env = (os.environ.get("GRAPH_AGENT_SEARCH_MODE") or "").strip().lower()
    if env in VALID_MODES:
        return env
    if env in ("fts-only", "fts_only"):
        return "fts"
    decision = load_decision()
    if decision:
        winner = (decision.get("winner") or "").strip().lower()
        if winner in ("fts", "fts-only", "fts_only"):
            return "fts"
        if winner in ("hybrid", "minilm_hybrid", "minilm_hybrid_plus_cjk_fts"):
            return "hybrid"
    return DEFAULT_MODE


def load_decision(path: Path | None = None) -> dict | None:
    target = path or _DECISION_PATH
    if not target.is_file():
        return None
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_decision(payload: dict, path: Path | None = None) -> Path:
    target = path or _DECISION_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target

"""Compose item projections after a scan. No file moves. No cli import."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from types import MappingProxyType

from items.connector import propose_inferred_links
from items.identity import project_after_scan as project_identity
from items.profile_items import mint_declared_items
from items.typing import project_typing


def project_context_graph(
        conn: sqlite3.Connection, sources, scan_state: str, *,
        run_typing: bool = False,
        run_connector: bool = False) -> dict[str, int]:
    """After scan: identity + mint (+ witnessed links). Typing is off by default.

    Call ``project_after_recognition`` once evidence exists.
    """
    project_identity(conn, sources, scan_state)
    minted = mint_declared_items(conn)
    typed = 0
    if run_typing:
        typed = _typing_with_detector(conn)
    inferred = 0
    if run_connector:
        inferred = propose_inferred_links(conn)
    return {
        "minted": minted,
        "typed": typed,
        "inferred": inferred,
    }


def project_after_recognition(conn: sqlite3.Connection) -> dict[str, int]:
    """Typing + inferred connector after extraction/recognition evidence exists."""
    typed = _typing_with_detector(conn)
    inferred = propose_inferred_links(conn)
    return {"typed": typed, "inferred": inferred}


def _handling_policy():
    from facts.domains import SCHEMA_IDS
    from recognition.detector import Handling, SAFETY_DOMAIN_HANDLING
    ordinary = {
        schema_id: Handling(
            handling_class="personal_non_sensitive",
            protected=False,
            basis="detector",
        )
        for schema_id in SCHEMA_IDS
    }
    return MappingProxyType({**ordinary, **SAFETY_DOMAIN_HANDLING})


def _typing_with_detector(conn: sqlite3.Connection) -> int:
    from privacy.classification_store import ClassificationStore
    from questions.store import activated_schemas, declared_lives
    from recognition.detector import Detector
    from recognition.rules import load_rules

    manifest = (
        Path(__file__).resolve().parents[1] / "recognition" / "library"
        / "recognition.json"
    )
    if not manifest.is_file():
        return 0
    rules = load_rules(manifest.read_text)
    from datetime import datetime, timezone
    detector = Detector(
        rules,
        handling_for=_handling_policy(),
        now=lambda: datetime.now(timezone.utc).isoformat(),
        declared_lives=lambda: declared_lives(conn),
        settled_by_user=lambda: activated_schemas(conn),
    )
    store = ClassificationStore(conn)

    def explain(c, file_id, content_hash):
        return detector.explain(c, file_id, content_hash)

    def classify(c, file_id, content_hash):
        current = store.current(file_id, content_hash)
        if current is not None:
            return current
        try:
            return detector(c, file_id, content_hash)
        except Exception:
            return None

    return project_typing(conn, explain=explain, classify=classify)

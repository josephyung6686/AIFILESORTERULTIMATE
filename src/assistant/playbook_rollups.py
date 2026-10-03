"""L2/L3 playbook Markdown rollups from rules + atoms.

L2 clusters: group live atoms/rules by kind under playbook/clusters/
L3 profiles: one summary profile under playbook/profiles/
Never steers filing — human-readable only.
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from assistant.memory_v1 import list_rules
from assistant.memory_v2 import ensure_atoms_schema, live_atoms


def default_playbook_root() -> Path:
    return Path(__file__).resolve().parents[2] / "playbook"


def write_rollups(
        conn: sqlite3.Connection,
        *,
        root: Path | None = None,
) -> dict[str, Any]:
    """Regenerate L2/L3 Markdown. Safe to call repeatedly (overwrite)."""
    root = root or default_playbook_root()
    clusters_dir = root / "clusters"
    profiles_dir = root / "profiles"
    clusters_dir.mkdir(parents=True, exist_ok=True)
    profiles_dir.mkdir(parents=True, exist_ok=True)

    ensure_atoms_schema(conn)
    rules = list_rules(conn)
    atoms = live_atoms(conn)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    by_kind: dict[str, list[str]] = defaultdict(list)
    for r in rules:
        by_kind[r.get("kind") or "rule"].append(r["rule_text"])
    for a in atoms:
        by_kind[a.get("kind") or "atom"].append(
            a.get("claim") or a.get("rule_text") or "")

    written: list[str] = []
    for kind, lines in sorted(by_kind.items()):
        path = clusters_dir / f"{kind}.md"
        body = [
            f"# Cluster: {kind}",
            "",
            f"_Generated {ts}. INDEX only — does not auto-file._",
            "",
        ]
        for i, text in enumerate(lines, 1):
            if text.strip():
                body.append(f"{i}. {text.strip()}")
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        written.append(str(path))

    profile = profiles_dir / "default.md"
    profile_body = [
        "# Profile: default",
        "",
        f"_Generated {ts}._",
        "",
        f"- Active rules: {len(rules)}",
        f"- Live atoms: {len(atoms)}",
        f"- Clusters: {', '.join(sorted(by_kind)) or '(none)'}",
        "",
        "## Rules",
    ]
    for r in rules[:20]:
        profile_body.append(f"- [{r.get('kind')}] {r['rule_text']}")
    if not rules:
        profile_body.append("- (none)")
    profile_body.append("")
    steering = False
    try:
        from assistant.memory_release import release_status
        status = release_status(conn)
        steering = bool(status.get("atoms_steering"))
    except Exception:
        status = {"dark": True, "atoms_steering": False}
    profile_body.append(
        "## Atoms "
        + ("(steering enabled via version-bound release)"
           if steering else
           "(dark — visible INDEX only; not steering until memory release)")
    )
    for a in atoms[:20]:
        profile_body.append(
            f"- {a.get('claim') or a.get('rule_text')} "
            f"(sources={a.get('source_ids')})"
        )
    if not atoms:
        profile_body.append("- (none)")
    profile_body.append("")
    profile.write_text("\n".join(profile_body) + "\n", encoding="utf-8")
    written.append(str(profile))

    return {
        "ok": True,
        "root": str(root),
        "files": written,
        "n_rules": len(rules),
        "n_atoms": len(atoms),
        "atoms_steering": steering,
        "atoms_dark": not steering,
        "moved": False,
    }

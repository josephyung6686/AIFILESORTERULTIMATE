"""Identity runs after scan; typing/connector run after evidence exists."""
from __future__ import annotations

import ast
from pathlib import Path


def test_orchestrator_scan_hook_does_not_type_before_extraction():
    """Typing needs body evidence. Scan-time compose must not enable it."""
    path = Path(__file__).resolve().parents[2] / "src" / "orchestrator.py"
    text = path.read_text(encoding="utf-8")
    # The call site must pass run_typing=False (and connector off) at scan time.
    assert "project_context_graph" in text
    assert "run_typing=False" in text
    assert "run_connector=False" in text


def test_cli_has_post_recognition_projection_hook():
    path = Path(__file__).resolve().parents[2] / "src" / "cli.py"
    text = path.read_text(encoding="utf-8")
    assert "project_after_recognition" in text

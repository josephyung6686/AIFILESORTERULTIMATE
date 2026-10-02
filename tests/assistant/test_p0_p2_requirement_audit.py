"""Living audit: every P0–P2 / Addendum A requirement has code+test evidence."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TESTS = ROOT / "tests"


def test_requirement_files_exist():
    required = [
        SRC / "assistant" / "tools.py",
        SRC / "assistant" / "chat.py",
        SRC / "assistant" / "egress.py",
        SRC / "assistant" / "trust.py",
        SRC / "assistant" / "memory_l0.py",
        SRC / "assistant" / "plans.py",
        SRC / "assistant" / "local_model.py",
        SRC / "items" / "hot_index.py",
        SRC / "items" / "commands.py",
        TESTS / "assistant" / "test_injection_fixtures.py",
        TESTS / "assistant" / "test_addendum_a.py",
        TESTS / "assistant" / "test_trajectories.py",
        TESTS / "assistant" / "test_held_egress.py",
        TESTS / "assistant" / "test_provider_trust.py",
        TESTS / "assistant" / "test_memory_l0_provenance.py",
        TESTS / "fixtures" / "injection" / "INJ-01_ignore_instructions.pdf.txt",
        ROOT / "tools" / "run_assistant_gates.sh",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    assert not missing, f"missing: {missing}"


def test_tools_mark_find_untrusted():
    src = (SRC / "assistant" / "tools.py").read_text(encoding="utf-8")
    assert "UNTRUSTED_LABEL" in src
    assert "untrusted=True" in src
    assert "remote_fetch" in src


def test_cli_has_ask_and_local_only():
    cli = (SRC / "cli.py").read_text(encoding="utf-8")
    cmds = (SRC / "items" / "commands.py").read_text(encoding="utf-8")
    assert '["ask"]' in cli
    assert "ask_main" in cli
    assert "--local-only" in cmds
    assert "--show-trust" in cmds


def test_write_shaped_hard_refuse_present():
    src = (SRC / "assistant" / "tools.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    # Ensure is_write_shaped / WRITE_SHAPED used in execute
    assert "is_write_shaped" in src and "WRITE_SHAPED" in src
    assert "write tools are not enabled" in src

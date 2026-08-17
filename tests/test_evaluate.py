"""Held-out evaluation on already-filed files."""

from __future__ import annotations

from pathlib import Path

from database_agent.evaluate import EvalReport, hold_out, make_synthetic_tree, run_synthetic
from database_agent.nodes import assign_file_to_node, build_profiles, iter_destination_folders


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return path


def test_hold_out_puts_plasmole_file_back(tmp_path: Path) -> None:
    plasmole = tmp_path / "Desktop" / "Work" / "Plasmole"
    files = [
        _touch(plasmole / "plasmole-protocol.md"),
        _touch(plasmole / "plasmole-demo.py"),
        _touch(plasmole / "plasmole-notes.txt"),
    ]
    dests = iter_destination_folders([tmp_path / "Desktop"])
    report = hold_out(dests, files)
    assert report.hits >= 2
    assert report.misses == 0
    held = files[0]
    rest = files[1:]
    profiles = build_profiles(dests, rest)
    from database_agent.classify import classify_loose

    decisions, _ = classify_loose([held], profiles)
    assert decisions[0].dest == assign_file_to_node(held, dests) == plasmole


def test_synthetic_held_out_is_perfect_precision_at_about_62_percent_coverage(
    tmp_path: Path,
) -> None:
    report = run_synthetic(tmp_path)
    assert isinstance(report, EvalReport)
    assert report.misses == 0
    assert report.precision == 1.0
    assert 0.58 <= report.coverage <= 0.66


def test_synthetic_tree_layout_matches_spec(tmp_path: Path) -> None:
    tree = make_synthetic_tree(tmp_path)
    assert (tree.desktop / "Work" / "Plasmole").is_dir()
    assert (tree.desktop / "Courses" / "CS3134").is_dir()
    assert tree.loose_dir.is_dir()
    assert len(tree.filed_files) == 21
    distinctive = [p for p in tree.filed_files if "plasmole-" in p.name or "cs3134-" in p.name]
    assert len(distinctive) >= 8

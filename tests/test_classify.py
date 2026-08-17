"""Classifier: frozen nodes only, abstain on nearest-wrong, propose missing folders."""

from __future__ import annotations

from pathlib import Path

from database_agent.classify import classify_loose
from database_agent.nodes import build_profiles, iter_destination_folders


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return path


def _tree(tmp_path: Path) -> tuple[Path, Path, Path]:
    desktop = tmp_path / "Desktop"
    plasmole = desktop / "Work" / "Plasmole"
    cs3134 = desktop / "Courses" / "CS3134"
    _touch(plasmole / "plasmole-protocol.md")
    _touch(plasmole / "plasmole-demo.py")
    _touch(cs3134 / "cs3134-hw1.pdf")
    _touch(cs3134 / "cs3134-lecture-03.pdf")
    return desktop, plasmole, cs3134


def test_plasmole_file_goes_to_plasmole_not_downloads(tmp_path: Path) -> None:
    desktop, plasmole, _ = _tree(tmp_path)
    loose = _touch(tmp_path / "Downloads" / "plasmole-readme.md")
    dests = iter_destination_folders([desktop])
    filed = [
        plasmole / "plasmole-protocol.md",
        plasmole / "plasmole-demo.py",
        tmp_path / "Desktop" / "Courses" / "CS3134" / "cs3134-hw1.pdf",
        tmp_path / "Desktop" / "Courses" / "CS3134" / "cs3134-lecture-03.pdf",
    ]
    profiles = build_profiles(dests, filed)
    decisions, proposals = classify_loose([loose], profiles)
    assert decisions[0].dest == plasmole
    assert decisions[0].disposition == "match"
    assert not proposals


def test_unmatched_stays_put(tmp_path: Path) -> None:
    desktop, plasmole, cs3134 = _tree(tmp_path)
    loose = _touch(tmp_path / "Downloads" / "random-scan-9921.pdf")
    dests = iter_destination_folders([desktop])
    filed = [
        plasmole / "plasmole-protocol.md",
        plasmole / "plasmole-demo.py",
        cs3134 / "cs3134-hw1.pdf",
        cs3134 / "cs3134-lecture-03.pdf",
    ]
    profiles = build_profiles(dests, filed)
    decisions, _ = classify_loose([loose], profiles)
    assert decisions[0].dest is None
    assert decisions[0].disposition == "skip"


def test_cs3157_does_not_land_in_cs3134(tmp_path: Path) -> None:
    desktop, plasmole, cs3134 = _tree(tmp_path)
    loose = _touch(tmp_path / "Downloads" / "cs3157-hw1.pdf")
    dests = iter_destination_folders([desktop])
    filed = [
        plasmole / "plasmole-protocol.md",
        plasmole / "plasmole-demo.py",
        cs3134 / "cs3134-hw1.pdf",
        cs3134 / "cs3134-hw2.pdf",
        cs3134 / "cs3134-lecture-03.pdf",
    ]
    for path in filed:
        if not path.exists():
            _touch(path)
    profiles = build_profiles(dests, filed)
    decisions, proposals = classify_loose([loose], profiles)
    assert decisions[0].dest is None
    assert decisions[0].disposition == "skip"
    assert cs3134 not in {p.suggested_parent for p in proposals}


def test_two_unknown_cs3157_files_propose_a_folder_not_mkdir(tmp_path: Path) -> None:
    desktop, plasmole, cs3134 = _tree(tmp_path)
    a = _touch(tmp_path / "Downloads" / "cs3157-hw1.pdf")
    b = _touch(tmp_path / "Downloads" / "cs3157-hw2.pdf")
    dests = iter_destination_folders([desktop])
    filed = [
        plasmole / "plasmole-protocol.md",
        plasmole / "plasmole-demo.py",
        cs3134 / "cs3134-hw1.pdf",
        cs3134 / "cs3134-lecture-03.pdf",
    ]
    profiles = build_profiles(dests, filed)
    decisions, proposals = classify_loose([a, b], profiles)
    assert all(d.dest is None for d in decisions)
    assert len(proposals) == 1
    assert proposals[0].label.lower() == "cs3157"
    assert set(proposals[0].example_files) == {a, b}
    assert not proposals[0].created_on_disk
    assert not (tmp_path / "Downloads" / "CS3157").exists()
    assert not (tmp_path / "Desktop" / "CS3157").exists()


def test_one_unknown_compound_does_not_propose(tmp_path: Path) -> None:
    desktop, plasmole, cs3134 = _tree(tmp_path)
    loose = _touch(tmp_path / "Downloads" / "cs3157-hw1.pdf")
    dests = iter_destination_folders([desktop])
    filed = [
        plasmole / "plasmole-protocol.md",
        plasmole / "plasmole-demo.py",
        cs3134 / "cs3134-hw1.pdf",
        cs3134 / "cs3134-lecture-03.pdf",
    ]
    profiles = build_profiles(dests, filed)
    _, proposals = classify_loose([loose], profiles)
    assert proposals == []


def test_cannot_name_a_path_that_is_not_frozen(tmp_path: Path) -> None:
    desktop, plasmole, _ = _tree(tmp_path)
    loose = _touch(tmp_path / "Downloads" / "plasmole-readme.md")
    dests = [plasmole]  # Work exists but is not frozen
    filed = [plasmole / "plasmole-protocol.md", plasmole / "plasmole-demo.py"]
    profiles = build_profiles(dests, filed)
    decisions, _ = classify_loose([loose], profiles)
    assert decisions[0].dest == plasmole
    work = desktop / "Work"
    assert decisions[0].dest != work
    assert work not in profiles

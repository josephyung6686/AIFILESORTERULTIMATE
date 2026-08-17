"""Indexer: destination folders, content profiles, sync/TCC flags."""

from __future__ import annotations

from pathlib import Path

import pytest

from database_agent.nodes import (
    RootInfo,
    assign_file_to_node,
    build_profiles,
    describe_root,
    iter_destination_folders,
    is_dataless,
    is_skipped_destination,
)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")
    return path


def test_work_folder_name_is_not_in_profile(tmp_path: Path) -> None:
    plasmole = tmp_path / "Desktop" / "Work" / "Plasmole"
    _touch(plasmole / "plasmole-protocol.md")
    _touch(plasmole / "enzyme-assay.py")
    work = tmp_path / "Desktop" / "Work"
    dests = iter_destination_folders([tmp_path / "Desktop"])
    profiles = build_profiles(dests, [plasmole / "plasmole-protocol.md", plasmole / "enzyme-assay.py"])

    work_profile = profiles[work]
    plasmole_profile = profiles[plasmole]
    assert "work" not in work_profile.token_counts
    assert "plasmole" in plasmole_profile.token_counts
    assert "enzyme" in plasmole_profile.token_counts
    assert work_profile.file_count == 0
    assert plasmole_profile.file_count == 2


def test_filed_file_trains_deepest_ancestor_only(tmp_path: Path) -> None:
    plasmole = tmp_path / "Desktop" / "Work" / "Plasmole"
    filed = _touch(plasmole / "plasmole-notes.md")
    dests = iter_destination_folders([tmp_path / "Desktop"])
    assert assign_file_to_node(filed, dests) == plasmole
    profiles = build_profiles(dests, [filed])
    assert profiles[tmp_path / "Desktop" / "Work"].file_count == 0
    assert profiles[plasmole].file_count == 1


def test_node_modules_is_not_a_destination(tmp_path: Path) -> None:
    nm = tmp_path / "Desktop" / "Hoyahacks" / "node_modules" / "left-pad"
    _touch(nm / "index.js")
    dests = iter_destination_folders([tmp_path / "Desktop"])
    assert nm not in dests
    assert (tmp_path / "Desktop" / "Hoyahacks" / "node_modules") not in dests
    assert is_skipped_destination(nm)


def test_folder_with_package_json_is_not_a_destination(tmp_path: Path) -> None:
    app = tmp_path / "Desktop" / "Hoyahacks"
    _touch(app / "package.json")
    _touch(app / "src" / "photo.jpg")
    dests = iter_destination_folders([tmp_path / "Desktop"])
    assert app not in dests
    assert (app / "src") not in dests


def test_git_dir_itself_is_skipped_but_parent_need_not_be(tmp_path: Path) -> None:
    repo = tmp_path / "Projects" / "notes"
    _touch(repo / "readme.md")
    (repo / ".git").mkdir()
    dests = iter_destination_folders([tmp_path / "Projects"])
    assert repo in dests
    assert (repo / ".git") not in dests


def test_icloud_placeholder_is_dataless(tmp_path: Path) -> None:
    placeholder = _touch(tmp_path / "Desktop" / "Taxes" / "w2.pdf.icloud")
    assert is_dataless(placeholder)


def test_onedrive_path_is_flagged_cloud_synced(tmp_path: Path) -> None:
    onedrive = tmp_path / "OneDrive" / "Documents"
    onedrive.mkdir(parents=True)
    info = describe_root(onedrive)
    assert info.cloud_synced
    assert "upload" in (info.warning or "").lower()


def test_empty_desktop_named_root_is_access_warning_not_zero_files(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    info = describe_root(desktop)
    assert info.tcc_protected
    assert info.listing_unreliable
    assert info.file_count == 0
    assert "grant" in (info.warning or "").lower()
    assert "0 files found" not in (info.warning or "").lower()


def test_nonempty_desktop_is_not_listed_as_access_failure(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    _touch(desktop / "notes.txt")
    info = describe_root(desktop)
    assert info.tcc_protected
    assert not info.listing_unreliable
    assert info.file_count == 1


def test_describe_root_returns_rootinfo(tmp_path: Path) -> None:
    p = tmp_path / "Projects"
    p.mkdir()
    info = describe_root(p)
    assert isinstance(info, RootInfo)
    assert info.path == p.resolve()

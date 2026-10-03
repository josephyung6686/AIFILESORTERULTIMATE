"""Software projects in the common languages are one item, never sorted.

The judge's Desktop held Xcode, Gradle and plain git projects that no marker
reached, so their asset catalogues and build files were offered folders and
asked questions about as if they were the person's own documents.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scan_agent.exclusion import project_root_markers_in


@pytest.mark.parametrize("name, is_dir", [
    ("Package.swift", False), ("build.gradle", False),
    ("build.gradle.kts", False), ("settings.gradle", False),
    ("settings.gradle.kts", False), ("pom.xml", False),
    ("Cargo.toml", False), ("go.mod", False), ("pyproject.toml", False),
    ("pyvenv.cfg", False),
    ("NavigatorImpaired.xcodeproj", True), ("App.xcworkspace", True),
    ("Tool.sln", False), ("Tool.csproj", False),
    (".git", True), (".git", False),
])
def test_a_common_project_marker_makes_its_folder_a_project(name, is_dir):
    listing = [("README.md", False), (name, is_dir), ("src", True)]
    assert project_root_markers_in(listing), name


@pytest.mark.parametrize("name, is_dir", [
    ("package.json", True),            # a folder, not the manifest
    ("Package.swift", True),
    ("notes.sln.txt", False),
    ("my.git", True),
    ("xcodeproj", True),
])
def test_look_alikes_are_not_markers(name, is_dir):
    assert project_root_markers_in([(name, is_dir)]) == ()


def _desktop(tmp_path: Path) -> Path:
    desk = tmp_path / "Desktop"
    app = desk / "MyApp"
    (app / "MyApp.xcodeproj").mkdir(parents=True)
    (app / "MyApp.xcodeproj" / "project.pbxproj").write_text("// pbx\n")
    icons = app / "MyApp" / "Assets.xcassets" / "AppIcon.appiconset"
    icons.mkdir(parents=True)
    (icons / "Contents.json").write_text('{"images": []}\n')
    (app / "MyApp" / "ContentView.swift").write_text("import SwiftUI\n")
    (desk / "history essay.txt").write_text("The causes of the war.\n")
    return desk


def test_an_xcode_project_is_set_aside_as_one_project(tmp_path):
    from database_agent.db import open_database
    from items.hot_index import find_files
    from items.indexing import index_folder
    from items.schema import create_items_schema

    desk = _desktop(tmp_path)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    counts = index_folder(conn, desk)
    assert counts.set_aside_folders == 1
    assert counts.set_aside >= 1
    live = [r[0] for r in conn.execute(
        "SELECT open_target FROM items WHERE presence = 'live' "
        "AND superseded_by IS NULL AND open_target IS NOT NULL")]
    assert any(t.endswith("history essay.txt") for t in live)
    assert not [t for t in live if "Assets.xcassets" in t
                or "ContentView.swift" in t], live
    for query in ("AppIcon", "Contents", "ContentView"):
        hits = find_files(conn, query, limit=20).hits
        assert not [h for h in hits
                    if "Assets.xcassets" in (h.open_target or "")
                    or "ContentView" in (h.display_label or "")], query
    conn.close()

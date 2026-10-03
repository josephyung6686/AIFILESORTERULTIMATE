"""The greeting's numbers are files, and they add up to what is on disk.

indexed + set aside + protected == every file on disk, where a protected
container (an app) is one thing: it is counted, never opened, so the files
inside it are never listed. Each protected thing says why in plain words.
"""
from __future__ import annotations

import os
from pathlib import Path

from database_agent.db import open_database
from items.indexing import counts, index_folder, protected_reasons


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "notes" / "plan.txt").write_text("a plan", encoding="utf-8")
    project = root / "proj"
    (project / "src" / "deep").mkdir(parents=True)
    (project / "package.json").write_text("{}", encoding="utf-8")
    (project / "src" / "a.js").write_text("x", encoding="utf-8")
    (project / "src" / "b.js").write_text("x", encoding="utf-8")
    (project / "src" / "deep" / "c.js").write_text("x", encoding="utf-8")
    vendored = project / "Vendor" / "Thing.app" / "Contents"
    vendored.mkdir(parents=True)
    (vendored / "Info.plist").write_text("<plist/>", encoding="utf-8")
    (vendored / "Thing").write_text("bin", encoding="utf-8")
    app = root / "Tool.app" / "Contents"
    (app / "MacOS").mkdir(parents=True)
    (app / "Info.plist").write_text("<plist/>", encoding="utf-8")
    (app / "MacOS" / "tool").write_text("bin", encoding="utf-8")
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    (root / "Jo vaccination card_page-0001.jpg").write_bytes(b"\xff\xd8\xff")
    (root / "Jo_HKID.pdf").write_bytes(b"%PDF-1.4")
    return root


def _files_on_disk(root: Path) -> int:
    """Every file, with a protected container standing as one thing."""
    total = 0
    for folder, dirs, files in os.walk(root):
        apps = [d for d in dirs if d.endswith(".app")]
        total += len(files) + len(apps)
        dirs[:] = [d for d in dirs if d not in apps]
    return total


def test_indexed_set_aside_and_protected_add_up_to_the_disk(tmp_path):
    root = _tree(tmp_path)
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    c = index_folder(conn, root)

    # Files inside proj/, not its folders; the app vendored in it is one.
    assert c.set_aside == 5
    assert c.set_aside_folders == 1
    # Tool.app (one thing) + the key + the two personal files.
    assert c.protected == 4
    assert c.indexed == 2                    # the two notes; never a protected one
    assert c.indexed + c.set_aside + c.protected == _files_on_disk(root)
    assert counts(conn) == c


def test_every_protected_thing_says_why(tmp_path):
    root = _tree(tmp_path)
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    c = index_folder(conn, root)

    reasons = {r["name"]: r for r in protected_reasons(conn)}

    assert len(reasons) == c.protected
    assert reasons["Tool.app"]["reason"] == "app or system item"
    assert reasons["id.pem"]["reason"] == "key or password file"
    assert reasons["Jo_HKID.pdf"]["reason"] == "looks like an ID document"
    assert reasons["Jo vaccination card_page-0001.jpg"]["reason"] == \
        "health record"
    assert reasons["id.pem"]["folder"] == str(root)

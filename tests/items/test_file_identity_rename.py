"""Rename-follow via st_dev:st_ino token."""
from __future__ import annotations

from pathlib import Path

from items.file_identity import (
    file_id_token,
    remember_path,
    resolve_renamed,
)
from items.schema import create_items_schema


def test_rename_follow_by_inode(conn, tmp_path: Path):
    create_items_schema(conn)
    src = tmp_path / "old.txt"
    src.write_text("same inode", encoding="utf-8")
    token = file_id_token(src)
    assert token
    remember_path(conn, "item-1", src)
    dst = tmp_path / "new.txt"
    src.rename(dst)
    assert file_id_token(dst) == token
    found = resolve_renamed(conn, "item-1", [dst, tmp_path / "other.txt"])
    assert found == dst

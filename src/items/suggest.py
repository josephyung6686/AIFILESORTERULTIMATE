"""Local suggestions. They are printed. They do not approve a link or move a file.

Delegates to ``items.nudge`` (required pairs from the profile package).
"""
from __future__ import annotations

import sqlite3

from items.nudge import render, warnings
from items.profile_loader import load_profile


def proposals(conn: sqlite3.Connection, *, now: str | None = None,
              profile_name: str = "student") -> list[dict]:
    """Read items and relationships. Write nothing."""
    try:
        profile = load_profile(profile_name)
    except Exception:
        profile = None
    return warnings(conn, profile=profile, now=now)

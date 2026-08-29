# tests/p3/conftest.py
"""Fixtures for P3. P1's root tests/conftest.py supplies `conn` and `sample_file`
and is NOT modified here."""
from pathlib import Path

import pytest


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """A fixture corpus. Every P3 test scans this, never the user's disk."""
    root = tmp_path / "corpus"
    root.mkdir()
    return root


def write(path: Path, data: bytes = b"fixture bytes") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path

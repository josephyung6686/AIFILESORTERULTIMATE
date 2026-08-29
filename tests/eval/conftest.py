# tests/eval/conftest.py
"""P2 fixtures. Deliberately separate from tests/conftest.py, which is P1's."""
from pathlib import Path

import pytest

from database_agent.db import open_database


@pytest.fixture()
def eval_conn(tmp_path: Path):
    """P1's handle (§0: one local database). P2 owns tables inside it."""
    c = open_database(tmp_path / "agent.sqlite")
    yield c
    c.close()

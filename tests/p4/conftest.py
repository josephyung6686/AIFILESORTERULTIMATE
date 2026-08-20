# tests/p4/conftest.py
import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema


@pytest.fixture()
def p4_conn(conn):
    """P1's database with P4's three tables added. `conn` is P1's root fixture and
    `tests/conftest.py` is not modified."""
    create_schema(conn)
    create_evidence_schema(conn)
    return conn

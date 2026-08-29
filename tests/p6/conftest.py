# tests/p6/conftest.py
"""P6's fixtures. P1's `tests/conftest.py` supplies `conn` and is not modified.

Nothing here may be imported across parts by name: under pytest's default prepend
import mode, with no `__init__.py` under `tests/`, every `conftest.py` is imported as
the top-level module `conftest` and the last one wins.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from evidence_shape.schema import create_evidence_schema

from facts.fields import create_fields

#: §8.5 replays a run and compares it against a prior result, so any test that
#: compares two records must be comparing what the resolver produced and not two
#: readings of the wall clock.
FIXED_OBSERVED_AT = "2026-08-19T14:03:22+00:00"


@pytest.fixture()
def observed_at() -> str:
    return FIXED_OBSERVED_AT


@pytest.fixture()
def p6_conn(conn):
    """P1's database with P4's three tables, P6's own tables, and the `fields`
    catalogue loaded — the same shape `tests/p4/conftest.py` builds as `p4_conn`.

    `create_fields` calls `create_facts_schema` itself, so there is no ordering trap
    for a test that only wants the catalogue.
    """
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn

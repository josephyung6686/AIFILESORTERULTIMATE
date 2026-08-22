# tests/p7/conftest.py
"""P7's test fixtures.

`p7_conn` is P1's root `conn` fixture with the substrate P7 reads from added:
P1's own tables, P3's scan tables, P4's evidence tables and P5's extraction
tables. `tests/conftest.py` is not modified — P1 owns it.

P7's own tables arrive with `privacy.schema.create_privacy_schema`, which is the
fifth call below. Everything else in this database belongs to another part and P7
creates none of it.

Nothing in this file may be a name another part's conftest or test helper also
defines: `tests/` carries no `__init__.py`, so pytest puts each test directory on
`sys.path` and two helpers sharing a name are one module. Only P7 fixtures live
here — and `tests/p7/__init__.py` makes this file `p7.conftest` rather than the
top-level module `conftest`, which is what keeps it from displacing `tests/p5`'s
(`tests/p5/test_p5_join.py` imports `RecordingSink` from `conftest` by name, and
`p7` sorts after `p5`).
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema

from scan_agent.schema import create_scan_schema

from evidence_shape.schema import create_evidence_schema

from extractors.schema import create_extraction_schema

from privacy.schema import create_privacy_schema

#: §8.5 requires replay to reproduce a run, and every P7 record carries §8.2's
#: "time of observation". An injectable clock is what makes an equality assertion
#: on a stored record possible at all.
FIXED_CLOCK = "2026-08-22T12:00:00+00:00"


@pytest.fixture()
def p7_conn(conn):
    """P1's database with P3's, P4's and P5's tables added, and then P7's own.

    P7 creates and owns its own tables inside this one database and creates no
    table belonging to another part. Five creators, run in dependency order, were
    verified to coexist: no collision.
    """
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_privacy_schema(conn)
    return conn

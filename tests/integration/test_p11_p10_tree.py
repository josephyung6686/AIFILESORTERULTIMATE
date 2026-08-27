"""G-P10: the live frozen-tree read, against P10's own `frozen_tree`.

The gate is not skipped and no source stub satisfies it: a stub would be P11
deciding what a frozen node is, which is the one thing SPEC:102 says P11 does not
own. While `tree_design.freeze` is absent the test reports an explicit `xfail`
naming the missing module -- the gap is in the run report, not hidden -- and the
moment P10 publishes `frozen_tree` the body executes for real and must pass.

`tree_design.records` already ships, and `tests/p11/p10_fixtures.py` imports
`Node`, `ExpectedValue` and `TemplateContext` from it rather than mirroring them,
so the half of the seam that exists is already live-tested by every P11 index test.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from placement.index import build_destination_index, legal_node_ids
from placement.schema import create_placement_schema
from p11.conftest import FIXED_CLOCK


@pytest.fixture()
def p11_conn(conn):
    # `tests/p11/conftest.py` is not on this directory's fixture path, so the
    # database is built here the way every other integration test builds its own
    # (`tests/integration/test_p9_p8_group_seam.py`).
    create_schema(conn)
    create_placement_schema(conn)
    return conn


def test_p11_indexes_p10s_live_frozen_tree(p11_conn):
    try:
        from tree_design.freeze import frozen_tree
    except ModuleNotFoundError as absent:  # G-P10
        pytest.xfail(f"G-P10 open: {absent}")

    tree = frozen_tree(p11_conn, plan_version="plan-1")
    entries = build_destination_index(
        p11_conn, tree, component_version="P11-integration",
        observed_at=FIXED_CLOCK,
    )
    assert entries
    assert all(entry.plan_version == "plan-1" for entry in entries)
    # ONE legality authority: P10's freeze record decides, P11's index projects.
    assert legal_node_ids(p11_conn, plan_version="plan-1") == frozenset(
        tree.freeze_record.legal_destination_ids)


def test_no_placement_module_imports_p11s_test_only_tree_fixture():
    # A source stub for P10 would make G-P10 unfalsifiable.
    import pathlib

    source = pathlib.Path(__file__).resolve().parents[2] / "src" / "placement"
    for module in source.glob("*.py"):
        assert "p10_fixtures" not in module.read_text(), module

"""A real P1 database carrying P7's, P10's and P11's tables and P12's own.

No mock and no in-memory stand-in. P12's refusals are reads of a real frozen tree
and a real classification row, and a test against an absent table would prove
nothing about refusing because a node is illegal rather than because a table is
missing. This mirrors `tests/p11/conftest.py`, which states the same reason.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from database_agent.db import create_schema
from eval_harness.store import create_eval_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema
from tree_design.fixtures import store_fixture_tree

from mutation.schema import create_mutation_schema

FIXED_CLOCK = "2026-08-29T00:00:00Z"


@pytest.fixture()
def p12_conn(conn):
    create_schema(conn)
    create_eval_schema(conn)
    create_privacy_schema(conn)
    create_placement_schema(conn)
    create_mutation_schema(conn)
    return conn


@pytest.fixture()
def frozen(p12_conn):
    """P10's stored fixture tree, frozen. P12 resolves against a real one."""
    return store_fixture_tree(p12_conn)


@pytest.fixture()
def fixture_root(tmp_path: Path) -> Path:
    """The one real directory P12's tests are allowed to mutate.

    Execution runs only against a real root, which in test is a fixture root
    (SPEC, Contract in -> From P2). Everything P12 writes goes beneath this.
    """
    root = tmp_path / "fixture_root"
    root.mkdir()
    return root


@pytest.fixture()
def clock():
    """A monotonic fixed clock. P12 takes `now` as an injected callable with no
    default, so no test depends on wall time and no record is stamped by chance."""
    ticks = iter(f"2026-08-29T00:{minute:02d}:00Z" for minute in range(60))
    return lambda: next(ticks)


@pytest.fixture()
def case_insensitive_root(fixture_root: Path) -> bool:
    """Whether the real fixture volume folds case. macOS APFS usually does; a
    Linux CI runner usually does not. Tests that need a specific answer build a
    `FilesystemConstraints` that STATES it rather than reading the volume, which
    is the whole reason resolution is evaluated against constraints and not
    against the machine the suite happens to run on."""
    probe = fixture_root / "CaseProbe"
    probe.mkdir()
    folded = (fixture_root / "caseprobe").exists()
    os.rmdir(probe)
    return folded

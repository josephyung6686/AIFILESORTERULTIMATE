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


# ---------------------------------------------------------------------------
# Wave D. The shared build blocks: a §1.1 folder landscape, a two-node tree, an
# id minter, and the two constraint tables. They live here rather than in each
# suite because Waves D, E and F all start from the same plan, and a fixture
# copied into five files is five things to keep in step.
# ---------------------------------------------------------------------------

import dataclasses
import itertools

from tree_design.records import Node

from mutation.constraints import FilesystemConstraints

#: A case-KEEPING volume. The default for every suite that is not about case.
CONSTRAINTS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
    max_path_bytes=4096, prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

#: The same volume with case folding on. `Resume.pdf` and `resume.pdf` are one
#: path here and two above, which is Done-means 7's whole content.
FOLDING_CONSTRAINTS = dataclasses.replace(CONSTRAINTS, case_sensitive=False)

#: The composition root names these; `src/mutation/` has no default (A7). P7 is
#: explicit that a neighbour consumes the `protected` flag rather than inferring
#: it from the class, and `Node` carries a class and no flag.
PROTECTED_CLASSES = frozenset({
    "sensitive_personal", "highly_sensitive_credential_bearing"})


def fixture_node(node_id, label, parent, **kwargs):
    base = dict(
        node_id=node_id, plan_version_id="plan-1", node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(), explanation="fixture node",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id)
    base.update(kwargs)
    return Node(**base)


FIXTURE_NODES = (fixture_node("n-course", "Coursework", None),
                 fixture_node("n-phys", "PHYS1401", "n-course"))

LEGAL_DESTINATIONS = frozenset({"n-course", "n-phys"})


@pytest.fixture()
def landscape(fixture_root: Path):
    """§1.1's high-level folder landscape, as two real directories."""
    folders = {"root_documents": fixture_root / "Documents",
               "root_downloads": fixture_root / "Downloads"}
    for folder in folders.values():
        folder.mkdir()
    return folders


@pytest.fixture()
def ids():
    """A monotonic id minter. P12 mints no id itself; every one is injected."""
    counter = itertools.count()
    return lambda: f"id-{next(counter)}"

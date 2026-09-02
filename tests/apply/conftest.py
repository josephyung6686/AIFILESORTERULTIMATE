"""A real corpus with real bytes, a real database, and four real decisions.

Nothing here is mocked. The gesture under test moves a person's files, so a
fixture that stood in for the filesystem would prove nothing about the one thing
that matters. This mirrors `tests/p12/conftest.py` and the walking skeleton
(`tests/integration/test_p12_walking_skeleton.py`), which state the same reason.

The world is deliberately awkward in the three ways a real one is: two branches
that do not share a parent, a branch three deep so that naming a node is not the
same as naming a top-level area, and one protected file among the ordinary ones.
"""
from __future__ import annotations

import dataclasses
import itertools
from pathlib import Path

import pytest
from database_agent.db import create_schema
from database_agent.files_table import record_file
from eval_harness.store import create_eval_schema
from grouping.schema import create_grouping_schema
from placement.fixtures import EXACT_PLACEMENT
from placement.records import Destination, PrivacyState, Subject
from placement.schema import create_placement_schema
from placement.vocabulary import AUTO_ELIGIBLE, ORDINARY, REVIEW_REQUIRED
from privacy.classification_store import ClassificationRecord, ClassificationStore
from privacy.schema import create_privacy_schema
from tree_design.records import Node

from mutation import vocabulary as v
from mutation.constraints import FilesystemConstraints
from mutation.schema import create_mutation_schema

PLAN_VERSION = "plan-under-test"

#: The composition root's answers, stated here because this test file IS one.
#: `src/apply_run/` holds none of them, for the same reason `src/mutation/` does
#: not: they are the numbers and sentences `src/cli.py` owns.
CONSTRAINTS = FilesystemConstraints(
    unicode_form="NFC", case_sensitive=True, max_component_bytes=255,
    max_path_bytes=4096, prohibited_characters=frozenset(),
    reserved_names=frozenset(), replacement_character="_")

PROTECTED_CLASSES = frozenset(
    {"sensitive_personal", "highly_sensitive_credential_bearing"})


def _node(node_id, label, parent):
    return Node(
        node_id=node_id, plan_version_id=PLAN_VERSION, node_type="proposed",
        display_label=label, parent_node_id=parent,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="fixture", node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id)


NODES = (
    _node("n-course", "Coursework", None),
    _node("n-phys", "PHYS1401", "n-course"),
    _node("n-hw", "Homework", "n-phys"),
    _node("n-read", "Reading Inbox", None),
)
LEGAL = frozenset(node.node_id for node in NODES)

#: What each file is, where it starts, where it is meant to end up, and whether
#: P7 marked it. One row per file so the world reads at a glance.
CORPUS = (
    ("Syllabus.pdf", b"PHYS1401 syllabus", "n-phys", False),
    ("Homework 3.pdf", b"problem 1: a block on a ramp", "n-hw", False),
    ("saved article.pdf", b"an article saved to read later", "n-read", False),
    ("passport scan.pdf", b"passport number redacted", "n-phys", True),
)


@pytest.fixture()
def world(conn, tmp_path):
    """The database, the folders, the bytes, and the four decisions."""
    # P9's tables are here because `freeze` now reads them: it joins the
    # provenance of every node's NAME before composing a path, and a read against
    # an absent table proves nothing about the read (`94` F1, and P11's conftest
    # gives the same reason for creating P9's).
    for create in (create_schema, create_eval_schema, create_privacy_schema,
                   create_placement_schema, create_mutation_schema,
                   create_grouping_schema):
        create(conn)

    documents = tmp_path / "Documents"
    inbox = documents / "Inbox"
    inbox.mkdir(parents=True)

    decisions, sources = [], {}
    for index, (filename, body, node_id, protected) in enumerate(CORPUS):
        source = inbox / filename
        source.write_bytes(body)
        stat = source.stat()
        file_id = record_file(
            conn, source, filename=filename,
            normalized_filename=filename.lower(), extension=".pdf",
            observed_size=stat.st_size,
            observed_timestamps=str(stat.st_mtime),
            parent_folder_context="Inbox", mime_type="application/pdf",
            detected_format="pdf", scan_state="included", materialized=True)
        content_hash = conn.execute(
            "SELECT content_hash FROM files WHERE file_id = ?",
            (file_id,)).fetchone()[0]
        handling = ("highly_sensitive_credential_bearing" if protected
                    else "personal_non_sensitive")
        ClassificationStore(conn).write(ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling, protected=protected, basis="user",
            evidence_refs=(), reliability_state="direct",
            observed_at="2026-09-02T00:00:00Z"))
        decisions.append(dataclasses.replace(
            EXACT_PLACEMENT,
            decision_id=f"decision-{index}", plan_version=PLAN_VERSION,
            destination=Destination(node_id=node_id, node_role=ORDINARY),
            subject=Subject(kind="file", file_id=file_id,
                            content_hash=content_hash, group_id=None,
                            member_file_ids=()),
            # The passport is marked and still carries an ordinary review
            # policy, so what stops it is §8.4's protection gate and not a
            # review queue. That is the harder case and the one the standing
            # rule is about.
            privacy=PrivacyState(handling_class=handling, protected=protected,
                                 model_eligibility="local_only",
                                 consent_audit_ref=None),
            review_policy=AUTO_ELIGIBLE))
        sources[file_id] = source

    return _World(conn=conn, root=tmp_path, documents=documents, inbox=inbox,
                  decisions=tuple(decisions), sources=sources)


@dataclasses.dataclass(frozen=True)
class _World:
    conn: object
    root: Path
    documents: Path
    inbox: Path
    decisions: tuple
    sources: dict


@pytest.fixture()
def review_required(world):
    """The same world with the article waiting on an approval nobody collects."""
    return tuple(
        dataclasses.replace(d, review_policy=REVIEW_REQUIRED)
        if d.destination.node_id == "n-read" else d
        for d in world.decisions)


@pytest.fixture()
def ids():
    counter = itertools.count()
    return lambda: f"id-{next(counter)}"


@pytest.fixture()
def clock():
    minutes = itertools.count()
    return lambda: f"2026-09-02T00:{next(minutes):02d}:00Z"


#: `74` §8 Q3 is open, so no suffix format exists to spell. The collision
#: behaviour a plan carries is `stop_and_ask`, which is one of `00`:172's own
#: four and needs no suffix, and this is what proves the other three were not
#: quietly reached: if a collision ever routes here the test fails loudly rather
#: than inventing " (1)".
def no_suffix(stem: str, attempt: int) -> str:
    raise AssertionError(
        "`74` §8 Q3 is unruled: no deterministic suffix format has been chosen, "
        "so nothing may compose one")


COLLISION_POLICY = v.STOP_AND_ASK

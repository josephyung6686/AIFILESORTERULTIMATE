"""`104` §18.111: `measure.py` reads one plan version's tree, never several at once.

`tree_nodes` is keyed `(plan_version_id, node_id)` and node ids are minted per
version, so a sort database that has been run six times holds six trees whose
node ids collide. A node map keyed on `node_id` alone takes whichever version's
row was read last, its parent links cross between trees, and every number derived
from it -- destination chains, node count, built depth, placeable paths -- is a
number about no tree that exists.

The version is not guessed inside the measurement. §18.111 records the guess that
was tried (latest `created_at`, tie broken on the id as a STRING, so `_4` beat
`_16`) and reverted. The caller that knows which plan it is measuring passes it;
a database holding exactly one tree needs no word, because one is not a choice;
a database holding several and a caller that names none is REFUSED, because a
measurement that silently picks the wrong tree is worse than one that says it
cannot tell.

Synthetic database, the product's own DDL, nothing under `.groundtruth/`, no
model. The two versions here share every node id on purpose: that is the
collision the defect needs, and a fixture with disjoint ids would pass under the
defect and prove nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hashlib
import json
import sqlite3

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from extractors.router import ROUTING_DDL
from facts.schema import create_facts_schema
from llm_harness.schema import create_llm_schema
from placement.schema import create_placement_schema
from privacy.schema import create_privacy_schema
from questions.schema import create_questions_schema
from scan_agent.exclusion import EXCLUSION_DDL
from tree_design.schema import create_tree_schema

from tools.groundtruth.measure import (
    AmbiguousPlanVersion, UnknownPlanVersion, observe_run,
)

SITUATION = "academic.coursework"
CLOCK = "2026-09-18T00:00:00Z"
OLDER, NEWER = "plan-a", "plan-b"

#: The same three node ids in both versions, with different labels and a fourth
#: node only the newer tree has. Under node-id keying the newer rows overwrite
#: the older, so the older version's file walks the newer tree's labels.
FIRST = "plan-0"
TREES = {
    FIRST: {"n-root": ("Draft", None)},
    OLDER: {"n-root": ("Coursework", None), "n-a": ("PHYS1403", "n-root"),
            "n-leaf": ("homework", "n-a")},
    NEWER: {"n-root": ("Everything", None), "n-a": ("Loose", "n-root"),
            "n-leaf": ("screenshots", "n-a"), "n-extra": ("Review", "n-root")},
}
FILES = {"Coursework/PHYS 1403 homework 2.txt": ("f1", OLDER),
         "Loose/shot.png": ("f2", NEWER)}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    for create in (create_schema, create_evidence_schema, create_facts_schema,
                   create_privacy_schema, create_placement_schema,
                   create_tree_schema, create_questions_schema, create_llm_schema):
        create(conn)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(ROUTING_DDL)
    return conn


def _tree(conn, version: str, nodes, state: str) -> None:
    # One `created_at` for every version, as the product writes them: a run
    # mints its chain of drafts and its frozen plan in one clock reading.
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) "
        "VALUES (?, NULL, ?, ?, 0, 'sel-1')", (version, state, CLOCK))
    for node_id, (label, parent) in nodes.items():
        conn.execute(
            "INSERT INTO tree_nodes (node_id, plan_version_id, origin_node_id, "
            "node_type, display_label, parent_node_id, root_anchor, ordinal, "
            "associated_group_ids, explanation, node_role, accepts_placement, "
            "handling_class) "
            "VALUES (?, ?, ?, 'folder', ?, ?, 'anchor', 0, '[]', '', 'ordinary', 1, "
            "'personal_non_sensitive')",
            (node_id, version, node_id, label, parent))


def _file(conn, corpus: Path, relative: str, file_id: str, version: str) -> None:
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, directory_position, volume_id, content_hash, hash_algorithm, "
        "observed_size, observed_timestamps, mime_type, detected_format, scan_state, "
        "extraction_status_by_tier, sensitivity_state) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sha256', 0, '{}', 'text/plain', 'text', "
        "'included', '{}', 'unknown')",
        (file_id, str(corpus / relative), Path(relative).name,
         Path(relative).name.casefold(), Path(relative).suffix, "0", "vol-1",
         _hash(file_id)))
    conn.execute(
        "INSERT INTO placement_decisions (record_id, subject_ref, plan_version, "
        "origin_stage, outcome, node_id, created_at, payload) "
        "VALUES (?, ?, ?, 'placement', 'place', 'n-leaf', ?, ?)",
        (f"d-{file_id}", f"file:{file_id}:{_hash(file_id)}", version, CLOCK,
         json.dumps({"ask": None})))


def _build(base: Path, versions: dict[str, str]) -> tuple[Path, Path]:
    """`versions` maps each plan version present to its `plan_versions.state`."""
    corpus = base / "corpus"
    for relative in FILES:
        (corpus / relative).parent.mkdir(parents=True, exist_ok=True)
        (corpus / relative).write_text("", encoding="utf-8")
    database = base / "run.sqlite"
    conn = _connect(database)
    for version, state in versions.items():
        _tree(conn, version, TREES[version], state)
    for relative, (file_id, version) in FILES.items():
        if version in versions:
            _file(conn, corpus, relative, file_id, version)
    conn.commit()
    conn.close()
    return database, corpus


@pytest.fixture(scope="module")
def two_trees(tmp_path_factory):
    """Two FROZEN plans: two runs over one database, neither superseding the
    other (`tree_design/store.py` writes `frozen` and never `superseded`)."""
    return _build(tmp_path_factory.mktemp("two_trees"),
                  {OLDER: "frozen", NEWER: "frozen"})


@pytest.fixture(scope="module")
def one_tree(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("one_tree"), {OLDER: "frozen"})


@pytest.fixture(scope="module")
def one_run(tmp_path_factory):
    """What ONE run writes: a chain of drafts and the plan it froze and placed
    into -- three versions, one `created_at`. A draft carries a stray decision
    here so the test can see it is not counted as the frozen tree's."""
    return _build(tmp_path_factory.mktemp("one_run"),
                  {FIRST: "draft", OLDER: "draft", NEWER: "frozen"})


def test_a_files_chain_is_walked_inside_the_named_version_and_no_other(two_trees):
    """SABOTAGE: key the node map on `node_id` alone. The newer version's rows
    overwrite the older's, and the older version's file reads
    `Everything / Loose / screenshots` -- a chain in a tree it was never placed in."""
    database, corpus = two_trees
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                      plan_version_id=OLDER)
    older = run.files["Coursework/PHYS 1403 homework 2.txt"]
    assert older.destination == ("Coursework", "PHYS1403", "homework")
    assert older.outcome == "place"
    # A decision recorded in ANOTHER version is not this tree's decision: the
    # file is observed (it is in the corpus) but has no outcome in this plan.
    newer = run.files["Loose/shot.png"]
    assert newer.outcome is None
    assert newer.destination == ()


def test_the_tree_wide_numbers_are_one_versions_not_the_union(two_trees):
    """SABOTAGE: count and walk every `tree_nodes` row. `node_count` becomes 7
    (the union over both versions is 3 + 4) and `node_paths` mixes the two trees."""
    database, corpus = two_trees
    older = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                        plan_version_id=OLDER)
    assert older.node_count == 3
    assert older.built_depth == 2
    assert older.node_paths == (("Coursework",), ("Coursework", "PHYS1403"),
                                ("Coursework", "PHYS1403", "homework"))
    newer = observe_run(database, corpus, situation=SITUATION, label="Everything",
                        plan_version_id=NEWER)
    assert newer.node_count == 4
    assert ("Everything", "Review") in newer.node_paths
    assert not any(chain[0] == "Coursework" for chain in newer.node_paths)


def test_several_versions_and_no_word_from_the_caller_is_refused_not_picked(two_trees):
    """SABOTAGE: pick the latest `created_at`, or the greatest id -- §18.111's own
    failed fix. Both versions here share one `created_at`, as the owner's six do."""
    database, corpus = two_trees
    with pytest.raises(AmbiguousPlanVersion) as refused:
        observe_run(database, corpus, situation=SITUATION, label="Coursework")
    message = str(refused.value)
    assert OLDER in message and NEWER in message
    assert "plan_version_id" in message


def test_the_plan_the_product_froze_is_the_tree_when_the_caller_says_nothing(one_run):
    """The product's own record, not a guess: `plan_versions.state = 'frozen'` is
    the plan the run committed to and placed into. SABOTAGE: latest `created_at`
    (all three share one) or the greatest id as a string (`plan-b` < `plan-0`?
    depends on the spelling -- which is the point)."""
    database, corpus = one_run
    run = observe_run(database, corpus, situation=SITUATION, label="Everything")
    assert run.plan_version == NEWER
    assert run.node_count == 4
    assert (run.files["Loose/shot.png"].destination
            == ("Everything", "Loose", "screenshots"))
    # The draft's stray decision is not the frozen tree's.
    assert run.files["Coursework/PHYS 1403 homework 2.txt"].outcome is None
    # The caller's word still wins over the product's record.
    draft = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                        plan_version_id=OLDER)
    assert draft.plan_version == OLDER and draft.node_count == 3


def test_a_version_the_database_does_not_hold_is_refused_by_name(two_trees):
    database, corpus = two_trees
    with pytest.raises(UnknownPlanVersion) as refused:
        observe_run(database, corpus, situation=SITUATION, label="Coursework",
                    plan_version_id="plan-z")
    assert "plan-z" in str(refused.value)
    assert OLDER in str(refused.value) and NEWER in str(refused.value)


def test_one_tree_needs_no_word_because_one_is_not_a_choice(one_tree):
    """Every existing caller measures a database `run.py` unlinked before the run,
    so it holds one tree; naming it would be ceremony. Naming it anyway is fine."""
    database, corpus = one_tree
    unnamed = observe_run(database, corpus, situation=SITUATION, label="Coursework")
    named = observe_run(database, corpus, situation=SITUATION, label="Coursework",
                        plan_version_id=OLDER)
    assert unnamed.node_count == named.node_count == 3
    assert unnamed.node_paths == named.node_paths
    assert (unnamed.files["Coursework/PHYS 1403 homework 2.txt"].destination
            == ("Coursework", "PHYS1403", "homework"))


def test_a_database_with_no_tree_at_all_is_measured_as_empty_not_refused(tmp_path):
    """`tree_nodes` empty is a run that stopped before the tree, which the scorecard
    reports as zero folders -- not a version question, and not an error."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    database = tmp_path / "run.sqlite"
    conn = _connect(database)
    conn.commit()
    conn.close()
    run = observe_run(database, corpus, situation=SITUATION, label="Coursework")
    assert run.node_count == 0
    assert run.node_paths == ()

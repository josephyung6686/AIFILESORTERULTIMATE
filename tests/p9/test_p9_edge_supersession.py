# tests/p9/test_p9_edge_supersession.py
"""R-67: a re-run re-derives an edge under a new address, and only one stays live.

`_edge_id` hashes the bridge entity, so `104` R-61's change -- from the neighbour's
`detail` to its `bridge_entity` -- gives the same logical edge a different content
address. `record_edges` inserts by that address with `INSERT OR IGNORE`, so a re-run
after the change ADDED the newly addressed edge beside the old one and both stayed
live: the same pair of files related twice, with nothing saying which relation the
product currently holds, and an edge count that grows with every run.

`00`:136-153 decides it, and against deletion: *"The product must never overwrite the
evidence record merely because a later extractor or model produces a different
answer. A newer result should supersede an earlier result while retaining the old
observation and the reason it was superseded."* The table already agreed -- its
delete trigger reads "an edge is superseded, never removed" -- so the old row keeps
its place and gains a forward pointer, and the reader stops returning it.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from grouping.records import TypedEdge  # noqa: E402
from grouping.vocabulary import (  # noqa: E402
    DUPLICATE, SHARED_VALIDATED_FACT,
)
from grouping.schema import create_grouping_schema  # noqa: E402
from grouping.store import edges_for_group, record_edges  # noqa: E402

T0 = "2026-09-06T00:00:00+00:00"
T1 = "2026-09-06T01:00:00+00:00"


@pytest.fixture()
def store(conn):
    create_grouping_schema(conn)
    return conn


def _edge(edge_id: str, *, bridge: str | None, created_at: str = T0) -> TypedEdge:
    """One relation between one pair, addressed by whatever the bridge was."""
    return TypedEdge(
        edge_id=edge_id, from_file_id="file-a", to_file_id="file-b",
        edge_type=SHARED_VALIDATED_FACT, evidence_ref="sha256:" + "a" * 64, weight=None,
        bridge_entity_ref=bridge, hub_suppressed=False, created_at=created_at)


def test_a_rerun_under_a_new_address_leaves_exactly_one_live_edge(store):
    """THE DEFECT, REPRODUCED AND FIXED. Before R-61 the bridge was the neighbour's
    `detail`; after it, its `bridge_entity`. Same two files, same kind, two
    addresses -- and the run after the change must not leave the corpus saying these
    files are related twice."""
    record_edges(store, "group-1", [_edge("edge-old", bridge="a detail string")],
                 created_at=T0)
    record_edges(store, "group-1", [_edge("edge-new", bridge="PHYS1401",
                                          created_at=T1)], created_at=T1)

    live = edges_for_group(store, "group-1")

    assert [edge.edge_id for edge in live] == ["edge-new"]
    assert len({(edge.from_file_id, edge.to_file_id, edge.edge_type)
                for edge in live}) == 1


def test_the_superseded_edge_is_kept_and_says_why(store):
    """Kept, never removed. `00`:136-153 wants the earlier record readable AND the
    reason it stopped being the answer; a row that vanished would leave a replay
    unable to explain why an edge it once drew is gone."""
    record_edges(store, "group-1", [_edge("edge-old", bridge="a detail string")],
                 created_at=T0)
    record_edges(store, "group-1", [_edge("edge-new", bridge="PHYS1401")],
                 created_at=T1)

    rows = {row["edge_id"]: row for row in store.execute(
        "SELECT edge_id, superseded_by, supersede_reason FROM group_edges")}

    assert set(rows) == {"edge-old", "edge-new"}, "the old row is still there"
    assert rows["edge-old"]["superseded_by"] == "edge-new"
    assert "different content address" in rows["edge-old"]["supersede_reason"]
    assert rows["edge-new"]["superseded_by"] is None


def test_the_history_is_readable_by_a_caller_that_asks_for_it(store):
    """The other half of what §8.2 keeps the row for. The default is the ANSWER;
    the history is available and never the default."""
    record_edges(store, "group-1", [_edge("edge-old", bridge="a detail string")],
                 created_at=T0)
    record_edges(store, "group-1", [_edge("edge-new", bridge="PHYS1401")],
                 created_at=T1)

    everything = edges_for_group(store, "group-1", include_superseded=True)

    assert [edge.edge_id for edge in everything] == ["edge-old", "edge-new"]
    assert everything[0].superseded_by == "edge-new"


def test_an_unchanged_rerun_supersedes_nothing_and_adds_nothing(store):
    """The ordinary replay, which must stay a no-op. A content-derived address
    re-derives identically over unchanged evidence, so there is no second row to
    supersede and no event to append twice."""
    record_edges(store, "group-1", [_edge("edge-1", bridge="PHYS1401")],
                 created_at=T0)
    record_edges(store, "group-1", [_edge("edge-1", bridge="PHYS1401")],
                 created_at=T1)

    live = edges_for_group(store, "group-1")
    rows = store.execute("SELECT count(*) FROM group_edges").fetchone()[0]
    events = store.execute(
        "SELECT count(*) FROM events WHERE event_type = 'graph-edge creation'"
    ).fetchone()[0]

    assert [edge.edge_id for edge in live] == ["edge-1"]
    assert rows == 1
    assert events == 1, "one edge, created once, however many times it is re-derived"


def test_a_different_pair_is_untouched(store):
    """Superseded on the pair AND the kind. An edge about other files is a
    different statement about the corpus and keeps its own life."""
    record_edges(store, "group-1", [
        _edge("edge-old", bridge="a detail string"),
        TypedEdge(edge_id="edge-other", from_file_id="file-a",
                  to_file_id="file-c", edge_type=SHARED_VALIDATED_FACT,
                  evidence_ref="sha256:" + "b" * 64, weight=None,
                  bridge_entity_ref="ECON2105", hub_suppressed=False,
                  created_at=T0),
    ], created_at=T0)
    record_edges(store, "group-1", [_edge("edge-new", bridge="PHYS1401")],
                 created_at=T1)

    live = {edge.edge_id for edge in edges_for_group(store, "group-1")}

    assert live == {"edge-new", "edge-other"}


def test_a_different_kind_between_the_same_pair_is_untouched(store):
    """Two files can be related in more than one way at once -- a duplicate AND a
    shared fact -- and neither supersedes the other."""
    record_edges(store, "group-1", [
        _edge("edge-shared", bridge="PHYS1401"),
        TypedEdge(edge_id="edge-dup", from_file_id="file-a", to_file_id="file-b",
                  edge_type=DUPLICATE, evidence_ref="sha256:" + "c" * 64,
                  weight=None, bridge_entity_ref=None, hub_suppressed=False,
                  created_at=T0),
    ], created_at=T0)
    record_edges(store, "group-1", [_edge("edge-shared-2", bridge="PHYS 1401")],
                 created_at=T1)

    live = {edge.edge_id for edge in edges_for_group(store, "group-1")}

    assert live == {"edge-shared-2", "edge-dup"}


def test_the_first_reason_sticks_across_a_third_run(store):
    """§8.2's rule everywhere else in this product: a supersede_reason already
    recorded is never rewritten. A third derivation supersedes what is still live
    and leaves the already-superseded row's account alone."""
    record_edges(store, "group-1", [_edge("edge-1", bridge="one")], created_at=T0)
    record_edges(store, "group-1", [_edge("edge-2", bridge="two")], created_at=T1)
    first_reason = store.execute(
        "SELECT supersede_reason FROM group_edges WHERE edge_id = 'edge-1'"
    ).fetchone()[0]

    record_edges(store, "group-1", [_edge("edge-3", bridge="three")], created_at=T1)

    rows = {row["edge_id"]: row for row in store.execute(
        "SELECT edge_id, superseded_by, supersede_reason FROM group_edges")}

    assert rows["edge-1"]["superseded_by"] == "edge-2", "not re-pointed at edge-3"
    assert rows["edge-1"]["supersede_reason"] == first_reason
    assert rows["edge-2"]["superseded_by"] == "edge-3"
    assert rows["edge-3"]["superseded_by"] is None
    assert [edge.edge_id for edge in edges_for_group(store, "group-1")] == ["edge-3"]

# tests/p3/test_p3_selection.py
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.schema import create_scan_schema
from scan_agent.selection import (
    SELECTION_COLUMNS, get_selection, record_selection, selection_candidate_roots,
    selection_sources,
)


@pytest.fixture()
def schema(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_a_selection_carries_exactly_1_1s_three_choices(schema, tmp_path: Path):
    selection_id = record_selection(
        schema,
        sources=[tmp_path / "Downloads"],
        candidate_roots=[tmp_path / "Documents"],
        cross_folder_moves=True,
        selected_by="user-1",
    )
    row = get_selection(schema, selection_id)
    assert selection_sources(schema, selection_id) == [tmp_path / "Downloads"]
    assert selection_candidate_roots(schema, selection_id) == [tmp_path / "Documents"]
    assert row["cross_folder_moves"] == 1
    assert row["selected_at"]
    assert row["selected_by"] == "user-1"


def test_all_three_selections_are_required_with_no_default(schema, tmp_path: Path):
    # §1.1 assigns the choice to the user. P3 has no source set and no root set
    # until one is supplied, and derives neither from the machine's layout.
    with pytest.raises(TypeError):
        record_selection(schema, sources=[tmp_path], candidate_roots=[])
    with pytest.raises(TypeError):
        record_selection(schema, sources=[tmp_path], cross_folder_moves=False,
                         selected_by=None)


def test_selected_by_is_nullable_and_is_a_correct_value_when_empty(schema, tmp_path: Path):
    # MINOR 10 / P1 OQ14: user identity is recorded "when there is an explicit user
    # action". An R1 not authored by a user leaves the field empty, and empty is a
    # correct value rather than a missing one.
    selection_id = record_selection(
        schema, sources=[tmp_path], candidate_roots=[], cross_folder_moves=False,
        selected_by=None,
    )
    assert get_selection(schema, selection_id)["selected_by"] is None


def test_selecting_a_root_produces_no_move_authorization(schema, tmp_path: Path):
    # Done-means 12, and §1.1: "roots are context for the proposal canvas, not
    # permission to move files." Tested as the negative it is.
    record_selection(schema, sources=[], candidate_roots=[tmp_path / "Desktop"],
                     cross_folder_moves=True, selected_by=None)
    columns = [r["name"] for r in schema.execute("PRAGMA table_info(corpus_selections)")]
    for forbidden in ("destination", "placement", "permission", "authorized",
                      "target_node", "approved"):
        assert not any(forbidden in c.lower() for c in columns), forbidden

    import scan_agent.selection as module
    for name in vars(module):
        assert not any(t in name.lower() for t in ("authorize", "permit", "destination",
                                                   "placement"))


def test_the_selection_record_carries_r1s_fields_and_no_others(schema):
    assert SELECTION_COLUMNS == (
        "selection_id", "sources", "candidate_roots", "cross_folder_moves",
        "selected_at", "selected_by",
    )
    columns = [r["name"] for r in schema.execute("PRAGMA table_info(corpus_selections)")]
    assert tuple(columns) == SELECTION_COLUMNS


def test_an_empty_source_set_is_stored_as_an_empty_set(schema, tmp_path: Path):
    # Done-means 2's precondition: no default corpus is synthesized at record time
    # any more than at scan time.
    selection_id = record_selection(schema, sources=[], candidate_roots=[],
                                    cross_folder_moves=False, selected_by=None)
    assert selection_sources(schema, selection_id) == []
    assert selection_candidate_roots(schema, selection_id) == []

import pytest

from database_agent.budget import CEILING_KEYS, all_ceilings, get_ceiling, set_ceiling
from database_agent.db import create_schema


def test_there_are_exactly_seventeen_keys():
    # §8.6's twelve, three of them namespaced across two owners (O10) = fifteen,
    # plus `evidence.context_window` ratified 2026-08-20, plus `tree.max_depth`
    # 2026-08-29 -- the second of the two numbers `00`:256 names on one line.
    assert len(CEILING_KEYS) == 17
    assert len(set(CEILING_KEYS)) == 17


def test_grouping_and_placement_resolve_independently(conn):
    # O10: two parts legitimately hold three ceilings on different graphs.
    create_schema(conn)
    set_ceiling(conn, "grouping.max_retrieved_neighbors", 25)
    set_ceiling(conn, "placement.max_retrieved_neighbors", 8)
    assert get_ceiling(conn, "grouping.max_retrieved_neighbors") == 25
    assert get_ceiling(conn, "placement.max_retrieved_neighbors") == 8


def test_all_seventeen_keys_are_readable(conn):
    create_schema(conn)
    for key in CEILING_KEYS:
        set_ceiling(conn, key, 1)
    assert set(all_ceilings(conn)) == set(CEILING_KEYS)


def test_p1_enforces_nothing(conn):
    # §8.6, G4: P1 holds and publishes values; enforcement belongs elsewhere.
    create_schema(conn)
    set_ceiling(conn, "ocr.max_pages_per_file", 1)
    # Reading a ceiling is not enforcing it — no operation is refused.
    assert get_ceiling(conn, "ocr.max_pages_per_file") == 1


def test_unknown_key_is_rejected(conn):
    create_schema(conn)
    with pytest.raises(KeyError):
        set_ceiling(conn, "made.up_ceiling", 5)


def test_the_sixteenth_key_is_the_evidence_context_window(conn):
    """B4, ratified 2026-08-20. §2.8 requires surrounding context be stored and §8.6
    forbids silent truncation, but none of §8.6's twelve ceilings — and none of the
    fifteen keys — was a context length, so the budget had no configuration surface
    to live on. P4 held `context_before`/`context_after` as caller-supplied and no
    number, which was honest and left the ceiling homeless."""
    from database_agent.budget import CEILING_KEYS, get_ceiling, set_ceiling
    assert "evidence.context_window" in CEILING_KEYS
    assert len(CEILING_KEYS) == 17
    set_ceiling(conn, "evidence.context_window", 400)
    assert get_ceiling(conn, "evidence.context_window") == 400


def test_the_seventeenth_key_is_the_tree_depth_ceiling(conn):
    """2026-08-29. `00`:256 reads "Maximum folder proposals and maximum depth" --
    two numbers on one line, where every other line in that list is one. P1
    published one key for both and P10 read the single value four times, two of
    them wanting opposite values: `00`:78's own recommended tree is five levels
    deep and a picker offering five options per branch is not a picker.

    Splitting publishes what §8.6 already names. It adds no ceiling the design
    does not state, which is the only reason it is not a contract act."""
    assert "tree.max_folder_proposals" in CEILING_KEYS
    assert "tree.max_depth" in CEILING_KEYS
    assert "tree.max_folder_proposals_and_depth" not in CEILING_KEYS
    set_ceiling(conn, "tree.max_folder_proposals", 4)
    set_ceiling(conn, "tree.max_depth", 5)
    assert get_ceiling(conn, "tree.max_folder_proposals") == 4
    assert get_ceiling(conn, "tree.max_depth") == 5


def test_an_eighteenth_key_is_still_rejected(conn):
    """The key set stays closed: adding one is a contract act, not a call."""
    from database_agent.budget import set_ceiling
    with pytest.raises(KeyError):
        set_ceiling(conn, "evidence.context_window_v2", 1)

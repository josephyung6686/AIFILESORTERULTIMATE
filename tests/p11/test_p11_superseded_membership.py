"""A file version P1 has retired is not a member, and P11 must not place one.

R-25 / `103` C15. `memberships` outlive the run that wrote them -- that is what
they are for -- so a row from an earlier run still names the file version that run
saw. When the bytes at a path change, P1 marks the old row `superseded_content`
and records the new content as a NEW `files` row (`00`:135: new content is a new
version). The old membership keeps pointing at the old row, and `place_group`
gives every membership it is handed a destination.

MEASURED, on the four-file corpus of `tests/integration/test_103_diagnosis_
backlog.py`: edit one file between two runs and the second run's plan version
holds FIVE placement decisions for FOUR files, both versions of the edited file
placed. `freeze` then wrote a `move_plans` row for the version that no longer
exists -- a plan to move bytes that are not on the disk -- while the live version
got none, because the two collided on one destination name.

This is `test_p11_excluded_membership.py` one cause further out, and it is the
same rule: a placement built on a membership that is no longer true is a
contradiction rather than a low-confidence decision. There the withdrawal is P9's;
here it is P1's.

The twins are the point. A filter that reached anything except a retired version
would be a correction behaving like a demolition -- which two earlier drafts of it
were, and both are pinned below so neither can be reintroduced quietly.
"""
from __future__ import annotations

import pytest

from database_agent.files_table import (
    PATH_NO_LONGER_EXISTS, SUPERSEDED_CONTENT,
)

from placement.groups import accepted_group_as_of

from p11.p9_fixtures import GROUP_ID, MEMBERSHIPS, seed_accepted_columbia

#: What P1 writes for a file that is present. P3 owns the column and its
#: vocabulary is wider than this one word -- which is the whole of the second
#: twin below.
SCANNED = "included"


@pytest.fixture()
def seeded(p11_conn):
    seed_accepted_columbia(p11_conn)
    return p11_conn


def _record_files(conn, *, scan_state: str = SCANNED) -> None:
    """A `files` row for every member of the fixture group.

    The fixtures seed `memberships` and nothing else, so without this there is no
    P1 row for the filter to read -- which is the first twin's condition, not this
    one's.
    """
    for membership in MEMBERSHIPS:
        conn.execute(
            "INSERT INTO files (file_id, current_path, filename, "
            "normalized_filename, extension, directory_position, volume_id, "
            "content_hash, hash_algorithm, observed_size, observed_timestamps, "
            "mime_type, detected_format, scan_state, extraction_status_by_tier, "
            "sensitivity_state, st_dev, st_ino) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (membership.file_id, f"/corpus/{membership.file_id}.txt",
             f"{membership.file_id}.txt", f"{membership.file_id}.txt", ".txt",
             "root", "vol-1", membership.content_hash, "sha256", 1, "{}",
             None, None, scan_state, "{}", None, 1, 1))


def _retire(conn, file_id: str, sentinel: str) -> None:
    """P1's own write, which is what `observe_path` does when a path's bytes
    change. Done here rather than through a real re-scan because the rule under
    test is what P11 does with the row, not how P1 comes to write it."""
    conn.execute("UPDATE files SET scan_state = ? WHERE file_id = ?",
                 (sentinel, file_id))


def test_a_superseded_version_is_not_handed_to_placement_as_a_member(seeded):
    """The guard. `place_group` gives every membership it is handed a
    destination, so a version the corpus no longer has must not be one."""
    _record_files(seeded)
    _retire(seeded, "f-essay", SUPERSEDED_CONTENT)

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert "f-essay" not in {m.file_id for m in accepted.memberships}, (
        "a file version P1 superseded was still handed to P11 as a member, and "
        "`freeze` writes a move plan for every placement it is given")


def test_a_version_whose_path_has_gone_is_not_a_member_either(seeded):
    """P1's other sentinel. A person who deleted a file must not be offered it
    again (`files_table.PATH_NO_LONGER_EXISTS`), and a move plan for it would be
    an offer."""
    _record_files(seeded)
    _retire(seeded, "f-essay", PATH_NO_LONGER_EXISTS)

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert "f-essay" not in {m.file_id for m in accepted.memberships}


def test_the_other_three_members_are_untouched(seeded):
    """The twin, on all three remaining bases rather than only the one that
    broke. A filter reaching any of them would be P11 dropping a live file on
    the strength of a fact about a different one."""
    _record_files(seeded)
    _retire(seeded, "f-essay", SUPERSEDED_CONTENT)

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert {m.file_id for m in accepted.memberships} == {
        "f-transcript", "f-scan", "f-duke-essay"}


def test_a_member_with_no_p1_row_at_all_is_still_a_member(seeded):
    """ABSENCE IS NOT RETIREMENT, and the first draft got this wrong.

    Reading "keep the members whose file id is among the corpus rows" is right
    when ENUMERATING a corpus and wrong when filtering a list somebody else
    assembled. Every P11 fixture seeds `memberships` without seeding P1's table,
    so that draft dropped all four members of every group: 18 tests failed and 5
    errored. What retires a version is P1 having written a sentence about it.
    """
    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert len(accepted.memberships) == len(MEMBERSHIPS)


def test_a_scan_state_that_is_not_a_p1_sentinel_retires_nothing(seeded):
    """THE SECOND DRAFT'S FAILURE, pinned so it cannot come back.

    "Drop any member whose row does not carry the scanned value" reads the whole
    of P3's vocabulary as retirement. `scanned`, `unscanned` and `pending` are all
    in it and all mean the file is present -- `tests/test_identity.py` seeds
    `scanned` as the ordinary case -- so that draft retired live files on a word
    P3 uses to mean the opposite.
    """
    _record_files(seeded, scan_state="pending")

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert len(accepted.memberships) == len(MEMBERSHIPS)


def test_nothing_changes_for_a_group_whose_versions_are_all_current(seeded):
    """The negative twin for the filter itself. A guard that has never had to
    let anything through is not a guard."""
    _record_files(seeded)

    accepted = accepted_group_as_of(seeded, group_id=GROUP_ID,
                                    plan_version="plan-1")

    assert {m.file_id for m in accepted.memberships} == {
        m.file_id for m in MEMBERSHIPS}

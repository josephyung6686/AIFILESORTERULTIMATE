from pathlib import Path

import pytest

from database_agent.identity import (
    HASH_ALGORITHM, OBSERVATION_SESSION, DatalessFileRefused, hash_file, volume_id_for,
)


def test_same_bytes_same_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"identical")
    b.write_bytes(b"identical")
    assert hash_file(a, materialized=True) == hash_file(b, materialized=True)


def test_different_bytes_different_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"one")
    b.write_bytes(b"two")
    assert hash_file(a, materialized=True) != hash_file(b, materialized=True)


def test_algorithm_is_recorded_alongside(tmp_path: Path):
    # §8.2 requires "Content hash and hash algorithm" — the name must be available.
    assert HASH_ALGORITHM
    assert isinstance(HASH_ALGORITHM, str)


def test_large_file_is_streamed_not_loaded(tmp_path: Path):
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (5 * 1024 * 1024))
    assert len(hash_file(big, materialized=True)) == 64


def test_a_file_not_declared_materialized_is_never_opened(tmp_path: Path):
    # 11-ops-runtime.md §5: hashing a dataless iCloud item downloads it. P3 detects
    # before hashing; P1 refuses to be the path that materializes one.
    p = tmp_path / "cloud.bin"
    p.write_bytes(b"bytes that must not be read")
    with pytest.raises(DatalessFileRefused):
        hash_file(p, materialized=False)


def test_materialized_is_a_required_keyword(tmp_path: Path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"a")
    with pytest.raises(TypeError):
        hash_file(p)


def test_volume_id_is_stable_within_one_process(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    assert volume_id_for(a) == volume_id_for(b)


def test_volume_id_carries_its_observation_session(tmp_path: Path):
    # P1 OQ9 is OPEN. st_dev is not stable across remount on macOS, so a value
    # observed in another process must NOT compare equal to one observed here —
    # a cross-session comparison has to fail loudly, not misfire (§8.3, P12).
    a = tmp_path / "a.bin"
    a.write_bytes(b"a")
    value = volume_id_for(a)
    assert value.startswith(OBSERVATION_SESSION + ":")
    from_another_session = "00000000-0000-0000-0000-000000000000:" + value.split(":", 1)[1]
    assert from_another_session != value


from p1_contract import p3_basic_record
from database_agent.db import create_schema
from database_agent.files_table import (
    ReservedScanState, file_path_history, get_file, observe_path,
)


def _observed(path=None, **overrides):
    """What P3 hands P1 on an observation. A fixture stands in for P3; `author` is
    what lands in `subsystem`, because the acting part authors and P1 writes (M8)."""
    fields = dict(author="P3", component_version="p3-fixture",
                  parent_folder_context="root", mime_type=None,
                  detected_format=None, scan_state="scanned", materialized=True)
    if path is not None:
        fields.update(p3_basic_record(path))
    fields.update(overrides)
    return fields


def test_a_moved_file_keeps_one_record_and_gains_path_history(conn, tmp_path: Path):
    # R2 (§8.2): the same content observed at a new path is the same file version.
    # The ORIGINAL is gone — this is a move, not a duplicate.
    create_schema(conn)
    first = tmp_path / "one.bin"
    first.write_bytes(b"same content")
    file_id = observe_path(conn, first, **_observed(first, parent_folder_context="a"))

    second = tmp_path / "moved" / "two.bin"
    second.parent.mkdir()
    second.write_bytes(b"same content")
    first.unlink()                       # the move: only one copy is live
    again = observe_path(conn, second, **_observed(second, parent_folder_context="moved"))

    assert again == file_id
    history = file_path_history(conn, file_id)
    assert [r["path"] for r in history] == [str(first), str(second)]


def test_p1_authors_none_of_the_scan_events(conn, tmp_path: Path):
    # Contract in: P1 originates no discovery / stat observation / hashing event.
    # Every row an observation produces names its caller, never P1.
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    observe_path(conn, p, **_observed(p, author="P3"))
    rows = conn.execute("SELECT subsystem, event_type FROM events").fetchall()
    assert rows
    assert {r["subsystem"] for r in rows} == {"P3"}
    assert "P1" not in {r["subsystem"] for r in rows}


def test_author_and_component_version_are_required(conn, tmp_path: Path):
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    fields = _observed()
    fields.pop("author")
    with pytest.raises(TypeError):
        observe_path(conn, p, **fields)


def test_path_history_publishes_volume_id_as_unknown(conn, tmp_path: Path):
    # SPEC Contract out §2 shape is (path, volume_id, observed_at, event_id).
    # No per-observation volume is recorded (P1 OQ9), so the column reads as
    # unknown rather than repeating a within-session value as if it were history.
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    file_id = observe_path(conn, p, **_observed(p))
    row = file_path_history(conn, file_id)[0]
    assert set(row.keys()) == {"path", "volume_id", "observed_at", "event_id"}
    assert row["volume_id"] is None


def test_two_live_copies_are_two_records_sharing_one_hash(conn, tmp_path: Path):
    # I1 (ratified): two live copies = two `files` rows, same content_hash,
    # different file_id and path. §2.9 requires duplicate-family signals, which
    # are unrepresentable if duplicates collapse into one record; §8.3's collision
    # policy presumes both copies exist.
    create_schema(conn)
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"identical bytes")
    b.write_bytes(b"identical bytes")

    id_a = observe_path(conn, a, **_observed(a))
    id_b = observe_path(conn, b, **_observed(b))

    assert id_a != id_b
    rows = conn.execute(
        "SELECT file_id, current_path, content_hash FROM files ORDER BY current_path"
    ).fetchall()
    assert len(rows) == 2
    assert rows[0]["content_hash"] == rows[1]["content_hash"]
    assert {r["current_path"] for r in rows} == {str(a), str(b)}


def test_deleting_one_of_two_live_copies_does_not_hijack_the_survivor(conn, tmp_path: Path):
    # R2 only applies when the observed path is not already a live row.
    create_schema(conn)
    a = tmp_path / "A.pdf"
    b = tmp_path / "B.pdf"
    a.write_bytes(b"duplicate bytes")
    b.write_bytes(b"duplicate bytes")
    file_a = observe_path(conn, a, **_observed(a))
    file_b = observe_path(conn, b, **_observed(b))
    a.unlink()
    again = observe_path(conn, b, **_observed(b))
    assert again == file_b
    assert again != file_a
    paths = [r["current_path"] for r in conn.execute("SELECT current_path FROM files")]
    assert len(paths) == len(set(paths))


def test_caller_cannot_supply_p1s_superseded_sentinel(conn, tmp_path: Path):
    create_schema(conn)
    p = tmp_path / "doc.txt"
    p.write_bytes(b"bytes")
    with pytest.raises(ReservedScanState):
        observe_path(conn, p, **_observed(p, scan_state="superseded_content"))


def test_observe_path_hashes_once(conn, tmp_path: Path, monkeypatch):
    import database_agent.files_table as ft

    real = ft.hash_file
    calls = []

    def counting_hash(path, *, materialized):
        calls.append(path)
        return real(path, materialized=materialized)

    monkeypatch.setattr(ft, "hash_file", counting_hash)
    p = tmp_path / "syncing.txt"
    p.write_bytes(b"bytes")
    file_id = observe_path(conn, p, **_observed(p))
    assert len(calls) == 1
    row_hash = get_file(conn, file_id)["content_hash"]
    event_hash = conn.execute(
        "SELECT content_hash FROM events WHERE file_id = ? ORDER BY event_id DESC LIMIT 1",
        (file_id,),
    ).fetchone()["content_hash"]
    assert row_hash == event_hash


def test_same_path_new_bytes_is_a_new_version_and_invalidates_extraction(conn, tmp_path: Path):
    # R3 (§8.2): a file whose content hash changes is a new version.
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed(p))

    p.write_bytes(b"version two")
    second_id = observe_path(conn, p, **_observed(p))

    assert second_id != first_id
    assert get_file(conn, second_id)["extraction_status_by_tier"] == "{}"
    assert get_file(conn, first_id)["scan_state"] == "superseded_content"


def test_the_superseded_version_carries_its_authors_explanation(conn, tmp_path: Path):
    # No mutation of the current projection is accepted without the authoring
    # part's event explaining it (SPEC, Cross-cutting answers → Provenance).
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed(p))
    p.write_bytes(b"version two")
    observe_path(conn, p, **_observed(p))

    explaining = conn.execute(
        "SELECT * FROM events WHERE file_id = ? AND event_type = "
        "'external modification detection'", (first_id,)
    ).fetchone()
    assert explaining is not None
    assert explaining["subsystem"] == "P3"


# ---------------------------------------------------------------------------
# Identity resolution inside a duplicate family.
#
# `observe_path` used to answer "is one of the rows for these bytes the file I am
# looking at?" by `lstat`ing every member of the duplicate family: O(k) syscalls to
# admit one file, O(k^2) to admit a family of k. The family is no longer read; the
# inode question is asked of an index and the move question is asked of the oldest
# recorded home. These tests pin what that must NOT have changed, because a syscall
# count that only falls can be satisfied by an identity resolver that answers wrongly.
# ---------------------------------------------------------------------------

import os


def _family(tmp_path: Path, size: int, *, content=b"IDENTICAL") -> list[Path]:
    corpus = tmp_path / "corpus"
    corpus.mkdir(exist_ok=True)
    members = []
    for index in range(size):
        member = corpus / f"copy_{index:03d}.bin"
        member.write_bytes(content)
        members.append(member)
    return members


def _admission_syscalls(conn, target: Path) -> int:
    """Filesystem calls `observe_path` makes admitting `target`, and nothing else.

    The R2 record is computed first and outside the count: deriving it is P3's job
    and P3's stat is not what is being measured here.
    """
    fields = _observed(target)
    calls = [0]
    real_lstat, real_stat = os.lstat, os.stat

    def counted_lstat(t, *a, _r=real_lstat, **k):
        calls[0] += 1
        return _r(t, *a, **k)

    def counted_stat(t, *a, _r=real_stat, **k):
        calls[0] += 1
        return _r(t, *a, **k)

    os.lstat, os.stat = counted_lstat, counted_stat
    try:
        observe_path(conn, target, **fields)
    finally:
        os.lstat, os.stat = real_lstat, real_stat
    return calls[0]


def test_admitting_a_duplicate_costs_the_same_in_a_big_family_as_in_a_small_one(
        conn, tmp_path: Path):
    """The in-suite twin of `test_identity_resolution_does_not_stat_the_whole_
    duplicate_family`, which is gated behind SCALE_STRESS=1 and takes a minute.

    Empty files, `.DS_Store`, stub configs and repeated downloads form families in
    the tens of thousands on a real disk, so a per-file cost that rises with family
    size is a scan that never finishes.
    """
    create_schema(conn)
    members = _family(tmp_path, 60)
    costs: dict[int, int] = {}
    for position, member in enumerate(members, start=1):
        cost = _admission_syscalls(conn, member)
        if position in (20, 60):
            costs[position] = cost

    assert costs[60] == costs[20], (
        f"admitting the 20th member of a duplicate family cost {costs[20]} filesystem "
        f"calls and the 60th cost {costs[60]}. Per-file cost that rises with family "
        "size means the family costs O(k^2) to admit."
    )
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 60


def test_every_live_copy_in_a_family_keeps_its_own_record(conn, tmp_path: Path):
    """I1, at family scale: two live copies are two records, and so are sixty.

    The negative twin of the syscall guard above. Not reading the family is only a
    fix if the file admitted is still recorded as a copy rather than resolved onto
    one of its twins.
    """
    create_schema(conn)
    members = _family(tmp_path, 60)
    ids = [observe_path(conn, member, **_observed(member)) for member in members]

    assert len(set(ids)) == 60
    rows = conn.execute("SELECT file_id, current_path, content_hash FROM files").fetchall()
    assert len(rows) == 60
    assert len({r["content_hash"] for r in rows}) == 1
    assert {r["current_path"] for r in rows} == {str(m) for m in members}


def test_a_rename_inside_a_duplicate_family_keeps_the_renamed_copys_identity(
        conn, tmp_path: Path):
    """The case the inode index exists for, and the one a naive "don't read the
    family" fix silently breaks.

    A rename on the same volume keeps the inode, so the observed file and its own
    row are the same file even though the path is new and fifty-nine identical
    twins share its bytes. Resolving this by content alone would hand the renamed
    file whichever twin came first; not resolving it at all would mint a second row
    for a file that only changed its name.
    """
    create_schema(conn)
    members = _family(tmp_path, 60)
    ids = {member: observe_path(conn, member, **_observed(member))
           for member in members}

    renamed_from = members[42]
    renamed_to = renamed_from.with_name("renamed.bin")
    renamed_from.rename(renamed_to)

    again = observe_path(conn, renamed_to, **_observed(renamed_to))

    assert again == ids[renamed_from], "the renamed copy became a different file"
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 60
    assert get_file(conn, again)["current_path"] == str(renamed_to)
    assert [r["path"] for r in file_path_history(conn, again)] == [
        str(renamed_from), str(renamed_to)]


def test_a_deleted_twin_does_not_steal_a_live_copys_identity_in_a_family(
        conn, tmp_path: Path):
    """`test_deleting_one_of_two_live_copies_does_not_hijack_the_survivor` at family
    scale, and against the new resolution path: the deleted member is now the OLDEST
    recorded home, which is the one row the move branch looks at."""
    create_schema(conn)
    members = _family(tmp_path, 20)
    ids = {member: observe_path(conn, member, **_observed(member))
           for member in members}
    members[0].unlink()

    for member in members[1:]:
        assert observe_path(conn, member, **_observed(member)) == ids[member], (
            f"{member.name} was resolved onto the deleted oldest copy")
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 20


def test_a_recycled_inode_is_a_candidate_and_never_an_answer(conn, tmp_path: Path):
    """Inodes are recycled. `st_dev`/`st_ino` are what the filesystem said when the
    row last wrote its path, so a stored pair can name a file that no longer exists
    and a number since handed to a different file — which is why an index hit is
    confirmed by `lstat`ing the recorded path before it is believed.

    The recycling is forced rather than waited for: which inode a filesystem reissues
    is not something a test can arrange, and the failure it would cause — two
    unrelated files resolved onto one record — is too expensive to leave to luck.
    """
    create_schema(conn)
    recorded = tmp_path / "recorded.bin"
    recorded.write_bytes(b"identical bytes")
    recorded_id = observe_path(conn, recorded, **_observed(recorded))

    newcomer = tmp_path / "newcomer.bin"
    newcomer.write_bytes(b"identical bytes")
    reissued = os.lstat(newcomer)
    conn.execute("UPDATE files SET st_dev = ?, st_ino = ? WHERE file_id = ?",
                 (reissued.st_dev, reissued.st_ino, recorded_id))

    newcomer_id = observe_path(conn, newcomer, **_observed(newcomer))

    assert newcomer_id != recorded_id, (
        "a row whose remembered inode had been reissued to another file claimed that "
        "file's identity; the index hit was believed instead of confirmed"
    )
    assert get_file(conn, recorded_id)["current_path"] == str(recorded)
    assert get_file(conn, newcomer_id)["current_path"] == str(newcomer)


def test_a_move_is_recognised_when_the_oldest_recorded_home_is_the_one_that_went(
        conn, tmp_path: Path):
    """R2's move, with twins present. A cross-volume move and a copy-then-delete
    arrive as a genuinely new inode, so the only evidence of the move is that a
    recorded copy of these bytes has gone missing — and the missing one here is the
    oldest recorded home, which is the row the move branch asks about."""
    create_schema(conn)
    gone = tmp_path / "gone.bin"
    twin = tmp_path / "twin.bin"
    gone.write_bytes(b"identical bytes")
    twin.write_bytes(b"identical bytes")
    gone_id = observe_path(conn, gone, **_observed(gone))
    twin_id = observe_path(conn, twin, **_observed(twin))

    arrived = tmp_path / "elsewhere" / "arrived.bin"
    arrived.parent.mkdir()
    arrived.write_bytes(b"identical bytes")     # a new inode: a copy, not a rename
    gone.unlink()

    assert observe_path(conn, arrived, **_observed(arrived)) == gone_id
    assert get_file(conn, twin_id)["current_path"] == str(twin)
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 2


def test_a_move_inside_a_live_family_now_mints_its_own_record(conn, tmp_path: Path):
    """CHARACTERISES the one deliberate narrowing, so it is visible in the diff.

    Deletion leaves nothing in the database, so "is any recorded copy of these bytes
    missing?" cannot be answered by an index — only by one filesystem call per
    recorded copy, which is the O(k^2) the family walk was. The move branch therefore
    asks the narrower question the oldest recorded home can answer in one call.

    Here the oldest home is still live and a LATER member is the one that went, so
    the walk would have relocated that member's record onto the arriving file and
    this does not: the arriving file gets its own record.

    The walk's answer was a guess. Which of k identical copies moved is not knowable
    from the bytes, and it always named the earliest rowid — so with `first` live and
    `second` gone it would have been right, and with `second` live and `first` gone it
    would have named the wrong one. What is not a guess is the direction of the error:
    this can only ever mint an extra record, never merge two files into one.
    """
    create_schema(conn)
    first = tmp_path / "first.bin"
    second = tmp_path / "second.bin"
    first.write_bytes(b"identical bytes")
    second.write_bytes(b"identical bytes")
    first_id = observe_path(conn, first, **_observed(first))
    second_id = observe_path(conn, second, **_observed(second))

    arrived = tmp_path / "elsewhere" / "arrived.bin"
    arrived.parent.mkdir()
    arrived.write_bytes(b"identical bytes")
    second.unlink()

    arrived_id = observe_path(conn, arrived, **_observed(arrived))

    assert arrived_id not in (first_id, second_id)
    assert get_file(conn, first_id)["current_path"] == str(first), (
        "the still-live oldest copy kept its own path — nothing was merged")
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 3


def test_a_rename_is_told_apart_from_a_twin_that_was_deleted(conn, tmp_path: Path):
    """The negative twin of the rename above, and the one that pins WHICH row the
    rename resolves onto rather than merely that it resolved onto one.

    The family walk answered "which of these rows is the file I am looking at?" with
    "the first one whose path has gone missing" — no inode evidence at all. With one
    missing member that guess is right by luck, so a family holding exactly one dead
    path cannot tell a correct resolver from a lucky one.

    Here two members are gone at once: the OLDEST was deleted outright, and a later
    one was renamed. The oldest is also the single row `_relocated_row` inspects, so
    both the walk's rule and the move branch's rule name it — and both are wrong. The
    renamed file must come back as itself, which only its own remembered inode can
    say. The deleted twin's record must be left where it is: relocating it onto the
    renamed file would merge two people's files into one record, which is the failure
    this whole resolver is written to avoid.
    """
    create_schema(conn)
    members = _family(tmp_path, 20)
    ids = {member: observe_path(conn, member, **_observed(member)) for member in members}

    deleted = members[0]
    renamed_from = members[13]
    renamed_to = renamed_from.with_name("renamed.bin")
    deleted.unlink()
    renamed_from.rename(renamed_to)

    again = observe_path(conn, renamed_to, **_observed(renamed_to))

    assert again == ids[renamed_from], (
        "the renamed copy was resolved onto a twin that had merely been deleted; "
        "identity came from 'some family member is missing', not from the inode"
    )
    assert get_file(conn, ids[deleted])["current_path"] == str(deleted), (
        "the deleted twin's record was dragged onto the renamed file")
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 20
    assert [r["path"] for r in file_path_history(conn, again)] == [
        str(renamed_from), str(renamed_to)]


def test_a_reissued_inode_whose_recorded_home_is_gone_is_indistinguishable_from_a_move(
        conn, tmp_path: Path):
    """CHARACTERISES the single point where a candidate is believed without its
    recorded path agreeing, so the boundary is visible in the diff rather than
    discovered later.

    `test_a_recycled_inode_is_a_candidate_and_never_an_answer` covers the case the
    row can settle: its recorded path is still there and is a DIFFERENT file, so the
    row's own home refutes the index hit. Here the home is GONE, and what is left is
    a row remembering this exact inode, these exact bytes, and no path — which is
    precisely what a rename looks like, because a rename is exactly that. Nothing in
    the database separates the two, and demanding more would reject every rename
    (test_a_rename_inside_a_duplicate_family_keeps_the_renamed_copys_identity).

    This is not a loosening. The walk this replaced relocated ANY family member whose
    path had gone missing, choosing between k of them by rowid and consulting no
    inode at all; it merged here too, on strictly less evidence.
    """
    create_schema(conn)
    gone = tmp_path / "gone.bin"
    gone.write_bytes(b"identical bytes")
    gone_id = observe_path(conn, gone, **_observed(gone))
    gone.unlink()

    newcomer = tmp_path / "newcomer.bin"
    newcomer.write_bytes(b"identical bytes")
    reissued = os.lstat(newcomer)
    conn.execute("UPDATE files SET st_dev = ?, st_ino = ? WHERE file_id = ?",
                 (reissued.st_dev, reissued.st_ino, gone_id))

    assert observe_path(conn, newcomer, **_observed(newcomer)) == gone_id, (
        "read as a move, which is what the evidence says and what the walk said too"
    )
    assert conn.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == 1

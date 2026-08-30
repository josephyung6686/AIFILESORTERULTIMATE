"""§8.3's collision policy. Four behaviours, and never a silent overwrite.

`00`:172: *"The engine should never silently overwrite an existing file. It may
propose one of several user-approved behaviors: preserve both files using a
deterministic suffix, merge only when hashes prove the files are identical,
retain the newer file while placing an older version into a version family
review, or stop and ask the user. The collision rule must distinguish exact
duplicates from different files that happen to share a filename. A content-hash
match supports deduplication review; a filename match alone does not."*

That last sentence is the negative twin, and it is the one a hurried
implementation gets wrong: falling back from `merge_only_if_hashes_identical` to
a suffix looks harmless and makes a deduplication behaviour reachable for two
files that are not duplicates at all.

**Q3 is the owner's and is open.** §8.3 requires *"a deterministic suffix"* and
names no form. `suffix_for` is injected with no default and the format below is
THIS FIXTURE's choice, not P12's.
"""
from __future__ import annotations

import itertools
import os
import unicodedata
from pathlib import Path

import pytest

from database_agent.identity import hash_file

from mutation import vocabulary as v
from mutation.collision import (
    MergeRefused, SuffixExhausted, find_collision, record_collision,
    resolve_collision,
)

from p12.conftest import CONSTRAINTS, FOLDING_CONSTRAINTS

#: `74` §8 Q3 is OPEN. This is the fixture's suffix format and nothing promotes
#: it to a module constant in `src/mutation/`: the moment it is one, it is the
#: answer, and the answer was not P12's to give.
def _suffix(stem: str, attempt: int) -> str:
    return f"{stem} ({attempt})"


#: Also the fixture's. §8.3 bounds nothing here either.
ATTEMPTS = 100

IDS = itertools.count()


def _mint():
    return f"vfr-{next(IDS)}"


def _resolve(plan, incumbent, incoming, behaviour, *, constraints=CONSTRAINTS,
             attempts=ATTEMPTS):
    return resolve_collision(
        plan, incumbent=incumbent, incoming_path=incoming,
        incoming_hash=hash_file(incoming, materialized=True),
        behaviour=behaviour, constraints=constraints, suffix_for=_suffix,
        max_suffix_attempts=attempts, materialized=True, mint_id=_mint)


@pytest.fixture()
def occupied(planned):
    """A destination directory holding an incumbent of the same name, whose
    bytes differ from the incoming file's."""
    plan, source = planned
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b"an incumbent with different bytes")
    return plan, source, destination


@pytest.fixture()
def duplicated(planned):
    """The same, but byte-identical -- the only case merge may be applied to."""
    plan, source = planned
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    return plan, source, destination


def _older(path: Path):
    os.utime(path, (1_700_000_000, 1_700_000_000))


def _newer(path: Path):
    os.utime(path, (1_800_000_000, 1_800_000_000))


# ---------------------------------------------------------------------------
# The pair Wave D3 names.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("behaviour", v.COLLISION_BEHAVIOURS)
def test_no_collision_behaviour_reaches_an_overwrite(planned, behaviour):
    """Done-means 6's last sentence: *"No path exists through the code that
    overwrites an existing file."*

    All four behaviours are exercised against a real occupied destination, and
    each is checked three ways -- the incumbent's bytes are unchanged, the
    directory holds exactly the entries it held before, and whatever path the
    behaviour hands back for writing is a path nothing occupies.

    The third is the structural one. `resolve_collision` writes nothing itself;
    what makes overwriting unreachable is that the executor is never HANDED an
    occupied path, which is a property of the return value and not of anyone's
    care at the call site.
    """
    plan, source = planned
    destination = Path(plan.resolved_destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # `merge_only_if_hashes_identical` may be applied only to a hash-identical
    # collision, so that is the incumbent it gets. Feeding it a different file
    # would be testing its refusal, which is the twin's job.
    identical = behaviour == v.MERGE_ONLY_IF_HASHES_IDENTICAL
    incumbent_bytes = (source.read_bytes() if identical
                       else b"an incumbent with different bytes")
    destination.write_bytes(incumbent_bytes)
    before = sorted(item.name for item in destination.parent.iterdir())

    got = _resolve(plan, destination, source, behaviour)

    assert got.behaviour_applied == behaviour
    assert got.outcome in v.COLLISION_OUTCOMES
    assert destination.read_bytes() == incumbent_bytes
    assert sorted(item.name for item in destination.parent.iterdir()) == before
    assert source.exists()
    if got.final_destination_path is not None:
        final = Path(got.final_destination_path)
        assert final != destination
        assert not final.exists()
        assert find_collision(final.parent, final.name,
                              constraints=CONSTRAINTS) is None


def test_a_filename_match_alone_is_never_treated_as_a_duplicate(occupied):
    """The negative twin. `00`:172: *"A content-hash match supports
    deduplication review; a filename match alone does not."*

    Two files that happen to share a filename are two files. Classifying that
    as a duplicate, or letting `merge_only_if_hashes_identical` quietly fall
    back to a suffix when the hashes differ, would make a deduplication
    behaviour reachable for two documents that have nothing to do with each
    other -- and the merge behaviour's outcome is *"merged, no write"*, so the
    incoming file would simply never arrive.

    Both directions are asserted: the name-only collision is refused, and the
    genuine hash match is accepted, so a guard that refused everything would
    not pass either.
    """
    plan, source, destination = occupied
    incumbent_bytes = destination.read_bytes()

    with pytest.raises(MergeRefused) as excinfo:
        _resolve(plan, destination, source, v.MERGE_ONLY_IF_HASHES_IDENTICAL)
    assert v.NAME_ONLY in str(excinfo.value)
    assert destination.read_bytes() == incumbent_bytes
    assert source.exists()

    # The kind itself, under every behaviour that does not refuse: same name,
    # different bytes, and it is never `content_hash_match`.
    for behaviour in (v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX, v.STOP_AND_ASK,
                      v.RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW):
        got = _resolve(plan, destination, source, behaviour)
        assert got.collision_kind == v.NAME_ONLY
        assert got.incumbent_content_hash != got.incoming_content_hash

    # And the other direction: a real duplicate IS one, and merges. The same
    # incumbent path, the same name, the only difference being the bytes -- so
    # nothing but the hash comparison can be what separates the two answers.
    destination.write_bytes(source.read_bytes())
    merged = _resolve(plan, destination, source,
                      v.MERGE_ONLY_IF_HASHES_IDENTICAL)
    assert merged.collision_kind == v.CONTENT_HASH_MATCH
    assert merged.outcome == v.MERGED_NO_WRITE
    assert merged.incumbent_content_hash == merged.incoming_content_hash


# ---------------------------------------------------------------------------
# Done-means 7 and 8 — what counts as one name on which volume.
# ---------------------------------------------------------------------------


def test_an_empty_directory_has_no_collision(planned):
    plan, _ = planned
    directory = Path(plan.resolved_destination_path).parent
    directory.mkdir(parents=True)
    assert find_collision(directory, "Syllabus.pdf",
                          constraints=CONSTRAINTS) is None


def test_a_directory_that_does_not_exist_yet_has_no_collision(planned):
    plan, _ = planned
    assert find_collision(Path(plan.resolved_destination_path).parent,
                          "Syllabus.pdf", constraints=CONSTRAINTS) is None


def test_resume_and_resume_are_one_name_on_a_folding_volume_and_two_otherwise(
        fixture_root):
    """Done-means 7. Case sensitivity is a property of the TARGET volume, and
    it is what decides whether these are one path or two."""
    directory = fixture_root / "dir"
    directory.mkdir()
    (directory / "Resume.pdf").write_bytes(b"the incumbent")
    assert find_collision(directory, "resume.pdf",
                          constraints=FOLDING_CONSTRAINTS) == \
        directory / "Resume.pdf"
    assert find_collision(directory, "resume.pdf",
                          constraints=CONSTRAINTS) is None


def test_two_names_differing_only_by_normalization_form_collide_on_both(
        fixture_root):
    """Done-means 8. *"Unicode normalization differs across operating systems
    and cloud services, making visually identical names potentially collide."*

    This is also why `find_collision` compares collation keys over the real
    listing instead of calling `Path.exists()`: on a case-sensitive volume
    `exists()` answers False for an NFC/NFD pair a person cannot tell apart.
    On macOS the volume normalizes the name itself, so the keys match for that
    reason instead -- the assertion holds either way, which is the point of
    comparing keys rather than raw bytes.
    """
    directory = fixture_root / "dir"
    directory.mkdir()
    composed = unicodedata.normalize("NFC", "Café.pdf")
    decomposed = unicodedata.normalize("NFD", "Café.pdf")
    assert composed != decomposed
    (directory / composed).write_bytes(b"the incumbent")
    for constraints in (CONSTRAINTS, FOLDING_CONSTRAINTS):
        assert find_collision(directory, decomposed,
                              constraints=constraints) is not None


# ---------------------------------------------------------------------------
# Done-means 6 — the four behaviours, one at a time.
# ---------------------------------------------------------------------------


def test_preserve_both_produces_a_suffixed_path_and_leaves_the_incumbent_alone(
        occupied):
    plan, source, destination = occupied
    got = _resolve(plan, destination, source,
                   v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX)
    assert got.collision_kind == v.NAME_ONLY
    assert got.outcome == v.SUFFIXED_PATH
    assert got.final_destination_path == str(
        destination.parent / "Syllabus (1).pdf")


def test_a_hash_identical_collision_merges_with_no_write(duplicated):
    plan, source, destination = duplicated
    got = _resolve(plan, destination, source, v.MERGE_ONLY_IF_HASHES_IDENTICAL)
    assert got.outcome == v.MERGED_NO_WRITE
    assert got.final_destination_path is None
    assert source.exists() and destination.exists()


def test_retain_newer_when_the_incumbent_is_newer_writes_nothing(occupied):
    """§7.11 forbids deleting a user file and the incumbent is one, so
    *"retain the newer file while placing an older version into a version
    family review"* keeps BOTH files in both branches. Here the incoming file
    is the older one, so it is the one routed to review and nothing is written.
    """
    plan, source, destination = occupied
    _older(source)
    _newer(destination)
    got = _resolve(plan, destination, source,
                   v.RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW)
    assert got.outcome == v.OLDER_SENT_TO_VERSION_FAMILY_REVIEW
    assert got.final_destination_path is None
    assert got.version_family_review_ref is not None
    assert source.exists()


def test_retain_newer_when_the_incoming_is_newer_suffixes_and_keeps_both(
        occupied):
    plan, source, destination = occupied
    incumbent_bytes = destination.read_bytes()
    _newer(source)
    _older(destination)
    got = _resolve(plan, destination, source,
                   v.RETAIN_NEWER_OLDER_TO_VERSION_FAMILY_REVIEW)
    assert got.outcome == v.OLDER_SENT_TO_VERSION_FAMILY_REVIEW
    assert got.final_destination_path == str(
        destination.parent / "Syllabus (1).pdf")
    assert got.version_family_review_ref is not None
    assert destination.read_bytes() == incumbent_bytes


def test_stop_and_ask_halts_with_no_mutation(occupied):
    plan, source, destination = occupied
    got = _resolve(plan, destination, source, v.STOP_AND_ASK)
    assert got.outcome == v.HALTED_AWAITING_USER
    assert got.final_destination_path is None
    assert got.version_family_review_ref is None


def test_no_behaviour_ever_returns_a_path_that_is_already_occupied(occupied):
    plan, source, destination = occupied
    (destination.parent / "Syllabus (1).pdf").write_bytes(b"already taken")
    got = _resolve(plan, destination, source,
                   v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX)
    assert got.final_destination_path == str(
        destination.parent / "Syllabus (2).pdf")
    assert not Path(got.final_destination_path).exists()


def test_suffix_exhaustion_raises_rather_than_looping_forever(occupied):
    """The bound is the caller's -- §8.3 states none -- and running out is a
    refusal to invent a name nobody could predict, not a silent overwrite."""
    plan, source, destination = occupied
    attempts = 3
    for attempt in range(1, attempts + 1):
        (destination.parent / f"Syllabus ({attempt}).pdf").write_bytes(b"taken")
    with pytest.raises(SuffixExhausted):
        _resolve(plan, destination, source,
                 v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX, attempts=attempts)


# ---------------------------------------------------------------------------
# Q3 and the vocabulary — injected with no default, refused when absent.
# ---------------------------------------------------------------------------


def test_the_suffix_format_and_its_bound_are_injected_with_no_default(occupied):
    """`74` §8 Q3. §8.3 asks for *"a deterministic suffix"* and names no form,
    and the form is user-visible in every filename it touches. So there is no
    default to fall back to and no module-level constant to read: omitting
    either is a `TypeError`, not a quiet house choice."""
    plan, source, destination = occupied
    incoming_hash = hash_file(source, materialized=True)
    common = dict(incumbent=destination, incoming_path=source,
                  incoming_hash=incoming_hash,
                  behaviour=v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
                  constraints=CONSTRAINTS, materialized=True, mint_id=_mint)
    with pytest.raises(TypeError):
        resolve_collision(plan, max_suffix_attempts=ATTEMPTS, **common)
    with pytest.raises(TypeError):
        resolve_collision(plan, suffix_for=_suffix, **common)


def test_an_unknown_behaviour_is_out_of_vocabulary(occupied):
    plan, source, destination = occupied
    with pytest.raises(v.OutOfVocabulary):
        _resolve(plan, destination, source, "overwrite_the_old_one")


def test_recording_a_collision_appends_one_event_and_round_trips(p12_conn,
                                                                 occupied):
    plan, source, destination = occupied
    got = _resolve(plan, destination, source,
                   v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX)
    record_collision(p12_conn, got, file_id=plan.file_id,
                     created_at="2026-08-29T00:00:00Z",
                     component_version="p12-test", record_id="col-1")
    rows = p12_conn.execute(
        "SELECT subsystem, old_path, new_path FROM events WHERE event_type = ?",
        (v.FILENAME_COLLISION_RESOLUTION,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == v.SUBSYSTEM
    assert rows[0]["old_path"] == str(destination)
    assert rows[0]["new_path"] == got.final_destination_path
    stored = p12_conn.execute(
        "SELECT collision_kind, behaviour_applied, outcome FROM "
        "collision_resolutions WHERE record_id = ?", ("col-1",)).fetchone()
    assert tuple(stored) == (v.NAME_ONLY,
                             v.PRESERVE_BOTH_DETERMINISTIC_SUFFIX,
                             v.SUFFIXED_PATH)

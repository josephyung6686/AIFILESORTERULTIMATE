"""Copy, confirm, and only then remove. §8.2's V4, and the one permitted unlink.

*"For a cross-volume move, the destination copy must be hashed and confirmed
before the source can be removed"* (§8.2). Everything in this module is that
sentence read as an order rather than as a list: the copy is written, P1 is asked
whether what landed is byte-identical to what was intended, and the source is
removed **only** on `True`. This is file fixity -- the system can show that the
file at its destination is byte-identical to the file it intended to move -- and
it is the only reason V4 exists as a separate point from V3.

**The one `unlink` in `src/mutation/`.** §7.11 forbids deleting a user's file and
SPEC §5 states the single exception: the cross-volume source removal, unreachable
until V4 returned True. It is on one line, in one function, behind one `if`, so
that the F4 introspection guard can name it and so that a reader can check the
whole of the exception in a glance. A copy that failed its own verification is
NOT cleaned up: a partial or unverified copy is still a file on the person's
disk, and P12 removing it would be the same act §7.11 forbids, differing only in
who would notice.

**`74` §8 Q7 is open and this module refuses rather than answering it.** §8.2
forbids removing the source and §7.11 forbids deleting the copy, so after an
unconfirmed copy BOTH paths exist. Where the copy lives, what it is called and
how the person is shown it are not settled anywhere in the design.
`unverified_copy_disposition` is therefore injected with no default and P12 will
not begin a cross-volume copy without it: a file P12 creates and cannot account
for to the person is worse than a move P12 did not make. When Q7 closes, the
answer lands in the composition root and this module does not change.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from database_agent.verify import confirm_cross_volume_copy

from mutation.constraints import FilesystemConstraints
from mutation.collision import find_collision
from mutation.vocabulary import SUBSYSTEM


class UnverifiedCopyDispositionRequired(RuntimeError):
    """`74` §8 Q7's answer is absent.

    NOT a refusal class, for the reason `plan.NoSuchPlan` is not one: a refusal
    describes a plan that could not execute and carries a sentence for the
    person, and this is the composition root not having stated a policy that is
    its own to state.
    """


@dataclass(frozen=True)
class CrossVolumeOutcome:
    """What the copy-and-confirm step did, and what is on disk afterwards."""

    #: P1's V4 answer. The source removal is gated on exactly this.
    destination_confirmed: bool
    source_removed: bool
    destination_path: str
    #: The copy that exists and was never confirmed, or `None`. Named on the
    #: record so it can be shown; never removed.
    unverified_copy_path: str | None
    #: The composition root's sentence about that copy (`74` §8 Q7).
    disposition: str | None


def _copy_bytes(source: Path, destination: Path) -> None:
    """Write the copy, refusing an occupied destination at the system call.

    Mode `"xb"` is `O_CREAT | O_EXCL`: a copy CREATES a file, so the kernel's own
    exclusive create is available here in a way it is not for the same-volume
    rename, and it CLOSES the window that `_atomic_rename` can only name.
    Nothing is removed if the write fails part-way -- see the module docstring.
    """
    with open(destination, "xb") as writing, open(source, "rb") as reading:
        shutil.copyfileobj(reading, writing)
    # Timestamps come across too: P12 carries P1's observed size and timestamps
    # forward unchanged after a move, and a copy that reset the modification
    # time would make that carry-forward a lie.
    shutil.copystat(source, destination)


def copy_and_confirm(conn: sqlite3.Connection, *, source: Path,
                     destination: Path, expected_hash: str,
                     constraints: FilesystemConstraints,
                     unverified_copy_disposition: str | None,
                     component_version: str,
                     materialized: bool) -> CrossVolumeOutcome:
    """The copy-and-delete half of a cross-volume move. V4 gates the removal."""
    if unverified_copy_disposition is None:
        raise UnverifiedCopyDispositionRequired(
            "`74` §8 Q7 is open: an unconfirmed copy leaves BOTH paths on disk "
            "and P12 will not create one until the composition root has said "
            "what the person is told about it")
    if find_collision(destination.parent, destination.name,
                      constraints=constraints) is not None:
        raise FileExistsError(
            f"{destination} is occupied; the executor is never handed an "
            "occupied path (§8.3, `00`:172)")

    _copy_bytes(source, destination)
    confirmed = confirm_cross_volume_copy(
        conn, source=source, destination=destination,
        expected_hash=expected_hash, author=SUBSYSTEM,
        component_version=component_version, materialized=materialized)
    if not confirmed:
        return CrossVolumeOutcome(
            destination_confirmed=False, source_removed=False,
            destination_path=str(destination),
            unverified_copy_path=str(destination),
            disposition=unverified_copy_disposition)

    # The one permitted unlink in `src/mutation/`, unreachable until V4 said
    # True (§7.11, SPEC §5). Nothing else in this part removes a file.
    os.unlink(source)
    return CrossVolumeOutcome(
        destination_confirmed=True, source_removed=True,
        destination_path=str(destination), unverified_copy_path=None,
        disposition=None)

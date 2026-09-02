"""One same-volume move that cannot land on an occupied path.

**This is the only place in the product where a person's bytes can be destroyed,
so the guarantee is the system call's and not a check's.** `os.rename` on POSIX
replaces the destination silently. Every check written before it -- `find_collision`
at plan time, `find_collision` again a line above the call -- is a check with a
window after it, and the window is wide enough: `undo` ran two full file hashes
inside its own. Worse, a check only sees what its `FilesystemConstraints` told it
to look for, and that table is one value for the whole process. A person filing
onto an exFAT stick, an NTFS partition, an SMB share or a casefold ext4 directory
runs with a table that does not describe their disk, and under `os.rename` a
wrong table is a destroyed file rather than a wrong answer.

`os.link` closes both at once. It fails with `FileExistsError` **atomically** if
anything is at the destination, and -- measured, not assumed -- it fails that way
under case folding and under NFC/NFD folding too, where the folding is the
volume's own and no declaration is consulted. So "never silently overwrite"
stops being a property of the constraint table being right and becomes a property
of the kernel.

This is what `docs/superpowers/plans/2026-08-29-p12-apply-undo.md` specified
(F14, and the rationale at line 4355). The implementation drifted to `os.rename`
and named the resulting window in `execute.py`'s docstring, citing §7.11 against
the fix -- the objection the plan had already answered at line 5316: after a
successful `os.link` the two paths are the SAME INODE, so unlinking one removes a
name and not a file. §7.11 forbids deleting a user file. Neither branch does.

**The fallback, and why it is not optional.** exFAT and FAT32 do not support hard
links, and that is precisely the volume the wrong-declaration case is about --
`os.link` alone would make the exFAT user's moves impossible instead of unsafe,
which is not an improvement. So a link that fails for any reason OTHER than an
occupied destination falls back to reserving the destination with
`O_CREAT | O_EXCL` and renaming onto the reservation. `O_EXCL` gives the same
"create only if absent" guarantee in one operation -- the plan says so itself at
line 5353, where it is already the ruled primitive for the cross-volume branch --
so the fallback is fail-closed too. `FileExistsError` therefore never reaches it:
an occupied destination is an ANSWER, not a reason to try another way in.

**One honesty note about that.** `os.link` and `O_EXCL` were MEASURED returning
`EEXIST` against a case-twin and an NFC/NFD twin on APFS. The fallback exists for
exFAT, FAT32 and network mounts, which cannot be measured from here, so the claim
that it is fail-closed under THEIR folding is inferred: `O_EXCL` goes through the
same name lookup that lets `rename` find and overwrite the twin in the first
place, so a volume where one folds is a volume where the other does. Sound, and
not run.

The fallback loses only atomicity, never a file: a crash between the reservation
and the rename leaves an empty file at the destination and the person's file
untouched at the source.

**No numeric literal beyond 0 and 1 appears in this file.** The reservation's
permission bits are `stat`'s own names rather than an octal, which is what they
mean and also what keeps `test_no_number_beyond_zero_and_one_is_written_into_the_part_package`
true: a mode written `0o600` is a number this package invented.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


def move_onto_free_path(source: Path, destination: Path) -> None:
    """Move `source` to `destination`, or raise `FileExistsError`.

    Raises `FileExistsError` if anything is at `destination` under the VOLUME's
    own folding rules, whatever any constraint table declared. Any other
    `OSError` propagates: a filesystem that can neither hard-link nor create a
    file is an environment fault, not something to tell a person about their
    file, and inventing a result class for it would be inventing vocabulary.

    On success the source name is gone and the destination holds the bytes. The
    source name is removed only after the same inode is reachable at the
    destination, which is the property §7.11 actually states.
    """
    try:
        os.link(source, destination)
    except FileExistsError:
        raise
    except OSError:
        # No hard links here -- exFAT, FAT32, some network mounts. Reserve the
        # destination instead, which fails the same way when it is taken.
        # Owner-read/write and nothing else. The reservation survives exactly
        # one `os.rename` and is never the file the person ends up with.
        os.close(os.open(destination,
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                         stat.S_IRUSR | stat.S_IWUSR))
        try:
            os.rename(source, destination)
        except OSError:
            # The rename never happened, so the reservation is a file the
            # product created and nobody else has seen. Removing it is not
            # §7.11's case: it holds no bytes of the person's.
            os.unlink(destination)
            raise
        return
    os.unlink(source)

# src/readers/archive_zipfile.py
"""`read_manifest` backed by the standard library's `zipfile`.

**Why this exists.** `deployment.py` wired `read_manifest = _no_reader`, whose
docstring says *"this deployment ships no library for the format"*. For archives
that sentence was never true: `zipfile` is in the standard library. The cost was
the same as the `.docx` gap and had the same shape -- every `.zip` on a person's
disk recorded §2.4's `unsupported`, which is defined as *"no reader exists and the
bytes were never looked at"*, so downstream every count agreed those files carried
nothing. An archive is often where somebody's finished work lives.

**Without extraction, which §2.5 requires and which is also what makes it safe.**
`infolist` reads the central directory -- the index the archive keeps of itself --
and decompresses nothing. So a zip bomb is never expanded (the sizes here are what
the header CLAIMS, never what unpacking would produce), and a password-protected
member is listed by name without any attempt to decrypt it. That is the archive
form of the standing rule: marked and counted, never opened.

**What is library knowledge and what is not.** The archive type, the member paths,
the directory flag and the stated sizes are facts `zipfile` reads. How many members
are worth listing is not: it is a deployment budget, so `max_members` is injected
and has no default that silently truncates -- `None` means list them all, and a
truncated manifest always says so in `partial_reason`.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Callable

from extractors.archive import ArchiveManifest, ArchiveMember

#: §2.5's own word for the format, and the key `extractors.router` maps to the
#: `archive` family. Named rather than spelled twice.
ZIP: str = "zip"


def _member(info: zipfile.ZipInfo) -> ArchiveMember:
    """One entry, as the archive describes itself.

    `is_dir()` is `zipfile`'s reading of the entry -- the external attribute bits
    as well as the trailing separator -- rather than a check for a trailing "/"
    here, which would be this module guessing at something the library knows.

    `file_size` is the size the header STATES. It is not verified and cannot be
    without decompressing, which §2.5 forbids; it is carried because §2.5 asks
    for the uncompressed size and because a claimed size wildly larger than the
    archive is itself the signal a caller needs.
    """
    return ArchiveMember(path=info.filename, is_directory=info.is_dir(),
                         uncompressed_size=info.file_size)


def zipfile_reader(*, max_members: int | None = None,
                   ) -> Callable[[Path], ArchiveManifest]:
    """A `read_manifest` for zip archives.

    Returns a manifest in every case, never raises. §2.4 draws the line this
    depends on: `unsupported` means no reader existed, `failed` means a reader ran
    and could not read. A reader that raised would lose that distinction and
    report a damaged archive the same way as a format nobody shipped a library
    for.
    """

    def read_manifest(path: Path) -> ArchiveManifest:
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
        except zipfile.BadZipFile as problem:
            # §2.5's malformed case. The reason is the library's own words: it
            # names what it found, and a sentence composed here would be this
            # module's opinion about bytes it did not parse.
            return ArchiveManifest(archive_type=ZIP,
                                   unreadable_reason=f"malformed archive: {problem}")
        except OSError as problem:
            return ArchiveManifest(archive_type=ZIP,
                                   unreadable_reason=f"could not be opened: {problem}")

        total = len(infos)
        listed = infos if max_members is None else infos[:max_members]
        # The sum of what the members CLAIM, and only over the ones listed -- a
        # total covering members this manifest does not contain would be a number
        # nothing in it accounts for.
        stated = sum(info.file_size for info in listed)
        partial = None
        if len(listed) < total:
            partial = (f"listed the first {len(listed)} of {total} members; the "
                       "rest were not read")
        return ArchiveManifest(
            archive_type=ZIP,
            members=tuple(_member(info) for info in listed),
            uncompressed_size=stated,
            inspected=len(listed), total=total,
            unreadable_reason=None, partial_reason=partial)

    return read_manifest

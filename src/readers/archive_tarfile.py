# src/readers/archive_tarfile.py
"""`read_manifest` backed by the standard library's `tarfile` -- the tar family,
beside `readers.archive_zipfile.zipfile_reader`'s zip.

**Why this exists.** `104` §18.2 gap 14, item 2. §2.5's archive handler
(`extractors.archive.extract_archive`) has always taken an injected
`read_manifest` of any shape; `extractors.router.SOURCE_TYPE_BY_FORMAT` routed
only `zip` to it, so `.tar`, `.tgz`/`.tar.gz`, `.tbz2`/`.tar.bz2` and
`.txz`/`.tar.xz` reached no extractor at all, on a format the standard library
has read since before this deployment's python floor. 00:35: "Compressed
archives should yield their manifests without extraction" names no format, the
same posture `zip`'s own entry rests on.

**Without extraction, exactly as `zipfile_reader` is.** `getmembers()` walks
the archive's header blocks -- a tar carries no central directory, so listing
the manifest means reading through it, and reading through it is not opening a
member: `extractfile`/`extract` are never called, so no member's DATA is ever
decompressed or written anywhere. `mode="r:*"` picks the codec (plain, gzip,
bzip2, xz) from the STREAM's own bytes, the same auto-detection `tarfile`
itself performs and never from the path's extension -- gap 21's rule, inside
the reader as well as at the router.

**`7z` and `rar` are not here and are not coming.** Neither has a
standard-library reader; `router.py`'s own comment beside their absence says
why they stay unsupported by omission rather than by a key that would open them
and fail.
"""
from __future__ import annotations

import tarfile
from pathlib import Path
from typing import Callable

from extractors.archive import ArchiveManifest, ArchiveMember

#: §2.5's own word for the family, and the value every tar variant's manifest
#: carries in `ARCHIVE_TYPE_FIELD` -- one family, the same way `zipfile_reader`
#: writes `"zip"` for a `.zip` that turns out to be a `.docx` underneath. WHICH
#: codec compressed it is `extraction_routing.detected_format`'s answer
#: (`tar`/`tar.gz`/`tar.bz2`/`tar.xz`), not this field's.
TAR: str = "tar"


def _member(info: tarfile.TarInfo) -> ArchiveMember:
    """One entry, as the archive describes itself -- `zipfile_reader._member`'s
    tar twin. `info.size` is the header's OWN claim, uninflated by decompressing
    anything, for the same decompression-bomb reason `extractors.archive`'s
    docstring states for zip."""
    return ArchiveMember(path=info.name, is_directory=info.isdir(),
                         uncompressed_size=info.size)


def tarfile_reader(*, max_members: int | None = None,
                   ) -> Callable[[Path], ArchiveManifest]:
    """A `read_manifest` for the tar family: plain, gzip, bzip2, xz.

    Returns a manifest in every case, never raises -- §2.4's line, exactly as
    `zipfile_reader` draws it: `unsupported` means no reader existed (never
    reached here, since the router only sends a tar-family token), `failed`
    means a reader ran and could not read. A reader that raised would lose that
    distinction and report a damaged archive the same way as a format nobody
    shipped a library for.
    """

    def read_manifest(path: Path) -> ArchiveManifest:
        try:
            with tarfile.open(path, mode="r:*") as archive:
                infos = archive.getmembers()
        except tarfile.TarError as problem:
            # §2.5's malformed case, in the library's own words -- the same
            # phrasing `zipfile_reader` uses for `zipfile.BadZipFile`, so the two
            # archive families read the same on the screen.
            return ArchiveManifest(archive_type=TAR,
                                   unreadable_reason=f"malformed archive: {problem}")
        except OSError as problem:
            return ArchiveManifest(archive_type=TAR,
                                   unreadable_reason=f"could not be opened: {problem}")

        total = len(infos)
        listed = infos if max_members is None else infos[:max_members]
        # The sum of what the members CLAIM, over the ones listed only -- the
        # same rule `zipfile_reader` states for the same reason.
        stated = sum(info.size for info in listed)
        partial = None
        if len(listed) < total:
            partial = (f"listed the first {len(listed)} of {total} members; the "
                       "rest were not read")
        return ArchiveManifest(
            archive_type=TAR,
            members=tuple(_member(info) for info in listed),
            uncompressed_size=stated,
            inspected=len(listed), total=total,
            unreadable_reason=None, partial_reason=partial)

    return read_manifest

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
from typing import Callable, Sequence

from extractors.archive import (
    LOCKED_REASON_PREFIX, MARKER_KINDS, ArchiveManifest, ArchiveMarker,
    ArchiveMember,
)
from readers.text_documents import filename_marker_kind

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
        # Bit 0 of the general-purpose flag is the header's own statement that
        # the member is encrypted. It is read from the central directory like
        # every other fact here and decrypts nothing. §2.5: a password-protected
        # archive is "marked as unreadable ... rather than forced open", and the
        # standing rule is marked and counted, never opened -- so the names are
        # still listed (they are in clear) and the manifest says the contents
        # are not readable. Without this line a locked archive was indexed as
        # an ordinary one and nothing downstream could tell.
        encrypted = sum(1 for info in infos if info.flag_bits & 0x1)
        locked = (f"{LOCKED_REASON_PREFIX}: {encrypted} of {total} member(s) are "
                  "encrypted; names listed, contents not read"
                  if encrypted else None)
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
            unreadable_reason=locked, partial_reason=partial)

    return read_manifest


#: §2.5's two marker classes are `extractors/archive.py`'s (`MARKER_KINDS`); this is
#: the first of them, named rather than spelled here, so a rename over there is an
#: ImportError and not a silently unrecognised kind.
SOURCE_CODE_MANIFEST: str = MARKER_KINDS[0]


def manifest_marker_recognizer(
) -> Callable[[Sequence[str]], tuple[ArchiveMarker, ...]]:
    """`extract_archive`'s `recognize_markers`, from the manifest alone.

    **What was here before was `lambda names: ()`, and `104` §18.2 gap 17 counts it
    among four silent losses.** The reason it gave was true when it was written:
    §2.5's marker set is Deferred in P5's SPEC, and "a list invented here would be
    this deployment authoring the open half of somebody else's section". What it
    missed is that this deployment ALREADY HOLDS the answer for one of §2.5's two
    classes -- `readers/text_documents._MARKERS_BY_FILENAME` is catalogue 05, the
    package manifests and repository markers a tool requires by exact spelling --
    so the marker arm of `extract_archive` sat reachable and permanently empty over
    a table standing one module away. §2.5's own sentence is the one this answers:
    *"A source-code archive may reveal a `README.md`, `package.json`, `src`
    directory, or Python package layout and can be recognized as a code project."*

    **NOT A NEW LIST.** `filename_marker_kind` is one definition with two callers,
    which is what keeps a `package.json` on the disk and a `package.json` inside
    `submission.zip` from being two different opinions about the same tool. The
    re-kinding to `source-code manifest` is forced rather than chosen: §2.4 names
    four classes and §2.5 offers two, `MARKER_KINDS` is the vocabulary
    `extract_archive` validates against, and inventing a third is
    `UnknownMarkerKind` at run time. Catalogue 07 makes exactly this move and calls
    it "a naming stretch worth flagging" -- §2.5's README and `src` directory are
    not literally manifests -- and the flag is repeated here rather than quietly
    inherited.

    **WHAT §2.5's OWN SENTENCE NAMES AND THIS DOES NOT ANSWER: `src`, and "Python
    package layout".** Neither `src` nor `__init__.py` is in catalogue 05, so neither
    is recognised here, and `test_a_source_code_manifest_inside_an_archive_is_
    recognized` pins `project/src/index.js` as unrecognised on purpose. Adding them
    would be the second list the paragraph above has just refused, and it would be a
    claim about DIRECTORY SHAPE rather than about filenames a tool requires by exact
    spelling -- a different kind of statement, which is why catalogue 05 does not
    carry it either. Open with a reason beats closed by invention.

    **§2.5's SECOND CLASS IS DEFERRED AND STAYS DEFERRED, WITH ITS REASON.**
    `document name` would be §2.5's five English words -- transcript, personal
    statement, resume, certificate, form -- matched against member basenames. That
    is a word list deciding an outcome, which this build does not write, and
    catalogue 07 itself rates the last of the five `high` false-positive risk
    (`form` is inside `format`, `formula`, `information`, `transformation`).
    Nothing is lost SILENTLY by the deferral, which is the distinction §18.2 draws:
    every member path is already stored as its own observation by
    `extract_archive`'s manifest arm, so a `transcript.pdf` inside a zip is on the
    record either way. What the missing class would add is a LABEL, and §2.5's own
    worked example turns on five documents CO-OCCURRING, which is a purpose fact
    (§3.9) and P6's to reach, not a marker's.

    **Manifest only, never extraction.** Every path here comes from the central
    directory `read_manifest` already read; nothing is decompressed, so §2.5's
    absolute prohibition is not touched by a line of this.
    """

    def recognize_markers(member_paths: Sequence[str]) -> tuple[ArchiveMarker, ...]:
        found: list[ArchiveMarker] = []
        for member_path in member_paths:
            # The member's own basename. A directory entry ends in a separator and
            # the `rstrip` is what removes it -- `PurePosixPath("src/").name` is
            # the empty string, so `src/` would silently never be looked at.
            basename = str(member_path).rstrip("/").rsplit("/", 1)[-1]
            if not basename:
                continue
            if filename_marker_kind(basename) is not None:
                found.append(ArchiveMarker(member_path=member_path,
                                           kind=SOURCE_CODE_MANIFEST))
        return tuple(found)

    return recognize_markers

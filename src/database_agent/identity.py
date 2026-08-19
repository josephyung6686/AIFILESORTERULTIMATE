"""Contract out §1 — identity rules R1–R5 (§8.2).

R1 the content hash is the stable identity of a file *version*.
R4 the file record's identity is not its path.
R5 P1 supplies the identity half of §3.4's cache key — content hash — and nothing else.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path

HASH_ALGORITHM = "sha256"   # I2: matches P4's observation_key formula (§3.4 keys on this)
_CHUNK = 1024 * 1024

#: Minted once per process. It tags the volume identifier so that a value observed
#: in a different process cannot compare equal to one observed here. See OQ9 below.
OBSERVATION_SESSION = str(uuid.uuid4())


class DatalessFileRefused(Exception):
    """11-ops-runtime.md §5 — opening a dataless iCloud item downloads it.

    P3 detects a dataless / not-downloaded ubiquitous item BEFORE hashing. P1 has
    no ubiquity API and invents no detection heuristic; it refuses to open bytes
    the caller has not declared local.
    """


def hash_file(path: Path, *, materialized: bool) -> str:
    """Content hash of a file's bytes, streamed. 64 hex chars.

    `materialized` is the caller's declaration that P3's dataless check has run and
    the bytes are on disk (11-ops-runtime.md §5). It is required, with no default,
    so that no caller reaches P1's bytes without having made that check.
    """
    if not materialized:
        raise DatalessFileRefused(
            f"{path} was not declared materialized; P3 detects dataless items before "
            "hashing and P1 does not download them (11-ops-runtime.md §5)"
        )
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def volume_id_for(path: Path) -> str:
    """§8.2's 'Filesystem volume or root identifier'.

    OPEN — P1 OQ9, and this plan does NOT close it. `st_dev` is not stable across
    remount, volume rename, or cloud re-sync on macOS, so P12's §8.3 cross-volume
    copy-and-delete would misfire if two values recorded in different sessions were
    compared as equal.

    The value is therefore prefixed with OBSERVATION_SESSION, which is minted once
    per process. Within one process the comparison behaves exactly as a volume
    identifier should; across processes it can never accidentally match, so no
    cross-session decision can be built on it. `files.volume_id` is nullable for the
    same reason. When OQ9 closes with a stable identifier, drop the prefix — the
    column name and every consumer stay as they are.
    """
    return f"{OBSERVATION_SESSION}:{os.stat(path).st_dev}"

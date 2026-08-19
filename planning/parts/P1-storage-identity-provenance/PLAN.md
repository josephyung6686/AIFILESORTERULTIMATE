# P1 — Storage, Identity, Provenance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the SQLite substrate every other part writes through — content-hash file identity, an append-only provenance log with a registration rule, supersede-never-overwrite, four fixity verification points, and three small stores (learning projection, budget config, vector arrays).

**Architecture:** One local SQLite database (§0), stdlib `sqlite3`, no ORM. Nine modules, one per published surface in [`SPEC.md`](SPEC.md)'s Contract out. P1 records and returns; it interprets nothing. Append-only is enforced by SQL triggers, not by convention, so a bug in a *neighbouring* part cannot mutate history.

**Tech Stack:** Python 3.12 · stdlib `sqlite3` · `pytest` · `hashlib` (SHA-256) · no third-party runtime dependencies.

## Global Constraints

Every task's requirements implicitly include these. Values are copied verbatim from `SPEC.md`.

- **One local SQLite database** (§0), transactional, durably committed, inspectable. Each part owns its own tables within it.
- **`events` is INSERT-only** (R6, §8.2): "No `UPDATE`, no `DELETE`, no row rewrite, no truncation, no compaction that drops rows. A correction to an event is a new event, not an edit."
- **The spelling is `supersede_reason`.** `supersession_reason` is not an alias and is not accepted (M1).
- **`preferred` is not P1's column.** It is published by name and carried on P6's `file_facts` only (M1). P1 creates no `preferred` column.
- **No vectors in `files` or `events`** (§0). The array store is a separate table.
- **No interpretation leaked** (Done-means 8): P1's code contains no fact-field name, domain name, template name, sensitivity class, or tier name. The §8.6 ceiling keys and the nineteen reserved event names are the only permitted vocabulary, because both are stated literally by the design.
- **P1 decides nothing.** It performs and records: no learning, no weighting, no enforcement of ceilings, no similarity function, no stale/undo judgement.
- **P1 authors nothing** (SPEC Cross-cutting answers → Provenance, M8): *"The acting part authors; P1 writes. P1 appends no event on its own initiative."* Every P1 function that appends takes the authoring part as a required `author` argument supplied by its caller, and writes that value into `subsystem`. There is no default. The one documented exception is V1–V4, where the SPEC itself fixes `subsystem = "P1"` because P1 *performs* the comparison — and even there the caller must name itself, because the decision that a verification was due is never P1's.
- **P1 supplies no value another part owns.** MIME type, detected format and scan state arrive from P3 (Contract in); P1 stores what it is handed and guesses nothing. The only `scan_state` value P1 itself writes is `superseded_content`, which SPEC OQ1 ratifies by name.
- **Nineteen reserved event names, verbatim from §8.2** — see Task 5.
- **Event types are frozen at build time, never minted at run time** (SPEC Contract out §3, rule 4): *"Registration is a spec-level act, not a runtime one: a type declared in no SPEC does not exist, and a part cannot mint one at run time."* P1 ships one frozen table compiled from the SPECs. There is no `register_event_type` call, no mutable registry, and no code path that adds a type after import.
- **The database is never inside a corpus.** [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §2: the SQLite file lives under `~/Library/Application Support/` and is *"never created inside a scan root, a candidate root, or the destination tree."*
- **P1 never opens a dataless iCloud file.** [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §5: P3 detects a dataless / not-downloaded ubiquitous item **before** hashing, and P1 must not be the path that materializes one. P1's hashing entry points refuse a path a caller has not declared materialized.
- **Python 3.12.** Pin it; do not assume a newer runtime.

---

## File Structure

```text
pyproject.toml                          project metadata, pytest config, Python 3.12 pin
src/database_agent/__init__.py          package marker; exports open_database
src/database_agent/db.py                Contract out §6 — handle, schema, transaction boundary
src/database_agent/identity.py          Contract out §1 — content hash, R1–R6
src/database_agent/files_table.py       Contract out §2 — files row + five history read surfaces
src/database_agent/events.py            Contract out §3 — append-only log, writer, registration rule
src/database_agent/supersede.py         Contract out §4 — the three shared columns + chain rules
src/database_agent/verify.py            Contract out §5 — V1–V4 fixity
src/database_agent/learning.py          Contract out §7 — §8.7 scoped projection over events
src/database_agent/budget.py            Contract out §8 — §8.6 fifteen-key config object
src/database_agent/vectors.py           Contract out §9 — §0 opaque array store
src/database_agent/scan_usage.py        Contract out §10 — §8.6's six per-scan resource counters

tests/conftest.py                       shared fixtures: temp db, sample files
tests/test_identity.py                  Done-means 1, 2, 3
tests/test_files_table.py               Done-means 1, 2, 9
tests/test_events.py                    Done-means 4, 7, 11, 12
tests/test_supersede.py                 Done-means 5
tests/test_verify.py                    Done-means 6, 10
tests/test_learning.py                  Done-means 13
tests/test_budget.py                    Done-means 14
tests/test_vectors.py                   Done-means 15
tests/test_scan_usage.py                Done-means 16
tests/test_no_interpretation.py         Done-means 8 (grep-style source scan)
```

Files split by published surface, not by technical layer — each module is one Contract-out section, so a reviewer can reject one without touching its neighbours.

---

### Task 1: Project skeleton and database handle

**Files:**
- Create: `pyproject.toml`
- Create: `src/database_agent/__init__.py`
- Create: `src/database_agent/db.py`
- Create: `tests/conftest.py`
- Test: `tests/test_db.py`

**Interfaces:**
- Consumes: nothing — this is the substrate.
- Produces: `open_database(path: Path, *, scan_roots: Iterable[Path] = ()) -> sqlite3.Connection`, `default_database_path(bundle_id: str) -> Path`, `DatabaseInsideCorpus`, `SCHEMA_VERSION: int`, `transaction(conn)` contextmanager.

**Binding [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §2.** The database lives under `~/Library/Application Support/`, in a directory named by the application's bundle identifier, as `agent.sqlite`, and is *"never created inside a scan root, a candidate root, or the destination tree."* Two consequences for this task:

- `default_database_path` takes the bundle identifier as an argument. **Unresolved:** `11-ops-runtime.md` §2 does not name the identifier, and P1 must not invent one — the application that launches P1 (P13, per `11` §1) supplies it. P1 composes the path and nothing else.
- `open_database` refuses when the resolved database path is inside any root the caller declares. P1 cannot know the roots on its own — P3 owns them (§1.1) — so they are a caller-supplied argument, and a caller that supplies none gets today's behaviour. The refusal is what makes `11` §2's rule enforceable rather than advisory.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_db.py
import sqlite3
from pathlib import Path

import pytest

from database_agent.db import (
    DatabaseInsideCorpus, default_database_path, open_database, transaction,
)


def test_default_location_is_application_support(tmp_path: Path):
    # 11-ops-runtime.md §2: Application Support / bundle identifier / agent.sqlite
    path = default_database_path("example.bundle.identifier")
    assert path.parts[-4:] == ("Library", "Application Support",
                               "example.bundle.identifier", "agent.sqlite")
    assert path.is_absolute()


def test_database_is_refused_inside_a_scan_root(tmp_path: Path):
    # 11-ops-runtime.md §2: never created inside a scan root, a candidate root,
    # or the destination tree. P3's exclusion rules never have to special-case it.
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    with pytest.raises(DatabaseInsideCorpus):
        open_database(corpus / "agent.sqlite", scan_roots=[corpus])


def test_database_outside_every_declared_root_is_allowed(tmp_path: Path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    conn = open_database(tmp_path / "support" / "agent.sqlite", scan_roots=[corpus])
    conn.close()


def test_open_database_creates_one_file(tmp_path: Path):
    db_path = tmp_path / "agent.sqlite"
    conn = open_database(db_path)
    assert db_path.exists()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_foreign_keys_are_enforced(tmp_path: Path):
    conn = open_database(tmp_path / "agent.sqlite")
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_transaction_rolls_back_on_error(tmp_path: Path):
    conn = open_database(tmp_path / "agent.sqlite")
    conn.execute("CREATE TABLE t (x INTEGER)")
    conn.commit()
    try:
        with transaction(conn):
            conn.execute("INSERT INTO t VALUES (1)")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert conn.execute("SELECT count(*) FROM t").fetchone()[0] == 0
    conn.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_db.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent'`

- [ ] **Step 3: Write pyproject.toml**

```toml
[project]
name = "database-agent"
version = "0.1.0"
requires-python = "==3.12.*"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Step 4: Write the database handle**

```python
# src/database_agent/db.py
"""Contract out §6 — one local SQLite database, transactional and inspectable (§0)."""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 1


class DatabaseInsideCorpus(Exception):
    """11-ops-runtime.md §2 — the database is never created inside a scanned root."""


def default_database_path(bundle_id: str) -> Path:
    """11-ops-runtime.md §2 — Application Support / bundle identifier / agent.sqlite.

    The bundle identifier is NOT specified by `11` and is not invented here: the
    application that launches P1 supplies it. P1 composes the path and nothing else.
    """
    return Path.home() / "Library" / "Application Support" / bundle_id / "agent.sqlite"


def open_database(path: Path, *, scan_roots: Iterable[Path] = ()) -> sqlite3.Connection:
    """Open (creating if absent) the single local database (§0).

    `scan_roots` are the roots the caller has selected (P3 owns them, §1.1). The
    database may not live inside any of them (11-ops-runtime.md §2), so P3's
    exclusion rules never have to special-case it.
    """
    resolved = path.expanduser().resolve()
    for root in scan_roots:
        root = Path(root).expanduser().resolve()
        if resolved == root or root in resolved.parents:
            raise DatabaseInsideCorpus(
                f"{resolved} is inside the declared root {root}; the database is "
                "never created inside a scan root (11-ops-runtime.md §2)"
            )
    path = resolved
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    """Explicit transaction boundary. P1 publishes this; each part owns its tables."""
    conn.execute("BEGIN")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")
```

```python
# src/database_agent/__init__.py
"""P1 — storage, identity, provenance. The substrate every other part writes through."""
from database_agent.db import (
    SCHEMA_VERSION, default_database_path, open_database, transaction,
)

__all__ = ["open_database", "default_database_path", "transaction", "SCHEMA_VERSION"]
```

```python
# tests/conftest.py
from pathlib import Path

import pytest

from database_agent.db import open_database


@pytest.fixture()
def conn(tmp_path: Path):
    c = open_database(tmp_path / "agent.sqlite")
    yield c
    c.close()


@pytest.fixture()
def sample_file(tmp_path: Path) -> Path:
    p = tmp_path / "corpus" / "Syllabus.pdf"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"the quick brown fox")
    return p
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_db.py -v`
Expected: PASS — 6 passed

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml src/database_agent/__init__.py src/database_agent/db.py tests/conftest.py tests/test_db.py
git commit -m "feat(P1): SQLite handle, schema version, transaction boundary"
```

---

### Task 2: Content-hash identity (R1–R5)

**Files:**
- Create: `src/database_agent/identity.py`
- Test: `tests/test_identity.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `HASH_ALGORITHM: str`, `hash_file(path: Path, *, materialized: bool) -> str`, `DatalessFileRefused`, `volume_id_for(path: Path) -> str`, `OBSERVATION_SESSION: str`.

**P1 OQ9 stays OPEN — the volume identifier is not persisted as a cross-session value.** The SPEC's OQ9 asks *"How is the volume or root identifier derived, and is it stable?"* and answers it nowhere; §8.3 names cloud-synced directories as externally mutable and subject to sync agents renaming and replacing files, and on macOS `st_dev` changes across a remount. The previous version of this task documented that danger and then stored `st_dev` `NOT NULL` on every `files` row, which is the worst of both — P12's §8.3 cross-volume copy-and-delete would compare two `st_dev` values recorded weeks apart and silently conclude "same volume".

This plan does not close OQ9 and does not pick a stable identifier. It makes the unstable one **unusable across sessions instead of quietly wrong**: `volume_id_for` returns the raw `st_dev` prefixed with a token minted once per process, and `files.volume_id` is **nullable**. Two rows observed in one process compare equal on the same volume, which is all any within-session caller needs; a row written last week never compares equal to one written today, so a cross-session decision fails loudly rather than misfiring. When OQ9 closes with a real identifier, the prefix is removed and the column keeps its name.

**Binding [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §5 — dataless iCloud files.** *"Hashing or opening them downloads the file… P3 detects a dataless / not-downloaded ubiquitous item **before** hashing. Do not materialize, hash, or extract."* P1 has no way to detect one without inventing a macOS ubiquity API binding, and `11` assigns detection to P3 — so `hash_file` takes `materialized` as a **required keyword** and refuses when it is false. The flag is the seam: a caller that has not run P3's detection cannot reach P1's bytes by accident.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_identity.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_identity.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.identity'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/identity.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_identity.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/identity.py tests/test_identity.py
git commit -m "feat(P1): content-hash identity, streamed, with recorded algorithm"
```

---

### Task 3: The `files` table and record creation (Done-means 1)

**Files:**
- Create: `src/database_agent/files_table.py`
- Modify: `src/database_agent/db.py` — add `files` DDL to `create_schema`
- Test: `tests/test_files_table.py`

**Interfaces:**
- Consumes: `hash_file`, `volume_id_for` (Task 2); `open_database`, `transaction` (Task 1).
- Produces: `create_schema(conn)`, `FILES_COLUMNS: tuple[str, ...]`, `record_file(conn, path, *, parent_folder_context, mime_type, detected_format, scan_state, materialized) -> str` returning `file_id`, `get_file(conn, file_id) -> sqlite3.Row`.

**Note on `directory_position`:** the published field name is §2.9's **parent-folder context**; `directory_position` is the physical column spelling only (MINOR 11). There is exactly one field. The keyword argument uses the published name; the column uses §1.2's word.

**P1 supplies no value P3 owns.** SPEC Contract in: P3 hands P1 *"the §1.2 per-file fields — filename, normalized filename, extension, MIME type, parent-folder context …, scan state"*, and P1's obligation is *"store them"*. `mime_type`, `detected_format` and `scan_state` are therefore required keyword arguments with no default and no fallback. The previous version of this task called `mimetypes.guess_type`, hard-coded `detected_format=None` and invented the `scan_state` value `"recorded"`, which is P1 interpreting a file — and `"recorded"` is a value no SPEC defines, so Done-means 8's forbidden-term scan would never have caught it. Filename, normalized filename and extension are derived from the path itself, which is mechanics, not vocabulary.

**`volume_id` is nullable** (Task 2, P1 OQ9). A caller with no usable volume identifier stores `NULL`; no P1 read treats `NULL` as a match.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_files_table.py
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import FILES_COLUMNS, get_file, record_file


def _p3_fields(**overrides):
    """The §1.2 fields P3 hands P1 (SPEC Contract in). A test stands in for P3;
    P1 never derives any of these itself."""
    fields = dict(parent_folder_context="corpus", mime_type="application/pdf",
                  detected_format="pdf", scan_state="scanned", materialized=True)
    fields.update(overrides)
    return fields


def test_record_file_writes_every_column(conn, sample_file: Path):
    create_schema(conn)
    file_id = record_file(conn, sample_file, **_p3_fields())
    row = get_file(conn, file_id)
    for column in FILES_COLUMNS:
        assert column in row.keys(), f"missing column {column}"
    assert row["content_hash"]
    assert row["hash_algorithm"]
    assert row["volume_id"]
    assert row["current_path"] == str(sample_file)
    assert row["filename"] == "Syllabus.pdf"
    assert row["extension"] == ".pdf"
    assert row["directory_position"] == "corpus"
    # stored exactly as handed over — P1 derives none of these
    assert row["mime_type"] == "application/pdf"
    assert row["detected_format"] == "pdf"
    assert row["scan_state"] == "scanned"


def test_p3_supplied_fields_have_no_defaults(conn, sample_file: Path):
    # Contract in: P3 supplies MIME type, detected format and scan state. P1 stores
    # them; it does not guess them. Omitting one is a TypeError, not a silent guess.
    create_schema(conn)
    with pytest.raises(TypeError):
        record_file(conn, sample_file, parent_folder_context="corpus")


def test_volume_id_is_nullable(conn, sample_file: Path):
    # P1 OQ9 is open; a caller with no usable volume identifier stores NULL rather
    # than a value a later session could compare against.
    create_schema(conn)
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, volume_id, content_hash, hash_algorithm, observed_size, "
        "observed_timestamps, scan_state) "
        "VALUES ('f-null', '/x', 'x', 'x', '', NULL, 'h', 'sha256', 1, '{}', 'scanned')"
    )
    assert get_file(conn, "f-null")["volume_id"] is None


def test_files_table_holds_no_vectors(conn):
    create_schema(conn)
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(files)")]
    for forbidden in ("embedding", "vector", "array"):
        assert not any(forbidden in c.lower() for c in cols)


def test_no_preferred_column_on_p1_tables(conn):
    # M1: `preferred` is carried on P6's file_facts only. P1 creates no such column.
    create_schema(conn)
    for table in ("files", "events"):
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        assert "preferred" not in cols
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_files_table.py -v`
Expected: FAIL with `ImportError: cannot import name 'create_schema'`

- [ ] **Step 3: Add the schema function to db.py**

Append to `src/database_agent/db.py`:

```python
FILES_DDL = """
CREATE TABLE IF NOT EXISTS files (
    file_id                   TEXT PRIMARY KEY,
    current_path              TEXT NOT NULL,
    filename                  TEXT NOT NULL,
    normalized_filename       TEXT NOT NULL,
    extension                 TEXT NOT NULL,
    directory_position        TEXT,
    volume_id                 TEXT,          -- nullable: P1 OQ9 is OPEN (Task 2)
    content_hash              TEXT NOT NULL,
    hash_algorithm            TEXT NOT NULL,
    observed_size             INTEGER NOT NULL,
    observed_timestamps       TEXT NOT NULL,
    mime_type                 TEXT,
    detected_format           TEXT,
    scan_state                TEXT NOT NULL,
    extraction_status_by_tier TEXT NOT NULL DEFAULT '{}',
    sensitivity_state         TEXT
);
CREATE INDEX IF NOT EXISTS files_content_hash ON files (content_hash);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    """Create every P1-owned table. Idempotent."""
    conn.executescript(FILES_DDL)
```

- [ ] **Step 4: Write files_table.py**

```python
# src/database_agent/files_table.py
"""Contract out §2 — the `files` row: the union of §8.2's file record and §1.2's per-file record."""
from __future__ import annotations

import json
import sqlite3
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path

from database_agent.identity import HASH_ALGORITHM, hash_file, volume_id_for

FILES_COLUMNS: tuple[str, ...] = (
    "file_id", "current_path", "filename", "normalized_filename", "extension",
    "directory_position", "volume_id", "content_hash", "hash_algorithm",
    "observed_size", "observed_timestamps", "mime_type", "detected_format",
    "scan_state", "extraction_status_by_tier", "sensitivity_state",
)


def _timestamps(path: Path) -> str:
    stat = path.stat()
    return json.dumps({
        "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "ctime": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
    })


def record_file(conn: sqlite3.Connection, path: Path, *,
                parent_folder_context: str | None,
                mime_type: str | None,
                detected_format: str | None,
                scan_state: str,
                materialized: bool) -> str:
    """Create the `files` row (Contract out §2).

    `mime_type`, `detected_format` and `scan_state` are P3's (Contract in: "store
    them"). They are required with no default: P1 does not sniff a MIME type, does
    not detect a format, and does not invent a scan state. `parent_folder_context`
    is §2.9's published name, stored in the `directory_position` column (§1.2's
    word) — one field, not two (MINOR 11).

    `materialized` is passed through to `hash_file` (11-ops-runtime.md §5).
    """
    file_id = str(uuid.uuid4())
    stat = path.stat()
    conn.execute(
        f"INSERT INTO files ({','.join(FILES_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(FILES_COLUMNS))})",
        (
            file_id, str(path), path.name,
            unicodedata.normalize("NFC", path.name), path.suffix,
            parent_folder_context, volume_id_for(path),
            hash_file(path, materialized=materialized), HASH_ALGORITHM,
            stat.st_size, _timestamps(path),
            mime_type, detected_format,
            scan_state, "{}", None,
        ),
    )
    return file_id


def get_file(conn: sqlite3.Connection, file_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_files_table.py -v`
Expected: PASS — 5 passed

- [ ] **Step 6: Commit**

```bash
git add src/database_agent/db.py src/database_agent/files_table.py tests/test_files_table.py
git commit -m "feat(P1): files table and record creation, no vectors, no preferred column"
```

---

### Task 4: Append-only `events` enforced by trigger (Done-means 4, 7)

**Files:**
- Modify: `src/database_agent/db.py` — add `EVENTS_DDL`
- Create: `src/database_agent/events.py`
- Test: `tests/test_events.py`

**Interfaces:**
- Consumes: `create_schema`, `transaction`.
- Produces: `EVENT_FIELDS: tuple[str, ...]` (the eleven §8.2 fields), `CORRECTION_FIELDS: tuple[str, ...]` (the §8.7 columns), `append_event(conn, **fields) -> int`.

**The §8.7 columns are not §8.2 fields.** SPEC Contract out §3 already carries `correction_scope` beside §8.2's eleven, and SPEC Contract out §10 states the rule explicitly: *"§8.2's event record keeps its eleven fields (MINOR 1) and Done-means 7 still tests exactly eleven."* Four more §8.7 columns land here for the same reason `correction_scope` did — the learning store cannot answer its own published read without them:

```text
correction_subject   the subject the correction is about, at correction_scope   §8.7
polarity             opaque; accept | reject, supplied by the acting part       §8.7
proposal_class       opaque; supplied by the acting part                        10-i4-learning-ops.md
basis_key            opaque; supplied by the acting part                        10-i4-learning-ops.md
```

`polarity`, `proposal_class` and `basis_key` are the **three opaque fields** SPEC Contract out §7 names: the store returns each record *"with its §8.2 `explanation`, `polarity`, `proposal_class`, `basis_key`, and evidence reference"*, and *"P1 stores and returns all three and decides nothing from them."*

`polarity ∈ accept | reject` is supplied by the acting part and **never derived by P1** — not from the event type, not from the explanation, not from anything. It exists because §8.7's *"rejected groups, rejected destination matches, rejected labels, and rejected residual recommendations"* have to be distinguishable from approvals **on read**: [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)'s query-before-propose rule fires on an unreset **reject**, so without the column all six reader parts would parse `explanation` free text to tell one from the other. A misread there either suppresses a valid proposal or resurfaces an already-rejected grouping, which is the failure §8.7 names by name. `proposal_class` and `basis_key` carry the equivalence rule in the same document. `correction_subject` is argued for in Task 9.

`EVENT_FIELDS` stays exactly eleven and Done-means 7 keeps testing eleven: all four of these are §8.7 columns like `correction_scope`, not §8.2 event-record fields.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_events.py
import sqlite3

import pytest

from database_agent.db import create_schema
from database_agent.events import CORRECTION_FIELDS, EVENT_FIELDS, append_event


def _minimal(**overrides):
    row = dict(
        event_type="discovery", file_id="f1", content_hash="abc",
        subsystem="P3", component_version="p3-fixture",
        observed_at="2026-08-19T00:00:00+00:00", explanation="fixture",
    )
    row.update(overrides)
    return row


def test_there_are_exactly_eleven_event_fields():
    # §8.2's event record, MINOR 1. The §8.7 columns are separate and do not count.
    assert len(EVENT_FIELDS) == 11
    assert not set(EVENT_FIELDS) & set(CORRECTION_FIELDS)


def test_event_carries_the_eleven_fields(conn):
    create_schema(conn)
    event_id = append_event(conn, **_minimal())
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    for field in EVENT_FIELDS:
        assert field in row.keys()
    # "where applicable" fields legitimately empty (Done-means 7) ...
    assert row["old_path"] is None
    assert row["new_path"] is None
    assert row["prompt_fingerprint"] is None
    assert row["user_id"] is None
    # ... and every other field populated. component_version is not optional.
    for field in EVENT_FIELDS:
        if field in ("old_path", "new_path", "prompt_fingerprint", "user_id"):
            continue
        assert row[field] is not None, f"Done-means 7: {field} must be populated"


def test_update_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE events SET explanation = 'rewritten'")


def test_delete_against_events_fails(conn):
    create_schema(conn)
    append_event(conn, **_minimal())
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM events")


def test_a_correction_is_a_new_event_not_an_edit(conn):
    create_schema(conn)
    append_event(conn, **_minimal(explanation="first"))
    append_event(conn, **_minimal(explanation="corrected"))
    rows = conn.execute("SELECT explanation FROM events ORDER BY event_id").fetchall()
    assert [r["explanation"] for r in rows] == ["first", "corrected"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_events.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.events'`

- [ ] **Step 3: Add EVENTS_DDL to db.py and append it in create_schema**

```python
EVENTS_DDL = """
CREATE TABLE IF NOT EXISTS events (
    event_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type         TEXT NOT NULL,
    base_event_type    TEXT,
    file_id            TEXT,
    content_hash       TEXT,
    old_path           TEXT,
    new_path           TEXT,
    subsystem          TEXT NOT NULL,
    component_version  TEXT,
    prompt_fingerprint TEXT,
    user_id            TEXT,
    observed_at        TEXT NOT NULL,
    explanation        TEXT,
    -- §8.7 columns. Not among §8.2's eleven fields (MINOR 1); on user-action events only.
    correction_scope   TEXT,
    correction_subject TEXT,
    polarity           TEXT,
    proposal_class     TEXT,
    basis_key          TEXT
);
CREATE TRIGGER IF NOT EXISTS events_no_update
BEFORE UPDATE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only (R6, 8.2)'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete
BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'events is append-only (R6, 8.2)'); END;
"""
```

Change `create_schema` to run both scripts:

```python
def create_schema(conn: sqlite3.Connection) -> None:
    """Create every P1-owned table. Idempotent."""
    conn.executescript(FILES_DDL)
    conn.executescript(EVENTS_DDL)
```

- [ ] **Step 4: Write events.py**

```python
# src/database_agent/events.py
"""Contract out §3 — the append-only provenance log (§8.2).

Append-only means INSERT only: no UPDATE, no DELETE, no row rewrite, no truncation,
no compaction that drops rows (R6). Enforced by trigger, not by convention.
"""
from __future__ import annotations

import sqlite3

#: §8.2's eleven event-record fields. Exactly eleven, forever (MINOR 1).
EVENT_FIELDS: tuple[str, ...] = (
    "event_type", "file_id", "content_hash", "old_path", "new_path",
    "subsystem", "component_version", "prompt_fingerprint", "user_id",
    "observed_at", "explanation",
)

#: §8.7 columns, carried beside the eleven on user-action events. P1 stores them
#: opaquely: it derives no polarity, compares no basis_key, interprets no
#: proposal_class. polarity ∈ accept | reject and is supplied by the acting part.
CORRECTION_FIELDS: tuple[str, ...] = (
    "correction_scope", "correction_subject", "polarity", "proposal_class", "basis_key",
)

_WRITABLE = (*EVENT_FIELDS, *CORRECTION_FIELDS, "base_event_type")


def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id.

    `subsystem` is the authoring part (§8.2 "the responsible subsystem"). P1 never
    fills it in: the acting part authors, P1 writes (M8).
    """
    columns = [k for k in fields if k in _WRITABLE]
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_events.py -v`
Expected: PASS — 5 passed

- [ ] **Step 6: Commit**

```bash
git add src/database_agent/db.py src/database_agent/events.py tests/test_events.py
git commit -m "feat(P1): append-only events log enforced by trigger"
```

---

### Task 5: The frozen event-type table (Done-means 11, 12)

**Files:**
- Modify: `src/database_agent/events.py` — add the reserved nineteen, the frozen registered table, and writer validation
- Test: `tests/test_events.py` — extend

**Interfaces:**
- Consumes: `append_event` (Task 4).
- Produces: `RESERVED_EVENT_TYPES: frozenset[str]`, `REGISTERED_EVENT_TYPES: Mapping[str, str | None]`, `EVENT_TYPES: Mapping[str, str | None]`, `UnregisteredEventType`.

**Registration is a spec-level act, so the table is frozen at import.** SPEC Contract out §3, rule 4: *"Registration is a spec-level act, not a runtime one: a type declared in no SPEC does not exist, and a part cannot mint one at run time."* There is therefore **no `register_event_type` function**. The previous version of this task shipped a process-local `dict` that any caller could mutate — which meant a type existed only in the process that added it, appends started failing after a restart, and a direct write to the dict bypassed the reserved-name check entirely. The table below is compiled from the declaring SPECs and is a read-only mapping; rule 1 (no reserved name is redefined) is checked once at import, so a collision is an import error rather than a runtime rejection.

**Where each name comes from.** Rule 2: *"Every other event type is declared by the part that authors it, in that part's own SPEC. The declaration is the definition."* So every name here is copied from the SPEC that declares it, and none is coined here:

| Declaring part | Count | Source |
|---|---|---|
| §8.2 reserved | 19 | P1 [`SPEC.md`](SPEC.md) Contract out §3, verbatim |
| P7 | 8 | [`../P7-privacy-consent-gate/SPEC.md`](../P7-privacy-consent-gate/SPEC.md) Cross-cutting answers → Provenance |
| P8 | 5 | [`../P8-llm-harness-validator/SPEC.md`](../P8-llm-harness-validator/SPEC.md) §8 "Events appended" |
| P13 | 3 | [`../P13-review-approval-surface/SPEC.md`](../P13-review-approval-surface/SPEC.md) Cross-cutting answers → Provenance |
| P11 | 8 | **unspelled — see below** |

**P11's eight are declared but not spelled, so P1 cannot register them.** P1's SPEC records that P11 declares eight *"typed specializations of the reserved `placement recommendation`"*, and adds that *"the names live in the declaring spec, not here."* [`../P11-placement-residual/SPEC.md`](../P11-placement-residual/SPEC.md) Cross-cutting answers → Provenance declares them as eight prose descriptions — "candidate destination retrieval performed", "group plan emitted", "residual set surfaced; residual set-level decision recorded" — and publishes **no identifiers**. P1 cannot turn a prose description into a stored value without choosing a spelling P11 never published, which is exactly the two-vocabularies failure this project has already hit. The eight are therefore **absent from the frozen table**, the writer rejects them today, and the missing spellings are recorded as a SPEC gap against P11 rather than papered over. Done-means 11's specialization clause is provable the day P11's SPEC prints eight identifiers; the `base_event_type` mechanism is built and tested here so nothing but the names is missing.

The writer's union is therefore **35 names today** (19 + 8 + 5 + 3) and 43 when P11 publishes — which is the count P1's SPEC states.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_events.py`:

```python
from database_agent.events import (
    EVENT_TYPES, REGISTERED_EVENT_TYPES, RESERVED_EVENT_TYPES, UnregisteredEventType,
)


def test_the_nineteen_reserved_names_are_present():
    assert len(RESERVED_EVENT_TYPES) == 19
    for name in ("discovery", "stat observation", "hashing", "extraction", "OCR",
                 "undo", "external modification detection", "planned move"):
        assert name in RESERVED_EVENT_TYPES


def test_registered_names_never_shadow_a_reserved_name():
    # Rule 1: the nineteen may not be redefined, narrowed, or reused.
    assert not set(REGISTERED_EVENT_TYPES) & set(RESERVED_EVENT_TYPES)


def test_the_registered_table_matches_the_declaring_specs():
    # Rule 2: the declaration is the definition, and it lives in the authoring
    # part's SPEC. Counts are P1 SPEC Contract out §3's table.
    p7 = {"classification_assigned", "classification_superseded", "policy_set",
          "consent_granted", "consent_revoked", "model_release",
          "model_release_denied", "consent_requested"}
    p8 = {"model_call_issued", "model_response_received", "validation_verdict",
          "verdict_superseded", "call_refused"}
    p13 = {"review presentation", "review action routed", "apply review approval"}
    assert len(p7) == 8 and len(p8) == 5 and len(p13) == 3
    assert set(REGISTERED_EVENT_TYPES) == p7 | p8 | p13
    # 19 + 8 + 5 + 3. Forty-three once P11's eight are spelled.
    assert len(EVENT_TYPES) == 35


def test_the_table_cannot_be_mutated_at_run_time():
    # Rule 4: a part cannot mint a type at run time.
    with pytest.raises(TypeError):
        EVENT_TYPES["invented at runtime"] = None
    with pytest.raises(TypeError):
        REGISTERED_EVENT_TYPES["invented at runtime"] = None


def test_the_module_publishes_no_registration_call():
    # There is no run-time registration path at all — not a guarded one.
    import database_agent.events as events_module
    assert not [n for n, v in vars(events_module).items()
                if callable(v) and n.lower().startswith("register")]


def test_writer_accepts_a_type_declared_by_another_part(conn):
    # Done-means 11's fixture: P13's `apply review approval`, accepted with no
    # registration call because the declaration is in P13's SPEC.
    create_schema(conn)
    event_id = append_event(conn, **_minimal(event_type="apply review approval",
                                             subsystem="P13", user_id="u1"))
    assert event_id


def test_writer_rejects_an_undeclared_type(conn):
    create_schema(conn)
    with pytest.raises(UnregisteredEventType):
        append_event(conn, **_minimal(event_type="invented at runtime"))


def test_a_specialization_stores_its_reserved_base_type(conn):
    # The mechanism, driven off the frozen table rather than a name typed here.
    create_schema(conn)
    specializations = [(n, b) for n, b in EVENT_TYPES.items() if b is not None]
    for name, base in specializations:
        event_id = append_event(conn, **_minimal(event_type=name, subsystem="P11"))
        row = conn.execute("SELECT * FROM events WHERE event_id = ?",
                           (event_id,)).fetchone()
        assert row["base_event_type"] == base


def test_p11s_eight_specializations_are_declared_but_unspelled():
    # P11's SPEC declares eight specializations of `placement recommendation` in
    # prose and publishes no identifiers, so P1 has no name to register. Inventing
    # one would be P1 authoring P11's vocabulary. This test is the standing record
    # of that gap: it starts failing the day P11 prints the eight names, which is
    # the day this plan's registry must gain them.
    assert [n for n, b in EVENT_TYPES.items()
            if b == "placement recommendation"] == []


def test_two_parts_may_author_the_same_reserved_type(conn):
    # M8: external modification detection has two authors, separable by subsystem.
    create_schema(conn)
    append_event(conn, **_minimal(event_type="external modification detection", subsystem="P12"))
    append_event(conn, **_minimal(event_type="external modification detection", subsystem="P3"))
    rows = conn.execute(
        "SELECT subsystem FROM events WHERE event_type = 'external modification detection'"
    ).fetchall()
    assert sorted(r["subsystem"] for r in rows) == ["P12", "P3"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_events.py -v`
Expected: FAIL with `ImportError: cannot import name 'RESERVED_EVENT_TYPES'`

- [ ] **Step 3: Write the frozen table**

Insert into `src/database_agent/events.py`, above `append_event`:

```python
from types import MappingProxyType

#: §8.2's nineteen, verbatim. Reserved: no part may redefine, narrow, or reuse one.
RESERVED_EVENT_TYPES: frozenset[str] = frozenset({
    "discovery", "stat observation", "hashing", "extraction", "OCR",
    "fact creation", "fact rejection", "graph-edge creation",
    "group membership proposal", "user group decision", "template application",
    "destination-tree edit", "placement recommendation",
    "filename-collision resolution", "planned move", "executed move",
    "failed move", "external modification detection", "undo",
})

# Registration is a spec-level act (rule 4), so this table is compiled from the
# declaring SPECs and frozen at import. There is no run-time registration call.
# name -> base type when the name is a typed specialization of a reserved name.
_REGISTERED: dict[str, str | None] = {
    # P7 SPEC, Cross-cutting answers -> Provenance. Eight.
    "classification_assigned": None,
    "classification_superseded": None,
    "policy_set": None,
    "consent_granted": None,
    "consent_revoked": None,
    "model_release": None,
    "model_release_denied": None,
    "consent_requested": None,
    # P8 SPEC, section 8 "Events appended". Five.
    "model_call_issued": None,
    "model_response_received": None,
    "validation_verdict": None,
    "verdict_superseded": None,
    "call_refused": None,
    # P13 SPEC, Cross-cutting answers -> Provenance. Three.
    "review presentation": None,
    "review action routed": None,
    "apply review approval": None,
    # P11's eight typed specializations of "placement recommendation" belong here
    # and are ABSENT ON PURPOSE: P11's SPEC declares them as prose descriptions and
    # publishes no identifiers. P1 does not coin a name another part owns. When P11
    # prints the eight, add them here with base="placement recommendation".
}

# Rule 1, checked once at import: a collision is an import error, not a run-time
# rejection, because there is no run time at which a name could be added.
_collisions = set(_REGISTERED) & RESERVED_EVENT_TYPES
if _collisions:
    raise ImportError(f"registered names shadow reserved 8.2 names: {sorted(_collisions)}")
_bad_bases = {b for b in _REGISTERED.values() if b is not None} - RESERVED_EVENT_TYPES
if _bad_bases:
    raise ImportError(f"specialization base is not a reserved name: {sorted(_bad_bases)}")

REGISTERED_EVENT_TYPES = MappingProxyType(_REGISTERED)
EVENT_TYPES = MappingProxyType(
    {name: None for name in RESERVED_EVENT_TYPES} | _REGISTERED
)


class UnregisteredEventType(Exception):
    """Rule 3: an unregistered type is rejected at the writer, never silently stored."""
```

Then change `append_event` to validate and to carry the base type:

```python
def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id.

    `subsystem` is the authoring part (§8.2 "the responsible subsystem"). P1 never
    fills it in: the acting part authors, P1 writes (M8).
    """
    event_type = fields.get("event_type")
    if event_type not in EVENT_TYPES:
        raise UnregisteredEventType(
            f"{event_type!r} is neither one of §8.2's nineteen reserved names nor "
            "declared by a part's SPEC; registration is a spec-level act (rule 4)"
        )
    base = EVENT_TYPES[event_type]
    if base is not None:
        fields.setdefault("base_event_type", base)
    columns = [k for k in fields if k in _WRITABLE]
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_events.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/events.py tests/test_events.py
git commit -m "feat(P1): frozen event-type table compiled from the SPECs, no runtime registration"
```

---

### Task 6: Path history and content-change identity (Done-means 2, 3)

**Files:**
- Modify: `src/database_agent/files_table.py`
- Test: `tests/test_identity.py` — extend

**Interfaces:**
- Consumes: `append_event`, `record_file`, `hash_file`.
- Produces: `observe_path(conn, path, *, author, component_version, parent_folder_context, mime_type, detected_format, scan_state, materialized) -> str`, `file_path_history(conn, file_id) -> list[sqlite3.Row]`, `invalidate_extraction_state(conn, file_id, *, author, component_version)`.

**`observe_path` is a write-only helper. The caller is the author.** SPEC Cross-cutting answers → Provenance: *"The acting part authors; P1 writes. P1 appends no event on its own initiative."* Contract in adds that P1 must *"accept the `discovery`, `stat observation`, `hashing` and `external modification detection` events **P3 authors** — P1 originates none of them."* The previous version of this task appended `stat observation` and `hashing` with `subsystem="P1"`, which would have written, into the log every later part audits, the claim that the storage substrate discovered and hashed the corpus. §8.2's reconstruction requirement — showing *"what it knew, what it proposed, what the user approved, what changed on disk, and why"* — cannot be met from a log whose author field is wrong.

The fix is one required keyword. `author` is the part making the observation (P3 in the running system, a fixture in these tests) and it is what lands in `subsystem`; `component_version` is that part's version, which Done-means 7 requires populated. There is no default for either. Every remaining argument is a §1.2 field P3 owns (Task 3).

**`invalidate_extraction_state` is published, not inlined.** SPEC R3 requires the extraction state to be marked invalid when content changes. A neighbour that needs R3 without going through `observe_path` had no function to call, because the `UPDATE` was buried inside it. It is a named surface here, and it takes the same `author` because it mutates the current projection on `files` — and *"no mutation of it is accepted without the authoring part's event explaining it"* (SPEC, Cross-cutting answers → Provenance).

**Which event explains a content change — the plan's reading, flagged for review.** When the same path yields different bytes, the prior row is superseded, and that mutation needs the authoring part's event on the *prior* `file_id`, otherwise the version P6's facts still point at has no provenance explaining why it stopped being current. The reserved type that fits is `external modification detection`, which the SPEC's authorship table assigns to *"P12 (§8.3 staleness triggers and sync conflicts) **and P3** (§1.2 re-scan)"* — a re-scan finding changed bytes at a known path is P3's half of exactly that. This is the plan's reading of a gap the SPEC does not spell out; if P3's SPEC names a different reserved type for a re-scan content change, use that one. Either way the event is authored by the caller, never by P1.

**`file_path_history` returns SPEC §2's four elements, and `volume_id` reads as unknown.** SPEC Contract out §2 publishes `file_path_history(file_id) -> ordered (path, volume_id, observed_at, event_id)`. No per-observation volume value is recorded anywhere — `events` carries no volume column, and P1 OQ9 is open, so `files.volume_id` is a within-session value (Task 2) that would be a lie if repeated across historical rows. The projection therefore returns the column with a `NULL`, which reads as *unknown* rather than as a wrong answer, and the gap is recorded against the SPEC. P12 cannot reconstruct an expected source volume from this surface until OQ9 closes; it must not silently get a plausible-looking one instead.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_identity.py`:

```python
from database_agent.db import create_schema
from database_agent.files_table import (
    file_path_history, get_file, observe_path,
)


def _observed(**overrides):
    """What P3 hands P1 on an observation. A fixture stands in for P3; `author` is
    what lands in `subsystem`, because the acting part authors and P1 writes (M8)."""
    fields = dict(author="P3", component_version="p3-fixture",
                  parent_folder_context="root", mime_type=None,
                  detected_format=None, scan_state="scanned", materialized=True)
    fields.update(overrides)
    return fields


def test_a_moved_file_keeps_one_record_and_gains_path_history(conn, tmp_path: Path):
    # R2 (§8.2): the same content observed at a new path is the same file version.
    # The ORIGINAL is gone — this is a move, not a duplicate.
    create_schema(conn)
    first = tmp_path / "one.bin"
    first.write_bytes(b"same content")
    file_id = observe_path(conn, first, **_observed(parent_folder_context="a"))

    second = tmp_path / "moved" / "two.bin"
    second.parent.mkdir()
    second.write_bytes(b"same content")
    first.unlink()                       # the move: only one copy is live
    again = observe_path(conn, second, **_observed(parent_folder_context="moved"))

    assert again == file_id
    history = file_path_history(conn, file_id)
    assert [r["path"] for r in history] == [str(first), str(second)]


def test_p1_authors_none_of_the_scan_events(conn, tmp_path: Path):
    # Contract in: P1 originates no discovery / stat observation / hashing event.
    # Every row an observation produces names its caller, never P1.
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    observe_path(conn, p, **_observed(author="P3"))
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
    file_id = observe_path(conn, p, **_observed())
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

    id_a = observe_path(conn, a, **_observed())
    id_b = observe_path(conn, b, **_observed())

    assert id_a != id_b
    rows = conn.execute(
        "SELECT file_id, current_path, content_hash FROM files ORDER BY current_path"
    ).fetchall()
    assert len(rows) == 2
    assert rows[0]["content_hash"] == rows[1]["content_hash"]
    assert {r["current_path"] for r in rows} == {str(a), str(b)}


def test_same_path_new_bytes_is_a_new_version_and_invalidates_extraction(conn, tmp_path: Path):
    # R3 (§8.2): a file whose content hash changes is a new version.
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed())

    p.write_bytes(b"version two")
    second_id = observe_path(conn, p, **_observed())

    assert second_id != first_id
    assert get_file(conn, second_id)["extraction_status_by_tier"] == "{}"
    assert get_file(conn, first_id)["scan_state"] == "superseded_content"


def test_the_superseded_version_carries_its_authors_explanation(conn, tmp_path: Path):
    # No mutation of the current projection is accepted without the authoring
    # part's event explaining it (SPEC, Cross-cutting answers → Provenance).
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed())
    p.write_bytes(b"version two")
    observe_path(conn, p, **_observed())

    explaining = conn.execute(
        "SELECT * FROM events WHERE file_id = ? AND event_type = "
        "'external modification detection'", (first_id,)
    ).fetchone()
    assert explaining is not None
    assert explaining["subsystem"] == "P3"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_identity.py -v`
Expected: FAIL with `ImportError: cannot import name 'observe_path'`

- [ ] **Step 3: Write the implementation**

Append to `src/database_agent/files_table.py`:

```python
from database_agent.events import append_event


def invalidate_extraction_state(conn: sqlite3.Connection, file_id: str, *,
                                author: str, component_version: str) -> None:
    """R3 — mark the file's extraction state invalid so the relevant extractors
    re-run. P1 does not run them; that is P5.

    `author` is the part that observed the change. Mutating the current projection
    on `files` without the authoring part's event is not accepted, so the caller
    appends its event and P1 records the invalidation under that author.
    """
    conn.execute(
        "UPDATE files SET extraction_status_by_tier = '{}' WHERE file_id = ?",
        (file_id,),
    )


def observe_path(conn: sqlite3.Connection, path: Path, *,
                 author: str,
                 component_version: str,
                 parent_folder_context: str | None,
                 mime_type: str | None,
                 detected_format: str | None,
                 scan_state: str,
                 materialized: bool) -> str:
    """R2/R3 — resolve a path observation to a file version (§8.2).

    Write-only helper: `author` is the part making the observation (P3 in the
    running system) and is what lands in `subsystem`. P1 appends no event on its
    own initiative (M8) and originates none of the scan types (Contract in).

    Same bytes at a new path where the old path is gone: same file version, path
    updated, history retained (a move).
    Same bytes at a new path where BOTH are live: two records sharing one
    content_hash (I1) — §2.9's duplicate family and §8.3's identical-file collision
    both require the two copies to remain distinguishable.
    New bytes: a new version; the prior row is superseded and its extraction state
    invalidated, under the caller's event.
    """
    content_hash = hash_file(path, materialized=materialized)
    now = datetime.now(timezone.utc).isoformat()

    # I1: a prior row for this hash is only the SAME file version if its recorded
    # path is no longer live. Two live copies are two records (§2.9, §8.3).
    existing = None
    for candidate in conn.execute(
        "SELECT * FROM files WHERE content_hash = ? AND scan_state != 'superseded_content' "
        "ORDER BY rowid", (content_hash,)
    ).fetchall():
        if candidate["current_path"] == str(path) or not Path(candidate["current_path"]).exists():
            existing = candidate
            break

    if existing is not None:
        if existing["current_path"] != str(path):
            append_event(
                conn, event_type="stat observation", file_id=existing["file_id"],
                content_hash=content_hash, old_path=existing["current_path"],
                new_path=str(path), subsystem=author,
                component_version=component_version, observed_at=now,
                explanation="same content observed at a new path (R2)",
            )
            conn.execute(
                "UPDATE files SET current_path = ? WHERE file_id = ?",
                (str(path), existing["file_id"]),
            )
        return existing["file_id"]

    prior = conn.execute(
        "SELECT file_id FROM files WHERE current_path = ? AND scan_state != 'superseded_content'",
        (str(path),),
    ).fetchone()
    if prior is not None:
        append_event(
            conn, event_type="external modification detection",
            file_id=prior["file_id"], content_hash=content_hash,
            old_path=str(path), new_path=str(path), subsystem=author,
            component_version=component_version, observed_at=now,
            explanation="content at this path changed; this version is superseded (R3)",
        )
        conn.execute(
            "UPDATE files SET scan_state = 'superseded_content' WHERE file_id = ?",
            (prior["file_id"],),
        )
        invalidate_extraction_state(conn, prior["file_id"], author=author,
                                    component_version=component_version)

    file_id = record_file(
        conn, path, parent_folder_context=parent_folder_context,
        mime_type=mime_type, detected_format=detected_format,
        scan_state=scan_state, materialized=materialized,
    )
    append_event(
        conn, event_type="hashing", file_id=file_id, content_hash=content_hash,
        new_path=str(path), subsystem=author, component_version=component_version,
        observed_at=now, explanation="new content hash recorded (R1, R3)",
    )
    return file_id


def file_path_history(conn: sqlite3.Connection, file_id: str) -> list[sqlite3.Row]:
    """§8.2 'Path history' — a projection over events carrying old/new paths.

    SPEC Contract out §2's shape is (path, volume_id, observed_at, event_id). No
    per-observation volume value is recorded: `events` has no volume column and
    P1 OQ9 is open, so the column is published as NULL — unknown, never a value
    a consumer could mistake for the volume this path was observed on.
    """
    return conn.execute(
        "SELECT COALESCE(new_path, old_path) AS path, NULL AS volume_id, "
        "observed_at, event_id "
        "FROM events WHERE file_id = ? AND (new_path IS NOT NULL OR old_path IS NOT NULL) "
        "ORDER BY event_id",
        (file_id,),
    ).fetchall()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_identity.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/files_table.py tests/test_identity.py
git commit -m "feat(P1): path and content identity, every event authored by its caller"
```

---

### Task 7: Supersede-never-overwrite (Done-means 5)

**Files:**
- Create: `src/database_agent/supersede.py`
- Test: `tests/test_supersede.py`

**Interfaces:**
- Consumes: `transaction`.
- Produces: `SUPERSEDE_COLUMNS: tuple[str, str, str]`, `supersede_ddl(table) -> str`, `mark_superseded(conn, table, *, old_id, new_id, reason)`, `chain(conn, table, record_id) -> list`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_supersede.py
import pytest

from database_agent.supersede import (
    SUPERSEDE_COLUMNS, chain, mark_superseded, supersede_ddl,
)


def _make_table(conn):
    conn.executescript(
        "CREATE TABLE extraction_records (record_id TEXT PRIMARY KEY, value TEXT, "
        + supersede_ddl("extraction_records") + ");"
    )


def test_the_three_shared_columns_are_exactly_these():
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")


def test_supersession_reason_is_not_an_alias():
    # M1: the spelling is supersede_reason. supersession_reason is not accepted.
    assert "supersession_reason" not in SUPERSEDE_COLUMNS
    assert "supersession_reason" not in supersede_ddl("t")


def test_preferred_is_not_in_the_shared_set():
    # M1: `preferred` is carried on P6's file_facts only.
    assert "preferred" not in SUPERSEDE_COLUMNS


def test_the_8_2_ocr_case_keeps_both_records_readable(conn):
    # §8.2's worked case is normative: a first OCR pass producing unreadable text
    # and a later engine that recovers a university name must BOTH remain available.
    _make_table(conn)
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r1', 'unreadable')")
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r2', 'recovered')")
    mark_superseded(conn, "extraction_records", old_id="r1", new_id="r2",
                    reason="improved OCR engine")

    old = conn.execute("SELECT * FROM extraction_records WHERE record_id='r1'").fetchone()
    new = conn.execute("SELECT * FROM extraction_records WHERE record_id='r2'").fetchone()
    assert old is not None and old["value"] == "unreadable"
    assert old["superseded_by"] == "r2"
    assert old["supersede_reason"] == "improved OCR engine"
    assert new["supersedes"] == "r1"
    assert [r["record_id"] for r in chain(conn, "extraction_records", "r1")] == ["r1", "r2"]


def test_superseding_never_deletes_or_mutates_the_old_value(conn):
    _make_table(conn)
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r1', 'original')")
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r2', 'newer')")
    mark_superseded(conn, "extraction_records", old_id="r1", new_id="r2", reason="x")
    assert conn.execute(
        "SELECT value FROM extraction_records WHERE record_id='r1'"
    ).fetchone()["value"] == "original"


def test_the_newest_record_is_not_automatically_preferred(conn):
    # §8.2 says the resolver MAY mark it — preference is an explicit act, and not P1's.
    _make_table(conn)
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(extraction_records)")]
    assert "preferred" not in cols
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_supersede.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.supersede'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/supersede.py
"""Contract out §4 — supersede-never-overwrite (§8.2).

P1 publishes three column names so that no part re-spells them (M1). The fourth,
`preferred`, is NOT in the shared set: §8.2 says the resolver may mark the newer
value, and §3.2 places the resolver after extraction, so it sits on P6's
`file_facts` only. P1 creates no `preferred` column.
"""
from __future__ import annotations

import sqlite3

SUPERSEDE_COLUMNS: tuple[str, str, str] = (
    "supersedes", "superseded_by", "supersede_reason",
)


def supersede_ddl(table: str) -> str:
    """The three shared columns, for a table that adopts the set."""
    return ("supersedes TEXT, superseded_by TEXT, supersede_reason TEXT")


def mark_superseded(conn: sqlite3.Connection, table: str, *,
                    old_id: str, new_id: str, reason: str) -> None:
    """Link a supersede chain. The old row stays readable and unmutated."""
    if not reason:
        raise ValueError("supersede_reason is required (§8.2)")
    conn.execute(
        f"UPDATE {table} SET superseded_by = ?, supersede_reason = ? WHERE record_id = ?",
        (new_id, reason, old_id),
    )
    conn.execute(
        f"UPDATE {table} SET supersedes = ? WHERE record_id = ?", (old_id, new_id)
    )


def chain(conn: sqlite3.Connection, table: str, record_id: str) -> list[sqlite3.Row]:
    """The full supersede chain, oldest first. Every link remains available (§8.2)."""
    rows, current = [], record_id
    while current is not None:
        row = conn.execute(
            f"SELECT * FROM {table} WHERE record_id = ?", (current,)
        ).fetchone()
        if row is None:
            break
        rows.append(row)
        current = row["superseded_by"]
    return rows
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_supersede.py -v`
Expected: PASS — 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/supersede.py tests/test_supersede.py
git commit -m "feat(P1): supersede columns and chain rules, preferred excluded"
```

---

### Task 8: Fixity verification points V1–V4 (Done-means 6)

**Files:**
- Create: `src/database_agent/verify.py`
- Test: `tests/test_verify.py`

**Interfaces:**
- Consumes: `hash_file`, `get_file`.
- Produces: `VerificationPoint` (enum V1–V4), `verify_content(conn, file_id, expected_hash, *, point, author, component_version, materialized) -> "match" | "mismatch"`, `confirm_cross_volume_copy(conn, *, source, destination, expected_hash, author, component_version, materialized) -> bool`.

**The event is `hashing`, and the author is the caller.** SPEC Cross-cutting answers → Provenance, *V1–V4 hashing*: *"P1 performs the four checksum verifications when a caller asks for one; the `hashing` event for a verification is authored by the calling part — P12 (§8.3), the only caller of V1–V4 (MINOR 5) — with `subsystem` naming P1 as the performer. P1's act is the comparison; the decision that a verification was due is never P1's."*

Two things follow, and the previous version of this task got both wrong. First, the event type is **`hashing`**, not `stat observation`: recording fixity under the wrong reserved name makes every fixity check unqueryable as hashing, and P2's per-stage replay would look at the wrong type. Second, `subsystem = "P1"` is **correct here and only here**, because the SPEC names P1 as the performer of the comparison — but P1 still must not originate the check, so `author` is a required keyword naming the part that asked, and it is recorded in §8.2's structured explanation. P1 verifies nothing on its own initiative.

`materialized` is required for the same reason as everywhere else ([`../../11-ops-runtime.md`](../../11-ops-runtime.md) §5): P12 already refuses a plan whose source is dataless, so it is P12 that knows, and P1 refuses to be the path that downloads one.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_verify.py
import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import observe_path
from database_agent.identity import hash_file
from database_agent.verify import (
    VerificationPoint, confirm_cross_volume_copy, verify_content,
)


def _observed(**overrides):
    fields = dict(author="P3", component_version="p3-fixture",
                  parent_folder_context="corpus", mime_type=None,
                  detected_format=None, scan_state="scanned", materialized=True)
    fields.update(overrides)
    return fields


def _asked_by_p12(**overrides):
    fields = dict(author="P12", component_version="p12-fixture", materialized=True)
    fields.update(overrides)
    return fields


def test_all_four_points_exist():
    assert [p.name for p in VerificationPoint] == ["V1", "V2", "V3", "V4"]


def test_verify_returns_match_for_unchanged_content(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed())
    expected = hash_file(sample_file, materialized=True)
    for point in VerificationPoint:
        if point is VerificationPoint.V4:
            continue
        assert verify_content(conn, file_id, expected, point=point,
                              **_asked_by_p12()) == "match"


def test_verify_returns_mismatch_after_content_changes(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed())
    expected = hash_file(sample_file, materialized=True)
    sample_file.write_bytes(b"different bytes entirely")
    assert verify_content(conn, file_id, expected, point=VerificationPoint.V1,
                          **_asked_by_p12()) == "mismatch"


def test_v4_refuses_success_until_destination_hash_is_confirmed(conn, tmp_path: Path):
    create_schema(conn)
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload")
    good = tmp_path / "good.bin"
    good.write_bytes(b"payload")
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"truncated")
    expected = hash_file(source, materialized=True)

    assert confirm_cross_volume_copy(conn, source=source, destination=good,
                                     expected_hash=expected, **_asked_by_p12()) is True
    assert confirm_cross_volume_copy(conn, source=source, destination=bad,
                                     expected_hash=expected, **_asked_by_p12()) is False


def test_verification_is_recorded_as_a_hashing_event(conn, sample_file: Path):
    # SPEC: the `hashing` event for a verification is authored by the calling part,
    # with `subsystem` naming P1 as the performer.
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed())
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    verify_content(conn, file_id, hash_file(sample_file, materialized=True),
                   point=VerificationPoint.V2, **_asked_by_p12())
    rows = conn.execute("SELECT * FROM events ORDER BY event_id DESC").fetchall()
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before + 1
    assert rows[0]["event_type"] == "hashing"
    assert rows[0]["subsystem"] == "P1"          # performer
    assert json.loads(rows[0]["explanation"])["requested_by"] == "P12"   # author


def test_p1_will_not_verify_without_a_caller(conn, sample_file: Path):
    # The decision that a verification was due is never P1's.
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed())
    with pytest.raises(TypeError):
        verify_content(conn, file_id, "abc", point=VerificationPoint.V1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_verify.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.verify'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/verify.py
"""Contract out §5 — the four checksum verification points (§8.2).

P12 (§8.3) is the only caller (MINOR 5). §6 decides where a file should go and never
touches bytes. P1 performs and records; it decides nothing about what a mismatch means —
§8.3's stale and undo decisions belong to P12.

Authorship: the `hashing` event for a verification is authored by the calling part,
with `subsystem` naming P1 as the performer (SPEC, Cross-cutting answers →
Provenance). P1 never originates a verification, so `author` has no default.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from database_agent.events import append_event
from database_agent.files_table import get_file
from database_agent.identity import hash_file


class VerificationPoint(Enum):
    V1 = "before preparing a filesystem action"
    V2 = "immediately before executing a move or copy"
    V3 = "after completing the action"
    V4 = "cross-volume copy-and-delete destination confirmation"


def _explanation(point: VerificationPoint, author: str, result: str, **extra) -> str:
    """§8.2's 'structured explanation'. It names who asked; `subsystem` names who performed."""
    return json.dumps({"point": point.name, "description": point.value,
                       "requested_by": author, "result": result, **extra})


def verify_content(conn: sqlite3.Connection, file_id: str, expected_hash: str, *,
                   point: VerificationPoint, author: str, component_version: str,
                   materialized: bool) -> str:
    """Return 'match' or 'mismatch'. Records the check; interprets nothing."""
    row = get_file(conn, file_id)
    actual = hash_file(Path(row["current_path"]), materialized=materialized)
    result = "match" if actual == expected_hash else "mismatch"
    append_event(
        conn, event_type="hashing", file_id=file_id, content_hash=actual,
        subsystem="P1", component_version=component_version,
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=_explanation(point, author, result),
    )
    return result


def confirm_cross_volume_copy(conn: sqlite3.Connection, *, source: Path,
                              destination: Path, expected_hash: str, author: str,
                              component_version: str, materialized: bool) -> bool:
    """V4 — the destination copy is hashed and confirmed BEFORE the source may be
    removed (§8.2). P1 never removes the source; it only answers whether it may be."""
    confirmed = (destination.exists()
                 and hash_file(destination, materialized=materialized) == expected_hash)
    append_event(
        conn, event_type="hashing", content_hash=expected_hash,
        old_path=str(source), new_path=str(destination), subsystem="P1",
        component_version=component_version,
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=_explanation(VerificationPoint.V4, author,
                                 "confirmed" if confirmed else "refused"),
    )
    return confirmed
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_verify.py -v`
Expected: PASS — 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/verify.py tests/test_verify.py
git commit -m "feat(P1): V1-V4 fixity as hashing events, authored by the caller, performed by P1"
```

---

### Task 9: The §8.7 learning-record store (Done-means 13)

**Files:**
- Create: `src/database_agent/learning.py`
- Modify: `src/database_agent/db.py` — add `LEARNING_DDL` to `create_schema`
- Test: `tests/test_learning.py`

**Interfaces:**
- Consumes: `append_event`.
- Produces: `SCOPES: tuple[str, ...]`, `learning_records(conn, scope, subject_id) -> list`, `reset_preferences(conn, scope, subject_id, *, author, component_version, user_id) -> int`, `reset_cutoff(conn, scope, subject_id) -> int | None`.

**The subject is not the file.** SPEC Contract out §7 publishes `learning_records(scope, subject_id)` over §8.7's six scopes — file, group, destination node, template, domain, corpus. The previous version keyed every scope through `events.file_id`, which works for exactly one of the six. [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md) turned that from a latent defect into a live one: **P6, P7, P8, P9, P10 and P11 now query this store before they propose**, at group, node, template, domain and corpus scope. A file column makes every one of those reads a miss, and a miss reads as *"the user has never rejected this"* — the exact failure §8.7 names, where the system *"will repeatedly resurface the same attractive but incorrect grouping."* The subject therefore has its own column, `correction_subject` (Task 4), and `file_id` keeps meaning what §8.2 says it means. This is also the shape SPEC OQ3 is open about — an event with no single file — and it does not answer OQ3: it stops the learning store from depending on the answer.

**Three opaque fields come back with the record.** SPEC Contract out §7: the store returns each record *"with its §8.2 `explanation`, `polarity`, `proposal_class`, `basis_key`, and evidence reference"*, and *"P1 stores and returns all three and decides nothing from them."*

- **`polarity ∈ accept | reject`** is supplied by the acting part on the user-action event it authors. P1 **never infers it** — not from the event type, not from the explanation. §8.7 requires *"rejected groups, rejected destination matches, rejected labels, and rejected residual recommendations"* to be recoverable as rejections, and [`../../10-i4-learning-ops.md`](../../10-i4-learning-ops.md)'s query-before-propose rule fires only on an unreset **reject** that no later cutoff covers. Without the column, P6, P7, P8, P9, P10 and P11 would each have to read polarity out of `explanation` free text; a misread suppresses a valid proposal in one direction and resurfaces an already-rejected grouping in the other — §8.7's named failure.
- **`proposal_class` and `basis_key`** carry the equivalence rule in the same document: two proposals are equivalent when they share both.

**P1 suppresses nothing.** It stores all three, returns all three, and applies none of them. Deciding that an unreset `reject` at a matching `basis_key` means "do not emit" is the acting part's rule, enforced in that part — P1 has no `polarity` filter, and adding one here would be P1 learning.

**Reset is a cutoff later reads honour, not a filter that changes nothing.** SPEC Contract out §7: *"Reset appends a scoped reset record that later reads honour; it never deletes an event (R6), so the history of what was learned and un-learned stays inspectable."* The previous version returned every `user_id IS NOT NULL` row including the reset itself, so a reset was inspectable and operationally a no-op — and with `10`'s query-before-propose readers now live, a reset that does nothing means a user who un-learned a preference still cannot get the proposal back. `reset_preferences` records the cutoff in a P1 table beside the appended event; `learning_records` returns only records after the newest cutoff at that scope and subject. Nothing is deleted, and every pre-reset row stays in `events` under R6.

**Reset mints no event type.** P13 already specified it: [`../P13-review-approval-surface/SPEC.md`](../P13-review-approval-surface/SPEC.md) §2 defines `review_action` with `surface = learning` and `action = reset_learning`, routed to P1, and P1's own Contract in names *"the learning-preference resets that arrive as `surface = learning` with `action = reset_learning`."* The event P13 authors for a collected gesture is its registered `review action routed`. The previous version wrote `_REGISTRY["preference reset"] = None` at run time and set `user_id="reset"` so the row would survive its own filter — a type in no SPEC, minted in a process-local dict, bypassing the reserved-name check. `reset_preferences` now takes the author and the real user identity, and appends `review action routed`.

**`SCOPES` uses §8.7's short spelling.** The stored value is `node`, matching P1's `events.correction_scope` column definition and P13's `review_action.correction_scope`. SPEC Contract out §7's prose says "destination node" for the same scope; that is a prose divergence to fix in the SPEC, not a second value.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_learning.py
from datetime import datetime, timezone
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.learning import SCOPES, learning_records, reset_preferences


def _correction(conn, scope, subject, explanation, **overrides):
    """A user-action event authored by the acting part (M8). `correction_subject`
    is the subject at `correction_scope`; it is not a file id unless scope=file."""
    fields = dict(
        event_type="user group decision", file_id=None, content_hash=None,
        subsystem="P9", component_version="p9-fixture",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=explanation, correction_scope=scope, correction_subject=subject,
        polarity="reject", proposal_class="group", basis_key="opaque-basis-1",
        user_id="u1",
    )
    fields.update(overrides)
    return append_event(conn, **fields)


def test_the_six_scopes():
    assert SCOPES == ("file", "group", "node", "template", "domain", "corpus")


def test_a_file_scoped_correction_is_not_returned_by_a_corpus_read(conn):
    # §8.7's worked case: one transcript belonging in a Columbia packet must not
    # teach the engine that all transcripts belong there.
    create_schema(conn)
    _correction(conn, "file", "f1", "this one belongs here")
    assert learning_records(conn, "corpus", "f1") == []
    assert len(learning_records(conn, "file", "f1")) == 1


def test_a_non_file_subject_is_addressable(conn):
    # 10-i4-learning-ops.md: P6/P7/P8/P9/P10/P11 query at group, node, template,
    # domain and corpus scope. None of those subjects is a file id.
    create_schema(conn)
    for scope, subject in (("group", "g1"), ("node", "n1"), ("template", "t1"),
                           ("domain", "d1"), ("corpus", "c1")):
        _correction(conn, scope, subject, f"rejected at {scope}")
        found = learning_records(conn, scope, subject)
        assert len(found) == 1, f"{scope} read missed its own record"
        assert found[0]["file_id"] is None
        assert found[0]["correction_subject"] == subject


def test_the_record_returns_its_proposal_class_and_basis_key(conn):
    # SPEC Contract out §7. Opaque to P1: stored and returned, never compared.
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected",
                proposal_class="group", basis_key="sorted-anchor-facts")
    record = learning_records(conn, "group", "g1")[0]
    assert record["proposal_class"] == "group"
    assert record["basis_key"] == "sorted-anchor-facts"


def test_the_record_returns_its_polarity(conn):
    # SPEC Contract out §7: polarity ∈ accept | reject, supplied by the acting
    # part. 10-i4-learning-ops.md's query-before-propose rule fires on an unreset
    # reject, so a reader must be able to tell one from the other without parsing
    # explanation free text.
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected here", polarity="reject")
    _correction(conn, "group", "g2", "accepted here", polarity="accept")
    assert learning_records(conn, "group", "g1")[0]["polarity"] == "reject"
    assert learning_records(conn, "group", "g2")[0]["polarity"] == "accept"


def test_p1_neither_infers_polarity_nor_filters_on_it(conn):
    # P1 stores and returns; it decides nothing from the value. An accept and a
    # reject at the same scope and subject both come back, in event order, and
    # P1 derives neither from the event type.
    create_schema(conn)
    _correction(conn, "group", "g1", "first", polarity="accept")
    _correction(conn, "group", "g1", "second", polarity="reject")
    returned = learning_records(conn, "group", "g1")
    assert [r["polarity"] for r in returned] == ["reject", "accept"]

    # A user-action event whose author supplied no polarity is stored as unknown,
    # never guessed from `event_type`.
    _correction(conn, "group", "g3", "no polarity supplied", polarity=None)
    assert learning_records(conn, "group", "g3")[0]["polarity"] is None

    import database_agent.learning as learning_module
    source = Path(learning_module.__file__).read_text(encoding="utf-8")
    assert "accept" not in source and "reject" not in source


def test_a_rejection_returns_with_its_evidence(conn):
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected: evidence_ref=obs-key-123")
    records = learning_records(conn, "group", "g1")
    assert "obs-key-123" in records[0]["explanation"]


def test_reset_appends_and_deletes_nothing(conn):
    create_schema(conn)
    _correction(conn, "domain", "d1", "first preference")
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    after = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    # pre-reset records stay readable in the log (R6) — reset deletes nothing
    surviving = conn.execute(
        "SELECT explanation FROM events WHERE correction_subject = 'd1'"
    ).fetchall()
    assert any("first preference" in r["explanation"] for r in surviving)


def test_later_reads_honour_the_reset(conn):
    # SPEC §7: "a scoped reset record that later reads honour". A reader that
    # queries before proposing must see an un-learned preference as un-learned.
    create_schema(conn)
    _correction(conn, "domain", "d1", "before the reset")
    assert len(learning_records(conn, "domain", "d1")) == 1

    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert learning_records(conn, "domain", "d1") == []

    _correction(conn, "domain", "d1", "after the reset")
    remaining = learning_records(conn, "domain", "d1")
    assert [r["explanation"] for r in remaining] == ["after the reset"]


def test_a_reset_is_scoped_and_does_not_clear_its_neighbours(conn):
    create_schema(conn)
    _correction(conn, "domain", "d1", "kept")
    _correction(conn, "domain", "d2", "also kept")
    _correction(conn, "group", "d1", "different scope, same subject id")
    reset_preferences(conn, "domain", "d1", author="P13",
                      component_version="p13-fixture", user_id="u1")
    assert learning_records(conn, "domain", "d1") == []
    assert len(learning_records(conn, "domain", "d2")) == 1
    assert len(learning_records(conn, "group", "d1")) == 1


def test_reset_appends_p13s_registered_type_and_mints_nothing(conn):
    # P13 SPEC §2: reset arrives as review_action, surface = learning,
    # action = reset_learning. The event P13 authors is `review action routed`.
    create_schema(conn)
    event_id = reset_preferences(conn, "domain", "d1", author="P13",
                                 component_version="p13-fixture", user_id="u1")
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == "review action routed"
    assert row["subsystem"] == "P13"
    assert row["user_id"] == "u1"


def test_unknown_scope_is_rejected(conn):
    create_schema(conn)
    with pytest.raises(ValueError):
        learning_records(conn, "everything", "x")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_learning.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.learning'`

- [ ] **Step 3: Add LEARNING_DDL to db.py and run it in create_schema**

```python
LEARNING_DDL = """
CREATE TABLE IF NOT EXISTS learning_resets (
    scope       TEXT NOT NULL,
    subject_id  TEXT NOT NULL,
    event_id    INTEGER NOT NULL,
    reset_at    TEXT NOT NULL,
    PRIMARY KEY (scope, subject_id, event_id)
);
"""
```

Add `conn.executescript(LEARNING_DDL)` to `create_schema` in `db.py`.

This table holds **cutoffs, not history**. The reset itself is an event in the append-only log; this is the index that lets a read honour it without P1 parsing another part's vocabulary out of an explanation. Nothing here is ever deleted either.

- [ ] **Step 4: Write the implementation**

```python
# src/database_agent/learning.py
"""Contract out §7 — the §8.7 learning-record store.

A scoped projection over `events`, not a new authority and not a second log.
P1 does not learn: no weighting, no generalization, no ranking, no application.
What a record means is decided by the part that authored the correction.

The three opaque fields — polarity, proposal_class, basis_key — are stored and
returned unchanged. P1 derives none of them from the event type or the
explanation, and filters on none of them. Suppressing a proposal is the acting
part's rule, applied in that part.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from database_agent.events import append_event

#: §8.7's six scopes, in the spelling `events.correction_scope` and P13's
#: `review_action.correction_scope` both use. "destination node" is the same scope
#: written out in prose; it is not a second value.
SCOPES: tuple[str, ...] = ("file", "group", "node", "template", "domain", "corpus")

#: The event P13 authors when it routes a collected gesture (P13 SPEC, Provenance).
#: A reset arrives as review_action with surface = learning, action = reset_learning.
_ROUTED = "review action routed"


def _check(scope: str) -> None:
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; §8.7 defines exactly {SCOPES}")


def reset_cutoff(conn: sqlite3.Connection, scope: str, subject_id: str) -> int | None:
    """The newest reset at this scope and subject, as an event_id, or None."""
    _check(scope)
    row = conn.execute(
        "SELECT MAX(event_id) AS cutoff FROM learning_resets "
        "WHERE scope = ? AND subject_id = ?",
        (scope, subject_id),
    ).fetchone()
    return None if row is None else row["cutoff"]


def learning_records(conn: sqlite3.Connection, scope: str,
                     subject_id: str) -> list[sqlite3.Row]:
    """User-action events at that scope for that subject, newest first, each with
    its §8.2 explanation, polarity, proposal_class and basis_key.

    Scope is the filter and it is exact. The subject is `correction_subject`, not
    `file_id`: five of §8.7's six scopes have no file. A reset at this scope and
    subject is honoured as a cutoff — records before it are not returned, and none
    of them is deleted (R6).
    """
    _check(scope)
    cutoff = reset_cutoff(conn, scope, subject_id) or 0
    return conn.execute(
        "SELECT * FROM events WHERE correction_scope = ? AND correction_subject = ? "
        "AND user_id IS NOT NULL AND event_id > ? ORDER BY event_id DESC",
        (scope, subject_id, cutoff),
    ).fetchall()


def reset_preferences(conn: sqlite3.Connection, scope: str, subject_id: str, *,
                      author: str, component_version: str, user_id: str) -> int:
    """Append a scoped reset and record the cutoff it establishes. Deletes nothing (R6).

    P1 mints no event type for this. P13 collects the gesture as `review_action`
    with surface = learning and action = reset_learning and routes it here; the
    event it authors is its registered `review action routed`, so `author` is the
    routing part and lands in `subsystem` (M8).
    """
    _check(scope)
    now = datetime.now(timezone.utc).isoformat()
    event_id = append_event(
        conn, event_type=_ROUTED, subsystem=author,
        component_version=component_version, observed_at=now,
        explanation=f"learning preferences reset at scope {scope}",
        correction_scope=scope, correction_subject=subject_id, user_id=user_id,
    )
    conn.execute(
        "INSERT INTO learning_resets (scope, subject_id, event_id, reset_at) "
        "VALUES (?, ?, ?, ?)",
        (scope, subject_id, event_id, now),
    )
    return event_id
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_learning.py -v`
Expected: PASS — 12 passed

- [ ] **Step 6: Commit**

```bash
git add src/database_agent/db.py src/database_agent/learning.py tests/test_learning.py
git commit -m "feat(P1): 8.7 learning projection with its own subject column and an honoured reset"
```

---

### Task 10: The §8.6 budget configuration object (Done-means 14)

**Files:**
- Create: `src/database_agent/budget.py`
- Test: `tests/test_budget.py`

**Interfaces:**
- Consumes: `transaction`.
- Produces: `CEILING_KEYS: tuple[str, ...]` (fifteen), `set_ceiling(conn, key, value)`, `get_ceiling(conn, key)`, `all_ceilings(conn) -> dict`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_budget.py
import pytest

from database_agent.budget import CEILING_KEYS, all_ceilings, get_ceiling, set_ceiling
from database_agent.db import create_schema


def test_there_are_exactly_fifteen_keys():
    assert len(CEILING_KEYS) == 15
    assert len(set(CEILING_KEYS)) == 15


def test_grouping_and_placement_resolve_independently(conn):
    # O10: two parts legitimately hold three ceilings on different graphs.
    create_schema(conn)
    set_ceiling(conn, "grouping.max_retrieved_neighbors", 25)
    set_ceiling(conn, "placement.max_retrieved_neighbors", 8)
    assert get_ceiling(conn, "grouping.max_retrieved_neighbors") == 25
    assert get_ceiling(conn, "placement.max_retrieved_neighbors") == 8


def test_all_fifteen_keys_are_readable(conn):
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_budget.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.budget'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/budget.py
"""Contract out §8 — the §8.6 budget configuration object (S5, G4).

Fifteen keys, because three of §8.6's twelve ceilings are held by two parts on
different graphs and are namespaced accordingly (O10). P1 holds and publishes
values; P1 enforces none of them. Reading a ceiling is not enforcing it.
"""
from __future__ import annotations

import sqlite3

CEILING_KEYS: tuple[str, ...] = (
    "ocr.max_pages_per_file",
    "ocr.max_time_per_file",
    "ocr.max_time_per_scan",
    "image.max_analysis_ops_per_scan",
    "model.max_llm_calls_per_thousand_files",
    "model.max_cost_per_scan",
    "model.max_dossier_tokens_per_call",
    "grouping.max_retrieved_neighbors",
    "placement.max_retrieved_neighbors",
    "grouping.max_local_graph_neighborhood",
    "placement.max_local_graph_neighborhood",
    "grouping.max_candidate_cluster_size",
    "placement.max_candidate_cluster_size",
    "residual.max_files_per_review_batch",
    "tree.max_folder_proposals_and_depth",
)

BUDGET_DDL = """
CREATE TABLE IF NOT EXISTS budget_ceilings (
    key           TEXT PRIMARY KEY,
    value         INTEGER NOT NULL,
    object_version INTEGER NOT NULL DEFAULT 1
);
"""


def _check(key: str) -> None:
    if key not in CEILING_KEYS:
        raise KeyError(f"{key!r} is not one of §8.6's fifteen ceiling keys")


def set_ceiling(conn: sqlite3.Connection, key: str, value: int) -> None:
    _check(key)
    conn.execute(
        "INSERT INTO budget_ceilings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
        "object_version = object_version + 1",
        (key, value),
    )


def get_ceiling(conn: sqlite3.Connection, key: str) -> int | None:
    _check(key)
    row = conn.execute("SELECT value FROM budget_ceilings WHERE key = ?", (key,)).fetchone()
    return None if row is None else row["value"]


def all_ceilings(conn: sqlite3.Connection) -> dict[str, int]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM budget_ceilings")}
```

Add `conn.executescript(BUDGET_DDL)` to `create_schema` in `db.py` (import `BUDGET_DDL` from `budget.py`, or inline the DDL string there — inline it to avoid a circular import).

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_budget.py -v`
Expected: PASS — 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/budget.py src/database_agent/db.py tests/test_budget.py
git commit -m "feat(P1): 8.6 budget config, fifteen keys, namespaced, enforced by nobody here"
```

---

### Task 11: The §0 vector array store (Done-means 15)

**Files:**
- Create: `src/database_agent/vectors.py`
- Test: `tests/test_vectors.py`

**Interfaces:**
- Consumes: `transaction`.
- Produces: `put_embedding(conn, subject_key, array, producer_version)`, `get_embedding(conn, subject_key) -> bytes | None`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_vectors.py
from database_agent.db import create_schema
from database_agent.vectors import get_embedding, put_embedding
import database_agent.vectors as vectors_module


def test_array_round_trips_byte_identically(conn):
    create_schema(conn)
    payload = bytes(range(256)) * 4
    put_embedding(conn, "file:abc", payload, producer_version="p9-v1")
    assert get_embedding(conn, "file:abc") == payload


def test_arrays_live_outside_files_and_events(conn):
    create_schema(conn)
    put_embedding(conn, "file:abc", b"\x00\x01", producer_version="p9-v1")
    for table in ("files", "events"):
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        assert not any(c.lower() in ("embedding", "vector", "array") for c in cols)


def test_p1_exposes_no_similarity_or_nearest_neighbour_call():
    # §0: never a vector database. Retrieval belongs to P9 (§4.2) and P11 (§6.3).
    exported = dir(vectors_module)
    for forbidden in ("similarity", "cosine", "nearest", "knn", "search", "index"):
        assert not any(forbidden in name.lower() for name in exported)


def test_missing_key_returns_none(conn):
    create_schema(conn)
    assert get_embedding(conn, "file:absent") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_vectors.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.vectors'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/vectors.py
"""Contract out §9 — the vector array store (S2, G2).

§0's exact posture: "store vectors separately as compact local arrays if embeddings
are used", never a vector database. P9 computes; P1 stores and returns bytes.
P1 exposes no similarity function, no index, and no nearest-neighbour query.
"""
from __future__ import annotations

import sqlite3

VECTORS_DDL = """
CREATE TABLE IF NOT EXISTS vector_arrays (
    subject_key      TEXT PRIMARY KEY,
    array_bytes      BLOB NOT NULL,
    producer_version TEXT NOT NULL
);
"""


def put_embedding(conn: sqlite3.Connection, subject_key: str, array: bytes, *,
                  producer_version: str) -> None:
    """Store an opaque compact local array. P1 does not interpret its contents."""
    conn.execute(
        "INSERT INTO vector_arrays (subject_key, array_bytes, producer_version) "
        "VALUES (?, ?, ?) ON CONFLICT(subject_key) DO UPDATE SET "
        "array_bytes = excluded.array_bytes, producer_version = excluded.producer_version",
        (subject_key, array, producer_version),
    )


def get_embedding(conn: sqlite3.Connection, subject_key: str) -> bytes | None:
    """Return it unchanged."""
    row = conn.execute(
        "SELECT array_bytes FROM vector_arrays WHERE subject_key = ?", (subject_key,)
    ).fetchone()
    return None if row is None else bytes(row["array_bytes"])
```

Add `conn.executescript(VECTORS_DDL)` to `create_schema` in `db.py` (inline the DDL string to avoid a circular import).

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_vectors.py -v`
Expected: PASS — 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/vectors.py src/database_agent/db.py tests/test_vectors.py
git commit -m "feat(P1): opaque vector array store, no index, no similarity"
```

---

### Task 12: No-interpretation guard (Done-means 8)

**Files:**
- Create: `tests/test_no_interpretation.py`

**Interfaces:**
- Consumes: the whole `src/database_agent/` package.
- Produces: nothing — this is a guard test that keeps P1 free of other parts' vocabulary.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_no_interpretation.py
"""Done-means 8 — P1's code contains no fact-field name, domain name, template name,
sensitivity class, or tier name (§3.11, §5.7, §7.3, §8.4 belong elsewhere).

The §8.6 ceiling keys and the nineteen reserved event names are NOT exceptions:
both are §0/§8.2/§8.6 vocabulary the design states literally, and neither names a
fact, a domain, or a class.
"""
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "database_agent"

FORBIDDEN = [
    # §3.11 domain fact fields
    "course", "syllabus", "instructor", "semester", "target_university",
    "application_cycle", "artifact_type", "tax_year", "capture_year",
    # §7.3 residual template names
    "reference clips", "reading inbox", "review later", "protected records",
    # §8.4 sensitivity classes
    "sensitive personal", "credential-bearing", "public or low",
    # §5.4 template dimension names used as P1 vocabulary
    "work type", "admissions",
]


def test_p1_source_contains_no_other_parts_vocabulary():
    offenders = []
    for path in SRC.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN:
            if term in text:
                offenders.append(f"{path.name}: {term!r}")
    assert not offenders, "P1 leaked interpretation: " + "; ".join(offenders)


def test_p1_stores_sensitivity_as_an_opaque_value():
    # P1 carries sensitivity_state as a column but defines none of P7's classes.
    text = (SRC / "files_table.py").read_text(encoding="utf-8")
    assert "sensitivity_state" in text
    for cls in ("sensitive personal", "credential", "unclassified"):
        assert cls not in text.lower()
```

- [ ] **Step 2: Run test to verify it fails or passes**

Run: `pytest tests/test_no_interpretation.py -v`
Expected: PASS if Tasks 1–11 stayed clean. If it FAILS, the named module leaked another part's vocabulary — remove the term, do not add it to `FORBIDDEN`.

- [ ] **Step 3: Run the whole suite**

Run: `pytest -v`
Expected: PASS — all tests from Tasks 1–12

- [ ] **Step 4: Commit**

```bash
git add tests/test_no_interpretation.py
git commit -m "test(P1): guard against leaking other parts' vocabulary into the substrate"
```

---

### Task 13: Walking-skeleton participation (Done-means 10)

**Files:**
- Create: `tests/test_skeleton_p1_step.py`

**Interfaces:**
- Consumes: everything above.
- Produces: the integration test that later parts must keep green.

**The skeleton depends on no P1-authored event.** [`../../02-segmentation-map.md`](../../02-segmentation-map.md)'s P1 slice is *hash, create the file record, discovery by a P3 fixture*. Every event this test produces is authored by the fixture standing in for P3, and the test asserts it: if a later edit reintroduces a P1-authored scan event, this test fails rather than blessing it.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skeleton_p1_step.py
"""The walking skeleton's P1 step (02-segmentation-map.md):
hash, create the file record, append a discovery event — and P12's step reaches
P1's V1-V4 and gets true answers.

This test stays in the repository as the integration test every later part must
keep green. It is deterministic: no model, no cloud, no embeddings.
"""
from datetime import datetime, timezone
from pathlib import Path

from database_agent.db import create_schema
from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path
from database_agent.identity import hash_file
from database_agent.verify import VerificationPoint, verify_content


def test_skeleton_p1_step(conn, tmp_path: Path):
    create_schema(conn)

    # One PDF whose title carries a course code (the skeleton's input file).
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_bytes(b"%PDF-1.4 fixture bytes")

    # P3's fixture hands P1 the §1.2 fields and authors the scan events (M8).
    # P1 hashes, creates the file record, and writes. It authors nothing.
    file_id = observe_path(
        conn, document, author="P3", component_version="p3-fixture",
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
    )
    append_event(
        conn, event_type="discovery", file_id=file_id,
        content_hash=hash_file(document, materialized=True), new_path=str(document),
        subsystem="P3", component_version="p3-fixture",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation="skeleton fixture stands in for P3",
    )

    row = get_file(conn, file_id)
    assert row["content_hash"] == hash_file(document, materialized=True)
    assert row["hash_algorithm"]
    assert row["volume_id"]

    discovery = conn.execute(
        "SELECT * FROM events WHERE event_type = 'discovery' AND file_id = ?", (file_id,)
    ).fetchone()
    assert discovery is not None
    assert discovery["subsystem"] == "P3"

    # Nothing in the scan half of the skeleton is authored by P1 (Contract in, M8).
    scan_authors = conn.execute(
        "SELECT DISTINCT subsystem FROM events WHERE event_type IN "
        "('discovery', 'stat observation', 'hashing')"
    ).fetchall()
    assert [r["subsystem"] for r in scan_authors] == ["P3"]

    # P12's step reaches V1-V4 and gets true answers. Here the `hashing` event is
    # authored by P12 and performed by P1 — the one place `subsystem` is P1.
    for point in (VerificationPoint.V1, VerificationPoint.V2, VerificationPoint.V3):
        assert verify_content(conn, file_id, row["content_hash"], point=point,
                              author="P12", component_version="p12-fixture",
                              materialized=True) == "match"
    performed = conn.execute(
        "SELECT subsystem FROM events WHERE event_type = 'hashing' ORDER BY event_id DESC"
    ).fetchone()
    assert performed["subsystem"] == "P1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skeleton_p1_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_skeleton_p1_step.py
git commit -m "test(P1): walking-skeleton P1 step, deterministic, every scan event authored by P3"
```

---

### Task 14: The §8.6 per-scan resource record (Done-means 16)

**Files:**
- Create: `src/database_agent/scan_usage.py`
- Modify: `src/database_agent/db.py` — add `SCAN_USAGE_DDL` to `create_schema`
- Test: `tests/test_scan_usage.py`

**Interfaces:**
- Consumes: `transaction`.
- Produces: `RESOURCE_COUNTERS: tuple[str, ...]` (six), `start_scan(conn) -> str`, `sample_scan_resources(conn, scan_id)`, `record_llm_cost(conn, scan_id, cost, *, author)`, `scan_resource_usage(conn, scan_id) -> sqlite3.Row`.

**Why this task exists.** SPEC Contract out §10 is a published surface with no task, and Done-means 16 is the only Done-means the plan did not cover. §8.6's first sentence names six resources — *"elapsed time, memory, CPU or accelerator usage, storage, network use, and LLM cost"* — and P1 records all six because it is the part every other part already writes through. **P3 is the next part built and it has nowhere else to put them**: if P1 ships without this row, P3 invents a second store, and P13's `progress_line` reads counters from a table that is not P1's.

**Recording is not bounding.** SPEC §10: *"§8.6 names a configurable ceiling for **none** of these six. P1 holds no threshold for any of them, rejects no operation for any value, and invents none — the twelve ceilings in Contract out §8 are a separate and unrelated set."* This module contains no comparison against any counter. Task 12's guard is extended to prove it.

**Absence reads as unknown, never as zero.** SPEC §10: *"A counter that could not be sampled is recorded as unavailable. §8.6's whole purpose is that deferred and unmeasured work stay visible as such rather than reading as work that completed cheaply."* Stdlib-only sampling cannot see everything §8.6 names — there is no network byte counter in the standard library, no portable current-RSS reading, and no accelerator time — so those sub-values are stored as `null` and the tests assert they are never `0`. Adding a third-party dependency to make them numbers is not in scope and would break the plan's stdlib-only constraint; what the SPEC asks for is that the gap be visible.

**`scan_id` stays off `events`.** SPEC §10: *"It is **not** added to `events` — §8.2's event record keeps its eleven fields (MINOR 1) and Done-means 7 still tests exactly eleven."* P1 mints the identifier locally. Whether it should become shared identity is **SPEC OQ19 and stays open** — if P2's replay or P13's progress line needs to join file counts to these counters, the identifier belongs wherever the scan is owned (P3), not here.

**Platform note.** `resource.getrusage(...).ru_maxrss` is **bytes on macOS** and kilobytes on Linux. v1 is macOS-only ([`../../11-ops-runtime.md`](../../11-ops-runtime.md)), so the value is recorded as bytes and the unit is named in the stored key rather than converted.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scan_usage.py
import json

from database_agent.db import create_schema
from database_agent.events import EVENT_FIELDS
from database_agent.scan_usage import (
    RESOURCE_COUNTERS, record_llm_cost, sample_scan_resources, scan_resource_usage,
    start_scan,
)


def test_the_six_resources_are_the_six_8_6_names():
    assert RESOURCE_COUNTERS == (
        "elapsed_time", "memory", "cpu_accelerator", "storage", "network", "llm_cost",
    )


def test_a_completed_scan_yields_one_row_carrying_all_six(conn):
    create_schema(conn)
    scan_id = start_scan(conn)
    sample_scan_resources(conn, scan_id)
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "0"}, author="P8")

    rows = conn.execute("SELECT * FROM scan_resource_usage").fetchall()
    assert len(rows) == 1
    row = scan_resource_usage(conn, scan_id)
    for counter in RESOURCE_COUNTERS:
        assert counter in row.keys()
    assert row["observed_at"]


def test_p1_samples_five_and_p8_writes_the_sixth(conn):
    # SPEC §10: llm_cost is written by P8, "the only part that can know it" (O9).
    create_schema(conn)
    scan_id = start_scan(conn)
    sample_scan_resources(conn, scan_id)
    assert scan_resource_usage(conn, scan_id)["llm_cost"] is None
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "1.25"}, author="P8")
    assert json.loads(scan_resource_usage(conn, scan_id)["llm_cost"])["amount"] == "1.25"


def test_an_unsampled_counter_reads_as_unavailable_never_as_zero(conn):
    # There is no network byte counter, no portable current-RSS reading and no
    # accelerator time in the standard library. Each reads as null, not 0.
    create_schema(conn)
    scan_id = start_scan(conn)
    sample_scan_resources(conn, scan_id)
    row = scan_resource_usage(conn, scan_id)

    assert row["network"] is None
    assert json.loads(row["memory"])["current_bytes"] is None
    assert json.loads(row["cpu_accelerator"])["accelerator_seconds"] is None
    for counter in RESOURCE_COUNTERS:
        assert row[counter] != 0
        assert row[counter] != "0"


def test_what_could_be_sampled_is_a_number(conn):
    create_schema(conn)
    scan_id = start_scan(conn)
    sample_scan_resources(conn, scan_id)
    row = scan_resource_usage(conn, scan_id)
    assert json.loads(row["elapsed_time"])["seconds"] >= 0
    assert json.loads(row["memory"])["peak_bytes"] > 0
    assert json.loads(row["cpu_accelerator"])["cpu_seconds"] >= 0
    assert json.loads(row["storage"])["database_bytes"] > 0


def test_p1_rejects_no_operation_for_any_value_of_any_counter(conn):
    # Done-means 16's negative test. Recording six counters gives P1 no ceiling on
    # any of them: there is no threshold to hit.
    create_schema(conn)
    scan_id = start_scan(conn)
    record_llm_cost(conn, scan_id, {"currency": "USD", "amount": "999999999"},
                    author="P8")
    sample_scan_resources(conn, scan_id)          # still samples
    assert scan_resource_usage(conn, scan_id) is not None
    # and the module holds no threshold to compare against
    import database_agent.scan_usage as module
    assert not [n for n in dir(module)
                if any(t in n.lower() for t in ("max_", "limit", "ceiling", "threshold"))]


def test_scan_id_is_on_none_of_the_event_fields(conn):
    # Done-means 16's second negative test, and MINOR 1.
    create_schema(conn)
    assert len(EVENT_FIELDS) == 11
    assert "scan_id" not in EVENT_FIELDS
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(events)")]
    assert "scan_id" not in columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scan_usage.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.scan_usage'`

- [ ] **Step 3: Add SCAN_USAGE_DDL to db.py and run it in create_schema**

```python
SCAN_USAGE_DDL = """
CREATE TABLE IF NOT EXISTS scan_resource_usage (
    scan_id         TEXT PRIMARY KEY,   -- minted by P1, deliberately not on events
    elapsed_time    TEXT,               -- every counter: JSON, or NULL for unavailable
    memory          TEXT,
    cpu_accelerator TEXT,
    storage         TEXT,
    network         TEXT,
    llm_cost        TEXT,               -- written by P8 (O9), never sampled here
    started_at      TEXT NOT NULL,      -- (mechanics) so elapsed_time is computable
    baseline        TEXT NOT NULL,      -- (mechanics) at-start samples, for deltas
    observed_at     TEXT
);
"""
```

Add `conn.executescript(SCAN_USAGE_DDL)` to `create_schema` in `db.py`. Every counter is nullable, and `NULL` is the only representation of *unavailable* — no counter defaults to `0`.

- [ ] **Step 4: Write the implementation**

```python
# src/database_agent/scan_usage.py
"""Contract out §10 — the §8.6 per-scan resource observability record (D1).

§8.6's first sentence names six resources: elapsed time, memory, CPU or accelerator
usage, storage, network use, and LLM cost. P1 records all six because it is the part
every other part already writes through. P13 renders them.

Recording is not bounding. §8.6 names a configurable ceiling for NONE of these six.
This module holds no threshold, rejects no operation, and derives no quality signal.
Absence reads as unknown: a counter that could not be sampled is NULL, never 0.
"""
from __future__ import annotations

import json
import resource
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

#: §8.6's six, in the order the design names them.
RESOURCE_COUNTERS: tuple[str, ...] = (
    "elapsed_time", "memory", "cpu_accelerator", "storage", "network", "llm_cost",
)


def _cpu_seconds() -> float:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime + usage.ru_stime


def _database_bytes(conn: sqlite3.Connection) -> int:
    """The database and its WAL/SHM sidecars. This is the storage P1 can count."""
    row = conn.execute("PRAGMA database_list").fetchone()
    path = Path(row["file"]) if row and row["file"] else None
    if path is None:
        return 0
    return sum(p.stat().st_size for p in
               (path, path.with_name(path.name + "-wal"), path.with_name(path.name + "-shm"))
               if p.exists())


def start_scan(conn: sqlite3.Connection) -> str:
    """Mint the scan identifier and open its row. §8.6 says "every scan" and no part
    publishes a scan id, so P1 mints one locally. Whether it should become shared
    identity is SPEC OQ19 and is not decided here."""
    scan_id = str(uuid.uuid4())
    baseline = json.dumps({
        "monotonic": time.monotonic(),
        "cpu_seconds": _cpu_seconds(),
    })
    conn.execute(
        "INSERT INTO scan_resource_usage (scan_id, started_at, baseline) VALUES (?, ?, ?)",
        (scan_id, datetime.now(timezone.utc).isoformat(), baseline),
    )
    return scan_id


def sample_scan_resources(conn: sqlite3.Connection, scan_id: str) -> None:
    """Sample the five counters P1 can observe. `llm_cost` is P8's (O9).

    Sub-values the standard library cannot supply are recorded as null: there is no
    network byte counter, no portable current-RSS reading, and no accelerator time.
    They are unavailable, which is not the same as zero (§8.6).
    """
    row = conn.execute(
        "SELECT baseline FROM scan_resource_usage WHERE scan_id = ?", (scan_id,)
    ).fetchone()
    baseline = json.loads(row["baseline"])
    # ru_maxrss is BYTES on macOS (v1 is macOS-only) and kilobytes on Linux.
    peak_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    conn.execute(
        "UPDATE scan_resource_usage SET elapsed_time = ?, memory = ?, "
        "cpu_accelerator = ?, storage = ?, network = ?, observed_at = ? "
        "WHERE scan_id = ?",
        (
            json.dumps({"seconds": time.monotonic() - baseline["monotonic"]}),
            json.dumps({"peak_bytes": peak_bytes, "current_bytes": None}),
            json.dumps({"cpu_seconds": _cpu_seconds() - baseline["cpu_seconds"],
                        "accelerator_seconds": None}),
            json.dumps({"database_bytes": _database_bytes(conn),
                        "log_bytes": None, "derived_artifact_bytes": None}),
            None,                       # unavailable, not zero
            datetime.now(timezone.utc).isoformat(),
            scan_id,
        ),
    )


def record_llm_cost(conn: sqlite3.Connection, scan_id: str, cost, *, author: str) -> None:
    """P8 is the single egress point and the only part that can know this (O9).
    P1 stores the value opaquely and compares it to nothing."""
    conn.execute(
        "UPDATE scan_resource_usage SET llm_cost = ?, observed_at = ? WHERE scan_id = ?",
        (json.dumps(cost), datetime.now(timezone.utc).isoformat(), scan_id),
    )


def scan_resource_usage(conn: sqlite3.Connection, scan_id: str) -> sqlite3.Row:
    """One row per scan, updated as the scan runs (Contract out §10)."""
    return conn.execute(
        "SELECT * FROM scan_resource_usage WHERE scan_id = ?", (scan_id,)
    ).fetchone()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_scan_usage.py -v`
Expected: PASS — 7 passed

- [ ] **Step 6: Run the full suite one final time**

Run: `pytest -v --tb=short`
Expected: PASS — every test from Tasks 1–14 green

- [ ] **Step 7: Commit**

```bash
git add src/database_agent/db.py src/database_agent/scan_usage.py tests/test_scan_usage.py
git commit -m "feat(P1): 8.6 per-scan resource record, six counters, unavailable is not zero"
```

---

## Self-Review

**Spec coverage.** Every Contract-out section has a task: §1 identity → Task 2, §2 files → Task 3, §3 events → Tasks 4–5, §4 supersede → Task 7, §5 verification → Task 8, §6 handle → Task 1, §7 learning → Task 9, §8 budget → Task 10, §9 vectors → Task 11, §10 scan resources → Task 14. Done-means 1–16 map as: 1→T3/T6, 2→T6, 3→T6, 4→T4, 5→T7, 6→T8, 7→T4, 8→T12, 9→T3/T11, 10→T13, 11→T5, 12→T5, 13→T9, 14→T10, 15→T11, 16→T14.

**Authorship.** P1 authors no event. `observe_path` (T6), `verify_content` and `confirm_cross_volume_copy` (T8), and `reset_preferences` (T9) all take the authoring part as a required keyword with no default, and `subsystem` is written from it. The single place `subsystem = "P1"` appears is V1–V4, where the SPEC itself names P1 as the *performer* of the comparison — and even there the caller must identify itself, and does so in §8.2's structured explanation. T6 and T13 both assert it: `test_p1_authors_none_of_the_scan_events` and the skeleton's `scan_authors` check fail if a P1-authored scan event returns.

**Registration.** T5 ships one frozen table compiled from the declaring SPECs. No `register_event_type`, no mutable mapping, no code path that adds a type after import; rule 1 is an import-time check. `test_the_module_publishes_no_registration_call` and `test_the_table_cannot_be_mutated_at_run_time` are the standing guards.

**Open questions this plan does not answer.** OQ9 (volume identifier) is left open and made unusable across sessions rather than silently answered — T2. OQ3 (events with no single file) is left open; T4/T9 stop the learning store from *depending* on the answer by giving the correction its own subject column. OQ19 (shared scan identity) is left open; T14 mints a local identifier and keeps it off `events`. OQ11's runtime half is bound to `11-ops-runtime.md` in T1; the bundle identifier it does not name is an argument, never a guess. I6 stays untouched: nothing here `DELETE`s from `events`.

**Placeholder scan.** No "TBD", no "add error handling", no "similar to Task N", no angle-bracket placeholder standing in for a real name. Every code step carries complete runnable code.

**Type consistency.** `observe_path` / `record_file` / `get_file` / `file_path_history` are spelled identically in Tasks 3, 6, 8, 13. `supersede_reason` never appears as `supersession_reason`. `VerificationPoint` members are V1–V4 in Tasks 8 and 13. `author`, `component_version` and `materialized` are spelled identically everywhere they appear.

## Known gaps, carried deliberately

- **`file_facts_history`, `group_memberships_history`, `placement_history`, `user_decisions_history`** (SPEC Contract out §2) are not implemented here: they project over tables owned by P6, P9 and P11, which do not exist yet. They are read surfaces P1 *guarantees*, and the guarantee is testable only once a neighbour writes rows. Add them when P6 lands.
- **`text_units`** (G1) lives in P1's database but is defined by P4. Not created here — P4 publishes the shape, and inventing one would be exactly the two-vocabularies failure this project already hit twice.
- **P11's eight event-type spellings** (Task 5). P11's SPEC declares eight typed specializations of `placement recommendation` in prose and publishes no identifiers, so the frozen table has 35 names where the SPEC's arithmetic says 43. P1 does not coin them. `test_p11s_eight_specializations_are_declared_but_unspelled` fails the day P11 publishes, which is the day they are added.
- **`file_path_history.volume_id`** (Task 6) is published as `NULL`. No per-observation volume value exists to return while OQ9 is open, and repeating the current within-session value across historical rows would be a fabrication. P12 cannot reconstruct an expected source volume from this surface yet, and must not be handed a plausible-looking wrong one instead.
- **Network bytes, current RSS and accelerator time** (Task 14) read as unavailable. The standard library supplies none of them and this plan adds no runtime dependency. §8.6 asks that unmeasured work stay visible as unmeasured, which `null` satisfies and `0` would not.
- **Schema migration.** `SCHEMA_VERSION` is stamped into `user_version` on every open and never compared. The first neighbouring table can land without one, but the first *change* to a P1 table cannot. Not blocking Tasks 1–14.
- **`create_schema` is not called by `open_database`.** Every caller must remember both. Not blocking, but the first neighbour that forgets gets a handle with no tables.
- **P1 Open questions** remain open and are not answered by this plan: OQ3, OQ4 (whether §8.2's five histories are physical or projections), OQ9, OQ13, OQ15, OQ16, OQ17, OQ18, OQ19, and the §8.4 deletion-versus-append-only conflict deferred to the P7 build (P7 OQ4, P5 OQ6, P13 OQ11). None blocks Tasks 1–14.

## Execution Handoff

Plan saved to `planning/parts/P1-storage-identity-provenance/PLAN.md`. Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints for review.

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
- **Nineteen reserved event names, verbatim from §8.2** — see Task 5.
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

tests/conftest.py                       shared fixtures: temp db, sample files
tests/test_identity.py                  Done-means 1, 2, 3
tests/test_files_table.py               Done-means 1, 2, 9
tests/test_events.py                    Done-means 4, 7, 11, 12
tests/test_supersede.py                 Done-means 5
tests/test_verify.py                    Done-means 6, 10
tests/test_learning.py                  Done-means 13
tests/test_budget.py                    Done-means 14
tests/test_vectors.py                   Done-means 15
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
- Produces: `open_database(path: Path) -> sqlite3.Connection`, `SCHEMA_VERSION: int`, `transaction(conn)` contextmanager.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_db.py
import sqlite3
from pathlib import Path
from database_agent.db import open_database, transaction


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
from contextlib import contextmanager
from pathlib import Path

SCHEMA_VERSION = 1


def open_database(path: Path) -> sqlite3.Connection:
    """Open (creating if absent) the single local database (§0)."""
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
from database_agent.db import SCHEMA_VERSION, open_database, transaction

__all__ = ["open_database", "transaction", "SCHEMA_VERSION"]
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
Expected: PASS — 3 passed

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
- Produces: `HASH_ALGORITHM: str`, `hash_file(path: Path) -> str`, `volume_id_for(path: Path) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_identity.py
from pathlib import Path

from database_agent.identity import HASH_ALGORITHM, hash_file, volume_id_for


def test_same_bytes_same_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"identical")
    b.write_bytes(b"identical")
    assert hash_file(a) == hash_file(b)


def test_different_bytes_different_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"one")
    b.write_bytes(b"two")
    assert hash_file(a) != hash_file(b)


def test_algorithm_is_recorded_alongside(tmp_path: Path):
    # §8.2 requires "Content hash and hash algorithm" — the name must be available.
    assert HASH_ALGORITHM
    assert isinstance(HASH_ALGORITHM, str)


def test_large_file_is_streamed_not_loaded(tmp_path: Path):
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (5 * 1024 * 1024))
    assert len(hash_file(big)) == 64


def test_volume_id_is_stable_for_same_volume(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    assert volume_id_for(a) == volume_id_for(b)
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
from pathlib import Path

HASH_ALGORITHM = "sha256"   # I2: matches P4's observation_key formula (§3.4 keys on this)
_CHUNK = 1024 * 1024


def hash_file(path: Path) -> str:
    """Content hash of a file's bytes, streamed. 64 hex chars."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def volume_id_for(path: Path) -> str:
    """§8.2's 'Filesystem volume or root identifier'.

    OPEN — P1 OQ9. `st_dev` is NOT stable across remount, rename, or cloud
    re-sync on macOS, so P12's cross-volume logic will misfire if this value is
    treated as durable. It is used here as a within-session identifier only.
    Do not persist a cross-session decision on it until OQ9 is closed.
    """
    return str(os.stat(path).st_dev)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_identity.py -v`
Expected: PASS — 5 passed

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
- Produces: `create_schema(conn)`, `FILES_COLUMNS: tuple[str, ...]`, `record_file(conn, path, *, parent_folder_context) -> str` returning `file_id`, `get_file(conn, file_id) -> sqlite3.Row`.

**Note on `directory_position`:** the published field name is §2.9's **parent-folder context**; `directory_position` is the physical column spelling only (MINOR 11). There is exactly one field. The keyword argument uses the published name; the column uses §1.2's word.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_files_table.py
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import FILES_COLUMNS, get_file, record_file


def test_record_file_writes_every_column(conn, sample_file: Path):
    create_schema(conn)
    file_id = record_file(conn, sample_file, parent_folder_context="corpus")
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
    volume_id                 TEXT NOT NULL,
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
import mimetypes
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
                parent_folder_context: str | None = None) -> str:
    """Create the `files` row. `parent_folder_context` is §2.9's published name;
    it is stored in the `directory_position` column (§1.2's word) — one field (MINOR 11)."""
    file_id = str(uuid.uuid4())
    stat = path.stat()
    conn.execute(
        f"INSERT INTO files ({','.join(FILES_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(FILES_COLUMNS))})",
        (
            file_id, str(path), path.name,
            unicodedata.normalize("NFC", path.name), path.suffix,
            parent_folder_context, volume_id_for(path),
            hash_file(path), HASH_ALGORITHM,
            stat.st_size, _timestamps(path),
            mimetypes.guess_type(path.name)[0], None,
            "recorded", "{}", None,
        ),
    )
    return file_id


def get_file(conn: sqlite3.Connection, file_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM files WHERE file_id = ?", (file_id,)).fetchone()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_files_table.py -v`
Expected: PASS — 3 passed

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
- Produces: `EVENT_FIELDS: tuple[str, ...]`, `append_event(conn, **fields) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_events.py
import sqlite3

import pytest

from database_agent.db import create_schema
from database_agent.events import EVENT_FIELDS, append_event


def _minimal(**overrides):
    row = dict(
        event_type="discovery", file_id="f1", content_hash="abc",
        subsystem="P3", observed_at="2026-08-19T00:00:00+00:00",
        explanation="fixture",
    )
    row.update(overrides)
    return row


def test_event_carries_the_eleven_fields(conn):
    create_schema(conn)
    event_id = append_event(conn, **_minimal())
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    for field in EVENT_FIELDS:
        assert field in row.keys()
    # "where applicable" fields legitimately empty
    assert row["old_path"] is None
    assert row["new_path"] is None
    assert row["prompt_fingerprint"] is None
    assert row["user_id"] is None


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
    correction_scope   TEXT
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

EVENT_FIELDS: tuple[str, ...] = (
    "event_type", "file_id", "content_hash", "old_path", "new_path",
    "subsystem", "component_version", "prompt_fingerprint", "user_id",
    "observed_at", "explanation",
)


def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id."""
    columns = [k for k in fields if k in (*EVENT_FIELDS, "correction_scope", "base_event_type")]
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_events.py -v`
Expected: PASS — 4 passed

- [ ] **Step 6: Commit**

```bash
git add src/database_agent/db.py src/database_agent/events.py tests/test_events.py
git commit -m "feat(P1): append-only events log enforced by trigger"
```

---

### Task 5: The event registration rule (Done-means 11, 12)

**Files:**
- Modify: `src/database_agent/events.py` — add the reserved nineteen, the registry, and writer validation
- Test: `tests/test_events.py` — extend

**Interfaces:**
- Consumes: `append_event` (Task 4).
- Produces: `RESERVED_EVENT_TYPES: frozenset[str]`, `register_event_type(part, name, *, base=None)`, `UnregisteredEventType`, `ReservedNameCollision`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_events.py`:

```python
from database_agent.events import (
    RESERVED_EVENT_TYPES, ReservedNameCollision, UnregisteredEventType,
    register_event_type,
)


def test_the_nineteen_reserved_names_are_present():
    assert len(RESERVED_EVENT_TYPES) == 19
    for name in ("discovery", "stat observation", "hashing", "extraction", "OCR",
                 "undo", "external modification detection", "planned move"):
        assert name in RESERVED_EVENT_TYPES


def test_writer_accepts_a_type_declared_by_another_part(conn):
    create_schema(conn)
    register_event_type("P13", "apply review approval")
    event_id = append_event(conn, **_minimal(event_type="apply review approval", subsystem="P13"))
    assert event_id


def test_writer_rejects_an_undeclared_type(conn):
    create_schema(conn)
    with pytest.raises(UnregisteredEventType):
        append_event(conn, **_minimal(event_type="invented at runtime"))


def test_redefining_a_reserved_name_is_rejected():
    with pytest.raises(ReservedNameCollision):
        register_event_type("P9", "discovery")


def test_a_specialization_stores_its_reserved_base_type(conn):
    create_schema(conn)
    register_event_type("P11", "residual set surfaced", base="placement recommendation")
    event_id = append_event(conn, **_minimal(event_type="residual set surfaced", subsystem="P11"))
    row = conn.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["base_event_type"] == "placement recommendation"


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

- [ ] **Step 3: Write the registration rule**

Insert into `src/database_agent/events.py`, above `append_event`:

```python
RESERVED_EVENT_TYPES: frozenset[str] = frozenset({
    "discovery", "stat observation", "hashing", "extraction", "OCR",
    "fact creation", "fact rejection", "graph-edge creation",
    "group membership proposal", "user group decision", "template application",
    "destination-tree edit", "placement recommendation",
    "filename-collision resolution", "planned move", "executed move",
    "failed move", "external modification detection", "undo",
})

_REGISTRY: dict[str, str | None] = {}


class UnregisteredEventType(Exception):
    """Rule 3: an unregistered type is rejected at the writer, never silently stored."""


class ReservedNameCollision(Exception):
    """Rule 1: the nineteen reserved names may not be redefined, narrowed, or reused."""


def register_event_type(part: str, name: str, *, base: str | None = None) -> None:
    """Rule 2: every non-reserved type is declared by the part that authors it."""
    if name in RESERVED_EVENT_TYPES:
        raise ReservedNameCollision(f"{name!r} is one of the nineteen reserved 8.2 names")
    if base is not None and base not in RESERVED_EVENT_TYPES:
        raise ReservedNameCollision(f"base {base!r} is not a reserved name")
    _REGISTRY[name] = base


def _known(name: str) -> bool:
    return name in RESERVED_EVENT_TYPES or name in _REGISTRY
```

Then change `append_event` to validate and to carry the base type:

```python
def append_event(conn: sqlite3.Connection, **fields) -> int:
    """Append one event. Returns its monotonic event_id."""
    event_type = fields.get("event_type")
    if not _known(event_type):
        raise UnregisteredEventType(
            f"{event_type!r} is neither reserved nor registered by a part's SPEC"
        )
    if event_type in _REGISTRY and _REGISTRY[event_type] is not None:
        fields.setdefault("base_event_type", _REGISTRY[event_type])
    columns = [k for k in fields if k in (*EVENT_FIELDS, "correction_scope", "base_event_type")]
    values = [fields[k] for k in columns]
    cursor = conn.execute(
        f"INSERT INTO events ({','.join(columns)}) VALUES ({','.join('?' * len(columns))})",
        values,
    )
    return cursor.lastrowid
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_events.py -v`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/events.py tests/test_events.py
git commit -m "feat(P1): event registration rule, nineteen reserved names, typed specializations"
```

---

### Task 6: Path history and content-change identity (Done-means 2, 3)

**Files:**
- Modify: `src/database_agent/files_table.py`
- Test: `tests/test_identity.py` — extend

**Interfaces:**
- Consumes: `append_event`, `record_file`, `hash_file`.
- Produces: `observe_path(conn, path, *, parent_folder_context) -> str`, `file_path_history(conn, file_id) -> list[sqlite3.Row]`, `invalidate_extraction_state(conn, file_id)`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_identity.py`:

```python
from database_agent.db import create_schema
from database_agent.files_table import (
    file_path_history, get_file, observe_path,
)


def test_a_moved_file_keeps_one_record_and_gains_path_history(conn, tmp_path: Path):
    # R2 (§8.2): the same content observed at a new path is the same file version.
    # The ORIGINAL is gone — this is a move, not a duplicate.
    create_schema(conn)
    first = tmp_path / "one.bin"
    first.write_bytes(b"same content")
    file_id = observe_path(conn, first, parent_folder_context="a")

    second = tmp_path / "moved" / "two.bin"
    second.parent.mkdir()
    second.write_bytes(b"same content")
    first.unlink()                       # the move: only one copy is live
    again = observe_path(conn, second, parent_folder_context="moved")

    assert again == file_id
    history = file_path_history(conn, file_id)
    assert [r["path"] for r in history] == [str(first), str(second)]


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

    id_a = observe_path(conn, a, parent_folder_context="root")
    id_b = observe_path(conn, b, parent_folder_context="root")

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
    first_id = observe_path(conn, p, parent_folder_context="root")

    p.write_bytes(b"version two")
    second_id = observe_path(conn, p, parent_folder_context="root")

    assert second_id != first_id
    assert get_file(conn, second_id)["extraction_status_by_tier"] == "{}"
    assert get_file(conn, first_id)["scan_state"] == "superseded_content"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_identity.py -v`
Expected: FAIL with `ImportError: cannot import name 'observe_path'`

- [ ] **Step 3: Write the implementation**

Append to `src/database_agent/files_table.py`:

```python
from database_agent.events import append_event


def observe_path(conn: sqlite3.Connection, path: Path, *,
                 parent_folder_context: str | None = None) -> str:
    """R2/R3 — resolve a path observation to a file version (§8.2).

    Same bytes at a new path where the old path is gone: same file version, path
    updated, history retained (a move).
    Same bytes at a new path where BOTH are live: two records sharing one
    content_hash (I1) — §2.9's duplicate family and §8.3's identical-file collision
    both require the two copies to remain distinguishable.
    New bytes: a new version; the prior row's extraction state is invalidated so
    the relevant extractors re-run. P1 does not run them — that is P5.
    """
    content_hash = hash_file(path)
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
                new_path=str(path), subsystem="P1",
                observed_at=datetime.now(timezone.utc).isoformat(),
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
        conn.execute(
            "UPDATE files SET scan_state = 'superseded_content', "
            "extraction_status_by_tier = '{}' WHERE file_id = ?",
            (prior["file_id"],),
        )

    file_id = record_file(conn, path, parent_folder_context=parent_folder_context)
    append_event(
        conn, event_type="hashing", file_id=file_id, content_hash=content_hash,
        new_path=str(path), subsystem="P1",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation="new content hash recorded (R1, R3)",
    )
    return file_id


def file_path_history(conn: sqlite3.Connection, file_id: str) -> list[sqlite3.Row]:
    """§8.2 'Path history' — a projection over events carrying old/new paths."""
    return conn.execute(
        "SELECT COALESCE(new_path, old_path) AS path, observed_at, event_id "
        "FROM events WHERE file_id = ? AND (new_path IS NOT NULL OR old_path IS NOT NULL) "
        "ORDER BY event_id",
        (file_id,),
    ).fetchall()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_identity.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/files_table.py tests/test_identity.py
git commit -m "feat(P1): path-change and content-change identity with retained history"
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
- Produces: `VerificationPoint` (enum V1–V4), `verify_content(conn, file_id, expected_hash, *, point) -> "match" | "mismatch"`, `confirm_cross_volume_copy(conn, *, source, destination, expected_hash) -> bool`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_verify.py
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import observe_path
from database_agent.identity import hash_file
from database_agent.verify import (
    VerificationPoint, confirm_cross_volume_copy, verify_content,
)


def test_all_four_points_exist():
    assert [p.name for p in VerificationPoint] == ["V1", "V2", "V3", "V4"]


def test_verify_returns_match_for_unchanged_content(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, parent_folder_context="corpus")
    expected = hash_file(sample_file)
    for point in VerificationPoint:
        if point is VerificationPoint.V4:
            continue
        assert verify_content(conn, file_id, expected, point=point) == "match"


def test_verify_returns_mismatch_after_content_changes(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, parent_folder_context="corpus")
    expected = hash_file(sample_file)
    sample_file.write_bytes(b"different bytes entirely")
    assert verify_content(conn, file_id, expected, point=VerificationPoint.V1) == "mismatch"


def test_v4_refuses_success_until_destination_hash_is_confirmed(conn, tmp_path: Path):
    create_schema(conn)
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload")
    good = tmp_path / "good.bin"
    good.write_bytes(b"payload")
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"truncated")
    expected = hash_file(source)

    assert confirm_cross_volume_copy(conn, source=source, destination=good,
                                     expected_hash=expected) is True
    assert confirm_cross_volume_copy(conn, source=source, destination=bad,
                                     expected_hash=expected) is False


def test_verification_is_recorded_as_an_event(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, parent_folder_context="corpus")
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    verify_content(conn, file_id, hash_file(sample_file), point=VerificationPoint.V2)
    after = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
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
"""
from __future__ import annotations

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


def verify_content(conn: sqlite3.Connection, file_id: str, expected_hash: str, *,
                   point: VerificationPoint) -> str:
    """Return 'match' or 'mismatch'. Records the check; interprets nothing."""
    row = get_file(conn, file_id)
    actual = hash_file(Path(row["current_path"]))
    result = "match" if actual == expected_hash else "mismatch"
    append_event(
        conn, event_type="stat observation", file_id=file_id, content_hash=actual,
        subsystem="P1", observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=f"{point.name}: {point.value} -> {result}",
    )
    return result


def confirm_cross_volume_copy(conn: sqlite3.Connection, *, source: Path,
                              destination: Path, expected_hash: str) -> bool:
    """V4 — the destination copy is hashed and confirmed BEFORE the source may be
    removed (§8.2). P1 never removes the source; it only answers whether it may be."""
    confirmed = destination.exists() and hash_file(destination) == expected_hash
    append_event(
        conn, event_type="stat observation", content_hash=expected_hash,
        old_path=str(source), new_path=str(destination), subsystem="P1",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=f"V4 destination confirmation -> {'confirmed' if confirmed else 'refused'}",
    )
    return confirmed
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_verify.py -v`
Expected: PASS — 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/verify.py tests/test_verify.py
git commit -m "feat(P1): V1-V4 fixity verification, V4 refuses until destination confirmed"
```

---

### Task 9: The §8.7 learning-record store (Done-means 13)

**Files:**
- Create: `src/database_agent/learning.py`
- Test: `tests/test_learning.py`

**Interfaces:**
- Consumes: `append_event`.
- Produces: `SCOPES: tuple[str, ...]`, `learning_records(conn, scope, subject_id) -> list`, `reset_preferences(conn, scope, subject_id) -> int`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_learning.py
from datetime import datetime, timezone

import pytest

from database_agent.db import create_schema
from database_agent.events import append_event, register_event_type
from database_agent.learning import SCOPES, learning_records, reset_preferences


def _correction(conn, scope, subject, explanation):
    return append_event(
        conn, event_type="user group decision", file_id=subject,
        subsystem="P9", observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=explanation, correction_scope=scope, user_id="u1",
    )


def test_the_six_scopes():
    assert SCOPES == ("file", "group", "node", "template", "domain", "corpus")


def test_a_file_scoped_correction_is_not_returned_by_a_corpus_read(conn):
    # §8.7's worked case: one transcript belonging in a Columbia packet must not
    # teach the engine that all transcripts belong there.
    create_schema(conn)
    _correction(conn, "file", "f1", "this one belongs here")
    assert learning_records(conn, "corpus", "f1") == []
    assert len(learning_records(conn, "file", "f1")) == 1


def test_a_rejection_returns_with_its_evidence(conn):
    create_schema(conn)
    _correction(conn, "group", "g1", "rejected: evidence_ref=obs-key-123")
    records = learning_records(conn, "group", "g1")
    assert "obs-key-123" in records[0]["explanation"]


def test_reset_appends_and_deletes_nothing(conn):
    create_schema(conn)
    _correction(conn, "domain", "d1", "first preference")
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    reset_preferences(conn, "domain", "d1")
    after = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    assert after == before + 1
    # pre-reset records stay readable (R6)
    assert any("first preference" in r["explanation"] for r in learning_records(conn, "domain", "d1"))


def test_unknown_scope_is_rejected(conn):
    create_schema(conn)
    with pytest.raises(ValueError):
        learning_records(conn, "everything", "x")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_learning.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'database_agent.learning'`

- [ ] **Step 3: Write the implementation**

```python
# src/database_agent/learning.py
"""Contract out §7 — the §8.7 learning-record store.

A scoped projection over `events`, not a new authority and not a second log.
P1 does not learn: no weighting, no generalization, no ranking, no application.
What a record means is decided by the part that authored the correction.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

SCOPES: tuple[str, ...] = ("file", "group", "node", "template", "domain", "corpus")
_RESET_TYPE = "preference reset"


def _check(scope: str) -> None:
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; §8.7 defines exactly {SCOPES}")


def learning_records(conn: sqlite3.Connection, scope: str,
                     subject_id: str) -> list[sqlite3.Row]:
    """User-action events at that scope for that subject, newest first, each with
    its §8.2 explanation. Scope is the filter, and it is exact."""
    _check(scope)
    return conn.execute(
        "SELECT * FROM events WHERE correction_scope = ? AND file_id = ? "
        "AND user_id IS NOT NULL ORDER BY event_id DESC",
        (scope, subject_id),
    ).fetchall()


def reset_preferences(conn: sqlite3.Connection, scope: str, subject_id: str) -> int:
    """Append a scoped reset record. Deletes nothing (R6)."""
    _check(scope)
    from database_agent.events import _REGISTRY, append_event
    if _RESET_TYPE not in _REGISTRY:
        _REGISTRY[_RESET_TYPE] = None
    return append_event(
        conn, event_type=_RESET_TYPE, file_id=subject_id, subsystem="P1",
        observed_at=datetime.now(timezone.utc).isoformat(),
        explanation=f"preferences reset at scope {scope}", correction_scope=scope,
        user_id="reset",
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_learning.py -v`
Expected: PASS — 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/database_agent/learning.py tests/test_learning.py
git commit -m "feat(P1): 8.7 learning projection, exact scope, append-only reset"
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

    # P1: hash it, create the file record, append a discovery event.
    file_id = observe_path(conn, document, parent_folder_context="corpus")
    append_event(
        conn, event_type="discovery", file_id=file_id,
        content_hash=hash_file(document), new_path=str(document),
        subsystem="P3", observed_at=datetime.now(timezone.utc).isoformat(),
        explanation="skeleton fixture stands in for P3",
    )

    row = get_file(conn, file_id)
    assert row["content_hash"] == hash_file(document)
    assert row["hash_algorithm"]
    assert row["volume_id"]

    discovery = conn.execute(
        "SELECT * FROM events WHERE event_type = 'discovery' AND file_id = ?", (file_id,)
    ).fetchone()
    assert discovery is not None

    # P12's step reaches V1-V4 and gets true answers.
    for point in (VerificationPoint.V1, VerificationPoint.V2, VerificationPoint.V3):
        assert verify_content(conn, file_id, row["content_hash"], point=point) == "match"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_skeleton_p1_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest -v --tb=short`
Expected: PASS — every test green

- [ ] **Step 4: Commit**

```bash
git add tests/test_skeleton_p1_step.py
git commit -m "test(P1): walking-skeleton P1 step, deterministic, no model"
```

---

## Self-Review

**Spec coverage.** Every Contract-out section has a task: §1 identity → Task 2, §2 files → Task 3, §3 events → Tasks 4–5, §4 supersede → Task 7, §5 verification → Task 8, §6 handle → Task 1, §7 learning → Task 9, §8 budget → Task 10, §9 vectors → Task 11. Done-means 1–15 map as: 1→T3/T6, 2→T6, 3→T6, 4→T4, 5→T7, 6→T8, 7→T4, 8→T12, 9→T3/T11, 10→T13, 11→T5, 12→T5, 13→T9, 14→T10, 15→T11.

**Placeholder scan.** No "TBD", no "add error handling", no "similar to Task N". Every code step carries complete runnable code.

**Type consistency.** `observe_path` / `record_file` / `get_file` / `file_path_history` are spelled identically in Tasks 3, 6, 8 and 13. `supersede_reason` never appears as `supersession_reason`. `VerificationPoint` members are V1–V4 in both Task 8 and Task 13.

## Known gaps, carried deliberately

- **`file_facts_history`, `group_memberships_history`, `placement_history`, `user_decisions_history`** (SPEC Contract out §2) are not implemented here: they project over tables owned by P6, P9 and P11, which do not exist yet. They are read surfaces P1 *guarantees*, and the guarantee is testable only once a neighbour writes rows. Add them when P6 lands.
- **`text_units`** (G1) lives in P1's database but is defined by P4. Not created here — P4 publishes the shape, and inventing one would be exactly the two-vocabularies failure this project already hit twice.
- **P1 Open questions** remain open and are not answered by this plan: whether §8.2's five histories are intended physically on the file record rather than as projections, and the §8.4 deletion-versus-append-only conflict (P7 OQ4, P5 OQ6, P13 OQ11). Neither blocks Tasks 1–13.

## Execution Handoff

Plan saved to `planning/parts/P1-storage-identity-provenance/PLAN.md`. Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints for review.

# P3 — Scan and Corpus Selection — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn an explicit user selection of folders into a populated `files` table and a recorded corpus boundary — §1.1's exclusion rules, §1.2's ten-field basic record and stat cache, the directory inventory behind §5.10's canvas, and the five §8.6 scan counters — with every scan event **authored by P3** and written through P1.

**Architecture:** P3 is a second package (`src/scan_agent/`) inside P1's single local SQLite database (§0). It owns six tables and writes `files` rows and `events` rows only through P1's published functions. The traversal is a **pure generator** (`walk`) with no database access; a separate writer (`scan`) turns what it yields into rows. That split is what makes Done-means 16 provable — the curation signal is computed in the generator and cannot reach the exclusion or cache decisions, because those are made before the writer ever sees it.

**Tech Stack:** Python 3.12 · stdlib only (`sqlite3`, `os`, `hashlib` via P1) · `pytest` · P1's `database_agent` package · no third-party runtime dependencies.

---

## The authorship rule — read this before Task 1

**P3 authors the scan events; P1 only writes them.** This is the single load-bearing rule of this plan and half of a contract whose other half already exists: P1's plan carries `test_p1_authors_none_of_the_scan_events`, which asserts that every event row an observation produces names its caller. P3 is that caller.

P1's SPEC (Cross-cutting answers → Provenance, M8): *"The acting part authors; P1 writes. P1 appends no event on its own initiative."* P1's Contract in: *"accept the `discovery`, `stat observation`, `hashing` and `external modification detection` events **P3 authors** (M8) — P1 originates none of them."*

Concretely, in this plan:

- Every call into `observe_path` and `append_event` passes `author="P3"` / `subsystem="P3"` from `scan_agent.authorship.SUBSYSTEM`. There is no other value and no default anywhere in `scan_agent`.
- P3 authors exactly four of §8.2's nineteen reserved types — `discovery`, `stat observation`, `hashing`, `external modification detection` — and **registers nothing** (B5): all four are reserved §8.2 names, already in P1's frozen table, so `scan_agent` contains no registration call and no new type name.
- `external modification detection` has **two** authors (M8). P3's half is the re-scan (§1.2) and the session watch (`11-ops-runtime.md` §4); P12's half is §8.3 staleness. Both rows survive and are separated by `subsystem`.
- Task 17's guard asserts the negative: no row P3 writes carries `subsystem = "P1"`, and `scan_agent` contains no author value other than `"P3"`.

---

## Global Constraints

Every task's requirements implicitly include these.

- **P3 decides nothing about meaning.** §1.2: *"This pass does not decide what a file means or where it belongs."* §1.1: *"No sorting decision is made."* No fact name, domain name, template name, sensitivity class, tier name, destination, or placement appears anywhere in `scan_agent` (Task 17).
- **`events` is INSERT-only.** P1 enforces it by SQL trigger. P3 issues no `UPDATE` and no `DELETE` against `events`, ever.
- **P3 writes no `extraction_runs` row.** That record is P4's and P5 is its writer. In particular, a dataless iCloud file gets a detection record and **no** run row; which `completeness` value such a file eventually carries is **P4 Open question 6** and is not resolved here, or anywhere in this plan. The strings `extraction_runs` and `completeness` do not appear in `scan_agent` (Task 17).
- **P3 never hashes a dataless file.** `11-ops-runtime.md` §5: *"Do not materialize, hash, or extract."* P1's `hash_file` takes a required `materialized` keyword and raises `DatalessFileRefused`; **P3 detects before hashing** and never passes `materialized=True` for a path it detected as dataless.
- **Full Disk Access before traversal.** `11-ops-runtime.md` §1: *"Until it is granted, P3 does not traverse."* Checked once per scan, before the first directory is listed (Task 8).
- **No invented values.** No numeric threshold, no ceiling value, no gazetteer, no category membership, no scan-state enumeration, no MIME determination method. Where the design leaves a value open, this plan holds a **key or a caller-supplied strategy, never a number and never a vocabulary**.
- **No durable volume identifier is built on.** P1 OQ9 is open; P1's `volume_id` is session-tagged and nullable on purpose. `scan_agent` reads it for nothing and compares it to nothing.
- **P3's scan-run handle is local and unpublished.** SPEC OQ16 is open. See Task 3.
- **Fixture directories, never the user's disk.** Every test builds its corpus under `tmp_path`.
- **Python 3.12**, stdlib only. `scan_agent` adds no third-party dependency.
- **P3 creates and modifies no P1 file.** `pyproject.toml`, `tests/conftest.py` and everything under `src/database_agent/` belong to P1. P1's `[tool.setuptools.packages.find] where = ["src"]` already discovers `scan_agent`, and P1's `pythonpath = ["src"]` already makes it importable under pytest, so nothing in P1 needs to change. P3's tests live in `tests/p3/` with their own `conftest.py`, and inherit P1's root fixtures (`conn`, `sample_file`) without editing them.

---

## What P3 consumes from P1

Written against the interfaces P1's plan **Produces**. Nothing else in `database_agent` is touched.

```text
database_agent.db          open_database(path, *, scan_roots=()) -> sqlite3.Connection
                           create_schema(conn) -> None
                           transaction(conn)                      contextmanager
database_agent.identity    HASH_ALGORITHM: str
                           hash_file(path, *, materialized: bool) -> str
                           DatalessFileRefused
database_agent.files_table record_file(conn, path, *, parent_folder_context, mime_type,
                                       detected_format, scan_state, materialized) -> str
                           observe_path(conn, path, *, author, component_version,
                                        parent_folder_context, mime_type, detected_format,
                                        scan_state, materialized) -> str
                           get_file(conn, file_id) -> sqlite3.Row
                           file_path_history(conn, file_id) -> list[sqlite3.Row]
database_agent.events      append_event(conn, **fields) -> int
                           RESERVED_EVENT_TYPES: frozenset[str]
                           EVENT_FIELDS: tuple[str, ...]          (eleven)
database_agent.scan_usage  start_scan(conn) -> str
                           sample_scan_resources(conn, scan_id) -> None
                           scan_resource_usage(conn, scan_id) -> sqlite3.Row
```

**`detected_format` is not one of P3's ten fields.** R2 lists ten and `detected_format` is not among them — it is §8.2's file-record field, and §2.9's *"inspect the real MIME type or file signature"* is P5's territory. P1's `record_file` requires the keyword, so P3 passes `detected_format=None` and invents no value another part owns. Task 10 asserts the column is `NULL` on every row P3 writes.

---

## File Structure

```text
src/scan_agent/__init__.py          package marker; exports scan
src/scan_agent/authorship.py        P3 is the author — subsystem, version, the four event types
src/scan_agent/schema.py            create_scan_schema — P3's six tables, all inside P1's database
src/scan_agent/selection.py         Contract out R1 — the corpus selection record (§1.1)
src/scan_agent/run.py               P3's local scan-run handle (OQ16 held open)
src/scan_agent/exclusion.py         Contract out R3 — §1.1's rules and the verdict record
src/scan_agent/dataless.py          11-ops-runtime.md §5 — detect before hashing
src/scan_agent/corpus_source.py     §8.5 — one interface over a live filesystem and a snapshot
src/scan_agent/access.py            11-ops-runtime.md §1 — Full Disk Access before traversal
src/scan_agent/traversal.py         the pure generator: exclusion, inventory, deferral
src/scan_agent/basic_record.py      Contract out R2 — the ten §1.2 fields, through P1
src/scan_agent/stat_cache.py        Contract out R4 — reuse | recompute
src/scan_agent/inventory.py         Contract out R6 — directory inventory, curation signal
src/scan_agent/summary.py           Contract out R5 — the five §8.6 counters
src/scan_agent/scan.py              the writer: composes the above into one scan run
src/scan_agent/watch.py             11-ops-runtime.md §4 — the session watch

tests/p3/conftest.py                fixture corpus builders, recording fakes
tests/p3/test_p3_authorship.py      the authorship rule
tests/p3/test_p3_selection.py       Done-means 12
tests/p3/test_p3_run.py             OQ16 held open
tests/p3/test_p3_exclusion.py       Done-means 3, 4, 5, 6
tests/p3/test_p3_dataless.py        11 §5
tests/p3/test_p3_corpus_source.py   §8.5 groundwork
tests/p3/test_p3_access.py          11 §1
tests/p3/test_p3_traversal.py       Done-means 2, 3, 4, 5, 6
tests/p3/test_p3_basic_record.py    Done-means 1, 10, 11
tests/p3/test_p3_stat_cache.py      Done-means 7, 8, 9, 18
tests/p3/test_p3_inventory.py       Done-means 15, 16
tests/p3/test_p3_summary.py         Done-means 13
tests/p3/test_p3_replay.py          Done-means 14
tests/p3/test_p3_watch.py           11 §4
tests/p3/test_p3_no_invention.py    Done-means 17, and every open question held open
tests/p3/test_p3_skeleton_step.py   02-segmentation-map.md's P3 step
```

Files split by published record, not by technical layer — each module is one Contract-out record, so a reviewer can reject one without touching its neighbours.

---

### Task 1: Package skeleton and P3's authorship constants

**Files:**
- Create: `src/scan_agent/__init__.py`
- Create: `src/scan_agent/authorship.py`
- Create: `tests/p3/conftest.py`
- Test: `tests/p3/test_p3_authorship.py`

**Interfaces:**
- Consumes: `database_agent.events.RESERVED_EVENT_TYPES`.
- Produces: `SUBSYSTEM: str`, `COMPONENT_VERSION: str`, `AUTHORED_EVENT_TYPES: tuple[str, str, str, str]`, `event_defaults(**fields) -> dict`.

**Why this is Task 1.** Every later task appends events, and the one thing that must never be got wrong is whose name lands in `subsystem`. Putting the constant and its four types first means no later task has a plausible reason to type `"P3"` again by hand, and Task 17's guard has exactly one place to look.

**`event_defaults` is a helper, not a writer.** It fills in §8.2's authorship fields — `subsystem`, `component_version`, `observed_at` — and returns a plain `dict` for the caller to hand to P1's `append_event`. It opens no connection and writes nothing, so there is no code path where P3 appends an event without a caller having decided to.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_authorship.py
from database_agent.events import RESERVED_EVENT_TYPES

from scan_agent.authorship import (
    AUTHORED_EVENT_TYPES, COMPONENT_VERSION, SUBSYSTEM, event_defaults,
)


def test_p3_names_itself_as_the_author():
    # M8: the acting part authors; P1 writes. There is one value and no default.
    assert SUBSYSTEM == "P3"


def test_p3_authors_exactly_the_four_types_its_spec_names():
    # SPEC Cross-cutting answers -> Provenance: discovery, stat observation,
    # scan-time hashing, external modification detection. No fifth.
    assert AUTHORED_EVENT_TYPES == (
        "discovery",
        "stat observation",
        "hashing",
        "external modification detection",
    )


def test_every_type_p3_authors_is_one_of_8_2s_reserved_nineteen():
    # B5: "P3 registers no new event type." All four are reserved §8.2 names, so
    # P1's frozen table already holds them and P3 declares nothing.
    assert set(AUTHORED_EVENT_TYPES) <= set(RESERVED_EVENT_TYPES)


def test_p3_publishes_no_registration_call():
    # Registration is a spec-level act (P1 Contract out §3, rule 4). P3 mints nothing.
    import scan_agent.authorship as module
    assert not [name for name, value in vars(module).items()
                if callable(value) and name.lower().startswith("register")]


def test_event_defaults_fill_in_8_2s_authorship_fields():
    fields = event_defaults(event_type="discovery", file_id="f1", content_hash="abc")
    assert fields["subsystem"] == "P3"
    assert fields["component_version"] == COMPONENT_VERSION
    assert fields["observed_at"]
    assert fields["event_type"] == "discovery"
    assert fields["file_id"] == "f1"


def test_event_defaults_refuse_a_type_p3_does_not_author():
    # Two authors share `external modification detection` (M8); nothing else is
    # shared. P3 must not put its name on P5's `extraction` or P12's `executed move`.
    import pytest
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1")


def test_event_defaults_cannot_be_told_to_name_another_subsystem():
    import pytest
    with pytest.raises(ValueError):
        event_defaults(event_type="discovery", file_id="f1", subsystem="P1")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_authorship.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/__init__.py
"""P3 — scan and corpus selection. The only part that walks the filesystem."""
```

```python
# src/scan_agent/authorship.py
"""P3 is the author of its scan events; P1 is only their writer (M8).

P1's SPEC: "The acting part authors; P1 writes. P1 appends no event on its own
initiative." P1's Contract in: "accept the `discovery`, `stat observation`,
`hashing` and `external modification detection` events P3 authors — P1 originates
none of them."

All four are reserved §8.2 names, already present in P1's frozen event-type table,
so P3 registers nothing (B5) and mints nothing at run time.
"""
from __future__ import annotations

from datetime import datetime, timezone

#: §8.2's "responsible subsystem" for every event this part appends.
SUBSYSTEM = "P3"

#: §8.2's "extractor or model version" field. P1's Done-means 7 requires it populated.
COMPONENT_VERSION = "P3/0.1.0"

#: The four reserved §8.2 types P3 authors, in the SPEC's order.
#: `external modification detection` has a second author, P12 (§8.3) — M8. The two
#: routes are independent and separable by `subsystem`.
AUTHORED_EVENT_TYPES: tuple[str, str, str, str] = (
    "discovery",
    "stat observation",
    "hashing",
    "external modification detection",
)


def event_defaults(**fields) -> dict:
    """Fill in §8.2's authorship fields and return the row for P1's `append_event`.

    This helper writes nothing and holds no connection: P3 authors, and the caller
    still has to decide that an event is due and hand it to P1.
    """
    event_type = fields.get("event_type")
    if event_type not in AUTHORED_EVENT_TYPES:
        raise ValueError(
            f"P3 does not author {event_type!r}; it authors {AUTHORED_EVENT_TYPES}"
        )
    if fields.get("subsystem", SUBSYSTEM) != SUBSYSTEM:
        raise ValueError(
            f"P3 events name P3 as the responsible subsystem, not "
            f"{fields['subsystem']!r} (M8)"
        )
    return {
        **fields,
        "subsystem": SUBSYSTEM,
        "component_version": COMPONENT_VERSION,
        "observed_at": fields.get(
            "observed_at", datetime.now(timezone.utc).isoformat()
        ),
    }
```

```python
# tests/p3/conftest.py
"""Fixtures for P3. P1's root tests/conftest.py supplies `conn` and `sample_file`
and is NOT modified here."""
from pathlib import Path

import pytest


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    """A fixture corpus. Every P3 test scans this, never the user's disk."""
    root = tmp_path / "corpus"
    root.mkdir()
    return root


def write(path: Path, data: bytes = b"fixture bytes") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_authorship.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/__init__.py src/scan_agent/authorship.py tests/p3/conftest.py tests/p3/test_p3_authorship.py
git commit -m "feat(P3): authorship constants, the four reserved event types P3 authors"
```

---

### Task 2: R1 — the corpus selection record (Done-means 12)

**Files:**
- Create: `src/scan_agent/selection.py`
- Create: `src/scan_agent/schema.py`
- Test: `tests/p3/test_p3_selection.py`

**Interfaces:**
- Consumes: `database_agent.db.create_schema` (P1's tables must exist first).
- Produces: `SELECTION_COLUMNS: tuple[str, ...]`, `SELECTION_DDL: str`, `create_scan_schema(conn) -> None`, `record_selection(conn, *, sources, candidate_roots, cross_folder_moves, selected_by) -> str`, `get_selection(conn, selection_id) -> sqlite3.Row`, `selection_sources(conn, selection_id) -> list[Path]`, `selection_candidate_roots(conn, selection_id) -> list[Path]`.

**§1.1 names three selections and P3 owns no others.** *"The user first chooses which folders should be analyzed and which high-level locations may serve as roots for a future file tree… The user can also select whether files may move across high-level folders."* Sources, candidate roots, and the cross-folder-move flag. All three are **required keywords with no default**: §1.1 assigns the choice to the user, so P3 must not derive a corpus from the machine's layout, and an omitted flag is a `TypeError` rather than a guessed policy.

**Roots are context, not permission** (§1.1: *"At this stage, roots are context for the proposal canvas, not permission to move files"*). Done-means 12 is a negative, so it is tested as one: the record has no destination column, no permission column, and no authorization surface, and the module publishes no function that could hand one out.

**`selected_by` is nullable and required.** MINOR 10 / P1 OQ14: §8.2 records user identity *"when there is an explicit user action"*. §1.1's selection **is** such an action, so a user-made R1 carries the identity; an R1 not authored by a user leaves it empty, and empty is a correct value rather than a missing one. So the keyword has no default (the caller must say) and the value may be `None`.

**`cross_folder_moves` is recorded here and enforced nowhere in P3** (SPEC Q12 — *"Where `cross_folder_moves` is enforced"* — is OPEN). Task 17's guard asserts that no P3 code branches on it.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_selection.py
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.schema import create_scan_schema
from scan_agent.selection import (
    SELECTION_COLUMNS, get_selection, record_selection, selection_candidate_roots,
    selection_sources,
)


@pytest.fixture()
def schema(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_a_selection_carries_exactly_1_1s_three_choices(schema, tmp_path: Path):
    selection_id = record_selection(
        schema,
        sources=[tmp_path / "Downloads"],
        candidate_roots=[tmp_path / "Documents"],
        cross_folder_moves=True,
        selected_by="user-1",
    )
    row = get_selection(schema, selection_id)
    assert selection_sources(schema, selection_id) == [tmp_path / "Downloads"]
    assert selection_candidate_roots(schema, selection_id) == [tmp_path / "Documents"]
    assert row["cross_folder_moves"] == 1
    assert row["selected_at"]
    assert row["selected_by"] == "user-1"


def test_all_three_selections_are_required_with_no_default(schema, tmp_path: Path):
    # §1.1 assigns the choice to the user. P3 has no source set and no root set
    # until one is supplied, and derives neither from the machine's layout.
    with pytest.raises(TypeError):
        record_selection(schema, sources=[tmp_path], candidate_roots=[])
    with pytest.raises(TypeError):
        record_selection(schema, sources=[tmp_path], cross_folder_moves=False,
                         selected_by=None)


def test_selected_by_is_nullable_and_is_a_correct_value_when_empty(schema, tmp_path: Path):
    # MINOR 10 / P1 OQ14: user identity is recorded "when there is an explicit user
    # action". An R1 not authored by a user leaves the field empty, and empty is a
    # correct value rather than a missing one.
    selection_id = record_selection(
        schema, sources=[tmp_path], candidate_roots=[], cross_folder_moves=False,
        selected_by=None,
    )
    assert get_selection(schema, selection_id)["selected_by"] is None


def test_selecting_a_root_produces_no_move_authorization(schema, tmp_path: Path):
    # Done-means 12, and §1.1: "roots are context for the proposal canvas, not
    # permission to move files." Tested as the negative it is.
    record_selection(schema, sources=[], candidate_roots=[tmp_path / "Desktop"],
                     cross_folder_moves=True, selected_by=None)
    columns = [r["name"] for r in schema.execute("PRAGMA table_info(corpus_selections)")]
    for forbidden in ("destination", "placement", "permission", "authorized",
                      "target_node", "approved"):
        assert not any(forbidden in c.lower() for c in columns), forbidden

    import scan_agent.selection as module
    for name in vars(module):
        assert not any(t in name.lower() for t in ("authorize", "permit", "destination",
                                                   "placement"))


def test_the_selection_record_has_exactly_1_1s_fields(schema):
    assert SELECTION_COLUMNS == (
        "selection_id", "sources", "candidate_roots", "cross_folder_moves",
        "selected_at", "selected_by",
    )
    columns = [r["name"] for r in schema.execute("PRAGMA table_info(corpus_selections)")]
    assert tuple(columns) == SELECTION_COLUMNS


def test_an_empty_source_set_is_stored_as_an_empty_set(schema, tmp_path: Path):
    # Done-means 2's precondition: no default corpus is synthesized at record time
    # any more than at scan time.
    selection_id = record_selection(schema, sources=[], candidate_roots=[],
                                    cross_folder_moves=False, selected_by=None)
    assert selection_sources(schema, selection_id) == []
    assert selection_candidate_roots(schema, selection_id) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_selection.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.schema'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/selection.py
"""Contract out R1 — the corpus selection record (§1.1).

§1.1: "The user first chooses which folders should be analyzed and which high-level
locations may serve as roots for a future file tree… The user can also select whether
files may move across high-level folders."

Three selections, and P3 owns no others. Roots are CONTEXT, not permission: "At this
stage, roots are context for the proposal canvas, not permission to move files."
Nothing in this module authorizes, targets, or approves anything.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

SELECTION_COLUMNS: tuple[str, ...] = (
    "selection_id", "sources", "candidate_roots", "cross_folder_moves",
    "selected_at", "selected_by",
)

SELECTION_DDL = """
CREATE TABLE IF NOT EXISTS corpus_selections (
    selection_id       TEXT PRIMARY KEY,
    sources            TEXT NOT NULL,     -- JSON array of paths (§1.1)
    candidate_roots    TEXT NOT NULL,     -- JSON array of paths (§1.1) -- context only
    cross_folder_moves INTEGER NOT NULL,  -- the user's selection (§1.1); enforced
                                          -- nowhere in P3 -- SPEC Q12 is OPEN
    selected_at        TEXT NOT NULL,
    selected_by        TEXT               -- nullable: §8.2 records identity only on
                                          -- an explicit user action (MINOR 10)
);
"""


def record_selection(conn: sqlite3.Connection, *,
                     sources: Iterable[Path],
                     candidate_roots: Iterable[Path],
                     cross_folder_moves: bool,
                     selected_by: str | None) -> str:
    """Record one corpus selection (R1). Returns its `selection_id`.

    All four keywords are required. §1.1 assigns the choice to the user, so P3 has
    no source set and no root set until one is supplied and must not derive either
    from the machine's layout. `selected_by` may be None — an R1 not authored by a
    user leaves the field empty, which is a correct value, not a missing one.
    """
    selection_id = str(uuid.uuid4())
    conn.execute(
        f"INSERT INTO corpus_selections ({','.join(SELECTION_COLUMNS)}) "
        f"VALUES ({','.join('?' * len(SELECTION_COLUMNS))})",
        (
            selection_id,
            json.dumps([str(Path(p)) for p in sources]),
            json.dumps([str(Path(p)) for p in candidate_roots]),
            int(bool(cross_folder_moves)),
            datetime.now(timezone.utc).isoformat(),
            selected_by,
        ),
    )
    return selection_id


def get_selection(conn: sqlite3.Connection, selection_id: str) -> sqlite3.Row:
    return conn.execute(
        "SELECT * FROM corpus_selections WHERE selection_id = ?", (selection_id,)
    ).fetchone()


def selection_sources(conn: sqlite3.Connection, selection_id: str) -> list[Path]:
    """The folders the user chose to analyze (§1.1). Empty is a real answer."""
    return [Path(p) for p in json.loads(get_selection(conn, selection_id)["sources"])]


def selection_candidate_roots(conn: sqlite3.Connection, selection_id: str) -> list[Path]:
    """The high-level locations that may serve as roots for a future file tree.

    Context for the proposal canvas (§1.1). This list is not an authorization and
    is consumable by P11 or P12 as nothing.
    """
    return [Path(p) for p in
            json.loads(get_selection(conn, selection_id)["candidate_roots"])]
```

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_selection.py -v`
Expected: PASS — 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/selection.py src/scan_agent/schema.py tests/p3/test_p3_selection.py
git commit -m "feat(P3): R1 corpus selection record, three choices, roots carry no permission"
```

---

### Task 3: The scan-run handle — local, and OQ16 stays open

**Files:**
- Create: `src/scan_agent/run.py`
- Modify: `src/scan_agent/schema.py` — add `RUN_DDL`
- Test: `tests/p3/test_p3_run.py`

**Interfaces:**
- Consumes: `create_scan_schema`, `record_selection`.
- Produces: `RUN_DDL: str`, `start_scan_run(conn, selection_id) -> str`, `finish_scan_run(conn, scan_run_id) -> None`, `get_scan_run(conn, scan_run_id) -> sqlite3.Row`.

**SPEC OQ16 is OPEN and this task does not close it.** OQ16 asks for *"Scan identity, and the boundary that brackets it"* and records that R5 *"carries five counters and no identity at all"*, that P1 mints a `scan_id` for `scan_resource_usage` which it *"deliberately keeps off `events`"*, and that P3 *"does not settle another part's open question inside its own contract"*.

So this task does the minimum that lets P3's own five tables have a key, and publishes nothing:

- `scan_run_id` is minted locally by P3 and used only as a foreign key inside `scan_agent`'s tables.
- It is **never** written to `events`. §8.2's event record keeps its eleven fields (MINOR 1).
- It is **not** joined to P1's `scan_id` and no function here returns one from the other. Whether they are the same identity is OQ16 and P1 OQ19, and both stay open.
- The name is not coined here: `11-ops-runtime.md` §3 already writes `scan_run_id — P3's scan` in the session record. **Conflict, recorded not resolved:** §3 treats that identifier as something P3 publishes, which is more than SPEC OQ16 concedes. This plan implements the narrower reading (local handle, published as nothing) and reports the discrepancy.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_run.py
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.events import EVENT_FIELDS

from scan_agent.run import finish_scan_run, get_scan_run, start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


@pytest.fixture()
def selection(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    return record_selection(conn, sources=[tmp_path], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)


def test_a_run_brackets_a_start_and_an_end(conn, selection):
    scan_run_id = start_scan_run(conn, selection)
    assert get_scan_run(conn, scan_run_id)["started_at"]
    assert get_scan_run(conn, scan_run_id)["completed_at"] is None
    finish_scan_run(conn, scan_run_id)
    assert get_scan_run(conn, scan_run_id)["completed_at"]


def test_the_run_handle_is_never_written_to_events(conn, selection):
    # SPEC OQ16 / P1 §10: the scan identifier stays off `events`; §8.2's event
    # record keeps its eleven fields (MINOR 1).
    start_scan_run(conn, selection)
    assert "scan_run_id" not in EVENT_FIELDS
    assert "scan_id" not in EVENT_FIELDS
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(events)")]
    assert "scan_run_id" not in columns


def test_p3_publishes_no_scan_identity_and_joins_none(conn, selection):
    # OQ16 is open. P3 does not claim this handle as §8.6's scan identity and does
    # not resolve it against P1's `scan_id` (P1 OQ19). No function here does either.
    import scan_agent.run as module
    assert not [n for n in vars(module)
                if "scan_id" in n and n != "start_scan_run"]
    assert "scan_resource_usage" not in module.__dict__
    source = Path(module.__file__).read_text()
    assert "database_agent.scan_usage" not in source


def test_a_run_names_the_selection_it_scanned(conn, selection):
    scan_run_id = start_scan_run(conn, selection)
    assert get_scan_run(conn, scan_run_id)["selection_id"] == selection


def test_a_run_cannot_reference_a_selection_that_does_not_exist(conn, selection):
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        start_scan_run(conn, "no-such-selection")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_run.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.run'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/run.py
"""P3's local scan-run handle.

SPEC OQ16 is OPEN and this module does not close it. §8.6 says "every scan"; P1
records six resource counters per scan under a `scan_id` it mints locally and
deliberately keeps off `events` (P1 Contract out §10, P1 OQ19); P3's SPEC records
that R5 "carries five counters and no identity at all" and that "P3 does not settle
another part's open question inside its own contract".

What this module therefore is: a foreign key for P3's own tables, minted by P3 and
published as nothing. It is not written to `events`, it is not resolved against
P1's `scan_id`, and no function here claims it as §8.6's scan identity. When OQ16
closes, the published identity lands here and this row is what carries it.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

RUN_DDL = """
CREATE TABLE IF NOT EXISTS scan_runs (
    scan_run_id  TEXT PRIMARY KEY,
    selection_id TEXT NOT NULL REFERENCES corpus_selections(selection_id),
    started_at   TEXT NOT NULL,
    completed_at TEXT
);
"""


def start_scan_run(conn: sqlite3.Connection, selection_id: str) -> str:
    """Open a scan run against one R1 selection. Returns P3's local run handle."""
    scan_run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO scan_runs (scan_run_id, selection_id, started_at) VALUES (?, ?, ?)",
        (scan_run_id, selection_id, datetime.now(timezone.utc).isoformat()),
    )
    return scan_run_id


def finish_scan_run(conn: sqlite3.Connection, scan_run_id: str) -> None:
    """Close the run. `completed_at` brackets the run for P3's own reads only —
    §8.6's `elapsed_time` is measured by P1's `scan_resource_usage`, not here."""
    conn.execute(
        "UPDATE scan_runs SET completed_at = ? WHERE scan_run_id = ?",
        (datetime.now(timezone.utc).isoformat(), scan_run_id),
    )


def get_scan_run(conn: sqlite3.Connection, scan_run_id: str) -> sqlite3.Row:
    return conn.execute(
        "SELECT * FROM scan_runs WHERE scan_run_id = ?", (scan_run_id,)
    ).fetchone()
```

Change `create_scan_schema` in `src/scan_agent/schema.py`:

```python
from scan_agent.run import RUN_DDL
from scan_agent.selection import SELECTION_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_run.py -v`
Expected: PASS — 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/run.py src/scan_agent/schema.py tests/p3/test_p3_run.py
git commit -m "feat(P3): local scan-run handle, published as nothing, OQ16 left open"
```

---

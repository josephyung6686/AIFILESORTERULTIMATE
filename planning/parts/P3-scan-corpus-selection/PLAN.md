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
src/scan_agent/deferrals.py         paths P3 did not index and no §1.1 rule rejected
src/scan_agent/traversal.py         the pure generator: exclusion, inventory, deferral
src/scan_agent/basic_record.py      Contract out R2 — the ten §1.2 fields, through P1
src/scan_agent/stat_cache.py        Contract out R4 — reuse | recompute
src/scan_agent/inventory.py         Contract out R6 — directory inventory, curation signal
src/scan_agent/summary.py           Contract out R5 — the five §8.6 counters
src/scan_agent/scan.py              the writer: composes the above into one scan run
src/scan_agent/replay.py            §8.5 — serialize a scan, re-assert it without a disk
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
import pytest

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
    with pytest.raises(ValueError):
        event_defaults(event_type="extraction", file_id="f1")


def test_event_defaults_cannot_be_told_to_name_another_subsystem():
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


def test_the_selection_record_carries_r1s_fields_and_no_others(schema):
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
This module grants nothing, targets nothing, and approves nothing.
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
    assert not [n for n in vars(module) if "scan_id" in n]
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

### Task 4: R3 — exclusion verdicts and §1.1's eleven literal directory names (Done-means 3, 6)

**Files:**
- Create: `src/scan_agent/exclusion.py`
- Modify: `src/scan_agent/schema.py` — add `EXCLUSION_DDL`
- Test: `tests/p3/test_p3_exclusion.py`

**Interfaces:**
- Consumes: `create_scan_schema`.
- Produces: `EXCLUDED_DIRECTORY_NAMES: tuple[str, ...]` (eleven), `EXCLUSION_CATEGORIES: tuple[str, ...]` (five), `CATEGORY_MEMBERS: Mapping[str, tuple[str, ...]]`, `RULE_LITERAL_DIRECTORY_NAME`, `RULE_CATEGORY`, `RULE_PROJECT_ROOT_DESCENDANT`, `APPLIES_TO_SCANNED_SOURCE`, `APPLIES_TO_CANDIDATE_ROOT`, `ExclusionVerdict` (frozen dataclass), `exclusion_for(path, *, is_dir, applies_to, project_root_markers=()) -> ExclusionVerdict | None`, `EXCLUSION_DDL: str`, `record_exclusion(conn, scan_run_id, verdict) -> int`, `exclusion_verdicts(conn, scan_run_id) -> list[sqlite3.Row]`.

**The eleven names are complete and implementable now.** §1.1 lists them literally: *"The engine should ignore `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`, `Pods`, `site-packages`, `Library`, `__pycache__`…"* They are copied verbatim, in the design's order, and nothing is added to the tuple.

**The five categories are named and empty.** §1.1 continues *"…build artifacts, caches, auto-save folders, previews, and generated dependency trees"* and enumerates no member of any of them. SPEC Deferred: *"the category members are a hand-authored list and are not guessed here."* So the category rule is **wired and empty**: `CATEGORY_MEMBERS` maps each of the five names to an empty tuple, the matching loop runs and never fires, and the day the list is hand-authored the rule starts working with no code change. Guessing a member here — `.cache`, `Thumbs.db`, `~$doc` — would be P3 authoring a gazetteer the design does not supply.

**They apply to directories.** §1.1: *"the system excludes **directories** that should not participate in organization"*, and R3's `rule_subject` is *"the literal directory name"*. A file that happens to be named `build` is not a directory and is not excluded by this rule.

**An excluded path yields no `files` row and no descendants** (SPEC R3). The pruning is Task 9's; this task is the rule and the record.

**A verdict is never deleted.** SPEC, *What P3 never overwrites*: *"Exclusion verdicts likewise survive a later rule-set change — an R3 record explaining why a path was skipped is not deleted when the path later becomes eligible."* Enforced by trigger, the same way P1 enforces `events`.

**R3 is not an event, and that is an open question, not a decision.** SPEC Q13: *"Do exclusion verdicts get events? §8.2's event record is keyed on file ID; an excluded directory has no file record and no hash."* This plan therefore writes R3 to its own table and appends **no** event for an exclusion; Task 17 pins that as the current state and names Q13 as the reason.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_exclusion.py
import sqlite3
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, CATEGORY_MEMBERS,
    EXCLUDED_DIRECTORY_NAMES, EXCLUSION_CATEGORIES, RULE_CATEGORY,
    RULE_LITERAL_DIRECTORY_NAME, exclusion_for, exclusion_verdicts, record_exclusion,
)
from scan_agent.run import start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


@pytest.fixture()
def run(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    selection = record_selection(conn, sources=[tmp_path], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return start_scan_run(conn, selection)


def test_the_eleven_names_are_1_1s_eleven_verbatim_and_in_order():
    assert EXCLUDED_DIRECTORY_NAMES == (
        "node_modules", ".git", "venv", "build", "dist", "target", "vendor",
        "Pods", "site-packages", "Library", "__pycache__",
    )
    assert len(EXCLUDED_DIRECTORY_NAMES) == 11


def test_each_of_the_eleven_is_excluded_as_a_directory(tmp_path: Path):
    for name in EXCLUDED_DIRECTORY_NAMES:
        verdict = exclusion_for(tmp_path / name, is_dir=True,
                                applies_to=APPLIES_TO_SCANNED_SOURCE)
        assert verdict is not None, name
        assert verdict.rule == RULE_LITERAL_DIRECTORY_NAME
        assert verdict.rule_subject == name
        assert verdict.applies_to == APPLIES_TO_SCANNED_SOURCE


def test_the_rule_is_about_directories(tmp_path: Path):
    # §1.1: "the system excludes directories that should not participate".
    # A FILE named `build` is not a directory and this rule does not reach it.
    assert exclusion_for(tmp_path / "build", is_dir=False,
                         applies_to=APPLIES_TO_SCANNED_SOURCE) is None


def test_an_ordinary_directory_is_not_excluded(tmp_path: Path):
    assert exclusion_for(tmp_path / "Coursework", is_dir=True,
                         applies_to=APPLIES_TO_SCANNED_SOURCE) is None


def test_the_five_categories_are_named_and_have_no_members():
    # SPEC Deferred: §1.1 names the categories and enumerates no member of any of
    # them. The rule is wired and empty; guessing a member would be P3 authoring a
    # gazetteer the design does not supply.
    assert EXCLUSION_CATEGORIES == (
        "build artifacts", "caches", "auto-save folders", "previews",
        "generated dependency trees",
    )
    assert set(CATEGORY_MEMBERS) == set(EXCLUSION_CATEGORIES)
    assert all(members == () for members in CATEGORY_MEMBERS.values())


def test_the_category_rule_fires_the_day_a_member_is_authored(tmp_path: Path, monkeypatch):
    # The rule is wired: authoring the deferred list is a data change, not a code
    # change. This test proves the wiring without authoring anything.
    from types import MappingProxyType

    import scan_agent.exclusion as module
    authored = dict.fromkeys(EXCLUSION_CATEGORIES, ())
    authored["caches"] = ("SomeHandAuthoredCacheDirectory",)
    monkeypatch.setattr(module, "CATEGORY_MEMBERS", MappingProxyType(authored))

    verdict = module.exclusion_for(tmp_path / "SomeHandAuthoredCacheDirectory",
                                   is_dir=True, applies_to=APPLIES_TO_SCANNED_SOURCE)
    assert verdict is not None
    assert verdict.rule == RULE_CATEGORY
    assert verdict.rule_subject == "caches"


def test_a_verdict_names_the_rule_that_rejected_the_path(conn, run, tmp_path: Path):
    # Done-means 6, and §8.2's "structured explanation or evidence reference".
    verdict = exclusion_for(tmp_path / "node_modules", is_dir=True,
                            applies_to=APPLIES_TO_SCANNED_SOURCE)
    record_exclusion(conn, run, verdict)
    row = exclusion_verdicts(conn, run)[0]
    assert row["path"] == str(tmp_path / "node_modules")
    assert row["rule"] == RULE_LITERAL_DIRECTORY_NAME
    assert row["rule_subject"] == "node_modules"
    assert row["applies_to"] == APPLIES_TO_SCANNED_SOURCE
    assert row["observed_at"]


def test_applies_to_has_exactly_the_specs_two_values():
    assert APPLIES_TO_SCANNED_SOURCE == "scanned source"
    assert APPLIES_TO_CANDIDATE_ROOT == "candidate root"


def test_a_verdict_is_never_deleted(conn, run, tmp_path: Path):
    # SPEC, "What P3 never overwrites": a verdict explaining why a path was skipped
    # is not deleted when the path later becomes eligible.
    record_exclusion(conn, run, exclusion_for(tmp_path / ".git", is_dir=True,
                                              applies_to=APPLIES_TO_SCANNED_SOURCE))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM exclusion_verdicts")


def test_an_exclusion_appends_no_event(conn, run, tmp_path: Path):
    # SPEC Q13 is OPEN: §8.2's event record is keyed on file ID and an excluded
    # directory has no file record. This plan does not answer it, so R3 lives in
    # its own table and no event is appended. When Q13 closes, this test changes.
    record_exclusion(conn, run, exclusion_for(tmp_path / "dist", is_dir=True,
                                              applies_to=APPLIES_TO_SCANNED_SOURCE))
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_exclusion.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.exclusion'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/exclusion.py
"""Contract out R3 — §1.1's exclusion rules and the verdict they produce.

§1.1: "Before scanning, the system excludes directories that should not participate
in organization… The exclusion must apply both to scanned sources and to candidate
roots. The engine should ignore `node_modules`, `.git`, `venv`, `build`, `dist`,
`target`, `vendor`, `Pods`, `site-packages`, `Library`, `__pycache__`, build
artifacts, caches, auto-save folders, previews, and generated dependency trees. It
should also reject descendants of software project roots indicated by files such as
`package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`."

An excluded path yields no `files` row and no descendants.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePath
from types import MappingProxyType

#: §1.1's eleven literal directory names, verbatim and in the design's order.
EXCLUDED_DIRECTORY_NAMES: tuple[str, ...] = (
    "node_modules", ".git", "venv", "build", "dist", "target", "vendor",
    "Pods", "site-packages", "Library", "__pycache__",
)

#: §1.1's five open-ended categories. The design NAMES them and enumerates no member
#: of any of them, so each maps to an empty membership (SPEC Deferred: "the category
#: members are a hand-authored list and are not guessed here"). The rule below is
#: wired against this mapping, so authoring the list is a data change, not a code one.
EXCLUSION_CATEGORIES: tuple[str, ...] = (
    "build artifacts", "caches", "auto-save folders", "previews",
    "generated dependency trees",
)
CATEGORY_MEMBERS = MappingProxyType({name: () for name in EXCLUSION_CATEGORIES})

#: R3's `rule` — which §1.1 rule fired. §1.1 states three rule kinds and no fourth.
RULE_LITERAL_DIRECTORY_NAME = "literal directory name"
RULE_CATEGORY = "category"
RULE_PROJECT_ROOT_DESCENDANT = "software project root descendant"

#: R3's `applies_to` — the SPEC's two words, and no third.
APPLIES_TO_SCANNED_SOURCE = "scanned source"
APPLIES_TO_CANDIDATE_ROOT = "candidate root"


@dataclass(frozen=True)
class ExclusionVerdict:
    """R3. One per rejected path, emitted for both sides of the scan."""
    path: str
    rule: str
    rule_subject: str
    applies_to: str


def exclusion_for(path, *, is_dir: bool, applies_to: str,
                  project_root_markers: tuple[str, ...] = ()) -> ExclusionVerdict | None:
    """The §1.1 verdict for one entry, or None when no rule fires.

    `project_root_markers` are the markers observed in the entry's PARENT directory:
    a non-empty tuple means this entry is a descendant of a software project root,
    which §1.1 rejects whether it is a file or a directory.
    """
    name = PurePath(path).name
    if project_root_markers:
        return ExclusionVerdict(str(path), RULE_PROJECT_ROOT_DESCENDANT,
                                project_root_markers[0], applies_to)
    if is_dir and name in EXCLUDED_DIRECTORY_NAMES:
        return ExclusionVerdict(str(path), RULE_LITERAL_DIRECTORY_NAME, name, applies_to)
    if is_dir:
        for category, members in CATEGORY_MEMBERS.items():
            if name in members:
                return ExclusionVerdict(str(path), RULE_CATEGORY, category, applies_to)
    return None


EXCLUSION_DDL = """
CREATE TABLE IF NOT EXISTS exclusion_verdicts (
    verdict_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    rule         TEXT NOT NULL,
    rule_subject TEXT NOT NULL,
    applies_to   TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS exclusion_verdicts_no_delete
BEFORE DELETE ON exclusion_verdicts
BEGIN
    SELECT RAISE(ABORT, 'an exclusion verdict survives a later rule-set change');
END;
"""


def record_exclusion(conn: sqlite3.Connection, scan_run_id: str,
                     verdict: ExclusionVerdict) -> int:
    conn.execute(
        "INSERT INTO exclusion_verdicts "
        "(scan_run_id, path, rule, rule_subject, applies_to, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (scan_run_id, verdict.path, verdict.rule, verdict.rule_subject,
         verdict.applies_to, datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def exclusion_verdicts(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE scan_run_id = ? ORDER BY verdict_id",
        (scan_run_id,),
    ).fetchall()
```

`src/scan_agent/schema.py` in full at this point:

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_exclusion.py -v`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/exclusion.py src/scan_agent/schema.py tests/p3/test_p3_exclusion.py
git commit -m "feat(P3): R3 exclusion verdicts, 1.1's eleven names, five categories wired and empty"
```

---

### Task 5: The software-project-root rule (Done-means 4)

**Files:**
- Modify: `src/scan_agent/exclusion.py` — add `PROJECT_ROOT_MARKERS` and `project_root_markers_in`
- Test: `tests/p3/test_p3_exclusion.py` — extend

**Interfaces:**
- Consumes: `exclusion_for` (Task 4).
- Produces: `PROJECT_ROOT_MARKERS: tuple[str, str, str, str]`, `project_root_markers_in(entry_names: Iterable[tuple[str, bool]]) -> tuple[str, ...]`.

**The four markers are literal and complete for now.** §1.1: *"descendants of software project roots indicated by files such as `package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`."* SPEC Deferred: *"§1.1's 'files such as' signals an extensible set without naming its other members. The four literal names are implementable now; any extension is hand-authored."* So four, and no fifth.

**The rule rejects descendants.** §1.1's word is *descendants*, and Done-means 4 is *"A directory containing `package.json` … yields zero `files` rows from its **descendants**."* A file sitting directly inside the marker-bearing directory **is** a descendant of it, so it is rejected; the marker-bearing directory **itself** is not rejected by this rule. Its rejection would be a different rule, and whether it should be rejected is **SPEC Q9** — *"Does the project-root rule exclude the root directory itself, or only its descendants? … Whether the marker-bearing directory can still be a candidate root, or appear in the canvas at all, is unstated."* **Q9 stays open.** This plan implements §1.1's literal word and asserts nothing about the marker-bearing directory's eligibility as a candidate root; the directory keeps its R6 inventory row (Task 13) and the marker is recorded there as evidence, which is what §1.1's AIKonic case asks the scan to know.

**The marker file is itself a descendant** and therefore excluded, with `rule_subject` naming it. It is still observable as R6 evidence because the traversal reads the directory listing before applying any rule.

**Only the first marker in the design's order lands in `rule_subject`**, so the verdict is deterministic across runs and replays. All markers observed in a directory are recorded in R6's `curation_evidence` (Task 13), so nothing is lost.

- [ ] **Step 1: Write the failing test**

Append to `tests/p3/test_p3_exclusion.py`:

```python
from scan_agent.exclusion import (
    PROJECT_ROOT_MARKERS, RULE_PROJECT_ROOT_DESCENDANT, project_root_markers_in,
)


def test_the_four_markers_are_1_1s_four_verbatim():
    assert PROJECT_ROOT_MARKERS == (
        "package.json", "requirements.txt", "Cargo.toml", "go.mod",
    )


def test_each_marker_makes_its_directory_a_project_root():
    for marker in PROJECT_ROOT_MARKERS:
        listing = [("README.md", False), (marker, False), ("src", True)]
        assert project_root_markers_in(listing) == (marker,)


def test_a_marker_must_be_a_file_not_a_directory():
    # §1.1: "indicated by FILES such as package.json".
    assert project_root_markers_in([("package.json", True)]) == ()


def test_markers_are_reported_in_the_designs_order():
    listing = [("go.mod", False), ("package.json", False)]
    assert project_root_markers_in(listing) == ("package.json", "go.mod")


def test_a_descendant_of_a_project_root_is_rejected(tmp_path: Path):
    # Done-means 4. Both a file and a subdirectory inside the marker-bearing
    # directory are descendants of it.
    markers = ("package.json",)
    for child, is_dir in (("notes.txt", False), ("src", True)):
        verdict = exclusion_for(tmp_path / "app" / child, is_dir=is_dir,
                                applies_to=APPLIES_TO_SCANNED_SOURCE,
                                project_root_markers=markers)
        assert verdict is not None
        assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT
        assert verdict.rule_subject == "package.json"


def test_the_marker_file_is_itself_a_descendant_and_is_rejected(tmp_path: Path):
    verdict = exclusion_for(tmp_path / "app" / "package.json", is_dir=False,
                            applies_to=APPLIES_TO_SCANNED_SOURCE,
                            project_root_markers=("package.json",))
    assert verdict is not None
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT


def test_the_marker_bearing_directory_itself_is_not_rejected_by_this_rule(tmp_path: Path):
    # SPEC Q9 is OPEN: §1.1 says "descendants of software project roots" and says
    # nothing about the root directory itself. This plan implements §1.1's literal
    # word and decides nothing about whether that directory may be a candidate root.
    assert exclusion_for(tmp_path / "app", is_dir=True,
                         applies_to=APPLIES_TO_SCANNED_SOURCE,
                         project_root_markers=()) is None


def test_the_project_root_rule_outranks_the_literal_name_rule(tmp_path: Path):
    # A `build` directory inside a project root is rejected as a descendant. Both
    # rules would fire; the verdict names one, deterministically.
    verdict = exclusion_for(tmp_path / "app" / "build", is_dir=True,
                            applies_to=APPLIES_TO_SCANNED_SOURCE,
                            project_root_markers=("Cargo.toml",))
    assert verdict.rule == RULE_PROJECT_ROOT_DESCENDANT
    assert verdict.rule_subject == "Cargo.toml"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_exclusion.py -v`
Expected: FAIL with `ImportError: cannot import name 'PROJECT_ROOT_MARKERS'`

- [ ] **Step 3: Write the implementation**

Insert into `src/scan_agent/exclusion.py`, below `EXCLUSION_CATEGORIES`:

```python
#: §1.1's four literal software-project-root markers, verbatim and in order.
#: §1.1's "files such as" signals an extensible set and names no other member, so
#: any extension is hand-authored (SPEC Deferred). Four, and no fifth.
PROJECT_ROOT_MARKERS: tuple[str, str, str, str] = (
    "package.json", "requirements.txt", "Cargo.toml", "go.mod",
)
```

And below `exclusion_for`:

```python
def project_root_markers_in(entry_names) -> tuple[str, ...]:
    """The §1.1 markers observed directly inside one directory, in the design's order.

    A non-empty result makes that directory a software project root, so §1.1 rejects
    its descendants. Whether the marker-bearing directory ITSELF is excluded — and
    whether it may still be a candidate root — is SPEC Q9 and is OPEN: §1.1 says
    only "descendants of software project roots". Nothing here decides it.

    `entry_names` is an iterable of (name, is_dir) pairs: §1.1 says the markers are
    FILES, so a directory called `package.json` is not one.
    """
    files = {name for name, is_dir in entry_names if not is_dir}
    return tuple(marker for marker in PROJECT_ROOT_MARKERS if marker in files)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_exclusion.py -v`
Expected: PASS — 18 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/exclusion.py tests/p3/test_p3_exclusion.py
git commit -m "feat(P3): software-project-root rule, four markers, descendants rejected"
```

---

### Task 6: Dataless iCloud detection, before hashing (`11-ops-runtime.md` §5)

**Files:**
- Create: `src/scan_agent/dataless.py`
- Modify: `src/scan_agent/schema.py` — add `DATALESS_DDL`
- Test: `tests/p3/test_p3_dataless.py`

**Interfaces:**
- Consumes: `create_scan_schema`.
- Produces: `SF_DATALESS: int`, `is_dataless(stat_result) -> bool`, `DATALESS_DDL: str`, `record_dataless_detection(conn, scan_run_id, path) -> int`, `dataless_detections(conn, scan_run_id) -> list[sqlite3.Row]`.

**Binding [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §5.** *"macOS 'Optimize Mac Storage' presents Finder entries that are not on disk. Hashing or opening them **downloads** the file. P3 detects a dataless / not-downloaded ubiquitous item **before** hashing. Detection is a filesystem observation, not a handling class. Do not materialize, hash, or extract."*

Three consequences, and this task is the whole of P3's half of the seam:

- **Detection is from `stat`, never from opening.** macOS `sys/stat.h` sets `SF_DATALESS` (`0x40000000`) in `st_flags` for a ubiquitous item whose bytes are not on this machine. `os.stat` does not download; `open` does. Python's `stat` module does not publish the constant, so it is written here as the one platform value P3 needs, with its source named.
- **P3 records the detection and writes no run row.** §5: *"Until it closes, P3 records the detection and writes no run row (P5 writes runs, not P3)."* Which `completeness` value such a file eventually carries is **P4 Open question 6** and none of P4's eight values means *"the bytes are not on this machine"*. This plan resolves nothing about it: the strings `extraction_runs` and `completeness` appear nowhere in `scan_agent`, and Task 17 asserts it.
- **A dataless file gets no `files` row this scan.** P1's identity is the content hash and the hash cannot be taken without downloading. §5: *"Materialization is a user action, shown by P13. After the file is local, P3 re-stats and hashing proceeds as normal."* So the detection record is what P13 renders, and the next scan picks the file up normally once it is local.

**Not detected here: the legacy `.icloud` placeholder form**, in which a not-downloaded `Foo.pdf` appears on disk as a separate hidden file named `.Foo.pdf.icloud`. That is a different on-disk shape, `11` §5 does not name it, and inventing a filename heuristic for it would be P3 authoring a detection rule the contract does not supply. Recorded as a known gap.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_dataless.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.dataless import (
    SF_DATALESS, dataless_detections, is_dataless, record_dataless_detection,
)
from scan_agent.run import start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


class FakeStat:
    """Stands in for os.stat_result. SF_DATALESS is not user-settable (it is outside
    macOS's SF_SETTABLE mask), so a real dataless file cannot be built in a fixture."""
    def __init__(self, st_flags: int):
        self.st_flags = st_flags


@pytest.fixture()
def run(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    selection = record_selection(conn, sources=[tmp_path], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return start_scan_run(conn, selection)


def test_the_constant_is_macos_sf_dataless():
    # macOS sys/stat.h. Python's `stat` module does not publish it.
    assert SF_DATALESS == 0x40000000


def test_a_file_carrying_sf_dataless_is_detected():
    assert is_dataless(FakeStat(SF_DATALESS)) is True
    assert is_dataless(FakeStat(SF_DATALESS | 0x00010000)) is True


def test_an_ordinary_file_is_not_dataless(tmp_path: Path):
    p = tmp_path / "local.bin"
    p.write_bytes(b"bytes that are really here")
    assert is_dataless(os.stat(p)) is False


def test_a_platform_without_st_flags_reads_as_not_dataless():
    class NoFlags:
        pass
    assert is_dataless(NoFlags()) is False


def test_detection_never_opens_the_file():
    # 11 §5: "Hashing or opening them downloads the file." Detection is a stat
    # observation, so this module reads no bytes at all.
    import scan_agent.dataless as module
    source = Path(module.__file__).read_text()
    assert "open(" not in source
    assert "read_bytes" not in source
    assert "hash_file" not in source


def test_a_detection_is_recorded_and_is_readable(conn, run, tmp_path: Path):
    # 11 §5: "§8.6's progress line must be able to name these files rather than
    # folding them into OCR-capped or unreadable."
    record_dataless_detection(conn, run, tmp_path / "Thesis.pdf")
    rows = dataless_detections(conn, run)
    assert [r["path"] for r in rows] == [str(tmp_path / "Thesis.pdf")]
    assert rows[0]["observed_at"]


def test_a_detection_writes_no_extraction_run_and_no_completeness(conn, run, tmp_path: Path):
    # 11 §5 / SPEC: that record is P4's and P5 is its writer. Which `completeness`
    # value a dataless file eventually carries is P4 Open question 6 and is NOT
    # resolved here — none of P4's eight values means "the bytes are not on this
    # machine", and P3 does not choose one or add a ninth.
    record_dataless_detection(conn, run, tmp_path / "Thesis.pdf")
    tables = [r["name"] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert "extraction_runs" not in tables
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(dataless_detections)")]
    assert "completeness" not in columns

    import scan_agent.dataless as module
    assert "completeness" not in Path(module.__file__).read_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_dataless.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.dataless'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/dataless.py
"""11-ops-runtime.md §5 — detect a dataless iCloud item BEFORE hashing.

"macOS 'Optimize Mac Storage' presents Finder entries that are not on disk. Hashing
or opening them downloads the file. P3 detects a dataless / not-downloaded ubiquitous
item before hashing. Detection is a filesystem observation, not a handling class. Do
not materialize, hash, or extract."

This module reads `stat` and nothing else: `os.stat` does not download, `open` does.
P3 records the detection and writes NO extraction run — that record is P4's and P5 is
its writer, and which of P4's eight closed status values such a file eventually
carries is P4 Open question 6, which nothing here resolves. P3 names none of them.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

#: macOS `sys/stat.h`. Marks a ubiquitous item whose bytes are not on this machine.
#: Python's `stat` module does not publish the constant, so it is named here with
#: its source. It is outside macOS's SF_SETTABLE mask, so it cannot be set by a test.
SF_DATALESS = 0x40000000


def is_dataless(stat_result) -> bool:
    """True when the stat result says the bytes are not on this machine.

    `st_flags` exists on BSD-family systems including macOS (v1 is macOS-only per
    11-ops-runtime.md). A platform without it reads as not dataless, which is the
    honest answer: P3 has observed nothing that says otherwise.
    """
    return bool(getattr(stat_result, "st_flags", 0) & SF_DATALESS)


DATALESS_DDL = """
CREATE TABLE IF NOT EXISTS dataless_detections (
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
"""


def record_dataless_detection(conn: sqlite3.Connection, scan_run_id: str, path) -> int:
    """Record that a path was observed dataless and skipped before hashing.

    This is the record §8.6's progress line reads so that these files can be NAMED
    rather than folded into OCR-capped or unreadable (11 §5). It is not an extraction
    run and carries no status from P4's closed vocabulary.
    """
    conn.execute(
        "INSERT INTO dataless_detections (scan_run_id, path, observed_at) "
        "VALUES (?, ?, ?)",
        (scan_run_id, str(Path(path)), datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def dataless_detections(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM dataless_detections WHERE scan_run_id = ? ORDER BY detection_id",
        (scan_run_id,),
    ).fetchall()
```

`src/scan_agent/schema.py` in full at this point:

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL
from scan_agent.dataless import DATALESS_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(DATALESS_DDL)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_dataless.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/dataless.py src/scan_agent/schema.py tests/p3/test_p3_dataless.py
git commit -m "feat(P3): dataless iCloud detection from stat, before hashing, no run row"
```

---

### Task 7: The corpus source — a live filesystem and a frozen snapshot (§8.5)

**Files:**
- Create: `src/scan_agent/corpus_source.py`
- Test: `tests/p3/test_p3_corpus_source.py`

**Interfaces:**
- Consumes: `database_agent.identity.hash_file`, `scan_agent.dataless.is_dataless`.
- Produces: `Entry` (frozen dataclass: `path`, `name`, `kind`, `size`, `mtime`, `dataless`), `KIND_DIRECTORY`, `KIND_FILE`, `KIND_OTHER`, `CorpusSource` (Protocol: `has_bytes: bool`, `entries(directory) -> list[Entry]`), `FilesystemCorpusSource`, `SnapshotCorpusSource`.

**The source lists; it does not hash.** P1's `observe_path` hashes internally from the path it is handed (`hash_file(path, materialized=...)`), so a `content_hash` method on this interface would have no caller and would be a second route to a value P1 owns. The source therefore reports what a listing can see — kind, size, mtime, dataless — and nothing more.

**Why an interface at all.** SPEC Contract in, from P2: §8.5 requires evaluation *"without touching a live filesystem"*, and the bundle carries *"a frozen corpus snapshot or a metadata-safe representation of one"*. So **P3 must be runnable against a bundle-backed corpus source as well as a live filesystem, with identical exclusion and cache verdicts.** One interface with two implementations is the smallest thing that makes Done-means 14 provable.

**P2's envelope is not defined here and not imported here.** P2 owns `bundle_manifest`, `bundle_file_entry` and `corpus_form`. This module imports no P2 code — P3 is buildable against P1 alone — and Task 15 defines only the payload P3 itself serializes and re-asserts, using P2's field spellings (`corpus_form`, `content_hash`) where P2 publishes one.

**`has_bytes` is what a metadata-safe bundle costs.** §8.5's `metadata_safe` form has no file bytes, so no content hash can be computed from it and P1's content-hash identity is unavailable. `has_bytes` is False for that form, and Task 15's replay writes exclusion verdicts, cache verdicts and inventory rows — exactly the three things Done-means 14 asks to be identical — and no `files` rows. This is a consequence of §8.5's own two forms, recorded rather than papered over.

**`kind` exists because SPEC Q7 is OPEN.** *"Scan-time traversal of symlinks, aliases, macOS packages and application bundles, network mounts, removable storage, and cloud-synced directories… Traversal is unstated."* This module resolves none of it. It reports three kinds — directory, regular file, and **other** — computed with `follow_symlinks=False`, so a symlink is never silently descended (a symlink loop would otherwise make traversal non-terminating, which is mechanics, not a design decision) and is never handed to `hash_file` (hashing a symlinked directory would raise). What the traversal then *does* with an `other` entry is Task 9's, and what it does is record it as unresolved and name Q7. A `.app` bundle is an ordinary directory and **is** descended today, because §1.1 supplies no rule that would stop it; that is Q7's stated cost and is a known gap, not a fix made here.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_corpus_source.py
from pathlib import Path

import pytest

from scan_agent.corpus_source import (
    KIND_DIRECTORY, KIND_FILE, KIND_OTHER, FilesystemCorpusSource, SnapshotCorpusSource,
)


def test_a_directory_listing_reports_kind_size_and_mtime(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_bytes(b"abc")
    entries = {e.name: e for e in FilesystemCorpusSource().entries(tmp_path)}
    assert entries["sub"].kind == KIND_DIRECTORY
    assert entries["a.txt"].kind == KIND_FILE
    assert entries["a.txt"].size == 3
    assert entries["a.txt"].mtime > 0
    assert entries["a.txt"].dataless is False
    assert entries["a.txt"].path == str(tmp_path / "a.txt")


def test_a_listing_is_ordered_so_two_runs_agree(tmp_path: Path):
    for name in ("c.txt", "a.txt", "b.txt"):
        (tmp_path / name).write_bytes(b"x")
    first = [e.path for e in FilesystemCorpusSource().entries(tmp_path)]
    second = [e.path for e in FilesystemCorpusSource().entries(tmp_path)]
    assert first == second == sorted(first)


def test_a_symlink_is_neither_a_directory_nor_a_file(tmp_path: Path):
    # SPEC Q7 is OPEN. `follow_symlinks=False` means a symlink is never silently
    # descended and never handed to hash_file. What the traversal does with it is
    # Task 9's, and Task 9 records it as unresolved rather than deciding.
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real")
    entries = {e.name: e for e in FilesystemCorpusSource().entries(tmp_path)}
    assert entries["link"].kind == KIND_OTHER


def test_a_dataless_entry_is_reported_as_dataless_and_never_opened(tmp_path: Path):
    # 11 §5: the source's job is to REPORT the observation; refusing to hash is
    # P1's, through the `materialized` flag P3 derives from this field (Task 10).
    p = tmp_path / "cloud.bin"
    p.write_bytes(b"bytes")
    entry = FilesystemCorpusSource().entries(tmp_path)[0]
    assert entry.dataless is False
    import scan_agent.corpus_source as module
    assert "hash_file" not in Path(module.__file__).read_text()


def test_the_filesystem_source_has_bytes():
    assert FilesystemCorpusSource().has_bytes is True


def test_a_snapshot_source_lists_without_touching_a_filesystem(tmp_path: Path):
    # §8.5: evaluation "without touching a live filesystem".
    snapshot = {
        "corpus_form": "metadata_safe",
        "entries": [
            {"path": "/c/sub", "name": "sub", "kind": KIND_DIRECTORY, "size": 0,
             "mtime": 0.0, "dataless": False, "content_hash": None, "parent": "/c"},
            {"path": "/c/a.txt", "name": "a.txt", "kind": KIND_FILE, "size": 3,
             "mtime": 1.5, "dataless": False, "content_hash": "aaa", "parent": "/c"},
        ],
    }
    source = SnapshotCorpusSource(snapshot)
    entries = {e.name: e for e in source.entries("/c")}
    assert entries["a.txt"].size == 3
    assert entries["a.txt"].mtime == 1.5
    assert source.entries("/c/sub") == []


def test_a_metadata_safe_snapshot_has_no_bytes():
    # §8.5's metadata-safe form carries no file bytes, so P1's content-hash identity
    # cannot be recomputed from it. Recorded, not papered over.
    assert SnapshotCorpusSource({"corpus_form": "metadata_safe", "entries": []}).has_bytes is False
    assert SnapshotCorpusSource({"corpus_form": "snapshot", "entries": []}).has_bytes is True


def test_the_module_imports_nothing_from_p2():
    # P3 is buildable against P1 alone; P2 owns the bundle envelope.
    import scan_agent.corpus_source as module
    source = Path(module.__file__).read_text()
    assert "eval_agent" not in source and "bundle_manifest" not in source
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_corpus_source.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.corpus_source'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/corpus_source.py
"""§8.5 — one interface over a live filesystem and a frozen corpus snapshot.

SPEC Contract in (from P2): §8.5 requires evaluation "without touching a live
filesystem", and the bundle contains "a frozen corpus snapshot or a metadata-safe
representation of one". P3 must therefore be runnable against a bundle-backed corpus
source as well as a live filesystem, with identical exclusion and cache verdicts.

P2 owns the bundle ENVELOPE. This module imports no P2 code and defines none of it.
"""
from __future__ import annotations

import os
import stat as stat_module
from dataclasses import dataclass
from typing import Protocol

from scan_agent.dataless import is_dataless

KIND_DIRECTORY = "directory"
KIND_FILE = "file"
#: Anything that is neither: symlinks, aliases, sockets, fifos, devices. SPEC Q7 is
#: OPEN on scan-time traversal of these, and this module decides nothing — it reports
#: the kind and lets the traversal record the unresolved case.
KIND_OTHER = "other"


@dataclass(frozen=True)
class Entry:
    path: str
    name: str
    kind: str
    size: int
    mtime: float
    dataless: bool


class CorpusSource(Protocol):
    has_bytes: bool

    def entries(self, directory) -> list[Entry]: ...


def _kind(mode: int) -> str:
    if stat_module.S_ISDIR(mode):
        return KIND_DIRECTORY
    if stat_module.S_ISREG(mode):
        return KIND_FILE
    return KIND_OTHER


class FilesystemCorpusSource:
    """The live filesystem."""

    has_bytes = True

    def entries(self, directory) -> list[Entry]:
        """One directory's entries, ordered by path so two runs agree.

        `follow_symlinks=False` throughout: a symlink is reported as KIND_OTHER, so
        it is never descended (a loop would make traversal non-terminating) and never
        handed to `hash_file`. SPEC Q7 stays open; this is termination, not policy.
        """
        found: list[Entry] = []
        with os.scandir(directory) as scan:
            for item in scan:
                st = item.stat(follow_symlinks=False)
                found.append(Entry(
                    path=item.path,
                    name=item.name,
                    kind=_kind(st.st_mode),
                    size=st.st_size,
                    mtime=st.st_mtime,
                    dataless=is_dataless(st),
                ))
        return sorted(found, key=lambda entry: entry.path)


class SnapshotCorpusSource:
    """A frozen corpus snapshot (§8.5). Touches no filesystem at all.

    `has_bytes` is False for §8.5's `metadata_safe` form: there are no bytes, so no
    content hash can be recomputed and P1's content-hash identity is unavailable.
    Exclusion, cache and inventory verdicts are all still reproducible, which is what
    Done-means 14 asks to be identical.
    """

    def __init__(self, snapshot: dict):
        self.has_bytes = snapshot["corpus_form"] == "snapshot"
        self._by_parent: dict[str, list[Entry]] = {}
        for record in snapshot["entries"]:
            entry = Entry(
                path=record["path"], name=record["name"], kind=record["kind"],
                size=record["size"], mtime=record["mtime"],
                dataless=record["dataless"],
            )
            self._by_parent.setdefault(record["parent"], []).append(entry)
        for children in self._by_parent.values():
            children.sort(key=lambda entry: entry.path)

    def entries(self, directory) -> list[Entry]:
        return list(self._by_parent.get(str(directory), []))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_corpus_source.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/corpus_source.py tests/p3/test_p3_corpus_source.py
git commit -m "feat(P3): corpus source over a live filesystem and a frozen snapshot"
```

---

### Task 8: Full Disk Access before traversal (`11-ops-runtime.md` §1)

**Files:**
- Create: `src/scan_agent/access.py`
- Test: `tests/p3/test_p3_access.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `FullDiskAccessRequired`, `unreadable_roots(roots) -> tuple[Path, ...]`, `require_access(roots) -> None`.

**Binding [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §1.** *"Full Disk Access is required before P3 may scan Desktop, Downloads, Documents, or any user-selected root that TCC protects. Until it is granted, P3 does not traverse; P13 shows why. This is not a handling class and not a `NeedsConsent` model prompt."*

**The OS is the oracle, not a list of folder names.** P3 holds no gazetteer of TCC-protected paths and does not test whether a path *is* protected: it attempts to list each selected root and treats `PermissionError` as the denial. That is exactly what a TCC refusal looks like from a process without Full Disk Access, and it needs no invented list.

**The check runs once, before the first directory is listed, and covers every selected root.** *"Until it is granted, P3 does not traverse"* — so a scan with one unreadable root performs **zero** traversal, not partial traversal of the readable ones. §8.6 requires the difference between completed and deferred work to be visible so that no unscanned file reads as one that *"was understood and found unimportant"*; a corpus quietly missing a whole root is exactly that failure. **This is the plan's reading of §1's scope, not a sentence `11` states**, and it is reported as such.

**A missing root is not a permission problem** and is not this function's business: `unreadable_roots` classifies `PermissionError` only, and a path that is absent at scan time is recorded by the traversal (Task 9) under SPEC Q14, which is open.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_access.py
import os
from pathlib import Path

import pytest

from scan_agent.access import FullDiskAccessRequired, require_access, unreadable_roots

needs_unprivileged = pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="root can list a 0o000 directory, so the TCC denial cannot be simulated",
)


def test_a_readable_root_passes(tmp_path: Path):
    (tmp_path / "Downloads").mkdir()
    require_access([tmp_path / "Downloads"])
    assert unreadable_roots([tmp_path / "Downloads"]) == ()


@needs_unprivileged
def test_an_unreadable_root_is_refused(tmp_path: Path):
    # 11 §1: "Until it is granted, P3 does not traverse."
    protected = tmp_path / "Documents"
    protected.mkdir()
    protected.chmod(0o000)
    try:
        assert unreadable_roots([protected]) == (protected,)
        with pytest.raises(FullDiskAccessRequired) as raised:
            require_access([protected])
        assert str(protected) in str(raised.value)
    finally:
        protected.chmod(0o700)


@needs_unprivileged
def test_one_unreadable_root_refuses_the_whole_check(tmp_path: Path):
    # A corpus quietly missing a whole root is §8.6's "understood and found
    # unimportant" failure. The refusal names every denied root, not just the first.
    ok = tmp_path / "Downloads"
    ok.mkdir()
    protected = tmp_path / "Documents"
    protected.mkdir()
    protected.chmod(0o000)
    try:
        with pytest.raises(FullDiskAccessRequired):
            require_access([ok, protected])
    finally:
        protected.chmod(0o700)


def test_a_missing_root_is_not_a_permission_problem(tmp_path: Path):
    # A path absent at scan time is SPEC Q14's territory and is recorded by the
    # traversal, not classified as a TCC denial here.
    assert unreadable_roots([tmp_path / "never-existed"]) == ()
    require_access([tmp_path / "never-existed"])


def test_p3_holds_no_list_of_protected_folders():
    # 11 §1 names Desktop, Downloads and Documents as examples. P3 encodes no
    # gazetteer of them: the OS's PermissionError is the oracle. (The module's
    # docstring quotes §1, so this checks bindings, not prose.)
    import scan_agent.access as module
    collections = [name for name, value in vars(module).items()
                   if not name.startswith("__")
                   and isinstance(value, (list, tuple, set, frozenset, dict))]
    assert collections == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_access.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.access'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/access.py
"""11-ops-runtime.md §1 — Full Disk Access before traversing a protected folder.

"Full Disk Access is required before P3 may scan Desktop, Downloads, Documents, or
any user-selected root that TCC protects. Until it is granted, P3 does not traverse;
P13 shows why."

P3 holds NO list of protected paths and does not decide which folders TCC covers.
It attempts to list each selected root; a TCC refusal arrives as PermissionError,
and that is the whole test. A root that is simply absent is not a permission problem
and is left to the traversal (SPEC Q14 is open on disappearance).
"""
from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path


class FullDiskAccessRequired(Exception):
    """11-ops-runtime.md §1 — until access is granted, P3 does not traverse."""


def unreadable_roots(roots: Iterable[Path]) -> tuple[Path, ...]:
    """The selected roots this process cannot list."""
    denied: list[Path] = []
    for root in roots:
        try:
            with os.scandir(root) as listing:
                next(iter(listing), None)
        except PermissionError:
            denied.append(Path(root))
        except (FileNotFoundError, NotADirectoryError):
            continue
    return tuple(denied)


def require_access(roots: Iterable[Path]) -> None:
    """Run once, before the first directory is listed.

    A scan with one unreadable root performs zero traversal rather than a partial
    one: §8.6 requires the difference between completed and deferred work to be
    visible, and a corpus quietly missing a whole root is not.
    """
    denied = unreadable_roots(roots)
    if denied:
        raise FullDiskAccessRequired(
            "Full Disk Access is required before traversing "
            + ", ".join(str(root) for root in denied)
            + " (11-ops-runtime.md §1)"
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_access.py -v`
Expected: PASS — 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/access.py tests/p3/test_p3_access.py
git commit -m "feat(P3): Full Disk Access precondition, the OS is the oracle"
```

---

### Task 9: The traversal (Done-means 2, 3, 4, 5, 6)

**Files:**
- Create: `src/scan_agent/deferrals.py`
- Create: `src/scan_agent/traversal.py`
- Modify: `src/scan_agent/schema.py` — add `DEFERRALS_DDL`
- Test: `tests/p3/test_p3_traversal.py`

**Interfaces:**
- Consumes: `CorpusSource`, `KIND_DIRECTORY`/`KIND_FILE`, `exclusion_for`, `project_root_markers_in`, `APPLIES_TO_*`.
- Produces (`deferrals.py`): `DEFERRED_BUDGET`, `DEFERRED_TRAVERSAL_UNRESOLVED`, `DEFERRED_PATH_ABSENT`, `DEFERRALS_DDL: str`, `record_deferral(conn, scan_run_id, deferred) -> int`, `scan_deferrals(conn, scan_run_id) -> list[sqlite3.Row]`.
- Produces (`traversal.py`): `ObservedFile`, `ObservedDirectory`, `Deferred` (frozen dataclasses), `walk(source, *, sources, candidate_roots, budget_exhausted) -> Iterator[ObservedFile | ObservedDirectory | ExclusionVerdict | Deferred]`.

**`walk` touches no database.** It is a pure generator over a `CorpusSource`, and every decision §1.1 asks for — what is excluded, what is descended, what is counted — is made here, before any row is written. That split is what makes Done-means 16 provable in Task 13: the curation signal is derived from `ObservedDirectory`, which the exclusion and cache decisions are already finished with.

**Exclusion prunes.** SPEC R3: *"An excluded path yields no `files` row and no descendants."* An excluded directory is never enqueued, so nothing below it is ever listed — not merely filtered afterwards.

**The root itself is checked.** §1.1's exclusion *"must apply both to scanned sources and to candidate roots"*, so a selected root that is itself one of the eleven names is rejected before its first listing, with `applies_to` naming which side it was offered on. This is Done-means 5's mechanism.

**Candidate roots are context.** §1.1: *"roots are context for the proposal canvas, not permission to move files. The engine uses them to understand the current folder landscape."* So a candidate root is traversed for its **landscape** — exclusion verdicts (R3) and directory inventory (R6) — and yields `ObservedFile` items tagged `applies_to = "candidate root"` that the writer counts but does not turn into `files` rows (Task 10). **This is a reading, not a SPEC sentence:** the SPEC never says candidate roots produce `files` rows and §1.1 calls them context, but it does make Done-means 5's *"zero `files` rows"* half easy to satisfy. Reported as such; the exclusion-verdict half of Done-means 5 is where the real assertion is, and it is tested here.

**The budget is a caller-supplied predicate and P3 holds no number.** §8.6's configurable-ceiling list names none for traversal or hashing, and SPEC Q15 is open. `budget_exhausted` is therefore a required keyword with **no default**: P3 owns no ceiling, invents none, and a caller with no ceiling passes a predicate that never fires. Nothing in `scan_agent` compares a count to a threshold.

**A directory observed only in part gets no R6 row.** When the budget fires mid-listing, the entries already observed are retained (§8.6: *"retain extracted evidence"*), every remaining entry is recorded as deferred, the containing directory is recorded as deferred too, and no inventory row is emitted for it — R6 has no field for a partial count, and adding one would be inventing a field. Done-means 15's *"every non-excluded directory has an R6 row"* is an assertion about a completed run; a deferred directory is visible in `scan_deferrals` instead, which is exactly §8.6's *"what has been deferred, and why"*.

**Three deferral reasons, each tracing to the design or to a named open question.** None is a judgement about the file:

```text
scan budget exhausted                          §8.6 — the only reason R5 counts
traversal behaviour unresolved (SPEC Q7)       symlinks, aliases, and every other
                                               non-regular entry: §8.3 defines these
                                               at mutation time only, traversal is
                                               unstated, and P3 invents no rule
path absent at scan time (SPEC Q14)            a directory that vanished between
                                               selection and listing; what happens to
                                               a record whose path no longer exists is
                                               open and is not decided here
```

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_traversal.py
from pathlib import Path

import pytest

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.deferrals import (
    DEFERRED_BUDGET, DEFERRED_PATH_ABSENT, DEFERRED_TRAVERSAL_UNRESOLVED,
)
from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, EXCLUDED_DIRECTORY_NAMES,
    PROJECT_ROOT_MARKERS, ExclusionVerdict, RULE_LITERAL_DIRECTORY_NAME,
    RULE_PROJECT_ROOT_DESCENDANT,
)
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk

NEVER = lambda: False           # a caller with no ceiling (§8.6 names none for traversal)


def _walk(root, *, sources=None, roots=None, budget=NEVER):
    return list(walk(FilesystemCorpusSource(),
                     sources=[root] if sources is None else sources,
                     candidate_roots=[] if roots is None else roots,
                     budget_exhausted=budget))


class RecordingSource(FilesystemCorpusSource):
    def __init__(self):
        self.listed = []

    def entries(self, directory):
        self.listed.append(str(directory))
        return super().entries(directory)


def test_no_source_set_means_no_traversal(corpus: Path):
    # Done-means 2: "Given no source set, zero rows and zero traversal — no default
    # corpus is synthesized."
    source = RecordingSource()
    items = list(walk(source, sources=[], candidate_roots=[], budget_exhausted=NEVER))
    assert items == []
    assert source.listed == []


def test_one_observed_file_per_non_excluded_file(corpus: Path):
    (corpus / "a.txt").write_bytes(b"a")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "b.pdf").write_bytes(b"b")
    files = [i for i in _walk(corpus) if isinstance(i, ObservedFile)]
    assert sorted(f.path for f in files) == [
        str(corpus / "a.txt"), str(corpus / "sub" / "b.pdf"),
    ]
    assert all(f.applies_to == APPLIES_TO_SCANNED_SOURCE for f in files)


def test_each_of_the_eleven_names_is_pruned(corpus: Path):
    # Done-means 3, and the walking skeleton's assertion on node_modules.
    for name in EXCLUDED_DIRECTORY_NAMES:
        directory = corpus / name
        directory.mkdir()
        (directory / "buried.txt").write_bytes(b"x")
        (directory / "deeper").mkdir()
        (directory / "deeper" / "deeper.txt").write_bytes(b"x")
    (corpus / "keep.txt").write_bytes(b"k")

    items = _walk(corpus)
    files = [i for i in items if isinstance(i, ObservedFile)]
    assert [f.path for f in files] == [str(corpus / "keep.txt")]

    verdicts = [i for i in items if isinstance(i, ExclusionVerdict)]
    assert {v.rule_subject for v in verdicts} == set(EXCLUDED_DIRECTORY_NAMES)
    assert {v.rule for v in verdicts} == {RULE_LITERAL_DIRECTORY_NAME}
    # pruned, not filtered: nothing inside them was ever listed
    assert not any("buried" in v.path or "deeper" in v.path for v in verdicts)


def test_a_pruned_directory_is_never_listed(corpus: Path):
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "pkg").mkdir()
    source = RecordingSource()
    list(walk(source, sources=[corpus], candidate_roots=[], budget_exhausted=NEVER))
    assert str(corpus / "node_modules") not in source.listed


def test_a_project_root_yields_no_files_from_its_descendants(corpus: Path):
    # Done-means 4, for each of §1.1's four markers.
    for index, marker in enumerate(PROJECT_ROOT_MARKERS):
        project = corpus / f"project{index}"
        (project / "src").mkdir(parents=True)
        (project / marker).write_bytes(b"{}")
        (project / "notes.md").write_bytes(b"notes")
        (project / "src" / "main.rs").write_bytes(b"code")
    (corpus / "essay.docx").write_bytes(b"essay")

    items = _walk(corpus)
    files = [i for i in items if isinstance(i, ObservedFile)]
    assert [f.path for f in files] == [str(corpus / "essay.docx")]
    rejected = [i for i in items if isinstance(i, ExclusionVerdict)
                and i.rule == RULE_PROJECT_ROOT_DESCENDANT]
    assert {i.rule_subject for i in rejected} == set(PROJECT_ROOT_MARKERS)


def test_the_same_rules_fire_on_a_candidate_root(corpus: Path):
    # Done-means 5: the exclusion "must apply both to scanned sources and to
    # candidate roots". Same tree, same rules, same subjects — only applies_to differs.
    (corpus / "node_modules").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "index.js").write_bytes(b"x")

    as_source = [i for i in _walk(corpus) if isinstance(i, ExclusionVerdict)]
    as_root = [i for i in _walk(corpus, sources=[], roots=[corpus])
               if isinstance(i, ExclusionVerdict)]

    assert [(v.path, v.rule, v.rule_subject) for v in as_source] == \
           [(v.path, v.rule, v.rule_subject) for v in as_root]
    assert {v.applies_to for v in as_source} == {APPLIES_TO_SCANNED_SOURCE}
    assert {v.applies_to for v in as_root} == {APPLIES_TO_CANDIDATE_ROOT}


def test_a_root_that_is_itself_excluded_is_rejected_before_listing(corpus: Path):
    excluded_root = corpus / "Library"
    excluded_root.mkdir()
    (excluded_root / "inside.txt").write_bytes(b"x")
    source = RecordingSource()
    items = list(walk(source, sources=[], candidate_roots=[excluded_root],
                      budget_exhausted=NEVER))
    assert [type(i) for i in items] == [ExclusionVerdict]
    assert items[0].applies_to == APPLIES_TO_CANDIDATE_ROOT
    assert source.listed == []


def test_every_excluded_path_carries_a_verdict_naming_its_rule(corpus: Path):
    # Done-means 6.
    (corpus / "dist").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    verdicts = [i for i in _walk(corpus) if isinstance(i, ExclusionVerdict)]
    assert verdicts
    for verdict in verdicts:
        assert verdict.rule
        assert verdict.rule_subject
        assert verdict.applies_to


def test_every_non_excluded_directory_is_observed(corpus: Path):
    (corpus / "sub" / "deep").mkdir(parents=True)
    (corpus / "sub" / "a.txt").write_bytes(b"a")
    directories = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)]
    by_path = {d.directory_path: d for d in directories}
    assert set(by_path) == {str(corpus), str(corpus / "sub"), str(corpus / "sub" / "deep")}
    assert by_path[str(corpus)].parent_directory is None
    assert by_path[str(corpus / "sub")].parent_directory == str(corpus)
    assert by_path[str(corpus / "sub")].file_count == 1
    assert by_path[str(corpus / "sub")].subdirectory_count == 1
    assert by_path[str(corpus / "sub")].extension_mix == {".txt": 1}


def test_counts_exclude_what_the_rules_rejected(corpus: Path):
    (corpus / "build").mkdir()
    (corpus / "a.txt").write_bytes(b"a")
    root = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)][-1]
    assert root.file_count == 1
    assert root.subdirectory_count == 0


def test_a_project_root_keeps_its_own_directory_row_and_its_markers(corpus: Path):
    # SPEC Q9 is OPEN. The marker-bearing directory is not rejected by §1.1's
    # "descendants" rule, so it keeps an inventory row and the markers land on it as
    # evidence (R6). Nothing here says whether it may be a candidate root.
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "Cargo.toml").write_bytes(b"[package]")
    row = [i for i in _walk(corpus) if isinstance(i, ObservedDirectory)
           and i.directory_path == str(corpus / "app")][0]
    assert row.project_root_markers == ("package.json", "Cargo.toml")
    assert row.file_count == 0


def test_a_symlink_is_recorded_as_unresolved_not_indexed(corpus: Path):
    # SPEC Q7 is OPEN: traversal of symlinks, aliases, packages and mounts is
    # unstated. P3 records the case and decides nothing.
    (corpus / "real").mkdir()
    (corpus / "link").symlink_to(corpus / "real")
    items = _walk(corpus)
    deferred = [i for i in items if isinstance(i, Deferred)]
    assert [(d.path, d.reason) for d in deferred] == [
        (str(corpus / "link"), DEFERRED_TRAVERSAL_UNRESOLVED),
    ]
    assert not any(isinstance(i, ObservedFile) for i in items)


def test_a_directory_that_vanished_is_recorded_not_crashed(corpus: Path):
    items = list(walk(FilesystemCorpusSource(), sources=[corpus / "gone"],
                      candidate_roots=[], budget_exhausted=NEVER))
    assert [(i.path, i.reason) for i in items] == [
        (str(corpus / "gone"), DEFERRED_PATH_ABSENT),
    ]


def test_budget_exhaustion_defers_the_remainder_and_keeps_what_was_seen(corpus: Path):
    # Done-means 13's traversal half. §8.6: "retain extracted evidence, mark the
    # deferred stage… Cost exhaustion must never turn into lower-quality automatic
    # classification." The observations already made survive.
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"x")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "d.txt").write_bytes(b"x")

    seen = {"n": 0}

    def after_two():
        seen["n"] += 1
        return seen["n"] > 2

    items = _walk(corpus, budget=after_two)
    observed = [i for i in items if isinstance(i, ObservedFile)]
    deferred = [i for i in items if isinstance(i, Deferred)]
    assert observed                                     # retained, not discarded
    assert deferred
    assert {d.reason for d in deferred} == {DEFERRED_BUDGET}
    # the partially-listed directory has no inventory row: R6 has no partial count
    assert not [i for i in items if isinstance(i, ObservedDirectory)
                and i.directory_path == str(corpus)]
    assert str(corpus) in {d.path for d in deferred}


def test_budget_exhaustion_defers_unreached_directories_too(corpus: Path):
    (corpus / "sub").mkdir()
    (corpus / "sub" / "a.txt").write_bytes(b"x")
    (corpus / "other").mkdir()
    (corpus / "other" / "b.txt").write_bytes(b"x")

    calls = {"n": 0}

    def after_the_root():
        calls["n"] += 1
        return calls["n"] > 2

    deferred = [i for i in _walk(corpus, budget=after_the_root) if isinstance(i, Deferred)]
    assert {str(corpus / "sub"), str(corpus / "other")} <= {d.path for d in deferred}


def test_budget_exhausted_is_required_with_no_default(corpus: Path):
    # §8.6 names no ceiling for traversal (SPEC Q15 is open), so P3 holds none and
    # the caller must supply the predicate.
    with pytest.raises(TypeError):
        list(walk(FilesystemCorpusSource(), sources=[corpus], candidate_roots=[]))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_traversal.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.deferrals'`

- [ ] **Step 3: Write `deferrals.py`**

```python
# src/scan_agent/deferrals.py
"""Paths P3 did not index and no §1.1 rule rejected.

§8.6: "The user should be able to see what is running, what has been deferred, and
why", and "the difference between completed work and deferred work" must be visible
"so that no unscanned file reads as one that was understood and found unimportant."

Every reason below names the design rule or the open question that produced it. None
of them is a judgement about the file, and none is a status from P4's closed
vocabulary — that vocabulary is P4's and P3 writes no extraction run.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

#: §8.6's budget exhaustion. This is the ONLY reason R5's deferred counter reports,
#: because R5's counter is spelled "files deferred (scan budget exhausted)".
DEFERRED_BUDGET = "scan budget exhausted"

#: SPEC Q7 is OPEN — scan-time traversal of symlinks, aliases, macOS packages and
#: application bundles, network mounts, removable storage and cloud-synced
#: directories is unstated. P3 records the case rather than inventing a rule.
DEFERRED_TRAVERSAL_UNRESOLVED = "traversal behaviour unresolved (SPEC Q7)"

#: SPEC Q14 is OPEN — what happens to a record whose path no longer exists is not
#: settled. P3 records that the path was gone and decides nothing else.
DEFERRED_PATH_ABSENT = "path absent at scan time (SPEC Q14)"

DEFERRALS_DDL = """
CREATE TABLE IF NOT EXISTS scan_deferrals (
    deferral_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    is_directory INTEGER NOT NULL,
    reason       TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
"""


def record_deferral(conn: sqlite3.Connection, scan_run_id: str, deferred) -> int:
    conn.execute(
        "INSERT INTO scan_deferrals "
        "(scan_run_id, path, is_directory, reason, observed_at) VALUES (?, ?, ?, ?, ?)",
        (scan_run_id, deferred.path, int(deferred.is_directory), deferred.reason,
         datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def scan_deferrals(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM scan_deferrals WHERE scan_run_id = ? ORDER BY deferral_id",
        (scan_run_id,),
    ).fetchall()
```

- [ ] **Step 4: Write `traversal.py`**

```python
# src/scan_agent/traversal.py
"""The corpus boundary: §1.1's exclusion rules applied while walking.

A pure generator over a CorpusSource. It opens no database and writes no row, so
every §1.1 decision is finished before any record exists — which is what lets Task
13's curation signal be provably unable to change an exclusion or a cache verdict.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import PurePath

from scan_agent.corpus_source import KIND_DIRECTORY, KIND_FILE, CorpusSource
from scan_agent.deferrals import (
    DEFERRED_BUDGET, DEFERRED_PATH_ABSENT, DEFERRED_TRAVERSAL_UNRESOLVED,
)
from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, exclusion_for,
    project_root_markers_in,
)


@dataclass(frozen=True)
class ObservedFile:
    """A non-excluded file. The writer turns a scanned-source one into an R2 row."""
    path: str
    size: int
    mtime: float
    dataless: bool
    applies_to: str


@dataclass(frozen=True)
class ObservedDirectory:
    """R6's observations for one fully-listed non-excluded directory."""
    directory_path: str
    parent_directory: str | None
    file_count: int
    subdirectory_count: int
    extension_mix: dict[str, int]
    project_root_markers: tuple[str, ...]
    applies_to: str


@dataclass(frozen=True)
class Deferred:
    path: str
    is_directory: bool
    reason: str


def walk(source: CorpusSource, *,
         sources: Iterable,
         candidate_roots: Iterable,
         budget_exhausted: Callable[[], bool]) -> Iterator:
    """Walk both sides of the scan, applying §1.1 before descending.

    `budget_exhausted` is required and has no default: §8.6's configurable-ceiling
    list names none for traversal or hashing (SPEC Q15 is open), so P3 holds no
    ceiling of its own and a caller with none supplies a predicate that never fires.
    """
    for root in sources:
        yield from _walk_root(source, root, APPLIES_TO_SCANNED_SOURCE, budget_exhausted)
    for root in candidate_roots:
        yield from _walk_root(source, root, APPLIES_TO_CANDIDATE_ROOT, budget_exhausted)


def _walk_root(source, root, applies_to, budget_exhausted) -> Iterator:
    root = str(root)
    root_verdict = exclusion_for(root, is_dir=True, applies_to=applies_to)
    if root_verdict is not None:
        # §1.1's exclusion "must apply both to scanned sources and to candidate
        # roots" — including when the root IS one of the eleven names.
        yield root_verdict
        return

    queue: deque[tuple[str, str | None]] = deque([(root, None)])
    while queue:
        directory, parent = queue.popleft()
        try:
            entries = source.entries(directory)
        except (FileNotFoundError, NotADirectoryError):
            yield Deferred(directory, True, DEFERRED_PATH_ABSENT)
            continue

        markers = project_root_markers_in(
            (entry.name, entry.kind == KIND_DIRECTORY) for entry in entries
        )
        file_count = 0
        subdirectory_count = 0
        mix: Counter[str] = Counter()

        for index, entry in enumerate(entries):
            if budget_exhausted():
                # Retain what was already observed (§8.6), record everything not
                # reached, and emit NO inventory row for this directory: R6 has no
                # field for a partial count and P3 does not invent one.
                for remaining in entries[index:]:
                    yield Deferred(remaining.path,
                                   remaining.kind == KIND_DIRECTORY, DEFERRED_BUDGET)
                yield Deferred(directory, True, DEFERRED_BUDGET)
                while queue:
                    pending, _ = queue.popleft()
                    yield Deferred(pending, True, DEFERRED_BUDGET)
                return

            is_dir = entry.kind == KIND_DIRECTORY
            verdict = exclusion_for(entry.path, is_dir=is_dir, applies_to=applies_to,
                                    project_root_markers=markers)
            if verdict is not None:
                yield verdict          # pruned: never enqueued, never listed
                continue
            if is_dir:
                subdirectory_count += 1
                queue.append((entry.path, directory))
            elif entry.kind == KIND_FILE:
                file_count += 1
                mix[PurePath(entry.path).suffix] += 1
                yield ObservedFile(entry.path, entry.size, entry.mtime,
                                   entry.dataless, applies_to)
            else:
                yield Deferred(entry.path, False, DEFERRED_TRAVERSAL_UNRESOLVED)

        yield ObservedDirectory(directory, parent, file_count, subdirectory_count,
                                dict(mix), markers, applies_to)
```

`src/scan_agent/schema.py` in full at this point:

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL
from scan_agent.dataless import DATALESS_DDL
from scan_agent.deferrals import DEFERRALS_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(DATALESS_DDL)
    conn.executescript(DEFERRALS_DDL)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_traversal.py -v`
Expected: PASS — 16 passed

- [ ] **Step 6: Commit**

```bash
git add src/scan_agent/deferrals.py src/scan_agent/traversal.py src/scan_agent/schema.py tests/p3/test_p3_traversal.py
git commit -m "feat(P3): traversal that prunes at 1.1's rules on both sides of the scan"
```

---

### Task 10: R2 — the ten §1.2 fields, written through P1 and authored by P3 (Done-means 1, 10, 11)

**Files:**
- Create: `src/scan_agent/basic_record.py`
- Create: `src/scan_agent/scan.py`
- Modify: `src/scan_agent/__init__.py` — export `scan`
- Test: `tests/p3/test_p3_basic_record.py`

**Interfaces:**
- Consumes: `database_agent.files_table.observe_path` / `get_file`, `database_agent.events.append_event`, `scan_agent.authorship.event_defaults`, `walk`, `record_exclusion`, `record_deferral`, `record_dataless_detection`, `require_access`, `start_scan_run` / `finish_scan_run`, `selection_sources` / `selection_candidate_roots`.
- Produces (`basic_record.py`): `parent_folder_context(path) -> str`, `record_basic_record(conn, observed, *, mime_type_for, scan_state) -> str`.
- Produces (`scan.py`): `scan(conn, selection_id, *, source, mime_type_for, scan_state, budget_exhausted) -> str` returning the `scan_run_id`.

**This is where the authorship rule becomes a row.** Every event this task produces names P3:

```text
discovery          appended by P3, once, when a file first enters the corpus     §1.1
stat observation   appended by P3, every scan, carrying the observed size/mtime  §1.2
hashing            appended INSIDE P1's observe_path with subsystem = the
                   `author` P3 supplied — so it is P3-authored and P1-written,
                   which is exactly M8                                           §1.2
```

P3 appends the first two itself and passes `author="P3"` into `observe_path` for the third. P1's `test_p1_authors_none_of_the_scan_events` is the other half of this contract; the tests below are P3's half and assert the same rows from the other side.

**`observe_path` is the only route to a `files` row.** §8.2 makes P1 the owner of identity resolution: *"If the same content appears at a new path, the system recognizes it as the same file version. If a file retains its name but its content hash changes, the system treats it as a new version."* P3 supplies (path, size, mtime, content hash) and P1 decides — so P3 never inserts into `files` directly and never mints a `file_id`. Done-means 10 is therefore a test of P3 **not** doing something: a moved file resolves to the same identity and P3 emits no second one.

**MIME type is a caller-supplied strategy, because SPEC Q6 is OPEN.** *"How MIME type is determined. §1.2 requires the field; §2.9 says to 'inspect the real MIME type or file signature where possible'… Does P3 sniff signatures, or record an extension-derived type that P5 later corrects?"* This plan does not choose. `mime_type_for` is a required keyword with no default; `scan_agent` imports no `mimetypes`, holds no signature table, and Task 17 asserts both. R2's field is populated by whatever the caller's strategy returns, which satisfies Done-means 1 without answering Q6.

**`scan_state` is a caller-supplied value, because SPEC Q4 is OPEN.** *"`scan state` enumeration (§1.2), and its relationship to §8.2's 'extraction status by extractor tier'. Are they one field or two?"* This plan invents no enumeration and no per-file state logic: one required `scan_state` value is applied to every row a run writes, `scan_agent` contains no scan-state vocabulary, and Task 17 asserts it.

**`detected_format` is `None`.** It is not one of R2's ten; it is §8.2's field and §2.9's determination is P5's. P3 invents no value another part owns.

**Parent-folder context is the parent directory's path.** §1.2 spells the field *directory position*, §2.9 spells it *parent-folder context*, and MINOR 11 settled that they are **one field under §2.9's name**, stored in P1's `directory_position` column. MINOR 11 also says *"What the value contains is still only what §1.2 and §2.9 say — P3 invents no structure for it."* So the value is the parent directory's path and nothing more: no depth number, no ancestor list, no computed role.

**Candidate roots produce no `files` row.** §1.1: roots are context. The writer skips `ObservedFile` items whose `applies_to` is `candidate root`; their counts still reach R6 (Task 13).

**A dataless file produces no `files` row either** — the detection is recorded (Task 6) and the file is skipped before any hashing is attempted (11 §5).

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_basic_record.py
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import file_path_history, get_file
from database_agent.identity import hash_file

from scan_agent.access import FullDiskAccessRequired
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"     # SPEC Q4 is OPEN; the caller supplies this


def fixture_mime(path: Path) -> str | None:
    """Stands in for whoever answers SPEC Q6. P3 holds no determination method."""
    return {".pdf": "application/pdf", ".txt": "text/plain"}.get(path.suffix)


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus, *, roots=(), sources=None):
    selection = record_selection(
        conn, sources=[corpus] if sources is None else sources,
        candidate_roots=list(roots), cross_folder_moves=False, selected_by=None,
    )
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def test_one_row_per_non_excluded_file_with_all_ten_1_2_fields(ready, corpus: Path):
    # Done-means 1.
    document = corpus / "Syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "ignored.pdf").write_bytes(b"x")

    _scan(ready, corpus)

    rows = ready.execute("SELECT * FROM files").fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["current_path"] == str(document)                     # 1  path
    assert row["filename"] == "Syllabus.pdf"                        # 2  filename
    assert row["normalized_filename"] == "Syllabus.pdf"             # 3  normalized
    assert row["extension"] == ".pdf"                               # 4  extension
    assert row["mime_type"] == "application/pdf"                    # 5  MIME type
    assert row["observed_size"] == len(b"%PDF-1.4 fixture bytes")   # 6  size
    assert row["observed_timestamps"]                               # 7  timestamps
    assert row["directory_position"] == str(corpus)                 # 8  parent-folder
    assert row["content_hash"] == hash_file(document, materialized=True)   # 9 hash
    assert row["scan_state"] == FIXTURE_STATE                       # 10 scan state


def test_p3_supplies_no_detected_format(ready, corpus: Path):
    # detected_format is NOT one of R2's ten. It is §8.2's field and §2.9's
    # determination is P5's; P3 invents no value another part owns.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    assert ready.execute("SELECT detected_format FROM files").fetchone()[0] is None


def test_p3_is_the_author_of_every_event_the_scan_produces(ready, corpus: Path):
    # M8, and the other half of P1's test_p1_authors_none_of_the_scan_events.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    rows = ready.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in rows] == ["P3"]


def test_discovery_stat_observation_and_hashing_are_all_appended(ready, corpus: Path):
    # Done-means 11, first half.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    types = {r["event_type"] for r in ready.execute("SELECT event_type FROM events")}
    assert {"discovery", "stat observation", "hashing"} <= types


def test_the_hashing_event_is_p3s_even_though_p1_wrote_it(ready, corpus: Path):
    # P1's observe_path appends `hashing` with subsystem = the `author` P3 supplied.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    row = ready.execute(
        "SELECT subsystem FROM events WHERE event_type = 'hashing'"
    ).fetchone()
    assert row["subsystem"] == "P3"


def test_a_second_scan_adds_a_stat_observation_and_keeps_the_first(ready, corpus: Path):
    # Done-means 11, second half: "a second scan of the same file adds a new stat
    # observation and leaves the earlier one intact and readable."
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    first = ready.execute(
        "SELECT event_id, explanation FROM events WHERE event_type = 'stat observation' "
        "ORDER BY event_id"
    ).fetchall()
    _scan(ready, corpus)
    after = ready.execute(
        "SELECT event_id, explanation FROM events WHERE event_type = 'stat observation' "
        "ORDER BY event_id"
    ).fetchall()
    assert len(after) == len(first) + 1
    assert after[0]["event_id"] == first[0]["event_id"]
    assert after[0]["explanation"] == first[0]["explanation"]


def test_discovery_is_appended_once_per_file(ready, corpus: Path):
    # §8.2's `discovery` is "a file enters the corpus". It enters once.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    _scan(ready, corpus)
    count = ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'discovery'"
    ).fetchone()["c"]
    assert count == 1


def test_a_moved_file_resolves_to_one_identity(ready, corpus: Path):
    # Done-means 10: "A file moved to a new path with byte-identical content resolves
    # to the same file version, and P3 emits no second identity."
    first = corpus / "one.pdf"
    first.write_bytes(b"identical bytes")
    _scan(ready, corpus)
    file_id = ready.execute("SELECT file_id FROM files").fetchone()["file_id"]

    moved = corpus / "moved" / "one.pdf"
    moved.parent.mkdir()
    first.rename(moved)
    _scan(ready, corpus)

    rows = ready.execute("SELECT * FROM files").fetchall()
    assert len(rows) == 1
    assert rows[0]["file_id"] == file_id
    assert rows[0]["current_path"] == str(moved)
    history = [r["path"] for r in file_path_history(ready, file_id)]
    assert history[0] == str(first)          # discovered here
    assert history[-1] == str(moved)         # and observed here afterwards
    assert set(history) == {str(first), str(moved)}     # and nowhere else


def test_a_candidate_root_contributes_no_files_row(ready, corpus: Path, tmp_path: Path):
    # §1.1: "roots are context for the proposal canvas, not permission to move files."
    landscape = tmp_path / "Documents"
    landscape.mkdir()
    (landscape / "elsewhere.txt").write_bytes(b"x")
    (corpus / "in-corpus.txt").write_bytes(b"x")
    _scan(ready, corpus, roots=[landscape])
    paths = [r["current_path"] for r in ready.execute("SELECT current_path FROM files")]
    assert paths == [str(corpus / "in-corpus.txt")]


def test_a_dataless_file_is_detected_and_never_hashed(ready, corpus: Path, monkeypatch):
    # 11 §5. SF_DATALESS is not settable on a fixture, so the source's verdict is
    # what is driven here; the point under test is that P3 skips before hashing.
    import scan_agent.corpus_source as module
    (corpus / "cloud.pdf").write_bytes(b"bytes that must not be read")

    real_entries = module.FilesystemCorpusSource.entries

    def entries(self, directory):
        from dataclasses import replace
        return [replace(e, dataless=e.name == "cloud.pdf")
                for e in real_entries(self, directory)]

    monkeypatch.setattr(module.FilesystemCorpusSource, "entries", entries)
    run = _scan(ready, corpus)

    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    detections = ready.execute(
        "SELECT path FROM dataless_detections WHERE scan_run_id = ?", (run,)
    ).fetchall()
    assert [d["path"] for d in detections] == [str(corpus / "cloud.pdf")]


def test_mime_strategy_and_scan_state_are_required(ready, corpus: Path):
    # SPEC Q6 and Q4 are OPEN. P3 holds neither a determination method nor an
    # enumeration, so the caller must supply both.
    selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    with pytest.raises(TypeError):
        scan(ready, selection, source=FilesystemCorpusSource(),
             scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    with pytest.raises(TypeError):
        scan(ready, selection, source=FilesystemCorpusSource(),
             mime_type_for=fixture_mime, budget_exhausted=NEVER)


def test_no_source_set_writes_nothing(ready, corpus: Path):
    # Done-means 2, at the writer.
    run = _scan(ready, corpus, sources=[])
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    assert ready.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
    assert ready.execute(
        "SELECT count(*) c FROM exclusion_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchone()["c"] == 0


def test_an_unreadable_root_refuses_the_scan_before_any_row_exists(ready, corpus: Path):
    # 11 §1: "Until it is granted, P3 does not traverse." No run row either.
    import os
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can list a 0o000 directory")
    corpus.chmod(0o000)
    try:
        selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                     cross_folder_moves=False, selected_by=None)
        with pytest.raises(FullDiskAccessRequired):
            scan(ready, selection, source=FilesystemCorpusSource(),
                 mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                 budget_exhausted=NEVER)
    finally:
        corpus.chmod(0o700)
    assert ready.execute("SELECT count(*) c FROM scan_runs").fetchone()["c"] == 0
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_basic_record.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.scan'`

- [ ] **Step 3: Write `basic_record.py`**

```python
# src/scan_agent/basic_record.py
"""Contract out R2 — the §1.2 per-file-version basic record.

§1.2: "For every file, the engine records path, filename, normalized filename,
extension, MIME type, size, timestamps, directory position, content hash, and scan
state."

R2 is the ONLY computation of this record (O5): P5's `source_type: filesystem`
observations cite this row and recompute none of its ten fields. P3 does not insert
into `files` — P1 owns identity resolution (§8.2) — so every field arrives through
P1's `observe_path`, which is also what makes the events P3-authored and P1-written.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from pathlib import Path, PurePath

from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path

from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM, event_defaults


def parent_folder_context(path) -> str:
    """§2.9's published name for §1.2's "directory position" — one field (MINOR 11).

    The value is the parent directory's path and nothing more. MINOR 11: "What the
    value contains is still only what §1.2 and §2.9 say — P3 invents no structure
    for it." No depth number, no ancestor list, no computed role.
    """
    return str(PurePath(path).parent)


def _already_discovered(conn: sqlite3.Connection, file_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM events WHERE file_id = ? AND event_type = 'discovery' LIMIT 1",
        (file_id,),
    ).fetchone() is not None


def record_basic_record(conn: sqlite3.Connection, observed, *,
                        mime_type_for: Callable[[Path], str | None],
                        scan_state: str) -> str:
    """Write one R2 row through P1 and append P3's events. Returns the file_id.

    `mime_type_for` is the caller's strategy: SPEC Q6 is OPEN on whether P3 sniffs a
    signature or records an extension-derived type P5 later corrects, and this plan
    answers neither. `scan_state` is the caller's value: SPEC Q4 is OPEN on the
    enumeration, and P3 invents none.
    """
    path = Path(observed.path)
    file_id = observe_path(
        conn, path,
        author=SUBSYSTEM,                # M8: the acting part authors, P1 writes
        component_version=COMPONENT_VERSION,
        parent_folder_context=parent_folder_context(path),
        mime_type=mime_type_for(path),
        detected_format=None,        # not one of R2's ten; §2.9's determination is P5's
        scan_state=scan_state,
        materialized=not observed.dataless,
    )
    content_hash = get_file(conn, file_id)["content_hash"]

    if not _already_discovered(conn, file_id):
        append_event(conn, **event_defaults(
            event_type="discovery", file_id=file_id, content_hash=content_hash,
            new_path=observed.path,
            explanation=json.dumps({"rule": "§1.1 corpus selection",
                                    "applies_to": observed.applies_to}),
        ))

    append_event(conn, **event_defaults(
        event_type="stat observation", file_id=file_id, content_hash=content_hash,
        new_path=observed.path,
        explanation=json.dumps({"observed_size": observed.size,
                                "observed_modification_time": observed.mtime}),
    ))
    return file_id
```

- [ ] **Step 4: Write `scan.py`**

```python
# src/scan_agent/scan.py
"""One scan run: §1.1's boundary and §1.2's records, written through P1."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

from scan_agent.access import require_access
from scan_agent.basic_record import record_basic_record
from scan_agent.corpus_source import CorpusSource
from scan_agent.dataless import record_dataless_detection
from scan_agent.deferrals import record_deferral
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE, ExclusionVerdict, record_exclusion
from scan_agent.run import finish_scan_run, start_scan_run
from scan_agent.selection import selection_candidate_roots, selection_sources
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk


def scan(conn: sqlite3.Connection, selection_id: str, *,
         source: CorpusSource,
         mime_type_for: Callable[[Path], str | None],
         scan_state: str,
         budget_exhausted: Callable[[], bool]) -> str:
    """Run one scan against one R1 selection. Returns P3's local run handle.

    Full Disk Access is checked BEFORE the run row exists: 11-ops-runtime.md §1 says
    "Until it is granted, P3 does not traverse", and a refused scan should leave no
    partial corpus and no run to mistake for one.
    """
    sources = selection_sources(conn, selection_id)
    candidate_roots = selection_candidate_roots(conn, selection_id)
    require_access([*sources, *candidate_roots])

    scan_run_id = start_scan_run(conn, selection_id)
    for item in walk(source, sources=sources, candidate_roots=candidate_roots,
                     budget_exhausted=budget_exhausted):
        if isinstance(item, ExclusionVerdict):
            record_exclusion(conn, scan_run_id, item)
        elif isinstance(item, Deferred):
            record_deferral(conn, scan_run_id, item)
        elif isinstance(item, ObservedDirectory):
            pass                      # R6 lands in Task 13
        elif isinstance(item, ObservedFile):
            if item.applies_to != APPLIES_TO_SCANNED_SOURCE:
                continue              # §1.1: roots are context, not corpus
            if item.dataless:
                # 11 §5: do not materialize, hash, or extract. No `files` row and no
                # extraction run — the status such a file carries is P4 OQ6.
                record_dataless_detection(conn, scan_run_id, item.path)
                continue
            record_basic_record(conn, item, mime_type_for=mime_type_for,
                                scan_state=scan_state)
    finish_scan_run(conn, scan_run_id)
    return scan_run_id
```

```python
# src/scan_agent/__init__.py
"""P3 — scan and corpus selection. The only part that walks the filesystem."""
from scan_agent.scan import scan

__all__ = ["scan"]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_basic_record.py -v`
Expected: PASS — 13 passed

- [ ] **Step 6: Commit**

```bash
git add src/scan_agent/basic_record.py src/scan_agent/scan.py src/scan_agent/__init__.py tests/p3/test_p3_basic_record.py
git commit -m "feat(P3): R2 basic record through P1, every scan event authored by P3"
```

---

### Task 11: R4 — the stat cache (Done-means 7, 8, 9)

**Files:**
- Create: `src/scan_agent/stat_cache.py`
- Modify: `src/scan_agent/basic_record.py` — publish `append_stat_observation`
- Modify: `src/scan_agent/scan.py` — take the verdict before hashing
- Modify: `src/scan_agent/schema.py` — add `STAT_CACHE_DDL`
- Test: `tests/p3/test_p3_stat_cache.py`

**Interfaces:**
- Consumes: `record_basic_record`, `walk`, `start_scan_run`.
- Produces: `VERDICT_REUSE`, `VERDICT_RECOMPUTE`, `REASON_FIRST_OBSERVATION`, `REASON_UNCHANGED`, `REASON_SIZE_CHANGED`, `REASON_MODIFICATION_TIME_CHANGED`, `CacheVerdict` (frozen dataclass), `STAT_CACHE_DDL: str`, `cache_verdict(observed, prior) -> CacheVerdict`, `prior_observation(conn, path) -> sqlite3.Row | None`, `record_cache_verdict(conn, scan_run_id, path, file_id, verdict) -> int`, `cache_verdicts(conn, scan_run_id) -> list[sqlite3.Row]`.
- Produces (`basic_record.py`): `append_stat_observation(conn, file_id, observed) -> None`.

**§1.2's rule, quoted, because every clause of it is load-bearing.** *"It uses a stat-based cache: if a file's size and modification time have not changed, the engine reuses its existing extraction results. If either changes, it recomputes the relevant information instead of assuming that time only moves forward. This protects against restores, migrations, and other filesystem changes that can alter state unexpectedly."*

- **Disjunctive**: *"if **either** changes"* — size **or** modification time, not both.
- **A difference test, not a newer-than test**: *"instead of assuming that time only moves forward"*. An mtime that moves **backwards** is a change. The comparison is `!=`, never `>`, and Task 17's guard asserts no `>` or `<` appears between two modification times.
- **`recompute` includes re-hashing** (SPEC R4): §1.2 requires recomputing *"the relevant information"* and §8.2 makes the content hash the thing that decides whether a new version exists.

**A first observation is a `recompute`.** There is nothing to reuse. `reason` is `first observation`, which is one of R4's four literal reasons.

**Both changed → one reason, `size changed`.** R4's `reason` is a single value and the SPEC supplies no compound one. Size is tested first so the choice is deterministic across runs and replays; the observed and prior values for **both** size and mtime are on the row regardless, so nothing is lost.

**The lookup is by path, and it is P3's own record.** The verdict must be reached **before** hashing, and before hashing there is no content hash and therefore no P1 identity — so path is the only key available. R4's `prior observed size` and `prior observed modification time` are R4's own fields, so the prior comes from P3's previous R4 row rather than from P1's `files` columns. That also keeps P3 off P1's `observed_timestamps` JSON, which is P1's internal spelling and not a published interface. `observed_path` is on the table as mechanics, the way P1 carries `started_at` and `baseline` on `scan_resource_usage`.

**A prior row only counts if its file still lives at that path.** The lookup joins `files` on `current_path`, so a verdict left behind by a file that has since moved away cannot be reused for a different file that later appears at the old path. §1.2's own limitation — content that changes with size and mtime both identical is not detected — is the design's and is left exactly as the design leaves it.

**Reuse re-reads nothing.** No hash, no `observe_path`, no `files` write. It still appends a `stat observation`, because Done-means 11 requires a second scan to add one and leave the earlier intact.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_stat_cache.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.stat_cache import (
    REASON_FIRST_OBSERVATION, REASON_MODIFICATION_TIME_CHANGED, REASON_SIZE_CHANGED,
    REASON_UNCHANGED, VERDICT_RECOMPUTE, VERDICT_REUSE, cache_verdicts,
)

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


@pytest.fixture()
def selection(ready, corpus: Path):
    return record_selection(ready, sources=[corpus], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)


def _scan(conn, selection):
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def _rewrite_keeping_mtime(path: Path, data: bytes):
    before = path.stat()
    path.write_bytes(data)
    os.utime(path, (before.st_atime, before.st_mtime))


def test_the_first_observation_recomputes(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    run = _scan(ready, selection)
    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_FIRST_OBSERVATION
    assert row["prior_observed_size"] is None
    assert row["prior_observed_modification_time"] is None
    assert row["observed_size"] == 3
    assert row["file_id"]


def test_rescanning_an_unchanged_corpus_reuses_everything(ready, selection, corpus: Path):
    # Done-means 7: "Re-scanning an unchanged corpus yields verdict = reuse for
    # every file and zero recomputes."
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"content")
    _scan(ready, selection)
    second = _scan(ready, selection)

    rows = cache_verdicts(ready, second)
    assert len(rows) == 3
    assert {r["verdict"] for r in rows} == {VERDICT_REUSE}
    assert {r["reason"] for r in rows} == {REASON_UNCHANGED}
    assert not [r for r in rows if r["verdict"] == VERDICT_RECOMPUTE]


def test_reuse_re_reads_nothing(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"content")
    _scan(ready, selection)
    before = ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'hashing'"
    ).fetchone()["c"]
    _scan(ready, selection)
    after = ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'hashing'"
    ).fetchone()["c"]
    assert after == before
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 1


def test_size_changed_with_mtime_unchanged_recomputes(ready, selection, corpus: Path):
    # Done-means 8. §1.2: "if either changes".
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    run = _scan(ready, selection)

    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_SIZE_CHANGED
    assert row["prior_observed_size"] == 3
    assert row["observed_size"] == len(b"one plus more bytes")


def test_mtime_moving_backwards_with_size_unchanged_recomputes(ready, selection, corpus: Path):
    # Done-means 9. §1.2: "instead of assuming that time only moves forward" — this
    # is a difference test, and a restore or migration moves mtime backwards.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    run = _scan(ready, selection)

    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_MODIFICATION_TIME_CHANGED
    assert row["observed_modification_time"] < row["prior_observed_modification_time"]


def test_mtime_moving_forwards_with_size_unchanged_recomputes(ready, selection, corpus: Path):
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime + 100_000))
    run = _scan(ready, selection)
    assert cache_verdicts(ready, run)[0]["reason"] == REASON_MODIFICATION_TIME_CHANGED


def test_both_changed_reports_one_deterministic_reason(ready, selection, corpus: Path):
    # R4's `reason` is one value and the SPEC supplies no compound one. Both
    # observed and both prior values are on the row regardless.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    target.write_bytes(b"a longer body entirely")
    run = _scan(ready, selection)
    row = cache_verdicts(ready, run)[0]
    assert row["reason"] == REASON_SIZE_CHANGED
    assert row["prior_observed_size"] is not None
    assert row["prior_observed_modification_time"] is not None


def test_there_is_one_verdict_per_file_per_run(ready, selection, corpus: Path):
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_bytes(b"x")
    first = _scan(ready, selection)
    second = _scan(ready, selection)
    assert len(cache_verdicts(ready, first)) == 2
    assert len(cache_verdicts(ready, second)) == 2


def test_a_prior_verdict_is_not_reused_for_a_different_file_at_that_path(
        ready, selection, corpus: Path):
    # The prior only counts while its file still lives at that path.
    original = corpus / "a.txt"
    original.write_bytes(b"one")
    _scan(ready, selection)
    moved = corpus / "moved.txt"
    original.rename(moved)
    _scan(ready, selection)

    replacement = corpus / "a.txt"
    replacement.write_bytes(b"two")
    run = _scan(ready, selection)
    row = [r for r in cache_verdicts(ready, run)
           if r["observed_path"] == str(replacement)][0]
    assert row["reason"] == REASON_FIRST_OBSERVATION


def test_the_comparison_is_never_a_newer_than_test():
    # §1.2 says so in as many words. A `>` between two modification times would
    # reintroduce exactly the assumption the design rejects.
    import scan_agent.stat_cache as module
    source = Path(module.__file__).read_text()
    # Operators, not prose: the module docstring quotes §1.2's "instead of assuming
    # that time only moves forward", so the words are expected and the code is not.
    for forbidden in ("mtime >", "mtime <", "modification_time >",
                      "modification_time <", "> prior", "< prior", "max(", "min("):
        assert forbidden not in source, forbidden
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_stat_cache.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.stat_cache'`

- [ ] **Step 3: Write `stat_cache.py`**

```python
# src/scan_agent/stat_cache.py
"""Contract out R4 — §1.2's stat-based cache.

§1.2: "It uses a stat-based cache: if a file's size and modification time have not
changed, the engine reuses its existing extraction results. If either changes, it
recomputes the relevant information instead of assuming that time only moves forward.
This protects against restores, migrations, and other filesystem changes that can
alter state unexpectedly."

Disjunctive (size OR mtime) and a DIFFERENCE test, never a newer-than test: an mtime
that moves backwards is a change. `recompute` includes recomputing the content hash,
because §8.2 makes the hash the thing that decides whether a new version exists.

This cache decides whether P3 re-READS. §3.4's cache key — content hash + extractor
version + analysis tier + model identifier + prompt fingerprint — decides whether an
extraction RESULT is reused, and belongs to P6. Nothing here touches it.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

#: R4's two verdicts, the SPEC's words.
VERDICT_REUSE = "reuse"
VERDICT_RECOMPUTE = "recompute"

#: R4's four reasons, the SPEC's words, and no fifth.
REASON_FIRST_OBSERVATION = "first observation"
REASON_UNCHANGED = "unchanged"
REASON_SIZE_CHANGED = "size changed"
REASON_MODIFICATION_TIME_CHANGED = "modification time changed"


@dataclass(frozen=True)
class CacheVerdict:
    observed_size: int
    observed_modification_time: float
    prior_observed_size: int | None
    prior_observed_modification_time: float | None
    verdict: str
    reason: str


def cache_verdict(observed, prior) -> CacheVerdict:
    """§1.2's verdict for one observed file. `prior` is P3's previous R4 row or None.

    Size is compared first so that a file whose size AND mtime both changed reports
    one deterministic reason — R4's `reason` is a single value and the SPEC supplies
    no compound one. Both observed and both prior values are on the record either way.
    """
    if prior is None:
        return CacheVerdict(observed.size, observed.mtime, None, None,
                            VERDICT_RECOMPUTE, REASON_FIRST_OBSERVATION)

    prior_size = prior["observed_size"]
    prior_mtime = prior["observed_modification_time"]
    if observed.size != prior_size:
        reason = REASON_SIZE_CHANGED
    elif observed.mtime != prior_mtime:
        # A difference test. Backwards is a change (§1.2: "instead of assuming that
        # time only moves forward"), which is what protects restores and migrations.
        reason = REASON_MODIFICATION_TIME_CHANGED
    else:
        return CacheVerdict(observed.size, observed.mtime, prior_size, prior_mtime,
                            VERDICT_REUSE, REASON_UNCHANGED)
    return CacheVerdict(observed.size, observed.mtime, prior_size, prior_mtime,
                        VERDICT_RECOMPUTE, reason)


STAT_CACHE_DDL = """
CREATE TABLE IF NOT EXISTS stat_cache_verdicts (
    verdict_id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id                      TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    file_id                          TEXT,     -- identity as resolved by P1; NULL when
                                               -- §8.5's metadata-safe form has no bytes
    observed_path                    TEXT NOT NULL,   -- mechanics: the pre-hash key
    observed_size                    INTEGER NOT NULL,
    observed_modification_time       REAL NOT NULL,
    prior_observed_size              INTEGER,
    prior_observed_modification_time REAL,
    verdict                          TEXT NOT NULL,
    reason                           TEXT NOT NULL,
    observed_at                      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS stat_cache_by_path
    ON stat_cache_verdicts (observed_path, verdict_id);
"""


def prior_observation(conn: sqlite3.Connection, path) -> sqlite3.Row | None:
    """P3's most recent R4 row for this path, while its file still lives there.

    The join on `files.current_path` is what stops a verdict left behind by a file
    that has since moved away from being reused for a different file that later
    appears at the old path.
    """
    return conn.execute(
        "SELECT v.* FROM stat_cache_verdicts v "
        "JOIN files f ON f.file_id = v.file_id AND f.current_path = v.observed_path "
        "WHERE v.observed_path = ? ORDER BY v.verdict_id DESC LIMIT 1",
        (str(Path(path)),),
    ).fetchone()


def record_cache_verdict(conn: sqlite3.Connection, scan_run_id: str, path,
                         file_id: str | None, verdict: CacheVerdict) -> int:
    conn.execute(
        "INSERT INTO stat_cache_verdicts "
        "(scan_run_id, file_id, observed_path, observed_size, "
        " observed_modification_time, prior_observed_size, "
        " prior_observed_modification_time, verdict, reason, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scan_run_id, file_id, str(Path(path)), verdict.observed_size,
         verdict.observed_modification_time, verdict.prior_observed_size,
         verdict.prior_observed_modification_time, verdict.verdict, verdict.reason,
         datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def cache_verdicts(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM stat_cache_verdicts WHERE scan_run_id = ? ORDER BY verdict_id",
        (scan_run_id,),
    ).fetchall()
```

- [ ] **Step 4: Publish `append_stat_observation` from `basic_record.py`**

Replace the trailing `append_event(... "stat observation" ...)` block inside
`record_basic_record` with a call to a published function, so the reuse path can
append one too:

```python
def append_stat_observation(conn: sqlite3.Connection, file_id: str, observed) -> None:
    """§8.2's `stat observation` — "size/timestamps observed; the §1.2 stat cache
    reads it". Appended on EVERY scan, reuse and recompute alike, so that a second
    scan adds one and leaves the earlier intact (Done-means 11)."""
    append_event(conn, **event_defaults(
        event_type="stat observation", file_id=file_id,
        content_hash=get_file(conn, file_id)["content_hash"],
        new_path=str(observed.path),
        explanation=json.dumps({"observed_size": observed.size,
                                "observed_modification_time": observed.mtime}),
    ))
```

and end `record_basic_record` with:

```python
    append_stat_observation(conn, file_id, observed)
    return file_id
```

- [ ] **Step 5: Take the verdict before hashing, in `scan.py`**

Replace the `ObservedFile` branch of `scan`:

```python
        elif isinstance(item, ObservedFile):
            if item.applies_to != APPLIES_TO_SCANNED_SOURCE:
                continue              # §1.1: roots are context, not corpus
            if item.dataless:
                record_dataless_detection(conn, scan_run_id, item.path)
                continue
            prior = prior_observation(conn, item.path)
            verdict = cache_verdict(item, prior)
            if verdict.verdict == VERDICT_REUSE:
                # §1.2: nothing is re-read. No hash, no observe_path, no files write.
                file_id = prior["file_id"]
                append_stat_observation(conn, file_id, item)
            else:
                file_id = record_basic_record(conn, item, mime_type_for=mime_type_for,
                                              scan_state=scan_state)
            record_cache_verdict(conn, scan_run_id, item.path, file_id, verdict)
```

with the matching imports:

```python
from scan_agent.basic_record import append_stat_observation, record_basic_record
from scan_agent.stat_cache import (
    VERDICT_REUSE, cache_verdict, prior_observation, record_cache_verdict,
)
```

`src/scan_agent/schema.py` in full at this point:

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL
from scan_agent.dataless import DATALESS_DDL
from scan_agent.deferrals import DEFERRALS_DDL
from scan_agent.stat_cache import STAT_CACHE_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(DATALESS_DDL)
    conn.executescript(DEFERRALS_DDL)
    conn.executescript(STAT_CACHE_DDL)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_stat_cache.py tests/p3/test_p3_basic_record.py -v`
Expected: PASS — 10 passed, 13 passed

- [ ] **Step 7: Commit**

```bash
git add src/scan_agent/stat_cache.py src/scan_agent/basic_record.py src/scan_agent/scan.py src/scan_agent/schema.py tests/p3/test_p3_stat_cache.py
git commit -m "feat(P3): R4 stat cache, disjunctive and a difference test, not newer-than"
```

---

### Task 12: `external modification detection`, authored by P3 (Done-means 18)

**Files:**
- Modify: `src/scan_agent/basic_record.py` — add `append_external_modification_detection`
- Modify: `src/scan_agent/scan.py` — append it on a recompute that had a prior
- Test: `tests/p3/test_p3_stat_cache.py` — extend

**Interfaces:**
- Consumes: `append_event`, `event_defaults`, `cache_verdict`.
- Produces: `append_external_modification_detection(conn, file_id, observed, verdict) -> None`.

**Done-means 18, quoted:** *"A file recorded in a prior scan whose size or modification time differs on re-scan yields an `external modification detection` event authored by P3, alongside its stat observation and its `recompute` verdict."* So the trigger is the **stat** difference, the author is P3, and all three records coexist.

**The type has two authors** (M8). P3's half is the re-scan (§1.2) and the session watch (`11` §4); P12's half is §8.3's staleness triggers and sync conflicts. Both rows survive and are separable by `subsystem`, which P1's own `test_two_parts_may_author_the_same_reserved_type` already proves from the other side.

**P1's `observe_path` may append a second one, and that is correct.** When the recompute finds *different bytes at the same path*, P1's plan appends its own `external modification detection` on the **prior** `file_id` to explain the supersede — authored by P3, because P3 is the `author` it was handed. So a content change produces two P3-authored rows: P3's, keyed on the stat difference that triggered the re-read, and P1's, keyed on the version being superseded. Both are true, both are append-only, and their `explanation` fields distinguish them. Neither is deleted, and the tests assert both. P1's plan flags its own reading as provisional (*"if P3's SPEC names a different reserved type for a re-scan content change, use that one"*) — P3's SPEC names this same type for the re-scan case, so the two agree, and the duplication is recorded as a seam worth review rather than optimized away.

**Content hash on the detection is the prior one.** The event says *the file we recorded as hash X has changed underneath us*; at detection time the new hash has not been taken yet, and §1.2 requires the detection **before** the recompute. Recording a hash P3 has not computed would be a fabrication.

**A first observation is not an external modification.** There is no prior record for the world to have changed underneath.

- [ ] **Step 1: Write the failing test**

Append to `tests/p3/test_p3_stat_cache.py`:

```python
def test_a_changed_stat_yields_a_p3_authored_external_modification_detection(
        ready, selection, corpus: Path):
    # Done-means 18.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    run = _scan(ready, selection)

    rows = ready.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()
    assert rows
    assert {r["subsystem"] for r in rows} == {"P3"}

    # alongside its stat observation and its recompute verdict
    assert cache_verdicts(ready, run)[0]["verdict"] == VERDICT_RECOMPUTE
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'stat observation'"
    ).fetchone()["c"] == 2


def test_the_detection_carries_the_hash_it_was_recorded_under(ready, selection, corpus: Path):
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    prior_hash = ready.execute("SELECT content_hash FROM files").fetchone()["content_hash"]
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    _scan(ready, selection)

    first = ready.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()[0]
    assert first["content_hash"] == prior_hash


def test_a_first_observation_yields_no_detection(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    _scan(ready, selection)
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'external modification detection'"
    ).fetchone()["c"] == 0


def test_an_unchanged_rescan_yields_no_detection(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    _scan(ready, selection)
    _scan(ready, selection)
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'external modification detection'"
    ).fetchone()["c"] == 0


def test_a_touch_alone_is_a_detection_even_with_identical_bytes(ready, selection, corpus: Path):
    # §1.2's rule is about size and mtime, not about bytes. A restore that resets
    # mtime is exactly the case the design names.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    _scan(ready, selection)
    rows = ready.execute(
        "SELECT subsystem FROM events WHERE event_type = 'external modification detection'"
    ).fetchall()
    assert [r["subsystem"] for r in rows] == ["P3"]


def test_the_earlier_detection_is_never_rewritten(ready, selection, corpus: Path):
    # SPEC, "What P3 never overwrites": a re-scan appends; it does not rewrite.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"two bytes longer")
    _scan(ready, selection)
    first = ready.execute(
        "SELECT event_id, explanation FROM events "
        "WHERE event_type = 'external modification detection' ORDER BY event_id"
    ).fetchall()[0]
    _rewrite_keeping_mtime(target, b"three bytes longer again")
    _scan(ready, selection)
    still = ready.execute(
        "SELECT event_id, explanation FROM events "
        "WHERE event_type = 'external modification detection' ORDER BY event_id"
    ).fetchall()[0]
    assert (still["event_id"], still["explanation"]) == \
           (first["event_id"], first["explanation"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_stat_cache.py -v`
Expected: FAIL — `test_a_changed_stat_yields_a_p3_authored_external_modification_detection` fails on `assert rows` (empty)

- [ ] **Step 3: Write the implementation**

Append to `src/scan_agent/basic_record.py`:

```python
def append_external_modification_detection(conn: sqlite3.Connection, file_id: str,
                                           observed, verdict) -> None:
    """§8.2's `external modification detection` — "a re-scan finds a recorded file's
    size or modification time changed underneath the product" (§1.2).

    P3 is one of this type's TWO authors (M8); P12's half is §8.3's staleness
    triggers and sync conflicts, and the two are separable by `subsystem`.

    `content_hash` is the hash the file was RECORDED under: the event says that the
    version P3 knows as X has changed on disk, and at detection time the new hash has
    not been taken — §1.2 requires the detection before the recompute. Recording a
    hash P3 has not computed would be a fabrication.
    """
    append_event(conn, **event_defaults(
        event_type="external modification detection", file_id=file_id,
        content_hash=get_file(conn, file_id)["content_hash"],
        old_path=str(observed.path), new_path=str(observed.path),
        explanation=json.dumps({
            "reason": verdict.reason,
            "prior_observed_size": verdict.prior_observed_size,
            "observed_size": verdict.observed_size,
            "prior_observed_modification_time": verdict.prior_observed_modification_time,
            "observed_modification_time": verdict.observed_modification_time,
        }),
    ))
```

In `scan.py`, append the detection before the recompute re-reads anything:

```python
            else:
                if prior is not None:
                    # Done-means 18: a recorded file whose size or modification time
                    # differs. Appended BEFORE the recompute, on the identity the
                    # file was recorded under.
                    append_external_modification_detection(
                        conn, prior["file_id"], item, verdict)
                file_id = record_basic_record(conn, item, mime_type_for=mime_type_for,
                                              scan_state=scan_state)
```

with the import extended:

```python
from scan_agent.basic_record import (
    append_external_modification_detection, append_stat_observation, record_basic_record,
)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_stat_cache.py -v`
Expected: PASS — 16 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/basic_record.py src/scan_agent/scan.py tests/p3/test_p3_stat_cache.py
git commit -m "feat(P3): external modification detection on re-scan, authored by P3"
```

---

### Task 13: R6 — directory inventory and the curation signal (Done-means 15, 16)

**Files:**
- Create: `src/scan_agent/inventory.py`
- Modify: `src/scan_agent/scan.py` — write the R6 row
- Modify: `src/scan_agent/schema.py` — add `INVENTORY_DDL`
- Test: `tests/p3/test_p3_inventory.py`

**Interfaces:**
- Consumes: `ObservedDirectory` from `walk`.
- Produces: `CURATION_CURATED`, `CURATION_INCIDENTAL`, `CURATION_UNDETERMINED`, `CURATION_SIGNAL_VALUES: tuple[str, str, str]`, `INVENTORY_DDL: str`, `curation_evidence(observed) -> dict`, `curation_signal(evidence) -> str`, `record_directory(conn, scan_run_id, observed) -> int`, `directory_inventory(conn, scan_run_id) -> list[sqlite3.Row]`.

**Why R6 exists.** §1.1 requires the engine to *"understand the current folder landscape and to show where a proposed branch could eventually live"*, and §5.10 requires the canvas to show *"where a current folder sits in the filesystem, how many files it contains"* and *"whether it appears to be curated or merely incidental"*. G9 puts the computation on P3, because the inputs are the directory inventory P3 already publishes.

**The threshold is Deferred and is not invented here.** SPEC Deferred: *"§1.1 gives one worked case — 'a lot of files such as JSON and other software material' — and no number, no ratio, and no list of which extensions read as software material… The threshold and the software-material extension list are hand-authored and are not guessed here."* So `curation_signal` returns `undetermined` for every directory, and `scan_agent` contains no ratio, no count comparison, and no extension list. The *record* is fully implementable now, which is the point: R6's counts, mix and evidence are observations, and `undetermined` is the honest value until a threshold is authored.

**`undetermined` is a real value, not a failure.** §8.6 requires the product to *"leave the file or group in review rather than guessing"*. A directory with no files reads `undetermined`, never `incidental`, and the tests assert exactly that.

**`curation_evidence` travels with the value** (§8.2's *"structured explanation or evidence reference"*): the counts, the extension mix, and every §1.1 project-root marker observed in that directory itself. R3 records the one marker that fired a verdict; R6 records all of them, so nothing is lost.

**It is P3's to compute, not to act on.** Every judgment that follows — preserve versus adopt, attach versus merge versus leave untouched — is P10's under §5.10, as is §5.10's prohibition on flattening, renaming or reorganizing. Nothing here enforces any of it, and Done-means 16 is the proof: the signal is computed from `ObservedDirectory`, which the traversal is finished with by the time it is yielded, so it is structurally incapable of changing an exclusion or a cache verdict.

**`applies_to` is on the row as mechanics**, not as an R6 field — the same way `observed_path` sits on R4 and `started_at` sits on P1's `scan_resource_usage`. R6 covers both sides of the scan, and a directory offered as both a source and a candidate root would otherwise produce two indistinguishable rows.

**A scan root's `parent_directory` is `NULL`**: it marks the top of the observed landscape. The full path is on `directory_path`, so §5.10's *"where a current folder sits in the filesystem"* loses nothing.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_inventory.py
import json
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.inventory import (
    CURATION_CURATED, CURATION_INCIDENTAL, CURATION_SIGNAL_VALUES,
    CURATION_UNDETERMINED, directory_inventory,
)
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


def _scan(conn, corpus, *, roots=()):
    selection = record_selection(conn, sources=[corpus], candidate_roots=list(roots),
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_every_non_excluded_directory_has_a_row(ready, corpus: Path):
    # Done-means 15, first half.
    (corpus / "Coursework" / "2026").mkdir(parents=True)
    (corpus / "Coursework" / "syllabus.pdf").write_bytes(b"x")
    (corpus / "node_modules").mkdir()
    run = _scan(ready, corpus)

    rows = {r["directory_path"]: r for r in directory_inventory(ready, run)}
    assert set(rows) == {
        str(corpus), str(corpus / "Coursework"), str(corpus / "Coursework" / "2026"),
    }
    assert rows[str(corpus)]["parent_directory"] is None
    assert rows[str(corpus / "Coursework")]["parent_directory"] == str(corpus)


def test_a_row_carries_5_10s_counts_and_the_mix(ready, corpus: Path):
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "a.pdf").write_bytes(b"x")
    (corpus / "Coursework" / "b.pdf").write_bytes(b"x")
    (corpus / "Coursework" / "c.json").write_bytes(b"{}")
    (corpus / "Coursework" / "nested").mkdir()
    run = _scan(ready, corpus)

    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "Coursework")][0]
    assert row["file_count"] == 3
    assert row["subdirectory_count"] == 1
    assert json.loads(row["extension_mix"]) == {".pdf": 2, ".json": 1}


def test_counts_and_mix_see_only_non_excluded_files(ready, corpus: Path):
    (corpus / "dist").mkdir()
    (corpus / "dist" / "bundle.js").write_bytes(b"x")
    (corpus / "a.pdf").write_bytes(b"x")
    run = _scan(ready, corpus)
    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus)][0]
    assert row["file_count"] == 1
    assert row["subdirectory_count"] == 0
    assert json.loads(row["extension_mix"]) == {".pdf": 1}


def test_every_signal_is_undetermined_and_none_is_silently_incidental(ready, corpus: Path):
    # Done-means 15, second half. The threshold is Deferred: §1.1 gives no number,
    # no ratio, and no list of which extensions read as software material.
    (corpus / "AIKonic Project").mkdir()
    for name in ("a.json", "b.json", "c.json", "d.py"):
        (corpus / "AIKonic Project" / name).write_bytes(b"{}")
    (corpus / "Empty").mkdir()
    run = _scan(ready, corpus)

    rows = directory_inventory(ready, run)
    assert rows
    assert {r["curation_signal"] for r in rows} == {CURATION_UNDETERMINED}
    assert CURATION_INCIDENTAL not in {r["curation_signal"] for r in rows}


def test_an_empty_directory_is_undetermined_not_incidental(ready, corpus: Path):
    # §8.6: "leave the file or group in review rather than guessing".
    (corpus / "Empty").mkdir()
    run = _scan(ready, corpus)
    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "Empty")][0]
    assert row["file_count"] == 0
    assert row["curation_signal"] == CURATION_UNDETERMINED


def test_the_evidence_travels_with_the_value(ready, corpus: Path):
    # §8.2's "structured explanation or evidence reference".
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    (corpus / "notes.md").write_bytes(b"x")
    run = _scan(ready, corpus)

    row = [r for r in directory_inventory(ready, run)
           if r["directory_path"] == str(corpus / "app")][0]
    evidence = json.loads(row["curation_evidence"])
    assert evidence["file_count"] == 0          # every child is an excluded descendant
    assert evidence["subdirectory_count"] == 0
    assert evidence["extension_mix"] == {}
    # R3 records the one marker that fired; R6 records all of them.
    assert evidence["project_root_markers"] == ["package.json", "go.mod"]


def test_the_three_signal_values_are_5_10s_three():
    assert CURATION_SIGNAL_VALUES == ("curated", "incidental", "undetermined")


def test_p3_holds_no_threshold_and_no_software_material_list():
    # SPEC Deferred. Guessing either would be P3 authoring what §1.1 does not supply.
    import scan_agent.inventory as module
    source = Path(module.__file__).read_text()
    # Tokens a threshold would have to introduce. The docstring quotes §1.1's
    # deferral in prose, so this checks code, not commentary.
    for forbidden in ("_THRESHOLD", "_RATIO", "PERCENT", "SOFTWARE_MATERIAL",
                      "if evidence[", "sum(", ">=", "<=", "0.5"):
        assert forbidden not in source, forbidden


def test_the_curation_signal_changes_nothing_else(tmp_path: Path, corpus: Path, monkeypatch):
    # Done-means 16: "the same corpus scanned with and without a curation threshold
    # authored yields identical files rows, identical exclusion verdicts, and
    # identical cache verdicts. The signal is an observation, not an exclusion rule."
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "a.pdf").write_bytes(b"a")
    (corpus / "node_modules").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "Cargo.toml").write_bytes(b"[package]")
    (corpus / "b.txt").write_bytes(b"b")

    def everything_but_the_signal(conn):
        return (
            [tuple(r) for r in conn.execute(
                "SELECT current_path, content_hash, observed_size, mime_type, "
                "scan_state, directory_position FROM files ORDER BY current_path")],
            [tuple(r) for r in conn.execute(
                "SELECT path, rule, rule_subject, applies_to FROM exclusion_verdicts "
                "ORDER BY path, applies_to")],
            [tuple(r) for r in conn.execute(
                "SELECT observed_path, verdict, reason FROM stat_cache_verdicts "
                "ORDER BY observed_path")],
        )

    def run_against(db_name):
        conn = open_database(tmp_path / db_name)
        create_schema(conn)
        create_scan_schema(conn)
        run = _scan(conn, corpus)
        return conn, run

    baseline_conn, _ = run_against("baseline.sqlite")

    import scan_agent.inventory as module
    monkeypatch.setattr(module, "curation_signal", lambda evidence: CURATION_CURATED)
    authored_conn, authored_run = run_against("authored.sqlite")

    assert everything_but_the_signal(baseline_conn) == \
           everything_but_the_signal(authored_conn)
    assert {r["curation_signal"] for r in directory_inventory(authored_conn, authored_run)} \
           == {CURATION_CURATED}
    baseline_conn.close()
    authored_conn.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_inventory.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.inventory'`

- [ ] **Step 3: Write `inventory.py`**

```python
# src/scan_agent/inventory.py
"""Contract out R6 — the directory inventory and its curation signal (§1.1, §5.10).

§1.1 requires the engine to "understand the current folder landscape and to show
where a proposed branch could eventually live". §5.10 requires the canvas to show
"where a current folder sits in the filesystem, how many files it contains" and
"whether it appears to be curated or merely incidental".

P3 COMPUTES this signal; it acts on nothing. Preserve versus adopt, attach versus
merge versus leave untouched, and §5.10's prohibition on flattening, renaming or
reorganizing are all P10's.
"""
from __future__ import annotations

import json
import sqlite3

#: §5.10's three values. `undetermined` is a real value, not a failure: §8.6 requires
#: the product to "leave the file or group in review rather than guessing".
CURATION_CURATED = "curated"
CURATION_INCIDENTAL = "incidental"
CURATION_UNDETERMINED = "undetermined"
CURATION_SIGNAL_VALUES: tuple[str, str, str] = (
    CURATION_CURATED, CURATION_INCIDENTAL, CURATION_UNDETERMINED,
)


def curation_evidence(observed) -> dict:
    """The observations behind the signal (§8.2's "structured explanation").

    R3 records the one project-root marker that fired a verdict; this records every
    marker observed in the directory itself, so nothing is lost.
    """
    return {
        "file_count": observed.file_count,
        "subdirectory_count": observed.subdirectory_count,
        "extension_mix": dict(observed.extension_mix),
        "project_root_markers": list(observed.project_root_markers),
    }


def curation_signal(evidence: dict) -> str:
    """§5.10's "curated or merely incidental".

    DEFERRED — and deliberately not guessed. §1.1 gives one worked case ("a lot of
    files such as JSON and other software material") and no number, no ratio, and no
    list of which extensions read as software material. Until that threshold is
    hand-authored, the honest value is `undetermined` for every directory, and a
    directory whose evidence supports neither reading is never rounded to
    `incidental`. The evidence above is complete now, so authoring the threshold is
    a change to this one function and to nothing else.
    """
    return CURATION_UNDETERMINED


INVENTORY_DDL = """
CREATE TABLE IF NOT EXISTS directory_inventory (
    inventory_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id        TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    directory_path     TEXT NOT NULL,
    parent_directory   TEXT,                -- NULL at a scan root: the top of the
                                            -- observed landscape
    file_count         INTEGER NOT NULL,    -- non-excluded, directly inside
    subdirectory_count INTEGER NOT NULL,    -- non-excluded, directly inside
    extension_mix      TEXT NOT NULL,       -- JSON: extension -> count
    curation_signal    TEXT NOT NULL,
    curation_evidence  TEXT NOT NULL,       -- JSON
    applies_to         TEXT NOT NULL        -- mechanics: which side of the scan
);
"""


def record_directory(conn: sqlite3.Connection, scan_run_id: str, observed) -> int:
    evidence = curation_evidence(observed)
    conn.execute(
        "INSERT INTO directory_inventory "
        "(scan_run_id, directory_path, parent_directory, file_count, "
        " subdirectory_count, extension_mix, curation_signal, curation_evidence, "
        " applies_to) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (scan_run_id, observed.directory_path, observed.parent_directory,
         observed.file_count, observed.subdirectory_count,
         json.dumps(dict(observed.extension_mix)), curation_signal(evidence),
         json.dumps(evidence), observed.applies_to),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def directory_inventory(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM directory_inventory WHERE scan_run_id = ? ORDER BY inventory_id",
        (scan_run_id,),
    ).fetchall()
```

- [ ] **Step 4: Write the R6 row in `scan.py`**

Replace the `ObservedDirectory` branch:

```python
        elif isinstance(item, ObservedDirectory):
            record_directory(conn, scan_run_id, item)
```

with the import:

```python
from scan_agent.inventory import record_directory
```

`src/scan_agent/schema.py` in full at this point:

```python
# src/scan_agent/schema.py
"""P3's tables. They live inside P1's single local SQLite database (§0); P1 owns the
handle, the transaction boundary, `files` and `events`, and P3 creates none of them.
"""
from __future__ import annotations

import sqlite3

from scan_agent.selection import SELECTION_DDL
from scan_agent.run import RUN_DDL
from scan_agent.exclusion import EXCLUSION_DDL
from scan_agent.dataless import DATALESS_DDL
from scan_agent.deferrals import DEFERRALS_DDL
from scan_agent.stat_cache import STAT_CACHE_DDL
from scan_agent.inventory import INVENTORY_DDL


def create_scan_schema(conn: sqlite3.Connection) -> None:
    """Create every P3-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(SELECTION_DDL)
    conn.executescript(RUN_DDL)
    conn.executescript(EXCLUSION_DDL)
    conn.executescript(DATALESS_DDL)
    conn.executescript(DEFERRALS_DDL)
    conn.executescript(STAT_CACHE_DDL)
    conn.executescript(INVENTORY_DDL)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_inventory.py -v`
Expected: PASS — 9 passed

- [ ] **Step 6: Commit**

```bash
git add src/scan_agent/inventory.py src/scan_agent/scan.py src/scan_agent/schema.py tests/p3/test_p3_inventory.py
git commit -m "feat(P3): R6 directory inventory, curation signal undetermined until authored"
```

---

### Task 14: R5 — the scan run summary and budget deferral (Done-means 13)

**Files:**
- Create: `src/scan_agent/summary.py`
- Test: `tests/p3/test_p3_summary.py`

**Interfaces:**
- Consumes: `exclusion_verdicts`, `cache_verdicts`, `scan_deferrals`, `DEFERRED_BUDGET`.
- Produces: `R5_COUNTERS: tuple[str, ...]` (five), `scan_run_summary(conn, scan_run_id) -> dict`.

**R5 is a projection, not a stored row.** The five counters are computed by reading the records they count, so a counter cannot disagree with the rows behind it. §8.6's example line — *"1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after the OCR limit; 34 files require model review; 18 files remain unreadable"* — draws **`indexed`** from P3, and the extraction, model-review and unreadable counts from P5 and P8. So R5 publishes P3's five and no sixth, and Task 17 asserts the key set is exactly five.

**The deferred counter is budget-only**, because the SPEC spells it *"files deferred (scan budget exhausted)"*. The other two deferral reasons (SPEC Q7, SPEC Q14) are readable from `scan_deferrals` and are deliberately not folded into an R5 counter the SPEC does not name.

**§8.6 on exhaustion, quoted:** *"the product should retain extracted evidence, mark the deferred stage, and leave the file or group in review rather than guessing"*, and *"Cost exhaustion must never turn into lower-quality automatic classification."* So P3 keeps everything already recorded, records the whole unreached frontier, relaxes no exclusion rule to finish faster, and samples nothing. The corpus cannot read as complete: the deferred rows are there.

**Dataless detections are not an R5 counter.** `11` §5 asks that the progress line be able to **name** these files; naming is what the `dataless_detections` record is for. Adding a sixth counter to R5 would be inventing a field, and folding them into an existing one would be exactly the *"folding them into OCR-capped or unreadable"* that §5 forbids.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_summary.py
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.deferrals import DEFERRED_BUDGET, scan_deferrals
from scan_agent.exclusion import RULE_LITERAL_DIRECTORY_NAME, RULE_PROJECT_ROOT_DESCENDANT
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.summary import R5_COUNTERS, scan_run_summary

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus, budget=NEVER):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=budget)


def test_the_summary_has_exactly_the_specs_five_counters():
    assert R5_COUNTERS == (
        "files_indexed", "paths_excluded_by_rule", "files_reused_from_stat_cache",
        "files_recomputed", "files_deferred",
    )


def test_the_summary_publishes_no_sixth_counter(ready, corpus: Path):
    # §8.6's example line draws `indexed` from P3; the extraction, model-review and
    # unreadable counts are P5's and P8's, and P3 does not invent a slot for them.
    (corpus / "a.txt").write_bytes(b"a")
    run = _scan(ready, corpus)
    assert tuple(scan_run_summary(ready, run)) == R5_COUNTERS


def test_a_first_scan_counts_indexed_and_recomputed(ready, corpus: Path):
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"x")
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert summary["files_indexed"] == 3
    assert summary["files_recomputed"] == 3
    assert summary["files_reused_from_stat_cache"] == 0
    assert summary["files_deferred"] == 0


def test_a_second_scan_counts_reuse(ready, corpus: Path):
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_bytes(b"x")
    _scan(ready, corpus)
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert summary["files_indexed"] == 2
    assert summary["files_reused_from_stat_cache"] == 2
    assert summary["files_recomputed"] == 0


def test_exclusions_are_counted_by_rule(ready, corpus: Path):
    (corpus / "node_modules").mkdir()
    (corpus / "dist").mkdir()
    (corpus / "app").mkdir()
    (corpus / "app" / "go.mod").write_bytes(b"module x")
    (corpus / "app" / "main.go").write_bytes(b"package main")
    run = _scan(ready, corpus)
    by_rule = scan_run_summary(ready, run)["paths_excluded_by_rule"]
    assert by_rule[RULE_LITERAL_DIRECTORY_NAME] == 2
    assert by_rule[RULE_PROJECT_ROOT_DESCENDANT] == 2


def test_budget_exhaustion_is_counted_and_the_corpus_cannot_read_as_complete(
        ready, corpus: Path):
    # Done-means 13.
    for name in ("a.txt", "b.txt", "c.txt", "d.txt", "e.txt"):
        (corpus / name).write_bytes(b"x")
    (corpus / "sub").mkdir()
    (corpus / "sub" / "f.txt").write_bytes(b"x")

    calls = {"n": 0}

    def after_two():
        calls["n"] += 1
        return calls["n"] > 2

    run = _scan(ready, corpus, budget=after_two)
    summary = scan_run_summary(ready, run)

    assert summary["files_deferred"] > 0
    assert summary["files_indexed"] < 6
    # everything already recorded is retained (§8.6)
    assert summary["files_indexed"] > 0
    # and the unreached frontier is on the record, directories included
    deferred = scan_deferrals(ready, run)
    assert {d["reason"] for d in deferred} == {DEFERRED_BUDGET}
    assert any(d["is_directory"] for d in deferred)


def test_exhaustion_relaxes_no_exclusion_rule(ready, corpus: Path):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." P3 does not finish faster by letting node_modules through.
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "buried.txt").write_bytes(b"x")
    (corpus / "a.txt").write_bytes(b"x")

    calls = {"n": 0}

    def immediately():
        calls["n"] += 1
        return calls["n"] > 1

    run = _scan(ready, corpus, budget=immediately)
    paths = [r["current_path"] for r in ready.execute("SELECT current_path FROM files")]
    assert not any("node_modules" in p for p in paths)
    assert scan_run_summary(ready, run)["files_deferred"] >= 0


def test_a_dataless_detection_is_not_an_r5_counter(ready, corpus: Path, monkeypatch):
    # 11 §5: the progress line must be able to NAME these files rather than folding
    # them into another count. Naming is `dataless_detections`, not an R5 slot.
    import scan_agent.corpus_source as module
    (corpus / "cloud.pdf").write_bytes(b"x")
    real_entries = module.FilesystemCorpusSource.entries

    def entries(self, directory):
        from dataclasses import replace
        return [replace(e, dataless=e.name == "cloud.pdf")
                for e in real_entries(self, directory)]

    monkeypatch.setattr(module.FilesystemCorpusSource, "entries", entries)
    run = _scan(ready, corpus)
    summary = scan_run_summary(ready, run)
    assert tuple(summary) == R5_COUNTERS
    assert summary["files_indexed"] == 0
    assert summary["files_deferred"] == 0
    assert ready.execute(
        "SELECT count(*) c FROM dataless_detections WHERE scan_run_id = ?", (run,)
    ).fetchone()["c"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_summary.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.summary'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/summary.py
"""Contract out R5 — the §8.6 scan-run summary.

§8.6's example line: "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs
deferred after the OCR limit; 34 files require model review; 18 files remain
unreadable." The `indexed` count is P3's; the extraction, model-review and unreadable
counts are P5's and P8's, and P3 publishes no slot for them.

R5 is a PROJECTION over the records it counts, not a stored row, so a counter cannot
drift from the rows behind it.
"""
from __future__ import annotations

import sqlite3

from scan_agent.deferrals import DEFERRED_BUDGET

#: The SPEC's five, in the SPEC's order. There is no sixth.
R5_COUNTERS: tuple[str, ...] = (
    "files_indexed", "paths_excluded_by_rule", "files_reused_from_stat_cache",
    "files_recomputed", "files_deferred",
)


def scan_run_summary(conn: sqlite3.Connection, scan_run_id: str) -> dict:
    """R5 for one run."""
    indexed = conn.execute(
        "SELECT count(DISTINCT file_id) AS c FROM stat_cache_verdicts "
        "WHERE scan_run_id = ? AND file_id IS NOT NULL", (scan_run_id,)
    ).fetchone()["c"]

    by_rule = {
        row["rule"]: row["c"] for row in conn.execute(
            "SELECT rule, count(*) AS c FROM exclusion_verdicts WHERE scan_run_id = ? "
            "GROUP BY rule", (scan_run_id,)
        )
    }

    verdicts = {
        row["verdict"]: row["c"] for row in conn.execute(
            "SELECT verdict, count(*) AS c FROM stat_cache_verdicts "
            "WHERE scan_run_id = ? GROUP BY verdict", (scan_run_id,)
        )
    }

    # "files deferred (scan budget exhausted)" — the SPEC's spelling, so the counter
    # filters on the budget reason. The other deferral reasons name open questions
    # (Q7, Q14) and are readable from `scan_deferrals` without an invented counter.
    deferred = conn.execute(
        "SELECT count(*) AS c FROM scan_deferrals "
        "WHERE scan_run_id = ? AND reason = ? AND is_directory = 0",
        (scan_run_id, DEFERRED_BUDGET),
    ).fetchone()["c"]

    return {
        "files_indexed": indexed,
        "paths_excluded_by_rule": by_rule,
        "files_reused_from_stat_cache": verdicts.get("reuse", 0),
        "files_recomputed": verdicts.get("recompute", 0),
        "files_deferred": deferred,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_summary.py -v`
Expected: PASS — 8 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/summary.py tests/p3/test_p3_summary.py
git commit -m "feat(P3): R5 scan run summary, five counters, deferral visible not silent"
```

---

### Task 15: Replay — the same verdicts from a frozen corpus (Done-means 14)

**Files:**
- Create: `src/scan_agent/replay.py`
- Test: `tests/p3/test_p3_replay.py`

**Interfaces:**
- Consumes: `CorpusSource`, `SnapshotCorpusSource`, `walk`, `record_exclusion`, `record_deferral`, `record_directory`, `cache_verdict`, `record_cache_verdict`, `require_access`, `start_scan_run` / `finish_scan_run`.
- Produces: `RecordingCorpusSource`, `CORPUS_FORM_SNAPSHOT`, `CORPUS_FORM_METADATA_SAFE`, `snapshot_from(conn, recording, *, corpus_form) -> dict`, `replay(conn, selection_id, *, snapshot, budget_exhausted) -> str`, `boundary_fingerprint(conn, scan_run_id) -> dict`.

**What §8.5 asks of P3.** SPEC Contract in: the bundle contains *"a frozen corpus snapshot or a metadata-safe representation of one"*, and *"P3 must therefore be runnable against a bundle-backed corpus source as well as a live filesystem, with identical exclusion and cache verdicts."* SPEC Serialization adds: *"R1–R4 and R6 must serialize into and re-assert from a P2 replay bundle (§8.5), `curation_signal` included — a replay that reproduces the corpus but not its curation reading would not reproduce P10's canvas."*

**What is serialized is the listings, not the results.** The exclusion rules must **re-fire** on replay rather than be replayed as conclusions, or the replay would prove nothing. So `RecordingCorpusSource` wraps a source and records every listing it served — including the excluded entries as they appeared in their parents' listings, and *not* including the contents of pruned directories, which were never listed and must stay unlisted for the pruning to reproduce.

**P2 owns the envelope; this is the payload.** The snapshot uses P2's field spellings where P2 publishes one — `corpus_form` with values `snapshot | metadata_safe`, and `content_hash` per indexed file, which §8.5's bundle requires and P2's `bundle_file_entry` carries. P2 wraps this; `replay.py` imports no P2 code, so P3 stays buildable against P1 alone.

**A replay writes no `files` row, and that is §8.5's own cost.** A `metadata_safe` corpus has no bytes, so no content hash can be computed and P1's content-hash identity is unavailable; P1 also publishes no entry point that records a file from a *supplied* hash. Done-means 14 asks for identical **exclusion verdicts**, **cache verdicts** and **`curation_signal` values**, and all three are reproduced. The gap is recorded, not papered over, and reported.

**A replay runs against a fresh database.** `11-ops-runtime.md` §3: *"P2 replay is not a session; it is a harness run."* In a fresh database there is no prior observation, so every cache verdict is `first observation` / `recompute` — which is exactly what the original **first** scan produced, and is what the comparison asserts.

**`boundary_fingerprint` is the comparison surface**: the three things Done-means 14 names, in a form two runs can be compared on directly.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_replay.py
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database

from scan_agent.corpus_source import FilesystemCorpusSource, SnapshotCorpusSource
from scan_agent.inventory import CURATION_UNDETERMINED
from scan_agent.replay import (
    CORPUS_FORM_METADATA_SAFE, CORPUS_FORM_SNAPSHOT, RecordingCorpusSource,
    boundary_fingerprint, replay, snapshot_from,
)
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


def _fresh(tmp_path: Path, name: str):
    conn = open_database(tmp_path / name)
    create_schema(conn)
    create_scan_schema(conn)
    return conn


@pytest.fixture()
def populated(corpus: Path):
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "syllabus.pdf").write_bytes(b"%PDF fixture")
    (corpus / "Coursework" / "notes.md").write_bytes(b"notes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "buried.js").write_bytes(b"x")
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "index.js").write_bytes(b"x")
    (corpus / "loose.txt").write_bytes(b"loose")
    return corpus


def _live_scan(conn, corpus):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    recording = RecordingCorpusSource(FilesystemCorpusSource())
    run = scan(conn, selection, source=recording, mime_type_for=fixture_mime,
               scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    return selection, run, recording


def test_a_replay_reproduces_exclusion_cache_and_curation_verdicts(
        tmp_path: Path, populated: Path):
    # Done-means 14.
    live = _fresh(tmp_path, "live.sqlite")
    _, live_run, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_METADATA_SAFE)

    harness = _fresh(tmp_path, "harness.sqlite")
    selection = record_selection(harness, sources=[populated], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    replay_run = replay(harness, selection, snapshot=snapshot, budget_exhausted=NEVER)

    assert boundary_fingerprint(live, live_run) == \
           boundary_fingerprint(harness, replay_run)
    live.close()
    harness.close()


def test_a_replay_touches_no_filesystem(tmp_path: Path, populated: Path):
    # §8.5: evaluation "without touching a live filesystem".
    live = _fresh(tmp_path, "live.sqlite")
    _, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_METADATA_SAFE)
    live.close()

    import shutil
    shutil.rmtree(populated)          # the corpus is gone

    harness = _fresh(tmp_path, "harness.sqlite")
    selection = record_selection(harness, sources=[populated], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    run = replay(harness, selection, snapshot=snapshot, budget_exhausted=NEVER)
    assert boundary_fingerprint(harness, run)["exclusions"]
    harness.close()


def test_the_snapshot_carries_the_listings_not_the_conclusions(
        tmp_path: Path, populated: Path):
    # The rules must re-fire on replay. The excluded directory is in the listing of
    # its parent; the contents it pruned were never listed and stay unlisted.
    live = _fresh(tmp_path, "live.sqlite")
    _, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_METADATA_SAFE)
    paths = {entry["path"] for entry in snapshot["entries"]}
    assert str(populated / "node_modules") in paths
    assert str(populated / "node_modules" / "buried.js") not in paths
    assert "rule" not in str(snapshot["entries"][0])
    live.close()


def test_the_snapshot_carries_content_hashes_for_p2s_envelope(
        tmp_path: Path, populated: Path):
    # §8.5's bundle contains "content hashes". P2 wraps this payload; P3's own
    # replay does not consume them, because P1 publishes no entry point that records
    # a file from a supplied hash.
    live = _fresh(tmp_path, "live.sqlite")
    _, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_SNAPSHOT)
    hashed = {e["path"]: e["content_hash"] for e in snapshot["entries"]
              if e["content_hash"] is not None}
    assert str(populated / "loose.txt") in hashed
    assert len(hashed[str(populated / "loose.txt")]) == 64
    assert snapshot["hash_algorithm"]
    live.close()


def test_a_metadata_safe_replay_writes_no_files_row(tmp_path: Path, populated: Path):
    # §8.5's own cost: no bytes, so no content-hash identity. Recorded, not hidden.
    live = _fresh(tmp_path, "live.sqlite")
    _, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_METADATA_SAFE)
    harness = _fresh(tmp_path, "harness.sqlite")
    selection = record_selection(harness, sources=[populated], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    run = replay(harness, selection, snapshot=snapshot, budget_exhausted=NEVER)
    assert harness.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    assert harness.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
    verdicts = harness.execute(
        "SELECT file_id FROM stat_cache_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchall()
    assert verdicts and all(v["file_id"] is None for v in verdicts)
    live.close()
    harness.close()


def test_the_replay_reproduces_the_curation_reading(tmp_path: Path, populated: Path):
    # SPEC Serialization: "a replay that reproduces the corpus but not its curation
    # reading would not reproduce P10's canvas."
    live = _fresh(tmp_path, "live.sqlite")
    _, live_run, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, corpus_form=CORPUS_FORM_METADATA_SAFE)
    harness = _fresh(tmp_path, "harness.sqlite")
    selection = record_selection(harness, sources=[populated], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    run = replay(harness, selection, snapshot=snapshot, budget_exhausted=NEVER)

    live_signals = boundary_fingerprint(live, live_run)["curation"]
    replay_signals = boundary_fingerprint(harness, run)["curation"]
    assert live_signals == replay_signals
    assert set(dict(replay_signals).values()) == {CURATION_UNDETERMINED}
    live.close()
    harness.close()


def test_replay_imports_no_p2_code():
    import scan_agent.replay as module
    source = Path(module.__file__).read_text()
    assert "eval_agent" not in source and "bundle_manifest" not in source
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_replay.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.replay'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/replay.py
"""§8.5 — serialize a scan's corpus and re-assert it without a live filesystem.

SPEC Contract in (from P2): "P3 must therefore be runnable against a bundle-backed
corpus source as well as a live filesystem, with identical exclusion and cache
verdicts." SPEC Serialization: "R1–R4 and R6 must serialize into and re-assert from a
P2 replay bundle (§8.5), `curation_signal` included."

P2 owns the bundle ENVELOPE. This module defines the payload P3 can re-assert from,
using P2's spellings where P2 publishes one, and imports no P2 code.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable

from database_agent.identity import HASH_ALGORITHM

from scan_agent.corpus_source import CorpusSource, SnapshotCorpusSource
from scan_agent.deferrals import record_deferral
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE, ExclusionVerdict, record_exclusion
from scan_agent.inventory import record_directory
from scan_agent.run import finish_scan_run, start_scan_run
from scan_agent.selection import selection_candidate_roots, selection_sources
from scan_agent.stat_cache import cache_verdict, prior_observation, record_cache_verdict
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk

#: §8.5's two corpus forms, P2's spellings.
CORPUS_FORM_SNAPSHOT = "snapshot"
CORPUS_FORM_METADATA_SAFE = "metadata_safe"


class RecordingCorpusSource:
    """Wraps a CorpusSource and remembers every listing it served.

    The LISTINGS are what a replay needs, not the verdicts: the §1.1 rules have to
    re-fire on replay or the replay proves nothing. The contents of a pruned
    directory were never listed and stay unlisted, which is what reproduces the
    pruning rather than replaying it as a conclusion.
    """

    def __init__(self, inner: CorpusSource):
        self._inner = inner
        self.has_bytes = inner.has_bytes
        self.listings: dict[str, list] = {}

    def entries(self, directory) -> list:
        served = self._inner.entries(directory)
        self.listings[str(directory)] = served
        return served


def snapshot_from(conn: sqlite3.Connection, recording: RecordingCorpusSource, *,
                  corpus_form: str) -> dict:
    """The re-assertable payload for one recorded scan.

    `content_hash` is carried for §8.5's bundle ("content hashes") and P2's
    `bundle_file_entry`; P3's own replay does not consume it, because P1 publishes no
    entry point that records a file from a supplied hash.
    """
    recorded_hashes = {
        row["current_path"]: row["content_hash"]
        for row in conn.execute("SELECT current_path, content_hash FROM files")
    }
    entries = []
    for directory, served in recording.listings.items():
        for entry in served:
            entries.append({
                "parent": directory,
                "path": entry.path,
                "name": entry.name,
                "kind": entry.kind,
                "size": entry.size,
                "mtime": entry.mtime,
                "dataless": entry.dataless,
                "content_hash": recorded_hashes.get(entry.path),
            })
    return {
        "corpus_form": corpus_form,
        "hash_algorithm": HASH_ALGORITHM,
        "listed_directories": sorted(recording.listings),
        "entries": entries,
    }


def replay(conn: sqlite3.Connection, selection_id: str, *,
           snapshot: dict,
           budget_exhausted: Callable[[], bool]) -> str:
    """Re-assert a scan's corpus boundary, cache verdicts and inventory (§8.5).

    Writes NO `files` row and appends NO event: a metadata-safe corpus has no bytes,
    so P1's content-hash identity is unavailable. Done-means 14 asks for identical
    exclusion verdicts, identical cache verdicts and identical curation signals, and
    those are what this reproduces.
    """
    source = SnapshotCorpusSource(snapshot)
    sources = selection_sources(conn, selection_id)
    candidate_roots = selection_candidate_roots(conn, selection_id)
    scan_run_id = start_scan_run(conn, selection_id)

    for item in walk(source, sources=sources, candidate_roots=candidate_roots,
                     budget_exhausted=budget_exhausted):
        if isinstance(item, ExclusionVerdict):
            record_exclusion(conn, scan_run_id, item)
        elif isinstance(item, Deferred):
            record_deferral(conn, scan_run_id, item)
        elif isinstance(item, ObservedDirectory):
            record_directory(conn, scan_run_id, item)
        elif isinstance(item, ObservedFile):
            if item.applies_to != APPLIES_TO_SCANNED_SOURCE or item.dataless:
                continue
            verdict = cache_verdict(item, prior_observation(conn, item.path))
            record_cache_verdict(conn, scan_run_id, item.path, None, verdict)
    finish_scan_run(conn, scan_run_id)
    return scan_run_id


def boundary_fingerprint(conn: sqlite3.Connection, scan_run_id: str) -> dict:
    """The three things Done-means 14 requires to be identical, comparably shaped."""
    return {
        "exclusions": [
            (row["path"], row["rule"], row["rule_subject"], row["applies_to"])
            for row in conn.execute(
                "SELECT path, rule, rule_subject, applies_to FROM exclusion_verdicts "
                "WHERE scan_run_id = ? ORDER BY path, applies_to", (scan_run_id,))
        ],
        "cache": [
            (row["observed_path"], row["verdict"], row["reason"])
            for row in conn.execute(
                "SELECT observed_path, verdict, reason FROM stat_cache_verdicts "
                "WHERE scan_run_id = ? ORDER BY observed_path", (scan_run_id,))
        ],
        "curation": [
            (row["directory_path"], row["curation_signal"])
            for row in conn.execute(
                "SELECT directory_path, curation_signal FROM directory_inventory "
                "WHERE scan_run_id = ? ORDER BY directory_path", (scan_run_id,))
        ],
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_replay.py -v`
Expected: PASS — 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/replay.py tests/p3/test_p3_replay.py
git commit -m "feat(P3): replay a recorded corpus, same exclusion, cache and curation verdicts"
```

---

### Task 16: The session watch (`11-ops-runtime.md` §4)

**Files:**
- Create: `src/scan_agent/watch.py`
- Test: `tests/p3/test_p3_watch.py`

**Interfaces:**
- Consumes: `append_external_modification_detection`-style authorship, `prior_observation`, `cache_verdict`, `FilesystemCorpusSource`.
- Produces: `CHANGE_MODIFIED`, `CHANGE_APPEARED`, `CHANGE_DISAPPEARED`, `SessionWatch` with `open(paths)`, `notify(path)`, `close()`, and `poll()`.

**Binding [`../../11-ops-runtime.md`](../../11-ops-runtime.md) §4, quoted:** *"P3 remains scan-plus-stat-cache. **While a session is open**, P3 also watches the selected roots (FSEvents / `DispatchSource`) and authors `external modification detection` for any watched path whose size or mtime changes, which appears, or which disappears. There is **no background daemon** in v1. Closing the app ends the watch. … A detection is not a rescan by itself. P3 may re-stat the one path; it does not restart the corpus scan unless the user asks."*

**The platform event source is not built here, and is not faked either.** FSEvents / `DispatchSource` need a macOS API binding that the standard library does not provide, and this plan adds no third-party runtime dependency. So the watch is built as the thing the platform adapter calls: `SessionWatch.notify(path)` is the entry point an FSEvents callback invokes, and `poll()` is a stdlib-only driver that re-stats the watched paths and calls `notify` for each difference. Every semantic rule §4 states — the four rules below — is implemented and tested against `notify`. The FSEvents adapter is a known gap; nothing about it is stubbed, mocked or pretended.

Four rules, each tested:

1. **Only while a session is open.** `notify` on a closed watch does nothing and appends no event. There is no timer, no thread, and no process that outlives `close()` — §4: *"There is no background daemon in v1."*
2. **Change, appearance and disappearance all author `external modification detection`.** §4 names all three. **Conflict, recorded:** SPEC Q14 still marks it *"unsettled"* whether a disappearance is that same event; `11` is binding and answers it for the watch, so this plan follows `11` and reports the discrepancy. Q14's other half — what happens to a `files` row whose path no longer exists — is **not** answered: the watch appends the detection and modifies no `files` row, and a test asserts the row is untouched.
3. **A detection is not a rescan.** `notify` writes no `files` row, no exclusion verdict, no inventory row and no scan run. It re-stats the one path and stops.
4. **P3 is the author.** Every row names `subsystem = "P3"`, and this is P3's half of the type M8 gives two authors.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_watch.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.watch import (
    CHANGE_APPEARED, CHANGE_DISAPPEARED, CHANGE_MODIFIED, SessionWatch,
)

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def scanned(conn, corpus: Path):
    create_schema(conn)
    create_scan_schema(conn)
    (corpus / "a.txt").write_bytes(b"one")
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    scan(conn, selection, source=FilesystemCorpusSource(), mime_type_for=fixture_mime,
         scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    return conn


def _detections(conn):
    return conn.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()


def test_a_change_while_a_session_is_open_is_detected(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    target = corpus / "a.txt"
    target.write_bytes(b"one plus more")
    watch.notify(target)

    rows = _detections(scanned)
    assert len(rows) == 1
    assert rows[0]["subsystem"] == "P3"
    assert CHANGE_MODIFIED in rows[0]["explanation"]
    watch.close()


def test_an_appearance_is_detected(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    fresh = corpus / "brand-new.txt"
    fresh.write_bytes(b"new")
    watch.notify(fresh)
    rows = _detections(scanned)
    assert len(rows) == 1
    assert CHANGE_APPEARED in rows[0]["explanation"]
    assert rows[0]["file_id"] is None      # no record for it yet; §8.2 allows empty
    watch.close()


def test_a_disappearance_is_detected_and_the_record_is_untouched(scanned, corpus: Path):
    # 11 §4 names disappearance. SPEC Q14 still marks it unsettled and asks what
    # happens to a `files` row whose path no longer exists — that half is NOT
    # answered here: the row is not modified, moved, or removed.
    before = scanned.execute("SELECT * FROM files").fetchone()
    watch = SessionWatch(scanned)
    watch.open([corpus])
    (corpus / "a.txt").unlink()
    watch.notify(corpus / "a.txt")

    rows = _detections(scanned)
    assert len(rows) == 1
    assert CHANGE_DISAPPEARED in rows[0]["explanation"]
    after = scanned.execute("SELECT * FROM files").fetchone()
    assert tuple(after) == tuple(before)
    watch.close()


def test_nothing_is_watched_before_open_or_after_close(scanned, corpus: Path):
    # 11 §4: "There is no background daemon in v1. Closing the app ends the watch."
    watch = SessionWatch(scanned)
    target = corpus / "a.txt"
    target.write_bytes(b"changed before open")
    watch.notify(target)
    assert _detections(scanned) == []

    watch.open([corpus])
    watch.close()
    target.write_bytes(b"changed after close")
    watch.notify(target)
    assert _detections(scanned) == []


def test_a_path_outside_the_watched_roots_is_ignored(scanned, corpus: Path, tmp_path: Path):
    outside = tmp_path / "elsewhere.txt"
    outside.write_bytes(b"x")
    watch = SessionWatch(scanned)
    watch.open([corpus])
    watch.notify(outside)
    assert _detections(scanned) == []
    watch.close()


def test_an_unchanged_path_produces_no_detection(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    watch.notify(corpus / "a.txt")
    assert _detections(scanned) == []
    watch.close()


def test_a_detection_is_not_a_rescan(scanned, corpus: Path):
    # 11 §4: "A detection is not a rescan by itself… it does not restart the corpus
    # scan unless the user asks."
    def counts():
        return tuple(
            scanned.execute(f"SELECT count(*) c FROM {table}").fetchone()["c"]
            for table in ("scan_runs", "files", "exclusion_verdicts",
                          "directory_inventory", "stat_cache_verdicts")
        )

    before = counts()
    watch = SessionWatch(scanned)
    watch.open([corpus])
    (corpus / "a.txt").write_bytes(b"one plus more")
    (corpus / "node_modules").mkdir()          # a new directory appears mid-session
    watch.notify(corpus / "a.txt")

    assert counts() == before                  # nothing rescanned, nothing re-indexed
    assert len(_detections(scanned)) == 1      # only the detection
    watch.close()


def test_poll_drives_the_watch_without_a_platform_binding(scanned, corpus: Path):
    # FSEvents / DispatchSource need a macOS API binding the standard library does
    # not supply. `poll` is the stdlib driver; the platform adapter calls `notify`.
    watch = SessionWatch(scanned)
    watch.open([corpus])
    target = corpus / "a.txt"
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    watch.poll()
    rows = _detections(scanned)
    assert len(rows) == 1
    assert rows[0]["subsystem"] == "P3"
    watch.close()


def test_the_module_starts_no_thread_and_no_timer():
    # "There is no background daemon in v1."
    import scan_agent.watch as module
    source = Path(module.__file__).read_text()
    # `daemon` is deliberately absent from this list: the module docstring quotes
    # §4's "There is no background daemon in v1".
    for forbidden in ("threading", "Thread", "Timer", "asyncio", "multiprocessing",
                      "signal.", "atexit"):
        assert forbidden not in source, forbidden
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_watch.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'scan_agent.watch'`

- [ ] **Step 3: Write the implementation**

```python
# src/scan_agent/watch.py
"""11-ops-runtime.md §4 — the live observation P3 does while a session is open.

"P3 remains scan-plus-stat-cache. While a session is open, P3 also watches the
selected roots (FSEvents / DispatchSource) and authors `external modification
detection` for any watched path whose size or mtime changes, which appears, or which
disappears. There is no background daemon in v1. Closing the app ends the watch. …
A detection is not a rescan by itself."

The PLATFORM event source is not built here: FSEvents / DispatchSource need a macOS
API binding the standard library does not supply, and this part adds no third-party
dependency. `notify` is the entry point such an adapter calls, and `poll` is a
stdlib driver for it. Everything §4 specifies about WHAT a detection means lives
here and is tested; only the platform callback is missing, and it is not faked.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from database_agent.events import append_event

from scan_agent.authorship import event_defaults

#: The three §4 names. Recorded in the event's structured explanation (§8.2).
CHANGE_MODIFIED = "size or modification time changed"
CHANGE_APPEARED = "appeared"
CHANGE_DISAPPEARED = "disappeared"


class SessionWatch:
    """Open for one session (11 §3). Closing it ends the watch; nothing survives."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._roots: tuple[Path, ...] = ()
        self._observed: dict[str, tuple[int, float] | None] = {}
        self._open = False

    def open(self, roots) -> None:
        """Begin watching the selected roots and record their current stat."""
        self._roots = tuple(Path(root) for root in roots)
        self._observed = {}
        for root in self._roots:
            for current, _, names in os.walk(root):
                for name in names:
                    path = Path(current) / name
                    self._observed[str(path)] = self._stat(path)
        self._open = True

    def close(self) -> None:
        """11 §4: "Closing the app ends the watch." No daemon, no thread, no timer."""
        self._open = False
        self._roots = ()
        self._observed = {}

    def poll(self) -> None:
        """Re-stat the watched paths and notify each difference.

        The stdlib driver. A platform adapter (FSEvents / DispatchSource) calls
        `notify` directly instead, and is not built here.
        """
        if not self._open:
            return
        known = set(self._observed)
        live: set[str] = set()
        for root in self._roots:
            for current, _, names in os.walk(root):
                for name in names:
                    live.add(str(Path(current) / name))
        for path in sorted(known | live):
            self.notify(Path(path))

    def notify(self, path) -> None:
        """One watched path may have changed. Authors the detection when it did.

        A detection is NOT a rescan (11 §4): this re-stats the one path, writes no
        `files` row, and starts no scan run.
        """
        if not self._open:
            return
        path = Path(path)
        if not any(path == root or root in path.parents for root in self._roots):
            return

        before = self._observed.get(str(path))
        after = self._stat(path)
        if before == after:
            return

        if before is None:
            change = CHANGE_APPEARED
        elif after is None:
            change = CHANGE_DISAPPEARED
        else:
            change = CHANGE_MODIFIED
        self._observed[str(path)] = after

        row = self._conn.execute(
            "SELECT file_id, content_hash FROM files WHERE current_path = ? "
            "ORDER BY rowid DESC LIMIT 1", (str(path),)
        ).fetchone()

        # SPEC Q14's other half stays OPEN: what happens to a `files` row whose path
        # no longer exists is not decided here, so no row is modified or removed.
        append_event(self._conn, **event_defaults(
            event_type="external modification detection",
            file_id=row["file_id"] if row else None,
            content_hash=row["content_hash"] if row else None,
            old_path=str(path), new_path=str(path),
            explanation=json.dumps({
                "change": change,
                "prior_observed": list(before) if before else None,
                "observed": list(after) if after else None,
                "source": "session watch (11-ops-runtime.md §4)",
            }),
        ))

    @staticmethod
    def _stat(path: Path) -> tuple[int, float] | None:
        try:
            result = os.stat(path, follow_symlinks=False)
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            return None
        return (result.st_size, result.st_mtime)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_watch.py -v`
Expected: PASS — 9 passed

- [ ] **Step 5: Commit**

```bash
git add src/scan_agent/watch.py tests/p3/test_p3_watch.py
git commit -m "feat(P3): session watch, detections while open, no daemon, not a rescan"
```

---

### Task 17: The no-invention guard (Done-means 17, and every open question held open)

**Files:**
- Test: `tests/p3/test_p3_no_invention.py`

**Interfaces:**
- Consumes: every module above.
- Produces: the standing guard the rest of the build must keep green.

**Two obligations, both negative.**

**Done-means 17 — the ten fields are computed once, by P3.** *"The ten §1.2 fields are computed exactly once per file version, by P3; a fixture in which another part re-derives one of them fails."* O5's stated reason is drift: *"A second derivation of any of them — including a second MIME-type determination or a second hash — is a contract violation, not an optimization, because the two would drift and §3.4's cache key is built on the hash."* This is tested two ways: a **drift test** asserting the values P3 observed are exactly the values on the row, and a **source guard** asserting `scan_agent` contains no second hash and no second MIME determination.

> **Divergence recorded, not fixed here.** P1's Contract in says P3 hands P1 *"a path, its stat result (size, timestamps), its bytes to hash, and the §1.2 per-file fields"*, but P1's **plan** has `record_file` call `path.stat()` and `hash_file(path, ...)` itself, deriving filename, normalized filename, extension, size, timestamps and content hash from the path rather than storing what P3 observed. That is P1 re-deriving six of P3's ten. P3 owns none of P1's files and does not change its signature; the drift test below is what catches it if the two ever disagree, and the divergence is reported for P1 to resolve. Related: P1's `record_file` normalizes with `unicodedata.normalize("NFC", ...)`, which **answers P3 OQ1** (*"`normalized filename` is undefined… Unicode form, case folding, whitespace and separator collapse, extension retention, and diacritic handling are all unstated"*) by picking one form. P3 does not ratify that choice and defines no normalization of its own; OQ1 stays open and is reported.

**Every open question stays open.** Each guard below names the question it holds and fails the moment someone answers it in code instead of in a SPEC.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_no_invention.py
"""Done-means 17, and the standing record that P3 answers no open question in code."""
from pathlib import Path

import pytest

import scan_agent
from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"

SOURCE_DIR = Path(scan_agent.__file__).parent


def modules():
    return sorted(SOURCE_DIR.glob("*.py"))


def all_source() -> str:
    return "\n".join(path.read_text() for path in modules())


def fixture_mime(path: Path) -> str | None:
    return "application/pdf" if path.suffix == ".pdf" else None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def test_the_observed_values_and_the_stored_values_are_the_same_values(ready, corpus: Path):
    # Done-means 17, as the drift test O5 argues for: "the two would drift".
    import os
    document = corpus / "Syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    observed = os.stat(document)

    selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    run = scan(ready, selection, source=FilesystemCorpusSource(),
               mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
               budget_exhausted=NEVER)

    row = ready.execute("SELECT * FROM files").fetchone()
    verdict = ready.execute(
        "SELECT * FROM stat_cache_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchone()

    assert row["observed_size"] == observed.st_size == verdict["observed_size"]
    assert verdict["observed_modification_time"] == observed.st_mtime
    assert row["filename"] == document.name
    assert row["extension"] == document.suffix
    assert row["mime_type"] == fixture_mime(document)


def test_p3_hashes_nothing_itself(all_modules=None):
    # O5: a second hash is a contract violation. P1's hash_file is the only one.
    source = all_source()
    assert "hashlib" not in source
    assert "sha256" not in source
    assert "md5" not in source


def test_p3_determines_no_mime_type(all_modules=None):
    # SPEC Q6 is OPEN: whether P3 sniffs a signature or records an extension-derived
    # type P5 later corrects is unsettled. P3 does neither.
    source = all_source()
    assert "mimetypes" not in source
    assert "%PDF" not in source
    assert "magic" not in source


def test_p3_defines_no_filename_normalization():
    # SPEC Q1 is OPEN: Unicode form, case folding, whitespace and separator collapse,
    # extension retention and diacritic handling are all unstated.
    source = all_source()
    assert "unicodedata" not in source
    assert "casefold" not in source
    assert "NFC" not in source and "NFD" not in source


def test_p3_holds_no_scan_state_enumeration():
    # SPEC Q4 is OPEN: the enumeration, and its relationship to §8.2's "extraction
    # status by extractor tier", is unsettled. The caller supplies the value.
    source = all_source()
    for value in ('"scanned"', '"unscanned"', '"pending"', '"superseded_content"',
                  '"stale"', '"complete"', '"skipped"'):
        assert value not in source, value


def test_p3_writes_no_extraction_run_and_names_no_completeness():
    # P4 Open question 6 stays open. None of P4's eight values means "the bytes are
    # not on this machine", and P3 chooses none and adds no ninth.
    source = all_source()
    for name in ("extraction_runs", "completeness", "text_units", "file_facts",
                 "handling_class", "sensitivity_state", "plan_version"):
        assert name not in source, name


def test_p3_holds_no_ceiling_and_no_threshold():
    # §8.6 names a configurable ceiling for neither traversal nor hashing, and SPEC
    # Q15 is OPEN. Every budget decision arrives as a caller-supplied predicate.
    source = all_source()
    # Constant-style spellings: a held ceiling would have to be bound to a name.
    # SQL's `LIMIT 1` and prose mentions of a deferred threshold are not ceilings.
    for token in ("MAX_", "_LIMIT", "CEILING", "THRESHOLD", "max_pages", "max_time"):
        assert token not in source, token


def test_p3_never_deletes_or_updates_an_event(all_modules=None):
    source = all_source().upper()
    assert "DELETE FROM EVENTS" not in source
    assert "UPDATE EVENTS" not in source


def test_p3_never_updates_the_files_table():
    # P1 owns identity resolution (§8.2); every files write goes through observe_path.
    source = all_source().upper()
    assert "UPDATE FILES" not in source
    assert "INSERT INTO FILES" not in source


def test_every_event_names_p3_and_only_through_event_defaults():
    # M8. `subsystem` is set in exactly one place.
    for path in modules():
        source = path.read_text()
        if path.name == "authorship.py":
            continue
        assert "subsystem=" not in source, path.name
        if "append_event(" in source:
            assert "event_defaults(" in source, path.name


def test_an_exclusion_still_appends_no_event():
    # SPEC Q13 is OPEN: §8.2's event record is keyed on file ID and an excluded
    # directory has no file record. This test is the standing record of that; it
    # changes the day Q13 closes.
    source = (SOURCE_DIR / "exclusion.py").read_text()
    assert "append_event" not in source
    assert "event_defaults" not in source


def test_nothing_branches_on_cross_folder_moves():
    # SPEC Q12 is OPEN: §1.1 records the selection, §6 and §7 never mention it, and
    # no part is assigned its enforcement. P3 records it and enforces nothing.
    for path in modules():
        source = path.read_text()
        if path.name == "selection.py":
            assert "if cross_folder_moves" not in source
            continue
        assert "cross_folder_moves" not in source, path.name


def test_p3_publishes_no_scan_identity_and_no_placement_vocabulary():
    # SPEC Q16 is OPEN (scan identity); §1.1's roots are context, not permission.
    source = all_source()
    for token in ("placement", "destination_node", "authorize", "approved_move",
                  "template_id", "domain_id"):
        assert token not in source, token


def test_p3_reads_no_volume_identifier():
    # P1 OQ9 is OPEN and P1's volume_id is session-tagged and nullable on purpose.
    # No P3 decision is built on it.
    source = all_source()
    assert "volume_id" not in source
    assert "OBSERVATION_SESSION" not in source


def test_the_deferred_exclusion_categories_are_still_empty():
    # SPEC Deferred: §1.1 names five categories and enumerates no member.
    from scan_agent.exclusion import CATEGORY_MEMBERS
    assert all(members == () for members in CATEGORY_MEMBERS.values())


def test_the_curation_threshold_is_still_unauthored():
    # SPEC Deferred, and Done-means 15.
    from scan_agent.inventory import CURATION_UNDETERMINED, curation_signal
    for evidence in (
        {"file_count": 0, "subdirectory_count": 0, "extension_mix": {},
         "project_root_markers": []},
        {"file_count": 900, "subdirectory_count": 40,
         "extension_mix": {".json": 800, ".py": 100}, "project_root_markers": []},
        {"file_count": 12, "subdirectory_count": 0, "extension_mix": {".pdf": 12},
         "project_root_markers": []},
    ):
        assert curation_signal(evidence) == CURATION_UNDETERMINED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_no_invention.py -v`
Expected: FAIL — collection succeeds and any guard whose forbidden token is present fails. If every prior task was written as specified, the only expected failures are ones this task exists to surface.

- [ ] **Step 3: Fix whatever the guard catches**

No new module. If a guard fires, the fix is in the module that tripped it, never in the guard: the guard is the SPEC's negative half. The one legitimate change is to the *token list* when a token proves to be a false positive against a design quotation in a docstring — in which case narrow the token, do not delete the test.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/p3/test_p3_no_invention.py -v`
Expected: PASS — 15 passed

- [ ] **Step 5: Commit**

```bash
git add tests/p3/test_p3_no_invention.py
git commit -m "test(P3): no-invention guard, one derivation of the ten fields, open questions held open"
```

---

### Task 18: The walking-skeleton P3 step

**Files:**
- Test: `tests/p3/test_p3_skeleton_step.py`

**Interfaces:**
- Consumes: everything above.
- Produces: the integration test every later part must keep green.

**[`../../02-segmentation-map.md`](../../02-segmentation-map.md)'s P3 slice, verbatim:** *"P3 — scan a fixture directory; assert the exclusion rules skip `node_modules`; P3 authors the discovery and stat-observation events P1 stores."*

The same document states the seam this test defends: *"P1 never originates a `discovery`, `stat observation`, `hashing` or `external modification detection` event: §8.2's reconstruction requirement is unmeetable from a log whose author field names the storage substrate as the thing that discovered the corpus. P3 authors the scan events… and P1 writes what it is handed."* This test is the P3 side of P1's `test_skeleton_p1_step`, which asserts the same rows from the other side. Deterministic: no model, no cloud, no embeddings, no network.

- [ ] **Step 1: Write the failing test**

```python
# tests/p3/test_p3_skeleton_step.py
"""The walking skeleton's P3 step (02-segmentation-map.md):
scan a fixture directory; assert the exclusion rules skip node_modules; P3 authors
the discovery and stat-observation events P1 stores.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.identity import hash_file

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import RULE_LITERAL_DIRECTORY_NAME
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.summary import scan_run_summary

NEVER = lambda: False


def fixture_mime(path: Path) -> str | None:
    return "application/pdf" if path.suffix == ".pdf" else None


def test_skeleton_p3_step(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)

    # A fixture directory: one PDF whose title carries a course code (the skeleton's
    # input file), and one node_modules the exclusion rules must skip.
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "syllabus-fixture.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "must-not-be-indexed.pdf").write_bytes(b"%PDF x")

    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by="skeleton-user")
    scan_run_id = scan(conn, selection, source=FilesystemCorpusSource(),
                       mime_type_for=fixture_mime, scan_state="fixture-scan-state",
                       budget_exhausted=NEVER)

    # The exclusion rules skip node_modules, and nothing inside it was indexed.
    rows = conn.execute("SELECT * FROM files").fetchall()
    assert [r["current_path"] for r in rows] == [str(document)]
    verdict = conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE scan_run_id = ?", (scan_run_id,)
    ).fetchone()
    assert verdict["path"] == str(corpus / "node_modules")
    assert verdict["rule"] == RULE_LITERAL_DIRECTORY_NAME
    assert verdict["rule_subject"] == "node_modules"

    # The record P1 holds is the one P3 handed over.
    assert rows[0]["content_hash"] == hash_file(document, materialized=True)
    assert rows[0]["mime_type"] == "application/pdf"
    assert rows[0]["directory_position"] == str(corpus)

    # P3 authors the discovery and stat-observation events P1 stores (M8).
    for event_type in ("discovery", "stat observation", "hashing"):
        row = conn.execute(
            "SELECT * FROM events WHERE event_type = ?", (event_type,)
        ).fetchone()
        assert row is not None, event_type
        assert row["subsystem"] == "P3", event_type
        assert row["component_version"]

    # Nothing in the scan half of the skeleton is authored by P1.
    authors = conn.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in authors] == ["P3"]

    # And the run is legible (§8.6).
    summary = scan_run_summary(conn, scan_run_id)
    assert summary["files_indexed"] == 1
    assert summary["paths_excluded_by_rule"] == {RULE_LITERAL_DIRECTORY_NAME: 1}
    assert summary["files_deferred"] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/p3/test_p3_skeleton_step.py -v`
Expected: FAIL if any prior task is incomplete; otherwise PASS.

- [ ] **Step 3: Run the full suite one final time**

Run: `pytest -v --tb=short`
Expected: PASS — every P3 test from Tasks 1–18 green, and every P1 test still green (P3 modified no P1 file).

- [ ] **Step 4: Commit**

```bash
git add tests/p3/test_p3_skeleton_step.py
git commit -m "test(P3): walking-skeleton P3 step, node_modules skipped, every event authored by P3"
```

---

## Self-Review

**Spec coverage.** Every Contract-out record has a task: R1 → Task 2, R2 → Task 10, R3 → Tasks 4–5, R4 → Task 11, R5 → Task 14, R6 → Task 13. The three `11-ops-runtime.md` runtime obligations have tasks of their own: the FSEvents session watch → Task 16, dataless iCloud detection → Task 6, Full Disk Access → Task 8. Done-means 1–18 map as: 1→T10, 2→T9/T10, 3→T4/T9, 4→T5/T9, 5→T9, 6→T4/T9, 7→T11, 8→T11, 9→T11, 10→T10, 11→T10, 12→T2, 13→T9/T14, 14→T15, 15→T13, 16→T13, 17→T17, 18→T12.

**Authorship.** P3 authors and P1 writes, everywhere. `event_defaults` (Task 1) is the single place `subsystem` is set, it refuses any value but `"P3"`, and it refuses a type P3 does not author. Task 17's `test_every_event_names_p3_and_only_through_event_defaults` fails if a second route appears. The scan-time `hashing` event is appended inside P1's `observe_path` and carries P3's name because P3 supplies `author` — Task 10 asserts that row's `subsystem` is `"P3"`, which is the same row P1's `test_p1_authors_none_of_the_scan_events` asserts from the other side.

**Registration.** P3 registers nothing (B5). All four types are reserved §8.2 names already in P1's frozen table; `scan_agent` contains no registration call, and Task 1 asserts both.

**Open questions this plan does not answer.** Q1 (normalized filename) — P3 defines no normalization and Task 17 guards it; the plan reports that **P1's** `record_file` picks NFC. Q2 (which timestamps) — P3 observes size and mtime for §1.2's cache and adds no timestamp of its own. Q4 (scan-state enumeration) — the caller supplies one value; `scan_agent` holds no vocabulary. Q6 (MIME determination) — a caller-supplied strategy; no `mimetypes`, no signature table. Q7 (symlinks, aliases, packages, mounts) — recorded as `traversal behaviour unresolved`, never decided; `.app` bundles are descended, which is Q7's stated cost. Q8 (exclusion override) — no override exists; §1.1 gives the user no control over the rules and P3 adds none. Q9 (does the project-root rule exclude the root itself) — §1.1's literal word `descendants` is implemented and the marker-bearing directory's eligibility is asserted nowhere. Q11 (where R1 lives) — R1 is a plain record with no plan-version binding. Q12 (where `cross_folder_moves` is enforced) — recorded, enforced nowhere, guarded. Q13 (do exclusion verdicts get events) — R3 has its own table and appends no event, guarded. Q14 (disappearance) — `11` §4's watch rule is followed for the *event*; the `files` row is untouched and that half stays open. Q15 (hashing ceiling) — none held; the budget is a caller predicate. Q16 (scan identity) — a local handle, off `events`, joined to P1's `scan_id` by nothing. P4 OQ6 (`completeness` for a dataless file) — no run row, no completeness value, guarded. P1 OQ9 (volume identifier) — read by nothing.

**Placeholder scan.** No "TBD", no "add error handling", no "similar to Task N", no angle-bracket placeholder standing in for a real name. Every code step carries complete runnable code and every test step names the exact `pytest` command and expected result.

**Type consistency.** `scan`, `walk`, `observe_path`, `record_basic_record`, `cache_verdict`, `record_directory`, `record_exclusion`, `record_deferral` are spelled identically in every task that mentions them. `applies_to` values are `"scanned source"` / `"candidate root"` throughout. `verdict` values are `reuse` / `recompute` and `reason` values are the SPEC's four, nowhere else respelled. `budget_exhausted`, `mime_type_for` and `scan_state` are required keywords with the same spelling in Tasks 9, 10, 11, 13, 14, 15 and 18.

## Known gaps, carried deliberately

- **The FSEvents / `DispatchSource` adapter** (Task 16). The standard library supplies no binding and this plan adds no runtime dependency. `SessionWatch.notify` is the entry point such an adapter calls and every semantic rule `11` §4 states is implemented and tested against it; `poll` is the stdlib driver. The platform callback itself is missing and is not faked.
- **The legacy `.icloud` placeholder form** (Task 6). A not-downloaded `Foo.pdf` can appear on disk as a hidden `.Foo.pdf.icloud`. `11` §5 does not name that shape and inventing a filename heuristic for it would be P3 authoring a detection rule the contract does not supply. `SF_DATALESS` is the one detection built.
- **macOS packages and application bundles are descended** (Task 7). They are ordinary directories and §1.1 supplies no rule that stops the traversal. SPEC Q7 names this exact cost — *"a descended `.app` bundle alone would inject thousands of spurious rows"* — and this plan records it rather than inventing the rule.
- **A metadata-safe replay writes no `files` row** (Task 15). §8.5's metadata-safe form has no bytes, P1's identity is the content hash, and P1 publishes no entry point that records a file from a supplied hash. Exclusion verdicts, cache verdicts and curation signals all reproduce, which is what Done-means 14 asks for; the `files` half does not.
- **R4's `file_id` is `NULL` in a metadata-safe replay** for the same reason. *"File identity as resolved by P1"* reads as unknown rather than as a fabricated value.
- **Two `external modification detection` rows on a content change** (Task 12): P3's, keyed on the stat difference that triggered the re-read, and P1's, keyed on the version being superseded. Both are P3-authored, both are true, both are append-only, and their explanations distinguish them. Recorded as a seam worth review rather than optimized away.
- **P1 re-derives six of P3's ten fields** (Task 17). P1's Contract in says P3 hands them over; P1's plan has `record_file` stat and hash the path itself. The drift test catches a disagreement; the divergence is P1's to resolve.
- **`create_scan_schema` is not called by `open_database`**, the same gap P1 carries. Every caller must run P1's `create_schema` and then P3's. Not blocking Tasks 1–18.
- **Schema migration.** P3 adds six tables to P1's database and stamps no version of its own. The first *change* to a P3 table needs one; the first creation does not.
- **P3 samples no resource counter.** §8.6's six are P1's `scan_resource_usage` (P1 Contract out §10), and joining a P3 run to a P1 `scan_id` is SPEC Q16 / P1 OQ19 and is open. So a P13 progress line can render P3's five counters and P1's six, and cannot yet join them.

## Execution Handoff

Plan saved to `planning/parts/P3-scan-corpus-selection/PLAN.md`. P3 builds on P1 alone: every task above is testable with no other part present, using fixture directories under `tmp_path` and never the user's disk. Two execution options:

1. **Subagent-Driven (recommended)** — a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints for review.

Tasks 1–8 are independent of each other except through `schema.py`; Tasks 9–18 are sequential.

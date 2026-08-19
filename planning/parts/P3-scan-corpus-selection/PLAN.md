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

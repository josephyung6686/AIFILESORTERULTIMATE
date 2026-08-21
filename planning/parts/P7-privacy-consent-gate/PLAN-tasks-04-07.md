# P7 — Privacy and consent gate — PLAN, Tasks 4–7

> This file is one section of P7's implementation plan. Tasks 1–3 and 8–22 are written by other
> authors against the same [`PLAN-SKELETON.md`](PLAN-SKELETON.md); everything they publish is
> consumed here under the names the skeleton's `Interfaces:` blocks fix. Format and standard are
> [`../P4-evidence-shape/PLAN.md`](../P4-evidence-shape/PLAN.md) and
> [`../P5-extractors/PLAN.md`](../P5-extractors/PLAN.md). A finished sibling section is
> [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md).

**Verified against the live substrate, 2026-08-22.** Every P1–P5 signature quoted below was read
with `inspect.signature` against the shipped packages, not from a PLAN:

```text
database_agent.files_table  set_sensitivity_state(conn, file_id, *, state: dict, author: str,
                                                  component_version: str) -> None
                            get_file(conn, file_id) -> sqlite3.Row
                            record_file(conn, path, *, filename, normalized_filename, extension,
                                        observed_size, observed_timestamps, parent_folder_context,
                                        mime_type, detected_format, scan_state, materialized,
                                        content_hash=None) -> str
                            FILES_COLUMNS  — sixteen, ending sensitivity_state
database_agent.supersede    SUPERSEDE_COLUMNS = ('supersedes','superseded_by','supersede_reason')
                            supersede_ddl(table) -> str
                            mark_superseded(conn, table, *, old_id, new_id, reason) -> None
                            chain(conn, table, record_id) -> list[sqlite3.Row]
database_agent.events       append_event(conn, **fields) -> int
database_agent.db           transaction(conn)   contextmanager
evidence_shape.canonical    canonical_json(value) -> str
evidence_shape.location     TextSpan(start, end) · Region(x,y,w,h,unit) · Segment(kind,index,label)
evidence_shape.store        runs_for_file(conn, file_id) -> list[ExtractionRun]
extractors.long_tail        POTENTIALLY_SENSITIVE = 'potentially sensitive'
                            sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]
```

Four facts read off that surface change what is written below.

1. **`mark_superseded` and `chain` are `... WHERE record_id = ?`.** P7's classification table
   therefore carries `record_id` as a **VIRTUAL generated projection** of its published
   `fact_id`, exactly as P4's `evidence` table projects `observation_id`
   (`src/evidence_shape/schema.py`, `SUPERSEDE_ADAPTER_COLUMN = "record_id"`). P1's tested
   supersede functions are reused verbatim rather than rewritten under a second name.
2. **`set_sensitivity_state` issues exactly one statement**, `UPDATE files SET sensitivity_state = ?
   WHERE file_id = ?`, and appends no event (M8: P7 authors, P1 stores). That single statement is
   observable at run time through `sqlite3.Connection.set_trace_callback`, which is how Task 4
   proves *"`src/privacy/` issues no `UPDATE files` of its own"* without grepping source text.
3. **`record_file` stats the path**, so a `files` row needs a real file on disk even when
   `content_hash` is supplied. Every fixture below writes bytes into `tmp_path` first.
4. **`sensitivity_signals_for` is keyed by `run_id` only.** The file-level walk is
   `runs_for_file(conn, file_id)` → `sensitivity_signals_for(conn, run.run_id)`. P7 adds no reader
   to P5; Task 7 composes the two that already exist.

---

## What binds these four tasks, applied rather than restated

**D2 (ratified 2026-08-21) restructured Task 4, and this section builds the new shape.** The
skeleton's Task 4 was a **P6 seam**: an injected `SensitivityFacts` protocol with a stand-in at
`tests/p7/p6_fixture.py`. D2 killed it. `ClassificationRecord` keyed `(file_id, content_hash)` is
**authoritative**, so there is no P6 record to read and no seam to inject.
`src/privacy/facts_seam.py` becomes **`src/privacy/classification_store.py`** and
`SensitivityFacts` becomes a concrete **`ClassificationStore`** over a table **P7 creates and
owns** — `current`, `write`, `supersede`, `history`, unchanged in shape, plus the
`current_fact_id` the sibling section requires. **No injection, no protocol, no default.**
`tests/p7/p6_fixture.py` is **deleted, not reimplemented**: there is no longer a P6 surface for it
to stand in for. Supersession still runs through P1's three columns and `files.sensitivity_state`
is still written through P1's published `set_sensitivity_state`. Task 4 loses a protocol and gains
a `CREATE TABLE`.

**`Unreadable or unclassified` is a gate OUTCOME, not a file fact.** It lives on the release
decision and never in `files.sensitivity_state`, because storing it there would make *"nothing has
looked"* indistinguishable from *"this file carries nothing"* (D2). Task 4 enforces that on both
sides of the projection: the store refuses to write such a record and `mirror_state` refuses to
build such a dict.

**§3.13's ordering is P6's, quoted, never re-derived.** The design's own listed order, line 50 of
[`../../00-database-agent-product-design.md`](../../00-database-agent-product-design.md): *"A user
confirmed fact has been explicitly accepted, entered, renamed, merged, or corrected by the user. A
direct fact was read from a reliable and explicit source… A validated fact was found by a
deterministic rule and passed contextual checks… An LLM-supported fact was proposed by a language
model… A possible fact is a useful but insufficient clue… A rejected fact is a proposal that the
user or validator marked as incorrect."* Five ranked, `rejected` outside the ranking. A
`user_confirmed` record outranks a `validated` one **by that listed order**, and Task 4 writes the
order down once and computes nothing from it.

**The detector is unwritten (D2), so `Denied(unclassified)` is the ordinary path.** No task in any
plan produces a rule set. Nothing below defaults an absent classification to `public_low` or to any
other low class; absence resolves to `unreadable_unclassified` at the gate and to `None` in the
store. Every test that needs a classification writes one itself and says so in its docstring,
standing in for the detector that does not exist.

**`src/privacy/` holds no threshold, no identifier class, no detection rule, and imports none of
`extractors`' three refusals** — `safety.admit`, `ProtectedContainerRefused`, `DatalessRefused`.
Task 21 asserts the absence repo-wide; these four tasks simply never reach for them.

---

## Deviations from the skeleton's `Interfaces:` blocks, reported not smuggled

Each is an addition or a widening that the task cannot be written without. They are listed here in
one place so the authors of the neighbouring tasks can see them without reading four task bodies.

| # | Task | Skeleton says | This section publishes | Why |
|---|---|---|---|---|
| A1 | 4 | `src/privacy/facts_seam.py`, `SensitivityFacts` protocol, `tests/p7/p6_fixture.py` | `src/privacy/classification_store.py`, concrete `ClassificationStore`, **no** `p6_fixture.py` | D2, and the skeleton's own SETTLED 2026-08-22 paragraph. The test file is renamed to `tests/p7/test_p7_classification_store.py` on the same ruling. |
| A2 | 4 | `Produces` stops at `mirror_state` | adds `current_fact_id(file_id, content_hash) -> str \| None` | `mark_superseded` keys on a row id and `ClassificationRecord`'s eight SPEC §2 fields carry none. Required by sibling Task 16's `reclassify`. Already reported in [`PLAN-tasks-15-16.md`](PLAN-tasks-15-16.md). |
| A3 | 4 | `Produces` stops at `mirror_state` | adds `mirror(conn, record, *, component_version) -> None` | The skeleton requires a test that the projection *"goes through P1's published `set_sensitivity_state`"*. That needs one call site inside `src/privacy/`, not a call written in a test. Task 16 may keep calling `mirror_state` + `set_sensitivity_state` itself — `mirror` is exactly those two composed — but calling `mirror` leaves Task 21 one call site to count instead of two. |
| A4 | 4 | `Files:` names only `facts_seam.py` | Task 4 creates `src/privacy/schema.py` with `create_privacy_schema(conn)`; **Task 5 extends the same function** | *"Task 4 loses a protocol and gains a `CREATE TABLE`"* and Task 4 runs first. One schema entry point, called once by `tests/p7/conftest.py`. |
| A5 | 4 | — | consumes `privacy.classification.UNREADABLE_UNCLASSIFIED` | The class name must exist as a bound name, not as a literal retyped in a second module — that duplication is the defect class P1's `set_sensitivity_state` docstring calls *"this project's most expensive"*. **Task 3 must publish it**; its own tests already assert `resolve_class(None) == "unreadable_unclassified"`. |
| A6 | 5 | `current_policy(conn, *, plan_version) -> Policy` | `-> Policy \| None` | A non-optional return forces `policy.py` to hold a default mode, which is Task 6's W1 job and which Task 6's negative test forbids anywhere else. `None` means *no policy has been set*, and Task 6 is what turns that into the local-first floor. |
| A7 | 5 | — | `SHOWN`, `REDACTED`, `REDACTION_VALUES: tuple[str, str]` | SPEC §10 spells the two values — *"each shown \| redacted"* — and `Policy` cannot validate `redaction_settings` without names for them. They arguably belong in Task 2's `vocabulary.py`; if Task 2 publishes them, `policy.py` re-exports and deletes its own. Reported to the Task 2 author. |
| A8 | 5 | `set_policy(conn, policy, …)` | refuses a `Policy` whose `policy_version` is not `UNSET_POLICY_VERSION` | SPEC §6: *"the gate owns the policy, so the caller does not supply this value, it echoes it."* A minted value cannot be minted if the caller already filled the field. |
| A9 | 5 | *"the policy, consent-grant and release-ledger tables"* | **one** table, `privacy_policies`; grants live on the policy row | `policy_version` is a binding term (B2). A consent grant that did not mint a new policy version would leave releases minted before the grant still spendable after it. §8.8 also lists *"Privacy and model-consent policies"* as one plan-version item, not two. The release ledger stays Task 12's. |
| A10 | 6 | `resolve_default_policy(stored) -> Policy` | `resolve_default_policy(stored, *, install_mode, plan_version, set_at) -> Policy` | `install_mode` is a **required keyword validated against `LOCAL_FIRST_MODES`** — the mechanical form of *"P7 constrains it without choosing it"* (Contract out §5, W1). It is why `src/privacy/` can hold no default mode at all and why Open question 11 stays structurally open. |
| A11 | 7 | `check_item(item, *, unit_length) -> None` | `check_item(item, *, unit_length, protected, sensitive_keys, allow_unratified) -> None` | `protected` is unavoidable: the skeleton itself requires *"`Filename` is permitted for non-protected files and denied for protected ones"*, which the two-argument form cannot express. `sensitive_keys` carries P5's `POTENTIALLY_SENSITIVE` set, which is the only way §8.4's *"raw sensitive values"* is recognisable without a detection rule P7 does not own. `allow_unratified` is B5d/C9a, below. |
| A12 | 7 | six item kinds, flat | `RATIFIED_ITEM_KINDS` (5) + `UNRATIFIED_ITEM_KINDS` (1), and `allow_unratified` with no default | §8.4 names **five** releasable kinds and puts *paths* in the always-local set; P7's SPEC adds `filename` as a sixth and flags it itself. **NEEDS-JOSEPH B5d/C9a.** The sixth kind is built but cannot be admitted by a caller who has not written the word `allow_unratified=True`. |
| A13 | 7 | — | `sensitive_observation_keys(conn, file_id) -> frozenset[str]`, `kind_of(item) -> str` | The first is the P4→P5 walk the skeleton describes and assigns to no task's `Produces`. The second maps a dataclass to its `ITEM_KINDS` name, needed by `check_item` here and by Task 10's `excerpts_included`. |

**NEEDS-JOSEPH C5 — flagged, not resolved.** P7's SPEC *Contract in* says *"**P6 must accept
`sensitivity` as a first-class universal field** (§3.11) rather than a domain-scoped one."* D2 makes
**P7's** record authoritative, and round 1's F-2 found that P6 field has **no producer**. Those two
sentences cannot both be load-bearing. Task 4 is therefore written so that **nothing in it depends
on a P6 field existing**: the store creates and reads its own table, no test creates a `file_facts`
row, and one test asserts the store works in a database that has no such table at all. D2 decided
which record is authoritative; it did **not** decide whether a second, P6-owned field row continues
to exist beside it. Until Joseph answers, P6 should create no such row and P7 reads none.

**NEEDS-JOSEPH B5d/C9a — flagged, not resolved.** §8.4's releasable list is *"selected excerpts,
redacted identifiers, candidate labels, non-sensitive metadata, and evidence references"* — five —
and the same sentence puts *"Paths"* in the always-local set. §7.7's residual dossier *"includes the
filename"*, and §7.3 forbids filenames in prompts **only** for `Protected Records`. P7's SPEC reads
directory path ≠ filename, permits `filename` for non-protected files, and lists the reading in its
own Open questions as number 2. Task 7 builds the sixth kind and makes it **unadmittable without an
explicit opt-in**, so a reviewer sees an unratified reading rather than a shipped one.

---

## Tasks

### Task 4: P7's own classification store, §3.13's ordering, and the `sensitivity_state` projection

**Files:**
- Create: `src/privacy/schema.py`, `src/privacy/classification_store.py`
- Modify: `tests/p7/conftest.py` (P7's own; `tests/conftest.py` is not touched)
- Test: `tests/p7/test_p7_classification_store.py`

**Interfaces:**
- Consumes: `database_agent.supersede.mark_superseded(conn, table, *, old_id, new_id, reason)
  -> None`, `.chain(conn, table, record_id) -> list[sqlite3.Row]`, `.SUPERSEDE_COLUMNS`,
  `.supersede_ddl(table) -> str`,
  `database_agent.files_table.set_sensitivity_state(conn, file_id, *, state: dict, author: str,
  component_version: str) -> None`, `.get_file(conn, file_id) -> sqlite3.Row`, `.FILES_COLUMNS`,
  `database_agent.db.create_schema(conn) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.classification.ClassificationRecord`, `.CLASSIFICATION_FIELDS`,
  `.UNREADABLE_UNCLASSIFIED` (A5),
  `privacy.authorship.SUBSYSTEM`.
- Produces (`schema.py`):
  - `CLASSIFICATIONS_TABLE: str = "classifications"`
  - `SUPERSEDE_ADAPTER_COLUMN: str = "record_id"`
  - `CLASSIFICATIONS_DDL: str`
  - `create_privacy_schema(conn) -> None` — idempotent; **Task 5 extends this function**.
- Produces (`classification_store.py`):
  - `RELIABILITY_ORDER: tuple[str, ...]` — §3.13's five ranked, strongest first.
  - `REJECTED: str = "rejected"` — the sixth state, outside the ranking.
  - `ClassificationStore(conn)` with `current(file_id, content_hash) -> ClassificationRecord | None`,
    `current_fact_id(file_id, content_hash) -> str | None`, `write(record) -> str`,
    `supersede(old_fact_id, new_fact_id, reason) -> None`,
    `history(file_id) -> list[ClassificationRecord]`.
  - `strongest(records: Sequence[ClassificationRecord]) -> ClassificationRecord`
  - `mirror_state(record) -> dict`
  - `mirror(conn, record, *, component_version) -> None`
  - `AmbiguousCurrentClassification`, `UnrankedReliability`, `GateOutcomeNotAFileFact`.

**Done-means:** 2 (second half).

**This task owns storage and authors nothing.** C4: *"the gate still raises and writes nothing — a
gate that also wrote would be doing two jobs."* `ClassificationStore.write` inserts a row and
appends **no** event; `classification_assigned` and `classification_superseded` are appended by
sibling Task 16's `assign` and `reclassify`, which are the entry points a detector or a user
correction calls. A store that also appended would put one act in the log twice and would make the
event's `user_id` a property of the storage layer rather than of the act.

**The key is `(file_id, content_hash)` and new bytes inherit nothing.** D2: *"Keyed on the hash
because a classification is about BYTES; new bytes at a path are a new file version and inherit
nothing."* `current` is keyed on the pair, not on `file_id`, and a second content hash at the same
`file_id` resolves to `None` until something classifies it. That is the whole reason
`unreadable_unclassified` cannot be a stored fact: an edited passport scan must read as *nobody has
looked at these bytes*, not as *these bytes were found to carry nothing*.

**Ties are a red test, never a pick.** Two unsuperseded records at one key and one reliability rank
raise `AmbiguousCurrentClassification`. P4 took the identical position on `observations_by_key`
returning two rows — resolve to the current row, and *"an unresolvable ambiguity raises rather than
picking the first"*. A gate that picked would release under whichever classification the query
planner happened to return first.

**Whether `protected` is co-extensive with the top two handling classes stays open.** SPEC Open
question 1, and SPEC §2: *"Neighbouring parts should consume the `protected` flag, not infer it from
the class."* `protected` is a stored column on every record and is never derived here; one test
holds the question by name.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_classification_store.py
"""Done-means 2's second half: exactly one current classification per file version,
supersede-never-overwrite through P1's three columns, and the projection onto
`files.sensitivity_state` through P1's published setter.

Three things this file deliberately does NOT do.

It creates no `file_facts` row and imports nothing from a P6 module, because D2 made
P7's `ClassificationRecord` authoritative and there is no P6 record to read. P7's
SPEC still says "P6 must accept `sensitivity` as a first-class universal field" while
round 1 found that field has no producer; that conflict is Joseph's (NEEDS-JOSEPH C5)
and this file is written so nothing in it depends on the answer.

It stores no `unreadable_unclassified` record and never lets one reach the column.
That value is a GATE OUTCOME (D2) -- what the release decision says when it has no
classification to release against -- and storing it would make "nothing has looked"
read as "this file carries nothing".

It writes its own classifications and says so, because the detector is unwritten (D2)
and on a real corpus every file would resolve to `Denied(unclassified)`. A fixture
standing in for a detector is the honest v1 posture; a fixture pretending to BE one
is not.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from database_agent.files_table import FILES_COLUMNS, get_file, record_file
from database_agent.supersede import SUPERSEDE_COLUMNS, chain

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.classification_store import (
    REJECTED,
    RELIABILITY_ORDER,
    AmbiguousCurrentClassification,
    ClassificationStore,
    GateOutcomeNotAFileFact,
    UnrankedReliability,
    mirror,
    mirror_state,
    strongest,
)
from privacy.schema import (
    CLASSIFICATIONS_TABLE,
    SUPERSEDE_ADAPTER_COLUMN,
    create_privacy_schema,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"

#: Bare hex digests, because that is what P1 stores (R1) and what P4 refuses to
#: accept anything else as: `MalformedRun: content_hash is the digest P1 stored`.
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_EDITED = "e" * 64

#: §8.4: "A scanned passport ... should enter a protected state immediately." The
#: DETECTOR that would notice is unwritten (D2), so the test plays its part and the
#: `basis` says which part it is playing.
PASSPORT_KEYS = ("obs-key-passport-mrz", "obs-key-passport-number")


def a_file(conn, tmp_path: Path, *, name: str = "passport.pdf",
           content_hash: str = HASH_A) -> str:
    """A `files` row. `record_file` stats the path, so the bytes must exist."""
    path = tmp_path / name
    path.write_bytes(b"scanned passport")
    return record_file(
        conn, path, filename=name, normalized_filename=name.rsplit(".", 1)[0],
        extension=".pdf", observed_size=path.stat().st_size,
        observed_timestamps="{}", parent_folder_context=None, mime_type=None,
        detected_format=None, scan_state="seen", materialized=True,
        content_hash=content_hash)


def a_record(**over) -> ClassificationRecord:
    base = dict(file_id="file-1", content_hash=HASH_A,
                handling_class="highly_sensitive_credential_bearing",
                protected=True, basis="detector", evidence_refs=PASSPORT_KEYS,
                reliability_state="validated", observed_at=FIXED_CLOCK)
    base.update(over)
    return ClassificationRecord(**base)


@pytest.fixture()
def store(p7_conn) -> ClassificationStore:
    return ClassificationStore(p7_conn)


# --- the table P7 creates and owns ------------------------------------------

def test_the_schema_is_idempotent(p7_conn):
    # `p7_conn` already created it; a second call is a no-op, the way P4's
    # `create_evidence_schema` is.
    create_privacy_schema(p7_conn)
    create_privacy_schema(p7_conn)


def test_the_table_carries_p1s_three_supersede_columns_under_p1s_spelling(p7_conn):
    # M1, and MINOR 3 confirms the spelling is `supersede_reason`. P7 does not
    # re-spell the set and does not add a fourth.
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns
    assert "preferred" not in columns


def test_record_id_is_a_virtual_projection_of_the_published_fact_id(p7_conn):
    # P1's `mark_superseded` and `chain` are `... WHERE record_id = ?`, and P7's
    # published id is `fact_id`. P4 solved this once (`SUPERSEDE_ADAPTER_COLUMN`)
    # and P7 copies the solution rather than a second supersede implementation.
    assert SUPERSEDE_ADAPTER_COLUMN == "record_id"
    visible = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({CLASSIFICATIONS_TABLE})")}
    assert "fact_id" in visible
    assert "record_id" not in visible          # VIRTUAL: absent from table_info
    hidden = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_xinfo({CLASSIFICATIONS_TABLE})")}
    assert "record_id" in hidden


def test_a_classification_cannot_be_deleted(p7_conn, store):
    # §8.2's rule, and §8.7 needs the rejected proposal's evidence to survive.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"DELETE FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (fact_id,))


def test_a_classification_cannot_be_overwritten(p7_conn, store):
    # §8.2 forbids overwriting the earlier record. The three supersede columns are
    # outside the trigger: supersession is the one legal write to an existing row.
    fact_id = store.write(a_record())
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {CLASSIFICATIONS_TABLE} SET handling_class = ? WHERE fact_id = ?",
            ("public_low", fact_id))


def test_p7_adds_no_column_to_p1s_files_table(p7_conn):
    # P7 creates and modifies no file owned by another part, and `sensitivity_state`
    # has been on `files` since P1's first schema.
    columns = tuple(row["name"] for row in p7_conn.execute("PRAGMA table_info(files)"))
    assert columns == FILES_COLUMNS


# --- one current record per file VERSION ------------------------------------

def test_write_returns_a_fact_id_and_current_reads_the_record_back(store):
    record = a_record()
    fact_id = store.write(record)
    assert isinstance(fact_id, str) and fact_id
    assert store.current("file-1", HASH_A) == record


def test_current_is_keyed_on_the_content_hash_and_not_on_the_file_id(store):
    store.write(a_record())
    assert store.current("file-1", HASH_B) is None


def test_new_bytes_at_the_same_file_inherit_nothing(store):
    # D2: "a classification is about BYTES; new bytes at a path are a new file
    # version and inherit nothing." The edited scan reads as unlooked-at, which is
    # what makes `Denied(unclassified)` correct rather than a regression.
    store.write(a_record())
    assert store.current("file-1", HASH_EDITED) is None
    assert store.current_fact_id("file-1", HASH_EDITED) is None


def test_current_is_none_before_anything_classifies(store):
    # The detector is unwritten (D2). This is the state a real corpus is in.
    assert store.current("file-unknown", "sha256:zzz") is None


def test_current_fact_id_returns_the_unsuperseded_row(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert store.current_fact_id("file-1", HASH_A) == new


# --- §3.13's ordering, quoted and not re-derived ----------------------------

def test_the_ordering_is_p6s_listed_order(store):
    # The design lists them in this order and states no comparison rule; P6's
    # canonical snake_case literals, never a respelling.
    assert RELIABILITY_ORDER == (
        "user_confirmed", "direct", "validated", "llm_supported", "possible")
    assert REJECTED == "rejected"
    assert REJECTED not in RELIABILITY_ORDER


def test_a_user_confirmed_record_outranks_a_validated_one(store):
    validated = a_record(reliability_state="validated")
    confirmed = a_record(reliability_state="user_confirmed",
                         handling_class="personal_non_sensitive", protected=False,
                         basis="user", evidence_refs=(), observed_at=LATER)
    store.write(validated)
    store.write(confirmed)
    assert store.current("file-1", HASH_A) == confirmed


def test_the_ordering_holds_regardless_of_write_order(store):
    confirmed = a_record(reliability_state="user_confirmed", basis="user",
                         evidence_refs=())
    store.write(confirmed)
    store.write(a_record(reliability_state="direct", observed_at=LATER))
    assert store.current("file-1", HASH_A) == confirmed


def test_strongest_reads_the_order_and_computes_no_score(store):
    records = [a_record(reliability_state=state) for state in
               ("possible", "llm_supported", "direct", "user_confirmed", "validated")]
    assert strongest(records).reliability_state == "user_confirmed"
    assert strongest(records[:1]).reliability_state == "possible"


def test_strongest_of_nothing_is_a_programming_error(store):
    with pytest.raises(ValueError):
        strongest(())


def test_a_rejected_record_is_stored_and_is_never_current(store):
    # §8.7: rejections are stored "with the evidence that produced them". A rejected
    # fact is a record of a proposal the user marked incorrect, so it must survive
    # and must never be the answer to "what is this file".
    rejected = store.write(a_record(reliability_state=REJECTED))
    assert store.current("file-1", HASH_A) is None
    assert [r.reliability_state for r in store.history("file-1")] == [REJECTED]
    assert rejected


def test_an_unranked_reliability_raises_rather_than_sorting_last(store):
    # A value outside §3.13's six is a load error, not a fallback. Sorting it last
    # would let an unknown state quietly become the weakest evidence in the product.
    with pytest.raises(UnrankedReliability):
        strongest([a_record(reliability_state="probably_fine")])


def test_two_live_records_at_the_same_rank_raise_rather_than_pick(store):
    store.write(a_record(evidence_refs=("obs-key-a",)))
    store.write(a_record(evidence_refs=("obs-key-b",), observed_at=LATER))
    with pytest.raises(AmbiguousCurrentClassification):
        store.current("file-1", HASH_A)


# --- supersede, never overwrite ---------------------------------------------

def test_a_revision_supersedes_through_p1s_three_columns(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(handling_class="personal_non_sensitive", protected=False,
                               basis="user", evidence_refs=(),
                               reliability_state="user_confirmed", observed_at=LATER))
    store.supersede(old, new, "user reclassified as non-sensitive")
    row = p7_conn.execute(
        f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?", (old,)).fetchone()
    assert row["superseded_by"] == new
    assert row["supersede_reason"] == "user reclassified as non-sensitive"
    assert p7_conn.execute(
        f"SELECT supersedes FROM {CLASSIFICATIONS_TABLE} WHERE fact_id = ?",
        (new,)).fetchone()["supersedes"] == old


def test_both_records_remain_readable_afterwards(store):
    # §8.2's explicit rule, and its OCR example applies directly: an early detector
    # and a later one may disagree and both survive.
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    history = store.history("file-1")
    assert len(history) == 2
    assert {r.basis for r in history} == {"detector", "user"}


def test_the_chain_is_p1s_and_p7_does_not_copy_it(p7_conn, store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert [row["fact_id"] for row in chain(p7_conn, CLASSIFICATIONS_TABLE, old)] == \
        [old, new]


def test_the_first_supersede_reason_is_never_overwritten(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    third = store.write(a_record(reliability_state="direct", observed_at=LATER))
    with pytest.raises(ValueError, match="already superseded"):
        store.supersede(old, third, "a second reason")


def test_a_superseded_record_is_not_current(store):
    old = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=()))
    new = store.write(a_record(reliability_state="validated", observed_at=LATER))
    store.supersede(old, new, "detector re-ran on better evidence")
    # The superseded record outranks the survivor by §3.13, and is still not the
    # answer: supersession is a stronger statement than reliability.
    assert store.current("file-1", HASH_A).reliability_state == "validated"


def test_history_is_oldest_first_and_spans_file_versions(store):
    store.write(a_record(observed_at=FIXED_CLOCK))
    store.write(a_record(content_hash=HASH_EDITED, observed_at=LATER))
    assert [r.content_hash for r in store.history("file-1")] == \
        [HASH_A, HASH_EDITED]


# --- the projection onto files.sensitivity_state ----------------------------

def test_the_mirror_goes_through_p1s_published_setter(p7_conn, tmp_path):
    # D2: the column is the record's PROJECTION, written through the twin of
    # `set_extraction_status`. P5 took the identical position on
    # `extraction_status_by_tier` and the resolution was P1 publishing the setter.
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    mirror(p7_conn, record, component_version=COMPONENT)
    stored = json.loads(get_file(p7_conn, file_id)["sensitivity_state"])
    assert stored == mirror_state(record)


def test_privacy_issues_no_update_files_of_its_own(p7_conn, tmp_path):
    # Asserted by RUNTIME TRACE, not by grepping source text: `set_trace_callback`
    # sees the statements sqlite actually executed, and a comment or a docstring
    # cannot fake one. Exactly one `UPDATE files` runs and it is P1's, verbatim.
    file_id = a_file(p7_conn, tmp_path)
    statements: list[str] = []
    p7_conn.set_trace_callback(statements.append)
    try:
        mirror(p7_conn, a_record(file_id=file_id), component_version=COMPONENT)
    finally:
        p7_conn.set_trace_callback(None)
    updates = [s for s in statements if s.lstrip().upper().startswith("UPDATE FILES")]
    assert len(updates) == 1
    assert updates[0].startswith("UPDATE files SET sensitivity_state = ")


def test_the_mirror_authors_as_p7(p7_conn, tmp_path, monkeypatch):
    # M8: the acting part authors, P1 stores. `author` is not a parameter a caller
    # of `mirror` may set.
    import privacy.classification_store as module
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        module, "set_sensitivity_state",
        lambda conn, file_id, **fields: seen.update(fields, file_id=file_id))
    mirror(p7_conn, a_record(file_id="file-1"), component_version=COMPONENT)
    assert seen["author"] == SUBSYSTEM == "P7"
    assert seen["component_version"] == COMPONENT


def test_the_projection_carries_the_record_and_not_a_second_vocabulary(store):
    record = a_record()
    state = mirror_state(record)
    assert state == {
        "handling_class": "highly_sensitive_credential_bearing",
        "protected": True,
        "basis": "detector",
        "reliability_state": "validated",
        "content_hash": HASH_A,
        "evidence_refs": list(PASSPORT_KEYS),
        "observed_at": FIXED_CLOCK,
    }


def test_the_projection_is_json_serialisable_the_way_p1_stores_it(store):
    # P1 does `json.dumps(state, sort_keys=True)` and holds no handling-class
    # vocabulary: a class P1 has never heard of round-trips unchanged.
    state = mirror_state(a_record())
    assert json.loads(json.dumps(state, sort_keys=True)) == state


def test_the_record_stays_authoritative_and_the_column_is_the_projection(p7_conn, tmp_path, store):
    file_id = a_file(p7_conn, tmp_path)
    record = a_record(file_id=file_id)
    store.write(record)
    mirror(p7_conn, record, component_version=COMPONENT)
    # Provenance -- basis, evidence, reliability, supersede chain -- is answerable
    # from the record. The column answers only "what is this file right now".
    assert store.current(file_id, HASH_A).evidence_refs == PASSPORT_KEYS
    assert json.loads(get_file(p7_conn, file_id)["sensitivity_state"])["evidence_refs"] \
        == list(PASSPORT_KEYS)


# --- `Unreadable or unclassified` is a gate outcome, not a file fact (D2) ---

def test_an_unclassified_record_is_refused_by_the_store(store):
    # D2. Absence already says "nothing has looked"; a row saying it would be a
    # FACT claiming the same thing, and the two would then disagree.
    with pytest.raises(GateOutcomeNotAFileFact):
        store.write(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False,
                             basis="detector", evidence_refs=("obs-key-a",)))


def test_unclassified_never_reaches_the_column(store):
    with pytest.raises(GateOutcomeNotAFileFact):
        mirror_state(a_record(handling_class=UNREADABLE_UNCLASSIFIED, protected=False))


def test_no_input_makes_the_column_read_public_low(p7_conn, tmp_path, store):
    # §8.6: "Cost exhaustion must never turn into lower-quality automatic
    # classification." The failure that sentence forbids is exactly defaulting an
    # unclassified file to public so the pipeline can continue.
    file_id = a_file(p7_conn, tmp_path)
    assert get_file(p7_conn, file_id)["sensitivity_state"] is None
    assert store.current(file_id, HASH_A) is None


# --- D2's shape: no protocol, no injection, no P6 surface -------------------

def test_the_store_is_concrete_and_takes_no_injection(p7_conn):
    import privacy.classification_store as module
    assert not hasattr(module, "SensitivityFacts")
    assert not hasattr(module, "SensitivityStateWriter")
    # One constructor argument: the connection. A second would be the injection D2
    # removed.
    import inspect
    assert list(inspect.signature(ClassificationStore).parameters) == ["conn"]


def test_the_p6_stand_in_is_deleted_and_not_reimplemented(p7_conn):
    # There is no longer a P6 surface for it to stand in for (D2).
    assert not (Path(__file__).parent / "p6_fixture.py").exists()


def test_the_store_needs_no_p6_table_to_exist(p7_conn, store):
    # NEEDS-JOSEPH C5: P7's SPEC still says "P6 must accept `sensitivity` as a
    # first-class universal field" while D2 makes P7's record authoritative and
    # round 1 found that P6 field has no producer. Task 4 is built so the answer
    # does not matter: there is no `file_facts` table in this database.
    tables = {row["name"] for row in p7_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "file_facts" not in tables
    store.write(a_record())
    assert store.current("file-1", HASH_A) is not None


def test_the_store_appends_no_event(p7_conn, store):
    # C4's one job. `classification_assigned` is Task 16's, once, with a user_id.
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", basis="user",
                               evidence_refs=(), observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_whether_protected_is_the_top_two_classes_is_not_answered_here(store):
    # SPEC Open question 1, unsettled and not settled by D2. `protected` is stored,
    # never derived: SPEC §2, "Neighbouring parts should consume the `protected`
    # flag, not infer it from the class."
    low_but_protected = a_record(handling_class="personal_non_sensitive",
                                 protected=True, basis="safety_domain")
    store.write(low_but_protected)
    assert store.current("file-1", HASH_A).protected is True
    import privacy.classification_store as module
    assert not [name for name in vars(module) if "co_extensive" in name]
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_classification_store.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.classification_store'`
(neither `privacy.schema` nor `privacy.classification_store` exists yet, so collection fails on the
first import of the module under test).

- [ ] **Step 3: Write `src/privacy/schema.py`**

```python
# src/privacy/schema.py
"""P7's tables. They live inside the one local SQLite database the design names --
§0: "A local SQLite database acts as the durable working memory of the product."

One table per part is this project's CONVENTION, not a design quotation. P4's schema
module records what happened the last time that convention acquired quote marks: a
sentence nobody wrote was cited in three PLANs and one module. It is written plainly
here instead.

P1 owns the handle, the transaction boundary, `files` and `events`. P7 creates none
of them and modifies no P1 file. `create_privacy_schema` is the one entry point;
Task 5 adds `privacy_policies` to it.

One column is not a published field. P1's `mark_superseded` and `chain` are
`... WHERE record_id = ?`, and P7's published primary key is `fact_id`. `record_id`
is a VIRTUAL generated projection of it: it stores nothing, cannot diverge, does not
appear in `PRAGMA table_info`, and lets P1's tested supersede functions be reused
verbatim instead of written a second time under a second name. P4 solved this once
(`evidence.record_id`) and P7 copies the solution, not the implementation.

The table is keyed on `(file_id, content_hash)` and the index says so. D2: a
classification is about BYTES. New bytes at a path are a new file version and
inherit nothing, which is what lets "nobody has looked at these bytes" stay
distinguishable from "these bytes were found to carry nothing".
"""
from __future__ import annotations

import sqlite3

#: P7's classification table. Named here so no caller retypes the string.
CLASSIFICATIONS_TABLE = "classifications"

#: The one column that is not a published classification field. See the docstring.
SUPERSEDE_ADAPTER_COLUMN = "record_id"

CLASSIFICATIONS_DDL = f"""
CREATE TABLE IF NOT EXISTS {CLASSIFICATIONS_TABLE} (
    fact_id           TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (fact_id) VIRTUAL,
    file_id           TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    handling_class    TEXT NOT NULL,
    protected         INTEGER NOT NULL,
    basis             TEXT NOT NULL,
    evidence_refs     TEXT NOT NULL,
    reliability_state TEXT NOT NULL,
    observed_at       TEXT NOT NULL,
    supersedes        TEXT,
    superseded_by     TEXT,
    supersede_reason  TEXT
);
-- Deliberately NOT unique: an early detector and a later one may disagree and both
-- survive (§8.2's OCR example). The resolver is `ClassificationStore.current`.
CREATE INDEX IF NOT EXISTS classifications_version
    ON {CLASSIFICATIONS_TABLE} (file_id, content_hash);
CREATE INDEX IF NOT EXISTS classifications_file
    ON {CLASSIFICATIONS_TABLE} (file_id);
CREATE TRIGGER IF NOT EXISTS classifications_no_delete
BEFORE DELETE ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never removed (§8.2, §8.7)'); END;
-- Over the eight SPEC §2 fields. The three supersede columns are outside it:
-- supersession is the one legal write to an existing row.
CREATE TRIGGER IF NOT EXISTS classifications_never_overwritten
BEFORE UPDATE OF fact_id, file_id, content_hash, handling_class, protected, basis,
                 evidence_refs, reliability_state, observed_at
    ON {CLASSIFICATIONS_TABLE}
BEGIN SELECT RAISE(ABORT, 'a classification is superseded, never overwritten (§8.2)'); END;
"""


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create every P7-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(CLASSIFICATIONS_DDL)
```

- [ ] **Step 4: Write `src/privacy/classification_store.py`**

```python
# src/privacy/classification_store.py
"""P7's own classification store (D2, ratified 2026-08-21).

This module used to be `facts_seam.py`: an injected `SensitivityFacts` protocol over
a `sensitivity` fact P6 owned. D2 removed the seam. P7's `ClassificationRecord`,
keyed `(file_id, content_hash)`, is AUTHORITATIVE, so there is no P6 record to read
and nothing to inject. The four methods keep their shape -- `current`, `write`,
`supersede`, `history` -- over a table P7 creates and owns.

Three rules, each a quotation rather than a choice.

**The key is the bytes.** A classification is bound to a file VERSION (§8.2). New
bytes at a path are a new version and inherit nothing, so `current` is keyed on the
pair and returns `None` for a hash nothing has classified.

**Supersede, never overwrite (§8.2).** A revision is a new record linked through P1's
three published columns; both remain inspectable. P7 does not implement supersession,
it calls `mark_superseded` and `chain`. §3.13's ordering is P6's -- the design's own
listed order, `user confirmed`, `direct`, `validated`, `LLM-supported`, `possible`,
with `rejected` outside it -- written down once and never re-derived from a score.

**`Unreadable or unclassified` is a gate OUTCOME, not a file fact (D2).** It lives on
the release decision. It is refused here on both sides of the projection, because a
stored row saying it would claim, as a fact, exactly what the absence of a row
already says -- and the two would then be able to disagree.

This module authors nothing. C4: "a gate that also wrote would be doing two jobs."
`classification_assigned` and `classification_superseded` are appended once, by
`privacy.learning_seam.assign` and `.reclassify`, which are the entry points a
detector or a user correction calls.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Sequence

from database_agent.files_table import set_sensitivity_state
from database_agent.supersede import chain, mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.schema import CLASSIFICATIONS_TABLE

#: §3.13, in the design's own listed order, strongest first. P6's canonical
#: snake_case literals. Never sorted, never scored, never re-derived.
RELIABILITY_ORDER: tuple[str, ...] = (
    "user_confirmed", "direct", "validated", "llm_supported", "possible",
)

#: The sixth state. "A rejected fact is a proposal that the user or validator marked
#: as incorrect" -- stored, kept for §8.7's negative examples, never current.
REJECTED = "rejected"

_COLUMNS = (
    "fact_id", "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)


class AmbiguousCurrentClassification(Exception):
    """Two live records at one key and one rank. Raised, never resolved by picking."""


class UnrankedReliability(Exception):
    """A reliability state outside §3.13's six. A load error, not a fallback."""


class GateOutcomeNotAFileFact(Exception):
    """`unreadable_unclassified` was offered as a stored fact or as a projection."""


def _rank(record: ClassificationRecord) -> int:
    try:
        return RELIABILITY_ORDER.index(record.reliability_state)
    except ValueError:
        raise UnrankedReliability(
            f"{record.reliability_state!r} is not one of §3.13's ranked states "
            f"{RELIABILITY_ORDER!r}; {REJECTED!r} is stored but never current"
        ) from None


def strongest(records: Sequence[ClassificationRecord]) -> ClassificationRecord:
    """The record §3.13's listed order ranks highest. Ties raise."""
    if not records:
        raise ValueError("strongest() of no records")
    ranked = sorted(records, key=_rank)
    best = _rank(ranked[0])
    tied = [r for r in ranked if _rank(r) == best]
    if len(tied) > 1:
        raise AmbiguousCurrentClassification(
            f"{len(tied)} live classifications at reliability "
            f"{tied[0].reliability_state!r} for {tied[0].file_id!r} at "
            f"{tied[0].content_hash!r}; one must supersede the other (§8.2)"
        )
    return ranked[0]


def _row_to_record(row: sqlite3.Row) -> ClassificationRecord:
    return ClassificationRecord(
        file_id=row["file_id"],
        content_hash=row["content_hash"],
        handling_class=row["handling_class"],
        protected=bool(row["protected"]),
        basis=row["basis"],
        evidence_refs=tuple(json.loads(row["evidence_refs"])),
        reliability_state=row["reliability_state"],
        observed_at=row["observed_at"],
    )


class ClassificationStore:
    """P7's authoritative classification record (D2). Concrete; no injection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def write(self, record: ClassificationRecord) -> str:
        """Insert one record and return its `fact_id`. Appends no event (C4)."""
        if record.handling_class == UNREADABLE_UNCLASSIFIED:
            raise GateOutcomeNotAFileFact(
                f"{UNREADABLE_UNCLASSIFIED!r} is a gate outcome, not a file fact "
                "(D2): the absence of a record already says nothing has looked"
            )
        fact_id = str(uuid.uuid4())
        self._conn.execute(
            f"INSERT INTO {CLASSIFICATIONS_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (fact_id, record.file_id, record.content_hash, record.handling_class,
             int(record.protected), record.basis,
             canonical_json(list(record.evidence_refs)), record.reliability_state,
             record.observed_at),
        )
        return fact_id

    def _live_rows(self, file_id: str, content_hash: str) -> list[sqlite3.Row]:
        return list(self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} "
            "WHERE file_id = ? AND content_hash = ? AND superseded_by IS NULL "
            "  AND reliability_state <> ? "
            "ORDER BY observed_at, rowid",
            (file_id, content_hash, REJECTED),
        ))

    def current(self, file_id: str, content_hash: str) -> ClassificationRecord | None:
        """The one current classification for this file VERSION, or None."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        return strongest([_row_to_record(row) for row in rows])

    def current_fact_id(self, file_id: str, content_hash: str) -> str | None:
        """The row id `mark_superseded` needs. `ClassificationRecord` carries none."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        pairs = [(row["fact_id"], _row_to_record(row)) for row in rows]
        best = strongest([record for _, record in pairs])
        # `strongest` returns one of the objects it was given, so identity is the
        # match. Equality would collapse two byte-identical live rows into one and
        # hide the ambiguity `current` raises on.
        return next(fact_id for fact_id, record in pairs if record is best)

    def supersede(self, old_fact_id: str, new_fact_id: str, reason: str) -> None:
        """P1's three columns. P7 does not copy P1's supersede implementation."""
        mark_superseded(self._conn, CLASSIFICATIONS_TABLE,
                        old_id=old_fact_id, new_id=new_fact_id, reason=reason)

    def history(self, file_id: str) -> list[ClassificationRecord]:
        """Every classification ever written for this file, oldest first."""
        return [_row_to_record(row) for row in self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE file_id = ? "
            "ORDER BY observed_at, rowid", (file_id,))]

    def chain_for(self, fact_id: str) -> list[sqlite3.Row]:
        """P1's `chain`, exposed so a caller does not name P7's table itself."""
        return chain(self._conn, CLASSIFICATIONS_TABLE, fact_id)


def mirror_state(record: ClassificationRecord) -> dict:
    """The opaque dict P1 stores in `files.sensitivity_state` (D2's projection).

    P1 holds no handling-class vocabulary and validates nothing here; §8.4's classes
    are P7's. `file_id` is absent because it is the row's key, and `fact_id` is
    absent because it is not one of SPEC §2's eight fields -- a reader needing the
    classification's provenance reads the record, not the column.
    """
    if record.handling_class == UNREADABLE_UNCLASSIFIED:
        raise GateOutcomeNotAFileFact(
            f"{UNREADABLE_UNCLASSIFIED!r} never reaches files.sensitivity_state "
            "(D2): 'nothing has looked' must not be readable as 'this file carries "
            "nothing'"
        )
    return {
        "handling_class": record.handling_class,
        "protected": record.protected,
        "basis": record.basis,
        "reliability_state": record.reliability_state,
        "content_hash": record.content_hash,
        "evidence_refs": list(record.evidence_refs),
        "observed_at": record.observed_at,
    }


def mirror(conn: sqlite3.Connection, record: ClassificationRecord, *,
           component_version: str) -> None:
    """Project the authoritative record onto P1's column, through P1's setter.

    The single `UPDATE files` in the product's privacy path is P1's, inside
    `set_sensitivity_state`. `author` is not a parameter: M8 makes the acting part
    the author, and a log where the author is a caller-supplied value cannot answer
    §8.2's reconstruction question.
    """
    set_sensitivity_state(conn, record.file_id, state=mirror_state(record),
                          author=SUBSYSTEM, component_version=component_version)
```

- [ ] **Step 5: Add P7's schema to the `p7_conn` fixture in `tests/p7/conftest.py`**

Keep everything Task 1 put in the file; the `p7_conn` fixture gains one line.

```python
# tests/p7/conftest.py
import pytest

from database_agent.db import create_schema

from privacy.schema import create_privacy_schema


@pytest.fixture()
def p7_conn(conn):
    """P1's database with P7's tables added. `conn` is P1's root fixture and
    `tests/conftest.py` is not modified. Nothing imported across parts by name lives
    in this file: under pytest's default prepend import mode every `conftest.py` is
    the top-level module `conftest`, and the last one wins."""
    create_schema(conn)
    create_privacy_schema(conn)
    return conn
```

- [ ] **Step 6: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_classification_store.py -v`
Expected: PASS — 39 passed

- [ ] **Step 7: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–4 green, and P1–P5 still green (P7 modified no file belonging to another
part; `tests/p7/conftest.py` is P7's own).

- [ ] **Step 8: Commit**

```bash
git add src/privacy/schema.py src/privacy/classification_store.py tests/p7/conftest.py tests/p7/test_p7_classification_store.py
git commit -m "feat(P7): P7's own classification store, §3.13's ordering, and the sensitivity_state projection through P1's setter"
```

---

### Task 5: Policy — the four modes, consent grants, redaction settings, `policy_version`

**Files:**
- Create: `src/privacy/policy.py`
- Modify: `src/privacy/schema.py` (Task 4 created it; Task 5 adds one table and one line)
- Test: `tests/p7/test_p7_policy.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `.CONSENT_OPTIONS`,
  `.MODE_SEMANTICS`, `.check_mode(value) -> str`, `.OutOfVocabulary`,
  `privacy.authorship.POLICY_SET`, `.CONSENT_GRANTED`, `.SUBSYSTEM`,
  `.event_defaults(*, event_type, **fields) -> dict[str, object]`,
  `database_agent.events.append_event(conn, **fields) -> int`,
  `database_agent.db.transaction(conn)`,
  `database_agent.supersede.mark_superseded(conn, table, *, old_id, new_id, reason) -> None`,
  `evidence_shape.canonical.canonical_json(value) -> str`,
  `privacy.schema.POLICIES_TABLE`.
- Produces (`schema.py`, added):
  - `POLICIES_TABLE: str = "privacy_policies"`, `POLICIES_DDL: str`;
    `create_privacy_schema` also executes it.
- Produces (`policy.py`):
  - `SHOWN: str = "shown"`, `REDACTED: str = "redacted"`,
    `REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)` (A7).
  - `NO_MODEL_USE: str = "no_model_use"` — validated against `CONSENT_OPTIONS` at import.
  - `UNSET_POLICY_VERSION: str = ""` — what a `Policy` carries before the gate mints one.
  - `Policy` — frozen: `policy_version: str`, `operation_mode: str`,
    `consent_grants: tuple[tuple[str, str], ...]`, `redaction_settings: dict`,
    `automatic_move_permissions: dict`, `plan_version: str`, `set_at: str`.
  - `set_policy(conn, policy, *, component_version, user_id, reason) -> str`
  - `current_policy(conn, *, plan_version) -> Policy | None` (A6)
  - `policy_at(conn, policy_version) -> Policy`
  - `grant_consent(conn, policy, scope, option, *, user_id, component_version, observed_at) -> str`
  - `revoke_consent(conn, policy, scope, *, user_id, component_version, observed_at) -> str`
  - `TranscriptionAuthorization` — frozen, `scope: str`, `__call__() -> bool`.
  - `transcription_authorized_for(conn, scope, *, plan_version) -> TranscriptionAuthorization`
  - `CallerSuppliedPolicyVersion`, `UnknownPolicyVersion`, `AmbiguousCurrentPolicy`.

**Done-means:** substrate for 5, 6, 8, 12; the P5 back-edge.

**Two more deviations, on top of the table above.**

- **A14 — `set_policy` drops `author` and gains a required `reason`.** Task 1's `event_defaults`
  *"fills `subsystem = "P7"` and never lets a caller override it, because M8's 'the acting part
  authors' is unmeetable from a log where the author is a parameter anyone may set."* An `author`
  keyword on `set_policy` is exactly that parameter. `reason` replaces it because
  `mark_superseded` refuses an empty one and because §8.8 requires the diff to be *"meaningful"* —
  a fixed string held in `policy.py` would make every privacy-policy diff line read the same, and
  §8.8 calls a silent widening of egress policy the least acceptable silent change in the product.
- **A15 — `transcription_authorized_for` gains `conn` and `plan_version`.** The predicate answers
  from the policy in force, and policy is plan-scoped (§8.8). The skeleton's one-argument form
  cannot reach a policy.

**One table, not two (A9), and the reason is the binding tuple.** A consent grant that did not mint
a new `policy_version` would leave a release minted before the grant still spendable after it —
`policy_version` is a binding term (B2), and Task 12's ledger checks it. §8.8 also lists *"Privacy
and model-consent policies"* as **one** plan-version item. So a policy version is the whole snapshot:
mode, grants, redaction settings, automatic-move permissions.

**One act, one event.** `_persist` mints, inserts, supersedes and appends nothing. `set_policy` is
`_persist` plus `policy_set`; `grant_consent` is `_persist` plus `consent_granted`; **`revoke_consent`
is `_persist` and no event at all** — the `consent_revoked` append belongs to sibling Task 15's
`revoke`, which is where §8.4's `prior_releases` and `retraction_limit` are assembled, and which
reads that event back out of the log. Two appends would put one act in the log twice.

**Policy is plan-scoped; classifications and audit records are not.** §8.8: *"The evidence database
remains shared across plan versions, but the destination tree and user policy define which
projections are valid in each version."* `current_policy` takes `plan_version`;
`ClassificationStore.current` does not, and a test asserts the asymmetry by signature rather than by
comment.

**Consent-grant scoping stays parameterised.** SPEC Open question 3: *"What is a 'corpus area'?
`cloud_assisted` permits a cloud model for 'selected corpus areas' (§8.4). A scan root (§1.1)? A
frozen tree node (§5.12)? An accepted group (§4)? A domain (§3.15)? Consent grants cannot be scoped
until this is named."* `scope` is an opaque string P7 neither parses nor validates. Task 21 asserts
P7 supplies no answer.

**The P5 back-edge is an adapter over a genuine mismatch, and the test says so.**
`transcription_authorized` is `Callable[[], bool]`, called as `transcription_authorized()` in
`src/extractors/long_tail.py:204`. It takes no `file_id` and no scope; P7's surfaces are all
per-file or per-scope. `TranscriptionAuthorization` closes over the scope and **carries it as a
field**, so the scope P5 cannot pass is visible on the object rather than hidden inside a lambda.
**Which of the four consent options authorizes speech-to-text is not stated anywhere in the design.**
§2.9 requires *"only under an explicit privacy and compute policy"*. The rule used is the narrowest
one expressible in the vocabulary P7 owns — an **explicit** grant naming the scope, whose option is
anything other than `no_model_use` — and it is reported as a reading, not a ratification.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_policy.py
"""§8.4's four operation modes, its consent options, its five configurable redaction
facets, and the `policy_version` the gate mints.

W1 is NOT here. This file never asserts what the resolved default is, because
`policy.py` holds no default: `current_policy` returns `None` when nothing has been
set and Task 6 is what turns that into §8.4's local-first floor. A default living in
two modules is a default that can disagree with itself, and the one it would disagree
about is whether content leaves the device.
"""
from __future__ import annotations

import inspect
import json
import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from extractors.dispatch import extract

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, SUBSYSTEM
from privacy.classification_store import ClassificationStore
from privacy.policy import (
    NO_MODEL_USE,
    REDACTED,
    REDACTION_VALUES,
    SHOWN,
    UNSET_POLICY_VERSION,
    AmbiguousCurrentPolicy,
    CallerSuppliedPolicyVersion,
    Policy,
    TranscriptionAuthorization,
    UnknownPolicyVersion,
    current_policy,
    grant_consent,
    policy_at,
    revoke_consent,
    set_policy,
    transcription_authorized_for,
)
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    OPERATION_MODES,
    OutOfVocabulary,
)

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
LATER = "2026-08-22T18:30:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

ALL_REDACTED = {facet: REDACTED for facet in DISPLAY_FACETS}


def a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="local_model",
                consent_grants=(), redaction_settings=dict(ALL_REDACTED),
                automatic_move_permissions={}, plan_version=PLAN, set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def store(conn, **over) -> str:
    return set_policy(conn, a_policy(**over), component_version=COMPONENT,
                      user_id="joseph", reason="the user chose local-model mode")


# --- the table -------------------------------------------------------------

def test_the_policy_table_carries_p1s_three_supersede_columns(p7_conn):
    columns = {row["name"] for row in p7_conn.execute(
        f"PRAGMA table_info({POLICIES_TABLE})")}
    assert set(SUPERSEDE_COLUMNS) <= columns


def test_a_policy_row_cannot_be_deleted(p7_conn):
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(f"DELETE FROM {POLICIES_TABLE} WHERE policy_version = ?",
                        (version,))


def test_a_policy_row_cannot_be_overwritten(p7_conn):
    # §8.8's diff needs both sides. A mutated policy row is a diff with one side.
    version = store(p7_conn)
    with pytest.raises(sqlite3.IntegrityError, match="superseded"):
        p7_conn.execute(
            f"UPDATE {POLICIES_TABLE} SET operation_mode = ? WHERE policy_version = ?",
            ("cloud_assisted", version))


# --- the gate mints the version --------------------------------------------

def test_the_gate_mints_the_policy_version(p7_conn):
    # SPEC §6: "the gate owns the policy, so the caller does not supply this value,
    # it echoes it."
    version = store(p7_conn)
    assert isinstance(version, str) and version != UNSET_POLICY_VERSION


def test_a_caller_supplied_policy_version_is_refused(p7_conn):
    with pytest.raises(CallerSuppliedPolicyVersion):
        set_policy(p7_conn, a_policy(policy_version="policy-i-picked"),
                   component_version=COMPONENT, user_id="joseph", reason="because")


def test_two_policies_never_share_a_version(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    assert first != second


def test_policy_at_returns_the_policy_that_was_set(p7_conn):
    version = store(p7_conn, operation_mode="offline")
    loaded = policy_at(p7_conn, version)
    assert loaded.policy_version == version
    assert loaded.operation_mode == "offline"
    assert loaded.redaction_settings == ALL_REDACTED
    assert loaded.plan_version == PLAN


def test_an_unknown_policy_version_raises(p7_conn):
    with pytest.raises(UnknownPolicyVersion):
        policy_at(p7_conn, "policy-never-minted")


def test_current_policy_is_none_before_anything_is_set(p7_conn):
    # A6. "No policy has been set" is a fact, and it is Task 6's input, not an
    # occasion for `policy.py` to invent one.
    assert current_policy(p7_conn, plan_version=PLAN) is None


# --- supersede, never mutate -----------------------------------------------

def test_a_policy_change_supersedes_the_prior_policy(p7_conn):
    first = store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER)
    row = p7_conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?", (first,)).fetchone()
    assert row["superseded_by"] == second
    assert row["supersede_reason"]
    assert current_policy(p7_conn, plan_version=PLAN).policy_version == second


def test_the_prior_policy_remains_readable(p7_conn):
    first = store(p7_conn)
    store(p7_conn, operation_mode="offline", set_at=LATER)
    # §8.5 replay reproduces "the policy in force at each call", so a superseded
    # policy version must stay loadable by name forever.
    assert policy_at(p7_conn, first).operation_mode == "local_model"


def test_a_policy_change_appends_policy_set_once(p7_conn):
    store(p7_conn)
    rows = p7_conn.execute("SELECT * FROM events WHERE event_type = ?",
                           (POLICY_SET,)).fetchall()
    assert len(rows) == 1
    assert rows[0]["subsystem"] == SUBSYSTEM == "P7"
    assert rows[0]["user_id"] == "joseph"


def test_the_policy_set_explanation_carries_a_diffable_policy(p7_conn):
    # §8.8 requires a privacy-policy change to appear as a first-class diff line.
    # The explanation carries both sides and the reason, so the diff is a read of
    # the log rather than a recomputation from two snapshots.
    store(p7_conn)
    second = store(p7_conn, operation_mode="offline", set_at=LATER,
                   consent_grants=(("Academics", "cloud_model"),))
    payload = json.loads(p7_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ? ORDER BY event_id DESC",
        (POLICY_SET,)).fetchone()["explanation"])
    assert payload["policy_version"] == second
    assert payload["operation_mode"] == "offline"
    assert payload["superseded_policy_version"]
    assert payload["consent_grants"] == [["Academics", "cloud_model"]]
    assert payload["reason"]


def test_two_live_policies_at_one_plan_version_raise_rather_than_pick(p7_conn):
    store(p7_conn)
    p7_conn.execute(
        f"INSERT INTO {POLICIES_TABLE} (policy_version, plan_version, operation_mode,"
        " consent_grants, redaction_settings, automatic_move_permissions, set_at)"
        " VALUES (?,?,?,?,?,?,?)",
        ("policy-smuggled", PLAN, "cloud_assisted", "[]", "{}", "{}", LATER))
    with pytest.raises(AmbiguousCurrentPolicy):
        current_policy(p7_conn, plan_version=PLAN)


# --- plan scoping ----------------------------------------------------------

def test_policy_is_plan_scoped(p7_conn):
    store(p7_conn)
    assert current_policy(p7_conn, plan_version="plan-2") is None


def test_each_plan_version_carries_its_own_current_policy(p7_conn):
    store(p7_conn, operation_mode="offline")
    store(p7_conn, operation_mode="local_model", plan_version="plan-2", set_at=LATER)
    assert current_policy(p7_conn, plan_version=PLAN).operation_mode == "offline"
    assert current_policy(p7_conn, plan_version="plan-2").operation_mode == "local_model"


def test_classifications_are_not_plan_scoped(p7_conn):
    # §8.8: "The evidence database remains shared across plan versions." Asserted by
    # signature, so a later plan_version parameter on the store is a failing test.
    assert "plan_version" not in inspect.signature(ClassificationStore.current).parameters
    assert "plan_version" in inspect.signature(current_policy).parameters


# --- the four modes --------------------------------------------------------

def test_policy_holds_no_second_list_of_modes(p7_conn):
    import privacy.policy as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert not [text for text in held if text in OPERATION_MODES]


def test_every_mode_in_the_vocabulary_is_settable(p7_conn):
    for index, mode in enumerate(OPERATION_MODES):
        version = store(p7_conn, operation_mode=mode, plan_version=f"plan-{index}")
        assert policy_at(p7_conn, version).operation_mode == mode


def test_a_mode_outside_the_vocabulary_is_a_load_error(p7_conn):
    # SPEC §1: "A value outside this set is a load error, not a fallback."
    with pytest.raises(OutOfVocabulary):
        a_policy(operation_mode="mostly_offline")


# --- redaction settings ----------------------------------------------------

def test_the_two_redaction_values_are_the_specs_own(p7_conn):
    # SPEC §10: "names | previews | thumbnails | ocr_text | location_data
    #            each shown | redacted".
    assert REDACTION_VALUES == ("shown", "redacted") == (SHOWN, REDACTED)


def test_an_unknown_facet_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={"filenames": REDACTED})


def test_an_unknown_redaction_value_is_a_load_error(p7_conn):
    with pytest.raises(OutOfVocabulary):
        a_policy(redaction_settings={DISPLAY_FACETS[0]: "blurred"})


def test_a_partial_redaction_map_is_accepted_and_left_to_task_6(p7_conn):
    # The migrated-from-nothing case. Refusing it here would make W1 unreachable:
    # Task 6's job is to fill an absent facet with its more redacting value, and it
    # cannot fill what `Policy` refuses to hold.
    partial = a_policy(redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    assert set(partial.redaction_settings) == {DISPLAY_FACETS[0]}


def test_the_five_facets_are_task_2s_and_policy_names_no_sixth(p7_conn):
    assert len(DISPLAY_FACETS) == 5
    version = store(p7_conn, redaction_settings=dict(ALL_REDACTED))
    assert set(policy_at(p7_conn, version).redaction_settings) == set(DISPLAY_FACETS)


# --- consent grants --------------------------------------------------------

def test_grant_consent_mints_a_new_version_carrying_the_grant(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    second = grant_consent(p7_conn, first, "Academics", "cloud_model",
                           user_id="joseph", component_version=COMPONENT,
                           observed_at=LATER)
    assert second != first.policy_version
    assert policy_at(p7_conn, second).consent_grants == (("Academics", "cloud_model"),)
    # The grant is why the version changes: a release minted under `first` must not
    # survive into a policy it was not authorized under (B2's binding tuple).
    assert policy_at(p7_conn, first.policy_version).consent_grants == ()


def test_grant_consent_appends_consent_granted_once_and_no_policy_set(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    granted = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                              (CONSENT_GRANTED,)).fetchone()["c"]
    policies = p7_conn.execute("SELECT count(*) c FROM events WHERE event_type = ?",
                               (POLICY_SET,)).fetchone()["c"]
    assert (granted, policies) == (1, 1)      # the 1 policy_set is the initial set


def test_an_option_outside_the_four_is_a_load_error(p7_conn):
    first = policy_at(p7_conn, store(p7_conn))
    with pytest.raises(OutOfVocabulary):
        grant_consent(p7_conn, first, "Academics", "cloud_model_but_only_tuesdays",
                      user_id="joseph", component_version=COMPONENT, observed_at=LATER)


def test_the_four_options_are_84s_own(p7_conn):
    # §8.4: the user should "choose whether to allow a local model, a cloud model, a
    # redacted prompt, or no model use."
    assert CONSENT_OPTIONS == ("local_model", "cloud_model", "redacted_prompt",
                               "no_model_use")


def test_revoke_consent_removes_the_grant_and_mints_a_version(p7_conn):
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    granted = policy_at(p7_conn, grant_consent(
        p7_conn, first, "Academics", "cloud_model", user_id="joseph",
        component_version=COMPONENT, observed_at=LATER))
    revoked = revoke_consent(p7_conn, granted, "Academics", user_id="joseph",
                             component_version=COMPONENT, observed_at=LATER)
    assert policy_at(p7_conn, revoked).consent_grants == ()
    assert policy_at(p7_conn, granted.policy_version).consent_grants == \
        (("Academics", "cloud_model"),)


def test_revoke_consent_appends_no_event(p7_conn):
    # Sibling Task 15 pins this: `consent_revoked` is appended once, by `revoke`,
    # which is where §8.4's prior-release list and retraction limit are assembled.
    # Two appends would put one act in the log twice and §8.4's `prior_releases` is
    # read back out of that log.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    revoke_consent(p7_conn, first, "Academics", user_id="joseph",
                   component_version=COMPONENT, observed_at=LATER)
    assert p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


def test_the_scope_is_opaque_and_p7_defines_no_corpus_area(p7_conn):
    # SPEC Open question 3, held: "Consent grants cannot be scoped until this is
    # named." A scan root, a frozen node, an accepted group and a domain are all
    # accepted, unparsed, because P7 has no basis to prefer one.
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    for scope in ("/Users/j/Corpus", "node-17", "group-4", "Finance"):
        first = policy_at(p7_conn, grant_consent(
            p7_conn, first, scope, "cloud_model", user_id="joseph",
            component_version=COMPONENT, observed_at=LATER))
    assert [grant[0] for grant in first.consent_grants] == \
        ["/Users/j/Corpus", "node-17", "group-4", "Finance"]


# --- the P5 back-edge (M10) ------------------------------------------------

def test_the_adapter_satisfies_p5s_zero_argument_predicate(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert isinstance(predicate, TranscriptionAuthorization)
    assert inspect.signature(predicate).parameters == {}
    assert predicate() is False


def test_the_adapter_carries_the_scope_p5_cannot_pass(p7_conn):
    # The mismatch is REPORTED, not patched: P5's call site is
    # `transcription_authorized()` with no arguments, so the scope has to live on
    # the object. A lambda would hide it.
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate.scope == "Academics"


def test_p5s_call_site_takes_no_scope(p7_conn):
    # Asserted against P5 as shipped, so the day P5's signature widens this test
    # fails and the adapter can be deleted rather than quietly kept.
    parameter = inspect.signature(extract).parameters["transcription_authorized"]
    assert "Callable[[], bool]" in str(parameter.annotation)


def test_an_explicit_grant_authorizes_and_absence_does_not(p7_conn):
    # §2.9: speech-to-text runs "only under an explicit privacy and compute policy".
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False
    grant_consent(p7_conn, first, "Academics", "local_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is True
    assert transcription_authorized_for(p7_conn, "Finance", plan_version=PLAN)() \
        is False


def test_no_model_use_does_not_authorize(p7_conn):
    assert NO_MODEL_USE in CONSENT_OPTIONS
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", NO_MODEL_USE, user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)() \
        is False


def test_the_adapter_reads_the_policy_in_force_and_caches_nothing(p7_conn):
    predicate = transcription_authorized_for(p7_conn, "Academics", plan_version=PLAN)
    assert predicate() is False
    first = policy_at(p7_conn, store(p7_conn, operation_mode="cloud_assisted"))
    grant_consent(p7_conn, first, "Academics", "cloud_model", user_id="joseph",
                  component_version=COMPONENT, observed_at=LATER)
    assert predicate() is True
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_policy.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.policy'` (collection fails on the
first import of the module under test).

- [ ] **Step 3: Add `privacy_policies` to `src/privacy/schema.py`**

Append the DDL and add one line to `create_privacy_schema`. Everything Task 4 wrote stays.

```python
#: P7's policy table. One row per policy VERSION; a change supersedes, never mutates.
POLICIES_TABLE = "privacy_policies"

POLICIES_DDL = f"""
CREATE TABLE IF NOT EXISTS {POLICIES_TABLE} (
    policy_version             TEXT PRIMARY KEY,
    {SUPERSEDE_ADAPTER_COLUMN} TEXT GENERATED ALWAYS AS (policy_version) VIRTUAL,
    plan_version               TEXT NOT NULL,
    operation_mode             TEXT NOT NULL,
    consent_grants             TEXT NOT NULL,
    redaction_settings         TEXT NOT NULL,
    automatic_move_permissions TEXT NOT NULL,
    set_at                     TEXT NOT NULL,
    supersedes                 TEXT,
    superseded_by              TEXT,
    supersede_reason           TEXT
);
CREATE INDEX IF NOT EXISTS privacy_policies_plan
    ON {POLICIES_TABLE} (plan_version);
CREATE TRIGGER IF NOT EXISTS privacy_policies_no_delete
BEFORE DELETE ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never removed (§8.2, §8.5 replay)'); END;
-- §8.8's diff needs both sides. The three supersede columns stay writable.
CREATE TRIGGER IF NOT EXISTS privacy_policies_never_overwritten
BEFORE UPDATE OF policy_version, plan_version, operation_mode, consent_grants,
                 redaction_settings, automatic_move_permissions, set_at
    ON {POLICIES_TABLE}
BEGIN SELECT RAISE(ABORT, 'a policy is superseded, never overwritten (§8.2, §8.8)'); END;
"""


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create every P7-owned table. Idempotent. P1's `create_schema` runs first."""
    conn.executescript(CLASSIFICATIONS_DDL)
    conn.executescript(POLICIES_DDL)
```

- [ ] **Step 4: Write `src/privacy/policy.py`**

```python
# src/privacy/policy.py
"""§8.4's operation modes, consent grants and redaction settings, as one versioned
policy record.

**One policy version is the whole snapshot.** §8.8 lists "Privacy and model-consent
policies" as a single plan-version item, and B2 makes `policy_version` a binding term
of every release. A consent grant that did not mint a new version would leave a
release minted before the grant still spendable after it, which is the one silent
widening of egress policy §8.8 calls the least acceptable silent change in the
product. So mode, grants, redaction settings and automatic-move permissions travel
together and a change to any of them is a new version.

**The gate mints the version; the caller echoes it.** SPEC §6. A `Policy` handed in
carries `UNSET_POLICY_VERSION` and is refused if it carries anything else.

**Supersede, never mutate (§8.2).** The prior version stays loadable by name forever,
because §8.5 replay must reproduce "the policy in force at each call".

**One act, one event.** `_persist` appends nothing. `set_policy` adds `policy_set`;
`grant_consent` adds `consent_granted`; `revoke_consent` adds NOTHING -- the
`consent_revoked` append belongs to `privacy.revocation.revoke`, which assembles
§8.4's prior-release list and retraction limit and reads that event back out of the
log.

**This module holds no default.** §8.4's local-first `must` is W1 and lives in
`privacy.defaults`. `current_policy` returns `None` when nothing has been set. A
default in two modules is a default that can disagree with itself, and the thing it
would disagree about is whether content leaves the device.

**`scope` is opaque.** SPEC Open question 3 -- "What is a 'corpus area'?" -- is open,
so a scan root, a frozen node id, a group id and a domain name are all accepted,
unparsed. P7 has no basis to prefer one and does not invent it.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, replace

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.supersede import mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, event_defaults
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    OutOfVocabulary,
    check_mode,
)

#: SPEC §10: "names | previews | thumbnails | ocr_text | location_data -- each
#: shown | redacted". Two values, named once. Reported to Task 2's author: if
#: `vocabulary.py` adopts them, this module re-exports and deletes its own.
SHOWN = "shown"
REDACTED = "redacted"
REDACTION_VALUES: tuple[str, str] = (SHOWN, REDACTED)

#: The consent option that authorizes nothing. Named so `transcription_authorized_for`
#: does not index into a tuple, and validated at import so it cannot drift from
#: Task 2's vocabulary.
NO_MODEL_USE = "no_model_use"
if NO_MODEL_USE not in CONSENT_OPTIONS:
    raise ImportError(
        f"{NO_MODEL_USE!r} is not one of §8.4's four consent options "
        f"{CONSENT_OPTIONS!r}; a value outside the set is a load error"
    )

#: What a `Policy` carries before the gate mints one (SPEC §6).
UNSET_POLICY_VERSION = ""

_COLUMNS = (
    "policy_version", "plan_version", "operation_mode", "consent_grants",
    "redaction_settings", "automatic_move_permissions", "set_at",
)


class CallerSuppliedPolicyVersion(Exception):
    """The gate owns the policy version; a caller offered one (SPEC §6)."""


class UnknownPolicyVersion(Exception):
    """No policy was ever minted under that version."""


class AmbiguousCurrentPolicy(Exception):
    """Two live policies at one plan version. Raised, never resolved by picking."""


@dataclass(frozen=True)
class Policy:
    """§8.4's authorizing policy: the mode, the grants, and the redaction settings.

    `redaction_settings` may be PARTIAL. Filling an absent facet with its more
    redacting value is W1's job (`privacy.defaults`), and a `Policy` that refused a
    partial map would make the migrated-from-nothing case unreachable.
    """

    policy_version: str
    operation_mode: str
    consent_grants: tuple[tuple[str, str], ...]
    redaction_settings: dict
    automatic_move_permissions: dict
    plan_version: str
    set_at: str

    def __post_init__(self) -> None:
        check_mode(self.operation_mode)
        for facet, value in self.redaction_settings.items():
            if facet not in DISPLAY_FACETS:
                raise OutOfVocabulary(
                    f"{facet!r} is not one of §8.4's five configurable facets "
                    f"{DISPLAY_FACETS!r}")
            if value not in REDACTION_VALUES:
                raise OutOfVocabulary(
                    f"{value!r} is not one of {REDACTION_VALUES!r} for facet {facet!r}")
        for scope, option in self.consent_grants:
            if option not in CONSENT_OPTIONS:
                raise OutOfVocabulary(
                    f"{option!r} is not one of §8.4's four consent options "
                    f"{CONSENT_OPTIONS!r} (scope {scope!r})")
        for scope, permitted in self.automatic_move_permissions.items():
            if not isinstance(permitted, bool):
                raise OutOfVocabulary(
                    f"automatic-move permission for {scope!r} is {permitted!r}; "
                    "§8.4 permits or does not permit, and nothing between")


def _row_to_policy(row: sqlite3.Row) -> Policy:
    return Policy(
        policy_version=row["policy_version"],
        operation_mode=row["operation_mode"],
        consent_grants=tuple(tuple(pair) for pair in
                             json.loads(row["consent_grants"])),
        redaction_settings=json.loads(row["redaction_settings"]),
        automatic_move_permissions=json.loads(row["automatic_move_permissions"]),
        plan_version=row["plan_version"],
        set_at=row["set_at"],
    )


def _live_row(conn: sqlite3.Connection, plan_version: str) -> sqlite3.Row | None:
    rows = list(conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} "
        "WHERE plan_version = ? AND superseded_by IS NULL ORDER BY set_at, rowid",
        (plan_version,)))
    if len(rows) > 1:
        raise AmbiguousCurrentPolicy(
            f"{len(rows)} live policies at plan version {plan_version!r}; "
            "one must supersede the other (§8.2)")
    return rows[0] if rows else None


def _persist(conn: sqlite3.Connection, policy: Policy, *,
             supersede_reason: str) -> str:
    """Mint a version, insert the row, supersede the prior one. Appends no event."""
    if policy.policy_version != UNSET_POLICY_VERSION:
        raise CallerSuppliedPolicyVersion(
            f"policy_version {policy.policy_version!r} was supplied by the caller; "
            "the gate owns the policy and the caller echoes it (SPEC §6)")
    version = f"policy-{uuid.uuid4().hex}"
    with transaction(conn):
        prior = _live_row(conn, policy.plan_version)
        conn.execute(
            f"INSERT INTO {POLICIES_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (version, policy.plan_version, policy.operation_mode,
             canonical_json([list(pair) for pair in policy.consent_grants]),
             canonical_json(policy.redaction_settings),
             canonical_json(policy.automatic_move_permissions), policy.set_at),
        )
        if prior is not None:
            mark_superseded(conn, POLICIES_TABLE, old_id=prior["policy_version"],
                            new_id=version, reason=supersede_reason)
    return version


def _explanation(conn: sqlite3.Connection, version: str, **extra) -> str:
    policy = policy_at(conn, version)
    prior = conn.execute(
        f"SELECT supersedes FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (version,)).fetchone()["supersedes"]
    payload = {
        "policy_version": version,
        "superseded_policy_version": prior,
        "plan_version": policy.plan_version,
        "operation_mode": policy.operation_mode,
        "consent_grants": [list(pair) for pair in policy.consent_grants],
        "redaction_settings": policy.redaction_settings,
        "automatic_move_permissions": policy.automatic_move_permissions,
    }
    payload.update(extra)
    return canonical_json(payload)


def set_policy(conn: sqlite3.Connection, policy: Policy, *,
               component_version: str, user_id: str, reason: str) -> str:
    """Mint and record a policy version, and append §8.4's `policy_set` event.

    `reason` is required and is the caller's: §8.8 requires the plan diff to be
    "meaningful", and a fixed sentence held here would make every privacy-policy
    diff line read the same. There is no `author` parameter -- M8 makes the acting
    part the author, and a log where the author is a caller-supplied value cannot
    answer §8.2's reconstruction question.
    """
    if not reason.strip():
        raise ValueError("a policy change carries a reason (§8.2, §8.8)")
    version = _persist(conn, policy, supersede_reason=reason)
    append_event(conn, **event_defaults(
        event_type=POLICY_SET, user_id=user_id, observed_at=policy.set_at,
        component_version=component_version,
        explanation=_explanation(conn, version, reason=reason)))
    return version


def current_policy(conn: sqlite3.Connection, *, plan_version: str) -> Policy | None:
    """The policy in force for this plan version, or None if none has been set.

    None is a fact, not a gap: §8.4's local-first floor is W1's and lives in
    `privacy.defaults`, which is what turns None into a resolved posture.
    """
    row = _live_row(conn, plan_version)
    return None if row is None else _row_to_policy(row)


def policy_at(conn: sqlite3.Connection, policy_version: str) -> Policy:
    """Any policy version, superseded or not. §8.5 replay reads through this."""
    row = conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (policy_version,)).fetchone()
    if row is None:
        raise UnknownPolicyVersion(policy_version)
    return _row_to_policy(row)


def grant_consent(conn: sqlite3.Connection, policy: Policy, scope: str, option: str,
                  *, user_id: str, component_version: str, observed_at: str) -> str:
    """Add one §8.4 consent grant, as a new policy version. Appends `consent_granted`."""
    if option not in CONSENT_OPTIONS:
        raise OutOfVocabulary(
            f"{option!r} is not one of §8.4's four consent options {CONSENT_OPTIONS!r}")
    grants = tuple(pair for pair in policy.consent_grants if pair[0] != scope)
    revised = replace(policy, policy_version=UNSET_POLICY_VERSION,
                      consent_grants=grants + ((scope, option),), set_at=observed_at)
    version = _persist(conn, revised, supersede_reason=canonical_json(
        {"act": "consent_granted", "scope": scope, "option": option}))
    append_event(conn, **event_defaults(
        event_type=CONSENT_GRANTED, user_id=user_id, observed_at=observed_at,
        component_version=component_version,
        explanation=_explanation(conn, version, granted_scope=scope,
                                 granted_option=option)))
    return version


def revoke_consent(conn: sqlite3.Connection, policy: Policy, scope: str, *,
                   user_id: str, component_version: str, observed_at: str) -> str:
    """Withdraw every grant at `scope` and return the new policy version.

    **Appends no event.** `privacy.revocation.revoke` appends `consent_revoked`
    once, because that is where §8.4's prior-release list and retraction limit are
    assembled and where the event is read back out of the log. `user_id` is on the
    signature because it is the acting user and `revoke` carries it into the event.
    """
    revised = replace(
        policy, policy_version=UNSET_POLICY_VERSION, set_at=observed_at,
        consent_grants=tuple(p for p in policy.consent_grants if p[0] != scope))
    return _persist(conn, revised, supersede_reason=canonical_json(
        {"act": "consent_revoked", "scope": scope, "user_id": user_id,
         "component_version": component_version}))


@dataclass(frozen=True)
class TranscriptionAuthorization:
    """P5's `Callable[[], bool]`, with the scope P5's call site cannot pass.

    `src/extractors/long_tail.py:204` calls `transcription_authorized()` with no
    arguments. P7's surfaces are per-file or per-scope, so the scope has to be
    closed over -- and it is carried as a FIELD rather than captured in a lambda so
    the mismatch stays visible to a reader and to a test.
    """

    conn: sqlite3.Connection
    scope: str
    plan_version: str

    def __call__(self) -> bool:
        policy = current_policy(self.conn, plan_version=self.plan_version)
        if policy is None:
            return False
        return any(scope == self.scope and option != NO_MODEL_USE
                   for scope, option in policy.consent_grants)


def transcription_authorized_for(conn: sqlite3.Connection, scope: str, *,
                                 plan_version: str) -> TranscriptionAuthorization:
    """§2.9's speech-to-text authorization, as P5's zero-argument predicate (M10).

    §2.9 permits transcripts "only under an explicit privacy and compute policy".
    **Which of the four consent options authorizes speech-to-text is not stated
    anywhere in the design.** The rule here is the narrowest one expressible in the
    vocabulary P7 owns -- an explicit grant naming this scope, whose option is
    anything other than `no_model_use` -- and it is a reported reading, not a
    ratification.
    """
    return TranscriptionAuthorization(conn, scope, plan_version)
```

- [ ] **Step 5: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_policy.py -v`
Expected: PASS — 38 passed

- [ ] **Step 6: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–5 green, and P1–P5 still green.

- [ ] **Step 7: Commit**

```bash
git add src/privacy/policy.py src/privacy/schema.py tests/p7/test_p7_policy.py
git commit -m "feat(P7): the four operation modes, consent grants, redaction settings, and a gate-minted policy_version"
```

---

### Task 6: The local-first default (W1)

**Files:**
- Create: `src/privacy/defaults.py`
- Test: `tests/p7/test_p7_defaults.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.OPERATION_MODES`, `.DISPLAY_FACETS`, `.check_mode(value) -> str`,
  `.OutOfVocabulary`, `privacy.policy.Policy`, `.current_policy(conn, *, plan_version)
  -> Policy | None`, `.REDACTED`, `.SHOWN`, `.REDACTION_VALUES`, `.UNSET_POLICY_VERSION`.
- Produces (`defaults.py`):
  - `OFFLINE: str = "offline"`, `LOCAL_MODEL: str = "local_model"` — each validated through
    `check_mode` at import, so neither can drift from Task 2's vocabulary.
  - `LOCAL_FIRST_MODES: tuple[str, str] = (OFFLINE, LOCAL_MODEL)`
  - `MORE_REDACTING: Mapping[str, str]` — every facet in `DISPLAY_FACETS` → `REDACTED`.
  - `resolve_default_policy(stored, *, install_mode, plan_version, set_at) -> Policy` (A10)
  - `effective_policy(conn, *, plan_version, install_mode, set_at) -> Policy` (A16)
  - `assert_local_first(policy) -> None`
  - `DefaultPostureViolation`

**Done-means:** 12.

**A16 — `effective_policy` is added, and it is the function the gate calls.** The skeleton's
`Consumes` block lists `policy.current_policy` and its `Produces` block lists nothing that reads a
connection, so the composition — read the stored policy, resolve the absent parts — has no home. It
is one line and it is what Task 13 needs; without it every caller would compose it again and each
composition would be a place the floor could be forgotten.

**`install_mode` is a required keyword and it is the whole design of this task (A10).** SPEC
Contract out §5: *"Which of `offline` and `local_model` ships is still open (Open question 11) and
P7 will not guess it; what is closed is that the answer cannot be `hybrid` or `cloud_assisted`, and
that no build configuration, first-run flow, or migration may set one of those as the state a user
arrives at without choosing it."* A required keyword validated against `LOCAL_FIRST_MODES` is that
sentence made mechanical: `src/privacy/` holds **no default mode at all**, so Open question 11 is
structurally open rather than open by discipline, and the two modes it forbids are unreachable
through this door.

**W1 binds the DEFAULT, never the choice.** §8.4's `must` — *"The default posture must therefore be
local-first and data-minimizing"* — constrains what a user finds on install, not what they may pick
afterwards. So `resolve_default_policy` returns a stored `cloud_assisted` policy **unchanged**;
`assert_local_first` on that same policy raises. Those are two different questions and one test
proves they are, because collapsing them would either forbid a mode §8.4 explicitly offers or let
an install ship one it forbids.

**The more-redacting rule is the second half of the same `must`, and §8.4 settles its direction.**
*"A summary such as '11 protected identity records' may be safe to show, while a visible list of
passport filenames on a shared screen may not be."* The aggregate is the default; the expansion is
the user's act. Between `shown` and `redacted` the more redacting value is `redacted`, for every one
of §8.4's five configurable facets. An absent facet is filled; a facet the user set is left alone.
`consent_grants` defaults to nothing granted and `automatic_move_permissions` to nothing permitted —
§8.4: protected material *"should not be moved automatically without a user policy that explicitly
permits it"*, and an empty map explicitly permits nothing.

**The negative half is asserted by runtime introspection, not by grep, and the skeleton says why.**
Done-means 12 says *"by fixture and by grep over the shipped defaults"*; the skeleton overrides
that, because `hybrid` and `cloud_assisted` appear legitimately in `vocabulary.py`, in docstrings
and in denial messages, and *"a text scan would either pass vacuously or fail on a comment."* The
guard here walks every module under `src/privacy/`, skips any object that **is** one of
`vocabulary.py`'s own — identity, not name, so a re-export of `OPERATION_MODES` is not a false
positive — and asserts no remaining module-level value names either mode. It also asserts
`defaults.py` binds no configuration reader at all, which is what makes *"no build flag, packaged
configuration file, or first-run flow"* checkable rather than aspirational.

**This test does not assert which of the two ships.** Open question 11 stays open; both are accepted
and a test says so by name.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_defaults.py
"""Done-means 12 — §8.4's local-first `must` (W1), and the negative half that matters
more than the positive one.

The positive half: with no user configuration present, the resolved mode is one of
the two under which no content leaves the device, and every configurable redaction
setting resolves to its more redacting value.

The negative half: no code path, build flag, packaged configuration file or first-run
flow produces a starting mode of `hybrid` or `cloud_assisted`. Asserted by calling
the resolver over every reachable stored state and by walking the package's
module-level namespaces at run time -- not by grepping source text, because both mode
names appear legitimately in `vocabulary.py`, in docstrings and in denial messages,
and a text scan would either pass vacuously or fail on a comment.

What this file must NOT assert: which of `offline` and `local_model` ships. That is
SPEC Open question 11 and P7 will not guess it.
"""
from __future__ import annotations

import importlib
import pkgutil

import pytest

import privacy
import privacy.vocabulary as vocab
from privacy.defaults import (
    LOCAL_FIRST_MODES,
    LOCAL_MODEL,
    MORE_REDACTING,
    OFFLINE,
    DefaultPostureViolation,
    assert_local_first,
    effective_policy,
    resolve_default_policy,
)
from privacy.policy import (
    REDACTED,
    SHOWN,
    UNSET_POLICY_VERSION,
    Policy,
    set_policy,
)
from privacy.vocabulary import DISPLAY_FACETS, OPERATION_MODES, OutOfVocabulary

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN = "plan-1"

#: The two names §8.4 forbids as a DEFAULT. Both remain modes a user may choose.
CLOUD_MODES = ("hybrid", "cloud_assisted")


def resolved(stored=None, *, install_mode=OFFLINE) -> Policy:
    return resolve_default_policy(stored, install_mode=install_mode,
                                  plan_version=PLAN, set_at=FIXED_CLOCK)


def a_stored_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={facet: REDACTED for facet in DISPLAY_FACETS},
                automatic_move_permissions={"Academics": True}, plan_version=PLAN,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


# --- the two modes under which nothing leaves the device --------------------

def test_the_two_local_first_modes_are_the_two_that_send_nothing(p7_conn):
    # §8.4: "Fully offline mode: No content leaves the device; only local rules and
    # local models may run." / "Local-model mode: Local extraction plus a
    # user-installed local LLM for eligible dossiers." The other two both permit a
    # cloud model, which is the posture §8.4 forbids as a DEFAULT.
    assert LOCAL_FIRST_MODES == (OFFLINE, LOCAL_MODEL) == ("offline", "local_model")
    assert set(LOCAL_FIRST_MODES) < set(OPERATION_MODES)
    assert set(OPERATION_MODES) - set(LOCAL_FIRST_MODES) == set(CLOUD_MODES)


def test_the_local_mode_names_are_task_2s_and_not_a_second_spelling(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert vocab.check_mode(mode) == mode


def test_more_redacting_covers_every_facet(p7_conn):
    # §8.4's five configurable facets: "names, previews, thumbnails, OCR text, or
    # location data".
    assert set(MORE_REDACTING) == set(DISPLAY_FACETS)
    assert set(MORE_REDACTING.values()) == {REDACTED}
    assert SHOWN not in MORE_REDACTING.values()


# --- fresh install ----------------------------------------------------------

def test_a_fresh_install_resolves_to_the_named_local_mode(p7_conn):
    assert resolved(None, install_mode=OFFLINE).operation_mode == OFFLINE
    assert resolved(None, install_mode=LOCAL_MODEL).operation_mode == LOCAL_MODEL


def test_a_fresh_install_redacts_every_facet(p7_conn):
    assert resolved(None).redaction_settings == dict(MORE_REDACTING)


def test_a_fresh_install_grants_nothing_and_permits_no_automatic_move(p7_conn):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." An empty map permits nothing explicitly.
    fresh = resolved(None)
    assert fresh.consent_grants == ()
    assert fresh.automatic_move_permissions == {}


def test_the_resolved_default_is_unpersisted(p7_conn):
    # A default nobody chose has no policy version. `set_policy` is what mints one,
    # and it is a user act with a reason (§8.8's meaningful diff).
    assert resolved(None).policy_version == UNSET_POLICY_VERSION


def test_the_resolved_default_passes_its_own_assertion(p7_conn):
    for mode in LOCAL_FIRST_MODES:
        assert_local_first(resolved(None, install_mode=mode))


# --- migrated from nothing --------------------------------------------------

def test_a_migrated_install_fills_every_absent_facet(p7_conn):
    # A policy row exists with a mode and no redaction settings -- the state a build
    # that predates §8.4's facets leaves behind.
    migrated = a_stored_policy(operation_mode=LOCAL_MODEL, redaction_settings={})
    assert resolved(migrated).redaction_settings == dict(MORE_REDACTING)


def test_a_partial_facet_map_is_completed_and_the_users_setting_survives(p7_conn):
    # Filling an absent facet is the default; overwriting a facet the user set would
    # be the product changing a choice behind their back (§8.8).
    partial = a_stored_policy(operation_mode=LOCAL_MODEL,
                              redaction_settings={DISPLAY_FACETS[0]: SHOWN})
    filled = resolved(partial).redaction_settings
    assert filled[DISPLAY_FACETS[0]] == SHOWN
    assert all(filled[facet] == REDACTED for facet in DISPLAY_FACETS[1:])


def test_every_reachable_stored_state_resolves_to_a_complete_facet_map(p7_conn):
    for stored in (None,
                   a_stored_policy(redaction_settings={}),
                   a_stored_policy(redaction_settings={DISPLAY_FACETS[2]: REDACTED}),
                   a_stored_policy()):
        assert set(resolved(stored).redaction_settings) == set(DISPLAY_FACETS)


# --- the floor is on the INSTALL, not on the user's choice ------------------

def test_a_user_chosen_cloud_mode_is_returned_unchanged(p7_conn):
    # §8.4: "Either remains a legitimate mode the user may choose; neither may be
    # what they find on install." W1 binds the default, never the choice.
    chosen = a_stored_policy(operation_mode="cloud_assisted")
    assert resolved(chosen).operation_mode == "cloud_assisted"
    assert resolved(chosen).consent_grants == (("Academics", "cloud_model"),)


def test_the_two_questions_are_different_and_the_test_proves_it(p7_conn):
    # `resolve_default_policy` answers "what is in force". `assert_local_first`
    # answers "is this a posture a user may arrive at without choosing it".
    # Collapsing them would either forbid a mode §8.4 offers or ship one it forbids.
    chosen = a_stored_policy(operation_mode="hybrid")
    assert resolved(chosen).operation_mode == "hybrid"
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(resolved(chosen))


# --- the negative half ------------------------------------------------------

@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(None, install_mode=mode)


@pytest.mark.parametrize("mode", CLOUD_MODES)
def test_a_cloud_mode_cannot_be_the_install_mode_over_a_stored_policy(p7_conn, mode):
    with pytest.raises(DefaultPostureViolation):
        resolved(a_stored_policy(redaction_settings={}), install_mode=mode)


def test_an_unknown_install_mode_is_a_load_error_and_not_a_posture_violation(p7_conn):
    # Two different failures. "A value outside this set is a load error, not a
    # fallback" is Task 2's; being a known mode that §8.4 forbids as a default is
    # W1's. A caller that catches one must not silently absorb the other.
    with pytest.raises(OutOfVocabulary):
        resolved(None, install_mode="mostly_offline")


def test_assert_local_first_rejects_a_shown_facet(p7_conn):
    # Data-minimizing is the second half of the same `must`, and §8.4's own example
    # settles the direction: the aggregate is safe to show, the expansion is not.
    almost = resolved(None)
    from dataclasses import replace
    loosened = replace(almost, redaction_settings={
        **almost.redaction_settings, DISPLAY_FACETS[0]: SHOWN})
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(loosened)


def test_assert_local_first_rejects_an_incomplete_facet_map(p7_conn):
    from dataclasses import replace
    with pytest.raises(DefaultPostureViolation):
        assert_local_first(replace(resolved(None), redaction_settings={}))


def test_no_module_under_privacy_names_a_cloud_mode_at_module_level(p7_conn):
    # Runtime introspection of every module's namespace, the way
    # `tests/p3/test_p3_no_invention.py` established. Objects that ARE
    # `vocabulary.py`'s own are skipped by IDENTITY, not by name, so a legitimate
    # re-export of `OPERATION_MODES` or `MODE_SEMANTICS` is not a false positive
    # while a second private copy of either is a failure.
    vocabulary_objects = {id(value) for value in vars(vocab).values()}
    forbidden = set(CLOUD_MODES)
    offenders: list[str] = []
    for info in pkgutil.iter_modules(privacy.__path__):
        module = importlib.import_module(f"privacy.{info.name}")
        if module is vocab:
            continue
        for name, value in vars(module).items():
            if name.startswith("_") or id(value) in vocabulary_objects:
                continue
            found: set[str] = set()
            if isinstance(value, str):
                found = forbidden & {value}
            elif isinstance(value, (tuple, list, set, frozenset)):
                found = forbidden & {v for v in value if isinstance(v, str)}
            elif isinstance(value, dict):
                found = forbidden & (
                    {k for k in value if isinstance(k, str)}
                    | {v for v in value.values() if isinstance(v, str)})
            if found:
                offenders.append(f"privacy.{info.name}.{name} -> {sorted(found)}")
    assert not offenders


def test_defaults_reads_no_configuration_at_all(p7_conn):
    # "No build flag, packaged configuration file, or first-run flow." A module that
    # cannot reach a file or an environment variable cannot be handed a mode by one.
    import privacy.defaults as module
    readers = {"os", "sys", "pathlib", "Path", "json", "tomllib", "configparser",
               "environ", "getenv", "open", "importlib", "pkgutil"}
    assert not (readers & set(vars(module)))


def test_the_resolver_is_deterministic(p7_conn):
    assert resolved(None) == resolved(None)


def test_p7_names_no_winner_between_the_two_local_modes(p7_conn):
    # SPEC Open question 11, held open BY CONSTRUCTION: there is no default mode in
    # `src/privacy/` for a later reader to mistake for an answer. `install_mode` has
    # no default, so a build that forgets to name one does not start; it fails.
    import inspect
    parameter = inspect.signature(resolve_default_policy).parameters["install_mode"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    import privacy.defaults as module
    held = [value for name, value in vars(module).items()
            if not name.startswith("_") and isinstance(value, str)]
    assert sorted(text for text in held if text in OPERATION_MODES) == \
        sorted(LOCAL_FIRST_MODES)


# --- what the gate actually calls -------------------------------------------

def test_effective_policy_falls_back_to_the_floor_when_nothing_is_set(p7_conn):
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.operation_mode == OFFLINE
    assert policy.policy_version == UNSET_POLICY_VERSION
    assert_local_first(policy)


def test_effective_policy_reads_the_stored_policy_when_there_is_one(p7_conn):
    version = set_policy(
        p7_conn,
        a_stored_policy(operation_mode="cloud_assisted", redaction_settings={}),
        component_version=COMPONENT, user_id="joseph",
        reason="the user turned on cloud assistance for Academics")
    policy = effective_policy(p7_conn, plan_version=PLAN, install_mode=OFFLINE,
                              set_at=FIXED_CLOCK)
    assert policy.policy_version == version
    assert policy.operation_mode == "cloud_assisted"
    # The absent facets are still filled with the more redacting value: a stored
    # policy that never named a facet has not chosen `shown` for it.
    assert policy.redaction_settings == dict(MORE_REDACTING)
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_defaults.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.defaults'` (collection fails on the
first import of the module under test).

- [ ] **Step 3: Write `src/privacy/defaults.py`**

```python
# src/privacy/defaults.py
"""W1 — §8.4's local-first `must`, made mechanical.

§8.4: "The default posture must therefore be local-first and data-minimizing." The
design names no install mode, so P7 does not pick one: `install_mode` is a required
keyword and the only values it accepts are the two under which no content leaves the
device. `src/privacy/` therefore holds NO default mode, which is what keeps SPEC
Open question 11 -- which of `offline` and `local_model` ships -- open by
construction rather than by discipline, and what makes `hybrid` and `cloud_assisted`
unreachable as a starting state through this door.

Both halves of the `must` are here.

**Local-first** is `LOCAL_FIRST_MODES`: §8.4's "Fully offline mode: No content leaves
the device" and "Local-model mode: Local extraction plus a user-installed local LLM
for eligible dossiers." The other two both permit a cloud model without the user
having asked for one.

**Data-minimizing** is `MORE_REDACTING`. §8.4's own example settles the direction: "A
summary such as '11 protected identity records' may be safe to show, while a visible
list of passport filenames on a shared screen may not be." The aggregate is the
default and the expansion is the user's act, so every facet the design leaves
configurable resolves to `redacted`, nothing is granted, and nothing is permitted to
move automatically.

**The floor binds the DEFAULT, never the choice.** §8.4: either cloud mode "remains a
legitimate mode the user may choose; neither may be what they find on install." So
`resolve_default_policy` returns a stored `cloud_assisted` policy unchanged, and
`assert_local_first` on that same policy raises. Two questions, two functions.

This module reads no file, no environment variable and no build flag. That is not a
style preference: Done-means 12's negative half names "build flag, packaged
configuration file, or first-run flow", and a module that cannot reach one cannot be
handed a mode by one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType

from privacy.policy import REDACTED, Policy, UNSET_POLICY_VERSION, current_policy
from privacy.vocabulary import DISPLAY_FACETS, check_mode

#: §8.4's two local modes, named once and validated against Task 2's vocabulary at
#: import so neither can drift into a second spelling.
OFFLINE = check_mode("offline")
LOCAL_MODEL = check_mode("local_model")

#: The floor. NOT a default: the caller names which of the two its build ships.
LOCAL_FIRST_MODES: tuple[str, str] = (OFFLINE, LOCAL_MODEL)

#: Per facet, the more redacting of §8.4's two values. Five facets, one value.
MORE_REDACTING: Mapping[str, str] = MappingProxyType(
    {facet: REDACTED for facet in DISPLAY_FACETS})


class DefaultPostureViolation(Exception):
    """A starting state §8.4's `must` forbids: a cloud mode, or a facet left shown."""


def _check_install_mode(install_mode: str) -> str:
    """A load error and a posture violation are different failures (Task 2, W1)."""
    check_mode(install_mode)
    if install_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"{install_mode!r} permits a cloud model without the user having asked "
            f"for one; §8.4's default posture must be local-first, so the install "
            f"default is one of {LOCAL_FIRST_MODES!r}. Either remains a mode the "
            f"user may choose."
        )
    return install_mode


def resolve_default_policy(stored: Policy | None, *, install_mode: str,
                           plan_version: str, set_at: str) -> Policy:
    """The policy in force, with everything nobody chose resolved to the floor.

    `install_mode` has no default. A build that forgets to name one does not start.
    """
    _check_install_mode(install_mode)
    if stored is None:
        return Policy(
            policy_version=UNSET_POLICY_VERSION,
            operation_mode=install_mode,
            consent_grants=(),
            redaction_settings=dict(MORE_REDACTING),
            automatic_move_permissions={},
            plan_version=plan_version,
            set_at=set_at,
        )
    # The mode is the user's and is not touched. An ABSENT facet is filled; a facet
    # the user set survives -- overwriting it would be the product changing a choice
    # behind their back (§8.8).
    return replace(stored, redaction_settings={**MORE_REDACTING,
                                               **stored.redaction_settings})


def effective_policy(conn: sqlite3.Connection, *, plan_version: str,
                     install_mode: str, set_at: str) -> Policy:
    """`current_policy` with the floor applied. The one composition the gate calls."""
    return resolve_default_policy(
        current_policy(conn, plan_version=plan_version),
        install_mode=install_mode, plan_version=plan_version, set_at=set_at)


def assert_local_first(policy: Policy) -> None:
    """Raise unless this is a posture a user may arrive at without choosing it.

    Applied to a fresh-install or migrated-from-nothing resolution. NOT applied to a
    policy the user set: §8.4 offers all four modes as choices and only constrains
    the default.
    """
    if policy.operation_mode not in LOCAL_FIRST_MODES:
        raise DefaultPostureViolation(
            f"a starting posture of {policy.operation_mode!r} permits a cloud model "
            f"without the user having asked for one (§8.4)")
    missing = sorted(set(DISPLAY_FACETS) - set(policy.redaction_settings))
    if missing:
        raise DefaultPostureViolation(
            f"facets {missing} are unresolved; §8.4's data-minimizing `must` has no "
            f"'unset' value, and an unresolved facet is decided by whoever reads it")
    shown = sorted(facet for facet, value in policy.redaction_settings.items()
                   if value != MORE_REDACTING[facet])
    if shown:
        raise DefaultPostureViolation(
            f"facets {shown} start shown; §8.4's example makes the aggregate the "
            f"default and the expansion the user's act")
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_defaults.py -v`
Expected: PASS — 26 passed (24 test functions; the two `CLOUD_MODES` parametrizations contribute
two cases each).

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–6 green, and P1–P5 still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/defaults.py tests/p7/test_p7_defaults.py
git commit -m "feat(P7): W1's local-first floor and the more-redacting default, with the mode left unchosen"
```

---

### Task 7: The six releasable item kinds, the always-local nine, and `whole_document_requested`

**Files:**
- Create: `src/privacy/items.py`
- Test: `tests/p7/test_p7_items.py`

**Interfaces:**
- Consumes: `privacy.vocabulary.ITEM_KINDS`, `.ALWAYS_LOCAL`, `.DENIAL_REASONS`, `.OutOfVocabulary`,
  `evidence_shape.location.TextSpan(start, end)`,
  `evidence_shape.store.runs_for_file(conn, file_id) -> list[ExtractionRun]`,
  `extractors.long_tail.POTENTIALLY_SENSITIVE`,
  `.sensitivity_signals_for(conn, run_id) -> list[sqlite3.Row]`.
- Produces (`items.py`):
  - `Excerpt(observation_key: str, span: TextSpan, reason: str)`
  - `RedactedIdentifier(observation_key: str, span: TextSpan, identifier_class: str)`
  - `CandidateLabel(label: str)`
  - `MetadataField(name: str, value: str)`
  - `EvidenceReference(observation_key: str)`
  - `Filename(file_id: str, value: str)`
  - `RequestedItem` — the union of the six.
  - `ITEM_FIELDS: Mapping[str, tuple[str, ...]]` — kind → field names, read from
    `dataclasses.fields`, never retyped.
  - `RATIFIED_ITEM_KINDS: tuple[str, ...]` (§8.4's five), `UNRATIFIED_ITEM_KINDS: tuple[str, ...]`
    (`("filename",)`), `FILENAME_OPEN_QUESTION: str`.
  - `kind_of(item) -> str`
  - `is_whole_document(item, *, unit_length) -> bool`
  - `check_item(item, *, unit_length, protected, sensitive_keys, allow_unratified) -> None` (A11)
  - `sensitive_observation_keys(conn, file_id) -> frozenset[str]` (A13)
  - `AlwaysLocalRequested`, `WholeDocumentRequested`, `UnratifiedItemKind`, `ProtectedItemRequested`.

**Done-means:** 6 (the `always_local_item` and `whole_document_requested` reasons).

**The sixth kind is built and cannot be shipped by accident — NEEDS-JOSEPH B5d/C9a.** §8.4's
sentence names **five**: *"selected excerpts, redacted identifiers, candidate labels, non-sensitive
metadata, and evidence references"*, and the same sentence puts *"Paths"* in the always-local set.
§7.7's residual dossier *"includes the filename"*. §7.3 forbids filenames in prompts **only** for
`Protected Records`: *"it should normally remain local-only and must not cause filenames or content
to be exposed in model prompts."* P7's SPEC reads directory path ≠ filename — §7.3's carve-out is
vacuous under any other reading — permits `filename` for non-protected files, denies it for
protected ones, and lists the whole thing as its own Open question 2. **This plan does not settle
it.** `allow_unratified` is a required keyword with no default, so a caller cannot admit a
`Filename` without writing the word; `UNRATIFIED_ITEM_KINDS` names the kind; and
`FILENAME_OPEN_QUESTION` names the three sections that disagree. A reviewer sees an unratified
reading rather than a shipped one, and Task 21 can assert that no module under `src/privacy/` passes
`allow_unratified=True`.

**The protected-filename rule takes the stricter of two readings, and says which.** §7.3 has no
locality qualifier — *"must not cause filenames or content to be exposed in model prompts"*, full
stop — while §8.4's *"not included in cloud-model prompts **by default**"* is what the consent path
reopens. So `check_item` refuses a `Filename` on a protected file for **any** target, and
`NeedsConsent` is where the user reopens it. Reported as a reading.

**The always-local set is enforced structurally for five kinds and by name for the sixth, and the
gap is named rather than papered over.** Eight of §8.4's nine always-local items have no field to
live in: `Excerpt`, `RedactedIdentifier` and `EvidenceReference` carry an `observation_key` and at
most a span; `CandidateLabel` carries a label; `Filename` carries a filename. `MetadataField` is
the one free-text channel, so its `name` is checked against `ALWAYS_LOCAL` — **the nine names
exactly, with no synonym list**. A synonym list is a detection rule and *"`src/privacy/` contains no
regex, no gazetteer, no filename pattern, no keyword list"*. **The consequence is real and is
reported: `MetadataField(name="current_path", ...)` is not caught by this layer.** What catches it
is that a `metadata_field` is *"a named non-sensitive field"* whose name the caller declares, and
Task 13 decides on the declared name; P7 owns no detector that could second-guess it.

**"OCR output" is the whole output, not an excerpt of it.** §8.4 permits *"a short heading or OCR
excerpt"* in the very sentence that puts *"OCR output"* in the always-local set, so an `Excerpt`
whose observation sits in the `ocr` zone is releasable and the complete OCR text is not — and the
mechanism that stops the complete text is `WholeDocumentRequested`, not the always-local check.

**"Raw sensitive values" is the one always-local item that needs P5.** It cannot be recognised
without a detection rule P7 does not own, and P5 already publishes the only per-value sensitivity
signal in the product: *"Email addresses, message content and every VCF value are marked
POTENTIALLY SENSITIVE at emission, for P7 to act on. P5 assigns no handling class: section 8.4
gives classification to P7."* So an `Excerpt` over an observation P5 marked is
`AlwaysLocalRequested`, while a `RedactedIdentifier` over the **same** key is permitted — that is
what §8.4's *"redacted identifiers"* allowance means, and Task 8's transform is injected with no
default so nothing unredacted escapes through it.

**`sensitive_keys` is a required keyword and `check_item` opens no database.** The walk is
`runs_for_file` → `sensitivity_signals_for`, published here as `sensitive_observation_keys`; P7
adds no reader to P5 and composes the two that exist.

- [ ] **Step 1: Write the failing test**

```python
# tests/p7/test_p7_items.py
"""§8.4's compact dossier: what may be named in a request, and what may not.

Two of the assertions here are held open on purpose.

`filename` is the sixth kind and §8.4's own sentence names five. §7.7 puts the
filename in the residual dossier and §7.3 forbids filenames in prompts only for
Protected Records. P7's SPEC adopts the reading that makes §7.3 non-vacuous and lists
it as Open question 2. NEEDS-JOSEPH B5d/C9a: the tests below prove the kind is
unadmittable without an explicit opt-in, and never that the reading is right.

The always-local check over `MetadataField.name` is a VOCABULARY check against §8.4's
nine names, not a detector. `MetadataField(name="current_path")` is not caught here
and a test says so, because a synonym list would be the gazetteer P7 is forbidden to
own.
"""
from __future__ import annotations

import dataclasses

import pytest

from evidence_shape.location import TextSpan
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_run

from extractors.long_tail import (
    POTENTIALLY_SENSITIVE,
    SENSITIVITY_DDL,
    SensitivitySignal,
    record_sensitivity_signals,
)

from privacy.items import (
    FILENAME_OPEN_QUESTION,
    ITEM_FIELDS,
    RATIFIED_ITEM_KINDS,
    UNRATIFIED_ITEM_KINDS,
    AlwaysLocalRequested,
    CandidateLabel,
    EvidenceReference,
    Excerpt,
    Filename,
    MetadataField,
    ProtectedItemRequested,
    RedactedIdentifier,
    UnratifiedItemKind,
    WholeDocumentRequested,
    check_item,
    is_whole_document,
    kind_of,
    sensitive_observation_keys,
)
from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OutOfVocabulary

HASH_A = "a" * 64
CLOCK = "2026-08-22T12:00:00+00:00"
UNIT = 400          # the length of the text unit the excerpts address
SENSITIVE_KEY = "obs-key-email"


def ok(item, **over) -> None:
    """The permissive baseline: nothing protected, nothing sensitive, no opt-in."""
    base = dict(unit_length=UNIT, protected=False, sensitive_keys=frozenset(),
                allow_unratified=False)
    base.update(over)
    check_item(item, **base)


def an_excerpt(start: int = 12, end: int = 60, key: str = "obs-key-heading") -> Excerpt:
    return Excerpt(observation_key=key, span=TextSpan(start, end),
                   reason="the heading that names the course")


@pytest.fixture()
def p4_p5_conn(p7_conn):
    """P7's database with P4's and P5's tables added, so the walk is a real walk."""
    create_evidence_schema(p7_conn)
    p7_conn.executescript(SENSITIVITY_DDL)
    return p7_conn


# --- the six kinds ----------------------------------------------------------

def test_the_five_ratified_kinds_are_84s_own_sentence():
    # "selected excerpts, redacted identifiers, candidate labels, non-sensitive
    # metadata, and evidence references."
    assert RATIFIED_ITEM_KINDS == ("excerpt", "redacted_identifier", "candidate_label",
                                   "metadata_field", "evidence_reference")


def test_the_sixth_kind_is_marked_unratified():
    # NEEDS-JOSEPH B5d/C9a. Six kinds exist; §8.4's sentence names five.
    assert UNRATIFIED_ITEM_KINDS == ("filename",)
    assert RATIFIED_ITEM_KINDS + UNRATIFIED_ITEM_KINDS == ITEM_KINDS
    assert len(ITEM_KINDS) == 6 and len(RATIFIED_ITEM_KINDS) == 5


def test_the_open_question_names_the_sections_that_disagree():
    for section in ("8.4", "7.7", "7.3"):
        assert section in FILENAME_OPEN_QUESTION


def test_kind_of_maps_every_kind(): 
    items = (an_excerpt(),
             RedactedIdentifier("obs-key-1", TextSpan(0, 9), "an-opaque-class"),
             CandidateLabel("BUSIB 4300"),
             MetadataField("page_count", "14"),
             EvidenceReference("obs-key-1"),
             Filename("file-1", "syllabus.pdf"))
    assert tuple(kind_of(item) for item in items) == ITEM_KINDS


def test_kind_of_refuses_a_stranger():
    # A seventh kind is a P7 contract revision, not an implementation decision.
    with pytest.raises(OutOfVocabulary):
        kind_of("just a string")


def test_item_fields_are_read_from_the_dataclasses_and_not_retyped():
    assert ITEM_FIELDS["excerpt"] == ("observation_key", "span", "reason")
    assert ITEM_FIELDS["redacted_identifier"] == ("observation_key", "span",
                                                  "identifier_class")
    assert set(ITEM_FIELDS) == set(ITEM_KINDS)


def test_an_evidence_reference_carries_an_id_and_no_content():
    # SPEC §4: "evidence_reference  an id only -- no content." Checked with
    # `dataclasses.fields`, not by reading the class body.
    names = {field.name for field in dataclasses.fields(EvidenceReference)}
    assert names == {"observation_key"}
    assert not (names & {"value", "text", "raw_value", "excerpt", "span"})


def test_the_citation_handle_is_the_key_and_never_the_id():
    # M14: "a per-row `observation_id` dies when the extractor is upgraded."
    for kind in (Excerpt, RedactedIdentifier, EvidenceReference):
        names = {field.name for field in dataclasses.fields(kind)}
        assert "observation_key" in names
        assert "observation_id" not in names


def test_a_redacted_identifier_carries_a_class_and_no_value():
    names = {field.name for field in dataclasses.fields(RedactedIdentifier)}
    assert names == {"observation_key", "span", "identifier_class"}


def test_every_ratified_kind_passes_without_the_opt_in():
    for item in (an_excerpt(),
                 RedactedIdentifier("obs-key-1", TextSpan(0, 9), "an-opaque-class"),
                 CandidateLabel("BUSIB 4300"),
                 MetadataField("page_count", "14"),
                 EvidenceReference("obs-key-1")):
        ok(item)


# --- the always-local nine --------------------------------------------------

def test_the_always_local_set_is_84s_nine():
    # "Paths, complete extracted text, OCR output, file hashes, image EXIF, GPS,
    # user edits, group memberships, and raw sensitive values should remain local."
    assert len(ALWAYS_LOCAL) == 9


@pytest.mark.parametrize("name", ALWAYS_LOCAL)
def test_no_always_local_name_is_expressible_as_a_metadata_field(name):
    # One test per name, nine tests. `metadata_field` is the only kind with a
    # free-text field name, so it is the only place one of the nine could be asked
    # for by name.
    with pytest.raises(AlwaysLocalRequested):
        ok(MetadataField(name, "whatever the caller put here"))


def test_five_kinds_have_no_field_an_always_local_item_could_live_in():
    # The structural half. An excerpt cannot carry a path, a hash or an EXIF blob
    # because it has nowhere to put one: it names an observation and a span.
    for kind in (Excerpt, RedactedIdentifier, EvidenceReference, CandidateLabel,
                 Filename):
        names = {field.name for field in dataclasses.fields(kind)}
        assert not (names & set(ALWAYS_LOCAL))


def test_the_always_local_check_is_a_vocabulary_check_and_not_a_detector():
    # REPORTED GAP, deliberately: P7 owns no synonym list, because a synonym list is
    # the gazetteer the SPEC's Deferred table puts outside this contract. A caller
    # that declares a path under another name is trusted, and Task 13 decides on the
    # declared name.
    ok(MetadataField("current_path", "/Users/j/Corpus/passport.pdf"))


def test_complete_extracted_text_is_unreachable_through_a_span_as_well():
    with pytest.raises(WholeDocumentRequested):
        ok(an_excerpt(0, UNIT))


def test_a_short_ocr_excerpt_is_permitted_and_the_whole_output_is_not():
    # §8.4 permits "a short heading or OCR excerpt" in the same sentence that puts
    # "OCR output" in the always-local set, so the boundary is the SPAN, not the
    # zone.
    ok(an_excerpt(0, 40, key="obs-key-ocr-line-1"))
    with pytest.raises(WholeDocumentRequested):
        ok(an_excerpt(0, UNIT, key="obs-key-ocr-whole"))


def test_a_raw_sensitive_value_is_not_releasable_as_an_excerpt():
    # P5's POTENTIALLY_SENSITIVE is the only per-value sensitivity signal in the
    # product, and §8.4's "raw sensitive values" cannot be recognised without it.
    with pytest.raises(AlwaysLocalRequested):
        ok(an_excerpt(key=SENSITIVE_KEY),
           sensitive_keys=frozenset({SENSITIVE_KEY}))


def test_the_redacted_form_of_the_same_value_is_releasable():
    # §8.4 lists "redacted identifiers" among what MAY be sent. The raw value stays
    # local; the transform's output is what leaves, and Task 8 injects the transform
    # with no default so a build that forgets to wire one emits nothing.
    ok(RedactedIdentifier(SENSITIVE_KEY, TextSpan(0, 9), "an-opaque-class"),
       sensitive_keys=frozenset({SENSITIVE_KEY}))


def test_an_unmarked_excerpt_is_not_made_sensitive_by_a_neighbour():
    ok(an_excerpt(), sensitive_keys=frozenset({SENSITIVE_KEY}))


# --- whole_document_requested -----------------------------------------------

def test_an_excerpt_covering_the_whole_unit_is_refused():
    # §8.4: "It should not send full documents where a short heading or OCR excerpt
    # is enough to resolve the question."
    assert is_whole_document(an_excerpt(0, UNIT), unit_length=UNIT) is True
    with pytest.raises(WholeDocumentRequested):
        ok(an_excerpt(0, UNIT))


def test_a_span_that_stops_one_character_short_is_not_a_whole_document():
    # The check is exact coverage and nothing cleverer. A near-whole dossier is
    # §8.6's ladder to reduce, and the ladder runs in P8 before the call (M9); a
    # threshold here would be a number the design does not state.
    assert is_whole_document(an_excerpt(0, UNIT - 1), unit_length=UNIT) is False
    ok(an_excerpt(0, UNIT - 1))


def test_a_span_starting_after_the_beginning_is_not_a_whole_document():
    assert is_whole_document(an_excerpt(1, UNIT), unit_length=UNIT) is False


def test_a_span_longer_than_the_unit_is_still_a_whole_document():
    assert is_whole_document(an_excerpt(0, UNIT + 50), unit_length=UNIT) is True


def test_is_whole_document_is_false_for_every_kind_without_document_text():
    # Only `excerpt` releases document text. `redacted_identifier` releases the
    # transform's output, so a span covering everything is pointless rather than
    # dangerous, and refusing it would be a rule the design does not state.
    for item in (RedactedIdentifier("obs-key-1", TextSpan(0, UNIT), "an-opaque-class"),
                 CandidateLabel("BUSIB 4300"), MetadataField("page_count", "14"),
                 EvidenceReference("obs-key-1"), Filename("file-1", "syllabus.pdf")):
        assert is_whole_document(item, unit_length=UNIT) is False


# --- the sixth kind, held unratified ---------------------------------------

def test_filename_is_refused_without_an_explicit_opt_in():
    with pytest.raises(UnratifiedItemKind) as caught:
        ok(Filename("file-1", "syllabus.pdf"))
    assert "8.4" in str(caught.value)


def test_filename_is_permitted_for_a_non_protected_file_under_the_flagged_reading():
    # SPEC Open question 2, and the SPEC's own words: "This is the one place where
    # the contract resolves an apparent conflict rather than deferring it, because
    # P8 and P11 cannot build without an answer."
    ok(Filename("file-1", "syllabus.pdf"), allow_unratified=True)


def test_filename_is_refused_for_a_protected_file():
    # §7.3, which carries no locality qualifier: Protected Records "must not cause
    # filenames or content to be exposed in model prompts". The stricter of the two
    # readings; §8.4's "by default" is what the consent path reopens.
    with pytest.raises(ProtectedItemRequested):
        ok(Filename("file-1", "passport.pdf"), protected=True, allow_unratified=True)


def test_a_protected_file_may_still_release_a_bounded_excerpt():
    # Protected is not the same refusal as always-local. §8.4's protected rule is
    # about cloud prompts and consent, and that decision is Task 13's; the item
    # layer refuses only what no mode can release.
    ok(an_excerpt(), protected=True)


def test_the_opt_in_has_no_default():
    import inspect
    parameter = inspect.signature(check_item).parameters["allow_unratified"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


# --- the P5 walk ------------------------------------------------------------

def test_sensitive_observation_keys_walks_p4s_runs_and_p5s_signals(p4_p5_conn):
    record_run(p4_p5_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=HASH_A,
        extractor_name="long_tail", extractor_version="1", source_type="email",
        analysis_tier="native", config={}, completeness="complete",
        started_at=CLOCK, observation_count=1))
    record_sensitivity_signals(
        p4_p5_conn, run_id="run-1",
        signals=[SensitivitySignal(observation_index=0, signal=POTENTIALLY_SENSITIVE,
                                   basis="email address in body")],
        observation_keys=[SENSITIVE_KEY], now=CLOCK)
    assert sensitive_observation_keys(p4_p5_conn, "file-1") == frozenset({SENSITIVE_KEY})
    assert sensitive_observation_keys(p4_p5_conn, "file-2") == frozenset()


def test_the_walk_feeds_check_item_and_the_two_meet(p4_p5_conn):
    record_run(p4_p5_conn, ExtractionRun(
        run_id="run-1", file_id="file-1", content_hash=HASH_A,
        extractor_name="long_tail", extractor_version="1", source_type="contacts",
        analysis_tier="native", config={}, completeness="complete",
        started_at=CLOCK, observation_count=1))
    record_sensitivity_signals(
        p4_p5_conn, run_id="run-1",
        signals=[SensitivitySignal(observation_index=0, signal=POTENTIALLY_SENSITIVE,
                                   basis="every VCF value")],
        observation_keys=[SENSITIVE_KEY], now=CLOCK)
    keys = sensitive_observation_keys(p4_p5_conn, "file-1")
    with pytest.raises(AlwaysLocalRequested):
        ok(an_excerpt(key=SENSITIVE_KEY), sensitive_keys=keys)


def test_p7_adds_no_reader_to_p5(p4_p5_conn):
    # The two readers P4 and P5 already publish are composed, not reimplemented.
    import privacy.items as module
    assert module.runs_for_file.__module__ == "evidence_shape.store"
    assert module.sensitivity_signals_for.__module__ == "extractors.long_tail"


# --- no invention -----------------------------------------------------------

def test_items_holds_no_threshold_and_no_identifier_class():
    # SPEC Deferred: "Which identifier classes exist and how each is transformed is
    # not enumerated anywhere in the design." And §8.6 gives no numeric value for
    # any ceiling. `unit_length` is the caller's measurement, not a constant.
    import privacy.items as module
    numbers = [value for name, value in vars(module).items()
               if not name.startswith("_") and isinstance(value, (int, float))
               and not isinstance(value, bool)]
    assert not numbers
    assert not [name for name in vars(module) if "identifier_classes" in name.lower()]


def test_items_imports_none_of_extractors_three_refusals():
    # `safety.admit`, ProtectedContainerRefused and DatalessRefused are P3's and
    # P5's refusals and are decided upstream; a file that failed either never
    # acquires the (file_id, content_hash) pair P7 keys on.
    import privacy.items as module
    assert not ({"admit", "ProtectedContainerRefused", "DatalessRefused"}
                & set(vars(module)))
```

- [ ] **Step 2: Run the test and watch it fail**

Run: `pytest tests/p7/test_p7_items.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'privacy.items'` (collection fails on the
first import of the module under test).

- [ ] **Step 3: Write `src/privacy/items.py`**

```python
# src/privacy/items.py
"""§8.4's compact dossier: the six kinds a request may name, and the nine it may not.

§8.4 permits "selected excerpts, redacted identifiers, candidate labels,
non-sensitive metadata, and evidence references" -- five -- and puts "Paths, complete
extracted text, OCR output, file hashes, image EXIF, GPS, user edits, group
memberships, and raw sensitive values" out of reach of every mode.

**The sixth kind is unratified and cannot be admitted by accident.** §7.7's residual
dossier "includes the filename"; §7.3 forbids filenames in prompts only for Protected
Records; §8.4 puts paths -- not filenames -- in the always-local set. P7's SPEC reads
directory path != filename, because §7.3's carve-out is vacuous under any other
reading, and lists the whole thing as its Open question 2. This module builds
`Filename` and refuses it unless the caller passes `allow_unratified=True`, so the
reading is visible at every call site instead of settled here.

**Every request names references, never content.** An `Excerpt` carries an
observation key and a span; the gate resolves it from local storage
(`privacy.resolve`) and nothing else in `src/privacy/` may. That asymmetry is what
makes a bypassing call unconstructible rather than merely forbidden.

**The always-local set is structural for five kinds and by name for the sixth.**
Nothing but `MetadataField` has a free-text field, so nothing but `MetadataField`
could name one of the nine -- and its `name` is checked against `ALWAYS_LOCAL`
exactly, with **no synonym list**, because a synonym list is the gazetteer the SPEC's
Deferred table puts outside this contract. A caller that declares a path under
another name is trusted; P7 owns no detector that could second-guess it.

**"Raw sensitive values" needs P5.** It is the one always-local item no vocabulary
check can recognise, and P5 already marks it: "Email addresses, message content and
every VCF value are marked POTENTIALLY SENSITIVE at emission, for P7 to act on."
An `Excerpt` over a marked observation is refused; a `RedactedIdentifier` over the
same observation is permitted, which is exactly what §8.4's "redacted identifiers"
allowance means.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, fields
from types import MappingProxyType

from evidence_shape.location import TextSpan
from evidence_shape.store import runs_for_file

from extractors.long_tail import POTENTIALLY_SENSITIVE, sensitivity_signals_for

from privacy.vocabulary import ALWAYS_LOCAL, ITEM_KINDS, OutOfVocabulary


@dataclass(frozen=True)
class Excerpt:
    """§8.4's "selected excerpts". A reference plus a bounded span, never text."""

    observation_key: str
    span: TextSpan
    reason: str


@dataclass(frozen=True)
class RedactedIdentifier:
    """§8.4's "redacted identifiers". The class is opaque (SPEC Deferred)."""

    observation_key: str
    span: TextSpan
    identifier_class: str


@dataclass(frozen=True)
class CandidateLabel:
    """§8.4's "candidate labels": a label already present in the local database.

    **Reported seam:** "already present" is P6's label store and P6 is unbuilt, so
    P7 cannot verify it. Until P6 exists, `candidate_label` is the one kind whose
    contents P7 cannot bound, and this is named rather than papered over with a
    length ceiling the design does not state.
    """

    label: str


@dataclass(frozen=True)
class MetadataField:
    """§8.4's "non-sensitive metadata": "file type, page count, capture year"."""

    name: str
    value: str


@dataclass(frozen=True)
class EvidenceReference:
    """§8.4's "evidence references". An id only -- no content (SPEC §4).

    The id is P4's `observation_key`, never the per-row `observation_id`, which dies
    on extractor upgrade (M14).
    """

    observation_key: str


@dataclass(frozen=True)
class Filename:
    """UNRATIFIED. §8.4 names five kinds; this is a sixth. See the module docstring."""

    file_id: str
    value: str


RequestedItem = (Excerpt | RedactedIdentifier | CandidateLabel | MetadataField
                 | EvidenceReference | Filename)

_KIND_BY_TYPE: Mapping[type, str] = MappingProxyType({
    Excerpt: "excerpt",
    RedactedIdentifier: "redacted_identifier",
    CandidateLabel: "candidate_label",
    MetadataField: "metadata_field",
    EvidenceReference: "evidence_reference",
    Filename: "filename",
})

#: §8.4's own sentence, in its own order.
RATIFIED_ITEM_KINDS: tuple[str, ...] = (
    "excerpt", "redacted_identifier", "candidate_label", "metadata_field",
    "evidence_reference",
)

#: NEEDS-JOSEPH B5d/C9a. Built, named, and unadmittable without an explicit opt-in.
UNRATIFIED_ITEM_KINDS: tuple[str, ...] = ("filename",)

FILENAME_OPEN_QUESTION = (
    "SPEC Open question 2. §8.4 puts *paths* in the always-local set; §7.7 puts the "
    "filename in the residual dossier; §7.3 forbids filenames in prompts only for "
    "Protected Records. P7's SPEC adopts the reading that makes §7.3 non-vacuous -- "
    "directory path is not filename -- and flags it. Unratified."
)

if RATIFIED_ITEM_KINDS + UNRATIFIED_ITEM_KINDS != ITEM_KINDS:
    raise ImportError(
        f"the ratified five plus the unratified one must be Task 2's {ITEM_KINDS!r}; "
        "adding a member is a P7 contract revision, not an implementation decision"
    )

#: kind -> field names, read from the dataclasses so a shape change cannot drift
#: from its published description.
ITEM_FIELDS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    kind: tuple(field.name for field in fields(item_type))
    for item_type, kind in _KIND_BY_TYPE.items()
})


class AlwaysLocalRequested(Exception):
    """One of §8.4's nine always-local items was named. No mode releases it."""


class WholeDocumentRequested(Exception):
    """An excerpt that resolves to the complete extracted text (§8.4)."""


class UnratifiedItemKind(Exception):
    """`filename` was requested without an explicit opt-in. See B5d/C9a."""


class ProtectedItemRequested(Exception):
    """§7.3: a Protected Records filename may not be exposed in a model prompt."""


def kind_of(item: RequestedItem) -> str:
    """The `ITEM_KINDS` name of an item. A seventh kind is a contract revision."""
    try:
        return _KIND_BY_TYPE[type(item)]
    except KeyError:
        raise OutOfVocabulary(
            f"{type(item).__name__} is not one of §8.4's item kinds {ITEM_KINDS!r}"
        ) from None


def is_whole_document(item: RequestedItem, *, unit_length: int) -> bool:
    """True when an excerpt covers the whole of the text unit it addresses.

    Exact coverage and nothing cleverer. A near-whole dossier is §8.6's ladder to
    reduce and the ladder runs in P8 before the call (M9); a threshold here would be
    a number the design does not state. Only `excerpt` releases document text, so
    only `excerpt` can be a whole document.
    """
    if not isinstance(item, Excerpt):
        return False
    return item.span.start == 0 and item.span.end >= unit_length


def check_item(item: RequestedItem, *, unit_length: int, protected: bool,
               sensitive_keys: frozenset[str], allow_unratified: bool) -> None:
    """Raise unless this item may be named in a request at all.

    Target-independent only. Whether a protected file may reach a *cloud* model under
    a given mode is `privacy.release`'s decision; what is refused here is what no
    mode releases.

    Every keyword is required. `sensitive_keys` comes from
    `sensitive_observation_keys`, `protected` from the classification record (never
    inferred from the class -- SPEC Open question 1), and `allow_unratified` from a
    caller willing to write the word.
    """
    kind = kind_of(item)
    if kind in UNRATIFIED_ITEM_KINDS and not allow_unratified:
        raise UnratifiedItemKind(
            f"{kind!r} is not one of §8.4's five releasable kinds "
            f"{RATIFIED_ITEM_KINDS!r}. {FILENAME_OPEN_QUESTION}"
        )
    if protected and isinstance(item, Filename):
        raise ProtectedItemRequested(
            "§7.3: Protected Records 'must not cause filenames or content to be "
            "exposed in model prompts'. The user reopens this through consent, not "
            "through a default."
        )
    if isinstance(item, MetadataField) and item.name in ALWAYS_LOCAL:
        raise AlwaysLocalRequested(
            f"{item.name!r} is one of §8.4's always-local items {ALWAYS_LOCAL!r}; "
            "no mode releases it and the gate has no code path that materialises one"
        )
    if isinstance(item, Excerpt) and item.observation_key in sensitive_keys:
        raise AlwaysLocalRequested(
            f"{item.observation_key!r} was marked {POTENTIALLY_SENSITIVE!r} by P5, "
            "so its raw value is one of §8.4's always-local items. A "
            "`redacted_identifier` over the same observation is releasable."
        )
    if is_whole_document(item, unit_length=unit_length):
        raise WholeDocumentRequested(
            "§8.4: the engine 'should not send full documents where a short heading "
            "or OCR excerpt is enough to resolve the question'"
        )


def sensitive_observation_keys(conn: sqlite3.Connection,
                               file_id: str) -> frozenset[str]:
    """The observation keys P5 marked POTENTIALLY SENSITIVE, for one file.

    P5's reader is keyed by `run_id` only, so the file-level walk composes P4's
    `runs_for_file` with P5's `sensitivity_signals_for`. P7 adds no reader to either.
    """
    keys: set[str] = set()
    for run in runs_for_file(conn, file_id):
        for row in sensitivity_signals_for(conn, run.run_id):
            if row["signal"] == POTENTIALLY_SENSITIVE:
                keys.add(row["observation_key"])
    return frozenset(keys)
```

- [ ] **Step 4: Run the test and watch it pass**

Run: `pytest tests/p7/test_p7_items.py -v`
Expected: PASS — 39 passed (31 test functions; the `ALWAYS_LOCAL` parametrization contributes nine
cases, one per always-local name).

- [ ] **Step 5: Run P7's suite so far, and P1–P5**

Run: `pytest tests/p7 -q && pytest tests/ -q`
Expected: PASS — Tasks 1–7 green, and P1–P5 still green.

- [ ] **Step 6: Commit**

```bash
git add src/privacy/items.py tests/p7/test_p7_items.py
git commit -m "feat(P7): the releasable item kinds, the always-local nine, whole_document_requested, and filename held unratified"
```

---

## What these four tasks leave open, by name

| # | Question | Held by | Where it must be answered |
|---|---|---|---|
| **C5** | Does P6 keep a `sensitivity status` row among §3.11's universal fields, beside P7's authoritative record? P7's SPEC Contract-in says P6 *"must accept `sensitivity` as a first-class universal field"*; D2 makes P7's record authoritative; round 1's F-2 found the P6 field has no producer. | Task 4 depends on no P6 field: its store creates its own table and one test asserts it works in a database with no `file_facts` at all. | **Joseph.** Until then P6 creates no such row and P7 reads none. |
| **B5d / C9a** | Is `filename` a sixth releasable kind? §8.4 names five and puts *paths* in the always-local set; §7.7 puts the filename in the residual dossier; §7.3 forbids filenames in prompts only for Protected Records. | Task 7: `UNRATIFIED_ITEM_KINDS`, `FILENAME_OPEN_QUESTION`, and `allow_unratified` as a required keyword with no default. | **Joseph.** Task 21 should assert no module under `src/privacy/` passes `allow_unratified=True`. |
| **OQ1** | Is `protected` exactly the top two handling classes? | Task 4 stores `protected` and never derives it; Task 7 takes it as a required keyword. | P7 SPEC revision. |
| **OQ3** | What is a *"corpus area"*? | Task 5: `scope` is an opaque string P7 neither parses nor validates. | P7 SPEC revision; affects P3, P9, P10. |
| **OQ11** | Which of `offline` and `local_model` ships as the install default? | Task 6: `install_mode` is a required keyword and `src/privacy/` holds no default mode. | Turns on whether a local model is assumed present. |
| **§2.9** | Which consent option authorizes speech-to-text? | Task 5: an explicit grant at the scope whose option is not `no_model_use`. Reported as a reading. | Not stated anywhere in the design. |
| **M10 seam** | P5's `transcription_authorized` is `Callable[[], bool]` and takes no scope. | Task 5: `TranscriptionAuthorization` carries the scope as a field, and a test asserts P5's signature so the day it widens the adapter can be deleted. | P5 contract revision, or leave the adapter. |
| **Always-local by name** | `MetadataField(name="current_path")` is not caught by Task 7's vocabulary check. | Task 7: a test asserts the gap deliberately, because a synonym list is the gazetteer P7 may not own. | Task 13's decision on the declared name, or a detector nobody has written. |
| **`candidate_label`** | *"a label already present in the local database"* is unverifiable while P6 is unbuilt. | Task 7: named in `CandidateLabel`'s docstring; no length ceiling invented. | P6. |

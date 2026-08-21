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

#: §8.4: "A scanned passport ... should enter a protected state immediately." The
#: DETECTOR that would notice is unwritten (D2), so the test plays its part and the
#: `basis` says which part it is playing.
PASSPORT_KEYS = ("obs-key-passport-mrz", "obs-key-passport-number")


def a_file(conn, tmp_path: Path, *, name: str = "passport.pdf",
           content_hash: str = "sha256:aaa") -> str:
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
    base = dict(file_id="file-1", content_hash="sha256:aaa",
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
    assert store.current("file-1", "sha256:aaa") == record


def test_current_is_keyed_on_the_content_hash_and_not_on_the_file_id(store):
    store.write(a_record())
    assert store.current("file-1", "sha256:bbb") is None


def test_new_bytes_at_the_same_file_inherit_nothing(store):
    # D2: "a classification is about BYTES; new bytes at a path are a new file
    # version and inherit nothing." The edited scan reads as unlooked-at, which is
    # what makes `Denied(unclassified)` correct rather than a regression.
    store.write(a_record())
    assert store.current("file-1", "sha256:edited") is None
    assert store.current_fact_id("file-1", "sha256:edited") is None


def test_current_is_none_before_anything_classifies(store):
    # The detector is unwritten (D2). This is the state a real corpus is in.
    assert store.current("file-unknown", "sha256:zzz") is None


def test_current_fact_id_returns_the_unsuperseded_row(store):
    old = store.write(a_record())
    new = store.write(a_record(reliability_state="user_confirmed", observed_at=LATER))
    store.supersede(old, new, "user reclassified")
    assert store.current_fact_id("file-1", "sha256:aaa") == new


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
    assert store.current("file-1", "sha256:aaa") == confirmed


def test_the_ordering_holds_regardless_of_write_order(store):
    confirmed = a_record(reliability_state="user_confirmed", basis="user",
                         evidence_refs=())
    store.write(confirmed)
    store.write(a_record(reliability_state="direct", observed_at=LATER))
    assert store.current("file-1", "sha256:aaa") == confirmed


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
    assert store.current("file-1", "sha256:aaa") is None
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
        store.current("file-1", "sha256:aaa")


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
    assert store.current("file-1", "sha256:aaa").reliability_state == "validated"


def test_history_is_oldest_first_and_spans_file_versions(store):
    store.write(a_record(observed_at=FIXED_CLOCK))
    store.write(a_record(content_hash="sha256:edited", observed_at=LATER))
    assert [r.content_hash for r in store.history("file-1")] == \
        ["sha256:aaa", "sha256:edited"]


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
        "content_hash": "sha256:aaa",
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
    assert store.current(file_id, "sha256:aaa").evidence_refs == PASSPORT_KEYS
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
    assert store.current(file_id, "sha256:aaa") is None


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
    assert store.current("file-1", "sha256:aaa") is not None


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
    assert store.current("file-1", "sha256:aaa").protected is True
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

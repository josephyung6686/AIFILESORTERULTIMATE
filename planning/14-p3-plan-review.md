# P3 Plan Review — `planning/parts/P3-scan-corpus-selection/PLAN.md`

**Verdict: EXECUTE AFTER THREE FIXES.** The plan is sound in substance — its contract
coverage is complete, its authorship rule holds end to end, and it answers none of the
open questions it is required to leave open. But it does not run as written: three
defects, all mechanical, all in the last patch layer. Fix items 1–3 of the edit order,
then execute Tasks 1–18 in sequence. Nothing here is a redesign and no task should be
dropped.

| | Count |
|---|---|
| **Blocking findings** | **3** |
| Non-blocking findings | 9 (one — N0 — is high severity) |
| Already sound (verified, do not re-litigate) | 18 |
| `13-p2-p3-plan-robustness.md` findings now **dead** | 1 (P3-A) |
| `13` findings still live | 8 (one — P3-C — moved from P1 to P3 and is now B2) |
| Contract-out surfaces (R1–R6) with no task | 0 |
| Done-means (1–18) with no executing test | 0 |
| Plan code that raises against the live P1 API | **0** |
| Dangling references (called-but-undefined) | 1, and it is B1 |

The single highest-value thing the brief asked for — plan code that would raise against
the live P1 API — **is not present**. Every `observe_path`, `record_file`, `hash_file`
and `append_event` call site matches the code in `src/database_agent/` as it stands
today. The three blocking findings are two self-contradicting guards and one missing
import line.

Reviewed against: P3 SPEC, `01-product-design-structured.md` (§1.1, §1.2, §8.2, §8.6),
the live P1 implementation in `src/database_agent/` (150 tests passing, verified
`python3 -m pytest -q` → `150 passed in 1.31s`), `11-ops-runtime.md`,
`10-i4-learning-ops.md`, and `13-p2-p3-plan-robustness.md`.

### Verification method — the plan was executed, not only read

Every one of the plan's 55 Python code blocks was extracted and assembled into a
runnable package outside the repository (`$SCRATCH/build/`), applying each task's
"Modify" edits in order: `basic_record.py` and `scan.py` were patched exactly as
Tasks 11, 12 and 13 instruct, `exclusion.py` took Task 5's two insertions, and each
`schema.py` reached its Task 13 state. P1 was copied unmodified from
`src/database_agent/`, together with the repo's `tests/conftest.py`. **No file in
`/Users/jy/GRAPH AGENT` was written except this review.**

Result — `python3 -m pytest tests/p3 -q`:

| Run | Outcome |
|---|---|
| Plan as written | **45 failed, 98 passed, 8 errors** |
| With only B1's two missing imports added | **2 failed, 149 passed** — the two remaining failures are exactly B2 and B3 |
| With B1, B2 and B3 fixed as the edit order below prescribes | **151 passed, 0 failed** |

So the plan's substance is sound and its defects are three, precisely located. The
150 P1 tests in the repo also still pass (`python3 -m pytest -q` → `150 passed`),
confirming P3 needs no P1 change to build.

---

## Blocking findings — do not execute these as written

### B1 — `basic_record.py` uses `unicodedata`, `datetime` and `timezone` without importing them (Task 10)

**Where:** PLAN.md Task 10, Step 3, `src/scan_agent/basic_record.py`.

The module's import block is exactly:

```python
import json
import sqlite3
from collections.abc import Callable
from pathlib import Path, PurePath

from database_agent.events import append_event
from database_agent.files_table import get_file, observe_path

from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM, event_defaults
```

and the body of `record_basic_record` then calls:

```python
        normalized_filename=unicodedata.normalize("NFC", path.name),
        ...
        observed_timestamps=json.dumps({
            "mtime": datetime.fromtimestamp(observed.mtime, timezone.utc).isoformat(),
        }),
```

`unicodedata`, `datetime` and `timezone` are all undefined names. The first non-excluded
file in any scan raises `NameError: name 'unicodedata' is not defined`.

**Why blocking:** this is the single function that produces R2. Every Done-means that
touches a `files` row (1, 10, 11, 17, 18) fails, and so do Tasks 11–18, which all scan.
`tests/p3/test_p3_basic_record.py` as written cannot go green.

**Fix:** add `import unicodedata` and `from datetime import datetime, timezone` to
`basic_record.py`'s import block.

### B2 — Task 17's `test_p3_defines_no_filename_normalization` fails against Task 10's own code

**Where:** PLAN.md Task 17, `tests/p3/test_p3_no_invention.py`, versus Task 10,
`src/scan_agent/basic_record.py`.

Task 17 asserts, over the concatenated text of every `src/scan_agent/*.py`:

```python
def test_p3_defines_no_filename_normalization():
    # SPEC Q1 is OPEN: Unicode form, case folding, whitespace and separator collapse,
    # extension retention and diacritic handling are all unstated.
    source = all_source()
    assert "unicodedata" not in source
    assert "casefold" not in source
    assert "NFC" not in source and "NFD" not in source
```

Task 10 writes, in `src/scan_agent/basic_record.py`:

```python
        normalized_filename=unicodedata.normalize("NFC", path.name),
```

`all_source()` is `"\n".join(path.read_text() for path in SOURCE_DIR.glob("*.py"))`,
so both `"unicodedata"` and `"NFC"` are present and the guard fails on its first two
assertions.

**Why blocking:** this is not a token false positive — it is the substantive
contradiction the guard exists to catch. Task 10 answers **P3 SPEC Q1** (*"`normalized
filename` is undefined … Unicode form, case folding, whitespace and separator collapse,
extension retention, and diacritic handling are all unstated"*) by choosing NFC in P3's
own code, which the SPEC says is open and Task 17's own prose says P3 must not do
(*"P3 does not ratify that choice and defines no normalization of its own; OQ1 stays
open"*). An executor hitting this will "fix" it by deleting or narrowing the guard —
Task 17 Step 3 explicitly tells them the fix is never in the guard — and Q1 gets
silently answered.

**Root cause:** the patch for P1's new `record_file` signature landed in Task 10 only.
Before the patch, P1 derived `normalized_filename` itself and P3 passed nothing; now
P3 must supply it, and the plan chose NFC without reconciling Task 17.

**Fix (a decision the plan must make explicitly, not a token edit):** make
`normalized_filename` a caller-supplied strategy exactly as `mime_type_for` and
`scan_state` already are — e.g. a required `normalize_filename` keyword on
`record_basic_record` / `scan`, with the test fixtures supplying
`unicodedata.normalize("NFC", ...)`. That keeps Q1 open in the same shape Q6 and Q4
are already held open in, keeps Task 17's guard green unchanged, and keeps P1's
required keyword satisfied. Deleting the guard's `unicodedata`/`NFC` assertions
instead would close Q1 by accident.

### B3 — Task 7's `test_a_dataless_entry_is_reported_as_dataless_and_never_opened` fails on its own module's docstring

**Where:** PLAN.md Task 7, `tests/p3/test_p3_corpus_source.py` versus
`src/scan_agent/corpus_source.py`.

The test asserts:

```python
    import scan_agent.corpus_source as module
    assert "hash_file" not in Path(module.__file__).read_text()
```

Task 7's own implementation, in `FilesystemCorpusSource.entries`, has the docstring:

```python
        `follow_symlinks=False` throughout: a symlink is reported as KIND_OTHER, so
        it is never descended (a loop would make traversal non-terminating) and never
        handed to `hash_file`. SPEC Q7 stays open; this is termination, not policy.
```

The literal `hash_file` is in the file, so the guard fails. Verified by execution
(see *Verification method* below): with only B1's missing imports added, this is one
of exactly two remaining failures across the whole assembled plan.

**Why blocking:** Task 7 Step 4 says "Expected: PASS — 8 passed". It cannot pass.
Unlike the analogous guards elsewhere in the plan (Task 13's `test_p3_holds_no_threshold`
and Task 16's `test_the_module_starts_no_thread`, both of which carry an explicit
comment reconciling the docstring against the token list), this one has no such
reconciliation, so an executor has no signal about which side to change.

**Fix:** the assertion is testing "this module does not hash", and a prose mention is
not a call. Either rephrase the docstring to say "never handed to P1's hasher", or
narrow the assertion to `"hash_file(" not in ...`. The docstring rewrite is preferable
— it keeps the guard blunt, and the plan already uses `assert "hash_file" not in source`
in the same shape in Task 17.


---

## Non-blocking findings

### N0 (highest severity of the non-blocking set) — one unreadable subdirectory aborts the whole scan with an unhandled `PermissionError`, and records no deferral

**Where:** PLAN.md Task 9, `_walk_root` in `src/scan_agent/traversal.py`:

```python
        try:
            entries = source.entries(directory)
        except (FileNotFoundError, NotADirectoryError):
            yield Deferred(directory, True, DEFERRED_PATH_ABSENT)
            continue
```

`PermissionError` is not caught. Task 8's `require_access` checks only the *selected
roots*, not every directory beneath them, so a single unreadable subdirectory anywhere
in the tree propagates out of `walk` and out of `scan`.

**Observed, on the assembled build** (corpus containing `ok.txt` and a `locked/`
directory at mode `0o000`):

```
RAISED: PermissionError [Errno 13] Permission denied: .../corpus/locked
files rows: 1
scan_runs: ('93de17e3-…', None)     <- completed_at is NULL
deferrals: 0
```

The scan run stays open forever, one `files` row is already committed, and **nothing
on the record says `locked/` was skipped**. That is precisely §8.6's named failure:
*"no unscanned file reads as one that was understood and found unimportant."* Task 9's
own prose argues this case for the *root* (*"a corpus quietly missing a whole root is
exactly that failure"*) and then leaves the subdirectory case unhandled.

**Not blocking** only because every plan test builds its corpus with default
permissions, so the build goes green and the failure waits for the first real Mac
scan — `~/Library` alone will produce it.

**Fix:** add `PermissionError` to the caught tuple with its own deferral reason, or
extend `DEFERRED_PATH_ABSENT`'s sibling set with a third reason for "not readable".
Note this coins one more deferral reason, which the SPEC does not name — the same
latitude Task 9 already took for Q7 and Q14, and it should be recorded the same way.

### N1 — Task 17's "Divergence recorded, not fixed here" block describes a P1 that no longer exists

**Where:** PLAN.md Task 17, the block-quoted paragraph above Step 1.

It says:

> P1's **plan** has `record_file` call `path.stat()` and `hash_file(path, ...)` itself,
> deriving filename, normalized filename, extension, size, timestamps and content hash
> from the path rather than storing what P3 observed. That is P1 re-deriving six of
> P3's ten. … Related: P1's `record_file` normalizes with
> `unicodedata.normalize("NFC", ...)`, which **answers P3 OQ1**.

The live P1 (`src/database_agent/files_table.py:65-118`) does none of that. Its
signature is

```python
def record_file(conn, path, *, filename, normalized_filename, extension,
                observed_size, observed_timestamps, parent_folder_context,
                mime_type, detected_format, scan_state, materialized,
                content_hash=None) -> str:
```

with the docstring `**P1 derives none of the R2 record.**`, and
`src/database_agent/files_table.py:29-31` carries an explicit
`NOTE: P1 deliberately has no timestamp/filename derivation helper.` The only thing
`record_file` still derives is the content hash (which P3's own SPEC assigns to P1)
and `volume_id_for(path)` (P1's field under §8.2).

The divergence this paragraph reports is **dead** — P1 fixed it. Leaving the text in
tells the executor P1 answers OQ1, which is exactly the mistaken premise that produced
B2. Delete the paragraph and replace it with the real current state: P1 requires the
five R2 fields as keywords with no default, so P3 is now the *only* possible author of
`normalized_filename`, and Q1 must therefore be held open at P3's own boundary (B2).

The same stale claim appears a second time, in **Known gaps, carried deliberately**:
*"**P1 re-derives six of P3's ten fields** (Task 17) ... The drift test catches a
disagreement; the divergence is P1's to resolve."* Delete that bullet too.

### N2 — the consume table still advertises three `scan_usage` functions P3 imports nowhere

**Where:** PLAN.md, *What P3 consumes from P1*:

```text
database_agent.scan_usage  start_scan(conn) -> str
                           sample_scan_resources(conn, scan_id) -> None
                           scan_resource_usage(conn, scan_id) -> sqlite3.Row
```

No module in `src/scan_agent/` imports `database_agent.scan_usage`, and Task 3's
`test_p3_publishes_no_scan_identity_and_joins_none` actively asserts
`"database_agent.scan_usage" not in source` for `run.py`. This is `13`'s **P3-I**,
still live and unrepaired: an agent executing Task 1 from the header will wire
`start_scan` because the header told it to, and then Task 3's guard will fire with no
explanation of why.

**Fix:** delete the three lines. If the intent is to record that these exist and are
deliberately unused, say that in the prose paragraph below the block, not in a table
headed "consumes".

### N3 — `discovery` is appended once per **file version**, not once per file, and the test that would catch it does not

**Where:** PLAN.md Task 10, `_already_discovered` in `basic_record.py`:

```python
def _already_discovered(conn: sqlite3.Connection, file_id: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM events WHERE file_id = ? AND event_type = 'discovery' LIMIT 1",
        (file_id,),
    ).fetchone() is not None
```

The key is `file_id`. P1's `observe_path` mints a **new** `file_id` when the bytes at
a path change (`src/database_agent/files_table.py:213-224`), so a file whose content
changes gets a **second** `discovery` event.

**Observed** on the assembled build - two files scanned twice, one of which changed
content between scans:

```
  discovery                          P3   3
```

The SPEC's own table glosses `discovery` as *"a file enters the corpus"* (§1.1). A
file already in the corpus does not enter it again. Task 10's
`test_discovery_is_appended_once_per_file` scans an **unchanged** corpus twice, so it
never exercises the case its own name promises.

**Not blocking** - it is a defensible reading (§1.2's record is per *file version*, so
per-version discovery is coherent), and nothing downstream is specified to count these
rows. But the name of the test and the behaviour of the code disagree, and that is the
kind of gap this project has been bitten by. Either rename the test to
`test_discovery_is_appended_once_per_file_version` and say so in the prose, or key the
check on path history rather than `file_id`.

### N4 — SPEC "Serialization" asks R1-R4 and R6 to round-trip; the plan round-trips R3, R4 and R6 only, and only R2's absence is disclosed

**Where:** PLAN.md Task 15 versus P3 SPEC, *Contract out -> Serialization*:

> **Serialization.** R1-R4 and R6 must serialize into and re-assert from a P2 replay
> bundle (§8.5), `curation_signal` included.

`snapshot_from` serializes directory listings plus per-path `content_hash`, and
`replay` re-asserts exclusion verdicts (R3), cache verdicts (R4) and the inventory
(R6). **R2** is deliberately absent and the plan says so at length (Known gaps, and
Task 15's prose). **R1 is absent and undisclosed**: `snapshot_from` carries no
`sources`, `candidate_roots`, `cross_folder_moves` or `selected_by`, and every replay
test re-creates the selection by hand —

```python
    selection = record_selection(harness, sources=[populated], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
```

— which means the harness must already know the corpus boundary the bundle was
supposed to carry.

**Not blocking:** Done-means 14 asks only for identical exclusion, cache and curation
verdicts, and those reproduce. But the Serialization sentence is a separate contract
obligation with no task, and R1 is three JSON fields - cheap to add to `snapshot_from`
and to re-assert in `replay`. At minimum, add R1 to the Known-gaps list beside R2 so
the omission is a decision rather than an oversight.

### N5 — `11-ops-runtime.md` §7's "two scans do not run on the same root" has no task and no mention

**Where:** absent from PLAN.md entirely; also absent from the P3 SPEC's *Runtime
obligations* paragraph, which binds only §1 (Full Disk Access), §4 (session watch) and
§5 (dataless).

`11-ops-runtime.md` §7 states: *"**Two scans do not run on the same root.** A second
scan of an in-flight root is refused. A scan of a disjoint root may run."* Scanning is
P3's operation and `scan_runs` already carries `started_at` / `completed_at`, so P3 is
where the refusal would live. Nothing in the plan refuses it; two concurrent `scan()`
calls on one root will interleave writes into `stat_cache_verdicts` and
`exclusion_verdicts` under two different `scan_run_id`s.

**Not blocking** for Tasks 1-18 (single-threaded tests), and it is arguably a **SPEC
gap first** - the SPEC omitted §7 when it enumerated the runtime obligations. Flagged
for the lead to decide whether §7 lands on P3 or on the P13 process that drives it.

### N6 — Done-means 17's "another part re-derives one of them" is no longer proved by any test

**Where:** PLAN.md Task 17, `test_the_observed_values_and_the_stored_values_are_the_same_values`.

Done-means 17 reads: *"a fixture in which another part re-derives one of them fails."*
The drift test compares `os.stat(document)` taken in the test against
`files.observed_size` and `stat_cache_verdicts.observed_modification_time`. Both sides
read the same path with the same syscall, so the test passes whether or not a second
derivation exists - `13`'s original observation, and it survives the P1 change.

What actually discharges Done-means 17 now is **P1's signature**: `record_file` and
`observe_path` require `filename`, `normalized_filename`, `extension`,
`observed_size` and `observed_timestamps` as keywords with no default
(`src/database_agent/files_table.py:65-79, 146-160`), so P1 *structurally cannot*
re-derive them. The source guards (`test_p3_hashes_nothing_itself`,
`test_p3_determines_no_mime_type`) only see `src/scan_agent/`, so they cannot see
another part either.

**Fix (documentation, not code):** say in Task 17 that Done-means 17 is discharged by
P1's required-keyword API plus P3's source guards, and that the drift test is a
regression check on P3's own hand-off rather than the proof. Leaving it as-is invites a
later reader to trust a tautology.

### N7 — the session watch observes paths §1.1 excludes from the corpus

**Where:** PLAN.md Task 16, `SessionWatch.open` / `poll`, which use bare `os.walk(root)`
over the selected roots with no exclusion applied.

A `node_modules` or `.git` directory inside a watched root is enumerated into
`self._observed`, and any change under it authors an `external modification detection`
event. `11-ops-runtime.md` §4 says P3 *"watches the selected roots"* without narrowing,
and §1.1's exclusion is written as a rule for *scanning*, so this is defensible - but
it means P13 (which §4 says *"marks review items whose `file_id` (or path) appears in a
detection as stale"*) will receive detections for paths that have no `file_id` and can
never be review items. Task 16's own `test_a_detection_is_not_a_rescan` creates a
`node_modules` mid-session and then never notifies on it, so the case is set up and not
asserted.

**Not blocking.** Worth one sentence in Task 16 recording which reading was taken.

### N8 — `test_exhaustion_relaxes_no_exclusion_rule` passes for the wrong reason

**Where:** PLAN.md Task 14, `tests/p3/test_p3_summary.py`.

The corpus is `node_modules/buried.txt` plus `a.txt`, and the budget predicate returns
True on its second call. Entries are sorted by path, so `a.txt` is observed on call 1
and `node_modules` is reached on call 2 - at which point it is recorded as
**`scan budget exhausted`**, not as an exclusion. The assertion
`assert not any("node_modules" in p for p in paths)` then holds because the directory
was deferred, not because the §1.1 rule fired, and
`assert ... ["files_deferred"] >= 0` is vacuous.

**Not blocking** (the property is genuinely true, and Task 9's pruning tests prove it
directly). But the test as written would still pass if the exclusion rule were deleted.
Order the fixture so `node_modules` is reached before the budget trips, and assert the
exclusion verdict exists.


---

## Already sound — do not re-litigate

Each of these was checked against the live code or the design text, not assumed.

| # | What holds | Evidence |
|---|---|---|
| S1 | **Every event P3 produces names P3.** All four reserved types, `component_version` never null. | Executed probe on the assembled build: `discovery/P3 3`, `stat observation/P3 5`, `hashing/P3 3`, `external modification detection/P3 3`; `select distinct subsystem from events` -> `['P3']`; zero null `component_version`. |
| S2 | **`event_defaults()` satisfies the live writer.** It supplies `subsystem`, `component_version`, `observed_at`; every call site supplies `event_type` + `explanation`; no call site passes a key outside `_WRITABLE`. | P1's `append_event` raises `MalformedEvent` on an unrecognised field and on any empty member of `("event_type","subsystem","component_version","observed_at","explanation")` (`src/database_agent/events.py:106-146`). 149 tests exercise every append path and none raises. |
| S3 | **Every `observe_path` / `record_file` call matches the live signature.** `filename`, `normalized_filename`, `extension`, `observed_size`, `observed_timestamps` are all supplied; `author` and `component_version` are supplied; `materialized=not observed.dataless`. | `src/scan_agent/basic_record.py` in the assembled build imports and runs against unmodified `src/database_agent/`. This is the risk the brief called highest-value; **it is clean**. |
| S4 | **`scan_state="superseded_content"` is never supplied**, so `ReservedScanState` never fires. | Task 17 `test_p3_holds_no_scan_state_enumeration` forbids the literal; green. |
| S5 | **P3 never calls `hash_file` and never passes `materialized=True` for a dataless path.** | `test_p3_hashes_nothing_itself` green; the dataless branch in `scan.py` `continue`s before `record_basic_record`. |
| S6 | **P3 writes no `extraction_runs` row and names no `completeness`.** P4 OQ6 stays open. | `test_p3_writes_no_extraction_run_and_names_no_completeness` green over all of `src/scan_agent/`. |
| S7 | **P3 SPEC Q4 stays open.** The caller supplies one `scan_state` value; `scan_agent` holds no enumeration. | `test_p3_holds_no_scan_state_enumeration` green; `scan_state` is a required keyword with no default (`test_mime_strategy_and_scan_state_are_required`). |
| S8 | **P1 OQ9 is respected.** No cross-session logic on `volume_id`; P3 reads it for nothing. | `test_p3_reads_no_volume_identifier` green. |
| S9 | **§1.1's literals are verbatim and in the design's order.** Eleven directory names, four project-root markers, five named-and-empty categories. | Checked word-for-word against `01-product-design-structured.md` §1.1. |
| S10 | **No invented threshold, ceiling or vocabulary.** `curation_signal` is `undetermined` for every directory; the budget is a caller predicate with no default; no `mimetypes`, no signature table, no software-material extension list. | `test_p3_holds_no_threshold_and_no_software_material_list`, `test_p3_holds_no_ceiling_and_no_threshold`, `test_p3_determines_no_mime_type`, `test_budget_exhausted_is_required_with_no_default` — all green. |
| S11 | **The stat cache is a difference test, disjunctive, and never a newer-than test.** mtime backwards recomputes. | Done-means 7/8/9 tests green; the operator guard `test_the_comparison_is_never_a_newer_than_test` green. |
| S12 | **MINOR 11 is honoured — one name, one concept.** `parent-folder context` is the published name (function `parent_folder_context`, keyword `parent_folder_context=`); `directory_position` appears only as P1's column, in SQL and PRAGMA reads. §1.2's spelling survives only inside a verbatim quotation. | grep over PLAN.md: 4 `directory_position` occurrences, all column-level; 5 `parent_folder_context`, all API-level. |
| S13 | **P2's `corpus_form` spellings are correct, not invented.** `snapshot` / `metadata_safe`. | `planning/parts/P2-eval-replay-harness/SPEC.md:186` — `corpus_form  snapshot \| metadata_safe  §8.5`. |
| S14 | **Contract coverage is complete.** R1->T2, R2->T10, R3->T4/T5, R4->T11, R5->T14, R6->T13. All eighteen Done-means have at least one executing test. | Traced individually; no Contract-out surface and no Done-means is without a task. |
| S15 | **`SF_DATALESS = 0x40000000` is the real macOS constant**, and detection is `stat`-only. | macOS `sys/stat.h`; the flag sits outside `SF_SETTABLE`, which is why the plan's `FakeStat` fixture is the right call rather than a shortcut. |
| S16 | **Exclusion prunes rather than filters**, on both sides of the scan, and a verdict cannot be deleted. | `test_a_pruned_directory_is_never_listed`, `test_the_same_rules_fire_on_a_candidate_root`, `test_a_verdict_is_never_deleted` — green. |
| S17 | **P3 modifies no P1 file.** The 150 P1 tests pass unchanged with `scan_agent` present. | `python3 -m pytest -q` in the repo -> `150 passed`; the assembled build imports `database_agent` byte-identical. |
| S18 | **The two `external modification detection` rows on a content change are real and are already disclosed.** P3's (keyed on the stat difference) and P1's (keyed on the supersede), both authored `P3`, distinguishable by `explanation`. | Reproduced in the probe; Task 12 documents it and Known-gaps repeats it. Do not "optimize" it away without deciding the seam. |

---

## Stale findings from `13-p2-p3-plan-robustness.md`

`13` was written on 2026-08-19 against a P1 that has since changed twice. Re-verified:

| `13` ID | Status now | Why |
|---|---|---|
| **P3-A** — "P1 `record_file` re-derives filename, normalized filename, extension, size, timestamps, hash; do not execute Task 10" | **DEAD** | Live `record_file`/`observe_path` require all five as keywords with no default and derive none (`src/database_agent/files_table.py:65-79, 146-160`), with an explicit `NOTE: P1 deliberately has no timestamp/filename derivation helper` at line 29. Task 10 is now safe to execute — after B1. |
| **P3-C** — "Q1 vs P1 NFC: the open question is already answered in another part's code" | **MOVED, not dead** | P1 no longer normalizes. P3's own Task 10 now does, which is **B2**. The concern is live; its owner changed from P1 to P3. |
| **P3-B / P3-I** — stale `scan_usage` lines in the consume table | **STILL LIVE** | Verified: the three lines are still in *What P3 consumes from P1*, and no `scan_agent` module imports `database_agent.scan_usage`. See **N2**. |
| **P3-D** — `.app` bundles and packages are descended (Q7) | **STILL LIVE**, correctly disclosed | Known gaps records it; §1.1 supplies no rule and the plan invents none. Needs a SPEC decision before v1, not a plan edit. |
| **P3-E** — legacy `.Foo.pdf.icloud` placeholders undetected | **STILL LIVE**, correctly disclosed | `11` §5 names only the dataless flag. Correct refusal. |
| **P3-F** — metadata-safe replay writes no `files` row; R4 `file_id` NULL | **STILL LIVE**, correctly disclosed | Confirmed by `test_a_metadata_safe_replay_writes_no_files_row`, green. |
| **P3-G** — two `external modification detection` rows on a content change | **STILL LIVE**, correctly disclosed | Reproduced (S18). |
| **P3-H** — P3 samples no `scan_resource_usage` counter | **STILL LIVE** | `scan()` never calls P1's `start_scan` / `sample_scan_resources`, so §8.6's six counters are never recorded for a P3 scan unless some other caller opens the row. Traced to OQ16 in Known gaps; still a real §8.6 observability hole. |
| `13`'s "wave defect: unpublished scan identity" | **STILL LIVE** | Task 3 holds OQ16 open and records the `11` §3 conflict honestly. Nothing to fix in this plan; it needs a SPEC decision. |
| `13`'s "Graphify path-check absent" | **STILL ABSENT** | Unchanged; a process note, not a plan defect. |

### One correction to the brief

The brief states that `mime_type_for(...)` is *"used once and defined zero times"*. That
is not what the plan contains. `mime_type_for` is a **required keyword parameter**,
declared in two signatures —

```python
def record_basic_record(conn, observed, *, mime_type_for: Callable[[Path], str | None],
                        scan_state: str) -> str:
def scan(conn, selection_id, *, source, mime_type_for: Callable[[Path], str | None],
         scan_state, budget_exhausted) -> str:
```

— and every one of the nine test files that calls `scan` defines its own `fixture_mime`
to supply it (PLAN.md lines 2409, 2855, 3498, 3864, 4132, 4483, 4831, 5065). It is the
mechanism that holds SPEC Q6 open, and it is correct.

**There are no other dangling references.** After adding B1's two imports, an AST
scope-walk over all eighteen assembled `src/scan_agent/*.py` modules reports zero
undefined names, and every module executes under the plan's own tests. B1 was the only
one.

---

## Edit order

Nothing below is a redesign. Items 1-3 must land before Task 1 is executed; the rest can
land as their tasks are reached.

| # | Where | Change | Unblocks |
|---|---|---|---|
| 1 | Task 10, `basic_record.py` | Add `import unicodedata` and `from datetime import datetime, timezone`. | **B1** — Tasks 10-18 |
| 2 | Task 10 + Task 17 | Decide Q1 explicitly. Recommended: make filename normalization a required caller-supplied `normalize_filename` keyword on `record_basic_record` / `scan`, matching `mime_type_for` and `scan_state`; test fixtures supply NFC. Do **not** weaken Task 17's guard. | **B2** — Q1 stays open |
| 3 | Task 7, `corpus_source.py` docstring | Rewrite `never handed to \`hash_file\`` as `never handed to P1's hasher`. | **B3** — Task 7 goes green |
| 4 | Task 17 prose + Known gaps | Delete the two "P1 re-derives six of P3's ten fields" passages; replace with the real state (P1 requires the five fields, derives none). | **N1** — stops the next reader repeating B2 |
| 5 | *What P3 consumes from P1* | Delete the three `database_agent.scan_usage` lines. | **N2** — Task 1 not mis-wired |
| 6 | Task 9, `traversal.py` | Catch `PermissionError` around `source.entries(directory)` and record a deferral for it. | **N0** — first real Mac scan |
| 7 | Task 15 Known gaps | Add R1 beside R2 as a Serialization surface the replay does not carry, or serialize it. | **N4** |
| 8 | Task 17 prose | State that Done-means 17 is discharged by P1's required-keyword API plus P3's source guards, not by the drift test. | **N6** |
| 9 | Tasks 10, 14, 16 | The three test/behaviour mismatches: `discovery` per version (N3), the exhaustion test that passes for the wrong reason (N8), the watch's unexcluded observation (N7). | **N3, N7, N8** |
| 10 | Lead / SPEC | Decide whether `11` §7's "two scans do not run on the same root" lands on P3. | **N5** |

**This edit order was verified, not proposed.** Items 1, 2 and 3 were applied to the
assembled build — item 2 in exactly the shape recommended above (a required
`normalize_filename` keyword on `record_basic_record` and `scan`, with each test file
supplying `unicodedata.normalize("NFC", ...)`) — and Task 17's guard went green with
**no change to the guard**. Result: **151 passed, 0 failed**.

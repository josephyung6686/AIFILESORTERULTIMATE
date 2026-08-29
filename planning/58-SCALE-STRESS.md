# 58 — Scale Stress

**What this is.** The largest fixture corpus anywhere in the test suite is 100 files;
almost every test uses two or three. This document reports what happens when the same
real code is driven over corpora with the size and the shape of a disk somebody owns.

**Harness:** `tests/integration/test_scale_stress.py` — 17 tests, **skipped by default**.

```
SCALE_STRESS=1 python -m pytest tests/integration/test_scale_stress.py -v -s
```

Default collection is unaffected: `python -m pytest tests/integration/test_scale_stress.py`
reports `19 skipped`. As first measured the harness ran **66 seconds**; 14 failed, 3 passed.

> **Status, after the scan fixes below.** The harness is now **19 tests, 35 seconds,
> 13 fail / 6 pass**. Two tests were added (one green, one red) and two previously
> failing tests now pass. Findings **1a is fixed and 1b is improved but not closed**;
> findings 2, 3 and 4 (retrieval, tree health, and the nonsense/threshold items) are
> untouched and reproduce exactly as measured. See **Status of each finding** below.

**Method.** Every test drives the real code — the real `scan` over a real directory
tree, the real `vertical_options`/`project_branch_preview`/`warnings_for`, the real
`build_destination_index` and `retrieve` over P10's live `Node` records. Timing tests
assert a **complexity curve, never a wall-clock threshold**: each holds one variable
fixed and moves another, so a failure names a cause instead of reporting that something
was slow. Corpora are long-tailed on purpose — a fat `Screenshots` folder, deep project
trees, a tail of one-file folders, duplicate basenames, and large duplicate families.
Two findings below are invisible on a uniform corpus.

**Caveat on reproducibility.** `src/tree_design/` and `src/placement/` were being
modified while these measurements ran; `src/placement/pipeline.py` and `fixtures.py`
appeared mid-run. Every placement number below was **re-measured against the tree that
includes them** and reproduced within 8% (retrieval growth x4.0 → x3.9 → x4.2). Numbers
are from a single machine and only the *ratios* are claims.

---

## Ranked: what fails first on a real user's disk

| # | Finding | Severity | Where | Status |
|---|---|---|---|---|
| 1a | Scan is quadratic in corpus size — per-file lookups are unindexed | **Breaks** | `db.py` FILES_DDL / EVENTS_DDL | **FIXED** |
| 1b | Scan is quadratic in duplicate-family size, with a syscall in the inner loop | **Breaks** | `database_agent/files_table.py:244-265` | **3× cheaper, still O(k²)** |
| 2 | Placement retrieval reads and deserialises **every legal node for every file** | **Breaks** | `placement/index.py:236`, `placement/retrieval.py:82` | verified, open |
| 3 | Tree health / §5.9 warnings are quadratic in node count | **Breaks** | `tree_design/health.py:60-80` | verified, open |
| 4 | `example_members` is the entire branch membership | Nonsense | `tree_design/candidates.py:463` | open |
| 5 | Nothing caps how many folders one split creates | Nonsense | `tree_design/routing.py:487` | open |
| 6 | The warning list outgrows the tree it describes | Nonsense | `tree_design/health.py:156` (`warnings_for`) | open |
| 7 | The corpus-scaling budget is read and never enforced | Uncalibrated | `placement/config.py:32` | open |
| 8 | One ceiling key serves the picker and the depth limit; they want opposite values | Uncalibrated | `tree_design/config.py:30` | open |
| 9 | Every §5.9 threshold's only exercised value fails `00`'s own example | Uncalibrated | `tree_design/config.py:39-45` | open |

*(The original numbering listed the two scan quadratics as one item and shifted
everything below by one. They are separated here because one is fixed and one is
not; the prose sections keep their original headings.)*

The first four are the ones that decide whether this product runs at all on a real disk.
**Items 1 and 2 matter most because the scan is the first thing the product does** — no
downstream quality matters if the corpus never finishes being read.

---

## 1. The scan does not scale. Two independent quadratics.

`scan_agent.scan` walks with a `deque` and has no recursion limit — traversal itself is
fine. The cost is entirely in `database_agent.files_table.observe_path`, which resolves
each observed file's identity, and it is quadratic twice over for different reasons.

### 1a. `files.current_path` has no index

`observe_path` runs two `WHERE current_path = ?` queries per observed file
(`files_table.py:258` and `:283`), and `prior_observation` joins on the same column.
`EXPLAIN QUERY PLAN` is unambiguous:

```
SELECT 1 FROM files WHERE current_path = ? AND scan_state != ?   ->  ['SCAN files']
SELECT file_id FROM files WHERE current_path = ? AND scan_state != ?  ->  ['SCAN files']
```

`files` carries `sqlite_autoindex_files_1` and `files_content_hash` — nothing on
`current_path`. Every file read costs a full pass over every file already recorded.

**The diagnosis was right and the query named was the smaller of two.** Timing every
statement the scan issues, at 1,000 files and again at 4,000, found the dominant term
somewhere else entirely:

```
SELECT 1 FROM events WHERE file_id = ? AND event_type = 'discovery' LIMIT 1
        1,000 files:  70.4 us per call        4,000 files:  540.9 us per call
```

`scan_agent/basic_record.py:38` asks that once per file admitted, `events` carries **no
index at all** beyond its integer primary key, and it grows about three rows per file —
so each file read costs a pass over three times the corpus. It is a bigger term than
either `current_path` lookup, and `file_path_history` (`files_table.py:329`) asks the
same table the same way. Both are fixed by one index on `events (file_id)`.

**FIXED**, in `database_agent/db.py`:

```sql
CREATE INDEX IF NOT EXISTS files_current_path ON files (current_path);
CREATE INDEX IF NOT EXISTS events_file_id     ON events (file_id);
```

Neither weakens R6: an index adds no way to update or delete an event.

Measured with **every file's content unique**, so no duplicate family can contribute:

| files | before | after |
|---|---|---|
| 1,000 | 0.82 s — 1,221 files/s | 0.68 s — 1,464 files/s |
| 4,000 | 6.26 s — 639 files/s | 3.01 s — 1,328 files/s |

Per-file cost grew **x1.9 before and x1.1 after**. Every per-file SELECT is now flat
within noise across the 4× range (3.9→4.1 µs, 5.5→5.7 µs, 5.8→6.0 µs, 6.1→6.4 µs); what
is left is per-file INSERT cost, which is constant.

*Tests:* `test_scan_stays_linear_when_every_file_is_unique` (**now passes**), and two
new query-plan tests in the DEFAULT suite —
`tests/test_db.py::test_identity_lookups_by_path_search_an_index_instead_of_scanning`
and `::test_the_per_file_event_lookups_search_an_index_instead_of_scanning`. They assert
`EXPLAIN QUERY PLAN` reports `SEARCH` rather than `SCAN`, which is the property rather
than the schema text, and both go red if either index is removed.

### 1b. Identity resolution is O(k²) in the duplicate family, with three syscalls per step

`observe_path` reads every row sharing the observed content hash and then walks that list
twice with a filesystem call in each pass — `_is_same_file` lstats two paths
(`files_table.py:34`), and the dead-path branch stats a third:

```python
same_hash = conn.execute(
    "SELECT * FROM files WHERE content_hash = ? AND scan_state != ?", ...).fetchall()
existing = next((row for row in same_hash if row["current_path"] == observed), None)
if existing is None:
    existing = next((row for row in same_hash if _is_same_file(row["current_path"], path)), None)
...
    existing = next((row for row in same_hash if not Path(row["current_path"]).exists()), None)
```

Isolated by holding the file count **fixed at 2,000** and varying only how many files
share a content hash:

| families | files per family | before | after |
|---|---|---|---|
| 500 | 4 | 3.05 s | 2.51 s |
| 1 | 2,000 | **25.25 s** | **8.87 s** |

**x8.3 slower for the same 2,000 files** before, **x3.5 after** — purely from duplicate
structure. A profile at 4,000 files showed 1.24 M `Path.exists()` and 2.48 M `lstat`
calls for 3,473 files, about 357 stat calls per file, rising with corpus size.

**PARTLY FIXED — 3× cheaper, same shape.** `observe_path` now:

* answers the exact-path case with an indexed
  `WHERE current_path = ? AND content_hash = ?` and **never loads the family at all**
  when the file is unchanged at the path it was found at — the steady state a real disk
  is in most of the time;
* loads `file_id, current_path` instead of all sixteen columns when it does walk;
* lstats the observed path **once per family** instead of once per candidate; and
* folds the dead-path pass into the inode pass. A row whose `lstat` fails cannot
  `exists()` either, and a live non-symlink always `exists()`, so only a *symlink*
  candidate now costs the extra syscall the third pass used to cost every candidate.

Counted rather than timed, which is the sharper instrument because the syscalls are the
cause and the seconds are only the symptom:

| family size | syscalls per file, before | after |
|---|---|---|
| 200 | 300 | 102 |
| 800 | 1,200 | 402 |

**The constant fell 3× and the curve did not move: still exactly x4.0 per-file for a
4× family.** The residual O(k) is `_is_same_file` asking the filesystem, once per
candidate, whether the recorded path and the observed path are the same inode. Removing
it needs a decision this work did not have standing to take, and there are two ways:

1. **Persist the inode** and answer the question with an indexed lookup. Blocked by an
   existing pinned test —
   `test_a_symlink_and_its_target_are_recorded_as_two_file_versions`
   (`tests/test_adversarial.py:1177`) asserts `files` has no `inode`/`st_ino`/
   `real_path`/`is_symlink` column, and calls the underlying SPEC question unsettled.
2. **Narrow the candidates by path spelling** — NFC-normalise and casefold, then still
   confirm by `lstat`, so a non-folding filesystem is unaffected. This is exact for the
   case `_is_same_file`'s docstring is written about, and it silently changes two cases
   it is not: **hard links** (two entries, one inode — collapsed to one row today) and
   **symlinked directory components**, which on macOS includes `/tmp` → `/private/tmp`.
   Neither has a test today. Changing them is a design ruling, not an optimisation.

Until one of those is taken, admitting a large duplicate family stays quadratic. What is
now linear is *re-observing* one — see
`test_reobserving_an_unchanged_duplicate_family_does_not_read_the_family`, which reads
**1 row per file at both 200 and 800**, and read 200 and 800 before the change.

This is not an exotic input. §2.9's duplicate families and §8.3's identical-file
collisions are the design stating that real corpora contain many identical files, and
they do: empty files, `.DS_Store`, stub configs, repeated downloads, thumbnails,
`node_modules` artefacts. A 20,000-member duplicate family — ordinary — costs
2×10⁸ lstat pairs.

*Tests:* `test_scan_is_quadratic_in_the_size_of_a_duplicate_family` (still fails, x3.5
against a x2.0 bar), the new counting test
`test_identity_resolution_does_not_stat_the_whole_duplicate_family` (still fails, x4.0),
and the new `test_reobserving_an_unchanged_duplicate_family_does_not_read_the_family`
(**passes**, and goes red if the fix is reverted).

### 1c. Combined, on a disk-shaped corpus

Long-tailed corpus (35% screenshots, deep project trees, tail of tiny folders, duplicate
basenames): **3,473 files recorded in 19.6 s — 177 files/s** before; **7.3 s — 477
files/s** after, a 2.7× improvement. This corpus is duplicate-heavy by construction, so
it carries the residual 1b cost as well as the fixed 1a one.

*Test:* `test_the_scan_finishes_a_realistic_disk_shaped_corpus` — **now passes**.

**Fix for 1a is two lines** — an index on `files (current_path)` and one on
`events (file_id)`; both are now in `db.py`. 1b still needs `observe_path` to stop
walking the family, which needs one of the two rulings above.

---

## 2. Placement retrieval is O(files × nodes)

`00`:105 is explicit about what §6.2's index is for:

> the engine retrieves the few most relevant approved destination nodes, **rather than
> searching the entire filesystem** or re-inventing a category.

`placement.retrieval.retrieve` opens with `entries_for_plan(conn, plan_version=...)`
(`retrieval.py:82`), and `entries_for_plan` (`index.py:236`) issues **one
`SELECT ... WHERE node_id = ?` and one `json.loads` per legal node**, then `retrieve`
loops over all of them. This happens once **per subject placed**. The retrieval index is
used as a full table read.

| tree size | per-file retrieval |
|---|---|
| 200 nodes | 2.6 ms |
| 800 nodes | 10.9 ms |

**x4.2 for four times the tree** — per-file cost is linear in tree size, so total cost is
files × nodes. Concretely: 10,000 files against an 800-node tree is **1.8 minutes and
8 million SQLite queries** before any scoring, any local graph, or any model call. A
250,000-file disk with a 2,000-node tree projects past **two hours**.

The control confirms the asymmetry: **building** the index is linear (`x1.01` per node)
and takes 25 ms for 800 nodes. The index is cheap to write and expensive to use.

*Tests:* `test_retrieval_does_not_read_every_legal_node_for_every_file` (fails),
`test_building_the_destination_index_scales_with_the_tree` (passes).

**Re-verified at the call sites, and the shape is N+1 queries, not one wide read.**
`legal_node_ids` (`index.py:194-201`) is one query returning every legal node id.
`entries_for_plan` (`index.py:236-241`) is a generator that then calls `entry_for` per
id, and `entry_for` (`index.py:221-234`) issues its own
`SELECT payload ... WHERE plan_version = ? AND node_id = ?` and one `json.loads`.
`retrieve` (`retrieval.py:82`) calls it as its **first statement**, per subject, and
then loops over every entry it got back. Reproduced unchanged after the fixes above:
2.9 ms per file at 200 nodes, 11.9 ms at 800 — **x4.1**.

**The fix, in two steps, both in `src/placement/` (not touched here — that directory has
an owner):**

1. `entries_for_plan` should be one query, not N+1:
   `SELECT node_id, payload FROM placement_index_entries WHERE plan_version = ? AND
   superseded_by IS NULL ORDER BY node_id`, decoded in the loop. This removes ~800
   round trips per file on its own and is behaviour-preserving.
2. `retrieve` should not call it at all. By `retrieval.py:82` the subject's facts, group
   ids and folder labels are already in hand, and `00`:105 says the engine retrieves
   "the few most relevant approved destination nodes, **rather than searching the entire
   filesystem**". The narrowing belongs in SQL — a join from the stated `(field, value)`
   pairs, group ids and casefolded labels to candidate `node_id`s — so the per-file cost
   is the size of the candidate set, not the size of the tree.

---

## 3. §5.11 tree health and §5.9 warnings are quadratic in node count

`tree_design/health.py` recomputes global structure per node:

- `_children(nodes, node_id)` filters **every node** to find one node's children (`:60`).
- `_descendants` calls `_children` once per node it reaches (`:64`).
- `_depth` rebuilds a `{node_id: node}` dict on **every call** (`:75`).
- `warnings_for` runs all three inside a loop over every node.
- `_counts_for_preview` (`candidates.py:335`) calls `branch_counts` once per node, and
  `branch_counts` calls `_children` **and** `_descendants`.

Measured over a preferential-attachment tree (a few fat hubs, a long tail — the shape a
real tree has):

| nodes | counts + warnings |
|---|---|
| 800 | 0.10 s |
| 3,200 | 1.60 s |
| 6,400 | 7.33 s |
| 12,800 | 29.61 s |

**x4.1 per doubling** — clean quadratic. A 50,000-node tree projects to **~7 minutes**,
and this is the canvas the user is sitting in front of waiting for.

The same quadratic reaches the picker through `_preview_warnings`. Two controlled sweeps
separate the causes:

- **Files fixed shape, files vary** (50 folders, 2,000 → 16,000 files): per-file cost
  **x0.76** — flat. *The picker is linear in how many files a branch holds.* This is a
  real result and it passes.
- **Files fixed at 4,000, folders vary** (400 → 1,600 folders): per-folder cost **x3.07**
  — quadratic. 0.018 s at 400 folders becomes 0.219 s at 1,600 and projects to **9 s per
  option** at 10,000 folders, with the ceiling permitting several options.

So the picker's cost is driven by the **width of the split**, not the size of the corpus
— which matters because of finding 6 below.

*Tests:* `test_tree_health_is_linear_enough_to_render_a_real_tree`,
`test_the_picker_is_quadratic_in_the_folders_a_split_would_create` (both fail),
`test_the_picker_is_linear_in_the_files_a_branch_holds`,
`test_tree_health_group_coverage_scales_with_the_accepted_groups` (both pass).

**Re-verified at the call sites.** `_children` (`health.py:60`) filters the whole node
sequence per call. `_descendants` (`:64-72`) calls it once per node it reaches.
`_depth` (`:75-82`) rebuilds `{node_id: node}` on **every** call. `branch_counts`
(`:126`) calls `_children` (`:145`) and `_descendants` (`:146`); `warnings_for` calls
`_children` at `:177` and `:206` and `_depth` at `:197`, inside a loop over every node;
and `candidates.py:361` calls `branch_counts` once per node. Reproduced unchanged:
0.108 s at 800 nodes, 1.767 s at 3,200 — **x4.1 per-node for a 4× tree**.

**The fix, in `src/tree_design/health.py` (not touched here — that directory has an
owner):** build `children_by_parent: dict[str, list[Node]]` and `depth_by_id:
dict[str, int]` **once** from `nodes`, and give `branch_counts` and `warnings_for` a
parameter to receive them. `_descendants` then walks the subtree it actually visits
instead of re-filtering the tree at every step. This is one module, it collapses both
this finding and the picker's width quadratic, and it changes no result — the same
children, the same depths, computed once.

`tree_health`'s group coverage — the §5.11 measure the brief flagged as a possible O(n²)
— **is linear**: 8,000 accepted groups in 0.018 s. It builds two sets per group and
intersects them, and that is all. Reporting this plainly is worth as much as the failures.

---

## 4. Where it degrades into nonsense

### 5. `example_members` is the whole branch

`00`:99 requires the picker to show, *before* the user chooses a split, "the resulting
number of child branches, the number of files under each child, **example members**,
unresolved files, and any evidence gaps".

`candidates.py:463`:

```python
example_members=members[:len(members)],
```

A slice that truncates nothing, written in the shape of a truncation. The no-split option
at `:490` is `example_members=members` outright, and `health.py:148` does the
same for every node's counts.

Measured: a 20,000-file branch produces `example_members` of length **20,000**, on every
option, plus a full copy per node in the preview counts.

*Test:* `test_example_members_is_a_sample_not_the_whole_branch`.

### 6. Nothing caps how many folders one split creates

§8.6's ceiling is named "Maximum folder proposals and maximum depth" and P1 publishes it
as one key. It bounds candidate **options** (`routing.py:481`) and candidate **depth**
(`validation.py:130`). It bounds **width nowhere**.

`00`:88 recommends exactly the split that exposes this — "Photos and capture-based media
are the major exception: time often belongs first." With
`tree.max_folder_proposals_and_depth = 6`, an 8,000-photo capture-date split proposes
**337 folders**, and the sentence the user reads is:

> This option would create 337 capture_date.

At 32,000 photos over four years it is 1,461 folders. A dimension whose cardinality grows
with the corpus — vendor on receipts, project name, filename-derived values — has no
bound at all, and by finding 3 the preview cost of that split is quadratic in its width.

*Test:* `test_nothing_caps_the_number_of_folders_one_split_would_create`.

### 7. The warning list outgrows the tree

§5.11 says the goal is "a good enough structural gist of the corpus so that only a
limited number of high-leverage changes remain." Measured on the preferential-attachment
tree:

| nodes | warnings | warnings/node |
|---|---|---|
| 100 | 35 | 0.35 |
| 1,600 | 1,330 | 0.83 |
| 3,200 | 2,991 | 0.93 |
| 12,800 | 15,099 | **1.18** |

At 12,800 folders the user is handed **15,099 warnings** — more warnings than folders.
They are unranked, unsummarised, and each is one node with one sentence.

**These fire for the right reason, and that is what makes it a design problem rather than
a bug.** Checked explicitly, per the standing rule:

- `WARN_ONE_CHILD` fires **three times on `00`:78's own worked example**
  (`Academics/Columbia/2026-Spring/PHYS1401/Homework`) — because the user has one school,
  in one term, taking one course. Every one of those levels is correct, and §5.8 makes
  uneven and shallow branches a *requirement*. On a real disk single-child levels are
  everywhere: one employer, one tax year with documents, one university.
- `WARN_TINY_FOLDERS` fires correctly on 4,000 one-file vendor folders — and carries
  **4,000 node ids in one `evidence` tuple**, with the reason "4000 of this level's
  children hold 2 file(s) or fewer". Right, and unusable.

*Tests:* `test_the_warning_list_does_not_outgrow_the_tree_it_describes`,
`test_the_one_child_warning_does_not_fire_on_the_designs_own_example`,
`test_the_tiny_folder_warning_says_something_a_user_can_act_on`.

---

## 5. Thresholds with no source

**There is no deployment configuration in this product.** `tree_limits()` and
`placement_limits()` have **no caller in `src/`** — only tests. `set_ceiling` is called
from nowhere in `src/` but its own definition. Every threshold value that has ever
existed in this repository is a literal inside a test file. The modules are right to
refuse defaults (`ConfigurationRequired` is well-argued in both `config.py` files), but
the consequence is that the first real deployment invents all of them, and the only
values ever exercised are these:

| threshold | source | only values ever used | verdict |
|---|---|---|---|
| `excessive_depth_warning` | §5.9 states none; §8.6 publishes no key; injected | `3` (once `5`, once `6`) | **flags `00`'s own example** |
| `tiny_folder_max_files` | as above | `2` (once `3`) | untested against a real distribution |
| `tiny_folder_count_warning` | as above | `3` (once `8`, once `12`) | fires on essentially any wide split |
| `tree.max_folder_proposals_and_depth` | §8.6, one P1 key for two numbers | `6`, `9`, `4`, `1`, `0` | **self-contradictory, see below** |
| `materially_improves_retrieval` | §5.9's flattening test; design states none | `lambda: None` everywhere | **never returns a verdict in any test** |

### 10. The depth threshold flags the design's own recommendation

With `excessive_depth_warning=3` — the value used in every test in the repository —
`warnings_for` fires on `00`:78's worked example:

```
n4: this node sits at depth 4, past the configured warning depth of 3
```

That path is the design document's own recommended shape.

### 9. One key, two jobs, opposite requirements

`tree.max_folder_proposals_and_depth` is read once and used twice, which
`tree_design/config.py:1-9` documents honestly. Driving V3 directly:

```
ceiling=4 (a readable picker): the candidate reaches depth 5, above the configured 4
```

`00`:78's tree needs depth 5, so the ceiling must be ≥ 5 — which means the picker offers
at least five options for every branch. Set it low enough for a readable picker and the
validator refuses the design's own tree; set it high enough for the tree and the proposal
ceiling stops bounding anything. **One number cannot be both**, and splitting it is a
change to `database_agent.budget` and §8.6, not a P10 decision.

### 8. The one budget that scales with the corpus is not enforced

`model.max_llm_calls_per_thousand_files` is the only §8.6 ceiling expressed *per corpus
size* — the only published bound on what a bigger disk costs. `placement/config.py:32`
reads it into `PlacementLimits`, and **no module in `src/placement/` references it**.
Verified against the current tree including the new `pipeline.py`:

```
ceilings with no consumer: ['max_llm_calls_per_thousand_files',
                            'max_cost_per_scan', 'max_candidate_cluster_size']
```

Only `max_retrieved_neighbors`, `max_local_graph_neighborhood`, `max_residual_files_per_batch`
and `max_dossier_tokens` have a consumer. `config.py`'s own docstring says a default would
mean "running a corpus under a limit nobody chose, with nothing to say so" — reading a
limit and never applying it arrives at the same place by a different route.

*Tests:* `test_the_budget_that_scales_with_the_corpus_is_enforced`,
`test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit`,
`test_the_depth_warning_threshold_admits_the_designs_own_example`.

---

## What was checked and found sound

Worth stating plainly, because a short list of real problems is only credible alongside
what held.

- **SQLite variable limits.** Checked every `IN (...)` in `src/`. All are fixed-width
  (`IN (?, ?, ?)` or `len(COLUMNS)` placeholders). **No query interpolates a member list**,
  so `SQLITE_MAX_VARIABLE_NUMBER` is not reachable no matter how large a group gets.
- **Recursion limits.** `scan_agent.traversal.walk` is BFS over a `deque`.
  `materialise._project` recurses per *dimension* (bounded by the template), not per node.
  `health.parent_concepts_for` and `index._ancestry` both detect and refuse parent cycles
  by name. No stack depth is reachable from corpus size.
- **`tree_health` group coverage** — §5.11's "summarize how much of each accepted group is
  represented" — is **linear**, 8,000 groups in 0.018 s. The brief flagged this as a likely
  quadratic; it is not.
- **The picker is linear in branch membership** (x0.76 per file over an 8× range). Its
  problem is split width, not corpus size.
- **Destination index build** is linear (x1.01 per node).
- **Routing deferral is graceful.** `route_branch` defers surplus candidates and *counts*
  them, and the no-split option states the count in the sentence the user reads. Deferral
  is kept distinct from abstention. This is the ceiling behaviour the brief asked about,
  and it is correct.

---

## Recommended order of work

1. ~~**Index `files.current_path`.**~~ **DONE**, together with the larger one the first
   pass missed: `events (file_id)`. The scan is now flat per file on unique content and
   2.7× faster on a disk-shaped corpus.
2. **Rule on `observe_path`'s inode question, then stop it walking the duplicate
   family.** The cheap parts are done (3× fewer syscalls, and an unchanged file no
   longer reads the family at all). Closing it needs either a persisted inode — which
   `tests/test_adversarial.py:1177` currently forbids — or a spelling-based narrowing,
   which changes what happens to hard links and symlinked directory components. Pick
   one; do not let it stay open, because a duplicate family of 20,000 is ordinary.
3. **Give `retrieve` a narrowed query.** It already knows the subject's fact values,
   group ids and folder labels before it loads anything; `entries_for_plan` should not be
   the first line of a per-file function. Make `entries_for_plan` one query instead of
   N+1 first — that alone removes ~800 round trips per file and changes no behaviour.
4. **Memoise structure in `health.py`.** Build `children_by_parent` and `depth_by_id` once
   per tree and pass them down. This collapses findings 4 and the picker's width quadratic
   together, and touches one module.
5. **Truncate `example_members`** to an actual sample, and give the §5.9 warnings a
   summary form and a bound on `evidence`.
6. **Split `tree.max_folder_proposals_and_depth` into two keys** and add a width bound.
   This is a §8.6 change, not a P10 one.
7. **Calibrate the §5.9 thresholds against `00`'s own examples** — any value that flags
   `Academics/Columbia/2026-Spring/PHYS1401/Homework` is wrong by the design's own
   standard — and decide whether `WARN_ONE_CHILD` should fire on a legitimately thin level
   at all.
8. **Enforce or delete the three unconsumed ceilings.**

# 1. Intake and identity

This section describes how a file gets into the system: what happens between the moment a
person names a directory and the moment a row exists that later parts can read. Two parts do
this work. **P3** (`src/scan_agent/`) owns the corpus boundary — which paths are in, which are
out, and why. **P1** (`src/database_agent/`) owns identity and the log — which row a path
resolves to, and what is written down about the resolution. Everything downstream reads what
these two produce and nothing else about the filesystem.

The two are deliberately not symmetrical. P3 decides and P1 records; P3 authors events and P1
writes them; P3 computes the ten per-file fields and P1 is forbidden from re-deriving any of
them (`files_table.py:31-33`, `basic_record.py:8-11`). Most of the sharp edges in this section
are places where that split is either enforced by a mechanism or merely asserted in a comment.

---

## 1.1 What happens when a directory is pointed at

### The database is opened before the corpus is touched

`cli.py:1053` calls `open_database(database, scan_roots=[directory])`. `open_database`
(`db.py:28-62`) resolves the database path, then refuses if that path is the scan root or lives
underneath it — `DatabaseInsideCorpus` (`db.py:15-17`, raised at `db.py:39`). The reason given
is that P3's exclusion rules would otherwise have to special-case the agent's own storage. The
default location is `~/Library/Application Support/<bundle_id>/agent.sqlite`
(`db.py:19-25`), and the bundle identifier is supplied by the caller rather than invented.

The same call sets the connection's durability and integrity posture, and one of those settings
is load-bearing rather than cosmetic: `PRAGMA recursive_triggers = ON` (`db.py:52`). Without it,
SQLite's `INSERT OR REPLACE` deletes a conflicting row *without firing delete triggers*, which
would let any caller rewrite an event row in place and silently forge the append-only log. The
schema is created eagerly at the end of `open_database` (`db.py:60`) so no neighbour has to
remember a second call.

### A selection is recorded before anything is walked

P3 has no corpus until one is handed to it. `record_selection` (`selection.py:40-65`) writes one
`corpus_selections` row carrying §1.1's three user choices: `sources`, `candidate_roots`, and
`cross_folder_moves`, plus `selected_at` and a nullable `selected_by`. All four keyword
arguments are required with no defaults, so P3 cannot derive a corpus from the machine's layout
(`selection.py:45-51`).

In the shipped CLI the selection is degenerate: `cli.py:583-585` passes
`sources=[directory], candidate_roots=[], cross_folder_moves=False`. The candidate-root half of
the design — the "high-level locations that may serve as roots for a future file tree" — is
always empty in a live run, which means every mechanism below that distinguishes the two sides
of the scan is exercised only by tests.

`cross_folder_moves` is recorded and enforced nowhere. The DDL comment says so in the schema
itself: "the user's selection (§1.1); enforced nowhere in P3 -- SPEC Q12 is OPEN"
(`selection.py:31-32`). No module in `src/` reads the column.

### A scan run is opened, and committed, before the first file

`scan()` (`scan.py:55-81`) is the whole run. In order:

| Step | Where | Note |
|---|---|---|
| Read the selection's two path sets | `scan.py:66-67` | |
| Check Full Disk Access on every root | `scan.py:68` → `access.py:38-51` | Before the run row exists |
| Mint and commit the `scan_runs` row | `scan.py:73` → `run.py:30-43` | Deliberately outside the write batches |
| Walk, recording each item | `scan.py:74-79` | Inside `batched_writes` |
| Close the run, sample resources | `scan.py:80` → `run.py:46-57` | |

The access check is a real attempt to list each root, not a table of TCC-protected paths:
`unreadable_roots` (`access.py:24-35`) calls `os.scandir` and treats `PermissionError` as the
whole test. If any selected root refuses, `require_access` raises `FullDiskAccessRequired` and
the scan performs *zero* traversal rather than a partial one (`access.py:38-51`). A root that is
merely absent is not a permission problem and falls through to the traversal.

The run row is committed before the first file so that an interrupted scan is a *visible
incomplete run* rather than an absent one (`scan.py:70-73`). `start_scan_run` inserts P3's row
first and only then registers the run with P1's `start_scan`, because `selection_id` is a
foreign key and a bad selection should fail before P1 opens a counter row (`run.py:34-42`).

`scan_run_id` is minted by P3 (`run.py:37`) and adopted by P1. That was P3 OQ16 / P1 OQ19,
ratified 2026-08-20 and recorded in the module docstring (`run.py:1-11`). It is published
identity but deliberately *not* an event field: §8.2's event record stays at eleven fields.

### Writes are batched, and why

Every walked item is recorded inside `batched_writes(conn, size=512)` (`scan.py:74`,
`db.py:105-169`). The connection is autocommit with `synchronous = FULL`, so without a boundary
every one of the five rows a file admission writes would be its own fsync — on macOS an
`F_FULLFSYNC`, a full device cache flush. The measured numbers are in both docstrings:
13.7 ms per file unbatched against 2.2 ms with a transaction held open, i.e. 11.5 ms of every
13.7 was fsync (`db.py:120-125`, `scan.py:30-34`). 512 was chosen by interleaved measurement
against 1/32/128 (`scan.py:41-48`).

The honest statement of what a crash costs is made in both places and is worth repeating,
because it is the kind of claim a critic should check: nothing is made *damageable* —
`synchronous` is untouched — and what a power cut loses is at most 512 *files not yet recorded*,
which the next scan re-records because no cache verdict exists for them
(`db.py:126-133`, `scan.py:44-48`). `batched_writes` catches `BaseException`, not `Exception`,
so a hand interrupt rolls back the batch in flight rather than leaving it for the next statement
to commit by accident (`db.py:162-168`).

---

## 1.2 The corpus boundary: traversal and exclusion

### The walk is pure

`traversal.walk` (`traversal.py:55-68`) is a generator over a `CorpusSource`. It opens no
database and writes no row (`traversal.py:5-7`). Every §1.1 decision is therefore finished
before any record exists, which is what makes it structurally impossible for a curation signal
or any other later-computed value to influence an exclusion or a cache verdict.

It yields four things, and `scan._record` (`scan.py:84-142`) dispatches on their types:

| Yielded | Written by | Table |
|---|---|---|
| `ExclusionVerdict` | `record_exclusion` | `exclusion_verdicts` |
| `Deferred` | `record_deferral` | `scan_deferrals` |
| `ObservedDirectory` | `record_directory` | `directory_inventory` |
| `ObservedFile` | `record_basic_record` → P1 | `files` + `events` |

`walk` runs the scanned sources first, then the candidate roots (`traversal.py:65-68`), tagging
each item with `applies_to`. Candidate-root *files* are yielded but dropped at the writer:
`scan.py:96-97` returns early for any `ObservedFile` whose `applies_to` is not
`"scanned source"` — "roots are context, not corpus". Their directories still produce inventory
rows.

The source abstraction (`corpus_source.py`) has two implementations: `FilesystemCorpusSource`
(`corpus_source.py:52-81`) and `SnapshotCorpusSource` (`corpus_source.py:84-107`), the latter
for §8.5 replay against a frozen corpus with no filesystem at all. Entries are sorted by path in
both so two runs agree (`corpus_source.py:81`, `:103-104`). `stat(follow_symlinks=False)`
throughout: a symlink is reported as `KIND_OTHER`, so it is never descended (a loop would make
traversal non-terminating) and never handed to a hasher (`corpus_source.py:59-68`).

### The exclusion predicate

`exclusion_for` (`exclusion.py:117-143`) is the single place a §1.1 rule fires. It returns an
`ExclusionVerdict` or `None`, and it tests four things in a fixed order:

1. **Protected container** — first, always (`exclusion.py:130-133`). See §1.3.
2. **Software-project-root descendant** (`exclusion.py:134-136`), if the entry's *parent*
   directory contained one of the four markers. Applies to files and directories alike.
3. **Literal directory name** (`exclusion.py:137-138`), directories only, against the eleven
   names §1.1 spells: `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`,
   `Pods`, `site-packages`, `Library`, `__pycache__` (`exclusion.py:23-26`).
4. **Category** (`exclusion.py:139-142`), directories only.

Rule 4 can never fire. §1.1 names five categories — build artifacts, caches, auto-save folders,
previews, generated dependency trees — and enumerates no member of any of them, so
`CATEGORY_MEMBERS` maps each to an empty tuple (`exclusion.py:32-43`). The loop is wired against
the mapping so that authoring the list is a data change rather than a code one, which is a
defensible choice, but as shipped `RULE_CATEGORY` is a constant with no reachable producer.
The same applies to marker extension: `PROJECT_ROOT_MARKERS` is fixed at four
(`exclusion.py:40-42`) and `project_root_markers_in` (`exclusion.py:145-157`) accepts no
additions.

`project_root_markers_in` requires the marker to be a *file*, so a directory named
`package.json` is not one (`exclusion.py:156`). Markers are computed once per directory listing
(`traversal.py:96-98`) and applied to every entry in it. Whether the marker-bearing directory
*itself* is excluded is P3 SPEC Q9 and is explicitly left open (`exclusion.py:150-154`) — only
descendants are rejected.

An exclusion is a **prune**: the verdict is yielded, the entry is never enqueued and never
listed (`traversal.py:120-122`). No `files` row, no descendants, no inventory row for it.

### Verdicts are permanent

`exclusion_verdicts` has an `exclusion_verdicts_no_delete` trigger (`exclusion.py:171-175`) —
"an exclusion verdict survives a later rule-set change". This matches the SPEC's statement that
an R3 record explaining why a path was skipped is not deleted when the path later becomes
eligible. Note the asymmetry with `events`: the events table is protected against UPDATE,
DELETE *and* replace (`db.py:265-274`); `exclusion_verdicts` is protected against DELETE only.

---

## 1.3 Protected containers — marked and counted, never opened

This is the project's one absolute rule. The P3 SPEC states it at length: an application bundle,
a macOS package, and anything under a system location is a protected container; P3 "does not
descend into one, does not stat its contents, does not hash a byte of it, and does not create a
`files` row for anything inside it", and "no policy, approval, or user gesture makes it
movable". `upstream.py:263-266` quotes the product owner's own words for it.

### Where the predicate lives

`is_protected_container(path, *, extra=None)` (`exclusion.py:69-89`). Two properties matter:

- **The unit of protection is the subtree, not the entry.** The function walks
  `(candidate, *candidate.parents)` and returns True if *any* ancestor carries a protected
  suffix (`exclusion.py:83-89`). The docstring records that an earlier version tested only the
  path's own suffix — which protected `Numbers.app` and admitted
  `Numbers.app/Contents/sheet.numbers`, the exact read the rule forbids — and that every test
  passed because every test asked about the bundle. It was found by injecting the predicate into
  P5's gate and watching the gate admit the file (`exclusion.py:74-80`).
- **`extra` can only add.** A caller-supplied predicate is OR'd in; there is no way to return
  False for a `.app`, because a predicate that could would be the override the rule says does
  not exist (`exclusion.py:80-82`).

The authored membership is one suffix: `PROTECTED_BUNDLE_SUFFIXES = (".app",)`
(`exclusion.py:66`). The SPEC also names the *category* "system location" and enumerates no
member, so P3 authors none — inventing `/System`, `/Library` or `/usr` here would be a
gazetteer the project refuses to write. The comment says "A deployment supplies the rest through
`extra`." **It cannot.** Neither `exclusion_for` call site passes `is_protected`
(`traversal.py:73`, `traversal.py:118-119`), and neither `walk()` nor `scan()` takes a parameter
that could reach it. The extension point exists and is unreachable from the scan.

### What an exclusion verdict is

`ExclusionVerdict` (`exclusion.py:96-114`) is a frozen record of five fields:

```text
path          the rejected path
rule          which §1.1 rule fired
rule_subject  the literal name, the category, or the marker file observed
applies_to    "scanned source" | "candidate root"
label         §8.6's display category — non-None only for protected containers
```

`label` is a **field rather than a constant**, and the docstring explains why at length
(`exclusion.py:103-114`): `LABEL_UNTOUCHED_PROTECTED` previously existed as a documented
constant whose only use anywhere was a test asserting it equalled its own literal. It reached no
verdict, no row and no summary, so P13 would have found it missing and re-derived it from
`rule` — one value computed twice, which this codebase repeatedly names as its most expensive
defect class. Only the protected container carries a label; the other three rules get `None`,
because inventing display names for them would be P3 authoring a vocabulary nobody asked for.

Ordering is what makes the label honest. Because the protected test runs first, a `.app` inside
`node_modules` is recorded as protected rather than under the weaker rule that would understate
why it was skipped (`exclusion.py:127-129`).

### How the mark reaches a person

Four independent mechanisms, in the order a file would meet them:

| Layer | Mechanism | Cite |
|---|---|---|
| Scan | `exclusion_for` tests protection first; the subtree is pruned, so no interior `files` row is ever created | `exclusion.py:130-133`, `traversal.py:120-122` |
| Extraction | `admit()` is the first statement of every extractor and raises `ProtectedContainerRefused` before its reader is touched | `safety.py:49-64` |
| Tree design | `protected_areas()` turns P3's verdicts into `ProtectedArea` records that reach the canvas | `upstream.py:283-303` |
| Report | The count and every path print **first**, before anything else | `cli.py:878-887` |

`SafetyPolicy` (`safety.py:38-46`) has exactly two fields "and deliberately no third: a `force`,
`override` or `approved` field would be the override 11 §4b says does not exist". The CLI wires
P3's own predicate into it (`cli.py:410`) rather than a second spelling.

`protected_areas` filters on `rule`, not on `label` (`upstream.py:290-292`) — the rule is the
decision, the label is the display string, and selecting on the display string would make a
presentation change silently alter which areas the tree represents. The `ProtectedArea`
docstring states the point of the whole record: "a protected container that is pruned and then
never mentioned has been silently omitted, and silent omission is the one outcome the rule
forbids" (`upstream.py:268-272`).

The report block is the reachable end of it (`cli.py:864-889`). It prints
`Protected containers: N marked, none opened`, then each area's display label, label and path,
then a sentence: nothing inside was read, indexed, classified or moved, and none of them is a
place anything can be filed. The docstring is explicit that position is part of the guarantee:
"'Marked and counted, never opened' is only true if the count is somewhere the person reads, and
a line at the bottom of a long report is not that." The later per-file listing, which truncates
to ten names per kind (`cli.py:809`), never truncates a protected group — `_protected`
(`cli.py:849-861`) treats any of three signals as protection, on the stated reasoning that the
cost of over-including is a longer list and the cost of the reverse is silent omission.

**The rule is enforced for `.app` bundles and for nothing else.** That is the honest summary. A
scan of a home directory protects `Foo.app`; it does not protect `/System`, `/usr`, `~/Library`
(which is excluded by the *weaker* literal-name rule, unlabelled and unreported), or anything a
deployment might consider sensitive, because there is no wiring by which a deployment can say so.

---

## 1.4 File identity

### The hash is the identity of a *version*

`HASH_ALGORITHM = "sha256"` (`identity.py:14`), chosen to match P4's `observation_key` formula
(P1 OQ10, ratified 2026-08-19). `hash_file` (`identity.py:49-65`) streams in 1 MiB chunks and
returns 64 lowercase hex characters. `is_content_hash` (`identity.py:43-46`) publishes the
predicate so no consumer re-spells "64 lowercase hex" as a second definition of one rule; it is
deliberately *not* algorithm-prefixed while P4's citation keys are, so a citation key stored in
a `content_hash` column cannot pass for a hash (`identity.py:31-39`).

`hash_file` takes `materialized: bool` **with no default** (`identity.py:53-60`). It is the
caller's declaration that P3's dataless check has run. Passing False raises
`DatalessFileRefused`. P1 has no ubiquity API and invents no detection heuristic; the required
keyword is the mechanism that stops any caller reaching P1's bytes without having made the
check.

### `volume_id` is per-process and therefore inert

`volume_id_for` (`identity.py:68-83`) returns `f"{OBSERVATION_SESSION}:{os.stat(path).st_dev}"`,
where `OBSERVATION_SESSION` is a UUID minted once per process (`identity.py:19`). P1 OQ9 — is
`st_dev` stable across remount, volume rename, or cloud re-sync? — is open, so the value is
deliberately poisoned across processes: within one process it compares correctly, across
processes it can never accidentally match, so no cross-session decision can be built on it.
`files.volume_id` is nullable for the same reason (`db.py:180`).

The practical consequence is that the column is written on every row and is meaningful to
nothing. `file_path_history` (`files_table.py:486-499`) publishes `volume_id` as a literal
`NULL` because `events` has no volume column at all (`files_table.py:489-493`). Note also that
`volume_id_for` uses `os.stat` (follows symlinks) while every other identity call in this module
uses `lstat` (does not) — see §1.10.

### Resolving a path to a row

`observe_path` (`files_table.py:369-483`) is the whole of R2/R3. It hashes the file, then asks
up to three questions in a fixed order:

1. **Is there a live row at exactly this path with these bytes?** (`files_table.py:408-412`) —
   an indexed lookup on `(current_path, content_hash)`. A re-scan of an unchanged corpus takes
   this branch for every file, so a duplicate family of any size costs nothing to re-observe.
   Exact path wins first so a deleted twin with an earlier rowid cannot steal a still-live
   copy's identity.
2. **Is one of the rows for these bytes *this very inode*?** — `_row_for_this_inode`
   (`files_table.py:113-168`), answered from the `files_inode` index on
   `(st_dev, st_ino, content_hash)` (`db.py:220-222`).
3. **Has the oldest recorded home of these bytes gone?** — `_relocated_row`
   (`files_table.py:171-216`), R2's cross-volume move.

The `st_dev`/`st_ino` columns are the most interesting piece of mechanism here and the schema
comment is emphatic that they are **not a second identity** (`db.py:190-198`). Inodes are
recycled, so a stored pair can name a file that no longer exists. Every index hit is a
*candidate*, confirmed against what the filesystem says now, and there are exactly two ways a
candidate confirms (`files_table.py:126-141`): its recorded path is still live and *is* this
inode (one file under two spellings of its name — NFC/NFD on APFS — which is one record), or its
recorded path is **gone**, which is what a rename necessarily leaves behind. A candidate whose
recorded path is live but is a different inode is rejected, and that is the recycled-inode case.

This index replaced a walk over the whole duplicate family that cost O(k) syscalls per file
admitted and O(k²) to admit a family of k (`files_table.py:117-121`) — empty files, `.DS_Store`,
stub configs and repeated downloads make families that size on a real disk.

`_relocated_row` is a **deliberate narrowing** and says so (`files_table.py:186-199`). Deletion
leaves nothing in the database, so no index can answer "is any recorded copy of these bytes
missing?"; only one filesystem call per recorded copy can, which is the O(k²) being removed. So
the question asked is narrower: *is the oldest recorded home of these bytes gone?* Inside a
family with several live copies whose oldest member is still live, a cross-volume move is now
recorded as a **new file** rather than as a relocation. The stated justification is that it can
only ever mint an extra record, never merge two files into one, and that the walk's answer there
was a guess anyway.

`_path_is_taken` (`files_table.py:99-110`) guards both relocation branches: a row whose home
vanished is never moved on top of a live row recording different bytes at the observed path.

`_lstat_or_none` (`files_table.py:36-63`) is used everywhere rather than string comparison,
because comparing `current_path` as a Python string would mint a second row for the NFC and NFD
spellings of one name — and §8.3's collision policy, seeing two rows whose hashes "prove the
files are identical", would offer to delete one copy and delete the only copy. Normalising the
string instead would be wrong on a filesystem that does not fold. `lstat`, never `stat`, so a
symlink and its target stay two records.

### When bytes change: `superseded_content`

If no row matches by content but a live row sits at the observed path, that row's bytes changed
(`files_table.py:450-467`). Three things happen, in one transaction:

1. An `external modification detection` event is appended under the *caller's* author, carrying
   the **new** hash and the explanation "content at this path changed; this version is
   superseded (R3)".
2. The prior row's `scan_state` is set to `SUPERSEDED_CONTENT` — the literal
   `"superseded_content"` (`files_table.py:24`).
3. `invalidate_extraction_state` resets that row's `extraction_status_by_tier` to `{}`
   (`files_table.py:293-305`).

Then a **new row with a new `file_id`** is created (`files_table.py:469-477`) and a `hashing`
event appended (`files_table.py:478-482`). This is P1 OQ1, ratified 2026-08-19 (I1): `file_id`
is version-scoped and every foreign key to it is version-scoped with it, so the previous
version's facts and evidence keep pointing at a row that still describes them.

`superseded_content` is P1's own sentinel and a caller may not supply it:
`_require_caller_scan_state` (`files_table.py:219-223`) raises `ReservedScanState`. Every
identity query in the module excludes superseded rows (`scan_state != SUPERSEDED_CONTENT` at
`files_table.py:109`, `:157`, `:206`, `:411`, `:452`), which is the mechanism that keeps a dead
version from answering for a live one.

### Why almost everything downstream is keyed on `(file_id, content_hash)`

Because the two answer different questions and neither alone is sufficient. `file_id` names a
*version*; `content_hash` names the *bytes*. Two live copies of identical bytes are two
`file_id`s sharing one `content_hash` — required, because §2.9's duplicate family has nothing to
detect if duplicates collapse and §8.3's collision policy presumes both exist and are separately
addressable (P1 OQ2, I1; `files_table.py:388-391`). Conversely, one file whose bytes change is
two `file_id`s with two hashes, and the old one must stay resolvable.

So a cache or an audit record keyed on `file_id` alone would survive a content change it should
not survive; keyed on `content_hash` alone it could not tell two live copies apart. P7's
`ClassificationRecord` is keyed on the pair and is authoritative, with `files.sensitivity_state`
as its projection onto the current row (`files_table.py:351-356`). P4's evidence, P6's facts and
P9's embeddings follow the same pattern — `vector_embeddings` has a partial unique index on
`(file_id, content_hash, scope, model, version) WHERE superseded_by IS NULL` (`db.py:326-329`).

---

## 1.5 `scan_state`

The column is `TEXT NOT NULL` on `files` (`db.py:187`). P1 defines exactly one value —
`superseded_content` — and refuses to accept it from a caller. Every other value is P3's, and
**P3 invents none**: `record_basic_record` takes `scan_state` as a caller parameter with the
note that SPEC Q4 (the enumeration) is open (`basic_record.py:44-51`).

The value a live run writes is `"included"`, meaning "this file is in the corpus". Its one
named home is `P1_INCLUDED_SCAN_STATE` in `grouping/vocabulary.py:91`, declared there because
P1 and P3 publish no constant for it and P9 wanted one home rather than a second literal
(`grouping/vocabulary.py:79-89`). Its reader is P9's retrieval: `_corpus`
(`grouping/retrieval.py:128-142`) selects `FROM files WHERE scan_state = ?` and admits nothing
else, on the reasoning that "an excluded file reaching a dossier would be the scan boundary
failing silently".

**This was a live defect, fixed 2026-08-29** (commit `53c41d1`). The composition root wrote the
literal `"scanned"`; P9's `_corpus` admits `"included"` and nothing else. The comment left at
the fix site is the clearest statement of the consequence (`cli.py:395-404`): on every live run
the neighbourhood of every file was empty, no shared-fact edge was ever built, and every group
was a group of one whatever the corpus said. P9's own tests write `included`, so thousands of
passing tests agreed with a production path that could not form a group of two. The fix is an
**import** of P9's constant rather than a corrected literal.

The type-level guard that remains is weak: `P1P7Authorities.__post_init__` checks only that
`scan_state` is a non-empty string (`production.py:123-126`). Any other misspelling reproduces
the same silent emptiness with the same test suite green.

---

## 1.6 The append-only event log

### The vocabulary is closed at import

`RESERVED_EVENT_TYPES` (`events.py:30-37`) is §8.2's nineteen names, verbatim. `_REGISTERED`
(`events.py:42-78`) is the table of types other parts' SPECs declare, compiled from those SPECs
and frozen at import — **there is no runtime registration call**, because registration is a
spec-level act (P1 SPEC Contract out §3, rule 4). Two consistency checks run at import and raise
`ImportError` rather than deferring to a runtime rejection: a registered name shadowing a
reserved one (`events.py:82-84`), and a specialization whose base is not a reserved name
(`events.py:85-87`).

The registered set is P7's eight, P8's five, P13's three, and P11's nine typed specializations
of the reserved `placement recommendation`. **The SPEC says eight for P11 and totals
twenty-four** (P1 SPEC, Contract out §3); the code registers nine and therefore twenty-five. The
divergence is deliberate and documented (`events.py:62-68`): P11's SPEC:689 is one bullet
carrying two state changes — a residual set *surfaced* and a set *decided* — and §7.6 gates
model spend on the second, so they are two names. The SPEC text has not been updated to match.

### Who may write, and what is checked

`append_event(conn, **fields)` (`events.py:118-154`) is the only writer. It rejects any field
outside `EVENT_FIELDS` + `CORRECTION_FIELDS` + `base_event_type` (`events.py:124-126`), requires
five fields to be present and non-empty — `event_type`, `subsystem`, `component_version`,
`observed_at`, `explanation` (`events.py:115`, `:127-130`) — rejects an unregistered
`event_type` (`events.py:132-136`), and validates `correction_scope` against §8.7's six scopes,
requiring a `correction_subject` alongside it (`events.py:137-144`). A typed specialization gets
its `base_event_type` filled in automatically (`events.py:145-147`).

`subsystem` is never filled in by P1. The rule is M8 — *the acting part authors, P1 writes* —
and P3 enforces its half in `authorship.event_defaults` (`authorship.py:33-56`), which refuses
to build a row for an event type P3 does not author and refuses a `subsystem` that is not `"P3"`.
P3 authors exactly four reserved names: `discovery`, `stat observation`, `hashing`,
`external modification detection` (`authorship.py:25-30`). The fourth has two authors — P3 on
re-scan and P12 on §8.3 staleness — and the two are separable by `subsystem`.

P1's own mutators take `author` and `component_version` and **append no event of their own**:
`invalidate_extraction_state`, `set_extraction_status`, `set_sensitivity_state`
(`files_table.py:293-366`). The stated reason is that P1 minting an event there would name the
storage substrate as the thing that classified the file, "which is exactly what §8.2's
reconstruction requirement cannot survive" (`files_table.py:358-361`). The parameters are
consequently accepted and unused — see §1.10.

### Supersede, never overwrite

"Append-only" is enforced three ways, not by convention:

| Mechanism | Cite | Covers |
|---|---|---|
| `events_no_update` / `events_no_delete` triggers | `db.py:265-270` | UPDATE, DELETE |
| `events_no_replace` trigger | `db.py:271-274` | `INSERT OR REPLACE` onto an existing `event_id` |
| `PRAGMA recursive_triggers = ON` | `db.py:52` | Makes the replace trigger reachable at all |
| Connection authorizer | `db.py:65-76` | `DROP TABLE events`, `DROP TRIGGER` on the three |

For records that *do* change, `supersede.py` publishes the three shared column names —
`supersedes`, `superseded_by`, `supersede_reason` (`supersede.py:12-14`) — so no part re-spells
them. `mark_superseded` (`supersede.py:22-55`) requires a non-empty reason, refuses
self-supersession, refuses to re-supersede an already-superseded row so the *first* reason
sticks, and walks the forward chain to refuse a cycle. `chain()` (`supersede.py:58-72`) returns
every link, oldest first. In practice this means: the old row stays readable and queryable
forever, the new row points back at it, and the reason the transition happened is recorded once
and never rewritten. `preferred` is deliberately *not* in the shared set — it lives on P6's
`file_facts` alone (`supersede.py:3-6`).

---

## 1.7 Absence is recorded, never assumed

Four tables exist because "we did not look" and "there was nothing there" must be
distinguishable. §8.6's requirement is that no unscanned file reads as one that was understood
and found unimportant.

### Deferrals — `scan_deferrals`

Four reasons, each naming the design rule or open question that produced it
(`deferrals.py:19-36`):

| Constant | Value | Produced when |
|---|---|---|
| `DEFERRED_BUDGET` | `scan budget exhausted` | `budget_exhausted()` fires mid-listing |
| `DEFERRED_TRAVERSAL_UNRESOLVED` | `traversal behaviour unresolved (SPEC Q7)` | Entry is neither file nor directory |
| `DEFERRED_PATH_ABSENT` | `path absent at scan time (SPEC Q14)` | `FileNotFoundError` / `NotADirectoryError` on listing |
| `DEFERRED_DIRECTORY_UNREADABLE` | `directory not readable at scan time` | `PermissionError` below a cleared root |

None is a judgement about the file and none is a status from P4's closed vocabulary
(`deferrals.py:8-10`). Budget exhaustion is thorough: the unreached entries in the current
listing, the current directory itself, *and* every directory still queued are each recorded as
deferred before the walk returns (`traversal.py:104-115`). No inventory row is emitted for a
partially-listed directory, because R6 has no field for a partial count and P3 does not invent
one (`traversal.py:105-107`). A `PermissionError` on one directory yields the directory and no
inventory row — nothing inside is known, because the listing never happened
(`traversal.py:88-94`).

### Dataless detections — `dataless_detections`

`is_dataless` (`dataless.py:38-45`) reads one bit: `SF_DATALESS = 0x40000000` from macOS's
`sys/stat.h`, named here with its source because Python's `stat` module does not publish it
(`dataless.py:32-35`). It is outside macOS's `SF_SETTABLE` mask, so a test cannot set it. A
platform without `st_flags` reads as not-dataless, which is the honest answer.

The detection happens during `scandir` (`corpus_source.py:79`), i.e. *before* any hash, because
`os.stat` does not download and `open` does. `scan._record` then splits two cases
(`scan.py:98-126`):

- **Never hashed** — the detection row is the whole record and the function returns
  (`scan.py:100-106`). No `files` row exists and none can be made: hashing downloads the bytes
  and P1 refuses to mint a row without a hash.
- **Hashed, then evicted** — scanned while local, since moved to iCloud by "Optimize Mac
  Storage". The row, hash and history exist, so a cache verdict is computed and recorded, and a
  `stat observation` appended if it says REUSE (`scan.py:107-126`). A RECOMPUTE verdict is
  **recorded and not followed**: following it means hashing, and appending an external
  modification event without the recompute would assert a content change P3 cannot confirm. The
  comment records that an unconditional skip used to sit here and dropped the file out of the
  scan silently.

The orchestrator then intersects P3's detections with the extraction roster
(`orchestrator.py:545`, `:552-553`). The comment at `orchestrator.py:363-375` is the honest
account of why: there are *two* predicates for one question — P3's scan-time detection and P5's
`SafetyPolicy.is_dataless` — and this module is the only place that sees both. It wired neither
to the other, so a caller passing the usual `is_dataless=lambda p: False` (which the CLI does,
`cli.py:411`) re-extracted an evicted file and on a real machine would have triggered the
iCloud download the rule exists to prevent. P3's observation wins because it is the one made
before any read.

### Stat-cache verdicts — `stat_cache_verdicts`

`cache_verdict` (`stat_cache.py:46-69`) is disjunctive and a **difference** test, never a
newer-than test — an mtime that moves backwards is a change, which is what protects restores and
migrations. Two verdicts and four reasons, the SPEC's words and no fifth
(`stat_cache.py:26-33`). Size is compared before mtime so a file where both changed reports one
deterministic reason, with all four values on the record either way.

`prior_observation` (`stat_cache.py:92-104`) joins the verdict to `files.current_path`, which
is what stops a verdict left behind by a file that has since moved away from being reused for a
different file that later appears at the old path.

A verdict row is written for **every** file the scan reaches, REUSE and RECOMPUTE alike
(`scan.py:142`), and `file_id` is nullable for §8.5's metadata-safe form where there are no
bytes to hash (`stat_cache.py:76-77`). This table is therefore the roster: the orchestrator
iterates `cache_verdicts(conn, scan_run_id)` to find every file this scan saw
(`orchestrator.py:547`, `production.py:528`), and `scan_run_summary` counts
`DISTINCT file_id` from it for `files_indexed` (`summary.py:27-30`).

On REUSE nothing is re-read: no hash, no `observe_path`, no `files` write — only a
`stat observation` event (`scan.py:129-132`). That is resumption, done without being called
that.

### Directory inventory — `directory_inventory`

One row per fully-listed non-excluded directory (`inventory.py:56-70`), carrying parent,
non-excluded file count, subdirectory count, extension mix, and a curation signal with its
evidence. `curation_evidence` (`inventory.py:28-39`) records *every* project-root marker
observed in the directory, where the exclusion verdict records only the one that fired.

`curation_signal` (`inventory.py:42-53`) **returns `CURATION_UNDETERMINED` unconditionally.**
This is deliberate and documented: §1.1 gives one worked case and no number, no ratio, and no
list of which extensions read as software material, so the honest value is `undetermined` for
every directory and no directory is ever rounded to `incidental`. P10 renders the three values
and refuses a fourth (`upstream.py:243-249`), and `candidates.py:302` compares against
`_CURATED` — a comparison that is currently always False.

---

## 1.8 Budgets and ceilings

`budget.py` publishes seventeen ceiling keys (`budget.py:13-51`) and enforces none of them. The
module docstring is unambiguous: "P1 holds and publishes values; P1 enforces none of them.
Reading a ceiling is not enforcing it" (`budget.py:6-7`).

The arithmetic: §8.6 names twelve ceilings; three of them are held by two parts on different
graphs and are namespaced `grouping.*` / `placement.*` (O10), giving fifteen; the sixteenth is
`evidence.context_window`, ratified 2026-08-20; the seventeenth is `tree.max_depth`, 2026-08-29.

**The 2026-08-29 split.** The list previously carried one key,
`tree.max_folder_proposals_and_depth`, because `00`:256 names two numbers on one line —
"Maximum folder proposals and maximum depth". Every other line in that list is one quantity;
this one is two, and P10 was reading the single value four times: how many options the picker
offers, how deep a candidate may go, how wide a date level may be, and the sample size of the
printed lists. The first two want opposite values — `00`:78's own recommended tree is five
levels deep, and a picker offering five options per branch is not a picker — so no P10 change
could reconcile them, and a test named
`test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` failed for as long as the key
was one (`budget.py:28-40`). The split publishes what §8.6 already names.

`evidence.context_window` was added because §2.8 requires surrounding context be stored and
§8.6 forbids silent truncation, yet none of the other sixteen is a context length — so the
budget had nowhere to live and P4 held it caller-supplied with no number. It belongs in the
extraction run's `config` fingerprint too: a ceiling outside the fingerprint makes two runs at
different context widths look identical to §3.4's cache key and §8.5's replay
(`budget.py:43-50`).

Access is guarded by `_check` (`budget.py:62-66`): reading or writing a key outside the
seventeen raises `KeyError`. `set_ceiling` bumps `object_version` on every write
(`budget.py:72-77`), which is what lets a replay pin the values it ran under. Consumers name
their own keys and assert at import that P1 publishes them —
`extractors/budgets.py:35-40` raises `ImportError` if P5 names a key P1 does not.

**What a live run actually does with this.** `_bootstrap` (`cli.py:531-533`) sets ceilings for
`CEILINGS.values()` imported from `placement.config` — seven keys (`placement/config.py:26-34`)
— all to the same value, 8 (`cli.py:123`). The other ten keys are never written. Grouping and
tree design read their ceilings through `get_ceiling` in their own config modules
(`grouping/config.py:67`, `tree_design/config.py:88`), where a missing value raises
`ConfigurationRequired` — but the CLI bypasses both by constructing `TreeLimits` and
`GroupingLimits` in Python with different numbers entirely (`cli.py:126-144`:
`max_folder_proposals=4, max_depth=5`, `max_retrieved_neighbors=50`). So the two keys split out
on 2026-08-29 are published by P1 and read from the database by nobody in the live path.
`facts/budgets.py:34` still says "P1 publishes sixteen".

---

## What looks wrong here

Ordered by how much a reader should press.

1. **The standing rule protects one file extension.** `PROTECTED_BUNDLE_SUFFIXES = (".app",)`
   (`exclusion.py:66`) is the entire authored membership. The `extra` predicate that was meant
   to carry a deployment's additions is threaded through `is_protected_container` but reaches
   the scan through no call path: `traversal.py:73` and `traversal.py:118-119` both omit it, and
   `walk()`/`scan()` accept no parameter that could. `watch.py:63` and `recognition/detector.py:309`
   *can* pass one; the scan cannot. A person scanning their home directory gets `.app` bundles
   marked, and `/System`, `/usr`, keychains, `.photoslibrary` and everything else treated
   ordinarily or swept up by the unlabelled `Library` rule.

2. **"Never silently omitted" holds for one of the four exclusion rules.** Only
   `RULE_PROTECTED_CONTAINER` carries a label, only protected verdicts become `ProtectedArea`
   records (`upstream.py:290-292`), and only those print (`cli.py:880-887`). A directory with a
   `package.json` has every descendant pruned and nothing in the report says so. Deferrals —
   including `directory not readable at scan time`, which is a whole subtree the person cannot
   see into — are written to `scan_deferrals` and read by nothing that reaches a person.

3. **R5, the §8.6 progress line, is inert.** `scan_run_summary` (`summary.py:25-62`) has no
   caller anywhere in `src/`; only `tests/p3/test_p3_summary.py` invokes it. The counters the
   SPEC calls "the legibility surface" are computed by a function nothing calls. `scan_deferrals()`
   and `file_path_history()` are in the same position — tested, and unreachable from any
   production path.

4. **`curation_signal` is a constant.** `inventory.py:42-53` returns `undetermined`
   unconditionally, and `candidates.py:302`'s `folder.curation_signal == _CURATED` is therefore
   always False. §1.1's "existing folder structures should mainly be preserved" has an
   observation pipeline, a database column, a validated vocabulary and no decision behind it.
   Similarly `RULE_CATEGORY` (`exclusion.py:139-142`) can never fire, because all five category
   memberships are empty.

5. **The `scan_state` fix removed one instance of a class of defect, not the class.** The only
   check on the value is "non-empty string" (`production.py:123-126`), the constant lives in
   P9's vocabulary module rather than P1's or P3's (`grouping/vocabulary.py:91`), and the
   failure mode is silent: every group becomes a group of one and every test stays green. Ask
   what else in this codebase is a string agreed on by convention between a writer and a reader
   that no schema, enum or assertion connects.

6. **P1's budget object is authoritative for one consumer.** Seven of seventeen keys are set,
   all to 8 (`cli.py:531-533`, `placement/config.py:26-34`); grouping and tree read hardcoded
   Python objects instead (`cli.py:126-144`). The 2026-08-29 split of `tree.max_folder_proposals`
   from `tree.max_depth` was made to fix a real contradiction, and the numbers that resolve it
   (4 and 5) are literals in the CLI, not values in `budget_ceilings`. Press on whether the
   ceiling table is doing any work at all.

7. **Dead code and dead parameters.** `basic_record.py:103-104` is unreachable — two statements
   after `return file_id`, one of which is a second `append_stat_observation` call, i.e. an
   intended behaviour that never happens. `supersede_ddl(table)` (`supersede.py:17-19`) ignores
   its only argument. `invalidate_extraction_state`, `set_extraction_status` and
   `set_sensitivity_state` (`files_table.py:293-366`) all take `author` and `component_version`
   and use neither; the rationale is documented, but a required-and-ignored parameter reads to a
   caller as a promise that something is recorded. `database_agent/verify.py` (V1–V4) has no
   caller in `src/` because P12 does not exist.

8. **`volume_id` is written on every row and is meaningless.** `OBSERVATION_SESSION`
   (`identity.py:19`) makes the value incomparable across processes by design, so the column
   accumulates one distinct garbage prefix per run, and `file_path_history` publishes the field
   as literal `NULL` anyway (`files_table.py:489-497`). §8.2 requires the field; what is stored
   satisfies the letter and nothing else. Note also `volume_id_for` uses `os.stat`
   (`identity.py:83`) — following symlinks — while the surrounding identity code is uniformly
   `lstat` precisely so a link and its target stay two rows.

9. **The cross-volume move rule is narrower than R2 and quietly so.** `_relocated_row`
   (`files_table.py:171-216`) only recognises a move when the *oldest* recorded copy of those
   bytes is the one that vanished. The docstring argues this errs safely (an extra record, never
   a merge), and that is probably right — but it means a user who moves the second of three
   identical files across volumes gets a new `file_id`, a new `discovery` event, and no path
   history connecting it to what they moved. Whether the report ever shows them the same file
   twice is worth checking.

10. **P11 registers nine event types where the SPEC says eight and totals twenty-four.**
    `events.py:62-78` explains the discrepancy and is likely correct; the SPEC (Contract out §3)
    has not been amended, so the two documents disagree on a closed, import-frozen vocabulary.

11. **Append-only is enforced against SQL, not against the file.** The triggers and authorizer
    (`db.py:65-76`, `:265-274`) stop `UPDATE`, `DELETE`, `REPLACE`, `DROP TABLE` and
    `DROP TRIGGER`. They do not stop `PRAGMA writable_schema`, a second connection opened with
    plain `sqlite3.connect` (which installs neither authorizer nor pragma), or anything at all
    at the filesystem level. Whether the guarantee is meant to hold against a hostile process or
    only against an inattentive one is not stated anywhere.

12. **The candidate-root half of §1.1 is dead in production.** `cli.py:584` passes
    `candidate_roots=[]`, so `APPLIES_TO_CANDIDATE_ROOT`, the second `_walk_root` loop
    (`traversal.py:67-68`), the `applies_to` column on three tables, and the early return at
    `scan.py:96-97` are all exercised only by tests. `cross_folder_moves` is likewise recorded
    and read by nothing (`selection.py:31-32`).

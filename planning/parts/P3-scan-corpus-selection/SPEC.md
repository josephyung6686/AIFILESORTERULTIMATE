# P3 — Scan and corpus selection

Owns: §1.1, §1.2
Status: contract draft

## Purpose

P3 turns a user's explicit choice of folders into the populated `files` table that every later part
reads. It is the only part that walks the filesystem to discover candidate material, the only part
that decides what is *not* in the corpus, and the only part that decides whether a previously seen
file needs to be looked at again.

It decides nothing about meaning. §1.2: "This pass does not decide what a file means or where it
belongs." §1.1: "No sorting decision is made." P3 produces a corpus and a reason for its boundary.

## Design slice owned

**§1.1 — corpus and root selection.**

- The user chooses two sets and one flag: the **sources** to be analyzed, the **candidate roots**
  that may serve as roots for a future file tree, and whether **files may move across high-level
  folders** (§1.1). These are the three selections §1.1 names, and P3 owns no others. The design
  assigns the choice to the user ("The user first chooses…"), so P3 has no source set and no root
  set until one is supplied and must not derive either from the machine's layout.
- **Roots are context, not permission** (§1.1): "At this stage, roots are context for the proposal
  canvas, not permission to move files." The candidate-root set is published to the canvas (P10) as
  landscape; it is not an authorization consumable by P11 or P12.
- **Exclusion, before scanning** (§1.1), applying to **both scanned sources and candidate roots**:
  - the eleven literal names: `node_modules`, `.git`, `venv`, `build`, `dist`, `target`, `vendor`,
    `Pods`, `site-packages`, `Library`, `__pycache__`;
  - five categories named but not enumerated by §1.1: build artifacts, caches, auto-save folders,
    previews, generated dependency trees (membership deferred — see Deferred);
  - **descendants of software project roots**, a root being a directory indicated by
    `package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`. §1.1's stated reason: "This
    prevents the proposal engine from mistaking a dependency subdirectory for a meaningful personal
    destination."
- **Protected containers are never opened, never read, never moved** (**ratified 2026-08-20**,
  closing Q7). An application bundle, a macOS package, and anything under a system location is a
  **protected container**. P3 does not descend into one, does not stat its contents, does not hash
  a byte of it, and does not create a `files` row for anything inside it. P12 may never move one
  or anything within one, and no policy, approval, or user gesture makes it movable — this is not
  a default that review can override, which is what separates it from every other refusal in this
  design.

  **What is recorded is the container, not its contents.** P3 emits one R3 exclusion verdict for
  the container itself with reason `protected_container`, carrying the container's own path and
  nothing derived from inside it. The verdict says *this is an application or system item and its
  contents were deliberately not examined* — it does not say how many files are in there, what
  they are called, or what they contain, because learning any of that requires the read this rule
  forbids. The label is **`untouched_protected`**, and it is a statement about the product's
  restraint, not about the file.

  **The user can find them.** P13 presents protected containers as a distinct, inspectable list
  (§8.6's progress line names the category; the review surface offers no action on the rows,
  because no action is permitted). A user who wonders why nothing was proposed for an application
  gets an answer instead of silence.

  **Why this is a rule and not a heuristic.** §1.1 already excludes dependency trees to stop the
  engine mistaking a subdirectory for a personal destination. This is stronger and differently
  motivated: an `.app` holds thousands of internal files whose names and contents are the vendor's,
  not the user's, and reading them would put third-party material — and, under a system location,
  material that is not the user's at all — into evidence the model may later see (§8.4). Descending
  was never a quality problem to tune; it is a boundary the product does not cross. **Membership of
  the protected set is authored, not inferred**: extension-based and location-based rules are
  written into this SPEC, and P3 guesses no new ones at run time.

- **Existing structure is mainly preserved** (§1.1). §1.1 states the system "should also know that
  existing folder structures should mainly be preserved," with the AIKonic Project example — a
  folder dense with JSON and software material that is "probably not supposed to be touched." P3
  owns the observation that makes this knowable (the directory inventory below); it does not own
  the preservation decision, which is P10's (§5.10).
- **P3 computes the curated-versus-incidental signal** (G9). §5.10 requires the canvas to show
  "whether it appears to be curated or merely incidental" and §1.1's AIKonic case requires the scan
  to know it; the inputs are the directory inventory P3 already publishes, so the computation is
  P3's. It stays an **observation**, in the sense §1.1 and §1.2 use throughout: P3 reports what the
  directory looks like and the evidence for it, and never concludes that a folder is preserved,
  adopted, flattened, or renamed. Those are P10's under §5.10, which is also where "a carefully
  curated existing folder should be treated as a strong expression of user intent" is acted on.
  Shape and deferral: Contract out R6.

**§1.2 — the reusable basic record and the stat cache.**

- One record per **file version**, containing the ten fields §1.2 names: path, filename, normalized
  filename, extension, MIME type, size, timestamps, directory position, content hash, scan state.
  §1.2's "directory position" and §2.9's "parent-folder context" are **one field**, published under
  §2.9's name (MINOR 11; R2 below).
- **The stat cache** (§1.2): "if a file's size and modification time have not changed, the engine
  reuses its existing extraction results. If either changes, it recomputes the relevant information
  instead of assuming that time only moves forward." The trigger is disjunctive (size **or** mtime),
  and it is a *difference* test, not a *newer-than* test — an mtime that moves backwards is a
  change. §1.2 gives the reason: "This protects against restores, migrations, and other filesystem
  changes that can alter state unexpectedly."

**The basic filesystem record is computed once, here** (O5). §2.9's "basic filesystem extraction"
restates most of this record, but written twice it is built twice with two shapes, so **P3 computes
it and P5 never recomputes it**: P5 emits `source_type: filesystem` observations that *reference* the
R2 row rather than re-deriving a path, size, timestamp, MIME type, or hash of its own. The two
signals §2.9 adds that §1.2 never mentions — duplicate family and version family — are neither P3's
nor P5's: they are universal facts, computed by **P6** from P1's content hashes and P5's perceptual
hashes (G5). P3 supplies the content hash they build on and nothing more.

## Contract in

**From P1 (§0, §8.2).**

- The `files` record shape and its identity fields — internal file ID, current path, path history,
  content hash and hash algorithm, filesystem volume or root identifier (§8.2). P3 populates the
  observed fields; **P1 owns identity resolution**. P3 supplies (path, size, mtime, content hash);
  P1 decides whether that is a known file version at a new path or a new version (§8.2: "If the same
  content appears at a new path, the system recognizes it as the same file version. If a file
  retains its name but its content hash changes, the system treats it as a new version and re-runs
  the relevant extractors.").
- The append-only `events` log and its record fields (§8.2), and supersede-never-overwrite. P3
  **authors** its four event types and appends them through P1's writer; P1 originates none of them
  (M8). Under P1's registration rule all four are reserved §8.2 names, so P3 registers nothing (B5).
- The three supersede columns every superseding record adopts — `supersedes`, `superseded_by`,
  `supersede_reason` (M1). `preferred` is not among them: it sits on P6's `file_facts` alone, and no
  P3 record carries it.

**From P2 (§8.5).**

- The replay-bundle format. §8.5 requires evaluation "without touching a live filesystem," and the
  bundle contains "a frozen corpus snapshot or a metadata-safe representation of one." P3 must
  therefore be runnable against a bundle-backed corpus source as well as a live filesystem, with
  identical exclusion and cache verdicts.

**From the user (§1.1).** The corpus selection record below. Absent it, P3 scans nothing.

**From the filesystem.** Directory entries, stat (size, modification time), volume identifier.

## Contract out

Six records. Field names are the design's words where the design supplies one.

**R1 — corpus selection record** (§1.1). One per scan configuration.

```text
sources[]                  folders the user chose to analyze
candidate_roots[]          high-level locations that may serve as roots for a future file tree
cross_folder_moves         the user's selection on whether files may move across high-level folders
selected_at
selected_by                user identity (§8.2 event field) — nullable, populated only on an
                           explicit user action (MINOR 10)
```

Consumed by P10 as canvas context (§1.1). `cross_folder_moves` is recorded here and carries no
enforcement in P3; where it is enforced is unsettled (Q12).

**`selected_by` follows P1's `user_id` rule exactly** (MINOR 10, P1 OQ14). §8.2 records user identity
"when there is an explicit user action", so the field is nullable and populated only then. §1.1's
selection *is* such an action — "The user first chooses…" — so a user-made R1 carries the identity;
an R1 not authored by a user leaves the field empty, and empty is a correct value rather than a
missing one. P3 defines no identity of its own and asserts nothing about how many users exist.

**R2 — the `files` row** (§1.2), the per-file-version basic extraction record.

```text
path                       P3 observes
filename                   P3 observes
normalized filename        P3 derives            (normalization rules unsettled — Q1)
extension                  P3 observes
MIME type                  P3 records            (determination method unsettled — Q6)
size                       P3 observes
timestamps                 P3 observes           (which timestamps unsettled — Q2)
parent-folder context      P3 observes           (§2.9's name; §1.2 spells it "directory
                                                 position" — one field, MINOR 11)
content hash               P3 computes; §8.2 makes it the stable identity for the file version
scan state                 P3 sets               (enumeration unsettled — Q4)
```

These are P3's ten fields from §1.2 and no more. The surrounding identity fields (internal file ID,
path history, hash algorithm, volume identifier) are P1's per §8.2. A neighbouring part may build
against fixtures containing exactly this shape.

**R2 is the only computation of this record** (O5). §2.9's basic filesystem extraction reads it; P5's
`source_type: filesystem` observations cite the R2 row and recompute none of its ten fields. A second
derivation of any of them — including a second MIME-type determination or a second hash — is a
contract violation, not an optimization, because the two would drift and §3.4's cache key is built on
the hash.

**R3 — exclusion verdict** (§1.1). One per rejected path, emitted for both sides of the scan.

```text
path
rule                       which §1.1 rule fired
rule_subject               the literal directory name, the category, or the marker file observed
applies_to                 scanned source | candidate root
observed_at
```

`rule` and `rule_subject` exist because §8.2 requires "a structured explanation or evidence
reference" and §8.6 requires the user "be able to see what is running, what has been deferred, and
why." An excluded path yields no `files` row and no descendants.

**R4 — stat-cache verdict** (§1.2). One per file per scan run.

```text
file identity              as resolved by P1
observed size
observed modification time
prior observed size
prior observed modification time
verdict                    reuse | recompute
reason                     first observation | unchanged | size changed | modification time changed
```

`recompute` includes recomputing the content hash, because §1.2 requires recomputing "the relevant
information" and §8.2 makes the content hash the thing that decides whether a new version exists.
The stat cache decides whether P3 re-reads; §3.4's cache key (content hash + extractor version +
analysis tier + model identifier + prompt fingerprint) decides whether an extraction *result* is
reused, and belongs to P6.

**R5 — scan run summary** (§8.6). The counters behind §8.6's legibility surface.

```text
files indexed
paths excluded, by rule
files reused from stat cache
files recomputed
files deferred (scan budget exhausted)
```

§8.6's example line — "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs deferred after
the OCR limit; 34 files require model review; 18 files remain unreadable" — draws `indexed` from
P3. The extraction, model-review, and unreadable counts are P5's and P8's.

**R6 — directory inventory** (§1.1). Observed non-excluded directories, each with parent and
non-excluded file count. §1.1 requires the engine to "understand the current folder landscape and to
show where a proposed branch could eventually live," and §5.10 requires the canvas to show "where a
current folder sits in the filesystem, how many files it contains."

```text
directory_path
parent_directory
file_count                 non-excluded files directly inside                    §5.10 "how many files it contains"
subdirectory_count
extension_mix              observed extensions with counts, non-excluded files only
curation_signal            curated | incidental | undetermined                   §5.10, §1.1 (G9)
curation_evidence          the observations behind the value — the counts and the
                           mix above, plus any §1.1 project-root marker observed
                           in this directory itself                              §8.2 "structured explanation"
```

**On `curation_signal`** (G9). §5.10 asks the canvas to show "whether it appears to be curated or
merely incidental", and §1.1's AIKonic case — "a lot of files such as JSON and other software
material" — is the design's one worked instance. Four constraints hold it in place:

- It is P3's to **compute**, not to act on. Every judgment that follows from it — preserve versus
  adopt, attach versus merge versus leave untouched — is P10's (§5.10). §5.10's prohibition ("existing
  folders must not be automatically flattened, renamed, or reorganized") is unaffected by this field
  and is not P3's to enforce.
- **`undetermined` is a real value, not a failure.** §8.6 requires the product to "leave the file or
  group in review rather than guessing"; a directory whose evidence supports neither reading gets
  `undetermined`, and P3 never rounds it to `incidental`.
- **`curation_evidence` travels with the value.** A signal a user can be shown and can disagree with
  must carry what produced it (§8.2's "structured explanation or evidence reference").
- The **threshold** is deferred (see Deferred). §1.1 defines none, and P3 will not invent one.

**Serialization.** R1–R4 and R6 must serialize into and re-assert from a P2 replay bundle (§8.5),
`curation_signal` included — a replay that reproduces the corpus but not its curation reading would
not reproduce P10's canvas.

## Deferred — manual design required

- **The membership of §1.1's five open-ended exclusion categories** — build artifacts, caches,
  auto-save folders, previews, generated dependency trees. §1.1 names the categories and enumerates
  no members. The eleven literal directory names in §1.1 are complete and implementable now; the
  category members are a hand-authored list and are not guessed here.
- **Software-project-root markers beyond §1.1's four** (`package.json`, `requirements.txt`,
  `Cargo.toml`, `go.mod`). §1.1's "files such as" signals an extensible set without naming its other
  members. The four literal names are implementable now; any extension is hand-authored.
- **The threshold behind `curation_signal`** (R6, G9). §1.1 gives one worked case — "a lot of files
  such as JSON and other software material" — and no number, no ratio, and no list of which
  extensions read as software material. The *record* is implementable now: R6's counts, mix, and
  evidence are observations, and `undetermined` is the honest value until a threshold is authored.
  The threshold and the software-material extension list are hand-authored and are not guessed here.

P3 defers entirely and depends on none of: the 200–300 template library (§5.7, P10); domain
fact-schema fields beyond §3.11's literal table (§3.11, P6); gazetteer contents (§3.7, P6); residual
library contents beyond the nine names in §7.3 (§7.2–§7.4, **P10** — M10 moved the residual-library
definitions from P11 to P10; P11 keeps the §7.5–§7.11 workflow).

## Done means

Each is assertable against fixtures.

1. Given a source set and a root set, one `files` row per non-excluded file, all ten §1.2 fields
   populated. (§1.2)
2. Given no source set, zero rows and zero traversal — no default corpus is synthesized. (§1.1)
3. A fixture tree containing each of the eleven §1.1 names yields zero `files` rows from inside any
   of them. The walking skeleton asserts `node_modules` specifically.
4. A directory containing `package.json` (and likewise `requirements.txt`, `Cargo.toml`, `go.mod`)
   yields zero `files` rows from its descendants. (§1.1)
5. Assertions 3 and 4 hold identically when the same directory is offered as a **candidate root**
   rather than a scan source — the exclusion "must apply both to scanned sources and to candidate
   roots." (§1.1)
6. Every excluded path has an R3 verdict naming the rule that rejected it. (§1.1, §8.2, §8.6)
7. Re-scanning an unchanged corpus yields `verdict = reuse` for every file and zero recomputes.
   (§1.2)
8. Size changed, mtime unchanged → recompute. (§1.2, "if either changes")
9. mtime moved **backwards**, size unchanged → recompute, not skip. (§1.2, "instead of assuming that
   time only moves forward")
10. A file moved to a new path with byte-identical content resolves to the same file version, and
    P3 emits no second identity. (§8.2)
11. Discovery, stat-observation, and hashing events are appended; a second scan of the same file
    adds a new stat observation and leaves the earlier one intact and readable. (§8.2)
12. Selecting a root produces no move authorization, no placement, and no destination. (§1.1)
13. Scan budget exhausted mid-run: the unreached remainder is marked deferred and counted in R5;
    the corpus is not silently truncated into something that reads as complete. (§8.6)
14. The full run reproduces from a P2 bundle with identical exclusion and cache verdicts, and with
    identical R6 `curation_signal` values. (§8.5)
15. Every non-excluded directory has an R6 row carrying a `curation_signal` and its
    `curation_evidence`; with no threshold authored, every value is `undetermined` and none is
    silently `incidental`. (§5.10, §1.1, G9)
16. The R6 signal changes nothing else: the same corpus scanned with and without a curation threshold
    authored yields identical `files` rows, identical exclusion verdicts, and identical cache
    verdicts. The signal is an observation, not an exclusion rule. (§1.1, §5.10)
17. The ten §1.2 fields are computed exactly once per file version, by P3; a fixture in which another
    part re-derives one of them fails. (O5, §1.2, §2.9)
18. A file recorded in a prior scan whose size or modification time differs on re-scan yields an
    `external modification detection` event authored by P3, alongside its stat observation and its
    `recompute` verdict. (§1.2, §8.2, M8)

## Cross-cutting answers

### Provenance (§8.2)

**P3 authors; P1 writes** (M8). P3 is the author of four of §8.2's nineteen reserved types, every one
appended through P1's append-only writer — P1 originates none of them:

```text
discovery                        a file enters the corpus                              §1.1
stat observation                 size/timestamps observed; the §1.2 stat cache reads it §1.2
hashing                          a content hash is computed at scan time                §1.2
external modification detection  a re-scan finds a recorded file's size or modification
                                 time changed underneath the product                    §1.2
```

`external modification detection` has **two authors** — P3 here, and P12 for §8.3's staleness
triggers and sync conflicts (M8). §8.2 assigns the type to nobody, and the two routes are genuinely
independent: P12 sees it when a planned action's precondition breaks, P3 sees it on the next scan.
Both rows survive and are separable by `subsystem`. P3 emits it for change detected on re-scan;
whether a *disappeared* path is the same event is unsettled (Q14).

**P3 registers no new event type.** All four are reserved §8.2 names under P1's registration rule
(B5); P3 declares nothing beyond them and mints nothing at run time.

Each event carries §8.2's fields: event type, file ID, content hash, old and new paths where
applicable, responsible subsystem, extractor or model version, prompt fingerprint where applicable,
user identity when there is an explicit user action (R1 selection), time of observation, and a
structured explanation or evidence reference.

**What P3 never overwrites.** A re-scan appends; it does not rewrite. Prior stat observations, prior
discovery records, and prior content hashes for earlier file versions all survive. A newer stat
observation supersedes an older one as the current state while the older remains inspectable
(§8.2). Exclusion verdicts likewise survive a later rule-set change — an R3 record explaining why a
path was skipped is not deleted when the path later becomes eligible.

Whether R3 belongs in `events` at all is open: §8.2 keys the event record on file ID, and an
excluded directory has no file record (Q13).

### Budgets and degradation (§8.6)

§8.6 requires "every scan" to have "an observable budget for elapsed time, memory, CPU or
accelerator usage, storage, network use, and LLM cost," and the scan is P3's operation. §8.6's list
of configurable ceilings names none for traversal or hashing — every ceiling it lists governs OCR,
image analysis, model calls, dossiers, retrieval, graphs, clusters, residual batches, or folder
proposals. P3 therefore operates under the general scan envelope with no ceiling of its own named by
the design (see Q15).

**No ceiling is not no observability (D1).** §8.6's first sentence asks for the six resources to be
*observable*, which is a separate obligation from bounding them, and it is discharged: **P1 records
all six as `scan_resource_usage`** (P1 Contract out §10) and P13 renders them. P3 bounds nothing and
measures nothing here; the disclaimer above is about ceilings only and must not be read as leaving
the scan unmeasurable.

P3 consumes zero LLM and zero network budget: §1.1 and §1.2 describe only local filesystem reads and
local hashing. P3 sits first in §8.6's degradation order, which begins with the cheap and reliable.

**Runtime obligations** ([`../../11-ops-runtime.md`](../../11-ops-runtime.md)). While a session is
open, P3 watches the selected roots and authors `external modification detection` for size/mtime
changes, appearances, and disappearances — not a background daemon. Before hashing, P3 detects a
dataless ubiquitous item and does **not** materialize it — no hash, no open, no download. P3 records
the detection and moves on; it writes **no** `extraction_runs` row, because that record is P4's and
P5 is its writer. Which `completeness` value a later attempted run carries is P4 Open question 6 —
none of the eight existing values means "the bytes are not on this machine". Full Disk Access is
required before traversing TCC-protected folders; until granted, P3 does not traverse.

**On exhaustion**: P3 retains everything already recorded, marks the unreached remainder deferred,
and reports it in R5. It does not sample, truncate the corpus silently, or relax an exclusion rule to
finish faster. §8.6: "the product should retain extracted evidence, mark the deferred stage, and
leave the file or group in review rather than guessing," and "Cost exhaustion must never turn into
lower-quality automatic classification." §8.6 also requires the difference between completed and
deferred work be visible, so that no unscanned file reads as one that "was understood and found
unimportant."

### Correction learning (§8.7)

**P3 records no correction.** §8.7's enumerated user actions — accepting or rejecting a group,
excluding a member from a packet, renaming a branch, merging or splitting, changing template order,
creating a custom template, relocating a residual file, choosing a shallow fallback, keeping a file
in place, marking a file private, disabling a suggestion type — are all owned by P9 through P12.
None is a P3 action.

The user actions P3 *does* record are the R1 selections, and §1.1 frames them as configuration
rather than correction: they say what to look at, not that a prior conclusion was wrong. P3 stores
them at scan-run scope, which is not one of §8.7's six scopes (file / group / node / template /
domain / corpus). Whether the user can override an exclusion — and whether such an override is a
corpus-scope correction under §8.7 — is not settled by the design (Q8).

### Plan versioning (§8.8)

**P3's evidence output is shared, not versioned.** §8.8: "The evidence database remains shared across
plan versions." The `files` rows (R2), stat-cache state (R4), exclusion verdicts (R3), and directory
inventory (R6) are evidence-database state and survive every plan version unchanged. A new plan
version never re-scans, never invalidates the stat cache, and never changes a content hash.

§8.8's enumerated plan-version contents include no source set, no candidate-root set, and no
cross-folder-move flag, so **R1's placement is unsettled** and is not decided here (Q11). §8.8's
governing rule still binds P3's consumers: "A new plan should never silently reclassify or move old
files."

## Open questions

Settled entries keep their original numbers so that existing citations (`P3 OQ3`, `P3 OQ5`,
`P3 OQ10`) still
resolve, and record what settled them; the rest are unanswered here.

1. **`normalized filename` is undefined** (§1.2). Unicode form, case folding, whitespace and
   separator collapse, extension retention, and diacritic handling are all unstated. *Threatens P6*
   — §3.7's word-boundary matching runs over this string, and the `MIT`-inside-"submit" failure it
   guards against is sensitive to how the string was normalized.
2. **Which timestamps** (§1.2 says only "timestamps"). Modification time is required by the cache
   rule; creation/birth time and change time are neither required nor excluded. *Threatens P6*
   (§3.10 narrow date extraction) and P1's file record.
3. **Settled — MINOR 11 (`05-minor-resolutions.md`).** `directory position` (§1.2) and `parent-folder context` (§2.9) are **one
   field, not two**. §2.9's spelling is the published name, so R2 renames; §1.2's wording is
   retained as the citation for where the field is required. P5 already used §2.9's name, so the
   two specs now agree and P4/P5 receive one field under one name. What the value *contains* is
   still only what §1.2 and §2.9 say — P3 invents no structure for it.
4. **`scan state` enumeration** (§1.2), and its relationship to §8.2's "extraction status by
   extractor tier." Are they one field or two? *Threatens P1, P5, P2.*
5. **Settled — O5 / G5.** **P3** computes the basic record (R2); P5 emits `source_type: filesystem`
   observations that reference it and recomputes none of its ten fields. §2.9's duplicate and
   version-family signals go to **P6**, as universal facts over P1's content hashes and P5's
   perceptual hashes. Nothing here is built twice.
6. **How MIME type is determined.** §1.2 requires the field; §2.9 says to "inspect the real MIME
   type or file signature where possible" and to treat extension as a routing signal only. Does P3
   sniff signatures, or record an extension-derived type that P5 later corrects? *Threatens P5's
   extractor routing.*
7. **Scan-time traversal of symlinks, aliases, macOS packages and application bundles, network
   mounts, removable storage, and cloud-synced directories.** §8.3 defines behavior for these at
   *mutation* time only. Traversal is unstated, and a descended `.app` bundle alone would inject
   thousands of spurious rows. *Threatens P5 and P12.*
8. **Exclusion override.** May the user re-include an excluded directory, or add an exclusion? §1.1
   states the rules and gives the user no control over them. *Threatens P2* (replay determinism) and
   the §8.7 answer above.
9. **Does the project-root rule exclude the root directory itself, or only its descendants?** §1.1
   says "descendants of software project roots." Whether the marker-bearing directory can still be a
   candidate root, or appear in the canvas at all, is unstated. *Threatens P10.*
10. **Ownership settled — G9; threshold deferred.** The AIKonic case is P3's to observe: R6 carries
    `curation_signal` and `curation_evidence`, and P10 keeps every judgment that follows (§5.10). What
    the design still does not supply is the **threshold** — no ratio, no count, no list of which
    extensions read as "software material" — so that is now a Deferred item rather than an open
    question, and every value is `undetermined` until it is authored.
11. **Where R1 lives** — plan version or shared evidence. §8.8's list omits sources, roots, and the
    cross-folder-move flag; the flag resembles §8.8's "placement policy settings," and roots feed the
    tree, which is plan-versioned. *Threatens P10, P11, P12.*
12. **Where `cross_folder_moves` is enforced.** §1.1 records the selection; §6 and §7 never mention
    it, and no part is assigned its enforcement. *Threatens P11 and P12.*
13. **Do exclusion verdicts get events?** §8.2's event record is keyed on file ID; an excluded
    directory has no file record and no hash. *Threatens P1 and P2* — §8.5's replay must reproduce
    the corpus boundary, not just the corpus.
14. **Disappearance and re-scan cadence.** Partly settled — M8 assigns `external modification
    detection` two authors, **P3** (§1.2 re-scan) and **P12** (§8.3 staleness), so the event is no
    longer unowned. Still open: what happens to a `files` row whose path no longer exists, whether a
    disappearance is that same event or another, and when a scan run is triggered. §1.2 covers only a
    file whose stat changed. *Threatens P12* (stale plan preconditions, §8.3) *and P11.*
15. **Hashing ceiling.** §8.2 makes the content hash mandatory identity; §8.6 names no ceiling for
    hashing or traversal. A 40 GB disk image is hashed in full under the current text. *Threatens
    §8.6's budget envelope.*
16. ~~**Scan identity, and the boundary that brackets it.**~~ **Settled — ratified 2026-08-20:
    P3 publishes `scan_run_id`; P1 adopts it.** P3 owns the scan, so P3 owns its name. P1's
    `start_scan(conn, *, scan_run_id)` takes the published value and keys
    `scan_resource_usage` on it; `11-ops-runtime.md` §3's `scan_run_id — P3's scan` on the
    session record is now true rather than aspirational. P3 may therefore sample §8.6's six
    counters through P1 — the reason it previously could not (P3-H) was that no shared
    identity existed to write them against. The original wording follows.
    New with D1. §8.6 says *"every scan"*, and
    the six resource counters are recorded per scan by P1 as `scan_resource_usage` (P1 Contract out
    §10), keyed on a `scan_id` that P1 mints locally and deliberately keeps off `events`. R5 carries
    five counters and no identity at all, so P13 cannot join the file counts it renders to the
    resource counters beside them, P2 cannot replay a scan as a named run, and nothing names the
    moment a scan begins and ends — which is what `elapsed_time`, *"wall-clock since the scan
    began"*, is measured against. P1 OQ19 points the answer here (*"it belongs wherever the scan is
    owned — P3 — not invented here"*), and P3 agrees the seam lands on it: R5 is where a published
    scan identity would live, and P3 is what would emit the start and end boundary. P3 does not
    settle another part's open question inside its own contract, so this is recorded rather than
    decided. *Threatens P1, P2, P13.*

# Phase 1: Lab file sorter agent

Date: 2026-08-16  
Status: v1.0 — aligned with the Phase 1 plan; ready to build  
Proving ground: Nutrigene lab folder (`~/Desktop/NutrigeneAI Lab Data`, relevant subtree)

Revision of the 2026-08-16 draft. Goal, users, target schema (as a *user-chosen* layout), north star, and deferred work stay. This revision fixes six gaps, specifies named-but-undefined parts, and locks the three open decisions.

This spec is Phase 1 only: **sort lab files extremely well**. The long-term product is a personal file intelligence system (see North star). Phase 1 takes only the parts of that vision that make sorting trustworthy: confidence-aware automation, ask-only-when-stuck, strict rules, and a log of decisions we can learn from later.

---

## Changelog against v0.1

| # | Change | Why |
|---|---|---|
| 1 | **New pipeline stage: Resolver**, between Grouper and Rules | Schema is `raw/{YYYY-MM-DD}/…` but only a minority of fully-routable files carry a date in their own name. Date resolution was a bullet inside the rule engine. |
| 2 | **mtime is not sufficient for auto-move** | Audit invariant: mtimes reflect copies, not acquisition. v0.1 listed mtime as a third fallback and still allowed auto-move. Now refused by the `Decision` type. |
| 3 | **`cohort_id` on Group** | Moving flattens date-only files into day folders and destroys co-location. Without `cohort_id`, “ask once, unlock a batch” has nothing to batch after the first run. |
| 4 | **`confidence` → `disposition`** | `needs_key` and `review` are routing classes, not a scale. |
| 5 | **First apply against a root is dry-run by default** | `apply(plan)` plans; `apply(plan, dry_run=False)` moves. |
| 6 | **Do not assert audit counts** | Audit arithmetic does not close (see Errata). Golden file from the fixture is the assertion source. |
| 7 | **Quiet-file rule, hardlink non-clobber, journalled pruning, verified cross-volume copy, per-run journals** | Named safety that v0.1 left implicit. |
| 8 | **Rename cut from Phase 1** | v0.1 offered suggestions with no generator and no LLM. Keep original names. |
| 9 | **`review` is a flag, not an auto-move into `_review/`** | Moving collisions changes their path and complicates re-planning. |
| 10 | **Instrument is per-group** | A day folder may mix EVOS and Leica; do not pick one instrument for the whole directory. |

---

## Goal

A standalone local app a busy lab person can run without Cursor. They point it at a messy lab folder. After they confirm a dry-run plan, it files the majority of files into a stable schema with **no per-file review**. It stops only when a human is actually required. Every move is undoable.

Success is not “an LLM guessed Images/Science.” Success is matching the *corrected* Nutrigene routing: sidecars stay glued, dates come from the Resolver ladder (never mtime for auto-move), leftovers and key-file questions are a short worklist grouped by cohort.

Phase 1 answers: **where does this group go, how sure are we, and do we need the user?** Later phases answer: what activity is it part of, how has this user handled similar files, and what is useful now.

## Non-goals (Phase 1)

- Generic Downloads / personal-file sorting (a later profile)
- First-run **profile screening** (“what do you do?”) — later; see Deferred
- Extracting `.fcs` / plate `.xlsx` / protocol `.docx` into human-readable tables (including reading the well map out of `IPSC分化EC-2.docx`)
- Renaming files, even as optional suggestions
- Forking or copying [hyperfield/ai-file-sorter](https://github.com/hyperfield/ai-file-sorter) (AGPL-3.0). Reuse *ideas* only; see `docs/research/2026-08-15-ai-file-sorter-reuse.md`
- Bundled local LLMs, visual captioning, cloud storage plugins
- Letting chat invent destination folders
- Knowledge graph, embeddings, hierarchical clustering, multimodal models, “what you need next”

## Users

People too busy or lazy to sort. Scientists, not developers. The UI is a local browser window. Conversation is a few bulk questions, not a terminal JSON workflow.

---

## Locked decisions

| Decision | Choice |
|---|---|
| First quality bar | Nutrigene lab tree, not personal Downloads |
| Interface | Standalone local agent + localhost UI |
| Classifier | Rules first (corrected `patterns.yaml`). Agent never routes around rules |
| Apply | Move in place from a plan, with per-run journals and undo |
| Dry run | Default. First contact with a root never moves until `dry_run=False` |
| Auto-move | `full` **and** `date_instrument`, and only with Resolver evidence stronger than mtime |
| Stop and ask | `needs_key`, `review`, `unclassifiable` |
| Review storage | Flag in the index; file stays put until the user acts. `_review/` is a user-chosen destination, not an auto-dump |
| Unclassifiable | Stay put, flagged; user may send a cohort to `_unsorted/` or a schema-legal path. Never guessed |
| Instrument | Per-group. A day may mix EVOS and Leica |
| Experiment | From sibling `.xit` or ancestor `Exp_*` folder; omitted when unknown, never blocking |
| Rename | Not in Phase 1. Keep original filenames |
| LLM in routing or chat | None in Phase 1. If chat gets an LLM later, output is a constrained enum validated against the schema |
| Learning in Phase 1 | Decision log only. No graph, no model training, log is not read for routing |
| State directory | `platformdirs`, keyed by canonical sort-root path. Do not hardcode `~/Library/Application Support` |

---

## Target schema

The selected folder is the **sort root**. After a confirmed apply, the app creates these directories inside it and moves **auto-eligible** files into them:

```text
<sort-root>/
  .labsort-root.json            # schema version + root identity (managed-tree marker)
  raw/
    YYYY-MM-DD/                 # ISO date, always four-digit year
      flow/
        {experiment}/
          _instrument/          # .xit, ExpSummaryForAPI.xml
      microscopy/
        leica/
        evos/
      plate-reader/
  documents/
    protocols/
  keys/                         # well maps, glossary — user-supplied
  _review/                      # only if the user sends a cohort here
  _unsorted/                    # only if the user sends a cohort here
```

Rules may only pick paths under this schema. Auto-move never targets `_review/` or `_unsorted/`.

Already-filed content under `raw/` and `documents/` of a **managed** root is skipped. Skipping those names by string match is only sound after `.labsort-root.json` is present; otherwise a pre-existing lab folder named `raw/` is not silently ignored.

For the Nutrigene proving ground, skip `2. Irrelevant files for the BO project` via a default ignore name. The user can add ignore names.

---

## Errata in the source audit — fix before copying `patterns.yaml`

The rule file is copied from `~/Personal Projects/Data Sorter/sorter-audit/patterns.yaml`. Four defects travel with it.

1. **Counts do not close.** `matched: 288` plus the two `unmatched` groups (header 26, rows summing to 28) does not equal 314. Real coverage is about 91.1%, not 91.7%. Either `leica_capture` is 202 not 204, or two files are double-counted.
2. **Three regexes fail on the audit’s own examples.** `Fib 10%`, `Fib c+`, and `ecT75` do not match. `coating_dose`, `coating_named_control`, and `freeform_shorthand` need case-insensitive matching. The report flags unstable case and then omits the flag.
3. **The 34% headline is ~29%.** Tier A only reaches 101 files if `coating_named_control` counts as automatic; `patterns.yaml` marks it `routing: date_only` (“presumably positive controls. Not confirmed.”).
4. **Two ordering warnings are false.** `US-old.fcs` cannot match `fcs_media_pass` (that pattern requires `-p<digits>`). `fib 2-5` never matches `well_replicate_index`. The hyphen ambiguity is semantic, not a matching conflict. Ordering was reasoned about, not executed.
5. **`experiment` is never captured.** Destination templates use `raw/{date}/flow/{experiment}/` but no rule captures an `experiment` field; `cyt_summary` captures nothing. The Resolver supplies it (sibling `.xit` or ancestor folder) or omits the segment.

**Testing consequence:** expected counts come from running the *corrected* rules over the checked-in fixture and freezing `tests/golden/nutrigene.json`. The audit is a sanity reference. Document every divergence. Do not assert the audit’s numbers.

---

## Architecture

```text
Folder
  → Scanner      skip junk, projects, symlinks, managed dirs, hot files
  → Grouper      sidecars glued; group key (directory, stem); cohort_id recorded
  → Resolver     date + instrument evidence ladder
  → Rules        corrected patterns.yaml; destinations only (no LLM)
  → Planner      sort-plan.json: group → destination + reason + disposition
  → Applier      journal first, then move; dry-run default
  → Agent UI     keys, leftovers; worklist grouped by cohort
  → Decision log append-only; later learning reads this
```

Rules own destinations. The agent owns conversation. The agent cannot name a folder the schema does not allow. No LLM in the routing path in Phase 1.

State lives outside the lab folder, keyed by the canonical path of the sort root, via `platformdirs` (Phase 2 collectors run on Windows instrument PCs). Per-run journals, not a single “last run” file.

First launch: this app can **move** files after you confirm; **undo** exists. First apply on a root is a dry run until the user confirms.

---

## Scanner

Walks the sort root. Records path, name, size, mtime, extension.

Skips:

- `.DS_Store` and equivalent junk
- Empty instrument `Backup/` directories
- Symlinks
- Git / source-project roots
- User ignore names (default includes the Nutrigene irrelevant folder)
- Managed dirs (`raw/`, `documents/`, `keys/`, `_review/`, `_unsorted/`) **only if** `.labsort-root.json` is present
- **Quiet-file rule (required, configurable windows):** skip any file with `mtime` inside the last 24 hours, and any file whose directory received a write in the last 5 minutes. An instrument mid-acquisition must never have output moved out from under it.
- On a failed exclusive open (file in use): **defer** that file, do not fail the scan

Writes `.labsort-root.json` at the sort root on first confirmed apply (schema version + root identity). Dry runs do not write the marker.

---

## Grouper

The unit of planning and moving is a **group**. A group never splits across destinations.

- `.jpeg` / `.jpg` + matching `.metadata` sidecar → one group
- Every other file is its own group, including each `.fcs`, `.xit`, and `ExpSummaryForAPI.xml`

`.xit` and `ExpSummaryForAPI.xml` are not glued to every `.fcs`. They have their own `full` rule to `raw/{date}/flow/{experiment}/_instrument/`. Gluing the experiment would block auto-moving well-named tubes while unlabeled wells wait on a key.

**Group key is `(directory, stem)`, never stem alone.** `ExpSummaryForAPI.xml` appears under the same name in five directories. `Exp_20260806_1` and `_2` share all nine filenames. Stem-only keys merge an aborted run into a real one.

**`cohort_id` = canonical source directory.** It persists in the index and in the undo journal. After a move, the UI can still say “these 30 images came from one folder; one answer covers all of them.”

---

## Resolver

Evidence ladder, strongest first, stop at the first hit:

| Rung | Source | Auto-move? |
|---|---|---|
| 1 | ISO date in the file’s own name | yes |
| 2 | Unanimous ISO date among siblings in the same directory | yes |
| 3 | `YYYYMMDD` ancestor folder | yes |
| 4 | `MMDD` ancestor folder, year inferred | yes, flagged `inferred_year` |
| 5 | mtime | **no** — disposition becomes `review` |

**Sibling dates must be unanimous.** `New Folder-copy-copy` carries no date; Leica captures inside it do. A directory holding two capture days is not a day folder; disagreement falls through.

**`MMDD` year inference.** Capture precedes the copy that set mtime. True year is the largest `Y` such that `date(Y, MM, DD) <= mtime`. Checking `Y` and `Y-1` covers a `1231` folder copied on 3 January. `inferred_year=True` is shown in the UI.

Instrument is resolved per group from filename prefix / extension / parent clues (`Leica_`, `QS_####.jpg`, `.fcs`, plate-export names). Mixed-instrument folders do not force a single instrument.

**Experiment ladder:** sibling `.xit` stem, then an ancestor folder shaped `Exp_20260806_1`, then omitted. A missing experiment must not push an otherwise routable tube into review; `raw/{date}/flow/` is legal.

Implementation module: `labsort/resolve.py`.

---

## Rules and disposition

Ordered regex/rules from the audit YAML, **corrected** (case-insensitive coating/shorthand; do not copy the false ordering comments as logic). Copied into this repo as `rules/nutrigene.yaml`.

Each group gets a `Decision`:

- `disposition`: see table
- `destination`: schema path, or empty
- `reason`: stable code (`leica_capture`, `fcs_coating`, `c_k_con_series`, …)
- extracted fields
- Resolver date + `inferred_year`
- `cohort_id`

| Disposition | Meaning | Behaviour |
|---|---|---|
| `full` | Destination fully determined | auto-move after confirm |
| `date_instrument` | Day + instrument known, condition unknown | auto-move after confirm |
| `needs_key` | Blocked on a user-supplied key | ask once per key type; file stays |
| `review` | Collision, archive-vs-live, aborted-run, date unresolved (mtime-only) | worklist by cohort; file stays |
| `unclassifiable` | No evidence | worklist by cohort; file stays; never guessed |
| `skip` | Junk, ignored, already filed, quiet/hot | no action |

`Decision` construction **refuses** an auto-movable disposition without a destination and without date evidence stronger than mtime. That invariant is in the type, not a code-review hope.

Hyphen semantics: `fib 2-5` is a dose when a coating word is present; `3-4` is well-image otherwise. Try coating patterns first. This is semantic, not a regex-order bug.

Never treat `-copy` as a duplicate to delete. Never dedupe on name alone; name + size equality required; name match + large size gap → `review` (aborted-run). Zip beside an unpacked folder of the same stem → `review`, never auto-delete.

---

## Planner

Writes `sort-plan.json` for the run: every group’s sources, destination, disposition, reason, cohort_id, whether it is auto-eligible, dry-run flag.

Also writes a one-paragraph human summary (counts per disposition).

---

## Applier

Four contracts, all tested:

1. **Journal before disk.** Every record is `fsync`ed before the change it describes. A crash between two moves leaves a journal undo can read. Journals are **per-run**, not one overwriteable “last run” file.
2. **Groups are atomic.** If any member fails, the group rolls back and the run stops. Already-committed groups stay committed and stay undoable.
3. **Nothing is overwritten.** Exclusive creation via `os.link`, which raises `EEXIST`. No `stat()`-then-move TOCTOU window.
4. **Dry run is the default.** `apply(plan)` does not move. `apply(plan, dry_run=False)` moves.

**Move mechanics.** Same volume: `os.link(src, dst)` then `os.unlink(src)`. The source survives until the link succeeds. Cross volume (`EXDEV`) or filesystems without hardlinks (FAT32 USB, which Phase 2 will meet): copy to a temp file in the destination directory, fsync, publish with `os.link` (or `O_CREAT|O_EXCL` where link is unavailable), verify digest, then unlink source. **`os.replace` is not allowed** — it silently overwrites.

**Identity fingerprint.** `blake2b` over `size ‖ first 64 KiB ‖ last 64 KiB`. Computed lazily, only for groups that actually move. Size in the hash means `Exp_20260806_1` (3–6 MB) and `_2` (13 KB) cannot collide.

**Directory pruning is journalled.** `New Folder-copy-copy` can be the only carrier of a capture date for files that already moved. Removing it without a journal record makes undo lossy even if every file comes back. After a group moves, prune empty source dirs only with a journal record.

**Undo.** Reverses only moves inside committed groups, reverse order, recreating pruned directories first. Identity is checked before each restore; a file edited after the run is left in place and reported. The destination is never deleted to make undo look successful. “Undo last run” means the latest per-run journal for that root.

Implementation module: `labsort/apply.py`.

---

## Key store

`keys/` in the sort root. Phase 1 accepts a well-map CSV and a label-glossary YAML, both user-supplied.

The only well map in the Nutrigene tree lives inside `IPSC分化EC-2.docx`. Phase 1 does **not** parse that document. The agent asks for a CSV and provides a **template pre-filled with the well numbers it found**. Reading the `.docx` is Phase 2.

When a key lands, `needs_key` groups are re-planned and auto-moved (after the usual dry-run/confirm policy for that root) if they become `full` or `date_instrument`. One prompt per missing key type, not per file. Worklists group by `cohort_id`.

---

## Agent + local UI

Localhost web UI, Python backend, plain language. No LLM in Phase 1. If one is added later for conversation, its output must be a constrained enum — provide key, choose from a short list of schema-legal destinations, skip, undo — never a free-text path. Validate against the schema before anything moves.

Post-scan (dry-run) message shape:

> I would file 271 groups by date and instrument. I need a well map for 10 flow files, and I can't place 26 images. Two archives and a possible aborted run need review. Nothing has moved yet.

Required actions: pick folder · run (dry) · confirm apply · status and counts · answer key prompt (drop CSV / paste path / fill template) · leftover worklist grouped by cohort · undo last run.

---

## Decision log

Append-only JSONL in the platform state dir for the sort root. Each event: timestamp, run id, group id, cohort_id, source signature (paths + sizes + fingerprint), disposition, reason, destination, actor (`rule` | `user`), action (`planned` | `auto_move` | `ask` | `key_provided` | `resolved` | `skipped` | `undo`).

Not a knowledge graph. Phase 1 writes it and does not read it to change routing.

---

## Data flow

1. User picks a sort root.
2. Scanner lists (quiet/hot files deferred); Grouper emits groups with `cohort_id`.
3. Resolver attaches date/instrument evidence.
4. Rules emit `Decision`s; Planner writes the plan + summary.
5. UI shows the dry-run plan. Nothing has moved.
6. User confirms → Applier writes the run journal, then moves auto-eligible groups; writes `.labsort-root.json` if missing.
7. Stuck groups stay in place, listed by cohort.
8. User supplies keys → re-plan those groups → dry-run then move if now auto-eligible.
9. User resolves leftovers (schema-legal path, `_review/`, `_unsorted/`, or skip).
10. Undo last run restores from that run’s journal (files + pruned directories).
11. Every planned auto-move, ask, answer, skip, and undo appends to the decision log.

---

## Error handling

- **Atomic groups.** Member fails → roll that group back, stop the apply loop. Earlier committed groups stay moved and undoable. Tell the user which group failed.
- **`EEXIST` on link.** Do not overwrite. Same fingerprint → skip as already filed. Different size/fingerprint → `review`, file stays.
- **Permission, file in use, disk full.** Stop apply; keep journal; one-sentence error plus undo for committed groups.
- **Undo identity mismatch.** Skip that row; report; do not delete the destination.
- **mtime-only date.** Cannot construct auto-move; `review`.
- **Disagreeing sibling dates.** Fall through the Resolver ladder; never pick a date.
- **Invalid UI destination.** Retry; do not move.
- **Crash mid-apply.** Journal fsync before each change; restart offers undo of that run.
- **Truncated journal.** Crash-recovery test: refuse to apply further; offer undo of committed records only.
- **Offline.** Phase 1 is fully local.

---

## Testing

Fixture-driven. Do not run the first implementation against the live Desktop folder.

**Fixture generation.** Same names, relative paths, and sidecar pairings as the real tree, with **sparse files at real byte counts** (`open(p,"wb").truncate(size)`). Aborted-run detection is a size gap; uniformly tiny dummies cannot exercise it.

**Golden output, not audit numbers.** Run corrected rules over the fixture, review by hand, freeze `tests/golden/nutrigene.json`. Compare to the audit as sanity; document divergences (several will be audit errors).

Required tests:

- **Date / Resolver:** filename beats folder beats mtime; MMDD year inference; new-year rollback; unanimous siblings date a `New Folder`; disagreeing siblings do not; mtime-only cannot auto-move
- **Moves:** never overwrites; same name + different size is not a duplicate; sidecar travels with its image; group key `(directory, stem)` does not merge `Exp_…_1` and `_2`
- **Transaction:** dry run touches nothing; group rolls back when one member fails; rerun skips already-filed without error
- **Undo:** restores files and pruned directories; leaves an edited file in place and reports it
- **Quiet-file rule:** recent mtime / hot directory is skipped
- **Crash recovery:** truncated journal does not lose committed groups and does not apply uncommitted ones
- **Agent guard:** illegal destination does not move
- **Key unlock:** well-map CSV reclassifies `needs_key` groups
- **Decision log:** apply writes `auto_move`; resolution writes `resolved`; undo writes `undo`
- **Golden routing:** assert `tests/golden/nutrigene.json`

Live Nutrigene data is a manual run after fixtures are green: dry run first, then apply, undo available.

---

## Implementation shape

- Python 3.12+
- Package `labsort`: `scanner`, `grouper`, `resolve`, `rules`, `plan`, `apply`, `undo`, `decision_log`
- Localhost HTTP UI calling the engine
- Rules: YAML, Nutrigene profile only (`rules/nutrigene.yaml`, corrected)
- Plans and journals: JSON/JSONL in `platformdirs` state dir
- Dependencies: stdlib + `pyyaml` + `platformdirs`
- No Qt, no llama.cpp, no AI File Sorter source

---

## North star

Long-term this is not a category picker. It becomes a **personal file intelligence system**: a continuously updated model of the user’s digital activity — what a file is, what work it belongs to, how this user has handled similar material, and what action is useful now.

The lasting advantage is not a generic model. It is a personalized model of projects, relationships, habits, and decisions that improves with every interaction.

Take these ideas into the product over time. **Do not build them in Phase 1** except where this spec already requires them.

| Idea | Phase 1 | Later |
|---|---|---|
| Confidence-aware automation | Yes — auto `full` and `date_instrument` after confirm; queue the rest | Same policy on other profiles |
| Active learning | Yes — ask once for keys / leftovers, grouped by cohort | Ask only on uncertain or high-stakes decisions |
| Neuro-symbolic rules | Yes — schema + regex own destinations; protect app/git trees; never split sidecars; mtime cannot auto-move | User-authored rules (“keep tax docs together”, “do not upload confidential files”) |
| Continual learning | Decision log written, not used for routing | Learn from approvals, corrections, searches, opens, moves, names — without full retrain |
| Personalized decision model | No | Predict folder / tags / related files this user would choose |
| Profile screening | No | First-run interview selects or generates a profile |
| Hierarchical clustering | No | Work → project → workstream (e.g. Plasmole → Research Outreach) |
| Dynamic knowledge graph | No | Files ↔ projects, people, orgs, events, versions |
| Temporal learning | No | Sequences: download paper → notes → results → slides |
| Multimodal understanding | No | Filenames + text + images + metadata + apps + people |
| Personal information OS | No | Detect projects, related material across folders, duplicates/versions, next actions, surface when relevant |
| Lab extraction | No | Raw instrument data → human-readable tables; parse protocol `.docx` for well maps (Phase 2) |

A personal graph that files a Leica capture under “Research / Photos” is a failed product. Every later layer still has to obey the active profile’s schema and invariants.

---

## Deferred

Order after Phase 1 is green:

1. **Profile screening** — first-run interview (lab vs personal vs other, instruments, how they think about folders). Produces a profile: schema + rules + ignore list. Must not weaken move/undo/sidecar/Resolver safety. Phase 1 hard-codes Nutrigene.
2. **Use the decision log** — retrieval of past approvals as hints inside the same profile (still no graph).
3. **Phase 2 lab extraction** — immutable `raw/`; local extraction of `.fcs` / plate `.xlsx` / protocol `.docx` into tables (this is when the well map can be read from Word).
4. **Personal-files profile** — Downloads / mixed life files, only after the lab profile is nailed.
5. **Graph + temporal + hierarchy** — projects, people, versions, activity sequences.
6. **Personalized predictor + OS features** — suggest next action, surface files when relevant, detect duplicates/outdated versions across folders.
7. **Rename suggestions** — only after a real generator exists (rule-field canonical names or a later constrained model).

---

## Reference

- Lab audit: `~/Personal Projects/Data Sorter/sorter-audit/report.md`
- Patterns (copy then correct): `~/Personal Projects/Data Sorter/sorter-audit/patterns.yaml`
- Idea-only reuse map: `docs/research/2026-08-15-ai-file-sorter-reuse.md`

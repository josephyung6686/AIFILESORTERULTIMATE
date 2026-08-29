# What to reuse from hyperfield/ai-file-sorter

Source: [hyperfield/ai-file-sorter](https://github.com/hyperfield/ai-file-sorter) (v1.9.2, AGPL-3.0, Qt/C++).
Date: 2026-08-15.

This is a **reuse map**, not a fork plan. We should **not copy their source**. License, stack, and product shape all argue against it. We should reimplement a smaller set of *behaviors* in our own code.

Related local work: `~/Personal Projects/Data Sorter/sorter-audit/` — the Nutrigene lab folder audit. That audit is the better spec for *lab* sorting than this repo.

---

## Verdict

AI File Sorter is a polished **consumer Downloads organizer**: LLM categories like `Documents / Invoices`, visual rename of `IMG_2048.jpg`, Qt desktop UI, bundled llama.cpp.

Database Agent Phase 1 needs to be a **safe, review-first file router** that can later grow into lab organization + extraction. The lab audit already showed the failure mode of generic tools: **91.7% of filenames match a regex, but only 34% can be routed**. An LLM that files microscope images under `Images / Science` would look smart and still destroy the dataset.

**Reuse their workflow and safety contract. Do not reuse their taxonomy, UI, or C++ runtime.**

---

## License (hard constraint)

The repo is **GNU AGPL-3.0**. If we copy their C++, prompts, or substantial source into this project, this project becomes AGPL too (including if we ever ship a network service).

Allowed:

- Reading the architecture and rewriting the *ideas* in original code
- Matching a similar user-facing flow (scan → suggest → review → apply → undo)

Not allowed without going AGPL:

- Copying `CategorizationService`, `UndoManager`, prompt text, or other source
- Vendoring the repo as our engine

---

## What the codebase actually is

Cross-platform Qt6 desktop app. Layers from `docs/architecture.md`:

| Layer | Their classes | Role |
|---|---|---|
| UI | `MainApp`, review/preview dialogs | Qt GUI |
| Orchestration | `AnalysisCoordinator`, `AnalysisWorkflowContext` | Scan → categorize → review plan → apply |
| Categorization | `CategorizationService`, `LocalLLMPromptBuilder`, whitelist store | LLM + taxonomy + cache |
| Persistence | `DatabaseManager`, `UserLearningStore`, `UndoManager` | SQLite cache, approved-label learning, undo plans |
| Headless | `HeadlessAnalysisCommand`, `HeadlessReviewApplyService` | CLI/JSON contract for Explorer and scripts |
| Storage | `IStorageProvider`, `LocalFsProvider`, OneDrive plugin | Move/rename behind a provider |

Language mix is ~C++ with a llama.cpp runtime, SQLite, and optional remote OpenAI/Gemini APIs.

---

## Steal these ideas (reimplement, do not copy)

### 1. Review-plan workflow (the product)

Nothing mutates until the user confirms. Their pipeline is:

1. Point at a folder
2. Analyze (rules + optional LLM)
3. Build a review table (category, subcategory, optional rename)
4. User edits / rejects
5. Apply creates folders and moves/renames
6. Persist an undo plan

This is the right product shape for lab data. Our existing audit already said the same thing: **a review queue, not a best guess**.

Key surfaces to *study*, not copy:

- `AnalysisCoordinator` — end-to-end orchestration, GUI-agnostic
- `HeadlessAnalysisCommand` / `docs/headless-runtime-contract.md` — `--review-only` vs `--auto-apply`, JSON review plans (`aifs.headlessReviewPlan`)
- `HeadlessReviewApplyService` — apply a saved plan without re-analyzing
- `DryRunPreviewDialog` — preview destinations before apply

For us: a `SortPlan` JSON (source, destination, reason, confidence, group-id) plus apply/undo. Headless first is fine; GUI can wait.

### 2. Undo as a first-class artifact

`UndoManager` stores a plan of `{source, destination, size, mtime, stable_identity}` and can reverse the last run after the app restarts.

We need this on day one. Lab files are irreplaceable. Copy their *contract*:

- Write the undo plan **before** mutating
- Identity is more than filename (size + mtime / hash)
- "Undo last run" survives process restart

### 3. Sidecar / atomic grouping (we need a stricter version)

They treat macOS bundles as one object (`FileScanner::is_file_bundle`). They do **not** have lab sidecars.

Our audit requires a stronger rule: **`.jpeg` + `.jpeg.metadata` are one object**. Same for `.fcs` + `.xit` + `ExpSummaryForAPI.xml` traveling together.

Study `FileScanner` for skip/junk/bundle logic, then write our own `FileGrouper`.

### 4. Never auto-delete “copies”

They skip junk (`.DS_Store`) and protect project roots. They do not encode our lab-specific traps, which we must:

- Never dedupe on name alone (`Exp_…_1` vs `Exp_…_2` share names, different sizes)
- `-copy` is a second capture, not a duplicate
- Archives next to unpacked folders go to `_review`, never auto-delete

### 5. Protected roots

`ProtectedProjectDetector` skips Unity/Unreal/Godot/Blender/git/source trees during recursive scans. We should skip git repos and any folder that looks like an already-organized `raw/` tree so we do not re-sort a sorted library.

### 6. Cache vs learned behavior (two stores)

They split:

- `DatabaseManager` — disposable categorization cache (speed + consistency hints)
- `UserLearningStore` — only **user-approved** review decisions, with embeddings for retrieval

This split is worth copying as a *design*: cache can be wiped; approvals are sacred. For Phase 1, a simpler version is enough: store approved routes keyed by pattern/signature, not a full embedding store.

### 7. Constrained vocabulary (whitelist), not free LLM labels

`WhitelistStore` + smart branching (`Documents → Invoices, Receipts` vs `Images → Screenshots`) is the closest analog to our lab schema:

```
raw/{ISO-date}/{instrument}/{experiment}/
documents/protocols/
keys/
_unsorted/
_review/
```

Do **not** use their default taxonomy (`Documents`, `Images`, `Videos`). Use a **schema whitelist** the way they use category whitelists: the model/rules may only pick destinations that exist in the schema.

### 8. Consistency from recent similar files

`CategorizationService::collect_consistency_hints` reuses recent assignments for the same extension. For a lab day-burst, this is useful: once the user files three Leica images under `2026-08-06/microscopy/leica/`, the rest of that day should follow unless a rule disagrees.

### 9. Document text extraction (Phase 2, not Phase 1)

`DocumentTextAnalyzer` extracts text from txt/md/csv/json/xml, PDF (PDFium), and Office (`docx`/`xlsx` via libzip+pugixml), then asks an LLM for a summary + rename.

For labs, the valuable part is **extraction of well maps from protocol `.docx`**, not renaming. Park this for Phase 2. Do not build PDFium/llama.cpp now.

### 10. Storage provider interface

`IStorageProvider` / `LocalFsProvider` so moves go through one API (local now, NAS/cloud later). Cheap to do from the start; do not build their OneDrive plugin.

---

## Do not use (wrong product or too expensive)

| Their piece | Why not |
|---|---|
| Entire Qt/C++ app | Wrong stack for a new agent; AGPL; months of packaging |
| Bundled llama.cpp / Gemma / LLaVA visual backends | Microscope images are not `IMG_2048.jpg`. Visual rename would invent captions and destroy instrument names |
| Default category taxonomy | `Images / Science` is a misfile for `Leica_2026-07-30 3-4.jpeg` |
| Filename localization / slugify-to-English | Lab names carry meaning (`fenxuan`, `well3`, `%` doses). Prefer keep original names in Phase 1 |
| MediaInfo audio/video rename | Out of scope |
| Updater, MSIX, Explorer extension, translations | Product chrome, not sorting quality |
| Cloud storage plugins | Later, if ever |
| Embedding-based taxonomy retrieval | Overkill until review-learning is proven |

---

## Mapping onto our two-phase product

### Phase 1 — sort files extremely well

Build a **plan-and-review router**, proven on the Nutrigene lab tree (and later on a messy Downloads folder if we want a second profile).

Minimum engine, informed by both this repo and `sorter-audit/`:

1. **Scanner** — recursive listing, skip junk, skip protected projects, skip symlinks
2. **Grouper** — sidecar atomicity, instrument bundles (`.fcs`+`.xit`+xml)
3. **Classifier** — ordered regex/rules from `patterns.yaml`; confidence tiers `automatic` / `date+instrument` / `needs_key` / `review` / `unclassifiable`
4. **Planner** — destination paths under a schema; never apply yet
5. **Review** — human confirms, supplies glossary / well-map when asked
6. **Apply** — move groups together; write undo plan first
7. **Learn** — store approved decisions; reuse as hints next run

LLM in Phase 1 is optional and **constrained**: it may only choose among schema destinations, and only after rules fail. It must not invent folder names. It must not rename lab files by default.

What “nailed” means (from the audit, not from AI File Sorter):

- Sidecars never split
- Filename date beats mtime
- 34% auto-route without a key file; the rest land in a *partially correct* date/instrument folder or `_review`
- Asking for `keys/well-map-*.csv` and a glossary is a feature, not a failure
- Undo restores the previous tree

### Phase 2 — organization + local extraction (later)

After sorting is trusted:

- Keep `raw/` immutable
- Extract human-readable tables from `.fcs` / plate `.xlsx` / protocol `.docx`
- Their `DocumentTextAnalyzer` idea (local text extract → structured output) is the seed for that, aimed at tables, not filenames

---

## Recommended relationship to the repo

**Not a dependency. Not a fork. A checklist.**

If we ever want to run their app as a black-box comparison on a *personal Downloads* folder, we can install the binary. We should not link it, vendor it, or port `CategorizationService.cpp`.

Closest files to reread when implementing Phase 1 (ideas only):

1. `docs/headless-runtime-contract.md` — review plan JSON, status machine
2. `app/include/AnalysisCoordinator.hpp` + `AnalysisWorkflowContext.hpp` — workflow split from UI
3. `app/include/UndoManager.hpp` — undo plan fields
4. `app/include/FileScanner.hpp` + `ProtectedProjectDetector.hpp` — scan policy
5. `app/include/UserLearningStore.hpp` — approvals ≠ cache
6. `app/include/WhitelistStore.hpp` — constrained destination vocabulary
7. `app/include/MovableCategorizedFile.hpp` — preview paths vs actual move

Our own files that already beat their taxonomy for labs:

- `~/Personal Projects/Data Sorter/sorter-audit/report.md`
- `~/Personal Projects/Data Sorter/sorter-audit/patterns.yaml`

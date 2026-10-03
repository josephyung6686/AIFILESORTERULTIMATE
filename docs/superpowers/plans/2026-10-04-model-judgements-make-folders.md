# Model judgements make folders — Plan

**Goal:** organise places loose files. Today the AI names each file's kind correctly (e.g. screenshots → `photos.screenshot-captures`, resume → `career.recruiting`), but on a 33-file live run **0 of 32** loose files got a destination.

**Cause (measured, agent N1, 4 Oct):** model answers are stored as `llm_supported` facts; grouping seeds groups only from `direct`/`validated` facts (`src/grouping/seeds.py:49 ANCHOR_STATES`, deliberate — "letting one seed a group lets the model…" docstring lines 5–16); proposed folders come only from accepted groups → no group, no folder, every loose file abstains. Second cause: the default folder's kind is decided by one file's rule facts outvoting 16 model photo readings, producing a whole-Desktop "Which of these is career?" question.

**Constitution check:** "LLM decides, code delivers." The model's per-file kind is a decision; code should deliver a folder for it. The seed rule exists so a single model guess cannot invent a group out of nothing — keep that safety, add a narrow path.

**First:** read the teammate's branch `origin/cursor/understanding-before-outline-16e7` ("Seat understanding answers before the outline is written", "Raise the understanding budget and add a residuals pass") — it may already address this. Merge or reconcile before building.

## Options

| | What | Risk |
|---|---|---|
| A (recommended) | **Kind folders without a group:** after site G, every branch kind the model assigned to ≥ N files (N=2, or 1 for a single clearly-named file) gets its library template folder; those files are placed there with the model's reason. No group needed; groups still need anchors. | A wrong model kind files a few files in a wrong folder — visible in the proposal, confirmable, undoable. |
| B | Let `llm_supported` facts seed groups when ≥ 2 files agree and the person allowed the AI for that folder. | Changes the grouping contract everywhere; harder to reason about. |
| C | Leave sorter; chat offers type-based quick sort for loose files. | Bypasses the sorter; doesn't fix the sorter score. |

## Tasks (Option A)

1. **Test (failing):** 6 screenshots + a resume + a syllabus, fake model returning kinds → proposal has `Photos/Screenshots` (6), `Career/Recruiting` (1), `Education/…` (1); loose files placed with reasons; protected files untouched. Path: `tests/integration/test_model_kinds_make_folders.py`.
2. **Kind folders:** in tree design (where accepted groups become nodes), add nodes for model-assigned kinds with no group, named from the library's template label for that kind (no new vocabulary). Files: `src/tree_design/pipeline.py`, placement eligibility in `src/placement/`.
3. **Default kind:** weigh model kinds by file count against rule facts when choosing the default folder's kind (a majority of model readings beats one file's rule facts); the whole-folder kind question is asked only when no kind holds a majority. File: the default-situation chooser (see 109-ACTION-PLAN).
4. **Re-organise after answers:** when the last open question is answered, the chat reruns organise (one confirm), so answers visibly change the plan.
5. **Offered homes:** expose the sorter's leftover homes ("Temporary Screenshots", "Review Later") as a confirmable option in chat.
6. **Measure live on ≤ 50 files** (credit rule), then user-judge both halves.

**Owner decisions in this plan:** Option A vs B; N; whether a single file with a confident model kind gets its own folder.

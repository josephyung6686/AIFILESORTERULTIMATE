# Context Graph + ML Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the local context graph (items + evidenced relationships + views) and the ML seams (semantic recognition default-when-available, read-only hybrid meaning search) without silent moves, without promoting semantic edges into life links, and with tests green.

**Architecture:** Additive `src/items/` package over the existing SQLite file index. Durable `item_id` follows `observe_path`. Relationships are a separate table from `group_edges`. Semantic retrieval stays in grouping; inferred life links are review-only; meaning search is read-only over vectors + facts.

**Tech Stack:** Python 3, SQLite, existing MiniLM ONNX encoder (`readers.embedding_minilm`), pytest, CLI entry in `src/cli.py`.

**Authority:** `docs/item-relationship-model-plan.md` (stages 1–7). Kill rules there are binding.

**Do not commit** unless the user explicitly asks. Verify with pytest after each task.

---

## File map

| Path | Role |
|---|---|
| `src/items/schema.py` | Tables + `create_items_schema` |
| `src/items/identity.py` | File items following `observe_path` |
| `src/items/relationships.py` | Witnessed link projection (Stage 2) |
| `src/items/decisions.py` | Approve / reject / undo (Stage 3) |
| `src/items/profiles/` + `profile_loader.py` | Pluggable packages (Stage 4) |
| `src/items/views.py` | Five query functions (Stage 5) |
| `src/items/mailbox.py` | Fixture mail/calendar (Stage 6, exists) |
| `src/items/search.py` | Hybrid meaning search (ML) |
| `src/cli.py` / `src/orchestrator.py` | Bootstrap + scan projection + commands |
| `tests/items/*` | Stage fixtures |

---

### Task 1: Wire Stage 1 (ported) and prove identity

**Files:**
- Modify: `src/cli.py` (import + `_bootstrap` + `sync`/`view`/`suggest` routing)
- Modify: `src/orchestrator.py` (`project_after_scan` after scan)
- Exists: `src/items/{schema,identity,mailbox,commands,deadline_view,suggest}.py`
- Test: `tests/items/test_file_identity.py` (+ mailbox/deadline/suggest)

- [x] **Step 1:** Ensure `create_items_schema` is called from `_bootstrap`
- [x] **Step 2:** Call `project_after_scan` from `run_p1_p7` after `scan(...)`
- [x] **Step 3:** Route `sync` / `view` / `suggest` in `main`
- [x] **Step 4:** Run `pytest tests/items/ -q` and fix failures until green

**Done when:** Stage 1 identity checks pass (rename keeps `item_id`, edit keeps `item_id` with new version, live copies are two items).

---

### Task 2: Stage 2 — witnessed links only

**Files:**
- Create: `src/items/relationships.py`
- Create: `tests/items/test_witnessed_links.py`
- Modify: call site after grouping or from a dedicated projector invoked post-scan

**Rules from plan §11 Stage 2:**
- Project `duplicate` and `version-family` from `group_edges` when `evidence_ref` non-empty
- Add `duplicate-of` from equal `content_hash` on two live file items
- Do **not** project `mutual-semantic-retrieval` or `bounded-session`
- confidence `witnessed`, state `proposed`, evidence_refs non-empty
- Kill: empty evidence row, or any semantic edge copied into `relationships`

- [x] **Step 1:** Write failing tests for hash duplicate, unrelated third file, and semantic-edge non-projection
- [x] **Step 2:** Implement projector
- [x] **Step 3:** Run tests green

---

### Task 3: Stage 3 — approve / reject / undo

**Files:**
- Create: `src/items/decisions.py`
- Create: `tests/items/test_link_decisions.py`
- Modify: `src/database_agent/events.py` only if `link` can be added to `CORRECTION_SCOPES` without breaking closed-vocab tests; otherwise store decisions in items package events projection and document the owner-edit needed

**Rules:**
- Reject suppresses same `basis_key` on rebuild
- Different pair with same `rel_type` still proposed
- Accept then undo restores live projection without deleting history
- Reject must **not** change `Detector.explain` schema for the file

- [x] **Step 1:** Failing tests
- [x] **Step 2:** Implement (`relationship_decisions` table; `link` scope left for owner edit of `CORRECTION_SCOPES`)
- [x] **Step 3:** Green

---

### Task 4: Stage 4 — pluggable profile packages

**Files:**
- Create: `src/items/profiles/student.json`, `src/items/profiles/files_only.json`
- Create: `src/items/profile_loader.py`
- Create: `tests/items/test_profile_packages.py`

**Rules:**
- One loader; no `if profile == "student"` in detector
- `files_only` proposes no `member-of`
- Safety holds unchanged on passport fixture
- Empty package leaves recognition unchanged

- [x] **Step 1–3:** TDD as above

---

### Task 5: Stage 5 — five view queries

**Files:**
- Create: `src/items/views.py`
- Create: `tests/items/test_views.py`
- Optionally extend `items/commands.py` `view` subcommands

**Rules:**
- Folder / Table / Board / Timeline / Graph query functions
- Graph default cap 40; semantic edges never drawn; inferred omitted + hidden count
- No path reaches `mutation/execute.py`

- [x] **Step 1–3:** TDD as above

---

### Task 6: ML — semantic recognition when model present

**Files:**
- Modify: `src/cli.py` `_semantic_classifier` / `--semantic-model` help + optional default probe
- Create: `tests/` covering fallback when model dir missing
- Do **not** auto-download weights
- Keep lexical-first composition and `SEMANTIC_*` floors

**Behavior:**
- If `~/.graph-agent/models/minilm` (or flag path) has `model.onnx` + `tokenizer.json`, compose `SemanticRecogniser`
- Else behave exactly as today (detector only)
- P9 embeddings follow the same presence probe when recognition is enabled that way

- [x] **Step 1–3:** TDD for on-when-present / off-when-absent

---

### Task 7: ML — read-only hybrid meaning search

**Files:**
- Create: `src/items/search.py`
- Create: `tests/items/test_meaning_search.py`
- Modify: `src/items/commands.py` + `cli.main` for `search` command

**Rules:**
- Read-only; moves nothing
- Combines fact/FTS hits with optional embedding neighbors when vectors exist
- Protected items counted as present-but-unopened, never silently omitted
- Embeddings alone never invent a life relationship row

- [x] **Step 1–3:** TDD as above

---

### Task 8: Full verification

- [x] Run `pytest tests/items/ -q` (35 passed)
- [x] Run composition-root / identity-related tests touched by wiring (63 passed with identity)
- [x] Fix any regressions
- [x] Summarize what shipped vs Stage 6/7 leftovers (live Gmail still fixture-only)

---

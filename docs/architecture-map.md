# Architecture map — sorter engine vs context graph

Date: 2026-10-02.  
Status: **binding for new work** on the context-graph path.  
Product direction: [`docs/product-one-pager.md`](product-one-pager.md).  
Engine design (still authoritative for sorting): [`planning/00-database-agent-product-design.md`](../planning/00-database-agent-product-design.md).  
Item/relationship stages: [`docs/item-relationship-model-plan.md`](item-relationship-model-plan.md).  
Earlier gap audit (what was missing as of 2026-09-30): [`docs/architecture-audit.md`](architecture-audit.md).

This document does not add product features. It names the layers that exist, which edges are allowed, and which edges are kill rules.

---

## 1. Two products, one repository

| Path | Job | May move files? |
|---|---|---|
| **Sorter engine** | Scan → evidence → facts → groups → propose tree → freeze → classify → apply / undo | Yes, only after freeze + apply |
| **Context graph** | Items + evidenced relationships + read-only views / search / suggest | **No. Never.** |

They share one SQLite file and the file index (`files`, `observe_path`). They do **not** share a write path to disk for organization.

Composition root: `src/cli.py` and `src/orchestrator.py` may call both. Packages under `src/items/` may not call the sorter’s move stack.

---

## 2. Layers (bottom → top)

```
Filesystem (system of record)
    ↑ open_target / current_path only; no virtual FS
SQLite working memory
    ├── P1 file index          database_agent (files, events, observe_path)
    ├── Evidence / facts       scan_agent, readers, facts, recognition, privacy
    ├── Grouping graph         grouping (group_edges — file-version neighbourhood)
    ├── Tree / placement       tree_design, placement (tree_nodes — proposed folders)
    ├── Mutation (sorter only) mutation, apply_run  ← moves bytes
    └── Context graph          items (items, item_versions, relationships, …)
            ├── identity projection from observe_path
            ├── witnessed / decided links
            ├── profile packages (data)
            └── read-only views, search, suggest, fixture mailbox
```

**Recognition / privacy** sit beside facts: they type or hold material. Holds are independent of profiles and of links.

**Questions / profile answers** (`questions/`) gate recognition (`declared_lives`) and feed declared course/project names. They are not the context-graph store; items may mint from them later.

---

## 3. Stores and what each is for

| Store | Owner package | Purpose | Not for |
|---|---|---|---|
| `files` + path history | `database_agent` | Live path, hash, version identity | Life links between email and project |
| `group_edges` | `grouping` | File–file neighbourhood for dossiers | Context-graph life links (esp. semantic / session) |
| `tree_nodes` | `tree_design` | Proposed / frozen filing tree | Folder *view* of the context graph |
| mutation journal | `mutation` / `apply_run` | Applied moves and undo | Anything under `items/` |
| `items` / `item_versions` | `items` | Durable things the person points at | Replacing `file_id` as the hash identity |
| `relationships` | `items` | Evidenced directed claims + state | Float weights; silent approvals |
| `relationship_decisions` | `items` | Accept / reject / undo of a `basis_key` | Changing recognition schema |
| Profile JSON packages | `items/profiles` | Allowed item/rel types, caps | Turning off safety holds |

---

## 4. Allowed edges

| From | To | Allowed? | Notes |
|---|---|---|---|
| `orchestrator` / scan | `items.identity.project_after_scan` | Yes | Projection after observe_path |
| `items.relationships` | `group_edges` (read) | Yes | Project only `duplicate` / `version-family` with non-empty evidence |
| `items` | `files` / `observe_path` results (read) | Yes | Identity and open_target |
| `items.mailbox` | fixture JSON (read) | Yes | Live Gmail/Calendar not yet connected |
| `items.views` / `search` / `suggest` / `deadline_view` | `items` + `relationships` (read) | Yes | Cap graph; hide inferred on default graph |
| `items.decisions` | `relationship_decisions` + relationship state | Yes | Exact `basis_key`; no recognition write |
| `cli` reserved words `sync` / `view` / `suggest` / `search` | `items.commands` | Yes | Must not enter `apply_run` |
| `cli` `--apply BRANCH` / freeze / undo-everything | `apply_run` / `mutation` | Yes | Sorter path only |
| `items/**` | `mutation` or `apply_run` | **No** | Kill rule (section 6) |
| `items` Folder view | `tree_nodes` | **No** | Reads `open_target` / `files.current_path` |
| `items` relationships | `mutual-semantic-retrieval` / `bounded-session` as life links | **No** | Stay in grouping only |
| Cloud / model | invent destination, approve link, bypass hold | **No** | Product one-pager |

---

## 5. Agent ladder (architecture only)

One store, three privileges. None write `state = approved`. None call `mutation.execute`.

1. **Connector** — inserts `proposed` links (prefer witnessed). Inferred requires stricter evidence; not silently drawn on the default graph.
2. **Nudge** — warnings from missing required pairs / deadlines (`suggest` is a thin slice). No new approved rows, no moves.
3. **Assistant** — answers with citations (`item_id` + evidence). Held bodies omitted from any cloud payload.

Approval is always a person event on a link (or a sorter freeze/apply on the other path).

---

## 6. Kill rules

These fail a stage or a PR if violated:

1. **`src/items/` imports `mutation` or `apply_run`** (static import or `importlib` of those packages).
2. **Context-graph CLI verbs move bytes** (`suggest --apply` must refuse; view/search/sync must not call apply).
3. **Empty `evidence_refs` on a relationship row.**
4. **Semantic or session `group_edges` copied into `relationships`.**
5. **Default graph returns uncapped corpus** (student package cap 40; hidden inferred count required).
6. **Link reject changes recognition `schema_id`.**
7. **Profile package clears a safety hold** (`finance` / `identity` / `medical` / `legal`).
8. **Held item body or attachment text in a model-request builder.**

---

## 7. What is built vs open (architecture view)

**Built (or on this working tree):** file `item_id` over `observe_path`; items schema; fixture mail/calendar; deadline + five view *queries*; witnessed duplicate/version projection; link decisions; profile package loader; read-only meaning search; declared-lives recognition gate; sorter apply/undo stack.

**Open (architecture, not UI):** typing_state projection from recognition; minting course/project items from profile answers; inferred connector; full nudge/assistant modules; live mail/calendar ingester; turning apply off for a “never move” product mode; correction memory that generalizes (explicitly out of the thin link plan); researched non-student profile packages.

---

## 8. How to extend safely

1. New context-graph behaviour → new module under `src/items/` (or profile JSON). Add a kill test if it touches disk organization.
2. New sorter behaviour → `mutation` / `apply_run` / placement / tree_design. Do not teach `items` to call it.
3. Shared need (e.g. “open this path”) → read `open_target` / `current_path`; do not route through apply.
4. New edge type → closed vocabulary in the item plan + profile allow-list; never promote a grouping-only edge without an explicit stage and evidence rule.

Enforcement for kill rule 1: `tests/items/test_mutation_boundary.py`.

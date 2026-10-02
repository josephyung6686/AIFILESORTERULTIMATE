# Never-move product mode (owner ruling)

Date: 2026-10-02.  
Status: **binding** for the context-graph path.  
Authority: [`docs/product-one-pager.md`](product-one-pager.md) (“Files never move on disk”) and [`docs/architecture-map.md`](architecture-map.md).

## Ruling

1. **Context-graph commands never move, rename, copy, or delete user files.**  
   Verbs: `sync`, `view`, `suggest`, `search`, and any future graph verb under `src/items/`.  
   `suggest --apply` stays refused.

2. **The sorter apply stack remains available** as a separate path (`--freeze`, `--apply BRANCH`, `--undo-everything` via `apply_run` / `mutation`). It is not deleted by this ruling.

3. **Composition root may call both.** `src/items/**` must not import `mutation` or `apply_run` (enforced by `tests/items/test_mutation_boundary.py`).

4. **Default product messaging** for the graph path is leave-in-place: opening an item uses `open_target` / the original path. No graph view button may share a control with sorter apply.

5. **Turning sorter apply off entirely** (shipping only the graph product) is a later owner decision. Until then, both paths coexist with a hard package boundary.

## Not decided here

- Agent one-sentence pitch (still placeholder on the one-pager).
- Release order of the five views.
- Which non-student profile is researched next beyond the `job_seeker` stub package.

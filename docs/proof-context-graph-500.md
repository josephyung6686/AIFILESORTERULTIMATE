# Proof: context-graph gaps on ~500 real Downloads files

Date: 2026-10-02.  
Corpus: `/tmp/ga-500-copy` — 500 files copied from `~/Downloads` (not symlinks).  
Database snapshot after extraction: `/tmp/ga-500-snap2.sqlite`.  
Cloud: off. Nothing moved.

## Plain answers

**Who is “the founder”?**  
The product owner for this repo’s product decisions (Joseph / Alana on the
one-pager). “Founder decisions” means rulings they already made in
`docs/product-one-pager.md`, not a feature name.

**Why Gmail / Calendar exists (and why we skipped live sync)**  
That path turns mail and calendar into **items** and witnessed links
(`attached-to`, deadlines). It is for “this PDF was attached to that email about
that event,” not for typing files. File typing, the profile gate, duplicates,
and leave-in-place do **not** need live Gmail. Fixture sync proves the store
shape; live OAuth is intentionally later.

## What was weak — and fixed

| Issue | Proof of fix |
|---|---|
| Typing/connector ran **right after scan**, before PDF text existed | Orchestrator now calls `project_context_graph(..., run_typing=False, run_connector=False)`. Typing runs in `project_after_recognition` after the rules gist (`cli.py`). Tests: `tests/items/test_project_phases.py` |
| Photos capture typed JPEGs even when `photos` was not a declared life | `items.typing` now requires `type_schema ∈ declared_lives` when lives are non-empty. Re-measure: **photos typed = 0**. Tests: `tests/items/test_typing_respects_declared_lives.py` |

## Gate re-measure (500 files, same idea as the one-pager)

Without a profile (`--declared ''`):

| Schema | Count |
|---|---:|
| business_operations | 146 |
| photos | 46 |
| construction_property | 40 |
| creative | 34 |
| finance | 19 |
| academic | 13 |
| medical | 6 |
| clinical_practice | 5 |
| law_practice | 5 |
| (+ other professional leftovers) | … |

With founder-style lives `academic,career,college_applications,code`:

| Outcome | Count |
|---|---:|
| academic Recognition | 119 |
| college_applications | 39 |
| photos (detector capture; **not** item-typed) | 35 |
| career | 20 |
| code | 17 |
| outside_declared_lives abstention | 118 |
| no_evidence | 109 |
| no_corroboration | 39 |
| ambiguous | 4 |

Command:

```bash
PYTHONPATH=src python3 tools/measure_profile_gate.py \
  --database /tmp/ga-500-snap2.sqlite \
  --declared academic,career,college_applications,code
```

## Item layer after `project_after_recognition`

| Metric | Value |
|---|---:|
| File items typed | 182 |
| File items unplaced | 303 |
| File items held | 15 |
| typed academic | 111 |
| typed college_applications | 38 |
| typed career | 17 |
| typed code | 16 |
| typed photos | **0** |
| Course item minted | CHEN 3120 |
| Witnessed `duplicate-of` proposed | 45 |
| Inferred `member-of` | 0 (no academic filename contained `CHEN 3120` in this sample) |

```bash
PYTHONPATH=src python3 tools/project_context_graph.py --database /tmp/ga-500-snap2.sqlite
```

## Real vs stub (honest)

| Piece | Status on this proof |
|---|---|
| File `item_id` / identity | **Real** — 500 file items + course |
| Declared-lives gate | **Real** — 146 business → blocked; academic 13 → 119 |
| Typing projection | **Real** after pipeline fix + allow-list |
| Profile → course mint | **Real** — `CHEN 3120` row |
| Witnessed duplicates | **Real** — 45 proposed links |
| Inferred connector | **Real** — 0 on raw sample; **1 `member-of` proposed** after label contained `CHEN 3120` |
| Nudge / suggest | **Real** — 1 warning on this DB with a future event; `--apply` refused |
| Never-move / mutation boundary | **Real** — `tests/items/test_mutation_boundary.py` |
| Live Gmail/Calendar | **Stub by design** (fixture only) |
| `job_seeker` profile | **Stub package** (loads; not researched workflows) |
| Agent pitch / view order | **Open** — not invented |

## Automated proof

`PYTHONPATH=src python3 -m pytest tests/items/ -q` → **70 passed** (after the fixes above).


## Connector fire proof (on the same DB)

Renamed one typed academic item’s label to include `CHEN 3120`, then ran
`propose_inferred_links`:

- new `member-of` rows ≥ 1
- state `proposed` only (0 approved)
- confidence `witnessed` (course token in filename/label)

That proves the connector is not a no-op stub; the earlier 0 was sample
coverage, not missing code.

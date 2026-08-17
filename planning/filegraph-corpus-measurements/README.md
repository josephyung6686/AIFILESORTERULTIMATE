# FileGraph corpus measurements

These scripts produced the numbers in
[`../02-filegraph-engine-how-extractors-templates-and-scoring-work.md`](../02-filegraph-engine-how-extractors-templates-and-scoring-work.md).
They are **experiments on a real Downloads/Desktop corpus**, not the product.

They often hard-code paths like `~/Desktop` and `~/Downloads` on the machine they were run on.
They are evidence, not something to ship.

| Script | What it measured |
|---|---|
| `recommend.py` / `recommend2.py` | How many loose files existing folders would absorb vs how many need new structure |
| `template_fit.py` | Which hand-written templates fire on this corpus |
| `extract_test.py` / `full_vs_peek.py` | Cost of reading whole PDFs/DOCX vs first-page peeks |
| `fact_edges.py` | Provable relationships (duplicates, versions, course codes, …) |
| `graph_value.py` | Whether a folder graph beats a file graph |
| `speed_test.py` | Runtime of extraction / OCR-related work |
| `static_test.py` | Static embeddings vs richer signals |
| `surface_test.py` / `surface_test2.py` | What to show the user first |
| `slot_test.py` / `slot_test2.py` | Filling template slots with corpus values |
| `role_test.py` | Role / purpose vs topic |
| `prop_test.py` | Facet / label propagation |
| `combined_test.py` / `real_test.py` | Combined or on-disk checks |

Start with the two planning markdown files, not these scripts, unless you are verifying a number.

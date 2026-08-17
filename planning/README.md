# Planning docs — start here

This folder is the shared plan for the **database agent** (working name; historically FileGraph).
Alana and Joseph edit these while the plan is still open. There is **no application code** in
this GitHub repo until the plan is locked.

| File | What it is | Who should read it |
|---|---|---|
| [`01-product-contract-what-we-are-building.md`](01-product-contract-what-we-are-building.md) | Short **product contract**: locked decisions, user flow, build order, what is in vs later | Both of you, first |
| [`02-filegraph-engine-how-extractors-templates-and-scoring-work.md`](02-filegraph-engine-how-extractors-templates-and-scoring-work.md) | Long **engine design**: knowledge graph, PDF/EXIF/OCR, templates, scoring, clustering, privacy — with measurements | Joseph’s original write-up; use when you need the how and why |
| [`filegraph-corpus-measurements/`](filegraph-corpus-measurements/) | Python **measurement scripts** that produced the numbers in the engine design (not the app) | Anyone checking a claim in file 02 |

If the two markdown files disagree on something the user sees (freeze, where a file may land,
name collisions, cloud consent), **file 01 wins** until you change it. File 02 wins on extractor
and graph mechanics.

Repo root [`README.md`](../README.md) points here.

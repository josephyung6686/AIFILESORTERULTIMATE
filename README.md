# Database agent — planning repo

Shared plan for Alana and Joseph. **Start in [`planning/`](planning/README.md).**

A local file intelligence system. The core is a **knowledge graph of your files** (people,
courses, events, same session). You freeze a folder tree; only then does anything move, and
only onto those nodes.

The canvas is a functional freeze view, not the product. Build order is fitness scorer, then
extraction, then classify.

**Status:** still being edited. This GitHub repo is **planning docs only**. No application
code until the plan is locked.

| Start with | What it is |
|---|---|
| [`planning/01-product-contract-what-we-are-building.md`](planning/01-product-contract-what-we-are-building.md) | Short contract: locked decisions and user flow |
| [`planning/02-filegraph-engine-how-extractors-templates-and-scoring-work.md`](planning/02-filegraph-engine-how-extractors-templates-and-scoring-work.md) | Long engine design (graph, extractors, templates, scoring) |
| [`planning/filegraph-corpus-measurements/`](planning/filegraph-corpus-measurements/) | Scripts behind the numbers in the engine design |

---

## Loop (what you see)

```text
1. PICK        sources + destination roots (no silent Desktop/Documents default)
2. PROFILE     optional role card — skip allowed
3. EXTRACT     whole files → fact graph (PDF/DOCX, EXIF, OCR, HEIC)
4. TEMPLATES   hand-written schemas fitted to this corpus; you split each node
5. CANVAS      functional tree — freeze the only legal destinations
6. CLASSIFY    mean+max vs folder members (filename Counter is the baseline)
7. APPLY       plan → confirm → move; name clash becomes file (1).ext; undo
```

---

## Locked in the product contract

- Knowledge graph of files; disk layout is a projection; graph decides ~90%, model the rest
- Whole-file extraction: PDF/DOCX, EXIF, Apple Vision OCR, screenshots, HEIC
- Embeddings, GLiNER, Leiden, mutual-kNN, hub exclusion; daemon only if measured
- Fitness scorer first; canvas is functional freeze, not polish
- Mean+max similarity to folder members; filename Counter is the baseline
- Name clash → `file (1).ext`, never overwrite
- Hand-written templates, per-node split-by, Wall-Picture, Aho-Corasick gazetteers
- Cloud allowed only after you see the exact text; ID/medical/tax/legal/keys stay local
- Project-skip on destinations; unmatched stay put; cross-root file into a chosen root

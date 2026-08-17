# Database agent

A local file intelligence system. The core is a **knowledge graph of your files** (people,
courses, events, same session). You freeze a folder tree; only then does anything move, and
only onto those nodes.

The canvas is a functional freeze view, not the product. Build order is fitness scorer, then
extraction, then classify.

**Product spec (canonical):** [`docs/superpowers/specs/2026-08-17-database-agent-design.md`](docs/superpowers/specs/2026-08-17-database-agent-design.md)

**Status:** spec v2.1 — still being edited with Joseph. This repo is **planning specs
only**. No application code until the plan is locked.

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

## In the contract (FileGraph design)

Detail lives in
[`docs/superpowers/specs/2026-08-16-filegraph-design.md`](docs/superpowers/specs/2026-08-16-filegraph-design.md).
Locked in the product spec:

- Knowledge graph of files; disk layout is a projection; graph decides ~90%, model the rest
- Whole-file extraction: PDF/DOCX, EXIF, Apple Vision OCR, screenshots, HEIC
- Embeddings, GLiNER, Leiden, mutual-kNN, hub exclusion; daemon only if measured
- Fitness scorer first; canvas is functional freeze, not polish
- Mean+max similarity to folder members; filename Counter is the baseline
- Name clash → `file (1).ext`, never overwrite
- Hand-written templates, per-node split-by, Wall-Picture, Aho-Corasick gazetteers
- Cloud allowed only after you see the exact text; ID/medical/tax/legal/keys stay local
- Project-skip on destinations; unmatched stay put; cross-root file into a chosen root

---

## Repository

```text
docs/superpowers/specs/2026-08-17-database-agent-design.md   product contract
docs/superpowers/specs/2026-08-16-filegraph-design.md        graph / extractors / templates
research/                                                    measurement scripts behind the FileGraph spec
README.md                                                    points here
```

Application code stays off this remote until the plan is locked.

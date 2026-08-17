# Database agent

A local file intelligence system. The core is a **knowledge graph of your files** (people,
courses, events, same session). You freeze a folder tree; only then does anything move, and
only onto those nodes.

The canvas is a functional freeze view, not the product. Build order is fitness scorer, then
extraction, then classify.

**Product spec (canonical):** [`docs/superpowers/specs/2026-08-17-database-agent-design.md`](docs/superpowers/specs/2026-08-17-database-agent-design.md)

**Status:** spec v2.1 — graph, extraction, templates, mean+max scoring, and cloud-consent are
in the contract. What exists in code today is the filename `Counter` baseline and hold-out
harness.

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

## Engine

```text
database_agent/nodes.py       index, project-skip, content profiles, sync/TCC flags
database_agent/classify.py    score onto frozen nodes, abstain, missing-folder proposals
database_agent/evaluate.py    held-out precision/coverage on already-filed files
```

Already-organised folders are a labelled dataset. Hold a filed file out, rebuild profiles
without it, see if the classifier puts it back. That is the number the UI should show:

> I'd place 6 in 10 of your loose files, and on your own filed data I get 97% of those right.

On the synthetic fixture the harness reports **100% held-out precision at 62% coverage**.

```bash
python -m pytest tests/
python -m database_agent.evaluate
```

Python 3.11+. `pip install -e ".[dev]"` (or `uv pip install pytest`) for tests.

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
database_agent/                                              filename baseline + hold-out
tests/                                                       baseline tests
research/                                                    measurement scripts
```

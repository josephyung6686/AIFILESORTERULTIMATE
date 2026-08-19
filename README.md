# Database agent — planning repo

Shared plan for Alana and Joseph. **The design is
[`planning/00-database-agent-product-design.md`](planning/00-database-agent-product-design.md).**

A local file intelligence system. The filesystem stays the system of record; a local SQLite
database is the durable working memory. Evidence is extracted once per file version and reused by
every later stage. Rules establish precision, the graph assembles context, the LLM interprets only
bounded evidence dossiers, and a deterministic validator checks every cited conclusion. The user
freezes a destination tree, and after freeze nothing may invent a destination outside it.

**Status:** the design doc is the guide for implementation. No application code in this repo yet.

---

## The document

It is numbered so implementation can proceed part by part — a phase names the section it
implements (`§2.7 OCR`, `§6.10 the two-condition rule`) and that section is its acceptance
contract.

| § | What it covers |
|---|---|
| 0 | Foundations — filesystem as system of record, SQLite as working memory |
| 1 | Corpus and root selection, exclusions, the reusable extraction pass |
| 2 | Content extraction and evidence creation — PDF, DOCX, archives, images, OCR, format coverage |
| 3 | Facts, facets, and hybrid intelligence — observations vs. facts, reliability states, core tables |
| 4 | Grouping — seeds, bounded neighbourhoods, the group dossier, stop rules |
| 5 | User selection for the folder tree — horizontal pass, templates, uneven depth, freeze |
| 6 | Group-aware classification against the frozen tree — destination profiles, node-local graphs |
| 7 | Residual files — the controlled miscellaneous library and final review |
| 8 | Trust, operations, lifecycle — provenance, mutation safety, privacy, replay, budgets, plan versions |

---

## Loop (what the user sees)

```text
1. PICK        sources + destination roots; exclusions applied first
2. EXTRACT     one reusable pass per file version → evidence in SQLite
3. FACTS       observations become structured claims, each with evidence and reliability state
4. GROUP       rules anchor, graph assembles context, LLM judges coherence, validator checks
5. TREE        design branches horizontally then vertically; freeze the only legal destinations
6. CLASSIFY    retrieve legal nodes, build a node-local graph, place or abstain
7. RESIDUAL    surface what did not fit; user decides per set before any AI review
8. APPLY       plan → verify preconditions → move → verify → conditional undo
```

---

## Standing constraints

- Evidence is extracted once per content version and reused; never re-read a file per template
- Raw observations are kept separately from normalized values
- The LLM may only propose fields in the active schema, and must cite evidence or return `unknown`
- Every LLM conclusion passes a deterministic validator before it becomes active
- Word-boundary matching, positional weighting, ranked candidates with a minimum margin
- Purpose is a first-class facet, distinct from topic; authorship is metadata, not a destination
- No fuzzy date parsing
- After freeze: no invented destinations, no silent override of a direct fact
- Two-condition acceptance — minimum support **and** a margin over the next-best destination
- Correct abstention is a successful outcome
- Never overwrite on collision; undo is conditional; sensitive material stays local by default

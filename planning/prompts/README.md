# Research dispatch pack — catalogues of the world

These prompts are for **research agents**, not for planning or implementation agents.
Each one is self-contained below its `---` line. Paste that block into a new session.

**Do not send these agents at:** D6 (field spelling / `subject` vs `course`), D2 first half (which record is authoritative), I6 (delete vs append-only), install default (`offline` vs `local_model`), "what is a corpus area", W1 ratification. Those are one-sentence decisions for Joseph.

## Dispatch order

```text
R0   connection architecture     FIRST — how 00's objects join (schema/template/group/residual)
R1a  schemas + template roster   one agent — few schemas, ~200–300 templates, canonical fields
R1b  per-row research            ONE AGENT PER ROSTER ROW — files, observations vs facts
R1c  merge + fact-check          one agent — field reuse, reciprocity, SOURCE_TYPES
R2   sensitivity detector        after R0
R3   residual library            nine 00 names, not the 200–300
R4   gazetteers                  after R0 names gazetteer-backed fields
R5   jurisdiction values         after R0 + D4
R6   academic/capture patterns   after R0
```

**R1b is the hundred-agent fire**, stamped on **templates** (plus a handful of schema rows). Same prompt, different ASSIGNMENT. How: [`01-DISPATCH.md`](01-DISPATCH.md).

**Read [`ALIGNMENT.md`](ALIGNMENT.md) before dispatching.** Joseph's "500+ connected subdomains" lands as the template library and folder-dimension depth, not as 500 schemas. `00` forbids prematurely hand-authoring hundreds of specialized schemas.

If R0 is not finished, R1a still follows ALIGNMENT.md. R1b must not invent a third object type.

## Shared rules (every prompt already repeats these; this is the short form)

- Source of truth: `planning/00-database-agent-product-design.md`. `01` is the numbered rendering; `00` wins.
- Never fabricate a quotation. No quote marks unless the span is in `00`.
- No numeric thresholds, no handling classes (`public_low` etc.), no `src/` edits, no SPEC edits unless the prompt says so.
- Data is **injected**, never imported as a module-level constant in `src/extractors/` or `src/facts/`.
- Provenance: `design` | `inference` | `proposal`.
- Open Joseph questions stay in `NEEDS-JOSEPH`; do not close them.

## Files

| # | Prompt | Writes |
|---|---|---|
| R0 | [`00-catalogue-connection-architecture.md`](00-catalogue-connection-architecture.md) | `planning/domains/CONNECTION.md` |
| align | [`ALIGNMENT.md`](ALIGNMENT.md) | how 500+ / `00` / the swarm land |
| R1 | [`01-domain-taxonomy-research.md`](01-domain-taxonomy-research.md) | pipeline overview (do not paste into a swarm agent) |
| R1a | [`01a-spine-roster.md`](01a-spine-roster.md) | `roster.json` + `canonical_fields.json` |
| R1b | [`01b-per-domain-research.md`](01b-per-domain-research.md) | **one** `planning/domains/nodes/<id>.json` |
| R1c | [`01c-merge-and-gate.md`](01c-merge-and-gate.md) | `FOREST-REPORT.md` + `check.py` |
| how | [`01-DISPATCH.md`](01-DISPATCH.md) | stamp R1b onto every roster row |
| R2 | [`02-sensitivity-detector.md`](02-sensitivity-detector.md) | `planning/deferred-catalogues/08-sensitivity-detector/` |
| R3 | [`03-residual-library.md`](03-residual-library.md) | `planning/deferred-catalogues/09-residual-library/` |
| R4 | [`04-gazetteers.md`](04-gazetteers.md) | `planning/deferred-catalogues/10-gazetteers/` |
| R5 | [`05-jurisdiction-values.md`](05-jurisdiction-values.md) | `planning/deferred-catalogues/11-jurisdiction-values/` |
| R6 | [`06-academic-capture-patterns.md`](06-academic-capture-patterns.md) | `planning/deferred-catalogues/12-academic-capture-patterns/` |

Audit of the current 574: [`../25-domains-verification.md`](../25-domains-verification.md).

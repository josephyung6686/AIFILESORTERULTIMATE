# Segmentation map — the thirteen parts

Date: 2026-08-19
Status: **structure contract** — how the project is cut, ordered, and connected
Design: [`01-product-design-structured.md`](01-product-design-structured.md) · source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

This document decides **how the work is divided**, not how any part is built. Each part owns a
slice of the design and publishes exactly one contract. A part can be built and tested while its
neighbours do not exist, because it is written against its neighbours' contracts and fixtures.

Nothing here overrides the design. Where this document and the design disagree, the design wins.

---

## Build shape

Three stages, in this order:

1. **Freeze the contracts.** All thirteen `SPEC.md` files written and reviewed together as one pass,
   before any implementation. A contract mismatch found by reading costs an afternoon; found at
   P11 it invalidates work in nine finished parts.
2. **Walking skeleton.** One thin deterministic path through all thirteen seams — minimum viable at
   every step, no LLM, no cloud. Its only job is to prove the contracts actually connect.
3. **Full depth, part by part.** Every part built out completely and perfected one at a time,
   against contracts that the skeleton has already exercised.

The skeleton is not a prototype to throw away. It is the first passing test of the seam layout,
and it stays in the repository as the integration test every later part must keep green.

---

## Why thirteen parts and not nine sections

The design's sections describe what the system believes. Build parts must be independently
buildable. Those are the same cut everywhere except four places:

| Design | Why it is not a build unit as written |
|---|---|
| **§2** Extraction | Six formats sharing one observation shape (§2.8). Written before the shape is frozen, six extractors invent six shapes and every downstream consumer grows per-format branches — exactly what §2.8 exists to prevent. |
| **§8** Trust and operations | Presented as a layer over everything, but §8.2 provenance is a schema decision, §8.4 requires privacy enforced *before content reaches any model*, and §8.5 requires evaluation *decomposed by stage*. A layer added last cannot satisfy any of the three. |
| The LLM mechanism | §3.6, §4.5+§4.8, §6.6+§6.10 and §7.7+§7.9 describe one mechanism — bounded dossier, cited response, deterministic validator, accept/reject/abstain. Implemented four times it drifts four ways, and §8.5's per-stage grounding metric becomes four different measurements. |
| The review surface | §6.11, §7.5–§7.6, §7.10, §8.3 and §5.2/§5.9/§5.11 all assume a surface that presents decisions and collects user choices. No §-section owns it, so an initial twelve-part cut left §8.3's `Required review policy` with no consumer — a plan could be marked review-required with nothing able to review it. P13 (S4). |

---

## The parts

| # | Part | Owns | Publishes |
|---|---|---|---|
| P1 | Storage, identity, provenance | §0, §8.2 | `files` + append-only `events`; content-hash identity; supersede-never-overwrite |
| P2 | Eval and replay harness | §8.5 | replay bundle format; per-stage assertions; shadow mode |
| P3 | Scan and corpus selection | §1.1, §1.2 | populated `files`; exclusion rules; stat-cache semantics |
| P4 | Evidence shape | §2.8 | **the observation record** — the one shape every extractor emits |
| P5 | Extractors (×6) | §2.1–2.7, §2.9 | conforming observations per format |
| P6 | Facts and facets | §3.1–3.14 | `fields` / `values` / `file_facts`; six reliability states |
| P7 | Privacy and consent gate | §8.4 | handling classes; four operation modes; consent-aware audit record |
| P8 | LLM harness and validator | §3.3, §3.6, §4.8, §6.10, §7.9 | dossier → cited response → validation verdict |
| P9 | Grouping | §4 | accepted groups; direct-anchor vs context-supported membership |
| P10 | Tree design and freeze | §5 | **the frozen tree** — node types and destination profiles |
| P11 | Placement and residual | §6, §7 | one placement-decision record |
| P12 | Apply and undo | §8.3 | the mutation transaction; conditional undo |
| P13 | Review and approval surface | §6.11, §7.5–§7.6, §7.10, §8.3–§8.6 (presentation) | `review_action`, `review_approval`, `progress_line` |

### Two groupings that are not one-to-one with the design

**P4 is split out of §2.** The observation record is a contract, not an extractor. It is frozen
once and then six extractors are written against it. §2.8 is explicit that downstream logic must
not need separate handling per format; that property is only achievable if the shape precedes the
extractors.

**P11 fuses §6 and §7.** §7.9 requires that when residual review finds a credible connection, the
file is handed *back* to the §6 placement engine rather than trapped in a residual folder. That is
a loop, not a hand-off. Both stages must also emit the same decision record so the user reviews one
surface, not two. Split into separate parts, this becomes two engines and two review interfaces.

---

## Cross-cutting constraints

These have no standalone deliverable and are not parts. Every `SPEC.md` must answer all four.

| Constraint | Design | What each spec must state |
|---|---|---|
| Provenance | §8.2 | which events this part appends, and what it never overwrites |
| Budgets and degradation | §8.6 | its ceilings, and what it does when the budget is exhausted — never lower-quality automatic classification |
| Correction learning | §8.7 | which user actions it records, and at what scope (file / group / node / template / domain / corpus) |
| Plan versioning | §8.8 | what of its state belongs to a plan version rather than the shared evidence database |

---

## Order

```
Wave 1  substrate          P1 → P2 → P3
Wave 2  understanding      P4 → P5 → P6          (deterministic only, no model)
Wave 3  the model enters   P7 → P8
Wave 4  structure          P9 → P10
Wave 5  placement          P11 → P12 → P13
```

**Acknowledged back-edges (M10).** Three dependencies run against wave order and are mediated by
fixtures rather than re-ordered: **P5 → P7** (audio/video transcription is authorized only by §8.4's
privacy-and-compute policy), and **P8 → P10, P8 → P11** (node-existence oracle and placement-dossier
contents). The fourth, P10 → P11, was removed structurally: the residual-library *definitions*
(§7.2–§7.4) moved to P10, leaving P11 the residual *workflow* (§7.5–§7.11).

**Graph the connectors (standing rule).** From P1 onward the repository carries a graphify graph, so
seam questions are answered by query rather than by reading every spec. `graphify hook install` once,
`graphify update .` after each part lands, `graphify watch .` during active work on a part — never
`graphify watch ./src`, which writes a phantom graph and leaves the real one stale. Before starting
part N, run `graphify path "<the record part N-1 publishes>" "<the consumer in part N>"` and confirm
the connector exists before writing code against it. This session found P4 and P5 had published
incompatible vocabularies only because an agent read 6,000 lines; at code scale that stops working.

P5's six extractors are mutually independent and can be built in parallel once P4 is frozen.

### Three deviations from section order, each forced by the design

- **P2 before the stages it measures.** §8.5 requires evaluation decomposed by stage, so the harness
  must exist before there are stages to instrument. Retrofitting per-stage measurement means
  rewriting every stage's boundaries.
- **P7 before P8.** §8.4: *"Privacy policy must be enforced before content reaches any model or
  external connector."* If the gate arrives after the harness, the first cloud call has already
  shipped an unclassified document.
- **P4 before P5.** §2.8, as above.

---

## The walking skeleton

One file, one deterministic path, every seam touched. No LLM, no cloud, no embeddings — which also
means no privacy gate is exercised, because nothing leaves the machine.

```text
input   one PDF whose title carries a course code

P1      hash it, create the file record, append a discovery event
P3      scan a fixture directory; assert the exclusion rules skip node_modules
P4/P5   extract page-one text; emit ONE observation in the frozen shape
P6      resolve it to ONE validated fact (course = X) with its evidence link
P8      not exercised — the fact is rule-validated, no model needed
P9      form a group of one, from a direct anchor
P10     a hand-authored TWO-node tree; freeze it (two nodes so the §6.10 margin
        condition is exercised, not bypassed — with one candidate it is vacuous)
P11     exact fact match to that node; emit a placement decision
P12     plan → verify preconditions → move → verify hash → undo → verify restored
P2      the whole run replays from a bundle and asserts each stage's output
```

**What it proves:** every table exists and connects, the observation shape survives a real
extractor, a fact carries its evidence, freeze actually constrains placement, the two-condition
rule is genuinely evaluated rather than vacuously satisfied, and a move is reversible with
verification. **What it deliberately does not prove:** anything about model
behaviour, grouping quality, or template design — those need depth, not a skeleton.

**Second fixture path** (ops runtime, still no live model): a dossier that requires sensitive text;
`Gate.release` returns `NeedsConsent`; P13 presents the four §8.4 options; choosing `no_model_use`
does not become `abstain` inside P8. This is the B2 contract test the first path cannot exercise.

---

## Layout

```text
planning/
├── 00-database-agent-product-design.md    source of truth — Joseph's wording is authoritative
├── 01-product-design-structured.md        the same content, §0–§8
├── 02-segmentation-map.md                 this file
├── 03–09                                  contract reviews and audits
├── 10-i4-learning-ops.md                  binding: analysis tiers + learning reads
├── 11-ops-runtime.md                      how the product runs on a Mac (not a part)
└── parts/
    └── P<n>-<name>/
        ├── SPEC.md      design slice owned · contract in · contract out · done-means ·
        │                the four cross-cutting answers
        └── PLAN.md      implementation plan — written per part, when that part comes up
```

`SPEC.md` is what makes independent construction real: it must state the contract precisely enough
that a neighbouring part can be built against fixtures before this one exists. If a spec cannot be
used that way, it is not finished.

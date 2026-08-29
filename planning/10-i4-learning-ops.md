# Resolutions — I4, learning reads, ops runtime

Date: 2026-08-19
Status: **binding** — implementers apply these verbatim; they do not re-adjudicate
Resolves: [`09-plan-spec-critique.md`](09-plan-spec-critique.md) findings **I4**, **"nobody reads the learning store"**, and the nine product-ops gaps
Against: [`01-product-design-structured.md`](01-product-design-structured.md) and [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

The ops rules themselves live in [`11-ops-runtime.md`](11-ops-runtime.md). This document is the contract-layer decisions those rules and the SPEC edits depend on.

**Decision criterion** (same as [`04-resolutions.md`](04-resolutions.md)): correctness of the application. Where two readings are defensible, the one that preserves more information, or that makes a wrong outcome impossible rather than merely unlikely, wins.

These three do not invent mechanisms. I4 names processes the design already distinguishes. The learning read path was already promised in P1 ("every other consumer reads the store for its own scope") and in P9 ("this store is what §4.9 SR6 queries") and never wired. The ops contract assigns runtime behaviour the design assumes and no part owned.

---

## I4 — analysis tiers

**P5 publishes a closed four-value vocabulary. Every cache key, run row, file-record status map, and replay tuple draws from it.** **Ratified 2026-08-19** — the four names below are settled and are not reopened; they are the same class of decision as I1 and I2.

§3.4 requires `analysis tier` on the cache key and never lists the values. §8.2 requires the file record to retain "Extraction status by extractor tier" and never lists the tiers. Inventing a depth scale (tier 1/2/3) would be authorship. The design already distinguishes four *processes* that must not collide in the cache:

| `analysis_tier` | The process §3.4 must not confuse with another | Named by |
|---|---|---|
| `filesystem` | Basic filesystem extraction — path, filename, size, timestamps, hash, parent-folder context | §1.2, §2.9 |
| `native` | Format-native content extraction — PDF text layer, DOCX, EXIF, archive manifest, structured text, and every §2.9 family except OCR | §2.2–§2.6, §2.9 |
| `ocr` | OCR, including targeted OCR on a broken text layer | §2.7, §2.2 |
| `llm` | Model-derived results — the cache key's "model identifier when relevant, and prompt fingerprint for model-derived results" | §3.3, §3.4 |

Why four, not the §8.6 degradation ladder (P6 OQ1's alternative). The ladder is an *order of work* (rules → extraction/OCR → graph → LLM). A cache key is an identity of a *result*. OCR and native extraction both sit in the ladder's second rung and must not share a cache slot: a PDF can have a complete native run and a capped OCR run on the same content hash. Graph retrieval is not an extraction result and does not belong here.

**`source_type` is not the tier.** P4's observation `source_type` says where a value was read (heading, EXIF field, OCR region). `analysis_tier` says which process produced the *run*. An OCR run is `tier = ocr`; its observations may still have `source_type = ocr`. A native PDF run is `tier = native` even when a heading observation looks similar to an OCR heading.

Changes:

- **P5** owns the vocabulary (03 already assigned I4 to P5). Each extractor family declares exactly one tier: filesystem observations that P5 re-emits as `source_type: filesystem` are `filesystem`; E1–E5 are `native`; E6 is `ocr`. P5 writes `extraction_status_by_tier` as a map from the four keys to P4 `completeness` (a missing key means that tier was not attempted).
- **P4** replaces `run.tier: "<see Open questions>"` with `analysis_tier ∈ filesystem \| native \| ocr \| llm`. Conformance: a value outside the four is rejected. P8 is the only writer of `llm` runs — P4 accepts the value; P5 never emits it.
- **P6** and **P8** form §3.4's cache key with this field. P8's model-derived facts and verdicts carry `analysis_tier = llm`.
- **P1** continues to store `extraction_status_by_tier` opaquely. The keys of that map are now known to be these four; P1 still does not interpret the completeness values.
- **P2** `version_tuple.analysis_tier` becomes `analysis_tiers_enabled[]` — a subset of the four — so a walking-skeleton run can declare `{filesystem, native}` and an OCR-on replay is a different tuple. A singular field cannot express "native on, OCR off."
- **P3** OQ4 is answered in part: `scan_state` (P3), `extraction_status_by_tier` (P5 via P1), and `completeness` (P4, per run) are three fields, not one. Scan state is not a tier.

P4 OQ1, P5 OQ3, P6 OQ1 (the seam half) close as settled by this document.

---

## Learning store — query before propose

**P1 remains the store. P13 remains the inspect/reset surface. P6, P7, P8, P9, P10 and P11 become the readers that §8.7 actually requires.**

The design's failure mode is literal: without stored negative feedback the system "will repeatedly resurface the same attractive but incorrect grouping." P1 already publishes `learning_records(scope, subject_id)`. P9 already says SR6 queries that store. P8 already refuses an equivalent dossier with `USER_REJECTED_EQUIVALENT`. None of those calls exist in any Contract-in.

Acceptance is per plan version (M15). Negative feedback must **not** be: a rejection in plan v2 has to stop the same proposal in v3. That is why the store is a versionless projection over `events`, and why SR6 cannot be implemented as a read of current-version `group_acceptance` alone.

### Equivalence (closes P8 Q5 and P9 OQ7)

Too narrow (same dossier bytes) and a trivial dossier edit resurfaces the rejection. Too broad (any overlapping files) and a genuinely new proposal is suppressed. The design's own unit of a proposal is the *claim*, stored with the evidence that produced it (§8.7).

Two proposals are equivalent when they share `proposal_class` and `basis_key`:

| `proposal_class` | `basis_key` | Why this and not the alternatives | Author |
|---|---|---|---|
| `fact` | `(file_id, field, value_id)` | Same claim about the same file. A different value is a different proposal. | P6 |
| `group` | sorted `anchor_facts[]` (the grouping *basis*, not the member set) | §4.9 SR6 is about the same attractive grouping. Adding a sparse member must not mint a new group that escapes the rejection. A different label on the same anchors is still the same grouping — labels are display. | P9 |
| `membership` | `(group_id, file_id)` | Excluding one transcript from a Columbia packet is file-within-group (§8.7's worked case). It must not suppress the group, and must not teach that all transcripts are excluded. | P9 |
| `branch` | `(parent_node_id, dimension_or_label)` | Rejecting a proposed branch under Academics is a node-scoped correction, not a template ban. | P10 |
| `placement` | `(subject_id, node_id)` | Same file-or-group into the same frozen node. A different node is a different proposal. | P11 |
| `residual` | `(file_id, residual_node_id)` | Same file into the same residual destination. §7.10's school-forms-out-of-Receipts case. | P11 |
| `privacy` | `(file_id, handling_class)` | Reclassifying a file as private is a file-scoped correction; it does not raise a corpus floor unless the user repeats it at corpus scope (P7 OQ7 stays open for generalization, not for the exact replay). | P7 |

Member-set, dossier hash, and display label are **not** in any `basis_key`. Scope remains exact: a `file`-scoped record is never returned by a `corpus`-scoped read (already P1's rule).

The acting part supplies `polarity`, `proposal_class` and `basis_key` on the user-action event it authors. P1 stores all three opaquely and returns them from `learning_records`. P1 still weights and generalizes nothing.

**`polarity ∈ accept | reject`** is the third required field and is not cosmetic. Every rule below turns on finding an *unreset reject*; §8.7 requires rejections be stored, and a reader that could not separate them from approvals on read would have to parse `explanation` free text to decide whether to suppress. It is supplied by the acting part, never inferred — P1 derives nothing from the event type.

### Query-before-propose (the missing read)

Before emitting a proposal of class C about subject S, the owning part calls `learning_records(scope, S)` and:

1. Ignores records at the wrong `proposal_class`.
2. Ignores records whose `basis_key` does not match.
3. Honours a later `reset_preferences` at that scope+subject (already P1: reset is an append that later reads honour).
4. On a record with `polarity = reject` that no later reset covers: does not emit the proposal. A `polarity = accept` record at the same `basis_key` is not a suppression and must not be read as one.

Enforcement by part:

| Part | When it queries | What suppression looks like |
|---|---|---|
| **P6** | Before writing a `file_facts` row that would revive a `rejected` claim | Leave the `rejected` row in place; do not propose the same `(field, value)` again |
| **P7** | Before assigning a handling class the user has already set or rejected at this scope | Do not re-prompt the same classification |
| **P8** | Before `Gate.release` at every call site | `abstain / USER_REJECTED_EQUIVALENT` — still no `NeedsConsent` mapping. Equivalence is `proposal_class + basis_key`, not dossier bytes |
| **P9** | Before surfacing a candidate group (SR6) and before proposing a membership | Group stays unsurfaced, or the member is not re-attached. Not a `supported` group |
| **P10** | Before proposing a branch candidate the user rejected | Candidate omitted from the canvas |
| **P11** | Before emitting `outcome = place` (or a residual equivalent) onto a node the user rejected for that subject | `abstain` with a distinct reason, or skip that node in retrieval — never auto-place |

P13 still does not learn. It renders `learning_records` as the inspect view and collects `reset_learning`.

**P2:** a replay bundle that exercises SR6 or `USER_REJECTED_EQUIVALENT` must carry the matching `bundle_learning_record[]` rows. Otherwise a run with the store populated and a run without it compare as a grouping-quality regression when the cause is a missing negative example. Dimension attribution stays with grouping / placement / factual_validation, not with a new stage.

Done-means (each owning part): a fixture with one unresected reject at the stated `basis_key` produces zero re-emissions of that proposal, including after a new plan version. A different `basis_key` at the same scope still emits. A reset at that scope+subject allows emission again.

---

## Ops runtime — not a fourteenth part

The nine product-ops gaps are not spec defects. They are runtime obligations the design assumes (local SQLite, Finder as system of record, cloud-synced directories, reversible journal, rebuild-from-filesystem) and no part owned.

They are specified in [`11-ops-runtime.md`](11-ops-runtime.md). Ownership summary:

| Gap | Owner | Why not a new part |
|---|---|---|
| Form factor, Full Disk Access, TCC | runtime contract; P13 is the process the user launches | Presentation, not a new seam |
| FSEvents during an open session | **P3** | P3 already authors `external modification detection` |
| iCloud dataless files | **P3** detects; **P12** refuses to hash-or-move until materialized. How a later run records it is **P4 OQ6**, left open | Scan and mutation, already those parts |
| Crash mid-apply | **P12** | The journal is already P12's |
| Concurrency | **P1** (one DB writer for apply); freeze exclusive in **P10** | Substrate + freeze |
| Database location and rebuild coverage | **P1** — closes OQ11 as far as location and what rebuild does *not* reconstruct | P1 already owns the database |
| Session | **P13** `session_id` grouping a sitting around P3's `scan_run` and P10's `plan_version` | Presentation grouping, not an eleventh §8.5 stage |

Nothing in `11` invents a numeric threshold, a template, or a gazetteer.

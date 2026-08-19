# Plan and spec critique

Date: 2026-08-19
Status: **do not freeze** — contracts are unusually strong; they are not freeze-ready
Scope: independent pass over the thirteen `parts/*/SPEC.md`, [`02-segmentation-map.md`](02-segmentation-map.md), the four prior review documents ([`03`](03-contract-review.md), [`06`](06-citation-audit.md), [`07`](07-fidelity-audit.md), [`08`](08-rereview.md)), and [`parts/P1-storage-identity-provenance/PLAN.md`](parts/P1-storage-identity-provenance/PLAN.md)
Source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

Prior reviews were treated as evidence, then re-checked against live spec text rather than trusted as current.

**Verdict:** Do not freeze. Do not treat [`08-rereview.md`](08-rereview.md) as current. Most of the original eight blockers are closed at both ends. What remains is a short list of identity decisions, one unreciprocated user-action seam, and a set of product-ops holes no prior review covered.

| Count | What |
|---|---|
| 13 | SPECs written |
| 1 | `PLAN.md` (P1 only) |
| 6 | Must decide before freeze |
| 9 | Product gaps never owned |

`08` is stale: `02` now has thirteen parts and a two-node skeleton, `stage_id` values are legal, `observation_key` landed in P7, and P12 consumes `review_approval`.

---

## Must decide before contracts freeze

These are not wording nits. Each one either blocks the walking skeleton, silently answers a still-open SPEC question in P1's PLAN, or lets a privacy `must` ship as an open question.

| ID | Finding | Why it is blocking | Where |
|---|---|---|---|
| **I1** | Identity model is still open in the SPEC and already implemented in the PLAN | P1 OQ1/OQ2 are the foreign-key question for every later part. PLAN Task 6 already chose: content change = new `files` row; same bytes at a new path = same `file_id` and one `current_path`. Two live duplicates therefore collapse into one record. That contradicts §2.9's duplicate family and §8.3's two-identical-files collision case. | P1 SPEC OQ1–2 · PLAN Task 6 |
| **I2** | Hash algorithm: SPEC open, PLAN and P4 already disagree | PLAN pins `blake2b-256`. P4's `observation_key` and examples are spelled `sha256:…`. §3.4 keys every extraction result on the content hash. An algorithm change re-keys the cache. Pick one in P1 SPEC OQ10 before any extractor is written. | P1 OQ10 · PLAN `identity.py` · P4 D-stable key |
| **I3** | Volume identifier is `st_dev` in the PLAN | P1 OQ9 asked whether the volume id is stable across remount, rename, and cloud re-sync. PLAN uses `os.stat().st_dev`, which is not stable across remount on macOS. P12's cross-volume move logic will misfire. | P1 OQ9 · PLAN `volume_id_for` |
| **I4** | Analysis tiers named | **Closed** in [`10-i4-learning-ops.md`](10-i4-learning-ops.md): `filesystem \| native \| ocr \| llm`. Live in P4/P5/P6/P2. |
| **I5** | §8.4 local-first `must` is still only an open question | Nothing forbids shipping `cloud_assisted` as the install default. That would satisfy every other P7 rule and violate the design's only local-first `must`. Constrain the shippable set to `offline` or `local_model`; leave the exact pick deferred if you want. | P7 OQ11 · fidelity audit W1 |
| **I6** | Delete-versus-append-only is a real design contradiction | §8.4 gives the user the right to delete local derived data. §8.2 forbids rewriting the evidence record. `Gate.delete_derived` exists marked as conflicting. A v1 product that cannot forget a passport OCR pass is not shippable; a v1 that silently `DELETE`s from `events` is not the product specified. Tombstone projections; keep the log. | P7 OQ4 · P5 OQ6 · P13 OQ11 |

**P1 PLAN is already deciding the substrate.** The structure map says SPECs freeze first, then plans, then code. P1 PLAN already answers OQ1, OQ2, OQ9, and OQ10 in runnable code, while the SPEC still lists them as open. If those answers are wrong — and the duplicate collapse is wrong — every later foreign key is built on them. Close the SPEC first. Then edit the PLAN. Do not execute Task 6 as written.

---

## Leftover contract seams

The 08 re-review listed six original blockers as still open. Four of those are closed in the live specs. These are the residues that are still true when you grep today.

| ID | Status vs 08 | Finding | Fix |
|---|---|---|---|
| **L1** | Still open | P13 routes `review_action` to P11, P10, P9, P7, P1, and P6. Grep of those SPECs for `review_action` or `From P13` returns nothing. Only P12 reciprocated, for `review_approval`. Tree edits, consent choices, group changes, and learning resets have a collector and no consumer. | One Contract-in line each. Same shape P12 already used. |
| **L2** | Still open | §8.6 resource observability (elapsed time, memory, CPU, network) has no owner. P3 quotes the sentence and then disclaims it as a ceiling question. P13's `progress_line` is file counts, not resources. The design's first sentence of that paragraph is unowned. | P3 observes; P13 renders. Ceilings can stay unowned. |
| **L3** | Still open (citation) | Citation audit 06 is still live: `Mn` used where `MINOR n` was meant in P1/P3/P11; P13 claims seven §7.10 actions then lists eight; canvas contracts counted as five, six, and four in the same spec. | Mechanical. Do not freeze with a citation scheme that collides with MAJOR ids. |
| **L4** | Closed | B7 `stage_id = P8/P10/P11`, `destination.kind`, P7 `observation_id`, `text_units` with no consumer, 02 still twelve parts / one-node skeleton. | Already fixed in live specs. Do not re-open. |
| **L5** | Correctly deferred | Every numeric threshold (§3.7 margin, §4 group size, §5.9 depth, §6.10 support, §8.6 ceilings). Gazetteer contents. 200–300 templates. Career fact schema. Locked/open/alias/shortcut behaviour. | Keep deferred. Do not invent numbers to look finished. Author a threshold process, not values. |

**What 08 got wrong by going stale.** If you re-read 08 today it will tell you to fix things that are already fixed. Trust grep, not that document, for B7, B8, M14, N-2, N-3, and the 02 update.

---

## Missed entirely — not in any prior review

Previous passes audited seams, citations, and fidelity to the design text. They did not ask whether the specified product can actually run on a Mac, learn from the user, or survive a crash. These are the holes that would still exist if every leftover seam were closed tomorrow.

### Runtime and platform

| Gap | Why it matters |
|---|---|
| **No product form factor** | The design is an interactive canvas with drag, merge, redaction, and review screens. The specs are Python/SQLite contracts. P13 explicitly fixes no pixel — correct for visual design, silent on whether this is a macOS app, a CLI with a webview, or a daemon. Full Disk Access, TCC, and packaging are unnamed. You cannot ship a Finder-adjacent organizer without this. |
| **Scan-only observation** | P3 is a scan plus stat-cache. There is no FSEvents/kqueue session. During a half-hour review, Downloads will change. Nothing invalidates a plan except P12's pre-apply recheck and a later re-scan. Stale review is the default, not the exception. |
| **iCloud dataless files** | P12 treats cloud paths as externally mutable. It does not mention Optimize Mac Storage: Finder entries that are not on disk. Hashing them forces a download. A Downloads scan on a laptop with optimized storage would pull gigabytes with no budget line and no consent. |
| **Crash mid-apply** | Journal and undo exist. Process death between copy and source removal, or between journal write and commit, is unspecified. SQLite WAL protects the database, not the filesystem transaction. This is the case §8.3's verification points exist for, and it has no crash protocol. |
| **Concurrency** | Can the user review while extraction continues? Can two scans run? PLAN enables WAL. No spec says who holds the write lock during apply, or whether P13 may collect an action against a tree P10 is still freezing. |
| **Database location and rebuild** | §0 says the product can be rebuilt from the filesystem. P1 OQ11 (what survives a rebuild) is still open. If the SQLite file lives inside a scanned root it gets scanned; if it lives in Application Support, provenance is unreconstructible by definition. Pick a location and a rebuild coverage statement. |

### Behaviour the design requires and no part reads

P1 owns the §8.7 learning-record store. P13 can reset it. Nobody queries it before proposing. P8 has `USER_REJECTED_EQUIVALENT` as a stop rule, and both P8 and P9 still leave "equivalent" undefined. As specified, the product records every correction and then ignores the store.

E3 is a dumping-ground extractor: spreadsheets, presentations, email, calendar, contacts, code, audio, and video. That is most of §2.9's format list in one family, with launch-scope for spreadsheets/presentations still an open question. Career is a named launch domain with no fact schema (correctly refused, still a product hole). A launch that claims six domains and can only fact-extract three of them should say so in the segmentation map, not only in deferred tables.

The walking skeleton never touches P7, P8, or P13. That was deliberate. It is also the wrong silence for the one seam where a mismatch is a privacy failure. Add a second fixture path: `NeedsConsent` must surface four options and must not become `abstain`. That is a contract test, not an LLM test.

### Session ownership

Each part publishes a record. The product the user experiences is a session: select corpus, scan, extract, group, design tree, place, review, apply. No part owns that session. P2 owns replay of stages; P13 owns screens; P3 owns a scan run. There is no run-id that ties "this review is of that scan of this plan version." P13 records `plan_version` on actions, which is necessary and not sufficient. Without a session record, `progress_line`, consent grants, and a stale plan cannot be attributed to one user sitting.

Thresholds, gazetteers, and the template library were correctly not invented. What was missed is the process for authoring them: who writes the first Academic gazetteer, from what corpus, and how P2 gates a threshold change. Deferred with no authoring path stays deferred forever.

---

## Already sound — do not re-litigate

The set is faithful to the design. Prior reviews found real bugs and most of those bugs were then actually fixed. Re-opening these will waste the freeze pass.

**Architecture cuts that hold.** Thirteen parts instead of nine sections is the right cut: P4 before P5, P7 before P8, P2 before the stages it measures, P13 as presentation-only, residual library definitions in P10. One observation shape, one gate signature, one verdict vocabulary, node-id addressing with P12 path resolution, `accepts_placement` consumed, embeddings stored as local arrays and forbidden as group establishment.

**Discipline that actually held.** Zero invented templates, gazetteer entries, domain fields, or numeric thresholds. Career/Code/Finance holes flagged rather than filled. §8.6 degradation answered in every part as "never lower-quality automatic classification." The model cannot invent a destination: five parts independently make it inexpressible. Abstention is a success class, not a failure. `NeedsConsent` cannot collapse into abstain inside P8.

| Closed finding | Live evidence |
|---|---|
| B1 one extraction-outcome record | P5 publishes no status vocabulary; eight completeness values match P4. |
| B2 one gate + consent | `Gate.release` → `Released \| Denied \| NeedsConsent` at both ends; P8 has no `NeedsConsent` code by construction. |
| B3 node → path | P10 holds no path strings; P12 composes. |
| B4 destination profile | P10 emits; P11 builds only the retrieval index. |
| B6 `accepts_placement` | P11 Contract-in and Done-means 2 test both absence and false. |
| B7 `stage_id` (after the fix) | P8 = `llm_interpretation`; P10 = `template_generation` + `tree_design`; P11 = `candidate_node_retrieval` + `placement_scoring`. |
| M14 `observation_key` | P7 now materialises by `observation_key`, not `observation_id`. |
| S4 P13 exists | Owns presentation; `review_approval` satisfies P12's required-review policy. |

---

## Recommended freeze order

Nothing below is a redesign. Each item is a named decision or a one-to-three-line contract edit.

| Order | Owner | Action |
|---|---|---|
| 1 | Joseph + P1 | Ratify identity: new row on content change; two live copies are two records sharing a hash, not one `current_path`. Close P1 OQ1 and OQ2 in the SPEC, then rewrite PLAN Task 6. |
| 2 | P1 | Name the hash algorithm in the SPEC. Reconcile PLAN `blake2b-256` with P4's `sha256:` examples. Do not leave this to the first implementer. |
| 3 | P5 + P4 + P6 | Enumerate analysis tiers. §3.4's cache key cannot be formed without them. |
| 4 | P10, P11, P9, P7, P1 | Accept P13 `review_action` in Contract-in. Only P12 currently does. |
| 5 | P7 | Bind §8.4's local-first `must`: install default is `offline` or `local_model`. Leave the exact choice open if needed; forbid `cloud_assisted` as the ship default. |
| 6 | P7 + P1 | Resolve delete-versus-append-only, even as a scoped rule (tombstone derived projections; never delete events). |
| 7 | Lead | Add a product-runtime note: form factor, Full Disk Access, dataless iCloud files, crash mid-apply, and who reads learning records. Not a fourteenth part — a one-page ops contract. |

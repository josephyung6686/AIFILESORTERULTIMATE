# Ops runtime contract

Date: 2026-08-19
Status: **structure contract for how the product runs** — not a fourteenth part, not a UI spec
Resolves: the nine product-ops gaps in [`09-plan-spec-critique.md`](09-plan-spec-critique.md)
Bindings: [`10-i4-learning-ops.md`](10-i4-learning-ops.md)
Design: [`01-product-design-structured.md`](01-product-design-structured.md) · source of truth: [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

This document decides **how the specified system sits on a Mac**. It does not override the design. Where this document and the design disagree, the design wins. Visual layout, pixel, and toolkit choice stay deferred (P13: "It fixes no pixel").

v1 is macOS-only (S1). Every rule below is for that scope.

**Ratified 2026-08-19:** the form factor (§1, a native macOS application) and the database location (§2, Application Support). Both were product decisions the design left implied; they are settled and not reopened. Everything else in this document is derived from the design and follows it.

---

## 1. Form factor

**Ratified 2026-08-19.** The product is a **native macOS application** that embeds the Python parts as a local library, not a CLI the user is expected to drive, and not a daemon that runs when the app is closed.

- **P13 is the process the user launches.** Canvas, review, consent, progress, eval view, and inspect/reset of learning records render here.
- **P1–P12 run in-process** (or in a child the app owns). There is no network listener.
- **Full Disk Access** is required before P3 may scan Desktop, Downloads, Documents, or any user-selected root that TCC protects. Until it is granted, P3 does not traverse; P13 shows why. This is not a handling class and not a `NeedsConsent` model prompt.
- **Packaging, Sparkle, notarization, and the exact UI toolkit** are deferred. The contract is: one local app, one local SQLite database, Finder remains the namespace.

---

## 2. Database location and rebuild (closes P1 OQ11 as far as runtime) — ratified 2026-08-19

The SQLite file lives at:

```text
~/Library/Application Support/<bundle-id>/agent.sqlite
```

It is **never** created inside a scan root, a candidate root, or the destination tree. P3's exclusion rules therefore never have to special-case the database; the database is not in the corpus.

**Rebuild-from-filesystem** (§0) reconstructs what the filesystem plus re-extraction can reconstruct: `files` identity (content hash), `extraction_runs`, observations, `text_units`, facts that deterministic extractors can reproduce. It does **not** reconstruct `events`, learning records, plan versions, consent grants, or review actions. Those have no filesystem source. P13 must say so before a rebuild: provenance and corrections will not come back.

Vectors (S2) are in the same Application Support directory, not in `files` or `events`, and are discarded on rebuild — they recompute from content hash.

---

## 3. Session

A **session** is one user sitting: select corpus, scan, extract, review, apply. It is a presentation grouping, not an §8.5 attribution stage (P13 still emits no `stage_output`).

```text
session_id
  scan_run_id          P3's scan
  plan_version         P10's frozen (or draft) tree this sitting is against
  started_at
```

P13 puts `session_id` on every `review_action` and `review_approval` it already stamps with `plan_version`. Progress line, consent prompts, and stale-plan banners are attributed to this sitting. P2 replay is not a session; it is a harness run.

---

## 4. Live observation (FSEvents)

P3 remains scan-plus-stat-cache. **While a session is open**, P3 also watches the selected roots (FSEvents / `DispatchSource`) and authors `external modification detection` for any watched path whose size or mtime changes, which appears, or which disappears.

- There is **no background daemon** in v1. Closing the app ends the watch.
- P13 marks review items whose `file_id` (or path) appears in a detection as stale — the same stale surfaces §8.3 already requires before apply.
- A detection is not a rescan by itself. P3 may re-stat the one path; it does not restart the corpus scan unless the user asks.

---

## 4b. Applications and system items — never read, never moved

**Ratified 2026-08-20.** Full Disk Access grants the *ability* to read protected locations. It is
not permission to use it. An application bundle, a macOS package, and anything under a system
location is a **protected container**: P3 does not descend into one and hashes nothing inside it,
and P12 never moves one. The rule and its label live in
[`parts/P3-scan-corpus-selection/SPEC.md`](parts/P3-scan-corpus-selection/SPEC.md); this section
exists so the runtime contract cannot be read as licence to traverse everything TCC will allow.

The distinction that matters at runtime: FDA is about what the OS permits, and this is about what
the product chooses. Granting FDA widens the first and changes nothing about the second.

---

## 5. iCloud dataless files

macOS "Optimize Mac Storage" presents Finder entries that are not on disk. Hashing or opening them **downloads** the file.

P3 detects a dataless / not-downloaded ubiquitous item **before** hashing. Detection is a filesystem observation, not a handling class.

- Do **not** materialize, hash, or extract.
- §8.6's progress line must be able to name these files rather than folding them into OCR-capped or unreadable. **This contract does not decide the field.** `extraction_runs.completeness` is P4's closed vocabulary and none of its eight values fits: `deferred` is budget exhaustion, `unreadable` is damaged-or-encrypted, `metadata_only` is format-driven. Choosing one, or adding a ninth, is P4's call — **P4 Open question 6**. Until it closes, P3 records the detection and writes no run row (P5 writes runs, not P3).
- P12 refuses a plan whose source is dataless — §8.3 already refuses an unavailable source, so this needs no new mechanism. It does not download in order to move.
- Materialization is a user action, shown by P13. After the file is local, P3 re-stats and hashing proceeds as normal.

Cloud-synced paths that *are* local still follow P12's existing "externally mutable" rule (verify immediately before and after).

---

## 6. Crash mid-apply

P12's journal is the recovery source. SQLite WAL recovers the database; it does not recover a half-finished filesystem mutation.

On app launch, P12 inspects incomplete journal entries **before** P13 accepts a new apply:

| Where the crash happened | Recovery |
|---|---|
| Journal written, copy not started | Nothing on disk to undo. Mark the entry failed; source is untouched. |
| Copy in progress or copy unverified | Source is truth. Delete the unverified destination copy if it exists (it is not a user file; it is an incomplete mutation). Source stays. |
| Copy verified (V3/V4), source not yet removed | Cross-volume case: complete the source removal **or** surface both copies and refuse to guess. Default: surface both; do not delete the source without the user. Same-volume rename: complete or reverse using the journal; do not leave two names. |
| Undo in progress | Same discipline in reverse. Incomplete undo leaves the post-move state and a failed undo verdict. |

No journal entry is deleted by recovery (append-only events; journal rows supersede). P13 shows the interrupted apply before any new plan runs.

Locked, open-in-another-app, alias, and shortcut behaviour remain P12 OQ3 — this contract does not invent it.

---

## 7. Concurrency

- **One apply at a time.** P12 holds the apply write. A second apply is refused until the journal is quiet.
- **Freeze is exclusive.** P10 does not freeze while P13 has an uncommitted canvas edit on that plan version, and P13 does not collect tree edits against a freeze in flight.
- **Extraction may run while the user reviews.** Review actions bind `plan_version` (already) and `session_id` (above). A fact that lands after freeze does not silently re-place; it waits for the next sitting or an explicit refresh (§8.8: a new plan never silently reclassifies).
- **Two scans do not run on the same root.** A second scan of an in-flight root is refused. A scan of a disjoint root may run.
- SQLite WAL (P1 PLAN) is the isolation mechanism. The rules above are the product rules WAL does not imply.

---

## 8. Learning reads

Specified in [`10-i4-learning-ops.md`](10-i4-learning-ops.md). Runtime consequence: every proposal path (P6, P7, P8, P9, P10, P11) queries `learning_records` **before** emit or `Gate.release`. P13 never applies learning; it only inspects and resets.

---

## 9. Privacy-gate fixture (skeleton addendum)

The walking skeleton in [`02-segmentation-map.md`](02-segmentation-map.md) stays deterministic and model-free. Add a **second fixture path**, still without a live model:

```text
P7/P8   a dossier that requires sensitive text
        Gate.release returns NeedsConsent
        P13 presents the four §8.4 options
        choosing no_model_use does not become abstain inside P8
```

This is a contract test of B2, not an LLM test. It is the minimum that makes the one privacy-failure seam exercisable without waiting for full depth.

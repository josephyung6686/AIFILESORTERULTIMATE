# Resolutions — every blocker, clash, gap and scope decision

Date: 2026-08-19
Status: **binding** — implementers apply these decisions verbatim; they do not re-adjudicate
Resolves: [`03-contract-review.md`](03-contract-review.md) · against [`01-product-design-structured.md`](01-product-design-structured.md) and [`00-database-agent-product-design.md`](00-database-agent-product-design.md)

**Decision criterion.** The north star is correctness of the application. Where two resolutions
are both defensible, the one that preserves more information, or that makes a wrong outcome
impossible rather than merely unlikely, wins. Simplicity is not a tiebreaker against accuracy.

Every finding in the review is resolved here. Five were spot-verified against the specs and the
source of truth before adjudication (B1, B2, B3, M3, M14); all five held.

---

## Scope decisions

| # | Decision | Consequence |
|---|---|---|
| S1 | **macOS-only for v1.** §2.7 names Apple Vision and no other OCR provider. | Closes G12. P5 states macOS-only explicitly; no phantom cross-platform requirement survives in any spec. |
| S2 | **Embeddings ship in v1, with an owner.** | Closes G2. Reverses an earlier recommendation to drop them. §4.2's own worked case is `HW 3.pdf` — the sparse file with no course code, found only by semantic neighbourhood. Dropping embeddings sends exactly those files to abstention, trading accuracy for simplicity. **P9 computes and owns them; P1 stores them as §0's compact local arrays, never a vector database.** They stay out of the walking skeleton, which is deterministic by design. §4.2's "embeddings never establish the group by themselves" and §6.5's "a semantic embedding alone is insufficient" remain in force — this decision affects retrieval reach only, never establishment. |
| S3 | **Career/recruiting fact schema (§3.11) and Code + Finance templates (§5.4) stay deferred.** | G11 is a hole in the design, not a spec defect — §3.15 names Career a launch domain while §3.11's table gives it no fields. Four agents independently caught it and correctly refused to invent one. Joseph authors these when those parts come up. |
| S4 | **The review and approval surface becomes P13.** | Closes G10, G13, G14. §6.11, §7.10, §8.3 and §5.2/§5.9/§5.11 all assume a review surface; none of the twelve owns it, so §8.3's "required review policy" currently has no consumer. Leaving it unowned is the option that guarantees a wrong outcome. |
| S5 | **The §8.7 learning-record store and the §8.6 budget configuration object are P1's.** | Closes G3, G4. P1 already owns the database, the `events` log and its `correction_scope`. A scoped projection over `events` is coherent and avoids inventing a part for a store with no independent behaviour. |

---

## BLOCKING

### B1 — one extraction-outcome record

**P4's `extraction_runs` is the record. P5's parallel status vocabulary is deleted.**

P4 is per-*(file version × extractor)*; P5 is per-file. An opaque image runs both the image
extractor and OCR — two P4 rows, one P5 row — so P5 structurally cannot express "EXIF read
successfully, OCR capped." P4 also carries `coverage {units, processed, total}` and §2.7's
required provider/version/config. Under the information criterion this is not close.

Changes:
- P4 adds `metadata_only` to `completeness` (§2.9's safe default for disk images, executables,
  databases, encrypted containers, unknown binary).
- P4's `completeness` becomes: `complete | capped | partial | metadata_only | deferred | unsupported | unreadable | failed`.
- P5 keeps its router table (format → extractor); P4 explicitly defers that to P5. P5 deletes its
  status enum and restates its §8.6 counting rules against P4's values.
- P5's `extracted_empty` maps to `complete` with zero observations — §2.4's distinction ("an empty
  extraction result is different from an extractor that does not yet exist") is preserved by
  `complete`-with-zero versus `unsupported`.
- P2's adversarial case A9 adopts P4's word (`capped`), not a third one.

### B2 — one gate, and consent survives

**P7's shape is adopted verbatim. P8 renames `seal` to `Gate.release` and gains a `NeedsConsent` branch.**

Verified: P8 contains zero occurrences of `NeedsConsent`. §8.4 requires the user be offered four
options — local model, cloud model, redacted prompt, or no model use — at the moment a model needs
sensitive text. Under P8's contract that requirement disappeared into an abstention. This is the
one seam where a mismatch is a privacy failure rather than a bug, and it is why P7 precedes P8.

Changes:
- P8's call becomes `Gate.release(ModelCallRequest) -> Released | Denied | NeedsConsent`.
- `NeedsConsent` **returns control to the calling part** and surfaces the four §8.4 options through
  P13. It must never be mapped to `abstain`.
- Binding tuple is `(model_target, prompt_fingerprint, policy_version)`. `call_site` is already
  inside `prompt_fingerprint` under P8's own fingerprint rule.
- P8 keeps `Refusal` only for gate-denied, distinct from consent-pending.

### B3 — P12 resolves node → path

**P10 stays platform-neutral. P12 composes and normalizes.**

§8.3's plan record carries "Requested destination node" *and* "Resolved destination path" as
separate fields — verified in the design — so the step exists and was unassigned. P12 owns §8.3's
case-sensitivity, Unicode-normalization, reserved-name and path-length rules, which any resolution
must obey. A plan-versioned tree must not hold platform-specific strings: the same frozen tree must
resolve correctly on a case-sensitive volume and a case-insensitive one.

Changes:
- P10 publishes `root_anchor` plus the ancestor `display_label` chain (it already holds both).
- P12 composes, normalizes, and records the intended display name separately from the
  filesystem-safe name, per §8.3.
- P12 deletes "paths must be supplied at tree design, never by P12."
- P11's "P12 resolves the node to a filesystem path" becomes correct as written.
- P12's Open question 5 (directory creation and its reversal) is now answerable and must be answered.

### B4 — P10 owns the destination profile

02's own *Publishes* column reads "node types **and destination profiles**", and §6.1's contents
(template, expected values, accepted groups, user-selected label, privacy restrictions) are all
P10-held. P11 owns only the §6.2 retrieval index, which P10 already concedes.

Changes: P11 deletes its Contract-out profile table, adds the profile to its Contract-in from P10,
and removes destination profiles from its plan-version state (they are P10's).

### B5 — the event vocabulary opens, with registration

§8.2 introduces its list with "This includes", so nineteen is a floor. P1's reading is right, but
P1's writer validates against a closed set, so as written it would reject all twenty-one types P7,
P8 and P11 declare.

Changes:
- P1 publishes a **registration rule**: each part declares its event types in its own SPEC; P1
  validates against the union; the nineteen §8.2 names are reserved and may not be redefined.
- P7's eight and P8's five are registered as-is.
- P11's eight prose-named events are registered as **typed specializations** of
  `placement recommendation`, not as free-text.
- **P1 OQ5 is settled: one log.** §8.2's event record already carries `prompt fingerprint`, which
  is P7/P8 audit data — the design put them in the same log. §8.4's consent-aware audit record is
  the same log with `correction_scope` and consent fields.

### B6 — P11 consumes the legality flag

`accepts_placement` is the single field P10 built to stop P11 placing into an `ignored` node —
§5.10's guarantee that a user may leave an existing folder untouched. P11 does not receive it, so
P11 as specified would place there, and would also lose §8.4's protected-node rule.

Changes: P11's Contract-in from P10 gains `accepts_placement`, `node_role`, `disposition`,
`expected_values[]` and `handling_class`. P11 Done-means #2 tests `accepts_placement = true` as
well as node existence.

### B7 — the measured parts accept P2's envelope

Verified: `stage_output`, `version_tuple`, `not_implemented` and `budget_state` appear only in P2's
own spec. This is precisely the failure 02 moved P2 to Wave 1 to prevent.

Changes:
- P5, P6, P8, P9, P10 and P11 each add to Contract out: *"Emits P2 `stage_output` with
  `stage_id = <id>`, carrying `inputs[]`, an explicit abstention value, a distinct budget-deferral
  value, and the version tuple."*
- **P6 gains an explicit abstention row.** §3.6 failure currently produces a missing row, which P2
  cannot distinguish from a crash or a skip. P6 emits an `unresolved` marker carrying the field
  attempted and the reason. This is the information-preservation criterion applied directly.

### B8 — the walking skeleton runs

Two independent breaks, both fixed, and the second is a semantic rule rather than a skeleton patch.

**(a) The fact.** P4's fixture 1 carries `context_before: "Course code: "`, which contains none of
§3.5's five required academic context terms, so P6 must refuse it — correctly. P4 changes fixture 1
to `context_before: "Syllabus — "`, which satisfies §3.5 and makes the fixture §3.2's own worked case.

**(b) The two-condition rule at N=1.** §6.10 requires minimum support **and** a margin over
next-best. With one legal candidate the margin is undefined. The resolution is **not** to weaken the
rule:
- P11 states the degenerate rule explicitly: **with exactly one legal candidate the margin condition
  is satisfied vacuously; the minimum-support threshold remains binding and is the sole gate.** A
  file that clears no support threshold abstains even when only one destination exists.
- **The skeleton gains a second frozen node**, so the margin path is genuinely exercised rather than
  bypassed. A skeleton that never tests the margin does not prove the seam it exists to prove.
- 02's skeleton section is updated to a two-node tree.

---

## MAJOR

| # | Resolution |
|---|---|
| **M1** | P1's four columns are the published set, spelled `supersedes`, `superseded_by`, `supersede_reason`, `preferred`. **`preferred` moves off the shared set onto P6's `file_facts` only** — §8.2 says "the resolver may mark", and §3.2 places the resolver after extraction, so P4 is right that the observation layer does not hold it. P4 renames `supersession_reason` → `supersede_reason`. P9 and P11 adopt the full set. |
| **M2** | **P4 adds `signal_tier ∈ {1,2,3}`** (nullable, §2.6-scoped). Re-deriving §2.6's hierarchy in P6 from `extractor_name` + field label would encode the design in a second place and drift. Separately P5 moves "no EXIF" onto `extraction_runs` (absence is never an observation) and moves conflicting-signal resolution to P6's §3.7 margin rule. P5's three image fixtures are restated accordingly. |
| **M3** | P4 relaxes conformance rule 9 to `unsupported`/`deferred`/`failed` only. **`unreadable` and `partial` runs carry the metadata-level observations §2.9 requires** — verified against the source of truth: "at minimum yield filename, format, dimensions or canvas properties, embedded metadata … recorded as indexed-but-unreadable rather than silently treated as empty." Zero observations would make an indexed PSD indistinguishable from a file nobody opened. |
| **M4** | No marker on the observation. **P6 gains an explicit producer/creator discount rule** keyed on P4's `zone = metadata` plus the deferred tool-string list P5 names (`python-docx`, `Mozilla/5.0`, browser-generated producer strings). §2.2 and §2.3 both require the behaviour and nobody owned it. P5 OQ13 closes as answered. |
| **M5** | P4's three-field split (`context_before`, `context_after`, `context_truncated`) is kept — §8.4 must redact a value without dropping its context. **P5, P6, P8, P9 and P11 correct their reproduced field lists** to name P4's three fields instead of §2.8's single "surrounding context" line. |
| **M6** | P2 replaces its four-value residual expectation with P11's full `outcome` vocabulary plus qualifiers. P2's four omitted §7.9's hand-back loop — the mechanism that is the entire reason P11 fuses §6 and §7 — so P2 could not express the design's own worked example (§7.8's Columbia submission screenshot). |
| **M7** | **P9 drops its own verdict enum and consumes P8's `outcome` + `reasons[]`.** P9's five values are recoverable as `(outcome, reason_code)` pairs; P9's central `valid-context-supported` distinction survives as `accept_context_supported`. Closes P9 OQ6. |
| **M8** | **The acting part authors; P1 writes.** P3's `discovery`/`stat observation`/`hashing` and P12's six move to P1's "accepts from others" list. `external modification detection` takes **two authors** — P12 (§8.3 staleness) and P3 (§1.2 re-scan) — and P1's framing is widened to allow it. |
| **M9** | **P8 measures the budget pre-seal and runs §8.6's reduction ladder; P7 keeps `dossier_over_budget` as a backstop that should never fire.** If the gate is the only real check, the ladder never runs and every over-budget dossier becomes a denial instead of a summarize/split/defer — strictly less capable and less accurate. Both specs state the split. |
| **M10** | **Structural fix, not acknowledgement. The residual-library *definitions* (§7.2–§7.4 — the nine names, their attribute slots, and the enable/rename/relocate model) move from P11 to P10; P11 retains the residual *workflow* (§7.5–§7.11).** §7.4 makes approved residual branches legal nodes in the frozen tree, so P10 cannot freeze a complete tree without them — the cycle is real. This also resolves O11 and O12 in one move. P5 → P7 (audio/video transcription authority only) and P8 → P10/P11 (fixture-mediated) are recorded in 02 as acknowledged back-edges. |
| **M11** | **P6 publishes `no_usable_facts(file_id, content_hash) -> bool`** on its read surface. §2.2 requires targeted OCR only when stored evidence yields no usable facts; P5 depends on it, P2 asserts it in case A10, P6 never mentioned it. The threshold is a deferred configuration value (P5 OQ1). |
| **M12** | P9's `basis_facts[]` renames to **`anchor_facts[]`**. P10 accepts **three** membership kinds (`direct-anchor`, `context-supported`, `user-attached` — the third is §4.9's manual attachment for unreadable files). **P9 OQ4 settles yes**: `group_category` *is* the §3.11/§3.15 domain vocabulary, so `domain` and `category` are one field. P10 derives `excluded_members[]` from `Membership.decision = excluded` and `rejected_proposals[]` from `Group.state = rejected` rather than requesting them as fields. |
| **M13** | P12's Contract-in is rewritten against P11's published field names, not §6.11's prose. **P12 states that the five non-`place` outcomes produce no plan**, and refuses on `outcome`, not on `confidence_class`. |
| **M14** | **`observation_key` is the citation handle** in P4's Contract out; P6, P8, P9 and P11 change "observation id" to "observation key." `observation_id` is per-row and dies on extractor upgrade; §8.7 requires a negative example recorded today to still resolve afterwards, which only the content-addressed key satisfies. |
| **M15** | P9 removes `plan_version_id` from `Group` and `Membership` and adds a per-version **`group_acceptance`** record. P9's own plan-versioning answer places groups and memberships in the shared evidence database and only their acceptance state in the plan version; the records contradicted it. Closes P9 OQ8 and defines what P10's freeze record means by "Accepted and rejected group memberships". |

---

## Coverage gaps

| # | Owner | Note |
|---|---|---|
| G1 | **P4** | Adds a `text_units` record keyed by `(run_id, container_path)`. P4's `text_span` already presupposes an addressable text unit and declined to own it; P5 emits bulk text with no home. **Blocks the skeleton** — resolve first. |
| G2 | **P9** computes, **P1** stores | Per S2. §0's compact local arrays; no vector database. |
| G3 | **P1** | Scoped projection over `events.correction_scope`. |
| G4 | **P1** | The §8.6 twelve-ceiling configuration object. Namespaced `grouping.*` / `placement.*` per O10. |
| G5 | **P6** | Version family and duplicate family as universal facts, from P1 content hashes and P5 perceptual hashes. |
| G6 | **P6** | Bounded download session, computed from P3 timestamps, emitted as a `possible` fact only (§3.9, §3.13). |
| G7 | **P6** | Photo-event clustering as a Photos-domain `event` fact (§3.11), deterministic from camera/time/GPS. P9 consumes it as §4.2's fourth seed kind. |
| G8 | **P12** | `cross_folder_moves` enforced at mutation time, alongside the volume check. |
| G9 | **P3** | Curated-versus-incidental signal, as an observation over the directory inventory it already publishes. |
| G10 | **P13** | Per S4. |
| G11 | **deferred** | Per S3 — Joseph authors. |
| G12 | **closed** | Per S1 — macOS-only v1. |
| G13 | **P13** | §8.5's user-facing evaluation view. |
| G14 | **P13** | §8.6's progress line, assembled from P3/P4/P5/P8 counts. |

## Overlaps

O1 → P10 (B4). O2 → P4 (B1). O3 → P3 authors, P1 writes (M8). O4 → P12 authors, plus P3 for
re-scan (M8). O5 → **P3 computes** the §1.2 basic filesystem record; P5 emits `source_type:
filesystem` observations referencing it, never recomputing it. O6 → P8 mechanism, P6 inputs and
consequence (both specs already say this; close P6 OQ2). O7 → P8 mechanism and verdict, P11
destination-specific checks and record (both propose it; confirm and close P11 OQ11). O8 → M9.
O9 → **P8** owns call-count and cost ceilings as the single egress point. O10 → both, namespaced.
O11, O12 → resolved by M10's move.

---

## Implementation partition

No two implementers write the same file.

| Agent | Owns | Applies |
|---|---|---|
| A | P4, P5 | B1, B8a, M1(P4), M2, M3, M4(P5 side), M5(P4 keeps/P5 corrects), M14(P4), G1, S1 |
| B | P7, P8 | B2, B5(register), M5(P8), M9, M14(P8), O9 |
| C | P10, P11 | B3(P10 side), B4, B6, B8b, M5(P11), M10, M12(P10), M13(P11 side), M14(P11), O11, O12 |
| D | P1, P3 | B5(rule), M1(published set), M8, G3, G4, G9, O3, O5(P3) |
| E | P6 | B7, M4(P6 rule), M5, M11, M14, G5, G6, G7, O6 |
| F | P2, P9 | B7(P2), M6, M7, M12(P9), M15, S2, G2 |
| G | P12 | B3(P12 side), M8(P12), M13, G8 |
| H | P13 (new) | S4, G10, G13, G14 |
| — | 02-segmentation-map | Updated by the lead: two-node skeleton, P13, M10 back-edges |

Every implementer works from this document. Where it and the review differ, **this document wins**;
where it and the design differ, **the design wins** and the implementer raises it rather than
resolving it.

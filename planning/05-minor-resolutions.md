# Minor resolutions and remaining question closures

Date: 2026-08-19
Status: **binding** — addendum to [`04-resolutions.md`](04-resolutions.md)
Resolves: the twelve MINOR findings and the four cross-spec questions not covered by 04

> **Citation convention.** Items in this document are cited as **`MINOR n`**, never as `Mn`.
> `M1`–`M15` refer to the MAJOR findings in [`04-resolutions.md`](04-resolutions.md), which are
> different items. Do not conflate the two schemes.

**Rule applied throughout: the design is ground truth.** Where two specs disagree on a count, a
spelling, or a field name, the answer is whatever §-text says — not whichever spec argued better.

---

## MINOR

| # | Finding | Resolution |
|---|---|---|
| 1 | P1 says "twelve §8.2 event fields" and "fourteen file-record items"; §8.2 lists **eleven** and **thirteen** | **Ground truth wins.** P1 corrects both counts and its Done-means #7, which tests against them. |
| 2 | `OCR` (§8.2, P1) vs `ocr` (P4, P5) | **§8.2 spells it `OCR`.** P4 and P5 change. The writer validates against the vocabulary, so this would have failed at runtime. |
| 3 | `supersede_reason` vs `supersession_reason` | `supersede_reason` — already settled by M1; noted here so the P4 edit is not missed. |
| 4 | P1 publishes four verification points; P12 says "three … and cross-volume fixity" | Same four things. §8.2 gives: before preparing an action, immediately before the move/copy, after completion, and cross-volume hash-before-removal. **P1's V1–V4 framing is adopted; P12 aligns to it.** |
| 5 | P1 names P11 as a caller of V1–V4; P11 never mentions fixity | **Drop P11 from P1's caller list.** §6 decides; it never touches bytes. Fixity belongs to P12 alone (plus P1's own writes). |
| 6 | P11's `destination.kind` vs P10's `node_role` | **P10's `node_role` is the vocabulary** — P10 owns the tree. P11 consumes it and drops `destination.kind` unless it expresses something orthogonal, in which case it must be renamed so the two are not confusable. This also gives P11 a way to say "shared-material branch" (§6.9) without abusing `confidence_class`. |
| 7 | P11's `two_condition.verdict = review` has no P8 counterpart | **Adopt P8's representation**: `accept_context_supported` + `requires_review: true`. One vocabulary for one concept (consistent with M7). |
| 8 | P2 keys extraction output by extractor version; P4 excludes version from `observation_key` | Compatible and deliberate — P4 excludes it *so that* replay diffs across extractor versions work. **Both specs state the reason in one sentence** so nobody later "fixes" it into a bug. |
| 9 | P2's bundle carries observations but no run records | **Real gap, not cosmetic.** §8.6's counts and P2's own adversarial case A9 both depend on `completeness`/`coverage`. **P2's replay bundle gains `extraction_runs`.** |
| 10 | P3 records `selected_by` user identity; P1 OQ14 asks whether `user_id` is real in a single-user product | **§8.2 settles it**: "user identity **when there is an explicit user action**". Keep the field, nullable, populated only on explicit user action. **Closes P1 OQ14.** |
| 11 | P5 calls it "parent-folder context"; P3 calls it "directory position" | **§2.9 says "parent-folder context".** Ground truth wins; P3 renames. **Closes P3 OQ3.** |
| 12 | P8's Deferred row reads as if the whole adversarial suite is deferred | P2 authors the twelve cases §8.5 names; **only the hand-labelled reference corpus is deferred.** P8 corrects the wording. |

---

## The four remaining cross-spec questions

| Question | Resolution | Closes |
|---|---|---|
| **May the user create a folder after freeze?** | **Yes — as a tree edit, routed to P10, producing a new plan version.** P11 had already reasoned this correctly; P10 left it open. It follows directly from §8.8 (a tree edit creates a draft plan version and shows a diff) and from §6.12's prohibition on inventing destinations *after* freeze — the user editing the tree is not the system inventing a destination. | P10 OQ4 |
| **Where do OCR provider / config / languages / confidence / capped-flag live?** | **P4's `extraction_runs`.** §2.7 requires all of them stored, and P4's record is per-*(file × extractor)*, which is the only granularity that can hold them. P5 flagged this as "the single most likely place P5 and P4 fail to meet" — it was right to flag it, and P4 had already answered it. | P5 OQ2 |
| **Is `Location` structured?** | **Yes — P4's structured record plus the canonical locator.** P5 called this "the single highest-risk item between P4 and P5"; P4 had settled it. §2.8's per-source-type examples (page/heading, table/row/column, EXIF field, OCR region, manifest path) cannot be expressed by a string. | P5 OQ1 |
| **Who runs §5.7's six template-validation checks?** | **P10.** P8 correctly observed the design does not draw the line, but §5.7 places the checks on "the engine" that validates a generated template against the accepted group — which is P10's freeze-time responsibility. P8 enforces the *JSON-schema conformance* of the generated template; P10 enforces the six semantic checks (no repeated parent dimension, no one-child level, depth limit, no author-as-collector, no protected exposure, no empty branches). | P8 Q9 |

---

## Fidelity rule for the cleanup pass

Every edit above is a correction *toward* the design, never away from it. An implementer that finds
a resolution here conflicting with §-text must **not** apply it, and must report the conflict — the
design is ground truth and this document is subordinate to it.

# Citation audit

Date: 2026-08-19
Scope: all thirteen `planning/parts/*/SPEC.md`, audited against
[`01-product-design-structured.md`](01-product-design-structured.md),
[`04-resolutions.md`](04-resolutions.md), [`05-minor-resolutions.md`](05-minor-resolutions.md),
[`02-segmentation-map.md`](02-segmentation-map.md), and each other.
**No file was edited.**

**Verdict:** the `Mn` / `MINOR n` conflation is real and not exhausted — nine live instances remain,
seven of them in P1 and P3, the two specs already patched for it; beyond that scheme the citation
layer is in good shape, with five further wrong references, three count mismatches, two stale
cross-part claims, and a scatter of quotations marked verbatim that are not.

**Checked:**

| Kind | Occurrences | Wrong |
|---|---|---|
| `Mn` (MAJOR) | 121 | **9** (+1 arguable) |
| `MINOR n` | 11 | 0 |
| `Bn` (BLOCKING) | 96 | 0 |
| `Gn` (coverage gap) | 68 | 0 |
| `Sn` (scope) | 37 | **1** |
| `On` (overlap) | 31 | 0 |
| `OQn` / `Open question n` | 47 | **3** stale, **1** wrong-part |
| `§n.n` | 4,140 (89 distinct sections) | **1** wrong section + 8 inexact quotations |

Every `Mn`, `MINOR n`, `Bn`, `Gn`, `Sn`, `On` and `OQn` occurrence was checked individually. For
`§n.n`, every section citation carrying a count, a field list, a required behaviour, a prohibition or
a quoted phrase was verified against the design text (all 89 distinct sections were read); the
remaining pointer-style citations were sampled. No spec cites a section that does not exist.

---

## WRONG — miscited, must fix

### A. `Mn` used where `MINOR n` was meant (the hunted bug)

| # | File | Line | Reads | Should be | Evidence |
|---|---|---|---|---|---|
| 1 | `parts/P1-storage-identity-provenance/SPEC.md` | 88 | `parent-folder context (§1.2's "directory position", renamed to §2.9's spelling — M11)` | `MINOR 11` | M11 is `no_usable_facts(file_id, content_hash) -> bool` on P6's read surface. MINOR 11 is *"P5 calls it 'parent-folder context'; P3 calls it 'directory position' → §2.9 says 'parent-folder context'. Ground truth wins; P3 renames."* P3:390 cites the same decision correctly as `MINOR 11`. |
| 2 | `parts/P1-storage-identity-provenance/SPEC.md` | 133 | `directory_position          P3 publishes it as parent-folder context (M11)   §1.2, §2.9` | `MINOR 11` | Same finding as #1. |
| 3 | `parts/P1-storage-identity-provenance/SPEC.md` | 178 | `user action — nullable, populated only then     §8.2, M10` | `MINOR 10` | M10 is the §7.2–§7.4 residual-library move from P11 to P10 — nothing to do with `user_id`. MINOR 10 is *"§8.2 settles it: 'user identity when there is an explicit user action'. Keep the field, nullable… Closes P1 OQ14."* P3:113 and P3:119 cite this correctly as `MINOR 10`. |
| 4 | `parts/P1-storage-identity-provenance/SPEC.md` | 265 | `**P12 (§8.3) is the only caller** (M5) — §6 decides where a file should go and never touches bytes` | `MINOR 5` | M5 is P4's three-field context split (`context_before` / `context_after` / `context_truncated`). MINOR 5 is *"P1 names P11 as a caller of V1–V4; P11 never mentions fixity → Drop P11 from P1's caller list. Fixity belongs to P12 alone."* The sentence is verbatim MINOR 5's reasoning. |
| 5 | `parts/P1-storage-identity-provenance/SPEC.md` | 464 | `the calling part — P12 (§8.3), the only caller of V1–V4 (M5) — with `subsystem` naming P1 as the performer` | `MINOR 5` | Same finding as #4. |
| 6 | `parts/P1-storage-identity-provenance/SPEC.md` | 603 | `14. **Settled — M10.** `user_id` is **kept, nullable, and populated only on an explicit user action**.` | `MINOR 10` | Same finding as #3. This is the closure of P1 OQ14, which MINOR 10 closes by name. |
| 7 | `parts/P3-scan-corpus-selection/SPEC.md` | 56 | `§1.2's "directory position" and §2.9's "parent-folder context" are **one field**, published under §2.9's name (M11; R2 below).` | `MINOR 11` | Same finding as #1. **P3's own OQ3 at line 390 already says "Settled — MINOR 11"** — the spec cites two schemes for one decision. |
| 8 | `parts/P3-scan-corpus-selection/SPEC.md` | 136 | `parent-folder context      P3 observes           (§2.9's name; §1.2 spells it "directory position" — one field, M11)` | `MINOR 11` | Same finding as #7. |
| 9 | `parts/P11-placement-residual/SPEC.md` | 299 | `verdict                     accept_direct \| accept_context_supported \| weak \| reject \| abstain — P8's outcome vocabulary, carried unchanged                     §6.10, §4.8, M7` | `MINOR 7` | M7 is *"P9 drops its own verdict enum and consumes P8's `outcome` + `reasons[]`"* — a P9 finding. The finding that made **P11** adopt P8's vocabulary is MINOR 7 (*"P11's `two_condition.verdict = review` has no P8 counterpart → adopt P8's representation"*). **P11:388 cites `MINOR 7` for this exact field.** |

**Arguable, same family — recommend correcting:**

| # | File | Line | Reads | Should be | Evidence |
|---|---|---|---|---|---|
| 9b | `parts/P11-placement-residual/SPEC.md` | 347 | `Two vocabularies for one concept is what M7 forbids, and P10 owns the tree` | `MINOR 7` (or MINOR 6) | The paragraph is headed *"**Why there is no `destination.kind`** (MINOR 6)"* — a `node_role` question. "One vocabulary for one concept" is MINOR 7's own formulation, which itself says *"(consistent with M7)"*. M7 states no general prohibition; appealing to it directly is one inference step too far in a spec that is otherwise exact. |

### B. Other reference kinds

| # | File | Line | Reads | Should be | Evidence |
|---|---|---|---|---|---|
| 10 | `parts/P13-review-approval-surface/SPEC.md` | 363 | `The contents of the nine residual templates — the values for §7.2's eight attribute slots \| §7.2, §7.3, **S3**` | **M10** (P10 owns the definitions; the slot *values* are deferred there) | S3 defers exactly two things: *"Career/recruiting fact schema (§3.11) and Code + Finance templates (§5.4)"*. Residual templates are not in its scope. P10:593 and P11:524 both attribute this same deferral to **M10**. |
| 11 | `parts/P6-facts-facets/SPEC.md` | 178–179 | `§4.3 is explicit that the graph "does not automatically copy those missing facts onto sparse files"` | **§4.1** | The sentence is design line 598, in §4.1 *The division of labour*. §4.3 does not contain it. (§3.9, cited alongside for the session clause, is correct.) |
| 12 | `parts/P6-facts-facets/SPEC.md` | 553 | `a deferred configuration value (P5 Open question 5 flags that the design defines it nowhere)` | **P5 OQ1** | P5's current OQ1 is *"What is the 'no usable facts' threshold?"*. P5's current OQ5 is *"Do spreadsheets and presentations ship at launch or ship as `unsupported`?"* — an unrelated release-scope question. P5 renumbered when it deleted settled entries. |
| 13 | `parts/P6-facts-facets/SPEC.md` | 605 | `\| **The `no_usable_facts` threshold** \| §2.2, §2.7 \| M11, **P5 OQ5**.` | **P5 OQ1** | Same as #12. (M11 is correct.) Note `04-resolutions.md` M11 carries the same stale number, so this propagated from the resolution. |
| 14 | `parts/P4-evidence-shape/SPEC.md` | 790–791 | `*Does the observation carry §2.6's signal tier?* **(P5 OQ3)** — settled by **M2**: yes, `signal_tier`.` | drop the OQ number, or cite P5's "Settled since the draft" block | P5's current OQ3 is *"What are the analysis tiers?"* (§3.4 / §8.2 extractor tiers) — a different question. P5 moved the §2.6-tier question into its settled block and renumbered. |

---

## UNVERIFIABLE — claim not locatable in the cited source

| # | File | Line | Claim | Finding |
|---|---|---|---|---|
| 15 | `parts/P13-review-approval-surface/SPEC.md` | 124 | *"…one row per (file version × extractor) (B1), **with P5 supplying which ceiling caused a `capped` or `deferred` run** (§2.7, §8.6)."* | P5 publishes no field naming *which* ceiling fired. P5's record is `run.completeness` (`capped`), `coverage {units, processed, total}`, `config`, `config_fingerprint` (P5:92–93, 157, 429). §8.6 names the twelve ceilings but nothing carries the identity of the one that stopped a run. P13:287 then requires the progress line to name it — *"named, not implied §8.6, G4"* — so this is a live contract gap, not just a citation slip. |
| 16 | `parts/P13-review-approval-surface/SPEC.md` | 594 | *"12. **Is `user_id` meaningful in a single-user product?** … and P1 asks whether it is real. *P1 OQ14. Threatens P1.*"* | P1 OQ14 is **settled**, by MINOR 10, and P1:603 records the closure. P13 presents a closed question as open. |
| 17 | `parts/P13-review-approval-surface/SPEC.md` | 42 | *"…and P10's rule that **"protected profiles are redacted at the boundary, not at the renderer"**."* | Locatable — P10:282 — but reworded: P10 writes *"Protected profiles are redacted at the boundary, not at the renderer"* as its own prose, not as a quotable rule. Presenting it in quotation marks as "P10's rule" is fine in substance; noted only for exactness. |
| 18 | `parts/P2-eval-replay-harness/SPEC.md` | 21 | *"(`02-segmentation-map.md`, *Order*: **"per-stage measurement cannot be retrofitted"**)"* | 02's *Order* section says *"Retrofitting per-stage measurement means rewriting every stage's boundaries."* The quoted string does not appear in 02. Paraphrase presented as a direct quote. |

---

## COUNT MISMATCHES

| # | File | Line | Asserts | Actual | Evidence |
|---|---|---|---|---|---|
| 19 | `parts/P13-review-approval-surface/SPEC.md` | 54 | *"the **seven** user actions §7.10 enumerates"* | **eight** | §7.10: *"accept a proposed destination for one file, accept the same destination for a small batch, change the destination, create a custom folder, return the file to a different accepted group, mark it as private, defer it, or leave it untouched."* **P13:390 itself lists eight**: *"accept one, accept a batch, change the destination, create a custom folder, return the file to a different accepted group, mark private, defer, leave untouched."* The spec contradicts itself. |
| 20 | `parts/P13-review-approval-surface/SPEC.md` | 98, 216 | *"the **five** canvas data contracts"* / *"P10's **five** canvas data contracts"* | **six** published by P10; P13 names **four** | P10 Contract out §5 (line 433) publishes six named surfaces: Branch candidate, Protected areas, Existing folders, Vertical pass, Live structural feedback, Tree health. P13:98's own parenthetical enumerates four (branch candidates; existing folders and protected areas; live structural feedback and warnings; tree health) and P13:66 lists four. Three different counts for one contract. |
| 21 | `parts/P7-privacy-consent-gate/SPEC.md` | 562, 564 | *"no non-model connector is named in **the twelve parts**"* / *"anything added beyond **the twelve**"* | **thirteen** | S4 added P13. `02-segmentation-map.md` still says twelve throughout (its §*Why twelve parts and not nine sections*, and *"all twelve seams"* at line 22) — 04's implementation partition assigns that update to the lead and it has not been made, so 02 and P7 are stale together. |

**Verified correct counts** (each checked against the design, no discrepancy): §8.2's nineteen event
types and eleven event-record fields and thirteen file-record items; §8.2's four checksum
verification points (V1–V4); §8.3's thirteen plan-precondition fields and five staleness triggers;
§8.4's five handling classes, five protected kinds, four options, four operation modes, six audit
fields, five redaction facets; §8.5's ten attribution stages, ten measured dimensions, twelve
adversarial cases, eight bundle items; §8.6's twelve ceilings (P1's fifteen keys = twelve + three
namespaced, internally consistent) and P5's four consumed ceilings; §8.7's six correction scopes and
the five tree-stage actions P10 claims; §0's four SQLite properties; §1.1's three selections and
eleven literal directory names; §1.2's ten fields; §2.6's three signal bands and three traps; §2.7's
nine required OCR items; §2.8's eleven-field observation shape; §3.3's four validator clauses; §3.5's
five academic context terms; §3.6's four checks; §3.10's three named patterns; §3.11's six-row domain
table; §3.13's six reliability states; §3.15's six launch domains; §4.2's four seed kinds and six
retrieval channels; §4.3's five pre-model computations; §4.5's four constrained tasks; §4.8's six
checks; §4.9's six stop rules; §4.10's five pipeline steps; §5.1's nine illustrative names; §5.2's six
branch actions; §5.4's five templates; §5.7's six semantic validation checks and 200–300 library;
§5.12's five node types; §6.6's six invocation conditions; §6.11's four confidence classes; §6.12's
nine steps and three prohibitions; §7.2's eight attribute slots; §7.3's nine templates and four stated
default locations / five unstated; §7.5's eight review-set lines and seven display attributes; §7.7's
eight actions; §8.8's eleven plan-version items; P4's twelve conformance rules; P5's six extractors;
P2's seven assertion verdicts; P9's twelve open questions with six settled; P12's six §8.2 event
types; P11's six placement outcomes (with its own explicit reconciliation of M13's "five" at P11:491).

---

## Inexact quotations — presented as verbatim, not verbatim

None changes a decision; all are worth tightening because these specs use quotation marks as a
fidelity claim.

| File | Line | Quoted as | Design says |
|---|---|---|---|
| `parts/P9-grouping/SPEC.md` | 452 | §4.9's *"a university name alone **must** not create a group"* | §4.9: *"A university name alone **should** not create a group"* — strengthened |
| `parts/P8-llm-harness-validator/SPEC.md` | 191 | §4.5: *"**may** not invent group members beyond those retrieved by the engine"* | §4.5: *"It **must** not create a final folder hierarchy, infer unsupported dates, or invent group members beyond those retrieved by the engine"* — weakened |
| `parts/P4-evidence-shape/SPEC.md` | 121, 520 | §8.5's *"did the expected text appear?"* | §8.5: *"Did the expected text, metadata, table values, OCR text, or image facts appear?"* — silently elided |
| `parts/P10-tree-design-freeze/SPEC.md` | 691 | §8.7: *"renaming a branch, merging or splitting groups, changing template order, creating a custom template, choosing a shallow fallback."* | §8.7 has *"…creating a custom template, moving a residual file to a custom location, choosing a shallow fallback…"* — an item dropped mid-quote with no ellipsis. The *count* of five is right; the quotation is not |
| `parts/P10-tree-design-freeze/SPEC.md` | 539 | §7.3: *"should normally remain local-only and must not cause filenames or content to be exposed in model prompts"* | §7.3: *"Normally local-only; must not cause filenames or content to be exposed in model prompts"* — reflowed into a sentence |
| `parts/P10-tree-design-freeze/SPEC.md` | 35 | §7.4: *"a legal node in the frozen destination tree,"* | §7.4: *"those branches become legal nodes in the frozen destination tree"* — silently singularised (P12:157 quotes it correctly) |
| `parts/P6-facts-facets/SPEC.md` | 356 | §8.6: *"visible as deferred, never as 'understood and found unimportant'"* | Compresses two separate §8.6 sentences (*"show the difference between completed work and deferred work"* and *"avoids the false impression that an unprocessed file was understood and found unimportant"*) into one quotation |
| `parts/P9-grouping/SPEC.md` | 455 | §4.3: *"Whether the neighbourhood has a syllabus"* | §4.3: *"identify whether the neighborhood has a syllabus"* |

**Also worth a look, not an error:** P6:502 and P6:516 (and G7 in `04-resolutions.md`) call the
deterministic photo event *"§4.2's fourth seed kind"*. §4.2's seed-kind enumeration is *"a strongly
identified file, a validated shared fact, a structural family, or a user-created starting point"* —
the photo event is the fourth **bulleted group-type example**, not the fourth member of that list.
The quoted phrase is exact; the ordinal is loose.

---

## CORRECT — spot-checked and sound

- **All 96 `Bn` citations.** B1 (P4's `extraction_runs` as the single outcome record — P4:411,
  P5:92/144/427/570/618, P13:124/295/563), B2 (the gate signature and `NeedsConsent` — thirteen in
  P7, fifteen in P8, three in P13), B3 (P12 resolves node → path — P10:201/544/635, P11:155/500,
  P12:697, P13:70/97), B4, B5 (event registration — P1:169/200/219/421/575/615, P3:85/315, P6:210,
  P7:432/438, P8:491, P13:438), B6, B7 (P2's envelope — P5:126, P6:170/315/347/562/578/662/719,
  P8:439/443, P10:158, P11:226), B8(a) and B8(b) each resolve to the right BLOCKING finding.
  P10:604 and P11:411 correctly flag that 02's skeleton is still one node where B8(b) requires two.
- **All 68 `Gn` and 31 `On` citations.** Including the two that read as suspicious and are not:
  P12:705 (*"Settled by S4 **and G5**"*) is right — S4 covers the reviewing surface, G5 covers the
  version-family fact being P6's — and P3:397 (*"Settled — O5 / G5"*) likewise splits correctly
  across the two halves of its sentence.
- **36 of 37 `Sn` citations**, including P13:361 (S3 for Career fact fields — correct, unlike its
  neighbour at 363).
- **All 11 `MINOR n` citations** (P3:113/119/390, P4:211/695, P5:524, P10:219, P11:345/388,
  P12:43/74). The four already-fixed instances the lead found are fixed and correct.
- **112 of 121 `Mn` citations**, including every M2, M3, M4, M9, M10, M12, M13, M14 and M15
  occurrence.
- **Cross-part `OQ` references** other than #12–#14, #16: P13:553→P11 OQ3 ✓, P13:581→P2 OQ12 ✓,
  P13:584→P2 OQ10 ✓, P13:588→P12 OQ7 ✓, P13:324→P12 OQ10 ✓, P10:136/346 and P8:711→P8 Q9 ✓,
  P9:453→its own OQ9 ✓.
- **`02-segmentation-map.md` references**: P4:16 and P4:604, P2:292/467/476, P9:464 all quote 02
  accurately (P2:21 is the exception, above).
- **§ citations**: no spec cites a nonexistent section. Every load-bearing § claim checked resolved
  correctly except #11. P11's entire §6/§7 design-slice table (lines 46–61) and P10's §5/§7 tables
  were verified obligation by obligation against the design and are accurate.

---

## Recommended fix order

1. **#1–#9** — nine one-token edits (`Mn` → `MINOR n`) across P1 (6), P3 (2), P11 (1). Both P3
   instances and the P11 instance sit in specs that already cite the correct scheme elsewhere for the
   same decision, so they are unambiguous.
2. **#10, #11** — one wrong scope decision and one wrong section, both single-token.
3. **#19, #20** — the two P13 counts; #20 requires deciding whether P13 means four, five or P10's six.
4. **#12–#14, #16** — stale open-question numbers. Consider adopting P1's and P3's convention
   (*"Settled entries keep their original numbers so that existing citations still resolve"*) in P5
   as well, which would make #12–#14 resolve without edits to the citing specs.
5. **#15** — a real contract gap, not a citation slip: either P5 gains a ceiling-identity field or
   P13:124 and P13:287 drop the requirement that the progress line name the ceiling.
6. **#21** — stale part count, blocked on 02 being updated for P13 as 04's partition table already
   requires.

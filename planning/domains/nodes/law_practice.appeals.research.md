# Research memo — `law_practice.appeals`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.appeals.json`
Roster row: catalogue `law.appeals` (07-law-legal-practice.md §12), template on the fieldless `law_practice` schema, `parent_id: null`, `launch: "placeholder"`
Pass: R1b edge repair on a salvaged draft **plus** the missing research memo. The JSON existed with no memo — an agent was killed mid-row — so the draft was treated as untrusted and verified against the schema anchor before this memo was written.

## Result

**Accept the node.** It passes the CONNECTION §2 template test on the first leg — detection signals — by a wide margin, and it does not need the other two legs. Its distinguishing default is a **two-tier proceeding-identifier pair bound by an explicit below/above relation**, plus a **compilation apparatus** (continuous independent pagination overprinted across documents that already carry their own page numbers, an index mapping each member to a page range, and a designation or certification page) that no other row in the 40-row `law_practice` family produces. It also carries one privacy rule the schema does not state: an appeal routinely produces a sealed version and a public-redacted version of one filing, and the public half never licenses the sealed half.

It declares **no fields** and **no folder dimensions** (PR-6, D1 as narrowed), and it mints nothing. The row's whole field contribution is a re-statement of the schema's own request that R1c adjudicate canonical `project` once for the family, plus one honest observation about cardinality that the schema does not raise.

**What this pass changed in the salvaged draft.** Nothing in `recognition`, `file_examples`, `template`, `sensitivity` or `open_question` — those were verified against the `law_practice` anchor and found consistent (see *Draft verification* below). Two changes were made:

1. All five `collides_with` entries and both `also_holds_with` entries were bare id strings. Each now carries a `signal` naming the concrete evidence item both rows compete for and what discriminates it. One entry carries a grep-verified `design_cite`.
2. One factual repair: the draft named `law_practice.depositions-testimony` inside a `must_not_conclude` string. That id does not exist. The roster row is `law.depositions` → `law_practice.depositions`. Corrected.

No entry was removed. All five collisions are real — see *Every collision re-argued* — and this is worth stating plainly because three of the five point at rows that are **real roster entries but not yet authored as node files** (`law.motions-and-briefs` #10, `law.orders-and-judgments` #11, `law.hearing-transcripts` #22). Their absence from `planning/domains/nodes/` is an authoring backlog, not a dangling edge, and deleting them to make the file self-consistent would have been the wrong repair.

## Binding material read

Read for this pass: the row's own JSON in full; the `law_practice` schema anchor (`law_practice.json`) for the precondition, the never-alone list, the template prose recommendation and the `proposed_fields` set it asks all 36+ siblings to reuse; `planning/domains/CONNECTION.md` at the `collides_with` / `also_holds_with` lines only (19, 182, 233, 241–272, 375–376, 393, 494) rather than whole, per the token-tight instruction; `planning/domains/dispatch/RESEARCH-BRIEF.md`; the catalogue entries for this row (§12) and for its five neighbours (§10, §11, §22, and the `law.evidence-exhibits` and `legal.personal-legal-matters` node files) in `planning/domains/07-law-legal-practice.md`; the roster table rows 1–40; `identity.core-documents.json` for the exemplar signal idiom; `legal.practice-matter-file.research.md` for memo calibration. `planning/00-database-agent-product-design.md` was **not** read whole — it was grepped only to verify the two spans quoted below, per instruction.

The controlling constraints:

- **PR-6 / D1 as narrowed** — `law_practice` is a fieldless placeholder schema, so a template of it declares `fields: []` and `dimension_order: []`. Activation unlocks recognition, safety posture, universal facts and child-template consideration only.
- **CONNECTION §5 and the `collides_with` row of the edge table** — `collides_with` means *mutex given the same evidence item*, is symmetric, is reciprocity-enforced post-migration, and **must carry `signal`: the discriminating evidence**. Its consumers are P6 activation step 3 and the P8 validator, which read the signal to decide which side a shared evidence item counts toward. A bare id therefore records the existence of a conflict while withholding the only part the engine can execute.
- **CONNECTION invariant 1** — `collides_with` and `also_holds_with` may coexist on one pair, and the price is that the collision entry must name the discriminating evidence. This row does not carry both edges to any one neighbour, but the invariant is why the `also_holds_with` entries were also converted rather than left bare.

Two spans quoted in the JSON were grep-verified verbatim against `00` for this pass:

- "The user’s frozen tree should therefore include a policy for shared material" (§6.9 in `01-product-design-structured.md`, line 1253; `00` line 113 — note the curly apostrophe, which is what the source carries).
- "Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed."

## Draft verification against the schema anchor

The draft was checked field by field against `law_practice.json` before any of it was trusted.

| Check | Verdict |
|---|---|
| `schema_id`, `kind`, `parent_id`, `launch`, `provenance` | consistent — `law_practice` / `template` / `null` / `placeholder` / `proposal` |
| `fields: []`, `template.dimension_order: []`, `time_first: false` | correct under PR-6; the schema's own three reasons are cited without being re-argued |
| `sensitivity` | `potentially_sensitive`, matching the schema and catalogue §12 |
| Precondition inheritance | The first `deterministic` entry restates the schema's two-leg precondition (a repeated exact matter reference **plus** an artefact separating a practitioner role from a client role) as a precondition rather than as a new claim, and every later signal is marked as an addition to it. This is correct and it is what makes the row's hardest fixture — the downloaded `Smith v Jones` appellate judgment — refuse even though it satisfies the row's own headline signal. |
| `never_alone` | Strictly a superset of the schema's list in this row's vocabulary. It correctly strikes the word *appeal*, the appellate caption, a single docket number, continuous pagination alone, volume numbering alone, and the existence of a redacted version. |
| `proposed_fields` | One entry, `project`, reusing the schema's own decline-to-mint argument unchanged and adding the cardinality observation. No mint. Correct. |
| `file_kinds` | Narrows the schema (drops `contacts`, `.mbox`, `.dat`). A template narrowing its schema's source types is legitimate; `never_alone: true` is preserved. |
| Neighbour ids referenced in prose | `law_practice.discovery` ✓, `law_practice.motions-and-briefs` ✓, `law_practice.evidence-exhibits` ✓, `law_practice.legal-research` ✓, `law_practice.time-and-billing` ✓, `law_practice.hearing-transcripts` ✓, **`law_practice.depositions-testimony` ✗ → repaired to `law_practice.depositions`** |

One divergence from the catalogue is deliberate and is left standing. Catalogue §12 proposes five fields (`appeal_identifier`, `lower_case_identifier`, `appellate_court`, `decision_under_appeal`, `appeal_stage`) and a `client → matter → appeal → document type` template. Under PR-6 none of that may be declared, and the draft correctly demotes the whole of it to prose plus one `proposed_field`. The catalogue's `appeal_identifier` / `lower_case_identifier` split is exactly the ordered-pair problem the row raises as NJ-APP-1, and it is raised as a **cardinality question about one canonical key**, not as a licence for two keys.

## The node test, all three legs

**Leg 1 — detection signals differ from the schema's default. PASSES, and this is the leg the row stands on.** The schema's default fires on one exact matter reference repeated across artefacts plus one artefact separating a practitioner role from a client role. This row requires that **plus** two things the default cannot express:

- A heading zone carrying **two** proceeding identifiers in a labelled below/above relation — an appellate docket in caption position and a separately labelled on-appeal-from line naming the court, the case number and the dated decision it comes from. The catalogue calls the two-identifier pattern "close to unique to appeals" and that is the right calibration: it is close to unique, not unique, which is why one identifier alone stays struck and why the downloaded-judgment fixture still refuses.
- A **compilation apparatus**: continuous independent pagination overprinted across member documents that already carry their own page numbers, an index mapping each member to a page range, a volume marker within a declared total, and a designation or certification page naming the compiler and an as-of date. No other row in the family produces the index-to-range mapping. The double pagination is the observation; the mapping is what makes it a compilation rather than a bundle.

**Leg 2 — recommended dimensions differ. PASSES on the prose recommendation, which is all PR-6 permits.** The schema recommends client (only where genuinely multi-client and explicitly approved) → matter → document function → period. Under that order an appealed matter collapses, because the same function words recur **at every tier**: there is a brief, a motion, an order, a transcript and a bundle at first instance and another of each on appeal. Flattening them puts two different documents with the same name in one folder and loses which decision each belongs to. The row holds matter → **proceeding tier** → function → period as prose, with the tier level named by the proceeding's own identifier and never by a party. This adds exactly one level and argues for it from `00`'s own intelligibility principle rather than from convenience.

**Leg 3 — privacy rules differ. PASSES on one specific rule.** The schema protects a named third party who never chose this filesystem. This row adds the sealed/public-redacted pair rule: the two halves are one `version_family`, both are kept, neither is a duplicate of the other, and **the existence of a public half raises the sealed half's protection rather than lowering it**. It also sharpens the bulk-sensitivity claim — a compiled record is a multi-subject document *by construction*, gathering and re-paginating the evidence of parties, witnesses, deponents and non-parties into one file.

Any one of the three would have carried the row. All three hold.

## Every collision re-argued, and why none was deleted

The task permitted deleting an entry that is genuinely not a collision. None qualified. Each pair below competes for a **specific evidence item that physically exists in both worlds**, which is the narrowed meaning `collides_with` now carries.

**`law_practice.orders-and-judgments`.** The shared item is the decision under appeal — one PDF that is both the instrument governing the proceeding below and a bound member of the appendix. The catalogue's own §12 table already names this pair, and §6.9 is the design's answer to a file with two valid homes. The signal makes the split executable rather than descriptive: the operative paragraphs and the single caption count wholly for the neighbour; the overprinted record pagination counts wholly for this row; appendix membership lives on the index, never on the member. This row takes only what carries the tier pair **and** a direction addressed to a lower tribunal — the appellate disposition, mandate, remittal or certificate of result. `design_cite` attached.

**`law_practice.motions-and-briefs`.** The shared item is a written submission with a table of contents, a table of authorities with page back-references, a certificate of compliance and a captioned counsel block. That combination is verbatim the neighbour's headline deterministic signal (§10: a table-of-authorities heading with a captioned case identifier; a certificate-of-compliance or word-count block co-occurring with a case identifier) and it is equally satisfied by an appellant's brief. Brief grammar therefore discriminates **nothing** and a bare edge here was actively misleading. The discriminators are the labelled STANDARD OF REVIEW section and the on-appeal-from line. The signal also names the hard half rather than smoothing it: an appellate **stay, extension of time or expedition** application is a motion in every structural respect and an appellate artefact in tier, and this row claims it — decided by the tier pair, never by the word *motion*.

**`law_practice.hearing-transcripts`.** Competes twice, and both were written in. (a) The appellate oral-argument transcript is a hearing transcript whose sitting court merely happens to be the appellate one. (b) A first-instance day's transcript is reproduced and re-paginated inside the record. The resolution is a concession this row should make loudly: **it never owns a transcript on a transcript's own evidence, not even its own hearing's.** Cover-plus-certificate-plus-page-and-line is §22's structure and owns every verbatim record at either tier. This row owns only the compilation apparatus around one — the transcript order and designation form (two-column designated / counter-designated, hearing dates, reporter slot, payment or certification line) and the index entry mapping a transcript extract to a record page range. A designation names hearing dates and contains no testimony.

**`law_practice.evidence-exhibits`.** The sharpest pair in the set, because the two rows have nearly the same **two-leg shape**: a token-bearing artefact plus a table closing over the token namespace. The shared item is one document carrying two overprinted numbering layers on top of its own pagination — an exhibit designator from tendering, a record page number from compilation. The discriminator is which namespace the table closes over and what its columns are for: the neighbour's schedule enumerates designators with a producing/offering party column and commonly an objection or admitted column (a table about **tendering**); this row's index maps members to page ranges with a volume marker and a certification page (a table about **compilation**). Item-by-item firewall: the designator counts wholly for the neighbour even on a page stamped JA-1041; the record range counts wholly for this row even when the member underneath is Exhibit 14.

**`legal.personal-legal-matters`.** The only pair where this row's headline signal **does not discriminate at all**, and saying so is the point. A litigant in person files a notice of appeal carrying the caption, the on-appeal-from line, the tier pair and the grounds — every deterministic signal this row lists. The discriminator is the **side**, supplied by the schema's precondition rather than by anything on the appellate face; the neighbour's mirror selector is direct holder-role evidence in the same file (holder named as a party, served, or signing). The error is asymmetric and the asymmetry is the routing rule: this row over-firing writes practitioner apparatus and a client role onto a person's own dispute, so wherever the side cannot be cited the neighbour's safety-only protection runs and this row abstains.

## `also_holds_with`, converted

Both entries were bare schema ids on a template row. Converted to objects with disjoint-evidence signals and an explicit firewall sentence each.

- **`legal`** — named fixture: an appellate judgment, sealed order or filed submission inside a matter. `legal` takes the tribunal caption plus operative paragraphs (or a bound party pair with an execution block); this row takes the tier pair, the record index, the designation page and the sealed/redacted version caption. The caption is struck never-alone here, so it is never double-counted. Safety order of operations quoted verbatim.
- **`finance`** — named fixture: `Appeal costs schedule - Hartley v Nash.xlsx`, already in this row's `file_examples`. This row takes the proceeding-identifier header and the statement-of-truth line; `finance` takes an institution-and-account header or an issuer-and-billed-to block with an invoice number, which this row claims none of. One money figure, one period label and one party name must never count for both.

## Fields and dimensions

`fields: []`. One `proposed_field`, `project`, reused unchanged from the schema's own proposal with a single addition: an appellate artefact does not carry one bounded-work reference, it carries an **ordered pair** of them, and the relation between them is the fact. A single-valued string can hold either half but not the relation. Stated preference order: (a) R1c adjudicates canonical `project` once for the family and this row inherits it; (b) if the pair must be representable, express it as a relation between two accepted groups (P9), not as a field on a file; (c) no per-template mint of an appeal-shaped identifier key. If none is decided the row stays fieldless and loses nothing, because the pair is used as **activation evidence**, which needs no field to exist.

`dimension_order: []` under PR-6. The prose recommendation adds exactly one level to the schema's — proceeding tier, between matter and function — and inherits the schema's three binding rules unchanged, including the absolute one: a named third party (adverse party, appellant, witness, child, accused) may never be a folder level.

## Open questions carried

Four `NEEDS-JOSEPH` items ride on the JSON's `open_question` and are unchanged by this pass:

- **NJ-APP-1** — the ordered pair vs. single-valued canonical `project`. R1c must decide: cardinality on `project`, a P9 group-to-group edge, or nothing.
- **NJ-APP-2** — the contract has no way to say that two members of one `version_family` differ in sensitivity. Until it does, the safe reading is that the whole family takes the stricter half.
- **NJ-APP-3** — the record's frozen membership comes from an **index inside a document**, the only place in this family where an anchor is a parsed list rather than a repeated token. R1c and P9 must decide whether an index may establish membership at all, since the alternative (matter-reference grouping) is stated here as actively wrong.
- **NJ-APP-4** — appellate tier structures and vocabulary are jurisdiction-specific. This row defines no court list, tier catalogue or jurisdiction rule, and jurisdiction remains unavailable as a field or a dimension.

## For R1c — cross-row recommendations (no neighbour was edited)

1. **Reciprocity, five edges.** `collides_with` is symmetric and reciprocity becomes enforced post-migration. Three of the five targets have no node file yet (`law_practice.orders-and-judgments`, `law_practice.motions-and-briefs`, `law_practice.hearing-transcripts`); when they are authored they must carry the reciprocal entry with the mirrored signal. `law_practice.evidence-exhibits` and `legal.personal-legal-matters` exist today and should each gain a reciprocal entry. This row did not add them.
2. **Two candidate edges deliberately not added**, because the dispatch forbade new neighbours — both are argued inside this row's own text and a reviewer should decide them: **`law_practice.discovery`** (its production sets are stamped with continuous control numbers over member documents in exactly the same way a record is paginated — the row's own `never_alone` calls this "the collision the row must survive inside its own family"), and **`law_practice.trial-preparation`** (named in catalogue §12's own collides table: an appeal record physically reproduces trial-bundle documents, §6.9). The `discovery` pair in particular looks like a genuine missing `collides_with`.
3. **Kind mismatch on `also_holds_with`.** CONNECTION's edge table scopes `also_holds_with` to *schema ↔ schema only*, and this row is a template pointing at two schemas. The corpus already does this elsewhere (`business_operations.budget-forecast.json` carries a template-to-template entry), so either the table's scope line or the corpus needs reconciling. Flagged, not silently resolved — the entries were converted rather than deleted because the disjoint evidence they describe is real either way.
4. **The `law.` → `law_practice.` prefix drift.** The catalogue in `07-law-legal-practice.md` numbers rows as `law.*` while every node file is `law_practice.*`. Harmless once known, but it is what made three live neighbours look like dangling ids on first inspection, and it will do so again for the next agent.

## Self-verification

- `python3 -m json.tool planning/domains/nodes/law_practice.appeals.json` → parses. 27 top-level keys, unchanged from the draft.
- `git diff --stat` → 41 insertions, 8 deletions, confined to this one file. The 8 deletions are the 5 bare `collides_with` strings, the 2 bare `also_holds_with` strings, and the one repaired `depositions` line. No other field touched.
- 5 of 5 `collides_with` entries carry a `signal`; 2 of 2 `also_holds_with` entries carry a `signal`.
- Both quoted spans grep back verbatim out of `planning/00-database-agent-product-design.md` (checked programmatically with a substring test, including the curly apostrophe in the §6.9 span). No other new quotation was introduced.
- `§6.9` and `§4.9` were confirmed against `planning/01-product-design-structured.md` headings before being written as cites; only `§6.9` was used in the JSON.
- No threshold numbers, no handling classes, no invented statistics.
- Files written: `planning/domains/nodes/law_practice.appeals.json` (edited), `planning/domains/nodes/law_practice.appeals.research.md` (created). Nothing else — no roster edit, no neighbour edit, no shared file.

# clinical_practice.protocol-guideline — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Sources

Same authority stack as `clinical_practice.research.md`: `00-database-agent-product-design.md`
(quoted verbatim only — every quotation in the JSON and in this memo was machine-checked against the
file after whitespace and curly-quote normalisation), `ALIGNMENT.md`, `CONNECTION.md` +
`CONNECTION-EXAMPLES.md`, `_CONTRACT.md`, `canonical_fields.json`, `DECISION-BRIEF.md` (D1, D4, D6,
J-IND taken as ratified and not re-argued), `ROSTER.md` §4 + Appendix A, `roster.json` (every edge id
checked to exist), `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

Landed siblings read for key set and idiom: the `clinical_practice` schema row and all five landed
templates — `.patient-chart`, `.case-conference`, `.licensure-credentialing`, `.malpractice-incident`,
`.referral-correspondence` — plus the two salvaged drafts in this wave. Legacy row absorbed per
`ROSTER.md` Appendix A line 597: `med.clinical-protocol-guideline` (ROW).

## What it is for, and what it holds

Instruction **about a class of patients**, never a record **of** one. National and specialty
guidelines, local protocols and SOPs, care pathways and algorithms, order sets and blank proformas,
safety alerts and bulletins, prescribing and antimicrobial policy, patient-information leaflets, the
controlled-document register that tracks review dates, consultation drafts, and superseded versions.
The organizing anchor is the **governed document and its version** — a thing with an issuing body, an
approval, an effective date and a review date. Every other row in this family is anchored on an event
or a person; this one is anchored on a document.

## Node test — passes cleanly, and on the leg that usually fails

Detection signals differ sharply: a **four-slot governance band** (version / approved-by /
effective / review-due) repeating on every page, plus a **population-scope block that names no
individual**. No sibling carries either.

Privacy rules differ too, and in the direction nobody expects — **this is the only row in
`clinical_practice` marked `sensitivity: none`.** That is deliberate. A guideline is about a
population and names nobody; most are published. Marking it `potentially_sensitive` alongside a
dispensing extract would be dishonest, would dilute what the value means where it matters, and would
sweep the family's one genuinely safe branch into the protected path. The value is not read across to
any neighbour, and the JSON names Protected Records as the destination the moment a document turns
out to carry a real entry.

Dimensions do **not** differ and could not — `clinical_practice` declares no fields, so every template
on it has an empty `dimension_order` by contract, and **the node test's third leg is unsatisfiable for
every row in this family** (recorded identically in `clinical_practice.patient-chart.research.md`).
Recorded here rather than papered over.

## Files considered and rejected

- **`Sepsis screening tool BLANK v4.2.docx` / `Sepsis screening tool - COMPLETED - BROWN A.pdf`** —
  kept as a deliberate *pair*, because they are the same document twice and the blank-versus-completed
  reading is the row's whole collision with `patient-chart`. The completed one is kept precisely as a
  file this row must **not** claim.
- **`NICE NG51 full guideline.pdf`** — kept. It carries the row's most abusable signal, a published
  evidence grading, and the JSON says explicitly that the designation is a raw observation belonging
  to the issuing body and never becomes this product's own confidence or ranking.
- **`guidelines_library_backup.zip`** — kept, with one member path that looks like a completed return,
  to make the point that a manifest is not a content reading.
- **A textbook chapter** — rejected as a standalone example; it is Reading Inbox material and folded
  into the `needs_llm` guideline-versus-reading judgement instead.
- **A patient-information leaflet** — kept as a work type, rejected as an example: it is the same
  governance structure with a lay register, and a separate fixture would only repeat the guideline.
- **An audit tool** — rejected as an example. It is a form, and the blank proforma already carries
  that argument better.

## proposed_fields

**None.** Deferred to the schema row's single `subject_of_record` proposal, which this row reuses
rather than varying. Two keys were tempting and I minted neither. `issuing_body` looked safe — but
`institution` already exists in `canonical_fields.json` and would hold it, so minting a synonym is the
exact D6 failure the contract describes. `document_version` was tempting because it is this row's
anchor — but the universal `version_family` fact already covers version identity, and inventing a
second version concept inside a placeholder template is worse than leaving it as prose. Both are
recorded in `template.why` so R1c can act on them if fields ever land.

## Neighbours considered that did NOT get an edge

- **`medical.personal-health-records`** — a patient's own printed guideline or leaflet is medical-side
  material, but the pair is not confusable on evidence: this row's material names nobody at all, so
  there is nothing to mistake. Asserting an edge would be padding.
- **`government.public-health-administration`** — a national body issues guidelines, and the issuer's
  own file is a government record. Left unasserted at gist depth: the discriminator is holder-side and
  identical to the one already carried against `government.professional-regulator` on the
  `practice-administration` row, so a third assertion of the same shape adds nothing.
- **`academic.coursework`** — a downloaded guideline used as course reading is academic evidence, but
  the case is carried better by the `teaching-material` row's own academic edge.
- **`legal`** — a clinical policy is quoted in litigation, but that is
  `clinical_practice.malpractice-incident`'s disclosure world and already edged from there.

## NEEDS-JOSEPH

- **NJ-CP-13 · Is a superseded version a version-family member or a duplicate?** The universal
  version-family fact joins them and an ordinary deduplication courtesy would offer to retire the old
  one — but for a governed clinical document the superseded version is exactly what must stay
  retrievable, because what matters retrospectively is which instruction was in force on a given day.
  My position: a governance band should make a version family **non-collapsible**. That is a rule about
  a *kind* of document rather than a fact about any file, so it is not this row's to set.
- **NJ-CP-14 · Reciprocal owed against `research.lab-notebook-protocols`.** Authored one-way here;
  verified by grep that the landed `research.lab-notebook-protocols.json` does **not** name
  `clinical_practice` (and it is outside my five, so I did not edit it). A trial protocol is honestly
  both a governed clinical document and a research artifact, so R1c should decide whether the pair is
  a collision at all or a case for co-activation on the research side.
- **NJ-CP-13a (rides along, smaller).** `business_operations.policy-handbook` has landed and does not
  name `clinical_practice`; the edge authored here is therefore also one-way. I judge it a real
  collision — an infection-control policy governs clinical care *and* staff conduct — but the
  reciprocal is R1c's, and the honest resolution for a document that governs both is 00's shared-
  material policy rather than a forced single owner.

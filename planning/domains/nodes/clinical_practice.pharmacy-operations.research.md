# clinical_practice.pharmacy-operations — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Provenance of this row — SALVAGED, then verified

**This node's JSON was not authored fresh in this pass.** It existed as a structurally complete but
**unverified** draft left by an agent killed mid-wave, with no memo. I verified it line by line against
`_CONTRACT.md`, `CONNECTION.md`, and the landed siblings rather than trusting or discarding it, and I
now own it. What that verification covered and found:

- **Key set** — byte-identical order and membership to the landed
  `clinical_practice.referral-correspondence.json`. Pass, no change.
- **Every `00` quotation** — machine-checked verbatim after whitespace and curly-quote normalisation.
  **All pass, no change.**
- **Every edge id** — checked against `roster.json`. `clinical_practice.patient-chart`,
  `retail_hospitality.stocktake`, `clinical_practice.protocol-guideline`,
  `finance.small-business-bookkeeping`, `clinical_practice.malpractice-incident` all exist. Pass.
- **Residual names** — all six are §7.3 names. Pass.
- **`SOURCE_TYPES`** — all entries and all `file_examples.source_type` values are in P5's fourteen.
  Pass.
- **`facts_legal` keys** — all present in `canonical_fields.json` (`capture_year`,
  `camera_information`, `version_family`, `duplicate_family`, `sensitivity_status`, …). Pass.
- **`fields: []`, `proposed_fields: []`, empty `dimension_order`** — correct under D1 as narrowed,
  `_CONTRACT` rules 10 and 15, and PR-6. Pass.
- **Every `file_examples.must_not_conclude` carries a folder-path guard.** Pass.

**Changes I made to the draft: none.** It is the one of the two salvaged files that needed no repair.
What it was missing was this memo, and the reciprocity and node-test statements below, which the draft
could not carry on its own.

## What it is for, and what it holds

Running a **dispensary**. Prescriptions received, dispensing labels and history, the controlled-drug
register and its reconciliations, witnessed destruction and denaturing, stock counts and wholesaler
deliveries, batch/expiry/recall, formulary and substitution decisions, clinical and medication reviews,
dispensing-error and near-miss logs, cold-chain temperature logs, reimbursement returns, responsible-
pharmacist and SOP records, and inspection returns. The organizing anchor is the **medicine and its
custody chain** — which is what separates it from the chart, where the anchor is a person, and from a
shop's stock, where the anchor is a product with no accountability obligation.

## Node test — passes, on a structure nothing else has

The discriminating structure is the **signed, witnessed running balance**. Ordinary stock records do
not carry a reconciled balance, because ordinary stock is not accountable to anyone. That single
structure separates this row from `retail_hospitality.stocktake` (identical product/pack/count shape),
from `finance.small-business-bookkeeping` (identical invoice shape), and from `patient-chart` (same
subject, product, dose, date, seen from the other end of the chain).

Privacy differs from the schema default in degree rather than kind, but the degree is real and the
draft says so: dispensing systems export **by period rather than by person**, so one CSV can carry
thousands of people, and a single product name can disclose a condition its subject told nobody.

Dimensions do **not** differ and could not — `clinical_practice` declares no fields, so every template
on it has an empty `dimension_order` by contract, and **the node test's third leg is unsatisfiable for
every row in this family** (recorded identically in `clinical_practice.patient-chart.research.md`).
Recorded here rather than quietly satisfied. The draft's `template.why` makes the useful observation
that this row's *wanted* dimension is a function rather than a person, which makes it materially safer
than the chart's — that is a note for R1c, not a dimension.

## Files considered and rejected

- **`wholesaler invoice 884210.pdf`** — kept as the collision fixture and kept to be *declined*: drug
  names with no accountability structure is a purchase record, not a dispensary record.
- **`BNF chapter 4 - CNS.pdf`** — kept as the reference-versus-operation fixture, pointing at the
  sibling `protocol-guideline` row.
- **`dispensing_export_202603.csv`** — kept because the bulk case matters more here than anywhere else
  in the family.
- **`near miss log Q1.docx`** — kept for the continuum against `malpractice-incident`; the JSON is right
  that "the word error supports neither".
- **A patient's own repeat-prescription slip** — rejected: it is `medical.personal-health-records`
  material, and the holder-side boundary is already carried by the schema row and the correspondence
  row. A third assertion would be padding.
- **A veterinary dispensing label** — rejected here and handled from the other side: the
  `clinical_practice.veterinary-practice` row (also mine, this wave) states the edge and says a
  dispensary register is a dispensary register whichever species it serves.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal, reused rather than varied.
I reviewed the draft for silently-minted keys and found none. Two were tempting and are correctly
absent: `batch` (a value in an observation, not a fact this schema may hold) and `product`, which would
have been a new canonical key invented by a placeholder template.

## Neighbours considered that did NOT get an edge

- **`medical.personal-health-records`** — the holder-versus-subject boundary is genuinely present but is
  already asserted by the schema row and by `referral-correspondence`; asserting it a third time from
  here would restate rather than discriminate.
- **`business_operations.procurement-sourcing`** — a dispensary purchases, but the argument is the same
  one the `finance.small-business-bookkeeping` edge already makes.
- **`logistics`** — cold chain and delivery touch it, but the row has not landed and the temperature-log
  discriminator is already stated in `file_examples`.

## NEEDS-JOSEPH

- **NJ-CP-11 · May a recognised statutory accountability register be MOVED at all?** (Carried from the
  draft's `open_question`, and I endorse it.) A controlled-substance register is the one file class on
  this roster a person may be legally obliged to keep, keep unaltered, and keep in a stated place for a
  stated period. The product's normal courtesies — propose a destination, move on approval, deduplicate
  a family, represent an archive without extracting it — are all defensible against an ordinary file and
  all questionable against a statutory register. The question is *not* whether it is sensitive
  (Protected Records already answers that); it is whether such a register should be marked **not
  movable** ahead of any user policy. That is a decision about someone's legal obligations, so it is
  Joseph's, and it does not depend on whether `clinical_practice` ever gets field rows.
- **NJ-CP-11a · Reciprocity owed on four of this row's five edges.** Verified by grep and by file
  listing: `retail_hospitality.stocktake` and `finance.small-business-bookkeeping`'s counterpart rows
  either have not landed or do not name `clinical_practice`, and all are outside my five, so I edited
  none. R1c owes them. The two intra-family edges are in better shape: `protocol-guideline` (mine, this
  wave) **does** now state the reciprocal, and `malpractice-incident` already stated its own side of the
  policy-versus-incident boundary before this wave.

# clinical_practice.practice-administration — lab notes (template row)

**Depth: GIST** (J-IND). Honest map, not deep per-industry research. Not padded.

## Provenance of this row — SALVAGED, one real repair

**This node's JSON was not authored fresh in this pass.** It existed as a structurally complete but
**unverified** draft left by an agent killed mid-wave, with no memo. I verified it line by line against
`_CONTRACT.md`, `CONNECTION.md`, and the landed siblings rather than trusting or discarding it, and I
now own it.

**One real defect found and repaired — a fabricated quotation.** The draft's `falls_through_to` entry
for Temporary Screenshots carried, inside quote marks:

> “Temporary Screenshots may live under Photos/Temporary Screenshots and hold routine screen captures
> with no durable identity.”

That sentence **is not in `00`**. It is a plausible paraphrase of a real sentence, which is exactly the
failure mode `_CONTRACT.md` rule 2 names as having already happened once in this project ("A previous
review in this project invented three of four clauses inside quote marks. That must not recur.").
Replaced with the verbatim text:

> “Temporary Screenshots may live under Photos/Temporary Screenshots and hold screenshots that appear
> time-sensitive or remind the user of something but have no accepted project, trip, application, or
> event relationship.”

**That is the only edit to the draft.** Everything else verified clean:

- **Key set** — byte-identical order and membership to the landed
  `clinical_practice.referral-correspondence.json`. Pass.
- **All other `00` quotations** — machine-checked verbatim after normalisation. Pass.
- **Every edge id** checked against `roster.json`: `business_operations.organisational-records`,
  `hr.org-design-headcount`, `clinical_practice.case-conference`,
  `clinical_practice.referral-correspondence`, `clinical_practice.licensure-credentialing`,
  `government.professional-regulator` all exist. Pass.
- **Residual names**, **`SOURCE_TYPES`**, **`facts_legal`** keys against `canonical_fields.json`,
  **`fields: []` / `proposed_fields: []` / empty `dimension_order`** under D1-as-narrowed and
  `_CONTRACT` rules 10 and 15, **folder-path guard on every `file_examples` entry** — all pass.

## What it is for, and what it holds

Running a clinical practice **as an organisation**, in the deliberately **narrow** reading: clinic lists
and session plans, rotas and on-call, appointment and did-not-attend reports, registered-population and
coded-activity returns, recall and overdue-review lists, practice registration with a health regulator,
inspection reports and action plans, practice meeting records, SOPs, clinical-system searches and
exports, complaint-handling summaries, and business plans.

What is **not** claimed: the generic half of running a business — contracts, vendors, facilities,
payroll, staff policies — which belongs to `business_operations` and `hr` and is not clinical for being
held by a clinic. What **is** claimed is administration whose documents routinely **contain patients**,
which is a privacy fact `business_operations` does not carry.

## Node test — passes on privacy, and the row says so honestly

The discriminating structure is **clinical content inside an administrative form**: a session or clinic
list populated with people, a search over a registered population, a coded activity return, a
health-regulator registration of the practice as a care provider. Administrative *shape* alone —
agenda, rota, minutes, report, contract — supports `business_operations`, not this row.

Privacy rules differ from the schema default in the way the node test actually cares about: this row's
documents **look administrative and read as clinical**, and the false negative is the dangerous
direction. A rota read as ordinary office material is exactly how a populated clinic list reaches a
cloud prompt. That is why `sensitivity` is assigned to the whole row rather than per file.

Dimensions do **not** differ and could not — `clinical_practice` declares no fields, so every template
on it has an empty `dimension_order` by contract, and **the node test's third leg is unsatisfiable for
every row in this family** (recorded identically in `clinical_practice.patient-chart.research.md`).
Recorded here rather than quietly satisfied.

## The collision the assignment flagged — `business_operations`

I was told to watch for it, and the draft had already found it and drawn the row narrowly around it.
Verified and endorsed: the `collides_with` entry against `business_operations.organisational-records` is
correctly framed as standing for **the whole `business_operations` family**, named at the nearest
template because `collides_with` joins same-kind rows only (`CONNECTION.md` §5). The
`cleaning contract - renewal 2026.pdf` fixture is the right one — a practice's supplier contract is
`business_operations.contract-administration` material and being held by a clinic changes nothing.

I did **not** soften the counter-argument, which the draft states against itself in `open_question`:
the row survives only by being narrow, the narrowing is a judgement rather than a fact, and a practice
manager does not experience registration, rotas, contracts and premises as two worlds. That is
**NJ-CP-12** and it is a genuine fold question, not a formality.

## Files considered and rejected

- **`cleaning contract - renewal 2026.pdf`** — kept as THE collision fixture, to be declined.
- **`overdue reviews search 2026-03.csv`** — kept as the row's most sensitive shape: the search criteria
  themselves disclose a condition for every person listed.
- **`clinics.ics`** — kept as the `.ics` fixture. `calendar` is a `SOURCE_TYPE`, never a domain; it
  fires nothing on its own.
- **`practice meeting minutes 2026-02-03.docx`** — kept as the reciprocal of the landed
  `case-conference` row's own edge; a single significant-event item is not enough to move a business
  meeting.
- **A payroll summary and a staff handbook** — rejected as examples. They are `hr` material outright and
  giving them fixtures would have implied this row contests them; folded into `needs_llm` instead.
- **A patient complaint letter** — rejected: it sits on the `malpractice-incident` continuum, already
  edged from that row.

## proposed_fields

**None** — deferred to the schema row's single `subject_of_record` proposal, reused rather than varied.
I reviewed the draft for silently-minted keys and found none. `session` and `clinic` were the tempting
pair and are correctly absent; `institution` already exists and would hold the practice.

## Neighbours considered that did NOT get an edge

- **`business_operations.meeting-record`** — real overlap, but the `case-conference` edge already carries
  the meeting argument and the `organisational-records` edge already carries the whole-family argument.
  A third would be padding.
- **`finance.small-business-bookkeeping`** — a practice's accounts are bookkeeping, and that is exactly
  the generic half this row disclaims; asserting an edge would contradict the row's own narrowing.
- **`legal.leases-agreements`** — premises are a practice's real filing world and are equally real for a
  bakery. Disclaimed for the same reason.

## NEEDS-JOSEPH

- **NJ-CP-12 · Should this row exist at all?** (Carried from the draft's `open_question`; I verified the
  argument and endorse recording it unresolved.) FOR: the node test licenses a template whose privacy
  rules differ from its schema's default, and this row's do — its administrative documents contain
  third-party patients by construction, which no `business_operations` template assumes; and **two
  landed siblings (`case-conference`, `referral-correspondence`) already state `collides_with` against
  this id**, so it is load-bearing for their discriminators. AGAINST: the row survives only by being
  narrow, and every boundary case in its own file list resolves toward `business_operations` or `hr`.
  A one-sentence ruling settles it. Folding a row two landed rows point at is a roster edit, which this
  agent may not make.
- **NJ-CP-12a · Reciprocity owed on three edges.** Verified by file listing that
  `hr.org-design-headcount` and `government.professional-regulator` have **not landed** as node files,
  and `business_operations.organisational-records` has landed but does **not** name `clinical_practice`.
  All three are outside my five and I edited none. R1c owes the reciprocals — the
  `business_operations` one especially, since it is the same argument stated from the side that would
  absorb this row if NJ-CP-12 resolves the other way.

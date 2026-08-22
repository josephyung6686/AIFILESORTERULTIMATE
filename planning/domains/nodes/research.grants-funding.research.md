# research.grants-funding — lab notes (R1b)

Node kind: `template` on `schema_id: research`. **Not refused.** `launch: placeholder` (roster's flag,
kept). Output: `planning/domains/nodes/research.grants-funding.json`.

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span in quote
  marks in the JSON was grep-verified against this file before it was written (a scripted pass over
  all string values re-checked them afterwards: 0 unverified spans).
- `planning/01-product-design-structured.md` — only §3.9 (purpose), §3.10 (narrow dates), §3.11
  (domain-scoped schemas), §5.6 (purpose-defined packets), §5.7 (template library, and the sentence
  that makes a **metadata-only field** a legal template output). `00` wins on any conflict; nothing
  conflicted.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `CONNECTION-EXAMPLES.md` (examples 1–3).
- `planning/domains/roster.json` (confirmed id, kind, schema_id, neighbours; and used it as the
  only source of edge endpoints), `planning/domains/canonical_fields.json`,
  `src/evidence_shape/vocabulary.py` (`SOURCE_TYPES`).
- Sibling nodes already landed: `research.json` (the schema — its fields, rule families and
  never-alone list are what this row references rather than restates) and
  `research.project-workspace.json` (the refused default-template row — read to see exactly where
  the node-test bar sits).
- `planning/deferred-catalogues/` — **not consumed.** Recognition here names two rule families
  (an orgs gazetteer for sponsors, R4's content; explicit date patterns, R6's) without inventing
  any gazetteer contents or regexes.

## The node test, and why this row is not refused

`research.project-workspace` was refused because all three limbs matched the schema's default. This
row differs on all three, and would still pass on one:

1. **Detection signals** — the research schema row's deterministic list is manuscript/protocol/venue
   shaped. None of it fires on a solicitation, an Award Number slot, a personnel/fringe/indirect
   workbook, or a submission-portal OCR line. Worse than absent: the schema's `venue` rule family
   would actively mis-read a funding agency as a publication venue, which is why the JSON says
   outright that a funder is not a venue.
2. **Recommended dimensions** — `project → stage`, with `artifact_type` held **metadata-only**. That
   is a deliberate narrowing of the schema default (`project → stage → artifact_type`), argued from
   `00`'s packet rule: a submitted proposal is content-incoherent and purpose-coherent, and
   splitting it by artifact type scatters the narrative, budget, justification, biosketches and
   letters that went out as one submission.
3. **Privacy rules** — the schema's reason is human subjects and unpublished work; this row's
   dominant fact is *compensation* (named individuals beside salary, fringe and person-month
   columns) plus sponsor mail.

## Files considered and rejected

- **`results_batch07.xlsx`** — kept only as the *contrast* inside the `research.dataset-analysis`
  collision signal, not as a fixture of this row. It is that situation's file.
- **`PVA-RDP_manuscript_v7.docx`, `submission.zip` (the manuscript one)** — belong to
  `research.manuscript-publication`. `submission_package.zip` here is a different archive with a
  different manifest (narrative + budget + justification + biosketches + letters + DMP), which is
  what makes it this row's fixture rather than a duplicate of the schema's.
- **A published paper's acknowledgements line naming an agency** — not a file, but it is the reason
  the "sponsor name alone" never-alone entry exists. A funded paper is a manuscript, not a funding
  record.
- **An IRB protocol** — real in a proposal packet, but it is `research.ethics-compliance`'s fixture
  and carries that row's participant privacy rules.
- **A reimbursement receipt charged to an award** — genuinely ambiguous, and the reason
  `finance.receipts-expenses` was *considered* as a collision (see below). Dropped as a fixture
  because the receipt's own evidence is transactional; `00` already gives it a residual home.
- **An encrypted proposal archive** — would fall through to *Unsupported or Encrypted*, but that
  fallthrough is already on the research schema row and adding it here would restate rather than
  narrow.

## proposed_fields — one, and it is a *reuse* proposal

`sponsor` is recorded, and recorded as a question, not as a mint. The funding organization has no
home on the Research schema: `lab` performs the work, `venue` publishes it, `our_firm`/`client` are
the engagement pair, and `institution` — the closest existing key by meaning — is finance-scoped and
**not declared by the research schema**. The recommendation to R1c is explicitly (a) declare the
existing canonical `institution` on the research schema, over (b) minting `sponsor`; a second
organization key meaning what an existing key already means is the 574's failure mode.

The row **does not branch on it**. `dimension_order` names only `project` and `stage`, both declared
by the research schema and both `destination_eligible: true` on the canonical row. A dimension on an
undeclared field would open a tree level no fact can fill (`_CONTRACT` rule 8, CONNECTION §3) —
which is exactly the 566-finding debt on the legacy slices.

## Neighbours considered that did **not** get an edge

- **`finance` (the schema)** — the roster's `must_consider_neighbors` names it, but `collides_with`
  joins **same-kind** pairs (CONNECTION §5), so a template row cannot name a schema. The finance
  confusion is carried instead by `finance.small-business-bookkeeping` (proposed budget vs executed
  ledger). The research **schema** row already carries the finance collision at schema level, with
  the same discriminator (project-scoped vs account-holder-scoped), so nothing is lost.
- **`finance.receipts-expenses`** — real (award-charged reimbursements) but the discriminator is the
  same scope test already stated on the bookkeeping edge; a second edge would restate it.
- **`finance.student-financial-aid`** — rejected. Student aid is the applicant-side money situation
  and its confusion is with `applications.scholarship-fellowship`, not with a project grant.
- **`research.manuscript-publication`** — no collision. A cover letter to an editor and a cover
  letter to a program officer look alike, but `venue` versus a solicitation identifier separates
  them cleanly, and both live on the same schema, so a mis-split costs a folder level, not a field.
- **`career.recruiting`** — a biosketch resembles a CV. Recorded per-file as
  `also_schema: "career"` on `Biosketch_2026.docx` rather than as an edge, because career is a
  field-less placeholder (PR-6): co-activation changes what is protected and searchable, not what is
  extracted.
- **`legal.practice-matter-file`** — subaward agreements are contracts. Left alone: the confusing
  evidence item would be a signature block, and this row claims no signature-based signal.

## Where CONNECTION overrode the dispatch prompt

The prompt's edge table offers `also_holds_with` to any node ("one file may legally carry both
schemas"). CONNECTION §5 restricts it to **schema ↔ schema**. CONNECTION wins, so
`also_holds_with` is `[]` here and the note in the JSON says why. The two genuine co-holds
(career on a biosketch, medical on a human-subjects proposal) are recorded per-file and on the
schema row respectively.

`parent_id` is `null` and was never authored (PR-5: R1b never authors it). `shares_field` is not
authored anywhere — it is derived from the canonical references.

## Notes on the recognition list

- The tempting false file is **`Grant_Wilson_recommendation_letter.pdf`**. It is worth flagging
  loudly: `00`'s word-boundary rule (the MIT-inside-submit case) does **not** save it, because
  `Grant` is a clean word-boundary match. Only the absence of a sponsor, a solicitation and a budget
  does. That is the same failure one level up — substring → role.
- **Currency columns alone** are never-alone here for the same structural reason: invoices, ledgers,
  consulting SOWs and event budgets all have them.
- Activation ≠ grouping is live on three fixtures: `Budget_Justification.docx`, `Biosketch_2026.docx`
  and `Award_Notice_signed.pdf` all carry `group_without_copying_facts: true`. They join a packet
  neighbourhood; none of them acquires the project fact from a sibling filename or from packet
  membership.
- No numeric threshold, no confidence score and no handling class appears anywhere in the node.
  `sensitivity` is `potentially_sensitive`, which is `00`'s phrase.

## NEEDS-JOSEPH (this node only)

**NJ-grants-1 · Sponsor-first or project-first?** A holder with awards from three agencies navigates
by sponsor — the agency sets the report formats, the deadlines and the rules. A holder with one
long-running project navigates by project. This row recommends `project → stage` **only because no
organization key on the research schema carries the funding role**, not because project-first is
obviously right for a funded lab. Two parts:

1. May the existing canonical `institution` be declared on the Research schema so this situation can
   branch on the funder (recommended), or is a `sponsor` key role-split against `lab` wanted?
2. If a sponsor dimension lands, does it **lead**, or does `project` still lead with sponsor held as
   metadata?

This decides someone's real folder structure, so it is not resolved here.

**NJ-grants-2 (small, for R1c rather than Joseph)** · The research **schema** row's
`falls_through_to` lists Reading Inbox, Independent Records and Unsupported or Encrypted, but omits
*Review Later* and *Temporary Screenshots* — and fixtures on this row (and on
`research.project-workspace`) fall through to both. The schema row's residual list looks incomplete.

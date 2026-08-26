# hr.payroll-benefits-administration — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: hr`, `launch: placeholder`, `parent_id: null`.
Output: [`hr.payroll-benefits-administration.json`](hr.payroll-benefits-administration.json).
No prior draft existed; both files are new.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, read in full. It set the six
  requirements this memo is audited against and the J-DEPTH standard.
- `python3 planning/domains/dispatch/make_prompt.py hr.payroll-benefits-administration` — the
  stamped assignment: row metadata, node test, research procedure, output shape, done-when list.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` for
  `payroll`, `Protected Records`, `purpose-coherent`. **`00` never uses the word "payroll".** That
  single negative result decided `provenance: proposal` and `design_cite: null` for this row, and it
  is why nothing here is dressed as design. Four spans were taken verbatim and re-verified with
  `grep -qF` (below).
- `planning/domains/nodes/hr.json` — the schema anchor, read in full. Its stated default template,
  its `work_types[0]`, and its file example `March 2026 payroll register - FINAL.xlsx` are the whole
  substance of the charge against this row.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named by the
  brief. Two things were taken from it as method rather than content: the discipline of an empty
  `proposed_fields` with the tempting keys argued down in prose, and the pattern of a fixture whose
  correct outcome is a **refusal to file** (its keystore; my bank batch file).
- `grep -rl "hr.payroll-benefits-administration" planning/domains/nodes/` — returned nine files, all
  under `construction_property`. Read only the matched spans. `construction_property.timesheet` is a
  **refused** row whose refusal routes its pay reading here; `construction_property.site-diary` and
  `.variation-claim` each authored a one-way boundary at this row. Reciprocated below.
- `planning/domains/roster.json` — every edge endpoint checked mechanically (10/10 resolve).
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — checked mechanically (12/12 file examples, and
  every member of `file_kinds.source_types`).

Not read, deliberately: other R1b rows "for context", and the `.research.md` of the hr anchor. The
anchor's JSON was decisive on its own; opening the memo would not have changed a verdict.

## THE CHARGE — the strongest case that this row should not exist

I put the case at its worst before writing anything, because on this row it is unusually strong.

**Charge 1 — it is a work_type value of its own schema, verbatim.** `hr.json` `work_types[0]` reads
"payroll register, remittance, employer filing, or benefits administration record". That is not a
paraphrase of this row's name; it is this row's name, already enumerated as a *value* inside the
schema that would host it. The brief and ALIGNMENT both say work types are values, never nodes. If
that is all this row is, it is the 574's original error with a modern id.

**Charge 2 — it is a document type.** "Payroll register", "remittance advice", "P60", "W-2",
"contribution schedule" are all names of documents. The refused `construction_property.timesheet`
was killed for exactly this — "a document type wearing a situation's clothes" — and it is not
obvious from the outside that "payroll" is different in kind from "timesheet".

**Charge 3 — it duplicates the schema's own fixture.** The register the row would be built around is
already `hr.json`'s first file example, with its finance collision already stated at schema level.

**Charge 4 — it duplicates a neighbour.** `finance.payroll-received` holds payslips;
`finance.small-business-bookkeeping` holds a small employer's payroll journal;
`hr.compensation-planning` holds pay. Three rows already touch payroll-shaped bytes.

**Charge 5 — a lifecycle stage.** "Payroll run" could be read as a stage of the employment lifecycle
that `hr.onboarding-offboarding` and `career.employment-records` bracket, and stages are not nodes.

### Defeating the charge

Charges 3, 4 and 5 fall to evidence and are dealt with in the boundary section. Charges 1 and 2 are
the real ones, and they are defeated by the same observation, which I state as **inference**:

> Payroll is the only situation on the hr schema that is **periodic, closed and externally
> obligated**. Every other hr row is event-driven and internal — a grievance runs until it ends, a
> survey wave happens once, onboarding is per person, a review cycle is annual and self-contained
> inside the organisation. Payroll produces the *same family of documents on a fixed cadence*, each
> occurrence of which must **reconcile within itself**, and roughly half of each occurrence's
> members are addressed to **parties outside the organisation** — a revenue authority, a pension
> provider, an insurance carrier, a bank, a court.

That is a description of an organizational situation, not of a document. It is what makes the
difference from `construction_property.timesheet`: that refusal found that after splitting the
contractual, statutory and site readings out of a timesheet, "the residue has no detection signal of
its own, no dimension order distinct from the diary's". Here the residue after splitting is not a
residue at all — it is a closed recurring set with its own joint slot structures (§ recognition), its
own spine (the run), and its own protected payload (§ privacy). A work_type value cannot have a
reconciliation obligation, and a document type cannot have a counterparty.

**Verdict: `refuse_node: false`.** Argued in full below, all three legs.

## The node test, all three legs

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The hr schema's
default template, quoted from `hr.json`'s own `template.why`, is: *work type or named people
programme first; then workforce unit or cohort when the corpus genuinely spans several; then people
cycle; and only under explicit user policy a pseudonymous personnel case.* Its default detection is
the seven-signal set on `hr.json`; its default privacy rule is that employee-identifying content is
protected before any cloud step.

### Leg 1 — detection signals differ. **PASSES, and this is the load-bearing leg.**

The hr default's payroll-adjacent signal is "a payroll register or workforce census spreadsheet
whose headers jointly describe multiple employees, organisational units, employment status or
movement, and employer-side totals" — one signal, framed as *a census of people*. This row does not
inherit that framing; it replaces it with four joint slot structures the schema default does not
contain, none of which is about the workforce as a population:

1. **Gross-to-net structure** — per-person identity slot repeated across rows, beside labelled
   earnings, deduction, employer-contribution and net slots, beside a run identifier, closing on
   control totals. The census signal has no deduction/net split and no control-total closure; the
   closure is the reconciliation obligation showing up as evidence.
2. **Employer obligation structure** — employer reference + contribution period + amount payable to
   a named external authority. Nothing on the hr schema default reaches outside the organisation.
3. **Provider-facing schedule structure** — a scheme reference beside per-member pensionable pay,
   with employee and employer contributions in **separate labelled columns**. The split of one
   amount into two payer roles is a discriminator that exists nowhere else on the schema, and it is
   what separates an employer's schedule from an individual's benefits statement.
4. **Disbursement instruction structure** — payee + routing/account slot + amount, under a header
   with a count and a hash total. This signal exists to trigger a **refusal**, not a placement.

Detection differs in kind, not in wording. That alone satisfies §2.

### Leg 2 — recommended dimensions differ. **PASSES conditionally; the condition is declared.**

The schema default is `work type → workforce unit → people cycle`. This row recommends
`people cycle (the pay run) → work type`, with **workforce unit dropped from the standing levels**.

The reason is evidential. A pay run is a closed set: register, disbursement instruction, filing
receipt, payslip batch, approval correspondence and reconciliation are content-incoherent and
purpose-coherent in exactly `00`'s sense, and the run is what makes each member intelligible —
`00`'s own parent-dimension argument (Homework 3 is meaningless without the course) read across.
Leading with work type instead scatters one run's closed set across five sibling folders and makes
the reconciliation that is the entire point of the run invisible. Workforce unit is dropped because
a run is organisation-wide by construction: a department column exists **inside** the register and
is a cut of it, never a parent of it, so promoting it opens a level most of this material cannot
fill.

The condition, stated rather than smoothed: under PR-6 the hr schema declares no canonical field
rows, so **both** dimension orders are empty in the JSON and this comparison is prose against prose.
That is honest, and it is why the row does not rest on this leg. Recorded as **NJ-HRPAY-4**.

### Leg 3 — privacy rules differ. **PASSES.**

The hr default protects *employee-identifying content*. This row concentrates two further protected
payloads that are not employee-role data at all, and one refinement:

- **Third-party financial credentials.** A disbursement instruction is a list of *other people's*
  bank account and routing numbers held by the user's organisation. `00`'s Protected Records
  description covers it directly, naming "account statements" and "credentials" as sensitive
  isolated material that "must not cause filenames or content to be exposed in model prompts". The
  correct outcome for that file is **protection in place, not filing** — the same shape of answer
  `finance.crypto-assets` reaches for a keystore.
- **Government identifiers about other people**, on the statutory filings and year-end statements.
- **A refinement the schema default does not state: on payroll, the deduction lines are more
  disclosing than the amounts.** A court-order deduction discloses debt or family proceedings; a
  statutory-pay line discloses illness or a birth. The sensitive fact is not "this person earns X".

Two consequences follow that the schema default does not imply: a **parallel-run or migration
extract inherits the live posture** (it carries real employees and real bank details however the
filename is labelled), and **benefits elections stay protected regardless of aggregation**, because
dependant counts and plan tiers re-identify in small populations.

Nothing was invented to keep the row: `fields: []`, `proposed_fields: []`, no new key, no new
dimension, no threshold, no handling class.

## Files considered and rejected

Requirement 3. These are the tempting false positives, each with why it is not this row's evidence.
Four are kept **in** the JSON as file examples precisely because their correct answer is "not mine".

- **`Payroll journal - March 2026.csv`** — kept as the collision fixture (§ below).
- **`Salary benchmarking 2026 - Customer Ops.xlsx`** — kept. Pay-shaped columns, no disbursement.
  `hr.compensation-planning`'s.
- **`variance check.xlsx`** — kept as the sparse fixture (§ below).
- **`Screenshot 2026-03-27 at 09.14.11.png`** — kept, as media discipline: OCR of numbers that
  already exist in a labelled slot in the register beside it, and the absence of EXIF proves
  nothing.
- **An invoice from the payroll bureau (`ADP invoice INV-88213.pdf`)** — rejected outright, and it
  is the most seductive miss on the row: it carries the word payroll, a period, and a supplier who
  exists only because payroll exists. It is a **supplier invoice**. Its facts are vendor, invoice
  number and amount owed by the organisation; not one employee appears. It belongs to
  `business_operations` / `Receipts and Confirmations`. Taking it would make this row "everything
  with the word payroll on it", which is the failure the charge predicted.
- **The employee handbook's pay and benefits chapter** — rejected. A governing policy is
  `business_operations`', as the hr anchor's own collision already says. Only an employee-specific
  acknowledgement crosses over, and even then not to this row.
- **An employment contract stating a salary** — rejected. A salary figure in a contract is a *term
  agreed*, not a *payment made*. `career.employment-records` / `legal`.
- **A commission or bonus schedule** — rejected as a file example, kept as a `needs_llm` case. Names
  against amounts with a period; genuinely ambiguous. It becomes this row's only when it lands as a
  line in a register or carries deductions.
- **An expense reimbursement batch** — rejected for the same shape, resolved differently: expenses
  are reimbursed *through* payroll in some organisations and *around* it in others. The
  discriminator is whether deductions were applied.
- **A timesheet / labour allocation sheet** — rejected as a file example and handled as a
  reciprocal boundary instead (§ below), because two landed neighbours already argued it.
- **A pension provider's annual statement addressed to one employee** — rejected. Provider-issued,
  individual-addressed, single. `finance.payroll-received` or the individual's own records.
- **A payroll software licence key or system configuration export** — rejected. Software artifacts.
  `Unsupported or Encrypted` handles the unreadable ones without this row.

## Reciprocal boundaries

Requirement 4: both directions, same fixture named on both sides. All seven are written into
`collides_with` in that form; the two that most needed argument:

**`finance.payroll-received` — shared fixture `P60 2025-26 - J Patel.pdf`, byte-identical on both
sides.** This row must not take a lone earnings statement, year-end certificate or benefits
statement merely because an employer issued it. That row must not take a **numbered series** of the
same certificate sharing one employer reference, a batch payslip PDF, or any register with more than
one person's row. The discriminator is **cardinality and custody of the run**, not the document
type: one person's copy is received; the batch that produced it is administered. This is why the
JSON's `P60` example carries `must_not_conclude: employer-side activation from the document alone;
the SERIES is the evidence` — the fixture is a trap in the direction of my own row, not away from it.

**`construction_property.site-diary` — shared fixture, a labour allocation sheet of names against
hours.** This edge was authored **at** this row and is reciprocated here for the first time. That
row takes the site reading (hours against trades, cost codes, one day, one site); this row takes the
pay reading and only when rates, deductions or a pay period are present. Its memo's NJ item asks
R1c to confirm the split rather than inherit it; this row confirms it from the other side and claims
nothing more. `construction_property.timesheet` stays refused — this row does not want it back.

The other five, in brief and both-directional in the JSON: `finance.small-business-bookkeeping`
(people rows vs account rows), `finance.tax-filings` (whose liability the form reports),
`hr.compensation-planning` (executed vs proposed), `career.employment-records` (output of a run vs
proof of one's own history), `identity.credentials-passwords` (both refuse the bank file; neither
grows a tree to hold it).

## The collision fixture

**`Payroll journal - March 2026.csv`.** It is exported by the payroll system, in the same operation
as the register, with the same period in its filename, from the same directory, by the same person.
Every positional signal points here.

It is not this row's evidence. **What discriminates it: there is no employee identity slot anywhere
in the file.** Its rows are chart-of-accounts codes with debits and credits and a balancing total —
it is the *accounting consequence* of a pay run, and it belongs to `finance.small-business-
bookkeeping`. This is encoded as a `never_alone` ("a chart-of-accounts code beside a debit and
credit pair") so that the tempting file trips it, and it is the same fixture named on the
bookkeeping side of the collision.

## Sparse-file discipline

`variance check.xlsx` is this row's `HW 3.pdf`: two unlabelled numeric columns and a difference
column, sitting in the directory with the March register and the reconciliation email, naming
nothing inside itself. It is `group_without_copying_facts: true`, its `facts_legal` is universals
only, and its `must_not_conclude` refuses both the copied period fact and the directory-as-evidence
inference — `00`: "A session should never be treated as proof of topic". The archive, the bank file
and the screenshot carry the same flag for the same reason.

## `proposed_fields` — empty, and why the two temptations were refused

- **A `pay_period` key.** Refused: `people_cycle` is already the hr schema row's proposal and its
  stated example is *literally* "March 2026 payroll run". Minting a period synonym is the exact
  move the dispatch forbids.
- **A counterparty key** (tax authority, pension provider, carrier, court). This is the real gap and
  the honest answer is that it cannot be closed from a leaf. It is the finance schema's `institution`
  role; a template may only branch on a field its own schema declares; and minting `payroll_provider`
  or similar is how the overnight pass produced thousands of private field names. Recorded as
  **NJ-HRPAY-2**, encoded as optional branch (a) in `template.why`, and proposed nowhere.

`proposed_context_terms` (eighteen) are candidates for R6, marked PROPOSED. `00` states the
pattern-plus-context *shape* for course codes only; it does not list these and this row does not
pretend otherwise.

## Neighbours considered that did not get an edge

- **`hr.onboarding-offboarding`** — a new joiner's first run and a leaver's final pay are real
  handoffs, but the *evidence* never collides: a joiner tracker's columns are process tasks and
  completion states, a register's are amounts. Two rows, one handoff, no shared discriminating slot.
- **`hr.workforce-analytics`** — a payroll cost report is analytics' evidence once it aggregates
  away the per-person rows, which is exactly this row's discriminator working in reverse. No edge
  needed; the gross-to-net signal already excludes it.
- **`business_operations`** — the budget line labelled salaries is already `never_alone` on the hr
  schema row and adding a second claimant would give one evidence item three homes.
- **`clinical_practice`** — occupational health touches statutory sick pay, but this row sees only
  the *pay calculation*; the certificate that justifies it is clinical and the hr anchor's
  schema-level `also_holds_with` already covers the co-activation.
- **`identity.core-documents`** — government identifiers appear on the filings, but as a slot on
  someone else's record rather than as the document itself. Handled in `sensitivity_why`, not as an
  edge.
- **`also_holds_with`: empty by contract.** It is declared at the schema row and the hr schema
  already carries business_operations, finance, clinical_practice and legal. Lawful dual membership
  is expressed through `also_schema` on individual file examples, drawn only from that declared
  list. A template must not widen its schema's edges from a leaf.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All four `00` spans re-verified with `grep -qF` against `planning/00-database-agent-product-design.md`:
  "A session should never be treated as proof of topic"; "account statements"; "credentials";
  "must not cause filenames or content to be exposed in model prompts"; plus "Unreadable, encrypted,
  corrupted, or unsupported files should retain basic metadata" behind the Unsupported-or-Encrypted
  route. **No `00` quotation in this node is fabricated or paraphrased inside quote marks**, and the
  row claims `provenance: proposal` because `00` never mentions payroll.
- Every `file_examples.source_type` in `SOURCE_TYPES` (12/12); every `file_kinds.source_types`
  member likewise.
- Every `collides_with.domain` and `role_split.domain` resolves on the roster (10/10, verified
  against `roster.json` `nodes[].domain_id`).
- Every `falls_through_to.template` and every `falls_through_if_inactive` is one of §7.3's nine
  residual names (3/3 and 12/12).
- `fields`, `proposed_fields` and `also_holds_with` are empty, each with a note saying why.
- No threshold, score, count of evidence or handling class appears; `sensitivity` is
  `potentially_sensitive` only. Digits in the file are filenames, years inside fixture names and
  form names.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/` and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-HRPAY-1 — does BENEFITS ADMINISTRATION belong on this row at all?** The row's name assumes
  it. The join is real and evidential, not nominal: benefits elections become payroll deduction
  lines. But its cadence is a **plan year**, not a pay period; its documents are issued by
  **carriers**, not by the employer; and its enrolment data carries household and health-adjacent
  attributes that pay data does not. Alternatives: (a) keep them together with plan year as an
  optional branch — what the row recommends; (b) split a benefits row, at the cost of two rows
  sharing one detection-signal set; (c) route benefits enrolment to Protected Records and keep only
  carrier invoices here. **Recorded, not resolved.**
- **NJ-HRPAY-2 — the external counterparty has no key.** A remittance, contribution schedule or
  carrier invoice has a stable external party that is its natural first dimension, and no hr key can
  hold it. Options: promote a shared counterparty key; license cross-schema reference for
  co-activated files; or accept that the provider-facing subset cannot open its natural first level
  (today's answer). This row proposed nothing.
- **NJ-HRPAY-3 — the bureau case.** When a bookkeeper or payroll bureau holds registers, bank files
  and filings for a **client** employer, the same bytes are simultaneously this row's employer-side
  record and `finance.small-business-bookkeeping`'s engagement deliverable, and the custodian is
  neither employer nor employee. The collision defers rather than deciding. R1c should say whether
  **custody** or **subject** governs — the answer generalises well beyond payroll.
- **NJ-HRPAY-4 — leg 2 is prose measured against prose.** PR-6 leaves both dimension orders empty,
  so the dimension difference this row argues is currently unrealizable. The row stands on legs 1
  and 3 without it. If R1c rules that an unrealizable dimension difference cannot count, every hr
  sibling resting chiefly on leg 2 should be re-examined **together** rather than one at a time.

## Recommendations to R1c (cross-row, not acted on)

1. **Reciprocals owed to this row.** `finance.payroll-received`, `finance.small-business-bookkeeping`,
   `finance.tax-filings`, `hr.compensation-planning`, `career.employment-records` and
   `identity.credentials-passwords` do not yet name this row. All six edges here are written in
   both-directional form so the reciprocal can be pasted without re-litigation.
2. **`construction_property.site-diary`'s open item 2** asks R1c to confirm the site/pay split of the
   labour allocation sheet rather than inherit it. This row now confirms it from the pay side.
3. **`construction_property.timesheet`'s NJ item** flags a sole trader's own hours-per-job record as
   homeless, noting that "hr.payroll-benefits-administration presumes an employer". Confirmed: this
   row does presume one, and should not be stretched to cover a one-person business's own hours.

# finance.payroll-received — lab notes (R1b)

Roster row: `kind: template`, `schema_id: finance`, `launch: placeholder`,
`provenance: inference`.

Verdict: **node accepted** (`refuse_node: false`).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. It is the authority for the
  observation/fact split, Finance's four legal keys, conservative date roles, field-versus-value
  discipline, template ordering, group non-propagation, residual names and the safety boundary.
  Curly double quotes in the JSON are reserved for verbatim spans from this file and are checked
  mechanically after authoring.
- `planning/01-product-design-structured.md` — the relevant renderings only: facts and schemas
  (§3), template/tree design (§5), residuals (§7.3), and privacy (§8.4). It is a locator; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`,
  `planning/domains/CONNECTION.md`, and `planning/domains/CONNECTION-EXAMPLES.md` — node test,
  schema/template split, closed edges, grouping firewall, field identity, browse-only parent and
  safety activation.
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`, and
  `src/evidence_shape/vocabulary.py` — exact assignment, canonical roles and types,
  destination eligibility, roster endpoints and the closed `SOURCE_TYPES` tuple.
- `planning/overnight/council/DECISION-BRIEF.md` — D6 keeps internal keys in `snake_case`; D4
  makes jurisdiction a value and never a dimension; D2 keeps the authoritative sensitivity
  classification in P7 rather than this catalogue; J-IND requires honest placeholder breadth and
  gist-level research without field inflation.
- Landed nodes read but not changed: `finance.json`, `career.json`,
  `career.recruiting.json`, `career.employment-records.json`,
  `finance.personal-records.json`, `finance.tax-filings.json`,
  `finance.investment-brokerage.json`, `finance.small-business-bookkeeping.json`,
  `finance.receipts-expenses.json`, `finance.loans-mortgage.json`,
  `finance.student-financial-aid.json`, `finance.insurance-personal.json`, and
  `finance.subscriptions-utilities.json`. Five already point to this row; this node reciprocates
  all five and adds the evidence-backed employee-side versus employer-run bookkeeping seam.

Primary sources were used to test that the fixtures resemble records actually issued in more
than one jurisdiction. They do not override the product design, and none of their wording is
attributed to `00`:

- [GOV.UK — Payslips: employee rights](https://www.gov.uk/payslips) distinguishes printed and
  electronic payslips and identifies before/after-deduction earnings, changing deductions and
  hours as normal payslip contents. It supports the gross/deduction/net anchor and the photo,
  electronic statement and portal-delivery fixtures.
- [GOV.UK — Running payroll: Payslips](https://www.gov.uk/running-payroll/payslips) separately
  describes gross wages, deductions, net wages, hours, employee identifiers, tax codes and
  cumulative tax-year amounts. This supports the rule that a year-to-date column can appear on a
  normal pay statement but does not, by itself, fill `tax_year`.
- [IRS — About Form W-2, Wage and Tax Statement](https://www.irs.gov/forms-pubs/about-form-w-2)
  identifies a jurisdiction-specific employer-to-employee wage-and-withholding statement and its
  corrected variant. It supports the year-end and correction fixtures while D4 keeps the form
  name as a `record_type` value rather than a field.
- [Australian Taxation Office — Accessing your income statement online](https://www.ato.gov.au/businesses-and-organisations/hiring-and-paying-your-workers/single-touch-payroll/single-touch-payroll-for-employees/accessing-your-income-statement-online)
  describes an employer-reported online income statement containing year-to-date wages,
  withholding and employer superannuation, updated when the employer pays and later finalized for
  tax use. This is the concrete cross-jurisdiction evidence for the payroll-history/tax-packet
  overlap and for avoiding a hard-coded form-name vocabulary.

## Committed history and what survived it

`git log -S` ties this roster row to commit `13bff36`: a Finance template for pay stubs, income
statements and employer year-end forms; Career is the required neighbour; Protected Records is the
required residual. The emitted row preserves that exact assignment.

The superseded catalogue's closest employee-side entry was `career.payroll`, introduced in
commit `9dcfe72` and spelling-normalized in `1082384`. Its useful bottom-up harvest was the
recurring employer-to-employee record, pay-period/gross-to-net recognition, employer-first order,
year-end summaries, corrections and the offer/invoice/tax collisions. Its private schema did not
survive:

- `employer` maps to the Finance `institution` role only when the employer/payer is explicitly
  the issuer of the pay record. A payroll bureau in producer metadata is not substituted for it.
- `payroll_document_type` maps to canonical `record_type`.
- `pay_period` maps to the already-shared `record_period` proposal, not a payroll-only key.
- `tax_year` already exists canonically and requires its own labelled tax-year role.
- `pay_date`, `employee_identifier` and `currency` remain observations/search evidence here.
  One placeholder template is not allowed to enlarge the long-term field language for values that
  do not improve its destination order.

The same legacy pass had an employer-side `biz.payroll-employer` entry: registers, journals,
remittances and run-wide returns covering many employees. The current roster does not preserve a
separate row for it. `finance.small-business-bookkeeping` is the closest landed organizational
situation, so this node uses an employer-wide payroll register as a negative fixture and adds a
collision edge instead of silently absorbing the business record.

## Node test — why this is not Finance's default template

The row differs on both load-bearing limbs:

- **Detection differs.** Finance's default is a broad union over statements, receipts, tax forms,
  pay stubs, policies and other money records. This row requires the employer/payer and
  employee/recipient roles plus either a labelled pay period and gross-to-net structure, or an
  explicit employer annual earnings structure. It also rejects offers, direct-deposit forms,
  bank credits, plan statements and employer-wide registers that remain valid Finance or Career
  records.
- **Dimension order differs.** Finance defaults to
  `institution -> account_type -> record_type`. Payroll omits `account_type`, because ordinary pay
  statements are not account records, and recommends
  `institution -> tax_year -> record_type`. Employer first separates concurrent or successive
  jobs; explicit tax year keeps a long history navigable; document kind is meaningful only inside
  that context. A missing tax year flattens rather than being guessed.
- **Privacy does not manufacture the distinction.** This row inherits the Finance safety posture.
  Its node licence comes from detection and ordering, not from inventing a stronger handling class.

That produces genuine v1 value even at placeholder depth: a confirmed employer history can stay
flat, split by explicitly supported year, or split by statement/correction/annual-summary values.
It never creates one folder per pay period.

## Bottom-up file coverage

The JSON contains seventeen concrete fixtures:

- recurring native PDF pay statement;
- photographed printed payslip with camera evidence and OCR;
- payroll-portal screenshot with OCR;
- sparse pay-statement-ready email that may group without fact copying;
- off-cycle bonus advice;
- corrected statement linked to an original by `version_family`;
- annual earnings summary with an explicit tax-year slot;
- jurisdiction-specific employer year-end form at the tax-packet seam;
- populated pay-history CSV;
- archive manifest inspected without extraction;
- offer-letter Career collision;
- direct-deposit authorization account-record collision;
- retirement-plan contribution confirmation collision;
- employer-wide payroll-register bookkeeping collision;
- recurring payday calendar false positive;
- salary-deposit bank alert false positive; and
- password-protected payroll-looking PDF.

The set covers `text_document`, `spreadsheet`, `image`, `ocr`, `email`, `calendar`, `archive` and
`opaque_binary`. It includes labelled versus sparse evidence, capture co-activation, archive
grouping, a file with zero Finance facts, several Finance-sibling negatives, and an unreadable
file. No extension, amount, organization, date, recurrence, identifier or filename can fire alone.

## proposed_fields

One proposal: `record_period` (`string`, direct only from an explicit labelled covered interval,
destination-ineligible).

Why the need is real: the pay period is the evidence that distinguishes recurring pay actually
reported from compensation merely offered, a bank credit after the fact, or an annual aggregate.
It also joins an original statement to its correction and a statement series to a pay-history
export. `creation_date` is a file-version timestamp, while `tax_year` is a tax role. Neither can
store a fortnightly or monthly covered interval without lying.

Why it is not a private payroll key: `finance.subscriptions-utilities` independently found the
same cross-record gap and proposed the same broad key. This row repeats that proposal deliberately
so R1c can see corroborating file evidence; it does not mint `pay_period`, `billing_period`,
`statement_period` or a jurisdiction-specific synonym. The key stays out of `dimension_order`, and
every recognition and grouping rule still works if R1c leaves periods as raw evidence.

## Edges and reciprocity

- `career.recruiting` — reciprocal now. An offer states future compensation under a proposed
  role; payroll reports pay actually made through pay-period and gross-to-net structure.
- `career.employment-records` — reciprocal now. Contracts, onboarding, benefits, reviews,
  compensation-change letters and separation records are job lifecycle records; recurring pay
  statements are the Finance neighbour even though both name the same employer.
- `finance.personal-records` — reciprocal now. A bank/account period plus balance structure is not
  an employer/employee pay period plus gross-to-net structure. The direct-deposit and salary-credit
  fixtures exercise both directions.
- `finance.tax-filings` — reciprocal now. Ordinary per-period pay statements are distinct from
  returns, assessments and filing acknowledgements. Employer year-end forms are the deliberate
  seam discussed below rather than an excuse to duplicate facts.
- `finance.investment-brokerage` — reciprocal now. An employer contribution line on a payslip is
  not a plan account, holding or custodian-issued contribution confirmation.
- `finance.small-business-bookkeeping` — new one-way edge for R1c reciprocity. One employee's
  received statement is distinct from the holder's multi-employee payroll run, journal and
  remittance records.

`also_holds_with` is empty because CONNECTION permits it only between schemas. Real co-activations
are represented by schema evidence and the fixtures' `also_schema` values (`photos`, `career`,
`identity`). Group overlap remains P9 data: a year-end income form can participate in a payroll
history and a tax packet without writing facts across either group.

`role_split` is empty because that edge lives only between canonical field keys. The crucial
roles are expressed with existing vocabulary and observations: `institution` is the labelled
employer/payer for a pay record; the Finance schema's proposed `account_holder` is the employee or
recipient; a payroll bureau remains producer metadata.

## Neighbours considered that did not get an edge

- **`finance`** — `schema_id`/`uses_schema` is the join. A template cannot collide with its own
  schema.
- **`career`** — the specific recruiting and employment-record templates carry the evidence-backed
  same-kind collisions. A direct template-to-schema edge would violate CONNECTION.
- **`finance.loans-mortgage`** — pay statements often join a loan-application packet, but that is
  P9 multi-membership, not same-evidence confusion. The pay statement remains payroll and the loan
  application remains a loan record; neither copies facts onto the other.
- **`finance.student-financial-aid`** — a campus job and an aid package can share a school and
  money, but a work-study pay statement retains payroll structure while an aid record has award,
  eligibility, disbursement or student-account structure. The school and amount alone support
  neither, so an edge would add topic similarity rather than a new discriminator.
- **`finance.receipts-expenses`** — a reimbursement line embedded in payroll is not a purchase
  receipt. A standalone reimbursement or deposit confirmation without payroll structure falls
  through to Receipts and Confirmations rather than making the whole transaction template collide.
- **`finance.insurance-personal`** — insurance and pension deductions are line items, not policies.
  Policy/coverage structure is already required by that node, so the shared provider or premium
  amount is handled by `never_alone` without another edge.
- **`finance.subscriptions-utilities`** — both recur and use `record_period`, but recurrence is not
  same-evidence confusion. Provider/service-account/usage structure and employer/gross-to-net
  structure are independently clear.
- **`photos.screenshot-captures` and `photos.scanned-documents`** — a screenshot or photograph of a
  payslip legitimately carries Photos and Finance evidence at once. Capture metadata and OCR
  content are disjoint, so a collision would erase the multi-schema rule.

## Other files considered and rejected

- blank payslip templates and payroll-software marketing pages — form shape without a filled
  employer/recipient/pay event is reference material, not a record received;
- compensation calculators, salary surveys and job-posting salary ranges — amounts without a
  payroll relationship or payment event;
- timesheets and hours logs without an issued pay calculation — Career employment records or
  business working records, depending on whose corpus owns them;
- invoices issued by a contractor — holder-as-vendor role, handled by consulting/bookkeeping, not
  employer-to-employee payroll;
- bank statements and deposit notifications showing salary credits — represented by the bank-alert
  negative fixture; net deposit is not gross-to-net evidence;
- direct-deposit forms, tax-withholding elections and benefits enrollments — instructions sent to
  the employer, not statements received after payment;
- retirement-plan, health-insurance and equity statements merely referenced by deduction lines —
  neighbouring records, not payroll copies;
- payday reminders and payroll-provider contact cards — calendar/contact source records, not proof
  of pay; and
- unreadable files with payroll words in their names — universal metadata only until content can
  be examined safely.

## Contract tension and NEEDS-JOSEPH

The dispatch serializes a template's schema pointer as `schema_id`; `_CONTRACT.md`'s older R0
wording calls it `uses_schema`. The roster, generated output skeleton and every landed R1b node use
`schema_id`, so this row follows the live shape and notes the naming tension rather than inventing a
second pointer.

There is also a real boundary between two landed assignments. This roster explicitly includes
employer year-end forms in payroll received; `finance.tax-filings` explicitly includes payer-issued
year-end information forms in the tax-year packet. The product's group model can preserve both
relationships without copying facts, but CONNECTION makes `also_holds_with` schema-only while the
two template rows already carry `collides_with`. The edge can distinguish ordinary pay-period
statements from returns/assessments, but it cannot alone express one statutory year-end form kept in
two accepted groups.

- **NJ-fin-payroll-1 · Shared interval field:** adopt one destination-ineligible
  `record_period` for explicit pay, billing, statement and coverage intervals, or leave all such
  intervals as raw evidence. This template works either way.
- **NJ-fin-payroll-2 · Year-end form ownership:** may one employer-issued statutory year-end form
  be a member of both the employer payroll-history group and the tax-filing packet, with one
  physical home decided later, or must P10 designate one of the two templates as its sole owner?
  The former matches `00`'s overlapping-group model; the current template-edge vocabulary does not
  state it directly.

Neither question blocks safe v1 detection, protection, fact extraction or the shallow payroll
recommendation.

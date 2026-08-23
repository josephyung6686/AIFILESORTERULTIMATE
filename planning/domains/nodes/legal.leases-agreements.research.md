# `legal.leases-agreements` — R1b lab notes

Date: 2026-08-22  
Roster row: `legal.leases-agreements`, `kind: template`, `schema_id: legal`, `launch: safety`  
Outputs: [`legal.leases-agreements.json`](legal.leases-agreements.json) and this file

## Result and node test

The node is **not refused**. It earns a template row without fields or dimensions because its
detection and privacy behavior differs materially from the broad `legal` default:

- the default Legal schema spans instruments, proceedings, court material, estate documents and
  counsel correspondence; this row requires an **agreement lifecycle** — presented parties,
  reciprocal duties or a grant of use, agreement-version evidence, and supporting amendments,
  schedules, signing records or notices;
- its main false-positive problem is not generic Legal vocabulary but distinguishing the holder's
  own agreement from a bill, account packet, employment record, equity instrument, practitioner
  file, association record, research data agreement or blank/public form;
- it needs the roster-specific residual fork between `Protected Records` and `Independent Records`,
  with privacy classification and user policy applied first; and
- fifteen same-kind collision seams are concrete enough to state as evidence-item mutexes, and all
  fifteen reciprocate already-landed rows after a final concurrent-state recheck.

The current `dimension_order` is empty. That does not make the template identical to the default:
CONNECTION's node test permits a template whose detection or privacy rule differs even when the
fieldless schema makes every current Legal template share an empty dimension list.

### Alternatives considered before authoring

1. **Refuse and merge into the broad `legal` default.** Rejected. The default correctly catches a
   will, summons, deed, counsel email and lease as Legal, but it cannot express the narrower
   holder-role boundary, the signed-agreement lifecycle, the `Independent Records` option, or the
   fifteen evidence-backed template collisions.
2. **Restore the legacy split between `legal.contracts` and `legal.lease`.** Rejected. The current
   roster deliberately assigns one situation, and the two old rows differed by proposed private
   fields rather than by a field vocabulary the Legal schema actually declares. Keeping one row
   treats lease, service and employment agreement as values and lets property, career and Finance
   templates carry the real organizational seams.
3. **Restore the legacy fields** for party, agreement kind, premises, dates, governing law,
   signature state and reference. Rejected. D1 as narrowed / PR-6 forbids Legal field rows, D4
   forbids a jurisdiction destination dimension, none of those concepts is in
   `canonical_fields.json`, and a template cannot copy a private schema to save its id.
4. **Split one child template per agreement type.** Rejected. Lease, NDA, service agreement,
   employment agreement and amendment are values, not nodes. Where one has genuinely different
   organization, the roster already supplies the neighbor — employment records, loans, equity,
   study abroad, research ethics, vehicle records and others.
5. **Chosen:** one fieldless safety template whose distinct value is agreement-shaped recognition,
   lifecycle grouping, residual ordering and high-precision collision discipline.

## Sources actually used

### Binding project sources

- `planning/00-database-agent-product-design.md` — read completely from line 1 through line 286.
  It controls observations versus facts, safety-domain ordering, local-first privacy, archive
  manifests, grouping without propagation, sparse protected records, residual names, dimensions,
  extension abstention and the prohibition on paths as facts.
- `planning/01-product-design-structured.md` — all 1,912 lines read as a locator and operational
  rendering. Its tables are not authority; `00` wins.
- `planning/prompts/ALIGNMENT.md`, `planning/domains/_CONTRACT.md`, and
  `planning/domains/CONNECTION.md` — read completely. The consequences here are: no Legal field
  rows; template collisions join templates; schema co-activation is not authored here;
  `file_kind_plausible` is never-alone; membership never propagates facts; residual names are
  closed; and safety activation does not unlock a deep template.
- `planning/domains/CONNECTION-EXAMPLES.md` — all eight fixtures read. The passport, `.ics`, sparse
  homework, multi-schema abstract and insurance fixtures were the most relevant.
- `planning/domains/roster.json` and the exact prompt regenerated with
  `planning/domains/dispatch/make_prompt.py legal.leases-agreements` — confirmed the exact id,
  name, kind, schema, safety launch, two required schema neighbors, two required residuals and two
  owned paths.
- `planning/domains/canonical_fields.json` — all 37 keys read. There is no Legal agreement,
  counterparty, premises, instrument, execution or term key. No key was proposed or borrowed.
- `src/evidence_shape/vocabulary.py` — the closed fourteen-member `SOURCE_TYPES` list and the
  reliability vocabulary. Every serialized source type was checked against it.
- `planning/domains/nodes/legal.json` and `legal.research.md` — read completely. The schema is a
  fieldless safety placeholder; its empty dimension recommendation, privacy boundary, Legal/Finance
  and Legal/Career schema joins, and broad instrument detector are inherited rather than copied.
- The thirteen non-Legal landed rows that already name this id in `collides_with`, together with their
  relevant fixtures and research notes: `academic.study-abroad`,
  `career.employer-side-hiring`, `career.employment-records`, `finance.cap-table-equity`,
  `finance.hoa-residents-association`, `finance.household-property`,
  `finance.insurance-corporate`, `finance.loans-mortgage`, `finance.personal-records`,
  `finance.small-business-bookkeeping`, `finance.subscriptions-utilities`,
  `finance.vehicle-records`, and `research.ethics-compliance`.
- The three Legal sibling nodes landed while this row was being verified. Their JSON and relevant
  research sections were re-read before the final edge pass. `legal.personal-legal-matters` and
  `legal.estate-planning` both reciprocate this id with compatible discriminators.
  `legal.practice-matter-file` deliberately records this id as a nonedge, so the provisional
  one-way collision drafted while that sibling was absent was removed rather than forcing a
  contradiction into the connected graph.
- The superseded `legal.contracts` and `legal.lease` rows in
  `planning/domains/05-finance-legal-admin.{json,md}`, plus the practitioner/party distinction in
  `planning/domains/07-law-legal-practice.{json,md}`. Their bottom-up examples were useful history;
  their private fields, old ids, thresholds and jurisdiction choices were not carried forward.
- `planning/overnight/council/DECISION-BRIEF.md` — the ratified D1, D4 and D6 results: Legal fields
  stay unwritten, jurisdiction is never a field or destination dimension, and canonical keys use
  `snake_case`.

No deferred catalogue value, gazetteer, regular expression or sensitivity class was consumed.
The sensitivity-detector catalogue was not used to assign a class; this row ends at
`potentially_sensitive` and the `legal` schema activation boundary.

### Current official structural sources

These sources were used only to verify that the file shapes are real. They are jurisdiction- and
program-specific. No jurisdictional validity rule, form number, notice period, signature rule,
retention rule, deadline, regex or threshold was serialized.

- [GOV.UK — Assured periodic tenancies: tenancy agreements](https://www.gov.uk/assured-tenancy-agreements-a-guide-for-landlords)
  confirms that a tenancy record concerns legal terms, occupation and rent, while also showing why
  a signature cannot be a universal formation test: the current England guidance expressly covers
  written and oral arrangements. This source caused the JSON to say agreement-shaped record rather
  than valid contract.
- [HUD — Model Lease for Subsidized Programs](https://www.hud.gov/sites/dfiles/OCHCO/documents/90105a.pdf)
  supplies a concrete labelled document shape: landlord and tenant roles, dwelling unit, term,
  rent, deposit, conditions, attachments and signatures. Only that structure was generalized.
- [GSA — Leasing guidance and lease/exhibit templates](https://www.gsa.gov/real-estate/leasing/leasing-guidance)
  confirms that a lease lifecycle can include a principal lease plus exhibits and supplemental
  requirements, and that a proposal/template is distinct from an executed lease.
- [Acas — The right to a written statement](https://www.acas.org.uk/what-must-be-written-in-an-employment-contract)
  distinguishes an employment contract from the narrower written statement that summarizes core
  terms. It grounds the Career collision and prevents the product from treating one document title
  or signature as the whole legal relationship.
- [Acas — Written statement worker template](https://www.acas.org.uk/templates-for-written-statements/written-statement-worker-template)
  supplies concrete employer/worker, start, pay, hours, leave, notice, collective-agreement and
  signature slots for the employment fixture. The JSON stores none of them as Legal facts.
- [HM Land Registry — Practice guide 82: electronic signatures](https://www.gov.uk/government/publications/electronic-signatures-accepted-by-hm-land-registry-pg82/practice-guide-82-electronic-signatures-accepted-by-hm-land-registry)
  documents a platform-produced completion certificate or audit report containing signing-event,
  completed-field and technical audit information. It grounds the email and JSON support records,
  while its process-specific scope is why those records never prove universal validity or effect.
- [CMS — Data Use Agreement form and instructions](https://www.cms.gov/cmsforms/downloads/cms-r-0235.pdf)
  supplies the named-provider/recipient, permitted-use, custodian, security-condition and signature
  structure behind the research-ethics collision. No CMS-specific term was encoded.

## Bottom-up file set

The JSON carries 29 concrete files across all nine claimed source families:

- **central agreements:** a residential tenancy agreement, lease addendum, consulting services
  agreement, ISP service agreement, employment agreement, mutual NDA and vehicle lease;
- **specialized dual-schema agreements:** a SAFE, research data-use agreement, study-abroad
  housing agreement, account-opening packet, settlement/release and mortgage loan agreement;
- **packet and sparse support:** a tenancy ZIP manifest, signing-completion email, signing audit
  JSON, lease reminder `.ics`, photographed signature page, OCR portal screenshot and rent schedule
  workbook;
- **neighbor false friends:** association covenants, a condition report, utility statement,
  consulting invoice, insurance declarations, vehicle renewal and employer-custody agreement; and
- **hard abstentions:** a blank lease form, generic terms of service and an unreadable binary whose
  only clue is its filename.

The set deliberately includes both native documents and capture/OCR forms, one manifest-only
archive, machine-structured signing evidence, calendar and email context, a sparse spreadsheet, an
opaque file, records that genuinely carry another schema, and records whose most tempting signal is
explicitly refused.

### Files considered and rejected from the serialized examples

| Considered | Why it was not kept as another example |
|---|---|
| `LICENSE.txt` in a repository | The broad `legal` schema already owns this corpus-scale boilerplate false positive and its `code` collision. The agreement template carries the same boilerplate never-alone rule without duplicating the schema fixture. |
| `Will and Testament.pdf`, `Power of Attorney.pdf`, `Advance Directive.pdf` | These are `legal.estate-planning` fixtures. Their signatures and witness blocks are used only as the sibling collision discriminator. |
| `Summons - Small Claims.pdf`, counsel correspondence and a court order | These are `legal.personal-legal-matters` or the broad Legal default, not reciprocal agreements. |
| a contract redline, issues list, negotiation playbook and closing checklist held by counsel | Those are practitioner-side apparatus for `legal.practice-matter-file`; a party's final copy belongs here. |
| oral-agreement audio or a recorded signing call | There may be no durable agreement document, and `00` permits transcript analysis only under an explicit privacy and compute policy. `audio_video` was not format-fished into this row. |
| a landlord, counterparty or counsel `.vcf` | Contacts are privacy/search material, not agreement evidence or a destination proposal basis. |
| a slide deck summarizing deal terms | A presentation about a deal is not the agreement. No `presentation` source type was added merely for coverage. |
| a public sample contract from a regulator or law firm | Same lesson as the blank form and terms-of-service fixtures; the two serialized negatives already cover it. |
| a handwritten note reading we agreed | Too little structure for deterministic recognition. It remains bounded LLM/user review and no formation conclusion. |

## Fields, work types and dimensions

- `fields: []` — templates reference their schema and do not copy it; `legal` declares none.
- `proposed_fields: []` — inventing a party, agreement, premises, date, jurisdiction or execution
  field would reverse D1 through a child row. The open question records the need without proposing a
  key.
- `role_split: []` — party/counterparty, employer/employee and provider/customer are genuine role
  distinctions, but `role_split` joins canonical field keys and none exists here.
- `dimension_order: []` — there is no destination-eligible Legal key. The hypothetical finding
  remains prose only: agreement/relationship identity would have to precede amendment, schedule,
  notice or termination role; time is not the default spine.
- `work_types[]` contains values only. It does not smuggle a Legal field or create child nodes.

Every `file_examples[].facts_legal` item is either one of the universal canonical keys or empty.
No party, address, agreement kind, execution state, effective date, term, jurisdiction, obligation,
breach or enforceability claim is serialized as a fact.

## Recognition and legal-status boundary

The strongest deterministic shape is deliberately conjunctive:

1. party roles presented in the document;
2. operative terms expressing reciprocal duties or a grant of use; and
3. completed execution or final-document evidence tied to the same document version.

That shape activates an **agreement record and protection**, not a legal opinion. The node never
concludes formation, validity, enforceability, delivery, current effect, renewal, expiry, breach,
compliance, ownership or authority to sign. Official sources show why a universal signature rule is
unsafe: written and oral arrangements coexist; a written statement may not be the whole employment
contract; and electronic-signing requirements vary by document and institution.

An unsigned but complete-looking document, a click-through record, an email exchange, a
multilingual or degraded scan, or unclear holder role is therefore `needs_llm` or user review. The
model may identify document shape from cited stored evidence and must return unknown on legal status.

## Grouping firewall

The accepted group is an agreement **lifecycle**, not a propagation mechanism. A recognized lease
can anchor an amendment, inventory, rent schedule, reminder, email or signing certificate. Those
sparse members do not inherit parties, premises, dates, rent, status or sensitivity details from the
anchor. The ZIP manifest likewise supports a candidate packet without proving the contents of its
members.

The row also preserves multi-membership. An employment agreement may sit in Career and Legal groups;
a vehicle lease in Finance and Legal; a study-abroad housing agreement in the exchange neighborhood
and Legal; a mortgage agreement in lending and Legal. Template collision edges reserve shared
evidence items; they are not file-level mutexes and do not select a physical home.

## Privacy and residual ordering

The ordering is explicit because the roster hint and `00` otherwise look contradictory:

1. Legal safety activation occurs locally.
2. P7 classification and the user's policy run before any model, connector or placement path.
3. If protected, the only offered residual is `Protected Records`, and names, signatures, addresses,
   agreement terms and filenames do not enter a cloud dossier or general summary.
4. Only if policy allows release and no broader group exists may a user-approved
   `Independent Records` residual be offered for the durable isolated agreement.
5. Both residuals remain optional and authorize neither a move nor a model call.

This row sets only `potentially_sensitive`. It does not name or assign any P7 class, invent a
release rule, infer that ordinary agreements are low-sensitivity, or treat encryption as permission
to inspect.

## Collision audit

`collides_with` is used only for same-kind evidence-item confusion. Schema co-activation remains on
the schema rows, and `also_holds_with` is empty because CONNECTION permits that edge only between
schemas.

| Neighbor | Discriminator | Status at authoring |
|---|---|---|
| `academic.study-abroad` | exchange academic roles/course transfer vs housing parties/occupancy terms | reciprocal landed edge |
| `career.employer-side-hiring` | holder as employee party vs employer custody of another person's agreement | reciprocal landed edge |
| `career.employment-records` | employer/employee relationship structure vs non-employment agreement subject | reciprocal landed edge |
| `finance.cap-table-equity` | equity issuance/conversion/grant terms vs non-equity subject | reciprocal landed edge |
| `finance.hoa-residents-association` | member account/governance/admin structure vs reciprocal operative agreement | reciprocal landed edge |
| `finance.household-property` | inventory/receipt/inspection/improvement record vs operative lease | reciprocal landed edge |
| `finance.insurance-corporate` | policy/period/limits reporting existing coverage vs clauses requiring coverage | reciprocal landed edge |
| `finance.loans-mortgage` | principal/interest/payoff vs use-for-rent/deposit | reciprocal landed edge |
| `finance.personal-records` | account descriptor/fee/rate structure vs general reciprocal agreement | reciprocal landed edge |
| `finance.small-business-bookkeeping` | invoice/ledger/reconciliation structure vs obligations/execution | reciprocal landed edge |
| `finance.subscriptions-utilities` | running account period/usage/bill state vs service obligations/execution | reciprocal landed edge |
| `finance.vehicle-records` | official vehicle ownership/registration/service structure vs agreement clauses | reciprocal landed edge |
| `research.ethics-compliance` | study participant/data subject matter vs unrelated personal/commercial subject | reciprocal landed edge |
| `legal.personal-legal-matters` | dispute/proceeding apparatus vs agreement lifecycle | reciprocal landed edge |
| `legal.estate-planning` | testamentary/delegation/end-of-life function vs reciprocal agreement | reciprocal landed edge |

### Neighbors considered without an edge

- **`career.consulting-client-engagement`** — its statement-of-work fixture is genuinely both Career
  and Legal on disjoint evidence. Client/scope supports the engagement; party/execution structure
  supports Legal. There is no shared evidence item that needs a mutex once those signals are kept
  separate, and the schema-level Career/Legal join already exists.
- **`finance.receipts-expenses`** — rent receipts and one-off payments are transactional, but the
  sharper agreement-versus-transaction seams already sit on household property, subscriptions and
  bookkeeping. Adding a fourth Finance edge for the same amount/date temptation would duplicate
  the discriminator.
- **`photos.scanned-documents` and `photos.screenshot-captures`** — a capture can carry Photos and
  Legal schemas on separate evidence; source/capture status is not a competing agreement template.
  The image and OCR fixtures retain `also_schema: photos` and the EXIF abstention rule instead.
- **`identity.core-documents`** — a signature or address does not make an identity credential, and
  this row has no credential fixture. The broad `legal` schema already owns the official-instrument
  versus identity-document collision.
- **`code.software-project`** — generic licences and terms are refused here, but repository-root
  structure is the broad Legal schema's code collision, not an executed-agreement lifecycle seam.
- **`medical.personal-health-records`** — medical terms inside an employment, insurance or service
  record can trigger protection on their own evidence. No one evidence item distinguishes this
  agreement template from a personal health record, so no mutex was authored.
- **`legal.practice-matter-file`** — the sibling's landed research deliberately treats agreements
  as content that may sit inside a practitioner packet and expresses holder-role ambiguity through
  its reciprocal collision with `legal.personal-legal-matters`. Once practitioner custody and
  matter apparatus are kept separate from this row's party/execution evidence, the executed PDF
  may remain a packet member without a shared evidence item forcing a mutex. Its explicit nonedge
  was honored; no one-way collision was retained.
- **`legal` and `career` / `finance` schemas** — wrong endpoint kind for `collides_with`.
  `schema_id` supplies the Legal join, and schema-level `also_holds_with` carries lawful
  co-activation.

## Prompt/contract tensions handled explicitly

- The prompt says a template reuses its schema fields; the Legal schema is intentionally empty.
  `_CONTRACT.md` rule 10 and CONNECTION PR-6 therefore require empty `fields`,
  `proposed_fields`, `dimension_order` and `role_split`. No private substitute was invented.
- The prompt presents `also_holds_with` in every output shape; CONNECTION restricts it to
  schema-to-schema. The array is empty and per-file co-activation appears as `also_schema`.
- The roster name says signed agreements. Official structural sources show that signature is not a
  universal formation test and that some arrangements may be oral or broader than one written
  record. The current template stays document-bound, treats execution as observation, and records
  scope widening as a Joseph question rather than answering it.
- The roster hint says isolated signed PDFs otherwise use `Independent Records`; `00` makes Legal a
  safety domain and names legal forms under `Protected Records`. The JSON applies privacy first and
  leaves the final global rule open rather than assuming all signed PDFs are releasable.
- `parent_id` stays null and browse-only. No activation, field or dimension is inherited from a
  parent.

## NEEDS-JOSEPH — this node only

1. **Document-bound scope.** Keep this id narrowly about signed or otherwise finalized written
   records, or widen it later to oral, click-through and correspondence-formed arrangements? The
   current safe answer is document-bound plus review; the product never decides contract formation.
2. **Future Legal vocabulary and visible structure.** If D1 is lifted, which shared concepts may
   identify an agreement/relationship and artifact role, and may any become destination dimensions?
   A counterparty, premises or matter label can disclose protected material even when file contents
   remain local. The current row authors none.
3. **Protected versus Independent residual.** After Legal activation, may P7/user policy ever permit
   an isolated ordinary agreement to be offered under `Independent Records`, or should every
   Legal-activated agreement force `Protected Records`? The current provisional ordering implements
   the roster hint without weakening the safety gate, but Joseph should ratify the branch.

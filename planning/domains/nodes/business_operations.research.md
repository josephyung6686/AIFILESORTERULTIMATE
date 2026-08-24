# `business_operations` — lab notes (schema row, deepened to J-DEPTH)

Row kind: **schema**. Launch: **placeholder** (`fields: []`). Verdict: **kept, not refused.**

This is the schema row for a 25-row family — this row plus **24 templates**, the second largest on
the roster. Those 24 siblings measure their node test against the default template stated here, so
this memo is written on the assumption that **a sibling author reads this file before writing
theirs**: the posture, the vocabulary, the default template and the seams are stated explicitly
rather than left to be inferred from the JSON.

**Status of this file.** The row was first written under the retired J-IND *gist* standard and
carried a 7.8KB memo. J-DEPTH (ratified 2026-08-24) overrules that clause. The JSON was
**verified-but-shallow, not untrusted** — its 40 quotations were machine-checked verbatim and its key
set matched the landed siblings — so it was **deepened, not rewritten**. What was preserved and what
was added is itemised under *Salvage and deepening* below.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in
  `business_operations.json` was grep-verified verbatim against it. The spans that did the real work
  on this row, and what each decided:
  - the **template-library sentence**, which is the reason this row's `design_cite` is `null`:
    *"covering common organizational situations such as academic programs, university applications,
    recruiting processes, client engagements, research workflows, financial records, travel, legal
    matters, creative projects, software repositories, personal administration, and photo
    collections."* Read it carefully. It names *client engagements* (which the roster gave to
    `career.consulting-client-engagement`), *financial records* (`finance`), *legal matters*
    (`legal`), and *personal administration*. **It does not name an organisation's own running
    record anywhere.** That absence is the single most important fact about this row and is argued
    in *Provenance* below.
  - the **collector prohibition** — *"A folder should not become a collection point for everything
    produced by the same person or organization."* — and the template validator's paired
    prohibitions, *"create meaningless one-child levels"* and *"use an author or organization merely
    as a collector"*. These three sentences are why `organization` is proposed
    `destination_eligible: false` despite being the field-shaped hole this family most obviously has.
  - the **multi-role token sentence** — *"A university name alone should not create a group because
    Columbia can appear as an authoring school, course provider, target institution, employer,
    research venue, or merely a cited organization."* This is the load-bearing sentence for the
    whole family. It is written about a university; reading it across to a **company** name is an
    **inference**, and it is marked as inference wherever it is used. It is also the sentence the
    family's one refusal turns on.
  - the **dimension-order rule** — *"For document and record domains, project, function, or subject
    usually comes before time because putting year first scatters related work across calendar
    folders."* — which fixes `time_first: false` for the family and constrains where `fiscal_period`
    may sit if R1c mints it.
  - the **purpose-coherence sentence** — *"The documents are content-incoherent but
    purpose-coherent."* — which is the licence for this family's most characteristic grouping
    reason, the governance pack.
  - the **topic/purpose distinction** — *"Topic answers what a file is about, while purpose answers
    what the file was for."* — which is the only clean way to separate a real operating record from
    a downloaded example of one.
  - the **abstention sentence** — *"Correct abstention is a successful outcome because the
    product’s goal is reliable organization, not maximum file movement."* — invoked more often on
    this row than on any other in the catalogue, because the career/hr/finance/legal seams here
    genuinely do not resolve on many real files.
  - the **role-split pair** — *"A consulting document may mention the author’s firm and the client
    organization."* — the source of `our_firm` / `client`, and the reason the **third** role
    (supplier / buying side) is visibly missing.
  - the **table sentence** — *"Tables matter because resumes, forms, applications, invoices, and
    administrative documents often place their most useful information in cells rather than body
    paragraphs."* — the licence for the management-financial-table detection signal.
  - the **recommendation sentence** — *"The system recommends an order based on the domain template,
    but the user can reverse, remove, add, or flatten dimensions."* — which is why an `organization`
    level seeded false is not a level denied to the user.
  - the residual-library definitions, for all six fallthroughs.
- `planning/domains/_CONTRACT.md` — rules 1–3 (provenance, no fabricated quotes, no numbers), 6
  (residuals out of this namespace), 8 (snake_case; a dimension may only branch on a declared
  field), 10 (no field rows on placeholder schemas), 11–15 (`kind`, closed edge vocabulary,
  `is_safety_domain`).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation (step 2 never-alone, step 5
  protective ordering), §5 closed edge vocabulary and invariant 2, §6 field identity, §9 failure
  mode 6.
- `CONNECTION-EXAMPLES.md` — fixture 5, the `.ics` fixture, which is why `Weekly leadership
  sync.ics` is a fixture here and why `calendar` is treated as a source type contributing a
  file-kind signal only.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema’s fields and dimension_order"* …
  *"it is the schema’s default template."* Stating the default template explicitly here is the
  service this row owes its 24 siblings.
- `planning/domains/canonical_fields.json` — the canonical keys. Confirmed that **no key holds
  either concept this row proposes**. **No key minted.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D4, D6, PR-2, PR-6 taken as
  ratified and not re-debated.
- `ROSTER.md` §4 and Appendix A — this family absorbs slice 11's 45 legacy ids as 20
  `business_operations.*` rows plus 10 `hr.*` rows, with `corp.regulatory-filings`,
  `corp.compliance-audit` and `soft.tech-compliance-evidence` arriving from other slices.

### Landed neighbours read before writing (and not touched)

- `creative.json` + `creative.research.md` — the J-DEPTH **schema anchor** written for exactly this
  purpose, and the calibration target for this file's shape: the argued three-leg node test, the
  default-template paragraph written *for the siblings*, the rejected-files table, and the named
  collision fixture.
- `career.json`, `finance.json`, `legal.json` — the three landed launch schemas this family
  overlaps hardest. All three read in full before the boundary section was written.
- `career.consulting-client-engagement.json`, `finance.small-business-bookkeeping.json`,
  `finance.payroll-received.json`, `finance.cap-table-equity.json`, `legal.leases-agreements.json`,
  `legal.practice-matter-file.json` — the landed **template** rows that contest actual bytes with
  this family.
- `construction_property.json` — shares the `organization` proposal and the professional-world
  posture; its `business_operations` edge is quoted and accepted below.
- `business_operations.organisational-records.json` — this family's one refusal, and the source of
  the principle generalised in *The never-alone principle, for all 24 siblings*.

### Contract conflict noticed, not silently resolved

`role_split` appears in the landed corpus in **three** shapes: `{domain, our_field, their_field,
why}` (`finance.json`), `{field, other_field, other_domain, why, provenance}`
(`business_operations.json`, `research.*`, and now `creative.json`), and `neighbor`-spelled variants
(`academic.*`, `career.*`). This row keeps the shape it already carries, which a landed sibling also
uses. It is a **catalogue-wide normalisation for R1c**, not a defect of this row — filed as NJ-BO-3.

---

## Provenance: why this row is `proposal` and its `design_cite` is `null`

This must be stated plainly because 24 siblings inherit it.

`00` never names an organisation's own running record as a template situation. The template-library
sentence quoted above enumerates twelve situations and this is not one of them. Every adjacent
family on this roster *is* named there — client engagements, financial records, legal matters,
recruiting processes, personal administration. **This family is the largest one on the roster with no
sentence of its own in the source of truth.**

Two honest readings, and this row takes the second:

1. `00` deliberately scoped the product to an individual's corpus, and an organisation's own record
   is out of scope. Under this reading the family should not exist and its material belongs to
   `career` (the individual's copy), `finance`, `legal`, and the residual library.
2. `00`'s list is explicitly *"such as"* — an open enumeration of common situations, not a closed
   grant — and its own worked examples repeatedly touch organisational material (the consulting
   role split is an organisation's document; *"administrative documents"* in the table sentence are
   organisational forms). Under this reading the family is licensed by the product's own examples
   even though it has no naming sentence.

The row takes reading 2, records `provenance: "proposal"` rather than `"design"`, and leaves
`design_cite: null` rather than pointing at a sentence that does not say what the row needs.
**A sibling author must do the same:** no row in this family may claim `provenance: "design"` for
the *existence* of its situation. Individual mechanisms (tables, purpose coherence, abstention,
residuals) are `design`; the situation is `proposal`. This is not pedantry — it is the difference
between the catalogue recording that 24 rows rest on an inference and the catalogue pretending they
do not.

---

## Did this row survive the node test? All three legs, argued

`kind: schema`, so CONNECTION §2's schema test applies: *can you name a distinct 3–6 field set, or
would you only repeat another schema, or need a giant form?* The test is complicated by the row
declaring **no fields at all** under D1-as-narrowed and PR-6, so leg 1 is run against the field set
the row *would* declare if the deferral were lifted.

### Leg 1 — a distinct field set

The candidate set is **`organization`, `fiscal_period`, plus `project` and `record_type` from the
canonical list** — four keys, inside the 3–6 band. Two of the four do not exist yet, and that is the
weakness of this leg, stated up front rather than buried.

- **Against the row:** `project` is `research`'s and `creative`'s; `record_type` is `finance`'s. If
  the two proposed keys are refused by R1c, the surviving set is *two borrowed keys*, which is
  exactly the "would only repeat another schema" failure. **This row's field leg is therefore
  contingent on NJ-BO-1.** No sibling should cite leg 1 as settled.
- **For the row:** the two proposed keys are not decorative. `organization` answers a **custody**
  question no canonical key answers — `our_firm` is the *authorship* role, `client` its counterparty,
  `institution` the finance-side issuer, `school`/`lab`/`venue` other worlds. None of them says
  *whose operating record this is*, which is the fact that separates a person's employer's board pack
  from that same person's own limited company's board pack sitting in the same Downloads folder.
  `fiscal_period` answers a **management-calendar** question `tax_year` cannot: an entity's fiscal
  year routinely does not coincide with a jurisdiction's statutory year, and reusing `tax_year`
  would quietly assert that it does.
- **Deliberately not offered as an argument:** that the *values* differ. A board pack's period
  labels and a tax year's labels look different, but values are values, and a `business_period` key
  would be precisely the two-spellings-one-concept bug D6 exists to prevent.

**Verdict on leg 1: passes, but conditionally**, and the condition is named as NJ-BO-1 rather than
smoothed away.

### Leg 2 — detection signals of its own

This leg does not depend on the field question and is where the row is strongest. Four signal
shapes belong to no other schema on the roster:

1. **The governance-cycle structure.** A body name, a period date, and at least two of an attendance
   list, a numbered agenda, a resolution block, and a papers index. No other schema has a fixture of
   this shape. `legal` has instruments and proceedings (adversarial, not cyclical); `academic` has
   terms (a calendar, not a decision record); `nonprofit` has the *same* shape, which is why that
   edge exists and is drawn on owner type rather than on structure.
2. **The controlled-document header.** Version / owner / approver / effective date / review date as a
   header block. This block does not appear on personal papers at all — it is the single cleanest
   discriminator this family has, and it is the reason `policy-handbook` passes its node test.
3. **The management-financial table without an institution.** A budget/forecast/actual/variance
   column set over line items, **with no account-number-and-balance header**. `00`'s table sentence
   licenses reading cells; the *absence* of the institution header is what makes it not `finance`.
   This is an argument from absent evidence and is marked as such wherever used.
4. **The post-signature obligation register.** A schedule of renewal dates, notice periods and
   counterparties that *manages* instruments rather than being one. `legal` owns the instrument;
   nobody else owns the register.

**Verdict on leg 2: passes cleanly.**

### Leg 3 — privacy rules of its own

Three grounds, none of them the generic "documents can be sensitive":

- **The exposed party is usually not the user.** This is the distinguishing fact and it is an
  inference, not a design claim. A customer list, a supplier contract, an employer's board pack on a
  personal laptop — the party who would be harmed by disclosure cannot consent to what the product
  does with it, because they are not operating the product. No other non-safety schema on the roster
  has this property as its *normal* case.
- **Attachment carriage.** `00`'s corpus sentence names material this family routinely carries as
  appendices: the corpus *"can include identity documents, account statements, tax records, medical
  information, legal records, credentials, private correspondence, GPS metadata, employment
  materials, and educational records"*. A board pack is a container for several of those at once.
- **The `hr` bleed.** A single spreadsheet crosses into employee-identifying material at one column.
  Where it does, the stricter side wins.

The row is `potentially_sensitive`, **does not carry `is_safety_domain`** — that flag stays with
`00`'s four — and assigns **no P7 handling class**. But the third-party point means a substitute
mechanism is needed, which is NJ-J-IND-4 below.

**Verdict on leg 3: passes.**

**Overall: kept.** Legs 2 and 3 pass cleanly; leg 1 passes conditionally on NJ-BO-1, and the
condition is recorded rather than resolved.

---

## The default template, stated for the 24 siblings

`template.dimension_order` is **empty by contract** — a dimension may only branch on a field the same
schema declares, and this placeholder declares none. The recommendation is therefore held as prose,
and **this is the paragraph every sibling must differ from**:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

Why each level, and why in that order:

- **`organization` is conditional, and seeded ineligible.** In a single-entity corpus it names the
  user's own employer above everything they have ever filed — both of `00`'s validator failures at
  once (*"create meaningless one-child levels"*, *"use an author or organization merely as a
  collector"*), and the collector sentence besides. It stays a *template-time* check against the
  accepted group, not a field-time ban; and *"the user can reverse, remove, add, or flatten
  dimensions."*
- **The body / project / contract / account level is the real top.** `00` puts project, function or
  subject above time explicitly. In this world it is also what stops the tree collapsing into a
  calendar, because nearly everything here is dated.
- **`fiscal_period` before function**, by the parent-context rule: *Q3 variance* is meaningless
  without knowing which budget, exactly as `Homework 3` is meaningless without the course.
- **Not time-first**, and this is the rule siblings will be most tempted to break, because this
  family is *made* of periods. `00` grants the time-first exception to **capture-based media only**.
  **No sibling in this family may claim it.** A budget year, a board year and a filing year are all
  content periods, not capture dates. A sibling claiming `time_first: true` is claiming the photos
  exception without the photos evidence, and R1c should reject it on sight.

A sibling therefore has a node only if it differs from **that** paragraph, or from this row's
detection signals, or from its privacy posture. **Differing in business function is not automatically
a difference**: "procurement", "facilities", "risk" and "IT asset" are *values of a function
dimension*. What earns those rows their node is a distinct **structure** — a tender evaluation
matrix, an asset register with serials and lifecycle dates, a risk register with likelihood/impact
scoring columns — not the topic word. This is the single most important sentence in this memo for
the sibling authors, and it is the sentence that would have prevented the 574.

---

## The never-alone principle, generalised for all 24 siblings

The family's one refusal, `business_operations.organisational-records`, is exemplary and its
argument generalises. Its core: an organisation name is **constitutionally never-alone** — read
across from *"A university name alone should not create a group because Columbia can appear as an
authoring school, course provider, target institution, employer, research venue, or merely a cited
organization."* — so a row whose entire support is an organisation name plus a document-type word
*can never clear activation* (CONNECTION §4 step 2). It would be a row that never fires.

Stated as a rule for this family:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**. If a proposed row cannot name such a pair, it is not
> a node — it is the schema's default template, or a residual wearing a domain's clothes.

Corollary, also from the refusal: **keeping a row to preserve a legacy id is the 574's mistake.** A
sibling author who finds their id has nothing left after its neighbours take the real situations
should refuse and route the coverage through `falls_through_to`. `refuse_node: true` with an argued
reason is a success.

---

## The vocabulary and posture the family shares

So that 24 rows do not each invent their own:

- **Anchor triple.** An *organisational unit* running a *cycle or project* producing a document with
  a *function*. If a candidate row cannot name all three, it is probably `career` (a person's own
  record), `finance` (custodial money), `hr` (people-identifying), or `legal` (an instrument).
- **Side.** Every document in this world has a side — seller or buyer, regulator or regulated,
  employer or employee, authority or applicant. **The side is evidence, and it is frequently
  unrecoverable from the file.** When it is unrecoverable, abstain.
- **Real versus exemplar.** Templates, samples, case studies and published best-practice packs are
  written to look exactly like the real thing. Topic will not separate them; *"purpose answers what
  the file was for"* is the only test that works.
- **Named residuals.** This family's six: Independent Records, Review Later, Receipts and
  Confirmations, Unsupported or Encrypted, Reading Inbox, Protected Records. A sibling should reuse
  from this set rather than reaching for a seventh.

---

## Files considered and rejected

The dispatch's own test: a row that only lists what it holds has not been researched. Named tempting
false positives, and what discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `Q3 strategy - McKinsey style template.pptx` (kept as the primary collision fixture) | Full strategy furniture — horizons, initiatives, a waterfall — with every value slot a placeholder and a consultancy's brand on the master. Discriminator: *"purpose answers what the file was for"*. It was for *illustrating* a strategy, not running one. **A document shaped like an operating record is not one.** |
| A **supplier invoice** with no register around it | A transactional document; this schema owns *cycles and registers*, not transactions. Goes to **Receipts and Confirmations**. It becomes this family's evidence only when a register, a purchase-order reference or a contract calendar sits around it. |
| A **CRM export** | A system dump. Its interesting members are contacts data, which `00` already rules out of folder proposals. Not a record of the organisation running itself; a database of other people. |
| An **org chart naming people** | Real, and it goes to `hr.org-design-headcount` the moment it names individuals. The role-only version stays here and earns a `work_type`, not a fixture. |
| A **saved industry report** or benchmark study | The tempting false file for this whole schema: dense in exactly this family's vocabulary and belonging to nobody's operating cycle. **Reading Inbox.** |
| An **MBA case study pack** or a business-school lecture deck | Identical vocabulary, identical shape, academic context. `academic` fires on its own evidence; this schema must not fire on business words. Deliberately given **no edge** (see below). |
| A **job description** downloaded while job-hunting | Employer-shaped, but held as the *individual's* recruiting material. `career`. |
| `Screenshot 2026-04-02 at 09.14.11.png` of a revenue dashboard (kept as a fixture) | OCR shows a chart and a period selector; no header, no entity, no labelled slot. And it may be a **competitor's** dashboard, a product demo, or a figure in an article. Temporary Screenshots. |
| `IMG_2044.HEIC`, a phone photo of a whiteboard quarterly plan (kept as a fixture) | Real EXIF, real capture date, and handwriting that no extractor has read. `also_schema: photos`, group without copying facts, and **conclude nothing about a plan before OCR exists**. |
| `dataroom-export-2026-02.zip`, password-protected (kept as a fixture) | The manifest names contracts, registers, policies, statements and HR summaries — and *"the normal scan should never extract archive contents to the filesystem"*. Unsupported or Encrypted. No purpose fact from a manifest. |
| `Weekly leadership sync.ics` (kept as a fixture) | Calendar is a **source type**, not a domain — CONNECTION-EXAMPLES fixture 5 forbids the inference. A meeting title is not a governance-body fact. |
| A **payslip** in the same folder as a payroll run | Two documents, two sides. The individual's payslip is `finance.payroll-received`; the employer's run is `hr`. Neither is this schema, and the folder is not evidence. |
| A **`.git`/`node_modules`/`dist` tree** inside an internal tool's repository | Removed by the exclusion rule; where the repo root fires, `code` owns the layout and this schema must not propose re-filing anything inside it. |

---

## The collision fixture, named

**`Q3 strategy - McKinsey style template.pptx` versus a real internal strategy deck.**

Both are `.pptx`. Both carry the same corporate furniture — a horizons chart, an initiative
portfolio, a waterfall, an owner column. Both carry a company brand on the slide master. Both were
created by someone at a company, on a company machine, in a folder called `Strategy`. Every
deterministic signal this schema owns fires on both: business vocabulary, a slide shape, an entity
name on the master, a plausible parent folder.

**What discriminates:** whether the value slots carry *this organisation's actual commitments*. The
template's owner column says `[Name]`; the real deck says a person and a date. The template's
numbers are round or lorem; the real deck's reconcile to a budget elsewhere in the corpus. That is a
`needs_llm` determination and it is one where *"A model that cannot cite sufficient evidence must
return unknown."* applies without softening.

**What emphatically does not discriminate:** the brand on the slide master. A corporate template
stamps the same company on every blank form it ever generated — including the ones a former employee
kept. This is the PDF-metadata warning, *"PDF metadata should be treated as supporting evidence, not
as truth"*, in its most seductive form.

**Second fixture, for the finance seam:** `FY26 budget v7 FINAL (2).xlsx`. Money in a spreadsheet,
with period columns and department sheets. It contests the same bytes with `finance` and with
`finance.small-business-bookkeeping`. The discriminator is **absence**: no institution, no account
number, no balance header, no double-entry structure. Both sides must name this file; see the table
below.

---

## Reciprocal boundaries, both directions

**A finding that must not be lost: no landed row on the roster names `business_operations`, except
`construction_property`.** `career`, `finance`, `legal` and their template rows were written before
this family landed and carry no edge back. Every boundary below except the last is therefore
**authored one-way here, and R1c owes the reciprocal.** That is a catalogue defect, not a judgement
about the seam.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| **`career`** (launch, field-less) | a document addressed to the holder **as an individual**, or held to evidence the holder's own employment, standing or engagement | the organisation's population-level or counterparty-level version of the same document — a schedule of many people, a register, a blank template, an approval workflow | an **offer letter**; a **compensation plan**; a **policy acknowledgement**; an **expense claim** — the same document family with the roles reversed |
| **`career.consulting-client-engagement`** (landed) | one piece of paid work done **for** another organisation, with its proposal, SOW, deliverables and correspondence — that row owns it, and `00`'s role-split sentence is its charter | the **delivering** organisation's contract register, renewal calendar and account plan that sit around many such engagements | `MSA - Acme Ltd - executed.pdf` — the individual's engagement record and the firm's contract record, on disjoint evidence inside one file |
| **`finance`** (safety, 4 fields) | anything with an **institution-and-account header**, a statutory form's issuing authority, or a double-entry ledger structure | a **plan of money that has not happened yet** — budget, forecast, variance commentary, business case — merely because it is money in a spreadsheet | `FY26 budget v7 FINAL (2).xlsx` |
| **`finance.small-business-bookkeeping`** (landed) | journals, ledgers, sales invoices, vendor bills, reconciliations, statements, accounting backups — that row is function-first and owns the working book | the **management** layer above the book: the board's financial appendix, the reforecast, the variance narrative | a workbook holding a forecast sheet **and** a reconciled-actuals sheet sourced from an accounting system — both true, disjoint evidence |
| **`legal`** (safety, field-less) | an executed instrument's operative clause structure, a dispute, a tribunal caption, or a privileged-advice framing — `legal` protects first (CONNECTION §4 step 5) | the **register, notice calendar, approval workflow and obligation tracker** that run an instrument after signature | `MSA - Acme Ltd - executed.pdf`; a contract register spreadsheet quoting its clause numbers |
| **`legal.leases-agreements`** (landed, safety) | the agreement lifecycle itself — amendments, schedules, signing evidence, renewals, termination records | a **portfolio** of agreements managed as an operating asset: renewal dates, notice-period tracking, spend by counterparty | an office lease and its renewal notice — the instrument set (that row) and the renewal-calendar entry (this family) |
| **`legal.practice-matter-file`** (landed) | anything anchored to a **matter identifier**, a client-and-engagement framing, time recording, or privileged advice | the same board minutes, statutory registers and negotiated agreements **held by the entity they are about**, with no matter anchor | corporate-secretarial output: board minutes and a statutory register, byte-identical on both sides |
| **`hr`** (schema not yet written) | material that **identifies named employees** — a case file, a payroll run, a personal review, a signed acknowledgement | material about the organisation's **shape, cost and policy without named individuals** — a headcount budget, a policy, an org chart by role | one **headcount spreadsheet** that becomes `hr` at the column where names appear |
| **`government`** | an issuing or deciding authority's letterhead, case reference and statutory power | an applicant's or supplier's **submission, acknowledgement and evidence file** | a permit; an inspection report; a tender — identical documents, opposite sides |
| **`nonprofit`** | trustee/member vocabulary, a charity or union registration slot, donor or membership records, a purpose-of-association framing | governance, budgets, policies and returns in a **commercial** framing — share capital, customer revenue, commercial counterparties | board minutes; an annual return — the same objects, split on owner type |
| **`law_practice`** | a practitioner's matter, engagement, time-recording or billing anchor | corporate-secretarial output held by the company itself | as `legal.practice-matter-file` above |
| **`code`** | anything inside a preserved repository root | an **asset register, change approval or compliance-evidence framing** merely because IT produced it | an architecture decision record; a dependency inventory |
| **`construction_property`** (landed, two-way) | a property or site that is the **subject of an instruction** for someone — a priced job, a valuation, a letting | a construction or property **firm's own running record** — its board pack, its insurance renewal, its staff policy | a **fit-out contract for the occupier's own office**: a contract sum and drawings (theirs) sitting in a contract register under a renewal calendar (ours) |

### Where `business_operations` stops and `hr` begins — written for the `hr` author

`hr` is a separate schema and is not yet written, so this line is stated in enough detail to be
written against. ROSTER §1b split the two on a **privacy-rule difference, not a topic one**, which
makes the boundary thin by construction. Concretely:

- **`hr` owns the individual-identifying employment record.** The roster's `hr.*` rows —
  `onboarding-offboarding`, `performance-cycle`, `employee-relations`, `compensation-planning`,
  `workforce-analytics`, `training-development`, `engagement-survey`, `dei-program`,
  `workplace-health-safety`, `org-design-headcount` — are about *people*, and their reason for
  existing separately is that they must be protected before any model path.
- **`business_operations` owns the same subjects at the population level with no individuals.** A
  policy is this schema; the signed acknowledgements are `hr`. A headcount budget is this schema;
  the leaver list inside it is `hr`. A workplace safety *procedure* is this schema; an incident
  report naming an injured employee is `hr`.
- **Where one file crosses, the stricter side governs the members that identify people, even where
  this schema activates on the container.** That is the `also_holds_with: hr` case, and it is
  disjoint-evidence co-activation rather than a mutex.
- **Note for the `hr` author:** `career.employer-side-hiring` already absorbed four legacy `hr.*`
  recruiting ids. Hiring is **not** yours; the roster gave it away. Check Appendix A before writing.

---

## Neighbours considered that did **not** get an edge

- **`retail_hospitality`, `logistics`, `resource_operations`, `manufacturing`, `engineering`** — every
  one of them runs governance, budgets, procurement and compliance. A `collides_with` to all five
  would be **true and useless**: it would say only that organisations are organisations. The sector
  confusions bite at *template* level (a procurement row genuinely contests a logistics sourcing
  record) and R1c should place them there. Naming them here would rebuild the industry forest
  ALIGNMENT.md removed.
- **`academic`** — an MBA case study and a university's own administration both look exactly like
  this. Deliberately no edge: an academic context term plus a course-code-shaped token is `academic`
  firing on its **own** evidence, and the confusion is fully handled by this row's `never_alone`
  entry on business vocabulary. Adding an edge would imply contested evidence where there is only
  contested vocabulary.
- **`creative`** — `creative.json` names `business_operations` in *its* table (a brand-guidelines
  PDF, a campaign's working files). Not reciprocated as a `collides_with` here, because from this
  side the contested item is a single document type rather than a family of them. Recorded so R1c
  can decide whether the pair should be symmetric.
- **`identity`, `medical`, `photos`, `college_applications`** — no honest schema-level confusion.
  `photos` appears as an `also_schema` on one fixture and that is the right weight.

---

## `proposed_fields` — two, and both are mints, not adoptions

Unlike `creative` (whose four proposals are all existing keys), **both of this row's proposals are
new keys**, which raises the bar. Each carries its own argument, `destination_eligible` reasoning,
`reliability_ceiling` and the reason the ceiling cannot be higher.

- **`organization`** — the **custody** role: whose operating record this is. Proposed
  `destination_eligible: false` on the collector argument above; `reliability_ceiling: "possible"`,
  because an entity name is the multi-role token, and a `direct` reading would need a
  gazetteer-plus-context rule family (R4 owns the gazetteer) that does not exist.
  **This is ONE decision, not two.** `construction_property` proposes the same key for the same
  custody reason and states that it *"REUSES the `organization` key already proposed by the landed
  business_operations schema row rather than minting a construction-flavoured variant, and it should
  be adjudicated once, there, for both."* R1c must settle it once, for both families. The JSON now
  says so in the proposal itself.
- **`fiscal_period`** — the management calendar. Proposed `destination_eligible: true` (a period is
  not a person, so the authorship prohibition does not reach it) but explicitly **not first**.
  `reliability_ceiling: "validated"`, and defensible only because a rule family *can* confirm it: a
  fiscal-period token pattern co-occurring with a period-context term in the same labelled block —
  the same pattern-plus-context **shape** `00` uses for the academic course code. This row writes no
  regex and no term list; R2/R6 own those. Without that rule the honest ceiling drops to `possible`.
  **Four rows in this family want this key and none can have it** (budget-forecast, board-governance,
  corporate-regulatory-filings, compliance-audit). It is the clearest field-shaped hole the pass
  found.

**A third hole is named and deliberately not proposed here.** `00`'s role pair is
`our_firm` / `client`. A **supplier** in a buy-side register, and a **subscription customer**, are two
further roles with no key at all. Raised on `contract-administration`, `procurement-sourcing` and
`customer-account-management` rather than smuggled onto the schema — minting a role key on a
field-less schema at the exact point of maximum temptation would be the 574's mistake performed
knowingly.

`proposed_context_terms` carries 40 practice terms (`financial year`, `variance`, `effective date`,
`document owner`, `registered office`, `quorum`, `terms of reference`, `statement of work`, `notice
period`, `corrective action`, `annual return`, …). These are **proposals**, not `00`'s floor — `00`'s
named context-term floor is the academic one, and this row does not pretend otherwise.

---

## Sparse-file discipline

Five of the eleven fixtures carry `group_without_copying_facts: true`, and this world needs the rule
badly, because its sparse members are the *normal* case: a budget workbook with a duplicate-shaped
suffix, a whiteboard photo, an encrypted data-room export, a recurring calendar entry, an archive
read from its manifest. In each, the neighbourhood may legitimately group the file while **no**
entity, period or function fact is written onto it — *"The graph does not automatically copy those
missing facts onto sparse files."* This is `00`'s `HW 3.pdf` rule applied to a world where a folder
of a hundred files may contain one that names the entity.

Every fixture also carries `"any business_operations fact - the schema declares none"` in
`must_not_conclude`, so the placeholder status is checkable file-by-file rather than only in the
header.

---

## Salvage and deepening — what was preserved, what was added

**Preserved unchanged** (verified correct, not rewritten):

- the key set — 27 keys, identical to the landed `creative.json` and `clinical_practice.json`, in the
  same order;
- all 40 quotations, machine-verified verbatim against `00`;
- `fields: []`, `dimension_order: []`, `time_first: false`, no threshold, no statistic, no P7
  handling class;
- both `proposed_fields` **arguments** (`organization`, `fiscal_period`) — kept as written;
- the `recognition` block (11 deterministic, 7 needs_llm, 9 never_alone), the 40 context terms, 15
  work types, 8 grouping reasons, 11 fixtures, 5 `also_holds_with`, 6 `falls_through_to`, the
  `role_split` entry, `sensitivity`, `sensitivity_why`, and the four-part `open_question`;
- the family's refusal `business_operations.organisational-records` — untouched, and now generalised
  into a family-wide principle in this memo.

**Added or changed in the JSON** (three surgical edits, nothing rewritten):

1. `one_line` — the retired `Gist-level placeholder (J-IND)` label replaced with *"A PLACEHOLDER
   SCHEMA ROW written to J-DEPTH"*. Substance unchanged.
2. `proposed_fields.organization.why_no_existing_key` — prefixed with the **ONE DECISION, TWO ROWS**
   statement quoting `construction_property`'s own reuse sentence, so R1c cannot read the two
   proposals as competing. The original argument follows verbatim.
3. `collides_with` — a **`construction_property`** entry added, making two-way an edge that family
   had authored one-way toward this row, accepting their discriminator verbatim and adding the
   second half (a property firm's own running record is this schema).

**Added in this memo** (the deepening proper): the provenance argument for `design_cite: null`; the
three-leg node test argued rather than asserted; the default-template paragraph written for the 24
siblings, including the no-sibling-may-claim-time-first rule and the function-words-are-values rule;
the never-alone principle generalised from the refusal; the shared vocabulary and posture section;
the thirteen-row rejected-files table; the named collision fixture with its
*what-does-not-discriminate* half; thirteen reciprocal boundaries in both directions with shared
fixture bytes named on both sides; the `hr` seam written for the `hr` author; the
neighbours-without-an-edge section with reasons; and the finding that **no landed row except
`construction_property` names this family**, so twelve of the thirteen boundaries are one-way and
R1c owes the reciprocals.

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/business_operations.json` → parses.
- Key set unchanged and identical to the landed `creative.json`, in the same order — compared
  programmatically, empty symmetric difference.
- Every quotation newly introduced into the JSON or this memo grep-verified verbatim against
  `00-database-agent-product-design.md`; the `construction_property` quotations grep-verified against
  `construction_property.json`. The pre-existing 40 were verified on the salvage pass and were not
  altered.
- `fields: []` holds; `dimension_order: []` holds; no canonical key minted; both `proposed_fields`
  entries carry `adjudicate: "R1c"`.
- No numeric threshold, statistic or file count invented. The two counts stated — 25 roster rows in
  the family, therefore 24 templates; 45 absorbed legacy ids — are read from `ROSTER.md` §4 and
  Appendix A, not estimated.
- Every `collides_with` and `also_holds_with` target is a real roster **schema** id (correct for a
  schema row); every `falls_through_to` is one of `00`'s nine residual names; every
  `file_examples.source_type` is in P5's fourteen.
- **Files written: exactly two** — `planning/domains/nodes/business_operations.json` and this memo.
  Nothing else was touched.

---

## NEEDS-JOSEPH

- **NJ-J-IND-3 (carried; this family's most load-bearing)** — **where does an *organisation's* money
  live?** The roster's reading is statutory-and-custodial to the `finance` safety schema,
  forward-looking-management to `business_operations`. Defensible, but drawn by the roster pass, not
  by `00`. Alternatives and costs: **(a) keep the split** — `budget-forecast` and
  `corporate-regulatory-filings` stand, but one workbook routinely holds both sides and the seam
  runs *inside* a file; **(b) all organisational money to `finance`** — clean, protective, and
  removes two rows from this family, but puts forward-looking management artifacts under a safety
  schema whose fields (`institution`, `account`, `record_type`, `tax_year`) cannot describe them;
  **(c) all organisational money here** — coherent for the family, but strips safety protection from
  statutory returns and ledgers, which is the wrong direction on a safety question. *This row's
  recommendation, offered and not taken: (a), with the seam restated as evidence-based (institution
  header present or absent) rather than topic-based.*
- **NJ-J-IND-4 (carried; this row's variant)** — this row correctly does **not** carry
  `is_safety_domain` and should not. But its material is frequently confidential to a **third party
  who is not the user and cannot consent**. If the flag stays with `00`'s four, the substitute
  mechanism that forces P7 ahead of a model path for confidential commercial material must be named
  somewhere. Alternatives: a fifth safety domain (breaks D-ratified scope); a per-row
  `sensitivity: potentially_sensitive` that P7 already honours (current assumption — **is it
  enough?**); or an explicit third-party-confidentiality flag on the sensitivity block (new
  mechanism, needs an owner).
- **NJ-BO-1 · Are `organization` and `fiscal_period` allowed to become canonical keys?** For R1c,
  **and it decides leg 1 of this row's node test.** If both are refused, this schema's field set is
  two borrowed keys and the fold question in NJ-BO-2 becomes sharper. **`organization` must be
  adjudicated once for both this family and `construction_property`.**
- **NJ-BO-2 · Is 24 templates on a field-less schema the right shape?** If the D1 deferral holds, the
  dimensions leg is unavailable to all 24 equally and each must justify itself on detection signals
  and privacy rules alone. The commercial cluster (`customer-account-management`, `partnerships-bd`,
  `go-to-market`, `market-research`) is where a trim would be cheapest; `go-to-market` is the weakest
  and carries its own fold question. Cost of trimming: the coverage returns to Reading Inbox and
  Independent Records, which for market research is arguably where it belongs.
- **NJ-BO-3 · `role_split` key spelling is inconsistent across the landed catalogue** (`neighbor` /
  `other_domain` / `domain`, with `our_field`/`their_field` versus `field`/`other_field`). Mechanical,
  but it is a stored join handle and D6's reasoning applies. R1c's to normalise; no row should do it
  unilaterally.
- **NJ-BO-4 (new) · The reciprocals are missing.** No landed row on the roster names
  `business_operations` except `construction_property`. Twelve of the thirteen boundaries in this
  memo are authored one-way from this side. Either R1c adds the return edges to `career`, `finance`,
  `legal` and their template rows, or the catalogue ships with asymmetric edges and the activation
  logic must be defined to tolerate that.
- **NJ-BO-5 (new) · The buying-side role has no key.** `our_firm`/`client` cannot express *supplier*
  or *subscription customer*. Three rows in this family need it. Not proposed here on purpose; R1c's
  call whether it is a third canonical role key or a value on `organization`.

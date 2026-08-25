# `nonprofit` — lab notes (schema row, authored at J-DEPTH)

**Verdict: the family stands, and it stands NARROW.** `refuse_node: false`, but the row concedes the
charge against it almost in full and writes the concession into its own JSON so a later reader cannot
quietly widen it. A charity's board minutes, budgets, contracts, policies, procurement, audits,
projects, IT assets, facilities and regulator returns are **`business_operations` with a different
tax status**, and this schema does not hold any of them. What is left is real, structural, and has no
home anywhere else on the roster.

The one-sentence thesis, which is also the answer to the charge:

> Every relation `business_operations` owns is an **exchange** (value for value) or a **statutory**
> one (compliance for authority). This family's relations are **neither**: money or labour given
> without a commensurate return — a funder's restricted grant, a donor's gift, a member's
> subscription, a volunteer's unpaid hours — and service given to a **named person who is not paying
> for it**. That is a structure. Tax status is a field value.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. **Every quotation in the JSON and
  in this memo was machine-checked with `grep -F` against this file before writing**; 26 unique
  quoted spans, all verbatim, all confirmed by a JSON-walking re-check after the file was written.
- `planning/domains/_CONTRACT.md`, `planning/domains/CONNECTION.md` (§2 node test, §4 activation —
  step 2 never-alone, step 5 protective ordering, §9 failure modes), `CONNECTION-EXAMPLES.md`.
- `planning/prompts/ALIGNMENT.md`; `planning/domains/canonical_fields.json` (36 canonical keys, and
  the 37 already-floated `proposed_fields` across the landed roster, enumerated before proposing
  anything).
- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment for `nonprofit`.

### The critical negative finding

**`00` contains no occurrence of `charity`, `charitable`, `nonprofit`, `non-profit`, `donor`,
`donation`, `volunteer`, `fundraising`, `congregation`, or `union`.** This was checked, not assumed.

Two consequences, both binding on this row:

1. `provenance` is `proposal` and `design_cite` is `null`, necessarily. Nothing in this family is
   *described* by `00`.
2. **Every structural claim below is inference and is marked as such.** What `00` does supply is the
   *method* — never-alone reasoning, the labelled-form-field path, the spreadsheet and archive
   extraction rules, the residual library, the abstention rule — and the method is applied here
   rather than paraphrased into false authority. Where the memo quotes, it quotes about method.

### Landed neighbours read before writing (and not touched)

`business_operations.json` (the anchor and its 24-sibling default paragraph),
`business_operations.organisational-records.json` (the refusal, read **in full**, including the
four-part two-role closure), `business_operations.research.md` §§ *The default template*, *The
never-alone principle generalised*, *The vocabulary and posture the family shares*;
`government.json` (authored 2765f94); `research.grants-funding.json`;
`finance.hoa-residents-association.json`; `clinical_practice.json` (`subject_of_record`);
`hr.json` (`workforce_member`, `personnel_case`).

---

## The charge, taken first and taken seriously

The dispatch states it exactly: *a charity is an organisation, and an organisation name is
constitutionally never-alone.* `business_operations.organisational-records` was refused on that
ground and its refusal closes the two-role escape route in four independent ways. So before
anything else, this row must survive its own refusal argument.

**Step 1 — apply the deletion test from the refusal, unchanged.** *Delete every entity name and every
document-type word.* Now delete the ones specific to this family: the charity registration number,
the 501(c)(3) reference, the CIC/CIO/e.V. suffix, the mission sentence, the word *beneficiary*, the
word *impact*. What survives?

- A **parties block with a labelled funder slot and a labelled grantee slot**, a **purpose clause
  restricting the money to a named activity**, an **instalment schedule conditional on reports**, and
  an **expenditure statement reconciling spend to agreed cost headings**, all sharing one repeated
  reference. Nothing was deleted. The structure is intact.
- A **column set partitioning the same rows into unrestricted / restricted / endowment**, or a table
  with **one row per named fund** carrying opening balance, income, expenditure, closing balance.
  Intact.
- A **register with one row per named person** carrying a membership number, a class, a join or lapse
  date and a subscription status; a **meeting instrument** with a notice period, a motion, proxies
  and a member-vote count. Intact.
- A **referral with a labelled referrer and a labelled service-user slot**, a case reference repeated
  across dated notes, an assessment of need, a support plan, a closure record. Intact.
- A **rite register**: entry number, date, person, officiant, witnesses, rite label. Intact.
- A **volunteer agreement whose own clauses disclaim employment**, beside a rota and an expense sheet
  **with no gross-to-net line**. Partly intact — see the honest weakness below.

**Step 2 — apply the pincer, which is the refusal's strongest limb.** *If two labelled roles are
present, the pair is already a named sibling's whole node and this row firing would be theft.* So
name every organisational role pair the roster already owns and check whether any of them is this
family's: buyer/supplier is `procurement-sourcing`; principal/counterparty is `legal` for the
instrument and `contract-administration` for the register; provider/customer is
`customer-account-management`; two organisations negotiating jointly is `partnerships-bd`;
regulator/regulated is `corporate-regulatory-filings`; employer/employee is `hr`; main
contractor/subcontractor is `construction_property.subcontract`; landlord/tenant is
`tenancy-management`; authority/applicant is `government`; clinician/patient is
`clinical_practice.patient-chart`; sponsor/PI-and-lab is `research.grants-funding`.

**None of them is funder/grantee-under-restriction, donor/recipient-without-return,
member/association, volunteer/organisation, or provider/non-paying-named-beneficiary.** The pincer
does not close. That is the finding, and it is the whole reason the row exists.

**Step 3 — concede everything the pincer *does* close.** This is where the row differs from a row
written to save an id. The charity's self-running record is not taken:

| The artefact | Where it goes | Why this row does not take it |
| --- | --- | --- |
| Trustee board minutes, agenda, papers, resolutions | `business_operations.board-governance` | A trustee board running a governance cycle is structurally identical to a company board. *Trustee* is a role word; a role word alone is never-alone. |
| Annual budget, forecast, variance | `business_operations.budget-forecast` | A period column set is a period column set. Only a **fund partition** fires here. |
| Charity annual return, Form 990, LM filing | `business_operations.corporate-regulatory-filings` | The relation is regulated-entity to regulator, which is that row's entire node. |
| Supplier contracts, tenders, POs | `procurement-sourcing`, `contract-administration` | Exchange relations. |
| Policies, handbooks, SOPs | `policy-handbook` | Identical structure and identical purpose. |
| Audits, controls, findings | `compliance-audit` | Identical. |
| Projects, risk registers, retros, IT assets, facilities | the matching `business_operations` siblings | Identical. |
| Bank statements, ledgers, filed returns | `finance` | Custodial and statutory money. |
| Staff records, payroll, grievances | `hr` | Employer/employee. |
| A **company's** donations, foundation, community-programme reporting | `business_operations` / `finance` | The giving side of a company is the company's own record. Charity as a *counterparty* does not import this schema. |

That table is not politeness. It is the row's defence: a schema that names precisely what it does
not hold cannot be accused of being another schema with a tax field.

**Step 4 — the honest residue.** Two candidate templates survive the deletion test only weakly and
the JSON says so in its `open_question` rather than hiding it: **volunteer-programme**, whose
discriminator is an *absence* of payroll structure, and **campaigning-advocacy**, which is
`go-to-market` with different nouns plus a lobbying filing that is a regulator return. If ten
templates are required, those two and a charity-regulator-return row should be **refused**, not
invented. Naming that up front is the whole lesson of the 574.

---

## Did this row survive the node test? All three legs, argued

CONNECTION §2: a row exists only where its **detection signals**, **recommended dimensions**, or
**privacy rules** differ from its parent's default. A schema row's parent is the roster itself, so
the test is read against the nearest schema it could be folded into — `business_operations`.

### Leg 1 — detection signals of its own. **PASSES, and this is the strong leg.**

Twelve deterministic signals are written, and every one of them pairs a **structure** with a
**labelled slot**, which is the rule `business_operations.research.md` generalises for its 24
siblings: *"No sibling may rest its activation on an entity name, a business vocabulary word, or a
document shape alone."* Applied here that rule is *stricter*, because this family has a fourth
never-alone token the others do not: **charitable status**.

The five load-bearing signals, and why each is false of `business_operations`:

1. **Restricted-grant lifecycle, grantee side.** A repeated reference across call → agreement with a
   labelled **purpose restriction** → milestone report against **agreed outputs and outcomes** →
   expenditure statement reconciled to cost headings. `business_operations` has no relation in which
   money arrives already earmarked and must be *accounted back* to a giver who bought nothing.
   `procurement-sourcing` is buyer-side; `customer-account-management` is revenue for a deliverable.
2. **Restricted-fund partition.** A **column set partitioning by fund class**, or one row per named
   fund with opening/income/expenditure/closing. `budget-forecast`'s structure is a *period* series;
   `finance`'s is an *institution and account*. A fund axis is a third structure and neither row has
   it. Read through `00`'s spreadsheet path: *"Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and
   Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell
   values, table-like regions, formulas only when useful, and dates or identifiers from labeled
   cells"*.
3. **Gift declaration.** A donor slot plus a **non-exchange assertion** — a statement that no goods
   or services were provided, a gift-aid style taxpayer declaration, a deed of covenant. The
   assertion *is* the signal: a payment with a deliverable is a sale.
4. **Beneficiary case accumulation.** Referral → assessment → dated notes under one case reference →
   plan → closure. Longitudinal accumulation about a single named subject, which is exactly the
   disjoint-from-the-schema signal that won `clinical_practice.patient-chart` its node, and it is
   disjoint from `business_operations` in the same way: `customer-account-management` accumulates a
   *commercial* relationship with an organisation, not a service history about a person.
5. **Rite register.** Entry number, date, person, officiant, witnesses, rite. This one has **no
   analogue anywhere on the roster**, in any schema. It is a register of named third parties
   accumulated across generations.

`00` licenses the reading path for all five: the labelled-slot route is its direct-fact path, *"a
labeled form field"*; position weighting is justified because *"A course code or university name
found in a filename, title, or page-one heading is more meaningful than the same text appearing once
in a reference list on page eighteen"*; the table route because *"Tables matter because resumes,
forms, applications, invoices, and administrative documents often place their"* key values in them;
and archives are read without unpacking because *"the normal scan should never extract archive
contents to the filesystem"*, yielding what `00` says an archive yields: *"The engine should read and
store the archive type, contained paths, filenames, folder names, extensions, file count,
uncompressed size where available, and recognizable markers such as source-code manifests or document
names"*.

### Leg 2 — a default template of its own. **PASSES, on one substitution and one prohibition.**

`business_operations`' default paragraph, which every sibling must differ from, is:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* → the
> **governance body, project, contract, or account** the material belongs to → the **fiscal period** →
> the **document function**. Not time-first.

This family's, stated as prose because `template.dimension_order` is empty by contract:

> the **association** only where the corpus genuinely spans more than one → the **non-exchange
> counterparty or fund** — the grant, the restricted fund, the appeal, the membership class, the
> case, the register → the **period** — grant period, appeal, membership year, financial year → the
> **document function**. Not time-first.

The second level is a genuine substitution, not a rename: *governance body / project / contract /
account* are all things the organisation runs for itself; *grant / fund / appeal / membership class /
case* are all **named after the outside party or the string attached to the money**. And the third
level differs materially in one respect worth recording: **a grant period frequently does not align
with the association's financial year**, which is why the `fiscal_period` proposal below asks R1c to
either widen the key's definition or record the misalignment.

Both of `business_operations`' guardrails carry, and one is added:

- The association level is **seeded ineligible** for the same reason — in a single-association corpus
  it is *"use an author or organization merely as a collector"* and it would *"create meaningless
  one-child levels"*.
- **Not time-first**, and this family may not claim the exception either. `00` grants time-first to
  capture-based media; a grant period, an appeal and a membership year are content periods.
- **New, and binding on all ten templates: a named beneficiary, donor, member or safeguarded person
  may NEVER be a folder level**, however strong the grouping axis. The case *group* may form; the
  *path* may not carry the person's name, because a path writes a vulnerable third party's identity
  into the filesystem where every later process reads it — against *"The default posture must
  therefore be local-first and data-minimizing."* This is the one dimension rule in the family that
  has no counterpart in `business_operations`, and it is a leg-2 difference in its own right.

And the recommendation stays a recommendation: *"The system recommends an order based on the domain
template, but the user can reverse, remove, add, or flatten dimensions."*

### Leg 3 — privacy rules of its own. **PASSES, and this is the leg the dispatch flagged.**

`business_operations` sits at `potentially_sensitive` on two grounds: `00`'s corpus sentence, and the
observation that much of its material is confidential to a third party. This row sits at the same
enum value — it is the strictest available, and 152 of 155 landed rows carry it — but on a **third,
different ground**, and the difference is what makes it a leg rather than a repetition.

1. Shared with `business_operations`: `00`'s corpus *"can include identity documents, account
   statements, tax records, medical information, legal records, credentials, private correspondence,
   GPS metadata, employment materials, and educational records"*, and beneficiary files carry medical
   information and identity documents as a matter of course.
2. **Different in kind:** the exposed party here is a third party who is neither the user, an
   employee, nor a customer, and who **frequently disclosed under need, harm or vulnerability**. A
   commercial counterparty in `business_operations` entered a relationship voluntarily and
   symmetrically. A safeguarded child did not. And the holder is very often a *volunteer or trustee
   working on a personal machine* — so the subject is a third party twice removed from the user, with
   no relationship to that machine at all.
3. **Different again:** membership and donation are **disclosive of protected characteristics from
   the mere fact of the record's existence**, before any content is read. A union roll, a
   congregation register, a political donation, a support-group membership. No `business_operations`
   record has this property; a customer list does not reveal the customers' beliefs.

The row does **not** carry `is_safety_domain`, and should not — `00`'s four are named and closed:
*"Finance, identity, medical, and legal material should be implemented first as safety domains,
meaning the system detects and protects them before any cloud or automated placement decision is
allowed."* That leaves a real gap, raised as **NJ-NP-3**: this is `business_operations`' NJ-J-IND-4
at higher stakes, because the third party here is often a child. Until the substitute mechanism is
named, the family's own rule stands and is written into the JSON: **safeguarding and beneficiary
structure is detected in order to be PROTECTED, never in order to be moved**, and *"If a model needs
text containing sensitive content, the user should see that requirement and choose whether to allow a
local model, a cloud model, a redacted prompt, or no model use."*

**All three legs pass. Leg 1 and leg 3 pass strongly; leg 2 passes on a substitution plus a
prohibition that is genuinely new.**

---

## Files considered and rejected

Named because a row that only lists what it holds has not been researched.

1. **A charity's trustee board minutes.** The single most tempting false positive in the family, and
   it is rejected outright — see the collision fixture below. `business_operations.board-governance`.
2. **A charity's annual return / Form 990.** Regulated-entity to regulator. That is
   `corporate-regulatory-filings`' whole node and this row takes none of it. The only residue is the
   *restricted-fund note* or *public-benefit account* the return may carry, and even that fires here
   on its own fund or beneficiary structure, not on the return.
3. **Another charity's published annual report, downloaded.** Reading material. Charitable branding,
   impact language and beneficiary photographs all present; no relation to the holder. *"purpose
   answers what the file was for"* is the only test that works. → **Reading Inbox**.
4. **A model safeguarding policy, a sample grant application, funder guidance PDFs.** Written to look
   exactly like the real thing — the family's `real versus exemplar` problem, inherited from
   `business_operations`' shared-posture section. → **Reading Inbox**.
5. **A donation receipt held by the giver.** Rejected *as this schema's*, and it is the collision
   fixture's twin: identical bytes, opposite side, and it belongs to `finance` as the giver's own
   charitable-giving record.
6. **A single HOA dues notice addressed to one owner.** `finance.hoa-residents-association`. The
   member's side, not the association's. The seam is drawn reciprocally below.
7. **A research award file — award number, period of performance, budget justification, F&A,
   biosketches, data-management plan.** `research.grants-funding`, landed and deep. Rejected here
   even though the word *grant* is on every page.
8. **An individual's scholarship or fellowship application.** `applications.scholarship-fellowship`.
   Money given rather than sold, but the applicant is a person applying for themselves.
9. **A corporate CSR or ESG report, a community-investment summary.** Full of *beneficiaries*,
   *outcomes*, *stakeholders*, *impact*. Written by a company about its own activity →
   `business_operations`. The vocabulary is a never-alone token, listed as such.
10. **A charity's employment contract, payroll run, grievance file.** `hr`. Employer/employee is an
    exchange relation and charitable status does not alter it.
11. **A service contract under which a charity delivers a commissioned public service.** Value for
    value → `business_operations.contract-administration`. Public money does not make it non-exchange
    and the *side* does not make it governmental.
12. **A crowdfunding page save, a donation-platform notification, a CRM export header.** The tool
    identifies who produced the bytes, not whose record it is nor which side. → **Receipts and
    Confirmations** or **Review Later**.

---

## The collision fixture, named

**`Trustee board minutes - 12 March 2026.pdf`.** A cover naming a board of trustees and a date;
attendance, apologies, quorum; numbered papers and numbered resolutions; **a registered-charity
number in the footer**; an embedded management-accounts appendix.

It looks like this schema's flagship evidence and **it is not this schema's file at all.** It is
`business_operations.board-governance`, and the fixture is written into `file_examples` with that
stated in its own `must_not_conclude`.

What discriminates: apply the deletion test. Strike the association name (never-alone), strike the
charity number (a status token — a field value, not a structure), strike the word *trustee* (a role
word alone). What remains is a governance cycle — notice, papers, attendance, minute, resolution —
which is `business_operations`' node exactly, on its own *"The documents are content-incoherent but
purpose-coherent."* grouping reason. **Nothing in the file names a non-exchange party.** No funder
with a restriction, no donor, no member roll, no beneficiary. The schema does not fire, and a
charitable footer must never promote a `business_operations` file into it.

**The fixture's twin, in the other direction:** `Thank you for your gift.pdf` — association
letterhead, charity number, a named individual, an amount, and the sentence that no goods or services
were provided. Here the non-exchange assertion *is* present, so a relation exists; but the **side is
unrecoverable from the bytes**, because the association keeps this as an issued acknowledgement and
the donor keeps the identical file as their own tax record, which is `finance`. The charity number is
on the page in both cases. This is why **Review Later** is named as a first-class fallthrough and why
`00`'s abstention rule is quoted on the row: *"Correct abstention is a successful outcome because the
product’s goal is reliable organization, not maximum file movement."*

---

## Reciprocal boundaries, both directions

Ten collisions are written into the JSON. The five that need the same fixture bytes named on both
sides:

**↔ `business_operations` (existential).** *Here:* only if a non-exchange party can be named. *There:*
everything else, including everything in the concession table. *Same bytes:* the trustee minutes
above, and a charity's FY26 budget — which is `budget-forecast`'s file unless a fund partition
appears in the column set, at which point both hold on disjoint evidence. *Reverse direction, stated
because it will be got wrong:* a company that donates, runs a foundation, or reports community
programmes does **not** enter this schema.

**↔ `business_operations.corporate-regulatory-filings`.** Called out separately from its anchor
because it is the seam most likely to be mis-drawn *in this row's favour*. It is not this row's.
Recommendation to R1c (not an edit): that row should name nonprofit regulator returns as its own, and
this row as also-holding on the restricted-fund note only.

**↔ `government`.** The roster's own split line — *the owner is a private association, not a public
authority* — and `government`'s landed `deterministic` list already excludes *"a private company,
charity, union, standards body, or member association with the same furniture … by owner role"*, so
the seam is half-drawn there already and this row completes it. *Same bytes:* a public grant
programme's file. The **administering office's** copy — decision record, applicant slots, statutory
power, case reference — is `government`; the **grantee's** copy — the application it submitted, the
offer it accepted, the reports it wrote — is this schema. Public money does not make a record
governmental; the side does.

**↔ `finance` and `finance.hoa-residents-association`.** Two forks. The **donor fork** (fixture twin
above). The **accounting fork**, which is `business_operations`' NJ-J-IND-3 read for this family:
the association's bank statements, ledgers and filed returns are custodial and statutory and are
`finance`'s; the **fund partition** is this row's. *This row does not claim the account — it claims
the partition.* And the HOA seam is the cleanest reciprocal on the row: **one dues notice addressed
to one member is `finance.hoa-residents-association`; the roll that generated a thousand of them is
this schema.** A treasurer who is also a member holds both, both activate on disjoint evidence, and
`finance`'s protective ordering runs first (CONNECTION §4 step 5). *Authored one-way here; R1c owes
the reciprocal, which that landed launch row could not have anticipated.*

**↔ `research.grants-funding`.** The sharpest open item, **NJ-NP-2**. Two grant lifecycles, one
landed and deep. *Discriminator:* what the money buys. Research output — award number, period of
performance, budget justification, indirect cost / F&A, biosketches, data-management plan, sponsor
portal — is that row. Service to beneficiaries — restricted purpose clause, outputs and outcomes
against agreed measures, beneficiaries reached, expenditure reconciled to cost headings — is this
one. It is legible in the **reporting structure**, never in the word *grant*. A research charity or a
university's charitable arm holds both. *One-way here; the landed neighbour was not touched.*

**↔ `hr` (asymmetric, deliberately).** Volunteers and employees share the agreement / rota /
induction / check / expense shape. The discriminator is payroll structure and it is largely an
**absence**, which is weak evidence — so the rule is asymmetric and written that way: **any
gross-to-net line anywhere makes the file `hr`, and `hr`'s posture governs.** Trustees and officers
are `hr`'s or `business_operations`' by the same logic; a trustee is not a beneficiary.

**↔ `clinical_practice`.** A beneficiary case record and a patient chart are both longitudinal
accumulation about one named subject held by a provider. Clinician role, diagnosis, treatment,
medication or clinical coding → `clinical_practice`, and the stricter side wins outright. Referral,
assessment of need, support plan and dated contact notes with no clinical structure → here. A hospice
or mental-health charity's corpus co-activates on most files, **and it should**.

---

## Neighbours considered that did **not** get an edge

- **`academic` / `career`.** A charity's training records and a volunteer's own certificate belong to
  the individual's side. No structure competes.
- **`creative` / `photos`.** Fundraising photography and campaign design assets are `creative`'s and
  `photos`' on capture and design structure. Worth one warning to template authors: **beneficiary
  photographs and consent forms are the family's most dangerous non-document artefact**, and any
  template that touches them inherits leg 3's posture, not `photos`'.
- **`construction_property`.** A charity that owns a building is a landlord or a client; those rows
  own it.
- **`code`.** Nothing competes.

---

## `proposed_fields` — four, and **all four are adoptions, not mints**

This is deliberate and it is the row's second defence against the charge: a family that had to invent
its own vocabulary would be admitting it was a tax status wearing a schema's clothes.

| Key | Status | Ask to R1c |
| --- | --- | --- |
| `organization` | already proposed by 13 rows | Adopt once for the roster. Must carry `business_operations`' seeded-ineligible condition. **No nonprofit synonym** — `charity` or `association` would encode tax status in a key name, which is the charge. |
| `fiscal_period` | already proposed by 9 rows | Adopt once. Note the family-specific fact: **a grant period frequently does not align with the financial year.** Either widen the definition or record the misalignment so a later `grant_period` proposal is not mistaken for a synonym mint. |
| `sponsor` | already proposed by `research.grants-funding` — **contested** | Adjudicate *with* that row, which itself prefers declaring canonical `institution` instead. What this row adds as evidence: the role-split case is **stronger** here, because a great many nonprofit funders are themselves charitable trusts, so **the same gazetteer string appears in both the funder and the grantee role within one corpus** — a sharper instance of `00`'s own warning that *"A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization."* Preference: (a) canonical `institution` on both; (b) `sponsor` once, role-split against `organization`; (c) **do not mint `funder` or `grantmaker`.** |
| `subject_of_record` | already proposed by `clinical_practice` | Adopt, and mark **`destination_eligible: false` for this family regardless of what `clinical_practice` needs.** This is the one key wanted *in order to be forbidden as a dimension*. Whether the canonical-fields shape permits a per-schema eligibility difference is **NJ-NP-5**; if it does not, the ban must live in the template contract and someone must write it there. |

Two `role_split` entries are recorded: `sponsor` ↔ `organization` (funder/grantee) and `organization`
↔ `subject_of_record` (provider/subject).

---

## Sparse-file discipline

The family's grouping axes are unusually strong — one grant reference, one fund, one appeal, one case
— which makes it unusually tempting to copy. `00`'s rule is quoted on the row and the JSON's
`file_examples` mark `group_without_copying_facts` where it bites: *"The graph does not automatically
copy those missing facts onto sparse files."* A grant reference read from an agreement is **not**
written onto a bare thank-you letter sitting beside it. And the stop rules hold: two associations'
registers do not merge, two grants' reports do not merge. Where nothing groups, that is a valid
outcome — *"Independent Records may live under Personal/Independent Records and hold standalone
certificates, notices, confirmations, forms, and PDFs that have a durable purpose but no broader
group."*

The `falls_through_to` list deliberately **inverts `business_operations`' ordering and names
Protected Records first**, because this family's characteristic isolated file is a named third
party's record, not a policy PDF. Six residuals, reused from `business_operations`' named set rather
than reaching for a seventh.

---

## The family-wide principle, for the ten templates

Written to be read by ten sibling authors, in the register of
`business_operations.research.md`'s never-alone section:

> **The non-exchange test.** No template in this family may activate on charitable status, an
> association name, mission vocabulary, or a document shape. Each of those four is never-alone here —
> and **charitable status is the family's own fourth token, the one no other family has to strike.**
> Every detection signal must name a **non-exchange party**: a funder whose money carries a purpose
> restriction, a donor giving without return, a member of the association, a volunteer giving unpaid
> time, or a named beneficiary receiving service without paying. If a template cannot name one, it is
> not a node — **it is `business_operations`, and it should say so and route there.**

Three corollaries:

1. **Differing in charitable function is not a difference.** *Fundraising*, *volunteering*,
   *advocacy*, *safeguarding* are values of a function dimension. What earns a row its node is a
   distinct **structure** — a fund-class column set, a gift declaration, a member roll with lapse
   dates, a rite register's entry-number series — never the topic word. This is the sentence that
   would have prevented the 574, restated for this family.
2. **No template may claim `time_first: true`,** and none may put a **named person** in
   `dimension_order`. The second is absolute and has no counterpart in `business_operations`.
3. **Refusing is success.** Three of the ten candidates are already marked weak in the JSON's
   `open_question` — volunteer-programme (discriminated by an *absence*), campaigning-advocacy
   (`go-to-market` with different nouns), and charity-regulator-return (**should not be built at
   all**; `corporate-regulatory-filings` owns that relation). *Keeping a row to preserve a legacy id
   is the 574's mistake.*

The seven this pass believes are defensible: **grant-funding-received, restricted-fund-accounting,
donor-and-fundraising, membership-register, beneficiary-service-record, safeguarding-record,
faith-rite-register.**

---

## Audits run before returning

- `python3 -m json.tool planning/domains/nodes/nonprofit.json` → **parses.**
- Key set compared programmatically against the landed `government.json` and `business_operations.json`
  (27 keys) → **exact match, symmetric difference empty.**
- `launch: "placeholder"`, `kind: "schema"`, `fields: []`, `template.dimension_order: []`,
  `time_first: false`, `provenance: "proposal"`, `design_cite: null` → **as PR-6 requires.**
- All `source_types` checked against `src/evidence_shape/vocabulary.py`'s exact list.
- **Every quotation machine-checked twice:** each constant `grep -F`'d against `00` before writing
  (26 unique spans, each found), then a JSON-walking regex re-extracted all `“…”` spans from the
  written file and confirmed all 26 present verbatim in `00`, with zero unconverted ASCII-quoted
  spans remaining.
- No canonical key minted; all four `proposed_fields` are adoptions of existing proposals, verified
  by enumerating every `proposed_fields` key across the landed roster first.
- **Files written: exactly two** — `planning/domains/nodes/nonprofit.json` and this memo. No
  neighbour, roster, contract, or `src/` file was edited.

---

## NEEDS-JOSEPH

- **NJ-NP-1 — the family's existence, answered narrow YES and reversible.** This schema stands only
  on the non-exchange relation and cedes governance, budgets, contracts, policies, procurement,
  audit, projects, IT, facilities and regulator returns to `business_operations`' landed rows. If
  R1c judges the non-exchange relation to be itself a field value rather than a structure, the
  correct outcome is **refusal**, with coverage routing to `business_operations` + `finance` + `hr` +
  `clinical_practice`. **This row would rather be refused than kept to save an id.**
- **NJ-NP-2 — the grant fork with `research.grants-funding`.** Alternatives: (a) two rows, with the
  reporting-structure discriminator stated reciprocally on both; (b) one shared grant node on
  whichever schema, the other also-holding. Not settled here; the landed neighbour was not touched.
- **NJ-NP-3 — the safety-domain gap.** Safeguarding and beneficiary material deserves safety-domain
  treatment and cannot have the flag, since `00`'s four are closed. `business_operations`' NJ-J-IND-4
  at higher stakes: **the third party here is often a child.** The substitute mechanism forcing P7
  ahead of any model path must be named somewhere.
- **NJ-NP-4 — the ten templates.** Seven defensible, two weak, one that should not be built. If ten
  are required, the weak three should be refused rather than invented.
- **NJ-NP-5 — per-schema field eligibility.** `subject_of_record` must be destination-**ineligible**
  for this family even if `clinical_practice` needs it otherwise. Unclear whether `canonical_fields`
  permits a per-schema difference; if not, the ban must move into the template contract.
- **Reciprocals owed by R1c** (this row authored them one-way and edited no neighbour):
  `business_operations`, `business_operations.corporate-regulatory-filings`, `government`, `finance`,
  `finance.hoa-residents-association`, `research.grants-funding`, `hr`, `clinical_practice`, `legal`,
  `applications.scholarship-fellowship`.

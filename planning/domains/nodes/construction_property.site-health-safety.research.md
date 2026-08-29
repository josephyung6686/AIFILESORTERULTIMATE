# `construction_property.site-health-safety` — lab notes

Depth: J-DEPTH (deepened from GIST, 2026-08-25). Placeholder row (J-IND). Absorbs legacy id
`cons.method-statement-ra` (ROSTER.md Appendix A).

**Verdict: the row stands.** It stands on **leg 3 first** — a privacy posture genuinely stricter
than its schema's — and on **leg 2 second**. Leg 1 is empty by contract and is argued, not skipped.
The gist verdict is **not** reversed, and this memo says why the three charges against the row do
not land, including the one that already refused a sibling in this family.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — authoritative. Every quotation below was
  `grep -F`-matched against this file before writing; the audit list is at the end.
- `planning/01-product-design-structured.md` — numbered rendering only; `00` wins.
- `planning/domains/CONNECTION.md` (node test §2, activation §4, closed edge vocabulary §5,
  failure modes §9, PR-6), `_CONTRACT.md` (rules 5, 6, 8, 10, 11–15), `ALIGNMENT.md`.
- `planning/domains/canonical_fields.json` — read to confirm that the two keys this row wants do
  **not** exist, which is why `proposed_fields` is empty and the want is recorded as prose.
- `planning/domains/roster.json` — every edge target below was checked mechanically against
  `nodes[].domain_id`. `government.public-authority-record`, `government.permit-licensing`,
  `hr.workplace-health-safety`, `manufacturing.hse-incident`,
  `business_operations.facilities-workplace` and `business_operations.compliance-audit` are all
  real roster ids.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked against every `file_examples` entry.

### The family, read before writing and not rewritten

- **`construction_property.research.md`** (the deepened schema anchor) — the default template, the
  never-alone list this row inherits, and — decisively for this memo — the **`timesheet` refusal**,
  which routes the site attendance register to this row *"under a **stricter** privacy posture than
  this schema's default"*. The anchor asserts this row's leg 3 on this row's behalf. That is
  corroboration, not licence, so leg 3 is argued from the documents below as well.
- **`construction_property.compliance-certificate.json`** — the family's landed refusal, and the
  charge this memo has to answer first.
- **`construction_property.construction-project.research.md`** — the spine. It names
  *"A method statement or risk assessment"* among the files that are **not** its evidence, saying
  *"`construction_property.site-health-safety` owns it"*, and it declines an `hr` edge because
  *"the confusable document family is `site-health-safety`'s"*. Both boundaries are honoured here
  unchanged.
- **`construction_property.site-diary.research.md`** — leaves the accident-book entry to this row,
  in its words *"because an injury narrative about a named person is health information and the
  safety ordering must run first."* Honoured unchanged, `also_schema: medical` included.
- **`construction_property.snagging-defects.research.md`** — declined a stricter posture on
  attributed-failure material and named this row as the only sibling that has one. Its NJ-CP-SNAG-3
  is the mirror of this row's leg 3 and this memo does not contradict it.
- **`construction_property.building-control.research.md`** — already authored this family's
  `government` seam. This memo extends that seam to the safety regulator **using the same rule**
  (custody and role, never the reference number) rather than inventing a second one.

### A source that is not available, and it matters

`government` is an **unwritten schema**. Its seam is therefore authored one-way here, exactly as
`building-control` authored its own, and R1c owes the reciprocal. Nothing below assumes a
`government` row's contents; it states only what `construction_property` gives up.

---

## The charge against this row, answered before the node test

The dispatch names three. They are answered first because if any of them lands, the node test is
academic.

### (a) "It is a document type — the charge that refused `compliance-certificate`"

This is the serious one, and it deserves the sibling's own reasoning applied honestly rather than
distinguished away. `compliance-certificate` was refused because, when its candidate signal was
stripped, *"what remains is a document-type word plus an address — and **BOTH** halves are
constitutionally never-alone"*, so it would have been *"a row that never fires."*

Run the identical strip on this row. Remove the words *risk assessment*, *method statement*,
*permit*, *induction*, *accident report* — every document-type word — and remove the site address.
**What remains is still four structures**:

1. A table whose columns are *hazard / who might be harmed / existing controls / likelihood /
   severity / residual / further action with an owner and a date*. The **likelihood–severity–residual
   triple** is a computed relationship between three cells, not a label. `00` licenses reading it:
   *"Tables matter because resumes, forms, applications, invoices, and administrative documents often
   place their most useful information in cells rather than body paragraphs."*
2. A **time-bounded authorisation**: an issue time, an expiry time, an issuer, an acceptor, and a
   hand-back or cancellation signature. The *issue-and-hand-back time pair on one form* appears
   nowhere else in this family. A certificate has one date; this has a lifespan measured in hours.
3. A **register with a signature column** — a list of names, each signed and dated, under one topic
   heading.
4. A **periodic re-inspection record** carrying an item identifier, an inspection date and a
   **next-due date**. The next-due date is the discriminator: it says the document expires and will
   be replaced. A certificate says a completed thing conformed once.

None of those four is a word, and none of them is an address. That is precisely what
`compliance-certificate` could not produce. **The two rows are not the same kind of claim:** a
certificate is a *statement about a finished installation*, this row is a *hazard and its controls
over time*, which is this row's own framing: the anchor is a hazard and its controls, not a document
kind. And the family already put the boundary in writing from the other side: this row's
`collides_with` on `compliance-certificate` discriminates on exactly the axis above — periodic
re-inspection with a next-due date is this row's; a one-off signed conformity statement is not.

The charge is **rejected**, and the refusal it comes from is left standing and uncontradicted.

### (b) "It is a `work_type` stage of `construction-project`"

Partly true and not sufficient. The anchor's warning is real: *"`variation`, `snagging`,
`dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`, `schedule`, `survey`,
`valuation` and `report` are **values of `work_type`**, not rows."* If safety paperwork were merely
another value on that list, this row would be the 574 mistake repeated.

Three reasons it is not, in ascending strength:

1. **It is not scoped by the project.** Safety documents exist where no project does: a training
   matrix and a competence card belong to a *person* and travel with them; a company safety policy
   belongs to the *firm*; a generic RAMS library belongs to *nobody*. The spine's own scoping
   sentence cannot reach them. Every other work-type value on the anchor's list is meaningless
   outside an instruction.
2. **The spine has formally conceded it.** `construction-project` lists the method statement and the
   risk assessment among files that are **not its evidence**, and lists the induction register among
   files it must not collect. A `work_type` value cannot be conceded away by the row that would
   carry it; that concession only makes sense if the situation is somebody else's.
3. **The privacy posture, which no `work_type` value can carry.** A value does not change how a file
   is handled. This one does — see leg 3. A stricter posture attached to a *value* would be
   unenforceable, because the value is not known until after extraction, and *"Privacy policy must be
   enforced before content reaches any model or external connector."* The posture has to attach to
   the recognised situation or it does not exist.

The charge is **rejected**, but it is why leg 1 below is argued as failing rather than quietly
passed.

### (c) "It is `government`'s regulatory material"

**Some of it is, and the seam runs through individual documents** — exactly as `building-control`
found. That row already wrote this family's rule, and the rule is **custody and role, not subject
matter**, with the warning that *the reference number is on both copies and discriminates nothing.*
This memo applies that rule unchanged rather than authoring a second one.

| Evidence present | Side |
|---|---|
| a notice **served on** the holder — an improvement or prohibition notice stating a contravention *the holder must remedy* by a date | **`construction_property.site-health-safety`** |
| the holder's own **notification to** a regulator (a reportable-incident notification and its acknowledgement), filed beside the incident report it arose from | **`construction_property.site-health-safety`** |
| the holder's **response**: revised RAMS, evidence of remedy, correspondence closing the notice | **`construction_property.site-health-safety`** |
| an **issuing** letterhead and inspector's signature block the holder controls; the inspector's **own visit report or case file**; a register entry; an enforcement decision written to justify a statutory power | **`government.public-authority-record`** (or a more specific `government` row when that schema is written) |
| an instrument licensing an **activity or occupation of the public realm** — a scaffold licence, a skip permit, a hoarding licence — as opposed to an internal permit to work | **`government.permit-licensing`** |
| a regulator's **guidance leaflet or approved code of practice** downloaded by the holder | **neither.** Reading Inbox or Reference Clips; it is published material about no site |
| role does not settle | **neither activates** — *"Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement."* |

**Where `construction_property` stops:** at the moment the holder is the *author of the statutory
power* rather than its subject. **What `government` must not take:** a notice addressed to the
holder, the holder's own incident notification, and the remedial evidence assembled to discharge it —
these are the holder's obligations, filed against the holder's site, and they are worthless to the
holder anywhere but beside the RAMS they contradict.

The charge is **rejected as to the received half** and **conceded as to the issued half**, which
this row does not claim. Authored one-way; recorded as NJ-CP-HS-3.

### And the privacy leg of the charge, taken in the right direction

The dispatch asks whether accident and near-miss records warrant a **stricter** posture, and warns
via `construction_property.agency-listing` that *getting a privacy posture wrong permissively is the
expensive error.* Taken seriously, and the answer is yes — see leg 3. The direction matters: the
error this row could make is not claiming too much protection but too little, because the exposed
person is an injured operative who never chose to be in the holder's filesystem.

---

## The node test, leg by leg

CONNECTION.md §2: a template row exists only when its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. One leg suffices.

**The schema's default template, stated so the difference is measurable** (quoting the anchor):

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation genuinely cycles. **Not time-first.**

### Leg 1 — recommended dimensions: **fails, and is recorded as failing**

`dimension_order` is empty by binding contract (a dimension may only branch on a field the same
entry's schema declares, and `construction_property` declares none — D1 as narrowed, `_CONTRACT`
rules 10 and 15, CONNECTION PR-6). Run against the prose default anyway, this row's shape is
**site → safety function → task or package** — which is the default with `instruction` replaced by
a function level, and the anchor is explicit that reordering *"is not a difference that earns a
node"*.

Two structural qualifications are worth recording even though they do not rescue the leg, because
they are real and unresolved: **generic template packs belong outside any site branch** (they belong
to no site), and **incident records may belong outside the project tree entirely**, for retention and
access reasons rather than organisational ones. If either is eventually honoured, this leg becomes a
genuine divergence; today it is not, and pretending otherwise would manufacture a passing leg.

**Verdict: fails.**

### Leg 2 — detection signals: **passes**

The four structures in section (a) above. Each was tested against the rest of the family before being
claimed:

- The **hazard matrix** is not the measured-works table (works description, quantity, unit, rate,
  amount), not the conditions schedule, not the apportionment schedule, and not the valuation's
  *to date, less previously certified* arithmetic. It is the only table in this family whose columns
  are a *judgement about a future event* rather than a quantity or a sum.
- The **permit's issue-and-hand-back pair** appears nowhere else in the catalogue, as far as this
  pass could establish. Marked **inference** — it is the kind of claim R2 could turn into a rule.
- The **signature register** is the weakest of the four and is explicitly never-alone: a signed name
  list is also a delivery log, a meeting sheet, a petition and a payroll sign-off.
- The **next-due date** on a periodic inspection is what separates this row from the certificate
  world, and it is a *labelled slot*, not a date-shaped token — the row's never-alone list forbids
  reading any unlabelled date as an expiry.

What is deliberately **not** offered as a signal: the safety vocabulary. *Hazard, risk, control, PPE,
near miss* are dense in office fire assessments, school trip forms, event stewarding plans and
care-home records. Vocabulary is the trap, structure is the signal — the same distinction the anchor
draws for the whole family (*"that structure, not the vocabulary of buildings, is what makes the
schema detectable"*).

**Verdict: passes.**

### Leg 3 — privacy rules: **passes, and this is the row's strongest leg**

The schema's posture is `potentially_sensitive` on three grounds: the material names a real person's
home and who is in it; `00`'s corpus sentence covers what the family carries; and the exposed party
is usually not the user. Every sibling inherits it. `snagging-defects` and `construction-project`
both examined whether they were stricter and both honestly answered no.

This row is stricter, on grounds none of its siblings share:

1. **It carries medical information about identified third parties as its ordinary content, not as
   an accident of scope.** An accident report *is* an injury description with a named person, a body
   part, a treatment and sometimes an ambulance. `00`'s corpus sentence names the category —
   the corpus *"can include identity documents, account statements, tax records, medical information,
   legal records, credentials, private correspondence, GPS metadata, employment materials, and
   educational records"* — and three of those ten are on one page of this row's most common form.
2. **`00` designates that material for protection ahead of placement.** *"Finance, identity, medical,
   and legal material should be implemented first as safety domains, meaning the system detects and
   protects them before any cloud or automated placement decision is allowed."* This row's schema is
   **not** one of the four; the *material* is. The consequence is the specific rule this row asserts
   and no sibling does: **on a file naming an injured or health-assessed individual, the medical
   ordering runs first and this row's recognition runs second.** That is why the people-bearing file
   examples carry `also_schema: "medical"` or `"identity"` and route to Protected Records, and why
   `site-diary` deferred the accident book here rather than keeping it.
3. **The data subject is neither the holder nor the holder's counterparty.** The schema's third
   ground says the exposed party is usually not the user — a client, a tenant. Here it is usually not
   even a *party*: a subcontractor's labourer, a visitor, a member of the public struck by falling
   material. They have no relationship with the filesystem's owner at all and no route to object.
   A competence card scan additionally carries a photograph and a date of birth — identity material
   about someone who handed it over to be allowed on site, for one week, in 2019.

The operative consequence, stated so it can be checked: **Protected Records is this row's default
residual for its people-bearing members, not its exception** — the only row in the family of which
that is true. *"Protected Records may represent sensitive isolated material such as passport scans,
medical documents, account statements, visas, legal forms, or credentials; it should normally remain
local-only and must not cause filenames or content to be exposed in model prompts."*

No `is_safety_domain` flag is set (`00` names four safety domains and this schema is not among them)
and no P7 handling class is assigned; that is P7's. The gap that leaves is NJ-CP-HS-4.

**Verdict: passes.**

### Overall

**Kept, on legs 2 and 3, with leg 1 recorded as failing.** Two legs is more than §2 requires and
more than the deepened spine itself has. The gist row asserted the same conclusion; this pass has
tested it against the family's own refusal standard and it survives.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting ones.

| File | Why it is not this row's evidence |
|---|---|
| `Office fire risk assessment 2026.docx` *(kept as a file example)* | **The load-bearing false positive**, retained deliberately because it defeats the row's own fingerprint — the matrix is identical, cell for cell. Discriminated by what surrounds it: a premises, an occupier, a floor plan and a responsible-person designation are `business_operations.facilities-workplace`'s; a task sequence, plant, a works package or a permit regime are this row's. |
| Generic downloaded or purchased **RAMS template packs** | Not records. A document with placeholders and a supplier's footer proves nothing was assessed. Reference Clips. This is the row's primary false-positive *family*, not a single file, and separating it from a site-specific pack is the row's central `needs_llm` determination — the two are the same document by most of their word count. |
| **Employer's and public liability insurance certificates** | They travel inside safety packs constantly. Their anchor is a policy and an insurer, which is `finance.insurance-corporate`'s world. They appear here only as members of a submitted pack. |
| **Asbestos surveys** (refurbishment/demolition) | `construction_property.site-survey`'s. A pre-works investigation of a building is a survey; its safety consequence is downstream. Recorded on that row, not annexed here. |
| `Health surveillance report - noise - K Adeyemi.pdf` *(added this pass as a file example)* | **The file that must not be lost to this row.** Individual health monitoring has an *employment* anchor, not a site one — `hr.workplace-health-safety` plus the medical posture, both stricter. This row's `also_schema: "medical"` makes it tempting to over-collect; the discriminator is that there is no hazard-and-control table and no works package. |
| A signed **dayworks sheet** | Routed by the family's `timesheet` refusal to `variation-claim`. It carries names and hours and would be easy to take; taking it would contradict a landed refusal. |
| A **site attendance register** | This *is* routed here by the same refusal — recorded so the row is seen applying the refusal in both directions rather than only where it gains. |
| A **CIS return, a site payroll run** | `finance` and `hr`. Names on a site are not employment apparatus. |
| A **programme / Gantt** with a safety milestone | `construction-project`'s. A plan is not a hazard record. |
| A regulator's **guidance leaflet** or approved code of practice | Reading Inbox. Full vocabulary overlap, zero evidence about any site. The strongest argument that vocabulary cannot be a signal here. |
| A **CDM appointment letter** | Genuinely contested: it is a contractual appointment (`subcontract`, `contract-administration`) that exists only because of a safety regime. Left with the contractual rows; recorded because it is the one file this pass could not settle cleanly. |
| A **first-aid certificate** for the holder personally | `career` / `identity`. A qualification about oneself is not a site record. It becomes this row's only inside a training matrix assembled for a site or a submission. |

---

## The collision fixture, in both directions

**Inbound — a file that would wrongly fire this row.** `Office fire risk assessment 2026.docx`.
Same matrix, same likelihood–severity–residual triple, same vocabulary, and a company address in the
header that looks exactly like a site address. **Both rows must name the same bytes**, and this one
does: the discriminator is the *subject of the assessment* — a premises being occupied versus a task
being carried out. Where neither is present, neither row fires.

**Inbound, second — the government fixture.** `Improvement notice - 18 River Court - received.pdf`.
The notice reference is identical on the regulator's copy and the holder's, and it discriminates
nothing at all — `building-control` already established that this is the strongest-looking and most
worthless token in the family. Custody decides: served on the holder, or issued by the holder.

**Outbound — a file that must not be lost to this row.**
`Health surveillance report - noise - K Adeyemi.pdf`. Every surface signal points here: a
construction employer, an occupational hazard, a named operative, a medical posture. It is
`hr.workplace-health-safety`'s with a `medical` overlay, and the absence of a site, a package and a
hazard table is what says so. If this row takes it, the row has become "anything about a worker's
body," which is the annexation the `hr` collision edge exists to prevent.

---

## Reciprocal boundaries, both directions

Every neighbour below was read before this table was written, and none of them is contradicted.

| Neighbour | This row must not take | The neighbour must not take | Same bytes both sides name |
|---|---|---|---|
| `business_operations.facilities-workplace` | a premises safety file, a DSE assessment, a responsible-person designation | a task-sequenced method statement, a permit to work, a site induction register | `Office fire risk assessment 2026.docx` |
| `hr.workplace-health-safety` | an individual's health surveillance, an occupational-health referral, an organisation-wide policy with no site, workforce accident statistics | a site-specific RAMS, a permit, a scaffold inspection | `Health surveillance report - noise - K Adeyemi.pdf` |
| `manufacturing.hse-incident` | an incident anchored to a production line, a machine asset number or a batch | an incident anchored to a site address, a works package or a principal contractor | an identical incident form differing only in its location block |
| `construction_property.subcontract` | the order, the payment application, the payment notice | the hazard matrix, the permit, the toolbox-talk register inside the submitted pack | `PQQ safety pack - Meridian Ltd.zip` |
| `construction_property.site-diary` | a day narrative that merely mentions a permit or an induction | the accident-book entry itself — deferred here by that row, *with the medical ordering running first* | an injury described in a diary entry and in a report on the same date |
| `construction_property.construction-project` | the job envelope, the head contract, the programme | the method statement, the risk assessment, the induction register — all conceded by that row | `Induction register - March 2026.xlsx` |
| `construction_property.compliance-certificate` *(refused)* | a one-off signed statement that a completed installation meets a named standard | a periodic re-inspection carrying a next-due date | `Scaffold inspection - week 11.pdf` |
| `business_operations.compliance-audit` | a management-system standard, an audit programme, an auditor's non-conformity register | a site safety inspection tied to a task and a hazard | a corrective-action log |
| `government.public-authority-record` *(schema unwritten)* | an issuing letterhead, an inspector's own case file, a register entry, an enforcement decision | a notice served on the holder, the holder's own incident notification, the remedial evidence discharging it | `Improvement notice - 18 River Court - received.pdf` |
| `government.permit-licensing` *(schema unwritten)* | a scaffold licence, a skip permit, a hoarding licence | an internal permit to work with an issuer, an acceptor and a same-day hand-back | the word "permit" and a number |

The two `government` seams are authored **one-way**; R1c owes the reciprocals.

---

## Sparse-file discipline

`Toolbox talk - manual handling - signed.jpg` is this row's `HW 3` case: a photographed sign-in sheet
with a topic, some signatures and a date, and **no site, no package, no company**. It may join a P9
group with the site's other safety material without this row writing a site fact onto it —
`group_without_copying_facts`. The prohibition is the same one `00` states for a course fact on a
homework file, and it bites harder here because the neighbouring files name real people.

Two never-alone rules do the heaviest work on this row's real corpus and are worth naming again:
**membership in a download session is not evidence** (*"A session should never be treated as proof of
topic"* — a document-portal export pulls an entire project down at once, safety pack included), and
**a PDF author or producer string is not evidence** (*"PDF metadata should be treated as supporting
evidence, not as truth"* — one contractor's template stamps the same firm on every blank form it ever
generated, including the generic ones this row must reject).

---

## `proposed_fields`

**Empty, and deliberately.** The schema declares no field rows (D1 as narrowed, PR-6), and a template
may not mint keys. Three candidates are recorded here as **prose**, for whoever answers the schema
row's `open_question`, and are **not** minted as variants:

1. **A site/project key.** Wanted by nearly every row in this family, which is an argument for one
   schema-level proposal at R1c rather than twenty-seven template-level ones. This row **seconds the
   family's existing proposal**; it does not propose its own.
2. **A safety-function key** (assessment and method / permits / briefings and registers /
   inspections / incidents). This is the one candidate that would be *this row's* rather than the
   family's, and this pass declines to propose it, because it is a `work_type` in everything but
   name and the schema anchor's sharpest warning is against exactly that move.
3. **The authored-versus-submitted role.** No canonical key expresses "the holder wrote this" versus
   "a counterparty submitted this." `business_operations.contract-administration` records the same
   hole for buying versus selling. **One canonical proposal should serve all three rows** — this row
   seconds it rather than minting a variant. Recorded as NJ-CP-HS-2.

---

## Neighbours considered that did **not** get an edge

- **`medical` (schema)** — a real relationship, and its absence from `also_holds_with` is not a claim
  that no medical overlap exists. `also_holds_with` joins **schemas**, and this is a template row, so
  the correct expression is `also_schema: "medical"` on the people-bearing file examples plus the
  protective routing. Recorded so R1c does not misread the empty array.
- **`identity` (schema)** — same treatment, via the competence-card example.
- **`legal.personal-legal-matters`** — an injury claim eventually becomes one, but at the document
  level there is no shared discriminating evidence item; an edge would be topic similarity.
- **`legal.practice-matter-file`** *(landed)* — once litigation starts the solicitor's file is that
  row's, on custody. No document-level confusion, so no edge.
- **`resource_operations.*`** and **`logistics.driver-compliance`** — genuinely similar safety
  regimes. Rejected because their discriminating anchors (a well, a mine, a vehicle) do not appear on
  this row's files. Adding the edges would have been taxonomy, not evidence.
- **`hr.training-development`** — the training matrix is confusable, but `hr.workplace-health-safety`
  already carries the whole people-shaped seam and a second `hr` edge would split one boundary across
  two rows.
- **`construction_property.building-control`** — considered, and rejected as a *collision*: the
  construction phase plan and the building-control application both sit in a compliance folder, but
  no evidence item is shared. That row's value here is its **method** for the government seam, which
  this memo reuses, not an edge.

---

## NEEDS-JOSEPH (this node only)

- **NJ-CP-HS-1 · Where incident and health-surveillance records live.** Stated reciprocally: this row
  claims incident reports as its *situation*, and simultaneously concedes that the medical protective
  ordering runs first on any file naming an injured person — so the file is **detected here and
  protected there**. What is undecided is the eventual folder home. **Alternatives and costs:**
  *(a) inside the site branch* — organisationally correct, keeps the incident beside the RAMS it
  contradicts; costs a named injury sitting one folder from a subcontractor's quote. *(b) outside the
  project tree, under the protective route* — privacy-correct; costs the investigative link that
  makes the record useful. This is a retention-and-access decision about real people and is Joseph's.
- **NJ-CP-HS-2 · The authored-versus-submitted role.** Reciprocal with
  `construction_property.subcontract` and `business_operations.contract-administration`. A
  subcontractor's safety pack is that row's engagement evidence and this row's hazard evidence, and
  no document-level evidence says which side of the transaction the filesystem is on.
  **Alternatives:** one canonical role key at R1c (preferred — three rows already want it), or
  permanent abstention on submitted packs (safe, and loses a large real corpus).
- **NJ-CP-HS-3 · The `government` reciprocal, owed.** *(New this pass.)* The seam table above is
  authored one-way because the `government` schema is unwritten. It is drawn to match
  `building-control`'s and should be adopted or amended **as a family**, not per row, so
  `construction_property` does not diverge from itself. R1c owns this.
- **NJ-CP-HS-4 · Does a stricter-than-schema posture need machinery that exists?** *(New this pass.)*
  This row asserts a posture stricter than its schema's, but the catalogue has only
  `none | potentially_sensitive`, and handling classes are P7's. **Alternatives and costs:**
  *(a) leave it as prose plus protective routing* — what this pass did; costs the risk that the
  assertion is decorative because nothing enforces it. *(b) ask P7 for a construction-safety handling
  class* — enforceable; costs a P7 dependency and a precedent other rows will want. The
  `agency-listing` lesson says the permissive failure is the expensive one, which argues for (b).

---

## What changed in this pass — checked line by line against the JSON as written

The JSON was already substantial and was **verified and extended, not rewritten**. Every claim below
was re-read out of the written file before this section was finalised.

**Preserved unchanged** (all of it verified against the sources named above and found sound):
the `stands` verdict; `refuse_node: false`; `fields: []` and `proposed_fields: []`;
`template.dimension_order: []` with its prose recommendation; all ten original `file_examples`;
all ten `recognition.deterministic` entries, seven `needs_llm` and ten `never_alone` entries; the
eight original `collides_with` edges; all six `falls_through_to` routes; `sensitivity` and
`sensitivity_why`; `open_question`; the empty `also_holds_with` and `role_split` (both argued above
rather than left silent).

**Added to the JSON this pass** — three changes, and only three:
1. `one_line`: the retired phrase *"Gist-level placeholder (J-IND)"* replaced by
   *"Placeholder row (J-IND, researched to J-DEPTH)"*. No other wording touched.
2. A ninth `collides_with` edge: **`government.public-authority-record`**, the custody seam, drawn
   to match `building-control`'s and marked one-way with the reciprocal owed.
3. Two `file_examples`, taking the list from ten to twelve:
   **`Improvement notice - 18 River Court - received.pdf`** (the government fixture; `facts_legal: []`,
   falls through to Independent Records) and
   **`Health surveillance report - noise - K Adeyemi.pdf`** (the outbound fixture — the file that must
   *not* be lost to this row; `also_schema: "medical"`, `group_without_copying_facts: true`, falls
   through to Protected Records).

**Nothing was reversed.** The gist verdict stands and is now argued rather than asserted.

**Added to the memo** (which is where the deepening mostly lives — the memo grew from 4,773 bytes):
the three dispatch charges answered explicitly, including the `compliance-certificate` strip test
applied to this row; the node test argued leg by leg with **leg 1 recorded as failing**; the schema's
default template quoted so the difference is measurable; a twelve-row files-considered-and-rejected
table; collision fixtures in **both** directions; a ten-row reciprocal boundary table naming the same
bytes on both sides; the sparse-file discipline section; the `proposed_fields` prose with an explicit
**second** of the family's existing proposals rather than variants; and two new NEEDS-JOSEPH items
(NJ-CP-HS-3, NJ-CP-HS-4) alongside the two preserved ones.

---

## Audits run before returning

- `python3 -m json.tool` on the node file — **parses**.
- Every quotation `grep -F`-matched verbatim against
  `planning/00-database-agent-product-design.md` — **all match**.
- Every `collides_with` and `falls_through_to` target checked against `roster.json` `domain_id`s and
  `00` §7.3 residual names — **all real**.
- Every `file_examples.source_type` checked against `SOURCE_TYPES` in
  `src/evidence_shape/vocabulary.py` — **all valid**.
- No numeric thresholds, no confidence scores, no P7 handling classes, no invented field keys.
- Files written: **only** `construction_property.site-health-safety.json` and this memo.

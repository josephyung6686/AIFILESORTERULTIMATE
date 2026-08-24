# `business_operations.compliance-audit` — lab notes (template row, deepened to J-DEPTH)

**Depth: J-DEPTH.** Deepened from the gist draft under `DEEPEN-ADDENDUM.md`. The gist draft's verdict
— the row stands — is **preserved and not reversed**, but the row it stands as has been **narrowed**:
see *What changed in this pass* at the end.

---

## Sources actually used

### Binding

- `planning/00-database-agent-product-design.md` — every quotation below was greped back verbatim
  against this file before the memo was written. No quotation is paraphrased inside quote marks.
- `planning/domains/_CONTRACT.md` (rules 6, 10, 15), `planning/domains/CONNECTION.md` (§2 node test,
  §4 step 2 activation, §5 invariant 2, §9 failure modes), `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json`, `planning/domains/canonical_fields.json`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed and J-IND, both ratified.

### Rows read before writing, and not touched

- **`business_operations.research.md`** (schema anchor). Supplies (i) the family's default template
  paragraph this row must differ from, (ii) the **never-alone principle generalised for all 24
  siblings**, (iii) the sentence that decides this row: *what earns a sibling its node is a distinct
  **structure** — "a tender evaluation matrix, an asset register with serials and lifecycle dates, a
  risk register with likelihood/impact scoring columns" — not the topic word.*
- **`business_operations.organisational-records.json`** — the family's refusal, read first on the
  assumption this row might be heading the same way. It is not; §*Why this is not
  organisational-records* below says why, in its own terms.
- **`construction_property.compliance-certificate.json`** — the landed refusal that is the charge
  against this row. §*Why this is not compliance-certificate* is the longest section here, because it
  is the section the dispatch asked for.
- **`business_operations.policy-handbook.json` / `.research.md`** — deepened in the same pass.
- **`business_operations.risk-register.json`** — deepened in parallel. Read, **not edited**; its own
  `collides_with` against this row is quoted and honoured below.
- **`finance.small-business-bookkeeping.json`, `finance.tax-filings.json`, `finance.cap-table-equity.json`**
  — the landed launch rows that own the money side of the word *audit*.

---

## Applying the family's never-alone principle, explicitly

The schema row states it as a rule for all 24 siblings:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** … Every detection signal a sibling writes must pair a **structure** with a
> **labelled slot**.

Applied here, honestly, one candidate signal at a time:

| Candidate signal | Verdict |
|---|---|
| The audited entity's name | **Never-alone.** Read across from 00: *"A university name alone should not create a group because Columbia can appear as an authoring school, course provider, target institution, employer, research venue, or merely a cited organization."* A company name is worse — it appears as employer, customer, supplier, competitor and regulator. Marked as inference; 00 writes that sentence about a university. |
| Compliance vocabulary — *control, audit, finding, remediation, attestation* | **Never-alone.** Every regulated family on the roster uses it, and so does a consultancy's sales deck. |
| A certificate shape | **Never-alone**, and this is where `compliance-certificate` died. Insurance, training, trade and personal credentials share the shape exactly. |
| A standard's name or number | **Never-alone.** Carried equally by the published standard, a job description and a training course. |
| A **finding structure** — a referenced finding crossed with a severity slot, a management response, a named owner and a target date | **PASSES.** A structure paired with labelled slots. |
| An **evidence-request (PBC) structure** — numbered requests against due dates and a received/outstanding marker, requested by a party named as distinct from the holder | **PASSES**, and is the strongest signal in the row: it exists in no other situation in the family. |
| The **cross-reference chain** — a request number recurring on an artifact, a finding reference recurring on a corrective action and on its closure evidence | **PASSES**, and is what actually holds the group together. |

Three signals clear the family's bar. That is the whole case for this row, and it is a structural
case, not a vocabulary case. **A new `never_alone` entry was added in this pass** to close the
remaining hole: a repeated standard name or audit year linking the members of a candidate pack is
exactly 00's stop rule — a group must not form *"when one high-frequency entity acts as the only
bridge"*. The chain must recur across members, not the name.

---

## Why this is not `construction_property.compliance-certificate`

The refusal there rests on five moves. Taken one at a time — and this row concedes one of them
outright rather than arguing all five.

**1. "The candidate signal is a document type plus an address, and both halves are never-alone."**
Different here. Strip this row's signals to the same depth and what remains is not a document type: it
is a **multi-document chain with an internal reference structure** (request № → artifact → finding
ref → corrective action → sign-off) produced by a **three-party asymmetry** — an assessor structurally
distinct from the assessed. A document type is a property of one file. A chain and an asymmetry are
properties of a *situation*, which is the thing a template row is for. This is the same distinction
the schema row draws when it says a tender evaluation matrix earns `procurement-sourcing` its node
while the word "procurement" does not.

**2. "The word 'certificate' is a `work_type` VALUE."** Conceded, and it applies to this row too.
`internal audit report` and `certificate of registration` are *values* on this row's own
`work_types[]`. This row is therefore **not built on either word**, and its `one_line` now says so.
The activation case rests on the finding structure, the request list and the chain — none of which is
a work type.

**3. "The coverage is already carried elsewhere, three times over."** This was the *deciding*
evidence there, and it is the one that most cleanly separates the two rows, because it is checkable
rather than arguable. It is **false here, and the neighbours say so themselves.** Both of the two rows
that could plausibly carry this coverage explicitly hand the audit side back:

> `business_operations.risk-register` → this row: *"an external standard, a control identifier, an
> auditor and an assurance opinion supports the audit row; a management-owned register with treatment
> and appetite supports this row."*

> `business_operations.policy-handbook` → this row: *"an audit or standard reference, a control
> identifier, a finding, or an auditor's request-list position supports the audit row; the governing
> document itself, with its control block, supports this row."*

`compliance-certificate` failed because `finance.household-property`,
`construction_property.building-control` and its own schema row had **already claimed** its material.
Nothing has claimed the assessment chain. Refusing this row would leave the request list, the finding
tracker and the closure evidence with no home but `Review Later` — coverage lost, not rerouted.

**4. "Its purpose is a residual's purpose — a durable standalone record with no broader group."**
This is the exact inverse of this row. Its anchor **is a group**: 00's own content-incoherent /
purpose-coherent case. *"The documents are content-incoherent but purpose-coherent."* A row whose
anchor is a group cannot be a residual wearing a domain's clothes, because residuals are 00's answer
to files that have *no* group.

**5. And the concession.** The half of this row that most resembles `compliance-certificate` — the
**standalone certificate** — is hereby **given up**. In the gist draft
`Certificate of Registration - ISO 9001.pdf` sat as a plain member. It is now marked
`must_not_conclude: activation of this row from the certificate ALONE`, the certification detection
signal is rewritten as *"the WEAKEST signal in this list and never sufficient by itself"* and requires
a visible assessment cycle around it, and 00's Independent Records sentence — which *names standalone
certificates first* — is quoted at it. This row **seconds** the `compliance-certificate` refusal
rather than reclaiming its material through the side door. That narrowing is the single most important
change in this pass.

---

## Why this is not `business_operations.organisational-records`

That refusal's core: *"material that carries an organisation name and a document type but no more
specific operational sub-domain — which is not an organizational situation but the ABSENCE of one."*
The test is whether anything is left after you remove the entity name and the document-type word. For
`organisational-records`, nothing was. Here, the request list, the finding table and the cross-
reference chain survive that subtraction intact — none of them is an entity name and none of them is
a document-type word. The refusal's diagnostic is applied and passed, not dodged.

---

## Why this is not a `work_type`

The charge is fair on its face: *auditing* is an activity, and CONNECTION §9 lists work types as
schemas among the forbidden constructions. The answer is the schema row's own sentence — *"Differing
in business function is not automatically a difference"* — and its remedy: the row must name a
structure. It does, three times over. Note also what this row does **not** do: it does not ask for a
child node per audit type. `internal audit`, `external assurance`, `surveillance audit` and
`certification audit` are all **values** on `work_types[]`, exactly as the dispatch prompt requires.

---

## The node test, leg by leg

CONNECTION §2: a template row exists only when its **detection signals**, **recommended dimensions**,
or **privacy rules** differ from its schema's default template.

### Leg 1 — detection signals. **DIFFERS. This leg carries the row on its own.**

The schema's default template activates on the family's generic shape: an organisational unit running
a cycle producing a document with a function. Three signals here are absent from that shape and from
every sibling's:

- **The evidence-request list.** Numbered requests against due dates with an outstanding marker, from
  a requester named as external to the holder. No other situation in this family produces a document
  whose entire content is *"prove these things to me by these dates."*
- **The finding structure.** A reference, a severity slot, a management response, a named owner, a
  target date. `risk-register` has the nearest table and its own row says the discriminator is real:
  an inherent-and-residual pair with a likelihood/impact scale is the register; a finding raised *by
  an identified assessment* with a corrective action is this row.
- **The assessor/assessed asymmetry.** A named auditor or firm distinct from the entity being
  audited, appearing in a labelled slot. The rest of the family produces documents whose author *is*
  the entity.

Two of the three are labelled-slot structures; the third is a structural relation between two named
parties. `00` licenses the underlying grouping: *"Purpose must be a first-class facet. Topic answers
what a file is about, while purpose answers what the file was for."*

### Leg 2 — recommended dimensions. **DIFFERS, narrowly, and the row does not lean on it.**

Argued in full in `template.why`. Summarised: the family default is *entity (conditional) → body /
project / contract / account → fiscal period → function*. An assessment occurrence is a cycle and this
row **does not pretend that level is new**. Two things do differ:

- The **standard** sits above the occurrence and is neither the entity nor a project. It is an
  external referent belonging to somebody else, and it outlives every occurrence beneath it — one
  standard, one certificate number, four audits across four years.
- The **fiscal period must drop** below the finding level or fall out. A finding opens in one year and
  closes in another; filing it under the year it was raised separates it from its own closure
  evidence. That is the family default returning a wrong answer here, which is what a dimension
  divergence means.

Not time-first, and this row makes no claim to the capture-media exception the schema row reserves:
*"For document and record domains, project, function, or subject usually comes before time because
putting year first scatters related work across calendar folders."*

### Leg 3 — privacy rules. **PARTIALLY DIFFERS. Recorded, and deliberately not leaned on.**

The catalogue value is `potentially_sensitive`, the same as the schema's, and the dispatch is right to
be suspicious of a leg that reduces to "this row is also sensitive." Two things are genuinely
additional, and both are stated as *reasons*, not as a different value:

- **Aggregation is the point, not a side effect.** An evidence pack exists *because* someone gathered
  access lists, key-management evidence, employee training records and system configuration into one
  place for an outsider to read. 00 requires several of those to be protected on sight: *"A scanned
  passport, tax statement, medical document, authentication key, or account record should enter a
  protected state immediately."* An evidence pack is a machine for manufacturing that condition.
- **The party harmed is often not the user.** An open finding is a description of a live weakness in
  an entity, and disclosure harms that entity. 00's protection model is built around the user's own
  policy — *"Protected material … should not be moved automatically without a user policy that
  explicitly permits it"* — and a user policy is exactly the wrong instrument for consenting on a
  third party's behalf. Marked **inference**; this is the row's contribution to NJ-J-IND-4 and it is
  P7's to resolve, not this row's.

**Verdict: the row stands, on Leg 1 outright, with Leg 2 supporting and Leg 3 recorded but not load-
bearing.** The gist verdict is preserved; the row's *scope* is narrowed as described above.

---

## Files considered and rejected

Beyond the ten in `file_examples`, and beyond the five the gist draft recorded:

- **`ISO 27001-2022 standard.pdf`** — kept, as fixture 1. The published standard is not conformity to
  it. Routes to `Reading Inbox`.
- **`ISO 27001 Gap Analysis - what we can do for you.pdf`** — **added this pass**, as fixture 2 and
  the harder one: a consultancy's sales PDF carries *every* term in `proposed_context_terms` and not
  one structure. It is the cleanest possible demonstration that this row is not a vocabulary row.
- **`Internal Audit Manager - job description.docx`** — rejected as an example because it collapses
  into fixture 2's argument (vocabulary, no structure) and `career` owns it; naming both would be
  padding.
- **A GDPR record of processing** — real and in scope, rejected again. It is a register, and it would
  restate the `risk-register` seam a third time without adding a discriminator.
- **A DPIA (data protection impact assessment)** — genuinely tempting, and rejected: its structure is
  a *risk* structure (likelihood, impact, mitigation), so `risk-register`'s discriminator already
  routes it and this row must not claim it merely because it is filed for a regulator.
- **A penetration-test report** — rejected as an example, but noted: it has the finding structure
  exactly and a distinct assessor, so it *is* this row's material, and it is also `code`'s. Covered by
  the existing `code.software-project` collision rather than by a tenth near-duplicate example.
- **A bank's SOC 2 report received as a customer** — rejected because
  `Supplier security questionnaire - Acme - completed.docx` already carries the which-side-is-the-
  holder argument, and carrying it twice adds nothing.
- **`Board minutes approving the audit plan.docx`** — `meeting-record`'s. Rejected without an edge:
  the minute is the meeting's structure, not the assessment's, and the schema row's default already
  separates them.

---

## Collision fixtures, both directions

**Would wrongly fire this row (and must not):**

1. `ISO 27001-2022 standard.pdf` — the published standard. Discriminator: no entity under assessment,
   no finding reference, no request number. → `Reading Inbox`.
2. `ISO 27001 Gap Analysis - what we can do for you.pdf` — full vocabulary, zero structure. →
   `Reading Inbox`.
3. `Food hygiene inspection report.pdf` — has the finding shape exactly. Discriminator: a statutory
   inspection power and a premises rating scheme belong to `retail_hospitality.food-safety`.

**Must not be lost TO this row — the same bytes, named on both sides:**

4. **`Information Security Policy v3.2 - approved.pdf`** — *added this pass.* `policy-handbook` names
   these bytes; its anchor is the document-control block. This row would steal it because a copy sits
   in the audit-evidence folder, and folder context never fires alone. Both rows now name the same
   file and agree on the discriminator, in the same words.
5. **`Statutory accounts FY26 - signed audit opinion.pdf`** — *added this pass.* Carries the word
   *audit* and an assessor's opinion, and is still not this row's: the assessed object is a set of
   accounts. `finance.small-business-bookkeeping` lists *balance sheet* and *profit and loss
   statement* among its own `work_types`, and finance is a **safety schema** kept local-only before
   any model path — so it wins on privacy as well as on topic.
6. `Risk register 2026.xlsx` — `risk-register`'s, on the discriminator its own row wrote and this one
   honours verbatim.

---

## Reciprocal boundaries, both directions

Eight collisions were on the row; **one was added** (`finance.small-business-bookkeeping`) and **one
was rewritten to be reciprocal** (`finance.tax-filings`).

- **`business_operations.risk-register`** — *this row takes* a finding raised by an identified
  assessment with a corrective action; *that row takes* a management-owned standing register with an
  inherent/residual pair and an appetite statement. Their wording, unchanged, quoted above. Findings
  become risks, and the two rows meet on the tracker; no edit made to that file.
- **`business_operations.policy-handbook`** — *this row takes* the audit reference, the control
  mapping and the attestation roster; *that row takes* the governing document with its control block.
  Their wording, unchanged. This row explicitly does **not** claim a policy PDF for sitting in an
  evidence folder.
- **`finance.tax-filings`** — reciprocal both ways now: it already lists *"audit or query
  correspondence"* among its own `work_types`, so an authority's enquiry into a return is **its**
  material and this row does not claim it; conversely a certification or control audit is not a tax
  record and finance should not claim it on the strength of the word *audit*.
- **`finance.small-business-bookkeeping`** — **new.** Where the object under assessment is a set of
  accounts or a ledger, finance takes it, on privacy as well as topic; where the object is a control,
  a management system or a process, this row takes it, and an accountancy firm's letterhead decides
  nothing. This is the seam the dispatch asked to be stated in both directions.
- **`construction_property.compliance-certificate`** — the edge is retained but its meaning has
  **inverted**. It is no longer "we both hold certificates and here is the discriminator"; it is now
  "that row was refused, this row seconds the refusal, and the standalone certificate goes to
  Independent Records on **both** sides." **Recommendation to R1c, not an edit:** that row's file
  needs no change, but R1c should record that its refusal is upheld by its nearest cross-family
  neighbour rather than routed around.
- **`business_operations.corporate-regulatory-filings`**, **`hr.workplace-health-safety`**,
  **`retail_hospitality.food-safety`**, **`code.software-project`** — unchanged from the gist draft;
  each was checked against its own file where landed and none is contradicted.

---

## `proposed_fields` — two, **both seconded, neither minted**

Per the dispatch: second the family's existing proposals rather than mint variants.

- **`fiscal_period`** — seconded from the schema row, which names this row as one of *four* siblings
  that want it. The argument added here is a **weakening**, offered because R1c will otherwise
  overcount: this row's dominant cycle is *not* the fiscal calendar. A certification runs across
  periods under one certificate number, and a finding opens in one year and closes in another. R1c
  should weight this row's vote **below** `budget-forecast`'s.
- **`organization`** — seconded from the schema row and from `construction_property`, which asks it be
  adjudicated once for both; `policy-handbook` seconds it too. This row adds both the sharpest reason
  to want it (holder's own record / supplier's evidence / customer's questionnaire are structurally
  identical and separable only by custody) and the sharpest reason one key is **not enough**: this
  row's documents carry two organisation roles at once. The seeded-ineligible caveat is seconded with
  the key.

**Two holes named and deliberately not minted**, following the schema row's own discipline with the
supplier and customer roles:

- **The assessor role.** 00 is explicit that co-occurring roles of the same entity type are distinct
  facets — *"The agent should model these as distinct facets, such as authored_by and target_school,
  or our_firm and client."* An audit report's letterhead is the **assessor's**, not the assessed's,
  so a single `organization` key reads the wrong party off the strongest slot in the document.
- **The standard-or-obligation referent**, which is this row's real top dimension. Minting a key for
  it on a field-less schema, at the exact point of maximum temptation, would be the 574's mistake
  performed knowingly. Both are in `open_question` for R1c.

`proposed_context_terms` carries 34 practice terms. They are **proposals**, not 00's floor — 00's
named context-term floor is the academic one (*"syllabus," "lecture," "credits," "instructor," or
"semester"*) and this row does not pretend otherwise.

---

## Neighbours considered that did **not** get an edge

- **`government.professional-regulator`**, **`government.environmental-regulation`** — an authority's
  inspection record. Unedged: the which-side-is-the-holder discriminator is already carried by
  `corporate-regulatory-filings` and by the schema row's `government` collision. Tripling it adds
  nothing.
- **`manufacturing`** quality-system rows — same shape, same reason.
- **`nonprofit.standards-body`** — a standards body's *own* material, not conformity to it.
- **`business_operations.meeting-record`** — the minute approving an audit plan. The minute's
  structure is the meeting's; the schema row's default already separates them.
- **`career`** — an internal-audit job description, a professional certification a *person* holds.
  `career` is a person's own record by the schema row's anchor triple; no contest.
- **`hr.training-records`** (where it lands) — training completion records are on this row's
  `work_types` **as evidence** and are `hr`'s **as personal records**. Not edged separately because
  `hr.workplace-health-safety` already carries the identifying-material discriminator in the exact
  terms that would be repeated here. **Recommendation to R1c**, not an edit: if a distinct
  `hr.training-records` row lands, the reciprocal edge should be added there and here.

---

## NEEDS-JOSEPH

- **NJ-BO-6 · This row's licence depends on NJ-3 (`purpose` scope).** *Alternatives and costs:*
  (a) purpose stays broad → row stands as written; (b) purpose narrows → fold into `risk-register`
  plus `policy-handbook`, at the cost of losing the request list and the closure chain, which neither
  neighbour claims and which would then land in `Review Later`.
- **NJ-BO-7 · Confirm the `soft.tech-compliance-evidence` fold.** Defensible, and it leaves a real
  seam with `code.software-project`: one configuration file is repository content and audit evidence
  at once. *Alternatives:* confirm the fold and rely on the existing collision, or split technical
  control evidence back out — the latter re-creates a row whose only signal is a file's location,
  which is the failure this pass exists to prevent.
- **NJ-BO-8 · The assessor role has no field key** (new this pass). *Alternatives:* mint an
  assessor/assessed pair on the family; reuse `organization` and accept that the strongest labelled
  slot names the wrong party; or leave both unfilled and let the row recognise without extracting,
  which is what a `placeholder` row does today and is the honest status quo.
- **NJ-BO-9 · The standard-or-obligation referent has no key** (new this pass), and it is this row's
  recommended top dimension. *Cost of doing nothing:* the dimension recommendation stays prose
  permanently, and `fiscal_period` gets adopted as the family's second axis on a vote this row has
  just asked to be discounted.
- Carries **NJ-J-IND-4** by inheritance, sharpened in Leg 3: an open finding describes a live
  weakness in an entity that is often **not the user**, and no safety flag reaches it. A user policy
  is the wrong instrument for consenting on a third party's behalf.

---

## What changed in this pass

**Preserved** (correct in the gist draft, not rewritten for its own sake): the verdict that the row
stands; the purpose-row framing and its honest weakness; all nine deterministic signals bar one; the
`work_types[]` list; the six `falls_through_to` routes; six of the eight collisions; the sensitivity
argument; the ten-item `file_examples` core; NJ-BO-6 and NJ-BO-7.

**Narrowed** — the substantive change: the **standalone certificate is given up** to
`construction_property.compliance-certificate`'s refusal and to `Independent Records`. The
certification detection signal is rewritten as the weakest in the list and never sufficient alone,
requiring a visible assessment cycle; the `Certificate of Registration` example now leads with
`must_not_conclude: activation of this row from the certificate ALONE`; and `one_line` states the
concession and re-anchors the row on the assessment occurrence and its cross-reference chain rather
than on certificates or on the word *audit*.

**Added:** the never-alone principle applied signal by signal, as a table, against the family rule;
the three-way charge (document type / work type / finance) answered in full, including the
neighbour-quotation evidence that this row's coverage is *not* already carried; the node test argued
leg by leg with Leg 3 explicitly demoted to non-load-bearing; `template.why` rewritten to argue two
divergences and concede one non-divergence against the schema row's default paragraph; three
`file_examples` (a gap-analysis sales PDF, a policy inside an evidence pack, a signed statutory audit
opinion), two of which are the *must-not-be-lost-to-me* direction the gist draft lacked entirely; a
new `never_alone` closing the one-high-frequency-bridge hole; a new reciprocal collision with
`finance.small-business-bookkeeping` and a rewritten reciprocal one with `finance.tax-filings`; two
seconded `proposed_fields` where the gist draft had none; two new NEEDS-JOSEPH items; and the
files-considered-and-rejected list extended from five to eight with the reason for each rejection.

**Reversed:** nothing. The gist verdict was right and is upheld. What was too broad was the row's
*scope*, and that is now narrowed rather than reversed.

**Not done, deliberately:** no neighbour file was edited. Two recommendations for R1c are recorded
above (the `compliance-certificate` upheld-refusal note, and the `hr.training-records` reciprocal
edge) instead of being written into other rows.

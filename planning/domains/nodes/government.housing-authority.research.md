# Research memo — `government.housing-authority`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.housing-authority.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch

## Result

**Accept.** The node survives the charge, but only on one argument, and it is worth stating before
anything else: this row is not "the government schema, applied to housing." It is the one world
inside `government` whose durable anchor is a **dwelling** rather than a **proceeding**, and whose
evidence is **account-shaped and stock-shaped** rather than identifier-chain-shaped. That difference
changes activation, changes the recommended dimension order, and adds a privacy rule the schema
default does not carry. Those are exactly the three legs CONNECTION §2 asks for.

It carries one unresolved structural problem which I have not smoothed: a large share of social
housing is held by charitable registered providers who are **not public bodies**, and the `government`
schema's activation precondition is an evidenced authority-side role. That is NJ-HA-1 below and it is
the honest reason this row's `provenance` is `inference`, not `design`.

---

## The charge, argued first

The brief asks for the strongest case that this row should not exist. There are five, and four of
them are strong.

**1. "Housing is a topic, and topics are not nodes."** The `government` anchor already names
"programme administrator" and "citizen-casework office" among its roles, and lists "constituent,
ombudsman, complaint, benefit, or service casework held by the public office" as a work type. Housing
casework is plainly a value of that. If that is all this row is, it is a `work_type` value wearing a
node's clothes, and the 574's original mistake repeated.

*Defeated, on evidence structure.* Read the anchor's `deterministic` list and every entry has the
same shape: **an identifier repeated across the stages of a bounded proceeding** — a bill identifier
across text/amendment/vote, a rulemaking identifier across notice/analysis/comments/final instrument,
a case reference across application/consultation/reasons/decision, a procurement reference across
notice/bids/evaluation/award. That is a proceeding fingerprint, and it works because a proceeding
*ends*.

Nothing in this row's core evidence has that shape. A rent account is a **ledger**: opening balance,
periodic charge debits, benefit credits, running balance carried forward, forever, with no terminal
state. A repairs order is a **work instruction with a target-response class**. A stock condition
survey and a compliance register are **per-dwelling row sets across a whole estate**. A choice-based
lettings bid list is **one property against many applicants** — a shape that only ever exists in the
allocator's hands, because an applicant sees one row of it. None of those five structures appears
anywhere in the schema anchor's deterministic list, and none of them would be recognised by it. That
is leg one of the node test: **detection signals differ.**

**2. "It is a duplicate of `construction_property.tenancy-management` with a public owner — i.e. an
organisation type, which is never-alone evidence."** This is the strongest form of the charge, and I
took it seriously, because "who owns the landlord" is precisely the kind of never-alone attribute the
brief warns about.

*Defeated, on documents that do not exist on the other side.* A private landlord's file, however
large, never contains: a housing-register application with a banding award and reasons; a bid list; a
statutory homelessness duty decision with eligibility, priority need, intentionality and local
connection sections and a review-right paragraph; a right-to-buy discount computation; a succession
or mutual-exchange decision; a void-and-re-let schedule across a stock; a stock-wide compliance
due-date register. Conversely, this row's tenancy pack never contains the private row's fingerprint —
a deposit-protection certificate with prescribed information, a market rent, letting particulars. The
boundary is carried by **document types that are absent from the other world**, not by the owner's
name. If the discriminator were only "council versus private", I would have refused.

**3. "It is defined by the absence of something — no deposit, no market rent, no agent."** Half true,
and I want it on the record that I noticed. The *sign-up pack* fixture really is discriminated partly
by absences. But the row is not defined by them: the register, the bid list, the duty decision and
the stock register are all positive, present, structurally distinctive evidence. A row defined only
by absence would have none of those.

**4. "It duplicates `government.municipal-administration`."** The schema anchor's own file example is
`Council Housing Committee - Agenda Pack - 18 August 2026.pdf` — a housing-titled authority document
already claimed by the default. *Defeated, and turned into this row's second collision fixture.* An
agenda pack is a governance cycle whose subject happens to be housing; this row is the operation
itself. A committee paper reporting arrears performance stays with the governance cycle. See below.

**5. "It is a lifecycle stage, or a medium, or a length."** No. It spans applications, tenancies,
money, works, cases and duties, in every source type from spreadsheet to calendar to archive. This
form of the charge does not land.

**Verdict: accept.** But note what the charge cost the row: it is narrower than its `one_line_hint`
implies. "Estate management" as a phrase would have swallowed communal block services, and I have
edged those out to `construction_property.block-management` rather than absorb them.

---

## The node test, all three legs

The `government` schema's **default template** is, verbatim from `government.json`:
`dimension_order: []`, `time_first: false`, and a prose recommendation of "authority-side function or
bounded proceeding/case/programme first, then an exact reference or cycle, then work type; named
people must not become the organizing dimension." Its default privacy posture is
`potentially_sensitive` with the rule that privacy is enforced before content reaches any model. Its
default activation requires an evidenced public body in an authority-side role.

**Leg 1 — detection signals differ.** Argued above. Five structural fingerprints (running-balance
ledger keyed to a tenancy; banding award with reasons and effective date; one-property-many-applicants
bid list; priority-classed repair order with target response; per-dwelling row set across a stock)
are absent from the schema's deterministic list and would not fire it. Conversely this row must
*decline* several signals the default accepts — a procurement notice, a rulemaking chain, an FOI
schedule — even when they concern housing.

**Leg 2 — recommended dimensions differ.** The default recommends a bounded proceeding first. That is
wrong here and would actively damage the corpus. A dwelling persists across successive tenancies; a
tenancy persists across dozens of repairs, arrears episodes and inspections. Proceeding-first would
scatter one flat's forty-year repair history across forty case folders. The honest order is
**dwelling anchor → tenancy or duty-case anchor → function**, with the duty case (homelessness, right
to buy) deliberately hung off the *household* rather than the dwelling, because a homelessness
applicant has no dwelling yet. Both orders are recorded as prose, not serialized, because PR-6 leaves
the schema fieldless and a template cannot branch on undeclared fields.

`time_first: false` matches the default, and for the same design reason — "For document and record
domains, project, function, or subject usually comes before time because putting year first scatters
related work across calendar folders." A rent account and a repairs history are the exact material a
year-first tree would shred. Matching the default on one sub-property is not a failure of the node
test; the test is disjunctive.

**Leg 3 — privacy rules differ.** Both are `potentially_sensitive`, so posture alone does not
distinguish. The *rule* does. The default says named people must not become the organizing dimension.
This row's natural organizing dimension is an **address**, and in a managed stock an address
identifies a household as precisely as a name does — "Flat 4, 12 Elm Court" and "the Reyes household"
are the same string in different clothes. The default has no rule for an anchor that is
simultaneously the correct grouping key and an identifier, so this row adds one: the dwelling
reference may be used internally as a grouping key and must not be surfaced as a display label.
Second added rule: cross-household semantic joining is suppressed outright, because addresses,
blocks, estates, contractors, officers and complaint subjects recur across unrelated households, and
a similarity join would disclose one tenant's affairs inside another's group. Neither rule is
derivable from the default.

All three legs pass independently.

---

## Evidence base, and what kind of evidence it is

Every claim in the node traces to one of three things, and I have marked which:

- **Design quotation.** Nine spans are quoted from `00`. Every one was grep-verified verbatim against
  `planning/00-database-agent-product-design.md` before use — the extension-as-routing-signal line,
  the session-is-not-topic line, the absence-of-EXIF line, the unknown-return line, the
  function-before-time line, the user-may-flatten line, the privacy-enforcement line, the protected-
  material line, and the nine residual definitions on line 120. One quote failed verification on the
  first pass (a paraphrase of the Temporary Screenshots definition) and was replaced with the
  verbatim text from line 120 rather than kept.
- **Named real document types.** The register application, banding decision, bid list, void schedule,
  rent account, notice seeking possession, homelessness duty decision, right-to-buy application and
  discount computation, stock condition survey, compliance register, ASB case log, sign-up pack,
  decant note, estate walkabout, and housing-system export are all real, named, structurally specific
  artifact types. They are named at the level of *what is inside them* — which slots, which columns,
  which blocks — because the filename alone is never the evidence.
- **Marked inference.** The node's `provenance` is `inference` and every `collides_with` entry ends
  with "Provenance: inference." No design document names a housing-authority world; the row extends
  the `government` schema's named authority-side role concept into a landlord function. That
  extension is exactly what NJ-HA-1 questions.

No thresholds, no counts, no statistics, no handling classes appear anywhere in the node.

---

## Files considered and rejected

A row that only lists what it holds has not been researched. These are the tempting false positives,
and why each is not this row's evidence.

| File | Where it actually goes, and why |
|---|---|
| `Housing Committee - Agenda Pack - 18 August 2026.pdf` | `government.municipal-administration`. **The primary collision fixture** — it is a file example on this row's own schema anchor. An agenda, numbered papers, attendance and apologies is a governance cycle. The resident appendix is what makes it tempting and it changes nothing. |
| `My council tenancy agreement and rent statement.pdf` | **Protected Records**, with `identity` as an independent schema. **The second collision fixture.** Byte-identical furniture to the landlord-side pack, opposite custody. The holder is the tenant. An authority-issued document held by its subject never activates this schema — the anchor's `never_alone` says so and this row repeats it. |
| `Housing Benefit award notice - Ms A Reyes.pdf` | Held by the claimant: Protected Records. Held by the benefits service: `government.social-services-casework`. Held by the landlord as a payment schedule: a *credit row* inside a rent account, which is this row — but the award notice itself is not. |
| `Planning permission for 40 new homes - PL-2026-184.docx` | `government.planning-application`. A development consent for housing is a planning case. The word housing is doing all the work and it is never-alone. |
| `Affordable Housing Development Appraisal.xlsx` | `construction_property.development-appraisal`. Land value, build cost, grant assumption, residual value. This row starts when there are tenants, not when there is a site. |
| `Gas Safety Record CP12 - 22 Beech Walk.pdf` | **Independent Records.** A single certificate for one address. `construction_property.compliance-certificate` refused for precisely this reason — a document-type word plus an address, both never-alone. A stock-wide due-date *register* is this row; one certificate is not. That distinction is authored as a `never_alone` and again in the `collides_with` entry. |
| `Section 20 major works consultation - Block C.pdf` | `construction_property.block-management` / `construction_property.service-charge`. Leaseholders, apportionment, communal budget. Genuinely arrives in a council housing office's post for a mixed-tenure block, which is why it is edged rather than silently rejected. |
| `Repairs contractor invoice - Job 118322.pdf` | `construction_property.trade-job`. The contractor's own job file. The repair *order* is this row; the invoice raised against it is the trade's, and both name the same dwelling and the same defect. |
| Blank tenancy template, published allocations policy, tenant handbook, regulator's consumer standard | **Reading Inbox** / Reference Clips. Nothing is filled in, so no relationship is evidenced. `construction_property.tenancy-management` and `block-management` both made the identical call and I am matching it deliberately. |
| `Homes and Communities statistics release 2026.pdf` | **Reading Inbox.** Publication by an authority is not authority-side custody — the schema anchor's `never_alone` says exactly that. |
| A `.vcf` for a tenant, a caretaker, or an out-of-hours contractor | A file-kind signal at most. `00` requires contact data be privacy-protected rather than used to create folder proposals. |
| A recurring weekly credit in a bank statement, the right size for social rent | Nothing. Also a salary, a standing order, a subscription, a loan repayment. In `never_alone` verbatim. |
| A grant agreement funding new social homes | `government.grant-programme-administration` on the funder side, `nonprofit.grant-reporting` on the provider side. Building homes is not housing *management*. |
| A housing officer's payslip, contract, or DBS check | `career.employment-records` / `hr.payroll-benefits-administration`. Government as employer is not this schema, and the anchor's `never_alone` already says so. |

---

## Reciprocal boundaries, named on the same fixture from both sides

Five collisions are authored. Each names the competing bytes, and states the discriminator in both
directions.

| Neighbour | Competing fixture | Theirs when | Mine when |
|---|---|---|---|
| `construction_property.tenancy-management` | `Tenancy sign-up pack - 22 Beech Walk - signed.pdf`; and a compliance certificate | an AST, a deposit-protection certificate with prescribed information, a market rent, letting particulars | a social tenancy type under a named lettings scheme, a rent set by standard or formula, an offer produced by a register or bid process, a stock around it |
| `government.municipal-administration` | `Housing Committee - Agenda Pack - 18 August 2026.pdf` | agenda, numbered papers, attendance, minute, resolution — a governance cycle whose subject is housing | rent accounts, banding awards, repair orders, void schedules — housing as the work, not the agenda item |
| `government.social-services-casework` | `Homelessness HL-2026-0912 - duty decision letter.pdf` and its annexes | care, protection or support duties owed to a person, with assessment and plan structures that survive wherever the person lives | the duty, decision and remedy are accommodation, eligibility, priority need, allocation, tenancy |
| `construction_property.block-management` | a communal-works consultation for a mixed-tenure block | leaseholders, an apportionment schedule, a communal budget, a building's own service-charge cycle | tenants, rent accounts, the landlord's own stock obligations |
| `nonprofit.governance` | a board pack containing a housing-performance report | the association running *itself* — trustees, members, constitution, charitable objects, board cycle | allocations, tenancies, rent, repairs, regardless of the provider's legal form |

**The reciprocity that already exists.** `construction_property.tenancy-management` landed first and
already edges here, phrasing the boundary as "a contracting or regulating authority, a statutory
scheme and an enforcement framing supports the government row; a landlord's or agent's own tenancy
file supports this row." I am accepting that edge and returning it, but I am **sharpening it in a way
R1c should notice**: their phrasing makes the boundary *enforcement framing*, which would give them
every social tenancy that is not an enforcement action. The evidence does not support that. A council
letting a flat to a tenant is not enforcing anything, and the discriminator that actually works is
the social-tenancy-plus-allocations-scheme fingerprint, not enforcement. This is recorded as a
recommendation, not an edit — I have not touched their file.

**`construction_property.survey-valuation`** considered this row for statutory disrepair inspections
and rejected the edge, on the ground that only topical adjacency was shared. **I agree and am not
edging back.** Their fixture set is valuation and condition opinions for a client; my stock condition
survey is a per-dwelling row set commissioned by the landlord for investment planning. Different
structure, not merely different framing. The non-edge is deliberate and symmetric.

**Neighbours considered that got no edge:**

- `government.public-authority-record` and `government.constituent-casework` — a councillor's housing
  enquiry on behalf of a resident is constituent casework until it enters the housing case system.
  Real, but the discriminating evidence is the *system of record*, which is a custody question already
  covered by this row's holder-role precondition. Adding the edge would author a collision on a topic.
- `government.permit-licensing` — HMO and selective licensing genuinely sits in housing departments.
  Rejected as a *this-row* edge because the licensing case fingerprint (application, conditions,
  decision, register entry) is the schema default's proceeding shape, held by the regulating side,
  against private landlords. It is `permit-licensing`'s, cleanly.
- `finance.hoa-residents-association` — a tenants' and residents' association. Rejected: the
  association running itself is not the landlord's file, and `block-management` already carries the
  mixed-tenure money boundary that actually collides.
- `legal.personal-legal-matters` and `legal.practice-matter-file` — possession proceedings and duty
  decision reviews. Expressed as `also_schema: "legal"` on the notice and duty-decision fixtures,
  which is the correct instrument for a template row: `also_holds_with` joins *schemas* and this row
  cannot author schema-level coactivation. `also_holds_with` is deliberately empty and this is why.
  Same call `construction_property.survey-valuation` made, for the same reason.
- `identity.core-documents` — identity copies inside a sign-up pack are members that keep their own
  evidence, not a conversion. Coactivation, not mutex.

`role_split` is empty. It requires pointing at a neighbour that holds the other role *with different
field keys*, and this row has no fields to split. Same fieldless reason `legal.practice-matter-file`
gave.

---

## The collision fixtures, in full

The brief asks for at least one. There are two, and the second is the more instructive.

**`Housing Committee - Agenda Pack - 18 August 2026.pdf`.** This is not a hypothetical: it is
fixture #2 on `government.json`, this row's own schema anchor. It carries an authority name, a
housing subject, a meeting date, and — the part that makes it genuinely dangerous — an appendix of
named residents and addresses, which is superficially indistinguishable from this row's core
evidence. **What discriminates it:** the document's *spine* is a governance cycle (numbered agenda,
indexed reports, attendance and apologies, a minute), and the residents appear as the subject of a
report rather than as parties to a tenancy. There is no tenancy reference, no rent account, no
allocation, no repair order. A committee paper that reports arrears performance across a stock stays
with the governance cycle even though every word in it is about rent.

**`My council tenancy agreement and rent statement.pdf`.** The tenant's own copy. Byte-for-byte the
same clause furniture and the same statement layout as the landlord's pack. **What discriminates it
is not in the file at all** — it is the corpus around it: no second tenancy, no stock, no allocations
scheme in operation, no officer-side workflow, and the holder is the addressee. This fixture is why
the row's precondition is a *role*, and why `facts_legal` on it is empty rather than merely
restricted.

---

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`. All intentional.

PR-6 leaves `government` fieldless and D1's deferral stands; a template may reuse only fields its
schema declares, and `government` declares none. Candidates were considered and **not** minted, in
line with the brief's instruction that a new key needs a reason no existing key works:

- `property_ref`, `tenancy_ref`, `case_ref` — the three keys this world actually wants. All would be
  new. Minting them here, in a child, is exactly the failure `legal.practice-matter-file` avoided.
  They belong to a central adjudication, and NJ-HA-2 asks for it.
- `institution` and `record_type` are scoped to Finance; `purpose` is scoped to College Applications;
  `work_type` is Academic's. Reusing any of them here would be a synonym-mint in disguise.
- `address` — deliberately *not* proposed even as a candidate, because of the privacy finding above:
  in a managed stock the address is a household identifier, and proposing it as a field invites
  proposing it as a destination.

`proposed_context_terms` is empty. The design floor for context terms is academic and I am not
extending it by assertion.

---

## Open questions

**NEEDS-JOSEPH NJ-HA-1 — the provider-status problem.** This is the real one, and it is not
smoothable. A large share of social housing is held by charitable registered providers and housing
associations. They are not public bodies. The `government` schema's activation precondition is an
evidenced authority-side role, and its `never_alone` explicitly excludes "a charity, campaign, union,
faith body, standards body, accreditor, or membership association" unless public-body status is
independently evidenced. Yet a housing association's allocations register, rent accounts, repair
orders and stock registers are structurally identical to a council's. Three alternatives:

- **(a)** Restrict this row to local-authority housing services, and route registered-provider
  material to `nonprofit.governance` plus `construction_property.tenancy-management`. Cost: splits one
  identical filing world across three rows, and puts a homelessness duty decision in a row that has
  no concept of one.
- **(b)** Treat the **social landlord function** — an allocations scheme, a rent standard, a statutory
  duty — as itself satisfying the government precondition regardless of legal form. This is the row's
  working assumption, and it stretches the schema's own stated precondition. It is why the row's
  provenance is `inference`.
- **(c)** Accept user confirmation of provider status for hybrid and quasi-public bodies. The schema
  anchor's own open question already floats this for the general case; housing is the sharpest
  instance of it.

I have not chosen. The node ships on (b) with the tension recorded in `open_question`.

**NEEDS-JOSEPH NJ-HA-2 — the identifying anchor.** If PR-6 is lifted, decide centrally whether a
dwelling anchor may be destination-eligible *at all*, given that it identifies a household, or
whether all housing grouping must use a local-only alias with a redacted display label. This is a
general problem — the same question arises for any row whose correct grouping key is a place where
one family lives — and it should not be decided inside a child row.

**Recommendation to R1c (not an edit):** `construction_property.tenancy-management`'s outbound edge
here should be re-worded from "enforcement framing" to the social-tenancy-plus-allocations-scheme
discriminator, for the reason given above. I have not touched their file.

---

## Self-verification

- `python3 -m json.tool` parses the node. Key set matches `government.json` and the landed
  `construction_property.tenancy-management`.
- All ten `00` quotations grep back verbatim with `grep -c -F`. One failed on the first pass and was
  corrected against line 120 rather than retained.
- Every edge id checked against `planning/domains/roster.json`: `construction_property.tenancy-management`,
  `government.municipal-administration`, `government.social-services-casework`,
  `construction_property.block-management`, `nonprofit.governance` all present.
- Every `falls_through_to` name is one of `00`'s nine residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. `code_structured` was dropped from
  `file_kinds` — a housing office does not hold source structure.
- No file example writes a folder path as a fact. No thresholds, counts, or handling classes appear.
- Sparse members (`Void and Re-let Schedule`, `Estate inspection .ics`, the compliance register, the
  screenshot) carry `group_without_copying_facts: true` rather than inventing a tenancy fact.
- Files written: exactly the two assigned. No neighbour, roster, canonical-fields, `check.py`, `src/`
  or SPEC file was opened for writing.

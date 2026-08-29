# business_operations.customer-account-management — lab notes (template row)

**Depth: J-DEPTH.** Deepened from the retired gist draft. The gist draft's facts and arguments were
checked and are preserved; what follows adds the node test argued leg by leg against the family's
now-stated default template, the files considered and rejected, collision fixtures in **both**
directions, reciprocal boundaries with every neighbour that could steal from this row or be stolen
from, and the open questions the gist smoothed. Not padded: where this row has less to say than a
launch row, it says less.

## Sources

Authority stack as in `RESEARCH-BRIEF.md`. All quotations machine-verified verbatim against
`planning/00-database-agent-product-design.md` (the check script is re-run at the end of this pass;
result in *Self-verification*). Read for this deepening, in this order:

- `business_operations.research.md` — the deepened schema anchor. It now states the family's
  **default template** and generalises the **never-alone principle for all 24 siblings**. This row's
  node test is measured against that paragraph and nothing else.
- `business_operations.organisational-records.json` — the family's one refusal, read **first and on
  the working assumption that this row was heading the same way**. It is the exemplar the dispatch
  named, and the reason the first section below is a charge sheet rather than a description.
- `business_operations.partnerships-bd.research.md` — deepened, and it **settled** the three-row
  counterparty question naming this row. Accepted, reciprocated, not reopened.
- `business_operations.vendor-management.research.md` — the mirror row.
- `business_operations.support-operations.research.md` and
  `business_operations.contract-administration.research.md` — deepened siblings whose files sit
  *inside* a customer relationship.
- Landed siblings for key set and idiom: `business_operations.json`,
  `career.consulting-client-engagement.json` (where `00`'s `our_firm` / `client` role split lives),
  `creative.client-engagement.json`.

Legacy row absorbed per `ROSTER.md` Appendix A line 825: `ops.customer-success` (ROW). That is the
whole of this row's inheritance, and — per the family rule — it is **not** a reason to keep the row.

---

## The charge against this row, taken seriously first

Two charges arrived with the assignment, and both are strong enough that this memo is organised
around answering them rather than around describing the world.

**Charge (a): the defining signal is a customer's organisation name, which is never-alone evidence
and can never activate a row.** This is the exact anchor `business_operations.organisational-records`
was refused for. The family rule, from the deepened schema row:

> **No sibling may rest its activation on an entity name, a business vocabulary word, or a document
> shape alone.** Each of the three is never-alone here. Every detection signal a sibling writes must
> pair a **structure** with a **labelled slot**.

The charge is well aimed, because this row is more exposed to it than any sibling: a customer account
is *organised around another organisation's name* in ordinary practice, and the folder a real user
keeps is literally called `Acme/`. If the row's activation reduced to *the token Acme appears*, it
would never fire and it should be refused.

**Charge (b): this may be the same world as `vendor-management`, with only the direction of the
relationship differing — and direction is plausibly a field value.** Also well aimed, and reinforced
by `00` itself, which answers role differences with fields:

> "The system must separate roles that happen to contain the same entity type."

**And the discriminator that saved `partnerships-bd` is unavailable here.** That row earned its node
on **relationship state** — not-yet-existing versus already-existing. This row is on the
already-exists side *with* `vendor-management`. Reusing that argument would be theft, and it is not
used below.

The answer to both charges is the same and it is the whole substance of this row: the row does not
rest on the name, and it does not rest on the direction of the money. It rests on the **direction of
assurance** — who, in the structure of the document, is being judged — and on a **privacy posture**
no sibling shares. Both are argued in full below, and both are now written into the JSON.

---

## What it is for, and what it holds

*(Preserved from the gist draft; still correct.)* Managing an **existing named customer relationship
after the sale**. Account plans and stakeholder maps, onboarding and success plans, periodic business
reviews, usage and adoption records, health and churn assessments, escalation summaries, renewal
preparation and expansion proposals, customer meeting notes, feedback exports, reference and
case-study material — and the customer's own material held inside the relationship.

One addition this pass makes explicit: **the customer's own material is not a marginal member of this
row, it is a constitutive one.** A relationship that has run for two years deposits the counterparty's
strategy packs, org charts, internal policies and security questionnaire responses on the holder's
machine. No other row in the family routinely accumulates a *third party's own confidential
documents* as a by-product of doing its job. That fact drives the privacy leg of the node test and
the choice of `Protected Records` as first fallthrough.

---

## The node test, argued leg by leg

CONNECTION.md §2: a template row exists only where its **detection signals**, **recommended
dimensions**, or **privacy rules** differ from its schema's default template.

### Leg 2 first, because it is unavailable and saying so is honest

`template.dimension_order` is `[]` by binding contract — a dimension may only branch on a field the
same entry's schema declares, and `business_operations` declares none (D1 as narrowed, `_CONTRACT`
rules 10 and 15, CONNECTION PR-6). **Leg 2 is therefore unavailable to all 24 siblings equally**, and
this row does not pretend to pass it. It is recorded here, and in `template.why`, as prose.

The family default, quoted from the deepened schema row, is the paragraph this row must differ from:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

This row's prose recommendation *does* differ from it, and the difference is worth recording even
though it cannot be scored:

- The default's first level is **conditional and seeded ineligible** — the holder's own employer,
  which is `00`'s collector failure: *"A folder should not become a collection point for everything
  produced by the same person or organization."* This row's first level is a **different**
  organisation, the counterparty. The collector prohibition is about the holder's own name and does
  not reach it — but a folder named for a customer **publishes the relationship in the filesystem
  namespace**, which is a distinct hazard the default paragraph does not contemplate. The posture
  taken: user-approved, never automatically proposed, and with no automatic depth beneath it.
- The default puts **`fiscal_period` before function**. This row would put the **engagement period or
  review cycle** there instead, which is the same slot filled by a relationship-shaped rather than a
  calendar-shaped value. Marked as **inference**, not as a licence: no such field exists.
- **Not time-first**, agreed and inherited without qualification. `00` grants the time-first
  exception to capture-based media only, and — as the schema row says — no sibling in this family may
  claim it. Renewal quarters and review cycles are content periods, not capture dates.

**Leg 2: unavailable. Not claimed.**

### Leg 1 — detection signals: passes, and this is where charge (a) dies

Eleven deterministic signals are written and **every one of them pairs a structure with a labelled
slot**, per the family rule. The four that carry the row:

1. **The account-plan structure.** One named counterparty, plus labelled slots for the relationship
   owner, current state, *named stakeholders with roles and sentiment markers*, objectives, risks, and
   an expansion outlook. The stakeholder-sentiment map is the single most characteristic element in
   the row and it appears nowhere else in the family — a board pack names people, an org chart names
   people, but only this artifact records the holder's **private judgements about named individuals at
   another organisation**.
2. **The business-review structure.** A periodic document *addressed to* the counterparty, carrying a
   period, usage or outcome figures, achievement against **previously agreed** objectives, and a
   forward plan with owners on both sides — produced **repeatedly for the same recipient**. The
   recurrence-for-one-recipient property is structural, not vocabulary.
3. **The adoption / health structure.** A per-counterparty record of usage, licence consumption,
   adoption milestones, or a health or risk score **with a trend**. *"Tables matter because resumes,
   forms, applications, invoices, and administrative documents often place their most useful
   information in cells rather than body paragraphs."*
4. **The renewal-preparation structure.** A per-counterparty row combining a contract end date, a
   current value, a proposed value, a risk marker **and an internal recommendation**. The internal
   recommendation is the discriminating slot; the contract end date alone is `contract-administration`'s.

Charge (a) is answered by construction: **none of the four is an organisation name**, and the
counterparty name is written into `never_alone` as *the sharpest instance of `00`'s own warning in
this family* — because in this row the same token appears on the holder's employer's letterhead, on
the counterparty's shared material, on a competitor mention and on a cited reference **inside one
folder**. Read across from `00`: *"A university name alone should not create a group because Columbia
can appear as an authoring school, course provider, target institution, employer, research venue, or
merely a cited organization."*

Two further never-alone entries were added this pass specifically to close charge (b) at the
detection layer: **a role word alone** (customer, client, account, supplier, partner, prospect) and
**the direction of an addressee alone**. A vendor scorecard, a customer review deck, a partner plan
and a regulator submission are all addressed outward, and three of them are other rows'.

**Leg 1: passes.**

### Leg 3 — privacy rules: passes, and this is the strongest leg

The family's posture is that the exposed party is usually not the user. This row is the **limiting
case** of that posture and it differs from the default in a way that changes handling, not merely
tone:

- Its characteristic artifacts hold **third parties' personal data** (a stakeholder map with sentiment
  markers, a contacts export, a usage export with a named-end-user column) and **third parties'
  commercial secrets** (the counterparty's own strategy document), and **none of those parties can
  consent** to what the product does with them. The user's consent is not the relevant consent, and
  no mechanism in the catalogue expresses that.
- `00` states the contacts rule outright, and it is quoted on the row rather than paraphrased: such
  data *"should normally be privacy-protected rather than used to create folder proposals"*. A
  contact list is not an account record and must not become a folder.
- The enforcement point is quoted as a precondition on the whole `recognition` block: *"Privacy
  policy must be enforced before content reaches any model or external connector."*
- Consequently **`Protected Records` is this row's first fallthrough, not its last** — the inversion
  of the family default, and the clearest single expression of leg 3.

**Leg 3: passes.**

**Overall: the row stands, on legs 1 and 3, with leg 2 unavailable to the whole family.** The gist
draft's verdict is **not reversed**; it is re-derived on a materially stronger footing. Where the
gist rested the row on *"one customer as an ongoing relationship"* — which contains a role word and
would not have survived the family rule unaided — this pass rests it on the four structures, on the
direction of assurance, and on the privacy posture. That is a change of argument, stated openly, not
a change of verdict.

---

## Charge (b), answered in full: this row and `vendor-management` are two worlds

`partnerships-bd` settled the three-row question and this row **accepts its settlement without
qualification**, including the premise that hurts:

> "I accept that premise. Role is a field value. No one of these three rows may rest on it, and this
> row does not"

Stated reciprocally from this side: **role is a field value; the direction of the money is a field
value; neither is this row's anchor.** And the state discriminator that saved `partnerships-bd` —
not-yet-existing versus already-existing — is **not available here and is not borrowed**: this row and
`vendor-management` are both on the already-exists side. What separates them is:

**1. The direction of assurance — who is being judged by the document's own structure.** This is the
discriminator, and it is checkable on real bytes:

| Artifact | Who is judged | Row |
|---|---|---|
| Onboarding form with a remittance block | the counterparty (are they real, payable, safe) | vendor-management |
| Diligence questionnaire, insurance certificate, security attestation | the counterparty (are they honest) | vendor-management |
| Supplier scorecard with SLA columns and a rating | the counterparty (did they perform) | vendor-management |
| Account plan with a stakeholder-sentiment map | **the holder's own position** in someone else's organisation | this row |
| Business review deck addressed to the counterparty | **the holder** (did we deliver value) | this row |
| Adoption record, renewal recommendation, expansion proposal | **the holder** (should they keep us) | this row |

The two worlds' inbound material differs in kind for the same reason. What arrives from a vendor is
**assurance the vendor is obliged to disclose** — certificates, attestations, codes of conduct. What
arrives from a customer is **material they chose to share inside a relationship** — their strategy,
their org chart, their internal policy. The first is disclosure; the second is confidence. That is
not one document with a field flipped.

**2. The privacy hazards differ, and that is a leg-3 difference between siblings, not merely between
this row and the default.** `vendor-management`'s sharpest hazard is a **payment fact** — its own
NJ-BO-VM-4 records that a supplier bank-change instruction is *a fraud vector, not merely confidential
material*. This row's sharpest hazard is **unconsented commentary on, and confidential material
belonging to, named third parties**. A single handling rule cannot serve both: one demands that the
product never write or act on a value it reads, the other demands that it never surface content it
holds. A merged row would have to carry both and would express neither.

**3. What a merged row's anchor would actually be.** Applying `partnerships-bd`'s decisive move to the
two-row case: strip this row and `vendor-management` of the structures above on the grounds that both
are *a counterparty relationship*, and the merged anchor is *an external organisation the holder has
dealings with*. That is an entity name and nothing else — the exact anchor
`business_operations.organisational-records` was refused for, quoted there as *"an organisation name
is constitutionally never-alone … A row whose entire support is never-alone evidence can never clear
activation (CONNECTION.md section 4 step 2), so it would be a row that never fires."* The merge
produces a row that cannot fire and destroys two that can.

**Not reversing the gist verdict. The two rows stand as two.** `vendor-management`'s NJ-BO-VM-3
(*which side of the relationship is the holder on?*) is accepted as a genuine and unresolved
detection difficulty, and it is reciprocated below — but a hard *detection* case is not evidence of a
single world; it is evidence that a single document sometimes fails to say which world it is in, and
the honest outcome there is `Review Later`, which is now what the new fixture routes to.

---

## Files considered and rejected

*(The gist draft's list, preserved, with the reasons deepened and three additions.)*

- **`QBR template - blank.pptx`** — kept as the collision fixture in the **wrongly-fires** direction.
  It carries the complete business-review structure with every value slot empty and a vendor's brand
  on the slide master. It is the cleanest demonstration that this row fires on a *filled* structure,
  not on a shape: a review structure with no counterparty is a template, and it routes to
  `Reference Clips`.
- **`Meridian - supplier scorecard 2026 H1.xlsx`** — **added this pass** as the collision fixture in
  the **must-not-be-lost** direction, which the gist draft lacked. One counterparty, a period, SLA
  columns, a rating, a relationship owner, a remediation column. Every one of those slots also
  appears on this row's artifacts; the discriminator is that the *ratings are of the counterparty*,
  which makes it `vendor-management`'s. Where the document does not say which party is rated, it
  routes to `Review Later` rather than being claimed. This is `vendor-management`'s NJ-BO-VM-3 given
  a fixture.
- **`Acme - company strategy 2026.pdf`** — kept deliberately, and it is the most important example in
  the row: a third party's confidential document, marked confidential, with no reference to the
  holder's organisation anywhere, held because a relationship exists. `group_without_copying_facts`
  is `false` on it for that reason.
- **`acme-contacts.vcf`** — kept as the contacts fixture, because `00` states the rule outright and
  the row must be seen to obey it rather than to restate it.
- **`Renewals forecast FY26.xlsx`** — kept as the shared object with `contract-administration`; both
  rows name it, and the row that owns it is not resolvable from structure.
- **A signed order form** — rejected. It is `contract-administration`'s, and the renewals-forecast
  fixture already carries that seam. Adding it would have implied a claim on the instrument.
- **A support ticket export** — rejected as an example, held as a `collides_with` against
  `support-operations` instead. That row's own file refuses a per-customer dimension for exactly this
  material; putting the export in this row's examples would have read as contesting that refusal.
- **A win/loss analysis** — rejected. It is pre-sale, and `partnerships-bd`'s settlement names *closed
  lost* and its win/loss review as its terminal state. Claiming it would reopen a settled question.
- **A sales pipeline or opportunity export** — rejected for the same reason, and named in `needs_llm`
  instead: a pipeline and an account plan share the stakeholder list exactly, and the contract's
  existence is the discriminator that the file rarely states.
- **A marketing case study, published** — rejected. The *approval and consent record* is this row's
  (it carries an approver on the counterparty's side); the published asset is `go-to-market`'s. The
  approval slot is now written as a deterministic signal so the seam is checkable.
- **An NPS or CSAT export** — rejected as an example. `support-operations` holds satisfaction exports
  and its file says so; this row's `collides_with` to `market-research` is deliberately absent (below).

---

## Reciprocal boundaries

For each, the boundary is stated in both directions, and the same contested bytes are named.

**↔ `business_operations.vendor-management`** — argued in full above; now written as a
`collides_with` on this side, which the gist draft was missing. **From that side:** it keeps a
supplier *"set up, safe to deal with, and honest"*, on an onboarding form with a remittance block, a
supplier register with a relationship owner, a diligence questionnaire and a scorecard. **From this
side:** the holder's own performance, measured and argued to a counterparty who may leave. **Same
bytes:** a scorecard-shaped spreadsheet naming one counterparty with SLA columns and a rating — that
row's unless the ratings are of the holder. **Divergence flagged honestly:** that row's file does not
carry a `collides_with` back to this one. The edge is one-sided from this side as of this pass;
recorded as **NJ-BO-CAM-2** for R1c, not fixed here, because editing a neighbour is out of scope.

**↔ `business_operations.contract-administration`** — that row's deepened file states the seam as
*"obligation versus relationship"* on the same renewal date and says it *"Reciprocated verbatim in
substance"* against this row's wording. Accepted; nothing here contradicts it. **From that side:** a
notice clause, a register entry, a notice calendar, a formal letter. **From this side:** an account
plan, a usage record, an internal renewal recommendation. **Same bytes:** `Renewals forecast FY26.xlsx`,
named in both rows' examples, carrying the contract end date (that row's anchor) and the internal
commentary column (this row's) in one sheet. Neither may resolve it from structure.

**↔ `business_operations.support-operations`** — **from that side:** a continuous queue of third-party
interactions, detected on *identifier + requester + status + agent in one header row*, and — this is
the part this row must not tread on — that row's `template.why` **refuses a per-customer dimension
outright**, on `00`'s collector prohibition. **From this side:** a relationship-level narrative with an
executive sponsor, an account owner and a commercial consequence. **Same bytes:** an outage record,
which is a major-incident ticket on that side and an escalation summary on this one; this row's
`Escalation summary - Acme - outage 14 Feb.docx` already says in `must_not_conclude` that *"an outage
narrative is also a support-operations record and an incident record"*. **Real tension, surfaced not
smoothed:** that row refuses the per-customer level; this row's prose recommends one. Both cannot be
family defaults without a stated rule. This row does **not** overrule it — the proposed distinction (a
bulk queue export may never acquire a per-counterparty branch; a bounded relationship file may, once
the user approves it) is offered to R1c and is now written into this row's `open_question` as item (3).

**↔ `business_operations.partnerships-bd`** — settled by that row and **reciprocated here in matching
terms: pre-sale is that row, post-sale is this one.** Its formulation is adopted rather than
re-argued: the two rows are *"mutex for one **opportunity**, not for one **counterparty**"*, so a
customer with a live expansion pursuit is legitimately both at once. **Same bytes:** an **expansion
proposal to an existing customer**, carrying a validity period (that row's slot) and an account number
plus usage history (this row's). Both fire honestly; `also_holds_with` cannot express it, because
CONNECTION's edge table is schema ↔ schema only and these are two templates on one schema, so it is
prose on both sides and P10's to choose from an accepted group. That row also names
`QBR - Northwind - Q1.pptx` as its primary wrongly-fires fixture and assigns it here; **accepted, and
this row's `Acme QBR - Q1 2026.pptx` is the same fixture under a different counterparty name.**

**↔ `career.consulting-client-engagement`** — **from that side:** a scoped deliverable, a fee
arrangement, a defined end, and `00`'s own `our_firm` / `client` pair, which lives on that row.
**From this side:** an ongoing subscription relationship with adoption and renewal records and no
defined end. **Same bytes:** a periodic review deck for a professional-services holder, which is a
client report there and an account review here. Genuinely close, and the reason this row does not
claim the `client` key.

**↔ `creative.client-engagement`** — **from that side:** a creative deliverable and a revision round.
**From this side:** no deliverable, only the relationship's own record. The seam is clean and the
overlap is furniture rather than substance.

**↔ `business_operations.go-to-market`** — **from that side:** a launch date and a readiness structure.
**From this side:** a named counterparty's own plan, usage and renewal record. **Same bytes:** a
reference case study — the *consent and approval record* is this row's, the *published asset* is that
row's.

**↔ `retail_hospitality.guest-feedback`** — **from that side:** a premises, a booking, or a guest-stay
anchor. **From this side:** a named business counterparty with a subscription relationship. Thin but
real, because satisfaction exports look identical.

### Neighbours considered that did NOT get an edge

- **`business_operations.market-research`** — voice-of-the-customer and NPS material sits in both.
  Left unedged: the `go-to-market` and `partnerships-bd` edges already carry the commercial cluster's
  discriminators, and a fourth would be **true and useless** — the schema row's own test for a bad
  edge.
- **`hr`** — account teams and named internal owners appear on every artifact here. Not edged; the
  whose-record-is-it discriminator belongs to the schema row and repeating it would rebuild it badly.
- **`nonprofit.fundraising-donor`** — donor stewardship is structurally the *same situation* with a
  different counterparty type: a relationship owner, a stewardship plan, a giving history that is
  structurally an adoption record, and a renewal-shaped ask. This is the closest unedged neighbour in
  the catalogue and it is **deliberately not guessed**, because the row is another agent's and the
  right answer may be that one of the two folds. Recorded as **NJ-BO-CAM-3**.
- **`finance`** — invoices and revenue records naming the same counterparty. Not edged: custodial money
  is `finance`'s by the family's anchor triple, and the confusion is about *which counterparty*, not
  about evidence.

---

## `proposed_fields`

**None minted, and the hole is named — unchanged from the gist draft, and the restraint is now
better argued.** The **customer** role has no canonical key. `00`'s pair is *"our_firm and client"*,
which is the professional-services reading; a subscription customer is a related but distinct role
and a supplier is a third.

This row **seconds the family's existing proposals rather than minting a variant**, per the
constraint and per the schema row's instruction that the third role be *"Raised on
`contract-administration`, `procurement-sourcing` and `customer-account-management` rather than
smuggled onto the schema"*:

- It endorses the schema row's `organization` proposal (custody role, `destination_eligible: false`,
  `reliability_ceiling: "possible"`), which R1c must settle **once** for this family and
  `construction_property` together.
- It endorses the schema row's `fiscal_period` proposal, while noting that the level this row would
  actually want there is a **relationship period**, not a fiscal one — recorded as inference, not as a
  competing mint.
- It **does not** mint `customer`, `supplier`, or a role variant. `vendor-management` records that the
  `supplier` key the schema row assigned to `contract-administration` was never proposed by anyone,
  and that it declined to mint it from the row that was told not to. This row is in the same position
  with respect to `customer` and takes the same course, for the same reason: minting a role key on a
  field-less schema at the exact point of maximum temptation would be the 574's mistake performed
  knowingly.

---

## NEEDS-JOSEPH

- **NJ-BO-9 (shared with `contract-administration`, `procurement-sourcing`, `vendor-management`) · No
  canonical key for the customer or supplier role.** `our_firm` / `client` cannot express either.
  Alternatives and their costs: (i) widen `client` to any commercial counterparty — cheapest, but it
  collapses the very role separation `00` demands; (ii) mint a third role key — honest, but it is a
  third key on a schema with no fields at all; (iii) make role a **value** on the proposed
  `organization` key — consistent with `partnerships-bd`'s accepted premise that role is a field
  value, and this row's preferred option, but it presupposes NJ-BO-1 resolving in favour of
  `organization`. Currently proposed by **nobody**, which is the actionable part.
- **NJ-BO-11 · Is a COUNTERPARTY-named folder acceptable in v1?** It is how people in this role really
  file, and it discloses the relationship, its commercial state, and by aggregation the holder's whole
  book. Alternatives: user-approved level with no automatic depth (this row's provisional posture);
  automatic but shallow; forbidden outright, as `support-operations` does for queue exports. Cost of
  forbidding: the row's recommendation collapses to function-first, which no practitioner files by.
- **NJ-BO-CAM-2 (new) · The `vendor-management` edge is one-sided.** This row now names that row;
  that row does not name this one. R1c should mirror it or record why not. Not fixed here — editing a
  neighbour is out of scope.
- **NJ-BO-CAM-3 (new) · `nonprofit.fundraising-donor` may be this row under another owner type.**
  Structurally the same situation. Left unedged and unguessed; R1c should decide whether the pair is
  two rows, one row, or an edge.
- **NJ-BO-CAM-4 (new) · The per-counterparty dimension rule is contested inside the family.**
  `support-operations` forbids it; this row wants it user-approved. One rule, stated once, is needed.
- **Carries NJ-J-IND-4 in its sharpest form** — this row's material is **third-party confidential by
  default** and no safety flag in the catalogue reaches it. The gist draft said this and it remains
  the most important unresolved thing about the row. Alternatives: rely on `potentially_sensitive`
  plus `Protected Records` (current, and it under-describes the hazard); add an explicit
  third-party-confidentiality marker on the sensitivity block (new mechanism, needs a P7 owner);
  or represent-without-moving such material entirely, as `support-operations` proposes for bulk
  exports.

---

## What changed in this pass

Checked line by line against the JSON that was actually written.

**Preserved unchanged** — the whole `one_line` substance, all 32 `proposed_context_terms`, all 14
`work_types`, all 7 `grouping_reasons`, the `template.why` prose recommendation, `file_kinds`, all 5
`falls_through_to` entries with `Protected Records` first, `sensitivity` and its `sensitivity_why`,
`fields: []`, `proposed_fields: []`, `refuse_node: false`, and the 10 original file examples with
their `must_not_conclude` lists.

**Added to the JSON:**

1. `one_line` — the retired "Gist-level placeholder" phrasing replaced with "Placeholder row (J-IND,
   deepened to J-DEPTH)", plus the sentence stating that the row is kept on **structure and privacy
   posture, never on the counterparty's role**, and citing `partnerships-bd`'s settlement.
2. Two new `deterministic` signals (10 → 11 … 12 entries counting the precondition): the **inbound
   third-party structure**, explicitly marked never-alone-by-construction; and the **reference /
   advocacy approval structure**, whose approver-on-the-counterparty's-side slot separates it from
   `go-to-market` collateral.
3. Two new `never_alone` entries (9 → 11): **a role word alone**, carrying `00`'s
   *"The system must separate roles that happen to contain the same entity type."* and accepting
   `partnerships-bd`'s premise explicitly; and **the direction of an addressee alone**.
4. A new first `collides_with` entry for **`business_operations.vendor-management`** (7 → 8 edges),
   arguing the direction-of-assurance discriminator, naming the divergent privacy hazards, and naming
   the same contested bytes on both sides.
5. A new file example, **`Meridian - supplier scorecard 2026 H1.xlsx`** (10 → 11), the collision
   fixture in the must-not-be-lost direction, routing to `Review Later` when the rated party is
   unstated.
6. `open_question` extended with item (3), the reciprocal tension with `support-operations` over the
   per-counterparty dimension, offered to R1c rather than asserted.

**Reversed:** nothing. The gist verdict (`refuse_node: false`) stands. What changed is the *ground*:
the gist rested the row on *"one customer as an ongoing relationship"*, which contains a role word
and would not survive the family's never-alone rule unaided. This pass rests it on four
structure-plus-slot signals, on the direction of assurance, and on a privacy posture that inverts the
family's fallthrough order. Stated openly as a change of argument, not a change of verdict — and the
gist's own wording is preserved in `one_line` rather than deleted, because it is a good description
even though it is not a good anchor.

**Considered and rejected as edits:** minting `customer` (declined, above); adding a
`collides_with` to `market-research` (true and useless); adding an `also_holds_with` for the
`partnerships-bd` expansion-proposal case (impossible — CONNECTION's edge table is schema ↔ schema
only); adding a `nonprofit.fundraising-donor` edge (deliberately left for R1c); claiming
`time_first: true` for a review cycle (forbidden to this whole family, and the schema row says R1c
should reject it on sight).

## Self-verification

- `python3 -m json.tool` on the JSON: **parses.**
- Every quotation in this memo and in the JSON re-checked verbatim against
  `00-database-agent-product-design.md` by script, with curly-quote normalisation: **all present.**
  The one quotation attributed to `00` *by analogy* — the university sentence read across to a
  company — is marked as inference on the row, as it was in the gist draft.
- Quotations attributed to neighbour files (`vendor-management`, `partnerships-bd`,
  `contract-administration`, `organisational-records`, the schema row) were copied from those files
  in this session.
- Key set unchanged from the landed siblings; no keys added or removed.
- Files written: **only** `business_operations.customer-account-management.json` and this memo. No
  neighbour, roster, canonical-fields, or `src/` file touched.
- Counts in *What changed* were read back out of the written JSON, not from intent: deterministic 12
  (incl. precondition), never_alone 11, collides_with 8, file_examples 11.

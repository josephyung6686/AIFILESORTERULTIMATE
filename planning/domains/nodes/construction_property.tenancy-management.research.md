# construction_property.tenancy-management — lab notes

Depth: J-DEPTH. Placeholder row (J-IND), `launch: "placeholder"`, `fields: []`. Absorbs legacy id
`prop.tenancy` (ROSTER.md Appendix A).

**Verdict: the row STANDS.** The gist pass's verdict is confirmed, not reversed — but two of its
supporting arguments were wrong and are corrected below, and one of its edges pointed at a row that
has since refused. The three charges the dispatch brought are answered in full, and the one that had
real force (the `finance.household-property` charge) forced the row's central discriminator to be
rebuilt on documentary grounds. That rebuild is the substance of this pass.

---

## Sources actually used

### Binding
- `planning/00-database-agent-product-design.md` — every quotation below `grep -F`-matched verbatim
  against this file before it was written. Note the curly apostrophe in the abstention sentence;
  the straight-quote form does not match and was corrected during this pass.
- `planning/domains/CONNECTION.md` (§2 node test, §5 closed edges and the never-alone list, PR-2 and
  PR-6 on safety ordering and the field deferral), `_CONTRACT.md` (rules 3, 5, 8, 9, 10, 11–15),
  `ALIGNMENT.md`, `roster.json`, `canonical_fields.json`, `src/evidence_shape/vocabulary.py`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, D4, J-IND. Not re-debated.

### The schema anchor, read first as the addendum requires
`construction_property.research.md`, now at J-DEPTH. Three things in it govern this row:

1. **The family default template**, which is the paragraph this row must differ from:
   > **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
   > function**, with a period level only where the situation *genuinely cycles* (a service-charge
   > year, a rent-review cycle). **Not time-first.**
2. **The professional-versus-householder seam**, drawn on INSTRUCTION and explicitly not on the
   address, the document type, the money, the trade or the format. Its warning — *an address does
   not select a side* — is this row's constitutional never-alone.
3. **The two refusals already made by this family**, `compliance-certificate` and `timesheet`, and
   the lesson attached to each. The first of them turns out to matter to this row's edge list; see
   "A stale edge, found and fixed" below.

### Siblings read in full and not rewritten
- **`construction_property.commercial-lease.research.md`** — deepened, and it names this row twice:
  once in its leg-1 dimension argument and once in a whole section titled *The commercial/residential
  seam*. Both are answered below, one confirmed and one corrected on a point of attribution.
- **`construction_property.block-management.research.md`** — deepened. It states, in terms, that it
  and this row *"share **no discriminating evidence item**"* and declines an edge for that reason.
  This pass agrees and reciprocates without minting an edge back.
- **`construction_property.service-charge.research.md`**, `inventory-inspection`, `trade-job`,
  `agency-listing`, `compliance-certificate` (refused), `progress-photos`.

### Landed launch rows read for the seams and for depth calibration
`finance.household-property`, `legal.leases-agreements`, `finance.crypto-assets` and
`legal.practice-matter-file` (calibration only), `finance.hoa-residents-association`.

---

## The three charges, answered

The dispatch brought three. They are not equally strong and this memo does not pretend they are.

### Charge (a) — "you may be a lifecycle stage of `commercial-lease` rather than a world"

**Rejected, and it is the weakest of the three.** Two independent reasons.

First, the factual premise is wrong. The charge assumes this row holds "only what happens
afterwards." It does not. Roughly half this row's material is **pre-grant**: the applicant's
referencing pack, the affordability calculation, the credit check, the previous-landlord reference,
and the right-to-rent identity check. None of that exists after a lease is granted; all of it exists
before there is a tenancy at all. A row that holds the vetting, the grant and the reckoning holds a
relationship end to end, which is what a world is.

Second — and this is decisive — **the two rows never hold the same bytes.** `commercial-lease` is
commercial; this row is residential. Its own deepened memo draws the reciprocal table and puts the
deposit protection certificate, the prescribed information, the co-occurring safety certificates and
the residential statutory notice on this row's side, and the alienation regime, the contracting-out
declaration, the upward-only review memorandum, the AGA and the terminal dilapidations schedule on
its own — *"none of which has a residential counterpart"*. A lifecycle stage of X shares X's
evidence and adds a phase. These two share **no document at all**. They are siblings, not stages.

The one thing the charge gets right is that both rows are *about* an occupier under an agreement,
which is why they carry a reciprocal edge rather than nothing.

### Charge (b) — "a private landlord's tenancy papers are `finance.household-property`'s material, and
the only discriminator is that a professional does the managing"

**This charge has real force, and half of it lands.** The gist draft was guilty of exactly what it
alleges, and this pass fixes it rather than defending it.

What the landed household row actually says, read before writing: its work-type list names
*"tenancy inventory"* and *"rent/deposit receipt"* among its **own** values; one of its explicit
grouping rules is *"one tenancy period"*; and its fixtures include `Move-in Inventory and Condition
Report - 18 River Court.pdf` and `Rent Receipt - January 2026.eml`. **The household row is right
about all of that and this row does not contest a line of it.** The overlap the dispatch named is
genuine, not imagined.

**Where the gist draft was wrong.** Its `finance.household-property` edge read, verbatim from the
pre-pass JSON:

> *…and several properties or several successive tenancies supports this row.*

That is **corpus scale**, and scale needs a threshold, which `_CONTRACT` rule 3 forbids inventing.
It is also, in substance, the dispatch's charge admitted: it discriminates on how much letting the
holder does, which shades directly into "a professional does the managing." A related error sat in
`recognition.needs_llm`, which asked the model to separate *"a MANAGED portfolio … from ONE let
property held by an accidental landlord."* Both have been rewritten in this pass.

**The discriminator as it now stands, and it is documentary in every limb.** Four structures exist
on the letting side and have no counterpart in a household's own file:

1. **A referencing pack about another named person** — their employer, their salary, a credit check,
   a previous landlord's written opinion of them, and copies of their identity or immigration
   documents. A household holds its **own** identity documents; it does not hold a third party's
   credit file. This is the strongest limb and it is asymmetric by construction.
2. **A deposit protection scheme certificate held by the party who protected the deposit, together
   with a served-on confirmation of prescribed information.** The tenant receives prescribed
   information; the landlord or agent holds the evidence that it *was served*, with a date and a
   method. Confirmation-of-service is a structure, not a document type.
3. **A rent ledger, not a rent receipt.** The household row's fixture is a receipt — a single period,
   an amount, a payment status. This row's is a running account: due dates against amounts due
   against amounts received against a balance carried forward, per tenancy. *"Tables matter because
   resumes, forms, applications, invoices, and administrative documents often place their most useful
   information in cells rather than body paragraphs."* Receipt versus ledger is the cleanest single
   test in this memo and it is the one the household row itself already half-drew.
4. **A statutory notice served on an occupier**, carrying a ground or section, a date of service and
   a method of service. Receiving one is the household's; serving one is this row's.

**What the discriminator deliberately does not use, stated so R1c can hold this row to it:** the
number of properties; whether an agent is involved; and the presence of an agent's letterhead. A
private landlord letting one flat who vets a tenant, protects a deposit, serves a notice and keeps a
ledger **fires this row**, on that apparatus alone, with no professional anywhere in the file. That
is the direct answer to the charge: the discriminator survives with the organisation removed.

**Where both fire.** A household that lets one flat honestly produces both files, and the landed
household row's own NJ-hp-2 anticipates precisely this shape. Both activate on disjoint evidence and
`finance`'s safety ordering runs first. That is NJ-CP-TEN-1 and it is genuinely Joseph's.

### Charge (c) — "the same world as `block-management`, with the unit of management as the only
difference, and a unit is plausibly a field value"

**Rejected, and the neighbour agrees in writing before this pass began.** `block-management`'s
deepened memo lists this row under *Neighbours considered that did not get an edge*:

> because the two rows share **no discriminating evidence item**: a deposit
> certificate and an apportionment schedule cannot be confused with one another.

That is the whole answer and it is theirs, not this row's. The fingerprints are disjoint:
`block-management` activates on an apportionment schedule, a staged consultation and a budget/account
pair over a named accounting year, with a leaseholders' body behind it; this row activates on the
deposit-and-compliance co-occurrence with a person living in the property. The unit of management is
not the difference — the **counterparty** is. A leaseholder owns a long interest and pays toward a
building; a tenant occupies under a term and pays rent to a landlord. Those produce different papers.

Corroboration worth recording because it happened independently: `block-management` refuses to
recommend a **unit** level in its dimension order, on the ground that a unit is a household and a
unit level writes a real person's home into a directory name. This row reached the identical
conclusion about a **tenant name** level (NJ-CP-TEN-3) from the other direction, before reading it.
Two rows arriving separately at the same collector prohibition is evidence the prohibition is real.

---

## The node test, all three legs, argued

The schema is `construction_property`. CONNECTION.md §2: a template row exists only where its
detection signals, its recommended dimensions, **or** its privacy rules differ from the schema's
default template. The default is quoted above. Each leg separately.

### Leg 2 first, because it is the strongest — detection signals

The family's detectable structures are the title block, the measured-works table, the *to date, less
previously certified* shape, and the apportionment schedule. **This row has none of them**, and
that is the point: it is detectable by something the family does not otherwise use.

Its fingerprint is a **co-occurrence, not a document**. A tenancy agreement, a deposit protection
certificate carrying a scheme name and a reference, a gas safety record, an electrical condition
report and an energy certificate, **all for one address**, each with its own expiry or next-due date.

Why the co-occurrence and not any member:

- Every one of the five exists in an owner-occupier's file. A gas safety record is issued for people
  who own their homes. An energy certificate is produced to sell as well as to let.
- Therefore **no member identifies the row alone**, and each is listed in `never_alone` for that
  reason. This is an unusual detection shape and the memo states it as such rather than dressing it
  up as a keyword list.
- Nothing else in the catalogue assembles that particular five for one address. `trade-job` holds one
  certificate against a job reference; `agency-listing` holds an energy certificate against
  particulars; `finance.household-property` holds any of them against a home the holder lives in.
  The **set** is unclaimed.

Three further structures, each supporting and none sufficient: the deposit-protection structure
(scheme certificate plus prescribed information plus served-on confirmation); the rent-ledger
structure (the receipt/ledger test above); and the referencing pack, which the JSON accurately calls
the most identity-dense material anywhere in this schema.

**Verdict on leg 2: passes cleanly.** It is the leg the row would be defended on if it had only one.

### Leg 1 — recommended dimensions

Two differences from the default paragraph, one confirming a sibling and one qualifying it.

**The `instruction` level is a TENANCY, and `commercial-lease` is right about why.** Its deepened
memo argues that the family's `instruction` level *"assumes a commissioned piece of work with a start
and an end; a tenancy is a relationship with a term, and the level that separates two of them is the
term itself."* **This row confirms that from the residential side and adopts it rather than
re-phrasing it.** The 2019 letting of 14 Oakfield Rd and the 2023 letting of the same flat are two
tenancies at one property, and a 2019 deposit deduction is meaningless inside the 2023 file. The
level that separates them is the term.

**On the period level, this row diverges — and the divergence is smaller than the dispatch supposed,
so the record is corrected here rather than argued past.** The dispatch's framing was that
`commercial-lease` *"needs no period level while you and `service-charge` correctly do."* Read
directly, that memo names **`service-charge` and `block-management`** — not this row — as the two
siblings that correctly take a year level, on the ground that a service-charge year is a *named
accounting period*. This row is not among the two, and takes neither position:

- A **fixed-term** residential tenancy does not cycle. A year level under it would scatter one
  tenancy across two directories and produce exactly the *"meaningless one-child levels"* the
  template validator rejects. On this half, `commercial-lease` is right and this row agrees.
- A **periodic** tenancy that has outlived its fixed term genuinely does cycle: an annual gas safety
  record, an annual rent review, an annual statement. There, and only there, a period level under the
  tenancy is earned.

The recommendation is therefore **conditional**, and it is written into `template.why` in those terms.
It is a difference from the family default in the same direction as `commercial-lease`'s, not a
contradiction of it. **It is explicitly not offered as the leg that earns this row a node** — the row
would stand on leg 2 alone.

**Not time-first**, per the family rule and `00`'s reason: *"putting year first scatters related work
across calendar folders."* The conditional period level sits *under* property and tenancy, not above
them, which is the same relationship `block-management` records for its year level.

**One level declined outright.** Naming the second level after the **tenant** rather than the period
is what an agent would want, because their whole working life is tenant-keyed. It writes a private
individual's name into a directory that other software indexes. This row declines to recommend it and
records the conflict as real rather than resolved: NJ-CP-TEN-3.

`dimension_order` is `[]` by binding contract — a dimension may only branch on a field the same
entry's schema declares, and this schema declares none (D1 as narrowed, `_CONTRACT` rules 10 and 15,
CONNECTION PR-6). All of the above is prose in `template.why` for whoever answers NJ-CP-1. Whatever
lands stays a recommendation: *"The system recommends an order based on the domain template, but the
user can reverse, remove, add, or flatten dimensions."*

**Verdict on leg 1: passes**, on the tenancy-as-term level; the period qualification is honest detail,
not load-bearing.

### Leg 3 — privacy rules

The family default's privacy ground is that *the material names a real person's home and who is in
it*, and the family setting is `potentially_sensitive`. This row differs **in degree so extreme that
it changes the default routing**, which is the form of difference §2 contemplates.

- **Its default residual is `Protected Records`, not its exception.** The schema anchor records that
  this is true of no other construction row except `site-health-safety`. *"Protected Records may
  represent sensitive isolated material such as passport scans, medical documents, account statements,
  visas, legal forms, or credentials; it should normally remain local-only and must not cause
  filenames or content to be exposed in model prompts."* A referencing pack is a passport scan, an
  account statement and a credit file in one folder.
- **`00`'s corpus sentence describes this row's ordinary contents almost item for item**: the corpus
  *"can include identity documents, account statements, tax records, medical information, legal
  records, credentials, private correspondence, GPS metadata, employment materials, and educational
  records"*. Referencing produces identity documents, account statements and employment materials by
  design, not by accident.
- **The exposed party is not the holder and cannot consent.** This is the sharpest ground. Almost
  everything protected here is about the tenant; the file exists in the landlord's or agent's custody.

**The reciprocal contrast is worth stating because a sibling drew it first.** `commercial-lease`'s
exposure is *commercial confidence* — a live negotiating position — and it says so, calling its own
leg 3 *"weakest … not load-bearing."* Two rows with the same subject and opposite privacy postures
is precisely the case §2 contemplates, and the contrast reinforces the split rather than crossing it.

Ordering is stated as a precondition inside both `recognition` blocks, per PR-2: *"Privacy policy
must be enforced before content reaches any model or external connector."* No `is_safety_domain` —
`00` names four safety domains and this is not among them — and no P7 handling class is assigned.

**Verdict on leg 3: passes, and here it is load-bearing** in a way it is not for `commercial-lease`.

**Overall: three passing legs, two of them strongly. The row stands.**

---

## A stale edge, found and fixed

The gist JSON carried a `collides_with` edge to **`construction_property.compliance-certificate`**.
That row's own node file now reads `refuse_node: true`, and the schema anchor records the refusal
and its reasoning: its only candidate signal reduces to *a document-type word plus an address*, and
both halves are constitutionally never-alone on this schema.

**A refused row cannot be a collision endpoint.** The edge was removed. The coverage it was pointing
at does not disappear, and this row is one of the *"situations that actually produce certificates"*
the anchor routes it to — a standalone certificate with no tenancy around it goes to Independent
Records, which this row already carries in `falls_through_to`.

The edge was replaced by a **live** collision that the gist pass missed: **`construction_property.trade-job`**.
The gas engineer or electrician who issued the certificate holds the identical bytes in their own job
file. The discriminator: an engineer's registration number, a job reference, a labour-and-materials
line and an invoice to whoever instructed the visit is the trade's; the same certificate co-occurring
with a tenancy agreement, a deposit certificate and prescribed information for one address is this
row's. The same bytes are genuinely both files, in two custodies — which is the schema anchor's own
custody-triple point applied to a certificate.

---

## Files considered and rejected

Not what this row holds — what tempts it and is not its evidence.

| File | Where it goes, and why not here |
|---|---|
| **`Schedule of condition - 14 Foundry Row - Fenwick Surveyors.pdf`** | `survey-valuation`'s collision fixture, taken verbatim from its owner. A reliance structure and a limitation of liability, and **no tenancy machinery at all**. This row must not acquire a surveyor's-report signal. |
| A commercial lease with alienation and dilapidations provisions | `commercial-lease`. The primary collision fixture, unchanged from the gist pass and now reciprocated by that row in its own words. |
| **`Rent Receipt - January 2026.eml`** — the household row's own fixture | `finance.household-property`, then `Receipts and Confirmations` when isolated. A single received receipt is not a ledger. This is the receipt/ledger test at work on named bytes, and the household row named them first. |
| **`Move-in Inventory and Condition Report - 18 River Court.pdf`** — also the household row's fixture | The **situation** is `construction_property.inventory-inspection`; the household row holds the occupier's copy. This row claims a check-out comparison only as *purpose*, never as a situation, and is edged reciprocally to both. |
| A standalone gas safety record with a next-due date and nothing else | `Independent Records`. Its would-be owner `compliance-certificate` refused, and correctly. |
| Landlord tax return, buy-to-let mortgage statement, rental income summary | `finance.*`. This row stops at the ledger. Money leaving the ledger for a tax computation has left this world. |
| Ground rent demand, service charge demand, Section 20 consultation notice | `service-charge`, `block-management` and `finance.hoa-residents-association`. These genuinely arrive in a landlord's tenancy folder for the same flat, which is why `hoa` gets an edge; the apportionment schedule is unmistakably not this row's. |
| Letting particulars, portal listing, viewing feedback, an offer | `agency-listing`. Material made to **find** an occupier, not to run the tenancy. A rent figure and an address count for neither — the same call `commercial-lease` made. |
| Licensing application, enforcement notice, standards inspection report | `government.housing-authority` where the authority's framing dominates; edged, because the same document is the landlord's obligation and the authority's record. |
| A blank AST template, a published how-to-rent guide, a deposit scheme leaflet | `Reference Clips` / `Reading Inbox`. Nothing is filled in, so no relationship is evidenced. The landed HOA row and `block-management` both made the identical call about blank templates. |
| A recurring monthly credit in a bank statement, the right size for rent | Nothing. A recurring monthly sum is also a salary, a standing order, a subscription and a loan repayment. In `never_alone` explicitly. |
| A managing agent's own PI insurance, staff payroll or client-account audit | `business_operations` and `finance`. The agent running *itself* is not the tenancy. Same distinction `block-management` draws from its side. |
| A `.vcf` for the tenant or the out-of-hours contractor | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most. |

---

## The collision fixture, in both directions

The addendum asks for both, and both are named on the same bytes as the neighbour names them.

**A file that would wrongly fire this row.**
`Gas Safety Record - 14 Oakfield Rd - 2026.pdf`, held **by the homeowner who lives there**. It has an
address this row cares about, a next-due date this row's compliance calendar is built on, an
engineer's registration, and a filename an eager matcher would take. It is not this row's — it is the
householder's own maintenance record, `finance.household-property`'s, and if isolated, Independent
Records'. **What discriminates:** the absence of every other member of the co-occurrence. No tenancy
agreement, no deposit certificate, no prescribed information, no ledger, no tenant. One certificate is
never this row, and `never_alone` says so in those words. This fixture is the reason the fingerprint
had to be a set.

**A file that must not be lost TO this row.**
`Lease Agreement - 18 River Court - Signed.pdf` — the landed `finance.household-property` row's
**mandatory legal collision fixture**, named here with its own filename so both sides argue the same
bytes. Parties, premises, covenants, execution blocks. It is an **executed instrument**, and
`legal.leases-agreements` is a safety template that owns it and protects it first (PR-2). This row is
the management *around* the instrument, never the instrument. The household row's rule —
*"A signed lease stays on the Legal template side even though the tenancy group may surface it beside
receipts and inventories"* — is adopted here unchanged and applied to this row as well: the tenancy
group may surface it; no fact is copied onto it; `group_without_copying_facts: true` on the
corresponding file example. **A tenancy agreement alone is in this row's `never_alone` list** for
exactly this reason, which is the concrete form of the protection.

---

## Reciprocal boundaries, both directions

| Neighbour | This row must not take | That row must not take |
|---|---|---|
| `legal.leases-agreements` (safety, landed) | the executed instrument, or any protective priority over it; legal orders first | the referencing, the compliance calendar, the ledger, the service record — the running of the relationship, none of which is an instrument |
| `finance.household-property` (landed) | the holder's own occupation, ownership, taxation, insurance and maintenance record; a received rent receipt; an inventory the holder was given | a referencing pack about a third party, a deposit-protection certificate with a served-on confirmation, a rent ledger, a served statutory notice |
| `construction_property.commercial-lease` | the alienation regime, contracting-out declaration, upward-only review memorandum, AGA, terminal dilapidations schedule | the deposit protection certificate, prescribed information, the co-occurring residential safety set, notices served on a person living there |
| `construction_property.block-management` | leaseholders, an apportionment schedule, a consultation, a building's own insurance | a tenant, a deposit, a tenancy agreement, a letting. It already declines these in writing |
| `construction_property.service-charge` | a budget/account pair over a named accounting year | a rent ledger, which is a tenancy account and not a building's money cycle |
| `construction_property.inventory-inspection` | the inspection **situation** — the room-by-room record is theirs | the tenancy the inventory belongs to, and the deposit deduction it feeds |
| `construction_property.trade-job` | an engineer's job reference, labour-and-materials lines, the invoice for the visit | the tenancy context that turns a certificate into a compliance obligation |
| `government.housing-authority` | the authority's enforcement framing and statutory scheme records | the landlord's or agent's own tenancy file |
| `finance.hoa-residents-association` | a leaseholders' body, a communal budget, an association's governance | the tenancy for a flat that happens to sit inside the association's building |

**One asymmetry worth naming.** `block-management` declined an edge back to this row, on the correct
ground that agreement should not be recorded as conflict. This row keeps its edge outward, because
ground rent and service charge demands really do land in a landlord's tenancy folder and a reader of
this file needs to be told where they go. A one-way edge is the honest shape here, and it is
deliberate rather than an oversight.

---

## `proposed_fields`

**None.** The schema declares no field rows (D1 as narrowed, PR-6, `_CONTRACT` rules 10 and 15), so
`fields: []` and `proposed_fields: []`.

This row **seconds** the schema row's existing proposal of a `property` key (NJ-CP-1) rather than
minting a variant, and notes that the landed `finance.household-property` independently proposes the
same key from the finance side — which is corroboration R1c should weigh, not two competing requests.
A **tenancy** key is the natural second, and `commercial-lease` records the same want; this row does
not mint it either, and defers to whichever form R1c prefers.

**D4 and `_CONTRACT` rule 9 bite harder here than anywhere else in this family.** Deposit protection
schemes, prescribed forms, right-to-rent regimes, notice sections and licensing all differ by country.
Every one of those differences must stay a **value**, never a field name. No jurisdiction-specific key
is proposed and none should be.

---

## Sparse-file discipline

Recorded because this row's corpus is unusually full of thin members. A photograph in a check-out
folder gets its Photos facts and no tenancy fact. A screenshot of a scheme portal gets capture facts
and OCR text, and OCR is `possible` at best. An encrypted agent pack — routine here, which is why
`Unsupported or Encrypted` is a busy residual for this row — stays metadata-only; filenames do not
rescue it. Group membership never writes a fact onto a member:
*"The documents are content-incoherent but purpose-coherent."* And where nothing settles it:
*"A model that cannot cite sufficient evidence must return unknown."*

---

## NEEDS-JOSEPH

- **NJ-CP-TEN-1 · The one-let-flat household seam.** Reciprocal with landed
  `finance.household-property`, which anticipates the same shape in its own NJ-hp-2. A household that
  lets one flat produces both rows' evidence on disjoint grounds. **Alternatives:** (i) both activate
  and `finance`'s safety ordering runs first — the provisional reading, written into the JSON;
  (ii) `finance.household-property` takes precedence for any holder with a residence record for the
  same address, which is simpler but silently deletes the referencing pack's protection posture;
  (iii) a threshold on properties or tenancies — **rejected here**, because `_CONTRACT` rule 3 forbids
  inventing one, and it is the error the gist draft actually made.
- **NJ-CP-TEN-2 · The tenant's own copy.** Stated reciprocally so no row silently claims both sides:
  the tenant's file of the same documents is `legal.leases-agreements` plus
  `finance.household-property`, not this row. Unchanged from the gist pass and still correct.
- **NJ-CP-TEN-3 · A tenant's name as a folder level.** The natural second dimension writes a private
  individual's name into a directory other software indexes. This row declines to recommend it. The
  conflict is usability against `00`'s collector prohibition, and it is Joseph's. `block-management`
  reached the identical conclusion about a **unit** level independently.
- **NJ-CP-TEN-4 · New this pass. The refused `compliance-certificate` leaves a routing gap.** With
  that row refused, a standalone in-date certificate for a property has no situation and lands in
  Independent Records — correct, but it means a landlord's compliance calendar is only assembled when
  a tenancy file is present. Is that acceptable, or should the certificate set be recognisable as a
  property record independent of any tenancy? This row cannot decide it, because deciding it in its
  own favour would resurrect exactly the row the family refused.

---

## Audits run before returning

- `python3 -m json.tool` on the JSON: parses.
- Every `00` quotation `grep -F`-matched against `planning/00-database-agent-product-design.md`
  before it was written into either file. One correction found and applied: the abstention sentence
  uses a curly apostrophe in *"product’s"*, and the straight-quote form returns zero matches.
- Every `collides_with` endpoint checked against its own node file for `refuse_node`. One failure
  found — `compliance-certificate`, refused — and fixed as described above. The other seven are live.
- Neighbour memos read before their edges were written or amended, per the addendum. No neighbour
  file was edited; the one place this row diverges from a neighbour's framing (the period level,
  against `commercial-lease`) is stated explicitly in both this memo and `template.why`.
- Key set compared against the landed siblings: identical.
- Files written: exactly the two assigned.

---

## What changed in this pass

Checked against the JSON as actually written, not against intent.

**Preserved unchanged**, because it was right: the co-occurrence fingerprint and the whole
`recognition.deterministic` block bar one line; the `never_alone` list, which is the strongest part of
the gist draft; the six `falls_through_to` residuals with their verbatim quotes; `sensitivity` and
`sensitivity_why`; the `template.why` ordering argument and `time_first: false`; the ten file
examples; `work_types`, `grouping_reasons`, `file_kinds`, `proposed_context_terms`; and NJ-CP-TEN-1
through 3.

**Changed in the JSON** — four edits, all verified in the written file:
1. `collides_with` — `construction_property.compliance-certificate` **removed** (that row refuses) and
   replaced by `construction_property.trade-job`, with the certificate-custody discriminator argued.
2. `collides_with` — the `finance.household-property` signal **rewritten** to drop *"several
   properties or several successive tenancies"* and rebuilt on four documentary structures, with an
   explicit statement that neither portfolio size nor professional involvement is part of the test.
3. `collides_with` — the `commercial-lease` signal **amended** to strike *"between two companies"*,
   adopting that row's friendly amendment and saying so.
4. `recognition.needs_llm` — the *"MANAGED portfolio versus ONE let property"* line **rewritten** to
   remove scale as a discriminator and recast corpus shape as reviewer context only.
   Plus: `template.why` extended with the conditional period-level position, and `one_line`'s
   *"Gist-level placeholder"* restamped as researched to J-DEPTH.

**Added in the memo**, which is where the bulk of the deepening is: the three dispatch charges
answered individually; the node test argued leg by leg against the schema anchor's quoted default
template, with leg 2 taken first as the strongest and leg 1's period qualification marked as not
load-bearing; a thirteen-row *files considered and rejected* table; the collision fixture in both
directions, naming the household row's own `Lease Agreement - 18 River Court - Signed.pdf` and
`Rent Receipt - January 2026.eml` on the same bytes both sides argue; a nine-row reciprocal boundary
table with the one-way-edge asymmetry explained; sparse-file discipline; NJ-CP-TEN-4; and this audit.

**Reversed:** nothing. The gist verdict that this row stands is **confirmed**, on stronger grounds
than the gist draft gave. Two of its *arguments* were reversed — the scale-based household
discriminator and the organisation-flavoured portfolio instruction — and one of its edges was
retired as stale. The dispatch's charge (b) was the one that had force, and it improved the row.

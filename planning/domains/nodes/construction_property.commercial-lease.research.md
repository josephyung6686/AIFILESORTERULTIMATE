# `construction_property.commercial-lease` — lab notes

Depth: J-DEPTH
Row: `construction_property.commercial-lease` · kind `template` · schema `construction_property`
· launch `placeholder` · absorbs the legacy row `prop.commercial-lease`.

**Status of this pass.** The row was written once under the retired `Depth: GIST` label. That draft
was verified-but-shallow: its JSON key set was house-correct, its quotations were machine-verified,
and its central argument — *instrument versus running apparatus* against `legal.leases-agreements` —
was right and is kept unchanged. This pass **deepened rather than rewrote**, with one substantive
correction that goes the other way: the gist memo rested the node test on two structures it claimed
existed nowhere else on the roster, and that claim is **wrong** against the landed
`construction_property.survey-valuation`. The correction is argued in full below and the row still
stands, on a different leg. See *What changed in this pass* at the end.

The dispatch warned that this row might not survive, on the ground that *the tenant is a business*
is an organisation name and organisation names are never-alone on this schema. **That warning is
correct and the row does not rely on it.** It is answered directly in the node test and again in the
`tenancy-management` boundary: the line is the covenant regime and the documents it produces, not
the legal form of the occupier.

---

## Sources actually used

### Binding local sources

- `planning/00-database-agent-product-design.md` — the only document quoted. Every quotation in the
  JSON was grep-verified back out of it verbatim, including the curly apostrophes. The spans that
  did the work here:
  - the multi-role-token sentence, which is this family's constitutional never-alone and which is
    also the dispatch's warning in `00`'s own words: *"A university name alone should not create a
    group because Columbia can appear as an authoring school, course provider, target institution,
    employer, research venue, or merely a cited organization."* Read across to a tenant company's
    name, it is why *the occupier is a business* can never be this row's evidence.
  - the abstention sentence, which is this row's most frequent correct outcome because four rows can
    honestly claim one premises address: *"Correct abstention is a successful outcome because the
    product's goal is reliable organization, not maximum file movement."*
  - the dimension-order sentence, which licenses the premises-first recommendation and forbids the
    time-first temptation this situation invites: *"For document and record domains, project,
    function, or subject usually comes before time because putting year first scatters related work
    across calendar folders."*
  - the sparse-file rule, which is load-bearing here because a rent roll is a table of other
    people's premises: *"The graph does not automatically copy those missing facts onto sparse
    files."*
  - the purpose-coherence sentence, which is the whole justification for the one-tenancy group: *"The
    documents are content-incoherent but purpose-coherent."*
  - the table sentence, behind the dilapidations and recharge signals: *"Tables matter because
    resumes, forms, applications, invoices, and administrative documents often place their most
    useful information in cells rather than body paragraphs."*
  - the privacy-ordering sentence, which is the precondition on every detection entry: *"Privacy
    policy must be enforced before content reaches any model or external connector."*
  - the residual-library definitions, for all six `falls_through_to` entries.
- `planning/domains/_CONTRACT.md` — rules 3 (no invented numbers; this row states no notice period,
  no review cycle length and no quarter-day date, all of which are jurisdictional), 8, 10 and 15 (no
  field rows on a placeholder schema), 11–14 (closed edge vocabulary).
- `planning/domains/CONNECTION.md` — §2 node test, §4 activation and its never-alone step, §5 closed
  edge vocabulary, PR-6.
- `planning/prompts/ALIGNMENT.md` — *"would only repeat its schema's fields and dimension_order"* …
  *"it is the schema's default template."* This row's whole burden.
- `planning/domains/canonical_fields.json` — all 37 keys re-read. **No key minted, none proposed.**
- `planning/overnight/council/DECISION-BRIEF.md` — D1 (as narrowed), D4, D6, PR-6, J-IND taken as
  ratified. J-DEPTH (2026-08-24) overrules J-IND's gist clause.

### Landed rows read in full before writing, and not contradicted

- **`legal.leases-agreements`** (safety, full depth) — the sharpest seam, and the one the dispatch
  put first. Read completely. Its instrument-versus-running-apparatus formula is adopted in its own
  vocabulary rather than re-phrased, so the two edges read as one boundary.
- **`construction_property`** (schema anchor, J-DEPTH) — the default template this row must differ
  from, and the row that **already assigns** the estate-management apparatus to this schema by name.
- **`construction_property.subcontract`** (J-DEPTH) — it settled the identical contract-versus-`legal`
  charge one row over. Its resolution is adopted, not re-derived.
- **`construction_property.survey-valuation`** — read this pass, and it is the row that forced the
  correction. It names the schedule of condition and the dilapidations schedule among its own
  deterministic signals.
- **`construction_property.tenancy-management`** — landed after the first pass, and it routes its
  commercial collision fixture *here*. The reciprocal is now written.
- **`construction_property.service-charge`**, **`.block-management`**, **`.agency-listing`**,
  **`.construction-project`** — siblings that handle a lease's ongoing life, its marketing and its
  works.
- **`business_operations.facilities-workplace`** — the collision most likely to fire on a real
  corpus, because most holders of these files are the tenant.
- `construction_property.compliance-certificate.json` and `.timesheet.json` — the family's two
  refusals, read as the standard this row had to clear rather than as a template to copy.

### A source that is not available, and it matters

`00` **never names this world.** Its template-library sentence lists *"academic programs, university
applications, recruiting processes, client engagements, research workflows, financial records,
travel, legal matters, creative projects, software repositories, personal administration, and photo
collections"*. Commercial property is absent. `design_cite` is therefore `null`, `provenance` is
`proposal`, and every `collides_with` entry is `provenance: inference`. `00` supplies the machinery;
this row supplies the situation.

---

## The node test, all three legs, argued

CONNECTION.md §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default template. The schema anchor
states that default explicitly, so the test is checkable rather than rhetorical:

> **`property` or site → `instruction` (the job, the letting, the scheme, the block) → document
> function**, with a period level only where the situation *genuinely cycles*. **Not time-first.**

And it states the trap, which is the one this row had to be tested hardest against:

> *`variation`, `snagging`, `dilapidations`, `retention`, `preliminaries`, `certificate`, `drawing`,
> `schedule`, `survey`, `valuation` and `report` are **values of `work_type`**, not rows.*

`dilapidations` is on that list by name. **A row cannot be earned by holding dilapidations
documents.** Everything below is written knowing that.

### Leg 2 first, because it is where the row nearly died

Leg 2 is detection. The gist draft named two structures — the **schedule of condition** and the
**dilapidations schedule** — and said neither exists anywhere else on the roster.

**That is false.** `construction_property.survey-valuation` landed with this among its own
deterministic signals:

> a schedule of condition or dilapidations: a room-by-room or element-by-element written record
> cross-referenced to numbered photographs, produced at the start or end of a lease term and
> explicitly framed as evidence between two named parties.

Both of the gist row's decisive structures are that sibling's too. Reversing a landed sibling's
signal would be the worse error, and the sibling is right: those documents are a **surveyor's
product**, and its `one_line` names *reliance* — an addressee, a stated purpose, a basis, a
limitation of liability, a PI statement — as the fingerprint. A schedule of condition has all of
that. So the concession is made openly, and the row is re-tested without those two structures.

**What survives, and it is enough:**

1. **The alienation regime.** A consent apparatus governing *who may occupy*: a licence to assign or
   to sublet naming a proposed transferee, an authorised guarantee agreement by the outgoing tenant,
   a landlord's consent conditioned on covenant strength. This is a document family with **no
   counterpart in an opinion document** (it states no opinion and names no addressee entitled to
   rely) and **no counterpart in residential letting** (where occupation is personal and there is
   nothing to assign). It is the strongest single signal this row has and it was under-weighted in
   the gist draft.
2. **The review-and-break machinery.** A memorandum recording a reviewed rent from a review date; a
   break notice and the vacant-possession evidence around it. What makes this a structure rather than
   a date is that it is **derived from an instrument and operates on it** — the memorandum amends the
   rent the lease reserved; the notice exercises a right the lease granted. An opinion document
   cannot do that, and neither can a bill.
3. **The lease-defined recharge proportion.** A service-charge or insurance-rent apportionment for
   **one unit** stated as *the proportion the lease defines*, applied to a landlord's expenditure
   schedule. The proportion's authority is the instrument. This is what separates it from
   `block-management`'s whole-building apportionment schedule, which derives the shares itself.
4. **The security apparatus.** A rent deposit deed with drawdown mechanics, a guarantee, an AGA.
5. **Heads of terms.** A subject-to-contract summary carrying an express non-binding legend — a
   document that exists *because* the instrument does not yet, which no other row on the roster holds.

None of these is a `work_type` value wearing a row's clothes, and the test for that is the one the
schema anchor set for `progress-photos`: *a `work_type` value cannot carry a different detection
method; only a template can.* The identical argument runs here — a value inside the family's default
tree cannot introduce a **derived-from-an-instrument** detection method, because a value has no
recognition rules of its own.

**Verdict on leg 2: passes, on a narrower base than the gist draft claimed.** The two conceded
structures remain in `recognition.deterministic` as detection signals — this row may legitimately
recognise a schedule of condition sitting in a tenancy file — but they are now marked as shared and
the row no longer rests on them.

### Leg 1 — recommended dimensions

The family default is *property → instruction → function, period level only where the situation
cycles.* Two differences, one positive and one negative:

- **The `instruction` level is a TENANCY, and it is not a job.** One shop is let in 2014, surrendered
  in 2019 and re-let in 2021. Three tenancies, one premises, and the papers of each are meaningless
  in the others' company — a 2014 rent review has nothing to do with the 2021 lease. The family's
  `instruction` level assumes a commissioned piece of work with a start and an end; a tenancy is a
  *relationship* with a term, and the level that separates two of them is the term itself.
- **No period level, explicitly.** This is the sharper difference and it is a negative, which is the
  rarer and more useful kind. The two siblings that share this row's folder — `service-charge` and
  `block-management` — both recommend a year level, and correctly: a service-charge year is a *named
  accounting period* that genuinely cycles. This situation does **not** cycle. Its dates are a
  diary — a review in year 5, a break in year 7, an expiry in year 10 — and foldering by year would
  scatter one tenancy across a decade of directories for no gain, producing exactly the *"meaningless
  one-child levels"* the template validator rejects. The `00` sentence that licenses the family's
  document-first order licenses this too: *"putting year first scatters related work across calendar
  folders."*

**Verdict on leg 1: passes**, and the negative is the part worth keeping. `dimension_order` is `[]`
by binding contract — a dimension may only branch on a declared field and this schema declares none —
so all of the above is held as prose in `template.why` for whoever answers NJ-CP-1.

### Leg 3 — privacy

Weakest leg, and the row would stand without it. Stated honestly for that reason.

The schema default's privacy ground is that *the material names a real person's home and who is in
it*. **This row's exposure is a different kind.** Its material is predominantly **commercially
confidential rather than personal**: what a named business pays for its premises, what it owes, what
security it gave, and what liability it faces at expiry. Its characteristic harm is not identifying
a person but **disclosing a live negotiating position** — a rent-review comparable, a dilapidations
claim total, an arrears position. Personal data enters by a narrow and specific door: individual
guarantors, who give personal guarantees in their own names, and arrears correspondence.

That is a genuine difference in kind from the schema default and from `tenancy-management`, whose
default residual is Protected Records *because a named person lives there*. It is not, on its own,
a difference that would earn a node. The setting stays `potentially_sensitive`; the handling class
is P7's and is not assigned here.

**Verdict on leg 3: passes weakly, and is not load-bearing.**

### Overall

**Kept, not refused** — on legs 1 and 2, with leg 3 supporting. The row would still stand if leg 3
were struck out entirely, which is the test of whether the other two are real.

### The dispatch's specific challenge, answered

> *If the only discriminator is that the tenant is a business rather than a person, that is an
> organisation name — never-alone evidence, which cannot activate a row.*

Agreed, and the row does not use it. The occupier's legal form appears nowhere in
`recognition.deterministic`; *a firm, practice, contractor, agency or authority name alone* is in
`never_alone` explicitly, on `00`'s multi-role-token sentence. What the row activates on is the
**covenant regime** — an alienation consent, an upward-only review memorandum, a contracting-out
declaration, an AGA, a lease-defined recharge proportion. Those are **documents that exist**, not
inferences about who the tenant is. A sole trader occupying a lock-up shop under a full commercial
lease fires this row; a limited company renting a flat for a director under an ordinary residential
tenancy does not. That is the correct behaviour and it is the proof the discriminator is not the
organisation name.

---

## The `legal.leases-agreements` seam — the row's defining boundary

`legal.leases-agreements` landed first, at full depth, is a **safety** template, and it owns leases
by name. This row must say what a commercial lease has that it does not, or not exist.

**What that row actually claims**, in its own `one_line`:

> A person or small team's own agreement records: leases, service and employment agreements, and the
> amendments, schedules, signing evidence, renewals and termination records around them. This safety
> template detects and protects an executed-agreement lifecycle.

And its own conjunctive detection shape, from its memo: *party roles presented in the document;
operative terms expressing reciprocal duties or a grant of use; and completed execution or
final-document evidence tied to the same document version.*

**The seam is instrument versus running apparatus**, and it is that row's own formula — the one it
uses against all fifteen of its neighbours. Its phrasing against `finance.household-property`:

> Party recitals, covenants, grant of occupancy, consideration and execution support this agreement
> situation; issuer plus receipt, inventory, inspection, tax or improvement structure supports
> finance.household-property.

Read across, in that row's idiom:

| Evidence | Reading |
|---|---|
| party recitals, a demise, a term, a rent, numbered covenants and an **execution block** — the lease itself, its deed of variation, its licence *as an executed deed*, its deed of surrender | **`legal.leases-agreements`**. `legal` is a safety domain; its protective ordering runs first. |
| the **apparatus that runs the tenancy after grant** — schedule of condition, rent-review memorandum, break notice, alienation consent, per-unit recharge, rent deposit drawdown, dilapidations schedule, lease-event diary | **this row** |
| a premises address, a rent figure, a signature block | **neither.** *"signature block alone counts for neither"* is that row's own phrasing, used four times over, and it is adopted here unchanged. |

**This is not this row's invention — the schema anchor already made the assignment**, in its own
reciprocal-boundaries table, naming the same bytes:

> `legal.leases-agreements` **(landed)** · this schema must not take *the operative clause structure
> of the instrument — recitals, covenants, consideration, execution* · the neighbour must not take
> *the estate-management apparatus around it: rent-review memoranda, schedules of condition,
> dilapidations, apportionments, licences to alter* · shared fixture `Lease Agreement - 18 River
> Court - Signed.pdf`.

This row is the sibling that occupies that assignment for business premises. It does not extend it.

**Consistency with `construction_property.subcontract`**, which settled the identical charge one row
over and reached the same place by the same route: *"What separates them is the same thing
`legal.leases-agreements` uses to separate itself from every one of its other fifteen neighbours:
instrument versus running apparatus."* Its consequence is adopted here verbatim in substance — **a
per-evidence-item mutex, not a file-level winner.** `Lease - Unit 3B - engrossment.pdf` is named on
**both** sides: it carries `also_schema: "legal"` in this row's JSON and routes to **Protected
Records** when inactive. This row reads the dates and the proportions out of it and runs them; the
instrument is the safety row's.

**The debt, stated openly rather than smoothed:** `legal.leases-agreements` does not name
`construction_property` anywhere in its own file — it landed before this family existed. The seam is
therefore **authored from one side only**, in that row's own vocabulary, and **R1c owes the
reciprocal.** `construction_property.construction-project` and `.subcontract` record the identical
debt in identical terms. This is **one debt with three creditors, not three debts**, and the fixture
bytes are named on this side so the reciprocal can be checked rather than asserted.

**Where I do not diverge:** nothing above contradicts a sentence of that row. Its `never_alone` on a
bare execution block, its refusal to conclude formation or validity, and its Protected-first ordering
are all adopted unchanged.

---

## The correction: `construction_property.survey-valuation`

Stated separately because the deepening addendum asks that a reversal be explicit rather than quiet.

**What the gist draft said:** *"The two decisive structures are the schedule of condition … and the
dilapidations schedule … Neither exists anywhere else on the roster."*

**What is true:** `survey-valuation` names both, in one deterministic entry, and owns them as
products of a professional's instruction. Its `one_line` puts *"the schedules of condition and
dilapidations that fix a state as evidence"* in its own scope sentence.

**How the pair is split**, using that row's discriminator rather than a new one:

| Evidence | Reading |
|---|---|
| a labelled addressee block, a stated purpose, a basis or standard, a limitation of liability, a professional signature with a designation and a PI statement | **`survey-valuation`** — a **reliance** document |
| a lease reference, a review or break date, an alienation consent, a lease-defined recharge proportion, a tenancy the file sits inside | **this row** — **tenancy machinery** |
| a room-by-room narrative, numbered photographs, costed remedies, a premises address, a covenant reference | **shared.** Both may hold, on disjoint evidence. |

A terminal dilapidations schedule prepared by a surveyor and sitting in a tenancy file is genuinely
both, and that is not a defect: it is one document performing two functions, which is what
`also_schema` and the per-item mutex exist for.

**What this cost the row:** its two most vivid signals stopped being proof. **What it did not cost:**
the alienation regime, the review-and-break machinery, the recharge proportion, the security
apparatus and heads of terms are untouched by the concession, and none of them appears in
`survey-valuation`.

---

## The commercial/residential seam — `construction_property.tenancy-management`

The gist draft deliberately withheld this edge, on the reasoning that the sibling had not landed and
a one-way edge would prejudge how it drew the residential line. **That was right at the time and is
now obsolete:** the sibling landed, and it routes its commercial fixture here in terms:

> **A commercial lease.** Kept as the collision fixture, routed to
> `construction_property.commercial-lease`.

Its discriminator, which this row **adopts unchanged rather than restating differently**:

> a deposit protection scheme, a right-to-rent check, prescribed information and a residential
> statutory notice support this row; a term of years, rent review provisions, alienation and
> dilapidations obligations between two companies support the commercial row.

One friendly amendment, and it is the dispatch's own point: *between two companies* is the half of
that sentence this row does **not** lean on. The rest of it — term of years, rent review, alienation,
dilapidations — is the whole discriminator, and it is documentary. The occupier's legal form is
corroboration at best and never-alone at worst.

**Reciprocal, both directions:**

| | Must not take |
|---|---|
| **this row** | a residential letting's apparatus: the deposit protection certificate and prescribed information, the safety certificates that co-occur for one address, the statutory notices served on a person living there. `tenancy-management`'s fingerprint is that **co-occurrence**, and no member of it identifies the row alone. |
| **`tenancy-management`** | the alienation regime, the contracting-out declaration, the upward-only review memorandum, the AGA and the terminal dilapidations schedule — none of which has a residential counterpart |

**Privacy reinforces the split rather than crossing it:** that row's default residual is Protected
Records because a named person lives in the property; this row's default exposure is commercial
confidence. Two rows with the same subject and opposite privacy postures are exactly the case
CONNECTION.md §2 contemplates.

**Where it is genuinely uncomfortable, and it is not hidden:** a small mixed-portfolio landlord with
three flats and a shop. One folder, one accounting habit, both regimes. The line is drawn on the
covenant regime anyway, because a line drawn on portfolio scale would need a threshold and
`_CONTRACT` rule 3 forbids inventing one. **NJ-CP-9**, now reciprocated rather than owed.

---

## `business_operations.facilities-workplace` — the collision most likely to fire on a real corpus

Not the legal one. **Most people holding these files are the tenant**, and a tenant organisation's
premises record and its workplace record live in the same folder, on the same drive, named by the
same person.

That row names this one already, and precisely:

> The instrument version of the same confusion. A lease is the property family's; the occupier's
> obligations extracted FROM it into a maintenance and inspection calendar are this row's.

Adopted, and reciprocated with a sharper handle: the discriminator is whether the document **manages
the lease** (review, break, licence, dilapidations, recharge — this row) or **manages the workplace**
(desk allocation, access passes, cleaning rotas, moves, the maintenance calendar). The premises
address is on both and decides nothing. The schema anchor draws the same line one level up:

> `business_operations` · this schema must not take *a desk-booking policy, an office move plan, a
> facilities vendor register* · the neighbour must not take *a fit-out with a contract sum, drawings
> and interim valuations, merely because the occupier commissioned it*.

Note what follows for the extracted obligations calendar: an occupier's maintenance calendar built
*out of* a lease is `facilities-workplace`'s even though its content came from this row's instrument.
Derivation is not ownership.

---

## The collision fixture, both directions

### A file that would wrongly fire this row

**`Schedule of condition - 14 Foundry Row - Fenwick Surveyors.pdf`** — added to the JSON this pass,
because the row previously carried no fixture that failed on *its own* signals.

It satisfies:

- the **schedule-of-condition structure** in full — a dated room-by-room written record
  cross-referenced to numbered photographs;
- a **premises address** in a labelled slot;
- a **document-type word** from this row's own `work_types` list;
- and it sits in a folder full of property paperwork.

**And this row must not fire.** What discriminates it: an **addressee block, a stated purpose and a
limitation of liability** — the reliance structure — and the **complete absence of tenancy
machinery**: no lease reference, no review or break date, no licence, no recharge proportion. It is
`survey-valuation`'s. Where the same schedule sits in a tenancy file against a lease reference, both
rows hold and neither is a file-level winner.

### A file that must not be lost *to* this row

**`Lease Agreement - 18 River Court - Signed.pdf`** — the schema anchor's own named bytes, and the
fixture `legal.leases-agreements` competes for. A lease is the most tempting file in this row's world
and it is **not this row's**: it is an executed instrument, `legal` is a safety domain, and its
protective ordering runs first. This row reads dates and proportions out of it. The same bytes are
named on both sides, per the addendum's requirement, and the JSON's `Lease - Unit 3B - engrossment.pdf`
example says so in its `must_not_conclude`.

Second, for the residential direction: **a deposit protection certificate beside an assured tenancy
agreement.** It has a premises address, a tenancy, a deposit and a statutory flavour, and it is
`tenancy-management`'s in full. This row has no deposit-scheme signal and must not acquire one.

---

## Files considered and rejected

The dispatch's test: a row that only lists what it holds has not been researched.

| File | Why it is **not** this row's evidence |
|---|---|
| `Schedule of condition - 14 Foundry Row - Fenwick Surveyors.pdf` | **The collision fixture.** Reliance structure, no tenancy machinery. `survey-valuation`'s. |
| `Lease Agreement - 18 River Court - Signed.pdf` | The operative instrument. `legal.leases-agreements`, and it protects first. |
| A rates demand and utility accounts for the premises | Real, and in every occupier's folder. `finance.subscriptions-utilities`, whose landed edges already state the service-address discriminator. A service address is not a demise. |
| Fit-out drawings and the building contract behind them | `construction-project` and `drawings-revisions`. The licence to alter *references* the drawing numbers; referencing is not holding, and the sheets are their own files with their own title blocks. |
| A business rates appeal; lease renewal proceedings; a dilapidations claim once issued | A **proceeding** is `legal`'s. The dilapidations schedule is this row's until it becomes a claim in a tribunal, and the JSON's fixture says *"that a claim is a proceeding; it is not, until it is"* |
| A whole-building service-charge budget with an apportionment schedule across every unit | `block-management` and `service-charge`. This row holds the **single unit's** recharge under **its own lease's** proportion. Reciprocated; a service-charge line appears in both and decides neither. |
| Letting particulars, a portal listing, viewing feedback, an offer | `agency-listing`. Material made to **find** an occupier, not to run the tenancy. A rent figure and a premises address count for neither. Reciprocated. |
| A tenant company's desk-booking policy, access-pass register or cleaning rota for the same premises | `business_operations.facilities-workplace`. Manages the workplace, not the lease. |
| An insurance policy schedule for the building | `finance.insurance-corporate`. Labelled Named Insured, Policy Number, Policy Period and coverage tables are its structure; a lease-defined **insurance rent recharge proportion** is this row's. The landed `legal.leases-agreements` states this pair from its side and the reasoning carries over unchanged. |
| A rent payment out of a bank statement | `finance`. A transaction is not a tenancy, and the amount is never-alone on every schema that touches money. |
| A CV of a property manager naming the buildings they ran | `career`. Full vocabulary overlap, zero evidence overlap. |
| A market report on office rents; a professional guidance note on dilapidations | Reading Inbox — *"papers, articles, reports, and saved PDFs that appear to be reading material but have no active research, course, or project association."* These accumulate heavily in exactly this folder. |
| A `.vcf` for the landlord's agent | `00` requires contact data be privacy-protected rather than used to create folder proposals. A file-kind signal at most. |
| A residential AST with a deposit protection certificate | `tenancy-management`. See the seam above. |

---

## Grouping, and the firewall

Five accepted groups, all in the JSON, and the reason they are legitimate is `00`'s own sentence:
*"The documents are content-incoherent but purpose-coherent."* A schedule of condition, a rent-review
memorandum, an AGA and a dilapidations response share no vocabulary, no format and no author. They
share a tenancy.

**The firewall.** The **tenancy schedule / rent roll** is the dangerous member: a table whose rows
are *other premises*, each with dates and rents. It is evidence about the portfolio and **not**
evidence about any premises it names — *"The graph does not automatically copy those missing facts
onto sparse files."* Its `file_example` says so explicitly, and the same rule kills the tempting
inference on `IMG_7743.jpg`: a photograph captured shortly after a lease expiry gets **no** tenancy
fact from that proximity. Proximity in time is not evidence.

**And no group at all is valid.** A single licence to alter with nothing around it is a standalone
record and goes to Independent Records. Most real corpora hold exactly that.

---

## Fields, dimensions and vocabulary

- `fields: []` — a template references its schema and does not copy it; `construction_property`
  declares none (D1 as narrowed, `_CONTRACT` rules 10 and 15, PR-6).
- **`proposed_fields: []`, and this is a deliberate second.** The key this row needs is `property`,
  which the **schema row already proposes** (NJ-CP-1). A tenancy or lease-reference key was
  considered and **not** proposed: the schema row's `instruction` proposal already covers the
  container concept, and minting a second one is exactly the near-duplicate defect D6 exists to
  kill. The dispatch's instruction to second the family's existing proposals rather than mint
  variants is followed literally — this row proposes nothing.
- `dimension_order: []` by binding contract; the recommendation is prose in `template.why`.
- `role_split: []` — landlord/tenant/agent is a genuine role distinction and the sharpest thing about
  this row's `needs_llm` list, but `role_split` joins **canonical field keys** and none exists.
- `work_types[]` carries values only. `dilapidations`, `schedule`, `licence` and `review` are values,
  and the schema anchor names several of them on its no-row list by name.
- **Jurisdiction stays a value, never a key or a level (D4).** This row is jurisdictionally loaded —
  security of tenure, contracting out, quarter days, notice periods and the statutory framing of a
  dilapidations claim all differ by country. `proposed_context_terms` carries the vocabulary as
  *terms*; no notice period, review cycle length or quarter-day date is stated anywhere, per
  `_CONTRACT` rule 3.

---

## NEEDS-JOSEPH

1. **NJ-CP-9 · The commercial/residential line.** Now **reciprocated** with the landed
   `construction_property.tenancy-management` rather than owed. Both sides draw it on the covenant
   regime and its documents. What stays open: the mixed-portfolio landlord whose corpus crosses the
   line inside one folder, and whether a corpus showing both regimes at one address should activate
   both rows or neither. Alternatives: *(a)* activate both and let the per-item mutex sort it — costs
   nothing but produces two proposals for one folder; *(b)* abstain — safe, and loses a real
   situation; *(c)* a scale threshold — forbidden by `_CONTRACT` rule 3.
2. **NJ-CP-CL-1 · The shared schedule-of-condition fingerprint. NEW in this pass.**
   `construction_property.survey-valuation` and this row both name the schedule of condition and the
   dilapidations schedule in `recognition.deterministic`. The split authored here is
   reliance-versus-tenancy-machinery and both rows can hold one document on disjoint evidence. R1c
   should **confirm the split rather than let two rows claim one fingerprint** — the alternative is
   to strike the two structures from this row's detection entirely, which would be defensible and
   would cost the row its ability to recognise a schedule of condition sitting inside a tenancy file
   with nothing else around it.
3. **NJ-CP-CL-2 · Is the lease-event diary a filing situation at all?** A schedule of dates held to
   be *diarised* rather than read may be a P10/P11 concern rather than a row's material, and `00` is
   explicit that calendar is a `SOURCE_TYPE` and not a domain. This row keeps it as a work type and a
   detection structure and claims nothing about diarising. Alternatives: keep it here (current, and
   cheap); move it wholesale to P10/P11 (clean, and loses `Lease events.xlsx`, which is a real file);
   or split the spreadsheet from the `.ics`, which is a format distinction and therefore wrong.
4. **The `legal` reciprocal is owed.** `legal.leases-agreements` does not name `construction_property`
   in its own file. R1c owes the edge on the `legal` side, using
   `Lease Agreement - 18 River Court - Signed.pdf` and `Lease - Unit 3B - engrossment.pdf`. One debt,
   three creditors, shared with `.construction-project` and `.subcontract`.
5. **Inherits NJ-CP-1.** Without a `property` canonical key this row's recommended tree cannot be
   expressed as dimensions at all, and leg 1 of its node test survives only as prose.

---

## What changed in this pass

**Preserved unchanged**, because it was right:

- the central `legal.leases-agreements` argument — instrument versus running apparatus — and the
  decision to state it in that row's own vocabulary;
- the whole `recognition` block's shape, the `never_alone` list, all ten original `file_examples`
  with their `facts_legal`, `must_not_conclude` and residual routing;
- `proposed_fields: []` and the reasoning for it;
- the `no period level` dimension recommendation and `time_first: false`;
- the `business_operations.facilities-workplace` collision as the one most likely to fire on a real
  corpus;
- the six `falls_through_to` residuals and every quotation, all re-verified verbatim this pass.

**Corrected** — a reversal, stated openly:

- the claim that the schedule of condition and the dilapidations schedule exist nowhere else on the
  roster. They exist on `construction_property.survey-valuation`. The detection entry now says so,
  the row's node test no longer rests on them, and the `one_line` names the machinery it does rest on.

**Added:**

- the node test argued leg by leg against the schema anchor's stated default template, with the
  dispatch's organisation-name challenge answered directly;
- three reciprocal `collides_with` edges to landed siblings that already name this id and were owed a
  reply — `tenancy-management`, `survey-valuation`, `construction-project`;
- an ALIENATION deterministic signal, which is the leg the row now stands on and was under-weighted;
- the collision fixture in both directions, with
  `Schedule of condition - 14 Foundry Row - Fenwick Surveyors.pdf` added as a `file_example` that
  satisfies this row's own signals and still must not fire;
- a files-considered-and-rejected table of thirteen tempting false positives;
- reciprocal boundary statements against `legal.leases-agreements`, `survey-valuation`,
  `tenancy-management` and `facilities-workplace`, naming the same fixture bytes on both sides;
- the D4 and `_CONTRACT` rule 3 posture on jurisdiction, which the gist draft did not state;
- two new NEEDS-JOSEPH items and the explicit `legal` reciprocal debt.

**Not padded.** This row has genuinely less field-level material to argue than a launch row, because
it proposes no fields and its schema declares none. Its length comes from having four live
neighbours, one landed safety row, one conceded fingerprint and one reversal to account for.

# business_operations.facilities-workplace — lab notes (template row)

**Depth: J-DEPTH.** Deepened from a gist draft. The gist draft's facts and its JSON key set were
correct and are preserved; what it lacked was the node test argued leg by leg, the rejected files, a
two-directional collision fixture, reciprocal boundaries read against the neighbours' own files, and
`proposed_fields`. Those are the additions. One gist judgement is reversed and one is superseded;
both are named in *What changed in this pass*.

---

## Sources actually used

### Binding
- `planning/00-database-agent-product-design.md` — every quotation below is verbatim and was checked
  with `grep -F` against this file before writing.
- `planning/domains/CONNECTION.md` §2 (node test), §4 (activation, step 2 never-alone), §5
  invariant 2; `_CONTRACT.md` rules 10 and 15; `canonical_fields.json`.
- `planning/overnight/council/DECISION-BRIEF.md` — D1 as narrowed, J-IND. Not re-debated.
- `ROSTER.md` Appendix A line 820: absorbs `ops.facilities-workplace` (ROW). `ops.business-travel`
  folded to `travel.bookings-confirmations`, **not** here.

### The schema anchor, read first and read as binding
`business_operations.research.md` (46KB). Two things in it govern this row and are applied
explicitly below: **the default template stated for the 24 siblings**, and **the never-alone
principle generalised for all 24 siblings**.

### Neighbours read before writing — and not contradicted
- `business_operations.organisational-records.json` — the family's refusal, read first on the
  dispatch's assumption that this row might be heading the same way. It is not; the reason is §"Why
  this row is not `organisational-records`".
- `construction_property.research.md` (43KB) — the landed family anchor. It states this seam itself
  and cedes territory to this row by name. Decisive, and this pass adopts its discriminator.
- `construction_property.commercial-lease.research.md` (38KB) — names this row as *"the collision
  most likely to fire on a real corpus"*, quotes this row's own JSON back, and settles the derived
  obligations calendar in this row's favour.
- `construction_property.block-management.research.md` (43KB) — declines to edge this row, with a
  reason. Reciprocated below rather than overridden.
- `business_operations.it-asset-inventory.research.md` (36KB) — the nearest sibling, which beat the
  same spreadsheet-shape charge. Its routing of an access-badge and keys register **to** this row is
  reciprocated here.

---

## What it is for, and what it holds

The physical workplace as an **administered** thing. Space records and floor plans, desk and
department allocation, asset and plant registers, planned and reactive maintenance, statutory site
checks (fire, electrical, water, lift, gas), access cards, keys and alarm records, workplace services
and their suppliers, moves and fit-outs, site incident and repair logs.

The anchor is a **site and its running record — the occupier's operational view of a building.**

---

## The hostile reading, stated first

The dispatch brings three charges, and each is survivable only if answered on evidence:

(a) **It is `construction_property`'s material seen from the tenant's side, which is a role, not a
structure.** (b) **Its signal is an organisation name plus a document-type word** — the never-alone
failure that refused `organisational-records`. (c) **It is a container so broad — leases, cleaning
contracts, desk plans, access passes — that it is a residual wearing a domain's clothes.**

Charge (c) is partly conceded at once, and the concession is written into the JSON rather than
argued away: **a lease is not this row's**, it is `construction_property`'s and `legal`'s, and this
row's own fixture list carries `Commercial lease - Fleet House - executed.pdf` as a file that must
**not** fire it. A charge sheet that includes an item the row already excludes is answered by
pointing at the exclusion. What remains of (c) — that desk plans, cleaning schedules and access
passes are too miscellaneous to be one node — is answered in leg 1: they are not miscellaneous, they
are four recurring **structures**, and a residual has none.

---

## The node test, argued leg by leg

CONNECTION.md §2: a template row exists only where its **detection signals**, its **recommended
dimensions**, or its **privacy rules** differ from its schema's default. Each leg separately.

### The schema's default template, quoted, because this is what the row must differ from

The anchor states it, and names it *"the paragraph every sibling must differ from"*:

> the **organisational unit or entity** *only where the corpus genuinely spans more than one* →
> the **governance body, project, contract, or account** the material belongs to → the **fiscal
> period** → the **document function**. Not time-first.

And it states the trap:

> **Differing in business function is not automatically a difference**: "procurement",
> "facilities", "risk" and "IT asset" are *values of a function dimension*. What earns those rows
> their node is a distinct **structure** … not the topic word.

So the word *facilities* earns this row nothing at all. Everything rests on leg 1 and leg 3.

### Leg 1 — detection signals. **Passes. This is the strong leg.**

The anchor's rule is not a ban on structures; it is a ban on **unpaired** ones: *"Every detection
signal a sibling writes must pair a **structure** with a **labelled slot**."* This row can name that
pair four times, and none of the four is the default template's governance/period/function shape.

1. **The asset-and-next-due pairing.** A tabular structure whose rows name a fixed plant item — lift,
   boiler, AHU, fire alarm panel — crossed with a service frequency, a last-service date, a next-due
   date and an attending contractor. Neither half qualifies alone: an asset column alone is a parts
   list or an IT register, a next-due column alone is a diary. **Plant identity crossed with a
   forward obligation** is the shape, and `00` licenses reading it — *"Tables matter because resumes,
   forms, applications, invoices, and administrative documents often place their most useful
   information in cells rather than body paragraphs."* This is the most characteristic table in the
   row.
2. **The statutory-check structure.** A premises address in a **labelled** slot, crossed with a test
   date, a next-due or review date, and a **competent-person identification** — an engineer's
   registration number, an assessor's competency statement. The competent-person slot is the half
   that carries the weight: it is what separates a statutory test certificate from every other
   certificate-shaped PDF in a corpus, and no other row in either family has a use for it.
3. **The access structure.** A card, fob, or key register listing **named holders against zones**,
   with issue and return dates; or a door schedule and alarm-code record. Identity crossed with
   spatial permission. `business_operations.it-asset-inventory` — whose own leg 1 rests on
   identity-plus-custody — explicitly routes *"An **access-badge list** or a keys register"* here,
   because its custody slot names a device and this row's names a **door**.
4. **The space-record structure.** A floor or area identifier crossed with an area measure, a use or
   department allocation, and a capacity or desk count. The discriminator against an architectural or
   estate-agency plan is precisely the **desk-and-department allocation**, not the drawing furniture;
   a title block and a revision letter appear on all of them.

None of these appears in the default template, which is built around cycles, controlled documents and
governance bodies. A PPM schedule is not a cycle artefact issued and superseded; it is a **living
document** re-saved in place, and its natural top level is a place, not a period.

**Answering charge (b) directly:** the row's support is not an organisation name plus a document-type
word. Every one of the four signals above pairs a structure with a labelled slot, and the JSON's
`never_alone` list disqualifies the tempting unpaired halves by name — a street address alone,
facilities vocabulary alone, a certificate-shaped PDF alone, a floor-plan-shaped drawing alone, a
gazetteer hit alone. That last one carries the anchor's own read-across: *"A university name alone
should not create a group because Columbia can appear as an authoring school, course provider, target
institution, employer, research venue, or merely a cited organization."*

### Leg 2 — recommended dimensions. **Cannot pass, and does not need to.**

`template.dimension_order` is `[]` and must be. `business_operations` declares **no field rows** (D1
as narrowed, `_CONTRACT` rules 10 and 15, CONNECTION PR-6), and a dimension may only branch on a
field the same entry's schema declares. A dimension naming an undeclared field opens a tree level no
fact could ever fill. **This leg is unavailable to all 24 siblings equally**, so no sibling can pass
or fail on it, and the anchor says so.

What is recorded, as prose, in `template.why`: **site → asset, area, or service → document function**,
with a year only where the corpus really cycles annually. That order is not the default template's,
and the difference is instructive even though it cannot count as a passing leg. A site is a genuine
**location**, not the collector `00`'s validator rejects — the failure named is to *"use an author or
organization merely as a collector"*, and a building is neither. And a next-due certificate is
unintelligible above its asset, which is `00`'s own reason for putting a course above a homework
number. Not time-first: *"For document and record domains, project, function, or subject usually comes
before time because putting year first scatters related work across calendar folders."* The anchor
warns that this family will be tempted to claim `time_first: true` and that **no sibling may**; this
row does not, and would not want to — a five-yearly electrical condition report and an annual gas
check share a site and share no period.

### Leg 3 — privacy rules. **Passes, and it is a genuine difference, not a restatement.**

The family default is commercial confidentiality. This row contains a small, identifiable class that
is **authentication material**, which is a different category with a different rule attached:

> "A scanned passport, tax statement, medical document, authentication key, or account record should
> enter a protected state immediately."

An alarm code, a keysafe location and an out-of-hours keyholder list are keys to a physical building
in the same sense a credential is a key to an account. `00`'s corpus sentence names both credentials
and GPS metadata among what the corpus holds — *"can include identity documents, account statements,
tax records, medical information, legal records, credentials, private correspondence, GPS metadata,
employment materials, and educational records"* — and both reach this row: credentials through the
alarm sheet, GPS through site condition photographs.

Two further facts make the posture strict rather than nominal. First, an access register **names
individuals**, including contractors and visitors who are **not the user** and never consented to
being in the corpus. Second — and this is the operative difference from every other sibling — **the
sensitive members are indistinguishable from the dull ones by filename.** `Site info.docx` is as
likely to be the alarm codes as the parking rules. A row whose sensitive material cannot be
identified without opening it must set the cautious value for the row as a whole, and this one does:
`potentially_sensitive`, with `Protected Records` as the fall-through and *"Protected material should
not be included in cloud-model prompts by default"* governing the model path.

The row assigns only the catalogue value. The handling class is P7's and is not set here.

### Overall

**Kept.** Leg 1 passes strongly and leg 3 passes on a real difference; leg 2 is unavailable to the
whole family. The row is not reversed. **Refusal was seriously considered** — the dispatch was right
to ask — and the reason it fails is that the four structures above have no home anywhere else: the
property family does not want them, `it-asset-inventory` routes two of them here, and the residuals
would scatter a coherent site file across four different bins.

---

## Why this row is not `organisational-records`

The family's refusal was correct and its reasoning is adopted, not resisted. `organisational-records`
failed because its **entire** support was an organisation name plus a document-type word: two
never-alone signals, which cannot combine into an activation however many of them there are.

This row's support is different in kind, not in degree. Take away the organisation name and the
vocabulary from a PPM schedule and what remains — plant items crossed with next-due dates and a
contractor — still identifies the situation. Take the same two away from a "company policy" and
nothing remains at all. That is the whole distinction, and it is the test the anchor asked siblings to
apply: *"If a proposed row cannot name such a pair, it is not a node — it is the schema's default
template, or a residual wearing a domain's clothes."* This row names four pairs.

The corollary is also accepted: **keeping a row to preserve a legacy id is the 574's mistake.** Had
the four structures turned out to belong elsewhere, `ops.facilities-workplace` would have been let go.

---

## Files considered and rejected

The tempting false positives, and what discriminates each.

| File | Why it is **not** this row's evidence |
|---|---|
| `Commercial lease - Fleet House - executed.pdf` | **The primary collision fixture.** Kept in the JSON precisely as a file that must not fire. A lease is an executed instrument; `legal.leases-agreements` holds the operative clause structure and `construction_property` the estate-management apparatus. The discriminator is the tenure relationship, not the address — and the address is on both sides. |
| `Boiler service certificate.pdf` at a residential address | **The household fixture.** Byte-identical to a workplace one. The address is the only clue and it is explicitly **not** decisive; for a home-based business it is genuinely both. Abstention: *"Correct abstention is a successful outcome because the product’s goal is reliable organization, not maximum file movement."* |
| `Service charge budget 2026 - Fleet House.pdf` | Looks like this row: a building, a maintenance programme, contractors, a year. It is `construction_property.block-management`'s or `commercial-lease`'s, because a **service-charge apportionment is a tenure instrument** — it recovers cost from a demise. The gist draft listed *service charge* and *dilapidations* among this row's `proposed_context_terms`; that was wrong and both are removed in this pass. A term that discriminates **for the neighbour** must not sit in this row's context list. |
| `Office fit-out - interim valuation 04.pdf` | A fit-out is a facilities move and a construction project at once. A contract sum, interim valuations, variations and a snagging list are `construction_property.construction-project`'s. The neighbour states this reciprocally: it must not take *"a desk-booking policy, an office move plan, a facilities vendor register"*, and this row must not take *"a fit-out with a contract sum, drawings and interim valuations, merely because the occupier commissioned it."* |
| `Accident book entry - 14 Mar.pdf` | Premises-shaped and person-centred. Safety splits on **who is at risk**: an assessment of the premises is this row's, material identifying an employee is `hr.workplace-health-safety`'s and must be protected before any model path. |
| `Facilities Management Handbook 2025.pdf`, a supplier's brochure | Written to look exactly like the real thing — the anchor's *"real versus exemplar"* problem. Topic will not separate them; *"purpose answers what the file was for"* does. It was for reading, not for running a site. → **Reference Clips**. |
| A utility bill for the premises | Real and in every occupier's folder, and **not this row's**. `finance.subscriptions-utilities` landed first and owns it; its service-address discriminator already covers this, and a service address is not a site record. Dropped by the gist pass; the drop is confirmed. |
| A rates demand | Same reasoning, `finance` side. A statutory charge on occupation is money, not a running record. |
| A car park permit list, a visitor book | **Genuinely this row's**, and named here only to record that they were considered and folded into the access `work_type` rather than given their own fixture. Not a rejection. |
| `Network rack layout - Floor 3.vsdx` | Rooms and floors, so it looks like this row. Subnets, VLANs, hostnames and rack labels are `it-asset-inventory`'s estate-diagram signal. The seam: a **fixed plant item tied to a building** here, a **device, licence, or endpoint identifier** there. Reciprocated. |
| An AGM minute set for the building | `construction_property.block-management`'s, where a leaseholder body meets about one building. This row's occupier has no such body. |

---

## The collision fixture, in both directions

### A file that would wrongly fire this row

`Service charge budget 2026 - Fleet House.pdf`. It carries a building name, a schedule of planned
works, named contractors, a plant list and a year — four of this row's surface features at once, and
its filename contains a term the gist draft had wrongly listed as this row's own context. It is the
neighbour's. **What discriminates it:** an apportionment. A budget that divides cost across demised
units is recovering money under a lease, which is a tenure instrument; this row's equivalent document
is a PPM schedule, which allocates **work to assets** and never allocates **cost to occupiers**. The
same bytes are named on the block-management side as a service-charge budget with a leaseholder body
behind it.

### A file that must not be lost *to* a neighbour

`Access card register.xlsx`. Rows naming individuals against card numbers, zones, issue and return
dates, with contractor and visitor holders. Two neighbours have a plausible claim: `it-asset-inventory`,
because identity-plus-custody is its own leg-1 shape, and `hr`, because it names employees. **Both
decline, and both say so in their own files** — `it-asset-inventory` routes *"An **access-badge list**
or a keys register"* to this row because its custody slot names a device and this row's names a door;
`hr`'s claim is on the person's employment record, not on which doors a contractor may open. If this
row did not exist, the file would go to **Protected Records** as an isolated sensitive spreadsheet, and
the site file it belongs to would lose its most operationally important member. That is the concrete
cost of refusing this row.

---

## Reciprocal boundaries, both directions

Read against each neighbour's own landed file first. Where this pass diverges from a gist judgement,
it says so.

| Neighbour | This row must not take | The neighbour must not take | Shared fixture bytes |
|---|---|---|---|
| `construction_property` (family) | a fit-out with a contract sum, drawings and interim valuations, merely because the occupier commissioned it | a desk-booking policy, an office move plan, a facilities vendor register | a lease of the office; a fit-out contract |
| `construction_property.commercial-lease` | the instrument, its rent review, break, licence, dilapidations and recharge — anything that **manages the lease** | the maintenance and inspection calendar derived **out of** the lease, the desk allocation, the access passes, the cleaning rota — anything that **manages the workplace** | `Commercial lease - Fleet House - executed.pdf`; the premises address, which decides nothing |
| `construction_property.tenancy-management` | the landlord's or agent's management of an occupier | the occupier's own space plan, asset register, maintenance schedule and access records | one address, one inspection report |
| `construction_property.block-management` | a leaseholder body, a service-charge budget, a demised-versus-common-parts framing | a single occupier's own workplace record | `Service charge budget 2026 - Fleet House.pdf` |
| `construction_property.site-health-safety` | the safety record of a **job** with CDM apparatus around it — construction phase plan, F10, principal-designer appointment | the occupier's standing premises regime, with no project around it | a contractor's RAMS, identical on both sides |
| `legal.leases-agreements` | the operative clause structure — recitals, covenants, consideration, execution | a PPM schedule or an access register because a lease obliges the occupier to keep them | the executed lease |
| `hr.workplace-health-safety` | anything identifying an employee — accident report, occupational health record, personal DSE assessment | an assessment of the **premises** | a fire risk assessment naming a fire marshal by name |
| `business_operations.it-asset-inventory` | hostnames, entitlements, device custody, subnet notation | rooms, desks, keys, premises, fixed plant, building plans | a door-access controller, which is an IT device and a facilities control at once |
| `business_operations.contract-administration` | the contract register entry, notice dates, obligation tracking | the operational schedule, the job log, the site record | one cleaning contract |
| `finance.subscriptions-utilities` **(landed)** | utility and rates accounts for the premises | a maintenance schedule because a service address matches | a utility bill for the site |
| `finance.household-property` **(landed)** | a household's own maintenance record of its dwelling | a workplace record because a home address appears | `Boiler service certificate.pdf` |
| `retail_hospitality.store-operations` | a trading, licensing, or guest-facing anchor | opening checks and maintenance logs framed as a generic workplace | a trading premises' cleaning rota |

**One divergence stated openly.** `block-management` declined to edge this row, calling the specific
confusion *"thin"* and a fifth `business_operations`-flavoured edge *"noise"*. This row keeps its edge
in that direction, because the traffic is asymmetric: the service-charge budget is a real and frequent
false positive **on this side**, even if the reverse is rare. An edge that is load-bearing in one
direction is worth carrying, and no contradiction arises — the neighbour's file does not deny the
seam, it declines to spend an edge on it.

**One reversal of a gist judgement.** The gist draft left `construction_property.site-health-safety`
unedged on the grounds that `hr.workplace-health-safety` already carried a who-is-at-risk
discriminator once. That reasoning was wrong: the two edges answer different questions. The `hr` edge
separates **person from premises**; the `site-health-safety` edge separates **a job's safety file from
a standing regime**, and a contractor's method statement for an office lift repair is on the wrong
side of neither test but the right side of only one. The edge is added.

---

## The discriminator, restated — and superseded

The gist draft drew the occupier/owner seam on **TENURE**, and did so unilaterally, filing the fact
that it had done so as NJ-BO-12. `construction_property` has since landed at full depth and draws the
seam itself, one level up, on **INSTRUCTION**:

> An **occupation, not a topic**. Somebody is *instructed* about a property that is not necessarily
> their own: to price it, survey it, design it, build it, approve it, certify it, value it, sell it,
> let it or manage it.

and its own routing table cedes territory to this row **by name**: *"an organisation's occupation of
its own premises as part of running itself"* → `business_operations.facilities-workplace`.

**This pass adopts the neighbour's discriminator and demotes tenure to the practical handle.** The
reason is not deference for its own sake: instruction is the better test because it explains cases
tenure cannot. An owner-occupier has no tenure evidence at all and is still plainly on this side; a
managing agent has tenure evidence and is plainly on the other. Tenure remains the evidence a rule
would actually read — a lease, a rent demand, an apportionment, a dilapidations schedule — because
instruction is often unrecoverable from a single file, and the anchor's own warning applies: the side
*"is frequently unrecoverable from the file. When it is unrecoverable, abstain."*

The JSON's `collides_with` entries for `tenancy-management` and `commercial-lease` are rewritten
accordingly, and NJ-BO-12 is narrowed rather than closed — see below.

---

## `proposed_fields` — two, both seconded, neither minted

`fields: []` by contract. The gist draft proposed **none**, and said so honestly. That abstention was
defensible but is superseded: the dispatch asks rows to second the family's existing proposals with
their own argument, and this row has arguments the schema could not have made for itself.

- **`organization`** — seconded, not proposed anew. This is now the **fourth signature on one
  decision**: the `business_operations` schema row proposes it, `construction_property` seconds it
  with the instruction that it *"should be adjudicated once, there, for both"*, `it-asset-inventory`
  seconds it a third time. R1c must not count this as a competing proposal. Seconded
  `destination_eligible: false`, with a site-specific reason of this row's own: **the level a
  facilities corpus wants above everything is the SITE, not the entity**, so an `organization` level
  here is the vanity level `00` forbids — *"create meaningless one-child levels"*, *"use an author or
  organization merely as a collector"*, and *"A folder should not become a collection point for
  everything produced by the same person or organization."* Seconded ceiling `possible`, with a
  facilities-specific reason it cannot rise: the entity name most reliably present on this row's files
  is the **contractor's or the certifying body's** — the maintenance firm on a PPM export, the
  assessor's practice on a fire risk assessment, the alarm company on a keyholder sheet. A rule
  reading the strongest entity token would name the supplier as the holder, and landlord letterheads
  on recharge paperwork make it worse, because that name belongs to the neighbour family's party.
- **`fiscal_period`** — seconded, and here this row **deliberately diverges from its siblings' ceiling
  and says why rather than smoothing it.** Siblings second `validated`; this row asks for `possible`.
  The reason: the date token most characteristic of this row's files is a **next-due date**, which is
  a forward-looking obligation and not a period the document belongs to. A rule family that read a
  next-due date as a fiscal period would file a February 2026 certificate under 2027. Seconded
  `destination_eligible: true` and explicitly **not first**, for the reason in leg 2 — a certificate is
  unintelligible above the asset it certifies, and a year-first tree scatters one lift's examination
  history across calendar folders.

**Deliberately not proposed:** a `site` or `premises` key, and an `asset` key. The temptation is
enormous — they are the two levels the prose template actually wants — and that is exactly why
minting them on a field-less placeholder would be the 574's mistake performed knowingly. Also not
proposed: `location`, which exists canonically but is the **photos-side capture facet**; asserting it
here would be the field-respelling failure the node test forbids. This preserves the gist draft's
judgement, which was right.

---

## Sparse-file discipline

The strongest grouping reason on this row — *one site over time* — is also its most dangerous, because
a site name is exactly the label a system would be tempted to paint onto every unrelated PDF sharing
an address. `00`: *"The graph does not automatically copy those missing facts onto sparse files."* The
JSON says so in `grouping_reasons`, and the `PPM schedule` fixture's `must_not_conclude` names it
concretely: *a site fact copied onto any other file naming the same address*.

The stop rules apply as written — *"when members carry irreconcilable course, institution, project,
term, or purpose facts"* — and the commonest real instance in this row is **a home address mixed with
a workplace address in one folder**. Two sites' records do not merge.

Three further disciplines, each carried in a fixture rather than asserted here: an archive's members
conclude nothing, because *"the normal scan should never extract archive contents to the filesystem"*;
a download session concludes nothing, because *"A session should never be treated as proof of topic"*;
and a PDF's corporate metadata string concludes nothing, because *"PDF metadata should be treated as
supporting evidence, not as truth"* — a corporate template stamps the same entity on every blank form
it ever generated.

---

## NEEDS-JOSEPH

- **NJ-BO-12 (narrowed, not closed) · the owner-occupier residue.** The occupier/owner seam is now
  reciprocal: `construction_property` states it as instruction and cedes this row's territory by name,
  and this pass adopts that. What the instruction test does not reach is the **owner-occupier**, who is
  uninstructed on both sides and holds both sets of records for one address. Alternatives and costs:
  (i) **abstain** — safe, but a real and coherent site file goes to Review Later; (ii) **co-activate**
  both rows via `also_holds_with` — honest, but produces two rows for one folder, which is the original
  complaint; (iii) **let occupation win where no instruction evidence exists** — simple, but silently
  takes material the property family may want. This row's provisional posture is (i).
- **NJ-BO-13 · the home-office case.** Workplace and household are one folder for a home-based holder,
  and in a personal-file product this may be the majority case rather than an edge. A boiler
  certificate, an alarm code note and a floor plan are identical artifacts in a home. Provisional
  posture is abstention rather than a guess from the address. Whether a home-office situation deserves
  its own recognition is Joseph's call, and it is not answerable from the design docs.
- **NJ-J-IND-4 (carried) · authentication material in a row with no safety flag.** `00` names four
  safety domains and this is not one, yet alarm codes and keyholder lists are squarely inside
  *"authentication key"*. The row compensates with `potentially_sensitive` and a `Protected Records`
  fall-through, which is a catalogue-level mitigation for a handling-level problem. **This is the same
  gap `construction_property` records** for occupier addresses and tenant identities, and the two
  should be resolved together rather than separately.
- **NJ-BO-14 (new) · the `fiscal_period` ceiling divergence.** This row asks `possible` where its
  siblings second `validated`, on the next-due-date argument above. R1c should either accept a
  per-row ceiling or require the family to move together; the cost of the latter is that one of the two
  rows is wrong about its own files.

---

## What changed in this pass

Auditable list, checked against the JSON actually written.

**Preserved unchanged** (the gist draft was right): the anchor sentence and `one_line`'s substance;
all 9 `deterministic`, 7 `needs_llm` and 10 `never_alone` signals; all 16 `work_types`; all 7
`grouping_reasons`; all 10 `file_examples` with their `must_not_conclude` lists; all 7
`falls_through_to` residuals; `template.why`'s prose recommendation and `time_first: false`;
`sensitivity` and `sensitivity_why`; the refusal of a `location` proposal; the drop of utility bills
to `finance.subscriptions-utilities`.

**Added to the JSON:**
- `proposed_fields`: `organization` and `fiscal_period`, both **seconded** with row-specific arguments
  (previously an empty list).
- `collides_with`: two new edges — `legal.leases-agreements` and
  `construction_property.site-health-safety` — taking the count from 9 to 11.
- `proposed_context_terms`: added `keyholder`, `door schedule`, `desk booking`, `next service due`,
  `condition report`.

**Changed in the JSON:**
- `one_line`: the "Gist-level placeholder (J-IND)" clause replaced with the instruction-versus-
  occupation discriminator adopted from `construction_property`.
- `collides_with` signals for `construction_property.tenancy-management` and
  `construction_property.commercial-lease`: rewritten to lead with instruction rather than tenure, and
  to record the reciprocation, including that a maintenance calendar derived out of a lease is this
  row's because **derivation is not ownership**.
- `open_question`: rewritten. Question (1) is narrowed from "confirm or replace the tenure
  discriminator" to the owner-occupier residue, because the neighbour's landed memo settled the rest.
- `proposed_context_terms`: **removed** `service charge` and `dilapidations`. Both are the property
  family's discriminators and had no business sitting in this row's context list.

**Reversed:** the gist draft's decision to leave `construction_property.site-health-safety` unedged.
Its stated reason — that the `hr` edge already carried the discriminator — conflated two different
questions, and the edge is now carried.

**Superseded, with the reason stated:** the tenure discriminator as the *primary* seam (now
instruction, per the neighbour's landed anchor; tenure demoted to the practical handle), and the
`proposed_fields: []` abstention (now two seconded keys).

**Not reversed:** the node test's verdict. The row stands, and the three charges are answered in
*The hostile reading* and in leg 1.

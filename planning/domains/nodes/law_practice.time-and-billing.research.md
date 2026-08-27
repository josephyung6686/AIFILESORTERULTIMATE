# Research memo — `law_practice.time-and-billing`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/law_practice.time-and-billing.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Accepted, narrowly.** The node stands on one structure — a table whose **row grain is a unit of chargeable work or a disbursement**, carrying an exact matter reference beside a timekeeper, a narrative, a duration or unit count and a rate — plus the bill rendered from that structure. It concedes everything else to six named neighbours. It is the row I would refuse first if R1c disagrees with the grain argument, and NJ-TB-1 records how to reverse it cheaply.

`fields: []`, `dimension_order: []`, `also_holds_with: []`, `role_split: []`. One `proposed_fields` entry, and it is a **reuse** of a proposal the schema already made, not a mint.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from `make_prompt.py law_practice.time-and-billing`.
- `planning/domains/nodes/law_practice.json` — the schema anchor, read for `template`, `recognition`, `work_types`, `grouping_reasons`, `file_kinds`, `falls_through_to`, `sensitivity_why`, and its `fiscal_period` proposal.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, read whole, for depth calibration.
- Landed neighbours that had already argued a boundary against this id, found with one grep: `law_practice.engagement-terms.json` (refused), `law_practice.pro-bono.json`, `law_practice.deadlines-diary.json`, `construction_property.timesheet.json` (refused).
- `planning/domains/roster.json` — every edge id programmatically confirmed present.
- `planning/00-database-agent-product-design.md` — reached only by `grep -c -F` on each candidate span. Every quotation in the JSON was verified verbatim before use.

**One quotation was rejected during verification.** The sentence *"A visible client or matter label can itself disclose the existence and subject of a representation."* returns **zero** hits in `00`. It is the landed `legal.practice-matter-file` row's own prose (whose actual wording is *"A visible client or matter branch can itself disclose that a representation exists"*), and the schema anchor cites it as a neighbour's sentence rather than a design span. This memo and the JSON therefore carry the naming rule as **inference**, never as a `00` quote. Flagging it because it is the family's most-repeated sentence and is one careless copy away from becoming a fabricated design cite.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength first, because it is nearly good enough to win.

1. **It is a document type.** "Bill", "invoice", "fee note", "timesheet", "disbursement" are document-type words, which the schema strikes never-alone in terms, and which killed `law_practice.engagement-terms` as an independent fourth ground.
2. **It is one verbatim value in its own schema's `work_types` enum** — *"time record, disbursement record, matter budget and bill narrative"*. The dispatch is explicit that work types are values and do not become nodes.
3. **It is a lifecycle stage.** Billing is the money stage of a matter, exactly as engagement is its opening stage — and the opening stage was refused for being a stage.
4. **It is a duplicate of its own schema's default template.** The schema's fourth deterministic entry *is* "A TIME-AND-DISBURSEMENT structure", described in the same column-set terms this row would use. A template whose signal is already written on its schema has no signal of its own — the precise reasoning that refused `engagement-terms`.
5. **It is a medium, not a world.** Every profession that sells time keeps a timesheet. `construction_property.timesheet` was **refused** on that ground, and its own file example records the shared fixture as being kept "to show how generic the row's only candidate signal was". If a construction timesheet is not a node, a legal one is a construction timesheet with a different word in the project column.
6. **It is a duplicate of a neighbour.** `finance.small-business-bookkeeping` already owns invoices, receivables and ledgers; `business_operations` already owns activity reporting.

## Defeating the charge — the node test, three legs

### Leg 1 — detection signals differ from the schema default

This is the leg that carries the row, and it turns on a fact about the schema's default that is easy to miss.

The `law_practice` default requires **both** legs of a two-part precondition: *(i)* an exact matter reference **repeated across two or more artefacts**, and *(ii)* **at least one artefact whose own labelled slots separate a practitioner or firm role from a client role**.

A firm-wide time export satisfies **neither**. It carries no artefact separating a practitioner role from a client role — a *timekeeper* column is an internal role, not a client-facing pair — and it needs no second artefact, because its own column set carries the matter reference in a column rather than as a repeated string. This row therefore fires on **one file, from its column set alone**, where the schema default cannot fire at all. That is not a variation on the default; it is the complement of it.

This also disposes of charge 4, and disposes of it *symmetrically* with the `engagement-terms` refusal. That row was refused because its artefact **is** the schema's precondition (leg ii in the flesh). This row survives because its artefact is the one on which the precondition **fails**. The refused row makes the point for me from its own side: its refusal reason lists the templates that survive as "a SEPARATE structure the precondition does not already describe", and the list it gives begins *"an intake-and-conflicts form, a matter-opening record, **a time-and-disbursement column set**…"*. A landed neighbour, written to refuse itself, certifies this id by name.

Against charges 1, 2 and 5, the schema's own **deletion test** is the instrument: delete every entity name and every document-type word and see whether structure survives. Applied to `Bill 3 - June 2026.pdf`, nothing survives — which is why the *word* bill is struck never-alone in this row's recognition. Applied to `WIP and unbilled time - all matters - July 2026.xlsx`, what survives is a header row: *Matter Ref | Fee Earner | Date | Narrative | Units | Rate | Value*. That is structure, and it is what the row is founded on. Compare `engagement-terms`, where the same test left "a professional-services agreement" — a shape belonging to another world entirely.

Charge 5 is answered by the discriminator being a **triple**, not the hours column: matter reference **plus** unit-priced work **plus** a recoverable-disbursement schedule. A consultant's invoice has the first two shapes (a project code and hours) and never the third; a construction timesheet has only hours. And the schema states the seam itself: *"an issuer-and-billed-to invoice structure without it is finance's on finance's own evidence, and a timesheet with a project column is business_operations'."*

### Leg 2 — recommended dimensions differ from the schema default

Both orders are empty under PR-6 and D1's deferral, so this leg has to be argued on the schema's **prose recommendation**, which is the paragraph every one of the 36 templates is required to differ from: client (only where approved) → **matter** → function → period.

This row differs at the **matter level, which is the schema's anchor level**. Its characteristic artefact is **matter-plural**. A firm-wide WIP or time export belongs to no single matter, so the matter dimension is not merely disclosive here — it is *inapplicable to the container*. Filing it under one matter would be false; filing it under all of them would copy a fact onto a file that does not carry it.

The recommendation therefore forks, and the fork is the difference:

- **matter-singular artefact** (a bill, a disbursement ledger, a fee note) — the schema's order stands unchanged;
- **matter-plural artefact** (a time export, a WIP schedule) — the matter level drops out, leaving function then **period**, with period doing the work the matter cannot.

That is the closest anything in this family comes to a period-led level, and it is deliberately **not** `time_first`. `00`'s rule holds — *"For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."* — and the period rises here only because the project level is *absent*, not because this world is capture-based. The schema forbids siblings from claiming time-first; that prohibition is respected in letter and in substance.

Two further constraints are inherited and one is added. The client level stays ineligible, doubly so here because a bill's billed-to block is an unusually tempting collector and `00` forbids exactly that — *"use an author or organization merely as a collector"* — and warns of *"create meaningless one-child levels"*. **Added:** a **payee** may never be a folder level. The disbursement ledger's payee column lists counsel, experts and agents, and those are frequently the same people who appear as witnesses in the same matter, so the family's named-third-party rule extends to a column the schema never had occasion to consider.

### Leg 3 — privacy rules differ from the schema default

`potentially_sensitive` is the ceiling and the schema already holds it, so a template that merely restates the schema's argument fails this leg (that is how `engagement-terms` failed it). This row extends the argument in two directions.

**The narrative column.** A time entry's narrative is a per-line prose description of what was done for a named client. It is the highest disclosure density per byte in the family: a single monthly export discloses the *subject* of every live representation at once, including matters the user will never open. Critically, it sits in exactly the cells `00`'s spreadsheet path otherwise licenses reading — *"Spreadsheets such as XLSX, XLS, CSV, TSV, ODS, and Numbers exports should yield workbook or file metadata, sheet names, column headers, visible cell values, table-like regions, formulas only when useful, and dates or identifiers from labeled cells"*. This row therefore states a restriction the default does not need: **column headers establish the structure and the narrative cells are not needed to establish it**, so they are not excerpted, summarised or placed in a prompt for activation purposes. `law_practice.deadlines-diary` reached the same conclusion independently from its side, listing "that the narrative column is safe to summarise" among its `must_not_conclude` because "it describes clients' affairs in prose". Two rows arriving at the same restriction from different fixtures is the best evidence available that it is real.

**Matter-plurality as bulk.** The schema reserves its bulk argument for the privilege log. This row generalises it: a matter-reference column beside a client column *is a client list*, and a client list of a criminal, family, insolvency or immigration practice discloses each person's situation before a narrative is read — and unlike a privilege log, this file is regenerated monthly.

**One gap that widens rather than narrows.** The schema notes that `legal` — a safety domain, whose protection runs first under *"Finance, identity, medical, and legal material should be implemented first as safety domains, meaning the system detects and protects them before any cloud or automated placement decision is allowed."* — usually co-activates and supplies protective ordering anyway. On this row's characteristic file it does **not**: a time export has no caption, no bound party pair and no execution block, so none of `legal`'s signals fire. The schema's residual concern is this row's ordinary case.

All three legs differ. The node stands.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`Invoice INV-2026-0412 - Meridian Consulting - hours and rate.pdf`** — issuer, billed-to, hours, rate, total, professional issuer. Rejected: an engagement or project code is not a matter reference, and there is no recoverable-disbursement schedule. This is the generic billing medium `construction_property.timesheet` was refused for.
- **`Fee earner utilisation and realisation - FY2026.xlsx`** — hours and rates in a legal practice's workbook. Rejected on **row grain**: the rows are people-per-period, not matters. When aggregation passes the matter, the artefact is the practice running itself as a business.
- **`Matter report - all live matters - July 2026.xlsx`** — carries WIP columns this row would recognise. Rejected **whole**: the grain is one row per matter with a key-date column, which is `law_practice.deadlines-diary`'s, and that row has already ruled the file cannot be carved. This row takes no slice of it, money columns included.
- **`Claim for costs - CIV CLAIM1 - assessed with reductions.pdf`** — a rate-by-duration table with a matter reference, i.e. every structural signal this row names. Rejected: the payer is a body that is not a party, the rates were scheme-set, and there is an assessment outcome the practice did not control. `law_practice.pro-bono`'s.
- **`Conditional Fee Agreement - no win no fee - executed.pdf`** — the most seductive fee-basis document in the world. Rejected twice over: a fee basis is a *value*, and a bound party pair plus an execution block is `legal`'s signal on a safety domain.
- **The firm's own accounts payable** — rent, stationery, software, professional indemnity premium, practising certificate fee. Rejected: no matter reference, so `finance.small-business-bookkeeping`'s on finance's own evidence. This is the largest volume of invoices any practice holds and none of it is this row's.
- **A bank statement for the office or client account** — rejected: an institution-and-account header is finance's structure. Only a *firm-internal* client-account ledger extract carrying a matter reference is admitted, and only as a bill-pack member.
- **`RE Bill 3 - 41127-0006 - query on disbursements.eml`** — rejected as a message: `law_practice.matter-correspondence`'s. Only the attachment is this row's.
- **A billing-system database or a live practice-management connector** — rejected as not being one file node. A bounded export with a readable manifest is represented; live-system ingestion is a later connector and security decision, exactly as `legal.practice-matter-file` held.
- **`Time entries 2026-07-14.csv`** with no matter column — rejected as an activation, kept as the `HW 3` case: `group_without_copying_facts: true`. It may join a matter neighbourhood in P9 without this template firing, and no matter fact is copied onto it from a sibling export in the same folder.
- **A court fee receipt on its own** — rejected: an isolated transactional document with no matter anchor, routed to Receipts and Confirmations, whose `00` sentence names *"isolated invoices"* first.

## The collision fixture

**`Ellis and Co - invoice for my divorce - March.pdf`** — a bill the **holder received as a client** of some other practice.

It is the sharpest collision in this row because it is not merely similar; it is **structurally identical**. Issuing practice block, billed-to block, an exact matter reference, a period, a per-item work narrative, an itemised disbursement schedule, a tax line, a total. Every deterministic signal this row declares is fully present.

The only discriminator is the **billed-to role**: holder as client → `legal.personal-legal-matters` (with `finance` on its own slots); holder's practice as issuer → this row. Nothing else separates them, which is why "which side the money is flowing" sits in `needs_llm` rather than `deterministic`, and why the unresolved answer is **Review Later** rather than a guess toward either side. The `engagement-terms` refusal made the same observation about matter references generally: the reference "is allocated by SOME firm; whose it is remains open".

A second, weaker collision is kept for the generic-medium charge: `Invoice INV-2026-0412 - Meridian Consulting - hours and rate.pdf`, discriminated by matter reference versus project code plus the absence of a disbursement schedule.

## Reciprocal boundaries

Seven, each naming the **same fixture on both sides**. All seven are written as objects with `domain`, `signal` and `provenance` — the bare-id defect is not recreated here.

| Neighbour | Shared fixture | This row owns | Neighbour owns | Discriminator |
|---|---|---|---|---|
| `finance.small-business-bookkeeping` | `41127-0006 - Bill 3 - June 2026.pdf` | matter-anchored work grain + disbursement schedule | issuer, billed-to, invoice number, tax, total, receivable | the matter-reference column |
| `law_practice.deadlines-diary` | `Matter report - all live matters - July 2026.xlsx` | tables whose grain is a unit of work | tables whose grain is one matter + key date | first column's **grain**, not which columns exist |
| `law_practice.pro-bono` | `Claim for costs - CIV CLAIM1 - assessed.pdf` | payer is the client, rates agreed | payer is a non-party body, rates scheme-set, assessed | payer role + rate provenance |
| `legal.personal-legal-matters` | `Ellis and Co - invoice for my divorce.pdf` | bill the practice **issued** | byte-identical bill the holder **received** | billed-to role, and nothing else |
| `law_practice.matter-correspondence` | `RE Bill 3 - 41127-0006.eml` + attachment | the attached artefact's column set | the message and the exchange of roles | work-grain structure vs named-role exchange |
| `business_operations.organisational-records` | `Fee earner utilisation - FY2026.xlsx` | tables whose rows are matters | rows that are people, teams, periods, practice areas | where the matter reference stops being a column |
| `career.consulting-client-engagement` | `Invoice INV-2026-0412 - Meridian.pdf` | matter reference + disbursement schedule | project code + milestones + acceptance | matter reference vs project code |

Three of these were **already written from the other side** before this row existed — `pro-bono` on the costs claim, `deadlines-diary` on the uncarvable export, `engagement-terms` on the fee seam and the costs-estimate workbook. This row adopts each of their formulations verbatim in substance rather than restating them differently, so R1c has nothing to reconcile.

## Neighbours considered that did not get an edge

- **`legal` (schema).** Not a collision. The whole family concedes to it, and this row's *characteristic* file is precisely one on which its signals do not fire (no caption, no bound party pair, no execution block). Where a bill-pack member *is* an executed instrument, `legal`'s safety ordering runs first as a matter of course. Recorded in `sensitivity_why`, not edged.
- **`law_practice.client-intake`** — a means or source-of-funds pack is about *whether* a client can pay, not about work recorded and charged. No shared fixture.
- **`law_practice.precedent-bank`** — a blank fee schedule with bracketed placeholders is its inverse-recognition signal and has no client, matter or third party in it. No shared fixture.
- **`finance.tax-filings`, `finance.receipts-expenses`, `hr`** — reachable only through the *practice's own* books, which this row has already conceded whole to `finance.small-business-bookkeeping` and `business_operations.organisational-records`. Adding them would multiply the same seam.
- **`construction_property.timesheet`** — refused, so there is nothing to edge; its argument is answered in the charge instead.

## `proposed_fields` justification

One entry, `fiscal_period`, and it is a **reuse**. The schema anchor's own proposal says in terms that it was *"Raised only so that the time-and-billing template author reuses it rather than minting `billing_period`."* This row complies exactly: it mints nothing — no `billing_period`, no `bill_number`, no `matter_id`, no `timekeeper`, no `rate`, no `units`, no `disbursement_type`, no payer or funder key. `capture_year` is wrong by role (nothing here is capture-based) and `tax_year` is finance's statutory year on the holder's own return. Under PR-6 and D1's deferral no field row and no dimension is written from it; R1c owns whether the key exists at all.

## NEEDS-JOSEPH

- **NJ-TB-1 — the existence question.** Answered *yes* on the narrow row-grain ground above, and recorded so it can be reversed cheaply. If R1c judges that a matter reference is merely a **value in the project slot** of a universal billing structure — the judgement that refused `construction_property.timesheet` — the correct outcome is **refusal**, and the coverage routes to the six neighbours in the table plus Protected Records, Receipts and Confirmations and Review Later. *Alternatives:* keep as accepted on the grain argument; refuse and route; or narrow further to the rendered bill alone, which this memo opposes because the bill is the *derived* artefact and the export is the primary one.
- **NJ-TB-2 — the coactivation that could not be written.** A rendered bill genuinely carries both schemas: `law_practice` on its matter-anchored work grain, `finance` on its issuer, billed-to, tax and total slots. CONNECTION §5 makes `also_holds_with` **schema ↔ schema only**, and this row is a template, so the intent is recorded here rather than edged. *Alternatives:* author `law_practice` ↔ `finance` at schema level, with the seam being that neither schema's facts may be copied onto the other's slots; leave it to per-fixture `also_schema` as done here; or rule the bill finance's outright — which this memo opposes, because it would strip the matter-anchored narrative of the family's naming and prompt restrictions.
- **NJ-TB-3 — the narrative-cell restriction's scope.** This row asserts that `00`'s general licence to read *visible cell values* is **suspended for one named column**, because that column is not needed for activation. The principle reaches well past this family — a diagnosis column, a complainant column, a salary column, a free-text incident column. *Alternatives:* ratify it product-wide as a column-level minimisation rule; keep it local to this row as a template-level privacy rule; or reject it and rely on the sensitivity posture alone, which leaves narrative text eligible for prompts. It is the same shape as `law_practice.pro-bono`'s NJ-PB-3 (an *attribute* of a third party being as unsafe in a path as their name) and the two should be decided together.
- **NJ-TB-4 — the aggregation seam, raised jointly.** Where a matter-anchored table becomes an organisational return is the same line `pro-bono` raised as NJ-PB-4. This row draws it identically — *are the rows matters, or are they people, periods and programmes?* — and asks R1c to confirm it reciprocally with `business_operations.organisational-records` rather than leaving both sides to claim the same workbook.

## Cross-row recommendations for R1c (no neighbour file was touched)

1. `law_practice.deadlines-diary` and this row now state the uncarvable-export seam in compatible terms; R1c may wish to add the reciprocal `collides_with` object on that row, since it currently argues the seam in a `must_not_conclude` rather than as an edge.
2. `law_practice.pro-bono`'s NJ-PB-4 and this row's NJ-TB-4 are the same question; settle once.
3. The family's naming rule should gain a **payee** clause (counsel, experts and agents on a disbursement ledger are frequently witnesses in the same matter). That is a schema-level amendment and this row did not make it.
4. The sentence *"A visible client or matter label can itself disclose the existence and subject of a representation."* is not in `00`. Any row citing it as `design` should be corrected to `inference`.

## Self-verification

- `python3 -m json.tool` — **passes**.
- Key set matches landed siblings `law_practice.deadlines-diary` and `law_practice.pro-bono` exactly (27 keys, including `proposed_context_terms`) — checked programmatically.
- Every edge id checked against `roster.json` by set membership: all present.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (`spreadsheet`, `text_document`, `archive`, `image`, `opaque_binary`).
- Every quotation `grep -c -F`-verified in `00` before use; one candidate returned zero hits and was demoted to inference (see Sources).
- No threshold numbers, no handling classes, no `is_safety_domain`, no folder path written as a fact.
- Twelve file examples: labelled form, unlabelled prose, spreadsheet, OCR/screenshot, archive, encrypted binary, email-adjacent, a sparse `HW 3` case, two collision fixtures, two neighbour-owned aggregates.
- `also_holds_with` empty (template; CONNECTION §5) with the intent recorded as NJ-TB-2. `role_split` empty (fieldless schema).
- Files written: exactly the two assigned. No neighbour node, roster, canonical-fields, `check.py`, `src/` or SPEC file was modified.

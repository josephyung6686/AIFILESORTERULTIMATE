# Research memo — `law_practice.conveyancing`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/law_practice.conveyancing.json`
Roster row: template on the fieldless `law_practice` schema, `parent_id: null`, `launch: placeholder`

## Result

**Node accepted**, on a narrower ground than the roster row's name suggests. It is not accepted as
"the property practice area." It is accepted because a conveyance is the one situation in this
schema whose organising anchor is **a registered parcel of land rather than a matter reference**,
and because that difference forces three consequences the schema's default template does not
produce: a substituted first detection leg, a different parent dimension, and a location-shaped
privacy rule.

## The charge — the strongest case that this row should not exist

Stated in full before anything was written, because the assignment is right that this is the
highest-value part of the work.

1. **It is a practice-area label, and a label is never-alone.** The `law_practice` anchor says so
   itself: activation may not come from "a legal-services label" or "a legal-vocabulary word."
   *Conveyancing* is exactly the kind of word a firm puts on a services page. If the row's only
   claim were "these matters are about houses," it would be a `work_type` **value** on a matter,
   not a node — and the schema already carries the value: its `work_types[]` includes
   *"transaction document set, due-diligence report, data-room index and completion or closing
   record"* and *"regulatory or registry submission made on a client's behalf."* A conveyance is
   both of those with land as the asset.
2. **It duplicates `law_practice.transactional-deal`.** Instruction → diligence → drafts →
   negotiation → conditions → completion date → closing set → post-completion filings. That is one
   arc, and swapping shares for a freehold is a subject change, not a structural one.
3. **It duplicates `construction_property.sale-purchase`**, which already holds property
   transactions, and the evidence is byte-identical on both sides.
4. **The interesting documents belong to `legal` anyway.** The contract, the transfer, the charge,
   the deed — all have `legal`'s bound-party-pair-plus-execution-block shape, and `legal` is a
   safety domain whose protection runs first. Strip those out and what is allegedly left is
   correspondence, which is `law_practice.matter-correspondence`'s.
5. **It could be a lifecycle stage.** "Completion" is a stage of a transaction, and a row defined by
   a stage is not a node.

Charges 1, 2 and 5 are defeated by one finding; charges 3 and 4 are defeated by a second. Both are
argued below and both are carried into the JSON as reciprocal boundaries rather than asserted here.

### Why the charge fails — the finding

**The characteristic files of a conveyance carry no matter reference and no client-role slot at all,
and the schema's default template cannot see them.**

The `law_practice` default requires *both* legs: an exact matter reference repeated across artefacts,
**and** at least one artefact whose own labelled slots separate a practitioner or firm role from a
client role. Now look at what actually arrives in a conveyancing file:

- an **official copy of the register** — issued by a registry, keyed to a title number, with a
  property part, a proprietorship part and a charges part. No client. No matter reference. No
  parties bound to each other. No execution block.
- a **local land charges result and a standard local-authority enquiries return** — issued by a
  council, addressed to whoever paid the fee, keyed to an address, answers against a fixed numbered
  schedule.
- a **drainage and water report**, an **environmental screen**, a **coal or mining report** — three
  more issuers, same parcel, same absence.
- a **property information form** and a **fittings and contents schedule** — numbered questions with
  a seller signing as *informant*, not as covenantor.

Four different bodies, one parcel, and the schema's default fires on none of them. That is not a
subject variation on the default; it is a class of evidence the default is structurally blind to.
The row's job is to see it, and the way it sees it is the **parcel-anchor substitution**: an exact
registry or parcel reference repeated across artefacts **issued by different bodies**, with the
practitioner/client role leg satisfied somewhere in the corpus rather than on the file itself.

That is a real, statable difference in detection signals — leg one of the node test — and it is not
available to any other row on this schema, because no other `law_practice` sibling has third-party
issuers returning documents keyed to a shared non-party identifier.

The second finding, which defeats charges 3 and 4: the artefacts above are also **the negation of
`legal`'s signal**. A `Draft TR1 transfer` with its execution panels *blank* is the clearest case —
the same bytes, dated and signed, leave this row for `legal`. And against
`construction_property.sale-purchase`, the discriminator is not the document type at all but the
presence of practitioner apparatus. Both seams are carried as `collides_with` with the same fixture
named on both sides.

Charge 5 falls with the rest: "completion" is indeed a stage, which is why `time_first` is false and
why the completion date — the single sharpest date in the roster — is explicitly **refused** as a
first dimension in the template's `why`.

## Node test, three legs

**Leg 1 — detection signals differ from the schema's default.** Argued above. The default's two-leg
requirement under-fires on the search pack, the register extract, the enquiry form and the
registration application; this row substitutes a parcel anchor across different issuers. It also
adds one signal nothing else in the roster has: an **apportionment split at a named completion
date**. A generic invoice has an issuer and a billed-to; a completion statement has a date-split and
a balance to complete on. That is a structure, not a vocabulary.

**Leg 2 — the recommended dimensions differ.** The schema's default prose is *client → matter →
document function → period*, with the client level seeded ineligible. This row's prose is *parcel →
transaction → function → period*, and the argument is 00's own parent rule — "A work type such as
Homework 3 is meaningful only after the course is known." Replies to enquiries, a requisition and a
discharge undertaking are meaningless without the **land** they concern; they are perfectly
intelligible without knowing the client. The **linked sale and purchase** proves it from the other
side: one client, one completion date, *two* parcels and two matter references, and a client-first
order would fuse two transactions that must stay separate. `dimension_order` remains `[]` by
contract (PR-6, no declared field), so the difference is carried as prose exactly where the schema
told the 36 siblings to differ from it.

**Leg 3 — the privacy rules differ.** The schema's argument is a third party who cannot consent.
True here, but the shape is different in four ways, set out in `sensitivity_why`: this is the only
row in the family whose central identifier is a **physical dwelling address** (locating, not merely
identifying); a single completion statement discloses price, deposit, advance, redemption figure and
balance in one place; source-of-funds work drags in a **gifted-deposit donor** who is not the
client, not a party and has no relationship with the holder; and existence discloses a **life
event** — a redemption figure beside a sale file implies a move, a separation, a probate or a
repossession. The operative new rule is that a **property address may never be a folder level**,
where the schema only forbade client, matter and third-party names.

Three legs, three differences. The node stands.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence.

| Considered | Why it is not this row's |
|---|---|
| **`Conveyancing - a practical guide - 4th edition.pdf`** | Carries every context term this row lists, plus specimen forms. No parcel, no client, no ordering reference. **Context terms are not evidence.** Reading Inbox. Kept as a fixture. |
| **`Report on Title - Project Harbour property portfolio.pdf`** | The declared collision fixture. Identical phrase, real title numbers. Portfolio schedule, deal codename, corporate addressee, cross-references to a disclosure letter. `law_practice.due-diligence` / `law_practice.transactional-deal`. Kept as a fixture. |
| **`Completion Statement - 14 Oakfield Road - please check.pdf`** | The role-fork fixture. Same apportionment, same figures, holder as addressee, no matter apparatus. `construction_property.sale-purchase`. Kept as a fixture, and named on both sides of that edge. |
| **An executed and dated transfer, contract or charge** | Bound party pair plus execution block — `legal`'s on `legal`'s own evidence, and `legal` is a safety domain whose protection runs first. This row keeps the *unexecuted* draft; `version_family` carries continuity across the seam. |
| **A RICS home survey or a lender's valuation report** | Arrives inside every purchase folder. Its authority is measurement or opinion, its addressee is a buyer or a lender as a professional deliverable. `construction_property.survey-valuation`. The **title plan** is this row's; the measured survey never is. Reciprocal to `construction_property.site-survey`'s own routing (below). |
| **An energy certificate, a building-regulation completion certificate, a gas-safety record, a guarantee** | All arrive as *copies inside an enquiry pack*. They keep their own homes (`construction_property.compliance-certificate` and neighbours). Arrival in a folder is not evidence, and this is the "arrived-copy problem" in `needs_llm`. |
| **An estate agent's memorandum of sale or brochure** | The agent's own artefact and the transaction's trigger, not its apparatus. `construction_property.agency-listing`, which has already recorded that the conveyance is `sale-purchase`'s seam and declined a second edge here. Not re-litigated. |
| **A mortgage offer or annual mortgage statement** | Issuer-and-borrower structure, no parcel apparatus. `finance.loans-mortgage`. Only the lender's *instructions to the firm*, the *certificate of title* and the *discharge undertaking* are this row's. |
| **A blank TR1 or a firm's standard contract precedent with every slot empty** | No client, no parcel, no third party — the one artefact class in this family that exposes nobody. `law_practice.precedent-bank`, and the schema already routes the precedent bank to Reading Inbox. |
| **A homeowner's £3 register download, checking their own boundary** | Byte-identical to this row's register extract, with no firm and no matter around it. `finance.household-property` or `construction_property.sale-purchase`. This is why "a bare registry-shaped token" is on `never_alone`. |
| **A commercial lease under negotiation** | `construction_property.commercial-lease` / `legal.leases-agreements`. A grant of a lease *can* be conveyancing work, but the row does not claim it on the lease document alone — it claims it only when the parcel-anchor and registration apparatus appear. |
| **A case-management system export, a practice-system database** | A source system, not a file node — the schema's rejection, unchanged. |
| **A folder named `~/Documents/14 Oakfield Road/`** | A filing habit. Treating it as evidence would activate this row on the holder's own home, which is the exact under-firing failure the role fork exists to prevent. On `never_alone`. |

## Reciprocal boundaries

Every edge in the JSON names the same fixture on both sides. Summarised:

- **`legal`** ↔ this row. `Draft TR1 transfer - v4 marked up.docx`: blank execution panels → this
  row; dated and signed → `legal`, whose safety protection runs first. Neither claims the other's
  state; `version_family` spans the seam.
- **`construction_property.sale-purchase`** ↔ this row. `Completion Statement - 14 Oakfield Road`:
  inside a client ledger under a matter reference → this row; incoming attachment to the holder with
  no apparatus → the neighbour. Discriminator is apparatus, never document type and never address.
- **`law_practice.transactional-deal`** ↔ this row. `Report on Title`: one parcel, third-party
  returns, apportionment, registry application → this row; deal codename, entity pair, CP checklist,
  disclosure letter, property as a diligence *chapter* → the neighbour. A corporate acquisition that
  owns freeholds is a deal that owns land; a residential purchase by a company is a conveyance with
  a corporate buyer. **R1c owes the reciprocal.**
- **`law_practice.estates-administration`** ↔ this row. `AP1 application and title information
  document`: grant of representation, estate account, asset schedule → the neighbour; sale contract,
  other side's practitioner, deposit, chain → this row. Where a personal representative sells, both
  are right — carried as NJ-LPC-3.
- **`finance.loans-mortgage`** ↔ this row. A redemption statement: the holder's own borrowing record
  → the neighbour; a line item a practitioner is redeeming on completion under a matter reference →
  this row. `finance` is a safety schema; its ordering runs first.
- **`construction_property.survey-valuation`** ↔ this row, and this one is **owed** rather than
  volunteered. `construction_property.site-survey.research.md` already argued against this id from
  its side: *"A title plan is a **legal boundary record**, not a measured survey: no datum, no
  levels, no accuracy statement, and its authority is registration rather than measurement.
  `law_practice.conveyancing` / `construction_property.sale-purchase`."* The reciprocal is now
  authored here on the same fixture — a plan sheet of one parcel: registry furniture and an entry
  reference → this row; datum, levels, scale bar, accuracy statement → the neighbour. That memo's
  routing is accepted unchanged and its file is not touched.

`construction_property.agency-listing.research.md` also names this id, only to decline an edge:
*"the conveyance is `sale-purchase`'s seam, already authored; no second edge earns its place."* That
is consistent with the edge set here, which points at `sale-purchase` and not at `agency-listing`.
No change is recommended to either landed row.

## The collision fixture

`Report on Title - Project Harbour property portfolio.pdf`. It quotes register extracts, lists real
title numbers, is written by a practitioner, concerns land, and is not this row's. **What
discriminates it:** the anchor is a *deal*, not a *parcel* — many parcels appear in one schedule
under a materiality threshold, the addressee is a corporate acquirer under a codename rather than an
individual purchaser, and it cross-references a disclosure letter and a conditions-precedent
checklist. There is no apportionment split at a completion date and no registration application over
any single parcel. Title numbers are the *content*; the deal is the *anchor*.

A second, harder one is carried as a fixture for the opposite failure: `Completion Statement -
14 Oakfield Road - please check.pdf`, where the bytes are this row's and the *holder's role* is not.

## Fields and `proposed_fields`

`fields: []` and `dimension_order: []` are correct and deliberate: the schema declares no field rows
under PR-6, a dimension may only branch on a field the same schema declares, and no deep template
unlocks from a safety co-activation.

One candidate is proposed for R1c: **`title_reference`**. The argument is a privacy argument, not a
filing one. The natural anchor of this world is a property, and the natural label for a property is
its **address** — which writes where a named person lives into a path that every later process
reads. A registry title number is *pseudonymous*: it discloses that some registered parcel is being
transacted, not which dwelling or whose. If any property-level branch is ever permitted in this
family, the pseudonymous identifier is strictly safer than the obvious one, and that trade-off
deserves adjudication rather than silent omission. `reliability_ceiling: validated`, rule family:
registry-identifier pattern **plus** registry-document context — the bare token is a bare
alphanumeric and 00 forbids a bare token as sole proof.

Rejected candidates, and why no existing key works: `location` is the Photos capture-place key and
would import a geographic reading of what is an opaque registry identifier; `institution` and
`record_type` are Finance-scoped; `project`, `stage` and `artifact_type` are Research and Code;
`purpose` remains scoped to College Applications; `client` and `our_firm` name people, not land, and
are borrowed only for the `role_split`. A `property_address` key is **deliberately not proposed** —
proposing it would create the disclosive destination this row exists to forbid.

## Neighbours considered that did not get an edge

- **`law_practice.matter-correspondence`** — every conveyance is largely correspondence, but the
  seam is a *function within* a matter, not competing evidence, and the schema already owns the
  correspondence work type. An edge would be a taxonomy, not a boundary.
- **`law_practice.due-diligence`** — named in the `needs_llm` reading of the report-on-title
  fixture, but the mutex is authored against `transactional-deal`, which is where the anchor
  actually differs. One edge, not two.
- **`government.planning-application`** — planning material arrives as *copies* inside a search or
  enquiry pack. The authority-side application record is `government`'s; the schema-level
  `also_holds_with government` already carries the seam without a template-level edge.
- **`construction_property.mortgage-brokering`** — the broker's own side. No shared discriminating
  evidence item: a broker's fact-find and lender panel comparison have no parcel apparatus.
- **`legal.leases-agreements`**, **`legal.personal-legal-matters`** — the holder-role ambiguity is
  already expressed against `construction_property.sale-purchase`, which is the sharper and more
  concrete fork for this row's evidence. Adding legal-content siblings would recreate a practice-area
  taxonomy, which is exactly what J-IND defers.
- **`photos.screenshot-captures`** and **`photos.scanned-documents`** — co-activations recorded on
  fixtures (`also_schema`), not mutexes.

`also_holds_with` is authored at schema level only (`government`, `identity`, `finance`) because
`also_holds_with` joins **schemas** and this is a template row; the finer co-activations are recorded
on fixtures. All three are one-way; **R1c owes the reciprocals.**

## Grouping without copied facts

The transaction group is content-incoherent and purpose-coherent — 00's own licence: *"The documents
are content-incoherent but purpose-coherent."* The anchor supports candidate membership and copies
no address, price, owner or lender fact onto any member. The search pack is the one grouping in this
row joined by a **parcel** rather than a matter, which is why the parcel leg had to exist. A shared
parcel across time is offered as a candidate and never asserted — the same dwelling may be
transacted twice a decade apart for different clients. And nothing groups on a shared address,
postcode, lender, agent, completion date or download session, because *"It should not form a
supported group when there is no valid anchor"*.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment from
`planning/domains/dispatch/make_prompt.py law_practice.conveyancing`;
`planning/domains/nodes/legal.practice-matter-file.research.md` (depth calibration);
`planning/domains/nodes/law_practice.json` (schema anchor — recognition, template, work_types,
grouping_reasons, edges, sensitivity); `planning/domains/roster.json` (every edge id verified
present); `planning/domains/canonical_fields.json` (full key list);
`planning/domains/nodes/construction_property.site-survey.research.md` and
`construction_property.agency-listing.research.md` (the two landed rows that already argued a
boundary against this id); `planning/00-database-agent-product-design.md`, read by targeted grep
only — every quoted span in the JSON and this memo was grep-verified verbatim before use. No
quotation is attributed to 00 that was not matched literally in that file. No threshold numbers, no
handling classes, no invented catalogue contents.

Document types named in the fixtures (register and title plan, local land charges and local-authority
enquiries returns, drainage and water report, property information and fittings-and-contents forms,
report on title, requisitions, certificate of title to a lender, completion statement with
apportionments, transfer-tax return, registration application and title information document,
practitioner undertakings) are named as **real document types** occurring in this world. They are
used only for artefact *shape* — no jurisdictional rule, deadline, priority period, retention
duty or legal effect is derived from any of them anywhere in the node.

## NEEDS-JOSEPH (this node only)

- **NJ-LPC-1 · The unprotected residue.** A search pack, an enquiry form, an apportionment schedule
  and a registration application are this row's *characteristic* files and fire **neither** `legal`
  nor `finance` — so the safety-domain protective ordering that usually rescues this material does
  not run on exactly the files carrying a dwelling address, a purchase price and a non-client
  donor's bank statements. Alternatives: (a) leave it to `potentially_sensitive` plus Protected
  Records routing, accepting that protection is a residual rather than an ordering guarantee;
  (b) give a template a way to require P7 handling ahead of any model path for third-party personal
  material — a mechanism this catalogue does not have, and which
  `construction_property.agency-listing` raised independently as NJ-CP-AL-1, so this is a *shared*
  gap and not a local one; (c) extend 00's four safety domains, which this row does **not** propose
  and believes must not be decided at row level.
- **NJ-LPC-2 · `title_reference` and the pseudonymity distinction.** Whether the key is adjudicated
  canonical at all, and if so whether a pseudonymous parcel identifier may be
  destination-**eligible** where a property address may **never** be. The whole disclosure argument
  of this row turns on that distinction, and if R1c rejects the key the correct consequence is that
  this family has *no* property-level branch, not that the address becomes the fallback.
- **NJ-LPC-3 · The estate sale.** Where a personal representative sells estate land, this row and
  `law_practice.estates-administration` are both correct on the same bytes. R1c must decide mutex or
  co-activation; both rows should name the registration application as the competing fixture.
- **NJ-LPC-4 · Unregistered title.** Where no register exists the anchor is an abstract or epitome
  of title — a numbered schedule of historic deeds. This row admits it as a structural variant in
  `needs_llm` rather than guessing at jurisdiction, but if R1c wants one recognition rule rather than
  two, the epitome schedule needs a first-class signal of its own.

## Recommendations to R1c (no file outside this node was touched)

1. Author the reciprocals for `law_practice.transactional-deal`,
   `construction_property.sale-purchase`, `construction_property.survey-valuation`,
   `law_practice.estates-administration` and `finance.loans-mortgage`, and for the three schema-level
   `also_holds_with` edges. Each names its fixture here already.
2. Do **not** add `law_practice.matter-correspondence`, `law_practice.due-diligence` or
   `government.planning-application` edges to this row; the reasons are recorded above and adding
   them would begin a practice-area taxonomy.
3. `construction_property.site-survey` and `construction_property.agency-listing` are consistent with
   this row as landed. Neither needs amending.

## Self-verification

- `python3 -m json.tool` parses the node cleanly.
- Every `collides_with`, `also_holds_with`, `role_split.other_domain` and `file_examples.also_schema`
  id was checked programmatically against `roster.json` — all ten present.
- Every `falls_through_to.residual_template` is one of 00's nine residual homes.
- Every `file_examples.source_type` is in `SOURCE_TYPES`.
- Every quoted span attributed to 00 was grep-matched verbatim in
  `planning/00-database-agent-product-design.md` before being written.
- `fields: []`; the single `proposed_fields` entry carries its reason and its rejected alternatives.
- Observations are split from facts on all fourteen fixtures; no fixture writes a folder path as a
  fact; three fixtures carry `group_without_copying_facts: true`.
- `never_alone` contains signals true of tempting false files actually named here — the address, the
  bare registry token, the vocabulary, the firm name, the deed, the extension, the download session,
  the house-named folder.
- No threshold numbers, no confidence scores, no handling classes, no `is_safety_domain`.
- Only the two assigned files were written.

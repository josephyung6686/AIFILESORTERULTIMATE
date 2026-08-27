# Research memo — `retail_hospitality.premises-licensing`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.premises-licensing.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, placeholder launch

## Result

**Accept.** The row passes on **detection** and on **privacy**; it passes on **dimensions** only by rewriting the middle level's *meaning* (continuing permission rather than dated trading session) while keeping the schema's three-level shape. That honesty is `NJ-PL-1`, not a silent claim that the dimension list is novel.

What makes this a situation rather than a label: it is the operator's **long-running permission-to-trade file** for one premises — application, grant, conditions, variation, temporary notice, responsible-person appointment, review — keyed to a place and to licensable activities with hours. It is not the word `licence`, not Companies House, not the authority's case, and not the kitchen's daily hygiene diary.

## The charge — the strongest case that this row should not exist

Six prosecutions. The fourth is the dangerous one.

**1. A lifecycle stage.** The hint lists applications, grants, conditions, variations, reviews. That is a stage vocabulary. *Defeated:* those are **functions inside** one permission life, not the row's identity. A variation of a lease, a variation of a software EULA and a variation of a premises licence share the word and share nothing else. Recognition fires on premises-keyed activity-hours-and-conditions under operator custody, unchanged if the word `variation` never appears.

**2. A document type — `licence` / `permit`.** The schema's own never-alone list already convicts rows that rest on document-type words. *Defeated,* and encoded as this row's first never-alone: software licences, driving licences, alienation licences, hot-works permits and blank application forms all wear the token. Nothing in recognition fires on the word.

**3. A work-type value on its own schema.** The schema's `work_types[]` already contains *"premises permission record - licence application, grant, conditions, variation, review, notice, hygiene inspection report."* *Defeated by the node test proper:* `work_types` is browse vocabulary. If enum membership defeated this row it would defeat all fourteen siblings. The hygiene-inspection clause inside that enum is separately prosecuted under charge 6 / `NJ-PL-2`.

**4. A duplicate of its schema's default template.** *This one nearly landed.* The schema already lists a PERMISSION-TO-TRADE deterministic structure, names "licensed premises" as an occasion type in the default prose, and groups "ONE PERMISSION over its life." A child that only repeats that union would be the default wearing a name.

*Survives on three differences, argued below.* (a) Detection is narrowed to **operator custody** of a **continuing** permission life, not the schema's whole recognition union. (b) Dimensions keep site → occasion → function but the occasion is a **years-long permission reference**, not a session/count/booking; year-first is uniquely destructive here. (c) Privacy differs from the family's guest-data default: responsible persons and objectors, plus the public-display / private-pack linkage trap.

**5. A duplicate of `government.permit-licensing`.** That row landed first and already treats the licensee's copy as the recipient side. *Defeated on the fixture:* `Premises Licence - The Mill Tavern - certificate and summary.pdf` is byte-identical in the parts that matter; custody apparatus discriminates. Two rows that give opposite answers on one file are not duplicates.

**6. A duplicate of `retail_hospitality.food-safety`, via hygiene inspection.** The schema work_type listed hygiene inspection under premises permission; `business_operations.compliance-audit` already routes food-hygiene inspection toward food-safety. *Survives narrowly:* this row may retain an inspection report only as a **pack member**; food-safety owns the operative diary. Recorded as `NJ-PL-2` because food-safety is still owed and both must agree.

**Verdict: `refuse_node: false`.** Charge 4 is contested on dimensions and written into `NJ-PL-1` rather than smoothed.

## The node test, argued in full

**Leg 1 — detection differs from the schema default. PASSES.**

The schema's recognition union names many structures (tender reconciliation, count-against-book, capacity-against-dated-demand, permission-to-trade, daily-signed-check, ingredient-and-yield, order-cycle, guest-voice, catalogue-and-price). As with guest-feedback's reading of GUEST-VOICE, that list is the schema naming what its children collectively recognise — not a claim that the default template already does this row's work.

This row's signals are specific:

- premises address + licensable activities with permitted hours + conditions annex + responsible-person role slot, under **operator** custody;
- one licence reference recurring across application / grant / variation / TEN / review over years;
- DPS/FBO consent pairing a personal credential to a premises reference;
- public notice or hearing papers received as operator correspondence;
- temporary/occasional permission keyed to a place and a dated window.

None of those is a Z-read, a stock count, a booking sheet, a recipe build, or a guest-review export. The authority-side register extract, officer report and determination minute are deliberately out of scope — they are government.permit-licensing's.

**Leg 2 — dimensions differ. PASSES PARTIALLY; CONTESTED.**

Default prose: trading unit → trading occasion → record function, not time-first. This row keeps the shape. The difference is the middle level's **referent**: a continuing permission, not a dated capacity occasion. That is a real filing difference (members years apart; year-first scatters the life) but it is uncomfortably close to re-describing the default's own "licensed premises" bullet. Serialised as `dimension_order: []` because the schema declares no fields. Whether `trading_occasion` may stretch is `NJ-PL-1`. Absolute prohibitions: named responsible persons and bare licence numbers as visible branches.

**Leg 3 — privacy differs. PASSES DECISIVELY.**

The family default is about guests and consumers. This row's pack is about **named responsible persons and objectors**, and it is **mixed public/protected** about the same permission: the wall summary is meant to be seen; the application, suitability and representations behind it are not. Display-copy publication must not lower the pack's posture — the same linkage trap guest-feedback records for review exports, and the same mixed posture government.permit-licensing records on the authority side. Sensitivity stays `potentially_sensitive` only; no handling class is minted.

## Binding material read

- `planning/00-database-agent-product-design.md` — every quotation below was `grep -F`-verified before writing.
- `planning/domains/CONNECTION.md` — node test, edges, activation ≠ grouping.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`, `planning/domains/dispatch/RESEARCH-BRIEF.md`.
- Stamped assignment from `make_prompt.py retail_hospitality.premises-licensing`.
- Schema anchor JSON only: `retail_hospitality.json` (not its memo).
- Depth calibration: `legal.practice-matter-file.research.md`.
- Idiom calibration: `retail_hospitality.guest-feedback.json` / `.research.md`.
- Neighbour greps: `government.permit-licensing`, `business_operations.corporate-regulatory-filings`, `business_operations.compliance-audit`, `construction_property.compliance-certificate` (refused document-genre control), `construction_property.commercial-lease` (roster id confirmed).

External grounding is by named real document types only (premises licence application / grant / conditions, DPS consent, personal licence, Temporary Event Notice, blue notice, licensing-subcommittee agenda, FHRS inspection report, street-trading consent). No gazetteer contents, regexes, thresholds, or legal-validity conclusions are proposed.

## Bottom-up file set

The JSON carries full observations / facts / residuals. Why each fixture exists:

1. `Premises Licence Application - The Bell, Wharf Street - PL-2026-0881.pdf` — labelled application structure.
2. `Premises Licence - The Mill Tavern - certificate and summary.pdf` — **collision fixture** with government.permit-licensing (same name both sides).
3. `Premises Licence PL-2026-0881 - full conditions annex.pdf` — conditions schedule member.
4. `Licence variation - extend hours - notice of application.pdf` — variation / notice.
5. `DPS consent form - Jordan Lee - The Bell.pdf` — responsible-person appointment.
6. `Personal Licence - Jordan Lee - PLH-44192.pdf` — personal credential; joins only as pack member; `also_schema: identity`.
7. `Temporary Event Notice - Ashcroft wedding - 6 Jun 2026.pdf` — occasional permission; collision with event-production.
8. `Licensing Sub-Committee hearing - The Bell - agenda and papers.pdf` — hearing papers in operator custody.
9. `Food hygiene inspection report - 12 Feb 2026.pdf` — **collision fixture** with food-safety (same name both sides; schema already used this filename).
10. `Licensing fee receipt - PL-2026-0881 - 2026 annual.pdf` — finance co-reading.
11. `Licence pack - The Bell PL-2026-0881.zip` — purpose-coherent archive; manifest only.
12. `IMG_1422 - licence summary on bar wall.jpg` — display photograph; photos co-reading; custody weak alone.
13. `Confirmation statement - The Bell Ltd - Companies House.pdf` — **rejected** entity filing false friend.
14. `Alienation licence - Unit 4 Wharf Street - landlord consent.pdf` — **rejected** lease-licence false friend.
15. `EPOS software licence key - Square for Restaurants.pdf` — **rejected** software-licence false friend.
16. `Blank premises licence application form - specimen.pdf` — **rejected** blank/template false friend.

## Files considered and rejected

- Authority register extracts and officer working papers — government.permit-licensing, even when emailed to the operator as attachments inside a larger case export.
- Companies House filings, VAT registrations, insurance schedules — business_operations / finance; trade name overlap is never-alone.
- Landlord alienation licences, rent reviews, dilapidations — construction_property.commercial-lease.
- Hot-works / permit-to-work — construction_property.site-health-safety (government.permit-licensing already edged this).
- Daily temperature logs, cleaning schedules, probe sheets — food-safety's diary, not this row.
- Software, content, and font licences — residual Independent Records or code/creative worlds.
- Blank specimens, franchise manual examples, solicitor training packs — purpose is not a live permission.
- A tourist or journalist photograph of a wall licence with no operator pack — Temporary Screenshots / One-Off Images; custody fails.
- Password-protected licensing-system dumps — Unsupported or Encrypted; filename invents nothing.

## Fields and proposed_fields

`fields: []` by contract. **`proposed_fields: []`** deliberately.

- Reuse the schema's existing proposals `site` and (contested) `trading_occasion` rather than mint `licence_number`, `premises_licence`, `dps`, `permission_ref`, or `venue`.
- `organization` is the wrong concept (entity collector).
- `property` belongs to construction_property's interest reading of the same address.
- Minting a permission-reference key is exactly what `NJ-PL-1` asks R1c; this pass refuses to mint under PR-6.

## Edges

**Authored collisions** (object form, same fixture both sides): government.permit-licensing; business_operations.corporate-regulatory-filings; retail_hospitality.food-safety; construction_property.commercial-lease; finance.small-business-bookkeeping; retail_hospitality.store-operations; retail_hospitality.event-production; logistics (explicit non-collision on the must-consider list).

**`also_holds_with: []`.** Handoff rule: schema ↔ schema only. Co-readings are recorded on fixtures (`identity`, `finance`, `photos`) and the schema anchor already carries `also_holds_with: government` for licence packs. R1c may add template-level notes; this row does not invent schema↔schema edges from a template.

**`role_split: []`.** Fieldless schema; the family's operator/guest split lives on the anchor.

**Fallthroughs:** Independent Records (standalone certificate), Protected Records (named-person material), Receipts and Confirmations (isolated fee receipt), Review Later (unsettled custody), Temporary Screenshots (wall/portal capture without pack), Unsupported or Encrypted.

## Deliberate non-edges

- `logistics` — must-consider neighbour; no shared bytes found; recorded as a non-collision signal so the requirement is not silently skipped.
- `government.public-health-administration` — inspects premises for transmission/hygiene frames; left to food-safety / that row's own NJ rather than triple-claiming the inspection report here.
- `identity` — personal-licence photograph is `also_schema` on the fixture, not a mutex collision.
- `legal.practice-matter-file` / `law_practice.*` — a solicitor's file of a licensing appeal is practitioner-side legal work; out of scope for this operator template at J-IND depth.
- `construction_property.compliance-certificate` — refused document-genre control; cited as negative control, not edged.

## NEEDS-JOSEPH

1. **NJ-PL-1** — Does `trading_occasion` admit continuing permissions, or is a later permission-reference concept required?
2. **NJ-PL-2** — Who owns hygiene inspection reports once food-safety lands?
3. **NJ-PL-3** — Personal licence alone: identity/Protected unless pack membership (this pass) vs other alternatives.
4. **NJ-PL-4** — May a licence number ever be destination-eligible (redacted / user-confirmed / never)?
5. **NJ-PL-5** — Confirm reciprocal with government.permit-licensing on the Mill Tavern certificate fixture.

## Self-verification

- Wrote only this id's two files; did not commit.
- JSON parses; `fields: []`; `also_holds_with: []`; every collision/also entry is an object with `domain` + `signal`.
- Collision signals use `SAME FIXTURE BOTH SIDES:` and name one real file.
- Quotes attributed to `00` were `grep -F`-verified before write.
- No threshold numbers; no handling classes; provenance `inference` / residual `design`.

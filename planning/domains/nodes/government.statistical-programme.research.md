# Research memo — `government.statistical-programme`

Depth: J-DEPTH
Date: 2026-08-26
Output: `planning/domains/nodes/government.statistical-programme.json`
Roster row: `kind: template` on the fieldless `government` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node, narrowly and on two grounds only: a **cycle-shaped grouping anchor** the government default does not have, and an **inverted privacy rule** that no other row in this schema needs. It writes no fields, proposes none, and recommends no serialized dimension order. Everything else about it — the vocabulary, the file formats, the agency names, the fact that the world is "statistics" — was tested and found to be non-evidence.

## The charge against this row, stated at full strength

I tried to kill it four ways before writing anything.

**1. It is a work_type value on its own schema.** This is the strongest attack and it is nearly fatal. `government.json` already carries, as one of thirteen `work_types` entries, the string *"census or survey instrument, collection record, methodology, quality report, statistical output, disclosure-control record, or microdata-access record"*. That is this row's entire subject matter, already enumerated as a value on the parent. CONNECTION.md §2 is explicit that a value is **not** a roster node: "Values auto-create at runtime … a runtime-created thing cannot be a hand-authored roster row". If the only content here were that list, the row is a work_type wearing a name, and the correct action is refusal.

**2. It is a document-type row.** "Questionnaire", "bulletin", "codebook", "quality report" are document types. §2 forbids "a schema per work type, never a schema per file format", and a template that only says *these seven document kinds exist* has said nothing.

**3. It is an organisation-name row — never-alone evidence dressed as a domain.** The world is popularly identified by a body: a national statistics office. The anchor already bars exactly this: "a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone". A row that fires on an agency name can never legally activate.

**4. It is a duplicate of the schema's default template.** Both are fieldless. Both have `dimension_order: []`. Both are `potentially_sensitive`. Both route to Independent Records / Protected Records / Reading Inbox / Review Later / Unsupported or Encrypted. On the serialized surface the two objects are close to identical.

**What defeats the charge.** Attacks 2 and 3 are conceded outright — they are why `never_alone` on this node is long and specific rather than a courtesy list. Attacks 1 and 4 fail together, for the same reason. The work_type entry on the anchor enumerates *artefacts*; it says nothing about how they cohere or how they must be protected. Two things about this world are not derivable from that list:

- **The grouping anchor is a cycle, not a case.** The government default's first grouping reason is "one evidenced authority-side proceeding or decision lifecycle, linked by an exact bill, rulemaking, consultation, application, permit, case, request, procurement, election, or programme reference". Every anchor in that list except the last is a *bounded* thing that opens, runs and closes. A statistical programme has no case number and never closes: it has an instrument that recurs, and a reference period that labels each recurrence. The consequence is a rule the default cannot state — the 2025 and 2026 rounds of one survey are **separate** groups sharing a series name, and merging them by series would copy a round fact onto members that never carried one. The `elections-administration` sibling made the same distinction from the other direction when it declined an edge to me: "a count is an enumeration, not a survey". A count closes on election night. A survey series does not.
- **The privacy rule runs backwards.** Everywhere else in this schema, the risk is that a protected packet leaks. Here the flagship artefact is *deliberately published on a pre-announced date*, and the risk is that the published half sets the posture of the whole. A single directory holds a public bulletin, a public quality report, a public release calendar — and beside them the completed returns naming households, the unit-record file, the pre-release access register naming individuals, and the embargoed draft. The anchor's `sensitivity_why` reaches for "restricted statistics" in a list; it does not carry the rule that publication of the aggregate must never lower the posture of the unit records. That rule is this row's, and it is a privacy difference, which CONNECTION.md §2 accepts as sufficient on its own.

The row therefore survives on the argued minimum, not comfortably. Had only the artefact list been true of it, I would have refused.

## Node test, all three legs

CONNECTION.md §2: "A **template** row exists only if its detection signals, recommended dimensions, or privacy rules differ from its schema's default template." Three legs, disjunctive. I argue each separately and report one failure honestly.

**Leg 1 — detection signals: DIFFER.** The anchor's `deterministic` list is a menu of thirteen role-shapes, each a one-line sketch; the statistical entry is one of them. This row's signals are not that entry restated. They add discriminators the anchor does not carry and could not: *instrument = numbered questions **plus** routing instructions **plus** a named field period* (which excludes every ordinary numbered form in the schema — permit applications, benefit claims, consultation response forms); *methodology artefact tied by an exact round identifier to another accepted member* (which is what stops a lone weighting note from firing); a **disclosure-control record** as a first-class signal, which exists nowhere else in government; a **release-calendar / pre-release-access** signal; and a mandatory **role check** on any completed return. That role check is a signal shape the anchor has no need for, because a bill or a permit case has no respondent.

**Leg 2 — recommended dimensions: DOES NOT DIFFER, and cannot.** Both this row and the default serialize `dimension_order: []`, because PR-6 leaves the schema fieldless and "A row's `dimension_order` may only name fields its schema declares". I will not claim a difference that the file does not contain. In prose the orders do diverge — the default wants a bounded proceeding reference first, this row wants instrument before round before work type, and the reason is specific (the same instrument recurs, so instrument-first is what keeps a round intelligible, in the same way 00 says Homework 3 is meaningless without the course). But prose divergence under a fieldless schema is a promissory note, not a passed leg. **This leg fails.** The node stands on legs 1 and 3.

**Leg 3 — privacy rules: DIFFER.** Argued above. Concretely: the default's protection reflex is *this packet is authority-side, therefore restrict*. This row needs the additional reflex *this packet is partly published, therefore do not infer that any of it is publishable*, plus a hard rule that no respondent-derived token (household address, business name, person) may become a display label or a folder level at any depth. Neither is stated on the anchor.

**Not distinguished by:** filenames, extensions (`.sav`/`.dta` are tool artefacts, not roles), statistical vocabulary, agency names, or work types. All four are in `never_alone` precisely because they are the tempting shortcuts.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (full) and the stamped assignment from `make_prompt.py government.statistical-programme` (full).
- `planning/domains/nodes/government.json` — the schema anchor. Read its `template`, `file_kinds`, `sensitivity`, `falls_through_to`, `open_question`, `work_types`, `grouping_reasons` and `recognition.never_alone`. This is my measured-against default template.
- `planning/domains/CONNECTION.md` §2, lines 75–112 — node test, and the value/group/residual exclusions.
- `planning/00-database-agent-product-design.md` — by targeted grep only. Every span I quote was verified with `grep -c -F` before it was written; all returned exactly 1.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — depth calibration (one launch row, as instructed).
- Landed neighbour boundaries, found with one grep for my id: `government.library-administration.json`, `government.elections-administration.research.md`, `business_operations.market-research.research.md`, `business_operations.corporate-regulatory-filings.research.md`. Read only the matched regions.
- `planning/domains/roster.json` — id existence check for every edge target.

**A finding worth recording plainly: `00` never mentions this world.** `grep -i` for `statistic`, `census`, `survey` and `microdata` across `00` returns **zero** hits. There is no design cite for the subject matter, only for the mechanics (residuals, dimension ordering, privacy enforcement, extension/session/EXIF rules). That is why `provenance` is `proposal` and `design_cite` is `null`. Every substantive claim about statistical production in this memo is either an argued inference from the anchor, or a named real artefact type — never a design reading, and never a quotation.

## Files considered and REJECTED

A row that lists only what it holds has not been researched. These were live candidates and are not this row's evidence.

- **`Statistical bulletin - Consumer Prices - August 2026.pdf`, downloaded.** The single most common file in this world and it is *not* mine. Publication is not custody; the anchor already bars "an official statistics release downloaded for reference". It is Reading Inbox. It appears in `file_examples` only so the fixture is on record as a rejection.
- **An open-data CSV, an API extract, a dashboard export.** Numbers-bearing, agency-branded, and pure reference material. No instrument, no round, no access condition.
- **A statistics-agency name, seal, letterhead or PDF producer string.** Attack 3 above. Never-alone, no exceptions.
- **Any `.sav` / `.dta` / `.sas7bdat` file as such.** These say *someone used SPSS or Stata*. Marketers, epidemiologists, PhD students and central banks all do. The format is a tool, and 00: "treat the file extension as a routing signal rather than an assumption about meaning".
- **An academic paper or working paper analysing an official series.** Citing is not producing. `research.reading-library` / `research.manuscript-publication` territory.
- **A completed return held by the respondent.** Rejected *as this row's* — see the reciprocal boundaries. This is the role-slot rejection and it is the most consequential one.
- **A census-themed genealogy holding.** See the collision fixture.
- **An employee survey run by a statistics agency.** Rejected: employer-to-workforce, `hr.engagement-survey`.
- **A live collection system, a survey platform account, a statistical database.** Source systems, not file nodes. A bounded export with a readable manifest is represented; ingestion is a later connector decision.
- **Population projections, national accounts and price index compilation as separate worlds.** Tempting as siblings; refused as the 574 mistake. They are outputs of programmes already covered, and splitting them would be a taxonomy of subject matter, not of organisational situations.
- **A charity's or company's survey of its own members or customers.** `nonprofit.member-association`, `business_operations.user-research`. Sponsorship decides, not shape.

## The collision fixture

**`1911 Census - Yorkshire - Smith household - schedule.jpg`** — a photographed historical enumeration schedule in a family historian's folder. It carries the word *Census*, a household roster grid, official printed headings, an archive reference stamp, and a hand transcription note. It looks more like a census artefact than my questionnaire does, because it *is* a census artefact.

It is not mine, and four things discriminate it, none of which is the word Census: **no instrument version**, **no field period or live collection round**, **no release calendar or revision policy**, **no access condition or licence**. The programme that produced it closed a century ago; what remains is a document, not a cycle. It is `photos.family-archive` evidence, and if that does not fire it is Independent Records — a standalone form with durable purpose and no broader group. Its practical value here is that it is the fixture my `never_alone` line about historical enumeration schedules must trip, and it demonstrates why *census vocabulary* had to be barred rather than merely deprioritised.

Second-order collision worth naming: **`Brand Tracker Wave 12 - questionnaire and weighting note.docx`**. Byte-shape identical to a real instrument — numbered questions, routing, wave token, quota and weighting section. The discriminator is contractual, not structural: a statutory collection power and a statistical-purposes-only pledge on one side; a commissioning client and a fieldwork agency on the other. If both are stripped or unbranded, neither row should fire and the file is Review Later.

## Reciprocal boundaries — same fixture named on both sides

- **`government.library-administration`** — *Annual return - public library statistics 2025-26.xlsx*. That row landed first and authored the seam against me: "the statistical sibling holds the collecting authority's cycle … This template holds the same instrument on the RESPONDENT side … The bytes can be identical; the role slot decides." I reciprocate verbatim in substance: collecting side beside the definitions guidance, the chasing log and the resulting tables is mine; the filing service reporting on itself is theirs; unevidenced slot means **neither** fires.
- **`business_operations.market-research`** — *Brand Tracker Wave 12 …* against *National Household Survey 2026 - questionnaire …*. Mine when statutory power and the statistical-purposes pledge are present; theirs when a commissioning client and fieldwork agency are. **Asymmetry:** their memo declined an edge, reasoning "a source, not a confusion". That is right about the published bulletin and wrong about the instrument, which is where the collision actually lives. I edge; R1c adjudicates.
- **`business_operations.corporate-regulatory-filings`** — a compelled business survey return. Theirs on the responding company's side (one more return with a reference and a deadline); mine on the collecting side (a received return inside a round). **Asymmetry:** they declined, holding `government.public-authority-record` already carries the which-side discriminator. I edge anyway because the generic authority row does not name the instrument, and a byte-identical fixture deserves a named seam.
- **`government.public-health-administration`** — a population health data collection. Designed sample with instrument, field period and weighting spec is mine; administrative or notifiable-disease surveillance assembled from operational case reporting is theirs, even when published weekly with charts. Designed collection versus administrative by-product; not subject matter.
- **`research.dataset-analysis`** — *NHS2026_microdata_EUL_v1.sav* plus codebook. The producing authority's curated, licensed, disclosure-controlled product is mine; the identical download inside an analyst's project with derived files and scripts is theirs. Secondary use is not production. Both keep the protected posture, so the seam is about routing, not safety.
- **`government.public-records-foi`** — *FOI 2026-0412 - response - unpublished regional breakdown.xlsx*. Produced on demand under a request reference with a disclosure schedule: theirs. Announced on a release calendar with a revision policy: mine. Same statistician, same source data, two workflows.
- **`hr.engagement-survey`** — *Staff engagement survey 2026 - questionnaire.docx* held by a statistics agency. Employer-to-own-workforce is theirs regardless of employer; household/business/population collection under statistical authority is mine.

Coactivations (`also_holds_with`, not mutexes): `research.ethics-compliance` on the signed secure-access agreement (the authority's access record *and* the researcher's undertaking, one file, both legal); `government.public-consultation` on a consultation about census question content (their response corpus never migrates here, only the programme-design half is mine); `photos.screenshot-captures` on the release-calendar screenshot.

## Neighbours considered that got NO edge

- **`government.elections-administration`** — turnout and result statistics. They declined an edge to me and I decline symmetrically, for the same reason in my own words: a count is a complete enumeration of a closed event, my discriminators (instrument, sampling design, disclosure control, microdata access) are all absent from a ballot account, and their discriminators (polling station, ballot batch, reconciliation) are absent from mine. This is the one place both sides already agree.
- **`government.public-authority-record`** — the generic authority row. Every child of this schema could edge it; edging it here would be re-authoring the parent's boundary and would add nothing this row's own signals do not.
- **`legal.*`** — the Government↔Legal seam is authored at schema level on `government.json`. Not duplicated.
- **`government.archives-recordkeeping`** — historical census schedules deposited with an archive. Real, but that is the archive's custody world, and my collision fixture is a *private* family holding, which archives-recordkeeping would also decline. Left unedged; flagged below only if R1c disagrees.
- **`business_operations.user-research`**, **`nonprofit.member-association`** — customer and member surveys. Covered in substance by the `market-research` edge; a third and fourth survey edge would be practice-area padding.
- **`hr.workforce-analytics`** — aggregated workforce statistics. Same decline as `engagement-survey`, already edged; one edge suffices.
- **`academic.*`** — students analysing microdata. Covered by `research.dataset-analysis`.

## Fields, proposed fields, dimensions

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false` — all deliberate under PR-6 and D1's standing deferral, and consistent with the landed `government` siblings. Candidates considered and **not** proposed:

- `programme`, `instrument`, `collection_round`, `reference_period`, `series`, `respondent_unit`, `release_reference`, `microdata_product` — none is a canonical key, all would be minted by a placeholder child, and the anchor's own open question reserves any role-safe vocabulary for **central** adjudication rather than for children. Minting `reference_period` here would also invite a `period`/`term`/`cycle` synonym family across the schema.
- `record_type` and `institution` exist canonically but are scoped to Finance; `work_type` is Academic's; `project` is Research's. Reusing any of them would be a synonym raid, not reuse — the same reasoning `elections-administration` recorded, and I am deliberately consistent with it.
- `respondent` in any spelling is refused on privacy grounds independent of canonicality: a respondent is a household, an address, a business or a person, and the moment it is a field it becomes a candidate folder level.

`proposed_context_terms` **is** populated (twenty-three methodology terms) and is explicitly labelled a proposal for R2 inside the array itself. The stamped prompt licenses this ("you may propose more in `proposed_context_terms`, you may not pretend `00` listed them"); 00's only stated context floor is the academic one, and I say so in the array rather than let the list imply otherwise. None of the terms is deterministic alone; each must co-occur with a named instrument or round.

## NEEDS-JOSEPH

- **NJ-GOV-SP-1 — proposal-only provenance.** `00` contains no occurrence of *statistic*, *census*, *survey* or *microdata*. This row is anchor-derived reasoning, not design reading. Alternatives: (a) accept that a J-DEPTH placeholder may stand on anchor-derived reasoning with `provenance: proposal` — the position taken here; (b) require at least one design-anchored clause per row, which would refuse this row and route the coverage entirely to Reading Inbox + Protected Records + `government.public-authority-record`.
- **NJ-GOV-SP-2 — the role slot has no field to live in.** Collector-versus-respondent decides the library return, the business survey return and the completed census schedule, and cannot be expressed while the schema is fieldless. Alternatives: (a) both sides stay dark when the slot is unevidenced and the file goes to Review Later — the position taken here, and it silently loses real files; (b) when PR-6 lifts, license one role-safe holder/custodian concept centrally on the anchor (its own open question already reserves this) and let children branch on it; (c) let the *user* confirm the role slot, which is a `user_confirmed` reliability question this pass cannot settle.
- **NJ-GOV-SP-3 — two live edge asymmetries.** `business_operations.market-research` and `business_operations.corporate-regulatory-filings` both landed with an explicit decline of the boundary this row asserts. Alternatives: (a) R1c makes both reciprocal on the instrument/received-return fixtures named on both sides here; (b) R1c upholds the declines and drops these two edges from this node. Do not let first-written win by default.
- **NJ-GOV-SP-4 — methodology term family.** Does `proposed_context_terms` become an R2 term-pattern rule family (with the never-alone co-occurrence requirement intact), or is it dropped because 00 authorises only the academic floor? Dropping it weakens leg 1 of the node test but does not defeat it.
- **NJ-GOV-SP-5 — leg 2 fails.** This node passes the node test on detection signals and privacy rules, not on dimensions, and cannot pass on dimensions while the schema is fieldless. If R1c later requires two of three legs, this row should be re-examined rather than quietly retained.

## Self-verification

- `python3 -m json.tool` on the node: **parses**.
- All six `00` spans used (`Independent Records may live under…`, `Protected Records may represent…`, `Reading Inbox may hold…`, `Receipts and Confirmations may hold…`, `Review Later may hold…`, `Unsupported or Encrypted may hold…`, plus `Privacy policy must be enforced…`, `Protected material should not be included…`, `For document and record domains…`, `The system recommends an order…`, `A session should never be treated as proof of topic`, `routing signal rather than an assumption about meaning`, `the system must not mistake the absence of EXIF…`): each `grep -c -F` returned exactly **1**. No fabricated quote. One phrase drawn from the anchor rather than 00 was de-quoted before finalising.
- Every `collides_with` / `also_holds_with` id checked against `roster.json`: `government.library-administration`, `government.public-health-administration`, `government.public-records-foi`, `government.public-consultation`, `business_operations.market-research`, `business_operations.corporate-regulatory-filings`, `research.dataset-analysis`, `research.ethics-compliance`, `hr.engagement-survey`, `photos.screenshot-captures`, `photos.family-archive` — all present.
- Every `falls_through_to.residual_template` is one of 00's nine names.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; `opaque_binary` is used for the SPSS product and `ocr` for the scanned return.
- No `facts_legal` entry anywhere (fieldless schema); no file example writes a folder path; sparse and cross-side fixtures carry `group_without_copying_facts: true`.
- No threshold numbers, no confidence scores, no handling classes; `sensitivity` is `potentially_sensitive`.
- Files written: exactly the two assigned. No roster, canonical-fields, neighbour-node, `src/`, `check.py` or SPEC edit.

# Research memo — `government.parks-public-lands`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.parks-public-lands.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch

## Result

Accept the node. It survives the charge, but only on a narrower claim than its roster name suggests. The row is **not** "government files about parks." It is the estate-side record of a **designated place** — the instrument that binds a parcel, the plan written against that parcel, the geometry that defines its compartments, the permissions attached to it, the monitoring of its fixed features, and the visitor operation run on it. The parcel, not a proceeding, is the durable unit of custody, and the material that must be protected is precise location rather than personal casework. Those two differences are what defeat the case against the node.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from `make_prompt.py`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibration launch row.
- `planning/domains/nodes/government.json` — my schema anchor, read for its default template: `recognition.deterministic` / `needs_llm` / `never_alone`, `work_types`, `grouping_reasons`, `template`, `file_kinds`, `file_examples`, `collides_with`, `falls_through_to`, `sensitivity_why`, `open_question`.
- `planning/domains/roster.json` — confirmed my id, kind, schema_id, and every edge target.
- `planning/00-database-agent-product-design.md` — reached by targeted `grep -n -F` only. Every span I put in quote marks was matched verbatim before use (see Quote verification).
- `grep -rln "parks-public-lands" planning/domains/nodes/` returned nothing. **No landed row has argued a boundary against me**, so every reciprocal below is authored fresh and is a recommendation to R1c, not an alignment to existing text.

## THE CHARGE — the strongest case that this row should not exist

Stated at full strength before any defence.

**1. It is a subject word wearing a schema's clothes.** Every workflow the roster hint names is already a value in the government anchor's own `work_types`: "planning application, permit or licence case, inspection, enforcement record, reasons, decision, variation, suspension, or revocation on the deciding side"; "grant call, received application, assessment, award, monitoring report, or closure record on the funder side"; "public-body agenda, committee report, budget, performance report, minute, resolution, or public notice". A campfire permit is `government.permit-licensing`. A consent for a building inside a national park is `government.planning-application`. A designation order is `government.legislative-record` or `government.regulatory-rulemaking`. A visitor-centre budget is `government.municipal-administration`. On that reading "parks" is the **portfolio label of an agency**, and the anchor already forbids exactly that: never-alone includes "a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone".

**2. It is an organisation name.** National Park Service, Parks Canada, Natural England, a county countryside service. If the row's real evidence is a park agency's name on a letterhead, it can never activate — the anchor's never-alone list kills it twice, on entity name and on ".gov-style domain, government email address, coat of arms, logo, letterhead".

**3. It is a lifecycle.** Designation → management plan → permissions → conservation works → visitor operations is a sequence of stages, and stages are values. The stamped prompt is explicit that work types are values of a field, never nodes.

**4. It is a duplicate of neighbours.** Conservation works are `construction_property.construction-project`. Species and habitat data are `government.environmental-regulation`. Campsite bookings are `retail_hospitality.bookings-reservations`. Grounds and tree inspections are `business_operations.facilities-workplace`. Concessions and grazing licences are `legal.leases-agreements`. Remove all five and what is left may be nothing.

**5. It is a duplicate of its own schema's default template.** `dimension_order` is empty on the anchor and must be empty here. If dimensions are identical and the recognition preconditions are the anchor's own preconditions, the row is the schema again with a topic filter.

## Defeating the charge

Charge 5 is the one that decides it, so take it first. CONNECTION.md §2's node test is a disjunction — detection signals **or** dimensions **or** privacy rules must differ. Dimensions are tied (both empty, by PR-6). So the row must win on the other two, and it does.

**Leg one — detection signals differ, and differ structurally rather than lexically.** The anchor's ten deterministic signals are all anchored on a *bounded proceeding or cycle*: a bill identifier, a rulemaking identifier, an application or case reference, a procurement notice, a meeting date and agenda number, a collection round, an election event, a records-request number. Each of those references dies when the proceeding closes. This row's signals are anchored on something that **outlives every proceeding**: a designation, vesting or register reference that names a parcel with no applicant slot; a boundary schedule or legal land description; a compartment gazetteer whose unit identifiers recur across a monitoring series, a works package, a closure notice and a licence that share no case reference with each other. That is a different join key, and it produces different groups from the same corpus. It is also testable against my file list: nine of my twenty fixtures carry a compartment or site reference and no case reference at all.

Geospatial evidence is the second structural difference. The anchor's `file_kinds` never contemplates a vector layer as primary evidence, and its `contacts` source type is present while geometry is not called out. Here a `.kml` compartment layer, a coordinate-bearing condition table, and an EXIF-GPS monitoring photograph are ordinary members of the same estate record, dispatched to three different extractors (`code_structured`, `spreadsheet`, `image`) and joined by the site reference in their attributes rather than by content similarity. I mark this as **inference** extending a named domain: `00` describes the extractor dispatch and EXIF handling, it does not name estate geospatial evidence.

**Leg two — privacy rules differ, and differ in kind.** The anchor's `sensitivity_why` protects "citizen casework, identity and contact data, complaints, submissions, unsuccessful bids, evaluator declarations, investigations, enforcement, restricted statistics, ballots or election operations". Every item on that list is **person-shaped**. This row's dominant risk is **place-shaped**: the coordinates of a Schedule 1 nest site, a bat roost, an unexcavated archaeological feature; a warden's patrol route and wildlife-crime narrative. That risk behaves differently. It is not reduced by anonymisation, because there is no person to anonymise. It leaks through channels the anchor does not police — EXIF GPS on an otherwise innocuous photograph, feature attributes inside a geometry file, a high-precision column in an otherwise publishable survey. And it inverts the usual publication logic: the estate's plan, boundary map and byelaws are deliberately published, and that publication must *not* lower the posture of the coordinate table filed beside them. A row whose safety rule is "the location is the secret, and the document around it is public" is not the schema's default rule.

**Leg three — dimensions are tied, and I say so rather than manufacture a difference.** Both are empty. PR-6 forbids fields; a template cannot branch on undeclared fields. The prose recommendation does differ (site first, then estate function, then plan cycle or works reference), but prose is not a serialized dimension and I do not count it as a passing leg.

**Against charges 1–4 specifically.** Charge 1 fails because the discriminator I actually wrote is not the subject "park" but the *absence of an applicant slot and the presence of a parcel-binding instrument*; a campfire permit with a statutory test and appeal rights genuinely is `government.permit-licensing`, and I have conceded that in the collision. Charge 2 fails because I put the park-agency name, the place name, and the `.gov` domain into `never_alone` explicitly — the row cannot activate on them. Charge 3 fails because I enumerated the lifecycle as thirteen `work_types` **values**, exactly as the prompt requires, and none of them is a node. Charge 4 is the serious one and I answer it by writing seven reciprocal collisions rather than by claiming the territory: what survives after all seven are honoured is the parcel-anchored core — the designation instrument, the management plan, the compartment gazetteer, the monitoring series against fixed units, and the estate-side permission. That core is held by no neighbour.

**Where the charge partly wins.** The roster name "Parks, public lands and heritage site management" is broader than what I can defend. "Visitor operations" in particular is mostly other people's territory once the estate reference is removed. I narrowed the `one_line` accordingly rather than defend the full name.

## Files considered and rejected

Named false positives, with the discriminator. Five are serialized as fixtures; the rest are rejected here.

- **`Hollow Marsh Conservation Trust - Estate Management Plan 2026.pdf`** — the primary collision fixture. Identical plan period, compartment prescriptions, condition objectives and boundary plates. Discriminated by front matter only: charity registration and a trustee board versus a designation or vesting instrument and a statutory-body identifier. Nothing in the body of the document decides it.
- **`Notification of designation - your land at Hill Farm.pdf`** — the same instrument, same register reference, same boundary schedule as my estate-side fixture. Discriminated by the **addressee block** and second-person wording plus a representation-rights section. Recipient side; Protected Records.
- **`Yosemite trip - park pass and campground confirmation.pdf`** — park-service branding, a validity window, a reservation reference. No compartment, plan or designation reference; a named holder and a payment total. Receipts and Confirmations.
- **`Corporate campus grounds - tree and playground inspection register 2026.xlsx`** — column-for-column identical to my estate inspection round. Zones are building-relative and the owner is a facilities team. A public body's *own office grounds* also land here, which is the point: public ownership is not public-benefit holding.
- **`Park estate records backup - password protected.7z`** — the filename cannot manufacture a site, a designation, a custody role or a sensitivity result. Unsupported or Encrypted.
- **A published state-of-the-park report, landscape strategy, or ecology paper about the reserve** — publication about a place is not custody of it. Reading Inbox.
- **A ranger's employment contract, payslip, or roster held by the ranger** — the anchor already refuses "a public-sector employer name on a person's resume, payslip, contract, or calendar". Government as employer is HR.
- **A GPX track log or hiking app export inside the boundary** — geometry alone; the same coordinates appear in a hiker's track, a survey firm's deliverable, a developer's site plan and a journalist's map.
- **A museum accession register for a visitor centre's collection** — movable objects with accession numbers are `government.museum-collection`. My heritage fixture is deliberately an *immovable* site with a list-entry reference.
- **A land registry title, transfer, or easement deed for the parcel** — tenure is the legal world's; the designation instrument binds use and condition, not ownership.
- **A live estate or GIS database, booking system, or records system** — a source system is not a file node. A bounded export with a readable manifest is represented; live ingestion is a later connector decision.
- **A friends-of-the-park newsletter, petition, or campaign pack** — advocacy about the site, held by an association; not confusable with an estate record, so no edge.

## Reciprocal boundaries

Each states the boundary in both directions and names the **same fixture** on both sides. All seven are fresh; R1c should author the reciprocal half.

| Neighbour | Shared fixture | Mine when | Theirs when |
|---|---|---|---|
| `government.permit-licensing` | `Filming permission - Estate ref PR-2026-233 - conditions and decision.docx` | the granting body is granting use of land it holds; permitted area is its own compartment; conditions cross-refer to plan prescriptions; **no** statutory test, **no** appeal rights | a statutory test, a regulatory case file, and appeal or review rights over a third party's own activity or premises |
| `government.environmental-regulation` | `Feature condition assessment - Units 4-11 - summer 2026.xlsx` | monitoring of the holder's own estate units, keyed to a compartment gazetteer, feeding a plan cycle | a regulatory monitoring, permitting or enforcement case against a regulated party, keyed to a case or consent reference, carrying a compliance determination |
| `nonprofit.member-association` | `…Estate Management Plan 2026.pdf` (the trust copy vs the authority copy) | designation, vesting or statutory-body identifier for the holder | charity registration, trustee governance or membership structure, and no independently evidenced public-body status |
| `construction_property.construction-project` | `Footbridge replacement - works package and drawings.zip` | employer block is the land-managing body; member paths repeat an estate compartment and a plan prescription | the same manifest sits with the builder, keyed to contract, programme and valuation cycle |
| `legal.leases-agreements` | `Grazing licence - Compartment 4 - Hillside Farms - executed.pdf` | grantor-side copy; demised area is a compartment in the body's own estate; conditions cross-refer to conservation prescriptions | grantee-side copy, or any copy held by a party managing its own tenure, anchored on the agreement and premises |
| `retail_hospitality.bookings-reservations` | `Campsite pitch occupancy and reservations - July 2026.csv` | operator is the land-managing body's booking office; pitch ids key into the estate gazetteer beside closure notices and counter series for the same season | a commercial site with no public-benefit holding and no estate reference |
| `business_operations.facilities-workplace` | `Tree safety inspection round…xlsx` vs `Corporate campus grounds…xlsx` | zones are compartments of land held for public benefit under evidenced designation or vesting | grounds and premises maintenance of an organisation's own workplace, zones building-relative, owner is a facilities team |

## The collision fixture

`Hollow Marsh Conservation Trust - Estate Management Plan 2026.pdf`. It is the hardest case in the row because the document is not merely similar to my central fixture — the two are the same genre, written to the same conventions, often by the same consultants, frequently for adjoining parcels. Plan period, compartment prescriptions, condition objectives, boundary map plates, monitoring schedule and volunteer programme all match. **What discriminates it is front matter alone**: a charity registration number and a trustee board block, and the absence of any designation, vesting or statutory-body identifier. This is a fragile discriminator, and I have marked it so: it lives in `needs_llm` ("separating a public land-managing body from a conservation charity, national trust, community land trust…") and the failure mode is a confident wrong answer, not a miss. The correct behaviour when front matter is cropped, scanned, or absent is abstention to Review Later — "A model that cannot cite sufficient evidence must return unknown."

Secondary collision, in the other direction: `Notification of designation - your land at Hill Farm.pdf` against `Notification of designation - Hollow Marsh - boundary schedule and map.pdf`. Same issuing authority, same register reference, same boundary schedule, same effective date. The addressee block is the whole of the evidence.

## Fields and dimensions

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`. All intentional.

I considered proposing a site/estate anchor key and a designation-reference key, since they carry my entire node-test argument, and rejected both. The government anchor's own open question says to "adjudicate a minimal role-safe vocabulary centrally rather than in children", and PR-6 with D1's deferral leaves the schema fieldless. Minting here would put a child ahead of its schema. The candidates are therefore routed to NJ-1 below as a recommendation to R1c.

Existing canonical keys were checked and none fits: `institution` and `record_type` are Finance-scoped; `project` and `artifact_type` are Research and Code; `purpose` is College Applications; `school`, `term`, `subject` are Academic. There is no canonical key for a parcel.

`time_first` is false: "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders," and a management plan cycle deliberately spans a decade — a year-first order would split one plan from its own monitoring returns.

## Deliberate non-edges

- `nonprofit.volunteer-management` — my `Compartment 12 coppicing - task day.ics` and a volunteer-management rota are genuinely close, and I nearly authored an eighth collision. I did not, because the discriminator is the same owner-role test already carried by `nonprofit.member-association`, and duplicating it would inflate the row without adding a distinct decision. **Recommendation to R1c:** if the volunteer row's own research finds a true same-evidence mutex, add it reciprocally.
- `government.museum-collection` — coactivation-adjacent, not a mutex. Movable objects with accession numbers versus an immovable site with a list entry; my heritage fixture states this in `must_not_conclude`.
- `government.planning-application` — a development consent inside a park boundary is a planning case whoever holds it. The place is the setting, not the anchor. No confusable bytes on my side.
- `government.municipal-administration` — a parks committee report is a governance-cycle artifact and belongs to the meeting cycle, not to the parcel.
- `photos.camera-events` and `research.dataset-analysis` — real coactivation cases, recorded per-fixture as `also_schema` rather than as edges. I kept `also_holds_with: []` deliberately: a fieldless template cannot author schema-level coactivation, matching both the government anchor and the `legal.practice-matter-file` launch row.
- `travel.bookings-confirmations` — a visitor's park pass is genuinely its territory, but `travel` is **not a schema id on the roster** (only `travel.trip-photos` and `travel.bookings-confirmations` exist as templates, with no `travel` schema row). Rather than guess a parent, I set that fixture's `also_schema` to null and routed it to Receipts and Confirmations. Flagged as NJ-3.

## Grouping without copied facts

Candidate groups are bounded by an exact site, designation, register, inventory, compartment, plan, works or permission reference. A group may contain a plan, a geometry layer, a monitoring series, a photograph, a calendar event, a licence and an archive manifest. Membership creates no site, plan, condition, date or custody fact on the member. Three fixtures carry `group_without_copying_facts: true` — the works-package archive, the EXIF-GPS erosion photograph, and the task-day calendar event — because each can join an estate neighbourhood on an exact reference while remaining, on its own evidence, a contractor's package, a personal photograph, and a volunteer's diary entry respectively. An archive manifest is read without unpacking, and no estate joins another on shared place names, species, contractors, consultants or semantic similarity.

## Quote verification

Every span in quote marks in the JSON and this memo was matched with `grep -F` against `planning/00-database-agent-product-design.md` before use: the seven residual definitions (Independent Records, Protected Records, Reading Inbox, Review Later, Unsupported or Encrypted, Receipts and Confirmations, One-Off Images, all at line 120); "Privacy policy must be enforced before content reaches any model or external connector."; "A model that cannot cite sufficient evidence must return unknown."; "the system must not mistake the absence of EXIF for proof that an image is a screenshot"; "treat the file extension as a routing signal rather than an assumption about meaning"; "A session should never be treated as proof of topic"; "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."; "The system recommends an order based on the domain template, but the user can reverse, remove, add, or flatten dimensions."; "A work type such as Homework 3 is meaningful only after the course is known". One quote was corrected during verification — I had originally written the Homework 3 sentence with a terminal period that `00` does not have; the period now sits outside the quotation marks. No threshold, count or statistic appears anywhere. `provenance` is `proposal`; the geospatial-evidence claim and the locational-privacy claim are marked above as inference.

## NEEDS-JOSEPH

**NJ-1 — the anchor concept, blocked by PR-6.** This row's entire node-test case rests on a designated place as the organizing anchor, and that cannot be expressed while the government schema is fieldless. Alternatives: (a) keep the row fieldless and leave the claim in prose, accepting that the recommendation is unenforceable — what I did; (b) lift PR-6 for a single site/estate anchor key adjudicated centrally on the schema, and let this and other place-anchored government rows reference it; (c) refuse the row until PR-6 is settled and route its coverage to Independent Records and Protected Records. I chose (a) because refusing would lose a real and reciprocally-argued boundary set that R1c can use immediately.

**NJ-2 — locational sensitivity has no vocabulary.** The design's sensitivity axis here is only `none | potentially_sensitive`, and handling classes are P7's. But a protected-feature coordinate is sensitive in a way a person's name is not: it survives anonymisation, and it leaks through EXIF and geometry attributes rather than through text. Alternatives: (a) treat it as ordinary `potentially_sensitive` and rely on P7 — what I did; (b) ask P7 for a location-suppression rule (strip or refuse to transmit coordinates from any file in a group that also contains a protected-feature marker); (c) forbid site-named branch labels entirely, since a branch named for a protected site is itself disclosure. I flagged (c) inside the JSON `open_question` because it interacts with NJ-1: the very anchor that would make this row filable may be the thing that must not be shown.

**NJ-3 — the missing `travel` schema.** `travel.trip-photos` and `travel.bookings-confirmations` are on the roster with no `travel` schema row. I could not name a valid `also_schema` for a visitor's park pass. Either the schema row is missing from the roster, or those templates sit on a schema whose id I could not determine. R1c should resolve it; my fixture currently carries `also_schema: null`.

## Self-verification

`python3 -m json.tool` parses the node, and its key set matches `government.json` exactly (including `proposed_context_terms`). All seven `collides_with.domain` values were checked against `roster.json` `domain_id`s and exist; `travel` was checked, found absent, and removed. All twenty `file_examples.source_type` values are in `SOURCE_TYPES`. Every `falls_through_to.residual_template` and `falls_through_if_inactive` names one of `00`'s nine residual homes. No fixture writes a folder path as a fact. `fields` and `proposed_fields` are empty. Five of the twenty fixtures are false friends, and every `never_alone` entry is true of at least one of them — the park-agency name on the trust plan, the place name on the reading copy, the GPS on the visitor photograph, the branding on the park pass. I wrote only my two assigned files.

# Research memo — `government.defence-veterans`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/government.defence-veterans.json`
Roster row: template on the fieldless `government` schema, `parent_id: null`, placeholder launch
Absorbed legacy id: `gov.defence-veterans-administration` (ROSTER.md §4, line 873)

## Result

Accept the node — but only after cutting roughly two thirds of what the row's name promises. The accepted scope is the **authority-side custody of one person's military service and of the entitlement chain decided by reference to it**: personnel and separation records held by the issuing service or records office, and claim, board, appeal, and veteran-programme files whose eligibility reasoning cites a service period, a service event, or a character-of-service determination.

Everything else that a "defence and veterans' affairs" portfolio would naively sweep in was routed to an existing sibling, because it is genuinely already covered there. The row survives on what does not decompose.

## The charge — the strongest case that this row should not exist

I ran the charge before writing anything, and most of it lands.

**1. It is an organisation name.** "Defence" and "Veterans' Affairs" are the names of ministries and departments. The government anchor already forbids exactly this as sole evidence: its `never_alone` opens with "a government department, regulator, municipality, legislature, court, public school, archive, museum, or official-looking seal alone". A row whose only distinguishing evidence is which department's letterhead is on the page can never activate, and the brief names that failure explicitly. This is the single most dangerous reading of the row and it must be defeated by structure, not by branding.

**2. It is a portfolio, and every part of the portfolio is a duplicate.** I decomposed the row honestly against the 31 landed `government.*` siblings on the roster:

| Naive coverage | Where it actually belongs |
|---|---|
| buying tanks, fuel, estates, IT | `government.public-procurement` — buyer-side procurement is procurement |
| defence white papers, strategy, alliance agreements | `government.policy-development` |
| military hospital and veteran clinic operations | `government.public-health-administration` |
| deposited historical service records, muster rolls | `government.archives-recordkeeping` |
| defence-ministry committee cycles, budgets, audit | `government.public-authority-record` |
| civil-emergency use of military assets | `government.emergency-management` |
| contractor-side everything | `business_operations` |
| a veteran's benefit letter, ID card, pension statement | `identity.core-documents`, `finance.*`, Protected Records |
| veterans' charities, posts, associations | `nonprofit.member-association` |

That table is most of the row. If nothing survived it, this should have been a refusal.

**3. It is a work_type family.** "Discharge record", "posting order", "medal citation" are values, not nodes — and the assignment prompt is explicit that work types are values on a field.

**4. It is a lifecycle stage.** "Veteran" is arguably just "after discharge" — the same person, later. A row defined by a stage of one continuous record is not a node.

**5. It may be a duplicate of its own schema's default template.** The government anchor's deterministic list already contains an "authority-side decision record with labelled applicant or regulated-party slots, an application or case reference, a decision status, reasons, and an authorized-officer or office block". A veterans' rating decision *is* that shape. If that is all this row has, it is the default with a departmental name attached.

## Defeating the charge

Two things survive the decomposition, and neither is a name, a value, a stage, or the schema default.

**A. The service-identity slot family.** No other `government.*` sibling's recognition needs a repeated labelled family of *personnel identifier, rank or rate, branch and component, unit or establishment, dates of service, and type or character of service*, carried across a lifecycle of artifacts by the same issuing office. A planning permit case has an applicant and a site. A procurement file has a supplier and a lot. A statistical programme has a collection round. None of them has a person-centred career-length slot family that the authority itself maintains, and the anchor's decision-record signal does not describe one. This is a structural discriminator, not a vocabulary one — it is true of `Service Record Brief - SMITH JORDAN A - personnel file copy 2026-05.pdf` and false of every fixture in the anchor.

**B. The service-connection link.** This is the sharper of the two. In this world an entitlement decision derives its eligibility premise *from a personnel record held by a different authority about the same person, sometimes decades earlier*. `Rating Decision - file 12-345-678 - 2026-06-19.pdf` has a "reasons and bases" section that cites a service period and an in-service event to justify the award. No other government sibling has a decision whose eligibility premise is a personnel history in another public body's custody. This produces a grouping behaviour the schema default cannot express: a personnel record may become a member of an entitlement casefile group **without any fact crossing in either direction** — the claim member acquires no rank or unit, the personnel member acquires no entitlement. That is encoded as its own `grouping_reasons` entry.

Both are inferences from the artifact shapes below, not from any span in `00`; the node's `provenance` is `inference` for that reason.

## The node test, argued in all three legs

CONNECTION's rule is that a template exists only when its **detection signals**, its **recommended dimensions**, or its **privacy rules** differ from its schema's default. The government default template is the one serialized in `planning/domains/nodes/government.json`: it fires on legislature, rulemaking, authority-side decision, procurement, governance-cycle, statistics, election, case-management-export, and public-office mail structures; it recommends an empty `dimension_order` under PR-6; and it protects submissions and named-person casework at `potentially_sensitive`.

**Leg 1 — detection signals: DIFFER.** Eleven deterministic signals, of which the service-identity family, the separation determination with a certifying custody stamp, the service-connection link, the fitness/medical-board proceeding, the vetting adjudication, the deployment/muster/casualty administration, and the service-records custody workflow are all absent from the default's list. The default would either miss these files or accept them for the wrong reason (an authority name). The `never_alone` list also differs materially: it must defeat rank, unit, operation names, protective markings, and military-history furniture, none of which the default's `never_alone` addresses.

**Leg 2 — recommended dimensions: DO NOT DIFFER.** Both are empty. PR-6 leaves the government schema fieldless, and a template cannot branch on fields that do not exist. I state this plainly rather than manufacturing a difference: this leg fails, and the row is accepted on the other two. The prose recommendation is recorded in `template.why` — bounded proceeding or casefile first, then workflow stage, then work type, with the person never becoming a branch — and it is explicitly not serialized.

**Leg 3 — privacy rules: DIFFER.** The default's posture is "authority holdings may contain casework and submissions, so protect". This row adds three rules the default does not carry:

1. *Composite custody.* One service file can hold personnel, disciplinary, clinical, vetting, casualty, and entitlement material about the same person. A member packet may therefore carry medical, identity, and legal evidence that must **retain its own schema** rather than be absorbed by membership.
2. *Aggregation suppression.* Unit, posting, base, rotation, and deployment values are suppressed from cross-file semantic joining, because the exposure is the aggregate itinerary, not any single member. `Deployment Manifest - Operation TRIDENT - rotation 4.xlsx` is the fixture: each row is mundane, the workbook is not, and joining it to three other rotation files is worse still. No other government sibling has a rule where individually-safe values become unsafe by accumulation.
3. *Markings are observations.* Protective markings, caveats, and distribution statements are recorded literally and never become a handling class or a sensitivity result. Handling classes are P7's; the node records only `potentially_sensitive`.

Two legs of three differ, and the differing legs are the ones that change activation and safety behaviour. The node is accepted.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from `make_prompt.py government.defence-veterans`.
- `planning/00-database-agent-product-design.md` — read by targeted grep only, per the token instruction. Eight spans were pulled and each was grep-verified verbatim before use (residual library definitions; the extension routing rule; the session rule; the EXIF rule; the abstention rule; the dimension-order and parent-context rules; the two privacy rules). No span is paraphrased inside quote marks.
- `planning/domains/nodes/government.json` — the schema anchor and my measuring stick. Read in full; its key set, precondition idiom, and universal `facts_legal` set are reused deliberately.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — the depth calibration row named by the brief.
- `planning/domains/ROSTER.md` §4 lines 854–887 — the `gov.*` and `edadmin.*` fold table, which is how I established that the portfolio decomposes.
- `planning/domains/roster.json` — every edge id in the JSON was checked against the 358 roster ids programmatically, as were the `also_schema` values (`research` and `photos` both exist).

`grep -rl "government.defence-veterans" planning/domains/nodes/` returned nothing: no landed row has argued a boundary against me, so every boundary below is authored from this side and is a recommendation to R1c for the reciprocal half.

## Real document types behind the fixtures

The fixtures are modelled on named, real artifact families rather than invented forms: a service record brief or personnel summary; a permanent-change-of-station assignment order; a periodic performance evaluation or fitness report; a certificate of release or discharge carrying numbered blocks for component, separation authority, narrative reason, and character of service; a disability compensation claim with an agency intake stamp; a rating decision with an "evidence considered / decision / reasons and bases" structure; a statement of the case issued on appeal; medical-board proceedings with convening authority, findings, and recommendation; a clearance adjudication summary keyed to an investigation reference; a records request with a search record and a certification of reproduction. The node names these by function rather than by any one country's form number, because the same structures recur across services and jurisdictions and a form-number list would be a gazetteer this pass must not invent.

## Files considered and rejected

Naming what this row does **not** hold was the largest part of the work.

- **A veteran's own discharge certificate, medal citation, veteran ID card, award letter, or pension statement.** This is the most tempting false positive in the whole row, because it is the file most people actually have. The government anchor already routes it away: "a person's civil-status, immigration, identity, property, benefit, tax, health, education, or voter record merely because a public body issued it". Recipient copies go to `identity.core-documents`, finance, or Protected Records.
- **A resume, payslip, employment contract, or LinkedIn export showing military service.** Government as employer is not this schema — the anchor's `never_alone` says so directly. `career.employment-records`.
- **Defence contractor material** — proposals, drawings, test reports, security plans, invoices, even internal clearance trackers carrying a protective marking. Supplier-side custody is `business_operations`.
- **Military history, doctrine, memoirs, unit histories, campaign maps, wargame scenarios, re-enactment rosters, declassified archive scans.** These reproduce genuine orders and forms *verbatim*, which is why the marking and the vocabulary cannot be activation signals. Reading Inbox or `research`.
- **Basic-training graduation photographs, reunion pictures, memorial images, medal displays.** A photograph of a military subject is a photograph. Photos / One-Off Images.
- **Veterans' charity and post material** — newsletters, membership rolls, parade flyers, donor records. `nonprofit.member-association`.
- **Defence procurement in all its forms.** Rejected on principle: the portfolio name is not a discriminator, and accepting it here would have made this row a duplicate of `government.public-procurement`.
- **Live personnel or claims systems.** A system is not a file node. Only a bounded export with a readable manifest is represented, and manifests are inspected without unpacking.
- **A blank or subject-completed vetting questionnaire.** Without an investigation reference and an issuing security office it is a form, not an adjudication file.
- **Contacts exports** containing officers, adjudicators, or representatives. The design says contact data "should normally be privacy-protected rather than used to create folder proposals"; `contacts` was therefore left out of `file_kinds.source_types` entirely, which is a deliberate narrowing from the schema anchor's full list.

## The collision fixture

The required fixture is `Certificate of Release or Discharge - SMITH JORDAN A.pdf`. The *bytes are the same document* in two worlds.

- **Mine:** it carries a certification-of-true-copy stamp naming a custodian office, and a routing block bearing an entitlement file reference — it is sitting inside an adjudication file.
- **Not mine:** the veteran's own scan, saved from a portal or a filing cabinet, with no stamp, no custodian, no case reference. That is `identity.core-documents`, falling through to Protected Records.

What discriminates is **custody evidence, not content**: a stamp, a custodian office block, a register entry, or an internal file reference. Nothing about the form's own numbered blocks distinguishes the two, which is why no signal in this row is allowed to fire on the form alone.

A second, subtler collision is `Operation TRIDENT - Lessons Learned Case Study.pdf`: a study institute's paper that reproduces a real assignment order as an illustration. It contains ranks, units, an operation name, and an order — every surface feature of my strongest fixture. It has no personnel-identifier *slot*, no custody block, and no case reference, and it has a bibliography. It falls to Reading Inbox.

## Reciprocal boundaries

Nine mutexes are authored, each with the same fixture named on both sides. The reciprocal halves are recommendations for R1c, not edits to anyone's file.

1. **`government.social-services-casework`** — the decisive test is the *eligibility premise*, not the agency. Mine cites a service period, event, or character-of-service determination plus a personnel identifier; theirs cites means, household, residency, or a non-service disability. Fixture on both sides: `Rating Decision - file 12-345-678 - 2026-06-19.pdf` against an identically laid out general disability allowance decision. **Their half:** a decision whose reasons cite service should not be claimed by social-services casework merely because the layout matches.
2. **`government.constituent-casework`** — adjudicating custody versus an elected office's enquiry-and-response file. Fixture: `RE file 12-345-678 - further service records requested.eml` (adjudication mailbox to records custodian, mine) against the same file reference inside an on-behalf-of-a-constituent thread (theirs). **Their half:** a constituent office holding a copy of a rating decision does not become the adjudicator.
3. **`career.employment-records`** — holder role. Fixture on both sides: `Evaluation Report - SMITH JORDAN A - period ending 2025-11-30.pdf`. Mine needs an issuing personnel office or custodian stamp; theirs is the individual's own working copy. **Their half:** a personnel office's evaluation file is not a career record because the subject happens to own the corpus.
4. **`identity.core-documents`** — the collision fixture above, in both directions.
5. **`government.public-procurement`** — `Defence Estate Fuel Supply - Tender Evaluation 2026-14.xlsx` is theirs, and I say so in my own fixture list so the boundary is testable from my side. **Their half:** procurement should not release a defence tender to this row on the strength of the buyer's name.
6. **`medical.personal-health-records`** — `Medical Board Proceedings - fitness for duty - MEB-2026-118.pdf`. I claim only the board-proceeding structure; the clinical content keeps its own schema. **Their half:** medical should not suppress the board structure, and neither side may erase the other. This is a genuine two-schema file, recorded as `also_schema: medical` on the fixture rather than as an `also_holds_with` edge (see below).
7. **`nonprofit.member-association`** — `Disability Compensation Claim - received 2026-03-04 - file 12-345-678.pdf` with an agency intake stamp (mine) against an accredited representative's retained copy under a service-organisation cover (theirs).
8. **`legal`** — `Statement of the Case - appeal - file 12-345-678.pdf`. Mine is the administering authority's custody; Legal covers the claimant's own record, a practitioner's matter file, and public decisions read as reference. This is also the reciprocal seam with `legal.practice-matter-file`, whose landed memo already draws the practitioner-versus-party line; the edge is authored at schema level because the competing custody could be either the practitioner file or a personal legal record.
9. **`business_operations`** — `Clearance Adjudication Summary - investigation 2026-4471.pdf` issued by a government security office (mine) against a contractor's internal clearance tracker carrying the same protective banner (theirs).

## Neighbours considered that got no edge

- **`government.public-health-administration`** — veteran hospital and clinic *operations* are theirs outright; I claim only eligibility and board determinations, which is already covered by the `medical.personal-health-records` mutex. Adding a third medical edge would restate the same seam.
- **`government.archives-recordkeeping`** — deposited historical service records are theirs. My records-custody signal is deliberately scoped to an *operative* request-search-certify workflow, which is a live administrative act rather than an archival holding. If R1c finds the two genuinely compete over a single fixture, that is an easy addition; I did not manufacture one.
- **`government.public-authority-record`** — defence-ministry governance cycles are covered by the parent shape, not by this row.
- **`government.emergency-management`** — military assistance to civil authorities is theirs; I have no fixture that competes.
- **`finance.insurance-personal`** — a veteran's own pension or insurance statement is a recipient record already excluded by `never_alone`; no same-evidence competition survives.
- **`photos.*`** — the graduation photograph is excluded by `never_alone`, not by a mutex.

## Fields, dimensions, and proposed fields

`fields: []`, `proposed_fields: []`, `template.dimension_order: []`, `time_first: false`, `role_split: []`, `also_holds_with: []` — all intentional.

- PR-6 leaves the government schema fieldless and D1's deferral stands; the assignment's `inherited_field_keys` is empty. A template may reuse only fields its schema declares, so there is nothing to order.
- I mint no proposed fields. The concepts this world would need — a personnel or service reference, a claim or file reference, a service period, a character-of-service determination, a workflow stage — are exactly the sort of thing the anchor's own open question says must be adjudicated centrally rather than in children. Proposing them from a placeholder child would pre-empt that. They are stated as prose in `open_question` instead.
- `role_split` is empty for the same reason `legal.practice-matter-file` left it empty: the split I would want to express (the same person as serving member on the defence side and as claimant on the veterans-agency side) needs two different field keys to point at, and neither schema exposes any.
- `also_holds_with` is empty because a template cannot author schema-level coactivation. The genuine two-schema cases — medical, identity, legal, career, business_operations, research, photos — are recorded per-fixture as `also_schema`.

## Grouping without copied facts

Groups are bounded by an exact anchor: a personnel identifier plus issuing-office custody, a claim or file reference, a board reference, a programme and period, a request reference, or an operation and rotation reference. Membership creates no facts on the member. Two fixtures are marked `group_without_copying_facts: true` — the adjudication email, which joins its casefile by an exact reference while contributing nothing, and the portal screenshot, whose OCR yields only a partial reference and which may sit near a casefile without proving membership. This is the `HW 3.pdf` behaviour the assignment asks for: a file can join a neighbourhood without the neighbourhood's labels being written onto it.

## Open questions

**NJ-1 — Is the narrowing correct?** This row is scoped to authority-side service and entitlement custody, and the portfolio's other nine faces are routed to siblings. Alternatives: (a) ratify the narrowing as written; (b) let the row carry the whole defence portfolio and accept that it duplicates `government.public-procurement`, `government.policy-development`, `government.public-health-administration`, and `government.archives-recordkeeping`; (c) refuse the row and route the surviving core to `government.social-services-casework` plus Protected Records, accepting that the service-identity family and the service-connection link then have no home. I recommend (a) and consider (c) the honest fallback if R1c judges the two surviving discriminators too thin.

**NJ-2 — May the service-connection relationship be represented at all?** It is the row's strongest discriminator and also its most dangerous: an edge between a personnel record and a benefit decision asserts something about a named person. Alternatives: represent it only as an in-memory grouping reason with no persisted edge; persist it as a reviewable candidate edge with no copied facts; or forbid it and lose the discriminator. This cannot be settled from `00`.

**NJ-3 — If PR-6 is lifted, is any reference here destination-eligible?** A branch named for a claim reference or a person discloses that a claim exists, exactly as the landed legal memo argues for client names. Alternatives: no branch depth at all for this row; redacted display labels over local-only aliases; or user-confirmed depth only.

**NJ-4 — Who owns protective markings?** This node treats a marking as a literal observation. If P7 later defines a handling vocabulary, decide whether a marking may seed it automatically or must always be user-confirmed. This row asserts nothing beyond `potentially_sensitive` and must not be read as pre-empting that decision.

**NJ-5 — Aggregation suppression is a rule with no home.** "Individually safe values become unsafe in aggregate" is a privacy rule I have asserted for unit, posting, and deployment data on the strength of the fixtures, not of any design span. If the product has no mechanism for suppressing cross-file joining on a value class, this rule is currently unenforceable and should be recorded as a gap rather than as a satisfied requirement.

## Self-verification

- `python3 -m json.tool` parses the node file. Key set is identical to `government.json`'s twenty-seven keys, in the same order.
- All nine `collides_with` ids, all `also_schema` values, and the absorbed legacy id were checked programmatically against `planning/domains/roster.json` (358 ids). All present.
- All five `falls_through_to` names and the two `falls_through_if_inactive` values outside that list (Reading Inbox, Temporary Screenshots, Unsupported or Encrypted) are residual templates named in `00`'s residual-library paragraph.
- Every quoted span was verified with `grep -c` against `00` before it was written; each returned exactly one match. Eight distinct spans are quoted; none is paraphrased inside quote marks.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a fact. No threshold, count, score, or handling class appears anywhere in either file.
- Two files written, both mine. No roster, canonical-field, neighbour-node, `src/`, or SPEC file was touched.

# Domain ownership — concurrent teams

Two teams are writing rows into `planning/domains/nodes/` at the same time. This file is the claim
register. **Claim before writing; release when done.**

Format: `<domain_id> | <TEAM> | active|complete`

## Rules

1. An agent may edit only `planning/domains/nodes/<domain_id>.json` and
   `planning/domains/nodes/<domain_id>.research.md` for an id its team has claimed here.
2. Never claim or edit an id assigned to another team.
3. Never edit shared files: the roster, prompts, canonical fields, `src/`, shared logs, or another
   agent's node. Cross-row changes are recommendations to R1c, never edits.
4. Commit by explicit file path. Never a wildcard.
5. **Do not stash, rebase, pull, or reset while either team has uncommitted work.**
6. On completion, change `active` to `complete`.

## Claims

law_practice | OTHER-TEAM | complete
nonprofit | OTHER-TEAM | complete
logistics | OTHER-TEAM | complete
retail_hospitality | OTHER-TEAM | complete

resource_operations | CODEX | complete
creative.performing-practice | CODEX | complete
creative.client-engagement | CODEX | complete
creative.revision-round | CODEX | complete
creative.deliverable-handoff | CODEX | complete
creative.licensing-rights | CODEX | complete
creative.stock-asset-library | CODEX | complete
creative.graphic-design-project | CODEX | complete
creative.brand-identity | CODEX | complete
creative.uiux-product-design | CODEX | complete
creative.illustration | CODEX | complete
creative.typeface-font | CODEX | complete
creative.print-production | CODEX | complete
creative.interior-design | CODEX | complete
creative.architectural-visualisation | CODEX | complete
creative.fashion-collection | CODEX | complete
creative.film-production | CODEX | complete
creative.shoot-day-media | CODEX | complete
creative.post-production | CODEX | complete
creative.motion-graphics | CODEX | complete
creative.3d-asset | CODEX | complete
creative.game-art-asset | CODEX | complete
creative.music-session | CODEX | complete
creative.podcast-episode | CODEX | complete
creative.commissioned-shoot | CODEX | active
creative.film-production | CODEX | active
creative.shoot-day-media | CODEX | active
creative.post-production | CODEX | active

## Split history — the claim inverted once, read this before assuming

The first proposed split gave OTHER-TEAM {nonprofit, retail_hospitality, logistics,
resource_operations} and CODEX law_practice. The agreed split **inverted**: OTHER-TEAM takes
law_practice, CODEX takes resource_operations. Both teams had already dispatched against the first
split, so two ids were briefly contested. Outcome:

- **`law_practice`** — OTHER-TEAM's first agent was stopped before writing; the id was clean, and
  OTHER-TEAM now owns it under the agreed split. No residue.
- **`resource_operations`** — ⚠ **OTHER-TEAM's agent wrote `resource_operations.json` (28,857 B,
  16:21) before being stopped.** There is **no `.research.md`**. The JSON parses. It is an
  UNTRUSTED PARTIAL from a stopped agent, not finished work.
  **OTHER-TEAM did not delete it**, because deleting a file inside another team's claimed id is
  itself a prohibited edit and CODEX's own agent may have been mid-write on the same path.
  **Resolved by CODEX:** its assigned agent completed the JSON and authored the matching research
  memo. CODEX then reparsed the final JSON, checked every universal schema key, verified the
  J-DEPTH opening marker and memo ending, and cross-checked the paired verdict. The completed pair
  supersedes the stopped partial; the contamination history remains here for auditability.
- OTHER-TEAM's four are all `kind: schema` anchor rows. Anchors are written before their templates
  because every template's node test is measured against its schema's default template.
- Prior work by OTHER-TEAM is committed and pushed through the gist-debt clearance (64/64 rows at
  J-DEPTH) and the four anchors `hr`, `engineering`, `manufacturing`, `government`.

## Claims — OTHER-TEAM, 2026-08-26 (J-DEPTH completion run, 166 rows)

Claimed by explicit id below. CODEX's `resource_operations.*` and `creative.commissioned-shoot` are
excluded and untouched.

creative.ad-campaign | OTHER-TEAM | active
creative.book-manuscript | OTHER-TEAM | active
creative.content-marketing | OTHER-TEAM | active
creative.exhibition | OTHER-TEAM | active
creative.journalism-reporting | OTHER-TEAM | active
creative.periodical-issue | OTHER-TEAM | active
creative.printmaking-editions | OTHER-TEAM | active
creative.publishing-title | OTHER-TEAM | active
creative.screenplay | OTHER-TEAM | active
creative.short-form-writing | OTHER-TEAM | active
creative.sound-design | OTHER-TEAM | active
creative.submission-query | OTHER-TEAM | active
creative.theatre-production | OTHER-TEAM | active
creative.translation-project | OTHER-TEAM | active
engineering.aerospace-airworthiness | OTHER-TEAM | active
engineering.automotive-program | OTHER-TEAM | active
engineering.bill-of-materials | OTHER-TEAM | active
engineering.cad-model | OTHER-TEAM | active
engineering.change-order | OTHER-TEAM | active
engineering.civil-structural | OTHER-TEAM | active
engineering.commissioning-handover | OTHER-TEAM | active
engineering.drawing-package | OTHER-TEAM | active
engineering.electrical-schematic | OTHER-TEAM | active
engineering.embedded-firmware | OTHER-TEAM | active
engineering.industrial-design | OTHER-TEAM | active
engineering.invention-disclosure | OTHER-TEAM | active
engineering.material-specification | OTHER-TEAM | active
engineering.pcb-layout | OTHER-TEAM | active
engineering.process-plant-design | OTHER-TEAM | active
engineering.product-certification | OTHER-TEAM | active
engineering.project | OTHER-TEAM | active
engineering.prototype-build | OTHER-TEAM | active
engineering.requirements-specification | OTHER-TEAM | active
engineering.risk-analysis-fmea | OTHER-TEAM | active
engineering.simulation-analysis | OTHER-TEAM | active
engineering.stage-gate-review | OTHER-TEAM | active
engineering.standards-library | OTHER-TEAM | active
engineering.verification-validation | OTHER-TEAM | active
government.archives-recordkeeping | OTHER-TEAM | active
government.constituent-casework | OTHER-TEAM | active
government.defence-veterans | OTHER-TEAM | active
government.diplomatic-consular | OTHER-TEAM | active
government.education-accreditation | OTHER-TEAM | active
government.education-institution-governance | OTHER-TEAM | active
government.elections-administration | OTHER-TEAM | active
government.emergency-management | OTHER-TEAM | active
government.environmental-regulation | OTHER-TEAM | active
government.grant-programme-administration | OTHER-TEAM | active
government.housing-authority | OTHER-TEAM | active
government.international-development | OTHER-TEAM | active
government.legislative-record | OTHER-TEAM | active
government.library-administration | OTHER-TEAM | active
government.municipal-administration | OTHER-TEAM | active
government.museum-collection | OTHER-TEAM | active
government.parks-public-lands | OTHER-TEAM | active
government.permit-licensing | OTHER-TEAM | active
government.planning-application | OTHER-TEAM | active
government.policy-development | OTHER-TEAM | active
government.professional-regulator | OTHER-TEAM | active
government.public-authority-record | OTHER-TEAM | active
government.public-consultation | OTHER-TEAM | active
government.public-health-administration | OTHER-TEAM | active
government.public-procurement | OTHER-TEAM | active
government.public-records-foi | OTHER-TEAM | active
government.regulatory-rulemaking | OTHER-TEAM | active
government.school-district-administration | OTHER-TEAM | active
government.social-services-casework | OTHER-TEAM | active
government.statistical-programme | OTHER-TEAM | active
government.transport-authority | OTHER-TEAM | active
hr.compensation-planning | OTHER-TEAM | active
hr.dei-program | OTHER-TEAM | active
hr.employee-relations | OTHER-TEAM | active
hr.engagement-survey | OTHER-TEAM | active
hr.onboarding-offboarding | OTHER-TEAM | active
hr.org-design-headcount | OTHER-TEAM | active
hr.payroll-benefits-administration | OTHER-TEAM | active
hr.performance-cycle | OTHER-TEAM | active
hr.training-development | OTHER-TEAM | active
hr.workforce-analytics | OTHER-TEAM | active
hr.workplace-health-safety | OTHER-TEAM | active
law_practice.admission-cle | OTHER-TEAM | active
law_practice.appeals | OTHER-TEAM | active
law_practice.client-intake | OTHER-TEAM | active
law_practice.closing-binder | OTHER-TEAM | active
law_practice.conflicts-check | OTHER-TEAM | active
law_practice.contract-negotiation | OTHER-TEAM | complete
law_practice.conveyancing | OTHER-TEAM | active
law_practice.corporate-secretarial | OTHER-TEAM | active
law_practice.court-filing-record | OTHER-TEAM | active
law_practice.criminal-defence | OTHER-TEAM | active
law_practice.deadlines-diary | OTHER-TEAM | active
law_practice.depositions-testimony | OTHER-TEAM | active
law_practice.discovery | OTHER-TEAM | active
law_practice.due-diligence | OTHER-TEAM | complete
law_practice.engagement-terms | OTHER-TEAM | active
law_practice.estates-administration | OTHER-TEAM | complete
law_practice.evidence-exhibits | OTHER-TEAM | active
law_practice.expert-materials | OTHER-TEAM | active
law_practice.family-law | OTHER-TEAM | active
law_practice.hearing-transcripts | OTHER-TEAM | active
law_practice.immigration-casework | OTHER-TEAM | active
law_practice.investigation | OTHER-TEAM | complete
law_practice.ip-prosecution | OTHER-TEAM | active
law_practice.legal-research | OTHER-TEAM | active
law_practice.matter-correspondence | OTHER-TEAM | active
law_practice.motions-and-briefs | OTHER-TEAM | active
law_practice.opinions-advice | OTHER-TEAM | active
law_practice.orders-and-judgments | OTHER-TEAM | active
law_practice.pleadings | OTHER-TEAM | active
law_practice.precedent-bank | OTHER-TEAM | active
law_practice.pro-bono | OTHER-TEAM | active
law_practice.regulatory-submission | OTHER-TEAM | complete
law_practice.settlement | OTHER-TEAM | complete
law_practice.time-and-billing | OTHER-TEAM | active
law_practice.transactional-deal | OTHER-TEAM | active
law_practice.trial-preparation | OTHER-TEAM | active
logistics.customs-export | OTHER-TEAM | active
logistics.driver-compliance | OTHER-TEAM | active
logistics.fleet-vehicle | OTHER-TEAM | active
logistics.last-mile-pod | OTHER-TEAM | active
logistics.route-dispatch | OTHER-TEAM | active
logistics.shipment | OTHER-TEAM | active
logistics.warehouse-ops | OTHER-TEAM | active
manufacturing.asset-register | OTHER-TEAM | active
manufacturing.calibration-record | OTHER-TEAM | active
manufacturing.energy-audit | OTHER-TEAM | complete
manufacturing.environmental-compliance | OTHER-TEAM | active
manufacturing.failure-analysis | OTHER-TEAM | active
manufacturing.field-service-report | OTHER-TEAM | active
manufacturing.hse-incident | OTHER-TEAM | active
manufacturing.inspection-record | OTHER-TEAM | active
manufacturing.maintenance-work-order | OTHER-TEAM | active
manufacturing.nonconformance-capa | OTHER-TEAM | active
manufacturing.production-planning | OTHER-TEAM | active
manufacturing.production-record | OTHER-TEAM | active
manufacturing.quality-management-system | OTHER-TEAM | active
manufacturing.safety-case | OTHER-TEAM | active
manufacturing.spare-parts | OTHER-TEAM | active
manufacturing.supplier-qualification | OTHER-TEAM | active
manufacturing.tooling-fixture | OTHER-TEAM | active
manufacturing.warranty-claim | OTHER-TEAM | active
manufacturing.work-instruction | OTHER-TEAM | active
nonprofit.advocacy-campaign | OTHER-TEAM | complete
nonprofit.fundraising-donor | OTHER-TEAM | active
nonprofit.governance | OTHER-TEAM | active
nonprofit.grant-reporting | OTHER-TEAM | complete
nonprofit.member-association | OTHER-TEAM | active
nonprofit.political-campaign | OTHER-TEAM | active
nonprofit.religious-institution | OTHER-TEAM | active
nonprofit.standards-body | OTHER-TEAM | active
nonprofit.trade-union | OTHER-TEAM | active
nonprofit.volunteer-management | OTHER-TEAM | active
retail_hospitality.bookings-reservations | OTHER-TEAM | complete
retail_hospitality.catering-contract | OTHER-TEAM | active
retail_hospitality.ecommerce-ops | OTHER-TEAM | active
retail_hospitality.event-production | OTHER-TEAM | active
retail_hospitality.food-safety | OTHER-TEAM | complete
retail_hospitality.guest-feedback | OTHER-TEAM | active
retail_hospitality.menu-recipe-costing | OTHER-TEAM | active
retail_hospitality.pos-reporting | OTHER-TEAM | active
retail_hospitality.premises-licensing | OTHER-TEAM | active
retail_hospitality.product-catalogue | OTHER-TEAM | active
retail_hospitality.returns-warranty | OTHER-TEAM | active
retail_hospitality.stocktake | OTHER-TEAM | active
retail_hospitality.store-operations | OTHER-TEAM | active
retail_hospitality.supplier-order | OTHER-TEAM | active

## Handover — OTHER-TEAM releases 8 ids to CODEX, 2026-08-27

CODEX claimed a 16-row, two-hour block (four waves of four). Checked before agreeing:

- **No overlap with OTHER-TEAM's running dispatch** — its live shard holds 22 rows and none of the
  16 is among them. CODEX's own no-overlap claim is confirmed, not assumed.
- **None of the 16 has files on disk**, so no duplicate work is being started.
- **But 8 of the 16 were registered `OTHER-TEAM | active`** under the 2026-08-26 166-id claim.
  Those rows sat in wave-2 shards 1 and 2, which were stopped at Joseph's instruction with
  **0 rows written**, so nothing is lost by releasing them. They are released below.

The 8 released (were OTHER-TEAM, now CODEX):

logistics.shipment | CODEX | active
logistics.customs-export | CODEX | active
logistics.route-dispatch | CODEX | active
logistics.last-mile-pod | CODEX | active
manufacturing.production-planning | CODEX | active
manufacturing.work-instruction | CODEX | active
manufacturing.tooling-fixture | CODEX | active
manufacturing.quality-management-system | CODEX | active

The other 8 (`resource_operations.*`) were already CODEX's and were excluded from OTHER-TEAM's
claim from the start; they are restated here as `active` for this block:

resource_operations.utility-metering-billing | CODEX | active
resource_operations.renewable-generation | CODEX | active
resource_operations.grid-connection | CODEX | active
resource_operations.oil-gas-operations | CODEX | active
resource_operations.mining-operations | CODEX | active
resource_operations.farm-records | CODEX | active
resource_operations.fisheries-catch | CODEX | active
resource_operations.forestry-records | CODEX | active

**OTHER-TEAM will not write, edit, or commit any of these 16 ids** while this block is open, and
will not delete a stray file inside them (rule 2 — report instead). `creative.commissioned-shoot`
and the remaining unclaimed rows stay outside the block until both teams recompute after the 16.

⚠ Note for whoever commits next: OTHER-TEAM commits **by explicit file list**, so CODEX's files are
never swept in — but a `git add planning/domains/nodes/` wildcard from either side would cross the
boundary. Do not use one.

## Claims — OTHER-TEAM, 2026-08-27 (16 unassigned rows, wave 3)

Picked by recomputing from the roster, then excluding CODEX's active 16-row block, the
`resource_operations` family, and `creative.commissioned-shoot` (held outside per CODEX's note).
Spread four-per-family so no shard hammers one schema anchor.

law_practice.motions-and-briefs | OTHER-TEAM | active
manufacturing.asset-register | OTHER-TEAM | active
nonprofit.member-association | OTHER-TEAM | active
retail_hospitality.product-catalogue | OTHER-TEAM | active
law_practice.orders-and-judgments | OTHER-TEAM | active
manufacturing.spare-parts | OTHER-TEAM | active
nonprofit.volunteer-management | OTHER-TEAM | active
retail_hospitality.supplier-order | OTHER-TEAM | active
law_practice.expert-materials | OTHER-TEAM | active
manufacturing.field-service-report | OTHER-TEAM | active
nonprofit.standards-body | OTHER-TEAM | active
retail_hospitality.pos-reporting | OTHER-TEAM | active
law_practice.trial-preparation | OTHER-TEAM | active
manufacturing.hse-incident | OTHER-TEAM | active
nonprofit.governance | OTHER-TEAM | active
retail_hospitality.returns-warranty | OTHER-TEAM | active

## OTHER-TEAM committed 4 CODEX rows, 2026-08-27 — at Joseph's instruction

Joseph asked OTHER-TEAM to commit CODEX's outstanding work so the branch could be pushed. This
overrides the undertaking recorded above ("OTHER-TEAM will not write, edit, or commit any of these
16 ids"). Recorded here so CODEX is not surprised to find its rows already in history.

Committed: `resource_operations.grid-connection`, `.oil-gas-operations`, `.renewable-generation`,
`.utility-metering-billing`.

Verified before staging: JSON + memo both present, all four parse, all four idle ~3 hours (not
mid-write). **Content was not edited.** Two memos — `grid-connection` and `oil-gas-operations` —
are missing the `Depth: J-DEPTH` header line; they were committed as their author left them.
**CODEX should add those headers**; OTHER-TEAM did not, because editing inside another team's claim
is the rule that still stands.

The remaining 12 ids of CODEX's block are still unwritten and remain CODEX's.

## Claims — OTHER-TEAM, 2026-08-27 (Cursor wave — finish remaining OWNED owed rows)

Recomputed owed (JSON+memo both required). Excluded every id still registered to CODEX's open
block (`creative.commissioned-shoot`, the four `logistics.*`, the four released `manufacturing.*`,
and the four remaining `resource_operations.*`). Claiming the 16 OTHER-TEAM can write:

law_practice.contract-negotiation | OTHER-TEAM | complete
law_practice.due-diligence | OTHER-TEAM | complete
law_practice.estates-administration | OTHER-TEAM | complete
law_practice.investigation | OTHER-TEAM | complete
law_practice.legal-research | OTHER-TEAM | active
law_practice.regulatory-submission | OTHER-TEAM | complete
law_practice.settlement | OTHER-TEAM | complete
manufacturing.energy-audit | OTHER-TEAM | complete
nonprofit.advocacy-campaign | OTHER-TEAM | active
nonprofit.grant-reporting | OTHER-TEAM | complete
nonprofit.trade-union | OTHER-TEAM | active
retail_hospitality.bookings-reservations | OTHER-TEAM | complete
retail_hospitality.catering-contract | OTHER-TEAM | active
retail_hospitality.food-safety | OTHER-TEAM | complete
retail_hospitality.premises-licensing | OTHER-TEAM | active
retail_hospitality.store-operations | OTHER-TEAM | active

⚠ Two are JSON-only partials from stopped agents: `law_practice.estates-administration` (landed
JSON, refuse=false, no memo) and `nonprofit.advocacy-campaign` (landed refusal JSON, no memo).
Salvage = write the matching `.research.md` (and only edit the JSON if it fails parse / contract).
Do **not** reverse `advocacy-campaign`'s argued refusal — it is one of the five nonprofit refusals
R1c must settle at the family level.

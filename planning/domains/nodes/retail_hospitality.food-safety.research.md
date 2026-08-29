# Research memo — `retail_hospitality.food-safety`

Depth: J-DEPTH
Date: 2026-08-27
Output: `planning/domains/nodes/retail_hospitality.food-safety.json`
Roster row: template on the fieldless `retail_hospitality` schema, `parent_id: null`, `launch: placeholder`

## Result

Accept the node. It survives the charge on all three legs of the CONNECTION §2 test. The dimensional leg is real but conditional (control point), and that conditionality is recorded as NJ-RH-FS-1 rather than smoothed over.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `also_holds_with: []`, `role_split: []`, `time_first: false`. Eleven `collides_with` entries, all written as objects naming a fixture on both sides.

## The charge — the strongest case that this row should not exist

I put six prosecutions to the row before writing anything. Three of them are serious.

**1. It is a work_type value.** This is the strongest charge and it is made by the schema itself. `retail_hospitality.json` lists, in `work_types[]`, verbatim: `"food safety record - temperature and probe log, cleaning schedule, delivery check, traceability and batch record, incident and corrective-action note"`. Every artefact I would claim is enumerated there as a *value* of a function dimension. The schema also wrote its own never-alone rule against exactly this move: a document-type word standing alone is the default template wearing a name. If `food-safety` is the phrase "temperature log" promoted to a node, the row is the 574's original mistake reproduced inside a family that already warned against it.

**Defeat.** The charge conflates the *documents* with the *situation*. A work_type value files a temperature log as one document of one type. What this row recognises is a **statutory diary pack**: a continuous, contemporaneous obligation whose output is structurally never one document. The minimum readable unit spans dissimilar artefacts — ruled probe sheets, food-contact cleaning schedules, delivery acceptance checks with temperature-on-arrival, batch-to-use TRACEABILITY pages, and incident notes — joined because an inspector or the operator asks for *the evidence that food was handled safely*, not for one form. No other sibling in this family requires that multi-class pack to be intelligible: a Z-read is complete on its own, a booking confirmation is complete on its own, a licence grant is complete on its own. The schema's own `grouping_reasons` do not name this pack explicitly, but its `recognition.deterministic` already isolates a DAILY-SIGNED-CHECK structure as something a generic company never files; this template is the organisational situation that structure belongs to, not a restatement of the document list.

**2. It is a duplicate of the schema's default template.** The schema's `recognition.deterministic` already contains a DAILY-SIGNED-CHECK signal, and the schema's exemplar fixture is literally `Fridge temps March.jpg`. If the family already detects daily signed checks, what does the template add?

**Defeat — detection alone would be too thin; the row passes on dimensions and privacy, with detection as a narrowing.** The schema's detection list is a family-level OR of many structures; owning one branch of an OR is not by itself a template (the stocktake memo made the same honest concession). This row sharpens DAILY-SIGNED-CHECK to **reading-against-tolerance on a food-control object**, adds the TRACEABILITY chain and the DELIVERY-ACCEPTANCE (temperature-on-arrival) signal the schema's order-cycle does not own, and — decisively — inserts a CONTROL POINT level and inverts the family's guest-primary privacy posture. If NJ-RH-FS-1 resolves against the control-point level, the dimensional leg fails and the row would rest on pack-grouping and privacy alone. It would still stand, but by a thinner margin.

**3. It is `retail_hospitality.store-operations` opening checks.** Both are recurring signed grids filed at a site.

**Defeat.** A general opening pack (`Opening checks March - Camden.pdf`) may contain one fridge line among lights, till float and door locks; that pack's purpose is premises readiness and belongs to store-operations when that sibling lands. This row fires when the sheet's *rows are majority food-control objects with tolerances* — Fridge 1, Walk-in, Hot hold, Probe, food-contact surfaces. A minority fridge line may JOIN a diary group without copying facts; it must not promote the whole pack. Reciprocity is owed when store-operations lands (NJ-RH-FS-2).

**4. It is `business_operations.compliance-audit` or the hygiene inspection report.** Checklist + statutory character.

**Defeat, and the neighbour already drew half of this.** Compliance-audit owns an assessment occurrence with a party structurally distinct from the party assessed. This row owns the operative's own contemporaneous diary that an inspection *pulls from*. The shared fixture `Food hygiene inspection report - 12 Feb 2026.pdf` looks like food-safety and is not this row's primary claim — see collision with premises-licensing and NJ-RH-FS-3.

**5. It is pharmacy cold chain / facilities cleaning / manufacturing CAPA wearing kitchen words.**

**Defeat by stock protected and structure.** Medicines cold-chain with CD/dispensary apparatus is pharmacy; premises cleaning and contractor logs are facilities; factory NCR/CAPA is manufacturing. A kitchen fridge grid, food-contact cleaning diary, and fridge-failure incident note are this row's. Temperature grids alone discriminate none of these — encoded in `never_alone` and in the pharmacy edge.

**6. It is a row defined by absence** (food that was *unsafe*). Rejected quickly: a period of perfect probe passes is still a diary, and the row's strongest signal is reading-against-tolerance structure, not failure.

## The node test, all three legs

CONNECTION §2: a template exists only where its **detection signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default.

**The schema's default template, stated so the difference is measurable.** `retail_hospitality.json` holds it as prose because PR-6 leaves the family fieldless: the TRADING UNIT (conditional), then the TRADING OCCASION, then the OPERATIONAL RECORD FUNCTION; trading period inside the occasion; NOT TIME-FIRST.

**Leg 1 — detection. Differs by narrowing plus two additions.** The family signal is DAILY-SIGNED-CHECK. This row sharpens it to reading-against-tolerance on a named CONTROL POINT, with corrective-action and initials. It adds TRACEABILITY (batch → use-by → use-out/disposal) and DELIVERY-ACCEPTANCE (temperature-on-arrival + accept/reject), which are not the schema's order-cycle and not a stocktake variance. Constitutional never-alone: food-safety vocabulary words alone never fire.

**Leg 2 — dimensions. Differs by one inserted level.** Recommendation: trading unit (conditional) → **control point** → record period → function. The control-point level is the entire difference: a diary is executed as simultaneous readings of disjoint equipment — Fridge 1, Walk-in, Hot hold A, Probe 3 — each with its own sheet and initials. Flattening puts four unrelated ruled sheets in one pile at the moment the user asks which unit failed. The level is conditional for the same reason the site level is (`00` validator sentence against one-child and collector levels). Forbidden: product/dish branches; operative-name branches. `time_first: false` — the date identifies the entry; a photograph's capture date is not the trading date; the photos exception stays with media.

**Leg 3 — privacy. Differs by inversion.** The family's posture exists for guest personal data at volume. An ordinary food-safety corpus names almost no guests. What it carries instead is staff-facing missed-check and incident data, occasional illness/allergen medical-adjacent guest content, and regulatory evidence that must stay local by default. Sensitivity is `potentially_sensitive`; no handling class.

Verdict: three legs, two of them decisive, one honest-but-conditional. Accept.

## Sources used

`planning/domains/dispatch/RESEARCH-BRIEF.md`; the stamped assignment via `python3 planning/domains/dispatch/make_prompt.py retail_hospitality.food-safety`; `planning/domains/nodes/legal.practice-matter-file.research.md` as the depth calibration; `planning/domains/nodes/retail_hospitality.json` (the schema anchor — `template`, `recognition`, `work_types`, `grouping_reasons`, `never_alone`, `sensitivity_why`, `falls_through_to`, `proposed_fields`, `file_examples`); `planning/domains/roster.json` (sibling ids and neighbour-id verification); single greps into already-landed neighbours that had argued a boundary touching this material — `business_operations.compliance-audit.json`, `clinical_practice.pharmacy-operations.json`, `retail_hospitality.stocktake.research.md` (explicit non-edge), `retail_hospitality.supplier-order.json` (delivery variance), `hr.workplace-health-safety.json`; and `planning/00-database-agent-product-design.md` reached only by targeted grep. Every `00` quotation in the JSON and this memo was `grep -F`-verified verbatim before use. No design cite is attached to the node itself: `design_cite` is `null` because no span of `00` names this situation.

The `.research.md` of the schema anchor was **not** opened. The JSON settled the node test without it.

## Files considered and rejected

Named false positives, each with the reason it is not this row's evidence.

- **`Food hygiene inspection report - 12 Feb 2026.pdf`** — THE COLLISION FIXTURE. Authority letterhead, rating, contravention schedule. Looks like food-safety because it is about hygiene. It is an assessment / permission outcome; this row owns the diary beside it, not the report bytes. Contested home between premises-licensing and compliance-audit's earlier hand-off (NJ-RH-FS-3).
- **`Opening checks March - Camden.pdf`** — daily signed grid that is mostly premises readiness with one fridge line. Store-operations pack; fridge line may join without promoting the pack.
- **`Fridge temps - CD cabinet - March 2026.pdf`** — temperature grid protecting medicines under a controlled-drugs cabinet. `clinical_practice.pharmacy-operations`.
- **`Delivery note 2026-03-28 - Brakes - 2 lines short.pdf`** — quantity shortage under an order reference. `retail_hospitality.supplier-order`. Temperature-on-arrival without shortage columns is this row's instead.
- **`Blank temperature log - FSA style.pdf`** — specimen form, no readings, no site, no period. Independent Records. Purpose without contemporaneous diary does not activate.
- **`Allergen matrix - Spring menu.xlsx`** — items × allergen grid built with costing. `retail_hospitality.menu-recipe-costing`. A signed allergen *control check* would be this row's; the matrix is not.
- **`Fire Risk Assessment - 14 Mill Street - 2026.pdf`** — assessment-instrument slots. `hr.workplace-health-safety`.
- **`Kitchen deep clean - contractor invoice.pdf`** — premises services / facilities administration, not a food-contact diary.
- **`Stock count W12 2026 - counted vs system.xlsx`** — count-versus-book. `retail_hospitality.stocktake`. Stocktake's memo already recorded the non-edge: reading-against-tolerance versus quantity-against-book.
- **`Food safety archive 2019-2024 - password protected.zip`** — never-alone words in a filename over an unreadable container. Unsupported or Encrypted. Must not be opened to classify it.
- **A photographed plated dish or fridge interior with no ruled sheet** — photos evidence until a diary structure claims it.
- **A live food-safety SaaS or EPOS compliance module** — a source system, not a file node. Only a bounded export with a readable manifest is represented.

## `proposed_fields` justification

There are none, deliberately. The schema owns the fields and declares none under PR-6 as D1 narrowed it; a template may only reuse what its schema declares, and this one declares nothing. Minting `control_point`, `check_class`, `diary_period` or `ccp` here would create exactly the second copy of the schema the contract forbids. Intent for R1c is in NJ-RH-FS-5: if PR-6 is lifted, want the schema's already-proposed `site` plus control-point and diary-period concepts — as concepts, not as keys minted here.

## Neighbours considered that did not get an edge

- **`retail_hospitality.stocktake`** — shares the kitchen, the fridge and photographed paper sheets. Discriminator is total: reading-against-tolerance versus quantity-against-book. Evidentially disjoint; stocktake's memo already recorded the non-edge. No mutex.
- **`retail_hospitality.pos-reporting`** — till reconciliation. No shared fixture that reads as both.
- **`logistics`** — movement/consignment identity. Delivery acceptance here is keyed to temperature and accept/reject at the operator's bay, not to carriage discharge. Schema-level logistics seam already covers inbound goods; no additional template mutex needed beyond supplier-order.
- **`finance`** — no ordinary join; a food-safety pack is not a ledger. Schema-level finance coactivation stays on the anchor.
- **`photos`** — photographed clipboard sheets are image evidence; capture facts remain photos'. Intent for schema-level `also_holds_with` is NJ-RH-FS-4; templates must not author schema↔schema edges.

## The collision fixture

`Food hygiene inspection report - 12 Feb 2026.pdf`. It carries hygiene vocabulary, a premises address, a rating and corrective deadlines — exactly the language that tempts this row. It is not this row's primary file. What discriminates: an external determination with a rating/contravention schedule is premises-licensing (operator's permission outcome) / government (authority custody) / not-compliance-audit (that row already refused the statutory food-hygiene scheme); this row owns `Fridge temps March.jpg` and the signed diary the report may cite. Same bytes named on both sides of the premises-licensing and compliance-audit edges.

A second, cleaner same-family fixture: `Delivery check - Brakes 28 Mar 2026 - temps on arrival.pdf` versus supplier-order's `Delivery note 2026-03-28 - Brakes - 2 lines short.pdf` — temperature acceptance versus quantity shortage.

## Recommendations for R1c (not applied — no neighbour file was touched)

1. `retail_hospitality.store-operations`, when it lands, must state the opening-checks seam in the same words: majority food-control rows decide for this row; a minority fridge line inside a premises-readiness pack decides for store-operations.
2. `retail_hospitality.premises-licensing`, when it lands, must claim `Food hygiene inspection report - 12 Feb 2026.pdf` as permission/rating outcome and leave the diary pack to this row — or R1c must overturn this row and compliance-audit's hand-off together (NJ-RH-FS-3).
3. Schema-level coactivation with `government` and `photos` belongs on `retail_hospitality`, not here (`also_holds_with` is schema↔schema only).

## NEEDS-JOSEPH

- **NJ-RH-FS-1** — CONTROL POINT level: conditional (A, this row's proposal) vs drop (B). If B, dimensional leg fails.
- **NJ-RH-FS-2** — mixed opening-checks pack: store-operations owns with fridge line joining (A) vs any food-control line promotes the pack here (B). Proposes A.
- **NJ-RH-FS-3** — home of the food hygiene inspection report bytes among this row, premises-licensing, and compliance-audit's earlier assignment to this id. Proposes premises-licensing for the report, this row for the diary beside it.
- **NJ-RH-FS-4** — schema-level `also_holds_with` intents (government custody split; photos for clipboard captures) cannot be recorded on a template.
- **NJ-RH-FS-5** — if D1/PR-6 lifted, fields wanted as concepts only; no key minted here.

## Self-verification

`python3 -m json.tool` parses the node. Key set matches landed siblings (`also_holds_with`, `collides_with`, `design_cite`, `falls_through_to`, `fields`, `file_examples`, `file_kinds`, `grouping_reasons`, `id`, `kind`, `launch`, `name`, `one_line`, `open_question`, `parent_id`, `proposed_fields`, `provenance`, `recognition`, `refuse_node`, `refuse_reason`, `role_split`, `schema_id`, `sensitivity`, `sensitivity_why`, `template`, `work_types`). Every `file_examples.source_type` is drawn from `SOURCE_TYPES`. Every `collides_with` entry is an object with `domain`, `signal` and `provenance`, and every `domain` was confirmed present in `roster.json`. Every `falls_through_to.residual_template` is one of `00`'s residual names (plus Temporary Screenshots as used by landed siblings). Every quotation was grep-verified verbatim in `00` before it was written. No thresholds, no handling classes, no confidence scores. `fields`, `proposed_fields`, `dimension_order`, `also_holds_with` and `role_split` are all empty by contract. Only the two assigned files were written. Do not commit (per assignment).

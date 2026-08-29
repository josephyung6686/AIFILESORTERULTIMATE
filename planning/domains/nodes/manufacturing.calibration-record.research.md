# Research memo — `manufacturing.calibration-record`

Date: 2026-08-27
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.calibration-record.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, placeholder launch

## Result

Accept the node. Its distinct job is to recognise the one manufacturing situation whose measured object is not a product but the measuring instrument itself, and to anchor that evidence on a controlled instrument rather than on a product or a lot.

The decisive structure is one no neighbour carries: an **as-found** value set paired with an **as-left** value set, joined to a **traceability statement** and a **next-due date**. That pair is not a stylistic marker. It encodes the property that makes the row necessary: a calibration record is retroactively load-bearing. When an instrument is found out of tolerance as-found, every measurement it produced since its previous certificate becomes suspect, and the certificate becomes a back-reference hub over a population of already-filed inspection records. No other manufacturing record reaches backwards that way.

## Binding material read

The standing brief; the stamped assignment from `make_prompt.py`; the schema anchor `manufacturing.json`; the landed sibling `manufacturing.inspection-record.json`; `legal.practice-matter-file.research.md` as depth calibration; `roster.json` (358 `domain_id` rows). `00` was read by targeted grep under the token instruction. Three spans were grep-verified verbatim before use and no others are quoted anywhere:

- "The recommendation should follow the practical rule that a parent dimension should provide the context required to understand the child."
- "For document and record domains, project, function, or subject usually comes before time because putting year first scatters related work across calendar folders."
- "A session should never be treated as proof of topic"

Top-level `design_cite` is `null`: `00` does not license this row's existence, only its dimension reasoning, which is where the quotes sit.

## THE CHARGE — the case that this row should not exist

Seven counts, stated at full strength. Four are serious and one is documented in the row's own schema file.

1. **It is a work_type value on its own schema.** Not hypothetical: `manufacturing.json`'s `work_types` literally contains `"calibration certificate, calibration result or instrument history"`. The brief is explicit that work types are values, not nodes. On its face this is a node minted for one enum entry — the 574's recorded failure.
2. **It is a document type.** "Certificate" is a document-type word, and the schema's own `never_alone` concedes "the word certificate alone never fires."
3. **It is a lifecycle stage of asset maintenance.** Calibration is one recurring preventive task in an asset's service cycle — i.e. `manufacturing.maintenance-work-order` with `record_type = calibration`, hanging off `manufacturing.asset-register`. The schema itself routes it there: its default prose says "site then asset then record type for maintenance **and calibration**" — one branch, both situations.
4. **It duplicates `manufacturing.inspection-record`.** Both sides are a table of measured values against stated limits, with per-row verdicts, an issuer, a certificate number and a signature. The sibling itself calls the pair "structurally near-identical documents."
5. **It is defined by an absence** — *not* a product measurement, *not* the register, *not* the procedure.
6. **Its most conspicuous marker is an organisation name.** What a human sees first is an accreditation mark and a laboratory or national-metrology-institute name — never-alone evidence.
7. **It duplicates its schema's default template**, whose prose already gives an asset-first order for the calibration branch.

### Defeating it

**Counts 1 and 4 fall together, on evidence already on the record.** A work_type is a leaf under a fixed anchor; a node becomes necessary when the *anchor itself changes*. Every other manufacturing work_type — traveller, genealogy, line log, inspection, nonconformance, work order — anchors on something the business makes or runs. Calibration anchors on a **measuring instrument**: a torque wrench, a bench balance, a load cell, a coordinate-measuring machine. It makes no product, appears in no bill of materials, belongs to no lot. The enum entry names the artifact; it cannot supply the anchor.

The precedent is landed and same-schema. `manufacturing.inspection-record` is *also* an entry in that same `work_types` array ("incoming, in-process or final inspection and test record") and was landed anyway, on exactly this ground — that "the schema default's product-then-lot parent chain cannot make it intelligible." If enum membership disqualified a row, that sibling would not exist.

Count 4 is answered by the neighbour rather than by me. `manufacturing.inspection-record.json` already argues the boundary: the discriminator is "which object the measurement is ABOUT… the measured object is the instrument itself, marked by as-found and as-left pairs and a next-due date, which no article inspection carries." It then **awards this row two named fixtures** — `Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf` and `Gage R&R Study - CMM-02 - operators A B C.xlsx` — and keeps `CMM_BPA-210-001_SN0004_2026-05-12.csv`. My boundary was conceded by the competing row, on named bytes, before I was dispatched; I mirror all three assignments rather than restate them.

**Count 3 is the closest call.** A maintenance work order records work performed to restore or preserve function, closed by return-to-service; its question is "does the machine run." A calibration record establishes a metrological state at an instant with a stated chain of traceability; its question is "can this instrument's numbers be believed, and for how long." Three checkable differences: a permitted-error table against applied reference values, a traceability statement to a recognised measurement standard, and the as-found/as-left pair. `Boiler service certificate - Plant 2.pdf` has a next-service date, an engineer's registration and a safe-to-use declaration and carries none of the three — which is why it sits in `file_examples` as the maintenance side's fixture on both sides of that edge.

Direction settles the rest. Maintenance is forward-looking. Calibration is bidirectional, and the backward leg has no analogue in the schema: an as-found failure retrospectively places a bounded population of *other files* in doubt. That is a grouping obligation, not a record-type attribute, and it is the single argument I would keep if only one were allowed.

**Count 7 fails on what is serialized.** The schema's serialized default is `dimension_order: []` and its prose primary is product → batch_lot → record_type; the prose then concedes two further branch shapes, one covering "maintenance and calibration" jointly. A default template is one order — it cannot be product-first and asset-first at once — so that note is an admission the calibration branch inverts the default, not proof that it is the default. Against the maintenance half of that shared branch, count 3 supplies the separation. This row also goes further than the prose by forbidding `product` and `batch_lot` from the chain entirely, which matters: one balance serves every product on site, and filing its certificate under a product would require inventing a product fact.

**Counts 2, 5 and 6 are conceded in part and encoded rather than argued away.** "Certificate", "calibration", "traceable" and "accredited" are all in `never_alone`, as is the accreditation-body count in its own entry — an organisation name "identifies the issuer of a document, never the holder's controlled instrument." Count 5 is wrong on the JSON: the recognition rules are positive co-occurrences (labelled instrument-identity slot, as-found with as-left, permitted-error criterion, traceability statement, due date). The negations in the one-line are boundary statements for a reader, not the activation rule.

**Verdict: accept** — on an anchor the schema cannot supply, a structure the nearest neighbour has already conceded on named bytes, and a backward-reaching grouping obligation that exists nowhere else in `manufacturing`.

## Node test, all three legs

**Leg 1 — detection signals.** The schema default fires on production, genealogy, inspection, nonconformance, work-order, register, line-log and HSE structures, with exactly one calibration clause. This row replaces that clause with eleven, and the discriminating ones have no counterpart in the default: as-found paired with as-left at each applied point; a reference master or artefact used to check the instrument; variance attributed to operators, gauges and trials rather than to parts; a due list carrying a per-instrument *outcome* column; an out-of-tolerance structure bounded by an interval and enumerating the measurements inside it; an uncertainty budget whose contributions are attributed to the measuring process. Its `never_alone` also carries an entry the schema does not — "an as-found value alone" — because as-found without as-left is just a measurement, a trap specific to this row.

**Leg 2 — dimension order.** The default's prose primary is product → batch_lot → record_type. This row is instrument asset → record function, `site` above only in a genuinely multi-site corpus, and product and batch_lot excluded outright. `00` licenses the inversion: "a parent dimension should provide the context required to understand the child." An as-found reading is unintelligible except under the instrument it was found on; under a product branch the product fact would have to be invented.

`time_first` is `false`, and the temptation is real — calibration is interval-driven and people do file certificates in year folders. It stays false because an instrument's chain (previous certificate → adjustment → current certificate → next due) is exactly the "related work" `00` warns that "putting year first scatters… across calendar folders."

**Leg 3 — privacy, and it is the weakest leg; I say so rather than inflate it.** The default's rationale is recipes, tolerances, yields, supplier lots and plant layouts. This row adds two exposures the default does not name: an instrument population plus its uncertainty budgets discloses a plant's *measurement capability*, and therefore the tolerances it can hold and the work it can bid for; and out-of-tolerance assessments are adverse quality evidence naming the lots placed in doubt. Both sit at `potentially_sensitive`, no handling class. Legs 1 and 2 carry the node on their own.

## Files considered and rejected

All appear in `file_examples`, so each rejection is testable rather than asserted.

- `Calibration procedure CP-014 rev 3.docx` — the purest false positive, since its filename is the row's own name. A document number, revision, approver and numbered steps addressed to an instrument *class*, with no serial and no measured value, is a controlled instruction: `manufacturing.quality-management-system`. Instance versus instruction.
- `CMM_BPA-210-001_SN0004_2026-05-12.csv` — names a coordinate-measuring machine, but carries nominal/actual/deviation triples for a part's features and no as-left set. The machine is provenance of the measuring act, not the subject. Stays with inspection-record, which has already claimed it.
- `Invoice - Metrology Services Ltd - Feb 2026.pdf` — line items literally say calibration; no serial slots, no readings, no due dates. It proves a transaction. Procurement, residual `Receipts and Confirmations`.
- `Boiler service certificate - Plant 2.pdf` — a certificate, an accredited engineer, a next date, and none of the three metrological markers. Function, not metrology.
- `Tachograph calibration certificate - VRN AB12 CDE.pdf` — the hardest rejection; kept as the collision fixture below.
- A general preventive-maintenance schedule — due dates and intervals are shared by every schedule in the schema and discriminate nothing.
- An instrument manual or datasheet — states a specification, which has no measured value, exactly as a material specification is not an inspection.
- A supplier's certificate of conformity travelling with delivered goods — letterhead resembles a calibration laboratory's, but its object is a consignment, not an owned instrument.
- A live calibration-management system, LIMS or instrument-software database — a source system, not a file node. Only a bounded export with a readable manifest is represented.
- Contact exports listing calibration laboratories and technicians — organisation and person names are never-alone evidence.
- Legal-metrology taxonomies, interval methodologies, uncertainty-evaluation frameworks — deferred; enumerating them would make a placeholder into the industry-depth catalogue J-IND forbids this round.

## The collision fixture

**`Tachograph calibration certificate - VRN AB12 CDE.pdf`.** It satisfies nearly every signal this row has: an approved workshop issuer with a workshop-card reference, a legally mandated periodic interval, a next inspection date, and values recorded before and after adjustment — a genuine as-found/as-left pair. On structure alone it is indistinguishable from a plant instrument certificate.

It is not this row's. The discriminator is the identity slot: the anchor is a **vehicle registration and identification number** under a road-transport enforcement regime, and it is filed with the vehicle, not in a plant's measuring population. The same test catches weighbridge and dispenser certificates, which is why NJ-CAL-3 exists. The `logistics.fleet-vehicle` edge names this file on both sides and gives it to logistics on both sides.

A softer second collision: `Thermocouple loop check TI-1042 - commissioning.pdf`, whose span-point table with as-found and as-left at each point is *identical* on both sides of the `engineering.commissioning-handover` edge. Only membership discriminates it — a turnover dossier index and a witness acceptance signature versus a recall interval and a reference to the previous certificate.

## Reciprocal boundaries

Eight `collides_with` entries, all objects, each naming one real file and resolving it identically in both directions.

| Neighbour | Shared fixture | Kept by |
|---|---|---|
| `manufacturing.inspection-record` | `Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf`; `Gage R&R Study - CMM-02 - operators A B C.xlsx` | this row (neighbour already conceded both) |
| `manufacturing.inspection-record` (reciprocal) | `CMM_BPA-210-001_SN0004_2026-05-12.csv` | inspection-record |
| `manufacturing.asset-register` | `Calibration due list 2026-Q4.xlsx` | split on presence of a per-instrument outcome column |
| `manufacturing.maintenance-work-order` | `Boiler service certificate - Plant 2.pdf` | maintenance-work-order |
| `manufacturing.quality-management-system` | `Calibration procedure CP-014 rev 3.docx` | quality-management-system |
| `manufacturing.nonconformance-capa` | `Out-of-tolerance impact assessment - LC-1142.pdf` | this row; the opened case file stays with nonconformance-capa |
| `engineering.commissioning-handover` | `Thermocouple loop check TI-1042 - commissioning.pdf` | split on dossier membership versus recall chain |
| `logistics.fleet-vehicle` | `Tachograph calibration certificate - VRN AB12 CDE.pdf` | logistics.fleet-vehicle |
| `business_operations.procurement-sourcing` | `Invoice - Metrology Services Ltd - Feb 2026.pdf` | procurement-sourcing |

The due-list split is the only one resolved by content rather than document identity, deliberately: the same workbook genuinely changes hands depending on whether its rows carry outcomes, so stating it as a column test is what makes it actionable for the validator.

All three `must_consider_neighbors` are covered at child granularity — `engineering` via commissioning-handover, `logistics` via fleet-vehicle, `business_operations` via procurement-sourcing. Child ids beat bare schema ids here because each collision is carried by a specific fixture, and an edge naming the fixture is worth more to P6 activation than one naming a schema.

## Neighbours considered that got no edge

- `manufacturing.production-record` — a traveller may mention "gauge G-207 used". A mention is not a competing claim on the certificate's bytes; the inspection-record edge already carries the confusable measurement evidence.
- `manufacturing.failure-analysis` — investigates why an article failed, not whether an instrument reads true. It competes only if an instrument is itself the failed article, at which point it is a product there.
- `business_operations.it-asset-inventory` — laptops and licences; overlap is the word "asset" only.
- `construction_property.compliance-certificate` — the schema anchor already argues plant-versus-building one level up, and the boiler instance is resolved on the maintenance edge; a second edge would duplicate it.
- `hr.training-development` — technician competence records are training evidence in their own right and do not contest the certificate.
- `research.lab-notebook-protocols` — pipette and balance calibration is real in laboratories, but that row's anchor is an experiment. Left un-edged deliberately; if a landed research sibling claims instrument certificates, R1c can add the reciprocal rather than have me invent it.

## Fields, and one deliberate non-proposal

`fields: []`, `proposed_fields: []`, `dimension_order: []` — all intentional.

`proposed_fields` is empty by decision, not omission. The obvious candidate is an `instrument` key; I did not propose it because the schema already proposes `asset`, and minting `instrument` beside it is exactly the synonym the dispatch forbids. A measuring instrument *is* an asset; what differs is its role, which is a role-split question for R1c (NJ-CAL-1), not a new key.

Others rejected: a calibration due date or status is a value that changes every cycle and is destination-ineligible — a folder level that goes stale is worse than none. `record_type` (schema-proposed) already covers calibration as a function value. `quality_event` is the schema's nonconformance anchor, and an out-of-tolerance assessment must not silently acquire one; the JSON's `must_not_conclude` says so. `site` is already schema-proposed.

`role_split` is empty for the reason `legal.practice-matter-file` left it empty: it requires different field keys and this schema serializes none.

`also_holds_with` is empty because CONNECTION §5 makes it schema ↔ schema only and this row is a template. **Coactivation intent recorded here for R1c:** a commissioning loop-check sheet can legitimately carry both `manufacturing` and `engineering` (the fixture marks `also_schema: engineering`), and a calibration invoice carries `finance` independently. Neither is a collision; neither may be authored as an edge from this row.

## Grouping without copied facts

Groups are bounded by an exact instrument identifier, a recall or dispatch identifier, or an archive manifest. Four fixtures carry `group_without_copying_facts: true` — the sticker photograph `IMG_2210.jpg` whose identifier is out of frame, the `.ics` recall event, the recall email, and the archive. These are this row's `HW 3.pdf` cases: they may join an instrument neighbourhood for review without any instrument fact being minted onto them, and the surrounding folder's identifier must not be copied in.

The out-of-tolerance back-reference is the sharpest constraint. An assessment may bind one instrument's interval to a population of inspection records as a reviewable candidate edge only; it must never write the instrument fact onto those records nor restate their measured values as findings. The hazard runs both ways and is stated on the `nonconformance-capa` edge too.

## NEEDS-JOSEPH

**NJ-CAL-1 — one `asset` key or a role split?** This row's asset is a measuring instrument that makes no product; asset-register and maintenance-work-order anchor on production assets that do. (a) One key, role carried by `record_type` — simplest, but "all my instruments" cannot be filtered; (b) a canonical role split on `asset`, mirroring the open `site`-versus-Photos-`location` question (NJ-MFG-3); (c) a distinct measuring-and-test-equipment key — rejected here as a synonym, but R1c may disagree. Recommend (b).

**NJ-CAL-2 — how does P9 record a backward candidate edge?** (a) A reviewable candidate edge with no fact propagation — recommended, and what the JSON assumes; (b) user-confirmed links only; (c) no edge, leaving the relation to search. Option (c) loses the property that most justifies this row.

**NJ-CAL-3 — legally mandated calibrations anchored elsewhere.** Tachograph, weighbridge and dispenser certificates carry every structural signal but anchor on a vehicle or trading instrument under an enforcement regime. (a) Leave them with `logistics.fleet-vehicle`, as the edge does — correct for tachographs, awkward for a weighbridge on the plant site; (b) admit them whenever the holder controls the instrument, weakening the plant-population anchor; (c) a separate legal-metrology situation later. Recommend (a) now; (c) is the likely eventual answer.

## Self-verification

JSON parses (`json.tool`). Key set identical and in order to the landed `manufacturing.json`. All 8 `collides_with` ids present in the roster's 358 `domain_id` set — zero bad ids. All 5 `falls_through_to` names among `00`'s nine residual homes — zero bad names. All 16 `file_examples.source_type` values and all `file_kinds.source_types` in `SOURCE_TYPES` — zero violations. All `also_schema` refs (`engineering`, `finance`, `photos`) on the roster. Every `collides_with` entry is an object with `domain`/`signal`/`provenance`; `also_holds_with` empty per CONNECTION §5. Three `00` quotes grep-verified verbatim; no other quotation used; `design_cite` null. No threshold numbers, no confidence scores, no handling classes. Files written: only the two assigned paths — no roster, canonical-field, `check.py`, `src/`, SPEC or neighbour file touched.

## Final recommendation

Keep `manufacturing.calibration-record` as a placeholder template with no fields, no dimensions and no schema coactivation edge. Activate it only on a labelled instrument identity joined to an as-found/as-left pair or equivalent metrological structure; anchor it on the instrument and never on a product or lot; treat the out-of-tolerance back-reference as a reviewable candidate edge that copies nothing; and route unmatched material to Independent Records, Receipts and Confirmations, or Review Later rather than inventing an instrument.

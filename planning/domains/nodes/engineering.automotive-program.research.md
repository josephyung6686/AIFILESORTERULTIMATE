# engineering.automotive-program — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.automotive-program.json`](engineering.automotive-program.json).
Verdict: **`refuse_node: true`.** No prior draft existed; this is a first pass.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` (in full) and the stamped assignment from
  `make_prompt.py engineering.automotive-program` — the node test, the procedure, the done-when list.
- `planning/00-database-agent-product-design.md` — authoritative, reached by `grep -n` for the five
  phrases quoted below rather than read through. All quotations verified verbatim at lines 63, 95, 120.
- **`planning/domains/nodes/engineering.json`** — my schema anchor and the decisive source in this
  pass: its default template, ten deterministic signals, `never_alone` list, `work_types` enum,
  twelve default-template fixtures, edges and `sensitivity_why`.
- `planning/domains/roster.json` — confirmed my row and enumerated the **twenty-four sibling
  templates already on the `engineering` schema**. This is where the refusal was decided.
- `finance.crypto-assets.research.md` (one landed launch row, depth calibration only);
  `business_operations.organisational-records.json` (refusal idiom and key set).
- `grep -rl "engineering.automotive-program"` and `grep -rl "automotive"` over
  `planning/domains/nodes/` — **no landed row argues a boundary against me.** Only
  `engineering.json` exists under the engineering prefix; the other twenty-three siblings are
  roster rows without node files. Boundaries below are therefore recommendations to R1c, except
  against `engineering.json` itself, which is landed and which I did not edit.

Deliberately not read, on the dispatch's token discipline: `00` in full,
`01-product-design-structured.md`, `CONNECTION.md` in full, any row outside my neighbour grep.

## THE CHARGE — the strongest case that this row should not exist

I make the case first, at full strength, because it is the case that won.

**This row is an industry name wrapped around four rows that already exist.** Its `one_line_hint`
decomposes without residue, and each clause already has an owner on the *same schema*:

| Clause of the hint | Row that already owns it |
|---|---|
| "its milestones" | `engineering.stage-gate-review`; `engineering.project` for the programme identity |
| "its customer requirements" | `engineering.requirements-specification` |
| "its type approval" | `engineering.product-certification` |

The rest of a vehicle programme's corpus distributes the same way: `engineering.risk-analysis-fmea`
(DFMEA, hazard analysis), `engineering.verification-validation` (DV/PV reports),
`engineering.prototype-build`, `engineering.cad-model`, `engineering.drawing-package`,
`engineering.bill-of-materials`, `engineering.change-order`, `engineering.embedded-firmware` (ECU
releases), `manufacturing.supplier-qualification` and `manufacturing.quality-management-system`.

**Worse: the schema anchor's own default template is already an automotive brake programme.**
`engineering.json`'s landed fixtures are `SYS-REQ-042_Braking-System-Requirements_RevB.docx`,
`BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`, `BPA-210_Product-Structure.xlsx`,
`ECR-1187_BPA-210_Bushing-Material.pdf`, `BPA-210_FEA_Loadcase-3_RevA.pdf`,
`BPA-210_DVT-07_Verification-Report.pdf`, `PDR_Braking-System_2026-04-18.pptx`,
`TDP_BPA-210_Baseline-C.zip`. A brake pedal assembly on a braking system is automotive to the bone.
This row's core evidence is not merely *similar* to the default's — it is the same bytes, already
spent. A template whose fixtures are its schema's own default fixtures **is** that default template,
which is exactly what the node test says is not a node.

Subtract the siblings and subtract the default, and the residue is the word *automotive* and its
vocabulary: vehicle, OEM, tier one, model year, VIN, nameplate. That is a **sector name** —
never-alone evidence of the purest kind. `00`'s reasoning about organisation names transfers:

> A university name alone should not create a group because Columbia can appear as an authoring
> school, course provider, target institution, employer, research venue, or merely a cited
> organization.

An industry name is weaker still than an organisation name: it does not name a party to the file,
only the sector of somebody's employer. `engineering.json` already refuses precisely this move at
its `code` boundary — a repository is not engineering merely because its employer builds hardware —
and that sentence refutes this row with the nouns swapped.

The charge also lands on three of the brief's other failure shapes. **A lifecycle stage:**
"programme" spans concept to start of production, and those stages are `lifecycle_stage` values
while the gates between them are `engineering.stage-gate-review`'s. **A document type:**
homologation dossier, certificate of conformity, customer technical specification and gate pack are
`work_type` values, sitting beside the values `engineering.json` already enumerates (released
technical data package, design review package, verification plan/procedure/report). **A duplicate
of a neighbour:** `engineering.project` is on the roster as the branch root for engineering material
carrying a project or product identity but no more specific sub-domain — a vehicle programme is
that, adjective included.

**I could not defeat this case.** What follows is the attempt and what it cost.

## The node test, argued in full

### Leg 1 — detection signals: FAIL

The schema's default already declares ten deterministic signals, each a *relation among labelled
slots*: drawing title block (item, drawing number, revision, status); requirements structure
(identifiers, allocation, rationale, verification method and status); technical data package
manifest; engineering change with affected item and current/replacement revision;
design-authoritative product structure; analysis package comparing margins to named requirements;
verification matrix; prototype build record reconciling deviations; archive manifest; and
parent-folder context that never fires alone.

I looked for a structure a vehicle programme has that is **not** in that list and not in a sibling.
Four candidates:

1. **Type approval.** Genuinely a different relation — approved *type* ↔ named *regulation* ↔
   approving *authority* ↔ *approval number* ↔ *validity*, with no drawing, requirement identifier
   or revision block anywhere in it. This is the strongest thing the row has, and it is real. But it
   is not automotive: it is `engineering.product-certification`'s relation ("the file that shows a
   product meets a regulation or a standard, and the certificate that comes out of it"). Road-vehicle
   regulations are one catalogue of **values** inside that relation, and under **D4** a jurisdiction
   is a value and never a field name — a regulator's catalogue is the same kind of object. Killing
   this candidate killed the row.
2. **A per-vehicle conformity document carrying a VIN.** Also a different relation — one *built*
   artifact, not a designed type. But a VIN-identified car is a person's or a fleet's property:
   `finance.vehicle-records`, `logistics.fleet-vehicle`. Not engineering evidence at all, and
   claiming it would have been actively harmful (leg 3).
3. **Programme timing and gateways.** A timing plan with a start-of-production milestone has no item,
   no revision, no requirement identifier — `engineering.json` itself says a project plan alone is
   not controlled technical definition. `engineering.project`, or
   `business_operations.project-delivery` when no technical evidence sits nearby.
4. **Sector-published method names** (a harmonised FMEA handbook, a functional-safety integrity
   level, a part-submission level). Values inside structures the siblings already own, exactly like
   a standard number on a drawing.

Nothing survived. `recognition.deterministic` therefore carries one honest entry saying the row has
no signal of its own, rather than a padded list that would be a copy of the schema's.

### Leg 2 — recommended dimensions: FAIL

The schema's researched default is `project → design_item → lifecycle_stage →
engineering_artifact_type` (machine-readable order empty under PR-6). The automotive rendering is
**programme → assembly → gate → artifact** — the same four levels with industry strings in them.

The two levels that felt automotive-only are both **values**. **`vehicle_line`/nameplate** is what
`project` or `design_item` already holds; a separate key would be a synonym. **`model_year`** is
tempting because MY27 really does partition a manufacturer's corpus — but it is a time level, and
`00` is explicit for record domains: "For document and record domains, project, function, or subject
usually comes before time because putting year first scatters related work across calendar folders."
Model-year-first would scatter one assembly's drawings, changes and test reports across year
folders — the precise harm named. In practice MY27 is a token *inside* the programme name, not an
independent labelled slot; standing alone it is a bare four-digit-shaped number wearing a prefix,
which `00` already forbids as proof.

Nothing about a car changes which parent makes which child intelligible. `00`'s rule — "A work type
such as Homework 3 is meaningful only after the course is known" — produces the schema default here,
and `00` assigns that recommendation to the domain template while leaving the user free: "The system
recommends an order based on the domain template, but the user can reverse, remove, add, or flatten
dimensions."

### Leg 3 — privacy rules: FAIL, and failing was the right outcome

`engineering.json` is already `potentially_sensitive`, for proprietary design definition, supplier
data, vulnerabilities, safety analyses, export-controlled or critical-technology information,
signatures and test evidence. Camouflaged prototype photography, crash-test footage and unreleased
styling are more of that category, not a different rule.

The one object whose privacy rule genuinely differs is the VIN-bearing Certificate of Conformity or
registration document — and it differs by **belonging to a different domain**,
`finance.vehicle-records`. Had this row activated on it, a private person's car paperwork would have
been filed inside a manufacturer's engineering programme, and a VIN — an identifier of a person's
property — would have become a candidate folder level. The refusal is load-bearing for the user, not
merely tidy. Where `finance.vehicle-records` does not fire, the JSON routes that document to
`Protected Records`, quoting `00` verbatim.

**Verdict: refuse.** Three legs, three failures, and the strongest surviving candidate (type
approval) belongs to a named sibling on the same schema.

## The collision fixture

`e11r-2018-858-00234-03_Whole-Vehicle-Type-Approval_XJ.pdf` — the best possible counterfeit of this
row's evidence: an official document, unmistakably automotive, with a labelled approval number, an
approving authority, a named regulation and an approved type designation, filed inside a
manufacturer's programme folder.

**What discriminates it:** it encodes a conformity relation, not a design-definition relation. No
design item under revision control, no drawing number, no requirement identifier, no product
structure — so none of the schema's ten deterministic signals touch it — and everything automotive
about it is a **value** from a road-vehicle regulation catalogue. Strip the catalogue and it is
structurally identical to a machinery-directive certificate or a radio-equipment approval.
`engineering.product-certification` owns that structure for every catalogue.

A second collision runs the other way: `Certificate-of-Conformity_WVWZZZ1JZ3W386752.pdf` looks like
manufacturer output and is a private owner's paperwork. Discriminator: the approval number appears
as a **citation**, not as an approval this filer holds, and the subject is one built vehicle
identified by VIN rather than a type.

## Reciprocal boundaries — both directions, same fixture on each side

Eleven are written into `collides_with`. The five that matter most:

1. **`engineering` (the schema default)** — fixture `BPA-210-001_Brake-Pedal-Assembly_RevC.dwg`,
   bytes-identical to a landed fixture on `engineering.json`. *Default → me:* it owns any file whose
   evidence is an identified design item plus a controlled artifact plus a revision or baseline, in
   any industry. *Me → default:* nothing remains, because the residue is a sector word.
2. **`engineering.product-certification`** — fixture the type-approval certificate above.
   *Certification → me:* it owns the conformity relation whatever the regulation catalogue.
   *Me → certification:* my homologation claim **is** that relation; I cede it entirely.
3. **`engineering.stage-gate-review` / `engineering.project`** — fixtures
   `MY27-XJ_Gateway-3_Design-Freeze_Review-Pack.pptx` and `Vehicle-Programme-Timing-Plan_MY27.xlsx`.
   *Siblings → me:* the gate pack with its decision slot is stage-gate-review's; the programme
   identity with no more specific sub-domain is engineering.project's branch root. *Me → siblings:*
   the "milestones" half of my hint is these two rows with an adjective.
4. **`manufacturing.supplier-qualification`** — fixture `PPAP_BPA-210_Level-3_Submission.zip`.
   *Manufacturing → me:* the packet's purpose is deciding whether a supplier's part may be used, and
   purpose governs the container. *Me → manufacturing:* I would have claimed it because it cites
   design records inside — exactly the archive discipline `00` forbids, copying a member's facts
   onto the container.
5. **`finance.vehicle-records`** (and `logistics.fleet-vehicle`) — fixture
   `Certificate-of-Conformity_WVWZZZ1JZ3W386752.pdf`. *Finance → me:* a VIN-identified built vehicle
   is owned property, filed by record type over its ownership life. *Me → finance:* I would have
   absorbed it on the approval number it cites; ceding it is the refusal's clearest user-visible
   benefit.

Also written: `engineering.requirements-specification` (`CTS_..._Rev4.pdf`),
`engineering.risk-analysis-fmea` (`DFMEA_..._AIAG-VDA_Rev2.xlsx`),
`engineering.verification-validation` (`BPA-210_DVT-07_Verification-Report.pdf`),
`engineering.embedded-firmware` (`ECU-BCM_SW-3.4.1_Release-Package.zip`),
`research.project-workspace` (`Battery-Cell-Ageing-Study_2026.xlsx`).

## Files considered and rejected

- **`Brochure_XJ_MY27.pdf`** — nameplate and model year in one filename and nothing else. A sales
  brochure. The fixture proving a vehicle-line token is never-alone; falls to `Reference Clips`.
- **`Owners-Manual_XJ_MY27.pdf`** — dense automotive technical prose, published by the manufacturer,
  and not an engineering record: product documentation shipped to a buyer. A technical *vocabulary*
  is not a technical *relation*.
- **`Service-Invoice_2026-03-14.pdf`** with a VIN — same identifier as the CoC, opposite side;
  `finance.vehicle-records`.
- **`Motor-Show_Press-Kit_2026.zip`** — marketing imagery and spec sheets; `creative` or
  `Reference Clips`. Would have padded the row with a corpus it has no claim on.
- **`Telematics-Fleet-Export_2026-Q1.csv`** — vehicle-identified rows, mileage, fault codes.
  `logistics.fleet-vehicle`: operational data about built vehicles, not design definition.
- **`IATF-16949_Audit-Report_2026.pdf`** — automotive to its name, squarely
  `manufacturing.quality-management-system`. Claiming it would make this row a quality-system domain
  by the back door.
- **`Homologation-Tracker.xlsx`** — a grid of regulations against approval statuses, the most
  automotive-looking spreadsheet in the corpus. It is a *management view* over
  `engineering.product-certification`'s records; its OCR'd screenshot is kept as a fixture precisely
  to show a partial grid yields universals only.
- **`Battery-Cell-Ageing-Study_2026.xlsx`** — measurement series, no item identifier, no revision;
  `research.project-workspace`. The intended destination of the cells is not evidence about the file.
- **`Autonomy-Dataset_run-0417.bag`** — bulk sensor capture. Machine state, not a personal or design
  record; `Unsupported or Encrypted` if it must land somewhere.

Eleven fixtures are kept in the JSON, each existing to show the id was a label: nine route to a
neighbour, two (`Screenshot 2026-05-12 at 09.14.33.png`, `IMG_4471.jpg`) to residuals with
universals only. Three carry `group_without_copying_facts: true`. `IMG_4471.jpg` is this node's
`HW 3.pdf`: it sits beside two gate packs, receives nothing from them, and its stripped location
EXIF proves nothing either.

## `proposed_fields` — empty, deliberately

`fields: []` by binding PR-6 and by contract (a template never copies its schema's list).
`proposed_fields: []` because a **refused** row must not touch the shared vocabulary — proposing a
key to justify a node one has just argued does not exist is the 574's mistake with an extra step.

Two keys were genuinely tempting and are recorded as *not proposed*. **`model_year`** — rejected on
leg 2: a time level in a record domain, and in practice a token inside `project`.
**`approval_number` / `regulation`** — real labelled slots, but they belong to whatever
`engineering.product-certification` needs, and that row's agent should propose them from its own
evidence; two rows proposing one key from different corpora is how synonym pairs get minted.

## Neighbours considered that did NOT get an edge

- **`business_operations.project-delivery`** — named in prose on the timing-plan fixture, no edge:
  `engineering.json` already carries that boundary at schema level, and duplicating it from a refused
  child would give one fixture two claimants.
- **`engineering.aerospace-airworthiness`** — the most interesting omission. No edge, because we
  share no evidence: no file is both an automotive and an aerospace record. Raised as NJ-AUTO-1.
- **`construction_property.drawings-revisions`** — shares drawing-and-revision evidence, but
  `engineering.json` already owns that boundary (`A101_Ground-Floor-Plan_Rev4_IFC.pdf` is one of its
  negatives) and nothing automotive is at stake.
- **`government.transport-authority`** — the regulator's own files are the *other* side of a type
  approval, but a manufacturer's copy of a certificate is still
  `engineering.product-certification`. No shared discriminating evidence from this side.
- **`career.*`, `legal.*`** — an automotive employment contract or supply agreement is a contract;
  the industry is incidental. The same fallacy the row is refused for.
- **`role_split`** — empty. The split this material wants is *customer* / *approval holder* /
  *issuer*, three roles for one organisation string in one title block. No canonical key exists to
  split against, and minting one for a refused row would be the worst possible reason to touch the
  shared vocabulary. See NJ-AUTO-3.

## Self-verification

- `python3 -m json.tool` — parses.
- Every span attributed to `00` grep-verified verbatim before writing: Independent Records, Review
  Later and Protected Records (line 120); university-name-alone (line 63); project-before-time,
  Homework-3, reverse/remove/add/flatten (line 95).
- Every `file_examples.source_type` is in `SOURCE_TYPES` (11/11). Every `collides_with.domain`
  resolves to a `roster.json` `domain_id` (11/11). Every `falls_through_to.residual_template` (3/3)
  and every `falls_through_if_inactive` (11/11) is one of `00`'s nine residual names. Every
  `also_schema` value resolves to a roster schema id.
- `also_holds_with` and `role_split` empty, each with a note saying why.
- No threshold, score, count or handling class anywhere. `sensitivity` is `potentially_sensitive`
  only, recorded to demonstrate sameness, not difference. No field key minted or proposed.
- Only the two assigned files were written. `29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `engineering.json` and every other node untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-AUTO-1 — the asymmetry with `engineering.aerospace-airworthiness`.** That sibling survives on
  the roster as a named industry row while this one refuses; R1c should decide whether that is
  principled. The distinction I can defend: *airworthiness* names a regulatory **relation** — an
  approval that must be actively held and continuously maintained, with a release document per
  article and a continuing obligation after delivery — whereas *automotive-program* names an
  **industry** plus the generic word *programme*. If airworthiness clears its own node test on that
  continuing-approval relation, the asymmetry is real and both verdicts stand. If it clears only on
  aerospace vocabulary, it should be refused on this row's reasoning and both coverages should route
  to `engineering.product-certification`. **Not this row's call; I did not read or edit that row.**
- **NJ-AUTO-2 — make the absorption visible.** This refusal routes homologation coverage to
  `engineering.product-certification`, which has no node file yet. Recommendation to R1c: that row
  should carry an explicit type-approval fixture and a road-vehicle regulation among its values, and
  `engineering.stage-gate-review` should carry a design-freeze gate example, so the absorbed
  coverage is demonstrably held rather than assumed. Without that, refusing here creates a silent
  gap — the one way a correct refusal can still cost the product something. **Recommendation only;
  I edited neither file.**
- **NJ-AUTO-3 — one organisation string, three roles, no key to split on.** On an automotive title
  block the same company name can be customer, design authority, approval holder, supplier and print
  vendor. `00`'s university-name-alone reasoning says this is exactly the ambiguity that must not
  create a group, but the shared vocabulary offers no producer-side / holder-side pair to
  `role_split` against. Alternatives: (a) leave it as a `never_alone` rule on the engineering schema —
  today's state, and in my view correct for launch; (b) mint an approval-holder or design-authority
  key on the shared vocabulary, a product-wide decision no single template may make; (c) let
  `engineering.product-certification` propose a holder key scoped to certificates only, accepting it
  will not generalise to title blocks. **Recorded, not resolved. No field proposed.**

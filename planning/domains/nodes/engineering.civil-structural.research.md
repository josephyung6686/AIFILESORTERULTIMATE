# engineering.civil-structural — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.civil-structural.json`](engineering.civil-structural.json). Salvage: none — no
prior draft of either file existed.

Verdict: **node kept, but only after being narrowed from a discipline to a situation.** The row as
named on the roster ("Civil and structural design") would have been refused. The row as written —
*the fixed work whose adequacy is justified by calculation against a published design code* —
survives all three legs of the node test on evidence I can name.

## 1. Sources

Binding: the standing brief; the stamped assignment from `make_prompt.py`;
`planning/00-database-agent-product-design.md` **by targeted grep only** (three greps — every
quoted span matched verbatim before it was written, §8); `planning/domains/nodes/engineering.json`
in full, as the anchor this row is measured against; `finance.crypto-assets.research.md` as the
depth calibration (two of its moves copied deliberately — empty `proposed_fields` with the
temptations parked, and an empty `role_split` with the refusal argued); `roster.json` for every edge
endpoint; `src/evidence_shape/vocabulary.py` for `SOURCE_TYPES`.

`construction_property.site-survey` (`.json` and `.research.md`) is the only landed row that already
argues a boundary against this id — found with one grep, read only at the matched regions. It is
load-bearing here and is quoted in §5.

The roster query also produced the fact that forced the narrowing: `engineering.drawing-package`,
`.cad-model`, `.simulation-analysis`, `.bill-of-materials`, `.material-specification`,
`.standards-library`, `.process-plant-design` and `.commissioning-handover` **already exist**, and
between them hold most of what a naive "civil engineering" row would have claimed.

Not read, deliberately: `01-product-design-structured.md`, `CONNECTION.md`, `canonical_fields.json`.
The node test, the closed edge vocabulary and the residual names were already stated in the stamped
assignment and the anchor, and this row proposes and reuses no field, so there was nothing to check
against the field file. Recorded rather than hidden.

External reality checks (no gazetteer content, no regex, no threshold): the document families named
below are standard practice artefacts — bar bending schedules under a published bending-shape
catalogue, load takedowns and limit-state combinations under a code suite, pile schedules, temporary
works design-and-check certificates with a check category, sealed design certificates carrying a
professional registration number. Nothing depends on a country's particular code designations; the
code names in `never_alone` are examples of a shape, not a match list.

## 2. THE CHARGE — the strongest case that this row should not exist

**`engineering.civil-structural` is an industry label.** "Civil and structural" is a *discipline* —
the name of a profession and of a department, in the same family as "aerospace" and "automotive",
which is to say the same family as the 574 sector rows this project exists to delete. Six ways it
fails:

1. **It is a value.** The engineering schema's own `work_types_note` says work types are values of
   `engineering_artifact_type`. "Civil", "structural", "geotechnical", "drainage" are values of a
   *discipline* facet in exactly the same way. Values are not nodes.
2. **It duplicates its own schema's default template.** Requirements, drawings, calculations,
   changes, verification — that is what `engineering.json` describes. If the only difference is that
   the item is a bridge rather than a brake pedal, the difference is a value of `design_item`.
3. **It duplicates its siblings.** Drawings → `drawing-package`. Models → `cad-model`. Analyses →
   `simulation-analysis`. Schedules → `bill-of-materials`. Specs → `material-specification`. Codes →
   `standards-library`. Nothing is left.
4. **It duplicates a neighbour.** Fixed works stand at places, and places are
   `construction_property`: `drawings-revisions`, `site-survey`, `construction-project` and
   `building-control` already carry the drawings, surveys, programme and approvals.
5. **Its evidence is never-alone evidence.** A consultancy's letterhead; the word "structural"; a
   `.dwg`. Organisation names and type words — the class that can never activate a node.
6. **It is defined by absence.** "Engineering that is not a product" is a hole in the schema
   default, not a filing world.

**Conceded:** 1, 3, 5 and 6 in full; 4 in part. The consequence is written into the JSON — the row
is renamed from the discipline to the situation, the discipline word goes into `never_alone` as
non-evidence, and every sibling in point 3 gets an explicit `collides_with` conceding the part that
is theirs. A row that had to concede this much and had nothing left would have been refused.

**What defeats the charge — one thing, and it is enough:** *the calculation that justifies a fixed
work against an external published standard.* Its structure is a computed demand, a computed
capacity, and a cited clause of a code nobody in the project wrote, resolved into a utilisation
figure for a named member mark on a structural grid. That relation is **inverted** relative to the
schema default: the default allocates a requirement to a design item from inside the project's own
controlled definition, whereas here the requirement is **external and public** and the design item is
a mark that does not exist outside the one structure. No sibling holds it — a drawing package holds
sheets, `simulation-analysis` holds runs, `standards-library` holds the code *document*, and a BOM
row holds a parent/child product structure.

The test I applied to myself: *delete this row — where does
`1042-STR-CALC-001_Superstructure-Design_RevP2.pdf` go?* Not the standards library (not a standard),
not drawing-package (not a drawing), not simulation-analysis (no model), not site-survey (that row
has explicitly said so). It would fall to `Independent Records` forever, and the check chain that
gives a bar schedule and a rebar detail their meaning would never assemble. Real loss; row stays.

## 3. The node test, all three legs

The schema's **default template**, from `engineering.json` so the comparison is exact: `dimension_
order` empty by PR-6, researched order *project → design_item → lifecycle_stage →
engineering_artifact_type*; deterministic signals are a controlled title block, a requirements
structure with allocation and verification columns, a TDP manifest, an engineering-change structure,
a design-authoritative BOM, an analysis compared against *named requirements*, a verification
matrix, a prototype record, an archive manifest; sensitivity reason is proprietary definition,
supplier data, export control.

**Leg 1 — signals differ. Yes; the row rests on this leg.** Five structures in this row's
`deterministic` list are absent from the default and true of the file list: a **code-clause-plus-
utilisation pairing** (the external requirement — `1042-STR-CALC-001`,
`Wind-Loading-ASCE7-22_Calc.xlsm`); a **load takedown / limit-state combination table** whose
columns are load cases (same two); a **mark schedule keyed to a structural grid**
(`Foundation-Design-Report`, PC-01..PC-12; the `.ifc`); a **reinforcement detailing structure** —
bar marks, shape codes, cover, concrete grade (`1042-S-201`, `Bar-Bending-Schedule`); and a **design
certificate with a professional registration number and a stated scope of design responsibility**
(`TW-14_Propping-Scheme`, and the calculation's footer). Conversely the default's requirement
identifiers, TDP manifest and prototype records do not appear in this material at all.

**Leg 2 — dimensions differ. Conditional, and written as conditional.** PR-6 keeps both this row and
its schema at `dimension_order: []`, so this leg cannot be shown in machine-readable form and I do
not pretend otherwise. The researched difference, for R1c: *project → structure →
engineering_artifact_type*. Two departures. (a) The item level must be the **fixed work**, not a
reusable configuration item — "Beam B12" is unintelligible outside its structure, which is `00`'s
parent-makes-child-intelligible rule applied one level higher than the schema applies it. (b)
`lifecycle_stage` is **demoted out of the standing levels**, because the civil lifecycle gate is
expressed as a drawing *issue status* that `construction_property.drawings-revisions` owns; a level
here would branch on a fact this row does not evidence and would scatter one structure's design
across status folders. A real disagreement with the parent, not a restatement.

**Leg 3 — privacy differs in kind.** Same value (`potentially_sensitive`, no handling class),
different reason, and not by degree. The schema's reason is commercial — IP, supplier data, export
control. This row's exposure is **third-party and safety**: a sealed calculation reproduces a named
individual's signature image and registration number; an adequacy assessment names a real address
and occupancy and may conclude a member is unsafe — a fact about people who do not own the file;
temporary works, bridge and dam records describe how a structure fails. Hence
`Structural-Adequacy-Assessment_St-Marys-Hall_Roof-Planks.pdf` is the one fixture routed to
`Protected Records` when inactive, surfaced as NJ-CIVIL-3 rather than assumed.

Nothing was invented to keep the row: `fields: []`, `proposed_fields: []`, `role_split: []`, no
dimension encoded, both tempting keys parked.

## 4. Files considered and REJECTED

Thirteen fixtures are kept in the JSON. These are the tempting ones that are **not** this row's
evidence.

| Considered | Why it is not this row |
|---|---|
| **A civil and structural consultancy's whole project folder** | The charge in physical form. An organisation's name is never-alone evidence; the folder holds fee proposals, programmes, invoices, CVs — `business_operations`. Written into `never_alone`. |
| **`Eurocode-2-Worked-Examples...pdf`** | Contains **every** context term this row lists and is still not evidence: the structures are "Example 3.1", with no address, client, scheme or responsible engineer. Kept as a *file example* precisely because context terms are not evidence. `Reading Inbox`. |
| **The design code itself** (`EN 1992-1-1`, `AISC Manual`) | `engineering.standards-library`. This row's files *cite* codes; that row holds them. Hence "a design-code name alone" in `never_alone`. |
| **A steel fabrication drawing under a works order** | The collision fixture — §6. `manufacturing`. |
| **A take-off or bill of quantities** | Same table shape, same member names, a **rate** column where this row has a utilisation column. `construction_property.quote-estimate`. Hence "a schedule of quantities alone" in `never_alone`. |
| **A building control submission pack** with the calcs appended | The application apparatus — reference, validation, approval notice — is `construction_property.building-control` / `government.permit-licensing`. The appendix is this row's; the pack is not. |
| **A CDM designer's risk register** | Genuinely a design-stage output and genuinely tempting. Rejected from `work_types`: its apparatus is a hazard/residual-risk register, a different structure already recognised by `construction_property.site-health-safety` and `business_operations.risk-register`. Including it would widen the row back toward the discipline. |
| **Site diary, progress photo run, snagging list** | `construction_property.site-diary` / `.progress-photos` / `.snagging-defects`. Execution and observation, no design step. |
| **Structural warranty, PI certificate, collateral warranty** | Reads as "structural", is a legal instrument. `legal.leases-agreements` / `law_practice.*`. |
| **An erection method statement** | Execution instruction — `construction_property.site-health-safety`. Near-miss worth stating: the *temporary works design* it implements **is** kept, because it carries a calculation and a check certificate. |
| **A drawing register or transmittal** listing this row's sheets | `construction_property.drawings-revisions`. Same bytes referenced, opposite relation — §5. |
| **`beam_check.py`** | `code`. Carried as a `collides_with` fixture rather than a file example, because the interesting statement is the mirror of the practice-name rule: a design office's script is code even though its employer designs bridges. |
| **A ground investigation factual report** | `construction_property.site-survey`, by that row's own written concession — §5. |
| **An architect's GA or planning drawing** | No load path, no code clause, no member marks. `construction_property.drawings-revisions` or `government.planning-application`. |

## 5. Reciprocal boundaries — both directions, same fixture on both sides

`construction_property.site-survey` wrote its half first: *"an analysis, a calculation, a design
assumption or a proposed solution supports the engineering row; a record of what was found with no
design step supports this row"*, and its rejected-files table repeats it — *"the discriminator is
the **design step**"*. This side agrees and does not rewrite it.

| Neighbour | This row holds | The neighbour holds | Shared fixture |
|---|---|---|---|
| `construction_property.site-survey` | adopted design parameters + capacity checks + a resulting schedule, **even when borehole logs are reproduced as an appendix** | the factual record of what was found, no design step | `Foundation-Design-Report_1042_Pile-Layout_RevB.pdf` vs `Ground-Investigation-Report_1042.pdf`; **both hold** where one PDF carries a log and a recommendation |
| `construction_property.drawings-revisions` | the design **content**: bar marks, shape codes, cover, grade, grid, and the calculation behind it | the **issue apparatus**: register, revision sequence, issue status, transmittal | `1042-S-201_RevC_Ground-Floor-Slab-Reinforcement.dwg`, named identically on both sides |
| `manufacturing` | the definition and its justification | execution against it: works order, fabrication, erection, heat and NDT records | `Fabrication-Drawing_Assembly-B12_WO-8871.pdf` |
| `engineering.simulation-analysis` | compliance: demand vs capacity vs a cited clause, for a fixed work | the simulation **run**: model, mesh, solver, post-processing | `Wind-Loading-ASCE7-22_Calc.xlsm` and any frame FE model — **both** where the run feeds member checks |
| `engineering.drawing-package` | the fixed-work design, of which drawings are one output | the discipline-neutral controlled drawing **set** | the same rebar sheet |
| `engineering.bill-of-materials` | a per-drawing member/bar quantity schedule under a published shape catalogue | a parent-assembly → child-part product structure | `Bar-Bending-Schedule_1042-S-201_RevC.xlsx`; this row **concedes** any schedule stating parent/child |
| `engineering.process-plant-design` | the structure carrying the plant, by load takedown and member check | the process apparatus: P&ID, line list, equipment schedule | a pipe rack package — both may hold |
| `engineering.standards-library` | files that **cite** a code as authority for a result | the code document itself | any file whose loudest string is a code designation |
| `government.planning-application` | the calculation deliverable | the application: reference, validation letter, consultee responses | the calculation appended to a submission pack |
| `code` | a produced calculation with a design responsibility statement | repository root, manifest, tests, source structure | `beam_check.py` |
| `research` | an adequacy verdict on a named existing structure at an address | a generalisable proposition with a venue and citations | a capacity study of a structural product |

**Where this row concedes rather than competes:** `drawings-revisions` on any transmittal or
register; `bill-of-materials` on any schedule with a parent/child structure; `simulation-analysis`
on any model study with no code check; `standards-library` on the code itself; `site-survey` on any
factual record with no design step. **R1c must carry the other half of every row in this table
except `site-survey`**, whose other half is already written.

## 6. The collision fixture

**`Fabrication-Drawing_Assembly-B12_WO-8871.pdf`** — a steel fabricator's shop drawing. It carries
piece marks *lexically identical* to member marks (B12), a steel grade, hole positions, weld
symbols, a bolt list, a drawing number and a revision letter. Every observation a naive detector
would fire on is present, and the assembly is the exact beam this row's calculation checked.

**What discriminates it, on its own bytes:** (a) the title block carries a **works order number and
a fabricator's job reference** where this row's files carry a **statement of design
responsibility**; and (b) there is **no load case, no code clause and no utilisation anywhere on the
sheet** — a shop drawing says how to make the thing, never why it is adequate. Citing the design
drawing number does not transfer the design step; that is written into the fixture's
`must_not_conclude`.

A softer second collision is carried as a file example for a different reason:
`Eurocode-2-Worked-Examples-for-Beam-and-Slab-Design.pdf` contains every proposed context term and
is teaching material — the row's standing proof that context terms are plausibility, never evidence.

## 7. Fields, and the two keys I did not mint

`fields: []` by PR-6 and by the rule that a template references its schema's fields and never copies
them. `proposed_fields: []` — deliberately, against real temptation:

- **`structure`** (the fixed work) is the level the dimension argument in §3 needs. Not proposed,
  because it would be a **near-synonym of the schema's own `design_item`, which is itself still
  unadjudicated by R1c** — minting a variant of an in-flight key is the exact failure the brief
  names. Recommendation: widen `design_item` to cover one-off fixed works. NJ-CIVIL-1.
- **`design_code`** is the most discriminating string in this material and is still **not a field**,
  for a structural reason: one design is checked against several codes at once (a Eurocode suite is
  EN 1990 + 1992 + 1993 + 1997 simultaneously), so it is multi-valued and can never be a destination
  dimension. A search fact at most. NJ-CIVIL-2.

`role_split` is empty and the refusal is argued in the JSON: the split this material wants is
**designer vs independent checker**, both named and registered on the same temporary works
certificate. There is no canonical key for either, authorship is never a destination under `00`, and
minting a producer-side key for one template is what generated thousands of private field names in
the overnight pass. Recorded in that fixture's observations instead.

**Sparse-file discipline.** `beam_check.png` is this node's `HW 3.pdf`: a cropped utilisation table
with no mark, scheme, clause or title visible, no EXIF, beside two accepted calculation PDFs.
`group_without_copying_facts: true`, universals only, and its `must_not_conclude` covers both halves
— the neighbourhood donates no structure or mark, and missing EXIF is not proof of a screenshot.
`Wind-Loading-ASCE7-22_Calc.xlsm` carries the same flag for a harder reason: it is *fully
recognisable* as a code check and identifies **no work at all**, so it may join a neighbourhood
while the scheme stays unknown. It routes to `Review Later`, under `00`'s rule that *"conflicting
signals should lead to abstention rather than an invented classification"*.

## 8. Audits run before returning

- `python3 -m json.tool` — parses.
- Every `collides_with.domain` (11/11) and `also_holds_with.domain` (3/3) resolves to a
  `roster.json` `domain_id`; checked mechanically, zero misses.
- Every `file_examples.source_type` (13/13) is in the fourteen-member `SOURCE_TYPES`.
- Every `falls_through_to.residual_template` (5/5) and every `falls_through_if_inactive` (13/13) is
  one of `00`'s nine residual names. Every `also_schema` is a roster **schema** id
  (`construction_property`, `manufacturing`) or `null`.
- **Quotations.** Seven spans are attributed to `00`; all were grep-matched verbatim before being
  written — the five residual sentences sit in one paragraph of `00`, and
  *"conflicting signals should lead to abstention rather than an invented classification"* and
  *"download session alone is never sufficient"* were each matched by direct grep. **No `00`
  quotation in this node is fabricated or paraphrased inside quote marks.** The two spans quoted
  from `construction_property.site-survey` are marked as coming from that file, not from `00`.
- No number in either file is a threshold, score, or count of evidence — the digits are filenames,
  code designations inside fixture names, and prose references. No handling class assigned.
- `fields`, `proposed_fields` and `role_split` are all empty, each with a note saying why.
- Only the two assigned files were written. No neighbour node, roster, canonical field file,
  `check.py`, `src/` or SPEC was touched.

## 9. NEEDS-JOSEPH (this node only)

- **NJ-CIVIL-1 — the intelligible parent is a STRUCTURE, and no key can say so.** One scheme has
  three bridges; one site has six blocks. A member mark is meaningless outside its structure, so the
  level is real, but `design_item` is defined around a reusable configuration item and is itself
  unadjudicated. (a) Widen `design_item` to include one-off fixed works — **recommended, and the
  reason no key was proposed**; (b) mint `structure`, creating two near-synonyms before either is
  settled; (c) collapse structures into `project`, losing the level that makes a mark intelligible.
- **NJ-CIVIL-2 — may a multi-valued fact exist as a non-destination fact at all?** `design_code` is
  the most discriminating string here and is multi-valued per design, so it can never be a folder
  level. If the product has no place for a search-only multi-valued fact, this row must drop the
  idea entirely rather than half-hold it.
- **NJ-CIVIL-3 — does an adequacy assessment of an occupied third-party building default to
  `Protected Records`?** This row says yes when inactive: the file names an address and an occupancy
  and may state a structure is unsafe — exposure belonging to people who do not own the file. That
  is a stronger default than any sibling applies and should be confirmed, not assumed. The
  alternative is `Independent Records`, treating it as an ordinary standalone report.
- **NJ-CIVIL-4 — overlapping claims inside plants.** This row and `engineering.process-plant-design`
  both claim structures in process facilities. This row's position: keep only the load-path
  justification, concede the process apparatus entirely. If R1c wants a single claimant per plant
  package, name it and this row concedes.
- **NJ-CIVIL-5 — the roster name is wrong for what survived.** The roster says "Civil and structural
  design", a discipline; the researched row is *fixed-works design justified by code calculation*,
  which is what the JSON's `name` and `one_line` say. **This is a recommendation to R1c to change
  the roster `name` and `one_line_hint`; this row did not edit the roster.** If the discipline name
  is retained, expect future agents to re-inflate the row into a sector.

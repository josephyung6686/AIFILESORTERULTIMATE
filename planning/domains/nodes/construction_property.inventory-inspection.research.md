# `construction_property.inventory-inspection` — lab notes (J-DEPTH deepening)

Row kind: **template**. Launch: **placeholder** (`fields: []`). Verdict: **kept, not refused**.

The retired gist draft was directionally right: it found the room-then-element grid, the paired
check-in/check-out lifecycle, and the unusually intimate privacy exposure. This pass tested the harder
dispatch charge: whether those are merely the format and values of a checklist, or a site-survey /
building-condition document under another name. The row survives, but narrowly. A contents list,
address, the word *inventory*, or room photographs do not establish it. What survives stripping is a
**dated comparison protocol** whose purpose is to preserve an agreed baseline and later attribute change.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — the only source quoted. Its observation/fact split,
  never-alone discipline, sparse-file rule, purpose distinction, privacy ordering, dimension rule,
  residual definitions and abstention rule govern this row. Every JSON quotation was re-checked.
- `ALIGNMENT.md`, `CONNECTION.md`, `_CONTRACT.md`, `canonical_fields.json`, `roster.json`,
  `src/evidence_shape/vocabulary.py`, `DECISION-BRIEF.md`, and `ROSTER.md` §4 / Appendix A. These settle
  the node test, closed vocabularies, D1/PR-6 field deferral, and the absorbed
  `prop.inventory-inspection` legacy row. No key was minted.
- Required comparisons: the deepened `construction_property` schema anchor;
  `construction_property.site-survey`; `construction_property.survey-valuation`; and the search-named
  `business_operations.it-asset-inventory` and `business_operations.facilities-workplace`.
- Boundary comparisons: `construction_property.tenancy-management`, `progress-photos`,
  `agency-listing`, `snagging-defects`; `finance.household-property`; and
  `legal.leases-agreements`.

`00` does not name this world. It supplies machinery, not a design claim for the situation. Therefore
`provenance` remains `proposal`, `design_cite` remains `null`, and boundaries remain inferences.

---

## What this situation is — and is not

This is **baseline-and-change evidence for a bounded property inspection event**. Its strongest packet
contains a check-in report, room-by-room contents/condition schedule, photographic appendix, meter and
key record, acknowledgement or comment period, and later a check-out comparison or deduction dispute.
The design licence for grouping this mixed packet is exact: *"The documents are content-incoherent but
purpose-coherent."*

It is not *any file that inventories property contents*. A furniture spreadsheet can be a register. It
is not *any condition inspection*. A home survey can be a professional opinion; a measured survey can
be geometry; a snag list can be work to rectify. Nor is it *any tenancy record*. A lease, rent ledger
and deposit certificate concern the same tenancy but lack the baseline/comparison protocol.

The draft's statement that the documents are *useless alone* was too absolute. A signed check-in is
useful alone as a baseline, and an interim report may stand alone. The accurate claim is that the
situation's strongest organizational value is **relational**: check-out is intelligible against
check-in, and a deduction response against both. Grouping is load-bearing without copying facts.
`00`: *"The graph does not automatically copy those missing facts onto sparse files."*

---

## Node test, leg by leg

The schema default is **property/site → instruction (job, letting, scheme, block) → document
function**, with period only for a genuine cycle. CONNECTION permits this template only if detection,
recommended dimensions, or privacy differs from that default.

### Leg 1 — detection differs. Pass; decisive.

The signal is not an address, word, extension or generic table. It is a conjunction enacting a
comparison protocol:

1. repeating **room → element** rows for walls, ceilings, flooring, fixtures and contents, carrying
   contemporaneous condition/cleanliness observations;
2. an event header distinguishing check-in, check-out or interim inspection and supplying a date;
3. a party acknowledgement or comment mechanism attached to the baseline;
4. on exit, a **before/current/difference** structure or explicit reference to the check-in baseline;
5. accessory custody observations — meter serial/readings and key/fob counts — tied to the event.

`00` licenses cell extraction: *"Tables matter because resumes, forms, applications, invoices, and
administrative documents often place their most useful information in cells rather than body
paragraphs."* It does not validate the opinions in those cells. *Carpet stained* is an inspector's
dated observation; *tenant caused damage* and *deduction agreed* remain unknown without evidence.

The format-only challenge fails in both directions. An IT register has asset tags, serials, custodian,
hostname and warranty. A facilities checklist has room, task, frequency and completion. A snag list has
defect, responsible trade, target date and close-out. None establishes an agreed baseline to compare at
a later handover. Conversely a signed email with labelled room photographs, check-in reference, meter
readings and invitation to correct the baseline can support this situation without a spreadsheet.
Format is neither necessary nor sufficient.

### Leg 2 — dimensions differ weakly; not load-bearing.

The prose recommendation is **property → tenancy or condition-proving engagement → inspection
event/type**, keeping baseline and comparison together. A tenancy/engagement is an instruction and
inspection type is a document function, so this specializes rather than replaces the default. Leg 2
alone would not earn a node.

The operational distinction is pairing. Year-first can split a March check-in from the following
February check-out. The design supports property/engagement first: *"For document and record domains,
project, function, or subject usually comes before time because putting year first scatters related work
across calendar folders."* It remains editable. JSON `dimension_order` stays `[]` because the schema
declares no fields; naming property, tenancy or event there would open an unlicensed level.

### Leg 3 — privacy differs. Pass; independently sufficient.

This row systematically creates a photographic tour of an occupied home, often including possessions,
correspondence, children's rooms, security devices, meter identifiers and GPS metadata. The exit packet
adds allegations about a named person and money proposed to be withheld. The exposed party is commonly
not the holder and cannot consent. That is more specific than generic address sensitivity: the evidence
method itself creates the exposure.

The required ordering is exact: *"Privacy policy must be enforced before content reaches any model or
external connector."* The row assigns only `potentially_sensitive`; it invents neither a P7 class nor
safety-domain status.

**Overall: kept.** Legs 1 and 3 each distinguish this situation. Leg 2 reinforces organization but is
not sufficient alone.

---

## Existence challenge: inventory contents or separate situation?

Remove check-in/check-out framing, event date, baseline acknowledgement, comparison reference and
tenancy/pre-works purpose. The residue is objects, conditions and photographs and should **not** activate
this row. It belongs to an asset register, facilities record, household record, survey packet, photo
collection or residual according to its own evidence.

The awkward extension is a pre-works schedule of a neighbouring property. It uses the same
baseline/change mechanism but lacks tenant, deposit and check-in vocabulary. JSON now requires
abstention when neither tenancy framing nor professional-reliance/measured-geometry framing settles it.
Whether that extension stays is NJ-CP-11, not silently smoothed over.

---

## Files considered and rejected

The nine JSON fixtures cover labelled baseline report, comparison report, sparse image, OCR sheet,
legal instrument, archive, non-tenancy schedule, email dispute and interim report. Each separates raw
observations from legal facts and forbids a folder-path conclusion.

| File | Why it is not this row's evidence |
|---|---|
| `Tenancy agreement - 14 Marsh Lane.pdf` | Executed instrument: parties, term, covenants, signatures. `legal.leases-agreements` protects it first. Referencing an inventory copies no facts. |
| `Property photos - Marsh Lane.zip` | Wide room images without captions, gradings, event, acknowledgement or baseline. `agency-listing` or image residual. |
| `1042-EX-01 Existing site plan Rev A.pdf` | Datum, levels, scale and geometry: `site-survey`; no contents grid or handover comparison. |
| `Level 2 Home Survey - 14 Oakfield Rd.pdf` | Addressee, basis, ratings and liability limitation: `survey-valuation`; *inspection* does not decide it. |
| `Snagging list - Plot 8 - handover.xlsx` | Defects assigned for rectification, target and close-out: `snagging-defects`, not later evidential comparison. |
| `IT Asset Inventory.xlsx` | Asset tags, serials, custodians, hostnames, warranties: `business_operations.it-asset-inventory`; only the label is shared. |
| `Office condition inspection checklist.xlsx` | Facilities task/completion evidence: `business_operations.facilities-workplace`; room names and *inspection* are insufficient. |
| `EPC - 14 Marsh Lane.pdf` | Scheme certificate/rating, not comparison protocol; standalone coverage falls to the producing situation or Independent Records. |
| Home-contents insurance photo schedule | Insured items/values and claim/policy framing: `finance.insurance-personal`; visually similar, different purpose. |
| `IMG_1001–IMG_1080.HEIC` move-in photographs | Without report/context they activate photos at most. EXIF and indoor rhythm do not prove inventory purpose. |
| Blank inventory template / landlord checklist | Reference Clips or Reading Inbox. Unfilled structure evidences no property, event or relationship. |
| Inventory clerk invoice / booking | Receipts and Confirmations. Transaction evidence around the report, not the report. |

---

## Collision fixtures in both directions

**Would wrongly fire this row:** `Property photos - Marsh Lane.zip`. Same rooms, date range and camera
behavior as an inventory. The discriminating absence is the report: no room/element captions, condition
observations, handover event, acknowledgement or baseline. An *indoor burst* rule would be a false detector.

**Must not be lost to this row:** `Level 2 Home Survey - 14 Oakfield Rd.pdf`. It contains a
room/element condition structure and photographs, so superficial inventory signals fire. Professional
reliance apparatus — addressee, purpose/basis, limitations — assigns `survey-valuation`. If professional
and tenancy framings genuinely coexist, abstain rather than force a template.

**Household custody fixture:** `Move-in Inventory and Condition Report - 18 River Court.pdf`, named
identically by `finance.household-property` and `tenancy-management`. This row owns the inspection
situation; the occupier can retain the same bytes in a household group. Custody does not copy facts.

---

## Reciprocal boundaries and R1c recommendations

| Neighbour | This row holds | Neighbour holds | Shared bytes / status |
|---|---|---|---|
| `construction_property.tenancy-management` | room baseline/comparison event | running relationship: referencing, rent, notices, deposits, renewals | `Move-in Inventory and Condition Report - 18 River Court.pdf`; neighbour names this row |
| `legal.leases-agreements` | dated condition record | executed instrument; legal protects first | `Tenancy agreement - 14 Marsh Lane.pdf` |
| `construction_property.site-survey` | contents/condition gradings plus tenancy/deposit/check-in framing | geometry: datum, levels, coordinates, scale, accuracy | same forty room images; neighbour already names seam; edge added here |
| `construction_property.survey-valuation` | baseline under tenancy/pre-works framing | reliance-bearing opinion or costed breach | schedule of condition versus check-in; discriminator revised here |
| `construction_property.progress-photos` | bounded inspection event/report | open-ended works capture sequence | standalone sequence conceded to neighbour |
| `construction_property.snagging-defects` | condition preserved for attribution | defects expected to be rectified and closed | room-by-room handover checklist |
| `construction_property.agency-listing` | evidential detail images tied to baseline | marketing images plus price/particulars | `Property photos - Marsh Lane.zip` |
| `finance.household-property` | professionally produced inspection situation | occupier's retained administration copy | `Move-in Inventory and Condition Report - 18 River Court.pdf` |

The gist JSON edged `business_operations.it-asset-inventory` solely because both rows use *inventory*.
That was incorrect. CONNECTION requires confusing evidence, while the edge admitted only the word
*inventory* and nothing else. Never-alone text cannot support activation and therefore cannot support collision.
**The edge was removed** and retained here as a rejected false positive. This is an explicit reversal.

`business_operations.facilities-workplace` also gets no edge. Room names and checklists are topical
adjacency; facilities evidence is occupancy/maintenance/task completion, not baseline/later comparison.
`finance.hoa-residents-association` remains unedged: block inspections route through block-management,
and no shared discriminating structure was established.

---

## Fields, role split, and sparse files

`fields: []`, `proposed_fields: []`, `role_split: []`. The schema declares none under D1/PR-6 and this
template may not mint a copy. Candidate concepts — property, tenancy/engagement, inspection event/type —
remain prose for R1c. This row seconds the anchor's property need without creating a variant.

Sparse members such as `IMG_9902.HEIC`, meter photograph, key receipt or dispute email may join an
accepted inspection group while acquiring no property, tenant, damage or outcome fact from neighbors.
A bare image may also carry the photos schema without turning this template into a category.

---

## NEEDS-JOSEPH

- **NJ-CP-11 · Letting or general condition-proving row?** (a) Keep tenancy plus pre-works schedules;
  cost: some professional schedules sit near `survey-valuation`. (b) Narrow to tenancy/deposit framing;
  cost: pre-works schedules lose their only comparison-lifecycle home and may fit neither geometry nor
  reliance. Recommend (a), with abstention for unframed middle cases.
- **NJ-CP-12 · May a frozen tree separate check-in and check-out?** (a) Permit year-first; cost: paired
  evidence splits. (b) warn/propose a shared pair branch; cost: enforcement beyond freely editable
  recommendations. No constraint invented.
- **NJ-CP-INV-3 · Third-party interior imagery lacks a machine-readable catalogue rule.** (a) prose
  only; cost: strongest privacy leg unenforced. (b) catalogue marker for concentrated third-party /
  private-location imagery; cost: new vocabulary beyond this field-less row.
- **NJ-CP-INV-4 · R1c reciprocity.** Merge the new `site-survey` edge against that neighbour's memo and
  the revised `survey-valuation` discriminator centrally. Neighbours were not edited.

---

## What changed in this pass

**Preserved:** verdict; `fields: []`, `proposed_fields: []`, `dimension_order: []`; all nine fixtures;
recognition, work types, grouping, residuals, sensitivity and the two original open questions.

**JSON changes:** (1) retired the gist label and narrowed the claim that every document is useless
alone; (2) revised the `survey-valuation` discriminator to match its reliance/costed-breach versus
tenancy/deposit/check-in boundary and require abstention in the middle; (3) added the reciprocal
`site-survey` collision on the same image-set seam its memo names; (4) removed the invalid word-only
IT-asset-inventory collision. No canonical key was minted.

**Memo additions:** schema-default comparison; full three-leg test; format/value existence challenge;
rejected files; both collision directions; reciprocal boundaries; asset-inventory non-edge; two new
NEEDS-JOSEPH items; and this auditable change log.

The row is shorter than a schema anchor because it declares no fields and argues one narrow situation.
That is honest scope, not missing depth.

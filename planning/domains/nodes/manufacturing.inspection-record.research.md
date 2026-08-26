# Research memo — `manufacturing.inspection-record`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/manufacturing.inspection-record.json`
Roster row: template on the fieldless `manufacturing` schema, `parent_id: null`, placeholder launch

## Result

**Accept the node**, on two of the three node-test legs, and say plainly that it is not saved by the
third. The row survives because its detection signal is a stricter structure than the schema default's
(a per-row *stated limit* beside a per-row *measured actual*), and because its recommended parent
dimension **inverts** the schema default rather than nesting beneath it. Its privacy posture is the
schema's, unchanged, and I do not pretend otherwise.

`fields: []`, `proposed_fields: []`, `dimension_order: []`, `time_first: false`.

## The charge — the strongest case that this row should not exist

I put three forms of the charge, hardest first.

**1. It is a `work_type` value, not a node.** This is the strongest form and it is nearly fatal. The
manufacturing schema anchor's own `work_types[]` array already contains, verbatim, `"incoming,
in-process or final inspection and test record"` and `"certificate of analysis or conformity"`. The
anchor also proposes a `record_type` key whose example value is `"batch production record"`. So on the
anchor's own account, "inspection record" is a **value of a field** — exactly the shape the dispatch
prompt forbids: *"Work types are values. `work_types[]` is an enum of values for a `work_type` (or
equivalent) field. Do not ask R1a for a child node per work type."* If this row is real, then by the
same logic `manufacturing.calibration-record`, `manufacturing.production-record` and
`manufacturing.maintenance-work-order` are also just values, and the manufacturing subtree is a
document-type taxonomy wearing node clothes. That is the 574's original mistake restated.

**2. It is a duplicate of its own schema's default template.** The anchor's second deterministic
signal reads `"an in-process or final-inspection table with characteristic, specification/tolerance,
measured result, pass/fail or disposition, instrument identifier and inspector/date slots"`. That is
my detection signal, written by someone else, already firing. A template exists only where signals,
dimensions or privacy differ from the default; if the default already fires on all my evidence and
files it product → lot → record_type, I add nothing.

**3. It is a lifecycle stage.** Inspection is the QC step of a production cycle whose document —
the traveller — literally contains inspection sign-off rows. A stage of a process already held by
`manufacturing.production-record` is not a filing situation.

I also checked the two remaining refusal shapes and neither applies: this row is not an organisation
name (never-alone evidence), and it is not defined by the *absence* of something. That second one
needed care, because "an inspection record is a measurement that did not become an NCR" is a
tempting and illegitimate definition. It is not the definition used: this row is defined by the
**presence** of the limit-and-actual pair, and `manufacturing.nonconformance-capa` by the presence of
an event identifier plus containment structure. A REJECT row does not evacuate this row.

## Defeating the charge

**Against (1) — a value cannot carry its own parent.** A `record_type` value is a leaf; a leaf is
filed under whatever parents the default supplies. The default's parents are `product` then
`batch_lot`, and the anchor defines `batch_lot` as *"a production quantity made under substantially
shared conditions"* — a quantity **the holder made**. A large share of real inspection evidence has no
such quantity anywhere in it:

- `FAI-Report_AS9102_BPA-210-001_SN0004.pdf` is anchored to a part number, a drawing revision, a
  serial number and a purchase order. There is no produced-lot slot on an AS9102 form set.
- `Material Test Report - Heat 4471822 - 316L bar - EN 10204 3.1.pdf` is anchored to a **supplier's**
  heat on incoming stock. The holder produced nothing yet.
- `CMM_BPA-210-001_SN0004_2026-05-12.csv` is anchored to one serial.

Filing any of these under a produced lot requires either inventing the lot fact or stranding the file.
`00` is explicit about what a parent must do: *"The recommendation should follow the practical rule
that a parent dimension should provide the context required to understand the child."* The default's
parent chain cannot provide that context here. A thing that needs a different parent than the default
supplies is a situation, not a value. That defeats the charge.

**Against (2) — the difference is the recommendation, not the signal.** I concede the anchor's signal
overlaps mine. The template test in CONNECTION.md is disjunctive: signals **or** dimensions **or**
privacy. My dimension recommendation inverts the default — inspected article (serial, else consignment
identity, else produced lot) first, product above it only in multi-product corpora, record function as
leaf. That is a real difference with a real consequence for what folders get built. I strengthened
the signal too, but I rest the acceptance on the dimension leg.

**Against (3) — the traveller records that a check happened; this row records what it measured.**
Those are different bytes with different identities and different retention. `BPR_AX410_L240817-03.pdf`
has a quality-release sign-off and stays with `production-record`; `Final inspection AX410 lot
L240817-03.csv` — also the anchor's own fixture — is mine. Both directions are written into the
`collides_with` entry, naming the same two files on both sides.

## Sources used

- `planning/domains/dispatch/RESEARCH-BRIEF.md`, read in full.
- The stamped assignment from `make_prompt.py manufacturing.inspection-record`.
- `planning/domains/nodes/legal.practice-matter-file.research.md` — one landed launch row, for depth
  calibration and house idiom.
- `planning/domains/nodes/manufacturing.json` — the schema anchor, read in full. It is the default
  template I am measured against, and its `work_types`, `recognition` and `template.why` are the
  material for the charge above.
- `planning/domains/roster.json` — confirmed my id, kind, schema and the nineteen manufacturing
  sibling ids and seven logistics ids used for edges.
- Neighbour nodes located by one grep for my id: `engineering.verification-validation.json`,
  `engineering.material-specification.json`, `engineering.product-certification.research.md`,
  `engineering.risk-analysis-fmea.research.md`.
- `planning/00-database-agent-product-design.md` — reached by grep, three spans verified verbatim
  before quoting (session-not-topic; parent-provides-context; project-function-subject-before-time).

## Neighbours who already argued a boundary against me — honoured, not re-litigated

Three landed rows had already named my fixtures. I adopted their resolutions rather than contesting
them, and wrote the reciprocal direction on my side using **the same file names**:

- `engineering.verification-validation` calls me *"the sharpest collision on the node"* and resolves
  `FAI-Report_AS9102_BPA-210-001_SN0004.pdf` and `LOT-24-081_Final-Inspection.xlsx` to **me**. It also
  authored a `role_split` against me on "a serialized unit carrying a signed conformity table", with
  its side keyed to requirement identifiers and mine to drawing characteristics. I wrote the collision
  reciprocally with those exact fixtures. I did **not** write a matching `role_split` back: the split
  is already authored once, from the side that owns the requirement key, and duplicating it would put
  two authorities on one seam. R1c should confirm that judgement.
- `engineering.material-specification` resolves `Material Test Report - Heat 4471822 - 316L bar -
  EN 10204 3.1.pdf` to me and `MS-4120 Rev D` to itself. Both files appear in my `file_examples` with
  those verdicts, and my collision text mirrors its discriminator (measured result plus consignment
  identity versus criteria plus named method).
- `engineering.product-certification` deliberately declined an edge to me, on the ground that the
  engineering schema row already states the design-versus-execution boundary and a third claimant on
  one file is worse than a missing edge. I respected that and wrote no edge back to it.
- `engineering.risk-analysis-fmea` dismisses me in one line as *"a pass/fail table, already
  never-alone on the anchor."* Correct; no edge either way.

## Files considered and rejected

Named false positives, each with the discriminator, all present in `file_examples` so the rejection is
testable rather than asserted:

| File | Why it is not mine | Where it goes |
|---|---|---|
| `Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf` | **The collision fixture.** Applied-value / indicated-value / permitted-error table, signed, accredited — structurally indistinguishable from a conformance sheet. The measured object is the *instrument*. Discriminator: as-found **and** as-left pair plus a next-due date. No article inspection has an as-left value. | `manufacturing.calibration-record` |
| `Gage R&R Study - CMM-02 - operators A B C.xlsx` | Repeated measurements of real parts, but **no specification limits at all** — the variance is attributed to the measurement system, not to the parts. | `manufacturing.calibration-record` |
| `NCR-2026-041 cracked housing.pdf` | The condition is narrated against a requirement, not scored per characteristic against a limit; carries an event identifier plus containment and disposition. | `manufacturing.nonconformance-capa` |
| `MS-4120 Rev D` | Names test methods, states property ranges, contains no heat, lot, serial or measured value. Naming a method is not performing one. | `engineering.material-specification` |
| `BPR_AX410_L240817-03.pdf` | Rows are operations completed in sequence; the inspection row records that a check *happened*. | `manufacturing.production-record` |
| Blank `QF-071 Final Inspection Record Rev 3` | Identical grid to `LOT-24-081_Final-Inspection.xlsx`, with a document number and issue revision and **no article and no values**. | `manufacturing.quality-management-system` |
| `Packing list L240817-03.pdf` | Shares the lot token with my inspection sheet — the purest never-alone trap on this row. Quantities shipped, no limits, no actuals. | `logistics.shipment` / Receipts and Confirmations |
| `SPC Xbar-R chart - Line 2 - dimension A - 2026-Q3.xlsx` | Subject is a characteristic over time across many lots; control limits are computed from the data and are not specification limits. No inspected article. | Unclaimed — Review Later, and NJ-INSP-2 |
| `IMG_9042.jpg` | A weld beside a steel rule, no marking in frame. Visual inspection evidence with no article identity of its own. | One-Off Images; may join a packet without receiving its facts |
| `Inspection sheet scan 0007.pdf` | OCR recovers three numeric columns but not the headers — which column is the limit and which the actual is unrecoverable. | Review Later |

A source-system rejection too: a CMM or gauge software database, a QMS instance, or an inspection
mailbox is a **source system**, not one file node. A bounded export with a readable manifest is
represented (`Inspection package SN0004.zip`); live ingestion is a later connector decision.

## The three-way discipline this row exists to enforce

The reason the manufacturing subtree needs this row rather than one merged quality node is that three
near-identical tables must be told apart, and only a rule about **what the measurement is about** does
it:

1. Measured object is a produced or received **article** → this row. Instrument appears as provenance.
2. Measured object is the **instrument** → `calibration-record`. Marked by as-found/as-left and a due date.
3. Measured object is the **measurement system** (instrument + operator) → also `calibration-record`.
   Marked by repeated trials and absent specification limits.

A merged node would have to hold all three and could then never state a discriminator, because the
discriminator is precisely the boundary between them.

## Fields and dimensions — why nothing is proposed

`proposed_fields` is empty, deliberately, and this was the closest call in the row. The obvious gap is
an **article identity** key: the schema anchor's `batch_lot` is defined as a produced quantity, and my
most common anchors are a serial and a supplier's heat. The brief says to reuse an existing proposal
rather than mint a variant, and the anchor's `batch_lot` proposal can absorb both if R1c widens its
definition to "any traced material quantity" and lets the produced-versus-received distinction ride on
the `logistics.shipment` role_split I authored. Minting `serial_unit` or `consignment` here would
create exactly the private synonym the overnight pass produced thousands of. So: nothing minted, the
gap recorded as NJ-INSP-1 with both alternatives spelled out.

Rejected outright: `record_type` is already the anchor's reuse proposal and its Finance-scoping is the
anchor's NJ-MFG-1, not mine to re-open. `asset` is available for the measuring machine on a CMM export
and I used it in `facts_legal` there, but it must never become a dimension on this row — filing
article inspections under the machine that measured them scatters a unit's evidence across gauges.
`site` appears only where a receiving location is labelled. `quality_event` belongs to the CAPA row.

`dimension_order` is `[]` by placeholder contract; the inversion lives in `template.why` as prose for
R1c. `time_first: false`, and this row is the clearest case for that rule — a unit's incoming,
in-process and final records are deliberately months apart, so a year-first tree guarantees the
scatter `00` warns about.

## Recognition boundary

Strong evidence is always a **pair**: a stated limit and an actual value on the same row, plus an
article identity in a labelled slot. Weak evidence stays weak in combination — quality vocabulary,
part numbers, supplier letterheads, accreditation logos, signatures, cited standards, folder names,
lot-shaped tokens and download sessions. Two never-alone entries are aimed at specific tempting files:
*"a cited standard or test-method designation alone"* trips `MS-4120 Rev D`, and *"an as-found value
alone: as-found WITH as-left and a due date is calibration evidence"* trips the load-cell certificate.
A third, *"a numeric result column alone"*, trips the shift log and the SPC chart.

Activation ≠ grouping is live here. `IMG_9042.jpg`, `Inspection sheet scan 0007.pdf`, `Packing list
L240817-03.pdf` and the SPC chart all carry `group_without_copying_facts: true`: they may be retrieved
into a candidate packet around one serial without any article, heat or lot fact being written onto
them.

## Neighbours considered that got no edge

- **`business_operations`** (named in `must_consider_neighbors`) — a QC tracker spreadsheet with
  owners, due dates and status is genuinely tempting, but it has no limit-and-actual pair, so nothing
  here fires on it; the `never_alone` entry on a bare results column already handles it. The closer
  claimant for audit and QMS-shaped material is `manufacturing.quality-management-system`, which I did
  edge. Adding a `business_operations` edge would put a third claimant on one file for no gain.
- **`logistics`** (also named) — handled as a `role_split` on `logistics.shipment` rather than a
  collision, because the contested thing is one identifier in two roles, not one document two rows
  want. `Packing list L240817-03.pdf` is custody evidence on both sides.
- **`manufacturing.supplier-qualification`** — `also_holds_with`, not a collision: the MTR's property
  tables and its issuer-relationship context are disjoint evidence in the same bytes.
- **`manufacturing.failure-analysis`** and **`manufacturing.warranty-claim`** — both contain
  measurements, but each is anchored to a failure occurrence or a claim, which is the same
  occurrence-identifier discriminator that already separates me from `nonconformance-capa`. Restating
  it twice more would multiply claimants.
- **`engineering.product-certification`** — declined by that row for a stated reason; respected.

## NEEDS-JOSEPH

1. **NJ-INSP-1 — article identity.** `batch_lot` as the anchor defines it cannot carry a serial or a
   supplier heat. Alternatives: (a) widen `batch_lot` to any traced material quantity and let the
   produced/received distinction ride on the logistics role_split; (b) mint a separate article-identity
   key. This row mints nothing and recommends (a). Recommendation to R1c, not a change I made.
2. **NJ-INSP-2 — process-level measurement.** An SPC chart or capability study has measured values,
   specification limits and no inspected article. Candidates: this row, `manufacturing.production-record`
   (line evidence), `manufacturing.quality-management-system` (a control activity). Currently unclaimed
   and routed to Review Later rather than guessed.
3. **NJ-INSP-3 — the invisible acceptance act.** A supplier certificate that arrives with a purchase
   order and is never acted on may be incoming-inspection evidence or procurement paperwork; the
   discriminating act often leaves no file. Alternatives: require a receipt or acceptance reference
   before activation, or activate and mark the acceptance unknown.
4. **NJ-INSP-4 — one-sided role_split.** `engineering.verification-validation` authored a role_split
   against me; I did not author the mirror, to avoid two authorities on one seam. R1c should confirm
   whether reciprocal splits must be written on both sides or once from the field-owning side.

## Recommendations to R1c (no cross-row edits made)

- Widen the anchor's `batch_lot` per NJ-INSP-1, rather than accepting a new key from this row.
- Confirm the one-sided role_split convention (NJ-INSP-4).
- If NJ-MFG-1 resolves `record_type` into a global document-function key, this row's leaf dimension
  becomes serializable without further research.

## Self-verification

- JSON parses; key set matches the landed launch siblings, plus the `node_test` block those rows carry.
- Every `file_examples.source_type` is in `SOURCE_TYPES`; no file example writes a folder path as a fact.
- Every edge id was read out of `roster.json` (`engineering.verification-validation`,
  `engineering.material-specification`, `manufacturing.calibration-record`,
  `manufacturing.nonconformance-capa`, `manufacturing.production-record`,
  `manufacturing.quality-management-system`, `manufacturing.supplier-qualification`,
  `logistics.shipment`) or is a schema id (`engineering`, `photos`). All five `falls_through_to`
  values are `00` §7.3 residual names.
- All three `00` quotations were grep-verified verbatim before being written.
- No thresholds, no confidence scores, no handling classes, no minted field keys.
- Only the two assigned files were written.

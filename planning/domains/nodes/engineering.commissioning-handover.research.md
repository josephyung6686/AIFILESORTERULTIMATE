# Research memo — `engineering.commissioning-handover`

Date: 2026-08-26
Depth: J-DEPTH
Output: `planning/domains/nodes/engineering.commissioning-handover.json`
Roster row: template on the fieldless `engineering` schema, `parent_id: null`, placeholder launch
Absorbs legacy row: `eng.as-built-record`

## Result

**Accept.** `refuse_node: false` — after a serious attempt to kill it, recorded below because two of the five
objections are strong enough to have refused a weaker row and both survive as NEEDS-JOSEPH items.

The distinguishing relation is **custody transfer of a located instance**: a three-place relation among (1) an
identified **installed instance** — a tag, loop, unit, skid or serial naming one physically located copy of a
design item, (2) an **acceptance-and-transfer act** with two named parties and a date that starts a defects or
warranty period, and (3) the **controlled design definition** the instance is reconciled against. No other
roster row requires all three; the engineering schema default requires none of them.

`fields: []`, `template.dimension_order: []`, `time_first: false`. One `proposed_fields` entry, a reuse not a mint.

## Sources

Standing brief and stamped assignment. `legal.practice-matter-file.research.md` for depth calibration only.
`engineering.json` (the schema anchor — `template`, `recognition`, `node_test`, `proposed_fields`,
`sensitivity_why`, edges). `manufacturing.json` (`proposed_fields`, `template`) to find whether an instance key
already existed — it did: `asset`, example `CNC-07`. `construction_property.construction-project.json` (the row
that already claims the handover envelope) and `construction_property.compliance-certificate.json` (the refused
certificate row). `roster.json` and `canonical_fields.json` for id and key checks.
`00-database-agent-product-design.md` reached by `grep -n` only, per the brief's token discipline; lines 45 and
120 supplied every quotation, all verified verbatim by substring match before the JSON was written. I did not
read `00`, `01` or `CONNECTION.md` in full; nothing here turns on a stamped-prompt/CONNECTION difference.

## THE CHARGE — the case that this row should not exist

### Objection 1 (strongest): it is a lifecycle stage, i.e. a VALUE

The anchor proposes `lifecycle_stage` spanning "concept, preliminary design, detailed design, qualification and
released design". Commissioning and handover is the terminal station of exactly that progression. If the row is
`lifecycle_stage = commissioning`, it is a value of a field on its own schema — an outright refusal condition.

**Answer.** Co-extension fails in **both** directions, which is what separates a situation from a stage label.
Files in the row whose stage value is earlier: a commissioning plan is written during detailed design; a
Factory Acceptance Test specification is agreed at procurement. Both are constituted by the acceptance relation
they set up, not by when they were written. Files at the stage that are not the row: a design review held
during the commissioning window is `engineering.stage-gate-review`; a change raised because commissioning found
an error is `engineering.change-order`; a close-out cost report from the same fortnight is
`business_operations.project-delivery`. The decisive asymmetry: a stage is a property of one artifact's
maturity, whereas this row is a property of a **relation between two parties**, and `lifecycle_stage` has no
place to record who took custody. The stage is a **correlate**, not the definition — but close enough that it
is surfaced as NJ-ENG-CH-1 rather than smoothed.

### Objection 2: it is a bundle of document types

As-built drawings, test certificates, O&M manuals, spares lists, warranties, training records — a row whose
only content is a document-type inventory is a file-kind node in disguise.

**Answer.** Every one of those exists independently elsewhere and none activates the row alone (asserted in
`never_alone`, true of the file list). An O&M manual for a domestic boiler is a compliance situation on
`construction_property`; a calibration certificate is manufacturing evidence whether or not it travels in a
pack; a spares list is procurement. What makes the bundle a bundle is the single transfer act that assembled
it — `00`'s purpose facet exactly: **"The documents are content-incoherent but purpose-coherent."** A
content-similarity system splits a handover pack into drawings, spreadsheets, PDFs and a zip; a human keeps it
whole because it changed hands as one thing.

### Objection 3: it duplicates `engineering.verification-validation`

Both hold witnessed test evidence with expected-versus-recorded columns, pass/fail and signatures.

**Answer.** The **object of proof** differs, visibly, in the file's own slots. V&V proves the **design**
satisfies a requirement — discriminating structure: a stable requirement identifier joined to a verification
method and configuration-under-test. Commissioning proves the **instance actually installed** behaves as its
design definition says and that a named party accepts it — discriminating structure: a tag plus witness
signature slots for both delivering and receiving party. Same fixture on both sides:
`SAT-Report_Chiller-CH-02_2026-06-14_witnessed.pdf`. Bare (tags, setpoints, two witnesses) it is this row;
extended with `SYS-REQ` identifiers and a method column it legitimately holds both. A design verification
report on a prototype has no instance and no counterparty and is never this row.

### Objection 4: the coverage is already claimed

`construction_property.construction-project` says of the handover envelope: *"RETAINED AS THIS ROW'S OWN, and
the reason the row survives after the demotions above."* Its own `open_question` treats the envelope as one of
four structures justifying its existence. Two rows cannot both own it.

**Answer, part concession.** The anchors already hold the seam: `construction_property` keys on a property/site
joined to a professional instruction or contract; `engineering` keys on a design item/configuration definition.
A pack anchored to a contract at an address — parties, contract sum, programme, practical-completion
certificate — is theirs. A pack anchored to a tagged system reconciled against a released design definition —
loop checks, SAT results, setpoints, an as-built P&ID superseding an issued-for-construction revision — is
mine. Real plant packs carry both, and both anchors license coexistence. I authored the mutex rather than
conceding, but NJ-ENG-CH-2 records that R1c must ratify it reciprocally, naming the same
`Handover Pack - Harbour Works.zip` bytes on both sides. If R1c rules for the neighbour on site-bound packs,
this row still holds cases that row cannot reach at all because they have no property: a packaging line, a
vehicle fleet system, a laboratory instrument, a shipborne system.

### Objection 5: it is defined by an absence

"Engineering after engineering stops" — the leftover bin at the end of the lifecycle.

**Answer.** Its two required structures are positive and additive: an instance identity the schema default
never needs, and an acceptance act the schema default has no concept of. The row demands *more* evidence than
its schema, not less. A file merely lacking design-change evidence lands in Review Later, not here.

**Verdict: accept**, with objections 1 and 4 escalated rather than buried.

## The node test, argued in full

A template exists only when its **detection signals**, **recommended dimensions**, or **privacy rules** differ
from its schema's default. All three differ.

**The engineering default template**, from the anchor: it fires on "a relation among an identified design item,
a lifecycle/design state, and controlled technical artifacts", with conditional order
`project → design_item → lifecycle_stage → engineering_artifact_type`, `time_first: false`.

**Leg 1 — detection signals.** The default is satisfied by an item plus a controlled artifact: a title block
with a revision, a requirements table with verification columns, a BOM with parent/child rows. This row is
satisfied by none of those. It adds (a) an installed-instance identity — a released drawing package for
"Chiller model CH-2000" has no instance; a SAT sheet for "CH-02, Plant Room 3" does — and (b) an
acceptance-and-transfer structure with two named parties, a takeover date, a period running from it, and a
punch list carrying owners. **Either alone fails**: an AS BUILT stamp with no pack and no acceptance is
`engineering.drawing-package`; an acceptance certificate with no reconciled technical definition is a contract
or project-closure record on a neighbouring schema. Requiring the conjunction is what keeps this from being a
keyword row.

**Leg 2 — dimensions, and they differ at the top level.** The default leads with project then design item. This
row **inverts the top**: `asset → design_item (or project) → engineering_artifact_type`. Structural, not
stylistic: one design item legitimately produces many separately-handed-over instances — twelve identical air
handling units, four substations to one drawing — each with its own acceptance date, punch list, warranty start
and witnesses. Leading with the design item merges twelve distinct transfers and loses the fact that makes each
retrievable. This is `00`'s parent-makes-child-intelligible rule applied one level lower than the schema
applies it: a punch item and a warranty date are meaningless without the unit, as Homework 3 is meaningless
without the course. Not time-first, deliberately — acceptance date, test date, document date and warranty start
are four different dates on one pack, so any as a first level scatters one transfer across calendar folders.
Serialized as `[]` under PR-6; the recommendation is held in prose in `template.why`, not silently encoded.

**Leg 3 — privacy rules differ in kind.** The schema's stated reason is proprietary design definition and
export-controlled technical data — an IP concern. This row's concern is **live operational access to a running
installation**: control-system backups with delivered engineering passwords, BMS/SCADA account schedules, alarm
and interlock setpoints, key and access-control schedules, plant-room locations, and named operators with
employers and signatures. Design IP stops mattering when a product is superseded; a default PLC password on an
operating plant does not. That argues for excerpt-only recognition and Protected Records routing on members the
default would treat as ordinary technical documents. Written as a posture, not a class — `sensitivity` stays
`potentially_sensitive`, the only value available this phase, and P7 owns classes.

## Bottom-up file set

Thirteen fixtures in the JSON, observations split from facts. Facts are written as `conditional on R1c: <key>`
throughout, because PR-6 means no fact is legal today and writing them as legal would misrepresent the
placeholder contract. What each is doing:

1. `Taking-Over Certificate - Package 4 - Substation SS-03 - signed.pdf` — the custody-transfer fixture. The
   structure nothing else on the engineering schema has.
2. `SAT-Report_Chiller-CH-02_2026-06-14_witnessed.pdf` — instance proof; shared bytes with V&V.
3. `210-PID-004 Rev D (AS BUILT).pdf` — the absorbed legacy `eng.as-built-record`; shared bytes with
   `drawing-package`. The reconciliation relation fires, not the AS BUILT words.
4. `Punch List - Harbour Pump Station - rev 7.xlsx` — the **owner** column separates an acceptance condition
   from an internal defect log; shared with `maintenance-work-order`.
5. `Handover Pack - Line 3 Packaging Cell.zip` — manifest read without extraction;
   `group_without_copying_facts: true`, so a calibration certificate inside stays independently manufacturing
   evidence and does not inherit the pack anchor.
6. `Asset Handover Schedule - Line 3.xlsx` — the role-split fixture; literally the seed of the operator's register.
7. `PLC-Backup-and-Setpoints_LINE3_v1.4.zip` — recognition signal and privacy trigger in one structure.
8. `Operator Training Attendance - Line 3 - 2026-06-20.pdf` — named third parties; must not conclude competence.
9. `RE Energisation window and witness attendance - SS-03.eml` — email as SOURCE_TYPE not domain; shared with
   `grid-connection`.
10. `IMG_4417.HEIC` — the sparse case. Joins a pack only through a legible nameplate tag matching an accepted
    anchor; `group_without_copying_facts: true` so membership never writes an asset fact onto the image.
11–13. The collision fixtures, below.

The set covers a labelled certificate, a labelled test form, a CAD-derived document, two spreadsheets, an
archive, a controls binary, free-text email, an image with OCR, and an unreadable file.

## The collision fixture

`Practical Completion Certificate - Harbour Works.pdf`. Tempting because it is structurally near-isomorphic to
a taking-over certificate: a signed transfer-of-responsibility document, two named parties, a date, and a
rectification period running from it — the same slots in the same order.

**Discriminator: the anchor of the two named parties.** A practical-completion certificate names contract
parties under a named building contract, references a contract sum and a site address, and is signed by a
contract administrator; it never names an equipment tag, never carries a test result, never references a design
definition being reconciled. A taking-over certificate names an identified system with instance identity and
points at the acceptance test results that justified it. Where a document genuinely carries both — plant handed
over under a construction contract — both rows hold. Where it carries only the contract anchor it is
`construction_property` in both directions and I do not take it.

Two further collisions carried: `LOT-24-081_Final-Inspection.xlsx` (production inspection of a **batch**, not a
located instance — citing drawing Rev C does not make it engineering evidence; the same fixture the anchor
already names against manufacturing, reused deliberately), and `Site Acceptance Test pack - client copy.zip`
(password-protected; the filename cannot manufacture an installation, an acceptance act or a sensitivity result).

## Files considered and REJECTED

- **A domestic boiler commissioning certificate / landlord gas safety record** — the most dangerous false
  positive, because *commissioning* sits in a labelled slot. `construction_property.compliance-certificate` is
  a refused row that routes certificates by owning situation and names "boiler or heating commissioning
  certificate" among its values. A dwelling's compliance record is not an engineered installation's transfer.
  Encoded as a `collides_with` against the refused row so the routing survives.
- **A generic O&M manual downloaded from a manufacturer's site** — no installation, no transfer, no
  reconciliation. The dossier is constituted by having been *delivered*; a download is not a delivery.
- **A calibration certificate alone** — manufacturing evidence; joins a pack only through an accepted anchor.
- **A project close-out report / lessons-learned deck** — `business_operations.project-delivery`. The word
  *handover* on every slide changes nothing.
- **A warranty registration confirmation email** — Receipts and Confirmations or Independent Records. A
  warranty start date is a slot on a handover schedule, not a handover.
- **A CMMS or asset-management system export** — a source system, not a file node.
- **A snagging list for a house purchase** — punch-list *shape* without an engineered instance and a delivery
  counterparty is not this row. This is why the owner column, not the defect rows, is the written signal.
- **A firmware release package** — `code` / `engineering.embedded-firmware`; contested only when delivered as a
  component of an installation's baseline, and then both hold.
- **A tender or contract pack** — the opening of a job, not the closing of one.
- **A design review deck held during commissioning** — `engineering.stage-gate-review`. Included because it is
  the counterexample that defeats Objection 1.

## Fields and dimensions

`fields: []` — binding. The engineering schema declares none under PR-6 and D1's deferral; a template may reuse
only what its schema declares.

`proposed_fields` contains exactly **one** entry, a **reuse not a mint**. `asset` (example
`CH-02 (Chiller 2, Plant Room 3)`) already exists as a proposal on the manufacturing anchor with example
`CNC-07`; the brief instructs reuse over variants, so `installed_instance`, `tag_number` and `unit_id` were
dropped in its favour. Why nothing existing covers it: `design_item` (anchor proposal) names the designed
configuration, and one design item yields many separately commissioned instances — the whole of Leg 2;
`location` (canonical) names a place, and two chillers in one plant room share a location but never a handover;
`project` (canonical) names the undertaking that delivered the instance, not the instance; `record_type` and
`artifact_type` are scoped to finance and to research/code, and the anchor has already exposed the
widen-or-role-specific question as NJ-ENG-1, which I do not duplicate.

Reusing manufacturing's `asset` is the substantive proposal and is deliberate rather than convenient: the same
key on both sides of the transfer is what makes the `manufacturing.asset-register` boundary a `role_split`
rather than a collision. The cost is recorded as NJ-ENG-CH-3 — one key carrying different reliability rules on
each side of the seam.

`template.dimension_order: []`, `time_first: false`; the prose recommendation and its inversion of the default
are argued in Leg 2 and stated in `template.why`.

## Reciprocal boundaries

Each names the same fixture bytes on both sides.

| Neighbour | This row fires when | They fire when | Shared fixture |
|---|---|---|---|
| `construction_property.construction-project` | pack anchored to a tagged system reconciled against a design definition | pack anchored to a contract at a site — parties, sum, programme, PC certificate | `Handover Pack - Harbour Works.zip`; `Practical Completion Certificate - Harbour Works.pdf` |
| `engineering.verification-validation` | object of proof is the located instance plus a counterparty accepting it | object of proof is the requirement, via stable identifiers and a method column | `SAT-Report_Chiller-CH-02_2026-06-14_witnessed.pdf` |
| `engineering.drawing-package` | terminal reconciled record inside a pack with an acceptance act | one issue in a live controlled sequence, still under change control | `210-PID-004 Rev D (AS BUILT).pdf` |
| `business_operations.project-delivery` | tag-level technical acceptance | schedule, budget, governance, delivery status | `Project Closeout Report - Harbour Works.pptx` |
| `resource_operations.grid-connection` | plant handed to whoever will run it, network or not | connection agreement, connection point, network-operator counterparty | `RE Energisation window and witness attendance - SS-03.eml` |
| `construction_property.compliance-certificate` (refused) | certificate arrives as a member of an engineered transfer, keeping its own meaning | dwelling/premises compliance situation, routed per that row's refusal | domestic boiler commissioning certificate |
| `manufacturing.asset-register` (role_split) | the unit as a **deliverable** | the unit as an **operated** asset | `Asset Handover Schedule - Line 3.xlsx` |
| `manufacturing.maintenance-work-order` (role_split) | punch items as conditions of acceptance, owned by the deliverer | work orders raised by the operator in service | `Punch List - Harbour Pump Station - rev 7.xlsx` |

Where the side of the taking-over date is unclear on a punch item, the file goes to Review Later rather than
being assigned by guess. Stated in the JSON so the ambiguity is not resolved silently.

## Neighbours considered that got NO edge

`engineering.change-order` — commissioning generates changes, but a change order is recognised by its own
affected-item and disposition structure; sequence adjacency is not same-evidence confusion.
`engineering.process-plant-design` / `civil-structural` — discipline containers whose evidence is design
definition, already covered by the schema seam; edges would encode a discipline taxonomy this pass must not
build. `engineering.product-certification` — type approval attaches to a product **type**, not a located
instance being transferred. `construction_property.snagging-defects` — genuinely close on punch-list shape, but
its anchor is a job at a site, already carried by the `construction-project` collision; R1c may promote it, but
I did not add a second edge into one family to say the same thing twice. `research` — named in
`must_consider_neighbors` and rejected deliberately: commissioning a laboratory instrument produces this row's
evidence, and the research relation is about knowledge production, which the pack never claims. `code` — kept
as `also_holds_with` only, on the controls-backup case; a repository is not a handover.

## Open questions — NEEDS-JOSEPH

**NJ-ENG-CH-1 (existential).** If R1c ratifies `lifecycle_stage`, does this row survive or collapse into the
value? This pass argues survival on the two-way failure of co-extension. Alternatives: (a) keep the row and
accept that stage and row correlate strongly; (b) demote to a value, route as-built reconciliation to
`engineering.drawing-package` and acceptance evidence to `engineering.verification-validation`, and accept that
the custody-transfer relation is lost — nothing else on the roster records who took the thing.

**NJ-ENG-CH-2 (contested territory).** `construction_property.construction-project` names the handover envelope
as the reason it survives its own demotions. R1c must ratify the seam reciprocally or one of the two rows loses
its centre. Alternatives: (a) ratify as written — system-and-design-definition versus job-at-a-site, both
holding on genuine plant packages; (b) give all site-bound packs to `construction_property` and leave this row
the non-site cases (packaging lines, vehicle systems, instruments, marine); (c) give all engineered-system
packs here and leave that row the contract envelope without the pack, reopening its own existence question.

**NJ-ENG-CH-3 (key reuse).** Is one `asset` key correct across manufacturing and engineering, or does the
deliverable/operated distinction need two? One key plus a `role_split` is recommended and is what makes the
register boundary coherent, but the field then carries different reliability rules on each side of the seam.

**NJ-ENG-CH-4 (privacy granularity).** May credential-bearing members route to Protected Records while the rest
of the pack stays grouped, or must the whole pack inherit the strictest posture? Splitting is recommended;
inheriting is safer and would make a large ordinary technical corpus invisible to the user who owns it.

Inherited and not re-litigated: NJ-ENG-1 to NJ-ENG-4 on the anchor. NJ-ENG-3 (site-bound design packages) is
NJ-ENG-CH-2 seen from the schema.

## Self-verification

- `python3 -m json.tool` parses. Key set matches `engineering.json`, with `node_test` extended to carry the
  three differ-from-default legs (the anchor's carries `distinct_field_set`, correct for a schema).
- All six `00` quotations verified verbatim by substring match against the source — five residual definitions
  from line 120, the purpose-coherence span from line 45.
- All thirteen edge ids programmatically confirmed present in `roster.json`; all five `falls_through_to` names
  are `00` residual templates.
- Every `file_examples.source_type` is in `SOURCE_TYPES`. No file example writes a folder path as a fact.
- No threshold numbers, no handling classes, no `public_low`, no invented regex or gazetteer content.
- Two files written, both mine. No neighbour node, roster, `canonical_fields.json`, `check.py`, `src/` or SPEC
  touched.

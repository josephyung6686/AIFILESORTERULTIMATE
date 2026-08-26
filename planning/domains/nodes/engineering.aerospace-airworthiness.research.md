# engineering.aerospace-airworthiness — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.aerospace-airworthiness.json`](engineering.aerospace-airworthiness.json).
Salvage: none — no prior draft, and no sibling `engineering.*` template had landed. Every edge below
is written from this side and is a **recommendation to R1c** for reciprocation, not a claim the
neighbour agrees.
Verdict: **kept**, narrowed, on two of the three node-test legs. The third is recorded as a failure.

## Sources used

- The standing brief and the stamped assignment (`make_prompt.py engineering.aerospace-airworthiness`):
  `must_consider_neighbors` = manufacturing, code, research; residuals = Independent Records,
  Review Later.
- **`planning/domains/nodes/engineering.json` — the anchor I am measured against.** Read via its
  parsed sections (`node_test`, `proposed_fields`, `recognition`, `template`, `work_types`, edges,
  `sensitivity_why`). Its `.research.md` was **not** opened: the JSON stated the default template,
  the proposed keys and the schema-level collisions unambiguously, so the node test was decidable.
- `CONNECTION.md` §2, read at source: *"A **template** row exists only if its detection signals,
  recommended dimensions, or privacy rules differ from its schema's default template"*, and the
  adjacent ban on *"An **empty industry label** — a row whose only content is a name and a
  one-liner"*.
- `_CONTRACT.md` rule 14, read at source. It settled three things: the edge vocabulary is closed;
  **`also_holds_with` joins schemas only**, so this template's list is empty; **`collides_with`
  joins same-kind pairs**, so every collision below is a *template* id, never one of the anchor's
  five schema-level collisions.
- `00-database-agent-product-design.md` — grepped, never streamed. Five spans used, all matched
  verbatim before being written.
- `roster.json` — all edge endpoints resolved against `nodes[].domain_id` (358 rows); nineteen
  neighbour `one_line_hint`s pulled in one pass.
- `canonical_fields.json` — the 37 keys. No canonical key names an approval or an individual
  article. `manufacturing.json`'s proposed keys (`product`, `site`, `batch_lot`, `asset`,
  `quality_event`, `record_type`) are why NJ-AERO-2 names `asset` as a live alternative rather than
  minting a serial key here.
- `finance.crypto-assets.research.md` — depth calibration, read once.
- Real document types, named because their internal structure is the evidence: type certificate data
  sheet; certification basis and means-of-compliance checklist; authorised release / conformity
  certificate (the numbered-block one-page form); airworthiness directive; design-approval-holder
  service bulletin; certificate of airworthiness and airworthiness review certificate;
  weight-and-balance report and equipment list; directive and bulletin compliance record;
  life-limited-part traceability record; instructions for continued airworthiness. **Identifier
  strings in the fixtures are shapes, not claims** — no real certificate, directive or registration
  number is asserted, and none is needed: the signal is always the relation among labelled slots.

## THE CHARGE — the case that this row should not exist

Written before the JSON. Five prosecution arguments, strongest first:

1. **It is an industry name.** "Aerospace" is the same kind of word as "automotive" — a sector, not
   an organizational situation. The 574's recorded failure was taking an industry, noticing it has
   documents, and calling that a node. CONNECTION §2 forbids an empty industry label outright.
2. **It duplicates `engineering.product-certification`**, whose roster hint is *"The file that shows
   a product meets a regulation or a standard, and the certificate that comes out of it"* — on its
   face, this row's whole type-certification half. Swapping a conformity mark for a type certificate
   is a swap of **values**, and `00` is explicit that runtime values are not hand-authored rows:
   *"The system may create new values when it sees a new course, project, company, university, or
   event, but it should not invent new fields automatically"*.
3. **The other half duplicates `logistics.fleet-vehicle` / `manufacturing.asset-register` /
   `manufacturing.maintenance-work-order`.** *"One vehicle across its working life — acquisition,
   licensing, insurance, servicing, defects, fuel and disposal"* is the shape of an aircraft's life
   record. A tail number is a registration plate with a letter prefix.
4. **Its distinguishing tokens are vocabulary** — TCDS, STC, Form 1, AD, SB, MRB, CAMO: one
   jurisdiction's catalogue of form names, which is a value list.
5. **Its privacy story is already taken** — the anchor's `sensitivity_why` already names
   export-controlled and critical-technology information.

**Where the prosecution fails.** 4 and 5 land and are conceded in the JSON: the vocabulary went into
`work_types` as values, and `sensitivity_why` states in terms that privacy does **not** differ.
1–3 fail on one structural fact no named neighbour carries:

> This corpus is organised by an approval **held outside the organisation that wrote the data**, and
> its work is to keep proving — for years, and often for one serialised article at a time — that the
> thing still conforms to that external approval.

Every neighbour holds one half and refuses the other. `product-certification` is type-level and
terminates at issue: a conformity certificate does not follow one unit for thirty years, carries no
effectivity serial range, and is not superseded by a mandatory directive. `fleet-vehicle` and
`asset-register` are article-level and never reference an approved *type design*: a van's service
history has no clause tying it back to the approval it was built to. The anchor's own default is
neither — its `design_item` is a type-level configuration item, it has no article dimension at all,
and its `lifecycle_stage` runs concept → released, so it **ends** where this row begins.

The row survives only narrowed to that relation, which the `one_line` says explicitly: an aircraft
manufacturer's ordinary drawings, BOMs and internal requirements **stay on the schema default**, a
job done to an aircraft stays manufacturing, a published airworthiness code stays a received
standard. The industry word does no work anywhere in the recognition block.

## The node test, all three legs

The schema default, from the anchor: `project → design_item → lifecycle_stage →
engineering_artifact_type`, `revision_or_baseline` as metadata, `time_first: false`, machine-empty
under PR-6.

**Leg 1 — detection signals differ. PASSES.** The anchor's ten deterministic signals key without
exception on structures the design organisation wrote about its own baseline: a title block with an
item and revision; a requirements table with *stable requirement identifiers* and allocation,
rationale and verification-method columns; a TDP manifest; an engineering-change structure; a
design-authoritative BOM; an analysis comparing margins to named requirements; a verification
matrix; a prototype configuration record. This row's discriminators key on evidence an outside
authority wrote, or that was written to be handed to one:

- an **issuing-authority block** joined to a certificate-number slot, a *holder* slot, and an
  approved-model or effectivity list;
- a compliance matrix whose requirement column holds **citations to a published code at a stated
  amendment level** — not the organisation's own identifiers — beside a **means-of-compliance**
  column from a small authority-defined vocabulary and a **finding / acceptance** column;
- a **numbered-block release certificate** joining a part number and serial to an explicit statement
  of conformity to approved design data and a return-to-service authorisation;
- a **mandatory directive** whose applicability is a model *plus a serial range* and whose compliance
  time is in operating hours, cycles or a calendar limit.

None appears in the anchor's list; none of the anchor's ten discriminates them. The requirements
pair is load-bearing: both signals are the same *shape* — rows of requirements with trace columns —
and are told apart by whether the identifiers are **owned or cited**, and whether the terminal
column is an internal verification status or an external finding. That is a discriminator over
labelled slots, not a vocabulary preference.

**Leg 2 — recommended dimensions differ. PASSES.** Two of the anchor's four levels are dropped and
one it does not have is inserted.

- `lifecycle_stage` **dropped**: this corpus lives entirely at and after approval, so the
  concept/preliminary/detailed/qualification axis resolves to one value and opens a branch the facts
  cannot fill. What actually varies is *approval currency* — in force, superseded,
  directive-mandated, expired — which is not a design gate and must not be read into
  `lifecycle_stage` (the checklist fixture's `must_not_conclude` says so).
- `project` **dropped or demoted**: the approval outlives the programme. A data sheet issued decades
  ago and a modification approved last year belong to the same type; a project level scatters them.
- The **approval instrument** is inserted first, and on the continued branch the **individual
  article** is. Neither exists on the schema default.

The recommendation is branch-shaped, not one deep tree: `approval_instrument →
engineering_artifact_type` for type-design data, `design_item` above only where a corpus spans
several certificated types; `article → engineering_artifact_type` for the continued half.
`time_first` stays false although the compliance ledger is indexed by date, hours and cycles,
because compliance status is a property of an article and an approval — year-first would scatter one
article's life across calendar folders, which `00` warns against for record domains.
`dimension_order` stays machine-empty: PR-6 binds, and encoding a level whose key is not legal yet
is the silent guess the contract forbids.

**Leg 3 — privacy differs. FAILS, recorded as a failure.** Export control, distribution statements,
safety-critical vulnerability data and proprietary substantiation are all real here and all already
claimed by the anchor's `sensitivity_why`. The per-article half adds owner/operator identity to
technical records — a degree, not a kind. One of three legs suffices; two pass; the third is stated
rather than padded into a fourth argument.

## Files considered and **rejected**

- **`Airworthiness-Code_Large-Aeroplanes_Amendment-27.pdf`** — kept as a fixture *whose correct
  outcome is not firing*. Authority masthead and paragraph numbering, but no holder, no effectivity,
  no article, no finding column. `engineering.standards-library`'s: received, never authored here.
- **`WO-2026-0413_N214FR_Wheel-Change.pdf`** — the collision fixture (below).
- **`N214FR_Hull-Insurance-Certificate-2026.pdf`** — trips two never-alone rules at once, a
  registration mark *and* the word "certificate", with an aviation insurer's masthead. Its real
  structure is policy number, period of cover, sums insured.
- **An assembly drawing, `35-2140_MLG-Trunnion_Rev-C.dwg`** — excluded deliberately; including it
  would have made this an aerospace-industry folder. It is the schema **default template**,
  unchanged, and its presence in a directory named for an aircraft type is exactly the
  parent-folder-context case the last `never_alone` refuses.
- **A pilot's flight logbook and an aircraft technical log** — aviation, per-article, and
  *operations*: they record who flew what and what defects were reported, not conformity.
- **A parts purchase order citing part number and serial** — the pair is a listed `never_alone`
  precisely because this file exists.
- **Flight-crew training records / a type rating** — an approval, of a *person*. Nothing here fires.
- **An organisation approval certificate for a maintenance or continuing-airworthiness
  organisation** — the closest miss: an authority-issued certificate with a number and a holder,
  approving an **entity**, not a product. `business_operations.compliance-audit`; collision written.
- **A `.step` model referenced from a submission** — a packet member with no approval slot; the
  packet's approval reference must not be copied onto it.
- **A flight-test campaign's raw data set** — the one honest `also_schema: "research"` case, left
  off the fixtures because a raw data set does not itself *show* the co-activation. Named in
  `also_holds_with_note` instead of asserted on a fixture that would not demonstrate it.

## The collision fixture

**`WO-2026-0413_N214FR_Wheel-Change.pdf`.** It looks exactly like this row's evidence: registration
mark in the asset field, aviation vocabulary throughout, a task-card reference where a compliance
reference would sit, a completion timestamp where a compliance date would. It is
`manufacturing.maintenance-work-order`'s.

Discriminator: the page carries **execution slots and no approval slot** — labour hours booked,
parts consumed with quantities, raised-by and assigned-to — and nowhere a statement of conformity to
approved design data, an approval basis, or a next-due obligation. Its `facts_legal` is empty in the
JSON, which is the strongest thing this row can say about a file: not "fewer facts", but *none of
mine*. If the job ends with a release certificate, **that certificate** is this row's and the work
order still is not.

A second, softer collision is the compliance checklist against `engineering.product-certification`,
where the same bytes go either way depending on whether the approval carries a continuing obligation
on individual articles.

## Reciprocal boundaries

All ten are template-to-template (rule 14), each naming the **same fixture on both sides**:

| Neighbour | This row takes it when… | The neighbour takes it when… | Shared fixture |
|---|---|---|---|
| `engineering.product-certification` | the approval must be maintained after issue — effectivity range, continuing obligation, directive trail | the certificate is point-in-time conformity ending at issue | `Compliance-Checklist_Cabin-Interiors_Rev-D.xlsx` |
| `engineering.verification-validation` | the requirement traced is a cited code paragraph feeding a finding | the requirement traced is the organisation's own identifier | the flammability report the checklist references |
| `engineering.standards-library` | the document is written *against* a code | the document *is* the received code | `Airworthiness-Code_…_Amendment-27.pdf` |
| `manufacturing.maintenance-work-order` | a release or conformity record comes out of the job | the file is the job: labour, parts, task card | `WO-2026-0413_N214FR_Wheel-Change.pdf` |
| `manufacturing.asset-register` | the per-article document's purpose is conformity | its purpose is identity, location, permanent truths | `N214FR_Weight-and-Balance_2026-03-18.pdf` |
| `manufacturing.inspection-record` | it releases the item against approved design data | it measures the item against its drawing | `Release-Cert_PN-30-4412_SN-4471-2296.pdf` + its dimensional sheet |
| `logistics.fleet-vehicle` | the record proves continued conformity to an approved type design | the record is about operating the asset: licensing, insurance, fuel, servicing | `AD-Compliance-Record_N214FR_2026.xlsx` vs the hull-insurance certificate |
| `engineering.change-order` | the change is externally approved and carries effectivity | the change is the internal request and its disposition | `SB-32-1180_Rev-2_MLG-Actuator.pdf` |
| `manufacturing.safety-case` | the assessment is submitted to close a named code paragraph | the spine is a hazard list with claims and evidence | the system safety assessment |
| `business_operations.compliance-audit` | the finding is against a **product** approval | the finding is against an **organisation** and its procedures | the organisation audit report |

`fleet-vehicle` is the pair to watch: two rows told apart only by the *purpose* of a record both
index by the same registration mark, and both will see the same directory.

## Neighbours considered that did **not** get an edge

- **`code` / `engineering.embedded-firmware`** — a `must_consider_neighbors` entry, refused.
  Certified avionics software is real, but its discriminating structures are a repository, a
  manifest and a source tree, which this row's signals never touch. The anchor carries the `code`
  boundary at schema level; a template edge here would duplicate it without adding a fixture.
- **`research`** — the other named neighbour. The genuine case is co-activation on a flight-test
  campaign, not collision, and co-activation on a template goes through `also_schema`, not an edge.
- **`engineering.automotive-program`** — the closest sibling by construction ("its type approval").
  No edge, because the collision is speculative until that row lands and says whether it claims type
  approval as a relation or a milestone. Raised as **NJ-AERO-3**, where it threatens this row's scope.
- **`construction_property.compliance-certificate`** — shares the certificate word and nothing else.
- **`identity.core-documents`** — a registration document is title for an article, not for a person.
- **`manufacturing.calibration-record`, `manufacturing.warranty-claim`** — per-article and tempting;
  calibration concerns measuring equipment's own fitness, warranty is a commercial claim. Neither
  reaches an approval basis.
- **`role_split`** — refused, argued in `role_split_note`: three organisation roles sit on one page
  (issuing authority, approval holder, operator), rule 14 allows role_split over canonical keys only,
  the canonical `our_firm`/`client` pair would misdescribe all three, and all three are organisation
  names, which the row already treats as never-alone evidence.

## `proposed_fields` — one key, and one deliberate non-proposal

**`approval_instrument`**, for R1c. No canonical key names the externally issued approval under which
an item is legal to operate, and that approval is this row's join key: `record_type` and the anchor's
`engineering_artifact_type` say what a document *is*; `project` says what produced it and is outlived
by the approval; `design_item` says which item, and one item routinely carries a base type approval
plus several independently held modification approvals whose data must not be merged. `institution`
is the finance issuer key and cannot serve, since three organisations appear here in three roles. The
honest alternative is named in the proposal and in **NJ-AERO-1**: widen the anchor's
`revision_or_baseline`, since an approval *is* a baseline held outside the organisation. R1c must
pick one; shipping both as synonyms is the failure mode.

**The individual-article key was deliberately not proposed** — it is the continued branch's first
dimension and its absence is felt, but three live answers give three different products
(**NJ-AERO-2**), and that is a shared-vocabulary decision one template must not make. The recommended
order describes the level in prose without minting a key.

Nothing else was close. A registration mark, a serial, a part number, an ATA chapter and a directive
number are **values**, and the first three are listed as `never_alone` precisely so a stable,
readable, labelled token cannot be mistaken for a fact-bearing field.

## Sparse-file discipline

Two fixtures carry `group_without_copying_facts: true`. `pressure_curve.png` is this node's
`HW 3.pdf`: an unlabelled plot beside two accepted substantiation reports, with the neighbourhood as
the only thing suggesting a domain. It receives the universals and nothing else, and its
`must_not_conclude` covers both halves — no approval or article identity copied from neighbours, and
no inference from missing capture metadata. `FW_ Release cert for SN 4471-2296.eml` applies the same
discipline to mail: the subject line carries the strongest-looking token in the corpus and the
labelled evidence is in the attachment, so the mail groups and does not activate.

## Audits run before returning

- `python3 -m json.tool` — parses.
- All five `00` spans were grepped back out of `00-database-agent-product-design.md` and matched
  verbatim before being written: the four residual definitions (Independent Records, Review Later,
  Unsupported or Encrypted, Protected Records) from the residual-library paragraph, and *"extension
  as a routing signal rather than an assumption about meaning"*. The CONNECTION §2 spans quoted here
  were read at source. **No quotation is paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (13/13); `file_kinds.source_types` likewise.
- Every `collides_with.domain` resolves to a roster `domain_id` (10/10) and every one is
  `kind: template`, satisfying rule 14's same-kind constraint.
- Every `falls_through_to.residual_template` is one of `00`'s nine (4/4); every fixture's
  `falls_through_if_inactive` likewise (Reading Inbox and One-Off Images used once each).
- `fields`, `also_holds_with`, `role_split`, `dimension_order` all empty by a stated contract rule,
  each with a note naming which.
- `proposed_fields` holds exactly one snake_case key with `adjudicate: "R1c"`.
- No threshold, score, evidence count or handling class. Every digit is a fixture name, an identifier
  shape, or a prose reference.
- Only the two assigned files were written; the ownership register, roster, `canonical_fields`,
  `check.py`, `src/` and every neighbour node untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-AERO-1 — `approval_instrument` vs a widened `revision_or_baseline`.** An approval is a
  baseline held outside the organisation, so the anchor's key may already cover it. (a) Keep the
  role-specific key — this row's recommendation, because a certificate number and a design revision
  are read from different structures and browse differently. (b) Widen `revision_or_baseline` —
  cheaper for the vocabulary, but loads one key with an internal and an external meaning. **Not
  both.**
- **NJ-AERO-2 — no key for the individual article.** Half this corpus is indexed by a serialised
  article and no canonical key can say so. (a) Reuse manufacturing's proposed `asset` across schemas
  — cheapest, but couples two vocabularies and imports an operations meaning. (b) Widen
  `design_item` to admit an individual article as well as a type — stays in one schema, but blurs
  the type/article distinction this row exists to hold. (c) Mint an article-identity key — cleanest
  semantically, and immediately raises whether a registration mark may be a folder level, which
  publishes an asset identifier on the filesystem. **Recorded, not resolved; no key proposed.**
- **NJ-AERO-3 — scope, and the row's name.** If R1c narrows `engineering.product-certification` to
  point-in-time conformity, every *operating* approval that must be maintained — rail vehicle
  authorisation, marine class, road type approval — has the same relation and no home. (a) This row
  absorbs them, in which case its aerospace name is wrong and it should be renamed for the relation,
  not the sector. (b) It stays aviation-scoped and `engineering.automotive-program` holds the same
  relation for vehicles, accepting one duplicated structure across two rows. The largest open
  question about whether the row, as named, survives R1c.
- **NJ-AERO-4 — does the continued-airworthiness half belong on the engineering schema at all?** A
  per-article compliance ledger may be manufacturing's asset-and-record relation wearing an approval
  reference. (a) Keep both halves here, joined by the type-to-article conformity relation, which is
  what makes the row distinct — this row's recommendation. (b) Narrow to type-design approval only
  and hand the article half to `manufacturing.asset-register` with a reciprocal edge — cleaner by
  schema, but splits one user-visible corpus and leaves the release certificate homeless between them.

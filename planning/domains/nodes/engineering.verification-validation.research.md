# engineering.verification-validation — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.verification-validation.json`](engineering.verification-validation.json).
Salvage: none — both files are new.
Verdict: **node survives**, `refuse_node: false`, on legs two and three of the node test. Leg one is
real but narrow, and this memo says so rather than inflating it.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief, read in full.
- `python3 planning/domains/dispatch/make_prompt.py engineering.verification-validation` — the
  stamped assignment: neighbours `manufacturing`, `code`, `research`; residuals `Independent
  Records`, `Review Later`; `inherited_field_keys: []`.
- `planning/domains/nodes/engineering.json` — **the schema anchor, and the thing this row is
  measured against.** Read for its `template.why` (the researched default order), its ten
  deterministic signals, its `work_types[]`, its five proposed keys, its twelve file examples and
  its `node_test`. I did not open `engineering.research.md`: the JSON left nothing about the
  default template undecided.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the named depth calibration. Two of
  its lessons are applied structurally here, not cosmetically: a same-schema multi-membership is a
  **two-group question**, never an `also_holds_with` edge; and a fact asserted in `facts_legal`
  must come from a schema that actually activates on that file.
- `planning/00-database-agent-product-design.md` — reached by `grep -n` only, for the residual
  library sentence. Every `design_cite` in the JSON is a span of that one paragraph, matched
  verbatim including its em dashes.
- `planning/domains/canonical_fields.json` — the 37 keys, enumerated mechanically. Confirms that
  neither a means-of-proof key nor a disposition key exists, and that `institution` does exist.
- `planning/domains/roster.json` — every edge endpoint checked against the `nodes[].domain_id`
  list. All sixteen `collides_with` targets and both `role_split` targets resolve.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — via the stamped prompt's verbatim listing;
  all twelve `file_examples.source_type` values are members.
- Landed neighbours that had **already argued a boundary against this id**, found with one grep:
  `engineering.commissioning-handover`, `business_operations.product-requirements`,
  `engineering.aerospace-airworthiness`, `engineering.embedded-firmware`,
  `engineering.automotive-program`. Their boundary text was extracted and **reciprocated in their
  own words and on their own fixture bytes** rather than restated in mine.
- `business_operations.user-research` (REFUSED) and `research.lab-notebook-protocols` — read for
  their fixture lists, both of which turned out to be load-bearing here.

## THE CHARGE — the strongest case that this row should not exist

I put this first because it is the strongest case I could build, and it is nearly sufficient.

1. **It is a work_type value, twice over.** `verification plan/procedure/report` and
   `validation report` are two literal entries in the engineering schema row's own `work_types[]`
   array. The stamped prompt is explicit: work types are values of a field, never nodes.
2. **Its roster name is a list of document types.** "Test plans, protocols and validation reports"
   names three document kinds joined by conjunctions. A row named by document types is the exact
   shape of the 574's failure.
3. **It is also a lifecycle stage.** The right-hand side of a V-model is a position in a
   lifecycle, and `lifecycle_stage` is already a proposed key on the anchor. So the row is
   simultaneously a value of `engineering_artifact_type` and a value of `lifecycle_stage` — which
   normally means it is a *cell*, not a node.
4. **The schema already detects it and already files it.** The anchor's deterministic list
   contains "a verification matrix or test report that links stable requirement identifiers to
   method, procedure, configuration-under-test and pass/fail evidence", and the anchor's own file
   examples already include `BPA-210_DVT-07_Verification-Report.pdf`. The default order
   `project → design_item → lifecycle_stage → engineering_artifact_type` files that fixture
   perfectly well without this row existing.
5. **Its method vocabulary is values too.** `engineering.automotive-program` already ruled that
   "crash and durability testing are methods, and a method is a value."

Point 4 is the one that nearly killed the row: the anchor does not merely permit this material, it
demonstrably handles the flagship fixture. So the burden is not "is this material real" — it
obviously is — but "does anything about it need a *different* template."

### Why the charge is defeated

**Leg 1 — detection signals: PARTIALLY different, and this is the weak leg.** The anchor's ten
signals are *definition* structures — title block, requirements table, TDP manifest, BOM
parent/child, change disposition — with one verification signal among them. Three discriminations
that actually decide files in this corpus are on none of them, and two are refusals:

- **The protocol/report seam.** The identical grid with the result and disposition columns
  systematically empty and no execution date is a *plan*, not evidence. The anchor has no signal
  that separates a blank protocol from an executed one, and this is precisely the discrimination
  `business_operations.product-requirements` already argues from its side: "Executed results
  transfer the file." That row's boundary presupposes a discriminator that its counterparty must
  own, and the schema default does not own it.
- **The third-party issuer relation.** An accredited laboratory report's cover carries an issuer
  with an accreditation or scope reference, a report number in the *lab's own* series, a standard
  designation, a sample-received description, and a conclusion clause scoped to that sample. No
  other engineering artifact has this relation, because every other engineering artifact is
  authored by the design authority. This is where canonical `institution` becomes relevant to an
  engineering file at all.
- **The raw-measurement refusal.** Instrument data with no acceptance criterion beside it is not
  verification evidence. This is the single most common false positive on the node and there is no
  schema-level signal that says so.

Real additions, but I will not claim more: the schema's verification signal is genuinely present,
and if that one signal were expanded to carry the three above, this leg would collapse.

**Leg 2 — dimension order: DIFFERENT, and decisive.** Recommended
`design_item → engineering_artifact_type` against the schema's
`project → design_item → lifecycle_stage → engineering_artifact_type`.

- `lifecycle_stage` is dropped **because this row is the lifecycle position.** Across this corpus
  that level's value is constant, so it opens a branch that never branches: a directory of depth
  bought for nothing. This is an argument the schema default structurally cannot make about
  itself, and it is the cleanest possible demonstration that "V&V is a lifecycle_stage value" and
  "V&V needs its own template" are compatible rather than contradictory — the row exists *because*
  it is a stage, since a corpus already scoped to one stage must not branch on it.
- `project` is demoted below `design_item`, and dropped entirely for the externally issued and
  standard-scoped subset. Accredited lab reports, reusable qualification packages and
  standard-scoped protocols routinely carry an article and a standard with **no project token**.
  This is the same evidential move `finance.crypto-assets` made when it dropped `account_type`:
  a level the files cannot fill is a fabricated fact, not a tidier tree.
- The corpus's most useful optional order — **institution-first**, all of one laboratory's reports
  together — the schema default cannot express at all, because `institution` is not in its order.

**Leg 3 — privacy: DIFFERENT IN KIND.** The schema is `potentially_sensitive` because engineering
packages carry proprietary and export-controlled design definition. That is a property-of-content
story. This row's defining privacy rule is instead a **refusal about people**: summative
human-factors and usability VALIDATION produces signed participant consent, session video and
transcripts that wear this row's exact vocabulary and are a person's record. The rule is that this
material never acquires a `design_item` and routes to Protected Records.

This leg is load-bearing rather than decorative because of a fact I did not expect:
`business_operations.user-research` is a **REFUSED** row, and its fixture list is
`P04 consent signed.pdf`, `P04_session_20260512.mp4`, `transcript_P04.vtt`. Nothing downstream is
holding that line. If this row is refused too, the material with the strongest claim on
"validation" in the whole corpus has no owner stating a rule about it.

**Net:** two legs differ, one structurally and one as a refusal. The row survives — but honestly
narrower than its roster name implies. It is not "test documents"; it is the
acceptance-criterion-to-recorded-result relation. If R1c widens the schema default to carry the
protocol/report seam and an `institution` level, this row's justification narrows to leg three
alone and should be re-tested. That contingency is written into the JSON's `node_test.why` rather
than left in this memo.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`FAI-Report_AS9102_BPA-210-001_SN0004.pdf`** — kept as a file example precisely *because* it
  is rejected. See the collision fixture section.
- **`Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf`** — same: kept as the second collision
  fixture. An accredited issuer, a certificate number, measured values against tolerances and a
  conformity statement, and it is `manufacturing.calibration-record`'s.
- **`IQ-OQ-PQ_Fill-Line-2_Protocol-and-Report_2026.pdf`** — rejected from the corpus and named in
  the `manufacturing.quality-management-system` collision instead. A fill line is a plant asset,
  not a designed product. This is the file that most tempted me to widen the row, and widening it
  would have made "validation" a magic word — the very thing the row's `never_alone` refuses.
- **A certificate of conformity / CE declaration** — rejected. It grants market permission and
  carries no measured results. It is `engineering.product-certification`'s, and the report behind
  it is this row's. Keeping both would give one evidence chain two owners.
- **`junit.xml` / a coverage report under a repository root** — rejected. Keyed to test function
  names and a commit, not to requirement identifiers, and its home is the repository tree.
  `code.software-project`. Taking it would have made this row the highest-volume node in the
  product on the strength of a pass/fail column.
- **`PDR_Braking-System_2026-04-18.pptx`** (the anchor's own review fixture) — rejected. It embeds
  a verification-status summary, which is a pointer, not the evidence. `engineering.stage-gate-review`.
- **`BPA-210_FEA_Loadcase-3_RevA.pdf`** (the anchor's own analysis fixture) — rejected *as
  written*. It reports margins; it becomes this row's only when those margins are tabulated
  against requirement identifiers with a disposition. Recorded as a collision with
  `engineering.simulation-analysis` rather than claimed.
- **A standards-library copy of the cited standard** (e.g. the EN 55032 text itself) — rejected. A
  standard is reference material; `engineering.standards-library` holds it. The standard
  designation appearing in three of my fixtures is exactly why "a standard designation alone" is a
  `never_alone`.
- **A test-equipment purchase order or lab quotation** — rejected. Issuer letterhead and a lab
  name, zero acceptance structure. Finance/procurement material; `Receipts and Confirmations` or
  `business_operations.procurement-sourcing`.
- **`Protocol_RNA-extraction_v2.docx`** (`research.lab-notebook-protocols`' landed fixture) —
  rejected, and it is why the research collision is stated: numbered steps and recorded readings
  with no acceptance criterion and no design item.
- **A warranty or field-failure report** — rejected. Post-delivery execution evidence;
  `manufacturing.warranty-claim` and `manufacturing.field-service-report`.

## The collision fixture

**`FAI-Report_AS9102_BPA-210-001_SN0004.pdf`** — a First Article Inspection report.

It looks like this row's evidence in every superficial respect: a serialized article, a table of
characteristics with stated limits, an accept/reject column per row, a signed inspector, a date,
and it cites the same `design_item` and the same drawing revision as the genuine verification
report next to it.

**What discriminates it: the left-hand column, and therefore the object.** This row's left column
holds *requirement identifiers* and its object is whether the **definition** satisfies what was
asked. The FAI's left column holds *drawing characteristic numbers and nominal dimensions* and its
object is whether the **process** reproduced the definition on this unit. Sharing an item and a
revision is not sharing a question.

A second, harder collision fixture is carried too, because the first can be defeated by reading one
column: **`Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf`**. It is structurally near-identical
to the accredited test report this row *does* take — same issuer relation, same accreditation
reference, same measured-values-against-tolerances table, same conformity statement — and it
appears *inside* `DVT-07_Test-Package.zip`, cited by the verification report as the evidence that
the measurement was admissible. The discriminator is that its object is a measuring instrument's
own conformity and its due date. Membership in the campaign archive does not transfer the
campaign's `design_item` onto it; it is marked `group_without_copying_facts: true`.

## Reciprocal boundaries

Sixteen collisions, which is a lot, and it is a true statement about where this row sits: every
domain that tests anything competes for its vocabulary. Five of them **reciprocate a boundary a
landed row argued first**, and in each case I adopted that row's own wording and its own fixture
bytes rather than inventing a second account:

| Neighbour | Their side (as landed) | This side | Same fixture bytes |
|---|---|---|---|
| `engineering.commissioning-handover` | the INSTANCE: the unit installed at a location, accepted by a named party | the REQUIREMENT: the design satisfies what was asked | `SAT-Report_Chiller-CH-02_2026-06-14_witnessed.pdf` |
| `business_operations.product-requirements` | intended criteria, no result column | executed results, and plans organised around method and sample size | the shared acceptance grid |
| `engineering.aerospace-airworthiness` | requirement column cites a published code paragraph, consumed by a compliance finding | requirement traced is the organisation's own identifier | flammability report under `Compliance-Checklist_Cabin-Interiors_Rev-D.xlsx` |
| `engineering.embedded-firmware` | release manifest is the organising structure | requirement-to-method-to-result matrix is the organising structure | `SN100_HIL-Verification_v1.4.2.pdf` vs `SN100_FW-v1.4.2_OTA-Package.zip` |
| `engineering.automotive-program` | a programme's gated structure; methods are values | planned testing against a stated requirement, any industry | `BPA-210_DVT-07_Verification-Report.pdf` |

The eleven stated first from this side each name the fixture on both sides too — the sharpest being
`manufacturing.inspection-record` (`FAI-…SN0004.pdf`, plus the anchor's own
`LOT-24-081_Final-Inspection.xlsx`), `engineering.simulation-analysis`
(`BPA-210_FEA_Loadcase-3_RevA.pdf`), `engineering.product-certification`
(`TR-2026-04188…` vs the one-page certificate citing its number), and
`manufacturing.calibration-record`.

**`also_holds_with` is empty by contract**, and this is deliberate rather than an omission. The
engineering schema row declares co-activation with manufacturing, code, research,
business_operations and construction_property; a template may not widen its schema's set. The two
files most tempting to mark as co-activations — the SAT report and the airworthiness-cited
flammability report — are **same-schema** multi-membership, so they are two-group questions in
`grouping_reasons`, not `also_holds` edges. That is the correction `finance.crypto-assets` had to
make after the fact; it is applied here from the start.

**`role_split` is non-empty**, which is unusual on this schema (the anchor's is `[]`), and it is
where the row's real structural claim lives: the **configuration under test is not the design
item**. `engineering.prototype-build` holds the article in its *build subject* role (what it is);
this row holds the same article in its *configuration under test* role (what it showed). A
verification report **cites** the article's identity; it does not establish it. The same split
runs against `manufacturing.inspection-record` on the design-proof / production-conformance seam,
visible on the FAI fixture.

## Neighbours considered that did **not** get an edge

- **`engineering.risk-analysis-fmea`** — a DFMEA's detection and recommended-action columns point
  at verification, but the shared evidence is a *reference*, not a structure. Linked, not
  colliding.
- **`construction_property.compliance-certificate`** — an electrical or fire test certificate on a
  building is genuinely pass/fail evidence from an accredited issuer. Rejected as an edge because
  the discriminating evidence is a *property or site*, which this row never carries; the
  `engineering`/`construction_property` seam is already declared at schema level and a template
  should not duplicate it.
- **`clinical_practice.*` and `medical.*`** — human-factors validation touches both. No edge: the
  correct outcome is a residual refusal (Protected Records), not a claim on a clinical row, and
  routing it through a medical neighbour would imply this row may hold participant material under
  some condition. It may not.
- **`manufacturing.production-record`** — process validation lots (PPQ) are tempting, but the
  seam is already carried by `manufacturing.quality-management-system` and adding a second
  claimant would give one evidence item three homes.
- **`business_operations.user-research`** — no edge, because the row is REFUSED. Its material is
  routed by residual instead. Recorded as NJ-VV-4 rather than papered over.

## `proposed_fields` — two, both declining destination eligibility

`fields: []` by contract (PR-6, plus rule 12: a template never copies its schema's list).

1. **`verification_method`** (enum: test / analysis / inspection / demonstration / simulation).
   No canonical key names the *means of proof*. `work_type` is academic's, `record_type` is
   finance's, and the anchor's proposed `engineering_artifact_type` names the *kind of document* —
   it cannot tell a requirement proven by physical test from the same requirement proven by
   analysis, though those two files are produced by different people, cite different inputs and
   fail in different ways. **`destination_eligible: false`**, because a method level scatters one
   requirement's evidence across sibling directories and breaks the only chain this row exists to
   preserve.
2. **`verification_status`** (planned / in progress / pass / fail / pass with deviation / waived /
   superseded by retest). Nothing canonical carries a disposition; `stage` is a research
   artifact's workflow position and the anchor's `lifecycle_stage` is design maturity, not
   outcome. **`destination_eligible: false`**, because a disposition is mutable — a retest flips
   fail to pass and a waiver flips it again — and folder membership must not churn as a result
   changes. 00 separates facts from paths precisely so a fact like this can be recorded without
   becoming a location.

Both are `reliability_ceiling: validated` with a named rule family and no regex, no term list
claimed complete, and no threshold.

**Deliberately NOT proposed:**

- **`configuration_under_test`** — the strongest temptation on the node. Rejected: `design_item`
  plus `revision_or_baseline` (both anchor proposals) cover the referent, and the article-versus-
  definition distinction is better expressed as `role_split` than as a fourth engineering key.
  Minting a key to solve one template's problem is the move that produced thousands of private
  field names in the overnight pass.
- **An issuing-laboratory key** — rejected in favour of *reusing* canonical `institution`. The
  reuse is not free (see NJ-VV-1) and is surfaced rather than assumed.
- **A standard designation key** — rejected outright. It is the row's second-worst `never_alone`:
  the same designation appears in a library copy, a purchase spec, a certificate and a marketing
  claim. Evidence, never a key, and never a level.

## Sparse-file discipline

Four of twelve fixtures carry `group_without_copying_facts: true`, and they are the row's honest
hard cases rather than decoration: `TEK00042.CSV` (an oscilloscope export sitting beside the
report that gives it meaning, receiving nothing from it), `Test_setup_thermocouple_placement.jpg`
(cited by figure number *in the report*, which is not evidence *in the image*),
`Screenshot 2026-06-14 at 11.24.03.png` (OCR of a table that already exists — and its
`must_not_conclude` carries 00's rule that the absence of EXIF is not proof of a screenshot), and
`Calibration-Cert_…pdf` (archive membership does not transfer the campaign's item).

## Self-verification run before returning

- `python3 -m json.tool` on the node: parses.
- All twelve `file_examples.source_type` values are members of the fourteen-name `SOURCE_TYPES`
  list (`text_document` ×5, `spreadsheet` ×2, `ocr`, `image`, `archive`, `email`).
- All sixteen `collides_with.domain` values and both `role_split.domain` values resolve to
  `roster.json` `nodes[].domain_id` entries.
- All six `falls_through_to.residual_template` names are among 00's nine, and all six
  `design_cite` spans were grepped verbatim out of the residual-library paragraph of
  `00-database-agent-product-design.md`, em dashes included, before being written.
- No `also_schema` is set on any fixture; `also_holds_with` is empty with a stated contractual
  reason.
- No number in the file is a threshold, a score or a count of evidence — the digits present are
  filenames, years and standard designations inside fixture names.
- No handling class assigned; `sensitivity` is `potentially_sensitive` only.
- `fields: []`; `proposed_fields` contains two keys, neither of which is a synonym of a canonical
  key (checked against all 37) and neither of which is destination-eligible.
- At least one `never_alone` is true of a tempting false file: "a pass/fail column alone" and "a
  laboratory, notified body or certification house name alone" are each tripped by
  `Calibration-Cert_LoadCell-LC-1142_2026-01-09.pdf`.
- Only the two assigned files were written. No neighbour node, roster, `canonical_fields.json`,
  `check.py`, `src/` or SPEC was touched.

## NEEDS-JOSEPH (this node only)

- **NJ-VV-1 — may canonical `institution` carry an issuing test laboratory?** `institution` is
  defined in the finance schema's issuer role. This row's institution-first optional branch, and
  the `facts_legal` of `TR-2026-04188_EMC_EN-55032_Class-B.pdf`, both depend on the reuse.
  Alternatives: (a) reuse `institution` as a general issuer key, accepting that its meaning
  broadens across schemas — what this row assumes; (b) mint an issuer key on engineering, which
  this row refused to do; (c) treat the laboratory as never-alone evidence only, with no fact —
  which kills the institution-first branch and leaves a real retrieval need unmet. **Recorded, not
  resolved. No key was minted.**
- **NJ-VV-2 — two proposed keys, both non-destination.** Are `verification_method` and
  `verification_status` two keys or one, with method folded into `engineering_artifact_type`? And
  is R1c willing to accept proposals that explicitly decline destination eligibility? There is no
  precedent for a non-destination fact on this schema, and if the answer is that every engineering
  key must be a possible level, then both proposals should be withdrawn rather than made eligible
  — making a mutable disposition into a folder is worse than losing the fact.
- **NJ-VV-3 — the qualification seam.** This row recommends: a qualification package activates
  engineering when the qualified object is a **design item**, and
  `manufacturing.quality-management-system` when the object is a **process, plant asset or
  computer system**. The alternative is that all IQ/OQ/PQ material sits in the QMS row regardless
  of object, which is simpler to detect (the vocabulary is stereotyped) but wrong for a
  design-qualification package. Confirm, or invert.
- **NJ-VV-4 — nobody owns usability-validation participant material.**
  `business_operations.user-research` is REFUSED and carries the very fixtures
  (`P04 consent signed.pdf`, `P04_session_20260512.mp4`, `transcript_P04.vtt`). This row routes
  them to Protected Records and refuses to give them a `design_item`, but that is a one-sided
  statement: no landed row asserts the reciprocal. Alternatives: (a) the residual is the whole
  answer and no row owns it; (b) the `business_operations` schema default owns it; (c) a
  human-factors row is created, which J-IND's roster does not currently contain. Someone must hold
  this, and it should not be a template on the engineering schema.

# engineering.stage-gate-review — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: engineering`, `launch: placeholder`, `parent_id: null`.
Output: [`engineering.stage-gate-review.json`](engineering.stage-gate-review.json).
Verdict: **node kept**, on legs one and two of the node test. Leg three fails honestly and is written
as failing.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` and the stamped assignment from
  `make_prompt.py engineering.stage-gate-review` — row metadata, node test, output shape, done-when list.
- `planning/00-database-agent-product-design.md` — grepped, not streamed. Four spans were pulled and
  verified verbatim before use: the parent-dimension / project-before-time paragraph (line 95), the
  residual library paragraph (line 120, source of both `falls_through_to` cites), and the stop-rules
  paragraph (line 63, source of the university-name read-across and the sparse-file discipline).
- `planning/domains/nodes/engineering.json` — the schema anchor, and the file this row is measured
  against. Its `node_test`, `recognition`, `work_types`, `template.why`, `collides_with` and
  `open_question` are what the charge below had to be argued against.
- `planning/domains/_CONTRACT.md` rule 14 — read directly, and it changed two fields: it restricts
  `also_holds_with` to schema-to-schema pairs and `collides_with` to same-kind pairs. So every
  collision here is a **template** id, and `also_holds_with` is empty with a note rather than a
  convenient list.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration.
- Neighbour rows that already argued a boundary against this id, found with one grep:
  `engineering.change-order.research.md`, `engineering.commissioning-handover.research.md`,
  `engineering.automotive-program.json`, `business_operations.product-roadmap.research.md`.
- `planning/domains/roster.json` — every edge endpoint checked mechanically (9/9 resolve).

External reality checks, creating no gazetteer, no regex, no threshold: the formal technical-review
series with entrance and success criteria (SRR, PDR, CDR, TRR) as described in the NASA Systems
Engineering Handbook — the same source the engineering schema row already leans on; Cooper's
stage-gate model, whose gate outputs are a Go / Kill / Hold / Recycle disposition, which is where the
disposition vocabulary in `recognition.deterministic` comes from; and the US design-control rule for
medical devices, which requires that design review results be documented, that the review include
representatives of all functions concerned, and that it include **an individual who does not have
direct responsibility for the design stage being reviewed** — that last requirement is the reason the
independent-reviewer slot is listed as a labelled structural signal rather than prose.

## THE CHARGE — the strongest case that this row should not exist

Made first, in its strongest form, because three of the six named failure modes land on it at once.

**(a) It is a lifecycle stage.** The whole content of a "stage gate" is a stage. `lifecycle_stage` is
a *proposed field on this row's own schema*; concept, preliminary design, detailed design,
qualification and released design are its values. A row whose subject is one value of one of its
schema's dimensions is a value wearing a node's clothes — the 574's original mistake.

**(b) It is a document type.** The engineering schema row's `work_types` array already contains
`"design review package"`, in so many words. ALIGNMENT is explicit that work types are values and
never nodes. If the row is the pack, the row is a work type, and it should be deleted the same way
`engineering.automotive-program` was deleted for being a sector noun.

**(c) It is a duplicate of the schema's default template.** The schema's researched order is
project → design_item → lifecycle_stage → engineering_artifact_type. A gate pack is a project, an
item, a stage and an artifact type. Nothing is added. And the schema's fixtures are already an
automotive brake-pedal programme, so a gate pack on BPA-210 is the default's own evidence.

**(d) A weaker but real fourth charge: it is defined by absence.** One could read the row as "the
engineering file that is *not* a drawing, *not* a change, *not* a verification report" — a leftover
bin, which is what the residual library is for.

### Defeating the charge

**Against (b), which is the strongest.** The row is not the pack. The pack is a work type and stays
one — it is listed in this row's own `work_types` array, exactly where it belongs. The row is the
**review event and its disposition**. The discriminating evidence is a decision slot whose value is a
disposition on *progression*, sitting beside a criteria assessment and a named board. That relation
survives when the pack does not exist: `CDR_BPA-210_..._Minutes.pdf` is fully constituted with no deck
attached, and `Design Review Checklist Template.docx` carries every work-type word and is **not** this
row, because it has no event, no board and no disposition. A work-type word that can be present
without the row firing, and absent while the row fires, is not what constitutes the row.

**Against (a).** A stage is a property of one artifact's maturity; a gate is a decision *event at a
boundary between* stages, with a board, a date, and a verdict that a stage may not have. The
`engineering.commissioning-handover` memo makes the same distinction from its own side and in the same
words: "a stage is a property of one artifact's maturity, whereas this row is a property of a relation
between two parties". Substitute *decision on progression* for *relation between two parties* and the
argument transfers. Independently, `engineering.change-order.research.md` reached this conclusion from
the outside: it dropped `lifecycle_stage` deliberately and wrote that "a gate review is *about*
lifecycle stage, which is precisely the dimension this row drops... the two rows are complementary
evidence that `lifecycle_stage` belongs there and not here." A sibling assigning a dimension to this
row is external evidence that the row is the dimension's home, not its duplicate. Charge (a) is
answered but not free: it becomes NJ-SGR-2, because a CDR record legitimately carries both the stage
reviewed and the stage entered.

**Against (c).** Two of the four default levels change, and both changes are evidential. `design_item`
is dropped: a gate is held on a programme, one pack spans many items or names none, and forcing the
level means copying one assembly's identity onto a whole-programme decision — the propagation error
00 forbids when it refuses to copy a course fact onto `HW 3.pdf`. `lifecycle_stage` rises to second,
because here the gate *is* the organising fact. And the deterministic signals are not the schema's:
the schema's ten are all controlled-definition structures (title block, requirements table, TDP
manifest, change record, BOM, analysis package, verification matrix, prototype record, archive
manifest, folder context) and **not one of them is a decision-on-progression structure**. A gate
record with zero drawings, zero requirement identifiers and zero revisions fires none of the ten and
is still unmistakably this row. That gap is the node.

**Against (d).** The row is defined positively — criteria + board + disposition — and the test is
that it *excludes* engineering files that are none of those. `BPA-210_DVT-07_Verification-Report.pdf`
is not a gate record despite being none of drawing/change/BOM. A leftover bin would have taken it.

Charge defeated on (a), (b), (c) and (d). Leg three of the node test is conceded rather than argued
around: privacy is `potentially_sensitive` on both sides, and the difference — unannounced hold and
cancel verdicts, individual accountability, waivers on safety-relevant criteria — is degree and
timing, not kind. CONNECTION's test is disjunctive; two clean legs carry the row and the third is
recorded as failing.

## Files considered and rejected

Tempting false positives, each with why it is not this row's evidence:

- **`Sprint-14-Project-Status.xlsx`** — the engineering schema row's own collision fixture, and doubly
  tempting here because a status report reports gate readiness. Rejected: a status report has a
  reporting period, not a decision; it says a gate is *approaching*. `business_operations.project-delivery`.
- **`Vehicle-Programme-Timing-Plan_MY27.xlsx`** — contains a row for every gate with dates. Rejected: a
  plan asserts a gate will occur. `engineering.project`, and reciprocated as a collision.
- **`ECR-1187_BPA-210_Bushing-Material.pdf`** — has a disposition and an approval block. Rejected: the
  disposition is on an item's revision, not on a programme's progression. `engineering.change-order`.
- **`BPA-210_DVT-07_Verification-Report.pdf`** — pass/fail against requirements is what a gate consumes.
  Rejected: producing verification evidence is not deciding on it. `engineering.verification-validation`.
- **`SYS-REQ-042_Braking-System-Requirements_RevB.docx`** — the object of an SRR. Rejected: a
  specification does not become a gate record by being approved.
- **`TDP_BPA-210_Baseline-C.zip`** — released at a gate. Rejected: it is the *product* of passing, and
  the schema's own TDP-manifest signal owns it.
- **A minutes file from a weekly engineering meeting** — same shape (attendees, actions, dates).
  Rejected: no criteria, no disposition on progression; ordinary meeting notes.
- **A standing risk register reviewed at every gate** — rejected: `engineering.risk-analysis-fmea`
  owns the structure, and being *shown* at a gate is not being *of* a gate.
- **A quality-manual clause describing how design reviews shall be conducted** — rejected: a procedure
  is not a record. `manufacturing.quality-management-system`.
- **A blank controlled pro-forma (`Design Review Checklist Template.docx`)** — kept as a file example
  precisely because it is the rejection: it is the never-alone case made concrete.

## The collision fixture

**`Phase-2-Gate-Review_Steering-Committee.pptx`** — an ERP rollout gate. It has the criteria table, the
gate token, the board, the date and a decision slide reading "Approved to proceed to Phase 3". It is
structurally indistinguishable from a technical gate pack and it is **not this row**.

What discriminates it: the *content of the criteria*, and nothing else. Budget variance, benefits
realisation, change-readiness and vendor status are governance criteria; requirements baselined,
design defined, analyses closed and verification planned are technical-maturity criteria. There is no
design item, no drawing number and no requirement identifier anywhere in the deck. This is why gate
vocabulary is a `never_alone` rule rather than a deterministic signal, and why the discrimination is
listed under `needs_llm` and not pretended to be a rule — honesty about which is recorded as NJ-SGR-3.

A second, sharper fixture: **`Invitation - CDR Brake Pedal Assembly (Fri 11 Mar).ics`**. Labelled
structure, right vocabulary, right programme, right people. It is a meeting, not a record; it gets
`group_without_copying_facts: true` and no facts.

## Reciprocal boundaries

Nine collisions, each stated in both directions on one shared fixture. The four that were argued
against this row by neighbours before it was written are honoured rather than relitigated:

| Neighbour | Shared fixture | This row holds | They hold |
|---|---|---|---|
| `business_operations.project-delivery` | `Phase-2-Gate-Review_Steering-Committee.pptx` | criteria about design maturity | criteria about budget, benefits, vendors |
| `engineering.change-order` | `ECR-1187_BPA-210_Bushing-Material.pdf` | disposition on progression | disposition on an item's revision |
| `engineering.verification-validation` | `BPA-210_DVT-07_Verification-Report.pdf` | the criteria assessment citing results | the procedure, article and results |
| `engineering.project` | `Vehicle-Programme-Timing-Plan_MY27.xlsx` | the gate was held, and returned X | the gate is scheduled for date Y |
| `engineering.commissioning-handover` | a design review held during commissioning | the review and its disposition | acceptance transferring custody |
| `engineering.requirements-specification` | `SYS-REQ-042_..._RevB.docx` | the SRR that baselined it | the requirement rows themselves |
| `manufacturing.production-planning` | a Production Readiness Review pack | criteria on design maturity | capacity, tooling, sequencing |
| `research.project-workspace` | an R&D go/no-go memo | criteria on a defined item's definition | criteria on whether a question was answered |
| `code.software-project` | a release readiness checklist | gates on a physical/system item | readiness inside a repository |

`engineering.automotive-program` is a refused row, so no edge is written to it; but it named
`MY27-XJ_Gateway-3_Design-Freeze_Review-Pack.pptx` as this row's fixture and routed gate vocabulary
here, and both are now accepted on this side — the fixture is file example four and the vocabulary is
in `proposed_context_terms`.

## Neighbours considered that did NOT get an edge

- **`business_operations.product-roadmap`** — it considered this row and declined, on the grounds that
  "the `project-delivery` and `go-to-market` edges between them cover the schedule and the gate; a
  third edge would duplicate both." Accepted from this side; adding the edge unilaterally would break
  rule 14's reciprocity requirement and double-count a relation `project-delivery` already carries.
- **`business_operations.product-requirements`** — a discovery-stage go/no-go with no design item is
  already contested between that row and `engineering.change-order`; a third claimant would give one
  evidence item three homes. This is NJ-ENG-4's territory, not a new edge.
- **`manufacturing.quality-management-system`** — a controlled design-review record is a QMS record by
  filing convention. Rejected as a collision: the QMS row owns the *procedure and the control system*;
  the record's discriminating evidence is still criteria + board + disposition. Noted on the
  `Design-Review-Record_DHF-04` fixture instead.
- **`engineering.risk-analysis-fmea`** — reviewed at every gate, owned by its own structure.
- **`business_operations.organisational-records`** — board minutes shape, but a company board is not a
  technical review board and no design-maturity criteria appear.
- **`role_split`** — empty, and it is the interesting refusal. The split this material wants is the
  board that DECIDED against the team that PRESENTED. Both are authorship; 00 keeps authorship out of
  destinations; no canonical key holds either role; minting a reviewer key for one template is the
  move that produced thousands of private field names overnight. The independent-reviewer slot stays a
  detection signal.

## Fields, dimensions, and what was not minted

`fields: []` — binding. The engineering schema declares none under PR-6 and D1's deferral, and rule 12
forbids a template copying its schema's list. `facts_legal` lines reference the schema row's
**proposed** keys (`project`, `design_item`, `lifecycle_stage`, `engineering_artifact_type`,
`revision_or_baseline`), which are pending R1c; that dependency is stated in `fields_note` rather than
silently relied on, in the same way `finance.crypto-assets` flagged `account_holder`.

`proposed_fields: []`. One key was genuinely tempting — the gate disposition — and it is parked in
`open_question` as NJ-SGR-1 rather than minted, because it is a small closed set of values rather than
a role, and because it is not destination-eligible: filing a programme's records under folders named
for verdicts scatters one gate's pack. `gate_id` was rejected outright: `lifecycle_stage` already
carries it, and `engineering.change-order` explicitly assigned that field's home here.

Recommended order, conditional on R1c: **project → lifecycle_stage → engineering_artifact_type**,
`time_first: false`, with one optional branch (single-programme corpora collapse `project` and lead on
`lifecycle_stage`). Project stays first on 00: "For document and record domains, project, function, or
subject usually comes before time because putting year first scatters related work across calendar
folders." The machine-readable array is empty under PR-6.

## Sparse-file discipline

Three fixtures carry `group_without_copying_facts: true`. `Notes.docx` is the `HW 3.pdf` of this node:
unlabelled prose sitting beside a criteria sheet and a decision memo, and it receives nothing.
`Screenshot 2026-03-11 at 10.42.13.png` is the OCR case, and its `must_not_conclude` covers both
halves of 00's stop rule — the capture timestamp is not the gate date, and absent EXIF is not proof of
a screenshot. The `.ics` invitation is the third: real labelled structure, no facts earned.

## Audits run before returning

- `python3 -m json.tool` parses the node (run below).
- Every `file_examples.source_type` is in the fourteen-member `SOURCE_TYPES` list (12/12 fixtures,
  drawing on seven members: text_document, spreadsheet, presentation, ocr, archive, calendar, email).
  `image` and `filesystem` appear in `file_kinds` without a fixture, as plausible kinds only.
- Every `collides_with.domain` resolves against `roster.json` (9/9), and every one is a **template**
  id, per rule 14's same-kind restriction.
- `falls_through_to` names two of §7.3's nine residual templates; both `design_cite` strings were
  grepped out of `00` line 120 verbatim before use.
- The two other `00` spans used (project-before-time, university-name-alone) were grepped out of lines
  95 and 63 verbatim. No quotation in either file is paraphrased inside quote marks.
- `also_holds_with` and `role_split` are empty by contract, each with a note.
- No threshold, score, count or handling class appears; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. The ownership register, roster, canonical fields, check.py
  and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-SGR-1 — the gate disposition has no key.** Proceed / proceed with actions / hold / recycle /
  cancel is the one fact this row owns that nothing can record. (a) leave it as content, searchable,
  never a dimension — what the row recommends; (b) mint `decision_outcome` as a search-and-privacy
  field with `destination_eligible: false`; (c) fold it into `lifecycle_stage`, which conflates the
  stage reviewed with the verdict returned. Recorded, not resolved; no field proposed.
- **NJ-SGR-2 — is a gate a stage, or an event between stages?** `engineering.change-order` assigned
  `lifecycle_stage` to this row, and this row accepted it, but a CDR record legitimately carries both
  "detailed design" (reviewed) and "entering qualification" (authorised). If one file may carry two
  values of one dimension, either the dimension is wrong or the second value is a different fact.
- **NJ-SGR-3 — governance gates with a technical annex.** Currently decided by criteria content, which
  is a `needs_llm` judgement, not a deterministic rule. Alternatives: one record activating both this
  row and `business_operations.project-delivery`; or a primary-criteria test that picks exactly one.
  The `Phase-2-Gate-Review_Steering-Committee.pptx` fixture is where this bites.
- **NJ-SGR-4 — dependency on NJ-ENG-1.** If R1c widens canonical `stage` instead of accepting
  `lifecycle_stage`, this row's recommended second dimension is renamed. Flagged so the dependency is
  not silent.

## Recommendations to R1c (cross-row; not made here)

1. Reciprocate the nine collisions from the neighbour side. Four are already effectively agreed in
   prose (`change-order`, `commissioning-handover`, `automotive-program`, and `product-roadmap`'s
   declination) but only `automotive-program` names this id in a machine-readable edge.
2. `business_operations.project-delivery` is the only neighbour that shares a fixture with this row
   and has no argued position on it in either direction. It is the highest-risk seam on the node.
3. If NJ-SGR-1 resolves to (b), the same key would serve `engineering.change-order`'s disposition and
   `engineering.commissioning-handover`'s acceptance; adjudicate once, across three rows, not here.

# hr.org-design-headcount — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: hr`, `launch: placeholder`, `parent_id: null`.
Output: [`hr.org-design-headcount.json`](hr.org-design-headcount.json). No prior draft existed; both
files are new.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief and its six depth requirements,
  which this memo is audited against.
- `planning/domains/dispatch/make_prompt.py hr.org-design-headcount` — the stamped assignment. It
  supplied the row metadata, the node test, the closed edge vocabulary and the done-when list.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` only
  (the brief forbids streaming it). Every phrase in quote marks in the JSON was printed verbatim by
  those greps before it was written; the audit below records the check.
- `planning/domains/nodes/hr.json` — the schema anchor, read in full. This is the file this row is
  measured against, and most of the argument below is a comparison to it.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the depth calibration named by the
  brief. Two things came from it beyond depth: the `also_holds_with` schema-only restriction (rule
  14) which is why this template's list is empty with a note rather than populated, and the practice
  of parking a tempting key in `open_question` rather than minting it.
- Neighbour nodes located by one grep (`grep -rl "hr.org-design-headcount" planning/domains/nodes/`)
  and read only at the matched lines: `business_operations.organisational-records.json`,
  `business_operations.project-delivery.json`, `clinical_practice.practice-administration.json`.
  All three had already argued a boundary against this row. None was edited.
- `planning/domains/roster.json` — every edge endpoint confirmed as a real roster id.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — via the assignment's verbatim listing.

## THE CHARGE — the strongest case that this row should not exist

I owe this first, and the case is strong enough that I expected to refuse.

1. **It is a work_type value.** `hr.json` lists, verbatim in its `work_types[]`, "organisation
   chart, establishment plan, headcount plan, or reorganisation proposal". That enum member is my
   row's entire extension, word for word. A row whose whole scope equals one value of its schema's
   own `work_type` field is a value, not a node — this is exactly the 574's failure and ALIGNMENT
   forbids asking for a child node per work type.
2. **It is a document type.** "Org chart" is a document-type word. Worse, `hr.json`'s `never_alone`
   already names "org chart" in its list of shapes that prove nothing alone — my row appears in the
   schema anchor as a *rejected* signal.
3. **It is a lifecycle stage.** Design and headcount planning is the *plan* stage of the workforce;
   onboarding, payroll and performance are the *execute* stages. Stages are not nodes.
4. **It is a duplicate of a neighbour.** A headcount plan is a salaries budget with the money hidden
   (`business_operations.budget-forecast`), or a strategy deck about shape
   (`business_operations.strategy-plan`), or a capacity plan (`business_operations.project-delivery`).
5. **It is defined by an absence** — "the HR files with no employee named in them".
6. **`hr.json` already covers it.** The anchor carries `FY27 establishment and headcount plan
   v5.pptx` as one of its own ten fixtures. If the schema's default template already files my
   flagship file, I add nothing.

### How the charge is defeated

By one fact that none of the six anticipates: **this row's evidence has a different subject.** Every
other hr situation files a corpus whose ROWS ARE PEOPLE — a payroll register, a joiner tracker, a
calibration sheet, a survey export, a case pack. This row files a corpus whose ROWS ARE POSTS:
approved positions carrying a post reference, a grade, an FTE and a reporting-to relation, which
exist whether or not anyone occupies them. That subject shift is not a lifecycle stage, not a
document type and not a value, because it changes what the extractor must look at.

The proof is a file: `Establishment by post - Customer Ops - Feb 2026.xlsx`, whose incumbent column
reads *Vacant* on every row. Test it against `hr.json`'s own first deterministic signal, which
requires "a structured personnel form whose labelled slots jointly identify an employee or workforce
cohort AND a personnel process". That sheet identifies **no employee** and instantiates **no
process**. Under the schema default it does not activate at all. This row is not a narrowing of hr's
default; it is an extension of activation to evidence the default misses. Charges 1, 2, 3 and 6 all
assume this row is a subset of hr, and it is not — it is partially disjoint from it.

Charge 5 inverts too. The definition is positive — post identifier plus grade or FTE plus reporting
relation, or a current-versus-proposed pairing. The absences (no pay per person, no allocation
percentage against a work package, no ownership percentage against an entity) are *discriminators
used inside* the row, not the row's definition.

Charge 4 is answered by fixtures rather than argument, and I kept the losing files in the node so
the boundary is testable: `Salaries and headcount budget FY27.xlsx` does **not** activate this row
despite the word headcount in its filename, and `Project Phoenix resource plan.xlsx` does not
activate it despite naming people, titles and percentages.

**Verdict: `refuse_node: false`.** But the row survives on a narrower and more honest basis than its
`one_line_hint` implies, and the JSON's `one_line` was rewritten to say so: it is the post-structure
row, not the "HR planning documents" row.

## The node test, all three legs

CONNECTION's test: a template exists only when its detection signals, its recommended dimensions, or
its privacy rules differ from its schema's default. This row differs on all three, and each leg is
argued separately because a verdict is not an argument.

**Leg 1 — detection signals differ, and differ in both directions.**
The hr default requires an employee or workforce cohort joined to a personnel process. This row's
discriminating signal is the joint post-structure (position identifier + grade or FTE + reporting-to
slot) and the current-versus-proposed pairing — two structure states in one artifact, which appears
in no executed personnel record. It fires on files the default misses (the all-vacant establishment
sheet) and declines files the default would take (a staff list of names, titles and emails carries a
workforce population but no post structure). The default also lists "org chart … shape alone" as
never-alone; this row's job is to state what must accompany the shape, which the default does not.

**Leg 2 — recommended dimensions differ, and are inverted, not merely reordered.**
hr's default prose order is work type or named people programme first, then workforce unit, then
people cycle. This row recommends **workforce unit first**, then the design round, then work type.
The reason is evidential: an establishment artifact is *about* a unit, so leading with work type
collects every unit's chart into one undifferentiated bucket while splitting a single design round
across chart, register, analysis and proposal folders. Version family is load-bearing here rather
than incidental, because v3 and v7 of a restructure propose **different structures**, whereas v3 and
v7 of a payroll register describe the same run. Two levels are forbidden outright: a personnel case
level, because this row has no case, and an individual's name, because `00` says "It should avoid
using authorship or creator identity as a destination dimension."
Under PR-6 `dimension_order` stays `[]` and the recommendation is prose for R1c — the same discipline
`hr.json` uses. This leg is therefore contingent; see NJ-ORG-2, where I say plainly that it dies if
`workforce_unit` is refused.

**Leg 3 — privacy rules differ in KIND, not in degree, and in both directions.**
hr keys protection to employee-identifying content. This row's most damaging file names nobody:
`Restructure proposal - CONFIDENTIAL - do not circulate v9.docx` identifies posts by reference only,
and premature disclosure of which posts are marked for deletion harms everyone who occupies them
collectively. Depersonalisation does not reduce the harm here; it is orthogonal to it. The risk is
also time-bounded in a way no other hr material is — the same chart is protected on Monday and on
the intranet on Friday. And the rule runs looser in the other direction: this row declines to treat a
published current-state chart as a personnel record merely because it prints names, which hr's
blanket posture would. A rule that protects a file with no person in it and releases a file full of
people is not the default rule turned up; it is a different rule.

## Files considered and REJECTED

Naming what I hold is not research. These are the tempting false positives, each rejected with the
discriminator, and the first two are kept **inside** the node as fixtures so the boundary is testable
rather than asserted.

- **`Project Phoenix resource plan.xlsx`** — the collision fixture. Names, job titles, utilisation
  percentages, start and end dates: it reads as a headcount plan on every surface cue.
  *Discriminator:* allocation is stated against **work packages on a project's own schedule and
  terminates at closure**; there is no post reference, no grade, no vacancy status, no reporting-to
  slot. Establishment structure outlives projects; that is the whole distinction.
- **`Group structure chart - entities and shareholdings.pdf`** — the second collision fixture, and
  the sharper one, because the *shape* is byte-for-byte the shape of an org chart: boxes, strict
  hierarchy, connecting lines. *Discriminator:* the node attributes. Legal entity names,
  incorporation jurisdictions and company numbers on the boxes, ownership percentages on the edges,
  and no grade, FTE, post reference or person anywhere. This is the file that proves the hierarchy
  shape is a never_alone.
- **`Salaries and headcount budget FY27.xlsx`** — rejected despite carrying the row's own keyword in
  its filename. FTE by department against salary cost, reconciling to a finance total, with no
  post-level structure. Kept as a fixture precisely because filename-keyword activation is the most
  likely way this row misfires in production.
- **A staff directory / contacts export** — a workforce population with job titles and managers.
  Rejected: no post attributes, no reporting structure as data, nothing proposed. It is the
  strongest argument that "list of people at a company" is *not* what this row means.
- **A payroll register cut by department** — has unit, headcount and cost. Rejected: rows are people
  and money, and it is `hr.payroll-benefits-administration` evidence. The register would satisfy
  hr's default and fails this row's.
- **An employee handbook section on reporting lines and delegation of authority** — describes
  structure in prose. Rejected: it is a governing policy, `business_operations.policy-handbook`, and
  the hr anchor already routes governing documents away from hr.
- **A consultancy's organisation-design methodology deck** — full of spans, layers and target
  operating models. Rejected: it is reference reading about designing organisations, not this
  organisation's establishment. Its residual is Reading Inbox and it teaches this row nothing it
  owns, so it stayed out of the fixture list.
- **A workforce attrition and headcount trend dashboard** — rejected to `hr.workforce-analytics`. A
  time series over an existing population is reporting; the presence of a **target** column is what
  makes a structural sheet design work. I kept `Spans and layers analysis.xlsx` as the fixture that
  sits exactly on that seam.
- **An HRIS position-export `.json` from a vendor API** — kept as a `code_structured` source type in
  `file_kinds`, but not given a fixture slot. Its evidence is identical to the establishment
  spreadsheet's and it would have added a source type without adding an argument.

## Reciprocal boundaries — including three the neighbours asked for

Three landed rows had already argued against this id before it was written. Each is now reciprocated
**naming the same fixture on both sides**, and none of those files was edited.

- **`business_operations.project-delivery`** states: "AUTHORED ONE-WAY HERE, replacing the gist
  pass's decision to leave it unedged; R1c owes the reciprocal." This row supplies the reciprocal
  over the same file, `Project Phoenix resource plan.xlsx`, in the same terms — allocation against
  work packages there, establishment posts here, hr's stricter posture governing handling wherever
  both apply.
- **`business_operations.organisational-records`** carries `Org chart 2026.pptx` and tells the file
  in its own `must_not_conclude` that "hr.org-design-headcount owns it". This row now carries that
  exact filename with that exact observation set, accepts ownership, and hands back the corporate
  half — `Group structure chart - entities and shareholdings.pdf` — so the seam is stated from both
  ends rather than only conceded from one.
- **`clinical_practice.practice-administration`** argues against the whole hr family (it notes that
  `collides_with` joins same-kind rows, so it named the nearest template). Restated from this side on
  the same fixture class: a rota naming clinics and patient-facing sessions is theirs, an
  establishment register of posts and grades is this row's, and a staff-by-day grid alone belongs to
  neither.

Four further reciprocals are authored fresh, each on a named shared fixture:
`hr.workforce-analytics` (`Spans and layers analysis.xlsx`, discriminated by a target column),
`career.employer-side-hiring` (`JD - Head of Customer Operations - approved.docx`, discriminated by
requisition slots), `business_operations.budget-forecast` (`Salaries and headcount budget FY27.xlsx`),
and `hr.compensation-planning` (the grade architecture — this row assigns **posts** to grades, that
row assigns **money** to grades, and the grade is the seam).

Two `role_split` entries record same-entity/different-role pairs rather than confusable evidence: the
post as an approved seat versus the individual's own employment record (`career.employment-records`),
and the workforce establishment versus the legal-entity constitution
(`business_operations.organisational-records`, which therefore carries both a collision and a split
because both relations are genuinely present).

## Neighbours considered that got NO edge, and why

- **`business_operations.strategy-plan`** — a target operating model deck is structure-adjacent, but
  the discriminating evidence never overlaps: a strategy plan carries objectives and initiatives, not
  post attributes. Adding the edge would give one evidence item a third claimant for no gain.
- **`business_operations.meeting-record`** — a design-review meeting note travels in the pack. It is
  a member of an accepted group, not a competing owner of the same bytes.
- **`business_operations.it-asset-inventory`** and **`facilities-workplace`** — seat plans and
  desk-allocation sheets look structural and are not. No shared discriminating slot, so no edge.
- **`hr.onboarding-offboarding`** — a vacancy created by a leaver connects the two worlds causally,
  not evidentially. The tracker's rows are joiners; the register's rows are posts.
- **`legal.*`** — kept as `also_schema` on the proposal and the consultation pack (collective
  consultation is legal instrument territory) but given no edge from this template, because
  `also_holds_with` is a schema-row relation and hr's anchor already lists `legal`.
- **`finance`** — the payroll and cost-side edges are hr's schema-level business. This row's finance
  contact is the budget fixture, which is handled by the `business_operations.budget-forecast`
  collision rather than by a second claim on the same file.

## `proposed_fields` — empty, argued

Nothing was minted. The two keys this material needs already exist as `hr.json` proposals and are
**reused**, per the brief's instruction to reuse an existing proposal rather than mint a variant:
`workforce_unit` for the establishment being designed and `people_cycle` for the design round. Two of
hr's four proposals are the wrong role here and are named as such in `fields_note`: `workforce_member`
(this row's subject is a post, not a person) and `personnel_case` (this row has no case).

The one genuinely tempting new key was a **post or position identifier**. It is rejected on a
structural ground rather than a privacy one: it is a **row-level datum inside a register**, not a
file-level fact about the register. One establishment sheet carries hundreds of post ids, so no
extractor could write one onto the file, and a fact that cannot be single-valued at file level is
evidence, not a key. The privacy objection (a folder named for a post id publishes structure) is a
second reason, not the first. Recorded in `proposed_fields_note`; no key proposed.

`fields` is empty twice over — PR-6 leaves the hr schema with no canonical rows to reference, and a
template may not copy its schema's list even when one exists.

## Sparse-file discipline

`IMG_2287.HEIC` is this node's `HW 3.pdf`: a phone photograph of a whiteboard covered in boxes and
arrows, no legible label, no readable grade or post reference, sitting in the same capture
neighbourhood as two design-round decks. It is marked `group_without_copying_facts: true`, its
`facts_legal` is universals only, and its `must_not_conclude` states both halves — the correct
activation set is empty, and the neighbourhood's unit and cycle are not copied onto it. Its residual
is One-Off Images. The paired OCR fixture, `Screenshot 2026-03-04 at 11.42.13.png`, carries the
matching rule that missing EXIF is not proof of a screenshot.

## Audits run before returning

- `python3 -m json.tool` — parses (recorded in the return message).
- Six quoted spans attributed to `00`. All six were printed verbatim by `grep -n` from
  `planning/00-database-agent-product-design.md` **before** they were written into the JSON: the
  Columbia never-alone sentence, the topic-versus-purpose sentence, the irreconcilable-facts clause,
  the Independent Records sentence, the Protected Records sentence, and the authorship-as-destination
  sentence (`grep -c` returned 1). No `00` quotation here is paraphrased inside quote marks.
- Every `file_examples.source_type` is in `SOURCE_TYPES` (12/12: spreadsheet, presentation,
  text_document, image, ocr, archive).
- Every `collides_with.domain` is a roster id (7/7, confirmed against `roster.json`); every
  `also_schema` is a roster schema id (`legal`, `career`, `photos`); every `falls_through_to.template`
  is one of `00`'s nine residual names (4/4).
- `also_holds_with` empty by contract with a note; `fields` and `proposed_fields` empty with notes.
- No threshold, score, count of evidence or handling class appears. `sensitivity` is
  `potentially_sensitive` only. Digits in the file are inside fixture filenames.
- Only the two assigned files were written. No neighbour node, no roster, no
  `29-DOMAIN-OWNERSHIP.md`, no `canonical_fields.json`, no `check.py`, no `src/`.

## NEEDS-JOSEPH (this node only)

- **NJ-ORG-1 — the contract has no vocabulary for pre-announcement confidentiality, and this row's
  sharpest fixture needs one.** `Restructure proposal - CONFIDENTIAL - do not circulate v9.docx`
  names nobody and is the most damaging file in this world. Alternatives: (a) an unannounced proposed
  structure is protected by default even when depersonalised — this row's answer, argued from
  collective and anticipatory harm; (b) sensitivity keys strictly to person-naming, which leaves that
  file unprotected; (c) a confidentiality-state or announcement-state fact is minted, which is a
  decision about the shared vocabulary that one template must not make. **No field was proposed.**
- **NJ-ORG-2 — leg two of the node test is contingent on a key that does not exist yet.** This row
  recommends inverting hr's default order to put `workforce_unit` first, and PR-6 makes that
  unenforceable. If R1c refuses `workforce_unit`, the dimension leg dies and the row survives on
  detection signals and privacy alone. It would still survive — but Joseph should be told the leg is
  conditional rather than discover it later.
- **NJ-ORG-3 — three reciprocals are now authored from this side that other rows explicitly asked
  R1c to supply** (`business_operations.project-delivery`, `business_operations.organisational-records`,
  `clinical_practice.practice-administration`). R1c should **confirm** these rather than double-author
  them; those three files were read at the matched lines and not edited.
- **NJ-ORG-4 — a post description carrying BOTH an approved post reference and an open requisition is
  genuinely dual.** Alternatives: co-membership in two accepted groups with disjoint facts, or a
  single owner decided by which slot set is more complete. This row states the transition rule (the
  requisition slots move it to `career.employer-side-hiring`) but cannot settle simultaneity, and
  that row has not stated its side.

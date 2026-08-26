# hr.workforce-analytics — lab notes (R1b)

Date: 2026-08-26
Depth: J-DEPTH
Roster row: `kind: template`, `schema_id: hr`, `launch: placeholder`, `parent_id: null`.
Output: [`hr.workforce-analytics.json`](hr.workforce-analytics.json).
Salvage: none. Both files are new; no prior draft existed.

## Sources actually used

- `planning/domains/dispatch/RESEARCH-BRIEF.md` — the standing brief; the six depth requirements
  this memo is audited against, and the ratified J-DEPTH override of J-IND's gist clause.
- `planning/domains/dispatch/make_prompt.py hr.workforce-analytics` — the stamped assignment.
  It supplied the row metadata, the node test, the output shape, and the done-when list.
- `planning/00-database-agent-product-design.md` — authoritative, read by targeted `grep -n` only.
  Every span placed in quote marks in the JSON was extracted and matched back with `grep -F`
  before it was written; the audit is below.
- `planning/domains/nodes/hr.json` — the schema anchor. This row is measured against its
  **default template**, its seven deterministic signals, its ten never-alone rules, its four
  proposed keys, and its four NEEDS-JOSEPH items. Read in full via a field-selective loader.
- `planning/domains/nodes/finance.crypto-assets.research.md` — the named depth calibration.
  Two of its moves are borrowed deliberately: refusing to mint a key for the string this
  material is saturated with (there, a wallet address; here, a measure name), and stating the
  contract reason `also_holds_with` is empty on a template rather than quietly leaving it blank.
- `planning/domains/nodes/clinical_practice.practice-administration.json` — the only landed row
  that already argued a boundary against this id. Reciprocated on the same fixture; see below.
- `planning/domains/roster.json` — every edge endpoint resolved mechanically (10/10).
- `src/evidence_shape/vocabulary.py` — all thirteen `file_examples.source_type` values and all
  eight `file_kinds.source_types` checked against the fourteen-member list.

Not read, deliberately: the other eleven `hr.*` sibling rows (none has landed — only `hr.json`
and `hr.research.md` exist in `nodes/`), and any row outside the boundary set. Their absence is
why NJ-WFA-3 is open rather than settled.

## THE CHARGE — the strongest case that this row should not exist

I put six charges against it before writing anything. Three are serious.

**Charge 1 (the strongest): this row is a work_type value wearing a node's clothes.** The hr
schema's `work_types` list already contains, as a single entry, *"workforce census, movement,
attrition, absence, cost, or diversity analysis"*. My row's `one_line_hint` is a paraphrase of
that entry. The brief and the assignment both say work types are **values** of a field and that
asking for a node per work type is the 574's original mistake. On its face this is exactly that.

**Charge 2: it is a lifecycle stage, not a world.** Every other hr sibling ends in reporting.
Onboarding produces completion rates; the performance cycle produces rating distributions;
engagement produces scores; compensation produces gap analyses; safety produces incident rates.
"Workforce analytics" may be nothing more than the terminal stage of eleven neighbours, and a
stage is not a filing world.

**Charge 3: it is defined by an absence.** The obvious way to describe this material is "the HR
files that are aggregated" — i.e. the ones where the employee is *missing*. The brief names a row
defined only by the ABSENCE of something as a refusal condition, and it is right to.

Charge 4 (medium): it is a medium — "dashboards and spreadsheets" are a `SOURCE_TYPE` plus
extensions, never a node. Charge 5 (weak): it duplicates `hr.org-design-headcount`, which already
counts people. Charge 6 (weak): it duplicates the hr default template, since PR-6 forces
`dimension_order: []` on both, making the two literally identical in the encoded field.

### Defeating charges 1–3

**Against Charge 1.** The test in CONNECTION §2 is not "does a work-type value with this name
exist" — a template and a value may share a name without the template being the value. The test
is whether *detection signals, recommended dimensions, or privacy rules* differ from the schema's
default. They do, on two of three legs, argued below. The decisive observation is that the hr
schema's deterministic rules are, without exception, **joint identity-plus-process** rules: an
employee ID beside a leaving date, a review period beside a rating, a grievance reference beside
an investigator. Not one of them fires on `Headcount and movement - FY26 Q3.xlsx`, in which no
person appears at all. If this row did not exist, the schema's own default template would fail to
recognize a real and ordinary employer artifact. That is a detection gap, not a naming preference.

**Against Charge 2.** A stage would inherit its parent's evidence. This one does not: the
`People dashboard - Feb 2026.pptx` fixture contains an engagement score and a diversity figure and
carries **none** of the engagement instrument's or the DEI programme's evidence — no item bank, no
wave, no fielding, no action owners. The artifact has its own structure (measurement nouns as
slide titles, period-over-period comparator columns) that survives independently of every source
process. A reporting stage of eleven neighbours would produce eleven artifacts; a corpus produces
one monthly pack, and that pack has one home.

**Against Charge 3 — the charge I take most seriously.** The row is *not* encoded as an absence.
Its positive discriminator is a **stock-and-flow reconciliation over a population**: an opening
balance, in-flows and out-flows, a closing balance, across a labelled period, with organisational
units as row values. That column family exists in no other hr sibling and in no business_operations
artifact I could construct. The absence of the identity-plus-process pair is stated in the second
deterministic rule as a *qualifier* on a positive pair (population + period), not as the trigger —
which is why that rule's own text says "The absence is not the signal". And the sharpest evidence
that the row is not merely "the aggregate ones" is that two of its fixtures,
`attrition_export_2026-02-01T0300.csv` and `Bradford factor report - Ops - Mar 2026.xlsx`, are
strictly **person-level** and still belong here. A row defined by absence could not hold them.

Charges 4–6: Charge 4 is answered by `never_alone` — extension and source type alone never
activate, and `.pbix` appears as a fixture whose correct outcome is a residual. Charge 5 is
answered by the reciprocal boundary with `hr.org-design-headcount` on tense and unit (measurement
of filled positions over a closed period vs authorisation of posts for a future one), stated on
the same fixture from both sides. Charge 6 is **conceded in part and stated in the JSON rather
than hidden**: under PR-6 the encoded `dimension_order` is `[]` on both rows, so leg 2 of the node
test cannot distinguish them today. The row therefore rests on legs 1 and 3, which is sufficient —
§2's test is disjunctive — and the prose difference is recorded for R1c under NJ-WFA-1.

**Verdict: the node survives, on legs 1 and 3.** Nothing was invented to keep it: `fields: []`,
`proposed_fields: []`, no minted key, no dimension, and the two keys that were genuinely tempting
are refused in writing.

## The node test, all three legs

**Leg 1 — detection signals differ from the hr default. Yes, and the difference is structural.**
The schema's default requires labelled slots that *jointly identify an employee or cohort AND a
personnel process*. This row's signals require a *population and a period* and are indifferent to
whether any individual is present. Concretely: the balance family (opening / joiners / leavers /
closing), the as-at-or-period slot beside aggregate measure columns, the job-category × protected-
characteristic cross-tabulation, the occasions-plus-days-lost absence index, the measurement-noun
slide-title set, and the event-level export with a reason category and no case artifacts. Seven
rules, none of which is a specialisation of a schema rule.

**Leg 2 — recommended dimensions differ, but cannot be encoded.** The schema's stated prose
default is work type or named people programme first, then workforce unit or cohort, then people
cycle. This row recommends **people cycle first, work type second, and workforce unit omitted
rather than demoted.** The reason is evidential rather than aesthetic: a measurement report exists
in order to span units and slice them, so a unit level would force one column *value* to be
promoted into the file's own fact — the precise error the JSON forbids in
`Headcount and movement - FY26 Q3.xlsx`'s `must_not_conclude` — and would scatter a single
quarter's pack across several unit folders. `time_first` is false: a labelled reporting period
defines this world, and a capture or modification date routinely differs from it by weeks, so the
photo-style time-primary ordering would be wrong. Under PR-6 none of this can be written into
`dimension_order`, so it is held as prose in `template.why` and raised as NJ-WFA-1.

**Leg 3 — privacy rules differ in kind, not degree. This is the row's strongest leg.** Every
other hr sibling protects because a person is named. Here the material *looks* safe and is not:
a table naming nobody discloses through small cells, and the harm surface is the cut rather than
the cell. The operative rule is therefore inverted — **aggregation is not de-identification, and
the absence of a name is not evidence of safety** — and it is encoded twice: as a `never_alone`
rule ("the absence of any person's name as proof that a file is aggregate or safe") and as a
`needs_llm` abstention rule that leans on `00`'s "It must return unknown where support is
insufficient." The schema anchor's own NJ-HR-4 points at this row by name, which is good evidence
the difference is real and not manufactured: the schema knew it had a question it could not answer
without this template. No threshold, cell-size rule, or handling class is stated.

## Files considered and rejected

The tempting false positives, and why each is not this row's evidence:

- **`Project Atlas resource utilisation Q1.xlsx` — kept, as THE collision fixture.** See below.
- **`March 2026 payroll register - FINAL.xlsx`** (the fixture the hr schema names against finance)
  — rejected as evidence. It is row-per-person and summable into a workforce cost figure, which is
  exactly the trap. Its rows are *payment obligations* with a pay-run identifier, deductions and a
  remittance structure; a workforce cost report has none of those and does not reconcile a
  population. Recorded as a reciprocal collision with `hr.payroll-benefits-administration`.
- **`FY27 establishment and headcount plan v5.pptx`** (named on the hr schema row against
  business_operations) — rejected. Same word, opposite tense. It authorises posts; this row counts
  filled ones. Its analogue is kept as a fixture (`Headcount by cost centre - budget submission
  FY27.xlsx`) precisely so the row can state what it refuses.
- **A learning completion roster / training matrix** — rejected. It has a population and a
  percentage and looks like measurement, but its rows are curriculum obligations against named
  learners; it is `hr.training-development`'s corpus. If a *completion rate by unit over a period*
  is extracted from it, that extract is this row's; the roster is not.
- **An engagement survey response dataset with a comments column** — rejected outright, and this
  one matters: it is the most dangerous near-miss because it is population-shaped, aggregate-
  looking and full of protected free text. It carries the instrument's structure (item codes,
  scale points, wave) and belongs to `hr.engagement-survey`. Taking it would have let this row
  swallow the sibling entirely.
- **An org chart (`.vsdx` / `.pptx`)** — rejected. It is a structure diagram, not a measurement;
  span-of-control *reporting* derived from it is this row's, the chart is `hr.org-design-headcount`'s.
- **`People analytics vendor proposal - Visier.pdf`** — rejected. A procurement document about a
  workforce-analytics tool is business_operations. It contains more of this row's vocabulary per
  page than most genuine fixtures do, which is why the vendor-name `never_alone` rule exists.
- **A published labour-market or benchmark report** — rejected. It measures *someone else's*
  workforce. Reading Inbox handles it; the "own organisation vs vendor benchmark" question is a
  `needs_llm` rule rather than a fixture because its correct outcome teaches this row nothing.
- **A board pack with a People section among eight others** — rejected as a fixture. It is a
  business_operations governance artifact that contains a people slide; the discriminator is
  whether the *file* is the measurement or merely carries one. Left to the collision statement.

## The collision fixture

**`Project Atlas resource utilisation Q1.xlsx`.** Columns `name / role / work package / billable
hours / capacity hours / utilisation % / department`, plus a milestone tab and a project end date.
It contains four of this row's metric words (utilisation, capacity, department, %), it is a
spreadsheet, its rows are people, and it reports a percentage by unit over a quarter. Every
surface signal says workforce analytics.

**What discriminates it:** the denominator. Utilisation is measured against a *project's scope* —
work packages, capacity hours, a bounded end date. Workforce analytics is measured against a
*period* — an opening balance reconciled to a closing one, with employment status and movement.
The file has no opening or closing population, no joiner or leaver column, and no employment-status
field, and it has a milestone tab and an end date that no population report has. The one-line rule
written into the JSON: *utilisation measures people against scope; workforce analytics measures a
population against a period.*

## Reciprocal boundaries

Nine collisions, each stated in both directions on named bytes. The three that required real work:

- **`hr.org-design-headcount`**, on `Headcount by cost centre - budget submission FY27.xlsx`.
  Neither side may take the other's tense: the sibling must not take a period-over-period
  reconciliation of the population that existed merely because "headcount" appears; this row must
  not take approved posts, vacancies, effective-from dates or a signed proposal merely because
  they are counted. Same bytes, opposite readings, both written out.
- **`clinical_practice`**, on `Clinic staffing grid - March 2026.xlsx`. This is the only boundary
  already argued against this id by a landed row:
  `clinical_practice.practice-administration.json` states that "a staffing grid read alone is
  hr.org-design-headcount or hr.workforce-analytics material, and only its clinical-session
  content moves it here - the reciprocal boundary stated on both sides." This row reciprocates on
  the same fixture and adds the sharper half its side owns: a **leave marker in a rota cell is not
  a measured absence occasion**, so this row must not read a rota as absence data even when the
  clinical side declines it.
- **`hr.engagement-survey`**, on `People dashboard - Feb 2026.pptx`. The instrument stays with the
  sibling; only the resulting measure comes here. Neither sibling has landed to agree it, so it is
  also NJ-WFA-3 rather than a settled fact.

The remaining six (`hr.dei-program`, `hr.employee-relations`, `hr.payroll-benefits-administration`,
`hr.compensation-planning`, `business_operations`, `finance`) are stated in the JSON in the same
MUST NOT TAKE / MUST NOT TAKE form, each naming a shared fixture.

## Neighbours considered that did NOT get a collision edge

- **`career`** — no collision, a `role_split` instead. The assignment named it a must-consider,
  and the honest finding is that this row's evidence and career's never compete: even the
  person-level attrition export is an *employer's* extract about a population, never the
  individual's own evidence about themselves. There is no fixture both sides could claim, so a
  collision would be decorative. The split is recorded instead.
- **`legal`** — an employment-tribunal statistics annex is legal's matter evidence; a workforce
  report is not a legal instrument. No shared discriminating evidence. The hr schema row already
  carries legal as a schema-level co-activation, which is the right level for it.
- **`identity`** — a demographic monitoring return touches protected characteristics but is never
  an identity document. The protection outcome that matters is already carried by
  `sensitivity: potentially_sensitive` and the Protected Records route.
- **`hr.workplace-health-safety`** — genuinely close (incident *rates* are workforce measurement),
  but the sibling's fixtures carry an incident, an injured person and a corrective action, and
  this row's absence rules explicitly refuse to read a health event. Left as a boundary the memo
  names rather than an edge, because no shared fixture survived construction.
- **`also_holds_with`** — empty **by contract**, not by omission. It is declared on schema rows;
  a template may not widen its schema's co-activation set. Two fixtures carry
  `also_schema: business_operations`, which is lawful only because the hr schema row already
  declares business_operations. Noted in `also_holds_with_note`.

## proposed_fields — empty, and why

Two keys were genuinely tempting and both were refused rather than proposed.

1. **A reporting-period key.** The reporting period is the one fact this material always carries
   and the level this row wants to lead with. But hr already proposes `people_cycle` for a bounded
   people cycle, and a measurement period *is* one. Minting a second period key is precisely the
   variant-minting this pass exists to prevent, so the row reuses the pending proposal and its
   fate is NJ-HR-1's, not mine.
2. **A measure or population-cut key.** A cut resolves to `workforce_unit` where it resolves at
   all. A measure name — attrition rate, Bradford score, FTE, median gap — is a value inside
   content, never a key, and certainly never a folder level: a directory tree branching on metric
   names would fragment one period's pack across five folders and would encode a vocabulary that
   changes whenever a vendor renames a tile. This is the same refusal `finance.crypto-assets` made
   for the asset ticker, for the same reason.

`fields: []` additionally because rule 12 forbids a template copying its schema's list, and
because the hr schema declares none at all under PR-6.

## Sparse-file discipline

`hc.csv` is the `HW 3.pdf` of this node: two unheadered columns, a short string and an integer,
sitting in the same download session as the quarter's workbook. It is marked
`group_without_copying_facts: true`, its `facts_legal` is the universals only, and its
`must_not_conclude` forbids both the tempting inferences — copying the neighbour's reporting
period or unit, and reading `hc` as an abbreviation of headcount. `Screenshot 2026-03-04 at
10.12.31.png` and `People analytics model.pbix` carry the same flag for the same reason: a legible
tile figure with no period, and a filename with no readable content behind it, are not facts.

## Audits run before returning

- `python3 -m json.tool` — parses.
- Key set compared mechanically against `hr.json`: **no missing keys**; five extra keys
  (`fields_note`, `proposed_fields_note`, `work_types_note`, `proposed_context_terms_note`,
  `also_holds_with_note`), which are the house idiom used by the landed `finance.crypto-assets`
  row for exactly this purpose.
- All thirteen quoted `00` spans were verified with `grep -F` against
  `planning/00-database-agent-product-design.md` **before** being written. 13/13 matched verbatim.
  **No `00` quotation in this node is fabricated or paraphrased inside quote marks.**
- Every `file_examples.source_type` is in `SOURCE_TYPES` (13/13); every `file_kinds.source_types`
  member too (8/8).
- Every `collides_with.domain` and `role_split.domain` resolves to a roster id (10/10); the one
  `also_schema` value used resolves to a roster schema id; every `falls_through_to.template` and
  every `falls_through_if_inactive` is one of `00`'s nine residual names (5/5 and 13/13).
- `fields: []` and `proposed_fields: []`, per PR-6 and rule 12.
- No number in the file is a threshold, score, or count of evidence — the digits present are
  filenames, years and dates inside fixture names, and prose references.
- No handling class is assigned; `sensitivity` is `potentially_sensitive` only.
- Only the two assigned files were written. `planning/29-DOMAIN-OWNERSHIP.md`, the roster,
  `canonical_fields.json`, `check.py`, `src/`, the SPECs and every neighbour node are untouched.

## NEEDS-JOSEPH (this node only)

- **NJ-WFA-1 — the recommended order, which PR-6 will not let this row encode.** The hr default is
  work type → workforce unit → people cycle. This row recommends people cycle → work type, with
  workforce unit **omitted** rather than demoted. Alternatives: (a) adopt this row's order;
  (b) keep the schema default and accept that one quarter's pack scatters across unit folders;
  (c) permit a unit level only where every report in the corpus is genuinely single-unit.
  Unresolvable until R1c rules on `people_cycle` under NJ-HR-1.
- **NJ-WFA-2 — where person-level analytic exports live.** `attrition_export_2026-02-01T0300.csv`
  and `Bradford factor report - Ops - Mar 2026.xlsx` are reporting artifacts whose rows are
  individuals. This row claims them with the protected posture, because their purpose is the
  population. The alternative is a bright line — any file carrying an employee identifier leaves
  this row for `hr.payroll-benefits-administration` or `hr.employee-relations` — which is far
  easier to enforce but strands ordinary attrition analysis inside a case-file row and would
  weaken this row's answer to Charge 3.
- **NJ-WFA-3 — whether the periodic pack splits.** This row claims
  `People dashboard - Feb 2026.pptx` whole and leaves the instrument with `hr.engagement-survey`
  and the programme with `hr.dei-program`. Stated reciprocally in `collides_with`, but neither
  sibling has landed, so no one has agreed it. **Recommendation to R1c:** when those two rows are
  written, they should carry this fixture with the same discriminator (instrument vs measure), or
  this row's claim should be withdrawn.
- **NJ-WFA-4 — this row depends on NJ-HR-4.** If aggregated workforce material does *not* stay
  protected by default, `sensitivity_why` here must be rewritten rather than softened, because
  the whole of leg 3 rests on it. This row answers yes and invents no threshold.

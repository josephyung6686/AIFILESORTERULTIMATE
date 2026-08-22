# research.dataset-analysis — lab notes

Roster row: `kind: template`, `schema_id: research`, `launch: placeholder`,
`file_kind_owner: ["spreadsheet"]`, `must_consider_neighbors: ["code"]`,
`must_consider_residuals: ["Review Later"]`.
Verdict: **node accepted** (`refuse_node: false`).

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span this
  node puts inside quote marks was matched against it mechanically before being written (a
  script walked every string in the emitted JSON, split on quote characters, and required each
  quoted segment to appear verbatim in `00`; it reports 0 problems). The load-bearing spans are
  the Research field sentence, the spreadsheet and structured-text format-coverage bullets, the
  code-structural-evidence rule, the project-before-time ordering rule, the
  parent-makes-the-child-intelligible rule, the narrow-date warning, the session-is-not-topic
  rule, the grouping firewall, the residual definitions for Review Later / Unsupported or
  Encrypted / Protected Records / Reading Inbox, and the two privacy sentences that bound what
  may reach a model.
- `planning/01-product-design-structured.md` — §2.9 (format coverage, the spreadsheet and
  notebook yields) and §3.11 (domain-scoped schemas) only, as locators. `00` wins everywhere and
  nothing here rests on a section number.
- `planning/domains/_CONTRACT.md` (entry shape, rules 8, 11–15), `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md` (sections 1–8), `CONNECTION-EXAMPLES.md` (fixtures 1–2).
- `planning/domains/roster.json` — confirmed the id, kind, schema, neighbours, and that all four
  collision targets are real roster ids.
- `planning/domains/canonical_fields.json` — every field named in `dimension_order` resolves
  (`project`, `artifact_type`, `stage`); `dataset_name` does not, which is why it is a proposal
  and not a dimension.
- `planning/domains/nodes/research.json` (the schema this template points at),
  `research.project-workspace.json` (refused — it routes its own `results_batch07.xlsx` fixture
  here), `research.manuscript-publication.json` (sibling shape).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; every `file_examples.source_type` is a
  member.

## Why the node test passes

The three limbs, against the schema's default order (`project → stage → artifact_type`, which is
`00`'s own recommendation and lives on `research.json`):

1. **Detection.** The schema row fires on prose-artifact structure — abstract headings, manuscript
   title blocks, numbered protocol steps, submission-lifecycle terms, venue hits. This template
   fires on structure with no prose in it: a header row over repeated same-typed rows, pipeline
   sheet names, a column/definition/units codebook table, notebook cell types beside a cell that
   names a data file, a script that reads a table and writes a results file. A file can satisfy
   every signal here and contain no sentence.
2. **Dimensions.** `artifact_type` rises above `stage`. One dataset keeps its raw, cleaned,
   codebook and results forms while its stage moves; stage-first splits one dataset's lineage
   across sibling folders whenever an exploratory pass and a reported pass touch the same data.
3. **Privacy.** A different rule, not a stronger one. The schema's sensitivity is about
   unpublished work and editorial mail. Here the exposure is mechanical: the extraction that makes
   a dataset legible is the one that lifts cell values into evidence, and a participant table's
   cell values are person-level rows. The added rule is that sheet names and column headers are
   dossier material and person-shaped cell rows are not.

## Files considered and rejected

- **A dedicated `.parquet` / `.h5` / `.sav` example.** Rejected as a *node*-level fixture: they are
  extensions, and an extension-only distinction is exactly what the node test refuses. They stay
  in `file_kinds.extensions` where they belong.
- **A SQL query file (`extract_cohort.sql`).** Real, but it adds nothing the notebook and script
  fixtures do not already carry, and the code-vs-research discriminator is identical.
- **A `.vcf` or `.ics`.** This situation never sees them as its own material. A participant roster
  can *look* contacts-shaped, which is why that trap is written into
  `PVA-RDP_participants_raw.csv`'s `must_not_conclude` rather than given a fixture of its own.
- **A README in a data directory.** Folded into the codebook fixture; a data README that names
  columns *is* the codebook signal, and one without column names is a project-workspace file, not
  this template's.
- **A figure image (`Figure_3.png`).** Belongs to the schema row and to
  `research.manuscript-publication`; the figure *source data* (the table behind the figure) is
  this template's, and that is a `work_types` value, not a fixture.
- **A LaTeX table fragment.** Manuscript material.

## proposed_fields justification

One proposal: **`dataset_name`**, `destination_eligible: false`, and deliberately kept out of
`dimension_order`.

One project routinely holds several datasets and their derivatives interleave. No canonical key
separates them: `project` is the project; `artifact_type` is orthogonal (every dataset has a raw,
a cleaned and a results form); `version_family` is the universal draft-family fact and a cleaned
table is not a *version* of the raw table but a different object derived from it; `subject` is the
academic key under D6. So the handle that groups one dataset's derivatives is missing.

It is proposed, not used. `_CONTRACT` rule 8's second half — checked across `uses_schema` for
templates — means a template may branch only on a field its schema declares, and the Research
schema does not declare this key. Adding it to the Research schema is R1c's or Joseph's call, so
the node records the gap, keeps the dimension order legal, and files the consequence as its
`open_question`. Until then the dataset is a P9 group, not a folder level — which is the correct
default anyway, because a group is reviewable and a folder level is not.

## Neighbours considered that did NOT get an edge, and why

- **`research.project-workspace`** — no `collides_with`. It is refused as a node; edging to a
  refused row would encode a mutex against something that will not exist. The material that would
  have sat on its side reaches the schema's default template directly.
- **`research.manuscript-publication`** — no edge. A results table cited in a manuscript is a
  *sequence* (this template's output becomes that template's input), not two templates competing
  for one evidence item. Nothing here fires on a cover letter or a manuscript id, and nothing there
  fires on a header row.
- **`research.grants-funding`** — no edge, though a budget workbook is tabular. The already-authored
  `research ↔ finance` collision on the schema row carries that discrimination (project-scoped
  budget vs account-scoped record), and duplicating it at template level would be the same signal
  stored twice.
- **`code.software-project`** — no edge; the notebook collision is with
  `code.notebooks-experiments`, and `code.software-project`'s discriminator (repository root,
  package manifest) is already the *signal text* of that collision. Two edges, one discrimination,
  would be redundancy.
- **`academic.coursework`** — considered and dropped. A course lab report with a Data section is the
  tempting case, but the `research ↔ academic` collision on the schema row already names the
  discriminator (course-code-plus-academic-context), and this template's signals need a header row
  and repeated rows, which a lab writeup does not have.
- **`photos.screenshot-captures`** — no edge. The table screenshot is handled inside this node's
  own fixture (`must_not_conclude`: no `media_type` from absent EXIF), and the photos schema's own
  screenshot handling is not in competition for the *research* reading of the OCR'd table.

Four collisions were authored: `code.notebooks-experiments`,
`research.lab-notebook-protocols`, `finance.small-business-bookkeeping`,
`medical.wearable-health-exports`. Each has a fixture in `file_examples` and each names a
discriminating signal. Reciprocity is R1c's; none of these four node files exists yet.

## Contract notes for R1c

1. **`also_holds_with` is empty on purpose.** The roster's `one_line_hint` for this id calls it a
   strong `also_holds` candidate with the code schema, and the dispatch prompt's edge table reads
   as though a template may author the edge. `CONNECTION.md` section 5 says `also_holds_with` joins
   **schemas only**, and CONNECTION wins over the prompt (the prompt says so itself). The
   co-activation is real and is already authored on both `research.json` and `code.json`; here it
   survives as the `also_schema: "code"` value on the `analysis/model_fit.py` fixture and as
   `also_holds_with_note`. Nothing is lost, but a merger should not read the empty list as "this
   situation never co-activates".
2. **`file_kind_owner` exclusivity.** `research.project-workspace`'s refusal already flagged this;
   it recurs here. A project's raw results workbook and a personal budget workbook are both
   `spreadsheet`, and this row is the roster's `spreadsheet` owner. If a later reviewer reads
   `file_kind_owner` as exclusive, `finance.small-business-bookkeeping` (also a spreadsheet-owning
   row) and this one are in direct contradiction. Reading it as *primary interest* makes both rows
   correct and makes the collision edge do the actual work. R1c should settle the reading, not the
   ownership.
3. **`Review Later` is missing from `research.json`'s `falls_through_to`.** Same finding as the
   refused sibling's. Four of this node's twelve fixtures fall through there, and it is the
   roster's own `must_consider_residual` for this id.

## NEEDS-JOSEPH (this node only)

**NJ-R-DATASET · Is a dataset a folder level, and if so does lineage or analysis own the
derivatives?**

Two linked halves, copied from the node's `open_question`:

1. One project usually holds several datasets, and no canonical key separates them (see
   `proposed_fields.dataset_name`). Should the Research schema gain such a key so a dataset can
   become a folder level, or is a dataset a P9 group only — held together by evidence and never by
   a folder?
2. If it does become a level, the lineage question follows immediately: does a cleaned table, and
   the results derived from it, live under the **dataset** it came from, or under the **analysis**
   that produced it?

The two answers give different trees from identical facts. `00`'s position is only that the facts
do not change when the view does, which is precisely why this node must not pick one: it decides
someone's real folder structure.

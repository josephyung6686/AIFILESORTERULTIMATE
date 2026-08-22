# research.project-workspace — lab notes (R1b)

**Verdict: `refuse_node: true`.** This id is the Research schema's default template wearing a
template id. The node file records the reasoning, the fixtures, and two findings for R1c.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every span I put inside quote
  marks was grep-verified against this file before it was written (mechanical check over the
  emitted JSON: zero misses attributed to `00`).
- `planning/domains/_CONTRACT.md` — entry shape, rules 8 and 11–15.
- `planning/domains/CONNECTION.md` — §2 node test, §5 closed edge vocabulary, §8 the
  `destination_dimensions` resolution path that makes this refusal free.
- `planning/domains/CONNECTION-EXAMPLES.md` — checked for a fixture naming a research template
  row. **There is none.** The research mentions there are all schema-level (fixture with
  `activation.schemas = ["research", "college_applications"]` and an `also_holds_with` edge between
  the two schemas). This matters: `academic.coursework` survived a near-identical challenge partly
  because fixtures 1 and 7 name `tpl.academic-coursework` explicitly. Nothing names this row.
- `planning/prompts/ALIGNMENT.md` — the binding sentence (line 84).
- `planning/domains/roster.json` — my row plus the eight sibling templates on `schema_id: research`.
- `planning/domains/canonical_fields.json` — `project`, `stage`, `artifact_type`, `lab`, `venue`,
  `authored_by` rows read; no key proposed.
- `planning/domains/nodes/research.json` — the schema row, which already carries the entire content
  this row would have carried.
- `planning/domains/nodes/academic.coursework.json` — read as the shape precedent for a
  "default-looking" template that was *kept*, to test whether the same argument rescues this one.
- `src/evidence_shape/vocabulary.py` `SOURCE_TYPES` — every `file_examples.source_type` checked
  against it.

## Why it fails the node test — the three limbs

The test (CONNECTION §2, ALIGNMENT line 84): a template row exists only if its **detection
signals**, **recommended dimensions**, or **privacy rules** differ from its schema's default.

| Limb | This row | Schema row (`research.json`) | Differs? |
|---|---|---|---|
| dimension_order | project → stage → artifact_type | project → stage → artifact_type | no |
| detection signals | project token + artifact structure, minus whatever a sibling claims | the same list, authored | no |
| privacy rules | potentially_sensitive; unpublished work, human subjects | identical wording in substance | no |

The roster's own `one_line_hint` concedes the first limb in writing.

## The steelman I tried, and why it failed

`academic.coursework` is the precedent for keeping a row that *looks* like its schema's default. It
survived on three things: a binding fixture naming it, a **narrowed `work_types`** list (gradebook
and transcript pushed to sibling rows), and a **privacy rule with a different direction** (the
holder's own record versus other people's records — a roster column routes a file *away*).

I looked for all three here:

- *Fixture:* none exists (checked above).
- *Narrowing:* the opposite. `research.project-workspace` is the **widest** row on the schema. Its
  eight siblings each take a structural fingerprint — manuscript lifecycle, abstract/poster/deck,
  numbered protocol + instrument output, dataset + analysis, proposal + budget, IRB + consent,
  DOI-only reading material, degree project. What is left is "the schema fired and nothing else
  dominates", which is a **complement**, not a signal. Defining a template by complement is exactly
  what "the schema's default template" means.
- *Privacy direction:* the sharper rules on this schema belong to `research.ethics-compliance`
  (participants) and `research.manuscript-publication` (pre-publication material). The workspace
  row inherits the schema's general posture unchanged.

I also checked that refusing breaks nothing downstream. It does not: CONNECTION §8 already
specifies `destination_dimensions(domain_id)` accepting "a schema id resolving through the schema's
default template", and `research.json` holds that default inline. So the material still activates,
still groups, and still reaches project → stage → artifact_type. The only thing lost is a second
stored copy of one recommendation — which is the defect `_CONTRACT.md` rule 8 was written about
(one concept, two vocabularies, at scale).

The alternative — inventing a difference to save the id (reordering to project →
artifact_type → stage, or promoting `lab` to a dimension) — is the named 574 failure. I did not do
it.

## Files considered, and which row already covers each

Eleven researched, none of which needs this row.

| File | source_type | Already covered by |
|---|---|---|
| `PVA-RDP_project_plan_v3.docx` | text_document | the schema's default template (no sibling; nothing added) |
| `notes_2026-03-11.md` | text_document | same; sparse — `group_without_copying_facts` |
| `PVA-RDP_manuscript_v7.docx` | text_document | `research.manuscript-publication` |
| `submission.zip` (schema row's own fixture, not re-listed) | archive | `research.manuscript-publication` |
| `Protocol_RNA-extraction_v2.docx` | text_document | `research.lab-notebook-protocols` |
| `Notebook_2026-03_p14_scan.pdf` (schema row's fixture) | ocr | `research.lab-notebook-protocols` |
| `results_batch07.xlsx` | spreadsheet | `research.dataset-analysis` (roster `file_kind_owner`) |
| `PVA-RDP_labmeeting_2026-03-11.pptx` | presentation | schema default; see finding 2 below |
| `Figure_3_final.ai` | design_creative | schema default (artifact_type only) |
| `Screenshot 2026-03-02 ….png` | ocr | falls through — Temporary Screenshots |
| `IRB_Protocol_PVA-RDP_2026_signed.pdf` (schema row's fixture) | text_document | `research.ethics-compliance` |
| `Abstract_PVA-RDP_UChicago.pdf` | text_document | `research.conference-presentation`; `also_holds_with college_applications` at schema level |
| `Ravikumar_2019_NatureMethods.pdf` | text_document | `research.reading-library` / Reading Inbox — the **collision fixture** |
| `analysis/train_eval.py` | code_structured | the `code` schema (repo markers beat the project token) |
| `Lab 4 writeup.docx` | text_document | the `academic` schema (course-code + context) |

The two rows in the collision column are the ones that matter for a workspace-shaped template
specifically: a directory named for a project will contain **someone else's paper** and **a
repository**. A template whose only anchor is "these files sit in the project's working directory"
absorbs both. That is why the `never_alone` entries I kept are about the *project token and the
project folder*, not about artifact structure.

## Files I considered and rejected from the list

- A `.ics` lab-meeting invite and an editorial `.eml` — already fixtures on the schema row; adding
  them here would only have padded a refused node.
- `Run07_platereader.raw` — instrument output; belongs to `research.lab-notebook-protocols` and is
  already the schema row's `Unsupported or Encrypted` fixture.
- A `README.md` at a project repo root — a genuinely interesting seam, but it is the `code`
  schema's, and drawing it into a research workspace row would be exactly the repository-traversal
  `00` warns against.
- A conference travel receipt found in the project folder — a residual (`Receipts and
  Confirmations`) reached by empty activation, not a research file. Residuals are not nodes.

## proposed_fields

**None.** Nothing here needs a key the canonical list lacks. The situation's fields are the
schema's five plus `authored_by`, all already canonical, and a refused row must not mint anything.

Two value-level gaps noted for R1c (values, not fields, so neither is a proposal): the research
schema row's `work_types` list omits **project plan** and **meeting notes**, both of which are real
`artifact_type` values in a working directory. Values auto-create at runtime, so this is a
completeness note on the schema row's enumeration only.

## Neighbours considered that got no edge, and why

A refused node authors **no edges** — `collides_with` and `also_holds_with` are reciprocal, so an
edge from a row that will not merge leaves a dangling half on a row that will. All four candidates
are already carried at schema level:

- `code` — the strongest candidate (shared `project` and `artifact_type` canonical keys, and my
  `analysis/train_eval.py` fixture sits on the seam). `research.json` already carries both a
  `collides_with` (repo markers are the discriminator) and an `also_holds_with` (a computational
  project's notebook holds both fact sets). Nothing to add.
- `academic` — `Lab 4 writeup.docx` is the fixture; `research.json` already carries the collision
  with the course-code-plus-context discriminator, and `academic.coursework` already carries the
  reciprocal naming `research.project-workspace` as its target. **That reciprocal is now
  one-sided** and is flagged below.
- `college_applications` — 00's own two-schema case (`Abstract_PVA-RDP_UChicago.pdf`), already an
  `also_holds_with` on the schema row.
- `finance` — a project budget beside a sponsor name; already a schema-row collision, and it is
  `research.grants-funding`'s situation, not this one.
- `research.manuscript-publication`, `research.dataset-analysis`, `research.lab-notebook-protocols`
  — template↔template collisions would have been legal (same kind), and I drafted them before
  refusing. They are dropped with the row: a set of collisions among siblings that exist only to
  carve out a complement is the clearest possible sign the complement is not a node.

## Deferred catalogues

Not consumed. Recognition here would have needed R4 gazetteer contents (orgs, venues) and R6
patterns; I invented neither, and a refused row states no rule families.

## Where CONNECTION and the dispatch prompt disagreed

They did not conflict on anything I relied on. One wording note: the dispatch prompt states the
refusal condition conjunctively ("detection signals, dimension order, **and** privacy rules are
identical"), while CONNECTION §2 and ALIGNMENT state the survival condition disjunctively
("detection signals, recommended dimensions, **or** privacy rules differ"). CONNECTION wins per my
brief, but it does not matter here: all three are identical, so the row fails under either reading.

Shape note: `_CONTRACT.md` rules 12–14 name `uses_schema` where the R1b dispatch shape uses
`schema_id`, and name `file_kind_plausible` where the R1b shape uses `file_kinds`. I emitted the
R1b dispatch shape, matching every landed peer node in `planning/domains/nodes/`. The rename is
R1c's merge concern, not a per-node decision.

## NEEDS-JOSEPH (this node only)

- **NJ-local-1 · The reciprocal that this refusal breaks.**
  `academic.coursework.json` already authors `collides_with: research.project-workspace` (the
  course-numbered thesis / lab-report seam, fixture `Senior Thesis Draft 3 - BIO 4990.docx`). With
  this row refused, that edge points at a non-row. It should be re-pointed at the `research`
  **schema** — where the same collision is already authored from the other direction — or at
  `research.thesis-dissertation`, which is the situation the fixture actually describes. I did not
  edit that file; re-pointing it is R1c's, and this is the note that tells R1c it must.

- **NJ-local-2 · Does a refused default-template row leave the schema under-served at P10?**
  Refusing is correct by the node test, and CONNECTION §8 says the resolution path exists. But a
  reader of the roster will now see nine `research.*` template ids and eight files, and may re-mint
  this row rather than read the refusal. If Joseph wants the schema's default template to be
  *visible* as a browsable row, the honest form is a marker on the schema row (its `template` block
  already is that), not a duplicate template id — and that is a decision about how the library is
  presented, which is his.

- **NJ-local-3 · `file_kind_owner` — exclusive claim, or primary interest?**
  The roster gives `presentation` to `research.conference-presentation` and `spreadsheet` to
  `research.dataset-analysis`. An internal status deck and a raw results workbook are neither. With
  this row refused they route to the schema and its default template, which is right; but if a
  later part reads `file_kind_owner` as exclusive, those two fixtures get mis-shelved. Worth
  settling once, roster-wide.

- **NJ-local-4 · Carried, not re-opened:** the schema row's own open question — whether a PI-named
  `lab` is an organization (a real dimension) or creator identity (metadata only) — bites hardest
  in exactly this situation, where a shared protocol has no single project to branch under
  (fixture: `Protocol_RNA-extraction_v2.docx`). It is `research.json`'s question and stays there.

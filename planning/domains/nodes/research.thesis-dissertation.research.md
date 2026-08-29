# research.thesis-dissertation — lab notes

Roster row: `kind: template`, `schema_id: research`, `launch: placeholder`, `provenance: inference`.
Verdict: **node accepted** (`refuse_node: false`). Reasoning below.

---

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. **`00` never uses the words
  thesis, dissertation, chapter, committee, defense, advisor or supervisor.** Grepped and
  confirmed before writing a line. So nothing on this node is `provenance: design` except
  quotations of general rules; the row itself is `inference` off `00`'s named Research domain
  ("Research files may use project, stage, artifact type, lab, and venue").
- `planning/domains/_CONTRACT.md` (entry shape, rules 8–15).
- `planning/domains/CONNECTION.md` (four graphs; node test §2; closed edge vocabulary §5;
  activation §4; template/schema ownership §7) and `CONNECTION-EXAMPLES.md` is referenced by it.
- `planning/prompts/ALIGNMENT.md` — the "a template that would only repeat its schema's fields
  and dimension order is not a node" rule, which is the test this row had to pass.
- `planning/domains/roster.json` — confirmed id, kind, schema_id, the nine sibling templates on
  the research schema, and every neighbour id used in an edge.
- `planning/domains/canonical_fields.json` — every field key reused, none minted. Confirmed there
  is no existing key for a chapter ordinal before proposing one.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (all fourteen read; the eleven used here
  are members), `RELIABILITY_STATES`, and D11's note that an extractor writes only
  `direct` / `possible`.
- Landed sibling nodes, read to align and not rewrite: `research.json` (the schema — its fields,
  its default template, its `also_holds_with academic` clause which already names this exact
  thesis case), `research.project-workspace.json` (the refusal shape, read as the counter-example),
  `research.manuscript-publication.json` (which already authors `collides_with
  research.thesis-dissertation`; I matched its wording so the pair reads as one edge),
  `research.conference-presentation.json`, `research.lab-notebook-protocols.json`,
  `research.dataset-analysis.json` (dimension orders and edge conventions).
- Quotation discipline: **every span in quote marks in the node JSON was `grep -F`'d against
  `00` before it was written.** One candidate span failed the check ("an academic abstract that is
  also an application document" — that is the dispatch prompt's paraphrase, not `00`'s wording)
  and was dropped rather than repaired.
- `planning/domains/check.py` was run before and after writing (14 files, 574 entries, 566
  in-file problems, 0 cross-file — unchanged; the gate reads the legacy slice files, not
  `nodes/`). No file other than my two was touched.

## Why this is a node and not a refusal

The node test (CONNECTION §2) asks whether **detection signals, recommended dimensions, *or*
privacy rules** differ from the schema's default template. Honest scoring per limb:

| Limb | Verdict | Why |
|---|---|---|
| Detection signals | **PASS, outright** | None of this row's six deterministic signals appears on `research.json`. The schema's are project-token-plus-artifact-structure, labelled Project/Protocol slots, submission-lifecycle terms, archive manifests, zone-restricted venue hits. This row's are a title-page degree-submission phrase, a labelled signature/approval page, a chapter-numbered contents list beside front matter and appendices, degree-milestone terms, an ETD deposit form, a thesis LaTeX document class. Zero overlap. Without this row, a signed approval page, a deposit form and a defense deck have **no** detection path at all — I checked each against the schema row's six signals and none fires. |
| Dimensions | **PASS, weakly** | `project → artifact_type → stage` vs the schema's `project → stage → artifact_type`. The swap is genuine (see below) but **not unique on this schema** — `research.dataset-analysis` reaches the same order from different material. The test is against the row's own schema default, not against siblings, so this counts; claiming uniqueness would have been a fabricated distinction and is recorded as such in `node_test`. |
| Privacy | **PARTIAL** | Unpublished work and human subjects are the schema's reasons. What is genuinely this row's: committee/examiner reports are evaluative statements about one named person who is normally the file's holder, and an embargo is a file-borne, labelled instruction that the work is not public. Recorded as an addition, not inflated into a distinct regime. |

The refusal shape is `research.project-workspace` — a row whose signals are the schema's restated
and whose dimension order is the schema's copied. This row is not that. But the honest margin is
one strong limb plus two partial ones, and I wrote that into `node_test` rather than dressing all
three as clean passes.

## The dimension argument, stated plainly

`project → artifact_type → stage`, lifting `artifact_type` above the schema default's `stage`.

A degree document divides primarily by **artifact** — chapters, committee feedback, defense
materials, deposit formalities — and each of those carries its own draft-to-final progression.
Stage on top interleaves a chapter draft with a defense deck under one Revision folder and
separates a chapter from the comments written on it. This is `research.manuscript-publication`'s
argument run the other way: there, one project produces several complete venue-scoped submission
families and stage is the live navigation axis; here there is one submission, to one degree
programme, so the artifact is the axis.

Two warnings from `00` that the row **carries rather than hides**:

1. `project` characteristically resolves to a **single value**. `00`: "It should warn when a level
   produces only one child" and "create meaningless one-child levels". In practice the thesis *is*
   the branch. I kept the dimension first anyway (a corpus with both a master's thesis and a
   doctoral dissertation needs it; a one-child level is flattened on the canvas, not removed from a
   recommendation) and said so in `template.why`.
2. `stage` is thin on most of this material — chapters vary by version family, not workflow
   position. `00`: "It should recommend flattening when a dimension does not materially improve
   retrieval", and "each branch should offer the dimensions that are actually present in its member
   groups".

`lab` and `venue` are legal facts here and deliberately **not** dimensions: a thesis is reviewed by
a committee, not a venue, and a lab level fragments one degree document across contributing groups.

## Files considered and rejected

Fourteen file examples landed. Rejected candidates, and why:

- **`Chapter_4.pdf` with a title page** — collapsed into `Ch4_results_v11_AB-comments.docx`,
  which is the harder and more honest version (no title page, no project token, a version suffix
  and a second person's comment metadata). It is this domain's `HW 3.pdf`: `group_without_copying_facts: true`.
- **`thesis_bibliography.bib`** — a `.bib` is real here, but it teaches nothing this list does not
  already cover, and `.bib` appears in `file_kinds.extensions` where it belongs. Adding it would
  have been an extension masquerading as a fixture.
- **`Chapter drafts/` folder listing** — a folder is not a file; folder context enters as a
  `never_alone` entry instead ("a parent folder named Dissertation or Thesis alone"), which is where
  `00`'s "The system learns from existing folders but must not silently reorganize them" belongs.
- **A defense-invitation email (`.eml`)** — `email` stays in `file_kinds.source_types` because
  defense correspondence is genuinely here, but the `.ics` fixture already carries the
  mail-adjacent privacy point ("treating addresses and message content as potentially sensitive")
  and the never-alone-on-attendees point. A second one would have been padding.
- **A raw analysis dataset** — routes to `research.dataset-analysis`, which the roster makes
  `file_kind_owner` of `spreadsheet`. Kept `spreadsheet` in `file_kinds` (thesis appendix tables are
  real) but did not fixture it, so as not to re-claim a sibling's material.
- **`Run07_platereader.raw` / `opaque_binary`** — kept in `file_kinds` for completeness, not
  fixtured: it is `research.json`'s and `research.lab-notebook-protocols`' example and adds nothing
  degree-specific.

The four ugly cases the prompt demands are all present: labelled form vs unlabelled prose
(`ETD_submission_form_signed.pdf` vs `Ch4_results_v11_AB-comments.docx`), OCR of the same thing
(`Approval_page_scan.pdf`), an archive manifest read without unpacking (`deposit_package.zip`),
calendar (`Dissertation defense — room 4.12.ics`), a collision fixture that looks like mine but is
not (`Capstone_Final_Paper_BUSIB4300.docx`, and the sharper
`Ravikumar_dissertation_2014.pdf`), and a file that is legitimately two schemas
(`Appendix_C_participant_consent_forms.pdf` → medical; `main.tex` → code;
four files → academic).

## `proposed_fields` justification — one key, `chapter`

`chapter` (string, e.g. `Chapter 4`), **`destination_eligible: false`**, `provenance: proposal`.

No canonical key holds a part-ordinal inside one degree document. `subject` is a course.
`artifact_type` is a kind and would explode into one value per chapter. `project` is the whole
thesis. `version_family` is `00`'s universal fact for drafts of *one* document — so it already
links `Ch4_v1`…`Ch4_v11` but **cannot** link that family to the separate file holding the
committee's comments on chapter four. That cross-artifact join is this situation's characteristic
sparse-file problem and it has no existing key.

Not destination-eligible, and deliberately absent from `dimension_order`: a folder per chapter is
the thing `00` warns about twice — it "creates a large number of tiny folders" and it "repeats a
concept already expressed in the parent" once the `artifact_type` level already reads Chapters. It
is one of `00`'s "several additional fields used only for search, privacy protection, explanation,
or later review".

**R1c may reject it outright** and leave the ordinal a P4 observation that never becomes a fact.
Nothing in this row's dimensions, signals or fixtures depends on it existing. I would rather record
a real gap than mint a folder level.

## Neighbours considered that did NOT get an edge

- **`academic` (the schema)** — the roster's `must_consider_neighbors` for this id, and the edge is
  **not authorable here**. CONNECTION §5 restricts `also_holds_with` to schema ↔ schema and
  `collides_with` to same-kind pairs; this row is `kind: template`. **This is the one place the
  dispatch prompt and CONNECTION disagree** (the prompt offers `also_holds_with` and names
  `academic` as the neighbour) and, per the prompt's own tiebreak, **CONNECTION wins**. The
  co-activation is real and already authored where it belongs: `research.json`'s `also_holds_with`
  with `academic` names this exact case in its own words. At file level I recorded it as
  `also_schema: "academic"` on four fixtures, which is description, not an edge. `academic` is
  represented in the edge list by its templates: `academic.coursework` and
  `academic.transcripts-credentials`.
- **`research.grants-funding`** — a dissertation-improvement award produces a proposal that reads
  like a thesis proposal. Rejected as an edge: the discriminating item is a sponsor slot, which is
  categorical rather than confusable, and `needs_llm` already carries the proposal-vs-proposal
  question. An edge here would have been topical adjacency, which is exactly what `collides_with`
  was narrowed away from.
- **`research.ethics-compliance`** — a consent-form appendix is fixtured
  (`Appendix_C_participant_consent_forms.pdf`) but not edged. The appendix is a *part of* the
  thesis, and the IRB record it derives from is that row's; no single evidence item confuses the
  two, so the relationship is `falls_through_to Protected Records` plus a fixture, not a mutex.
- **`code.software-project`** — `main.tex` under version control is fixtured with
  `also_schema: "code"`, but the repository-marker precedence rule already resolves it in `00`'s
  own words, and `research.manuscript-publication` already carries the
  `collides_with code.software-project` edge for the LaTeX-tree case. Duplicating it here would put
  one discrimination in two rows.
- **`career.portfolio-work-samples`** — a dissertation used as a writing sample on a job
  application. Rejected: that is a *purpose* reading of a file this row's evidence already
  explains, and under PR-1 `purpose` lives on the college-applications schema only. No edge.
- **`photos.scanned-documents`** — `Approval_page_scan.pdf` is a scan. Rejected because
  `media_type = scan` is a photos fact about the *capture*, not a competing reading of the
  document; `ocr` as a `SOURCE_TYPE` already carries it, and treating a format as a competing
  domain is the format-as-schema bug CONNECTION §9.4 names.

Five edges were authored, all template ↔ template, all against ids verified present in
`roster.json`: `research.manuscript-publication` (reciprocal to an edge that already exists),
`research.conference-presentation`, `academic.coursework`, `research.reading-library`,
`academic.transcripts-credentials`. Reciprocity on the four new ones is R1c's merge job.

## Things I deliberately did not do

- No numeric thresholds, no confidence scores, no handling classes. The embargo fixture explicitly
  refuses to turn an embargo period into anything but a value read from a labelled slot.
- No detector regexes and no gazetteer contents — signals are described as rule *families*
  (`00` / P4: an extractor writes `direct` or `possible`; `validated` names a rule that will
  confirm later). R2 and R4 own the patterns and the lists.
- No `parent_id` (R1b never authors it, PR-5), no `shares_field` (derived, never authored), no
  invented edge names.
- No folder path anywhere. Every fixture's `must_not_conclude` opens with "a folder path".
- No fields copied from the schema — `fields: []` with a note explaining that it is the contract,
  not an omission.

## NEEDS-JOSEPH (this node only)

**NJ-thesis-1 · A thesis branch cannot offer a school level, and probably should.**
`school` and `term` are the academic schema's fields. CONNECTION §3 makes a template's
`dimension_order` a subset of *its own* schema's fields with no parent walk — so a template on the
research schema can never branch on them, even though `research.json`'s `also_holds_with academic`
says both schemas legitimately hold facts on the same thesis file. Three ways out, none of them a
node's to choose:

- **(a) Accept it.** One person's thesis rarely needs a school level; the co-activated academic
  facts stay searchable and explainable without becoming folder levels. Cheapest, and possibly
  right.
- **(b) A mirror template on the academic schema** for the degree-programme view. It would then
  need `collides_with` against this row and risks the two-rows-one-situation shape
  `research.project-workspace` was refused for.
- **(c) Allow a `dimension_order` to draw on the union of a file's co-activated schemas.** That is
  a change to CONNECTION §3 and to the gate — not a catalogue edit, and it would touch every
  template in the roster.

This decides how someone's real degree work is filed, so it is recorded rather than resolved.

**NJ-thesis-2 · Does `chapter` land at all?** R1c's or Joseph's: adopt it as a search/review key,
or leave the ordinal a P4 observation that never becomes a fact. Nothing here depends on the answer.

## Findings handed to R1c (not acted on)

1. `research.json`'s `artifact_type` value list holds none of the degree-specific members
   (signed approval page, deposit form, embargo request, committee feedback, examiner report,
   defense recording, formatting review letter), and its `stage` example (`under review`) is a
   submission-lifecycle value while this situation's stage values are degree milestones
   (proposal defense, candidacy, committee review, defense, deposit, embargo). **Value-list gaps,
   explicitly not a reason for a node** — the dispatch rule that work types are values is what
   stopped me minting anything here.
2. `role_split`: the canonical row for `authored_by` lists `target_school` only, and `instructor`
   lists nothing. A thesis title page prints candidate and supervisor one line apart, and an
   approval page prints four unlabelled names above ruled lines, so `authored_by ↔ instructor` is a
   real same-entity/different-role pair. Widening the canonical list is R1c's or Joseph's, never a
   node's — recorded on the row as `provenance: proposal`.
3. `research.manuscript-publication` already carries `collides_with research.thesis-dissertation`;
   this row now carries the reverse with matching wording. The other four collisions here are
   one-way pending R1c's reciprocity pass.

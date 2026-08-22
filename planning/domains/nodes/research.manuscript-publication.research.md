# research.manuscript-publication — lab notes

R1b, one roster row, `kind: template`, `schema_id: research`. Verdict: **node stands** (`refuse_node: false`).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full; the authority. Every span this
  node puts inside quote marks was grep-verified against it before it was written, and then
  re-verified mechanically: 42 quoted spans extracted from the finished JSON, all 42 found
  verbatim (whitespace-normalised) in `00`. One span that failed that check was a quotation of the
  *schema row*, not of `00`; it was de-quoted rather than left to read as a design citation.
- `planning/domains/_CONTRACT.md` — entry shape, rules 11–15, the closed edge vocabulary.
- `planning/domains/CONNECTION.md` (+ `CONNECTION-EXAMPLES.md`) — binding. Node test, closed
  edges, activation ≠ grouping, browse-only `parent_id`.
- `planning/prompts/ALIGNMENT.md` — templates are organizational situations, work types are values.
- `planning/domains/roster.json` — confirmed id, kind, schema, the nine sibling research templates,
  and every id used in `collides_with`.
- `planning/domains/canonical_fields.json` — the Research row's five keys plus the universals; no
  synonym minted.
- `planning/domains/nodes/research.json` — the schema row. Its default template
  (`project → stage → artifact_type`) is the thing this node had to differ from, and its own note
  reserving `venue` and `lab` for separate template rows is what this situation cashes in.
- `planning/domains/nodes/academic.teaching.json` — read only for convention (a sibling
  `kind: template` row: empty `fields`, empty `also_holds_with`, collisions naming templates).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`, checked programmatically against every
  `file_examples.source_type`.
- I did **not** read `planning/deferred-catalogues/` and this node consumes no catalogue: the venue
  and organization gazetteers it leans on are R4's content, and the manuscript-id and lifecycle-term
  shapes are R6's. This node names rule *families*; it writes no regex, no gazetteer member and no
  number.

## Why this is a node and not padding

The node test asks whether detection signals, recommended dimensions, or privacy rules differ from
the schema's default template. All three do.

- **Detection.** Nothing in the workspace default fires on an editorial-office reply chain, an
  author-query proof, a referee report or a submission manifest. These are lifecycle signals about
  a file's position in someone else's review process, and they are the only signals in this whole
  schema that make `venue` reachable from a *high-weight zone* (a cover-letter salutation, an email
  subject) rather than from a bibliography.
- **Dimensions.** `venue` enters the order. The concrete reason is the rejected-and-resubmitted
  manuscript: one project, one version family, two complete submission lifecycles whose `stage`
  values are identical. With `stage` above `venue`, two submissions interleave inside one Revision
  folder; with `venue` above `stage`, each submission is a readable unit.
- **Privacy.** Unpublished manuscripts, confidential referee reports and editorial correspondence.
  The workspace default's material is the holder's own working output; this material is partly other
  people's, some of it anonymous. `00`'s mail rule is what the row cites, because that is the part
  `00` actually states.

## Files considered and rejected

- **A citation-manager library export (`library.bib`, `Zotero.sqlite`)** — rejected. The `.bib` is
  reference plumbing for whichever manuscript uses it and carries no lifecycle evidence; the
  sqlite file is `opaque_binary` with a filename-only story, which `00` forbids concluding from.
  Both belong to `research.reading-library` or to nothing. `.bib` survives only in `file_kinds`.
- **A journal's author-guidelines PDF** — rejected. Venue-shaped, but it is reading material about
  a venue, not an artifact of a submission. Including it would have made "a venue name in a
  high-weight zone" look sufficient, which is exactly the never-alone this node has to hold.
- **A press release / altmetrics screenshot** — rejected as an example: it is post-publication
  communications material whose evidence is a venue name plus a screenshot, i.e. the two weakest
  signals in the node stacked. It would have been a padded example.
- **An ORCID or funder-report export** — rejected; a career/grants artifact, not a manuscript one.
- **A conference poster (`Poster_ASM2026.pptx`)** — deliberately excluded and handled as a
  *collision* with `research.conference-presentation` instead, because the roster gives that
  template ownership of the `presentation` source_type. Writing it as a file example here would
  have quietly claimed the file kind.

Fifteen examples were kept. The ones doing real work rather than illustrating the happy case:
`Response to Reviewers.docx` (the `HW 3`-shaped sparse file — `group_without_copying_facts: true`,
no project fact from the neighbouring manuscript), `Ravikumar_2019_NatureMethods.pdf` (the
collision fixture that looks exactly like this template and is not),
`Abstract_PVA-RDP_UChicago.pdf` (`also_schema`, one file two schemas),
`PVA_manuscript_final_FINAL_v2 (1).docx` (the version/duplicate mess where the name lies about
recency), `Proof_marked_scan.pdf` (broken-vs-absent text layer), `IMG_5512.png` (portal capture
with no EXIF), `submission_PVA-2026-0417.zip` (archive read from its manifest only), `main.tex`
(the code-side structural discriminator).

## proposed_fields — one, and why

`manuscript_id` (identifier, `destination_eligible: false`, provenance `proposal`).

The submission tracking token issued by an editorial system is what physically ties the decision
email, the referee report, the proof header, the portal capture and the response document together
— it is repeated verbatim across five different `SOURCE_TYPES`. No canonical key holds it:
`project` is coarser (one project, many submissions), `venue` is coarser in the other direction
(one venue, many of the holder's manuscripts), and `version_family` is the universal *computed*
draft family, whereas this is an *observed labelled value* that spans several version families
(original and revision are one submission under two stems). Without a key, P9's shared-validated-fact
edge has no fact to share and the join degrades to retrieval similarity, which `00` never lets stand
alone.

Rejected alternatives, explicitly: overloading `version_family` (collapses a computed universal into
an observed domain value); overloading `project` (would merge every submission of one project);
minting a per-template spelling like `submission_id` (a second column for one concept — the D6
defect). It is **not** in `dimension_order` and not written into `canonical_fields.json`: a template
may only branch on fields its schema declares, and a folder per submission id is the tiny-folder
explosion `00` asks the canvas to warn about. R1c or Joseph decides; nothing in this node depends
on the answer.

## Neighbours considered that did NOT get an edge

- **`academic` / `research` / `code` / `college_applications` (schemas).** `collides_with` joins
  same-kind pairs and `also_holds_with` joins schemas only, so a template row cannot carry either
  against a schema. The roster's `must_consider_neighbors: ["academic"]` was honoured by colliding
  with **`academic.coursework`**, the template on that schema where the confusion actually lives (a
  term paper written in journal form). Where CONNECTION's kind rules and the dispatch prompt's
  "prefer `must_consider_neighbors`" pulled apart, CONNECTION won, as instructed.
- **`legal.personal-legal-matters`.** Genuinely tempting: `Signed_License_to_Publish_nmeth.pdf` is
  a signed agreement with a signature block, which is that template's core shape. No edge, because
  the discriminator is not subtle — the agreement's *subject* is a named manuscript at a named
  venue, and that evidence is present on the face of the document. An edge here would be asserting
  a confusion the evidence does not actually produce. Recorded as a `must_not_conclude` on the file
  example instead, which is where it belongs.
- **`research.grants-funding`.** A cover letter to a programme officer and a cover letter to an
  editor share a genre. No edge: sponsor/budget/deadline evidence and editorial/manuscript-id
  evidence do not overlap on any single item, so there is nothing for an evidence-item mutex to
  arbitrate.
- **`research.lab-notebook-protocols`, `research.dataset-analysis`, `research.ethics-compliance`.**
  Same project, same neighbourhood, but the items that support them (bench structure, sample-shaped
  columns, consent/IRB slots) support this template not at all. No edge.
- **`photos.screenshot-captures`.** `IMG_5512.png` looks like its material. No edge authored here:
  the discriminator is entirely inside the OCR text, and `00`'s screenshot rule is already carried
  as a `never_alone`. If R1c wants the pair, it should be authored from the photos side where the
  `media_type` fact lives.

`also_holds_with` is empty **by contract, not by omission** — the note in the JSON says so, and
names where the two real co-activations (research + college_applications, research + code) are
already carried: on the Research schema row. `role_split` is empty for the same reason — splits live
in the canonical field list, and the `venue ↔ lab` split is already recorded on the schema row.
`parent_id` is null and was never a candidate: R1b does not author it (PR-5).

## Things this node deliberately does not do

- No folder path is written as a fact anywhere; `dimension_order` is a recommendation the user may
  reverse, remove, add to or flatten, and the JSON says so in `00`'s own words.
- No number, no threshold, no confidence score, no handling class.
- No child node per lifecycle step. Cover letter, referee report, response, proof and camera-ready
  are values of `artifact_type`; submitted / under review / revision / accepted / in proof are
  values of `stage`.
- Activation ≠ grouping is stated three times where it bites: `Response to Reviewers.docx`,
  `Fig2_revised.tif` and `Proof_marked_scan.pdf` all carry
  `group_without_copying_facts: true` — they join the manuscript neighbourhood and acquire no
  project or venue fact from it.

## NEEDS-JOSEPH (this node only)

**Should `venue` be a folder level in this situation, or metadata only?** This node recommends
`project → venue → stage`. The case for venue: a rejected-then-resubmitted manuscript otherwise
interleaves two submissions' stages, and "Response to Reviewers" is unintelligible without knowing
whose reviewers. The case against: for a researcher whose manuscripts each go to exactly one
journal, venue is a one-child level — the thing `00` asks the canvas to warn about — and plenty of
people keep the venue in the filename and file by manuscript. The fork decides someone's real
folder structure, so it is not resolved here: does the recommendation ship with venue included and
let the canvas offer flattening, or ship flat (`project → stage`) and offer venue as an optional
split once a second venue appears for the same version family?

Secondary, and smaller: whether `manuscript_id` is adopted as a canonical search/grouping key (above).

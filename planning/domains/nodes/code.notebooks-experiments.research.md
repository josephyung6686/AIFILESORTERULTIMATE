# code.notebooks-experiments — lab notes

Roster row: `kind: template`, `schema_id: code`, `launch: placeholder`, `provenance: inference`.
Verdict: **not refused.** Reasoning below, because this row came close.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every span in quote marks in the
  node JSON was `grep -cF`'d against this file before it was written; all returned 1.
- `planning/01-product-design-structured.md` — §2.4 (text-bearing and structured files, the
  notebook-metadata sentence) and §2.9's code/notebook extractor bullet only, plus §5's launch
  scope line. `00` is the authority; 01 was used only to locate.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (nothing in the eight
  worked joins touches code).
- `planning/domains/roster.json` — confirmed id, kind, `schema_id: code`, the four sibling code
  templates, and the research template ids used as edge targets.
- `planning/domains/canonical_fields.json` — `project`, `repository`, `programming_language`,
  `artifact_type`; `programming_language.destination_eligible = false` is why it is absent from
  `dimension_order`.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; every `file_examples.source_type` is a
  member.
- Neighbour node files that had already landed: `nodes/code.json` (the schema),
  `nodes/research.json`, `nodes/research.dataset-analysis.json`,
  `nodes/research.project-workspace.json`. Their edges were read and aligned to, not rewritten.

## The node test — why this row survived it

The test: a template exists only if its detection signals, recommended dimensions, or privacy
rules differ from the schema's default. `research.project-workspace` refused itself on exactly
this ground, so the bar was taken seriously.

- **Detection signals differ.** The Code schema's anchoring rule is a project-root marker file at
  a real root (`00`'s four named examples). This situation is defined by that marker being absent.
  The row therefore authors a rule family the schema does not have: the **run-directory layout** —
  a labelled config + an append-only metrics log + a checkpoint-shaped binary as immediate
  siblings, repeated across sibling directories — plus an on-disk **lineage link** (a notebook cell
  naming a sibling file that exists). Both are structural in `00`'s sense and neither is on the
  schema row.
- **Dimension order differs, and not merely by flattening.** `repository` is absent by definition
  of the situation, not for lack of files, and `artifact_type` — which the schema row itself calls
  the optional deepest level, "normally flattened away" when a root is preserved — is here the only
  level that separates a checkpoint from its training data. The `template.why` states this
  explicitly so a merge pass can check the claim rather than take it.
- **Privacy rule differs.** A `.ipynb` stores its outputs inside the file: printed data rows, a
  rendered figure, a traceback with local paths. The Code schema's sensitivity note is about
  credentials in configuration files; this one is about a code-shaped file whose body carries
  somebody else's data, which changes what a dossier may excerpt. That is the difference that made
  the row worth writing rather than the dimension order alone.

Had only the dimension order differed, this would have been a refusal.

## Files considered and rejected

- **`requirements.txt` / `environment.yml` on their own** — a package manifest is the schema's
  anchor and `code.software-project`'s signal. Kept out of the examples so this row does not claim
  the marker it is defined by not having; it appears only inside the software-project collision.
- **`.py` files generally** — covered by the schema and by `code.scratch-prototypes`. The one `.py`
  example here (`analysis/model_fit.py`) is present purely as the collision fixture.
- **A Colab share link / `.url` file** — the interesting fact would be a remote URL, and a URL in a
  file is a citation, not a repository marker. It added nothing the notification `.eml` did not.
- **A `sweep.yaml`** — same evidence shape as `config.yaml`; a second example of one rule family is
  padding.
- **`.vcf` / contacts** — this situation never sees them; `00` puts contact data on the
  privacy-protected side regardless.
- **A wearable-device CSV** — a genuine near-miss for the dataset example, but
  `research.dataset-analysis` already owns that collision with `medical.wearable-health-exports`
  and wrote the discriminator. Duplicating it here would add an edge without adding a signal.

## proposed_fields — deliberately empty

The honest gap is a **run identifier**. It is not `project` (one project has many runs), not
`artifact_type` (that is the kind, not the instance), not `version_family` (differing
hyperparameters are not drafts of one document), and not `event` (photos' key). No canonical key
fits.

It is still not proposed, because a template minting a field is precisely how a tree level appears
that no fact can ever fill — the failure `_CONTRACT.md` rule 8 records at scale ("566 of 1,648
dimensions branch on a field the schema does not declare"), and fields are R1a's global table, not
a template's. Whether a run is a fifth Code field, a value inside `artifact_type`, or a P9 group
with no folder level at all is a decision about what the domain legitimises, so it went to
`open_question` instead. The cost of leaving it out is written into the open question rather than
hidden: fifty runs of one project collapse into one `checkpoints` level.

## Edges

Authored: `collides_with` → `code.software-project`, `research.dataset-analysis`,
`code.scratch-prototypes`, `research.lab-notebook-protocols`. All four are template↔template, which
is what `CONNECTION.md` §5 allows for this kind. `research.dataset-analysis` had already authored a
collision at this id; its signal was read and reciprocated using the fixture it named
(`clean_and_merge.ipynb`), so the pair agrees rather than contradicting.

**`also_holds_with` is empty, and that is not an omission.** The roster hint for this row calls it
"the strongest also_holds candidate with research" — but `CONNECTION.md` §5 restricts
`also_holds_with` to **schema ↔ schema**, and `code ↔ research` is already authored on
`nodes/code.json`. Every landed template node in `nodes/` carries the key empty; this one matches.
The per-file two-schema cases are recorded where a template legitimately can record them, on
`file_examples[].also_schema`: `participants_raw.csv → medical`, `clean_and_merge.ipynb →
research`. **Where the dispatch prompt's edge table and CONNECTION.md disagree on this, CONNECTION
wins** (prompt's own instruction), and this note is the record of that.

`falls_through_to`: Review Later (roster's required residual, `design`), Unsupported or Encrypted
(`design` — checkpoints are `00`'s unknown-binary class), Reading Inbox (`inference` — `00` names
papers and PDFs there, not notebooks), Protected Records (`inference` — a participant dataset with
no project).

`parent_id` is null and was never authored (PR-5: R1b never authors it). `shares_field` was never
authored (derived only). `role_split` is empty — this situation has no same-entity role pair.

## Neighbours considered that did not get an edge

- **`research` and `code` (the schemas)** — a template may not carry `also_holds_with`, and
  `collides_with` joins same-kind pairs only. The schema-level code↔research collision and
  also-holds are already on `nodes/code.json` and `nodes/research.json`.
- **`code.dotfiles-environment`** — an `environment.yml` or a pinned lockfile beside a notebook is
  a real overlap, but the discriminator that row is built on is credential-bearing configuration,
  which is not what a run config is. A collision edge would have carried no discriminating signal
  the two rows do not already state separately.
- **`code.pkm-vault`** — markdown vaults and notebook markdown cells share a format and nothing
  else; a vault marker is a structural signal that never appears in this situation.
- **`medical.wearable-health-exports` and `finance.small-business-bookkeeping`** — reachable
  through the dataset example, but `research.dataset-analysis` authored both collisions with the
  same discriminator (what anchors the table). Recorded here rather than duplicated as edges.
- **`career.portfolio-work-samples`** — a notebook shown as a work sample is a real case, but the
  recruiting evidence is disjoint and career writes no field rows (PR-6); the schema row already
  carries `code ↔ career` also-holds.
- **Temporary Screenshots** — the loss-curve screenshot falls through there, but the fallthrough
  belongs to the capture side, not to this template. Recorded on the file example only, matching
  `nodes/code.json`'s treatment of the same case.

## NEEDS-JOSEPH (this node only)

- **NJ-code-run — is an experiment run a folder level?** Copied from the node's `open_question`.
  A run identifier has no canonical key; a run is the unit this situation is actually organized
  by; and the three defensible answers (a fifth Code field, a value inside `artifact_type`, or a
  P9-group-only concept with no folder level) each imply a different `dimension_order` for this
  row. Left open rather than resolved, because it decides what the Code domain legitimises, and
  because the alternative — minting the field here — is the catalogue's recorded failure mode.
  It interacts with the open question already on `nodes/code.json` (whether a Code template may
  ever propose levels inside a preserved project): both are the same underlying question of
  whether Code's folder half is about roots or about artifacts.

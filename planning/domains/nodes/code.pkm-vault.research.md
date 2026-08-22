# code.pkm-vault — lab notes (R1b)

Date: 2026-08-22
Roster row: `code.pkm-vault`, `kind: template`, `schema_id: code`, `launch: placeholder`, provenance `proposal`.
Verdict: **not refused.** The node test passes on two of its three limbs outright (detection
signals, privacy rules) and the third (recommended dimensions) differs for a reason that belongs to
this situation rather than to the schema.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full; every quoted span in the node JSON
  was `grep -F` verified against this file before it was written. No section numbers are asserted
  of `00`.
- `planning/01-product-design-structured.md` — §1.1 (corpus selection and the exclusion list) and
  §2.4 (text-bearing and structured files) only, as locators for the two `00` paragraphs this node
  leans on hardest. `00` wins on any conflict; there was none.
- `planning/domains/_CONTRACT.md`, `planning/prompts/ALIGNMENT.md`,
  `planning/domains/CONNECTION.md`, `planning/domains/CONNECTION-EXAMPLES.md` (skimmed for fixture
  shape).
- `planning/domains/roster.json` — confirmed id, kind, `schema_id: code`, neighbour `research`,
  residual `Review Later`, and the four sibling `code.*` templates.
- `planning/domains/canonical_fields.json` — every field key referenced resolves here; nothing was
  minted.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked member by member against every
  `file_examples.source_type`.
- Neighbour node files already landed: `code.json` (the schema), `code.software-project.json`
  (refused), `code.notebooks-experiments.json`, `research.lab-notebook-protocols.json`,
  `research.reading-library.json`. Edges were aligned to them; none was rewritten.

## Why this is a node and not a label

`code.software-project` was refused because its signals, dimensions and privacy posture were the
Code schema's own. This row is the opposite case on all three:

1. **Detection signals are not the schema's.** `code.json`'s deterministic list is entirely
   project-root markers, manifest slots, source-layout archive manifests and notebook metadata. A
   vault has none of them. Its marker set is an application settings directory at a root
   (`.obsidian/app.json`, `logseq/config.edn`, `dendron.yml`), a *resolved* wiki-link and embed
   graph across sibling notes, or — for a Notion export — a hex-token filename paired with `.csv`
   sidecars and a same-named attachment directory. Sharper still: `code.json` files loose markdown
   under **`needs_llm`** ("a markdown file that could be project documentation, a personal note, or
   a saved article"). This node converts part of that LLM question into a deterministic structural
   test, which is exactly the kind of difference a template row is for.
2. **Privacy rules differ.** The schema's privacy case is a credential slot in a config file
   (`.env`, an "authentication key"). This node's case is that a vault is thousands of small,
   readable, personal prose files, so the binding rule is a *prompt* rule — `00`'s "complete
   extracted text" must "remain local" and the engine "should not send full documents where a short
   heading or OCR excerpt is enough to resolve the question". Same schema, different failure mode.
3. **Dimensions differ, and the narrowing is reasoned.** One dimension, `project`. `repository` is
   normally undeclarable here (no manifest slot; `.git` is on `00`'s ignore list), and
   `artifact_type` would open a level *inside* a structure `00` asks to preserve, breaking the
   embed and wiki-link references that resolve by sibling position. That is a situation-specific
   argument, not the "schema default with the last level flattened" that got the sibling refused.

The load-bearing gap: `00`'s exclusion rule protects project interiors via four *named* software
markers. A vault matches none of them, so without this node its notes read as loose personal
documents and get scattered individually into Reading Inbox / One-Off Images / Review Later — the
`attachments/Pasted image ...png` fixture is that failure in one file.

## Files considered and rejected

- **`.gitignore`, `LICENSE`, `CHANGELOG.md` at a vault root.** Real, but they carry no vault-specific
  evidence and no vault-specific restraint; they are the schema's markdown/config story.
- **`workspace.json` and plugin data inside `.obsidian/`.** Kept only as a *must_not_conclude* on the
  marker fixture rather than as its own example: they are app state beside the corpus, and whether
  they are excluded the way `00` excludes "caches, auto-save folders, previews" is a scan-side
  question recorded in `open_question`, not this node's to settle.
- **A Roam/Logseq EDN journal file.** Would have duplicated the daily-note fixture with a different
  extension; extensions are `SOURCE_TYPES` and values, never nodes.
- **A `.vcf` or `.ics` exported from a notes app.** Rejected on `CONNECTION.md`'s own worked
  examples: a format is not a domain, and contact data "should normally be privacy-protected rather
  than used to create folder proposals".
- **An Evernote `.enex` export.** Genuinely this situation, but it is a single opaque XML container
  rather than a corpus of files; it would have argued for an extractor, not for a folder situation.
- **A Notion `.csv` database export on its own, in Downloads.** Rejected as a fixture because with
  no paired markdown and no sibling directory it is `00`'s "spreadsheet with unclear purpose" —
  residual, not this node.

## proposed_fields

**None.** Two candidates were considered and both were rejected:

- `note_type` — refused. Its members (note, daily note, literature note, attachment, canvas,
  template) are *values* of the existing `artifact_type` enum. `00`: "The system may create new
  values when it sees a new course, project, company, university, or event, but it should not
  invent new fields automatically." Minting it would be the 574's exact failure at one row.
- `tag` — refused. Frontmatter tags are real, labelled, and extractable, but a tag is a
  user-vocabulary value with no destination role here, and grouping on a hub tag is what `00`'s stop
  rules exclude ("when one high-frequency entity acts as the only bridge").

The honest finding instead, recorded in `open_question` (3): the Code schema fits this situation
only partly — `programming_language` never fires and `repository` is normally absent. That is a
question for R1c about how thin a schema reuse may be, not a licence to mint one.

## Edges — and where the prompt and CONNECTION disagreed

The dispatch prompt lists `also_holds_with` as available to this row. **CONNECTION.md §5 restricts
`also_holds_with` to schema ↔ schema, and `_CONTRACT.md` rule 14 repeats it**, so CONNECTION wins
and `also_holds_with` is left empty here. The co-holding relationships this research did find are
recorded as `also_schema` on the fixtures instead:

- **medical** (`Health/Bloodwork 2026-03.md`) — a vault member that is a health record. `code.json`
  currently declares `also_holds_with` research, career and identity, but **not medical**. That is a
  finding for R1c against the *schema* row; this template did not author it.
- **academic** (`PHYS1401 lecture 8 notes.md`) — disjoint evidence (vault marker vs course-code +
  context terms), so co-holding rather than collision. `code.software-project`'s refusal already
  flagged a missing code↔academic edge on the schema row from the other direction; this is a second
  witness for the same R1c fix.

`collides_with` (template ↔ template, same kind, per CONNECTION §5): `code.scratch-prototypes`,
`research.lab-notebook-protocols`, `research.reading-library`. Each carries a discriminating
`signal`; all three are roster ids; reciprocity is R1c's.

`falls_through_to`: Review Later, Reading Inbox, Unsupported or Encrypted — each backed by a
fixture. Note that two fixtures fall through to **One-Off Images** and one to **Protected Records**
without those becoming edges: like `code.json`'s screenshot case, those fallthroughs belong to the
capture and safety sides, not to this node.

`parent_id`: not authored. PR-5 — R1b never authors it.
`role_split`: none; no near-duplicate field role appears in this situation.
`shares_field`: never authored (derived).

## Neighbours considered that did NOT get an edge

- **`research` (the schema, and the roster's `must_consider_neighbors` entry)** — a schema cannot be
  a collision partner of a template under CONNECTION §5 (`collides_with` joins same-kind pairs), so
  the neighbour was honoured by colliding with its two *templates* whose evidence actually overlaps
  (`research.lab-notebook-protocols`, `research.reading-library`) rather than by an illegal edge.
- **`research.project-workspace`** — plausible (a project folder of notes), but the discriminator is
  the same vault-marker test already stated against `lab-notebook-protocols`; a third near-identical
  signal would be padding.
- **`code.notebooks-experiments`** — a vault can hold a notebook, but the two situations are told
  apart by their own markers with no shared tempting item, and it already collides with
  `code.software-project`. Left unedged deliberately.
- **`academic.coursework`** — the `PHYS1401` fixture is co-holding on disjoint evidence, not an
  evidence-item mutex, so a collision edge would misdescribe it (and would be schema→template,
  which is illegal anyway).
- **`code.dotfiles-environment`** — the settings directory at a vault root is application config,
  which reads adjacent; no edge, because that node's situation is credential-bearing shell and
  editor configuration, and a vault marker carries no credentials.
- **`photos.screenshot-captures`** — the pasted-image and photographed-note fixtures brush against
  it, but the resolution in both is the never-alone EXIF rule, not a mutex between templates.

## NEEDS-JOSEPH (this node only)

- **NJ-pkm-1 · Is a detected vault atomic?** May a template ever propose folder levels *inside* a
  preserved vault, or is the root relocatable only whole? This node recommends `["project"]` on the
  preservation reading. It is the same fork `code.json` already files for repository roots and
  should be answered once, for both. `_CONTRACT.md` rule 7 forbids this row resolving it.
- **NJ-pkm-2 · Are application settings directories excluded from organization?** `00`'s ignore list
  is written for software projects and names no app settings directory. `.obsidian/` and `logseq/`
  hold workspace state and plugin caches that are not user destinations, but they are also the
  marker that makes this node work — so they must be *readable as evidence* while being *ineligible
  as destinations*. That distinction does not exist in `00` and is R2/P3's to build once Joseph
  confirms it.
- **NJ-pkm-3 · Is the Code schema the right home?** `project` = the vault, `repository` normally
  absent, `programming_language` never fires. The roster's assignment is followed here because
  minting a schema is the named failure mode, but R1c should record whether a two-of-four field fit
  is the thinnest reuse the roster will accept.

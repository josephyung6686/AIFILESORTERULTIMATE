# R1b lab notes — `code.software-project` (REFUSED)

Roster row: `kind: template`, `schema_id: code`, `launch: full`, `provenance: design`,
`file_kind_owner: [code_structured, filesystem, archive]`.
Verdict: **refuse_node: true.** The row is the Code schema's default template wearing a template id.

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Authority. Every quoted span in
  the node JSON was `grep -F`'d against this file before it was written; the two non-`00`
  quotations are attributed in place (ALIGNMENT.md's node-test sentence, CONNECTION.md's
  `destination_dimensions` row) and were matched the same way.
- `planning/prompts/ALIGNMENT.md` — the node-test sentence that decides this row.
- `planning/domains/CONNECTION.md` — sections 2 (node test), 5 (closed edge vocabulary,
  `file_kind_plausible` on schema rows), 8 (`destination_dimensions` resolves a schema id through
  the schema's default template).
- `planning/domains/_CONTRACT.md` — entry shape; rules 7 (do not resolve Joseph's question),
  8 (snake_case, template branches only on declared fields), 11–14 (R0 delta).
- `planning/domains/roster.json` — my row, the code schema row, and the four sibling code
  templates.
- `planning/domains/canonical_fields.json` — `project`, `repository`, `programming_language`,
  `artifact_type` and the universals. No new key was needed, so `proposed_fields` is empty.
- `planning/domains/nodes/code.json` — the schema row. **This is the decisive read.**
- `planning/domains/nodes/research.project-workspace.json` — the swarm's existing precedent for
  refusing a schema's default situation; and `academic.coursework.json`, the counter-precedent.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`; all thirteen fixtures validate against it.
- `planning/01-product-design-structured.md` — heading map only, to confirm which numbered
  sections cover this area (§1.1 roots and exclusions, §2.4 structured text, §2.5 archives,
  §3.11 domain-scoped schemas, §3.15 launch scope, §5.4/§5.7 templates, §7.3 residual library).
  Nothing was quoted from it; `00` wins and `00` carries all of it.

## Why refused — the three limbs, briefly

`code.json` was already authored and it is thorough. It carries:

- `dimension_order: [project, repository, artifact_type]` with the parent-context reasoning;
- deterministic signals that are *entirely* project-root markers, manifest slots, source-layout
  archive manifests and parent-folder repo markers;
- the exclusion rule (`node_modules` … dependency descendants) as a `never_alone`;
- `.env` / credentials as its `sensitivity_why`;
- fixtures for the root manifest, the `node_modules` false positive, README, the source archive,
  the take-home archive, `.env`, the stack-trace screenshot.

A "software project" template can add none of that, because a repository-rooted project **is** how
`00` makes the Code domain plausible. The four roster siblings take every *un*rooted situation
(`code.scratch-prototypes`, `code.notebooks-experiments`, `code.dotfiles-environment`,
`code.pkm-vault`), so this id is defined by complement: *the schema fired and no sibling's shape
dominates.* That is CONNECTION.md section 8's schema-id resolution path, not a node.

The one dimension change available — drop `artifact_type` so a preserved root is atomic — is the
question `code.json` already files as its `open_question`. `_CONTRACT` rule 7 says not to resolve
Joseph's question; minting a row whose only distinguishing content is an answer to it would do
exactly that.

## Files considered and rejected

Thirteen fixtures are in the JSON. What each one proved:

| File | Why it did not rescue the row |
|---|---|
| `AIKonic Project/config.json` | **New fixture.** `00` names this folder by name as the case not to touch. It sharpens a preservation rule that binds *every* template on the schema — schema-row content. |
| `MyApp.xcodeproj` | **New fixture.** Bundle atomicity is `00`'s filesystem-safety rule ("avoid moving package bundles unless explicitly approved"), a P3/P8 mutation constraint, not a folder-shape difference. |
| `requirements.txt` at a root | A poorer marker than `package.json` (no repository slot). A per-marker extraction nuance for R2/R6. |
| `src/cli/query.ts` | The file that most tempts a rooted template into inventing interior levels. Restraint is the schema's open question. |
| `dist/bundle.min.js` | Excluded from organization by `00`'s named directory list; `falls_through_if_inactive: null`, like `node_modules`. |
| `node_modules/left-pad/package.json` | Already fixture 2 on `code.json`. |
| `graphify-main.zip` | Already fixture 5 on `code.json`, with `00`'s source-code-archive sentence attached. |
| `PHYS1401_hw3.py` | Real neighbour collision (academic), but it is a **missing edge on the schema row**, recorded as open_question (1). |
| `Untitled.ipynb`, `utils.py` | Already `code.json` fixtures; also the roster's notebooks / scratch siblings. |
| `.env` | Already `code.json` fixture 7; sharper rule belongs to `code.dotfiles-environment`. |
| `acme_takehome_submission.zip` | Already `code.json` fixture 6 (the `career` also-holds case). |
| `IMG_5512.png` stack trace | Already `code.json` fixture 11; the fallthrough belongs to the capture side. |

Also considered and dropped before writing: `.git/config` (inside an excluded directory, same
finding as `node_modules` with nothing added), `pnpm-lock.yaml` (a value of `artifact_type`, not a
fixture), `LICENSE` (zero own-evidence root file, subsumed by `src/cli/query.ts`'s point),
`.zshrc` and an Obsidian vault marker (owned outright by named siblings; including them would have
been claiming a sibling's material to bulk out a refused row).

`utils.py`, `Untitled.ipynb`, `IMG_5512.png` and `PHYS1401_hw3.py` carry
`group_without_copying_facts: true` where relevant — the `HW 3` discipline: P9 may attach them to
a project neighbourhood without any `project` fact being written.

## proposed_fields justification

None. The four inherited keys (`project`, `repository`, `programming_language`, `artifact_type`)
cover every fact in every fixture, and a refused row must not mint keys. `programming_language`
stays `destination_eligible: false` from its canonical row; nothing here widens it (a field's
eligibility is never widened by a schema, CONNECTION.md section 6).

## Neighbours considered that got no edge

All edge arrays are empty because a refused row must not author edges. What I found while looking,
recorded here and in `open_question` for R1c:

- **`academic`** — a coursework programming assignment (`PHYS1401_hw3.py`) is a genuine
  evidence-item collision with this schema. `code.json` declares `collides_with: research` only.
  The missing pair is `code ↔ academic`, and the discriminating signal is `00`'s course-code-plus-
  academic-context rule against the structural-marker rule. **This belongs on `code.json`, not
  here.** Flagged, not authored.
- **`research`** — already carried on `code.json` as both `collides_with` (shared `project` /
  `artifact_type`) and `also_holds_with` (analysis code of a study). Reciprocity with
  `research.json` is R1c's check.
- **`career`** — already on `code.json` (take-home / portfolio). Career writes no field rows
  today (PR-6), so it records co-activation only.
- **`identity`** — already on `code.json` (`.env`, credentials).
- **`photos`** — not an edge. The stack-trace screenshot falls through to Temporary Screenshots on
  the *capture* side; `code.json` correctly declines the residual.
- **Residuals** — Review Later and Unsupported or Encrypted are already `code.json`'s
  `falls_through_to`, matching my roster row's `must_consider_residuals`. No gap found (unlike the
  research schema, where `research.project-workspace` reported one).

## Contract notes

- The dispatch prompt's output shape uses `schema_id`; `_CONTRACT` rule 12 names the edge
  `uses_schema` on template entries. I followed the prompt and the existing node files
  (all 45 use `schema_id`), so R1c renames uniformly at merge. Flagging rather than diverging.
- No disagreement found between CONNECTION.md and the dispatch prompt for this node. CONNECTION's
  "if present" clauses were treated as present and binding, per the orchestrator.
- D6/D2 as ratified: snake_case keys throughout; no `course` key anywhere (not applicable to this
  domain in any case).
- No numeric thresholds, no confidence scores, no handling classes. `sensitivity` is
  `potentially_sensitive`, which is `00`'s phrase and nothing more.

## NEEDS-JOSEPH (this node only)

1. **Is a repository root atomic?** May a Code template ever propose folder levels *inside* a
   preserved project, or is a root relocatable only whole? `00` says existing folder structures
   "should mainly be preserved" and rejects descendants of project roots as destinations, yet the
   Code domain also carries a three-deep template. This is already `code.json`'s open question and
   I am **not** answering it. Three fixtures here (`src/cli/query.ts`, `MyApp.xcodeproj`,
   `AIKonic Project/config.json`) are evidence that the answer is a schema-wide preservation
   constraint rather than a distinguishing feature of a rooted-project template — which is part of
   why this row refuses.
2. **`file_kind_owner` semantics.** The roster gives this refused id ownership of
   `code_structured`, `filesystem` and `archive`. CONNECTION.md section 5 puts `file_kind_plausible`
   on **schema** rows, and `code.json` already carries all three. If a later reviewer reads
   `file_kind_owner` as exclusive, this refusal would look like it orphans three source types when
   it does not. R1c should settle whether `file_kind_owner` means exclusivity or primary interest.
3. **Missing `code ↔ academic` collision** on the schema row (see above). A schema-row repair for
   R1c, surfaced here because this node's fixture found it.

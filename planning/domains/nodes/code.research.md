# `code` — R1b lab notes (kind: schema)

Date: 2026-08-22 · Roster row: `code` / `kind: schema` / `launch: full` / `provenance: design`
Output: [`code.json`](code.json)

---

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Authority. Every quoted span in
  `code.json` was `grep -F`-verified against this file **before** it was written; 22 spans checked,
  22 matched.
- `planning/01-product-design-structured.md` — read only §2.4 (text-bearing and structured files),
  §2.5 (archives), §3.11–§3.15 (domain-scoped schemas, reliability states, launch scope). `00` wins
  on any conflict; none arose — 01's §3.11 table is a rendering of `00`'s one-sentence list.
- `planning/domains/_CONTRACT.md` — entry shape, rules 1–15.
- `planning/prompts/ALIGNMENT.md` — the "domain = schema or template" reading; work types are values.
- `planning/domains/CONNECTION.md` + `CONNECTION-EXAMPLES.md` — both present and binding. Closed edge
  vocabulary; activation ≠ grouping; `parent_id` browse-only and never authored here; `shares_field`
  derived, never authored.
- `planning/domains/roster.json` — confirmed `code` is `kind: schema`, `schema_id: code`,
  `launch: full`, neighbours `research` + `career`, residuals Review Later + Unsupported or
  Encrypted, five `kind: template` rows point at this schema.
- `planning/domains/canonical_fields.json` — all four fields resolve; no synonyms minted.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` (fourteen) checked mechanically against every
  `file_examples[].source_type` and every `file_kinds.source_types` member.

D6/D2 ratified state followed as recorded (snake_case keys; the academic key is `subject` — not
referenced by this schema, but it is the reason no `course`-shaped spelling appears anywhere here).

## Node test — passed, not padded

`code` survives as a schema because its field set is **genuinely distinct**, not a respelling:

- `repository` and `programming_language` exist in no other schema.
- `project` and `artifact_type` are shared with `research` — that is `shares_field` (derived), and
  it is precisely why `collides_with: research` is authored with a discriminating signal.
- The remainder of `research` (`stage`, `lab`, `venue`) is absent here, and the remainder of `code`
  is absent there. Neither is a subset of the other.

`00` also names the domain outright — "Code files may use project, repository, programming language,
and artifact type" — and puts "code projects" in the launch list, so `provenance: design` and
`launch: full` are the roster's, not an inflation of it.

Four fields, not six. `00` sizes a schema at "usually three to six that may help build a future
folder proposal and several additional fields used only for search, privacy protection, explanation,
or later review". The four `00` names are enough; I added no fifth to reach a target. Sensitivity and
version/duplicate family are **universal** fields and are already in the allow-list union
(CONNECTION §3) — re-declaring them on this schema would have been padding.

## `proposed_fields` — empty, and why

Three candidates were considered and rejected:

| Candidate | Rejected because |
|---|---|
| a `secret_present` / credential flag | that is the universal `sensitivity_status` plus P7's handling class. Minting a code-local flag would put P7's vocabulary on a catalogue row (`_CONTRACT` rule 5). |
| `repo_owner` / `organization` | authorship-side identity. `00`: "It should avoid using authorship or creator identity as a destination dimension" — and `authored_by` already exists canonically, unreferenced here because this schema needs no author facet. |
| `build_status` / `runtime` / `framework` | values of `artifact_type` and `programming_language`, or nothing. Minting them would be the 574's failure at one-node scale. |

## Files considered and rejected as examples

- **`.gitignore`, `LICENSE`, `CHANGELOG.md`** — real, but they add nothing the `README.md` and
  manifest fixtures do not already test.
- **`Dockerfile` / `docker-compose.yml`** — same detection shape as the manifest fixture; one more
  happy case, no new failure mode.
- **A `.sql` dump** — genuinely ambiguous (data export vs schema migration), but the discrimination
  is the same one `.json`/`.csv` already carries in `never_alone`, so it earned a `never_alone`
  clause rather than a thirteenth example.
- **A `.vcf` / an email thread** — `00` sends contacts to privacy protection rather than folder
  proposals, and mail is a `SOURCE_TYPE` this domain has no distinct read on. `standup.ics` was kept
  instead because it is the sharper fixture: a calendar entry naming a repository is the
  repository-name-alone case, and it is the direct analogue of CONNECTION-EXAMPLES §5.

## Neighbours considered that did NOT get an edge

- **`photos`** — a screenshot of a stack trace (`IMG_5512.png`) touches both. No edge: the image
  yields nothing for this schema on its own, the discrimination is `photos`' internal
  photo-vs-screenshot rule, and `code` never competes for the file. Recorded inside the file example
  instead, including the note that **Temporary Screenshots is deliberately not a
  `falls_through_to` edge on this node** — that fallthrough is owned by the capture side.
- **`college_applications`** — a code portfolio can be submitted with an application, but the
  evidence path runs through `career` or through the application packet's own purpose evidence.
  Adding it would have been an `also_holds_with` I could not fixture from a real file.
- **`academic`** — a programming-course homework repo is real, but the discriminating evidence
  (course code + academic context) is `academic`'s and `00` gives no code-specific tension. The file
  in that case simply co-activates on disjoint evidence; asserting an edge on a pair I could not
  discriminate would have been noise. **Flagged for R1c**: if `academic` authors
  `also_holds_with: code`, reciprocity will need this side added.
- **`career` collides_with** — considered and rejected. The take-home archive carries a company
  token *and* a source layout: those are **disjoint** evidence items, which is `also_holds_with`, not
  a collision. `collides_with` is per-evidence-item mutex (CONNECTION §5), and no single item here
  reads as both.

## Things this node deliberately does not do

- No `parent_id` (PR-5: R1b never authors it).
- No `shares_field` (derived-only; the `project` / `artifact_type` overlap with `research` is left
  for the merge to compute).
- No numeric threshold anywhere; margin and activation score are named as injected slots or not named.
- `programming_language` is **not** widened to destination-eligible. CONNECTION §6: "A field's
  eligibility is never widened by a schema." The canonical row already records that widening is
  Joseph's call, so I did not restate it as this node's `open_question`.
- No folder path is written as a fact in any of the twelve examples.

## NEEDS-JOSEPH (this node only)

**NJ-code-1 · Is a repository root atomic?** `00` says "The system should also know that existing
folder structures should mainly be preserved" and requires the engine to "reject descendants of
software project roots indicated by files such as package.json, requirements.txt, Cargo.toml, or
go.mod" — yet Code is a launch domain with a folder template, and a template's job is to propose
folder levels. Two readings:

- **Atomic (what `code.json` recommends):** the tree may relocate a project root whole and never
  proposes levels inside it. `artifact_type` is then a dimension only for loose code that has no
  root — scripts, standalone notebooks, snippets — and is flattened away wherever a root exists.
- **Divisible:** a Code template may propose interior levels (`src` / `docs` / `notebooks`), which
  makes `artifact_type` a first-class dimension and puts the template in tension with the
  preservation sentence.

This decides whether this schema's third dimension is real or decorative, and it propagates to all
five `kind: template` rows on this schema (`code.software-project`, `code.notebooks-experiments`,
`code.scratch-prototypes`, `code.dotfiles-environment`, `code.pkm-vault`). It is recorded verbatim in
`code.json`'s `open_question` and is not resolved here.

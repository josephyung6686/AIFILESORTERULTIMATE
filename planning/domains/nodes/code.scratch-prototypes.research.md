# code.scratch-prototypes — lab notes (R1b)

**Outcome: `refuse_node: true`.** The row names the complement of the Code schema's activation
condition. It has no detection signal of its own, no destination-eligible field it can fill, and
no privacy rule that is not already the schema's or a named sibling's. Its material's honest home
is the residual library, which `00` and CONNECTION.md deliberately keep outside the
domain-template library.

## Sources used

- `planning/00-database-agent-product-design.md` — read in full. Every span in quote marks in the
  node JSON was `grep -F` verified against this file before it was written (17 + 10 spans, two
  passes, all OK). The load-bearing ones: the structural-evidence rule for code
  ("Code-related files should rely heavily on local structural evidence…"), the excluded-descendant
  rule (`package.json, requirements.txt, Cargo.toml, or go.mod`), the extension-as-routing-signal
  rule, the residual-library paragraph (Reference Clips naming "code snippets"; Review Later for
  files "whose meaning is partly understood"), the shallow-for-isolated-files rule, and the two
  canvas warnings about one-child levels and flattening.
- `planning/domains/_CONTRACT.md` (rules 11–14, R0 delta), `planning/prompts/ALIGNMENT.md`
  (the node test sentence, quoted in `refuse_reason`), `planning/domains/CONNECTION.md`
  (sections 2, 4, 5, 7), `CONNECTION-EXAMPLES.md` (nothing binding on this id — no code fixture).
- `planning/domains/roster.json` — confirmed id, `kind: template`, `schema_id: code`,
  `launch: placeholder`, neighbours, and the four sibling code templates.
- `planning/domains/canonical_fields.json` — the four code keys plus `version_family`,
  `download_session`, `media_type`. No new key was needed, because no field was authored.
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES`. The four used in fixtures
  (`code_structured`, `archive`, `ocr`, `email`) are members.
- Landed neighbour nodes, read to align rather than rewrite: `code.json` (the schema),
  `code.software-project.json` (refused — precedent followed here), and
  `code.notebooks-experiments.json` (passed — the contrast that decided this refusal, below).

## Why this refuses where `code.notebooks-experiments` passed

The sibling passed because it found a **structural anchor that survives the absence of a
manifest**: notebook kernel/cell metadata for the artifact and language, and a run-directory
layout (labelled config + metrics log + checkpoint, repeated under one parent) as the project-root
analogue. Its recommended order `[project, artifact_type]` is therefore fillable.

This id has no such anchor. I looked hard for one and found exactly one candidate —
**sibling-import resolution**: several loose scripts in one directory whose imports resolve to each
other, no manifest above. It is genuine local structural evidence in `00`'s sense, and it is *not*
on `code.json`'s deterministic list. But it establishes only cohesion, and cohesion is P9's object
("A group does not create a schema"). To fill a dimension it would have to yield a `project`
**value**, and the only candidate value is the enclosing folder's name — the name-alone case the
schema already forbids. So the signal is a `grouping_reasons` entry owed to `code.json`, not a
template. That is finding (3) in the node's `open_question`.

The second candidate signal — a provenance comment header (`# from https://…`) on a downloaded
snippet — points *away* from a template: `00` puts that file in Reference Clips by name. Residual
accepted-evidence patterns are R3's content, and CONNECTION.md forbids a residual home acquiring
detection signals of its own inside this namespace.

## Files considered and rejected

Eleven files are in the node JSON. Considered and dropped:

- `node_modules/left-pad/package.json`, `dist/bundle.min.js` — `00` excludes these from
  organization entirely; already fixtures on `code.json` / `code.software-project.json`, and they
  test the *rooted* rule, not this one.
- `Untitled.ipynb` in Downloads — the roster gives notebooks to `code.notebooks-experiments`, which
  already carries it as `Untitled(3).ipynb`. Claiming it would be poaching a sibling's situation.
- `.zshrc`, `.env.example` — `code.dotfiles-environment`'s. I kept one credential fixture
  (`run.sh` with an inline `export …TOKEN`) only because it is the limb-3 evidence that the privacy
  rule here is the schema's, not this row's.
- `standup.ics`, a `.vcf` — calendar and contacts reach this domain only as format-plausibility,
  which is never-alone; `code.json` already carries the `.ics` case and CONNECTION-EXAMPLES carries
  the `.vcf` one. Nothing about loose code changes them.
- `backup.7z` (encrypted, source-shaped name) — already `code.json`'s Unsupported-or-Encrypted
  fixture; the unreadable case is format-driven and root-independent.
- `main.py` inside a preserved `AIKonic Project` folder — has a root above it, so by construction
  not this situation.

## `proposed_fields`

**None, deliberately.** A refused row authors no fields, and nothing here needed one: every fact
this material can carry is either a Code schema key (`project`, `repository`,
`programming_language`, `artifact_type`) or a universal (`version_family`, `download_session`,
`sensitivity_status`). The two temptations I explicitly declined to mint:

- a `snippet_source` / `origin_url` field for the downloaded-snippet header — that is a residual
  accepted-evidence pattern (R3) and a `possible`-grade observation, not a folder-shaping fact;
- a `scratch`-flavoured clone of `artifact_type` — its members are **values** of the existing enum,
  and `00`: the system "should not invent new fields automatically".

## Neighbours considered that got no edge

A refused row authors no edges (the `code.software-project` precedent), so all four lists are
empty. Recorded here so R1c does not read the emptiness as an oversight:

- **`research`** (my `must_consider_neighbors`) — the real relationship is a *schema-level* pair
  that `code.json` already authors both ways: `collides_with` on a shared project identifier in
  prose, `also_holds_with` on disjoint structural-versus-lab evidence. The unrooted variant
  (`pva_rdp_prototype.py`) changes neither, so a template-level copy would be a second stored form
  of one join.
- **`academic`** — the strongest *missing* edge I found. `pset4_solutions.py` is a real
  evidence-item collision (a `.py` file whose only anchor is `00`'s course-code-plus-context rule),
  and `code.json` declares `collides_with` research only. This is a schema-row finding for R1c;
  `code.software-project.json` reached the same conclusion independently from `PHYS1401_hw3.py`,
  which is corroboration, not duplication.
- **`identity`** — `code.json` already carries `also_holds_with identity` for credential-bearing
  files; the sharper situation is `code.dotfiles-environment`'s.
- **`code.notebooks-experiments`** — it authored `collides_with code.software-project`. I did not
  author a reciprocal or a parallel edge to it: the notebook/no-notebook line is a file-shape line
  the schema's own `never_alone` list already draws, and edges from a refused row would need
  reciprocals on rows that must not carry them.
- **Residuals `Review Later` / `Reference Clips`** (my `must_consider_residuals`) — both are real
  for this material and neither is authored here. Review Later is already on `code.json`;
  Reference Clips is missing there and is finding (1).

## NEEDS-JOSEPH (this node only)

1. **May a user-confirmed group label become a `project` value?** A folder of cross-importing
   loose scripts is a genuine unit with no admissible name. If the user accepts the group and names
   it, the label is `user_confirmed` — the strongest reliability state — yet the schema's project
   rule family (root marker + directory position) never fired. If the answer is yes, this material
   reaches the Code schema's default template through P9 + user confirmation and still needs no
   template row; if no, it stays residual permanently. Either answer keeps this row refused; the
   answer decides how much of a real corpus's loose code is reachable at all.
2. **Does `Reference Clips` belong on the Code schema row?** `00` names "code snippets" inside the
   Reference Clips sentence, so a saved snippet has a design-named home that is *not* Review Later.
   Adding the edge is a one-line change to `code.json` that I am not permitted to make from here.

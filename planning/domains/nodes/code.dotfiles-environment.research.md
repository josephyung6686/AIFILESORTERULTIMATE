# Lab notes — `code.dotfiles-environment`

Kind: `template` on `schema_id: code`. Verdict: **accepted** (`refuse_node: false`), `launch: placeholder`,
`provenance: proposal` (the roster's own provenance for this row; `00` never names a
machine-configuration situation).

## Sources actually used

- `planning/00-database-agent-product-design.md` — read in full. Every quoted span in the node JSON
  was grep-verified against this file with `grep -qF` **before** it was written, and the finished
  node was then re-checked mechanically: every quoted span it carries resolves verbatim into `00`.
  One candidate span failed the first check (a mis-remembered "The system should not force every
  branch…" — `00` says "The product should not force…") and was corrected rather than kept. No span
  was written from memory.
- `planning/domains/_CONTRACT.md` (entry shape; rules 8, 11–15).
- `planning/domains/CONNECTION.md` (node test §2; no schema inheritance §3; activation shape §4;
  the closed edge vocabulary §5; field identity §6; four objects §7).
- `planning/domains/CONNECTION-EXAMPLES.md` (fixtures 1–2 read; the observations→facts split and the
  "no folder path as a fact" rule are taken from there).
- `planning/prompts/ALIGNMENT.md`.
- `planning/domains/roster.json` — confirmed id, kind, `schema_id`, `must_consider_neighbors:
  ["identity"]`, `must_consider_residuals: ["Review Later"]`, and the ids of the four sibling
  templates used as collision endpoints.
- `planning/domains/canonical_fields.json` — every field named here resolves to it; no new key minted.
- `planning/domains/nodes/code.json` (the schema this template points at), `code.software-project.json`
  (refused; read so this row would not repeat it), `code.notebooks-experiments.json` (an accepted
  sibling; read for edge-authoring shape), `identity.json` (read to align, not rewrite).
- `src/evidence_shape/vocabulary.py` — `SOURCE_TYPES` checked mechanically against every
  `file_examples.source_type` and every member of `file_kinds.source_types`.
- `planning/01-product-design-structured.md` — **not** opened. `00` is the authority and carried every
  span this row needed; opening the rendering would have added locators, not facts.
- `planning/deferred-catalogues/` — **not** opened. Nothing here consumes a gazetteer: this template's
  signals are structural (naming convention, directory position, labelled key=value shape), not
  name-matching, so it has no legitimate call on R4's contents.

## The node test, and why this row survived it where its sibling did not

`code.software-project` refused because its detection signals, dimensions and privacy rules were the
Code schema's own. This row differs on all three, and the differences point in three different
directions rather than being three restatements of one:

1. **Detection.** The schema's anchor is a project-root marker; this situation's files are
   recognized precisely where that marker is *absent*. A signal set whose firing condition is the
   negation of the schema's own anchor is not the schema's signal set.
2. **Dimensions.** `project` — the default order's leading field — has no value to take, because a
   shell config belongs to a machine and a tool. The recommendation is one level shorter and led by
   a different field: `repository, artifact_type`.
3. **Privacy.** The schema row's stated posture is that code projects are not sensitive as a class.
   Here the credential-bearing file is the ordinary member, so protection ordering, not folder shape,
   is what the row is mostly *for* — which is also what the roster's own hint says.

Any one of the three alone would have made this a marginal row. Three independent differences made
refusing it the dishonest option.

## Files considered and rejected

- **`.DS_Store`, `.gitkeep`, a `.gitignore` inside a downloaded third-party repo.** Rejected as
  fixtures, kept as the first `never_alone` entry. They are the dot-prefix false-positive population
  and they exist to strike the dot convention as sole proof, not to be filed.
- **`~/.bash_history`, `~/.zsh_history`, `~/.viminfo`.** Tempting (dot-named, home-rooted, and
  genuinely sensitive), rejected because they are application state rather than configuration and
  because filing them would be the opposite of what `00`'s privacy posture wants. They belong to the
  same discussion as the `Library` exclusion and add nothing the `settings.json` fixture does not
  already carry.
- **`~/.aws/credentials`, `~/.npmrc` with an auth token.** Rejected as *additional* fixtures only —
  they are the same shape as `.env` and `.gitconfig` and would have padded the list without moving
  the boundary. The boundary they would test is already tested by the `id_ed25519` collision fixture.
- **`Dockerfile` at a project root.** Rejected: it is a build definition inside a preserved project,
  which the `docker-compose.yml` fixture already covers on the software-project side.
- **`.zprofile` / `.bash_profile` / `.vimrc` as separate rows.** Rejected as fixtures for the reason
  the contract gives generally: they are *values* of `artifact_type`, and one shell-config fixture
  (`.zshrc`) exercises the whole class.
- **A `crontab` export, a `launchd` plist, `/etc`-level system config.** Rejected as out of corpus:
  `00`'s scan is over user-selected sources such as Downloads, Desktop and Documents, and system-owned
  configuration is not personal material the product is asked to organize.

## `proposed_fields` — deliberately empty, and the reasoning

The dimension a person laying out real dotfiles reaches for is **which tool** a config belongs to
(`zsh/`, `nvim/`, `git/`). No canonical key names it. Three candidate keys were tested and all three
were rejected:

- `project` — wrong role. A configured tool is not a project, and using it here would put tool names
  into the same value space as software projects, which is exactly the collision the code schema's
  root test exists to prevent.
- `repository` — already used, and for the collection, not the tool.
- a **new** `tool` or `host` key — rejected. `artifact_type` already carries the distinction at a
  coarse grain (shell configuration vs editor configuration vs environment file); a `tool` key would
  be a finer-grained near-duplicate of an existing key, which is the near-duplicate-field failure the
  canonical list exists to prevent, and `00` says the system "should not invent new fields
  automatically". Recorded as `open_question` for Joseph instead of minted here.

So: `proposed_fields: []`, and `fields: []` — the template references the code schema's four keys and
copies none of them, per CONNECTION §3 rule 1.

## Neighbours considered that did *not* get an edge

- **`identity` (the schema, and this row's only `must_consider_neighbors` entry).** No edge from this
  row, and the omission is deliberate. `also_holds_with` joins **schemas only** (CONNECTION §5), and
  this row is a template; authoring it here would create a non-reciprocable edge under a template id.
  The join is real and is already authored where it belongs — `code.json` carries
  `also_holds_with: identity` with the `.env` fixture attached. What this row *could* legally take
  is a same-kind collision, and it did: `identity.credentials-passwords`. Recorded in the node as
  `also_holds_with_note` so a merger does not read the empty list as an oversight.
- **`code` (own schema).** No edge: the join is `schema_id` / `uses_schema`, which is the pointer, not
  a `collides_with`.
- **`academic`.** A `.py` coursework assignment is a genuine code-vs-academic evidence collision, but
  it is a **schema**-level collision and `code.json` is the row that owes it (its absence is already
  recorded as finding (1) in `code.software-project.json`'s `open_question`). Nothing about dotfiles
  makes it this row's, so no edge.
- **`research` / `career`.** Both are `code.json`'s authored neighbours for project-shaped and
  recruiting-shaped evidence. Neither touches machine configuration; a `.env` is not a research
  artifact and a `.zshrc` is not a recruiting document. No edge.
- **`finance`.** Considered because `identity.credentials-passwords` names it, and rejected: an API
  token in a config is not a financial record, and the shared item (an opaque identifier string) is
  too generic to be a discriminating `signal`, which would make the edge decorative.
- **`code.notebooks-experiments`.** Considered for the environment-file overlap (a `requirements.txt`
  or `environment.yml` beside a notebook) and rejected: that row's own collision with
  `code.software-project` already resolves environment files by the same root test this row uses, so
  a third edge would restate an existing boundary rather than draw a new one.

Reciprocity: all four authored collisions are one-directional today, exactly as
`code.notebooks-experiments` authored its four. R1c reconciles; per-node agents cannot write into a
neighbour's file.

## Where this row deviates from the dispatch prompt

The prompt's edge table describes `also_holds_with` as "One file may legally carry **both**
schemas", which reads as available to any row. CONNECTION §5 restricts it to schema↔schema pairs and
`_CONTRACT` rule 14 repeats the restriction. **CONNECTION wins**, per the prompt's own closing rule;
the edge is left empty here and the reason is recorded in the node.

## NEEDS-JOSEPH (this node only)

1. **Per-tool depth: values, or a field?** Is the tool a config belongs to left to `artifact_type`
   values and to user-created depth on the canvas (this row's recommendation), or does the Code
   schema owe a `tool` key? Minting one is a near-duplicate of an existing canonical key, so this row
   refused to decide it.
2. **Should this template propose destinations at all?** A dotfile is read by a tool from a fixed
   absolute location, so moving it breaks the machine. The honest default for this situation may be
   represent-and-leave-in-place. `00` licenses that posture explicitly — "a policy that tells the
   system to leave files in place" — but it says it of **residual** templates, and extending it to a
   domain template changes what a domain template is. Joseph's call, not this node's.
3. **Inherited, not re-opened:** the atomic-root question already filed as `code.json`'s
   `open_question` decides whether any Code template may open levels inside a preserved project. It
   bounds this row too — every fixture here that sits inside a project root resolves to
   "the software-project situation applies", which is only stable while that answer is pending.

# Database agent

A local-first file assistant. The filesystem stays the system of record; a local SQLite
database is the working memory. You point it at a folder. It reads the files, proposes a
destination tree, and does not move anything until you freeze that tree and apply a branch.
Undo puts the bytes back. A file it is not sure about stays where it is. Sensitive files
are held and are not sent to a cloud model.

The design this implements is
[`planning/00-database-agent-product-design.md`](planning/00-database-agent-product-design.md).
Search and the folder watcher are not part of this path.

Python 3.12. The command is `database-agent`. It runs on macOS and Linux. On Linux, Apple
Vision OCR, `.doc` via AppKit, and ImageIO metadata are absent; text, PDF, and `.docx`
still read.

## Quickstart

```bash
python3.12 -m pip install -e ".[dev,readers]"
database-agent /path/to/folder --user you --database ./plan.sqlite --accept-groups
database-agent /path/to/folder --user you --database ./plan.sqlite --freeze
database-agent /path/to/folder --user you --database ./plan.sqlite --apply BRANCH
database-agent /path/to/folder --user you --database ./plan.sqlite --undo-everything
```

`--accept-groups` writes `proposed-structure.txt` next to the database and moves nothing.
`--freeze` names each branch and the exact `--apply` line for it, and still moves nothing.
`--apply BRANCH` moves the files that branch froze. `--undo-everything` puts them back.
`--stop-after tree` stops once the outline exists.

A scan sorts with a model provider. Set the profile with `filesorter onboard`, then
`filesorter providers`, then `database-agent FOLDER --database ./plan.sqlite`. The
scan runs understanding after the rules. It does not ask whether to use a model.
Protected files stay on this computer. A folder with no provider stops and says to
set one up. `--model-dry-run` prints what would be sent and does not open a network
connection. Developers skip the pass with `--no-understand` or
`FILESORTER_SKIP_UNDERSTANDING=1`. A model cannot invent a folder or move a file
outside the frozen tree.

Score a labelled folder without moving it:

```bash
python3 -m tools.groundtruth --corpus DIR --labels labels.json --out ./score --force
```

Tests:

```bash
python3 -m pytest tests/
```

`jsonschema` is in the `dev` extra because several tests validate model-response schemas.

---

## The document

It is numbered so implementation can proceed part by part — a phase names the section it
implements (`§2.7 OCR`, `§6.10 the two-condition rule`) and that section is its acceptance
contract.

| § | What it covers |
|---|---|
| 0 | Foundations — filesystem as system of record, SQLite as working memory |
| 1 | Corpus and root selection, exclusions, the reusable extraction pass |
| 2 | Content extraction and evidence creation — PDF, DOCX, archives, images, OCR, format coverage |
| 3 | Facts, facets, and hybrid intelligence — observations vs. facts, reliability states, core tables |
| 4 | Grouping — seeds, bounded neighbourhoods, the group dossier, stop rules |
| 5 | User selection for the folder tree — horizontal pass, templates, uneven depth, freeze |
| 6 | Group-aware classification against the frozen tree — destination profiles, node-local graphs |
| 7 | Residual files — the controlled miscellaneous library and final review |
| 8 | Trust, operations, lifecycle — provenance, mutation safety, privacy, replay, budgets, plan versions |

---

## Loop (what the user sees)

```text
1. PICK        sources + destination roots; exclusions applied first
2. EXTRACT     one reusable pass per file version → evidence in SQLite
3. FACTS       observations become structured claims, each with evidence and reliability state
4. GROUP       rules anchor, graph assembles context, LLM judges coherence, validator checks
5. TREE        design branches horizontally then vertically; freeze the only legal destinations
6. CLASSIFY    retrieve legal nodes, build a node-local graph, place or abstain
7. RESIDUAL    surface what did not fit; user decides per set before any AI review
8. APPLY       plan → verify preconditions → move → verify → conditional undo
```

---

## Standing constraints

- Evidence is extracted once per content version and reused; never re-read a file per template
- Raw observations are kept separately from normalized values
- The LLM may only propose fields in the active schema, and must cite evidence or return `unknown`
- Every LLM conclusion passes a deterministic validator before it becomes active
- Word-boundary matching, positional weighting, ranked candidates with a minimum margin
- Purpose is a first-class facet, distinct from topic; authorship is metadata, not a destination
- No fuzzy date parsing
- After freeze: no invented destinations, no silent override of a direct fact
- Two-condition acceptance — minimum support **and** a margin over the next-best destination
- Correct abstention is a successful outcome
- Never overwrite on collision; undo is conditional; sensitive material stays local by default

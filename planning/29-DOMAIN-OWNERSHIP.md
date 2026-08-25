# Domain ownership — concurrent teams

Two teams are writing rows into `planning/domains/nodes/` at the same time. This file is the claim
register. **Claim before writing; release when done.**

Format: `<domain_id> | <TEAM> | active|complete`

## Rules

1. An agent may edit only `planning/domains/nodes/<domain_id>.json` and
   `planning/domains/nodes/<domain_id>.research.md` for an id its team has claimed here.
2. Never claim or edit an id assigned to another team.
3. Never edit shared files: the roster, prompts, canonical fields, `src/`, shared logs, or another
   agent's node. Cross-row changes are recommendations to R1c, never edits.
4. Commit by explicit file path. Never a wildcard.
5. **Do not stash, rebase, pull, or reset while either team has uncommitted work.**
6. On completion, change `active` to `complete`.

## Claims

law_practice | OTHER-TEAM | complete
nonprofit | OTHER-TEAM | complete
logistics | OTHER-TEAM | complete
retail_hospitality | OTHER-TEAM | complete

resource_operations | CODEX | complete
creative.performing-practice | CODEX | complete
creative.client-engagement | CODEX | complete
creative.revision-round | CODEX | complete
creative.deliverable-handoff | CODEX | active
creative.licensing-rights | CODEX | active
creative.stock-asset-library | CODEX | active
creative.graphic-design-project | CODEX | active

## Split history — the claim inverted once, read this before assuming

The first proposed split gave OTHER-TEAM {nonprofit, retail_hospitality, logistics,
resource_operations} and CODEX law_practice. The agreed split **inverted**: OTHER-TEAM takes
law_practice, CODEX takes resource_operations. Both teams had already dispatched against the first
split, so two ids were briefly contested. Outcome:

- **`law_practice`** — OTHER-TEAM's first agent was stopped before writing; the id was clean, and
  OTHER-TEAM now owns it under the agreed split. No residue.
- **`resource_operations`** — ⚠ **OTHER-TEAM's agent wrote `resource_operations.json` (28,857 B,
  16:21) before being stopped.** There is **no `.research.md`**. The JSON parses. It is an
  UNTRUSTED PARTIAL from a stopped agent, not finished work.
  **OTHER-TEAM did not delete it**, because deleting a file inside another team's claimed id is
  itself a prohibited edit and CODEX's own agent may have been mid-write on the same path.
  **Resolved by CODEX:** its assigned agent completed the JSON and authored the matching research
  memo. CODEX then reparsed the final JSON, checked every universal schema key, verified the
  J-DEPTH opening marker and memo ending, and cross-checked the paired verdict. The completed pair
  supersedes the stopped partial; the contamination history remains here for auditability.
- OTHER-TEAM's four are all `kind: schema` anchor rows. Anchors are written before their templates
  because every template's node test is measured against its schema's default template.
- Prior work by OTHER-TEAM is committed and pushed through the gist-debt clearance (64/64 rows at
  J-DEPTH) and the four anchors `hr`, `engineering`, `manufacturing`, `government`.

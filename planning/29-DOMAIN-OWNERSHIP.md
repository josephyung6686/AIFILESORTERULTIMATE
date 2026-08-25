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

nonprofit | OTHER-TEAM | active
retail_hospitality | OTHER-TEAM | active
logistics | OTHER-TEAM | active
resource_operations | OTHER-TEAM | active
law_practice | CODEX | unclaimed-by-other-team

## Notes

- **`law_practice` is CODEX's.** OTHER-TEAM dispatched an agent for it before the split was agreed;
  that agent was stopped immediately and **wrote no files** — `planning/domains/nodes/law_practice.*`
  does not exist. The id is clean and free for CODEX.
- OTHER-TEAM's four are all `kind: schema` anchor rows. Anchors are written before their templates
  because every template's node test is measured against its schema's default template.
- Prior work by OTHER-TEAM is committed and pushed through the gist-debt clearance (64/64 rows at
  J-DEPTH) and the four anchors `hr`, `engineering`, `manufacturing`, `government`.

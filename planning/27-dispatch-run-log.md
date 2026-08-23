# Dispatch run log — append-only

Companion to [`26-research-dispatch-state.md`](26-research-dispatch-state.md). Newest entry at the bottom.
Rule: append one line per completed unit of work the moment it is verified. Never rewrite history here.

---

## 2026-08-23 — session resume (Claude, batches of ~3–5, budget-constrained)

- Recomputed owed rows from `domains/roster.json` vs disk: **80/83 landed, 0 missing, 3 partial.**
  The prior state file's "22 owed" is stale — a Codex session landed 19 of them (finance tail,
  identity, medical, legal). All 83 candidate JSON files parse; no stub-sized files.
- Owed at resume: `finance.insurance-corporate`, `finance.insurance-healthcare`, `finance.crypto-assets`
  — each has an UNTRUSTED partial `.json` and no `.research.md`.
- Dispatched wave 1 (3 Opus agents, one per partial, salvage rule applied).
- Wave 1 landed and verified: `finance.insurance-healthcare`, `finance.insurance-corporate`,
  `finance.crypto-assets`. All three: JSON parses, required key set matches landed siblings exactly
  (`_note` keys are house style, used by 38 nodes), `fields: []` correct for `launch: placeholder`
  per J-IND, whitespace clean, no writes outside their own two files, no verbatim-quote violations
  found by audit. None refused. New open questions raised: NJ-fin-ins-1, NJ-IH-1..4, NJ-CRYPTO-1..3.
- **R1b is complete: 83/83 rows landed.** (3 honest `refuse_node` rows remain for R1c to adjudicate:
  `research.project-workspace`, `code.software-project`, `code.scratch-prototypes`.)
- Next: J-IND roster expansion (~20 schemas + triage of all 574 legacy ids), then the capped
  industry gist swarm, then R1c merge gate.

## J-IND roster expansion — landed and independently verified

- `roster.json` + `ROSTER.md` only; no other file touched. All 83 original rows byte-identical
  (proved by diffing against `HEAD:roster.json`), so the 83 landed node files stay keyed correctly.
- Roster: **83 → 358 rows** = 23 schemas (10 original + 13 new) + 335 templates. 275 new rows,
  of which 262 are `launch: placeholder` industry templates and 13 are new placeholder schemas.
- New schemas (13): creative, engineering, manufacturing, business_operations, hr, government,
  nonprofit, construction_property, retail_hospitality, logistics, resource_operations,
  clinical_practice, law_practice. Count was driven by the 574, not padded to hit ~20.
- **574 reconciliation verified independently, not taken on trust:** 270 became 1:1 rows, 229 folded
  into an R1a row, 34 folded into a new J-IND row, 15 dropped as values-not-nodes, 18 dropped as
  formats/SOURCE_TYPES, 8 dropped to the residual library. Sums to 574 exactly. A script confirms
  all 574 legacy ids appear individually in ROSTER.md Appendix A — **0 uncited**.
- Integrity: no duplicate `domain_id` in the 358; every template's `schema_id` resolves to a real
  schema row; `make_prompt.py --all` generates all 358 prompts successfully.
- `python3 planning/domains/check.py` → 14 files, 574 entries, 566 in-file / 0 cross-file.
  Legacy baseline UNCHANGED, as required.
- Next: the industry gist swarm over the 275 new rows, run in capped batches, verified and
  committed per batch so partial progress is never lost.

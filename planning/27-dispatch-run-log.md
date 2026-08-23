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

## Industry gist swarm — pilot (clinical_practice, 6 of its 11 rows)

- **Grouping deviation, recorded:** the plan said one agent per row (275 agents). The dominant cost
  per agent is re-reading the identical authority stack, so rows are grouped ~6-10 siblings per
  agent (~31 agents). At gist depth this also improves coherence: one agent writing six siblings
  makes them agree, where six isolated agents each guess the boundary between them.
- Pilot landed 12 files, exactly its 6 assigned rows, nothing out of scope. All JSON parses, key
  sets match landed siblings, `fields: []` correct for placeholder rows, memos 3.9-7.7KB (gist
  depth — deliberately shorter than R1b's 19-22KB, and labelled "Depth: GIST" in each memo).
- Quality spot-check passed: memos cite which legacy ids they absorbed (with Appendix A line refs),
  use a *reciprocal* fixture with `medical.json` (same bytes named on both sides of the boundary),
  reject tempting-but-wrong files with reasons, and record that the node test's third leg is
  unsatisfiable for this family (the schema declares no fields) rather than papering over it.
- One `proposed_fields` entry for R1c: `subject_of_record` on the schema. No row refused.
- **Dispatch error caught and corrected:** `clinical_practice` has 11 rows; only 6 were assigned
  because the inspection command sliced the list. Remaining 5 (pharmacy-operations,
  practice-administration, protocol-guideline, teaching-material, veterinary-practice) are queued
  into the next wave. Row counts must come from the roster, never from a truncated listing.

## Wave 1 — killed by the session limit, partial salvage

- All 5 agents died on "session limit reached" (2026-08-23 ~14:14 HKT). Wave 1 covered 39 rows
  across business_operations (3 chunks), the clinical_practice tail, and construction_property.
- **Survivors on disk (4 JSON, no memos)** — structurally complete (27 keys, none missing vs landed
  siblings) and normally sized, so treated as salvageable drafts rather than discarded:
  `business_operations`, `business_operations.it-asset-inventory`,
  `clinical_practice.pharmacy-operations`, `clinical_practice.practice-administration`.
- Lesson applied: waves are now smaller (4 agents) so a limit-kill loses less, and every wave is
  committed before the next starts. The four orphans go back out under the salvage rule
  (verify line-by-line, repair, complete, own) rather than being rewritten from scratch.

## clinical_practice complete — 11/11

- Tail of 5 landed and verified: pharmacy-operations, practice-administration, protocol-guideline,
  teaching-material, veterinary-practice. All parse, key sets match landed siblings, `fields: []`
  correct, memos 7.2-8.9KB, nothing written out of scope.
- Both salvaged drafts (pharmacy-operations, practice-administration) were verified and completed
  rather than rewritten; the tokens that produced them were not wasted.
- None refused: `veterinary-practice` was argued to stand as its own filing world rather than a
  subject value, and `practice-administration` to stand apart from `business_operations`.
- **`clinical_practice` is the first schema family finished end to end (11/11).**

## business_operations chunks A+B — 18 rows, one honest refusal

- 18/18 landed and verified: parse, key sets match siblings, `fields: []`, memos 3.8-7.8KB,
  nothing out of scope. Salvaged drafts (`business_operations`, `.it-asset-inventory`) verified
  and completed rather than rewritten.
- `proposed_fields` for R1c: `organization`, `fiscal_period` (both on the schema row).
- **`business_operations.organisational-records` REFUSED** — the first refusal of the gist swarm,
  and a well-argued one: fails all three legs of the node test (its only signal is an organisation
  name, which is constitutionally never-alone, so the row could never activate; dimensions and
  privacy rules identical to the schema default). Identified as "a residual wearing a domain's
  clothes" and routed to four residual templates (Independent Records, Review Later, Protected
  Records, Unsupported or Encrypted) with verbatim design quotes. Its own summary of the principle:
  "Keeping the id as a row to preserve coverage would be the 574's mistake: inventing a node to
  save an id."

## business_operations complete — 25/25 (second family finished)

- Chunk C (project-delivery, retrospective-postmortem, risk-register, strategy-plan,
  support-operations, user-research, vendor-management) landed while chunks A+B were being
  committed, and the commit glob swept it in **before it had been verified**.
- Process slip, recorded rather than hidden: verification was run retroactively instead of
  pre-commit. All 7 pass (parse, key sets match siblings, `fields: []`, memos 4.5-6.7KB, no
  proposed fields, none refused), so nothing needed repair — but the ordering was wrong.
  Fix for later waves: commit by explicit file list, never by wildcard, so a concurrently
  finishing agent cannot enter a commit unverified.
- None of chunk C's flagged refusal candidates were refused: `retrospective-postmortem` was argued
  to stand apart from `project-delivery`, and `user-research` apart from the landed `research.*`.

## Wave 2 attempt 1 — killed 3 minutes in, zero survivors

- All 4 agents (construction_property x3, creative x1) died on the session limit ~3 min after
  dispatch, during the authority-stack read phase. **Nothing written, nothing to salvage** — the
  cost was the wasted read, not lost work.
- Observed pattern: wave 1 (4 agents, 30 rows) ran ~4h and completed; wave 2 died immediately
  because the limit window was already nearly spent at dispatch time. Quota remaining is not
  visible from inside the session, so waves must be sized to fail cheaply.
- Adjustment: dispatch whole *families* per wave where possible, so a completed wave is a clean
  commit boundary, and keep waves at 3-4 agents.

## construction_property chunk B — 9 rows

- All 9 verified: parse, key sets match siblings, `fields: []`, memos 5.3-6.2KB, no proposed
  fields, none refused, nothing out of scope. Committed by explicit file list (the wildcard fix).
- Both seeded challenges were engaged rather than waved through. `progress-photos` was argued to
  stand on leg 1 of the node test — every other row on the schema is recognised by document
  structure, this one by capture metadata and rhythm, and "a `work_type` value cannot carry a
  different detection method; only a template can". Its discriminator against the landed
  `photos.camera-events` is repetition of place across time: a camera roll visits many places once,
  a site walk visits one place many times. `photos` is recorded as `also_schema` rather than as a
  competitor, per 00's "One file may hold facts from more than one domain without losing information."

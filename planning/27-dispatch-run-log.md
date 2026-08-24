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

## construction_property chunk A — 9 rows, second refusal

- All 9 verified pre-commit: parse, key sets match siblings, `fields: []`, memos 3.3-7.3KB,
  nothing out of scope.
- `proposed_fields` for R1c: `property`, `instruction`, `organization` (schema row); `revision`
  (drawings-revisions). Note `organization` was also proposed by `business_operations` — R1c
  should cluster these two into one decision, not two.
- **`construction_property.compliance-certificate` REFUSED** — the row flagged in dispatch as a
  likely document type. Fails dimensions (identical to the schema default) and privacy (a
  certificate names an address and an installer, exactly as every sibling does, already covered by
  the schema's `potentially_sensitive`), and its detection leg does not survive inspection.
  Routed to five residual templates.
- The seeded challenges are cutting both ways, which is the point: `progress-photos` survived its
  challenge on a real argument, `compliance-certificate` did not survive its own.
- `drawings-revisions` was argued to stand rather than collapse into the version-family design,
  and proposes `revision` for R1c.

## construction_property complete — 28/28 (third family finished)

- Chunk C: all 10 verified pre-commit. Memos 3.9-5.4KB, no proposed fields, nothing out of scope.
- **`construction_property.timesheet` REFUSED** — the collision predicted at dispatch. Argued as
  "a document type wearing a situation's clothes": a construction timesheet is three different
  documents sharing a table shape, and each already has a home — a signed dayworks sheet is
  evidence for `variation-claim`, and the payroll-shaped content belongs to a schema whose privacy
  posture is stricter than this one's. Coverage routed rather than dropped.
- `site-survey` vs `survey-valuation`: argued explicitly as requested and **both kept** — the
  tempting reading is one world under two names ("a professional looking at a building"), which
  fails once you ask what the deliverable is (measuring the land vs pricing the asset).
- Running refusal tally across the swarm: 3 of 60 rows (organisational-records,
  compliance-certificate, timesheet). Every one routed to residuals or siblings, none dropped.

## Wave 3 (creative, 42 rows) — killed twice, zero survivors both times

- 4 agents dispatched over the whole `creative` family; all died on the session limit before
  writing any file. Nothing on disk, nothing to salvage. Redispatch the family whole.
- The node-test warnings seeded for those agents are preserved in `26-research-dispatch-state.md`
  §0a so the next dispatch does not have to re-derive them.

## Saved at user request — end of session 2026-08-24

- Working tree clean; every landed row committed. **147/358 rows landed, 211 owed.**
- 13 commits pushed to `build/p6-p7-first-packages`.
- Resume point is `26-research-dispatch-state.md` §0. Its stale §2 and §3 are now marked
  SUPERSEDED — they claimed 22 R1b rows were still owed, which would have caused a future session
  to redo finished work.

## J-DEPTH ratified 2026-08-24 — gist depth overruled

- Joseph ruled the industry rows must reach the **same depth as the 83 launch rows**. J-IND's gist
  clause is overruled; recorded as J-DEPTH in DECISION-BRIEF.md.
- `GIST-BRIEF.md` renamed `RESEARCH-BRIEF.md` and its depth section rewritten: full R1b depth, the
  `Depth: GIST` label retired, and six explicit requirements (evidence not assertion; node test
  argued on all three legs; files considered-and-rejected; reciprocal boundaries; a collision
  fixture; open questions surfaced). Agents are told to calibrate against landed *launch* rows
  (~13KB memos), and explicitly told the gist families are debt, not exemplars.
- **The 64 committed gist rows are now debt, not done** — clinical_practice (11),
  business_operations (25), construction_property (28). They must be deepened. The index must not
  present them as finished until they are.
- Revised scope: **275 rows at full depth, one agent per row.** At one wave per usage window this
  is a run measured in weeks, not days. Recorded so the estimate is not rediscovered as a surprise.

## First J-DEPTH row — the standard demonstrably changed

- `creative.creative-brief`: memo **19,331B**, JSON 23,706B, 11 file_examples.
  Benchmarks: gist median 4,921B · R1b launch-row median 12,993B. This row is 3.9x the gist depth
  and above the launch-row median, so J-DEPTH is landing, not just declared.
- All six required sections present, including the node test argued leg by leg (not a verdict) and
  a "Files considered and rejected" section — the two things gist rows were skipping.
- **REFUSED**, as flagged at dispatch, on a genuinely new argument: a brief-shaped document is the
  strongest single evidence that a CLIENT ENGAGEMENT exists, and "a signal that is decisive for a
  neighbour cannot also be constitutive of this row" — running both would let one evidence item
  activate two templates, which is the collision discipline CONNECTION.md section 4 step 3 exists
  to prevent. Routed to five residual templates.
- Two NEEDS-JOSEPH items surfaced rather than smoothed, including one escalated upward about the
  fieldless-schema consequence for the whole family.

## `creative.raw-photo-catalogue` — stands, at 24.5KB

- Memo **24,470B** (gist median 4.9KB, launch-row median 13KB), 12 file_examples, every universal
  key present. Not refused — argued to stand against a three-way collision.
- **Engaged the prior cross-family argument rather than ignoring it:** cites
  `construction_property.progress-photos` five times and reasons against it explicitly, as
  instructed. This is the behaviour that grouped gist agents could not produce across families.
- **Exemplary proposed-field discipline:** it needs `capture_date` and *seconds*
  `photos.camera-events`' existing proposal instead of minting a variant — "a second independent
  situation needing the same key is evidence for the proposal, not a second proposal." Keeps
  `destination_eligible: false` as originally proposed and declines to widen it, citing 00's
  warning about trees that create "a large number of tiny folders". Nothing written into
  canonical_fields.json.

## `creative.self-initiated-work` — REFUSED, 27.6KB, the hardest case on the roster

- Memo **27,633B**, the deepest row written so far. Refused, which was the flagged likely outcome.
- The argument is the one the row was dispatched to test: **"the row's defining condition is the
  absence of a signal, and absence never activates."** Strip the client and what remains — a .psd
  with layers, a RAW with EXIF, a .docx with headings — is byte-for-byte the schema's own material.
- Fails all three limbs of the node test plus a fourth that 00 states about this row's shape in
  advance. Routed to six residual templates rather than dropped.
- **Engaged the landed `code.*` refusals six times** (`code.software-project`,
  `code.scratch-prototypes`), which were refused on nearly identical grounds — the cross-family
  consistency J-DEPTH was adopted to get.
- Running J-DEPTH tally: 3 rows, memos 19.3 / 24.5 / 27.6 KB (gist median 4.9KB, launch median
  13KB). Two refusals, one stands. The depth is buying arguments, not adjectives.

## `creative` schema row — the anchor for 41 siblings, 28.9KB

- Memo **28,917B**, deepest row to date. 13 file_examples, every universal key present, stands.
- Written deliberately as an anchor: it states the family's posture, vocabulary, default template
  and seams explicitly, "on the assumption that a sibling author reads *this file* before writing
  theirs" — which is what 41 siblings need, since each measures its node test against the default
  template defined here.
- **NJ-R1a-1 handled correctly: recorded, NOT resolved.** Referenced 5 times, with the alternatives
  and their costs spelled out, and the reasoning for leaving it open stated plainly — "this is the
  row where a silent resolution would be least visible and most consequential."
- Verified `source_type` values programmatically against `src/evidence_shape/vocabulary.py`'s
  `SOURCE_TYPES` rather than assuming them — rigor no gist row showed.
- `proposed_fields` for R1c: `project`, `stage`, `artifact_type`, `client` — the same four the
  roster already names as NJ-R1a-1's option (b) candidates, so the proposal and the open question
  are consistent rather than competing.

## Clearing the gist debt — Joseph's call, 2026-08-24

- Ordered to clear the 64 gist rows to J-DEPTH **before** writing the 207 unwritten rows.
- Sequencing: **the three schema rows go first** (`clinical_practice` 7.7KB, `business_operations`
  7.8KB, `construction_property` 7.3KB). Every sibling measures its node test against its schema's
  default template, so deepening a template before its schema guarantees redoing it.
- Then the 61 templates, one agent per row, shallowest first. Debt inventory: 332,767 bytes across
  64 rows, median 4,921B, against a J-DEPTH floor of ~13KB and observed J-DEPTH rows of 19-29KB.
- Deepening rule for these agents: the existing row is a VERIFIED-BUT-SHALLOW draft, not an
  untrusted one. Its facts were checked; what it lacks is depth, cross-family argument, the node
  test argued leg by leg, and files-considered-and-rejected. Preserve what is right, deepen the
  rest, do not rewrite for the sake of rewriting.

## Debt clearing 1/64 — `clinical_practice` schema deepened

- **7,749B → 40,102B (5.2x)**, JSON 39,719B, 13 file_examples, all universal keys. Deepest row on
  the roster. 23 sections, so the growth is structure and argument, not padding.
- Preserved as instructed: the `subject_of_record` proposal, and the honest treatment of the node
  test's unsatisfiable leg — now stated outright as "unsatisfiable, and I am not going to pretend
  otherwise", with legs 2 and 3 carrying the row instead.
- Added what gist depth lacked: the default template stated for the ten siblings **and each sibling
  measured against it**; a collision fixture named in BOTH directions (over-firing on a blank
  consultation-letter template, under-firing on the After Visit Summary — the reciprocal bytes
  shared with `medical`); files considered and rejected; reciprocal boundaries both ways
  (`medical.*` engaged 16 times); a sparse-file discipline section; and a "what changed in the JSON
  in this pass" section that makes the deepening auditable.

## Debt clearing 2-3/64 — the other two schema anchors deepened

- `business_operations`: **7,848B → 45,984B (5.9x)**, 15 sections, 10 file_examples, all universal
  keys. Generalises its family's one refusal into a stated "never-alone principle, for all 24
  siblings" — turning a single row's argument into a rule the whole family can apply.
- `construction_property`: **7,329B → 43,353B (5.9x)**, 15 sections, 11 file_examples, all
  universal keys. Stays explicitly consistent with the `progress-photos` reasoning and with
  `creative.raw-photo-catalogue`, which had argued against it.
- **The shared `organization` proposal is genuinely reciprocal, not two rival claims.** Each memo
  names the other, quotes its edge, and states it is deliberately not contradicting it. R1c will
  find one decision to make, not two competing ones — which is exactly what was asked for.
- All three schema anchors are now at J-DEPTH. Their 61 templates can go out shallowest-first,
  each measured against a default template that now actually exists.

## Debt clearing 4/64 — `business_operations.market-research` deepened, and survives

- **3,755B → 29,398B (7.8x)**, 9 file_examples, `Depth: J-DEPTH` header replacing the retired
  `Depth: GIST`. **Not refused** — but the gist verdict was genuinely retested, not rubber-stamped.
- It read the family's refusal FIRST, explicitly "on the assumption that this row was heading the
  same way", applied the schema anchor's generalised never-alone principle to itself, and then
  argued its way out. That is the debt-clearing pass working as intended: a thin "stands" verdict
  re-examined against a real test.
- Engaged the `research.*` collision 31 times, and **followed its sibling `user-research`'s
  reasoning rather than re-deriving it** — including `research.project-workspace`, a landed
  refusal it calls "the sharpest precedent for what a default-template row looks like when it is
  caught". Cross-family consistency, which the gist pass could not produce.

## Note: the debt was mis-measured, corrected

The gist rows' **JSON payloads were already substantial** (~25KB, ~10 file_examples). Only the
`.research.md` memos were shallow. Earlier log entries quoted memo bytes as if they were whole-row
sizes. Deepening is therefore cheaper per row than the 3-4x projection: agents verify-and-extend
the JSON and rewrite the memo. Corrected in the retry prompts.

## Debt clearing 5/64 — `construction_property.agency-listing` deepened

- **3,466B → 36,028B (10.4x)**, the largest expansion so far. 10 file_examples, all universal keys,
  no proposed fields, stands.
- The dispatch challenge — a listing is public-facing marketing material, so is it *less* sensitive
  than the schema default? — was engaged head-on and answered **against** the intuition, with the
  agent noting the intuition is reasonable before dismantling it. Privacy reasoning appears 13
  times; leg 3 is the leg this row turns on.
- This is the argument the gist row did not contain at all, and it is the kind that matters:
  getting a privacy posture wrong in the permissive direction is the expensive error.

## Debt clearing 6-7/64 — both salvaged from a limit-kill, both complete

- The usage limit killed both agents, but **the write-as-you-go instruction paid off**: both had
  written complete files before dying. Verified rather than assumed — JSON parses, all universal
  keys present, memos end on finished sentences, no truncation.
- `business_operations.budget-forecast`: **3,777B → 43,409B (11.5x)**, 10 file_examples, stands.
  Notes that "nine of the ten boundaries in this memo are one-way" — a reciprocity observation R1c
  will want, since one-way boundaries are exactly what the merge gate checks.
- `construction_property.construction-project`: **3,261B → 38,433B (11.8x)**, 15 file_examples,
  stands. Now a spine heavy enough to carry the siblings that define themselves against it.
- Both expansions are the largest yet (11.5x, 11.8x), continuing the trend: richer anchors and
  neighbours give each new row more to genuinely argue with.

## Debt clearing 8/64 — `business_operations.it-asset-inventory` deepened, stands

- **3,912B → 35,723B (9.1x)**, 10 file_examples, all universal keys, `Depth: J-DEPTH` header.
- Structure worth copying: it opens the node test with **"The hostile reading, stated first"** —
  granting the dispatch's charge (an asset inventory is plausibly a spreadsheet shape, and its
  obvious signals are never-alone) before defending. It also states outright that two legs pass on
  real evidence and one "cannot pass at all", noting that saying which is which "is the point of
  running the test rather than announcing a verdict".
- Closes with an explicit attestation that nothing in it is padding — the right instinct now that
  memo size is a visible metric. Size must not become the target; the argument is the target.

## Debt clearing 9/64 — `business_operations.policy-handbook` deepened, stands

- **4,091B → 33,624B (8.2x)**, 11 file_examples, all universal keys, `Depth: J-DEPTH`.
- Survived the sharpest challenge set so far — it is the nearest sibling to the row this family
  already refused, on the same document-type charge — and closed the trap deliberately: it cites
  00's universal-facts sentence (file type, creation date, language, duplicate family, version
  family, sensitivity status) to establish that **annual reissue is not an argument for this row**,
  because version family is already a universal fact rather than a domain concern. Backed from the
  other end by the content-hash-vs-filename collision sentence.
- **Wrote the `hr` boundary 18 times for an author who does not exist yet.** `hr` is an unwritten
  schema, and a staff handbook is its most obvious material; the seam is now specified in advance
  rather than left to be negotiated when that family is written. Cheapest possible time to fix it.

## Debt clearing 10/64 — `clinical_practice.case-conference` deepened, stands

- **3,869B → 36,887B (9.5x)**, 11 file_examples, all universal keys, `Depth: J-DEPTH`, complete.
- Engaged `business_operations.meeting-record` 6 times — the cross-family collision that mattered
  here, since a clinical case conference and a corporate meeting record must not both claim the
  same evidence. Third-party aggregation reasoned about explicitly for the privacy leg.
- Ends with a stated list of exactly which files it modified — the auditability habit now showing
  up unprompted across deepened rows.

## Wave summary — 4 dispatched, 4 landed, 0 killed

First wave since the limits reset with no agent losses. Expansions 9.1x / 8.2x / 9.5x, all
stands, no refusals this wave despite three of four being flagged as likely failures. That is a
reasonable outcome, not a rubber stamp: each granted the hostile reading first and answered it on
cited evidence (spreadsheet-shape, document-type, and work_type-of-patient-chart charges
respectively). The two flagged-likely-refusal rows that DID fail earlier — organisational-records,
compliance-certificate — show the flagging discriminates rather than always producing "stands".

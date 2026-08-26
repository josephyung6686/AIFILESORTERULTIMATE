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

**Correction:** this heading was written when only THREE had landed; `subcontract` was still
running and was reported as complete prematurely. It landed shortly after (11.0x, stands) and the
summary below now reflects all four. Do not report a wave complete until every row is verified.

First wave since the limits reset with no agent losses. Expansions 9.1x / 8.2x / 9.5x / 11.0x, all
stands, no refusals this wave despite three of four being flagged as likely failures. That is a
reasonable outcome, not a rubber stamp: each granted the hostile reading first and answered it on
cited evidence (spreadsheet-shape, document-type, and work_type-of-patient-chart charges
respectively). The two flagged-likely-refusal rows that DID fail earlier — organisational-records,
compliance-certificate — show the flagging discriminates rather than always producing "stands".

## Debt clearing 11/64 — `construction_property.subcontract` deepened, stands

- **3,882B → 42,561B (11.0x)**, 10 file_examples, all universal keys, `Depth: J-DEPTH`.
- Survived a two-sided charge: that it is a document type inside `construction-project`'s
  lifecycle, or that it is `legal`'s material wearing a construction label. Engaged the `legal.*`
  launch rows 11 times to settle the contract seam reciprocally rather than assuming it.

## Debt clearing 12/64 — `construction_property.commercial-lease` deepened, stands

- **4,251B → 38,129B (9.0x)**, 11 file_examples, all universal keys, `Depth: J-DEPTH`.
- The charge was the strongest available: `legal.leases-agreements` is a landed launch row that
  owns leases by name, and "the tenant is a business" is an organisation name — never-alone
  evidence that cannot activate a row. Engaged that row 14 times.
- **It found a structural discriminator instead**, on dimensions rather than subject matter: the
  family's `instruction` level assumes a commissioned job with a start and an end, but a tenancy is
  a *relationship with a term* — one shop let in 2014, surrendered 2019, re-let 2021 is three
  tenancies on one premises whose papers "are meaningless in the others' company".
- It also argued a **negative** difference — no period level, where its two folder-sharing siblings
  (`service-charge`, `block-management`) both correctly want a year level — and noted that a
  negative difference is "the rarer and more useful kind". Worth propagating: rows have been
  arguing only from what they have, not from what they conspicuously lack.

## Debt clearing 13-14/64 — `product-requirements` and `building-control`, both stand

- `business_operations.product-requirements`: **4,296B → 41,012B (9.5x)**, 9 file_examples.
  **It settled the pair question the gist pass left hanging.** Verdict: PRD and roadmap are TWO
  worlds, discriminated by structural axis — the roadmap's is time (swimlanes, horizons, now/next/
  later, no acceptance criteria anywhere), this row's is a specification of intended behaviour with
  acceptance criteria. The roadmap's own bytes (`H1 roadmap.pptx`) are named as the collision
  fixture by both rows. Principle worth keeping: *"a question stated identically on two rows is a
  well-documented deferral, not an answer."*
  It also **corrected an edge in its own JSON** after reading the `code.*` refusals, and adopted
  `user-research`'s boundary wording unchanged rather than restating it — reciprocity by reuse.
  Note: it names a row `engineering.requirements-specification` in an unwritten schema; that row
  must exist or the reference dangles. **R1c to check.**
- `construction_property.building-control`: **4,288B → 37,764B (8.8x)**, 11 file_examples.
  Survived the charge that refused its own family's `compliance-certificate`, and wrote the
  `government` seam 33 times for a schema nobody has written yet — the second row to specify a
  boundary in advance of its neighbour existing.

## Debt clearing 15/64 — `construction_property.development-appraisal`, and the wave closes

- **4,165B → 46,497B (11.2x)**, the largest memo yet. 12 file_examples, all universal keys, stands.
- Survived the spreadsheet-shape charge and settled the `finance` seam (engaged 13 times), staying
  consistent with the earlier `site-survey` vs `survey-valuation` split (engaged 6 times) — pricing
  a scheme before it is built vs pricing an asset that exists.
- **Qualified the gist draft's leg-2 claim** rather than preserving it, and stated explicitly that
  nothing else was reversed. That is the deepening pass doing its actual job: not just expanding a
  thin row, but correcting what the thin row got wrong, and saying so audibly.
- Nice detail: it invokes the sparse-file rule because half this row's real files are an untitled
  `Cashflow.xlsx` in a folder named after a site — reasoning about the unhelpful real-world file,
  not the tidy imagined one.

## Wave complete — 4 dispatched, 4 landed, 0 killed (verified this time before reporting)

Expansions 9.0x / 9.5x / 8.8x / 11.2x. All four stand. Techniques worth propagating from this wave:
arguing from a **conspicuous absence** (commercial-lease's missing period level), settling a
deferred pair question outright (product-requirements), specifying a seam with an **unwritten**
schema (building-control -> government), and **qualifying a predecessor's claim** with an explicit
statement of what else was left alone (development-appraisal).

## Debt clearing 16/64 — `business_operations.meeting-record` deepened, stands

- **4,446B → 40,526B (9.1x)**, 11 file_examples, all universal keys, `Depth: J-DEPTH`.
- Answered its real charge rather than the easy one: it names the values-are-not-nodes rule, then
  says the harsher objection is that **a meeting may be a *format*** — the SOURCE_TYPE boundary
  that got 18 legacy ids dropped in triage — and calls that "this row's actual risk", answered
  head-on.
- **Cross-agent reciprocity worked under parallel edit.** `board-governance` was being deepened at
  the same time; this row read that row's `collides_with` entry naming it and reciprocated **in
  that row's own words**, without editing it. It also adopted `clinical_practice.case-conference`'s
  wording (7 references) rather than competing with it. The no-double-edit rule held.

## Debt clearing 17-19/64 — and the dispatcher gets corrected

- `business_operations.board-governance`: **4,373B → 49,734B (11.4x)**, largest memo to date,
  11 file_examples, stands, no proposed fields.
- `construction_property.block-management`: **4,298B → 43,055B (10.0x)**, 11 file_examples, stands.
  Had to beat `finance.hoa-residents-association` on something other than "a company does the
  work", and did.
- `construction_property.drawings-revisions`: **4,373B → 30,062B (6.9x)** — the SMALLEST expansion
  of the wave, and the most valuable row in it.
  - **Verdict: KEPT, but on one leg instead of three, on a different structure than the gist named,
    and with the gist's `revision` field proposal WITHDRAWN.** `proposed_fields` is now empty.
  - "Three of its four claims are reversed below and each reversal is stated as a reversal."
  - **It corrected the dispatch itself:** the warning "was correct about the *danger* and wrong
    about *where* the danger was. The trap this row nearly fell into was not the version family —
    the gist had already seen and refused that. It was standing on a signal that belongs to its own
    schema." The agent found a failure mode the dispatcher had not identified.
- Lesson recorded: **expansion ratio is not a quality signal.** The smallest growth in this wave
  produced the most correction. Judge rows on reversals, withdrawals and arguments, never on bytes.

## Debt clearing 20/64 — `business_operations.partnerships-bd`, and a second pair question settled

- **4,486B → 35,864B (8.0x)**, 13 file_examples, all universal keys, stands.
- **Settled the three-row counterparty question** (partnerships vs `customer-account-management` vs
  `vendor-management`, engaged 14 times) rather than restating it — explicitly citing the principle
  established by `product-requirements` that a question stated identically on several rows is a
  deferral, not an answer.
- The discriminator is **relationship state, not counterparty role**: this row holds a commercial
  relationship *that does not exist yet* — prospects, pitches, proposals, NDAs, letters of intent —
  where its two siblings hold relationships that already do. Role would have been a field value;
  state is structural. This is the same class of move as `commercial-lease`'s tenancy-vs-job
  argument.
- Found and fixed a cross-family error: a fundraising term sheet was "one of this row's named
  instruments pointed at the wrong counterparty", producing a new reciprocal edge to
  `finance.cap-table-equity`.

## Debt clearing 21/64 — `business_operations.contract-administration`, stands

- **4,323B → 39,418B (9.1x)**, 12 file_examples, all universal keys, stands.
- Engaged `legal.*` 16 times and followed `construction_property.subcontract`'s settlement of the
  same contract-vs-`legal` charge 11 times, rather than re-deriving it.
- **Best practice worth propagating: it encoded the trap into the data, not just the prose.** The
  dispatch's charge — that if the only discriminator were a company rather than a person holding
  the contract, the row would fail — is accepted outright AND written into the JSON as
  `recognition.never_alone[2]`, "so that no downstream reader can mistake it for support."
  A rejected signal recorded as machine-readable never-alone evidence survives; a rejected signal
  argued only in a memo can be silently re-adopted later.

## Debt clearing 22/64 — `business_operations.go-to-market`, stands

- **4,406B → 46,901B (10.6x)**, 10 file_examples, all universal keys, stands.
- Quoted the dispatch's charge verbatim into the memo and answered it as "an answer rather than a
  defence" — the phase-not-a-world objection engaged directly.

## Wave of 8 — outcome, and an honest read on the flagging

7 landed so far, all stand; 1 (`snagging-defects`) still running. **No refusals in this wave**
despite 5 of 8 being flagged as likely failures. That could look like rubber-stamping, so the
honest accounting:

- The flagging is still producing corrections, just short of refusal. `drawings-revisions` reversed
  three of four claims, withdrew a field proposal, and corrected the dispatcher's own diagnosis.
  `partnerships-bd` settled a three-row merge question and fixed a mis-pointed instrument.
  `contract-administration` wrote its disqualifying signal into the JSON as never-alone evidence.
- Earlier waves DID refuse under the same flagging (organisational-records, compliance-certificate,
  timesheet, creative-brief, self-initiated-work), so the mechanism discriminates.
- **But the ratio is worth watching.** If flagged rows stop failing entirely across the next two
  waves, the flagging has become theatre and the challenge needs re-designing, not repeating.
  Recorded here so a future session checks it rather than assuming.

## Debt clearing 23/64 — `construction_property.snagging-defects`, and the wave of 8 closes

- **4,308B → 52,309B (12.1x)**, largest memo of the run, 14 file_examples, stands.
- Re-tested properly against the deepened spine after surviving the same `work_type` charge on thin
  reasoning at gist depth. Engaged `progress-photos` 14 times — the photographic-evidence
  collision, since a snag list is often annotated photographs and that row earned its place on
  detection *method*. Consistent with it rather than competing.

## WAVE OF 8 — COMPLETE. 8 dispatched, 8 landed, 0 killed, 0 double-edits.

Doubling the wave size cost nothing. The two overlapping pairs deepening simultaneously
(`board-governance`/`meeting-record`, `contract-administration`/`partnerships-bd`) each stated
their boundary reciprocally without editing the other — the no-double-edit rule held under
parallel load, and `meeting-record` even reciprocated `board-governance` **in that row's own
words** while it was still being written.

Debt: 64 -> 41 remaining. Total landed 173/358.

**Wave size 8 is validated.** Nothing in this wave argues for going back to 4.

## Debt clearing 24-26/64 — three rows, all salvaged intact from a limit-kill

The usage limit killed all four agents, but three had written both files completely. Verified:
JSON parses, all universal keys, memos end on finished sentences, `Depth: J-DEPTH`.

- `construction_property.trade-job`: **4,512B → 50,740B**, stands. Beat the charge that it is
  `construction-project` at smaller scale (scale is not a structural difference); fixture bytes
  named on its side of the seam.
- `business_operations.procurement-sourcing`: **4,534B → 37,717B**, stands. Placed itself relative
  to the counterparty settlement `partnerships-bd` made, rather than reopening it.
- `business_operations.compliance-audit`: **28,176B**, stands. Survived the same document-type
  charge that refused `construction_property.compliance-certificate`, and routed its overflow into
  reciprocal edges (including one to `hr.training-records`) "instead of being written into other
  rows" — the no-double-edit rule applied by the agent itself.

## DEFECT CAUGHT — `business_operations.risk-register` memo and JSON disagree

Its memo is complete (45,609B, J-DEPTH, ends cleanly) and its **"What changed" section claims the
`needs_llm` and `never_alone` lists were "extended, not rewritten"** — but `risk-register.json` is
**unmodified** in the working tree. The agent was killed between writing the memo and writing the
JSON, so the memo documents changes the data does not contain.

**Not committed.** A memo that describes edits its JSON lacks is worse than a shallow row: it reads
as done and audits as done. Held back for a reconciliation pass that either applies the extensions
or corrects the memo's claim.

**Rule for the autopilot:** a complete-looking memo is not proof the row is complete. Cross-check
the memo's own "what changed" claims against the JSON before committing.

## DEFECT RESOLVED — `business_operations.risk-register` reconciled, and committed

The reconciliation pass closed the memo/JSON gap **in both directions**, which is the honest
outcome rather than the convenient one:

- **Applied** every JSON change the memo's arguments genuinely required: five new `collides_with`
  edges, a `board-governance` `also_holds_with`, two seconded `proposed_fields`, two new
  `never_alone` entries (7 → 9), and an FMEA file example.
- **Corrected three memo claims to match reality** instead of inventing data to justify them —
  including the `needs_llm` extension, which the memo had announced but its arguments never asked
  for. Walking back an overstated claim is as valid a fix as applying it.
- The memo now carries a standing note explaining the interruption and the repair, so the anomaly
  is legible to R1c rather than invisible.

**Net effect of catching this:** one row's recognition data is now provably consistent with its own
reasoning, and the autopilot has a new pre-commit check that applies to every remaining row.

## Debt clearing 28/64 — `business_operations.strategy-plan`, stands

- **4,736B → 29,888B (6.3x)**, 10 file_examples, all universal keys, both files written, stands.
- **Declined the easy discriminator.** "A roadmap is product-level, a strategy is company-level"
  is refused outright as "exactly the move the schema anchor forbids" — *"Differing in business
  function is not automatically a difference"* — because a function or a unit is a **value of a
  dimension, not a structure**. It states plainly that a company-wide roadmap is still a roadmap
  and this row does not claim it.
- **The refusal is encoded in the data, twice**: a never-alone entry disclaiming horizon and period
  axes, and a deterministic signal stating the discriminator as **decision axis vs period axis**.
- Best detail: the discriminator is **falsifiable** — "testable by deleting the dates". A
  discriminator you can run an experiment against is worth more than one you can only agree with.
- Stays consistent with the requirements-vs-roadmap settlement rather than reopening it; its four
  wanted changes are recommendations to R1c under NJ-BO-SP-3, not edits to neighbours.

## Debt clearing 29-30/64 — the wave closes, 4 dispatched 4 landed 0 killed

- `construction_property.survey-valuation`: **4,558B → 35,675B (7.8x)**, 11 file_examples, stands.
  Confirmed the `site-survey` split from its own side, where it had only ever been argued from the
  other row's side.
- `business_operations.customer-account-management`: **4,556B → 34,647B (7.6x)**, 11 file_examples,
  stands. Barred from reusing `partnerships-bd`'s relationship-state discriminator (it sits on the
  "already exists" side with `vendor-management`), it accepted and reciprocated that settlement
  "not reopened" and found its own ground, reaching for `00`'s `our_firm`/`client` role split.
- **The line worth keeping:** of the legacy id it absorbed, it says that inheritance "is **not** a
  reason to keep the row." That is the 574's original failure — inventing or retaining a node to
  save an id — named and refused by a row that had every incentive to lean on it.

## Autopilot status

Cron 7c720ee2 firing every 2h at :13. Wave size 4. Debt 64 -> 34. Total landed 180/358.
Pre-commit checks now in force: JSON parses · all universal keys · `Depth: J-DEPTH` header · memo
ends unbroken · both files modified · memo's "what changed" claims match the JSON · no file outside
the row's two touched · commit by explicit file list.

## Debt clearing 31/64 — `business_operations.project-delivery`, narrowed not refused

- **4,793B → 35,090B (7.3x)**, 13 file_examples, both files written, all universal keys, stands.
- **A third outcome, and a healthy one: "The row is narrowed, not refused."** It clears leg 2
  outright, leg 3 "by a genuine downward difference", and **leg 1 narrowly — reported as "a narrow
  win, argued and flagged rather than claimed."** Grading its own margin honestly instead of
  presenting a marginal pass as a clean one is exactly what R1c needs to prioritise its review.
- Stated the cross-schema boundary against `construction_property.construction-project` (5 refs) —
  the charge that two "project" rows on two schemas differ only by industry, and industry is a
  value not a structure.
- Note for the tripwire: outcomes are now spread across refuse / narrow / stand rather than
  clustering on "stands", which is evidence the charges still bite.

## Debt clearing 32/64 — `business_operations.support-operations`, stands at the format boundary

- **4,857B → 32,336B (6.7x)**, 10 file_examples, both files written, all universal keys, stands.
- Conceded the dispatch's premise while holding the verdict: it "sits closer to the format boundary
  than any other survivor in this family", and answers that charge **"with bytes rather than with
  confidence"** — the right instinct for a row whose material is ticket exports, chat logs and mail
  threads, the class 18 legacy ids were dropped for.
- **Two verification habits now appearing unprompted and worth keeping:**
  - every quotation machine-checked verbatim with `grep -F` *before* being written into either file;
  - the memo's own claims "re-read against the written JSON **after** writing, not before" — the
    new cross-check rule, followed and reported rather than assumed.

## Debt clearing 33-34/64 — the wave closes, 4 dispatched 4 landed 0 killed

- `clinical_practice.patient-chart`: **4,886B → 37,837B (7.7x)**, 11 file_examples, stands.
  **The best single argument of the run so far.** Charged with naming what it does NOT hold — since
  a chart that absorbs everything becomes a residual in disguise — it answers: *"everything about a
  patient is Protected Records with a nicer label"*, and then draws a distinction the catalogue did
  not previously have:
  > a row supported by a **relation between two labelled roles** is not a row supported by
  > never-alone tokens, even though each of its tokens is never-alone on its own
  The never-alone failure `00` describes is **role ambiguity** (one token, many possible roles);
  this row's activation requires two person-shaped blocks with roles separately labelled and filled
  by different people, which resolves exactly that ambiguity. The JSON records it token by token.
  **This generalises** — every row whose evidence is a two-role structure can now be argued this way
  instead of dying on never-alone. R1c should consider promoting it to a contract-level rule.
  It also found and fixed a missing reciprocal edge to `case-conference`: "It did not; it does now."
- `construction_property.site-health-safety`: **4,773B → 35,357B (7.4x)**, 12 file_examples, stands.
  Survived the document-type charge that refused `compliance-certificate` in its own family.

## Debt clearing 35-37/64 — three rows, and the memo/JSON check catches a SECOND instance

- `business_operations.corporate-regulatory-filings`: **4,951B → 29,780B (6.0x)**, 13 file_examples,
  both files written, stands.
- `business_operations.facilities-workplace`: **4,892B → 33,825B (6.9x)**, 10 file_examples, both
  files written, stands. Beat the charge that it is `construction_property`'s material seen from
  the tenant's side — a role, not a structure.
- `construction_property.tenancy-management`: **5,010B → 35,052B (7.0x)**, 10 file_examples, both
  files written, stands.

## DEFECT CAUGHT AGAIN — `business_operations.organisational-records`

Same signature as `risk-register`, same detection: only `.research.md` modified, `.json` untouched.
The memo (50,583B, `refuse_node: true` correctly preserved) claims under **Added** that it wrote
the two-role closure *"into the JSON as a `recognition.never_alone` entry and a new clause in
`refuse_reason`."* Verified absent: `never_alone` has 5 entries, none mentioning two-role, and
`refuse_reason` contains no such clause.

**Not committed.** Held for reconciliation.

**The check earns its place.** This is the second occurrence in ~14 rows, so the defect class is not
a one-off — it is what a usage-limit kill looks like when it lands between the two writes, and the
memo is always the file that survives. Every future row must be checked this way; a complete-looking
memo is not evidence the row is complete.

Note: the memo's substance is otherwise excellent — 33 references closing the two-role escape route
with a stated pincer (two-role present, a sibling owns it; two-role absent, never-alone strikes it)
and a deletion-test closure. Only the JSON write is missing.

## DEFECT RESOLVED — `organisational-records` reconciled, and the escape route is now in the data

- `refuse_node` still **true**. `never_alone` **5 → 6**, the new entry carrying the two-role closure;
  a matching clause added to `refuse_reason`. Both verified present programmatically.
- **All four load-bearing sentences preserved verbatim** — *constitutionally never-alone* · *a row
  that never fires* · *a residual wearing a domain's clothes* · *inventing a node to save an id* —
  which matters because a dozen neighbour files quote them as text.
- **Why this repair mattered more than the last one:** the closure now lives in the JSON, so a
  future reader holding only the data cannot use `patient-chart`'s two-role argument to resurrect
  this row. Left in prose, the strongest argument in the catalogue would have been defeatable by
  the second-strongest simply because nobody read 50KB.
- Repair-order rule adopted: on a reconciliation, **write the JSON first** — it is the file a
  limit-kill loses, and the memo is the file that survives.

## Debt clearing 38/64 complete. Standing: 188/358 landed, 26 debt rows left.

## Debt clearing 39/64 — `construction_property.site-survey`, and a boundary confirmed from both sides

- **5,272B → 40,120B (7.6x)**, 11 file_examples, both files written, all universal keys, stands.
- **The two-sided test worked.** Asked whether `survey-valuation`'s confirmation matched its own
  original reasoning, it answered: *"It matches, and it is not a restatement. The two arguments run
  in opposite directions and meet."* That is the difference between a boundary two rows agree on
  and a boundary one row asserted and the other did not contradict.
- The discriminator is now sharper than the gist version ("measuring the land vs pricing the
  asset"): **measured data with no addressee**, consumed by the design that follows, versus **an
  opinion addressed to a named party under a reliance clause**, consumed by a lender or buyer.
  Addressee and reliance are testable on a real file; "measuring vs pricing" was a paraphrase.

## Debt clearing 40/64 — `business_operations.product-roadmap`, pair question confirmed both ways

- **5,058B → 44,506B (8.8x)**, 10 file_examples, both files written, all universal keys, stands.
- **Confirmed the requirements-vs-roadmap settlement from this side with independent reasoning**,
  explicitly accepting the framing that a boundary argued from one side is half a boundary and that
  the gist's identical `open_question` on both rows was "a well-documented deferral, not an answer."
- Also had to answer `strategy-plan`, which disclaims this row's horizon axis in its own JSON — so
  this row sits between two neighbours that each defined themselves partly against it, and agrees
  with both without contradiction.
- **Both of this wave's two-sided tests now pass** (site-survey/survey-valuation, and
  requirements/roadmap). Neither pair merely deferred to the other.

## Debt clearing 41-42/64 — the wave closes, 4 dispatched 4 landed 0 killed

- `clinical_practice.malpractice-incident`: **5,176B → 41,872B (8.1x)**, 12 file_examples, stands.
  Verified its own scope with `git status` before finishing — "only this row's two files touched."
- `construction_property.variation-claim`: **5,253B → 50,527B (9.6x)**, 15 file_examples, stands.
  **It holds the load a landed refusal placed on it.** `timesheet` was refused partly by routing its
  dayworks evidence here, so this row read that refusal in full "because its routing depends on this
  row", and carries a dedicated section — *The load this row is carrying for a refusal*. Had it
  refused, that routing would have broken; the dependency was made explicit rather than discovered
  later by the merge gate.
  It ends by listing what it did NOT do, including "no attempt to rescue leg 3" — declaring a leg
  it could not win instead of quietly claiming it.

## Push contention with the parallel workstream — handled

Push rejected: the P6/P7 track had pushed `src/` and `tests/` work, including a commit merging 27
of this track's J-DEPTH commits into theirs. Zero file overlap. The rebase initially failed on
unstaged changes — two agents were still mid-write. **Deliberately did not stash live agent work;**
waited for both rows to complete, verified them, committed, then rebased. Stashing files an agent
is actively writing is how a wave gets silently corrupted.

## Debt clearing 43/64 — `construction_property.materials-delivery`, stands

- **5,284B → 35,600B (6.7x)**, 12 file_examples, both files written, all universal keys, stands.
- Beat the charge that a delivery note is `logistics`' material distinguished only by the
  destination being a building site — which would be a location value, not a structure.
- **Wrote the `logistics` seam 19 times for a schema nobody has written yet** — the third row to
  specify a boundary in advance of its neighbour existing (after `policy-handbook`→`hr` and
  `building-control`→`government`). This is becoming a house habit rather than a one-off, and it
  is the cheapest possible moment to fix those seams: while the question is live, and before an
  author on the other side has committed to anything that would have to be renegotiated.

## Debt clearing 44/64 — `business_operations.retrospective-postmortem`, retested and stands

- **5,281B → 38,338B (7.3x)**, 11 file_examples, both files written, stands.
- Faced four independent failure routes (work_type of `project-delivery`; a meeting output already
  covered by `meeting-record`; a document type; content splitting entirely between two siblings)
  and answered each rather than the easiest one.
- **The retest was genuine on both sides.** `project-delivery` had already re-examined this row from
  its side and kept it "while correcting one of its three grounds" — so the original thin gist
  verdict has now been checked twice, from two directions, and one of its supports was replaced.
- **Reversed a gist decision to decline an edge:** `meeting-record` had named this row and stated
  the boundary; the gist draft declined that edge, and this pass accepts and reciprocates it, so the
  edge is now written from both sides.
- Reached across families for the right neighbour: read `clinical_practice.case-conference` for the
  **morbidity-and-mortality edge** — an M&M review is a clinical retrospective, and no prompt named
  that connection.

## ★ MILESTONE — THE GIST DEBT IS CLEARED. 64/64 rows at J-DEPTH.

Every row written under the retired gist standard has been deepened to launch-row depth.
`clinical_practice` (11), `business_operations` (25), `construction_property` (28) are all J-DEPTH.

**Cross-session autopilot worked.** The cron ticks ran in other sessions and carried the work
without supervision: they committed the two rows this session had verified (`abb6e44`), finished the
remaining debt, and moved on to authoring new schema anchors — `hr`, `engineering`, `manufacturing`,
`government` (873d553, 4f24b7b, ee523a0, 2765f94). The autopilot file did its job: no session needed
briefing from Joseph to continue.

**Deepening reversed real gist verdicts.** Among the rows cleared while unsupervised:
`veterinary-practice` REFUSED as species-valued overlap (it stood at gist depth);
`protocol-guideline` REFUSED as a policy genre; clinical `teaching-material` REFUSED across
academia; `practice-administration` and `pharmacy-operations` both **narrowed** to regulated scope;
`progress-photos` narrowed beyond source type; `sale-purchase` routed to `legal` and `finance`.
The debt-clearing pass was not cosmetic — it changed verdicts.

**Refusal tally across the corpus: 16 rows.** The flagging tripwire is answered: flagged rows do
still fail, so the challenge has not become theatre.

## State at this point

LANDED **155/358** · DEBT **0** · UNWRITTEN **203** · REFUSED 16.
Unwritten by family: creative 38 · law_practice 37 · government 31 · engineering 24 ·
manufacturing 19 · retail_hospitality 15 · nonprofit 11 · hr 11 · resource_operations 9 ·
logistics 8.

**Priority now: schema anchors before their templates.** Five remain unwritten — `law_practice`,
`nonprofit`, `retail_hospitality`, `logistics`, `resource_operations`. Every template's node test is
measured against its schema's default template, so a template written before its anchor must be
redone. Four dispatched now.

## Schema anchor authored — `nonprofit` (OTHER-TEAM claim), stands but heavily narrowed

- Memo **36,858B**, `kind: schema`, `fields: []`, 6 file_examples, all universal keys, stands.
- **It conceded most of the family away rather than defending it.** Board minutes, budgets,
  contracts, policies, procurement, audits, projects, IT assets, facilities and regulator returns
  are "`business_operations` with a different tax status, and this schema does not hold any of them."
- **The structural discriminator, which answers the existential charge:**
  > Every relation `business_operations` owns is an **exchange** (value for value) or a **statutory**
  > one (compliance for authority). This family's relations are **neither** — money or labour given
  > without a commensurate return (a restricted grant, a gift, a subscription, unpaid volunteer
  > hours), and service given to a named person who is not paying.
  That is structure, not tax status, and it survives the never-alone rule because it is a relation
  rather than an organisation name.
- A schema that gives away nine-tenths of its plausible scope to keep a defensible tenth is the
  outcome this pass was designed to produce.

## Schema anchor authored — `logistics` (OTHER-TEAM claim), stands

- Memo **42,574B**, `kind: schema`, `fields: []`, 15 file_examples, all universal keys, stands.
- Survived the format charge — a waybill, manifest, tracking export and delivery note are all
  form- or log-shaped, and 18 legacy ids were dropped for exactly that.
- **The write-the-seam-early strategy is now proven end to end.** `construction_property.materials-delivery`
  wrote this seam 19 times before this schema existed; the anchor read it in full "as instructed"
  and answered it in its own §1 — a boundary now argued from both sides before either family's
  templates are written.
- It also picked up work left by two other anchors without being told: `manufacturing`'s
  `collides_with.logistics` entry and its `asset` / `site` / `record_type` proposals are "both
  answered and reused" rather than duplicated, and it found the passage where
  `business_operations.procurement-sourcing` **declined** an edge with this family and addressed it.
- Followed `construction_property`'s NJ-CP-5, which had drawn this seam one-way and left it to
  "whoever writes those schemas" — the open question was resolved by the row it was addressed to.

## Schema anchor authored — `retail_hospitality` (OTHER-TEAM claim), stands

- Memo **33,493B**, `kind: schema`, `fields: []`, 6 file_examples, all universal keys, stands.
- Answered the existential charge first, before anything else, and stated the counterfactual
  plainly: *"**The row would have been refused if it were.**"* A schema that names the condition
  under which it would not exist is easier to audit than one that only argues it does.
- Passes most clearly on **leg 3 (privacy)**, "not shared with any neighbour" — customer data,
  bookings, CCTV and staff records give it a posture `business_operations` does not have.
- **Its `recognition.never_alone` list is the longest of any anchor written so far, deliberately.**
  The row defines itself substantially by what it refuses to accept as evidence, which is the
  strongest available defence for a family whose obvious signals (an organisation name, a sector)
  are all never-alone.
- Inherits `business_operations`' never-alone principle and "does not restate where it already
  holds" — extending a neighbour's rule rather than duplicating it.

## OTHER-TEAM claim status: 3 of 4 complete (nonprofit, logistics, retail_hospitality). law_practice next.

## Schema anchor authored — `law_practice` (OTHER-TEAM claim), stands. ALL 23 ANCHORS NOW EXIST.

- JSON **86,076B**, memo **25,518B**, `kind: schema`, `fields: []`, 13 file_examples, all universal
  keys, stands. The largest unwritten family (36 templates) now has its anchor.
- Answered the existential charge — that this is `legal` with a practising certificate — and stated
  the counterfactual, as `retail_hospitality` did.
- Closes with a self-audit rather than a summary: quotations traced to `00` or the landed node they
  were borrowed from (**0 unverified**); PR-6 shape confirmed field by field; **every neighbour id
  in `collides_with` / `also_holds_with` / `role_split` checked to exist on the roster, no id
  invented**; six `proposed_fields`, all reuses, four already canonical; and an explicit statement
  that only its own two files were written.
  That last check — verifying every referenced id actually exists — is worth generalising to R1c.

## ★ ALL 23 SCHEMA ANCHORS ARE WRITTEN AT J-DEPTH.

This is the gate that unblocks the rest of the catalogue: every remaining template measures its node
test against its schema's default template, and all 23 default templates now exist.

## OTHER-TEAM claims: 4 of 4 COMPLETE (law_practice, nonprofit, logistics, retail_hospitality).

CODEX's four rows (`resource_operations`, `creative.performing-practice`, `creative.client-engagement`,
`creative.revision-round`) have landed on disk but are **left uncommitted for CODEX** — they are not
this team's to commit. `resource_operations.json` now has a memo alongside it, so CODEX's agent
appears to have written over the stray partial this team left; that contested file is resolved.

## STOPPING HERE at Joseph's instruction. Next session: see `28-AUTOPILOT.md` §0 (two-team rules)
then §2 (the loop). Remaining: ~199 templates, then R1c, the review panel, and the index.

## Audit + edge gate — 2026-08-26 (orchestrator, mid-dispatch)

Two auditors (overlap, design-fidelity) ran against the landed corpus. **Both returned FAIL:**
31 findings, 17 critical/major. A new mechanical gate, `planning/domains/check_edges.py`, was
written to turn the judgement findings into counted, repeatable checks. **These are R1c's repair
list — no node file was edited by the orchestrator.**

Structural gate (`check.py`-style, run first): **214 rows, 0 defects** — JSON parses, no dangling
edge ids, residual names valid, source_types valid, fields canonical-or-proposed, no invented edge
keys. The defects below are all *edge semantics*, which no gate was checking.

`python3 planning/domains/check_edges.py` — current reading:

| Finding | Count | Rows | What it means |
|---|---:|---:|---|
| `collides_with` one-way | 632 | 179 | §5 makes collisions reciprocal; B never names A back. Matches the historic 44%-reciprocity defect of the 574. |
| `KEY_DRIFT_signal` | 279 | 58 | The discriminator is spelled `why`, not `signal` (`_CONTRACT.md` §72 shape). **The argument text exists** — this is a rename, not a missing discriminator. |
| `also_holds_with` one-way | 147 | 53 | Same reciprocity rule, co-activation side. |
| `also_holds_on_template` | 92 | 35 | §5 restricts `also_holds_with` to **schema ↔ schema only**; 35 template rows carry it. |
| `collides_kind_mismatch` | 59 | 30 | §5: collisions join **same-kind pairs**; schema↔template edges cannot be evaluated. |
| `KEY_DRIFT_target` | 29 | 6 | Target spelled `domain_id`/other, not `domain`. Concentrated in `creative.*`. |

### Corrections to the auditors' own claims — verified, not accepted

- The overlap auditor reported **"111 `collides_with` with `signal: null`"** as its one CRITICAL.
  **That over-calls it.** Those rows carry the discriminating argument under the key `why`; the
  evidence-item reasoning is present and often good. The true defect is **key drift** (279), which
  is a mechanical rename for R1c, not 111 rows of missing argument. Fixing the label matters:
  the CRITICAL as written would have sent R1c to re-research rows that are already argued.
- The orchestrator's first gate ran with `domain_id` as canonical and reported 1,535 target-key
  drifts. `_CONTRACT.md`'s own example shape is `{"domain", "signal", "design_cite"}`, so **`domain`
  is correct and that finding was the gate's bug, not the corpus's.** Corrected reading is 29.

### Judgement findings worth keeping (from the auditors, not mechanical)

- `creative.film-production` / `shoot-day-media` / `post-production` compete for the same call
  sheets and `.prproj` files with **no edge between any pair**, and all three sit on the field-less
  creative schema so `dimension_order` cannot discriminate. Recommended split: shoot-day-media owns
  capture-day media, post-production owns the edit/master chain, film-production narrows to the
  production spine or is refused as the schema's default template.
- `finance.household-property` positively claims files that are the flagship examples of five
  `construction_property` rows; eleven rows collide *into* it and it names none of them back.
  Recommended discriminator: the owner's retained copy vs the professional's working copy.

### Standing note for R1c

`check_edges.py` is deliberately separate from `check.py` (which still does not scan `nodes/` —
extending it is R1c's task). Two teams were writing when it was authored, so it only reads.
Reciprocity is judged **only where both rows are on disk**, so the counts will move as the
remaining rows land; re-run it rather than quoting these numbers.

### Repair plan (Joseph, 2026-08-26): fix everything once all agents return

Ordered, and split by whether judgement is required. Nothing is applied while dispatches run —
writing into a file an agent still owns is the collision `29-DOMAIN-OWNERSHIP.md` rule 1 forbids.
`fix_edges.py` enforces that itself: it refuses if any node file was touched in the last 120s.

1. **Wait for all four shards** (`w6u3r5eqr`, `wno5gz1he`, `wwjc0onmb`, `wh12ufh32`), then commit
   the landed rows by explicit file list.
2. **Mechanical pass — `python3 planning/domains/fix_edges.py --apply`.** Deterministic renames
   only: `why`→`signal`, `domain_id`/`id`/`target`→`domain`. ~308 repairs, no judgement, key order
   preserved. Clears `KEY_DRIFT_*` outright.
3. **Judgement pass — R1c** (`planning/prompts/01c-merge-and-gate.md`), which owns cross-row edits:
   - 632 one-way `collides_with` / 147 one-way `also_holds_with` → add the reciprocal, or record a
     `one_way_reason`. Per pair; the two are not interchangeable.
   - 92 `also_holds_with` on templates → **lift** to the schema pair or **convert** to
     `collides_with`, depending on what the row meant. Guessing destroys the §5 distinction.
   - 59 cross-kind `collides_with` → lift to the schema pair or push down to the template pair.
   - The two argued overlaps: the `creative` film-production/shoot-day-media/post-production trio,
     and `finance.household-property` vs five `construction_property` rows.
4. **Re-run both gates** (`check.py`, `check_edges.py`) and re-run the two auditors on the repaired
   corpus — a repair that is not re-audited is a claim, not a result.
5. Then the final review panel and the index (`26-research-dispatch-state.md` §0a).

Reciprocity counts move as rows land (a collision into an unwritten row is owed, not one-way), so
step 3 must re-run the gate rather than work from the numbers logged above.

## Deferred to the next batch — Joseph's credit cut, 2026-08-26

Shards 1 and 3 were ended to stop **39 unrun rows** from spending credits. Shards 0 and 2 were
left running and were not touched. Killed agents' finished files persist (agents write each file
the moment it is ready) — verified: **zero memo-without-JSON partials**, so nothing is a half-row.

Do not work from this list — recompute from the roster (`26-research-dispatch-state.md` §0).
It is recorded only so the size of the cut is auditable:

```text
  law_practice.contract-negotiation
  law_practice.criminal-defence
  law_practice.depositions-testimony
  law_practice.due-diligence
  law_practice.expert-materials
  law_practice.hearing-transcripts
  law_practice.investigation
  law_practice.legal-research
  law_practice.motions-and-briefs
  law_practice.orders-and-judgments
  law_practice.precedent-bank
  law_practice.regulatory-submission
  law_practice.time-and-billing
  law_practice.trial-preparation
  logistics.driver-compliance
  logistics.last-mile-pod
  logistics.shipment
  manufacturing.asset-register
  manufacturing.energy-audit
  manufacturing.failure-analysis
  manufacturing.hse-incident
  manufacturing.maintenance-work-order
  manufacturing.production-planning
  manufacturing.quality-management-system
  manufacturing.spare-parts
  manufacturing.tooling-fixture
  manufacturing.work-instruction
  nonprofit.fundraising-donor
  nonprofit.grant-reporting
  nonprofit.political-campaign
  nonprofit.standards-body
  nonprofit.volunteer-management
  retail_hospitality.catering-contract
  retail_hospitality.event-production
  retail_hospitality.guest-feedback
  retail_hospitality.pos-reporting
  retail_hospitality.product-catalogue
  retail_hospitality.stocktake
  retail_hospitality.supplier-order
```


## Second credit cut — shard 0 ended, 2026-08-26

Cut timed to an agent completion (a watcher waited for the next node file to land, then the
workflow was ended) so that row banked. Shard 2 left running as the only dispatch.

- **This run's 166 claimed rows: 99 have JSON on disk, 67 owed.**
- Roster total **358**; node files on disk **282**.
- Shard 0 ended at 27/41; shard 2 continues at 26/40.

### ⚠ Six UNTRUSTED PARTIALS — JSON written, memo missing

Killed agents write the JSON first, so these six rows have a `.json` and **no `.research.md`**:

```text
creative.book-manuscript
hr.training-development
law_practice.appeals
law_practice.corporate-secretarial
law_practice.estates-administration
law_practice.opinions-advice
```

Per the operating rule (`28-AUTOPILOT.md` §4): **verify line-by-line, repair, complete, own.**
Never discard unread — the JSON cost real tokens. Never trust unverified — no auditor has seen it
and the memo that would carry its argument does not exist. The resume query in
`26-research-dispatch-state.md` §0 keys on `.json` existence, so **these six will look landed and
will be skipped.** The next batch must select on the memo as well:

```bash
python3 -c "
import json,os
r=json.load(open('planning/domains/roster.json')); n=r['nodes'] if isinstance(r,dict) else r
owed=[x['domain_id'] for x in n
      if not os.path.exists('planning/domains/nodes/'+x['domain_id']+'.json')
      or not os.path.exists('planning/domains/nodes/'+x['domain_id']+'.research.md')]
print(len(owed),'owed (counts memo-less partials)')"
```

## SESSION END — stopped at Joseph's mark, 2026-08-26

Shard 2 was stopped once it reached **35 of its 40** rows (a watcher polled for the 35th file, so
the stop landed on a completion boundary). All four shards are now ended. Nothing is running.

### Verified corpus state

| | Count |
|---|---:|
| Roster rows | 358 |
| **Complete (JSON + memo)** | **283** |
| JSON-only partials (agent killed mid-row) | 8 |
| Owed (no files) | 67 |

Session movement: **183 → 283 complete rows** (+100).

**Owed by family:** manufacturing 15 · law_practice 15 · retail_hospitality 14 · nonprofit 9 ·
resource_operations 8 (CODEX's) · logistics 5 · creative 1.

### ⚠ Eight JSON-only partials — untrusted drafts, NOT finished rows

```text
creative.book-manuscript          law_practice.appeals
hr.training-development           law_practice.corporate-secretarial
manufacturing.production-record   law_practice.estates-administration
manufacturing.supplier-qualification
nonprofit.advocacy-campaign
```

They are committed so the tokens are not lost, **not because they are done**. `28-AUTOPILOT.md` §4
applies: verify line-by-line, repair, complete, own. The §0 resume query in
`26-research-dispatch-state.md` now selects on **both** files, so these are counted as owed.

### Gates, re-read at session end

- `check.py` — 574 legacy entries, 566 in-file / 0 cross-file. **Unchanged baseline**; the legacy
  slices are superseded by the roster, not repaired.
- `check_edges.py` — **1,979 findings** (up from 1,239, because 100 more rows landed and
  reciprocity is only judged when both ends exist). Largest: 905 one-way `collides_with`,
  427 `why`-instead-of-`signal`, 245 one-way `also_holds_with`, 196 `also_holds_with` on templates,
  88 cross-kind collisions, 32 genuinely empty collision signals (`hr.dei-program`,
  `law_practice.opinions-advice`, `.pleadings`, `.court-filing-record`, `.appeals`).
- The 32 empty signals are the one finding that is **not** a rename — those rows record no
  discriminating evidence at all and need re-argument, unlike the 427 key drifts.

### Commits this session

`a1376d0` claim 166 ids · `de1c6c9` edge gate + audit findings · `cc54db6` repair tool + plan ·
`9cdaeab` defer 39 rows · `6f551ad` second cut + partials · `df41425` land rows · plus the final
row commit above. Node files were committed **by explicit file list**, only when quiescent 45-60s,
with every staged JSON parse-checked first.

### Next session — do these in order

1. `python3 planning/domains/check_edges.py` — re-read, do not trust the numbers above.
2. `python3 planning/domains/fix_edges.py --apply` — the deterministic renames (`why`→`signal`,
   `domain_id`→`domain`). Safe now: nothing is running. Then re-run the gate to confirm both
   KEY_DRIFT categories go to zero.
3. Finish the **67 owed rows** + the **8 partials** (deferred lists are in this log; recompute with
   the §0 query rather than trusting them).
4. **R1c** for the judgement repairs (one-way edges, template-borne `also_holds_with`, cross-kind
   collisions, the 32 empty signals, the creative-trio and household-property overlaps).
5. Re-run both gates **and** the two auditors on the repaired corpus, then the review panel + index.
